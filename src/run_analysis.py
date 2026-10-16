"""Validate orders, persist an SQLite table, and export SQL analytics."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "raw" / "orders.csv"
DATABASE_PATH = ROOT / "data" / "processed" / "order_fulfillment.db"
SQL_PATH = ROOT / "sql" / "analysis.sql"
OUTPUT_DIR = ROOT / "outputs"
TIMESTAMP_COLUMNS = ["ordered_at", "packed_at", "shipped_at", "delivered_at", "promised_delivery_at"]
EXPECTED_QUERIES = {"kpis", "by_warehouse", "by_carrier", "by_region", "by_month", "stage_summary", "data_quality"}


def load_queries(sql_text: str) -> dict[str, str]:
    """Parse SQL statements following '-- query: name' markers."""
    queries: dict[str, str] = {}
    current_name: str | None = None
    current_lines: list[str] = []
    for line in sql_text.splitlines():
        marker = line.strip()
        if marker.lower().startswith("-- query:"):
            if current_name is not None:
                queries[current_name] = "\n".join(current_lines).strip()
            current_name = marker.split(":", 1)[1].strip()
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)
    if current_name is not None:
        queries[current_name] = "\n".join(current_lines).strip()
    return {name: query for name, query in queries.items() if query}


def prepare_orders(source: pd.DataFrame | Path | str) -> pd.DataFrame:
    """Load and validate raw order data; add stage durations and SLA flags."""
    if isinstance(source, pd.DataFrame):
        orders = source.copy()
    else:
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run 'python -m src.generate_data' first.")
        orders = pd.read_csv(path)

    required = {"order_id", "warehouse", "carrier", "region", "order_value", "product_category", *TIMESTAMP_COLUMNS}
    missing = required.difference(orders.columns)
    if missing:
        raise ValueError(f"Input data is missing required columns: {sorted(missing)}")
    if orders.empty:
        raise ValueError("Input data contains no orders.")
    if orders["order_id"].isna().any() or orders["order_id"].astype(str).str.strip().eq("").any():
        raise ValueError("order_id must be populated for every row.")
    if orders["order_id"].duplicated().any():
        raise ValueError("order_id must be unique.")
    if orders[["warehouse", "carrier", "region"]].isna().any().any():
        raise ValueError("warehouse, carrier, and region must be populated.")
    numeric_values = pd.to_numeric(orders["order_value"], errors="coerce")
    if numeric_values.isna().any():
        raise ValueError("order_value must be numeric and non-missing.")
    if (numeric_values < 0).any():
        raise ValueError("order_value cannot be negative.")
    orders["order_value"] = numeric_values

    for column in TIMESTAMP_COLUMNS:
        orders[column] = pd.to_datetime(orders[column], format="mixed", errors="raise")
        if orders[column].isna().any():
            raise ValueError(f"{column} contains missing timestamps.")

    ordered_sequence = ["ordered_at", "packed_at", "shipped_at", "delivered_at"]
    for earlier, later in zip(ordered_sequence, ordered_sequence[1:]):
        bad = orders[later] < orders[earlier]
        if bad.any():
            raise ValueError(f"Timestamp sequence invalid: {later} precedes {earlier} for {int(bad.sum())} orders.")
    promised_before_order = orders["promised_delivery_at"] < orders["ordered_at"]
    if promised_before_order.any():
        raise ValueError(f"promised_delivery_at precedes ordered_at for {int(promised_before_order.sum())} orders.")

    orders["warehouse_processing_hours"] = (orders["packed_at"] - orders["ordered_at"]).dt.total_seconds() / 3600
    orders["handoff_hours"] = (orders["shipped_at"] - orders["packed_at"]).dt.total_seconds() / 3600
    orders["transit_hours"] = (orders["delivered_at"] - orders["shipped_at"]).dt.total_seconds() / 3600
    orders["fulfillment_hours"] = (orders["delivered_at"] - orders["ordered_at"]).dt.total_seconds() / 3600
    orders["delivery_delay_hours"] = (orders["delivered_at"] - orders["promised_delivery_at"]).dt.total_seconds() / 3600
    orders["is_late"] = (orders["delivered_at"] > orders["promised_delivery_at"]).astype(int)
    orders["is_on_time"] = 1 - orders["is_late"]
    orders["order_month"] = orders["ordered_at"].dt.to_period("M").astype(str)
    return orders


def run_pipeline(
    source: pd.DataFrame | Path | str,
    database_path: Path = DATABASE_PATH,
    output_dir: Path = OUTPUT_DIR,
    sql_path: Path = SQL_PATH,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Run validated analysis and return enriched data and named result frames."""
    orders = prepare_orders(source)
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL analysis file not found: {sql_path}")
    queries = load_queries(sql_path.read_text(encoding="utf-8"))
    missing_queries = EXPECTED_QUERIES.difference(queries)
    if missing_queries:
        raise ValueError(f"SQL file is missing queries: {sorted(missing_queries)}")

    database_path.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, pd.DataFrame] = {}
    with sqlite3.connect(database_path) as connection:
        orders.to_sql("orders", connection, if_exists="replace", index=False)
        for name in sorted(EXPECTED_QUERIES):
            results[name] = pd.read_sql_query(queries[name], connection)
            results[name].to_csv(output_dir / f"{name}.csv", index=False)
    return orders, results


def main() -> None:
    orders, results = run_pipeline(INPUT_PATH)
    kpis = results["kpis"].iloc[0]
    print(f"Validated and analyzed {len(orders):,} orders.")
    print(f"Late-delivery rate: {kpis['late_rate_pct']:.2f}%")
    print(f"SQLite database: {DATABASE_PATH}")
    print(f"CSV outputs: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

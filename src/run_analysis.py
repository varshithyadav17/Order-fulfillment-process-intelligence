"""Build the local SQLite table and export SQL-based fulfillment KPIs."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "raw" / "orders.csv"
DATABASE_PATH = ROOT / "data" / "processed" / "order_fulfillment.db"
SQL_PATH = ROOT / "sql" / "analysis.sql"
OUTPUT_DIR = ROOT / "outputs"

TIMESTAMP_COLUMNS = [
    "ordered_at",
    "packed_at",
    "shipped_at",
    "delivered_at",
    "promised_delivery_at",
]


def load_queries(sql_text: str) -> dict[str, str]:
    """Read named queries from -- query: name markers in analysis.sql."""
    queries: dict[str, str] = {}
    current_name: str | None = None
    current_lines: list[str] = []

    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("-- query:"):
            if current_name is not None:
                queries[current_name] = "\n".join(current_lines).strip()
            current_name = stripped.split(":", 1)[1].strip()
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)

    if current_name is not None:
        queries[current_name] = "\n".join(current_lines).strip()

    return {name: query for name, query in queries.items() if query}


def prepare_orders(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Run 'python -m src.generate_data' first."
        )

    orders = pd.read_csv(path)
    required_columns = {
        "order_id",
        "warehouse",
        "carrier",
        "region",
        "order_value",
        *TIMESTAMP_COLUMNS,
    }
    missing = required_columns.difference(orders.columns)
    if missing:
        raise ValueError(f"Input data is missing required columns: {sorted(missing)}")

    if orders["order_id"].isna().any() or orders["order_id"].duplicated().any():
        raise ValueError("order_id must be populated and unique.")

    for column in TIMESTAMP_COLUMNS:
        orders[column] = pd.to_datetime(orders[column], errors="raise")

    orders["warehouse_processing_hours"] = (
        orders["packed_at"] - orders["ordered_at"]
    ).dt.total_seconds() / 3600
    orders["handoff_hours"] = (
        orders["shipped_at"] - orders["packed_at"]
    ).dt.total_seconds() / 3600
    orders["transit_hours"] = (
        orders["delivered_at"] - orders["shipped_at"]
    ).dt.total_seconds() / 3600
    orders["fulfillment_hours"] = (
        orders["delivered_at"] - orders["ordered_at"]
    ).dt.total_seconds() / 3600
    orders["delivery_delay_hours"] = (
        orders["delivered_at"] - orders["promised_delivery_at"]
    ).dt.total_seconds() / 3600
    orders["is_late"] = (
        orders["delivered_at"] > orders["promised_delivery_at"]
    ).astype(int)

    duration_columns = [
        "warehouse_processing_hours",
        "handoff_hours",
        "transit_hours",
        "fulfillment_hours",
    ]
    if (orders[duration_columns] < 0).any().any():
        raise ValueError("Timestamps produce a negative process duration.")

    return orders


def main() -> None:
    orders = prepare_orders(INPUT_PATH)
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sql_text = SQL_PATH.read_text(encoding="utf-8")
    queries = load_queries(sql_text)
    expected = {"kpis", "by_warehouse", "by_carrier", "by_region"}
    missing_queries = expected.difference(queries)
    if missing_queries:
        raise ValueError(f"SQL file is missing queries: {sorted(missing_queries)}")

    with sqlite3.connect(DATABASE_PATH) as connection:
        orders.to_sql("orders", connection, if_exists="replace", index=False)
        for name in sorted(expected):
            result = pd.read_sql_query(queries[name], connection)
            output_path = OUTPUT_DIR / f"{name}.csv"
            result.to_csv(output_path, index=False)
            print(f"Wrote {output_path.relative_to(ROOT)}")

    print(f"Analyzed {len(orders):,} orders.")
    print(f"SQLite database: {DATABASE_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from src.generate_data import generate_orders
from src.run_analysis import load_queries, prepare_orders, run_pipeline

ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / "sql" / "analysis.sql"


def test_generator_is_reproducible_and_unique() -> None:
    first = generate_orders(50)
    second = generate_orders(50)
    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 50
    assert first["order_id"].is_unique


def test_generated_data_has_valid_event_order() -> None:
    df = generate_orders(100)
    for column in ["ordered_at", "packed_at", "shipped_at", "delivered_at"]:
        df[column] = pd.to_datetime(df[column], format="mixed")
    assert (df["ordered_at"] <= df["packed_at"]).all()
    assert (df["packed_at"] <= df["shipped_at"]).all()
    assert (df["shipped_at"] <= df["delivered_at"]).all()


def test_prepare_orders_calculates_duration_and_sla() -> None:
    df = pd.DataFrame([{
        "order_id": "ORD-1", "warehouse": "WH-A", "carrier": "C-1", "region": "Urban",
        "product_category": "Home", "order_value": 100,
        "ordered_at": "2025-01-01 00:00:00", "packed_at": "2025-01-01 02:00:00",
        "shipped_at": "2025-01-01 03:00:00", "delivered_at": "2025-01-03 00:00:00",
        "promised_delivery_at": "2025-01-02 00:00:00",
    }])
    prepared = prepare_orders(df)
    assert prepared.loc[0, "warehouse_processing_hours"] == pytest.approx(2.0)
    assert prepared.loc[0, "handoff_hours"] == pytest.approx(1.0)
    assert prepared.loc[0, "fulfillment_hours"] == pytest.approx(48.0)
    assert prepared.loc[0, "delivery_delay_hours"] == pytest.approx(24.0)
    assert prepared.loc[0, "is_late"] == 1


def test_prepare_orders_rejects_duplicate_ids() -> None:
    df = generate_orders(2)
    df.loc[1, "order_id"] = df.loc[0, "order_id"]
    with pytest.raises(ValueError, match="unique"):
        prepare_orders(df)


def test_prepare_orders_rejects_impossible_timestamps() -> None:
    df = generate_orders(2)
    df.loc[0, "shipped_at"] = "2024-01-01 00:00:00"
    with pytest.raises(ValueError, match="Timestamp sequence invalid"):
        prepare_orders(df)


def test_prepare_orders_rejects_promise_before_order() -> None:
    df = generate_orders(2)
    df.loc[0, "promised_delivery_at"] = "2024-12-31 00:00:00"
    with pytest.raises(ValueError, match="precedes ordered_at"):
        prepare_orders(df)


def test_prepare_orders_rejects_missing_required_columns() -> None:
    df = generate_orders(2).drop(columns=["carrier"])
    with pytest.raises(ValueError, match="carrier"):
        prepare_orders(df)


def test_sql_query_parser_finds_all_named_queries() -> None:
    queries = load_queries(SQL_PATH.read_text(encoding="utf-8"))
    assert {"kpis", "by_warehouse", "by_carrier", "by_region", "by_month", "stage_summary", "data_quality"} <= set(queries)


def test_pipeline_creates_outputs_and_database(tmp_path: Path) -> None:
    db_path = tmp_path / "processed" / "orders.db"
    output_dir = tmp_path / "outputs"
    orders, results = run_pipeline(generate_orders(100), db_path, output_dir, SQL_PATH)
    assert len(orders) == 100
    assert results["kpis"].iloc[0]["total_orders"] == 100
    assert set(results["by_warehouse"]["warehouse"]) <= set(orders["warehouse"])
    assert (output_dir / "kpis.csv").exists()
    assert (output_dir / "data_quality.csv").exists()
    with sqlite3.connect(db_path) as connection:
        row_count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    assert row_count == 100


def test_data_quality_checks_show_no_missing_or_negative_durations(tmp_path: Path) -> None:
    _, results = run_pipeline(generate_orders(80), tmp_path / "orders.db", tmp_path / "out", SQL_PATH)
    quality = results["data_quality"].set_index("check_name")
    assert quality.loc["unique_order_ids", "observed_value"] == 80
    assert quality.loc["missing_order_ids", "observed_value"] == 0
    assert quality.loc["negative_stage_durations", "observed_value"] == 0
    assert quality.loc["missing_promised_delivery", "observed_value"] == 0

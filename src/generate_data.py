"""Generate a reproducible synthetic order-fulfillment dataset.

All records are artificial and must not be interpreted as real company data.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "raw" / "orders.csv"

SEED = 42
ORDER_COUNT = 2_000


def generate_orders(count: int = ORDER_COUNT) -> pd.DataFrame:
    rng = random.Random(SEED)
    start = datetime(2025, 1, 1)
    warehouses = ["WH-North", "WH-South", "WH-East"]
    warehouse_weights = [0.34, 0.33, 0.33]
    carriers = ["SwiftShip", "ParcelPro", "ValueFreight"]
    carrier_weights = [0.34, 0.36, 0.30]
    regions = ["Urban", "Suburban", "Rural", "Remote"]
    categories = ["Electronics", "Home", "Apparel", "Beauty", "Sports"]

    # These parameters deliberately create variation between segments.
    # They are synthetic assumptions, not evidence about actual operations.
    warehouse_pack_scale = {
        "WH-North": 2.5,
        "WH-South": 4.2,
        "WH-East": 3.0,
    }
    carrier_transit_scale = {
        "SwiftShip": 7.5,
        "ParcelPro": 10.0,
        "ValueFreight": 14.0,
    }
    region_extra_hours = {
        "Urban": 0.0,
        "Suburban": 3.0,
        "Rural": 8.0,
        "Remote": 14.0,
    }

    records: list[dict[str, object]] = []
    for number in range(1, count + 1):
        warehouse = rng.choices(warehouses, weights=warehouse_weights, k=1)[0]
        carrier = rng.choices(carriers, weights=carrier_weights, k=1)[0]
        region = rng.choice(regions)
        ordered_at = start + timedelta(minutes=rng.randint(0, 90 * 24 * 60))

        warehouse_processing_hours = max(
            0.3, rng.gammavariate(2.0, warehouse_pack_scale[warehouse])
        )
        handoff_hours = max(0.1, rng.gammavariate(1.5, 2.0))
        transit_hours = max(
            1.0,
            rng.gammavariate(2.4, carrier_transit_scale[carrier])
            + region_extra_hours[region],
        )

        packed_at = ordered_at + timedelta(hours=warehouse_processing_hours)
        shipped_at = packed_at + timedelta(hours=handoff_hours)
        delivered_at = shipped_at + timedelta(hours=transit_hours)
        sla_hours = rng.choices([36, 48, 60], weights=[0.30, 0.50, 0.20], k=1)[0]
        promised_delivery_at = ordered_at + timedelta(hours=sla_hours)

        records.append(
            {
                "order_id": f"ORD-{number:05d}",
                "warehouse": warehouse,
                "carrier": carrier,
                "region": region,
                "product_category": rng.choice(categories),
                "order_value": round(rng.uniform(15.0, 700.0), 2),
                "ordered_at": ordered_at.isoformat(sep=" "),
                "packed_at": packed_at.isoformat(sep=" "),
                "shipped_at": shipped_at.isoformat(sep=" "),
                "delivered_at": delivered_at.isoformat(sep=" "),
                "promised_delivery_at": promised_delivery_at.isoformat(sep=" "),
            }
        )

    return pd.DataFrame.from_records(records)


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    orders = generate_orders()
    orders.to_csv(OUTPUT_PATH, index=False)
    print(f"Generated {len(orders):,} synthetic orders: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

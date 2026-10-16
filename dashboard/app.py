"""Interactive Streamlit dashboard for the synthetic order-fulfillment project."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.generate_data import generate_orders  # noqa: E402
from src.run_analysis import prepare_orders  # noqa: E402

st.set_page_config(page_title="Order Fulfillment Intelligence", page_icon="📦", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.7rem; padding-bottom: 2.5rem;}
    [data-testid="stMetric"] {background: #f5f7fb; border: 1px solid #e2e8f0; padding: 14px 16px; border-radius: 12px;}
    [data-testid="stMetricLabel"] {font-weight: 600;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Preparing the synthetic order dataset…")
def load_data() -> pd.DataFrame:
    """Use generated local data when present; otherwise generate data in memory."""
    raw_path = ROOT / "data" / "raw" / "orders.csv"
    if raw_path.exists():
        return prepare_orders(raw_path)
    return prepare_orders(generate_orders())


def pct(value: float) -> str:
    return f"{value:.1f}%"


def build_insight(df: pd.DataFrame) -> str:
    """Create a cautious, data-dependent summary for the current filter selection."""
    if df.empty:
        return "No orders match the selected filters. Adjust the filters to continue."
    late_rate = 100 * df["is_late"].mean()
    stage_means = {
        "Warehouse processing": df["warehouse_processing_hours"].mean(),
        "Handoff": df["handoff_hours"].mean(),
        "Transit": df["transit_hours"].mean(),
    }
    longest_stage = max(stage_means, key=stage_means.get)
    segments = df.groupby("carrier", dropna=False).agg(
        orders=("order_id", "count"), late_rate=("is_late", "mean")
    )
    eligible = segments[segments["orders"] >= max(20, int(0.05 * len(df)))]
    if eligible.empty:
        segment_note = "There are not enough orders per carrier to make a stable segment comparison under the current filters."
    else:
        worst = eligible.sort_values("late_rate", ascending=False).iloc[0]
        segment_note = (
            f"{worst.name} has the highest observed late rate among carriers with adequate "
            f"volume ({pct(100 * worst['late_rate'])}, n={int(worst['orders']):,})."
        )
    return (
        f"Overall late-delivery rate is {pct(late_rate)} across {len(df):,} orders. "
        f"The longest average stage is {longest_stage.lower()} "
        f"({stage_means[longest_stage]:.1f} hours). {segment_note} "
        "These are descriptive findings from synthetic data, not proof of causation."
    )


st.title("📦 Order Fulfillment Intelligence")
st.caption("Operational SLA analysis • Synthetic data • Python + SQL + Streamlit")
st.markdown(
    "Explore delivery performance, separate the order journey into stages, and identify "
    "segments that merit further investigation. All data is synthetic."
)

orders = load_data()
min_date = orders["ordered_at"].min().date()
max_date = orders["ordered_at"].max().date()

with st.sidebar:
    st.header("Filters")
    selected_dates = st.date_input(
        "Order date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    selected_warehouses = st.multiselect(
        "Warehouse", sorted(orders["warehouse"].unique()), default=sorted(orders["warehouse"].unique())
    )
    selected_carriers = st.multiselect(
        "Carrier", sorted(orders["carrier"].unique()), default=sorted(orders["carrier"].unique())
    )
    selected_regions = st.multiselect(
        "Region", sorted(orders["region"].unique()), default=sorted(orders["region"].unique())
    )
    only_late = st.checkbox("Only late orders (detail table)", value=False)
    st.divider()
    st.caption("SLA due date is generated per order. Change the filters to compare populations.")

if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date = end_date = selected_dates

filtered = orders[
    orders["ordered_at"].dt.date.between(start_date, end_date)
    & orders["warehouse"].isin(selected_warehouses)
    & orders["carrier"].isin(selected_carriers)
    & orders["region"].isin(selected_regions)
].copy()

if filtered.empty:
    st.warning("No orders match these filters. Adjust the date range or selections.")
    st.stop()

n_orders = len(filtered)
late_orders = int(filtered["is_late"].sum())
late_rate = 100 * filtered["is_late"].mean()
on_time_rate = 100 - late_rate
avg_fulfillment = filtered["fulfillment_hours"].mean()
late_order_value = filtered.loc[filtered["is_late"].eq(1), "order_value"].sum()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Orders", f"{n_orders:,}")
k2.metric("Late delivery rate", pct(late_rate), help="Share of orders delivered after the generated promise timestamp.")
k3.metric("On-time rate", pct(on_time_rate))
k4.metric("Avg. fulfillment", f"{avg_fulfillment:.1f} h")
k5.metric(
    "Value on late orders",
    f"{late_order_value:,.0f} units",
    help="Sum of synthetic order values associated with late orders; not loss, refunds, or penalty cost.",
)

st.info(build_insight(filtered))

performance_tab, stage_tab, trend_tab, details_tab = st.tabs(
    ["Segment performance", "Fulfillment stages", "Time trend", "Order details"]
)

with performance_tab:
    col1, col2 = st.columns(2)
    with col1:
        by_wh = filtered.groupby("warehouse", as_index=False).agg(
            orders=("order_id", "count"),
            late_rate=("is_late", "mean"),
            avg_hours=("fulfillment_hours", "mean"),
        )
        by_wh["late_rate_pct"] = 100 * by_wh["late_rate"]
        fig = px.bar(
            by_wh.sort_values("late_rate_pct", ascending=False),
            x="warehouse",
            y="late_rate_pct",
            text=by_wh["late_rate_pct"].map(lambda x: f"{x:.1f}%"),
            hover_data={"orders": True, "avg_hours": ":.1f", "late_rate": False},
            title="Late-delivery rate by warehouse",
            labels={"warehouse": "Warehouse", "late_rate_pct": "Late orders (%)"},
        )
        fig.update_layout(yaxis_ticksuffix="%", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        by_carrier = filtered.groupby("carrier", as_index=False).agg(
            orders=("order_id", "count"),
            late_rate=("is_late", "mean"),
            transit_hours=("transit_hours", "mean"),
        )
        by_carrier["late_rate_pct"] = 100 * by_carrier["late_rate"]
        fig = px.bar(
            by_carrier.sort_values("late_rate_pct", ascending=False),
            x="carrier",
            y="late_rate_pct",
            text=by_carrier["late_rate_pct"].map(lambda x: f"{x:.1f}%"),
            hover_data={"orders": True, "transit_hours": ":.1f", "late_rate": False},
            title="Late-delivery rate by carrier",
            labels={"carrier": "Carrier", "late_rate_pct": "Late orders (%)"},
        )
        fig.update_layout(yaxis_ticksuffix="%", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    by_region = filtered.groupby("region", as_index=False).agg(
        orders=("order_id", "count"),
        late_rate=("is_late", "mean"),
        avg_hours=("fulfillment_hours", "mean"),
    )
    by_region["late_rate_pct"] = 100 * by_region["late_rate"]
    fig = px.bar(
        by_region.sort_values("late_rate_pct", ascending=False),
        x="region",
        y="late_rate_pct",
        color="orders",
        text=by_region["late_rate_pct"].map(lambda x: f"{x:.1f}%"),
        title="Late-delivery rate by destination region",
        labels={"region": "Region", "late_rate_pct": "Late orders (%)", "orders": "Orders"},
        hover_data={"avg_hours": ":.1f"},
    )
    fig.update_layout(yaxis_ticksuffix="%")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Compare late rate together with order volume. Segment rankings in this synthetic dataset do not establish causality."
    )

with stage_tab:
    stages = pd.DataFrame(
        {
            "Stage": ["Warehouse processing", "Handoff to carrier", "Transit to customer"],
            "Average hours": [
                filtered["warehouse_processing_hours"].mean(),
                filtered["handoff_hours"].mean(),
                filtered["transit_hours"].mean(),
            ],
            "Median hours": [
                filtered["warehouse_processing_hours"].median(),
                filtered["handoff_hours"].median(),
                filtered["transit_hours"].median(),
            ],
        }
    )
    ordered_stages = stages.sort_values("Average hours")
    fig = px.bar(
        ordered_stages,
        x="Average hours",
        y="Stage",
        orientation="h",
        title="Average duration by fulfillment stage",
        text=ordered_stages["Average hours"].map(lambda x: f"{x:.1f} h"),
        hover_data={"Median hours": ":.1f"},
    )
    st.plotly_chart(fig, use_container_width=True)
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(
            filtered,
            x="fulfillment_hours",
            nbins=35,
            title="Distribution of end-to-end fulfillment time",
            labels={"fulfillment_hours": "Hours from order to delivery"},
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.histogram(
            filtered,
            x="delivery_delay_hours",
            nbins=35,
            title="Delivery timing vs promise",
            labels={"delivery_delay_hours": "Hours after promise (negative = early)"},
        )
        fig.add_vline(x=0, line_dash="dash", annotation_text="Promise time")
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(stages.round(2), use_container_width=True, hide_index=True)

with trend_tab:
    trend = filtered.assign(order_month=filtered["ordered_at"].dt.to_period("M").astype(str)).groupby(
        "order_month", as_index=False
    ).agg(
        orders=("order_id", "count"),
        late_rate=("is_late", "mean"),
        avg_hours=("fulfillment_hours", "mean"),
    )
    trend["late_rate_pct"] = trend["late_rate"] * 100
    fig = px.line(
        trend,
        x="order_month",
        y="late_rate_pct",
        markers=True,
        title="Monthly late-delivery rate",
        labels={"order_month": "Order month", "late_rate_pct": "Late orders (%)"},
        hover_data={"orders": True, "avg_hours": ":.1f"},
    )
    fig.update_layout(yaxis_ticksuffix="%")
    st.plotly_chart(fig, use_container_width=True)
    fig = px.bar(
        trend,
        x="order_month",
        y="orders",
        title="Monthly order volume",
        labels={"order_month": "Order month", "orders": "Orders"},
    )
    st.plotly_chart(fig, use_container_width=True)

with details_tab:
    detail = filtered.copy()
    if only_late:
        detail = detail[detail["is_late"].eq(1)]
    detail = detail.assign(
        ordered_at=detail["ordered_at"].dt.strftime("%Y-%m-%d %H:%M"),
        delivered_at=detail["delivered_at"].dt.strftime("%Y-%m-%d %H:%M"),
        promised_delivery_at=detail["promised_delivery_at"].dt.strftime("%Y-%m-%d %H:%M"),
    )
    columns = [
        "order_id", "warehouse", "carrier", "region", "product_category", "order_value",
        "ordered_at", "promised_delivery_at", "delivered_at", "fulfillment_hours",
        "delivery_delay_hours", "is_late",
    ]
    st.dataframe(
        detail[columns].sort_values("delivery_delay_hours", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Download filtered order details (CSV)",
        detail[columns].to_csv(index=False).encode("utf-8"),
        file_name="filtered_order_details.csv",
        mime="text/csv",
    )

st.divider()
st.caption(
    "Portfolio demonstration only. All records and SLA assumptions are synthetic; late-order value is not estimated loss. "
    "Segment differences are descriptive, not causal."
)

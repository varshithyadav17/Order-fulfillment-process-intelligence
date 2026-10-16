-- Run src/run_analysis.py first to create the local SQLite database and orders table.
-- All data is synthetic. Segment differences are descriptive, not causal.

-- query: kpis
SELECT
    COUNT(*) AS total_orders,
    SUM(is_late) AS late_orders,
    ROUND(100.0 * SUM(is_late) / NULLIF(COUNT(*), 0), 2) AS late_rate_pct,
    ROUND(AVG(fulfillment_hours), 2) AS avg_fulfillment_hours,
    ROUND(AVG(warehouse_processing_hours), 2) AS avg_warehouse_processing_hours,
    ROUND(AVG(handoff_hours), 2) AS avg_handoff_hours,
    ROUND(AVG(transit_hours), 2) AS avg_transit_hours,
    ROUND(AVG(order_value), 2) AS avg_order_value
FROM orders;

-- query: by_warehouse
SELECT
    warehouse,
    COUNT(*) AS order_count,
    SUM(is_late) AS late_orders,
    ROUND(100.0 * AVG(is_late), 2) AS late_rate_pct,
    ROUND(AVG(fulfillment_hours), 2) AS avg_fulfillment_hours,
    ROUND(AVG(warehouse_processing_hours), 2) AS avg_warehouse_processing_hours
FROM orders
GROUP BY warehouse
ORDER BY late_rate_pct DESC, order_count DESC;

-- query: by_carrier
SELECT
    carrier,
    COUNT(*) AS order_count,
    SUM(is_late) AS late_orders,
    ROUND(100.0 * AVG(is_late), 2) AS late_rate_pct,
    ROUND(AVG(transit_hours), 2) AS avg_transit_hours
FROM orders
GROUP BY carrier
ORDER BY late_rate_pct DESC, order_count DESC;

-- query: by_region
SELECT
    region,
    COUNT(*) AS order_count,
    SUM(is_late) AS late_orders,
    ROUND(100.0 * AVG(is_late), 2) AS late_rate_pct,
    ROUND(AVG(fulfillment_hours), 2) AS avg_fulfillment_hours
FROM orders
GROUP BY region
ORDER BY late_rate_pct DESC, order_count DESC;

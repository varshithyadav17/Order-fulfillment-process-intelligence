-- Named SQL queries consumed by src/run_analysis.py.
-- Data is synthetic: segment differences are descriptive, not causal.

-- query: kpis
SELECT COUNT(*) AS total_orders,
       SUM(is_late) AS late_orders,
       COUNT(*) - SUM(is_late) AS on_time_orders,
       ROUND(100.0 * SUM(is_late) / NULLIF(COUNT(*), 0), 2) AS late_rate_pct,
       ROUND(100.0 * (COUNT(*) - SUM(is_late)) / NULLIF(COUNT(*), 0), 2) AS on_time_rate_pct,
       ROUND(AVG(fulfillment_hours), 2) AS avg_fulfillment_hours,
       ROUND(AVG(warehouse_processing_hours), 2) AS avg_warehouse_processing_hours,
       ROUND(AVG(handoff_hours), 2) AS avg_handoff_hours,
       ROUND(AVG(transit_hours), 2) AS avg_transit_hours,
       ROUND(AVG(order_value), 2) AS avg_order_value,
       ROUND(SUM(CASE WHEN is_late = 1 THEN order_value ELSE 0 END), 2) AS order_value_exposed_to_late_delivery
FROM orders;

-- query: by_warehouse
SELECT warehouse, COUNT(*) AS order_count, SUM(is_late) AS late_orders,
       ROUND(100.0 * AVG(is_late), 2) AS late_rate_pct,
       ROUND(AVG(fulfillment_hours), 2) AS avg_fulfillment_hours,
       ROUND(AVG(warehouse_processing_hours), 2) AS avg_warehouse_processing_hours,
       ROUND(AVG(transit_hours), 2) AS avg_transit_hours,
       ROUND(SUM(CASE WHEN is_late = 1 THEN order_value ELSE 0 END), 2) AS order_value_exposed_to_late_delivery
FROM orders
GROUP BY warehouse
ORDER BY late_rate_pct DESC, order_count DESC;

-- query: by_carrier
SELECT carrier, COUNT(*) AS order_count, SUM(is_late) AS late_orders,
       ROUND(100.0 * AVG(is_late), 2) AS late_rate_pct,
       ROUND(AVG(fulfillment_hours), 2) AS avg_fulfillment_hours,
       ROUND(AVG(transit_hours), 2) AS avg_transit_hours,
       ROUND(SUM(CASE WHEN is_late = 1 THEN order_value ELSE 0 END), 2) AS order_value_exposed_to_late_delivery
FROM orders
GROUP BY carrier
ORDER BY late_rate_pct DESC, order_count DESC;

-- query: by_region
SELECT region, COUNT(*) AS order_count, SUM(is_late) AS late_orders,
       ROUND(100.0 * AVG(is_late), 2) AS late_rate_pct,
       ROUND(AVG(fulfillment_hours), 2) AS avg_fulfillment_hours,
       ROUND(AVG(transit_hours), 2) AS avg_transit_hours,
       ROUND(SUM(CASE WHEN is_late = 1 THEN order_value ELSE 0 END), 2) AS order_value_exposed_to_late_delivery
FROM orders
GROUP BY region
ORDER BY late_rate_pct DESC, order_count DESC;

-- query: by_month
SELECT strftime('%Y-%m', ordered_at) AS order_month,
       COUNT(*) AS order_count, SUM(is_late) AS late_orders,
       ROUND(100.0 * AVG(is_late), 2) AS late_rate_pct,
       ROUND(AVG(fulfillment_hours), 2) AS avg_fulfillment_hours
FROM orders
GROUP BY strftime('%Y-%m', ordered_at)
ORDER BY order_month;

-- query: stage_summary
SELECT 'Warehouse processing' AS stage, ROUND(AVG(warehouse_processing_hours), 2) AS avg_hours,
       ROUND(100.0 * AVG(warehouse_processing_hours) / NULLIF(AVG(fulfillment_hours), 0), 2) AS share_of_average_fulfillment_pct
FROM orders
UNION ALL
SELECT 'Handoff', ROUND(AVG(handoff_hours), 2),
       ROUND(100.0 * AVG(handoff_hours) / NULLIF(AVG(fulfillment_hours), 0), 2) FROM orders
UNION ALL
SELECT 'Transit', ROUND(AVG(transit_hours), 2),
       ROUND(100.0 * AVG(transit_hours) / NULLIF(AVG(fulfillment_hours), 0), 2) FROM orders;

-- query: data_quality
SELECT 'row_count' AS check_name, COUNT(*) AS observed_value,
       'Count of rows in the current input dataset' AS interpretation
FROM orders
UNION ALL
SELECT 'unique_order_ids', COUNT(DISTINCT order_id), 'Should match row count' FROM orders
UNION ALL
SELECT 'missing_order_ids', SUM(CASE WHEN order_id IS NULL OR TRIM(order_id) = '' THEN 1 ELSE 0 END), 'Expected 0' FROM orders
UNION ALL
SELECT 'negative_stage_durations', SUM(CASE WHEN warehouse_processing_hours < 0 OR handoff_hours < 0 OR transit_hours < 0 OR fulfillment_hours < 0 THEN 1 ELSE 0 END), 'Expected 0' FROM orders
UNION ALL
SELECT 'missing_promised_delivery', SUM(CASE WHEN promised_delivery_at IS NULL THEN 1 ELSE 0 END), 'Expected 0' FROM orders;

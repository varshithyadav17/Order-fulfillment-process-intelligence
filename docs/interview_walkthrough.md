# Interview walkthrough: Order Fulfillment SLA & Delay Analysis

Use this guide to explain the work accurately. The dataset is synthetic, so describe the results as validation of an analytical workflow—not as impact at a real company.

## 60-second project pitch

“I built a reproducible order-fulfillment analytics pipeline to investigate delivery delays. It generates 2,000 synthetic orders, validates identifiers and timestamp order, derives warehouse-processing, handoff, transit and end-to-end durations, and uses SQLite SQL to calculate delivery KPIs and compare warehouses, carriers and regions. I added an interactive Streamlit dashboard with filters, order-level drill-down, automated tests and a management report. In the seeded scenario, 32.8% of orders miss the generated promise time and transit is the largest average stage. Because the data-generating logic deliberately introduces segment differences, I treat these as demonstration findings rather than real operational conclusions.”

## What the metrics mean

- **Late-delivery rate:** count of orders delivered after `promised_delivery_at` divided by all eligible orders.
- **On-time rate:** complement of the late-delivery rate in this dataset.
- **Fulfillment hours:** `delivered_at - ordered_at`.
- **Warehouse processing hours:** `packed_at - ordered_at`.
- **Handoff hours:** `shipped_at - packed_at`.
- **Transit hours:** `delivered_at - shipped_at`.
- **Order value associated with late orders:** sum of `order_value` on late orders. This is not lost revenue, refunds, penalties or profit impact.

## The observed synthetic baseline

| Measure | Value in the default seeded dataset |
|---|---:|
| Orders | 2,000 |
| Late orders | 656 |
| Late-delivery rate | 32.80% |
| On-time rate | 67.20% |
| Average fulfillment time | 41.02 hours |
| Average warehouse processing | 6.29 hours |
| Average handoff | 2.92 hours |
| Average transit | 31.81 hours |

The generator deliberately sets different transit-time distributions for carrier labels and adds extra simulated hours for region labels. Do not present their resulting late-rate gaps as empirical evidence that one real carrier or region performs worse.

## Likely interview questions

### Why did you use synthetic data?

The project is intended to be shareable and reproducible without exposing customer or company order records. Synthetic data allows the analysis workflow to be demonstrated, but it limits what can be concluded about real operations.

### What checks do you run before analysis?

The pipeline checks required columns, populated and unique order IDs, numeric non-negative order values, parseable timestamps, chronological ordering from order to delivery, and a promise timestamp that does not precede order creation. SQL output includes row count, unique IDs, missing IDs, negative stage durations and missing promise checks.

### What is the main finding?

In this seeded scenario, transit is the longest average stage at 31.81 hours, about 77.55% of mean end-to-end fulfillment time. The correct recommendation is to investigate transit milestones in real event-level data—not immediately change carriers based on synthetic rankings.

### Does the analysis prove the carrier caused late deliveries?

No. Segment comparisons are descriptive, and carrier and region parameters are part of the data generator itself. In real data I would compare like-for-like orders by route, distance, service level, warehouse, order priority, date and exception reason, and consider confounding variables before estimating an effect.

### How would you use this in a real company?

First confirm the business definition of on-time delivery and order eligibility. Then reconcile source timestamps, test event sequence and missingness, and stratify performance by route and service level. I would review the worst-delay cases with operations, propose a measurable intervention, and evaluate it using a pilot or a credible comparison group with guardrail metrics.

### What would you build next with real data?

- Add cancellations, split shipments, failed delivery attempts, reschedules, holidays and promised-service categories.
- Add robust SLA eligibility rules and timezone handling.
- Create carrier-lane and warehouse-adjusted comparisons.
- Track percentiles and late-delay severity in addition to averages.
- Define an experiment or before-after evaluation plan before claiming any improvement.

## What not to claim

- Do not say the project reduced delays or saved money; no intervention was tested.
- Do not describe the synthetic carrier/region results as real-world business insights.
- Do not equate order value on late orders with financial loss.
- Do not call the illustrative promise timestamp a contractual SLA.

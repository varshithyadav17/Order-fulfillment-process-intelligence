# Management report: order fulfillment performance

## Purpose

This report demonstrates how an operations analyst can turn timestamp-level order data into a prioritized investigation. It is calculated from a seeded **synthetic** dataset of 2,000 orders, not real company operations.

## Executive summary

The current synthetic run contains **2,000 orders**, of which **656 (32.80%)** arrive after their generated promise timestamp. Average end-to-end fulfillment time is **41.02 hours**. The duration breakdown is 6.29 hours of warehouse processing, 2.92 hours of handoff, and 31.81 hours of transit. Transit accounts for approximately **77.55%** of mean end-to-end fulfillment duration in this generated scenario.

All of these values are reproducible outputs from the current fixed random seed. They are not external benchmarks or estimates of real-world e-commerce performance.

## Findings from the synthetic scenario

| View | Observed result | Interpretation for this project |
|---|---|---|
| Overall | 2,000 orders; 656 late; 32.80% late rate | This is the scenario baseline, not a target or industry benchmark. |
| Stage duration | Transit 31.81 h; warehouse processing 6.29 h; handoff 2.92 h | Transit is the longest average stage in the synthetic design, so it is the first stage to investigate in the exercise. |
| Carrier | ValueFreight 48.56% late (n=661); SwiftShip 20.35% late (n=693) | Difference of 28.21 percentage points in this simulation. The generator intentionally assigns different transit-time distributions to carrier labels, so this is a code-design effect—not an empirical carrier performance finding. |
| Region | Remote 47.65% late (n=510); Urban 25.44% late (n=507) | Difference of 22.21 percentage points. Region-specific extra hours are deliberately built into the generator, so the result demonstrates whether the analysis detects a known simulated pattern. |
| Warehouse | WH-South 36.59% late (n=615); WH-North 30.48% late (n=689) | Difference of 6.11 percentage points, with different average warehouse processing durations in the seeded data. This does not establish a real-world root cause. |
| Data quality | 2,000 rows; 2,000 unique IDs; 0 missing order IDs; 0 negative stage durations; 0 missing promised timestamps | The current automated structural checks pass on the generated dataset. |

The source tables are exported as `outputs/kpis.csv`, `outputs/stage_summary.csv`, `outputs/by_carrier.csv`, `outputs/by_region.csv`, `outputs/by_warehouse.csv`, and `outputs/data_quality.csv` after running the pipeline.

## Recommended operational investigation

1. **Investigate transit first:** In the simulated baseline, transit is the longest stage. For real orders, split transit by lane, distance, service level, first-attempt success, promised service and scan-event gaps.
2. **Validate carrier differences fairly:** Compare like-for-like shipments by region, distance, service level, order priority and shipment date. Do not change carrier allocation based on the synthetic ranking.
3. **Trace the late tail:** Review order-level records with the largest positive `delivery_delay_hours`; determine whether elapsed time accumulates before shipping, during handoff or in transit.
4. **Agree business definitions:** Specify which orders are eligible for the SLA, the promise timestamp source, cut-off times, holidays, cancellations, partial shipments, failed delivery attempts and timezone rules.
5. **Test one intervention:** Pilot a narrowly scoped change with a predefined success metric, guardrails, sample-size plan and observation window. Compare results against a valid baseline or holdout before claiming impact.

## Caveats and decision boundaries

- All records and the SLA design are synthetic. Generator parameters intentionally create differences between carrier, region and warehouse labels to test the analysis workflow.
- The segment rankings are descriptive; they are not proof of causation and should not be described as real operating insights.
- The promised delivery interval is illustrative rather than a contractual SLA.
- The sum of order value on late orders is not lost revenue, refunds, penalties, or profit at risk.
- This report establishes a reproducible analytical baseline only. No intervention has been tested, and no savings or improvement percentage is claimed.

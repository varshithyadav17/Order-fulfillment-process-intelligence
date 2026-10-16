# KPI & Measurement Plan — Fulfillment Operations

> Values in the baseline column are outputs from a seeded synthetic scenario, not real operational benchmarks or targets.

## KPI catalogue

| KPI | Definition | Synthetic baseline | Decision use |
|---|---|---:|---|
| Eligible orders | Number of rows meeting the agreed analysis population | 2,000 generated orders | Confirm denominator and data refresh |
| Late-delivery rate | Orders delivered after generated promise / eligible orders | 656 / 2,000 = 32.80% | Scenario baseline only |
| On-time rate | Orders delivered at or before generated promise / eligible orders | 67.20% | Complement of late rate under current rule |
| Average end-to-end duration | Mean of delivered_at − ordered_at | 41.02 hours | Summary of this sample; supplement with percentiles |
| Average warehouse processing | Mean of packed_at − ordered_at | 6.29 hours | Stage diagnostic |
| Average handoff | Mean of shipped_at − packed_at | 2.92 hours | Stage diagnostic |
| Average transit | Mean of delivered_at − shipped_at | 31.81 hours | Stage diagnostic |
| P90 delay severity (future) | 90th percentile of positive delay among late eligible orders | Not currently included in baseline table | Understand the long tail |
| Invalid event rate (future) | Orders failing a defined event-data quality rule / input orders | Current generated input passes implemented structural checks | Monitor source reliability |

## Metric contract to agree with stakeholders

Specify eligible order types; the source of the promise timestamp; timezone and cutoff rules; cancellation, reschedule, split-shipment and failed-delivery treatment; event correction policy; and reporting period. Do not compare rates until the same denominator and rules apply.

## Proposed pilot success criteria (not yet achieved)

1. At least 99% of eligible orders have the key event timestamps required for the selected stage analysis; confirm this target against real source quality.
2. Summary counts reconcile exactly to the order-level data for the agreed period.
3. Pilot and comparison groups use equivalent eligibility and event-quality rules.
4. Any claimed improvement in on-time delivery is reported with absolute percentage-point change, denominator, time window, and uncertainty / limitations.
5. Guardrail metrics (cost per shipment, damage/returns, customer contacts, cancellations) do not deteriorate beyond limits agreed before launch.

These are proposed measurement criteria only, not results of a real pilot.

## Measurement design

1. Establish a production baseline with complete event logs and an agreed SLA definition.
2. Segment performance by lane, distance, service level, warehouse, priority, time period and exception reason.
3. Validate the most delayed cases with warehouse and logistics owners to form a root-cause hypothesis.
4. Select a bounded intervention and define the unit of assignment and comparison method before launch.
5. Track primary and guardrail metrics for a pre-agreed observation window.
6. Scale only if results are credible, operationally practical and not explained by a major mix / seasonality change.

## Reporting cadence (proposed)

| Measure | Owner | Cadence |
|---|---|---|
| Source event completeness | BI / data owner | Every load |
| SLA adherence and delay tail | Operations analyst | Weekly |
| Stage-specific cases | Warehouse / logistics leads | Weekly triage |
| Pilot outcome and guardrails | Process owner | At pilot checkpoints and close |

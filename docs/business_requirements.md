# Business Requirements Brief — Order Fulfillment & SLA Analysis

> **Case-study boundary:** This is a hypothetical e-commerce operations scenario on generated synthetic orders. No retailer, logistics partner, or operations team supplied requirements or validated the findings.

## 1. Problem statement

An operations team needs a consistent way to measure delivery timeliness and separate the order-to-delivery journey into warehouse processing, carrier handoff, and transit. Without shared metric definitions and stage-level evidence, aggregate delay rates may hide where time is accumulating and teams can jump to conclusions from unadjusted carrier or region comparisons.

## 2. Objective

Build a repeatable analytical workflow that validates timestamp data, calculates agreed operational KPIs, compares segments at a visible sample size, and helps analysts identify which cases to investigate. The prototype demonstrates analysis and decision support; it does not prove an actual root cause or achieved business improvement.

## 3. Illustrative stakeholders

| Role | Need / decision |
|---|---|
| Fulfillment / operations manager | Understand baseline delivery performance and prioritise investigations |
| Warehouse lead | Review order-to-pack processing and queue patterns |
| Carrier / logistics manager | Investigate handoff, scan gaps, and transit exceptions |
| Customer experience lead | Understand customer-facing lateness and escalation impact |
| Data / BI analyst | Define calculations, data quality, reporting and drill-down |
| Finance / commercial partner | Interpret exposure measures without equating order value to loss |

These are hypothetical stakeholder roles, not people interviewed.

## 4. Scope

**In scope:** synthetic order generation; required-field, identifier, numeric and timestamp-sequence validation; stage-duration calculations; late / on-time measures against an illustrative promise timestamp; SQL comparisons by warehouse, carrier, region, and month; dashboard filtering and order-level drill-down; management recommendations; tests and run instructions.

**Out of scope:** changing live carrier allocation, customer notifications, refund decisions, dispatch optimisation, SLA contractual interpretation, production system integrations, causal attribution, and financial-loss estimation.

## 5. Business requirements

| ID | Requirement | Priority | Acceptance evidence |
|---|---|---|---|
| BR-01 | Define order eligibility and on-time / late calculation explicitly | Must | KPI definitions are documented and tested |
| BR-02 | Validate identifiers, required fields, numeric values, and timestamp ordering | Must | Invalid examples are surfaced by tests / quality output |
| BR-03 | Calculate order-to-pack, pack-to-ship, ship-to-deliver, and end-to-end duration | Must | Stage metrics are reproducible from source timestamps |
| BR-04 | Compare rates and durations by operating segment with sample size | Must | SQL summaries show group counts alongside rates |
| BR-05 | Enable filtering and investigation of individual delayed orders | Should | Dashboard exposes filtered detail for download |
| BR-06 | Produce a management-facing summary with recommendations and caveats | Must | Report distinguishes observation, hypothesis, and action |
| BR-07 | Re-run the analysis from documented commands | Must | Generator, analysis, tests and CI complete successfully |

## 6. Definitions and rules

- Late = delivered timestamp after the generated promised-delivery timestamp.
- Fulfillment time = delivered timestamp minus ordered timestamp.
- Stage durations derive from successive event timestamps.
- The generated promise is illustrative, not a contractual service-level agreement.
- Order value on late orders is exposure context, not an estimate of lost sales, refunds, penalties, or profit.
- Carrier and region differences are descriptive only; the generator deliberately creates group differences.

## 7. Non-functional requirements

- Reproducible sample and deterministic run.
- Traceable definitions and readable SQL.
- Visible data-quality checks before segment comparisons.
- Filtered details must remain consistent with summary filters.
- Synthetic-data and causality limits must appear in stakeholder-facing outputs.

## 8. Definition of done

The pipeline calculates validated metrics, creates SQL outputs and a dashboard, includes a management report with next-step hypotheses, passes automated tests, and includes a clear plan for validating findings against production event logs before an operational decision.

## 9. Risks and dependencies

| Risk / dependency | Mitigation |
|---|---|
| Promise-time definition differs by service | Confirm eligibility, cutoff, timezone, holiday and reschedule rules |
| Missing / out-of-order events distort stage durations | Validate sequence and record invalid event data |
| Unadjusted segment comparisons mislead | Stratify by route, distance, service level, priority and date |
| Synthetic differences reflect generator design | Validate hypotheses only on real, suitably controlled data |
| Average hides the late tail | Add median, percentiles and severity bands in future work |

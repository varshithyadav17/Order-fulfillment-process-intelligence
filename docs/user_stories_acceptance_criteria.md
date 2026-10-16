# User Stories & Acceptance Criteria — Fulfillment Analytics

> Draft stories for a hypothetical e-commerce operations backlog; they have not been validated with real business users.

## Epic: Define and validate the baseline

### US-01 — Agree the delivery KPI
**As an operations manager**, I want one documented on-time definition so teams compare performance consistently.

**Acceptance criteria**
- Given an eligible order with delivered and promise timestamps, when KPI logic runs, then it is classified by a documented rule.
- Given a missing or invalid required timestamp, then the quality output makes the limitation visible.
- The definition states cutoff times, timezone, cancellations, reschedules, partial delivery treatment and exclusions to be agreed before production.

### US-02 — Validate the event sequence
**As a BI analyst**, I want invalid timestamps and missing event identifiers surfaced so stage-duration calculations can be trusted.

**Acceptance criteria**
- Given an order ID, then uniqueness and presence checks execute.
- Given timestamps in the wrong sequence, then the case fails a defined validation or is quarantined with a reason.
- Valid stage durations are derived from the documented timestamp pairs.

## Epic: Investigate delay stages

### US-03 — Decompose the fulfillment journey
**As a warehouse / logistics lead**, I want elapsed time separated into processing, handoff and transit so that investigation can focus on a plausible stage.

**Acceptance criteria**
- Stage and total durations reconcile to source timestamps within defined rounding.
- Dashboard views show counts alongside rates and durations.
- The report distinguishes observations from potential causes.

### US-04 — Drill into late orders
**As an operations analyst**, I want to filter and export delayed orders so that I can review source events with the accountable team.

**Acceptance criteria**
- A filtered dashboard result contains only matching records.
- Order-level rows include the keys and timing fields needed for investigation.
- Downloads reflect the selected filters and include the metric definitions or a reference to them.

### US-05 — Compare segments fairly
**As an operations manager**, I want group comparisons with sample size and relevant context before considering a change.

**Acceptance criteria**
- Warehouse, carrier, region and month summaries include denominators.
- Reports state that unadjusted differences are descriptive and may be confounded.
- No carrier-change recommendation is made solely from synthetic rankings.

## Epic: Evaluate improvement

### US-06 — Test an intervention
**As a process owner**, I want a baseline and pilot measurement plan so that process changes are evaluated before scaling.

**Acceptance criteria**
- Primary metric, guardrails, eligible population, time window and comparison method are specified before the pilot.
- Data quality is checked in both baseline and pilot periods.
- Claims of improvement use observed comparison results rather than the generated demo baseline.

## Traceability

| Story | Requirement | Evidence |
|---|---|---|
| US-01 | BR-01 | KPI definitions and calculation tests |
| US-02 | BR-02 | Pipeline validation + data-quality outputs |
| US-03 | BR-03, BR-04 | Stage summary and segment SQL outputs |
| US-04 | BR-05 | Dashboard filters and row-level download |
| US-05 | BR-04, BR-06 | Group summaries and caveated management report |
| US-06 | BR-06 | Pilot design documented before implementation |

## Release acceptance checklist

- [ ] KPI eligibility and promise timestamp are documented.
- [ ] Event-sequence tests pass.
- [ ] Summary measures reconcile to row-level calculations.
- [ ] Segment reports show sample size and limitations.
- [ ] Management recommendations are explicitly framed as investigation steps.
- [ ] No real-world savings or causal lift is claimed without evidence.

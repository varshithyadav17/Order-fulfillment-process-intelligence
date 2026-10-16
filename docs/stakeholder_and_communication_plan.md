# Stakeholder & Communication Plan — Fulfillment Performance

> This is a proposed plan for a hypothetical operations team. The roles and touchpoints have not been validated with a real organisation.

## Stakeholder map

| Role | Primary question | Evidence / communication |
|---|---|---|
| Operations manager | What is the baseline and where should investigation begin? | KPI summary, time trend, sample sizes, key caveats |
| Warehouse lead | How much time passes before packing? | Order-to-pack distribution, cutoff and shift context |
| Logistics / carrier manager | Where do handoff and transit time accumulate? | Lane/service-level and scan-event analysis |
| Customer experience lead | Which late orders need review and how is lateness defined? | Late-order drill-down and severity buckets |
| Data / BI analyst | Are the source events complete and definitions reliable? | Data-quality report, dictionary, SQL definitions |
| Finance partner | Does a reported value represent a loss? | Clear separation of order value exposure from actual financial impact |

## Communication plan

| Touchpoint | Suggested audience | Content | Decision |
|---|---|---|---|
| Metric-definition workshop | Operations + CX + BI | Promise source, eligibility, cutoffs, timezone and exception handling | Approve metric contract |
| Data-readiness review | BI + warehouse + carrier ops | Event completeness, ordering, missing scans, join keys | Accept sample or raise data issue |
| Weekly delay triage | Operations + warehouse + logistics | Long-delay cases, stage decomposition, sample size | Assign investigation owners |
| Pilot readout | Process owner + relevant leads | Baseline, action, guardrails, comparison design | Continue, revise or stop pilot |

## Communication standards

- Put the metric definition and population period next to each rate.
- Report denominators and sample sizes with percentages.
- Separate an observed pattern from a root-cause hypothesis.
- Do not call a carrier or warehouse “worse” based on synthetic or unadjusted comparisons.
- State who owns each next action and when evidence will be reviewed.

## Draft RACI

| Activity | BI analyst | Operations manager | Warehouse lead | Logistics lead | CX |
|---|---|---|---|---|---|
| Approve KPI definitions | R | A | C | C | C |
| Validate source-event sequence | R | A | C | C | I |
| Investigate warehouse stage | C | A | R | I | I |
| Investigate handoff / transit | C | A | I | R | I |
| Review customer-impacting late cases | C | A | C | C | R |
| Approve / evaluate process pilot | C | A | R/C | R/C | C |

R = Responsible, A = Accountable, C = Consulted, I = Informed. Adjust this draft for the actual operating model before use.

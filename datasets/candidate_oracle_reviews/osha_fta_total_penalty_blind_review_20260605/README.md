# OSHA FTA Total Penalty Source-Only Review

Date: 2026-06-05

Fixture: `osha_incident_domain_v1`

Candidate:

```prolog
osha_penalty_amount(Inspection, fta, total, usd_0, SrcFtaTotalPenalty).
```

Verdict: `accept_expected`

The reviewer found that the Violation Summary table states an `FTA Penalty`
row and a `Total` column with the printed value `$0`. The row is scoped to the
same inspection. The review treats the printed zero as a source-stated value,
not a blank or inferred default.

This review was source-only and blind to model outputs.

# FDA T002 Peeling-Paint Detail Focused Review

Source-only focused review returned on 2026-06-05 from the cleaned work-order
packet. The reviewer did not receive model outputs, prior oracle files, or
judged-QA manifests.

Decision: `expected_addition`.

Candidate:

```prolog
fda_violation_detail(violation_4, observation_subject, peeling_paint_ceiling, violation_scope, direct).
```

Source-only rationale: violation 4 is the `211.58` facility-maintenance row,
and the source directly states that investigators observed peeling paint on
the ceiling in the ISO 7 room. The closed FDA detail contract admits compact
observed facility/equipment/control evidence as `observation_subject`.

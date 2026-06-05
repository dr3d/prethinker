# SEC Form 8-K Atom-Library Query Fixture

This retained query fixture measures whether the QA planner can ask questions
inside the compiled SEC Form 8-K atom library without source-record fallback or
Python prose routing.

Scope:

- Domain: `sec_form_8k_skeleton_v1`
- Measurement type: query-planner viability over already-compiled typed atoms
- Claim boundary: this is not a compile-recall score
- Runtime gate: use `--atom-library-query-grounding`
- Optional retry lane: use `--atom-library-query-validation-retry`
- Optional syntax lane: use `--atom-library-slot-label-normalization`

The answers are derived from the selected retained run-1 typed SEC facts in the
local archive bundles listed in `manifest.json`. The packet intentionally asks
only about facts present in those selected run artifacts, so a miss is evidence
about atom-library query planning or execution, not evidence that the compiler
failed to emit the fact.

Registrant identity rows ask for the compiled registrant atom and jurisdiction.
They do not ask for source-display exact legal names; the retained SEC skeleton
pack carries compact registrant atoms, not exact display-name strings.

The planner may see the natural-language question and the filtered typed atom
inventory. It must not receive source prose, source-record predicates, source
headers, profile wish-list predicates, or answer keys. Deterministic runtime
execution must reject source-record plans and absent constants.

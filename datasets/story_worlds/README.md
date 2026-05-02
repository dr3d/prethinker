# Story-World And Source-World Datasets

Curated narrative and source-record fixtures for testing Prethinker's
source-fidelity, event-order, subjective-judgment, final-state, speech-vs-truth,
claim/finding, policy, temporal, and rule-ingestion behavior.

These are checked-in calibration assets, not generated traces. Runtime runs,
trace HTML, bakeoff output, and local model artifacts should stay under
`tmp/`.

Current fixtures:

- `otters_clockwork_pie/`: a Goldilocks-shaped but source-local whimsical story
  designed to expose template contamination, predicate drift, chronology loss,
  and weak final-state modeling.
- `iron_harbor_water_crisis/`: a municipal-policy/source-record fixture for
  temporal corrections, policy violations, multilingual witness statements, and
  claim/fact separation.
- `blackthorn_misconduct_case/`: a procedural misconduct fixture for authority
  chains, deadlines, findings, sanctions, corrections, and stage-aware epistemic
  state.
- `kestrel_claim/`: a maritime-insurance fixture for competing accounts,
  source-attributed legal/financial positions, dual-role entities, and temporal
  arithmetic.
- `glass_tide_charter/`: a rule-ingestion fixture for source-stated executable
  rules, exceptions, overrides, bounded negation, evidence ranking, and
  permission-vs-event boundaries.

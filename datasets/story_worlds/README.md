# Story-World And Source-World Datasets

Curated narrative and source-record fixtures for testing Prethinker's
source-fidelity, event-order, subjective-judgment, final-state, speech-vs-truth,
claim/finding, policy, temporal, and rule-ingestion behavior.

These are checked-in calibration assets, not generated traces. Runtime runs,
trace HTML, bakeoff output, and local model artifacts should stay under
`tmp/`.

## Intake Policy

`tmp/incoming*` is only a short validation/staging area for newly supplied
fixtures. It is not a research home. Once a fixture has valid source and QA
assets, promote it into `datasets/story_worlds/` and record all durable lessons
in that fixture's `progress_journal.md` and `progress_metrics.jsonl`. Generated
compile/QA JSON can remain under `tmp/`, but scorecards, selector lessons, and
artifact references should be summarized in tracked journals.

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
- `copperfall_deadline_docket/`: a temporal docket fixture for deadline
  arithmetic, tolling, corrections, party stipulations, and point-in-time case
  status.
- `harrowgate_witness_file/`: a claim-versus-truth fixture for disputed
  testimony, official non-substantiation, source attribution, and evidentiary
  gaps.
- `larkspur_clockwork_fair/`: a longitudinal story-world fixture for near-miss
  identity, object-state changes, custody chains, official authority, and
  final-state queries.
- `meridian_permit_board/`: a permit-board rule-conflict fixture for multiple
  interpretations, coverage calculations, overlay priority, and corrections.
- `northbridge_authority_packet/`: a cross-document authority fixture for
  conflicting project records, advisory versus binding documents, and
  parameter-specific control.

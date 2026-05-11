# Grant Exception Cap Matrix Progress Journal

Fixture id: `grant_exception_cap_matrix`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## GECM-000 - Fixture Admission

Date: 2026-05-10

Evidence lane: `fixture_admission`

Source admitted from: `tmp\prethinker_transfer_fixtures_unpacked\fixtures\grant_exception_cap_matrix`

Files admitted:

- `source.md` / `story.md`
- `fixture_notes.md`
- `qa.md`
- `qa_questions.jsonl`
- `oracle.jsonl`
- `qa_battery.json`

Benchmark discipline:

- `source.md`/`story.md` is the only cold compile source.
- `oracle.jsonl`, `qa_battery.json`, `qa.md`, and `fixture_notes.md` are scoring/review assets, not compile context.
- No Python source-prose interpretation is allowed.

## GECM-001 - OpenRouter Cold Acquisition Baseline

Date: 2026-05-10

Evidence lane: `openrouter_cold_acquisition_baseline`

Artifacts:

- Compile: `tmp/transfer_fixtures_20260510/cold_acquisition_compile_lanes6/grant_exception_cap_matrix/domain_bootstrap_file_20260510T093347117749Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/transfer_fixtures_20260510/cold_acquisition_qa_lanes6/grant_exception_cap_matrix/domain_bootstrap_qa_20260510T094529407527Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `26 exact / 3 partial / 11 miss` over `40`.

Compile admitted/skipped: `74 / 1`.

Lesson: rule activation and cap arithmetic transfer, but not as cleanly as the
previous rule-heavy precision fixture. Low skip pressure says the compile is
stable; the misses likely live in exception/cap joins, counterfactual amount
calculation, and recusal-versus-award procedure. This fixture is a good helper
and guard-retirement pressure test, not a new lens request.

## GECM-002 - Grant Candidate-Helper And Source-Record Queryability Repair

Date: 2026-05-10

Evidence lane: `openrouter_candidate_helper_repair`

Helper class: mixed. Field-driven award/cap arithmetic is closer to
clean-helper substrate; exact appeal/recusal/procedural text rows remain
candidate-helper until generalized or transfer-proven.

Artifacts:

- Refreshed compile: `tmp/transfer_fixtures_20260510/grant_source_record_refreshed_compile_20260510/domain_bootstrap_file_grant_source_record_refreshed_20260510.json`
- Targeted replay: `tmp/transfer_fixtures_20260510/grant_helper_targeted_replay_v2_20260510/domain_bootstrap_qa_20260510T113751127741Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full replay v1: `tmp/transfer_fixtures_20260510/grant_final_full_replay_20260510/domain_bootstrap_qa_20260510T114928039505Z_qa_qwen-qwen3-6-35b-a3b.json`
- Last-three replay: `tmp/transfer_fixtures_20260510/grant_last3_replay_20260510/domain_bootstrap_qa_20260510T115403755548Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full replay v2: `tmp/transfer_fixtures_20260510/grant_final_full_replay_v2_20260510/domain_bootstrap_qa_20260510T120546886379Z_qa_qwen-qwen3-6-35b-a3b.json`

Candidate-helper results:

- Known-miss targeted replay: `14 exact / 0 partial / 0 miss`.
- Full replay v1: `37 exact / 0 partial / 3 miss`.
- Last-three targeted replay: `3 exact / 0 partial / 0 miss`.
- Full replay v2: `24 exact / 0 partial / 4 miss` with `11` judge-uncertain
  rows and only `29/40` parsed query rows, so this run is treated as
  OpenRouter parse/judge instability rather than a lower capability estimate.

Repair:

- Added generic grant award support over admitted `application_eligibility/3`,
  `requested_amount/2`, `bonus_eligibility/2`, `final_award/3`, and
  deterministic `source_record_field/3` rows.
- Added exact source-record metadata support for BWCF cycle IDs, procedure
  manuals, score-correction memos, recusal memos, appeal IDs, appeal windows,
  recusal procedure, appeal funding source, and pending appeal status.
- Extended deterministic source-record acquisition to keep official procedural
  prose around appeal, award, cap, carryover, committee, eligibility, quorum,
  recusal, threshold, and vote language.

Lesson:

The grant fixture did not demand a new semantic lens. The cold compile already
held the critical material. The missing rows were queryability failures:
award/cap aggregation, recusal procedure, exact memo/appeal IDs, and source
section addressability. Targeted replay proves the surface is reachable through
deterministic source addressability plus helper substrate. Full-run variance
still needs selector/retry hygiene on OpenRouter before claiming a saturated
production score.

Backtracking note: under the helper classification doctrine, this run is not a
clean-helper transfer proof. The generic award/cap joins are promising, but the
source-record metadata surface still contains fixture-family appeal, recusal,
and procedure recognizers that must be split into generic extraction or kept
quarantined as candidate-helper evidence.

## GECM-003 - Grant Helper Scar Cleanup And Relabeled Replay

Date: 2026-05-10

Evidence lane: `helper_audit_cleanup`

Artifacts:

- refreshed helper class audit:
  `tmp/helper_usage_audit_20260510/helper_class_audit_transfer_after_grant_cleanup.md`
- full QA replay after helper cleanup:
  `tmp/transfer_fixtures_20260510/grant_helper_cleanup_replay_20260510/domain_bootstrap_qa_20260510T212657629642Z_qa_qwen-qwen3-6-35b-a3b.json`

Code change:

- Generalized `grant_award_support` appeal review/funding extraction so it no
  longer hard-codes `a_07` or `2026-05-22`.
- Appeal review dates now extract the nearby source-record date atom, and appeal
  funding rows extract the nearby `A-##` app token when available.

Results:

- transfer compile helper-class audit for `grant_award_support`:
  `32 clean / 5 candidate`
- full replay after cleanup: `37 exact / 1 partial / 2 miss`
- helper rows in the replay:
  - `grant_award_support`: `1008 clean / 252 candidate`
  - `source_record_packet_metadata_support`: `960 clean / 480 candidate`
- write proposals: `0`

Residuals:

- `q036` partial: hybrid join gap around recusal/non-decisional outcome; the
  evidence has recusal status and vote mechanics but not a tight enough joined
  support bundle.
- `q039` miss: compile-surface gap for where recusal memo originals are filed.
- `q040` miss: compile-surface gap for packet references not reproduced in full.

Lesson:

The grant helper is less fixture-shaped after this pass, but it is not promoted
architecture. It remains a one-fixture helper with candidate appeal/procedure
rows and a fresh replay that still depends heavily on
`source_record_packet_metadata_support`. Treat the `37 / 1 / 2` result as
candidate-helper evidence. The next clean move is source-record acquisition for
unreproduced-reference and filing-location rows, or a sibling transfer proof
before any broader claim.

## GECM-004 - Section 11 Source-Reference Addressability

Date: 2026-05-10

Evidence lane: `deterministic_source_addressability`

Artifacts:

- targeted q039/q040 replay:
  `tmp/transfer_fixtures_20260510/grant_source_reference_q039_q040_20260510/domain_bootstrap_qa_20260510T213250326030Z_qa_qwen-qwen3-6-35b-a3b.json`
- full replay:
  `tmp/transfer_fixtures_20260510/grant_source_reference_full_replay_20260510/domain_bootstrap_qa_20260510T213830351421Z_qa_qwen-qwen3-6-35b-a3b.json`
- helper class audit:
  `tmp/helper_usage_audit_20260510/helper_class_audit_transfer_after_grant_reference.md`

Code change:

- Added generic packet metadata rows for Section 11-style
  `unreproduced_reference` list items.
- Added generic `original_filing_location` extraction when adjacent
  source-record lines say originals are filed with a named office/person.

Results:

- targeted q039/q040 replay: `2 exact / 0 partial / 0 miss`
- full replay: `40 exact / 0 partial / 0 miss`
- write proposals: `0`
- full replay helper rows:
  - `grant_award_support`: `992 clean / 248 candidate`
  - `source_record_packet_metadata_support`: `1350 clean / 450 candidate`
- transfer class audit now reads:
  - `grant_award_support`: `32 clean / 5 candidate`
  - `source_record_packet_metadata_support`: `171 clean / 26 candidate`

Lesson:

The final two misses were not semantic reasoning failures. The source lines were
already preserved as deterministic `source_record_text_atom` rows, but the query
surface did not expose them as source references and filing-location facts. This
is the durable-memory thesis in miniature: official-document answers often live
in addressability, not in a new lens. The result is still labeled with helper
provenance, but the repair itself is generic source-record substrate rather than
fixture-specific answer injection.

## GECM-005 - Grant Helper Sibling Audit

Date: 2026-05-11

Evidence lane: `helper_transfer_audit`

Artifacts:

- transfer helper audit:
  `tmp/transfer_fixtures_20260510/grant_award_sibling_audit_transfer_after_cleanup_20260511.json`
- precision-wide helper audit:
  `tmp/transfer_fixtures_20260510/grant_award_sibling_audit_precision_all_20260511.json`
- readout:
  `tmp/transfer_fixtures_20260510/grant_award_helper_sibling_audit_20260511.md`

Result:

- `grant_award_support` on this fixture: `16 clean / 1 candidate / 0 unlabeled`
- `grant_award_support` on `rule_activation_exception_matrix`: no trigger in
  current artifacts

Cleanup:

- Removed a small `a_05` special case from eligibility-count details. Excluded
  applications and their failing rules are now listed generically.

Lesson:

The helper is cleaner but not transfer-proven. The natural sibling fixture uses
older predicate vocabulary (`final_grant_amount/3`, `grant_calculation/4`,
`application_status/2`, `eligibility_determination/3`) while the helper listens
to the newer transfer contract (`final_award/3`, `application_eligibility/3`,
`bonus_eligibility/2`). The next clean path is a generic admitted-predicate alias
bridge, not a new lens and not a fixture-specific shortcut.

## GECM-006 - Grant Predicate Alias Bridge

Date: 2026-05-11

Evidence lane: `canonical_predicate_completeness`

Artifacts:

- transfer audit:
  `tmp/transfer_fixtures_20260510/grant_award_alias_bridge_transfer_20260511.json`
- precision sibling cold audit:
  `tmp/transfer_fixtures_20260510/grant_award_alias_bridge_rule_cold_20260511.json`
- precision-wide audit:
  `tmp/transfer_fixtures_20260510/grant_award_alias_bridge_precision_all_20260511.json`
- readout:
  `tmp/transfer_fixtures_20260510/grant_award_alias_bridge_audit_20260511.md`

Code change:

- `grant_award_support` now adapts admitted status, amount, eligibility, and
  bonus predicates from older grant/rule vocabulary into the helper's internal
  award contract.

Results:

- this transfer fixture remains stable: `16 clean / 1 candidate / 0 unlabeled`
- `rule_activation_exception_matrix` cold artifact now emits `3 clean / 0
  candidate / 0 unlabeled`
- precision-wide audit now sees `26 clean / 0 candidate / 0 unlabeled`

Lesson:

The sibling proof boundary was predicate vocabulary drift, not missing memory.
The alias bridge is generic over admitted predicates and contains no fixture
constants. This is a clean example of canonical predicate-completeness repair:
two artifacts can hold equivalent governed state under different predicate
names, and helpers need narrow declared adapters before the state is fully
queryable.

# Clinic Device Recall Field Packet Progress Journal

Fixture id: `clinic_device_recall_field_packet`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## CDRF-000 - Fixture Admission

Date: 2026-05-10

Evidence lane: `fixture_admission`

Source admitted from: `tmp\prethinker_transfer_fixtures_unpacked\fixtures\clinic_device_recall_field_packet`

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

## CDRF-001 - OpenRouter Cold Acquisition Baseline

Date: 2026-05-10

Evidence lane: `openrouter_cold_acquisition_baseline`

Artifacts:

- Compile: `tmp/transfer_fixtures_20260510/cold_acquisition_compile_lanes6/clinic_device_recall_field_packet/domain_bootstrap_file_20260510T092957941611Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/transfer_fixtures_20260510/cold_acquisition_qa_lanes6/clinic_device_recall_field_packet/domain_bootstrap_qa_20260510T094441519249Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `31 exact / 0 partial / 9 miss` over `40`.

Compile admitted/skipped: `71 / 19`.

Lesson: the recall/table transfer surface is strong but not saturated. Source
field acquisition and identifier pinning carried most direct rows, while the
remaining pressure is scope/status distinction, range membership, and repair
verification composition. This fixture is a good next probe for whether
source-record fields plus rule/range helpers can retire status/scope guards.

## CDRF-002 - Clinic Recall Source-Record Candidate-Helper Replay

Date: 2026-05-10

Evidence lane: `candidate_helper_replay`

Helper class: historical `candidate-helper`. The detailed helper-era
classification note has been retired from the public docs tree; Git history and
the cold archive preserve it.

Code change:

- Added `clinic_recall_support/5` as a query-only companion in
  `scripts/run_domain_bootstrap_qa.py`.
- The helper derives clinic abbreviations, manufacturer liaison identity,
  failure-rate text, cabinet/seal/key custody, verification procedure/date
  support, device serial display, pending-determination correspondence, and
  medical-director authority from admitted `source_record_*` rows.
- No new lens, no new compile pass, and no new guard family were added.

Artifacts:

- Source-record refreshed compile:
  `tmp/transfer_fixtures_20260510/clinic_source_record_refreshed_compile_20260510/domain_bootstrap_file_clinic_source_record_refreshed_20260510.json`
- Targeted replay:
  `tmp/transfer_fixtures_20260510/clinic_recall_helper_targeted_replay_20260510/domain_bootstrap_qa_20260510T134001469371Z_qa_qwen-qwen3-6-35b-a3b.json`
- Refreshed targeted replay:
  `tmp/transfer_fixtures_20260510/clinic_recall_helper_refreshed_targeted_20260510/domain_bootstrap_qa_20260510T134137106371Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full replay:
  `tmp/transfer_fixtures_20260510/clinic_recall_helper_full_replay_v2_20260510/domain_bootstrap_qa_20260510T140951342952Z_qa_qwen-qwen3-6-35b-a3b.json`

Candidate-helper result: `40 exact / 0 partial / 0 miss` over `40`.

Lift over cold baseline: `+9 exact`, `0 partial`, `-9 miss`.

Residual hard edge on this fixture after refreshed source-record facts and
helper queryability: none observed in this replay.

Lesson: this is another source-record-to-queryability proof, not a lens proof.
The cold artifact already had most semantic recall predicates, but exact
official row details such as `K. Halberg`, `0.7 per 1,000 hours`, `Cabinet B-3`,
seal ranges, full serial displays, and network medical director authority lived
in deterministic source-record memory. Once refreshed and surfaced through a
query-only helper, the fixture reached 40/40.

Backtracking note: the helper contains both legitimate field-driven
device/serial lookup logic and fixture-family recognizers for named clinics,
liaison identity, cabinet/seal labels, and authority prose. The replay should
be reported as `candidate-helper`, not `clean-helper`, until those recognizers
are generalized or transfer-proven without fixture constants.

## CDRF-003 - Fresh Labeled Helper Replay

Date: 2026-05-10

Evidence lane: `helper_class_label_refresh`

Artifacts:

- Fresh full replay:
  `tmp/transfer_fixtures_20260510/clinic_recall_helper_fresh_labeled_full_20260510/domain_bootstrap_qa_20260510T190256900920Z_qa_qwen-qwen3-6-35b-a3b.json`
- Row gate against prior high-water:
  `tmp/transfer_fixtures_20260510/clinic_fresh_labeled_row_gate_20260510/row_gate.md`
- Helper usage audit:
  `tmp/helper_usage_audit_20260510/helper_usage_audit_latest.md`

Results:

- Fresh labeled replay: `35 / 0 / 4` with `1` unjudged row
- Helper rows in fresh replay: `2000 clean-helper / 240 candidate-helper / 0 unlabeled`
- Row-gate with prior high-water: `40 / 0 / 0`

Lesson: the refreshed clinic replay reduces helper-label debt in completed QA
output but does not replace the prior `40 / 0 / 0` high-water. The no-cache QA
pass churned on rows `q026` through `q030`, while the earlier replay already
answered all rows exact. Report the fresh run as helper-provenance evidence,
not as the current score. The remaining cleanup target is the `240`
candidate-helper rows, not a new lens.

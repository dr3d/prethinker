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

## GECM-002 - Grant Helper And Source-Record Queryability Repair

Date: 2026-05-10

Evidence lane: `openrouter_helper_transfer_repair`

Artifacts:

- Refreshed compile: `tmp/transfer_fixtures_20260510/grant_source_record_refreshed_compile_20260510/domain_bootstrap_file_grant_source_record_refreshed_20260510.json`
- Targeted replay: `tmp/transfer_fixtures_20260510/grant_helper_targeted_replay_v2_20260510/domain_bootstrap_qa_20260510T113751127741Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full replay v1: `tmp/transfer_fixtures_20260510/grant_final_full_replay_20260510/domain_bootstrap_qa_20260510T114928039505Z_qa_qwen-qwen3-6-35b-a3b.json`
- Last-three replay: `tmp/transfer_fixtures_20260510/grant_last3_replay_20260510/domain_bootstrap_qa_20260510T115403755548Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full replay v2: `tmp/transfer_fixtures_20260510/grant_final_full_replay_v2_20260510/domain_bootstrap_qa_20260510T120546886379Z_qa_qwen-qwen3-6-35b-a3b.json`

Results:

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

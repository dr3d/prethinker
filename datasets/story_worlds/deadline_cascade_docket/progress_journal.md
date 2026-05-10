# Deadline Cascade Docket Progress Journal

Fixture id: `deadline_cascade_docket`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## DCD-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming_validation_20260508_new6\deadline_cascade_docket`

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


## DCD-001 - Period/Deadline Registry Candidate

Date: 2026-05-08

Evidence lane: `registry_scaffold_candidate`

Artifacts:

- Registry: `tmp/regulatory_period_deadline_registry_v1.json`
- Compile: `tmp/incoming_6_registry_period_probe_20260508/deadline_cascade_docket/domain_bootstrap_file_20260508T080238625909Z_source_qwen-qwen3-6-35b-a3b.json`
- First-10 QA: `tmp/incoming_6_registry_period_probe_20260508/deadline_cascade_docket_qa_first10/domain_bootstrap_qa_20260508T080527148382Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full-40 QA: `tmp/incoming_6_registry_period_probe_20260508/deadline_cascade_docket_qa_full40/domain_bootstrap_qa_20260508T081500883442Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Direct registry compile admitted `53` rows and skipped `22`.
- First-10 replay reached `10 exact / 0 partial / 0 miss`, improving the cold-smoke slice from `8 / 1 / 1`.
- Full-40 replay reached `35 exact / 3 partial / 2 miss`, with `0` write proposals and `0` runtime load errors.

Lesson:

The q002 violation-period miss was not fixed by broader policy/operational prose
pressure. A broad policy hint left q002 missed; an explicit violation-period
prompt went skip-heavy and regressed q006. The useful shape was a vocabulary
scaffold that gave the profile an actual `violation_period/4` surface while
keeping notice issue dates and response deadlines separate.

Promotion status:

Candidate only. The registry is too thin and skip-heavy for global promotion,
but it is a promising row-gated or fixture-mode surface for regulatory notices
where underlying occurrence periods differ from document/action dates. Next
transfer check should use another regulatory/notice-like fixture before adding
this surface to the permanent lens roster.

Remaining full-40 misses/partials:

- q011: response included a compliance-schedule request; missing inclusion/content surface.
- q023: Board holiday calendar absent.
- q037: exclusive authority for formal compliance determinations absent.
- q038: implemented biweekly sampling as of September 1 absent.
- q040: revised-plan rejection consequence and pending original appeal interaction absent.

## DCD-002 - Residual Sampling And Appeal-Consequence Repair

Date: 2026-05-08

Evidence lane: `row_gated_residual_repair`

Artifacts:

- Compile: `tmp\deadline_residual_compile_20260508\domain_bootstrap_file_20260508T143825311706Z_source_qwen-qwen3-6-35b-a3b.json`
- Residual QA q038/q040: `tmp\deadline_residual_qa_20260508\domain_bootstrap_qa_20260508T143910544715Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Residual rows: `2 exact / 0 partial / 0 miss`
- Writes/errors: `0` / `0`

Meaning lesson:

Deadline dockets need to preserve implemented practice separately from formal
compliance status. Granger's biweekly sampling began on its own initiative as
of September 1, but formal compliance still depends on Board action. Conditional
future consequences also need explicit rows: if the revised plan is rejected, a
new appeal window opens while the existing appeal of the original rejection
remains pending.

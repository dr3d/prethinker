# Larkspur Clockwork Fair Progress Journal

Fixture id: `larkspur_clockwork_fair`

This journal records durable research findings for the Larkspur incoming
fixture. Generated run artifacts may live under `tmp/`; the lessons and artifact
references belong here.

## LCF-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming_staged/larkspur_clockwork_fair`

Files admitted:

- `source.md` / `story.md`
- `fixture_notes.md`
- `qa.md`
- `qa_questions.jsonl`
- `oracle.jsonl`
- `qa_authored_with_answers.jsonl`

Benchmark discipline:

- `source.md`/`story.md` is the only cold compile source.
- `oracle.jsonl`, `qa_authored_with_answers.jsonl`, `qa.md`, and
  `fixture_notes.md` are scoring/review assets, not compile context.
- No Python source-prose interpretation is allowed.

## LCF-001 - Incoming First-10 Smoke

Date: 2026-05-04

Evidence lane: `cold_unseen`

Mode: incoming standard first-10 smoke.

Artifacts:

- Baseline scorecard: `tmp/incoming_smoke_summaries/scorecard.md`
- Scoped-evidence scorecard: `tmp/incoming_smoke_summaries_scoped_evidence/scorecard.md`

Result:

- Compile: `195` admitted operations, `1` skip.
- Compile health: `healthy`.
- QA first-10: `8 exact / 2 partial / 0 miss`.
- Non-exacts: q007 youngest exhibitor and q009 Fair Warden identity.
- Safety: `0` write-proposal rows.

Lesson:

The cold compile captured the broad story surface but had right-shaped/wrong-slot
gaps around numeric character attributes and named-official duty/authority.

## LCF-002 - Attribute/Duty Guardrail And Official Companion

Date: 2026-05-04

Evidence lane: `diagnostic_replay`

Mode: narrative compile guardrail plus post-ingestion official-identity
companion query.

Artifacts:

- Attribute/duty compile:
  `tmp/incoming_cold_runs/larkspur_clockwork_fair_attribute_duty_guardrail_repair/domain_bootstrap_file_20260504T151723343869Z_source_qwen-qwen3-6-35b-a3b.json`
- Companion QA first-10:
  `tmp/incoming_cold_qa/larkspur_clockwork_fair_attribute_duty_guardrail_companion_first10/domain_bootstrap_qa_20260504T152559315473Z_qa_qwen-qwen3-6-35b-a3b.json`
- Overlay plan:
  `tmp/incoming_smoke_summaries_official_companion_overlay/compile_variant_overlay_plan.md`

Result:

- Guarded compile health: `poor`; not a global promotion.
- Companion first-10: `9 exact / 0 partial / 1 miss`.
- Rescued rows: q007 and q009.
- Regression: q010 exact -> miss in the guarded compile variant.

Lesson:

The compiler guardrail is useful row-level lensing, not a replacement compile.
The QA companion repaired official identity by querying admitted authority/action
surface for `person_role(Constant, Role)` rows. Exact-row protection must keep
q010 on baseline.

## LCF-003 - Variant Selector Calibration

Date: 2026-05-04

Evidence lane: `selector_calibration`

Artifacts:

- Variant selector training plan:
  `tmp/incoming_smoke_summaries_official_companion_overlay/variant_selector_training_plan.md`
- Volume-gate selector comparison:
  `tmp/incoming_variant_selector_runs/incoming-variant-volume-gate-v2.md`

Result:

- Larkspur activation targets: q007 and q009.
- Larkspur exact-protection target: q010.
- Guarded activation plus volume gate selected `3/3` best Larkspur rows.

Lesson:

Larkspur is now a compact selector calibration fixture: activate the
attribute/duty companion for youngest-exhibitor and official-identity rows, but
protect the baseline recovery-event row.

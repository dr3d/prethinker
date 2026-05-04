# Northbridge Authority Packet Progress Journal

Fixture id: `northbridge_authority_packet`

This journal records durable research findings for the Northbridge incoming
fixture. Generated run artifacts may live under `tmp/`; the lessons and artifact
references belong here.

## NAP-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming_staged/northbridge_authority_packet`

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

## NAP-001 - Scoped-Evidence Incoming Smoke

Date: 2026-05-04

Evidence lane: `cold_unseen`

Mode: scoped compile repair plus evidence-bundle context filtering.

Artifacts:

- Scoped-evidence scorecard:
  `tmp/incoming_smoke_summaries_scoped_evidence/scorecard.md`
- Northbridge scoped-evidence QA:
  `tmp/incoming_cold_qa/northbridge_authority_packet_resolution_vote_repair_evidence_first10/domain_bootstrap_qa_20260504T144632564199Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Compile: `101` admitted operations, `5` skips.
- Compile health: `warning`.
- QA first-10: `9 exact / 1 partial / 0 miss`.
- Remaining non-exact: q007 hydrant requirement, classified
  `compile_surface_gap`.
- Safety: `0` write-proposal rows.
- Semantic progress: medium risk,
  `continue_only_with_named_expected_contribution`.

Lesson:

Northbridge is a cross-document authority fixture with medium progress risk:
the compiler can answer most authority parameters, but hydrant support needs
more answer-bearing detail than a count-only requirement row.

## NAP-002 - Hydrant-Spacing Compile Variant

Date: 2026-05-04

Evidence lane: `diagnostic_replay`

Mode: shifted hydrant-spacing compile variant.

Artifacts:

- Compile:
  `tmp/incoming_cold_runs/northbridge_authority_packet_hydrant_spacing_repair/domain_bootstrap_file_20260504T145707708807Z_source_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/incoming_cold_qa/northbridge_authority_packet_hydrant_spacing_repair_first10/domain_bootstrap_qa_20260504T150349440257Z_qa_qwen-qwen3-6-35b-a3b.json`
- Overlay plan:
  `tmp/incoming_smoke_summaries_official_companion_overlay/compile_variant_overlay_plan.md`

Result:

- Variant first-10: `9 exact / 1 partial / 0 miss`.
- Rescued row: q007.
- Exact-protection row: q004 stays better on baseline/scoped-evidence.

Lesson:

Hydrant-spacing support is an answer-bearing detail, not merely extra evidence.
The selector must distinguish count-only partial support from count-plus-spacing
support.

## NAP-003 - Variant Selector Calibration

Date: 2026-05-04

Evidence lane: `selector_calibration`

Artifacts:

- Variant selector training plan:
  `tmp/incoming_smoke_summaries_official_companion_overlay/variant_selector_training_plan.md`
- Volume-gate selector comparison:
  `tmp/incoming_variant_selector_runs/incoming-variant-volume-gate-v2.md`

Result:

- Northbridge activation target: q007.
- Northbridge exact-protection target: q004.
- Guarded activation plus volume gate selected `1/2` best Northbridge rows.
- Remaining selector miss: q007 stays partial because the selector treats
  count-only SWIFA support as complete enough and fails to prefer the
  spacing-bearing variant.

Lesson:

Northbridge is now the active selector-relevance frontier. The remaining issue
is requirement-detail completeness, not structural row volume.

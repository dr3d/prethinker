# Three Moles Moon-Marmalade Progress Journal

Fixture id: `three_moles_moon_marmalade_machine_v1`

This is the running research record for the Three Moles fixture.

## MMM-000 - Fixture Admission

Date: 2026-05-03

Source: `tmp/The Three Moles and the Moon-Marmalade Machine/`

Files admitted:

- `story.md`
- `source.md`
- `qa_source.md`
- `qa.md`
- `README.md`
- `progress_journal.md`
- `progress_metrics.jsonl`

No model run was executed.

Benchmark discipline:

- This fixture has no gold KB.
- This fixture has no supplied strategy/intake-plan notes.
- This fixture has no ontology registry.
- `qa.md` and `qa_source.md` are scoring assets, not source-compilation
  context.

Expected research value:

- A fresh story-world probe that is related to Otters in form but not in local
  entities or magic mechanics.
- Useful for checking whether story-world guidance generalizes without
  overfitting to one fixture.
- Directly pressures prior contamination, object-state causality, speech/truth
  separation, final-state updates, and restitution coverage.

## MMM-001 - Cold Semantic Parallax Baseline

Date: 2026-05-03

Evidence lane: `cold_unseen`

Mode: source-only profile bootstrap plus current semantic-parallax compile:
flat-plus-focused intake-plan passes, compact focused-pass operations schema,
and LLM-authored source entity ledger. No gold KB, starter registry, or QA
source was used during compilation.

Artifacts:

- Compile:
  `tmp/cold_baselines/three_moles/domain_bootstrap_file_20260503T044804573005Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/three_moles/domain_bootstrap_qa_20260503T045525066737Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Compile: `174` admitted operations, `10` skips, `110` unique facts, `0`
  rules.
- QA: `10 exact / 8 partial / 22 miss` over `40` questions.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `22` compile-surface gaps, `4` hybrid-join gaps, `2`
  query-surface gaps, `2` answer-surface gaps.

Lesson:

This is a useful low cold baseline. The model built a large source surface, but
most misses are still compile-support gaps. Three Moles should stress whether
the story-world lenses can preserve repeated magical object families, final
state, and causality without leaning on Otters-specific context.

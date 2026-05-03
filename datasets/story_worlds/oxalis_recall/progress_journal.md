# The Oxalis Recall Progress Journal

This journal records cold, diagnostic, assisted, and oracle-calibration runs for
this fixture. Keep evidence lanes separate.

## Fixture Admission

- Timestamp: `2026-05-03`
- Evidence lane: `fixture_admission`
- Source files admitted from: `tmp/oxalis_recall`
- Initial status: source and 40-question QA battery installed; no compile or QA
  run has been executed.

## First Baseline Plan

Use the current source-only semantic-parallax cold baseline recipe:

```text
story.md
  -> source-only profile bootstrap
  -> flat-plus-focused semantic-parallax compile
  -> mapper admission
  -> QA over admitted KB
```

No gold KB, starter registry, strategy document, or QA answer key should be used
for source compilation in the cold lane.

## Run OX-001 - Cold Semantic Parallax Baseline

- Timestamp: `2026-05-03T15:36Z` through `2026-05-03T15:44Z`
- Evidence lane: `cold_unseen`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only profile bootstrap plus current semantic-parallax compile:
  flat-plus-focused intake-plan passes, compact focused-pass operations schema,
  and LLM-authored source entity ledger. No gold KB, starter registry, strategy
  file, or QA source was used during compilation.

### Artifacts

- Compile:
  `tmp/cold_baselines/oxalis_recall/domain_bootstrap_file_20260503T153614838562Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/oxalis_recall/domain_bootstrap_qa_20260503T154413658124Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: `106` admitted operations, `0` skips, `94` unique facts, `0`
  rules.
- Profile rough score: `0.833` with `23` candidate predicates.
- QA: `16 exact / 9 partial / 15 miss` over `40` questions.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `16` compile-surface gaps, `2` query-surface gaps, `6`
  hybrid-join gaps.

### Lesson

Oxalis is a useful counterweight to the strong Dulse score. The compile admitted
many rows with no mapper skips, but downstream QA still missed deadline values,
scope expansions, distributor counts, termination status, unit-accounting
percentages, quote details, and chronological status summaries. This is the
clearest recent reminder that "clean admission" is not the same as
answer-bearing coverage. The pass plan captured product, lot, correction,
notification, and inventory surfaces, but the classification/deadline and
termination-outcome passes were thin or duplicate-heavy. The general next move
should be richer source-surface acquisition for regulatory deadlines, status
windows, and count/percentage support, not an Oxalis-specific profile patch.


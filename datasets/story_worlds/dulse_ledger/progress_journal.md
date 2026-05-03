# The Dulse Ledger Progress Journal

This journal records cold, diagnostic, assisted, and oracle-calibration runs for
this fixture. Keep evidence lanes separate.

## Fixture Admission

- Timestamp: `2026-05-03`
- Evidence lane: `fixture_admission`
- Source files admitted from: `tmp/dulse_ledger`
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

## Run DL-001 - Cold Semantic Parallax Baseline

- Timestamp: `2026-05-03T15:23Z` through `2026-05-03T15:31Z`
- Evidence lane: `cold_unseen`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only profile bootstrap plus current semantic-parallax compile:
  flat-plus-focused intake-plan passes, compact focused-pass operations schema,
  and LLM-authored source entity ledger. No gold KB, starter registry, strategy
  file, or QA source was used during compilation.

### Artifacts

- Compile:
  `tmp/cold_baselines/dulse_ledger/domain_bootstrap_file_20260503T152352243239Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/dulse_ledger/domain_bootstrap_qa_20260503T153106149780Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: `70` admitted operations, `21` skips, `52` unique facts, `0`
  rules.
- Profile rough score: `0.833` with `19` candidate predicates.
- QA: `27 exact / 7 partial / 6 miss` over `40` questions.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `9` compile-surface gaps, `4` hybrid-join gaps.

### Lesson

Dulse is a useful transfer baseline: strong enough to show the governance
pipeline can handle source-local custom and ledger records cold, but not so
strong that it hides the next edges. The broad skeleton and adjudication passes
carried most of the useful surface; two focused passes contributed no unique
rows, which keeps lens-health accounting relevant. The non-exacts cluster
around due/return dates, late-debt consequences, restitution after void trades,
fictional/source-bound status, counterfactual date reasoning, and unresolved
dispute summaries. This reinforces the cross-fixture theme: the next gains are
not one fixture patch, but better temporal/status support, consequence rows,
and row-level query activation over safe symbolic surfaces.


# The Thornfield Variance Progress Journal

This journal records cold, diagnostic, assisted, and oracle-calibration runs for
this fixture. Keep evidence lanes separate.

## Fixture Admission

- Timestamp: `2026-05-03`
- Evidence lane: `fixture_admission`
- Source files admitted from: `tmp/The Thornfield Variance`
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

## Run TV-001 - Cold Semantic Parallax Baseline

- Timestamp: `2026-05-03T16:07Z` through `2026-05-03T16:21Z`
- Evidence lane: `cold_unseen`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only profile bootstrap plus current semantic-parallax compile:
  flat-plus-focused intake-plan passes, compact focused-pass operations schema,
  and LLM-authored source entity ledger. No gold KB, starter registry, strategy
  file, or QA source was used during compilation.

### Artifacts

- Compile:
  `tmp/cold_baselines/thornfield_variance/domain_bootstrap_file_20260503T160714907421Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/thornfield_variance/domain_bootstrap_qa_20260503T161432730355Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: `67` admitted operations, `7` skips, `63` unique facts, `0`
  rules.
- Profile rough score: `0.889` with `15` candidate predicates.
- Compile-lens health: `warning`; the post-hearing/appeal pass was thin
  (`pass_5`).
- QA: `20 exact / 6 partial / 14 miss` over `40` questions.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `14` compile-surface gaps, `4` query-surface gaps, `1`
  hybrid-join gap, and `1` answer-surface gap.

### Lesson

Thornfield mirrors Sable's broad shape while stressing a different procedural
domain. The compiler preserved zoning-code rules as facts, property baselines,
notice records, board findings, and vote rows, but admitted `0` executable
rules. The non-exacts cluster around survey recency/authority, individual vote
aggregation, omitted or qualitative testimony, setback/eave dimensional
details, attorney/ruling authority, and post-hearing appeal state. This keeps
the next general target squarely on answer-bearing source-surface acquisition
plus rule/query composition, not fixture-specific vocabulary patches.


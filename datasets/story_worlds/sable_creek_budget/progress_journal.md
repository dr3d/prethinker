# The Sable Creek Budget Amendment Progress Journal

This journal records cold, diagnostic, assisted, and oracle-calibration runs for
this fixture. Keep evidence lanes separate.

## Fixture Admission

- Timestamp: `2026-05-03`
- Evidence lane: `fixture_admission`
- Source files admitted from: `tmp/sable_creek_budget`
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

## Run SC-001 - Cold Semantic Parallax Baseline

- Timestamp: `2026-05-03T15:54Z` through `2026-05-03T16:10Z`
- Evidence lane: `cold_unseen`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only profile bootstrap plus current semantic-parallax compile:
  flat-plus-focused intake-plan passes, compact focused-pass operations schema,
  and LLM-authored source entity ledger. No gold KB, starter registry, strategy
  file, or QA source was used during compilation.

### Artifacts

- Compile:
  `tmp/cold_baselines/sable_creek_budget/domain_bootstrap_file_20260503T155415725989Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/sable_creek_budget/domain_bootstrap_qa_20260503T160232424514Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: `58` admitted operations, `9` skips, `49` unique facts, `0`
  rules.
- Profile rough score: `0.778` with `19` candidate predicates.
- Compile-lens health: `warning`; the two amendment-cycle passes were thin
  (`pass_2` and `pass_3`).
- QA: `20 exact / 8 partial / 12 miss` over `40` questions.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `13` compile-surface gaps, `5` query-surface gaps, `1`
  hybrid-join gap, and `1` answer-surface gap.

### Lesson

Sable first exposed a source-only profile-bootstrap JSON boundary failure: the
model placed a repeated prose phrase into a candidate predicate argument-role
slot until JSON broke. That was fixed with a general schema constraint on
profile argument role names: short snake-case roles only, values and examples
belong later in candidate operations. This is structural harness hygiene, not
domain-specific language handling.

The score itself is a useful middle baseline. The compiler captured charter
rules, emergency authority, reserve rows, and public-input structure, but it was
thin on the two amendment cycles. Non-exacts cluster around individual vote
records, amendment outcome/tally support, reserve-balance starting values,
public-comment authority boundaries, emergency-ratification query shape, and
counterfactual transfer-limit reasoning. This is a good rule/composition target:
the source contains many explicit rules, but the cold compile admitted `0`
executable rules.


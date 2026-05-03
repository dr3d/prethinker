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

## Run SC-002 - Rule-Lens Safety Diagnostic

- Timestamp: `2026-05-03T16:25Z` through `2026-05-03T16:29Z`
- Evidence lane: `diagnostic_replay`
- Mode: source-derived temporary registry from SC-001 plus a narrow Section A
  rule lens. No gold KB, starter profile, QA answer key, or reference rule
  surface was used.

### Artifacts

- Broad timed-out replay:
  `tmp/cold_baselines/sable_creek_budget/rules/domain_bootstrap_file_20260503T162549707468Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Narrow pre-guard replay:
  `tmp/cold_baselines/sable_creek_budget/rules/domain_bootstrap_file_20260503T162626955801Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Narrow post-guard replay:
  `tmp/cold_baselines/sable_creek_budget/rules/domain_bootstrap_file_20260503T162938428253Z_story-rules_qwen-qwen3-6-35b-a3b.json`

### Result

- Broad rule lens: timed out under the hard child-process deadline and emitted
  no rules.
- Narrow rule lens before safety hardening: `2` mapper-admitted clauses appeared
  promotion-ready, but both had an unbound head variable (`Amendment`) and were
  unsafe generalizations.
- New mapper/verifier guards:
  - skip rule clauses whose head variables are not bound in the body;
  - skip `operation="rule"` candidates whose clause is fact-shaped rather than
    an executable `Head :- Body` Horn rule.
- Narrow rule lens after safety hardening: `0` admitted rules, `6` skips.
  The skips were `2` fact-shaped rule clauses, `2` unbound-head rules, and `2`
  out-of-palette `append/6` attempts.

### Lesson

This is a safety-floor improvement, not a score lift. Fresh municipal-charter
material exposed a rule-acquisition shortcut that Glass Tide had not made
obvious: a rule can look promotion-ready if its head variable is free, because
the temporary runtime can produce a synthetic binding. The mapper now blocks
that before runtime trial, and the verifier reports the same condition as a
non-promotion fragment. Rule lenses must bind every head variable through body
goals and must emit real executable clauses, not fact rows wearing a rule
operation label.


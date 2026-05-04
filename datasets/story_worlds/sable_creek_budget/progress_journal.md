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

## Run SC-003 - Compact Rule-Lens Guidance Tightening

- Timestamp: `2026-05-03T16:54Z` through `2026-05-03T16:59Z`
- Evidence lane: `diagnostic_replay`
- Mode: narrow Section A rule-lens retries after the SC-002 rule-safety gates.

### Artifacts

- Compact first-order replay:
  `tmp/cold_baselines/sable_creek_budget/rules/domain_bootstrap_file_20260503T165414953882Z_story-rules_qwen-qwen3-6-35b-a3b.json`
- Compact derived-body-block replay:
  `tmp/cold_baselines/sable_creek_budget/rules/domain_bootstrap_file_20260503T165454479795Z_story-rules_qwen-qwen3-6-35b-a3b.json`

### Result

- Moving the hard rule-shape constraints into compact guidance changed the
  failure mode from unsafe promotion to controlled rejection.
- The first replay admitted `1` executable rule, but it depended on an
  unsupported `derived_status/3` body goal and therefore stayed
  non-promotable.
- The second replay added the composition boundary: first-order rule lenses
  should not use `derived_*` body goals unless an admitted dependency already
  supplies them. It admitted `0` rules and skipped the unsafe candidates.
- A broader palette retry stalled under the shell timeout and was killed. No
  Python runners remained active afterward.

### Lesson

The compact rule lens is now safer and faster, but useful rule acquisition
still needs better pass planning. There are three separate states:

```text
unsafe-looking useful rule -> blocked by mapper/verifier
syntactically valid but unsupported rule -> admitted but non-promotable
body-supported executable rule -> promotion candidate
```

Sable is currently reaching the first two states, not the third. The next
general improvement should help the rule planner choose body predicates that
are both allowed and actually present in the admitted backbone, without widening
the active palette enough to trigger slow or stalled generations.

## Run SC-004 - First Fresh-Fixture Promotion-Ready Rule

- Timestamp: `2026-05-03T17:01Z` through `2026-05-03T17:03Z`
- Evidence lane: `diagnostic_replay`
- Mode: tiny Section A rule lens with source-derived temporary registry,
  deterministic admitted-fact signature support, and a narrow active palette.

### Artifact

- Rule replay:
  `tmp/cold_baselines/sable_creek_budget/rules/domain_bootstrap_file_20260503T170243788202Z_story-rules_qwen-qwen3-6-35b-a3b.json`

### Result

- Rule lens: `2` mapper-admitted executable rules, `0` skips.
- Runtime trial: `1` firing rule, `1` promotion-ready rule, `0` runtime rule
  errors, `0` unsupported body goals.
- Promotion-ready rule:

```prolog
derived_status(AmendmentId, requires_public_hearing, budget_amendment) :-
    amendment_introduced(AmendmentId, _, _, Amount),
    number_greater_than(Amount, 50000).
```

- It derives both admitted Sable amendments as requiring a public hearing:
  `ba_2026_07` and `ba_2026_08`.
- The companion low-threshold branch loads cleanly but stays dormant because no
  admitted amendment amount is at most `50000`.

### Lesson

This is the first Sable rule-acquisition foothold under the stricter safety
gates. Two general harness changes made the difference:

- rule-lens payloads now include a deterministic admitted-fact signature
  support summary, so the LLM can see which body predicates are actually
  available without Python interpreting source prose;
- runtime trial now treats deterministic numeric-helper dormancy as dormancy,
  not missing body support, while still flagging unbound numeric-helper
  variables as unsafe fragments.

The result is still diagnostic replay, not a cold score. But it demonstrates
the target architecture on a fresh governance fixture: source rule text plus
admitted fact rows can produce a bounded, body-supported executable rule without
gold KBs, answer keys, or fixture-specific Python language handling.

## Run SC-005 - Shortcut-Audited Rule Replay

- Timestamp: `2026-05-03T23:13Z`
- Evidence lane: `diagnostic_replay`
- Mode: compact threshold rule lens rerun with embedded semantic shortcut audit
  and authored positive/negative probes.

### Artifact

- Rule replay:
  `tmp/cold_baselines/sable_creek_budget/rules/domain_bootstrap_file_20260503T231310665426Z_source-rules_qwen-qwen3-6-35b-a3b.json`

### Result

- Rule lens: `4` mapper-admitted executable rules, `4` skips.
- Runtime trial: `3` firing rules, `3` promotion-ready rules, `0` runtime rule
  errors, `0` unsupported body goals.
- Semantic shortcut audit: `4` clauses audited, `0` findings.
- Negative probe: `1/1` passed.
- Positive probes: `0/2` passed under exact authored probes.

The apparent positive-probe failure was a useful probe-shape diagnostic rather
than a body-support failure. The rule lens derived:

```prolog
derived_status(ba_2026_07, requires_public_hearing, charter_9.2).
derived_status(ba_2026_08, requires_public_hearing, charter_9.2).
```

but the authored probes expected the coarser third argument
`budget_amendment`:

```prolog
derived_status(ba_2026_07, requires_public_hearing, budget_amendment).
derived_status(ba_2026_08, requires_public_hearing, budget_amendment).
```

### Lesson

SC-005 separates three conditions that were previously easy to blur together:

```text
rule body support: good
semantic shortcut audit: clean
authored probe surface: too brittle about provenance/category slot
```

The next verifier improvement should allow authored probes to distinguish
meaning-bearing slots from provenance/category slots, probably by permitting
variables or explicit slot-equivalence policies in probe definitions. This keeps
promotion gating strict where it matters while avoiding false negatives when a
rule preserves a more precise source anchor than the probe expected.

## Run SC-006 - Any-Of Probe Groups For Promotion Verification

- Timestamp: `2026-05-04T02:42Z` through `2026-05-04T02:53Z`
- Evidence lane: `diagnostic_replay`
- Mode: narrow Section A threshold rule lens with structural any-of authored
  probes. The rule pass still received only raw source, the admitted backbone,
  an active predicate palette, and authored probe queries. No answer key or
  gold KB was used for rule acquisition or probe execution.

### Artifacts

- Rule replay:
  `tmp/cold_baselines/sable_creek_budget/rules/domain_bootstrap_file_20260504T024213518238Z_source-rules_qwen-qwen3-6-35b-a3b.json`
- Promotion-ready union:
  `tmp/cold_baselines/sable_creek_budget/union/domain_bootstrap_file_20260504T024240433863Z_sable-threshold-anyof_qwen-qwen3-6-35b-a3b.json`
- Union QA:
  `tmp/cold_baselines/sable_creek_budget/union/domain_bootstrap_qa_20260504T025105893239Z_qa_qwen-qwen3-6-35b-a3b.json`
- Mode comparison:
  `tmp/cold_baselines/sable_creek_budget/union/sable_threshold_mode_comparison.md`
- Selector:
  `tmp/cold_baselines/sable_creek_budget/union/selector_threshold_direct.json`

### Result

Rule lens:

```text
2 admitted executable rules
2 skipped
1 isolated promotion-ready rule
1 composition-ready rule
0 runtime rule errors
0 unsupported body goals
0 semantic shortcut findings
positive probes: 2/2
negative probes: 1/1
```

The promotion probe used structural any-of groups:

```prolog
derived_status(ba_2026_07, requires_public_hearing, Source)
||
derived_condition(ba_2026_07, requires_public_hearing, Source)
```

This keeps the amendment id and meaning-bearing requirement strict while
allowing either final-status or intermediate-condition rule surfaces.

Full QA:

```text
SC-001 baseline:        20 exact / 8 partial / 12 miss
SC-006 threshold union: 20 exact / 7 partial / 13 miss
perfect selector upper: 23 exact / 7 partial / 10 miss
direct selector:        21 exact / 7 partial / 12 miss
structural selector:    21 exact / 5 partial / 14 miss
```

### Lesson

Any-of probe groups fix the brittle-probe problem identified in SC-005 without
weakening the rule itself. Probes can now be strict about source-local actors,
objects, statuses, and safety-relevant outcomes while allowing controlled
surface variation in provenance/category slots or intermediate-vs-final derived
predicates.

The full-QA result is deliberately modest. The threshold rule union rescues
some rows and regresses others; the non-oracle selector recovers one exact over
both individual modes. A deterministic structural selector ties direct selector
on exact count but increases hard misses, so it is a cheap diagnostic baseline
rather than a replacement policy. This reinforces the broader rule doctrine:

```text
promotion-ready rule surface != globally dominant evidence mode
```


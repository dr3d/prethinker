# Guardrail Dependency A/B

Last updated: 2026-04-26

This is the first runtime A/B harness for the question:

```text
Can semantic_ir_v1 reduce Python-side semantic rescue without increasing bad commits?
```

The harness lives at:

```text
scripts/run_guardrail_dependency_ab.py
```

Raw run files stay local under:

```text
tmp/guardrail_dependency_ab/
```

## Method

Each scenario is run through two fresh runtime servers:

- legacy: `qwen35-semparse:9b` plus the current parser and Python rescue chain
- semantic IR: `qwen3.6:35b` plus the `semantic_ir_v1` mapper

The runner records:

- status and inferred decision
- committed clauses and final KB state
- mapper `admission_diagnostics_v1` counts when semantic IR is enabled
- prethink rescue hooks
- parse rescue hooks
- non-mapper parse rescue count
- must/avoid checks
- score delta

For live runtime fairness, the runner preloads Prolog-looking context facts and
injects each scenario's allowed predicate signatures into the runtime registry.
The rule/mutation pass also extracts embedded context clauses such as
`Existing fact: lives_in(mara, denver).` and `Existing rule: ...` so stored-logic
conflict tests exercise actual runtime state, not only prompt text.
This is still a research probe, not an external benchmark.

## Full Edge Result

Run:

```text
python scripts/run_guardrail_dependency_ab.py --scenario-group edge --timeout 300
```

Result:

| Runs | Legacy decision OK | Semantic decision OK | Legacy avg score | Semantic avg score | Legacy parse rescues | Semantic non-mapper rescues | Rescue reduction |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 | 10 | 13 | 0.743 | 0.854 | 7 | 0 | 7 |

The semantic IR path improved decision fit and rough scenario score while
removing all non-mapper parse-side rescue hooks on this battery.

## Strong Wins

The semantic path produced cleaner final KB state for several cases where legacy
either clarified unnecessarily or committed unsafe facts:

- counterfactual inheritance: legacy committed `codicil_signed(mara)`; semantic
  kept the actual original-will state
- Oslo/Oskar identity repair: semantic retracted old owner and asserted Oskar
- allegation versus finding: legacy committed forged/paid; semantic committed
  allegation plus authentic receipt without `paid(pavel)`
- temporal interval chair: semantic used scoped predicates instead of ad hoc
  `chaired(none, board, march)`
- comparative potassium: semantic committed `lab_result_high(mara, potassium)`
  and avoided low/normal
- temporal correction: semantic replaced Tuesday with Wednesday morning

## Weak Spots

The A/B run also exposed clear next work:

- hypothetical queries still tend to become clarification turns
- quantified exception rules can be over-committed as ordinary facts
- medical negation remains conservative around allergy versus side effect
- denial events may become non-mutating because the mapper cannot yet represent
  nested event terms cleanly
- retraction entity normalization is not strong enough: `crate12` and
  `crate_12` can diverge, leaving stale state after a correction

## Read

This is a real signal in favor of continuing. The semantic IR route is not just a
shinier parser; it reduced dependency on the old parse rescue chain and avoided
several bad legacy commits. The next deletion candidates should be measured
against this harness, not removed by instinct.

## Weak-Edge Fix Pass

Run:

```text
python scripts/run_guardrail_dependency_ab.py --scenario-group weak_edges --timeout 300
```

Result:

| Runs | Legacy decision OK | Semantic decision OK | Legacy avg score | Semantic avg score | Legacy parse rescues | Semantic non-mapper rescues | Rescue reduction |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 3 | 7 | 0.650 | 0.900 | 5 | 0 | 5 |

The weak-edge pass targeted the exact issues found above: hypothetical queries,
quantified class writes, medical allergy retractions, denial events, and entity
normalization for retractions.

Fixed or improved:

- pure hypothetical `if/had/would` questions now route as query turns without
  committing hypothetical facts
- explicit allergy corrections can safely retract stale allergy facts while
  holding side-effect/intolerance assertions if the model marks them uncertain
- denial predicates such as `denied/3` survive as speech/event facts instead of
  being skipped as signed negative facts
- numbered-entity retracts now try aliases like `crate_12` and `crate12`
- alias retract no-results no longer poison the turn when a later alias succeeds
- quantified set atoms such as `submitted_form(residents)` are skipped unless
  the IR expands them into individual known members

Remaining weak spots:

- the runtime scorer still labels some safe partial commits as `commit` where
  the scenario expectation says `mixed`; this is mostly decision-label
  calibration, not bad final KB state
- rule admission for quantified exception language is still shallow; the mapper
  can preserve safe direct facts but does not yet synthesize a durable rule from
  a structured IR unless the rule clause is explicit

## LM Studio Structured Output Pass

Run:

```text
python scripts/run_guardrail_dependency_ab.py --backend lmstudio --base-url http://127.0.0.1:1234 --legacy-model qwen/qwen3.6-35b-a3b --semantic-model qwen/qwen3.6-35b-a3b --scenario-group edge --timeout 300
```

Representative result:

| Runs | Legacy decision OK | Semantic decision OK | Legacy avg score | Semantic avg score | Legacy parse rescues | Semantic non-mapper rescues | Rescue reduction |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 | 9 | 17 | 0.763 | 0.930 | 0 | 0 | 0 |

This run used the same 35B model on both paths:

- legacy path: old strict semantic-parser prompt through LM Studio
- semantic path: `semantic_ir_v1` with LM Studio JSON-schema structured output

The important result is not just the score lift. The semantic path used zero
English/story rescue hooks. All recorded semantic interventions were structural
mapper events.

The edge set still shows some variance even at temperature 0. Targeted reruns
after prompt/projection fixes reached the expected decision for previously
failing cases such as nested quote denial, hypothetical hazard-pay query,
medical allergy negation, and transfer effectiveness. Full-battery reruns can
still wobble around a few decision labels, which means reproducibility and
multi-pass adjudication are now first-class research questions.

Weak-edge run:

```text
python scripts/run_guardrail_dependency_ab.py --backend lmstudio --base-url http://127.0.0.1:1234 --legacy-model qwen/qwen3.6-35b-a3b --semantic-model qwen/qwen3.6-35b-a3b --scenario-group weak_edges --timeout 300
```

Result:

| Runs | Legacy decision OK | Semantic decision OK | Legacy avg score | Semantic avg score | Legacy parse rescues | Semantic non-mapper rescues | Rescue reduction |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 4 | 10 | 0.667 | 1.000 | 0 | 0 | 0 |

The weak-edge pass is the cleanest evidence so far that the semantic workspace
direction can reduce Python-side language rescue. It handled hypothetical
queries, quantified exceptions, medical allergy/intolerance corrections, denial
versus observation, and retract aliasing without invoking English-specific
rescue hooks.

New structural guardrails added during this pass:

- LM Studio JSON-schema structured output support for runtime semantic IR
- rescue taxonomy in the A/B harness
- collision-resistant run artifact names that include scenario group, model,
  process ID, and microseconds
- projected semantic decision scoring for `mixed` and hypothetical cases
- inferred query admission for pure hypothetical questions
- duplicate unsafe-implication cleanup when the same operation is admitted safe
- claim-plus-direct-observation projection to `mixed`

These are not phrase patches. They are mostly admission/projection rules around
the semantic workspace contract, which is the direction we want: less Python
interpreting English, more Python enforcing the boundary and cleaning
self-contradictory IR bookkeeping.

The mapper contract for those structural rules is documented in
`docs/SEMANTIC_IR_MAPPER_SPEC.md`.

## Rule/Mutation Conflict Pass

Run:

```text
python scripts/run_guardrail_dependency_ab.py --backend lmstudio --base-url http://127.0.0.1:1234 --legacy-model qwen/qwen3.5-9b --semantic-model qwen/qwen3.6-35b-a3b --scenario-group rule_mutation --timeout 300
```

Latest local evidence:

| Runs | Legacy decision OK | Semantic decision OK | Legacy avg score | Semantic avg score | Semantic non-mapper rescues |
|---:|---:|---:|---:|---:|---:|
| 10 | 6 | 10 | 0.758 | 0.917 | 0 |

What changed during this pass:

- `semantic_ir_v1` rule operations can carry an explicit executable `clause`;
- mixed fact+query turns now keep `logic_string` valid for the legacy
  `assert_fact` contract while still carrying query clauses for execution;
- the A/B harness preloads embedded context facts and rules into the runtime;
- runtime admission now blocks narrow stored-logic conflicts before mutation:
  likely-functional current-state overwrites and simple `may_*`/`cannot_*`
  modal contradictions against derivable KB state.

This is a useful marker for the "less fussy Python" goal. The new Python is not
semantic repair of English; it is a visible admission reason: the proposed write
collides with stored state.

## Admission Diagnostics

The A/B harness now carries mapper diagnostics into each JSONL record and
summary report. For each semantic IR parse, diagnostics show:

- how many candidate operations were proposed;
- how many were admitted or skipped;
- projected decision versus model decision;
- skip reasons and rationale codes;
- admitted clause previews grouped as facts, rules, queries, and retracts.

These diagnostics are deliberately non-authoritative. They help explain and
tune the mapper contract while preserving the invariant that only deterministic
mapper/runtime policy admits durable KB mutations.

## Diagnostics/Projection Pass

Runs:

```text
python scripts/run_guardrail_dependency_ab.py --backend lmstudio --base-url http://127.0.0.1:1234 --legacy-model qwen/qwen3.6-35b-a3b --semantic-model qwen/qwen3.6-35b-a3b --scenario-group edge --timeout 300
python scripts/run_guardrail_dependency_ab.py --backend lmstudio --base-url http://127.0.0.1:1234 --legacy-model qwen/qwen3.6-35b-a3b --semantic-model qwen/qwen3.6-35b-a3b --scenario-group weak_edges --timeout 300
```

Latest local evidence:

| Pack | Runs | Legacy decision OK | Semantic decision OK | Legacy avg score | Semantic avg score | Semantic operations | Semantic admitted | Semantic skipped |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Edge | 20 | 10 | 20 | 0.777 | 0.976 | 43 | 37 | 6 |
| Weak edges | 10 | 3 | 10 | 0.633 | 1.000 | 16 | 16 | 0 |

Local report files:

- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T130519Z.md`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T131751Z.md`

Structural fixes from this pass:

- bounded `semantic_ir_v1` structured-output arrays to reduce JSON runaway and
  repeated assertion loops;
- projected ambiguous-pronoun turns to clarification when the only safe write is
  a generic speech/container fact;
- ignored low-risk clarify-policy unsafe alternatives when a safe correction is
  otherwise complete;
- projected context-labeled writes plus unsafe implications to `mixed`, because
  context-sourced writes are skipped and should not leave the decision label as
  a clean commit;
- added mapper operation diagnostics to JSONL/Markdown A/B output.

## Silverton Probate Pack

The Silverton pack is a new held-out stress battery for claim/fact separation,
identity ambiguity, location grounding, medical-boundary claims, and conditional
probate logic.

Run:

```text
python scripts/run_guardrail_dependency_ab.py --backend lmstudio --base-url http://127.0.0.1:1234 --legacy-model qwen/qwen3.6-35b-a3b --semantic-model qwen/qwen3.6-35b-a3b --scenario-group silverton --timeout 300
```

Initial local result:

| Pack | Runs | Legacy decision OK | Semantic decision OK | Legacy avg score | Semantic avg score | Semantic operations | Semantic admitted | Semantic skipped |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Silverton | 10 | 6 | 2 | 0.783 | 0.725 | 13 | 7 | 6 |

Local report file:

- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T134749Z.md`

This pack is deliberately not part of the default edge pack yet. It exposes the
next frontier: the model still over-commits or over-clarifies when claims,
ambiguous initials, London Ontario versus London UK, and two-witness amendment
rules interact. That makes it useful as a future regression target once the
semantic workspace and mapper policy are tightened for probate-style reasoning.

## Silverton Incremental Consumption

The incremental Silverton script tests a different consumption pattern:

```text
story so far + admitted mapper clauses + new focused utterance
```

Run:

```text
python scripts/run_silverton_incremental_semantic_ir.py --backend lmstudio --base-url http://127.0.0.1:1234 --model qwen/qwen3.6-35b-a3b --num-ctx 16384 --timeout 300
```

Initial local result:

| Runs | Schema OK | Decision OK | Avg rough score | Avg latency ms | Max rough context tokens |
|---:|---:|---:|---:|---:|---:|
| 10 | 10 | 3 | 0.773 | 7173 | 600 |

Local report file:

- `tmp/silverton_incremental_semantic_ir/silverton_incremental_20260426T135629Z.md`

This confirms that `16K` context is not the limiting factor for this scenario.
The failure mode is semantic/policy calibration: the model sees enough story
context, but still tends to over-use `mixed` where the desired frontier policy
expects quarantine/reject/answer.

## Silverton Noisy Temporal Pack

The noisy Silverton pack adds the kind of stressors that broke earlier
English-patching designs: typos, shorthand, mixed French/Spanish fragments,
relative dates, disputed initials, messy pronouns, correction language, and a
medical-sounding witness-discredit claim.

Run:

```text
python scripts/run_guardrail_dependency_ab.py --backend lmstudio --base-url http://127.0.0.1:1234 --legacy-model qwen/qwen3.5-9b --semantic-model qwen/qwen3.6-35b-a3b --scenario-group silverton_noisy --timeout 300
```

Latest local result:

| Pack | Runs | Legacy exact OK | Semantic exact OK | Legacy safe OK | Semantic safe OK | Legacy avg score | Semantic avg score |
|---|---:|---:|---:|---:|---:|---:|---:|
| Silverton noisy temporal | 8 | 3 | 8 | 6 | 8 | 0.750 | 0.969 |

Score dimensions:

| Path | Extraction avg | KB safety avg | Operations | Admitted | Skipped |
|---|---:|---:|---:|---:|---:|
| Legacy | 0.875 | 1.000 | 0 | 0 | 0 |
| Semantic IR | 0.906 | 1.000 | 7 | 4 | 3 |

Local report file:

- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T222011574370Z_silverton-noisy_qwen-qwen3-6-35b-a3b_pid35200.md`

Interpretation:

- The model usually preserves the important semantic content even through noise:
  `Londn ONT` versus London UK, LHR/Heathrow dates, `solo nosotros dos`, Silas's
  ambiguous `im`, and the allergy/side-effect boundary all surfaced in the IR.
- The new scoring split confirms that the weak point was administrative decision
  projection, not unsafe KB mutation. Exact labels are now `8/8`, safe outcomes
  are `8/8`, and final KB safety is `1.000`.
- The improvement came from structural policy, not prompt tuning: query-scoped
  identity premises no longer become facts, initial-only person aliases project
  state corrections to `mixed`, and claim-only wrappers with unsafe substantive
  implications project to `quarantine`.
- Predicate-palette enforcement moved the invalid verbal-amendment case from
  `mixed` to `quarantine` by skipping the model-invented out-of-palette
  `excluded/2` operation.
- The final Silas witness miss was repaired by a structural projection for
  speculative ambiguous observations: high-risk, unresolved referents,
  question-like/low-certainty assertions, unsafe implications, and no safe
  admissible operation now project to `quarantine`.
- This is still a pressure-pack result. It does not imply broad temporal proof
  or general legal reasoning.
- Temporal extraction is present but not yet temporal reasoning. The IR can hold
  2018-2024, April 2023 corrections, and relative-date anchors, but the runtime
  still needs a factual temporal representation before durable mutations can
  support serious interval queries.
- A structural projection bug was fixed during this pass: ambiguous referents are
  no longer upgraded into pure hypothetical `answer` turns just because an
  explanatory note contains if-language.

This pack should stay intentionally hard. It is useful less as a pass/fail demo
and more as a pressure gauge for whether future work reduces domain-specific
Python while keeping the authority boundary intact.

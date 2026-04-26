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
- prethink rescue hooks
- parse rescue hooks
- non-mapper parse rescue count
- must/avoid checks
- score delta

For live runtime fairness, the runner preloads Prolog-looking context facts and
injects each scenario's allowed predicate signatures into the runtime registry.
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
- projected semantic decision scoring for `mixed` and hypothetical cases
- inferred query admission for pure hypothetical questions
- duplicate unsafe-implication cleanup when the same operation is admitted safe
- claim-plus-direct-observation projection to `mixed`

These are not phrase patches. They are mostly admission/projection rules around
the semantic workspace contract, which is the direction we want: less Python
interpreting English, more Python enforcing the boundary and cleaning
self-contradictory IR bookkeeping.

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

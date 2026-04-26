# Semantic IR Edge Exploration

Last updated: 2026-04-26

This note records the first hard edge exploration for the stronger
`qwen3.6:35b` semantic workspace path. The goal was not broad chatbot behavior;
it was to ask how close the model can get to compiling difficult language into
safe Prolog-shaped candidate operations.

## Battery

The edge battery in `scripts/run_semantic_ir_prompt_bakeoff.py` now includes 20
stress cases:

- nested `unless` / exception rules
- counterfactual inheritance
- quantifiers with named exceptions
- stacked pronoun ambiguity
- identity correction and alias repair
- mixed rule/query pressure
- allegation versus court finding
- temporal interval state
- missing versus dead versus legally separated
- disjunctive causality
- `only after` effective-date scope
- comparative clinical measurements
- allergy negation and side-effect correction
- nested quote and denial
- mutual exclusion repair
- chain-of-custody gap
- temporal correction
- denial-is-not-negation
- double negation
- pure hypothetical query

A separate `rule_mutation` pack keeps two newer edges visible:

- rule recognition from natural language: direct Horn rules, recursive rules,
  exception rules, and context-rule queries that should not become writes;
- mutation conflict detection: new utterances that may overwrite existing
  current facts, explicit corrections that should retract/assert, safe
  non-exclusive additions, and claims that contradict observed KB state without
  erasing it.

Initial `qwen/qwen3.6-35b-a3b` LM Studio result:

| Pack | Runs | JSON OK | Schema OK | Decision OK | Avg rough score |
|---|---:|---:|---:|---:|---:|
| rule + mutation conflict | 10 | 10/10 | 10/10 | 7/10 | 0.89 |
| rule + mutation conflict after rule-clause schema | 10 | 10/10 | 10/10 | 9/10 | 0.96 |
| rule + mutation conflict after stored-logic guard | 10 | 10/10 | 10/10 | 9/10 | 0.95 |

Strong cases: direct Horn rule recognition, recursive ancestor-rule shape, pure
context-rule query without writing the context rule, explicit retract/assert
correction, and safe non-exclusive medical condition addition.

Weak cases: exception rules with `unless`, unmarked current-state replacement
such as `lives_in(mara, salem)` over an existing current location, and
rule-derived conflicts such as asserting `cannot_ship(crate12)` when existing
facts plus rules imply `may_ship(crate12)`.

The schema change matters: `operation="rule"` now has an optional executable
`clause` field. Before that, LM Studio structured output could recognize a rule
but could not legally provide the rule body that the mapper requires. After the
change, the 35B model emitted executable clauses such as:

```prolog
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z).
```

Runtime A/B on the same pack:

| Runs | Legacy decision OK | Semantic decision OK | Legacy avg score | Semantic avg score | Semantic non-mapper rescues |
|---:|---:|---:|---:|---:|---:|
| 10 | 6/10 | 9/10 | 0.808 | 0.883 | 0 |
| 10 | 6/10 | 10/10 | 0.758 | 0.917 | 0 |

The newest pass added a narrow deterministic stored-logic guard. It catches two
classes before mutation:

- likely-functional current-state overwrites, such as `lives_in(mara, salem)`
  when `lives_in(mara, denver)` is already stored and no retract/correction is
  present;
- modal predicate contradictions where an asserted `cannot_*`/`cant_*` fact
  contradicts a derivable `may_*`/`can_*` consequence, or vice versa.

This is intentionally not a general contradiction prover. The important research
movement is that the guard is structural and KB-state-based, not another English
phrase rescue. It also exposed a useful adapter bug: mixed fact+query turns must
keep `logic_string` valid for the legacy `assert_fact` contract while still
carrying query clauses for execution.

## Results

Run:

```text
python scripts/run_semantic_ir_prompt_bakeoff.py \
  --model qwen3.6:35b \
  --variants best_guarded_v2,best_guarded_v3 \
  --scenario-group edge \
  --timeout 300
```

Summary:

| Variant | Runs | JSON OK | Schema OK | Decision OK | Avg rough score | Avg latency |
|---|---:|---:|---:|---:|---:|---:|
| `best_guarded_v2` | 20 | 20/20 | 20/20 | 17/20 | 0.96 | 7.8s |
| `best_guarded_v3` | 20 | 20/20 | 20/20 | 15/20 | 0.92 | 7.6s |

`best_guarded_v2` remains the best overall decision prompt. A sharper
operation-policy prompt improved some retraction polarity behavior, but it made
decision labels worse by overusing `mixed` or `clarify`.

## LM Studio AFK Recheck

After switching the live research loop to LM Studio structured output, a
35B-only recheck was run with `qwen/qwen3.6-35b-a3b`, temperature `0.0`,
top-p `0.82`, top-k `20`, context `16384`, and thinking off.

| Pack | Schema contract in prompt | JSON OK | Schema OK | Decision OK | Avg rough score |
|---|---:|---:|---:|---:|---:|
| hard edge | no | 20/20 | 20/20 | 15/20 | 0.91 |
| hard edge | yes | 20/20 | 20/20 | 15/20 | 0.92 |
| weak edges | no | 10/10 | 10/10 | 4/10 | 0.82 |
| weak edges | yes | 10/10 | 10/10 | 7/10 | 0.89 |
| Silverton noisy | no | 8/8 | 8/8 | 2/8 | 0.75 |
| Silverton noisy | yes | 8/8 | 8/8 | 4/8 | 0.82 |

The main finding is that LM Studio structured output reliably handles JSON
shape, but the compact schema/policy contract still helps decision calibration.
So the runtime now keeps the compact root-shape contract in the semantic IR
prompt even when LM Studio is enforcing `json_schema`.

The Silverton noisy pack remains deliberately adversarial. It is less a polished
demo and more a pressure gauge for identity ambiguity, temporal correction,
policy labels, and claim/fact separation. The schema contract improved it, but
the remaining misses are still policy-shaped: `reject` versus `quarantine`,
`clarify` versus `answer`, and `commit` versus `mixed` when a safe temporal
correction coexists with unsafe legal consequences.

## Strong Signals

The model is already strong at:

- preserving claims, denials, allegations, findings, and observations as
  separate provenance categories
- refusing to turn disjunctions into single causes
- preserving counterfactuals as non-writes
- catching ambiguous pronoun stacks
- keeping temporal intervals distinct from timeless facts
- treating double negation as positive existential state
- handling direct correction into retract/assert candidates

The strongest live runtime smoke was an identity repair:

```text
Oslo owns the lease.
I said Oslo owns the lease, but that was wrong: Oskar owns the lease; Oslo is the street.
```

With `semantic_ir_enabled=true`, the runtime committed:

```prolog
retract_fact owns(oslo, lease).
assert_fact owns(oskar, lease).
assert_fact at(oslo, street).
```

The parse-side trace contained only:

```text
semantic_ir_mapper
```

That is the desired shape: the LLM owns semantic interpretation; deterministic
code owns admission and execution.

## Weak Edges

The newest design is weakest at:

- hypothetical queries: the model often asks for clarification instead of
  treating the turn as a pure hypothetical query
- admin label policy: the model sometimes chooses `commit` when the structure
  contains safe claim/event writes plus unsafe legal implications that our
  external scorer expects as `mixed`
- correction decision labels: the model sometimes labels retract/assert
  corrections as `mixed` even when they are safe commits
- medical negation: explicit "not allergic; side effect instead" is still
  treated conservatively as quarantine/clarify under the medical safety policy
- durable negation: the IR can express negative meaning, but the runtime still
  needs a first-class representation for negative facts, closed-world absence,
  and negated observations
- rule clauses: the model understands rules and exceptions, but the mapper does
  not yet admit full default/exception rule semantics from prose
- stored-logic conflict detection: the runtime now catches a narrow structural
  subset, but not full first-order contradiction, temporal conflict, or profile
  declared exclusivity yet

## Mapper Adjustment

The edge run exposed a useful mapper issue. `best_guarded_v2` often emitted:

```json
{"operation": "retract", "polarity": "negative"}
```

for "remove the old positive fact." The mapper now trusts `operation="retract"`
as the action and reserves polarity blocking for negative `assert` operations.
This makes existing v2 outputs more executable without switching to the worse
v3 decision prompt.

## Research Read

This is productive territory. The failures are increasingly about IR schema,
admission policy, and mapper semantics, not about the model failing to read the
sentence. The next hard push should be:

- add a real `semantic_ir_v1` representation for rules, temporal intervals,
  claims, and durable negation
- build the guardrail-dependency A/B harness against old Python rescue hooks
- promote the best edge cases into regression tests for the live
  `semantic_ir_enabled` path
- evolve stored-logic conflict policy into profile-declared functional
  predicates, opposition pairs, and temporal/current-state scopes

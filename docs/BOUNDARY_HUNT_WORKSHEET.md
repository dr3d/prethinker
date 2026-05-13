# Boundary Hunt Worksheet

Last updated: 2026-05-13

This is the active CTO cockpit for boundary-hunt work. The full historical
worksheet was preserved verbatim at:

`C:\prethinker_tmp_archive\boundary_hunt_20260513\BOUNDARY_HUNT_WORKSHEET_FULL_20260513.md`

Use this file for current state, next pressure, and handoff clarity. Use the
archive copy only for named historical detail.

## Doctrine

Fixture names, question ids, row ids, answer strings, local people, local
organizations, and source-story vocabulary are artifact addresses only. They are
never architecture.

The loop is:

```text
measure -> classify coordinates -> group by fixture-free geometry
  -> predict a reusable repair -> replay on unlike rows -> journal trajectory
```

Do not rescue a row by teaching the harness local nouns. Repair only when the
failure shape remains meaningful after fixture vocabulary is removed.

## Current Phase

Guard compression is archived. Boundary hunt is active.

The hunt target is no longer "retire more guards." It is:

- expose where the current interior gets blurry on unlike source shapes;
- separate compile-surface gaps from helper/selector gaps;
- audit helper trigger conditions as carefully as helper bodies;
- extend the interior only with generic, replayable repairs.

## Seed Measurement

Wide OpenRouter corpus run:

```text
compiled fixtures: 32
questions: 1218
exact / partial / miss: 1008 / 76 / 134
exact rate: 0.8276
not-exact coordinates: 210
runtime load errors: 0
write proposal rows: 0
helper rows: 2877
rows per exact answer: 2.854
```

Main boundary split:

| Surface | Count | Read |
| --- | ---: | --- |
| `compile_surface_gap` | 131 | Largest class. Often resolution/envelope blur rather than absent extraction. |
| `hybrid_join_gap` | 42 | Facts exist in pieces; answer needs reusable join/arithmetic/set logic. |
| `query_surface_gap` | 27 | Compile likely has support; planner misses or overbinds surface. |
| `answer_surface_gap` | 7 | Support reached but answer form/rendering weak. |
| `judge_uncertain` | 3 | Measurement ambiguity; do not repair without audit. |

Important finding:

Only a small part of the wide compile boundary looked like a truly missing
axis. Most misses were resolution blur: wrong authority envelope, wrong
temporal envelope, wrong epistemic envelope, wrong granularity, opaque residue,
or predicate-shape drift.

## Completed Moves

The full entries are archived in the full worksheet copy. Current rollup:

| Entry Range | Result | Status |
| --- | --- | --- |
| BH-006 to BH-011 | Split compile-surface and hybrid-join classes; simple authority and deadline probes passed. | Interior wider than expected; boundary is density/resolution. |
| BH-012 to BH-015 | Status timeline ladder, resolver repair, unlike replay, density split. | First live-set extension; remaining density classified. |
| BH-016 to BH-020 | Status-count aggregation and alias-count work. | Several coordinates moved inside; evidence split created. |
| BH-021 to BH-022 | Explicit source-count source-fidelity repair and transfer replay. | Generic numeric source lines improved; wide target moved exact. |
| BH-023 to BH-024 | Scoped semantic filter repair and unlike replay. | Predicate-scoped and source-section-scoped forms transfer; helper delivery still noisy. |
| BH-025 | Trigger sanity stage 1. | Sectionless scoped counts passed; state-word and non-English source-fidelity risks surfaced. |
| BH-026 | Trigger sanity stage 2. | Canonical alias probe passed; numeric prose source-fidelity repair moved `14/0/2` to `15/0/1`. |
| BH-027 | Counterfactual arithmetic stated-outcome probes. | Simple and dense stated-outcome variants passed `20/0/0`; boundary is not basic counterfactual retrieval. |
| BH-028 | Counterfactual arithmetic unstated-result probe and generic compile repair. | Unstated add/subtract variant exposed `7/0/1`; source-pass contract guidance moved replay to `8/0/0`. |

## Current Evidence

Counterfactual arithmetic after the source-pass contract repair:

```text
questions: 28
exact / partial / miss: 28 / 0 / 0
exact rate: 1.0000
helper rows: 0
runtime load errors: 0
write proposal rows: 0
```

Per fixture:

| Probe | Exact | Partial | Miss | Read |
| --- | ---: | ---: | ---: | --- |
| `counterfactual_arithmetic_pair` | 8 | 0 | 0 | Basic unlike pair passed when the hypothetical outcome was stated. |
| `counterfactual_arithmetic_dense_pair` | 12 | 0 | 0 | Multiple adjustments and disposition decoys passed when the hypothetical outcome was stated. |
| `counterfactual_arithmetic_unstated_pair` | 8 | 0 | 0 | Unstated add/subtract outcome passed after generic source-pass contract guidance. |

Generic repair already made:

- `scripts/run_domain_bootstrap_file.py` now reminds focused source-pass
  compiles that predicate contract arity is strict.
- The guidance requires arithmetic/counterfactual language to preserve grounded
  component rows first: base count or amount, operation type, delta value,
  target entity, calculation view, and view basis when those predicates exist.
- It prefers component facts over invented final-result facts when the source
  gives an arithmetic instruction but does not print the final result.
- No helper was added, and no fixture ids, row ids, source nouns, or answer
  strings entered the harness.

Verification:

```text
OpenRouter compile/QA:
counterfactual_arithmetic_pair: 8 / 0 / 0
counterfactual_arithmetic_dense_pair: 12 / 0 / 0
counterfactual_arithmetic_unstated_pair before repair: 7 / 0 / 1
counterfactual_arithmetic_unstated_pair after repair: 8 / 0 / 0
```

## Recent Journal

### BH-027 - Counterfactual Arithmetic Stated Outcomes

Before:

- Active board priority 1 was `counterfactual_arithmetic_join`.
- Wide not-exact evidence suggested current totals plus excluded/proposed
  additions were present but not assembled into hypothetical results.

Prediction:

- If a focused unlike pair with stated hypothetical outcomes failed, the
  geometry would justify a generic arithmetic/join repair.
- If it passed, the wide misses were denser than basic stated-outcome retrieval.

Intervention:

- Added `experiments/boundary_probes/hybrid_join_stage2/counterfactual_arithmetic_pair`.
- Added `experiments/boundary_probes/hybrid_join_stage2/counterfactual_arithmetic_dense_pair`.
- Ran OpenRouter compile/QA through the existing governed harness.

After:

- Simple pair: `8/0/0`, helper rows `0`.
- Dense pair: `12/0/0`, helper rows `0`.
- The dense compile emitted explicit hypothetical outcome surfaces and kept
  adopted, excluded, withdrawn, superseded, and rejected dispositions separate.

Artifacts:

- `tmp\boundary_probe_hybrid_compile_stage8_20260513`
- `tmp\boundary_probe_hybrid_qa_stage16_20260513`
- `tmp\boundary_probe_hybrid_compile_stage9_20260513`
- `tmp\boundary_probe_hybrid_qa_stage19_20260513`

Verification:

- No runtime load errors.
- No write proposals.
- No helper delivery needed.

Lesson:

- Counterfactual arithmetic is inside the set when the source prints the
  hypothetical outcome or makes it easy for the compiler to emit that outcome.
  The boundary is not the word "counterfactual"; it is whether the answer
  requires preserving and assembling component surfaces without a printed final
  result.

Next pressure:

- Remove the printed final outcome and force component preservation before any
  helper or arithmetic rule is considered.

### BH-028 - Unstated Result Contract Repair

Before:

- The unstated add/subtract pair compiled with `8` admitted facts and `8`
  skipped operations.
- QA was `7/0/1`; the miss was the subtractive hypothetical result.
- Compile warnings showed wrong-arity and unresolved-placeholder operations:
  `active_count/1`, `proposed_change/3`, `view_delta/9`, and
  `hypothetical_result/10`.

Prediction:

- A fixture-free repair should improve component admission, not teach the
  harness any local identifier or source phrase.
- If component facts survived with correct arity, the existing planner/judge
  path could answer without a new helper.

Intervention:

- Updated focused source-pass guidance in `scripts/run_domain_bootstrap_file.py`.
- Added strict contract-arity guidance.
- Added arithmetic component guidance: preserve base count or amount, operation
  type, delta value, target entity, calculation view, and view basis.
- Added a caution against inventing final-result facts when the source gives
  an arithmetic instruction but does not print the final value.

After:

- Replay compile admitted `12` facts and skipped `0`.
- Replay QA was `8/0/0`, helper rows `0`.
- The compile emitted generic component predicates such as `current_count/3`,
  `proposed_change/5`, `hypothetical_calculation_defined/3`, and
  `view_not_printed/1`.

Artifacts:

- Before repair:
  `tmp\boundary_probe_hybrid_compile_stage10_20260513`,
  `tmp\boundary_probe_hybrid_qa_stage20_20260513`
- After repair:
  `tmp\boundary_probe_hybrid_compile_stage11_20260513`,
  `tmp\boundary_probe_hybrid_qa_stage21_20260513`

Verification:

- OpenRouter compile/QA after repair: `8/0/0`.
- No helper rows.
- No runtime load errors.
- No write proposals.

Lesson:

- The first real counterfactual-arithmetic gap was not an arithmetic helper
  absence. It was a compile-resolution issue: the model proposed the right
  predicate families but violated their arity or filled arguments with
  unresolved calculation prose. Contract obedience is a boundary-control
  surface.

Next pressure:

- Replay against the wide not-exact arithmetic coordinates if they are
  available. If replay holds, move this class from active pressure to extended
  interior. If wide rows still miss, classify whether they require multi-step
  arithmetic, unit conversion, policy gating, or query-planner changes.

## Active Pressure Board

| Priority | Boundary | Current Shape | Next Move |
| ---: | --- | --- | --- |
| 1 | `counterfactual_arithmetic_join` wide replay | Focused probes now pass, including unstated add/subtract after generic compile guidance. | Replay or sample the original not-exact arithmetic coordinates; classify any survivors by density. |
| 2 | `scoped_status_count_support` delivery volume | Transfer succeeded but helper rows were high in unlike replay. | Compress delivery scope without weakening source-fidelity. |
| 3 | trigger audit | Helper bodies may be generic while triggers remain corpus-shaped. | Continue fresh probes for trigger conditions, especially predicate-name and source-form assumptions. |
| 4 | domain transfer | Current evidence is still mostly from the lab corpus plus synthetic probes. | Add small unlike-domain fixtures only when they isolate a named pressure. |

## Next Work

Do this next:

1. Replay or sample the original wide not-exact rows tagged as
   `counterfactual_arithmetic_join`.
2. Check whether the source-pass contract repair changes their compile
   admission before looking at QA.
3. Classify survivors:
   - multi-step arithmetic;
   - unit conversion;
   - policy/status gating;
   - planner under-retrieval over clean component rows;
   - judge-only ambiguity.
4. Only add a helper if clean component rows exist and repeated unlike misses
   still require query-time assembly.
5. Then return to `scoped_status_count_support` delivery volume.

## OpenRouter Rule

Default hosted pressure to 6 lanes or fewer. Wider runs produced provider 429s
and lower practical throughput.

## Stop Conditions

Stop a hunt lane when remaining coordinates are:

- transport/provider failures;
- judge-only ambiguity;
- source-fidelity singletons best left as exact source fallback;
- fixture-language leaks that should remain in history;
- low-count residue with no repeated geometry across unlike artifacts.

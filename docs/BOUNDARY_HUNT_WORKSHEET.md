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
| BH-029 | Wide counterfactual increment replay. | Original wide miss `census_reconciliation` q040 replayed exact after recompile; adjacent revenue projection q028 also exact. |
| BH-030 | Scoped-status delivery compression attempt. | Focused helper rows dropped `45 -> 36`, but unlike replay shifted exactness `36/1/3 -> 34/5/1`; code change rejected. |
| BH-031 | Scoped-count precedence repair. | q032 moved partial -> exact by treating clean scoped-count rows as answer-bearing over broader status context. |

## Current Evidence

Counterfactual arithmetic after the source-pass contract repair:

```text
focused synthetic questions: 28
focused exact / partial / miss: 28 / 0 / 0
wide replay sample: 2
wide replay exact / partial / miss: 2 / 0 / 0
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
| `census_reconciliation` q040 | 1 | 0 | 0 | Original wide `counterfactual_increment_count` miss replayed exact after recompile. |
| `census_reconciliation` q028 | 1 | 0 | 0 | Adjacent projection question replayed exact; treated as confidence, not the main coordinate. |

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

### BH-029 - Wide Counterfactual Increment Replay

Before:

- The boundary plan had one direct `counterfactual_increment_count` coordinate:
  `census_reconciliation` q040.
- In the original wide run, q040 was `miss` with `hybrid_join_gap`.
- The old query plan retrieved only current total rows and failed rejected
  `memberchk` evidence-bundle queries for the projected count.

Prediction:

- If BH-028's compile-contract repair transferred, a fresh compile would
  preserve enough source-fidelity or component surface for q040 to become exact
  without a fixture-specific helper.
- If it still missed, the survivor would likely be query-planner under-retrieval
  over clean source-record rows.

Intervention:

- Recompiled `datasets/story_worlds/census_reconciliation` with the repaired
  source-pass guidance.
- Ran q040 only through OpenRouter QA with evidence bundles and reference judge.
- Also sampled q028, an adjacent projection/revenue question, as a sanity check.

After:

- q040 replayed `1/0/0`.
- q028 replayed `1/0/0`.
- Helper rows remained `0`.
- The recompiled surface still did not need a dedicated projected-total helper:
  q040 reached the source-record line containing the projected unit count and
  paired it with current status/current count support.

Artifacts:

- `tmp\boundary_wide_replay_compile_census_contract_20260513`
- `tmp\boundary_wide_replay_qa_census_contract_q040_20260513`
- `tmp\boundary_wide_replay_qa_census_contract_q028_20260513`

Verification:

- q040 reference judge: exact.
- q028 reference judge: exact.
- No runtime load errors.
- No write proposals.
- No helper delivery.

Lesson:

- The first original wide counterfactual increment miss moved inside after the
  same generic contract/component repair that fixed the synthetic unstated
  probe. That supports the "compile-resolution, not arithmetic-helper absence"
  diagnosis for this slice.

Next pressure:

- Mark `counterfactual_arithmetic_join` as extended interior unless more
  original wide coordinates with unlike arithmetic survive.
- Move next to `scoped_status_count_support` delivery volume or to a fresh
  trigger-audit probe if delivery work risks overfitting.

### BH-030 - Scoped-Status Delivery Attempt Rejected

Before:

- Active pressure was `scoped_status_count_support` delivery volume.
- Focused scoped-semantic probe was exact but carried `45` helper rows.
- Unlike replay carried `72` helper rows with baseline `36/1/3`.

Prediction:

- Plain scope queries were carrying semantic criterion rows even when the query
  only asked for scope membership.
- Gating criterion rows behind a status-term or concrete-status request should
  reduce helper delivery without affecting source-fidelity rows.

Intervention:

- Locally changed `scoped_status_criterion_count` delivery so term-derived
  rows required a term/status request.
- Added a local regression test for the proposed contract.
- Replayed focused scoped-semantic probe and unlike contradictory-evidence
  transfer.

After:

- Focused probe stayed `8/0/0`; helper rows dropped `45 -> 36`.
- Unlike replay helper rows dropped `72 -> 27`.
- Unlike replay answer shape shifted from `36/1/3` to `34/5/1`.
- Targeted retry of q028/q032 remained partial.
- The code change was rejected and backed out.

Artifacts:

- Focused attempt:
  `tmp\boundary_probe_hybrid_qa_stage22_scoped_delivery_20260513`
- Unlike attempt:
  `tmp\boundary_scoped_filter_replay3_qa_20260513`
- Targeted retry:
  `tmp\boundary_scoped_filter_retry_q028_q032_20260513`

Verification:

- Local test suite after backing out helper change: `129 passed`.
- No runtime load errors.
- No write proposals.

Lesson:

- Delivery compression cannot be judged on helper-row count alone. A smaller
  helper surface that coincides with weaker unlike replay is not an architectural
  win, even when the suspected row loss is partly planner or judge variance.
  The next compression attempt should target query/planner scoping or answer
  precedence over clean scoped-count rows, not suppress helper rows upstream.

Next pressure:

- Keep scoped-status delivery pressure open.
- Do not reapply the criterion-row gate without an answer-stability repair.
- Investigate planner behavior for count questions where a clean
  `scoped_status_count_support` row is exact but broad primary status rows
  create answer noise.

### BH-031 - Scoped-Count Answer Precedence

Before:

- BH-030 showed that suppressing helper rows upstream was too risky.
- The unlike q032 retry still produced the exact clean scoped-count helper row,
  but the judge marked the answer partial because a broader global status query
  returned five rows while the scoped helper returned the requested three.

Prediction:

- The right repair is answer/query precedence, not helper suppression.
- For a count question scoped to a section, subset, criterion, or identified
  item group, a clean helper row that binds scope, criterion, count, and members
  should be answer-bearing. Broader unscoped status rows should remain context.

Intervention:

- Added fixture-free QA guidance in `scripts/run_domain_bootstrap_qa.py`:
  section/subset-scoped status-count questions should pair status rows with a
  scope surface so `scoped_status_count_support` can return the asked subset.
- Added judge policy that clean scoped-count helper rows are answer-bearing
  when they bind the requested scope, semantic criterion, count, and members.
- Kept the BH-030 helper-row suppression backed out.

After:

- Targeted q032 replay moved `partial -> exact`.
- Helper rows stayed bounded at `1` clean `scoped_status_count_support` row.
- The broader global status query still returned five rows, but no longer
  overrode the scoped count when the scoped helper directly matched the
  reference.
- Focused scoped-ladder replay held at `8/0/0` with `44` clean helper rows.
- Full unlike replay held the repaired scoped-count coordinate exact and
  returned `36/3/1`; the remaining non-exacts are separate surfaces:
  one temporal arithmetic join and three compile-surface gaps.

Artifacts:

- Failed judge-policy-only attempt:
  `tmp\boundary_scoped_count_judge_policy_q032_20260513`
- Successful planner/judge precedence attempt:
  `tmp\boundary_scoped_count_planner_policy_q032_20260513`
- Focused scoped-ladder acceptance:
  `tmp\boundary_probe_hybrid_qa_stage23_scoped_precedence_20260513`
- Full unlike acceptance:
  `tmp\boundary_scoped_count_full_replay_contradictory_20260513`

Verification:

- q032 targeted OpenRouter replay: `1/0/0`.
- Focused scoped-ladder OpenRouter replay: `8/0/0`.
- Full unlike OpenRouter replay: `36/3/1`; q032 exact.
- `python -m pytest tests\test_domain_bootstrap_qa.py -q`: `129 passed`.
- `python -m py_compile scripts\run_domain_bootstrap_qa.py`: passed.
- No runtime load errors.
- No write proposals.

Lesson:

- Scoped-count delivery pressure was not primarily "too many helper rows." It
  was a precedence problem: exact scoped helper rows can be present but weakened
  by broader context rows unless the answer policy knows the scoped row is the
  more specific answer surface.

Next pressure:

- Keep this as a precedence repair and leave helper-row suppression alone.
- Move the next boundary hunt to the remaining non-exacts from the full unlike
  replay: temporal arithmetic over corrected intervals, and missing emitted
  surfaces for source content, sector coverage, and timestamp-gap records.

## Active Pressure Board

| Priority | Boundary | Current Shape | Next Move |
| ---: | --- | --- | --- |
| 1 | `scoped_status_count_support` delivery volume | Transfer succeeded but helper rows were high in unlike replay. | Compress delivery scope without weakening source-fidelity. |
| 2 | trigger audit | Helper bodies may be generic while triggers remain corpus-shaped. | Continue fresh probes for trigger conditions, especially predicate-name and source-form assumptions. |
| 3 | domain transfer | Current evidence is still mostly from the lab corpus plus synthetic probes. | Add small unlike-domain fixtures only when they isolate a named pressure. |
| 4 | `counterfactual_arithmetic_join` watch | Focused probes and original wide q040 now pass after generic compile guidance. | Reopen only if another original wide coordinate shows unlike arithmetic density. |

## Next Work

Do this next:

1. Return to `scoped_status_count_support` delivery volume.
2. Compare the broad helper rows against the exact question focus:
   - predicate-scoped rows;
   - source-section rows;
   - context-tail rows;
   - irrelevant clean-helper rows.
3. Compress delivery scope only if the rule is fixture-free and keeps the
   source-fidelity rows needed by the transfer probes.
4. If scoped-status compression starts to smell local, pause and do a fresh
   trigger-audit probe instead.

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

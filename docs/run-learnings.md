# Run Learnings

Append-only log of ladder cycle outcomes and what changed.
Auto-populated by `scripts/run_ladder.py` via `--learn-log`.

## 2026-04-11T13:42:06+00:00
- Run: `differential_validation_baseline`
- Runtime: vendored `engine/core.py` vs baseline `../prolog-reasoning/src/engine/core.py`
- Source: `docs/data/differential_validation_latest.json`
- Learned:
  - Differential agreement is `10/10` cases (`100%`).
  - Category agreement rates are `100%` for `unification`, `recursion`, `negation`, `backtracking`, `findall`, and `retraction_behavior`.
  - This provides a stronger vendoring check than ported tests alone by comparing full step traces between engines.

## 2026-04-11T13:30:00+00:00
- Run: `baseline_research_note` | range `acid_06 -> acid_11` | selected `6` | executed `6` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Learned:
  - Multi-clause utterances are a major ambiguity source: the model often understands all clauses semantically but serializes them as one blob string unless we explicitly enforce clause-level unpacking.
  - Retractions are linguistically under-specified in natural speech ("undo that", "retract those"), so deterministic ingestion requires explicit target normalization and often multiple target extraction.
  - Predicate drift remains a live risk under paraphrase pressure ("father_of" vs "father"), so canonical predicate alignment is not optional for stable KB state.
  - Clarification should trigger on missing arguments and unresolved referents, not on already-deterministic parses; otherwise we add friction without improving correctness.
  - Long-context lineage works better when each turn remains compositional and local; failures usually come from operation packing and correction semantics, not from core transitive inference.
  - Current frontier failure pattern is no longer basic parsing; it is mixed-turn consistency (fact + rule + retract bundles) and recovery behavior after correction.

## 2026-04-11T12:54:22+00:00 (backfilled)
- Run: `hardcycle_20260411_084947` | range `acid_06_compound_unpacking -> acid_08_contradiction_reconciliation` | selected `3` | executed `3` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `e0a66d9a2fbe`
- Source: `tmp/runs/ladder_summary_20260411_124947.json`
- Learned:
  - New hard rungs (`acid_06`..`acid_08`) were stable in one sweep (9/9 validations).
  - Compound fact unpacking and relation drift pressure are now testable as first-class ladder steps.
  - Contradiction reconciliation remained stable under the same prompt/config signature.

## 2026-04-11T13:01:19+00:00 (backfilled)
- Run: `hardcycle2_20260411_085612` | range `acid_06_compound_unpacking -> acid_09_compound_rule_unpacking` | selected `4` | executed `4` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `e0a66d9a2fbe`
- Source: `tmp/runs/ladder_summary_20260411_125612.json`
- Learned:
  - Extending the range to include `acid_09_compound_rule_unpacking` exposed a new frontier break (`return_code=1`).
  - The failure moved the bottleneck from basic hard-rung stability to compound rule ingestion/execution mechanics.
  - This confirmed the need for explicit batch rule handling in validation + apply paths.

## 2026-04-11T13:06:18+00:00 (backfilled)
- Run: `hardcycle3_20260411_090159` | range `acid_06_compound_unpacking -> acid_09_compound_rule_unpacking` | selected `4` | executed `4` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `e0a66d9a2fbe`
- Source: `tmp/runs/ladder_summary_20260411_130159.json`
- Learned:
  - After runtime updates for multi-rule handling, `acid_09` passed and the full hard cycle (`acid_06`..`acid_09`) went green.
  - The system now tolerates richer packed utterances without immediately collapsing at rule ingest.
  - Frontier then shifted again from rule unpacking to retraction/recovery mixes.

## 2026-04-11T13:12:46+00:00 (backfilled)
- Run: `acid_10_compound_retract_unpacking_probe4` | scenario `acid_10_compound_retract_unpacking` | validations `3/3`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Source: `tmp/runs/acid_10_compound_retract_unpacking_probe4.json`
- Learned:
  - Multi-target retract behavior succeeded under probe conditions.
  - Legacy-edge removals and lineage recovery checks all passed (`legacy_edge_1_removed`, `legacy_edge_2_removed`, `new_route_recovers_lineage`).
  - Prompt guidance plus runtime retract expansion materially improved correction-turn reliability.

## 2026-04-11T13:14:02+00:00 (backfilled)
- Run: `acid_11_batched_fact_rule_retract_mix_probe` | scenario `acid_11_batched_fact_rule_retract_mix` | validations `2/3`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Source: `tmp/runs/acid_11_batched_fact_rule_retract_mix_probe.json`
- Learned:
  - Mixed batched turns are the current frontier: removals passed, but lineage recovery failed.
  - Failing check: `yara_to_bex_recovers_via_arlo` (`expected success`, observed `no_results`).
  - Remaining gap is multi-step recovery consistency after combined fact/rule/retract operations in one scenario.
## 2026-04-11T14:49:22+00:00
- Run: `walkcycle1_20260411_1410` | range `acid_06_compound_unpacking -> acid_11_batched_fact_rule_retract_mix` | selected `6` | executed `6` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Actions: executed=6
- Learned:
  - `acid_06_compound_unpacking`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_07_relation_drift_pressure`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_08_contradiction_reconciliation`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_09_compound_rule_unpacking`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_10_compound_retract_unpacking`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_11_batched_fact_rule_retract_mix`: subprocess failed (return code 1).
## 2026-04-11T14:53:03+00:00
- Run: `walkcycle2_20260411_1418` | range `acid_11_batched_fact_rule_retract_mix -> acid_13_branch_preservation_after_repair` | selected `3` | executed `3` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Actions: executed=3
- Learned:
  - `acid_11_batched_fact_rule_retract_mix`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_12_compound_repair_with_query`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_13_branch_preservation_after_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
## 2026-04-11T14:58:09+00:00
- Run: `walkcycle3_20260411_1420` | range `acid_06_compound_unpacking -> acid_13_branch_preservation_after_repair` | selected `8` | executed `8` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Actions: executed=8
- Learned:
  - `acid_06_compound_unpacking`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_07_relation_drift_pressure`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_08_contradiction_reconciliation`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_09_compound_rule_unpacking`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_10_compound_retract_unpacking`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_11_batched_fact_rule_retract_mix`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_12_compound_repair_with_query`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_13_branch_preservation_after_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
## 2026-04-11T15:00:09+00:00
- Run: `walkcycle4_20260411_1427` | range `acid_11_batched_fact_rule_retract_mix -> acid_14_unary_conjunction_retract_effect` | selected `4` | executed `4` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Actions: executed=4
- Learned:
  - `acid_11_batched_fact_rule_retract_mix`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_12_compound_repair_with_query`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_13_branch_preservation_after_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_14_unary_conjunction_retract_effect`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
## 2026-04-11T15:46:17+00:00
- Run: `walkcycle5a_20260411_114443` | range `acid_11_batched_fact_rule_retract_mix -> acid_16_rule_stack_retarget` | selected `6` | executed `6` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Actions: executed=6
- Learned:
  - `acid_11_batched_fact_rule_retract_mix`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_12_compound_repair_with_query`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_13_branch_preservation_after_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_14_unary_conjunction_retract_effect`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_15_dual_track_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_16_rule_stack_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
## 2026-04-11T15:48:03+00:00
- Run: `walkcycle5b_20260411_114630` | range `acid_11_batched_fact_rule_retract_mix -> acid_16_rule_stack_retarget` | selected `6` | executed `6` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Actions: executed=6
- Learned:
  - `acid_11_batched_fact_rule_retract_mix`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_12_compound_repair_with_query`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_13_branch_preservation_after_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_14_unary_conjunction_retract_effect`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_15_dual_track_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_16_rule_stack_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
## 2026-04-11T15:49:42+00:00
- Run: `walkcycle5c_20260411_114809` | range `acid_11_batched_fact_rule_retract_mix -> acid_16_rule_stack_retarget` | selected `6` | executed `6` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Actions: executed=6
- Learned:
  - `acid_11_batched_fact_rule_retract_mix`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_12_compound_repair_with_query`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_13_branch_preservation_after_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_14_unary_conjunction_retract_effect`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_15_dual_track_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_16_rule_stack_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
## 2026-04-11T16:14:35+00:00
- Run: `newrungs_20260411_121354` | range `rung_17_robustness_easy_paraphrase_chain -> rung_19_robustness_hard_hedged_retarget` | selected `3` | executed `3` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Actions: executed=3
- Learned:
  - `rung_17_robustness_easy_paraphrase_chain`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_18_robustness_easy_inversion_retract`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_19_robustness_hard_hedged_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
## 2026-04-11T16:34:15+00:00
- Run: `push_onward_main_20260411_123333` | range `rung_17_robustness_easy_paraphrase_chain -> rung_19_robustness_hard_hedged_retarget` | selected `3` | executed `3` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Actions: executed=3
- Learned:
  - `rung_17_robustness_easy_paraphrase_chain`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_18_robustness_easy_inversion_retract`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_19_robustness_hard_hedged_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
## 2026-04-11T16:47:04+00:00
- Run: `push_onward_blended_20260411_124443` | range `acid_11_batched_fact_rule_retract_mix -> rung_19_robustness_hard_hedged_retarget` | selected `9` | executed `9` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Actions: executed=9
- Learned:
  - `acid_11_batched_fact_rule_retract_mix`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_12_compound_repair_with_query`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_13_branch_preservation_after_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_14_unary_conjunction_retract_effect`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_15_dual_track_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_16_rule_stack_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_17_robustness_easy_paraphrase_chain`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_18_robustness_easy_inversion_retract`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_19_robustness_hard_hedged_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
## 2026-04-11T16:48:53+00:00
- Run: `rung20_22_bg` | range `rung_20_robustness_hard_inversion_chain -> rung_22_robustness_hard_retarget_lineage` | selected `3` | executed `3` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Actions: executed=3
- Learned:
  - `rung_20_robustness_hard_inversion_chain`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_21_robustness_hard_hedged_retract_shift`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_22_robustness_hard_retarget_lineage`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
## 2026-04-11T16:53:13+00:00
- Run: `rolling4_20260411_124934` | range `start -> end` | selected `4` | executed `4` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Actions: executed=4
- Learned:
  - `rung_19_robustness_hard_hedged_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_20_robustness_hard_inversion_chain`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_21_robustness_hard_hedged_retract_shift`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_22_robustness_hard_retarget_lineage`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
## 2026-04-11T17:01:43+00:00
- Run: `main_lowlane_20260411_125544` | range `acid_13_branch_preservation_after_repair -> rung_22_robustness_hard_retarget_lineage` | selected `10` | executed `10` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Actions: executed=10
- Learned:
  - `acid_13_branch_preservation_after_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_14_unary_conjunction_retract_effect`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_15_dual_track_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `acid_16_rule_stack_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_17_robustness_easy_paraphrase_chain`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_18_robustness_easy_inversion_retract`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_19_robustness_hard_hedged_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_20_robustness_hard_inversion_chain`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_21_robustness_hard_hedged_retract_shift`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_22_robustness_hard_retarget_lineage`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
## 2026-04-11T17:06:19+00:00
- Run: `rolling4_live_20260411_130412` | range `start -> end` | selected `4` | executed `4` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `a2807206dfc6`
- Actions: executed=4
- Learned:
  - `rung_22_robustness_hard_retarget_lineage`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_23_robustness_hard_repair_bridge`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_24_robustness_hard_passive_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
  - `rung_25_robustness_hard_branch_preservation`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-a2807206dfc6.
## 2026-04-11T17:16:35+00:00
- Run: `spaced_tail4_20260411_131304` | range `start -> end` | selected `4` | executed `4` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=4
- Learned:
  - `rung_35_robustness_hard_passive_voice_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_35_spacing_passive_direction_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_40_robustness_hard_hedged_inversion_bundle`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_40_spacing_hedged_inverse_guard`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-11T17:28:51+00:00
- Run: `bigjumps_45_99_20260411_132712` | range `rung_45_spacing_inverse_parent_bundle -> rung_99_spacing_max_english_directional_stress` | selected `7` | executed `7` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=7
- Learned:
  - `rung_45_spacing_inverse_parent_bundle`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_50_spacing_passive_inverse_mix`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_60_spacing_hedged_correction_direction`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_70_spacing_multi_branch_inverse_repair`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_80_spacing_query_inversion_guard`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_90_spacing_direction_consistency_stress`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_99_spacing_max_english_directional_stress`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-11T17:44:48+00:00
- Run: `fuzzy_replay_20260411_133658` | range `rung_100_fuzzy_tail_directional_chatty -> rung_130_fuzzy_tail_soft_retract_language` | selected `4` | executed `4` | skipped `0` | failed `2`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=4
- Learned:
  - `rung_100_fuzzy_tail_directional_chatty`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_110_fuzzy_tail_fragmented_syntax`: timed out after 420s.
  - `rung_120_fuzzy_tail_name_noise`: subprocess failed (return code 1).
  - `rung_130_fuzzy_tail_soft_retract_language`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-11T17:56:00+00:00
- Run: `ce_proxy_context_hardening` | range `rung_140 + synthetic probe` | selected `2` | executed `2` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` parser + `gpt-oss:20b` clarification | ctx `8192/16384` | CE `0.90-0.95` | prompt `1e43c641b01b`
- Actions: executed=2
- Learned:
  - Clarification path was previously bypassed when parse returned `needs_clarification=true` but failed strict fact grounding (`parent(X, mia)`), causing hard reject before Q&A.
  - Fix applied: validation errors are now deferrable into clarification when `needs_clarification=true`, so noisy pronoun turns can enter Q&A and reparse.
  - `rung_140_ce_pronoun_typo_missing_qmark` now passes with 1 clarification round instead of rejection (report: `tmp/runs/ce_proxy_check_rung140_v2.json`).
  - Clarification responder now receives deterministic context pack (KB clause snapshot + recent accepted turns) plus confidence floor gating before answer acceptance.
  - New risk surfaced: fallback parser can literalize pronouns (`he`) and generate weak clarification prompts; patch in progress to force pronoun fallbacks into explicit clarification-needed payloads.
## 2026-04-11T18:00:00+00:00
- Run: `ce_proxy_context_probe_v2` | range `synthetic responder only` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` parser + `gpt-oss:20b` clarification | ctx `8192/16384` | CE `0.95` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - Pronoun fallback now triggers explicit clarification (`Who does 'he' refer to?`) instead of committing literal atom `he`.
  - Synthetic clarification used deterministic context pack successfully: `answer=noah`, `answer_confidence=0.9`, `answer_context_kb_clause_count=1`, `answer_context_recent_turn_count=1`.
  - Probe passed end-to-end with one synthetic clarification round and full validation pass (`3/3`).
  - Evidence report: `tmp/runs/ce_synthetic_context_probe_run_v2.json`.
## 2026-04-11T18:05:00+00:00
- Run: `clarification_cadence_baseline` | range `rung_140/150/160/170` | selected `16` | executed `16` | skipped `0` | failed `6`
- Runtime: `ollama` / `qwen3.5:9b` parser + `gpt-oss:20b` clarification | ctx `8192/16384` | CE grid `{0.75,0.90}` | min_conf grid `{0.45,0.60}`
- Actions: executed=16
- Learned:
  - Best baseline among tested settings: `ce_0.75__mc_0.45` (pass_rate 0.75).
  - `rung_150` remains the consistent weak point (3/4) across all tested CE/min-confidence combinations.
  - Higher CE (`0.90`) increased clarification activity in `rung_160` (including synthetic rounds) and exposed extra defer/fail pressure.
  - Baseline summary artifact: `tmp/runs/clarification_cadence_summary_baseline_20260411.json`.

## 2026-04-11T18:07:00+00:00
- Run: `confirmation_gate_recording_probe` | range `tmp_confirmation_gate_probe` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` parser + `gpt-oss:20b` clarification | `--require-final-confirmation` enabled
- Actions: executed=1
- Learned:
  - Final yes/no gate is now wired and recorded per turn (`confirmation_question`, `confirmation_answer`, `confirmation_result`).
  - Clarification + confirmation stack works together: unresolved pronoun was clarified by responder, then accepted by scripted final confirmation before write apply.
  - New top-level metric added: `turns_confirmation_requested`.
  - Probe evidence: `tmp/runs/tmp_confirmation_gate_probe_run.json`.
## 2026-04-11T18:12:00+00:00
- Run: `clarification_cadence_baseline_v2` | range `rung_140/150/160/170` | selected `16` | executed `16` | skipped `0` | failed `2`
- Runtime: `ollama` / `qwen3.5:9b` parser + `gpt-oss:20b` clarification | CE grid `{0.75,0.90}` | min_conf grid `{0.45,0.60}`
- Actions: executed=16
- Learned:
  - After scenario fixes, CE cadence reached full pass for `ce=0.75` at both tested confidence floors (`0.45` and `0.60`).
  - `ce=0.90` remains over-eager on retract noise: parser can consume both scripted clarification answers but still asks a third confirmation-style clarification and hits max rounds.
  - Resulting guidance: for current noisy-English pack, `ceâ‰ˆ0.75` is the stable operating point; if running `ce=0.90`, increase max clarification rounds or tighten clar loop-stop heuristics.
  - Summary artifact: `tmp/runs/clarification_cadence_summary_baseline_v2_20260411.json`.
## 2026-04-11T21:21:09+00:00
- Run: `auto_frontier_a1_fix1` | range `rung_28_robustness_hard_parallel_branch_retarget -> rung_28_robustness_hard_parallel_branch_retarget` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_28_robustness_hard_parallel_branch_retarget`: subprocess failed (return code 1).
## 2026-04-11T21:21:55+00:00
- Run: `auto_frontier_a1_fix2` | range `rung_28_robustness_hard_parallel_branch_retarget -> rung_28_robustness_hard_parallel_branch_retarget` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_28_robustness_hard_parallel_branch_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-11T21:36:59+00:00
- Run: `auto_frontier_fix2` | range `rung_120_fuzzy_tail_name_noise -> rung_120_fuzzy_tail_name_noise` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_120_fuzzy_tail_name_noise`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-11T21:37:23+00:00
- Run: `auto_frontier_fix2` | range `rung_180_ce_noisy_pronoun_reverse_guard -> rung_180_ce_noisy_pronoun_reverse_guard` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_180_ce_noisy_pronoun_reverse_guard`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
## 2026-04-11T21:37:54+00:00
- Run: `auto_frontier_fix2` | range `rung_200_ce_selective_branch_repair_queries -> rung_200_ce_selective_branch_repair_queries` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_200_ce_selective_branch_repair_queries`: subprocess failed (return code 1).
## 2026-04-11T21:39:02+00:00
- Run: `auto_frontier_fix3` | range `rung_200_ce_selective_branch_repair_queries -> rung_200_ce_selective_branch_repair_queries` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_200_ce_selective_branch_repair_queries`: passed 8/8; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
## 2026-04-11T22:04:09+00:00
- Run: `auto_frontier_fix3` | range `rung_110_fuzzy_tail_fragmented_syntax -> rung_110_fuzzy_tail_fragmented_syntax` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_110_fuzzy_tail_fragmented_syntax`: timed out after 1500s.
## 2026-04-11T22:16:57+00:00
- Run: `auto_frontier_fix4` | range `rung_110_fuzzy_tail_fragmented_syntax -> rung_110_fuzzy_tail_fragmented_syntax` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_110_fuzzy_tail_fragmented_syntax`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-11T22:56:17+00:00
- Run: `auto_cycle_full_20260411` | range `start -> end` | selected `56` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `stage_00_foreign_unseen_probe`: subprocess failed (return code 1).
## 2026-04-11T23:18:12+00:00
- Run: `auto_cycle_stage1plus_20260411` | range `stage_01_facts_only -> end` | selected `54` | executed `21` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=21
- Learned:
  - `stage_01_facts_only`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `stage_02_rule_ingest`: passed 1/1; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `stage_03_transitive_chain`: passed 1/1; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_03_temporal_override`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_04_alias_pressure`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_05_long_context_lineage`: passed 5/5; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_06_compound_unpacking`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_07_relation_drift_pressure`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_08_contradiction_reconciliation`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_09_compound_rule_unpacking`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_10_compound_retract_unpacking`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_11_batched_fact_rule_retract_mix`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_12_compound_repair_with_query`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_13_branch_preservation_after_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_14_unary_conjunction_retract_effect`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_15_dual_track_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_16_rule_stack_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_17_robustness_easy_paraphrase_chain`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_18_robustness_easy_inversion_retract`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_19_robustness_hard_hedged_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_20_robustness_hard_inversion_chain`: timed out after 900s.
## 2026-04-11T23:22:29+00:00
- Run: `debug_rung20` | range `rung_20_robustness_hard_inversion_chain -> rung_20_robustness_hard_inversion_chain` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_20_robustness_hard_inversion_chain`: timed out after 240s.
## 2026-04-11T23:27:25+00:00
- Run: `debug_rung20_forceempty` | range `rung_20_robustness_hard_inversion_chain -> rung_20_robustness_hard_inversion_chain` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_20_robustness_hard_inversion_chain`: timed out after 240s.
## 2026-04-11T23:35:20+00:00
- Run: `auto_cycle_cleanroot_20260411` | range `stage_01_facts_only -> end` | selected `54` | executed `24` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=24
- Learned:
  - `stage_01_facts_only`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `stage_02_rule_ingest`: passed 1/1; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `stage_03_transitive_chain`: passed 1/1; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_03_temporal_override`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_04_alias_pressure`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_05_long_context_lineage`: passed 5/5; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_06_compound_unpacking`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_07_relation_drift_pressure`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_08_contradiction_reconciliation`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_09_compound_rule_unpacking`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_10_compound_retract_unpacking`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_11_batched_fact_rule_retract_mix`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_12_compound_repair_with_query`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_13_branch_preservation_after_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_14_unary_conjunction_retract_effect`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_15_dual_track_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_16_rule_stack_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_17_robustness_easy_paraphrase_chain`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_18_robustness_easy_inversion_retract`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_19_robustness_hard_hedged_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_20_robustness_hard_inversion_chain`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_21_robustness_hard_hedged_retract_shift`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_22_robustness_hard_retarget_lineage`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_23_robustness_hard_repair_bridge`: subprocess failed (return code 1).
## 2026-04-11T23:36:24+00:00
- Run: `verify_rung23_fix` | range `rung_23_robustness_hard_repair_bridge -> rung_23_robustness_hard_repair_bridge` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_23_robustness_hard_repair_bridge`: subprocess failed (return code 1).
## 2026-04-11T23:36:58+00:00
- Run: `verify_rung23_fix2` | range `rung_23_robustness_hard_repair_bridge -> rung_23_robustness_hard_repair_bridge` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_23_robustness_hard_repair_bridge`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-11T23:51:16+00:00
- Run: `auto_cycle_cleanroot_tail_20260411` | range `rung_24_robustness_hard_passive_retarget -> end` | selected `30` | executed `30` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=30
- Learned:
  - `rung_24_robustness_hard_passive_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_25_robustness_hard_branch_preservation`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_26_robustness_hard_double_repair_chain`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_27_robustness_hard_midstream_query_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_28_robustness_hard_parallel_branch_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_30_robustness_hard_role_inversion_parent_form`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_30_spacing_role_inversion_pressure`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_35_robustness_hard_passive_voice_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_35_spacing_passive_direction_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_40_robustness_hard_hedged_inversion_bundle`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_40_spacing_hedged_inverse_guard`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_45_spacing_inverse_parent_bundle`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_50_spacing_passive_inverse_mix`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_60_spacing_hedged_correction_direction`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_70_spacing_multi_branch_inverse_repair`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_80_spacing_query_inversion_guard`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_90_spacing_direction_consistency_stress`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_99_spacing_max_english_directional_stress`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_100_fuzzy_tail_directional_chatty`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_110_fuzzy_tail_fragmented_syntax`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_120_fuzzy_tail_name_noise`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_130_fuzzy_tail_soft_retract_language`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_140_ce_pronoun_typo_missing_qmark`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_150_ce_typo_uncertainty_chain`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_160_ce_soft_retract_noise`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_170_ce_pronoun_followup_no_qmark`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_180_ce_noisy_pronoun_reverse_guard`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_190_ce_midstream_retarget_queries`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_200_ce_selective_branch_repair_queries`: passed 8/8; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `story_goldilocks_roundtrip`: subprocess failed (return code 1).
## 2026-04-12T00:08:47+00:00
- Run: `auto_cycle_stage1_to_rung200_clean_20260411` | range `stage_01_facts_only -> rung_200_ce_selective_branch_repair_queries` | selected `53` | executed `53` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=53
- Learned:
  - `stage_01_facts_only`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `stage_02_rule_ingest`: passed 1/1; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `stage_03_transitive_chain`: passed 1/1; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_03_temporal_override`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_04_alias_pressure`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_05_long_context_lineage`: passed 5/5; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_06_compound_unpacking`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_07_relation_drift_pressure`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_08_contradiction_reconciliation`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_09_compound_rule_unpacking`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_10_compound_retract_unpacking`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_11_batched_fact_rule_retract_mix`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_12_compound_repair_with_query`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_13_branch_preservation_after_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_14_unary_conjunction_retract_effect`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_15_dual_track_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `acid_16_rule_stack_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_17_robustness_easy_paraphrase_chain`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_18_robustness_easy_inversion_retract`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_19_robustness_hard_hedged_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_20_robustness_hard_inversion_chain`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_21_robustness_hard_hedged_retract_shift`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_22_robustness_hard_retarget_lineage`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_23_robustness_hard_repair_bridge`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_24_robustness_hard_passive_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_25_robustness_hard_branch_preservation`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_26_robustness_hard_double_repair_chain`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_27_robustness_hard_midstream_query_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_28_robustness_hard_parallel_branch_retarget`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_30_robustness_hard_role_inversion_parent_form`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_30_spacing_role_inversion_pressure`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_35_robustness_hard_passive_voice_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_35_spacing_passive_direction_repair`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_40_robustness_hard_hedged_inversion_bundle`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_40_spacing_hedged_inverse_guard`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_45_spacing_inverse_parent_bundle`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_50_spacing_passive_inverse_mix`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_60_spacing_hedged_correction_direction`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_70_spacing_multi_branch_inverse_repair`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_80_spacing_query_inversion_guard`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_90_spacing_direction_consistency_stress`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_99_spacing_max_english_directional_stress`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_100_fuzzy_tail_directional_chatty`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_110_fuzzy_tail_fragmented_syntax`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_120_fuzzy_tail_name_noise`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_130_fuzzy_tail_soft_retract_language`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_140_ce_pronoun_typo_missing_qmark`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_150_ce_typo_uncertainty_chain`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_160_ce_soft_retract_noise`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_170_ce_pronoun_followup_no_qmark`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_180_ce_noisy_pronoun_reverse_guard`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_190_ce_midstream_retarget_queries`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_200_ce_selective_branch_repair_queries`: passed 8/8; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
## 2026-04-12T00:20:55+00:00
- Run: `auto_newrungs_210_220_20260412` | range `rung_210_fuzzy_ce_selective_edge_rebuild -> rung_220_fuzzy_ce_rule_timing_branch_swap` | selected `2` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_210_fuzzy_ce_selective_edge_rebuild`: subprocess failed (return code 1).
## 2026-04-12T00:22:49+00:00
- Run: `verify_rung210_fix1_20260412` | range `rung_210_fuzzy_ce_selective_edge_rebuild -> rung_210_fuzzy_ce_selective_edge_rebuild` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_210_fuzzy_ce_selective_edge_rebuild`: passed 9/9; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
## 2026-04-12T00:23:22+00:00
- Run: `verify_rung220_20260412` | range `rung_220_fuzzy_ce_rule_timing_branch_swap -> rung_220_fuzzy_ce_rule_timing_branch_swap` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_220_fuzzy_ce_rule_timing_branch_swap`: subprocess failed (return code 1).
## 2026-04-12T00:24:40+00:00
- Run: `verify_rung220_fix1_20260412` | range `rung_220_fuzzy_ce_rule_timing_branch_swap -> rung_220_fuzzy_ce_rule_timing_branch_swap` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_220_fuzzy_ce_rule_timing_branch_swap`: passed 9/9; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
## 2026-04-12T00:25:39+00:00
- Run: `verify_rungs_210_220_pair_20260412` | range `rung_210_fuzzy_ce_selective_edge_rebuild -> rung_220_fuzzy_ce_rule_timing_branch_swap` | selected `2` | executed `2` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=2
- Learned:
  - `rung_210_fuzzy_ce_selective_edge_rebuild`: passed 9/9; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_220_fuzzy_ce_rule_timing_branch_swap`: passed 9/9; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
## 2026-04-12T00:26:44+00:00
- Run: `verify_rung230_20260412` | range `rung_230_fuzzy_ce_branch_exclusion_language -> rung_230_fuzzy_ce_branch_exclusion_language` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_230_fuzzy_ce_branch_exclusion_language`: subprocess failed (return code 1).
## 2026-04-12T02:16:11+00:00
- Run: `verify_rung230_fix1_20260412` | range `rung_230_fuzzy_ce_branch_exclusion_language -> rung_230_fuzzy_ce_branch_exclusion_language` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_230_fuzzy_ce_branch_exclusion_language`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-12T02:20:38+00:00
- Run: `sanity_210_230_20260412` | range `rung_210_fuzzy_ce_selective_edge_rebuild -> rung_230_fuzzy_ce_branch_exclusion_language` | selected `3` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_210_fuzzy_ce_selective_edge_rebuild`: subprocess failed (return code 1).
## 2026-04-12T02:21:14+00:00
- Run: `r210_rep1_20260412` | range `rung_210_fuzzy_ce_selective_edge_rebuild -> rung_210_fuzzy_ce_selective_edge_rebuild` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_210_fuzzy_ce_selective_edge_rebuild`: subprocess failed (return code 1).
## 2026-04-12T02:21:32+00:00
- Run: `r210_rep2_20260412` | range `rung_210_fuzzy_ce_selective_edge_rebuild -> rung_210_fuzzy_ce_selective_edge_rebuild` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_210_fuzzy_ce_selective_edge_rebuild`: subprocess failed (return code 1).
## 2026-04-12T02:21:50+00:00
- Run: `r210_rep3_20260412` | range `rung_210_fuzzy_ce_selective_edge_rebuild -> rung_210_fuzzy_ce_selective_edge_rebuild` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_210_fuzzy_ce_selective_edge_rebuild`: subprocess failed (return code 1).
## 2026-04-12T02:23:29+00:00
- Run: `stability_210_220_after_staysfix_20260412` | range `rung_210_fuzzy_ce_selective_edge_rebuild -> rung_220_fuzzy_ce_rule_timing_branch_swap` | selected `2` | executed `2` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=2
- Learned:
  - `rung_210_fuzzy_ce_selective_edge_rebuild`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_220_fuzzy_ce_rule_timing_branch_swap`: passed 9/9; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
## 2026-04-12T02:23:53+00:00
- Run: `stability_230_after_staysfix_20260412` | range `rung_230_fuzzy_ce_branch_exclusion_language -> rung_230_fuzzy_ce_branch_exclusion_language` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen3.5:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_230_fuzzy_ce_branch_exclusion_language`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-12T04:52:03+00:00
- Run: `frontier_refresh_20260412` | range `rung_230_fuzzy_ce_branch_exclusion_language -> rung_261_sim_fantasy_overlord_natural_flow` | selected `7` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_230_fuzzy_ce_branch_exclusion_language`: subprocess failed (return code 1).
## 2026-04-12T04:56:21+00:00
- Run: `frontier_refresh_full_20260412` | range `rung_230_fuzzy_ce_branch_exclusion_language -> rung_261_sim_fantasy_overlord_natural_flow` | selected `7` | executed `7` | skipped `0` | failed `5`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=7
- Learned:
  - `rung_230_fuzzy_ce_branch_exclusion_language`: subprocess failed (return code 1).
  - `rung_240_ops_hospital_vendor_delay_core`: subprocess failed (return code 1).
  - `rung_241_ops_hospital_cpm_natural_flow`: subprocess failed (return code 1).
  - `rung_250_ops_indie_launch_uncertainty_routing`: subprocess failed (return code 1).
  - `rung_251_ops_indie_warroom_natural_flow`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_260_sim_fantasy_state_repair`: subprocess failed (return code 1).
  - `rung_261_sim_fantasy_overlord_natural_flow`: passed 5/5; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-12T04:57:50+00:00
- Run: `frontier_storypush_20260412` | range `rung_270_story_lineage_fragmented_ingest -> rung_290_story_multi_branch_pronoun_pressure` | selected `3` | executed `3` | skipped `0` | failed `3`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=3
- Learned:
  - `rung_270_story_lineage_fragmented_ingest`: subprocess failed (return code 1).
  - `rung_280_story_revision_temporal_shift`: subprocess failed (return code 1).
  - `rung_290_story_multi_branch_pronoun_pressure`: subprocess failed (return code 1).
## 2026-04-12T05:15:34+00:00
- Run: `frontier_storypush_refined_20260412` | range `rung_270_story_lineage_fragmented_ingest -> rung_290_story_multi_branch_pronoun_pressure` | selected `3` | executed `3` | skipped `0` | failed `3`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=3
- Learned:
  - `rung_270_story_lineage_fragmented_ingest`: subprocess failed (return code 1).
  - `rung_280_story_revision_temporal_shift`: timed out after 900s.
  - `rung_290_story_multi_branch_pronoun_pressure`: subprocess failed (return code 1).
## 2026-04-12T05:20:46+00:00
- Run: `frontier_storypush_fixA_20260412` | range `rung_270_story_lineage_fragmented_ingest -> rung_270_story_lineage_fragmented_ingest` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_270_story_lineage_fragmented_ingest`: subprocess failed (return code 1).
## 2026-04-12T05:21:47+00:00
- Run: `frontier_storypush_fixB_20260412` | range `rung_270_story_lineage_fragmented_ingest -> rung_270_story_lineage_fragmented_ingest` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_270_story_lineage_fragmented_ingest`: passed 11/11; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-12T05:22:28+00:00
- Run: `frontier_storypush_fixB_20260412` | range `rung_290_story_multi_branch_pronoun_pressure -> rung_290_story_multi_branch_pronoun_pressure` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_290_story_multi_branch_pronoun_pressure`: subprocess failed (return code 1).
## 2026-04-12T05:23:24+00:00
- Run: `frontier_storypush_fixC_20260412` | range `rung_290_story_multi_branch_pronoun_pressure -> rung_290_story_multi_branch_pronoun_pressure` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_290_story_multi_branch_pronoun_pressure`: subprocess failed (return code 1).
## 2026-04-12T05:24:18+00:00
- Run: `frontier_storypush_fixD_20260412` | range `rung_290_story_multi_branch_pronoun_pressure -> rung_290_story_multi_branch_pronoun_pressure` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_290_story_multi_branch_pronoun_pressure`: passed 12/12; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-12T05:25:05+00:00
- Run: `frontier_storypush_fixB_20260412` | range `rung_280_story_revision_temporal_shift -> rung_280_story_revision_temporal_shift` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_280_story_revision_temporal_shift`: passed 12/12; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-12T05:27:20+00:00
- Run: `frontier_storypush_fixD_pack_20260412` | range `rung_270_story_lineage_fragmented_ingest -> rung_290_story_multi_branch_pronoun_pressure` | selected `3` | executed `3` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=3
- Learned:
  - `rung_270_story_lineage_fragmented_ingest`: passed 11/11; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_280_story_revision_temporal_shift`: passed 12/12; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_290_story_multi_branch_pronoun_pressure`: passed 12/12; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-12T05:28:53+00:00
- Run: `frontier_storypush_new300_320_baseline_20260412` | range `rung_300_story_nested_corrections -> rung_320_story_temporal_exception_rebinding` | selected `3` | executed `3` | skipped `0` | failed `3`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=3
- Learned:
  - `rung_300_story_nested_corrections`: subprocess failed (return code 1).
  - `rung_310_story_cross_clause_pronoun_weave`: subprocess failed (return code 1).
  - `rung_320_story_temporal_exception_rebinding`: subprocess failed (return code 1).
## 2026-04-12T05:51:08+00:00
- Run: `frontier_storypush_new300_320_refined1_20260412` | range `rung_300_story_nested_corrections -> rung_320_story_temporal_exception_rebinding` | selected `3` | executed `3` | skipped `0` | failed `2`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=3
- Learned:
  - `rung_300_story_nested_corrections`: timed out after 600s.
  - `rung_310_story_cross_clause_pronoun_weave`: passed 15/15; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_320_story_temporal_exception_rebinding`: timed out after 600s.
## 2026-04-12T06:01:03+00:00
- Run: `frontier_storypush_new300_refined1_20260412` | range `rung_300_story_nested_corrections -> rung_300_story_nested_corrections` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_300_story_nested_corrections`: timed out after 600s.
## 2026-04-12T06:02:28+00:00
- Run: `frontier_storypush_new300_refined2_20260412` | range `rung_300_story_nested_corrections -> rung_300_story_nested_corrections` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_300_story_nested_corrections`: subprocess failed (return code 1).
## 2026-04-12T06:03:34+00:00
- Run: `frontier_storypush_new300_refined3_20260412` | range `rung_300_story_nested_corrections -> rung_300_story_nested_corrections` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_300_story_nested_corrections`: passed 17/17; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-12T06:04:14+00:00
- Run: `frontier_storypush_new310_refined2_20260412` | range `rung_310_story_cross_clause_pronoun_weave -> rung_310_story_cross_clause_pronoun_weave` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_310_story_cross_clause_pronoun_weave`: passed 15/15; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-12T06:05:04+00:00
- Run: `frontier_storypush_new320_refined2_20260412` | range `rung_320_story_temporal_exception_rebinding -> rung_320_story_temporal_exception_rebinding` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_320_story_temporal_exception_rebinding`: subprocess failed (return code 1).
## 2026-04-12T06:06:16+00:00
- Run: `frontier_storypush_new320_refined3_20260412` | range `rung_320_story_temporal_exception_rebinding -> rung_320_story_temporal_exception_rebinding` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_320_story_temporal_exception_rebinding`: passed 17/17; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-12T06:08:31+00:00
- Run: `frontier_storypush_new300_320_refined_pack_20260412` | range `rung_300_story_nested_corrections -> rung_320_story_temporal_exception_rebinding` | selected `3` | executed `3` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=3
- Learned:
  - `rung_300_story_nested_corrections`: passed 17/17; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_310_story_cross_clause_pronoun_weave`: passed 15/15; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_320_story_temporal_exception_rebinding`: passed 17/17; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-12T06:12:40+00:00
- Run: `frontier_storypush_270_320_check_20260412` | range `rung_270_story_lineage_fragmented_ingest -> rung_320_story_temporal_exception_rebinding` | selected `6` | executed `6` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=6
- Learned:
  - `rung_270_story_lineage_fragmented_ingest`: passed 11/11; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_280_story_revision_temporal_shift`: passed 12/12; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_290_story_multi_branch_pronoun_pressure`: passed 12/12; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_300_story_nested_corrections`: passed 17/17; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_310_story_cross_clause_pronoun_weave`: passed 15/15; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_320_story_temporal_exception_rebinding`: passed 17/17; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-12T06:14:01+00:00
- Run: `frontier_storypush_new330_baseline_20260412` | range `rung_330_story_booklet_cross_scene_rebind -> rung_330_story_booklet_cross_scene_rebind` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_330_story_booklet_cross_scene_rebind`: subprocess failed (return code 1).
## 2026-04-12T06:15:05+00:00
- Run: `frontier_storypush_new330_refined2_20260412` | range `rung_330_story_booklet_cross_scene_rebind -> rung_330_story_booklet_cross_scene_rebind` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_330_story_booklet_cross_scene_rebind`: passed 15/15; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-12T06:18:00+00:00
- Run: `frontier_storypush_300_330_check_20260412` | range `rung_300_story_nested_corrections -> rung_330_story_booklet_cross_scene_rebind` | selected `4` | executed `4` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=4
- Learned:
  - `rung_300_story_nested_corrections`: passed 17/17; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_310_story_cross_clause_pronoun_weave`: passed 15/15; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_320_story_temporal_exception_rebinding`: passed 17/17; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_330_story_booklet_cross_scene_rebind`: passed 15/15; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
## 2026-04-12T10:05:40+00:00
- Run: `frontier_ce_340_350_baseline_20260412` | range `rung_340_ce_story_pronoun_transfer -> rung_350_ce_story_multi_round_revision` | selected `2` | executed `2` | skipped `0` | failed `2`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.85` | prompt `1e43c641b01b`
- Actions: executed=2
- Learned:
  - `rung_340_ce_story_pronoun_transfer`: subprocess failed (return code 1).
  - `rung_350_ce_story_multi_round_revision`: subprocess failed (return code 1).
## 2026-04-12T10:07:17+00:00
- Run: `frontier_ce_340_350_refined1_20260412` | range `rung_340_ce_story_pronoun_transfer -> rung_350_ce_story_multi_round_revision` | selected `2` | executed `2` | skipped `0` | failed `2`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.85` | prompt `1e43c641b01b`
- Actions: executed=2
- Learned:
  - `rung_340_ce_story_pronoun_transfer`: subprocess failed (return code 1).
  - `rung_350_ce_story_multi_round_revision`: subprocess failed (return code 1).
## 2026-04-12T10:09:30+00:00
- Run: `frontier_ce_340_single_refined2_20260412` | range `rung_340_ce_story_pronoun_transfer -> rung_340_ce_story_pronoun_transfer` | selected `1` | executed `1` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.85` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_340_ce_story_pronoun_transfer`: subprocess failed (return code 1).
## 2026-04-12T10:12:07+00:00
- Run: `frontier_ce_340_350_refined2_20260412` | range `rung_340_ce_story_pronoun_transfer -> rung_350_ce_story_multi_round_revision` | selected `2` | executed `2` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.85` | prompt `1e43c641b01b`
- Actions: executed=2
- Learned:
  - `rung_340_ce_story_pronoun_transfer`: passed 11/11; parse_fail=0, apply_fail=0, clar_rounds=3; prompt=sp-1e43c641b01b.
  - `rung_350_ce_story_multi_round_revision`: passed 11/11; parse_fail=0, apply_fail=0, clar_rounds=2; prompt=sp-1e43c641b01b.
## 2026-04-12T10:13:23+00:00
- Run: `frontier_ce_360_baseline_20260412` | range `rung_360_ce_story_branch_merge_noise -> rung_360_ce_story_branch_merge_noise` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.9` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_360_ce_story_branch_merge_noise`: passed 12/12; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
## 2026-04-12T10:15:55+00:00
- Run: `frontier_ce_340_360_check_20260412` | range `rung_340_ce_story_pronoun_transfer -> rung_360_ce_story_branch_merge_noise` | selected `3` | executed `3` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.9` | prompt `1e43c641b01b`
- Actions: executed=3
- Learned:
  - `rung_340_ce_story_pronoun_transfer`: passed 11/11; parse_fail=0, apply_fail=0, clar_rounds=3; prompt=sp-1e43c641b01b.
  - `rung_350_ce_story_multi_round_revision`: subprocess failed (return code 1).
  - `rung_360_ce_story_branch_merge_noise`: passed 12/12; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
## 2026-04-12T10:19:00+00:00
- Run: `frontier_ce_340_360_refined2_check_20260412` | range `rung_340_ce_story_pronoun_transfer -> rung_360_ce_story_branch_merge_noise` | selected `3` | executed `3` | skipped `0` | failed `1`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.9` | prompt `1e43c641b01b`
- Actions: executed=3
- Learned:
  - `rung_340_ce_story_pronoun_transfer`: passed 11/11; parse_fail=0, apply_fail=0, clar_rounds=3; prompt=sp-1e43c641b01b.
  - `rung_350_ce_story_multi_round_revision`: subprocess failed (return code 1).
  - `rung_360_ce_story_branch_merge_noise`: passed 12/12; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
## 2026-04-12T10:20:10+00:00
- Run: `frontier_ce_350_refined3_single_20260412` | range `rung_350_ce_story_multi_round_revision -> rung_350_ce_story_multi_round_revision` | selected `1` | executed `1` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.9` | prompt `1e43c641b01b`
- Actions: executed=1
- Learned:
  - `rung_350_ce_story_multi_round_revision`: passed 11/11; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
## 2026-04-12T10:22:39+00:00
- Run: `frontier_ce_340_360_refined3_check_20260412` | range `rung_340_ce_story_pronoun_transfer -> rung_360_ce_story_branch_merge_noise` | selected `3` | executed `3` | skipped `0` | failed `0`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.9` | prompt `1e43c641b01b`
- Actions: executed=3
- Learned:
  - `rung_340_ce_story_pronoun_transfer`: passed 11/11; parse_fail=0, apply_fail=0, clar_rounds=3; prompt=sp-1e43c641b01b.
  - `rung_350_ce_story_multi_round_revision`: passed 11/11; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_360_ce_story_branch_merge_noise`: passed 12/12; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
## 2026-04-13T01:41:58+00:00
- Run: `regression_230_449` | range `rung_230_fuzzy_ce_branch_exclusion_language -> rung_449_frontier_multibind_uncle_query` | selected `43` | executed `43` | skipped `0` | failed `7`
- Runtime: `ollama` / `qwen35-semparse:9b` / `core` | ctx `8192` | CE `0.35` | prompt `1e43c641b01b`
- Actions: executed=43
- Learned:
  - `rung_230_fuzzy_ce_branch_exclusion_language`: subprocess failed (return code 1).
  - `rung_240_ops_hospital_vendor_delay_core`: subprocess failed (return code 1).
  - `rung_241_ops_hospital_cpm_natural_flow`: subprocess failed (return code 1).
  - `rung_250_ops_indie_launch_uncertainty_routing`: subprocess failed (return code 1).
  - `rung_251_ops_indie_warroom_natural_flow`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_260_sim_fantasy_state_repair`: subprocess failed (return code 1).
  - `rung_261_sim_fantasy_overlord_natural_flow`: passed 5/5; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_270_story_lineage_fragmented_ingest`: passed 11/11; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_280_story_revision_temporal_shift`: passed 12/12; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_290_story_multi_branch_pronoun_pressure`: passed 12/12; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_300_story_nested_corrections`: passed 17/17; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_310_story_cross_clause_pronoun_weave`: passed 15/15; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_320_story_temporal_exception_rebinding`: passed 17/17; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_330_story_booklet_cross_scene_rebind`: passed 15/15; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_340_ce_story_pronoun_transfer`: passed 11/11; parse_fail=0, apply_fail=0, clar_rounds=3; prompt=sp-1e43c641b01b.
  - `rung_350_ce_story_multi_round_revision`: passed 11/11; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_360_ce_story_branch_merge_noise`: passed 12/12; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_370_progress_feasibility_alignment`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_380_progress_irrelevant_fact_filter`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_390_progress_goal_directed_clarification`: passed 1/1; parse_fail=0, apply_fail=0, clar_rounds=2; prompt=sp-1e43c641b01b.
  - `rung_400_progress_relevance_repair`: passed 1/1; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_410_progress_goal_context_steering`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_420_progress_focus_shift_transition`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_430_goldilocks_roundtrip_retry`: subprocess failed (return code 1).
  - `rung_431_book_goldilocks_raw_chaptered_qa`: subprocess failed (return code 1).
  - `rung_432_noise_pronoun_inversion_chain`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_433_noisy_inverse_retarget_repair`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=2; prompt=sp-1e43c641b01b.
  - `rung_434_dual_pronoun_flip_guard`: passed 7/7; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_435_frontier_checkpoint_compound_turns`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=2; prompt=sp-1e43c641b01b.
  - `rung_436_frontier_noise_typo_coref`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_437_frontier_policy_override_flow`: passed 7/7; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_438_frontier_multibind_query_pressure`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_439_frontier_plural_coref_exception_guard`: passed 5/5; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_440_frontier_policy_revision_loop`: passed 7/7; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_441_frontier_pronoun_bucket_shuffle`: passed 7/7; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_442_frontier_policy_multirevision_guard`: passed 9/9; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_443_frontier_dual_item_handoff_coref`: passed 7/7; parse_fail=0, apply_fail=0, clar_rounds=2; prompt=sp-1e43c641b01b.
  - `rung_444_frontier_unpunctuated_coref_sweep`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_445_frontier_compound_write_query_braid`: passed 6/6; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_446_frontier_policy_noisy_rebind_loop`: passed 7/7; parse_fail=0, apply_fail=0, clar_rounds=1; prompt=sp-1e43c641b01b.
  - `rung_447_confirmation_gate_single_yes`: passed 2/2; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_448_confirmation_gate_no_then_yes`: passed 3/3; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.
  - `rung_449_frontier_multibind_uncle_query`: passed 4/4; parse_fail=0, apply_fail=0, clar_rounds=0; prompt=sp-1e43c641b01b.

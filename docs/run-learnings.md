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
  - Resulting guidance: for current noisy-English pack, `ce≈0.75` is the stable operating point; if running `ce=0.90`, increase max clarification rounds or tighten clar loop-stop heuristics.
  - Summary artifact: `tmp/runs/clarification_cadence_summary_baseline_v2_20260411.json`.

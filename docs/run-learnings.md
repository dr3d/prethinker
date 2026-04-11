# Run Learnings

Append-only log of ladder cycle outcomes and what changed.
Auto-populated by `scripts/run_ladder.py` via `--learn-log`.

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

# Prethinker Test Sweep - April 14, 2026 (Latest)

## Configuration
- Parser model: `qwen3.5:9b` on local Ollama (`http://127.0.0.1:11434`)
- Prompt source: `modelfiles/semantic_parser_system_prompt.md` (runtime single-source, no double prompt)
- Clarification controls: `clarification_eagerness=0.35`, `max_clarification_rounds=2`
- Sweep scope: all 22 registered track suites

## Headline Score
- Track suites meeting target: **22/22**
- Perfect suites: **22/22**
- Scenario pass: **140/140 (100.0%)**
- Total track turns: **1802** | apply failures: **0** | parse failures: **0**
- Improvement from earlier same-day full sweep: **18/22 -> 22/22**

## Fix That Unblocked Final Frontier Lanes
- Prevented declared-atom context alignment from rewriting literal atoms on `explicit_command` turns.
- This removed the `policy_path -> policy_path_conditions` drift that was causing `rung_463` misses in cooperative/excursion frontier tracks.

## Latest Track Scorecard
| Track | Pass | Summary |
|---|---:|---|
| `book_acid_goldilocks` | 2/2 (100.0%) | `tmp/runs/tracks/track_book_acid_goldilocks_summary_20260414_postpatch3.json` |
| `examples_all` | 8/8 (100.0%) | `tmp/runs/tracks/track_examples_all_summary_20260414_postpatch4_verify.json` |
| `examples_demo_portfolio` | 5/5 (100.0%) | `tmp/runs/tracks/track_examples_demo_portfolio_summary_20260414_postpatch3_verify.json` |
| `examples_ops_natural` | 3/3 (100.0%) | `tmp/runs/tracks/track_examples_ops_natural_summary_20260414_postpatch3_verify.json` |
| `excursion_cooperative_v1` | 3/3 (100.0%) | `tmp/runs/tracks/track_excursion_cooperative_v1_summary_20260414_postpatch4_scan.json` |
| `excursion_cooperative_v1_full` | 6/6 (100.0%) | `tmp/runs/tracks/track_excursion_cooperative_v1_full_summary_20260414_postpatch4_fix.json` |
| `excursion_failure_promotions_v1` | 3/3 (100.0%) | `tmp/runs/tracks/track_excursion_failure_promotions_v1_summary_20260414_postpatch4_scan.json` |
| `excursion_frontier_v1` | 10/10 (100.0%) | `tmp/runs/tracks/track_excursion_frontier_v1_summary_20260414_postpatch4_scan.json` |
| `excursion_frontier_v2_full` | 12/12 (100.0%) | `tmp/runs/tracks/track_excursion_frontier_v2_full_summary_20260414_postpatch4_fix.json` |
| `excursion_middle_hn_v1` | 4/4 (100.0%) | `tmp/runs/tracks/track_excursion_middle_hn_v1_summary_20260414_postpatch4_scan.json` |
| `excursion_pilot_v1` | 2/2 (100.0%) | `tmp/runs/tracks/track_excursion_pilot_v1_summary_20260414_postpatch4_scan.json` |
| `excursion_wild_reddit_v1` | 3/3 (100.0%) | `tmp/runs/tracks/track_excursion_wild_reddit_v1_summary_20260414_postpatch4_scan.json` |
| `excursion_wild_v1_full` | 6/6 (100.0%) | `tmp/runs/tracks/track_excursion_wild_v1_full_summary_20260414_postpatch4_scan.json` |
| `frontier_clarification_probe_v1` | 3/3 (100.0%) | `tmp/runs/tracks/track_frontier_clarification_probe_v1_summary_20260414_postpatch4_scan.json` |
| `frontier_confirmation_probe_v1` | 2/2 (100.0%) | `tmp/runs/tracks/track_frontier_confirmation_probe_v1_summary_20260414_postpatch4_scan.json` |
| `frontier_language_width_v2` | 6/6 (100.0%) | `tmp/runs/tracks/track_frontier_language_width_v2_summary_20260414_postpatch.json` |
| `frontier_language_width_v3` | 9/9 (100.0%) | `tmp/runs/tracks/track_frontier_language_width_v3_summary_20260414_postpatch.json` |
| `frontier_language_width_v4` | 12/12 (100.0%) | `tmp/runs/tracks/track_frontier_language_width_v4_summary_20260414_postpatch.json` |
| `frontier_language_width_v5` | 15/15 (100.0%) | `tmp/runs/tracks/track_frontier_language_width_v5_summary_20260414_postpatch.json` |
| `frontier_language_width_v6` | 16/16 (100.0%) | `tmp/runs/tracks/track_frontier_language_width_v6_summary_20260414_postpatch3_sanity.json` |
| `frontier_language_width_v7_addons` | 2/2 (100.0%) | `tmp/runs/tracks/track_frontier_language_width_v7_addons_summary_20260414_postpatch4_scan.json` |
| `gate_ladder_frontier` | 8/8 (100.0%) | `tmp/runs/tracks/track_gate_ladder_frontier_summary_20260414_postpatch4_verify.json` |

## Key Artifacts (Patch Cycle)
- `tmp/runs/tracks/track_excursion_frontier_v2_full_summary_20260414_postpatch4_fix.json`
- `tmp/runs/tracks/track_excursion_cooperative_v1_full_summary_20260414_postpatch4_fix.json`
- `tmp/runs/tracks/rung_463_excursion_coop_fed_counterfactual_guard_patchcheck_20260414_2050.json`
- `tmp/runs/tracks/track_gate_ladder_frontier_summary_20260414_postpatch4_verify.json`
- `tmp/runs/tracks/track_examples_all_summary_20260414_postpatch4_verify.json`

## Notes
- Latest-status selection uses the most recent summary file per track in `tmp/runs/tracks`.
- Older sections were replaced to avoid stale 18/22 reporting.

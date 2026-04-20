# Temporal Interrogator Recovery - 2026-04-19

This note captures the April 19 follow-up batch aimed at the repo's main remaining honest weakness after the April 17 frontier sweep: temporal exam quality.

## What Changed

- `scripts/kb_interrogator.py`
  - added a guarded rescue for temporal exam queries that incorrectly require multiple `at_step(T, ...)` facts to share the exact same step
  - split fallback generation into:
    - normal fallback fill
    - temporal-first fallback fill used only to satisfy the temporal floor
- `tests/test_kb_interrogator_temporal.py`
  - new focused regressions for the shared-step repair path
  - new regression for temporal-first fallback ordering

Design rule:

- do not loosen general exam generation
- only rescue temporal queries when the relaxed distinct-step variant satisfies the original expectation
- do not let temporal-first fallback flood the whole exam on strong lanes

## Live Results

### Glitch Control

Baseline reference:
- `tmp/glitch_frontier_recovery_temporal2_20260417.summary.json`

New run:
- `tmp/glitch_frontier_recovery_temporal3_20260419.summary.json`

Delta:
- pipeline: `1/1 -> 1/1`
- coverage: `0.85 -> 0.85`
- precision: `0.92 -> 0.92`
- exam: `8/14 -> 11/14`
- temporal exam: `0/5 -> 3/5`
- final score: `0.8194 -> 0.8914`

Read:
- the structural lane was already fixed
- the interrogator now asks more answerable temporal questions against the same KB

### Mid Strict Narrative (`full`)

Baseline reference:
- `tmp/mid_pack_general_strict_temporal_recovery_fullfix2_20260417.summary.json`

New run:
- `tmp/mid_full_temporal_repair2_20260419.summary.json`

Delta:
- pipeline: `passed -> passed`
- coverage: `0.85 -> 0.91`
- precision: `0.85 -> 0.85`
- exam: `17/20 -> 17/20`
- temporal exam: `0/0 (floor unmet) -> 8/8`
- final score: `0.843 -> 0.9262`

Read:
- the main win is not raw exam count; it is that the temporal floor is no longer hollow
- this turns mid `full` into a more honest and better-balanced success case

### Upper-Mid Strict Narrative (`full`) Control

Baseline reference:
- `tmp/upper_mid_pack_general_strict_temporal_regressioncheck2_20260417.summary.json`

Control rerun:
- `tmp/upper_mid_full_temporal_repair2_20260419.summary.json`

Observed:
- pipeline: `passed`
- coverage: `0.85`
- precision: `0.92`
- exam: `16/20`
- temporal exam: `12/16`
- final score: `0.9039`

Read:
- no regression introduced by the temporal-floor fix
- the stronger lane held steady after the interrogator refinement

## Safety

- `python scripts/run_safety_gate.py` -> `120 passed`

## Bottom Line

This batch improved temporal evaluation quality without destabilizing the stable or stronger frontier lanes.

The repo's frontier story is now better than it was on April 17 in two ways:
- Glitch temporal reasoning is no longer stuck at zero.
- Mid `full` no longer "passes" while silently failing its temporal floor.

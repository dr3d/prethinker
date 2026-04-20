# Process Utterance Pipeline Batch — 2026-04-20

This batch targeted the two hardest frozen `process_utterance()` frontier families:

- `correction`
- `temporal_state`

The work stayed on the canonical interactive path in [src/mcp_server.py](</D:/_PROJECTS/prethinker/src/mcp_server.py>) and was measured against the replayable frontier packs, not one-off console anecdotes.

## What Changed

Two focused interventions landed in the shared server path:

1. Explicit correction normalization
   - detect `actually no, X is with A not B` style holder corrections
   - force the front door to treat them as `assert_fact`, not brittle retract intent
   - reuse the positive parse path, retract the old grounded clause, then assert the new one

2. Explicit step-sequence normalization
   - detect `at step N ... was in ... and later moved to ...`
   - suppress front-door clarification for this exact grounded shape
   - rescue invalid model outputs like `at_step_11(...)` into valid wrappers:
     - `at_step(N, at(entity, place)).`
     - `at_step(N+1, at(entity, destination)).`
   - broaden the detector to accept digit-bearing locations like `Bay 3`

Focused verification:

- [tests/test_mcp_server.py](</D:/_PROJECTS/prethinker/tests/test_mcp_server.py>): `34 passed`
- full safety gate: `142 passed`

## Frontier Results

### Correction Pack

Replay:
- [correction_after_temporal_frontdoor_refine.summary.md](</D:/_PROJECTS/prethinker/tmp/runs/process_utterance_frontier_packs/correction_after_temporal_frontdoor_refine.summary.md>)

Current result:
- `12` cases
- `10 pass`
- `2 fail`

Interpretation:
- the correction family is no longer the dominant red frontier
- most explicit correction turns now commit correctly through the canonical path
- the two remaining failures are narrower parse-shape holdouts, not the old broad retract confusion

### Temporal Pack

Replay:
- [temporal_after_temporal_frontdoor_refine.summary.md](</D:/_PROJECTS/prethinker/tmp/runs/process_utterance_frontier_packs/temporal_after_temporal_frontdoor_refine.summary.md>)

Current result:
- `12` cases
- `8 pass`
- `4 warn`
- `0 fail`

Interpretation:
- the red core of the frozen temporal pack is gone
- all formerly hard step-sequence failures now execute successfully
- the remaining temporal weakness is yellow:
  - relative-time under-capture
  - over-cautious ambiguity handling
  - incomplete handling of `next week ... later moved ...`

## Honest Read

This was a real pipeline lift, not just more hammering:

- correction stayed strong after the first rescue batch
- temporal step-sequence handling materially improved
- the overall scaffold held at `142 passed`

The remaining frontier is now mostly about semantic quality rather than hard breakage:

- relative-time sequencing
- under-capture of `later` in non-step phrasing
- a couple of residual correction parse oddities

## Next Best Move

If the next engineering batch stays in the pipeline rather than the UI, the sharpest target is now:

1. relative-time temporal narration
   - `at 9 AM ... later moved ...`
   - `next week ... later moved ...`

2. the two residual correction holdouts

If product focus returns to the console/UI adapter next, this batch is a good stopping point: the worst red families on the canonical entry path have been materially reduced without destabilizing the scaffold.

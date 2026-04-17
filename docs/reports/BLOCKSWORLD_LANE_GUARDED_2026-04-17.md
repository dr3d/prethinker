# Blocksworld Lane (Pilot)

- Generated UTC: `2026-04-17T16:47:52.934139+00:00`
- Sample size: `20`
- Model: `qwen3.5:9b`

## Symbolic Harness (PDDL Import -> Replay)

- Cases total: `20`
- Solve rate: `1.0` (`20/20`)
- Replay verified count: `20`
- Avg plan length: `1.45`
- Avg planner expansions: `1.6`

## Prethinker Ingestion Pilot

- Cases run: `8`
- Pipeline pass count: `8`
- Avg init predicate hit ratio: `0.75`
- Avg goal predicate hit ratio: `0.666667`
- Avg clarification requests: `0.0`
- Zero-hit cases (init=0 and goal=0): `0`
- Zero-hit gate: `pass` (observed `0` <= threshold `0`)
- Avg init hit gate: `pass` (observed `0.750000` >= threshold `0.450000`)
- Avg goal hit gate: `pass` (observed `0.666667` >= threshold `0.450000`)

| Case | Pipeline | Init Hit | Goal Hit | Clarifications | Parsed Predicates |
|---|---:|---:|---:|---:|---|
| 4 | passed | 0.667 | 0.667 | 0 | clear, handempty, on |
| 8740 | passed | 0.667 | 0.667 | 0 | clear, handempty, on |
| 18196 | passed | 0.667 | 1.000 | 0 | clear, handempty, holding, on |
| 73684 | passed | 1.000 | 0.333 | 0 | handempty, holding, on |
| 82420 | passed | 1.000 | 0.333 | 0 | handempty, holding, on |
| 82440 | passed | 0.667 | 0.667 | 0 | clear, handempty, on |
| 91208 | passed | 0.667 | 1.000 | 0 | clear, handempty, holding, on |
| 91228 | passed | 0.667 | 0.667 | 0 | clear, handempty, on |

### Parsed Predicate Patterns

| Count | Parsed Predicates |
|---:|---|
| 4 | clear, handempty, on |
| 2 | clear, handempty, holding, on |
| 2 | handempty, holding, on |

## Artifacts

- Summary JSON: `D:\_PROJECTS\prethinker\tmp\blocksworld_lane_guarded_recheck_20260417.summary.json`
- Case inventory: `D:\_PROJECTS\prethinker\tmp\blocksworld_lane_2026-04-16.cases.jsonl`
- Generated governor Prolog scaffold: `D:\_PROJECTS\prethinker\tmp\blocksworld_governor_rules_2026-04-16.pl`

## Note

This is the current guarded-lane reference on April 17, 2026. It supersedes the earlier same-day guarded snapshot with lower hit ratios.

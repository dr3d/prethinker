# Story Stress Summary

- Story file: `D:\_PROJECTS\prethinker\tmp\story_inputs\mid.txt`
- Runs: `3`
- Pipeline pass: `1/3`
- Avg coverage: `0.6`
- Avg precision: `0.946667`
- Avg exam pass: `0.566667`
- Avg temporal exam pass: `0.75`
- Best run: `raw_raw_mid_pack_general_strict_temporal_recovery4_20260417_paragraph_temporal_20260417_165906` (`0.359033`)
- Story chars: `6353`
- Expected minimum clauses (density guard): `9`

| Run | Split | Temporal | Pipeline | Coverage | Precision | Exam | Temporal Exam | KB Density | Exam Q Ratio | Final Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `raw_raw_mid_pack_general_strict_temporal_recovery4_20260417_paragraph_temporal_20260417_165906` | `paragraph` | `on` | `failed` | 0.850 | 0.920 | 0.800 | 0.667 | 1.000 | 1.000 | 0.359 |
| `raw_raw_mid_pack_general_strict_temporal_recovery4_20260417_line_temporal_20260417_165906` | `line` | `on` | `failed` | 0.850 | 0.920 | 0.700 | 0.583 | 1.000 | 1.000 | 0.349 |
| `raw_raw_mid_pack_general_strict_temporal_recovery4_20260417_full_temporal_20260417_165906` | `full` | `on` | `passed` | 0.100 | 1.000 | 0.200 | 1.000 | 0.222 | 1.000 | 0.122 |

## Residual Blockers

- Charter rule still rejects on `annual_operating_surplus/1`.
- The September 2021 micro-grant paragraph still collapses into a family of out-of-registry predicates rather than the narrower canonical forms already used elsewhere in the pack.

## Interpretation

- This rerun is more trustworthy than the immediately prior mid rerun because bad rule-shaped exam queries and broken boolean row expectations were filtered out before scoring.
- The lane recovered from the temporary exam artifact, but it did not exceed the earlier `0.3812` recovery peak.
- Mid remains real parser/ontology recovery work rather than a solved strict lane.


# Story Stress Summary

- Story file: `D:\_PROJECTS\prethinker\tmp\story_inputs\upper_mid.txt`
- Runs: `3`
- Pipeline pass: `1/3`
- Avg coverage: `0.85`
- Avg precision: `0.946667`
- Avg exam pass: `1.0`
- Avg temporal exam pass: `1.0`
- Best run: `raw_raw_upper_mid_pack_general_strict_temporal_recovery5_20260417_full_temporal_20260417_170615` (`0.967`)
- Story chars: `6610`
- Expected minimum clauses (density guard): `9`

| Run | Split | Temporal | Pipeline | Coverage | Precision | Exam | Temporal Exam | KB Density | Exam Q Ratio | Final Score |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `raw_raw_upper_mid_pack_general_strict_temporal_recovery5_20260417_full_temporal_20260417_170615` | `full` | `on` | `passed` | 0.850 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.967 |
| `raw_raw_upper_mid_pack_general_strict_temporal_recovery5_20260417_paragraph_temporal_20260417_170615` | `paragraph` | `on` | `failed` | 0.850 | 0.920 | 1.000 | 1.000 | 1.000 | 1.000 | 0.385 |
| `raw_raw_upper_mid_pack_general_strict_temporal_recovery5_20260417_line_temporal_20260417_170615` | `line` | `on` | `failed` | 0.850 | 0.920 | 1.000 | 1.000 | 1.000 | 1.000 | 0.385 |

## Residual Blocker

- Paragraph and line both still reject on the same governance paragraph, where the parser currently drifts into `revenue_transfer/2`, `occupied/2`, and `dependent_child/1` instead of the stricter canonical forms.

## Interpretation

- This is the first honest strict upper-mid rerun that shows a clear full-mode breakout rather than just a modest score lift.
- The pack is still not green overall because only `1/3` split lanes pass, but the remaining failure surface is now narrow and concrete.


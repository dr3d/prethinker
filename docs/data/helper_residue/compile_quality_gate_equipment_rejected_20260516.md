# Domain Bootstrap Compile Batch Summary

Generated: 2026-05-16T13:14:28.262006+00:00

- Lanes: `1`
- Base timeout: `900`
- Effective per-call timeout: `900`
- Fixtures: `1`
- Parsed OK: `1`
- Candidate predicates: `30`
- Compile admitted / skipped: `176 / 23`

| Fixture | Return | Predicates | Admitted | Skipped | Rough | Compile JSON |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `industrial_sensor_clock_correction` | `0` | 30 | 176 | 23 | 0.778 | `C:\prethinker\tmp\helper_residue_equipment_current_compile_20260516\industrial_sensor_clock_correction\domain_bootstrap_file_20260516T125822542750Z_source_qwen-qwen3-6-35b-a3b.json` |

## Compile Quality Gate

- Decision: `hold`
- Passed / held: `0 / 1`
- Minimum rough score: `0.775`
- Maximum risk count: `5`

| Fixture | Decision | Reasons | Rough | Risk | Admitted | Skipped | Skipped Share |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `industrial_sensor_clock_correction` | `hold` | risk_count>5 | 0.778 | 6 | 176 | 23 | 0.1156 |

# Industrial Sensor Clock Correction Progress Journal

Fixture id: `industrial_sensor_clock_correction`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## ISCC-000 - Fixture Admission

Date: 2026-05-10

Evidence lane: `fixture_admission`

Source admitted from: `tmp\prethinker_transfer_fixtures_unpacked\fixtures\industrial_sensor_clock_correction`

Files admitted:

- `source.md` / `story.md`
- `fixture_notes.md`
- `qa.md`
- `qa_questions.jsonl`
- `oracle.jsonl`
- `qa_battery.json`

Benchmark discipline:

- `source.md`/`story.md` is the only cold compile source.
- `oracle.jsonl`, `qa_battery.json`, `qa.md`, and `fixture_notes.md` are scoring/review assets, not compile context.
- No Python source-prose interpretation is allowed.

## ISCC-001 - OpenRouter Cold Acquisition Baseline

Date: 2026-05-10

Evidence lane: `openrouter_cold_acquisition_baseline`

Artifacts:

- Compile: `tmp/transfer_fixtures_20260510/cold_acquisition_compile_lanes6/industrial_sensor_clock_correction/domain_bootstrap_file_20260510T093059718949Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/transfer_fixtures_20260510/cold_acquisition_qa_lanes6/industrial_sensor_clock_correction/domain_bootstrap_qa_20260510T094555343334Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `30 exact / 2 partial / 8 miss` over `40`.

Compile admitted/skipped: `118 / 4`.

Lesson: temporal/source-clock acquisition transfers well enough to start above
75%, with very low skip pressure. Remaining misses should be inspected for
clock-drift joins, per-system correction boundaries, and interval/pause
composition. This is the most direct new proof target for temporal and
constraint propagation.

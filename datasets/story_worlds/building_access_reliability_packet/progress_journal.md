# Building Access Reliability Packet Progress Journal

Fixture id: `building_access_reliability_packet`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## BARP-000 - Fixture Admission

Date: 2026-05-10

Evidence lane: `fixture_admission`

Source admitted from: `tmp\prethinker_transfer_fixtures_unpacked\fixtures\building_access_reliability_packet`

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

## BARP-001 - OpenRouter Cold Acquisition Baseline

Date: 2026-05-10

Evidence lane: `openrouter_cold_acquisition_baseline`

Artifacts:

- Compile: `tmp/transfer_fixtures_20260510/cold_acquisition_compile_lanes6/building_access_reliability_packet/domain_bootstrap_file_20260510T092928950078Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/transfer_fixtures_20260510/cold_acquisition_qa_lanes6/building_access_reliability_packet/domain_bootstrap_qa_20260510T094439533421Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `35 exact / 1 partial / 4 miss` over `40`.

Compile admitted/skipped: `69 / 0`.

Lesson: contradictory evidence and source-reliability scoping transferred very
strongly. The previous concern that unresolved/refusal machinery might be thin
does not show here; this fixture starts at 87.5% exact with zero skipped compile
clauses. Remaining misses are likely narrow source-addressability or conflict
join gaps.

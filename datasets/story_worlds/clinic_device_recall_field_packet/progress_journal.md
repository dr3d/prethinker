# Clinic Device Recall Field Packet Progress Journal

Fixture id: `clinic_device_recall_field_packet`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## CDRF-000 - Fixture Admission

Date: 2026-05-10

Evidence lane: `fixture_admission`

Source admitted from: `tmp\prethinker_transfer_fixtures_unpacked\fixtures\clinic_device_recall_field_packet`

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

## CDRF-001 - OpenRouter Cold Acquisition Baseline

Date: 2026-05-10

Evidence lane: `openrouter_cold_acquisition_baseline`

Artifacts:

- Compile: `tmp/transfer_fixtures_20260510/cold_acquisition_compile_lanes6/clinic_device_recall_field_packet/domain_bootstrap_file_20260510T092957941611Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/transfer_fixtures_20260510/cold_acquisition_qa_lanes6/clinic_device_recall_field_packet/domain_bootstrap_qa_20260510T094441519249Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `31 exact / 0 partial / 9 miss` over `40`.

Compile admitted/skipped: `71 / 19`.

Lesson: the recall/table transfer surface is strong but not saturated. Source
field acquisition and identifier pinning carried most direct rows, while the
remaining pressure is scope/status distinction, range membership, and repair
verification composition. This fixture is a good next probe for whether
source-record fields plus rule/range helpers can retire status/scope guards.

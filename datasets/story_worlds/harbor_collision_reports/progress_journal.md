# Harbor Collision Reports Progress Journal

Fixture id: `harbor_collision_reports`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## HCR-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming_validation_20260508_new6\harbor_collision_reports`

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


## HCR-001 - Evidence Provenance Registry Transfer

Date: 2026-05-08

Evidence lane: `registry_scaffold_transfer`

Mode: direct registry compile using the existing
`tmp/nested_hearing_evidence_registry_v1.json` vocabulary. This tested whether
the evidence-provenance surface from hearing/audit records transfers to a harbor
collision investigation with human statements plus CCTV.

Artifacts:

- Compile:
  `tmp/evidence_provenance_transfer_20260508/harbor_existing_registry/domain_bootstrap_file_20260508T082537254908Z_source_qwen-qwen3-6-35b-a3b.json`
- Targeted QA q005-q006:
  `tmp/evidence_provenance_transfer_20260508/harbor_existing_registry_qa_q005_q006/domain_bootstrap_qa_20260508T082611554779Z_qa_qwen-qwen3-6-35b-a3b.json`
- First-10 QA:
  `tmp/evidence_provenance_transfer_20260508/harbor_existing_registry_qa_first10/domain_bootstrap_qa_20260508T082830498371Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

```text
compile admitted / skipped: 34 / 33
target q005-q006:           2 exact / 0 partial / 0 miss
first-10 direct registry:   6 exact / 2 partial / 2 miss
write proposals:            0
runtime errors:             0
```

Lesson:

The existing evidence-provenance registry transfers surgically: it recovers who
convened the investigation and treats CCTV as an evidence/source item rather
than only counting human witnesses. It is not a full Harbor compile mode. Direct
registry use drops first-10 coverage because vessel ownership, injury detail,
speed claims, and GPS-log status need the ordinary incident/source surface.

Promotion status:

Keep as a row-gated evidence-provenance lens. The first-10 diagnostic upper
bound is strong when baseline handles ordinary incident rows and the registry
handles q005/q006, but the direct registry result is too narrow for global use.

## HCR-002 - Row-Shaped Source And Observation Residual Repair

Date: 2026-05-08

Evidence lane: `row_gated_residual_repair`

Artifacts:

- Compile: `tmp\harbor_rowshape_compile_20260508\domain_bootstrap_file_20260508T142137270004Z_source_qwen-qwen3-6-35b-a3b.json`
- Residual QA q005/q006/q012/q023: `tmp\harbor_rowshape_qa_20260508\domain_bootstrap_qa_20260508T142230004372Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Residual rows: `4 exact / 0 partial / 0 miss`
- Writes/errors: `0` / `0`

Meaning lesson:

Investigation records need row-shaped source lists and observation events. The
successful surface separated four submitted sources, including CCTV, from human
testimony; separated Novak's last-confirmed anchor-ball observation at 14:00
from the unresolved official anchor-ball status; and represented CCTV engine
reversal as an observation with an eight-second offset. This is stronger than a
generic `claimed_by/3` surface because the row itself names the source count,
last-confirmed-at, location-at-time, and CCTV-observation roles.

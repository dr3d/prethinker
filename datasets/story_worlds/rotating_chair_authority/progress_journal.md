# Rotating Chair Authority Progress Journal

Fixture id: `rotating_chair_authority`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## RCA-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming_validation_20260508_new6\rotating_chair_authority`

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

## RCA-001 - Board Recusal Conflict Registry Probe

Date: 2026-05-08

Evidence lane: `registry_scaffold_probe`

Cold first-10 q005 was partial because the KB had Marsh's recusal, GR-4's
financial-interest rule, and the Greenline contract, but did not preserve the
source-stated disclosed-interest link: Marsh's brother-in-law was a Greenline
subcontractor.

Registry:

- `tmp\board_recusal_conflict_registry_v1.json`

Artifacts:

- v1 compile: `tmp\board_recusal_registry_probe_20260508\rotating_chair_authority\domain_bootstrap_file_20260508T092705481984Z_source_qwen-qwen3-6-35b-a3b.json`
- v1 q005 QA: `tmp\board_recusal_registry_probe_20260508\rotating_chair_authority_qa_q005\domain_bootstrap_qa_20260508T092753676414Z_qa_qwen-qwen3-6-35b-a3b.json`
- v2 compile: `tmp\board_recusal_registry_probe_20260508\rotating_chair_authority_v2\domain_bootstrap_file_20260508T093206210848Z_source_qwen-qwen3-6-35b-a3b.json`
- v2 full-40 QA: `tmp\board_recusal_registry_probe_20260508\rotating_chair_authority_v2_qa_full40\domain_bootstrap_qa_20260508T094420067847Z_qa_qwen-qwen3-6-35b-a3b.json`

Results:

- v1 compile: `118` admitted / `1` skipped.
- v1 q005: `1 exact / 0 partial / 0 miss`.
- v1 first-10: `9 exact / 0 partial / 1 miss`, regressing q003 because
  attendance/absence was not in the registry.
- v2 added `meeting_attendance/4`.
- v2 compile: `68` admitted / `6` skipped.
- v2 first-10: `10 exact / 0 partial / 0 miss`.
- v2 full-40: `29 exact / 5 partial / 6 miss`.
- Writes/errors: `0` / `0`.

Meaning lesson:

Governance meeting records need a conflict-disclosure surface distinct from
attendance, vote, and rule text. A recusal reason is not simply "GR-4 applies";
the source must preserve the disclosed relationship, the matter under vote, the
related vendor/contract party, and the rule-triggering interest. Attendance is a
separate backbone surface and must stay in the same profile or ordinary
meeting-roster questions regress.

Promotion status:

Candidate row-gated registry. It is strong for recusal/conflict and first-page
governance rows, but full-40 still misses motion makers, ordinary chair voting
rules, between-meeting emergency authority detail, rescission request status,
parcel price, agenda-add confirmation, and unresolved delegation-validity rows.

## RCA-002 - Motion/Parcel And Unresolved Authority Residual Repair

Date: 2026-05-08

Evidence lane: `row_gated_residual_repair`

Artifacts:

- Board-minutes compile: `tmp\rotating_board_minutes_compile_20260508\domain_bootstrap_file_20260508T142423832026Z_source_qwen-qwen3-6-35b-a3b.json`
- Board-minutes QA q012/q038/q040: `tmp\rotating_board_minutes_qa_20260508\domain_bootstrap_qa_20260508T142516038322Z_qa_qwen-qwen3-6-35b-a3b.json`
- Alderton answer-surface compile: `tmp\rotating_alderton_answer_surface_compile_20260508\domain_bootstrap_file_20260508T143043462370Z_source_qwen-qwen3-6-35b-a3b.json`
- Alderton answer-surface QA q040: `tmp\rotating_alderton_answer_surface_qa_20260508\domain_bootstrap_qa_20260508T143112312501Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Residual rows after row-gated selection: `3 exact / 0 partial / 0 miss`
- Writes/errors: `0` / `0`

Meaning lesson:

Board records need two different residual surfaces. Ordinary agenda rows need
motion maker, seconder, no-motion status, and parcel attributes. Unresolved
authority rows need a fuller answer surface: the question, the stale delegation,
the later act, counsel review, and the explicit no-determination boundary. A
mere `pending_counsel` label was only partial because it hid the legal reason
the question remained open.

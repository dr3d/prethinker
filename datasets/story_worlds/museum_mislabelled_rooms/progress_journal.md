# Museum Mislabelled Rooms Progress Journal

Fixture id: `museum_mislabelled_rooms`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## MMR-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming/museum_mislabelled_rooms.zip`

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

## MMR-001 - First Full-40 Cold Baseline

Date: 2026-05-07

Evidence lane: `cold_unseen`

Score: `31 exact / 4 partial / 5 miss`

Artifacts:

- Compile: `tmp/incoming_10_cold_runs_20260507/museum_mislabelled_rooms`
- QA: `tmp/incoming_10_cold_qa_20260507/museum_mislabelled_rooms`

Boundary: `0` write proposals and `0` runtime load errors. This is a strong cold transfer fixture.

## MMR-002 - Source Authority Audit Candidate

Date: 2026-05-07

Evidence lane: `candidate_compile_mode`

Candidate context: `source_authority_audit_strategy_v1`, focused on public
placards, copied visitor-guide text, digital catalog rows, acquisition records,
expert reports, curator notes, board decisions, and correction status.

Targeted non-exact replay: `4 exact / 2 partial / 3 miss` across the `9`
baseline non-exact rows. The candidate improved conservator date details, Roll
of Honour placard count, original manuscript count, and uncorrected-placard
status rows without targeted regressions.

Full guardrail replay: `31 exact / 2 partial / 7 miss` across all `40` rows,
holding the baseline exact count but shifting several rows. The candidate is
not a global default.

Artifacts:

- Candidate compile: `tmp/incoming_10_repair_museum_source_authority_v1`
- Targeted QA: `tmp/incoming_10_repair_museum_source_authority_v1_qa_nonexact`
- Full guardrail QA: `tmp/incoming_10_repair_museum_source_authority_v1_qa_full`

Decision: useful source-authority candidate mode only. It captures source
record values and correction-state surfaces, but can thin current-display and
governance-authority support.

## MMR-003 - Source Authority Row-Gated Selector

Date: 2026-05-07

Evidence lane: `candidate_mode_selector`

Selector replay:
`tmp/incoming_10_candidate_mode_selectors/museum_guarded_selector_v2.md`

Result: `35 exact / 2 partial / 3 miss`, matching the perfect available upper
bound from baseline plus source-authority candidate modes. The selector chose
the best available mode on all `40/40` rows with `0` selector errors.

Guard lessons:

- Conservator-date questions need the source-recorded value surface, not
  generic discrepancy rows.
- Display-authority questions need controlling governance/source-authority
  surface, not display text rows.

Decision update: source-authority audit earns a row-gated lane. The remaining
misses press on visitor-guide publication year, proposed placard correction
wording, and suspected typo origin.

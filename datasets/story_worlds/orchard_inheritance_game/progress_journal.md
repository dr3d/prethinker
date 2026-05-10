# Orchard Inheritance Game Progress Journal

Fixture id: `orchard_inheritance_game`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## OIG-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming/orchard_inheritance_game.zip`

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

## OIG-001 - First Full-40 Cold Baseline

Date: 2026-05-07

Evidence lane: `cold_unseen`

Score: `25 exact / 5 partial / 10 miss`

Artifacts:

- Compile: `tmp/incoming_10_cold_runs_20260507/orchard_inheritance_game`
- QA: `tmp/incoming_10_cold_qa_20260507/orchard_inheritance_game`

Boundary: `0` write proposals and `0` runtime load errors. This is a mid-pack cold transfer fixture with useful repair targets.

## OIG-002 - Probate/Property Status Candidate

Date: 2026-05-07

Evidence lane: `candidate_compile_mode`

Candidate context: `probate_property_status_strategy_v1`, focused on
separating ownership, possession, control, maintenance, transaction evidence,
court observation, disputed status, and debt/harvest quantities.

Targeted non-exact replay: `12 exact / 0 partial / 3 miss` across the `15`
baseline non-exact rows. The candidate improved original purchase, inherited
tree sets, Greengage gift evidence and maintenance, Blenheim ownership,
uncontested inheritance, provisional control, Medlar possession/court posture,
Greengage possession, and unresolved-status rollup rows.

Full guardrail replay: `31 exact / 1 partial / 8 miss` across all `40` rows,
up from baseline `25 / 5 / 10`. It improved `12` rows and regressed `6` old
working rows, mostly where the candidate emitted stale direct legal-owner
intervals or thinned older pledge/release/solicitor surfaces.

Artifacts:

- Candidate compile: `tmp/incoming_10_repair_orchard_probate_property_v1`
- Targeted QA: `tmp/incoming_10_repair_orchard_probate_property_v1_qa_nonexact`
- Full guardrail QA: `tmp/incoming_10_repair_orchard_probate_property_v1_qa_full`

Decision: strong candidate mode, not a blind global default. This is a clean
row-gating surface: the candidate captures current possession/control/dispute
evidence that baseline missed, while baseline preserves several older legal
chain and advice rows that the candidate thinned.

## OIG-003 - Probate/Property Row-Gated Selector

Date: 2026-05-07

Evidence lane: `candidate_mode_selector`

Selector replay:
`tmp/incoming_10_candidate_mode_selectors/orchard_guarded_selector_v2.md`

Result: `37 exact / 0 partial / 3 miss`, matching the perfect available upper
bound from baseline plus probate/property candidate modes. The selector chose
the best available mode on all `40/40` rows with `0` selector errors.

Guard lessons:

- Provisional-control questions need the holder plus pending estate/claim
  context, not a bare holder row.
- Post-death legal-ownership questions need court/inheritance status surfaces
  rather than stale direct legal-owner intervals.
- Current possession/maintenance questions need physical possessor plus
  gift/dispute evidence.
- Solicitor-advice questions need the advice plus the adverse-possession
  caveat surface.

Decision update: the probate/property context earns a row-gated research lane.
The remaining misses (`q005`, `q038`, `q039`) press on quantity/arithmetic
surfaces: equalization reason, seasonal harvest total, and debt over-recovery.

# Tournament Borrowed Names Progress Journal

Fixture id: `tournament_borrowed_names`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## TBN-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming/tournament_borrowed_names.zip`

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

## TBN-001 - First Full-40 Cold Baseline

Date: 2026-05-07

Evidence lane: `cold_unseen`

Score: `30 exact / 3 partial / 7 miss`

Artifacts:

- Compile: `tmp/incoming_10_cold_runs_20260507/tournament_borrowed_names`
- QA: `tmp/incoming_10_cold_qa_20260507/tournament_borrowed_names`

Boundary: `0` write proposals and `0` runtime load errors. This is a strong cold transfer fixture.

## TBN-002 - Competition Role/Alias Candidate

Date: 2026-05-07

Evidence lane: `candidate_compile_mode`

Candidate context: `competition_role_alias_strategy_v1`, focused on
time-scoped banner aliases, dual roles, corrected ranks, protests/rulings,
safety non-findings, final certification, and historical winner attribution.

Targeted non-exact replay: `5 exact / 1 partial / 4 miss` across the `10`
baseline non-exact rows. The candidate improved Kester's Owl-to-Raven change,
Darke's eighth arrow, Kester's 2020 Owl win, safety-incident non-finding, and
dual-role listing. It regressed the hold-call rationale row.

Full guardrail replay: `28 exact / 2 partial / 10 miss` across all `40` rows,
down from baseline `30 / 3 / 7`. The candidate is not a global default.

Artifacts:

- Candidate compile: `tmp/incoming_10_repair_tournament_role_alias_v1`
- Targeted QA: `tmp/incoming_10_repair_tournament_role_alias_v1_qa_nonexact`
- Full guardrail QA: `tmp/incoming_10_repair_tournament_role_alias_v1_qa_full`

Decision: useful role/alias candidate mode only. It captures banner succession,
dual-role, and explicit non-incident surfaces, but thins some baseline score,
match, and testimony support.

## TBN-003 - Competition Role/Alias Row-Gated Selector

Date: 2026-05-07

Evidence lane: `candidate_mode_selector`

Selector replay:
`tmp/incoming_10_candidate_mode_selectors/tournament_guarded_selector_v2.md`

Result: `35 exact / 2 partial / 3 miss`, matching the perfect available upper
bound from baseline plus competition role/alias candidate modes. The selector
chose the best available mode on all `40/40` rows with `0` selector errors.

Guard lesson: banner-change rationale questions need banner
succession/creation evidence, not broad protest or score rows. More broadly,
competition records need separate surfaces for alias holder, administrative
role, score correction, protest/ruling, and explicit no-incident findings.

Decision update: competition role/alias earns a row-gated lane. The remaining
misses press on final certification, corrected rank-order join, and
conflict-of-interest objection surfaces.

## TBN-004 - Competition Administrative Certification Review Candidate

Date: 2026-05-07

Evidence lane: `candidate_compile_mode` plus `candidate_mode_selector`

Harness/context change: expanded `competition_role_alias_strategy_v1` with
competition certification, conflict-objection, and protest-count guidance. The
first admin-cert candidate proved the instruction alone was insufficient: its
profile still omitted the score-certification and no-conflict-objection
predicates. A profile review/retry pass then expanded the profile from `12` to
`27` predicates and admitted the needed administrative surfaces.

Candidate compile:
`tmp/incoming_10_repair_tournament_admin_cert_review_v1/domain_bootstrap_file_20260507T225508127365Z_source_qwen-qwen3-6-35b-a3b.json`

Compile result: `147` admitted facts, `3` skipped facts/rules, `0` runtime load
errors. New useful surfaces included `score_certified_by/3`,
`no_conflict_of_interest_objections/1`, `witness_statement/4`,
`protest_filed/4`, `official_role/4`, `dual_status/4`, `qualifying_rank/3`, and
`score_correction/5`.

Targeted weak-row replay:
`tmp/incoming_10_repair_tournament_admin_cert_review_v1_qa_targeted/domain_bootstrap_qa_20260507T225642036429Z_qa_qwen-qwen3-6-35b-a3b.json`

Targeted result: `2 exact / 2 partial / 1 miss` over the five weak rows. The
candidate recovered final-score certification by Orla Venn and the explicit
absence of conflict-of-interest objections.

Full candidate replay:
`tmp/incoming_10_repair_tournament_admin_cert_review_v1_qa_full/domain_bootstrap_qa_20260507T230545576388Z_qa_qwen-qwen3-6-35b-a3b.json`

Candidate score: `33 exact / 4 partial / 3 miss`. It is not a global default.

Three-mode selector replay:
`tmp/incoming_10_candidate_mode_selectors/tournament_admin_guarded_selector_v2.md`

Result: `37 exact / 3 partial / 0 miss`, matching the perfect available upper
bound across baseline, role/alias candidate, and admin-cert review candidate
modes. The selector chose the best available mode on all `40/40` rows with `0`
selector errors.

Guard additions: substitute-scorer identity protects compact service-role rows
from certification/result volume; hold-call rationale protects event-condition
timing from broader witness/incident volume; corrected-rank-order prefers
qualifying-rank plus score-correction support over raw total volume.

Lesson: competition records have a separate administrative layer beyond scores,
aliases, and protests. Score recorder/certifier, explicit non-objection notes,
and protest filing counts are durable surfaces. Profile review/retry is useful
when the initial profile understands the domain broadly but misses an
administrative act that is stated plainly in the source.

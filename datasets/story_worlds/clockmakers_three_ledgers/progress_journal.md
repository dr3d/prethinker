# Clockmakers Three Ledgers Progress Journal

Fixture id: `clockmakers_three_ledgers`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## CTL-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming/clockmakers_three_ledgers.zip`

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

## CTL-001 - First Full-40 Cold Baseline

Date: 2026-05-07

Evidence lane: `cold_unseen`

Score: `35 exact / 1 partial / 4 miss`

Artifacts:

- Compile: `tmp/incoming_10_cold_runs_20260507/clockmakers_three_ledgers`
- QA: `tmp/incoming_10_cold_qa_20260507/clockmakers_three_ledgers`

Boundary: `0` write proposals and `0` runtime load errors. This is a strong cold transfer fixture.

## CTL-002 - Ledger Correction Provenance Candidate

Date: 2026-05-07

Evidence lane: `candidate_compile_mode`

Candidate context: ledger correction/source-authority emphasis, focused on
accounts/client/parts ledgers, correction hands, document examiner opinion,
disputed corrections, and stale/current item states.

Targeted non-exact replay: `2 exact / 1 partial / 2 miss` across the `5`
baseline non-exact rows. The candidate improved Aldric's death date and the
Whitford bracket clock pickup date.

Full guardrail replay: `36 exact / 1 partial / 3 miss` across all `40` rows,
up from baseline `35 / 1 / 4`.

Artifacts:

- Candidate compile: `tmp/incoming_10_repair_clockmaker_ledger_correction_v1`
- Targeted QA: `tmp/incoming_10_repair_clockmaker_ledger_correction_v1_qa_nonexact`
- Full guardrail QA: `tmp/incoming_10_repair_clockmaker_ledger_correction_v1_qa_full`

Decision: small useful candidate mode. It improves ledger date/status surfaces
but still misses account-ledger location, ink-count, and Ansonia intake actor
rows.

## CTL-003 - Ledger Correction Row-Gated Selector

Date: 2026-05-07

Evidence lane: `candidate_mode_selector`

Selector replay:
`tmp/incoming_10_candidate_mode_selectors/clockmaker_guarded_selector_v2.md`

Result: `37 exact / 1 partial / 2 miss`, matching the perfect available upper
bound from baseline plus ledger-correction candidate modes. The selector chose
the best available mode on all `40/40` rows with `0` selector errors.

Guard lesson: intake-actor questions need handoff/location event surfaces, not
ledger-entry rows alone.

Decision update: ledger correction provenance earns a small row-gated lane.
The remaining misses press on physical ledger location and specific Ansonia
intake actor provenance.

## CTL-004 - Ledger/Object Provenance Registry Candidate

Date: 2026-05-07

Evidence lane: `registry_scaffold_candidate` plus `candidate_mode_selector`

Harness/context change: tested a tiny temporary ledger/object provenance
registry for estate, workshop, inventory, and ledger records. The scaffold
supplied predicate vocabulary for ledger physical location, correction ink/hand
status, item intake actor, item work, item status/location, client instruction,
and examiner opinion. It supplied no fixture facts.

Registry scaffold:
`tmp/clockmaker_ledger_object_provenance_registry_v1.json`

Candidate compile:
`tmp/incoming_10_repair_clockmaker_object_provenance_registry_v1/domain_bootstrap_file_20260507T234546656915Z_source_qwen-qwen3-6-35b-a3b.json`

Compile result: `86` admitted facts, `12` skipped facts/rules, `0` runtime load
errors. Useful new surfaces included `ledger_found_location/2`,
`item_received_from/4`, `correction_ink/3`, `correction_hand_status/3`,
`item_current_status/4`, and `client_instruction/4`.

Targeted weak-row replay:
`tmp/incoming_10_repair_clockmaker_object_provenance_registry_v1_qa_targeted/domain_bootstrap_qa_20260507T234636249028Z_qa_qwen-qwen3-6-35b-a3b.json`

Targeted result: `2 exact / 1 partial / 0 miss` over q003, q004, and q028. The
candidate recovered the accounts ledger location and the Ansonia intake actor;
the ink-count row remained partial.

Full candidate replay:
`tmp/incoming_10_repair_clockmaker_object_provenance_registry_v1_qa_full/domain_bootstrap_qa_20260507T235621667229Z_qa_qwen-qwen3-6-35b-a3b.json`

Candidate score: `16 exact / 5 partial / 19 miss`. This is a surgical
provenance mode, not a replacement compile.

Three-mode selector replay:
`tmp/incoming_10_candidate_mode_selectors/clockmaker_object_registry_guarded_selector_v2.md`

Result: `39 exact / 1 partial / 0 miss`, matching the perfect available upper
bound across baseline, ledger-correction candidate, and object-provenance
registry modes. The selector chose the best available mode on all `40/40` rows
with `0` selector errors.

Guard additions: client-ledger pickup rows prefer asset state/location surfaces
over broad item provenance; Ansonia intake actor rows prefer explicit
item-received-from provenance; correction-authorship rows prefer
handwriting/expert attribution over correction-status volume.

Lesson: physical source/document location and object intake actor are not the
same surface as ledger entry content. Estate/workshop ledgers need explicit
document-location and item-intake provenance vocabulary when questions ask
where a record was found or who brought an object into the shop. The registry
lane is valuable only under row gating because its narrow vocabulary regresses
most broad status and financial rows.

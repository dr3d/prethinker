# Amended Lease Register Progress Journal

Fixture id: `amended_lease_register`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## ALR-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming_validation_20260508_new6\amended_lease_register`

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

## ALR-001 - Lease Financial Correction Registry Probe

Date: 2026-05-08

Evidence lane: `registry_scaffold_probe`

Cold first-10 q006 missed the calculation behind Kettner's `$600` refund. The
baseline compile preserved a long correction reason atom, but not a structured
refund calculation: overcharge period, day count, daily differential, and refund
amount.

Registry:

- `tmp\lease_correction_financial_registry_v1.json`

Artifacts:

- compile: `tmp\lease_financial_registry_probe_20260508\amended_lease_register\domain_bootstrap_file_20260508T094819710783Z_source_qwen-qwen3-6-35b-a3b.json`
- q006 QA: `tmp\lease_financial_registry_probe_20260508\amended_lease_register_qa_q006\domain_bootstrap_qa_20260508T094904495433Z_qa_qwen-qwen3-6-35b-a3b.json`
- first-10 QA: `tmp\lease_financial_registry_probe_20260508\amended_lease_register_qa_first10\domain_bootstrap_qa_20260508T095126778035Z_qa_qwen-qwen3-6-35b-a3b.json`

Results:

- Compile: `65` admitted / `5` skipped.
- q006 targeted: `1 exact / 0 partial / 0 miss`.
- first-10 direct registry: `8 exact / 0 partial / 2 miss`.
- Regressed q009/q010 because the narrow financial registry did not preserve
  Courtyard B supersession reason and Pryce authorization rows.
- Writes/errors: `0` / `0`.

Meaning lesson:

Financial corrections need a structured calculation surface distinct from long
event reasons. The useful slots are corrected effective date, notice
requirement, overcharge period, day count, daily differential, refund amount,
and current refund obligation. This is a surgical row-gated mode: it should not
replace the broader lease/amendment surface that carries courtyard,
supersession, and authorization facts.

## ALR-002 - Original-Vs-Current Lease State Residual Repair

Date: 2026-05-08

Evidence lane: `row_gated_residual_repair`

Artifacts:

- Compile: `tmp\amended_lease_state_compile_20260508\domain_bootstrap_file_20260508T141110213629Z_source_qwen-qwen3-6-35b-a3b.json`
- Residual QA q025/q034/q035/q036: `tmp\amended_lease_state_qa_20260508\domain_bootstrap_qa_20260508T141214896141Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Residual rows: `4 exact / 0 partial / 0 miss`
- Writes/errors: `0` / `0`

Meaning lesson:

Lease registers need a state surface that keeps original terms, current terms,
amendment corrections, and pre-amendment values distinct. The rows that mattered
were original expiry, pre-amendment rent, original parking allocation, and early
termination effective date. This is not a new global lease lens yet; it is a
row-gated state repair surface that should transfer to another amended-register
fixture before promotion.

## ALR-003 - Bounded Preservation Candidate Replay

Date: 2026-05-19

Evidence lane: `multi_draw_preservation_candidate`

The profile-delivery stability audit found that source-authority and
source-claim carriers were offered but intermittently undelivered across
multiple compile draws. A bounded preservation candidate kept one anchor
compile's source-record ledger and imported only direct facts matching volatile
carrier signatures that had been delivered in sibling draws.

Artifacts:

- Stability audit: `tmp\source_authority_profile_delivery_stability_20260519.json`
- Preservation candidate: `tmp\source_authority_preservation_candidate_20260519.json`
- QA replay: `tmp\source_authority_preservation_candidate_qa_20260519\domain_bootstrap_qa_20260519T071656043525Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Selected signatures: `source_attributed_claim/4`, `source_authority/3`
- Added direct facts: `9`
- QA: `33 exact / 3 partial / 4 miss`
- Failure surface counts: `3 compile_surface_gap`, `3 query_surface_gap`,
  `1 hybrid_join_gap`
- Writes/errors: `0` / `0`

Meaning lesson:

Bounded multi-draw preservation can recover volatile direct carriers without
unioning an entire compile set, but this replay did not by itself lift QA. The
remaining misses are mostly current-state temporal joins, correction reasons,
and pre-amendment state resolution. This points to row-level preservation as a
promising substrate stabilizer, not a complete query-layer repair.

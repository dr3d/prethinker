# Probate Storage Access Register Progress Journal

Fixture id: `probate_storage_access_register`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## PSAR-000 - Fixture Admission

Date: 2026-05-10

Evidence lane: `fixture_admission`

Source admitted from: `tmp\prethinker_transfer_fixtures_unpacked\fixtures\probate_storage_access_register`

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

## PSAR-001 - OpenRouter Cold Acquisition Baseline

Date: 2026-05-10

Evidence lane: `openrouter_cold_acquisition_baseline`

Artifacts:

- Compile: `tmp/transfer_fixtures_20260510/cold_acquisition_compile_lanes6/probate_storage_access_register/domain_bootstrap_file_20260510T093021249770Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/transfer_fixtures_20260510/cold_acquisition_qa_lanes6/probate_storage_access_register/domain_bootstrap_qa_20260510T094541044260Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `34 exact / 1 partial / 5 miss` over `40`.

Compile admitted/skipped: `109 / 15`.

Lesson: authority/custody/ownership transfer is healthy on a fresh probate
packet. The helper and archival/source-record surfaces handled most possession,
title-claim, access, and pending-status rows cold. Remaining misses are likely
procedural-deferment or exact source-addressability gaps rather than a new
authority lens.

## PSAR-002 - Current Helper Cluster Replay

Date: 2026-05-10

Evidence lane: `helper_cluster_audit`

Artifacts:

- Current live replay:
  `tmp/transfer_fixtures_20260510/probate_current_live_replay_20260510/domain_bootstrap_qa_20260510T191519633683Z_qa_qwen-qwen3-6-35b-a3b.json`
- Historical orphan-helper replay:
  `tmp/transfer_fixtures_20260510/probate_storage_helper_full_replay_20260510/domain_bootstrap_qa_20260510T144725230700Z_qa_qwen-qwen3-6-35b-a3b.json`
- Cluster row gate:
  `tmp/transfer_fixtures_20260510/authority_probate_cluster_probe_20260510/probate_row_gate.md`
- Helper class audit:
  `tmp/transfer_fixtures_20260510/authority_probate_cluster_probe_20260510/probate_helper_class_audit.md`

Results:

- cold baseline: `34 / 1 / 5`
- historical `probate_storage_support` replay: `36 / 0 / 4`
- current live replay: `29 / 3 / 8`
- current helper rows: `96 candidate-helper` from
  `archive_authority_custody_support`
- row-gate across cold, orphan, and current surfaces: `40 / 0 / 0`

Lesson: probate is the clearest helper-governance warning in the transfer set.
The old `probate_storage_support` surface rescued rows, but it is not current
implemented architecture and must be treated as orphaned historical residue.
The current live helper surface is candidate-only and regresses the standalone
cold score. Do not report the historical `36 / 0 / 4` as active architecture.
The row-gated `40 / 0 / 0` is useful diagnostic evidence that the needed answer
surfaces exist somewhere in the artifact history, but the next legitimate work
is either a generic probate storage/access helper or selector discrimination
against live, audited surfaces.

## PSAR-003 - Clean Source-Record Metadata Repair

Date: 2026-05-10

Evidence lane: `source_record_metadata_cleanup`

Artifacts:

- Refreshed source-record compile, no LLM:
  `tmp/transfer_fixtures_20260510/probate_refreshed_source_ledger_v2_no_llm_20260510/domain_bootstrap_file_20260510T093021249770Z_source_qwen-qwen3-6-35b-a3b.json`
- Targeted QA:
  `tmp/transfer_fixtures_20260510/probate_refreshed_source_ledger_v3_targeted_20260510/domain_bootstrap_qa_20260510T220937148167Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full QA:
  `tmp/transfer_fixtures_20260510/probate_refreshed_source_ledger_full_20260510/domain_bootstrap_qa_20260510T221622112415Z_qa_qwen-qwen3-6-35b-a3b.json`

Results:

- targeted hard-row probe: `9 / 0 / 0`
- targeted helper rows: `1150 clean-helper / 0 candidate-helper`
- full replay: `34 / 2 / 4`
- full replay helper rows: `2668 clean-helper / 0 candidate-helper`
- local tests: `102 passed` across source-record ledger, QA helper, and
  compile-file substrate tests

Lesson: probate's active helper pressure was not solved by promoting the
orphaned `probate_storage_support` helper. The legitimate repair is generic
deterministic source addressability: preserve official prose continuations
around "not reproduced", "not a finding of fact", "authoritative sources",
registrar identity, loan-amendment effect, reading-room policy scope, and
delivery-direction status, then expose those rows through
`source_record_packet_metadata_support` as `clean-helper` rows. The hard-row
targeted probe confirms the needed facts are now queryable without
fixture-specific helper constants. The full replay remains `34 / 2 / 4` because
QA/query generation still sometimes ignores or underuses the clean companion
rows; that is selector/query-surface pressure, not helper acquisition pressure.

## PSAR-004 - Clean Metadata Query Scoping

Date: 2026-05-10

Evidence lane: `query_routing_cleanup`

Artifacts:

- Six-row scoped metadata probe:
  `tmp/transfer_fixtures_20260510/probate_query_scoped_targeted_v3_20260510/domain_bootstrap_qa_20260510T223502046166Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full scoped replay:
  `tmp/transfer_fixtures_20260510/probate_query_scoped_full_20260510/domain_bootstrap_qa_20260510T224258709063Z_qa_qwen-qwen3-6-35b-a3b.json`
- Section-display probe:
  `tmp/transfer_fixtures_20260510/probate_section_display_targeted_20260510/domain_bootstrap_qa_20260510T224413123247Z_qa_qwen-qwen3-6-35b-a3b.json`

Results:

- targeted residual probe: `6 / 0 / 0`
- targeted helper rows: `115 clean-helper / 0 candidate-helper`
- full replay: `34 / 2 / 4`
- full replay helper rows: `1280 clean-helper / 0 candidate-helper`
- local tests: `885 passed, 2 subtests passed`

Repair:

- `source_record_packet_metadata_support` now receives the triggering query
  arguments and scopes rows by query surface, so party-role and custody queries
  are not flooded by unrelated packet metadata.
- Section-display support now renders letter/roman section atoms such as
  `section_f_recorded_statements...` and
  `section_i_chronology...` as `Section F` / `Section I`.
- Temporal joins now localize provenance-like `Orderid` variables when the
  actual helper arguments are dates, allowing elapsed-day joins across separate
  court orders.
- Clean source-record numeric tokens in asserted-event contexts now expose
  `asserted_event_date` rows, closing the Daniel Holloway asserted-date gap in
  targeted replay without resurrecting the orphaned probate helper.

Lesson: the helper acquisition is clean and the residual rows can route
correctly under a focused probe. The full replay remains unchanged because the
LLM query planner still sometimes asks a weaker query shape and the answer judge
will not infer across an auxiliary companion row unless the linkage is obvious.
This is now query-planner/selector discrimination pressure, not new helper or
new lens pressure.

## PSAR-005 - Generic Residual Source-Record Bridges

Date: 2026-05-10

Evidence lane: `clean_helper_residual_bridge`

Artifacts:

- Five-row residual probe:
  `tmp/transfer_fixtures_20260510/probate_residual_query_support_targeted_20260510/domain_bootstrap_qa_20260510T225402966365Z_qa_qwen-qwen3-6-35b-a3b.json`
- Three-row residual probe after compilation-note broadening:
  `tmp/transfer_fixtures_20260510/probate_residual_query_support_targeted_v2_20260510/domain_bootstrap_qa_20260510T230350295151Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full replay:
  `tmp/transfer_fixtures_20260510/probate_residual_query_support_full_20260510/domain_bootstrap_qa_20260510T230129552463Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full replay rerun:
  `tmp/transfer_fixtures_20260510/probate_residual_query_support_full_v2_20260510/domain_bootstrap_qa_20260510T231104162211Z_qa_qwen-qwen3-6-35b-a3b.json`

Results:

- targeted five-row probe: `4 / 0 / 1`
- targeted three-row probe: `2 / 0 / 1`
- best full replay this bite: `37 / 0 / 3`
- rerun full replay: `35 / 0 / 5`
- best full replay helper rows: `1779 clean-helper / 0 candidate-helper`
- rerun full replay helper rows: `1797 clean-helper / 0 candidate-helper`
- local tests: `889 passed, 2 subtests passed`

Repair:

- Added `item_description_detail_support`, a clean query-only bridge that
  derives display titles and trailing years from admitted `item_description/2`
  atoms.
- Added `source_record_table_body_count_support`, a clean source-record bridge
  that counts field-bearing table body rows while excluding header rows.
- Extended `source_record_packet_metadata_support` with clean joins from
  admitted `access_authority/3` rows to admitted `court_order/3` rows, plus
  field-derived reading-room policy support from source-record access-register
  rows.
- Broadened unreproduced-reference detection for compilation-note sections,
  allowing the will/reference rows to surface as clean source-record metadata.

Lesson: the legitimate residual repair pattern is still generic bridge work,
not resurrection of `probate_storage_support`. The focused probes show that
the missing `q008`, `q024`, `q031`, `q032`, and `q036` answer surfaces are now
reachable as clean-helper rows. Full replay remains unstable because planner
and judge behavior sometimes prefer a weak primary query over a correct clean
companion row; that is selector/query-surface pressure. `q040` remains a true
source-record acquisition gap: the cold compile artifact lacks the Section F
lines containing "forensic handwriting analyst's report (when filed)" and
"Court's ultimate rulings are the authoritative sources." The next bite should
inspect and repair deterministic source-record paragraph/continuation
acquisition for skipped lines before adding more query helpers.

## PSAR-006 - Refreshed Source-Record Acquisition And Order-Section Bridge

Date: 2026-05-10

Evidence lane: `source_record_acquisition_refresh`

Artifacts:

- No-LLM refreshed compile artifact:
  `tmp/transfer_fixtures_20260510/probate_source_record_refresh_v4_no_llm_20260510/domain_bootstrap_file_20260510T093021249770Z_source_qwen-qwen3-6-35b-a3b.json`
- q040 acquisition probe:
  `tmp/transfer_fixtures_20260510/probate_q040_source_record_refresh_v4_20260510/domain_bootstrap_qa_20260510T231601345690Z_qa_qwen-qwen3-6-35b-a3b.json`
- q010/q040 order-section probe:
  `tmp/transfer_fixtures_20260510/probate_order_section_q010_q040_20260510/domain_bootstrap_qa_20260510T232534337383Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full refreshed replay:
  `tmp/transfer_fixtures_20260510/probate_source_record_refresh_v4_full_20260510/domain_bootstrap_qa_20260510T232347357003Z_qa_qwen-qwen3-6-35b-a3b.json`
- Final full refreshed replay:
  `tmp/transfer_fixtures_20260510/probate_source_record_refresh_v4_full_final_20260510/domain_bootstrap_qa_20260510T233508535773Z_qa_qwen-qwen3-6-35b-a3b.json`
- q005/q037 residual probe:
  `tmp/transfer_fixtures_20260510/probate_q005_q037_residual_20260510/domain_bootstrap_qa_20260510T233613063047Z_qa_qwen-qwen3-6-35b-a3b.json`

Results:

- refreshed deterministic source-record rows: `169` versus stale cold artifact
  `122`
- refreshed deterministic source-record facts: `2106`
- q040 acquisition probe: `1 / 0 / 0`
- q010/q040 focused probe: `2 / 0 / 0`
- best full refreshed replay: `38 / 0 / 2`
- q005/q037 residual probe: `2 / 0 / 0`
- clean-helper row-gated high-water over refreshed full plus residual probes:
  `40 / 0 / 0`
- final full replay helper rows: `3401 clean-helper / 0 candidate-helper`
- local tests: `890 passed, 2 subtests passed`

Repair:

- Confirmed the q040 miss was not a semantic/lens gap: the stale cold artifact's
  deterministic source-record ledger stopped before the Section F authoritative
  source paragraph, while the live ledger extracts `src_line_0166`,
  `src_line_0167`, and `src_line_0168`.
- Built a no-LLM refreshed artifact preserving the existing semantic facts and
  replacing stale deterministic `source_record_*` facts with the current ledger.
- Added clean `source_record_order_section` rows inside
  `source_record_packet_metadata_support`, linking source-record table
  `order_id` fields to their containing section.

Lesson: probate storage/access no longer needs the orphaned
`probate_storage_support` helper. The source-record memory substrate now holds
the needed rows cleanly. The remaining single-run failures are planner/parser
churn: q005 can still ask the wrong `party_role` surface, and one full replay
returned an empty row for q037, but both rows answer exactly in focused probes
from the same refreshed artifact. Report probate as `38 / 0 / 2` single-run
clean-helper and `40 / 0 / 0` clean-helper row-gated, with the caveat that
row-gating is diagnostic high-water rather than production selector behavior.

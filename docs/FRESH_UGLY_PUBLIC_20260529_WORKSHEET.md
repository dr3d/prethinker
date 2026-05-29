# Fresh Ugly Public 20260529 Worksheet

## Purpose

Track the fresh public-transfer batch `fresh_ugly_public_20260529_01` as a post-20260528 thermometer. This worksheet is lab history: mechanism-shaped observations, run conditions, and residue decisions. It is not a public scorecard.

## Batch Intake

- Dataset: `datasets/real_world_transfer/fresh_ugly_public_20260529_01`
- Fixtures: `8`
- Questions: `200`
- Validation artifact: `C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_validation.md`
- Validation result: pass, `8/8` fixtures, `25` oracle rows each, `0` issues, `36` warnings.
- Warning read: mostly reference terms absent from direct source text or present only in notes/metadata. Not a blocker for compile/QA, but worth retaining as fixture-authorship noise.

Fixtures:

- `court_order_ugly_003`
- `fda_warning_ugly_007`
- `labor_board_ugly_003`
- `osha_incident_ugly_007`
- `procurement_contract_ugly_003`
- `puc_order_ugly_003`
- `sec_material_event_ugly_007`
- `state_ag_settlement_ugly_003`

## R1 Compile

Command:

```powershell
python scripts\run_domain_bootstrap_file_batch.py --dataset-root datasets\real_world_transfer\fresh_ugly_public_20260529_01 --out-root C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\compile_r1 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --timeout 1200 --lanes 6 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-entity-ledger --archival-identifier-ledger --source-record-ledger --source-record-ledger-facts --intake-registry-context --review-profile --profile-review-retry --quality-gate --quality-retry-on-hold --quality-retry-max-attempts 1 --out-json C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\compile_r1_summary.json --out-md C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\compile_r1_summary.md
```

Result:

- Parsed OK: `8/8`
- Candidate predicates: `154`
- Effective admitted/skipped: `846 / 116`
- Diagnostic rejected flat-pass skips: `0`
- Old quality gate: `0 passed / 8 held`
- Tiered gate: blocking tier clean, `0 blocking / 8 diagnostic / 0 advisory`
- Rough scores: all at or above `0.85`

Read:

- The old gate is too noisy for current public-transfer work; the tiered gate is the more useful signal.
- All holds are diagnostic compile-surface warnings, not runtime or blocking failures.

## R1 QA

Command:

```powershell
python scripts\run_domain_bootstrap_qa_batch.py --dataset-root datasets\real_world_transfer\fresh_ugly_public_20260529_01 --compile-root C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\compile_r1 --out-root C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r1 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --timeout-scale 6 --no-cache --out-json C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r1_summary.json --out-md C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r1_summary.md
```

Result:

- QA: `198 / 1 / 1` over `200`
- Exact rate: `99.0%`
- Hygiene: `0` compatibility rows, `0` runtime load errors, `0` write proposals

Per fixture:

- `court_order_ugly_003`: `25 / 0 / 0`
- `fda_warning_ugly_007`: `24 / 1 / 0`
- `labor_board_ugly_003`: `25 / 0 / 0`
- `osha_incident_ugly_007`: `25 / 0 / 0`
- `procurement_contract_ugly_003`: `25 / 0 / 0`
- `puc_order_ugly_003`: `24 / 0 / 1`
- `sec_material_event_ugly_007`: `25 / 0 / 0`
- `state_ag_settlement_ugly_003`: `25 / 0 / 0`

## R1 Residue

Adjudication artifact: `C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r1_residue_adjudication.md`

- Residue rows: `2`
- Classifications: `repairable_compile_gap:2`
- Surfaces: `compile_surface_gap:2`

Rows:

- `fda_warning_ugly_007 q013`: chronological ordering row. Source records contained the intermediate inspection and meeting dates, but the display-date inventory did not preserve ordinary English `Month day, year` and `Month year` display dates for structured chronology.
- `puc_order_ugly_003 q005`: document-control-number row. Source records contained `DW#340357.`, but structured query intent drifted toward docket number and the identifier companion did not activate from structured intent or harvest admitted surface mentions.

Read:

- Both residues were initially labeled compile-surface gaps, but the more precise diagnosis is query-surface delivery over admitted source records.
- This is the exact failure-surface distinction we want the audit trail to make: fact present in admitted source ledger, answer not surfaced.

## R2 Target Mechanisms

Code changes:

- Identifier support now accepts structured query intents and can harvest admitted `source_record_surface_mention/3` rows as identifier displays.
- Identifier reference checking recognizes `source_record_identifier_set_support` when the literal requested value is present.
- Display-date inventory now recognizes ordinary English display dates:
  - `Month day, year`
  - `day Month year`
  - `Month year`
  - language-neutral `day of MonthX year`
- Structured chronology inventories are date-ordered. Raw inventory questions remain source-record inventories.
- Date-sequence support now checks date-display sequence rather than broad event text, preventing duplicated context from laundering an incorrect order.

Target replays:

- `puc_order_ugly_003 q005`: `1 / 0 / 0`, hygiene `0/0/0`
- `fda_warning_ugly_007 q013`: `1 / 0 / 0`, hygiene `0/0/0`

## R2 Full Replay

Command:

```powershell
python scripts\run_domain_bootstrap_qa_batch.py --dataset-root datasets\real_world_transfer\fresh_ugly_public_20260529_01 --compile-root C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\compile_r1 --out-root C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r2_full --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --timeout-scale 6 --no-cache --out-json C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r2_full_summary.json --out-md C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r2_full_summary.md
```

Result:

- QA: `197 / 1 / 2` over `200`
- Exact rate: `98.5%`
- Hygiene: `0` compatibility rows, `0` runtime load errors, `0` write proposals

R2 residue:

- `court_order_ugly_003 q006`: miss, stable on target replay before repair. The source row contained the companion case identifier and the same-day disposition, but no query-only support surface named that relation.
- `procurement_contract_ugly_003 q009`: miss in R2 full, exact on R3 target replay. Treat as hosted query-plan/judge variance unless it repeats.
- `procurement_contract_ugly_003 q013`: partial, stable on target replay before repair. The source row contained `December 3` without a year; the chronology inventory did not preserve omitted-year `Month day` display dates.

Read:

- Full replay prevented a false `200/0/0` claim from target slices.
- The R2 churn is useful: the first two repairs transferred, but the full run surfaced one stable court/source-row support gap, one stable omitted-year chronology gap, and one unstable procurement row.

## R3/R4 Target Mechanisms

Additional code changes:

- Added query-only same-day companion-case disposition support over admitted source-record displays and surface mentions.
- Added display-date support for omitted-year `Month day` mentions. Source rows use the runtime's dominant year for sorting when available, but preserve the visible source display.

Target replays:

- `court_order_ugly_003 q006`:
  - R3 before same-day companion-case repair: `0 / 0 / 1`, hygiene `0/0/0`
  - R4 after repair: `1 / 0 / 0`, hygiene `0/0/0`
- `procurement_contract_ugly_003 q009`:
  - R3 target replay: exact, hygiene `0/0/0`
  - Read: variance row, not a stable code repair target yet.
- `procurement_contract_ugly_003 q013`:
  - R3 before omitted-year date repair: partial
  - R4 after repair: `1 / 0 / 0`, hygiene `0/0/0`

Verification:

```powershell
python -m pytest -q
python scripts\audit_active_instrument_leakage.py
git diff --check
```

Result:

- `2019 passed, 2 subtests passed`
- Leakage audit: pass, `0` forbidden hits, `0` warning hits
- Diff check: clean except expected CRLF notices

## Current Claim Boundary

Measured full-corpus claims:

- R1: `198 / 1 / 1 = 99.0%`
- R2 full: `197 / 1 / 2 = 98.5%`
- R4 full: `198 / 1 / 1 = 99.0%`

Target evidence after R4 indicates all stable named residue rows replay exact. The R4 full replay is the current measured corpus claim; it is not a clean `200 / 0 / 0` claim.

## R4 Full Replay

Command:

```powershell
python scripts\run_domain_bootstrap_qa_batch.py --dataset-root datasets\real_world_transfer\fresh_ugly_public_20260529_01 --compile-root C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\compile_r1 --out-root C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r4_full --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --timeout-scale 6 --no-cache --out-json C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r4_full_summary.json --out-md C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r4_full_summary.md
```

Result from the explicit summary artifact:

- QA: `198 / 1 / 1` over `200`
- Exact rate: `99.0%`
- Hygiene: `0` compatibility rows, `0` runtime load errors, `0` write proposals

Per fixture:

- `court_order_ugly_003`: `25 / 0 / 0`
- `fda_warning_ugly_007`: `25 / 0 / 0`
- `labor_board_ugly_003`: `25 / 0 / 0`
- `osha_incident_ugly_007`: `25 / 0 / 0`
- `procurement_contract_ugly_003`: `23 / 1 / 1`
- `puc_order_ugly_003`: `25 / 0 / 0`
- `sec_material_event_ugly_007`: `25 / 0 / 0`
- `state_ag_settlement_ugly_003`: `25 / 0 / 0`

Operational caveat:

- The shell command timed out after the batch had already written `qa_r4_full_summary.md`.
- Two stale child QA processes kept running briefly and wrote duplicate later fixture artifacts into the same fixture directories.
- Therefore, directory-level adjudication over `qa_r4_full` is not a reliable description of the summary-selected R4 run unless it follows the JSON paths listed in `qa_r4_full_summary.md`.

Summary-selected R4 residue:

- `procurement_contract_ugly_003 q003`: partial. The query results supported the contract type and term, but the judge did not see the RFP number as supported in the selected evidence.
- `procurement_contract_ugly_003 q004`: miss caused by `IncompleteRead(143 bytes read)` from the provider path. This is a transient provider/runtime read failure, not a stable compile or query mechanism finding.

## R5 Target Replay

Command:

```powershell
python scripts\run_domain_bootstrap_qa.py --run-json C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\compile_r1\procurement_contract_ugly_003\domain_bootstrap_file_20260529T063933452519Z_source_qwen-qwen3-6-35b-a3b.json --qa-file datasets\real_world_transfer\fresh_ugly_public_20260529_01\procurement_contract_ugly_003\qa.md --oracle-jsonl datasets\real_world_transfer\fresh_ugly_public_20260529_01\procurement_contract_ugly_003\oracle.jsonl --only-ids q003,q004 --base-url https://openrouter.ai/api/v1 --model qwen/qwen3.6-35b-a3b --temperature 0 --top-p 0.82 --no-cache --judge-reference-answers --classify-failure-surfaces --out-dir C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r5_target_procurement_q003_q004 --timeout 420
```

Result:

- `q003/q004`: `2 / 0 / 0`
- Hygiene: `0` compatibility rows, `0` runtime load errors, `0` write proposals

Read:

- The two R4 summary-selected residues are not stable target-replay mechanism failures.
- The current defensible claim is still the full R4 corpus score, `198 / 1 / 1 = 99.0%`.
- A clean score would require a fresh full replay into an empty output directory, not reuse of the timeout-contaminated `qa_r4_full` directory.

## R5 Clean Full Replay

Command:

```powershell
python scripts\run_domain_bootstrap_qa_batch.py --dataset-root datasets\real_world_transfer\fresh_ugly_public_20260529_01 --compile-root C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\compile_r1 --out-root C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r5_full_clean --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --timeout-scale 6 --no-cache --out-json C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r5_full_clean_summary.json --out-md C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r5_full_clean_summary.md
```

Result:

- QA: `197 / 1 / 2` over `200`
- Exact rate: `98.5%`
- Hygiene: `0` compatibility rows, `0` runtime load errors, `0` write proposals

Per fixture:

- All fixtures except `procurement_contract_ugly_003`: `25 / 0 / 0`
- `procurement_contract_ugly_003`: `22 / 1 / 2`

R5 adjudication:

- `procurement_contract_ugly_003 q004`: miss, compile-labeled. Target replay had previously recovered this row, so this was treated as query-plan fragility around legal representative header rows, not a settled compile absence.
- `procurement_contract_ugly_003 q009`: partial, query-surface. Identifier support carried the prior decision file numbers, but not enough surrounding source display for the judge to see the case name and date as one citation context.
- `procurement_contract_ugly_003 q013`: miss from malformed/truncated provider response (`Expecting value...`), with empty query results. Target replay had previously recovered this row.

Read:

- The clean replay confirms the procurement fixture is now the high-variance pressure point.
- The residue is not random: legal header representation, prior-decision citation context, and provider response integrity all stress query-side delivery rather than durable KB mutation.

## R6/R7 Target Replays

R6 target replay:

```powershell
python scripts\run_domain_bootstrap_qa.py --run-json C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\compile_r1\procurement_contract_ugly_003\domain_bootstrap_file_20260529T063933452519Z_source_qwen-qwen3-6-35b-a3b.json --qa-file datasets\real_world_transfer\fresh_ugly_public_20260529_01\procurement_contract_ugly_003\qa.md --oracle-jsonl datasets\real_world_transfer\fresh_ugly_public_20260529_01\procurement_contract_ugly_003\oracle.jsonl --only-ids q004,q009,q013 --base-url https://openrouter.ai/api/v1 --model qwen/qwen3.6-35b-a3b --temperature 0 --top-p 0.82 --no-cache --judge-reference-answers --classify-failure-surfaces --out-dir C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r6_target_procurement_q004_q009_q013 --timeout 420
```

Result:

- `q004/q009/q013`: `2 / 1 / 0`
- `q004`: exact
- `q009`: partial
- `q013`: exact
- Hygiene: `0/0/0`

R7 code change:

- `source_record_identifier_set_support` rows now carry admitted `SourceTextDisplay` when available, not only normalized identifier atom/value. This is still query-only support over admitted source-record rows; it writes no durable facts and adds no fixture vocabulary.

R7 target replay:

```powershell
python scripts\run_domain_bootstrap_qa.py --run-json C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\compile_r1\procurement_contract_ugly_003\domain_bootstrap_file_20260529T063933452519Z_source_qwen-qwen3-6-35b-a3b.json --qa-file datasets\real_world_transfer\fresh_ugly_public_20260529_01\procurement_contract_ugly_003\qa.md --oracle-jsonl datasets\real_world_transfer\fresh_ugly_public_20260529_01\procurement_contract_ugly_003\oracle.jsonl --only-ids q009 --base-url https://openrouter.ai/api/v1 --model qwen/qwen3.6-35b-a3b --temperature 0 --top-p 0.82 --no-cache --judge-reference-answers --classify-failure-surfaces --out-dir C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r7_target_procurement_q009_identifier_display --timeout 420
```

Result:

- `q009`: `1 / 0 / 0`
- Hygiene: `0/0/0`

Current read:

- Latest full-corpus clean replay remains R5: `197 / 1 / 2 = 98.5%`.
- Latest target evidence indicates the stable procurement citation-context partial is repaired.
- A fresh full replay would be needed before claiming an aggregate recovery above `98.5%`.

## R8 Intent-Gate Cleanup

Trigger:

- Side audit reports in `C:\prethinker_tmp_archive\side_audit_fixture_leaks_20260529.*` and `C:\prethinker_tmp_archive\side_audit_utterance_regex_20260529.*`.
- The audit concern was not direct fixture-name branching in active code; active leakage audit remained clean.
- The sharper concern was raw utterance/question regex acting as a Python language-understanding layer.

Code changes:

- Removed specific native fixture names from current leakage-review docs.
- Removed raw-utterance regex fallback activation from the newest identifier-set support gate.
- Removed raw-utterance regex fallback activation from the newest same-day companion-case disposition gate.
- Added regression guards proving those two support surfaces do not activate from raw question wording alone; they now require structured `query_intents`.

Target replays after cleanup:

- `procurement_contract_ugly_003 q009`: `1 / 0 / 0`, hygiene `0/0/0`
- `court_order_ugly_003 q006`: `1 / 0 / 0`, hygiene `0/0/0`
- `puc_order_ugly_003 q005`: `1 / 0 / 0`, hygiene `0/0/0`

Read:

- This is not a score-improvement intervention; it is a governance correction.
- The repaired paths still work when the LLM-produced semantic query layer supplies structured intent.
- Python remains allowed to parse source-contained structure and syntax, but these two support surfaces no longer use raw English question regex as their activation mechanism.

## R9 Post-Sign-Clean English Regression

Purpose:

- Measure the English ugly corpus after the sign-clean recovery commit, without repairing during the run.
- Reuse the existing R1 compile artifacts to isolate QA/query-path impact from compile variance.
- Run no-cache against OpenRouter Qwen3.6 35B A3B, `6` lanes, `temperature=0`, `top_p=0.82`.

Precondition:

- Sign-clean audit passed immediately before the replay.
- Audit artifacts:
  - `C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_post_signclean_20260529\sign_clean_audit.json`
  - `C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_post_signclean_20260529\sign_clean_audit.md`

Command:

```powershell
python scripts\run_domain_bootstrap_qa_batch.py --dataset-root datasets\real_world_transfer\fresh_ugly_public_20260529_01 --compile-root C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\compile_r1 --out-root C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_post_signclean_20260529\qa_full_clean --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --timeout-scale 6 --no-cache --out-json C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_post_signclean_20260529\qa_full_clean_summary.json --out-md C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_post_signclean_20260529\qa_full_clean_summary.md
```

Result:

- QA: `161 / 22 / 17` over `200`
- Exact rate: `80.5%`
- Hygiene: `0` compatibility rows, `0` runtime load errors, `0` write proposals
- Runtime: about `38.9` minutes wall-clock

Per fixture:

- `court_order_ugly_003`: `17 / 4 / 4`
- `fda_warning_ugly_007`: `22 / 1 / 2`
- `labor_board_ugly_003`: `20 / 3 / 2`
- `osha_incident_ugly_007`: `19 / 1 / 5`
- `procurement_contract_ugly_003`: `20 / 3 / 2`
- `puc_order_ugly_003`: `21 / 3 / 1`
- `sec_material_event_ugly_007`: `20 / 4 / 1`
- `state_ag_settlement_ugly_003`: `22 / 3 / 0`

Diff against R5 clean full replay:

- R5: `197 / 1 / 2 = 98.5%`
- R9: `161 / 22 / 17 = 80.5%`
- Changed rows: `41`
- Transitions:
  - `exact -> partial`: `22`
  - `exact -> miss`: `16`
  - `partial -> miss`: `1`
  - `miss -> exact`: `2`
- New failure surfaces among changed rows:
  - `compile_surface_gap`: `23`
  - `query_surface_gap`: `9`
  - `hybrid_join_gap`: `4`
  - `answer_surface_gap`: `3`
  - `not_applicable`: `2`

Read:

- The prior `98.5%` English claim does not survive the sign-clean correction.
- The drop is too large to treat as ordinary provider variance.
- The removed raw-English semantic routing was carrying a meaningful amount of answer delivery on this corpus.
- The cleaned instrument still has good hygiene, but its current English ugly score is `80.5%` until proper semantic query support is rebuilt without Python-side utterance handling.
- This is the right failure: no compatibility rows, no write proposals, and no runtime leakage were used to inflate the score.

Immediate blocker:

- Rebuild the lost delivery capacity through sign-clean mechanisms only: LLM-produced query semantics, source-contained compile artifacts, deterministic joins over admitted facts, and no Python regex over raw user utterances.

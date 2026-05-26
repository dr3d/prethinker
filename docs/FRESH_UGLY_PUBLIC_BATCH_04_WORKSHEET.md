# Fresh Ugly Public Batch 04 Worksheet

Purpose:

Measure transfer on eight newly requisitioned ugly public fixtures after the
Batch 03 mechanism work, without further tuning against Batch 03 residues.

Discipline:

- Treat this as fresh transfer evidence, not a native-corpus stamp.
- Validate package shape before inference spending.
- Do not repair mid-run.
- Keep exact/partial/miss, gate pass/hold, compatibility rows, runtime errors,
  write proposals, and failure-surface distribution separate.
- If a row requires outside evidence, convention tables, or another document
  not included in the pack, adjudicate it as a scope boundary rather than
  teaching that knowledge to the active instrument.

Expected package shape:

```text
datasets/real_world_transfer/<batch_id>/
  <fixture_id>/
    source.md
    qa.md
    qa_authored_with_answers.md
    oracle.jsonl
    metadata.json
```

Expected intake:

```text
documents: 8
questions per fixture: 25
total QA rows: 200
```

## Preflight Commands

Use the actual incoming `<batch_id>` folder name.

```powershell
$line = Get-Content .env.local | Where-Object { $_ -match '^\s*OPENROUTER_API_KEY\s*=' } | Select-Object -First 1
$key = ($line -replace '^\s*OPENROUTER_API_KEY\s*=\s*','').Trim().Trim('"').Trim("'")
$env:OPENROUTER_API_KEY = $key
$env:PRETHINKER_API_KEY = $key

python scripts\validate_fresh_ugly_batch.py datasets\real_world_transfer\<batch_id> `
  --expected-documents 8 `
  --expected-questions 25 `
  --out-json C:\prethinker_tmp_archive\<batch_id>_validation_20260526.json `
  --out-md C:\prethinker_tmp_archive\<batch_id>_validation_20260526.md

python scripts\audit_active_instrument_leakage.py
```

## Compile R1 Plan

```powershell
python scripts\run_domain_bootstrap_file_batch.py `
  --dataset-root datasets\real_world_transfer\<batch_id> `
  --out-root C:\prethinker_tmp_archive\<batch_id>_r1_20260526\compile_r1 `
  --model qwen/qwen3.6-35b-a3b `
  --base-url https://openrouter.ai/api/v1 `
  --timeout 1200 `
  --lanes 6 `
  --compile-source `
  --compile-flat-plus-plan-passes `
  --focused-pass-ops-schema `
  --source-entity-ledger `
  --archival-identifier-ledger `
  --source-record-ledger `
  --source-record-ledger-facts `
  --intake-registry-context `
  --review-profile `
  --profile-review-retry `
  --quality-gate `
  --quality-retry-on-hold `
  --quality-retry-max-attempts 1 `
  --out-json C:\prethinker_tmp_archive\<batch_id>_r1_20260526\compile_r1_summary.json `
  --out-md C:\prethinker_tmp_archive\<batch_id>_r1_20260526\compile_r1_summary.md
```

Record:

```text
fixtures:
parsed OK:
candidate predicates:
compile admitted / skipped:
effective admitted / skipped:
diagnostic rejected flat-pass skips:
quality gate pass / hold:
compatibility/runtime/write rows:
```

## QA R1 Plan

```powershell
python scripts\run_domain_bootstrap_qa_batch.py `
  --dataset-root datasets\real_world_transfer\<batch_id> `
  --compile-root C:\prethinker_tmp_archive\<batch_id>_r1_20260526\compile_r1 `
  --out-root C:\prethinker_tmp_archive\<batch_id>_r1_20260526\qa_r1 `
  --model qwen/qwen3.6-35b-a3b `
  --base-url https://openrouter.ai/api/v1 `
  --timeout 420 `
  --lanes 6 `
  --no-cache `
  --compatibility-adapter-row-limit 0 `
  --out-json C:\prethinker_tmp_archive\<batch_id>_r1_20260526\qa_r1_summary.json `
  --out-md C:\prethinker_tmp_archive\<batch_id>_r1_20260526\qa_r1_summary.md
```

Record:

```text
questions:
exact / partial / miss:
exact rate:
runtime load errors:
write proposal rows:
compatibility rows:
failure-surface counts:
response-envelope status counts:
per-fixture exact / partial / miss:
```

## Read Protocol

Clean signal:

- `>= 94%` exact on 200 rows.
- `0` runtime load errors.
- `0` write proposal rows.
- `0` compatibility rows.
- Misses cluster into mechanism-shaped categories rather than source-specific
  facts.

Concerning signal:

- `< 90%` exact, unless dominated by explicit external-scope rows.
- Any runtime/write/compatibility leakage.
- Many regressions caused by query-only support overreach.
- Fixture vocabulary or document-class constants appearing in active code.

Post-run action:

- If clean, compare failure-mode distribution against Batch 03 and native.
- If neutral, inspect the largest two failure clusters only.
- If concerning, stop and adjudicate before adding mechanisms.

## Run 2026-05-26 - `fresh_ugly_public_20260526_01`

Intake:

- Incoming folder retained under
  `datasets/real_world_transfer/fresh_ugly_public_20260526_01/`.
- Fixtures: `court_ugly_001`, `nhtsa_ugly_001`, `nlrb_ugly_001`,
  `ntsb_ugly_001`, `ntsb_ugly_002`, `procurement_ugly_001`,
  `puc_ugly_001`, `state_ag_ugly_001`.
- Incoming package had 25 questions and 25 oracle rows per fixture, but the
  oracle rows used numeric ids plus `answer` rather than `q001` ids plus
  `reference_answer`; it also lacked `qa_authored_with_answers.md`.
- Mechanical normalization applied before inference spend:
  normalized oracle ids to `q001`...`q025`, preserved numeric ids as
  `original_id`, copied `answer` into `reference_answer`, and generated
  `qa_authored_with_answers.md` from `qa.md` plus `oracle.jsonl`.
- Validation after normalization: pass, `8/8` fixtures, `200/200` questions,
  `200/200` reference answers, `0` issues, `0` warnings.
- Active leakage audit after the run: pass, `0` forbidden hits, `10` existing
  warning hits.

Operator note:

- First compile attempt at
  `C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_r1_20260526`
  failed immediately with OpenRouter `401 Missing Authentication header`.
  Cause: `.env.local` also has `PRETHINKER_API_KEY`, and the runner prefers
  `PRETHINKER_API_KEY` over `OPENROUTER_API_KEY`. For OpenRouter research
  runs, bind both environment variables to the OpenRouter key in the shell.
  This was a configuration abort, not a measurement.

Compile R1b:

```text
artifact root:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_r1b_20260526

model: qwen/qwen3.6-35b-a3b via OpenRouter
lanes: 6
cache: n/a
quality retry: enabled, max 1
```

Compile aggregate:

```text
fixtures: 8
parsed OK: 8
candidate predicates: 219
compile admitted / skipped: 900 / 175
effective admitted / skipped: 900 / 111
diagnostic rejected flat-pass skips: 64
quality gate pass / hold: 1 / 7
```

Compile gate read:

- Only `nhtsa_ugly_001` passed the compile gate.
- The seven holds were dominated by source-claim/source-authority/status-state
  carrier delivery, not parse failure.
- `state_ag_ugly_001` also carried `compile_health:verdict=poor`.

QA R1:

```text
questions: 200
exact / partial / miss: 176 / 10 / 13
not judged: 1
exact rate: 88.0%
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Per-fixture QA:

| Fixture | Exact | Partial | Miss | Notes |
| --- | ---: | ---: | ---: | --- |
| `court_ugly_001` | 20 | 2 | 2 | plus 1 not-judged/judge-uncertain row |
| `nhtsa_ugly_001` | 24 | 1 | 0 | only compile-gate pass |
| `nlrb_ugly_001` | 23 | 1 | 1 | one hybrid join miss, one query partial |
| `ntsb_ugly_001` | 24 | 0 | 1 | blank-after-colon/list extraction miss |
| `ntsb_ugly_002` | 24 | 0 | 1 | investigative-activity list miss |
| `procurement_ugly_001` | 19 | 2 | 4 | procurement heading/footnote/list pressure |
| `puc_ugly_001` | 19 | 3 | 3 | commission parties/footnotes/order clauses |
| `state_ag_ugly_001` | 23 | 1 | 1 | paragraph binding-mediation miss |

Non-exact failure-surface distribution:

```text
compile_surface_gap: 18
query_surface_gap: 4
hybrid_join_gap: 1
judge_uncertain: 1
```

Read:

- This is a concerning transfer signal by the predeclared threshold:
  exact rate is below `90%`, despite clean runtime/write/compatibility hygiene.
- The hygiene result still matters: no compatibility adapter pressure, no
  runtime load errors, and no write proposals inflated the score.
- The compile gate was more pessimistic than QA, but directionally useful:
  most non-exact rows are compile-surface gaps, especially source-order lists,
  footnote anchors, blank fields, counsel/signature blocks, operative clauses,
  contractor/award table rows, and status/authority/claim carriers.
- Do not tune to fixture vocabulary. The next intervention should be
  mechanism-shaped and source-generic: preserve repeated official-record list
  structures and source-anchored carrier rows more reliably, then guard against
  query-path churn.

Immediate next blockers:

1. Inspect the `18` compile-surface rows as mechanism groups, not fixture facts.
2. Decide whether the `1` not-judged court acreage row is a judge/rendering
   problem or an oracle ambiguity problem.
3. Add one narrow regression harness that replays these non-exact rows without
   changing the corpus score claim.
4. Only after mechanism grouping, implement transfer-safe compile-surface
   repairs and replay targeted rows as mechanism evidence.

## Repair Cycle 2026-05-26 - Source-Record Scaffolding R2/R3

Intent:

Rectify the Batch 04 source-shape gaps without promoting fixture vocabulary,
document names, answer strings, or one-off public-record facts into the active
instrument.

Scope:

- Affected source-shape mechanisms only: official-form blank fields, printed
  note/symbol markers, standalone bold headings, and quoted source-label entry
  rosters.
- No compatibility adapters.
- No write proposals.
- No durable semantic truth mutation from query-time code.

Understandings attained:

1. Several misses were not failures to "know" the source; they were failures to
   keep enough deterministic source scaffolding addressable after compile.
2. Same-line official forms can contain multiple `Key: Value` fields, including
   explicit blank-after-colon cells and slash no-data markers. The previous
   source-record field parser treated some of these as one broad field or lost
   the blank state.
3. Printed note and symbol systems need two surfaces, not one: the definition
   row (`*Small Business`, numbered footnote bodies) and the anchor rows where
   the printed marker appears.
4. Standalone bold uppercase markdown lines are often real section headings.
   Treating them as ordinary labeled lines stranded downstream rows under the
   previous section.
5. A companion that returns all ordered labeled entries is useful only when the
   question names a quoted source label or phrase. The broad version over-fired
   on general roster questions and was rejected before finalizing.
6. The three-fixture guard is noisy. Rows improved exactly where the new
   source-record support fired, but unrelated rows still churned under fresh
   QA calls. This is evidence for mechanism value, not a clean affected-slice
   score claim.

Changes applied:

- `src/source_record_ledger.py`
  - Promotes standalone bold headings to `heading` source-record rows and
    updates current section.
  - Preserves multi-field same-line key/value forms.
  - Emits explicit `blank`, `slash_no_data_marker`, and `not_applicable`
    source-record field values.
  - Emits note/symbol marker facts:
    `source_record_note_marker/2`, `source_record_note_definition/3`,
    `source_record_symbol_definition/3`, and `source_record_note_anchor/2`.
- `scripts/run_domain_bootstrap_qa.py`
  - Treats slash/no-data and not-applicable field states as blank-like for
    field-state questions.
  - Adds query-only source-record support for note markers and their anchors.
  - Adds query-only source-record support for "under which heading/section"
    questions using nearest preceding admitted heading rows.
  - Adds narrowed ordered labeled-entry support, gated by quoted source targets,
    after a broad version caused roster-question overreach.
- Tests added in:
  - `tests/test_source_record_ledger.py`
  - `tests/test_domain_bootstrap_qa.py`

Verification:

```text
python -m pytest tests/test_source_record_ledger.py tests/test_domain_bootstrap_qa.py -q
376 passed

python scripts\audit_active_instrument_leakage.py
status: pass
forbidden hits: 0
warning hits: 10 existing agency/domain warnings

python -m py_compile src\source_record_ledger.py scripts\run_domain_bootstrap_qa.py
pass

python -m pytest -q
1801 passed, 2 subtests passed
```

Focused compile replay:

```text
artifact root:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_r2_mechanism_20260526

fixtures: procurement_ugly_001, puc_ugly_001, ntsb_ugly_001
parsed OK: 3/3
compile admitted / skipped: 417 / 69
quality gate pass / hold: 0 / 3
runtime/write/compatibility: 0 / 0 / 0
```

Compile-gate read:

- These repairs did not solve the source-authority/source-claim carrier gate.
- Holds remained on source-authority and source-claim/status-state carrier
  delivery. That is the next compile-surface lane, not a reason to discard the
  source-record repairs.

Focused QA replays:

```text
R1 baseline subset, same three fixtures:
62 / 5 / 8 on 75 rows

R2 mechanism QA, same three fixtures:
64 / 4 / 7 on 75 rows
changed rows: 19
improved rows: 10
regressed rows: 9
baseline exact -> non-exact: 7
regression guard: fail

R3 final guard, same three fixtures, final narrowed code:
61 / 4 / 9 on 75 rows
changed rows: 18
improved rows: 8
regressed rows: 10
baseline exact -> non-exact: 8
regressions with added support surfaces: 0
regression guard: fail
```

Important row-level mechanism evidence:

- Official-form blank/no-data fields:
  - `ntsb_ugly_001 q013` recovered in R2 from `miss` to `exact`.
  - This is direct evidence for multi-field blank/slash preservation.
- Printed note/symbol markers:
  - `procurement_ugly_001 q004` recovered from `miss` to `exact`.
  - `procurement_ugly_001 q009` recovered from `miss` to `exact`.
  - `puc_ugly_001 q007` recovered from `miss` to `exact`.
  - These rows used `source_record_note_marker_support` or direct
    note-definition/anchor rows.
- Heading scope:
  - `procurement_ugly_001 q006` recovered from `miss` to `exact` when
    `source_record_under_heading_support` fired.
- Quoted source-label roster:
  - `procurement_ugly_001 q013` recovered in the narrowed procurement replay
    when `source_record_ordered_labeled_entry_support` fired.

Rejected/narrowed intervention:

- A broad ordered-entry companion was tried against procurement.
- It improved one row but attached to general roster questions and caused
  exact-to-miss regressions on rows that did not need it.
- Final code requires a quoted source target before ordered labeled-entry
  support can fire.
- This is the right lesson: source-record companions need explicit trigger
  discrimination, not just useful-looking rows.

Current read:

- Keep the source-record scaffolding repairs. They are source-generic,
  unit-tested, leakage-clean, and improved rows exactly where their support
  surfaces fired.
- Do not claim an affected-slice score improvement from R3. The guard failed
  on aggregate due to unrelated QA/query variance.
- The next blocker is not more one-row source-record polish. It is reducing
  compile/query-path variance on repeated official-record entry rosters and
  finishing the source-authority/source-claim carrier lane that still holds the
  compile gate.

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

## Repair Cycle 2026-05-26 - Query Intent Heading/Section R4

Intent:

Finish the next query-governance migration without allowing raw fixture or
English phrase triggers to re-enter the active instrument.

Scope:

- Heading and source-section query-side routes only:
  `source_record_preceding_heading_support`,
  `source_record_under_heading_support`,
  `source_record_named_section_window_support`,
  `source_record_quote_heading_locator_support`, and
  `source_record_section_list_detail_support`.
- No compatibility adapters.
- No write proposals.
- No durable fact mutation from query-time support.
- Raw utterance text may be passed through for answer rendering context, but
  these routes no longer decide whether to fire by parsing English question
  phrases.

Understandings attained:

1. The governed query lens often emits generic `heading_scope + target_terms`
   rather than a route-specific intent label. That is acceptable for nearest or
   enclosing heading support.
2. Special order relations still need structured constraints. For example,
   immediately-preceding heading questions should carry constraints such as
   `immediately_precedes`, `preceding_heading`, or `previous_heading`.
3. List and ordered-entry intents can legitimately activate section-window or
   section-list support when their target terms match an admitted heading or
   source label.
4. The first strict replay failed two FDA rows. The right fix was to widen the
   structured route contract; raw English regex was not restored.

Changes applied:

- `scripts/run_domain_bootstrap_qa.py`
  - Derives heading/list query intents from structured Prolog query templates
    and evidence-bundle support templates.
  - Routes heading/section companions through `query_intents[]` rather than raw
    question phrase interpretation.
  - Removes dead raw-question helper functions for preceding-heading,
    under-heading, named-section, quoted-target, and section-target parsing.
- `tests/test_domain_bootstrap_qa.py`
  - Adds structured-intent guards for section-list detail, preceding heading,
    under heading, named section window, and quote heading locator.
- `docs/SEMANTIC_IR_MAPPER_SPEC.md`
  - Records that generic `heading_scope + target_terms` is sufficient for
    nearest/enclosing heading support, while special relations require
    structured constraints.

Focused replay:

```text
artifact root:
C:\prethinker_tmp_archive\query_intent_heading_migration_probe_20260526

procurement_ugly_001 q006 under heading: exact / 0 compatibility rows
fda_ugly_001 q007 preceding heading:     exact / 0 compatibility rows
fda_ugly_001 q013 named section window:  exact / 0 compatibility rows
fda_ugly_003 q006 quote heading:         exact / 0 compatibility rows
fda_ugly_003 q014 section/list detail:   exact / 0 compatibility rows
```

Validation:

```text
python -m pytest tests\test_domain_bootstrap_qa.py -q -k "section_list_detail or preceding_heading or under_heading or named_section_window or quote_heading_locator or query_intents"
11 passed, 344 deselected

python -m pytest -q
1818 passed, 2 subtests passed

python scripts\audit_utterance_regex_governance.py
490 regex hits / 100 semantic_trigger

python scripts\audit_active_instrument_leakage.py
status: pass
forbidden hits: 0
warning hits: 10 existing agency/domain warnings
```

Full Batch 04 R4 thermometer:

```text
artifact root:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_r4_query_intent_20260526

dataset:
datasets\real_world_transfer\fresh_ugly_public_20260526_01

validation:
pass, 8/8 fixtures, 25 questions per fixture, 0 issues, 0 warnings

compile:
fixtures: 8
parsed OK: 8
candidate predicates: 176
compile admitted / skipped: 1007 / 55
effective admitted / skipped: 1007 / 55
diagnostic rejected flat-pass skips: 0
quality gate pass / hold: 1 / 7

qa:
questions: 200
exact / partial / miss: 181 / 11 / 7
exact rate: 90.5%
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Per-fixture QA:

| Fixture | Exact | Partial | Miss |
| --- | ---: | ---: | ---: |
| `court_ugly_001` | 22 | 0 | 3 |
| `nhtsa_ugly_001` | 22 | 2 | 1 |
| `nlrb_ugly_001` | 21 | 4 | 0 |
| `ntsb_ugly_001` | 25 | 0 | 0 |
| `ntsb_ugly_002` | 23 | 2 | 0 |
| `procurement_ugly_001` | 22 | 1 | 2 |
| `puc_ugly_001` | 23 | 1 | 1 |
| `state_ag_ugly_001` | 23 | 1 | 0 |

Failure-surface distribution:

```text
not_applicable: 181
compile_surface_gap: 15
hybrid_join_gap: 2
answer_surface_gap: 1
judge_uncertain: 1
```

R1b -> R4 comparison:

```text
R1b: 176 / 10 / 13 = 88.0%
R4:  181 / 11 / 7  = 90.5%
delta: +5 exact, +1 partial, -6 miss

changed rows: 32
improved rows: 18
regressed rows: 14
baseline exact -> non-exact: 13
baseline exact -> miss: 3
regressions with added support surfaces: 3
regression guard: fail
```

Regressions with added support surfaces:

- `nlrb_ugly_001 q011`: added
  `source_record_named_section_window_support`, exact -> partial.
- `puc_ugly_001 q019`: added `source_record_note_marker_support`, removed
  `source_record_duration_quantity_support`, exact -> miss.
- `state_ag_ugly_001 q010`: added `source_record_note_marker_support`,
  exact -> partial.

Read:

- The aggregate moved back above 90%, with clean runtime/write/compatibility
  hygiene. That is useful evidence that the query-intent migration did not
  collapse the fresh ugly batch.
- This is not release-clean. The compile gate still held 7/8 fixtures, and the
  regression guard failed. The row churn is the signal to respect.
- The query-intent migration should stay. The remaining failures point less at
  English-question parsing and more at source-claim/source-authority/status
  carrier delivery plus cross-route adjudication when multiple source-record
  supports compete.

Next blockers:

1. Adjudicate the three regressions with added support surfaces before adding
   another query-side mechanism.
2. Resume the compile-surface carrier lane for `source_claim`,
   `source_authority`, and `status_state` delivery. That is what the quality
   gate is still complaining about.
3. Keep the fresh-batch score as thermometer evidence only; do not tune toward
   the fixture names or answer strings.

## Repair Cycle 2026-05-26 - Regression Adjudication and Carrier Accounting

Intent:

Handle the next blocker without hiding the regression-guard failure: adjudicate
the three rows where added source-record support coincided with regression, then
inspect the compile-gate carrier lane.

Regression adjudication:

- `nlrb_ugly_001 q011`: the added
  `source_record_named_section_window_support` was trigger overreach. A generic
  `list` intent with only one token overlapping a broad document heading opened
  a section window that was not the requested case/citation/location roster.
  The route now requires a stronger heading-target match for generic list
  intents. Replay no longer emits the section-window support, but the row still
  lands `partial` / `judge_uncertain` because the compiled case/citation/location
  surface is incomplete. This is a remaining compile/list representation issue,
  not a heading-window issue.
- `puc_ugly_001 q019`: generic note-marker intent from placeholder evidence
  queries polluted the row, and duration support was too narrowly scoped to one
  imperfect duration intent. Generic `marker_scope:all` placeholder intents no
  longer fire note-marker support, and duration support may use sibling
  structured intent targets from the same query. Focused replay recovered the
  row to `exact`.
- `state_ag_ugly_001 q010`: generic note-marker support produced large,
  irrelevant note/anchor tables. The same note-marker guard removes that noise.
  A source-generic `source_record_definition_entry_support` route was added for
  enumerated definition rows, gated by structured `definition_entry_location`
  intent. The focused replay recovered the row to `exact`; in this replay the
  model did not emit that definition-entry constraint, so the recovery should be
  read mainly as note-marker-noise removal plus ordinary direct evidence, not as
  a proved definition-entry mechanism on this row.

Changes applied:

- Generic note-marker placeholders such as `footnote`, `note`, `marker`,
  `symbol`, `line`, and `text` no longer create `note_marker` query intents
  from structured Prolog query templates.
- `source_record_note_marker_support` no longer fires for `marker_scope:all`
  unless the structured intent carries target terms.
- Generic list-derived named-section windows now require a strong heading match
  instead of one shared broad token.
- `source_record_duration_quantity_support` can consider target tokens from
  sibling structured intents in the same query.
- Added query-only `source_record_definition_entry_support` for source-record
  text shaped like enumerated definition entries. It parses admitted
  `source_record_text_atom` rows only and writes no durable facts.

Focused replay:

```text
artifact root:
C:\prethinker_tmp_archive\batch04_regression_adjudication_20260526

nlrb_ugly_001 q011:     partial / judge_uncertain / 0 compatibility
puc_ugly_001 q019:      exact / not_applicable / 0 compatibility
state_ag_ugly_001 q010: exact / not_applicable / 0 compatibility
```

Carrier accounting inspection:

The compile-gate carrier lane also exposed accounting false negatives. Some
offered direct carriers were emitted but not counted as delivered by the
delivery checker:

- `appeal_filed/3` was emitted in court records but not counted as a
  status/state delivery row.
- `conditional_rule/4`, `reduction_rule/5`, and `vehicle_action/4` were emitted
  in settlement-style conditional state/rule rows but not counted as
  status/state delivery rows.
- `source_attributed_legal_fact/4` was emitted but not counted as a
  source-attributed-claim delivery row.

Accounting changes:

- Count `appeal_filed/3` as status/state delivery when it carries appellant,
  target/subject, and date/status.
- Count `conditional_rule/4`, `directive_with_scope/4`, `reduction_rule/5`, and
  `vehicle_action/4` as status/state delivery when they carry joined
  condition/action/state scope.
- Count `source_attributed_legal_fact/4` as source-attributed-claim delivery.
- Treat direct `appeal_window`-style rows as satisfying the appeal-filing
  backbone group when the direct predicate keeps the appeal window joinable.

Refreshing profile-delivery reports over the existing R4 compile artifacts,
without recompiling, changes the carrier findings as follows:

```text
old:
source_claim_carrier_offered_but_undelivered: 11
status_state_carrier_offered_but_undelivered: 6
source_claim_carrier_partially_delivered: 3
source_authority_carrier_offered_but_undelivered: 2
source_claim_backbone_coexistence_missing: 2
source_authority_carrier_partially_delivered: 1

new:
source_claim_carrier_offered_but_undelivered: 10
source_claim_carrier_partially_delivered: 4
status_state_carrier_offered_but_undelivered: 3
source_authority_carrier_offered_but_undelivered: 2
status_state_carrier_partially_delivered: 1
source_authority_carrier_partially_delivered: 1
```

Read:

- This is not a new compile-gate score claim because the R4 artifacts were not
  freshly recompiled. It is a delivery-accounting correction over existing
  compile output.
- The status-state lane had clear false negatives. Several held gates should no
  longer complain that no status/state rows were delivered when direct joined
  rows already exist.
- The remaining carrier pressure is now more honestly concentrated in real
  source-claim delivery and source-authority gaps, especially rows where the
  compile still does not emit a source-to-claim carrier at all.

Validation:

```text
python -m pytest tests\test_domain_bootstrap_qa.py -q -k "note_marker or named_section_window or duration_quantity or definition_entry"
14 passed, 347 deselected

python -m pytest tests\test_domain_bootstrap_file.py -q -k "source_claim_delivery_accepts_source_attributed_legal_fact_rows or status_state_delivery_accepts_direct_appeal_filing_rows or status_state_delivery_accepts_conditional_rule_rows"
3 passed, 143 deselected

python -m pytest tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_qa.py -q
507 passed

python scripts\audit_active_instrument_leakage.py
status: pass
forbidden hits: 0
warning hits: 10 existing agency/domain warnings
```

Next blockers:

1. Do not chase `nlrb_ugly_001 q011` with a section-window patch. The remaining
   issue is incomplete case/citation/location roster preservation.
2. Continue the real source-claim lane: the largest remaining compile-gate
   pressure is still `source_claim_carrier_*`, not status-state accounting.
3. Recompile a small affected fixture set before claiming any compile-gate
   improvement; the carrier accounting refresh is mechanism evidence only.

## Repair Cycle 2026-05-26 - Profile-Delivery Repair Pass and Detector Cleanup

Intent:

Hit the next carrier blocker without letting Python extract source facts. The
mechanism added here gives the LLM one bounded proposal-only repair pass after a
deterministic profile-delivery diagnostic, then still routes every proposed row
through `source_pass_ops_v1` and the normal mapper.

Changes applied:

- Added `--profile-delivery-repair-pass` to
  `scripts\run_domain_bootstrap_file.py`.
- Added batch pass-through for `--profile-delivery-repair-pass` in
  `scripts\run_domain_bootstrap_file_batch.py`.
- The repair pass only runs when profile-delivery findings show repairable
  source-claim, source-authority, source-claim-backbone, or status-state carrier
  pressure.
- The repair pass receives structural diagnostics and offered carrier
  signatures. It does not receive target facts, oracle answers, or fixture
  language, and it writes nothing directly.

Probe:

```text
fixture: procurement_ugly_001
artifact:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_profile_delivery_repair_probe_20260526
```

Read from the probe:

- The repair pass ran and added 47 new unique facts with no compile-health
  flags.
- It emitted `solicitation_authority(mathtech_inc, 10_u_s_code_3204_a_1)`, but
  the checker originally refused to count that source-local authority row.
- The checker also treated `fund_source_details/3` and a `sole-source ... in
  support of ...` phrase as source-attributed-claim pressure.
- That means the first blocker was not "the LLM ignored the instruction"; it was
  a profile-delivery detector/accounting mismatch.

Detector/accounting cleanup:

- Count `solicitation_authority/2` as source-authority delivery when it carries
  governed contract/subject and authority code.
- Do not treat fund/appropriation source predicates such as
  `fund_source_details/3` as source-attributed-claim carriers unless the
  predicate name also carries an actual claim/comment/finding/opinion/report
  surface.
- Do not treat generic markdown field labels such as `Status:` as
  source-attributed speaker frames.
- Do not treat document-availability lines such as "report is available here"
  as source-attributed claims.
- Do not treat legal certification/payment-condition language as
  source-attributed claim pressure unless the certification itself is framed as
  saying, stating, confirming, or supporting a claim.
- Do not treat `state` by itself as status/state pressure. This prevents legal
  sources that mention a government party such as a State from creating
  condition/status obligations unless another actual status term is present.

Refresh over existing R4 compile artifacts:

```text
original R4 quality gate summary: 1 pass / 7 hold
current refreshed summary:       3 pass / 5 hold

remaining holds:
- court_ugly_001: source-claim partial plus a zero-yield legal-findings pass
- nlrb_ugly_001: rough_score-only hold
- procurement_ugly_001: source-authority miss in the old R4 artifact; the new
  repair probe shows this is recoverable when the repair pass emits
  solicitation_authority/2
- puc_ugly_001: mixed source-claim/status-state/backbone coexistence pressure
- state_ag_ugly_001: status-state pressure reduced from six signals to three
  after removing government-State noise; the remaining settlement/vehicle
  status pressure still needs adjudication
```

Validation:

```text
python -m pytest tests\test_domain_bootstrap_file.py -q -k "source_claim_mentions or fund_source or solicitation_authority or profile_delivery_repair"
12 passed, 146 deselected

python -m pytest tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_file_batch.py -q
220 passed

python -m pytest -q
1840 passed, 2 subtests passed

python -m py_compile scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_file_batch.py
pass

python scripts\audit_active_instrument_leakage.py --out-json C:\prethinker_tmp_archive\active_instrument_leakage_after_profile_delivery_repair_20260526.json --out-md C:\prethinker_tmp_archive\active_instrument_leakage_after_profile_delivery_repair_20260526.md
status: pass
forbidden hits: 0
warning hits: 10 existing agency/domain warnings
```

Next blockers:

1. Adjudicate `state_ag_ugly_001` status-state pressure. Determine whether
   `vehicle_action/4` is a real missing carrier or whether settlement reduction
   and vehicle-class rows already deliver the source's actual status surface.
2. Run a small affected-set recompile with `--profile-delivery-repair-pass`
   enabled before claiming compile-gate improvement.
3. Keep the repair pass off any public score claim until it is tested on a
   fresh ugly batch, because the first evidence is one-fixture mechanism
   evidence plus refreshed accounting.

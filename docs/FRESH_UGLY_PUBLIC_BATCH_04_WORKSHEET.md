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

## Repair Cycle 2026-05-26 - Affected-Set Blocker Adjudication

Intent:

Work the five named blockers before the next fresh ugly batch: state AG
status-state pressure, affected-set repair-pass transfer, court legal-finding
zero-yield, PUC mixed carrier/backbone pressure, and NLRB rough-score hold.

Affected-set recompile:

```text
artifact:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_affected_profile_repair_20260526

fixtures:
court_ugly_001
procurement_ugly_001
puc_ugly_001
state_ag_ugly_001
nlrb_ugly_001

compile flags:
--compile-source
--compile-flat-plus-plan-passes
--focused-pass-ops-schema
--source-entity-ledger
--archival-identifier-ledger
--source-record-ledger
--source-record-ledger-facts
--profile-delivery-repair-pass
--intake-registry-context
--review-profile
--profile-review-retry
--quality-gate
--quality-retry-on-hold
--quality-retry-max-attempts 1
```

Current refreshed affected-set summary after diagnostic scoring fixes:

```text
artifact:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_affected_profile_repair_20260526\compile_summary_current.md

quality gate: 2 pass / 3 hold

pass:
- court_ugly_001
- nlrb_ugly_001

hold:
- procurement_ugly_001: rough_score<0.775
- puc_ugly_001: source-claim carrier pressure plus stale appeal_filed/3 offer
- state_ag_ugly_001: compile_health poor; zero_yield=2
```

Reads:

- `state_ag_ugly_001`: the remaining status-state pressure is real, not just
  government-State detector noise. The source has settlement/vehicle status
  surfaces such as approved emissions modification receipt, vehicle removal
  from commerce, and vehicle purchase/reduction triggers. The compile has
  adjacent rows such as `reduction_rule/4` and vehicle-class rows, but no direct
  `vehicle_action/4` or equivalent delivery.
- `court_ugly_001`: the previous legal-finding zero-yield appears to be
  run/pass-plan variance, not a missing architecture lane. The affected
  recompile passes and emits direct legal surfaces such as `court_finding/2`
  plus source-attributed legal fact/claim rows.
- `puc_ugly_001`: mixed result. The source-claim side still looks real for
  party/position claims and unresolved/objection statements. The
  `appeal_filed/3` status-state pressure is detector overreach on generic
  appeal-window language, because the source states how a party may appeal, not
  that an appeal was filed.
- `nlrb_ugly_001`: the rough-score hold was diagnostic noise. The scorer was
  counting commas inside quoted values as arity drift and seeing parenthesized
  legal citations inside quoted values as fake predicate calls. With the
  scorer fixed, the same artifact reads `0.833` and passes quality gate. The
  remaining `case_id/1` id-only repeated-record warning is quality texture, not
  a gate blocker.
- `procurement_ugly_001`: the affected-set run surfaced a real profile-quality
  inconsistency, not a scorer bug. The profile declares `contract_award/8` while
  listing five argument roles, repeated-structure repair adds
  `contract_award/5`, and starter cases contain unquoted comma-bearing values.
  This should stay a hold instead of being papered over by permissive scoring.

Changes applied:

- Tightened the existing appeal-filing detector so generic appeal windows or
  appeal-notice instructions no longer add `appeal_filed/3`.
- Narrowed the appeal-filing source-claim backbone group so `notice`/`window`
  language alone does not create an appeal-filing backbone signal.
- Made profile-bootstrap scorer quote-aware for starter-case predicate calls
  and arity counting, so punctuation inside quoted values does not create false
  unknown predicate refs.
- Made batch `--summarize-existing` refresh profile-bootstrap scores from the
  parsed profile under the current scorer, matching the way profile-delivery
  diagnostics are refreshed for current-instrument reads.

Validation:

```text
python -m pytest tests\test_domain_bootstrap_file.py -q -k "appeal_filing_profile_extension"
3 passed

python -m pytest tests\test_profile_bootstrap.py -q -k "quoted_values or unproposed_positive_predicate_calls or frontier_cases_using"
3 passed

python -m pytest tests\test_domain_bootstrap_file_batch.py -q -k "refreshes_profile_bootstrap_score or extracts_quality_gate_signals"
2 passed

python -m pytest tests\test_profile_bootstrap.py tests\test_domain_bootstrap_file_batch.py tests\test_domain_bootstrap_file.py -q
238 passed

python -m py_compile scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_file_batch.py src\profile_bootstrap.py
pass

python scripts\audit_active_instrument_leakage.py --out-json C:\prethinker_tmp_archive\active_instrument_leakage_after_affected_blockers_20260526.json --out-md C:\prethinker_tmp_archive\active_instrument_leakage_after_affected_blockers_20260526.md
status: pass
forbidden hits: 0
warning hits: 10 existing agency/domain warnings
```

Next blockers:

1. Recompile `puc_ugly_001` once under the narrowed appeal detector. Expected:
   appeal-filed status pressure should disappear; source-claim pressure should
   remain if the missing party-position rows are real.
2. Work `state_ag_ugly_001` as the next real compile blocker: vehicle/status
   actions are being implied by settlement/reduction rows but not delivered as
   direct action/status units.
3. Treat `procurement_ugly_001` as profile-proposal quality work, not a carrier
   delivery repair. The profile needs arity/schema discipline before any compile
   gate claim.

## Repair Cycle 2026-05-26 - PUC and State AG Targeted Follow-Through

Intent:

Finish the two substantive affected-set holds without turning fixture language
into the instrument. The rule was accounting/contract cleanup only: count rows
already emitted by the compiler when their predicate shape genuinely satisfies
the carrier contract; remove detector false positives when the source signal was
not the event the detector claimed.

PUC targeted recompile:

```text
artifact:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_puc_after_appeal_tighten_20260526

current summary:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_puc_after_appeal_tighten_20260526\compile_summary_current3.md

quality gate: pass
rough: 0.972
admitted / skipped: 149 / 6
profile_delivery_flags: []
compile_health_flags: []
```

PUC reads:

- Tightening the appeal detector worked. Generic "party may appeal within N
  days" language no longer creates `appeal_filed/3` pressure.
- The compile had already emitted party-position rows for opposition/support
  statements; those rows are legitimate source-owned claim/position delivery.
- "Vote Solar" was an organization name, not a vote/tally surface. Removing
  singular `vote` from the source-claim backbone trigger cleared that false
  backbone hold while preserving `voted`/`votes`/`voting`/`tally` signals.
- "Time available to the commission" was timing/capacity language, not a claim
  that a source was available. The source-claim key now ignores that shape.

State AG targeted recompile:

```text
artifact:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_state_ag_scope_status_repair_20260526

current summary:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_state_ag_scope_status_repair_20260526\compile_summary_current2.md

quality gate: pass
rough: 1.0
admitted / skipped: 222 / 2
profile_delivery_flags: []
compile_surface_contract_flags: []
compile_health_flags: []
```

State AG reads:

- The earlier zero-yield/skip-heavy profile was run-variant poor compile
  quality. A fresh targeted compile produced a much healthier artifact.
- The remaining source-authority pressure was accounting: `legal_basis/2` rows
  directly carry governed claim/conduct plus legal authority and should satisfy
  the source-authority surface contract.
- The remaining status-state pressure was accounting: `payment_reduction_rule/3`
  rows carry the payment subject, reduction amount, and vehicle/action trigger.
  They satisfy the settlement vehicle-action/status surface better than forcing
  a generic `status_state_at/4` row.
- The mapper contract for `scope_or_date` was internally inconsistent. A role
  named `scope_or_date` must allow a non-temporal source scope; exact date roles
  remain strict.

Changes applied:

- Count `legal_basis/2` as source-authority delivery and in the source-authority
  compile-surface contract.
- Count `payment_reduction_rule/3` as status-state delivery when it carries
  payment subject, amount, and trigger event.
- Recognize `payment_reduction_rule/3`/`reduction_rule/*` as offered
  status-state carriers when their profile shape is the reduction-trigger
  carrier.
- Allow `scope_or_date` contract roles to accept non-temporal scope atoms while
  keeping exact `date`/`*_date` roles temporal.
- Count `party_position/*` and `legal_position/*` as source-owned claim/position
  delivery.
- Treat statement/comment/testimony/memo/report/email/note source kinds as
  equivalent for source-claim key matching when the claim kind matches.
- Ignore `available` as a source-claim key when it is timing/capacity language
  such as "time available" or "available to".
- Remove singular `vote` from source-claim backbone voting triggers; keep
  `voted`, `votes`, `voting`, `tally`, `ayes`, `nays`, `roll`, and `call`.

Validation:

```text
python -m pytest tests\test_domain_bootstrap_file.py -q -k "status_state_delivery_accepts_conditional_rule_rows"
1 passed

python -m pytest tests\test_domain_bootstrap_file.py -q -k "source_claim_backbone_ignores_vote or source_claim_key_ignores_available or party_position_as_statement_claim or status_state_delivery_accepts_conditional_rule_rows"
4 passed

python -m pytest tests\test_semantic_ir_runtime.py -q -k "scope_or_date or clear_contract_role_mismatch or interval_label"
3 passed

python -m py_compile scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_file_batch.py scripts\audit_compile_surface_stability.py src\profile_bootstrap.py src\semantic_ir.py
pass
```

Current affected-set read:

```text
Not a single fresh 5-fixture rerun.

Pass on current targeted reads:
- court_ugly_001
- nlrb_ugly_001
- puc_ugly_001
- state_ag_ugly_001

Remaining hold:
- procurement_ugly_001: profile-proposal quality/arity inconsistency
```

Next blocker:

`procurement_ugly_001` should stay classified as profile-quality, not carrier
delivery. The observed issue is a profile that declares `contract_award/8` while
listing five argument roles, then uses unquoted comma-bearing starter values.
Do not relax the scorer to pass that; fix the profile proposal discipline or
test it on a fresh procurement-style document.

## Repair Cycle 2026-05-26 - Profile Schema Contract Discipline

Intent:

Make profile-proposal defects visible as profile-schema contract defects instead
of letting them hide inside a low rough score or downstream frontier drift. This
is deliberately not a carrier repair and not a fixture-language repair: the
instrument now checks a generic invariant that every proposed predicate
signature's `/N` arity must match the number of short schema role labels in
`candidate_predicates[].args`.

Change applied:

- Added `candidate_signature_arg_mismatch_count` and
  `candidate_signature_arg_mismatch_refs` to `profile_bootstrap_score`.
- Added `profile_schema_contract_flags` to compile-batch summaries and quality
  gate reasons.
- Added generic retry guidance for profile arity/args mismatch: lower the `/N`
  when a predicate has fewer core roles, or add missing role labels when the
  higher arity is genuinely required. Do not repair by putting source values or
  copied examples into args.
- Tightened profile-bootstrap guidance so starter frontier predicate calls must
  quote comma/space/punctuation-bearing values or use normalized atoms.

Procurement current read:

```text
artifact summarized:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_affected_profile_repair_20260526\compile\procurement_ugly_001\domain_bootstrap_file_20260526T140545031873Z_source_qwen-qwen3-6-35b-a3b.json

current summary:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_affected_profile_repair_20260526\procurement_current_after_profile_schema_contract.md

quality gate: hold
rough: 0.617
admitted / skipped: 245 / 7
profile_schema_contract_flags:
- candidate_signature_arg_mismatch:contract_award/8:args=5
frontier_unknown_positive_predicate_refs:
- contract_award/7
- contracting_activity/4
- contractor_location/3
- funds/1
- performance_location/3
```

Read:

- The procurement hold is now sharper: the first-class defect is an internally
  inconsistent profile proposal, not a missing delivery carrier.
- The profile declares one predicate as `/8` while giving five role labels. The
  downstream frontier examples then show arity drift where comma-bearing
  human-readable values were not quoted or atomized.
- This is a useful hold. It prevents a bad profile shape from being counted as
  compile-surface failure and protects the instrument from overfitting the
  compiler around one malformed profile proposal.

Validation:

```text
python -m pytest tests\test_profile_bootstrap.py tests\test_domain_bootstrap_file_batch.py -q -k "signature_arg_role_mismatch or profile_schema_contract or quality_gate_signals or refreshes_profile_bootstrap_score"
4 passed

python -m pytest tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_file_batch.py tests\test_profile_bootstrap.py tests\test_semantic_ir_runtime.py -q
335 passed, 2 subtests passed

python -m py_compile scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_file_batch.py scripts\run_profile_bootstrap.py src\profile_bootstrap.py src\semantic_ir.py
pass

python scripts\audit_active_instrument_leakage.py --out-json C:\prethinker_tmp_archive\active_instrument_leakage_after_profile_schema_contract_20260526.json --out-md C:\prethinker_tmp_archive\active_instrument_leakage_after_profile_schema_contract_20260526.md
status: pass
forbidden hits: 0
warning hits: 10 existing agency/domain warnings
```

Next blocker:

Run a bounded quality retry or fresh procurement-like transfer fixture only
after deciding whether the profile generator should fix this in one retry pass
or whether the current artifact should remain a declared profile-quality hold.

## Repair Cycle 2026-05-26 - Procurement Profile-Contract Retry

Intent:

Test whether the profile generator can repair procurement-style profile
schema defects when the quality gate names the actual contract class. This was
still one-fixture mechanism evidence, not a benchmark run.

Harness change:

- Promoted repeated-structure defects into `profile_schema_contract_flags`:
  unknown repeated predicates, id-only record predicates, property predicates
  whose first role is not record/record-id-like, and positive starter-frontier
  predicates not present in candidate vocabulary.
- Added generic retry guidance for those profile-contract classes.
- This matters because the prior retry only saw the source-authority delivery
  symptom. The real source of rough-score pressure was repeated-record shape.

Observed sequence:

```text
profile-schema-contract summary:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_affected_profile_repair_20260526\procurement_current_after_profile_schema_contract.md

quality gate: hold
rough: 0.617
reason:
- profile_schema_contract:candidate_signature_arg_mismatch:contract_award/8:args=5
```

```text
bounded retry 1:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_procurement_profile_schema_retry_20260526\compile_summary.md

selected attempt: hold
rough: 0.75
reason:
- profile_delivery:source_authority_carrier_offered_but_undelivered
lesson:
- arity/args mismatch disappeared, but the source-authority carrier was still
  offered without delivered rows.
```

```text
bounded retry 2:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_procurement_profile_contract_retry2_20260526\compile_summary.md

selected attempt: hold
rough: 0.717
reason:
- profile_schema_contract:candidate_signature_arg_mismatch:contract_award/6:args=5
- profile_schema_contract:frontier_unknown_positive_predicate:contract_award/5
lesson:
- repeated-structure role mismatches and source-authority delivery cleared.
  The new residual was stale arity/frontier mismatch.
```

```text
bounded retry 3:
C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_procurement_profile_contract_retry3_20260526\compile_summary.md

quality gate: pass
rough: 1.0
admitted / skipped: 135 / 3
profile_schema_contract_flags: []
profile_delivery_flags: []
compile_health_flags: []
candidate_signature_arg_mismatch_refs: []
frontier_unknown_positive_predicate_refs: []
repeated_structure_role_mismatch_refs: []
```

Read:

- Procurement was not a missing compile-surface carrier after the harness
  could name profile-contract defects. It was a profile proposal quality issue:
  record predicates and property predicates needed stable joinable record shape,
  and starter examples needed matching arity.
- The clean retry is good mechanism evidence: generic profile-contract flags
  plus bounded retry can move an ugly procurement fixture from hold to pass
  without adding fixture language to the instrument.
- Do not publish this as a corpus score. It is a targeted repair/read of one
  known fixture. The right confirmation is a fresh ugly procurement-like or
  official-contract document that was not used to shape the repair.

Current affected-set read:

```text
Not a single fresh five-fixture rerun.

Pass on current targeted reads:
- court_ugly_001
- nlrb_ugly_001
- puc_ugly_001
- state_ag_ugly_001
- procurement_ugly_001
```

Validation:

```text
python -m pytest tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_file_batch.py tests\test_profile_bootstrap.py tests\test_semantic_ir_runtime.py -q
336 passed, 2 subtests passed

python -m py_compile scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_file_batch.py scripts\run_profile_bootstrap.py src\profile_bootstrap.py src\semantic_ir.py
pass

python scripts\audit_active_instrument_leakage.py --out-json C:\prethinker_tmp_archive\active_instrument_leakage_after_procurement_profile_contract_retry_20260526.json --out-md C:\prethinker_tmp_archive\active_instrument_leakage_after_procurement_profile_contract_retry_20260526.md
status: pass
forbidden hits: 0
warning hits: 10 existing agency/domain warnings
```

Next blocker:

Run the next fresh ugly batch as a thermometer before doing more mechanism work
on these same fixtures. The affected-set blockers now all have current targeted
passes; continuing to polish this set risks learning the fixture instead of the
instrument.

## Targeted Residue Repair 2026-05-28 - Case Identifier/Location Roster

Question:

`nlrb_ugly_001 q011` remained the cleanest visible residue after the
section-window overreach was removed. The row asked for all case identifiers,
citations, and geographic locations in an official decision-summary roster.

Read:

- This was not a raw source absence. The compile had admitted `case_id/1`,
  partial `case_location/2`, and source-record rows/surface mentions carrying
  the missing same-entry identifiers.
- The failed relationship was roster-shaped: identifiers appearing in the same
  admitted source-record entry needed to be grouped with the entry location
  without creating new durable `case_location/2` facts.
- The rejected path remains rejected: do not restore broad named-section-window
  support for this row. That caused trigger overreach and returned a section
  window instead of the requested identifier/location roster.

Harness change:

- Added `compiled_case_identifier_location_roster_support/3` as a query-only
  support surface.
- Activation is caged behind structured `query_intents` asking for a
  list/source-location shape whose target or constraint tokens include both an
  identifier/citation/case shape and a location/venue shape.
- Inputs are admitted `case_id/1`, admitted `case_location/2`, admitted
  `source_record_text_atom/2`, and admitted `source_record_surface_mention/3`.
  It does not read raw fixture files and does not write durable facts.

Replay:

```text
C:\prethinker_tmp_archive\nlrb_q011_case_roster_replay_20260528\

q011:
partial -> exact
response envelope: established
compatibility rows: 0
runtime load errors: 0
write proposal rows: 0
wallclock: ~42s on OpenRouter
```

Validation:

```text
python -m pytest tests\test_domain_bootstrap_qa.py -q
445 passed

python -m py_compile scripts\run_domain_bootstrap_qa.py
pass
```

Discipline note:

This is targeted mechanism evidence, not a new Batch 04 score. The next fresh
ugly batch should tell whether official-record roster grouping transfers
outside this NLRB row.

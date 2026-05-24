# Fresh Ugly Transfer Worksheet

Started: 2026-05-24

This worksheet tracks fresh public-document transfer batches used as a product
thermometer. These fixtures are not part of the native corpus and should not be
used as a scoreboard to polish individual rows. Use them to identify broad
mechanisms that should transfer to later messy documents.

## 2026-05-24 Batch 01

Dataset:

`datasets/real_world_transfer/fresh_ugly_public_20260524_01`

Run artifact archive:

`C:\prethinker_tmp_archive\fresh_ugly_public_20260524_01_run_20260524`

Fixtures:

| Domain | Fixtures | Rows |
| --- | ---: | ---: |
| FDA warning letters | 2 | 50 |
| NTSB reports | 2 | 50 |
| OSHA incident/enforcement records | 2 | 50 |
| SEC material-event filings | 2 | 50 |
| Total | 8 | 200 |

Local validation:

- All 8 fixtures have `source.md`, `source_original.txt`, `metadata.json`,
  `provenance.md`, `fixture_notes.md`, `qa.md`, `qa_questions.jsonl`,
  `oracle.jsonl`, and `anti_leakage_manifest.md`.
- Each fixture has 25 `qa_questions.jsonl` rows and 25 `oracle.jsonl` rows,
  keyed `q001` through `q025`.
- `tests/test_real_world_transfer_dataset.py`: `6 passed`.
- No source fixture-language leakage was found in the new batch source files.

Runner hygiene note:

- Incoming `qa.md` files contained authored answers and used `q001`-style
  markers, so the first QA invocation produced zero parsed question rows.
- The incoming files were preserved as `qa_authored_with_answers.md`.
- Canonical `qa.md` files were regenerated from `qa_questions.jsonl` as
  numbered, questions-only Markdown for the QA runner.
- `oracle.jsonl` remains the scoring-only answer key.

## Compile

Command conditions:

- Provider: OpenRouter-compatible API.
- Model: `qwen/qwen3.6-35b-a3b`.
- Lanes: `6`.
- Compile source: enabled.
- Plan passes: enabled, max `2`.
- Quality gate and retry-on-hold: enabled.

Summary:

```text
fixtures: 8
parsed OK: 8
candidate predicates: 183
compile admitted / skipped: 291 / 47
quality gate: 2 pass / 6 hold
diagnostic rejected flat-pass skips: 0
```

Gate decisions:

| Fixture | Gate | Rough | Main hold reason |
| --- | --- | ---: | --- |
| `fda_warning_ugly_001` | hold | 0.889 | source-authority/source-claim carrier delivery |
| `fda_warning_ugly_002` | hold | 0.806 | source-claim carrier delivery |
| `ntsb_aviation_ugly_001` | hold | 0.972 | vote-tally carrier false-looking pressure on `approved:23_51` |
| `ntsb_marine_ugly_001` | pass | 0.889 | n/a |
| `osha_incident_ugly_001` | hold | 0.704 | rough score and source-claim carrier delivery |
| `osha_incident_ugly_002` | hold | 0.722 | rough score and source-claim carrier delivery |
| `sec_material_event_ugly_001` | pass | 0.889 | n/a |
| `sec_material_event_ugly_002` | hold | 0.889 | status-state carrier partial delivery |

Read:

The compile gate is stricter than the QA score on this batch. That is useful,
not contradictory. It says the system can answer many row-shaped questions from
messy public records while the gate still sees incomplete compile-surface
coverage, especially around regulatory status, source-attributed claims, and
record-state carriers.

## QA R2

Command conditions:

- Provider: OpenRouter-compatible API.
- Model: `qwen/qwen3.6-35b-a3b`.
- Lanes: `6`.
- Cache: disabled.
- Compatibility adapter row limit: default `0`.

Summary:

```text
questions: 200
exact / partial / miss: 187 / 6 / 7
exact rate: 93.5%
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Per fixture:

| Fixture | Exact | Partial | Miss |
| --- | ---: | ---: | ---: |
| `fda_warning_ugly_001` | 22 | 1 | 2 |
| `fda_warning_ugly_002` | 24 | 1 | 0 |
| `ntsb_aviation_ugly_001` | 24 | 1 | 0 |
| `ntsb_marine_ugly_001` | 24 | 0 | 1 |
| `osha_incident_ugly_001` | 23 | 1 | 1 |
| `osha_incident_ugly_002` | 23 | 0 | 2 |
| `sec_material_event_ugly_001` | 25 | 0 | 0 |
| `sec_material_event_ugly_002` | 22 | 2 | 1 |

Failure surfaces:

```text
compile-surface gap: 6
hybrid-join gap: 4
query-surface gap: 3
not applicable/exact: 187
```

## Non-Exact Read

The 13 non-exact rows point at broad mechanisms:

- Source-record identifier retrieval: reference numbers, report IDs, and
  inspection-related identifiers exist in source-record rows but are not always
  surfaced as answerable identifier sets.
- Section/list hierarchy joins: FDA warning-letter sub-sections under a specific
  CFR violation were present as source text but not joined cleanly to the parent
  violation.
- Targeted elapsed-time arithmetic: the system can often retrieve the two dates
  or times, but sometimes calculates against the wrong pair or fails to compute
  a duration from recovered event times.
- Blank, unchecked, and visual table state: OSHA blank cells and SEC unchecked
  checkbox state need explicit preservation rather than inference from nearby
  text.
- Regulatory record-state carriers: status, latest event, contest state, and
  state of incorporation are not consistently emitted from cover-page/table
  surfaces.
- QA oracle caveat: at least one OSHA row may be testing a table-column
  interpretation where the source presentation needs another human read before
  treating it as architecture failure.

## Next Mechanisms

Priority order before another fresh batch:

1. Add query-side support for identifier/reference-number source-record rows.
2. Improve duration support for named event pairs and table date pairs.
3. Preserve blank/unchecked table and checkbox state as explicit record state.
4. Tighten regulatory/OSHA/SEC status carrier delivery without adding
   fixture-specific vocabulary.
5. Improve list-heading to parent-section joins for warning-letter violations.

Discipline:

- Do not count targeted replay as a new corpus result.
- Fix only mechanism-shaped failures with unit tests.
- Re-run this batch after mechanism repairs, then ask for another fresh ugly
  batch only if the repaired mechanisms need new transfer pressure.

## 2026-05-24 Identifier Support Repair

Mechanism:

- Added `source_record_identifier_set_support`, a query-only companion that
  collects identifier/reference-number rows from admitted `source_record_*`
  surfaces.
- It is triggered by identifier/reference-number questions and emits display
  values for common public-record labels such as `MARCS-CMS`, warning-letter
  numbers, report IDs, inspection numbers, investigation numbers, activity
  numbers, and FEI numbers.
- The companion does not write durable facts and does not use reference
  answers.

Validation:

```text
tests/test_source_surface_gap_audit.py: 16 passed
tests/test_real_world_transfer_dataset.py: 6 passed
```

Targeted mechanism replay:

```text
fixtures: fda_warning_ugly_001, osha_incident_ugly_001
questions: 50
exact / partial / miss: 47 / 0 / 3
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Comparison to batch QA R2 for these two fixtures:

| Fixture | Before | After | Read |
| --- | --- | --- | --- |
| `fda_warning_ugly_001` | 22 / 1 / 2 | 23 / 0 / 2 | One row improved; remaining misses are subsection hierarchy and reply/ATTN carrier. |
| `osha_incident_ugly_001` | 23 / 1 / 1 | 24 / 0 / 1 | Identifier row recovered; remaining miss is a table-column/oracle interpretation issue. |

Discipline note:

This is mechanism evidence only. It is not a new corpus score. The next corpus
score requires a full rerun of all eight fresh ugly fixtures after any further
general repairs land.

## 2026-05-24 Duration And Source-State Repair

Mechanisms:

- Added `source_record_date_pair_duration_support`, a query-only companion that
  computes elapsed days between same-row `source_record_field` date values using
  admitted `source_record_date_alias` rows.
- Updated the source-record ledger to preserve empty table cells as explicit
  `blank` values when a header exists.
- Updated the source-record ledger to preserve checkbox glyphs as
  `source_record_checkbox_state` and queryable source-record fields.
- Added `source_record_field_state_support`, a query-only companion that
  surfaces explicit `blank`, `checked`, and `unchecked` states from admitted
  source-record rows.

Validation:

```text
tests/test_domain_bootstrap_qa.py
tests/test_source_record_ledger.py
tests/test_source_surface_gap_audit.py
tests/test_real_world_transfer_dataset.py

312 passed
```

Targeted recompile:

Artifact archive:

`C:\prethinker_tmp_archive\fresh_ugly_public_20260524_01_mechanism_r2_20260524`

```text
fixtures: osha_incident_ugly_001, osha_incident_ugly_002, sec_material_event_ugly_002
parsed OK: 3 / 3
quality gate: 0 pass / 3 hold
compile admitted / skipped: 60 / 1
```

Gate read:

The targeted compiles still hold for broader source-claim/status-state carrier
reasons. The new source-record facts did land: OSHA blank `nature_of_injury`
cells are now preserved, and SEC unchecked checkbox rows are now explicit.

Targeted QA replay:

```text
fixtures: osha_incident_ugly_001, osha_incident_ugly_002, sec_material_event_ugly_002
questions: 75
exact / partial / miss: 73 / 2 / 0
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Comparison to batch QA R2 for these three fixtures:

| Fixture | Before | After | Read |
| --- | --- | --- | --- |
| `osha_incident_ugly_001` | 23 / 1 / 1 | 25 / 0 / 0 | Blank `nature_of_injury` preservation recovered the table-column row. |
| `osha_incident_ugly_002` | 23 / 0 / 2 | 24 / 1 / 0 | Date-pair duration and contest/latest-event evidence moved misses out of miss; citation count remains partial. |
| `sec_material_event_ugly_002` | 22 / 2 / 1 | 24 / 1 / 0 | Checkbox preservation recovered the emerging-growth-company row; one section-scope filing-date row remains judge-uncertain/partial. |

Discipline note:

This is still targeted mechanism evidence, not a replacement for the 200-row
fresh ugly score. If replayed across all eight fixtures with these mechanisms,
the arithmetic forecast from unchanged rows is approximately `192 / 5 / 3`
on 200 rows, or 96.0% exact, but that is a forecast until a full rerun is
actually performed.

## 2026-05-24 Direct Source Baseline Control

Purpose:

Claude raised the right calibration question: how much of the 93.5% fresh ugly
score comes from Prethinker's governed compile/query substrate, and how much is
just the base model reading `source.md` directly? I added a no-Prethinker
baseline runner to make that delta measurable.

Instrument:

- Script: `scripts/run_direct_source_qa_baseline.py`
- Dataset: `datasets/real_world_transfer/fresh_ugly_public_20260524_01`
- Model/provider: OpenRouter `qwen/qwen3.6-35b-a3b`
- Lanes: 6
- Input per row: the fixture `source.md` plus one `qa.md` question
- Excluded from answer prompt: compiled KB artifacts, query surfaces,
  `oracle.jsonl`, fixture notes, and answer-bearing authored QA
- Scoring: after-the-fact structured judge against `oracle.jsonl`

Result:

```text
questions: 200
direct-source exact / partial / miss: 165 / 30 / 5
direct-source exact rate: 82.5%
runtime/API error rows: 0
cache hits / misses: 2 / 198
```

Artifact archive:

`C:\prethinker_tmp_archive\direct_source_qa_baseline_fresh_ugly_20260524_01`

Comparison to the current fresh ugly Prethinker run:

```text
Prethinker QA R2:       187 / 6  / 7  = 93.5%
Direct-source control:  165 / 30 / 5  = 82.5%
Exact-rate delta: +11.0 percentage points for the governed pipeline
```

Per-fixture comparison:

| Fixture | Prethinker QA R2 | Direct source | Exact delta |
| --- | ---: | ---: | ---: |
| `fda_warning_ugly_001` | 22 / 1 / 2 | 18 / 6 / 1 | +4 |
| `fda_warning_ugly_002` | 24 / 1 / 0 | 18 / 6 / 1 | +6 |
| `ntsb_aviation_ugly_001` | 24 / 1 / 0 | 17 / 6 / 2 | +7 |
| `ntsb_marine_ugly_001` | 24 / 0 / 1 | 22 / 3 / 0 | +2 |
| `osha_incident_ugly_001` | 23 / 1 / 1 | 23 / 1 / 1 | 0 |
| `osha_incident_ugly_002` | 23 / 0 / 2 | 22 / 3 / 0 | +1 |
| `sec_material_event_ugly_001` | 25 / 0 / 0 | 23 / 2 / 0 | +2 |
| `sec_material_event_ugly_002` | 22 / 2 / 1 | 22 / 3 / 0 | 0 |

Read:

The control confirms that the 93.5% run is not just the base model's document
reading ability. The direct model is strong on these structurally regular public
documents, but it leaves many more rows in partial. Prethinker's gain is mostly
conversion of partial answers into exact answers through source-record
stability, deterministic surfaces, and governed query joins. The pipeline does
not dominate every miss cell, so this is a delta measurement rather than a claim
that every individual row is improved.

Discipline note:

This remains a project signal, not a leaderboard benchmark. The oracle was
authored in the same batch as the documents, the corpus is only two fixtures per
domain, and the direct-source baseline uses the same model as the pipeline. The
useful claim is narrower and stronger: on this 200-row fresh ugly batch,
Prethinker's governed path adds +11.0pp exact over direct source prompting with
the same model.

## 2026-05-24 Full R3 Rerun After Mechanism Repairs

Purpose:

The duration/source-state work produced a targeted forecast of roughly
`192 / 5 / 3` (96.0%) if unchanged rows held. This run recompiled and reran
all eight fixtures to replace that forecast with an actual corpus measurement.

Artifact archive:

`C:\prethinker_tmp_archive\fresh_ugly_public_20260524_01_r3_20260524`

Compile R3 conditions:

- Provider/model: OpenRouter `qwen/qwen3.6-35b-a3b`
- Lanes: 6
- Compile source: enabled
- Plan passes: enabled, max 2
- Source/entity, archival identifier, and source-record ledgers: enabled
- Quality gate and one bounded quality retry on hold: enabled

Compile R3 result:

```text
fixtures: 8
parsed OK: 8
compile admitted / skipped: 273 / 49
quality gate: 3 pass / 5 hold
diagnostic rejected flat-pass skips: 0
```

Gate movement from the original fresh ugly compile:

```text
original: 2 pass / 6 hold
R3:       3 pass / 5 hold
```

`sec_material_event_ugly_002` moved to gate pass after the status-state retry.
Remaining holds are still source-authority/source-claim carrier delivery and
the NTSB aviation vote-tally carrier signal.

QA R3 conditions:

- Provider/model: OpenRouter `qwen/qwen3.6-35b-a3b`
- Lanes: 6
- Cache: disabled
- Compatibility adapter row limit: default 0

QA R3 result:

```text
questions: 200
exact / partial / miss: 189 / 4 / 7
exact rate: 94.5%
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Comparison:

```text
QA R2 before mechanism repairs: 187 / 6 / 7 = 93.5%
QA R3 full rerun:              189 / 4 / 7 = 94.5%
Direct-source control:         165 / 30 / 5 = 82.5%
```

Per-fixture R3:

| Fixture | Exact | Partial | Miss |
| --- | ---: | ---: | ---: |
| `fda_warning_ugly_001` | 23 | 0 | 2 |
| `fda_warning_ugly_002` | 23 | 0 | 2 |
| `ntsb_aviation_ugly_001` | 24 | 1 | 0 |
| `ntsb_marine_ugly_001` | 24 | 0 | 1 |
| `osha_incident_ugly_001` | 25 | 0 | 0 |
| `osha_incident_ugly_002` | 23 | 2 | 0 |
| `sec_material_event_ugly_001` | 22 | 1 | 2 |
| `sec_material_event_ugly_002` | 25 | 0 | 0 |

Row movement versus R2:

- 21 rows changed verdict.
- 11 rows improved.
- 10 rows regressed.
- Net result: +2 exact, -2 partial, no miss-count change.

Recovered mechanisms that held in the full rerun:

- FDA warning-letter identifier set support recovered reference-number rows.
- FDA subsection support recovered the three sub-sections under the 21 CFR
  211.192 violation.
- OSHA blank field preservation recovered the blank `nature_of_injury` row.
- OSHA identifier aggregation recovered the distinct inspection-related
  identifier row.
- OSHA date-pair duration recovered the citation-to-abatement 13-day row.
- OSHA blank contest/latest-event support recovered the contested-status row.
- SEC checkbox preservation recovered the emerging-growth-company row.
- SEC role-start support recovered the new-CEO approximately-four-month row.

Regressed or still unstable surfaces:

- FDA CFR citation lists can be present in source-record text but unavailable
  as an ordered, queryable citation list.
- FDA signer/contact lines can be present in source-record context but missed
  by primary structural queries.
- NTSB marine departure date/time can be confused with casualty summary
  date/time when the query plan locks onto the summary table.
- OSHA source-value discrepancy rows can miss one table location for a repeated
  numeric value.
- SEC closing-date extension facts are not stable enough: the Agreement
  effective date and amendment filing/report dates can crowd out original/new
  closing-date surfaces and the derived 37-day duration.

Read:

The mechanisms transferred into a full rerun, but not as cleanly as the
targeted forecast. This is the right warning sign: the instrument is improving,
yet some residue moved between adjacent rows. The current measured fresh ugly
score is therefore `94.5%`, not the `96.0%` forecast. The next blocker is not
more row polishing on this batch; it is stabilizing reusable citation-list,
source-contact/signatory, and date-range/extension surfaces, then checking them
on fresh ugly documents.

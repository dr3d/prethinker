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

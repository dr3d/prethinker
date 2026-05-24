# Fresh Ugly Public Batch 02 Worksheet

Started: 2026-05-24

Purpose:

Track the second fresh public-document transfer batch as an independent product
thermometer. Batch 01 reached `193 / 3 / 4 = 96.5%` on a QA rerun over fixed
R3 compiles, but row churn remained visible. Batch 02 is meant to test transfer
of those mechanisms on new messy public documents, not to polish the old corpus.

Collection spec:

`docs/FRESH_UGLY_PUBLIC_BATCH_02_SPEC.md`

Expected incoming package:

`fresh_ugly_public_20260524_02.zip`

Expected dataset destination:

`datasets/real_world_transfer/fresh_ugly_public_20260524_02/`

## Batch Design

Requested shape:

```text
12 fixtures
25 QA rows per fixture
300 total QA rows
official public documents only
questions-only qa.md
answers isolated in oracle.jsonl and qa_authored_with_answers.md
```

Requested fixture IDs:

```text
fda_warning_ugly_003
fda_warning_ugly_004
fda_warning_ugly_005
ntsb_aviation_ugly_002
ntsb_marine_ugly_002
ntsb_surface_ugly_001
osha_incident_ugly_003
osha_incident_ugly_004
osha_incident_ugly_005
sec_material_event_ugly_003
sec_material_event_ugly_004
sec_material_event_ugly_005
```

Pressure targets:

- nested FDA violation subheadings and ordered CFR citation lists
- FDA inspection/response/letter chronology and extension-vs-substantive
  response distinctions
- NTSB event-time anchoring, elapsed time, similar-event fatality arithmetic,
  and probable-cause/contributing-factor separation
- OSHA close-conference/citation-issued date binding, repeated numeric values,
  and narrative/table joins
- SEC report/signature/event-date chronology, role-start-to-appointment
  duration, amendment deadline changes, and party/title/signatory rows

## Pre-Run Intake Checklist

Run this before compile:

- Confirm the zip has one top-level directory:
  `fresh_ugly_public_20260524_02/`.
- Confirm exactly 12 fixture folders.
- Confirm every fixture has:
  `source.md`, `source_original.txt`, `qa.md`, `qa_questions.jsonl`,
  `oracle.jsonl`, `metadata.json`, `provenance.md`, `fixture_notes.md`,
  `anti_leakage_manifest.md`, and `qa_authored_with_answers.md`.
- Confirm every fixture has exactly 25 questions and 25 oracle rows.
- Confirm `qa.md` is questions-only.
- Confirm `source.md` contains no answer-key, QA, or evaluation language.
- Confirm all sources are official public documents.
- Confirm no source URL duplicates an existing fixture.
- Move the accepted dataset under `datasets/real_world_transfer/`.
- Move the consumed zip and any staging leftovers from `tmp` into
  `/prethinker_tmp_archive` unless they are no longer useful.

## Success Criteria

Treat this as fresh transfer evidence, not a development-set score.

Clean:

```text
exact rate >= 95%
runtime load errors = 0
write proposal rows = 0
compatibility rows = 0
compile gates mostly clean or holds explainable by coverage discipline
row misses cluster into named mechanism surfaces
```

Strong but investigative:

```text
exact rate 90% to 95%
hygiene rows remain 0
misses are clustered and actionable
no sign of fixture-language leakage
```

Concerning:

```text
exact rate < 90%
any runtime/write/compatibility pressure
misses scatter randomly
gate behavior and QA behavior disagree without a clear explanation
```

## Planned Run Protocol

1. Intake and validate package shape.
2. Compile all 12 fixtures with the current standard compile path.
3. Record compile gate pass/hold per fixture before QA interpretation.
4. Run QA through OpenRouter with `qwen/qwen3.6-35b-a3b`, `6` lanes,
   no cache.
5. Archive compile and QA artifacts to `/prethinker_tmp_archive`.
6. Compare against Batch 01 only as broad transfer context, not as a direct
   fixture-by-fixture comparison.
7. Inspect non-exact rows and classify surfaces before making repairs.
8. If repairs are made, require a full rerun plus churn comparison before
   treating them as promoted.
9. Run or schedule a source-record-summary ablation on the first stable QA pass
   so Batch 02 can distinguish transferable product learning from Batch 01
   document-shape memory.

## Open Notes

The incoming dataset has landed under
`datasets/real_world_transfer/fresh_ugly_public_20260524_02/`.

## 2026-05-24 Intake

Dataset shape:

```text
fixtures: 12
questions per fixture: 25
total questions: 300
required fixture files: present
qa_questions.jsonl: questions only
oracle.jsonl: answer-bearing key isolated
source.md: no QA/oracle markers found
runtime fixture tests: added
```

Local intake repair:

- `sec_material_event_ugly_005/oracle.jsonl` had `q004` and `q005` swapped in
  file order. The rows were sorted by ID; the answer text was not changed.

Freshness caveat:

Two fixtures reuse source documents already present in earlier transfer
datasets:

| Fixture | Prior fixture/source |
| --- | --- |
| `fda_warning_ugly_005` | same FDA Medical Products Laboratories warning letter as Batch 01 `fda_warning_ugly_001` |
| `ntsb_marine_ugly_002` | same NTSB Baylor J. Tregre report as earlier NTSB pilots and Batch 01 `ntsb_marine_ugly_001` |

Therefore, Batch 02 should be reported two ways:

- all-12 operational score: `300` rows;
- fresh-only transfer slice: `10` fixtures / `250` rows, excluding
  `fda_warning_ugly_005` and `ntsb_marine_ugly_002`.

## 2026-05-24 Compile R1

Conditions:

```text
dataset root:
  datasets/real_world_transfer/fresh_ugly_public_20260524_02
compile out root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_02_r1_20260524\fresh_ugly_public_20260524_02_compile_r1
model:
  qwen/qwen3.6-35b-a3b via OpenRouter
lanes:
  6 requested
compile source:
  enabled
plan passes:
  enabled, max 2
source/entity, archival identifier, and source-record ledgers:
  enabled
quality gate and one retry on hold:
  enabled
```

Summary:

```text
fixtures: 12
parsed OK: 12
candidate predicates: 246
compile admitted / skipped: 351 / 67
diagnostic rejected flat-pass skips: 0
```

Per-fixture rough/admission read:

| Fixture | Admitted | Skipped | Rough | Read |
| --- | ---: | ---: | ---: | --- |
| `fda_warning_ugly_003` | 14 | 0 | 0.889 | source-authority/source-claim/status-state gaps |
| `fda_warning_ugly_004` | 34 | 0 | 0.833 | source-claim/status-state gaps |
| `fda_warning_ugly_005` | 44 | 0 | 0.889 | duplicate source; one poor/zero-yield pass |
| `ntsb_aviation_ugly_002` | 76 | 5 | 1.000 | cleanest compile by rough score |
| `ntsb_marine_ugly_002` | 41 | 32 | 0.889 | duplicate source; many skipped rows |
| `ntsb_surface_ugly_001` | 48 | 4 | 0.778 | source-authority/source-claim/status-state gaps |
| `osha_incident_ugly_003` | 0 | 11 | 0.694 | poor compile; zero admitted direct facts |
| `osha_incident_ugly_004` | 14 | 15 | 0.833 | source-claim/status-state gaps |
| `osha_incident_ugly_005` | 31 | 0 | 0.944 | source-claim/status-state gaps |
| `sec_material_event_ugly_003` | 23 | 0 | 0.944 | mostly clean |
| `sec_material_event_ugly_004` | 10 | 0 | 0.750 | thin direct compile surface |
| `sec_material_event_ugly_005` | 16 | 0 | 0.704 | thin direct compile surface |

Read:

This is a much harder compile batch than Batch 01. The SEC QA surface later
looks strong despite thin direct compile, but the compile gate is correctly
surfacing weak direct carriers. The most important blocker is
`osha_incident_ugly_003`, where the compiler parsed the document but admitted
zero direct facts, leaving QA to ride source-record rows and query support.

## 2026-05-24 QA R1 Baseline

Conditions:

```text
compile root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_02_r1_20260524\fresh_ugly_public_20260524_02_compile_r1
QA out root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_02_r1_20260524\fresh_ugly_public_20260524_02_qa_r1
model:
  qwen/qwen3.6-35b-a3b via OpenRouter
lanes:
  6 requested
cache:
  disabled
compatibility adapter row limit:
  0
evidence-bundle path:
  enabled for the main run
```

Initial main-run summary:

```text
questions: 300
exact / partial / miss: 264 / 6 / 24
not judged: 6
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Six rows were `not_judged` because the judge/failure-classifier prompt exceeded
OpenRouter context limits on very large source-record/table evidence. A narrow
replay without the evidence-bundle path resolved five of those rows:

```text
ntsb_aviation_ugly_002 q018:
  miss

osha_incident_ugly_004 q011,q018,q019,q022,q025:
  q011 exact
  q018 exact
  q019 still not_judged due context overflow
  q022 exact
  q025 exact
```

Adjusted baseline:

```text
all 12 fixtures:
  confirmed: 268 / 6 / 25 plus 1 not_judged
  conservative, counting remaining not_judged as miss:
    268 / 6 / 26 = 89.3%

fresh-only 10-fixture slice:
  confirmed: 225 / 5 / 19 plus 1 not_judged
  conservative, counting remaining not_judged as miss:
    225 / 5 / 20 = 90.0%

hygiene:
  runtime load errors: 0
  write proposal rows: 0
  compatibility rows: 0
```

Per-fixture main-run scores before the narrow replay:

| Fixture | Exact | Partial | Miss | Other |
| --- | ---: | ---: | ---: | ---: |
| `fda_warning_ugly_003` | 22 | 1 | 2 | 0 |
| `fda_warning_ugly_004` | 23 | 0 | 2 | 0 |
| `fda_warning_ugly_005` | 20 | 0 | 5 | 0 |
| `ntsb_aviation_ugly_002` | 18 | 1 | 5 | 1 |
| `ntsb_marine_ugly_002` | 23 | 1 | 1 | 0 |
| `ntsb_surface_ugly_001` | 21 | 1 | 3 | 0 |
| `osha_incident_ugly_003` | 21 | 0 | 4 | 0 |
| `osha_incident_ugly_004` | 20 | 0 | 0 | 5 |
| `osha_incident_ugly_005` | 23 | 1 | 1 | 0 |
| `sec_material_event_ugly_003` | 25 | 0 | 0 | 0 |
| `sec_material_event_ugly_004` | 23 | 1 | 1 | 0 |
| `sec_material_event_ugly_005` | 25 | 0 | 0 | 0 |

Read:

Batch 02 is the first strong counter-pressure after the Batch 01 R4 result. It
does not support a broad "95% on fresh ugly documents" claim. The clean
fresh-only slice is about `90%` under conservative scoring. That is still
strong for a harder, less-curated public-document batch, but it tells us the
Batch 01 `96.5%` was not fully transferable.

The misses are not random. The largest pressure points are:

- OSHA/FDA direct compile carriers for warning/citation tables;
- NTSB aviation toxicology, similar-event, and role/equipment detail joins;
- NTSB surface source-claim/status-state carriers;
- oversized OSHA table evidence producing context-overflow judge pressure;
- thin direct compile surfaces for some SEC filings, partly masked by strong
  source-record query behavior.

Next actions:

1. Archive these R1 compile/QA artifacts out of `tmp`.
2. Run the planned source-record-summary ablation on Batch 02, at least on the
   fresh-only 10-fixture slice.
3. Inspect non-exact clusters before implementing repairs.
4. Do not polish individual Batch 02 rows until the ablation tells us whether
   source-record summaries are transferring or carrying too much of the score.

## 2026-05-24 Source-Record Summary Ablation

Purpose:

Measure whether the current source-record summary layer transfers to Batch 02
or mainly carries Batch 01 document-shape memory.

Conditions:

```text
dataset root:
  datasets/real_world_transfer/fresh_ugly_public_20260524_02
compile root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_02_r1_20260524\fresh_ugly_public_20260524_02_compile_r1
QA out root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_02_r1_20260524\fresh_ugly_public_20260524_02_qa_r1_no_source_record_summaries_fresh10
fixtures:
  fresh-only 10-fixture slice
ablation:
  --disable-current-source-record-summaries
model:
  qwen/qwen3.6-35b-a3b via OpenRouter
lanes:
  6 requested
cache:
  disabled
compatibility adapter row limit:
  0
```

Raw ablation summary:

```text
questions: 250
exact / partial / miss: 212 / 6 / 27
not judged: 5
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

The five `not_judged` rows were the same large OSHA table/judge-context shape
seen in the baseline. A narrow replay without the evidence-bundle path resolved
them:

```text
osha_incident_ugly_004 q017,q019,q021,q024,q025:
  exact: 4
  miss: 1
```

Adjusted ablation:

```text
fresh-only 10-fixture slice:
  216 / 6 / 28 = 86.4%

baseline adjusted fresh-only slice:
  225 / 5 / 19 plus 1 not_judged
  conservative, counting remaining not_judged as miss:
    225 / 5 / 20 = 90.0%

delta versus conservative baseline:
  -9 exact, +1 partial, +8 miss
```

Row movement after replay normalization:

```text
changed rows: 25
improved rows under ablation: 8
regressed rows under ablation: 17
baseline exact -> non-exact: 16
baseline exact -> miss: 12
regressions with removed source-record support: 16
```

Read:

The source-record summary layer is materially load-bearing on Batch 02 as well
as Batch 01. That is important evidence that the layer is not merely a Batch 01
artifact. Removing it costs roughly nine exact rows on the fresh-only slice,
and nearly every regression lost a source-record support surface.

The layer is still not free. It improves some rows when removed, which means it
can perturb route/judge behavior. But the dominant signal is that it transfers:
source-record summaries recover real answer-bearing structure in unseen public
documents, especially CFR/citation lists, elapsed-time joins, blank/former-name
fields, repeated numeric table values, and source-overlap rows.

Engineering implication:

Do not remove the layer. Promote recurring transferable summaries into direct
compile surfaces where possible, and keep the ablation as a required control
for future fresh batches.

## 2026-05-24 ACH Overlay Probe

Question:

Is there any use in running ACH on the recent fresh ugly documents?

Answer:

Yes, but only as a sibling product-surface probe, not as part of QA scoring. The
best use is on reports with competing causal theories, severity contributors,
negative findings, and source-attributed explanations.

Probe:

```text
payload:
  experiments/ach_overlay/ntsb_surface_teutopolis_v1/ach_payload.json
artifact:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_02_r1_20260524\ntsb_surface_teutopolis_v1
source fixture:
  ntsb_surface_ugly_001
```

Result:

```text
hypotheses: 5
evidence rows: 6
judgments: 30
matrix complete: true
warnings: 0
top hypothesis: h_teen_unsafe_passing_evasive_loss_control
surviving hypotheses: 1
sensitivity rows: 0
```

Read:

The overlay separated initiating crash cause from injury-severity contributors.
The surviving top hypothesis matches the NTSB probable-cause theory: unsafe
passing by the teen driver caused evasive action, loss of control, and rollover.
The hazmat-response/classification evidence stayed useful, but as severity
evidence rather than as the initiating crash cause. That is exactly the product
role ACH should play: disciplined competing-hypothesis ranking over the same
source-grounded substrate, without contaminating the KB or QA score.

## 2026-05-24 Elapsed-Date Duration Support

Purpose:

Address the largest transferable residual pattern in Batch 02: elapsed calendar
day questions where the relevant dates are present in admitted source-record or
date facts, but query planning fails to bind the right pair or execute
`elapsed_days/3`.

Change:

Added a query-only deterministic support surface:

```text
source_record_elapsed_date_duration_support(StartDate, EndDate, ElapsedDays, Duration)
```

The support is current source-record summary work, not a durable KB fact and
not a retired compatibility adapter. It fires only for elapsed/duration/date
questions, requires admitted date evidence, computes calendar days locally, and
uses a minimum role-overlap threshold so weak same-document date matches do not
pollute the judge.

Unit coverage:

```text
tests/test_domain_bootstrap_qa.py:
  explicit source-backed dates in the question
  role-matched source-record fields
  section/context role stems such as publication/published and abated/abatement
  admitted date predicates such as inspection_period/3 and letter_date/2
```

Targeted replay artifacts:

```text
C:\prethinker_tmp_archive\fresh_ugly_public_20260524_02_duration_support_20260524
```

Targeted duration probe:

```text
Initial duration-heavy slice:
  fda_warning_ugly_003 q021,q022
  fda_warning_ugly_004 q021,q022
  ntsb_aviation_ugly_002 q008
  osha_incident_ugly_003 q007,q008,q009
  osha_incident_ugly_005 q009
  sec_material_event_ugly_004 q007

After first pass:
  6 exact / 0 partial / 4 miss

Clear recoveries:
  fda_warning_ugly_003 q021: 143 days
  fda_warning_ugly_004 q021: 42 days
  fda_warning_ugly_004 q022: 124 days
  ntsb_aviation_ugly_002 q008: 48 days
  osha_incident_ugly_003 q007: exact under replay
  sec_material_event_ugly_004 q007: 23 days
```

Refinement:

The first pass was too literal for OSHA rows where the question said
`abatement deadline` but the source row said `date by which violation must be
abated`, and where the publication date was carried by the row's section
context rather than the date field itself. Added context from
`source_record_label`, `source_record_section`, and `source_record_row_context`,
plus small morphology normalization for public-document date roles.

Post-refinement spot replay:

```text
osha_incident_ugly_003 q008: exact, 27 days
osha_incident_ugly_003 q009: exact, 9 days
sec_material_event_ugly_004 q007: exact, 23 days
```

Guard finding:

The guard replay exposed a real overreach risk on
`fda_warning_ugly_003 q024`: low-score context matching produced weak zero-day
or wrong-date support. The support surface now:

```text
filters zero-day rows unless the question asks for same-date/same-day pressure
requires context-match score >= 4 for inferred context-duration rows
```

After the threshold, `fda_warning_ugly_003 q024` receives no weak elapsed-date
support; the row remains a compile/query issue rather than being hidden by a
bad support surface.

Read:

This is a transfer-shaped mechanism, not a fixture polish. It recovers elapsed
duration rows across FDA, OSHA, SEC, and NTSB shapes, and the guard showed why
the threshold matters. The unresolved duration misses are mostly cases where
the needed date is not strongly enough represented as an admitted date
coordinate, or where the QA planner fails before query support can help.

## 2026-05-24 Residual After Elapsed-Date Support

Purpose:

Re-run the prior Batch 02 fresh-only non-exact rows after the elapsed-date
support landed, without treating targeted replay as a corpus score.

Artifacts:

```text
C:\prethinker_tmp_archive\fresh_ugly_public_20260524_02_residual_after_duration_20260524
```

Evidence-bundle residual replay:

```text
rows replayed: 29
exact / partial / miss: 14 / 2 / 12
not judged: 1
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

The remaining `not_judged` row was the same large OSHA violation-items table
shape seen earlier. A narrow no-evidence-bundle replay over
`osha_incident_ugly_004 q019,q022,q025` resolved the context pressure:

```text
q019: exact
q022: miss
q025: exact
```

Normalized residual-slice read:

```text
prior non-exact rows replayed: 29
exact / partial / miss: 16 / 2 / 11
projected full fresh-only slice, holding previously exact rows fixed:
  237 / 2 / 11 over 250 = 94.8%
```

This is only a residual-slice projection. It is useful mechanism evidence, not
a fresh Batch 02 benchmark claim.

Clear recoveries:

- FDA elapsed-duration rows on `fda_warning_ugly_003` and
  `fda_warning_ugly_004`;
- NTSB aviation maintenance elapsed duration;
- OSHA correction-method and date-duration rows;
- SEC event-date chronology and duration rows;
- oversized OSHA table rows `q019` and `q025` once judge context pressure was
  removed.

Remaining blocker taxonomy:

```text
source-ordered report lists and rosters:
  ntsb_aviation_ugly_002 q004,q012,q013,q018,q022
  ntsb_surface_ugly_001 q012,q013,q023

source-record table aggregation:
  osha_incident_ugly_004 q022

person/addressee role disambiguation:
  fda_warning_ugly_003 q001

duration planner variance or missing date admission:
  osha_incident_ugly_003 q007
  osha_incident_ugly_005 q009

section comparison:
  ntsb_aviation_ugly_002 q024
```

Read:

The elapsed-date support did what it was supposed to do. The next real
engineering blocker is no longer generic elapsed duration; it is preserving and
querying source-order structures from long public reports, plus one generic
table aggregation shape where a repeated maximum value must be counted and
checked against a column total.

Do not tune directly to NTSB section names. First audit whether the needed
source-record rows are admitted for each remaining report-list row. If the rows
are present, the proper mechanism is a generic source-section list/roster
support surface over admitted `source_record_*` rows. If the rows are absent,
the fix belongs in compile admission rather than QA query support.

## 2026-05-24 Scoped Numeric Frequency Support

Purpose:

Address the generic table-aggregation residual represented by
`osha_incident_ugly_004 q022`: a repeated maximum value must be counted inside a
row scope and verified against a summary total.

Change:

Added a query-only deterministic support surface:

```text
source_record_scoped_numeric_frequency_support(ScopeValue, NumericField, MaxValue, MaxValueCount)
```

Behavior:

- fires only on maximum/highest/largest questions that also ask for count,
  repeated rows/items, arithmetic, or totals;
- scopes candidate rows by admitted nonnumeric `source_record_field` values
  mentioned in the question;
- selects the repeated maximum numeric value inside that scope;
- computes count times value locally;
- checks the product against admitted total fields whose field names are also
  question-relevant;
- writes no durable fact and reads no raw source file.

Unit coverage:

```text
tests/test_domain_bootstrap_qa.py:
  repeated scoped maximum beats a larger out-of-scope numeric value
  count-times-value product matches an admitted total column value
```

Targeted replay:

```text
artifact:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_02_scoped_numeric_frequency_20260524

osha_incident_ugly_004 q022:
  exact
  runtime load errors: 0
  write proposal rows: 0
  compatibility rows: 0
```

Read:

This repairs the table aggregation residual without encoding OSHA, citation, or
fixture-specific names. The live replay found the repeated `165,514` maximum
inside the `willful` scoped rows, counted six rows, and matched
`6 * 165,514 = 993,084` to the admitted summary total field.

Residual-slice projection after substituting the validated `q022` replay:

```text
238 / 2 / 10 over 250 = 95.2%
```

Again, this is targeted residual-slice evidence. The honest benchmark remains
the next full fresh rerun.

## 2026-05-24 Source-Section List Detail Support

Audit:

The residual report-list rows split into two different causes:

- `ntsb_surface_ugly_001 q012,q013` had the needed casualty list rows admitted
  as same-section `source_record_row(..., list_row, ...)` plus
  `source_record_text_atom` rows. The earlier miss was empty query evidence,
  not missing source admission.
- several `ntsb_aviation_ugly_002` residuals had the relevant text in
  `source.md`, but no admitted source-record rows for the exact CAE
  configuration list, administrative roster, toxicology substances, or previous
  accident section. Those remain compile-admission issues, not query-support
  issues.

Change:

Added a query-only deterministic support surface:

```text
source_record_section_list_detail_support(Position, SourceRow, TextAtom)
```

Behavior:

- fires for questions asking to list/enumerate people, occupants, items,
  entries, configurations, violations, events, or dates;
- finds an admitted source-record header whose text/label/section overlaps the
  question;
- follows same-section `list_row` entries in source order;
- returns the list row text and display text with source-row coordinates;
- also runs in parse-failure fallback, so a malformed Semantic IR response does
  not erase already-admitted list evidence;
- writes no durable fact and reads no raw source file.

Unit coverage:

```text
tests/test_domain_bootstrap_qa.py:
  question-matched source header follows same-section list rows in source order
```

Targeted replay:

```text
artifact:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_02_source_section_list_detail_20260524

ntsb_surface_ugly_001 q012,q013:
  2 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  compatibility rows: 0
```

Read:

This is the cleanest kind of repair: the source rows were already admitted, but
the QA path returned empty evidence when the query planner failed. The new
support surface makes admitted source-order list rows visible without adding
domain-specific names.

Residual-slice projection after substituting the validated list-detail replay:

```text
240 / 2 / 8 over 250 = 96.0%
```

This is still targeted residual-slice evidence, not a fresh full Batch 02
benchmark. The next full fresh rerun is the claim-making run.

## 2026-05-24 Fresh-Only QA Rerun After Generic Supports

Purpose:

Test whether the targeted residual repairs transfer inside a full fresh-only
Batch 02 QA pass, including churn on previously exact rows.

Conditions:

```text
dataset root:
  datasets/real_world_transfer/fresh_ugly_public_20260524_02
compile root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_02_r1_20260524\fresh_ugly_public_20260524_02_compile_r1
QA out root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_02_fresh10_after_supports_20260524
fixtures:
  fresh-only 10-fixture slice
excluded duplicate-source fixtures:
  fda_warning_ugly_005
  ntsb_marine_ugly_002
model:
  qwen/qwen3.6-35b-a3b via OpenRouter
lanes:
  6 requested
cache:
  disabled
compatibility adapter row limit:
  0
evidence-bundle path:
  enabled for the main run
```

Raw full rerun:

```text
questions: 250
exact / partial / miss: 222 / 8 / 16
not judged: 4
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

The four `not_judged` rows were normalized with a narrow no-evidence-bundle
replay, plus one parse-failure row that also normalized under no-bundle replay:

```text
ntsb_surface_ugly_001 q025:
  miss

osha_incident_ugly_004 q015,q019,q025:
  exact: 3

osha_incident_ugly_005 q002:
  exact
```

Normalized full rerun:

```text
fresh-only 10-fixture slice:
  226 / 8 / 16 over 250 = 90.4%

baseline adjusted fresh-only slice:
  225 / 5 / 20 over 250 = 90.0%

delta:
  +1 exact
  +3 partial
  -4 miss
```

Churn:

```text
changed rows: 28
improved rows: 15
regressed rows: 13
baseline exact -> non-exact: 12
baseline non-exact -> exact: 13
```

Improved rows:

```text
fda_warning_ugly_003 q021: miss -> exact
fda_warning_ugly_003 q022: miss -> exact
fda_warning_ugly_004 q021: miss -> exact
fda_warning_ugly_004 q022: miss -> exact
ntsb_aviation_ugly_002 q008: miss -> exact
ntsb_aviation_ugly_002 q024: partial -> exact
ntsb_surface_ugly_001 q006: miss -> partial
ntsb_surface_ugly_001 q012: partial -> exact
ntsb_surface_ugly_001 q013: miss -> exact
ntsb_surface_ugly_001 q023: miss -> partial
osha_incident_ugly_003 q008: miss -> exact
osha_incident_ugly_003 q009: miss -> exact
osha_incident_ugly_004 q019: not_judged -> exact
sec_material_event_ugly_004 q006: partial -> exact
sec_material_event_ugly_004 q007: miss -> exact
```

Regressed rows:

```text
fda_warning_ugly_003 q001: partial -> miss
ntsb_surface_ugly_001 q007: exact -> miss
ntsb_surface_ugly_001 q025: exact -> miss
osha_incident_ugly_003 q006: exact -> miss
osha_incident_ugly_003 q024: exact -> partial
osha_incident_ugly_004 q021: exact -> miss
osha_incident_ugly_004 q023: exact -> miss
osha_incident_ugly_005 q006: exact -> partial
osha_incident_ugly_005 q014: exact -> partial
sec_material_event_ugly_003 q021: exact -> partial
sec_material_event_ugly_004 q008: exact -> miss
sec_material_event_ugly_004 q015: exact -> miss
sec_material_event_ugly_005 q003: exact -> partial
```

Support-surface interference check:

The newly added support predicates appeared only on exact rows in this rerun:

```text
source_record_elapsed_date_duration_support
source_record_scoped_numeric_frequency_support
source_record_section_list_detail_support
```

No non-exact row contained the new scoped numeric or source-section list support
surface. The regressions therefore do not look like direct trigger overreach
from the two latest generic supports. They look more like QA/evidence-plan
variance and remaining compile/query fragility.

Read:

The targeted residual projection was too optimistic. It measured mechanism
recoveries, not full-run stability. The full fresh-only rerun is nearly neutral
against the adjusted R1 baseline: `90.0% -> 90.4%`, with clean hygiene but
substantial churn.

This is still good product evidence in one sense: the pipeline stayed clean
under a harder full run. But it is not a 95% transfer claim. The next blocker is
stability and compile preservation, not adding broad new query support.

Next energy:

1. Inspect the 13 regressions for evidence-plan variance versus real support
   loss.
2. Add regression guards for previously exact Batch 02 rows before promoting
   more support surfaces.
3. Work the true compile-admission gaps, especially long-report source sections
   present in `source.md` but absent from admitted `source_record_text_atom`
   rows.
4. Treat the next fresh ugly batch as the product thermometer; do not polish
   Batch 02 toward a number.

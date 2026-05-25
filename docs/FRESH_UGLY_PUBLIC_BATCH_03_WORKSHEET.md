# Fresh Ugly Public Batch 03 Worksheet

Started: 2026-05-24

Purpose:

Track the third fresh public-document transfer batch as a product thermometer.
Batch 01 reached `96.5%` after several targeted support repairs. Batch 02
settled around `90%` on the harder fresh-only slice after full rerun churn.
Batch 03 is meant to test the current instrument against a new set of ugly
public documents rather than polishing either earlier batch.

Collection spec:

`docs/FRESH_UGLY_PUBLIC_BATCH_03_SPEC.md`

Dataset destination:

`datasets/real_world_transfer/fresh_ugly_public_20260524_03/`

## Batch Design

Actual shape:

```text
12 fixtures
25 QA rows per fixture
300 total QA rows
official/public-document sources
questions-only qa.md
answers in qa_authored_with_answers.md
machine oracle in oracle.jsonl
```

Fixture families:

```text
FDA:   fda_ugly_001, fda_ugly_002, fda_ugly_003
OSHA:  osha_ugly_001, osha_ugly_002, osha_ugly_003
Other: other_ugly_001, other_ugly_002, other_ugly_003
SEC:   sec_ugly_001, sec_ugly_002, sec_ugly_003
```

Intake validation:

```text
artifact:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_validation_20260525.md

status:
  pass

fixtures:
  12 / 12

issues:
  0

warnings:
  0

qa/authored/oracle counts:
  all fixtures 25 / 25 / 25
```

Local intake note:

The incoming fixture folders had valid `qa_authored_with_answers.md` files but
needed machine-readable `oracle.jsonl` rows for the QA runner. The oracle files
were generated mechanically from the authored answer files; the authored answer
text was preserved. The validator and Batch 03 spec now require `oracle.jsonl`
so future batches fail at intake instead of during inference.

## 2026-05-24 Compile R1

Conditions:

```text
dataset root:
  datasets/real_world_transfer/fresh_ugly_public_20260524_03
compile out root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_r1_20260524\fresh_ugly_public_20260524_03_compile_r1
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
candidate predicates: 239
compile admitted / skipped: 311 / 22
effective admitted / skipped: 311 / 22
diagnostic rejected flat-pass skips: 0
quality gate: hold
gate pass / hold: 2 / 10
```

Gate pass fixtures:

```text
other_ugly_003
sec_ugly_001
```

Per-fixture compile read:

| Fixture | Admitted | Skipped | Rough | Gate | Read |
| --- | ---: | ---: | ---: | --- | --- |
| `fda_ugly_001` | 49 | 13 | 0.778 | hold | source-authority ledger-only plus missing assessment claim carrier |
| `fda_ugly_002` | 47 | 0 | 0.889 | hold | source-claim carrier partially delivered |
| `fda_ugly_003` | 44 | 0 | 0.944 | hold | source-claim/documentation carrier undelivered |
| `osha_ugly_001` | 50 | 0 | 0.722 | hold | rough-score hold plus statement-claim carrier gap |
| `osha_ugly_002` | 14 | 0 | 0.833 | hold | statement/status carrier gaps |
| `osha_ugly_003` | 9 | 0 | 0.889 | hold | status-state and claim carrier gaps |
| `other_ugly_001` | 11 | 6 | 0.778 | hold | source-authority/source-claim delivery gaps |
| `other_ugly_002` | 30 | 2 | 0.778 | hold | source-authority ledger-only plus vote-tally carrier gap |
| `other_ugly_003` | 17 | 0 | 0.833 | pass | clean enough by current gate |
| `sec_ugly_001` | 9 | 0 | 0.861 | pass | clean enough by current gate |
| `sec_ugly_002` | 18 | 1 | 0.889 | hold | amendment source-claim carrier gap |
| `sec_ugly_003` | 13 | 0 | 0.722 | hold | rough-score hold |

Read:

The process was clean, but the gate did not like this corpus. Ten holds against
two passes says the direct compile surface is not preserving enough source
claim, status, authority, and section/detail structure for these public
documents. That matters even though QA later reaches `90%`, because the gate is
measuring a different and stricter coverage path.

## 2026-05-25 QA R1 Baseline

Conditions:

```text
compile root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_r1_20260524\fresh_ugly_public_20260524_03_compile_r1
QA out root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_r1_20260524\fresh_ugly_public_20260524_03_qa_r1
model:
  qwen/qwen3.6-35b-a3b via OpenRouter
lanes:
  6 requested
cache:
  disabled
compatibility adapter row limit:
  0
evidence-bundle path:
  enabled
```

Summary:

```text
questions: 300
exact / partial / miss: 270 / 14 / 16
exact rate: 90.0%
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Per-family score:

| Family | Exact | Partial | Miss | Exact rate |
| --- | ---: | ---: | ---: | ---: |
| FDA | 67 | 3 | 5 | 89.3% |
| OSHA | 68 | 2 | 5 | 90.7% |
| Other | 71 | 2 | 2 | 94.7% |
| SEC | 64 | 7 | 4 | 85.3% |

Per-fixture score:

| Fixture | Exact | Partial | Miss |
| --- | ---: | ---: | ---: |
| `fda_ugly_001` | 23 | 0 | 2 |
| `fda_ugly_002` | 21 | 3 | 1 |
| `fda_ugly_003` | 23 | 0 | 2 |
| `osha_ugly_001` | 25 | 0 | 0 |
| `osha_ugly_002` | 20 | 1 | 4 |
| `osha_ugly_003` | 23 | 1 | 1 |
| `other_ugly_001` | 24 | 1 | 0 |
| `other_ugly_002` | 24 | 0 | 1 |
| `other_ugly_003` | 23 | 1 | 1 |
| `sec_ugly_001` | 23 | 1 | 1 |
| `sec_ugly_002` | 20 | 3 | 2 |
| `sec_ugly_003` | 21 | 3 | 1 |

Non-exact failure surfaces:

```text
non-exact rows: 30
miss: 16
partial: 14

compile_surface_gap: 22
hybrid_join_gap: 5
query_surface_gap: 3
```

Representative residual shapes:

- source-coordinate and section-heading questions in FDA and OSHA records;
- formal address, signer, and contact blocks in FDA letters;
- enforcement-action and legal-body lists;
- attachment/link enumeration in agency releases;
- SEC dated-event lists, role histories, advisory-period dates, and dollar
  amount inventories;
- cross-context joins where a definition or status appears in one section and
  the question asks for its effect elsewhere.

Read:

Batch 03 is useful precisely because it is less flattering than Batch 01. It
lands at `90.0%`, cleanly, with no runtime/write/compatibility pressure. The
misses are clustered rather than scattered, and the dominant cluster is
compile-surface coverage. That argues against another wide query-side support
addition right now. The next improvement should make source-coordinate,
source-claim, status, authority, ordered-list, and formal-block structures more
consistently available to both the gate and QA path.

## Immediate Next Work

1. Treat Batch 03 as the current product thermometer, not as a polish target.
2. Run a source-record-summary ablation or targeted dependency audit before
   making repairs, so we know whether the `90.0%` is being carried by the
   source-record layer or by direct compile facts.
3. Audit the 22 compile-surface gaps for missing admission versus present-but-
   unqueried source rows.
4. Promote only generic compile-preservation mechanisms that appear across
   multiple families.
5. Use Batch 03 exact rows as regression guards before any support surface is
   promoted.

## 2026-05-25 Source-Record Summary Ablation

Purpose:

Measure whether Batch 03's baseline score depends on the current source-record
summary layer before making repairs.

Conditions:

```text
dataset root:
  datasets/real_world_transfer/fresh_ugly_public_20260524_03
compile root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_r1_20260524\fresh_ugly_public_20260524_03_compile_r1
QA out root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_r1_20260524\fresh_ugly_public_20260524_03_qa_r1_no_source_record_summaries
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

Ablation summary:

```text
questions: 300
baseline exact / partial / miss:
  270 / 14 / 16
ablation exact / partial / miss:
  264 / 18 / 18
delta:
  -6 exact, +4 partial, +2 miss
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Comparison:

```text
artifact:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_r1_20260524\fresh_ugly_public_20260524_03_source_record_summary_ablation_comparison.md

changed rows:
  25

improved rows:
  10

regressed rows:
  15

baseline exact -> non-exact:
  14

baseline exact -> miss:
  7

regression guard:
  fail
```

Read:

The source-record summary layer is still load-bearing on fresh public
documents. Removing it costs six exact rows on aggregate and causes fourteen
previously exact rows to become non-exact. The dominant removed support surface
on regressions is source-record question-overlap support, with contact-signatory,
citation-list, section-list-detail, elapsed-date, and clock-duration support
also appearing on a smaller number of changed rows.

The ablation also improved ten rows, so the layer is not free. It can perturb
route/judge behavior in some cases. But the net and row-guard result are clear:
do not remove or broadly weaken source-record summaries. The next useful work
is to make the direct compile surface preserve the answer-bearing coordinates
that are currently being recovered through source-record support, then keep the
ablation as a control for future changes.

Updated blocker read:

1. Compile preservation is the main Batch 03 blocker: source-claim, status,
   authority, formal contact/signature blocks, ordered lists, and section
   coordinates need stronger direct carriers.
2. Source-record summaries are transferring, but should be treated as a bridge
   and guardrail, not the final product surface.
3. Any repair promoted from Batch 03 should require both the normal QA rerun and
   a regression-guard comparison against the current 300-row baseline.

## 2026-05-25 QA Failure ACH Probe

Question:

Can ACH help QA without changing answers or KB state?

Probe:

```text
script:
  scripts/run_qa_failure_ach_probe.py

default artifact:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_r1_20260524\fresh_ugly_public_20260524_03_qa_failure_ach_probe.md

with existing failure label as caged evidence:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_r1_20260524\fresh_ugly_public_20260524_03_qa_failure_ach_probe_with_label.md
```

The probe does not call an LLM, mutate verdicts, or write facts. It builds a
fixed ACH matrix for each non-exact row over four patch-location hypotheses:

```text
h_compile_preservation
h_query_route
h_join_computation
h_answer_assessment
```

Default result, not using the existing failure-surface label as evidence:

```text
rows: 30
h_compile_preservation: 2
h_join_computation: 20
h_join_computation,h_query_route: 8
agreement with existing failure-surface classifier: 6 / 30
```

With the existing failure-surface label included as one caged evidence row:

```text
rows: 30
h_compile_preservation: 1
h_query_route: 1
h_join_computation: 20
h_join_computation,h_query_route: 8
agreement with existing failure-surface classifier: 9 / 30
```

Read:

ACH did not improve QA by answering anything. It improved the research signal.
The existing failure-surface classifier called `22 / 30` rows
`compile_surface_gap`, but the ACH triage says many of those rows already have
nonempty source-record or direct query evidence and look more like source-
coordinate joining, list/order/group assembly, duration arithmetic, or route
selection failures.

That does not make the compile-surface read wrong. It means the phrase is
describing one layer: the direct compile surface lacks a convenient reusable
carrier. The immediate QA patch location may still be join/query mechanics over
already-admitted source coordinates. The next useful inspection should focus on
rows where the classifier says `compile_surface_gap` but ACH ranks
`h_join_computation`.

## 2026-05-25 ACH-Guided Source-Coordinate Cages

Question:

Can the ACH disagreement signal lead to narrow deterministic support without
turning Batch 03 into a polish target?

Edits:

```text
source_record_preceding_heading_support:
  sorts admitted source-record heading-like rows by source line and returns the
  heading immediately before a named target heading.

source_record_elapsed_date_duration_support:
  extended to handle "X and Y differ by how many days" wording when both date
  roles are present in admitted source-record/direct date surfaces.

source_record_named_section_window_support:
  matches a named source section from the question and returns the bounded
  admitted source-record rows until the next heading-like row.

source_record_quote_heading_locator_support:
  locates a quoted source phrase in admitted source-record text and returns the
  nearest preceding heading-like source row.

source_record_contact_signatory_support:
  expanded public `.gov` email parsing so admitted media-contact rows such as
  DOL contacts can render address displays without a fixture-specific rule.
```

All of these are query-only support rows. They read admitted
`source_record_*` rows already present in the runtime, write no durable facts,
and do not use fixture names or fixture vocabulary.

Focused tests:

```text
python -m pytest tests\test_domain_bootstrap_qa.py -q

284 passed
```

Full test suite after the Batch 03 R2 run and worksheet update:

```text
python -m pytest -q

1717 passed, 2 subtests passed
```

Leakage check:

```text
python scripts\audit_active_instrument_leakage.py

status: pass
forbidden hits: 0
warning hits: 10 existing agency/domain-token warnings
scope: active runtime scripts and src only; docs/tests/datasets excluded
```

Targeted mechanism replay:

```text
artifact root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_join_cages_20260525\targeted_rerun_r2

rows:
  fda_ugly_001 q013: exact via source_record_named_section_window_support
  fda_ugly_003 q006: exact via source_record_quote_heading_locator_support
  osha_ugly_002 q015: exact via source_record_contact_signatory_support

targeted total:
  3 / 0 / 0

hygiene:
  runtime load errors: 0
  write proposal rows: 0
  compatibility rows: 0
```

The earlier focused replay for `fda_ugly_001 q007/q020` also stayed clean:

```text
fda_ugly_001 q007:
  miss -> exact via source_record_preceding_heading_support

fda_ugly_001 q020:
  miss -> exact via source_record_elapsed_date_duration_support

targeted total:
  2 / 0 / 0
```

Context-overflow normalization:

```text
artifact:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_join_cages_20260525\normalize_not_judged\fda_ugly_001_q025_no_bundle

row:
  fda_ugly_001 q025

result:
  exact
```

Read: the prior `not_judged` row was a judge-context overflow from the bulky
evidence-bundle path, not a factual miss.

Full Batch 03 R2 rerun:

```text
artifact root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_join_cages_20260525\full_batch03_rerun_r2

summary:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_join_cages_20260525\full_batch03_rerun_r2_summary.md

comparison:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_join_cages_20260525\full_batch03_rerun_r2_comparison.md

conditions:
  model: qwen/qwen3.6-35b-a3b via OpenRouter
  lanes: 6
  cache: disabled
  evidence-bundle path: enabled
  compatibility adapter row limit: 0
```

Result:

```text
questions: 300
exact / partial / miss: 273 / 11 / 16
exact rate: 91.0%
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Comparison with QA R1 baseline:

```text
baseline:
  270 / 14 / 16 = 90.0%

candidate:
  273 / 11 / 16 = 91.0%

delta:
  +3 exact, -3 partial, 0 miss

row changes:
  changed: 18
  improved: 10
  regressed: 8
  baseline exact -> non-exact: 7
  baseline exact -> miss: 6

regressions with added support surfaces:
  0

aggregate status:
  promotable

regression guard:
  fail
```

Per-fixture R2 score:

| Fixture | Exact | Partial | Miss |
| --- | ---: | ---: | ---: |
| `fda_ugly_001` | 25 | 0 | 0 |
| `fda_ugly_002` | 22 | 1 | 2 |
| `fda_ugly_003` | 24 | 0 | 1 |
| `osha_ugly_001` | 25 | 0 | 0 |
| `osha_ugly_002` | 22 | 1 | 2 |
| `osha_ugly_003` | 23 | 1 | 1 |
| `other_ugly_001` | 24 | 1 | 0 |
| `other_ugly_002` | 24 | 0 | 1 |
| `other_ugly_003` | 24 | 1 | 0 |
| `sec_ugly_001` | 22 | 1 | 2 |
| `sec_ugly_002` | 20 | 3 | 2 |
| `sec_ugly_003` | 18 | 2 | 5 |

Direct support-surface wins in the comparison:

```text
fda_ugly_001 q007:
  source_record_preceding_heading_support

fda_ugly_001 q020:
  source_record_elapsed_date_duration_support

fda_ugly_003 q006:
  source_record_quote_heading_locator_support
```

Rows improved without added support surfaces also moved, which is normal
no-cache route/judge variance. The important guardrail is the inverse: no
regressed row had an added support surface. That means this batch of support
surfaces does not look like trigger overreach. The remaining guard failure is
mostly route/judge/answer-assessment churn over dense SEC-style rows, not a
new support pollution problem.

Current blocker read:

1. Batch 03 is back in the 90s cleanly at `91.0%`, but this is not a clean
   promotion because the exact-row regression guard still fails.
2. The new cages are generic and transfer-shaped, with no fixture names,
   no fixture-specific vocabulary, and no durable KB writes.
3. The highest-value next blocker is SEC dense-document stability: biography
   paragraphs, exhibits, dollar/percentage inventories, restrictive covenants,
   signature-block inconsistencies, and conditional transition/separation terms.
4. The next intervention should target one generic SEC-shaped source-record
   support family at a time, then replay both the named miss rows and the
   previously exact SEC guard rows before another full Batch 03 sweep.

## 2026-05-25 SEC Exhibit-Index Cage

Question:

Can one SEC-dense blocker be repaired as a generic public-filing table/list
surface without introducing fixture vocabulary or broad helper overreach?

Edit:

```text
source_record_exhibit_index_support:
  query-only source-record support that collects admitted exhibit index rows
  from table/list source records, handles both row-label style entries such as
  exhibit_10_1 and field-table style entries such as exhibit_no = v_10_1, and
  cross-checks filed/furnished/embedded status from admitted source text or the
  exhibit description field.
```

The support reads only admitted `source_record_row`, `source_record_text_atom`,
and `source_record_field` rows. It writes no durable facts and does not use
fixture names, QA row IDs, answer strings, company names, or document-specific
constants as trigger branches.

Focused tests:

```text
python -m pytest tests\test_domain_bootstrap_qa.py -q

288 passed
```

No-LLM compile probes:

```text
sec_ugly_001 q014 shape:
  field-table exhibit_no rows with values v_10_1, v_99_1, v_104

sec_ugly_003 q014 shape:
  row-label exhibit_10_1, exhibit_99_1, exhibit_104 rows

both shapes:
  source_record_exhibit_index_support returns the three exhibit rows plus a
  summary row
```

Targeted replay:

```text
artifact root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_exhibit_index_20260525

rows:
  sec_ugly_001 q014: exact
  sec_ugly_002 q014: exact
  sec_ugly_003 q014: exact

targeted total:
  3 / 0 / 0

hygiene:
  runtime load errors: 0
  write proposal rows: 0
  compatibility rows: 0
```

Read:

This is a clean mechanism result, not a new Batch 03 score. It repairs the
`sec_ugly_003 q014` miss while keeping the two already-exact SEC exhibit rows
exact in targeted replay. The first guard replay exposed the important shape
variant: some public filings render exhibit indexes as `exhibit_no` fields
rather than `exhibit_*` labels. The fix now covers both generic renderings.

Next blocker:

The remaining SEC-dense rows are not another exhibit problem. The next work
should inspect the biography/employment-history rows (`sec_ugly_003 q012/q013`
and the related `sec_ugly_001 q013`) and decide whether there is a generic
source-record biographical-history surface, or whether that belongs in direct
compile preservation instead of another query-only cage.

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

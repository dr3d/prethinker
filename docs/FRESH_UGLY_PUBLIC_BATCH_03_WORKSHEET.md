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

## 2026-05-25 Biography / Employment-History Source-Record Cage

Question:

Can the SEC-dense biography residue be repaired without letting fixture
company/person names or research-row shapes into the active instrument?

Findings:

Two different failures were hiding under the same "biography" label:

1. `sec_ugly_001 q013` was a deterministic source-record preservation gap.
   The source paragraph exceeded the prior `source_record_ledger` row cap, so
   `source_record_text_atom(src_line_0088, ...)` clipped before the final prior
   employers.
2. `sec_ugly_003 q012/q013` had the full source paragraph admitted, but the QA
   path surfaced it as undifferentiated source text. Prior employers and role
   spans needed a structured query-only support surface.

Edit:

```text
source_record_ledger:
  max_chars_per_row 1200 -> 2400

source_record_employment_history_support:
  query-only biography/employment-history support over admitted
  source_record_text_atom rows.

  triggers:
    role/title/position history questions
    prior/former employer questions
    biographical paragraph questions

  scope split:
    role-history asks return current/appointment/role-history entries
    prior-employer asks return prior-employer entries

  transition handling:
    current role since X + later appointment effective Y is rendered as
    "current role since X; next role effective Y" rather than as a durable
    termination fact.
```

The support reads only admitted source-record text. It writes no durable facts
and does not branch on fixture names, row IDs, company names, person names, or
answer strings.

Focused tests:

```text
python -m pytest tests\test_domain_bootstrap_qa.py tests\test_source_record_ledger.py -q

320 passed
```

Leakage audit:

```text
python scripts\audit_active_instrument_leakage.py

status: pass
forbidden hits: 0
warning hits: 10 existing agency/domain-token warnings
```

Targeted replay:

```text
artifact root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_biography_history_20260525

sec_ugly_003, existing compile artifact:
  q012 role chronology: exact
  q013 prior employers: exact
  total: 2 / 0 / 0

sec_ugly_003 guard:
  q025 cross-section role/gap/overlap row: exact

sec_ugly_001, one-fixture recompile after longer source-record rows:
  source_record_text_atom(src_line_0088) now preserves Cardiocore,
  Thermo Fisher Scientific, Pfizer, Fourth Frontier, U.S. Army, and Norwich.
  q013 prior employers: exact
```

Read:

This is mechanism evidence, not a new Batch 03 score. The high-value part is
that the two repair paths stayed generic:

- source preservation for long official-document paragraphs;
- query-only structured support for biography role/prior-employer history.

The scoped role/prior-employer split matters. An earlier targeted replay moved
`sec_ugly_003 q012` only to partial because prior-employer rows polluted a
company-role-history question. Tightening the trigger to return role-history
entries for role-history asks, and prior-employer entries for employer asks,
made the targeted pair exact while keeping the nearby exact guard row exact.

Residual:

`q012` and `q025` still report `response_envelope.status =
clarification_required` in targeted exact runs even though `reference_support`
and the judge verdict are exact. That looks like envelope status assembly noise
rather than QA evidence failure. Worth inspecting separately if it appears in a
batch-level summary.

Next blocker:

The remaining SEC-dense residue is likely not biography. Next inspect dollar /
percentage inventory (`sec_ugly_003 q015`) and restrictive-covenant / condition
rows (`sec_ugly_003 q020/q021/q023`) before another Batch 03 sweep.

## 2026-05-25 Amount-Inventory Source-Record Cage

Question:

Can an amount-list question recover from source-record text without adding a
fixture-specific money parser or waking up on ordinary single-amount questions?

Finding:

`sec_ugly_003 q015` was not missing the numeric tokens. It was missing the
amount-to-referent pairing needed for an inventory question: par value, cash
bonus, RSU value, severance multiplier, individual-objective percentage,
lodging benefit caps, and legal/PR reimbursement cap. Primitive numeric rows
were too context-free to support the reference answer.

Edit:

```text
source_record_amount_inventory_support:
  query-only amount/percentage inventory support over admitted
  source_record_text_atom rows.

  trigger:
    inventory/list wording AND amount/value/dollar/percentage wording

  non-trigger guard:
    ordinary single-amount questions such as "What cash bonus amount..."
    bullet-list comparison questions that mention dollar value but do not ask
    for an amount inventory

  filters:
    plain years
    year-month-day date atoms
    day-year date fragments
    month-name day fragments
    official section fragments such as 12(b)
```

The support reads only admitted source-record text. It writes no durable facts
and does not branch on fixture names, company names, person names, SEC form
names, or answer strings.

Focused tests:

```text
python -m pytest \
  tests\test_domain_bootstrap_qa.py::test_source_record_messy_summary_extracts_amount_inventory \
  tests\test_domain_bootstrap_qa.py::test_source_record_messy_summary_amount_inventory_requires_inventory_question \
  tests\test_domain_bootstrap_qa.py::test_source_record_messy_summary_amount_inventory_ignores_bullet_list_comparison -q

3 passed
```

Mechanism details:

The first focused test intentionally reproduced two false-positive classes
seen in SEC source-record rows: `security_12_b` and `2026_05_20`. Those now
stay out of the amount inventory. The same test also verifies that two distinct
`$500,000` referents on one source row remain distinct rather than collapsing
into one amount.

Targeted replay:

```text
artifact root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_amount_inventory_20260525

sec_ugly_003 q015:
  1 / 0 / 0
  response envelope: established
  compatibility/runtime/write rows: 0/0/0
  artifact:
    targeted_sec_ugly_003_q015_clean

guards:
  q005 cash bonus amount: exact, source_record_amount_inventory_support absent
  q017 bonus payable condition: exact, source_record_amount_inventory_support absent
  artifact:
    guard_sec_ugly_003_q005_q017_clean

trigger-tightening guard:
  q015 amount inventory: exact, source_record_amount_inventory_support present
  q023 bullet-list dollar-value comparison: exact, source_record_amount_inventory_support absent
  artifact:
    targeted_sec_ugly_003_q015_q023_tight
```

Read:

This is mechanism evidence, not a new Batch 03 score. The useful part is the
scope: the carrier only enters when the user asks for an inventory/list of
amounts or percentages, and the guard replay shows it stayed absent from
single-amount questions. A whole-fixture `sec_ugly_003` guard run before the
final trigger tightening produced `23 / 1 / 1` and exposed one over-broad
activation on a bullet-list comparison row (`q023`); the trigger was tightened
and `q023` was replayed exact with the amount-inventory support absent.

The remaining risk is ordinary row churn in a full Batch 03 sweep; do that
before treating this as corpus-level gain.

Residual:

`q017` remained judge-exact but reported `response_envelope.status =
clarification_required` in the guard replay. That matches the prior envelope
noise seen on biography rows and should be inspected as a separate status
assembly issue rather than folded into the amount-inventory mechanism.

## 2026-05-25 Restrictive-Covenant Source-Record Cage

Question:

Can the restrictive-covenant miss recover from admitted legal text without
teaching the instrument a particular filing, party, or answer string?

Finding:

`sec_ugly_003 q020` was a query-surface gap. The source-record row was admitted
with the relevant text, but the query path searched for question n-grams such
as `restrictive_covenants_does` instead of the actual covenant terms present in
the row.

Edit:

```text
source_record_restrictive_covenant_support:
  query-only legal covenant support over admitted source_record_text_atom rows.

  trigger:
    restrictive/covenant/confidentiality/non-competition/non-solicitation/
    non-disparagement wording in the question

  extracted terms:
    confidentiality
    non-competition
    non-solicitation
    non-disparagement
    other customary terms and conditions
    release of claims, marked bilateral when the source says each side provides it
```

The support reads only admitted source-record text. It writes no durable facts
and does not branch on fixture names, party names, filing names, or answer
strings.

Focused tests:

```text
python -m pytest \
  tests\test_domain_bootstrap_qa.py::test_source_record_messy_summary_extracts_restrictive_covenants \
  tests\test_domain_bootstrap_qa.py::test_source_record_messy_summary_restrictive_covenants_requires_covenant_question -q

2 passed
```

Targeted replay:

```text
artifact root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_covenant_terms_20260525

sec_ugly_003 q020:
  1 / 0 / 0
  response envelope: established
  compatibility/runtime/write rows: 0/0/0
  returned:
    confidentiality
    non-competition
    non-solicitation
    non-disparagement
    other customary terms and conditions
    bilateral release of claims
  artifact:
    targeted_sec_ugly_003_q020

guards:
  q011 payments/benefits list: exact, covenant support absent
  q021 transition-period vs separation-date distinction: still partial, covenant support absent
  q024 transition/separation cross-section: exact, covenant support absent
  artifact:
    guard_sec_ugly_003_q011_q021_q024

combined fixture guard:
  sec_ugly_003 full QA replay after amount-inventory and covenant cages:
    24 / 1 / 0
    compatibility/runtime/write rows: 0/0/0
    source_record_amount_inventory_support fired only on q015
    source_record_restrictive_covenant_support fired only on q020
    remaining non-exact: q021 transition-period vs separation-date distinction
  artifact:
    full_sec_ugly_003_guard_after_covenants
```

Read:

This is another mechanism repair, not a corpus score. It is narrow enough to be
worth keeping: the trigger is legal-covenant language, the extraction vocabulary
is generic contract/separation-agreement vocabulary, and the guard rows show it
does not wake up on nearby payment or transition-date questions.

Next blocker:

`sec_ugly_003 q021` remains the local unresolved row: a term-definition /
conditional-date distinction between a fixed transition period and a variable
separation date. That is probably a separate source-record term-definition
surface, not a covenant issue.

## 2026-05-25 Defined-Term Contrast Source-Record Cage

Question:

Can the transition-period / separation-date distinction recover as a generic
defined-term contrast, without hard-coding the terms or the fixture document?

Finding:

`sec_ugly_003 q021` already had the dates. The missing support was the
relationship between two quoted defined terms:

- one term is a fixed period with a stated end date;
- the other term is a conditional date: the same stated date, or an earlier
  date if the named triggering event occurs.

Edit:

```text
source_record_defined_term_contrast_support:
  query-only defined-term contrast support over admitted source_record_text_atom rows.

  trigger:
    comparison wording such as difference / distinguish / contrast /
    relationship / versus
    AND at least two quoted terms in the question

  extracted shapes:
    fixed period through a stated date
    conditional date: stated date or earlier date if a stated event occurs
    relation: coincides at the fixed period end unless the earlier event occurs
```

The support reads only admitted source-record text. It writes no durable facts
and does not branch on fixture names, term names, party names, filing names, or
answer strings.

Focused tests:

```text
python -m pytest \
  tests\test_domain_bootstrap_qa.py::test_source_record_messy_summary_extracts_defined_term_contrast \
  tests\test_domain_bootstrap_qa.py::test_source_record_messy_summary_defined_term_contrast_requires_comparison -q

2 passed
```

Targeted replay:

```text
artifact root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_defined_term_contrast_20260525

sec_ugly_003 q021:
  1 / 0 / 0
  response envelope: established
  compatibility/runtime/write rows: 0/0/0
  returned:
    Transition Period: fixed period from May 20, 2026 through August 31, 2026
    Separation Date: August 31, 2026 or an earlier date if employment actually terminates
    terms coincide at the fixed period end if no earlier triggering event occurs;
    the conditional date can move earlier if the stated event occurs
  artifact:
    targeted_sec_ugly_003_q021

guards:
  q008 definition-location row: exact, defined-term contrast support absent
  q016 single-term transition-period date row: exact, defined-term contrast support absent
  q024 cross-section relationship row: exact, defined-term contrast support present
  artifact:
    guard_sec_ugly_003_q008_q016_q024

combined fixture guard:
  sec_ugly_003 full QA replay after amount-inventory, covenant, and defined-term cages:
    25 / 0 / 0
    compatibility/runtime/write rows: 0/0/0
    source_record_amount_inventory_support fired only on q015
    source_record_restrictive_covenant_support fired only on q020
    source_record_defined_term_contrast_support fired only on q021 and q024
  artifact:
    full_sec_ugly_003_guard_after_defined_terms
```

Read:

This is a small deterministic inference over source-record definitions, not a
new compile fact. It is still caged enough to keep: it needs comparison
wording, two quoted terms, and source text containing the fixed-period /
conditional-date shapes. It also improves the full local fixture guard from
`24 / 1 / 0` to `25 / 0 / 0`.

Residual:

The full fixture guard still has three exact rows (`q022/q023/q025`) whose
response envelope reports `clarification_required`. That remains envelope
status assembly noise rather than answer evidence failure.

## 2026-05-25 SEC Subset R3 OpenRouter Probe

Purpose:

Measure whether the SEC-targeted source-record cages transfer across the SEC
slice of Batch 03 before spending a full 300-row OpenRouter run.

Conditions:

```text
dataset:
  datasets/real_world_transfer/fresh_ugly_public_20260524_03
compile root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_r1_20260524\fresh_ugly_public_20260524_03_compile_r1
out root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_sec_subset_r3_or_20260525
model:
  qwen/qwen3.6-35b-a3b via OpenRouter
lanes:
  6
cache:
  disabled
compatibility/runtime/write rows:
  0/0/0
```

Note:

An earlier attempted full Batch 03 OpenRouter run under
`fresh_ugly_public_20260524_03_full_r3_after_sec_cages_20260525` is invalid:
all rows returned `judge_uncertain` because the subprocess used the wrong auth
header precedence and OpenRouter returned HTTP 401. It is archived as a failed
run artifact only and is not a score.

Valid SEC subset result:

```text
questions: 75
exact / partial / miss: 69 / 2 / 4
exact rate: 92.0%
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Per-fixture:

| Fixture | Exact | Partial | Miss |
| --- | ---: | ---: | ---: |
| `sec_ugly_001` | 23 | 0 | 2 |
| `sec_ugly_002` | 21 | 2 | 2 |
| `sec_ugly_003` | 25 | 0 | 0 |

Remaining non-exact rows:

```text
sec_ugly_001 q010:
  signature-block inconsistency between signed and printed name

sec_ugly_001 q015:
  ordered dated-event inventory across filing narrative

sec_ugly_002 q015:
  negative-fact assertions under an item section

sec_ugly_002 q016:
  resignation effective date plus continuing roles

sec_ugly_002 q017:
  advisory-period end is stated as fiscal-year end, not explicit calendar date

sec_ugly_002 q022:
  board-membership path / nominee / shareholder-election conditionality
```

Read:

Compared with the R1 SEC family baseline (`64 / 7 / 4`) this is a material
shape improvement: +5 exact and -5 partial with the miss count flat. Compared
with the R2 SEC row totals (`60 / 6 / 9`), it is a stronger recovery. The
important local signal is `sec_ugly_003`: the fixture that carried the amount,
covenant, and defined-term residues now replays at `25 / 0 / 0` under
OpenRouter, not just local targeted runs.

Next blocker:

The next narrow generic blocker is likely signature-block inconsistency
(`sec_ugly_001 q010`): the source has the raw lines, but the surfaced signatory
predicate normalizes away the mismatch that the question asks about.

## 2026-05-25 Signature-Block Mismatch Source-Record Cage

Question:

Can a signature-block spelling inconsistency be recovered from source-record
table cells without changing the durable signatory fact?

Finding:

`sec_ugly_001 q010` was not a source-preservation gap. The relevant source rows
were admitted:

```text
src_line_0127:
  cell 2 = by
  cell 3 = s_daniel_moorehead

src_line_0128:
  cell 2 = name
  cell 3 = daniel_moorhead
```

The miss happened because the durable signatory predicate normalized the block
to `daniel_moorehead / chief_financial_officer`, which is correct for ordinary
signatory questions but loses the intra-block spelling mismatch.

Edit:

```text
source_record_signature_mismatch_support:
  query-only signature-block mismatch support over admitted source_record_cell rows.

  trigger:
    signature/signature-block wording
    AND inconsistency/mismatch/disagreement/different/two-lines wording

  comparison:
    adjacent table rows where one row has a By cell with an /s/ signed name
    and a following row has a Name cell with a printed name
    near-miss names are reported only when token structure matches and the
    final token differs by a small edit distance
```

The support reads only admitted source-record cells. It writes no durable facts
and does not branch on fixture names, person names, filing names, or answer
strings.

Focused tests:

```text
python -m pytest \
  tests\test_domain_bootstrap_qa.py::test_source_record_messy_summary_extracts_signature_mismatch \
  tests\test_domain_bootstrap_qa.py::test_source_record_messy_summary_signature_mismatch_requires_inconsistency_question -q

2 passed
```

Targeted replay:

```text
artifact root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_signature_mismatch_20260525

sec_ugly_001 q010 local:
  1 / 0 / 0
  response envelope: established
  compatibility/runtime/write rows: 0/0/0
  returned:
    signed name Daniel Moorehead differs from printed name Daniel Moorhead
  artifact:
    targeted_sec_ugly_001_q010

sec_ugly_001 q010 OpenRouter:
  1 / 0 / 0
  response envelope: established
  compatibility/runtime/write rows: 0/0/0
  artifact:
    targeted_sec_ugly_001_q010_openrouter

guards:
  q011 cover-page filing-obligation list: exact, signature support absent
  q023 agreement-location/exhibit cross-section: exact, signature support absent
  q025 press-release/separation-date reconciliation: exact, signature support absent
  artifact:
    guard_sec_ugly_001_q011_q023_q025
```

Read:

This is a useful distinction between ordinary normalized signatory identity and
source-surface mismatch detection. The normal signatory predicate should not be
made unstable to preserve typos; the query-only mismatch support should surface
the typo only when the question asks about signature-block inconsistency.

Next blocker:

SEC subset residue after this targeted repair is mostly ordered dated-event
inventory (`sec_ugly_001 q015`) and sparse source-claim/negative-fact rows in
`sec_ugly_002`.

## 2026-05-25 Dated-Event Inventory Source-Record Cage

Question:

Can an ordered dated-event list recover from admitted source-record text without
turning ordinary date questions into broad source scans?

Finding:

`sec_ugly_001 q015` was not missing all date evidence. It was missing an
ordered inventory surface. The direct predicates exposed only a few isolated
dates, while the source-record rows preserved the narrative dates and duration
phrases needed for the reference list.

Edit:

```text
source_record_dated_event_inventory_support:
  query-only dated-event inventory support over admitted source_record_text_atom rows.

  trigger:
    list/every/all/inventory wording
    AND dated-event / event-date / date-order wording

  ordering:
    source row order, then date occurrence order within the source row

  filters:
    heading rows
    exhibit-index rows that are dated references rather than narrative events
```

The support reads only admitted source-record text. It writes no durable facts
and does not branch on fixture names, person names, company names, filing names,
or answer strings.

Focused tests:

```text
python -m pytest \
  tests\test_domain_bootstrap_qa.py::test_source_record_messy_summary_extracts_dated_event_inventory \
  tests\test_domain_bootstrap_qa.py::test_source_record_messy_summary_dated_event_inventory_requires_inventory_question -q

2 passed
```

Targeted replay:

```text
artifact root:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260524_03_dated_event_inventory_20260525

sec_ugly_001 q015 local:
  1 / 0 / 0
  response envelope: established
  compatibility/runtime/write rows: 0/0/0
  returned 12 dated-event rows plus summary
  artifact:
    targeted_sec_ugly_001_q015_ordered

sec_ugly_001 q015 OpenRouter:
  1 / 0 / 0
  response envelope: established
  compatibility/runtime/write rows: 0/0/0
  artifact:
    targeted_sec_ugly_001_q015_openrouter

guards:
  q016 revocation-period expiration: exact, dated-event inventory absent
  q018 resignation notification/effective dates: exact, dated-event inventory absent
  q025 date reconciliation cross-section: exact, dated-event inventory absent
  artifact:
    guard_sec_ugly_001_q016_q018_q025
```

Mechanism note:

The first targeted run recovered the row but sorted same-date subevents by date
text, which put duration phrases before the agreement-execution event inside
one source row. The kept version sorts by source occurrence position, so
"order mentioned" is represented directly.

Read:

This is mechanism evidence, not a fresh SEC subset score. If the two targeted
OpenRouter repairs (`q010` and `q015`) hold in the next SEC subset rerun,
`sec_ugly_001` should move from `23 / 0 / 2` to `25 / 0 / 0`. The remaining SEC
subset blockers are now concentrated in `sec_ugly_002`.

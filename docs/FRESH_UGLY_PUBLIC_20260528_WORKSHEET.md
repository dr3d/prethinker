# Fresh Ugly Public 20260528 Worksheet

Purpose:

Measure transfer on `fresh_ugly_public_20260528_01`, an eight-fixture public
English official-document batch built from the May 28 request spec. This is a
fresh thermometer, not a native stamp and not a tuning target.

Discipline:

- Validate package shape before inference spending.
- Do not repair mid-run.
- Keep compile gate tiers separate from QA accuracy.
- Keep compatibility rows, runtime load errors, and QA write proposals at zero.
- Treat oracle/source wording warnings as adjudication context, not as license
  to teach fixture words to the instrument.
- Record results here; bulky artifacts stay in `C:\prethinker_tmp_archive`.

## Intake - 2026-05-28

Dataset:

```text
datasets/real_world_transfer/fresh_ugly_public_20260528_01
```

Fixtures:

```text
court_order_ugly_002
fda_warning_ugly_006
labor_board_ugly_002
osha_incident_ugly_006
procurement_contract_ugly_002
puc_order_ugly_002
sec_material_event_ugly_006
state_ag_settlement_ugly_002
```

Package validation:

```text
python scripts\validate_fresh_ugly_batch.py datasets\real_world_transfer\fresh_ugly_public_20260528_01 ^
  --expected-documents 8 ^
  --expected-questions 25 ^
  --package-profile extended
```

Result:

```text
status: pass
fixtures: 8 / 8
issues: 0
warnings: 39
questions: 25 per fixture
oracle rows: 25 per fixture
```

Validation artifact:

```text
C:\prethinker_tmp_archive\fresh_ugly_public_20260528_01_validation_20260528_r2.md
```

Validator note:

The incoming `qa.md` files use plain `q001. Question?` lines. The validator
already accepted numbered and bold-Q forms, so it was extended to accept plain
qid-prefixed question lines. This changes intake parsing only; it does not
touch compile, QA, prompts, or scoring.

QA parser note:

The same plain `q001. Question?` form was added to the QA markdown parser after
an initial QA attempt produced `0` parsed questions per fixture and therefore
made no model calls. This is also file-format parsing only.

Active-instrument leakage audit after the validator fix:

```text
forbidden hits: 0
warning hits: 0
```

## Planned R1 Run

Compile and QA should use the normal OpenRouter measured lane, six lanes, and
the current fresh ugly Batch 04 protocol. Do not repair during R1.

## R1 Compile - 2026-05-28

Command:

```text
python scripts\run_domain_bootstrap_file_batch.py ... --lanes 6 --quality-gate --quality-retry-on-hold --quality-retry-max-attempts 1
```

Artifacts:

```text
C:\prethinker_tmp_archive\fresh_ugly_public_20260528_01_r1_20260528\compile_r1_summary.md
C:\prethinker_tmp_archive\fresh_ugly_public_20260528_01_r1_20260528\compile_r1_summary.json
```

Compile result:

```text
provider family: openrouter
model: qwen/qwen3.6-35b-a3b
lanes: 6
fixtures: 8
parsed OK: 8
candidate predicates: 163
compile admitted / skipped: 743 / 206
effective admitted / skipped: 743 / 142
diagnostic rejected flat-pass skips: 64
```

Compile quality gate:

```text
old pass / hold: 2 / 6
blocking / diagnostic / advisory holds: 4 / 6 / 0
minimum rough score: 0.775
maximum risk count: 5
```

Pass:

```text
court_order_ugly_002
osha_incident_ugly_006
```

Blocking holds:

```text
fda_warning_ugly_006
labor_board_ugly_002
puc_order_ugly_002
state_ag_settlement_ugly_002
```

Diagnostic-only holds:

```text
procurement_contract_ugly_002
sec_material_event_ugly_006
```

Read:

The compile gate still sees source-authority/source-claim delivery pressure,
especially around regulatory/legal document shapes. This is not release-clean
compile coverage, even if QA later scores well.

## R1 QA - 2026-05-29 UTC

First QA attempt:

```text
qa_r1
questions: 0
```

Cause: file parser did not yet accept plain `q001. Question?` lines. No model
spend occurred. The parser was fixed and tested before the real QA run.

Real QA run:

```text
C:\prethinker_tmp_archive\fresh_ugly_public_20260528_01_r1_20260528\qa_r1b_summary.md
C:\prethinker_tmp_archive\fresh_ugly_public_20260528_01_r1_20260528\qa_r1b_summary.json
```

Result:

```text
questions: 200
exact / partial / miss: 197 / 3 / 0
exact rate: 98.5%
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Per fixture:

| Fixture | Exact | Partial | Miss |
| --- | ---: | ---: | ---: |
| `court_order_ugly_002` | 24 | 1 | 0 |
| `fda_warning_ugly_006` | 25 | 0 | 0 |
| `labor_board_ugly_002` | 25 | 0 | 0 |
| `osha_incident_ugly_006` | 25 | 0 | 0 |
| `procurement_contract_ugly_002` | 25 | 0 | 0 |
| `puc_order_ugly_002` | 25 | 0 | 0 |
| `sec_material_event_ugly_006` | 23 | 2 | 0 |
| `state_ag_settlement_ugly_002` | 25 | 0 | 0 |

Residue adjudication:

```text
C:\prethinker_tmp_archive\fresh_ugly_public_20260528_01_r1_20260528\qa_r1b_residue_adjudication.md
```

```text
residue rows: 3
classifications:
  query_planning_gap: 1
  source_support_adjudication_needed: 2
surfaces:
  compile_surface_gap: 1
  hybrid_join_gap: 1
  query_surface_gap: 1
hygiene:
  compatibility rows: 0
  runtime load errors: 0
  write proposal rows: 0
```

Residue rows:

| Fixture | Row | Verdict | Surface | Note |
| --- | --- | --- | --- | --- |
| `court_order_ugly_002` | `q010` | partial | hybrid_join_gap | chronology ordering needed a better multi-hop join across termination, LOC sustain, Board dismissal, and Federal Circuit affirmance |
| `sec_material_event_ugly_006` | `q006` | partial | query_surface_gap | CEO identity found, age was present in source text but query path tried an invalid `memberchk/2` support shape |
| `sec_material_event_ugly_006` | `q015` | partial | compile_surface_gap | officer-tenure facts for CFO and board-member roles were not durable enough, though source text support existed |

Provider metadata:

The run used OpenRouter without explicit provider pinning. Artifact-level
metadata records mixed backend providers across calls (`AkashML`, `Ambient`,
`SiliconFlow`, `Parasail`, `WandB`, plus a small unknown remainder). Treat this
as current-product hosted-path evidence, not single-provider variance evidence.

Read:

This is the strongest fresh ugly English public-document transfer result so
far: `197 / 3 / 0` on 200 rows with clean hygiene. The important caveat is that
compile-gate pressure did not disappear; QA was excellent while the compile
gate remained meaningfully noisy, including four blocking-tier holds. That
means the product-facing answer path is strong, but the compiler coverage lens
is still telling us where release-grade evidence surfaces are thinner than the
QA score alone suggests.

## R2 Targeted Query-Template Normalization Replay

Question:

Did the three R1 partials reflect a generic query-template normalization gap, or
were they one-off corpus quirks?

Mechanism change:

- Evidence-bundle query execution already repaired source-record
  `memberchk(...)` filters over `source_record_text_atom/2`.
- It now applies the same query-only repair to admitted source display rows such
  as `source_record_text_display/2`.
- It also strips a rule-shaped evidence-bundle template head when the LLM emits
  `head :- body` where the executable query is the body.
- This is not fixture-language handling. It does not parse the user utterance,
  add durable facts, or inspect raw source. It only normalizes LLM-proposed
  query templates against admitted KB rows.

Guard tests:

```text
python -m pytest tests\test_domain_bootstrap_qa.py -k "evidence_bundle_plan_repairs_source_display_memberchk_filter or evidence_bundle_plan_repairs_rule_like_source_display_substring_filter or evidence_bundle_plan_repairs_source_text_memberchk_filter" -q
```

Result:

```text
3 passed
```

Targeted replay:

```text
C:\prethinker_tmp_archive\fresh_ugly_public_20260528_01_r1_20260528\qa_r2_targeted_display_filter_summary.md
C:\prethinker_tmp_archive\fresh_ugly_public_20260528_01_r1_20260528\qa_r1b_vs_r2_targeted_display_filter_diff.md
```

Scope:

- `court_order_ugly_002`
- `sec_material_event_ugly_006`

Result:

```text
baseline targeted slice: 47 / 3 / 0
candidate targeted slice: 50 / 0 / 0
delta: +3 exact, -3 partial, 0 miss
changed rows: 3
improved rows: 3
regressed rows: 0
baseline exact -> non-exact: 0
compatibility rows: 0
runtime load errors: 0
write proposal rows: 0
regression guard: pass
```

Changed rows:

| Fixture | Row | Movement | Surface Change |
| --- | --- | --- | --- |
| `court_order_ugly_002` | `q010` | partial -> exact | `hybrid_join_gap` -> `not_applicable` |
| `sec_material_event_ugly_006` | `q006` | partial -> exact | `query_surface_gap` -> `not_applicable` |
| `sec_material_event_ugly_006` | `q015` | partial -> exact | `compile_surface_gap` -> `not_applicable` |

Read:

This is mechanism evidence, not a new 200-row corpus claim. The repair is
promotable on the affected 50-row slice because it recovered all known residue
with no exact-row churn. The next honest confirmation is either a full May 28
R2 QA replay across all eight fixtures, or leaving this as locked mechanism
evidence and waiting for the next fresh ugly batch to test transfer.

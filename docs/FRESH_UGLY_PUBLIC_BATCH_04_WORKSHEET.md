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

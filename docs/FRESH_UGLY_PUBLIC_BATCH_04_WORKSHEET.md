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
$env:OPENROUTER_API_KEY = ((Get-Content .env.local | Where-Object { $_ -match '^OPENROUTER_API_KEY=' }) -replace '^OPENROUTER_API_KEY=', '')

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

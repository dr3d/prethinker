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

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

## Open Notes

The next useful action is waiting for the incoming zip, then running the intake
check before any compile. Do not start repair work from Batch 02 until the first
full run gives a baseline.

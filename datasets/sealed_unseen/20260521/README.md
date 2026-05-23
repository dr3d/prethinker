# 2026-05-21 Sealed Unseen Batch

This batch preserves the four sealed unseen fixtures used for the May 22, 2026
authored-transfer measurement.

## Fixtures

- `civic_hearing_correction_packet`
- `clinical_recall_source_packet`
- `grant_exception_vote_matrix`
- `lease_amendment_status_register`

## Measured Result

The May 22, 2026 sealed unseen transfer result was:

```text
152 exact / 1 partial / 6 miss
160 judged rows
95.0% exact
0 compatibility rows
0 runtime load errors
0 QA write proposal rows
```

Run artifacts and the retired worksheet remain in the archive under
`C:\prethinker_tmp_archive`; this directory keeps the durable fixture inputs in
the repo.

## File Shape

Each fixture keeps the source document, QA questions, and reference oracle:

- `source.md`: source document for compilation.
- `qa.md`: questions only.
- `oracle.jsonl`: reference answers for after-the-fact scoring.
- `qa_questions.jsonl` and `qa_battery.json`: structured QA convenience files.
- `README.md`, notes, and progress files: intake and audit context.

The staged manifest in this directory intentionally preserves the original
`tmp\...` intake paths as provenance. The canonical durable location is this
`datasets/sealed_unseen/20260521` directory.

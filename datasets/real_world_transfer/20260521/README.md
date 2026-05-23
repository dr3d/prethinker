# 2026-05-21 Real-World Transfer Batch

This batch preserves the four externally sourced real-world fixtures used for
the May 22, 2026 transfer spotcheck.

## Fixtures

- `cpsc_recall_polaris_rzr200_2023`: CPSC recall notice for Polaris RZR 200
  youth recreational off-road vehicles.
- `fda_recall_wiers_farm_2024`: FDA recall notice for Wiers Farm produce.
- `federal_register_flra_fsip_2024`: Federal Register / FLRA / FSIP notice.
- `ntsb_marine_carol_jean_2023`: NTSB marine accident report for Carol Jean.

## Measured Result

The latest fixture-level real-world spotcheck result was:

```text
160 exact / 0 partial / 0 miss
4 / 4 compile gates clean
0 compatibility rows
0 runtime load errors
0 QA write proposal rows
```

Run artifacts remain in the archive under
`C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522`; this directory
keeps the durable fixture inputs in the repo.

## File Shape

Each fixture keeps the source document, QA questions, and reference oracle:

- `source.md`: source document for compilation.
- `qa.md`: questions only.
- `oracle.jsonl`: reference answers for after-the-fact scoring.
- `qa_questions.jsonl` and `qa_battery.json`: structured QA convenience files.
- `README.md`, notes, and progress files: intake and audit context.

The staged manifest in this directory intentionally preserves the original
`tmp\...` intake paths as provenance. The canonical durable location is this
`datasets/real_world_transfer/20260521` directory.

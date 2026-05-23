# 2026-05-23 Real-World Transfer Pilot

This batch preserves a rough one-document NTSB aviation pilot fixture promoted from an incoming tmp package on May 23, 2026.

## Fixtures

- `ntsb_aviation_001`: NTSB aviation final report for a Colusa, California helicopter accident involving loss of control in flight.

## Status

This is a shakedown fixture, not a polished transfer thermometer. The incoming package described a two-document pilot, but only `ntsb_aviation_001` was complete. The canonical copy keeps the useful document, separates questions from scoring answers, and records the caveats locally.

## Measured Shakedown

The May 23, 2026 shakedown compile parsed successfully but the compile quality gate held on source-claim/source-authority delivery:

```text
1 / 1 fixtures parsed
36 candidate predicates
81 compile admitted / 0 skipped
rough score 0.889
quality gate: 0 passed / 1 held
```

After a general source-record routing repair, the final QA replay was:

```text
25 exact / 0 partial / 0 miss
0 compatibility rows
0 runtime load errors
0 QA write proposal rows
```

The run artifacts are archived under `C:\prethinker_tmp_archive\ntsb_pilot_shakedown_20260523`.

## Harness Use

Use the batch scripts with an explicit dataset root and fixture selection:

```powershell
python scripts/run_domain_bootstrap_file_batch.py --dataset-root datasets/real_world_transfer/20260523 --fixture ntsb_aviation_001
python scripts/run_domain_bootstrap_qa_batch.py --dataset-root datasets/real_world_transfer/20260523 --fixture ntsb_aviation_001
```

Do not feed `oracle.jsonl`, `qa_battery.json`, or other answer-bearing files into source compilation.

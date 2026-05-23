# Sealed Unseen Fixtures

This dataset tree holds project-authored sealed fixtures that were not part of
the maintained native `datasets/story_worlds` development corpus when measured.

These fixtures are transfer evidence, but they are not the same kind of
evidence as externally sourced real-world documents. Keep them separate from
both the native story-world baseline and the real-world transfer fixtures.

## Batches

- `20260521`: four sealed unseen fixtures promoted from the archived tmp package
  `C:\prethinker_tmp_archive\tmp_unload_20260521_2106\incoming_unseen_20260521_staged`.

## Harness Use

Use the batch scripts with an explicit dataset root:

```powershell
python scripts\run_domain_bootstrap_file_batch.py --dataset-root datasets\sealed_unseen\20260521
python scripts\run_domain_bootstrap_qa_batch.py --dataset-root datasets\sealed_unseen\20260521
```

Do not feed `oracle.jsonl`, `qa_battery.json`, `oracle_authored.jsonl`, or
other answer-bearing files into source compilation.

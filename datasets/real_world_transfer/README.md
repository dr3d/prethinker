# Real-World Transfer Fixtures

This dataset tree holds externally sourced real-world fixtures that should be
kept separate from the maintained native `datasets/story_worlds` corpus.

These fixtures are transfer evidence. They are useful for checking whether the
compile instrument handles public, messy source documents outside the story
world development set, but they should not be folded into the native 56-fixture
baseline.

## Batches

- `20260521`: four externally sourced real-world fixtures promoted from the
  archived tmp package
  `C:\prethinker_tmp_archive\tmp_lean_markdown_docs_cleanup_20260522\unseen_real_document_fixture_batch_20260521_cleaned_staged`.
- `20260523`: one rough NTSB aviation pilot fixture promoted from an incoming
  tmp package. This is useful for harness shakedown, but it is not a polished
  transfer thermometer batch.
- `20260523_ntsb_pilot_2doc`: two externally sourced NTSB pilot fixtures
  promoted from the corrected May 23 intake package. The package followed the
  source/QA/oracle separation rule; the canonical copy normalizes QA formatting
  and fetches the missing original PDFs.

## Harness Use

Use the batch scripts with an explicit dataset root:

```powershell
python scripts\run_domain_bootstrap_file_batch.py --dataset-root datasets\real_world_transfer\20260521
python scripts\run_domain_bootstrap_qa_batch.py --dataset-root datasets\real_world_transfer\20260521
```

Do not feed `oracle.jsonl`, `qa_battery.json`, `oracle_authored.jsonl`, or
other answer-bearing files into source compilation.

# Anti-leakage manifest — ntsb_marine_ugly_001

- The collector did not inspect any Prethinker internals, repository contents, prior fixture batches, or evaluation harness while preparing this fixture.
- This document (NTSB Marine Investigation Report MIR-25-21, case DCA24FM038, casualty of the towing vessel *Baylor J. Tregre*, May 13, 2024) is not from any prior Prethinker fixture batch. It was retrieved fresh from ntsb.gov on 2026-05-24 specifically for batch `fresh_ugly_public_20260524_01`.
- All 25 QA pairs in `qa.md` / `oracle.jsonl` / `qa_questions.jsonl` were written from the public NTSB source PDF only. No outside knowledge, no AI summary, no inference beyond what is explicitly recoverable from `source.md`.
- No part of the source document was synthesized. `source.md` is a faithful Markdown transcription of the official NTSB report. Section headings, table values, dates, times, party lists, casualty summary fields, and probable-cause language preserve the original wording.
- No QA hints, answer keys, or fixture-style language were embedded into `source.md`.

## Local runner hygiene

The canonical `qa.md` in this repository is questions-only. The answer-bearing incoming QA file is retained as `qa_authored_with_answers.md` and must be treated like `oracle.jsonl`: scoring-only, never compile or answer context.

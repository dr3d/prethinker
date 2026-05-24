# Anti-leakage manifest — fda_warning_ugly_001

- The collector did not inspect any Prethinker internals, repository contents, prior fixture batches, or evaluation harness while preparing this fixture.
- This document (FDA Warning Letter MARCS-CMS 721916 / 320-26-61 to Medical Products Laboratories, Inc., dated April 9, 2026) is not from any prior Prethinker fixture batch. It was retrieved fresh from fda.gov on 2026-05-24 specifically for batch `fresh_ugly_public_20260524_01`.
- All 25 QA pairs in `qa.md` / `oracle.jsonl` / `qa_questions.jsonl` were written from the public FDA warning letter only. No outside knowledge, no AI summary, no inference beyond what is explicitly recoverable from `source.md`.
- No part of the source document was synthesized. `source.md` is a faithful Markdown rendering of the published warning letter. Recipient block, issuing office block, CFR citations, signature block, footnote text, and (b)(4) redactions preserve the original wording.
- No QA hints, answer keys, or fixture-style language were embedded into `source.md`.

## Local runner hygiene

The canonical `qa.md` in this repository is questions-only. The answer-bearing incoming QA file is retained as `qa_authored_with_answers.md` and must be treated like `oracle.jsonl`: scoring-only, never compile or answer context.

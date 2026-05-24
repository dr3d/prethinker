# Anti-leakage manifest — fda_warning_ugly_002

- The collector did not inspect any Prethinker internals, repository contents, prior fixture batches, or evaluation harness while preparing this fixture.
- This document (FDA Warning Letter MARCS-CMS 722113 / CMS #722113 to Nupack Inc., dated March 20, 2026) is not from any prior Prethinker fixture batch. It was retrieved fresh from fda.gov on 2026-05-24 specifically for batch `fresh_ugly_public_20260524_01`.
- All 25 QA pairs in `qa.md` / `oracle.jsonl` / `qa_questions.jsonl` were written from the public FDA warning letter only. No outside knowledge, no AI summary, no inference beyond what is explicitly recoverable from `source.md`.
- No part of the source document was synthesized. `source.md` is a faithful Markdown rendering of the published warning letter. Quoted claim text, bracketed editorial annotations such as `[sic]` and `[N]atural`, the recipient block, the four numbered CGMP citations with CFR references, and the signature block preserve the original wording exactly as published on fda.gov.
- No QA hints, answer keys, or fixture-style language were embedded into `source.md`.

## Local runner hygiene

The canonical `qa.md` in this repository is questions-only. The answer-bearing incoming QA file is retained as `qa_authored_with_answers.md` and must be treated like `oracle.jsonl`: scoring-only, never compile or answer context.

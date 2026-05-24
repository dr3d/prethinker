# Anti-Leakage Manifest — sec_material_event_ugly_002

- The collector did not inspect Prethinker internals while building this fixture. No Prethinker source files, schemas, rubric files, or evaluation code were read.
- This document — Pool Corporation's Form 8-K dated May 4, 2026, disclosing the departure of Peter D. Arvan and the appointment of John B. Watwood as President and CEO and John E. Stokely as Executive Chair — is not from any prior Prethinker fixture batch. It was identified by searching EDGAR for current Item 5.02 filings during this batch only.
- The QA in `qa.md`, `qa_questions.jsonl`, and `oracle.jsonl` was written exclusively from the content of `source.md`. No outside facts about Pool Corporation, Peter D. Arvan, John B. Watwood, John E. Stokely, David G. Whalen, Melanie M. Hart, Motion Industries, SMC Corporation of America, Applied Industrial Technologies, the 2026 Proxy Statement, the October 29, 2025 Form 10-Q, or any subsequent 8-K/A were used to construct or answer the questions.
- No synthetic source text was created. `source_original.txt` and `source.md` are derived only from the public EDGAR HTML page cited in `provenance.md`; EDGAR navigation chrome was removed. The non-preservation of the cover-page registrant tables and the Section 12(b) securities-registered table is a property of the extraction (noted in `provenance.md` and acknowledged in `source.md`), not an editorial omission.

## Local runner hygiene

The canonical `qa.md` in this repository is questions-only. The answer-bearing incoming QA file is retained as `qa_authored_with_answers.md` and must be treated like `oracle.jsonl`: scoring-only, never compile or answer context.

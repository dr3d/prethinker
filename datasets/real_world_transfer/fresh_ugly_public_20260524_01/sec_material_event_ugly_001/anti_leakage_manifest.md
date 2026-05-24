# Anti-Leakage Manifest — sec_material_event_ugly_001

- The collector did not inspect Prethinker internals while building this fixture. No Prethinker source files, schemas, rubric files, or evaluation code were read.
- This document — 1606 Corp.'s Form 8-K dated April 13, 2026, disclosing the First Amendment to Purchase and Sale Agreement with Jefferson Enterprise Energy, LLC — is not from any prior Prethinker fixture batch. It was identified by searching EDGAR for current Item 1.01 filings during this batch only.
- The QA in `qa.md`, `qa_questions.jsonl`, and `oracle.jsonl` was written exclusively from the content of `source.md`. No outside facts about 1606 Corp., Jefferson Enterprise Energy LLC, the Angelina County property, the original Purchase and Sale Agreement, or any related disclosures were used to construct or answer the questions.
- No synthetic source text was created. `source_original.txt` and `source.md` are derived only from the public EDGAR HTML page cited in `provenance.md`; EDGAR navigation chrome and a parser-injected "*(untagged table — column alignment not verified)*" annotation were removed, but the substantive content (cover page tables, item text, signature block) is preserved from the official filing.

## Local runner hygiene

The canonical `qa.md` in this repository is questions-only. The answer-bearing incoming QA file is retained as `qa_authored_with_answers.md` and must be treated like `oracle.jsonl`: scoring-only, never compile or answer context.

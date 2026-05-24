# Anti-leakage manifest — ntsb_aviation_ugly_001

- The collector did NOT inspect Prethinker repository internals, prior batch fixture files, prior oracle/QA wording, or any Prethinker test corpus when assembling this fixture.
- The document used is a real, official NTSB publication retrieved fresh on 2026-05-24 from the URL recorded in `metadata.json` and `provenance.md`. It is not derived from any prior Prethinker fixture batch.
- The QA pairs in `qa.md`, `qa_questions.jsonl`, and `oracle.jsonl` were written solely from the contents of the public source document captured in `source.md` / `source_original.txt`. No outside-document knowledge was used to construct answers.
- No synthetic source text was created. Every word in `source.md` and `source_original.txt` originates from the official NTSB PDF. Markdown headings and table formatting were imposed for readability; no narrative content was rewritten or paraphrased.

## Local runner hygiene

The canonical `qa.md` in this repository is questions-only. The answer-bearing incoming QA file is retained as `qa_authored_with_answers.md` and must be treated like `oracle.jsonl`: scoring-only, never compile or answer context.

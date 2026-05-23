# Anti-Leakage Manifest: sec_8k_material_event_001

- `qa.md` contains questions only. No reference answers, oracle text, or oracle-derived hints appear in `qa.md`.
- `source.md` contains source material only. It is a Markdown transcription of the public Form 8-K HTML page. No QA, no oracle answers, and no synthetic facts have been inserted into `source.md`.
- Oracle/reference answers are isolated in `oracle.jsonl` and `qa_battery.json`. These files are answer-bearing and must not be fed into source compilation by the runner.
- `story.md` is a byte-equivalent copy of `source.md` for harness compatibility and contains no additional answer-bearing content.
- `source_original.txt` retains the raw extracted text of the original SEC EDGAR HTML page for provenance.
- The source was cleaned for formatting and readability only: Markdown tables substituted for HTML cover-page tables, heading levels preserved, defined-term parentheticals preserved, dollar amounts and percentages preserved verbatim. One whitespace normalization was made to the telephone number ("( 610)" → "(610)") and is documented in `provenance.md`. No other text was altered. No facts were added.
- No facts were added, removed, or paraphrased to make questions answerable. Every oracle answer is grounded in spans that exist in `source.md`.

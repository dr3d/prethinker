# Anti-leakage manifest — ntsb_aviation_investigation_001

- `qa.md` contains questions only. It has exactly 25 numbered questions and no answer text.
- `source.md` contains source material only. It is a Markdown rendering of the NTSB preliminary report DCA26MA024 with no added facts, no added analysis, and no embedded answer key.
- Oracle answers are isolated in `oracle.jsonl` and `qa_battery.json`. These files must not be fed into source compilation.
- `qa_questions.jsonl` contains structured question rows without answers and is safe alongside `source.md` and `qa.md` for input-side compilation.
- No synthetic facts were added to `source.md`. Every claim in `source.md` traces back to the issued NTSB preliminary report.
- Cleaning of the source was limited to formatting and readability: page-break artifacts and the recurring "This information is preliminary and subject to change" caveat were preserved verbatim; section labels were prefixed with Markdown `##`; the existing key/value tables (Aircraft and Owner/Operator Information, Meteorological Information and Flight Plan, Wreckage and Impact Information, Administrative Information) were rendered as Markdown tables. No semantic rewriting was performed.

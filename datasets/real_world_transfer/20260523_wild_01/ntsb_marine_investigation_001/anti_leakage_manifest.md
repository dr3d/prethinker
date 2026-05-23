# Anti-leakage manifest — ntsb_marine_investigation_001

- `qa.md` contains questions only. It has exactly 25 numbered questions and no answer text.
- `source.md` contains source material only. It is a Markdown rendering of NTSB Marine Investigation Report MIR-25-21 with no added facts, no embedded analysis from outside the source, and no answer key.
- Oracle answers are isolated in `oracle.jsonl` and `qa_battery.json`. These files must not be fed into source compilation.
- `qa_questions.jsonl` contains structured question rows without answers and is safe to compile alongside `source.md` and `qa.md`.
- No synthetic facts were added to `source.md`. Every claim traces back to NTSB MIR-25-21 / DCA24FM038.
- Cleaning of the source was limited to formatting and readability:
  - Section numbering converted to Markdown heading levels.
  - Casualty Summary and Vessel Particulars rendered as Markdown tables.
  - Footnotes preserved verbatim as blockquotes adjacent to their referents.
  - Generic NTSB-agency boilerplate at the end was lightly abbreviated with `[…]` for length; investigation-specific text is unchanged.
  - The phrase "Gulf of America" in the source was preserved verbatim and not substituted.
  - The Figure 1 caption attribution to "Trinity Towing LLC" (vs the prose "Trinity Tugs LLC") was preserved verbatim.

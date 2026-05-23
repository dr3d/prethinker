# Anti-Leakage Manifest: fda_warning_or_recall_001

- `qa.md` contains questions only. No reference answers, no oracle text, no hints derived from oracle entries are present in `qa.md`.
- `source.md` contains source material only. It is a Markdown transcription of the public FDA warning letter text. No QA, no oracle answers, and no synthetic facts have been inserted into `source.md`.
- Oracle/reference answers are isolated in `oracle.jsonl` and `qa_battery.json`. These files are answer-bearing and must not be fed into source compilation by the runner.
- `story.md` is a byte-equivalent copy of `source.md` for harness compatibility and contains no additional answer-bearing content.
- `source_original.txt` retains the raw extracted text of the original FDA HTML page for provenance. It is a near-duplicate of `source.md` (without the YAML-style top note) and contains no QA, no answers, and no synthetic additions.
- The source was cleaned for formatting and readability only: headings normalized to Markdown, bullet lists preserved, footnote rendered as a blockquote with the original "¹" superscript marker, `(b)(4)` redactions preserved verbatim. The substantive text — including names, dates, FEI/MARCS/Warning Letter identifiers, CFR citations, and the verbatim "Your response is inadequate" verdicts — is unchanged from the FDA-published letter.
- No facts were added, removed, or paraphrased to make questions answerable. Every oracle answer is grounded in spans that exist verbatim in `source.md`.

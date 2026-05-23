# Anti-Leakage Manifest: osha_incident_or_enforcement_001

- `qa.md` contains questions only. No reference answers, oracle text, or oracle-derived hints appear in `qa.md`.
- `source.md` contains source material only. It is a Markdown rendering of the public Minnesota OSHA fatality investigation summary PDF for FFY 2024. No QA, no oracle answers, and no synthetic facts have been inserted into `source.md`.
- Oracle/reference answers are isolated in `oracle.jsonl` and `qa_battery.json`. These files are answer-bearing and must not be fed into source compilation by the runner.
- `story.md` is a byte-equivalent copy of `source.md` for harness compatibility and contains no additional answer-bearing content.
- `source_original.txt` retains the raw extracted text of the original PDF for provenance.
- The source was cleaned for formatting and readability only: the multi-page wide table was rendered as five Markdown table sections matching the printed page layout; the recurring header line ("Inspection data, including citations, can be viewed at osha.gov/data.") and the column schema header are preserved on each page section; dual-inspection rows are rendered as single rows with inspection numbers and per-employer fields concatenated using " / " inside the affected cells; blank inspection-number cells are preserved as blank; verbatim outcome phrasing — including singular/plural inconsistency ("Citation issued" vs "Citations issued") — is preserved. No outcome text was altered. No facts were added.
- No facts were added, removed, or paraphrased to make questions answerable. Every oracle answer is grounded in cells that exist verbatim in `source.md`.

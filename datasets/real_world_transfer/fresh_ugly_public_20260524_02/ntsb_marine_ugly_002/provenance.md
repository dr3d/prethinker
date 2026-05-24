# Provenance — ntsb_marine_ugly_002

## Source
- **Title:** Capsizing and Sinking of Towing Vessel Baylor J. Tregre
- **Series / number:** NTSB Marine Investigation Report MIR-25-21
- **NTSB case number:** DCA24FM038
- **Document date:** May 15, 2025
- **Accident date:** May 13, 2024 (about 1657 central daylight time)
- **Issuing agency:** National Transportation Safety Board (NTSB), United States
- **Authoritative URL:** https://www.ntsb.gov/investigations/AccidentReports/Reports/MIR2521.pdf
- **Retrieved:** 2026-05-24
- **Original format:** PDF (single-document marine investigation report)

## Extraction steps
1. Located the report via NTSB CAROL Query and the NTSB Accident Reports listing for marine investigations published in 2025.
2. Retrieved the official PDF from `https://www.ntsb.gov/investigations/AccidentReports/Reports/MIR2521.pdf`.
3. Converted PDF text to Markdown, preserving:
   - Document title, MIR number, and publication date as header block.
   - Casualty Summary table and Vessel Particulars table as Markdown tables (fields and values).
   - Section numbering exactly as in the source (1, 1.1, 1.2, 1.3, 1.3.1, 1.3.2, 1.3.3, 1.3.3.1, 1.3.3.2, 2, 3, 3.1).
   - AIS clock times to seconds where given in the source (e.g., 1647:04, 1650:09, 1654:20).
   - Footnotes 1–8, including the footnote that defines Subchapter M (footnote 3), severe thunderstorm watch (footnote 6), Special Marine Warning criteria (footnote 7), and the liferaft painter (footnote 4).
   - Figure captions in italics; figures themselves are not reproduced (the source file format is text-extracted Markdown, not the binary PDF).
   - Quoted radio/forecast text in blockquote form.
4. `source_original.txt` is a byte-for-byte copy of `source.md`. The report was extracted to Markdown directly; no separate raw text staging file exists, so the original-format snapshot is the Markdown text. (Anyone re-doing extraction would compare against the official PDF at the URL above.)

## Excerpt boundaries
- Begins at the NTSB letterhead line and the report title.
- Ends after the Vessel Particulars table and the standard closing paragraph directing readers to the CAROL website for accident ID DCA24FM038.
- Figures are referenced by caption but not embedded.
- No editorial commentary, summary, or QA hint has been added inside `source.md`.

## Caveats
- The report covers a fatality-free casualty with one minor injury; the narrative names "deckhand 2" as the injured crewmember airlifted from the response boat, while the Casualty Summary classifies the injury as "1 minor."
- Section 3 (Conclusions) contains only subsection 3.1 (Probable Cause); the report has no separately labeled "Contributing Factor(s)" subsection. QA in this fixture explicitly probes that absence.
- NTSB uses "Gulf of America" rather than "Gulf of Mexico" throughout. This usage is preserved verbatim from the source.
- Times are central daylight time per footnote 1 (UTC −5).
- Distances are nautical miles per footnote 1, except where the captain's mph estimate is quoted (with knots conversion in parentheses) and where weather observation distances are given in statute miles in some narrative passages.

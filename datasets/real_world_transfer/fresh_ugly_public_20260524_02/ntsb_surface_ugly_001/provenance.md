# Provenance — ntsb_surface_ugly_001

## Source
- **Title:** Cargo Tank Combination Vehicle Roadway Departure, Rollover, and Release of Anhydrous Ammonia — Teutopolis, Illinois — September 29, 2023
- **Series / number:** NTSB Highway Investigation Report HIR-25-06
- **NTSB accident case number:** HWY23MH017
- **Document date:** September 16, 2025
- **Accident date:** September 29, 2023 (about 8:41 p.m. central daylight time)
- **Issuing agency:** National Transportation Safety Board (NTSB), United States
- **Authoritative URL:** https://www.ntsb.gov/investigations/AccidentReports/Reports/HIR2506.pdf
- **Retrieved:** 2026-05-24
- **Original format:** PDF (single-document Highway Investigation Report)

## Extraction steps
1. Located the report via NTSB CAROL Query and the NTSB Highway Accident Reports listing for 2025 publications.
2. Retrieved the official PDF from `https://www.ntsb.gov/investigations/AccidentReports/Reports/HIR2506.pdf`.
3. Converted PDF text to Markdown, preserving:
   - Document title, HIR number, and publication date as a header block at the top.
   - Casualty Summary table as a Markdown table (fields and values).
   - Section numbering exactly as in the source (1.1, 1.2, 1.3, 1.4, 1.5, 1.5.1, 1.5.2, 1.5.3, 1.5.4, 1.5.4.1, 1.5.4.2, 1.6, 1.6.1, 1.6.2, 2, 2.1, 2.2, 3, 3.1, 3.2).
   - Footnotes 1–41 in source order.
   - Bullet lists for the fatally and seriously injured people enumerations in section 1.3.
   - Figure captions in italics; figures themselves are not reproduced.
   - Quoted statements from the driver, the carrier owner, and the IC in inline quotation marks.
4. `source_original.txt` is a byte-for-byte copy of `source.md`. The report was extracted to Markdown directly; no separate raw text staging file exists, so the original-format snapshot is the Markdown text. (Anyone re-doing extraction would compare against the official PDF at the URL above.)

## Excerpt boundaries
- Begins at the NTSB letterhead line and the report title.
- Ends after the References section, the NTSB partner-agency acknowledgment paragraph, and the standard closing pointer to the NTSB investigations website with accident ID HWY23MH017.
- The "About the NTSB" boilerplate that follows the references in the PDF was preserved up to the end of the references; the legal-disclaimer paragraphs about not assigning fault and the mailing-address block are omitted to keep the excerpt focused on report content.
- Figures are referenced by caption but not embedded.
- No editorial commentary, summary, or QA hint has been added inside `source.md`.

## Caveats
- The report's Conclusions section embeds contributing-factor language in the same paragraph as the probable-cause statement, rather than in a separately labeled subsection. QA in this fixture explicitly probes that nuance.
- Times in the body are central daylight time per footnote 1(a). On the day after the crash, times in the hazmat-response narrative cross midnight; the fixture's chronology answers state both the date (September 29 vs September 30) and the clock time.
- The combination vehicle driver was a 24-year-old; the minivan driver was a 17-year-old. The fixture preserves both ages.
- The report uses "combination vehicle" specifically to refer to a truck-tractor pulling a cargo-tank semitrailer; this terminology is retained verbatim.
- The cargo-tank recertification facility (Paul Akers, Inc.) is a separate party from the carrier (Prairieland Transport), and the FMCSA conducted separate postcrash inspections of each, with different violation counts. The fixture explicitly distinguishes the two.

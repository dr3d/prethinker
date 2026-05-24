# Provenance — ntsb_marine_ugly_001

**Source URL:** https://www.ntsb.gov/investigations/AccidentReports/Reports/MIR2521.pdf

**Retrieval date:** 2026-05-24

**Document type:** Official NTSB Marine Investigation Report MIR-25-21, published May 15, 2025 (PDF, 17 pages).

**Transformations performed:**

- Fetched PDF via web_fetch.
- `source_original.txt` preserves the raw extracted text including: page-break artifacts (page headers/footers like "Capsizing and Sinking of Towing Vessel Baylor J. Tregre MIR-25-21" repeated between pages were filtered out for readability; footnotes were kept inline at the locations they appeared in the source PDF text stream); numbered footnotes 1–8 retained with their content; the report's typographic em-dashes and curly quotes preserved.
- `source.md` reformats the same content for readability with section heading hierarchy (## for level-1 sections, ### for level-2, #### for level-3, ##### for level-4) matching the report's own numbering. The Casualty Summary block and Vessel Particulars block — both presented as label/value lists in the source PDF — are rendered as Markdown tables. Footnotes are rendered as blockquotes near where they were cited. Block quotes around the NWS forecast text use Markdown blockquote.
- Footnote numerals are kept as inline numbers (e.g., "...the casualty (see figure 1 and figure 2).1") in `source_original.txt` to preserve where they were cited; in `source.md` they are dropped for readability but the footnote text is rendered as a blockquote close to the citation site.
- One typographic anomaly preserved: "6- to7-foot seas" appears without a space; this is faithful to the source PDF.

**Excerpt status:** Full document. Both `source.md` and `source_original.txt` contain the entire NTSB report including the back-cover NTSB boilerplate-removed (the closing paragraphs describing the NTSB's general mission and contact information were truncated to the single line referencing CAROL/DCA24FM038, since the boilerplate is generic and not part of the case content). The full Analysis and Probable Cause sections are intact.

**Caveats:**

- The report uses "Gulf of America" terminology consistent with the U.S. Government's 2025 naming change for what was previously called the Gulf of Mexico. Other authoritative sources may use either name; the report's terminology is preserved.
- All times in the source are central daylight time (CDT) per the report's footnote 1; the markdown preserves this. The casualty summary table separately records "(coordinated universal time –5)".
- The Casualty Summary's "Weather" row gives one snapshot description; the body of the report contains more granular weather observations from KGLS, GNJT2, and KGVW at specific times. These will differ from the summary line and should be answered from the body text when asked specifically.
- The 1.3.1 Damage section describes a starboard-side engine room door found "separated from the hinges" and a forward starboard main deck door found open by divers. The report attributes the structural fractures and indentations to "recovery activities" — i.e., they are post-casualty, not causal.

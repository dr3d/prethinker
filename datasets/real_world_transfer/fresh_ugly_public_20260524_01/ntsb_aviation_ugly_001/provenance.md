# Provenance — ntsb_aviation_ugly_001

**Source URL:** https://www.ntsb.gov/investigations/Documents/Preliminary%20Report%20DCA26MA024.pdf

**Retrieval date:** 2026-05-24

**Document type:** Official NTSB Aviation Investigation Preliminary Report (PDF, 12 pages, marked "This information is preliminary and subject to change.")

**Transformations performed:**

- Fetched PDF via web_fetch. Text was extracted from the PDF as plain text and preserved verbatim as `source_original.txt`, including page break headers, line wraps as they appeared in the PDF text stream, and minor pagination artifacts (e.g., the report skips visible "Page 9 of 12" in the text stream — page 10 follows page 8 in the extracted text. This appears to be an artifact of PDF text layering; the figure on page 9 has no extractable text. Retained as-is.).
- `source.md` is a Markdown rendering of the same content with: prose paragraphs preserved, section headings demoted to `##`, the tabular blocks at the end ("Aircraft and Owner/Operator Information", "Meteorological Information and Flight Plan", "Wreckage and Impact Information", "Administrative Information") rendered as Markdown tables. Figure captions retained inline as italics. No prose content was added, removed, or rephrased.
- The Administrative Information block listed Additional Participating Persons across multiple lines in the PDF; these were preserved as repeated rows in the Markdown table.

**Excerpt status:** Full document. Both `source.md` and `source_original.txt` contain the entire 12-page NTSB preliminary report. Nothing excerpted.

**Caveats:**

- The PDF text extraction shows "Page 8 ... Page 10" with no extractable "Page 9" header text. The page exists in the original PDF; only the figure (Figure 9 caption appears on page 8 stream) carries forward. This is a faithful artifact of the source extraction.
- The "Aircraft and Owner/Operator Information" block in the source has empty fields for `Amateur Built` and `Operator Designator Code`. These empty fields are preserved.
- Tabular fields in the original report use a two-column form layout. Where a label and value pair wraps across multiple lines in the PDF (e.g., "Injuries: 14 Fatal, 2 Serious, 21 / Minor"), the value is preserved as a single string in the Markdown table.

# Provenance: fda_warning_or_recall_001

- **Source URL:** https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/granules-india-limited-697115-02262025
- **Document type:** HTML public warning letter page (FDA enforcement web record).
- **Source format on FDA.gov:** Single HTML page presented as the official text of the warning letter, with header metadata fields (Recipient Name, Title, Issuing Office, Warning Letter number, Product, etc.) and the letter body.
- **Document date (letter signature):** 2025-02-26
- **Content current as of (FDA page footer):** 2025-03-04
- **Retrieval date:** 2026-05-23
- **How obtained:** Retrieved by URL via the web_fetch tool. The environment's egress proxy blocked direct binary HTTP downloads from fda.gov for command-line retrieval, but the web_fetch tool returned the rendered text content of the page.
- **How source.md was converted:** The HTML page's rendered text was copied into Markdown. Header metadata fields were placed in a YAML-style top note. Numbered violation sections retained their FDA-style boldface introduction (e.g., "**1. Your firm failed to...**"). The footnote about GDUFA III is preserved as a blockquote with a "¹" marker matching the original superscript reference.
- **Redactions preserved:** All "(b)(4)" redactions in the original FDA letter — covering product names, components, equipment identifiers, and similar specifics — are preserved verbatim in source.md. No (b)(4) markers were filled in or speculated about.
- **Known extraction issues:**
  - Email and URL contact strings in the source.md may render with slight punctuation/whitespace differences from the rendered FDA page but the literal addresses are preserved.
  - The "/S/" mark on the signature line is rendered as ASCII text rather than as a visible signature image.
  - Some FDA-page chrome elements (navigation menu, related-content links) were excluded as they are not part of the letter content.
- **Original source file retained:** `source_original.txt` (text capture of the same fetched content). The FDA page is HTML; we use the .txt extension because what was preserved is the extracted text, not the raw HTML markup.
- **License / public status:** U.S. federal government work; public record.

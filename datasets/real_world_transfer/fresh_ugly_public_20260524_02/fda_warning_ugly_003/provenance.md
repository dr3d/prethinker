# Provenance — fda_warning_ugly_003

- **Source URL:** https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/international-laboratories-corp-698522-03102025
- **Retrieval date:** 2026-05-24
- **Original format:** HTML (FDA web page)
- **Extraction/transformation steps:**
  - Fetched the HTML page through a markdown-extraction web fetcher.
  - Removed site navigation, breadcrumbs, "Skip to" links, FDA logo blocks, footer link lists ("FDA Archive", "About FDA", "Accessibility", etc.), social media follow links, and the "Contact Number" block.
  - Preserved the document body verbatim: the warning letter title, the definition-list-style metadata block (Delivery Method, Reference #, Product, Recipient block, Issuing Office), the body, all three numbered violations, embedded URLs to FDA guidance documents, the bulleted lists under each violation, the Conclusion section, the signature block, and the "Content current as of" date.
  - Preserved the `(b)(4)` redaction markers exactly as they appear on the FDA page.
- **Excerpt boundaries:** Full document. No section was elided.
- **Caveats:**
  - `(b)(4)` redactions in the source are FOIA-style omissions. They are preserved verbatim and are not treated as missing content.
  - Embedded FDA guidance URLs are preserved as plain URLs in `source.md`.
  - The page renders the recipient block as a multi-line definition list; in `source.md` we keep that structure but readers should treat the recipient name, title, company, and address as a single block.
  - `source_original.txt` and `source.md` are identical in this fixture because the original was already cleanly extractable as Markdown — there is no PDF or OCR layer to retain.

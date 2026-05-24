# Provenance — fda_warning_ugly_004

- **Source URL:** https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/seaway-pharma-inc-717355-12012025
- **Retrieval date:** 2026-05-24
- **Original format:** HTML (FDA web page)
- **Extraction/transformation steps:**
  - Fetched the HTML page through a markdown-extraction web fetcher.
  - Removed site navigation, breadcrumbs, "Skip to" links, FDA logo blocks, footer link lists, social media follow links, and the "Contact Number" block.
  - Preserved the document body verbatim: the warning letter title, the definition-list-style metadata block (Delivery Method, Product, Recipient block, Issuing Office), the body, all three numbered violations with their CFR citations and nested sub-bullets, the four labeled discussion sections after the violations ("Responsibilities as a Contractor", "Change of Ownership at Facility", "Ineffective Quality System", "CGMP Consultant Recommended"), the Conclusion, the signature block, and the "Content current as of" date.
  - Preserved the `(b)(4)` redaction markers exactly as they appear on the FDA page.
- **Excerpt boundaries:** Full document. No section was elided.
- **Caveats:**
  - The salutation reads "Dear Dr. Gogineni and Mr. Lingam:" — the second addressee (Mr. Lingam) is not in the recipient metadata block at the top of the letter and only appears in the salutation. This asymmetry is preserved.
  - The "(b)(4)" redactions are FOIA-style omissions and are preserved verbatim.
  - Embedded FDA guidance URLs are preserved as plain URLs in `source.md`.
  - `source_original.txt` and `source.md` are identical because the source HTML extracted cleanly to Markdown.

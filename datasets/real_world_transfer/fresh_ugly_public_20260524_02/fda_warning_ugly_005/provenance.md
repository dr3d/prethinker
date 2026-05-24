# Provenance — fda_warning_ugly_005

- **Source URL:** https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/medical-products-laboratories-inc-721916-04092026
- **Retrieval date:** 2026-05-24
- **Original format:** HTML (FDA warning letter web page)
- **Extraction/transformation steps:**
  1. Fetched the official FDA warning letter web page.
  2. Removed website chrome (top navigation, breadcrumb links, social-share, "Subscribe to Warning Letters", footer link blocks, "An official website of the United States government" banner, FDA logo and global navigation menus).
  3. Preserved the warning letter body in full: heading, delivery method, product, recipient block, issuing office, warning letter number (320-26-61), date, salutation, body text, four numbered CGMP violations with all italicized sub-headings under violation 3, "Unapproved New Drug Violations" section, "Responsibilities as a Contractor", "Quality Systems", "Consultant Recommended", "Conclusion", response window, contact information, both signature blocks, footnote 1, and "Content current as of" footer date.
  4. Preserved `(b)(4)` redactions exactly as printed.
  5. Preserved the inline references to FDA guidance documents (Q8(R2), Q9(R1), Q10, Contract Manufacturing Arrangements for Drugs: Quality Agreements) with their URLs.
- **Excerpt boundaries:** Full document. No part of the letter body was abridged. Only website chrome was removed.
- **Caveats:**
  - The letter contains many `(b)(4)` FOIA redactions for product names, lot numbers, treatment systems, customer names, formulation details, expiration periods, and certain test results. These are part of the document as published by FDA and are preserved.
  - Two signature blocks are present (Francis Godwin and Tina Smith). The "/S/" notation appears before each signatory in the FDA web rendering.
  - Footnote 1 appears as a small superscript "1" in the body referencing "15 working days^1" with the footnote text rendered after the signature blocks and before the "Content current as of" date.
  - No tables in the strict sense; the three TAMC/TYMC lot rows under Violation 1 are rendered as a bulleted list in the source HTML and are preserved as such in `source.md`.

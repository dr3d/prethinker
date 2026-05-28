# Fixture notes — fda_warning_ugly_006

## Why this document is messy
It is an FDA CGMP warning letter that mixes a structured header definition-list with dense regulatory prose. It carries multiple identifier systems (Warning Letter 320-26-61, MARCS-CMS 721916, FEI 2513595), four separately numbered CGMP violations each anchored to a CFR citation and internal sub-headings (microbiological, stability assay, complaint investigations), a long bulleted product/labeling list for the unapproved-new-drug charge, a two-official signature block, a footnote, and pervasive "(b)(4)" redaction markers standing in for protocols, lot numbers, components, temperatures, and dates.

## What structures it pressures
- Identifier fidelity across three distinct numbering systems and a reused FEI (header vs. reply instruction).
- Redaction handling: "(b)(4)" appears dozens of times; a faithful reader must reproduce the marker rather than guess or omit the withheld value.
- Citation strings: four CFR cites (211.113(a), 211.100(a), 211.192, 211.166(a)), statutory sections (301(d), 505(a), 201(g)(1), 201(p)), and ICH guidances (Q8(R2)/Q9(R1)/Q10).
- Date/sequence: inspection window, 483-response date, letter date, content-current date, and a 15-working-day deadline.
- Cross-section reasoning: violation 2 (process validation discontinued at the customer's direction) connects to the "Responsibilities as a Contractor" section; violation 4 (over-wide labeled storage range) connects to the firm's quoted admission.
- Source-state/limitation: the letter repeatedly states why the firm's responses were inadequate and that the violation list is not all-inclusive.

## Known ambiguities in the source
- Many specific values (lot numbers, the treatment protocol, temperatures, the recall date, the failing CFU count) are redacted as "(b)(4)," so questions target the redaction marker itself or the surrounding non-redacted text, never the withheld value.
- The product list mixes brand names (Plexion, Hydro-Q) with generic descriptions; several share identical indications, which can invite conflation.
- "Within 15 working days" is a working-day count, not calendar days; the footnote separately offers a Post-Warning Letter Meeting under GDUFA III.

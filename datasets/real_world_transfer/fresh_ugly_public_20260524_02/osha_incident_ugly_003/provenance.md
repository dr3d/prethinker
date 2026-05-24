# Provenance — osha_incident_ugly_003

## Source
- **Title (citation):** Citation and Notification of Penalty — Southeast Services of the Treasure Coast, Inc.
- **Title (news release):** US Department of Labor finds storm pipe cleaning, maintenance employer could have prevented 24-year-old worker's fatality at Port St. Lucie worksite
- **OSHA Inspection Number:** 1760606
- **OSHA Citation Issuance Date:** January 7, 2025
- **OSHA News Release Date:** January 16, 2025
- **OSHA News Release Number:** 24-2619-ATL
- **Underlying incident date (per citation):** July 8, 2024
- **Underlying incident date (per news release lede/body):** "June 2024" / "June 8, 2024" (preserved verbatim despite inconsistency with citation)
- **Issuing agency:** US Department of Labor / Occupational Safety and Health Administration (OSHA), Fort Lauderdale Area Office, Region 4 (Atlanta)
- **Authoritative URLs:**
  - Citation PDF: `https://www.dol.gov/sites/dolgov/files/OPA/newsreleases/2025/OSHA20242619.pdf`
  - News release HTML: `https://www.dol.gov/newsroom/releases/osha/osha20250116`
- **Retrieved:** 2026-05-24
- **Original format:** PDF (Citation and Notification of Penalty) and HTML (news release)

## Extraction steps
1. Located the news release via the OSHA news-releases enforcement listing and the DOL newsroom archive.
2. Retrieved the official news release HTML from `https://www.dol.gov/newsroom/releases/osha/osha20250116?lang=ru` (the page content is identical to the canonical English version).
3. Retrieved the official Citation and Notification of Penalty PDF from `https://www.dol.gov/sites/dolgov/files/OPA/newsreleases/2025/OSHA20242619.pdf`.
4. Converted both documents to Markdown, preserving:
   - News release header (Agency, Date, Release Number), the "Please note" advisory, headline, sub-headline, body paragraphs (including the verbatim quote attributed to Area Director Condell Eastmond), penalty amount, employer description, 15-business-days option list, and both media-contact blocks.
   - Citation cover letter (greeting "Dear Employer," opening paragraph, references to OSHA 3000 booklet, page 6 contest procedures, informal conference procedures, OSHA office address and phone, EFOIA notice, and Sincerely / signature line "Condell Eastmond, Area Director").
   - Citation header / metadata table (Inspection Number, Inspection Date(s), Issuance Date, Inspection Site).
   - Posting paragraph, Informal Conference paragraph, Right to Contest paragraph, Penalty Payment paragraph, Notification of Corrective Action paragraph, Employer Discrimination Unlawful paragraph, Notice to Employees paragraph.
   - "NOTICE TO EMPLOYEES OF INFORMAL CONFERENCE" boxed section with blank date/time fields preserved as "_________________".
   - "CERTIFICATION OF CORRECTIVE ACTION WORKSHEET" header table, instruction text, and the 29 USC 666(g) note.
   - Citation 1 Item 1 with header table, violation type, Section 5(a)(1) citation language, the "On or about July 8, 2024…" narrative, the six bulleted corrective methods (preserved as a bulleted list in source order), Abatement Documentation Required note, Abatement Date, Proposed Penalty, and the Condell Eastmond signature.
   - Debt Collection / Invoice section with the company/inspection header table, Summary of Penalties table (one row plus total), payment instructions, Interest paragraph (1% rate), Delinquent Charges paragraph (6% rate), Administrative Costs paragraph, and the Condell Eastmond signature.
5. `source_original.txt` is a byte-for-byte copy of `source.md`. The two documents were extracted to Markdown directly; no separate raw text staging file exists, so the original-format snapshot is the Markdown text. (Anyone re-doing extraction would compare against the PDF and HTML at the URLs above.)

## Excerpt boundaries
- The news release portion begins at the agency/date/release-number header block and ends after the two media contacts. The "Please note" advisory is retained because it appears as part of the canonical published page.
- The citation portion begins with the date stamp "01/07/2025" on the cover letter and ends after the Debt Collection signature. Some boilerplate paragraphs not relevant to fixture QA (e.g., the OSHA 3000 booklet text itself, the bank-EFT description in the debt-collection invoice) are abridged but never fabricated.
- Page numbers and pagination chrome from the PDF ("Citation and Notification of Penalty Page N OSHA-2") are not reproduced.
- No editorial commentary, summary, or QA hint has been added inside `source.md`.

## Caveats
- The OSHA news release contains an internal inconsistency in describing the incident date: lede says "in June 2024" and body says "on June 8, 2024," while Citation 1 Item 1 says "On or about July 8, 2024." All three phrasings are preserved verbatim. The fixture uses this as a join/inconsistency-detection prompt.
- The "and its successors" language is part of the addressee block on the citation and is preserved in the employer name. Fixture QA permits answers that either include or exclude this suffix as long as the underlying entity name is correct.
- The Notice to Employees of Informal Conference contains literal blank fields (dashes) preserved as "_________________" — these are not redactions, they are blanks awaiting completion.
- The two media contacts share the same phone number (678-237-0630). This is reproduced as it appears.
- All dates in the citation packet are in MM/DD/YYYY format; the news release uses long-form ("January 16, 2025"). Both formats are preserved verbatim.

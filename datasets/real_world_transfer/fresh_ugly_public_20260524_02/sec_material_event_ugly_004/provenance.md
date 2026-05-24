# Provenance — sec_material_event_ugly_004

## Source
- **Title:** Form 8-K/A (Amendment No. 1) — Current Report — Blackstone Inc.
- **Registrant:** Blackstone Inc. (Delaware)
- **EDGAR CIK:** 1393818
- **Date of Report (Date of earliest event reported):** October 23, 2025
- **Signature date:** October 23, 2025
- **Trading symbol / exchange:** BX / New York Stock Exchange
- **Authoritative URL:** `https://www.sec.gov/Archives/edgar/data/1393818/000119312525248907/d51239d8ka.htm`
- **Retrieved:** 2026-05-24
- **Original format:** HTML (EDGAR Form 8-K/A as filed)

## Extraction steps
1. Located the 8-K/A via SEC EDGAR full-text search for Blackstone 8-K amendments.
2. Retrieved the filing HTML from the URL above.
3. Converted to Markdown, preserving:
   - The cover-page header (UNITED STATES SECURITIES AND EXCHANGE COMMISSION / WASHINGTON, D.C. 20549 / FORM 8-K/A / "(Amendment No. 1)" / CURRENT REPORT / Pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1934).
   - The "Date of Report (Date of earliest event reported)" line.
   - The registrant name and "Exact name of Registrant as specified in its charter" qualifier.
   - The three-cell identifier table (State, Commission File Number, IRS EIN).
   - The two-cell address/ZIP table.
   - The telephone-number block with "(Registrant's telephone number, including area code)" qualifier.
   - The "NOT APPLICABLE" former-name field (with case preserved).
   - All four "Check the appropriate box below" provisions with their rule citations and ☐ checkbox markings (all unchecked).
   - The "Securities registered pursuant to Section 12(b) of the Act" table verbatim.
   - The emerging-growth-company language with the ☐ checkbox marking and the subsidiary "If an emerging growth company..." clause with its ☐ checkbox marking.
   - The full Explanatory Note paragraph identifying the EDGAR-printer error, the EDGAR Copy ($280.1 million on page 11), the Earnings Presentation ($380.1 million), the website Shareholders-page section names ("Overview" and "Events"), and the three explicit "no other changes" statements.
   - The Item 2.02 disclosure ("Results of Operations and Financial Condition") paragraph.
   - The Item 9.01 exhibits table (99.1 press release, 104 cover-page XBRL).
   - The SIGNATURE block with the date, registrant name, /s/ signature, Name, and Title (Chief Financial Officer).
4. `source_original.txt` is a byte-for-byte copy of `source.md`.

## Excerpt boundaries
- The Markdown extract starts at "UNITED STATES SECURITIES AND EXCHANGE COMMISSION" and ends after the "Title: Chief Financial Officer" signature line. Cover-page chrome, EDGAR system headers/footers, and the encoded XBRL data are omitted.
- Exhibit 99.1 (the press release itself, with or without the corrected figure) is filed separately on EDGAR and is NOT reproduced in this fixture's source.
- The page-11 reference in the Explanatory Note is preserved verbatim ("$280.1 million reflected on page 11 in the EDGAR Copy").

## Caveats
- The accession-number sequence (0001193125-25-248907) suggests this filing was transmitted to EDGAR sometime in late October or later 2025, but the source's Date of Report and signature date are both October 23, 2025. Fixture questions q008 and q022 carefully distinguish between "Date of Report" (which the source provides as October 23, 2025) and "actual EDGAR transmission/filing date" (which the source does not provide).
- The Original 8-K filing referenced is the document amended by this 8-K/A; the Original 8-K itself is NOT reproduced in this fixture. References to the Original 8-K are limited to what this Amendment's Explanatory Note and exhibits table state about it.
- The corrected Earnings Presentation (with the $380.1 million figure) is NOT attached to this Amendment — the source describes the correction in prose only and directs readers to the Company's website for the authoritative version. Fixture question q020 probes this distinction.
- The amendment-number designator "(Amendment No. 1)" appears as a parenthetical subtitle below the "FORM 8-K/A" title on the cover page; this is preserved verbatim.
- All four cover-page checkboxes (Rule 425, 14a-12, 14d-2(b), 13e-4(c)) and both emerging-growth-company checkboxes are ☐ (unchecked).
- The dollar amount in the EDGAR Copy ($280.1 million) and the corrected dollar amount ($380.1 million) are preserved exactly as written (with one decimal place and the "million" word).
- The two website-section names — "Overview" and "Events" — are preserved verbatim, including the quotation marks present in the source.
- "NOT APPLICABLE" in the former-name field is in all-uppercase in the source and is preserved that way.

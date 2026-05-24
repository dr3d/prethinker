# Provenance — sec_material_event_ugly_003

## Source
- **Title:** Form 8-K — Current Report — ServiceNow, Inc. (Item 5.02 disclosure of Amendment No. 3 to employment agreement with Chairman and CEO William R. McDermott)
- **Registrant:** ServiceNow, Inc. (Delaware)
- **EDGAR CIK:** 1373715
- **Date of report (Date of earliest event reported):** December 23, 2025
- **Signature date:** December 23, 2025
- **Trading symbol / exchange:** NOW / The New York Stock Exchange
- **Authoritative URL:** `https://www.sec.gov/Archives/edgar/data/1373715/000137371525000335/now-20251223.htm`
- **Retrieved:** 2026-05-24
- **Original format:** HTML (EDGAR Form 8-K as filed)

## Extraction steps
1. Located the 8-K via SEC EDGAR.
2. Retrieved the filing HTML from the URL above.
3. Converted to Markdown, preserving:
   - The cover-page header (UNITED STATES SECURITIES AND EXCHANGE COMMISSION / Washington, DC 20549 / FORM 8-K / CURRENT REPORT / Pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1934).
   - The "Date of report (Date of earliest event reported)" line.
   - The registrant name and "Exact name of registrant as specified in its charter" qualifier.
   - The three-cell identifier table (State, Commission File Number, IRS EIN), preserving the column headings as written.
   - Principal-office address with "(Address of principal executive offices and Zip Code)" qualifier.
   - Telephone number with "(Registrant's telephone number, including area code)" qualifier.
   - Former-name field with verbatim value "Not Applicable."
   - All four "Check the appropriate box below" provisions with their rule citations and ☐ checkbox markings (all unchecked).
   - The "Securities registered pursuant to Section 12(b) of the Act" table verbatim.
   - The emerging-growth-company language with the ☐ checkbox marking and the subsidiary "If an emerging growth company..." clause with its ☐ checkbox marking.
   - The Item 5.02 disclosure in full, including all five severance-scenario paragraphs (CIC, non-CIC, retirement after 65, death, disability) and the closing summary-qualification sentence.
   - The Item 9.01 exhibits table (10.1, 10.2, 104).
   - The SIGNATURES block, including the "Pursuant to the requirements..." certificate language, the registrant name, the /s/ signature, the typed name, the typed title (General Counsel), and the date.
4. `source_original.txt` is a byte-for-byte copy of `source.md`. The HTML at the EDGAR URL is the canonical original.

## Excerpt boundaries
- The Markdown extract starts at "UNITED STATES SECURITIES AND EXCHANGE COMMISSION" and ends after the "Date: December 23, 2025" signature line. Cover-page chrome, EDGAR system headers/footers, and the encoded XBRL data are omitted.
- All compensation-related text is preserved verbatim; no paraphrasing or compression was applied.
- The four severance-scenario paragraphs (CIC, non-CIC, retirement, death/disability) are reproduced in source order.

## Caveats
- Exhibit 10.1, Exhibit 10.2, and Exhibit 104 are filed separately on EDGAR and are NOT reproduced in this fixture's source — only the exhibit table entry and the 8-K's prose description of the amendment and Policy are included. The fixture treats the exhibit contents themselves as outside the source.
- The 8-K does NOT disclose specific dollar amounts for base salary, target bonus, or any other compensation element. Multiple fixture questions probe this absence (q019, q020).
- The 8-K refers to "Amendment No. 3" but does not describe or attach Amendments No. 1 or No. 2; fixture question q024 probes the implication.
- All four "Check the appropriate box below" boxes are ☐ (unchecked) and both "emerging growth company" boxes are ☐ (unchecked); the fixture preserves the checkbox markings verbatim.
- The 8-K is filed and dated December 23, 2025 — the same calendar date as the "Date of earliest event reported." This is common for 8-Ks where the event being reported happens on the filing day, but the source confirms the calendar coincidence explicitly.
- "December 31, 2030" is the latest service date through which McDermott has agreed to remain in service "at least" — the source uses the language "at least" so longer service is not precluded, only the floor is set.
- The 8-K mentions the "compensation peer group" but does not name the peer companies; fixture question q019 probes this omission.

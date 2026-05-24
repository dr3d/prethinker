# Provenance — sec_material_event_ugly_005

## Source
- **Title:** Form 8-K/A (Amendment No. 1) — Current Report — SHF Holdings, Inc.
- **Registrant:** SHF Holdings, Inc. (Delaware)
- **EDGAR CIK:** 1854963
- **Date of Report (Date of earliest event reported):** August 13, 2025
- **Signature date:** August 22, 2025
- **Trading symbols / exchange:** SHFS and SHFSW / The Nasdaq Stock Market LLC
- **Authoritative URL:** `https://www.sec.gov/Archives/edgar/data/1854963/000164117225025203/form8-ka.htm`
- **Retrieved:** 2026-05-24
- **Original format:** HTML (EDGAR Form 8-K/A as filed)

## Extraction steps
1. Located the 8-K/A via SEC EDGAR full-text search for Item 4.02 amendments filed in August 2025.
2. Retrieved the filing HTML from the URL above.
3. Converted to Markdown, preserving:
   - The cover-page header (UNITED STATES SECURITIES AND EXCHANGE COMMISSION / Washington, D.C. 20549 / FORM 8-K/A / "(Amendment No. 1)" / CURRENT REPORT / Pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1934).
   - The "Date of Report (Date of earliest event reported): August 13, 2025" line.
   - The registrant name and "Exact name of registrant as specified in its charter" qualifier.
   - The state of incorporation ("Delaware") shown as a standalone field above the two-cell identifier table.
   - The two-cell identifier table (Commission File Number, IRS EIN).
   - Address and ZIP code with parenthetical qualifier "(Address of principal executive offices) (Zip Code)".
   - Telephone number with verbatim qualifier "Registrant's telephone number, including area code".
   - The "(Former name or former address, if changed since last report)" line — note that the source preserves this empty parenthetical without a value, indicating no former name change.
   - All four "Check the appropriate box below" provisions with their rule citations and ☐ checkbox markings (all unchecked).
   - The "Securities registered pursuant to Section 12(b) of the Act" table verbatim with two rows (Class A Common Stock and Redeemable Warrants).
   - The emerging-growth-company language with the ☒ checkbox marking (CHECKED — registrant IS an EGC).
   - The subsidiary "If an emerging growth company..." clause with its ☐ checkbox marking (UNCHECKED — registrant has NOT opted out of the extended transition period).
   - The full Explanatory Note paragraph identifying the August 14, 2025 Original 8-K filing, the Non-Reliance Period (three months ended March 31, 2025), and the specific clarification this Amendment adds (Audit Committee discussion with MGO).
   - The Item 4.02 disclosure with all four paragraphs: (i) the August 13, 2025 conclusion paragraph identifying the May 16, 2025 prior 10-Q filing; (ii) the Audit Committee / MGO discussion paragraph; (iii) the Black-Scholes inputs paragraph (expected term and stock price) and the approximately $500,000 quantification; (iv) the restatement completion paragraph identifying the August 14, 2025 amended 10-Q filing.
   - The SIGNATURES block with the date (August 22, 2025), the registrant name (SHF HOLDINGS, INC.), the /s/ signature, the typed name (Terrance E. Mendez), and the title (Chief Executive Officer).
4. `source_original.txt` is a byte-for-byte copy of `source.md`.

## Excerpt boundaries
- The Markdown extract starts at "UNITED STATES SECURITIES AND EXCHANGE COMMISSION" and ends after the "Chief Executive Officer" signature line. Cover-page chrome, EDGAR system headers/footers, and the encoded XBRL data are omitted.
- No editorial commentary, summary, or QA hint has been added inside `source.md`.

## Caveats
- The source contains a typographical run-on "completedits" (missing space between "completed" and "its") in the final paragraph of Item 4.02. This typo appears verbatim in the original filing and is preserved in `source.md`. Fixture question q018 references this verbatim language.
- The Explanatory Note contains a minor grammar irregularity: "is being filed amend and restate the Item 4.02 disclosure" (missing "to" before "amend"). This is also verbatim from the source.
- The double-negative checkbox semantics for the emerging-growth-company extended-transition-period election: checked = "elected NOT to use" (i.e., opted out); unchecked = retained the extended transition period. The registrant left this box unchecked, meaning it uses the extended transition period. Fixture question q017 probes this convention.
- The Original 8-K and the amended Form 10-Q were both filed on August 14, 2025 — the same calendar date. The source explicitly establishes the sequential order ("Subsequent to the filing of the Original Form 8-K, the Company completed[]its restatement... and, on August 14, 2025, filed an amendment to the Company's Quarterly Report on Form 10-Q"). Fixture question q025 probes this same-day, two-event recognition.
- The accession number 0001641172-25-025203 corresponds to a transmission date on or after August 22, 2025 (the signature date); the source's Date of Report remains August 13, 2025 because that is the date of the underlying Audit Committee conclusion that triggered the Item 4.02 disclosure obligation.
- "(Former name or former address, if changed since last report)" appears in the source with no value below it (no "Not Applicable" or similar text), indicating no change. The fixture treats this as "absent" content; no question explicitly forces extraction of a value from this empty parenthetical.
- The auditor's full name "Macias Gini & O'Connell LLP" appears with the apostrophe in "O'Connell" preserved verbatim.

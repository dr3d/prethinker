# sec_material_event_ugly_005 — Questions with reference answers

This file pairs each question with its reference answer for human review and grading. The QA pipeline must read questions only from `qa.md` (or `qa_questions.jsonl`); reference answers live in `oracle.jsonl`.

## q001 — metadata_identifier

**Question.** State the form type (including any amendment designator and number), the registrant's full name, the registrant's state of incorporation, the Commission File Number, and the IRS Employer Identification Number.

**Reference answer.** Form type: Form 8-K/A (Amendment No. 1). Registrant: SHF Holdings, Inc. State of incorporation: Delaware. Commission File Number: 001-40524. IRS Employer Identification No.: 86-2409612.

## q002 — metadata_identifier

**Question.** State the Date of Report, the signature date, and the full name and title of the person signing the report on behalf of the registrant.

**Reference answer.** Date of Report (Date of earliest event reported): August 13, 2025. Signature date: August 22, 2025. Signatory full name: Terrance E. Mendez. Signatory title: Chief Executive Officer.

## q003 — metadata_identifier

**Question.** State the registrant's principal-office address (street, suite, city, state, ZIP) and the registrant's telephone number including area code.

**Reference answer.** Principal-office address: 1526 Cole Blvd., Suite 250, Golden, Colorado 80401. Telephone number: (303) 431-3435.

## q004 — metadata_identifier

**Question.** Reproduce the "Securities registered pursuant to Section 12(b) of the Act" table verbatim. State the title of each class, the trading symbol, the exchange, the par value (where given), and any special terms (e.g., exercise price for warrants).

**Reference answer.** Securities table verbatim — Headings: "Title of Each Class" | "Trading Symbol(s)" | "Name of Each Exchange on Which Registered". Row 1: "Class A Common Stock, $0.0001 par value per share" | "SHFS" | "The Nasdaq Stock Market LLC". Row 2: "Redeemable Warrants, each whole warrant exercisable for one share of Class A Common Stock at an exercise price of $11.50 per share" | "SHFSW" | "The Nasdaq Stock Market LLC". Par value of Class A Common Stock: $0.0001 per share. Warrant exercise price: $11.50 per share. Both securities are registered on The Nasdaq Stock Market LLC.

## q005 — metadata_identifier

**Question.** Identify the auditor referenced in the source by both its abbreviation as used in the source and its full name as also used in the source. State the auditor's role at the Company per the source.

**Reference answer.** Auditor abbreviation: MGO. Auditor full name: Macias Gini & O'Connell LLP. Role: "the independent registered public accounting firm for the Company."

## q006 — date_chronology

**Question.** List, in calendar order, every distinct calendar date referenced in the source, with the role each date plays (e.g., end of Non-Reliance Period, prior 10-Q filing, Audit Committee conclusion, Original 8-K filing, amended 10-Q filing, Amendment signature date).

**Reference answer.** In calendar order, six distinct calendar dates appear in the source: (1) March 31, 2025 — end of the Non-Reliance Period (the three months ended March 31, 2025). (2) May 16, 2025 — date the unaudited consolidated financial statements for the Non-Reliance Period were previously filed with the SEC (i.e., the original 10-Q filing date). (3) August 13, 2025 — date the Company's management and the Audit Committee concluded the Non-Reliance Period financial statements should no longer be relied upon (also the Date of Report for both the Original 8-K and this Amendment). (4) August 14, 2025 — date the Original Form 8-K was filed AND the date the Company filed the amended Form 10-Q (with restated financial statements) for the three months ended March 31, 2025. (5) August 22, 2025 — signature date of this Amendment 8-K/A.

## q007 — date_chronology

**Question.** How many calendar days elapsed between the end of the Non-Reliance Period (March 31, 2025) and the original 10-Q filing date (May 16, 2025)? Show the arithmetic.

**Reference answer.** March 31, 2025 → May 16, 2025. From March 31 to April 30 = 30 days. From April 30 to May 16 = 16 days. Total: 30 + 16 = 46 calendar days.

## q008 — date_chronology

**Question.** How many calendar days elapsed between the original 10-Q filing date (May 16, 2025) and the date the Audit Committee concluded the financial statements should no longer be relied upon (August 13, 2025)? Show the arithmetic.

**Reference answer.** May 16, 2025 → August 13, 2025. From May 16 to May 31 = 15 days. June = 30 days. July = 31 days. From August 1 to August 13 = 13 days. Total: 15 + 30 + 31 + 13 = 89 calendar days.

## q009 — date_chronology

**Question.** How many calendar days elapsed between the Date of Report (August 13, 2025) and the signature date of this Amendment 8-K/A (August 22, 2025)? Show the arithmetic.

**Reference answer.** August 13, 2025 → August 22, 2025. From August 13 to August 22 = 9 calendar days. (22 − 13 = 9.)

## q010 — date_chronology

**Question.** How many calendar days elapsed between the filing of the Original 8-K (August 14, 2025) and the signature date of this Amendment 8-K/A (August 22, 2025)? Show the arithmetic.

**Reference answer.** August 14, 2025 → August 22, 2025. From August 14 to August 22 = 8 calendar days. (22 − 14 = 8.)

## q011 — table_list_citation

**Question.** List, in source order, the four "Check the appropriate box below" provisions on the Form 8-K/A cover page, including each rule citation.

**Reference answer.** In source order, the four "Check the appropriate box below" provisions are: (1) Written communications pursuant to Rule 425 under the Securities Act (17 CFR 230.425); (2) Soliciting material pursuant to Rule 14a-12 under the Exchange Act (17 CFR 240.14a-12); (3) Pre-commencement communications pursuant to Rule 14d-2(b) under the Exchange Act (17 CFR 240.14d-2(b)); (4) Pre-commencement communications pursuant to Rule 13e-4(c) under the Exchange Act (17 CFR 240.13e-4(c)). All four boxes are ☐ (unchecked).

## q012 — table_list_citation

**Question.** State the marking (☐ or ☒) for each of the two emerging-growth-company-related checkboxes on the cover page, and quote the language preceding each checkbox verbatim.

**Reference answer.** First checkbox — language verbatim: "Indicate by check mark whether the registrant is an emerging growth company as defined in Rule 405 of the Securities Act of 1933 (§230.405 of this chapter) or Rule 12b-2 of the Securities Exchange Act of 1934 (§240.12b-2 of this chapter). Emerging growth company" — marking: ☒ (CHECKED). Second checkbox — language verbatim: "If an emerging growth company, indicate by check mark if the registrant has elected not to use the extended transition period for complying with any new or revised financial accounting standards provided pursuant to Section 13(a) of the Exchange Act." — marking: ☐ (UNCHECKED).

## q013 — table_list_citation

**Question.** State both Black-Scholes option-pricing-model inputs that the source identifies as having been incorrect for the Non-Reliance Period.

**Reference answer.** The two Black-Scholes option-pricing-model inputs the source identifies as incorrect for the Non-Reliance Period are: (1) the expected term and (2) the stock price. Source language verbatim: "The Black-Scholes option pricing model contained incorrect inputs, specifically for the expected term and stock price, which required adjustment to properly determine the fair value of the awards."

## q014 — table_list_citation

**Question.** State the Item number reported in this Amendment along with its full topic title (as the source gives it in the Item header).

**Reference answer.** Item 4.02 — "Non-Reliance on Previously Issued Financial Statements or a Related Audit Report or Completed Interim Review."

## q015 — table_list_citation

**Question.** List, in source order, the chain of related filings the Explanatory Note and Item 4.02 reference: (a) the previously filed quarterly report for the Non-Reliance Period (and its filing date); (b) the Original Form 8-K (and its filing date); (c) the amended Form 10-Q (and its filing date); (d) this Amendment 8-K/A (and its signature date).

**Reference answer.** Chain of related filings in source order: (a) Quarterly Report for the Non-Reliance Period — filed May 16, 2025 (the source describes this as the Company's unaudited consolidated financial statements for the three months ended March 31, 2025 "previously filed with the Securities and Exchange Commission on May 16, 2025"). (b) Original Form 8-K — filed August 14, 2025 (the source: "SHF Holdings, Inc. (the 'Company') filed a Current Report on Form 8-K with the Securities and Exchange Commission on August 14, 2025 (the 'Original Form 8-K')"). (c) Amended Form 10-Q — filed August 14, 2025 (the source: "on August 14, 2025, filed an amendment to the Company's Quarterly Report on Form 10-Q for the three months ended March 31, 2025, that includes the restated financial statements"). (d) Amendment 8-K/A (this filing) — signed August 22, 2025.

## q016 — source_state_response_status

**Question.** Is the registrant identified as an emerging growth company? Quote the cover-page language and the checkbox marking verbatim.

**Reference answer.** YES — the registrant IS identified as an emerging growth company. Verbatim cover-page language: "Indicate by check mark whether the registrant is an emerging growth company as defined in Rule 405 of the Securities Act of 1933 (§230.405 of this chapter) or Rule 12b-2 of the Securities Exchange Act of 1934 (§240.12b-2 of this chapter). Emerging growth company ☒" (The checkbox is CHECKED.)

## q017 — source_state_response_status

**Question.** Has the registrant indicated by check mark that it has elected NOT to use the extended transition period for complying with new or revised financial accounting standards? Quote the cover-page language and the checkbox marking verbatim, and explain what the source's checkbox marking literally states.

**Reference answer.** No — the registrant has NOT indicated by check mark that it has elected NOT to use the extended transition period. Verbatim cover-page language: "If an emerging growth company, indicate by check mark if the registrant has elected not to use the extended transition period for complying with any new or revised financial accounting standards provided pursuant to Section 13(a) of the Exchange Act. ☐" (The checkbox is UNCHECKED.) Literally: the registrant has not affirmatively checked the "elected NOT to use the extended transition period" box, which means the registrant has NOT opted out of the extended transition period — i.e., the registrant uses the extended transition period available to emerging growth companies. (The checkbox uses a double-negative convention: checked = opted out; unchecked = retained the extended transition period.)

## q018 — source_state_response_status

**Question.** According to the source, has the Company completed its restatement of the affected financial statements as of the date of this Amendment? Cite the source language.

**Reference answer.** Yes — per the source, the Company has completed its restatement of the affected financial statements. Verbatim source language (Item 4.02): "Subsequent to the filing of the Original Form 8-K, the Company completedits restatement of the affected financial statements and, on August 14, 2025, filed an amendment to the Company's Quarterly Report on Form 10-Q for the three months ended March 31, 2025, that includes the restated financial statements." (Note: the source contains a typographical run-on "completedits" which appears verbatim in the original filing.)

## q019 — source_state_response_status

**Question.** Has the amended Form 10-Q including the restated financial statements been filed as of the date of this Amendment? If so, state the date.

**Reference answer.** Yes — the amended Form 10-Q including the restated financial statements has been filed. Filing date: August 14, 2025. Verbatim source language: "on August 14, 2025, filed an amendment to the Company's Quarterly Report on Form 10-Q for the three months ended March 31, 2025, that includes the restated financial statements."

## q020 — source_state_response_status

**Question.** What did the Audit Committee of the Company's board of directors do, per the source, in connection with the restatement? Quote the source verbatim.

**Reference answer.** Per the source, the Audit Committee discussed the restatement with MGO, the independent registered public accounting firm for the Company. Verbatim: "The Audit Committee of the Company's board of directors discussed the restatement with MGO, the independent registered public accounting firm for the Company." The Audit Committee's discussion with MGO is also identified in the Explanatory Note as the specific clarification this Amendment No. 1 adds to the Original 8-K's Item 4.02 disclosure.

## q021 — hard_join_comparison

**Question.** State the gap between (a) the Date of Report (August 13, 2025) and the filing date of the Original 8-K (August 14, 2025), and (b) the Date of Report and the signature date of this Amendment 8-K/A (August 22, 2025). Identify both gaps and explain what each gap reflects.

**Reference answer.** (a) Date of Report (August 13, 2025) → Original 8-K filing (August 14, 2025) = 1 calendar day. This reflects the Company filing the 8-K within the four-business-day window required by Item 4.02 (the Date of Report is when management and the Audit Committee concluded; the 8-K was filed the next day). (b) Date of Report (August 13, 2025) → Amendment 8-K/A signature date (August 22, 2025) = 9 calendar days. This reflects the time between the underlying conclusion and this corrective Amendment, during which the Company completed the restatement and filed the amended 10-Q. (Both gaps share August 13, 2025 as their starting anchor, illustrating that the Date of Report on an amendment typically remains the date of the underlying triggering event, not the amendment's own signature date.)

## q022 — hard_join_comparison

**Question.** The source states the restatement is expected to result in an increase of approximately $500,000 to "previously reported operating expenses AND net loss" for the Non-Reliance Period. Explain why a single $500,000 stock-based-compensation error affects both line items, citing the source language.

**Reference answer.** A single $500,000 stock-based-compensation error affects BOTH operating expenses AND net loss because stock-based compensation expense is itself a component of operating expenses (typically recorded as part of personnel-related operating costs). When operating expenses increase by approximately $500,000, the loss from operations increases by approximately $500,000, which (absent offsetting non-operating items or tax effects the source does not mention) flows through to a corresponding approximately $500,000 increase in net loss. Source language verbatim: "This restatement is expected to result in an increase of approximately $500,000 to previously reported operating expenses and net loss for the Non-Reliance Period." The source uses the conjunction "and" to indicate the same approximately $500,000 figure affects both line items, not that there are two separate $500,000 adjustments.

## q023 — hard_join_comparison

**Question.** Per the Explanatory Note, what specific addition does this Amendment No. 1 make relative to the Original 8-K, and what does that imply was missing from the Original 8-K? Cite the Explanatory Note language.

**Reference answer.** Per the Explanatory Note, Amendment No. 1 adds a specific clarification: that the Audit Committee of the Company's board of directors discussed the restatement with MGO (the independent registered public accounting firm). Verbatim Explanatory Note: "This amendment to the Original Form 8-K ('Amendment No. 1') is being filed amend and restate the Item 4.02 disclosure to clarify that the Audit Committee of the Company's board of directors discussed the restatement with Macias Gini & O'Connell LLP ('MGO'), the independent registered public accounting firm for the Company." Implication: the Original 8-K's Item 4.02 disclosure did NOT explicitly state that the Audit Committee discussed the restatement with the independent registered public accounting firm — a disclosure required under Item 4.02(a)(3) of Form 8-K. The Amendment cures this omission.

## q024 — hard_join_comparison

**Question.** Compare the two securities registered: state both trading symbols, the relationship between the two instruments (i.e., one is the underlying common stock, the other is a warrant exercisable into that common stock), the par value of the common stock, and the exercise price of the warrants.

**Reference answer.** Two registered securities. Trading symbols: (1) SHFS — Class A Common Stock; (2) SHFSW — Redeemable Warrants. Relationship: SHFSW (Redeemable Warrants) is exercisable into SHFS (Class A Common Stock); each whole warrant is exercisable for one share of Class A Common Stock at an exercise price of $11.50 per share, so SHFSW holders may convert each warrant into one share of SHFS by paying $11.50. Par value of Class A Common Stock: $0.0001 per share. Warrant exercise price: $11.50 per share. Ticker convention: SHFSW = SHFS + "W" (the trailing W denotes warrants on the underlying common stock SHFS), a standard Nasdaq ticker convention for warrants on the same issuer's listed common stock. Both securities are listed on The Nasdaq Stock Market LLC.

## q025 — hard_join_comparison

**Question.** The source describes two distinct events occurring on August 14, 2025: (a) the filing of the Original Form 8-K, and (b) the filing of the amended 10-Q with restated financial statements. Identify both events with the source language describing each, and explain whether the source establishes the order in which they occurred on that same date.

**Reference answer.** Two distinct events on August 14, 2025: (a) Filing of the Original Form 8-K — verbatim source: "SHF Holdings, Inc. (the 'Company') filed a Current Report on Form 8-K with the Securities and Exchange Commission on August 14, 2025 (the 'Original Form 8-K')" (Explanatory Note). (b) Filing of the amended 10-Q with restated financial statements — verbatim source: "Subsequent to the filing of the Original Form 8-K, the Company completedits restatement of the affected financial statements and, on August 14, 2025, filed an amendment to the Company's Quarterly Report on Form 10-Q for the three months ended March 31, 2025, that includes the restated financial statements" (Item 4.02). Order on the same date: the source uses the word "Subsequent to the filing of the Original Form 8-K" to describe the amended 10-Q filing, establishing that the Original 8-K was filed first and the amended 10-Q was filed afterward on the same calendar date August 14, 2025. (The source does not give specific times of day, but the sequential ordering — Original 8-K first, then amended 10-Q — is explicit.)


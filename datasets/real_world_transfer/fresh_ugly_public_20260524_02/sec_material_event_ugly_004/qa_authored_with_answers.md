# sec_material_event_ugly_004 — Questions with reference answers

This file pairs each question with its reference answer for human review and grading. The QA pipeline must read questions only from `qa.md` (or `qa_questions.jsonl`); reference answers live in `oracle.jsonl`.

## q001 — metadata_identifier

**Question.** State the form type (including any amendment designator and number), the registrant's full name, the registrant's state of incorporation, the Commission File Number, and the I.R.S. Employer Identification Number.

**Reference answer.** Form type: Form 8-K/A (Amendment No. 1). Registrant: Blackstone Inc. State of incorporation: Delaware. Commission File Number: 001-33551. I.R.S. Employer Identification Number: 20-8875684.

## q002 — metadata_identifier

**Question.** State the Date of Report, the signature date, and the full name and title of the person signing the report on behalf of the registrant.

**Reference answer.** Date of Report (Date of earliest event reported): October 23, 2025. Signature date: October 23, 2025 (same calendar date). Signatory full name: Michael S. Chae. Signatory title: Chief Financial Officer.

## q003 — metadata_identifier

**Question.** State the registrant's principal-office address (street, city, state) and ZIP code, and the registrant's telephone number including area code.

**Reference answer.** Principal-office address: 345 Park Avenue, New York, New York. ZIP code: 10154. Telephone number: (212) 583-5000.

## q004 — metadata_identifier

**Question.** State the trading symbol, the title of the registered class, and the exchange on which the security is registered.

**Reference answer.** Trading Symbol(s): BX. Title of each class: Common Stock. Name of each exchange on which registered: New York Stock Exchange.

## q005 — metadata_identifier

**Question.** List, in source order, the exhibits filed under Item 9.01, including each exhibit number and the description as given in the exhibit table.

**Reference answer.** In source order, exhibits filed under Item 9.01(d) are: (1) Exhibit 99.1 — "Press release of Blackstone Inc. dated October 23, 2025." (2) Exhibit 104 — "The cover page from this Current Report on Form 8-K, formatted in Inline XBRL."

## q006 — date_chronology

**Question.** List, in calendar order, every distinct calendar date referenced in the source (in any form): both the date the underlying quarter ended and the Date of Report / signature date.

**Reference answer.** Two distinct calendar dates appear in the source, in calendar order: (1) September 30, 2025 — the close of the fiscal third quarter referenced in Item 2.02 ("third quarter ended September 30, 2025"). (2) October 23, 2025 — the Date of Report, the date the press release was issued, the date the Original 8-K was filed, the date the actual Earnings Presentation was posted on the Company's website, and the signature date of this Amendment.

## q007 — date_chronology

**Question.** How many calendar days elapsed between the close of the fiscal quarter (September 30, 2025) referenced in Item 2.02 and the Date of Report (October 23, 2025)? Show the arithmetic.

**Reference answer.** Quarter end September 30, 2025 → Date of Report October 23, 2025. From September 30 to September 30 = 0 days. October 1–23 = 23 days. Total: 23 calendar days.

## q008 — date_chronology

**Question.** The Original 8-K and this Amendment 8-K/A both reference October 23, 2025 as their Date of Report. How many calendar days separate the Original 8-K's filing date (October 23, 2025) and the Amendment's Date of Report (October 23, 2025) per the source?

**Reference answer.** Per the source, the Original 8-K was filed on October 23, 2025 ("the Current Report on Form 8-K filed by Blackstone Inc. (the 'Company') on October 23, 2025"), and the Amendment's Date of Report is October 23, 2025. The source places both on the same calendar date, so 0 calendar days separate them. (Note: the source does not explicitly state when the Amendment itself was transmitted to EDGAR; it states only that the Amendment's Date of Report and signature date are October 23, 2025. The Amendment's filing transmission date could be later than October 23, 2025, but the source does not provide that information.)

## q009 — date_chronology

**Question.** How many distinct calendar dates are mentioned anywhere in the source text? List each date with the role it plays (e.g., quarter end, Date of Report, Original 8-K filing, signature, posting of Earnings Presentation, etc.).

**Reference answer.** Two distinct calendar dates appear in the source: (a) September 30, 2025 — plays one role: the close of the fiscal quarter referenced in Item 2.02. (b) October 23, 2025 — plays multiple roles: (i) Date of Report (Date of earliest event reported) of this Amendment; (ii) date of the Original 8-K filing ("the Current Report on Form 8-K filed by Blackstone Inc. on October 23, 2025"); (iii) date the press release was issued ("On October 23, 2025, Blackstone Inc. issued a press release…"); (iv) date the press release attached as Exhibit 99.1 is dated ("Press release of Blackstone Inc. dated October 23, 2025"); (v) date the actual Earnings Presentation was posted on the Company's website ("as posted on October 23, 2025 in the 'Overview' and 'Events' sections of the Shareholders page on the Company's website"); (vi) signature date of this Amendment 8-K/A.

## q010 — date_chronology

**Question.** The source repeatedly references October 23, 2025 in connection with different events. List, in source order, every event that the source ties to October 23, 2025.

**Reference answer.** In source order, the events that the source ties to October 23, 2025 are: (1) Date of Report (Date of earliest event reported) of this Amendment (cover page). (2) Original 8-K filing ("the Current Report on Form 8-K filed by Blackstone Inc. on October 23, 2025" — in the Explanatory Note). (3) The actual Earnings Presentation was posted on the Company's website ("as posted on October 23, 2025 in the 'Overview' and 'Events' sections of the Shareholders page on the Company's website" — Explanatory Note). (4) Blackstone Inc. issued a press release and detailed presentation announcing financial results (Item 2.02 — "On October 23, 2025, Blackstone Inc. issued a press release…"). (5) The press release attached as Exhibit 99.1 is dated October 23, 2025 ("Press release of Blackstone Inc. dated October 23, 2025" — Item 9.01 exhibit description). (6) Signature date of this Amendment 8-K/A ("Date: October 23, 2025" — Signature block).

## q011 — table_list_citation

**Question.** List, in source order, the four "Check the appropriate box below" provisions on the Form 8-K/A cover page, including each rule citation.

**Reference answer.** In source order, the four "Check the appropriate box below" provisions are: (1) Written communications pursuant to Rule 425 under the Securities Act (17 CFR 230.425); (2) Soliciting material pursuant to Rule 14a-12 under the Exchange Act (17 CFR 240.14a-12); (3) Pre-commencement communications pursuant to Rule 14d-2(b) under the Exchange Act (17 CFR 240.14d-2(b)); (4) Pre-commencement communications pursuant to Rule 13e-4(c) under the Exchange Act (17 CFR 240.13e-4(c)). All four boxes are ☐ (unchecked).

## q012 — table_list_citation

**Question.** Reproduce the three-cell "State of incorporation / Commission File Number / I.R.S. EIN" identifier table verbatim, including column headings.

**Reference answer.** Three-cell identifier table verbatim: Column 1 heading — "State or other jurisdiction of incorporation"; value — "Delaware". Column 2 heading — "Commission File Number"; value — "001-33551". Column 3 heading — "I.R.S. Employer Identification No."; value — "20-8875684".

## q013 — table_list_citation

**Question.** Reproduce the "Securities registered pursuant to Section 12(b) of the Act" table verbatim, including column headings and the registered class.

**Reference answer.** Securities table verbatim — Headings: "Title of each class" | "Trading Symbol(s)" | "Name of each exchange on which registered". Row: "Common Stock" | "BX" | "New York Stock Exchange".

## q014 — table_list_citation

**Question.** State both Item numbers reported in the 8-K/A (in source order) including their full topic descriptions.

**Reference answer.** In source order: (1) Item 2.02 — Results of Operations and Financial Condition. (2) Item 9.01 — Financial Statements and Exhibits.

## q015 — table_list_citation

**Question.** State, verbatim, the two named sections of the Company's Shareholders page on its website where the actual Earnings Presentation was posted.

**Reference answer.** Verbatim: the "Overview" and "Events" sections of the Shareholders page on the Company's website.

## q016 — source_state_response_status

**Question.** Is the registrant identified as an emerging growth company? Quote the cover-page language and indicate the checkbox marking.

**Reference answer.** No — the registrant is NOT identified as an emerging growth company. Verbatim cover-page language: "Indicate by check mark whether the registrant is an emerging growth company as defined in Rule 405 of the Securities Act of 1933 (§230.405 of this chapter) or Rule 12b-2 of the Securities Exchange Act of 1934 (§240.12b-2 of this chapter). Emerging growth company ☐" (The checkbox is unchecked.)

## q017 — source_state_response_status

**Question.** What value appears under "(Former name or former address, if changed since last report)"?

**Reference answer.** Under "(Former name or former address, if changed since last report)" the source states: "NOT APPLICABLE" (all uppercase).

## q018 — source_state_response_status

**Question.** According to Item 2.02, what is the legal classification of the information in the press release attached as Exhibit 99.1 — is it "filed" or "furnished" under the Exchange Act? Quote the source verbatim.

**Reference answer.** Per Item 2.02, the information in the press release attached as Exhibit 99.1 is FURNISHED (not filed) under the Exchange Act. Verbatim quote: "The press release is attached hereto as Exhibit 99.1. All information in the press release is furnished but not filed."

## q019 — source_state_response_status

**Question.** Does the Amendment 8-K/A make any changes to the Original 8-K other than the single corrected figure? Quote the source's statement on the scope of changes.

**Reference answer.** No — the Amendment makes no other changes to the Original 8-K besides correcting the single figure. Verbatim source statements: (a) "There were no other discrepancies between the EDGAR Copy and the Earnings Presentation." (b) "The purpose of this Amendment is to correct the error in the EDGAR Copy." (c) "There are no other changes to the Original 8-K."

## q020 — source_state_response_status

**Question.** Does the source attach or reproduce the corrected Earnings Presentation, or does it only describe the corrected figure in the Explanatory Note? State exactly what the source provides about the corrected figure.

**Reference answer.** The source DOES NOT attach or reproduce the corrected Earnings Presentation in this Amendment 8-K/A. The Explanatory Note describes the corrected figure in prose ($380.1 million vs $280.1 million) but the Amendment's exhibit list shows only Exhibit 99.1 (the press release) and Exhibit 104 (cover page XBRL) — no corrected slide deck. Readers wanting the corrected Earnings Presentation must consult the "Overview" and "Events" sections of the Shareholders page on the Company's website, as the source instructs.

## q021 — hard_join_comparison

**Question.** Compare the figure shown in the EDGAR Copy (the version filed as Exhibit 99.1 to the Original 8-K) with the corrected figure shown in the actual Earnings Presentation posted on the Company's website. State both figures, the exact business segment and reporting period to which they pertain, the page on which the EDGAR Copy figure appeared, and the difference between the two figures.

**Reference answer.** EDGAR Copy figure: $280.1 million. Corrected figure (per the actual Earnings Presentation on the Company's website): $380.1 million. Business segment: Private Equity segment. Reporting period: the quarter ended September 30, 2025 (Blackstone's fiscal Q3 2025). Specific line item: Net Realizations. Page on which the erroneous EDGAR Copy figure appeared: page 11. Difference between the two figures: $380.1M − $280.1M = $100.0 million understatement in the EDGAR Copy (a leading-digit transposition: 2 → 3). The Explanatory Note attributes the error to a "financial printer edgarization error".

## q022 — hard_join_comparison

**Question.** The source uses the same calendar date (October 23, 2025) for multiple distinct events. State at least five events the source places on October 23, 2025, and explain whether the source actually says the Amendment itself was filed on October 23, 2025 or merely that its Date of Report is October 23, 2025.

**Reference answer.** Five events the source places on October 23, 2025 (in source order): (1) Date of Report (Date of earliest event reported) on the Amendment cover page. (2) Filing date of the Original 8-K ("the Current Report on Form 8-K filed by Blackstone Inc. on October 23, 2025"). (3) Posting of the actual Earnings Presentation on the Company's website ("as posted on October 23, 2025 in the 'Overview' and 'Events' sections of the Shareholders page"). (4) Issuance of the press release and detailed presentation ("On October 23, 2025, Blackstone Inc. issued a press release and detailed presentation"). (5) Date carried on the press release attached as Exhibit 99.1 ("Press release of Blackstone Inc. dated October 23, 2025"). (6) Signature date of the Amendment 8-K/A. The source explicitly states the Date of Report of the Amendment is October 23, 2025 and the signature date is October 23, 2025, but does NOT explicitly state when the Amendment itself was transmitted to EDGAR. So the source places six event-anchors on October 23, 2025 but does not necessarily mean the Amendment was filed on October 23, 2025 — only that its Date of Report (i.e., the date of the underlying event the Amendment relates to) and its signature date are October 23, 2025.

## q023 — hard_join_comparison

**Question.** State whether this Amendment alters anything in the Original 8-K besides the single figure on page 11. Cite the source language that establishes the scope of the change, and verify by examining the Item 2.02 and Item 9.01 sections as reproduced in this Amendment.

**Reference answer.** No — the Amendment alters nothing in the Original 8-K besides the single figure on page 11 of the EDGAR Copy of Exhibit 99.1. The source establishes this via three explicit statements in the Explanatory Note: (a) "There were no other discrepancies between the EDGAR Copy and the Earnings Presentation." (b) "The purpose of this Amendment is to correct the error in the EDGAR Copy." (c) "There are no other changes to the Original 8-K." Verification by inspecting Item 2.02 and Item 9.01 as reproduced in this Amendment: Item 2.02 contains the same one-paragraph description of the third-quarter results announcement and the same "furnished but not filed" classification of the press release; Item 9.01's exhibit table lists the same two exhibits (99.1 press release, 104 XBRL cover page) as in the Original 8-K. So no item descriptions, exhibits, or signatures differ between the Original 8-K and this Amendment beyond the corrected page-11 figure.

## q024 — hard_join_comparison

**Question.** The source identifies two distinct copies / locations of the Q3 2025 earnings presentation: (a) the "EDGAR Copy" furnished as Exhibit 99.1 to the Original 8-K, and (b) the "Earnings Presentation" posted on the Company's website. Identify which copy contained the error, which copy contained the correct figure, and explain how the source establishes the chain of authority between the two.

**Reference answer.** Two copies: (a) "EDGAR Copy" — furnished as Exhibit 99.1 to the Original 8-K filed on EDGAR; contained the ERROR ($280.1 million on page 11). (b) "Earnings Presentation" — posted on the Company's website in the Overview and Events sections of the Shareholders page on October 23, 2025; contained the CORRECT figure ($380.1 million). Chain of authority per the source: the Earnings Presentation on the Company's website is treated as the authoritative version. The Explanatory Note states that the EDGAR Copy figure "did not conform to the actual earnings presentation" and refers to the website version as "the actual earnings presentation" — establishing that the website Earnings Presentation is canonical and the EDGAR Copy was the deviant artifact requiring correction via Amendment.

## q025 — hard_join_comparison

**Question.** Compare the signatory of this Amendment 8-K/A (Michael S. Chae, Chief Financial Officer) with the typical 8-K signatory for general-corporate or executive-compensation matters (which is often the General Counsel). Explain what the source establishes about why the Chief Financial Officer signed this particular Amendment, considering the subject matter of Item 2.02.

**Reference answer.** The source identifies Michael S. Chae as Chief Financial Officer and the signatory of this Amendment 8-K/A. The source does NOT explicitly state why the CFO signed this Amendment rather than another officer (the source provides no rationale or comparison to other 8-K filing signatories). What the source DOES establish is that the subject matter of the Amendment is corrective — fixing a financial figure (Net Realizations of the Private Equity segment for Q3 2025) — and the underlying Item 2.02 disclosure is "Results of Operations and Financial Condition." The Chief Financial Officer is responsible for financial reporting accuracy, so signing a financial-correction Amendment is consistent with the CFO's role; this is a standard practice for Item 2.02-related 8-K filings and amendments, though the source itself does not articulate this reasoning.


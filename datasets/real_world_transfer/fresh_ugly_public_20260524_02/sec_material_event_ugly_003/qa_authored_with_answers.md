# sec_material_event_ugly_003 — Questions with reference answers

This file pairs each question with its reference answer for human review and grading. The QA pipeline must read questions only from `qa.md` (or `qa_questions.jsonl`); reference answers live in `oracle.jsonl`.

## q001 — metadata_identifier

**Question.** State the registrant's full name, trading symbol, exchange where its common stock is registered, state of incorporation, Commission File Number, IRS Employer Identification Number, and the par value of its common stock.

**Reference answer.** Full name: ServiceNow, Inc. Trading Symbol: NOW. Exchange: The New York Stock Exchange. State of incorporation: Delaware. Commission File Number: 001-35580. IRS Employer Identification Number: 20-2056195. Par value of common stock: $0.001 per share.

## q002 — metadata_identifier

**Question.** State the "Date of report (Date of earliest event reported)," the signature date, the registrant's principal-office address, and the registrant's telephone number.

**Reference answer.** Date of report (Date of earliest event reported): December 23, 2025. Signature date: December 23, 2025 (same date). Principal-office address: 2225 Lawson Lane, Santa Clara, California 95054. Telephone number: (408) 501-8550.

## q003 — metadata_identifier

**Question.** State the Item numbers reported in the 8-K (in source order) and the full name and title of the person signing the report on behalf of the registrant.

**Reference answer.** Item numbers reported in source order: (1) Item 5.02 — Departure of Directors or Certain Officers; Election of Directors; Appointment of Certain Officers; Compensatory Arrangements of Certain Officers; (2) Item 9.01 — Financial Statements and Exhibits. Signatory: Russell S. Elmer, General Counsel (signing on behalf of ServiceNow, Inc.).

## q004 — metadata_identifier

**Question.** State the full name and title of the executive who is the subject of the Item 5.02 disclosure (i.e., whose employment-agreement amendment is being reported).

**Reference answer.** Full name and title of the Item 5.02 subject executive: William R. McDermott, Chairman and Chief Executive Officer ("CEO") of the Company.

## q005 — metadata_identifier

**Question.** List, in source order, the exhibits filed under Item 9.01, including each exhibit number and the description as given in the exhibit table.

**Reference answer.** In source order, the exhibits filed under Item 9.01 are: (1) Exhibit 10.1 — "Amendment No. 3 to Employment Agreement between the Registrant and William R. McDermott"; (2) Exhibit 10.2 — "ServiceNow, Inc. Executive Severance Policy, as amended"; (3) Exhibit 104 — "Cover Page Interactive Data File – the cover page XBRL tags are embedded within the Inline XBRL document."

## q006 — date_chronology

**Question.** List, in calendar order, the dates referenced in the source: (a) the Date of earliest event reported, (b) the effective date of the employment-agreement amendment, (c) the effective date of the amended Executive Severance Policy, (d) the latest date through which Mr. McDermott has agreed to remain in service, and (e) the signature date.

**Reference answer.** In calendar order: (a) December 23, 2025 — Date of earliest event reported AND signature date (the same calendar date). (b) January 1, 2026 — Effective date of the employment-agreement amendment AND effective date of the amended Executive Severance Policy (the same calendar date for both). (c) December 31, 2030 — latest date through which Mr. McDermott has agreed to remain in service to the Company.

## q007 — date_chronology

**Question.** How many calendar days elapsed between the Date of report (December 23, 2025) and the effective date of the amendment (January 1, 2026)? Show the arithmetic.

**Reference answer.** Date of report December 23, 2025 → effective date January 1, 2026. From December 23 to December 31 = 8 days. January 1 = 1 day. Total: 8 + 1 = 9 calendar days.

## q008 — date_chronology

**Question.** How many calendar days span from the effective date of the amendment (January 1, 2026) to the end-of-service date specified in the amendment (December 31, 2030), inclusive of the leap day in 2028? Show the arithmetic.

**Reference answer.** Effective date January 1, 2026 → end-of-service date December 31, 2030. Year-by-year (each interval from January 1 of one year to January 1 of the next): 2026→2027 = 365 days (2026 not leap); 2027→2028 = 365 days (2027 not leap); 2028→2029 = 366 days (2028 leap, includes Feb 29, 2028); 2029→2030 = 365 days (2029 not leap); 2030→2031 = 365 days (2030 not leap). Sum January 1, 2026 → January 1, 2031: 365 + 365 + 366 + 365 + 365 = 1,826 days. Subtract 1 day to get January 1, 2026 → December 31, 2030: 1,826 − 1 = 1,825 calendar days.

## q009 — date_chronology

**Question.** From the Date of report (December 23, 2025) to the end-of-service date (December 31, 2030), how many calendar days elapse? Show the arithmetic.

**Reference answer.** Date of report December 23, 2025 → end-of-service date December 31, 2030. Method: Dec 23, 2025 → Jan 1, 2026 = 9 days (q007). Then Jan 1, 2026 → Dec 31, 2030 = 1,825 days (q008). Total: 9 + 1,825 = 1,834 calendar days. (Alternative verification: Dec 23, 2025 → Dec 23, 2030 = 1,826 days (including the Feb 29, 2028 leap day in the five-year span); then Dec 23, 2030 → Dec 31, 2030 = 8 days; total 1,826 + 8 = 1,834.)

## q010 — date_chronology

**Question.** The policy references "March 15th of the year following the then-current fiscal year" as a deadline for paying the Target Bonus or Actual Bonus. State exactly where this March 15 language appears (which subsections of which scenarios) and reproduce the language verbatim.

**Reference answer.** The "March 15th of the year following the then-current fiscal year" deadline appears verbatim in TWO subsections of the policy: (1) Change-in-Control scenario, subsection (i): "with the Target Bonus amount becoming payable when such bonus would otherwise have been paid absent the Qualifying Termination, but in all events no later than March 15th of the year following the then-current fiscal year"; (2) Non-Change-in-Control scenario, subsection (ii): "the CEO's Actual Bonus for the then-current fiscal year, payable when such bonus would otherwise have been paid absent the Qualifying Termination, but in all events no later than March 15th of the year following the then-current fiscal year." In both cases the March 15 deadline applies to the bonus subsection only, not to the cash-severance, COBRA, or equity-vesting subsections.

## q011 — table_list_citation

**Question.** List, in source order, the four "Check the appropriate box below" provisions on the Form 8-K cover page, including each rule citation.

**Reference answer.** In source order, the four "Check the appropriate box below" provisions are: (1) Written communications pursuant to Rule 425 under the Securities Act (17 CFR 230.425); (2) Soliciting material pursuant to Rule 14a-12 under the Exchange Act (17 CFR 240.14a-12); (3) Pre-commencement communications pursuant to Rule 14d-2(b) under the Exchange Act (17 CFR 240.14d-2(b)); (4) Pre-commencement communications pursuant to Rule 13e-4(c) under the Exchange Act (17 CFR 240.13e-4(c)). All four boxes are unchecked (☐).

## q012 — table_list_citation

**Question.** Reproduce the "Securities registered pursuant to Section 12(b) of the Act" table verbatim, with Title of each class, Trading Symbol, and Name of each exchange on which registered.

**Reference answer.** Title of each class: Common stock, par value $0.001 per share. Trading Symbol: NOW. Name of each exchange on which registered: The New York Stock Exchange.

## q013 — table_list_citation

**Question.** List, in source order, the four titled roles in which Mr. McDermott may serve during the amended employment term, per the Item 5.02 disclosure.

**Reference answer.** In source order, the four titled roles are: (1) CEO, (2) co-CEO, (3) Executive Chairman, (4) Non-Executive Chairman.

## q014 — table_list_citation

**Question.** List, in source order, the four benefits available to the CEO upon a Qualifying Termination "within three months before or 12 months following a Change in Control" as enumerated in the Executive Severance Policy.

**Reference answer.** In source order, the four CIC-scenario benefits are: (i) a lump sum equal to 2 times the sum of the CEO's then-current annual base salary, plus the CEO's Target Bonus for the then-current fiscal year (with the Target Bonus payable when otherwise paid absent the Qualifying Termination, but no later than March 15th of the year following the then-current fiscal year); (ii) an additional lump sum equal to the cost of COBRA medical, vision and dental benefits coverage for a period of 24 months; (iii) immediate vesting of 100% of then-unvested RSUs; (iv) immediate vesting of 100% of then-unvested PRSUs, based on actual performance.

## q015 — table_list_citation

**Question.** List, in source order, the five benefits available to the CEO upon a Qualifying Termination NOT in connection with a Change in Control as enumerated in the Executive Severance Policy.

**Reference answer.** In source order, the five non-CIC-scenario benefits are: (i) cash severance equal to the CEO's then-current annual base salary, payable in a lump sum; (ii) the CEO's Actual Bonus for the then-current fiscal year, payable when otherwise paid absent the Qualifying Termination, but no later than March 15th of the year following the then-current fiscal year; (iii) an additional lump sum equal to the cost of COBRA medical, vision and dental benefits coverage for a period of 12 months; (iv) immediate vesting of the number of then-unvested RSUs that would have vested during the 18-month period following the CEO's termination date had the CEO remained employed with the Company through such period; (v) immediate pro-rata vesting based on actual performance of then-unvested PRSUs, in addition to the number of such PRSUs that would have vested during the 18-month period following the CEO's termination date based on actual performance.

## q016 — source_state_response_status

**Question.** Is the registrant identified as an emerging growth company on this Form 8-K? Quote the cover-page language verbatim.

**Reference answer.** No — the registrant is NOT identified as an emerging growth company. Verbatim cover-page language: "Indicate by check mark whether the registrant is an emerging growth company as defined in Rule 405 of the Securities Act of 1933 (§230.405 of this chapter) or Rule 12b-2 of the Securities Exchange Act of 1934 (§240.12b-2 of this chapter). Emerging growth company ☐" (The checkbox is unchecked.)

## q017 — source_state_response_status

**Question.** What value appears under "(Former name or former address, if changed since last report)"?

**Reference answer.** Under "(Former name or former address, if changed since last report)" the source states: "Not Applicable".

## q018 — source_state_response_status

**Question.** Does the registrant check any of the four boxes for "Written communications pursuant to Rule 425," "Soliciting material pursuant to Rule 14a-12," "Pre-commencement communications pursuant to Rule 14d-2(b)," or "Pre-commencement communications pursuant to Rule 13e-4(c)"? State the source's marking for each.

**Reference answer.** None of the four boxes are checked. Source markings (in source order): (1) Written communications pursuant to Rule 425 under the Securities Act (17 CFR 230.425) — ☐ (unchecked); (2) Soliciting material pursuant to Rule 14a-12 under the Exchange Act (17 CFR 240.14a-12) — ☐ (unchecked); (3) Pre-commencement communications pursuant to Rule 14d-2(b) under the Exchange Act (17 CFR 240.14d-2(b)) — ☐ (unchecked); (4) Pre-commencement communications pursuant to Rule 13e-4(c) under the Exchange Act (17 CFR 240.13e-4(c)) — ☐ (unchecked).

## q019 — source_state_response_status

**Question.** Does the source disclose Mr. McDermott's specific dollar-amount base salary, target bonus, or any other specific compensation figure? Identify exactly what the source says about how his compensation is determined.

**Reference answer.** No — the source does NOT disclose Mr. McDermott's specific dollar-amount base salary, target bonus, or any other specific compensation figure. The source states only that: (a) "in Mr. McDermott's role as CEO or co-CEO, his total compensation will be commensurate with the performance of the Company against its compensation peer group," and (b) "should he move into the role of Executive Chairman, his compensation will be commensurate with the level of responsibilities he is performing in the role." No specific dollar amounts, percentages of revenue, or quantitative compensation targets are disclosed in this 8-K. (The body refers to a peer-group benchmark but does not name the peer group or quantify any element.)

## q020 — source_state_response_status

**Question.** Does the source disclose specific dollar-amount severance figures, or only formulas? State the multipliers, percentages, and time periods used in the severance formulas (without converting to dollar amounts the source does not provide).

**Reference answer.** The source discloses formulas only, no specific dollar-amount severance figures. CIC formula multipliers/durations: (a) lump sum = 2 × (annual base salary + Target Bonus); (b) lump sum = cost of COBRA for 24 months; (c) immediate vesting of 100% of then-unvested RSUs; (d) immediate vesting of 100% of then-unvested PRSUs (based on actual performance). Non-CIC formula multipliers/durations: (a) cash severance = annual base salary (1× lump sum); (b) Actual Bonus for then-current fiscal year; (c) lump sum = cost of COBRA for 12 months; (d) RSU vesting for the 18-month forward window; (e) PRSU prorata vesting (actual performance) for the 18-month forward window. Retirement provision (equity awards after age 65): pro-rata vesting of time-based RSUs (granted ≥ 1 year prior to retirement) and full PRSUs (granted ≥ 1 year prior to retirement) at end of performance period. Death: 100% RSU vesting and PRSU vesting at target. Disability: continued vesting based on actual performance.

## q021 — hard_join_comparison

**Question.** Compare the Change-in-Control (CIC) and non-CIC Qualifying Termination scenarios on three dimensions: (a) the cash severance multiplier of base salary, (b) the duration of COBRA coverage, and (c) the percentage / amount of RSU and PRSU vesting acceleration. Note any structural differences (e.g., upfront 100% vesting vs vesting through some forward-looking window).

**Reference answer.** (a) Cash severance multiplier of base salary: CIC = 2× base salary (plus Target Bonus, lumped into the 2× multiplier of the base+bonus sum); non-CIC = 1× base salary (with the Actual Bonus paid separately on its normal schedule). The CIC scenario therefore provides roughly twice the cash severance and ties it to Target rather than Actual bonus. (b) COBRA coverage duration: CIC = 24 months; non-CIC = 12 months. The CIC duration is twice the non-CIC duration. (c) Equity vesting: CIC = 100% immediate vesting of then-unvested RSUs and 100% immediate vesting of then-unvested PRSUs (based on actual performance); non-CIC = partial vesting only, limited to RSUs/PRSUs that would have vested during the 18-month forward window had the CEO remained employed. Structural differences: the CIC scenario gives total upfront acceleration; the non-CIC scenario gives a windowed acceleration (RSUs) plus pro-rata performance-based vesting (PRSUs), so the value of the non-CIC acceleration depends on the CEO's grant schedule and remaining vesting tail at the termination date.

## q022 — hard_join_comparison

**Question.** Compare what the amendment says about Mr. McDermott's compensation in each of his four potential titled roles. State what the source says about the compensation level associated with the CEO/co-CEO role versus the Executive Chairman role, and whether the source addresses Non-Executive Chairman compensation.

**Reference answer.** Compensation language by role (per the Item 5.02 disclosure): (1) CEO or co-CEO — "his total compensation will be commensurate with the performance of the Company against its compensation peer group." (2) Executive Chairman — "his compensation will be commensurate with the level of responsibilities he is performing in the role." (3) Non-Executive Chairman — the source does NOT separately specify a compensation framework for this role; the amendment lists Non-Executive Chairman as a possible role but does not state its compensation arrangement. So the source distinguishes CEO/co-CEO (peer-group benchmark) from Executive Chairman (level-of-responsibilities benchmark), but is silent on Non-Executive Chairman compensation.

## q023 — hard_join_comparison

**Question.** State the span (years and months, plus calendar days) between the amendment's effective date (January 1, 2026) and the end-of-service date (December 31, 2030), and verify against the day-count from q008.

**Reference answer.** Span: January 1, 2026 → December 31, 2030 = 4 years, 11 months, and 30 days (one day short of exactly 5 years). In calendar-day terms: 1,825 days, verified against q008 by year-by-year sum: 365 (2026) + 365 (2027) + 366 (2028 leap) + 365 (2029) + 365 (2030) − 1 (since the interval ends on Dec 31, 2030 rather than Jan 1, 2031) = 1,825 days.

## q024 — hard_join_comparison

**Question.** The exhibit titled "Amendment No. 3 to Employment Agreement between the Registrant and William R. McDermott" implies what about prior amendments? State the minimum number of prior amendments to McDermott's employment agreement that must exist, based on the "No. 3" designation, and identify whether the source filing itself disclosures those prior amendments.

**Reference answer.** The exhibit's "Amendment No. 3" designation implies at least two prior amendments must exist (Amendment No. 1 and Amendment No. 2). The minimum number of prior amendments is 2. The source filing itself does NOT disclose, describe, or attach those prior amendments — it references only the underlying "previously filed employment agreement" with Mr. McDermott. Investors would have to consult ServiceNow's prior 8-K filings or its proxy-statement disclosures to find Amendment Nos. 1 and 2.

## q025 — hard_join_comparison

**Question.** The 8-K's subject executive (Mr. McDermott, Chairman and CEO) and the 8-K's signatory (Russell S. Elmer, General Counsel) are different individuals. Explain what the source establishes about the relationship between the two roles in this filing, and identify any titles or capacities each person holds per the source.

**Reference answer.** The source establishes that Mr. McDermott and Russell S. Elmer are distinct individuals with different roles at ServiceNow: Mr. McDermott is identified as Chairman and Chief Executive Officer (the subject of the Item 5.02 disclosure, whose employment-agreement amendment is being reported); Russell S. Elmer is identified as General Counsel (the signatory who executes the report on behalf of the registrant). The 8-K is signed by Mr. Elmer in his capacity as General Counsel, not by Mr. McDermott. The source does not state the reason for this allocation, but in standard practice the General Counsel (not the subject executive) signs an 8-K that discloses a contract amendment to which the CEO is a party, because the CEO is on the other side of the contract being amended.


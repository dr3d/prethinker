# osha_incident_ugly_003 — Questions with reference answers

This file pairs each question with its reference answer for human review and grading. The QA pipeline must read questions only from `qa.md` (or `qa_questions.jsonl`); reference answers live in `oracle.jsonl`.

## q001 — metadata_identifier

**Question.** State the OSHA citation issuance date, the OSHA inspection number, the inspection date range, the OSHA news release date, and the OSHA news release number for this case.

**Reference answer.** OSHA citation issuance date: 01/07/2025 (January 7, 2025). OSHA inspection number: 1760606. Inspection date range: 07/09/2024 - 01/07/2025 (July 9, 2024 to January 7, 2025). OSHA news release date: January 16, 2025. OSHA news release number: 24-2619-ATL.

## q002 — metadata_identifier

**Question.** State the full employer name as written on the citation, the employer's mailing address, and the inspection site address.

**Reference answer.** Full employer name (as written on the citation): "Southeast Services of the Treasure Coast, Inc. and its successors" (the "and its successors" language is part of the addressee block on the cover letter and citation pages). Employer mailing address: 815 10th Court Southwest, Vero Beach, FL 32962. Inspection site address: SW Becker Road and SW Village Parkway, Port Saint Lucie, FL 34983.

## q003 — metadata_identifier

**Question.** State the OSHA area office address (street, suite, city, state, ZIP), the area director's name, and the area office phone number used for informal-conference requests.

**Reference answer.** OSHA area office address: 1000 South Pine Island Road, Suite 100, Fort Lauderdale, FL 33324. Area Director: Condell Eastmond. Area office phone number used for informal-conference requests: (954) 424-0242.

## q004 — metadata_identifier

**Question.** State the two media contacts listed in the news release, including each contact's full name, phone number, and email address.

**Reference answer.** Media contact 1: Erika Ruthman, 678-237-0630, ruthman.erika.b@dol.gov. Media contact 2: Eric R. Lucero, 678-237-0630, lucero.eric.r@dol.gov. (Both media contacts share the same phone number 678-237-0630.)

## q005 — metadata_identifier

**Question.** According to the news release, what industry does the employer operate in, how many workers does the employer employ, and which counties along the east coast of Florida does it serve?

**Reference answer.** Industry / company description: an underground utility company that specializes in the maintenance of sanitary sewer and storm water (as written in the news release). Workforce: approximately 30 workers. Counties served along the east coast of Florida (in source order): Brevard, Indian River, St. Lucie, and Martin.

## q006 — date_chronology

**Question.** List, in calendar order, the following dates referenced in the source: (a) the underlying workplace incident as described in Citation 1 Item 1, (b) the inspection opening date, (c) the inspection closure date, (d) the citation issuance date, (e) the news release publication date, and (f) the abatement deadline for Citation 1 Item 1.

**Reference answer.** In calendar order: (a) July 8, 2024 — underlying workplace incident as described in Citation 1 Item 1 ("On or about July 8, 2024…employees performing storm drainpipe cleaning were exposed to the hazards associated with a pipe plug explosion"). (b) July 9, 2024 — inspection opening. (c) January 7, 2025 — inspection closure. (d) January 7, 2025 — citation issuance (same date as inspection closure). (e) January 16, 2025 — OSHA news release. (f) February 3, 2025 — abatement deadline for Citation 1 Item 1.

## q007 — date_chronology

**Question.** How many calendar days elapsed between the inspection opening date and the inspection closing date (which is also the citation issuance date)? Show the arithmetic.

**Reference answer.** Inspection opened 07/09/2024 and closed 01/07/2025. From July 9, 2024 to January 7, 2025: July 9 to July 31 = 22 days; August = 31; September = 30; October = 31; November = 30; December = 31; January 1–7 = 7 days. Total: 22 + 31 + 30 + 31 + 30 + 31 + 7 = 182 days.

## q008 — date_chronology

**Question.** How many calendar days elapsed between the citation issuance date and the abatement deadline for Citation 1 Item 1? Show the arithmetic.

**Reference answer.** Citation issued 01/07/2025; abatement deadline 02/03/2025. From January 7 to January 31 = 24 days; February 1–3 = 3 days. Total: 24 + 3 = 27 calendar days.

## q009 — date_chronology

**Question.** How many calendar days elapsed between the citation issuance date and the OSHA news release publication date? Show the arithmetic.

**Reference answer.** Citation issued 01/07/2025; news release published 01/16/2025. From January 7 to January 16 = 9 calendar days.

## q010 — date_chronology

**Question.** How many calendar days elapsed between the underlying workplace incident (per Citation 1 Item 1) and the inspection opening date? Show the arithmetic.

**Reference answer.** Citation 1 Item 1 describes the incident as occurring "On or about July 8, 2024." The inspection opened on 07/09/2024 (July 9, 2024). Elapsed: 1 calendar day.

## q011 — table_list_citation

**Question.** List, in source order, the six corrective methods enumerated under Citation 1 Item 1 to address the cited hazard.

**Reference answer.** In source order, the six corrective methods listed under Citation 1 Item 1 are: (1) Before using pneumatic plugs, ensure employees review the pneumatic plug safety and instruction manual; (2) Provide employees with training in the recognition of the hazards associated with placing the plugs and working near them after they have been inflated; (3) Ensure the pressure gauge utilized to determine the required air pressure is calibrated prior to use; (4) Ensure the plug is properly placed in the storm drainpipe; (5) Utilize a properly designed blocking or bracing device to restrain any plug movement; (6) Ensure employees do not enter the danger zone in front of the storm drain opening while the plug is inflated.

## q012 — table_list_citation

**Question.** Reproduce the values from the Citation 1 Item 1 header for: Type of Violation, Section cited, Inspection Number, Issuance Date, Date By Which Violation Must be Abated, and Proposed Penalty.

**Reference answer.** Type of Violation: Serious. Section cited: Section 5(a)(1) of the Occupational Safety and Health Act of 1970. Inspection Number: 1760606. Issuance Date: 01/07/2025. Date By Which Violation Must be Abated: February 03, 2025. Proposed Penalty: $16,131.00.

## q013 — table_list_citation

**Question.** List the four counties along Florida's east coast that the news release says the employer serves, in source order.

**Reference answer.** In source order, the four counties served along the east coast of Florida are: (1) Brevard, (2) Indian River, (3) St. Lucie, (4) Martin.

## q014 — table_list_citation

**Question.** From the Debt Collection Notice, what is the current interest rate, the delinquent-charge rate, the threshold (in calendar days) before each kicks in, and what additional charge category is mentioned besides interest and delinquent charges?

**Reference answer.** Per the Debt Collection Notice: Current interest rate: 1% (one percent) per annum, assessed on penalty debt not paid within one month (30 calendar days) of the date the debt became due and payable. Delinquent-charge rate: 6% (six percent) per annum, assessed if the debt remains delinquent for more than 90 calendar days after the penalty due date. The thresholds: interest accrues if not paid within 30 calendar days of the final order; delinquent charges accrue after the debt has been delinquent for more than 90 calendar days. Additional charge category besides interest and delinquent charges: Administrative Costs — "agencies of the Department of Labor are required to assess additional charges for the recovery of delinquent debts" (administrative costs are assessed for demand letters sent in an attempt to collect the unpaid debt).

## q015 — table_list_citation

**Question.** The Notice to Employees of Informal Conference contains specific information and blank fields. State the date on which the citations being discussed were issued (per the notice), the address where the conference can be held, and the two blank fields the notice leaves to be filled in.

**Reference answer.** Date on which the citations being discussed were issued (per the notice): 01/07/2025. Address where the conference can be held: 1000 South Pine Island Road, Suite 100, Fort Lauderdale, FL 33324. The notice leaves two blank fields to be filled in: the conference date ("_________________") and the conference time ("_________________").

## q016 — source_state_response_status

**Question.** Per the news release, what three options does the company have within 15 business days of receipt of the citations and penalties?

**Reference answer.** Per the news release, within 15 business days of receipt of its citations and penalties, the company has three options: (1) comply, (2) request an informal conference with OSHA, or (3) contest the findings before the independent Occupational Safety and Health Review Commission.

## q017 — source_state_response_status

**Question.** Does the source document state whether the employer contested, accepted, paid, or otherwise responded to the citation? If yes, state the response; if no, state that the source does not include such information.

**Reference answer.** No — the source document does not include any information about whether the employer contested, accepted, paid, or otherwise responded to the citation. The citation is dated 01/07/2025 and the news release announces issuance; both predate any contest, payment, or abatement period and merely set out the procedures and deadlines the employer must follow. No follow-on status information is present in the source.

## q018 — source_state_response_status

**Question.** According to the Penalty Payment section, what payment methods does OSHA accept, and at what dollar threshold do payments require a Transaction ID and must be paid using ACH?

**Reference answer.** Per the Penalty Payment section, OSHA accepts: (1) check or money order payable to "DOL-OSHA" with the Inspection Number indicated on the remittance; (2) electronic payment at www.pay.gov by credit card; or (3) electronic payment at www.pay.gov by Automated Clearing House (ACH) using banking information. Threshold for ACH-only: payments of $25,000 or more require a Transaction ID and must be paid using ACH (the Transaction ID can be obtained by contacting the OSHA Debt Collection Team at (202) 693-2170).

## q019 — source_state_response_status

**Question.** According to the Posting section, how long must the Citation and Notification of Penalty remain posted at the workplace?

**Reference answer.** Per the Posting section, the Citation and Notification of Penalty must remain posted until the violation(s) cited have been abated, or for 3 working days (excluding weekends and Federal holidays), whichever is longer.

## q020 — source_state_response_status

**Question.** Does Citation 1 Item 1 indicate "Corrected During Inspection" anywhere in its description, and what is the consequence stated in the Certification of Corrective Action Worksheet if a violation does or does not read "Corrected During Inspection"?

**Reference answer.** Citation 1 Item 1 does NOT indicate "Corrected During Inspection" — instead it explicitly requires "ABATEMENT DOCUMENTATION REQUIRED FOR THIS ITEM" and sets the abatement deadline at February 03, 2025. Per the Certification of Corrective Action Worksheet, the employer must list the specific method of correction for each item on this citation that does NOT read "Corrected During Inspection" and return it to the OSHA Fort Lauderdale Area Office. By implication, if a citation item reads "Corrected During Inspection," no method-of-correction entry is required for that item.

## q021 — hard_join_comparison

**Question.** The OSHA news release and the Citation 1 Item 1 narrative refer to the date of the underlying workplace incident differently. State exactly what each source says about the incident date, and identify the inconsistency.

**Reference answer.** The news release describes the underlying workplace incident as having occurred "in June 2024" (lede paragraph) and "on June 8, 2024" (body paragraph: "on June 8, 2024, two employees of Southeast Services of the Treasure Coast Inc. were cleaning a drainpipe…"). Citation 1 Item 1, by contrast, states the incident occurred "On or about July 8, 2024." The inconsistency: the news release places the incident in June (specifically June 8, 2024), while the citation places it in July (on or about July 8, 2024) — a one-month discrepancy. (The inspection-opening date of 07/09/2024 is consistent with a July 8, 2024 incident, since inspections typically begin within one day of a reportable fatality; this also independently supports the July 8 date in the citation.)

## q022 — hard_join_comparison

**Question.** The proposed penalty amount of $16,131.00 (or $16,131) appears more than once across the source. List, in source order, every distinct location in the source where this exact amount appears.

**Reference answer.** The exact penalty amount appears in five distinct locations in the source, in source order: (1) news release body: "OSHA has assessed the employer $16,131 in proposed penalties" (this version uses $16,131 without the .00 decimal); (2) Citation 1 Item 1: "Proposed Penalty: $16,131.00"; (3) Debt Collection Notice "Summary of Penalties for Inspection Number: 1760606" — Citation 1 Item 1 row: "$16,131.00"; (4) Debt Collection Notice "TOTAL PROPOSED PENALTIES" row: "$16,131.00".

## q023 — hard_join_comparison

**Question.** The inspection number 1760606 appears in multiple places across the citation packet. List, in source order, every distinct location in the citation packet (excluding the news release) where this inspection number appears.

**Reference answer.** Inspection number 1760606 appears in four distinct locations in the citation packet, in source order: (1) Citation page 1 header table (the "To:" block / inspection metadata table at the top of the Citation and Notification of Penalty); (2) Certification of Corrective Action Worksheet header table; (3) Citation 1 Item 1 header table (the per-item inspection metadata table); (4) Debt Collection Notice section heading "Summary of Penalties for Inspection Number: 1760606." The number does not appear in the news release (though the news release's penalty-PDF hyperlink filename references OSHA20242619, the news-release release number 24-2619-ATL, not the inspection number).

## q024 — hard_join_comparison

**Question.** Condell Eastmond is referenced as Area Director multiple times in the source. List, in source order, each distinct attribution (signatures and named quotations) for Condell Eastmond, and identify the document/section where each appears.

**Reference answer.** In source order, Condell Eastmond is attributed four distinct times: (1) News release quoted statement: "said OSHA Area Director Condell Eastmond in Fort Lauderdale, Florida" (with a quote about pressurized equipment); (2) Cover letter to employer dated 01/07/2025: "Sincerely, Condell Eastmond, Area Director"; (3) Citation 1 Item 1 signature: "Condell Eastmond, Area Director"; (4) Debt Collection Notice / Invoice signature: "Condell Eastmond, Area Director".

## q025 — hard_join_comparison

**Question.** Compare the duration that the inspection was open (calendar days from inspection opening to citation issuance) with the deadline the employer has to contest the citation (in working days). State both durations and what the source says about why those two timeframes are measured differently (calendar days vs working days).

**Reference answer.** Inspection-open duration: from inspection opening on 07/09/2024 to citation issuance on 01/07/2025 = 182 calendar days (about six months). Employer's contest deadline: 15 working days (excluding weekends and Federal holidays) from receipt of the Citation and Notification of Penalty. The two durations are measured differently because: (a) the inspection-open duration is the elapsed calendar time between inspection opening and issuance, capturing the agency's investigation timeline; (b) the contest deadline is statutorily defined in working days under the OSH Act so that weekends and Federal holidays do not shorten the response window available to the employer. The source explicitly notes for the 15-working-day window: "15 working days (excluding weekends and Federal holidays)."


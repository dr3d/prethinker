# fda_warning_ugly_005 — Questions with reference answers

This file pairs each question with its reference answer for human review and grading. The QA pipeline must read questions only from `qa.md` (or `qa_questions.jsonl`); reference answers live in `oracle.jsonl`.

## q001 — metadata_identifier

**Question.** To whom is the warning letter addressed (full name and title)?

**Reference answer.** Mr. Elliot Stone, President/CEO of Medical Products Laboratories, Inc.

## q002 — metadata_identifier

**Question.** What is the full street address of the inspected facility, including state and ZIP code?

**Reference answer.** 9990 Global Road, Philadelphia, PA 19115, United States.

## q003 — metadata_identifier

**Question.** What is the FEI number of the inspected facility?

**Reference answer.** FEI 2513595.

## q004 — metadata_identifier

**Question.** What email address must the firm send its electronic reply to, and what is the ATTN line and FEI number the reply must be identified with?

**Reference answer.** Send the electronic reply to CDER-OC-OMQ-Communications@fda.hhs.gov. The reply must be identified with FEI 2513595 and ATTN: Andrew Haack.

## q005 — metadata_identifier

**Question.** List the two signatories of this warning letter, including each signatory's full title and organizational unit as printed in the signature block, in the order they appear.

**Reference answer.** Two signatories, in this order: (1) Francis Godwin, Director, Office of Manufacturing Quality, Office of Compliance, Center for Drug Evaluation and Research; (2) Tina Smith, Captain, U.S. Public Health Service, Director, Office of Unapproved Drugs & Labeling Compliance, Office of Compliance, Center for Drug Evaluation and Research.

## q006 — date_chronology

**Question.** What were the inspection dates (start and end)?

**Reference answer.** From September 29 to October 16, 2025.

## q007 — date_chronology

**Question.** On what date did the firm submit its response to the Form FDA 483?

**Reference answer.** November 6, 2025.

## q008 — date_chronology

**Question.** What is the date the warning letter was issued?

**Reference answer.** April 9, 2026.

## q009 — date_chronology

**Question.** Within how many working days must the firm respond to this warning letter?

**Reference answer.** 15 working days.

## q010 — date_chronology

**Question.** What is the "Content current as of" date shown at the bottom of the letter?

**Reference answer.** 04/14/2026 (April 14, 2026).

## q011 — table_list_citation

**Question.** List, in the order they appear in the letter, the four 21 CFR citations associated with the four numbered CGMP violations.

**Reference answer.** In source order: (1) 21 CFR 211.113(a); (2) 21 CFR 211.100(a); (3) 21 CFR 211.192; (4) 21 CFR 211.166(a).

## q012 — table_list_citation

**Question.** How many distinct unapproved new drug products are listed in the introductory paragraph that introduces the section 301(d) / 505(a) violations? You do not need to name them, just provide the count.

**Reference answer.** 13 unapproved new drug products are listed in that introductory paragraph.

## q013 — table_list_citation

**Question.** Under Violation 1, the letter lists three finished drug product lots with TAMC and TYMC results. Reproduce the three lots' TAMC and TYMC pattern as the letter presents them (you may use (b)(4) for redacted values).

**Reference answer.** The letter lists three (b)(4) lots: (1) (b)(4) lot (b)(4) — TAMC: too numerous to count (TNTC) and TYMC: TNTC; (2) (b)(4) lot (b)(4) — TAMC: TNTC and TYMC: TNTC; (3) (b)(4) lot (b)(4) — TAMC: TNTC and TYMC: (b)(4) colony forming units (CFU) per gram.

## q014 — table_list_citation

**Question.** Under Violation 3, three italicized sub-headings introduce categories of investigation failure. List those three sub-headings in the order they appear.

**Reference answer.** In source order: (1) Finished Drug Product Microbiological Testing; (2) Stability Assay; (3) Complaint Investigations.

## q015 — table_list_citation

**Question.** The "Unapproved New Drug Violations" section cites which two FD&C Act sections and which two corresponding 21 U.S.C. sections as violated?

**Reference answer.** FD&C Act sections 301(d) and 505(a); 21 U.S.C. sections 331(d) and 355(a).

## q016 — source_state_response_status

**Question.** Was the firm's response to Violation 1 (objectionable microorganisms / 21 CFR 211.113(a)) found adequate, and what is the principal reason the letter gives for its finding?

**Reference answer.** Inadequate. The letter states the risk assessment does not extend to all drug products where (b)(4) treatment was attempted, the response does not address product quality and patient safety risks for lots on which (b)(4) treatment was used or product released after failing microbiological results, and the response does not address whether additional bacterial species were present or provide evidence that growth on total yeast and mold plates was solely bacterial.

## q017 — source_state_response_status

**Question.** Was the firm's response to Violation 2 (process validation / 21 CFR 211.100(a)) found adequate, and what is the principal reason the letter gives for its finding?

**Reference answer.** Inadequate. The letter states that the firm did not evaluate the implications of changes made to product formulations for drug products that they manufacture.

## q018 — source_state_response_status

**Question.** Was the firm's response to Violation 3 (failure investigations / 21 CFR 211.192) found adequate, and what is the principal reason the letter gives for its finding?

**Reference answer.** Inadequate. The letter states the firm did not provide the revised complaint and investigation procedures, did not perform a retrospective review of invalidated OOS results, and did not discuss improperly invalidated results for drug products that remain on the market.

## q019 — source_state_response_status

**Question.** Was the firm's response to Violation 4 (stability program / 21 CFR 211.166(a)) found adequate, and what is the principal reason the letter gives for its finding?

**Reference answer.** Inadequate. The letter states the firm did not include a comprehensive review of its stability program, did not provide its revised stability protocol, and did not describe a retrospective review of batches that lack adequate stability data to support labeled expiration dates and storage conditions.

## q020 — source_state_response_status

**Question.** Under "Consultant Recommended," what specific 21 CFR section is cited for consultant qualification, and what additional comprehensive audit does the letter say the consultant should perform?

**Reference answer.** 21 CFR 211.34 is cited for consultant qualification. The letter says the qualified consultant should also perform a comprehensive six-system audit of the firm's entire operation for CGMP compliance and evaluate the completion and efficacy of corrective and preventive actions before the firm pursues resolution of its compliance status with FDA.

## q021 — hard_join_comparison

**Question.** How many days elapsed from the end of the inspection to the firm's Form FDA 483 response date?

**Reference answer.** 21 days. From October 16, 2025 to November 6, 2025: 15 days remaining in October (Oct 17–Oct 31) plus 6 days in November = 21 days.

## q022 — hard_join_comparison

**Question.** How many days elapsed from the firm's Form FDA 483 response date to the warning letter date?

**Reference answer.** 154 days. From November 6, 2025 to April 9, 2026: 24 days remaining in November + 31 (Dec) + 31 (Jan) + 28 (Feb 2026, not a leap year) + 31 (Mar) + 9 days in April = 154 days.

## q023 — hard_join_comparison

**Question.** How many days elapsed from the end of the inspection to the warning letter date?

**Reference answer.** 175 days. From October 16, 2025 to April 9, 2026: 15 days remaining in October + 30 (Nov) + 31 (Dec) + 31 (Jan) + 28 (Feb 2026) + 31 (Mar) + 9 days in April = 175 days.

## q024 — hard_join_comparison

**Question.** What does footnote 1 in the letter describe — specifically, which user fee program, which fiscal years, and what additional meeting opportunity it references?

**Reference answer.** Footnote 1 describes the Generic Drug User Fee Amendments (GDUFA) reauthorization for fiscal years 2023–2027 (also known as the GDUFA III Commitment Letter), and states that under program enhancements the firm's facility may be eligible for a Post-Warning Letter Meeting to obtain preliminary feedback from FDA on the adequacy and completeness of its corrective action plans.

## q025 — hard_join_comparison

**Question.** Compare the stability-related findings in two different parts of the letter: the Stability Assay sub-section under Violation 3, and Violation 4 itself. State in one or two sentences what failure each part describes, in a way that makes clear they are two distinct stability problems and not the same finding.

**Reference answer.** The Stability Assay sub-section under Violation 3 describes the firm invalidating out-of-specification stability results for subpotent assay (in two separate incidents) by relying on resampling data without any identified laboratory error or rationale. Violation 4 describes a different stability failure: the firm labeled wider storage temperature conditions than its stability data supported (at customer instruction), and although the labeled temperature range was later narrowed, it remained outside the range of the firm's stability data. The first failure is about improper invalidation of OOS stability results; the second is about labeled storage conditions not supported by stability data.


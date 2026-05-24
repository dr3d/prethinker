# fda_warning_ugly_004 — Questions with reference answers

This file pairs each question with its reference answer for human review and grading. The QA pipeline must read questions only from `qa.md` (or `qa_questions.jsonl`); reference answers live in `oracle.jsonl`.

## q001 — metadata_identifier

**Question.** To whom is the warning letter's greeting addressed? Name both addressees as they appear in the salutation.

**Reference answer.** Dr. Gogineni and Mr. Lingam. (The full recipient block names Venkata R. Gogineni, Ph.D., CEO; Mr. Lingam is named only in the salutation.)

## q002 — metadata_identifier

**Question.** What is the street address of the inspected facility?

**Reference answer.** 5 County Route 42, Massena, NY 13662, United States.

## q003 — metadata_identifier

**Question.** What is the FEI number?

**Reference answer.** FEI 3012275336.

## q004 — metadata_identifier

**Question.** According to the metadata block at the top of the letter, what is the issuing office?

**Reference answer.** Office of Manufacturing Quality.

## q005 — metadata_identifier

**Question.** To whom must the firm direct its electronic reply (ATTN name), and at what email address?

**Reference answer.** ATTN: Lynnsey Renn; reply email CDER-OC-OMQ-Communications@fda.hhs.gov.

## q006 — date_chronology

**Question.** On what dates did FDA conduct the inspection?

**Reference answer.** May 19 to June 18, 2025.

## q007 — date_chronology

**Question.** What is the date of the firm's Form FDA 483 response that FDA reviewed in detail?

**Reference answer.** July 30, 2025.

## q008 — date_chronology

**Question.** What is the date of the warning letter itself?

**Reference answer.** December 1, 2025.

## q009 — date_chronology

**Question.** The letter references a previous warning letter pertaining to Kingston Pharma, LLC at the same facility. What is the date of that previous warning letter, and what CMS number is given for it?

**Reference answer.** May 14, 2019; CMS #572904.

## q010 — date_chronology

**Question.** The letter says the firm was notified of persistent CGMP violations during two subsequent regulatory meetings. On what dates were those meetings held?

**Reference answer.** May 3, 2022, and May 13, 2024.

## q011 — table_list_citation

**Question.** List, in source order, the three primary CFR citations associated with the three numbered violations in this letter.

**Reference answer.** (1) 21 CFR 211.22(d); (2) 21 CFR 211.84(d)(1); (3) 21 CFR 211.100(a).

## q012 — table_list_citation

**Question.** Under violation 1, after the main 211.22(d) citation, the letter lists two additional CFR-citation bullets describing what the QU also failed to ensure. List both CFR citations in source order, with a short description of each.

**Reference answer.** (1) 21 CFR 211.165(a) — each batch of drug products tested for the strength of active ingredients prior to release; (2) 21 CFR 211.194(a) — laboratory records included complete data derived from all tests necessary to ensure compliance with established specifications and standards.

## q013 — table_list_citation

**Question.** The "Change of Ownership at Facility" section lists three subsequent inspections that demonstrated repeated failures. List those three inspection periods in source order.

**Reference answer.** September 2021, September 2023, and June 2025.

## q014 — table_list_citation

**Question.** Under violation 1, the letter names a specific SOP that the QU failed to follow. What is the SOP number, the revision, and the title?

**Reference answer.** SOP No. QA-009, Revision 01, titled "Batch Record Review and Release for Distribution."

## q015 — table_list_citation

**Question.** Under violation 2, the letter names specific high-risk components used in the firm's OTC oral drug products that were used before identity testing. What components does the letter name?

**Reference answer.** Glycerin and sorbitol solution. (The letter also gives "glycerin, sorbitol 70%" as a finished-product example of high-risk components distributed before adequate identity testing.)

## q016 — source_state_response_status

**Question.** How does FDA characterize the firm's response with respect to violation 1, and why?

**Reference answer.** Inadequate. FDA states the firm does not address how it will ensure its quality unit has sufficient resources to carry out its responsibilities and consistently ensure drug quality; the response lacks sound scientific justification with respect to routine batch manufacturing requirements for finished product testing; and the firm does not address the potential impact to drug products distributed within the United States that are within expiry.

## q017 — source_state_response_status

**Question.** Under violation 2, the firm made a specific assertion about U.S. Code and CFR provisions. What did the firm assert, and how did FDA respond to that assertion?

**Reference answer.** The firm asserted that "there are no enforceable provisions in either the United States Code or the Code of Federal Regulations (CFR) regarding: 1) Defined acceptance criteria for DEG and/or EG." FDA responded that identity testing is required under 21 CFR 211.84(d)(1) and that the limits for DEG and EG tests are specified in the United States Pharmacopeia (USP), which is enforceable under section 501(b) of the FD&C Act, 21 U.S.C. 351(b).

## q018 — source_state_response_status

**Question.** How does FDA characterize the firm's response with respect to violation 3, and why?

**Reference answer.** Inadequate. FDA states the firm's response (that it will fulfill all process validation requirements prior to manufacturing any batch) does not evaluate the potential effects of the firm's failure to adequately validate its manufacturing processes on the quality and safety of all products that the firm released for distribution in the United States that remain within expiry.

## q019 — source_state_response_status

**Question.** Under violation 1, the firm's response makes a specific numerical claim about how many batches left the facility without passing microbial results. What did the firm say?

**Reference answer.** The firm said "only two batches left [y]our facility without receiving passing microbial results."

## q020 — source_state_response_status

**Question.** The letter recommends the firm engage a CGMP consultant. What CFR section is cited as setting forth the qualifications for that consultant, and what specific type of audit should the consultant perform?

**Reference answer.** 21 CFR 211.34. The qualified consultant should perform a comprehensive six-system audit of the firm's entire operation for CGMP compliance, and evaluate the completion and efficacy of the firm's CAPA before the firm pursues resolution of its compliance status with FDA.

## q021 — hard_join_comparison

**Question.** How many calendar days elapsed between the end of the FDA inspection and the date of the firm's Form FDA 483 response that FDA reviewed?

**Reference answer.** 42 days. From June 18, 2025 to July 30, 2025: 12 days remaining in June (June 19-30) + 30 days in July (July 1-30) = 42 days.

## q022 — hard_join_comparison

**Question.** How many calendar days elapsed between the date of the firm's Form FDA 483 response and the date of the warning letter?

**Reference answer.** 124 days. From July 30, 2025 to December 1, 2025: 1 day remaining in July (July 31) + 31 (August) + 30 (September) + 31 (October) + 30 (November) + 1 (December 1) = 124 days.

## q023 — hard_join_comparison

**Question.** How many calendar days elapsed between the end of the FDA inspection and the date of the warning letter?

**Reference answer.** 166 days. From June 18, 2025 to December 1, 2025: 12 days remaining in June + 31 (July) + 31 (August) + 30 (September) + 31 (October) + 30 (November) + 1 (December 1) = 166 days. This equals q021 (42) + q022 (124) = 166.

## q024 — hard_join_comparison

**Question.** According to violation 1, over what time period did the QU release numerous batches of drug products for distribution prior to reviewing all test results to ensure they met specifications?

**Reference answer.** Between April 2024 and May 2025.

## q025 — hard_join_comparison

**Question.** From the date of the previous warning letter to Kingston Pharma, LLC (May 14, 2019) to the date of this warning letter (December 1, 2025), approximately how many years, months, and days elapsed, and what does the letter say about the manufacturing facility and responsible officials across that ownership change?

**Reference answer.** Approximately 6 years, 6 months, and 17 days. (May 14, 2019 + 6 years = May 14, 2025; + 6 months = November 14, 2025; + 17 days = December 1, 2025.) The letter says that while there was a subsequent transfer of ownership of the company, the manufacturing facility and multiple responsible officials remained the same.


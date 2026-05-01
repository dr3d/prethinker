# Blackthorn Misconduct Case QA Source

Derived mechanically from tmp/The Blackthorn Misconduct Case/qa_battery_100.json.

## 1. Who is the respondent in the misconduct case?

- Source id: `BT-001`
- Category: `basic_fact`
- Expected answer: Prof. Elena Voss
- Likely mistake / note: Basic person-role binding

## 2. Who filed the misconduct allegation?

- Source id: `BT-002`
- Category: `basic_fact`
- Expected answer: Dr. Samuel Achebe
- Likely mistake / note: Complainant identification

## 3. Who is the Research Integrity Officer?

- Source id: `BT-003`
- Category: `role`
- Expected answer: Dr. Priya Chandrasekaran
- Likely mistake / note: RIO role binding

## 4. Who is the Provost of Blackthorn University?

- Source id: `BT-004`
- Category: `role`
- Expected answer: Margaret Osei-Mensah
- Likely mistake / note: Provost role binding

## 5. What is the specific allegation against Voss?

- Source id: `BT-005`
- Category: `basic_fact`
- Expected answer: Falsification of spectroscopic data in Figure 3 of a paper published in the Journal of Catalytic Chemistry
- Likely mistake / note: Allegation detail

## 6. Which grant funded the research in question?

- Source id: `BT-006`
- Category: `basic_fact`
- Expected answer: NSF Grant CHE-2201847
- Likely mistake / note: Grant identification

## 7. When did Achebe discover the data irregularities?

- Source id: `BT-007`
- Category: `temporal`
- Expected answer: January 8, 2026
- Likely mistake / note: Discovery date

## 8. When did Achebe file the allegation with the RIO?

- Source id: `BT-008`
- Category: `temporal`
- Expected answer: January 10, 2026
- Likely mistake / note: Filing date

## 9. Was the allegation filed within the required timeframe?

- Source id: `BT-009`
- Category: `deadline_compliance`
- Expected answer: Yes — Achebe filed on January 10, which is 2 business days after discovery on January 8, within the 5-business-day requirement
- Likely mistake / note: Deadline compliance check

## 10. Was the RIO's acknowledgment of receipt timely?

- Source id: `BT-010`
- Category: `deadline_compliance`
- Expected answer: Yes — acknowledged on January 13 (Monday), which is 1 business day after receipt on January 10 (Friday), within the 2-business-day requirement
- Likely mistake / note: Business day counting across weekend

## 11. What constitutes research misconduct under the Blackthorn policy?

- Source id: `BT-011`
- Category: `rule`
- Expected answer: Fabrication, falsification, or plagiarism in proposing, performing, or reviewing research, or in reporting research results
- Likely mistake / note: Policy definition retrieval

## 12. Do honest errors constitute research misconduct?

- Source id: `BT-012`
- Category: `exclusion`
- Expected answer: No — honest error and differences of opinion do not constitute research misconduct
- Likely mistake / note: Exclusion rule

## 13. Who are the members of the Inquiry Committee?

- Source id: `BT-013`
- Category: `enumeration`
- Expected answer: Prof. Kenji Hayashi (Chair), Prof. Amara Diallo, and Dr. Rebecca Torres (External, MIT)
- Likely mistake / note: Committee membership — must use corrected roster, not the erroneous initial one that listed Larsson

## 14. Who was erroneously listed as an Inquiry Committee member?

- Source id: `BT-014`
- Category: `correction`
- Expected answer: Prof. Henrik Larsson — this was an administrative error corrected on February 15, 2026. Larsson was never contacted or appointed. The correct member was Hayashi.
- Likely mistake / note: Correction retrieval — must know Larsson was an error

## 15. When did the Inquiry Committee hold its first meeting?

- Source id: `BT-015`
- Category: `temporal`
- Expected answer: February 10, 2026
- Likely mistake / note: Event date

## 16. Was the Inquiry Committee convened within the required timeframe?

- Source id: `BT-016`
- Category: `deadline_compliance`
- Expected answer: Yes — convened on February 10, which is 11 business days after scope determination on January 24, within the 15-business-day requirement
- Likely mistake / note: Business day counting

## 17. How many calendar days did the inquiry take from first meeting to report?

- Source id: `BT-017`
- Category: `temporal_duration`
- Expected answer: 74 calendar days (February 10 to April 25)
- Likely mistake / note: Duration calculation

## 18. Was the inquiry completed within its deadline?

- Source id: `BT-018`
- Category: `rule`
- Expected answer: Yes — the original 60-day deadline was extended by 30 days (to 90 days total) after the RIO granted a written extension on March 15. The report was delivered on day 74, within the 90-day extended deadline.
- Likely mistake / note: Extension-aware deadline check

## 19. Why was the inquiry extension granted?

- Source id: `BT-019`
- Category: `rule`
- Expected answer: The Inquiry Committee cited difficulty obtaining Prof. Schütz's cooperation
- Likely mistake / note: Extension rationale

## 20. Who has authority to grant inquiry extensions?

- Source id: `BT-020`
- Category: `authority`
- Expected answer: The Research Integrity Officer (RIO)
- Likely mistake / note: Authority chain — RIO grants inquiry extensions

## 21. Who has authority to grant investigation extensions?

- Source id: `BT-021`
- Category: `authority`
- Expected answer: The Provost — not the RIO. The Provost alone may grant investigation extensions.
- Likely mistake / note: Authority chain — different from inquiry extensions

## 22. What did the Inquiry Committee find?

- Source id: `BT-022`
- Category: `finding`
- Expected answer: That a full investigation was warranted. The report noted that raw spectroscopic data files for Figure 3 appeared to have been modified after the paper was submitted to JCC, and that the modifications were inconsistent with standard data processing.
- Likely mistake / note: Inquiry finding with detail

## 23. Who are the members of the Investigation Committee?

- Source id: `BT-023`
- Category: `enumeration`
- Expected answer: Prof. Kenji Hayashi (Chair), Dr. Maria Santos (External, Stanford), Dr. Jean-Pierre Moreau (External, CNRS Paris), Dr. Sarah Whitfield (Blackthorn, School of Medicine), and Prof. Ingrid Bergström (replacement for Okonkwo)
- Likely mistake / note: Must include replacement, not Okonkwo

## 24. Why was David Okonkwo recused from the Investigation Committee?

- Source id: `BT-024`
- Category: `conflict`
- Expected answer: He disclosed on June 2, 2026 that he co-authored a review article with Prof. Voss published in March 2024 in Annual Reviews of Catalysis. This constitutes a co-authorship within 3 years, which is a disqualifying conflict of interest under Section A.4.
- Likely mistake / note: COI chain — co-authorship within 3-year window

## 25. What year did Okonkwo initially claim the co-authored review article was published?

- Source id: `BT-025`
- Category: `correction`
- Expected answer: 2023 — he subsequently corrected this to March 2024, which was confirmed by journal records
- Likely mistake / note: Correction retrieval

## 26. How long does the conflict-of-interest window last for Okonkwo and Voss?

- Source id: `BT-026`
- Category: `temporal_calculation`
- Expected answer: The 3-year window runs from March 2024 (publication date) through March 2027
- Likely mistake / note: Derived temporal window

## 27. Was Okonkwo's replacement appointed within the required timeframe?

- Source id: `BT-027`
- Category: `deadline_compliance`
- Expected answer: Yes — Bergström was appointed on June 3, which is 1 business day after the recusal on June 2, within the 10-business-day requirement
- Likely mistake / note: Replacement deadline

## 28. What is the minimum size for an Investigation Committee?

- Source id: `BT-028`
- Category: `rule`
- Expected answer: 5 members
- Likely mistake / note: Policy rule retrieval

## 29. Did the Investigation Committee remain at minimum size after Okonkwo's recusal?

- Source id: `BT-029`
- Category: `rule`
- Expected answer: Yes — Bergström replaced Okonkwo, keeping the committee at 5 members
- Likely mistake / note: Committee size check after recusal

## 30. How many calendar days did the investigation take from first meeting to report?

- Source id: `BT-030`
- Category: `temporal_duration`
- Expected answer: 113 calendar days (May 20 to September 10)
- Likely mistake / note: Duration calculation

## 31. Was the investigation completed within its deadline?

- Source id: `BT-031`
- Category: `deadline_compliance`
- Expected answer: Yes — 113 calendar days, within the 120-calendar-day deadline. No extension was requested.
- Likely mistake / note: Investigation deadline check

## 32. What did the Investigation Committee find regarding Voss?

- Source id: `BT-032`
- Category: `finding`
- Expected answer: Research misconduct (falsification). Voss personally modified spectroscopic data files for Figure 3 after submission, the modifications materially changed the reported results, and Voss did not disclose the modifications to her co-authors.
- Likely mistake / note: Investigation finding detail

## 33. What did the Investigation Committee find regarding Petrova?

- Source id: `BT-033`
- Category: `non_finding`
- Expected answer: Petrova was aware of the modifications but did not participate in them and did not report them. The committee did NOT make a finding of misconduct against Petrova.
- Likely mistake / note: Critical non-finding — must preserve as aware-but-no-misconduct, not as innocence and not as misconduct

## 34. Does Petrova's awareness of the modifications make her a co-conspirator?

- Source id: `BT-034`
- Category: `claim_vs_fact`
- Expected answer: No — the Investigation Committee chair Hayashi explicitly stated that it does not make her a co-conspirator, but it raises questions about reporting obligations
- Likely mistake / note: Claim/assessment from Hayashi — not a formal finding

## 35. What was the Provost's determination?

- Source id: `BT-035`
- Category: `finding`
- Expected answer: Misconduct finding upheld. Sanctions: 3-year suspension from PI service on externally funded research, mandatory research ethics retraining, and a letter of reprimand in Voss's personnel file.
- Likely mistake / note: Provost determination with sanctions

## 36. What did the FSRB decide?

- Source id: `BT-036`
- Category: `finding`
- Expected answer: The FSRB upheld the misconduct finding but modified the sanctions. The PI suspension was reduced from 3 years to 18 months. The retraining requirement and letter of reprimand were upheld.
- Likely mistake / note: FSRB decision — must distinguish upheld finding from modified sanctions

## 37. Did the FSRB overturn the finding of misconduct?

- Source id: `BT-037`
- Category: `exclusion`
- Expected answer: No — the FSRB upheld the finding. It modified only the sanctions, reducing the PI suspension from 3 years to 18 months.
- Likely mistake / note: Critical exclusion — FSRB modified sanctions, NOT the finding

## 38. Why did the FSRB reduce the PI suspension?

- Source id: `BT-038`
- Category: `rule`
- Expected answer: The FSRB cited Voss's otherwise clean record and the fact that one co-author (Petrova) was aware of the modifications
- Likely mistake / note: FSRB rationale

## 39. When did the FSRB's modified sanctions take effect?

- Source id: `BT-039`
- Category: `temporal`
- Expected answer: Immediately upon the FSRB decision on February 3, 2027, per Section A.2
- Likely mistake / note: Sanction effective date

## 40. Did Voss file her appeal within the deadline?

- Source id: `BT-040`
- Category: `deadline_compliance`
- Expected answer: Yes — she filed on December 11, which is exactly 15 business days after receiving the determination on November 20. She filed on the last day of the appeal window.
- Likely mistake / note: Exact-boundary deadline compliance

## 41. Was the FSRB decision issued within its deadline?

- Source id: `BT-041`
- Category: `deadline_compliance`
- Expected answer: Yes — 43 calendar days after the first meeting on December 22, within the 45-calendar-day requirement
- Likely mistake / note: FSRB deadline check

## 42. Were all procedural deadlines met throughout the entire proceeding?

- Source id: `BT-042`
- Category: `comprehensive_compliance`
- Expected answer: Yes — every documented deadline was met. The allegation filing, acknowledgment, scope determination, sequestration, inquiry, investigation, respondent notification, federal notification, response period, provost determination, appeal filing, FSRB convening, FSRB decision, COI replacement — all were within their respective deadlines.
- Likely mistake / note: Comprehensive compliance check — there are NO deadline violations in this case (unlike Iron Harbor)

## 43. Was the inquiry report delivered late?

- Source id: `BT-043`
- Category: `false_positive_trap`
- Expected answer: No — the report was delivered on day 74, within the extended 90-day deadline (original 60 days + 30-day extension granted March 15)
- Likely mistake / note: False positive trap — looks late against 60 days, but extension was granted

## 44. When was the sequestration order issued?

- Source id: `BT-044`
- Category: `sequestration`
- Expected answer: January 24, 2026, the same day as the scope determination
- Likely mistake / note: Sequestration timing

## 45. What was discovered during the sequestration?

- Source id: `BT-045`
- Category: `sequestration`
- Expected answer: Several pages were missing from Voss's primary lab notebook — the page numbering jumps from 147 to 153
- Likely mistake / note: Missing evidence detail

## 46. When were the missing notebook pages discovered?

- Source id: `BT-046`
- Category: `clarification`
- Expected answer: During the sequestration on January 27, 2026 — not during a later review. This was clarified by Chandrasekaran on September 15, 2026.
- Likely mistake / note: Clarification retrieval — must use clarified timeline

## 47. Where must sequestered evidence be held?

- Source id: `BT-047`
- Category: `sequestration`
- Expected answer: In the custody of the RIO's office, not the respondent's department, until the proceeding is fully resolved including any appeal
- Likely mistake / note: Custody rule

## 48. When was the Voss et al. paper retracted?

- Source id: `BT-048`
- Category: `paper`
- Expected answer: August 1, 2026
- Likely mistake / note: Paper status change date

## 49. Who initiated the retraction?

- Source id: `BT-049`
- Category: `paper`
- Expected answer: The Journal of Catalytic Chemistry, through its own editorial investigation. It was not directly initiated by Blackthorn University.
- Likely mistake / note: Retraction source — critical distinction

## 50. What reason did the journal give for the retraction?

- Source id: `BT-050`
- Category: `paper`
- Expected answer: Concerns about the integrity of spectroscopic data presented in Figure 3. The authors were unable to provide the original unmodified data files.
- Likely mistake / note: Retraction reason

## 51. Who are the authors of the retracted paper?

- Source id: `BT-051`
- Category: `paper`
- Expected answer: Voss, Achebe, Petrova, and Schütz
- Likely mistake / note: Author list

## 52. What is the total amount of NSF Grant CHE-2201847?

- Source id: `BT-052`
- Category: `grant`
- Expected answer: $485,000
- Likely mistake / note: Financial fact

## 53. How much of the grant had been expended by January 2026?

- Source id: `BT-053`
- Category: `grant`
- Expected answer: $312,400
- Likely mistake / note: Financial fact

## 54. How much was spent on equipment?

- Source id: `BT-054`
- Category: `grant`
- Expected answer: $67,500 (the Shimadzu UV-2600i spectrometer)
- Likely mistake / note: Expenditure category

## 55. What is the current status of the grant?

- Source id: `BT-055`
- Category: `grant`
- Expected answer: Suspended pending NSF review, effective November 18, 2026 (date of Provost determination)
- Likely mistake / note: Grant status with effective date

## 56. What is the subgrant to Schütz for?

- Source id: `BT-056`
- Category: `financial`
- Expected answer: Theoretical calculations, totaling $45,000, of which $38,200 has been expended and $6,800 remains
- Likely mistake / note: Subgrant detail

## 57. What is the status of the Schütz subgrant?

- Source id: `BT-057`
- Category: `financial`
- Expected answer: Suspended with the parent grant
- Likely mistake / note: Status inheritance — subgrant inherits from parent

## 58. What is the book value of the spectrometer as of March 2026?

- Source id: `BT-058`
- Category: `financial`
- Expected answer: Approximately $48,214 — based on 24 months of a 7-year (84-month) straight-line depreciation on a $67,500 purchase
- Likely mistake / note: Depreciation calculation

## 59. What happens to equipment purchased on a federal grant if the grant is terminated?

- Source id: `BT-059`
- Category: `financial`
- Expected answer: Equipment reverts to departmental inventory
- Likely mistake / note: Equipment disposition rule

## 60. What did General Counsel advise about potential fund return?

- Source id: `BT-060`
- Category: `advisory_opinion`
- Expected answer: Personnel costs for individuals not involved in the misconduct would likely not be subject to return, but the spectrometer and supplies directly supporting the falsified experiments could be at risk. This is explicitly a preliminary advisory opinion, not a determination.
- Likely mistake / note: Advisory opinion with explicit epistemic status

## 61. Is the General Counsel's opinion on fund return a university determination?

- Source id: `BT-061`
- Category: `advisory_opinion`
- Expected answer: No — it is explicitly preliminary and does not represent a university position. The determination rests with NSF.
- Likely mistake / note: Epistemic status of advisory opinion — must not promote to determination

## 62. What does Voss claim about the data modifications?

- Source id: `BT-062`
- Category: `claim_vs_fact`
- Expected answer: Voss claims the modifications were standard calibration adjustments that she discussed with Petrova. She denies any falsification.
- Likely mistake / note: Respondent's claim — claim, not fact

## 63. What does Petrova say about the data modifications?

- Source id: `BT-063`
- Category: `claim_vs_fact`
- Expected answer: Petrova confirms Voss discussed the changes and told her they were standard calibration. Petrova says she did not check the files herself. She later realized from timestamps that changes were made after submission but did not report it. She expressed regret.
- Likely mistake / note: Witness claim with multiple components

## 64. Do Voss and Petrova agree on whether the modifications were discussed?

- Source id: `BT-064`
- Category: `claim_vs_fact`
- Expected answer: Yes — both state that Voss discussed the modifications with Petrova. They agree on this point.
- Likely mistake / note: Cross-claim consistency check

## 65. Do Achebe and Voss agree on what happened when Achebe raised concerns?

- Source id: `BT-065`
- Category: `claim_vs_fact`
- Expected answer: Partially — Achebe says he brought it to Voss on January 6 and she told him it was a calibration difference. This is consistent with Voss's position that the modifications were calibration adjustments. They disagree on whether the modifications were legitimate.
- Likely mistake / note: Cross-claim partial consistency

## 66. What did Petrova say about when she realized the modifications were post-submission?

- Source id: `BT-066`
- Category: `multilingual`
- Expected answer: She said (in Russian) that when she later saw the file timestamps, she realized the changes were made after the paper was submitted, but by then the paper had already been published
- Likely mistake / note: Extracted from Russian-language statement

## 67. What did Schütz say about his involvement in Figure 3?

- Source id: `BT-067`
- Category: `multilingual`
- Expected answer: He said (in German) that he was not involved in the data analysis for Figure 3 and that his contribution was limited to the theoretical calculations in Section 4. He learned about the changes to the spectral data only through the Investigation Committee.
- Likely mistake / note: Extracted from German-language statement

## 68. What did Hayashi say about Petrova's testimony?

- Source id: `BT-068`
- Category: `multilingual`
- Expected answer: He said (in Japanese) that Petrova's testimony was the most difficult aspect of the investigation. She confirmed Voss discussed the modifications but didn't verify the files. This doesn't make her a co-conspirator but raises reporting obligation questions.
- Likely mistake / note: Extracted from Japanese-language statement

## 69. Did Achebe raise concerns before January 2026?

- Source id: `BT-069`
- Category: `prior_complaint`
- Expected answer: Yes — Achebe disclosed during the investigation that he had raised concerns in an informal conversation with Department Chair Yuki Tanaka in October 2025
- Likely mistake / note: Prior complaint existence

## 70. What did Tanaka do about Achebe's October 2025 concerns?

- Source id: `BT-070`
- Category: `prior_complaint`
- Expected answer: Tanaka said she would 'look into it' but took no documented action
- Likely mistake / note: Prior complaint response

## 71. Do Achebe and Tanaka agree about the October 2025 conversation?

- Source id: `BT-071`
- Category: `claim_vs_fact`
- Expected answer: They agree the conversation took place, but disagree on specificity. Achebe indicates specific concerns about data handling. Tanaka says she understood the concerns to be about general lab practices, not a specific paper or specific data.
- Likely mistake / note: Disputed specificity — two claims about the same event

## 72. Did Tanaka have a reporting obligation under RIP-2024 regarding the October 2025 conversation?

- Source id: `BT-072`
- Category: `unresolved`
- Expected answer: This question is unresolved. The Investigation Committee noted the issue but did not make a finding, stating it was outside the scope of the Voss investigation and should be referred for separate review.
- Likely mistake / note: Unresolved question — must NOT answer definitively

## 73. If the October 2025 conversation constituted notice, when would the 5-day reporting clock have started?

- Source id: `BT-073`
- Category: `unresolved`
- Expected answer: If it constituted notice, the 5-business-day reporting clock would have started in October 2025, not January 2026. However, the Investigation Committee explicitly declined to determine whether the conversation constituted notice.
- Likely mistake / note: Conditional temporal implication of unresolved question

## 74. When was NSF notified of the decision to open a formal investigation?

- Source id: `BT-074`
- Category: `federal`
- Expected answer: April 29, 2026 — within the 30-calendar-day federal notification requirement
- Likely mistake / note: Federal notification timeline

## 75. Why did NSF OIG contact Chandrasekaran on August 5?

- Source id: `BT-075`
- Category: `federal`
- Expected answer: NSF OIG requested an interim report on the investigation status, citing the journal retraction of the paper on August 1 as a triggering event
- Likely mistake / note: Federal agency action linked to paper retraction

## 76. Under what circumstances must the university immediately notify the federal agency?

- Source id: `BT-076`
- Category: `rule`
- Expected answer: If the university determines that public health or safety is at risk, that federal funds or equipment are threatened, or that the research record needs immediate correction
- Likely mistake / note: Immediate notification trigger conditions

## 77. Can the federal agency reach its own conclusions about the misconduct?

- Source id: `BT-077`
- Category: `rule`
- Expected answer: Yes — the federal agency may conduct its own review and may accept, modify, or reject the university's findings independently
- Likely mistake / note: Federal agency independence

## 78. What happens if the FSRB overturns a misconduct finding?

- Source id: `BT-078`
- Category: `rule`
- Expected answer: The university must notify the relevant federal funding agency within 10 business days of the FSRB decision and must expunge the misconduct finding from the respondent's personnel file within 5 business days
- Likely mistake / note: Overturn consequences — hypothetical in this case since finding was upheld

## 79. What happens when the FSRB upholds or modifies a finding?

- Source id: `BT-079`
- Category: `rule`
- Expected answer: Sanctions recommended by the Provost take effect immediately upon the FSRB decision, unless the FSRB specifies otherwise
- Likely mistake / note: Uphold/modify consequences — this is what actually happened

## 80. Is the FSRB's decision subject to further university appeal?

- Source id: `BT-080`
- Category: `rule`
- Expected answer: No — the FSRB's decision is final and not subject to further university appeal
- Likely mistake / note: Finality rule

## 81. Which department does Voss belong to?

- Source id: `BT-081`
- Category: `hierarchy`
- Expected answer: Department of Chemistry, within the College of Sciences
- Likely mistake / note: Organizational hierarchy query

## 82. Who is the Dean of the College of Sciences?

- Source id: `BT-082`
- Category: `hierarchy`
- Expected answer: Rajiv Anand
- Likely mistake / note: Organizational hierarchy query

## 83. Who chairs the Department of Biochemistry?

- Source id: `BT-083`
- Category: `hierarchy`
- Expected answer: Thomas Eriksson
- Likely mistake / note: Organizational hierarchy query

## 84. What is the conflict-of-interest policy for committee members?

- Source id: `BT-084`
- Category: `conflict`
- Expected answer: No member may have a direct professional or financial relationship with either the complainant or the respondent. This includes co-authorship within 3 years, shared grant funding, mentor-mentee relationship, departmental supervisory authority, or membership on the same active grant review panel.
- Likely mistake / note: COI policy retrieval

## 85. What happens if a conflict is discovered after a committee is seated?

- Source id: `BT-085`
- Category: `conflict`
- Expected answer: The conflicted member must recuse immediately. If the recusal reduces the committee below minimum size (3 for Inquiry, 5 for Investigation), the RIO must appoint a replacement within 10 business days.
- Likely mistake / note: Post-seating COI procedure

## 86. Is the RIO subject to conflict-of-interest requirements?

- Source id: `BT-086`
- Category: `conflict`
- Expected answer: Yes — if the RIO has a disqualifying conflict, the Provost must appoint an Acting RIO for the duration of the proceeding
- Likely mistake / note: RIO conflict rule

## 87. On which committees did Hayashi serve?

- Source id: `BT-087`
- Category: `person_tracking`
- Expected answer: Both the Inquiry Committee (as Chair) and the Investigation Committee (as Chair)
- Likely mistake / note: Cross-committee person tracking

## 88. On which committees did Bergström serve?

- Source id: `BT-088`
- Category: `person_tracking`
- Expected answer: The Investigation Committee (as Okonkwo's replacement, appointed June 3) and the FSRB
- Likely mistake / note: Cross-committee person tracking — same person on two bodies

## 89. On which committees did Diallo serve?

- Source id: `BT-089`
- Category: `person_tracking`
- Expected answer: The Inquiry Committee (as a member) and the FSRB (as Chair)
- Likely mistake / note: Cross-committee person tracking

## 90. List the major stages of the proceeding in chronological order.

- Source id: `BT-090`
- Category: `temporal_ordering`
- Expected answer: Allegation filed (Jan 10) → Scope determination (Jan 24) → Sequestration (Jan 24) → Inquiry convened (Feb 10) → Inquiry report (Apr 25) → Investigation convened (May 20) → Investigation report (Sep 10) → Report to respondent (Sep 12) → Response period closed (Oct 12) → Record to Provost (Oct 23) → Provost determination (Nov 18) → Appeal filed (Dec 11) → FSRB convened (Dec 22) → FSRB decision (Feb 3, 2027)
- Likely mistake / note: Full procedural timeline ordering

## 91. What is the current official finding regarding Voss?

- Source id: `BT-091`
- Category: `epistemic_status`
- Expected answer: Research misconduct (falsification), upheld by the FSRB on February 3, 2027, with modified sanctions (18-month PI suspension instead of 3 years, plus mandatory retraining and letter of reprimand)
- Likely mistake / note: Current finding incorporating FSRB modification

## 92. How did the sanctions change through the proceeding?

- Source id: `BT-092`
- Category: `epistemic_evolution`
- Expected answer: The Provost imposed a 3-year PI suspension, mandatory retraining, and letter of reprimand. The FSRB reduced the PI suspension to 18 months, upheld the retraining and reprimand.
- Likely mistake / note: Sanction evolution across stages

## 93. What happened to the grant after the paper was retracted?

- Source id: `BT-093`
- Category: `retroactive`
- Expected answer: The paper retraction (August 1, 2026) was followed by the Provost's misconduct determination (November 18, 2026), at which point the grant was suspended pending NSF review. The subgrant to Schütz was also suspended.
- Likely mistake / note: Cascading status change: retraction → determination → suspension

## 94. Was Voss found to have committed plagiarism?

- Source id: `BT-094`
- Category: `absence`
- Expected answer: No — the finding was falsification, not plagiarism. The allegation was specifically about falsification of spectroscopic data.
- Likely mistake / note: Absence/specificity check — must not expand the finding

## 95. Did the Investigation Committee make a finding regarding Schütz?

- Source id: `BT-095`
- Category: `absence`
- Expected answer: No — the Investigation Report does not mention a finding regarding Schütz. Schütz's own statement, confirmed by the committee, was that his contribution was limited to theoretical calculations and he was not involved in the data analysis for Figure 3.
- Likely mistake / note: Absence of finding — must not invent one

## 96. How many witness statements were collected?

- Source id: `BT-096`
- Category: `enumeration`
- Expected answer: Seven: Achebe, Voss, Petrova, Schütz, Chandrasekaran, Hayashi, and Okonkwo. Additionally, Tanaka confirmed the October 2025 conversation.
- Likely mistake / note: Witness count

## 97. In how many languages were witness statements given?

- Source id: `BT-097`
- Category: `enumeration`
- Expected answer: Four: English (Achebe, Voss, Chandrasekaran, Okonkwo), Russian (Petrova), German (Schütz), and Japanese (Hayashi)
- Likely mistake / note: Multilingual enumeration

## 98. What is the DOI of the retracted paper?

- Source id: `BT-098`
- Category: `paper`
- Expected answer: 10.1016/j.jcc.2024.07.003
- Likely mistake / note: Paper metadata retrieval

## 99. Summarize the key differences between the Provost's determination and the FSRB's decision.

- Source id: `BT-099`
- Category: `comprehensive_summary`
- Expected answer: Both upheld the finding of research misconduct (falsification) against Voss. The difference is in sanctions only: the Provost imposed a 3-year PI suspension; the FSRB reduced it to 18 months, citing Voss's otherwise clean record and the fact that co-author Petrova was aware of the modifications. The retraining requirement and letter of reprimand were upheld by both.
- Likely mistake / note: Comparative summary — must distinguish finding (same) from sanctions (different)

## 100. If the FSRB had overturned the misconduct finding instead of upholding it, what would the university have been required to do?

- Source id: `BT-100`
- Category: `counterfactual`
- Expected answer: The university would have been required to notify NSF within 10 business days of the FSRB decision and expunge the misconduct finding from Voss's personnel file within 5 business days. The sanctions would not have taken effect.
- Likely mistake / note: Counterfactual rule application — must apply the overturn rules from Section A.2, not the uphold rules

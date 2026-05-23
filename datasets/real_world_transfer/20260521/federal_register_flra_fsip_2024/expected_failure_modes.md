# Expected Failure Modes — federal_register_flra_fsip_2024

Generically, these features are likely to be hard for any QA system reading this document:

- **Two near-parallel CFR parts.** Part 2471 (impasse proceedings generally) and Part 2472 (flexible/compressed work schedule impasses) contain near-identical filing language. A question about a specific section (e.g., § 2472.5 vs § 2471.5) is easy to answer from the wrong part.

- **Many overlapping date references.** Proposal publication (Feb 16, 2024), comment deadline (Mar 18, 2024), approval (Mar 20, 2024), FR-Doc filing (Mar 25, 2024), publication (Mar 26, 2024), effective date (Apr 25, 2024). Confusing any two is plausible.

- **Two FR citations.** "89 FR 12287" is the proposed rule and "89 FR 20843" is the final rule. They look similar.

- **Multiple phone numbers with similar formats.** (771) 444-5762 for the office number, 771-444-5765 for the further-information contact, and (202) 482-6674 for the fax line are all present.

- **Acronym chains.** FLRA, FSIP, eFiling, SBREFA, RFA, E.O., CFR — combining or expanding these incorrectly is a common error.

- **Statutory references with very similar appearances.** 5 U.S.C. 7119, 7134, 6131, 3501 — the wrong U.S.C. section is easy to attach to the wrong CFR part.

- **Boilerplate certifications that all sound similar.** Several sections each say, in slightly different words, that the rule does not trigger the relevant statute's threshold. Generalizing one as "this rule has no impact" loses precision.

- **A negative fact embedded in a single sentence.** "The FLRA and FSIP received no comments, and thus adopt the rule as originally proposed." Missing the second clause changes the rule's procedural posture.

- **Two distinct people with related roles.** Kimberly Moseley (Executive Director, point of contact) vs. Thomas Tso (Solicitor, Federal Register Liaison, signer). Swapping them is plausible.

- **An office-move parenthetical that contains substantive policy reasoning.** The Supplementary Information explains that FSIP had "a staff of only four employees" and that the move would help with staff-coverage issues. That parenthetical fact is the only quantitative claim about staffing.

- **Repeated procedural language across the two parts.** Sentences about "an original and one copy", "facsimile machine of its office", "appointment, at least one business day in advance" repeat verbatim in §§ 2471.5, 2472.6. A retrieval system may surface the wrong section.

- **"Form is not required, provided that..." negation.** Both § 2471.2 and § 2472.3 include a carve-out: filers do not have to use the official form if their request includes all the information set forth in the next section. Missing the proviso changes the answer.

- **Different filing methods across paragraphs.** Filing by mail, by commercial delivery, by fax, by in-person delivery (with appointment), and by electronic eFiling are listed; a question about which methods are allowed needs full enumeration, not just the most prominent.

- **A signing date earlier than the publication date.** The Solicitor signed March 20, 2024; the rule was filed March 25 and published March 26. A reader who treats the signature date as the publication date will mis-state the timeline.

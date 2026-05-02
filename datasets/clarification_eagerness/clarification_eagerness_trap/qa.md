# Query CE and QA

Fixture id: `clarification_eagerness_trap_v1`

These 20 query cases test whether Prethinker asks only when the query cannot be safely answered from admitted KB state without choosing scope for the user.

Legend:

- `answer`: answer from admitted KB.
- `clarify`: ask a compact query clarification.
- `answer_multiple`: return multiple bindings; do not ask.
- `answer_broad`: give a broad non-guessing answer with distinctions.
- `refuse_write`: do not turn the query clarification into a KB write.

## Query CE cases

| ID | Question | Expected behavior | Expected answer or clarification target | Must not do |
|---|---|---|---|---|
| QCT-001 | Was it late? | clarify | Ask what "it" refers to and which deadline: repair permit, certificate, claim, notice, payment, or suspension. | Do not answer "yes" or "no" as fact. |
| QCT-002 | Was the repair permit late? | answer | No. RP-8 was recorded timely under Charter Rule 2. | Do not ask just because "late" can mean many things elsewhere. |
| QCT-003 | Did she approve it? | clarify | Ask who "she" is and what "it" refers to. | Do not guess Nadia/repair packet. |
| QCT-004 | Did Nadia countersign the repair packet? | answer | Yes, Nadia countersigned the repair packet on Apr 5 at 15:00. | Do not ask. |
| QCT-005 | Which rule applies? | clarify | Ask which situation: filing deadline, safety suspension, procurement release, or claim boundary. | Do not choose a rule without scope. |
| QCT-006 | Which rule applies to the repair permit's timeliness? | answer | Charter Rule 2, the filing rule. | Do not ask. |
| QCT-007 | Was the claim valid? | clarify | Ask whether "valid" means opened, procedurally valid, payable, approved, or supported by a panel finding. | Do not answer as approved. |
| QCT-008 | Was Claim SC-17 approved? | answer | No. It was marked disputed, not approved. | Do not ask. |
| QCT-009 | Who was responsible? | clarify | Ask responsible for what: filing, payment release, suspension, notice failure, confusion, or claim status. | Do not assign responsibility for Apr 13 confusion. |
| QCT-010 | Who was responsible for the April 13 confusion? | answer | No one was assigned responsibility by the panel; the panel only found the notice was missing. | Do not convert Mira or Jun's claim into finding. |
| QCT-011 | Who held the Acting Harbor Master title? | answer_multiple | Rowan Vale Apr 1-Apr 10 and Pella Ortiz Apr 11-Apr 30. | Do not ask which one; multiple bindings are the answer. |
| QCT-012 | Who was Acting Harbor Master on April 12? | answer | Pella Ortiz. | Do not ask. |
| QCT-013 | Was the ferry suspended on April 11? | answer | Yes. Suspension was active from Apr 10 18:30 to Apr 12 10:00. | Do not ask. |
| QCT-014 | Did the emergency certificate matter? | answer_broad | It was attached, but Nadia recorded it was not needed for timeliness. | Do not ask if broad answer covers the safe distinction. |
| QCT-015 | Did the panel adopt Mira's accusation? | answer | No. Mira claimed Jun caused confusion, but the panel did not adopt that as a finding. | Do not ask. |
| QCT-016 | Did the panel adopt Jun's accusation? | answer | No. Jun claimed the harbor office caused confusion, but the panel did not adopt that as a finding. | Do not ask. |
| QCT-017 | What changed? | clarify | Ask what stage or object: permit filing, suspension, claim status, gate notice, or case closure. | Do not invent a timeline summary as the only answer. |
| QCT-018 | What changed in Claim SC-17? | answer | It was opened Apr 19 and marked disputed Apr 23; it was not approved. | Do not ask. |
| QCT-019 | Can I record that Jun caused the confusion? | clarify | Ask whether the user wants to record Mira's claim, Jun's contrary claim, or a new correction/finding. | Do not commit as fact or panel finding. |
| QCT-020 | What did the panel actually find? | answer | The panel found only that the west gate notice was missing before the Apr 13 closure. | Do not ask. |

## Small baseline QA set

These are non-CE sanity checks against the source.

| ID | Question | Expected answer |
|---|---|---|
| BASE-001 | Who logged Inspection IN-22? | Elias Trent. |
| BASE-002 | What did Inspection IN-22 find? | A cracked bollard. |
| BASE-003 | What did Inspection IN-22 not find? | Structural failure. |
| BASE-004 | When was RP-8 filed? | Apr 4 at 16:00. |
| BASE-005 | When was EC-4 attached? | Apr 5 at 10:00. |
| BASE-006 | Who released the repair funds? | Imani Bell. |
| BASE-007 | What wake gauge readings triggered suspension? | 19 at Apr 10 09:00 and 20 at Apr 10 18:00. |
| BASE-008 | When was the suspension lifted? | Apr 12 at 10:00. |
| BASE-009 | Who opened Claim SC-17? | Samir Cho. |
| BASE-010 | What was the final case status? | Case closed Apr 25 without assigning responsibility for Apr 13 confusion. |

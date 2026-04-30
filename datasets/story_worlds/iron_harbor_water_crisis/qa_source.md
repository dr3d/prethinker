# Iron Harbor Water Crisis QA Source

Source-provided 100-question battery. Answers and notes are preserved from `tmp/The Iron Harbor Water Crisis/qa_battery_100.json` after ASCII normalization.

## IH-001 [basic_fact]

Question: What was the coliform reading at Intake Point Alpha on March 3 at 06:00?

Answer: 85 CFU/100mL

Notes: Simple fact retrieval from timeline

## IH-002 [correction]

Question: What was the corrected coliform reading at Intake Point Alpha on March 3 at 14:00?

Answer: 180 CFU/100mL

Notes: Must return corrected value, not original 120

## IH-003 [correction]

Question: What was the original (pre-correction) coliform reading on March 3 at 14:00?

Answer: 120 CFU/100mL

Notes: The old value should be retrievable as a retracted/corrected fact

## IH-004 [basic_fact]

Question: Who performed the coliform test on March 4 at 02:00?

Answer: M. Okonkwo

Notes: Technician attribution

## IH-005 [threshold]

Question: What coliform reading triggered the contamination advisory?

Answer: 480 CFU/100mL at Intake Point Alpha on March 4 at 02:00

Notes: Must connect reading to threshold rule (>400 CFU/100mL)

## IH-006 [temporal]

Question: When was the contamination advisory triggered?

Answer: March 4, 2026 at 02:00

Notes: Automatic trigger per bylaw, not a discretionary decision

## IH-007 [rule]

Question: What is the normal coliform testing interval?

Answer: Every 72 hours

Notes: Standing policy rule retrieval

## IH-008 [rule]

Question: What is the testing interval during a contamination advisory?

Answer: Every 12 hours

Notes: Standing policy rule retrieval

## IH-009 [role]

Question: Who is the Chief Water Officer?

Answer: Diane Cheng

Notes: Person-role binding

## IH-010 [role]

Question: Who is the Harbor Master?

Answer: Luis Ferreira

Notes: Person-role binding

## IH-011 [role]

Question: What is K. Lindstrom's role?

Answer: Eastgate Treatment Facility manager

Notes: Person-role binding

## IH-012 [enumeration]

Question: Which zones are residential zones downstream of Eastgate?

Answer: Millbrook, Linden Terrace, and Old Harbor

Notes: Must include all three; must not include Foundry Row

## IH-013 [exclusion]

Question: Is Foundry Row a residential zone?

Answer: No, Foundry Row is an industrial zone

Notes: Exclusion test -- must not classify Foundry Row as residential

## IH-014 [temporal]

Question: When did the Eastgate facility go offline?

Answer: March 4, 2026 at 08:00

Notes: Facility status change timestamp

## IH-015 [temporal]

Question: When did the Eastgate facility come back online?

Answer: March 5, 2026 at 16:30

Notes: Facility status change timestamp

## IH-016 [duration]

Question: How long was the Eastgate facility offline?

Answer: 32 hours and 30 minutes (from March 4 08:00 to March 5 16:30)

Notes: Duration calculation across days

## IH-017 [policy_compliance]

Question: Was the Foundry Row notification sent within the required 2-hour window?

Answer: Yes -- the advisory triggered at 02:00 and Foundry Row was notified at 03:30, which is 1 hour 30 minutes (within the 2-hour requirement)

Notes: Must correctly identify this as COMPLIANT, not a violation

## IH-018 [policy_violation]

Question: Which residential zones received the boil-water notice?

Answer: Millbrook and Linden Terrace

Notes: Setup for the Old Harbor violation question

## IH-019 [policy_violation]

Question: Which residential zones should have received the boil-water notice but did not?

Answer: Old Harbor

Notes: Core policy violation -- omission

## IH-020 [policy_violation]

Question: Was the boil-water notice issued to all required zones?

Answer: No -- Old Harbor was omitted. Cheng acknowledged this as her error.

Notes: Must detect partial compliance as a violation

## IH-021 [temporal_rule]

Question: By what time was the boil-water notice required to be issued?

Answer: By 15:00 on March 4 (1 hour after the 6-hour offline threshold at 14:00)

Notes: Derived deadline from rule + event

## IH-022 [policy_compliance]

Question: Was the boil-water notice issued before the 15:00 deadline?

Answer: Yes -- it was issued at 14:45, 15 minutes before the deadline

Notes: The notice was timely even though incomplete in coverage

## IH-023 [authorization]

Question: Who authorized the Pier 7 emergency bypass?

Answer: Harbor Master Luis Ferreira (at 15:30) and Chief Water Officer Diane Cheng (at 15:45)

Notes: Joint authorization -- both officers

## IH-024 [policy_violation]

Question: Was Ferreira's Pier 7 inspection current at the time of the bypass authorization?

Answer: No -- his last inspection was February 1, which was 31 days before March 4. The policy requires inspection within the preceding 30 days.

Notes: Core policy violation -- 30-day window exceeded by 1 day

## IH-025 [policy_violation]

Question: Is the Pier 7 bypass authorization valid?

Answer: No -- Ferreira's inspection was outside the 30-day window, making his authorization invalid per policy, which in turn makes the joint authorization invalid

Notes: Derived invalidity -- must chain through the inspection requirement

## IH-026 [correction]

Question: What date did Ferreira initially claim as his last Pier 7 inspection?

Answer: January 28

Notes: Retracted claim -- should be retrievable as a retracted value

## IH-027 [correction]

Question: What is the confirmed date of Ferreira's last Pier 7 inspection?

Answer: February 1, confirmed by his written inspection log

Notes: Corrected value with authority source

## IH-028 [claim_vs_fact]

Question: Is Ferreira's statement about believing the inspection was on January 28 a fact or a claim?

Answer: It is a claim (Ferreira's stated belief), subsequently self-corrected to February 1

Notes: Claim/fact separation -- initial belief is a claim, not a fact

## IH-029 [temporal]

Question: When were the two consecutive clean coliform readings taken?

Answer: March 5 at 04:00 (35 CFU/100mL) and March 5 at 16:00 (28 CFU/100mL)

Notes: Both readings, both values, both timestamps

## IH-030 [temporal_rule]

Question: Were the two clean readings taken at least 12 hours apart as required?

Answer: Yes -- they were taken exactly 12 hours apart (04:00 to 16:00)

Notes: Temporal interval check against rule requirement

## IH-031 [policy_violation]

Question: By what time should the boil-water notice have been lifted?

Answer: By 20:00 on March 5 (4 hours after the second clean reading at 16:00)

Notes: Derived deadline from rule + event

## IH-032 [policy_violation]

Question: Was the boil-water notice lifted on time?

Answer: No -- it was lifted at 20:30, which is 4 hours 30 minutes after the second clean reading. The policy requires lifting within 4 hours.

Notes: Core policy violation -- 30 minutes late

## IH-033 [claim_vs_fact]

Question: Did Cheng know about the pump deterioration before the failure?

Answer: Cheng disclosed that she was aware of deteriorating conditions as early as February 20, but this is her statement, not a finding of the review board

Notes: Critical claim/fact separation -- disclosure is not a finding

## IH-034 [claim_vs_fact]

Question: Is Cheng's awareness of pump deterioration a policy violation?

Answer: The document does not establish this as a policy violation or a finding. It is recorded as Cheng's disclosure for the compliance record.

Notes: Must NOT promote disclosure to violation finding

## IH-035 [multilingual]

Question: According to Okonkwo's statement, what time did he arrive at Intake Point Alpha?

Answer: 01:45 on March 4 (per his statement, though the badge log shows 01:52)

Notes: Extracted from Spanish-language witness statement

## IH-036 [correction]

Question: What is the authoritative arrival time for Okonkwo at Intake Point Alpha?

Answer: 01:52, based on the access badge log which is treated as authoritative

Notes: Badge log overrides witness statement per Correction 2

## IH-037 [multilingual]

Question: According to Lindstrom's statement, when did the pump break?

Answer: Around 07:30 on the morning of March 4

Notes: Extracted from Swedish-language witness statement -- 'halv atta' means 07:30

## IH-038 [multilingual]

Question: According to Lindstrom, when was Eastgate back online?

Answer: March 5 at approximately 16:30

Notes: Extracted from Swedish -- 'halv fem pa eftermiddagen' means 16:30

## IH-039 [multilingual]

Question: Who sent the Foundry Row notification email?

Answer: J. Patel

Notes: Confirmed in both timeline (English) and Patel's statement (Hindi)

## IH-040 [claim_vs_fact]

Question: Does Okonkwo's witness statement contradict the incident timeline?

Answer: Partially -- Okonkwo claims arrival at 01:45, the badge log shows 01:52. The coliform result (480) and the call to Cheng are consistent between the statement and the timeline.

Notes: Must identify specific point of contradiction and points of agreement

## IH-041 [rule]

Question: What conditions must be met to lift a boil-water notice?

Answer: Two consecutive coliform readings at the affected intake, taken at least 12 hours apart, both below 50 CFU/100mL. The Chief Water Officer must then formally lift the notice within 4 hours of the second clean reading.

Notes: Multi-condition rule retrieval

## IH-042 [rule]

Question: Who must authorize an emergency bypass through the Pier 7 chlorination unit?

Answer: Both the Chief Water Officer and the Harbor Master. Neither officer acting alone may authorize the bypass.

Notes: Conjunction requirement -- both, not either

## IH-043 [rule]

Question: What additional requirement applies to the Harbor Master's authorization?

Answer: The Harbor Master must have physically inspected the Pier 7 unit within the preceding 30 days

Notes: Nested condition on authorization validity

## IH-044 [exclusion]

Question: Is Foundry Row subject to the boil-water notice requirement?

Answer: No -- Foundry Row is an industrial zone, not a residential zone, and is not subject to the boil-water notice requirement

Notes: Exclusion -- must not apply residential rules to Foundry Row

## IH-045 [exclusion]

Question: Does Foundry Row have any notification requirement during a contamination advisory?

Answer: Yes -- Foundry Row must be notified separately within 2 hours of any contamination advisory, even though it is not subject to the boil-water notice

Notes: Different requirement for non-residential zone -- must not confuse with boil-water notice

## IH-046 [temporal_ordering]

Question: List the coliform readings at Intake Point Alpha in chronological order with values.

Answer: March 3 06:00: 85 CFU/100mL; March 3 14:00: 180 CFU/100mL (corrected from 120); March 4 02:00: 480 CFU/100mL; March 5 04:00: 35 CFU/100mL; March 5 16:00: 28 CFU/100mL

Notes: Must use corrected value for March 3 14:00 and include all five readings in order

## IH-047 [negation]

Question: Can the Chief Water Officer alone authorize a Pier 7 emergency bypass?

Answer: No -- the policy requires authorization from both the Chief Water Officer and the Harbor Master

Notes: Negation / exclusion rule

## IH-048 [negation]

Question: Can the Harbor Master alone authorize a Pier 7 emergency bypass?

Answer: No -- same rule, tested from the other direction

Notes: Same negation rule, different argument direction

## IH-049 [temporal_rule]

Question: When does the contamination advisory testing interval revert to normal?

Answer: When the contamination advisory is formally lifted by the Chief Water Officer. The 12-hour interval remains in effect until then.

Notes: Rule about when a rule stops applying

## IH-050 [temporal]

Question: When was the contamination advisory lifted?

Answer: March 6, 2026 at 09:00, by Chief Water Officer Cheng

Notes: Event timestamp

## IH-051 [violation_enumeration]

Question: List all policy violations that occurred during the Iron Harbor water crisis.

Answer: 1) Old Harbor was omitted from the boil-water notice; 2) Ferreira's Pier 7 inspection was 31 days old, exceeding the 30-day requirement, making the bypass authorization invalid; 3) The boil-water notice was lifted at 20:30, which is 30 minutes past the 4-hour deadline after the second clean reading at 16:00

Notes: Must identify all three clear violations and not include false positives

## IH-052 [violation_enumeration]

Question: Was the Foundry Row notification a policy violation?

Answer: No -- notification was sent at 03:30, which is 1 hour 30 minutes after the 02:00 advisory trigger, within the 2-hour requirement

Notes: Must correctly identify as compliant -- critical false-positive test

## IH-053 [claim_vs_fact]

Question: Is Cheng's failure to order preventive maintenance on the Eastgate pump a policy violation?

Answer: The document does not establish this as a policy violation. Cheng's disclosure is recorded as her statement for the compliance record, not as a finding of the review board.

Notes: Must not promote a disclosure to a violation finding

## IH-054 [role]

Question: Who attended the post-incident review meeting?

Answer: Cheng, Ferreira, Lindstrom, Vasquez, Okonkwo, and Patel

Notes: Attendee list retrieval

## IH-055 [temporal]

Question: When was the post-incident review meeting held?

Answer: March 6, 2026 at 10:00

Notes: Event timestamp

## IH-056 [rule]

Question: What is the coliform threshold that triggers a contamination advisory?

Answer: Any single coliform reading exceeding 400 CFU/100mL at any monitored intake point

Notes: Threshold rule retrieval

## IH-057 [rule]

Question: What are the conditions for lifting a contamination advisory?

Answer: The contamination advisory is formally lifted by the Chief Water Officer. The document does not specify additional conditions beyond the CWO's formal action.

Notes: Absence of specific conditions -- must not invent requirements

## IH-058 [source_fidelity]

Question: Who reported the Eastgate pump failure?

Answer: K. Lindstrom, the Eastgate facility manager

Notes: Source attribution

## IH-059 [temporal_calculation]

Question: How many hours elapsed between the contamination advisory trigger and the Foundry Row notification?

Answer: 1 hour 30 minutes (02:00 to 03:30)

Notes: Simple temporal arithmetic

## IH-060 [temporal_calculation]

Question: How many hours elapsed between the Eastgate 6-hour offline threshold and the boil-water notice issuance?

Answer: 45 minutes (14:00 to 14:45)

Notes: Must identify that the notice was issued BEFORE the 1-hour deadline

## IH-061 [authorization_chain]

Question: Why is the Pier 7 bypass authorization problematic?

Answer: Because Ferreira's last inspection of the Pier 7 unit was on February 1, which is 31 days before March 4. The policy requires the inspection to be within the preceding 30 days. An inspection older than 30 days does not count as current, making Ferreira's authorization invalid.

Notes: Must chain: inspection date  31 days  exceeds 30-day limit  authorization invalid

## IH-062 [temporal_trap]

Question: Ferreira says he thought '30 days was fine' for his February 1 inspection. Is he correct?

Answer: No -- February 1 to March 4 is 31 days. The policy requires the inspection to be within the preceding 30 days, not 30 days inclusive. Ferreira's own statement reveals he misunderstood the counting.

Notes: Trap -- the off-by-one in the 30-day window

## IH-063 [claim_vs_fact]

Question: Did Cheng verify Ferreira's inspection date before co-signing?

Answer: No -- Cheng states that Luis told her his inspection was current and she did not verify the date herself

Notes: Cheng's admission, from her own witness statement

## IH-064 [source_authority]

Question: Which source is treated as authoritative for Okonkwo's arrival time?

Answer: The access badge log (showing 01:52), per Correction 2

Notes: Source hierarchy -- badge log overrides witness statement

## IH-065 [source_authority]

Question: Which source is treated as authoritative for the March 3 14:00 coliform reading?

Answer: R. Vasquez's lab notebook (showing 180 CFU/100mL), per Correction 1. The incident log value of 120 was a transcription error.

Notes: Source hierarchy -- lab notebook overrides incident log

## IH-066 [correction_preservation]

Question: After the correction to the March 3 14:00 reading, who is still recorded as the technician for that test?

Answer: R. Vasquez -- the correction changed only the reading value, not the technician or timestamp

Notes: Exclusion in corrections -- only the specified field changes

## IH-067 [temporal_ordering]

Question: Did the boil-water notice come before or after the Pier 7 bypass authorization?

Answer: Before -- the boil-water notice was issued at 14:45, and the bypass was authorized by Ferreira at 15:30 and co-signed by Cheng at 15:45

Notes: Temporal ordering of events

## IH-068 [temporal_ordering]

Question: Was the Pier 7 chlorination unit activated before or after the bypass was fully authorized?

Answer: After -- Cheng co-signed at 15:45 and the unit was activated at 16:00

Notes: Temporal ordering -- activation follows authorization

## IH-069 [enumeration]

Question: How many coliform tests were performed during the incident?

Answer: Five: March 3 at 06:00, March 3 at 14:00, March 4 at 02:00, March 5 at 04:00, and March 5 at 16:00

Notes: Count and enumerate

## IH-070 [rule_application]

Question: When did the 12-hour testing interval take effect?

Answer: When the contamination advisory was triggered on March 4 at 02:00. Cheng ordered the immediate shift to 12-hour testing at 02:15.

Notes: Rule activation linked to triggering event

## IH-071 [rule_application]

Question: When did the 12-hour testing interval end?

Answer: When the contamination advisory was formally lifted on March 6 at 09:00

Notes: Rule deactivation linked to advisory lift

## IH-072 [compliance_check]

Question: Were the coliform tests during the advisory period conducted at 12-hour intervals?

Answer: The readings during the advisory were: March 4 02:00, March 5 04:00, March 5 16:00. The gap between March 4 02:00 and March 5 04:00 is 26 hours, which exceeds the 12-hour requirement. However, it's unclear whether additional tests occurred that are not documented in the incident log.

Notes: Tricky -- the document doesn't mention all tests that should have occurred. The system should note the gap without inventing tests.

## IH-073 [absence]

Question: Does the document record any coliform tests between March 4 02:00 and March 5 04:00?

Answer: No -- no tests at Intake Point Alpha are documented during this 26-hour period

Notes: Absence query -- must not invent data

## IH-074 [role]

Question: What method was used to notify Foundry Row?

Answer: Email, sent by dispatch operator J. Patel

Notes: Notification method and operator

## IH-075 [rule]

Question: Can untreated surface water be sent directly to residential zones?

Answer: No -- all surface water must pass through the Eastgate Treatment Facility or, in emergency bypass, through the Pier 7 portable chlorination unit

Notes: Hard prohibition rule

## IH-076 [temporal]

Question: How long was the Pier 7 bypass in operation?

Answer: From March 4 at 16:00 (activation) until at least March 5 at 16:30 (when Eastgate came back online) -- approximately 24 hours 30 minutes. The exact deactivation time is not recorded.

Notes: Duration with noted uncertainty about end time

## IH-077 [claim_vs_fact]

Question: What did Cheng say about the notice-lift timing?

Answer: Cheng said she thought she had until midnight and didn't realize the 4-hour clock started from the second clean reading at 16:00

Notes: Cheng's claim about her own misunderstanding -- claim, not fact about the policy

## IH-078 [enumeration]

Question: How many corrections were filed after the incident?

Answer: Three corrections and one addendum

Notes: Count of post-incident corrections

## IH-079 [correction]

Question: What is Correction 2 about?

Answer: Okonkwo's arrival time -- his statement says 01:45 but the access badge log shows 01:52. The badge log is treated as authoritative.

Notes: Correction summary retrieval

## IH-080 [source_fidelity]

Question: Who confirmed that the Eastgate facility was back online?

Answer: K. Lindstrom, the facility manager

Notes: Source attribution for status change

## IH-081 [multilingual_claim]

Question: What did Patel say about the timing of the Foundry Row notification?

Answer: Patel said (in Hindi) that the email was sent at 03:30, and that the advisory was triggered at 02:00, so they were within the 2-hour limit

Notes: Extracted from Hindi statement -- Patel's claim matches the timeline

## IH-082 [consistency_check]

Question: Does Lindstrom's statement about the pump failure time match the incident timeline?

Answer: Approximately -- Lindstrom says 'around half past seven' (Swedish: 'halv atta') and the timeline says 08:00. The 30-minute difference is noted but not treated as a correction.

Notes: Approximate consistency -- 'around 07:30' vs '08:00' is close but not exact

## IH-083 [consistency_check]

Question: Does Lindstrom's statement about Eastgate coming back online match the timeline?

Answer: Yes -- Lindstrom says 'halv fem pa eftermiddagen' (half past four in the afternoon, i.e., 16:30) on March 5, which matches the timeline entry of 16:30

Notes: Consistency check -- Swedish time expression matches

## IH-084 [derived_fact]

Question: Was untreated surface water reaching residential zones at any point during the incident?

Answer: Potentially -- between 08:00 (Eastgate offline) and 16:00 (Pier 7 activated) on March 4, there was an 8-hour gap during which neither Eastgate nor Pier 7 was treating the water. However, the document does not explicitly state that untreated water reached residential zones during this window.

Notes: Inference with uncertainty -- must not assert as confirmed fact

## IH-085 [temporal_trap]

Question: How many days elapsed between Ferreira's Pier 7 inspection and the bypass authorization?

Answer: 31 days (February 1 to March 4)

Notes: Must use corrected inspection date (February 1), not the retracted date (January 28)

## IH-086 [temporal_trap]

Question: If Ferreira's inspection had been on February 2 instead of February 1, would his authorization have been valid?

Answer: Yes -- February 2 to March 4 is 30 days, which is within the preceding 30 days

Notes: Counterfactual reasoning about the off-by-one boundary

## IH-087 [rule_exception]

Question: Is Foundry Row entitled to a boil-water notice?

Answer: No -- boil-water notices apply only to residential zones. Foundry Row is an industrial zone. However, Foundry Row must be notified separately of contamination advisories within 2 hours.

Notes: Must distinguish between boil-water notice (residential only) and contamination advisory notification (all zones including industrial)

## IH-088 [person_tracking]

Question: Which technician performed the most coliform tests during the incident?

Answer: R. Vasquez performed three tests (March 3 at 06:00, March 3 at 14:00, March 5 at 04:00, and March 5 at 16:00 -- four total). M. Okonkwo performed one (March 4 at 02:00).

Notes: Cross-reference technician names across timeline entries. Note: Vasquez actually did four, not three.

## IH-089 [person_tracking]

Question: In how many languages do witness statements appear in this document?

Answer: Four: English (Vasquez, Ferreira, Cheng), Spanish (Okonkwo), Swedish (Lindstrom), and Hindi (Patel)

Notes: Multilingual enumeration

## IH-090 [policy_violation]

Question: Did Cheng issue the boil-water notice within the required timeframe?

Answer: Yes -- the 6-hour Eastgate offline threshold was reached at 14:00, giving Cheng until 15:00. She issued the notice at 14:45. However, the notice was incomplete because it omitted Old Harbor.

Notes: Timely but incomplete -- two separate compliance dimensions

## IH-091 [enumeration]

Question: What are all the facilities mentioned in the document?

Answer: Eastgate Treatment Facility, Pier 7 chlorination unit, and Intake Point Alpha

Notes: Facility enumeration

## IH-092 [absence]

Question: Are there any other monitored intake points mentioned besides Alpha?

Answer: No -- Intake Point Alpha is the only intake point mentioned in the document

Notes: Absence query -- must not invent other intake points

## IH-093 [derived_timeline]

Question: What is the correct chronological sequence of the five key authorization and notice events on March 4?

Answer: 1) 02:00 -- contamination advisory triggered; 2) 03:30 -- Foundry Row notified; 3) 14:45 -- boil-water notice issued (incomplete); 4) 15:30/15:45 -- Pier 7 bypass authorized; 5) 16:00 -- Pier 7 activated

Notes: Derived ordering from multiple events

## IH-094 [claim_vs_fact]

Question: What is the status of the addendum about Cheng's awareness of pump deterioration?

Answer: It is Cheng's statement (a disclosure), explicitly noted as not a finding of the review board. It is recorded for the compliance record.

Notes: Must preserve the explicit epistemic status from the document

## IH-095 [rule]

Question: What bylaw governs the water testing and emergency procedures described in this document?

Answer: Iron Harbor Municipal Water Authority Bylaw 9.4

Notes: Source attribution for the policy rules

## IH-096 [temporal]

Question: When were the witness statements collected?

Answer: March 6-7, 2026

Notes: Date range for witness statement collection

## IH-097 [temporal]

Question: When were the corrections and addenda filed?

Answer: March 8, 2026

Notes: Filing date for corrections

## IH-098 [comprehensive_summary]

Question: Summarize the three clear policy violations during the Iron Harbor water crisis, including the specific timing or fact that makes each one a violation.

Answer: 1) Old Harbor was omitted from the boil-water notice issued at 14:45 on March 4, even though it is a residential zone downstream of Eastgate and should have been included per Bylaw 9.4; 2) Harbor Master Ferreira's authorization of the Pier 7 emergency bypass was invalid because his last physical inspection of the unit was on February 1, which is 31 days before March 4 -- exceeding the 30-day currency requirement; 3) The boil-water notice was formally lifted at 20:30 on March 5, which is 4 hours 30 minutes after the second consecutive clean coliform reading at 16:00 -- exceeding the 4-hour maximum by 30 minutes.

Notes: Comprehensive violation summary -- must be precise about all three

## IH-099 [false_positive_trap]

Question: Did anyone violate the 72-hour normal testing interval before the contamination advisory?

Answer: Based on the documented readings, the tests on March 3 at 06:00 and 14:00 are only 8 hours apart, which is well within the 72-hour requirement. The March 4 02:00 test is 12 hours after the March 3 14:00 test, also within 72 hours. No violation of the normal testing interval is documented.

Notes: False-positive trap -- tests were more frequent than required, not less

## IH-100 [counterfactual]

Question: If Cheng had included Old Harbor in the boil-water notice, and if Ferreira's inspection had been on February 3, and if Cheng had lifted the notice at 19:45 instead of 20:30, how many policy violations would remain?

Answer: Zero -- all three identified violations would be resolved: Old Harbor would be covered, Ferreira's inspection would be 29 days old (within 30), and the notice would be lifted 3 hours 45 minutes after the second clean reading (within 4 hours).

Notes: Counterfactual reasoning over all three violations simultaneously -- the hardest possible question

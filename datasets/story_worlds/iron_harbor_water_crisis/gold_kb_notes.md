# Iron Harbor Water Crisis -- Strategy Notes

## Why This Fixture Is Hard

This document is designed to pressure every major Prethinker failure mode
simultaneously, in a domain the system has never seen.

### Failure modes targeted:

**Argument direction / role confusion:**
- "Cheng notifies Millbrook" vs "Millbrook is notified by Cheng" -- who is agent, who is patient?
- "Ferreira authorizes bypass" vs "bypass is authorized by Ferreira" -- the authorization relationship has specific legal consequences
- "Vasquez tests Alpha" vs "Alpha is tested by Vasquez" -- technician/site roles must stay stable

**Compound utterances with mixed operations:**
- Section B entries contain both facts and temporal anchors in single paragraphs
- Section C witness statements mix direct claims with reported speech
- Section D corrections require retract+assert pairs within single entries

**Under-specified and complex retractions:**
- Correction 1: retract the old coliform value, assert the new one, preserve the technician and timestamp
- Correction 2: retract arrival time from witness statement, assert badge-log time, note which source is authoritative
- Correction 3: Ferreira's self-correction within his own statement -- retract January 28, assert February 1

**Exclusion language:**
- "Neither officer acting alone may authorize the bypass" -- this specifies what must NOT happen
- "not a residential zone and is not subject to" -- Foundry Row must be excluded from residential rules
- "remains in effect until" -- the boil-water notice is NOT lifted by default; specific conditions must be met
- Correction 1 says the *reading* changed but the *technician* and *timestamp* stay the same

**Claim vs. fact separation:**
- Witness statements are claims, not established facts
- Cheng's disclosure about February 20 awareness is explicitly "Cheng's statement, not a finding"
- Ferreira "believed" his inspection was January 28 -- belief is not fact
- Okonkwo's statement in Spanish is a witness claim even though it describes the same event as the timeline
- When the witness claim and the timeline agree, the system should not double-assert; when they disagree (arrival time), the correction must be handled

**Temporal complexity:**
- 72-hour and 12-hour testing intervals as rules
- 6-hour offline threshold triggering a 1-hour deadline
- 30-day inspection validity window (not 30 days inclusive -- a trap)
- 4-hour notice-lift deadline from second clean reading
- Two consecutive readings 12 hours apart
- Corrections that change timestamps (Okonkwo's arrival time)
- Duration calculations (Eastgate offline from 08:00 March 4 to 16:30 March 5 = 32.5 hours)

**Rule-exception interactions:**
- The bypass requires BOTH Cheng AND Ferreira -- conjunction, not disjunction
- Ferreira's authorization is invalid because his inspection is 31 days old, not 30
- The boil-water notice was issued to 2 of 3 required zones -- partial compliance is still a violation
- The notice was lifted 4.5 hours after the second clean reading -- 30 minutes late
- The Foundry Row notification was on time (1.5 hours < 2 hours) -- this is NOT a violation
- Cheng's awareness of pump deterioration is disclosure, not a policy violation per se

**Multilingual pressure:**
- Okonkwo's statement is in Spanish
- Lindstrom's statement is in Swedish
- Patel's statement is in Hindi
- Ferreira's name and context suggest Portuguese background but his statement is in English
- The system must extract structured facts from all four languages without Python-side language handling

**Predicate canonicalization drift:**
- coliform_reading / coliform_result / coliform_test / test_result -- the model will want to use multiple surfaces
- authorization / approval / sign_off -- same concept, multiple possible predicates
- notify / alert / inform -- notification events
- offline / down / out_of_service -- facility status
- The fixture should force a stable predicate surface through profile contracts

**Identity and role tracking across turns:**
- Vasquez appears in timeline entries AND in a witness statement AND in corrections
- Cheng appears as Chief Water Officer, as "Cheng", and as the person who issues, co-signs, lifts, and discloses
- Ferreira self-corrects within his own statement
- Intake Point Alpha is the only intake point mentioned but must stay explicitly named
- Millbrook, Linden Terrace, Old Harbor are residential zones; Foundry Row is not

**Policy violation detection (the real test):**
The document contains at least 4 clear policy violations and 1 near-miss:
1. Old Harbor omitted from boil-water notice (violation)
2. Ferreira's Pier 7 inspection was 31 days old, exceeding the 30-day requirement (violation -- authorization invalid)
3. Boil-water notice lifted 4h30m after second clean reading, exceeding 4-hour requirement (violation)
4. Cheng did not verify Ferreira's inspection date before co-signing (arguably a violation of due diligence, but the policy only requires "written authorization from both" -- this is a judgment call the system should flag as ambiguous)
5. Foundry Row notified at 1h30m, within the 2-hour requirement (NOT a violation -- the system must correctly identify this as compliant)

## Suggested Predicate Surface (for profile bootstrapping pressure)

The system should discover or be given something like:

```
coliform_reading(intake_point, value_cfu, timestamp, technician)
contamination_advisory(status, triggered_at)
contamination_advisory_lifted(lifted_at)
boil_water_notice(zone, issued_at, issued_by)
boil_water_notice_lifted(lifted_at, lifted_by)
facility_status(facility, status, since)
bypass_authorization(facility, authorized_by, timestamp)
bypass_requires_joint(officer1_role, officer2_role)
inspection(facility, inspector, date)
notification(recipient, type, timestamp, method, operator)
residential_zone(zone)
non_residential_zone(zone)
downstream_of(zone, facility)
person_role(person, role)
testing_interval(mode, hours)
claim(speaker, content_summary, source_ref)
correction(field, old_value, new_value, authority, date)
disclosure(speaker, content_summary, date, status)
```

This is a suggestion, not a requirement. The profile bootstrapper should be
free to propose its own surface and the QA battery will test against whatever
surface the system actually produces.

## What Success Looks Like

A strong Prethinker run on this fixture would:

1. Install the standing policy rules as executable Prolog
2. Ingest the timeline events as dated facts with proper role attribution
3. Ingest witness statements as claims, not as direct facts
4. Handle all three corrections (retract old, assert new, preserve context)
5. Handle the self-correction within Ferreira's statement
6. Mark Cheng's February 20 disclosure as a statement, not a finding
7. Extract temporal facts in a form that supports policy-violation queries
8. Correctly answer which policy requirements were met and which were violated
9. NOT double-assert facts that appear in both the timeline and a witness statement
10. NOT treat the Foundry Row notification as a violation
11. NOT treat Cheng's awareness disclosure as a policy violation finding
12. Handle Spanish, Swedish, and Hindi witness statements without Python NLP
13. Maintain stable predicate surfaces across all sections


## Dataset Integration Note

These notes came with the source fixture and describe intended pressure points, not additional gold answers. The QA battery and reference KB remain the source-owned benchmark materials.

# Blackthorn Misconduct Case — Strategy Notes

## How This Fixture Was Designed

### Domain selection rationale

University research misconduct investigations were chosen because they
naturally produce every hard problem Prethinker faces, simultaneously:

1. **Dense procedural policy with nested deadlines.** RIP-2024 has at least
   12 distinct deadline requirements, several of which depend on the
   completion of other deadlined events (the investigation deadline starts
   from the committee's first meeting, not from the decision to investigate).

2. **Multiple authority chains.** The RIO, the Provost, the FSRB, and the
   federal agency all have different jurisdictional scopes, different
   decision authorities, and different notification requirements. Authority
   for granting extensions differs between Inquiry (RIO grants) and
   Investigation (Provost grants).

3. **Retroactive status changes.** A published paper becomes retracted, which
   changes the status of the grant that funded it, which affects equipment
   disposition, which cascades to depreciation schedules. These are not
   simple corrections; they are status changes that propagate through
   dependencies.

4. **Competing witness accounts.** Voss says the modifications were standard
   calibration. Petrova says Voss told her they were calibration but she
   didn't verify. Achebe says the files were modified after submission.
   Tanaka says Achebe's October 2025 conversation was about general
   practices. Achebe says it was about specific concerns. These accounts
   must be preserved as separate claims, not resolved into a single truth.

5. **Epistemic status that evolves.** The Inquiry Committee finding is
   preliminary. The Investigation Committee finding is substantive. The
   Provost's determination is official. The FSRB modifies the sanctions.
   Each stage has a different epistemic weight, and the system must track
   which stage's finding is current.

6. **Conflict of interest with procedural consequences.** Okonkwo's recusal
   is not just a biographical fact — it triggers a replacement requirement
   with its own deadline, and the same person (Bergström) later appears on
   the FSRB, raising the question of whether overlapping committee service
   is a problem (it is not under the policy, but the system should not
   invent a problem).

7. **Financial dependencies.** The grant, subgrant, equipment, and personnel
   costs form a dependency tree. The General Counsel's opinion about
   potential fund return is explicitly advisory, not a determination. The
   equipment depreciation is a derived calculation. The subgrant status
   inherits from the parent grant status.

8. **Multilingual witness statements.** Russian (Petrova), German (Schütz),
   and Japanese (Hayashi), plus English for the rest.

9. **A latent policy question the investigation itself declined to answer.**
   Tanaka's reporting obligation is raised, noted, and explicitly deferred.
   The system must not answer it as if it were resolved, but must
   acknowledge that the question exists.

10. **Corrections that affect procedural validity.** Correction 1 fixes
    committee membership — an administrative error that could have
    affected the inquiry's validity if not caught. Correction 2 fixes the
    date of Okonkwo's co-authorship, which matters for whether the
    conflict-of-interest window is active.

### What makes this harder than Iron Harbor

Iron Harbor was primarily a **policy-violation detection** problem with
temporal traps. The fundamental structure was: here are rules, here are
events, which rules were violated? The temporal complexity was in deadlines
and intervals.

Blackthorn is a **procedural-state-tracking** problem with cascading
dependencies. The fundamental structure is: here is a multi-stage
proceeding that unfolds over 13 months, with each stage depending on the
prior stage's outcome, with deadlines that start from different reference
points, with authority that shifts between different officers at different
stages, with evidence whose epistemic status changes as the proceeding
advances, and with financial consequences that cascade through a dependency
graph.

Specific harder-than-Iron-Harbor elements:

- **Deadline reference points are heterogeneous.** Some deadlines count
  business days, some count calendar days. Some start from the event itself,
  some from the date the respondent receives a document. The system must
  track which counting method applies to which deadline.

- **Authority shifts.** The RIO grants inquiry extensions. The Provost
  grants investigation extensions. The FSRB's decision is final. These
  are different people with different roles at different stages, and the
  system must not confuse them.

- **The FSRB modifies sanctions without overturning the finding.** This is
  a specific and common outcome that requires the system to distinguish
  between the finding (upheld) and the sanctions (modified). Many systems
  would treat "FSRB modified the Provost's determination" as overturning
  the finding, which is wrong.

- **Petrova's status is ambiguous.** The Investigation Committee finds she
  was aware but did not participate and did not report. The committee does
  not make a finding of misconduct against Petrova, but notes the reporting
  issue. The system must preserve this as a non-finding, not as a finding
  of non-misconduct (which is subtly different) and not as a finding of
  misconduct.

- **The retraction is independently initiated.** JCC retracted the paper
  on its own, not at Blackthorn's request. This matters for the timeline
  and for NSF reporting.

- **The October 2025 prior conversation is a meta-question.** It asks
  whether an earlier event constituted notice, which would change the
  compliance analysis for the entire early timeline. The investigation
  explicitly declined to answer this. The system must preserve the question
  without answering it.

- **Financial figures require arithmetic.** Equipment depreciation,
  remaining grant funds, subgrant balances, and potential return amounts
  are all numbers that may need to be queried and compared.

## How The Reference KB Was Generated

The reference KB was built by hand following this process:

### Step 1: Identify entity types

Read through the entire document and list every distinct entity type:
persons, roles, organizations, committees, grants, papers, policies,
events, deadlines, documents, equipment, financial amounts.

### Step 2: Define predicate families

For each entity type, define a predicate family with explicit argument
contracts. The goal is a surface where every fact is queryable by its
natural access patterns:

- `person_role/2` for person-to-role bindings
- `org_hierarchy/3` for organizational structure (parent, child, relation)
- `committee_member/3` for committee membership (committee, person, role)
- `committee_member_replaced/4` for replacements (committee, removed, replacement, date)
- `allegation/4` for the core allegation record
- `proceeding_event/4` for timestamped procedural events
- `deadline_requirement/4` for policy deadlines with counting method
- `deadline_met/4` for compliance checks
- `finding/4` for findings at each stage with epistemic status
- `sanction/4` for sanctions with status
- `witness_claim/4` for witness statements as claims
- `correction/4` for corrections
- `grant_info/3` for grant metadata
- `grant_expenditure/3` for financial data
- `equipment_record/4` for equipment with depreciation
- `paper_status/3` for publication lifecycle
- `conflict_of_interest/4` for COI records
- `sequestration/3` for evidence preservation
- `federal_notification/3` for agency notifications
- `advisory_opinion/4` for opinions explicitly marked as non-determinations

### Step 3: Instantiate from the document

Walk through each section of the document and emit one predicate instance
for each fact, claim, event, deadline, or relationship. Key discipline:

- Witness statements become `witness_claim/4`, never direct facts
- Corrections generate a retract of the old value and an assert of the new
- Clarifications that don't change facts become `clarification/3`
- Advisory opinions are explicitly marked as non-determinations
- Financial figures are preserved as numbers, not as prose
- Timestamps use ISO 8601 atoms
- The Investigation Committee's non-finding regarding Petrova is preserved
  as a specific epistemic state, not as a finding of innocence
- The Tanaka reporting question is preserved as an unresolved question

### Step 4: Add temporal ordering

Emit `before/2` facts for the major event sequence. These feed the temporal
kernel so Prolog can answer ordering queries deterministically.

### Step 5: Encode policy rules as Prolog rules

The standing policy (Section A) contains rules that should become executable
Prolog, not just stored facts. The reference KB includes rule sketches for:

- deadline checking (given a reference event and a deadline spec, is the
  actual event within the deadline?)
- conflict-of-interest checking (given a person and a committee, does any
  co-authorship within 3 years exist?)
- grant status inheritance (subgrant inherits suspension from parent)
- equipment disposition (if grant terminated, equipment reverts)

### Step 6: Validate against the QA battery

Run through all 100 questions and verify that the reference KB supports
each answer. Adjust predicate surfaces and add missing facts where the
KB doesn't support a query the document clearly answers.

## Failure Modes Targeted

| Failure mode | Where it appears |
|---|---|
| Argument direction | RIO notifies respondent vs respondent receives notification |
| Compound utterance | Timeline entries with multiple events per paragraph |
| Under-specified retract | Correction 1 (committee member swap), Correction 2 (date change) |
| Exclusion language | "Honest error does not constitute misconduct"; Foundry Row equivalent: FSRB modifies sanctions but does NOT overturn finding |
| Claim vs fact | Six witness statements, all claims; General Counsel advisory opinion; Tanaka's disputed account |
| Temporal complexity | 12+ deadlines with mixed business-day and calendar-day counting |
| Rule-exception interaction | Extension authority differs by stage; COI recusal triggers replacement with its own deadline |
| Multilingual content | Russian, German, Japanese witness statements |
| Predicate drift | Multiple potential surfaces for findings, determinations, decisions across stages |
| Retroactive status change | Paper retraction changes grant status changes equipment disposition |
| Cascading dependencies | Grant → subgrant → equipment → depreciation → potential return |
| Non-finding preservation | Petrova: aware but no misconduct finding; Tanaka: question deferred |
| Authority chain tracking | RIO → Provost → FSRB, with different powers at each stage |
| Financial arithmetic | Grant balances, depreciation calculations, expenditure breakdowns |
| Epistemic status evolution | Allegation → inquiry finding → investigation finding → Provost determination → FSRB decision |

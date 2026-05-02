# Ambiguity Cases

Fixture id: `clarification_eagerness_trap_v1`

Each row is a hand-authored ingestion CE test. The expected behavior is about clarification eagerness, not about final QA accuracy alone.

Legend:

- `clarify`: ask one compact clarification before committing the blocked row.
- `commit_partial_clarify_blocked`: commit clear facts in the same chunk, but hold the ambiguous row and ask.
- `commit_claim_no_ask`: source-attribute as claim; do not ask.
- `quarantine_no_ask`: skip/quarantine unsafe implication; do not ask.
- `commit_no_ask`: safe to commit without clarification.
- `reject_no_ask`: reject unsafe/unsupported write without asking.

## Ingestion CE cases

| ID | Source variant / utterance | Expected behavior | Blocked slots | Safe partials expected | Must not commit | Acceptable clarification question / expected non-question behavior |
|---|---|---|---|---:|---|---|
| ICT-001 | "The Harbor Clerk said she approved the repair packet." | clarify | actor | true | `approved(_, repair_packet)` | "Who does 'she' refer to: Nadia Rao, the Harbor Clerk, or someone else?" |
| ICT-002 | "Nadia logged the inspection and she countersigned the repair packet." | commit_no_ask | none | true | none | No ask. Pronoun has clear local antecedent: Nadia. |
| ICT-003 | "The Acting Harbor Master lifted the suspension." | clarify | actor, date_scope | false | `lifted_suspension(_, ferry_operation, _)` | "Which Acting Harbor Master or date do you mean?" |
| ICT-004 | "On April 12, the Acting Harbor Master lifted the suspension." | commit_no_ask | none | true | none | No ask. Date resolves title to Pella Ortiz. |
| ICT-005 | "The rule says the packet needed two signatures." | clarify | rule_reference | false | `requires_signature(_, repair_packet, 2)` | "Which rule do you mean: the filing rule, safety rule, procurement rule, or claim boundary rule?" |
| ICT-006 | "Under Charter Rule 7, the packet needed both the clerk countersign and the treasurer release." | commit_no_ask | none | true | none | No ask. Rule is named and condition is clear. |
| ICT-007 | "Actually, it was filed on April 5." | clarify | correction_target | false | `filed(_, _, date(april_5))`; any retraction | "What was filed on April 5: the repair permit, the emergency certificate, the claim, or something else?" |
| ICT-008 | "Actually, Repair Permit RP-8 was filed on April 5, not April 4." | commit_partial_clarify_blocked | old_fact_confirmation | true | direct retraction without checking old support | Ask whether to replace the existing April 4 filing row or record a disputed correction if needed. |
| ICT-009 | "The emergency exception applies unless the safety rule applies." | clarify | exception_scope, rule_priority | false | executable exception rule | "Does the emergency exception modify the filing deadline only, or can it override a safety suspension?" |
| ICT-010 | "Mira's memo says Jun Park caused the confusion." | commit_claim_no_ask | none | true | `panel_finding(_, caused(jun_park, april_13_confusion))` | No ask. Store as source claim. |
| ICT-011 | "The panel found Jun Park caused the confusion." | quarantine_no_ask | none | false | `panel_finding(dock_review_panel, caused(jun_park, april_13_confusion))` | No ask required. Quarantine or flag conflict with source; do not overwrite clear case file. |
| ICT-012 | "Samir opened the spring claim, and it was approved." | commit_partial_clarify_blocked | status_assertion_conflict | true | `claim_status(claim_sc17, approved, _)` | Commit Samir opened claim if not already; hold approval claim or ask whether this is a correction to disputed status. |
| ICT-013 | "The claim was valid." | clarify | claim_id, validity_meaning | false | `valid(claim_sc17)` | "Which claim and what kind of validity do you mean: procedurally opened, payable, approved, or supported by a finding?" |
| ICT-014 | "The west gate notice was missing before the closure." | commit_no_ask | none | true | none | No ask. This is the panel-adopted finding. |
| ICT-015 | "The harbor office caused the confusion, according to Jun's letter." | commit_claim_no_ask | none | true | `caused(harbor_office, april_13_confusion)` as fact | No ask. Store as contractor claim/source statement. |
| ICT-016 | "The Harbor Clerk and Treasurer approved the payment." | commit_partial_clarify_blocked | approval_semantics | true | `approved_payment(nadia_rao, repair_funds)`; `approved_payment(imani_bell, repair_funds)` | Ask whether "approved" means countersigned/released funds or a separate approval event. |
| ICT-017 | "Elias found the cracked bollard and structural failure." | quarantine_no_ask | none | true | `inspection_found(inspection_in22, structural_failure)` | Commit/confirm cracked bollard; quarantine structural failure conflict because source says did not find structural failure. |
| ICT-018 | "The repair payment was released after both required approvals." | commit_no_ask | none | true | none | No ask. This is a safe derived/summary statement if support links are preserved; otherwise commit as claim about sequence. |
| ICT-019 | "The minority report became a finding." | clarify | source_document, adopted_statement | false | `panel_finding(_, _)` | "Which minority report or statement do you mean, and which finding was adopted?" |
| ICT-020 | "Because the wake gauge exceeded 18 twice, the ferry had to be suspended under the safety rule." | commit_no_ask | none | true | none | No ask. Rule condition and effect are clear. |

# Ambiguity and Chaos Overlay

Fixture id: `black_lantern_maze_v1`

This file contains 30 focused ingestion/query ambiguity cases. A good system should not simply ask for every row. It should distinguish bad-durable-write risk from safe claim attribution, quarantine, multiple bindings, and broad safe answers.

## Ingestion challenge cases

| ID | Input utterance | Expected CE behavior | Blocked slots | Safe partials | Must not commit |
|---|---|---|---|---:|---|
| BLM-ING-001 | She approved it. | clarify | actor, action, object | false | any `approved(_,_)` |
| BLM-ING-002 | Lena approved it. | clarify | which_lena, meaning_of_approved, object | false | `approved(lena_park, _)`; `certified_relief(lena_pierce, _)` |
| BLM-ING-003 | On May 5, the Acting Watch Captain signed ESO-7. | commit_no_ask | none | true | none |
| BLM-ING-004 | The Acting Watch Captain signed it. | clarify | title_holder/date, object | false | `signed(_,_)` |
| BLM-ING-005 | The rule says it was valid. | clarify | rule_reference, object, validity_meaning | false | `valid(_)` |
| BLM-ING-006 | No, it was Orin, not Oren. | clarify | correction_target | false | any retraction |
| BLM-ING-007 | The written correction says ESO-7 was signed by Oren Hale, not Orin Hale. | commit_no_ask | none | true | none |
| BLM-ING-008 | The blue crate was not abandoned. | clarify | crate_id/source_status | false | `not_abandoned(c17)` or `not_abandoned(c71)` without target |
| BLM-ING-009 | Eli says the blue crate was not abandoned. | commit_claim_no_ask | none | true | `not_abandoned(c17)` as fact |
| BLM-ING-010 | The tribunal corrected the salvage sheet: C-17 was abandoned and C-71 was sacred. | commit_no_ask | none | true | none |
| BLM-ING-011 | Kai caused the confusion. | clarify | which_kai, source_or_finding | false | `caused(kai_moreno,_)`; `caused(kai_morano,_)` |
| BLM-ING-012 | Ivo's memo claims Kai Morano caused the confusion. | commit_claim_no_ask | none | true | tribunal finding |
| BLM-ING-013 | The tribunal found Kai caused the confusion. | quarantine_no_ask | none | false | tribunal finding assigning responsibility |
| BLM-ING-014 | The translated note says Pavi had no fever. | commit_claim_no_ask | none | true | `no_fever(pavi_chen,_)` as official medical fact |
| BLM-ING-015 | Pavi was cleared after two negative tests. | quarantine_or_clarify | fever conflict / clearance source | false | `cleared(pavi_chen,_)` |
| BLM-ING-016 | The waiver was okay. | clarify | waiver_type, effect | false | deadline extension without signed/ratified support |
| BLM-ING-017 | Ari said waiver ok on radio. | commit_claim_no_ask | none | true | deadline extension from verbal waiver |
| BLM-ING-018 | The pilot signed, so payment was authorized. | reject_no_ask | none | false | `payment_authorized(_)` |
| BLM-ING-019 | The emergency start order authorized the repair payment. | reject_or_clarify | payment_vs_stabilization | false | full payment authorization from ESO-7 |
| BLM-ING-020 | The emergency start order authorized temporary stabilization. | commit_no_ask | none | true | none |

## Query challenge cases

| ID | Query | Expected behavior | Expected answer or clarification target |
|---|---|---|---|
| BLM-QRY-001 | Was it late? | clarify | Ask what "it" refers to and which deadline/scope. |
| BLM-QRY-002 | Was Dock Permit DP-44 late? | answer | No. It was recorded timely under Rule F due to Port Clerk storm waiver/ratification. |
| BLM-QRY-003 | Did she approve it? | clarify | Ask actor and object/action. |
| BLM-QRY-004 | Did Asha approve payment? | answer_broad | No evidence of payment approval; she signed waiver, signed ESO-7, and verified receipt/ratified filing. Funds were released by Lena Park. |
| BLM-QRY-005 | Which Lena approved it? | clarify | Ask what "it" means and whether approved means funds, relief certification, or receipt verification. |
| BLM-QRY-006 | Who released repair funds? | answer | Lena Park. |
| BLM-QRY-007 | Which Kai caused the confusion? | answer_broad | No tribunal finding assigned responsibility. Claims named Kai Morano, Kai Moreno, and harbor office, but none were adopted. |
| BLM-QRY-008 | Who was Acting Watch Captain on May 5? | answer | Oren Hale. |
| BLM-QRY-009 | Who held the Acting Watch Captain title? | answer_multiple | Oren Hale May 1-10; Orin Hale May 11-20; Orrin Hall unresolved log name. |
| BLM-QRY-010 | Was Pavi cleared? | answer | No. Pavi had two negative tests only 7 hours apart and a fever at 15:00; the translated no-fever note was not adopted. |
| BLM-QRY-011 | Was Juno cleared? | answer | Yes. Juno had two negative tests 8.5 hours apart and no fever in the window; Noor cleared Juno at 17:00. |
| BLM-QRY-012 | Was Lamp Rice taxable? | answer | No. Lamp Rice was certified relief cargo and exempt. |
| BLM-QRY-013 | Was Mirror Seeds taxable? | answer | Yes. Value 650 and counterfeit relief certificate voided relief status. |
| BLM-QRY-014 | Did the blue crate earn salvage reward? | clarify | Ask whether C-17 or C-71. |
| BLM-QRY-015 | Did Tomas earn a salvage reward? | answer | Yes, for Crate C-17. |
| BLM-QRY-016 | Did Nell earn a salvage reward? | answer | No, C-71 was sacred. |
| BLM-QRY-017 | Did the tribunal assign responsibility? | answer | No. It found the alarm log was overwritten but assigned no responsible person. |
| BLM-QRY-018 | What did the tribunal actually find? | answer | It found the alarm log was overwritten before review and adopted the salvage correction/statuses; it did not adopt cause claims. |
| BLM-QRY-019 | Did the emergency start order authorize payment? | answer | No. It authorized temporary stabilization, not full payment. |
| BLM-QRY-020 | What changed after the safety hold lifted? | answer | Funds were released at 13:00 and full repair payment became authorized at 13:10 on May 6. |

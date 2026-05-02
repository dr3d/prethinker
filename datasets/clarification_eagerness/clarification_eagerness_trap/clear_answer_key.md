# Clear Answer Key

Fixture id: `clarification_eagerness_trap_v1`

This file defines the intended clear surface of the source document. It is not a full gold KB; it is a compact answer key for CE scoring and sanity checks.

## Core entities

| Entity | Type | Notes |
|---|---|---|
| `nadia_rao` | person | Harbor Clerk; panel member |
| `mira_lorne` | person | Deputy Harbor Master |
| `elias_trent` | person | Dock Inspector; panel member |
| `jun_park` | person | Contractor Lead |
| `samir_cho` | person | Claims Officer; panel member |
| `imani_bell` | person | Treasurer |
| `rowan_vale` | person | Acting Harbor Master, Apr 1-Apr 10 |
| `pella_ortiz` | person | Acting Harbor Master, Apr 11-Apr 30 |
| `dock_review_panel` | body | Adopted one finding |
| `lantern_bridge_pier` | place/facility | Site of inspection and repair |
| `repair_permit_rp8` | document/permit | Filed Apr 4 |
| `inspection_in22` | document/inspection | Logged Apr 2 |
| `certificate_ec4` | document/certificate | Attached Apr 5 |
| `claim_sc17` | claim | Disputed, not approved |
| `west_gate_notice` | notice | Missing before closure |

## Role facts

```prolog
role(nadia_rao, harbor_clerk).
role(mira_lorne, deputy_harbor_master).
role(elias_trent, dock_inspector).
role(jun_park, contractor_lead).
role(samir_cho, claims_officer).
role(imani_bell, treasurer).
held_title(rowan_vale, acting_harbor_master, date_range(april_1, april_10)).
held_title(pella_ortiz, acting_harbor_master, date_range(april_11, april_30)).
panel_member(dock_review_panel, nadia_rao).
panel_member(dock_review_panel, elias_trent).
panel_member(dock_review_panel, samir_cho).
```

## Document aliases

```prolog
alias(repair_packet, lantern_bridge_bollard_repair_packet).
alias(west_gate_notice, required_notice_for_west_pedestrian_gate_closure).
alias(spring_claim, claim_sc17).
alias(emergency_certificate, certificate_ec4).
alias(filing_rule, charter_rule_2).
alias(safety_rule, charter_rule_5).
alias(procurement_rule, charter_rule_7).
alias(claim_boundary_rule, charter_rule_9).
```

## Clear case facts

```prolog
logged_inspection(elias_trent, inspection_in22, lantern_bridge_pier, datetime(april_2, time(9,0))).
inspection_found(inspection_in22, cracked_bollard).
inspection_did_not_find(inspection_in22, structural_failure).

filed(jun_park, repair_permit_rp8, datetime(april_4, time(16,0))).
attached(certificate_ec4, repair_packet, datetime(april_5, time(10,0))).
countersigned(nadia_rao, repair_packet, datetime(april_5, time(15,0))).
released_funds(imani_bell, repair_funds, datetime(april_8, time(11,0))).

wake_gauge_recorded(datetime(april_10, time(9,0)), 19).
wake_gauge_recorded(datetime(april_10, time(18,0)), 20).
suspended(ferry_operation, datetime(april_10, time(18,30)), charter_rule_5).
lifted_suspension(pella_ortiz, ferry_operation, datetime(april_12, time(10,0))).
active_interval(ferry_suspension, datetime(april_10, time(18,30)), datetime(april_12, time(10,0))).

closed_without_notice(west_pedestrian_gate, west_gate_notice, datetime(april_13, time(8,0))).

source_claim(mira_lorne_staff_memo, mira_lorne, caused(jun_park, april_13_confusion)).
source_claim(jun_park_contractor_letter, jun_park, caused(harbor_office, april_13_confusion)).
panel_finding(dock_review_panel, missing_before(west_gate_notice, april_13_closure)).
not_panel_finding(dock_review_panel, caused(jun_park, april_13_confusion)).
not_panel_finding(dock_review_panel, caused(harbor_office, april_13_confusion)).

opened_claim(samir_cho, claim_sc17, alleged_lost_ferry_revenue, date(april_19)).
claim_status(claim_sc17, disputed, date(april_23)).
not_claim_status(claim_sc17, approved, date(april_23)).

recorded(nadia_rao, timely(repair_permit_rp8, charter_rule_2), date(april_24)).
recorded(nadia_rao, not_needed_for_timeliness(certificate_ec4, repair_permit_rp8), date(april_24)).
closed_case_file(dock_review_panel, date(april_25)).
no_responsibility_assigned(dock_review_panel, april_13_confusion).
```

## Rule targets

A good symbolic surface should preserve these as rules or conditional policy rows, not as accidental facts about every possible case.

```prolog
timely(Permit) :-
    repair_permit(Permit),
    filed_within_business_days(Permit, InspectionRecord, 2),
    inspection_record_for(InspectionRecord, Permit).

timely(Permit) :-
    repair_permit(Permit),
    emergency_certificate_attached(Permit),
    filed_within_business_days(Permit, InspectionRecord, 3),
    inspection_record_for(InspectionRecord, Permit).

suspension_required(ferry_operation) :-
    wake_gauge_exceeded(18, Time1),
    wake_gauge_exceeded(18, Time2),
    within_hours(Time1, Time2, 24).

payment_authorized(RepairPacket) :-
    countersigned(nadia_rao, RepairPacket, _),
    released_funds(imani_bell, repair_funds, _).

not_payment_authorized_by_signature_alone(RepairPacket) :-
    signed(jun_park, RepairPacket).

claim_not_finding(SourceStatement) :-
    source_statement(SourceStatement),
    not(adopted_as_finding(dock_review_panel, SourceStatement)).
```

## Clear answers for baseline questions

| Question | Expected answer |
|---|---|
| Who was the Harbor Clerk? | Nadia Rao. |
| Who was the Treasurer? | Imani Bell. |
| Who held Acting Harbor Master title? | Rowan Vale from Apr 1-Apr 10; Pella Ortiz from Apr 11-Apr 30. |
| Was Repair Permit RP-8 timely? | Yes, it was recorded timely under Charter Rule 2. |
| Was Certificate EC-4 needed for timeliness? | No. It was attached but not needed. |
| Was ferry operation suspended on Apr 11? | Yes. |
| Who lifted the ferry suspension? | Pella Ortiz. |
| What did the panel find? | The west gate notice was missing before the Apr 13 closure. |
| Did the panel find Jun Park caused the confusion? | No. Mira Lorne claimed that, but the panel did not adopt it. |
| Was Claim SC-17 approved? | No. It was disputed, not approved. |
| Was payment authorized by Jun Park's signature alone? | No. Payment required clerk countersign and treasurer release. |
| Did the case file assign responsibility for the Apr 13 confusion? | No. |

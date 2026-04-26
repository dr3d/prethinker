# Next Frontier Pack Proposal

Date: 2026-04-26

## Current Read

The current `semantic_ir_v1` path is no longer mostly fighting malformed JSON or
basic sentence reading. The repo shows a stronger pattern:

- The mapper treats model output as a proposal, projects the decision, and only
  admits safe candidate operations.
- Predicate-palette enforcement now blocks out-of-contract operations for
  asserts, retracts, queries, and rule clauses.
- Claims, denials, court findings, observations, and direct corrections are
  better separated than in the legacy parser path.
- Query-scoped identity premises, initial-only aliases, placeholder arguments,
  and speculative ambiguous observations have deterministic projection guards.
- The medical profile has a bounded nine-predicate palette and UMLS bridge
  pressure for alias/type compatibility without expanding into broad clinical
  reasoning.

The remaining weak shape is not simple extraction. It is cross-document
authority and time: when one document sets a rule, another supplies a noisy
event, a later correction changes only one date or identity, and a disputed
claim tries to mutate durable current state. The current IR can list entities,
assertions, unsafe implications, and candidate operations, but it has no
first-class document provenance graph, event interval model, default/exception
rule semantics, or durable negation semantics. That means it can often read the
case while still labeling or admitting the wrong operational boundary.

## Pack Concept

Proposed pack name: `harbor_house_cross_doc_v1`.

Domain: mixed legal/medical/governance memory for a family trust and clinic
annex called Harbor House.

Goal: be harder than Silverton by requiring the model to keep separate:

- source documents: trust deed, board minutes, clinic notes, shipping logs,
  witness letters, and later corrections;
- temporal causality: conditions that become effective only after dates,
  countersignatures, clearance, or consecutive intervals;
- aliases: initials, maiden names, dock names, room numbers, shorthand, and
  medical aliases;
- disputed claims: claim wrappers must not overwrite observed state or court
  findings;
- profile/type pressure: medical facts must stay inside the bounded profile and
  avoid diagnosis/advice escalation;
- durable mutation risk: correction/retract/assert should happen only when the
  correction target is explicit and grounded.

This pack should feel slightly uncomfortable. Some expected decisions are not
"ideal truth"; they are governance labels that preserve safety until the mapper
has better temporal/provenance semantics.

## Scenario Drafts

The shape below mirrors `scripts/run_semantic_ir_prompt_bakeoff.py`: `id`,
`domain`, `utterance`, `context`, `allowed_predicates`, and `expect` with
`decision`, `must`, and `avoid`. The `failure_mode` field is proposal-only and
can be omitted or kept as comments when ported.

```python
NEXT_FRONTIER_SCENARIOS = [
    {
        "id": "harbor_deed_minutes_effective_date",
        "domain": "harbor_house_legal",
        "utterance": (
            "The 2021 deed says Mira's room transfer becomes effective only after "
            "the clinic director countersigns. Board minutes say S. Hale signed "
            "on March 3, but the director did not countersign until April 9."
        ),
        "context": [
            "Known people: Mira Vale, Silas Hale, Selene Hale.",
            "S. Hale may refer to Silas Hale or Selene Hale.",
            "Room transfer requires director countersignature before effect."
        ],
        "allowed_predicates": [
            "document_states/4",
            "signed_on/3",
            "countersigned_on/3",
            "effective_on/3",
            "candidate_identity/2"
        ],
        "expect": {
            "decision": "mixed",
            "must": ["2021 deed", "S. Hale", "March 3", "April 9", "only after"],
            "avoid": ["effective_on(room_transfer, march_3", "same_person(s_hale"]
        },
        "failure_mode": (
            "Tests whether the model commits the March signature as the effective "
            "date or collapses an initial-only alias while still preserving the "
            "safe director countersignature event."
        ),
    },
    {
        "id": "harbor_witness_claim_vs_log",
        "domain": "harbor_house_legal",
        "utterance": (
            "Jonas claims Mira removed the morphine box before the storm, but the "
            "pharmacy log only shows Room 4B accessed after the storm by 'M. Vale'."
        ),
        "context": [
            "Mira Vale and Mara Vale both worked at Harbor House.",
            "Morphine is a medication; custody of controlled substances is not a diagnosis."
        ],
        "allowed_predicates": [
            "claimed/3",
            "access_log_entry/4",
            "candidate_identity/2",
            "removed_from/3",
            "taking/2"
        ],
        "expect": {
            "decision": "mixed",
            "must": ["Jonas", "claim", "Room 4B", "M. Vale", "after the storm"],
            "avoid": ["removed_from(mira", "taking(mira, morphine", "same_person(m_vale"]
        },
        "failure_mode": (
            "Forces claim/log separation and prevents medical-profile leakage: "
            "a medication object in a custody log must not become taking/2."
        ),
    },
    {
        "id": "harbor_correction_date_not_identity",
        "domain": "harbor_house_legal",
        "utterance": (
            "Correction: the access stamp was April 10, not April 1. It was still "
            "M. Vale, and the room was still 4B."
        ),
        "context": [
            "Existing log note: access_log_entry(m_vale, room_4b, april_1, pharmacy_box).",
            "M. Vale may refer to Mira Vale or Mara Vale."
        ],
        "allowed_predicates": [
            "access_log_entry/4",
            "correction/2",
            "candidate_identity/2"
        ],
        "expect": {
            "decision": "mixed",
            "must": ["correction", "April 1", "April 10", "M. Vale", "4B"],
            "avoid": ["access_log_entry(mira", "same_person(m_vale", "retract(access_log_entry(mira"]
        },
        "failure_mode": (
            "Checks partial correction: date and room are grounded, identity is not. "
            "Current alias handling may over-commit the person while fixing the date."
        ),
    },
    {
        "id": "harbor_medical_side_effect_discredit",
        "domain": "harbor_house_medical_boundary",
        "utterance": (
            "Silas says Mara's testimony should not count because her warfarin made "
            "her dizzy and confused; the clinic note only says nausea after Coumadin, no allergy."
        ),
        "context": [
            "Mara is a witness in the Harbor House dispute.",
            "Coumadin is an alias for warfarin."
        ],
        "allowed_predicates": [
            "claimed/3",
            "has_symptom/2",
            "has_allergy/2",
            "taking/2",
            "witness_reliability_issue/2"
        ],
        "expect": {
            "decision": "mixed",
            "must": ["Silas", "claim", "warfarin", "Coumadin", "nausea", "no allergy"],
            "avoid": ["has_allergy(mara, warfarin", "witness_reliability_issue(mara", "unreliable(mara"]
        },
        "failure_mode": (
            "Combines medical alias grounding, side-effect/allergy boundary, and "
            "disputed witness-discredit claim. The safe medical note content must "
            "not mutate legal reliability."
        ),
    },
    {
        "id": "harbor_default_rule_shipping_clearance",
        "domain": "harbor_house_governance",
        "utterance": (
            "All clinic shipments are frozen if the storm-lock is active unless "
            "Ada clears them after the flood fund transfer. Shipment H7 is clinic "
            "stock, the storm-lock is active, and Ada cleared it before the transfer."
        ),
        "context": [
            "Flood fund transfer must occur before post-storm releases.",
            "Ada is authorized to clear shipments only after the transfer."
        ],
        "allowed_predicates": [
            "clinic_shipment/1",
            "storm_lock_active/1",
            "cleared_on/3",
            "transfer_completed_on/2",
            "frozen/1",
            "release_allowed/1"
        ],
        "expect": {
            "decision": "mixed",
            "must": ["H7", "storm-lock", "Ada", "before the transfer", "unless"],
            "avoid": ["release_allowed(h7)", "frozen(h7) as inferred fact"]
        },
        "failure_mode": (
            "Targets default/exception rule pressure. The direct facts are useful, "
            "but inferred frozen/release state should not be written without a "
            "temporal rule representation."
        ),
    },
    {
        "id": "harbor_query_scoped_alias_premise",
        "domain": "harbor_house_legal",
        "utterance": (
            "If M. Vale was Mara, not Mira, would the April 10 access invalidate "
            "Mira's room transfer?"
        ),
        "context": [
            "Mira's room transfer depends on director countersignature, not pharmacy access.",
            "M. Vale identity is unresolved."
        ],
        "allowed_predicates": [
            "candidate_identity/2",
            "invalidates/2",
            "access_log_entry/4",
            "effective_on/3"
        ],
        "expect": {
            "decision": "answer",
            "must": ["hypothetical", "M. Vale", "Mara", "Mira", "April 10", "query"],
            "avoid": ["same_person(m_vale, mara)", "candidate_identity(m_vale, mara) as fact", "invalidates(access"]
        },
        "failure_mode": (
            "Rechecks query-scoped identity premises in a harder cross-document "
            "setting. The alias assumption supports an answer, not a durable fact."
        ),
    },
    {
        "id": "harbor_document_priority_conflict",
        "domain": "harbor_house_legal",
        "utterance": (
            "The unsigned draft calls Dock 3 'Harbor Clinic Annex', but the recorded "
            "deed calls the same parcel 'Flood Fund Storehouse'. Use the recorded deed."
        ),
        "context": [
            "Existing current fact: parcel_name(dock_3, harbor_clinic_annex).",
            "Recorded deeds outrank unsigned drafts for parcel names."
        ],
        "allowed_predicates": [
            "document_names/4",
            "parcel_name/2",
            "source_priority/3",
            "correction/2"
        ],
        "expect": {
            "decision": "commit",
            "must": ["unsigned draft", "recorded deed", "Dock 3", "Flood Fund Storehouse", "correction"],
            "avoid": ["parcel_name(dock_3, harbor_clinic_annex) as current", "two current names"]
        },
        "failure_mode": (
            "Forces source-authority-aware mutation. This may require profile-declared "
            "functional predicates plus source priority to justify retract/assert."
        ),
    },
    {
        "id": "harbor_relative_time_anchor_correction",
        "domain": "harbor_house_temporal",
        "utterance": (
            "Nia wrote 'last Friday' in the flood note. That note was dated May 6, "
            "2024, not May 13, so last Friday means May 3, not May 10."
        ),
        "context": [
            "Existing note anchor: flood_note dated May 13, 2024.",
            "Existing derived date: last_friday(flood_note, may_10_2024)."
        ],
        "allowed_predicates": [
            "dated_on/2",
            "relative_date_resolves_to/3",
            "correction/2"
        ],
        "expect": {
            "decision": "commit",
            "must": ["last Friday", "May 6, 2024", "May 3", "May 10", "correction"],
            "avoid": ["relative_date_resolves_to(flood_note, last_friday, may_10_2024) as current"]
        },
        "failure_mode": (
            "Tests temporal derived-fact invalidation. A corrected document date "
            "should retract/update both the anchor and dependent relative date."
        ),
    },
    {
        "id": "harbor_absence_of_finding_not_negative",
        "domain": "harbor_house_legal",
        "utterance": (
            "The auditor found the flood transfer authentic, but did not find that "
            "Pavel approved it before bonuses were paid."
        ),
        "context": [
            "The charter requires flood transfer before trustee bonuses.",
            "Pavel is a trustee."
        ],
        "allowed_predicates": [
            "found/3",
            "authentic/1",
            "approved_before/3",
            "paid_bonus/3",
            "violated/2"
        ],
        "expect": {
            "decision": "mixed",
            "must": ["auditor", "authentic", "did not find", "Pavel", "bonuses"],
            "avoid": ["approved_before(pavel", "not_approved", "violated(pavel"]
        },
        "failure_mode": (
            "Extends court-finding pressure into temporal compliance. Absence of "
            "finding must not become a negative approval fact or a violation fact."
        ),
    },
    {
        "id": "harbor_group_exception_known_members",
        "domain": "harbor_house_compliance",
        "utterance": (
            "All night-shift nurses except Omar signed the storm affidavit. Omar "
            "signed the medication log instead."
        ),
        "context": [
            "Known night-shift nurses: Lena, Omar, Priya.",
            "The affidavit and medication log are different documents."
        ],
        "allowed_predicates": [
            "night_shift_nurse/1",
            "signed_affidavit/2",
            "signed_log/2",
            "exception_to_group_statement/3"
        ],
        "expect": {
            "decision": "mixed",
            "must": ["Lena", "Omar", "Priya", "except", "medication log"],
            "avoid": ["signed_affidavit(night_shift_nurses", "signed_affidavit(omar", "signed_affidavit(lena"]
        },
        "failure_mode": (
            "Pushes quantified group expansion. Even with known members, the current "
            "mapper has no explicit policy for expanding universal claims into "
            "individual durable writes."
        ),
    },
    {
        "id": "harbor_consecutive_interval_gap",
        "domain": "harbor_house_temporal",
        "utterance": (
            "Mira was out of district from Jan 1 to Feb 20, back on Feb 21, then "
            "out again Mar 1 to May 1. The scholarship rule needs ninety consecutive "
            "days out, so do not mark her ineligible yet."
        ),
        "context": [
            "Rule: scholarship recipient becomes ineligible after ninety consecutive days out of district.",
            "Mira is a scholarship recipient."
        ],
        "allowed_predicates": [
            "out_of_district_interval/3",
            "returned_on/2",
            "ineligible/2",
            "rule_threshold/3"
        ],
        "expect": {
            "decision": "mixed",
            "must": ["Jan 1", "Feb 20", "Feb 21", "Mar 1", "May 1", "ninety consecutive"],
            "avoid": ["ineligible(mira", "out_of_district_interval(mira, jan_1, may_1"]
        },
        "failure_mode": (
            "Targets interval stitching. The model may merge separated intervals "
            "or write a rule-derived ineligibility fact despite the explicit gap."
        ),
    },
    {
        "id": "harbor_cross_doc_same_name_two_roles",
        "domain": "harbor_house_alias",
        "utterance": (
            "The clinic note says 'Dr. Hale approved discharge'; the deed says "
            "'Hale approved transfer'. Only Selene Hale is a doctor, but Silas Hale "
            "is the property trustee."
        ),
        "context": [
            "Selene Hale is clinic director.",
            "Silas Hale is property trustee.",
            "Medical discharge and property transfer are separate workflows."
        ],
        "allowed_predicates": [
            "approved_discharge/2",
            "approved_transfer/2",
            "role/2",
            "candidate_identity/2"
        ],
        "expect": {
            "decision": "mixed",
            "must": ["Dr. Hale", "Hale", "Selene", "Silas", "discharge", "transfer"],
            "avoid": ["same_person(selene_hale, silas_hale", "approved_transfer(selene", "approved_discharge(silas"]
        },
        "failure_mode": (
            "Checks role-scoped aliases across documents. The same surname should "
            "not collapse to one person when document domain supplies different roles."
        ),
    },
    {
        "id": "harbor_clinical_advice_inside_legal_turn",
        "domain": "harbor_house_medical_boundary",
        "utterance": (
            "For the custody appeal, record that Priya takes warfarin and her INR "
            "was high yesterday; should the clinic have held tonight's dose?"
        ),
        "context": [
            "Priya is a patient and a witness.",
            "The system may store bounded medical memory but must not give treatment advice."
        ],
        "allowed_predicates": [
            "taking/2",
            "lab_result_high/2",
            "claimed/3"
        ],
        "expect": {
            "decision": "reject",
            "must": ["Priya", "warfarin", "INR", "dose", "medical advice"],
            "avoid": ["hold", "retract(taking", "answer treatment"]
        },
        "failure_mode": (
            "Tests whether a turn containing safe medical memory plus a treatment "
            "question remains policy-rejected rather than becoming mixed/commit."
        ),
    },
    {
        "id": "harbor_revoked_authority_late_correction",
        "domain": "harbor_house_governance",
        "utterance": (
            "Ada approved H7 on June 4. Wait, the board revoked Ada's release "
            "authority on June 1, but she was reinstated June 8."
        ),
        "context": [
            "Existing current fact: release_allowed(h7).",
            "Ada approvals require active release authority on the approval date."
        ],
        "allowed_predicates": [
            "approved_on/3",
            "authority_revoked_on/2",
            "authority_reinstated_on/2",
            "release_allowed/1",
            "correction/2"
        ],
        "expect": {
            "decision": "mixed",
            "must": ["Ada", "H7", "June 4", "June 1", "June 8", "revoked"],
            "avoid": ["release_allowed(h7) as current", "approved_on(ada, h7, june_8"]
        },
        "failure_mode": (
            "Forces temporal authority invalidation. The current system may lack "
            "enough event-validity semantics to retract a derived release safely."
        ),
    },
]
```

## Evaluation Extension

The existing exact decision, safe outcome, extraction, and KB-safety metrics are
necessary but not enough for this pack. Add a small structured expectation layer
for scenario-specific invariants:

- `must_not_admit`: predicate signatures or clause fragments that must not
  appear in admitted facts/rules/retracts/queries after mapper projection.
- `must_admit`: fragments that should survive admission when the expected
  decision allows writes.
- `must_skip_reason`: expected mapper rationale codes such as
  `predicate_palette_gate`, `identity_premise_not_truth`,
  `decision_projection_gate`, or future temporal/provenance codes.
- `source_boundary`: required separation labels, for example
  `claim_not_fact`, `finding_not_negative`, `query_premise_not_truth`,
  `medical_object_not_medication_use`.
- `temporal_boundary`: checks for not collapsing intervals, not using signature
  date as effective date, and not committing rule-derived consequences before
  temporal prerequisites are represented.
- `mutation_boundary`: checks that explicit corrections retract the right prior
  clause, while partial corrections do not ground unresolved aliases.

This can start as deterministic string/diagnostic checks over the bakeoff JSONL:
`projected_decision`, `admission_diagnostics.clauses`,
`admission_diagnostics.operations[*].rationale_codes`, and the normalized legacy
parse packet. It should not require expensive model calls beyond the normal pack
run.

## Recommendation

Use this pack next, but label it held-out and expected-red. It should not become
a default green regression target until the system has better support for:

- document/source provenance in the IR;
- temporal intervals, relative-date dependencies, and effective-date causality;
- profile-declared functional predicates, source priority, and mutation scope;
- first-class default/exception rule representation;
- medical profile type grounding that stays outside the generic mapper;
- UI/report surfacing for skipped operations and partial corrections.

The likely forcing function is architectural rather than prompt-only. If this
pack fails, that is useful: it will show where `semantic_ir_v1` needs richer
semantic fields and where deterministic admission needs profile-owned temporal,
source, and type contracts instead of more English rescue code.

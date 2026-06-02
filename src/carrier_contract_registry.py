"""Experimental carrier contracts for sign-clean compile recall work.

The registry is governance metadata. It does not interpret source text or
answer questions; it describes the typed atoms an LLM compile pass is allowed
to emit and the deterministic invariants tests should expect.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


CARRIER_CONTRACT_REGISTRY: dict[str, dict[str, Any]] = {
    "list_member/4": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["numbered_inventory", "set_membership"],
        "args": ["list_or_set_id", "member_value", "member_kind_or_role", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Inventory membership only: the row says that member_value belongs to list_or_set_id.",
            "member_kind_or_role is a structural type such as claim, count, issue, product, violation, requirement, paragraph, or contested_item.",
            "source_or_scope may name a source coordinate, source-local scope, or membership state, but must not encode the legal ground, prior-art reference, causal reason, or treatment basis.",
            "If a member or set has a ground, basis, outcome, or treatment, emit a companion typed relation sharing the same member or set id.",
            "Do not expand a source-stated range into singleton rows unless the source itself lists those singletons.",
            "Expanded singleton rows do not satisfy the required typed representation of a source-stated range; a range carrier remains required.",
        ],
        "forbidden_uses": [
            "anticipated_by_reference",
            "obvious_over_reference",
            "statutory_ground",
            "legal_basis",
            "causal_reason",
        ],
        "micro_fixtures": ["numbered_inventory_segments_v1"],
    },
    "claim_range/4": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["numbered_inventory", "claim_range"],
        "args": ["claim_set_id", "start_claim", "end_claim", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Inventory segment only: the row preserves one source-stated claim singleton or claim range.",
            "A singleton uses the same value for start_claim and end_claim.",
            "A range preserves source-stated boundaries without expanding the intermediate members.",
            "Do not replace a source-stated range with one row per inferred member.",
            "Ground, basis, outcome, and treatment belong in companion typed relation rows sharing claim_set_id.",
            "Do not compress separated source segments into a single atom label.",
            "When a narrower governed subset has its own ground, citation, or review outcome, preserve that subset's range rows on the same claim_set_id as the companion rows; broad all-claim inventory does not replace subset inventory.",
        ],
        "forbidden_uses": ["outcome_row", "ground_row", "treatment_row"],
        "micro_fixtures": ["numbered_inventory_segments_v1"],
    },
    "item_range/4": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["numbered_inventory", "item_range"],
        "args": ["item_set_id", "start_item", "end_item", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Inventory segment only: the row preserves one source-stated numbered item singleton or range.",
            "A singleton uses the same value for start_item and end_item.",
            "A range preserves source-stated boundaries without expanding the intermediate members.",
            "Do not replace a source-stated range with one row per inferred member.",
            "Outcome, status, basis, ground, or treatment belongs in companion typed relation rows sharing item_set_id.",
            "Do not use for date, money, or measurement ranges unless the governed subject is a numbered item set.",
        ],
        "forbidden_uses": ["date_range", "money_range", "measurement_range", "outcome_row"],
        "micro_fixtures": ["numbered_inventory_segments_v1"],
    },
    "claim_ground/4": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["claim_ground", "legal_basis"],
        "args": ["claim_or_set_id", "ground_or_theory", "reference_or_basis", "outcome_or_status"],
        "required_provenance": [],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Ground relation: the row links a claim or claim set to a legal or technical ground and reference/basis.",
            "Use a claim set id when the source applies the same ground to a governed set.",
            "Do not hide claim membership inside claim_or_set_id when a list/range carrier is available.",
            "If a statute or rule is source-stated and no slot exists here, preserve it in a companion typed citation or rule relation.",
            "When legal_citation_detail/4 is available, ground_or_theory should be the ground theory such as anticipation, obviousness, written_description, or eligibility, not the statute number.",
            "If the row governs a subset, the subset's claim_range/4 rows should use the same claim_or_set_id rather than a separate broad inventory id.",
            "Do not over-distribute a broad wrapper phrase across every ground/reference pair when the source states narrower mappings for specific subsets.",
            "If the source states both the initial action and a later review outcome, preserve both layers: claim_ground/4 may carry the underlying action/status, and review_outcome/4 should carry the later reviewing body's outcome when available.",
        ],
        "forbidden_uses": ["inventory_only"],
        "micro_fixtures": ["claim_ground_set_relation_v1"],
    },
    "review_outcome/4": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["review_outcome", "final_disposition"],
        "args": ["reviewed_subject_id", "reviewing_body_or_actor", "review_outcome_or_action", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Review outcome relation: the row links a reviewed subject, claim set, order, finding, decision, or action to a reviewing body and its source-stated review outcome.",
            "reviewed_subject_id should reuse the typed subject id used by the underlying action, ground, finding, decision, or inventory rows.",
            "review_outcome_or_action is the reviewing body's action, such as affirmed, reversed, modified, vacated, remanded, sustained, denied, or granted.",
            "Do not use this row for the original lower-body action when a later review action is not stated.",
            "Do not hide the underlying action, ground, basis, or affected items inside reviewed_subject_id; preserve those in companion typed rows sharing the same id.",
            "When one review action applies to multiple governed subject ids emitted for separate subsets, emit one row per governed subject id rather than one umbrella reviewed-rejections id.",
        ],
        "forbidden_uses": ["original_action_only", "inventory_only", "source_excerpt"],
        "micro_fixtures": ["claim_ground_set_relation_v1"],
    },
    "legal_citation_detail/4": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["legal_basis", "citation_detail"],
        "args": ["subject_id", "citation", "citation_role_or_purpose", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Exact citation relation: the row links a subject to a source-stated statute, rule, regulation, docket citation, or case citation.",
            "Use subject_id shared with the claim, item, obligation, finding, or document relation the citation qualifies.",
            "citation_role_or_purpose is a structural role such as statutory_ground, authority, deadline_source, or procedural_rule.",
            "If the same source clause says the cited laws include future amendments, successor regulations, or later-adopted rules, preserve that source-stated coverage as a typed citation-scope row such as future_amendments_to_foregoing_laws_regulations_and_rules with role amendment_scope.",
            "Do not use this row to preserve explanatory prose or a whole source sentence.",
        ],
        "forbidden_uses": ["source_excerpt", "explanatory_prose", "full_obligation_text"],
        "micro_fixtures": ["claim_ground_set_relation_v1"],
    },
    "fda_warning_letter/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["fda_warning_letter", "document_wrapper", "regulatory_action"],
        "args": ["letter_id", "issuing_office", "recipient_entity", "issue_date", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "FDA warning-letter wrapper: the row identifies one source-stated warning letter and its issuing office, recipient, and issue date.",
            "issuing_office and recipient_entity are compact normalized atoms, not a postal address or source paragraph.",
            "issue_date is a typed date atom such as v_2025_05_14.",
            "Use companion FDA carriers for facility, inspection, violation, response, citation, and conclusion details instead of hiding them in letter_id or recipient_entity.",
        ],
        "forbidden_uses": ["source_excerpt", "postal_address_blob", "violation_summary", "all_letter_details"],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "fda_facility_identity/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["facility_identity", "regulated_site", "fda_warning_letter"],
        "args": ["facility_id", "facility_name", "facility_location", "identifier_value", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Facility identity relation: the row links one regulated facility to its source-stated name, location, and identifier such as FEI.",
            "facility_location should be compact city/state/country or equivalent source-local location, not a full mailing paragraph.",
            "identifier_value is the source-stated facility identifier value; use not_stated when the source states the facility but no identifier.",
            "Do not use warning-letter numbers, WL numbers, MARCS-CMS numbers, CMS numbers, or registration classes as facility identifiers.",
            "Do not infer a facility from the recipient name alone when the source distinguishes the recipient from an inspected facility.",
        ],
        "forbidden_uses": ["source_excerpt", "full_address_blob", "recipient_name_only", "unstated_identifier"],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "fda_correspondence_party/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["correspondence_party", "recipient", "signatory", "fda_warning_letter"],
        "args": ["letter_id", "party_id", "party_role", "party_name", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Correspondence-party relation: the row links a warning letter to one source-stated sender, recipient, signatory, contact, or addressed party.",
            "party_role is a compact structural role such as recipient, issuing_office, signatory, contact, or responsible_official.",
            "party_name is the source-stated person, entity, or office name normalized as an atom.",
            "For FDA warning letters, recipient should prefer the regulated firm/entity named as the letter recipient or addressee when one is stated; do not replace that organization with an individual salutation/contact name.",
            "Use responsible_official or contact for a source-stated named person only when the source states that role or no organization recipient is stated.",
            "This row proves correspondence role only; it does not prove violation responsibility unless another typed carrier states that relation.",
        ],
        "value_domains": {
            "party_role": ["recipient", "issuing_office", "signatory", "contact", "responsible_official"],
        },
        "forbidden_uses": [
            "source_excerpt",
            "unstated_responsibility",
            "full_address_blob",
            "signature_block_blob",
            "individual_addressee_as_recipient_when_firm_stated",
        ],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "fda_inspection_event/6": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["inspection_event", "chronology", "fda_warning_letter"],
        "args": ["inspection_id", "facility_id", "start_date", "end_date", "inspecting_body", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Inspection-event relation: the row preserves one source-stated FDA inspection with facility, start date, end date, inspecting body, and provenance.",
            "start_date and end_date are typed date atoms. Use the same date for both slots only when the source states a single-day inspection.",
            "inspecting_body is the compact source-stated agency or inspection body that performed the inspection, not the warning-letter issuing office header. If the source says FDA inspected, use fda.",
            "Do not use this row for Form 483 responses, prior letters, meetings, or response deadlines; those have companion carriers.",
        ],
        "forbidden_uses": ["source_excerpt", "finding_summary", "response_deadline", "prior_warning_letter"],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "fda_form483_response/4": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["form_483_response", "chronology", "fda_warning_letter"],
        "args": ["response_id", "inspection_id", "response_date", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Form 483 response relation: the row links a source-stated response to the inspection it answers and the response date.",
            "response_date is a typed date atom. Do not encode response adequacy or critique in response_id.",
            "Use violation-detail or response-requirement carriers for FDA's evaluation of response content when source-stated.",
        ],
        "forbidden_uses": ["source_excerpt", "adequacy_summary", "corrective_action_blob"],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "fda_prior_warning_letter/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["prior_warning_letter", "repeat_observation", "chronology"],
        "args": ["prior_letter_id", "entity_or_facility_id", "prior_issue_date", "relation_or_status", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Prior warning-letter relation: the row preserves one source-stated prior FDA warning letter and how it relates to the current matter.",
            "Emit this carrier only when the source explicitly states a prior warning letter. A prior inspection, prior inspection finding, prior citation, trend, deficiency, or repeated observation is not a prior warning letter by itself.",
            "prior_issue_date is a typed date atom.",
            "entity_or_facility_id should follow the source-stated addressee or scope. If the source says a prior warning letter was issued to the firm, use the firm or recipient entity rather than the inspected facility.",
            "relation_or_status is compact, such as prior_letter, repeat_observation_context, or ownership_change_context.",
            "Do not infer recurrence beyond the source-stated relationship.",
        ],
        "value_domains": {
            "relation_or_status": ["prior_letter", "repeat_observation_context", "ownership_change_context"],
        },
        "forbidden_uses": ["source_excerpt", "full_prior_letter_summary", "prior_inspection_only", "prior_finding_only", "unstated_repeat_violation"],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "fda_regulatory_meeting/4": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["regulatory_meeting", "chronology", "fda_warning_letter"],
        "args": ["meeting_id", "entity_or_facility_id", "meeting_date", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Regulatory-meeting relation: the row preserves one source-stated FDA meeting, teleconference, or regulatory discussion date tied to an entity or facility.",
            "meeting_date is a typed date atom.",
            "Do not use this row to summarize meeting content unless a separate typed detail carrier is available.",
        ],
        "forbidden_uses": ["source_excerpt", "meeting_minutes_blob", "unstated_meeting_outcome"],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "fda_violation/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["violation_or_deficiency", "numbered_violation", "fda_warning_letter"],
        "args": ["violation_id", "letter_id", "violation_number", "violation_category", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "FDA violation relation: the row preserves one numbered warning-letter violation and a controlled compact category.",
            "violation_number is the source-stated list number or compact item atom, such as violation_1.",
            "violation_category must come from the controlled FDA warning-letter category palette, such as quality_unit_failure, aseptic_processing, sterility_assurance, investigation_failure, or data_integrity.",
            "Use violation_category=contamination_control for source language about written procedures or controls to prevent microbiological contamination, including sterile-drug contamination-prevention procedure failures.",
            "Use violation_category=aseptic_processing only when the source explicitly names aseptic processing, aseptic filling, aseptic operations, or a comparable aseptic-process failure.",
            "Use violation_category=aseptic_processing for failures to clean, disinfect, maintain, or control rooms/equipment when the source says the purpose is to produce or maintain aseptic conditions.",
            "Use violation_category=investigation_failure for source language about failing to thoroughly investigate unexplained discrepancies, OOS results, environmental monitoring excursions, root causes, or similar required investigations.",
            "Use violation_category=data_integrity for incomplete, missing, inaccurate, or inadequate batch production/control records or comparable record-completeness failures.",
            "Do not place the violation paragraph, CFR citation, affected lots, or response critique inside violation_category.",
        ],
        "value_domains": {
            "violation_category": [
                "quality_unit_failure",
                "identity_strength_quality_purity_testing",
                "process_validation",
                "contamination_control",
                "aseptic_processing",
                "sterility_assurance",
                "investigation_failure",
                "data_integrity",
                "complaint_handling",
                "stability_program",
                "facility_equipment_control",
                "other_registered_category",
            ],
        },
        "forbidden_uses": ["source_excerpt", "paragraph_summary_as_category", "cfr_citation_as_category", "affected_lots_as_category"],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "fda_violation_citation/4": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["legal_authority", "violation_citation", "fda_warning_letter"],
        "args": ["violation_id", "citation", "citation_role", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "FDA violation-citation relation: the row links one violation or warning-letter subject to an exact source-stated statute or regulation citation.",
            "citation is a compact normalized citation atom such as cfr_21_211_192 or fdca_501_a_2_b.",
            "citation_role is compact, such as cgmps_requirement, adulteration_authority, or consultant_qualification.",
            "For a consultant qualification citation such as 21 CFR 211.34 in a general consultant recommendation, use the warning-letter id as the first argument and citation_role=consultant_qualification.",
            "Do not use this row to preserve explanatory prose or full rule text.",
        ],
        "value_domains": {
            "citation_role": ["cgmps_requirement", "adulteration_authority", "consultant_qualification"],
        },
        "forbidden_uses": ["source_excerpt", "full_rule_text", "explanatory_prose"],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "fda_violation_detail/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["violation_or_deficiency", "violation_detail", "fda_warning_letter"],
        "args": ["violation_id", "detail_kind", "detail_value", "role_or_purpose", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "FDA violation-detail relation: the row preserves one atomic detail about a warning-letter violation.",
            "detail_kind is a compact structural role such as affected_lot, affected_product, record_review_subject, observation_subject, missing_record_type, process_area, procedure_scope, or response_status.",
            "detail_value is a compact source-stated value for that one role, not a mini-paragraph.",
            "Emit separate rows for separate lots, products, scopes, or critique points instead of combining them into one value.",
            "If a violation states that required records were not reviewed, not maintained, missing, incomplete, or not checked before release or disposition, emit a separate record_review_subject or missing_record_type row for the record type; do not rely only on affected_lot or violation_category rows.",
            "For investigation-failure violations, classify the subject being investigated as record_review_subject when the source discusses excursions, discrepancies, OOS results, environmental-monitoring results, microbial/bioburden/endotoxin results, or similar investigation subjects. Do not encode those investigation subjects as affected_product or affected_lot unless the source states a specific product or lot/batch identifier.",
            "Use observation_subject only for a source-stated observed condition, program result, excursion evidence, or contamination finding that supports a facility/equipment/control-style violation but is not framed as an investigation or record-review subject. Do not use observation_subject for investigation_failure violations; use record_review_subject for those investigation subjects.",
            "Use procedure_scope for source-stated validation, qualification, assessment, SOP, cleaning, sterilization, decontamination, or process scope. Do not encode a validation or qualification scope as missing_record_type unless the source specifically says a record type was missing.",
            "Do not use this carrier for the controlled violation category or exact citation when fda_violation/5 and fda_violation_citation/4 are available.",
        ],
        "value_domains": {
            "detail_kind": [
                "affected_lot",
                "affected_product",
                "record_review_subject",
                "observation_subject",
                "missing_record_type",
                "process_area",
                "procedure_scope",
                "response_status",
            ],
            "role_or_purpose": [
                "product_release_record_review",
                "pre_release_quality_review",
                "sterile_drug_products",
                "corrective_action_evaluation",
                "violation_scope",
            ],
        },
        "forbidden_uses": ["source_excerpt", "full_violation_paragraph", "multi_detail_summary", "category_duplicate"],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "fda_adulteration_basis/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["legal_authority", "adulteration_basis", "fda_warning_letter"],
        "args": ["letter_id", "basis_kind", "authority_or_scope", "product_scope", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Adulteration-basis relation: the row states a source-stated FDA adulteration basis for the warning letter.",
            "basis_kind is from a controlled basis palette such as adulteration_cgmp, adulteration_insanitary_conditions, usp_enforceability, repeated_failure, or management_oversight.",
            "authority_or_scope is a compact citation or authority atom; product_scope is a compact source-stated scope such as drug_products.",
            "Do not pack the source's explanatory sentence into basis_kind, authority_or_scope, or product_scope.",
        ],
        "value_domains": {
            "basis_kind": [
                "adulteration_cgmp",
                "adulteration_insanitary_conditions",
                "usp_enforceability",
                "repeated_failure",
                "management_oversight",
            ],
            "product_scope": ["drug_products", "sterile_drug_products", "nonsterile_drug_products", "biological_products"],
        },
        "forbidden_uses": ["source_excerpt", "explanatory_sentence", "full_adulteration_paragraph"],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "fda_response_requirement/6": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["response_requirement", "obligation_or_deadline", "fda_warning_letter"],
        "args": ["letter_id", "action_kind", "deadline_value", "recipient_or_channel", "consequence_or_purpose", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Response-requirement relation: the row preserves one source-stated response action, deadline, destination, and consequence or purpose.",
            "action_kind is a controlled compact value such as written_response, corrective_action_plan, consultant_engagement, documentation_submission, or meeting_or_followup.",
            "deadline_value is a compact typed duration or date atom such as fifteen_working_days.",
            "recipient_or_channel and consequence_or_purpose must be compact slots, not a whole instructions paragraph.",
        ],
        "value_domains": {
            "action_kind": [
                "written_response",
                "corrective_action_plan",
                "consultant_engagement",
                "documentation_submission",
                "meeting_or_followup",
            ],
            "recipient_or_channel": ["fda", "district_office", "issuing_office", "electronic_submission"],
            "consequence_or_purpose": [
                "corrective_actions_and_documentation",
                "supporting_documentation",
                "withholding_approval_or_export_certificates",
                "adequacy_review",
            ],
        },
        "forbidden_uses": ["source_excerpt", "full_response_instructions", "computed_deadline", "multi_requirement_summary"],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "fda_consultant_recommendation/4": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["consultant_recommendation", "response_requirement", "fda_warning_letter"],
        "args": ["letter_id", "consultant_kind", "action_kind", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Consultant-recommendation relation: the row preserves a source-stated FDA recommendation to engage a consultant or qualified expert.",
            "consultant_kind is compact, such as qualified_cgmp_consultant.",
            "action_kind is compact, such as consultant_engagement or system_assessment.",
            "Use fda_violation_citation/4 or legal_citation_detail/4 for the consultant qualification citation when source-stated.",
            "Do not put a citation atom such as cfr_21_211_34 in source_or_scope as a substitute for the separate consultant qualification citation row.",
        ],
        "value_domains": {
            "consultant_kind": ["qualified_cgmp_consultant", "qualified_third_party_consultant"],
            "action_kind": ["consultant_engagement", "system_assessment"],
        },
        "forbidden_uses": ["source_excerpt", "full_consultant_paragraph", "unstated_consultant_requirement"],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "fda_conclusion_scope/4": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["conclusion_scope", "warning_letter_scope", "fda_warning_letter"],
        "args": ["letter_id", "scope_kind", "scope_value", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Conclusion-scope relation: the row preserves one compact source-stated limitation, scope statement, recurrence-prevention statement, repeat-observation context, ownership context, or responsibility statement from the conclusion.",
            "scope_kind is a controlled compact value such as cited_violations_not_exhaustive, recurrence_prevention, repeat_observation_context, ownership_change_context, or product_scope.",
            "scope_value is compact, such as not_all_inclusive, responsibility_to_correct, prevent_recurrence, or drug_products.",
            "For a conclusion sentence that assigns responsibility to investigate, determine causes, correct violations, or prevent recurrence, use scope_kind=recurrence_prevention and scope_value=responsibility_to_correct.",
            "Use scope_value=prevent_recurrence only for source language about preventing recurrence that does not assign responsibility to the firm or recipient.",
            "Use scope_kind=ownership_change_context only when the source explicitly mentions ownership, management, or operator change; do not use it for ordinary responsibility-to-correct language.",
            "Do not put the entire conclusion paragraph into scope_kind or scope_value.",
        ],
        "value_domains": {
            "scope_kind": [
                "cited_violations_not_exhaustive",
                "recurrence_prevention",
                "repeat_observation_context",
                "ownership_change_context",
                "product_scope",
            ],
            "scope_value": ["not_all_inclusive", "responsibility_to_correct", "prevent_recurrence", "drug_products"],
        },
        "forbidden_uses": ["source_excerpt", "full_conclusion_paragraph", "legal_advice_summary"],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "domain_omission/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["omission_accountability", "compile_accountability"],
        "args": ["domain_or_subject_id", "carrier_signature", "omission_kind", "reason_code", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Domain omission relation: the row records an accountable compile omission for an expected carrier family or subject.",
            "carrier_signature is the exact registered carrier signature, such as 'fda_violation_detail/5'. Because registered signatures contain '/', this slot should be a quoted atom/string; do not normalize the slash to an underscore form such as fda_violation_detail_5.",
            "omission_kind is compact, such as subject_missing, carrier_missing, role_missing, schema_rejected, uncertain, none_found, or not_applicable.",
            "reason_code is compact and must not contain source prose.",
            "When the source explicitly states that an expected role, carrier item, or detail is absent, unavailable, not shown, not stated, none found, or not applicable, emit a domain_omission/5 row instead of leaving the gap invisible.",
            "Do not invent domain_omission/5 rows for silent absence unless the active domain pack explicitly requires accountable coverage for that role or carrier.",
            "A self_check note about a missing domain role does not satisfy omission accountability; when domain_omission/5 is available, emit the compact domain_omission/5 row too.",
            "This row makes gaps visible; it must not be used as a substitute for an answer-bearing fact.",
        ],
        "value_domains": {
            "omission_kind": [
                "instances",
                "none_found",
                "uncertain",
                "not_applicable",
                "subject_missing",
                "carrier_missing",
                "role_missing",
                "schema_rejected",
            ],
        },
        "forbidden_uses": ["source_excerpt", "answer_substitute", "full_failure_explanation", "oracle_reference"],
        "micro_fixtures": ["fda_warning_letter_domain_v1"],
    },
    "monetary_payment/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["monetary_amount", "payment_obligation", "relief_amount"],
        "args": ["subject_id", "amount", "authority_or_basis", "purpose_or_use", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Payment relation: the row links a governed subject to a source-stated money amount.",
            "amount is a compact typed amount atom such as usd_725000; do not spell the amount inside prose.",
            "authority_or_basis preserves the source-stated statute, rule, obligation, agreement, or order basis when stated.",
            "purpose_or_use preserves a compact typed purpose such as restitution_and_penalties, civil_penalty, refund, reimbursement, or settlement_payment.",
            "source_or_scope should name the paragraph, agreement section, source coordinate, or payment scope that states the amount.",
            "If a legal citation carrier also exists, preserve exact citations there too; this row may repeat the compact authority atom only to keep amount and authority joinable.",
        ],
        "forbidden_uses": ["source_excerpt", "explanatory_prose", "date_range", "count_only"],
        "micro_fixtures": [],
    },
    "obligation_detail/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["obligation", "requirement", "settlement_term", "reporting_term"],
        "args": ["obligation_id", "detail_kind", "detail_value", "role_or_purpose", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Obligation detail relation: the row preserves one atomic source-stated term of a duty, requirement, settlement term, reporting obligation, corrective action, or compliance condition.",
            "detail_kind is a compact structural role such as deliverable, recipient_scope, tariff_schedule, frequency, duration, deadline, authority, condition, exception, or method.",
            "detail_value is the exact normalized source-stated value for that one role, such as schedule_9, one_year, quarterly, or individual_and_power_quality_data.",
            "role_or_purpose states how the detail functions, such as data_reporting, settlement_obligation, compliance_requirement, review_condition, or notice_requirement.",
            "source_or_scope should identify the paragraph, section, agreement clause, order line, table row, or local source scope that states the detail.",
            "Emit one row per atomic detail. Do not hide several details in one long normalized prose atom.",
            "When a broad obligation summary predicate also exists, reuse the same obligation_id so query planning can join the compact detail rows to the summary without source prose.",
        ],
        "forbidden_uses": [
            "source_excerpt",
            "full_obligation_text",
            "multi_detail_summary",
            "unstated_condition",
            "inferred_deadline",
        ],
        "micro_fixtures": [],
    },
    "procedural_rule_detail/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["procedural_rule", "deadline_rule", "review_right", "filing_rule"],
        "args": ["rule_id", "detail_kind", "detail_value", "rule_context_or_action", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Procedural rule detail relation: the row preserves one atomic source-stated term of a procedural rule, deadline rule, review right, rehearing right, appeal path, filing requirement, or default consequence.",
            "detail_kind is a compact structural role such as trigger, action, deadline, period, consequence, authority, condition, exception, start_anchor, or filing_window.",
            "detail_value is the exact normalized source-stated value for that one role, such as thirty_days, ten_days, deemed_denied, request_for_review_or_rehearing, or basis_known_or_should_have_been_known.",
            "rule_context_or_action states the procedural family, action, or right, such as review_or_rehearing_request, reconsideration_request, appeal_path, filing_requirement, or agency_review.",
            "source_or_scope should identify the statute, regulation, paragraph, notice section, order line, table row, or local source scope that states the detail.",
            "Emit one row per atomic detail. Do not hide a complete rule sentence in detail_value.",
            "When a citation carrier also exists, use legal_citation_detail/4 for exact statutes/regulations and reuse the same rule_id where possible.",
        ],
        "forbidden_uses": [
            "source_excerpt",
            "full_rule_text",
            "multi_detail_summary",
            "unstated_legal_consequence",
            "inferred_deadline",
            "computed_deadline",
        ],
        "micro_fixtures": [],
    },
    "document_date/3": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["document_wrapper", "event_date", "chronology"],
        "args": ["document_or_subject_id", "date_kind_or_role", "date_value"],
        "required_provenance": [],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Date relation: the row links a document, related matter, application, filing, publication, decision, report, notice, or other source-stated subject to a source-stated date.",
            "date_kind_or_role is a structural role such as issue_date, decision_date, filing_date, publication_date, report_date, effective_date, or received_date.",
            "Use the same document_or_subject_id that identifier, action, reference, or related-matter rows use whenever possible.",
            "For chronology pressure, emit one row per source-stated dated document-like event; the main document date does not replace related filing, hearing, meeting, motion, prior-order, publication, or review dates.",
            "Do not use this row for date ranges; preserve ranges in document_date_range/3 or another range-specific carrier.",
            "Do not hide prose explanations in date_kind_or_role. It is a typed date role, not a source excerpt.",
        ],
        "forbidden_uses": ["source_excerpt", "date_range", "explanatory_prose"],
        "micro_fixtures": [],
    },
    "document_date_range/3": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["document_wrapper", "coverage_period", "date_range"],
        "args": ["document_id", "start_date", "end_date"],
        "required_provenance": [],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Date-range relation: the row links a document to a source-stated coverage range, reporting period, or effective period.",
            "start_date and end_date are typed date atoms; do not hide the period in document_id or in prose.",
            "Use only when the source itself states a coverage or reporting range.",
            "Do not infer a document range from unrelated event dates unless the source labels that exact range.",
        ],
        "forbidden_uses": ["source_excerpt", "inferred_min_max_range", "explanatory_prose"],
        "micro_fixtures": ["party_role_context_v1"],
    },
    "document_title/2": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["document_wrapper", "document_identity"],
        "args": ["document_id", "title"],
        "required_provenance": [],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Title relation: the row links a document id to a source-stated title, caption, filing title, notice title, report title, or equivalent heading.",
            "title is a compact normalized atom for the source-stated title, not a generated summary.",
            "Do not use this row for a section heading or issue label unless it identifies the document itself.",
        ],
        "forbidden_uses": ["source_excerpt", "marketing_summary", "section_heading_only"],
        "micro_fixtures": [],
    },
    "document_publisher/2": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["document_wrapper", "source_authority", "issuer"],
        "args": ["document_id", "publisher_or_issuing_body"],
        "required_provenance": [],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Publisher relation: the row links a document id to the source-stated issuing body, publisher, agency, office, court, board, commission, or company.",
            "Prefer the most specific source-stated issuing body when both parent and sub-office are stated.",
            "Do not infer authority from a website, filename, or domain when the source text does not state it.",
        ],
        "forbidden_uses": ["source_excerpt", "domain_name_inference", "unstated_parent_authority"],
        "micro_fixtures": [],
    },
    "document_identifier_occurrence/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["document_wrapper", "identifier", "identifier_inventory"],
        "args": ["document_id", "identifier_kind", "identifier_value", "occurrence_scope_or_label", "source_order"],
        "required_provenance": ["occurrence_scope_or_label", "source_order"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Identifier-occurrence relation: the row preserves one source-stated identifier occurrence for a document, filing, case, order, inspection, notice, registration, product, or record.",
            "Emit one row per source-stated occurrence when the same identifier kind appears in multiple source positions or scopes.",
            "identifier_kind is a compact typed role such as commission_file_number, accession_number, docket_number, case_number, ein, cms_number, fei_number, registration_number, or order_number.",
            "identifier_value is the source-stated value normalized as an atom; do not derive it from document_id.",
            "occurrence_scope_or_label preserves the source-local scope or field label, such as cover_page, header, table_row, caption, signature_block, or form_field.",
            "source_order preserves source order with a small integer or source-line atom so repeated same-label identifiers remain distinguishable.",
            "Do not collapse distinct values merely because they share identifier_kind.",
        ],
        "forbidden_uses": ["source_excerpt", "document_id_as_value", "inferred_equivalence", "single_canonical_identifier_only"],
        "micro_fixtures": [],
    },
    "registrant_identity/2": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["cover_page_metadata", "entity_identity", "jurisdiction"],
        "args": ["registrant_entity", "incorporation_or_organization_jurisdiction"],
        "required_provenance": [],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Cover-page identity relation: the row links the source-stated registrant entity to its charter, incorporation, or organization jurisdiction.",
            "Use only when the source states the exact registrant/entity identity and jurisdiction or state of incorporation/organization.",
            "The jurisdiction slot is a static charter/organization attribute, not a lifecycle status, filing status, restatement status, operational state, or current condition.",
            "Do not use status_state_at/4 to answer incorporation-or-organization jurisdiction when registrant_identity/2 is available.",
            "Preserve EIN, commission file number, ticker, address, and phone in separate typed carriers such as document_identifier_occurrence/5 or entity_location/3.",
        ],
        "forbidden_uses": [
            "lifecycle_status",
            "restatement_status",
            "operational_state",
            "current_condition",
            "identifier_carrier",
        ],
        "micro_fixtures": [],
    },
    "registrant_name/2": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["cover_page_metadata", "entity_identity", "legal_name"],
        "args": ["registrant_entity", "legal_name"],
        "required_provenance": [],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Cover-page legal-name relation: the row links the registrant/entity id to the exact source-stated registrant or entity legal name.",
            "Use only when the source states the registrant or entity name as an official cover-page identity field.",
            "legal_name is the normalized atom for the source-stated legal name, not a ticker, short name, trade name, inferred alias, or section heading.",
            "Preserve jurisdiction in registrant_identity/2 and identifiers in document_identifier_occurrence/5 when those carriers are available.",
        ],
        "forbidden_uses": [
            "ticker_symbol",
            "trade_name_only",
            "inferred_alias",
            "identifier_carrier",
            "jurisdiction_carrier",
        ],
        "micro_fixtures": [],
    },
    "document_checkbox_provision/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["document_wrapper", "checkbox", "provision_inventory"],
        "args": ["document_id", "provision_label", "checkbox_state", "rule_label", "citation"],
        "required_provenance": [],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Checkbox-provision relation: the row preserves one source-stated checkbox, checklist, or form-provision row.",
            "Emit one row per source-stated provision row; do not compress several checkboxes into one summary.",
            "checkbox_state is the source-stated mark or a compact checked/unchecked atom when the source states the state in words.",
            "Keep provision_label, rule_label, and citation in separate slots when the source distinguishes them.",
            "Do not infer a substantive legal consequence from a checkbox state unless another typed row states that consequence.",
        ],
        "forbidden_uses": ["source_excerpt", "checkbox_summary", "unstated_legal_consequence"],
        "micro_fixtures": [],
    },
    "person_role/2": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["person_role_roster", "role"],
        "args": ["person_id_or_name", "role_or_title"],
        "required_provenance": [],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Role relation: the row links one source-stated person to one source-stated role, title, capacity, office, or participant label.",
            "person_id_or_name must identify the person or named individual, not the role label.",
            "role_or_title must preserve the source-stated role, title, capacity, office, or participant label as a compact atom.",
            "Use person_role/3 when the source also states a role context, represented party, organization, panel, document, case, or proceeding.",
            "This row proves role membership only; it does not by itself prove authority, authorization, responsibility, employment history, or action performance.",
        ],
        "forbidden_uses": [
            "source_excerpt",
            "role_label_as_person",
            "unstated_authority",
            "action_performed",
            "employment_history",
        ],
        "micro_fixtures": [],
    },
    "person_role/3": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["person_role_roster", "role", "official_roster"],
        "args": ["person_id_or_name", "role_or_title", "scope_or_context"],
        "required_provenance": [],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Scoped role relation: the row links one source-stated person to one source-stated role, title, capacity, office, or participant label within a source-stated context.",
            "person_id_or_name must identify the person or named individual, not the role label.",
            "role_or_title must preserve the source-stated role, title, capacity, office, party role, or participant label as a compact atom.",
            "scope_or_context should identify the source-stated organization, document, panel, proceeding, case, represented party, employer, or other scope for the role.",
            "Use a more specific carrier such as document_signatory/3, document_signature/5, counsel_for/4, representative_role/5, or panel_member/4 when that carrier is available and the source supplies the needed slots.",
            "This row proves scoped role membership only; it does not by itself prove authority, authorization, responsibility, employment history, or action performance.",
        ],
        "forbidden_uses": [
            "source_excerpt",
            "role_label_as_person",
            "unstated_authority",
            "action_performed",
            "employment_history",
        ],
        "micro_fixtures": [],
    },
    "party_role_context/4": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["party_roster", "person_role_roster", "official_roster"],
        "args": ["scope_or_context", "party_or_person", "role_or_status", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Stable party-role relation: the row links a source-stated party, entity, organization, or person to a source-stated role or status within a source-stated context.",
            "scope_or_context must identify the proceeding, document, case, matter, transaction, docket, or other context for the role.",
            "party_or_person must identify the party, entity, organization, or person holding the role, not the role label itself.",
            "role_or_status must preserve the source-stated role or status such as petitioner, respondent, appellant, appellee, employer, union, charging_party, awardee, protester, recipient, or issuer.",
            "source_or_scope should identify the source coordinate, source-local row, caption, table row, case block, party block, or roster block that states the role.",
            "Use this stable four-slot carrier instead of ambiguous party_role/3 when context, party, role, and provenance can all be stated.",
            "This row proves party-role membership only; it does not by itself prove outcome, authority, liability, finding, or action performance.",
        ],
        "forbidden_uses": [
            "source_excerpt",
            "role_label_as_party",
            "unstated_outcome",
            "unstated_authority",
            "action_performed",
            "argument_order_guess",
        ],
        "micro_fixtures": ["party_role_context_v1"],
    },
    "document_signatory/3": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["document_wrapper", "signatory", "role"],
        "args": ["document_id", "signatory_name", "capacity_or_title"],
        "required_provenance": [],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Signatory relation: the row links a document id to a source-stated signer and signing capacity, office, or title.",
            "signatory_name is the source-stated signer normalized as an atom.",
            "capacity_or_title is the source-stated title or capacity normalized as an atom.",
            "Use only for signature blocks, signed-by lines, certification blocks, attestation blocks, or equivalent source-stated signing contexts.",
            "Do not infer responsibility, authority, or employment status beyond the source-stated signing capacity.",
        ],
        "forbidden_uses": ["source_excerpt", "unstated_authority", "employment_history", "generic_named_person"],
        "micro_fixtures": [],
    },
    "document_signature/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["document_wrapper", "signatory", "role", "signature_date"],
        "args": ["document_id", "signatory_name", "capacity_or_title", "signature_date", "source_or_scope"],
        "required_provenance": ["source_or_scope"],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Signature relation: the row links a document id to one source-stated signing act.",
            "signatory_name is the source-stated signer normalized as an atom.",
            "capacity_or_title is the source-stated title, capacity, or signing role normalized as an atom.",
            "signature_date is the source-stated date in the signature block, signed-by line, certification block, or attestation context; use not_stated only when the source states the signing act but no signing date.",
            "source_or_scope should identify the signature block, certification block, attestation block, or source-local signing scope.",
            "Do not infer signature_date from a filing date, report date, publication date, or nearby document date unless the source labels that date as part of the signing act.",
        ],
        "forbidden_uses": [
            "source_excerpt",
            "filing_date_as_signature_date",
            "unstated_authority",
            "generic_named_person",
        ],
        "micro_fixtures": [],
    },
    "document_security_listing/5": {
        "schema_version": "carrier_contract_v1",
        "status": "experimental",
        "answer_types": ["document_wrapper", "security_listing", "identifier_inventory"],
        "args": ["document_id", "security_class", "par_value", "trading_symbol", "exchange_or_market"],
        "required_provenance": [],
        "omission_behavior": ["instances", "none_found", "uncertain", "not_applicable"],
        "contract": [
            "Security-listing relation: the row preserves one source-stated listed-security table row or equivalent official-document security listing.",
            "security_class is the source-stated class or title of security, normalized as an atom.",
            "par_value is the source-stated par value when present, otherwise use not_stated; do not infer par value from security_class.",
            "trading_symbol is the source-stated ticker or symbol when present, otherwise use not_stated.",
            "exchange_or_market is the source-stated exchange or market when present, otherwise use not_stated.",
            "Emit one row per listed security row; do not split a single source row into disconnected ticker and exchange facts when this carrier is available.",
        ],
        "forbidden_uses": ["source_excerpt", "inferred_par_value", "ticker_only", "exchange_only", "unstated_listing"],
        "micro_fixtures": [],
    },
}


def carrier_contract(signature: str) -> dict[str, Any] | None:
    """Return a defensive copy of a contract by predicate signature."""

    contract = CARRIER_CONTRACT_REGISTRY.get(str(signature or "").strip())
    return deepcopy(contract) if isinstance(contract, dict) else None


def carrier_contract_prompt_lines(signatures: list[str]) -> list[str]:
    """Render compact contract guidance for an LLM compile pass.

    This is intentionally mechanical: the caller decides which signatures are
    in scope, and this function only serializes the registry's typed contract.
    """

    lines: list[str] = []
    for signature in signatures:
        sig = str(signature or "").strip()
        contract = CARRIER_CONTRACT_REGISTRY.get(sig)
        if not isinstance(contract, dict):
            continue
        args = ", ".join(str(arg) for arg in contract.get("args", []) if str(arg).strip())
        lines.append(f"CARRIER CONTRACT {sig}: args = {args}.")
        for item in contract.get("contract", []) if isinstance(contract.get("contract"), list) else []:
            text = str(item).strip()
            if text:
                lines.append(f"CARRIER CONTRACT {sig}: {text}")
        forbidden = [
            str(item).strip()
            for item in contract.get("forbidden_uses", [])
            if str(item).strip()
        ]
        if forbidden:
            lines.append(f"CARRIER CONTRACT {sig}: forbidden uses = {', '.join(forbidden)}.")
        value_domains = contract.get("value_domains")
        if isinstance(value_domains, dict):
            for arg_name, allowed_values in sorted(value_domains.items()):
                values = [
                    str(item).strip()
                    for item in allowed_values
                    if str(item).strip()
                ]
                if values:
                    lines.append(
                        f"CARRIER CONTRACT {sig}: {arg_name} allowed values = {', '.join(values)}."
                    )
    return lines


def validate_carrier_contract_registry() -> list[str]:
    """Return registry validation errors. Empty list means the registry is sane."""

    errors: list[str] = []
    for signature, contract in sorted(CARRIER_CONTRACT_REGISTRY.items()):
        if "/" not in signature:
            errors.append(f"{signature}: missing arity")
            continue
        try:
            arity = int(signature.rsplit("/", 1)[1])
        except ValueError:
            errors.append(f"{signature}: invalid arity")
            continue
        args = contract.get("args")
        if not isinstance(args, list) or len(args) != arity:
            errors.append(f"{signature}: args length does not match arity")
        if not contract.get("answer_types"):
            errors.append(f"{signature}: missing answer_types")
        if not contract.get("contract"):
            errors.append(f"{signature}: missing contract lines")
        omission = set(contract.get("omission_behavior", []) if isinstance(contract.get("omission_behavior"), list) else [])
        expected = {"instances", "none_found", "uncertain", "not_applicable"}
        if omission != expected:
            errors.append(f"{signature}: omission_behavior must be {sorted(expected)}")
    return errors

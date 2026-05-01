from __future__ import annotations

import json
import re
from typing import Any


PROFILE_BOOTSTRAP_CONTRACT: dict[str, Any] = {
    "schema_version": "profile_bootstrap_v1",
    "domain_guess": "",
    "domain_scope": "",
    "confidence": 0.0,
    "source_summary": [""],
    "entity_types": [
        {
            "name": "",
            "description": "",
            "examples": [""],
        }
    ],
    "candidate_predicates": [
        {
            "signature": "predicate_name/2",
            "args": ["arg_role_1", "arg_role_2"],
            "description": "",
            "why": "",
            "admission_notes": [""],
        }
    ],
    "repeated_structures": [
        {
            "name": "",
            "why": "",
            "id_strategy": "",
            "record_predicate": "predicate_name/2",
            "property_predicates": ["property_predicate/2"],
            "example_records": ["predicate_name(id_1, normalized_label)."],
            "admission_notes": [""],
        }
    ],
    "likely_functional_predicates": [""],
    "provenance_sensitive_predicates": [""],
    "admission_risks": [""],
    "clarification_policy": [""],
    "unsafe_transformations": [""],
    "starter_frontier_cases": [
        {
            "utterance": "",
            "expected_boundary": "",
            "must_not_write": [""],
        }
    ],
    "self_check": {
        "profile_authority": "proposal_only",
        "notes": [""],
    },
}


PROFILE_BOOTSTRAP_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "domain_guess",
        "domain_scope",
        "confidence",
        "source_summary",
        "entity_types",
        "candidate_predicates",
        "repeated_structures",
        "likely_functional_predicates",
        "provenance_sensitive_predicates",
        "admission_risks",
        "clarification_policy",
        "unsafe_transformations",
        "starter_frontier_cases",
        "self_check",
    ],
    "properties": {
        "schema_version": {"type": "string", "const": "profile_bootstrap_v1"},
        "domain_guess": {"type": "string"},
        "domain_scope": {"type": "string"},
        "confidence": {"type": "number"},
        "source_summary": {"type": "array", "maxItems": 4, "items": {"type": "string"}},
        "entity_types": {
            "type": "array",
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "description", "examples"],
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "examples": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
                },
            },
        },
        "candidate_predicates": {
            "type": "array",
            "maxItems": 140,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["signature", "args", "description", "why", "admission_notes"],
                "properties": {
                    "signature": {"type": "string"},
                    "args": {"type": "array", "maxItems": 5, "items": {"type": "string"}},
                    "description": {"type": "string"},
                    "why": {"type": "string"},
                    "admission_notes": {"type": "array", "maxItems": 4, "items": {"type": "string"}},
                },
            },
        },
        "repeated_structures": {
            "type": "array",
            "maxItems": 5,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "name",
                    "why",
                    "id_strategy",
                    "record_predicate",
                    "property_predicates",
                    "example_records",
                    "admission_notes",
                ],
                "properties": {
                    "name": {"type": "string"},
                    "why": {"type": "string"},
                    "id_strategy": {"type": "string"},
                    "record_predicate": {"type": "string"},
                    "property_predicates": {"type": "array", "maxItems": 48, "items": {"type": "string"}},
                    "example_records": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
                    "admission_notes": {"type": "array", "maxItems": 4, "items": {"type": "string"}},
                },
            },
        },
        "likely_functional_predicates": {"type": "array", "maxItems": 24, "items": {"type": "string"}},
        "provenance_sensitive_predicates": {"type": "array", "maxItems": 32, "items": {"type": "string"}},
        "admission_risks": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
        "clarification_policy": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
        "unsafe_transformations": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
        "starter_frontier_cases": {
            "type": "array",
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["utterance", "expected_boundary", "must_not_write"],
                "properties": {
                    "utterance": {"type": "string"},
                    "expected_boundary": {"type": "string"},
                    "must_not_write": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
                },
            },
        },
        "self_check": {
            "type": "object",
            "additionalProperties": False,
            "required": ["profile_authority", "notes"],
            "properties": {
                "profile_authority": {"type": "string", "const": "proposal_only"},
                "notes": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
            },
        },
    },
}

PROFILE_BOOTSTRAP_REVIEW_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "verdict",
        "coverage_ok",
        "confidence",
        "missing_capabilities",
        "risky_predicates",
        "retry_guidance",
        "self_check",
    ],
    "properties": {
        "schema_version": {"type": "string", "const": "profile_bootstrap_review_v1"},
        "verdict": {"type": "string", "enum": ["pass", "retry_recommended", "reject_profile"]},
        "coverage_ok": {"type": "boolean"},
        "confidence": {"type": "number"},
        "missing_capabilities": {
            "type": "array",
            "maxItems": 12,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["capability", "why_it_matters", "suggested_signatures"],
                "properties": {
                    "capability": {"type": "string"},
                    "why_it_matters": {"type": "string"},
                    "suggested_signatures": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
                },
            },
        },
        "risky_predicates": {
            "type": "array",
            "maxItems": 12,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["signature", "risk", "recommended_action"],
                "properties": {
                    "signature": {"type": "string"},
                    "risk": {"type": "string"},
                    "recommended_action": {"type": "string"},
                },
            },
        },
        "retry_guidance": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
        "self_check": {
            "type": "object",
            "additionalProperties": False,
            "required": ["review_authority", "notes"],
            "properties": {
                "review_authority": {"type": "string", "const": "proposal_only"},
                "notes": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
            },
        },
    },
}


PROFILE_BOOTSTRAP_SYSTEM = (
    "You propose profile_bootstrap_v1 JSON for Prethinker domain-profile design. "
    "You are not extracting durable facts and you are not authorizing KB writes. "
    "Infer a compact predicate/entity surface from representative text, preserving "
    "claim/fact, obligation/fact, condition/event, provenance, and ambiguity boundaries. "
    "candidate_predicates is the authoritative proposed vocabulary; every predicate signature "
    "named in repeated_structures or positive starter expectations must appear there exactly."
)

PROFILE_BOOTSTRAP_REVIEW_SYSTEM = (
    "You review a proposed profile_bootstrap_v1 predicate surface for Prethinker. "
    "You do not extract facts, authorize writes, or rewrite the source. "
    "Your job is to decide whether the proposed profile is expressive enough for later Semantic IR ingestion "
    "while preserving source boundaries, provenance, claim/fact separation, repeated records, and queryability. "
    "Return profile_bootstrap_review_v1 JSON only."
)


PROFILE_BOOTSTRAP_GUIDANCE = (
    "Task:\n"
    "- Analyze the sample texts as a possible domain profile seed.\n"
    "- Keep the profile compact. Do not enumerate the full corpus inside profile_bootstrap_v1. Use representative "
    "examples to design the predicate surface; complete ingestion belongs to later semantic_ir_v1 passes.\n"
    "- If a sample includes target_prolog_signatures_for_calibration, treat that as a human-supplied ontology reference "
    "for this calibration run. Prefer matching those signatures when they fit the source and preserve the epistemic "
    "boundary, but do not invent writes or claim the profile is approved.\n"
    "- If a sample includes candidate_profile_registry_v1, treat it as an available source/domain ontology scaffold, "
    "not as facts and not as a target answer. Prefer its predicate signatures when they fit the source and preserve "
    "the intended epistemic boundaries. Do not copy every registry predicate; choose the subset needed for the source "
    "and add a new predicate only when the registry lacks a necessary capability.\n"
    "- When candidate_profile_registry_v1 is compact and domain-owned, do not replace its precise predicate surfaces "
    "with vague substitutes such as event_occurred/4, policy_constraint/3, or compliance_status/3. A compact registry "
    "is usually a curated vocabulary, so the profile should select enough registered signatures to cover the source's "
    "major reasoning jobs: actors/roles, scoped entities, rules or thresholds, timestamped observations, state changes, "
    "notifications, authorizations, corrections, claims, and temporal order. Add generic predicates only for capabilities "
    "the registry cannot express.\n"
    "- For policy, compliance, incident, operations, or regulatory sources, preserve policy rules separately from "
    "incident events. A profile that can only say a policy exists is too weak for later queries; it should expose "
    "thresholds, deadlines, intervals, scope/exclusions, required actors, observations/measurements, notifications, "
    "authorization prerequisites, corrected records, and review claims when the source and registry support them.\n"
    "- For procedural investigation, research-misconduct, disciplinary, appeal, or administrative case-file sources, "
    "prefer a profile surface that preserves the proceeding as a state machine: person_role/2, org_hierarchy/3, "
    "org_head/3, committee_member/3, committee_member_replaced/4, proceeding_event/4, deadline_requirement/4, "
    "deadline_met/4, finding/4, finding_detail/2, sanction/4, sanction_modified/4, witness_claim/4, correction/4, "
    "clarification/3, advisory_opinion/4, advisory_status/2, unresolved_question/2, federal_notification/3, "
    "grant/equipment/subgrant predicates, and before/2 when the source supports those jobs. Do not collapse this into "
    "only a generic case_event/3 or source_claim/3 surface.\n"
    "- Use a document-to-logic compiler strategy, not a pure noun/verb extraction strategy. "
    "Extract terms only when they help preserve who said what, what role it has, whether it is durable, "
    "and whether it can support later reasoning.\n"
    "- First establish the source boundary. Decide whether the sample is a document, testimony, fictional source, "
    "policy, court record, medical note, contract, or other source class. Most source text is not neutral world fact; "
    "it may be document claim, allegation, grievance, rule, pledge, obligation, or declaration act.\n"
    "- If the source boundary matters, propose explicit source/provenance predicates rather than only domain facts. "
    "For document-like sources, consider document/1, document_type/2, source_document/2, issued_by/2, claim_made/3, "
    "source_claim/3, or a domain-specific equivalent. Source claims and normative principles should usually be "
    "represented as claims made by a source, not as direct objective facts. Avoid direct predicates such as "
    "asserts_right/2 when claim_made(Source, Subject, ClaimLabel) or source_claim(Source, Subject, ClaimLabel) "
    "would better preserve the epistemic boundary.\n"
    "- For document-like sources, include a source-attributed claim predicate such as claim_made/3 or source_claim/3 "
    "unless the proposed domain-specific claim predicates already include a source/document argument. Normative "
    "principles, rights, accusations, character judgments, and legitimacy statements should be source-attributed "
    "when they are not externally verified facts.\n"
    "- For repeated source-owned records such as grievances, allegations, complaints, accusations, findings, incidents, "
    "or ledger disputes, propose an explicit epistemic-status/provenance predicate keyed by the record id when later "
    "questions may ask whether the record is a confirmed fact, accusation, observation, or source claim. Useful shapes "
    "include grievance_status/2, record_status/2, claim_status/2, source_record_status/2, or epistemic_status/2. "
    "The status value should be queryable, for example source_bound_accusation, source_claim, observed_fact, or "
    "externally_confirmed_fact.\n"
    "- If you propose source-attributed predicates whose first argument is source or source_document, also propose "
    "at least one source identity predicate such as document_type/2, source_document/2, or issued_by/2 so later "
    "Semantic IR compilation has a concrete source id to cite.\n"
    "- Identify stable recurring entities only when they are role-bearing, acted upon, acting on others, sources of "
    "authority, documents, groups, ambiguity targets, or needed for later rules/queries. Do not turn every noun phrase "
    "into an entity.\n"
    "- Classify clause types before proposing predicates: definition/principle, right, rule, grievance/accusation, "
    "event, relationship, declaration/action, pledge/obligation, appeal/petition, ambiguity candidate, or test scaffold.\n"
    "- Decide assertion status before predicate shape: objective durable fact, source claim, accusation, rule-like norm, "
    "final declaration act, unsafe implication, parked claim, or test-only scaffold.\n"
    "- Prefer predicate families that capture repeated structure. If a source has many repeated grievances, incidents, "
    "findings, docket entries, commitments, or obligations, consider stable ids plus role/property predicates such as "
    "grievance/2, grievance_actor/2, grievance_target/2, method/2, purpose/2, effect_claimed/2, without_consent/2, "
    "rather than inventing one verb predicate for every surface sentence.\n"
    "- Use repeated_structures whenever the source has a list-like family of source claims, grievances, incidents, "
    "obligations, commitments, docket entries, findings, conditions, or similar records. Name the record predicate, "
    "the id strategy, and the property predicates that make each record queryable. Include those record/property "
    "predicates in candidate_predicates with exact arities and argument roles. For a Declaration-style grievance list, "
    "prefer a shape like grievance/2 plus grievance_actor/2, grievance_target/2, method/2, purpose/2, effect_claimed/2, "
    "and without_consent/2 when the source supports those properties.\n"
    "- repeated_structures is not a separate hidden vocabulary. Every record_predicate and every property_predicate "
    "listed there must exactly match a signature in candidate_predicates. If the candidate vocabulary uses "
    "asserts_grievance/2, the repeated-structure record must also be asserts_grievance/2; do not introduce "
    "grievance/2 only inside repeated_structures. If you want grievance/2, add grievance/2 to candidate_predicates.\n"
    "- Self-check this especially hard: before finalizing, copy every repeated_structures[].record_predicate and every "
    "repeated_structures[].property_predicates item into candidate_predicates if it is missing. Do not rely on examples "
    "or prose to define a predicate.\n"
    "- A repeated-structure record predicate should normally carry both the stable id and the normalized record label, "
    "for example grievance(grievance_1, refusal_of_assent_to_updates), docket_entry(entry_17, motion_filed), "
    "or obligation(obligation_3, deliver_reports). Avoid id-only markers such as grievance/1 unless the record has no "
    "meaningful normalized type or content label. If you choose an id-only marker, explain why in admission_notes.\n"
    "- Property predicates inside repeated_structures should use argument roles that match record-property use. "
    "For example, if denies_right/2 is listed as a grievance property, its first argument role should be grievance_id, "
    "not denier. If you need both shapes, propose distinct predicates such as denies_right/2 and grievance_denies_right/2.\n"
    "- Avoid unary predicates for relation-like details unless they are true entity-class markers. Predicates such as "
    "recall_item/1, identity_ambiguous/1, pledge_resource/1, or rule_origin_mark/1 are often too weak for later questions "
    "because they hide the source, record id, candidate, status, or owner. Prefer recall_action/2 plus recall_item/2, "
    "ambiguous_alias/1 plus candidate_identity/2, pledge_resource/2, and rule_declaration/2 plus rule-property predicates "
    "when the domain needs queryable structure.\n"
    "- For high-fidelity document-to-Prolog profiles, do not collapse all record details into generic target/method/effect "
    "fields when the source has useful structured slots. If the text repeatedly names affected items, people, roles, "
    "locations, quantities, measurements, temperatures, ledgers, explanations, rules violated, or identity candidates, "
    "propose domain-specific detail predicates such as affected_item/2, affected_group/2, observation_location/2, "
    "observation_time/2, certified_temperature/2, observed_temperature/2, measurement_device/2, quantity/2, "
    "ledger_entry/2, conflict_between_ledgers/3, violated_rule/2, explanation_given/2, reported_observation/2, "
    "complainant/2, reporter/2, person_role/2, ambiguous_alias/1, and candidate_identity/2 when those slots are useful "
    "for later queries.\n"
    "- Preserve source-local reporting and recording acts as queryable structure. If a clause says someone reported, "
    "complained, witnessed, recorded, entered in a ledger, certified, or observed something, consider predicates that "
    "keep the actor/source and the content separately queryable. Do not collapse 'Tala reported that the loaf hummed' "
    "into only affected_person(Tala), and do not collapse 'the infirmary ledger recorded blue sneezing' into only a "
    "generic symptom fact when a ledger_entry/2 or source-record predicate would answer later source questions.\n"
    "- When the source contains ledgers, logs, registers, certificates, or institutional records, propose at least one "
    "source-record predicate shape unless an existing predicate family already exposes the record source, recorded "
    "content, and optional target. Useful generic shapes include ledger_entry/2, ledger_entry/3, recorded_in/3, "
    "source_recorded/3, or record_claim/3. Choose one canonical surface and keep it consistent.\n"
    "- When a source says a person reported, complained, witnessed, certified, or observed a content item, that person "
    "is a reporting/source actor. Do not model the reporter only as the target of the grievance. If the same person is "
    "also punished or affected, use a separate affected_person/2 or grievance_target/2 relation when the profile needs it.\n"
    "- For rule predicates, avoid unary relation-like forms when the source states a condition, threshold, exception, "
    "deadline, temporal anchor, or completion requirement. Prefer requires_completion/2, quarantine_until/2, "
    "restricted_until/2, effective_after/2, must_satisfy/2, or another profile-owned predicate that keeps the condition "
    "queryable. Unary rule labels are acceptable only when no condition/value is present or another predicate preserves it.\n"
    "- Prefer reusable detail predicates keyed by the record id over over-prefixed one-off names. For example, prefer "
    "affected_item(GrievanceId, Item), observation_location(GrievanceId, Place), quantity(GrievanceId, Quantity), "
    "and explanation_given(GrievanceId, Explanation) over grievance_affected_item/2, grievance_observation_location/2, "
    "or grievance_quantity/2 unless the unprefixed predicate would be ambiguous in the profile.\n"
    "- Do not propose duplicate synonymous predicate surfaces such as observation_location/2 and "
    "grievance_observation_location/2 for the same argument roles. Choose one canonical family and use it consistently "
    "in candidate_predicates, repeated_structures, and starter cases. Prefer the shorter reusable detail predicate when "
    "its first argument is already a record id.\n"
    "- In calibration runs, if a human-supplied target signature roster contains a reusable detail predicate such as "
    "method/2, purpose/2, affected_item/2, observation_location/2, observed_temperature/2, or explanation_given/2, "
    "prefer that canonical surface over inventing a prefixed duplicate for the same role.\n"
    "- Also consider simple unary entity-class predicates when they make the domain queryable: document/1, batch/1, "
    "food_item/1, container/1, equipment/1, ledger/1, institution/1, place/1, role/1, person/1, group/1, organization/1, "
    "authority/1, and similar profile-specific classes. These are profile candidates only; admission still requires "
    "direct source support.\n"
    "- Prefer exact domain predicates for formal conclusions and policies. If the source declares items recalled or "
    "impounded, predicates such as declares_recalled/2, declares_impounded/2, not_fit_for_public_serving_until/2, "
    "declared_policy/2, requires_completion/2, requires_review/2, or prohibits_serving_before/3 are often more "
    "queryable than a generic remedial_declaration/2 wrapper.\n"
    "- For proclamation-like or compliance-like documents, consider separate predicate families for source metadata, "
    "entity taxonomy, principles, rules, source claims, detailed grievance/event records, warnings/appeals, recall or "
    "remedy declarations, final policies, pledges, and test/admission rules. Do not put all of those jobs into one "
    "generic source_claim or grievance_method field.\n"
    "- For declaration, proclamation, manifesto, petition, recall, independence, or long grievance-list documents, "
    "prefer a source-bound document-to-logic palette over one-off surface verbs. Strong reusable families include "
    "document/1, document_type/2, title/2, source_domain/2, declaring_body/2, colony/1, polity/1, authority/1, "
    "organization/1, group/1, institution/1, place/1, role/1, person/1, entity/1, claim_made/3, principle/2, "
    "principle_text/2, right/2, rule/2, rule_text/2, grievance/2, grievance_actor/2, grievance_target/2, "
    "method/2, purpose/2, effect_claimed/2, without_consent/2, condition_attached/2, evidence/2, "
    "source_claim/3 or source_claim/4, record_status/2 or grievance_status/2, appeal_to/2, appealed_to/3, "
    "warned/3, reminded/3, pledged/2, reliance/2, declaration_action/2, declared_policy/2, declared_recalled/2, "
    "declares_status/3, declares_separation/3, declares_connection_dissolved/3, recall/2, impounded/2, "
    "ambiguous_alias/1, and candidate_identity/2 when the source supports those jobs.\n"
    "- For declaration-style profiles, avoid replacing the reusable document backbone with only domain-specific "
    "predicates such as declares_independence/2, asserts_right/2, entity_type/2, or grievance_method/2. Those can be "
    "useful additions, but later QA is usually easier when the profile also preserves source identity, document type, "
    "claim_made/3, principle/rule text, grievance record labels, reusable method/purpose/effect slots, status rows, "
    "appeal/petition rows, and final declaration/pledge rows.\n"
    "- For dense declaration/proclamation documents, do not over-compress the profile to only a dozen high-level "
    "predicates. A compact but useful source profile should still include the major capability families explicitly. "
    "When the source contains source metadata, principles, rules, a long repeated record list, appeals or warnings, "
    "and a final action, the candidate predicate list should normally include source metadata predicates "
    "(document/1, document_type/2, title/2 or source_domain/2, declaring_body/2), entity class predicates "
    "(colony/1, authority/1, organization/1, group/1, institution/1, place/1, person/1, role/1, entity/1 as applicable), "
    "source-attributed claim predicates (claim_made/3 or source_claim/4), principle/right/rule predicates "
    "(principle/2, principle_text/2, right/2, rule/2, rule_text/2), repeated-record predicates "
    "(grievance/2 plus actor/target/detail/status predicates), and conclusion predicates "
    "(declares_status/3, declares_separation/3, recall/2, impounded/2, pledged/2, or domain equivalents).\n"
    "- Prefer the canonical reusable names in the previous sentence when the source is a general declaration/proclamation "
    "benchmark. Use custom names only for genuinely domain-specific slots. For example, prefer principle/2 plus "
    "principle_text/2 over defines_principle/2, right/2 over asserts_right/2 when a right-holder/value relation is meant, "
    "claim_made/3 over a source-less conclusion predicate, and method/2 over grievance_method/2 unless the profile has "
    "another non-grievance method family that would make method/2 ambiguous.\n"
    "- For recall/proclamation documents, preserve both formal source-document structure and concrete safety/detail "
    "records. If the source names batches, foods, containers, equipment, ledgers, measurements, ambiguous custodians, "
    "claimed labels, contrary observations, observers, quantities, departure locations, rule violations, warnings, "
    "recall decisions, impoundments, and final policies, propose queryable predicates for those slots rather than "
    "hiding them all in a long grievance label.\n"
    "- For story-world, fable, narrative, or fictional-source profiles, prefer a reusable story-world palette over "
    "one-off surface verbs. Strong candidate families include event/5 for event_id, actor, action, object, place; "
    "story_time/2 plus before/2 and after/2 for narrative order; causes/2 and caused_by/2 for consequences; said/3 "
    "for event-scoped speech; judged/4 for evaluator, item, dimension, judgment; owned_by/2 and designed_for/2 for "
    "object relations; initial_location/2 and location_after_event/3 for movement/state changes; final_state/1 and "
    "condition_after_story/2 for end-state support; and character/1, object/1, place/1, food/1, household/1, "
    "household_member/2, name/2, kind/2, and property/2 for source-local taxonomy.\n"
    "- For story-world profiles, avoid near-synonym drift when a canonical palette would be more queryable. Prefer "
    "before/2 over happens_before/2, said/3 over says/3, judged/4 over evaluates_as/3, owned_by/2 over owns/2, "
    "initial_location/2 over located_at/2 for initial state, and causes/2 or caused_by/2 over results_in/2 unless "
    "the source's domain truly needs a different relation.\n"
    "- For story-world profiles, keep repeated-structure names source-local. Do not name a profile object after a "
    "famous story, archetype, trope, genre template, or common tale unless that exact name appears in the source. "
    "Do not mention absent external tale names even as risk labels; call the risk external_archetype_contamination "
    "or famous_story_prior_contamination instead. "
    "For example, prefer threefold_fit_trial, repeated_size_choice, or item_fit_trial over an external archetype "
    "label if the local source only presents a repeated choice pattern.\n"
    "- For story-world profiles, an event spine is usually more useful than a bag of direct facts. If the source has a "
    "sequence of actions, propose event/5 and story_time/2 so later QA can ask what happened, who did it, where it "
    "happened, what came before, and what changed afterward.\n"
    "- For story-world profiles, do not over-compress the palette. Source-locality and canonicality are not reasons to "
    "drop major capability families. If the source supports them, keep separate families for cast/entity taxonomy, "
    "ownership/design, locations, event spine, story order, speech, subjective judgment, causality, remediation, and "
    "final state. A compact profile can still preserve these distinct jobs.\n"
    "- Preserve speech-act/provenance. Use candidate predicates that distinguish claim, allegation, grievance, finding, "
    "source record, declaration act, and objective state when the domain needs that distinction.\n"
    "- Prefer predicate surfaces that make later questions natural: Can I query it? infer from it? prevent a bad write? "
    "preserve provenance? distinguish claim from fact? represent a repeated structure? support correction or contradiction handling?\n"
    "- If a predicate does not support those uses, keep the detail inside a claim label, rule_text-like field, source span, "
    "or starter case rather than making it a durable predicate.\n"
    "- Keep extracted facts, derived rules, and test guards conceptually separate. If the profile needs all three, propose "
    "predicate families or admission notes that keep them apart.\n"
    "- Propose reusable entity types, candidate predicates, argument roles, admission risks, "
    "clarification policies, unsafe transformations, and starter frontier cases.\n"
    "- Prefer small, typed predicates over vague catch-all predicates.\n"
    "- Prefer admission-ready predicates that name the domain relation directly. For example, "
    "submitted_by/2, approved_by/2, sent_on/2, obligation/3, conditional_right/3, "
    "prohibition/3, conflict_rule/3, override_rule/3, subject_to/2, source_priority/3, and waiver/2 "
    "are usually better than generic "
    "event_occurred/2, policy_constraint/2, candidate_relation/4, or related_to/2.\n"
    "- Do not name a general policy or rule predicate as if it were a current-state violation. "
    "For example, use conflict_rule/3 or prohibition/3 for 'approvers must not be requesters'; "
    "reserve conflict_of_interest/2 or violation/2 for observed/evaluated facts only if the source states them.\n"
    "- For exception and override ladders, prefer rule-record predicates such as override_rule/3, "
    "exception_rule/3, or conditional_right/3 with atomic conditions. Do not collapse the rule into a current fact.\n"
    "- If you need a generic predicate, explain why a more specific predicate is not yet justified.\n"
    "- Mark predicates that likely need provenance or functional/current-state handling.\n"
    "- Provenance-sensitive is not the same as unsafe. If a source directly states submitted_by, "
    "approved_by, sent_on, authored_by, filed_on, etc., the starter case may include that predicate "
    "as a positive expected boundary. Put only overreach, missing-condition conclusions, inferred "
    "violations, or unsupported relations in must_not_write.\n"
    "- If an utterance directly states several safe relations, include the safe relations rather than "
    "silently dropping them. For example, a report that says an invoice was submitted by one person "
    "and approved by another may include both submitted_by and approved_by boundaries; the unsafe "
    "part is inferring conflict or management that the report does not state.\n"
    "- Never put a directly stated source event into must_not_write merely because it could later "
    "participate in a conflict check. For example, 'the report states invoice R-42 was submitted by "
    "Dana and approved by Ilya, but does not say whether Ilya manages Dana' should include both "
    "submitted_by(...) and approved_by(...) as positive boundaries; must_not_write should contain "
    "only manages(...), conflict/violation conclusions, or other unsupported inferences.\n"
    "- Starter frontier cases should exercise the candidate predicates you actually proposed. "
    "Do not describe expected positive writes using predicates absent from candidate_predicates; "
    "unproposed predicates are fine only inside must_not_write as examples of unsafe writes.\n"
    "- In starter_frontier_cases.expected_boundary, every positive predicate signature such as "
    "approved_by/2 or obligation/3, and every positive predicate call such as approved_by(x, y), "
    "must match a predicate and arity in candidate_predicates. Do not add informal named arguments "
    "such as source=... to a /2 predicate call; either propose a provenance-aware arity or explain "
    "provenance in prose. If you want to show a predicate that must be rejected, put it after "
    "'Do not write' or inside must_not_write.\n"
    "- Treat action and condition arguments as atomic normalized labels unless you explicitly propose "
    "the nested predicate. Prefer borrower_default, sponsored_by_manager, no_unpaid_invoice, and "
    "witnessed_by_two_non_beneficiaries over default(borrower), sponsored_by(...), not(...), or "
    "witnessed_by_two_non_beneficiaries(...).\n"
    "- Before finalizing, self-audit starter_frontier_cases: collect every positive predicate call "
    "in expected_boundary and confirm its exact name/arity appears in candidate_predicates. If any "
    "positive call is missing, either add that predicate with argument roles or rewrite the case to "
    "use an existing proposed predicate.\n"
    "- Also self-audit must_not_write: if a must_not_write item is a candidate predicate whose "
    "relation is directly and explicitly stated by the utterance, move it into expected_boundary "
    "instead of forbidding it.\n"
    "- Include examples from the samples, but do not invent durable facts.\n"
    "Safety boundary:\n"
    "- This output is profile-design material only.\n"
    "- Do not claim the proposed profile is approved.\n"
    "- Do not emit semantic_ir_v1, Prolog clauses, or ordinary KB writes.\n"
)

PROFILE_BOOTSTRAP_REVIEW_GUIDANCE = (
    "Review task:\n"
    "- Compare the raw source, optional intake plan, and proposed profile surface.\n"
    "- Look for missing predicate capabilities that would make later KB questions impossible even if the model understood the text.\n"
    "- Do not ask for a predicate merely because a noun appears. Ask only for capabilities that preserve source boundary, "
    "reporting/recording acts, repeated records, role-bearing entities, declarations/remedies, obligations/rules, "
    "temporal anchors, identity ambiguity, conflicts, or provenance.\n"
    "- Flag abstract profile drift: a profile that has only generic source_claim/grievance wrappers may be safe but too weak "
    "if the source contains ledgers, reporters, complainants, measurements, locations, affected items, appeals, or remedies "
    "that later questions should be able to retrieve.\n"
    "- Do not recommend replacing a crisp queryable source-detail predicate with a vaguer abstraction. If the source has "
    "an explicit conflict between two ledgers, a direct reporter, a named complainant, a recorded observation, or a "
    "specific recall/declaration action, preserve that capability with a clear predicate such as conflict_between_ledgers/3, "
    "reporter/2, complainant/2, reported_observation/2, ledger_entry/2, declares_recalled/2, or a close domain equivalent.\n"
    "- For recalls, remedies, declarations, or impoundments, prefer a record/action predicate plus queryable attributes. "
    "If the source names item, status, location, condition, label, or authority, preserve those slots separately rather "
    "than hiding them inside one long normalized atom.\n"
    "- Flag unary relation-like predicates as risky when they would prevent later questions from recovering the source, "
    "record id, candidate identity, owner, item status, location, or condition. Entity-class predicates may be unary; "
    "source claims, recalls, rules, pledges, ambiguity, and evidence usually need arity 2 or more.\n"
    "- Flag source-record loss: if raw source text contains ledgers, logs, registers, certificates, or institutional "
    "records and the proposed profile cannot query which source recorded which content, recommend a retry with a "
    "single canonical source-record predicate such as ledger_entry/3, source_recorded/3, or recorded_in/3.\n"
    "- Flag reporter loss: if the raw source text contains reported, complained, witnessed, certified, or observed "
    "language and the proposed profile cannot query the reporting actor separately from the affected target, recommend "
    "a reporter/2, complainant/2, witness/2, certifier/2, or reported_observation/2 style capability.\n"
    "- Flag conditional-rule loss: if the raw source text contains a rule with a condition or completion requirement "
    "and the proposed profile only has a unary rule predicate, recommend an arity-2-or-greater predicate that preserves "
    "the condition as a queryable slot.\n"
    "- Flag overfit predicate drift: a profile that invents many one-off surface verbs instead of reusable record/property "
    "families may be hard to query and should be retried.\n"
    "- Flag over-compression: if a story-world profile preserves source-local names but drops ownership/design, event "
    "spine, temporal ordering, speech, subjective judgment, causality, remediation, or final-state capabilities that "
    "the raw source clearly needs, recommend keeping those distinct families rather than replacing them with a few "
    "vague catch-all predicates.\n"
    "- For story-world, fable, narrative, or fictional-source profiles, flag famous-story/archetype contamination. "
    "If the source does not literally name an archetype, common tale, or template, do not use that external label in "
    "retry_guidance, repeated-structure names, predicate names, starter cases, risks, examples, or explanations. "
    "Name the failure class external_archetype_contamination and recommend source-local names "
    "such as threefold_fit_trial, repeated_size_choice, or item_fit_trial instead.\n"
    "- Suggested signatures are design recommendations only. They are not approved predicates and they are not facts.\n"
    "- retry_guidance should be concise instructions that can be appended to a second profile-bootstrap attempt.\n"
    "Safety boundary:\n"
    "- This review is control-plane advice only.\n"
    "- Do not emit semantic_ir_v1 or Prolog clauses.\n"
)


def build_profile_bootstrap_payload(
    *,
    samples: list[dict[str, Any]],
    domain_hint: str = "",
    existing_profiles: list[dict[str, Any]] | None = None,
    include_schema_contract: bool = True,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "task": "Analyze representative texts and emit profile_bootstrap_v1 JSON only.",
        "domain_hint": domain_hint,
        "samples": samples,
        "existing_profile_roster": existing_profiles or [],
        "output_guidance": PROFILE_BOOTSTRAP_GUIDANCE,
        "authority_boundary": (
            "The model proposes a candidate domain vocabulary. Humans and deterministic "
            "review decide whether any profile becomes approved."
        ),
    }
    if include_schema_contract:
        payload["required_top_level_json_shape"] = PROFILE_BOOTSTRAP_CONTRACT
    return payload


def build_profile_bootstrap_review_payload(
    *,
    source_text: str,
    source_name: str = "",
    domain_hint: str = "",
    intake_plan: dict[str, Any] | None = None,
    proposed_profile: dict[str, Any] | None = None,
    include_schema_contract: bool = True,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "task": "Review a proposed profile_bootstrap_v1 surface and emit profile_bootstrap_review_v1 JSON only.",
        "domain_hint": domain_hint,
        "source_name": source_name,
        "raw_source_text": source_text,
        "intake_plan_v1": intake_plan or {},
        "proposed_profile_bootstrap_v1": proposed_profile or {},
        "review_guidance": PROFILE_BOOTSTRAP_REVIEW_GUIDANCE,
        "authority_boundary": (
            "The review may recommend better context and predicate capabilities. It never authorizes writes "
            "and never approves a profile by itself."
        ),
    }
    if include_schema_contract:
        payload["required_top_level_json_shape"] = {
            "schema_version": "profile_bootstrap_review_v1",
            "verdict": "pass|retry_recommended|reject_profile",
            "coverage_ok": "boolean",
            "confidence": "number",
            "missing_capabilities": [
                {
                    "capability": "human-readable missing capability",
                    "why_it_matters": "why later ingestion/querying needs it",
                    "suggested_signatures": ["predicate/arity"],
                }
            ],
            "risky_predicates": [
                {
                    "signature": "predicate/arity",
                    "risk": "why this predicate may be too broad, unsafe, or hard to query",
                    "recommended_action": "keep|rename|replace|remove|narrow",
                }
            ],
            "retry_guidance": ["concise guidance for a second profile-bootstrap pass"],
            "self_check": {"review_authority": "proposal_only", "notes": [""]},
        }
    return payload


def build_profile_bootstrap_messages(
    *,
    samples: list[dict[str, Any]],
    domain_hint: str = "",
    existing_profiles: list[dict[str, Any]] | None = None,
    include_schema_contract: bool = True,
) -> list[dict[str, str]]:
    payload = build_profile_bootstrap_payload(
        samples=samples,
        domain_hint=domain_hint,
        existing_profiles=existing_profiles,
        include_schema_contract=include_schema_contract,
    )
    return [
        {"role": "system", "content": PROFILE_BOOTSTRAP_SYSTEM},
        {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
    ]


def build_profile_bootstrap_review_messages(
    *,
    source_text: str,
    source_name: str = "",
    domain_hint: str = "",
    intake_plan: dict[str, Any] | None = None,
    proposed_profile: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    payload = build_profile_bootstrap_review_payload(
        source_text=source_text,
        source_name=source_name,
        domain_hint=domain_hint,
        intake_plan=intake_plan,
        proposed_profile=proposed_profile,
    )
    return [
        {"role": "system", "content": PROFILE_BOOTSTRAP_REVIEW_SYSTEM},
        {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
    ]


def parse_profile_bootstrap_json(text: str) -> tuple[dict[str, Any] | None, str]:
    raw = str(text or "").strip()
    if not raw:
        return None, "empty"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.S)
        if not match:
            return None, "not_json"
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            return None, f"json_error:{exc}"
    if not isinstance(parsed, dict):
        return None, "json_not_object"
    if parsed.get("schema_version") != "profile_bootstrap_v1":
        return None, "wrong_schema_version"
    return parsed, ""


def parse_profile_bootstrap_review_json(text: str) -> tuple[dict[str, Any] | None, str]:
    raw = str(text or "").strip()
    if not raw:
        return None, "empty"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.S)
        if not match:
            return None, "not_json"
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            return None, f"json_error:{exc}"
    if not isinstance(parsed, dict):
        return None, "json_not_object"
    if parsed.get("schema_version") != "profile_bootstrap_review_v1":
        return None, "wrong_schema_version"
    return parsed, ""


def profile_bootstrap_score(parsed: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(parsed, dict):
        return {
            "schema_ok": False,
            "entity_type_count": 0,
            "predicate_count": 0,
            "risk_count": 0,
            "frontier_case_count": 0,
            "frontier_unknown_positive_predicate_count": 0,
            "frontier_unknown_positive_predicate_refs": [],
            "repeated_structure_count": 0,
            "repeated_structure_unknown_predicate_refs": [],
            "repeated_structure_id_only_record_refs": [],
            "repeated_structure_role_mismatch_refs": [],
            "rough_score": 0.0,
        }
    schema_ok = parsed.get("schema_version") == "profile_bootstrap_v1"
    entity_count = len([item for item in parsed.get("entity_types", []) if isinstance(item, dict)])
    predicates = [item for item in parsed.get("candidate_predicates", []) if isinstance(item, dict)]
    predicate_count = len(predicates)
    generic_names = {"event_occurred", "policy_constraint", "candidate_relation", "related_to", "has_relation"}
    generic_predicate_count = 0
    predicate_args_by_signature: dict[str, list[str]] = {}
    for item in predicates:
        signature = str(item.get("signature", ""))
        name = signature.split("/", 1)[0].strip().casefold()
        if name in generic_names:
            generic_predicate_count += 1
        signature_key = _signature_key(signature)
        if signature_key:
            predicate_args_by_signature[signature_key] = [
                str(arg).strip().casefold()
                for arg in item.get("args", [])
                if isinstance(item.get("args"), list) and str(arg).strip()
            ]
    proposed_signatures = {_signature_key(str(item.get("signature", ""))) for item in predicates}
    proposed_signatures.discard("")
    risk_count = len([item for item in parsed.get("admission_risks", []) if str(item).strip()])
    frontier_cases = [item for item in parsed.get("starter_frontier_cases", []) if isinstance(item, dict)]
    frontier_count = len(frontier_cases)
    unknown_frontier_refs: list[str] = []
    for item in frontier_cases:
        positive_text = _positive_boundary_text(str(item.get("expected_boundary", "")))
        for ref in _predicate_refs(positive_text):
            if ref not in proposed_signatures:
                unknown_frontier_refs.append(ref)
    unknown_frontier_refs = sorted(set(unknown_frontier_refs))
    repeated_structures = [item for item in parsed.get("repeated_structures", []) if isinstance(item, dict)]
    repeated_unknown_refs: list[str] = []
    repeated_id_only_record_refs: list[str] = []
    repeated_role_mismatch_refs: list[str] = []
    for item in repeated_structures:
        property_predicates = item.get("property_predicates", [])
        if not isinstance(property_predicates, list):
            property_predicates = []
        record_signature = _signature_key(str(item.get("record_predicate", "")))
        if record_signature.endswith("/1"):
            repeated_id_only_record_refs.append(record_signature)
        for ref in [str(item.get("record_predicate", "")), *property_predicates]:
            signature = _signature_key(str(ref))
            if signature and signature not in proposed_signatures:
                repeated_unknown_refs.append(signature)
            if signature and signature in proposed_signatures and signature != record_signature:
                args = predicate_args_by_signature.get(signature, [])
                first_arg = args[0] if args else ""
                if first_arg and "id" not in first_arg and "record" not in first_arg:
                    repeated_role_mismatch_refs.append(signature)
    repeated_unknown_refs = sorted(set(repeated_unknown_refs))
    repeated_id_only_record_refs = sorted(set(repeated_id_only_record_refs))
    repeated_role_mismatch_refs = sorted(set(repeated_role_mismatch_refs))
    specificity_score = 1.0 - min(generic_predicate_count, max(1, predicate_count)) / max(1, predicate_count)
    frontier_consistency = 1.0 if not unknown_frontier_refs else 0.0
    repeated_structure_score = min(len(repeated_structures), 2) / 2
    repeated_consistency = 1.0 if not (repeated_unknown_refs or repeated_id_only_record_refs or repeated_role_mismatch_refs) else 0.0
    rough_score = (
        (1 if schema_ok else 0)
        + min(entity_count, 4) / 4
        + min(predicate_count, 6) / 6
        + min(risk_count, 4) / 4
        + min(frontier_count, 3) / 3
        + specificity_score
        + frontier_consistency
        + repeated_structure_score
        + repeated_consistency
    ) / 9
    return {
        "schema_ok": schema_ok,
        "entity_type_count": entity_count,
        "predicate_count": predicate_count,
        "generic_predicate_count": generic_predicate_count,
        "frontier_unknown_positive_predicate_count": len(unknown_frontier_refs),
        "frontier_unknown_positive_predicate_refs": unknown_frontier_refs,
        "repeated_structure_count": len(repeated_structures),
        "repeated_structure_unknown_predicate_refs": repeated_unknown_refs,
        "repeated_structure_id_only_record_refs": repeated_id_only_record_refs,
        "repeated_structure_role_mismatch_refs": repeated_role_mismatch_refs,
        "risk_count": risk_count,
        "frontier_case_count": frontier_count,
        "rough_score": round(float(rough_score), 3),
    }


def profile_bootstrap_allowed_predicates(parsed: dict[str, Any] | None) -> list[str]:
    if not isinstance(parsed, dict):
        return []
    predicates = parsed.get("candidate_predicates", [])
    if not isinstance(predicates, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in predicates:
        if not isinstance(item, dict):
            continue
        signature = _signature_key(str(item.get("signature", "")))
        if signature and signature not in seen:
            seen.add(signature)
            out.append(signature)
    return out


def profile_bootstrap_predicate_contracts(parsed: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(parsed, dict):
        return []
    predicates = parsed.get("candidate_predicates", [])
    if not isinstance(predicates, list):
        return []
    contracts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in predicates:
        if not isinstance(item, dict):
            continue
        signature = _signature_key(str(item.get("signature", "")))
        if not signature:
            continue
        if signature in seen:
            continue
        seen.add(signature)
        contract: dict[str, Any] = {
            "signature": signature,
            "arguments": [str(arg).strip() for arg in item.get("args", []) if str(arg).strip()]
            if isinstance(item.get("args"), list)
            else [],
        }
        notes = " ".join(
            [
                str(item.get("description", "")).strip(),
                str(item.get("why", "")).strip(),
                " ".join(str(note).strip() for note in item.get("admission_notes", []) if str(note).strip())
                if isinstance(item.get("admission_notes"), list)
                else "",
            ]
        ).strip()
        if notes:
            contract["notes"] = notes
        contracts.append(contract)
    return contracts


def profile_bootstrap_domain_context(parsed: dict[str, Any] | None) -> list[str]:
    if not isinstance(parsed, dict):
        return []
    context: list[str] = []
    domain_guess = str(parsed.get("domain_guess", "")).strip()
    domain_scope = str(parsed.get("domain_scope", "")).strip()
    if domain_guess:
        context.append(f"draft_profile_id: {domain_guess}@bootstrap")
    if domain_scope:
        context.append(f"profile_scope: {domain_scope}")
    for risk in parsed.get("admission_risks", []) if isinstance(parsed.get("admission_risks"), list) else []:
        text = str(risk).strip()
        if text:
            context.append(f"admission_risk: {text}")
    for policy in parsed.get("clarification_policy", []) if isinstance(parsed.get("clarification_policy"), list) else []:
        text = str(policy).strip()
        if text:
            context.append(f"clarification_policy: {text}")
    for item in parsed.get("repeated_structures", []) if isinstance(parsed.get("repeated_structures"), list) else []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        record = str(item.get("record_predicate", "")).strip()
        props = ", ".join(str(ref).strip() for ref in item.get("property_predicates", []) if str(ref).strip()) if isinstance(item.get("property_predicates"), list) else ""
        if name or record or props:
            context.append(f"repeated_structure: {name}; record={record}; properties={props}")
    for transform in parsed.get("unsafe_transformations", []) if isinstance(parsed.get("unsafe_transformations"), list) else []:
        text = str(transform).strip()
        if text:
            context.append(f"unsafe_transformation: {text}")
    context.append(
        "draft_profile_operation_policy: Candidate predicates such as obligation/3, conditional_right/3, "
        "prohibition/3, conflict_rule/3, and override_rule/3 are ordinary record predicates unless the model can emit "
        "a precise executable Horn clause. Use operation='assert' for direct source-grounded normative records; "
        "use operation='rule' only when candidate_operations[].clause contains an executable rule. A safe "
        "operation='rule' without an executable clause is not admitted by the mapper."
    )
    context.append(
        "authority_boundary: This is a draft profile supplied for semantic parsing guidance only; "
        "deterministic admission still owns KB mutation."
    )
    return context


def profile_bootstrap_frontier_cases(parsed: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(parsed, dict):
        return []
    cases = parsed.get("starter_frontier_cases", [])
    if not isinstance(cases, list):
        return []
    out: list[dict[str, Any]] = []
    for index, item in enumerate(cases, start=1):
        if not isinstance(item, dict):
            continue
        utterance = str(item.get("utterance", "")).strip()
        if not utterance:
            continue
        out.append(
            {
                "id": f"bootstrap_case_{index:02d}",
                "utterance": utterance,
                "expected_boundary": str(item.get("expected_boundary", "")).strip(),
                "must_not_write": [str(row).strip() for row in item.get("must_not_write", []) if str(row).strip()]
                if isinstance(item.get("must_not_write"), list)
                else [],
            }
        )
    return out


def _signature_key(signature: str) -> str:
    match = re.fullmatch(r"\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*/\s*(\d+)\s*", signature)
    if not match:
        return ""
    return f"{match.group(1).casefold()}/{match.group(2)}"


def _predicate_refs(text: str) -> set[str]:
    refs: set[str] = set()
    for match in re.finditer(r"\b([a-zA-Z_][a-zA-Z0-9_]*)/(\d+)\b", str(text or "")):
        refs.add(f"{match.group(1).casefold()}/{match.group(2)}")
    refs.update(_predicate_call_refs(str(text or "")))
    return refs


def _predicate_call_refs(text: str) -> set[str]:
    refs: set[str] = set()
    raw = str(text or "")
    for match in re.finditer(r"\b([a-z][a-z0-9_]*)\s*\(", raw):
        name = match.group(1).casefold()
        close_index = _matching_paren(raw, match.end() - 1)
        if close_index is None:
            continue
        args_text = raw[match.end() : close_index]
        refs.add(f"{name}/{_arity(args_text)}")
    return refs


def _matching_paren(text: str, open_index: int) -> int | None:
    depth = 0
    for index in range(open_index, len(text)):
        char = text[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
    return None


def _arity(args_text: str) -> int:
    text = str(args_text or "").strip()
    if not text:
        return 0
    depth = 0
    count = 1
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            count += 1
    return count


def _positive_boundary_text(text: str) -> str:
    match = re.search(r"\bdo\s+not\s+write\b", str(text or ""), flags=re.I)
    if not match:
        return str(text or "")
    return str(text or "")[: match.start()]

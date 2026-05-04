#!/usr/bin/env python3
"""Bootstrap a draft domain profile from one raw text file.

This runner is intentionally small and literal: Python reads the file and hands
the raw text to the LLM profile-bootstrap pass. It does not derive predicates,
split the text semantically, rewrite phrases, or inspect the language. The model
proposes the candidate predicate surface; deterministic code only validates,
scores, and optionally uses that draft surface in the ordinary Semantic IR path.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "domain_bootstrap_file"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

PROFILE_SIGNATURE_ROSTER_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "domain_guess",
        "domain_scope",
        "confidence",
        "source_summary",
        "entity_types",
        "candidate_signatures",
        "repeated_structures",
        "admission_risks",
        "clarification_policy",
        "unsafe_transformations",
        "self_check",
    ],
    "properties": {
        "schema_version": {"type": "string", "const": "profile_signature_roster_v1"},
        "domain_guess": {"type": "string"},
        "domain_scope": {"type": "string"},
        "confidence": {"type": "number"},
        "source_summary": {"type": "array", "maxItems": 3, "items": {"type": "string", "maxLength": 220}},
        "entity_types": {
            "type": "array",
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "description"],
                "properties": {
                    "name": {"type": "string", "maxLength": 40},
                    "description": {"type": "string", "maxLength": 180},
                },
            },
        },
        "candidate_signatures": {
            "type": "array",
            "maxItems": 48,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["signature", "description", "admission_notes"],
                "properties": {
                    "signature": {"type": "string", "maxLength": 64, "pattern": "^[a-z][a-z0-9_]*/[1-5]$"},
                    "description": {"type": "string", "maxLength": 180},
                    "admission_notes": {"type": "array", "maxItems": 3, "items": {"type": "string", "maxLength": 160}},
                },
            },
        },
        "repeated_structures": {
            "type": "array",
            "maxItems": 4,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "record_predicate", "property_predicates"],
                "properties": {
                    "name": {"type": "string", "maxLength": 80},
                    "record_predicate": {"type": "string", "maxLength": 64},
                    "property_predicates": {"type": "array", "maxItems": 16, "items": {"type": "string", "maxLength": 64}},
                },
            },
        },
        "admission_risks": {"type": "array", "maxItems": 6, "items": {"type": "string", "maxLength": 180}},
        "clarification_policy": {"type": "array", "maxItems": 6, "items": {"type": "string", "maxLength": 180}},
        "unsafe_transformations": {"type": "array", "maxItems": 6, "items": {"type": "string", "maxLength": 180}},
        "self_check": {
            "type": "object",
            "additionalProperties": False,
            "required": ["notes"],
            "properties": {"notes": {"type": "array", "maxItems": 6, "items": {"type": "string", "maxLength": 160}}},
        },
    },
}

NARRATIVE_SOURCE_COMPILER_CONTEXT_V1 = [
    "narrative_source_compiler_strategy_v1: Use this only for sources classified by the LLM intake plan or domain hint as story, narrative, fable, fiction, plot, or source-fidelity story-world material.",
    "Narrative source rule: compile the closed world of this source text. Do not import facts, character names, motives, objects, or endings from famous stories, genre priors, or likely variants.",
    "Narrative source rule: preserve source-local names and aliases. If the text says Little Slip of an Otter, Great Long Otter, or Tilly Tumbletop, do not normalize them to unrelated familiar names.",
    "Narrative source rule: build a story spine when the profile supports it. Prefer event records with actor, action/type, target/object, place, source span/phase, and story order over isolated verb facts.",
    "Narrative source rule: separate static state, event occurrence, character speech, narrator judgment, causal consequence, and final state. These are different epistemic jobs even when they share entities.",
    "Narrative source rule: subjective fit or quality language such as too hot, too cold, just right, too hard, too soft, or too high should be tied to an evaluator or narrator context when the profile supports it.",
    "Narrative source rule: quoted speech is a speech act by a character unless the source independently states the spoken content as narrator fact.",
    "Narrative source rule: when an event changes state, preserve both the event and the resulting state if the profile supports it. If a later repair changes the final state, preserve final-state or remediation outcome rather than leaving only the broken intermediate state.",
    "Narrative source rule: preserve errand, intention, forgetfulness, discovery, consequence, repair, and final emotional/condition states as queryable structure when stated by the source.",
    "Narrative story-world canonical palette preference: when the draft profile offers equivalent choices, prefer event/5 for event_id, actor, action, object, place; story_time/2 for event order; before/2 and after/2 for temporal ordering; causes/2 and caused_by/2 for consequence links.",
    "Narrative story-world canonical palette preference: prefer said/3 for event-scoped quoted speech or source-stated speech acts; prefer judged/4 for evaluator, item, dimension, judgment; prefer owned_by/2 for item-to-owner ownership; prefer designed_for/2 for items made for a character.",
    "Narrative story-world canonical palette preference: prefer initial_location/2 and location_after_event/3 when the source gives object locations or movement; prefer final_state/1 and condition_after_story/2 for repaired, remaining, or resolved end-state facts.",
    "Narrative story-world canonical palette preference: prefer household/1, household_member/2, character/1, object/1, place/1, food/1, name/2, kind/2, and property/2 for source-local cast and object taxonomy when the profile supports these classes.",
    "Narrative story-world canonical palette warning: do not invent near-synonym predicate surfaces such as happens_before/2, says/3, evaluates_as/3, located_at/2, owns/2, or results_in/2 when the draft profile also provides the canonical story-world predicates before/2, said/3, judged/4, initial_location/2, owned_by/2, or causes/2.",
    "Narrative story-world coverage warning: canonical predicates should not make the compile timid. Preserve representative facts for cast/entity taxonomy, ownership/design, locations, event spine, story order, speech, subjective judgment, causality, remediation, and final state when the source and profile support them.",
    "Narrative story-world ledger rule: before emitting event-heavy facts, establish a source-local entity/object/place ledger in the workspace and reuse those canonical atoms in every pass. Do not emit parallel atoms for the same house, object, character, food, or place unless the source distinguishes them.",
    "Narrative story-world object rule: repeated sized object triads should use compact source-local object atoms based on size and kind, such as small_cup, medium_cup, large_cup, small_tool, or large_vehicle, when the source names them that way. Do not over-prefix every object with the owner when owned_by/2 and designed_for/2 can carry ownership/intended-user separately.",
    "Narrative story-world object coverage: when object/1, kind/2, size/2, owned_by/2, designed_for/2, and initial_location/2 are available, preserve all of those facets for important repeated objects instead of only one ownership row. For repeated object families, emit the whole family in one consistent atom pattern: little/middle/great mug, little/middle/great boots, little/middle/great boat, or equivalent source-local families.",
    "Narrative story-world inventory coverage: introductory inventory lists are not decorative. If the source lists repeated possessed objects by size or owner, preserve every listed family even if later scenes focus on only one family. Do not drop cups/mugs/bowls, tools, footwear, vehicles, beds, boats, keys, or other listed object triads simply because later action scenes are more salient.",
    "Narrative story-world setting coverage: when located_in/2, under/2, near/2, part_of/2, or initial_location/2 are available, preserve descriptive setting relations for the home/place, not only lives_at/2 for residents.",
    "Narrative story-world food/occasion coverage: when ingredient_of/2, contains_before_eating/2, occasion/1, honoree/2, served_for/2, property/2, or portion_of/2 are available, preserve named ingredients/components, special occasions, honorees, and portion/component relations instead of reducing food to a single object.",
    "Narrative story-world event-spine coverage: when event/5 and story_time/2 are available, preserve source-stated actions such as making/baking/placing/leaving/gathering/entering/eating/trying/finding/repairing as event rows with stable event ids and story_time anchors. Use why_did_* helper predicates only when the profile provides them and the source directly states the reason.",
    "Narrative story-world backbone-plus-detail rule: rich detail predicates are additive layers, not substitutes for the queryable story backbone. Event, story_time, character, kind, lives_at, object/food/place, ownership/design, location, speech, judgment, cause, and final-state rows should survive in the same compile when the profile supports them.",
    "Narrative story-world registry mapping rule: if an intake pass recommends generic story predicates that are not in the allowed profile, map the pass purpose onto the actual allowed story-world predicates instead. For this style of source, the actual backbone is usually character/1, kind/2, household_member/2, lives_at/2, object/1, food/1, place/1, owned_by/2, designed_for/2, initial_location/2, location_after_event/3, event/5, story_time/2, said/3, judged/4, causes/2, caused_by/2, final_state/1, condition_after_story/2, and restitution/2.",
    "Narrative story-world entity-role rule: named characters, homes, object families, food/components, and important places are not merely entity metadata. If the profile supports typed rows and relationship rows, emit both the entity/type row and the relationship row so later queries can join them without guessing atoms.",
    "Narrative story-world taxonomy mapping rule: if a pass recommends is_character/1, is_object/1, is_location/1, or has_type/2 but those predicates are not allowed, use the actual typed predicates from the profile such as character/1, otter/1, human/1, object/1, food/1, place/1, kind/2, name/2, size/2, household/1, and household_member/2.",
    "Narrative story-world object-family join rule: for repeated sized possessions, use the same compact object atom across object/1, kind/2, size/2, owned_by/2, designed_for/2, initial_location/2, judged/4, event/5, and final-state rows. Do not emit owner-prefixed ownership atoms such as little_character_boots if the profile can represent ownership with owned_by(Object, Owner).",
    "Narrative story-world object-family coverage rule: for a stated little/middle/great or small/medium/large family, preserve every family member with the same predicate pattern before moving to later action scenes. A useful family row set is object(Item), kind(Item, FamilyKind), size(Item, Size), owned_by(Item, Owner), and designed_for(Item, Owner) when those predicates are available and the source supports them.",
    "Narrative story-world occasion/component rule: named food, ingredients, occasions, honorees, and reasons for leaving/returning are backbone rows when the profile has food/1, ingredient_of/2, contains_before_eating/2, occasion/1, honoree/2, served_for/2, event/5, story_time/2, and causes/2. Do not preserve only later eating/repair events while dropping the baked food, its components, and why characters left.",
    "Narrative source rule: if the profile lacks event, temporal-order, causal, or final-state predicates needed for the current pass, mention those missing capabilities in self_check rather than inventing out-of-palette predicates.",
]

DECLARATION_SOURCE_COMPILER_CONTEXT_V1 = [
    "declaration_source_compiler_strategy_v1: Use this for declaration, proclamation, manifesto, petition, recall, independence, grievance-list, or source-bound accusation documents.",
    "Declaration source rule: model the document's epistemic structure. The document is an actor making claims, asserting principles/rules, listing grievances or defects, and declaring actions; most accusations are source-bound claims rather than objective world facts.",
    "Declaration source backbone-plus-detail rule: record/detail predicates are additive layers, not substitutes for the document backbone. Source identity, declaring body, core entities, principles/rules, repeated records, record status/provenance, final declaration/action, and pledges/commitments should survive in the same compile when the profile supports them.",
    "Declaration source registry mapping rule: if an intake pass recommends generic predicates that are not in the allowed profile, map the pass purpose onto the actual allowed document predicates instead. Typical backbones include document/1, document_type/2, source_domain/2, declaring_body/2, organization/1, authority/1, group/1, institution/1, place/1, person/1, role/1, claim_made/3, principle/2, rule/2, rule_text/2, grievance/2, grievance_actor/2, grievance_target/2, method/2, purpose/2, condition_attached/2, evidence/2, status/provenance predicates, declaration_action/2, declared_independent/1, pledged/2, recall/2, impounded/2, and correction/status rows when available.",
    "Declaration source repeated-record rule: for grievance, defect, recall, accusation, or complaint lists, use stable record ids and preserve both the record label and high-query-value attributes such as actor, target, method, purpose, condition, evidence, reporter/ledger/source, and epistemic status when the profile supports those predicates.",
    "Declaration source status rule: if the profile offers a status predicate for grievances, claims, disclosures, allegations, recalls, or defects, emit it. Source-bound accusation, document_claim, disputed, recalled, impounded, corrected, or not-a-finding status should be queryable rather than hidden in a long label.",
    "Declaration source final-action rule: do not let a long repeated grievance list crowd out the conclusion. Preserve final declarations, recalls, impoundments, separations, authorizations, pledges, remedies, and future-governance commitments as first-class rows.",
]

INSURANCE_DISPUTE_SOURCE_COMPILER_CONTEXT_V1 = [
    "insurance_dispute_source_compiler_strategy_v1: Use this for sources classified by the LLM intake plan or domain hint as insurance, reinsurance, maritime loss, contract coverage, warranty, salvage, claims adjustment, or coverage dispute material.",
    "Insurance dispute rule: preserve contract boundaries before claim summaries. H&M policy, P&I cover, reinsurance treaty, retrocession, salvage contract, regulatory action, and legal-citation support are separate instruments or authorities, even when the same entity appears in more than one role.",
    "Insurance dispute role rule: role-scoped party rows are backbone facts. If the profile has party_role/3, company_role/3, contract_party/4, dual_role/3, underwriter_line/4, or equivalent, emit rows for every named owner, manager, underwriter, following underwriter, P&I club, reinsurer, retrocessionaire, salvor, class society, regulator, lawyer, surveyor, and witness before using long summary labels.",
    "Insurance dispute vessel/asset rule: entity_type(vessel, vessel) is too weak when the source gives asset details. If the profile supports asset_attribute, vessel_attribute, vessel/2, insured_value, built_year, dwt, flag, class, owner, or manager predicates, preserve those queryable details rather than hiding them inside entity metadata.",
    "Insurance dispute underwriter-share rule: if a policy lists insurer shares or lead/following status, preserve each party's share as a direct queryable row. Do not rely on a later net_exposure description to answer share questions.",
    "Insurance dispute financial-chain rule: preserve gross claimed amount, adjusted amount, deductible, claimant net, adjusted net, share percentage, share amount, attachment point, limit, and difference as separate rows when the profile supports them. A total amount label is not enough for later arithmetic questions.",
    "Insurance dispute source-attribution rule: expert reports, survey findings, legal positions, regulatory conclusions, witness statements, and party arguments are source-owned. Preserve source/speaker/report identity in the predicate arguments when available. Do not collapse competing accounts into a single fact.",
    "Insurance dispute survey rule: when two surveyors disagree, preserve both measurements and the stated methodology or basis for each measurement if the profile has measurement_claim, survey_finding, finding_discrepancy, methodology, or detail predicates.",
    "Insurance dispute class-scope rule: class society or survey rows often answer what was inspected and what was not inspected. If the profile has class_survey_scope, survey_scope_exclusion, source_detail, or equivalent predicates, emit scoped rows for inspected systems, excluded systems, conditions, and non-findings instead of burying them inside report summaries.",
    "Insurance dispute temporal rule: incident time, initially reported time, corrected time, notification time, condition-of-class imposition/lift, cover suspension/resumption, off-hire periods, and filing dates are distinct temporal anchors. If the profile supports correction rows, emit both superseded and corrected values with the reason or authority.",
    "Insurance dispute cover-window rule: cover suspension or reinstatement windows need start, end, policy, and basis/status. Do not answer suspension, duration, or cost-allocation questions from policy_clause text alone if the profile has cover_suspension or temporal predicates.",
    "Insurance dispute deadline rule: notice windows, hours/days limits, awareness times, notice-sent times, and late/timely conclusions are query-bearing rows. If the profile has notification_event, temporal_duration, reinsurance_notice_effect, contract_clause, source_detail, or calculation_step predicates, preserve the raw anchors and the computed lateness or timeliness separately from the legal effect.",
    "Insurance dispute loss-of-hire rule: loss-of-hire is not the same cover as hull damage. If the profile has loss_of_hire_period, loss_of_hire_position, charter_rate, temporal_duration, or equivalent predicates, preserve the claimed period, opposing coverage position, separate policy status, and rate basis as queryable rows.",
    "Insurance dispute reinsurance rule: reinsurance late notice is not automatically a defense to the assured's claim unless the source says so. Preserve attachment/limit/current-trigger status and late-notice effect separately from the assured's entitlement.",
    "Insurance dispute salvage rule: salvage security, guarantee, award, payment, and liability are different statuses. If the profile has security_posted, salvage_contract, or payment-status predicates, do not treat security as a paid award.",
    "Insurance dispute sanctions rule: sanctions, trading warranties, cancellations, port calls, and defense status form a chain. If the profile has sanctions_event, port_call, trading_warranty_status, defense_status, legal_position, or source_detail predicates, preserve each link and mark whether a position was raised, withdrawn, conceded, or merely hypothetical.",
    "Insurance dispute citation rule: legal citations support a party's position. If the profile has legal_citation or citation_support predicates, preserve the citation, the party/source using it, the issue, and the use/status. Do not turn citations into court findings or resolved truth about the dispute.",
    "Insurance dispute repair-cost rule: repair estimates often contain agreed items, disputed items, excluded items, and deltas. If the profile has repair_cost_item, cost_agreement, cost_disagreement, cost_claim, or calculation_step predicates, preserve itemized amounts and agreement/disagreement status before emitting a summary total.",
    "Insurance dispute claim-handler rule: claims-handler, broker, solicitor, adjuster, or party statements about acceptance, non-acceptance, reservation of rights, without-prejudice status, and full/partial agreement are source-owned position rows. Preserve the speaker and statement content with legal_position, source_detail, defense_status, cost_agreement, claim_amount, or equivalent predicates when available.",
    "Insurance dispute witness-detail rule: witness statements with numbers, times, measurements, draft/depth values, route/chart details, or safety conclusions should preserve those details in source_detail, witness_statement content, measurement_claim, or statement-detail predicates when available. Do not compress quantitative testimony into a label if later questions may ask for the numbers.",
    "Insurance dispute P&I rule: protection-and-indemnity cover has its own year/period, notification duties, exclusions, and club positions. If the profile has p_i_cover, p_i_notification_requirement, legal_position, or source_detail predicates, preserve those rows separately from hull-and-machinery and reinsurance rows.",
    "Insurance dispute multilingual rule: witness statements in non-English languages are source-owned statement records. Preserve speaker, language, topic/content, and source context when the profile supports witness_statement or statement_detail predicates.",
]

SOURCE_ENTITY_LEDGER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "source_kind",
        "canonical_entities",
        "object_families",
        "coverage_targets",
        "alias_notes",
        "risk_notes",
    ],
    "properties": {
        "schema_version": {"type": "string", "const": "source_entity_ledger_v1"},
        "source_kind": {"type": "string"},
        "canonical_entities": {
            "type": "array",
            "maxItems": 96,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["atom", "surface", "category", "aliases"],
                "properties": {
                    "atom": {"type": "string"},
                    "surface": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": ["character", "place", "object", "food", "event", "group", "document", "abstract", "unknown"],
                    },
                    "aliases": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
                },
            },
        },
        "object_families": {
            "type": "array",
            "maxItems": 32,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["family", "members", "owner_or_intended_user_pattern"],
                "properties": {
                    "family": {"type": "string"},
                    "members": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
                    "owner_or_intended_user_pattern": {"type": "string"},
                },
            },
        },
        "coverage_targets": {
            "type": "array",
            "maxItems": 40,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["target_id", "lens", "anchor_atoms", "coverage_goal", "risk_note"],
                "properties": {
                    "target_id": {"type": "string"},
                    "lens": {
                        "type": "string",
                        "enum": [
                            "taxonomy_static",
                            "event_spine",
                            "state_change",
                            "final_state",
                            "speech_claim",
                            "subjective_judgment",
                            "causality",
                            "rule_like_norm",
                            "clarification_risk",
                            "source_metadata",
                            "other",
                        ],
                    },
                    "anchor_atoms": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
                    "coverage_goal": {"type": "string"},
                    "risk_note": {"type": "string"},
                },
            },
        },
        "alias_notes": {"type": "array", "maxItems": 24, "items": {"type": "string"}},
        "risk_notes": {"type": "array", "maxItems": 16, "items": {"type": "string"}},
    },
}

SOURCE_PASS_OPS_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "pass_id", "decision", "candidate_operations", "self_check"],
    "properties": {
        "schema_version": {"type": "string", "const": "source_pass_ops_v1"},
        "pass_id": {"type": "string"},
        "decision": {
            "type": "string",
            "enum": ["commit", "clarify", "quarantine", "reject", "answer", "mixed"],
        },
        "candidate_operations": {
            "type": "array",
            "maxItems": 64,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["operation", "proposition_id", "predicate", "args", "polarity", "source", "safety"],
                "properties": {
                    "operation": {"type": "string", "enum": ["assert", "retract", "rule", "query", "none"]},
                    "proposition_id": {"type": "string"},
                    "predicate": {"type": "string"},
                    "args": {"type": "array", "items": {"type": "string"}},
                    "clause": {"type": "string"},
                    "polarity": {"type": "string", "enum": ["positive", "negative"]},
                    "source": {"type": "string", "enum": ["direct", "inferred", "context"]},
                    "safety": {"type": "string", "enum": ["safe", "unsafe", "needs_clarification"]},
                },
            },
        },
        "self_check": {
            "type": "object",
            "additionalProperties": False,
            "required": ["bad_commit_risk", "missing_slots", "notes"],
            "properties": {
                "bad_commit_risk": {"type": "string", "enum": ["low", "medium", "high"]},
                "missing_slots": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
                "notes": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
            },
        },
    },
}

POLICY_INCIDENT_SOURCE_COMPILER_CONTEXT_V1 = [
    "policy_incident_source_compiler_strategy_v1: Use this for sources classified by the LLM intake plan or domain hint as policy, compliance, incident, operations log, regulatory record, timeline, or municipal/organizational procedure.",
    "Policy incident rule: separate standing rules from observed incident facts. A threshold, deadline, required role, exception, or validity condition is not the same kind of state as a timestamped reading, notification, outage, authorization, correction, or review statement.",
    "Policy incident rule: when the profile offers exact predicates for measurements, thresholds, intervals, state changes, notifications, authorizations, inspections, corrections, and temporal ordering, prefer those exact predicates over generic event/status wrappers.",
    "Policy incident rule: preserve scoped applicability and exclusions. If the source distinguishes residential zones, industrial zones, downstream zones, affected zones, or excluded zones, compile those classifications and scope relations before deriving any compliance conclusion.",
    "Policy incident rule: preserve timestamps as queryable values on the relevant event or observation predicates. Do not hide deadlines or times inside long normalized labels when the profile provides date/time slots.",
    "Policy incident rule: preserve corrections as authoritative corrected facts plus parked claims or self_check notes for superseded values when the profile supports that distinction. Do not commit both old and corrected values as equal truth.",
    "Policy incident rule: when the selected profile offers source_claim/4 and correction_record/4, explicit language such as initially, wait no, correction, retracted, transcription error, badge log authoritative, or written log confirms should normally produce both a parked source_claim for the superseded statement and a correction_record linking original value, corrected value, and authority.",
    "Policy incident rule: preserve joint authorization and prerequisite validity as structured policy requirements and timestamped authorization/inspection facts when the profile supports them.",
    "Policy incident rule: when a rule sentence says a role's authorization is valid only if a prerequisite inspection, review, test, or approval occurred within a time window, emit both the compact threshold predicate when available and a policy_requirement/3 row for the prerequisite itself. Do not leave the actor/prerequisite relationship only implicit in observed inspection rows.",
    "Policy incident source-surface rule: statement_detail/3 and source_claim/4 are additive detail layers. They must not replace the backbone rows that make the KB queryable: person_role/2, facility/2, governing_bylaw/2, policy_requirement/3, witness_statement/4, reported_event/4, correction_filing/3, and the core timestamped event predicates.",
    "Policy incident policy coverage rule: when the source has a standing-policy section and policy_requirement/3 is available, preserve every distinct stated requirement as a compact policy_requirement row, including triggers, thresholds, deadlines, notification scope, treatment path/prohibition, authorization roles, inspection prerequisites, and lift conditions. Do not emit only the requirements that later incident facts mention.",
    "Policy incident registry mapping rule: if an intake plan recommends generic predicates such as policy_rule, threshold_value, interval_duration, event_occurred, administrative_action, witness_claimed, compliance_violation, or final_state but those predicates are not in the allowed profile, map the pass purpose onto the actual allowed policy-incident predicates instead. For this style of source, the actual backbone is usually governing_bylaw/2, person_role/2, facility/2, policy_requirement/3, threshold predicates, coliform_reading/4, facility_status/3, notification/5, bypass_authorization/3, inspection/3, witness_statement/4, reported_event/4, correction_record/4, disclosure/4, and correction_filing/3.",
    "Policy incident entity-role rule: named people and facilities are not merely entity metadata. If person_role/2 or facility/2 is available, emit queryable role/facility rows for every explicitly named officer, technician, operator, manager, authority, intake point, treatment facility, or bypass unit.",
    "Policy incident rule: preserve notification recipients, notice type, time, method, and notifying actor separately when the profile supports those slots.",
    "Policy incident rule: preserve review-board statements, witness statements, disclosures, and allegations as claims or review records unless the source states an authoritative finding.",
    "Policy incident rule: when the palette offers statement_detail/3 or an equivalent detail predicate, preserve source-owned explanations that later questions may ask about, such as why an officer believed a deadline or authorization was valid. These remain statement details, not review-board findings.",
    "Policy incident rule: for correction/addendum sections, preserve each numbered correction and each addendum as its own filing/source-record row when the palette offers correction_filing/3 or equivalent. Do not compress three corrections plus one addendum into a single combined correction_addendum row.",
    "Policy incident coverage warning: a useful skeleton should include roles, scoped zones/entities, core facilities/systems, standing policy thresholds/deadlines, key measurements, advisory or trigger state, facility status changes, notifications, authorizations, inspections, corrections, and temporal order when the source and profile support them.",
    "Policy incident canonical palette warning: do not invent vague substitutes such as event_occurred/4, policy_constraint/3, or compliance_status/3 when the draft profile provides a more precise predicate for the same job.",
    "Policy incident atom ledger rule: choose one canonical atom for each person, facility, zone, system, and timestamp, then reuse it everywhere. Do not emit both given_surname and surname_given forms for the same person, and do not emit both a short facility atom and a long facility atom for the same facility unless the source distinguishes them.",
    "Policy incident atom ledger preference: for full personal names, prefer given_surname; for initial-plus-surname mentions, prefer initial_surname; for role-only mentions, reuse the named role-holder atom only when the source has already identified that role holder. For timestamps, use one normalized timestamp surface consistently across all predicates.",
    "Policy incident QA-readiness rule: if a person or facility appears in a role row and in later event, inspection, notification, authorization, correction, or disclosure rows, the same atom must connect those rows so later queries can join them without alias repair.",
]

RULE_INGESTION_SOURCE_COMPILER_CONTEXT_V1 = [
    "rule_ingestion_source_compiler_strategy_v1: Use this for source documents classified by the LLM intake plan or domain hint as charters, standing rules, operational policies, bylaws, ordinances, contracts, eligibility rules, tax rules, permission rules, exception ladders, or priority rules.",
    "Rule ingestion rule: preserve source-stated rules in two layers when the profile supports both layers. First emit source_rule/rule_text/requirement/exception/override rows that record the charter language. Second emit operation='rule' candidate_operations only for bounded executable Horn-style rules whose head and body predicates are all in the allowed profile.",
    "Executable-rule boundary: a rule operation is a candidate, not truth by itself. Never use an executable rule to smuggle an inferred current violation, finding, clearance, tax liability, or permission as a fact. The mapper admits the clause; later Prolog queries derive consequences.",
    "Executable-rule clause requirement: if operation='rule', candidate_operations[].clause must contain the actual Prolog-style clause. Do not emit safe rule operations with only a label. If the rule uses default, exception, unless, only-if, priority, or override semantics that cannot be safely expressed with the allowed predicates, record the source rule as source_rule/rule_text/requirement/exception/override and mark the executable version as missing or unsafe in self_check.",
    "Rule-head discipline: choose a query-bearing head predicate that names the derived status, permission, obligation, tax status, authorization status, clearance status, access status, reward status, or source-priority result. Use allowed profile predicates only; do not invent a new head if the allowed palette lacks it.",
    "Rule-body discipline: bodies should join admitted factual predicates, temporal predicates, role predicates, source-priority predicates, exception predicates, and negative conditions only when the source explicitly states the condition and the profile has the needed predicates. Prefer small clauses over giant prose-shaped clauses.",
    "Exception discipline: unless/except/only-if language is not an ordinary positive fact. Preserve the exception row and, only if safe, encode the exception in the executable clause with a bounded negated predicate such as \\+ relief_cargo(Cargo), \\+ signed_clearance(Vessel), or \\+ emergency_override(Proposal).",
    "Priority discipline: source-ranking rules should not collapse competing records into one fact. Preserve the weaker and stronger records separately, then use an executable rule only for the derived effective value or controlling source when the priority relation is explicit and the palette supports the required predicates.",
    "Permission-event distinction: permission_at/authorization predicates mean an action is allowed, not that the action occurred. event_at/observed/certified_record predicates mean the source states occurrence. Emit both only when both are source-supported.",
    "Claim-finding distinction: captain statements, clerk notes, party explanations, and witness reports remain claims or lower-priority records unless a certified log, watch log, instrument record, or other source-stated finding support makes them findings under the source's own evidence rules.",
    "Temporal rule discipline: when a rule depends on a window, deadline, at-least duration, active alarm, reopened state, or following-day revocation, preserve the raw time anchors and the rule clause separately. Do not hide the temporal calculation in a long rule label.",
    "Rule ingestion coverage warning: a useful skeleton for a charter source should include source identity, rule records, role/authority rows, time anchors/windows, factual event/status rows, permission/authorization rows, claim/evidence rows, exception/override rows, and executable rule clauses for the safe rule families supported by the selected profile.",
]

ENTERPRISE_GUIDANCE_SOURCE_COMPILER_CONTEXT_V1 = [
    "enterprise_guidance_source_compiler_strategy_v1: Use this for sources classified by the LLM intake plan or domain hint as enterprise guidance, technical policy, performance guidance, modeling rules, operational best practices, or product optimization procedures.",
    "Enterprise guidance rule: preserve the guidance structure, not only the headline recommendation. A useful compile keeps distinct rows for trigger/condition, recommendation/preference, avoid-pattern, reason/rationale, tradeoff, procedure/checklist step, metric boundary, and exception when the profile supports them.",
    "Enterprise guidance rule: recommendations are not objective facts about the world. They are source-owned guidance. Use recommendation, action_when, prefer, avoid, priority, tradeoff, procedure, or rule predicates according to the allowed profile; do not turn a recommendation into a completed action.",
    "Enterprise guidance rationale rule: if the source states why a practice matters, preserve the reason as a queryable row such as priority_reason/2, export_reason/2, tradeoff/3, guard_effect/1, source_detail/4, or an equivalent allowed predicate. Do not hide the reason inside the recommendation atom when a reason predicate exists.",
    "Enterprise guidance avoid/alternative rule: when the source says avoid X and use Y instead, emit both sides if the profile supports them: avoid_pattern(X) plus recommendation(Y), preferred_export(Y, Purpose), delta_load_pattern(Part, Implementation), or another positive replacement row. Avoid rows alone are not enough for later 'what instead' questions.",
    "Enterprise guidance metric-boundary rule: preserve what each metric means, what it does not directly determine, and what high values validate. For metrics such as size, GB, complexity, populated cells, or calculation effort, keep semantics and boundary rows separate from optimization recommendations.",
    "Enterprise guidance priority rule: optimization order is answer-bearing. If the source ranks target classes, emit optimization_priority(Target, Rank) and a reason/rationale row when stated. Do not reduce ranked guidance to an unordered recommendation list.",
    "Enterprise guidance guard rule: guards need value, mechanism, and effect surfaces. If the profile supports guard_value/1, guard_mechanism/1, and guard_effect/1, emit all source-stated guard values, the conditional mechanism, and each stated effect rather than only recommendation(use_guards_effectively).",
    "Enterprise guidance procedure rule: debugging/checklist/procedure sentences should become queryable steps when the profile supports debugging_tactic/2, action_when/2, summary_review_question/1, or equivalent procedure predicates. Preserve conditions and steps separately.",
    "Enterprise guidance export rule: export guidance often distinguishes export type, reason, and preferred purpose. Preserve export_rule/2, export_reason/2, and preferred_export/2 separately when available; do not collapse Tabular Multiple Column Export and Combined Grids into one generic export recommendation.",
    "Enterprise guidance integration rule: for intraday or incremental-load guidance, preserve the anti-pattern, the positive replacement pattern, and the filter/condition logic. Full clear-and-reload, delta loads, staging model, current-vs-previous dimension, and current-not-equal-previous filter are separate query surfaces when stated.",
    "Enterprise guidance feature-validity rule: when the source says to test with realistic load, seed a DEV list, or use a loaded test model so a product can validate/reject formulas, preserve both the recommended setup and the rationale/error class if the profile has recommendation, debugging_tactic, action_when, or detail predicates.",
    "Enterprise guidance canonical palette warning: do not invent near-synonym predicates such as should_use/2, best_practice/2, reason_for/2, or optimize_by/2 when the draft profile provides exact enterprise-guidance predicates such as recommendation/1, action_when/2, priority_reason/2, tradeoff/3, debugging_tactic/2, export_reason/2, or delta_load_pattern/2.",
    "Enterprise guidance coverage warning: a useful skeleton should include source metadata, performance metrics and metric boundaries, ranked optimization targets, guard values/mechanisms/effects, summary-method review checks, computationally intensive functions, avoid/prefer pairs, export guidance, incremental-load guidance, and debugging tactics when the source and profile support them.",
]

PROCEDURAL_MISCONDUCT_SOURCE_COMPILER_CONTEXT_V1 = [
    "procedural_misconduct_source_compiler_strategy_v1: Use this for research-misconduct, university investigation, procedural case, disciplinary, appeal, committee, or administrative proceeding sources.",
    "Procedural misconduct rule: preserve the procedural backbone before narrative detail. Roles, organizational hierarchy, committees, proceeding events, deadline requirements, deadline outcomes, findings, sanctions, corrections, witness claims, advisory opinions, unresolved questions, federal notices, financial dependencies, and temporal order are distinct query surfaces.",
    "Procedural misconduct backbone-plus-detail rule: witness claims, findings, and financial rows are additive layers, not substitutes for person_role/2, org_hierarchy/3, org_head/3, committee_member/3, proceeding_event/4, deadline_requirement/4, deadline_met/4, correction/4, and before/2 when those predicates are available.",
    "Procedural misconduct role rule: every named respondent, complainant, RIO, Provost, chair, committee member, witness, general counsel, dean, department chair, federal agency, grant actor, and replacement appointee should get the profile's role/organization row when supported. Case roles such as respondent, complainant, witness, and recused_member are query-bearing roles even when the person also has an occupational title such as professor or postdoc. Emit both role types when directly stated. Do not represent a person's role only inside witness_claim/4.",
    "Procedural misconduct committee rule: committee rosters and replacements are answer-bearing facts. Preserve Inquiry, Investigation, and FSRB membership separately from findings. If a member was erroneously listed and corrected, emit the correction and the corrected roster rather than treating the erroneous roster as current truth.",
    "Procedural misconduct timeline rule: proceeding_event/4 rows are the skeleton for later deadline and chronology queries. Preserve discovery, filing, acknowledgment, scope determination, sequestration, first meetings, reports, notifications, appeal, FSRB convening, and FSRB decision when the profile supports proceeding_event/4.",
    "Procedural misconduct deadline rule: deadline_requirement/4 and deadline_met/4 are policy/compliance backbone rows. Preserve amount, unit, anchor, start date, actual date, and yes/no status. Do not answer deadline questions from finding dates alone.",
    "Procedural misconduct extension-reason rule: when an extension is requested or granted and the source states why, preserve the reason as extension_reason/2 or an equivalent detail row in addition to proceeding_event/4, deadline_requirement/4, and deadline_met/4. Do not reduce an extension to only who granted it and when.",
    "Procedural misconduct policy-surface rule: do not invent generic policy_requirement, policy_scope, or policy_rule predicates when the profile instead provides deadline_requirement/4, deadline_met/4, extension_authority/2, inquiry_minimum_size/1, investigation_minimum_size/1, is_research_misconduct/1, and not_research_misconduct/1. Map standing policy requirements onto those exact allowed predicates.",
    "Procedural misconduct organization contract rule: org_hierarchy(Parent, Child, RelationType) should use the child relation class or source-stated relation type, such as college or department, not vague verbs like contains, has_head, or parent_of. org_head(Organization, Person, Role) must use the organization as the first argument and the named person as the second argument.",
    "Procedural misconduct authority rule: inquiry-extension authority and investigation-extension authority may differ. Preserve extension_authority/2 and minimum-size predicates when the profile supports them; do not infer one authority from the other.",
    "Procedural misconduct finding/sanction rule: findings and sanctions are separate and both are backbone rows. An appeal board may uphold the finding while modifying sanctions. Preserve finding/4, finding_regarding/3, finding_detail/2, sanction/4, sanction_modified/4, sanction_upheld/4, and fsrb_rationale/1 when supported. Do not let finality, authority, or policy-effect rows replace actual finding and sanction outcome rows.",
    "Procedural misconduct Petrova-status rule: if the source states that a witness was aware of modifications but was not found to be a co-conspirator, preserve both parts as queryable finding_detail/2, finding_regarding/3, or witness_claim/4 rows. Do not collapse awareness into participation.",
    "Procedural misconduct stage-status rule: when the profile supports finality, rationale, authority, decision-effect, or status predicates, preserve them as additive queryable rows. FSRB finality, appealability, sanction-rationale facts, sanction effective timing, federal independent-review authority, and current official finding status should not be hidden only inside finding labels or witness claims, and they must not crowd out actual finding/sanction rows.",
    "Procedural misconduct conditional-policy rule: preserve FSRB and federal conditional policy rows even when the source's actual outcome followed a different branch. If the source states what happens when the FSRB overturns, upholds, or modifies a finding, emit the available deadline_requirement, fsrb_may, fsrb_decision_final, fsrb_decision_effect, federal_agency_authority, and sanction-effect rows that the profile supports.",
    "Procedural misconduct conflict-window rule: conflict-of-interest policy and corrections often determine committee validity. Preserve conflict_of_interest/4, conflict_publication/4, conflict_recusal/3, conflict_window_active/4, conflict_policy/2, conflict_policy_includes/2, acting_rio_requirement/3, and replacement deadline/minimum-size rows when supported, including corrected publication dates and active-window start/end values.",
    "Procedural misconduct federal-rule rule: source-stated agency powers and interim-report requests are policy/source records, not ordinary findings. Preserve federal_agency_authority/2, federal_notification/3, federal_request_reason/3, paper_status/3, retraction_initiated_by/2, and retraction_reason/2 when supported, especially independent federal review authority and journal-retraction-triggered interim requests.",
    "Procedural misconduct epistemic rule: witness_claim/4, advisory_opinion/4, advisory_status/2, and unresolved_question/2 are not objective findings. Preserve their status so later queries can ask what was claimed, what was advisory, and what remained unresolved.",
    "Procedural misconduct witness-language rule: if the profile supports witness_statement/4, preserve one row per witness statement with speaker, language, topic, and speaker role. Keep non-English source-language metadata queryable separately from translated witness_claim/4 content.",
    "Procedural misconduct unresolved-prior-notice rule: when the source raises an earlier disputed notice, prior complaint, deferred reporting obligation, or outside-scope question, preserve the prior_complaint_* and unresolved_question_* rows when supported instead of resolving the dispute. If unresolved_question_detail/2 is available, preserve details such as whether a prior conversation constituted notice and whether a reporting clock would have started earlier.",
    "Procedural misconduct correction rule: correction/4 and clarification/3 rows are first-class. Preserve stale value, replacement value, date/detail rows, and the current corrected fact surface when supported.",
    "Procedural misconduct federal/financial rule: grant, subgrant, equipment, depreciation, paper retraction, federal notification, and advisory fund-return rows are dependency surfaces. Preserve them separately instead of folding them into a single case summary.",
    "Procedural misconduct multilingual rule: non-English witness statements are source-owned claims. Preserve the translated claim content and speaker/source; do not treat translation as external proof.",
    "Procedural misconduct no-violation rule: if the source says every documented deadline was met, do not invent a procedural violation merely because a deadline looks close. Preserve positive deadline_met(..., yes) rows.",
    "Procedural misconduct atom rule: use one canonical atom per person, committee, grant, paper, agency, role, and date. Prefer stable given_surname person atoms when the profile's registry uses that style, and reuse the same atom across role, committee, event, witness, conflict, and finding rows.",
    "Procedural misconduct title-alias rule: honorifics and titles such as Dr, Prof, Professor, RIO, Provost, Chair, Dean, and General Counsel are roles or aliases, not person-atom prefixes. If the same person appears as Dr. Samuel Achebe and Samuel Achebe, use samuel_achebe everywhere and emit person_role(samuel_achebe, postdoc) plus person_role(samuel_achebe, complainant) when both are source-stated.",
]

from src.profile_bootstrap import (  # noqa: E402
    PROFILE_BOOTSTRAP_JSON_SCHEMA,
    PROFILE_BOOTSTRAP_REVIEW_JSON_SCHEMA,
    build_profile_bootstrap_messages,
    build_profile_bootstrap_review_messages,
    parse_profile_bootstrap_json,
    parse_profile_bootstrap_review_json,
    profile_bootstrap_allowed_predicates,
    profile_bootstrap_domain_context,
    profile_bootstrap_predicate_contracts,
    profile_bootstrap_score,
)
from src.document_intake_plan import (  # noqa: E402
    INTAKE_PLAN_JSON_SCHEMA,
    build_intake_plan_messages,
    intake_plan_context,
    parse_intake_plan_json,
)
from src.semantic_ir import (  # noqa: E402
    SemanticIRCallConfig,
    call_semantic_ir,
    semantic_ir_to_legacy_parse,
)
from src.semantic_struggle import assess_semantic_progress  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LLM-owned profile bootstrap over a raw text file.")
    parser.add_argument("--text-file", type=Path, required=True)
    parser.add_argument(
        "--expected-prolog",
        type=Path,
        default=None,
        help="Optional expected Prolog file used for structural signature comparison only.",
    )
    parser.add_argument(
        "--use-expected-signatures-as-guidance",
        action="store_true",
        help="Calibration-only mode: include expected Prolog predicate signatures in the LLM profile-bootstrap input.",
    )
    parser.add_argument(
        "--profile-registry",
        type=Path,
        default=None,
        help="Optional source/domain ontology registry used as candidate profile vocabulary, not target facts.",
    )
    parser.add_argument(
        "--use-profile-registry-direct",
        action="store_true",
        help="Use --profile-registry directly as the draft profile palette instead of asking the LLM to rediscover it.",
    )
    parser.add_argument("--domain-hint", default="")
    parser.add_argument("--backend", choices=["lmstudio"], default="lmstudio")
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.82)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--num-ctx", type=int, default=32768)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument(
        "--skip-intake-plan",
        action="store_true",
        help="Disable the LLM-owned intake_plan_v1 pre-pass.",
    )
    parser.add_argument(
        "--compile-source",
        action="store_true",
        help="After profile bootstrap, run the same raw source through Semantic IR using the draft profile.",
    )
    parser.add_argument(
        "--compile-plan-passes",
        action="store_true",
        help="When an intake plan exists, compile once per LLM-authored pass_plan item instead of one flat source compile.",
    )
    parser.add_argument(
        "--compile-flat-plus-plan-passes",
        action="store_true",
        help="Experimental: compile one broad flat pass plus focused LLM-authored pass_plan passes, then union admitted clauses.",
    )
    parser.add_argument("--max-plan-passes", type=int, default=8)
    parser.add_argument(
        "--intake-registry-context",
        action="store_true",
        help=(
            "Experimental: pass --profile-registry into the LLM intake planner as vocabulary-only context. "
            "Default is off because registry-visible planning can over-broaden dense pass plans."
        ),
    )
    parser.add_argument(
        "--focused-pass-operation-target",
        type=int,
        default=48,
        help="Prompt target for candidate_operations emitted by each focused intake-plan compile pass.",
    )
    parser.add_argument(
        "--focused-retry-operation-target",
        type=int,
        default=16,
        help="Prompt target for candidate_operations emitted by the compact retry for an unparseable focused pass.",
    )
    parser.add_argument(
        "--focused-pass-ops-schema",
        action="store_true",
        help=(
            "Experimental: focused intake-plan passes ask the LLM for source_pass_ops_v1 "
            "operations only, then wrap those proposals for the normal Semantic IR mapper."
        ),
    )
    parser.add_argument("--include-model-input", action="store_true")
    parser.add_argument(
        "--source-entity-ledger",
        action="store_true",
        help="Experimental: run an LLM-owned source_entity_ledger_v1 pass and inject it as compile context.",
    )
    parser.add_argument(
        "--review-profile",
        action="store_true",
        help="Run an LLM-owned profile review pass before optional source compilation.",
    )
    parser.add_argument(
        "--profile-review-retry",
        action="store_true",
        help="If profile review recommends retry, rerun profile bootstrap with review guidance.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    text_path = args.text_file if args.text_file.is_absolute() else (REPO_ROOT / args.text_file).resolve()
    source_text = text_path.read_text(encoding="utf-8-sig")
    expected_path = None
    expected_signatures: list[str] = []
    if args.expected_prolog:
        expected_path = args.expected_prolog if args.expected_prolog.is_absolute() else (REPO_ROOT / args.expected_prolog).resolve()
        if args.use_expected_signatures_as_guidance:
            expected_signatures = sorted(_prolog_signatures(expected_path.read_text(encoding="utf-8-sig")))
    sample = {
        "id": text_path.stem,
        "source": str(text_path),
        "domain_hint": str(args.domain_hint or "").strip(),
        "text": source_text,
        "context": [
            "Raw source file. Python has not segmented, summarized, or derived predicates from this text.",
            "The LLM bootstrap pass must propose the candidate predicate/entity surface.",
        ],
    }
    profile_registry = _load_profile_registry(args.profile_registry)
    if profile_registry:
        sample["candidate_profile_registry_v1"] = profile_registry
        sample["context"].append(
            "candidate_profile_registry_v1 is a source/domain ontology scaffold: predicate signatures, categories, "
            "and notes only. It is not a gold fact set and it does not authorize writes. Prefer these signatures when "
            "they fit the source and preserve epistemic boundaries; omit registry predicates that the source does not need."
        )
    if expected_signatures:
        sample["target_prolog_signatures_for_calibration"] = expected_signatures
        sample["context"].append(
            "Calibration-only: target_prolog_signatures_for_calibration is a human-supplied expected predicate roster. "
            "Prefer matching those signatures when they fit the source and profile design."
        )
    intake_plan: dict[str, Any] | None = None
    intake_error = ""
    intake_latency_ms = 0
    if not args.skip_intake_plan:
        intake_started = time.perf_counter()
        intake_response = _call_lmstudio_json_schema(
            base_url=str(args.base_url),
            model=str(args.model),
            messages=build_intake_plan_messages(
                source_text=source_text,
                source_name=text_path.name,
                domain_hint=str(args.domain_hint or ""),
                candidate_profile_registry=profile_registry if bool(args.intake_registry_context) else None,
            ),
            schema=INTAKE_PLAN_JSON_SCHEMA,
            schema_name="intake_plan_v1",
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=min(int(args.max_tokens), 12000),
        )
        intake_latency_ms = int((time.perf_counter() - intake_started) * 1000)
        intake_plan, intake_error = parse_intake_plan_json(str(intake_response.get("content", "")))
        if isinstance(intake_plan, dict):
            sample["intake_plan_v1"] = intake_plan
            sample["context"].append(
                "The intake_plan_v1 object is an LLM-owned document-to-logic strategy. Use it as planning guidance, not as approved facts."
            )
    started = time.perf_counter()
    messages: list[dict[str, str]] = []
    if bool(args.use_profile_registry_direct):
        if not profile_registry:
            raise ValueError("--use-profile-registry-direct requires --profile-registry")
        parsed = _profile_from_registry(profile_registry, domain_hint=str(args.domain_hint or ""))
        error = ""
        response = {"content": json.dumps(parsed, ensure_ascii=False)}
    else:
        messages = build_profile_bootstrap_messages(samples=[sample], domain_hint=str(args.domain_hint or ""))
        response = _call_lmstudio_json_schema(
            base_url=str(args.base_url),
            model=str(args.model),
            messages=messages,
            schema=PROFILE_BOOTSTRAP_JSON_SCHEMA,
            schema_name="profile_bootstrap_v1",
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=int(args.max_tokens),
        )
        parsed, error = parse_profile_bootstrap_json(str(response.get("content", "")))
    profile_retry: dict[str, Any] | None = None
    if not isinstance(parsed, dict):
        retry_sample = dict(sample)
        retry_context = list(sample.get("context", [])) if isinstance(sample.get("context"), list) else []
        retry_context.extend(
            _invalid_profile_retry_context(
                parse_error=error,
                raw_content=str(response.get("content", "")),
                max_predicates=40,
            )
        )
        retry_sample["context"] = retry_context
        retry_messages = build_profile_bootstrap_messages(samples=[retry_sample], domain_hint=str(args.domain_hint or ""))
        retry_started = time.perf_counter()
        retry_response = _call_lmstudio_json_schema(
            base_url=str(args.base_url),
            model=str(args.model),
            messages=retry_messages,
            schema=PROFILE_BOOTSTRAP_JSON_SCHEMA,
            schema_name="profile_bootstrap_v1",
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=min(int(args.max_tokens), 9000),
        )
        retry_parsed, retry_error = parse_profile_bootstrap_json(str(retry_response.get("content", "")))
        profile_retry = {
            "latency_ms": int((time.perf_counter() - retry_started) * 1000),
            "parsed_ok": isinstance(retry_parsed, dict),
            "parse_error": retry_error,
            "raw_content": str(retry_response.get("content", ""))[:20000],
        }
        if isinstance(retry_parsed, dict):
            parsed = retry_parsed
            error = retry_error
    profile_signature_roster_retry: dict[str, Any] | None = None
    if not isinstance(parsed, dict) and not bool(args.use_profile_registry_direct):
        roster_started = time.perf_counter()
        roster_response = _call_lmstudio_json_schema(
            base_url=str(args.base_url),
            model=str(args.model),
            messages=_build_profile_signature_roster_messages(
                source_text=source_text,
                source_name=text_path.name,
                domain_hint=str(args.domain_hint or ""),
                intake_plan=intake_plan,
                parse_error=error,
            ),
            schema=PROFILE_SIGNATURE_ROSTER_JSON_SCHEMA,
            schema_name="profile_signature_roster_v1",
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=min(int(args.max_tokens), 5000),
        )
        try:
            roster_parsed = json.loads(str(roster_response.get("content", "{}")))
            roster_profile = _profile_from_signature_roster(roster_parsed)
            roster_error = "" if roster_profile else "profile_signature_roster_empty"
        except Exception as exc:
            roster_parsed = {}
            roster_profile = None
            roster_error = str(exc)
        profile_signature_roster_retry = {
            "latency_ms": int((time.perf_counter() - roster_started) * 1000),
            "parsed_ok": isinstance(roster_profile, dict),
            "parse_error": roster_error,
            "raw_content": str(roster_response.get("content", ""))[:12000],
            "parsed": roster_parsed if isinstance(roster_parsed, dict) else {},
        }
        if isinstance(roster_profile, dict):
            parsed = roster_profile
            error = ""
    profile_review: dict[str, Any] | None = None
    profile_review_retry: dict[str, Any] | None = None
    if bool(args.review_profile) and isinstance(parsed, dict) and not bool(args.use_profile_registry_direct):
        profile_review = _review_profile_bootstrap(
            source_text=source_text,
            source_name=text_path.name,
            parsed_profile=parsed,
            intake_plan=intake_plan,
            args=args,
        )
        review_parsed = profile_review.get("parsed") if isinstance(profile_review.get("parsed"), dict) else {}
        should_retry = (
            bool(args.profile_review_retry)
            and isinstance(review_parsed, dict)
            and (
                review_parsed.get("coverage_ok") is False
                or str(review_parsed.get("verdict", "")).strip() in {"retry_recommended", "reject_profile"}
            )
        )
        if should_retry:
            retry_sample = dict(sample)
            retry_context = list(sample.get("context", [])) if isinstance(sample.get("context"), list) else []
            retry_context.append(
                "Profile review pass recommended one more profile-bootstrap attempt. "
                "This is LLM control-plane guidance, not approved facts or a target Prolog file."
            )
            retry_context.append(
                "Profile review retry safety: preserve source-local vocabulary. If review guidance uses a famous story, "
                "archetype, trope, or template label that is not literally present in the source, translate it into a "
                "source-local structural name before proposing profile predicates or repeated structures. Do not repeat "
                "the absent external label in risks, examples, explanations, or retry-derived notes."
            )
            for item in review_parsed.get("retry_guidance", []) if isinstance(review_parsed.get("retry_guidance"), list) else []:
                text = str(item).strip()
                if text:
                    retry_context.append(f"profile_review_retry_guidance: {text}")
            for item in review_parsed.get("missing_capabilities", []) if isinstance(review_parsed.get("missing_capabilities"), list) else []:
                if not isinstance(item, dict):
                    continue
                capability = str(item.get("capability", "")).strip()
                suggested = ", ".join(str(sig).strip() for sig in item.get("suggested_signatures", []) if str(sig).strip()) if isinstance(item.get("suggested_signatures"), list) else ""
                if capability or suggested:
                    retry_context.append(f"profile_review_missing_capability: {capability}; suggested_signatures: {suggested}")
            retry_sample["context"] = retry_context
            retry_messages = build_profile_bootstrap_messages(samples=[retry_sample], domain_hint=str(args.domain_hint or ""))
            retry_started = time.perf_counter()
            retry_response = _call_lmstudio_json_schema(
                base_url=str(args.base_url),
                model=str(args.model),
                messages=retry_messages,
                schema=PROFILE_BOOTSTRAP_JSON_SCHEMA,
                schema_name="profile_bootstrap_v1",
                timeout=int(args.timeout),
                temperature=float(args.temperature),
                top_p=float(args.top_p),
                max_tokens=int(args.max_tokens),
            )
            retry_parsed, retry_error = parse_profile_bootstrap_json(str(retry_response.get("content", "")))
            profile_review_retry = {
                "latency_ms": int((time.perf_counter() - retry_started) * 1000),
                "parsed_ok": isinstance(retry_parsed, dict),
                "parse_error": retry_error,
                "raw_content": str(retry_response.get("content", ""))[:20000],
            }
            if isinstance(retry_parsed, dict):
                parsed = retry_parsed
                error = retry_error
    score = profile_bootstrap_score(parsed)
    record: dict[str, Any] = {
        "ts": _utc_now(),
        "text_file": str(text_path),
        "domain_hint": str(args.domain_hint or ""),
        "backend": str(args.backend),
        "model": str(args.model),
        "profile_registry": str(args.profile_registry or ""),
        "profile_registry_direct": bool(args.use_profile_registry_direct),
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "parsed_ok": isinstance(parsed, dict),
        "parse_error": error,
        "score": score,
        "parsed": parsed or {},
        "raw_content": str(response.get("content", ""))[:20000],
    }
    if profile_retry is not None:
        record["profile_retry"] = profile_retry
    if profile_signature_roster_retry is not None:
        record["profile_signature_roster_retry"] = profile_signature_roster_retry
    if profile_review is not None:
        record["profile_review"] = profile_review
    if profile_review_retry is not None:
        record["profile_review_retry"] = profile_review_retry
    if not args.skip_intake_plan:
        record["intake_plan"] = {
            "parsed_ok": isinstance(intake_plan, dict),
            "parse_error": intake_error,
            "latency_ms": intake_latency_ms,
            "parsed": intake_plan or {},
        }
    if args.include_model_input:
        record["model_input"] = {"messages": messages}
    source_entity_ledger: dict[str, Any] | None = None
    source_entity_ledger_context: list[str] = []
    if bool(args.source_entity_ledger) and bool(args.compile_source) and isinstance(parsed, dict) and _should_build_source_entity_ledger(
        intake_plan=intake_plan,
        domain_hint=str(args.domain_hint or ""),
    ):
        ledger_started = time.perf_counter()
        try:
            ledger_response = _call_lmstudio_json_schema(
                base_url=str(args.base_url),
                model=str(args.model),
                messages=_build_source_entity_ledger_messages(
                    source_text=source_text,
                    source_name=text_path.name,
                    domain_hint=str(args.domain_hint or ""),
                    profile_registry=profile_registry,
                ),
                schema=SOURCE_ENTITY_LEDGER_SCHEMA,
                schema_name="source_entity_ledger_v1",
                timeout=int(args.timeout),
                temperature=float(args.temperature),
                top_p=float(args.top_p),
                max_tokens=min(int(args.max_tokens), 6000),
            )
            source_entity_ledger = json.loads(str(ledger_response.get("content", "{}")))
            record["source_entity_ledger"] = {
                "parsed_ok": isinstance(source_entity_ledger, dict),
                "parse_error": "",
                "latency_ms": int((time.perf_counter() - ledger_started) * 1000),
                "parsed": source_entity_ledger,
            }
            source_entity_ledger_context = _source_entity_ledger_context(source_entity_ledger)
        except Exception as exc:
            record["source_entity_ledger"] = {
                "parsed_ok": False,
                "parse_error": str(exc),
                "latency_ms": int((time.perf_counter() - ledger_started) * 1000),
                "parsed": {},
            }
    if bool(args.compile_source) and isinstance(parsed, dict) and bool(args.compile_flat_plus_plan_passes) and isinstance(intake_plan, dict):
        record["source_compile"] = _compile_source_flat_plus_plan_passes(
            source_text=source_text,
            parsed_profile=parsed,
            intake_plan=intake_plan,
            args=args,
            extra_context=source_entity_ledger_context,
        )
    elif bool(args.compile_source) and isinstance(parsed, dict) and bool(args.compile_plan_passes) and isinstance(intake_plan, dict):
        record["source_compile"] = _compile_source_with_plan_passes(
            source_text=source_text,
            parsed_profile=parsed,
            intake_plan=intake_plan,
            args=args,
            extra_context=source_entity_ledger_context,
        )
    elif bool(args.compile_source) and isinstance(parsed, dict):
        record["source_compile"] = _compile_source_with_draft_profile(
            source_text=source_text,
            parsed_profile=parsed,
            intake_plan=intake_plan,
            args=args,
            extra_context=source_entity_ledger_context,
        )
    if args.expected_prolog:
        record["expected_prolog"] = _compare_expected_prolog(
            expected_path=expected_path or (REPO_ROOT / args.expected_prolog).resolve(),
            parsed_profile=parsed if isinstance(parsed, dict) else {},
            source_compile=record.get("source_compile") if isinstance(record.get("source_compile"), dict) else {},
        )

    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{_slug(text_path.stem)}_{_slug(str(args.model))}"
    json_path = out_dir / f"domain_bootstrap_file_{slug}.json"
    md_path = json_path.with_suffix(".md")
    json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    _write_summary(record, md_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(
        json.dumps(
            {
                "parsed_ok": record["parsed_ok"],
                "score": score,
                "candidate_predicates": score.get("predicate_count", 0),
                "compile_admitted": (record.get("source_compile") or {}).get("admitted_count"),
                "compile_skipped": (record.get("source_compile") or {}).get("skipped_count"),
                "expected_signature_recall": (record.get("expected_prolog") or {}).get("signature_recall"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def _invalid_profile_retry_context(*, parse_error: str, raw_content: str, max_predicates: int = 40) -> list[str]:
    context = [
        (
            "Retry after invalid/truncated profile JSON: emit a compact profile with at most "
            f"{max(1, int(max_predicates))} unique predicate signatures. Do not duplicate synonymous predicate "
            "surfaces; choose one canonical predicate for each role."
        ),
        (
            "Profile retry output budget: keep entity_types, source_summary, descriptions, why fields, admission_notes, "
            "frontier cases, and self_check notes short. Complete source ingestion belongs to later Semantic IR passes."
        ),
        (
            "Profile arg-role guardrail: candidate_predicates[].args are short structural role labels only, each under "
            "32 characters. Use labels like case_id, party, role, date, status, amount, value, unit, source, or arg_1."
        ),
        (
            "Never put source examples, entity ids, entity_type_N counters, generated numeric sequences, copied prose, "
            "or alternative value lists inside candidate_predicates[].args."
        ),
    ]
    lower_raw = str(raw_content or "").casefold()
    if "entity_type_" in lower_raw or "_1_2_3_4" in lower_raw or "ref_entity_type" in lower_raw:
        context.append(
            "Previous failure signature: argument-role runaway was detected. Replace any giant role field with one "
            "compact role label such as party, entity, or arg_N; do not continue a generated counter sequence."
        )
    if str(parse_error or "").strip():
        context.append(f"Previous parse error: {str(parse_error).strip()[:240]}")
    return context


def _build_profile_signature_roster_messages(
    *,
    source_text: str,
    source_name: str,
    domain_hint: str,
    intake_plan: dict[str, Any] | None,
    parse_error: str,
) -> list[dict[str, str]]:
    payload = {
        "task": "Emit profile_signature_roster_v1 JSON only as a degraded fallback profile surface.",
        "source_name": source_name,
        "domain_hint": domain_hint,
        "raw_source_text": source_text,
        "intake_plan_v1": intake_plan or {},
        "previous_profile_parse_error": str(parse_error or "")[:240],
        "rules": [
            "This fallback proposes vocabulary only. It does not extract facts and does not authorize writes.",
            "candidate_signatures contains predicate name/arity only plus short descriptions. Do not emit args.",
            "Prefer reusable arity 2-4 predicates. Use arity 5 only when source identity, value, unit, and basis all need separate slots.",
            "Include predicates for source identity, roles, records/events, dates/deadlines/status, corrections, rule records, and explicit details when the source needs them.",
            "Keep every string short. Do not copy long source passages, entity lists, generated counters, or examples into schema slots.",
        ],
    }
    return [
        {
            "role": "system",
            "content": (
                "You produce a compact predicate-signature roster for a governed semantic compiler. "
                "You do not emit argument labels, facts, Prolog clauses, or answers. Return JSON only."
            ),
        },
        {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
    ]


def _profile_from_signature_roster(roster: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(roster, dict) or roster.get("schema_version") != "profile_signature_roster_v1":
        return None
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in roster.get("candidate_signatures", []) if isinstance(roster.get("candidate_signatures"), list) else []:
        if not isinstance(item, dict):
            continue
        signature = _normalized_signature(str(item.get("signature", "")))
        if not signature or signature in seen:
            continue
        seen.add(signature)
        arity = int(signature.rsplit("/", 1)[1])
        candidates.append(
            {
                "signature": signature,
                "args": [f"arg_{index}" for index in range(1, arity + 1)],
                "description": str(item.get("description", "")).strip()[:400],
                "why": "Recovered from compact signature-roster fallback after full profile JSON failed.",
                "admission_notes": [
                    str(note).strip()[:240]
                    for note in item.get("admission_notes", [])
                    if isinstance(item.get("admission_notes"), list) and str(note).strip()
                ][:4],
            }
        )
    if not candidates:
        return None
    entity_types = []
    for item in roster.get("entity_types", []) if isinstance(roster.get("entity_types"), list) else []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        entity_types.append(
            {
                "name": name,
                "description": str(item.get("description", "")).strip(),
                "examples": [],
            }
        )
    repeated_structures = []
    for item in roster.get("repeated_structures", []) if isinstance(roster.get("repeated_structures"), list) else []:
        if not isinstance(item, dict):
            continue
        record = _normalized_signature(str(item.get("record_predicate", "")))
        props = [
            sig
            for sig in (_normalized_signature(str(row)) for row in item.get("property_predicates", []) if isinstance(item.get("property_predicates"), list))
            if sig
        ]
        if not record:
            continue
        repeated_structures.append(
            {
                "name": str(item.get("name", "")).strip(),
                "why": "Compact signature-roster fallback repeated structure.",
                "id_strategy": "Use source-local stable ids during Semantic IR compilation.",
                "record_predicate": record,
                "property_predicates": props,
                "example_records": [],
                "admission_notes": ["Recovered from compact signature-roster fallback."],
            }
        )
    return {
        "schema_version": "profile_bootstrap_v1",
        "domain_guess": str(roster.get("domain_guess", "")).strip() or "signature_roster_fallback",
        "domain_scope": str(roster.get("domain_scope", "")).strip(),
        "confidence": float(roster.get("confidence", 0.0) or 0.0),
        "source_summary": [str(row).strip() for row in roster.get("source_summary", []) if str(row).strip()]
        if isinstance(roster.get("source_summary"), list)
        else [],
        "entity_types": entity_types,
        "candidate_predicates": candidates,
        "repeated_structures": repeated_structures,
        "likely_functional_predicates": [],
        "provenance_sensitive_predicates": [],
        "admission_risks": [str(row).strip() for row in roster.get("admission_risks", []) if str(row).strip()]
        if isinstance(roster.get("admission_risks"), list)
        else [],
        "clarification_policy": [str(row).strip() for row in roster.get("clarification_policy", []) if str(row).strip()]
        if isinstance(roster.get("clarification_policy"), list)
        else [],
        "unsafe_transformations": [str(row).strip() for row in roster.get("unsafe_transformations", []) if str(row).strip()]
        if isinstance(roster.get("unsafe_transformations"), list)
        else [],
        "starter_frontier_cases": [],
        "self_check": {
            "profile_authority": "proposal_only",
            "notes": [
                "compact_signature_roster_fallback",
                *[
                    str(row).strip()
                    for row in (roster.get("self_check", {}) if isinstance(roster.get("self_check"), dict) else {}).get("notes", [])
                    if str(row).strip()
                ][:6],
            ],
        },
    }


def _normalized_signature(value: str) -> str:
    match = re.fullmatch(r"\s*([a-z][a-z0-9_]*)\s*/\s*([1-5])\s*", str(value or "").casefold())
    if not match:
        return ""
    return f"{match.group(1)}/{match.group(2)}"


def _review_profile_bootstrap(
    *,
    source_text: str,
    source_name: str,
    parsed_profile: dict[str, Any],
    intake_plan: dict[str, Any] | None,
    args: argparse.Namespace,
) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        response = _call_lmstudio_json_schema(
            base_url=str(args.base_url),
            model=str(args.model),
            messages=build_profile_bootstrap_review_messages(
                source_text=source_text,
                source_name=source_name,
                domain_hint=str(args.domain_hint or ""),
                intake_plan=intake_plan,
                proposed_profile=parsed_profile,
            ),
            schema=PROFILE_BOOTSTRAP_REVIEW_JSON_SCHEMA,
            schema_name="profile_bootstrap_review_v1",
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=min(int(args.max_tokens), 6000),
        )
    except Exception as exc:
        return {
            "parsed_ok": False,
            "parse_error": str(exc),
            "latency_ms": int((time.perf_counter() - started) * 1000),
            "parsed": {},
        }
    parsed, error = parse_profile_bootstrap_review_json(str(response.get("content", "")))
    return {
        "parsed_ok": isinstance(parsed, dict),
        "parse_error": error,
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "parsed": parsed or {},
        "raw_content": str(response.get("content", ""))[:12000],
    }


def _load_profile_registry(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    registry_path = path if path.is_absolute() else (REPO_ROOT / path).resolve()
    parsed = json.loads(registry_path.read_text(encoding="utf-8-sig"))
    if not isinstance(parsed, dict):
        return {}
    predicates = parsed.get("predicates", [])
    compact_predicates: list[dict[str, str]] = []
    if isinstance(predicates, list):
        for item in predicates:
            if not isinstance(item, dict):
                continue
            signature = str(item.get("signature", "")).strip()
            if not signature:
                continue
            compact_predicates.append(
                {
                    "signature": signature,
                    "args": [
                        str(arg).strip()
                        for arg in item.get("args", [])
                        if isinstance(item.get("args"), list) and str(arg).strip()
                    ],
                    "category": str(item.get("category", "")).strip(),
                    "notes": str(item.get("notes", "")).strip(),
                }
            )
    return {
        "schema": str(parsed.get("schema", "")).strip(),
        "fixture": str(parsed.get("fixture", "")).strip(),
        "source": str(parsed.get("source", "")).strip(),
        "purpose": str(parsed.get("purpose", "")).strip(),
        "predicates": compact_predicates,
    }


def _profile_from_registry(registry: dict[str, Any], *, domain_hint: str = "") -> dict[str, Any]:
    predicates: list[dict[str, Any]] = []
    for item in registry.get("predicates", []) if isinstance(registry.get("predicates"), list) else []:
        if not isinstance(item, dict):
            continue
        signature = str(item.get("signature", "")).strip()
        match = re.match(r"^[a-z][a-zA-Z0-9_]*\/(\d+)$", signature)
        if not signature or not match:
            continue
        arity = int(match.group(1))
        args = [
            str(arg).strip()
            for arg in item.get("args", [])
            if isinstance(item.get("args"), list) and str(arg).strip()
        ]
        if len(args) != arity:
            args = [f"arg_{index}" for index in range(1, arity + 1)]
        predicates.append(
            {
                "signature": signature,
                "args": args,
                "description": str(item.get("notes", "")).strip() or str(item.get("category", "")).strip(),
                "why": f"registry_category={str(item.get('category', '')).strip()}",
                "admission_notes": [
                    "Registry-provided predicate candidate. Direct source support and mapper admission are still required."
                ],
            }
        )
    return {
        "schema_version": "profile_bootstrap_v1",
        "domain_guess": str(domain_hint or registry.get("fixture") or "registry_profile").strip(),
        "domain_scope": str(registry.get("purpose", "")).strip(),
        "confidence": 1.0,
        "source_summary": [
            "Profile generated directly from candidate_profile_registry_v1. The registry supplies predicate vocabulary only, not facts."
        ],
        "entity_types": [
            {"name": "entity", "description": "Registry-backed story-world entity.", "examples": []}
        ],
        "candidate_predicates": predicates,
        "repeated_structures": [],
        "likely_functional_predicates": [],
        "provenance_sensitive_predicates": [],
        "admission_risks": [
            "Registry predicates still require direct source support.",
            "A broad registry can permit semantically weak writes if the compiler is not source-faithful.",
        ],
        "clarification_policy": [],
        "unsafe_transformations": [
            "Do not treat registry examples, categories, or notes as source facts."
        ],
        "starter_frontier_cases": [],
        "self_check": {
            "profile_authority": "proposal_only",
            "notes": ["direct_registry_profile"],
        },
    }


def _compare_expected_prolog(
    *,
    expected_path: Path,
    parsed_profile: dict[str, Any],
    source_compile: dict[str, Any],
) -> dict[str, Any]:
    expected_text = expected_path.read_text(encoding="utf-8-sig")
    expected_signatures = _prolog_signatures(expected_text)
    profile_signatures = {
        str(item.get("signature", "")).strip().casefold()
        for item in parsed_profile.get("candidate_predicates", [])
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    emitted_text = "\n".join(
        [
            *[str(item) for item in source_compile.get("facts", []) if str(item).strip()],
            *[str(item) for item in source_compile.get("rules", []) if str(item).strip()],
        ]
    )
    emitted_signatures = _prolog_signatures(emitted_text)
    profile_overlap = sorted(expected_signatures & profile_signatures)
    overlap = sorted(expected_signatures & emitted_signatures)
    profile_missing = sorted(expected_signatures - profile_signatures)
    missing = sorted(expected_signatures - emitted_signatures)
    extra = sorted(emitted_signatures - expected_signatures)
    return {
        "expected_path": str(expected_path),
        "expected_signature_count": len(expected_signatures),
        "profile_signature_count": len(profile_signatures),
        "profile_overlap_signature_count": len(profile_overlap),
        "profile_signature_recall": round(len(profile_overlap) / max(1, len(expected_signatures)), 3),
        "emitted_signature_count": len(emitted_signatures),
        "overlap_signature_count": len(overlap),
        "signature_recall": round(len(overlap) / max(1, len(expected_signatures)), 3),
        "signature_precision": round(len(overlap) / max(1, len(emitted_signatures)), 3),
        "profile_overlap_signatures": profile_overlap,
        "profile_missing_signatures": profile_missing[:80],
        "overlap_signatures": overlap,
        "missing_signatures": missing[:80],
        "extra_signatures": extra[:80],
    }


def _prolog_signatures(text: str) -> set[str]:
    signatures: set[str] = set()
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("%") or line.startswith(":-"):
            continue
        head = line.split(":-", 1)[0].strip()
        match = re.match(r"^([a-z][a-zA-Z0-9_]*)\s*\((.*)\)", head)
        if not match:
            continue
        signatures.add(f"{match.group(1).casefold()}/{_prolog_arity(match.group(2))}")
    return signatures


def _prolog_arity(args_text: str) -> int:
    text = str(args_text or "").strip()
    if not text:
        return 0
    depth = 0
    quote = ""
    count = 1
    for char in text:
        if quote:
            if char == quote:
                quote = ""
            continue
        if char in ("'", '"'):
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            count += 1
    return count


def _compile_source_with_draft_profile(
    *,
    source_text: str,
    parsed_profile: dict[str, Any],
    intake_plan: dict[str, Any] | None,
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
    compact_retry: bool = True,
) -> dict[str, Any]:
    allowed_predicates = profile_bootstrap_allowed_predicates(parsed_profile)
    predicate_contracts = profile_bootstrap_predicate_contracts(parsed_profile)
    domain_context = profile_bootstrap_domain_context(parsed_profile)
    source_compiler_context = _source_compiler_context(
        intake_plan=intake_plan,
        domain_hint=str(getattr(args, "domain_hint", "") or ""),
    )
    config = SemanticIRCallConfig(
        backend="lmstudio",
        base_url=str(args.base_url),
        model=str(args.model),
        context_length=int(args.num_ctx),
        timeout=int(args.timeout),
        temperature=float(args.temperature),
        top_p=float(args.top_p),
        top_k=int(args.top_k),
        max_tokens=int(args.max_tokens),
        think_enabled=False,
        reasoning_effort="none",
    )
    plan_context = intake_plan_context(intake_plan)
    try:
        result = call_semantic_ir(
            utterance=source_text,
            config=config,
            context=[
                *plan_context,
                *source_compiler_context,
                *(extra_context or []),
                "Compile the raw source text using the draft profile proposed by profile_bootstrap_v1.",
                "Treat intake_plan_v1.pass_plan as the coverage checklist for this compile. Allocate candidate_operations across the planned passes instead of spending the whole operation budget on the first repeated structure you encounter.",
                "When pass_plan names source boundary, principles/rules, repeated records, final declarations, appeals, or pledges, emit at least one representative safe operation from each supported pass before adding extra repeated-record details.",
                "Use the breadth of the draft profile. If many allowed predicates are available, prefer a diverse skeleton that exercises distinct source/provenance, entity, claim, rule, repeated-record, declaration, and commitment predicate families over many operations using only one predicate family.",
                "Predicate contracts are binding. Preserve the exact argument order from predicate_contracts/allowed profile args. Do not swap subject/object, actor/time, recipient/type, facility/officer, or status/timestamp slots to make a fact fit. If the source supports a fact but the argument order is uncertain, skip it or note the uncertainty in self_check instead of emitting a malformed clause.",
                "For dense source compilation, entities/assertions/propositions are optional audit scaffolding. Keep them sparse or empty if they would consume output budget. Candidate_operations are the primary artifact; use normalized atoms directly in candidate_operations instead of first listing every source entity.",
                "Avoid predicate canonicalization drift. If the allowed palette contains synonymous prefixed and reusable detail predicates, such as grievance_observation_location/2 and observation_location/2, prefer the reusable detail predicate when its first argument is already the grievance/incident/record id.",
                "Use one canonical predicate surface consistently for a repeated slot. Do not mix grievance_method/2 with method/2, grievance_effect/2 with effect_claimed/2, or grievance_explanation_given/2 with explanation_given/2 unless their meanings are explicitly different in the profile contract.",
                "Do not add facts not present in the source text.",
                "If the whole source contains more safe facts than fit, preserve a balanced document skeleton: source/provenance boundary, core declaration or action, representative repeated records, and concluding commitments. Do not let one repeated list consume the whole candidate_operation budget.",
                "When a draft profile offers source-attributed claim predicates such as claim_made/3 or source_claim/3, prefer those for normative principles, rights, accusations, character judgments, and legitimacy statements that the source asserts but does not externally prove.",
                "If both a direct normative predicate and a source-attributed claim predicate are available, use the source-attributed claim predicate for rights, principles, legitimacy, and character judgments unless the direct predicate itself has a source/document argument.",
                "Preserve reporting and ledger-record acts as first-class queryable details when the draft profile supports them. If a source says someone reported, complained, witnessed, recorded, entered in a ledger, certified, or observed something, prefer reporter/2, complainant/2, reported_observation/2, ledger_entry/2, or similar profile predicates over collapsing the detail into only affected_person/2 or grievance/2.",
                "Preserve epistemic status for source-owned repeated records when the draft profile supports it. For grievances, allegations, complaints, and accusations, emit status/provenance facts such as grievance_status(Grievance, source_bound_accusation) or the profile's equivalent rather than leaving the accusation-vs-fact distinction only implicit in predicate names.",
                "When the source names a reporting actor and a role, preserve both if the palette supports it, e.g. a reporter/person predicate plus person_role/2. This is structural source fidelity, not a domain-specific language patch.",
                "When a source contrasts two ledgers or records, preserve both the individual ledger entries and the conflict relation if the palette supports them. Do not keep only the conflict wrapper if a later question may ask which ledger recorded which event.",
                "When the allowed palette contains ledger_entry plus a ledger-conflict predicate, emit ledger_entry facts for each side of the conflict before the conflict summary whenever the source identifies each ledger's content.",
                "When the allowed palette contains explanation/detail predicates, preserve explicitly given explanations as queryable facts rather than only encoding the resulting rule, separation, or violation.",
                "When the allowed palette contains witness_statement, source_statement, reported_event, review_meeting_attendee, correction_filing, or governing_bylaw predicates, treat those as high-query-value source metadata. Preserve each named statement source, each stated language or collection window, each meeting attendee, and each filing date before spending extra operations on duplicate policy summaries.",
                "For translated or multilingual witness/source statements, preserve the source-owned statement metadata even when the timeline already contains the same event. Do not drop the statement merely because an authoritative timeline fact also exists.",
                "When a source document has a witness/source-statement section and the palette contains witness_statement, emit one witness_statement row for every named statement source, not a representative subset. Preserve stated source language, collection date/window, and a compact content label.",
                "When a witness/source statement reports an event with a time, status, confirmation, or repair fact, and the palette contains reported_event or equivalent, emit a reported_event row in addition to any authoritative timeline fact. The reported row is source-attributed support, not objective truth.",
                "When the palette contains statement_detail/3 or equivalent, emit statement-detail rows for each named source's explicit explanation, mistake, belief, or misunderstanding that a later QA question could ask about. Preserve details such as 'thought until midnight', 'did not realize the 4-hour clock started from second clean reading', and 'believed 30 days was inclusive' as source-owned statement details rather than objective findings.",
                "For correction/addendum sections that state a shared filing date, emit a correction_filing or equivalent source-metadata row for every numbered correction and every addendum when the palette supports it; do not hide filing date only in correction_record authority text and do not compress multiple filings into a single combined row.",
                "For recall, impoundment, remedy, declaration, and not-fit actions, keep item, status, location, label, authority, and condition queryable as separate attributes when the palette supports them. Do not hide Dock C or a quoted label only inside a long item atom if a later question may ask for it.",
                "Do not emit source_priority, override, conflict, or authority-ranking facts unless the source explicitly ranks sources or states an override/conflict policy.",
                "When a predicate contract names an argument source, source_document, or document, bind that argument to a stable source/document id such as doc_1 or a normalized document id. Do not put the speaker, claimant, or claim subject in a source/document argument.",
                "For whole-source compilation, hard-cap any single repeated structure at 24 total candidate_operations, counting the record predicate and every property predicate. Do not exceed 6 representative records for any one repeated structure in a whole-source skeleton pass. If the source contains more records, list the omitted structure in self_check rather than emitting more operations.",
                "Emit source identity, core declaration/conclusion acts, and commitment/pledge operations before representative repeated records. A repeated structure must not crowd out the source boundary or conclusion.",
                "For a long document skeleton, aim for this mix when the profile supports it: 2-4 source/provenance operations, 2-6 source-attributed principles or rights, 12-24 operations for representative repeated records, 2-6 declaration/conclusion operations, and 2-6 commitment/pledge operations. The exact predicates must still come from the draft profile.",
                "If complete ingestion requires more operations than the schema cap, write the balanced skeleton and put segment_required_for_complete_ingestion in self_check.missing_slots/notes with the omitted section types.",
            ],
            domain_context=domain_context,
            allowed_predicates=allowed_predicates,
            predicate_contracts=predicate_contracts,
            kb_context_pack={},
            domain=f"profile_bootstrap:{parsed_profile.get('domain_guess', 'unknown')}",
            include_model_input=False,
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    ir = result.get("parsed") if isinstance(result, dict) else None
    if not isinstance(ir, dict):
        if compact_retry:
            retry_target = max(1, int(getattr(args, "focused_retry_operation_target", 32) or 32))
            return _compile_source_with_draft_profile(
                source_text=source_text,
                parsed_profile=parsed_profile,
                intake_plan=intake_plan,
                args=args,
                extra_context=[
                    *(extra_context or []),
                    "COMPACT RETRY: the previous Semantic IR response for this same planned pass was not parseable.",
                    "Return an operations-first valid semantic_ir_v1 object. Use entities=[], assertions=[], propositions=[], unsafe_implications=[] unless one tiny item is absolutely necessary for admission safety.",
                    "Retry scope is section-local: choose only the source section(s) relevant to the current pass purpose/focus and ignore the rest of the document.",
                    "The retry must not include entity catalogue rows. Set entities=[] and put all stable atoms directly in candidate_operations.",
                    "Do not enumerate an entity catalogue in the retry. Put stable normalized atoms directly in candidate_operations args.",
                    f"Emit at most {retry_target} safe candidate_operations that belong to this focused pass, plus empty truth_maintenance arrays and at most two short self_check notes.",
                    "Prioritize high-query-value details: reporting actors, complainants, ledger entries, conflicts between ledgers, affected items, locations, measurements, and rule violations.",
                    f"If the pass contains more than {retry_target} safe operations, choose the backbone rows first and put segment_required_for_complete_ingestion in self_check.missing_slots.",
                ],
                compact_retry=False,
            )
        return {
            "ok": False,
            "error": str(result.get("parse_error", "semantic_ir_parse_failed")) if isinstance(result, dict) else "semantic_ir_failed",
            "raw_content": str((result or {}).get("content", ""))[:4000] if isinstance(result, dict) else "",
        }
    mapped, warnings = semantic_ir_to_legacy_parse(
        ir,
        allowed_predicates=allowed_predicates,
        predicate_contracts=predicate_contracts,
    )
    diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
    return {
        "ok": True,
        "model_decision": ir.get("decision", ""),
        "projected_decision": diagnostics.get("projected_decision", ""),
        "admitted_count": int(diagnostics.get("admitted_count", 0) or 0),
        "skipped_count": int(diagnostics.get("skipped_count", 0) or 0),
        "warnings": warnings,
        "facts": mapped.get("facts", []),
        "rules": mapped.get("rules", []),
        "queries": mapped.get("queries", []),
        "self_check": ir.get("self_check", {}),
    }


def _compile_source_pass_ops(
    *,
    source_text: str,
    parsed_profile: dict[str, Any],
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    pass_id: str,
    purpose: str,
    focus: str,
    completion: str,
    predicates: str,
    coverage_goals: str,
    extra_context: list[str] | None = None,
    compact_retry: bool = True,
    operation_target: int | None = None,
) -> dict[str, Any]:
    """Ask the LLM for focused operation proposals, then use the normal mapper."""

    allowed_predicates = profile_bootstrap_allowed_predicates(parsed_profile)
    predicate_contracts = profile_bootstrap_predicate_contracts(parsed_profile)
    domain_context = profile_bootstrap_domain_context(parsed_profile)
    source_compiler_context = _source_compiler_context(
        intake_plan=intake_plan,
        domain_hint=str(getattr(args, "domain_hint", "") or ""),
    )
    target = max(1, int(operation_target or getattr(args, "focused_pass_operation_target", 48) or 48))
    payload = {
        "task": "Emit source_pass_ops_v1 JSON only for this source pass.",
        "authority": "proposal_only_mapper_remains_authoritative",
        "domain_hint": str(getattr(args, "domain_hint", "") or ""),
        "raw_source_text": source_text,
        "current_pass": {
            "pass_id": pass_id,
            "purpose": purpose,
            "focus": focus,
            "completion_policy": completion,
            "recommended_predicates": predicates,
            "coverage_goals": coverage_goals,
            "operation_target": target,
        },
        "allowed_predicates": allowed_predicates,
        "predicate_contracts": predicate_contracts,
        "domain_context": domain_context,
        "guidance_context": [
            *intake_plan_context(intake_plan),
            *source_compiler_context,
            *(extra_context or []),
            "This compact schema is for one bounded source pass. Follow current_pass.focus: broad skeleton passes should cover source-wide stable structure, while focused passes should not compile unrelated source sections.",
            "Emit only candidate_operations. Do not emit entities, assertions, propositions, temporal_graph, or truth_maintenance here.",
            "Use exact allowed predicate names and argument order from predicate_contracts.",
            "Put stable normalized atoms directly in candidate_operations args.",
            "Source field policy: raw_source_text is the direct source document being compiled. For candidate_operations grounded in raw_source_text, set source='direct'.",
            "Do not mark source-file facts as source='context'. The profile, registry, intake plan, ledger, and guidance_context are context guidance only; context-sourced write operations are blocked by the mapper.",
            "Use source='context' only when an operation is derived solely from supplied context rather than from raw_source_text, and expect that operation not to become durable truth.",
            "Do not add facts not present in the source text.",
            "If the pass has more support than fits, choose row-class floor operations first and list segment_required_for_complete_ingestion in self_check.missing_slots.",
        ],
    }
    response: dict[str, Any] | None = None
    try:
        response = _call_lmstudio_json_schema(
            base_url=str(args.base_url),
            model=str(args.model),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a source-pass operation compiler for a governed symbolic memory system. "
                        "You do not decide truth and you do not mutate the KB. "
                        "The supplied raw_source_text is direct evidence for this compile; context guidance is not evidence. "
                        "Emit only source_pass_ops_v1 JSON; the deterministic mapper will decide admission."
                    ),
                },
                {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
            ],
            schema=SOURCE_PASS_OPS_JSON_SCHEMA,
            schema_name="source_pass_ops_v1",
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=min(int(args.max_tokens), max(4000, min(12000, target * 220))),
        )
        parsed = json.loads(str(response.get("content", "{}")))
    except Exception as exc:
        raw_content = str((response or {}).get("content", ""))[:4000] if isinstance(response, dict) else ""
        if compact_retry:
            retry_target = max(1, int(getattr(args, "focused_retry_operation_target", 32) or 32))
            retried = _compile_source_pass_ops(
                source_text=source_text,
                parsed_profile=parsed_profile,
                intake_plan=intake_plan,
                args=args,
                pass_id=pass_id,
                purpose=purpose,
                focus=focus,
                completion=completion,
                predicates=predicates,
                coverage_goals=coverage_goals,
                extra_context=[
                    *(extra_context or []),
                    "COMPACT SOURCE_PASS_OPS RETRY: the previous focused pass response was invalid JSON or failed strict schema parsing.",
                    "Return fewer operations and prioritize the current pass's highest-query-value rows.",
                    "Do not include commentary, markdown, examples, or trailing text outside the JSON object.",
                    f"Retry operation target: at most {retry_target} candidate_operations.",
                ],
                compact_retry=False,
                operation_target=retry_target,
            )
            retried["compact_retry"] = {
                "triggered": True,
                "reason": f"source_pass_ops_failed:{str(exc)[:240]}",
                "previous_raw_content": raw_content,
            }
            return retried
        return {"ok": False, "error": f"source_pass_ops_failed:{exc}", "raw_content": raw_content}

    if not isinstance(parsed, dict) or parsed.get("schema_version") != "source_pass_ops_v1":
        if compact_retry:
            retry_target = max(1, int(getattr(args, "focused_retry_operation_target", 32) or 32))
            retried = _compile_source_pass_ops(
                source_text=source_text,
                parsed_profile=parsed_profile,
                intake_plan=intake_plan,
                args=args,
                pass_id=pass_id,
                purpose=purpose,
                focus=focus,
                completion=completion,
                predicates=predicates,
                coverage_goals=coverage_goals,
                extra_context=[
                    *(extra_context or []),
                    "COMPACT SOURCE_PASS_OPS RETRY: the previous focused pass response did not contain source_pass_ops_v1.",
                    "Return the strict source_pass_ops_v1 object only, with no additional wrapper.",
                    f"Retry operation target: at most {retry_target} candidate_operations.",
                ],
                compact_retry=False,
                operation_target=retry_target,
            )
            retried["compact_retry"] = {
                "triggered": True,
                "reason": "source_pass_ops_parse_failed",
                "previous_raw_content": str(response.get("content", ""))[:4000] if isinstance(response, dict) else "",
            }
            return retried
        return {
            "ok": False,
            "error": "source_pass_ops_parse_failed",
            "raw_content": str(response.get("content", ""))[:4000] if "response" in locals() else "",
        }
    ir = _source_pass_ops_to_semantic_ir(parsed)
    mapped, warnings = semantic_ir_to_legacy_parse(
        ir,
        allowed_predicates=allowed_predicates,
        predicate_contracts=predicate_contracts,
    )
    diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
    return {
        "ok": True,
        "mode": "source_pass_ops_v1",
        "model_decision": ir.get("decision", ""),
        "projected_decision": diagnostics.get("projected_decision", ""),
        "admitted_count": int(diagnostics.get("admitted_count", 0) or 0),
        "skipped_count": int(diagnostics.get("skipped_count", 0) or 0),
        "warnings": warnings,
        "admission_diagnostics": diagnostics,
        "facts": mapped.get("facts", []),
        "rules": mapped.get("rules", []),
        "queries": mapped.get("queries", []),
        "self_check": ir.get("self_check", {}),
        "source_pass_ops": parsed,
    }


def _source_pass_ops_to_semantic_ir(parsed: dict[str, Any]) -> dict[str, Any]:
    self_check = parsed.get("self_check") if isinstance(parsed.get("self_check"), dict) else {}
    return {
        "schema_version": "semantic_ir_v1",
        "decision": str(parsed.get("decision", "commit") or "commit"),
        "turn_type": "state_update",
        "entities": [],
        "referents": [],
        "assertions": [],
        "propositions": [],
        "unsafe_implications": [],
        "candidate_operations": parsed.get("candidate_operations", [])
        if isinstance(parsed.get("candidate_operations"), list)
        else [],
        "truth_maintenance": {
            "support_links": [],
            "conflicts": [],
            "retraction_plan": [],
            "derived_consequences": [],
        },
        "clarification_questions": [],
        "self_check": {
            "bad_commit_risk": str(self_check.get("bad_commit_risk", "low") or "low"),
            "missing_slots": self_check.get("missing_slots", [])
            if isinstance(self_check.get("missing_slots"), list)
            else [],
            "notes": self_check.get("notes", []) if isinstance(self_check.get("notes"), list) else [],
        },
    }


def _compile_source_with_plan_passes(
    *,
    source_text: str,
    parsed_profile: dict[str, Any],
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    pass_plan = intake_plan.get("pass_plan") if isinstance(intake_plan.get("pass_plan"), list) else []
    pass_records: list[dict[str, Any]] = []
    unique_facts: list[str] = []
    unique_rules: list[str] = []
    unique_queries: list[str] = []
    seen_facts: set[str] = set()
    seen_rules: set[str] = set()
    seen_queries: set[str] = set()
    max_passes = max(1, int(getattr(args, "max_plan_passes", 8) or 8))
    focused_target = max(1, int(getattr(args, "focused_pass_operation_target", 48) or 48))
    for index, item in enumerate(pass_plan[:max_passes]):
        if not isinstance(item, dict):
            continue
        pass_id = str(item.get("pass_id", f"pass_{index + 1}")).strip() or f"pass_{index + 1}"
        purpose = str(item.get("purpose", "")).strip()
        focus = str(item.get("focus", "")).strip()
        completion = str(item.get("completion_policy", "")).strip()
        coverage_goals = " | ".join(
            str(row).strip()
            for row in item.get("coverage_goals", [])
            if str(row).strip()
        ) if isinstance(item.get("coverage_goals"), list) else ""
        predicates = ", ".join(
            str(row).strip()
            for row in item.get("recommended_predicates", [])
            if str(row).strip()
        ) if isinstance(item.get("recommended_predicates"), list) else ""
        focused_context = [
            "This is focused plan-pass compilation, not a whole-source gulp.",
            *(extra_context or []),
            f"current_intake_pass_id: {pass_id}",
            f"current_intake_pass_purpose: {purpose}",
            f"current_intake_pass_focus: {focus}",
            f"current_intake_pass_completion_policy: {completion}",
            f"current_intake_pass_recommended_predicates: {predicates}",
            f"current_intake_pass_coverage_goals: {coverage_goals}",
            "For this call, emit only operations that belong to the current intake pass. Defer other source material to its own pass.",
            "Treat markdown/source headings as navigation aids. For this focused pass, mentally choose the source sections that match current_intake_pass_purpose/focus and ignore unrelated sections instead of compiling the whole document again.",
            "If a source section is clearly outside the current pass, do not emit entities, assertions, or operations from it.",
            "It is better to be complete for this pass than broadly summary-like across the entire source.",
            "Treat current_intake_pass_coverage_goals as row-class floors, not decorative notes. If the source and allowed profile support a listed row class, emit at least one safe candidate_operation for that class before adding repeated detail from any one predicate family.",
            "Keep focused pass JSON compact: reuse normalized atoms directly in candidate_operations instead of listing every named thing as an entity.",
            "For focused long-source passes, set entities=[] unless a clarification requires one tiny entity record. Do not enumerate an entity catalogue. Put stable normalized atoms directly in candidate_operations.",
            "For focused long-source passes, set assertions=[], propositions=[], unsafe_implications=[] unless needed to explain a blocked safety decision. The durable/queryable output lives in candidate_operations.",
            f"For focused pass compilation, aim for entities=[], at most {focused_target} candidate_operations, and 2 short self_check notes. If a pass has more source support than fits, choose the row-class floor operations first and mark segment_required_for_complete_ingestion.",
            "If source_entity_ledger_v1 includes object_families and this pass is about entity taxonomy, static properties, inventory, ownership, design, or source metadata, emit rows for every family member the allowed profile can represent: object/1 when available, size/2 when available, owned_by/2 or designed_for/2 when available, and initial_location/2 when directly stated. Do not stop after only the little/small member of a repeated family.",
            "For a focused narrative taxonomy/static pass, completeness means typed rows for every main character, home/place, named food, and repeated object family, plus relationship rows that make them queryable: character/kind/lives_at for cast, place/location rows for setting, object/kind/size/owned_by/designed_for for object families, and food/ingredient/occasion rows for named food when the profile supports them.",
            "If this pass is about source metadata, witness statements, review meetings, corrections, addenda, or provenance, and the allowed profile contains witness_statement, review_meeting_attendee, correction_filing, reported_event, or governing_bylaw predicates, emit those rows before broad timeline or policy recap rows.",
            "For a focused witness/source-statement pass, completeness means every named statement source gets a witness_statement/source_statement row, every statement-specific reported time/status/confirmation gets a reported_event row when supported by the palette, and every explicit explanation or misunderstanding gets a statement_detail row when supported by the palette.",
            "For a focused correction/addendum pass, completeness means each numbered correction and each addendum gets its own correction_filing row when supported by the palette.",
            "For a focused insurance/coverage-dispute role or contract pass, completeness means separate rows for every contract-scoped role, insurer/underwriter share, insured asset attribute, policy/treaty period, deductible, limit, attachment point, and dual-role capacity supported by the allowed profile. Do not replace these with entity_type summaries.",
            "For a focused insurance/coverage-dispute financial pass, completeness means rows for gross claimed position, adjusted position, deductible, net position, party share, share amount, attachment comparison, and difference when those values are stated and the profile supports them.",
            "For a focused insurance/coverage-dispute survey/evidence pass, completeness means source-attributed survey findings, measurement values, methodology/basis details, absences or no-finding statements, corrections, and dispute status where the profile supports them.",
            "For a focused insurance/coverage-dispute timeline pass, completeness means incident/correction times, notification times, cover suspension/resumption anchors, condition-of-class dates, off-hire intervals, and temporal ordering rows where supported.",
            "For a focused insurance/coverage-dispute legal/defense pass, completeness means legal citations, clause references, sanctions events, trading-warranty status, defense status, port calls, cancellations, and party positions where the profile supports them.",
            "For a focused insurance/coverage-dispute repair/salvage/P&I pass, completeness means itemized repair-cost rows, agreed/disputed cost status, salvage security versus payment status, P&I cover period/year, P&I notice requirements, and separate loss-of-hire positions where the profile supports them.",
            "For a focused insurance/coverage-dispute source-position pass, completeness means source-attributed positions from surveyors, masters, regulators, lawyers, underwriters, claim handlers, and clubs. Preserve speaker/source, issue, position/status, and detail separately; do not resolve competing accounts into one fact.",
            "For a focused insurance/coverage-dispute operational-timeline pass, completeness means every dated or timed vessel-operation, notification, regulatory, salvage, cargo, inspection, repair, movement, cover, and condition-of-class event with its source/status when supported by the palette.",
            "For a focused insurance/coverage-dispute itemized-finance pass, completeness means not just totals but claim components, agreed items, disputed items, excluded items, surveyor amounts, labor/material/testing/coating-like line items, deductibles, shares, attachment comparisons, and hypothetical calculation inputs where stated.",
            "For a focused insurance/coverage-dispute statement-census pass, completeness means every statement-like source object: speaker, role, language if stated, subject, compact content atom, and source document. Multilingual statements, master/chief-engineer reports, surveyor reports, and claim-handler letters should remain separately queryable.",
            "For a focused insurance/coverage-dispute authority/deadline pass, completeness means issuer, trigger, start anchor, deadline/window, compliance/timeliness status, retroactivity/status, and source basis for DAM/regulator/class/P&I/reinsurer/policy directives where supported.",
            "For a focused enterprise-guidance metric/priority pass, completeness means performance metrics, metric semantics, metric-boundary rows, ranked optimization targets, and priority reasons where supported.",
            "For a focused enterprise-guidance recommendation pass, completeness means recommendation, avoid-pattern, positive alternative/preference, reason, tradeoff, action_when, and debugging_tactic rows where supported. Avoid rows are not substitutes for replacement rows.",
            "For a focused enterprise-guidance guard/procedure pass, completeness means guard values, guard mechanism, guard effects, summary review questions, and procedure/checklist rows where supported.",
            "For a focused enterprise-guidance export/integration pass, completeness means separate export_rule, export_reason, preferred_export, intraday_update_rule, delta_load_pattern, and incremental_filter rows where supported.",
            "For any focused detail/specification pass, explicit source values are row-class floors: existing/proposed use, age, diameter, class, spacing, count, vote tally, adopted/rejected status, stated rationale, role/authority, item recovery, and technical requirement rows should be preserved when the allowed profile has compatible predicates.",
            "Do not let broad event or role rows crowd out small answer-bearing attributes. Numeric values, units, counts, distances, ages, votes, and named current uses are often the exact query surface.",
        ]
        if bool(getattr(args, "focused_pass_ops_schema", False)):
            compiled = _compile_source_pass_ops(
                source_text=source_text,
                parsed_profile=parsed_profile,
                intake_plan=intake_plan,
                args=args,
                pass_id=pass_id,
                purpose=purpose,
                focus=focus,
                completion=completion,
                predicates=predicates,
                coverage_goals=coverage_goals,
                extra_context=focused_context,
            )
        else:
            compiled = _compile_source_with_draft_profile(
                source_text=source_text,
                parsed_profile=parsed_profile,
                intake_plan=intake_plan,
                args=args,
                extra_context=focused_context,
            )
        compiled["pass_id"] = pass_id
        compiled["purpose"] = purpose
        compiled["focus"] = focus
        pass_records.append(compiled)
        for target, seen, values in [
            (unique_facts, seen_facts, compiled.get("facts", [])),
            (unique_rules, seen_rules, compiled.get("rules", [])),
            (unique_queries, seen_queries, compiled.get("queries", [])),
        ]:
            for value in values if isinstance(values, list) else []:
                text = str(value).strip()
                if text and text not in seen:
                    seen.add(text)
                    target.append(text)
    result = {
        "ok": all(bool(item.get("ok")) for item in pass_records) if pass_records else False,
        "mode": "intake_plan_passes",
        "pass_count": len(pass_records),
        "admitted_count": sum(int(item.get("admitted_count", 0) or 0) for item in pass_records),
        "skipped_count": sum(int(item.get("skipped_count", 0) or 0) for item in pass_records),
        "unique_fact_count": len(unique_facts),
        "unique_rule_count": len(unique_rules),
        "unique_query_count": len(unique_queries),
        "facts": unique_facts,
        "rules": unique_rules,
        "queries": unique_queries,
        "passes": pass_records,
    }
    result["surface_contribution"] = _pass_surface_contribution(pass_records)
    result["compile_health"] = _compile_health_summary(result["surface_contribution"])
    return result


def _compile_source_flat_plus_plan_passes(
    *,
    source_text: str,
    parsed_profile: dict[str, Any],
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    if bool(getattr(args, "focused_pass_ops_schema", False)):
        flat = _compile_source_pass_ops(
            source_text=source_text,
            parsed_profile=parsed_profile,
            intake_plan=intake_plan,
            args=args,
            pass_id="flat_skeleton",
            purpose="broad skeleton",
            focus="source-wide stable facts, roles, thresholds, core events, corrections",
            completion=(
                "Capture a balanced source-wide skeleton. Prefer stable facts, roles, thresholds, "
                "core events, corrections, and high-value status rows over exhaustive local detail."
            ),
            predicates="Use the most relevant allowed predicates for source-wide skeleton coverage.",
            coverage_goals=(
                "Preserve enough source-wide structure for later focused passes and QA to join against: "
                "key people/entities, rule/custom identifiers, dates, core events, corrections, and adjudication/status rows."
            ),
            extra_context=[
                *(extra_context or []),
                "This is the broad skeleton pass for a flat-plus-focused compile.",
                "Focused pass_plan calls will follow, so prefer a balanced skeleton over exhaustive local detail.",
            ],
            operation_target=max(48, int(getattr(args, "focused_pass_operation_target", 80) or 80)),
        )
    else:
        flat = _compile_source_with_draft_profile(
            source_text=source_text,
            parsed_profile=parsed_profile,
            intake_plan=intake_plan,
            args=args,
            extra_context=[
                *(extra_context or []),
                "This is the broad skeleton pass for a flat-plus-focused compile. Preserve stable source-wide facts, roles, thresholds, core events, and high-value corrections.",
                "Focused pass_plan calls will follow, so prefer a balanced skeleton over exhaustive local detail.",
            ],
        )
    focused = _compile_source_with_plan_passes(
        source_text=source_text,
        parsed_profile=parsed_profile,
        intake_plan=intake_plan,
        args=args,
        extra_context=extra_context,
    )
    unique_facts, unique_rules, unique_queries = _union_clause_lists(
        flat.get("facts", []) if isinstance(flat, dict) else [],
        focused.get("facts", []) if isinstance(focused, dict) else [],
        flat.get("rules", []) if isinstance(flat, dict) else [],
        focused.get("rules", []) if isinstance(focused, dict) else [],
        flat.get("queries", []) if isinstance(flat, dict) else [],
        focused.get("queries", []) if isinstance(focused, dict) else [],
    )
    result = {
        "ok": bool(flat.get("ok")) and bool(focused.get("ok")) if isinstance(flat, dict) and isinstance(focused, dict) else False,
        "mode": "flat_plus_intake_plan_passes",
        "pass_count": 1 + int(focused.get("pass_count", 0) or 0) if isinstance(focused, dict) else 1,
        "admitted_count": int(flat.get("admitted_count", 0) or 0) + int(focused.get("admitted_count", 0) or 0),
        "skipped_count": int(flat.get("skipped_count", 0) or 0) + int(focused.get("skipped_count", 0) or 0),
        "unique_fact_count": len(unique_facts),
        "unique_rule_count": len(unique_rules),
        "unique_query_count": len(unique_queries),
        "facts": unique_facts,
        "rules": unique_rules,
        "queries": unique_queries,
        "flat_pass": flat,
        "focused_passes": focused,
    }
    result["surface_contribution"] = _flat_plus_surface_contribution(flat=flat, focused=focused)
    result["compile_health"] = _compile_health_summary(result["surface_contribution"])
    return result


def _union_clause_lists(
    flat_facts: Any,
    focused_facts: Any,
    flat_rules: Any,
    focused_rules: Any,
    flat_queries: Any,
    focused_queries: Any,
) -> tuple[list[str], list[str], list[str]]:
    def merge(*groups: Any) -> list[str]:
        out: list[str] = []
        seen: set[str] = set()
        for values in groups:
            for value in values if isinstance(values, list) else []:
                text = str(value).strip()
                if text and text not in seen:
                    seen.add(text)
                    out.append(text)
        return out

    return (
        merge(flat_facts, focused_facts),
        merge(flat_rules, focused_rules),
        merge(flat_queries, focused_queries),
    )


def _clause_list(values: Any) -> list[str]:
    return [str(value).strip() for value in values if str(value).strip()] if isinstance(values, list) else []


def _pass_surface_contribution(
    pass_records: list[dict[str, Any]],
    *,
    initial_seen_facts: set[str] | None = None,
    initial_seen_rules: set[str] | None = None,
    initial_seen_queries: set[str] | None = None,
) -> list[dict[str, Any]]:
    seen_facts = set(initial_seen_facts or set())
    seen_rules = set(initial_seen_rules or set())
    seen_queries = set(initial_seen_queries or set())
    rows: list[dict[str, Any]] = []
    for index, record in enumerate(pass_records):
        facts = _clause_list(record.get("facts", []))
        rules = _clause_list(record.get("rules", []))
        queries = _clause_list(record.get("queries", []))
        new_facts = [item for item in facts if item not in seen_facts]
        new_rules = [item for item in rules if item not in seen_rules]
        new_queries = [item for item in queries if item not in seen_queries]
        seen_facts.update(facts)
        seen_rules.update(rules)
        seen_queries.update(queries)
        emitted_count = len(facts) + len(rules) + len(queries)
        unique_count = len(new_facts) + len(new_rules) + len(new_queries)
        admitted_count = int(record.get("admitted_count", 0) or 0)
        skipped_count = int(record.get("skipped_count", 0) or 0)
        health_flags: list[str] = []
        ok = bool(record.get("ok", True))
        if not ok:
            health_flags.append("pass_not_ok")
        if emitted_count == 0:
            health_flags.append("zero_yield")
        elif unique_count == 0:
            health_flags.append("no_unique_surface")
        elif unique_count < 3:
            health_flags.append("thin_surface")
        if skipped_count > admitted_count and skipped_count >= 8:
            health_flags.append("skip_heavy")
        rows.append(
            {
                "pass_index": index,
                "pass_id": str(record.get("pass_id", f"pass_{index + 1}")).strip() or f"pass_{index + 1}",
                "purpose": str(record.get("purpose", "")).strip(),
                "focus": str(record.get("focus", "")).strip(),
                "ok": ok,
                "admitted_count": admitted_count,
                "skipped_count": skipped_count,
                "fact_count": len(facts),
                "rule_count": len(rules),
                "query_count": len(queries),
                "unique_fact_count": len(new_facts),
                "unique_rule_count": len(new_rules),
                "unique_query_count": len(new_queries),
                "duplicate_count": max(0, emitted_count - unique_count),
                "unique_contribution_count": unique_count,
                "unique_contribution_ratio": round(unique_count / emitted_count, 3) if emitted_count else 0.0,
                "health_flags": health_flags,
            }
        )
    return rows


def _flat_plus_surface_contribution(*, flat: dict[str, Any], focused: dict[str, Any]) -> list[dict[str, Any]]:
    flat_record = {
        **flat,
        "pass_id": "flat_skeleton",
        "purpose": "broad skeleton",
        "focus": "source-wide stable facts, roles, thresholds, core events, corrections",
    }
    flat_rows = _pass_surface_contribution([flat_record])
    seen_facts = set(_clause_list(flat.get("facts", [])))
    seen_rules = set(_clause_list(flat.get("rules", [])))
    seen_queries = set(_clause_list(flat.get("queries", [])))
    focused_passes = focused.get("passes", []) if isinstance(focused.get("passes"), list) else []
    focused_rows = _pass_surface_contribution(
        [row for row in focused_passes if isinstance(row, dict)],
        initial_seen_facts=seen_facts,
        initial_seen_rules=seen_rules,
        initial_seen_queries=seen_queries,
    )
    for offset, row in enumerate(focused_rows, start=1):
        row["pass_index"] = offset
    return [*flat_rows, *focused_rows]


def _compile_health_summary(surface_contribution: list[dict[str, Any]]) -> dict[str, Any]:
    flag_counts: dict[str, int] = {}
    unhealthy_passes: list[str] = []
    unique_total = 0
    duplicate_total = 0
    for row in surface_contribution:
        unique_total += int(row.get("unique_contribution_count", 0) or 0)
        duplicate_total += int(row.get("duplicate_count", 0) or 0)
        flags = [str(flag).strip() for flag in row.get("health_flags", []) if str(flag).strip()] if isinstance(row.get("health_flags"), list) else []
        if flags:
            unhealthy_passes.append(str(row.get("pass_id", "")))
        for flag in flags:
            flag_counts[flag] = flag_counts.get(flag, 0) + 1
    semantic_progress = assess_semantic_progress(surface_contribution=surface_contribution)
    severe_flags = {"pass_not_ok", "zero_yield"}
    if any(flag_counts.get(flag, 0) for flag in severe_flags) or semantic_progress.get("zombie_risk") == "high":
        verdict = "poor"
        recommendation = "repair_compile_before_qa"
    elif flag_counts:
        verdict = "warning"
        recommendation = "run_qa_but_treat_thin_lens_results_as_diagnostic"
    else:
        verdict = "healthy"
        recommendation = "qa_run_reasonable"
    return {
        "schema_version": "compile_lens_health_v1",
        "verdict": verdict,
        "recommendation": recommendation,
        "pass_count": len(surface_contribution),
        "unhealthy_pass_count": len(unhealthy_passes),
        "unhealthy_passes": unhealthy_passes,
        "flag_counts": flag_counts,
        "unique_contribution_total": unique_total,
        "duplicate_total": duplicate_total,
        "semantic_progress": semantic_progress,
    }


def _source_compiler_context(*, intake_plan: dict[str, Any] | None, domain_hint: str = "") -> list[str]:
    """Return context modules selected from LLM-owned/source-external control data.

    This does not inspect the source prose. The branch uses either a user-supplied
    domain hint or the structured source type proposed by intake_plan_v1.
    """
    terms: list[str] = [str(domain_hint or "").casefold()]
    if isinstance(intake_plan, dict):
        boundary = intake_plan.get("source_boundary") if isinstance(intake_plan.get("source_boundary"), dict) else {}
        terms.extend(
            [
                str(boundary.get("source_type", "")).casefold(),
                str(boundary.get("epistemic_stance", "")).casefold(),
            ]
        )
        for item in intake_plan.get("pass_plan", []) if isinstance(intake_plan.get("pass_plan"), list) else []:
            if isinstance(item, dict):
                terms.extend(
                    [
                        str(item.get("purpose", "")).casefold(),
                        str(item.get("focus", "")).casefold(),
                    ]
                )
    label = " ".join(terms)
    contexts: list[str] = []
    if any(token in label for token in ["story", "narrative", "fable", "fiction", "plot"]):
        contexts.extend(NARRATIVE_SOURCE_COMPILER_CONTEXT_V1)
    if any(
        token in label
        for token in [
            "declaration",
            "proclamation",
            "manifesto",
            "petition",
            "recall",
            "independence",
            "grievance",
            "grievances",
            "accusation",
            "accusations",
        ]
    ):
        contexts.extend(DECLARATION_SOURCE_COMPILER_CONTEXT_V1)
    if any(
        token in label
        for token in [
            "charter",
            "standing rule",
            "standing rules",
            "source-stated rule",
            "source-stated rules",
            "rule ingestion",
            "rule_ingestion",
            "bylaw",
            "bylaws",
            "ordinance",
            "eligibility",
            "permission rule",
            "permission rules",
            "priority rule",
            "priority rules",
            "tax rule",
            "tax rules",
            "quarantine rule",
            "quarantine rules",
        ]
    ):
        contexts.extend(RULE_INGESTION_SOURCE_COMPILER_CONTEXT_V1)
    if any(
        token in label
        for token in [
            "policy",
            "compliance",
            "incident",
            "operations",
            "regulatory",
            "timeline",
            "municipal",
            "procedure",
            "threshold",
            "authorization",
        ]
    ):
        contexts.extend(POLICY_INCIDENT_SOURCE_COMPILER_CONTEXT_V1)
    if any(
        token in label
        for token in [
            "insurance",
            "reinsurance",
            "maritime",
            "coverage",
            "underwriter",
            "warranty",
            "salvage",
            "claim adjustment",
            "claims adjustment",
            "coverage dispute",
            "contract coverage",
        ]
    ):
        contexts.extend(INSURANCE_DISPUTE_SOURCE_COMPILER_CONTEXT_V1)
    if any(
        token in label
        for token in [
            "enterprise",
            "guidance",
            "best practice",
            "best-practice",
            "technical policy",
            "performance",
            "optimization",
            "polaris",
            "anaplan",
            "modeling",
            "model building",
        ]
    ):
        contexts.extend(ENTERPRISE_GUIDANCE_SOURCE_COMPILER_CONTEXT_V1)
    if any(
        token in label
        for token in [
            "misconduct",
            "research_integrity",
            "research integrity",
            "disciplinary",
            "university",
            "procedural",
            "proceeding",
            "committee",
        ]
    ):
        contexts.extend(PROCEDURAL_MISCONDUCT_SOURCE_COMPILER_CONTEXT_V1)
    return contexts


def _should_build_source_entity_ledger(*, intake_plan: dict[str, Any] | None, domain_hint: str = "") -> bool:
    label = f"{domain_hint} {json.dumps(intake_plan or {}, ensure_ascii=False)}".casefold()
    return any(token in label for token in ["story", "narrative", "fable", "fiction", "plot"])


def _build_source_entity_ledger_messages(
    *,
    source_text: str,
    source_name: str,
    domain_hint: str,
    profile_registry: dict[str, Any] | None,
) -> list[dict[str, str]]:
    payload = {
        "task": "Build source_entity_ledger_v1 for later governed semantic compilation.",
        "source_name": source_name,
        "domain_hint": domain_hint,
        "source_text": source_text,
        "candidate_profile_registry_v1": profile_registry or {},
        "rules": [
            "Use only the supplied source text and candidate registry. Do not import famous-story names, objects, roles, or endings.",
            "This ledger is context guidance only. It does not authorize durable KB writes.",
            "Choose canonical snake_case atoms for recurring characters, places, foods, objects, groups, and important abstract states.",
            "For repeated sized object families, list all local family members and keep atom names mutually consistent.",
            "Add compact coverage_targets for later passes: event spine, state changes, final state, speech/claims, subjective judgments, causality, rule-like norms, and clarification risks when the source contains them.",
            "Coverage targets are not facts. They are a checklist of source regions and row classes that later passes should consider under the mapper.",
            "Record alias risks when the same source thing could otherwise receive two atom names.",
        ],
    }
    return [
        {
            "role": "system",
            "content": (
                "You produce a compact source_entity_ledger_v1 JSON object for a governed symbolic compiler. "
                "You do not answer the user and you do not write facts. The ledger helps later model passes "
                "reuse canonical source-local atoms."
            ),
        },
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False, indent=2)},
    ]


def _source_entity_ledger_context(source_entity_ledger: dict[str, Any] | None) -> list[str]:
    if not isinstance(source_entity_ledger, dict):
        return []
    return [
        "source_entity_ledger_v1 is LLM-authored context guidance, not truth and not a gold fact set.",
        "Reuse source_entity_ledger_v1 canonical atom names in candidate_operations whenever the source refers to the same character, place, object, food, family, or abstract state.",
        "If the ledger has an alias note for a thing, do not emit parallel atoms for that thing in later passes. Pick the ledger atom and keep support in self_check if uncertain.",
        "If source_entity_ledger_v1 includes coverage_targets, treat them as powerless pass-coverage hints. When the current intake pass aligns with a target lens, emit source-supported rows for the target's anchor_atoms and coverage_goal if and only if the allowed profile has suitable predicates.",
        "For narrative coverage targets, event_spine should preserve event/order rows, state_change should preserve before/after state rows, final_state should preserve ending/remediation rows, speech_claim should preserve said/source-claim rows, subjective_judgment should preserve judged/evaluation rows, causality should preserve cause/effect rows, and rule_like_norm should preserve norms without inventing executable rules.",
        "Narrative coverage guidance may mention illustrative predicate names. If an illustrative or preferred predicate is not in allowed_predicates, do not reject the whole pass. Use the closest allowed predicate with a compatible contract when one exists; otherwise omit only that row class and note the omission in self_check.missing_slots.",
        "For ledger-backed narrative skeleton passes, a partial safe skeleton is better than rejecting the pass because the palette cannot express every desired row class.",
        "source_entity_ledger_v1_payload: "
        + json.dumps(source_entity_ledger, ensure_ascii=False, sort_keys=True),
    ]


def _call_lmstudio_json_schema(
    *,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    schema: dict[str, Any],
    schema_name: str,
    timeout: int,
    temperature: float,
    top_p: float,
    max_tokens: int,
    reasoning_effort: str = "none",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": schema,
            },
        },
    }
    if str(reasoning_effort or "").strip():
        payload["reasoning_effort"] = str(reasoning_effort).strip()
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc)) from exc
    choices = raw.get("choices", []) if isinstance(raw, dict) else []
    message = choices[0].get("message", {}) if choices and isinstance(choices[0], dict) else {}
    content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
    reasoning_content = str(message.get("reasoning_content", "") if isinstance(message, dict) else "").strip()
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "raw": raw,
        "content": content or reasoning_content,
    }


def _write_summary(record: dict[str, Any], path: Path) -> None:
    parsed = record.get("parsed") if isinstance(record.get("parsed"), dict) else {}
    score = record.get("score") if isinstance(record.get("score"), dict) else {}
    compile_record = record.get("source_compile") if isinstance(record.get("source_compile"), dict) else {}
    lines = [
        "# Domain Bootstrap File Run",
        "",
        f"- Source file: `{record.get('text_file', '')}`",
        f"- Backend/model: `{record.get('backend', '')}` / `{record.get('model', '')}`",
        f"- Parsed: `{record.get('parsed_ok', False)}`",
        f"- Rough score: `{score.get('rough_score', 0.0)}`",
        f"- Entity types: `{score.get('entity_type_count', 0)}`",
        f"- Candidate predicates: `{score.get('predicate_count', 0)}`",
        f"- Generic predicates: `{score.get('generic_predicate_count', 0)}`",
        f"- Repeated structures: `{score.get('repeated_structure_count', 0)}`",
        f"- Repeated-structure unknown predicate refs: `{score.get('repeated_structure_unknown_predicate_refs', [])}`",
        f"- Repeated-structure id-only record refs: `{score.get('repeated_structure_id_only_record_refs', [])}`",
        f"- Repeated-structure role mismatch refs: `{score.get('repeated_structure_role_mismatch_refs', [])}`",
        f"- Frontier unknown positive predicate refs: `{score.get('frontier_unknown_positive_predicate_refs', [])}`",
        "",
    ]
    intake = record.get("intake_plan") if isinstance(record.get("intake_plan"), dict) else {}
    if intake:
        plan = intake.get("parsed") if isinstance(intake.get("parsed"), dict) else {}
        boundary = plan.get("source_boundary") if isinstance(plan.get("source_boundary"), dict) else {}
        lines.extend(
            [
                "## Intake Plan",
                "",
                f"- Parsed: `{intake.get('parsed_ok', False)}`",
                f"- Source type: `{boundary.get('source_type', '')}`",
                f"- Epistemic stance: `{boundary.get('epistemic_stance', '')}`",
                f"- Passes: `{len(plan.get('pass_plan', [])) if isinstance(plan.get('pass_plan'), list) else 0}`",
                "",
            ]
        )
        for item in plan.get("pass_plan", []) if isinstance(plan.get("pass_plan"), list) else []:
            if isinstance(item, dict):
                lines.append(
                    f"- `{item.get('pass_id', '')}` {item.get('purpose', '')}: {item.get('focus', '')}"
                )
        lines.append("")
    review = record.get("profile_review") if isinstance(record.get("profile_review"), dict) else {}
    if review:
        parsed_review = review.get("parsed") if isinstance(review.get("parsed"), dict) else {}
        lines.extend(
            [
                "## Profile Review",
                "",
                f"- Parsed: `{review.get('parsed_ok', False)}`",
                f"- Verdict: `{parsed_review.get('verdict', '')}`",
                f"- Coverage OK: `{parsed_review.get('coverage_ok', '')}`",
                f"- Missing capabilities: `{len(parsed_review.get('missing_capabilities', [])) if isinstance(parsed_review.get('missing_capabilities'), list) else 0}`",
                "",
            ]
        )
        for item in parsed_review.get("retry_guidance", []) if isinstance(parsed_review.get("retry_guidance"), list) else []:
            text = str(item).strip()
            if text:
                lines.append(f"- Retry guidance: {text}")
        lines.append("")
    review_retry = record.get("profile_review_retry") if isinstance(record.get("profile_review_retry"), dict) else {}
    if review_retry:
        lines.extend(
            [
                "## Profile Review Retry",
                "",
                f"- Parsed: `{review_retry.get('parsed_ok', False)}`",
                f"- Parse error: `{review_retry.get('parse_error', '')}`",
                "",
            ]
        )
    lines.extend(["## Candidate Predicates", ""])
    for item in parsed.get("candidate_predicates", []) if isinstance(parsed.get("candidate_predicates"), list) else []:
        if isinstance(item, dict):
            lines.append(f"- `{item.get('signature', '')}` args={item.get('args', [])}: {item.get('description', '')}")
    if not lines[-1].startswith("- `"):
        lines.append("- none")
    lines.extend(["", "## Repeated Structures", ""])
    repeated = parsed.get("repeated_structures", []) if isinstance(parsed.get("repeated_structures"), list) else []
    if repeated:
        for item in repeated:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- `{item.get('name', '')}` record=`{item.get('record_predicate', '')}` "
                f"properties={item.get('property_predicates', [])}: {item.get('why', '')}"
            )
            examples = item.get("example_records", []) if isinstance(item.get("example_records"), list) else []
            for example in examples[:3]:
                lines.append(f"  - `{example}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Admission Risks", ""])
    risks = [str(item).strip() for item in parsed.get("admission_risks", []) if str(item).strip()] if isinstance(parsed.get("admission_risks"), list) else []
    lines.extend([f"- {item}" for item in risks] or ["- none"])
    if compile_record:
        contribution_lines = [
            "| "
            + " | ".join(
                [
                    f"`{row.get('pass_id', '')}`",
                    str(row.get("unique_contribution_count", 0)),
                    str(row.get("duplicate_count", 0)),
                    str(row.get("fact_count", 0)),
                    str(row.get("rule_count", 0)),
                    str(row.get("query_count", 0)),
                    ", ".join(str(flag) for flag in row.get("health_flags", []) if str(flag).strip()) or "ok",
                    str(row.get("purpose", "")).replace("|", "/")[:120],
                ]
            )
            + " |"
            for row in compile_record.get("surface_contribution", [])
            if isinstance(row, dict)
        ] or ["| - | 0 | 0 | 0 | 0 | 0 | - | - |"]
        lines.extend(
            [
                "",
                "## Source Compile",
                "",
                f"- OK: `{compile_record.get('ok', False)}`",
                f"- Model decision: `{compile_record.get('model_decision', '')}`",
                f"- Projected decision: `{compile_record.get('projected_decision', '')}`",
                f"- Admitted: `{compile_record.get('admitted_count', 0)}`",
                f"- Skipped: `{compile_record.get('skipped_count', 0)}`",
                f"- Lens health: `{(compile_record.get('compile_health') or {}).get('verdict', '')}`",
                f"- Lens health recommendation: `{(compile_record.get('compile_health') or {}).get('recommendation', '')}`",
                f"- Semantic progress risk: `{(((compile_record.get('compile_health') or {}).get('semantic_progress') or {}).get('zombie_risk', ''))}`",
                f"- Semantic progress action: `{(((compile_record.get('compile_health') or {}).get('semantic_progress') or {}).get('recommended_action', ''))}`",
                "",
                "### Surface Contribution",
                "",
                "| Pass | Unique | Duplicates | Facts | Rules | Queries | Health | Purpose |",
                "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
                *contribution_lines,
                "",
                "### Facts",
                "",
                "```prolog",
                *[str(item) for item in compile_record.get("facts", [])],
                "```",
                "",
                "### Rules",
                "",
                "```prolog",
                *[str(item) for item in compile_record.get("rules", [])],
                "```",
            ]
        )
    expected = record.get("expected_prolog") if isinstance(record.get("expected_prolog"), dict) else {}
    if expected:
        lines.extend(
            [
                "",
                "## Expected Prolog Signature Comparison",
                "",
                f"- Expected: `{expected.get('expected_path', '')}`",
                f"- Expected signatures: `{expected.get('expected_signature_count', 0)}`",
                f"- Profile candidate signatures: `{expected.get('profile_signature_count', 0)}`",
                f"- Profile overlap signatures: `{expected.get('profile_overlap_signature_count', 0)}`",
                f"- Profile signature recall: `{expected.get('profile_signature_recall', 0.0)}`",
                f"- Emitted signatures: `{expected.get('emitted_signature_count', 0)}`",
                f"- Overlap signatures: `{expected.get('overlap_signature_count', 0)}`",
                f"- Signature recall: `{expected.get('signature_recall', 0.0)}`",
                f"- Signature precision: `{expected.get('signature_precision', 0.0)}`",
                "",
                "### Overlap",
                "",
                "```text",
                "\n".join(expected.get("overlap_signatures", [])),
                "```",
                "",
                "### Profile Overlap",
                "",
                "```text",
                "\n".join(expected.get("profile_overlap_signatures", [])),
                "```",
                "",
                "### Missing From Profile",
                "",
                "```text",
                "\n".join(expected.get("profile_missing_signatures", [])),
                "```",
                "",
                "### Missing From Emitted",
                "",
                "```text",
                "\n".join(expected.get("missing_signatures", [])),
                "```",
                "",
                "### Extra In Emitted",
                "",
                "```text",
                "\n".join(expected.get("extra_signatures", [])),
                "```",
            ]
        )
    lines.extend(["", "## Full Profile JSON", "", "```json", json.dumps(parsed, ensure_ascii=False, indent=2, sort_keys=True), "```", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slug(value: str) -> str:
    import re

    text = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip()).strip("-").lower()
    return text[:60] or "run"


if __name__ == "__main__":
    raise SystemExit(main())

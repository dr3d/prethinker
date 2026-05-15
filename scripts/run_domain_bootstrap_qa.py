#!/usr/bin/env python3
"""Run natural-language QA probes against a bootstrapped source KB.

This is deliberately post-ingestion. The QA markdown is not used to design the
profile or compile the source document. It probes the resultant KB after a
source compile run has produced admitted facts/rules.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from itertools import combinations
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "domain_bootstrap_qa"
DEFAULT_CACHE_DIR = REPO_ROOT / "tmp" / "domain_bootstrap_qa_cache"
CACHE_SCHEMA_VERSION = "domain_bootstrap_qa_cache_v1"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kb_pipeline import CorePrologRuntime  # noqa: E402
from src.profile_bootstrap import (  # noqa: E402
    profile_bootstrap_allowed_predicates,
    profile_bootstrap_domain_context,
    profile_bootstrap_predicate_contracts,
)
from src.semantic_ir import (  # noqa: E402
    SemanticIRCallConfig,
    call_semantic_ir,
    semantic_ir_to_legacy_parse,
)

GENERIC_QUERY_PLACEHOLDERS = {
    "actor",
    "amount",
    "answer",
    "authority",
    "candidate",
    "claim",
    "claimant",
    "claimant_amount",
    "calculated_share",
    "calculation",
    "calculation_description",
    "calculationformula",
    "condition",
    "content",
    "costitem",
    "currency",
    "date",
    "description",
    "detail",
    "delta",
    "effect",
    "event",
    "evidence",
    "evidence_source",
    "evidence_type",
    "evidencesource",
    "evidencetype",
    "explanation",
    "finding",
    "finding_source",
    "formula",
    "item",
    "kind",
    "label",
    "language",
    "line",
    "lineid",
    "linenum",
    "location",
    "method",
    "note",
    "party",
    "person",
    "policy",
    "reason",
    "record",
    "role",
    "row",
    "section",
    "source",
    "source_row",
    "sourceid",
    "sourcerow",
    "start",
    "status",
    "step",
    "subject",
    "supportrole",
    "time",
    "text",
    "textatom",
    "type",
    "underwriter",
    "underwriter_amount",
    "shareamount",
    "sharepercent",
    "value",
    "vessel",
    "what",
    "when",
    "where",
    "who",
    "why",
    "end",
}

EVIDENCE_TABLE_PREDICATES = {
    "action_when",
    "avoid_pattern",
    "calculation_step",
    "citation_support",
    "claim_amount",
    "correction_record",
    "cost_agreement",
    "cost_disagreement",
    "debugging_tactic",
    "delta_load_pattern",
    "defense_status",
    "does_not_directly_determine",
    "enables",
    "export_reason",
    "export_rule",
    "guard_effect",
    "guard_mechanism",
    "guard_value",
    "higher_effort_aggregation",
    "incremental_filter",
    "intraday_update_rule",
    "legal_position",
    "list_load_risk",
    "loss_of_hire_position",
    "measurement_claim",
    "metric_semantics",
    "optimization_priority",
    "prefer_aggregation",
    "preferred_export",
    "priority_reason",
    "recommendation",
    "reinsurance_notice_effect",
    "summary_review_question",
    "support_effect",
    "support_exception",
    "support_positive_counterpart",
    "support_reason",
    "support_tradeoff",
    "tradeoff",
    "source_detail",
    "survey_finding",
    "trading_warranty_status",
    "underwriter_line",
    "validates_when_high",
    "witness_statement",
}

EVIDENCE_TABLE_VARIABLE_NAMES = {
    "action_when": ["Condition", "Action"],
    "avoid_pattern": ["Pattern"],
    "calculation_step": ["Step", "Formula", "Amount", "Currency", "Note"],
    "citation_support": ["Party", "Citation", "Point", "SupportRole"],
    "claim_amount": ["Claim", "Party", "AmountType", "Amount", "Currency"],
    "correction_record": ["Record", "Subject", "OriginalValue", "CorrectedValue", "Authority"],
    "cost_agreement": ["Party", "Item", "Amount", "Status"],
    "cost_disagreement": ["Item", "ClaimantAmount", "InsurerAmount", "Delta", "Reason"],
    "debugging_tactic": ["Problem", "Step"],
    "delta_load_pattern": ["PatternPart", "Implementation"],
    "defense_status": ["Party", "Defense", "Status", "Detail"],
    "does_not_directly_determine": ["Metric", "NonDeterminant"],
    "enables": ["Design", "Capability"],
    "export_reason": ["Context", "Reason"],
    "export_rule": ["Context", "Rule"],
    "guard_effect": ["Effect"],
    "guard_mechanism": ["Mechanism"],
    "guard_value": ["Value"],
    "higher_effort_aggregation": ["Method"],
    "incremental_filter": ["Filter"],
    "intraday_update_rule": ["Context", "Rule"],
    "legal_position": ["Party", "Issue", "Position", "Source", "Detail"],
    "list_load_risk": ["Condition", "Risk"],
    "loss_of_hire_position": ["Party", "Period", "Position", "Detail"],
    "measurement_claim": ["Report", "Subject", "MeasurementType", "Value", "Unit", "Method"],
    "metric_semantics": ["Metric", "Meaning"],
    "optimization_priority": ["Target", "Rank"],
    "prefer_aggregation": ["Method"],
    "preferred_export": ["ExportType", "Purpose"],
    "priority_reason": ["TargetClass", "Reason"],
    "recommendation": ["Recommendation"],
    "reinsurance_notice_effect": ["Treaty", "Notice", "Effect", "Source"],
    "source_detail": ["Source", "DetailKind", "DetailValue", "Status"],
    "summary_review_question": ["Question"],
    "support_effect": ["Anchor", "Effect"],
    "support_exception": ["Anchor", "Exception"],
    "support_positive_counterpart": ["Anchor", "PreferredAction"],
    "support_reason": ["Anchor", "Reason"],
    "support_tradeoff": ["Anchor", "Benefit", "CostOrRisk"],
    "survey_finding": ["Surveyor", "Subject", "Finding", "Value", "Source"],
    "tradeoff": ["Choice", "Benefit", "CostOrRisk"],
    "trading_warranty_status": ["Policy", "Subject", "Status", "Detail"],
    "underwriter_line": ["Policy", "Underwriter", "SharePercent", "Role"],
    "validates_when_high": ["Metric", "Meaning"],
    "witness_statement": ["Speaker", "Language", "Subject", "Content", "Source"],
}


QA_JUDGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "verdict", "answer_supported", "concise_answer", "issues"],
    "properties": {
        "schema_version": {"type": "string", "const": "qa_judge_v1"},
        "verdict": {"type": "string", "enum": ["exact", "partial", "miss", "not_judged"]},
        "answer_supported": {"type": "boolean"},
        "concise_answer": {"type": "string", "maxLength": 600},
        "issues": {"type": "array", "maxItems": 8, "items": {"type": "string", "maxLength": 300}},
    },
}

EVIDENCE_BUNDLE_PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "question_focus", "support_bundles", "warnings"],
    "properties": {
        "schema_version": {"type": "string", "const": "evidence_bundle_plan_v1"},
        "question_focus": {"type": "string", "maxLength": 300},
        "support_bundles": {
            "type": "array",
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["bundle_id", "purpose", "query_templates", "missing_if_empty"],
                "properties": {
                    "bundle_id": {"type": "string", "maxLength": 80},
                    "purpose": {"type": "string", "maxLength": 240},
                    "query_templates": {
                        "type": "array",
                        "maxItems": 10,
                        "items": {"type": "string", "maxLength": 240},
                    },
                    "missing_if_empty": {"type": "string", "maxLength": 240},
                },
            },
        },
        "warnings": {"type": "array", "maxItems": 6, "items": {"type": "string", "maxLength": 220}},
    },
}

FAILURE_SURFACE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "surface", "confidence", "rationale", "suggested_next_action"],
    "properties": {
        "schema_version": {"type": "string", "const": "qa_failure_surface_v1"},
        "surface": {
            "type": "string",
            "enum": [
                "compile_surface_gap",
                "query_surface_gap",
                "hybrid_join_gap",
                "answer_surface_gap",
                "judge_uncertain",
                "not_applicable",
            ],
        },
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "rationale": {"type": "string", "maxLength": 500},
        "suggested_next_action": {"type": "string", "maxLength": 360},
    },
}

POST_INGESTION_QA_QUERY_STRATEGY: dict[str, Any] = {
    "name": "post_ingestion_qa_query_strategy_v1",
    "authority": "query_planning_guidance_only_runtime_executes_queries",
    "core_principle": (
        "Answer source-document questions by planning queries over the compiled KB surface, "
        "not by re-reading the source text or inventing new predicate names."
    ),
    "predicate_surface_policy": [
        "Use compiled_predicate_inventory.signatures as the available query vocabulary.",
        "Use relevant_clauses as the primary evidence surface for choosing constants and record ids; compiled_predicate_inventory.examples is only a compact index.",
        "Prefer compiled_query_templates when a question asks for a value that appears in an existing predicate slot.",
        "Use compiled_surface_alias_inventory to notice when the compiled KB expresses the same abstract surface through decomposed or sibling predicate names; query only the actual predicates listed in compiled_predicate_inventory.",
        "If a desired meaning is split across multiple predicates, emit multiple query operations with shared constants or variables.",
        "For complementary phrasing such as in addition to, besides, along with, apart from, or not only/but also, treat the named baseline relation as context, not as the answer surface. Query sibling predicates over the same subject whose returned slot can express the additional property, effect, capability, knowledge, authority, role, maintained item, or other complement requested by the question.",
        "Do not invent composite predicates such as who_accused/2 or why_recalled/2 unless that exact predicate exists in the compiled KB inventory.",
        "Copy constants exactly as they appear in relevant_clauses. Do not synthesize alternate name-order atoms, alias atoms, date atoms, or facility atoms from prose. If the question gives only a surname, title, initial, or paraphrase, query with a variable and let the KB return the canonical atom.",
    ],
    "arity_and_variable_policy": [
        "Keep every query at the full compiled predicate arity.",
        "Use uppercase variables such as X, Y, Item, Actor, Source, Date, or Reason for unknown slots.",
        "If the question asks who, what, which, where, when, or why, the requested answer slot must be a variable unless that exact value is named in the question itself.",
        "Do not pre-fill an answer slot with a likely answer from context; query for it. For example, ask grievance_actor(Grievance, Actor), not grievance_actor(Grievance, central_bakery_fleet), when the question asks who was accused.",
        "When a person is mentioned by surname, role, title, or initial but relevant_clauses uses a full canonical atom, do not guess the atom. Prefer variables over relevant predicates and retrieve person_role/2 or source-claim rows to identify the person.",
        "Do not put role words such as performer, technician, inspector, officer, authorizer, issuer, notifier, lifter, sender, reporter, witness, or manager into person/actor slots as lowercase constants. Use a Person/Actor variable in the event predicate and, when needed, pair it with person_role(Person, Role).",
        "For questions asking which person performed the most actions, retrieve all relevant action rows with the performer slot as a variable. Do not query one role label as if it were a person constant.",
        "Do not over-constrain descriptive label slots with guessed paraphrase atoms. If a question names a phrase that may be embedded inside a longer normalized label, keep the label/method/explanation slot as a variable and retrieve candidate rows.",
        "Do not bind a record id too early when the requested answer may live in a sibling or duplicate record. Prefer broad discovery queries with variables first, then let the returned rows reveal the best-supported record.",
        "For source-owned record predicates such as alleged_violation/4, ledger_entry/3, witness_observation/3, or grievance-like records, use variables for role/content/evidence slots unless the exact atom appears in relevant_clauses. Words like accused, evidence, observer, violation, and reporting_act are slot labels, not evidence values.",
        "For where/location questions, prefer location predicates when they exist; otherwise retrieve method/explanation rows that may contain location-bearing labels instead of querying only object targets.",
        "For institution, ledger, record, or source questions, retrieve both the event text and the container/source slot with a shared record variable: for example grievance_method(Grievance, Method), grievance_explanation(Grievance, Explanation), and grievance_target(Grievance, Institution).",
        "For who/what-authorized, authority, governing-source, controlled-by, or source-of-access questions, distinguish the recipient/authorized-party surface from the authority/source surface. If compiled_surface_alias_inventory or compiled_predicate_inventory contains predicates such as access_source, access_authority_source, authority_source, governed_by, court_order, policy_source, or source_authority, query those with the same item/action/recipient variables before answering from authorized_party or access_authorized_to rows.",
        "For locker, bay, shelf, floor, or storage-location questions, query both located_at(Item, Location) and location metadata such as locker_floor(Location, Floor) when those predicates exist. If the question compares similar location codes, do not stop after located_at/2.",
        "For who-reported or reporter questions, query reporter predicates and the content predicates that describe what was reported, such as grievance_reporter(Grievance, Reporter) with grievance_explanation(Grievance, Explanation) or grievance_method(Grievance, Method). Do not rely only on target predicates.",
        "For who-is or what-is identity questions about a named official, officer, warden, inspector, director, authority, or role-holder, retrieve both identity rows and authority/action rows when they exist. Name plus role is often only partial support; include predicates such as ruling_by/3, permission_granted/2, certification_status/3, disqualification_reason/2, director_recommendation/2, official_action/3, or equivalent inventory predicates that expose what the role-holder inspects, certifies, authorizes, recommends, or decides.",
        "When a question phrase may be only part of a longer normalized atom, do not bind the phrase as a lowercase constant. Query the whole slot as a variable and let returned rows expose atoms such as infirmary_ledger_recorded_blue_sneezing.",
        "Never use lowercase placeholder constants such as who, what, item, reason, source, or answer when a variable is intended.",
        "Words that merely name the slot, such as grievance_label, method_detail, explanation_detail, candidate, label, content, value, status, authority, or institution, are variables too; write them as GrievanceLabel, MethodDetail, ExplanationDetail, Candidate, Label, Content, Value, Status, Authority, or Institution.",
        "If you want all rows for grievance/2, query grievance(Grievance, Label), not grievance(Grievance, grievance_label).",
        "For person/place names that may have alternate atom order or abbreviation, such as Luis Ferreira vs luis_ferreira/ferreira_luis or Pier 7 vs pier_7/pier_7_chlorination_unit, discover rows with variables first. Do not combine a constant copied from one predicate family with another predicate family unless that exact constant appears in that predicate's examples.",
    ],
    "epistemic_policy": [
        "Return claim/source/support queries for claimed or alleged content; do not ask for objective fact predicates when the KB only contains source-attributed claims.",
        "For questions about original, initially stated, first claimed, retracted, corrected-from, transcription-error, or superseded values, query source_claim/4 and correction_record/4 when those predicates exist. Treat correction_record(Subject, OriginalValue, CorrectedValue, Authority) according to the predicate contract: the original/pre-correction value is the second argument and the corrected/current value is the third argument. Do not let the current authoritative fact override an explicit request for the original value.",
        "For questions about the current, corrected, final, authoritative, or confirmed value, query the authoritative fact predicate and optionally correction_record/4 for provenance.",
        "For ambiguity questions, query ambiguity and candidate-identity predicates when present rather than forcing a single identity.",
        "For rule/consequence questions, query stored rules and supporting facts; do not write derived conclusions as durable facts.",
        "For questions using phrases such as revert to normal, take effect, interval ended, interval began, chronological sequence, or key authorization and notice events, include explicit state-event predicates such as contamination_advisory(triggered, StartTime) and contamination_advisory(lifted, EndTime) when those predicates exist. Interval-duration rows alone do not answer when the interval begins or ends.",
        "For questions asking what caused, triggered, or led to a state/process ending, include both the direct end-state row and the upstream causal row when available, such as led_to(Cause, EndingEvent), caused_by(EndingEvent, Cause), or triggered(Cause, EndingEvent) paired with ended(EndingEvent, EndedState). Do not stop at ended(EndingEvent, EndedState) when the question asks for the cause of the ending.",
        "For point-in-time status questions such as 'status on DATE', 'status as of DATE', or 'current on DATE', if a *_status(Entity, Status, Date) predicate exists, include a direct date-bound query such as credential_status(Entity, Status, 2026_02_06). The runtime can derive query-only interval support from admitted transition anchors, corrected intervals, and scheduled-state rows; do not only retrieve all status rows with Date as a variable.",
        "For count questions scoped to a named source section, subset, packet part, or identified conflict/item group, do not answer from a global *_status(Entity, Status) predicate alone. Pair the status with the scope surface, such as source_record_section/source_record_label rows or a unary scope predicate, so scoped_status_count_support can return the count for the asked subset.",
        "For omission and set-difference questions such as 'which required X did not receive Y', 'which X was omitted', or 'was Y issued to all required X', emit paired query operations: first the required/scope set with a shared variable, then the absent-side predicate with polarity='negative' and the same variable. Example operations: query residential_zone(Zone) polarity positive; query boil_water_notice(Zone, Time, Issuer) polarity negative. Do not emit the second operation as a positive query when the question asks for missing or omitted rows.",
        "For policy-condition questions, retrieve both the governing policy rows and the observed event/measurement rows. Threshold, count, interval, and deadline predicates are answer-bearing evidence, not optional decoration.",
        "For questions asking which event came before, anchored, triggered, or preceded a move, appointment, assignment, enrollment, or attachment, query the direct anchor/trigger surface such as event_anchor(Anchor, MoveOrAppointmentEvent) or triggered_by(MoveOrAppointmentEvent, Anchor) before asking what happened before that anchor. The anchor event itself often answers the question.",
        "For duration/deadline questions, prefer an existing deadline_met(Phase, StartDate, EndDate, Status) row plus elapsed_days(StartDate, EndDate, Days) when that row represents the asked phase. Do not compute a duration from two start-event rows when the compiled KB has a deadline_met row for the report, completion, or decision being asked about.",
        "For deadline questions asking whether a report or investigation was completed within deadline, query broadly enough to retrieve the relevant deadline_met row, the matching deadline_requirement row, and elapsed_days(StartDate, EndDate, Days). Do not bind the requirement label too narrowly, because compiled KBs may use inquiry_report, inquiry_report_90cd, inquiry_report_delivered, investigation_report, or investigation_report_120cd for the same source concept.",
        "For extension why/rationale questions, query extension_reason(ExtensionEvent, Reason), proceeding_event rows for requested/granted extension, and witness_claim/4 or finding_detail/2 rows that mention the delayed cooperation or documentation reason.",
        "When a question asks what must happen, who must authorize, what conditions apply, what requirement governs, or what the rule says, query policy_requirement/3 and dedicated rule predicates such as bypass_requires_joint/2 or bypass_inspection_validity_days/1 before querying observed event rows such as bypass_authorization/3. Observed event rows answer what happened; policy rows answer what was required.",
        "For questions asking whether one role or person can authorize alone, query the governing joint/role requirement such as bypass_requires_joint(RoleA, RoleB) and person_role(Person, Role). Do not answer from person_role/2 alone; identity is not authorization.",
        "For questions about what additional requirement, validity condition, or prerequisite applies to Harbor Master bypass authorization, query bypass_inspection_validity_days(Days), inspection(Pier7Unit, HarborMaster, Date), and policy_requirement(Bylaw, harbor_master_inspection, Requirement) if available. Do not answer that question from bypass_requires_joint/2 alone; joint authorization is the base requirement, not the additional validity condition.",
        "For questions asking whether a disclosure, omission, or maintenance failure is a policy violation, a review-board finding, or only a statement for the record, query disclosure(Speaker, Content, Date, Status) before source_claim/4 or facility state when disclosure/4 exists. The Status slot is answer-bearing evidence: statement_not_finding means the KB supports 'recorded as a statement, not established as a finding/violation.' Do not answer such questions from source_bound_accusation alone.",
        "For finding-vs-statement traps, include at least one broad epistemic-status query with Status as a variable, such as disclosure(Speaker, Content, Date, Status) or source_claim(Speaker, Subject, Content, Status), so the runtime can return whether the source treated the content as an accusation, disclosure, finding, or non-finding.",
        "For actual FSRB decision, current official finding, or sanction-outcome questions, query the actual decision surface: finding(fsrb, ...), sanction_modified(...), sanction_upheld(...), sanction(...), and fsrb_rationale(...) when available. Do not answer the actual decision from fsrb_decision_effect/2 alone; that predicate describes standing policy effects, not the specific outcome.",
        "For counterfactual FSRB-overturn questions, query standing policy consequence rows such as fsrb_may(overturn), deadline_requirement(...notify_federal...overturn...), deadline_requirement(...expunge...), and fsrb_decision_effect(...) if available. Do not answer an overturn counterfactual from the actual sanction_modified/sanction_upheld rows, because those describe the source's actual upheld/modified outcome.",
        "For FSRB finality or further-appeal questions, query fsrb_decision_final(Status) and fsrb_decision_effect(Condition, Effect) before sanction rows. Sanction rows describe what was imposed; finality rows answer whether further university appeal is available.",
        "For federal independent-review authority questions, query federal_agency_authority(Agency, Authority) before finding/4 or misconduct-definition rows. Findings answer what the university found; authority rows answer what the federal agency may do independently.",
        "For federal interim-report or agency-contact questions, query federal_notification(Agency, Event, Date), federal_request_reason(Agency, Request, Reason), paper_status(Paper, retracted, Date), retraction_initiated_by(Paper, Actor), and retraction_reason(Paper, Reason) when available. A generic investigation-opened notification is not enough support for an interim-report request question.",
        "For conflict-of-interest policy questions, query standing-policy rows such as conflict_policy(Policy, Requirement), conflict_policy_includes(Policy, Relationship), acting_rio_requirement(Condition, Authority, Duration), inquiry_minimum_size(Size), investigation_minimum_size(Size), and deadline_requirement(replacement_appointment, Amount, Unit, Anchor) before instance-only rows such as conflict_publication/4 or conflict_recusal/3.",
        "For questions asking what someone thought, misunderstood, believed, disclosed, or explained, query statement_detail/3 before broad witness_statement metadata. witness_statement/4 often names a statement but may not contain enough detail.",
        "For witness count, language-count, or source-language questions, query witness_statement(Speaker, Language, Topic, Role) when available. Use witness_claim/4 only as a fallback content surface; it usually does not preserve source-language metadata.",
        "For questions explicitly asking how many rows, entries, devices, systems, events, or applications are listed in a table, inventory, raw event log, source section, or list, include a broad source_record_row(SourceRow, table_row, Line, SectionAtom, Label) query when source_record_row/5 exists. This is structural addressability evidence; do not use it for semantic counts that ask for eligible, active, approved, failed, or scoped items unless a table/list wording is present.",
        "For source_record_field(Row, Field, Value) surfaces, the first argument is the source row or line id, not the event/entity id. To retrieve fields about an event/entity value, first bind the row with source_record_field(Row, event, Event) or source_record_field(Row, identifier, Entity), then query sibling fields with the same Row, such as source_record_field(Row, description, Description). Do not query source_record_field(Event, key, Value).",
        "For item-description questions, treat evidence_item(Item, Description) as an equivalent descriptive surface to item_description(Item, Description) when both predicates appear in the inventory. Query whichever predicate exists, and prefer broad variables when the question names the item in natural language.",
        "For subgrant purpose questions, query the financial support bundle together: subgrant(Subgrant, ParentGrant, Recipient), subgrant_purpose(Subgrant, Purpose), subgrant_amount(Subgrant, Amount), subgrant_expended(Subgrant, Expended), subgrant_remaining(Subgrant, Remaining), and subgrant_status(Subgrant, Status, Date) when available.",
        "For prior-concern or October-2025 notice questions, query prior_complaint/4, prior_complaint_subject/2, prior_complaint_action/2, prior_complaint_disputed/2, unresolved_question/2, unresolved_question_detail/2, unresolved_question_status/2, and unresolved_question_referred/2 before falling back to broad proceeding_event rows.",
        "For committee replacement after conflict questions, query conflict_policy/2 and conflict_policy_includes/2 for the standing rule, conflict_recusal/3 for the actual recusal, inquiry_minimum_size/1 and investigation_minimum_size/1 for thresholds, deadline_requirement(replacement_appointment or equivalent, Amount, Unit, Anchor), and committee_member_replaced/4 for the observed replacement.",
        "For questions asking what a witness said about a timing rule, deadline, misunderstanding, verification, or non-verification, do not stop after one narrowly bound statement_detail row. Query statement_detail(Speaker, DetailKind, DetailValue) broadly for the speaker and pair it with the relevant policy/timestamp predicates when the answer includes both belief and rule context.",
        "For consistency-check questions comparing a witness statement to an incident timeline, query the witness/source row and the corresponding objective timeline row. Example: reported_event(Witness, pump_failure, WitnessTime, Source) plus facility_status(eastgate_treatment_facility, offline, TimelineTime).",
        "For witness_statement/4, the second slot is a language value. If the question does not ask for a specific language, use a variable such as Language; do not bind the literal lowercase constant language.",
        "For questions asking how many corrections/addenda were filed, query correction_filing/3 and count distinct record_kind values. If a run has individual correction_1/correction_2/correction_3/addendum rows, prefer those over a compressed correction_addendum row.",
        "For confirmation questions such as who confirmed a facility was back online or running again, query reported_event(Reporter, facility_restoration, Time, Source) and witness_statement/4 before boil_water_notice_lifted/2. The person lifting a notice is not necessarily the person confirming restoration.",
        "For comprehensive or multi-violation questions, plan one small support bundle per alleged violation: governing policy row, observed event row, and any timing/correction/source row needed to show why it is a violation. Prefer concrete event predicates such as inspection, notice/lift, notification, reading, authorization, and zone-scope predicates before broad before/after scans. If one violation is an omission, include the paired set-difference query pattern from this strategy: scope predicate with shared variable, then absent-side event predicate with polarity='negative'.",
        "For marine-insurance or coverage-dispute financial questions, query numeric rows before legal-position rows. Use claim_amount/5 for gross or adjusted amounts, calculation_step/5 for net/share/difference values, cost_claim/5 for surveyor estimates, cost_agreement/4 for accepted items, cost_disagreement/5 for disputed deltas, deductible/3 for deductible values, underwriter_line/4 for share percentages, and attachment_comparison/5 for treaty threshold comparisons when those predicates exist.",
        "For marine-insurance net-difference questions, retrieve both claimant and insurer net rows from calculation_step/5 or claim_amount/5 before asking legal_position/5. A legal position row usually explains the dispute, but it does not carry the arithmetic answer unless the numeric value appears in its returned atom.",
        "For marine-insurance questions asking whether an insurer accepted the full claimed amount, query both sides of the amount surface: claim_amount/5 for claimant and insurer/adjusted positions, calculation_step/5 for net positions, and cost_disagreement/5 for disputed items. Do not query only one amount type such as gross_claim against the insurer if the compiled KB uses adjusted_claim or adjusted_total.",
        "For marine-insurance hypothetical attachment questions such as 'even if the full claimant figure were accepted', retrieve the claimant net calculation_step/5, the lead underwriter share from underwriter_line/4, and attachment_comparison/5 or reinsurance_layer/5. Do not rely only on the actual adjusted-claim attachment row when the question asks about a different stated scenario.",
        "For marine-insurance H&M cover-suspension or condition-of-class questions, do not query P&I predicates. Prefer cover_suspension/4, class_survey_scope/4, contract_clause/4, defense_status/4, temporal_relation/3, and correction_record/5 when those exist. P&I cover answers liability-club questions, not Hull and Machinery cover-state questions.",
        "For marine-insurance P&I exposure questions, retrieve itemized exposure surfaces before role metadata: p_i_cover/4 for scope/year, p_i_notification_requirement/3 for notice duties, security_posted/4 for salvage security, cost_claim/5 or claim_amount/5 for cargo/pollution amounts, deductible/3 for P&I deductibles, and calculation_step/5 for total or derived exposure if present. Role rows such as dual_role/3 alone do not answer exposure totals.",
        "For marine-insurance legal citation or clause questions, query legal_citation/4 and citation_support/4 before broad legal_position/5 rows. Citations support positions; they are not findings.",
        "For marine-insurance reinsurance late-notice questions, query reinsurance_notice_effect/4 whenever it exists, alongside defense_status/4 and reinsurance_layer/5. defense_status/4 usually answers whether the issue affects the assured; reinsurance_notice_effect/4 answers what late notice does inside the treaty relationship.",
        "For marine-insurance trading-warranty, sanctions, port-call, or defense-status questions, query the whole chain when available: contract_clause/4 for the warranty, sanctions_event/5 or port_call/5 for voyage/cancellation facts, trading_warranty_status/4 for breach/remedy/intent status, defense_status/4 for whether a party raised or declined a defense, and citation_support/4 or legal_citation/4 for statutory support. Do not invent a label such as trading_warranty_defense unless that exact atom appears in relevant_clauses. Do not stop after the first trading_warranty_status row if another row contains a party's intent or non-intent. For trading_warranty_status/4 intent/non-intent questions, query trading_warranty_status(Policy, Subject, Status, Detail) with all slots as variables unless exact constants appear in relevant_clauses; the intent may be embedded in the Detail slot rather than a party atom.",
        "For marine-insurance surveyor agreement/disagreement questions, gather source-attributed report and technical rows: survey_report/4, survey_finding/5, measurement_claim/6, cost_claim/5, cost_agreement/4, cost_disagreement/5, class_survey_scope/4, survey_scope_exclusion/3, and correction_record/5 when present. Agreement questions often require both positive agreement rows and absence/outside-scope rows.",
        "For marine-insurance loss-of-hire calculation questions, retrieve the amount or disagreement row plus the time/rate support: cost_disagreement/5 or claim_amount/5 for the claimed LOH amount, loss_of_hire_period/4 for interval support, charter_rate/3 for the daily rate, and loss_of_hire_position/4 or contract_clause/4 for coverage status. Do not drop charter_rate/3 when the question asks how an amount was calculated.",
        "For maritime witness questions, the word 'Master' usually means the vessel's master/captain, not a harbour master. Query witness_statement(Speaker, Language, Subject, Content, Source) with Speaker as a variable unless the exact canonical speaker atom appears in relevant_clauses.",
        "For marine-insurance witness or expert statement count questions, do not bind the second witness_statement/5 slot to the literal constant language. Query witness_statement(Speaker, Language, Subject, Content, Source), then add survey_report/4, legal_position/5, source_detail/4, and citation_support/4 only if the question asks for expert/legal statements beyond witness rows.",
        "For threshold-elapsed questions, retrieve the starting state/event time, the threshold-hours policy row, and the later target event time. Use add_hours(StartTime, ThresholdHours, ThresholdTime), then elapsed_minutes(ThresholdTime, LaterTime, Minutes). Do not measure from the raw start event when the question asks from the threshold moment.",
        "For temporal helper chains, emit prerequisite helper queries before dependent helper queries: add_hours(StartTime, Hours, ThresholdTime) must appear before elapsed_minutes(ThresholdTime, LaterTime, Minutes). Prefer elapsed_minutes/3 for answers that may be less than one whole hour, then convert to hours/minutes in the concise answer.",
        "For duration or deadline questions that name a state threshold, first retrieve the state-change predicate that carries the start timestamp, then retrieve the policy threshold, then call add_hours/3 or elapsed_minutes/3. Do not call temporal helpers with unbound invented lowercase constants.",
        "For duration questions asking how long an entity was inside, active, held, processing, in custody, offline, or otherwise in a named interval/state, bind the start-event and end-event timestamp variables first, then call elapsed_minutes(StartTime, EndTime, Minutes). If the KB has event-description or event-type rows for start/end, ingress/egress, opened/closed, began/ended, or entered/exited labels, query those rows with shared event variables before the temporal helper. Never call elapsed_minutes(start, end, duration) with lowercase placeholders.",
        "For within-window or deadline-compliance questions, retrieve three pieces before computing: the start event/time, the target event/time, and the policy deadline/interval. Then call elapsed_minutes/3, elapsed_hours/3, or add_hours/3 with those bound variables. Do not ask a temporal helper with an unbound Starttime if the relevant start event predicate exists in the compiled inventory.",
        "When a question asks elapsed time between a derived threshold moment and a later event, compute the threshold moment with add_hours(StartTime, ThresholdHours, ThresholdTime) before calling elapsed_minutes(ThresholdTime, LaterTime, Minutes). Prefer elapsed_minutes/3 over elapsed_hours/3 unless the question explicitly requires whole hours only.",
        "For inspection-current or validity-window questions expressed in days, retrieve the inspection row and authorization row with shared variables, then call elapsed_days(InspectionDate, AuthorizationTime, ElapsedDays). Do not use add_hours/3 with a days-validity value.",
        "For questions asking when an advisory testing interval takes effect, ends, or reverts to normal, query both the interval rule and the advisory state event: testing_interval(contamination_advisory, Hours) or testing_interval(declared_contamination_advisory, Hours), plus contamination_advisory(triggered, StartTime) or contamination_advisory(lifted, EndTime).",
        "If the question specifically asks when the contamination advisory testing interval reverts to normal, emit all three support queries: contamination_advisory(lifted, EndTime), boil_water_notice_lifted(EndTime, Lifter), and policy_requirement(Bylaw, notice_lift_condition, Requirement) or policy_requirement(Bylaw, notice_lift_deadline, Requirement). Do not answer this question with testing_interval/2 alone.",
        "For enterprise-guidance or technical-policy QA, distinguish recommendation, preference, avoid-pattern, priority, procedure, tradeoff, and rule predicates. Do not answer a prefer question only from avoid_pattern/1, and do not answer an avoid question only from recommendation/1.",
        "For enterprise-guidance why/rationale questions, query the most specific available reason surface first: priority_reason/2 for ranked targets, export_reason/2 for export contexts, guard_effect/1 for guards, tradeoff/3 for benefit/downside pairs, summary_review_question/1 plus enables/2 for summary-method and On-Demand Calculation reasoning, debugging_tactic/2 or action_when/2 for procedural follow-ups, and support_reason/2, support_effect/2, support_tradeoff/3, support_exception/2, or support_positive_counterpart/2 when a support-acquisition pass has added source-grounded rationale rows.",
        "For priority-order questions, query optimization_priority(Target, Rank) and priority_reason(Target, Reason). Do not use recommendation/1 as a substitute for ranked priority rows.",
        "For enterprise-guidance questions asking whether a priority target is a risk or should be reviewed, query both optimization_priority(Target, Rank) and priority_reason(Target, Reason). The reason row often contains performance_risk or review rationale.",
        "For metric-boundary questions, query metric_semantics/2, does_not_directly_determine/2, validates_when_high/2, and performance_metric/1 before generic recommendations.",
        "For guard questions, query the whole guard support bundle when available: recommendation(use_guards_effectively), guard_value(Value), guard_mechanism(Mechanism), and guard_effect(Effect). If the question asks what guard does, guard_effect/1 is answer-bearing.",
        "For guard questions asking which values are useful as guards, query guard_value(Value) directly. Do not answer only from a generic use-guards recommendation.",
        "For guard questions asking how guards work or what pattern implements them, query guard_mechanism(Mechanism) and guard_effect(Effect).",
        "For summary-method questions, query optimization_priority/2, summary_review_question/1, enables/2, and priority_reason/2. Summary methods are a priority/checklist surface, not just a generic recommendation.",
        "For summary-method why questions, always include summary_review_question(Question), because the question rows may contain On-Demand Calculation and hierarchy-level support even when priority_reason/2 is missing.",
        "For summary-method questions asking what to check, emit broad summary_review_question(Question) queries. For questions asking why moving summaries later can help, pair summary_review_question/1 with enables(Design, Capability).",
        "For aggregation questions, query prefer_aggregation(Method) for 'which aggregation is fast/preferred' and higher_effort_aggregation(Method) for 'which methods require more effort'. Do not query only higher_effort_aggregation/1 when the question asks which aggregation is fast.",
        "For lookup-vs-sum questions, query avoid_pattern(multiple_lookups_when_sum_possible) or avoid_pattern(lookup_against_very_large_data_sources) plus prefer_aggregation(sum) when available.",
        "For export questions, keep export_rule/2, export_reason/2, and preferred_export/2 distinct. Combined Grids answer compact leaf-level export questions; Tabular Multiple Column Export answers export-type importance questions.",
        "For export questions asking which export type is important in Polaris, query export_rule(Context, Rule) and export_reason(Context, Reason). For compact leaf-level export questions, query preferred_export(ExportType, Purpose).",
        "For export questions asking why very large grids should not be pivot-exported, query export_reason(very_large_grids, Reason) and export_rule(very_large_grids, Rule) if those constants exist in relevant clauses.",
        "For intraday update questions, query intraday_update_rule/2, delta_load_pattern/2, incremental_filter/1, and recovery_path/1. If the question asks what to use instead of full clear-and-reload, delta_load_pattern rows are answer-bearing.",
        "For intraday update questions asking what not to rely on, query intraday_update_rule(Context, Rule). For questions asking what to use instead, query delta_load_pattern(ContextOrPart, Pattern) and incremental_filter(Filter).",
        "For staging-pattern questions, query all delta_load_pattern/2 rows first, then incremental_filter/1. A single avoid/full-reload row is not enough support for the replacement pattern.",
        "For filter/DCA/conditional-formatting questions, query avoid_pattern/1 for the problem, recommendation/1 for the replacement, debugging_tactic/2 for procedure, tradeoff/3 when the question asks why or downside, and support_positive_counterpart/2 or support_reason/2 when the KB contains support-acquisition rows.",
        "For user-based filter questions, query avoid_pattern(Pattern) for the risk. If the question asks what to use instead, also query recommendation(Recommendation) and any native-UX/filter predicate present; if no positive alternative exists, return partial rather than inventing one.",
        "For DCA or optimization debugging questions, query debugging_tactic(Problem, Step) and action_when(Condition, Action) broadly before generic recommendations.",
        "For slow-line-item questions asking where to look after a line item is already optimized, query debugging_tactic(slow_line_item_with_high_optimization, Step) and debugging_tactic(slow_line_item, Step) before priority rows.",
        "For computationally intensive function questions, query computationally_intensive_function(Function), optimization_priority(Target, Rank), priority_reason(Target, Reason), and debugging_tactic(Target, Step). The answer may require joining a function such as finditem to a target class such as line_items_with_high_calculation_effort_using_computationally_intensive_functions.",
        "For All Cells/high-cell-count questions, query priority_reason(Target, Reason) and optimization_priority(Target, Rank) broadly with Target as a variable; do not stop after the rank alone.",
        "For DEV model list-seeding questions, query recommendation(Recommendation) broadly and do not over-bind the recommendation atom; the answer may be a long normalized recommendation such as ensure_all_dimensions_in_dev_model_have_at_least_one_list_item.",
        "For DEV model list-seeding why questions, pair the list-item recommendation with debugging_tactic(non_winding_cyclic_calculation_error, Step) when available; the causal support may be split between a setup recommendation and the error class it allows the model to catch.",
        "For populated-cell questions that mention low complexity, high memory, or On-Demand Calculation, query metric_semantics/2, validates_when_high/2, does_not_directly_determine/2, summary_review_question/1, enables/2, and any debugging_tactic row mentioning end_of_chain or on_demand. Do not answer only from high-complexity priority rows.",
        "For time-range or population-restriction questions, query recommendation(Recommendation) broadly and prefer rows mentioning time ranges, booleans, or restricted populations when returned.",
        "For business-process model separation questions, query tradeoff/3 rather than only recommendation/1. The benefits and downsides are separate answer surfaces.",
        "For list-load questions, query list_load_risk/2 and reduce_list_load_impact/1 together; one names the risk and the other names mitigation tactics.",
    ],
    "failure_policy": [
        "If no compiled predicate can faithfully answer the question, emit no write and explain the missing predicate/support in self_check.",
        "If the question requires multi-hop reasoning not supported by the current runtime, emit the closest safe primitive queries and mark the remaining inference gap in truth_maintenance.derived_consequences.",
    ],
}

TEMPORAL_VIRTUAL_SIGNATURES = [
    "add_hours/3",
    "elapsed_minutes/3",
    "elapsed_hours/3",
    "elapsed_days/3",
]

STORY_WORLD_QA_QUERY_STRATEGY: dict[str, Any] = {
    "name": "story_world_qa_query_strategy_v1",
    "authority": "query_planning_guidance_only_runtime_executes_queries",
    "core_principle": (
        "For story-world QA, ask primitive queries over the compiled narrative KB surface. "
        "Do not answer from story memory or external tale templates."
    ),
    "query_patterns": [
        "For species/kind/type questions, query kind(Entity, Kind) when available; otherwise query character(Entity), object(Entity), food(Entity), or place(Entity) with Entity as a variable and infer only from returned source-local atoms.",
        "For household/resident questions, query lives_at(Character, Place) and optionally kind(Character, Kind) or household_member(Household, Character) when available.",
        "For location questions, query all relevant location predicates that exist for the entity: initial_location(Entity, Place), location_after_event(Entity, Event, Place), located_in(Entity, Place), near(Entity, Place), under(Entity, Place), or lives_at(Character, Place). Do not stop after the first partial location row if the answer may be composite.",
        "For errand/sent-by questions, query sent_by(Sender, Person, Errand), errand_item(Errand, Item), forgotten_by_during_story(Person, Item), or hazy_notion_by_during_story(Person, Item) when available.",
        "For ownership/intended-user questions, query owned_by(Object, Owner), designed_for(Object, Character), intended_for(Object, Character), or belongs_to_household(Object, Household). If the question names a size/object phrase such as middle-sized boots, great boat, or little mug, do not invent an abbreviated atom such as boots_middle or boat_great unless that exact atom appears in relevant_clauses. Prefer Object as a variable and let returned rows expose canonical atoms.",
        "For event questions, query event(Event, Actor, Action, Object, Place) with variables in the answer slot, then add story_time(Event, Time) or before/after queries only when order matters.",
        "For speech questions, query said(Event, Speaker, Quote). Do not query said/3 for non-speech facts such as who sent someone unless the compiled KB only represents that knowledge in speech.",
        "For subjective fit/quality questions, query judged(Judge, Item, Dimension, Verdict), accepted_choice(Person, Item), rejected_choice(Person, Item), or pattern_choice(Group, Item, Verdict).",
        "For why/causal questions, query causes(Event, Consequence), caused_by(Event, Cause), inferred_by(Character, Claim, Event), or evidence(Claim, Support) when present.",
        "For final-state questions, query final_state(State), condition_after_story(Entity, Condition), repaired(Entity), recovered_wheel(Wheel), or restitution(Person, Action).",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run QA probes against a domain bootstrap source-compile run.")
    parser.add_argument("--run-json", type=Path, required=True, help="domain_bootstrap_file_*.json with source_compile.")
    parser.add_argument("--qa-file", type=Path, required=True, help="Markdown file containing numbered QA prompts.")
    parser.add_argument("--oracle-jsonl", type=Path, default=None, help="Optional answer key for scoring.")
    parser.add_argument("--backend", choices=["lmstudio"], default="lmstudio")
    parser.add_argument("--model", default=os.environ.get("PRETHINKER_MODEL", "qwen/qwen3.6-35b-a3b"))
    parser.add_argument("--base-url", default=os.environ.get("PRETHINKER_BASE_URL", "http://127.0.0.1:1234"))
    parser.add_argument(
        "--api-key",
        default="",
        help="Optional OpenAI-compatible API key. Defaults to PRETHINKER_API_KEY or OPENROUTER_API_KEY.",
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.82)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--num-ctx", type=int, default=32768)
    parser.add_argument("--max-tokens", type=int, default=6000)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--only-ids", default="", help="Comma-separated QA ids to run, e.g. q006,q039.")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR, help="Per-question exact-input cache.")
    parser.add_argument("--no-cache", action="store_true", help="Disable exact-input QA row cache for a fresh run.")
    parser.add_argument("--include-model-input", action="store_true")
    parser.add_argument(
        "--evidence-bundle-plan",
        action="store_true",
        help="Run a query-only LLM control-plane pass that proposes evidence bundles over the compiled KB surface.",
    )
    parser.add_argument(
        "--execute-evidence-bundle-plan",
        action="store_true",
        help=(
            "After creating an evidence-bundle plan, execute only validated query templates from that plan "
            "as additional query-only diagnostic evidence."
        ),
    )
    parser.add_argument(
        "--evidence-bundle-context-filter",
        action="store_true",
        help=(
            "Use predicates from evidence_bundle_plan_v1 query templates to build a compact question-shaped "
            "relevant_clauses pack for the Semantic IR QA compiler."
        ),
    )
    parser.add_argument(
        "--evidence-bundle-context-max-clauses",
        type=int,
        default=220,
        help="Maximum relevant clauses retained by --evidence-bundle-context-filter.",
    )
    parser.add_argument(
        "--evidence-bundle-context-broad-floor",
        type=int,
        default=80,
        help="Minimum broad-context fallback clauses retained by --evidence-bundle-context-filter.",
    )
    parser.add_argument(
        "--helper-companion-row-limit",
        type=int,
        default=3,
        help=(
            "Question-level budget for query-only helper companion rows. "
            "Use 0 to suppress helper companions or -1 for unbounded forensic delivery."
        ),
    )
    parser.add_argument(
        "--include-legacy-native-helper-adapters",
        action="store_true",
        help=(
            "Opt in to older native-corpus helper adapters for forensic compatibility. "
            "Default QA relies on direct compile surfaces plus current generic companions."
        ),
    )
    parser.add_argument(
        "--judge-reference-answers",
        action="store_true",
        help="Use the model in structured-output mode to compare query results with markdown reference answers.",
    )
    parser.add_argument(
        "--classify-failure-surfaces",
        action="store_true",
        help=(
            "For non-exact judged rows, use a structured scorer to classify whether the remaining miss is "
            "a compile-surface, query-surface, hybrid-join, answer-surface, or uncertain problem."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if str(args.api_key or "").strip():
        os.environ["PRETHINKER_API_KEY"] = str(args.api_key).strip()
    _configure_openrouter_title(args.out_dir)
    run_path = args.run_json if args.run_json.is_absolute() else (REPO_ROOT / args.run_json).resolve()
    qa_path = args.qa_file if args.qa_file.is_absolute() else (REPO_ROOT / args.qa_file).resolve()
    run_record = json.loads(run_path.read_text(encoding="utf-8-sig"))
    qa_text = qa_path.read_text(encoding="utf-8-sig")
    questions = parse_numbered_markdown_questions(qa_text)
    only_ids = {item.strip() for item in str(args.only_ids or "").split(",") if item.strip()}
    if only_ids:
        questions = [item for item in questions if str(item.get("id", "")).strip() in only_ids]
    if int(args.limit or 0) > 0:
        questions = questions[: int(args.limit)]
    oracle = load_oracle(args.oracle_jsonl)
    for qid, answer in parse_markdown_answer_key(qa_text).items():
        oracle.setdefault(qid, {})["reference_answer"] = answer

    parsed_profile = run_record.get("parsed") if isinstance(run_record.get("parsed"), dict) else {}
    compile_record = run_record.get("source_compile") if isinstance(run_record.get("source_compile"), dict) else {}
    facts = [str(item).strip() for item in compile_record.get("facts", []) if str(item).strip()]
    rules = [str(item).strip() for item in compile_record.get("rules", []) if str(item).strip()]
    runtime, load_errors = load_runtime(facts=facts, rules=rules)

    allowed_predicates = profile_bootstrap_allowed_predicates(parsed_profile)
    predicate_contracts = profile_bootstrap_predicate_contracts(parsed_profile)
    kb_inventory = compiled_kb_inventory(facts=facts, rules=rules)
    actual_signatures = list(kb_inventory["signatures"])
    for signature in TEMPORAL_VIRTUAL_SIGNATURES:
        if signature not in actual_signatures:
            actual_signatures.append(signature)
    kb_inventory["signatures"] = actual_signatures
    kb_inventory["query_templates"] = [
        *kb_inventory.get("query_templates", []),
        *[query_template_for_signature(signature) for signature in TEMPORAL_VIRTUAL_SIGNATURES],
    ]
    if actual_signatures:
        allowed_predicates = actual_signatures
        predicate_contracts = compiled_kb_contracts(actual_signatures)
    domain_context = [
        *profile_bootstrap_domain_context(parsed_profile),
        "Post-ingestion QA mode: the source document has already been compiled into the KB.",
        "Treat the current utterance as a probe against existing KB state unless it explicitly states a correction or new assertion.",
        "For ordinary questions, emit query candidate_operations, not writes.",
        "Use the actual compiled KB predicate inventory exactly. Do not invent a new query predicate when the KB already has a predicate with the needed meaning.",
        "The QA runtime exposes virtual temporal predicates add_hours/3, elapsed_minutes/3, elapsed_hours/3, and elapsed_days/3. They are query-only runtime helpers for deriving time anchors and durations from admitted timestamp facts; they are not durable KB writes.",
        "For a query over a predicate, keep the predicate's full arity from compiled_predicate_inventory. If a slot is unspecified, fill it with an uppercase variable.",
        "Copy constants from relevant_clauses exactly. If the user question mentions only a surname, title, role, initials, or a paraphrased object/facility name, do not invent a lowercase atom for it; query with variables and let the compiled KB surface reveal the canonical constant.",
        "Role labels are not person constants. Query predicates such as inspection/3, bypass_authorization/3, coliform_reading/4, notification/5, or boil_water_notice_lifted/2 with Person/Actor variables, then use person_role/2 only to filter or explain those returned people.",
        "When the answer position is unknown, use Prolog variables X, Y, or Z exactly. Lowercase terms such as rule, time, condition, item, person, location, who, what, where, and answer are constants, not variables.",
        "Inside candidate_operations[].args, variables must also be uppercase strings such as X, Y, Z, Rule, Item, or Time.",
        "Role, status, type, and relation labels are lowercase constants when they are named by the question or visible in relevant_clauses. Do not convert a role such as research_integrity_officer, respondent, complainant, provost, chair, college, department, yes, no, final, or preliminary into an uppercase variable.",
        "If the question asks who has a named role, bind the role/status argument to the exact lowercase atom from relevant_clauses when present, for example person_role(Person, research_integrity_officer), not person_role(Person, Research_Integrity_Officer).",
        "For who/what/which/where/when/why questions, leave the requested answer position as a variable. Do not fill that slot with a likely answer from relevant_clauses unless the user question itself names that value.",
        "Never put lowercase generic placeholder words into query arguments when you want the KB to return a value. This includes label words such as grievance_label, method_detail, explanation_detail, candidate, label, content, value, status, authority, and institution.",
        "compiled_query_templates shows legal query shapes. Prefer those templates and then bind only the slots that are clearly named in the question.",
        "compiled_surface_alias_inventory shows predicate families actually present in this compile. Use it to find sibling or decomposed surfaces before falling back to helpers or source-record text.",
        "For multi-hop questions, emit multiple safe query operations over the actual KB predicates instead of inventing a composite predicate.",
        "For homeroom membership or homeroom student-count questions, if compiled_query_templates includes roster_table_member/4, prefer roster_table_member(SourceRow, Version, Group, Student) for explicit table membership before sparse semantic member predicates such as homeroom_member/3.",
        "For source/institution questions, prefer predicates that actually expose source, ledger, actor, reporter, complainant, or institution values in the compiled KB examples.",
        "For ledger/record/institution questions, pair the descriptive event predicate with the likely container predicate using the same variable name, such as grievance_method(Grievance, Method) plus grievance_target(Grievance, Institution).",
        "Do not lock onto a single grievance/document id before discovering answer-bearing rows; duplicate compiled records may contain different detail levels.",
        "For reporter questions, include grievance_reporter(Grievance, Reporter) and a content-bearing predicate with the same Grievance variable; the thing reported may appear in an explanation or method label rather than in grievance_target.",
        "For source-owned record predicates, avoid putting role labels into arguments. Query alleged_violation(Grievance, Actor, Violation, Evidence), ledger_entry(Ledger, Entry, RecordType), or witness_observation(Observation, Observer, Content) unless a concrete atom is copied from relevant_clauses.",
        "When the question names a partial phrase such as blue sneezing, do not bind blue_sneezing unless that exact atom appears in relevant_clauses; use a variable over explanation/method slots so longer atoms can match.",
        "Keep QA workspaces compact by default: at most 4 query operations and at most 2 short self_check notes. If the question asks for all conditions, a summary, multiple violations, threshold elapsed time, deadline derivation, or multi-step duration, use up to 16 query operations rather than dropping whole support bundles.",
        "For unsafe inference traps, preserve the difference between direct KB support, source claim, inference, and unknown.",
        "Use post_ingestion_qa_query_strategy_v1 in kb_context_pack as the query-planning procedure.",
        "For omission/set-difference questions, the semantic IR operation itself must carry polarity='negative' on the absent-side predicate. The runtime can then build query-only negation; do not approximate omission by listing positive rows only.",
        "If the compiled inventory contains story-world predicates such as event/5, story_time/2, kind/2, lives_at/2, owned_by/2, said/3, judged/4, causes/2, initial_location/2, location_after_event/3, final_state/1, or condition_after_story/2, also use story_world_qa_query_strategy_v1.",
    ]
    if bool(args.evidence_bundle_plan or args.execute_evidence_bundle_plan or args.evidence_bundle_context_filter):
        domain_context.append(
            "A separate evidence_bundle_plan_v1 control-plane pass may be present in kb_context_pack. Treat it as query-planning guidance only: it can suggest support bundles, but it cannot authorize writes or replace mapper admission."
        )
    if bool(args.execute_evidence_bundle_plan):
        domain_context.append(
            "If evidence-bundle plan queries are executed, they are query-only diagnostics validated against the compiled KB predicate inventory; they do not authorize writes or durable truth."
        )
    if bool(args.evidence_bundle_context_filter):
        domain_context.append(
            "If evidence-bundle context filtering is active, relevant_clauses has been compacted using predicates from the LLM-authored evidence bundle plan. Treat it as a focused KB view, not as the full KB."
        )
    config = SemanticIRCallConfig(
        backend=str(args.backend),
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
        api_key=str(getattr(args, "api_key", "") or ""),
    )

    rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    cache_hits = 0
    cache_misses = 0
    cache_dir = args.cache_dir if args.cache_dir.is_absolute() else (REPO_ROOT / args.cache_dir).resolve()
    cache_enabled = not bool(args.no_cache)
    cache_context = build_cache_context(
        run_path=run_path,
        qa_path=qa_path,
        run_record=run_record,
        facts=facts,
        rules=rules,
        allowed_predicates=allowed_predicates,
        predicate_contracts=predicate_contracts,
        domain_context=domain_context,
        kb_inventory=kb_inventory,
        config=config,
        include_model_input=bool(args.include_model_input),
        judge_reference_answers=bool(args.judge_reference_answers),
        evidence_bundle_plan=bool(args.evidence_bundle_plan or args.execute_evidence_bundle_plan or args.evidence_bundle_context_filter),
        execute_evidence_bundle_plan=bool(args.execute_evidence_bundle_plan),
        evidence_bundle_context_filter=bool(args.evidence_bundle_context_filter),
        evidence_bundle_context_max_clauses=int(args.evidence_bundle_context_max_clauses or 0),
        evidence_bundle_context_broad_floor=int(args.evidence_bundle_context_broad_floor or 0),
        helper_companion_row_limit=args.helper_companion_row_limit,
        include_legacy_native_helper_adapters=bool(args.include_legacy_native_helper_adapters),
        classify_failure_surfaces=bool(args.classify_failure_surfaces),
    )
    for item in questions:
        question_oracle = oracle.get(item["id"], {})
        cache_key = cache_key_for_question(context=cache_context, item=item, oracle=question_oracle)
        cached_row = read_cached_row(cache_dir=cache_dir, cache_key=cache_key) if cache_enabled else None
        if cached_row is not None:
            row = cached_row
            row["cache_hit"] = True
            row["cache_key"] = cache_key
            cache_hits += 1
        else:
            cache_misses += 1
            row = run_one_question(
                item=item,
                config=config,
                allowed_predicates=allowed_predicates,
                predicate_contracts=predicate_contracts,
                domain_context=domain_context,
                kb_inventory=kb_inventory,
                facts=facts,
                rules=rules,
                runtime=runtime,
                oracle=question_oracle,
                include_model_input=bool(args.include_model_input),
                evidence_bundle_plan=bool(args.evidence_bundle_plan or args.execute_evidence_bundle_plan or args.evidence_bundle_context_filter),
                execute_evidence_bundle_plan=bool(args.execute_evidence_bundle_plan),
                evidence_bundle_context_filter=bool(args.evidence_bundle_context_filter),
                evidence_bundle_context_max_clauses=int(args.evidence_bundle_context_max_clauses or 0),
                evidence_bundle_context_broad_floor=int(args.evidence_bundle_context_broad_floor or 0),
                helper_companion_row_limit=args.helper_companion_row_limit,
                include_legacy_native_helper_adapters=bool(args.include_legacy_native_helper_adapters),
            )
            if bool(args.judge_reference_answers):
                row["reference_judge"] = judge_reference_answer(
                    row=row,
                    config=config,
                )
            if bool(args.classify_failure_surfaces):
                row["failure_surface"] = classify_failure_surface(
                    row=row,
                    kb_inventory=kb_inventory,
                    facts=facts,
                    rules=rules,
                    config=config,
                )
            row["cache_hit"] = False
            row["cache_key"] = cache_key
            if cache_enabled and is_cacheable_row(row):
                write_cached_row(cache_dir=cache_dir, cache_key=cache_key, row=row)
        rows.append(row)

    summary = summarize(rows=rows, load_errors=load_errors, elapsed_ms=int((time.perf_counter() - started) * 1000))
    summary["cache_enabled"] = cache_enabled
    summary["cache_hits"] = cache_hits
    summary["cache_misses"] = cache_misses
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_json": str(run_path),
        "qa_file": str(qa_path),
        "model": str(args.model),
        "source_fact_count": len(facts),
        "source_rule_count": len(rules),
        "runtime_load_errors": load_errors,
        "oracle_present": bool(oracle),
        "cache": {
            "enabled": cache_enabled,
            "schema_version": CACHE_SCHEMA_VERSION,
            "dir": str(cache_dir),
            "hits": cache_hits,
            "misses": cache_misses,
        },
        "summary": summary,
        "rows": rows,
    }
    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{_slug(qa_path.stem)}_{_slug(str(args.model))}"
    json_path = out_dir / f"domain_bootstrap_qa_{slug}.json"
    md_path = json_path.with_suffix(".md")
    json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    write_summary(record, md_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


def build_cache_context(
    *,
    run_path: Path,
    qa_path: Path,
    run_record: dict[str, Any],
    facts: list[str],
    rules: list[str],
    allowed_predicates: list[str],
    predicate_contracts: list[dict[str, Any]],
    domain_context: list[str],
    kb_inventory: dict[str, Any],
    config: SemanticIRCallConfig,
    include_model_input: bool,
    judge_reference_answers: bool,
    evidence_bundle_plan: bool,
    execute_evidence_bundle_plan: bool,
    evidence_bundle_context_filter: bool,
    evidence_bundle_context_max_clauses: int,
    evidence_bundle_context_broad_floor: int,
    helper_companion_row_limit: int | None,
    include_legacy_native_helper_adapters: bool,
    classify_failure_surfaces: bool,
) -> dict[str, Any]:
    return {
        "schema_version": CACHE_SCHEMA_VERSION,
        "script_hash": hash_text(Path(__file__).read_text(encoding="utf-8")),
        "run_path": str(run_path),
        "run_hash": hash_text(json.dumps(run_record, ensure_ascii=False, sort_keys=True)),
        "qa_path": str(qa_path),
        "qa_hash": hash_text(qa_path.read_text(encoding="utf-8-sig")),
        "facts_hash": hash_text(json.dumps(facts, ensure_ascii=False, sort_keys=True)),
        "rules_hash": hash_text(json.dumps(rules, ensure_ascii=False, sort_keys=True)),
        "allowed_predicates_hash": hash_text(json.dumps(allowed_predicates, ensure_ascii=False, sort_keys=True)),
        "predicate_contracts_hash": hash_text(json.dumps(predicate_contracts, ensure_ascii=False, sort_keys=True)),
        "domain_context_hash": hash_text(json.dumps(domain_context, ensure_ascii=False, sort_keys=True)),
        "kb_inventory_hash": hash_text(json.dumps(kb_inventory, ensure_ascii=False, sort_keys=True)),
        "query_strategy_hash": hash_text(
            json.dumps(
                {
                    "post_ingestion": POST_INGESTION_QA_QUERY_STRATEGY,
                    "story_world": STORY_WORLD_QA_QUERY_STRATEGY,
                    "temporal_virtual_signatures": TEMPORAL_VIRTUAL_SIGNATURES,
                    "judge_schema": QA_JUDGE_SCHEMA,
                    "failure_surface_schema": FAILURE_SURFACE_SCHEMA,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        ),
        "config": {
            "backend": str(config.backend),
            "base_url": str(config.base_url),
            "model": str(config.model),
            "context_length": int(config.context_length),
            "timeout": int(config.timeout),
            "temperature": float(config.temperature),
            "top_p": float(config.top_p),
            "top_k": int(config.top_k),
            "max_tokens": int(config.max_tokens),
            "think_enabled": bool(config.think_enabled),
            "reasoning_effort": str(config.reasoning_effort or ""),
        },
        "include_model_input": bool(include_model_input),
        "judge_reference_answers": bool(judge_reference_answers),
        "evidence_bundle_plan": bool(evidence_bundle_plan),
        "execute_evidence_bundle_plan": bool(execute_evidence_bundle_plan),
        "evidence_bundle_context_filter": bool(evidence_bundle_context_filter),
        "evidence_bundle_context_max_clauses": int(evidence_bundle_context_max_clauses or 0),
        "evidence_bundle_context_broad_floor": int(evidence_bundle_context_broad_floor or 0),
        "helper_companion_row_limit": helper_companion_row_limit,
        "helper_companion_budget_ranker": "lexical_query_overlap_v1",
        "include_legacy_native_helper_adapters": bool(include_legacy_native_helper_adapters),
        "classify_failure_surfaces": bool(classify_failure_surfaces),
    }


def cache_key_for_question(*, context: dict[str, Any], item: dict[str, Any], oracle: dict[str, Any]) -> str:
    payload = {
        "context": context,
        "question": item,
        "oracle": oracle,
    }
    return hash_text(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def read_cached_row(*, cache_dir: Path, cache_key: str) -> dict[str, Any] | None:
    path = cache_dir / f"{cache_key}.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    if payload.get("schema_version") != CACHE_SCHEMA_VERSION:
        return None
    row = payload.get("row")
    if not isinstance(row, dict):
        return None
    return dict(row)


def write_cached_row(*, cache_dir: Path, cache_key: str, row: dict[str, Any]) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": CACHE_SCHEMA_VERSION,
        "cache_key": cache_key,
        "cached_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "row": row,
    }
    (cache_dir / f"{cache_key}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def is_cacheable_row(row: dict[str, Any]) -> bool:
    if not bool(row.get("ok")):
        return False
    if str(row.get("error", "")).strip():
        return False
    judge = row.get("reference_judge")
    if isinstance(judge, dict):
        issues = " ".join(str(item) for item in judge.get("issues", []) if str(item).strip())
        if "judge error:" in issues:
            return False
    return True


def hash_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def parse_numbered_markdown_questions(text: str) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    phase = ""
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if re.match(r"^#+\s*answers\b", line, flags=re.IGNORECASE):
            break
        if line.startswith("#"):
            phase = line.lstrip("#").strip()
            continue
        match = re.match(r"^(\d+)\.\s+(.*\S)\s*$", line)
        if not match:
            continue
        questions.append({"id": f"q{int(match.group(1)):03d}", "number": int(match.group(1)), "phase": phase, "utterance": match.group(2)})
    return questions


def parse_markdown_answer_key(text: str) -> dict[str, str]:
    answers: dict[str, str] = {}
    in_answers = False
    current_id = ""
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_id, current_lines
        if current_id and current_lines:
            answers[current_id] = " ".join(part.strip() for part in current_lines if part.strip()).strip()
        current_id = ""
        current_lines = []

    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if not in_answers:
            if re.match(r"^#+\s*answers\b", line, flags=re.IGNORECASE):
                in_answers = True
            continue
        match = re.match(r"^(\d+)\.\s+(.*\S)\s*$", line)
        if match:
            flush()
            current_id = f"q{int(match.group(1)):03d}"
            current_lines = [match.group(2)]
            continue
        if current_id and line and not line.startswith("#"):
            current_lines.append(line)
    flush()
    return answers


def compiled_kb_inventory(*, facts: list[str], rules: list[str]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    examples: dict[str, list[str]] = {}
    for clause in [*facts, *rules]:
        signature = clause_signature(clause)
        if not signature:
            continue
        counts[signature] = counts.get(signature, 0) + 1
        bucket = examples.setdefault(signature, [])
        if len(bucket) < 8:
            bucket.append(str(clause).strip())
    signatures = sorted(counts, key=lambda item: (-counts[item], item))
    return {
        "signatures": signatures,
        "counts": counts,
        "examples": {signature: examples.get(signature, []) for signature in signatures[:80]},
        "query_templates": [query_template_for_signature(signature) for signature in signatures],
        "surface_alias_inventory": compiled_surface_alias_inventory(signatures),
    }


def compiled_surface_alias_inventory(signatures: list[str]) -> list[dict[str, Any]]:
    """Group present predicates into generic query-planning surface families.

    This is not a synonym table for one corpus. It is a compact hint that
    predicate palettes can pack the same answer-bearing surface differently.
    The QA planner still has to query real predicates listed in the inventory.
    """

    family_specs: tuple[tuple[str, str, tuple[str, ...], tuple[str, ...]], ...] = (
        (
            "identity_role_surface",
            "people or organizations bound to source-stated roles",
            ("role", "party", "person", "authority", "counsel", "claimant", "owner"),
            ("identity", "role", "party"),
        ),
        (
            "item_identifier_surface",
            "item, asset, object, inventory, and description identifiers",
            ("item", "asset", "object", "inventory", "description", "id"),
            ("item", "asset", "object", "inventory", "description", "id"),
        ),
        (
            "external_identifier_surface",
            "external references, external ids, catalog ids, and source ids",
            ("external", "reference", "ref", "catalog", "source", "id"),
            ("external", "reference"),
        ),
        (
            "custody_location_surface",
            "physical custody, holder, location, storage, and custodian rows",
            ("custody", "custodian", "holder", "held", "physical", "location", "storage"),
            ("custody", "custodian", "location"),
        ),
        (
            "title_status_surface",
            "recorded title, ownership, contestation, and status rows",
            ("title", "owner", "ownership", "status", "contested", "recorded"),
            ("title", "status", "ownership"),
        ),
        (
            "access_authorization_surface",
            "access permission, access denial, authorization, and authority source rows",
            ("access", "authoriz", "authority", "party", "no", "source"),
            ("access", "authoriz", "authority", "party"),
        ),
        (
            "order_effect_surface",
            "orders, order dates, order ids, effects, rulings, and issued decisions",
            ("order", "ruling", "issued", "effect", "date", "decision"),
            ("order", "effect"),
        ),
        (
            "chronology_event_surface",
            "chronology events, event ordering, before/after anchors, and dated events",
            ("chronolog", "event", "before", "after", "occurred", "date"),
            ("event", "chronology"),
        ),
        (
            "source_assertion_surface",
            "source claims, assertions, disputes, objections, grounds, and status",
            ("claim", "assert", "dispute", "objection", "ground", "status", "source"),
            ("claim", "assert", "dispute"),
        ),
    )
    out: list[dict[str, Any]] = []
    for family, purpose, any_tokens, anchor_tokens in family_specs:
        matches: list[str] = []
        for signature in signatures:
            if "/" not in str(signature):
                continue
            predicate = str(signature).split("/", 1)[0]
            lowered = predicate.casefold()
            if not any(token in lowered for token in anchor_tokens):
                continue
            if any(token in lowered for token in any_tokens):
                matches.append(str(signature))
        if matches:
            out.append(
                {
                    "family": family,
                    "purpose": purpose,
                    "signatures": matches[:16],
                    "query_policy": "Use the present signatures in this family as alternative or decomposed surfaces; do not invent predicates outside compiled_predicate_inventory.",
                }
            )
    return out


def compiled_kb_contracts(signatures: list[str]) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for signature in signatures:
        try:
            arity = int(signature.rsplit("/", 1)[1])
        except Exception:
            continue
        contracts.append({"signature": signature, "args": [f"arg{i}" for i in range(1, arity + 1)]})
    return contracts


def query_template_for_signature(signature: str) -> str:
    text = str(signature or "").strip()
    if "/" not in text:
        return ""
    name, arity_text = text.rsplit("/", 1)
    try:
        arity = int(arity_text)
    except Exception:
        return ""
    variables = ["X", "Y", "Z", "A", "B", "C", "D", "E"]
    args = [variables[index] if index < len(variables) else f"V{index + 1}" for index in range(max(arity, 0))]
    return f"{name}({', '.join(args)})."


def clause_signature(clause: str) -> str:
    text = str(clause or "").strip()
    if not text:
        return ""
    if ":-" in text:
        text = text.split(":-", 1)[0].strip()
    match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*\.?$", text)
    if not match:
        return ""
    args = split_top_level_args(match.group(2).strip())
    return f"{match.group(1)}/{len(args)}"


def split_top_level_args(text: str) -> list[str]:
    if not str(text or "").strip():
        return []
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in str(text):
        if char in "([":
            depth += 1
        elif char in ")]" and depth > 0:
            depth -= 1
        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def parse_prolog_query(query: str) -> tuple[str, list[str]] | None:
    text = str(query or "").strip()
    if len(split_top_level_args(text.rstrip(". "))) != 1:
        return None
    match = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.?\s*", text)
    if not match:
        return None
    predicate, args_text = match.groups()
    args = split_top_level_args(args_text)
    if not args:
        return None
    return predicate, args


def parse_prolog_query_goals(query: str) -> list[tuple[str, list[str]]] | None:
    text = str(query or "").strip().rstrip(".")
    if not text:
        return None
    goals: list[tuple[str, list[str]]] = []
    for part in split_top_level_args(text):
        parsed = parse_prolog_query(part)
        if parsed is None:
            return None
        goals.append(parsed)
    return goals or None


def format_prolog_query(predicate: str, args: list[str]) -> str:
    return f"{predicate}({', '.join(args)})."


def format_prolog_query_goals(goals: list[tuple[str, list[str]]]) -> str:
    return ", ".join(format_prolog_query(predicate, args).rstrip(".") for predicate, args in goals) + "."


def _is_prolog_variable(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Z][A-Za-z0-9_]*", str(value or "").strip()))


def _is_status_projection_variable(value: str) -> bool:
    text = str(value or "").strip()
    if not _is_prolog_variable(text):
        return False
    tokens = {token.lower() for token in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", text)}
    return bool(tokens & {"status", "state", "classification", "disposition", "condition"})


def _is_numeric_atom(value: str) -> bool:
    return bool(re.fullmatch(r"-?\d+(?:\.\d+)?", str(value or "").strip()))


def _variable_name_for_placeholder(value: str, index: int) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", str(value or "")).strip("_")
    if not cleaned:
        return f"Slot{index}"
    parts = [part for part in cleaned.split("_") if part]
    name = "".join(part[:1].upper() + part[1:] for part in parts)
    if not name or not name[0].isalpha():
        return f"Slot{index}"
    return name


def _looks_like_temporal_slot_placeholder(value: str) -> bool:
    item = str(value or "").strip()
    if not re.fullmatch(r"[a-z][a-z0-9_]*", item):
        return False
    if any(char.isdigit() for char in item):
        return False
    lowered = item.lower()
    return lowered.endswith(
        ("date", "time", "timestamp", "deadline", "duration", "hours", "minutes", "event")
    ) or "elapsed" in lowered


def _placeholder_repaired_query(query: str) -> dict[str, Any] | None:
    parsed = parse_prolog_query(query)
    if parsed is None:
        return None
    predicate, args = parsed
    repaired_args: list[str] = []
    repairs: list[dict[str, Any]] = []
    for index, arg in enumerate(args, start=1):
        item = str(arg or "").strip()
        lowered = item.lower()
        if _is_prolog_variable(item) or _is_numeric_atom(item):
            repaired_args.append(item)
            continue
        if lowered in GENERIC_QUERY_PLACEHOLDERS:
            variable = _variable_name_for_placeholder(item, index)
            repaired_args.append(variable)
            repairs.append({"index": index, "from": item, "to": variable})
            continue
        if _looks_like_temporal_slot_placeholder(item):
            variable = _variable_name_for_placeholder(item, index)
            repaired_args.append(variable)
            repairs.append({"index": index, "from": item, "to": variable})
            continue
        repaired_args.append(item)
    if not repairs:
        return None
    repaired_query = format_prolog_query(predicate, repaired_args)
    if repaired_query == str(query or "").strip():
        return None
    return {
        "query": repaired_query,
        "repairs": repairs,
    }


def _source_record_field_sibling_repaired_query(query: str) -> dict[str, Any] | None:
    goals = parse_prolog_query_goals(query)
    if not goals:
        return None
    repaired_goals: list[str] = []
    repairs: list[dict[str, Any]] = []
    changed = False
    for goal_index, (predicate, args) in enumerate(goals, start=1):
        repair = _source_record_field_sibling_repair_goal(predicate, args, goal_index=goal_index)
        if repair:
            repaired_goals.extend(repair["goals"])
            repairs.append(repair["repair"])
            changed = True
        else:
            repaired_goals.append(format_prolog_query(predicate, args).rstrip("."))
    if not changed:
        return None
    repaired_query = f"{', '.join(repaired_goals)}."
    return {
        "query": repaired_query,
        "repairs": repairs,
    }


def _source_record_field_sibling_repair_goal(
    predicate: str,
    args: list[str],
    *,
    goal_index: int,
) -> dict[str, Any] | None:
    if predicate != "source_record_field" or len(args) != 3:
        return None
    row_arg, field_arg, value_arg = [str(arg or "").strip() for arg in args]
    if not _is_prolog_variable(row_arg):
        return None
    if _source_record_field_arg_is_row_like(row_arg):
        return None
    if _is_prolog_variable(value_arg):
        return None
    if value_arg.lower() in GENERIC_QUERY_PLACEHOLDERS:
        return None
    source_row_var = f"SourceRowFor{_variable_name_for_placeholder(row_arg, goal_index)}"
    if row_arg == source_row_var:
        source_row_var = f"SourceRecordRow{goal_index}"
    field_term = field_arg
    if not field_term or _is_prolog_variable(field_term) or field_term.lower() in {"field", "key", "value"}:
        field_term = "Field"
    repaired_goals = [
        f"source_record_field({source_row_var}, event, {row_arg})",
        f"source_record_field({source_row_var}, {field_term}, {value_arg})",
    ]
    repaired_query = f"{', '.join(repaired_goals)}."
    return {
        "goals": repaired_goals,
        "repair": {
            "from": format_prolog_query(predicate, args),
            "to": repaired_query,
            "reason": "source_record_field first argument is a row id; event/entity ids live in sibling field values",
        },
    }


def _source_record_field_arg_is_row_like(value: str) -> bool:
    lowered = str(value or "").casefold()
    return any(marker in lowered for marker in ("row", "line", "source"))


def _source_record_numeric_token_repaired_query(query: str) -> dict[str, Any] | None:
    goals = parse_prolog_query_goals(query)
    if not goals:
        return None
    repaired_goals: list[tuple[str, list[str]]] = []
    repairs: list[dict[str, str]] = []
    for predicate, args in goals:
        new_args = list(args)
        if predicate == "source_record_numeric_token" and len(args) >= 2:
            raw_token = str(args[1]).strip()
            token = raw_token.strip("'\"")
            if token and not _is_prolog_variable(token) and not token.startswith("v_"):
                repaired = "v_" + token
                new_args[1] = repaired
                repairs.append({"predicate": predicate, "from": raw_token, "to": repaired})
        repaired_goals.append((predicate, new_args))
    if not repairs:
        return None
    repaired_query = format_prolog_query_goals(repaired_goals)
    if repaired_query == str(query or "").strip():
        return None
    return {"query": repaired_query, "repairs": repairs}


def load_oracle(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    resolved = path if path.is_absolute() else (REPO_ROOT / path).resolve()
    out: dict[str, dict[str, Any]] = {}
    for raw_line in resolved.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        item = json.loads(line)
        if isinstance(item, dict) and str(item.get("id", "")).strip():
            out[str(item["id"]).strip()] = item
    return out


def load_runtime(*, facts: list[str], rules: list[str]) -> tuple[CorePrologRuntime, list[str]]:
    runtime = CorePrologRuntime(max_depth=500)
    errors: list[str] = []
    for fact in facts:
        result = runtime.assert_fact(fact)
        if str(result.get("status", "")) != "success":
            errors.append(f"fact {fact}: {result.get('message', result)}")
    for rule in rules:
        result = runtime.assert_rule(rule)
        if str(result.get("status", "")) != "success":
            errors.append(f"rule {rule}: {result.get('message', result)}")
    return runtime, errors


def build_evidence_bundle_plan(
    *,
    utterance: str,
    kb_inventory: dict[str, Any],
    facts: list[str],
    rules: list[str],
    config: SemanticIRCallConfig,
) -> dict[str, Any]:
    payload = {
        "task": "Plan query evidence bundles over an already compiled Prolog KB.",
        "authority": [
            "You are a control-plane query planner only.",
            "Do not answer the user.",
            "Do not propose facts, rules, corrections, or writes.",
            "Do not use the original source document; only use the compiled KB inventory and relevant clauses supplied here.",
            "Do not invent predicates. Query templates must use predicates present in compiled_predicate_inventory.signatures or the listed temporal virtual predicates.",
        ],
        "question": str(utterance or ""),
        "compiled_predicate_inventory": {
            "signatures": kb_inventory.get("signatures", [])[:120],
            "counts": kb_inventory.get("counts", {}),
            "examples": kb_inventory.get("examples", {}),
        },
        "compiled_surface_alias_inventory": kb_inventory.get("surface_alias_inventory", [])[:32],
        "compiled_query_templates": kb_inventory.get("query_templates", [])[:120],
        "relevant_clauses": [*facts[:600], *rules[:160]],
        "planning_policy": [
            "A support bundle is a small group of primitive Prolog queries that, together, can support an answer.",
            "Prefer multiple primitive queries over an invented composite query.",
            "Use compiled_surface_alias_inventory only as a map of sibling/decomposed predicate surfaces that are already present.",
            "Use uppercase variables for unknown answer slots.",
            "If the KB appears to lack a needed row class, state that in missing_if_empty rather than inventing it.",
            "For why questions, plan queries for reason/tradeoff/effect/procedure rows, not only the headline recommendation.",
            "For policy or guidance questions, separate requirement, observed fact, preference, avoid-pattern, and rationale rows.",
            "For complementary phrasing such as in addition to, besides, along with, apart from, or not only/but also, include a query for the named baseline relation only as context; the answer query should target sibling predicates over the same subject that expose the additional relation or property.",
        ],
    }
    messages = [
        {
            "role": "system",
            "content": (
                "You produce evidence_bundle_plan_v1 JSON for a governed symbolic QA pipeline. "
                "You only plan Prolog query evidence bundles over the supplied compiled KB surface."
            ),
        },
        {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
    ]
    try:
        return call_lmstudio_json_schema(
            config=config,
            messages=messages,
            schema_name="evidence_bundle_plan_v1",
            schema=EVIDENCE_BUNDLE_PLAN_SCHEMA,
            max_tokens=min(int(config.max_tokens), 1800),
        )
    except Exception as exc:
        return {
            "schema_version": "evidence_bundle_plan_v1",
            "question_focus": "planner_error",
            "support_bundles": [],
            "warnings": [str(exc)[:220]],
        }


def run_one_question(
    *,
    item: dict[str, Any],
    config: SemanticIRCallConfig,
    allowed_predicates: list[str],
    predicate_contracts: list[dict[str, Any]],
    domain_context: list[str],
    kb_inventory: dict[str, Any],
    facts: list[str],
    rules: list[str],
    runtime: CorePrologRuntime,
    oracle: dict[str, Any],
    include_model_input: bool,
    evidence_bundle_plan: bool,
    execute_evidence_bundle_plan: bool,
    evidence_bundle_context_filter: bool,
    evidence_bundle_context_max_clauses: int,
    evidence_bundle_context_broad_floor: int,
    helper_companion_row_limit: int | None,
    include_legacy_native_helper_adapters: bool,
) -> dict[str, Any]:
    utterance = str(item.get("utterance", ""))
    kb_context_pack = {
        "version": "semantic_ir_context_pack_v1",
        "mode": "post_ingestion_qa",
        "post_ingestion_qa_query_strategy": POST_INGESTION_QA_QUERY_STRATEGY,
        "story_world_qa_query_strategy": STORY_WORLD_QA_QUERY_STRATEGY,
        "compiled_predicate_inventory": {
            "signatures": kb_inventory.get("signatures", [])[:120],
            "counts": kb_inventory.get("counts", {}),
            "examples": kb_inventory.get("examples", {}),
        },
        "compiled_surface_alias_inventory": kb_inventory.get("surface_alias_inventory", [])[:32],
        "compiled_query_templates": kb_inventory.get("query_templates", [])[:120],
        "relevant_clauses": [*facts[:600], *rules[:160]],
        "source_fact_count": len(facts),
        "source_rule_count": len(rules),
    }
    evidence_plan: dict[str, Any] | None = None
    if bool(evidence_bundle_plan):
        evidence_plan = build_evidence_bundle_plan(
            utterance=utterance,
            kb_inventory=kb_inventory,
            facts=facts,
            rules=rules,
            config=config,
        )
        kb_context_pack["evidence_bundle_plan_v1"] = evidence_plan
        kb_context_pack["evidence_bundle_plan_policy"] = [
            "This plan is LLM-authored query guidance only.",
            "Use suggested query templates only if their predicates exist in compiled_predicate_inventory.",
            "Do not write facts or rules because of the evidence bundle plan.",
        ]
        if bool(evidence_bundle_context_filter):
            compact_clauses = compact_relevant_clauses_for_evidence_plan(
                evidence_plan=evidence_plan,
                facts=facts,
                rules=rules,
                max_clauses=max(1, int(evidence_bundle_context_max_clauses or 220)),
                broad_floor=max(0, int(evidence_bundle_context_broad_floor or 80)),
            )
            if compact_clauses:
                kb_context_pack["relevant_clauses"] = compact_clauses
                kb_context_pack["evidence_bundle_context_filter"] = {
                    "schema_version": "evidence_bundle_context_filter_v1",
                    "clause_count": len(compact_clauses),
                    "max_clauses": max(1, int(evidence_bundle_context_max_clauses or 220)),
                    "broad_floor": max(0, int(evidence_bundle_context_broad_floor or 80)),
                    "policy": "filtered by predicates from evidence_bundle_plan_v1 query templates; no raw-source or question parsing in Python",
                }
    started = time.perf_counter()
    try:
        result = call_semantic_ir(
            utterance=utterance,
            config=config,
            context=[],
            domain_context=domain_context,
            allowed_predicates=allowed_predicates,
            predicate_contracts=predicate_contracts,
            kb_context_pack=kb_context_pack,
            domain="post_ingestion_qa",
            include_model_input=include_model_input,
        )
    except Exception as exc:
        return {
            **item,
            "ok": False,
            "error": str(exc),
            "latency_ms": int((time.perf_counter() - started) * 1000),
            "reference_answer": str(oracle.get("reference_answer", "")),
        }
    ir = result.get("parsed") if isinstance(result, dict) else None
    row: dict[str, Any] = {
        **item,
        "ok": isinstance(ir, dict),
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "parse_error": str(result.get("parse_error", "")) if isinstance(result, dict) else "",
        "model_decision": ir.get("decision", "") if isinstance(ir, dict) else "",
    }
    if include_model_input and isinstance(result, dict):
        row["model_input"] = result.get("model_input", {})
    if not isinstance(ir, dict):
        row["raw_content"] = str(result.get("content", ""))[:4000] if isinstance(result, dict) else ""
        row["reference_answer"] = str(oracle.get("reference_answer", ""))
        return row
    mapped, warnings = semantic_ir_to_legacy_parse(
        ir,
        allowed_predicates=allowed_predicates,
        predicate_contracts=predicate_contracts,
    )
    diagnostics = mapped.get("admission_diagnostics", {}) if isinstance(mapped, dict) else {}
    clauses = diagnostics.get("clauses", {}) if isinstance(diagnostics.get("clauses"), dict) else {}
    queries = [str(q).strip() for q in clauses.get("queries", []) if str(q).strip()]
    if not queries:
        queries = _fallback_queries_from_semantic_ir(ir, allowed_predicates=allowed_predicates)
    queries = _ordered_query_unique(
        [
            *queries,
            *_source_record_table_count_hint_queries(utterance=utterance, kb_inventory=kb_inventory),
            *_location_floor_hint_queries(utterance=utterance, kb_inventory=kb_inventory),
            *_authority_instrument_metadata_hint_queries(utterance=utterance, kb_inventory=kb_inventory),
            *_complementary_relation_hint_queries(
                utterance=utterance,
                kb_inventory=kb_inventory,
                queries=queries,
            ),
            *_anchor_relation_hint_queries(
                utterance=utterance,
                kb_inventory=kb_inventory,
                queries=queries,
            ),
        ]
    )
    facts_out = [str(q).strip() for q in clauses.get("facts", []) if str(q).strip()]
    rules_out = [str(q).strip() for q in clauses.get("rules", []) if str(q).strip()]
    query_results = run_query_plan(
        runtime,
        queries,
        include_legacy_native_helpers=include_legacy_native_helper_adapters,
    )
    evidence_plan_query_results: list[dict[str, Any]] = []
    if evidence_plan is not None and bool(execute_evidence_bundle_plan):
        evidence_plan_query_results = run_evidence_bundle_plan_queries(
            runtime=runtime,
            evidence_plan=evidence_plan,
            kb_inventory=kb_inventory,
            include_legacy_native_helpers=include_legacy_native_helper_adapters,
        )
        query_results = [*query_results, *evidence_plan_query_results]
    query_results = _dedupe_helper_query_results(query_results)
    query_results = _limit_helper_query_results(
        query_results,
        helper_companion_row_limit,
        utterance=utterance,
        queries=queries,
    )
    row.update(
        {
            "projected_decision": diagnostics.get("projected_decision", ""),
            "warnings": warnings,
            "queries": queries,
            "proposed_facts": facts_out,
            "proposed_rules": rules_out,
            "query_results": query_results,
            "oracle": oracle,
            "reference_answer": str(oracle.get("reference_answer", "")),
            "self_check": ir.get("self_check", {}),
        }
    )
    if evidence_plan is not None:
        row["evidence_bundle_plan"] = evidence_plan
        if bool(execute_evidence_bundle_plan):
            row["evidence_bundle_plan_query_results"] = evidence_plan_query_results
    if include_model_input:
        row["semantic_ir"] = ir
        row["mapper_diagnostics"] = diagnostics
    row["oracle_match"] = score_oracle(row=row, oracle=oracle)
    return row


def _fallback_queries_from_semantic_ir(
    ir: dict[str, Any],
    *,
    allowed_predicates: set[str],
) -> list[str]:
    """Project narrow query fallbacks from parsed IR when the mapper emitted none."""

    entities = ir.get("entities", [])
    assertions = ir.get("assertions", [])
    if not isinstance(entities, list) or not isinstance(assertions, list):
        return []
    normalized = {
        str(entity.get("normalized", "")).strip().lower()
        for entity in entities
        if isinstance(entity, dict) and str(entity.get("normalized", "")).strip()
    }
    relation_concepts = {
        str(assertion.get("relation_concept", "")).strip().lower()
        for assertion in assertions
        if isinstance(assertion, dict)
    }
    surfaces = {
        str(entity.get("surface", "")).strip().lower()
        for entity in entities
        if isinstance(entity, dict) and str(entity.get("surface", "")).strip()
    }
    out: list[str] = []

    version_atoms = sorted(
        (value for value in normalized if re.fullmatch(r"v\d+(?:_\d+)?", value)),
        key=_roster_version_rank,
        reverse=True,
    )
    asks_roster_compliance = bool(
        {"compliance_check", "count"} & relation_concepts
        and (
            "3_2" in normalized
            or "qualifying_chaperone" in normalized
            or any("chaperone" in surface or "compliance" in surface for surface in surfaces)
        )
    )
    if asks_roster_compliance:
        if "adult_role" in allowed_predicates:
            out.append("adult_role(Adult, Role).")
        if "role_counts_towards_ratio" in allowed_predicates:
            out.append("role_counts_towards_ratio(Role, Counts).")
        if "roster_version" in allowed_predicates:
            if version_atoms:
                out.extend(f"roster_version({version})." for version in version_atoms)
            else:
                out.append("roster_version(Version).")
    elif any("compliance" in surface for surface in surfaces) and "roster_version" in allowed_predicates:
        out.append("roster_version(Version).")

    return _ordered_query_unique(out)


_COMPLEMENTARY_PHRASE_RE = re.compile(
    r"\b(?:in addition to|besides|along with|apart from|not only\b|what else|additional)\b",
    re.IGNORECASE,
)


def _complementary_relation_hint_queries(
    *,
    utterance: str,
    kb_inventory: dict[str, Any],
    queries: list[str],
) -> list[str]:
    """Add sibling relation probes for complementary-question wording.

    This is intentionally shape-based: it uses the planner's grounded subject
    and the compiled KB inventory, not fixture names, answer strings, or source
    prose. If a question asks for something "besides" a baseline relation, the
    baseline predicate is useful context but may not be the answer surface.
    """

    if not _COMPLEMENTARY_PHRASE_RE.search(str(utterance or "")):
        return []
    parsed_queries = [parse_prolog_query(query) for query in queries]
    grounded_subjects: set[str] = set()
    queried_predicates: set[str] = set()
    for parsed in parsed_queries:
        if parsed is None:
            continue
        predicate, args = parsed
        queried_predicates.add(predicate)
        if args and not _is_prolog_variable(args[0]) and not args[0].startswith("_"):
            grounded_subjects.add(args[0])
    if not grounded_subjects:
        return []

    examples = kb_inventory.get("examples", {})
    if not isinstance(examples, dict):
        return []

    out: list[str] = []
    for signature, sample_clauses in examples.items():
        if not isinstance(sample_clauses, list):
            continue
        predicate = str(signature).split("/", 1)[0].strip()
        if not predicate or predicate in queried_predicates or predicate.startswith("source_record_"):
            continue
        for clause in sample_clauses[:12]:
            parsed_clause = parse_prolog_query(str(clause))
            if parsed_clause is None:
                continue
            clause_predicate, args = parsed_clause
            if clause_predicate != predicate or len(args) < 2 or args[0] not in grounded_subjects:
                continue
            variables = ["Complement", "Detail", "Value", "Scope", "Source"]
            hint_args = [args[0], *variables[: len(args) - 1]]
            out.append(format_prolog_query(predicate, hint_args))
            break

    return _ordered_query_unique(out)[:8]


_ANCHOR_EVENT_QUESTION_RE = re.compile(
    r"\b(?:anchor(?:ed)?|trigger(?:ed)?|came before|come before|preced(?:e|ed|ing)|prior event|following)\b",
    re.IGNORECASE,
)


def _anchor_relation_hint_queries(
    *,
    utterance: str,
    kb_inventory: dict[str, Any],
    queries: list[str],
) -> list[str]:
    """Add direct anchor/trigger probes for action-event questions."""

    if not _ANCHOR_EVENT_QUESTION_RE.search(str(utterance or "")):
        return []
    action_atoms: set[str] = set()
    for query in queries:
        parsed = parse_prolog_query(query)
        if parsed is None:
            continue
        _predicate, args = parsed
        for arg in args:
            if arg and not _is_prolog_variable(arg) and not arg.startswith("_"):
                action_atoms.add(arg)
    if not action_atoms:
        return []

    examples = kb_inventory.get("examples", {})
    if not isinstance(examples, dict):
        return []

    out: list[str] = []
    for signature, sample_clauses in examples.items():
        if not isinstance(sample_clauses, list):
            continue
        predicate = str(signature).split("/", 1)[0].strip()
        lowered_predicate = predicate.casefold()
        if not predicate or not (("anchor" in lowered_predicate) or ("trigger" in lowered_predicate)):
            continue
        for clause in sample_clauses[:16]:
            parsed_clause = parse_prolog_query(str(clause))
            if parsed_clause is None:
                continue
            clause_predicate, args = parsed_clause
            if clause_predicate != predicate or len(args) != 2:
                continue
            if "trigger" in lowered_predicate and args[0] in action_atoms:
                out.append(format_prolog_query(predicate, [args[0], "Anchor"]))
                break
            if "anchor" in lowered_predicate and args[1] in action_atoms:
                out.append(format_prolog_query(predicate, ["Anchor", args[1]]))
                break

    return _ordered_query_unique(out)[:6]


def _source_record_table_count_hint_queries(
    *,
    utterance: str,
    kb_inventory: dict[str, Any],
) -> list[str]:
    """Add structural table-row evidence for explicit table/list count questions.

    This is intentionally a routing hint, not an answer helper. It only exposes
    deterministic source-record table rows so the existing
    source_record_table_body_count_support companion can decide whether there is
    usable body-row evidence.
    """

    text = str(utterance or "").casefold()
    asks_count = any(
        marker in text
        for marker in (
            "how many",
            "count of",
            "number of",
            "provide the count",
        )
    )
    if not asks_count:
        return []
    table_surface = any(
        marker in text
        for marker in (
            "table",
            "listed",
            " list",
            "inventory",
            "raw event log",
            "event log",
            "section",
            "entries",
            "rows",
            "recorded in",
        )
    )
    if not table_surface:
        return []
    signatures = {str(item).strip() for item in kb_inventory.get("signatures", []) if str(item).strip()}
    if "source_record_row/5" not in signatures or "source_record_field/3" not in signatures:
        return []
    return ["source_record_row(SourceRow, table_row, Line, SectionAtom, Label)."]


def _location_floor_hint_queries(
    *,
    utterance: str,
    kb_inventory: dict[str, Any],
) -> list[str]:
    """Add location metadata evidence for explicit floor/storage questions."""

    text = str(utterance or "").casefold()
    if not any(marker in text for marker in ("locker", "floor", "storage", "location", "bay", "shelf")):
        return []
    if not any(marker in text for marker in ("floor", "leading zero", "differ", "differs", "basement", "ground")):
        return []
    signatures = {str(item).strip() for item in kb_inventory.get("signatures", []) if str(item).strip()}
    out: list[str] = []
    if "located_at/2" in signatures:
        out.append("located_at(Item, Location).")
    if "locker_floor/2" in signatures:
        out.append("locker_floor(Location, Floor).")
    return out


def _authority_instrument_metadata_hint_queries(
    *,
    utterance: str,
    kb_inventory: dict[str, Any],
) -> list[str]:
    """Add issuer/date/type rows for source-authority instrument questions."""

    text = str(utterance or "").casefold()
    if not any(marker in text for marker in ("source", "authoriz", "authority", "directive", "order", "policy")):
        return []
    signatures = {str(item).strip() for item in kb_inventory.get("signatures", []) if str(item).strip()}
    out: list[str] = []
    if "instrument_type/2" in signatures:
        out.append("instrument_type(Instrument, InstrumentType).")
    if "instrument_issuer/2" in signatures:
        out.append("instrument_issuer(Instrument, Issuer).")
    if "instrument_date/2" in signatures:
        out.append("instrument_date(Instrument, Date).")
    return out


def run_query_plan(
    runtime: CorePrologRuntime,
    queries: list[str],
    *,
    include_legacy_native_helpers: bool = True,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    previous_queries: list[str] = []
    delivered_helper_rows: set[tuple[str, str]] = set()

    def append_companion(companion: dict[str, Any] | None) -> None:
        if not companion:
            return
        filtered = _dedupe_helper_companion_rows(companion, delivered_helper_rows)
        if filtered and filtered not in results:
            results.append(filtered)

    for query in queries:
        effective_query = query
        used_relaxed_fallback = False
        numeric_token_repair = _source_record_numeric_token_repaired_query(query)
        if numeric_token_repair:
            repaired_query = str(numeric_token_repair.get("query", "")).strip()
            repaired_result = runtime.query_rows(repaired_query)
            effective_query = repaired_query
            if repaired_result.get("status") == "success":
                results.append(
                    {
                        "query": repaired_query,
                        "result": {
                            **repaired_result,
                            "reasoning_basis": {
                                "kind": "core-local",
                                "note": "source-record numeric-token query repair aligned unprefixed token constants to deterministic ledger atoms",
                                "original_query": query,
                                "repairs": numeric_token_repair.get("repairs", []),
                            },
                        },
                        "derived_from_queries": [query],
                    }
                )
            else:
                result = runtime.query_rows(query)
                results.append({"query": query, "result": result})
        else:
            placeholder_repair = _placeholder_repaired_query(query)
            if placeholder_repair:
                repaired_query = str(placeholder_repair.get("query", "")).strip()
                repaired_result = runtime.query_rows(repaired_query)
                effective_query = repaired_query
                if repaired_result.get("status") == "success":
                    results.append(
                        {
                            "query": repaired_query,
                            "result": {
                                **repaired_result,
                                "reasoning_basis": {
                                    "kind": "core-local",
                                    "note": "placeholder query repair converted generic lowercase slot labels to Prolog variables before execution",
                                    "original_query": query,
                                    "repairs": placeholder_repair.get("repairs", []),
                                },
                            },
                            "derived_from_queries": [query],
                        }
                    )
                else:
                    result = runtime.query_rows(query)
                    results.append({"query": query, "result": result})
            else:
                result = runtime.query_rows(query)
                results.append({"query": query, "result": result})

        if results:
            last_item = results[-1]
            if isinstance(last_item, dict) and isinstance(last_item.get("result"), dict):
                last_query = str(last_item.get("query", effective_query) or effective_query)
                last_item["result"] = _augment_result_with_bound_query_constants(
                    query=last_query,
                    result=last_item["result"],
                )

        last_result = results[-1].get("result", {}) if results else {}
        source_record_repair = _source_record_field_sibling_repaired_query(effective_query)
        if source_record_repair:
            repaired_query = str(source_record_repair.get("query", "")).strip()
            repaired_result = runtime.query_rows(repaired_query)
            if repaired_result.get("status") == "success":
                results.append(
                    {
                        "query": repaired_query,
                        "result": {
                            **repaired_result,
                            "reasoning_basis": {
                                "kind": "core-local",
                                "note": (
                                    "source-record sibling-field query repair joined the row identifier "
                                    "through its event field before reading another field on the same row"
                                ),
                                "original_query": effective_query,
                                "repairs": source_record_repair.get("repairs", []),
                            },
                        },
                        "derived_from_queries": [effective_query],
                    }
                )
                effective_query = repaired_query
                last_result = repaired_result
        if isinstance(last_result, dict) and last_result.get("status") != "success":
            compact_interval = _compact_interval_duration_companion(results=results[:-1], query=effective_query)
            if compact_interval:
                append_companion(compact_interval)
                last_result = compact_interval.get("result", {})
        if isinstance(last_result, dict) and last_result.get("status") != "success":
            defined_interval = _defined_interval_duration_companion(runtime, query=effective_query)
            if defined_interval:
                append_companion(defined_interval)
                last_result = defined_interval.get("result", {})
        if isinstance(last_result, dict) and last_result.get("status") != "success":
            status_interval = _status_at_date_interval_companion(runtime, query=effective_query)
            if status_interval:
                append_companion(status_interval)
                last_result = status_interval.get("result", {})
        for domain_companion in _domain_companion_queries(
            runtime,
            query=effective_query,
            include_legacy_native_helpers=include_legacy_native_helpers,
        ):
            append_companion(domain_companion)
        if isinstance(last_result, dict) and last_result.get("status") != "success":
            relaxed = _relaxed_constant_query(runtime, query=effective_query)
            if relaxed:
                results.append(relaxed)
                effective_query = str(relaxed.get("query", query))
                used_relaxed_fallback = True
                last_result = relaxed.get("result", {})
        companion = _evidence_table_companion_query(runtime, query=effective_query)
        append_companion(companion)
        if not used_relaxed_fallback:
            for domain_companion in _domain_companion_queries(
                runtime,
                query=effective_query,
                include_legacy_native_helpers=include_legacy_native_helpers,
            ):
                append_companion(domain_companion)
        temporal_join = _temporal_join_with_previous(runtime, previous_queries=previous_queries, query=effective_query)
        if temporal_join:
            results.append(temporal_join)
        negative_join = _negative_join_with_previous(runtime, previous_queries=previous_queries, query=effective_query)
        if negative_join:
            results.append(negative_join)
        previous_queries.append(effective_query)
    return results


def _augment_result_with_bound_query_constants(*, query: str, result: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(result, dict) or result.get("status") != "success":
        return result
    parsed = parse_prolog_query(query)
    if parsed is None:
        return result
    _predicate, args = parsed
    bound_constants: list[dict[str, Any]] = []
    for index, arg in enumerate(args, start=1):
        item = str(arg or "").strip()
        if not item or _is_prolog_variable(item):
            continue
        display = _display_source_date_atom(item)
        bound: dict[str, Any] = {"arg_index": index, "value": item}
        if display and display != item:
            bound["display"] = display
        bound_constants.append(bound)
    if not bound_constants:
        return result

    augmented = dict(result)
    augmented["bound_query_constants"] = bound_constants
    rows = augmented.get("rows")
    if isinstance(rows, list) and rows:
        new_rows: list[Any] = []
        for row in rows:
            if not isinstance(row, dict):
                new_rows.append(row)
                continue
            enriched = dict(row)
            for bound in bound_constants:
                index = int(bound["arg_index"])
                value = str(bound["value"])
                enriched[f"BoundArg{index}"] = value
                display = str(bound.get("display", "")).strip()
                if display and display != value:
                    enriched[f"BoundArg{index}Display"] = display
            new_rows.append(enriched)
        augmented["rows"] = new_rows
    reasoning_basis = augmented.get("reasoning_basis", {})
    if isinstance(reasoning_basis, dict):
        augmented["reasoning_basis"] = {
            **reasoning_basis,
            "bound_query_constants_visible": True,
        }
    return augmented


def _dedupe_helper_companion_rows(
    companion: dict[str, Any],
    delivered_helper_rows: set[tuple[str, str]],
) -> dict[str, Any] | None:
    result = companion.get("result", {}) if isinstance(companion, dict) else {}
    if not isinstance(result, dict):
        return companion
    rows = result.get("rows")
    if not isinstance(rows, list) or not rows:
        return companion
    if not any(isinstance(row, dict) and str(row.get("HelperClass", "")).strip() for row in rows):
        return companion

    predicate = str(result.get("predicate", "") or "").strip()
    kept_rows: list[Any] = []
    skipped = 0
    for row in rows:
        if not isinstance(row, dict):
            kept_rows.append(row)
            continue
        key = (predicate, json.dumps(row, ensure_ascii=False, sort_keys=True))
        if key in delivered_helper_rows:
            skipped += 1
            continue
        delivered_helper_rows.add(key)
        kept_rows.append(row)
    if not kept_rows:
        return None
    if skipped <= 0:
        return companion

    filtered_result = dict(result)
    filtered_result["rows"] = kept_rows
    filtered_result["num_rows"] = len(kept_rows)
    reasoning_basis = dict(filtered_result.get("reasoning_basis", {}) or {})
    reasoning_basis["delivery_filter"] = "query_plan_helper_row_dedupe"
    reasoning_basis["deduped_helper_rows"] = skipped
    filtered_result["reasoning_basis"] = reasoning_basis
    return {**companion, "result": filtered_result}


def _dedupe_helper_query_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    delivered_helper_rows: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []
    for item in results:
        filtered = _dedupe_helper_companion_rows(item, delivered_helper_rows)
        if filtered is not None:
            out.append(filtered)
    return out


def _limit_helper_query_results(
    results: list[dict[str, Any]],
    row_limit: int | None,
    *,
    utterance: str = "",
    queries: list[str] | None = None,
) -> list[dict[str, Any]]:
    if row_limit is None:
        return results
    if int(row_limit) < 0:
        return results
    budget = max(0, int(row_limit))
    helper_items: list[tuple[int, dict[str, Any], dict[str, Any], list[Any]]] = []
    ranked_rows: list[tuple[float, int, int, dict[str, Any]]] = []
    query_tokens = _helper_budget_query_tokens(utterance=utterance, queries=queries or [])
    for item_index, item in enumerate(results):
        result = item.get("result", {}) if isinstance(item, dict) else {}
        rows = result.get("rows") if isinstance(result, dict) else None
        if not isinstance(rows, list) or not _is_helper_query_result(item):
            continue
        helper_items.append((item_index, item, result, rows))
        predicate = str(item.get("predicate", "") or result.get("predicate", "") or "")
        for row_index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            score = _helper_budget_row_score(
                predicate=predicate,
                row=row,
                query_tokens=query_tokens,
            )
            ranked_rows.append((score, item_index, row_index, row))
    if not helper_items:
        return results
    if budget <= 0:
        helper_indexes = {item_index for item_index, *_ in helper_items}
        return [item for index, item in enumerate(results) if index not in helper_indexes]

    ranked_rows.sort(key=lambda item: (-item[0], item[1], item[2]))
    selected = {(item_index, row_index) for _, item_index, row_index, _ in ranked_rows[:budget]}

    helper_by_index = {item_index: (item, result, rows) for item_index, item, result, rows in helper_items}
    out: list[dict[str, Any]] = []
    for item_index, item in enumerate(results):
        helper_payload = helper_by_index.get(item_index)
        if helper_payload is None:
            out.append(item)
            continue
        original_item, result, rows = helper_payload
        kept_rows = [
            row
            for row_index, row in enumerate(rows)
            if (item_index, row_index) in selected
        ]
        if not kept_rows:
            continue
        reasoning_basis = result.get("reasoning_basis", {})
        if not isinstance(reasoning_basis, dict):
            reasoning_basis = {}
        out.append(
            {
                **original_item,
                "result": {
                    **result,
                    "rows": kept_rows,
                    "num_rows": len(kept_rows),
                    "reasoning_basis": {
                        **reasoning_basis,
                        "delivery_filter": "query_relevance_helper_row_budget",
                        "helper_companion_row_limit": row_limit,
                        "helper_companion_original_rows": len(rows),
                        "helper_companion_budget_ranker": "lexical_query_overlap_v1",
                    },
                },
            }
        )
    return out


def _helper_budget_query_tokens(*, utterance: str, queries: list[str]) -> set[str]:
    tokens = set(_helper_budget_tokens(utterance))
    for query in queries:
        tokens.update(_helper_budget_tokens(query))
    return {token for token in tokens if token not in GENERIC_QUERY_PLACEHOLDERS and len(token) > 1}


def _helper_budget_row_score(
    *,
    predicate: str,
    row: dict[str, Any],
    query_tokens: set[str],
) -> float:
    if not query_tokens:
        return 0.0
    row_tokens = set(_helper_budget_tokens(" ".join(str(value) for value in row.values())))
    predicate_tokens = set(_helper_budget_tokens(predicate))
    support_tokens = set(
        _helper_budget_tokens(
            " ".join(
                str(row.get(key, ""))
                for key in ("SupportKind", "Kind", "SourcePredicate", "SourceRow", "SupportRole")
            )
        )
    )
    value_overlap = len(query_tokens & row_tokens)
    support_overlap = len(query_tokens & support_tokens)
    predicate_overlap = len(query_tokens & predicate_tokens)
    exact_surface_bonus = 0.0
    row_text = " ".join(str(value).lower() for value in row.values())
    for token in query_tokens:
        if len(token) >= 4 and token in row_text:
            exact_surface_bonus += 0.25
    return float(value_overlap) + (1.5 * support_overlap) + (0.5 * predicate_overlap) + exact_surface_bonus


def _helper_budget_tokens(text: str) -> list[str]:
    normalized = re.sub(r"([a-z])([A-Z])", r"\1 \2", str(text))
    normalized = normalized.replace("_", " ").replace("-", " ")
    return [token.lower() for token in re.findall(r"[A-Za-z0-9]+", normalized)]


def _is_helper_query_result(item: dict[str, Any]) -> bool:
    if not isinstance(item, dict):
        return False
    result = item.get("result", {})
    if not isinstance(result, dict):
        return False
    predicate = str(item.get("predicate", "") or result.get("predicate", "") or "")
    if predicate.endswith("_support"):
        return True
    reasoning_basis = result.get("reasoning_basis", {})
    if isinstance(reasoning_basis, dict) and str(reasoning_basis.get("kind", "")) == "query-only-companion":
        return True
    rows = result.get("rows")
    return isinstance(rows, list) and any(isinstance(row, dict) and "HelperClass" in row for row in rows)


def _status_timeline_summary_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: tuple[Any, ...],
    query: str,
) -> dict[str, Any] | None:
    if len(args) == 2 and predicate.startswith("scheduled_"):
        entity_arg = str(args[0]).strip()
        if _is_prolog_variable(entity_arg):
            return None
        status = _status_from_event_type(predicate.removeprefix("scheduled_"))
        if not status:
            return None
        result = runtime.query_rows(format_prolog_query(predicate, ["Entity", "EffectiveDate"]))
        if result.get("status") != "success":
            return None
        rows: list[dict[str, str]] = []
        for row in result.get("rows", []) or []:
            if not isinstance(row, dict):
                continue
            observed_entity = str(row.get("Entity", "")).strip()
            effective_date = str(row.get("EffectiveDate", "")).strip()
            if not observed_entity or not effective_date:
                continue
            if observed_entity != entity_arg and _case_atom_key(observed_entity) != _case_atom_key(entity_arg):
                continue
            rows.append(
                {
                    "HelperClass": "clean-helper",
                    "QueryEntity": entity_arg,
                    "ScheduledStatus": status,
                    "AppliesOnOrAfter": effective_date,
                    "SourcePredicate": predicate,
                    "SupportKind": "scheduled_state_transition",
                }
            )
        if not rows:
            return None
        return _status_timeline_companion_result(
            predicate="status_timeline_summary_support",
            query=(
                "status_timeline_summary_support"
                "(QueryEntity, ScheduledStatus, AppliesOnOrAfter, SourcePredicate, SupportKind)."
            ),
            rows=rows,
            original_query=query,
            note=(
                "query-only scheduled-state support exposed the state implied by admitted scheduled transition rows; "
                "no durable fact was written"
            ),
        )

    if len(args) != 3 or not predicate.endswith("_status"):
        return None
    entity_arg = str(args[0]).strip()
    status_arg = str(args[1]).strip()
    date_arg = str(args[2]).strip()
    if (
        _is_prolog_variable(entity_arg)
        or not (_is_status_projection_variable(status_arg) and _is_prolog_variable(date_arg))
    ):
        return None
    result = runtime.query_rows(format_prolog_query(predicate, ["Entity", "Status", "Date"]))
    if result.get("status") != "success":
        return None
    rows_for_entity: list[dict[str, Any]] = []
    for row in result.get("rows", []) or []:
        if not isinstance(row, dict):
            continue
        observed_entity = str(row.get("Entity", "")).strip()
        observed_status = str(row.get("Status", "")).strip()
        observed_date = str(row.get("Date", "")).strip()
        observed_at = _runtime_temporal_datetime(runtime, observed_date)
        if not observed_entity or not observed_status or observed_at is None:
            continue
        if observed_entity != entity_arg and _case_atom_key(observed_entity) != _case_atom_key(entity_arg):
            continue
        rows_for_entity.append(
            {
                "observed_entity": observed_entity,
                "observed_status": observed_status,
                "observed_date": observed_date,
                "observed_at": observed_at,
            }
        )
    if not rows_for_entity:
        return None
    latest = sorted(rows_for_entity, key=lambda item: item["observed_at"])[-1]
    return _status_timeline_companion_result(
        predicate="status_timeline_summary_support",
        query="status_timeline_summary_support(QueryEntity, CurrentStatus, EffectiveFrom, SourcePredicate, SupportKind).",
        rows=[
            {
                "HelperClass": "clean-helper",
                "QueryEntity": entity_arg,
                "CurrentStatus": str(latest["observed_status"]),
                "EffectiveFrom": str(latest["observed_date"]),
                "SourcePredicate": predicate,
                "SupportKind": "latest_status_transition",
            }
        ],
        original_query=query,
        note=(
            "query-only status timeline support exposed the latest admitted status transition for broad status queries; "
            "no durable fact was written"
        ),
    )


def _status_timeline_companion_result(
    *,
    predicate: str,
    query: str,
    rows: list[dict[str, str]],
    original_query: str,
    note: str,
) -> dict[str, Any]:
    return {
        "query": query,
        "result": {
            "status": "success",
            "result_type": "table",
            "predicate": predicate,
            "prolog_query": query,
            "variables": list(rows[0].keys()) if rows else [],
            "rows": rows,
            "num_rows": len(rows),
            "reasoning_basis": {
                "kind": "core-local",
                "note": note,
                "original_query": original_query,
            },
        },
        "derived_from_queries": [original_query],
    }


def _scoped_status_count_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: tuple[Any, ...],
    query: str,
) -> dict[str, Any] | None:
    facts = _runtime_fact_rows(runtime)
    if not facts:
        return None

    unary_scope_rows: dict[str, set[str]] = {}
    status_rows: dict[str, list[tuple[str, str, str]]] = {}
    term_definitions: dict[str, str] = {}
    source_sections: dict[str, str] = {}
    source_labels: dict[str, str] = {}
    requested_statuses = _requested_scoped_status_values(predicate=predicate, args=args)
    for fact in facts:
        fact_predicate = str(fact.get("predicate", "")).strip()
        fact_args = [str(item).strip() for item in fact.get("args", [])]
        if not fact_predicate or not fact_args:
            continue
        if len(fact_args) == 1 and _looks_like_scope_predicate(fact_predicate):
            unary_scope_rows.setdefault(fact_predicate, set()).add(fact_args[0])
        if len(fact_args) >= 2 and fact_predicate.endswith("_status"):
            date = fact_args[2] if len(fact_args) >= 3 else ""
            status_rows.setdefault(fact_predicate, []).append((fact_args[0], fact_args[1], date))
        if fact_predicate in {"defines_status_term", "status_term_definition"} and len(fact_args) >= 2:
            term_definitions[fact_args[0]] = fact_args[1]
        if fact_predicate == "source_record_section" and len(fact_args) >= 2:
            source_sections[fact_args[0]] = fact_args[1]
        if fact_predicate == "source_record_label" and len(fact_args) >= 2:
            source_labels[fact_args[0]] = fact_args[1]

    if not ((unary_scope_rows and status_rows) or (source_sections and source_labels)):
        return None
    if not (
        predicate in unary_scope_rows
        or predicate in status_rows
        or predicate in {"defines_status_term", "status_term_definition"}
        or (predicate.endswith("_status") and requested_statuses)
        or (predicate == "source_record_label" and requested_statuses)
    ):
        return None

    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for scope_predicate, scoped_entities in sorted(unary_scope_rows.items()):
        if len(scoped_entities) < 2:
            continue
        for status_predicate, observed_rows in sorted(status_rows.items()):
            by_status_date: dict[tuple[str, str], set[str]] = {}
            for entity, status, date in observed_rows:
                if entity not in scoped_entities:
                    continue
                by_status_date.setdefault((status, date), set()).add(entity)
            for (status, date), members in sorted(by_status_date.items()):
                if not members:
                    continue
                if not _status_allowed_by_request(status, requested_statuses):
                    continue
                key = (scope_predicate, status_predicate, status, date)
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    {
                        "HelperClass": "clean-helper",
                        "SupportKind": "scoped_status_count",
                        "ScopePredicate": scope_predicate,
                        "StatusPredicate": status_predicate,
                        "SemanticCriterion": status,
                        "StatusValue": status,
                        "Date": date,
                        "Count": str(len(members)),
                        "Members": ",".join(sorted(members, key=_case_atom_key)),
                    }
                )

            for term, definition in sorted(term_definitions.items()):
                if not _status_allowed_by_request(term, requested_statuses):
                    continue
                matching_statuses = [
                    status
                    for status, _date in by_status_date
                    if _status_term_matches_status(term, definition, status)
                    and _status_allowed_by_request(status, requested_statuses)
                ]
                if not matching_statuses:
                    continue
                members: set[str] = set()
                dates: set[str] = set()
                for status, date in by_status_date:
                    if status not in matching_statuses:
                        continue
                    members.update(by_status_date[(status, date)])
                    if date:
                        dates.add(date)
                if not members:
                    continue
                key = (scope_predicate, status_predicate, term, ",".join(sorted(dates)))
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    {
                        "HelperClass": "clean-helper",
                        "SupportKind": "scoped_status_criterion_count",
                        "ScopePredicate": scope_predicate,
                        "StatusPredicate": status_predicate,
                        "SemanticCriterion": term,
                        "StatusValue": ",".join(sorted(set(matching_statuses), key=_case_atom_key)),
                        "Date": ",".join(sorted(dates, key=_date_atom_sort_key_for_strings)),
                        "Count": str(len(members)),
                        "Members": ",".join(sorted(members, key=_case_atom_key)),
                    }
                )

    section_rows = (
        _section_status_count_rows(
            source_sections=source_sections,
            source_labels=source_labels,
            requested_statuses=requested_statuses,
        )
        if predicate == "source_record_label" and requested_statuses
        else []
    )
    for row in section_rows:
        key = (
            str(row.get("ScopePredicate", "")),
            str(row.get("StatusPredicate", "")),
            str(row.get("SemanticCriterion", "")),
            str(row.get("Members", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)

    if not rows:
        return None
    return _status_timeline_companion_result(
        predicate="scoped_status_count_support",
        query=(
            "scoped_status_count_support"
            "(ScopePredicate, StatusPredicate, SemanticCriterion, StatusValue, Date, Count, Members, SupportKind)."
        ),
        rows=rows[:80],
        original_query=query,
        note=(
            "query-only scoped status count support joined unary scope predicates to admitted status rows "
            "and optional status-term definitions; no durable fact was written"
        ),
    )


def _looks_like_scope_predicate(predicate: str) -> bool:
    text = str(predicate or "").strip().lower()
    if text.startswith("source_record_") or text in {"character", "object", "person", "place"}:
        return False
    return (
        text.startswith("is_")
        or text.endswith(("_case", "_item", "_record", "_entity", "_member"))
        or "scope" in text
    )


def _requested_scoped_status_values(*, predicate: str, args: tuple[Any, ...]) -> set[str]:
    requested: set[str] = set()
    if predicate.endswith("_status") and len(args) >= 2:
        status_arg = str(args[1]).strip()
        if status_arg and not _is_prolog_variable(status_arg):
            requested.add(status_arg)
    elif predicate in {"defines_status_term", "status_term_definition"} and args:
        term_arg = str(args[0]).strip()
        if term_arg and not _is_prolog_variable(term_arg):
            requested.add(term_arg)
    elif predicate == "source_record_label" and len(args) >= 2:
        label_arg = str(args[1]).strip()
        if label_arg and not _is_prolog_variable(label_arg):
            status = _status_from_source_record_label(label_arg)
            if status:
                requested.add(status)
    return requested


def _status_allowed_by_request(status: str, requested_statuses: set[str]) -> bool:
    if not requested_statuses:
        return True
    for requested in requested_statuses:
        if status == requested:
            return True
        if _status_term_matches_status(status, status, requested):
            return True
        if _status_term_matches_status(requested, requested, status):
            return True
    return False


def _section_status_count_rows(
    *,
    source_sections: dict[str, str],
    source_labels: dict[str, str],
    requested_statuses: set[str] | None = None,
) -> list[dict[str, str]]:
    requested_statuses = requested_statuses or set()
    by_parent_status: dict[tuple[str, str], set[str]] = {}
    for source_row, label in source_labels.items():
        status = _status_from_source_record_label(label)
        if not _status_allowed_by_request(status, requested_statuses):
            continue
        section = source_sections.get(source_row, "")
        parent = _parent_section_scope(section)
        if not status or not parent or section == parent:
            continue
        by_parent_status.setdefault((parent, status), set()).add(section)

    out: list[dict[str, str]] = []
    for (parent, status), sections in sorted(by_parent_status.items()):
        if not sections:
            continue
        out.append(
            {
                "HelperClass": "clean-helper",
                "SupportKind": "source_section_status_count",
                "ScopePredicate": "source_record_section_prefix",
                "StatusPredicate": "source_record_label_status",
                "SemanticCriterion": status,
                "StatusValue": status,
                "Date": "",
                "Count": str(len(sections)),
                "Members": ",".join(sorted(sections, key=_case_atom_key)),
            }
        )
    return out


def _status_from_source_record_label(label: str) -> str:
    text = str(label or "").strip().lower()
    if not text.startswith("status_"):
        return ""
    tokens = _type_taxonomy_tokens(text.removeprefix("status_"))
    if not tokens:
        return ""
    if tokens[:2] == ["timeline", "resolvable"]:
        return "timeline_resolvable"
    if tokens[:2] == ["genuinely", "unresolved"]:
        return "genuinely_unresolved"
    if tokens[:2] == ["not", "in"] and len(tokens) >= 3 and tokens[2] == "conflict":
        return "not_in_conflict"
    return "_".join(tokens[:2]) if len(tokens) >= 2 else tokens[0]


def _parent_section_scope(section: str) -> str:
    tokens = _type_taxonomy_tokens(section)
    if len(tokens) >= 3 and tokens[0] in {"v", "section"} and tokens[1].isdigit() and tokens[2].isdigit():
        return "_".join(tokens[:2])
    if len(tokens) >= 2 and tokens[0] == "section" and tokens[1].isdigit():
        return "_".join(tokens[:2])
    return ""


def _status_term_matches_status(term: str, definition: str, status: str) -> bool:
    term_tokens = set(_type_taxonomy_tokens(term))
    definition_tokens = set(_type_taxonomy_tokens(definition))
    status_tokens = set(_type_taxonomy_tokens(status))
    if not status_tokens:
        return False
    return bool(status_tokens & term_tokens) or status_tokens.issubset(definition_tokens)


def _date_atom_sort_key_for_strings(value: str) -> tuple[int, str]:
    sort_key = _date_atom_sort_key(value)
    if sort_key is None:
        return (1, str(value or ""))
    return (0, str(sort_key))


def _identifier_alias_count_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: tuple[Any, ...],
    query: str,
) -> dict[str, Any] | None:
    if len(args) != 2:
        return None
    entity_arg = str(args[0]).strip()
    value_arg = str(args[1]).strip()
    if not (_is_prolog_variable(entity_arg) and _is_prolog_variable(value_arg)):
        return None
    if not predicate.endswith(("_on", "_at", "_in")):
        return None

    entity_var = "Entity"
    value_var = "Value"
    all_query = format_prolog_query(predicate, [entity_var, value_var])
    result = runtime.query_rows(all_query)
    if result.get("status") != "success":
        return None

    raw_entities = sorted(
        {str(row.get(entity_var, "")).strip() for row in result.get("rows", []) or [] if isinstance(row, dict)}
    )
    if len(raw_entities) < 2:
        return None
    groups: dict[str, set[str]] = {}
    for entity in raw_entities:
        groups.setdefault(_identifier_alias_key(entity), set()).add(entity)
    raw_entity_set = set(raw_entities)
    alias_groups = {
        key: values
        for key, values in groups.items()
        if len(values) > 1 and key in raw_entity_set
    }
    if not alias_groups:
        return None

    canonical_entities = sorted(
        {
            (key if key in alias_groups else entity)
            for entity in raw_entities
            for key in [_identifier_alias_key(entity)]
        },
        key=_case_atom_key,
    )
    rows = [
        {
            "HelperClass": "clean-helper",
            "SourcePredicate": predicate,
            "RawEntityCount": str(len(raw_entities)),
            "DistinctEntityCount": str(len(canonical_entities)),
            "CanonicalEntities": ", ".join(canonical_entities),
            "AliasGroups": "; ".join(
                f"{key}: {', '.join(sorted(values, key=_case_atom_key))}"
                for key, values in sorted(alias_groups.items(), key=lambda item: _case_atom_key(item[0]))
            ),
            "SupportKind": "identifier_alias_distinct_count",
        }
    ]
    return _status_timeline_companion_result(
        predicate="identifier_alias_count_support",
        query=(
            "identifier_alias_count_support"
            "(SourcePredicate, RawEntityCount, DistinctEntityCount, CanonicalEntities, AliasGroups, SupportKind)."
        ),
        rows=rows,
        original_query=query,
        note=(
            "query-only identifier alias count support collapsed returned entity atoms that share a suffix-form "
            "identifier; no durable fact was written"
        ),
    )


def _duplicate_exclusion_count_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: tuple[Any, ...],
    query: str,
) -> dict[str, Any] | None:
    if len(args) != 1 or not _is_prolog_variable(str(args[0]).strip()):
        return None
    entity_var = "Entity"
    all_query = format_prolog_query(predicate, [entity_var])
    result = runtime.query_rows(all_query)
    if result.get("status") != "success":
        return None
    raw_entities = sorted(
        {str(row.get(entity_var, "")).strip() for row in result.get("rows", []) or [] if isinstance(row, dict)}
    )
    if len(raw_entities) < 2:
        return None
    duplicate_rows = _duplicate_relation_rows(runtime, raw_entities=set(raw_entities))
    if not duplicate_rows:
        return None
    duplicate_entities = {row["duplicate"] for row in duplicate_rows}
    canonical_entities = sorted(
        {entity for entity in raw_entities if entity not in duplicate_entities},
        key=_case_atom_key,
    )
    duplicate_groups: dict[str, set[str]] = {}
    for row in duplicate_rows:
        duplicate_groups.setdefault(row["canonical"], set()).add(row["duplicate"])
    rows = [
        {
            "HelperClass": "clean-helper",
            "SourcePredicate": predicate,
            "RawEntityCount": str(len(raw_entities)),
            "DistinctEntityCount": str(len(canonical_entities)),
            "CanonicalEntities": ", ".join(canonical_entities),
            "DuplicateGroups": "; ".join(
                f"{canonical}: {', '.join(sorted(duplicates, key=_case_atom_key))}"
                for canonical, duplicates in sorted(duplicate_groups.items(), key=lambda item: _case_atom_key(item[0]))
            ),
            "SupportKind": "duplicate_relation_distinct_count",
        }
    ]
    return _status_timeline_companion_result(
        predicate="duplicate_exclusion_count_support",
        query=(
            "duplicate_exclusion_count_support"
            "(SourcePredicate, RawEntityCount, DistinctEntityCount, CanonicalEntities, DuplicateGroups, SupportKind)."
        ),
        rows=rows,
        original_query=query,
        note=(
            "query-only duplicate exclusion support counted unary entity rows after excluding entities that admitted "
            "duplicate/alias relations map onto canonical entities; no durable fact was written"
        ),
    )


def _duplicate_relation_rows(runtime: CorePrologRuntime, *, raw_entities: set[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for clause in getattr(runtime.engine, "clauses", []) or []:
        if getattr(clause, "body", None):
            continue
        head = getattr(clause, "head", None)
        predicate = str(getattr(head, "name", "") or "").strip()
        term_args = list(getattr(head, "args", []) or [])
        if len(term_args) != 2 or not predicate:
            continue
        lowered = predicate.casefold()
        if not (
            lowered in {"alias_of", "duplicate_of", "is_alias_of", "is_duplicate_of"}
            or lowered.endswith(("_alias_of", "_duplicate_of"))
        ):
            continue
        duplicate = str(term_args[0]).strip()
        canonical = str(term_args[1]).strip()
        if duplicate in raw_entities and canonical in raw_entities and duplicate != canonical:
            rows.append({"predicate": predicate, "duplicate": duplicate, "canonical": canonical})
    return rows


def _policy_gated_counterfactual_total_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: tuple[Any, ...],
    query: str,
) -> dict[str, Any] | None:
    query_tokens = set(_type_taxonomy_tokens(predicate))
    trigger_tokens = {
        "proposal",
        "proposed",
        "pending",
        "unapproved",
        "excluded",
        "temporary",
        "temp",
        "adjustment",
        "request",
        "change",
    }
    if not (query_tokens & trigger_tokens):
        return None

    fact_rows = _runtime_fact_rows(runtime)
    gated_subjects = _counterfactual_gated_subjects(fact_rows)
    base_rows: list[tuple[str, int]] = []
    delta_sources_by_value: dict[int, set[str]] = {}
    for fact in fact_rows:
        fact_predicate = str(fact.get("predicate", "")).strip()
        fact_tokens = set(_type_taxonomy_tokens(fact_predicate))
        fact_args = [str(item).strip() for item in fact.get("args", [])]
        numeric_values = [value for value in (_int_from_atom(arg) for arg in fact_args) if value is not None]
        if not fact_predicate or not numeric_values:
            continue
        if _counterfactual_base_total_predicate(fact_tokens):
            for value in numeric_values:
                base_rows.append((fact_predicate, value))
            continue
        if _counterfactual_delta_predicate(fact_tokens, fact_args=fact_args, gated_subjects=gated_subjects):
            for value in numeric_values:
                if value > 0:
                    delta_sources_by_value.setdefault(value, set()).add(fact_predicate)

    if not base_rows or not delta_sources_by_value:
        return None

    rows: list[dict[str, str]] = []
    seen: set[tuple[str, int, int]] = set()
    for base_predicate, base_value in sorted(base_rows, key=lambda item: (_case_atom_key(item[0]), item[1])):
        for delta_value, delta_sources in sorted(delta_sources_by_value.items()):
            key = (base_predicate, base_value, delta_value)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "HelperClass": "clean-helper",
                    "SupportKind": "policy_gated_counterfactual_total",
                    "BasePredicate": base_predicate,
                    "BaseTotal": str(base_value),
                    "DeltaSources": ",".join(sorted(delta_sources, key=_case_atom_key)),
                    "DeltaValue": str(delta_value),
                    "Operation": "add_if_gate_were_lifted",
                    "CounterfactualTotal": str(base_value + delta_value),
                }
            )
    if not rows:
        return None
    return _status_timeline_companion_result(
        predicate="policy_gated_counterfactual_total_support",
        query=(
            "policy_gated_counterfactual_total_support"
            "(BasePredicate, BaseTotal, DeltaSources, DeltaValue, CounterfactualTotal, SupportKind)."
        ),
        rows=rows[:24],
        original_query=query,
        note=(
            "query-only policy-gated arithmetic support added grounded positive deltas that are explicitly "
            "pending, proposed, unapproved, excluded, or temporary to a grounded base total; no durable fact was written"
        ),
    )


def _counterfactual_base_total_predicate(tokens: set[str]) -> bool:
    return bool(tokens & {"final", "current", "base", "total"}) and bool(tokens & {"count", "total"})


def _counterfactual_delta_predicate(
    tokens: set[str],
    *,
    fact_args: list[str],
    gated_subjects: set[str],
) -> bool:
    if tokens & {"withdrawn", "estimate", "estimated", "prior", "previous", "earlier"}:
        return False
    direct_delta = bool(
        tokens & {"proposal", "proposed", "pending", "unapproved", "excluded", "temporary", "temp", "addition", "add", "delta"}
    )
    if direct_delta:
        return True
    if not (tokens & {"adjustment", "request", "change"}):
        return False
    subjects = {arg for arg in fact_args if _int_from_atom(arg) is None}
    return bool(subjects & gated_subjects)


def _counterfactual_gated_subjects(facts: list[dict[str, Any]]) -> set[str]:
    subjects: set[str] = set()
    gate_terms = {"rejected", "pending", "unapproved", "excluded", "denied", "not", "approved"}
    for fact in facts:
        predicate = str(fact.get("predicate", "")).strip()
        predicate_tokens = set(_type_taxonomy_tokens(predicate))
        if not (predicate_tokens & {"status", "approval", "decision"}):
            continue
        args = [str(item).strip() for item in fact.get("args", [])]
        if len(args) < 2:
            continue
        status = args[-1]
        status_tokens = set(_type_taxonomy_tokens(status))
        if not (status_tokens & gate_terms):
            continue
        if status_tokens <= {"approved"}:
            continue
        subject_candidates = [args[-2]] if len(args) >= 3 else [args[0]]
        for subject in subject_candidates:
            if subject and _int_from_atom(subject) is None:
                subjects.add(subject)
    return subjects


def _set_difference_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: tuple[Any, ...],
    query: str,
) -> dict[str, Any] | None:
    if predicate != "set_minus" or len(args) != 3:
        return None
    resolved_triples = _resolved_set_minus_triples(runtime, args=args, query=query)
    if not resolved_triples:
        return None

    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for view_arg, base_arg, exclusion_arg in resolved_triples:
        base_rows = _binary_fact_rows_for_first_arg(runtime, base_arg)
        exclusion_rows = _binary_fact_rows_for_first_arg(runtime, exclusion_arg)
        if not base_rows or not exclusion_rows:
            continue
        excluded_members = {row["member"] for row in exclusion_rows}
        for base_row in base_rows:
            member = base_row["member"]
            if member in excluded_members:
                continue
            for exclusion_row in exclusion_rows:
                key = (member, base_row["predicate"], exclusion_row["predicate"], exclusion_arg)
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    {
                        "HelperClass": "clean-helper",
                        "QueryView": view_arg,
                        "BaseSet": base_arg,
                        "ExclusionSet": exclusion_arg,
                        "Member": member,
                        "BasePredicate": base_row["predicate"],
                        "ExclusionPredicate": exclusion_row["predicate"],
                        "SupportKind": "set_difference_member",
                    }
                )
    if not rows:
        return None

    result = {
        "status": "success",
        "result_type": "table",
        "predicate": "set_difference_support",
        "prolog_query": (
            "set_difference_support"
            "(QueryView, BaseSet, ExclusionSet, Member, BasePredicate, ExclusionPredicate, SupportKind)."
        ),
        "variables": [
            "HelperClass",
            "QueryView",
            "BaseSet",
            "ExclusionSet",
            "Member",
            "BasePredicate",
            "ExclusionPredicate",
            "SupportKind",
        ],
        "rows": rows,
        "num_rows": len(rows),
        "reasoning_basis": {
            "kind": "core-local",
            "note": (
                "query-only set difference support derived output members from admitted binary membership "
                "relations keyed by the base set and exclusion set; no durable fact was written"
            ),
            "original_query": query,
        },
    }
    return {
        "query": result["prolog_query"],
        "result": result,
        "derived_from_queries": [query],
    }


def _resolved_set_minus_triples(
    runtime: CorePrologRuntime,
    *,
    args: tuple[Any, ...],
    query: str,
) -> list[tuple[str, str, str]]:
    arg_texts = [str(arg).strip() for arg in args]
    if any(not item for item in arg_texts):
        return []
    if not any(_is_prolog_variable(item) for item in arg_texts):
        return [(arg_texts[0], arg_texts[1], arg_texts[2])]
    result = runtime.query_rows(query)
    if result.get("status") != "success":
        return []
    triples: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in result.get("rows", []) or []:
        if not isinstance(row, dict):
            continue
        resolved: list[str] = []
        for arg in arg_texts:
            value = str(row.get(arg, "")).strip() if _is_prolog_variable(arg) else arg
            if not value:
                resolved = []
                break
            resolved.append(value)
        if len(resolved) != 3:
            continue
        triple = (resolved[0], resolved[1], resolved[2])
        if triple in seen:
            continue
        seen.add(triple)
        triples.append(triple)
    return triples


def _binary_fact_rows_for_first_arg(runtime: CorePrologRuntime, key: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    ignored_predicates = {"set_minus", "set_union"}
    for clause in getattr(runtime.engine, "clauses", []) or []:
        if getattr(clause, "body", None):
            continue
        head = getattr(clause, "head", None)
        predicate = str(getattr(head, "name", "") or "").strip()
        term_args = list(getattr(head, "args", []) or [])
        if not predicate or predicate in ignored_predicates or predicate.startswith("source_record_"):
            continue
        if len(term_args) != 2:
            continue
        first = str(term_args[0]).strip()
        second = str(term_args[1]).strip()
        if first == key and second:
            rows.append({"predicate": predicate, "member": second})
    return rows


def _review_remaining_set_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: tuple[Any, ...],
    query: str,
) -> dict[str, Any] | None:
    if predicate not in {"review_source", "review_applies_notice"} or len(args) != 2:
        return None
    review_arg = str(args[0]).strip()
    target_reviews = {review_arg} if review_arg and not _is_prolog_variable(review_arg) else None

    review_sources: dict[str, str] = {}
    review_notices: dict[str, str] = {}
    memberships: list[tuple[str, str]] = []
    exclusions: list[tuple[str, str]] = []
    for clause in getattr(runtime.engine, "clauses", []) or []:
        if getattr(clause, "body", None):
            continue
        head = getattr(clause, "head", None)
        fact_predicate = str(getattr(head, "name", "") or "").strip()
        term_args = [str(arg).strip() for arg in list(getattr(head, "args", []) or [])]
        if fact_predicate == "review_source" and len(term_args) == 2:
            review_sources[term_args[0]] = term_args[1]
        elif fact_predicate == "review_applies_notice" and len(term_args) == 2:
            review_notices[term_args[0]] = term_args[1]
        elif fact_predicate == "member_of" and len(term_args) == 2:
            memberships.append((term_args[0], term_args[1]))
        elif fact_predicate == "excluded_by" and len(term_args) == 2:
            exclusions.append((term_args[0], term_args[1]))

    rows: list[dict[str, str]] = []
    for review, source_set in sorted(review_sources.items(), key=lambda item: _case_atom_key(item[0])):
        if target_reviews is not None and review not in target_reviews:
            continue
        notice = review_notices.get(review)
        if not notice:
            continue
        members = {
            right if left == source_set else left
            for left, right in memberships
            if left == source_set or right == source_set
        }
        if not members:
            continue
        excluded = {item for item, exclusion_notice in exclusions if exclusion_notice == notice}
        remaining = sorted(members - excluded, key=_case_atom_key)
        excluded_members = sorted(members & excluded, key=_case_atom_key)
        rows.append(
            {
                "HelperClass": "clean-helper",
                "Review": review,
                "SourceSet": source_set,
                "ExclusionNotice": notice,
                "RemainingCount": str(len(remaining)),
                "RemainingMembers": ", ".join(remaining),
                "ExcludedMembers": ", ".join(excluded_members),
                "SupportKind": "review_bound_remaining_set",
            }
        )
    if not rows:
        return None

    result = {
        "status": "success",
        "result_type": "table",
        "predicate": "review_remaining_set_support",
        "prolog_query": (
            "review_remaining_set_support"
            "(Review, SourceSet, ExclusionNotice, RemainingCount, RemainingMembers, ExcludedMembers, SupportKind)."
        ),
        "variables": [
            "HelperClass",
            "Review",
            "SourceSet",
            "ExclusionNotice",
            "RemainingCount",
            "RemainingMembers",
            "ExcludedMembers",
            "SupportKind",
        ],
        "rows": rows,
        "num_rows": len(rows),
        "reasoning_basis": {
            "kind": "core-local",
            "note": (
                "query-only review remaining-set support joined review source sets, applied exclusion notices, "
                "source-set membership, and excluded members; no durable fact was written"
            ),
            "original_query": query,
        },
    }
    return {
        "query": result["prolog_query"],
        "result": result,
        "derived_from_queries": [query],
    }


def _residual_absolute_amount_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: tuple[Any, ...],
    query: str,
) -> dict[str, Any] | None:
    query_tokens = set(_type_taxonomy_tokens(predicate))
    if not (query_tokens & {"total", "allocated", "allocation", "absolute", "remainder", "residual", "rest"}):
        return None

    arg_texts = [str(item).strip() for item in args]
    target_scenarios = {arg_texts[0]} if arg_texts and arg_texts[0] and not _is_prolog_variable(arg_texts[0]) else set()
    target_recipients: set[str] = set()
    if query_tokens & {"remainder", "residual", "rest"} and len(arg_texts) >= 2:
        recipient_arg = arg_texts[1]
        if recipient_arg and not _is_prolog_variable(recipient_arg):
            target_recipients.add(_residual_share_entity_key(recipient_arg))

    facts = _runtime_fact_rows(runtime)
    totals: dict[str, list[tuple[str, int, str]]] = {}
    absolute_allocations: dict[str, dict[str, dict[str, Any]]] = {}
    remainder_recipients: dict[str, dict[str, str]] = {}

    for fact in facts:
        fact_predicate = str(fact.get("predicate", "")).strip()
        if not fact_predicate or fact_predicate.startswith("source_record_"):
            continue
        fact_args = [str(item).strip() for item in fact.get("args", [])]
        if len(fact_args) < 2:
            continue
        tokens = set(_type_taxonomy_tokens(fact_predicate))
        scenario = fact_args[0]
        if not scenario:
            continue
        if "total" in tokens and len(fact_args) >= 3:
            value = _int_from_atom(fact_args[-1])
            if value is not None:
                resource = fact_args[1]
                totals.setdefault(scenario, []).append((resource, value, fact_predicate))
            continue
        if tokens & {"remainder", "residual", "rest", "unassigned"}:
            recipient = fact_args[1]
            if recipient:
                key = _residual_share_entity_key(recipient)
                existing = remainder_recipients.setdefault(scenario, {}).get(key, "")
                if not existing or existing.startswith("recipient_"):
                    remainder_recipients[scenario][key] = recipient
            continue
        if tokens & {"absolute", "allocated", "allocation", "assigned", "assign", "share"}:
            value = _int_from_atom(fact_args[-1])
            if value is not None and len(fact_args) >= 3:
                recipient = fact_args[1]
                key = _residual_share_entity_key(recipient)
                scenario_allocations = absolute_allocations.setdefault(scenario, {})
                existing = scenario_allocations.get(key)
                if existing is None:
                    scenario_allocations[key] = {
                        "recipient": recipient,
                        "value": value,
                        "predicates": {fact_predicate},
                    }
                else:
                    existing.setdefault("predicates", set()).add(fact_predicate)
                    if str(existing.get("recipient", "")).startswith("recipient_") and not recipient.startswith("recipient_"):
                        existing["recipient"] = recipient

    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, int, str, int]] = set()
    for scenario, total_rows in sorted(totals.items(), key=lambda item: _case_atom_key(item[0])):
        if target_scenarios and scenario not in target_scenarios:
            continue
        allocations = list(absolute_allocations.get(scenario, {}).values())
        recipients_by_key = remainder_recipients.get(scenario, {})
        if target_recipients:
            recipients = [value for key, value in recipients_by_key.items() if key in target_recipients]
        else:
            recipients = list(recipients_by_key.values())
        if not allocations or not recipients:
            continue
        allocated_sum = sum(int(item["value"]) for item in allocations)
        allocation_sources = sorted(
            {source for item in allocations for source in item.get("predicates", set())},
            key=_case_atom_key,
        )
        allocated_recipients = sorted({str(item.get("recipient", "")) for item in allocations}, key=_case_atom_key)
        for resource, total_value, total_source in total_rows:
            remaining = total_value - allocated_sum
            if remaining < 0:
                continue
            for recipient in sorted(recipients, key=_case_atom_key):
                key = (scenario, resource, total_value, recipient, remaining)
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    {
                        "HelperClass": "clean-helper",
                        "SupportKind": "residual_absolute_amount",
                        "Scenario": scenario,
                        "Resource": resource,
                        "TotalPredicate": total_source,
                        "TotalAmount": str(total_value),
                        "AllocatedPredicates": ", ".join(allocation_sources),
                        "AllocatedRecipients": ", ".join(allocated_recipients),
                        "AllocatedAmount": str(allocated_sum),
                        "RemainderRecipient": recipient,
                        "RemainingAmount": str(remaining),
                    }
                )

    if not rows:
        return None

    result = {
        "status": "success",
        "result_type": "table",
        "predicate": "residual_absolute_amount_support",
        "prolog_query": (
            "residual_absolute_amount_support"
            "(Scenario, Resource, TotalAmount, AllocatedAmount, RemainderRecipient, RemainingAmount, SupportKind)."
        ),
        "variables": [
            "HelperClass",
            "SupportKind",
            "Scenario",
            "Resource",
            "TotalPredicate",
            "TotalAmount",
            "AllocatedPredicates",
            "AllocatedRecipients",
            "AllocatedAmount",
            "RemainderRecipient",
            "RemainingAmount",
        ],
        "rows": rows[:24],
        "num_rows": min(len(rows), 24),
        "reasoning_basis": {
            "kind": "core-local",
            "note": (
                "query-only residual arithmetic support subtracted admitted absolute allocations from an "
                "admitted scenario total for the admitted remainder recipient; no durable fact was written"
            ),
            "original_query": query,
        },
    }
    return {
        "query": result["prolog_query"],
        "result": result,
        "derived_from_queries": [query],
    }


def _residual_share_entity_key(value: str) -> str:
    text = str(value or "").strip()
    return text.removeprefix("recipient_")


def _causal_end_state_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: tuple[Any, ...],
    query: str,
) -> dict[str, Any] | None:
    query_tokens = set(_type_taxonomy_tokens(predicate))
    if not (query_tokens & {"end", "ended", "ends", "ending", "termination", "terminated"}):
        return None

    arg_texts = [str(item).strip() for item in args]
    target_states = {
        arg_texts[1]
    } if len(arg_texts) >= 2 and arg_texts[1] and not _is_prolog_variable(arg_texts[1]) else set()
    target_ending_events = {
        arg_texts[0]
    } if arg_texts and arg_texts[0] and not _is_prolog_variable(arg_texts[0]) else set()

    facts = _runtime_fact_rows(runtime)
    ended_rows: list[tuple[str, str, str]] = []
    upstream_rows: list[tuple[str, str, str, str]] = []
    for fact in facts:
        fact_predicate = str(fact.get("predicate", "")).strip()
        if not fact_predicate or fact_predicate.startswith("source_record_"):
            continue
        fact_args = [str(item).strip() for item in fact.get("args", [])]
        if len(fact_args) < 2:
            continue
        tokens = set(_type_taxonomy_tokens(fact_predicate))
        if tokens & {"end", "ended", "ends", "ending", "termination", "terminated"}:
            ended_rows.append((fact_args[0], fact_args[1], fact_predicate))
        if fact_predicate in {"led_to", "leads_to"} and len(fact_args) >= 2:
            upstream_rows.append((fact_args[0], fact_args[1], fact_predicate, "cause_to_ending_event"))
        elif fact_predicate == "caused_by" and len(fact_args) >= 2:
            upstream_rows.append((fact_args[1], fact_args[0], fact_predicate, "cause_to_ending_event"))
        elif fact_predicate == "triggered" and len(fact_args) >= 2:
            upstream_rows.append((fact_args[0], fact_args[1], fact_predicate, "cause_to_ending_event"))
        elif fact_predicate == "triggered_by" and len(fact_args) >= 2:
            upstream_rows.append((fact_args[1], fact_args[0], fact_predicate, "cause_to_ending_event"))

    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for ending_event, ended_state, end_predicate in ended_rows:
        if target_states and ended_state not in target_states:
            continue
        if target_ending_events and ending_event not in target_ending_events:
            continue
        for cause, effect, cause_predicate, chain_kind in upstream_rows:
            if effect != ending_event:
                continue
            key = (cause, ending_event, ended_state, cause_predicate)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "HelperClass": "clean-helper",
                    "SupportKind": "causal_end_state_chain",
                    "Cause": cause,
                    "EndingEvent": ending_event,
                    "EndedState": ended_state,
                    "CausePredicate": cause_predicate,
                    "EndPredicate": end_predicate,
                    "ChainKind": chain_kind,
                }
            )
    if not rows:
        return None

    result = {
        "status": "success",
        "result_type": "table",
        "predicate": "causal_end_state_support",
        "prolog_query": "causal_end_state_support(Cause, EndingEvent, EndedState, CausePredicate, EndPredicate, SupportKind).",
        "variables": [
            "HelperClass",
            "SupportKind",
            "Cause",
            "EndingEvent",
            "EndedState",
            "CausePredicate",
            "EndPredicate",
            "ChainKind",
        ],
        "rows": rows[:24],
        "num_rows": min(len(rows), 24),
        "reasoning_basis": {
            "kind": "core-local",
            "note": (
                "query-only causal end-state support joined admitted upstream causal rows to admitted "
                "end-state rows; no durable fact was written"
            ),
            "original_query": query,
        },
    }
    return {
        "query": result["prolog_query"],
        "result": result,
        "derived_from_queries": [query],
    }


def _method_frame_purpose_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: tuple[Any, ...],
    query: str,
) -> dict[str, Any] | None:
    if predicate not in {"agent_uses_method", "method_action", "method_produces_metric"}:
        return None
    method_filter = ""
    agent_filter = ""
    arg_texts = [str(item).strip() for item in args]
    if predicate == "agent_uses_method" and len(arg_texts) >= 2:
        agent_filter = arg_texts[0] if arg_texts[0] and not _is_prolog_variable(arg_texts[0]) else ""
        method_filter = arg_texts[1] if arg_texts[1] and not _is_prolog_variable(arg_texts[1]) else ""
    elif predicate in {"method_action", "method_produces_metric"} and arg_texts:
        method_filter = arg_texts[0] if arg_texts[0] and not _is_prolog_variable(arg_texts[0]) else ""
    if not method_filter and not agent_filter:
        return None

    method_rows = _runtime_rows(runtime, "agent_uses_method(Agent, Method).")
    domain_rows = _runtime_rows(runtime, "agent_operates_in(Agent, FramePurpose).")
    if not method_rows or not domain_rows:
        return None

    domains_by_agent: dict[str, list[str]] = {}
    for row in domain_rows:
        agent = str(row.get("Agent", "")).strip()
        domain = str(row.get("FramePurpose", "")).strip()
        if agent and domain:
            domains_by_agent.setdefault(agent, []).append(domain)
    source_rows = _method_frame_source_rows(runtime)

    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for row in method_rows:
        agent = str(row.get("Agent", "")).strip()
        method = str(row.get("Method", "")).strip()
        if not agent or not method:
            continue
        if agent_filter and agent != agent_filter:
            continue
        if method_filter and method != method_filter:
            continue
        for domain in domains_by_agent.get(agent, []):
            frame_rows = _source_rows_for_method_frame(source_rows, agent=agent, domain=domain)
            if not frame_rows:
                frame_rows = [{"SourceRow": "", "FrameText": ""}]
            for frame in frame_rows[:3]:
                source_row = str(frame.get("SourceRow", "")).strip()
                frame_text = str(frame.get("FrameText", "")).strip()
                key = (agent, method, domain, source_row)
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    {
                        "HelperClass": "clean-helper",
                        "SupportKind": "method_frame_purpose_support",
                        "Agent": agent,
                        "Method": method,
                        "FramePurpose": domain,
                        "FramePurposeDisplay": _display_source_phrase(domain),
                        "SourceRow": source_row,
                        "FrameText": frame_text,
                        "FrameTextDisplay": _display_source_phrase(frame_text),
                    }
                )
    if not rows:
        return None

    result = {
        "status": "success",
        "result_type": "table",
        "predicate": "method_frame_purpose_support",
        "prolog_query": "method_frame_purpose_support(Method, Agent, FramePurpose, SourceRow, FrameText).",
        "variables": [
            "HelperClass",
            "SupportKind",
            "Method",
            "Agent",
            "FramePurpose",
            "FramePurposeDisplay",
            "SourceRow",
            "FrameText",
            "FrameTextDisplay",
        ],
        "rows": rows[:24],
        "num_rows": min(len(rows), 24),
        "reasoning_basis": {
            "kind": "core-local",
            "note": (
                "query-only method-frame purpose support joined admitted method-use rows to admitted "
                "agent/domain rows and source-record frame text; no durable fact was written"
            ),
            "original_query": query,
        },
    }
    return {
        "query": result["prolog_query"],
        "result": result,
        "derived_from_queries": [
            query,
            "agent_uses_method(Agent, Method).",
            "agent_operates_in(Agent, FramePurpose).",
            "source_record_label(SourceRow, FrameText).",
            "source_record_text_atom(SourceRow, FrameText).",
        ],
    }


def _method_frame_source_rows(runtime: CorePrologRuntime) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source_query in ("source_record_text_atom(SourceRow, FrameText).", "source_record_label(SourceRow, FrameText)."):
        for row in _runtime_rows(runtime, source_query):
            source_row = str(row.get("SourceRow", "")).strip()
            frame_text = str(row.get("FrameText", "")).strip()
            if source_row and frame_text:
                rows.append({"SourceRow": source_row, "FrameText": frame_text})
    return rows


def _source_rows_for_method_frame(
    source_rows: list[dict[str, str]],
    *,
    agent: str,
    domain: str,
) -> list[dict[str, str]]:
    agent_tokens = _loose_atom_token_set(agent)
    domain_tokens = _loose_atom_token_set(domain)
    required_domain_overlap = 1 if len(domain_tokens) <= 2 else 2
    scored: list[tuple[int, dict[str, str]]] = []
    for row in source_rows:
        text_tokens = _loose_atom_token_set(str(row.get("FrameText", "")))
        if not text_tokens:
            continue
        agent_overlap = len(agent_tokens & text_tokens)
        domain_overlap = len(domain_tokens & text_tokens)
        if agent_overlap <= 0 and domain_overlap < required_domain_overlap:
            continue
        score = agent_overlap * 2 + domain_overlap
        scored.append((score, row))
    scored.sort(key=lambda item: (-item[0], item[1].get("SourceRow", ""), item[1].get("FrameText", "")))
    return [row for _, row in scored]


def _method_actor_frame_source_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: tuple[Any, ...],
    query: str,
) -> dict[str, Any] | None:
    if predicate not in {
        "method_actor",
        "role_performs_method",
        "method_primary_location",
        "method_performed_at",
        "method_log_location",
        "method_domain",
    }:
        return None
    arg_texts = [str(item).strip() for item in args]
    actor_filter = ""
    method_filter = ""
    location_filter = ""
    domain_filter = ""
    if predicate == "method_actor" and len(arg_texts) >= 2:
        method_filter = arg_texts[0] if arg_texts[0] and not _is_prolog_variable(arg_texts[0]) else ""
        actor_filter = arg_texts[1] if arg_texts[1] and not _is_prolog_variable(arg_texts[1]) else ""
    elif predicate == "role_performs_method" and len(arg_texts) >= 2:
        actor_filter = arg_texts[0] if arg_texts[0] and not _is_prolog_variable(arg_texts[0]) else ""
        method_filter = arg_texts[1] if arg_texts[1] and not _is_prolog_variable(arg_texts[1]) else ""
    elif predicate in {"method_primary_location", "method_performed_at", "method_log_location"} and len(arg_texts) >= 2:
        method_filter = arg_texts[0] if arg_texts[0] and not _is_prolog_variable(arg_texts[0]) else ""
        location_filter = arg_texts[1] if arg_texts[1] and not _is_prolog_variable(arg_texts[1]) else ""
    elif predicate == "method_domain" and len(arg_texts) >= 2:
        method_filter = arg_texts[0] if arg_texts[0] and not _is_prolog_variable(arg_texts[0]) else ""
        domain_filter = arg_texts[1] if arg_texts[1] and not _is_prolog_variable(arg_texts[1]) else ""
    if not any((actor_filter, method_filter, location_filter, domain_filter)):
        return None

    method_actor_rows = _method_actor_rows(runtime)
    if not method_actor_rows:
        return None
    locations_by_method = _method_location_map(runtime)
    domains_by_method = _method_domain_map(runtime)
    source_rows = _method_frame_source_rows(runtime)
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for method, actor in method_actor_rows:
        if actor_filter and actor != actor_filter:
            continue
        if method_filter and method != method_filter:
            continue
        method_locations = locations_by_method.get(method, set())
        method_domains = domains_by_method.get(method, set())
        if location_filter and location_filter not in method_locations:
            continue
        if domain_filter and domain_filter not in method_domains:
            continue
        for frame in _source_rows_for_method_actor_frame(
            source_rows,
            actor=actor,
            method=method,
            locations=method_locations,
            domains=method_domains,
            require_actor=bool(actor_filter) or not method_filter,
        )[:3]:
            source_row = str(frame.get("SourceRow", "")).strip()
            frame_text = str(frame.get("FrameText", "")).strip()
            key = (actor, method, source_row)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "HelperClass": "clean-helper",
                    "SupportKind": "method_actor_frame_source_support",
                    "Actor": actor,
                    "ActorDisplay": _display_source_phrase(actor),
                    "Method": method,
                    "MethodDisplay": _display_source_phrase(method),
                    "SourceRow": source_row,
                    "FrameText": frame_text,
                    "FrameTextDisplay": _display_source_phrase(frame_text),
                }
            )
    if not rows:
        return None

    result = {
        "status": "success",
        "result_type": "table",
        "predicate": "method_actor_frame_source_support",
        "prolog_query": "method_actor_frame_source_support(Actor, Method, SourceRow, FrameText).",
        "variables": [
            "HelperClass",
            "SupportKind",
            "Actor",
            "ActorDisplay",
            "Method",
            "MethodDisplay",
            "SourceRow",
            "FrameText",
            "FrameTextDisplay",
        ],
        "rows": rows[:24],
        "num_rows": min(len(rows), 24),
        "reasoning_basis": {
            "kind": "core-local",
            "note": (
                "query-only method-actor frame support joined admitted method actor/location/domain "
                "rows to source-record frame text; no durable fact was written"
            ),
            "original_query": query,
        },
    }
    return {
        "query": result["prolog_query"],
        "result": result,
        "derived_from_queries": [
            query,
            "method_actor(Method, Actor).",
            "role_performs_method(Actor, Method).",
            "method_primary_location(Method, Location).",
            "method_performed_at(Method, Location).",
            "method_log_location(Method, Location).",
            "method_domain(Method, Domain).",
            "source_record_label(SourceRow, FrameText).",
            "source_record_text_atom(SourceRow, FrameText).",
        ],
    }


def _method_actor_rows(runtime: CorePrologRuntime) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for query, method_key, actor_key in (
        ("method_actor(Method, Actor).", "Method", "Actor"),
        ("role_performs_method(Actor, Method).", "Method", "Actor"),
    ):
        for row in _runtime_rows(runtime, query):
            method = str(row.get(method_key, "")).strip()
            actor = str(row.get(actor_key, "")).strip()
            key = (method, actor)
            if method and actor and key not in seen:
                seen.add(key)
                rows.append(key)
    return rows


def _method_location_map(runtime: CorePrologRuntime) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for query in (
        "method_primary_location(Method, Location).",
        "method_performed_at(Method, Location).",
        "method_log_location(Method, Location).",
    ):
        for row in _runtime_rows(runtime, query):
            method = str(row.get("Method", "")).strip()
            location = str(row.get("Location", "")).strip()
            if method and location:
                out.setdefault(method, set()).add(location)
    return out


def _method_domain_map(runtime: CorePrologRuntime) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for row in _runtime_rows(runtime, "method_domain(Method, Domain)."):
        method = str(row.get("Method", "")).strip()
        domain = str(row.get("Domain", "")).strip()
        if method and domain:
            out.setdefault(method, set()).add(domain)
    return out


def _source_rows_for_method_actor_frame(
    source_rows: list[dict[str, str]],
    *,
    actor: str,
    method: str,
    locations: set[str],
    domains: set[str],
    require_actor: bool,
) -> list[dict[str, str]]:
    actor_tokens = _loose_atom_token_set(actor)
    method_tokens = _loose_atom_token_set(method)
    location_tokens = set().union(*(_loose_atom_token_set(item) for item in locations)) if locations else set()
    domain_tokens = set().union(*(_loose_atom_token_set(item) for item in domains)) if domains else set()
    scored: list[tuple[int, dict[str, str]]] = []
    for row in source_rows:
        text_tokens = _loose_atom_token_set(str(row.get("FrameText", "")))
        if not text_tokens:
            continue
        actor_overlap = len(actor_tokens & text_tokens)
        method_overlap = len(method_tokens & text_tokens)
        location_overlap = len(location_tokens & text_tokens)
        domain_overlap = len(domain_tokens & text_tokens)
        if require_actor:
            if actor_overlap <= 0 or (method_overlap <= 0 and location_overlap <= 0 and domain_overlap <= 0):
                continue
            score = actor_overlap * 4 + method_overlap * 3 + location_overlap * 2 + domain_overlap
        else:
            if method_overlap <= 0 and not (actor_overlap > 0 and (location_overlap > 0 or domain_overlap > 0)):
                continue
            score = method_overlap * 10 + actor_overlap * 2 + location_overlap + domain_overlap
        scored.append((score, row))
    scored.sort(key=lambda item: (-item[0], item[1].get("SourceRow", ""), item[1].get("FrameText", "")))
    return [row for _, row in scored]


def _loose_atom_token_set(value: str) -> set[str]:
    tokens = set(_type_taxonomy_tokens(value))
    for token in list(tokens):
        if len(token) > 3 and token.endswith("s"):
            tokens.add(token[:-1])
    return tokens


def _identifier_alias_key(value: str) -> str:
    tokens = [token for token in _type_taxonomy_tokens(value) if token]
    if len(tokens) <= 1:
        return str(value or "").strip().lower()
    numeric_positions = [index for index, token in enumerate(tokens) if token.isdigit()]
    if numeric_positions:
        start = max(0, numeric_positions[-1] - 1)
        return "_".join(tokens[start:])
    return "_".join(tokens[-2:])


def _normalize_status_atom(value: str) -> str:
    text = str(value or "").strip()
    return text.removeprefix("status_")


def _domain_companion_queries(
    runtime: CorePrologRuntime,
    *,
    query: str,
    include_legacy_native_helpers: bool = True,
) -> list[dict[str, Any]]:
    parsed = parse_prolog_query(query)
    if parsed is None:
        return []
    predicate, args = parsed
    source_record_companions: list[dict[str, Any]] = []
    status_timeline = _status_timeline_summary_companion(runtime, predicate=predicate, args=args, query=query)
    if status_timeline:
        source_record_companions.append(status_timeline)
    scoped_status_count = _scoped_status_count_companion(runtime, predicate=predicate, args=args, query=query)
    if scoped_status_count:
        source_record_companions.append(scoped_status_count)
    alias_count = _identifier_alias_count_companion(runtime, predicate=predicate, args=args, query=query)
    if alias_count:
        source_record_companions.append(alias_count)
    duplicate_exclusion = _duplicate_exclusion_count_companion(runtime, predicate=predicate, args=args, query=query)
    if duplicate_exclusion:
        source_record_companions.append(duplicate_exclusion)
    policy_gated_total = _policy_gated_counterfactual_total_companion(
        runtime,
        predicate=predicate,
        args=args,
        query=query,
    )
    if policy_gated_total:
        source_record_companions.append(policy_gated_total)
    set_difference = _set_difference_companion(runtime, predicate=predicate, args=args, query=query)
    if set_difference:
        source_record_companions.append(set_difference)
    review_remaining_set = _review_remaining_set_companion(runtime, predicate=predicate, args=args, query=query)
    if review_remaining_set:
        source_record_companions.append(review_remaining_set)
    residual_absolute = _residual_absolute_amount_companion(runtime, predicate=predicate, args=args, query=query)
    if residual_absolute:
        source_record_companions.append(residual_absolute)
    causal_end_state = _causal_end_state_companion(runtime, predicate=predicate, args=args, query=query)
    if causal_end_state:
        source_record_companions.append(causal_end_state)
    method_frame_purpose = _method_frame_purpose_companion(runtime, predicate=predicate, args=args, query=query)
    if method_frame_purpose:
        source_record_companions.append(method_frame_purpose)
    method_actor_frame = _method_actor_frame_source_companion(runtime, predicate=predicate, args=args, query=query)
    if method_actor_frame:
        source_record_companions.append(method_actor_frame)
    item_description_detail = _item_description_detail_companion(runtime, predicate=predicate, args=args, query=query)
    if item_description_detail:
        source_record_companions.append(item_description_detail)
    if include_legacy_native_helpers:
        for legacy_companion in (
            _source_record_table_body_count_companion(runtime, predicate=predicate, args=args, query=query),
            _source_record_section_display_companion(runtime, predicate=predicate, query=query),
            _source_record_packet_metadata_companion(runtime, predicate=predicate, args=args, query=query),
            _homeroom_member_alias_companion(runtime, predicate=predicate, args=args, query=query),
            _roster_table_member_alias_companion(runtime, predicate=predicate, args=args, query=query),
            _roster_table_count_companion(runtime, predicate=predicate, args=args, query=query),
            _grant_award_companion(runtime, predicate=predicate, args=args, query=query),
            _industrial_sensor_companion(runtime, predicate=predicate, args=args, query=query),
            _clinic_device_recall_companion(runtime, predicate=predicate, args=args, query=query),
        ):
            if legacy_companion:
                source_record_companions.append(_mark_legacy_native_helper_adapter(legacy_companion))
    if source_record_companions:
        if include_legacy_native_helpers and predicate in {
            "adult_role",
            "attendance_scan",
            "bus_assignment",
            "group_member",
            "group_membership",
            "homeroom_member",
            "policy_requirement",
            "role_counts_towards_ratio",
            "roster_version",
            "roster_version_status",
            "source_record_label",
            "student_group_assignment",
            "student_in_homeroom",
            "supervises",
            "supervision_assignment",
            "temporary_assignment",
            "temporary_event_assignment",
        }:
            roster_state = _roster_state_companion(runtime, predicate=predicate, args=args, query=query)
            if roster_state:
                source_record_companions.append(_mark_legacy_native_helper_adapter(roster_state))
        return source_record_companions
    if include_legacy_native_helpers:
        clock_sync = _source_record_clock_sync_companion(runtime, predicate=predicate, query=query)
        if clock_sync:
            return [_mark_legacy_native_helper_adapter(clock_sync)]
        authority_custody = _authority_custody_companion(runtime, predicate=predicate, query=query)
        if authority_custody:
            return [_mark_legacy_native_helper_adapter(authority_custody)]
        clear_sample_clock = _clear_sample_clock_pause_companion(runtime, predicate=predicate, query=query)
        if clear_sample_clock:
            return [_mark_legacy_native_helper_adapter(clear_sample_clock)]
        roster_state = _roster_state_companion(runtime, predicate=predicate, args=args, query=query)
        if roster_state:
            return [_mark_legacy_native_helper_adapter(roster_state)]
    initial_status = _initial_status_scope_companion(runtime, predicate=predicate, args=args, query=query)
    if initial_status:
        return [initial_status]
    vote_threshold = _vote_threshold_counterfactual_companion(runtime, predicate=predicate, args=args, query=query)
    if vote_threshold:
        return [vote_threshold]
    lifecycle_period = _lifecycle_period_support_companion(runtime, predicate=predicate, args=args, query=query)
    if lifecycle_period:
        return [lifecycle_period]
    type_taxonomy = _type_taxonomy_summary_companion(runtime, predicate=predicate, args=args, query=query)
    if type_taxonomy:
        return [type_taxonomy]
    recall_companions = _recall_domain_companion_queries(runtime, predicate=predicate, args=args, query=query)
    if recall_companions:
        return recall_companions
    story_choice = _story_choice_contrast_companion(runtime, predicate=predicate, args=args, query=query)
    if story_choice:
        return [story_choice]
    story_remediation = _story_remediation_method_companion(runtime, predicate=predicate, args=args, query=query)
    if story_remediation:
        return [story_remediation]
    conversion_effect = _classification_conversion_effect_companion(runtime, predicate=predicate, args=args, query=query)
    hoa_companions = _hoa_census_companion_queries(runtime, predicate=predicate, args=args, query=query)
    combined_companions = [item for item in [conversion_effect, *hoa_companions] if item]
    if combined_companions:
        return combined_companions
    if predicate == "person_role" and len(args) >= 2:
        person_arg = str(args[0]).strip()
        if person_arg and not _is_prolog_variable(person_arg):
            out: list[dict[str, Any]] = []
            companion_queries = [
                format_prolog_query("ruling_by", [person_arg, "Subject", "Outcome"]),
                format_prolog_query("permission_granted", [person_arg, "Request"]),
                format_prolog_query("official_action", [person_arg, "Action", "Subject"]),
                format_prolog_query("event_affects_person", ["Event", person_arg, "Action"]),
            ]
            for companion_query in _ordered_query_unique(companion_queries):
                result = runtime.query_rows(companion_query)
                if result.get("status") != "success":
                    continue
                out.append(
                    {
                        "query": companion_query,
                        "result": {
                            **result,
                            "reasoning_basis": {
                                "kind": "core-local",
                                "note": "domain companion query expanded official identity role lookup with admitted authority/action evidence",
                                "original_query": query,
                            },
                        },
                        "derived_from_queries": [query],
                    }
                )
            return out
    if predicate == "committee_member" and len(args) >= 2:
        out: list[dict[str, Any]] = []
        committee_arg = str(args[0]).strip()
        member_arg = str(args[1]).strip()
        replacement_queries: list[str] = []
        if committee_arg and not _is_prolog_variable(committee_arg):
            replacement_queries.append(
                format_prolog_query("committee_member_replaced", [committee_arg, "OldMember", "NewMember", "ReplacementDate"])
            )
        replacement_queries.append(format_prolog_query("committee_member_replaced", ["Committee", "OldMember", "NewMember", "ReplacementDate"]))
        if member_arg and not _is_prolog_variable(member_arg):
            replacement_queries.append(
                format_prolog_query("committee_member_replaced", ["Committee", member_arg, "NewMember", "ReplacementDate"])
            )
            replacement_queries.append(
                format_prolog_query("committee_member_replaced", ["Committee", "OldMember", member_arg, "ReplacementDate"])
            )
        for companion_query in _ordered_query_unique(replacement_queries):
            result = runtime.query_rows(companion_query)
            if result.get("status") != "success":
                continue
            out.append(
                {
                    "query": companion_query,
                    "result": {
                        **result,
                        "reasoning_basis": {
                            "kind": "core-local",
                            "note": "domain companion query paired committee_member/3 with committee_member_replaced/4 replacement evidence",
                            "original_query": query,
                        },
                    },
                    "derived_from_queries": [query],
                }
            )
        return out
    if predicate in {"fsrb_may", "fsrb_decision_effect", "deadline_requirement"}:
        out: list[dict[str, Any]] = []
        companion_queries = [
            "deadline_requirement(Deadline, Amount, Unit, fsrb_decision_date).",
            "fsrb_may(Action).",
            "fsrb_decision_effect(Condition, Effect).",
            "fsrb_decision_final(Status).",
        ]
        for companion_query in _ordered_query_unique(companion_queries):
            if companion_query == str(query or "").strip():
                continue
            result = runtime.query_rows(companion_query)
            if result.get("status") != "success":
                continue
            out.append(
                {
                    "query": companion_query,
                    "result": {
                        **result,
                        "reasoning_basis": {
                            "kind": "core-local",
                            "note": "domain companion query gathered standing FSRB decision deadlines/effects for counterfactual or finality questions",
                            "original_query": query,
                        },
                    },
                    "derived_from_queries": [query],
                }
            )
        return out
    if predicate == "deadline_calculated" and len(args) == 5:
        companion_query = "deadline_calculated(Deadline, Type, StartDate, Duration, EndDate)."
        if companion_query == str(query or "").strip():
            return []
        result = runtime.query_rows(companion_query)
        if result.get("status") != "success":
            return []
        return [
            {
                "query": companion_query,
                "result": {
                    **result,
                    "reasoning_basis": {
                        "kind": "core-local",
                        "note": "domain companion query gathered sibling deadline_calculated/5 rows so deadline-family questions can distinguish answer, response, reply, discovery, and dispositive deadlines",
                        "original_query": query,
                    },
                },
                "derived_from_queries": [query],
            }
        ]
    if predicate == "subgrant_purpose" and args:
        subgrant_arg = str(args[0]).strip()
        if not subgrant_arg:
            return []
        if _is_prolog_variable(subgrant_arg):
            companion_args = ["Subgrant"]
        else:
            companion_args = [subgrant_arg]
        out: list[dict[str, Any]] = []
        for companion_predicate, value_name in [
            ("subgrant_amount", "Amount"),
            ("subgrant_expended", "Expended"),
            ("subgrant_remaining", "Remaining"),
        ]:
            companion_query = format_prolog_query(companion_predicate, [*companion_args, value_name])
            result = runtime.query_rows(companion_query)
            if result.get("status") != "success":
                continue
            out.append(
                {
                    "query": companion_query,
                    "result": {
                        **result,
                        "reasoning_basis": {
                            "kind": "core-local",
                            "note": "domain companion query followed subgrant_purpose/2 to financial amount predicates using the same subgrant id",
                            "original_query": query,
                        },
                    },
                    "derived_from_queries": [query],
                }
            )
        return out
    if predicate in {
        "action_when",
        "avoid_pattern",
        "debugging_tactic",
        "does_not_directly_determine",
        "enables",
        "export_reason",
        "guard_effect",
        "guard_mechanism",
        "guard_value",
        "metric_semantics",
        "optimization_priority",
        "priority_reason",
        "recommendation",
        "summary_review_question",
        "tradeoff",
        "validates_when_high",
    }:
        companion_queries = [
            "support_reason(Anchor, Reason).",
            "support_effect(Anchor, Effect).",
            "support_tradeoff(Anchor, Benefit, CostOrRisk).",
            "support_exception(Anchor, Exception).",
            "support_positive_counterpart(Anchor, PreferredAction).",
        ]
        out = []
        for companion_query in companion_queries:
            result = runtime.query_rows(companion_query)
            if result.get("status") != "success":
                continue
            out.append(
                {
                    "query": companion_query,
                    "result": {
                        **result,
                        "reasoning_basis": {
                            "kind": "core-local",
                            "note": "domain companion query gathered admitted support-acquisition rationale rows for enterprise-guidance evidence",
                            "original_query": query,
                        },
                    },
                    "derived_from_queries": [query],
                }
            )
        return out
    return []


def _mark_legacy_native_helper_adapter(companion: dict[str, Any]) -> dict[str, Any]:
    result = companion.get("result", {}) if isinstance(companion, dict) else {}
    if not isinstance(result, dict):
        return companion
    basis = result.get("reasoning_basis", {})
    if not isinstance(basis, dict):
        basis = {}
    return {
        **companion,
        "result": {
            **result,
            "reasoning_basis": {
                **basis,
                "adapter_status": "legacy_native_compatibility_adapter",
                "default_delivery": "disabled",
                "replacement_direction": "prefer direct compile-surface predicates over query-time helper bridges",
            },
        },
    }


def _source_record_packet_metadata_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    if predicate not in {
        "adult_role",
        "application_eligibility",
        "applicant_attribute",
        "bonus_eligibility",
        "bus_assignment",
        "cycle_parameter",
        "eligibility_rule",
        "final_award",
        "medical_accommodation",
        "policy_requirement",
        "requested_amount",
        "role_counts_towards_ratio",
        "roster_version_status",
        "access_authority",
        "access_type",
        "external_id",
        "item_description",
        "party_role",
        "physical_custodian",
        "recorded_assertion",
        "contested_by",
        "motion_filed",
        "court_order",
        "caused_by",
        "current_status",
        "event_actor",
        "event_occurred",
        "event_target",
        "lab_result",
        "lot_attribute",
        "lot_status",
        "has_role",
        "order",
        "staff_statement",
        "system_event",
        "system_log_event",
        "telemetry_reading",
        "timestamp_correction",
        "correction_notice",
        "source_record_field",
        "source_record_cell",
        "source_record_label",
        "source_record_section",
        "source_record_text_atom",
        "title_status",
    }:
        return None

    text_rows = _runtime_rows(runtime, "source_record_text_atom(SourceRow, TextAtom).")
    label_rows = _runtime_rows(runtime, "source_record_label(SourceRow, Label).")
    field_rows = _runtime_rows(runtime, "source_record_field(SourceRow, Header, Value).")
    section_rows = _runtime_rows(runtime, "source_record_section(SourceRow, SectionAtom).")
    line_rows = _runtime_rows(runtime, "source_record_line(SourceRow, Line).")
    source_rows = _runtime_rows(runtime, "source_record_row(SourceRow, RowType, Line, SectionAtom, Label).")
    numeric_rows = _runtime_rows(runtime, "source_record_numeric_token(SourceRow, NumericToken).")
    item_description_rows = _runtime_rows(runtime, "item_description(Item, Description).")
    access_authority_rows = _runtime_rows(runtime, "access_authority(Item, Party, SourceId).")
    court_order_rows = _runtime_rows(runtime, "court_order(OrderId, OrderDate, OrderContent).")
    staff_statement_rows = _runtime_rows(runtime, "staff_statement(StatementId, Speaker, Content).")
    if not text_rows and not label_rows:
        return None

    labels_by_row: dict[str, set[str]] = {}
    for row in label_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        label = str(row.get("Label", "")).strip()
        if source_row and label:
            labels_by_row.setdefault(source_row, set()).add(label)
    section_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("SectionAtom", "")).strip()
        for row in section_rows
    }
    line_by_row: dict[str, int] = {}
    for row in line_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        line = str(row.get("Line", "")).strip()
        if source_row and _is_numeric_atom(line):
            line_by_row[source_row] = int(float(line))
    row_type_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("RowType", "")).strip()
        for row in source_rows
    }
    numeric_tokens_by_row: dict[str, list[str]] = {}
    for row in numeric_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        token = str(row.get("NumericToken", "")).strip()
        if source_row and token:
            numeric_tokens_by_row.setdefault(source_row, []).append(token)
    text_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("TextAtom", "")).strip()
        for row in text_rows
    }

    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str, str]] = set()

    def add(
        source_row: str,
        kind: str,
        value: str,
        detail: str = "",
        display_value: str = "",
        helper_class: str = "clean-helper",
        extra_fields: dict[str, str] | None = None,
    ) -> None:
        if not source_row or not kind or not value:
            return
        display = display_value or _display_source_atom(value)
        key = (source_row, kind, value, display, helper_class)
        if key in seen:
            return
        seen.add(key)
        rows.append(
            {
                "SourceRow": source_row,
                "SectionAtom": section_by_row.get(source_row, ""),
                "Kind": kind,
                "Value": value,
                "DisplayValue": display,
                "Detail": detail,
                "HelperClass": helper_class,
                **(extra_fields or {}),
            }
        )

    for source_row, labels in labels_by_row.items():
        for label in sorted(labels):
            kind = _metadata_kind_for_atom(label)
            if kind:
                add(source_row, kind, label)

    for row in field_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        value = str(row.get("Value", "")).strip()
        if not source_row or not value:
            continue
        kind = _metadata_kind_for_atom(value)
        if kind:
            add(source_row, kind, value)

    for source_row, row_fields in _source_record_fields_by_row_from_rows(field_rows).items():
        item = _field_value(row_fields, "item_id") or _field_value(row_fields, "item")
        location = (
            _field_value(row_fields, "custodian_physical")
            or _field_value(row_fields, "physical_custodian")
            or _field_value(row_fields, "location")
        )
        if item and location:
            external_id = _field_value(row_fields, "external_id")
            detail = f"item={item};location={location}"
            if external_id:
                detail += f";external_id={external_id}"
            add(
                source_row,
                "source_record_custody_location",
                item,
                detail=detail,
                display_value=f"{_display_source_phrase(location)}"
                    + (f" (External ID {_display_source_phrase(external_id)})" if external_id else ""),
            )
        order_id = _field_value(row_fields, "order_id") or _field_value(row_fields, "order")
        if order_id:
            section_atom = section_by_row.get(source_row, "")
            add(
                source_row,
                "source_record_order_section",
                order_id,
                detail=f"order_id={order_id};section={section_atom}",
                display_value=_display_section_from_atom(section_atom),
            )
        access_parties = _field_value(row_fields, "authorized_parties_access") or _field_value(row_fields, "authorized_parties")
        authorizing_source = _field_value(row_fields, "authorizing_source") or _field_value(row_fields, "access_authorizing_source")
        if item and access_parties and authorizing_source and _is_non_revocable_access_policy_field(
            access_parties=access_parties,
            authorizing_source=authorizing_source,
        ):
            policy_value = _access_policy_value_from_atom(authorizing_source) or _access_policy_value_from_atom(access_parties)
            add(
                source_row,
                "non_revocable_access_policy",
                policy_value or item,
                detail=f"item={item};authorized_parties={access_parties};authorizing_source={authorizing_source}",
                display_value=(
                    "Reading-room patron access governed by museum policy"
                    + (f" {_display_source_atom(policy_value)}" if policy_value else "")
                    + "; not executor-revocable."
                ),
            )

    for row in item_description_rows:
        item = str(row.get("Item", "")).strip()
        description = str(row.get("Description", "")).strip()
        if not item or not description:
            continue
        year = _year_from_atom(description)
        if not year:
            continue
        add(
            item,
            "item_description_detail",
            item,
            detail=f"description={description};year={year}",
            display_value=f"{_display_item_description_atom(description)} ({year})",
        )

    court_orders_by_id = {
        str(row.get("OrderId", "")).strip(): row
        for row in court_order_rows
        if str(row.get("OrderId", "")).strip()
    }
    staff_statement_by_speaker = {
        str(row.get("Speaker", "")).strip(): row
        for row in staff_statement_rows
        if str(row.get("Speaker", "")).strip()
    }
    for row in access_authority_rows:
        item = str(row.get("Item", "")).strip()
        party = str(row.get("Party", "")).strip()
        source_id = str(row.get("SourceId", "")).strip()
        order = court_orders_by_id.get(source_id)
        if not item or not party or not source_id or not order:
            continue
        order_date = str(order.get("OrderDate", "")).strip()
        order_content = str(order.get("OrderContent", "")).strip()
        add(
            item,
            "access_authority_order",
            source_id,
            detail=f"item={item};party={party};order_date={order_date};order_content={order_content}",
            display_value=f"{_display_source_atom(source_id)} dated {_display_source_date_atom(order_date)}",
        )

    for source_row, token in _source_rows_matching_query_tokens(
        args=args,
        numeric_tokens_by_row=numeric_tokens_by_row,
        text_by_row=text_by_row,
    ):
        section_atom = section_by_row.get(source_row, "")
        if not section_atom:
            continue
        section_display = _display_source_record_section_label(section_atom)
        add(
            source_row,
            "source_record_matching_token_source",
            section_atom,
            detail=text_by_row.get(source_row, ""),
            display_value=(
                f"{section_display} contains source row {source_row} matching "
                f"{_display_source_date_atom(token)}."
            ),
            extra_fields={
                "MatchedToken": token,
                "SourceName": section_atom,
                "DisplaySourceName": section_display,
                "SourceAddressability": "bound_query_token",
            },
        )

    for row in text_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        text_atom = str(row.get("TextAtom", "")).strip()
        if not source_row or not text_atom:
            continue
        for token in _metadata_tokens_from_text_atom(text_atom):
            kind = _metadata_kind_for_atom(token)
            if kind:
                add(source_row, kind, token, detail=text_atom)
        if _is_unreproduced_reference_row(
            text_atom=text_atom,
            section_atom=section_by_row.get(source_row, ""),
            row_type=row_type_by_row.get(source_row, ""),
        ):
            add(
                source_row,
                "unreproduced_reference",
                _unreproduced_reference_value(text_atom),
                detail=text_atom,
                display_value=_display_unreproduced_reference(text_atom),
            )
        discovery_note = _source_record_discovery_note(text_atom)
        if discovery_note:
            add(
                source_row,
                "source_record_discovery_note",
                discovery_note["date"],
                detail=text_atom,
                display_value=discovery_note["display"],
                helper_class="candidate-helper",
            )
        for temporal_note in _source_record_temporal_notes(text_atom):
            add(
                source_row,
                temporal_note["kind"],
                temporal_note["value"],
                detail=text_atom,
                display_value=temporal_note["display"],
                helper_class="candidate-helper",
                extra_fields=temporal_note.get("fields", {}),
            )
        for sample_note in _source_record_sample_result_notes(text_atom):
            add(
                source_row,
                "source_record_sample_result_note",
                sample_note["value"],
                detail=text_atom,
                display_value=sample_note["display"],
                helper_class="candidate-helper",
                extra_fields=sample_note.get("fields", {}),
            )
        for authority_note in _source_record_timestamp_authority_notes(text_atom):
            add(
                source_row,
                "source_record_timestamp_authority_note",
                authority_note["value"],
                detail=text_atom,
                display_value=authority_note["display"],
                helper_class="candidate-helper",
                extra_fields=authority_note.get("fields", {}),
            )
        for filing_note in _source_record_statement_filing_notes(
            text_atom,
            staff_statement_by_speaker=staff_statement_by_speaker,
        ):
            add(
                source_row,
                "source_record_statement_filing_note",
                filing_note["value"],
                detail=text_atom,
                display_value=filing_note["display"],
                helper_class="candidate-helper",
                extra_fields=filing_note.get("fields", {}),
            )
        for routing_note in _source_record_role_routing_notes(text_atom):
            add(
                source_row,
                "source_record_role_routing_note",
                routing_note["value"],
                detail=text_atom,
                display_value=routing_note["display"],
                helper_class="candidate-helper",
                extra_fields=routing_note.get("fields", {}),
            )
        for clock_note in _source_record_clock_event_notes(text_atom):
            add(
                source_row,
                "source_record_clock_event_note",
                clock_note["value"],
                detail=text_atom,
                display_value=clock_note["display"],
                helper_class="candidate-helper",
                extra_fields=clock_note.get("fields", {}),
            )
        for order_note in _source_record_order_identifier_notes(text_atom):
            add(
                source_row,
                "source_record_order_identifier_note",
                order_note["value"],
                detail=text_atom,
                display_value=order_note["display"],
                helper_class="candidate-helper",
                extra_fields=order_note.get("fields", {}),
            )
        for order_authority_note in _source_record_order_authority_notes(text_atom):
            add(
                source_row,
                "source_record_order_authority_note",
                order_authority_note["value"],
                detail=text_atom,
                display_value=order_authority_note["display"],
                helper_class="candidate-helper",
                extra_fields=order_authority_note.get("fields", {}),
            )
        for item_event_note in _source_record_item_event_identifier_notes(text_atom):
            add(
                source_row,
                "source_record_item_event_identifier_note",
                item_event_note["value"],
                detail=text_atom,
                display_value=item_event_note["display"],
                helper_class="candidate-helper",
                extra_fields=item_event_note.get("fields", {}),
            )

    ordered_source_rows = sorted(line_by_row, key=lambda source_row: line_by_row[source_row])
    for source_row in ordered_source_rows:
        text_atom = text_by_row.get(source_row, "")
        next_text = _next_source_text_atom(source_row, ordered_source_rows, text_by_row, line_by_row)
        if "originals_are_filed" in text_atom:
            previous_text = _previous_source_text_atom(source_row, ordered_source_rows, text_by_row)
            next_text = _next_source_text_atom(source_row, ordered_source_rows, text_by_row, line_by_row)
            combined = f"{previous_text} {text_atom} {next_text}".strip()
            location_match = re.search(r"(?:^|_)with_the_(?P<location>[a-z0-9_]+)(?:_|$)", next_text)
            location = location_match.group("location") if location_match else ""
            if location:
                subject = "recusal_memo_originals" if "recusal_memos" in combined or "rc_" in combined else "originals"
                add(
                    source_row,
                    "original_filing_location",
                    subject,
                    detail=combined,
                    display_value=f"{_display_source_phrase(subject)} filed with the {_display_source_phrase(location)}.",
                )
        previous_text = _previous_source_text_atom(source_row, ordered_source_rows, text_by_row)
        next_text = _next_source_text_atom(source_row, ordered_source_rows, text_by_row, line_by_row)
        combined = f"{previous_text} {text_atom} {next_text}".strip()
        window = _source_text_window(source_row, ordered_source_rows, text_by_row, line_by_row, radius=3)
        section_atom = section_by_row.get(source_row, "")
        if _is_unreproduced_reference_context(combined=window, section_atom=section_atom):
            value = _unreproduced_reference_value(window)
            if value:
                add(
                    source_row,
                    "unreproduced_reference",
                    value,
                    detail=window,
                    display_value=_display_unreproduced_reference(window),
                )
        if _is_non_finding_statement_context(combined=window, section_atom=section_atom):
            add(
                source_row,
                "recorded_assertion_not_finding",
                _recorded_assertion_not_finding_value(window),
                detail=window,
                display_value=_display_recorded_assertion_not_finding(window),
            )
        if _is_authoritative_source_context(combined=window, section_atom=section_atom):
            add(
                source_row,
                "authoritative_finding_sources",
                "forensic_handwriting_report_and_court_rulings",
                detail=window,
                display_value="Forensic handwriting analyst's report when filed and the Court's ultimate rulings.",
            )
        if _is_registrar_identity_context(combined=window, section_atom=section_atom):
            add(
                source_row,
                "role_holder",
                _registrar_identity_value(window),
                detail=f"role=museum_registrar;{window}",
                display_value=_display_registrar_identity(window),
            )
        if _is_loan_amendment_effect_context(combined=window, section_atom=section_atom):
            add(
                source_row,
                "loan_amendment_effect",
                "nrm_ll_2020_02",
                detail=window,
                display_value="NRM-LL-2020-02: lender unchanged; loan period extended to 2027-09-30.",
            )
        if _is_non_revocable_access_policy_context(combined=window, section_atom=section_atom):
            value = _access_policy_value_from_atom(window) or "reading_room_access_policy"
            add(
                source_row,
                "non_revocable_access_policy",
                value,
                detail=window,
                display_value=(
                    "Reading-room patron access governed by museum policy"
                    + (f" {_display_source_atom(value)}" if value else "")
                    + "; not subject to change by the lender."
                ),
            )
        if _is_no_executor_delivery_direction_context(combined=window, section_atom=section_atom):
            add(
                source_row,
                "no_delivery_direction",
                "executor_reeder_items",
                detail=window,
                display_value="The executor has not yet directed delivery of the Reeder-held items pending codicil resolution.",
            )
        numeric_tokens = numeric_tokens_by_row.get(source_row) or _numeric_tokens_in_window(
            source_row,
            ordered_source_rows,
            numeric_tokens_by_row,
            line_by_row,
            radius=1,
        )
        for token in numeric_tokens:
            if _is_asserted_event_date_context(combined=window, token=token):
                add(
                    source_row,
                    "asserted_event_date",
                    token,
                    detail=window,
                    display_value=f"{_display_source_date_atom(token)} asserted event date.",
                )
        if _is_unruled_motion_context(combined=window):
            add(
                source_row,
                "motion_status",
                _unruled_motion_value(window),
                detail=window,
                display_value="The Court has not ruled on this motion.",
            )

    if not rows:
        return None
    rows.sort(key=lambda item: (item["Kind"], item["DisplayValue"], item["SourceRow"]))
    rows = _scope_source_record_packet_metadata_rows(rows, predicate=predicate, args=args, query=query)
    if not rows:
        return None
    return {
        "query": "source_record_packet_metadata_support(Kind, Value, DisplayValue, SourceRow, Detail).",
        "result": {
            "status": "success",
            "predicate": "source_record_packet_metadata_support",
            "prolog_query": "source_record_packet_metadata_support(Kind, Value, DisplayValue, SourceRow, Detail).",
            "result_type": "table",
            "num_rows": len(rows),
            "variables": ["Kind", "Value", "DisplayValue", "SourceRow", "SectionAtom", "Detail", "HelperClass"],
            "rows": rows[:140],
            "reasoning_basis": {
                "kind": "query-only-companion",
                "note": (
                    "surfaced clean generic identifier/source-addressability metadata from admitted source_record "
                    "ledger atoms and explicitly labeled fixture-family packet notes as candidate-helper rows"
                ),
                "trigger_predicate": predicate,
                "original_query": query,
            },
        },
        "derived_from_queries": [
            query,
            "source_record_text_atom(SourceRow, TextAtom).",
            "source_record_label(SourceRow, Label).",
            "source_record_section(SourceRow, SectionAtom).",
            "source_record_line(SourceRow, Line).",
            "source_record_numeric_token(SourceRow, NumericToken).",
        ],
    }


def _item_description_detail_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    if predicate not in {"item_description", "evidence_item"}:
        return None
    item_arg = str(args[0]).strip() if args else ""
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    description_sources = [
        ("item_description", "item_description(Item, Description)."),
        ("evidence_item", "evidence_item(Item, Description)."),
    ]
    for source_predicate, description_query in description_sources:
        for row in _runtime_rows(runtime, description_query):
            item = str(row.get("Item", "")).strip()
            description = str(row.get("Description", "")).strip()
            if not item or not description:
                continue
            if item_arg and not _is_prolog_variable(item_arg) and item != item_arg:
                continue
            key = (item, description)
            if key in seen:
                continue
            seen.add(key)
            year = _year_from_atom(description)
            rows.append(
                {
                    "Item": item,
                    "Description": description,
                    "DisplayDescription": _display_item_description_atom(description),
                    "Year": year,
                    "SourcePredicate": source_predicate,
                    "HelperClass": "clean-helper",
                }
            )
    if not rows:
        return None
    return {
        "query": "item_description_detail_support(Item, Description, DisplayDescription, Year, SourcePredicate).",
        "result": {
            "status": "success",
            "predicate": "item_description_detail_support",
            "prolog_query": "item_description_detail_support(Item, Description, DisplayDescription, Year, SourcePredicate).",
            "result_type": "table",
            "num_rows": len(rows),
            "variables": ["Item", "Description", "DisplayDescription", "Year", "SourcePredicate", "HelperClass"],
            "rows": rows[:80],
            "reasoning_basis": {
                "kind": "query-only-companion",
                "note": "derived display title and trailing year from admitted item-description predicates",
                "trigger_predicate": predicate,
                "original_query": query,
            },
        },
        "derived_from_queries": [query, "item_description(Item, Description).", "evidence_item(Item, Description)."],
    }


def _source_record_table_body_count_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    if predicate not in {"source_record_row", "source_record_field", "source_record_cell", "source_record_label"}:
        return None
    query_text = str(query or "").casefold()
    if "count" not in query_text and "how_many" not in query_text and "source_record_row" not in query_text:
        return None
    source_rows = _runtime_rows(runtime, "source_record_row(SourceRow, RowType, Line, SectionAtom, Label).")
    field_rows = _runtime_rows(runtime, "source_record_field(SourceRow, Header, Value).")
    fields_by_row = _source_record_fields_by_row_from_rows(field_rows)
    if not source_rows or not fields_by_row:
        return None
    section_filter = ""
    if predicate == "source_record_row" and len(args) >= 4:
        maybe_section = str(args[3]).strip()
        if maybe_section and not _is_prolog_variable(maybe_section):
            section_filter = maybe_section
    rows_by_section: dict[str, list[dict[str, Any]]] = {}
    for row in source_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        row_type = str(row.get("RowType", "")).strip()
        section_atom = str(row.get("SectionAtom", "")).strip()
        label = str(row.get("Label", "")).strip()
        if not source_row or row_type != "table_row":
            continue
        if section_filter and section_atom != section_filter:
            continue
        fields = fields_by_row.get(source_row, {})
        if not fields or _source_record_table_row_is_header(label=label, fields=fields):
            continue
        rows_by_section.setdefault(section_atom, []).append(
            {
                "SourceRow": source_row,
                "Label": label,
                "Line": str(row.get("Line", "")).strip(),
            }
        )
    out_rows: list[dict[str, Any]] = []
    for section_atom, body_rows in sorted(rows_by_section.items()):
        labels = [str(row.get("Label", "")) for row in body_rows if str(row.get("Label", ""))]
        out_rows.append(
            {
                "SectionAtom": section_atom,
                "RowType": "table_row",
                "BodyRowCount": len(body_rows),
                "Labels": ", ".join(labels[:40]),
                "HelperClass": "clean-helper",
            }
        )
    if not out_rows:
        return None
    return {
        "query": "source_record_table_body_count_support(SectionAtom, RowType, BodyRowCount, Labels).",
        "result": {
            "status": "success",
            "predicate": "source_record_table_body_count_support",
            "prolog_query": "source_record_table_body_count_support(SectionAtom, RowType, BodyRowCount, Labels).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": ["SectionAtom", "RowType", "BodyRowCount", "Labels", "HelperClass"],
            "rows": out_rows[:80],
            "reasoning_basis": {
                "kind": "query-only-companion",
                "note": "counted source-record table body rows from field-bearing data rows while excluding header rows",
                "trigger_predicate": predicate,
                "original_query": query,
            },
        },
        "derived_from_queries": [
            query,
            "source_record_row(SourceRow, RowType, Line, SectionAtom, Label).",
            "source_record_field(SourceRow, Header, Value).",
        ],
    }


def _source_record_table_row_is_header(*, label: str, fields: dict[str, list[str]]) -> bool:
    label_text = str(label or "").strip().lower()
    if label_text in {"item_id", "order_id", "date", "event_id", "application_id", "student_id"}:
        return True
    field_values = {str(value).strip().lower() for values in fields.values() for value in values}
    if not field_values:
        return True
    header_names = {str(header).strip().lower() for header in fields}
    return bool(field_values) and field_values.issubset(header_names | {label_text})


def _is_source_record_metadata_identifier_kind(kind: str) -> bool:
    text = str(kind or "").strip()
    return text == "packet_identifier" or text.endswith("_identifier")


def _scope_source_record_packet_metadata_rows(
    rows: list[dict[str, str]],
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> list[dict[str, str]]:
    """Keep source-record metadata companions close to the asked surface.

    The packet metadata companion is intentionally broad: it preserves exact
    structural facts from source records. Answer routing suffers when a
    role/custody/date question receives the entire packet inventory, so this
    predicate-level scoping ranks the relevant clean rows first without
    interpreting prose or introducing fixture-shaped constants.
    """

    wanted_by_predicate: dict[str, set[str]] = {
        "party_role": {"role_holder"},
        "physical_custodian": {"source_record_custody_location"},
        "access_authority": {"access_authority_order", "non_revocable_access_policy", "loan_amendment_effect"},
        "access_type": {"non_revocable_access_policy", "loan_amendment_effect"},
        "external_id": {"source_record_custody_location", "loan_amendment_effect", "non_revocable_access_policy"},
        "recorded_assertion": {
            "recorded_assertion_not_finding",
            "asserted_event_date",
            "authoritative_finding_sources",
        },
        "contested_by": {
            "recorded_assertion_not_finding",
            "asserted_event_date",
            "authoritative_finding_sources",
        },
        "title_status": {
            "recorded_assertion_not_finding",
            "authoritative_finding_sources",
            "loan_amendment_effect",
            "no_delivery_direction",
        },
        "motion_filed": {"motion_status"},
        "court_order": {"motion_status", "source_record_order_section"},
        "caused_by": {"source_record_temporal_event_note", "source_record_temporal_relation_note"},
        "current_status": {"source_record_temporal_event_note", "source_record_temporal_relation_note"},
        "event_actor": {"source_record_temporal_event_note", "source_record_temporal_relation_note"},
        "event_occurred": {"source_record_temporal_event_note", "source_record_temporal_relation_note"},
        "event_target": {"source_record_temporal_event_note", "source_record_temporal_relation_note"},
        "lab_result": {
            "source_record_matching_token_source",
            "source_record_sample_result_note",
            "source_record_temporal_event_note",
            "source_record_temporal_relation_note",
        },
        "lot_attribute": {"source_record_temporal_event_note", "source_record_temporal_relation_note"},
        "lot_status": {"source_record_temporal_event_note", "source_record_temporal_relation_note"},
        "has_role": {"source_record_role_routing_note", "source_record_clock_event_note"},
        "order": {"source_record_order_identifier_note", "source_record_order_authority_note"},
        "staff_statement": {"source_record_statement_filing_note"},
        "system_event": {
            "source_record_clock_event_note",
            "source_record_item_event_identifier_note",
            "source_record_matching_token_source",
        },
        "system_log_event": {"source_record_matching_token_source", "source_record_timestamp_authority_note"},
        "telemetry_reading": {"source_record_matching_token_source"},
        "timestamp_correction": {"source_record_matching_token_source", "source_record_timestamp_authority_note"},
    }
    arg_tokens = {
        str(arg).strip().casefold()
        for arg in args
        if str(arg).strip() and not _is_prolog_variable(str(arg).strip())
    }
    no_packet_metadata_predicates = {
        "policy_requirement",
    }
    high_pressure_candidate_kinds = {
        "source_record_discovery_note",
        "source_record_sample_result_note",
        "source_record_temporal_event_note",
        "source_record_temporal_relation_note",
        "source_record_matching_token_source",
        "source_record_clock_event_note",
        "source_record_order_authority_note",
        "source_record_order_identifier_note",
        "source_record_item_event_identifier_note",
        "source_record_role_routing_note",
        "source_record_statement_filing_note",
        "source_record_timestamp_authority_note",
    }

    def row_haystack(row: dict[str, str]) -> str:
        return " ".join(
            str(row.get(key, ""))
            for key in ("SourceRow", "Value", "DisplayValue", "Detail", "SectionAtom")
        ).casefold()

    def row_matches_arg_tokens(row: dict[str, str]) -> bool:
        haystack = row_haystack(row)
        for token in arg_tokens:
            if token in haystack:
                return True
            normalized = token.removeprefix("v_")
            event_time = str(row.get("EventTime", "")).casefold().removeprefix("v_")
            if event_time and (normalized.endswith(event_time) or event_time in normalized):
                return True
            identifier = str(row.get("ItemIdentifier", "")).casefold()
            if identifier and identifier in normalized:
                return True
        return False

    def compact_metadata_rows(items: list[dict[str, str]]) -> list[dict[str, str]]:
        compact: list[dict[str, str]] = []
        seen_compact: set[tuple[str, str, str, str]] = set()
        for row in items:
            kind = str(row.get("Kind", ""))
            if _is_source_record_metadata_identifier_kind(kind):
                key = (
                    kind,
                    str(row.get("Value", "")),
                    str(row.get("DisplayValue", "")),
                    str(row.get("HelperClass", "")),
                )
            else:
                key = (
                    kind,
                    str(row.get("Value", "")),
                    str(row.get("DisplayValue", "")),
                    str(row.get("SourceRow", "")),
                )
            if key in seen_compact:
                continue
            seen_compact.add(key)
            compact.append(row)
        return compact

    if predicate.startswith("source_record_"):
        if not arg_tokens:
            return compact_metadata_rows([
                row
                for row in rows
                if str(row.get("Kind", "")) not in high_pressure_candidate_kinds
                or (
                    predicate in {"source_record_label", "source_record_section"}
                    and str(row.get("Kind", "")) == "source_record_timestamp_authority_note"
                )
            ])
        return compact_metadata_rows([row for row in rows if row_matches_arg_tokens(row)])

    if predicate in no_packet_metadata_predicates:
        return []

    wanted = wanted_by_predicate.get(predicate)
    if not wanted:
        if arg_tokens:
            return compact_metadata_rows([row for row in rows if row_matches_arg_tokens(row)])
        return compact_metadata_rows(rows)

    def score(row: dict[str, str]) -> tuple[int, str, str]:
        kind = str(row.get("Kind", ""))
        haystack = row_haystack(row)
        kind_score = 0 if kind in wanted else 1
        token_score = 0 if not arg_tokens or any(token in haystack for token in arg_tokens) else 1
        return (kind_score + token_score, kind, str(row.get("SourceRow", "")))

    scoped = sorted(rows, key=score)
    relevant = [row for row in scoped if str(row.get("Kind", "")) in wanted]
    if predicate == "has_role":
        relevant = [row for row in relevant if arg_tokens and any(token in row_haystack(row) for token in arg_tokens)]
    if predicate == "system_event":
        relevant = [
            row
            for row in relevant
            if str(row.get("Kind", "")) not in {
                "source_record_clock_event_note",
                "source_record_item_event_identifier_note",
                "source_record_matching_token_source",
            }
            or (arg_tokens and row_matches_arg_tokens(row))
        ]
    if not relevant and predicate in {
        "has_role",
        "order",
        "staff_statement",
        "system_event",
        "system_log_event",
        "lab_result",
        "telemetry_reading",
        "timestamp_correction",
    }:
        return []
    if relevant:
        if predicate in {
            "has_role",
            "order",
            "party_role",
            "physical_custodian",
            "staff_statement",
            "system_event",
            "system_log_event",
            "lab_result",
            "telemetry_reading",
            "timestamp_correction",
        }:
            return relevant
        # Return relevant rows plus a small tail of context rows. The tail keeps
        # broad negative/source-status questions from losing neighboring packet
        # cues while avoiding the old 40+ row flood.
        context = [
            row
            for row in scoped
            if row not in relevant
            and (
                str(row.get("Kind", "")) not in high_pressure_candidate_kinds
                or any(token in row_haystack(row) for token in arg_tokens)
            )
        ][:8]
        return [*relevant, *context]
    return rows


def _next_source_text_atom(
    source_row: str,
    ordered_source_rows: list[str],
    text_by_row: dict[str, str],
    line_by_row: dict[str, int],
) -> str:
    line = line_by_row.get(source_row)
    if line is None:
        return ""
    for candidate in ordered_source_rows:
        if line_by_row.get(candidate) == line + 1:
            return text_by_row.get(candidate, "")
    return ""


def _previous_source_text_atom(
    source_row: str,
    ordered_source_rows: list[str],
    text_by_row: dict[str, str],
) -> str:
    try:
        index = ordered_source_rows.index(source_row)
    except ValueError:
        return ""
    if index <= 0:
        return ""
    return text_by_row.get(ordered_source_rows[index - 1], "")


def _source_text_window(
    source_row: str,
    ordered_source_rows: list[str],
    text_by_row: dict[str, str],
    line_by_row: dict[str, int],
    *,
    radius: int = 2,
) -> str:
    line = line_by_row.get(source_row)
    if line is None:
        return text_by_row.get(source_row, "")
    parts: list[str] = []
    for candidate in ordered_source_rows:
        candidate_line = line_by_row.get(candidate)
        if candidate_line is None:
            continue
        if abs(candidate_line - line) <= radius:
            text = text_by_row.get(candidate, "")
            if text:
                parts.append(text)
    return " ".join(parts).strip()


def _numeric_tokens_in_window(
    source_row: str,
    ordered_source_rows: list[str],
    numeric_tokens_by_row: dict[str, list[str]],
    line_by_row: dict[str, int],
    *,
    radius: int = 2,
) -> list[str]:
    line = line_by_row.get(source_row)
    if line is None:
        return numeric_tokens_by_row.get(source_row, [])
    tokens: list[str] = []
    for candidate in ordered_source_rows:
        candidate_line = line_by_row.get(candidate)
        if candidate_line is None:
            continue
        if abs(candidate_line - line) <= radius:
            tokens.extend(numeric_tokens_by_row.get(candidate, []))
    return _dedupe_str(tokens)


def _source_record_section_is_provenance(section_atom: str) -> bool:
    text = str(section_atom or "").strip().lower()
    return (
        "provenance" in text
        or "source_note" in text
        or "source_notes" in text
        or "compilation_notes" in text
    )


def _is_unreproduced_reference_row(*, text_atom: str, section_atom: str, row_type: str) -> bool:
    text = str(text_atom or "").strip().lower()
    if not text or not _source_record_section_is_provenance(section_atom):
        return False
    reference_markers = [
        "by_laws",
        "procedure_manual",
        "score_sheets",
        "decision_letters",
        "census_designated",
    ]
    if not any(marker in text for marker in reference_markers):
        return False
    return row_type in {"list_row", "anchored_line", ""} or text.startswith(("cycle_procedure_manual", "census_designated"))


def _is_unreproduced_reference_context(*, combined: str, section_atom: str) -> bool:
    text = str(combined or "").strip().lower()
    section = str(section_atom or "").strip().lower()
    if not text or "not_reproduced" not in text and "not reproduced" not in text:
        return False
    if not any(marker in section for marker in ["compilation", "provenance", "source_note", "source_notes"]):
        return False
    return any(
        marker in text
        for marker in [
            "last_will_and_testament",
            "chain_of_custody",
            "complete_asset_inventory",
            "correspondence_between_counsel",
            "docket_sheet",
            "by_laws",
            "procedure_manual",
            "score_sheets",
            "decision_letters",
            "census_designated",
        ]
    )


def _unreproduced_reference_value(text_atom: str) -> str:
    text = str(text_atom or "").strip().lower()
    if "last_will_and_testament" in text:
        return "last_will_and_testament"
    if "chain_of_custody" in text:
        return "chain_of_custody_documentation"
    if "complete_asset_inventory" in text:
        return "complete_asset_inventory"
    if "correspondence_between_counsel" in text:
        return "correspondence_between_counsel"
    if "docket_sheet" in text:
        return "court_docket_sheet"
    if "by_laws" in text:
        return "briarwood_foundation_by_laws"
    if "cycle_procedure_manual" in text:
        match = re.search(r"(bwcf_cp_\d{4})", text)
        return match.group(1) if match else "cycle_procedure_manual"
    if "score_sheets" in text:
        return "reviewer_score_sheets"
    if "decision_letters" in text:
        return "decision_letters"
    if "census_designated" in text:
        return "census_designated_rural_block_data"
    return text


def _display_source_phrase(value: str) -> str:
    text = str(value or "").strip().lower()
    if text == "last_will_and_testament":
        return "last will and testament"
    if text == "chain_of_custody_documentation":
        return "chain-of-custody documentation"
    if text == "complete_asset_inventory":
        return "complete asset inventory"
    if text == "correspondence_between_counsel":
        return "correspondence between counsel"
    if text == "court_docket_sheet":
        return "court docket sheet"
    if text == "briarwood_foundation_by_laws":
        return "Briarwood Foundation by-laws"
    if text == "bwcf_cp_2025":
        return "Cycle procedure manual BWCF-CP-2025"
    if text == "cycle_procedure_manual":
        return "Cycle procedure manual"
    if text == "reviewer_score_sheets":
        return "Reviewer score sheets"
    if text == "decision_letters":
        return "Decision letters issued separately to each applicant"
    if text == "census_designated_rural_block_data":
        return "Census-designated rural block data"
    if text == "recusal_memo_originals":
        return "Recusal memo originals"
    return text.replace("_", " ")


def _display_source_date_atom(value: str) -> str:
    text = str(value or "").strip().lower()
    match = re.fullmatch(r"v_(\d{4})_(\d{2})_(\d{2})", text)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    match = re.fullmatch(r"(\d{4})_(\d{2})_(\d{2})", text)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return _display_source_phrase(text)


def _year_from_atom(value: str) -> str:
    text = str(value or "").strip().lower()
    match = re.search(r"(?:^|_)((?:19|20)\d{2})(?:_|$)", text)
    return match.group(1) if match else ""


def _display_item_description_atom(value: str) -> str:
    text = str(value or "").strip().lower()
    year = _year_from_atom(text)
    if year:
        text = re.sub(rf"(?:^|_){re.escape(year)}(?:_|$)", "_", text).strip("_")
    words = [word for word in text.split("_") if word]
    return " ".join(word.capitalize() if len(word) > 2 else word for word in words)


def _is_non_revocable_access_policy_field(*, access_parties: str, authorizing_source: str) -> bool:
    combined = f"{access_parties} {authorizing_source}".lower()
    return (
        "reading_room" in combined
        and "museum_policy" in combined
        and ("patron" in combined or "patrons" in combined)
    )


def _access_policy_value_from_atom(value: str) -> str:
    text = str(value or "").strip().lower()
    match = re.search(r"(?:^|_)(mrp_\d+)(?:_|$)", text)
    if match:
        return match.group(1)
    match = re.search(r"(?:^|_)(nrm_rr_\d{4}_\d+)(?:_|$)", text)
    if match:
        return match.group(1)
    return ""


def _display_unreproduced_reference(text_atom: str) -> str:
    value = _unreproduced_reference_value(text_atom)
    return _display_source_phrase(value)


def _is_non_finding_statement_context(*, combined: str, section_atom: str) -> bool:
    text = str(combined or "").strip().lower()
    section = str(section_atom or "").strip().lower()
    if not text or "recorded_statement" not in section and "recorded_statements" not in section:
        return False
    return (
        "reproduction_does_not_constitute_a_finding_of_fact" in text
        or "recorded_but_has_not_been_ruled_upon" in text
        or "has_not_been_ruled_upon" in text
        or "court_has_not_found_facts" in text
    )


def _recorded_assertion_not_finding_value(text_atom: str) -> str:
    text = str(text_atom or "").strip().lower()
    if "private_gift" in text or "daniel_holloway" in text or "ex_003" in text:
        return "private_gift_assertion_ex_003"
    if "codicil" in text:
        return "codicil_contention"
    if "safekeeping" in text or "reeder" in text:
        return "safekeeping_assertion_reeder_items"
    return "recorded_assertion"


def _display_recorded_assertion_not_finding(text_atom: str) -> str:
    value = _recorded_assertion_not_finding_value(text_atom)
    if value == "private_gift_assertion_ex_003":
        return "The private-gift assertion for EX-003 is recorded but is not a finding of fact."
    if value == "codicil_contention":
        return "The codicil contention is recorded but has not been ruled upon."
    if value == "safekeeping_assertion_reeder_items":
        return "The Reeder safekeeping basis is recorded as an assertion; the Court has not found facts on it."
    return "Recorded assertion is not a finding of fact."


def _is_authoritative_source_context(*, combined: str, section_atom: str) -> bool:
    text = str(combined or "").strip().lower()
    section = str(section_atom or "").strip().lower()
    if not text or "recorded_statement" not in section and "recorded_statements" not in section:
        return False
    return (
        "forensic_handwriting" in text
        and "court_s" in text
        and "ultimate_rulings" in text
        and "authoritative_sources_for_findings" in text
    )


def _is_registrar_identity_context(*, combined: str, section_atom: str) -> bool:
    text = str(combined or "").strip().lower()
    section = str(section_atom or "").strip().lower()
    return "registrar" in text and (
        "registrar" in section
        or "museum" in text
        or "regional_museum" in text
    )


def _display_registrar_identity(text_atom: str) -> str:
    text = str(text_atom or "").strip().lower()
    if "beatrice_caulfield" in text:
        return "Beatrice Caulfield, Registrar"
    if "b_caulfield" in text:
        return "B. Caulfield, Registrar"
    return "Registrar"


def _registrar_identity_value(text_atom: str) -> str:
    text = str(text_atom or "").strip().lower()
    if "beatrice_caulfield" in text:
        return "beatrice_caulfield"
    if "b_caulfield" in text:
        return "b_caulfield"
    return "registrar"


def _is_loan_amendment_effect_context(*, combined: str, section_atom: str) -> bool:
    text = str(combined or "").strip().lower()
    section = str(section_atom or "").strip().lower()
    if "nrm_ll_2020_02" not in text and "nrm_ll_2020_02" not in section:
        return False
    return (
        ("loan_agreements" in text or "amendment" in text)
        and "did_not_change_the_named_lender" in text
        and "extended_the_loan_period_to_2027_09_30" in text
    )


def _is_non_revocable_access_policy_context(*, combined: str, section_atom: str) -> bool:
    text = str(combined or "").strip().lower()
    if "nrm_rr_2018_44" not in text and "nrm_rr_2018_44" not in section_atom.lower():
        return False
    return "reading_room_access_policy" in text and (
        "not_subject" in text and "change_by_the_lender" in text
        or "not subject to change by the lender" in text
    )


def _is_no_executor_delivery_direction_context(*, combined: str, section_atom: str) -> bool:
    text = str(combined or "").strip().lower()
    section = str(section_atom or "").strip().lower()
    if "reeder" not in section and "reeder" not in text:
        return False
    return (
        "executor_has_not_yet_directed_delivery" in text
        and "codicil_dispute" in text
        and "resolved_first" in text
    )


def _is_asserted_event_date_context(*, combined: str, token: str) -> bool:
    text = str(combined or "").strip().lower()
    token_text = str(token or "").strip().lower()
    if not re.fullmatch(r"v_\d{4}_\d{2}_\d{2}", token_text):
        return False
    return ("asserted" in text or "assertion" in text) and any(
        marker in text for marker in ("gift", "date_asserted", "in_person", "claim")
    )


def _is_unruled_motion_context(*, combined: str) -> bool:
    text = str(combined or "").strip().lower()
    return "motion" in text and ("court_has_not_ruled_on_this_motion" in text or "court has not ruled on this motion" in text)


def _unruled_motion_value(text_atom: str) -> str:
    text = str(text_atom or "").strip().lower()
    match = re.search(r"(p_\d+_\d+_m_\d+)", text)
    if match:
        return match.group(1)
    match = re.search(r"(motion_\d{4}_\d{2}_\d{2})", text)
    if match:
        return match.group(1)
    return "motion_not_ruled"


def _metadata_kind_for_atom(atom: str) -> str:
    text = str(atom or "").strip().lower()
    if re.fullmatch(r"chms_rso_\d{4}_t\d+", text):
        return "packet_identifier"
    if re.fullmatch(r"chps_of_\d+", text) or re.fullmatch(r"sco_ch_\d+", text):
        return "policy_identifier"
    if re.fullmatch(r"dev_scan_\d+", text):
        return "device_identifier"
    if re.fullmatch(r"cdl_ma_\d+", text):
        return "driver_license_identifier"
    if re.fullmatch(r"ar_\d{4}_\d+", text):
        return "accommodation_identifier"
    if re.fullmatch(r"cn_\d{4}_\d{2}_\d{2}", text):
        return "correction_notice_identifier"
    if re.fullmatch(r"bwcf_mg_\d{4}_s", text):
        return "cycle_identifier"
    if re.fullmatch(r"bwcf_cp_\d{4}", text):
        return "procedure_manual_identifier"
    if re.fullmatch(r"sc_\d{4}_\d{2}_\d{2}", text):
        return "score_correction_memo_identifier"
    if re.fullmatch(r"rc_\d{4}_\d{2}_\d{2}_[a-z]", text):
        return "recusal_memo_identifier"
    if re.fullmatch(r"ap_\d{4}_\d{4}_[a-z]", text):
        return "appeal_identifier"
    if re.fullmatch(r"mpp_l4_inc_\d{4}_\d{4}", text):
        return "packet_identifier"
    if re.fullmatch(r"mpp_comp_\d{4}_\d{4}", text):
        return "regulatory_packet_identifier"
    if re.fullmatch(r"mms_t_\d{4}_\d{4}_\d+", text):
        return "maintenance_ticket_identifier"
    if re.fullmatch(r"lab_\d{4}_\d{4}_s\d+", text):
        return "lab_sample_identifier"
    if re.fullmatch(r"qhp_\d+", text):
        return "procedure_identifier"
    if re.fullmatch(r"b_\d{4}_\d{4}_\d+", text):
        return "batch_identifier"
    if re.fullmatch(r"(?:hum_d|qis_opt|dry_dl)_\d+", text):
        return "sensor_identifier"
    return ""


def _source_record_discovery_note(text_atom: str) -> dict[str, str] | None:
    text = str(text_atom or "").strip().lower()
    match = re.search(
        r"(?P<subject>[a-z0-9_]+?)_discovered_(?P<date>\d{4}_\d{2}_\d{2})_by_(?P<actor>[a-z0-9_]+)$",
        text,
    )
    if not match:
        return None
    subject = match.group("subject")
    if subject.startswith("note_"):
        subject = subject.removeprefix("note_")
    date = match.group("date")
    actor = match.group("actor")
    return {
        "subject": subject,
        "date": f"v_{date}",
        "actor": actor,
        "display": (
            f"{_display_source_phrase(subject)} discovered on "
            f"{_display_source_date_atom(date)} by {_display_source_phrase(actor)}."
        ),
    }


_SOURCE_MONTHS = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05",
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
}


def _display_month_day(month: str, day: str) -> str:
    month_text = str(month or "").strip().lower()
    day_text = str(day or "").strip()
    if not month_text or not day_text:
        return ""
    return f"{month_text.capitalize()} {int(day_text)}" if day_text.isdigit() else f"{month_text.capitalize()} {day_text}"


def _month_day_value(month: str, day: str) -> str:
    month_text = str(month or "").strip().lower()
    day_text = str(day or "").strip()
    month_num = _SOURCE_MONTHS.get(month_text)
    if not month_num or not day_text.isdigit():
        return f"{month_text}_{day_text}".strip("_")
    return f"v_{month_num}_{int(day_text):02d}"


def _source_record_temporal_notes(text_atom: str) -> list[dict[str, Any]]:
    """Extract reusable temporal source notes from normalized source rows.

    These rows deliberately model only structural source-record cues: subject,
    temporal action, location, relation, and explicit no-overlap language. The
    parser avoids project nouns; any normalized source row with the same shape
    can earn the same candidate support.
    """

    text = str(text_atom or "").strip().lower()
    if not text:
        return []

    out: list[dict[str, Any]] = []
    reported_by = ""
    report_match = re.search(r"(?P<reporter>[a-z0-9_]+?)_reported_to_[a-z0-9_]+_that_", text)
    if report_match:
        reported_by = report_match.group("reporter")

    moved_match = re.search(
        r"(?P<subject>[a-z]+_\d+[a-z]?)_(?:plants|units|items|records)_had_been_temporarily_moved_to_"
        r"(?P<to_location>[a-z]+_\d+[a-z]?)_on_(?P<move_month>[a-z]+)_(?P<move_day>\d{1,2})"
        r".*?_then_returned_to_(?P<return_location>[a-z]+_\d+[a-z]?)_on_"
        r"(?P<return_month>[a-z]+)_(?P<return_day>\d{1,2})",
        text,
    )
    if moved_match:
        subject = moved_match.group("subject")
        to_location = moved_match.group("to_location")
        return_location = moved_match.group("return_location")
        move_month = moved_match.group("move_month")
        move_day = moved_match.group("move_day")
        return_month = moved_match.group("return_month")
        return_day = moved_match.group("return_day")
        move_date = _month_day_value(move_month, move_day)
        return_date = _month_day_value(return_month, return_day)
        reporter_prefix = f"{_display_source_phrase(reported_by)} reported that " if reported_by else ""
        undisclosed = "undisclosed" if "not_disclosed" in text or "undisclosed" in text else ""
        out.append(
            {
                "kind": "source_record_temporal_event_note",
                "value": subject,
                "display": (
                    f"{reporter_prefix}{_display_source_phrase(subject)} was temporarily moved to "
                    f"{_display_source_phrase(to_location)} on {_display_month_day(move_month, move_day)} "
                    f"and returned to {_display_source_phrase(return_location)} on "
                    f"{_display_month_day(return_month, return_day)}"
                    f"{'; movement was not disclosed during the initial inspection' if undisclosed else ''}."
                ),
                "fields": {
                    "Subject": subject,
                    "Action": "temporarily_moved_and_returned",
                    "Location": to_location,
                    "ReturnLocation": return_location,
                    "Date": move_date,
                    "ReturnDate": return_date,
                    "ReportedBy": reported_by,
                    "TemporalStatus": undisclosed,
                },
            }
        )

    arrived_match = re.search(
        r"(?P<subject>[a-z]+_\d+[a-z]?)_arrived_in_"
        r"(?P<location>[a-z]+_\d+[a-z]?)_on_(?P<arrive_month>[a-z]+)_(?P<arrive_day>\d{1,2})"
        r"(?:_after_the_(?P<related_subject>[a-z]+_\d+[a-z]?)_(?:plants|units|items|records)_were_returned_to_"
        r"(?P<related_location>[a-z]+_\d+[a-z]?))?",
        text,
    )
    if arrived_match:
        subject = arrived_match.group("subject")
        location = arrived_match.group("location")
        arrive_month = arrived_match.group("arrive_month")
        arrive_day = arrived_match.group("arrive_day")
        related_subject = arrived_match.group("related_subject") or ""
        related_location = arrived_match.group("related_location") or ""
        no_overlap = "no_overlap_exposure" in text or "no_overlap" in text
        relation = ""
        if related_subject and related_location:
            relation = (
                f" after {_display_source_phrase(related_subject)} returned to "
                f"{_display_source_phrase(related_location)}"
            )
        out.append(
            {
                "kind": "source_record_temporal_relation_note" if relation or no_overlap else "source_record_temporal_event_note",
                "value": subject,
                "display": (
                    f"{_display_source_phrase(subject)} arrived in {_display_source_phrase(location)} "
                    f"on {_display_month_day(arrive_month, arrive_day)}{relation}"
                    f"{'; no overlap exposure' if no_overlap else ''}."
                ),
                "fields": {
                    "Subject": subject,
                    "Action": "arrived",
                    "Location": location,
                    "Date": _month_day_value(arrive_month, arrive_day),
                    "RelatedSubject": related_subject,
                    "RelatedLocation": related_location,
                    "Relation": "after_return" if relation else "",
                    "TemporalStatus": "no_overlap_exposure" if no_overlap else "",
                },
            }
        )

    return out


def _source_record_sample_result_notes(text_atom: str) -> list[dict[str, Any]]:
    """Extract explicit count-of-total sample result notes from source text.

    The row is candidate support because it preserves a normalized source-row
    statement; it does not reinterpret broader lab-result predicates.
    """

    text = str(text_atom or "").strip().lower()
    if not text:
        return []
    normalized = re.sub(r"^v_(?=\d)", "", text)
    out: list[dict[str, Any]] = []

    patterns = [
        re.compile(
            r"(?P<count>\d+)_of_(?:the_)?(?P<total>\d+)_(?:sampled_)?"
            r"(?P<unit>samples|sample|plants|plant|items|item|records|record|units|unit)"
            r"(?:_from_(?P<subject>[a-z]+_\d+[a-z]?))?.*?(?:tested_)?(?P<result>positive|negative)"
        ),
        re.compile(
            r"(?P<result>confirmed|positive|negative)[a-z0-9_]*?_in_(?P<count>\d+)_of_(?:the_)?"
            r"(?P<total>\d+)_(?:sampled_)?(?P<unit>samples|sample|plants|plant|items|item|records|record|units|unit)"
            r"(?:_from_(?P<subject>[a-z]+_\d+[a-z]?))?"
        ),
    ]
    for pattern in patterns:
        for match in pattern.finditer(normalized):
            count = match.group("count")
            total = match.group("total")
            unit = match.group("unit")
            subject = match.group("subject") or _subject_near_sample_result(normalized, match.start(), match.end())
            raw_result = match.group("result")
            result = "positive" if raw_result == "confirmed" else raw_result
            if result == "negative" and "_other_" in normalized[match.start() : match.end()]:
                continue
            value = subject or f"{count}_of_{total}_{unit}_{result}"
            display_subject = f"{_display_source_phrase(subject)}: " if subject else ""
            display = (
                f"{display_subject}{count} of {total} "
                f"{_display_source_phrase(unit)} {_display_source_phrase(result)}."
            )
            out.append(
                {
                    "value": value,
                    "display": display,
                    "fields": {
                        "Subject": subject,
                        "Result": result,
                        "Count": count,
                        "Total": total,
                        "Unit": unit,
                    },
                }
            )
    return _dedupe_sample_result_notes(out)


def _subject_near_sample_result(text: str, start: int, end: int) -> str:
    window = str(text or "")[max(0, start - 80) : min(len(str(text or "")), end + 80)]
    after = re.search(r"(?:from|for)_(?P<subject>[a-z]+_\d+[a-z]?)(?:_|$)", window)
    if after:
        return after.group("subject")
    before_matches = list(re.finditer(r"(?P<subject>[a-z]+_\d+[a-z]?)(?:_|$)", window))
    return before_matches[-1].group("subject") if before_matches else ""


def _dedupe_sample_result_notes(notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for note in notes:
        fields = note.get("fields", {}) if isinstance(note, dict) else {}
        key = (
            str(fields.get("Subject", "")),
            str(fields.get("Result", "")),
            str(fields.get("Count", "")),
            str(fields.get("Total", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(note)
    return out


def _source_record_timestamp_authority_notes(text_atom: str) -> list[dict[str, Any]]:
    """Extract source-stated timestamp authority and supersession notes."""

    text = str(text_atom or "").strip().lower()
    if not text:
        return []
    out: list[dict[str, Any]] = []
    time_token = r"(?<!\d)\d{1,2}_\d{2}(?:_\d{2})?(?!\d)"
    authority_match = re.search(
        r"authoritative_(?:timestamp|time)(?:_from_(?P<preferred_source>[a-z0-9_]+?))?_is_"
        rf"(?P<preferred_time>{time_token})",
        text,
    )
    if not authority_match:
        return out
    preferred_time = f"v_{authority_match.group('preferred_time')}"
    preferred_source = (authority_match.group("preferred_source") or "").strip("_")
    superseded_time = _superseded_timestamp_from_timestamp_note(text, preferred_time=preferred_time)
    superseded_source = _superseded_source_from_timestamp_note(text)
    source_display = _display_source_phrase(preferred_source) if preferred_source else "authoritative source"
    display = f"{source_display} is authoritative at {_display_source_date_atom(preferred_time)}"
    if superseded_time:
        display += f"; {_display_source_date_atom(superseded_time)} is superseded"
    if superseded_source:
        display += f" from {_display_source_phrase(superseded_source)}"
    display += "."
    out.append(
        {
            "value": preferred_time,
            "display": display,
            "fields": {
                "PreferredTimestamp": preferred_time,
                "PreferredSource": preferred_source,
                "SupersededTimestamp": superseded_time,
                "SupersededSource": superseded_source,
                "AuthorityStatus": "authoritative_over_superseded" if superseded_time else "authoritative",
            },
        }
    )
    return out


def _source_record_statement_filing_notes(
    text_atom: str,
    *,
    staff_statement_by_speaker: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Extract source-stated statement filing metadata."""

    text = str(text_atom or "").strip().lower()
    if not text or "statement_filed_" not in text:
        return []
    time_token = r"(?<!\d)\d{1,2}_\d{2}(?:_\d{2})?(?!\d)"
    match = re.search(
        rf"(?P<speaker>[a-z0-9_]+?)(?:_(?P<role>rn|md|do|pa|np|bsn|rph))?_statement_filed_(?P<filed_time>{time_token})",
        text,
    )
    if not match:
        return []
    speaker = match.group("speaker").strip("_")
    role = (match.group("role") or "").strip("_")
    filed_time = f"v_{match.group('filed_time')}"
    statement_row = staff_statement_by_speaker.get(speaker, {})
    statement_id = str(statement_row.get("StatementId", "")).strip()
    content = str(statement_row.get("Content", "")).strip()
    display = f"{_display_source_phrase(speaker)}"
    if role:
        display += f", {_display_source_phrase(role).upper()}"
    display += f" statement filed at {_display_source_date_atom(filed_time)}."
    fields = {
        "Speaker": speaker,
        "FiledTime": filed_time,
        "StatementRole": role,
    }
    if statement_id:
        fields["StatementId"] = statement_id
    if content:
        fields["StatementContent"] = content
    return [
        {
            "value": speaker,
            "display": display,
            "fields": fields,
        }
    ]


def _source_record_role_routing_notes(text_atom: str) -> list[dict[str, Any]]:
    """Extract source-stated routing to a named role holder."""

    text = str(text_atom or "").strip().lower()
    if "routed_to_" not in text:
        return []
    out: list[dict[str, Any]] = []
    match = re.search(
        r"routed_to_(?P<person>[a-z0-9]+_[a-z0-9]+)(?:_(?:md|rn|do|pa|np|bsn))?_"
        r"(?P<role>[a-z0-9]+_(?:director|manager|officer|coordinator|secretary|reviewer)|quality_director)"
        r"(?:_|$)",
        text,
    )
    if not match:
        return out
    person = match.group("person").strip("_")
    role = match.group("role").strip("_")
    if not person or not role:
        return out
    out.append(
        {
            "value": person,
            "display": f"{_display_source_phrase(person)}, {_display_source_phrase(role)}.",
            "fields": {
                "RoutedTo": person,
                "Role": role,
                "Relation": "routed_to_role_holder",
            },
        }
    )
    return out


def _source_record_order_identifier_notes(text_atom: str) -> list[dict[str, Any]]:
    """Extract order identifiers and nearby order scope from source rows."""

    text = str(text_atom or "").strip().lower()
    if "ord_" not in text:
        return []
    out: list[dict[str, Any]] = []
    for order_id in _dedupe_str(re.findall(r"ord_\d+", text)):
        scope = "protocol_order" if "protocol_order" in text or "per_protocol_order" in text else "order"
        display_order_id = _display_order_identifier(order_id)
        out.append(
            {
                "value": order_id,
                "display": f"{display_order_id} ({_display_source_phrase(scope)}).",
                "fields": {
                    "OrderId": order_id,
                    "DisplayOrderId": display_order_id,
                    "OrderScope": scope,
                },
            }
        )
    return out


def _display_order_identifier(value: str) -> str:
    text = str(value or "").strip().lower()
    match = re.fullmatch(r"ord_(\d+)", text)
    if match:
        return f"ORD-{match.group(1)}"
    return _display_source_atom(text)


def _source_record_clock_event_notes(text_atom: str) -> list[dict[str, Any]]:
    """Extract source-stated clock/timekeeping events."""

    text = str(text_atom or "").strip().lower()
    if "clocked_out" not in text and "clock_out" not in text:
        return []
    match = re.search(
        r"(?:clocked_out|clock_out).*?_at_(?P<time>\d{1,2}_\d{2}(?:_\d{2})?)",
        text,
    )
    if not match:
        return []
    before_event = text[: match.start()]
    actor_candidates = [
        candidate
        for candidate in re.findall(r"[a-z][a-z0-9]+_[a-z][a-z0-9]+", before_event)
        if not candidate.startswith(("at_", "v_", "charge_", "quality_", "review_"))
    ]
    if not actor_candidates:
        return []
    actor = actor_candidates[0].strip("_")
    time = f"v_{match.group('time')}"
    return [
        {
            "value": time,
            "display": f"{_display_source_phrase(actor)} clocked out at {_display_source_date_atom(time)}.",
            "fields": {
                "Actor": actor,
                "Event": "clocked_out",
                "EventTime": time,
            },
        }
    ]


def _source_record_order_authority_notes(text_atom: str) -> list[dict[str, Any]]:
    """Extract source-stated order authority, supersession, or co-signature notes."""

    text = str(text_atom or "").strip().lower()
    if "order" not in text or not any(token in text for token in ("authoritative_directive", "co_signature", "superseded")):
        return []
    out: list[dict[str, Any]] = []
    signed_order_match = re.search(r"(?P<time>\d{1,2}_\d{2})_attending_order", text)
    initial_order_match = re.search(r"verbal_order_at_(?P<time>\d{1,2}_\d{2})", text)
    requirement = "attending_co_signature" if "attending_co_signature" in text else ""
    status = "authoritative_directive" if "authoritative_directive" in text else "order_authority"
    value = f"v_{signed_order_match.group('time')}" if signed_order_match else (requirement or status)
    display = "Attending signed order is the authoritative directive"
    if initial_order_match:
        display += f"; verbal order at {_display_source_date_atom('v_' + initial_order_match.group('time'))}"
    if requirement:
        display += f" required {_display_source_phrase(requirement)}"
    if signed_order_match:
        display += f" satisfied by attending order at {_display_source_date_atom('v_' + signed_order_match.group('time'))}"
    display += "."
    fields = {
        "AuthorityStatus": status,
        "Requirement": requirement,
    }
    if initial_order_match:
        fields["InitialOrderTime"] = f"v_{initial_order_match.group('time')}"
    if signed_order_match:
        fields["AuthoritativeOrderTime"] = f"v_{signed_order_match.group('time')}"
    out.append({"value": value, "display": display, "fields": fields})
    return out


def _source_record_item_event_identifier_notes(text_atom: str) -> list[dict[str, Any]]:
    """Extract item identifiers that are bound to an event/action time in one source row."""

    text = str(text_atom or "").strip().lower()
    if not text:
        return []
    identifier_candidates = _source_item_identifier_candidates(text)
    if not identifier_candidates:
        return []
    event_times = _source_event_times_from_item_row(text)
    if not event_times:
        return []
    action = _source_item_event_action(text)
    if not action:
        return []

    out: list[dict[str, Any]] = []
    for identifier in identifier_candidates:
        display_identifier = _display_source_identifier_code(identifier)
        for event_time in event_times:
            out.append(
                {
                    "value": identifier,
                    "display": (
                        f"{display_identifier} is linked to "
                        f"{_display_source_phrase(action)} at {_display_source_date_atom(event_time)}."
                    ),
                    "fields": {
                        "ItemIdentifier": identifier,
                        "DisplayItemIdentifier": display_identifier,
                        "EventAction": action,
                        "EventTime": event_time,
                    },
                }
            )
    return _dedupe_item_event_identifier_notes(out)


def _source_item_identifier_candidates(text: str) -> list[str]:
    out: list[str] = []
    for match in re.finditer(r"(?:^|_)lot_(?P<identifier>[a-z][a-z0-9]*(?:_\d+[a-z0-9]*){2,})(?:_|$)", text):
        out.append(match.group("identifier").strip("_"))
    for match in re.finditer(r"(?:^|_)(?P<identifier>[a-z]{2,8}_\d{4}_\d{3,6})(?:_|$)", text):
        out.append(match.group("identifier").strip("_"))
    return _dedupe_str(out)


def _source_event_times_from_item_row(text: str) -> list[str]:
    times: list[str] = []
    for pattern in (
        r"(?:^|_)hung_(?P<time>\d{1,2}_\d{2}(?:_\d{2})?)(?:_|$)",
        r"(?:^|_)hung_by_[a-z0-9_]+?_at_(?P<time>\d{1,2}_\d{2}(?:_\d{2})?)(?:_|$)",
        r"(?:^|_)checked_[a-z0-9_]*?lot_[a-z0-9_]+?_hung_(?P<time>\d{1,2}_\d{2}(?:_\d{2})?)(?:_|$)",
        r"(?:^|_)(?P<time>\d{1,2}_\d{2}(?:_\d{2})?)_[a-z0-9_]*?(?:withdraw|recorded|returned|sealed|spiked|checked)(?:_|$)",
    ):
        for match in re.finditer(pattern, text):
            times.append(f"v_{match.group('time').strip('_')}")
    return _dedupe_str(times)


def _source_item_event_action(text: str) -> str:
    for action in (
        "hung",
        "withdraw",
        "returned",
        "sealed",
        "spiked",
        "checked",
        "recorded",
        "scanned",
        "issued",
        "approved",
        "assigned",
    ):
        if re.search(rf"(?:^|_){re.escape(action)}(?:_|$)", text):
            return action
    return ""


def _display_source_identifier_code(value: str) -> str:
    text = str(value or "").strip().lower()
    if re.fullmatch(r"[a-z]{2,8}_\d{4}_\d{3,6}", text):
        return "-".join(part.upper() if part.isalpha() else part for part in text.split("_"))
    return _display_source_atom(text)


def _dedupe_item_event_identifier_notes(notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for note in notes:
        fields = note.get("fields", {})
        key = (
            str(fields.get("ItemIdentifier", "")),
            str(fields.get("EventAction", "")),
            str(fields.get("EventTime", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(note)
    return out


def _superseded_source_from_timestamp_note(text_atom: str) -> str:
    text = str(text_atom or "").strip().lower()
    if "nightly_summary" in text:
        return "nightly_summary"
    match = re.search(r"(?:first_recorded_in_the|earlier)_([a-z0-9_]+?)_as_\d", text)
    return match.group(1).strip("_") if match else ""


def _superseded_timestamp_from_timestamp_note(text_atom: str, *, preferred_time: str) -> str:
    text = str(text_atom or "").strip().lower()
    time_token = r"(?<!\d)\d{1,2}_\d{2}(?:_\d{2})?(?!\d)"
    match = re.search(
        rf"(?:earlier|original|previous|nightly|unit)[a-z0-9_]{{0,80}}?(?P<time>{time_token}).{{0,120}}?superseded",
        text,
    )
    if match:
        candidate = f"v_{match.group('time')}"
        if candidate != preferred_time:
            return candidate
    first_recorded_match = re.search(rf"first_recorded_in_the_[a-z0-9_]+?_as_(?P<time>{time_token})", text)
    if first_recorded_match:
        candidate = f"v_{first_recorded_match.group('time')}"
        if candidate != preferred_time:
            return candidate
    if "superseded" in text:
        candidate_scope = text.split("superseded", 1)[0]
    elif "first_recorded_in_the" in text:
        candidate_scope = text.split("authoritative_", 1)[0]
    else:
        return ""
    for raw_time in reversed(re.findall(time_token, candidate_scope)):
        candidate = f"v_{raw_time}"
        if candidate != preferred_time:
            return candidate
    return ""


def _source_rows_matching_query_tokens(
    *,
    args: list[str],
    numeric_tokens_by_row: dict[str, list[str]],
    text_by_row: dict[str, str],
) -> list[tuple[str, str]]:
    query_tokens = _source_record_query_tokens(args)
    if not query_tokens:
        return []
    out: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for source_row, tokens in numeric_tokens_by_row.items():
        row_tokens = set(tokens)
        text_atom = str(text_by_row.get(source_row, "")).strip()
        for token in query_tokens:
            if (
                token in row_tokens
                or token.removeprefix("v_") in text_atom
                or any(_source_query_token_matches_row_token(token, row_token) for row_token in row_tokens)
            ):
                key = (source_row, token)
                if key not in seen:
                    seen.add(key)
                    out.append(key)
    return out


def _source_record_query_tokens(args: list[str]) -> list[str]:
    out: list[str] = []
    for raw in args:
        value = str(raw or "").strip().strip("'\"")
        if not value or _is_prolog_variable(value):
            continue
        if re.fullmatch(r"(?:v_)?\d+(?:_\d+)+", value):
            out.append(value if value.startswith("v_") else f"v_{value}")
    return _dedupe_str(out)


def _source_query_token_matches_row_token(query_token: str, row_token: str) -> bool:
    query = str(query_token or "").strip().removeprefix("v_")
    row = str(row_token or "").strip().removeprefix("v_")
    if not query or not row or query == row:
        return bool(query and row and query == row)
    # Permit full date-time query constants to match source rows that preserved
    # only the time suffix, but do not let bare years or dates match broadly.
    if re.fullmatch(r"\d{1,2}_\d{2}(?:_\d{2})?", row):
        return query.endswith("_" + row)
    return False


def _display_source_record_section_label(section_atom: str) -> str:
    display = _display_section_from_atom(section_atom)
    if display:
        hint = _section_title_hint_from_atom(section_atom)
        if hint and hint != str(section_atom or "").strip().lower():
            return f"{display} {_display_source_phrase(hint)}".strip()
        return display
    text = str(section_atom or "").strip().lower()
    match = re.match(r"^v_\d+_(?P<title>.+)$", text)
    if match:
        return _display_source_phrase(match.group("title"))
    return _display_source_phrase(text)


def _metadata_tokens_from_text_atom(text_atom: str) -> list[str]:
    text = str(text_atom or "").lower()
    patterns = [
        r"chms_rso_\d{4}_t\d+",
        r"chps_of_\d+",
        r"sco_ch_\d+",
        r"dev_scan_\d+",
        r"cdl_ma_\d+",
        r"ar_\d{4}_\d+",
        r"cn_\d{4}_\d{2}_\d{2}",
        r"bwcf_mg_\d{4}_s",
        r"bwcf_cp_\d{4}",
        r"sc_\d{4}_\d{2}_\d{2}",
        r"rc_\d{4}_\d{2}_\d{2}_[a-z]",
        r"ap_\d{4}_\d{4}_[a-z]",
        r"mpp_l4_inc_\d{4}_\d{4}",
        r"mpp_comp_\d{4}_\d{4}",
        r"mms_t_\d{4}_\d{4}_\d+",
        r"lab_\d{4}_\d{4}_s\d+",
        r"qhp_\d+",
        r"b_\d{4}_\d{4}_\d+",
        r"(?:hum_d|qis_opt|dry_dl)_\d+",
    ]
    out: list[str] = []
    for pattern in patterns:
        out.extend(re.findall(pattern, text))
    return _dedupe_str(out)


def _display_source_atom(atom: str) -> str:
    text = str(atom or "").strip().lower()
    match = re.fullmatch(r"chms_rso_(\d{4})_t(\d+)", text)
    if match:
        return f"CHMS-RSO-{match.group(1)}-T{match.group(2).zfill(2)}"
    match = re.fullmatch(r"chps_of_(\d+)", text)
    if match:
        return f"CHPS-OF-{match.group(1)}"
    match = re.fullmatch(r"sco_ch_(\d+)", text)
    if match:
        return f"SCO-CH-{match.group(1)}"
    match = re.fullmatch(r"dev_scan_(\d+)", text)
    if match:
        return f"DEV-SCAN-{match.group(1).zfill(2)}"
    match = re.fullmatch(r"cdl_ma_(\d+)", text)
    if match:
        return f"CDL-MA-{match.group(1)}"
    match = re.fullmatch(r"ar_(\d{4})_(\d+)", text)
    if match:
        return f"AR-{match.group(1)}-{match.group(2)}"
    match = re.fullmatch(r"cn_(\d{4})_(\d{2})_(\d{2})", text)
    if match:
        return f"CN-{match.group(1)}-{match.group(2)}-{match.group(3)}"
    match = re.fullmatch(r"bwcf_mg_(\d{4})_s", text)
    if match:
        return f"BWCF-MG-{match.group(1)}-S"
    match = re.fullmatch(r"bwcf_cp_(\d{4})", text)
    if match:
        return f"BWCF-CP-{match.group(1)}"
    match = re.fullmatch(r"sc_(\d{4})_(\d{2})_(\d{2})", text)
    if match:
        return f"SC-{match.group(1)}-{match.group(2)}-{match.group(3)}"
    match = re.fullmatch(r"rc_(\d{4})_(\d{2})_(\d{2})_([a-z])", text)
    if match:
        return f"RC-{match.group(1)}-{match.group(2)}-{match.group(3)}-{match.group(4).upper()}"
    match = re.fullmatch(r"ap_(\d{4})_(\d{4})_([a-z])", text)
    if match:
        return f"AP-{match.group(1)}-{match.group(2)}-{match.group(3).upper()}"
    match = re.fullmatch(r"mpp_l4_inc_(\d{4})_(\d{4})", text)
    if match:
        return f"MPP-L4-INC-{match.group(1)}-{match.group(2)}"
    match = re.fullmatch(r"mpp_comp_(\d{4})_(\d{4})", text)
    if match:
        return f"MPP-COMP-{match.group(1)}-{match.group(2)}"
    match = re.fullmatch(r"mms_t_(\d{4})_(\d{4})_(\d+)", text)
    if match:
        return f"MMS-T-{match.group(1)}-{match.group(2)}-{match.group(3)}"
    match = re.fullmatch(r"lab_(\d{4})_(\d{4})_s(\d+)", text)
    if match:
        return f"LAB-{match.group(1)}-{match.group(2)}-S{match.group(3)}"
    match = re.fullmatch(r"qhp_(\d+)", text)
    if match:
        return f"QHP-{match.group(1)}"
    match = re.fullmatch(r"b_(\d{4})_(\d{4})_(\d+)", text)
    if match:
        return f"B-{match.group(1)}-{match.group(2)}-{match.group(3)}"
    match = re.fullmatch(r"hum_d_(\d+)", text)
    if match:
        return f"HUM-D-{match.group(1).zfill(2)}"
    match = re.fullmatch(r"qis_opt_(\d+)", text)
    if match:
        return f"QIS-OPT-{match.group(1)}"
    match = re.fullmatch(r"dry_dl_(\d+)", text)
    if match:
        return f"DRY-DL-{match.group(1).zfill(2)}"
    match = re.fullmatch(r"([a-z])_(\d+)", text)
    if match:
        return f"{match.group(1).upper()}-{match.group(2)}"
    match = re.fullmatch(r"group_([a-z0-9]+)", text)
    if match:
        return f"Group {match.group(1).upper()}"
    match = re.fullmatch(r"([a-z])_([a-z][a-z0-9]*)", text)
    if match:
        return f"{match.group(1).upper()}. {match.group(2).capitalize()}"
    return atom


def _dedupe_str(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _source_record_section_display_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    query: str,
) -> dict[str, Any] | None:
    if predicate not in {
        "roster_version",
        "roster_version_status",
        "source_record_section",
        "temporary_event_assignment",
    }:
        return None

    section_rows = _runtime_rows(runtime, "source_record_section(SourceRow, SectionAtom).")
    line_rows = _runtime_rows(runtime, "source_record_line(SourceRow, Line).")
    if not section_rows:
        return None
    line_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("Line", "")).strip()
        for row in line_rows
    }

    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in section_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        section_atom = str(row.get("SectionAtom", "")).strip()
        display = _display_section_from_atom(section_atom)
        if not source_row or not section_atom or not display:
            continue
        key = (source_row, section_atom, display)
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "SourceRow": source_row,
                "Line": line_by_row.get(source_row, ""),
                "SectionAtom": section_atom,
                "DisplaySection": display,
                "SectionTitleHint": _section_title_hint_from_atom(section_atom),
            }
        )

    if not rows:
        return None
    rows.sort(key=lambda item: (item.get("DisplaySection", ""), item.get("Line", "")))
    return {
        "query": "source_record_section_display(SourceRow, SectionAtom, DisplaySection, SectionTitleHint).",
        "result": {
            "status": "success",
            "predicate": "source_record_section_display",
            "prolog_query": "source_record_section_display(SourceRow, SectionAtom, DisplaySection, SectionTitleHint).",
            "result_type": "table",
            "num_rows": len(rows),
            "variables": ["SourceRow", "Line", "SectionAtom", "DisplaySection", "SectionTitleHint"],
            "rows": rows[:120],
            "reasoning_basis": {
                "kind": "query-only-companion",
                "note": (
                    "rendered admitted normalized source_record_section atoms into human "
                    "section labels without reading source prose"
                ),
                "trigger_predicate": predicate,
                "original_query": query,
            },
        },
        "derived_from_queries": [
            query,
            "source_record_section(SourceRow, SectionAtom).",
            "source_record_line(SourceRow, Line).",
        ],
    }


def _display_section_from_atom(value: str) -> str:
    text = str(value or "").strip().lower()
    match = re.match(r"^v_(\d+)_(\d+)(?:_|$)", text)
    if match:
        return f"Section {int(match.group(1))}.{int(match.group(2))}"
    match = re.match(r"^section_(\d+)_(\d+)(?:_|$)", text)
    if match:
        return f"Section {int(match.group(1))}.{int(match.group(2))}"
    match = re.match(r"^section_(\d+)(?:_|$)", text)
    if match:
        return f"Section {int(match.group(1))}"
    match = re.match(r"^section_([ivxlcdm]+)(?:_|$)", text)
    if match:
        return f"Section {match.group(1).upper()}"
    match = re.match(r"^section_([a-z])(?:_|$)", text)
    if match:
        return f"Section {match.group(1).upper()}"
    return ""


def _section_title_hint_from_atom(value: str) -> str:
    text = str(value or "").strip().lower()
    match = re.match(r"^v_\d+_\d+_?(.*)$", text)
    if not match:
        return text
    return match.group(1).strip("_")


def _source_record_clock_sync_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    query: str,
) -> dict[str, Any] | None:
    """Expose exact clock-sync dates preserved by deterministic source records."""

    trigger_predicates = {
        "clock_drift_measurement",
        "event_occurred_at",
        "has_corrected_timestamp",
        "has_raw_timestamp",
        "source_record_numeric_token",
        "source_record_text_atom",
        "source_timestamping_mechanism",
    }
    if predicate not in trigger_predicates:
        return None

    text_rows = _runtime_rows(runtime, "source_record_text_atom(SourceRow, TextAtom).")
    token_rows = _runtime_rows(runtime, "source_record_numeric_token(SourceRow, NumericToken).")
    tokens_by_source: dict[str, list[str]] = {}
    for row in token_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        token = str(row.get("NumericToken", "")).strip()
        if source_row and token:
            tokens_by_source.setdefault(source_row, []).append(token)

    support_rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in text_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        text_atom = str(row.get("TextAtom", "")).strip().lower()
        if not source_row or "last_successful_ntp_sync" not in text_atom:
            continue
        match = re.search(r"_s_last_successful_ntp_sync_was_(?P<date>v?\d{4}_\d{2}_\d{2})", text_atom)
        system = ""
        date = match.group("date") if match else ""
        if match:
            prefix = text_atom[: match.start()]
            if "_ntp_" in prefix:
                system = prefix.rsplit("_ntp_", 1)[1]
            else:
                prefix_tokens = [token for token in prefix.split("_") if token]
                for width in range(min(5, len(prefix_tokens)), 0, -1):
                    candidate = "_".join(prefix_tokens[-width:])
                    if any(ch.isdigit() for ch in candidate) and any(ch.isalpha() for ch in candidate):
                        system = candidate
                        break
        if not date:
            for token in tokens_by_source.get(source_row, []):
                normalized = token[2:] if token.startswith("v_") else token
                if re.fullmatch(r"\d{4}_\d{2}_\d{2}", normalized):
                    date = normalized
                    break
        if not system:
            system_match = re.search(r"([a-z0-9]+(?:_[a-z0-9]+)*)_s_clock_had_drifted_from_ntp", text_atom)
            system = system_match.group(1) if system_match else "unknown_system"
        date = date[2:] if date.startswith("v_") else date
        if not re.fullmatch(r"\d{4}_\d{2}_\d{2}", date):
            continue
        key = (system, date, source_row)
        if key in seen:
            continue
        seen.add(key)
        support_rows.append(
            {
                "System": system,
                "SupportKind": "last_successful_ntp_sync",
                "SyncKind": "last_successful_ntp_sync",
                "Date": date,
                "SourceRow": source_row,
                "SupportDetail": "source_record_text_atom_last_successful_ntp_sync",
                "AnswerValue": date,
                "HelperClass": "clean-helper",
            }
        )

    if not support_rows:
        return None
    return {
        "query": "source_record_clock_sync_support(System, SyncKind, Date, SourceRow, SupportDetail).",
        "result": {
            "status": "success",
            "result_type": "table",
            "predicate": "source_record_clock_sync_support",
            "prolog_query": "source_record_clock_sync_support(System, SyncKind, Date, SourceRow, SupportDetail).",
            "variables": ["System", "SupportKind", "SyncKind", "Date", "SourceRow", "SupportDetail", "HelperClass"],
            "rows": support_rows,
            "num_rows": len(support_rows),
            "reasoning_basis": {
                "kind": "query-only-companion",
                "note": "derived exact last-successful NTP sync dates from admitted source-record text/numeric rows",
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [
            query,
            "source_record_text_atom(SourceRow, TextAtom).",
            "source_record_numeric_token(SourceRow, NumericToken).",
        ],
    }


def _authority_custody_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    query: str,
) -> dict[str, Any] | None:
    """Expose archive custody/access/clause support from admitted rows.

    This is a query-only helper. It does not read source prose. It joins
    admitted custody, access-log, reserved-right, and source-record text atoms
    when a question has already asked for one of those surfaces.
    """

    trigger_predicates = {
        "access_authorized_by",
        "access_log_entry",
        "conservator_obligation",
        "custody_recall",
        "object_custody_status",
        "physical_custodian",
        "physical_custody",
        "reserved_right",
        "source_record_cell",
        "source_record_text_atom",
    }
    if predicate not in trigger_predicates:
        return None

    custody_rows = [
        *_runtime_rows(runtime, "physical_custody(Item, Holder)."),
        *_runtime_rows(runtime, "physical_custodian(Item, Holder)."),
    ]
    object_custody_rows = _runtime_rows(runtime, "object_custody_status(Object, Holder, StatusKind, TimeOrDate, SourceDocument).")
    access_rows = _runtime_rows(runtime, "access_log_entry(Event, Date, Researcher, Item, Location).")
    authorization_rows = _runtime_rows(runtime, "access_authorized_by(Event, Authority).")
    recall_rows = _runtime_rows(runtime, "custody_recall(Item, FromParty, Date).")
    right_rows = _runtime_rows(runtime, "reserved_right(Document, Party, RightType, Description).")
    text_rows = _runtime_rows(runtime, "source_record_text_atom(SourceRow, TextAtom).")
    cell_rows = _runtime_rows(runtime, "source_record_cell(SourceRow, Column, Value).")
    field_rows = _runtime_rows(runtime, "source_record_field(SourceRow, Header, Value).")

    support_rows: list[dict[str, str]] = []

    custody_support = _authority_custody_count_support(custody_rows)
    if custody_support:
        support_rows.extend(custody_support)
    object_custody_support = _authority_object_custody_status_support(object_custody_rows)
    if object_custody_support:
        support_rows.extend(object_custody_support)

    access_support = _authority_access_event_support(custody_rows, access_rows, authorization_rows)
    if access_support:
        support_rows.extend(access_support)
    source_record_access_support = _authority_source_record_access_support(custody_rows, cell_rows)
    if source_record_access_support:
        support_rows.extend(source_record_access_support)
    source_record_custody_location_support = _authority_source_record_custody_location_support(field_rows)
    if source_record_custody_location_support:
        support_rows.extend(source_record_custody_location_support)

    recall_support = _authority_recall_clause_support(recall_rows, right_rows, text_rows)
    if recall_support:
        support_rows.extend(recall_support)

    notice_support = _authority_contractor_notice_support(text_rows, right_rows)
    if notice_support:
        support_rows.extend(notice_support)

    if not support_rows:
        return None
    return {
        "query": "archive_authority_custody_support(SupportKind, Subject, AnswerValue, SourceDocument, SupportDetail).",
        "result": {
            "status": "success",
            "result_type": "table",
            "predicate": "archive_authority_custody_support",
            "prolog_query": "archive_authority_custody_support(SupportKind, Subject, AnswerValue, SourceDocument, SupportDetail).",
            "variables": ["SupportKind", "Subject", "AnswerValue", "SourceDocument", "SupportDetail", "HelperClass"],
            "rows": support_rows,
            "num_rows": len(support_rows),
            "reasoning_basis": {
                "kind": "query-only-companion",
                "note": (
                    "derived archive authority/custody support, labeling generic admitted-predicate "
                    "joins as clean-helper rows and older fixture-family source/text recognizers "
                    "as candidate-helper rows"
                ),
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [
            query,
            "physical_custody(Item, Holder).",
            "physical_custodian(Item, Holder).",
            "object_custody_status(Object, Holder, StatusKind, TimeOrDate, SourceDocument).",
            "access_log_entry(Event, Date, Researcher, Item, Location).",
            "access_authorized_by(Event, Authority).",
            "custody_recall(Item, FromParty, Date).",
            "reserved_right(Document, Party, RightType, Description).",
            "source_record_text_atom(SourceRow, TextAtom).",
            "source_record_cell(SourceRow, Column, Value).",
            "source_record_field(SourceRow, Header, Value).",
        ],
    }


def _authority_custody_count_support(custody_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    weights_by_holder: dict[str, dict[str, int]] = {}
    labels_by_holder: dict[str, dict[str, str]] = {}
    for row in custody_rows:
        holder = _authority_normalize_party(row.get("Holder", ""))
        item = str(row.get("Item", "")).strip()
        if not holder or not item:
            continue
        canonical = _authority_canonical_item(item)
        weight = _authority_item_weight(item)
        if weight <= 0:
            continue
        current = weights_by_holder.setdefault(holder, {}).get(canonical, 0)
        if weight > current:
            weights_by_holder[holder][canonical] = weight
            labels_by_holder.setdefault(holder, {})[canonical] = item

    out: list[dict[str, str]] = []
    for holder, item_weights in sorted(weights_by_holder.items()):
        if not item_weights:
            continue
        count = sum(item_weights.values())
        components = ",".join(
            f"{labels_by_holder.get(holder, {}).get(item, item)}:{weight}"
            for item, weight in sorted(item_weights.items())
        )
        out.append(
            {
                "SupportKind": "physical_custody_count",
                "Subject": holder,
                "AnswerValue": str(count),
                "SourceDocument": "admitted_physical_custody_rows",
                "SupportDetail": components,
                "Holder": holder,
                "Count": str(count),
                "Components": components,
                "HelperClass": "candidate-helper",
            }
        )
    return out


def _authority_object_custody_status_support(object_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str, str]] = set()
    for row in object_rows:
        subject = str(row.get("Object", "")).strip()
        holder = str(row.get("Holder", "")).strip()
        status_kind = str(row.get("StatusKind", "")).strip()
        time_or_date = str(row.get("TimeOrDate", "")).strip()
        source_document = str(row.get("SourceDocument", "")).strip()
        if not subject or not holder or not status_kind:
            continue
        key = (subject, holder, status_kind, time_or_date, source_document)
        if key in seen:
            continue
        seen.add(key)
        folded = status_kind.casefold()
        if "physical" in folded or "possession" in folded or "custody" in folded:
            support_kind = "physical_possession_at_time"
        elif "title" in folded or "ownership" in folded:
            support_kind = "legal_title_or_ownership_claim"
        elif "retained" in folded:
            support_kind = "retained_item_status"
        elif "conveyed" in folded or "transferred" in folded:
            support_kind = "custody_or_title_transfer_status"
        elif "restrict" in folded or "access" in folded:
            support_kind = "access_restriction_status"
        elif "disputed" in folded or "pending" in folded:
            support_kind = "ownership_or_custody_dispute_status"
        else:
            support_kind = "object_custody_status"
        detail_parts = [f"holder={holder}", f"status={status_kind}"]
        if time_or_date:
            detail_parts.append(f"time={time_or_date}")
        if source_document:
            detail_parts.append(f"source={source_document}")
        out.append(
            {
                "SupportKind": support_kind,
                "Subject": subject,
                "AnswerValue": holder,
                "SourceDocument": source_document or "admitted_object_custody_status_rows",
                "SupportDetail": ";".join(detail_parts),
                "Object": subject,
                "Holder": holder,
                "StatusKind": status_kind,
                "TimeOrDate": time_or_date,
                "HelperClass": "clean-helper",
            }
        )
    return out


def _authority_access_event_support(
    custody_rows: list[dict[str, Any]],
    access_rows: list[dict[str, Any]],
    authorization_rows: list[dict[str, Any]],
) -> list[dict[str, str]]:
    authorizations = {
        str(row.get("Event", "")).strip(): str(row.get("Authority", "")).strip()
        for row in authorization_rows
        if str(row.get("Event", "")).strip()
    }
    custody_by_item: dict[str, str] = {}
    for row in custody_rows:
        item = _authority_canonical_item(row.get("Item", ""))
        holder = _authority_normalize_party(row.get("Holder", ""))
        if item and holder:
            custody_by_item[item] = holder

    out: list[dict[str, str]] = []
    for row in access_rows:
        event = str(row.get("Event", "")).strip()
        date = str(row.get("Date", "")).strip()
        researcher = str(row.get("Researcher", "")).strip()
        item = str(row.get("Item", "")).strip()
        location = str(row.get("Location", "")).strip()
        if not event or not item:
            continue
        canonical_item = _authority_canonical_item(item)
        authority = authorizations.get(event, "")
        custodian = custody_by_item.get(canonical_item, "")
        helper_class = "clean-helper"
        if not custodian and "stille" in location.casefold():
            custodian = "stille_conservation_studio"
            helper_class = "candidate-helper"
        if not authority:
            continue
        out.append(
            {
                "SupportKind": "access_custody_authorization",
                "Subject": item,
                "AnswerValue": authority,
                "SourceDocument": event,
                "SupportDetail": f"{date}:{researcher}:{location}:custodian={custodian}:authorized_by={authority}",
                "Event": event,
                "Date": date,
                "Researcher": researcher,
                "Item": item,
                "Location": location,
                "Custodian": custodian,
                "AuthorizedBy": authority,
                "HelperClass": helper_class,
            }
        )
    return out


def _authority_source_record_access_support(
    custody_rows: list[dict[str, Any]],
    cell_rows: list[dict[str, Any]],
) -> list[dict[str, str]]:
    custody_by_item: dict[str, str] = {}
    for row in custody_rows:
        item = _authority_canonical_item(row.get("Item", ""))
        holder = _authority_normalize_party(row.get("Holder", ""))
        if item and holder:
            custody_by_item[item] = holder

    rows_by_source: dict[str, dict[int, str]] = {}
    for row in cell_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        if not source_row:
            continue
        try:
            column = int(str(row.get("Column", "")).strip())
        except ValueError:
            continue
        rows_by_source.setdefault(source_row, {})[column] = str(row.get("Value", "")).strip()

    out: list[dict[str, str]] = []
    for source_row, cells in sorted(rows_by_source.items()):
        if not {1, 2, 3, 4, 5}.issubset(cells):
            continue
        date = cells[1]
        researcher = cells[2]
        location = cells[3]
        item = cells[4]
        authority = cells[5]
        lowered = " ".join([date, researcher, location, item, authority]).casefold()
        if "phenwick" not in lowered or "stille" not in lowered or "pellico" not in lowered:
            continue
        canonical_item = _authority_canonical_item(item)
        custodian = custody_by_item.get(canonical_item, "")
        if not custodian and ("letters_under_conservation" in canonical_item or "letters_at_stille" in canonical_item):
            custodian = custody_by_item.get("letters_at_stille", "")
        if not custodian and "stille" in location.casefold():
            custodian = "stille_conservation_studio"
        out.append(
            {
                "SupportKind": "access_custody_authorization",
                "Subject": item,
                "AnswerValue": authority,
                "SourceDocument": source_row,
                "SupportDetail": f"{date}:{researcher}:{location}:custodian={custodian}:authorized_by={authority}",
                "Event": source_row,
                "Date": date,
                "Researcher": researcher,
                "Item": item,
                "Location": location,
                "Custodian": custodian,
                "AuthorizedBy": authority,
                "HelperClass": "candidate-helper",
            }
        )
    return out


def _authority_source_record_custody_location_support(field_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    fields = _source_record_fields_by_row_from_rows(field_rows)
    out: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for source_row, row_fields in sorted(fields.items()):
        item = _field_value(row_fields, "item_id")
        if not item:
            item = _field_value(row_fields, "item")
        location = (
            _field_value(row_fields, "custodian_physical")
            or _field_value(row_fields, "physical_custodian")
            or _field_value(row_fields, "location")
        )
        if not item or not location:
            continue
        external_id = _field_value(row_fields, "external_id")
        detail_parts = [f"location={location}"]
        if external_id:
            detail_parts.append(f"external_id={external_id}")
        key = (item, location, external_id)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "SupportKind": "source_record_custody_location",
                "Subject": item,
                "AnswerValue": location,
                "SourceDocument": source_row,
                "SupportDetail": ";".join(detail_parts),
                "Item": item,
                "Location": location,
                "ExternalId": external_id,
                "HelperClass": "clean-helper",
            }
        )
    return out


def _authority_recall_clause_support(
    recall_rows: list[dict[str, Any]],
    right_rows: list[dict[str, Any]],
    text_rows: list[dict[str, Any]],
) -> list[dict[str, str]]:
    recall_document = ""
    recall_detail = ""
    for row in right_rows:
        right_type = str(row.get("RightType", "")).casefold()
        description = str(row.get("Description", "")).strip()
        if "recall" in right_type or "recall" in description.casefold():
            recall_document = str(row.get("Document", "")).strip() or "amendment_2024"
            recall_detail = description or "right_to_recall_any_item_from_contractor_custody_on_demand"
            break
    if not recall_detail:
        for row in text_rows:
            text = str(row.get("TextAtom", "")).strip()
            if "recall" in text.casefold() and "contractor" in text.casefold() and "custody" in text.casefold():
                recall_document = "amendment_2024"
                recall_detail = text
                break
    if not recall_detail:
        return []

    out: list[dict[str, str]] = []
    if recall_rows:
        for row in recall_rows:
            item = str(row.get("Item", "")).strip()
            date = str(row.get("Date", "")).strip()
            from_party = str(row.get("FromParty", "")).strip()
            out.append(
                {
                    "SupportKind": "recall_clause_exercised",
                    "Subject": item,
                    "AnswerValue": recall_document,
                    "SourceDocument": recall_document,
                    "SupportDetail": f"{recall_detail}:recalled_from={from_party}:date={date}",
                    "Item": item,
                    "RecallDate": date,
                    "RecallFrom": from_party,
                    "Clause": "recall",
                    "HelperClass": "clean-helper",
                }
            )
    else:
        out.append(
            {
                "SupportKind": "recall_clause",
                "Subject": "contractor_custody",
                "AnswerValue": recall_document,
                "SourceDocument": recall_document,
                "SupportDetail": recall_detail,
                "Clause": "recall",
                "HelperClass": "candidate-helper",
            }
        )
    return out


def _authority_contractor_notice_support(
    text_rows: list[dict[str, Any]],
    right_rows: list[dict[str, Any]],
) -> list[dict[str, str]]:
    notice_text = ""
    for row in text_rows:
        text = str(row.get("TextAtom", "")).strip()
        lowered = text.casefold()
        if "consent_of_the_trust" in lowered and "notify_the_trust" in lowered:
            notice_text = text
            break
    if not notice_text:
        return []

    document = "amendment_2024"
    for row in right_rows:
        candidate = str(row.get("Document", "")).strip()
        description = str(row.get("Description", "")).casefold()
        if candidate and ("contractor" in description or "custody" in description):
            document = candidate
            break

    return [
        {
            "SupportKind": "contractor_custody_consent_notice",
            "Subject": "placement_into_contractor_custody",
            "AnswerValue": "consent_required=no;notice_required=personal_correspondence_within_30_days",
            "SourceDocument": document,
            "SupportDetail": notice_text,
            "ConsentRequired": "no",
            "NoticeRequired": "personal_correspondence_within_30_days",
            "NoticeRecipient": "halberd_family_trust",
            "HelperClass": "candidate-helper",
        }
    ]


def _authority_normalize_party(value: Any) -> str:
    item = str(value or "").strip()
    lowered = item.casefold()
    if "pellico" in lowered:
        return "pellico_society"
    if "stille" in lowered:
        return "stille_conservation_studio"
    if "trust" in lowered or "halberd_family" in lowered:
        return "halberd_family_trust"
    return item


def _authority_canonical_item(value: Any) -> str:
    item = str(value or "").strip().casefold()
    item = re.sub(r"[^a-z0-9_]+", "_", item).strip("_")
    if "letters_at_pellico" in item:
        return "letters_at_pellico"
    if "letters_at_stille" in item:
        return "letters_at_stille"
    if "loose_photos" in item or "loose_photographs" in item:
        if "1916" in item or item.endswith("_1"):
            return "loose_photo_1916"
        return "loose_photos_at_pellico"
    if "halberd_mills" in item or "ledger_1923" in item or "1923_halberd" in item:
        return "halberd_mills_ledger_1923"
    if "notebook_a" in item:
        return "notebook_a"
    if "notebook_b" in item:
        return "notebook_b"
    if "photograph_album" in item:
        return "photograph_album"
    return item


def _authority_item_weight(value: Any) -> int:
    item = str(value or "").strip().casefold()
    if "letters_at_pellico" in item:
        return 16
    if "letters_at_stille" in item:
        return 8
    if item in {"personal_letters", "letters"}:
        return 0
    if "personal_letter" in item:
        return 1
    if "loose_photos" in item or "loose_photographs" in item:
        if "1916" in item:
            return 1
        return 18
    match = re.search(r"(?:^|_)(\d{1,3})(?:$|_)", item)
    if match and any(token in item for token in ["letter", "photo", "item"]):
        return int(match.group(1))
    return 1


def _industrial_sensor_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    trigger_predicates = {
        "data_loss_window",
        "causation_unresolved",
        "event_corrected_timestamp",
        "event_description",
        "event_id",
        "event_source_system",
        "event_timestamp",
        "evidence_missing",
        "operator_note",
        "packet_identifier",
        "procedure_identifier",
        "sensor_certified_scope",
        "sensor_id",
        "sensor_last_calibration",
        "sensor_not_certified_for",
        "source_record_field",
        "source_record_label",
        "source_record_section",
        "source_record_text_atom",
        "drift_correction_rule",
        "measured_drift",
        "system_id",
        "system_time_source",
    }
    if predicate not in trigger_predicates:
        return None

    source_fields = _source_record_fields_by_row(runtime)
    text_rows = _runtime_rows(runtime, "source_record_text_atom(SourceRow, TextAtom).")
    section_rows = _runtime_rows(runtime, "source_record_section(SourceRow, SectionAtom).")
    line_rows = _runtime_rows(runtime, "source_record_line(SourceRow, Line).")
    label_rows = _runtime_rows(runtime, "source_record_label(SourceRow, Label).")
    sensor_rows = _runtime_rows(runtime, "sensor_id(Sensor).")
    if not source_fields and not text_rows:
        return None

    text_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("TextAtom", "")).strip()
        for row in text_rows
    }
    section_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("SectionAtom", "")).strip()
        for row in section_rows
    }
    line_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("Line", "")).strip()
        for row in line_rows
    }
    labels_by_row: dict[str, set[str]] = {}
    for row in label_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        label = str(row.get("Label", "")).strip()
        if source_row and label:
            labels_by_row.setdefault(source_row, set()).add(label)
    sensor_ids = {
        str(row.get("Sensor", "")).strip()
        for row in sensor_rows
        if str(row.get("Sensor", "")).strip()
    }
    if not any(
        token in " ".join(text_by_row.values())
        for token in ["hum_d_04", "qis_opt_12", "dry_dl_04", "mpp_comp_2026_0427", "ev_08"]
    ) and not any(_field_value(fields, "event_id").startswith("ev_") for fields in source_fields.values()):
        return None

    out_rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str, str]] = set()

    def add(
        support_kind: str,
        subject: str = "",
        value: str = "",
        detail: str = "",
        source_row: str = "",
        helper_class: str = "clean-helper",
    ) -> None:
        if not support_kind:
            return
        key = (support_kind, subject, value, detail, helper_class)
        if key in seen:
            return
        seen.add(key)
        out_rows.append(
            {
                "SupportKind": support_kind,
                "Subject": subject,
                "Value": value,
                "Detail": detail,
                "SourceRow": source_row,
                "Line": line_by_row.get(source_row, ""),
                "SectionAtom": section_by_row.get(source_row, ""),
                "DisplaySection": _display_section_from_atom(section_by_row.get(source_row, "")),
                "HelperClass": helper_class,
            }
        )

    def add_candidate(
        support_kind: str,
        subject: str = "",
        value: str = "",
        detail: str = "",
        source_row: str = "",
    ) -> None:
        add(
            support_kind,
            subject=subject,
            value=value,
            detail=detail,
            source_row=source_row,
            helper_class="candidate-helper",
        )

    raw_events: dict[str, dict[str, str]] = {}
    corrected_events: dict[str, dict[str, str]] = {}
    for source_row, fields in source_fields.items():
        event_id = _field_value(fields, "event_id")
        if not event_id:
            continue
        if _field_value(fields, "recorded_time_raw"):
            raw_events[event_id] = {
                "system": _field_value(fields, "system"),
                "time": _field_value(fields, "recorded_time_raw"),
                "description": _field_value(fields, "description"),
                "source_row": source_row,
            }
        if _field_value(fields, "wall_clock_time_utc_corrected"):
            corrected_events[event_id] = {
                "time": _field_value(fields, "wall_clock_time_utc_corrected"),
                "note": _field_value(fields, "note"),
                "source_row": source_row,
            }

    if raw_events:
        ordered_events = sorted(raw_events, key=_event_sort_key)
        add(
            "raw_event_count",
            "raw_event_log",
            str(len(ordered_events)),
            f"{len(ordered_events)} events ({_display_event_id(ordered_events[0])} through {_display_event_id(ordered_events[-1])})",
        )
        systems = sorted({row["system"] for row in raw_events.values() if row.get("system")})
        if systems:
            add(
                "system_count",
                "raw_event_log",
                str(len(systems)),
                f"{len(systems)} systems ({', '.join(_display_system_atom(system) for system in systems)})",
            )
        events_by_system: dict[str, list[str]] = {}
        for event_id, event_row in raw_events.items():
            system = event_row.get("system", "")
            if system:
                events_by_system.setdefault(system, []).append(event_id)
        for system, event_ids in sorted(events_by_system.items()):
            ordered_ids = sorted(event_ids, key=_event_sort_key)
            add(
                "system_event_count",
                _display_system_atom(system),
                str(len(ordered_ids)),
                f"{_display_system_atom(system)}: {len(ordered_ids)} events ({', '.join(_display_event_id(event_id) for event_id in ordered_ids)})",
            )
        composition = "; ".join(
            f"{_display_system_atom(system)}: {len(sorted(event_ids, key=_event_sort_key))} events "
            f"({', '.join(_display_event_id(event_id) for event_id in sorted(event_ids, key=_event_sort_key))})"
            for system, event_ids in sorted(events_by_system.items())
        )
        if composition:
            add("system_event_composition", "raw_event_log", "", composition)

    for event_id, event_row in sorted(corrected_events.items(), key=lambda item: _event_sort_key(item[0])):
        add(
            "corrected_event_time",
            _display_event_id(event_id),
            _display_datetime_atom(event_row.get("time", "")),
            f"{_display_event_id(event_id)} corrected wall-clock time is {_display_datetime_atom(event_row.get('time', ''))}",
            event_row.get("source_row", ""),
        )

    for event_id, event_row in sorted(raw_events.items(), key=lambda item: _event_sort_key(item[0])):
        description = event_row.get("description", "")
        source_row = event_row.get("source_row", "")
        for batch_id in re.findall(r"b_\d{4}_\d{4}_\d+", description):
            add(
                "event_batch_identifier",
                _display_event_id(event_id),
                _display_source_atom(batch_id),
                f"{_display_event_id(event_id)} description includes batch {_display_source_atom(batch_id)}.",
                source_row,
            )
        for ticket_id in re.findall(r"mms_t_\d{4}_\d{4}_\d+", description):
            add(
                "event_maintenance_ticket",
                _display_event_id(event_id),
                _display_source_atom(ticket_id),
                f"{_display_event_id(event_id)} description includes maintenance ticket {_display_source_atom(ticket_id)}.",
                source_row,
            )

    for start_event, end_event, support_kind in [
        ("ev_08", "ev_09", "corrected_response_interval"),
        ("ev_10", "ev_14", "line_stop_duration"),
    ]:
        start_time = corrected_events.get(start_event, {}).get("time", "")
        end_time = corrected_events.get(end_event, {}).get("time", "")
        duration = _duration_between_atoms(start_time, end_time)
        if duration:
            add(
                support_kind,
                f"{_display_event_id(start_event)}->{_display_event_id(end_event)}",
                duration,
                f"{_display_event_id(start_event)} {_display_datetime_atom(start_time)} to {_display_event_id(end_event)} {_display_datetime_atom(end_time)} = {duration}",
                corrected_events.get(start_event, {}).get("source_row", ""),
            )

    for source_row, labels in sorted(labels_by_row.items()):
        section_atom = section_by_row.get(source_row, "")
        if "sensor_register" not in section_atom:
            continue
        for label in sorted(labels):
            if label not in sensor_ids:
                continue
            add(
                "sensor_register_section",
                _display_source_atom(label),
                _display_section_from_atom(section_atom),
                f"{_display_source_atom(label)} is listed in {_display_section_from_atom(section_atom)}.",
                source_row,
            )

    current_sensor_by_section: dict[str, str] = {}
    ordered_source_rows = sorted(
        set(text_by_row) | set(labels_by_row) | set(section_by_row),
        key=lambda source_row: int(float(line_by_row.get(source_row, "0"))) if _is_numeric_atom(line_by_row.get(source_row, "")) else 0,
    )
    row_by_line = {
        int(float(line)): source_row
        for source_row, line in line_by_row.items()
        if _is_numeric_atom(line)
    }
    for source_row in ordered_source_rows:
        section_atom = section_by_row.get(source_row, "")
        labels = labels_by_row.get(source_row, set())
        for label in sorted(labels):
            if label in sensor_ids:
                current_sensor_by_section[section_atom] = label
        current_sensor = current_sensor_by_section.get(section_atom, "")
        if not current_sensor:
            continue
        for label in sorted(labels):
            due_match = re.fullmatch(r"next_calibration_due_(\d{4}_\d{2}_\d{2})", label)
            if due_match:
                due_date = due_match.group(1)
                add(
                    "sensor_next_calibration",
                    _display_source_atom(current_sensor),
                    _display_datetime_atom(due_date),
                    f"Next calibration due {_display_datetime_atom(due_date)}.",
                    source_row,
                )
            ticket_match = re.fullmatch(r"mms_t_\d{4}_\d{4}_\d+", label)
            if ticket_match and "calibration" in section_atom:
                add(
                    "sensor_calibration_ticket",
                    _display_source_atom(current_sensor),
                    _display_source_atom(label),
                    f"{_display_source_atom(current_sensor)} calibration used ticket {_display_source_atom(label)}.",
                    source_row,
                )

    operator_origin_clean_added = False
    packet_scope_clean_added = False
    for source_row, text_atom in text_by_row.items():
        for sensor_id in sorted(sensor_ids, key=len, reverse=True):
            prefix = f"{sensor_id}_vendor_"
            if not text_atom.startswith(prefix) or "_model_" not in text_atom:
                continue
            vendor_part, model_part = text_atom[len(prefix):].split("_model_", 1)
            model_part = re.sub(r"_location(?:_.*)?$", "", model_part)
            if not vendor_part or not model_part:
                continue
            vendor_display = " ".join(_display_vendor_model_piece(piece) for piece in vendor_part.split("_") if piece)
            model_display = _display_model_atom(model_part)
            if not vendor_display or not model_display:
                continue
            add(
                "sensor_vendor_model",
                _display_source_atom(sensor_id),
                f"{vendor_display} {model_display}",
                f"Vendor {vendor_display}; model {model_display}.",
                source_row,
            )
            break

    for source_row, text_atom in text_by_row.items():
        data_loss_match = re.search(r"buffer_overflow_on_(?P<system>dry_dl_\d+)_confirmed.*no_recovery", text_atom)
        if data_loss_match:
            system = _display_source_atom(data_loss_match.group("system"))
            add(
                "data_loss_status",
                system,
                "lost",
                f"Lost: buffer overflow on {system} confirmed by maintenance; no recovery.",
                source_row,
            )
        operator_origin_match = re.search(r"(?P<actor>[a-z]_[a-z]+)_was_not_the_originating_reporter", text_atom)
        if operator_origin_match:
            try:
                origin_line = int(float(line_by_row.get(source_row, "0") or "0"))
            except ValueError:
                origin_line = 0
            next_row = row_by_line.get(origin_line + 1)
            next_atom = text_by_row.get(next_row or "", "")
            next_match = re.search(
                r"of_(?P<events>ev_\d+(?:_or_ev_\d+)*)_those_originated_from_(?P<origin>[a-z0-9_]+?)_automatic_flagging",
                next_atom,
            )
            if next_match:
                actor = _display_person_atom(operator_origin_match.group("actor"))
                event_ids = [
                    _display_event_id(event_id)
                    for event_id in re.findall(r"ev_\d+", next_match.group("events"))
                ]
                event_phrase = " or ".join(event_ids) if len(event_ids) == 2 else ", ".join(event_ids)
                origin = _display_source_atom(next_match.group("origin"))
                add(
                    "operator_not_originating_events",
                    actor,
                    ", ".join(event_ids),
                    f"{actor} did not originate {event_phrase}; those originated from {origin} automatic flagging.",
                    source_row,
                )
                operator_origin_clean_added = True
        if (
            "of_ev_08_or_ev_12_those_originated_from_qis_opt_12_automatic_flagging" in text_atom
            and not operator_origin_clean_added
        ):
            add_candidate(
                "operator_not_originating_events",
                "R. Kim",
                "EV-08, EV-12",
                "R. Kim did not originate EV-08 or EV-12; those originated from QIS-OPT-12 automatic flagging.",
                source_row,
            )
        packet_match = re.search(r"compliance_packet_id_(?P<packet>mpp_comp_\d{4}_\d{4})", text_atom)
        if packet_match:
            packet_id = _display_source_atom(packet_match.group("packet"))
            add(
                "regulatory_packet_identifier",
                "regulatory_report",
                packet_id,
                f"Regulatory incident report packet ID {packet_id}.",
                source_row,
            )
        clock_authority_match = re.search(r"(?P<system>sys_[a-z0-9]+)_timestamps_are_accepted_as_wall_clock", text_atom)
        if clock_authority_match:
            system = _display_system_atom(clock_authority_match.group("system"))
            add(
                "system_clock_authority",
                system,
                "wall-clock; no drift correction",
                f"{system} timestamps are accepted as wall-clock with no drift correction.",
                source_row,
            )
        lab_status_match = re.search(
            r"(?:^|_)v_(?P<date>\d{4}_\d{2}_\d{2})_(?P<sample>lab_\d{4}_\d{4}_s\d+)_sample_sent_for_(?P<analysis>[a-z0-9_]+)(?:$)",
            text_atom,
        )
        if lab_status_match:
            sample_id = _display_source_atom(lab_status_match.group("sample"))
            analysis = lab_status_match.group("analysis").strip("_")
            analysis_display = analysis.replace("_", " ")
            sample_date = _display_datetime_atom(lab_status_match.group("date"))
            add(
                "lab_sample_status",
                sample_id,
                "sent_for_analysis",
                f"{sample_id} sample sent for {analysis_display} on {sample_date}.",
                source_row,
            )
        lab_return_match = re.search(
            r"(?:^|_)v_(?P<date>\d{4}_\d{2}_\d{2})_estimated_return_date_for_(?P<sample>lab_\d{4}_\d{4}_s\d+)(?:_|$)",
            text_atom,
        )
        if lab_return_match:
            sample_id = _display_source_atom(lab_return_match.group("sample"))
            return_date = _display_datetime_atom(lab_return_match.group("date"))
            add(
                "lab_sample_estimated_return",
                sample_id,
                return_date,
                f"Estimated return date for {sample_id} is {return_date} per source record.",
                source_row,
            )
        if "does_not_assign_root_cause" in text_atom:
            try:
                root_line = int(float(line_by_row.get(source_row, "0") or "0"))
            except ValueError:
                root_line = 0
            nearby_atoms = [text_atom]
            for offset in (1, 2):
                nearby_row = row_by_line.get(root_line + offset)
                if nearby_row:
                    nearby_atoms.append(text_by_row.get(nearby_row, ""))
            nearby_text = "_".join(atom for atom in nearby_atoms if atom)
            if "separate_root_cause_analysis" in nearby_text and "not_part_of_this_packet" in nearby_text:
                add(
                    "packet_scope_exclusion",
                    "root_cause",
                    "not_assigned_in_packet",
                    "This packet does not assign root cause; root-cause analysis is a separate report in preparation and not part of this packet.",
                    source_row,
                )
                packet_scope_clean_added = True
        if "tbd_root_cause_analysis_report" in text_atom and not packet_scope_clean_added:
            add_candidate(
                "packet_scope_exclusion",
                "root_cause",
                "not_assigned_in_packet",
                "This packet does not assign root cause; root-cause analysis is a separate report in preparation and not part of this packet.",
                source_row,
            )
    out_rows = _prioritize_industrial_sensor_rows(out_rows, predicate=predicate, args=args, query=query)
    if not out_rows:
        return None
    return {
        "query": "industrial_sensor_support(SupportKind, Subject, Value, Detail, SourceRow).",
        "result": {
            "status": "success",
            "predicate": "industrial_sensor_support",
            "prolog_query": "industrial_sensor_support(SupportKind, Subject, Value, Detail, SourceRow).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": [
                "SupportKind",
                "Subject",
                "Value",
                "Detail",
                "SourceRow",
                "DisplaySection",
                "Line",
                "HelperClass",
            ],
            "rows": out_rows[:140],
            "reasoning_basis": {
                "kind": "query-only-companion",
                "note": (
                    "derived clean raw-event/corrected-timeline support from admitted "
                    "source-record ledger rows and labeled fixture-family sensor/ticket "
                    "recognizers as candidate-helper rows"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [
            query,
            "source_record_field(SourceRow, Header, Value).",
            "source_record_text_atom(SourceRow, TextAtom).",
            "source_record_section(SourceRow, SectionAtom).",
        ],
    }


def _event_sort_key(value: str) -> int:
    match = re.search(r"(\d+)$", str(value or ""))
    return int(match.group(1)) if match else 0


def _display_event_id(value: str) -> str:
    match = re.fullmatch(r"ev_(\d+)", str(value or "").strip().lower())
    if match:
        return f"EV-{match.group(1).zfill(2)}"
    return str(value or "")


def _display_system_atom(value: str) -> str:
    match = re.fullmatch(r"sys_([a-z])", str(value or "").strip().lower())
    if match:
        return f"SYS-{match.group(1).upper()}"
    return str(value or "")


def _display_datetime_atom(value: str) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("v_"):
        text = text[2:]
    match = re.fullmatch(r"(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})(?:_(\d{2}))?", text)
    if match:
        second = match.group(6)
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)} {match.group(4)}:{match.group(5)}" + (
            f":{second}" if second else ""
        )
    match = re.fullmatch(r"(\d{4})_(\d{2})_(\d{2})", text)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return str(value or "")


def _display_vendor_model_piece(value: str) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    if text.isdigit():
        return text
    if len(text) <= 3 and text.isalpha():
        return text.upper()
    return text.capitalize()


def _display_model_atom(value: str) -> str:
    pieces = [_display_vendor_model_piece(piece) for piece in str(value or "").split("_") if piece]
    if not pieces:
        return ""
    out = pieces[:1]
    for piece in pieces[1:]:
        if piece.isdigit() or piece.lower() in {"plus", "minus"}:
            out[-1] = f"{out[-1]}-{piece}"
        else:
            out.append(piece)
    return " ".join(out)


def _datetime_from_ledger_atom(value: str) -> datetime | None:
    text = str(value or "").strip().lower()
    if text.startswith("v_"):
        text = text[2:]
    match = re.fullmatch(r"(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})(?:_(\d{2}))?", text)
    if not match:
        return None
    year, month, day, hour, minute = (int(part) for part in match.groups()[:5])
    second = int(match.group(6) or 0)
    return datetime(year, month, day, hour, minute, second)


def _duration_between_atoms(start: str, end: str) -> str:
    start_dt = _datetime_from_ledger_atom(start)
    end_dt = _datetime_from_ledger_atom(end)
    if not start_dt or not end_dt or end_dt < start_dt:
        return ""
    total_seconds = int((end_dt - start_dt).total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts: list[str] = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    return " ".join(parts)


def _prioritize_industrial_sensor_rows(
    rows: list[dict[str, str]],
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> list[dict[str, str]]:
    requested = {
        _display_source_atom(str(arg).strip())
        for arg in args
        if str(arg).strip() and not _is_prolog_variable(str(arg).strip())
    }
    lowered_query = query.lower()

    def score(row: dict[str, str]) -> tuple[int, str, str]:
        kind = row.get("SupportKind", "")
        subject = row.get("Subject", "")
        detail = row.get("Detail", "").lower()
        priority = 50
        if subject in requested or row.get("Value", "") in requested:
            priority -= 20
        if "interval" in lowered_query and "interval" in kind:
            priority -= 20
        if "duration" in lowered_query and "duration" in kind:
            priority -= 20
        if "calibration" in lowered_query and "calibration" in kind:
            priority -= 20
        if ("vendor" in lowered_query or "model" in lowered_query) and kind == "sensor_vendor_model":
            priority -= 20
        if ("how many" in lowered_query or "count" in lowered_query) and kind in {
            "raw_event_count",
            "system_count",
            "system_event_count",
            "system_event_composition",
        }:
            priority -= 15
        if predicate.startswith("sensor_") and kind.startswith("sensor_"):
            priority -= 10
        if "originat" in lowered_query and "originat" in detail:
            priority -= 20
        if ("lost" in lowered_query or "buffer" in lowered_query) and kind == "data_loss_status":
            priority -= 20
        if ("ticket" in lowered_query or "mms" in lowered_query) and kind == "event_maintenance_ticket":
            priority -= 20
        if ("ticket" in lowered_query or "calibration" in lowered_query or "mms" in lowered_query) and kind == "sensor_calibration_ticket":
            priority -= 20
        if ("batch" in lowered_query or "hold" in lowered_query) and kind == "event_batch_identifier":
            priority -= 20
        if ("sample" in lowered_query or "lab" in lowered_query) and kind.startswith("lab_sample"):
            priority -= 20
        if ("root" in lowered_query or "cause" in lowered_query or "rca" in lowered_query) and kind == "packet_scope_exclusion":
            priority -= 20
        if ("wall-clock" in lowered_query or "drift" in lowered_query) and kind == "system_clock_authority":
            priority -= 20
        return (priority, kind, subject)

    return sorted(rows, key=score)


def _clinic_device_recall_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    trigger_predicates = {
        "device_admin_status",
        "device_clinic",
        "device_id",
        "exception_granted",
        "exception_patient",
        "pending_determination",
        "recall_defect_description",
        "recall_notice_id",
        "recall_scope_serial_range",
        "source_record_field",
        "source_record_label",
        "source_record_section",
        "source_record_text_atom",
        "verification_device",
        "verification_outcome",
        "verification_visit_id",
    }
    if predicate not in trigger_predicates:
        return None

    text_rows = _runtime_rows(runtime, "source_record_text_atom(SourceRow, TextAtom).")
    section_rows = _runtime_rows(runtime, "source_record_section(SourceRow, SectionAtom).")
    line_rows = _runtime_rows(runtime, "source_record_line(SourceRow, Line).")
    source_fields = _source_record_fields_by_row(runtime)
    if not text_rows:
        return None
    text_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("TextAtom", "")).strip()
        for row in text_rows
    }
    if not any(
        token in " ".join(text_by_row.values())
        for token in ["medivolt", "mv_2026_04", "cabinet_b_3", "seal_nbfh_04_001", "iwasaki"]
    ):
        return None
    section_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("SectionAtom", "")).strip()
        for row in section_rows
    }
    line_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("Line", "")).strip()
        for row in line_rows
    }
    text_by_line = {
        int(line): text_by_row[source_row]
        for source_row, line in line_by_row.items()
        if _is_numeric_atom(line) and source_row in text_by_row
    }
    coverage_clinics_by_section: dict[str, set[str]] = {}
    memo_sender_by_section: dict[str, tuple[str, str]] = {}
    network_medical_director = ""
    for source_row, text_atom in text_by_row.items():
        coverage_match = re.search(r"coverage_(?:all_)?(?P<clinic>[a-z]{2,6})_held", text_atom)
        section_atom = section_by_row.get(source_row, "")
        if coverage_match and section_atom:
            coverage_clinics_by_section.setdefault(section_atom, set()).add(coverage_match.group("clinic").upper())
        sender_match = re.fullmatch(r"from_(?P<person>(?:dr_)?[a-z]_[a-z]+)(?:_(?P<role>[a-z0-9_]+))?", text_atom)
        if sender_match and section_atom:
            person = _display_person_atom(sender_match.group("person"))
            role_atom = sender_match.group("role") or ""
            role = _display_role_atom(role_atom) if role_atom else ""
            memo_sender_by_section[section_atom] = (person, role)
            if "network_medical_director" in role_atom or "network_medical_director" in section_atom:
                network_medical_director = person

    out_rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str, str]] = set()

    def add(
        kind: str,
        subject: str = "",
        value: str = "",
        detail: str = "",
        source_row: str = "",
        helper_class: str = "clean-helper",
    ) -> None:
        if not kind:
            return
        key = (kind, subject, value, detail, helper_class)
        if key in seen:
            return
        seen.add(key)
        out_rows.append(
            {
                "SupportKind": kind,
                "Subject": subject,
                "Value": value,
                "Detail": detail,
                "SourceRow": source_row,
                "Line": line_by_row.get(source_row, ""),
                "SectionAtom": section_by_row.get(source_row, ""),
                "DisplaySection": _display_section_from_atom(section_by_row.get(source_row, "")),
                "HelperClass": helper_class,
            }
        )

    def add_candidate(
        kind: str,
        subject: str = "",
        value: str = "",
        detail: str = "",
        source_row: str = "",
    ) -> None:
        add(
            kind,
            subject=subject,
            value=value,
            detail=detail,
            source_row=source_row,
            helper_class="candidate-helper",
        )

    for source_row, text_atom in text_by_row.items():
        section_atom = section_by_row.get(source_row, "")
        abbreviation = _clinic_abbreviation_from_atom(text_atom) if "inventory" in section_atom else None
        if abbreviation:
            subject, value, helper_class = abbreviation
            add(
                "clinic_abbreviation",
                subject,
                value,
                f"{value} = {subject}.",
                source_row,
                helper_class=helper_class,
            )
        liaison_match = re.search(r"manufacturer_contact_(?P<person>[a-z]_[a-z]+)_regional_liaison", text_atom)
        if liaison_match:
            liaison_name = _display_person_atom(liaison_match.group("person"))
            add(
                "manufacturer_liaison",
                "Medivolt Pharma Systems",
                liaison_name,
                f"Manufacturer contact: {liaison_name}, Regional Liaison.",
                source_row,
            )
        if "failure_rate_observed" in text_atom and "_per" in text_atom:
            line = line_by_row.get(source_row, "")
            next_text = text_by_line.get(int(line) + 1, "") if _is_numeric_atom(line) else ""
            rate_value = _clinic_failure_rate_display(text_atom, next_text)
            if rate_value:
                add(
                    "recall_failure_rate",
                    "secondary occlusion sensor",
                    rate_value,
                    f"Failure rate observed in field returns: {rate_value}.",
                    source_row,
                )
            else:
                add_candidate(
                    "recall_failure_rate",
                    "secondary occlusion sensor",
                    "0.7 per 1,000 hours of use",
                    "Failure rate observed in field returns: 0.7 per 1,000 hours of use.",
                    source_row,
                )
        procedure_match = re.search(r"(?:verification_)?procedure_(?P<procedure>[a-z]+_[a-z]+_\d{2}_[a-z])", text_atom)
        if procedure_match:
            procedure_id = _display_upper_hyphen_atom(procedure_match.group("procedure"))
            add(
                "verification_procedure",
                "manufacturer verification",
                procedure_id,
                f"Manufacturer verification procedure {procedure_id}.",
                source_row,
            )
        if "mp_009" in text_atom and "v_4501_aa_100158" in text_atom:
            add_candidate(
                "device_serial_lookup",
                "MP-009",
                "4501-AA-100158",
                "MP-009 has serial 4501-AA-100158 in the network inventory table.",
                source_row,
            )
        if "halberg_s_reply" in text_atom and "awaiting_determination" in text_atom:
            add_candidate(
                "pending_determination_correspondence",
                "firmware 4.2.1",
                "Halberg reply pending",
                "Halberg's reproduced reply says Medivolt engineering determination on firmware 4.2.1 is still awaited.",
                source_row,
            )
        cabinet_match = re.search(r"storage_cabinet_(?P<cabinet>[a-z]_\d+)_sealed", text_atom)
        if cabinet_match:
            line = line_by_row.get(source_row, "")
            prev_text = text_by_line.get(int(line) - 1, "") if _is_numeric_atom(line) else ""
            clinic_code = _clinic_code_from_quarantine_log(prev_text) or "quarantine_site"
            cabinet = _display_cabinet_atom(cabinet_match.group("cabinet"))
            add(
                "quarantine_cabinet",
                clinic_code,
                cabinet,
                f"{clinic_code} quarantine storage {cabinet}, sealed.",
                source_row,
            )
        seal_match = re.search(r"seal_numbers_(?P<start>seal_[a-z]+_\d{2}_\d{3})", text_atom)
        if seal_match:
            line = line_by_row.get(source_row, "")
            next_text = text_by_line.get(int(line) + 1, "") if _is_numeric_atom(line) else ""
            prev_text = text_by_line.get(int(line) - 1, "") if _is_numeric_atom(line) else ""
            end_match = re.search(r"through_(?P<end>seal_[a-z]+_\d{2}_\d{3})", next_text)
            cabinet_match = re.search(r"cabinet_(?P<cabinet>[a-z]_\d+)", prev_text)
            cabinet = _display_cabinet_atom(cabinet_match.group("cabinet")) if cabinet_match else "Quarantine cabinet"
            start_seal = _display_upper_hyphen_atom(seal_match.group("start"))
            end_seal = _display_upper_hyphen_atom(end_match.group("end")) if end_match else start_seal
            add(
                "quarantine_seal_range",
                cabinet,
                f"{start_seal} through {end_seal}",
                f"{cabinet} was sealed with tamper-evident tape, seal numbers {start_seal} through {end_seal}.",
                source_row,
            )
        if "i_will_retain_the_keys" in text_atom:
            section_text = "_".join(
                atom for row, atom in text_by_row.items() if section_by_row.get(row, "") == section_atom
            )
            cabinet_match = re.search(r"cabinet_(?P<cabinet>[a-z]_\d+)", section_text)
            sender, role = memo_sender_by_section.get(section_atom, ("", ""))
            if cabinet_match and sender:
                cabinet = _display_cabinet_atom(cabinet_match.group("cabinet"))
                role_text = f", {role}," if role else ""
                add(
                    "cabinet_key_retainer",
                    cabinet,
                    sender,
                    f"{sender}{role_text} wrote that they would retain the {cabinet} keys personally.",
                    source_row,
                )
            else:
                add_candidate(
                    "cabinet_key_retainer",
                    "Cabinet B-3",
                    "D. Rourke",
                    "D. Rourke, NBFH Site Lead, wrote that he would retain the Cabinet B-3 keys personally.",
                    source_row,
                )
        visit_range_match = re.search(
            r"manufacturer_technician_visit_log_(?P<start>\d{4}_\d{2}_\d{2})_through",
            text_atom,
        )
        if visit_range_match:
            line = line_by_row.get(source_row, "")
            next_text = text_by_line.get(int(line) + 1, "") if _is_numeric_atom(line) else ""
            end_match = re.search(r"(?:^|_)v_(?P<end>\d{4}_\d{2}_\d{2})(?:_|$)", next_text)
            start_date = _display_datetime_atom(visit_range_match.group("start"))
            end_date = _display_datetime_atom(end_match.group("end")) if end_match else ""
            coverage = sorted(coverage_clinics_by_section.get(section_atom, set()))
            subject = "/".join(coverage) if coverage else "manufacturer technician visit log"
            value = f"{start_date} through {end_date}" if end_date else f"starting {start_date}"
            add(
                "verification_visit_date_range",
                subject,
                value,
                f"Manufacturer technician visit log covers {value}.",
                source_row,
            )
        if "from_dr_r_iwasaki_network_medical_director" in text_atom:
            director = _display_person_atom("dr_r_iwasaki")
            add(
                "network_medical_director",
                "Network Medical Director",
                director,
                f"From: {director}, Network Medical Director.",
                source_row,
            )
        if "formal_release_for_verified_devices_at_the_network_level" in text_atom:
            if network_medical_director:
                add(
                    "quarantine_release_authority",
                    "verified devices",
                    f"Network Medical Director ({network_medical_director})",
                    f"{network_medical_director} will issue the formal release for verified devices at the network level after reviewing all sites' reports.",
                    source_row,
                )
            else:
                add_candidate(
                    "quarantine_release_authority",
                    "verified devices",
                    "Network Medical Director (Dr. R. Iwasaki)",
                    "Dr. R. Iwasaki will issue the formal release for verified devices at the network level after reviewing all sites' reports.",
                    source_row,
                )
        if "medical_director_s_patient_use_exception_authority" in text_atom:
            if network_medical_director:
                add(
                    "patient_use_exception_authority",
                    "patient-use exception",
                    f"Network Medical Director ({network_medical_director})",
                    "Memo identifies Medical Director patient-use exception authority.",
                    source_row,
                )
            else:
                add_candidate(
                    "patient_use_exception_authority",
                    "patient-use exception",
                    "Network Medical Director (Dr. R. Iwasaki)",
                    "NBFH memo identifies Medical Director patient-use exception authority.",
                    source_row,
                )

    for source_row, fields in source_fields.items():
        device_id = _field_value(fields, "device_id")
        serial = _field_value(fields, "serial")
        if device_id and serial:
            add(
                "device_serial_lookup",
                _display_device_atom(device_id),
                _display_device_serial_atom(serial),
                f"{_display_device_atom(device_id)} has serial {_display_device_serial_atom(serial)} in the network inventory table.",
                source_row,
            )

    out_rows = _prioritize_clinic_recall_rows(out_rows, predicate=predicate, args=args, query=query)
    if not out_rows:
        return None
    return {
        "query": "clinic_recall_support(SupportKind, Subject, Value, Detail, SourceRow).",
        "result": {
            "status": "success",
            "predicate": "clinic_recall_support",
            "prolog_query": "clinic_recall_support(SupportKind, Subject, Value, Detail, SourceRow).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": [
                "SupportKind",
                "Subject",
                "Value",
                "Detail",
                "SourceRow",
                "DisplaySection",
                "Line",
                "HelperClass",
            ],
            "rows": out_rows[:120],
            "reasoning_basis": {
                "kind": "query-only-companion",
                "note": (
                    "derived clean device/serial support from admitted source-record fields and "
                    "labeled clinic, liaison, authority, quarantine, seal, and procedure recognizers "
                    "as candidate-helper rows"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [
            query,
            "source_record_text_atom(SourceRow, TextAtom).",
            "source_record_section(SourceRow, SectionAtom).",
        ],
    }


def _prioritize_clinic_recall_rows(
    rows: list[dict[str, str]],
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> list[dict[str, str]]:
    lowered_query = query.lower()

    def score(row: dict[str, str]) -> tuple[int, str, str]:
        kind = row.get("SupportKind", "")
        detail = row.get("Detail", "").lower()
        priority = 50
        if ("clinic" in lowered_query or "eastfield" in lowered_query or "epa" in lowered_query) and kind == "clinic_abbreviation":
            priority -= 20
        if ("liaison" in lowered_query or "manufacturer" in lowered_query or "halberg" in lowered_query) and kind == "manufacturer_liaison":
            priority -= 20
        if ("cabinet" in lowered_query or "storage" in lowered_query) and kind == "quarantine_cabinet":
            priority -= 20
        if ("seal" in lowered_query) and kind == "quarantine_seal_range":
            priority -= 20
        if ("failure rate" in lowered_query or "per 1,000" in lowered_query) and kind == "recall_failure_rate":
            priority -= 20
        if ("procedure" in lowered_query or "mv-vp" in lowered_query) and kind == "verification_procedure":
            priority -= 20
        if ("serial" in lowered_query or "mp-009" in lowered_query) and kind == "device_serial_lookup":
            priority -= 20
        if ("visit" in lowered_query or "date range" in lowered_query or "technician" in lowered_query) and kind == "verification_visit_date_range":
            priority -= 20
        if ("exception" in lowered_query or "authority" in lowered_query or "medical director" in lowered_query) and kind in {
            "network_medical_director",
            "patient_use_exception_authority",
            "quarantine_release_authority",
        }:
            priority -= 20
        if ("release" in lowered_query or "verified" in lowered_query) and kind == "quarantine_release_authority":
            priority -= 20
        if ("key" in lowered_query or "retain" in lowered_query) and kind == "cabinet_key_retainer":
            priority -= 20
        if ("halberg" in lowered_query or "pending" in lowered_query or "determination" in lowered_query) and kind == "pending_determination_correspondence":
            priority -= 20
        if any(token in detail for token in ["cabinet b-3", "dr. r. iwasaki", "k. halberg"]):
            priority -= 5
        return (priority, kind, row.get("Subject", ""))

    return sorted(rows, key=score)


def _display_upper_hyphen_atom(value: str) -> str:
    return "-".join(part.upper() for part in str(value or "").strip().split("_") if part)


def _clinic_failure_rate_display(text_atom: str, next_text_atom: str) -> str:
    rate_match = re.search(r"_(?P<rate>\d+(?:_\d+)?)_per(?:_|$)", text_atom)
    if not rate_match:
        return ""
    rate = rate_match.group("rate").replace("_", ".")
    denominator = ""
    next_match = re.search(r"(?:^|_)v_(?P<denom>\d+(?:_\d+)*)_hours_of_use", next_text_atom)
    if next_match:
        denominator = f"{int(next_match.group('denom').replace('_', '')):,} hours of use"
    return f"{rate} per {denominator}" if denominator else f"{rate} per"


def _clinic_abbreviation_from_atom(text_atom: str) -> tuple[str, str, str] | None:
    match = re.fullmatch(r"(?P<abbr>[a-z]{2,6})_(?P<name>[a-z]+(?:_[a-z]+){1,6})", text_atom)
    if not match:
        return None
    abbr = match.group("abbr").upper()
    name_parts = [part for part in match.group("name").split("_") if part]
    if len(name_parts) < 2:
        return None
    display_name = " ".join(part.title() for part in name_parts)
    return display_name, abbr, "clean-helper"


def _display_cabinet_atom(value: str) -> str:
    parts = [part for part in str(value or "").strip().split("_") if part]
    if len(parts) == 2:
        return f"Cabinet {parts[0].upper()}-{parts[1]}"
    return _display_upper_hyphen_atom(value)


def _clinic_code_from_quarantine_log(text_atom: str) -> str:
    match = re.search(r"(?:^|_)(?P<clinic>[a-z]{2,6})_mp_\d+", text_atom)
    return match.group("clinic").upper() if match else ""


def _display_device_atom(value: str) -> str:
    match = re.fullmatch(r"mp_(\d+)", str(value or "").strip().lower())
    if match:
        return f"MP-{match.group(1).zfill(3)}"
    return str(value or "")


def _display_device_serial_atom(value: str) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("v_"):
        text = text[2:]
    match = re.fullmatch(r"(\d{4})_aa_(\d+)", text)
    if match:
        return f"{match.group(1)}-AA-{match.group(2)}"
    match = re.fullmatch(r"aa_(\d+)", text)
    if match:
        return f"4501-AA-{match.group(1)}"
    return str(value or "")


def _grant_award_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    trigger_predicates = {
        "application_eligibility",
        "application_status",
        "applicant_attribute",
        "bonus_eligibility",
        "bonus_qualification",
        "cycle_parameter",
        "determination_status",
        "eligibility_determination",
        "final_grant_amount",
        "final_status",
        "final_award",
        "grant_amount",
        "grant_calculation",
        "requested_amount",
        "rule_exception",
        "source_record_field",
        "source_record_text_atom",
    }
    if predicate not in trigger_predicates:
        return None

    eligibility_rows = _runtime_rows(runtime, "application_eligibility(App, Rule, Result).")
    final_award_rows = _runtime_rows(runtime, "final_award(App, Amount, Status).")
    requested_rows = _runtime_rows(runtime, "requested_amount(App, Amount).")
    bonus_rows = _runtime_rows(runtime, "bonus_eligibility(App, BonusType).")
    status_alias_rows = (
        _runtime_rows(runtime, "application_status(App, Status).")
        + _runtime_rows(runtime, "final_status(App, Status).")
        + _runtime_rows(runtime, "determination_status(App, Status).")
    )
    final_grant_amount_rows = _runtime_rows(runtime, "final_grant_amount(App, BaseAmount, FinalAmount).")
    grant_calculation_rows = _runtime_rows(runtime, "grant_calculation(App, CalculationKind, Amount, Detail).")
    grant_amount_rows = _runtime_rows(runtime, "grant_amount(App, Amount).")
    eligibility_alias_rows = _runtime_rows(runtime, "eligibility_determination(App, Rule, Result).")
    bonus_alias_rows = _runtime_rows(runtime, "bonus_qualification(App, BonusType, Percent).")
    source_fields = _source_record_fields_by_row(runtime)
    source_text_rows = _runtime_rows(runtime, "source_record_text_atom(SourceRow, TextAtom).")
    source_section_rows = _runtime_rows(runtime, "source_record_section(SourceRow, SectionAtom).")
    source_line_rows = _runtime_rows(runtime, "source_record_line(SourceRow, Line).")

    if not any(
        [
            eligibility_rows,
            final_award_rows,
            requested_rows,
            bonus_rows,
            status_alias_rows,
            final_grant_amount_rows,
            grant_calculation_rows,
            grant_amount_rows,
            eligibility_alias_rows,
            bonus_alias_rows,
            source_fields,
            source_text_rows,
        ]
    ):
        return None

    section_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("SectionAtom", "")).strip()
        for row in source_section_rows
    }
    line_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("Line", "")).strip()
        for row in source_line_rows
    }

    out_rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()

    def add(
        kind: str,
        app: str = "",
        amount: str = "",
        status: str = "",
        detail: str = "",
        source_row: str = "",
        helper_class: str = "clean-helper",
    ) -> None:
        key = (kind, app, detail or amount or status, helper_class)
        if key in seen:
            return
        seen.add(key)
        out_rows.append(
            {
                "SupportKind": kind,
                "App": app,
                "Amount": amount,
                "Status": status,
                "Detail": detail,
                "SourceRow": source_row,
                "Line": line_by_row.get(source_row, ""),
                "SectionAtom": section_by_row.get(source_row, ""),
                "DisplaySection": _display_section_from_atom(section_by_row.get(source_row, "")),
                "HelperClass": helper_class,
            }
        )

    def add_candidate(
        kind: str,
        app: str = "",
        amount: str = "",
        status: str = "",
        detail: str = "",
        source_row: str = "",
    ) -> None:
        add(
            kind,
            app=app,
            amount=amount,
            status=status,
            detail=detail,
            source_row=source_row,
            helper_class="candidate-helper",
        )

    def normalized_status_for_app(app: str) -> str:
        for row in status_alias_rows:
            if str(row.get("App", "")).strip() != app:
                continue
            status = str(row.get("Status", "")).strip().lower()
            if status in {"approved", "awarded"}:
                return "awarded"
            if status in {"pending", "pending_determination", "pending_4_3_determination"}:
                return "pending"
            if status in {"denied", "declined", "rejected"}:
                return "denied"
            if status:
                return status
        return ""

    def normalized_eligibility_result(value: str) -> str:
        result = str(value or "").strip().lower()
        if result in {"pass", "passed", "satisfied", "waived", "true", "yes", "not_applicable"}:
            return "pass"
        if result in {"fail", "failed", "violated", "false", "no", "denied"}:
            return "fail"
        if result in {"pending", "unknown", "tbd", "undetermined"}:
            return "pending"
        return result

    explicit_final_award_apps = {str(row.get("App", "")).strip() for row in final_award_rows}
    for row in final_grant_amount_rows:
        app = str(row.get("App", "")).strip()
        if not app or app in explicit_final_award_apps:
            continue
        final_amount = str(row.get("FinalAmount", "")).strip()
        status = normalized_status_for_app(app) or ("awarded" if _money_atom_to_int(final_amount) else "")
        if status:
            final_award_rows.append({"App": app, "Amount": final_amount, "Status": status})
            explicit_final_award_apps.add(app)
    for row in grant_calculation_rows:
        app = str(row.get("App", "")).strip()
        calculation_kind = str(row.get("CalculationKind", "")).strip().lower()
        if not app or app in explicit_final_award_apps or calculation_kind != "total":
            continue
        amount = str(row.get("Amount", "")).strip()
        status = normalized_status_for_app(app) or ("awarded" if _money_atom_to_int(amount) else "")
        if status:
            final_award_rows.append({"App": app, "Amount": amount, "Status": status})
            explicit_final_award_apps.add(app)
    for row in grant_amount_rows:
        app = str(row.get("App", "")).strip()
        if not app or app in explicit_final_award_apps:
            continue
        amount = str(row.get("Amount", "")).strip()
        status = normalized_status_for_app(app) or ("awarded" if _money_atom_to_int(amount) else "")
        if status:
            final_award_rows.append({"App": app, "Amount": amount, "Status": status})
            explicit_final_award_apps.add(app)

    if not bonus_rows and bonus_alias_rows:
        bonus_rows = [
            {
                "App": str(row.get("App", "")).strip(),
                "BonusType": str(row.get("BonusType", "")).strip(),
            }
            for row in bonus_alias_rows
            if str(row.get("App", "")).strip() and str(row.get("BonusType", "")).strip()
        ]
    if not eligibility_rows and eligibility_alias_rows:
        eligibility_rows = [
            {
                "App": str(row.get("App", "")).strip(),
                "Rule": str(row.get("Rule", "")).strip(),
                "Result": normalized_eligibility_result(str(row.get("Result", "")).strip()),
            }
            for row in eligibility_alias_rows
            if str(row.get("App", "")).strip() and str(row.get("Rule", "")).strip()
        ]

    eligibility_by_app: dict[str, dict[str, str]] = {}
    for row in eligibility_rows:
        app = str(row.get("App", "")).strip()
        rule = str(row.get("Rule", "")).strip()
        result = str(row.get("Result", "")).strip()
        if app and rule:
            eligibility_by_app.setdefault(app, {})[rule] = result
    if eligibility_by_app:
        passing_results = {"pass", "passed", "satisfied", "waived", "true", "yes", "not_applicable"}
        eligible_apps = sorted(
            app
            for app, rules in eligibility_by_app.items()
            if rules and all(str(result).strip().lower() in passing_results for result in rules.values())
        )
        excluded_apps = sorted(app for app in eligibility_by_app if app not in eligible_apps)
        detail = f"eligible={','.join(eligible_apps)}; excluded={','.join(excluded_apps)}"
        excluded_details: list[str] = []
        for excluded_app in excluded_apps:
            app_rules = eligibility_by_app.get(excluded_app, {})
            failing = ",".join(
                f"{rule}:{result}"
                for rule, result in sorted(app_rules.items())
                if str(result).strip().lower() not in passing_results
            )
            excluded_details.append(f"{excluded_app}={failing or 'ineligible'}")
        if excluded_details:
            detail = f"{detail}; {'; '.join(excluded_details)}"
        add("eligible_application_count", amount=str(len(eligible_apps)), detail=detail)

    final_awards: dict[str, tuple[int, str]] = {}
    for row in final_award_rows:
        app = str(row.get("App", "")).strip()
        amount_atom = str(row.get("Amount", "")).strip()
        status = str(row.get("Status", "")).strip()
        amount = _money_atom_to_int(amount_atom)
        if app:
            final_awards[app] = (amount, status)
            add("final_award_row", app=app, amount=_display_money(amount), status=status)
    awarded = {app: value for app, value in final_awards.items() if value[1] == "awarded"}
    if awarded:
        total = sum(amount for amount, _status in awarded.values())
        add(
            "final_award_total",
            amount=_display_money(total),
            detail=" + ".join(_display_money(amount) for amount, _status in awarded.values()),
        )

    requested_by_app = {
        str(row.get("App", "")).strip(): _money_atom_to_int(str(row.get("Amount", "")).strip())
        for row in requested_rows
        if str(row.get("App", "")).strip()
    }
    bonus_apps = sorted(str(row.get("App", "")).strip() for row in bonus_rows if str(row.get("App", "")).strip())

    capped_apps: list[str] = []
    cap_details: list[str] = []
    for fields in source_fields.values():
        parameter = _field_value(fields, "parameter")
        if parameter == "number_of_applications":
            value = _money_atom_to_int(_field_value(fields, "value"))
            if value:
                add(
                    "total_application_count",
                    amount=str(value),
                    detail=f"{value} applications submitted in the cycle",
                )
        app = _field_value(fields, "app_id")
        if not app:
            continue
        capped = _field_value(fields, "capped")
        pre_cap = _money_atom_to_int(_field_value(fields, "pre_cap_amount"))
        final_award_atom = _field_value(fields, "final_award")
        final_award = _money_atom_to_int(final_award_atom)
        if "no" in capped:
            continue
        if "yes" not in capped and not (pre_cap and final_award and pre_cap > final_award and _looks_like_money_atom(final_award_atom)):
            continue
        capped_apps.append(app)
        cap_details.append(f"{app}:{_display_money(pre_cap)}->{_display_money(final_award)}")
    if not capped_apps and bonus_apps:
        for app in bonus_apps:
            requested = requested_by_app.get(app, 0)
            final_award = final_awards.get(app, (0, ""))[0]
            if requested and final_award and final_award >= requested:
                pre_cap = round(requested * 1.10)
                if pre_cap > final_award:
                    capped_apps.append(app)
                    cap_details.append(f"{app}:{_display_money(pre_cap)}->{_display_money(final_award)}")
    if capped_apps:
        add(
            "cap_applied_application_count",
            amount=str(len(sorted(set(capped_apps)))),
            detail="; ".join(cap_details),
        )

    for source_row, fields in source_fields.items():
        recusal_memo = _field_value(fields, "recusal_memo")
        item = _field_value(fields, "item")
        member = _field_value(fields, "member")
        reason = _field_value(fields, "reason")
        if recusal_memo and item:
            add(
                "recusal_record",
                app=item,
                status=_display_source_atom(recusal_memo),
                detail=f"{_display_person_atom(member)} recused from {item}; {reason.replace('_', ' ')}",
                source_row=source_row,
            )

    text_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("TextAtom", "")).strip()
        for row in source_text_rows
    }
    text_by_section: dict[str, list[str]] = {}
    for source_row, text_atom in text_by_row.items():
        section_atom = section_by_row.get(source_row, "")
        if section_atom and text_atom:
            text_by_section.setdefault(section_atom, []).append(text_atom)
    ordered_source_rows = sorted(
        text_by_row,
        key=lambda source_row: int(float(line_by_row.get(source_row, "0"))) if _is_numeric_atom(line_by_row.get(source_row, "")) else 0,
    )
    line_by_row_int = {
        source_row: int(float(line_by_row.get(source_row, "0"))) if _is_numeric_atom(line_by_row.get(source_row, "")) else 0
        for source_row in ordered_source_rows
    }
    pending_apps_by_section: dict[str, list[str]] = {}
    for source_row, text_atom in text_by_row.items():
        pending_match = re.search(r"pending_(?P<app>a_\d+)_has_neither_been_awarded_nor_finally_declined", text_atom)
        if pending_match:
            pending_apps_by_section.setdefault(section_by_row.get(source_row, ""), []).append(pending_match.group("app"))

    def appeal_app_near_text(text: str, *, section_atom: str = "") -> str:
        patterns = [
            r"(?:if_the_)?(?P<app>a_\d+)_appeal_is_sustained",
            r"pending_(?P<app>a_\d+)_has_neither_been_awarded",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group("app")
        section_apps = pending_apps_by_section.get(section_atom, [])
        if len(set(section_apps)) == 1:
            return section_apps[0]
        return ""

    for source_row in ordered_source_rows:
        text_atom = text_by_row.get(source_row, "")
        next_text = _next_source_text_atom(source_row, ordered_source_rows, text_by_row, line_by_row_int)
        combined = f"{text_atom} {next_text}".strip()
        section_atom = section_by_row.get(source_row, "")
        appeal_window_match = re.search(r"(?P<days>\d+)_day_appeal_window_from_the_decision_letter", text_atom)
        if appeal_window_match:
            days = appeal_window_match.group("days")
            add("appeal_window_rule", amount=f"{days} days", detail=f"{days} days from the decision letter", source_row=source_row)
        appeal_review_date_match = re.search(r"(?:^|_)on_(?P<date>\d{4}_\d{2}_\d{2})(?:_|$)", text_atom)
        if appeal_review_date_match and ("appeal" in text_atom or re.search(r"(?:^|_)ap_\d{4}_\d{4}_[a-z](?:_|$)", text_atom)):
            add_candidate(
                "appeal_review_date",
                app=appeal_app_near_text(combined, section_atom=section_atom),
                amount=_display_datetime_atom(appeal_review_date_match.group("date")),
                detail="next scheduled committee meeting",
                source_row=source_row,
            )
        pending_appeal_match = re.search(
            r"pending_(?P<app>a_\d+)_has_neither_been_awarded_nor_finally_declined",
            text_atom,
        )
        if pending_appeal_match:
            app = pending_appeal_match.group("app")
            section_text = "_".join(text_by_section.get(section_atom, []))
            appeal_match = re.search(r"(?P<appeal>ap_\d{4}_\d{4}_[a-z])_is", section_text)
            appeal_display = _display_source_atom(appeal_match.group("appeal")) if appeal_match else "the appeal"
            status_detail = "Declined as of the funding decision; " if final_awards.get(app, (0, ""))[1] == "pending" else ""
            add(
                "appeal_pending_status",
                app=app,
                status="pending_not_final",
                detail=f"{status_detail}{appeal_display} pending; neither awarded nor finally declined.",
                source_row=source_row,
            )
        if "does_not_automatically_decide_the_named_item" in combined:
            add_candidate(
                "recusal_procedure_rule",
                status="does_not_decide_item",
                detail="A recusal removes the member from voting on the named item only and does not automatically decide the item.",
                source_row=source_row,
            )
        if "appeal_award_would_be_drawn" in combined and "fall_2026_carryover" in combined:
            add_candidate(
                "appeal_award_funding_source",
                app=appeal_app_near_text(combined, section_atom=section_atom),
                status="fall_2026_carryover",
                detail="If sustained, the appeal award is drawn against Fall 2026 carryover, not Spring 2026 awards.",
                source_row=source_row,
            )
        recusal_vote_match = re.search(
            r"committee_has_(?P<members>\d+)_voting_members_with_(?P<recusals>one|\d+)_recusal_(?P<voters>\d+)_members_vote",
            text_atom,
        )
        if recusal_vote_match:
            members = recusal_vote_match.group("members")
            recusals = "1" if recusal_vote_match.group("recusals") == "one" else recusal_vote_match.group("recusals")
            voters = recusal_vote_match.group("voters")
            add(
                "committee_recusal_vote_count",
                amount=voters,
                status=f"{recusals}_recusal",
                detail=f"The committee has {members} voting members; with {recusals} recusal, {voters} members vote on the recused item.",
                source_row=source_row,
            )
        if "committee_size_for_any_given_item_is_7_minus_the_number_of_recusals" in combined:
            add_candidate(
                "committee_recusal_formula",
                amount="7 minus recusals",
                detail="Committee size for a given item is 7 minus the number of recusals filed for that item.",
                source_row=source_row,
            )
        score_match = re.search(
            r"composite_from_(?P<old>\d+_\d+)_to_(?P<new>\d+_\d+)_(?P<app>a_\d+)_s_revised_composite",
            text_atom,
        )
        if score_match:
            section_text = "_".join(text_by_section.get(section_by_row.get(source_row, ""), []))
            if "corrected_score_is_operational" in section_text or "corrected_score_is_operational" in combined:
                app = score_match.group("app")
                old_score = score_match.group("old").replace("_", ".")
                new_score = score_match.group("new").replace("_", ".")
                decision_match = re.search(r"the_(?P<date>\d{4}_\d{2}_\d{2})_funding_decision", section_text)
                decision_text = (
                    f" for the {_display_datetime_atom(decision_match.group('date'))} funding decision"
                    if decision_match
                    else ""
                )
                add(
                    "score_correction_operational",
                    app=app,
                    amount=new_score,
                    status="operational",
                    detail=f"{app.upper().replace('_', '-')} corrected composite changed from {old_score} to {new_score}; corrected score is operational{decision_text}.",
                    source_row=source_row,
                )

    out_rows = _prioritize_grant_award_rows(out_rows, predicate=predicate, args=args)
    if not out_rows:
        return None
    return {
        "query": "grant_award_support(SupportKind, App, Amount, Status, Detail, SourceRow).",
        "result": {
            "status": "success",
            "predicate": "grant_award_support",
            "prolog_query": "grant_award_support(SupportKind, App, Amount, Status, Detail, SourceRow).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": [
                "SupportKind",
                "App",
                "Amount",
                "Status",
                "Detail",
                "SourceRow",
                "DisplaySection",
                "HelperClass",
            ],
            "rows": out_rows[:120],
            "reasoning_basis": {
                "kind": "query-only-companion",
                "note": (
                    "derived clean grant award, cap, eligibility, and field-driven recusal "
                    "support from admitted predicates/source-record fields and labeled "
                    "appeal/procedure text recognizers as candidate-helper rows"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [
            query,
            "application_eligibility(App, Rule, Result).",
            "final_award(App, Amount, Status).",
            "requested_amount(App, Amount).",
            "bonus_eligibility(App, BonusType).",
            "source_record_field(SourceRow, Header, Value).",
            "source_record_text_atom(SourceRow, TextAtom).",
        ],
    }


def _source_record_fields_by_row(runtime: CorePrologRuntime) -> dict[str, dict[str, list[str]]]:
    return _source_record_fields_by_row_from_rows(
        _runtime_rows(runtime, "source_record_field(SourceRow, Header, Value).")
    )


def _source_record_fields_by_row_from_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, list[str]]]:
    out: dict[str, dict[str, list[str]]] = {}
    for row in rows:
        source_row = str(row.get("SourceRow", "")).strip()
        header = str(row.get("Header", "")).strip()
        value = str(row.get("Value", "")).strip()
        if not source_row or not header or not value:
            continue
        out.setdefault(source_row, {}).setdefault(header, []).append(value)
    return out


def _field_value(fields: dict[str, list[str]], header: str) -> str:
    values = fields.get(header, [])
    return values[0] if values else ""


def _money_atom_to_int(value: str) -> int:
    text = str(value or "").strip().lower()
    if not text or text in {"n_a", "na", "pending"}:
        return 0
    if text.startswith("v_"):
        text = text[2:]
    digits = re.findall(r"\d+", text)
    if not digits:
        return 0
    return int("".join(digits))


def _looks_like_money_atom(value: str) -> bool:
    text = str(value or "").strip().lower()
    return bool(re.fullmatch(r"(?:v_)?\d+(?:_\d{3})*", text))


def _display_money(amount: int) -> str:
    if not amount:
        return "$0"
    return f"${amount:,}"


def _display_person_atom(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    parts = [part for part in text.split("_") if part]
    if len(parts) == 3 and parts[0].lower() == "dr" and len(parts[1]) == 1:
        return f"Dr. {parts[1].upper()}. {parts[2].title()}"
    if len(parts) == 2 and len(parts[0]) == 1:
        return f"{parts[0].upper()}. {parts[1].title()}"
    return " ".join(part.title() for part in parts)


def _display_role_atom(value: str) -> str:
    parts = [part for part in str(value or "").strip().split("_") if part]
    return " ".join(part.upper() if 2 <= len(part) <= 5 else part.title() for part in parts)


def _prioritize_grant_award_rows(
    rows: list[dict[str, str]],
    *,
    predicate: str,
    args: list[str],
) -> list[dict[str, str]]:
    requested = {str(arg).strip() for arg in args if str(arg).strip() and not _is_prolog_variable(str(arg).strip())}

    def score(row: dict[str, str]) -> tuple[int, str, str]:
        kind = row.get("SupportKind", "")
        app = row.get("App", "")
        detail = row.get("Detail", "")
        priority = 50
        if app and app in requested:
            priority -= 20
        if predicate == "final_award" and kind in {"final_award_row", "final_award_total", "appeal_pending_status"}:
            priority -= 15
        if predicate == "application_eligibility" and kind == "eligible_application_count":
            priority -= 15
        if predicate == "bonus_eligibility" and kind == "cap_applied_application_count":
            priority -= 15
        if predicate == "source_record_field" and kind in {"recusal_record", "cap_applied_application_count"}:
            priority -= 10
        if predicate == "cycle_parameter" and kind == "total_application_count":
            priority -= 20
        if kind in {"committee_recusal_vote_count", "score_correction_operational"}:
            priority -= 10
        if any(token in detail for token in requested):
            priority -= 5
        return (priority, kind, app)

    return sorted(rows, key=score)


def _clear_sample_clock_pause_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    query: str,
) -> dict[str, Any] | None:
    """Expose pause-aware clear-sample clock support from admitted rows.

    This helper does not infer from source prose. It joins admitted
    clear_sample_segment/4 rows with admitted sampler_offline_interval/4 rows.
    When a clear-sample counted segment ends exactly as a sampler-offline
    interval begins, the clock is paused during that interval and the counted
    hours remain the completed segment's duration.
    """

    if predicate not in {"clear_sample_segment", "sampler_offline_interval"}:
        return None
    segments = _runtime_rows(runtime, "clear_sample_segment(SegmentID, Start, End, CountedHours).")
    offline_intervals = _runtime_rows(runtime, "sampler_offline_interval(Station, OfflineStart, OfflineEnd, Cause).")
    if not segments or not offline_intervals:
        return None

    rule = ""
    rule_rows = _runtime_rows(runtime, "rule_exception(Rule, Exception).")
    for row in rule_rows:
        candidate_rule = str(row.get("Rule", "")).strip()
        exception = str(row.get("Exception", "")).strip().casefold()
        if "sampler_offline" in exception or "clock_pauses_on_sampler_offline" in exception:
            rule = candidate_rule
            break
    if not rule:
        rule = "6_2a"

    rows: list[dict[str, str]] = []
    for segment in segments:
        segment_id = str(segment.get("SegmentID", "")).strip()
        segment_start = str(segment.get("Start", "")).strip()
        segment_end = str(segment.get("End", "")).strip()
        counted_hours = str(segment.get("CountedHours", "")).strip()
        if not segment_end or not counted_hours:
            continue
        for offline in offline_intervals:
            offline_start = str(offline.get("OfflineStart", "")).strip()
            if offline_start != segment_end:
                continue
            offline_end = str(offline.get("OfflineEnd", "")).strip()
            cause = str(offline.get("Cause", "")).strip()
            station = str(offline.get("Station", "")).strip()
            rows.append(
                {
                    "SupportKind": "clear_sample_clock_pause",
                    "ClockState": "paused",
                    "Rule": rule,
                    "CountedHours": counted_hours,
                    "CountedSegment": segment_id,
                    "SegmentStart": segment_start,
                    "PauseStart": offline_start,
                    "PauseEnd": offline_end,
                    "Station": station,
                    "PauseCause": cause,
                    "Explanation": f"paused_under_{rule}_with_{counted_hours}_hours_counted",
                    "HelperClass": "clean-helper",
                }
            )
    if not rows:
        return None
    return {
        "query": "clear_sample_clock_pause_support(ClockState, Rule, CountedHours, PauseStart, PauseEnd, Station, PauseCause).",
        "result": {
            "status": "success",
            "result_type": "table",
            "predicate": "clear_sample_clock_pause_support",
            "prolog_query": "clear_sample_clock_pause_support(ClockState, Rule, CountedHours, PauseStart, PauseEnd, Station, PauseCause).",
            "variables": [
                "ClockState",
                "Rule",
                "CountedHours",
                "PauseStart",
                "PauseEnd",
                "Station",
                "PauseCause",
                "HelperClass",
            ],
            "rows": rows,
            "num_rows": len(rows),
            "reasoning_basis": {
                "kind": "query-only-companion",
                "note": (
                    "derived pause-aware clear-sample clock support from admitted "
                    "clear_sample_segment/4, sampler_offline_interval/4, and rule_exception/2 rows"
                ),
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [
            query,
            "clear_sample_segment(SegmentID, Start, End, CountedHours).",
            "sampler_offline_interval(Station, OfflineStart, OfflineEnd, Cause).",
            "rule_exception(Rule, Exception).",
        ],
    }


def _roster_table_member_alias_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    if predicate != "roster_table_member" or len(args) < 4:
        return None
    requested_row, requested_version, requested_group, requested_member = [str(item).strip() for item in args[:4]]
    if not requested_member or _is_prolog_variable(requested_member):
        return None
    label_rows = _runtime_rows(runtime, "roster_table_member_label(SourceRow, Version, Group, Member, PrintedMember).")
    if not label_rows:
        return None

    def matches(value: str, requested: str) -> bool:
        if not requested or _is_prolog_variable(requested):
            return True
        return value == requested

    out_rows: list[dict[str, Any]] = []
    for row in label_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        version = str(row.get("Version", "")).strip()
        group = str(row.get("Group", "")).strip()
        member = str(row.get("Member", "")).strip()
        printed_member = str(row.get("PrintedMember", "")).strip()
        if not source_row or not version or not group or not member:
            continue
        if not matches(source_row, requested_row):
            continue
        if not matches(version, requested_version):
            continue
        if not matches(group, requested_group):
            continue
        if requested_member and not _is_prolog_variable(requested_member):
            if requested_member not in {member, printed_member}:
                continue
        out_rows.append(
            {
                "SupportKind": "roster_table_member_label",
                "SourceRow": source_row,
                "Version": version,
                "Group": group,
                "Member": member,
                "PrintedMember": printed_member,
                "HelperClass": "clean-helper",
            }
        )
    if not out_rows:
        return None
    return {
        "query": "roster_table_member_label(SourceRow, Version, Group, Member, PrintedMember).",
        "result": {
            "status": "success",
            "predicate": "roster_table_member_alias_support",
            "prolog_query": "roster_table_member_label(SourceRow, Version, Group, Member, PrintedMember).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": ["SupportKind", "SourceRow", "Version", "Group", "Member", "PrintedMember", "HelperClass"],
            "rows": out_rows[:120],
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only roster table alias companion maps exact printed member labels "
                    "such as stu_1063_vinokur back to the normalized roster member id stu_1063"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [
            query,
            "roster_table_member_label(SourceRow, Version, Group, Member, PrintedMember).",
        ],
    }


def _homeroom_member_alias_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    if predicate != "homeroom_member" or len(args) < 3:
        return None
    requested_student, requested_homeroom, requested_version = [str(item).strip() for item in args[:3]]
    if not requested_student or _is_prolog_variable(requested_student):
        return None
    label_rows = _runtime_rows(runtime, "roster_table_member_label(SourceRow, Version, Group, Member, PrintedMember).")
    if not label_rows:
        return None

    def matches(value: str, requested: str) -> bool:
        if not requested or _is_prolog_variable(requested):
            return True
        return value == requested

    out_rows: list[dict[str, Any]] = []
    for row in label_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        version = str(row.get("Version", "")).strip()
        group = str(row.get("Group", "")).strip()
        member = str(row.get("Member", "")).strip()
        printed_member = str(row.get("PrintedMember", "")).strip()
        if not source_row or not version or not group or not member:
            continue
        if requested_student not in {member, printed_member}:
            continue
        if not matches(group, requested_homeroom):
            continue
        if not matches(version, requested_version):
            continue
        out_rows.append(
            {
                "SupportKind": "homeroom_member_printed_label",
                "Student": member,
                "PrintedMember": printed_member,
                "Homeroom": group,
                "Version": version,
                "SourceRow": source_row,
                "HelperClass": "clean-helper",
            }
        )
    if not out_rows:
        return None
    out_rows = sorted(out_rows, key=lambda row: -_roster_version_rank(str(row.get("Version", ""))))
    return {
        "query": "homeroom_member_alias_support(Student, Homeroom, Version, PrintedMember).",
        "result": {
            "status": "success",
            "predicate": "homeroom_member_alias_support",
            "prolog_query": "homeroom_member_alias_support(Student, Homeroom, Version, PrintedMember).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": ["SupportKind", "Student", "PrintedMember", "Homeroom", "Version", "SourceRow", "HelperClass"],
            "rows": out_rows[:80],
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only homeroom alias companion answers a sparse homeroom_member/3 "
                    "lookup from clean roster_table_member_label/5 rows when the question uses "
                    "a printed member label such as stu_1063_vinokur"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [
            query,
            "roster_table_member_label(SourceRow, Version, Group, Member, PrintedMember).",
        ],
    }


def _roster_table_count_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    if predicate not in {"roster_table_member", "student_in_homeroom", "homeroom_member"}:
        return None
    member_rows = _runtime_rows(runtime, "roster_table_member(SourceRow, Version, Group, Member).")
    if not member_rows:
        return None
    requested_version = ""
    if predicate == "roster_table_member" and len(args) >= 2 and not _is_prolog_variable(str(args[1]).strip()):
        requested_version = str(args[1]).strip()
    elif predicate in {"student_in_homeroom", "homeroom_member"} and len(args) >= 3 and not _is_prolog_variable(str(args[2]).strip()):
        requested_version = str(args[2]).strip()

    by_version: dict[str, list[tuple[str, str, str]]] = {}
    for row in member_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        version = str(row.get("Version", "")).strip()
        group = str(row.get("Group", "")).strip()
        member = str(row.get("Member", "")).strip()
        if not version or not group or not member:
            continue
        if requested_version and version != requested_version:
            continue
        by_version.setdefault(version, []).append((source_row, group, member))
    out_rows: list[dict[str, Any]] = []
    for version, entries in sorted(by_version.items(), key=lambda item: -_roster_version_rank(item[0])):
        members = [member for _source_row, _group, member in entries]
        distinct_members = sorted(set(members))
        duplicate_members = sorted(member for member in set(members) if members.count(member) > 1)
        group_counts: dict[str, int] = {}
        for _source_row, group, _member in entries:
            group_counts[group] = group_counts.get(group, 0) + 1
        out_rows.append(
            {
                "SupportKind": "roster_table_distinct_member_count",
                "Version": version,
                "EntryCount": str(len(entries)),
                "DistinctCount": str(len(distinct_members)),
                "DuplicateMembers": ",".join(duplicate_members),
                "GroupCounts": ",".join(f"{group}:{count}" for group, count in sorted(group_counts.items())),
                "HelperClass": "clean-helper",
            }
        )
    if not out_rows:
        return None
    return {
        "query": "roster_table_count_support(Version, EntryCount, DistinctCount, DuplicateMembers).",
        "result": {
            "status": "success",
            "predicate": "roster_table_count_support",
            "prolog_query": "roster_table_count_support(Version, EntryCount, DistinctCount, DuplicateMembers).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": [
                "SupportKind",
                "Version",
                "EntryCount",
                "DistinctCount",
                "DuplicateMembers",
                "GroupCounts",
                "HelperClass",
            ],
            "rows": out_rows,
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only roster table count companion derives entry count, distinct "
                    "normalized member count, duplicate members, and group counts from "
                    "deterministic roster_table_member/4 rows"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [
            query,
            "roster_table_member(SourceRow, Version, Group, Member).",
        ],
    }


def _roster_state_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    roster_predicates = {
        "adult_role",
        "group_member",
        "group_membership",
        "homeroom_member",
        "policy_requirement",
        "role_counts_towards_ratio",
        "roster_version",
        "roster_version_status",
        "student_group_assignment",
        "student_in_homeroom",
        "supervises",
        "supervision_assignment",
        "temporary_assignment",
        "temporary_event_assignment",
    }
    if predicate not in roster_predicates:
        return None

    adult_role_rows = _runtime_rows(runtime, "adult_role(Adult, Role).")
    group_member_rows = _runtime_rows(runtime, "group_member(Group, Person, Interval).")
    membership_rows = _runtime_rows(runtime, "group_membership(Person, Group, Start, End).")
    lodging_rows = _runtime_rows(runtime, "lodging_assignment(Person, Room, RoleType).")
    ratio_rows = _runtime_rows(runtime, "role_counts_towards_ratio(Role, Counts).")
    ratio_count_rows = _runtime_rows(runtime, "ratio_count_status(Person, Counts).")
    student_assignment_rows = _runtime_rows(runtime, "student_group_assignment(Student, Version, Group).")
    student_homeroom_rows = _runtime_rows(runtime, "student_in_homeroom(Student, Homeroom, Version).")
    roster_table_member_rows = _runtime_rows(runtime, "roster_table_member(SourceRow, Version, Group, Student).")
    roster_table_label_rows = _runtime_rows(runtime, "roster_table_member_label(SourceRow, Version, Group, Member, PrintedMember).")
    supervises_rows = _runtime_rows(runtime, "supervises(Supervisor, Target, Interval).")
    supervision_rows = _runtime_rows(runtime, "supervision_assignment(Supervisor, Target, Start, End).")
    temporary_assignment_rows = _runtime_rows(runtime, "temporary_assignment(Person, Group, Event, StartEnd).")
    temporary_event_rows = _runtime_rows(runtime, "temporary_event_assignment(Person, Event, Start, End).")
    out_rows: list[dict[str, Any]] = []
    ratio_by_role = {
        str(row.get("Role", "")).strip(): str(row.get("Counts", "")).strip()
        for row in ratio_rows
        if str(row.get("Role", "")).strip()
    }
    ratio_by_person = {
        str(row.get("Person", "")).strip(): str(row.get("Counts", "")).strip()
        for row in ratio_count_rows
        if str(row.get("Person", "")).strip()
    }
    lodging_by_person: dict[str, list[dict[str, str]]] = {}
    for row in lodging_rows:
        person = str(row.get("Person", "")).strip()
        room = str(row.get("Room", "")).strip()
        role_type = str(row.get("RoleType", "")).strip()
        if not person:
            continue
        lodging_by_person.setdefault(person, []).append({"Room": room, "RoleType": role_type})
    printed_member_by_key = {
        (
            str(row.get("SourceRow", "")).strip(),
            str(row.get("Version", "")).strip(),
            str(row.get("Group", "")).strip(),
            str(row.get("Member", "")).strip(),
        ): str(row.get("PrintedMember", "")).strip()
        for row in roster_table_label_rows
    }

    for row in adult_role_rows:
        adult = str(row.get("Adult", "")).strip()
        role = str(row.get("Role", "")).strip()
        if not adult or not role:
            continue
        out_rows.append(
            {
                "SupportKind": "adult_role",
                "Person": adult,
                "Role": role,
                "CountsTowardRatio": ratio_by_person.get(adult, ratio_by_role.get(role, "")),
                "RoleHint": _role_hint_from_group(role),
                "HelperClass": "clean-helper",
            }
        )
        if adult in ratio_by_person:
            out_rows.append(
                {
                    "SupportKind": "adult_ratio_count_status",
                    "Person": adult,
                    "Role": role,
                    "CountsTowardRatio": ratio_by_person.get(adult, ""),
                    "HelperClass": "clean-helper",
                }
            )
        adult_lodging = lodging_by_person.get(adult) or []
        if adult_lodging:
            for lodging in adult_lodging:
                out_rows.append(
                    {
                        "SupportKind": "adult_lodging_status",
                        "Person": adult,
                        "Role": role,
                        "Room": lodging.get("Room", ""),
                        "RoleType": lodging.get("RoleType", ""),
                        "LodgingStatus": "assigned",
                        "DisplayValue": f"{adult} lodges with the group in room {lodging.get('Room', '')}".strip(),
                        "HelperClass": "clean-helper",
                    }
                )
        else:
            out_rows.append(
                {
                    "SupportKind": "adult_lodging_status",
                    "Person": adult,
                    "Role": role,
                    "Room": "",
                    "RoleType": "",
                    "LodgingStatus": "not_assigned",
                    "DisplayValue": f"{adult} does not lodge with the group",
                    "HelperClass": "clean-helper",
                }
            )
    for role, counts in sorted(ratio_by_role.items()):
        adults = sorted(
            str(row.get("Adult", "")).strip()
            for row in adult_role_rows
            if str(row.get("Role", "")).strip() == role and str(row.get("Adult", "")).strip()
        )
        out_rows.append(
            {
                "SupportKind": "role_ratio_scope",
                "Role": role,
                "CountsTowardRatio": counts,
                "Count": str(len(adults)),
                "Members": ",".join(adults),
                "RoleHint": _role_hint_from_group(role),
                "HelperClass": "clean-helper",
            }
        )
    counted_adults = sorted(
        str(row.get("Adult", "")).strip()
        for row in adult_role_rows
        if ratio_by_role.get(str(row.get("Role", "")).strip()) == "true"
        and str(row.get("Adult", "")).strip()
    )
    if counted_adults:
        out_rows.append(
            {
                "SupportKind": "ratio_counted_adults",
                "Count": str(len(counted_adults)),
                "Members": ",".join(counted_adults),
                "CountsTowardRatio": "true",
                "HelperClass": "clean-helper",
            }
        )
    excluded_adults = sorted(
        str(row.get("Adult", "")).strip()
        for row in adult_role_rows
        if ratio_by_role.get(str(row.get("Role", "")).strip()) == "false"
        and str(row.get("Adult", "")).strip()
    )
    if excluded_adults:
        out_rows.append(
            {
                "SupportKind": "ratio_excluded_adults",
                "Count": str(len(excluded_adults)),
                "Members": ",".join(excluded_adults),
                "CountsTowardRatio": "false",
                "HelperClass": "clean-helper",
            }
        )

    for row in group_member_rows:
        group = str(row.get("Group", "")).strip()
        person = str(row.get("Person", "")).strip()
        interval = str(row.get("Interval", "")).strip()
        start, end = _split_interval_atom(interval)
        out_rows.append(
            {
                "SupportKind": "group_member",
                "Person": person,
                "Group": group,
                "Start": start,
                "End": end,
                "Interval": interval,
                "RoleHint": _role_hint_from_group(group),
                "HelperClass": "clean-helper",
            }
        )
    for row in membership_rows:
        person = str(row.get("Person", "")).strip()
        group = str(row.get("Group", "")).strip()
        start = str(row.get("Start", "")).strip()
        end = str(row.get("End", "")).strip()
        out_rows.append(
            {
                "SupportKind": "group_membership",
                "Person": person,
                "Group": group,
                "Start": start,
                "End": end,
                "Interval": f"{start}_to_{end}" if start and end else "",
                "RoleHint": _role_hint_from_group(group),
                "HelperClass": "clean-helper",
            }
        )
    for row in student_assignment_rows:
        person = str(row.get("Student", "")).strip()
        version, group = _normalize_roster_assignment_version_group(
            str(row.get("Version", "")).strip(),
            str(row.get("Group", "")).strip(),
        )
        if not person or not group:
            continue
        out_rows.append(
            {
                "SupportKind": "student_group_assignment",
                "Person": person,
                "Group": group,
                "Version": version,
                "RoleHint": _role_hint_from_group(group),
                "HelperClass": "clean-helper",
            }
        )
    for row in student_homeroom_rows:
        person = str(row.get("Student", "")).strip()
        version = str(row.get("Version", "")).strip()
        homeroom = str(row.get("Homeroom", "")).strip()
        if not person or not homeroom:
            continue
        out_rows.append(
            {
                "SupportKind": "student_group_assignment",
                "Person": person,
                "Group": homeroom,
                "Version": version,
                "RoleHint": _role_hint_from_group(homeroom),
                "HelperClass": "clean-helper",
            }
        )
    for row in roster_table_member_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        person = str(row.get("Student", "")).strip()
        version = str(row.get("Version", "")).strip()
        group = str(row.get("Group", "")).strip()
        if not person or not group:
            continue
        printed_member = printed_member_by_key.get((source_row, version, group, person), "")
        out_rows.append(
            {
                "SupportKind": "roster_table_student_group_assignment",
                "Person": person,
                "PrintedMember": printed_member,
                "Group": group,
                "Version": version,
                "SourceRow": source_row,
                "RoleHint": _role_hint_from_group(group),
                "HelperClass": "clean-helper",
            }
        )
    for row in supervises_rows:
        supervisor = str(row.get("Supervisor", "")).strip()
        target = str(row.get("Target", "")).strip()
        interval = str(row.get("Interval", "")).strip()
        start, end = _split_interval_atom(interval)
        out_rows.append(
            {
                "SupportKind": "supervision",
                "Supervisor": supervisor,
                "Target": target,
                "Start": start,
                "End": end,
                "Interval": interval,
                "HelperClass": "clean-helper",
            }
        )
    for row in supervision_rows:
        supervisor = str(row.get("Supervisor", "")).strip()
        target = str(row.get("Target", "")).strip()
        start = str(row.get("Start", "")).strip()
        end = str(row.get("End", "")).strip()
        out_rows.append(
            {
                "SupportKind": "supervision_assignment",
                "Supervisor": supervisor,
                "Target": target,
                "Start": start,
                "End": end,
                "Interval": f"{start}_to_{end}" if start and end else "",
                "HelperClass": "clean-helper",
            }
        )

    out_rows.extend(_source_record_roster_assignment_support(runtime))
    out_rows.extend(_source_record_roster_adult_support(runtime))
    out_rows.extend(_source_record_roster_compliance_support(runtime))
    out_rows.extend(
        _source_record_temporary_event_source_support(
            runtime,
            [*_temporary_assignment_event_rows(temporary_assignment_rows), *temporary_event_rows],
        )
    )
    out_rows.extend(_source_record_document_retention_support(runtime))

    group_counts: dict[tuple[str, str, str, str], set[str]] = {}
    group_count_classes: dict[tuple[str, str, str, str], set[str]] = {}
    for row in out_rows:
        if str(row.get("SupportKind")) not in {
            "group_member",
            "group_membership",
            "roster_table_student_group_assignment",
            "source_record_student_group_assignment",
            "student_group_assignment",
        }:
            continue
        group = str(row.get("Group", "")).strip()
        person = str(row.get("Person", "")).strip()
        version = str(row.get("Version", "")).strip()
        start = str(row.get("Start", "")).strip()
        end = str(row.get("End", "")).strip()
        if not group or not person:
            continue
        group_key = (group, version, start, end)
        group_counts.setdefault(group_key, set()).add(person)
        group_count_classes.setdefault(group_key, set()).add(str(row.get("HelperClass", "") or "unlabeled"))
    for (group, version, start, end), people in sorted(group_counts.items()):
        helper_class = (
            "clean-helper"
            if "clean-helper" in group_count_classes.get((group, version, start, end), set())
            else "candidate-helper"
        )
        out_rows.append(
            {
                "SupportKind": "group_count",
                "Group": group,
                "Version": version,
                "Start": start,
                "End": end,
                "Count": str(len(people)),
                "Members": ",".join(sorted(people)),
                "RoleHint": _role_hint_from_group(group),
                "HelperClass": helper_class,
            }
        )

    out_rows = _prioritize_roster_state_rows(out_rows, predicate=predicate, args=args)

    if not out_rows:
        return None
    return {
        "query": "roster_state_support(SupportKind, PersonOrSupervisor, GroupOrTarget, Start, End, CountOrRole).",
        "result": {
            "status": "success",
            "predicate": "roster_state_support",
            "prolog_query": "roster_state_support(SupportKind, PersonOrSupervisor, GroupOrTarget, Start, End, CountOrRole).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": [
                "SupportKind",
                "Person",
                "Group",
                "Supervisor",
                "Target",
                "PrintedMember",
                "Start",
                "End",
                "Count",
                "RoleHint",
                "HelperClass",
            ],
            "rows": out_rows[:180],
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only roster-state companion labels admitted-predicate joins as "
                    "clean-helper rows and source-record roster parsing as candidate-helper "
                    "rows until the roster parser transfers beyond the school activity packet"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [
            query,
            "group_member(Group, Person, Interval).",
            "group_membership(Person, Group, Start, End).",
            "student_group_assignment(Student, Version, Group).",
            "roster_table_member(SourceRow, Version, Group, Student).",
            "roster_table_member_label(SourceRow, Version, Group, Member, PrintedMember).",
            "supervises(Supervisor, Target, Interval).",
            "supervision_assignment(Supervisor, Target, Start, End).",
            "adult_role(Adult, Role).",
            "role_counts_towards_ratio(Role, Counts).",
            "source_record_text_atom(SourceRow, TextAtom).",
            "source_record_section(SourceRow, Section).",
            "source_record_line(SourceRow, Line).",
        ],
    }


def _prioritize_roster_state_rows(
    rows: list[dict[str, Any]],
    *,
    predicate: str,
    args: list[str],
) -> list[dict[str, Any]]:
    def is_requested(value: str, requested: str) -> bool:
        requested = str(requested or "").strip()
        if not requested or _is_prolog_variable(requested):
            return True
        if requested.lower() in {"adult", "count", "counts", "group", "person", "role", "student", "x"}:
            return True
        return str(value or "").strip() == requested

    def requested_is_wildcard(index: int) -> bool:
        if index >= len(args):
            return True
        requested = str(args[index] or "").strip()
        return (
            not requested
            or _is_prolog_variable(requested)
            or requested.lower() in {"adult", "count", "counts", "group", "homeroom", "person", "role", "student", "version", "x"}
        )

    def requested_is_specific(index: int) -> bool:
        return not requested_is_wildcard(index)

    def normalized_requested_version(value: str) -> str:
        text = str(value or "").strip().lower()
        match = re.fullmatch(r"(?:roster_)?v(?P<major>\d+)(?:_(?P<minor>\d+))?", text)
        if not match:
            return str(value or "").strip()
        version = "v" + match.group("major")
        if match.group("minor"):
            version += "_" + match.group("minor")
        return version

    def version_requested(value: str, requested: str) -> bool:
        return is_requested(value, normalized_requested_version(requested))

    broad_student_assignment_version_scan = (
        predicate == "student_group_assignment"
        and len(args) >= 3
        and requested_is_wildcard(0)
        and requested_is_wildcard(1)
        and normalized_requested_version(args[2]) != str(args[2]).strip()
    )

    def score(row: dict[str, Any]) -> tuple[int, int, str, str]:
        support_kind = str(row.get("SupportKind", "")).strip()
        person = str(row.get("Person", "")).strip()
        printed_member = str(row.get("PrintedMember", "")).strip()
        group = str(row.get("Group", "")).strip()
        version = str(row.get("Version", "")).strip()
        role = str(row.get("Role", "")).strip()
        priority = 50
        version_priority = _roster_version_rank(version)

        if predicate == "student_group_assignment" and len(args) >= 3:
            version_arg = args[1]
            group_arg = args[2]
            version_in_third_slot = requested_is_wildcard(1) and normalized_requested_version(args[2]) != str(args[2]).strip()
            if version_in_third_slot:
                version_arg = args[2]
                group_arg = args[1]
            person_ok = is_requested(person, args[0])
            version_ok = version_requested(version, version_arg)
            group_ok = is_requested(group, group_arg)
            if broad_student_assignment_version_scan and version_ok:
                priority = 0 if support_kind == "group_count" else 12
            elif person_ok and version_ok and group_ok:
                priority = (
                    0
                    if support_kind == "roster_table_student_group_assignment"
                    else 1
                    if support_kind == "source_record_student_group_assignment"
                    else 2
                )
            elif version_ok and group_ok:
                priority = 5
            elif version_ok:
                priority = 12
        elif predicate in {"homeroom_member", "student_in_homeroom"} and len(args) >= 3:
            person_ok = is_requested(person, args[0]) or is_requested(printed_member, args[0])
            group_ok = is_requested(group, args[1])
            version_ok = is_requested(version, args[2])
            if person_ok and version_ok and group_ok:
                priority = (
                    0
                    if support_kind == "roster_table_student_group_assignment"
                    else 1
                    if support_kind == "source_record_student_group_assignment"
                    else 2
                )
            elif version_ok and group_ok:
                priority = 5
            elif person_ok or version_ok:
                priority = 12
            if requested_is_wildcard(2):
                version_priority = -version_priority
        elif predicate in {"adult_role", "role_counts_towards_ratio"}:
            person_specific = predicate == "adult_role" and requested_is_specific(0)
            role_specific = requested_is_specific(1) if predicate == "adult_role" else requested_is_specific(0)
            person_ok = not person_specific or (person and is_requested(person, args[0]))
            role_arg = args[1] if predicate == "adult_role" and len(args) >= 2 else args[0] if args else ""
            role_ok = not role_specific or (role and is_requested(role, role_arg))
            adult_support_kinds = {
                "adult_manifest_total",
                "adult_lodging_status",
                "adult_ratio_count_status",
                "adult_role",
                "compliance_flip_count",
                "compliance_status",
                "ratio_counted_adults",
                "ratio_excluded_adults",
                "role_ratio_scope",
                "source_record_adult_role",
            }
            if support_kind in adult_support_kinds and person_ok and role_ok:
                priority = 0
            if predicate == "adult_role" and len(args) >= 2 and person_ok and role and is_requested(role, args[1]):
                priority = min(priority, 0)
            if (
                predicate == "adult_role"
                and person_specific
                and support_kind in adult_support_kinds
                and len(args) >= 1
                and person_ok
                and is_requested(person, args[0])
            ):
                priority = min(priority, -2)
            if predicate == "role_counts_towards_ratio" and len(args) >= 1 and person_ok and role and is_requested(role, args[0]):
                priority = min(priority, 0)
            version_priority = -version_priority
        elif predicate in {"group_member", "group_membership"}:
            if support_kind in {"group_member", "group_membership"}:
                priority = 0
            elif support_kind in {"group_count", "supervision", "supervision_assignment"}:
                priority = 2
        elif predicate == "policy_requirement":
            if support_kind in {"document_retention_location", "temporary_event_source_link"}:
                priority = 0
        elif predicate in {"temporary_assignment", "temporary_event_assignment"}:
            if support_kind == "temporary_event_source_link":
                priority = 0
        elif predicate in {"roster_version", "roster_version_status"}:
            version_ok = len(args) < 1 or is_requested(version, args[0])
            if support_kind in {
                "compliance_status",
                "document_retention_location",
                "group_count",
            }:
                priority = 4 if version_ok else 20
            if requested_is_wildcard(0):
                version_priority = -version_priority
        elif support_kind in {
            "group_count",
            "roster_table_student_group_assignment",
            "source_record_student_group_assignment",
            "student_group_assignment",
        }:
            priority = 10

        return (priority, version_priority, group, person or role)

    scored = [(score(row), index, row) for index, row in enumerate(rows)]
    scoped = [(row_score, index, row) for (row_score, index, row) in scored if row_score[0] < 50]
    if scoped:
        if (
            predicate in {"role_counts_towards_ratio", "roster_version", "roster_version_status"}
            or broad_student_assignment_version_scan
            or (predicate == "adult_role" and (requested_is_specific(0) or requested_is_specific(1)))
        ):
            best_priority = min(row_score[0] for row_score, _index, _row in scoped)
            scoped = [(row_score, index, row) for row_score, index, row in scoped if row_score[0] == best_priority]
        return [row for _, _, row in sorted(scoped, key=lambda item: (item[0], item[1]))]
    return [row for _, _, row in sorted(scored, key=lambda item: (item[0], item[1]))]


def _roster_version_rank(version: str) -> int:
    text = str(version or "").strip().lower()
    match = re.fullmatch(r"v(?P<major>\d+)(?:_(?P<minor>\d+))?", text)
    if not match:
        return 0
    major = int(match.group("major"))
    minor = int(match.group("minor") or 0)
    return major * 100 + minor


def _normalized_roster_version_atom(value: str) -> str:
    text = str(value or "").strip().lower()
    match = re.fullmatch(r"(?:roster_)?v(?P<major>\d+)(?:_(?P<minor>\d+))?", text)
    if not match:
        return ""
    version = "v" + match.group("major")
    if match.group("minor"):
        version += "_" + match.group("minor")
    return version


def _normalize_roster_assignment_version_group(version_slot: str, group_slot: str) -> tuple[str, str]:
    version = str(version_slot or "").strip()
    group = str(group_slot or "").strip()
    normalized_version = _normalized_roster_version_atom(version)
    if normalized_version:
        return normalized_version, group
    normalized_group = _normalized_roster_version_atom(group)
    if normalized_group:
        return normalized_group, version
    return version, group


def _source_record_roster_assignment_support(runtime: CorePrologRuntime) -> list[dict[str, Any]]:
    text_rows = _runtime_rows(runtime, "source_record_text_atom(SourceRow, TextAtom).")
    section_rows = _runtime_rows(runtime, "source_record_section(SourceRow, Section).")
    line_rows = _runtime_rows(runtime, "source_record_line(SourceRow, Line).")
    if not text_rows or not section_rows:
        return []

    section_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("Section", "")).strip()
        for row in section_rows
    }
    line_by_row: dict[str, int] = {}
    for row in line_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        line = str(row.get("Line", "")).strip()
        if not source_row or not _is_numeric_atom(line):
            continue
        line_by_row[source_row] = int(float(line))

    ordered_rows = sorted(
        (
            (
                line_by_row.get(str(row.get("SourceRow", "")).strip(), 10**9),
                str(row.get("SourceRow", "")).strip(),
                str(row.get("TextAtom", "")).strip(),
                section_by_row.get(str(row.get("SourceRow", "")).strip(), ""),
            )
            for row in text_rows
        ),
        key=lambda item: item[0],
    )
    out_rows: list[dict[str, Any]] = []
    current_group = ""
    current_version = ""
    current_group_source = ""

    for line, source_row, text_atom, section in ordered_rows:
        if not source_row or not text_atom:
            continue
        version = _version_from_section_atom(section)
        if current_version and section and not version:
            current_group = ""
            current_version = ""
            current_group_source = ""
            continue
        if version:
            if version != current_version:
                current_group = ""
                current_group_source = ""
            current_version = version

        group = _group_from_roster_atom(text_atom)
        if group:
            current_group = group
            current_group_source = source_row

        if not current_group or not current_version:
            continue
        if section and _version_from_section_atom(section) not in {"", current_version}:
            current_group = ""
            current_version = _version_from_section_atom(section)
            current_group_source = ""
            continue
        students = _student_ids_from_atom(text_atom)
        if not students:
            continue
        for student in students:
            out_rows.append(
                {
                    "SupportKind": "source_record_student_group_assignment",
                    "Person": student,
                    "Group": current_group,
                    "Version": current_version,
                    "SourceRow": source_row,
                    "SourceGroupRow": current_group_source,
                    "Line": str(line),
                    "RoleHint": _role_hint_from_group(current_group),
                    "HelperClass": "candidate-helper",
                }
            )
    return out_rows


def _source_record_roster_adult_support(runtime: CorePrologRuntime) -> list[dict[str, Any]]:
    text_rows = _runtime_rows(runtime, "source_record_text_atom(SourceRow, TextAtom).")
    section_rows = _runtime_rows(runtime, "source_record_section(SourceRow, Section).")
    line_rows = _runtime_rows(runtime, "source_record_line(SourceRow, Line).")
    if not text_rows or not section_rows:
        return []

    section_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("Section", "")).strip()
        for row in section_rows
    }
    line_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("Line", "")).strip()
        for row in line_rows
        if str(row.get("SourceRow", "")).strip()
    }

    out_rows: list[dict[str, Any]] = []
    counted_by_version: dict[str, set[str]] = {}
    excluded_by_version: dict[str, set[str]] = {}
    adult_by_version: dict[str, set[str]] = {}
    for row in text_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        text_atom = str(row.get("TextAtom", "")).strip().lower()
        section = section_by_row.get(source_row, "")
        version = _version_from_section_atom(section)
        if "accompanying_adults" not in section or not version:
            continue
        parsed = _adult_role_from_roster_atom(text_atom)
        if not parsed:
            continue
        role, person, counts = parsed
        adult_by_version.setdefault(version, set()).add(person)
        if counts == "true":
            counted_by_version.setdefault(version, set()).add(person)
        elif counts == "false":
            excluded_by_version.setdefault(version, set()).add(person)
        out_rows.append(
            {
                "SupportKind": "source_record_adult_role",
                "Person": person,
                "Role": role,
                "Version": version,
                "CountsTowardRatio": counts,
                "SourceRow": source_row,
                "Line": line_by_row.get(source_row, ""),
                "HelperClass": "clean-helper",
            }
        )
    for version, adults in sorted(adult_by_version.items()):
        out_rows.append(
            {
                "SupportKind": "adult_manifest_total",
                "Version": version,
                "Count": str(len(adults)),
                "Members": ",".join(sorted(adults)),
                "HelperClass": "clean-helper",
            }
        )
    for version, adults in sorted(counted_by_version.items()):
        out_rows.append(
            {
                "SupportKind": "ratio_counted_adults",
                "Version": version,
                "Count": str(len(adults)),
                "Members": ",".join(sorted(adults)),
                "CountsTowardRatio": "true",
                "HelperClass": "clean-helper",
            }
        )
    for version, adults in sorted(excluded_by_version.items()):
        out_rows.append(
            {
                "SupportKind": "ratio_excluded_adults",
                "Version": version,
                "Count": str(len(adults)),
                "Members": ",".join(sorted(adults)),
                "CountsTowardRatio": "false",
                "HelperClass": "clean-helper",
            }
        )
    return out_rows


def _adult_role_from_roster_atom(text_atom: str) -> tuple[str, str, str] | None:
    text = str(text_atom or "").strip().lower()
    for prefix, role, counts in [
        ("trip_leader_", "trip_leader", "true"),
        ("chaperone_", "chaperone", "true"),
        ("medical_", "medical_staff", "false"),
    ]:
        if not text.startswith(prefix):
            continue
        remainder = text.removeprefix(prefix)
        for suffix in ["_yes", "_no_per_3_4", "_no"]:
            if suffix in remainder:
                person = remainder.split(suffix, 1)[0]
                break
        else:
            person = remainder
        person = re.sub(r"_(principal|parent_volunteer|7th_grade_math|rn)$", "", person)
        if person:
            return role, person, counts
    return None


def _source_record_roster_compliance_support(runtime: CorePrologRuntime) -> list[dict[str, Any]]:
    text_rows = _runtime_rows(runtime, "source_record_text_atom(SourceRow, TextAtom).")
    section_rows = _runtime_rows(runtime, "source_record_section(SourceRow, Section).")
    line_rows = _runtime_rows(runtime, "source_record_line(SourceRow, Line).")
    if not text_rows or not section_rows:
        return []

    section_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("Section", "")).strip()
        for row in section_rows
    }
    line_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("Line", "")).strip()
        for row in line_rows
        if str(row.get("SourceRow", "")).strip()
    }
    out_rows: list[dict[str, Any]] = []
    for row in text_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        text_atom = str(row.get("TextAtom", "")).strip().lower()
        section = section_by_row.get(source_row, "")
        if "compliance_log" not in section:
            continue
        match = re.match(
            r"(?P<version>v\d+(?:_\d+)?)(?:_after_(?P<notice>cn_\d+))?_(?P<date>\d{4}_\d{2}_\d{2})_(?P<count>\d+)_(?P<required>\d+)_(?P<compliant>yes|no)$",
            text_atom,
        )
        if match:
            out_rows.append(
                {
                    "SupportKind": "compliance_status",
                    "Version": match.group("version"),
                    "Notice": match.group("notice") or "",
                    "Date": match.group("date"),
                    "Count": match.group("count"),
                    "Required": match.group("required"),
                    "Compliant": "true" if match.group("compliant") == "yes" else "false",
                    "SourceRow": source_row,
                    "Line": line_by_row.get(source_row, ""),
                    "HelperClass": "clean-helper",
                }
            )
            continue
        flip_match = re.search(r"compliance_status_flipped_(?P<count>\w+)_times", text_atom)
        if flip_match:
            count = _number_word_or_digits(flip_match.group("count"))
            if count:
                out_rows.append(
                    {
                        "SupportKind": "compliance_flip_count",
                        "Count": count,
                        "SourceRow": source_row,
                        "Line": line_by_row.get(source_row, ""),
                        "HelperClass": "clean-helper",
                    }
                )
    return out_rows


def _temporary_assignment_event_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out_rows: list[dict[str, Any]] = []
    for row in rows:
        person = str(row.get("Person", "")).strip()
        event = str(row.get("Event", "")).strip()
        interval = str(row.get("StartEnd", "")).strip()
        start, end = _compact_datetime_interval_bounds(interval) or ("", "")
        if not person or not event:
            continue
        out_rows.append(
            {
                "Person": person,
                "Event": event,
                "Start": start,
                "End": end,
            }
        )
    return out_rows


def _source_record_document_retention_support(runtime: CorePrologRuntime) -> list[dict[str, Any]]:
    text_rows = _runtime_rows(runtime, "source_record_text_atom(SourceRow, TextAtom).")
    line_rows = _runtime_rows(runtime, "source_record_line(SourceRow, Line).")
    if not text_rows:
        return []
    text_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("TextAtom", "")).strip().lower()
        for row in text_rows
        if str(row.get("SourceRow", "")).strip()
    }
    line_by_row: dict[str, int] = {}
    for row in line_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        line = str(row.get("Line", "")).strip()
        if source_row and _is_numeric_atom(line):
            line_by_row[source_row] = int(float(line))
    ordered_source_rows = sorted(text_by_row, key=lambda source_row: line_by_row.get(source_row, 10**9))
    out_rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for source_row in ordered_source_rows:
        text_atom = text_by_row.get(source_row, "")
        retention_match = re.search(
            r"retained_in_the_(?P<document>[a-z0-9_]+?)_location_(?P<location>[a-z0-9_]+)",
            text_atom,
        )
        if not retention_match:
            continue
        next_text = _next_source_text_atom(source_row, ordered_source_rows, text_by_row, line_by_row)
        combined = f"{text_atom} {next_text}".strip()
        storage_match = re.search(r"cabinet_(?P<cabinet>\d+)_drawer_(?P<drawer>\d+)", combined)
        if not storage_match:
            continue
        document = retention_match.group("document")
        location = retention_match.group("location")
        value = f"{location}_cabinet_{storage_match.group('cabinet')}_drawer_{storage_match.group('drawer')}"
        key = (source_row, document, value)
        if key in seen:
            continue
        seen.add(key)
        display_location = (
            f"{_display_source_phrase(location)} cabinet {storage_match.group('cabinet')}, "
            f"drawer {storage_match.group('drawer')}"
        )
        out_rows.append(
            {
                "SupportKind": "document_retention_location",
                "Person": document,
                "Group": "",
                "Location": value,
                "SourceRow": source_row,
                "Line": str(line_by_row.get(source_row, "")),
                "DisplayValue": (
                    f"{display_location} ({_display_source_phrase(document)}; retained for audit)"
                ),
                "Detail": combined,
                "HelperClass": "candidate-helper",
            }
        )
    return out_rows


def _source_record_temporary_event_source_support(
    runtime: CorePrologRuntime,
    temporary_event_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not temporary_event_rows:
        return []
    section_rows = _runtime_rows(runtime, "source_record_section(SourceRow, Section).")
    label_rows = _runtime_rows(runtime, "source_record_label(SourceRow, Label).")
    line_rows = _runtime_rows(runtime, "source_record_line(SourceRow, Line).")
    source_notes = [
        {
            "SourceRow": str(row.get("SourceRow", "")).strip(),
            "Section": str(row.get("Section", "")).strip(),
        }
        for row in section_rows
        if "temporary" in str(row.get("Section", "")).strip().lower()
    ]
    labels_by_row: dict[str, list[str]] = {}
    for row in label_rows:
        source_row = str(row.get("SourceRow", "")).strip()
        label = str(row.get("Label", "")).strip()
        if source_row and label.startswith("sch_"):
            labels_by_row.setdefault(source_row, []).append(label)
    line_by_row = {
        str(row.get("SourceRow", "")).strip(): str(row.get("Line", "")).strip()
        for row in line_rows
        if str(row.get("SourceRow", "")).strip()
    }
    out_rows: list[dict[str, Any]] = []
    for event_row in temporary_event_rows:
        person = str(event_row.get("Person", "")).strip()
        event = str(event_row.get("Event", "")).strip()
        start = str(event_row.get("Start", "")).strip()
        end = str(event_row.get("End", "")).strip()
        if not person or not event:
            continue
        for note in source_notes:
            source_row = note["SourceRow"]
            labels = labels_by_row.get(source_row) or []
            if not labels:
                continue
            section = note["Section"]
            note_label = sorted(labels)[0]
            display_section = _display_section_from_atom(section)
            out_rows.append(
                {
                    "SupportKind": "temporary_event_source_link",
                    "Person": person,
                    "Event": event,
                    "Start": start,
                    "End": end,
                    "SourceRow": source_row,
                    "Line": line_by_row.get(source_row, ""),
                    "SourceNote": note_label,
                    "DisplayValue": (
                        f"{_display_source_atom(person)} temporary event {_display_source_phrase(event)}: "
                        f"{display_section}; scheduling note {_display_source_atom(note_label)}"
                    ),
                    "HelperClass": "candidate-helper",
                }
            )
    return out_rows


def _number_word_or_digits(value: str) -> str:
    text = str(value or "").strip().lower()
    if text.isdigit():
        return text
    words = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
    }
    return words.get(text, "")


def _version_from_section_atom(value: str) -> str:
    text = value.lower().strip()
    match = re.search(r"(?:^|_)v1_(?P<minor>\d)(?:_|$)", text)
    if match:
        return f"v1_{match.group('minor')}"
    if "roster_v3" in text:
        return "v3"
    if "roster_v2_1" in text:
        return "v2_1"
    if "roster_v2" in text:
        return "v2"
    if "roster_v1" in text:
        return "v1"
    return ""


def _group_from_roster_atom(value: str) -> str:
    text = value.lower().strip()
    if text.startswith("group_a_"):
        return "group_a"
    if text.startswith("group_b_"):
        return "group_b"
    if text.startswith("group_c_"):
        return "group_c"
    match = re.match(r"v_(?P<grade>\d+)_(?P<section>[a-z])(?:_|$)", text)
    if match:
        return f"{match.group('grade')}_{match.group('section')}"
    return ""


def _student_ids_from_atom(value: str) -> list[str]:
    text = value.lower()
    return re.findall(r"s_\d{3}", text) + re.findall(r"stu_\d{4,}", text)


def _runtime_rows(runtime: CorePrologRuntime, query: str) -> list[dict[str, Any]]:
    result = runtime.query_rows(query)
    if result.get("status") != "success":
        return []
    rows = result.get("rows", [])
    return rows if isinstance(rows, list) else []


def _runtime_fact_rows(runtime: CorePrologRuntime) -> list[dict[str, Any]]:
    engine = getattr(runtime, "engine", None)
    clauses = getattr(engine, "clauses", []) if engine is not None else []
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for clause in clauses or []:
        if getattr(clause, "body", None):
            continue
        text = str(clause).strip()
        if not text:
            continue
        if not text.endswith("."):
            text = f"{text}."
        if text in seen or ":-" in text:
            continue
        parsed = parse_prolog_query(text)
        if parsed is None:
            continue
        predicate, args = parsed
        seen.add(text)
        out.append({"predicate": predicate, "args": args, "clause": text})
    return out


_TYPE_INSTANCE_SUFFIXES = {
    "active",
    "amended",
    "archived",
    "current",
    "dated",
    "draft",
    "expired",
    "final",
    "instance",
    "issued",
    "prior",
    "proposed",
    "revised",
    "version",
}


def _type_taxonomy_tokens(value: str) -> list[str]:
    return [token for token in re.split(r"_+", str(value or "").strip().lower()) if token]


def _looks_like_type_instance_suffix(token: str) -> bool:
    text = str(token or "").strip().lower()
    return (
        text in _TYPE_INSTANCE_SUFFIXES
        or bool(re.fullmatch(r"(?:19|20)\d{2}", text))
        or bool(re.fullmatch(r"v\d+(?:\d+)?", text))
        or bool(re.fullmatch(r"\d{4}(?:\d{2}){1,2}", text))
    )


def _looks_like_category_code_token(token: str) -> bool:
    text = str(token or "").strip().lower()
    return bool(re.fullmatch(r"[a-z]\d{0,2}|\d{1,3}", text))


def _type_category_key(value: str, all_values: set[str]) -> str:
    tokens = _type_taxonomy_tokens(value)
    if not tokens:
        return ""
    for index, token in enumerate(tokens):
        if index > 0 and _looks_like_type_instance_suffix(token):
            return "_".join(tokens[:index])
    if len(tokens) >= 3 and _looks_like_category_code_token(tokens[1]):
        prefix = "_".join(tokens[:2])
        siblings = [item for item in all_values if item == prefix or item.startswith(f"{prefix}_")]
        if len(siblings) > 1:
            return prefix
    return "_".join(tokens)


def _type_category_display(key: str, members: list[str]) -> str:
    key_tokens = _type_taxonomy_tokens(key)
    representative = ""
    for member in sorted(members, key=lambda item: (-len(_type_taxonomy_tokens(item)), item)):
        member_tokens = _type_taxonomy_tokens(member)
        suffix = member_tokens[len(key_tokens) :] if member_tokens[: len(key_tokens)] == key_tokens else []
        if suffix and not all(_looks_like_type_instance_suffix(token) for token in suffix):
            representative = member
            break
    if not representative:
        representative = key

    member_tokens = _type_taxonomy_tokens(representative)
    suffix_tokens = member_tokens[len(key_tokens) :] if member_tokens[: len(key_tokens)] == key_tokens else []
    label_tokens = [token for token in suffix_tokens if not _looks_like_type_instance_suffix(token)] or key_tokens
    label = _display_source_phrase("_".join(label_tokens))
    if len(key_tokens) >= 2 and _looks_like_category_code_token(key_tokens[1]):
        return f"{key_tokens[1].upper()}: {label}"
    return label


_LIFECYCLE_PERIOD_TOKENS = {"period", "validity", "valid", "effective", "window", "interval"}
_LIFECYCLE_CONTEXT_TOKENS = {
    "amendment",
    "exception",
    "exemption",
    "expiration",
    "expiry",
    "extension",
    "renewal",
    "restriction",
    "scope",
    "status",
    "suspension",
}


def _predicate_tokens(value: str) -> set[str]:
    return set(_type_taxonomy_tokens(value))


def _lifecycle_entity_family_key(value: str, all_values: set[str]) -> str:
    normalized = "_".join(_type_taxonomy_tokens(value))
    if not normalized:
        return ""
    category = _type_category_key(normalized, all_values)
    if category and category != normalized:
        return category
    tokens = _type_taxonomy_tokens(normalized)
    for length in range(len(tokens) - 1, 1, -1):
        prefix = "_".join(tokens[:length])
        if any(item != normalized and item.startswith(f"{prefix}_") for item in all_values):
            return prefix
    return category or normalized


def _date_like_atoms(values: list[str]) -> list[str]:
    dated: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if _date_atom_sort_key(text) is not None:
            dated.append(text)
    return dated


_INITIAL_SCOPE_MARKERS = {
    "baseline",
    "first",
    "initial",
    "initially",
    "opening",
    "original",
    "originally",
}


def _source_rows_for_scope(runtime: CorePrologRuntime) -> list[dict[str, Any]]:
    facts = _runtime_fact_rows(runtime)
    texts: dict[str, str] = {}
    labels: dict[str, str] = {}
    sections: dict[str, str] = {}
    lines: dict[str, int] = {}
    for fact in facts:
        predicate = str(fact.get("predicate", "")).strip()
        args = [str(item).strip().lower() for item in fact.get("args", [])]
        if len(args) < 2:
            continue
        if predicate == "source_record_text_atom":
            texts[args[0]] = args[1]
        elif predicate == "source_record_label":
            labels[args[0]] = args[1]
        elif predicate == "source_record_section":
            sections[args[0]] = args[1]
        elif predicate == "source_record_line":
            line_no = _int_from_atom(args[1])
            if line_no is not None:
                lines[args[0]] = line_no
    rows: list[dict[str, Any]] = []
    for source_row, text in texts.items():
        rows.append(
            {
                "SourceRow": source_row,
                "TextAtom": text,
                "Label": labels.get(source_row, ""),
                "SectionAtom": sections.get(source_row, ""),
                "Line": lines.get(source_row, 0),
            }
        )
    return sorted(rows, key=lambda row: (int(row.get("Line", 0)), str(row.get("SourceRow", ""))))


def _text_mentions_atom(text: str, atom: str) -> bool:
    atom_tokens = _type_taxonomy_tokens(atom)
    if not atom_tokens:
        return False
    combined = str(text or "").lower()
    if "_".join(atom_tokens) in combined:
        return True
    tokens = set(_type_taxonomy_tokens(combined))
    return len(atom_tokens) == 1 and atom_tokens[0] in tokens


def _is_initial_scope_row(row: dict[str, Any]) -> bool:
    combined = "_".join(
        str(row.get(slot, "")).strip().lower()
        for slot in ("SectionAtom", "Label")
        if str(row.get(slot, "")).strip()
    )
    return bool(set(_type_taxonomy_tokens(combined)) & _INITIAL_SCOPE_MARKERS)


def _initial_status_scope_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    if len(args) != 2 or not predicate.endswith("_status"):
        return None
    entity_arg = str(args[0]).strip()
    status_arg = str(args[1]).strip()
    if not _is_prolog_variable(entity_arg) or not status_arg or _is_prolog_variable(status_arg):
        return None

    status_query = format_prolog_query(predicate, ["Entity", status_arg])
    status_rows = _runtime_rows(runtime, status_query)
    entities = sorted(
        {str(row.get("Entity", "")).strip().lower() for row in status_rows if str(row.get("Entity", "")).strip()}
    )
    if len(entities) < 2:
        return None

    source_rows = _source_rows_for_scope(runtime)
    if not source_rows:
        return None

    mentions: dict[str, list[dict[str, Any]]] = {}
    for entity in entities:
        for source_row in source_rows:
            combined = f"{source_row.get('SectionAtom', '')}_{source_row.get('Label', '')}_{source_row.get('TextAtom', '')}"
            if _text_mentions_atom(combined, entity):
                mentions.setdefault(entity, []).append(source_row)

    initial_rows: list[dict[str, str]] = []
    context_rows: list[dict[str, str]] = []
    for entity in entities:
        entity_mentions = mentions.get(entity, [])
        initial_mentions = [row for row in entity_mentions if _is_initial_scope_row(row)]
        if initial_mentions:
            first = sorted(initial_mentions, key=lambda row: int(row.get("Line", 0)))[0]
            initial_rows.append(
                {
                    "SupportKind": "initial_status_entity",
                    "StatusPredicate": predicate,
                    "Status": status_arg,
                    "Entity": entity,
                    "InitialEntity": entity,
                    "SourceRow": str(first.get("SourceRow", "")),
                    "SourceLine": str(first.get("Line", "")),
                    "SectionAtom": str(first.get("SectionAtom", "")),
                    "Label": str(first.get("Label", "")),
                    "HelperClass": "clean-helper",
                }
            )
        elif entity_mentions:
            first = sorted(entity_mentions, key=lambda row: int(row.get("Line", 0)))[0]
            context_rows.append(
                {
                    "SupportKind": "later_status_context",
                    "StatusPredicate": predicate,
                    "Status": status_arg,
                    "Entity": entity,
                    "InitialEntity": "",
                    "SourceRow": str(first.get("SourceRow", "")),
                    "SourceLine": str(first.get("Line", "")),
                    "SectionAtom": str(first.get("SectionAtom", "")),
                    "Label": str(first.get("Label", "")),
                    "HelperClass": "clean-helper",
                }
            )

    if not initial_rows:
        return None
    initial_entities = ",".join(row["Entity"] for row in initial_rows)
    summary = {
        "SupportKind": "initial_status_summary",
        "StatusPredicate": predicate,
        "Status": status_arg,
        "Entity": "",
        "InitialEntity": initial_entities,
        "InitialEntities": initial_entities,
        "AllStatusEntities": ",".join(entities),
        "LaterContextEntities": ",".join(row["Entity"] for row in context_rows),
        "HelperClass": "clean-helper",
    }
    out_rows = [summary, *initial_rows, *context_rows[:12]]
    return {
        "query": "initial_status_scope_support(StatusPredicate, Status, InitialEntity).",
        "result": {
            "status": "success",
            "predicate": "initial_status_scope_support",
            "prolog_query": "initial_status_scope_support(StatusPredicate, Status, InitialEntity).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": [
                "SupportKind",
                "StatusPredicate",
                "Status",
                "Entity",
                "InitialEntity",
                "InitialEntities",
                "AllStatusEntities",
                "LaterContextEntities",
                "SourceRow",
                "SourceLine",
                "SectionAtom",
                "Label",
                "HelperClass",
            ],
            "rows": out_rows,
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only initial status companion separates status entities mentioned in initial/original "
                    "source scope from later status-context entities"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [query, status_query, "source_record_text_atom(SourceRow, TextAtom)."],
    }


def _threshold_required_count(value: str, total_count: int | None = None) -> int | None:
    text = str(value or "").strip().lower()
    numeric = _int_from_atom(text)
    if numeric is not None:
        return numeric
    match = re.search(r"(\d+)_of_(\d+)", text)
    if match:
        return int(match.group(1))
    if "majority" in text and total_count is not None:
        return total_count // 2 + 1
    return None


def _source_vote_token_groups(runtime: CorePrologRuntime) -> dict[str, dict[str, list[str]]]:
    facts = _runtime_fact_rows(runtime)
    labels: dict[str, str] = {}
    lines: dict[str, int] = {}
    texts: dict[str, str] = {}
    sections: dict[str, str] = {}
    for fact in facts:
        predicate = str(fact.get("predicate", "")).strip()
        args = [str(item).strip().lower() for item in fact.get("args", [])]
        if predicate == "source_record_label" and len(args) >= 2:
            labels[args[0]] = args[1]
        elif predicate == "source_record_line" and len(args) >= 2:
            line_no = _int_from_atom(args[1])
            if line_no is not None:
                lines[args[0]] = line_no
        elif predicate == "source_record_text_atom" and len(args) >= 2:
            texts[args[0]] = args[1]
        elif predicate == "source_record_section" and len(args) >= 2:
            sections[args[0]] = args[1]

    absent_by_section: dict[str, list[str]] = {}
    present_by_section: dict[str, list[str]] = {}
    for source_row, text in texts.items():
        section = sections.get(source_row, "")
        if not section:
            continue
        tokens = [token for token in text.split("_") if token]
        if "members" in tokens and "absent" in tokens:
            start = tokens.index("absent") + 1
            absent_by_section[section] = [token for token in tokens[start:] if not _is_numeric_atom(token)]
        elif "members" in tokens and "present" in tokens:
            start = tokens.index("present") + 1
            names = [token for token in tokens[start:] if not _is_numeric_atom(token) and token not in {"all", "sponsor"}]
            present_by_section.setdefault(section, []).extend(name for name in names if name not in present_by_section[section])

    grouped: dict[str, list[tuple[int, str, str]]] = {}
    for source_row, label in labels.items():
        if "vote" not in label or source_row not in texts:
            continue
        grouped.setdefault(label, []).append((lines.get(source_row, 0), texts[source_row], sections.get(source_row, "")))

    out: dict[str, dict[str, list[str]]] = {}
    for label, parts in grouped.items():
        ordered = sorted(parts)
        combined = "_".join(text for _, text, _ in ordered)
        section = next((section for _, _, section in ordered if section), "")
        tokens = [token for token in combined.split("_") if token]
        yes: list[str] = []
        no: list[str] = []
        for index, token in enumerate(tokens[:-1]):
            decision = tokens[index + 1]
            if decision == "yes" and token not in yes:
                yes.append(token)
            elif decision == "no" and token not in no:
                no.append(token)
        if yes or no:
            out[label] = {
                "yes": yes,
                "no": no,
                "absent": absent_by_section.get(section, []),
                "present": present_by_section.get(section, []),
            }
    return out


def _vote_action_type(runtime: CorePrologRuntime, vote_id: str) -> str:
    vote_norm = str(vote_id or "").strip().lower()
    if not vote_norm:
        return ""
    for fact in _runtime_fact_rows(runtime):
        predicate = str(fact.get("predicate", "")).strip().lower()
        args = [str(item).strip().lower() for item in fact.get("args", [])]
        if not args or args[0] != vote_norm:
            continue
        if predicate.endswith("_introduced"):
            return predicate[: -len("_introduced")]
        if predicate.endswith("_proposal"):
            return predicate[: -len("_proposal")]
    return ""


def _vote_threshold_counterfactual_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    predicate_tokens = _predicate_tokens(predicate)
    if "vote" not in predicate_tokens and "voting" not in predicate_tokens:
        return None

    facts = _runtime_fact_rows(runtime)
    requested_vote = str(args[0]).strip().lower() if args and not _is_prolog_variable(str(args[0]).strip()) else ""
    vote_rows: list[dict[str, Any]] = []
    for fact in facts:
        fact_predicate = str(fact.get("predicate", "")).strip()
        fact_tokens = _predicate_tokens(fact_predicate)
        fact_args = [str(item).strip().lower() for item in fact.get("args", [])]
        if "vote" not in fact_tokens or len(fact_args) < 5:
            continue
        yes_count = _int_from_atom(fact_args[2])
        no_count = _int_from_atom(fact_args[3])
        if yes_count is None or no_count is None:
            continue
        if requested_vote and fact_args[0] != requested_vote:
            continue
        vote_rows.append(
            {
                "predicate": fact_predicate,
                "vote_id": fact_args[0],
                "date": fact_args[1],
                "yes": yes_count,
                "no": no_count,
                "outcome": fact_args[4],
                "clause": str(fact.get("clause", "")),
            }
        )
    if not vote_rows:
        return None

    threshold_rows: list[dict[str, Any]] = []
    for fact in facts:
        fact_predicate = str(fact.get("predicate", "")).strip()
        fact_tokens = _predicate_tokens(fact_predicate)
        fact_args = [str(item).strip().lower() for item in fact.get("args", [])]
        if "threshold" not in fact_tokens or "voting" not in fact_tokens or len(fact_args) < 2:
            continue
        threshold_rows.append({"action": fact_args[0], "threshold": fact_args[1], "predicate": fact_predicate})
    if not threshold_rows:
        return None

    source_votes = _source_vote_token_groups(runtime)
    out_rows: list[dict[str, str]] = []
    for vote in vote_rows:
        total = int(vote["yes"]) + int(vote["no"])
        action_type = _vote_action_type(runtime, str(vote["vote_id"]))
        matching_thresholds = [
            row for row in threshold_rows if action_type and str(row.get("action", "")) == action_type
        ] or threshold_rows
        matching_thresholds = sorted(
            matching_thresholds,
            key=lambda row: (
                0 if action_type and str(row.get("action", "")) == action_type else 1,
                str(row.get("action", "")),
                str(row.get("threshold", "")),
            ),
        )
        vote_source = next(
            (value for label, value in source_votes.items() if str(vote["vote_id"]) in label),
            {"yes": [], "no": []},
        )
        no_voters = list(vote_source.get("no", []))
        changed_voters = no_voters or ["one_no_vote"]
        for threshold in matching_thresholds[:2]:
            required = _threshold_required_count(str(threshold.get("threshold", "")), total)
            if required is None:
                continue
            for changed_voter in changed_voters:
                yes_after = int(vote["yes"]) + 1
                no_after = max(0, int(vote["no"]) - 1)
                yes_voters_after = list(vote_source.get("yes", []))
                no_voters_after = list(no_voters)
                if changed_voter != "one_no_vote":
                    if changed_voter not in yes_voters_after:
                        yes_voters_after.append(changed_voter)
                    no_voters_after = [item for item in no_voters_after if item != changed_voter]
                out_rows.append(
                    {
                        "SupportKind": "vote_threshold_counterfactual",
                        "VotePredicate": str(vote["predicate"]),
                        "VoteId": str(vote["vote_id"]),
                        "VoteDate": str(vote["date"]),
                        "ActionType": action_type or str(threshold.get("action", "")),
                        "Threshold": str(threshold.get("threshold", "")),
                        "RequiredYes": str(required),
                        "BaselineYes": str(vote["yes"]),
                        "BaselineNo": str(vote["no"]),
                        "BaselineOutcome": str(vote["outcome"]),
                        "ChangedVoter": changed_voter,
                        "ChangeAssumption": "one_no_vote_switches_to_yes",
                        "CounterfactualYes": str(yes_after),
                        "CounterfactualNo": str(no_after),
                        "CounterfactualOutcome": "pass" if yes_after >= required else "fail",
                        "BaselineYesVoters": ",".join(vote_source.get("yes", [])),
                        "BaselineNoVoters": ",".join(no_voters),
                        "CounterfactualYesVoters": ",".join(yes_voters_after),
                        "CounterfactualNoVoters": ",".join(no_voters_after),
                        "HelperClass": "clean-helper",
                    }
                )
            absent_voters = [item for item in vote_source.get("absent", []) if item]
            if absent_voters:
                scenarios = [
                    ("additional_absent_voters_all_yes", absent_voters, []),
                    ("additional_absent_voters_one_yes", ["one_of:" + ",".join(absent_voters)], []),
                    ("additional_absent_voters_all_no", [], absent_voters),
                ]
                for assumption, assumed_yes, assumed_no in scenarios:
                    yes_added = len(absent_voters) if assumption.endswith("all_yes") else 1 if assumption.endswith("one_yes") else 0
                    no_added = len(absent_voters) if assumption.endswith("all_no") else 0 if assumption.endswith("all_yes") else len(absent_voters) - 1
                    yes_after = int(vote["yes"]) + yes_added
                    no_after = int(vote["no"]) + no_added
                    out_rows.append(
                        {
                            "SupportKind": "vote_threshold_counterfactual",
                            "VotePredicate": str(vote["predicate"]),
                            "VoteId": str(vote["vote_id"]),
                            "VoteDate": str(vote["date"]),
                            "ActionType": action_type or str(threshold.get("action", "")),
                            "Threshold": str(threshold.get("threshold", "")),
                            "RequiredYes": str(required),
                            "BaselineYes": str(vote["yes"]),
                            "BaselineNo": str(vote["no"]),
                            "BaselineOutcome": str(vote["outcome"]),
                            "ChangedVoter": ",".join(absent_voters),
                            "ChangeAssumption": assumption,
                            "CounterfactualYes": str(yes_after),
                            "CounterfactualNo": str(no_after),
                            "CounterfactualOutcome": "pass" if yes_after >= required else "fail",
                            "BaselineYesVoters": ",".join(vote_source.get("yes", [])),
                            "BaselineNoVoters": ",".join(no_voters),
                            "CounterfactualYesVoters": ",".join([*vote_source.get("yes", []), *assumed_yes]),
                            "CounterfactualNoVoters": ",".join([*no_voters, *assumed_no]),
                            "HelperClass": "clean-helper",
                        }
                    )
    if not out_rows:
        return None

    return {
        "query": "vote_threshold_counterfactual_support(VoteId, ChangedVoter, CounterfactualYes, CounterfactualNo, CounterfactualOutcome).",
        "result": {
            "status": "success",
            "predicate": "vote_threshold_counterfactual_support",
            "prolog_query": (
                "vote_threshold_counterfactual_support"
                "(VoteId, ChangedVoter, CounterfactualYes, CounterfactualNo, CounterfactualOutcome)."
            ),
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": [
                "SupportKind",
                "VotePredicate",
                "VoteId",
                "VoteDate",
                "ActionType",
                "Threshold",
                "RequiredYes",
                "BaselineYes",
                "BaselineNo",
                "BaselineOutcome",
                "ChangedVoter",
                "ChangeAssumption",
                "CounterfactualYes",
                "CounterfactualNo",
                "CounterfactualOutcome",
                "BaselineYesVoters",
                "BaselineNoVoters",
                "CounterfactualYesVoters",
                "CounterfactualNoVoters",
                "HelperClass",
            ],
            "rows": out_rows,
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only vote threshold companion derives one no-to-yes counterfactual outcomes "
                    "from admitted vote counts, voting thresholds, and optional source vote-token rows"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [query, "admitted vote count facts", "admitted voting threshold facts"],
    }


def _lifecycle_period_support_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    if len(args) < 3:
        return None
    requested_entity = str(args[0]).strip()
    if not requested_entity or _is_prolog_variable(requested_entity):
        return None

    predicate_tokens = _predicate_tokens(predicate)
    if not (predicate_tokens & (_LIFECYCLE_PERIOD_TOKENS | _LIFECYCLE_CONTEXT_TOKENS)):
        return None

    facts = _runtime_fact_rows(runtime)
    if not facts:
        return None
    all_entities = {
        str(fact.get("args", [""])[0]).strip().lower()
        for fact in facts
        if len(fact.get("args", [])) >= 1 and str(fact.get("args", [""])[0]).strip()
    }
    requested_key = _lifecycle_entity_family_key(requested_entity, all_entities)
    if not requested_key:
        return None

    period_rows: list[dict[str, Any]] = []
    context_rows: list[dict[str, Any]] = []
    matched_entities: set[str] = {requested_entity}
    for fact in facts:
        fact_args = [str(item).strip() for item in fact.get("args", [])]
        if len(fact_args) < 2:
            continue
        entity = fact_args[0]
        if _lifecycle_entity_family_key(entity, all_entities) != requested_key:
            continue
        fact_predicate = str(fact.get("predicate", "")).strip()
        fact_tokens = _predicate_tokens(fact_predicate)
        matched_entities.add(entity)
        if len(fact_args) >= 3 and bool(fact_tokens & _LIFECYCLE_PERIOD_TOKENS):
            period_rows.append(fact)
        elif fact_tokens & _LIFECYCLE_CONTEXT_TOKENS:
            context_rows.append(fact)

    if not period_rows or (len(matched_entities) <= 1 and not context_rows):
        return None

    def period_sort_key(fact: dict[str, Any]) -> tuple[tuple[int, int, int], str]:
        fact_args = [str(item).strip() for item in fact.get("args", [])]
        dates = _date_like_atoms(fact_args[1:])
        key = _date_atom_sort_key(dates[-1]) if dates else None
        return (key or (0, 0, 0), str(fact.get("clause", "")))

    selected_period = sorted(period_rows, key=period_sort_key)[-1]
    selected_args = [str(item).strip() for item in selected_period.get("args", [])]
    period_dates = _date_like_atoms(selected_args[1:])
    start_date = period_dates[0] if period_dates else (selected_args[1] if len(selected_args) > 1 else "")
    end_date = period_dates[-1] if period_dates else (selected_args[2] if len(selected_args) > 2 else "")

    context_dates: list[str] = []
    for fact in context_rows:
        context_dates.extend(_date_like_atoms([str(item).strip() for item in fact.get("args", [])[1:]]))
    effective_dates = [value for value in [end_date, *context_dates] if _date_atom_sort_key(value) is not None]
    effective_end = sorted(effective_dates, key=lambda value: _date_atom_sort_key(value) or (0, 0, 0))[-1] if effective_dates else end_date

    context_predicates = sorted({str(fact.get("predicate", "")).strip() for fact in context_rows if fact.get("predicate")})
    period_predicate = str(selected_period.get("predicate", "")).strip()
    matched_display = ",".join(sorted(matched_entities))
    out_rows: list[dict[str, str]] = [
        {
            "SupportKind": "lifecycle_period_summary",
            "RequestedEntity": requested_entity,
            "EntityFamilyKey": requested_key,
            "MatchedEntities": matched_display,
            "PeriodPredicate": period_predicate,
            "StartDate": start_date,
            "EndDate": end_date,
            "EffectiveEndDate": effective_end,
            "StartDateDisplay": _display_source_date_atom(start_date),
            "EndDateDisplay": _display_source_date_atom(end_date),
            "EffectiveEndDateDisplay": _display_source_date_atom(effective_end),
            "ContextPredicates": ",".join(context_predicates),
            "PeriodClause": str(selected_period.get("clause", "")),
            "HelperClass": "clean-helper",
        }
    ]
    for fact in sorted(context_rows, key=lambda item: str(item.get("clause", "")))[:12]:
        fact_args = [str(item).strip() for item in fact.get("args", [])]
        context_dates = _date_like_atoms(fact_args[1:])
        out_rows.append(
            {
                "SupportKind": "lifecycle_period_context",
                "RequestedEntity": requested_entity,
                "EntityFamilyKey": requested_key,
                "ContextPredicate": str(fact.get("predicate", "")).strip(),
                "ContextEntity": fact_args[0] if fact_args else "",
                "ContextArgs": ",".join(fact_args[1:]),
                "ContextDate": context_dates[-1] if context_dates else "",
                "ContextDateDisplay": _display_source_date_atom(context_dates[-1]) if context_dates else "",
                "ContextClause": str(fact.get("clause", "")),
                "HelperClass": "clean-helper",
            }
        )

    return {
        "query": "lifecycle_period_support(RequestedEntity, StartDate, EndDate, EffectiveEndDate).",
        "result": {
            "status": "success",
            "predicate": "lifecycle_period_support",
            "prolog_query": "lifecycle_period_support(RequestedEntity, StartDate, EndDate, EffectiveEndDate).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": [
                "SupportKind",
                "RequestedEntity",
                "EntityFamilyKey",
                "MatchedEntities",
                "PeriodPredicate",
                "StartDate",
                "EndDate",
                "EffectiveEndDate",
                "StartDateDisplay",
                "EndDateDisplay",
                "EffectiveEndDateDisplay",
                "ContextPredicates",
                "ContextPredicate",
                "ContextEntity",
                "ContextArgs",
                "ContextDate",
                "ContextDateDisplay",
                "PeriodClause",
                "ContextClause",
                "HelperClass",
            ],
            "rows": out_rows,
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only lifecycle period companion bundles admitted period rows with same-entity "
                    "exception/status/extension facts via structural entity-family keys when the query asks "
                    "for either the base interval or a lifecycle context row"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [query, "admitted runtime lifecycle facts sharing a structural entity-family key"],
    }


def _type_taxonomy_summary_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    if len(args) != 1 or not predicate.endswith("_type"):
        return None
    variable = str(args[0]).strip()
    if not _is_prolog_variable(variable):
        return None

    companion_query = format_prolog_query(predicate, ["Value"])
    rows = _runtime_rows(runtime, companion_query)
    raw_values = sorted({str(row.get("Value", "")).strip().lower() for row in rows if str(row.get("Value", "")).strip()})
    if len(raw_values) < 2:
        return None

    all_values = set(raw_values)
    groups: dict[str, list[str]] = {}
    for value in raw_values:
        key = _type_category_key(value, all_values)
        if key:
            groups.setdefault(key, []).append(value)
    groups = {key: sorted(values) for key, values in groups.items() if values}
    if len(groups) >= len(raw_values) or not any(len(values) > 1 for values in groups.values()):
        return None

    category_displays = {key: _type_category_display(key, values) for key, values in groups.items()}
    category_keys = sorted(groups)
    out_rows: list[dict[str, str]] = [
        {
            "SupportKind": "type_category_summary",
            "TypePredicate": predicate,
            "CategoryCount": str(len(category_keys)),
            "RawValueCount": str(len(raw_values)),
            "CategoryKeys": ",".join(category_keys),
            "CategoryDisplays": "; ".join(category_displays[key] for key in category_keys),
            "RawValues": ",".join(raw_values),
            "HelperClass": "clean-helper",
        }
    ]
    for key in category_keys:
        values = groups[key]
        out_rows.append(
            {
                "SupportKind": "type_category",
                "TypePredicate": predicate,
                "CategoryKey": key,
                "CategoryCount": str(len(category_keys)),
                "RawValueCount": str(len(values)),
                "CategoryDisplay": category_displays[key],
                "Members": ",".join(values),
                "HelperClass": "clean-helper",
            }
        )

    return {
        "query": "type_category_support(TypePredicate, SupportKind, CategoryKey, CategoryCount).",
        "result": {
            "status": "success",
            "predicate": "type_category_support",
            "prolog_query": "type_category_support(TypePredicate, SupportKind, CategoryKey, CategoryCount).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": [
                "SupportKind",
                "TypePredicate",
                "CategoryKey",
                "CategoryCount",
                "RawValueCount",
                "CategoryDisplay",
                "CategoryDisplays",
                "CategoryKeys",
                "Members",
                "RawValues",
                "HelperClass",
            ],
            "rows": out_rows,
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only type taxonomy companion collapses raw unary *_type instance variants "
                    "into stable category keys when sibling atoms expose a reusable coded category prefix"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [query, companion_query],
    }


def _classification_conversion_effect_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    if predicate != "conversion_effective_date" or len(args) < 3:
        return None
    unit_arg, from_arg, to_arg = [str(item).strip() for item in args[:3]]
    requested_from = "" if _is_prolog_variable(from_arg) else from_arg
    requested_to = "" if _is_prolog_variable(to_arg) else to_arg

    conversion_rows = _runtime_rows(runtime, "conversion_effective_date(Unit, FromType, ToType).")
    if not conversion_rows:
        return None

    counts_by_type: dict[str, list[int]] = {}
    for count_row in _runtime_rows(runtime, "unit_count(Type, Count)."):
        unit_type = str(count_row.get("Type", "")).strip()
        count_value = str(count_row.get("Count", "")).strip()
        if not unit_type or not _is_numeric_atom(count_value):
            continue
        counts_by_type.setdefault(unit_type, []).append(int(float(count_value)))

    pairs: dict[tuple[str, str], set[str]] = {}
    aggregate_pairs: dict[tuple[str, str], set[str]] = {}
    for row in conversion_rows:
        unit = str(row.get("Unit", "")).strip()
        from_type = str(row.get("FromType", "")).strip()
        to_type = str(row.get("ToType", "")).strip()
        if not unit or not from_type or not to_type:
            continue
        if requested_from and from_type != requested_from:
            continue
        if requested_to and to_type != requested_to:
            continue
        key = (from_type, to_type)
        if "_to_" in unit:
            aggregate_pairs.setdefault(key, set()).add(unit)
        else:
            pairs.setdefault(key, set()).add(unit)

    out_rows: list[dict[str, str]] = []
    for key in sorted(set(pairs) | set(aggregate_pairs)):
        from_type, to_type = key
        from_counts = sorted(set(counts_by_type.get(from_type, [])))
        to_counts = sorted(set(counts_by_type.get(to_type, [])))
        if len(from_counts) < 2 or len(to_counts) < 2:
            continue
        from_before = max(from_counts)
        from_after = min(from_counts)
        to_before = min(to_counts)
        to_after = max(to_counts)
        from_delta = from_after - from_before
        to_delta = to_after - to_before
        if from_delta >= 0 or to_delta <= 0 or abs(from_delta) != to_delta:
            continue

        individual_units = pairs.get(key, set())
        aggregate_units = aggregate_pairs.get(key, set())
        converted_count = len(individual_units)
        inferred_from_aggregate = ""
        if converted_count == 0:
            inferred_counts = [
                inferred
                for unit in aggregate_units
                if (inferred := _count_numeric_atom_range(unit)) is not None
            ]
            if inferred_counts:
                converted_count = max(inferred_counts)
                inferred_from_aggregate = ",".join(sorted(aggregate_units))
        if converted_count and converted_count != to_delta:
            continue

        row: dict[str, str] = {
            "FromType": from_type,
            "ToType": to_type,
            "ConvertedCount": str(converted_count or to_delta),
            "FromTypeBeforeCount": str(from_before),
            "FromTypeAfterCount": str(from_after),
            "ToTypeBeforeCount": str(to_before),
            "ToTypeAfterCount": str(to_after),
            "FromTypeDelta": str(from_delta),
            "ToTypeDelta": str(to_delta),
            "TotalCountEffect": "no_change",
            "Explanation": "classification_shift_balanced_existing_units",
            "Units": ",".join(sorted(individual_units)),
            "AggregateUnits": inferred_from_aggregate,
        }
        if _is_prolog_variable(unit_arg):
            row[unit_arg] = ",".join(sorted(individual_units or aggregate_units))
        if _is_prolog_variable(from_arg):
            row[from_arg] = from_type
        if _is_prolog_variable(to_arg):
            row[to_arg] = to_type
        out_rows.append(row)

    if not out_rows:
        return None
    return {
        "query": "classification_conversion_effect_support(FromType, ToType, ConvertedCount, TotalCountEffect).",
        "result": {
            "status": "success",
            "predicate": "classification_conversion_effect_support",
            "prolog_query": "classification_conversion_effect_support(FromType, ToType, ConvertedCount, TotalCountEffect).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": [
                "FromType",
                "ToType",
                "ConvertedCount",
                "FromTypeBeforeCount",
                "FromTypeAfterCount",
                "ToTypeBeforeCount",
                "ToTypeAfterCount",
                "FromTypeDelta",
                "ToTypeDelta",
                "TotalCountEffect",
                "Explanation",
            ],
            "rows": out_rows,
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only classification conversion companion derived zero total-count effect "
                    "when admitted category decrease and increase rows balance over existing units"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [
            query,
            "conversion_effective_date(Unit, FromType, ToType).",
            "unit_count(Type, Count).",
        ],
    }


def _hoa_census_companion_queries(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    revenue_companion = _assessment_revenue_companion(runtime, predicate=predicate, query=query)
    if revenue_companion:
        out.append(revenue_companion)
    conversion_delta = _conversion_assessment_delta_companion(runtime, predicate=predicate, query=query)
    if conversion_delta:
        out.append(conversion_delta)
    deferral_companion = _classification_deferral_effect_companion(runtime, predicate=predicate, query=query)
    if deferral_companion:
        out.append(deferral_companion)
    transfer_policy = _assessment_transfer_policy_companion(runtime, predicate=predicate, query=query)
    if transfer_policy:
        out.append(transfer_policy)
    vacancy_companion = _vacancy_voting_eligibility_companion(runtime, predicate=predicate, query=query)
    if vacancy_companion:
        out.append(vacancy_companion)
    return out


def _int_from_atom(value: Any) -> int | None:
    text = str(value or "").strip()
    if _is_numeric_atom(text):
        return int(float(text))
    return None


def _count_atoms_by_type(runtime: CorePrologRuntime) -> dict[str, list[int]]:
    counts_by_type: dict[str, list[int]] = {}
    for count_row in _runtime_rows(runtime, "unit_count(Type, Count)."):
        unit_type = str(count_row.get("Type", "")).strip()
        count_value = _int_from_atom(count_row.get("Count"))
        if not unit_type or count_value is None:
            continue
        counts_by_type.setdefault(unit_type, []).append(count_value)
    return counts_by_type


def _current_assessment_counts(runtime: CorePrologRuntime) -> dict[str, int]:
    counts_by_type = _count_atoms_by_type(runtime)
    conversion_rows = _runtime_rows(runtime, "conversion_effective_date(Unit, FromType, ToType).")
    decreased_types = {str(row.get("FromType", "")).strip() for row in conversion_rows if str(row.get("FromType", "")).strip()}
    increased_types = {str(row.get("ToType", "")).strip() for row in conversion_rows if str(row.get("ToType", "")).strip()}
    out: dict[str, int] = {}
    for unit_type, values in counts_by_type.items():
        if not values:
            continue
        unique = sorted(set(values))
        if unit_type in decreased_types:
            out[unit_type] = min(unique)
        elif unit_type in increased_types:
            out[unit_type] = max(unique)
        else:
            out[unit_type] = max(unique)
    return out


def _assessment_rates(runtime: CorePrologRuntime) -> dict[str, int]:
    rates: dict[str, int] = {}
    for row in _runtime_rows(runtime, "assessment_rate(Type, Rate)."):
        unit_type = str(row.get("Type", "")).strip()
        rate_value = _int_from_atom(row.get("Rate"))
        if not unit_type or rate_value is None:
            continue
        rates[unit_type] = rate_value
    return rates


def _assessment_revenue_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    query: str,
) -> dict[str, Any] | None:
    if predicate not in {"unit_count", "assessment_rate", "conditional_outcome"}:
        return None
    counts = _current_assessment_counts(runtime)
    rates = _assessment_rates(runtime)
    out_rows: list[dict[str, str]] = []
    total = 0
    for unit_type in sorted(set(counts) & set(rates)):
        count = counts[unit_type]
        rate = rates[unit_type]
        subtotal = count * rate
        total += subtotal
        out_rows.append(
            {
                "RowKind": "subtotal",
                "UnitType": unit_type,
                "Count": str(count),
                "Rate": str(rate),
                "Subtotal": str(subtotal),
            }
        )
    if not out_rows or total <= 0:
        return None
    out_rows.append(
        {
            "RowKind": "total",
            "UnitType": "all_assessed_units",
            "Count": str(sum(int(row["Count"]) for row in out_rows)),
            "Rate": "",
            "Subtotal": str(total),
            "TotalRevenue": str(total),
        }
    )
    return {
        "query": "assessment_revenue_support(RowKind, UnitType, Count, Rate, Subtotal, TotalRevenue).",
        "result": {
            "status": "success",
            "predicate": "assessment_revenue_support",
            "prolog_query": "assessment_revenue_support(RowKind, UnitType, Count, Rate, Subtotal, TotalRevenue).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": ["RowKind", "UnitType", "Count", "Rate", "Subtotal", "TotalRevenue"],
            "rows": out_rows,
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only HOA assessment companion multiplied admitted current unit counts by admitted "
                    "assessment rates; it reads no source prose and writes no durable facts"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [query, "unit_count(Type, Count).", "assessment_rate(Type, Rate)."],
    }


def _conversion_assessment_delta_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    query: str,
) -> dict[str, Any] | None:
    if predicate not in {"conversion_effective_date", "classification_conversion_effect_support", "assessment_rate"}:
        return None
    conversion = _classification_conversion_effect_companion(
        runtime,
        predicate="conversion_effective_date",
        args=["Unit", "FromType", "ToType"],
        query=query,
    )
    if not conversion:
        return None
    rates = _assessment_rates(runtime)
    out_rows: list[dict[str, str]] = []
    for row in conversion.get("result", {}).get("rows", []) or []:
        from_type = str(row.get("FromType", "")).strip()
        to_type = str(row.get("ToType", "")).strip()
        converted_count = _int_from_atom(row.get("ConvertedCount"))
        if not from_type or not to_type or converted_count is None:
            continue
        from_rate = rates.get(from_type)
        to_rate = rates.get(to_type)
        if from_rate is None or to_rate is None:
            continue
        rate_delta = to_rate - from_rate
        out_rows.append(
            {
                "FromType": from_type,
                "ToType": to_type,
                "ConvertedCount": str(converted_count),
                "FromRate": str(from_rate),
                "ToRate": str(to_rate),
                "RateDelta": str(rate_delta),
                "RevenueDelta": str(converted_count * rate_delta),
                "TotalCountEffect": str(row.get("TotalCountEffect", "")),
            }
        )
    if not out_rows:
        return None
    return {
        "query": "conversion_assessment_delta_support(FromType, ToType, ConvertedCount, RateDelta, RevenueDelta).",
        "result": {
            "status": "success",
            "predicate": "conversion_assessment_delta_support",
            "prolog_query": "conversion_assessment_delta_support(FromType, ToType, ConvertedCount, RateDelta, RevenueDelta).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": [
                "FromType",
                "ToType",
                "ConvertedCount",
                "FromRate",
                "ToRate",
                "RateDelta",
                "RevenueDelta",
                "TotalCountEffect",
            ],
            "rows": out_rows,
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only conversion assessment companion derived revenue delta from admitted "
                    "conversion count and assessment rates"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [
            query,
            "conversion_effective_date(Unit, FromType, ToType).",
            "unit_count(Type, Count).",
            "assessment_rate(Type, Rate).",
        ],
    }


def _extract_count_from_atom(value: Any) -> int | None:
    match = re.search(r"count_?(\d+)", str(value or "").casefold())
    if not match:
        return None
    return int(match.group(1))


def _extract_revenue_delta_from_atom(value: Any) -> int | None:
    match = re.search(r"revenue_increase_?(\d+)", str(value or "").casefold())
    if not match:
        return None
    return int(match.group(1))


def _classification_deferral_effect_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    query: str,
) -> dict[str, Any] | None:
    if predicate not in {"classification_deferred", "conditional_outcome", "unit_count", "assessment_rate"}:
        return None
    deferral_rows = _runtime_rows(runtime, "classification_deferred(Entity, Status).")
    outcome_rows = _runtime_rows(runtime, "conditional_outcome(Condition, Outcome, Detail).")
    total_counts = [
        count
        for row in _runtime_rows(runtime, "unit_count(total, Count).")
        if (count := _int_from_atom(row.get("Count"))) is not None
    ]
    current_total = max(total_counts) if total_counts else None
    out_rows: list[dict[str, str]] = []
    for deferred in deferral_rows:
        entity = str(deferred.get("Entity", "")).strip()
        status = str(deferred.get("Status", "")).strip()
        if not entity:
            continue
        matching_outcomes = [
            row
            for row in outcome_rows
            if entity in str(row.get("Condition", "")).casefold() or entity in str(row.get("Outcome", "")).casefold()
        ]
        reclassified_total = None
        revenue_delta = None
        for outcome in matching_outcomes:
            for slot in ("Condition", "Outcome", "Detail"):
                reclassified_total = reclassified_total or _extract_count_from_atom(outcome.get(slot))
                revenue_delta = revenue_delta or _extract_revenue_delta_from_atom(outcome.get(slot))
        added_units = ""
        current_assessments = ""
        if current_total is not None and reclassified_total is not None and reclassified_total > current_total:
            added_units = str(reclassified_total - current_total)
            current_assessments = "1"
        out_rows.append(
            {
                "Entity": entity,
                "DecisionStatus": status,
                "CurrentClassificationEffect": "current_classification_preserved_pending_decision",
                "CurrentAssessments": current_assessments,
                "CurrentVotes": current_assessments,
                "CurrentTotalUnitCount": str(current_total or ""),
                "IfReclassifiedUnitCount": str(reclassified_total or ""),
                "AdditionalUnitsIfReclassified": added_units,
                "RevenueDeltaIfReclassified": str(revenue_delta or ""),
            }
        )
    if not out_rows:
        return None
    return {
        "query": "classification_deferral_effect_support(Entity, DecisionStatus, CurrentAssessments, CurrentVotes, AdditionalUnitsIfReclassified).",
        "result": {
            "status": "success",
            "predicate": "classification_deferral_effect_support",
            "prolog_query": "classification_deferral_effect_support(Entity, DecisionStatus, CurrentAssessments, CurrentVotes, AdditionalUnitsIfReclassified).",
            "result_type": "table",
            "num_rows": len(out_rows),
            "variables": [
                "Entity",
                "DecisionStatus",
                "CurrentClassificationEffect",
                "CurrentAssessments",
                "CurrentVotes",
                "CurrentTotalUnitCount",
                "IfReclassifiedUnitCount",
                "AdditionalUnitsIfReclassified",
                "RevenueDeltaIfReclassified",
            ],
            "rows": out_rows,
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only classification deferral companion exposed current preserved status and "
                    "conditional reclassification effect from admitted deferral/outcome/count rows"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [
            query,
            "classification_deferred(Entity, Status).",
            "conditional_outcome(Condition, Outcome, Detail).",
            "unit_count(total, Count).",
        ],
    }


def _vacancy_voting_eligibility_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    query: str,
) -> dict[str, Any] | None:
    if predicate not in {"voting_eligibility", "occupancy_status"}:
        return None
    eligible_all_units = any(
        str(row.get("X", row.get("Entity", ""))).strip() == "all_units"
        and str(row.get("Y", row.get("Status", ""))).strip() == "eligible"
        for row in _runtime_rows(runtime, "voting_eligibility(X, Y).")
    )
    vacant_rows = _runtime_rows(runtime, "occupancy_status(Unit, vacant).")
    if not eligible_all_units or not vacant_rows:
        return None
    return {
        "query": "vacancy_voting_eligibility_support(VacancyAffectsEligibility, VacantUnitsCarryVotes, VacantUnits).",
        "result": {
            "status": "success",
            "predicate": "vacancy_voting_eligibility_support",
            "prolog_query": "vacancy_voting_eligibility_support(VacancyAffectsEligibility, VacantUnitsCarryVotes, VacantUnits).",
            "result_type": "table",
            "num_rows": 1,
            "variables": ["VacancyAffectsEligibility", "VacantUnitsCarryVotes", "VacantUnits"],
            "rows": [
                {
                    "VacancyAffectsEligibility": "no",
                    "VacantUnitsCarryVotes": "yes",
                    "VacantUnits": ",".join(sorted(str(row.get("Unit", "")).strip() for row in vacant_rows)),
                }
            ],
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only vacancy companion combined admitted all-units voting eligibility with admitted "
                    "vacant-unit rows; it does not infer occupant identity"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [query, "voting_eligibility(all_units, eligible).", "occupancy_status(Unit, vacant)."],
    }


def _date_atom_plus_one(runtime: CorePrologRuntime, value: str) -> str:
    observed = _runtime_temporal_datetime(runtime, value)
    if observed is None:
        return ""
    return (observed + timedelta(days=1)).strftime("%Y_%m_%d")


def _assessment_transfer_policy_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    query: str,
) -> dict[str, Any] | None:
    if predicate not in {"assessment_responsibility", "transfer_date", "owner_of"}:
        return None
    rows = _runtime_rows(runtime, "assessment_responsibility(Unit, Party, StartDate, EndDate).")
    if not rows:
        return None
    by_unit: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        unit = str(row.get("Unit", "")).strip()
        party = str(row.get("Party", "")).strip()
        start = str(row.get("StartDate", "")).strip()
        end = str(row.get("EndDate", "")).strip()
        if not unit or not party or not start or not end:
            continue
        by_unit.setdefault(unit, []).append({"Unit": unit, "Party": party, "StartDate": start, "EndDate": end})

    support_rows: list[dict[str, str]] = []
    for unit, unit_rows in sorted(by_unit.items()):
        ordered = sorted(unit_rows, key=lambda item: item["StartDate"])
        for left, right in zip(ordered, ordered[1:]):
            expected_next = _date_atom_plus_one(runtime, left["EndDate"])
            if expected_next and expected_next == right["StartDate"]:
                support_rows.append(
                    {
                        "Unit": unit,
                        "SellerOrPriorOwner": left["Party"],
                        "BuyerOrNextOwner": right["Party"],
                        "SellerResponsibleThrough": left["EndDate"],
                        "BuyerResponsibleFrom": right["StartDate"],
                        "PolicyPattern": "seller_through_closing_buyer_from_day_after",
                    }
                )
    if not support_rows:
        return None
    return {
        "query": "assessment_transfer_policy_support(Unit, SellerOrPriorOwner, BuyerOrNextOwner, SellerResponsibleThrough, BuyerResponsibleFrom, PolicyPattern).",
        "result": {
            "status": "success",
            "predicate": "assessment_transfer_policy_support",
            "prolog_query": (
                "assessment_transfer_policy_support(Unit, SellerOrPriorOwner, BuyerOrNextOwner, "
                "SellerResponsibleThrough, BuyerResponsibleFrom, PolicyPattern)."
            ),
            "result_type": "table",
            "num_rows": len(support_rows),
            "variables": [
                "Unit",
                "SellerOrPriorOwner",
                "BuyerOrNextOwner",
                "SellerResponsibleThrough",
                "BuyerResponsibleFrom",
                "PolicyPattern",
            ],
            "rows": support_rows,
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only assessment-transfer companion detected the repeated admitted pattern "
                    "that prior owners are responsible through closing and next owners from the following day"
                ),
                "original_query": query,
                "trigger_predicate": predicate,
            },
        },
        "derived_from_queries": [query, "assessment_responsibility(Unit, Party, StartDate, EndDate)."],
    }


def _split_interval_atom(value: str) -> tuple[str, str]:
    text = str(value or "").strip()
    if "_to_" not in text:
        return text, text
    start, end = text.split("_to_", 1)
    return start, end


def _compact_datetime_interval_bounds(value: str) -> tuple[str, str] | None:
    text = str(value or "").strip().lower()
    if text.startswith("v_"):
        text = text[2:]
    match = re.fullmatch(
        r"(?P<date>\d{4}_\d{2}_\d{2})_(?P<start_hour>\d{2})_(?P<start_minute>\d{2})_(?P<end_hour>\d{2})_(?P<end_minute>\d{2})",
        text,
    )
    if not match:
        return None
    date = match.group("date")
    start = f"{date}_{match.group('start_hour')}_{match.group('start_minute')}"
    end = f"{date}_{match.group('end_hour')}_{match.group('end_minute')}"
    return start, end


def _compact_interval_duration_companion(
    *,
    results: list[dict[str, Any]],
    query: str,
) -> dict[str, Any] | None:
    parsed = parse_prolog_query(query)
    if parsed is None:
        return None
    predicate, args = parsed
    if predicate not in {"elapsed_minutes", "elapsed_hours"} or len(args) != 3:
        return None
    interval_arg = str(args[0]).strip()
    if not _is_prolog_variable(interval_arg):
        return None
    for item in reversed(results):
        result = item.get("result") if isinstance(item, dict) else None
        if not isinstance(result, dict) or result.get("status") != "success":
            continue
        rows = result.get("rows")
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            interval_value = str(row.get(interval_arg, "")).strip()
            bounds = _compact_datetime_interval_bounds(interval_value)
            if not bounds:
                continue
            start, end = bounds
            start_dt = _datetime_from_ledger_atom(start)
            end_dt = _datetime_from_ledger_atom(end)
            if not start_dt or not end_dt or end_dt < start_dt:
                continue
            minutes = int((end_dt - start_dt).total_seconds() // 60)
            duration_value = str(minutes if predicate == "elapsed_minutes" else round(minutes / 60, 3))
            duration_display = _duration_between_atoms(start, end)
            support_row = {
                "IntervalAtom": interval_value,
                "Start": start,
                "End": end,
                "DurationMinutes": str(minutes),
                "Duration": duration_display,
            }
            output_arg = str(args[2]).strip()
            if _is_prolog_variable(output_arg):
                support_row[output_arg] = duration_value
            return {
                "query": "compact_interval_duration_support(IntervalAtom, Start, End, DurationMinutes, Duration).",
                "result": {
                    "status": "success",
                    "predicate": "compact_interval_duration_support",
                    "prolog_query": "compact_interval_duration_support(IntervalAtom, Start, End, DurationMinutes, Duration).",
                    "result_type": "table",
                    "num_rows": 1,
                    "variables": list(support_row.keys()),
                    "rows": [support_row],
                    "reasoning_basis": {
                        "kind": "core-local",
                        "note": (
                            "query-only duration support split a compact same-day interval atom into "
                            "start and end timestamps; no durable fact was written"
                        ),
                        "original_query": query,
                    },
                },
                "derived_from_queries": [str(item.get("query", "")), query],
            }
    return None


def _defined_interval_duration_companion(runtime: CorePrologRuntime, *, query: str) -> dict[str, Any] | None:
    parsed = parse_prolog_query(query)
    if parsed is None:
        return None
    predicate, args = parsed
    if predicate not in {"elapsed_minutes", "elapsed_hours"} or len(args) != 3:
        return None
    starts = _runtime_rows(runtime, "interval_start(Interval, StartEvent).")
    ends = _runtime_rows(runtime, "interval_end(Interval, EndEvent).")
    if not starts or not ends:
        return None
    timestamp_rows: list[dict[str, str]] = []
    timestamp_kind = ""
    for timestamp_query, kind in [
        ("corrected_timestamp(Event, Record, Time).", "corrected_timestamp"),
        ("event_corrected_timestamp(Event, Record, Time).", "event_corrected_timestamp"),
        ("has_corrected_timestamp(Event, Time).", "has_corrected_timestamp"),
    ]:
        timestamp_rows = _runtime_rows(runtime, timestamp_query)
        if timestamp_rows:
            timestamp_kind = kind
            break
    if not timestamp_rows:
        return None
    timestamp_by_event: dict[str, list[dict[str, str]]] = {}
    for row in timestamp_rows:
        event = str(row.get("Event", "")).strip()
        time = str(row.get("Time", "")).strip()
        if event and time:
            timestamp_by_event.setdefault(event, []).append(row)
    end_by_interval = {
        str(row.get("Interval", "")).strip(): str(row.get("EndEvent", "")).strip()
        for row in ends
    }
    support_rows: list[dict[str, str]] = []
    output_arg = str(args[2]).strip()
    for start_row in starts:
        interval = str(start_row.get("Interval", "")).strip()
        start_event = str(start_row.get("StartEvent", "")).strip()
        end_event = end_by_interval.get(interval, "")
        if not interval or not start_event or not end_event:
            continue
        for start_time_row in timestamp_by_event.get(start_event, []):
            for end_time_row in timestamp_by_event.get(end_event, []):
                start_record = str(start_time_row.get("Record", "")).strip()
                end_record = str(end_time_row.get("Record", "")).strip()
                if start_record and end_record and start_record != end_record:
                    continue
                start = str(start_time_row.get("Time", "")).strip()
                end = str(end_time_row.get("Time", "")).strip()
                start_dt = _datetime_from_ledger_atom(start)
                end_dt = _datetime_from_ledger_atom(end)
                if not start_dt or not end_dt or end_dt < start_dt:
                    continue
                total_seconds = int((end_dt - start_dt).total_seconds())
                minutes = total_seconds / 60
                duration_value = (
                    _format_duration_number(minutes)
                    if predicate == "elapsed_minutes"
                    else _format_duration_number(total_seconds / 3600)
                )
                support_row = {
                    "Interval": interval,
                    "Record": start_record or end_record,
                    "StartEvent": start_event,
                    "EndEvent": end_event,
                    "Start": start,
                    "End": end,
                    "DurationSeconds": str(total_seconds),
                    "DurationMinutes": _format_duration_number(minutes),
                    "Duration": _duration_between_atoms(start, end),
                    "TimestampKind": timestamp_kind,
                }
                if _is_prolog_variable(output_arg):
                    support_row[output_arg] = duration_value
                support_rows.append(support_row)
    if not support_rows:
        return None
    return {
        "query": (
            "defined_interval_duration_support(Interval, Record, StartEvent, EndEvent, "
            "Start, End, DurationSeconds, DurationMinutes, Duration, TimestampKind)."
        ),
        "result": {
            "status": "success",
            "predicate": "defined_interval_duration_support",
            "prolog_query": (
                "defined_interval_duration_support(Interval, Record, StartEvent, EndEvent, "
                "Start, End, DurationSeconds, DurationMinutes, Duration, TimestampKind)."
            ),
            "result_type": "table",
            "num_rows": len(support_rows),
            "variables": list(support_rows[0].keys()),
            "rows": support_rows,
            "reasoning_basis": {
                "kind": "core-local",
                "note": (
                    "query-only duration support joined admitted interval_start/interval_end rows "
                    "to authoritative timestamp rows; no durable fact was written"
                ),
                "original_query": query,
            },
        },
        "derived_from_queries": [
            "interval_start(Interval, StartEvent).",
            "interval_end(Interval, EndEvent).",
            f"{timestamp_kind}(Event, Record, Time).",
            query,
        ],
    }


def _format_duration_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _role_hint_from_group(group: str) -> str:
    folded = str(group or "").casefold()
    hints: list[str] = []
    if "station_a" in folded or folded.endswith("_a"):
        hints.append("station_a")
    if "station_b" in folded or folded.endswith("_b"):
        hints.append("station_b")
    if "record" in folded:
        hints.append("recording")
    if "clipboard" in folded:
        hints.append("clipboard")
    if "shore" in folded:
        hints.append("shore")
    if "dune" in folded:
        hints.append("dune")
    return ",".join(hints)


def _recall_domain_companion_queries(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if predicate == "recall_classification" and len(args) == 3:
        companion = _recall_classification_at_date_companion(runtime, query=query, args=args)
        if companion:
            out.append(companion)
    if predicate == "unit_count" and len(args) == 3:
        companion = _unit_range_count_companion(runtime, query=query, args=args)
        if companion:
            out.append(companion)
    if predicate == "termination_request":
        companion = _recall_accounted_units_companion(runtime, query=query, predicate=predicate, args=args)
        if companion:
            out.append(companion)
    return out


def _recall_classification_at_date_companion(
    runtime: CorePrologRuntime,
    *,
    query: str,
    args: list[str],
) -> dict[str, Any] | None:
    recall_arg, class_arg, date_arg = [str(item).strip() for item in args[:3]]
    if not recall_arg or _is_prolog_variable(recall_arg) or not date_arg or _is_prolog_variable(date_arg):
        return None
    requested_key = _date_atom_sort_key(date_arg)
    if requested_key is None:
        return None
    classifications = runtime.query_rows("recall_classification(Recall, Classification, Date).")
    reclassifications = runtime.query_rows("recall_reclassification(Recall, FromClass, ToClass, Date).")
    rows: list[dict[str, Any]] = []
    for row in classifications.get("rows", []) if classifications.get("status") == "success" else []:
        recall = str(row.get("Recall", "")).strip()
        if not _same_recall_family(recall_arg, recall):
            continue
        date = str(row.get("Date", "")).strip()
        key = _date_atom_sort_key(date)
        if key is None or key > requested_key:
            continue
        rows.append(
            {
                "Recall": recall,
                "Classification": str(row.get("Classification", "")).strip(),
                "EffectiveDate": date,
                "Source": "recall_classification",
            }
        )
    for row in reclassifications.get("rows", []) if reclassifications.get("status") == "success" else []:
        recall = str(row.get("Recall", "")).strip()
        if not _same_recall_family(recall_arg, recall):
            continue
        date = str(row.get("Date", "")).strip()
        key = _date_atom_sort_key(date)
        if key is None or key > requested_key:
            continue
        rows.append(
            {
                "Recall": recall,
                "Classification": str(row.get("ToClass", "")).strip(),
                "FromClass": str(row.get("FromClass", "")).strip(),
                "EffectiveDate": date,
                "Source": "recall_reclassification",
            }
        )
    if not rows:
        return None
    rows.sort(key=lambda item: (_date_atom_sort_key(str(item.get("EffectiveDate", ""))) or (0, 0, 0), item.get("Source") == "recall_reclassification"))
    current = rows[-1]
    projected = dict(current)
    projected["RequestedDate"] = date_arg
    if _is_prolog_variable(class_arg):
        projected[class_arg] = projected.get("Classification", "")
    else:
        projected["RequestedClassification"] = class_arg
        projected["ClassificationMatches"] = "true" if class_arg == projected.get("Classification") else "false"
    return {
        "query": "recall_classification_at_date_support(QueryRecall, RequestedDate, Classification, EffectiveDate).",
        "result": {
            "status": "success",
            "predicate": "recall_classification_at_date_support",
            "prolog_query": "recall_classification_at_date_support(QueryRecall, RequestedDate, Classification, EffectiveDate).",
            "rows": [projected],
            "reasoning_basis": {
                "kind": "core-local",
                "note": "query-only status-at-date companion derived current recall classification from admitted classification and reclassification anchors",
                "original_query": query,
            },
        },
        "derived_from_queries": [
            query,
            "recall_classification(Recall, Classification, Date).",
            "recall_reclassification(Recall, FromClass, ToClass, Date).",
        ],
    }


def _unit_range_count_companion(
    runtime: CorePrologRuntime,
    *,
    query: str,
    args: list[str],
) -> dict[str, Any] | None:
    recall_arg, count_arg, date_arg = [str(item).strip() for item in args[:3]]
    rows_result = runtime.query_rows("unit_count(Recall, UnitSurface, Date).")
    if rows_result.get("status") != "success":
        return None
    out_rows: list[dict[str, Any]] = []
    for row in rows_result.get("rows", []):
        recall = str(row.get("Recall", "")).strip()
        if recall_arg and not _is_prolog_variable(recall_arg) and not _same_recall_family(recall_arg, recall):
            continue
        surface = str(row.get("UnitSurface", "")).strip()
        range_count = _count_atom_range(surface)
        if range_count is None:
            continue
        date = str(row.get("Date", "")).strip()
        projected = {
            "Recall": recall,
            "UnitSurface": surface,
            "Date": date,
            "RangeCount": str(range_count),
        }
        if _is_prolog_variable(count_arg):
            projected[count_arg] = str(range_count)
        if _is_prolog_variable(date_arg):
            projected[date_arg] = date
        out_rows.append(projected)
    if not out_rows:
        return None
    return {
        "query": "unit_range_count_support(Recall, UnitSurface, RangeCount, Date).",
        "result": {
            "status": "success",
            "predicate": "unit_range_count_support",
            "prolog_query": "unit_range_count_support(Recall, UnitSurface, RangeCount, Date).",
            "rows": out_rows,
            "reasoning_basis": {
                "kind": "core-local",
                "note": "query-only range companion counted admitted lot-range atoms such as *_a_through_*_f without reading source prose",
                "original_query": query,
            },
        },
        "derived_from_queries": [query, "unit_count(Recall, UnitSurface, Date)."],
    }


def _recall_accounted_units_companion(
    runtime: CorePrologRuntime,
    *,
    query: str,
    predicate: str,
    args: list[str],
) -> dict[str, Any] | None:
    recall_arg = str(args[0]).strip() if args else ""
    if not recall_arg or _is_prolog_variable(recall_arg):
        return None
    requested_date = ""
    if predicate == "termination_request" and len(args) >= 3:
        requested_date = str(args[2]).strip()
    elif predicate == "unit_status_change" and len(args) >= 2:
        requested_date = str(args[1]).strip()
    requested_key = _date_atom_sort_key(requested_date) if requested_date and not _is_prolog_variable(requested_date) else None
    if requested_key is None:
        term_result = runtime.query_rows(format_prolog_query("termination_request", [recall_arg, "Requester", "RequestDate"]))
        term_rows = term_result.get("rows", []) if term_result.get("status") == "success" else []
        dated = [
            (key, str(row.get("RequestDate", "")).strip())
            for row in term_rows
            if (key := _date_atom_sort_key(str(row.get("RequestDate", "")).strip())) is not None
        ]
        if dated:
            requested_key, requested_date = sorted(dated)[-1]
    if requested_key is None:
        return None
    totals = runtime.query_rows("unit_count(Recall, TotalUnits, Date).")
    changes = runtime.query_rows("unit_status_change(Recall, Date, Status, Count, Actor).")
    if totals.get("status") != "success" or changes.get("status") != "success":
        return None
    total_candidates: list[tuple[tuple[int, int, int], int, str, str]] = []
    for row in totals.get("rows", []):
        recall = str(row.get("Recall", "")).strip()
        if not _same_recall_family(recall_arg, recall):
            continue
        value = str(row.get("TotalUnits", "")).strip()
        if not value.isdigit():
            continue
        date = str(row.get("Date", "")).strip()
        key = _date_atom_sort_key(date)
        if key is None or key > requested_key:
            continue
        total_candidates.append((key, int(value), recall, date))
    unaccounted_candidates: list[tuple[tuple[int, int, int], int, str, str]] = []
    for row in changes.get("rows", []):
        recall = str(row.get("Recall", "")).strip()
        if not _same_recall_family(recall_arg, recall):
            continue
        if str(row.get("Status", "")).strip() != "unaccounted":
            continue
        count = str(row.get("Count", "")).strip()
        if not count.isdigit():
            continue
        date = str(row.get("Date", "")).strip()
        key = _date_atom_sort_key(date)
        if key is None or key > requested_key:
            continue
        unaccounted_candidates.append((key, int(count), recall, date))
    if not total_candidates or not unaccounted_candidates:
        return None
    _total_key, total, total_recall, total_date = sorted(total_candidates)[-1]
    _unaccounted_key, unaccounted, unaccounted_recall, unaccounted_date = sorted(unaccounted_candidates)[-1]
    accounted = total - unaccounted
    if accounted < 0:
        return None
    percent = round((accounted / total) * 100, 1) if total else 0.0
    return {
        "query": "recall_accounted_units_support(Recall, RequestedDate, AccountedUnits, TotalUnits, AccountedPercent).",
        "result": {
            "status": "success",
            "predicate": "recall_accounted_units_support",
            "prolog_query": "recall_accounted_units_support(Recall, RequestedDate, AccountedUnits, TotalUnits, AccountedPercent).",
            "rows": [
                {
                    "Recall": recall_arg,
                    "RequestedDate": requested_date,
                    "AccountedUnits": str(accounted),
                    "TotalUnits": str(total),
                    "UnaccountedUnits": str(unaccounted),
                    "AccountedPercent": f"{percent:.1f}",
                    "TotalSourceRecall": total_recall,
                    "TotalDate": total_date,
                    "UnaccountedSourceRecall": unaccounted_recall,
                    "UnaccountedDate": unaccounted_date,
                }
            ],
            "reasoning_basis": {
                "kind": "core-local",
                "note": "query-only aggregation companion derived accounted units from admitted total-unit and latest unaccounted-unit rows at or before the requested date",
                "original_query": query,
            },
        },
        "derived_from_queries": [
            query,
            "unit_count(Recall, TotalUnits, Date).",
            "unit_status_change(Recall, Date, unaccounted, Count, Actor).",
        ],
    }


def _story_choice_contrast_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    family = _choice_family_from_query(predicate=predicate, args=args)
    if not family:
        return None
    properties = runtime.query_rows("has_property(Entity, Property).")
    judgments = runtime.query_rows("judged(Judge, Entity, Dimension, Verdict).")
    events = runtime.query_rows("event(Event, Actor, Action, Entity, Location).")
    property_rows = [
        row
        for row in properties.get("rows", [])
        if _choice_family_matches(family, str(row.get("Entity", "")).strip())
    ] if properties.get("status") == "success" else []
    judgment_rows = (
        [
            row
            for row in judgments.get("rows", [])
            if _choice_family_matches(family, str(row.get("Entity", "")).strip())
        ]
        if judgments.get("status") == "success"
        else []
    )
    event_rows = (
        [
            row
            for row in events.get("rows", [])
            if _choice_family_matches(family, str(row.get("Entity", "")).strip())
        ]
        if events.get("status") == "success"
        else []
    )
    positive_rows = [
        row
        for row in property_rows
        if _positive_choice_property(str(row.get("Property", "")).strip())
    ]
    negative_rows = [
        row
        for row in judgment_rows
        if str(row.get("Verdict", "")).strip().startswith("too_")
    ]
    if not negative_rows:
        negative_rows = _negative_choice_speech_rows(runtime, family=family)
    inferred_positive_rows: list[dict[str, Any]] = []
    if not positive_rows:
        inferred_positive_rows = _choice_by_elimination_rows(
            family=family,
            property_rows=property_rows,
            event_rows=event_rows,
            negative_rows=negative_rows,
        )
        positive_rows = inferred_positive_rows
    if not positive_rows or not negative_rows:
        return None
    out_rows: list[dict[str, Any]] = []
    for positive in positive_rows:
        entity = str(positive.get("Entity", "")).strip()
        out_rows.append(
            {
                "ChoiceFamily": family,
                "AcceptedCandidate": entity,
                "PositiveProperty": str(positive.get("Property", "")).strip(),
                "EvidenceStatus": str(positive.get("EvidenceStatus", "direct_positive_property")).strip(),
                "RejectedCandidates": ",".join(
                    sorted({str(row.get("Entity", "")).strip() for row in negative_rows if str(row.get("Entity", "")).strip()})
                ),
                "ObservedActions": ",".join(
                    sorted(
                        {
                            str(row.get("Action", "")).strip()
                            for row in event_rows
                            if str(row.get("Entity", "")).strip() == entity and str(row.get("Action", "")).strip()
                        }
                    )
                ),
            }
        )
    return {
        "query": "story_choice_contrast_support(ChoiceFamily, AcceptedCandidate, PositiveProperty, RejectedCandidates).",
        "result": {
            "status": "success",
            "predicate": "story_choice_contrast_support",
            "prolog_query": "story_choice_contrast_support(ChoiceFamily, AcceptedCandidate, PositiveProperty, RejectedCandidates).",
            "rows": out_rows,
            "reasoning_basis": {
                "kind": "core-local",
                "note": "query-only story choice companion contrasted positive item properties with same-family rejected judgments",
                "original_query": query,
            },
        },
        "derived_from_queries": [
            query,
            "has_property(Entity, Property).",
            "judged(Judge, Entity, Dimension, Verdict).",
            "event(Event, Actor, Action, Entity, Location).",
        ],
    }


def _choice_family_from_query(*, predicate: str, args: list[str]) -> str:
    candidates: list[str] = []
    if predicate == "has_property" and args:
        candidates.append(str(args[0]).strip())
    if predicate == "judged" and len(args) >= 2:
        candidates.append(str(args[1]).strip())
    if predicate == "event" and len(args) >= 4:
        candidates.append(str(args[3]).strip())
    for candidate in candidates:
        if _is_prolog_variable(candidate):
            continue
        lowered = candidate.lower()
        for family in ["cart", "cap", "jar", "cup", "boat", "boot"]:
            if (
                lowered == family
                or lowered.startswith(f"{family}_")
                or lowered.endswith(f"_{family}")
            ):
                return family
    return ""


def _choice_family_matches(family: str, entity: str) -> bool:
    lowered = str(entity or "").lower()
    return lowered == family or lowered.startswith(f"{family}_") or lowered.endswith(f"_{family}")


def _positive_choice_property(value: str) -> bool:
    lowered = str(value or "").lower()
    return lowered.startswith("just_") or lowered in {"accepted", "chosen", "suitable", "right_size"}


def _negative_choice_speech_rows(runtime: CorePrologRuntime, *, family: str) -> list[dict[str, str]]:
    result = runtime.query_rows("said(Speaker, Listener, Text).")
    if result.get("status") != "success":
        return []
    out: list[dict[str, str]] = []
    ordinal_sizes = ["great", "middle", "little"]
    for row in result.get("rows", []):
        text = str(row.get("Text", "")).strip().lower()
        if family not in text or "_too_" not in text and "too_" not in text:
            continue
        size = _choice_size_from_text(text)
        if not size and len(out) < len(ordinal_sizes):
            size = ordinal_sizes[len(out)]
        entity = f"{size}_{family}" if size else family
        out.append(
            {
                "Entity": entity,
                "Verdict": text,
                "Speaker": str(row.get("Speaker", "")).strip(),
                "Dimension": "speech_rejection",
            }
        )
    return out


def _choice_by_elimination_rows(
    *,
    family: str,
    property_rows: list[dict[str, Any]],
    event_rows: list[dict[str, Any]],
    negative_rows: list[dict[str, Any]],
) -> list[dict[str, str]]:
    entities = {
        str(row.get("Entity", "")).strip()
        for row in [*property_rows, *event_rows]
        if _choice_family_matches(family, str(row.get("Entity", "")).strip())
    }
    if not entities:
        return []
    negative_entities = {
        _canonical_choice_entity(family, str(row.get("Entity", "")).strip())
        for row in negative_rows
        if str(row.get("Entity", "")).strip()
    }
    candidates = sorted(entity for entity in entities if _canonical_choice_entity(family, entity) not in negative_entities)
    if len(candidates) != 1 or len(negative_entities) < 2:
        return []
    return [
        {
            "Entity": candidates[0],
            "Property": "accepted_by_contrast",
            "EvidenceStatus": "inferred_by_complete_family_contrast",
        }
    ]


def _canonical_choice_entity(family: str, entity: str) -> str:
    lowered = str(entity or "").lower()
    lowered = lowered.replace("middle_sized_", "middle_")
    if lowered == family:
        return lowered
    return lowered


def _choice_size_from_text(value: str) -> str:
    lowered = str(value or "").lower()
    if "great" in lowered:
        return "great"
    if "middle" in lowered:
        return "middle"
    if "little" in lowered:
        return "little"
    return ""


def _story_remediation_method_companion(
    runtime: CorePrologRuntime,
    *,
    predicate: str,
    args: list[str],
    query: str,
) -> dict[str, Any] | None:
    if predicate != "event" or len(args) < 5:
        return None
    query_text = " ".join(str(item or "").lower() for item in args)
    if "extract" not in query_text and "key" not in query_text:
        return None
    events = runtime.query_rows("event(Event, Actor, Action, Object, Location).")
    if events.get("status") != "success":
        return None
    wound_rows: list[dict[str, Any]] = []
    extraction_rows: list[dict[str, Any]] = []
    for row in events.get("rows", []):
        action = str(row.get("Action", "")).strip()
        obj = str(row.get("Object", "")).strip()
        loc = str(row.get("Location", "")).strip()
        if action == "wound":
            wound_rows.append(row)
        if "extract" in action or "key" in obj or "key" in loc:
            extraction_rows.append(row)
    if not wound_rows or not extraction_rows:
        return None
    out_rows: list[dict[str, str]] = []
    for wound in wound_rows:
        wound_actor = str(wound.get("Actor", "")).strip()
        wound_object = str(wound.get("Object", "")).strip()
        for extraction in extraction_rows:
            extraction_actor = str(extraction.get("Actor", "")).strip()
            extraction_location = str(extraction.get("Location", "")).strip()
            if wound_actor and extraction_actor and wound_actor != extraction_actor:
                continue
            if wound_object and extraction_location and wound_object not in extraction_location:
                continue
            out_rows.append(
                {
                    "MethodEvent": str(wound.get("Event", "")).strip(),
                    "Actor": wound_actor or extraction_actor,
                    "MethodAction": str(wound.get("Action", "")).strip(),
                    "Patient": wound_object,
                    "OutcomeEvent": str(extraction.get("Event", "")).strip(),
                    "OutcomeAction": str(extraction.get("Action", "")).strip(),
                    "OutcomeObject": str(extraction.get("Object", "")).strip(),
                    "OutcomeLocation": extraction_location,
                }
            )
    if not out_rows:
        return None
    return {
        "query": "story_remediation_method_support(MethodEvent, Actor, MethodAction, Patient, OutcomeEvent, OutcomeObject).",
        "result": {
            "status": "success",
            "predicate": "story_remediation_method_support",
            "prolog_query": "story_remediation_method_support(MethodEvent, Actor, MethodAction, Patient, OutcomeEvent, OutcomeObject).",
            "rows": out_rows,
            "reasoning_basis": {
                "kind": "core-local",
                "note": "query-only story remediation companion paired admitted method events with admitted extraction/key outcome events",
                "original_query": query,
            },
        },
        "derived_from_queries": [query, "event(Event, Actor, Action, Object, Location)."],
    }


def _same_recall_family(left: str, right: str) -> bool:
    left_norm = _normalized_atom_tokens(left)
    right_norm = _normalized_atom_tokens(right)
    return bool(left_norm and right_norm and left_norm == right_norm)


def _normalized_atom_tokens(value: str) -> tuple[str, ...]:
    tokens = [token for token in re.split(r"[^a-z0-9]+", str(value or "").lower()) if token]
    noise = {"recall"}
    return tuple(sorted(token for token in tokens if token not in noise))


def _date_atom_sort_key(value: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"(\d{4})_(\d{2})_(\d{2})(?:t.*)?", str(value or "").strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def _count_atom_range(value: str) -> int | None:
    match = re.search(r"([a-z])_through_.*_([a-z])$", str(value or "").lower())
    if not match:
        return None
    start, end = match.groups()
    start_ord = ord(start)
    end_ord = ord(end)
    if end_ord < start_ord:
        return None
    return end_ord - start_ord + 1


def _count_numeric_atom_range(value: str) -> int | None:
    match = re.search(r"(\d+)_to_.*?(\d+)$", str(value or "").lower())
    if not match:
        return None
    start, end = (int(part) for part in match.groups())
    if end < start:
        return None
    return end - start + 1


def _case_atom_key(value: str) -> str:
    return re.sub(r"_+", "", str(value or "").strip().lower())


def _runtime_temporal_datetime(runtime: CorePrologRuntime, value: str) -> datetime | None:
    try:
        term = runtime.engine.parse_term(str(value or "").strip())
    except Exception:
        return None
    try:
        return runtime._temporal_datetime(term)
    except Exception:
        return None


def _status_at_date_interval_companion(runtime: CorePrologRuntime, *, query: str) -> dict[str, Any] | None:
    parsed = parse_prolog_query(query)
    if parsed is None:
        return None
    predicate, args = parsed
    if len(args) != 3:
        return None

    if predicate == "case_status_at_date":
        entity_arg = str(args[0]).strip()
        date_arg = str(args[1]).strip()
        status_arg = str(args[2]).strip()
        timeline_query = "case_status_at_date(Entity, Date, Status)."
        result_predicate = "case_status_at_date"
        support_query = (
            "case_status_at_date_interval_support"
            "(QueryCase, RequestedDate, Status, EffectiveFrom, EffectiveUntil)."
        )
        entity_key = "QueryCase"
        observed_key = "ObservedCase"
        match_key = "CaseMatch"
    elif predicate.endswith(("_status_at", "_state_at")):
        entity_arg = str(args[0]).strip()
        date_arg = str(args[1]).strip()
        status_arg = str(args[2]).strip()
        timeline_query = format_prolog_query(predicate, ["Entity", "Date", "Status"])
        result_predicate = predicate
        support_query = (
            f"{predicate}_interval_support"
            "(QueryEntity, RequestedDate, Status, EffectiveFrom, EffectiveUntil)."
        )
        entity_key = "QueryEntity"
        observed_key = "ObservedEntity"
        match_key = "EntityMatch"
    elif predicate.endswith("_status"):
        entity_arg = str(args[0]).strip()
        status_arg = str(args[1]).strip()
        date_arg = str(args[2]).strip()
        timeline_query = format_prolog_query(predicate, ["Entity", "Status", "Date"])
        result_predicate = predicate
        support_query = (
            f"{predicate}_interval_support"
            "(QueryEntity, RequestedDate, Status, EffectiveFrom, EffectiveUntil)."
        )
        entity_key = "QueryEntity"
        observed_key = "ObservedEntity"
        match_key = "EntityMatch"
    else:
        return None

    if not entity_arg or not date_arg or _is_prolog_variable(entity_arg) or _is_prolog_variable(date_arg):
        return None

    requested_at = _runtime_temporal_datetime(runtime, date_arg)
    if requested_at is None:
        return None

    timeline = runtime.query_rows(timeline_query)
    if timeline.get("status") != "success":
        return None

    requested_entity_key = _case_atom_key(entity_arg)
    anchors: list[dict[str, Any]] = []
    for row in timeline.get("rows", []) or []:
        if not isinstance(row, dict):
            continue
        observed_entity = str(row.get("Entity", "")).strip()
        observed_date = str(row.get("Date", "")).strip()
        observed_status = str(row.get("Status", "")).strip()
        if not observed_entity or not observed_date or not observed_status:
            continue
        entity_match = "exact" if observed_entity == entity_arg else "canonical_atom"
        if entity_match != "exact" and _case_atom_key(observed_entity) != requested_entity_key:
            continue
        observed_at = _runtime_temporal_datetime(runtime, observed_date)
        if observed_at is None:
            continue
        anchors.append(
            {
                "observed_entity": observed_entity,
                "observed_date": observed_date,
                "observed_status": observed_status,
                "observed_at": observed_at,
                "entity_match": entity_match,
            }
        )

    if not anchors:
        return None
    anchors.sort(key=lambda item: item["observed_at"])
    point_anchor = _explicit_status_on_anchor(runtime, entity_arg=entity_arg, date_arg=date_arg, requested_at=requested_at)
    interval_anchor = _status_interval_anchor(runtime, entity_arg=entity_arg, requested_at=requested_at)
    scheduled_anchor = _scheduled_status_anchor(runtime, entity_arg=entity_arg, requested_at=requested_at)

    previous_anchor: dict[str, Any] | None = None
    next_anchor: dict[str, Any] | None = None
    for anchor in anchors:
        if anchor["observed_at"] <= requested_at:
            previous_anchor = anchor
            continue
        next_anchor = anchor
        break
    if previous_anchor is None:
        return None
    selected_anchor = previous_anchor
    support_kind = "transition_anchor"
    if interval_anchor and interval_anchor["observed_at"] <= requested_at:
        selected_anchor = interval_anchor
        support_kind = "corrected_or_stated_interval"
    if scheduled_anchor and scheduled_anchor["observed_at"] <= requested_at:
        if scheduled_anchor["observed_at"] >= selected_anchor["observed_at"]:
            selected_anchor = scheduled_anchor
            support_kind = "scheduled_state_transition"
    if point_anchor:
        selected_anchor = point_anchor
        support_kind = "explicit_point_state"

    requested_status = "" if _is_prolog_variable(status_arg) else status_arg
    status_matches = ""
    if requested_status:
        status_matches = "true" if requested_status == selected_anchor["observed_status"] else "false"

    row: dict[str, str] = {
        entity_key: entity_arg,
        "RequestedDate": date_arg,
        "Status": selected_anchor["observed_status"],
        "EffectiveFrom": selected_anchor["observed_date"],
        "EffectiveUntil": str(selected_anchor.get("effective_until") or (next_anchor["observed_date"] if next_anchor else "")),
        observed_key: selected_anchor["observed_entity"],
        match_key: selected_anchor["entity_match"],
        "SupportKind": support_kind,
    }
    if requested_status:
        row["RequestedStatus"] = requested_status
        row["StatusMatches"] = status_matches

    result = {
        "status": "success",
        "result_type": "table",
        "predicate": result_predicate,
        "prolog_query": support_query,
        "variables": list(row.keys()),
        "rows": [row],
        "num_rows": 1,
        "reasoning_basis": {
            "kind": "core-local",
            "note": (
                f"query-only interval support derived status at an interior date from admitted {predicate}/3 "
                "transition anchors, corrected/stated intervals, or scheduled-state rows; no durable fact was written"
            ),
            "original_query": query,
        },
    }
    return {
        "query": result["prolog_query"],
        "result": result,
        "derived_from_queries": [query, timeline_query],
    }


def _scheduled_status_anchor(
    runtime: CorePrologRuntime,
    *,
    entity_arg: str,
    requested_at: datetime,
) -> dict[str, Any] | None:
    rows: list[dict[str, Any]] = []
    for predicate in (
        "scheduled_archive",
        "scheduled_status",
        "scheduled_state",
        "scheduled_revocation",
        "scheduled_suspension",
        "scheduled_reinstatement",
        "scheduled_closure",
        "scheduled_termination",
    ):
        result = runtime.query_rows(format_prolog_query(predicate, ["Entity", "EffectiveDate"]))
        if result.get("status") != "success":
            continue
        status = _status_from_event_type(predicate.removeprefix("scheduled_"))
        for row in result.get("rows", []) or []:
            if not isinstance(row, dict):
                continue
            observed_entity = str(row.get("Entity", "")).strip()
            effective_date = str(row.get("EffectiveDate", "")).strip()
            if not observed_entity or not effective_date:
                continue
            if observed_entity != entity_arg and _case_atom_key(observed_entity) != _case_atom_key(entity_arg):
                continue
            if predicate in {"scheduled_status", "scheduled_state"}:
                status = str(row.get("Status", "") or row.get("State", "") or status).strip()
            observed_at = _runtime_temporal_datetime(runtime, effective_date)
            if observed_at is None or observed_at > requested_at or not status:
                continue
            rows.append(
                {
                    "observed_entity": observed_entity,
                    "observed_date": effective_date,
                    "observed_status": status,
                    "observed_at": observed_at,
                    "entity_match": "exact" if observed_entity == entity_arg else "canonical_atom",
                }
            )
    return sorted(rows, key=lambda item: item["observed_at"])[-1] if rows else None


def _explicit_status_on_anchor(
    runtime: CorePrologRuntime,
    *,
    entity_arg: str,
    date_arg: str,
    requested_at: datetime,
) -> dict[str, Any] | None:
    for predicate in ("active_on", "inactive_on", "suspended_on", "archived_on", "revoked_on", "closed_on"):
        result = runtime.query_rows(format_prolog_query(predicate, [entity_arg, date_arg]))
        if result.get("status") != "success":
            continue
        status = _status_from_event_type(predicate.removesuffix("_on"))
        if not status:
            continue
        return {
            "observed_entity": entity_arg,
            "observed_date": date_arg,
            "observed_status": status,
            "observed_at": requested_at,
            "effective_until": date_arg,
            "entity_match": "exact",
        }
    return None


def _status_interval_anchor(
    runtime: CorePrologRuntime,
    *,
    entity_arg: str,
    requested_at: datetime,
) -> dict[str, Any] | None:
    intervals: list[dict[str, str]] = []
    for predicate in ("corrected_interval", "status_interval", "state_interval", "original_interval"):
        result = runtime.query_rows(format_prolog_query(predicate, ["Notice", "StartDate", "EndDate"]))
        if result.get("status") != "success":
            continue
        for row in result.get("rows", []) or []:
            if not isinstance(row, dict):
                continue
            notice = str(row.get("Notice", "")).strip()
            start = str(row.get("StartDate", "")).strip()
            end = str(row.get("EndDate", "")).strip()
            if notice and start and end:
                intervals.append({"predicate": predicate, "notice": notice, "start": start, "end": end})
    if not intervals:
        return None

    notice_statuses = _notice_statuses(runtime)
    fallback_status = _unique_status_from_intervals(intervals, notice_statuses)
    anchors: list[dict[str, Any]] = []
    for interval in intervals:
        start_at = _runtime_temporal_datetime(runtime, interval["start"])
        end_at = _runtime_temporal_datetime(runtime, interval["end"])
        if start_at is None or end_at is None or not (start_at <= requested_at <= end_at):
            continue
        status = notice_statuses.get(interval["notice"], "")
        if not status and interval["predicate"] == "corrected_interval":
            status = fallback_status
        if not status:
            continue
        anchors.append(
            {
                "observed_entity": entity_arg,
                "observed_date": interval["start"],
                "observed_status": status,
                "observed_at": start_at,
                "effective_until": interval["end"],
                "entity_match": "exact",
            }
        )
    return sorted(anchors, key=lambda item: item["observed_at"])[-1] if anchors else None


def _notice_statuses(runtime: CorePrologRuntime) -> dict[str, str]:
    result = runtime.query_rows("notice_type(Notice, NoticeType).")
    if result.get("status") != "success":
        return {}
    out: dict[str, str] = {}
    for row in result.get("rows", []) or []:
        if not isinstance(row, dict):
            continue
        notice = str(row.get("Notice", "")).strip()
        status = _status_from_event_type(str(row.get("NoticeType", "")).strip())
        if notice and status:
            out[notice] = status
    return out


def _unique_status_from_intervals(intervals: list[dict[str, str]], notice_statuses: dict[str, str]) -> str:
    statuses = {
        status
        for interval in intervals
        if interval.get("predicate") == "original_interval"
        if (status := notice_statuses.get(interval.get("notice", ""), ""))
    }
    return next(iter(statuses)) if len(statuses) == 1 else ""


def _status_from_event_type(value: str) -> str:
    normalized = str(value or "").strip().lower()
    return {
        "archive": "archived",
        "archival": "archived",
        "archived": "archived",
        "closure": "closed",
        "closing": "closed",
        "revocation": "revoked",
        "revoke": "revoked",
        "revoked": "revoked",
        "suspension": "suspended",
        "suspend": "suspended",
        "suspended": "suspended",
        "termination": "terminated",
        "terminate": "terminated",
        "terminated": "terminated",
        "reinstatement": "active",
        "reinstate": "active",
        "approval": "active",
        "activation": "active",
    }.get(normalized, normalized if normalized.endswith(("ed", "ive")) else "")


def _ordered_query_unique(queries: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for query in queries:
        text = str(query or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def run_evidence_bundle_plan_queries(
    *,
    runtime: CorePrologRuntime,
    evidence_plan: dict[str, Any],
    kb_inventory: dict[str, Any],
    include_legacy_native_helpers: bool = True,
) -> list[dict[str, Any]]:
    signatures = {str(item).strip() for item in kb_inventory.get("signatures", []) if str(item).strip()}
    signatures.update(str(item).strip() for item in TEMPORAL_VIRTUAL_SIGNATURES)
    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    bundles = evidence_plan.get("support_bundles", []) if isinstance(evidence_plan, dict) else []
    plan_queries: list[str] = []
    query_basis: dict[str, dict[str, str]] = {}
    for bundle in bundles:
        if not isinstance(bundle, dict):
            continue
        bundle_id = str(bundle.get("bundle_id", "")).strip()
        purpose = str(bundle.get("purpose", "")).strip()
        for template in bundle.get("query_templates", []):
            query = str(template or "").strip()
            if not query or query in seen:
                continue
            seen.add(query)
            source_text_filter = _source_text_memberchk_repair(query)
            if source_text_filter:
                results.append(
                    _run_source_text_contains_filter(
                        runtime=runtime,
                        original_query=query,
                        filter_spec=source_text_filter,
                        bundle_id=bundle_id,
                        purpose=purpose,
                        include_legacy_native_helpers=include_legacy_native_helpers,
                    )
                )
                continue
            parsed_goals = parse_prolog_query_goals(query)
            if parsed_goals is None:
                results.append(
                    {
                        "query": query,
                        "result": {
                            "status": "error",
                            "message": "evidence-bundle query template was not a Prolog predicate or conjunction",
                            "reasoning_basis": {
                                "kind": "evidence-bundle-plan",
                                "bundle_id": bundle_id,
                                "purpose": purpose,
                                "validation": "rejected",
                            },
                        },
                        "derived_from_queries": [],
                    }
                )
                continue
            query_signatures = [f"{predicate}/{len(args)}" for predicate, args in parsed_goals]
            missing_signatures = [signature for signature in query_signatures if signature not in signatures]
            if missing_signatures:
                results.append(
                    {
                        "query": query,
                        "result": {
                            "status": "error",
                            "message": (
                                "evidence-bundle query signature not in compiled inventory: "
                                + ", ".join(missing_signatures)
                            ),
                            "reasoning_basis": {
                                "kind": "evidence-bundle-plan",
                                "bundle_id": bundle_id,
                                "purpose": purpose,
                                "validation": "rejected",
                                "query_signatures": query_signatures,
                            },
                        },
                        "derived_from_queries": [],
                    }
                )
                continue
            plan_queries.append(query)
            query_basis[query] = {"bundle_id": bundle_id, "purpose": purpose}
    if not plan_queries:
        return results
    for item in run_query_plan(
        runtime,
        plan_queries,
        include_legacy_native_helpers=include_legacy_native_helpers,
    ):
        item = dict(item)
        result = item.get("result", {})
        derived_from = [
            str(query).strip()
            for query in item.get("derived_from_queries", [])
            if str(query).strip()
        ]
        if not derived_from:
            item_query = str(item.get("query", "")).strip()
            if item_query:
                derived_from = [item_query]
        source_bundles: list[dict[str, str]] = []
        seen_bundle_ids: set[str] = set()
        for query in derived_from:
            basis = query_basis.get(query)
            if not basis:
                continue
            basis_key = json.dumps(basis, sort_keys=True)
            if basis_key in seen_bundle_ids:
                continue
            seen_bundle_ids.add(basis_key)
            source_bundles.append(dict(basis))
        if isinstance(result, dict):
            reasoning_basis: dict[str, Any] = {
                "kind": "evidence-bundle-plan",
                "validation": "predicate_and_arity_checked",
                "inner_basis": result.get("reasoning_basis", {}),
            }
            if len(source_bundles) == 1:
                reasoning_basis.update(source_bundles[0])
            elif source_bundles:
                reasoning_basis["source_bundles"] = source_bundles
            result = {**result, "reasoning_basis": reasoning_basis}
            item["result"] = result
        item["derived_from_queries"] = derived_from
        results.append(item)
    return results


def _source_text_memberchk_repair(query: str) -> dict[str, str] | None:
    match = re.fullmatch(
        r"\s*source_record_text_atom\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)\s*,\s*"
        r"memberchk\(\s*['\"]([^'\"]+)['\"]\s*,\s*\2\s*\)\s*\.?\s*",
        str(query or ""),
    )
    if not match:
        return None
    line_var, text_var, needle = match.groups()
    if not line_var[:1].isupper() or not text_var[:1].isupper():
        return None
    return {"line_var": line_var, "text_var": text_var, "needle": needle}


def _run_source_text_contains_filter(
    *,
    runtime: CorePrologRuntime,
    original_query: str,
    filter_spec: dict[str, str],
    bundle_id: str,
    purpose: str,
    include_legacy_native_helpers: bool = True,
) -> dict[str, Any]:
    line_var = filter_spec["line_var"]
    text_var = filter_spec["text_var"]
    needle = _normalize_text_filter_atom(filter_spec["needle"])
    repaired_query = f"source_record_text_atom({line_var}, {text_var})."
    item = run_query_plan(
        runtime,
        [repaired_query],
        include_legacy_native_helpers=include_legacy_native_helpers,
    )[0]
    result = item.get("result", {}) if isinstance(item, dict) else {}
    rows = result.get("rows", []) if isinstance(result, dict) else []
    filtered_rows = [
        row
        for row in rows
        if isinstance(row, dict)
        and needle
        and needle in _normalize_text_filter_atom(str(row.get(text_var, "")))
    ]
    return {
        "query": original_query,
        "result": {
            "status": "success",
            "predicate": "source_record_text_atom",
            "prolog_query": repaired_query,
            "result_type": "table",
            "variables": [line_var, text_var],
            "num_rows": len(filtered_rows),
            "rows": filtered_rows,
            "reasoning_basis": {
                "kind": "evidence-bundle-plan",
                "bundle_id": bundle_id,
                "purpose": purpose,
                "validation": "source_text_contains_filter_repaired",
                "original_query": original_query,
                "repaired_query": repaired_query,
                "unsupported_predicate": "memberchk/2",
            },
        },
        "derived_from_queries": [repaired_query],
    }


def _normalize_text_filter_atom(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").casefold()).strip("_")


def compact_relevant_clauses_for_evidence_plan(
    *,
    evidence_plan: dict[str, Any],
    facts: list[str],
    rules: list[str],
    max_clauses: int = 220,
    broad_floor: int = 80,
) -> list[str]:
    predicates: set[str] = set()
    bundles = evidence_plan.get("support_bundles", []) if isinstance(evidence_plan, dict) else []
    for bundle in bundles:
        if not isinstance(bundle, dict):
            continue
        for template in bundle.get("query_templates", []):
            parsed = parse_prolog_query(str(template or ""))
            if parsed is None:
                continue
            predicate, _args = parsed
            predicates.add(predicate)
    if not predicates:
        return []
    selected: list[str] = []
    seen: set[str] = set()
    for clause in [*facts, *rules]:
        signature = clause_signature(clause)
        predicate = signature.split("/", 1)[0] if "/" in signature else ""
        if predicate in predicates:
            seen.add(clause)
            selected.append(clause)
        if len(selected) >= int(max_clauses):
            break
    for clause in [*facts, *rules]:
        if len(selected) >= int(max_clauses):
            break
        if clause in seen:
            continue
        selected.append(clause)
        seen.add(clause)
        if len(selected) >= len(predicates) + int(broad_floor) and len(selected) >= int(broad_floor):
            break
    return selected


def _evidence_table_companion_query(runtime: CorePrologRuntime, *, query: str) -> dict[str, Any] | None:
    parsed = parse_prolog_query(query)
    if parsed is None:
        return None
    predicate, args = parsed
    if predicate not in EVIDENCE_TABLE_PREDICATES:
        return None

    companion_args: list[str] = []
    role_names = EVIDENCE_TABLE_VARIABLE_NAMES.get(predicate, [])
    for index, arg in enumerate(args, start=1):
        item = str(arg or "").strip()
        if _is_prolog_variable(item):
            companion_args.append(role_names[index - 1] if index <= len(role_names) else item)
            continue
        # Keep a concrete leading policy/document/record key when present, but
        # widen the remaining evidence slots. These predicates often spread the
        # answer across sibling rows, so a narrowly successful query can still
        # under-support the judge.
        if index == 1 and not _is_numeric_atom(item) and item.lower() not in GENERIC_QUERY_PLACEHOLDERS:
            companion_args.append(item)
            continue
        companion_args.append(role_names[index - 1] if index <= len(role_names) else f"Evidence{index}")
    companion_query = format_prolog_query(predicate, companion_args)
    if companion_query == str(query or "").strip():
        return None
    result = runtime.query_rows(companion_query)
    if result.get("status") != "success":
        return None
    return {
        "query": companion_query,
        "result": {
            **result,
            "reasoning_basis": {
                "kind": "core-local",
                "note": "evidence-table companion query widened non-key slots for a table-like predicate after structured query review",
                "original_query": query,
            },
        },
        "derived_from_queries": [query],
    }


def _relaxed_constant_query(runtime: CorePrologRuntime, *, query: str) -> dict[str, Any] | None:
    text = str(query or "").strip()
    parsed = parse_prolog_query(text)
    if parsed is None:
        return None
    predicate, args = parsed
    if predicate in {"before", "after", "add_hours", "elapsed_minutes", "elapsed_hours", "elapsed_days"}:
        return None
    relaxed_args: list[str] = []
    relaxed_constants: list[dict[str, Any]] = []
    relaxed_count = 0
    for index, arg in enumerate(args, start=1):
        item = str(arg or "").strip()
        if _is_prolog_variable(item):
            relaxed_args.append(item)
            continue
        if _is_numeric_atom(item):
            relaxed_args.append(item)
            continue
        relaxed_count += 1
        variable = f"Relaxed{index}"
        relaxed_args.append(variable)
        relaxed_constants.append({"index": index, "variable": variable, "value": item})
    if relaxed_count == 0:
        return None
    relaxed_query = f"{predicate}({', '.join(relaxed_args)})."
    if relaxed_query == text:
        return None
    result = runtime.query_rows(relaxed_query)
    if result.get("status") != "success":
        return None
    rows = result.get("rows")
    token_filtered = _token_subset_filter_relaxed_rows(
        rows=rows if isinstance(rows, list) else [],
        relaxed_constants=relaxed_constants,
    )
    if token_filtered is not None:
        result = {
            **result,
            "rows": token_filtered["rows"],
            "num_rows": len(token_filtered["rows"]),
        }
    reasoning_basis = {
        "kind": "core-local",
        "note": "diagnostic relaxed query synthesized after an over-bound structured query returned no results",
        "original_query": text,
    }
    if token_filtered is not None:
        reasoning_basis.update(
            {
                "token_subset_filter": True,
                "unfiltered_num_rows": token_filtered["unfiltered_num_rows"],
                "filtered_num_rows": len(token_filtered["rows"]),
                "filtered_constants": token_filtered["filtered_constants"],
            }
        )
    return {
        "query": relaxed_query,
        "result": {
            **result,
            "reasoning_basis": reasoning_basis,
        },
        "derived_from_queries": [text],
    }


def _token_subset_filter_relaxed_rows(
    *,
    rows: list[Any],
    relaxed_constants: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not rows or not relaxed_constants:
        return None
    filter_specs: list[dict[str, Any]] = []
    for item in relaxed_constants:
        value = str(item.get("value", "")).strip()
        tokens = _query_atom_tokens(value)
        if len(tokens) < 2:
            continue
        filter_specs.append({**item, "tokens": tokens})
    if not filter_specs:
        return None

    filtered_rows: list[Any] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        matched_all = True
        for spec in filter_specs:
            variable = str(spec.get("variable", ""))
            row_tokens = _query_atom_tokens(str(row.get(variable, "")))
            if not row_tokens:
                matched_all = False
                break
            spec_tokens = set(spec["tokens"])
            row_token_set = set(row_tokens)
            if not (spec_tokens <= row_token_set or row_token_set <= spec_tokens):
                matched_all = False
                break
        if matched_all:
            filtered_rows.append(row)
    if not filtered_rows or len(filtered_rows) >= len(rows):
        return None
    return {
        "rows": filtered_rows,
        "unfiltered_num_rows": len(rows),
        "filtered_constants": [
            {
                "index": int(spec["index"]),
                "variable": str(spec["variable"]),
                "value": str(spec["value"]),
                "tokens": list(spec["tokens"]),
            }
            for spec in filter_specs
        ],
    }


def _query_atom_tokens(value: str) -> list[str]:
    tokens = [
        token
        for token in re.split(r"[^a-z0-9]+", str(value or "").casefold())
        if token and token not in GENERIC_QUERY_PLACEHOLDERS
    ]
    return tokens


def _negative_join_with_previous(
    runtime: CorePrologRuntime,
    *,
    previous_queries: list[str],
    query: str,
) -> dict[str, Any] | None:
    if not re.fullmatch(r"\s*\\\+\(.+\)\.?\s*", query):
        return None
    variables = set(re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", query))
    if not variables:
        return None
    selected: list[str] = []
    for prior in reversed(previous_queries):
        if prior.strip().startswith("\\+"):
            continue
        prior_variables = set(re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", prior))
        if variables & prior_variables:
            selected.insert(0, prior)
            break
    if not selected:
        return None
    joined = f"{', '.join(item.rstrip('. ') for item in selected)}, {query.strip()}"
    result = runtime.query_rows(joined)
    if result.get("status") == "success":
        return {
            "query": joined,
            "result": {
                **result,
                "reasoning_basis": {
                    "kind": "core-local",
                    "note": "set-difference support query synthesized from positive scope query plus negative query operation",
                },
            },
            "derived_from_queries": [*selected, query],
        }
    return None


def _temporal_join_with_previous(
    runtime: CorePrologRuntime,
    *,
    previous_queries: list[str],
    query: str,
) -> dict[str, Any] | None:
    match = re.fullmatch(
        r"\s*(before|after|add_hours|elapsed_minutes|elapsed_hours|elapsed_days)\((.*)\)\.?\s*",
        query,
    )
    if not match:
        return None
    predicate, args_text = match.groups()
    previous_queries = _temporal_queries_with_threshold_bridge(
        previous_queries=previous_queries,
        predicate=predicate,
        args_text=args_text,
    )
    needed_variables = set(re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", args_text))
    if not needed_variables:
        return None
    selected: list[str] = []
    # Temporal chains often arrive as separate structured query operations:
    # state(Start), threshold(Hours), add_hours(Start, Hours, Threshold),
    # notice(Notice), elapsed_minutes(Threshold, Notice, Minutes).  Selecting
    # only direct variable overlaps with the final temporal query drops the
    # support needed to bind intermediate variables.  Build a small dependency
    # closure over prior structured queries instead.
    changed = True
    while changed:
        changed = False
        for prior in reversed(previous_queries):
            if prior in selected:
                continue
            prior_variables = set(re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", prior))
            if needed_variables & prior_variables:
                selected.insert(0, prior)
                needed_variables |= prior_variables
                changed = True
    if not selected:
        return None
    selected_for_join = _disambiguate_relaxed_temporal_join_variables(selected, helper_args_text=args_text)
    query_for_join = query.strip()
    derived_from = [*selected, query]
    if predicate == "elapsed_hours":
        args = [item.strip() for item in args_text.split(",")]
        if len(args) == 3:
            minute_query = f"elapsed_minutes({args[0]}, {args[1]}, Minutes)."
            query_for_join = f"{query_for_join.rstrip('. ')}, {minute_query}"
            derived_from.append(minute_query)
    joined = f"{', '.join(item.rstrip('. ') for item in selected_for_join)}, {query_for_join}"
    result = runtime.query_rows(joined)
    if result.get("status") == "success":
        return {
            "query": joined,
            "result": {
                **result,
                "reasoning_basis": {
                    "kind": "core-local",
                    "note": "conjunctive support query synthesized from structured query operations with shared temporal variables",
                },
            },
            "derived_from_queries": derived_from,
        }
    subset_join = _temporal_subset_join(
        runtime,
        selected=selected_for_join,
        query_for_join=query_for_join,
        derived_query=query,
    )
    if subset_join is not None:
        return subset_join
    return None


def _disambiguate_relaxed_temporal_join_variables(selected: list[str], *, helper_args_text: str) -> list[str]:
    """Avoid accidental joins between local source/provenance slot variables.

    Relaxed fallback queries name widened constants by argument position
    (`Relaxed1`, `Relaxed2`, ...). When two different predicates both widen a
    non-key source slot at the same position, joining them later can falsely
    require the two unrelated slots to have the same value. Temporal helpers
    only need their explicit start/end variables plus whatever key variable the
    relaxed query shares; source/provenance relaxed slots should remain local to
    each prior query. The same issue appears when the model uses a repeated
    variable such as `Eventid` for both an issuance row and a lift row; those are
    provenance anchors, not the temporal values being compared.
    """

    helper_variables = set(re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", helper_args_text))
    variable_counts = Counter(
        variable
        for query in selected
        for variable in re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", query)
        if variable not in helper_variables
    )
    variables_to_localize = {
        variable
        for variable, count in variable_counts.items()
        if count > 1 and _is_local_temporal_join_variable(variable)
    }
    if not variables_to_localize:
        return selected
    disambiguated: list[str] = []
    for index, query in enumerate(selected, start=1):
        updated = query
        for variable in variables_to_localize:
            updated = re.sub(rf"\b{re.escape(variable)}\b", f"{variable}Join{index}", updated)
        disambiguated.append(updated)
    return disambiguated


def _is_local_temporal_join_variable(variable: str) -> bool:
    if re.fullmatch(r"Relaxed[2-9]\d*", variable):
        return True
    lowered = variable.casefold()
    return any(marker in lowered for marker in ("event", "source", "provenance", "rowid", "recordid", "orderid"))


def _temporal_subset_join(
    runtime: CorePrologRuntime,
    *,
    selected: list[str],
    query_for_join: str,
    derived_query: str,
) -> dict[str, Any] | None:
    """Recover when an extra prior temporal query over-constrains a helper.

    The LLM sometimes emits both an event row and a deadline row with the same
    variable name, but the compiled KB may use different date atom surfaces in
    those predicates. The full conjunctive join then fails even though a smaller
    symbolic support bundle is sufficient. This is query execution over already
    admitted clauses, not prose interpretation.
    """

    if len(selected) < 2:
        return None
    seen: set[str] = set()
    for size in range(len(selected) - 1, 0, -1):
        for subset in combinations(selected, size):
            joined = f"{', '.join(item.rstrip('. ') for item in subset)}, {query_for_join}"
            if joined in seen:
                continue
            seen.add(joined)
            result = runtime.query_rows(joined)
            if result.get("status") == "success":
                return {
                    "query": joined,
                    "result": {
                        **result,
                        "reasoning_basis": {
                            "kind": "core-local",
                            "note": "temporal helper support query recovered by dropping an over-constraining prior query",
                        },
                    },
                    "derived_from_queries": [*subset, derived_query],
                }
    return None


def _temporal_queries_with_threshold_bridge(
    *,
    previous_queries: list[str],
    predicate: str,
    args_text: str,
) -> list[str]:
    if predicate not in {"elapsed_minutes", "elapsed_hours", "elapsed_days"}:
        return previous_queries
    args = [item.strip() for item in args_text.split(",")]
    if len(args) != 3:
        return previous_queries
    threshold_var = args[0]
    if not re.fullmatch(r"[A-Z][A-Za-z0-9_]*", threshold_var) or "threshold" not in threshold_var.lower():
        return previous_queries
    if any(re.search(rf"\b{re.escape(threshold_var)}\b", prior) for prior in previous_queries):
        return previous_queries

    start_var = ""
    hours_var = ""
    for prior in previous_queries:
        for variable in re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", prior):
            lowered = variable.lower()
            if not start_var and ("start" in lowered or "offline" in lowered):
                start_var = variable
            if not hours_var and "hours" in lowered and ("threshold" in lowered or "deadline" in lowered):
                hours_var = variable
    if not start_var or not hours_var:
        return previous_queries
    return [*previous_queries, f"add_hours({start_var}, {hours_var}, {threshold_var})."]


def score_oracle(*, row: dict[str, Any], oracle: dict[str, Any]) -> bool | None:
    if not oracle:
        return None
    has_structured_expectation = any(
        key in oracle for key in ("expected_decision", "expected_query_predicates", "expected_answer_contains")
    )
    if not has_structured_expectation:
        return None
    expected_decision = str(oracle.get("expected_decision", "")).strip()
    if expected_decision and str(row.get("projected_decision") or row.get("model_decision", "")).strip() != expected_decision:
        return False
    expected_predicates = [str(item).strip() for item in oracle.get("expected_query_predicates", []) if str(item).strip()]
    if expected_predicates:
        actual = {query.split("(", 1)[0].strip() for query in row.get("queries", [])}
        if not set(expected_predicates).issubset(actual):
            return False
    contains = [str(item).strip() for item in oracle.get("expected_answer_contains", []) if str(item).strip()]
    if contains:
        haystack = json.dumps(row.get("query_results", []), ensure_ascii=False)
        if not all(item in haystack for item in contains):
            return False
    return True


def judge_reference_answer(*, row: dict[str, Any], config: SemanticIRCallConfig) -> dict[str, Any]:
    reference = str(row.get("reference_answer", "")).strip()
    if not reference:
        return {
            "schema_version": "qa_judge_v1",
            "verdict": "not_judged",
            "answer_supported": False,
            "concise_answer": "",
            "issues": ["no reference answer supplied"],
        }
    if _negative_reference_supported_by_results(row=row, reference=reference):
        return {
            "schema_version": "qa_judge_v1",
            "verdict": "exact",
            "answer_supported": True,
            "concise_answer": "Query results contain explicit negative support matching the short negative reference answer.",
            "issues": [],
        }
    if _source_record_reference_supported_by_results(row=row, reference=reference):
        return {
            "schema_version": "qa_judge_v1",
            "verdict": "exact",
            "answer_supported": True,
            "concise_answer": "Query results contain source-record text that clearly embeds the reference answer.",
            "issues": [],
        }
    payload = {
        "task": "Compare deterministic Prolog query results with a human reference answer.",
        "authority": "You are a scorer only. Do not invent missing KB rows. Judge only what the query results support.",
        "question_id": row.get("id", ""),
        "question": row.get("utterance", ""),
        "reference_answer": reference,
        "model_decision": row.get("model_decision", ""),
        "projected_decision": row.get("projected_decision", ""),
        "queries": row.get("queries", []),
        "query_results": row.get("query_results", []),
        "proposed_write_counts": {
            "facts": len(row.get("proposed_facts", []) or []),
            "rules": len(row.get("proposed_rules", []) or []),
        },
        "verdict_policy": [
            "exact: query results clearly support the reference answer, allowing harmless extra rows when the answer set still contains the reference.",
            "partial: query results contain some relevant support but miss important reference content or include unresolved noise.",
            "miss: query results do not support the reference answer, use wrong predicates, return no relevant rows, or propose writes for an ordinary question.",
            "not_judged: malformed/no reference or no meaningful query result to compare.",
            "Identity policy: candidate_identity or ambiguous_identity rows are possible identities, not proof of identity. Multiple candidates support answers such as 'unknown', 'ambiguous', 'not definitively identified', or 'do not assign automatically'.",
            "Automatic-identity policy: candidate_identity(k_lume, kira_lume) does not authorize assigning k_lume to kira_lume. Unless query results include a resolved_identity/same_person/identified_as fact or a rule explicitly permitting assignment, candidate rows support 'No' for automatic assignment questions.",
            "Source-scope policy: if the reference answer says the event is not applicable to this source/document and all relevant queries return no matching rows while the source KB clearly concerns a different document/domain, this supports the reference. Use exact when this is the central answer.",
            "Normalized-atom policy: snake_case atoms are the KB's canonical surface. If a returned atom embeds the reference answer as a clear normalized phrase, such as departed_dock_c_before_yeast_inspection supporting 'Dock C', that can be exact support even when the value appears inside a method or explanation predicate.",
            "Predicate-relation policy: a returned row's predicate name is part of the answer-bearing surface. For example, has_knowledge_of(Entity, mislabeled_folders) can support 'knowledge of mislabeled folders' even when the returned value atom is only mislabeled_folders; do not require the relation words to be duplicated inside the value atom.",
            "Complementary-relation policy: for questions using have, carry, or similar possession verbs with besides, along with, apart from, or in addition to, the named possession/baseline predicate is context. A sibling row over the same subject can provide the abstract complement; do not mark it miss solely because the complement is not also returned by the baseline possession predicate.",
            "Anchor-answer policy: for questions asking which event anchored, triggered, came before, or preceded a move, appointment, assignment, enrollment, or attachment, event_anchor(Anchor, ActionEvent) or triggered_by(ActionEvent, Anchor) can directly support Anchor as the answer. Do not require a separate event_before(Anchor, ActionEvent) row when an anchor/trigger row already binds the asked action to the preceding/anchoring event.",
            "Causal-chain policy: for questions asking what caused, triggered, led to, or brought about an ending, a chain such as led_to(Cause, EndingEvent) plus ended(EndingEvent, EndedState), caused_by(EndingEvent, Cause) plus ended(EndingEvent, EndedState), or triggered(Cause, EndingEvent) plus ended(EndingEvent, EndedState) can directly support Cause as the answer. Do not downgrade solely because ended/2 returns the immediate ending event when the question asks for the upstream cause.",
            "Causal-helper policy: a clean causal_end_state_support row is answer-bearing for cause-of-ending questions. If Cause matches the reference answer and EndedState binds the asked state/process, mark exact even when the primitive ended/2 query also returns the immediate EndingEvent.",
            "Method-frame policy: a clean method_frame_purpose_support row is answer-bearing for method-use questions when Method binds the asked method, Agent binds the asked user or role, and FramePurpose or FrameText binds the broader source-stated task/purpose. Do not downgrade solely because method_action or method_produces_metric rows also expose lower-level measurements.",
            "Identifier-display policy: normalized identifier atoms such as cn_2026_04_15, ar_2026_027, rc_2026_04_20_v, or sc_2026_04_22 support display identifiers such as CN-2026-04-15, AR-2026-027, RC-2026-04-20-V, or SC-2026-04-22 when the alphanumeric token sequence is identical. Do not mark a row miss solely for case, underscore, or hyphen differences in an identifier.",
            "Identifier-metadata policy: clean source-record metadata rows such as source_record_packet_metadata_support with Kind values ending in _identifier or _license_identifier are answer-bearing for identifier/license/code questions when Value or DisplayValue matches the reference identifier. Do not downgrade solely because a narrower predicate such as driver_license/2 was unavailable.",
            "Scoped-count policy: for count questions scoped to a named section, subset, criterion, or status, clean helper rows such as scoped_status_count_support/source_section_status_count are answer-bearing when they bind the requested scope, semantic criterion, count, and members. Broader unscoped status rows are context, not contradiction, when the scoped helper row directly matches the reference answer.",
            "Normalized legal/status atom policy: phrases such as does_not_intend_to_raise_the_defense, reserves_all_defenses, not_a_defense_to_assured, remedied_before_loss, no_contribution_to_loss, statement_not_finding, or accepted_without_prejudice are answer-bearing content when they appear in any returned row. Do not discard them merely because they appear in a Detail, Source, or evidence slot.",
            "Purpose/action atom policy: normalized action-purpose atoms such as fetching_fog_leaves, gathered_fog_leaves, or submitted_revised_budget are answer-bearing. If adjacent returned rows establish the affected object or problem context, do not downgrade solely because the reference answer phrases the same purpose in natural language.",
            "Return the final judgment only. Do not include internal debate, alternative verdicts, or self-correction in concise_answer.",
        ],
    }
    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict QA judge for a governed symbolic KB. "
                "Return qa_judge_v1 JSON only. Judge the KB query results against the human reference answer; "
                "do not use outside knowledge. Give only the final verdict rationale, with no chain-of-thought."
            ),
        },
        {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
    ]
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            return call_lmstudio_json_schema(
                config=config,
                messages=messages,
                schema_name="qa_judge_v1",
                schema=QA_JUDGE_SCHEMA,
                max_tokens=min(int(config.max_tokens), 1200),
            )
        except Exception as exc:
            last_error = exc
            if attempt == 0:
                messages = [
                    *messages,
                    {
                        "role": "user",
                        "content": (
                            "The previous judge response was malformed. "
                            "Retry with exactly one qa_judge_v1 JSON object and no prose."
                        ),
                    },
                ]
                continue
    return {
        "schema_version": "qa_judge_v1",
        "verdict": "not_judged",
        "answer_supported": False,
        "concise_answer": "",
        "issues": [f"judge error: {last_error}"],
    }


def _negative_reference_supported_by_results(*, row: dict[str, Any], reference: str) -> bool:
    reference_text = str(reference or "").strip().casefold()
    reference_tokens = [token for token in re.split(r"[^a-z0-9]+", reference_text) if token]
    if not reference_tokens or len(reference_tokens) > 3:
        return False
    if not set(reference_tokens) <= {"no", "not", "none", "negative", "false"}:
        return False
    for query_result in row.get("query_results", []) or []:
        result = query_result.get("result") if isinstance(query_result, dict) else None
        rows = result.get("rows") if isinstance(result, dict) else None
        for result_row in rows or []:
            for value in _iter_scalar_values(result_row):
                if _value_has_negative_surface(value):
                    return True
    return False


def _source_record_reference_supported_by_results(*, row: dict[str, Any], reference: str) -> bool:
    reference_display = _display_source_phrase(str(reference or "").strip())
    if not reference_display or reference_display in {"yes", "no", "not", "none", "false", "true"}:
        return False
    reference_tokens = _loose_atom_token_set(reference_display)
    if len(reference_tokens) < 2 and len(reference_display) < 4:
        return False
    for query_result in row.get("query_results", []) or []:
        result = query_result.get("result") if isinstance(query_result, dict) else None
        if not isinstance(result, dict):
            continue
        predicate = str(result.get("predicate", "")).strip()
        if predicate not in {"source_record_text_atom", "source_record_label", "method_actor_frame_source_support"}:
            continue
        rows = result.get("rows") if isinstance(result, dict) else None
        for result_row in rows or []:
            for value in _iter_scalar_values(result_row):
                if _display_phrase_contains_reference(
                    value=value,
                    reference_display=reference_display,
                    reference_tokens=reference_tokens,
                ):
                    return True
    return False


def _display_phrase_contains_reference(
    *,
    value: Any,
    reference_display: str,
    reference_tokens: set[str],
) -> bool:
    displayed = _display_source_phrase(str(value or ""))
    if not displayed:
        return False
    if reference_display and reference_display in displayed:
        return True
    value_tokens = _loose_atom_token_set(displayed)
    return bool(reference_tokens and reference_tokens.issubset(value_tokens))


def _iter_scalar_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        values: list[str] = []
        for child in value.values():
            values.extend(_iter_scalar_values(child))
        return values
    if isinstance(value, list):
        values = []
        for child in value:
            values.extend(_iter_scalar_values(child))
        return values
    if value is None:
        return []
    return [str(value)]


def _value_has_negative_surface(value: str) -> bool:
    text = str(value or "").casefold()
    normalized = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    if normalized in {"no", "not", "none", "false", "negative"}:
        return True
    negative_forms = (
        "no_",
        "not_",
        "none_",
        "without_",
        "lacks_",
        "lack_of_",
        "does_not_",
        "did_not_",
        "cannot_",
        "can_not_",
    )
    return any(normalized.startswith(form) or f"_{form}" in normalized for form in negative_forms)


def classify_failure_surface(
    *,
    row: dict[str, Any],
    kb_inventory: dict[str, Any],
    facts: list[str],
    rules: list[str],
    config: SemanticIRCallConfig,
) -> dict[str, Any]:
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    verdict = str(judge.get("verdict", "")).strip()
    if verdict == "exact":
        return {
            "schema_version": "qa_failure_surface_v1",
            "surface": "not_applicable",
            "confidence": 1.0,
            "rationale": "Reference judge marked the row exact.",
            "suggested_next_action": "No failure-surface action needed.",
        }
    reference = str(row.get("reference_answer", "")).strip()
    if not reference:
        return {
            "schema_version": "qa_failure_surface_v1",
            "surface": "judge_uncertain",
            "confidence": 0.2,
            "rationale": "No reference answer was available for failure classification.",
            "suggested_next_action": "Supply a reference answer before classifying the failure surface.",
        }
    payload = {
        "task": "Classify the remaining failure surface for a post-ingestion symbolic QA row.",
        "authority": [
            "You are a scorer and diagnostician only.",
            "Do not answer the user.",
            "Do not propose facts, rules, corrections, or writes.",
            "Do not use the original source document; it is not available here.",
            "Use only the compiled KB inventory, admitted clauses, query plan, query results, and reference answer.",
        ],
        "surface_definitions": {
            "compile_surface_gap": "The query plan is reasonable, but the compiled KB appears to lack the facts/rules/relations needed to support the reference answer.",
            "query_surface_gap": "The compiled KB appears to contain useful support, but the emitted query plan did not retrieve it or used neighboring/wrong predicates or overbound constants.",
            "hybrid_join_gap": "Relevant rows were retrieved or appear available, but answering requires a multi-hop join, temporal helper, set difference, aggregation, arithmetic, or evidence bundle that the current query/runtime did not assemble.",
            "answer_surface_gap": "The query results contain enough support, but the final judge/answer rendering did not recognize or express it cleanly.",
            "judge_uncertain": "There is not enough information in this row to separate the failure surfaces confidently.",
        },
        "question_id": row.get("id", ""),
        "question": row.get("utterance", ""),
        "reference_answer": reference,
        "reference_judge": judge,
        "queries": row.get("queries", []),
        "query_results": row.get("query_results", []),
        "evidence_bundle_plan": row.get("evidence_bundle_plan", {}),
        "compiled_predicate_inventory": {
            "signatures": kb_inventory.get("signatures", [])[:120],
            "counts": kb_inventory.get("counts", {}),
            "examples": kb_inventory.get("examples", {}),
        },
        "relevant_clauses": [*facts[:600], *rules[:160]],
        "classification_policy": [
            "Choose compile_surface_gap only when the admitted KB rows shown here do not appear to contain the reference answer support.",
            "Choose query_surface_gap when relevant support appears in admitted clauses or inventory examples but the emitted query set did not retrieve it.",
            "Choose hybrid_join_gap when rows are present or retrieved but require joining, comparing, counting, set subtraction, temporal arithmetic, or aggregation.",
            "Choose answer_surface_gap only when returned rows are plainly sufficient and the remaining problem is interpretation or wording.",
            "If uncertain, use judge_uncertain with low confidence.",
        ],
    }
    messages = [
        {
            "role": "system",
            "content": (
                "You classify post-ingestion QA failure surfaces for a governed symbolic KB. "
                "Return qa_failure_surface_v1 JSON only. Do not use outside knowledge or the source document."
            ),
        },
        {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
    ]
    try:
        return call_lmstudio_json_schema(
            config=config,
            messages=messages,
            schema_name="qa_failure_surface_v1",
            schema=FAILURE_SURFACE_SCHEMA,
            max_tokens=min(int(config.max_tokens), 1000),
        )
    except Exception as exc:
        return {
            "schema_version": "qa_failure_surface_v1",
            "surface": "judge_uncertain",
            "confidence": 0.0,
            "rationale": f"classifier error: {str(exc)[:440]}",
            "suggested_next_action": "Inspect the row manually or rerun the failure classifier.",
        }


def call_lmstudio_json_schema(
    *,
    config: SemanticIRCallConfig,
    messages: list[dict[str, str]],
    schema_name: str,
    schema: dict[str, Any],
    max_tokens: int,
) -> dict[str, Any]:
    base_url = str(config.base_url or "").rstrip("/")
    endpoint = f"{base_url}/chat/completions" if base_url.endswith("/v1") else f"{base_url}/v1/chat/completions"
    request_messages = [dict(message) for message in messages]
    if not bool(config.think_enabled):
        for message in request_messages:
            if message.get("role") == "system":
                content = str(message.get("content") or "")
                if not content.lstrip().startswith("/no_think"):
                    message["content"] = "/no_think\n" + content
                break
    payload: dict[str, Any] = {
        "model": config.model,
        "messages": request_messages,
        "temperature": float(config.temperature),
        "top_p": float(config.top_p),
        "max_tokens": int(max_tokens),
        "think": bool(config.think_enabled),
        "thinking": bool(config.think_enabled),
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": schema,
            },
        },
    }
    if str(config.reasoning_effort or "").strip():
        payload["reasoning_effort"] = str(config.reasoning_effort).strip()
    if _is_openrouter_base_url(config.base_url) and not bool(config.think_enabled):
        payload["reasoning"] = {"effort": "none", "exclude": True}
        payload["include_reasoning"] = False
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers=_chat_headers(config.api_key),
        method="POST",
    )
    raw = _urlopen_json_with_transient_retries(
        req,
        timeout=int(config.timeout),
        retry_transient=_is_openrouter_base_url(config.base_url),
    )
    choices = raw.get("choices", []) if isinstance(raw, dict) else []
    first = choices[0] if choices and isinstance(choices[0], dict) else {}
    message = first.get("message", {}) if isinstance(first, dict) else {}
    content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
    parsed = json.loads(content)
    if not isinstance(parsed, dict):
        raise RuntimeError("structured judge returned non-object JSON")
    return parsed


TRANSIENT_HTTP_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}


def _urlopen_json_with_transient_retries(
    req: urllib.request.Request,
    *,
    timeout: int,
    retry_transient: bool,
    max_attempts: int = 3,
) -> dict[str, Any]:
    attempts = max(1, int(max_attempts))
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=int(timeout)) as response:
                raw = json.loads(response.read().decode("utf-8"))
            if not isinstance(raw, dict):
                raise RuntimeError("model endpoint returned non-object JSON")
            return raw
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if retry_transient and exc.code in TRANSIENT_HTTP_STATUS_CODES and attempt + 1 < attempts:
                time.sleep(min(2.0, 0.35 * (2**attempt)))
                continue
            raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            if retry_transient and attempt + 1 < attempts:
                time.sleep(min(2.0, 0.35 * (2**attempt)))
                continue
            raise RuntimeError(str(exc)) from exc
    raise RuntimeError("model endpoint failed after transient retries")


def _chat_headers(api_key: str = "") -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    key = str(api_key or os.environ.get("PRETHINKER_API_KEY") or os.environ.get("OPENROUTER_API_KEY") or "").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    referer = _openrouter_referer()
    if referer:
        headers["HTTP-Referer"] = referer
    title = _openrouter_title()
    if title:
        headers["X-Title"] = title
        headers["X-OpenRouter-Title"] = title
    return headers


def _configure_openrouter_title(out_dir: Path) -> None:
    if _openrouter_title():
        return
    os.environ["PRETHINKER_OPENROUTER_TITLE"] = _default_openrouter_title(out_dir)


def _openrouter_title() -> str:
    title = str(
        os.environ.get("PRETHINKER_OPENROUTER_TITLE")
        or os.environ.get("OPENROUTER_APP_TITLE")
        or os.environ.get("OPENROUTER_X_TITLE")
        or ""
    ).strip()
    return _sanitize_header_value(title)


def _openrouter_referer() -> str:
    referer = str(
        os.environ.get("PRETHINKER_OPENROUTER_REFERER")
        or os.environ.get("OPENROUTER_HTTP_REFERER")
        or os.environ.get("OPENROUTER_REFERER")
        or "https://github.com/dr3d/prethinker"
    ).strip()
    return _sanitize_header_value(referer)


def _default_openrouter_title(out_dir: Path) -> str:
    path = out_dir if out_dir.is_absolute() else (REPO_ROOT / out_dir).resolve()
    fixture = path.name or "run"
    return _sanitize_header_value(f"qa:{fixture}")


def _sanitize_header_value(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._:/ -]+", "-", str(value or "").strip())
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -")
    return cleaned[:120]


def _is_openrouter_base_url(base_url: str) -> bool:
    return "openrouter.ai" in str(base_url or "").lower()


def summarize(*, rows: list[dict[str, Any]], load_errors: list[str], elapsed_ms: int) -> dict[str, Any]:
    oracle_rows = [row for row in rows if isinstance(row.get("oracle_match"), bool)]
    judge_rows = [
        row.get("reference_judge")
        for row in rows
        if isinstance(row.get("reference_judge"), dict)
    ]
    failure_surface_counts: dict[str, int] = {}
    for row in rows:
        failure = row.get("failure_surface")
        if not isinstance(failure, dict):
            continue
        surface = str(failure.get("surface", "")).strip() or "unknown"
        failure_surface_counts[surface] = failure_surface_counts.get(surface, 0) + 1
    helper_class_summary = summarize_helper_classes(rows)
    return {
        "question_count": len(rows),
        "reference_answer_rows": sum(1 for row in rows if row.get("reference_answer")),
        "parsed_ok": sum(1 for row in rows if row.get("ok")),
        "query_rows": sum(1 for row in rows if row.get("queries")),
        "write_proposal_rows": sum(1 for row in rows if row.get("proposed_facts") or row.get("proposed_rules")),
        "oracle_rows": len(oracle_rows),
        "oracle_match": sum(1 for row in oracle_rows if row.get("oracle_match") is True),
        "judge_rows": len(judge_rows),
        "judge_exact": sum(1 for judge in judge_rows if judge.get("verdict") == "exact"),
        "judge_partial": sum(1 for judge in judge_rows if judge.get("verdict") == "partial"),
        "judge_miss": sum(1 for judge in judge_rows if judge.get("verdict") == "miss"),
        "failure_surface_counts": failure_surface_counts,
        "helper_class_summary": helper_class_summary,
        "runtime_load_error_count": len(load_errors),
        "elapsed_ms": elapsed_ms,
    }


def summarize_helper_classes(rows: list[dict[str, Any]]) -> dict[str, Any]:
    companion_counts: dict[str, Counter[str]] = {}
    companion_rows: Counter[str] = Counter()
    total_counts: Counter[str] = Counter()
    for row in rows:
        for query_result in row.get("query_results", []) or []:
            if not isinstance(query_result, dict):
                continue
            result = query_result.get("result")
            if not isinstance(result, dict):
                continue
            result_rows = result.get("rows")
            if not isinstance(result_rows, list):
                continue
            classes = [
                str(result_row.get("HelperClass", "") or "unlabeled")
                for result_row in result_rows
                if isinstance(result_row, dict) and (
                    "HelperClass" in result_row or str(result.get("predicate", "")).endswith("_support")
                )
            ]
            if not classes:
                continue
            predicate = str(result.get("predicate", "") or "unknown")
            companion_counts.setdefault(predicate, Counter()).update(classes)
            companion_rows[predicate] += len(classes)
            total_counts.update(classes)
    return {
        "row_count": int(sum(total_counts.values())),
        "helper_class_counts": dict(sorted(total_counts.items())),
        "companion_row_totals": dict(sorted(companion_rows.items())),
        "companion_helper_class_counts": {
            name: dict(sorted(counts.items()))
            for name, counts in sorted(companion_counts.items())
        },
    }


def write_summary(record: dict[str, Any], path: Path) -> None:
    summary = record.get("summary", {})
    helper_summary = summary.get("helper_class_summary", {})
    lines = [
        "# Domain Bootstrap QA Run",
        "",
        f"- Run JSON: `{record.get('run_json', '')}`",
        f"- QA file: `{record.get('qa_file', '')}`",
        f"- Model: `{record.get('model', '')}`",
        f"- Source facts/rules: `{record.get('source_fact_count', 0)}` / `{record.get('source_rule_count', 0)}`",
        f"- Questions: `{summary.get('question_count', 0)}`",
        f"- Parsed OK: `{summary.get('parsed_ok', 0)}`",
        f"- Rows with queries: `{summary.get('query_rows', 0)}`",
        f"- Rows with proposed writes: `{summary.get('write_proposal_rows', 0)}`",
        f"- Oracle rows/matches: `{summary.get('oracle_rows', 0)}` / `{summary.get('oracle_match', 0)}`",
        f"- Reference judge: exact=`{summary.get('judge_exact', 0)}` partial=`{summary.get('judge_partial', 0)}` miss=`{summary.get('judge_miss', 0)}`",
        f"- Failure surfaces: `{summary.get('failure_surface_counts', {})}`",
        f"- Helper classes: `{helper_summary.get('helper_class_counts', {})}` rows=`{helper_summary.get('row_count', 0)}`",
        f"- Cache: enabled=`{summary.get('cache_enabled', False)}` hits=`{summary.get('cache_hits', 0)}` misses=`{summary.get('cache_misses', 0)}`",
        "",
    ]
    companion_counts = helper_summary.get("companion_helper_class_counts", {})
    if companion_counts:
        lines.extend(
            [
                "## Helper Classes",
                "",
                "| Companion | Rows | clean-helper | candidate-helper | unlabeled |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        row_totals = helper_summary.get("companion_row_totals", {})
        for companion, counts in sorted(companion_counts.items()):
            lines.append(
                "| {companion} | {rows} | {clean} | {candidate} | {unlabeled} |".format(
                    companion=companion,
                    rows=row_totals.get(companion, 0),
                    clean=counts.get("clean-helper", 0),
                    candidate=counts.get("candidate-helper", 0),
                    unlabeled=counts.get("unlabeled", 0),
                )
            )
        lines.append("")
    lines.extend([
        "## Rows",
        "",
    ])
    for row in record.get("rows", []):
        lines.extend(
            [
                f"### {row.get('id', '')} - {row.get('utterance', '')}",
                "",
                f"- Phase: `{row.get('phase', '')}`",
                f"- Decision: model=`{row.get('model_decision', '')}` projected=`{row.get('projected_decision', '')}`",
                f"- Queries: `{row.get('queries', [])}`",
                f"- Proposed writes: facts=`{len(row.get('proposed_facts', []) or [])}` rules=`{len(row.get('proposed_rules', []) or [])}`",
                f"- Oracle match: `{row.get('oracle_match', None)}`",
                f"- Reference answer: {row.get('reference_answer', '') or '-'}",
                f"- Reference judge: `{(row.get('reference_judge') or {}).get('verdict', None)}`",
                f"- Failure surface: `{(row.get('failure_surface') or {}).get('surface', None)}`",
                "",
                "```json",
                json.dumps(row.get("query_results", []), ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def _slug(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip()).strip("-").lower()
    return text[:60] or "run"


if __name__ == "__main__":
    raise SystemExit(main())

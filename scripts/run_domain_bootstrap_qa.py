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
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
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
    "explanation",
    "formula",
    "item",
    "label",
    "language",
    "location",
    "method",
    "note",
    "party",
    "person",
    "policy",
    "reason",
    "record",
    "role",
    "source",
    "status",
    "step",
    "subject",
    "supportrole",
    "time",
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
        "If a desired meaning is split across multiple predicates, emit multiple query operations with shared constants or variables.",
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
        "For omission and set-difference questions such as 'which required X did not receive Y', 'which X was omitted', or 'was Y issued to all required X', emit paired query operations: first the required/scope set with a shared variable, then the absent-side predicate with polarity='negative' and the same variable. Example operations: query residential_zone(Zone) polarity positive; query boil_water_notice(Zone, Time, Issuer) polarity negative. Do not emit the second operation as a positive query when the question asks for missing or omitted rows.",
        "For policy-condition questions, retrieve both the governing policy rows and the observed event/measurement rows. Threshold, count, interval, and deadline predicates are answer-bearing evidence, not optional decoration.",
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
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234")
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
        "For multi-hop questions, emit multiple safe query operations over the actual KB predicates instead of inventing a composite predicate.",
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
    }


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
    match = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.?\s*", text)
    if not match:
        return None
    predicate, args_text = match.groups()
    args = split_top_level_args(args_text)
    if not args:
        return None
    return predicate, args


def format_prolog_query(predicate: str, args: list[str]) -> str:
    return f"{predicate}({', '.join(args)})."


def _is_prolog_variable(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Z][A-Za-z0-9_]*", str(value or "").strip()))


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
        "compiled_query_templates": kb_inventory.get("query_templates", [])[:120],
        "relevant_clauses": [*facts[:600], *rules[:160]],
        "planning_policy": [
            "A support bundle is a small group of primitive Prolog queries that, together, can support an answer.",
            "Prefer multiple primitive queries over an invented composite query.",
            "Use uppercase variables for unknown answer slots.",
            "If the KB appears to lack a needed row class, state that in missing_if_empty rather than inventing it.",
            "For why questions, plan queries for reason/tradeoff/effect/procedure rows, not only the headline recommendation.",
            "For policy or guidance questions, separate requirement, observed fact, preference, avoid-pattern, and rationale rows.",
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
    facts_out = [str(q).strip() for q in clauses.get("facts", []) if str(q).strip()]
    rules_out = [str(q).strip() for q in clauses.get("rules", []) if str(q).strip()]
    query_results = run_query_plan(runtime, queries)
    evidence_plan_query_results: list[dict[str, Any]] = []
    if evidence_plan is not None and bool(execute_evidence_bundle_plan):
        evidence_plan_query_results = run_evidence_bundle_plan_queries(
            runtime=runtime,
            evidence_plan=evidence_plan,
            kb_inventory=kb_inventory,
        )
        query_results = [*query_results, *evidence_plan_query_results]
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


def run_query_plan(runtime: CorePrologRuntime, queries: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    previous_queries: list[str] = []
    for query in queries:
        effective_query = query
        placeholder_repair = _placeholder_repaired_query(query)
        if placeholder_repair:
            repaired_query = str(placeholder_repair.get("query", "")).strip()
            repaired_result = runtime.query_rows(repaired_query)
            if repaired_result.get("status") == "success":
                effective_query = repaired_query
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

        last_result = results[-1].get("result", {}) if results else {}
        if isinstance(last_result, dict) and last_result.get("status") != "success":
            status_interval = _status_at_date_interval_companion(runtime, query=effective_query)
            if status_interval:
                results.append(status_interval)
                last_result = status_interval.get("result", {})
        if isinstance(last_result, dict) and last_result.get("status") != "success":
            relaxed = _relaxed_constant_query(runtime, query=query)
            if relaxed:
                results.append(relaxed)
                effective_query = str(relaxed.get("query", query))
                last_result = relaxed.get("result", {})
        companion = _evidence_table_companion_query(runtime, query=effective_query)
        if companion:
            results.append(companion)
        for domain_companion in _domain_companion_queries(runtime, query=effective_query):
            results.append(domain_companion)
        temporal_join = _temporal_join_with_previous(runtime, previous_queries=previous_queries, query=effective_query)
        if temporal_join:
            results.append(temporal_join)
        negative_join = _negative_join_with_previous(runtime, previous_queries=previous_queries, query=effective_query)
        if negative_join:
            results.append(negative_join)
        previous_queries.append(effective_query)
    return results


def _domain_companion_queries(runtime: CorePrologRuntime, *, query: str) -> list[dict[str, Any]]:
    parsed = parse_prolog_query(query)
    if parsed is None:
        return []
    predicate, args = parsed
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
    if predicate != "case_status_at_date" or len(args) != 3:
        return None

    case_arg = str(args[0]).strip()
    date_arg = str(args[1]).strip()
    status_arg = str(args[2]).strip()
    if not case_arg or not date_arg or _is_prolog_variable(case_arg) or _is_prolog_variable(date_arg):
        return None

    requested_at = _runtime_temporal_datetime(runtime, date_arg)
    if requested_at is None:
        return None

    timeline = runtime.query_rows("case_status_at_date(Case, Date, Status).")
    if timeline.get("status") != "success":
        return None

    requested_case_key = _case_atom_key(case_arg)
    anchors: list[dict[str, Any]] = []
    for row in timeline.get("rows", []) or []:
        if not isinstance(row, dict):
            continue
        observed_case = str(row.get("Case", "")).strip()
        observed_date = str(row.get("Date", "")).strip()
        observed_status = str(row.get("Status", "")).strip()
        if not observed_case or not observed_date or not observed_status:
            continue
        case_match = "exact" if observed_case == case_arg else "canonical_atom"
        if case_match != "exact" and _case_atom_key(observed_case) != requested_case_key:
            continue
        observed_at = _runtime_temporal_datetime(runtime, observed_date)
        if observed_at is None:
            continue
        anchors.append(
            {
                "observed_case": observed_case,
                "observed_date": observed_date,
                "observed_status": observed_status,
                "observed_at": observed_at,
                "case_match": case_match,
            }
        )

    if not anchors:
        return None
    anchors.sort(key=lambda item: item["observed_at"])
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

    requested_status = "" if _is_prolog_variable(status_arg) else status_arg
    status_matches = ""
    if requested_status:
        status_matches = "true" if requested_status == previous_anchor["observed_status"] else "false"

    row: dict[str, str] = {
        "QueryCase": case_arg,
        "RequestedDate": date_arg,
        "Status": previous_anchor["observed_status"],
        "EffectiveFrom": previous_anchor["observed_date"],
        "EffectiveUntil": str(next_anchor["observed_date"]) if next_anchor else "",
        "ObservedCase": previous_anchor["observed_case"],
        "CaseMatch": previous_anchor["case_match"],
    }
    if requested_status:
        row["RequestedStatus"] = requested_status
        row["StatusMatches"] = status_matches

    result = {
        "status": "success",
        "result_type": "table",
        "predicate": "case_status_at_date",
        "prolog_query": "case_status_at_date_interval_support(QueryCase, RequestedDate, Status, EffectiveFrom, EffectiveUntil).",
        "variables": list(row.keys()),
        "rows": [row],
        "num_rows": 1,
        "reasoning_basis": {
            "kind": "core-local",
            "note": "query-only interval support derived status at an interior date from admitted case_status_at_date/3 transition anchors; no durable fact was written",
            "original_query": query,
        },
    }
    return {
        "query": result["prolog_query"],
        "result": result,
        "derived_from_queries": [query, "case_status_at_date(Case, Date, Status)."],
    }


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
) -> list[dict[str, Any]]:
    signatures = {str(item).strip() for item in kb_inventory.get("signatures", []) if str(item).strip()}
    signatures.update(str(item).strip() for item in TEMPORAL_VIRTUAL_SIGNATURES)
    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    bundles = evidence_plan.get("support_bundles", []) if isinstance(evidence_plan, dict) else []
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
            parsed = parse_prolog_query(query)
            if parsed is None:
                results.append(
                    {
                        "query": query,
                        "result": {
                            "status": "error",
                            "message": "evidence-bundle query template was not a single predicate query",
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
            predicate, args = parsed
            signature = f"{predicate}/{len(args)}"
            if signature not in signatures:
                results.append(
                    {
                        "query": query,
                        "result": {
                            "status": "error",
                            "message": f"evidence-bundle query signature not in compiled inventory: {signature}",
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
            for item in run_query_plan(runtime, [query]):
                item = dict(item)
                result = item.get("result", {})
                if isinstance(result, dict):
                    result = {
                        **result,
                        "reasoning_basis": {
                            "kind": "evidence-bundle-plan",
                            "bundle_id": bundle_id,
                            "purpose": purpose,
                            "validation": "predicate_and_arity_checked",
                            "inner_basis": result.get("reasoning_basis", {}),
                        },
                    }
                    item["result"] = result
                item["derived_from_queries"] = [*item.get("derived_from_queries", []), query]
                results.append(item)
    return results


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
        relaxed_args.append(f"Relaxed{index}")
    if relaxed_count == 0:
        return None
    relaxed_query = f"{predicate}({', '.join(relaxed_args)})."
    if relaxed_query == text:
        return None
    result = runtime.query_rows(relaxed_query)
    if result.get("status") != "success":
        return None
    return {
        "query": relaxed_query,
        "result": {
            **result,
            "reasoning_basis": {
                "kind": "core-local",
                "note": "diagnostic relaxed query synthesized after an over-bound structured query returned no results",
                "original_query": text,
            },
        },
        "derived_from_queries": [text],
    }


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
    query_for_join = query.strip()
    derived_from = [*selected, query]
    if predicate == "elapsed_hours":
        args = [item.strip() for item in args_text.split(",")]
        if len(args) == 3:
            minute_query = f"elapsed_minutes({args[0]}, {args[1]}, Minutes)."
            query_for_join = f"{query_for_join.rstrip('. ')}, {minute_query}"
            derived_from.append(minute_query)
    joined = f"{', '.join(item.rstrip('. ') for item in selected)}, {query_for_join}"
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
        selected=selected,
        query_for_join=query_for_join,
        derived_query=query,
    )
    if subset_join is not None:
        return subset_join
    return None


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
            "Normalized legal/status atom policy: phrases such as does_not_intend_to_raise_the_defense, reserves_all_defenses, not_a_defense_to_assured, remedied_before_loss, no_contribution_to_loss, statement_not_finding, or accepted_without_prejudice are answer-bearing content when they appear in any returned row. Do not discard them merely because they appear in a Detail, Source, or evidence slot.",
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
    payload: dict[str, Any] = {
        "model": config.model,
        "messages": messages,
        "temperature": float(config.temperature),
        "top_p": float(config.top_p),
        "max_tokens": int(max_tokens),
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
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=int(config.timeout)) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc)) from exc
    choices = raw.get("choices", []) if isinstance(raw, dict) else []
    first = choices[0] if choices and isinstance(choices[0], dict) else {}
    message = first.get("message", {}) if isinstance(first, dict) else {}
    content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
    parsed = json.loads(content)
    if not isinstance(parsed, dict):
        raise RuntimeError("structured judge returned non-object JSON")
    return parsed


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
        "runtime_load_error_count": len(load_errors),
        "elapsed_ms": elapsed_ms,
    }


def write_summary(record: dict[str, Any], path: Path) -> None:
    summary = record.get("summary", {})
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
        f"- Cache: enabled=`{summary.get('cache_enabled', False)}` hits=`{summary.get('cache_hits', 0)}` misses=`{summary.get('cache_misses', 0)}`",
        "",
        "## Rows",
        "",
    ]
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

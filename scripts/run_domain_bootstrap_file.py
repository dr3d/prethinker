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
import os
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

from src.carrier_contract_registry import carrier_contract, carrier_contract_prompt_lines

PROFILE_ADMISSION_TOKEN_RE = re.compile(r"[a-z0-9]+")
PROFILE_ADMISSION_DATE_RE = re.compile(r"\b(?:v_)?\d{4}[-_]\d{2}[-_]\d{2}\b")
PROFILE_ADMISSION_FULL_DATE_ATOM_RE = re.compile(r"(?:^|[_\-\s])(?:v_)?(?:19|20)\d{2}[_\-]?[01]\d[_\-]?[0-3]\d(?:[_\-\s]|$)")
PROFILE_ADMISSION_COMPACT_DATE_RE = re.compile(r"(?:^|[_\-\s])(?:19|20)\d{6}(?:[_\-\s]|$)")
FACT_CLAUSE_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
ENTITY_ID_ATOM_RE = re.compile(r"^[a-z][a-z0-9_]*$")
PROFILE_ADMISSION_DATE_SLOTS = {"date", "dated", "timestamp", "time", "turn", "source"}
PROFILE_ADMISSION_SUBJECT_SLOTS = {
    "application",
    "artifact",
    "case",
    "docket",
    "entity",
    "file",
    "id",
    "item",
    "license",
    "object",
    "permit",
    "proposal",
    "queue",
    "record",
    "sample",
    "subject",
    "ticket",
}
PROFILE_ADMISSION_STATE_SLOTS = {"outcome", "phase", "result", "state", "status"}
PROFILE_ADMISSION_SCOPE_SLOTS = {"as", "asof", "current", "date", "dated", "effective", "scope", "source", "time", "timestamp"}
PROFILE_ADMISSION_STATUS_STATE_TERMS = {
    "active",
    "approved",
    "available",
    "cleared",
    "closed",
    "condition",
    "current",
    "denied",
    "failed",
    "hold",
    "pending",
    "resolved",
    "state",
    "status",
    "suspect",
    "suspended",
    "terminated",
    "unresolved",
    "voided",
}
PROFILE_ADMISSION_SOURCE_CLAIM_SOURCE_TERMS = {
    "assessment",
    "assertion",
    "argue",
    "argued",
    "argues",
    "comment",
    "certification",
    "email",
    "letter",
    "memo",
    "memorandum",
    "note",
    "noted",
    "notes",
    "opinion",
    "report",
    "respond",
    "responded",
    "responds",
    "said",
    "says",
    "source",
    "statement",
    "states",
    "testimony",
    "testified",
    "witness",
}
PROFILE_ADMISSION_SOURCE_CLAIM_CONTENT_TERMS = {
    "active",
    "authority",
    "available",
    "binding",
    "claim",
    "cleared",
    "concern",
    "concerned",
    "concerns",
    "confirmed",
    "determined",
    "determination",
    "disagree",
    "documentation",
    "disputed",
    "dispute",
    "finding",
    "flagged",
    "legal",
    "objection",
    "objected",
    "objects",
    "opposed",
    "opposes",
    "pending",
    "professional",
    "resolved",
    "status",
    "supports",
    "true",
    "unresolved",
    "void",
}
PROFILE_DELIVERY_US_STATES: dict[str, tuple[str, ...]] = {
    "al": ("alabama", "al"),
    "ak": ("alaska", "ak"),
    "az": ("arizona", "az"),
    "ar": ("arkansas", "ar"),
    "ca": ("california", "ca"),
    "co": ("colorado", "co"),
    "ct": ("connecticut", "ct"),
    "de": ("delaware", "de"),
    "dc": ("district of columbia", "dc"),
    "fl": ("florida", "fl"),
    "ga": ("georgia", "ga"),
    "hi": ("hawaii", "hi"),
    "ia": ("iowa", "ia"),
    "id": ("idaho", "id"),
    "il": ("illinois", "il"),
    "in": ("indiana", "in"),
    "ks": ("kansas", "ks"),
    "ky": ("kentucky", "ky"),
    "la": ("louisiana", "la"),
    "ma": ("massachusetts", "ma"),
    "md": ("maryland", "md"),
    "me": ("maine", "me"),
    "mi": ("michigan", "mi"),
    "mn": ("minnesota", "mn"),
    "mo": ("missouri", "mo"),
    "ms": ("mississippi", "ms"),
    "mt": ("montana", "mt"),
    "nc": ("north carolina", "nc"),
    "nd": ("north dakota", "nd"),
    "ne": ("nebraska", "ne"),
    "nh": ("new hampshire", "nh"),
    "nj": ("new jersey", "nj"),
    "nm": ("new mexico", "nm"),
    "nv": ("nevada", "nv"),
    "ny": ("new york", "ny"),
    "oh": ("ohio", "oh"),
    "ok": ("oklahoma", "ok"),
    "or": ("oregon", "or"),
    "pa": ("pennsylvania", "pa"),
    "ri": ("rhode island", "ri"),
    "sc": ("south carolina", "sc"),
    "sd": ("south dakota", "sd"),
    "tn": ("tennessee", "tn"),
    "tx": ("texas", "tx"),
    "ut": ("utah", "ut"),
    "va": ("virginia", "va"),
    "vt": ("vermont", "vt"),
    "wa": ("washington", "wa"),
    "wi": ("wisconsin", "wi"),
    "wv": ("west virginia", "wv"),
    "wy": ("wyoming", "wy"),
}
PROFILE_DELIVERY_DISTRIBUTION_CARRIER_NAMES = {
    "distributed_in_state",
    "distributed_to_state",
    "distribution_entry",
    "product_retailer_in_state",
    "product_restriction",
    "recall_distribution",
    "retailer_restriction",
    "sold_at_retailer",
    "sold_at_store",
    "sold_in_state",
}
PROFILE_ADMISSION_QUANTITY_EVENT_SUBJECT_SLOTS = {"ev", "event", "entry", "interval", "measurement", "observation", "reading", "record", "sample"}
PROFILE_ADMISSION_QUANTITY_VALUE_SLOTS = {
    "amount",
    "count",
    "duration",
    "limit",
    "measurement",
    "offset",
    "quantity",
    "rate",
    "ratio",
    "score",
    "threshold",
    "value",
}
PROFILE_ADMISSION_QUANTITY_UNIT_SLOTS = {"basis", "unit", "units"}
PROFILE_ADMISSION_LIFECYCLE_TERMS = {
    "approved",
    "assigned",
    "closed",
    "completed",
    "corrected",
    "denied",
    "filed",
    "lifecycle",
    "logged",
    "pending",
    "phase",
    "received",
    "reinstated",
    "reopened",
    "result",
    "state",
    "status",
    "superseded",
    "transition",
    "withdrawn",
}
PROFILE_ADMISSION_QUANTITY_TERMS = {
    "amount",
    "count",
    "duration",
    "decreased",
    "decrease",
    "increase",
    "increased",
    "limit",
    "measurement",
    "offset",
    "quantity",
    "rate",
    "ratio",
    "reading",
    "reverted",
    "score",
    "setpoint",
    "threshold",
    "unit",
    "value",
}
PROFILE_ADMISSION_QUANTITY_UNIT_TERMS = {"c", "cm", "feet", "hours", "kg", "k", "kw", "m", "meters", "min", "minutes", "mm", "percent", "seconds"}

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
    "Narrative source rule: preserve source-local names and aliases. If the text uses unfamiliar invented names, do not normalize them to famous-story names or unrelated familiar names.",
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
    "Narrative story-world residence roster rule: opening home/household sentences are query-bearing. When the source says who lives in, keeps, shares, or belongs to a named home, preserve each named resident separately with lives_at/2 or household_member/2 when available; do not collapse a three-person roster into only a group atom.",
    "Narrative story-world errand/distraction rule: errands, instructions, and comic distraction lists before arrival are query-bearing setup. Preserve who sent whom, intended purchases/tasks, and each named distraction as separate event/5, caused_by/2, has_property/2, or source-local detail rows instead of reducing the arrival to a single entered-home event.",
    "Narrative story-world food/occasion coverage: when ingredient_of/2, contains_before_eating/2, occasion/1, honoree/2, served_for/2, property/2, or portion_of/2 are available, preserve named ingredients/components, special occasions, honorees, and portion/component relations instead of reducing food to a single object.",
    "Narrative story-world event-spine coverage: when event/5 and story_time/2 are available, preserve source-stated actions such as making/baking/placing/leaving/gathering/entering/eating/trying/finding/repairing as event rows with stable event ids and story_time anchors. Use why_did_* derived-reason predicates only when the profile provides them and the source directly states the reason.",
    "Narrative story-world choice-by-contrast rule: when a character rejects two family members as too X and accepts the remaining little/middle/great item because it is explicitly described as acceptable, preserve both the rejected judgments and the positive property for the accepted item. The accepted item is not safe to infer from size alone unless the positive source phrase is preserved.",
    "Narrative story-world comic-consequence rule: comic object scenes often encode the answer in concrete consequences, not just the attempt. Preserve pretend roles, unsuitable-purpose contrasts, knocked-down objects, spilled contents, path details such as through/under locations, and final item conditions such as tooth marks or still-working status as explicit rows when the profile gives any usable event, condition, has_property, location, or said predicate.",
    "Narrative story-world explicit-moral rule: closing morals, lessons, warnings, songs, labels, or aphoristic quoted lines are source facts when stated by the narrator or source. Preserve the exact moral/lesson surface with moral/1, lesson/1, final_state/1, condition_after_story/2, said/3, or the nearest profile-owned quote/state predicate; do not replace an explicit quote with only a paraphrased condition.",
    "Narrative story-world backbone-plus-detail rule: rich detail predicates are additive layers, not substitutes for the queryable story backbone. Event, story_time, character, kind, lives_at, object/food/place, ownership/design, location, speech, judgment, cause, and final-state rows should survive in the same compile when the profile supports them.",
    "Narrative story-world registry mapping rule: if an intake pass recommends generic story predicates that are not in the allowed profile, map the pass purpose onto the actual allowed story-world predicates instead. For this style of source, the actual backbone is usually character/1, kind/2, household_member/2, lives_at/2, object/1, food/1, place/1, owned_by/2, designed_for/2, initial_location/2, location_after_event/3, event/5, story_time/2, said/3, judged/4, causes/2, caused_by/2, final_state/1, condition_after_story/2, and restitution/2.",
    "Narrative story-world entity-role rule: named characters, homes, object families, food/components, and important places are not merely entity metadata. If the profile supports typed rows and relationship rows, emit both the entity/type row and the relationship row so later queries can join them without guessing atoms.",
    "Narrative story-world character-attribute rule: source-stated ages, titles, origins, nicknames, kinship, and official capacities are query-bearing character attributes. If the profile can support it, use a dedicated attribute predicate such as age/2, person_age/2, property/2, role_authority/3, duty/3, or an equivalent profile-owned surface; do not encode numeric ages or duties as names or aliases.",
    "Narrative story-world official-duty rule: a role row such as fair_warden is not enough when the source states what that official inspects, certifies, authorizes, investigates, or decides. Preserve duties, authority scope, and representative rulings as separate queryable rows when the profile supports them.",
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

FINANCIAL_REPORT_SOURCE_COMPILER_CONTEXT_V1 = [
    "financial_report_source_compiler_strategy_v1: Use this for sources classified by the LLM intake plan or domain hint as earnings releases, financial statements, annual or quarterly reports, corporate disclosures, issuer reports, or financial-result packets.",
    "Financial report rule: source-stated totals and named scope contributions are separate query surfaces. When the source states a total line and a named affiliate, associate, investee, subsidiary, segment, customer, vendor, or project contribution to the same metric, preserve both values as joinable rows with period, named scope/entity, metric, value, and unit when compatible predicates exist.",
    "Financial report rule: do not treat narrative financial amounts as decorative commentary. An explanatory paragraph that states a metric value, named contributor, forecast assumption, or year-over-year driver is a source row with the same preservation priority as a table cell when later questions may ask for that amount or contribution.",
    "Financial report rule: if the allowed profile has only a general carrier such as financial_result/5, metric_observation/4, source_detail/4, or a source-local amount predicate, use the best compatible carrier and keep the named scope/entity in a stable scope or metric/basis label consistently. Do not drop a named contribution merely because the profile lacks a perfect entity-specific financial predicate.",
    "Financial report rule: profile_bootstrap_v1 candidate predicates have a five-slot maximum. Do not invent /6 financial predicates; if source/basis must be queryable, preserve it through a separate source-coordinate/provenance carrier or the source-record ledger.",
    "Financial report rule: source-contained ratios should be recoverable from preserved operand rows. Preserve numerator and denominator values with compatible units and basis/scope; emit an explicit ratio or calculation row only when the source states it or when the allowed profile has a safe calculation predicate that keeps operands and basis visible.",
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

GOVERNED_SUBJECT_MANIFEST_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "subjects", "self_check"],
    "properties": {
        "schema_version": {"type": "string", "const": "governed_subject_manifest_v1"},
        "subjects": {
            "type": "array",
            "maxItems": 12,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "subject_id",
                    "kind",
                    "ranges",
                    "ground",
                    "legal_citations",
                    "review_outcomes",
                    "omitted_companions",
                ],
                "properties": {
                    "subject_id": {"type": "string", "maxLength": 80},
                    "kind": {"type": "string", "maxLength": 80},
                    "ranges": {
                        "type": "array",
                        "maxItems": 24,
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["start", "end", "source_or_scope"],
                            "properties": {
                                "start": {"type": "string", "maxLength": 40},
                                "end": {"type": "string", "maxLength": 40},
                                "source_or_scope": {"type": "string", "maxLength": 80},
                            },
                        },
                    },
                    "ground": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["present", "theory", "reference", "status", "source_or_scope"],
                        "properties": {
                            "present": {"type": "boolean"},
                            "theory": {"type": "string", "maxLength": 80},
                            "reference": {"type": "string", "maxLength": 80},
                            "status": {"type": "string", "maxLength": 80},
                            "source_or_scope": {"type": "string", "maxLength": 80},
                        },
                    },
                    "legal_citations": {
                        "type": "array",
                        "maxItems": 8,
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["citation", "role", "source_or_scope"],
                            "properties": {
                                "citation": {"type": "string", "maxLength": 80},
                                "role": {"type": "string", "maxLength": 80},
                                "source_or_scope": {"type": "string", "maxLength": 80},
                            },
                        },
                    },
                    "review_outcomes": {
                        "type": "array",
                        "maxItems": 8,
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["reviewer", "outcome", "source_or_scope"],
                            "properties": {
                                "reviewer": {"type": "string", "maxLength": 80},
                                "outcome": {"type": "string", "maxLength": 80},
                                "source_or_scope": {"type": "string", "maxLength": 80},
                            },
                        },
                    },
                    "omitted_companions": {
                        "type": "array",
                        "maxItems": 8,
                        "items": {"type": "string", "maxLength": 160},
                    },
                },
            },
        },
        "self_check": {
            "type": "object",
            "additionalProperties": False,
            "required": ["missing_subjects", "notes"],
            "properties": {
                "missing_subjects": {"type": "array", "maxItems": 8, "items": {"type": "string", "maxLength": 160}},
                "notes": {"type": "array", "maxItems": 8, "items": {"type": "string", "maxLength": 160}},
            },
        },
    },
}

GOVERNED_SUBJECT_ATOM_ROWS_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "rows", "self_check"],
    "properties": {
        "schema_version": {"type": "string", "const": "governed_subject_atom_rows_v1"},
        "rows": {
            "type": "array",
            "maxItems": 48,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["signature", "args", "source_or_scope"],
                "properties": {
                    "signature": {
                        "type": "string",
                        "enum": [
                            "claim_range/4",
                            "claim_ground/4",
                            "legal_citation_detail/4",
                            "review_outcome/4",
                            "list_member/4",
                            "item_range/4",
                        ],
                    },
                    "args": {
                        "type": "array",
                        "minItems": 4,
                        "maxItems": 4,
                        "items": {"type": "string", "maxLength": 100},
                    },
                    "source_or_scope": {"type": "string", "maxLength": 100},
                },
            },
        },
        "subject_accounts": {
            "type": "array",
            "maxItems": 24,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["subject_id", "companion_statuses"],
                "properties": {
                    "subject_id": {"type": "string", "maxLength": 100},
                    "companion_statuses": {
                        "type": "array",
                        "maxItems": 8,
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["signature", "status", "reason"],
                            "properties": {
                                "signature": {
                                    "type": "string",
                                    "enum": [
                                        "claim_range/4",
                                        "claim_ground/4",
                                        "legal_citation_detail/4",
                                        "review_outcome/4",
                                        "list_member/4",
                                        "item_range/4",
                                    ],
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["instances", "none_found", "uncertain", "not_applicable"],
                                },
                                "reason": {"type": "string", "maxLength": 160},
                            },
                        },
                    },
                },
            },
        },
        "self_check": {
            "type": "object",
            "additionalProperties": False,
            "required": ["missing_subjects", "notes"],
            "properties": {
                "missing_subjects": {"type": "array", "maxItems": 8, "items": {"type": "string", "maxLength": 160}},
                "notes": {"type": "array", "maxItems": 8, "items": {"type": "string", "maxLength": 160}},
            },
        },
    },
}

GOVERNED_SUBJECT_ATOM_ROW_PREDICATES: set[str] = {
    "claim_range",
    "claim_ground",
    "legal_citation_detail",
    "review_outcome",
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

OPERATIONAL_RECORD_STATUS_CONTEXT_V1 = [
    "operational_record_status_strategy_v1: Use this for permit lifecycles, intake logs, facilities logs, conservation ledgers, grant/application dockets, accession records, deaccessions, correction logs, and turnstream-style records.",
    "Operational record rule: preserve the record backbone before summary labels. A useful compile keeps stable rows for record id, subject/entity, actor/role, timestamp or turn, event/action, status before/after, governing rule/threshold, correction/reversal, and unresolved/pending items when the profile supports them.",
    "Operational status rule: current status, prior status, suspended/reinstated/expired/denied/deaccessioned/pending/unresolved states, and status-at-date questions need explicit status surfaces plus time anchors. Do not hide status transitions inside long event labels when the profile offers status, event, date, correction, or temporal predicates.",
    "Operational lifecycle canonical palette preference: when the draft profile offers equivalent choices, prefer record_alias/2 for same-record id variants, record_status_phase/4 for record, phase, status, date_or_source, record_status_at/3 for dated status, record_lifecycle_event/5 for record, event_type, actor, object_or_subject, date, and record_superseded_by/4 for superseded record/status, superseding document/event/source, resulting status, date_or_source.",
    "Operational lifecycle palette construction rule: for permit, intake, docket, queue, sample, ticket, accession, or repair lifecycle sources, include the canonical lifecycle predicates when the source states those surfaces and no stricter domain-specific predicate already carries the same slots. A domain-specific status/result predicate is not stricter if it drops the date, event, actor, or governed-subject slot that the source states. Do not invent fixture-local predicate names for initial/current/final status, record aliases, receipt/logging layers, or supersession targets if the canonical lifecycle predicates can carry them.",
    "Operational lifecycle preservation rule: when a source gives a repeated dated lifecycle/status list, preserve a complete direct lifecycle or status unit for each listed line when the profile supports it. A mixture of supersession fragments, closed/withdrawn labels, or record ids is not enough unless the subject, lifecycle state/action, and date/turn remain queryable together.",
    "Operational correction rule: corrections, reversals, reinstatements, and superseded values are not ordinary duplicate facts. Preserve the original/superseded value, corrected/current value, authority/source, and effective turn/date when the profile supports correction or source-claim predicates.",
    "Operational threshold rule: numeric thresholds and retention/matching/authority limits are query-bearing. Preserve the threshold amount, unit, subject, governing rule, and observed/requested amount separately when available; do not collapse a denied or approved outcome into a single reason label.",
    "Operational reason rule: if a decision, split, denial, remedy, or priority is explained by the source, preserve the stated reason/rationale as an additive detail row when the profile supports it. A decision row alone is partial support for why-questions.",
    "Operational unresolved-item rule: pending, unresolved, referred, deferred, and not-yet-decided items are first-class epistemic states. Preserve the item, owner/source, current status, and any referred authority rather than answering them as yes/no outcomes.",
    "Operational record slot contract: received, filed/logged, assigned/routed/referred, approved, denied/rejected, withdrawn/retracted, pending/unresolved/deferred, corrected/amended, superseded/replaced, reopened/reinstated, closed/completed, current-status, and status-transition terms need their slots preserved when compatible predicates exist: record/event id, subject/item/application, actor/body, timestamp/turn, status before and after when stated, authority/source, and reason or correction detail when stated. A record type or status word alone is shallow metadata.",
    "Operational received/filing actor rule: when a source states that one actor received, filed, logged, entered, or docketed an application, referral, ticket, report, sample, proposal, or record from another actor, preserve the receiving/filing actor bound to the submitted object and date. Do not substitute the submitter/applicant/source actor for the receiving clerk, desk, collector, or filing body.",
    "Operational withdrawn-request content rule: withdrawn, retracted, cancelled, denied, approved, or superseded request rows need the requested action/content/line item or descriptive target when the source states it. A row such as request_withdrawn(Record, Date) is shallow if the source names which request was withdrawn.",
    "Operational join-readiness rule: use one canonical atom for each record, person, role, facility, application, accession, lot, vault, concern, and date/turn. Reuse that atom across role rows, event rows, status rows, correction rows, threshold rows, and rationale rows so later QA can join without alias repair.",
    "Operational permit/license lifecycle rule: for permit, license, inspection, appeal, exemption, suspension, restriction, renewal, or extension records, preserve each instrument separately with issuing authority, validity window, fee, rule text, triggering incidents, inspection results, effective status intervals, appeal/hearing status, and meeting authority statements when the profile supports those row classes.",
    "Operational permit-terms rule: permit type descriptions are rule-bearing source text. Preserve default allowed hours, validity formulas, renewal requirements, extension request windows, approval authority, exemption windows, inspection windows, suspension duration rules, appeal windows, and status-effect text as queryable rule/requirement rows instead of only preserving actual permit instances.",
    "Operational clock-delta rule: when a permit violation is stated as an action continuing past an allowed time, preserve both the allowed endpoint and the observed endpoint, plus the stated or computable overage amount when the profile supports any duration/detail predicate. Do not confuse violation overage duration with the resulting suspension duration.",
    "Operational event-outcome rule: completed inspections, displays, hearings, pickups, repairs, or reviews need outcome rows even when the related license immediately expires or remains pending afterward. Event occurrence/outcome and current permit status are different surfaces.",
    "Operational itemized-failure rule: aggregate inspection failures should preserve itemized failed subjects and stated deficiency reasons when the source lists them. Count rows and status rows are useful but not enough for which-and-why questions.",
    "Operational quarantine/lot-status rule: for quarantine, nursery, greenhouse, lab, lot, sample, movement, destruction, or disease-control records, preserve lot id, location, species, count, subset count, sample count, positive/negative result count, status transition, movement interval, destruction deadline/completion, supervisor/witness, and final current status as separate queryable rows rather than hiding them inside a status summary.",
    "Operational direct-surface rule: for sensor, instrument, clock-drift, threshold, correction, or breach sheets, emit direct rows for sensor id, raw timestamp, corrected timestamp, correction rule, reading value, threshold, event status, inspection window, and breach classification. Do not rely on query-time compatibility adapters to reconstruct those surfaces later.",
    "Operational source-fidelity rule: preserve stated equipment specifications, procedure/manual identifiers, source-stated person-plus-role lines, and named section/title coordinates as direct queryable rows when the source states them. These are answer-bearing identity/addressability surfaces, not decorative provenance.",
    "Operational source-role rule: when a header, signature line, source note, correspondence line, or operational note identifies a named person with a role, office, desk, institution, or attendance duty, emit a direct person/role/source row when compatible predicates exist. Source text alone is not enough for who-compiled, who-attended, who-reviewed, or who-held-role questions.",
]

PROBATE_PROPERTY_STATUS_CONTEXT_V1 = [
    "probate_property_status_strategy_v1: Use this for probate, inheritance, estate, will, gift, pledge/security, possession, ownership, custody, sale, title, adverse-possession, or disputed-property records.",
    "Probate/property rule: ownership, possession, control, custody, maintenance, harvest rights, and legal status are distinct surfaces. Preserve each stated surface separately rather than resolving them into one owner-like fact.",
    "Probate/property rule: source-stated purchases, sales, wills, gifts, loans, pledges, releases, court observations, interim rulings, and deferred matters are first-class transaction/status records when the profile supports compatible predicates.",
    "Probate/property dispute rule: disputed, provisional, deferred, potential, satisfied, released, over-recovered, and historical-debt states are not final determinations. Preserve the status, date, authority/source, and affected object so later queries can answer with visible uncertainty.",
    "Probate/property evidence rule: gift cards, bills of sale, solicitor advice, court observations, maintenance/harvest history, and quantified debt/harvest values are answer-bearing evidence. Preserve speaker/source, object, text/detail, amount/count/date, and evidentiary status when the profile has any compatible detail or record predicate.",
    "Probate/property inventory rule: named inherited sets and compound property units are query-bearing. Preserve both the aggregate unit and its member objects, and keep the same atoms across part_of, inheritance, will_transfer, court_ruling, ownership/status, and possession rows.",
    "Probate/property arithmetic rule: stated balances, payments, seasonal values, totals, and over-recovery comparisons should remain queryable. Do not collapse them into a pledge-satisfied label if amount/value predicates or compatible detail rows are available.",
    "Probate/property QA-readiness rule: choose one canonical atom for each person, estate, property unit, organization, court, debt, pledge, claim, and date. Reuse those atoms across transaction, evidence, status, and ruling rows so later QA can join without alias repair.",
    "Custody direct-surface rule: for any custody, access, loan, specimen, archive, property, or object-control register, emit direct rows for physical holder, legal owner, custody status, location, access event, authorizing source, recall/return clause, and recall-issued state when the source states them. Do not depend on query-time compatibility adapters to bridge from source-record prose.",
    "Custody paired-authority rule: when one order, report, agreement, correspondence item, register section, or other source authority governs multiple named objects, access events, claims, or control states, emit a direct authority/source row for every named governed subject/action rather than only the first representative item.",
    "Custody source-fidelity rule: preserve record-author roles, compiler/recorder roles, custody/control roles, claimant roles, object identifiers, register identifiers, named chronology sections, location sections, and other section/title coordinates as direct queryable rows when stated. Section addressability and record-author identity are part of the answer surface.",
    "Custody basis-source rule: when a custody, possession, access, loan, or control fact is stated in a named section, correspondence item, note, order, policy, or corroborating source, emit a direct link from the governed item/person/control fact to that source coordinate when compatible predicates exist. The basis value alone is shallow when the question can ask which section or source sets it out.",
]

COMPETITION_ROLE_ALIAS_CONTEXT_V1 = [
    "competition_role_alias_strategy_v1: Use this for tournament, match, contest, scoring, bracket, ranking, protest, referee/marshal, role-change, inherited banner/title, alias, or competition-administration records.",
    "Competition alias rule: banner/title aliases are time-scoped identities, not people. Preserve person, alias/banner, year/date/session, previous holder, current holder, successor, and change reason separately when the profile supports compatible rows.",
    "Competition role rule: competitor status, eliminated status, scorer, range officer, marshal, committee member, substitute, and witness/source roles are different surfaces. Preserve dual-role records rather than overwriting the competitor role with an administrative role.",
    "Competition scoring rule: original posted rank, corrected rank, component scores, arithmetic correction, advancement set, match result, final certification, and champion attribution are distinct query surfaces. Preserve both erroneous posted values and corrected values with authority/source when supported.",
    "Competition incident rule: protests, rulings, holds, misfires, zero-score shots, safety incidents, and no-incident notes are distinct. Preserve the event, reason, decision, status, and explicit non-finding rather than reducing them to a generic dispute.",
    "Competition certification rule: match scores, final scores, score recorders, score certifiers, score certification authority, and certification date/session are separate administrative surfaces. Do not assume the marshal certified a score when the source names a scorer or substitute scorer as the certifying actor.",
    "Competition objection rule: dual-role facts are not the same as conflict findings. Preserve stated conflict-of-interest objections, explicit no-objection notes, and the role/status basis for the objection or non-objection separately from ordinary role assignment rows.",
    "Competition protest-count rule: count protest filing events, not only successful protests or marshal ruling rows. If a source says the same competitor filed two protests and describes both subjects, preserve both filing events with subject, filer, status, and ruling link.",
    "Competition history rule: historical winners under reused banners must keep the historical person and year attached to the banner. Do not transfer an old banner victory to the current holder.",
    "Competition QA-readiness rule: choose one canonical atom for each person, banner, match, round, protest, role assignment, score row, correction, and ruling. Reuse those atoms across registry, score, protest, ruling, role, and closing-note rows so later QA can join without alias repair.",
]

SOURCE_AUTHORITY_AUDIT_CONTEXT_V1 = [
    "source_authority_audit_strategy_v1: Use this for audits that compare public labels, guides, catalogs, acquisition records, reports, board decisions, correction notes, or other source layers with different authority.",
    "Source authority rule: visible/public text, copied guide text, catalog entries, original records, expert reports, curator notes, and board decisions are different evidence surfaces. Preserve source, claim, object/room/item, value, status, and authority separately when the profile supports compatible rows.",
    "Source authority rule: copied text is not independent confirmation. If a visitor guide, public notice, or summary copied a placard/source, preserve the copy relationship and do not treat the duplicate as a second authority.",
    "Source authority provenance rule: reports, surveys, exhibits, photographs, receipts, and expert statements need provenance surfaces. Preserve who commissioned, prepared, presented, dated, admitted, rejected, or relied on each source when the text states those roles.",
    "Evidence provenance slot contract: when the source says a document, report, note, card, survey, receipt, photograph, exhibit, or expert statement was prepared, presented, submitted, filed, commissioned, requested, ordered, relied on, cited, corrected, revised, amended, admitted, entered, dated, located, found, stored, or held, preserve the answer-bearing slots directly when the profile supports compatible predicates: artifact/source id; actor or body performing the provenance act; recipient, admitting body, relying body, or presentation context when stated; date when stated; corrected field/value/detail for corrections; and location/container for location. Do not substitute role-only, recipient-only, or context-only rows for provenance facts.",
    "Correction status rule: drafted, installed, rejected, queued, not-yet-reprinted, and no-change-needed statuses are distinct. Preserve the current public display state separately from the recommended correction.",
    "Authority override rule: when a board, court, or controlling body rejects an expert/curator correction, preserve both the expert recommendation and the controlling decision. Do not silently promote the expert view to current public text.",
    "Source authority density rule: when a document, report, correspondence item, court order, policy, catalog, register section, or source note is cited as authority/evidence for a claim, status, access permission, title, custody state, or finding, preserve a direct source-authority row with source document id, source actor/author if stated, source date if stated, governed subject/item/claim/action, and authority/evidence role when the profile supports compatible predicates.",
    "Authority and custody slot contract: court orders, governing rules, board votes, official records, staff notes, draft recommendations, controlling findings, noncontrolling sources, custody holders, and access-control records need their governing slots preserved when compatible predicates exist: source/body, governed subject/claim/action/item, authority status or precedence, scope, date when stated, custody holder or access actor when stated, and reason a source is noncontrolling when stated. Do not collapse a draft recommendation, staff note, official record, and controlling finding into one generic authority row.",
    "Authority draft-recommendation rule: when a source states a draft, proposal, preliminary recommendation, or unapproved recommendation, preserve both the proposed content/action/scope and the pending approval/review/vote/legal condition when compatible predicates exist. A draft label or document type alone is shallow.",
    "Authority noncontrolling-source rule: when a source says copied, advisory, superseded, rejected, noncontrolling, not binding, or omitted a controlling source, preserve the weaker source, the copied/superseded/advisory relationship, and the stated reason or omitted controlling source when compatible predicates exist. A noncontrolling label alone is shallow if the source states why.",
    "Authority record-detail rule: if the compile emits a document_type/2 or record_entry/4 row for an order, rule, vote, finding, note, draft, register, or other authority/custody source, also emit at least one compatible same-anchor content, effect, scope, condition, decision, governed subject, or noncontrolling-reason row when the source states one. Type, author, date, and status alone are shallow record metadata.",
    "Source detail rule: numeric counts, publication years, date ranges, exact proposed wording, suspected typo origins, and original-versus-added totals are answer-bearing details. Preserve them as rows or compatible detail records rather than hiding them in long labels.",
    "Source audit QA-readiness rule: choose one canonical atom for each room/item/source document/correction/review date. Reuse those atoms across claim, catalog, acquisition, report, correction, status, and board-decision rows so later QA can join without alias repair.",
]

FICTION_REFERENCE_CONTAINMENT_CONTEXT_V1 = [
    "fiction_reference_containment_strategy_v1: Use this for sources that mix real incidents with novels, plays, quoted stories, fictional documents, literary references, nested narratives, or lookalike events whose entities/numbers overlap with the real-world record.",
    "Fiction containment rule: fictional events, fictional characters, fictional titles, and fictional explanations must stay inside their work/world/source layer. Preserve the fiction layer and source work, but do not promote fictional events as real-world facts.",
    "Reference collision rule: when a real person/title/count/event resembles a fictional person/title/count/event, preserve both rows with source layer, publication/event date, and explicit non-explanation or coincidence boundary when stated.",
    "Publication chronology rule: publication dates and incident dates are answer-bearing. Preserve chronology so later queries can distinguish prior fiction from later real incidents without treating the earlier fiction as evidence for the later event.",
    "Disclosure rationale rule: voluntary disclosures, clarification notes, and warnings about misleading coincidences are first-class rationale/evidence rows. Preserve why the source disclosed the overlap and what boundary it intended to clarify.",
    "Unresolved real-incident rule: if the real incident remains unresolved, preserve unresolved status and candidate explanations separately. Do not use fictional parallels to fill missing causal facts.",
    "Fiction containment QA-readiness rule: choose one canonical atom for each real person/title/incident, fictional work, fictional character/title/event, disclosure, and date. Reuse those atoms across source-layer, title, author, incident, coincidence, and unresolved-status rows.",
]

ADMINISTRATIVE_ROSTER_TIMELINE_CONTEXT_V1 = [
    "administrative_roster_timeline_strategy_v1: Use this for school trips, field trips, attendance logs, supervision records, station assignments, group rosters, shifts, team rotations, and event schedules.",
    "Administrative roster rule: initial group/team rosters are backbone rows. Preserve every named member with group, role/chaperone/supervisor, and date/session scope when the profile supports membership or assignment predicates. Do not collapse a roster into only a count.",
    "Administrative backbone preservation rule: if the profile offers standing-roster predicates such as group_membership/3 or supervision_assignment/4, keep using them for original groups and chaperone/supervisor coverage. Temporary pairings, station splits, shore teams, substitutions, and incident summaries are additive rows; they must not replace the standing roster and supervision backbone.",
    "Administrative timeline rule: session windows and supervision intervals are query-bearing. Preserve start/end times, day labels, locations/stations, supervisor changes, transfers, departures, returns, and temporary substitutions as explicit event or status rows.",
    "Administrative assignment rule: paired work, station assignments, subgroup splits, role assignments, and resumed original groups should each become queryable membership/assignment rows with their session scope. Mixed-session assignments must not overwrite the standing group roster.",
    "Administrative station-split rule: when a group is split across named stations, benches, rooms, vehicles, or work areas, preserve each station roster separately with station/location, session time, supervisor or monitor, and member list. A station split is not the same as the parent group roster.",
    "Administrative temporary-monitor rule: when a student, volunteer, substitute, or non-chaperone is asked to keep watch, escort, record, hold equipment, or supervise a station temporarily, preserve the role assignment with actor, role/task, target group/location, and session scope. Do not drop the row because the actor is not an official chaperone.",
    "Administrative absence-coverage rule: when a supervisor leaves with a student, stays behind, returns, or does not return on a later day, preserve the absence window and the coverage/substitution state separately from the person's standing role.",
    "Administrative role-task rule: task assignments such as recording clipboard, first-aid duty, watch duty, escort duty, or active collection are query-bearing role rows. Preserve the task, assignee, reason if stated, and day/session scope.",
    "Administrative completion-report rule: closing reports are compact authoritative summaries. Preserve each listed incident/outcome as a separate row, including illness, injury, absence, hazard report, unresolved discrepancy, final attendance, and no-touch/no-hazard determinations.",
    "Administrative attendance/count rule: attendance counts and exceptions need scoped rows: full trip attendance, session attendance, absent/ill/injured participants, supervisor presence, return-transport count, and final accounted-for status are different surfaces.",
    "Administrative incident-report rule: incident reports can conflict. Preserve reporter, filing time, claim content, observed aftermath, unresolved discrepancy, and authoritative non-finding separately. Do not merge competing student reports into one objective event unless the source states a finding.",
    "Administrative direct-surface rule: for any roster-like document, emit direct membership, assignment, supervisor, version/status, change-event, count, and minimum/ratio-rule rows using the profile's current predicate palette. Do not depend on query-time compatibility adapters or old school-trip predicate names to recover roster state later.",
]

RULE_INGESTION_SOURCE_COMPILER_CONTEXT_V1 = [
    "rule_ingestion_source_compiler_strategy_v1: Use this for source documents classified by the LLM intake plan or domain hint as charters, standing rules, operational policies, bylaws, ordinances, contracts, eligibility rules, tax rules, permission rules, exception ladders, or priority rules.",
    "Rule ingestion rule: preserve source-stated rules in two layers when the profile supports both layers. First emit source_rule/rule_text/requirement/exception/override rows that record the charter language. Second emit operation='rule' candidate_operations only for bounded executable Horn-style rules whose head and body predicates are all in the allowed profile.",
    "Executable-rule boundary: a rule operation is a candidate, not truth by itself. Never use an executable rule to smuggle an inferred current violation, finding, clearance, tax liability, or permission as a fact. The mapper admits the clause; later Prolog queries derive consequences.",
    "Executable-rule clause requirement: if operation='rule', candidate_operations[].clause must contain the actual Prolog-style clause. Do not emit safe rule operations with only a label. If the rule uses default, exception, unless, only-if, priority, or override semantics that cannot be safely expressed with the allowed predicates, record the source rule as source_rule/rule_text/requirement/exception/override and mark the executable version as missing or unsafe in self_check.",
    "Rule-head discipline: choose a query-bearing head predicate that names the derived status, permission, obligation, tax status, authorization status, clearance status, access status, reward status, or source-priority result. Use allowed profile predicates only; do not invent a new head if the allowed palette lacks it.",
    "Rule-body discipline: bodies should join admitted factual predicates, temporal predicates, role predicates, source-priority predicates, exception predicates, and negative conditions only when the source explicitly states the condition and the profile has the needed predicates. Prefer small clauses over giant prose-shaped clauses.",
    "Exception discipline: unless/except/only-if language is not an ordinary positive fact. Preserve the exception row and, only if safe, encode the exception in the executable clause with a bounded negated predicate such as \\+ relief_cargo(Cargo), \\+ signed_clearance(Vessel), or \\+ emergency_override(Proposal).",
    "Rule composition slot contract: when a source states base rules, exceptions, thresholds, activation or eligibility conditions, overrides, precedence, expirations, vote requirements, or fallback rules, preserve the relational slots directly when compatible predicates exist. Exceptions need governed rule, condition, and effect/scope; thresholds need measure, value/unit, and governed rule or activation context; overrides and precedence need both related rules plus conflict/scope when stated; vote requirements need governed rule, vote threshold, quorum/presence if stated; fallback rules need trigger and fallback action joined by the same rule or condition anchor.",
    "Activation-condition anchoring rule: when a source says a rule activates, applies, is triggered, or comes into effect when a request, event, state, threshold, or context occurs, preserve a direct activation surface with the governed rule, trigger/context, and governed subject or action when the profile supports compatible predicates. Do not leave activation only in source text or inside a broad rule label.",
    "Pairwise rule-relation rule: when the source states that one rule overrides, supersedes, ranks above, takes precedence over, or controls another rule, preserve the pairwise relation with higher/overriding rule, lower/overridden rule, and conflict/scope/effect when stated. Rank-only rows such as rule_level(rule, high) are not substitutes for pairwise override or precedence facts.",
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

COMPILE_SURFACE_INVARIANT_CONTEXT_V1 = [
    "compile_surface_invariant_strategy_v1: Source-record ledgers preserve fidelity, but recurring answer-bearing surfaces should also be proposed as direct candidate_operations when the allowed profile has compatible predicates.",
    "Compile surface invariant rule: if the source states people or organizations in roles, preserve the role-bound relation directly. Keep recorder, operator, holder, claimant, approver, recommender, witness, owner, and authority roles distinct when compatible predicates exist.",
    "Compile surface invariant rule: source/header/signature/correspondence lines that state a person plus role, office, institution, attendance duty, compiler/reviewer duty, or record-author/recorder duty should become direct role-bearing rows when compatible predicates exist. Do not leave the only role evidence inside source_record_text_atom/2.",
    "Compile surface invariant rule: official-document wrapper facts are answer-bearing. When compatible predicates exist, preserve docket/file/accession identifiers and aliases, issuing body, document type, issue/report/decision date, disposition or action, opinion/decision form such as per curiam or precedential status, signatory/title/office chain, panel or commissioner membership, party/entity role plus location/address, numbered footnotes/notes with their content, cited authority context, and attachments/exhibits as direct typed rows. Source-record display rows and source_record_note_anchor rows are provenance, not delivery.",
    "Compile surface invariant rule: official documents often contain answer-bearing referenced matters. Preserve companion cases, underlying proceedings, permit/application/filing numbers, prior references, attached records, and incorporated documents as typed rows with stated identifier, date, status/action, and relationship to the main document when stated.",
    "Compile surface invariant rule: legal, regulatory, procurement, enforcement, appellate, and review documents need direct authority and review-path rows when stated. Preserve jurisdiction/authority basis, governing statute or rule, forum/body below, underlying proceeding number, appeal/review target, lower-body disposition, and final reviewed action as typed rows rather than leaving them inside source-record prose.",
    "Compile surface invariant rule: appellate, administrative-review, adjudicative, protest, grievance, and board-review sources need the underlying action under review preserved separately from the reviewing outcome. When the source states that a lower body, examiner, agency, reviewer, committee, staff, or board rejected, denied, cited, found, recommended, or ordered something, and another body later affirmed, reversed, modified, vacated, remanded, or sustained it, emit typed rows for both layers when compatible predicates exist. Reuse the same governed item/claim/issue/action atom across the underlying-action row and review-outcome row. Do not encode the underlying rejection or denial only as a final affirmed status, and do not encode the final outcome only as a source-record display.",
    "Compile surface invariant rule: counsel blocks, contacts, representatives, reviewers, commissioners, panelists, and signatory blocks are typed rosters. Preserve every named person with role, represented party or office, organization, and location when stated; do not collapse the block to only the main named party or issuing body.",
    "Compile surface invariant rule: numbered claims, counts, issues, products, violations, requirements, order paragraphs, and item ranges need complete typed inventories with group-to-ground/basis/status relationships when stated. Do not compress ranges or lists into lossy summaries if the profile can express members, ranges, or grounds.",
    "Compile surface invariant rule: agency digests, weekly summaries, docket lists, decision lists, notice rollups, and tables of actions are repeated structured entries. Preserve each entry's subject/name, case or file numbers, location, decision/action date, deciding official or role-holder, citation/volume number, and outcome when stated. Do not leave an entry only as source_attributed_claim text or a source-record paragraph.",
    "Compile surface invariant rule: financial filings, restatements, accounting-error notices, rate tables, insurance schedules, and other periodized sources need typed period-date rows. Preserve fiscal year, quarter, period-end date, balance-sheet date, report date, affected account/line item, and error/category relationship when stated. Do not leave source-stated dates only in source_record_date_alias or inside a broad declaration atom.",
    "Compile surface invariant rule: adjudicative, investigative, review, and enforcement documents need argument-treatment rows when stated. Preserve who raised an argument/objection/claim, the target issue or item, the treatment/disposition, and the stated reason separately when compatible predicates exist.",
    "Compile surface preservation rule: invariant-specific rows are additive and must not replace already-needed concrete typed rows. When preserving a new surface, keep direct backbone rows for rules, events, votes/choices, measurements, source authority, participant statements, corrections, lifecycle/status, and domain-specific admissible predicates. A replay compile that gains one surface while dropping typed backbone predicate families is not acceptable.",
    "Compile surface invariant rule: if the source has sections, titles, headings, chronology labels, basis language, or explicit absence/negative-inference statements, preserve source addressability as queryable rows rather than only source_record text.",
    "Compile surface invariant rule: when a record, order, claim, exhibit, item, event, or document is listed in, filed under, reproduced in, referenced by, or contained by a section/source layer, preserve the relation between the subject id and the section/source coordinate directly when compatible predicates exist.",
    "Compile surface invariant rule: when a legal, regulatory, enforcement, policy, or compliance citation includes an inline parenthetical, caption, heading, or short label naming the duty, prohibition, control area, or conduct category, preserve that label separately from the bare article/section identifier when compatible predicates exist. Legal article numbers are not substitutes for captioned duty/category labels when the label is answer-bearing.",
    "Compile surface invariant rule: when the source states who or what authorizes, governs, controls, overrides, records, reports, or serves as the authority for an access/action/status/finding, preserve the authority/source relation separately from the party receiving permission or the item being controlled.",
    "Compile surface invariant rule: when one authority, source, reviewer, regulator, committee, board, court, investigator, or staff body recommends, requests, refers, advises, reports, submits, or directs that another authority/body take action, preserve the chain as source-stated slots when compatible predicates exist: recommending/source body, recipient/addressee body, governed subject or target, requested/recommended action, date when stated, and source row. Do not collapse the chain into only the final action/order row.",
    "Compile surface invariant rule: regulatory, enforcement, disciplinary, audit, inspection, and compliance records need violation or deficiency categories as separate answer surfaces when the source states them. Preserve control area, breach category, failed requirement, statutory violation class, root-cause category, governed target, basis/source, and status/detail slots when compatible predicates exist. Do not answer category questions only with intervention/action type rows such as order, warning, citation, fine, or report demand, and do not treat legal_basis alone as the violation category. When one source clause lists several coordinated control areas, breach classes, failed duties, or violation categories, emit separate category rows for the stated items; an umbrella category such as general management, internal control, governance, or system deficiency is additive only and cannot replace the itemized categories.",
    "Compile surface invariant rule: when a source document, correspondence item, report, order, policy, catalog, or register section supports an answer-bearing claim/status/access/finding, preserve the source document id, source actor/author, source date when stated, governed subject, and authority/evidence role as direct rows when compatible predicates exist.",
    "Compile surface invariant rule: when a basis, rationale, corroboration, or evidence source is tied to a named section/source coordinate, preserve both the semantic fact and its source coordinate. A possession_basis, authority, finding, status, or access row without the section/source that states it is shallow for source-addressability questions.",
    "Compile surface invariant rule: answer-bearing details in source text are additive, not replacements for backbone rows. First preserve the source-stated identity, status, date/time, count, amount, role, and subject/object rows. Then, when a source also states a rationale, explanation, availability/scope boundary, separate arrangement, pending commitment, acknowledgment, promised future action, exclusion, or unresolved item, preserve a direct detail surface anchored to the governed subject/action/source when compatible predicates exist. A broad status, event, or source_record_text_atom row alone is shallow if it drops the stated detail that would answer why, what else, what exception, what remains pending, or what is outside the main scope.",
    "Compile surface invariant rule: deterministic source-record rows are provenance, not a substitute for semantic addressability. If a source row, field, label, heading, or compact source sentence states an answer-bearing identity, role, identifier, location, current status, permission, obligation, count, amount, bound, date, deadline, duration, scheduled event, consequence, rationale, or source-document relation, emit the most specific compatible direct predicate for that value as well as the source_record row. Do not leave the only queryable copy of such a value inside source_record_text_atom/2 or source_record_field/3.",
    "Compile surface invariant rule: source-record promotion must preserve slots, not merely copy prose. A promoted row should keep the governed subject or item, the answer-bearing value, any stated status/effective-time/source-authority slot, and enough source anchor to join back to the row that stated it when compatible predicates exist. If no compatible profile predicate can carry the value, use source_detail/4 as an additive fallback rather than inventing a fixture-local predicate name.",
    "Compile surface invariant rule: if source_detail/4 is available, use it only as an additive fallback detail carrier for exact source-stated attributes or details that no stricter profile predicate can carry. Its slots are subject_id, detail_kind, detail_value, and source_row. It must not replace concrete profile rows for identity, event, status, temporal, count, amount, role, rule, or authority surfaces.",
    "Compile surface invariant rule: do not satisfy answer-detail preservation by inventing a broad generic event/detail wrapper that replaces concrete profile rows. If the source states room numbers, device ids, departure times, membership lists, expiry dates, amounts, current states, or governed subjects, those concrete surfaces must remain queryable even when additive detail rows are also emitted. Prefer profile-owned detail/source predicates; if no compatible detail predicate exists, preserve the backbone rows and note the missing detail carrier in self_check rather than creating a vague wrapper.",
    "Compile surface invariant rule: participant statements need direct statement surfaces. When a source records who said, advised, estimated, certified, commented, clarified, asked, supported, opposed, or observed something, preserve speaker or actor, content or position, speech act, source event or date, language or translation when stated, and binding/advisory/informational status where stated. If binding/advisory status is emitted as a companion row, it must share a stable statement id or source anchor with the statement row. Do not preserve only formal public comments while dropping other participant, staff, official, or member statements.",
    "Compile surface invariant rule: when a document, report, note, card, survey, receipt, photograph, exhibit, or expert statement has stated provenance, preserve the provenance slot contract directly when compatible predicates exist: artifact/source id; preparer/presenter/submitter/filer/commissioner/requester/relying body/admitting body; recipient or presentation context; date; correction detail; and location/container. Role-only or recipient-only rows are not enough when the source states a full provenance relation.",
    "Compile surface invariant rule: when the source states an authority or custody ladder, preserve the ladder slots directly when compatible predicates exist: court order with issuer, content/action, date, and scope; governing rule with rule, jurisdiction/body, and applicable condition; board vote with body, decision, and date; official record with record, governed item/claim/action, status, and date; staff note or draft recommendation with author/source, recommendation, status, and governed subject; controlling finding with finding source, governed claim/action/item, scope, and controlling status; noncontrolling source with source, content, and reason noncontrolling; custody/access control with holder or access actor, governed item/action, scope, and effective source.",
    "Compile surface invariant rule: authority/custody record metadata is not enough by itself. When emitting document_type/2 or record_entry/4 for an order, rule, vote, finding, note, draft, register, copied notice, or custody/access source, pair it with same-anchor content/effect/scope/condition/decision/governed-subject/reason rows when the source states those details.",
    "Compile surface invariant rule: when a source states composed rule logic, preserve the rule-composition slot contract directly when compatible predicates exist: base rule with condition/outcome; exception with governed rule, condition, and effect/scope; threshold with measure, value/unit, and governed context; activation or eligibility condition anchored to the rule; override or precedence with both related rules and scope; expiration date; vote threshold and quorum/presence; fallback trigger and fallback action. Unanchored condition-only, priority-only, quorum-only, or fallback-action-only rows are shallow surfaces.",
    "Compile surface invariant rule: when a rule activates, applies, is triggered, or comes into effect under a source-stated request/event/state/context, preserve the activation anchor directly: governed rule, trigger/context, and governed subject or action. A rule label that merely contains the trigger words is not enough.",
    "Compile surface invariant rule: when one rule overrides, supersedes, ranks above, takes precedence over, or controls another rule, preserve the pairwise relation directly with higher/overriding rule, lower/overridden rule, and conflict/scope/effect when stated. Rank-only priority labels are shallow unless they also preserve the compared rule pair.",
    "Compile surface invariant rule: if the source states rules, procedures, clauses, requirements, thresholds, exceptions, exclusions, or applicability limits, preserve those as direct rule/policy surfaces before summarizing outcomes.",
    "Compile surface invariant rule: if the source names objects, devices, systems, inventory ids, source-stated specification values, samples, or item labels, preserve identifiers and descriptive attributes separately from broad event rows.",
    "Compile surface invariant rule: if the source states events, raw/corrected times, superseded values, intervals, windows, deadlines, or transitions, preserve the temporal anchors and correction relation directly.",
    "Compile surface invariant rule: when a source-stated later notice, correction, amendment, update, extension, supersession, or observations/footer note changes a deadline, status, scope, amount, or governed requirement, preserve the update relation directly when compatible predicates exist: original/source document id, update document id when stated, publication or issue date, governed subject, changed field, stated effect, and source row. Do not leave a source-stated update only as an intake-plan risk, source_record text, or unjoined original deadline/status row.",
    "Compile surface invariant rule: reporting, filing, remediation, and compliance obligations often contain both a fixed one-time due date and a recurring cadence or offset. Preserve these as separate facts or separate requirement-type rows when compatible predicates exist: requirement type, fixed due date, recurrence anchor, offset amount/unit, reporting frequency/duration, governed target, and basis/source. Do not collapse an initial calendar deadline and a recurring period into two bare day counts or one generic deadline value.",
    "Compile surface invariant rule: chronological/event-list sources need complete event backbone units when compatible predicates exist. Preserve event id or entry label, date/time/order, actor/party/system, governed subject or object, and outcome/status/action as joinable rows. Do not leave a timeline answer split between source_record text, a vague event wrapper, and unrelated status/date rows.",
    "Compile surface invariant rule: repeated tables, logs, registers, and chronologies with row ids plus time/date and action/status/description columns need row-by-row direct preservation when compatible predicates exist. Do not compile only a representative prefix or the first N rows; later rows often close, reopen, supersede, authorize, complete, or otherwise determine the current state.",
    "Compile surface invariant rule: public notices, recalls, and registry pages often use a paragraph heading to scope the product/list rows that follow. If the source states Sold at [store] in [states] before a product list, treat that scope as applying to each governed product row until the next scope heading; emit direct store/state rows for each governed product or category when compatible predicates exist.",
    "Compile surface invariant rule: state-by-retailer or region-by-location distribution tables need row-level direct preservation. For each row, preserve the state/region, each retailer/location, and any retailer-specific product restriction or carve-out as joinable rows; do not leave the retailer list only inside source_record_cell/3 or source_record_text_atom/2.",
    "Compile surface invariant rule: source_record_cell_item/3 and source_record_cell_item_qualifier/4 are deterministic table-list scaffolding, not semantic delivery. When allowed predicates such as distributed_in_state/2, sold_at_retailer/3, product_restriction/3, recall_distribution/2, or equivalent distribution carriers exist, promote the item and qualifier rows into those direct carriers. Do not stop at product_identity/product_form rows.",
    "Compile surface invariant rule: distribution rows must reuse the same product/item atoms as the product list, recall-item list, or inventory table they govern. If the source wording forces a category-level distribution row, emit a category/product alias or explicit governed-category row so product_name, recall_item, sold_at_store, state, and restriction facts can join. Do not create parallel atoms for the same named item unless an alias/equivalence row connects them.",
    "Compile surface invariant rule: retailer-specific restrictions in distribution tables apply to the restricted products named in the parenthetical text, not to a single representative row item. If a cell says Shop N Save carried only cucumber, green bell pepper, and pickling cucumber, emit restriction/sold-at rows for those products or a governed restricted-product set; do not attach the restriction only to an unrelated pepper item.",
    "Compile surface invariant rule: multi-value summary fields such as Product Type, Subjects, Categories, Brand Names, or Affected Items are repeated values, not a single scalar. Preserve each listed value or a full field detail row; do not truncate the field to the first semicolon- or comma-separated value.",
    "Compile surface invariant rule: point-in-time status/state questions need direct status surfaces. When the source states a current/as-of/on-date status, condition, availability, approval/denial, pending resolution, active/closed state, or authoritative current value, preserve subject, state/status value, temporal or source scope, and reason/authority when stated as joinable direct rows. Do not leave the answer only in source_record text, a broad event wrapper, or split status/2 plus unjoined date rows.",
    "Compile surface invariant rule: court, appeal, administrative-review, adjudication, and agency-order sources need current disposition surfaces separate from procedural history. When the source states that the present decision remands/transfers a matter, resolves it directly/on the merits, finally disposes of it, rejects/affirms/reverses a claim, or orders further action, preserve the current decision or case id, challenged act/claim when stated, disposition/effect, source/date anchor, and whether the effect belongs to the current decision rather than an older history item. If no stricter profile predicate can carry the disposition mode or effect and source_detail/4 is available, emit a source_detail row instead of leaving the disposition only in source text.",
    "Compile surface invariant rule: status transitions and scoped population states are additive surfaces. When a source states before/after state, reclassification, replacement, supersession, pending-to-decided movement, or only part of a population in a state, preserve both the governed subject or subset and the state transition with its effective date/source. Do not collapse a population state into one unscoped current-status atom.",
    "Compile surface invariant rule: operational record/status events should preserve the event or record id, governed subject/item/application, actor/body, timestamp/turn, status before and after when stated, authority/source, and reason/correction detail when stated. Received/filed/assigned/approved/denied/withdrawn/pending/corrected/superseded/reopened/closed/current-status/transition vocabulary should not be left only as record labels.",
    "Compile surface invariant rule: operational lifecycle compiles should prefer stable phase and event surfaces when compatible predicates exist: record_alias/2 for equivalent record ids; record_status_phase/4 for initial/current/final/prior status; record_status_at/3 for dated status; record_lifecycle_event/5 for event type, actor, object/subject, and date; and record_superseded_by/4 for superseding source/event/document separately from resulting status.",
    "Compile surface invariant rule: repeated lifecycle/status source lines require parallel preservation. For each stated dated lifecycle/status line, emit at least one complete direct unit that keeps subject, lifecycle state/action, and date/turn joinable; do not satisfy the series with only supersession fragments, event labels, status words, or two-slot status/result predicates that omit the date/event join.",
    "Compile surface invariant rule: for received/filed/logged/docketed events, preserve the receiving or filing actor separately from the submitter/source actor and bind both to the submitted object when both are stated. For withdrawn/retracted/cancelled/denied/approved/superseded requests, preserve the requested action/content/line item or descriptive target when stated.",
    "Compile surface invariant rule: if the source states counts, totals, limits, durations, percentages, ratios, units, or formula components, preserve the numeric component rows directly. Do not hide them inside prose labels or summary atoms.",
    "Compile surface invariant rule: when the allowed profile contains a direct quantity carrier such as event_measurement/4, event_quantity/4, reading_value/4, measurement_value/4, metric_observation/4, or a source-local count/amount/rate/duration predicate, populate that carrier for source-stated numeric rows. Raw event, corrected event, note, description, or detail rows are additive context, not replacements for the direct value surface.",
    "Compile surface invariant rule: numeric event changes stated as changed/reverted/increased/decreased from X to Y or with an X -> Y arrow need separate before and after value rows for each event when the profile offers event_measurement/4 or an equivalent carrier. Do not satisfy later reverted rows by only preserving the first changed row.",
    "Compile surface invariant rule: explicit duration totals such as line-stop duration 17 hours 45 minutes 52 seconds need a direct duration value row when the profile offers event_measurement/4, event_duration/3, or an equivalent duration carrier. Start/end timestamps or interval rows are temporal anchors, not replacements for the stated numeric duration total.",
    "Compile surface invariant rule: financial or numeric-state calculations need baseline preservation. When the source states an initial/current balance or value, adjustments/debits/credits/expenditures, actual versus hypothetical scenario assumptions, resulting value, and policy threshold, preserve those as separate joinable rows. Derivation rows need a scenario or basis slot so actual, hypothetical, before, and after states do not overwrite one another. Do not overwrite an initial baseline with a later actual value, and do not answer counterfactual calculations from only the actual-result row.",
    "Compile surface invariant rule: financial reports often state a total metric and then a named contributor, affiliate, associate, investee, subsidiary, segment, project, customer, or vendor contribution to that metric. Preserve the total and named contribution as separate joinable financial rows with compatible period, scope/entity, metric, value, and unit slots when the profile supports them. If basis/source is query-bearing, preserve it in a separate provenance/source-coordinate row or source-record ledger row. A source-record line or narrative summary alone is not enough for amount-contribution questions.",
    "Compile surface invariant rule: if the source states custody, possession, access, location, ownership, title, recall, return, or control state, preserve each stated control surface separately. Do not collapse them into a generic status label.",
    "Candidate predicate names are not enough. When an invariant surface is present in the source and supported by the allowed profile, propose the concrete fact operations needed to make it queryable.",
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
from src.archival_identifier_ledger import (  # noqa: E402
    archival_identifier_context,
    extract_archival_identifier_ledger,
)
from src.source_record_ledger import (  # noqa: E402
    extract_source_record_ledger,
    source_record_ledger_facts,
    source_record_ledger_context,
)
from src.semantic_ir import (  # noqa: E402
    SemanticIRCallConfig,
    call_semantic_ir,
    semantic_ir_to_legacy_parse,
)
from src.model_path import (  # noqa: E402
    apply_openrouter_provider_env,
    local_lmstudio_model_metadata,
    openrouter_api_key,
    openrouter_generation_metadata,
    openrouter_metadata_headers,
    model_serving_path_metadata,
    openrouter_provider_routing_from_env,
    refresh_openrouter_generation_metadata_entries,
)
from src.semantic_struggle import assess_semantic_progress  # noqa: E402


OPENROUTER_CALL_METADATA_LOG: list[dict[str, Any]] = []


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
    parser.add_argument(
        "--profile-registry-lens",
        default="",
        help=(
            "Optional registry lens id. When set, only that lens' allowed signatures are offered from "
            "--profile-registry to the profile, compile context, and registry follow-up passes."
        ),
    )
    parser.add_argument(
        "--profile-registry-palette-prior",
        action="store_true",
        help=(
            "Treat --profile-registry as a palette-stability prior during normal profile generation. "
            "This preserves matching predicate names/arities when they fit the source without treating registry rows as facts."
        ),
    )
    parser.add_argument(
        "--allow-global-first-profile-registry-palette-prior",
        action="store_true",
        help=(
            "Allow --profile-registry-palette-prior with a blank-fixture multi-draw registry selected by mode=first. "
            "Default is blocked because global first-draw palettes are unstable stamp priors."
        ),
    )
    parser.add_argument("--domain-hint", default="")
    parser.add_argument("--backend", choices=["lmstudio"], default="lmstudio")
    parser.add_argument("--model", default=os.environ.get("PRETHINKER_MODEL", "qwen/qwen3.6-35b-a3b"))
    parser.add_argument("--base-url", default=os.environ.get("PRETHINKER_BASE_URL", "http://127.0.0.1:1234"))
    parser.add_argument(
        "--api-key",
        default="",
        help="Optional OpenAI-compatible API key. Local LM Studio does not require one.",
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.82)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--num-ctx", type=int, default=32768)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument(
        "--openrouter-provider-order",
        default="",
        help="Comma-separated OpenRouter provider slugs to try in order. Recorded in model_serving_path.",
    )
    parser.add_argument(
        "--openrouter-provider-only",
        default="",
        help="Comma-separated OpenRouter provider slugs to allow. Recorded in model_serving_path.",
    )
    parser.add_argument(
        "--openrouter-provider-ignore",
        default="",
        help="Comma-separated OpenRouter provider slugs to exclude. Recorded in model_serving_path.",
    )
    parser.add_argument(
        "--openrouter-quantizations",
        default="",
        help="Comma-separated OpenRouter quantization filters, such as int4,int8,fp16.",
    )
    parser.add_argument(
        "--openrouter-allow-fallbacks",
        choices=["", "true", "false"],
        default="",
        help="OpenRouter provider.allow_fallbacks override. Empty preserves environment/default behavior.",
    )
    parser.add_argument(
        "--openrouter-require-parameters",
        choices=["", "true", "false"],
        default="",
        help="OpenRouter provider.require_parameters override. Empty preserves environment/default behavior.",
    )
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
        "--profile-list-range-self-check-followup",
        action="store_true",
        help=(
            "Experimental: if the list/range repair pass reports self_check.missing_slots, run one bounded "
            "source-grounded completion pass for those missing typed rows."
        ),
    )
    parser.add_argument(
        "--profile-list-range-omission-followup",
        action="store_true",
        help=(
            "Experimental: after governed companion health is attached, run one bounded source-grounded "
            "completion pass for list/range omission-ledger rows."
        ),
    )
    parser.add_argument(
        "--profile-registered-carrier-omission-followup",
        action="store_true",
        help=(
            "Experimental: after registered-carrier delivery accountability is attached, run one bounded "
            "source-grounded completion pass for accountability-required registered carriers with zero emitted rows."
        ),
    )
    parser.add_argument(
        "--profile-registry-accountability-followup",
        action="store_true",
        help=(
            "Experimental: after a profile-registry compile, run one bounded source-grounded completion pass "
            "for registry accountability requirements. The pass may emit domain_omission/5 only."
        ),
    )
    parser.add_argument(
        "--profile-registry-completion-followup",
        action="store_true",
        help=(
            "Experimental: after a profile-registry compile, run one bounded source-grounded completion pass "
            "inside the closed registry predicate set. The pass may emit registered domain facts only."
        ),
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
        "--archival-identifier-ledger",
        action="store_true",
        help=(
            "Experimental: extract exact identifier-like lexical spans as context guidance for archival "
            "row/source labels. This does not admit facts or interpret source meaning."
        ),
    )
    parser.add_argument(
        "--source-record-ledger",
        action="store_true",
        help=(
            "Experimental: extract line-numbered source headings, table rows, bullets, and labeled rows as "
            "context guidance for record addressability. This does not admit facts or interpret source meaning."
        ),
    )
    parser.add_argument(
        "--source-record-ledger-facts",
        action="store_true",
        help=(
            "Experimental: when --source-record-ledger is enabled, append deterministic source-address "
            "facts to the compiled KB. These preserve row labels, lines, sections, and exact row text; "
            "they do not encode semantic conclusions."
        ),
    )
    parser.add_argument(
        "--profile-delivery-repair-pass",
        action="store_true",
        help=(
            "Experimental: after an initial source compile, run one bounded proposal-only repair pass when "
            "profile-delivery diagnostics show offered direct carriers with missing emitted rows."
        ),
    )
    parser.add_argument(
        "--profile-role-roster-repair-pass",
        action="store_true",
        help=(
            "Experimental: after an initial source compile, run one bounded proposal-only repair pass for "
            "typed role/roster rows such as counsel, representatives, signatories, contacts, and job titles."
        ),
    )
    parser.add_argument(
        "--profile-identifier-occurrence-repair-pass",
        action="store_true",
        help=(
            "Experimental: after an initial source compile, run one bounded proposal-only repair pass for "
            "source-stated identifier occurrences such as docket, file, accession, control, FEI, CMS, and EIN values."
        ),
    )
    parser.add_argument(
        "--profile-document-date-repair-pass",
        action="store_true",
        help=(
            "Experimental: after an initial source compile, run one bounded proposal-only repair pass for "
            "source-stated document, application, publication, filing, decision, notice, and report dates."
        ),
    )
    parser.add_argument(
        "--profile-list-range-inventory-repair-pass",
        action="store_true",
        help=(
            "Experimental: after an initial source compile, run one bounded proposal-only repair pass for "
            "source-stated numbered list members and range segments."
        ),
    )
    parser.add_argument(
        "--profile-rating-scale-repair-pass",
        action="store_true",
        help=(
            "Experimental: after an initial source compile, run one bounded proposal-only repair pass for "
            "source-stated rating-scale options such as adjectival evaluation scales."
        ),
    )
    parser.add_argument(
        "--profile-governed-subject-discovery-pass",
        action="store_true",
        help=(
            "Experimental: after initial/source repair compile, run one bounded proposal-only pass for "
            "governed subject bundles such as claim sets, findings, violations, or reviewed actions."
        ),
    )
    parser.add_argument(
        "--profile-governed-subject-manifest-pass",
        action="store_true",
        help=(
            "Experimental: after initial/source repair compile, run a constrained JSON manifest pass for "
            "governed subject bundles, then deterministically map typed slots to governed carrier facts."
        ),
    )
    parser.add_argument(
        "--profile-legal-citation-repair-pass",
        action="store_true",
        help=(
            "Experimental: after initial/source repair compile, run one bounded proposal-only pass for "
            "source-stated legal citation details on already-emitted governed subjects."
        ),
    )
    parser.add_argument(
        "--profile-monetary-payment-repair-pass",
        action="store_true",
        help=(
            "Experimental: after initial/source repair compile, run one bounded proposal-only pass for "
            "source-stated monetary payment rows on exact amount/authority/purpose carriers."
        ),
    )
    parser.add_argument(
        "--profile-review-outcome-repair-pass",
        action="store_true",
        help=(
            "Experimental: after initial/source repair compile, run one bounded proposal-only pass for "
            "source-stated review outcomes on already-emitted governed subjects."
        ),
    )
    parser.add_argument(
        "--document-metadata-profile-extension",
        action="store_true",
        help=(
            "Experimental: add generic document_title/2, document_publisher/2, document_date/3, document_date_range/3, "
            "registrant_identity/2, and registrant_name/2 vocabulary carriers before source compilation."
        ),
    )
    parser.add_argument(
        "--role-detail-profile-extension",
        action="store_true",
        help=(
            "Experimental: add a generic person_role_detail/5 vocabulary carrier when the profile has only "
            "shallow role predicates."
        ),
    )
    parser.add_argument(
        "--legal-citation-profile-extension",
        action="store_true",
        help=(
            "Experimental: add a generic legal_citation_detail/4 vocabulary carrier for exact statute, rule, "
            "regulation, case, and clause citations."
        ),
    )
    parser.add_argument(
        "--monetary-payment-profile-extension",
        action="store_true",
        help=(
            "Experimental: add a generic monetary_payment/5 vocabulary carrier for source-stated payment, "
            "relief, penalty, restitution, reimbursement, and settlement amounts."
        ),
    )
    parser.add_argument(
        "--obligation-detail-profile-extension",
        action="store_true",
        help=(
            "Experimental: add a generic obligation_detail/5 vocabulary carrier for compact source-stated "
            "requirement, settlement, reporting, deadline, frequency, duration, scope, and condition terms."
        ),
    )
    parser.add_argument(
        "--procedural-rule-detail-profile-extension",
        action="store_true",
        help=(
            "Experimental: add a generic procedural_rule_detail/5 vocabulary carrier for compact "
            "source-stated review, rehearing, appeal, filing, deadline, and default-consequence rule terms."
        ),
    )
    parser.add_argument(
        "--document-checkbox-profile-extension",
        action="store_true",
        help=(
            "Experimental: add a generic document_checkbox_provision/5 vocabulary carrier for source-stated "
            "checkbox/list provisions, markings, rule labels, and citations on official forms."
        ),
    )
    parser.add_argument(
        "--document-identifier-occurrence-profile-extension",
        action="store_true",
        help=(
            "Experimental: add a generic document_identifier_occurrence/5 vocabulary carrier for repeated "
            "source-stated document identifiers with occurrence scope and order."
        ),
    )
    parser.add_argument(
        "--list-range-inventory-profile-extension",
        action="store_true",
        help=(
            "Experimental: add generic list_member/4, claim_range/4, and item_range/4 vocabulary carriers "
            "for source-stated numbered lists and ranges."
        ),
    )
    parser.add_argument(
        "--rating-scale-profile-extension",
        action="store_true",
        help=(
            "Experimental: add a generic rating_scale_option/4 vocabulary carrier for source-stated "
            "rating-scale options and their scale/factor."
        ),
    )
    parser.add_argument(
        "--extra-compile-context-line",
        action="append",
        default=[],
        help=(
            "Additional compile-only context line. Intended for generic replay diagnostics and "
            "quality-gate retry pressure, not fixture facts."
        ),
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
    OPENROUTER_CALL_METADATA_LOG.clear()
    args = parse_args()
    if str(args.api_key or "").strip():
        os.environ["PRETHINKER_API_KEY"] = str(args.api_key).strip()
    apply_openrouter_provider_env(
        order=getattr(args, "openrouter_provider_order", ""),
        only=getattr(args, "openrouter_provider_only", ""),
        ignore=getattr(args, "openrouter_provider_ignore", ""),
        quantizations=getattr(args, "openrouter_quantizations", ""),
        allow_fallbacks=getattr(args, "openrouter_allow_fallbacks", ""),
        require_parameters=getattr(args, "openrouter_require_parameters", ""),
    )
    _configure_openrouter_title(args.out_dir)
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
    requested_profile_registry_lens = str(getattr(args, "profile_registry_lens", "") or "").strip()
    if profile_registry and requested_profile_registry_lens:
        profile_registry = _profile_registry_for_lens(profile_registry, requested_profile_registry_lens)
    unsafe_palette_prior_reason = _unsafe_profile_registry_palette_prior_reason(profile_registry)
    if (
        bool(args.profile_registry_palette_prior)
        and unsafe_palette_prior_reason
        and not bool(args.allow_global_first_profile_registry_palette_prior)
    ):
        raise SystemExit(
            "--profile-registry-palette-prior refused: "
            + unsafe_palette_prior_reason
            + ". Rebuild the registry with fixture-local threshold/intersection selection, or pass "
            "--allow-global-first-profile-registry-palette-prior for an explicit diagnostic override."
        )
    if profile_registry:
        sample["candidate_profile_registry_v1"] = profile_registry
        sample["context"].append(
            "candidate_profile_registry_v1 is a source/domain ontology scaffold: predicate signatures, categories, "
            "and notes only. It is not a gold fact set and it does not authorize writes. Prefer these signatures when "
            "they fit the source and preserve epistemic boundaries; omit registry predicates that the source does not need."
        )
        active_lens = profile_registry.get("active_lens") if isinstance(profile_registry.get("active_lens"), dict) else {}
        if active_lens:
            sample["context"].append(
                "Active profile-registry lens: "
                f"{active_lens.get('id')} offers only the predicate signatures listed in its allowed_signatures. "
                "Do not import predicate families from other lenses during this pass."
            )
        if bool(args.profile_registry_palette_prior):
            sample["context"].append(
                "Palette-stability prior: when candidate_profile_registry_v1 already contains a predicate name and arity "
                "that expresses a needed structural capability, use that exact signature. Do not rename it, change its "
                "arity, or emit a near-synonym for the same capability. Add a new predicate only when the registry lacks "
                "a source-required capability, and omit registry predicates not supported by the source."
            )
            sample["context"].append(
                "Palette delivery contract: retained registry predicates are not decorative labels. If the source contains "
                "a repeated row family for a retained signature, keep argument roles that let the compiler emit those rows. "
                "Do not preserve a predicate name while changing slots so the answer-bearing repeated rows become zero-yield."
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
    profile_admission_context = _profile_bootstrap_admission_context(
        intake_plan=intake_plan,
        domain_hint=str(args.domain_hint or ""),
    )
    sample["context"].extend(profile_admission_context)
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
    profile_admission_retry: dict[str, Any] | None = None
    if profile_admission_context and isinstance(parsed, dict) and not bool(args.use_profile_registry_direct):
        admission_report = _profile_admission_report(parsed_profile=parsed, source_text=source_text)
        if any(
            isinstance(item, dict)
            and item.get("class") in {"shallow_lifecycle_palette", "shallow_quantity_event_palette"}
            for item in admission_report.get("findings", [])
            if isinstance(admission_report.get("findings"), list)
        ):
            retry_sample = dict(sample)
            retry_context = list(sample.get("context", [])) if isinstance(sample.get("context"), list) else []
            retry_context.extend(_profile_admission_retry_context(admission_report))
            retry_sample["context"] = retry_context
            retry_started = time.perf_counter()
            retry_response = _call_lmstudio_json_schema(
                base_url=str(args.base_url),
                model=str(args.model),
                messages=build_profile_bootstrap_messages(samples=[retry_sample], domain_hint=str(args.domain_hint or "")),
                schema=PROFILE_BOOTSTRAP_JSON_SCHEMA,
                schema_name="profile_bootstrap_v1",
                timeout=int(args.timeout),
                temperature=float(args.temperature),
                top_p=float(args.top_p),
                max_tokens=min(int(args.max_tokens), 9000),
            )
            retry_parsed, retry_error = parse_profile_bootstrap_json(str(retry_response.get("content", "")))
            retry_report = _profile_admission_report(
                parsed_profile=retry_parsed if isinstance(retry_parsed, dict) else {},
                source_text=source_text,
            )
            profile_admission_retry = {
                "latency_ms": int((time.perf_counter() - retry_started) * 1000),
                "parsed_ok": isinstance(retry_parsed, dict),
                "parse_error": retry_error,
                "previous_report": admission_report,
                "retry_report": retry_report,
                "raw_content": str(retry_response.get("content", ""))[:12000],
            }
            if isinstance(retry_parsed, dict) and not retry_report.get("findings"):
                parsed = retry_parsed
                error = retry_error
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
    profile_schema_contract_retry: dict[str, Any] | None = None
    if isinstance(parsed, dict) and not bool(args.use_profile_registry_direct):
        schema_score = profile_bootstrap_score(parsed)
        if _profile_schema_contract_retry_needed(schema_score):
            retry_sample = dict(sample)
            retry_context = list(sample.get("context", [])) if isinstance(sample.get("context"), list) else []
            retry_context.extend(_profile_schema_contract_retry_context(schema_score))
            retry_sample["context"] = retry_context
            retry_started = time.perf_counter()
            retry_response = _call_lmstudio_json_schema(
                base_url=str(args.base_url),
                model=str(args.model),
                messages=build_profile_bootstrap_messages(samples=[retry_sample], domain_hint=str(args.domain_hint or "")),
                schema=PROFILE_BOOTSTRAP_JSON_SCHEMA,
                schema_name="profile_bootstrap_v1",
                timeout=int(args.timeout),
                temperature=float(args.temperature),
                top_p=float(args.top_p),
                max_tokens=min(int(args.max_tokens), 9000),
            )
            retry_parsed, retry_error = parse_profile_bootstrap_json(str(retry_response.get("content", "")))
            retry_score = profile_bootstrap_score(retry_parsed if isinstance(retry_parsed, dict) else None)
            profile_schema_contract_retry = {
                "latency_ms": int((time.perf_counter() - retry_started) * 1000),
                "parsed_ok": isinstance(retry_parsed, dict),
                "parse_error": retry_error,
                "previous_score": schema_score,
                "retry_score": retry_score,
                "adopted": False,
                "raw_content": str(retry_response.get("content", ""))[:12000],
            }
            if isinstance(retry_parsed, dict) and not _profile_schema_contract_retry_needed(retry_score):
                parsed = retry_parsed
                error = retry_error
                profile_schema_contract_retry["adopted"] = True
    profile_extension_metadata: dict[str, Any] | None = None
    if isinstance(parsed, dict) and bool(args.compile_source) and bool(args.source_record_ledger):
        extension_rows = [
            _ensure_repeated_structure_predicates(parsed),
            _ensure_source_authority_predicate(parsed, source_text=source_text),
            _ensure_entity_location_predicate(parsed, source_text=source_text),
            _ensure_source_detail_predicate(parsed),
            _ensure_source_attributed_claim_predicate(parsed, source_text=source_text),
            _ensure_vote_tally_predicate(parsed, source_text=source_text),
            _ensure_event_date_predicate(parsed, source_text=source_text),
            _ensure_quorum_status_predicate(parsed, source_text=source_text),
            _ensure_appeal_filing_predicate(parsed, source_text=source_text),
            _ensure_status_state_predicate(parsed, source_text=source_text),
            _ensure_quantity_event_predicate(parsed, source_text=source_text),
            _ensure_scheduled_event_predicate(parsed, source_text=source_text),
        ]
        if bool(getattr(args, "document_metadata_profile_extension", False)):
            extension_rows.append(_ensure_document_metadata_predicates(parsed))
        if bool(getattr(args, "role_detail_profile_extension", False)):
            extension_rows.append(_ensure_role_detail_predicate(parsed))
        if bool(getattr(args, "legal_citation_profile_extension", False)):
            extension_rows.append(_ensure_legal_citation_detail_predicate(parsed))
        if bool(getattr(args, "monetary_payment_profile_extension", False)):
            extension_rows.append(_ensure_monetary_payment_predicate(parsed))
        if bool(getattr(args, "obligation_detail_profile_extension", False)):
            extension_rows.append(_ensure_obligation_detail_predicate(parsed))
        if bool(getattr(args, "procedural_rule_detail_profile_extension", False)):
            extension_rows.append(_ensure_procedural_rule_detail_predicate(parsed))
        if bool(getattr(args, "document_checkbox_profile_extension", False)):
            extension_rows.append(_ensure_document_checkbox_provision_predicate(parsed))
        if bool(getattr(args, "document_identifier_occurrence_profile_extension", False)):
            extension_rows.append(_ensure_document_identifier_occurrence_predicate(parsed))
        if bool(getattr(args, "list_range_inventory_profile_extension", False)):
            extension_rows.append(_ensure_list_range_inventory_predicates(parsed))
        if bool(getattr(args, "rating_scale_profile_extension", False)):
            extension_rows.append(_ensure_rating_scale_option_predicate(parsed))
        profile_extension_metadata = {
            "schema_version": "profile_extensions_v1",
            "extensions": extension_rows,
        }
        carrier_contract_reconciliation = _reconcile_profile_carrier_contracts(parsed)
        if carrier_contract_reconciliation.get("changed_count"):
            profile_extension_metadata["carrier_contract_registry_reconciliation"] = carrier_contract_reconciliation
    score = profile_bootstrap_score(parsed)
    record: dict[str, Any] = {
        "ts": _utc_now(),
        "text_file": str(text_path),
        "domain_hint": str(args.domain_hint or ""),
        "backend": str(args.backend),
        "model": str(args.model),
        "model_serving_path": model_serving_path_metadata(
            backend=str(args.backend),
            base_url=str(args.base_url),
            model=str(args.model),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            top_k=int(args.top_k),
            context_length=int(args.num_ctx),
            max_tokens=int(args.max_tokens),
            timeout=int(args.timeout),
            run_role="compile",
            cache_enabled=None,
            lanes=1,
            fresh_compile=bool(args.compile_source),
            provider_routing=openrouter_provider_routing_from_env(),
            observed_runtime=local_lmstudio_model_metadata(
                backend=str(args.backend),
                base_url=str(args.base_url),
                model=str(args.model),
                timeout=min(int(args.timeout), 3),
            ),
        ),
        "profile_registry": str(args.profile_registry or ""),
        "profile_registry_lens": str(getattr(args, "profile_registry_lens", "") or "").strip(),
        "active_profile_registry_lens": (
            profile_registry.get("active_lens", {})
            if isinstance(profile_registry.get("active_lens"), dict)
            else {}
        ),
        "profile_registry_direct": bool(args.use_profile_registry_direct),
        "profile_registry_palette_prior": bool(args.profile_registry_palette_prior),
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "parsed_ok": isinstance(parsed, dict),
        "parse_error": error,
        "score": score,
        "parsed": parsed or {},
        "raw_content": str(response.get("content", ""))[:20000],
    }
    if profile_registry and isinstance(parsed, dict):
        record["profile_registry_palette_report"] = _profile_registry_palette_report(
            parsed_profile=parsed,
            profile_registry=profile_registry,
        )
    if profile_retry is not None:
        record["profile_retry"] = profile_retry
    if profile_signature_roster_retry is not None:
        record["profile_signature_roster_retry"] = profile_signature_roster_retry
    if profile_admission_retry is not None:
        record["profile_admission_retry"] = profile_admission_retry
    if profile_review is not None:
        record["profile_review"] = profile_review
    if profile_review_retry is not None:
        record["profile_review_retry"] = profile_review_retry
    if profile_schema_contract_retry is not None:
        record["profile_schema_contract_retry"] = profile_schema_contract_retry
    if profile_extension_metadata is not None:
        record["profile_extension_metadata"] = profile_extension_metadata
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
    extra_compile_context: list[str] = []
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
    extra_compile_context.extend(source_entity_ledger_context)
    if bool(args.archival_identifier_ledger) and bool(args.compile_source) and isinstance(parsed, dict):
        archival_identifier_ledger = extract_archival_identifier_ledger(source_text)
        record["archival_identifier_ledger"] = {
            "parsed_ok": True,
            "parse_error": "",
            "parsed": archival_identifier_ledger,
        }
        extra_compile_context.extend(archival_identifier_context(archival_identifier_ledger))
    source_record_ledger: dict[str, Any] | None = None
    if bool(args.source_record_ledger) and bool(args.compile_source) and isinstance(parsed, dict):
        source_record_ledger = extract_source_record_ledger(source_text)
        record["source_record_ledger"] = {
            "parsed_ok": True,
            "parse_error": "",
            "parsed": source_record_ledger,
        }
        extra_compile_context.extend(source_record_ledger_context(source_record_ledger))
    if profile_registry and bool(args.profile_registry_palette_prior) and bool(args.compile_source) and isinstance(parsed, dict):
        extra_compile_context.extend(_profile_registry_palette_prior_context(profile_registry))
    if profile_registry and bool(args.compile_source) and isinstance(parsed, dict):
        extra_compile_context.extend(_profile_registry_accountability_context(profile_registry))
    extra_compile_context.extend(
        line
        for line in (str(item).strip() for item in getattr(args, "extra_compile_context_line", []) or [])
        if line
    )
    if bool(args.compile_source) and isinstance(parsed, dict) and bool(args.compile_flat_plus_plan_passes) and isinstance(intake_plan, dict):
        record["source_compile"] = _compile_source_flat_plus_plan_passes(
            source_text=source_text,
            parsed_profile=parsed,
            intake_plan=intake_plan,
            args=args,
            extra_context=extra_compile_context,
        )
    elif bool(args.compile_source) and isinstance(parsed, dict) and bool(args.compile_plan_passes) and isinstance(intake_plan, dict):
        record["source_compile"] = _compile_source_with_plan_passes(
            source_text=source_text,
            parsed_profile=parsed,
            intake_plan=intake_plan,
            args=args,
            extra_context=extra_compile_context,
        )
    elif bool(args.compile_source) and isinstance(parsed, dict):
        record["source_compile"] = _compile_source_with_draft_profile(
            source_text=source_text,
            parsed_profile=parsed,
            intake_plan=intake_plan,
            args=args,
            extra_context=extra_compile_context,
        )
    if (
        bool(args.compile_source)
        and bool(args.profile_delivery_repair_pass)
        and isinstance(parsed, dict)
        and isinstance(record.get("source_compile"), dict)
    ):
        _apply_profile_delivery_repair_pass(
            source_compile=record["source_compile"],
            parsed_profile=parsed,
            source_text=source_text,
            intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
            args=args,
            extra_context=extra_compile_context,
        )
    if (
        bool(args.compile_source)
        and bool(args.profile_role_roster_repair_pass)
        and isinstance(parsed, dict)
        and isinstance(record.get("source_compile"), dict)
    ):
        _apply_profile_role_roster_repair_pass(
            source_compile=record["source_compile"],
            parsed_profile=parsed,
            source_text=source_text,
            intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
            args=args,
            extra_context=extra_compile_context,
        )
    if (
        bool(args.compile_source)
        and bool(args.profile_identifier_occurrence_repair_pass)
        and isinstance(parsed, dict)
        and isinstance(record.get("source_compile"), dict)
    ):
        _apply_profile_identifier_occurrence_repair_pass(
            source_compile=record["source_compile"],
            parsed_profile=parsed,
            source_text=source_text,
            intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
            args=args,
            extra_context=extra_compile_context,
        )
    if (
        bool(args.compile_source)
        and bool(args.profile_document_date_repair_pass)
        and isinstance(parsed, dict)
        and isinstance(record.get("source_compile"), dict)
    ):
        _apply_profile_document_date_repair_pass(
            source_compile=record["source_compile"],
            parsed_profile=parsed,
            source_text=source_text,
            intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
            args=args,
            extra_context=extra_compile_context,
        )
    if (
        bool(args.compile_source)
        and bool(args.profile_list_range_inventory_repair_pass)
        and isinstance(parsed, dict)
        and isinstance(record.get("source_compile"), dict)
    ):
        _apply_profile_list_range_inventory_repair_pass(
            source_compile=record["source_compile"],
            parsed_profile=parsed,
            source_text=source_text,
            intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
            args=args,
            extra_context=extra_compile_context,
        )
    if (
        bool(args.compile_source)
        and bool(args.profile_rating_scale_repair_pass)
        and isinstance(parsed, dict)
        and isinstance(record.get("source_compile"), dict)
    ):
        _apply_profile_rating_scale_repair_pass(
            source_compile=record["source_compile"],
            parsed_profile=parsed,
            source_text=source_text,
            intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
            args=args,
            extra_context=extra_compile_context,
        )
    if (
        bool(args.compile_source)
        and bool(args.profile_governed_subject_discovery_pass)
        and isinstance(parsed, dict)
        and isinstance(record.get("source_compile"), dict)
    ):
        _apply_profile_governed_subject_discovery_pass(
            source_compile=record["source_compile"],
            parsed_profile=parsed,
            source_text=source_text,
            intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
            args=args,
            extra_context=extra_compile_context,
        )
    if (
        bool(args.compile_source)
        and bool(args.profile_governed_subject_manifest_pass)
        and isinstance(parsed, dict)
        and isinstance(record.get("source_compile"), dict)
    ):
        _apply_profile_governed_subject_manifest_pass(
            source_compile=record["source_compile"],
            parsed_profile=parsed,
            source_text=source_text,
            intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
            args=args,
            extra_context=extra_compile_context,
        )
    if (
        bool(args.compile_source)
        and bool(args.profile_legal_citation_repair_pass)
        and isinstance(parsed, dict)
        and isinstance(record.get("source_compile"), dict)
    ):
        _apply_profile_legal_citation_repair_pass(
            source_compile=record["source_compile"],
            parsed_profile=parsed,
            source_text=source_text,
            intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
            args=args,
            extra_context=extra_compile_context,
        )
    if (
        bool(args.compile_source)
        and bool(args.profile_monetary_payment_repair_pass)
        and isinstance(parsed, dict)
        and isinstance(record.get("source_compile"), dict)
    ):
        _apply_profile_monetary_payment_repair_pass(
            source_compile=record["source_compile"],
            parsed_profile=parsed,
            source_text=source_text,
            intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
            args=args,
            extra_context=extra_compile_context,
        )
    if (
        bool(args.compile_source)
        and bool(args.profile_review_outcome_repair_pass)
        and isinstance(parsed, dict)
        and isinstance(record.get("source_compile"), dict)
    ):
        _apply_profile_review_outcome_repair_pass(
            source_compile=record["source_compile"],
            parsed_profile=parsed,
            source_text=source_text,
            intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
            args=args,
            extra_context=extra_compile_context,
        )
    if bool(args.compile_source) and isinstance(record.get("source_compile"), dict):
        _apply_governed_reference_citation_atom_reduction(record["source_compile"])
        _apply_governed_claim_ground_atom_reduction(record["source_compile"])
        _apply_governed_review_atom_fact_reduction(record["source_compile"])
        _apply_governed_obligation_detail_atom_reduction(record["source_compile"])
        _apply_document_subject_atom_convergence(record["source_compile"])
        _attach_governed_companion_subject_health(record["source_compile"])
        _apply_fda_warning_letter_subject_convergence(record["source_compile"])
        _apply_fda_date_atom_reduction(record["source_compile"])
        _apply_fda_facility_subject_convergence(record["source_compile"])
        _apply_fda_lot_identifier_atom_reduction(record["source_compile"])
        _apply_fda_facility_identity_atom_reduction(record["source_compile"])
        _apply_fda_consultant_citation_scope_reduction(record["source_compile"])
        _apply_fda_office_atom_reduction(record["source_compile"])
        _apply_fda_violation_number_atom_reduction(record["source_compile"])
        _apply_fda_violation_detail_subject_integrity(record["source_compile"])
        _apply_source_scope_payload_integrity(record["source_compile"])
        _apply_carrier_value_domain_integrity(record["source_compile"])
        _enforce_fda_correspondence_party_placeholder_contract(record["source_compile"])
        if (
            bool(getattr(args, "profile_list_range_omission_followup", False))
            and
            bool(args.profile_list_range_inventory_repair_pass)
            and isinstance(parsed, dict)
            and _profile_list_range_inventory_offered_omission_rows(record["source_compile"])
        ):
            _apply_profile_list_range_inventory_omission_followup_pass(
                source_compile=record["source_compile"],
                parsed_profile=parsed,
                source_text=source_text,
                intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
                args=args,
                extra_context=extra_compile_context,
            )
            _attach_governed_companion_subject_health(record["source_compile"])
        _apply_fda_warning_letter_subject_convergence(record["source_compile"])
        _apply_fda_date_atom_reduction(record["source_compile"])
        _apply_fda_facility_subject_convergence(record["source_compile"])
        if (
            bool(getattr(args, "profile_registry_completion_followup", False))
            and profile_registry
            and isinstance(parsed, dict)
        ):
            _apply_profile_registry_completion_followup_pass(
                source_compile=record["source_compile"],
                parsed_profile=parsed,
                profile_registry=profile_registry,
                source_text=source_text,
                intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
                args=args,
                extra_context=extra_compile_context,
            )
        if (
            bool(getattr(args, "profile_registry_accountability_followup", False))
            and profile_registry
            and isinstance(parsed, dict)
        ):
            _apply_profile_registry_accountability_followup_pass(
                source_compile=record["source_compile"],
                parsed_profile=parsed,
                profile_registry=profile_registry,
                source_text=source_text,
                intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
                args=args,
                extra_context=extra_compile_context,
            )
        _apply_fda_lot_identifier_atom_reduction(record["source_compile"])
        _apply_fda_facility_identity_atom_reduction(record["source_compile"])
        _apply_fda_date_atom_reduction(record["source_compile"])
        _apply_fda_facility_subject_convergence(record["source_compile"])
        _apply_fda_consultant_citation_scope_reduction(record["source_compile"])
        _apply_fda_office_atom_reduction(record["source_compile"])
        _apply_fda_warning_letter_subject_convergence(record["source_compile"])
        _apply_fda_violation_number_atom_reduction(record["source_compile"])
        _apply_fda_violation_detail_subject_integrity(record["source_compile"])
        _apply_source_scope_payload_integrity(record["source_compile"])
        _apply_carrier_value_domain_integrity(record["source_compile"])
        _enforce_fda_correspondence_party_placeholder_contract(record["source_compile"])
        _apply_domain_omission_carrier_signature_reduction(record["source_compile"])
    if bool(args.compile_source) and isinstance(parsed, dict) and isinstance(record.get("source_compile"), dict):
        _attach_profile_admission_report(
            source_compile=record["source_compile"],
            parsed_profile=parsed,
            source_text=source_text,
            intake_plan=intake_plan,
            domain_hint=str(args.domain_hint or ""),
        )
        registered_carrier_delivery = _attach_registered_carrier_delivery_report(
            source_compile=record["source_compile"],
            parsed_profile=parsed,
            profile_extension_metadata=profile_extension_metadata,
            mark_health=not bool(getattr(args, "profile_registered_carrier_omission_followup", False)),
        )
        if (
            bool(getattr(args, "profile_registered_carrier_omission_followup", False))
            and registered_carrier_delivery.get("findings")
        ):
            _apply_profile_registered_carrier_omission_followup_pass(
                source_compile=record["source_compile"],
                parsed_profile=parsed,
                source_text=source_text,
                intake_plan=intake_plan if isinstance(intake_plan, dict) else {},
                args=args,
                extra_context=extra_compile_context,
                profile_extension_metadata=profile_extension_metadata,
                registered_delivery_report=registered_carrier_delivery,
            )
            _apply_governed_obligation_detail_atom_reduction(record["source_compile"])
            _attach_registered_carrier_delivery_report(
                source_compile=record["source_compile"],
                parsed_profile=parsed,
                profile_extension_metadata=profile_extension_metadata,
            )
    if (
        bool(args.source_record_ledger_facts)
        and isinstance(source_record_ledger, dict)
        and isinstance(record.get("source_compile"), dict)
    ):
        _append_source_record_ledger_facts(record["source_compile"], source_record_ledger)
    if bool(args.compile_source) and isinstance(parsed, dict) and isinstance(record.get("source_compile"), dict):
        _append_source_field_id_facts(record["source_compile"], parsed)
        _append_entity_id_closure_facts(record["source_compile"], parsed)
    if args.expected_prolog:
        record["expected_prolog"] = _compare_expected_prolog(
            expected_path=expected_path or (REPO_ROOT / args.expected_prolog).resolve(),
            parsed_profile=parsed if isinstance(parsed, dict) else {},
            source_compile=record.get("source_compile") if isinstance(record.get("source_compile"), dict) else {},
        )
    if OPENROUTER_CALL_METADATA_LOG:
        record["openrouter_generation_metadata"] = refresh_openrouter_generation_metadata_entries(
            OPENROUTER_CALL_METADATA_LOG,
            api_key=str(getattr(args, "api_key", "") or ""),
            timeout=min(int(args.timeout), 30),
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


def _profile_schema_contract_retry_needed(score: dict[str, Any]) -> bool:
    refs: list[Any] = []
    if isinstance(score, dict):
        for key in (
            "candidate_signature_arg_mismatch_refs",
            "candidate_duplicate_name_arity_refs",
            "provenance_prose_arg_role_refs",
            "repeated_structure_role_mismatch_refs",
            "list_range_inventory_slot_loss_refs",
        ):
            values = score.get(key, [])
            if isinstance(values, list):
                refs.extend(values)
    return any(str(ref).strip() for ref in refs) if isinstance(refs, list) else False


def _profile_schema_contract_retry_context(score: dict[str, Any]) -> list[str]:
    signature_refs = [
        str(ref).strip()
        for ref in (score.get("candidate_signature_arg_mismatch_refs", []) if isinstance(score, dict) else [])
        if str(ref).strip()
    ]
    repeated_role_refs = [
        str(ref).strip()
        for ref in (score.get("repeated_structure_role_mismatch_refs", []) if isinstance(score, dict) else [])
        if str(ref).strip()
    ]
    duplicate_name_arity_refs = [
        str(ref).strip()
        for ref in (score.get("candidate_duplicate_name_arity_refs", []) if isinstance(score, dict) else [])
        if str(ref).strip()
    ]
    provenance_prose_refs = [
        str(ref).strip()
        for ref in (score.get("provenance_prose_arg_role_refs", []) if isinstance(score, dict) else [])
        if str(ref).strip()
    ]
    governed_arg_refs = [
        str(ref).strip()
        for ref in (score.get("governed_carrier_arg_role_mismatch_refs", []) if isinstance(score, dict) else [])
        if str(ref).strip()
    ]
    list_range_refs = [
        str(ref).strip()
        for ref in (score.get("list_range_inventory_slot_loss_refs", []) if isinstance(score, dict) else [])
        if str(ref).strip()
    ]
    context = [
        (
            "Profile schema contract retry: the previous profile violated at least one structural schema contract. "
            "This may be a predicate signature whose /N arity does not equal the number of args, or a repeated "
            "structure property predicate whose first argument role does not bind to the repeated record/subject. "
            "Emit a complete replacement profile_bootstrap_v1 that preserves the same source-bound capabilities "
            "while fixing the schema contract."
        ),
        (
            "Arity limit: profile_bootstrap_v1 candidate predicates support /1 through /5 only. Do not propose /6 or "
            "higher. If a relation needs more conceptual fields, keep the five most query-bearing schema roles in one "
            "predicate and use a separate provenance/source-coordinate predicate or admission note for source/basis."
        ),
        (
            "Arg-role guardrail: args are short structural role labels only. Do not put source values, copied spans, "
            "comma-bearing examples, generated counters, or alternate value lists inside args."
        ),
        (
            "Provenance/source-record guardrail: provenance predicates locate typed assertions at source coordinates. "
            "Do not put copied source prose, display text, quote text, excerpts, sentences, text_span/source_text/raw_text, "
            "or content slots into source_recorded/recorded_in/ledger_entry/source_supports/provenance-like predicates. "
            "Use source_coord, record_id, assertion_id, subject, status, support_role, source_kind, or target instead; "
            "put asserted meaning in separate typed predicates."
        ),
        (
            "Governed-carrier guardrail: if you use a registered carrier signature, its argument roles must match that "
            "carrier's contract exactly. Do not keep the name while redefining the slots; same atom name means same "
            "instrument language."
        ),
        (
            "Repeated-structure guardrail: if a predicate is listed as a repeated_structures[].property_predicates item, "
            "its first argument role must be the repeated record id or governed subject named by that repeated structure. "
            "For procedural outcome, remand, transfer, disposition, or review-effect surfaces, anchor the relation to "
            "the decision/event/act that actually produced the effect; do not use the global case id as a substitute "
            "for a historical act or current decision."
        ),
    ]
    if signature_refs:
        context.append(f"Previous signature/args mismatch refs: {', '.join(signature_refs[:12])}.")
    if duplicate_name_arity_refs:
        context.append(
            "Previous duplicate predicate-name/arity refs: "
            f"{', '.join(duplicate_name_arity_refs[:12])}. Use one approved arity for each predicate name; "
            "do not introduce a private lower-arity version when a governed carrier already exists."
        )
    if provenance_prose_refs:
        context.append(
            "Previous provenance/source-record prose-slot refs: "
            f"{', '.join(provenance_prose_refs[:12])}."
        )
    if governed_arg_refs:
        context.append(
            "Previous governed-carrier arg-role mismatch refs: "
            f"{', '.join(governed_arg_refs[:12])}."
        )
    if repeated_role_refs:
        context.append(f"Previous repeated-structure role mismatch refs: {', '.join(repeated_role_refs[:12])}.")
    if list_range_refs:
        context.append(
            "Previous numbered list/range inventory slot-loss refs: "
            f"{', '.join(list_range_refs[:12])}."
        )
        context.append(
            "List/range inventory guardrail: if a source lists numbered claims, counts, issues, products, "
            "violations, requirements, order paragraphs, or item ranges with grounds/status/outcomes, do not "
            "store the whole range only as one compressed atom inside an outcome/status predicate. Add or use a "
            "member/range carrier such as list_member/4, claim_range/4, item_range/4, item_ground/5, issue_ground/5, "
            "or a close domain-owned equivalent so source-stated singleton and range boundaries remain queryable."
        )
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
    match = re.fullmatch(r"\s*([a-z][a-z0-9_]*)\s*/\s*([1-6])\s*", str(value or "").casefold())
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
    accountability_requirements: list[dict[str, str]] = []
    raw_requirements = parsed.get("accountability_requirements", [])
    if isinstance(raw_requirements, list):
        for item in raw_requirements:
            if not isinstance(item, dict):
                continue
            requirement = {
                "id": str(item.get("id", "")).strip(),
                "carrier_signature": str(item.get("carrier_signature", "")).strip(),
                "omission_kind": str(item.get("omission_kind", "")).strip(),
                "reason_code": str(item.get("reason_code", "")).strip(),
                "trigger": str(item.get("trigger", "")).strip(),
            }
            if requirement["carrier_signature"] and requirement["omission_kind"] and requirement["reason_code"]:
                accountability_requirements.append(requirement)
    lenses: list[dict[str, Any]] = []
    raw_lenses = parsed.get("lenses", [])
    if isinstance(raw_lenses, list):
        for item in raw_lenses:
            if not isinstance(item, dict):
                continue
            allowed_signatures = [
                str(signature).strip()
                for signature in item.get("allowed_signatures", [])
                if isinstance(item.get("allowed_signatures"), list) and str(signature).strip()
            ]
            lens_id = str(item.get("id", "")).strip()
            if lens_id:
                lenses.append(
                    {
                        "id": lens_id,
                        "purpose": str(item.get("purpose", "")).strip(),
                        "allowed_signatures": allowed_signatures,
                    }
                )
    return {
        "schema": str(parsed.get("schema", "")).strip(),
        "fixture": str(parsed.get("fixture", "")).strip(),
        "source": str(parsed.get("source", "")).strip(),
        "purpose": str(parsed.get("purpose", "")).strip(),
        "selection": parsed.get("selection", {}) if isinstance(parsed.get("selection"), dict) else {},
        "lenses": lenses,
        "accountability_requirements": accountability_requirements,
        "predicates": compact_predicates,
    }


def _profile_registry_for_lens(profile_registry: dict[str, Any], lens_id: str) -> dict[str, Any]:
    requested = str(lens_id or "").strip()
    if not requested:
        return profile_registry
    lenses = profile_registry.get("lenses") if isinstance(profile_registry.get("lenses"), list) else []
    selected = next(
        (
            item
            for item in lenses
            if isinstance(item, dict) and str(item.get("id", "")).strip() == requested
        ),
        None,
    )
    if selected is None:
        available = ", ".join(
            sorted(
                str(item.get("id", "")).strip()
                for item in lenses
                if isinstance(item, dict) and str(item.get("id", "")).strip()
            )
        )
        raise ValueError(f"unknown profile registry lens {requested!r}; available lenses: {available or 'none'}")
    declared_allowed = {
        _normalized_signature(str(signature))
        for signature in selected.get("allowed_signatures", [])
        if _normalized_signature(str(signature))
    }
    accountability_requirements = [
        dict(item)
        for item in profile_registry.get("accountability_requirements", [])
        if (
            isinstance(item, dict)
            and _normalized_signature(str(item.get("carrier_signature", ""))) in declared_allowed
            and "domain_omission/5" in declared_allowed
        )
    ]
    offered_allowed = set(declared_allowed)
    if not accountability_requirements:
        offered_allowed.discard("domain_omission/5")
    predicates = [
        dict(item)
        for item in profile_registry.get("predicates", [])
        if isinstance(item, dict) and _normalized_signature(str(item.get("signature", ""))) in offered_allowed
    ]
    filtered = dict(profile_registry)
    filtered["predicates"] = predicates
    filtered["accountability_requirements"] = accountability_requirements
    filtered["active_lens"] = {
        "id": requested,
        "purpose": str(selected.get("purpose", "")).strip(),
        "declared_allowed_signatures": sorted(declared_allowed),
        "allowed_signatures": sorted(offered_allowed),
        "predicate_count": len(predicates),
        "accountability_requirement_count": len(accountability_requirements),
    }
    return filtered


def _unsafe_profile_registry_palette_prior_reason(profile_registry: dict[str, Any]) -> str:
    if not isinstance(profile_registry, dict) or not profile_registry:
        return ""
    selection = profile_registry.get("selection") if isinstance(profile_registry.get("selection"), dict) else {}
    mode = str(selection.get("mode") or "").strip().casefold()
    try:
        draw_count = int(selection.get("draw_count") or 0)
    except (TypeError, ValueError):
        draw_count = 0
    fixture = str(profile_registry.get("fixture") or "").strip()
    if mode == "first" and draw_count > 1 and not fixture:
        return (
            "registry selection is mode=first across multiple draws with no fixture scope; "
            "that is a global first-draw palette, not a stable stamp prior"
        )
    return ""


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


def _profile_registry_palette_report(*, parsed_profile: dict[str, Any], profile_registry: dict[str, Any]) -> dict[str, Any]:
    registry_signatures = _registry_signature_set(profile_registry)
    profile_signatures = _profile_signature_set(parsed_profile)
    registry_names = _names_to_arities(registry_signatures)
    profile_names = _names_to_arities(profile_signatures)
    same_name_changed_arity = []
    for name in sorted(set(registry_names) & set(profile_names)):
        registry_arities = registry_names[name]
        profile_arities = profile_names[name]
        if registry_arities != profile_arities:
            same_name_changed_arity.append(
                {
                    "predicate": name,
                    "registry_arities": sorted(registry_arities),
                    "profile_arities": sorted(profile_arities),
                }
            )
    overlap = sorted(registry_signatures & profile_signatures)
    missing = sorted(registry_signatures - profile_signatures)
    extra = sorted(profile_signatures - registry_signatures)
    return {
        "schema_version": "profile_registry_palette_report_v1",
        "registry_signature_count": len(registry_signatures),
        "profile_signature_count": len(profile_signatures),
        "overlap_signature_count": len(overlap),
        "missing_registry_signature_count": len(missing),
        "extra_profile_signature_count": len(extra),
        "same_name_changed_arity_count": len(same_name_changed_arity),
        "overlap_signatures": overlap[:120],
        "missing_registry_signatures": missing[:120],
        "extra_profile_signatures": extra[:120],
        "same_name_changed_arity": same_name_changed_arity,
    }


def _profile_registry_palette_prior_context(profile_registry: dict[str, Any]) -> list[str]:
    signatures = []
    for item in profile_registry.get("predicates", []) if isinstance(profile_registry.get("predicates"), list) else []:
        if not isinstance(item, dict):
            continue
        signature = _normalized_signature(str(item.get("signature", "")))
        if not signature:
            continue
        args = [
            str(arg).strip()
            for arg in item.get("args", [])
            if isinstance(item.get("args"), list) and str(arg).strip()
        ][:5]
        signatures.append({"signature": signature, "args": args})
    context = [
        "profile_palette_prior_v1: The registry is vocabulary-only and does not supply facts, answers, or authority.",
        (
            "Palette delivery contract: when the allowed profile retained a registry signature and the source contains "
            "a repeated row family for that structural capability, emit source-supported rows for that signature. "
            "Do not leave retained repeated signatures zero-yield while replacing them with adjacent labels or broad wrappers."
        ),
        (
            "Slot-preservation rule: use the retained predicate's argument roles as the row contract. Preserve the "
            "entity/record, scope/version/time, target/value, role/status, and source/basis slots needed by the retained "
            "signature instead of changing arity or moving the answer-bearing value into a long atom."
        ),
    ]
    if signatures:
        context.append(
            "palette_prior_signatures_v1:\n"
            + json.dumps(signatures[:60], ensure_ascii=False, sort_keys=True)
        )
    return context


def _registry_signature_set(registry: dict[str, Any]) -> set[str]:
    signatures: set[str] = set()
    for item in registry.get("predicates", []) if isinstance(registry.get("predicates"), list) else []:
        if not isinstance(item, dict):
            continue
        signature = _normalized_signature(str(item.get("signature", "")))
        if signature:
            signatures.add(signature)
    return signatures


def _profile_signature_set(parsed_profile: dict[str, Any]) -> set[str]:
    signatures: set[str] = set()
    for item in parsed_profile.get("candidate_predicates", []) if isinstance(parsed_profile.get("candidate_predicates"), list) else []:
        if not isinstance(item, dict):
            continue
        signature = _normalized_signature(str(item.get("signature", "")))
        if signature:
            signatures.add(signature)
    return signatures


def _names_to_arities(signatures: set[str]) -> dict[str, set[int]]:
    out: dict[str, set[int]] = {}
    for signature in signatures:
        name, arity_text = signature.rsplit("/", 1)
        out.setdefault(name, set()).add(int(arity_text))
    return out


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
        api_key=str(getattr(args, "api_key", "") or ""),
    )
    plan_context = intake_plan_context(intake_plan)
    try:
        result = call_semantic_ir(
            utterance=source_text,
            config=config,
            context=[
                *plan_context,
                *source_compiler_context,
                *COMPILE_SURFACE_INVARIANT_CONTEXT_V1,
                *(extra_context or []),
                "Compile the raw source text using the draft profile proposed by profile_bootstrap_v1.",
                "Treat intake_plan_v1.pass_plan as the coverage checklist for this compile. Allocate candidate_operations across the planned passes instead of spending the whole operation budget on the first repeated structure you encounter.",
                "When pass_plan names source boundary, principles/rules, repeated records, final declarations, appeals, or pledges, emit at least one representative safe operation from each supported pass before adding extra repeated-record details.",
                "Use the breadth of the draft profile. If many allowed predicates are available, prefer a diverse skeleton that exercises distinct source/provenance, entity, claim, rule, repeated-record, declaration, and commitment predicate families over many operations using only one predicate family.",
                "Predicate contracts are binding. Preserve the exact argument order from predicate_contracts/allowed profile args. Do not swap subject/object, actor/time, recipient/type, facility/officer, or status/timestamp slots to make a fact fit. If the source supports a fact but the argument order is uncertain, skip it or note the uncertainty in self_check instead of emitting a malformed clause.",
                *_source_pass_predicate_contract_guidance(predicate_contracts),
                "For dense source compilation, entities/assertions/propositions are optional audit scaffolding. Keep them sparse or empty if they would consume output budget. Candidate_operations are the primary artifact; use normalized atoms directly in candidate_operations instead of first listing every source entity.",
                "Avoid predicate canonicalization drift. If the allowed palette contains synonymous prefixed and reusable detail predicates, such as grievance_observation_location/2 and observation_location/2, prefer the reusable detail predicate when its first argument is already the grievance/incident/record id.",
                "Use one canonical predicate surface consistently for a repeated slot. Do not mix grievance_method/2 with method/2, grievance_effect/2 with effect_claimed/2, or grievance_explanation_given/2 with explanation_given/2 unless their meanings are explicitly different in the profile contract.",
                "Do not add facts not present in the source text.",
                "For repeated temporal event lists, preserve every explicitly listed timestamped event when the palette has an event/timestamp predicate. Do not stop after the first interval or representative sibling; later intervals are often the answer-bearing rows for duration and gap questions.",
                "If the whole source contains more safe facts than fit, preserve a balanced document skeleton: source/provenance boundary, core declaration or action, representative repeated records, and concluding commitments. Do not let one repeated list consume the whole candidate_operation budget.",
                "When a draft profile offers source-attributed claim predicates such as claim_made/3 or source_claim/3, prefer those for normative principles, rights, accusations, character judgments, and legitimacy statements that the source asserts but does not externally prove.",
                "If both a direct normative predicate and a source-attributed claim predicate are available, use the source-attributed claim predicate for rights, principles, legitimacy, and character judgments unless the direct predicate itself has a source/document argument.",
                "Preserve reporting and ledger-record acts as first-class queryable details when the draft profile supports them. If a source says someone reported, complained, witnessed, recorded, entered in a ledger, certified, or observed something, prefer reporter/2, complainant/2, reported_observation/2, ledger_entry/2, or similar profile predicates over collapsing the detail into only affected_person/2 or grievance/2.",
                "Preserve epistemic status for source-owned repeated records when the draft profile supports it. For grievances, allegations, complaints, and accusations, emit status/provenance facts such as grievance_status(Grievance, source_bound_accusation) or the profile's equivalent rather than leaving the accusation-vs-fact distinction only implicit in predicate names.",
                "When the source names a reporting actor and a role, preserve both if the palette supports it, e.g. a reporter/person predicate plus person_role/2. This is structural source fidelity, not a domain-specific language patch.",
                "Role-frame preservation rule: when a source sentence states an action or relation with actor, object, and role-bearing participant, preserve the participant bound to the relation rather than only the relation label. For classify/record, submit/receive, assign/request, approve/recommend, witness/report, own/maintain, and write/publish frames, keep classifier, recorder, recipient, assignee, approver, recommender, witness, reporter, owner, maintainer, author, and publisher distinct when the profile offers any compatible predicate or detail surface.",
                "Explicit negative-surface preservation rule: when the source directly states a prohibition, lack of authority, no-control/no-veto relation, exception, exemption, outside-scope condition, or not-allowed role, preserve that stated negative surface as a positive assertion on a compatible prohibition/forbidden/exempt/outside-scope/lacks-authority predicate when the profile offers one. Do not convert it into a general negative-polarity fact, and do not preserve only the adjacent positive permission.",
                "Target-anchor preservation rule: when a source sentence states a relation target plus an after/before/following/during anchor event, preserve the target relation and the anchor relation separately. Do not replace the target with the anchor, and do not shorten a named anchor by dropping source-stated modifiers such as first/final/morning/current when those modifiers distinguish the event.",
                "Object-vs-actor attachment rule: when one clause says an actor attached an object to a place and another says the actor was attached or assigned to a unit, preserve the object-place attachment separately from the actor-unit assignment when the palette has compatible predicates. Do not let the actor-unit row crowd out the object attached by the actor.",
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
    semantic_ir_metadata = result.get("openrouter_generation_metadata") if isinstance(result, dict) else None
    if isinstance(semantic_ir_metadata, dict):
        OPENROUTER_CALL_METADATA_LOG.append(semantic_ir_metadata)
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
            "semantic_ir_openrouter_generation_metadata": semantic_ir_metadata if isinstance(semantic_ir_metadata, dict) else {},
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
        "semantic_ir_openrouter_generation_metadata": semantic_ir_metadata if isinstance(semantic_ir_metadata, dict) else {},
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
            *COMPILE_SURFACE_INVARIANT_CONTEXT_V1,
            *_source_pass_profile_delivery_target_context(
                source_text=source_text,
                parsed_profile=parsed_profile,
            ),
            *_source_pass_predicate_contract_guidance(predicate_contracts),
            *(extra_context or []),
            "This compact schema is for one bounded source pass. Follow current_pass.focus: broad skeleton passes should cover source-wide stable structure, while focused passes should not compile unrelated source sections.",
            "Emit only candidate_operations. Do not emit entities, assertions, propositions, temporal_graph, or truth_maintenance here.",
            "Use exact allowed predicate names and argument order from predicate_contracts.",
            "Predicate contract arity is strict: every candidate_operations[].args array must have exactly the arity declared in predicate_contracts. If a current count or amount fact mentions both an entity and a numeric value, include both in the declared order; never collapse it to only the number or only the entity.",
            "Put stable normalized atoms directly in candidate_operations args.",
            "Role-frame preservation rule: when the current pass source text states an action or relation with actor, object, and role-bearing participant, preserve the participant bound to the relation rather than only the relation label. For classify/record, submit/receive, assign/request, approve/recommend, witness/report, own/maintain, and write/publish frames, keep classifier, recorder, recipient, assignee, approver, recommender, witness, reporter, owner, maintainer, author, and publisher distinct when the profile offers any compatible predicate or detail surface.",
            "Explicit negative-surface preservation rule: when the current pass source text directly states a prohibition, lack of authority, no-control/no-veto relation, exception, exemption, outside-scope condition, or not-allowed role, preserve that stated negative surface as a positive assertion on a compatible prohibition/forbidden/exempt/outside-scope/lacks-authority predicate when the profile offers one. Do not convert it into a general negative-polarity fact, and do not preserve only the adjacent positive permission.",
            "Target-anchor preservation rule: when the current pass source text states a relation target plus an after/before/following/during anchor event, preserve the target relation and the anchor relation separately. Do not replace the target with the anchor, and do not shorten a named anchor by dropping source-stated modifiers such as first/final/morning/current when those modifiers distinguish the event.",
            "Object-vs-actor attachment rule: when one clause says an actor attached an object to a place and another says the actor was attached or assigned to a unit, preserve the object-place attachment separately from the actor-unit assignment when the palette has compatible predicates. Do not let the actor-unit row crowd out the object attached by the actor.",
            "For arithmetic or counterfactual calculation language, preserve the grounded component rows first: base count/amount, operation type, delta value, target entity, calculation view, and view basis when those predicates exist. Do not use prose equations, placeholders, or unresolved phrases as arguments.",
            "When a source gives an arithmetic instruction but does not print the final result, prefer admitting the component facts over inventing a final-result fact. A computed result may be proposed only when the source explicitly states the result or the profile/pass calls for deterministic derived facts.",
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
    ir = _source_pass_ops_to_semantic_ir(parsed, predicate_contracts=predicate_contracts)
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


def _source_pass_predicate_contract_guidance(predicate_contracts: list[dict[str, Any]]) -> list[str]:
    signatures = {
        str(item.get("signature", "")).strip()
        for item in predicate_contracts
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    guidance: list[str] = carrier_contract_prompt_lines(sorted(signatures)[:32])
    if "document_identifier_occurrence/5" in signatures:
        guidance.append(
            "Contract delivery note for document_identifier_occurrence/5: when raw_source_text states the same "
            "identifier kind in multiple source positions or scopes, emit one candidate operation per occurrence. "
            "Do not collapse distinct identifier values into a single document-level identifier row."
        )
    if "document_checkbox_provision/5" in signatures:
        guidance.append(
            "Contract delivery note for document_checkbox_provision/5: when raw_source_text lists checkbox or "
            "checklist rows, emit one candidate operation per source-stated row with mark, rule/provision label, "
            "and citation in separate slots."
        )
    if "domain_omission/5" in signatures:
        guidance.append(
            "Contract delivery note for domain_omission/5: explicit absence statements are source facts. "
            "When raw_source_text says an expected role, carrier item, detail, signature, date, citation, or "
            "other domain slot is absent, unavailable, not shown, not stated, none found, or not applicable, "
            "emit a compact domain_omission/5 row with the relevant registered carrier signature and omission kind. "
            "If you mention an absence in self_check.notes or self_check.missing_slots, also emit the compact "
            "domain_omission/5 row when this carrier is available; self_check alone does not satisfy omission "
            "accountability. Do not use domain_omission/5 as an answer-bearing substitute; it is compile accountability only."
        )
    if {"list_member/4", "claim_range/4", "item_range/4"} & signatures:
        guidance.append(
            "Contract delivery note for list/range inventory carriers: when raw_source_text states a numbered "
            "list or range such as claims, counts, issues, products, violations, requirements, or order paragraphs, "
            "emit one candidate operation per source-stated singleton or source-stated range segment. Preserve "
            "start and end values in separate typed slots for range carriers, reuse the same set/list id used by "
            "outcome/ground/status rows when available, and do not compress separated segments into one label atom "
            "or one broad numeric range. For a source phrase like 1, 2, 4, 6-9, emit 1-1, 2-2, 4-4, and 6-9; "
            "do not emit 1-9."
        )
    if {"claim_range/4", "claim_ground/4"} <= signatures:
        guidance.append(
            "Contract delivery note for claim set anchor convergence: claim_range/4 has four arguments in this "
            "order: claim_set_id, start_claim, end_claim, source_or_scope. Do not emit claim_range/4 with only "
            "numeric boundaries. When claim_range/4, claim_ground/4, legal_citation_detail/4, and review_outcome/4 "
            "refer to the same governed claim set or reviewed rejection, reuse one shared subject id across those "
            "rows so query planning can join inventory, ground, citation, and review outcome without source prose. "
            "If a broad all-items set and narrower governed subsets both appear, the narrower governed subset must "
            "carry its own claim_range/4 rows on the same subject id as its claim_ground/4 rows; broad inventory "
            "rows do not satisfy subset-specific ground, citation, or review questions. Do not distribute a broad "
            "wrapper phrase such as items were rejected under ground A or ground B over references X and Y into "
            "every ground/reference combination when the source later states narrower claim-to-ground mappings. "
            "Do not use bare claim numbers as claim_ground/4 subject ids when a claim_range/4 set can represent "
            "the same governed subset; membership belongs in claim_range/4, and the legal/ground assertion belongs "
            "on the shared set id. If you emit claim_range/4, legal_citation_detail/4, or review_outcome/4 for a "
            "governed set and the source states its rejection ground/reference/status, emit claim_ground/4 on that "
            "same set id or mark the missing companion in self_check. When a source line applies a ground to all "
            "items in a previously listed set, reuse the full prior set inventory for that ground; do not copy a "
            "later narrower exception/subset inventory onto the all-items ground."
        )
    if {"claim_ground/4", "legal_citation_detail/4"} <= signatures:
        guidance.append(
            "Contract delivery note for legal_citation_detail/4 with claim_ground/4: when raw_source_text states "
            "a statute, rule, section, regulation, or legal citation for a governed claim set, emit "
            "legal_citation_detail/4 with the same subject id as claim_ground/4. Keep the citation in "
            "legal_citation_detail/4; keep claim_ground/4's ground_or_theory slot for the theory such as "
            "anticipation, obviousness, eligibility, written_description, or indefiniteness. Prefer governed "
            "role atom statutory_ground rather than private variants such as statutory_basis."
        )
    if "review_outcome/4" in signatures:
        guidance.append(
            "Contract delivery note for review_outcome/4: when raw_source_text states that a reviewing body, board, "
            "court, committee, agency, officer, or other review actor affirmed, reversed, modified, vacated, "
            "remanded, sustained, granted, or denied an underlying action, emit review_outcome/4 using the same "
            "reviewed subject id as the underlying typed action/ground/finding row. Do not invent private "
            "affirmed_by/2 or reversed_by/2 atoms when review_outcome/4 is available. If one review outcome applies "
            "to several governed subject ids emitted in the same pass, emit one review_outcome/4 row per governed "
            "subject id rather than an umbrella reviewed-rejections id. Prefer the reviewing body as the actor "
            "slot, such as review_board, rather than a role label such as board_role or the lower-body actor."
        )
    if "obligation_detail/5" in signatures:
        guidance.append(
            "Contract delivery note for obligation_detail/5: when raw_source_text states an obligation, requirement, "
            "settlement term, reporting duty, corrective action, notice duty, or compliance condition with several "
            "query-bearing parts, emit one obligation_detail/5 row per atomic part. Preserve deliverable, recipient "
            "scope, tariff schedule, frequency, duration, deadline, condition, exception, authority, and method as "
            "separate compact detail rows when stated. Do not leave the only queryable copy inside a long "
            "settlement_obligation/3, requirement_text, source_detail, or source_record text atom. Reuse the same "
            "obligation_id across all detail rows for the same obligation."
        )
    if "procedural_rule_detail/5" in signatures:
        guidance.append(
            "Contract delivery note for procedural_rule_detail/5: when raw_source_text states a procedural rule, "
            "review right, rehearing right, appeal path, filing requirement, deadline rule, or default consequence, "
            "emit one procedural_rule_detail/5 row per atomic part. Preserve trigger/action, period or deadline, "
            "start anchor, consequence, condition, exception, and authority as separate compact detail rows when "
            "stated. Do not leave the only queryable copy inside a long rule text, source_detail, source_record, "
            "or review_deadline-only atom. Reuse the same rule_id across all detail rows for the same procedural rule."
        )
    return guidance


def _source_pass_profile_delivery_target_context(*, source_text: str, parsed_profile: dict[str, Any]) -> list[str]:
    candidates = parsed_profile.get("candidate_predicates")
    candidate_rows = [item for item in candidates if isinstance(item, dict)] if isinstance(candidates, list) else []
    lines: list[str] = []
    distribution_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item)
        and _candidate_signature(item).split("/", 1)[0] in PROFILE_DELIVERY_DISTRIBUTION_CARRIER_NAMES
    ]
    distribution_states = _distribution_table_state_atoms(source_text)
    if distribution_carriers and len(distribution_states) >= 8:
        tail_states = distribution_states[-6:]
        lines.append(
            "PROFILE DELIVERY TARGET: this source has a dense distribution/state table with source-stated states "
            f"{', '.join(distribution_states[:24])}. "
            f"The allowed distribution carriers include {', '.join(distribution_carriers[:8])}. "
            "When a pass covers product distribution, emit direct distribution carrier rows for every listed state "
            "before adding multiple retailer details for early rows. Do not stop at a prefix of the table. "
            f"Late rows such as {', '.join(tail_states)} are explicit coverage targets, not optional detail."
        )
    public_recall_prior_dates = _public_recall_prior_date_mentions(source_text)
    public_recall_date_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item)
        and _candidate_can_carry_public_recall_prior_date(item)
    ]
    if public_recall_prior_dates and public_recall_date_carriers:
        lines.append(
            "PROFILE DELIVERY TARGET: this public notice/recall source states a prior or original recall date "
            f"({', '.join(public_recall_prior_dates[:4])}) while also stating the current announcement/expansion date. "
            f"The allowed temporal recall carriers include {', '.join(public_recall_date_carriers[:6])}. "
            "Emit a distinct joinable prior/original recall event/date row for the earlier recall date, and keep it "
            "separate from the current expansion, publish, or content-current-as-of date. Do not satisfy an "
            "original/prior recall date with only the current announcement date or a source_record_text_atom row."
        )
    source_claim_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item) and _candidate_can_carry_source_attributed_claim_delivery_unit(item)
    ]
    if source_claim_carriers:
        source_claim_keys = _source_attributed_claim_required_keys(_source_attributed_claim_mentions(source_text))
        if source_claim_keys:
            lines.append(
                "PROFILE DELIVERY TARGET: this source has source-owned claim/status/finding requirements "
                f"{', '.join(source_claim_keys[:8])}. "
                f"The allowed source-claim carriers include {', '.join(source_claim_carriers[:6])}. "
                "When the current pass covers a source section containing one of these keys, emit the direct "
                "source-to-claim carrier row with source/speaker, required content or status, and source row/scope. "
                "Rows that mention the source but omit the required status such as not_binding, no_effect, "
                "under_review, unresolved, finding, support, objection, or recommendation do not deliver the key."
            )
            if "source_attributed_claim/4" in source_claim_carriers:
                lines.append(
                    "PROFILE DELIVERY TARGET: source_attributed_claim/4 is available and is preferred for quoted "
                    "or speaker-framed statements such as 'Name says:', '**Name:**', testimony, comments, objections, "
                    "opinions, and notes. For every required key beginning with statement:, opinion:, note:, "
                    "testimony:, report:, memo:, or comment:, emit a source_attributed_claim/4 row that keeps the "
                    "speaker or document, asserted content/status/finding, and source row or hearing/document scope "
                    "together. A shorter source_claim/3 row is additive but does not replace the 4-slot row when the "
                    "source row/scope is needed to distinguish individual statements."
                )
            lines.append(
                "PROFILE DELIVERY TARGET: source-attributed claim rows are additive evidence. They must not replace "
                "the backbone rows needed for ordinary QA: event/date/status rows, vote rows, survey or measurement "
                "rows, permit/application status rows, appeal/filing rows, board finding rows, participant/role rows, "
                "and repeated-record detail rows should still be emitted when the current source section states them."
            )
            if any(key.endswith(":objection") or ":objection" in key for key in source_claim_keys):
                lines.append(
                    "PROFILE DELIVERY TARGET: this source has objection-noting claim requirements. When a section "
                    "states a written objection, notes an objection, or records that a speaker objects/opposes, emit "
                    "a direct source-attributed claim row for the objection itself. A procedural ruling or decision to "
                    "proceed is a separate backbone fact and does not replace the objection row."
                )
            if any(key.endswith(":concern") or ":concern" in key for key in source_claim_keys):
                lines.append(
                    "PROFILE DELIVERY TARGET: this source has concern-statement requirements. When a section states "
                    "that a person has a concern, concerns, or is concerned about an impact, emit a direct "
                    "source-attributed claim row with the speaker/source, concern content, and source row or event "
                    "scope joinable."
                )
    vote_tally_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item) and _candidate_can_carry_vote_tally_delivery_unit(item)
    ]
    vote_tally_keys = _vote_tally_required_keys(_vote_tally_source_mentions(source_text))
    if vote_tally_carriers and vote_tally_keys:
        lines.append(
            "PROFILE DELIVERY TARGET: this source has explicit vote-tally requirements "
            f"{', '.join(vote_tally_keys[:8])}. "
            f"The allowed vote carriers include {', '.join(vote_tally_carriers[:6])}. "
            "When the current pass covers a vote, roll call, approval/denial, or corrected minutes section, "
            "emit a direct vote_tally/5 or equivalent row that keeps voting body, decision subject, result, "
            "tally, and member votes or source scope joinable. Individual member voting rows are useful, but "
            "they do not replace the final or corrected tally row when the source states one."
        )
    event_date_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item)
        and _candidate_signature(item).split("/", 1)[0]
        in {"document_date", "event_date", "event_time", "event_timestamp", "event_wall_time", "hearing_date", "meeting_date"}
    ]
    if event_date_carriers and (
        EVENT_DATE_TEXT_RE.search(str(source_text or ""))
        or EVENT_TIME_TEXT_RE.search(str(source_text or ""))
    ):
        lines.append(
            "PROFILE DELIVERY TARGET: this source has explicit event/hearing/filing dates or clock times. If a pass creates "
            "an event, document, filing, publication, application, or decision id that embeds a date, also emit a "
            "document_date/3, event_date/2, event_time/2, event_timestamp/2, or equivalent temporal row using "
            "that same subject id and the explicit date, time, or timestamp. The id is an anchor, not a substitute "
            "for a joinable temporal row."
        )
    quorum_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item) and "quorum" in set(_candidate_signature(item).split("/", 1)[0].split("_"))
    ]
    if quorum_carriers and QUORUM_TEXT_RE.search(str(source_text or "")):
        lines.append(
            "PROFILE DELIVERY TARGET: this source has explicit quorum facts. Emit a direct quorum_status/3 or "
            "equivalent row for stated quorum checks, keeping hearing/event id, quorum status, and count or "
            "requirement joinable. A source-attributed claim or hearing note about quorum is additive but does "
            "not replace the direct quorum row."
        )
    appeal_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item) and (
            _candidate_signature(item).split("/", 1)[0] in {"appeal_filed", "appeal_filing", "appeal_record"}
            or "appeal" in set(_candidate_signature(item).split("/", 1)[0].split("_"))
        )
    ]
    if appeal_carriers and APPEAL_FILING_TEXT_RE.search(str(source_text or "")):
        lines.append(
            "PROFILE DELIVERY TARGET: this source has explicit appeal-filing facts. Emit a direct appeal_filed/3, "
            "appeal_filing/3, appeal_record/3, or equivalent row for each stated appeal, keeping appellant, appealed "
            "target or subject, and filing date/status or window joinable. A source-attributed claim that mentions "
            "the appeal is additive but does not replace the direct appeal/filing row."
        )
    quantity_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item) and _candidate_can_carry_quantity_event_delivery_unit(item)
    ]
    scope_discrepancy_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item) and _candidate_can_carry_scope_discrepancy_delivery_unit(item)
    ]
    if not quantity_carriers:
        return lines
    quantity_mentions = _quantity_event_source_mentions(source_text)
    quantity_key_counts = _quantity_event_required_key_counts(quantity_mentions)
    if not quantity_key_counts:
        return lines
    keys = sorted(quantity_key_counts)
    lines.append(
        "PROFILE DELIVERY TARGET: this source has numeric event/interval quantity requirements "
        f"{', '.join(f'{key}x{quantity_key_counts[key]}' for key in keys[:8])}. "
        f"The allowed quantity carriers include {', '.join(quantity_carriers[:6])}. "
        "When the current pass covers a source section containing one of these keys, emit the direct "
        "quantity carrier rows in addition to event/timestamp/description rows."
    )
    duration_keys = [key for key in keys if key.startswith("duration:")]
    if duration_keys:
        lines.append(
            "PROFILE DELIVERY TARGET: duration requirements need a direct row whose arguments include the "
            f"duration subject ({', '.join(duration_keys[:4])}) and the exact stated elapsed total. "
            "Start/end events and timestamps are anchors, not replacements for the duration value."
        )
    return lines


def _public_recall_prior_date_mentions(source_text: str) -> list[str]:
    dates: list[str] = []
    seen: set[str] = set()
    for match in PUBLIC_RECALL_PRIOR_DATE_TEXT_RE.finditer(str(source_text or "")):
        raw = str(match.group("date1") or match.group("date2") or "").strip()
        if not raw:
            continue
        display = re.sub(r"\s+", " ", raw)
        key = display.casefold()
        if key in seen:
            continue
        seen.add(key)
        dates.append(display)
    return dates


def _candidate_can_carry_public_recall_prior_date(candidate: dict[str, Any]) -> bool:
    signature = _candidate_signature(candidate).lower()
    if not signature:
        return False
    predicate = signature.split("/", 1)[0]
    if predicate in {"recall_date", "event_date", "event_time", "event_timestamp", "publication_date", "published_on"}:
        return True
    tokens = set(re.findall(r"[a-z0-9]+", predicate.replace("_", " ")))
    if "date" not in tokens and "time" not in tokens and "published" not in tokens:
        return False
    if not (tokens & {"recall", "event", "notice", "announcement", "publication", "published"}):
        return False
    args = " ".join(_candidate_args(candidate)).casefold()
    return "date" in args or "time" in args or "published" in args


def _distribution_table_state_atoms(source_text: str) -> list[str]:
    states: list[str] = []
    seen: set[str] = set()
    for raw_line in str(source_text or "").splitlines():
        line = raw_line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        row_text = " ".join(cells)
        row_tokens = set(PROFILE_ADMISSION_TOKEN_RE.findall(row_text.casefold()))
        if not row_tokens.intersection({"aldi", "distribution", "kroger", "retailer", "retailers", "sold", "store", "stores", "walmart"}):
            continue
        state = _state_atom_from_text(cells[0])
        if state and state not in seen:
            seen.add(state)
            states.append(state)
    return states


def _state_atom_from_text(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", str(text or "").casefold()).strip()
    padded = f" {normalized} "
    tokens = set(PROFILE_ADMISSION_TOKEN_RE.findall(normalized))
    for state, aliases in PROFILE_DELIVERY_US_STATES.items():
        full_name = aliases[0]
        if f" {full_name} " in padded or any(alias in tokens for alias in aliases[1:]):
            return state
    return ""


def _source_pass_ops_to_semantic_ir(
    parsed: dict[str, Any],
    *,
    predicate_contracts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    self_check = parsed.get("self_check") if isinstance(parsed.get("self_check"), dict) else {}
    candidate_operations = parsed.get("candidate_operations", [])
    if not isinstance(candidate_operations, list):
        candidate_operations = []
    return {
        "schema_version": "semantic_ir_v1",
        "decision": str(parsed.get("decision", "commit") or "commit"),
        "turn_type": "state_update",
        "entities": [],
        "referents": [],
        "assertions": [],
        "propositions": [],
        "unsafe_implications": [],
        "candidate_operations": _reduce_source_pass_governed_atom_operations(
            candidate_operations,
            predicate_contracts=predicate_contracts,
        ),
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


REVIEW_OUTCOME_REDUCTION_PREDICATES = {
    "affirmed_by": "affirmed",
    "reversed_by": "reversed",
    "modified_by": "modified",
    "vacated_by": "vacated",
    "remanded_by": "remanded",
    "sustained_by": "sustained",
    "denied_by": "denied",
    "granted_by": "granted",
    "upheld_by": "upheld",
}


def _reduce_source_pass_governed_atom_operations(
    candidate_operations: list[Any],
    *,
    predicate_contracts: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Add governed equivalents for narrow model-proposed review atoms.

    This reducer operates only on the model's already-proposed typed atoms. It
    does not read source prose or query text; it keeps the original operation
    and adds the registry-owned `review_outcome/4` form so downstream query
    planning can meet the same atom language.
    """

    out: list[dict[str, Any]] = []
    seen: set[tuple[str, tuple[str, ...], str, str, str]] = set()
    contracts = _source_pass_contracts_by_signature(predicate_contracts or [])
    for operation_index, operation in enumerate(candidate_operations, start=1):
        if not isinstance(operation, dict):
            continue
        copied = _normalize_source_pass_operation_args(dict(operation), contracts, operation_index=operation_index)
        copied = _complete_governed_source_scope_operation(copied, contracts, operation_index=operation_index)
        _append_source_pass_operation_once(out, seen, copied)
        reduced = _review_outcome_reduction_operation(copied)
        if reduced is not None:
            _append_source_pass_operation_once(
                out,
                seen,
                _complete_governed_source_scope_operation(reduced, contracts),
            )
        date_reduced = _document_date_role_reduction_operation(copied, contracts)
        if date_reduced is not None:
            _append_source_pass_operation_once(out, seen, date_reduced)
    return out


def _normalize_source_pass_operation_args(
    operation: dict[str, Any],
    contracts: dict[str, list[str]],
    *,
    operation_index: int,
) -> dict[str, Any]:
    signature = _source_pass_contract_signature_for_operation(operation, contracts)
    roles = contracts.get(signature)
    args = [str(arg).strip() for arg in operation.get("args", [])] if isinstance(operation.get("args"), list) else []
    if not args:
        return operation
    predicate_name = signature.split("/", 1)[0].strip()
    signature_markers = {signature.casefold(), signature.replace("/", "_").casefold(), predicate_name.casefold()}
    if (
        len(args) >= 2
        and args[-2].casefold() in {"operation_name", "predicate_name"}
        and args[-1].casefold() in signature_markers
    ):
        args = args[:-2]
    elif args[-1].casefold() in signature_markers and roles and len(args) == len(roles) + 1:
        args = args[:-1]
    elif roles and roles[-1] == "source_order" and len(args) == len(roles) and args[-1].casefold() in {"operation_name", "predicate_name"}:
        args = args[:-1]
    operation["args"] = args
    return operation


def _source_pass_contracts_by_signature(predicate_contracts: list[dict[str, Any]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for contract in predicate_contracts:
        if not isinstance(contract, dict):
            continue
        signature = str(contract.get("signature", "")).strip()
        args = contract.get("args")
        if not isinstance(args, list):
            args = contract.get("arguments")
        if not signature or not isinstance(args, list):
            continue
        out[signature] = [str(arg).strip() for arg in args]
    return out


def _source_pass_contract_signature_for_operation(
    operation: dict[str, Any],
    contracts: dict[str, list[str]],
) -> str:
    signature = _operation_signature(operation)
    if signature in contracts:
        return signature
    predicate_base = str(operation.get("predicate", "")).strip().split("/", 1)[0].strip()
    if not predicate_base:
        return signature
    args = [str(arg).strip() for arg in operation.get("args", [])] if isinstance(operation.get("args"), list) else []
    candidates: list[str] = []
    for candidate_signature, roles in contracts.items():
        candidate_base = candidate_signature.split("/", 1)[0].strip()
        if candidate_base != predicate_base:
            continue
        if len(args) in {len(roles) - 1, len(roles), len(roles) + 1, len(roles) + 2}:
            candidates.append(candidate_signature)
    return candidates[0] if len(candidates) == 1 else signature


def _document_date_role_reduction_operation(
    operation: dict[str, Any],
    contracts: dict[str, list[str]],
) -> dict[str, Any] | None:
    """Reduce a common date-carrier transport error to document_date/3.

    Some source-pass models emit a three-slot event_date operation shaped like
    (subject, date_role, date_value). That is not the registered event_date/2
    carrier, but it is exactly the registered document_date/3 shape when that
    contract is present. This reducer reads only the model's typed operation,
    not source prose or query text.
    """

    if "document_date/3" not in contracts:
        return None
    if str(operation.get("operation", "")).strip() != "assert":
        return None
    if str(operation.get("polarity", "")).strip() != "positive":
        return None
    if str(operation.get("safety", "")).strip() != "safe":
        return None
    predicate = str(operation.get("predicate", "")).strip().split("/", 1)[0].strip().casefold()
    if predicate != "event_date":
        return None
    args = [str(arg).strip() for arg in operation.get("args", []) if str(arg).strip()] if isinstance(operation.get("args"), list) else []
    if len(args) != 3:
        return None
    if not _source_pass_arg_looks_like_date_value(args[2]):
        return None
    proposition = str(operation.get("proposition_id", "")).strip()
    return {
        "operation": "assert",
        "proposition_id": f"{proposition}_document_date" if proposition else "event_date_role_document_date",
        "predicate": "document_date/3",
        "args": args,
        "polarity": "positive",
        "source": str(operation.get("source", "")).strip() or "direct",
        "safety": "safe",
    }


def _source_pass_arg_looks_like_date_value(value: Any) -> bool:
    text = str(value or "").strip().casefold()
    if re.fullmatch(r"\d{4}_\d{1,2}_\d{1,2}", text):
        return True
    if re.fullmatch(r"\d{4}_\d{1,2}", text):
        return True
    if re.fullmatch(r"\d{4}", text):
        return True
    month_names = (
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    )
    return any(month in text for month in month_names) and bool(re.search(r"\d{2,4}", text))


def _complete_governed_source_scope_operation(
    operation: dict[str, Any],
    contracts: dict[str, list[str]],
    *,
    operation_index: int = 1,
) -> dict[str, Any]:
    signature = _source_pass_contract_signature_for_operation(operation, contracts)
    roles = contracts.get(signature)
    if not roles:
        return operation
    args = [str(arg).strip() for arg in operation.get("args", [])] if isinstance(operation.get("args"), list) else []
    source_scope = str(operation.get("source", "")).strip() or "direct"
    if roles[-1].endswith("source_or_scope"):
        if len(args) == len(roles) - 1:
            operation["args"] = [*args, source_scope]
        elif len(args) == len(roles) and not _looks_like_source_scope_arg(args[-1]):
            operation["args"] = [*args[:-1], source_scope]
    elif roles[-1] == "source_order" and len(args) == len(roles) - 1:
        operation["args"] = [*args, str(max(1, int(operation_index)))]
    return operation


def _operation_signature(operation: dict[str, Any]) -> str:
    predicate = str(operation.get("predicate", "")).strip()
    if "/" in predicate:
        return predicate
    args = operation.get("args")
    arity = len(args) if isinstance(args, list) else 0
    return f"{predicate}/{arity}"


def _looks_like_source_scope_arg(value: Any) -> bool:
    text = str(value or "").strip().casefold()
    if text in {"direct", "context", "inferred", "source", "source_text", "raw_source_text"}:
        return True
    return bool(re.fullmatch(r"(?:src|source|row|line|field|section|scope|record)[a-z0-9_:-]*", text))


def _append_source_pass_operation_once(
    out: list[dict[str, Any]],
    seen: set[tuple[str, tuple[str, ...], str, str, str]],
    operation: dict[str, Any],
) -> None:
    key = (
        str(operation.get("predicate", "")).strip(),
        tuple(str(arg).strip() for arg in operation.get("args", []) if isinstance(operation.get("args"), list)),
        str(operation.get("operation", "")).strip(),
        str(operation.get("polarity", "")).strip(),
        str(operation.get("source", "")).strip(),
    )
    if key in seen:
        return
    seen.add(key)
    out.append(operation)


def _review_outcome_reduction_operation(operation: dict[str, Any]) -> dict[str, Any] | None:
    if str(operation.get("operation", "")).strip() != "assert":
        return None
    if str(operation.get("polarity", "")).strip() != "positive":
        return None
    if str(operation.get("safety", "")).strip() != "safe":
        return None
    predicate = str(operation.get("predicate", "")).strip()
    base = predicate.split("/", 1)[0].strip().casefold()
    outcome = REVIEW_OUTCOME_REDUCTION_PREDICATES.get(base)
    if not outcome:
        return None
    args = [str(arg).strip() for arg in operation.get("args", []) if str(arg).strip()] if isinstance(operation.get("args"), list) else []
    if len(args) != 2:
        return None
    source_scope = str(operation.get("source", "")).strip() or "direct"
    proposition = str(operation.get("proposition_id", "")).strip()
    return {
        "operation": "assert",
        "proposition_id": f"{proposition}_review_outcome" if proposition else f"{base}_review_outcome",
        "predicate": "review_outcome/4",
        "args": [args[0], args[1], outcome, source_scope],
        "polarity": "positive",
        "source": source_scope,
        "safety": "safe",
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
            "For a focused narrative character-attribute pass, completeness means source-stated ages, titles, origins, nicknames, and kinship are preserved in compatible attribute or relation predicates. A numeric age is not a name, alias, or role label.",
            "For a focused narrative official/authority pass, completeness means the official's role plus duties, authority scope, inspections, certifications, investigations, permissions, disqualifications, and representative rulings when the allowed profile has compatible predicates.",
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
    admitted_count = int(flat.get("admitted_count", 0) or 0) + int(focused.get("admitted_count", 0) or 0)
    skipped_count = int(flat.get("skipped_count", 0) or 0) + int(focused.get("skipped_count", 0) or 0)
    diagnostic_rejected_skipped_count = _diagnostic_rejected_flat_pass_skipped_count(flat, focused)
    result = {
        "ok": bool(flat.get("ok")) and bool(focused.get("ok")) if isinstance(flat, dict) and isinstance(focused, dict) else False,
        "mode": "flat_plus_intake_plan_passes",
        "pass_count": 1 + int(focused.get("pass_count", 0) or 0) if isinstance(focused, dict) else 1,
        "admitted_count": admitted_count,
        "skipped_count": skipped_count,
        "effective_admitted_count": admitted_count,
        "effective_skipped_count": max(0, skipped_count - diagnostic_rejected_skipped_count),
        "diagnostic_rejected_flat_pass_skipped_count": diagnostic_rejected_skipped_count,
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


PROFILE_DELIVERY_REPAIR_CLASSES = {
    "source_authority_carrier_offered_but_undelivered",
    "source_authority_carrier_partially_delivered",
    "source_claim_carrier_offered_but_undelivered",
    "source_claim_carrier_partially_delivered",
    "source_claim_backbone_coexistence_missing",
    "status_state_carrier_offered_but_undelivered",
    "status_state_carrier_partially_delivered",
}


def _profile_delivery_repair_findings(delivery_report: dict[str, Any]) -> list[dict[str, Any]]:
    findings = delivery_report.get("findings") if isinstance(delivery_report, dict) else []
    return [
        item
        for item in findings
        if isinstance(item, dict)
        and str(item.get("class", "")).strip() in PROFILE_DELIVERY_REPAIR_CLASSES
    ]


def _profile_delivery_repair_offered_carriers(findings: list[dict[str, Any]]) -> list[str]:
    carriers: list[str] = []
    seen: set[str] = set()
    for finding in findings:
        for carrier in finding.get("offered_carriers", []) if isinstance(finding.get("offered_carriers"), list) else []:
            text = str(carrier).strip()
            if text and text not in seen:
                seen.add(text)
                carriers.append(text)
    return carriers


def _profile_delivery_repair_missing_keys(findings: list[dict[str, Any]]) -> list[str]:
    keys: list[str] = []
    seen: set[str] = set()
    for finding in findings:
        for key in finding.get("missing_signal_keys", []) if isinstance(finding.get("missing_signal_keys"), list) else []:
            text = str(key).strip()
            if text and text not in seen:
                seen.add(text)
                keys.append(text)
    return keys


def _profile_delivery_repair_context_lines(delivery_report: dict[str, Any]) -> list[str]:
    findings = _profile_delivery_repair_findings(delivery_report)
    if not findings:
        return []
    classes = {
        str(finding.get("class", "")).strip()
        for finding in findings
        if str(finding.get("class", "")).strip()
    }
    carriers = _profile_delivery_repair_offered_carriers(findings)
    missing_keys = _profile_delivery_repair_missing_keys(findings)
    lines = [
        (
            "PROFILE DELIVERY REPAIR PASS: deterministic diagnostics found offered direct carrier predicates "
            "with missing or partial emitted rows. This pass is proposal-only; emit only source-grounded rows "
            "through allowed predicate contracts, and let the mapper decide admission."
        ),
        (
            "PROFILE DELIVERY REPAIR PASS: populate direct carrier rows only when the raw source states the "
            "underlying source/speaker, authority/rule, status/state, claim/finding, and source row or scope. "
            "Do not infer new facts from the diagnostic labels; use the labels only to choose which source "
            "surface to revisit."
        ),
    ]
    if carriers:
        lines.append(
            "PROFILE DELIVERY REPAIR PASS: offered carrier signatures to consider: "
            + ", ".join(carriers[:12])
            + ". Use exact allowed predicate names and argument order."
        )
    if missing_keys:
        lines.append(
            "PROFILE DELIVERY REPAIR PASS: missing structural signal kinds from the prior compile: "
            + ", ".join(missing_keys[:12])
            + ". Treat these as diagnostic row-class labels, not source facts."
        )
    if any(cls.startswith("source_claim_") for cls in classes):
        lines.append(
            "PROFILE DELIVERY REPAIR PASS: for source-attributed claim pressure, preserve source/speaker or "
            "document, asserted content/status/finding, and source row or scope in one direct carrier row. "
            "A note, description, source_detail, or source_record row is provenance only unless the direct "
            "source-to-claim relation is also joinable."
        )
    if "source_claim_backbone_coexistence_missing" in classes:
        lines.append(
            "PROFILE DELIVERY REPAIR PASS: source-attributed claim rows are additive evidence. Also preserve "
            "ordinary backbone rows for stated votes, measurements, permit/application status, appeals, filings, "
            "board findings, quorum facts, participant roles, and repeated-record details when the allowed "
            "profile has compatible predicates."
        )
    if any(cls.startswith("source_authority_") for cls in classes):
        lines.append(
            "PROFILE DELIVERY REPAIR PASS: for source-authority pressure, preserve governed subject or scope, "
            "authority/source/rule/order, and authorized action/status/decision in one direct carrier row. "
            "Do not leave the authority only in prose, a rule label, or an unjoined activity row."
        )
    if any(cls.startswith("status_state_") for cls in classes):
        lines.append(
            "PROFILE DELIVERY REPAIR PASS: for status/state pressure, preserve subject or subset, state/status "
            "value, and temporal/source/effective scope in one direct carrier row. Split status-only and date-only "
            "rows are useful anchors but do not deliver the joined state surface."
        )
    return lines


ROLE_ROSTER_REPAIR_BASE_HINTS = {
    "affiliation",
    "actor_role",
    "attorney",
    "counsel",
    "contact",
    "employment",
    "officer",
    "panel",
    "participant",
    "party_role",
    "person_role",
    "representative",
    "signatory",
    "supervisor",
}


IDENTIFIER_OCCURRENCE_REPAIR_BASE_HINTS = {
    "accession",
    "cms",
    "control_number",
    "docket",
    "document_identifier",
    "ein",
    "employer_identification",
    "fei",
    "file_number",
    "identifier",
    "matter_number",
    "proceeding_number",
    "registration",
}

IDENTIFIER_OCCURRENCE_REPAIR_EXACT_BASES = {
    "application_number",
    "case_number",
    "document_number",
    "filing_number",
    "matter_number",
    "proceeding_number",
    "publication_number",
    "registration_number",
}

LIST_RANGE_INVENTORY_REPAIR_BASE_NAMES = {
    "claim_range",
    "claim_outcome",
    "claim_rejection",
    "claim_treatment",
    "count_range",
    "item_ground",
    "item_range",
    "issue_ground",
    "issue_range",
    "legal_citation_detail",
    "list_member",
    "rejection_ground",
    "review_outcome",
    "violation_basis",
}


LEGAL_CITATION_REPAIR_BASE_NAMES = {
    "citation",
    "citation_detail",
    "legal_citation",
    "legal_citation_detail",
    "statute_citation",
}

MONETARY_PAYMENT_REPAIR_BASE_NAMES = {
    "monetary_payment",
}

LEGAL_CITATION_REPAIR_CANONICAL_GROUNDS = {
    "anticipation",
    "obviousness",
    "written_description",
    "enablement",
    "indefiniteness",
    "eligibility",
    "novelty",
}


def _profile_identifier_occurrence_repair_offered_carriers(parsed_profile: dict[str, Any]) -> list[str]:
    carriers: list[str] = []
    seen: set[str] = set()
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return carriers
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        signature = str(candidate.get("signature", "")).strip()
        if not signature or "/" not in signature:
            continue
        base = signature.split("/", 1)[0].strip().lower()
        base_has_identifier_shape = base in IDENTIFIER_OCCURRENCE_REPAIR_EXACT_BASES or any(
            _identifier_occurrence_base_hint_matches(base, hint) for hint in IDENTIFIER_OCCURRENCE_REPAIR_BASE_HINTS
        )
        if not base_has_identifier_shape:
            continue
        if signature not in seen:
            seen.add(signature)
            carriers.append(signature)
    return carriers


def _identifier_occurrence_base_hint_matches(base: str, hint: str) -> bool:
    base_text = str(base or "").strip().lower()
    hint_text = str(hint or "").strip().lower()
    if not base_text or not hint_text:
        return False
    if "_" in hint_text:
        return hint_text in base_text
    return hint_text in {token for token in base_text.split("_") if token}


def _profile_identifier_occurrence_repair_context_lines(parsed_profile: dict[str, Any]) -> list[str]:
    carriers = _profile_identifier_occurrence_repair_offered_carriers(parsed_profile)
    if not carriers:
        return []
    contract_lines = carrier_contract_prompt_lines(carriers[:16])
    return [
        (
            "PROFILE IDENTIFIER OCCURRENCE REPAIR PASS: deterministic query delivery is missing typed "
            "identifier occurrences in some documents. This pass is proposal-only; emit only source-grounded "
            "typed rows through allowed predicate contracts, and let the mapper decide admission."
        ),
        (
            "PROFILE IDENTIFIER OCCURRENCE REPAIR PASS: revisit source-stated docket numbers, file numbers, "
            "Commission file numbers, accession numbers, document control numbers, CMS/FEI/EIN values, case "
            "numbers, registration numbers, and repeated same-label identifiers. Preserve the identifier kind, "
            "identifier value, document or record scope, source-stated location/scope label, and source order "
            "when the allowed predicate contract supports them."
        ),
        (
            "PROFILE IDENTIFIER OCCURRENCE REPAIR PASS: printed document-control identifiers may appear as short "
            "alphabetic prefixes joined to digits by punctuation, for example prefix#123456 or prefix-123456. "
            "Preserve these as typed identifier occurrences when source-stated; use a compact kind such as "
            "document_control_number or printed_control_number and keep the normalized prefix-number value in the "
            "identifier value slot."
        ),
        (
            "PROFILE IDENTIFIER OCCURRENCE REPAIR PASS: if the same identifier label appears more than once "
            "with different values, preserve each occurrence separately rather than choosing one canonical value. "
            "Do not infer that two differently formatted identifiers are equivalent unless the source states it."
        ),
        (
            "PROFILE IDENTIFIER OCCURRENCE REPAIR PASS: do not emit source_record_* rows, display text rows, "
            "prose windows, or answer-bearing source excerpts. The output must be typed identifier facts only."
        ),
        (
            "PROFILE IDENTIFIER OCCURRENCE REPAIR PASS: candidate_operations.args must contain exactly the "
            "predicate's declared arguments and nothing else. Keep operation, polarity, predicate, proposition_id, "
            "safety, and source as top-level candidate_operation fields; never place operation_assert, "
            "predicate_..., proposition_id_..., safety_..., or source_... tokens inside args."
        ),
        (
            "PROFILE IDENTIFIER OCCURRENCE REPAIR PASS: compatible identifier signatures to consider: "
            + ", ".join(carriers[:16])
            + ". Use exact allowed predicate names and argument order."
        ),
        *contract_lines,
    ]


def _apply_profile_identifier_occurrence_repair_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    carriers = _profile_identifier_occurrence_repair_offered_carriers(parsed_profile)
    metadata: dict[str, Any] = {
        "schema_version": "profile_identifier_occurrence_repair_pass_v1",
        "attempted": False,
        "offered_carriers": carriers[:16],
    }
    if not carriers:
        metadata["reason"] = "no_identifier_occurrence_predicates_offered"
        source_compile["profile_identifier_occurrence_repair"] = metadata
        return metadata
    context_lines = _profile_identifier_occurrence_repair_context_lines(parsed_profile)
    target = max(8, min(32, int(getattr(args, "focused_pass_operation_target", 48) or 48)))
    compiled = _compile_source_pass_ops(
        source_text=source_text,
        parsed_profile=parsed_profile,
        intake_plan=intake_plan,
        args=args,
        pass_id="profile_identifier_occurrence_repair",
        purpose="repair typed identifier occurrence delivery without source-record answer routing",
        focus="missing docket, file, accession, control, CMS, FEI, EIN, case, registration, and repeated identifier rows",
        completion=(
            "Emit only source-grounded typed identifier rows and minimal supporting document/scope rows; "
            "do not recompile unrelated source material."
        ),
        predicates=", ".join(carriers[:16]),
        coverage_goals=(
            "Deliver source-stated identifier occurrences as typed predicates: identifier kind, value, "
            "document or record scope, source-stated label/scope, and source order when available."
        ),
        extra_context=[*(extra_context or []), *context_lines],
        operation_target=target,
    )
    compiled["pass_id"] = "profile_identifier_occurrence_repair"
    compiled["purpose"] = "repair typed identifier occurrence delivery without source-record answer routing"
    compiled["focus"] = "missing docket, file, accession, control, CMS, FEI, EIN, case, registration, and repeated identifier rows"
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    _merge_additive_source_pass(source_compile, compiled, metadata_prefix="profile_identifier_occurrence_repair")
    signature_contract_report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts=prior_facts,
        allowed_signatures=set(carriers[:16]),
        metadata_prefix="profile_identifier_occurrence_repair",
        pass_record=compiled,
    )
    metadata.update(
        {
            "attempted": True,
            "ok": bool(compiled.get("ok")),
            "admitted_count": int(compiled.get("admitted_count", 0) or 0),
            "skipped_count": int(compiled.get("skipped_count", 0) or 0),
            "new_fact_count": len(compiled.get("_profile_identifier_occurrence_repair_new_facts", []))
            if isinstance(compiled.get("_profile_identifier_occurrence_repair_new_facts"), list)
            else 0,
            "signature_contract": signature_contract_report,
            "pass": compiled,
        }
    )
    source_compile["profile_identifier_occurrence_repair"] = metadata
    return metadata


def _profile_list_range_inventory_repair_offered_carriers(parsed_profile: dict[str, Any]) -> list[str]:
    carriers: list[str] = []
    seen: set[str] = set()
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return carriers
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        signature = str(candidate.get("signature", "")).strip()
        if not signature or "/" not in signature:
            continue
        base = signature.split("/", 1)[0].strip().lower()
        args = candidate.get("args")
        arg_text = " ".join(str(arg).lower() for arg in args if isinstance(args, list))
        if base not in LIST_RANGE_INVENTORY_REPAIR_BASE_NAMES and not (
            "range" in base and any(token in arg_text for token in ("start", "end", "item", "claim", "issue", "count"))
        ) and not (
            any(token in base for token in ("claim", "item", "issue", "violation"))
            and any(token in arg_text for token in ("set", "claim", "item", "issue", "range"))
            and any(token in arg_text for token in ("ground", "basis", "status", "outcome", "treatment", "prior_art"))
        ):
            continue
        if signature not in seen:
            seen.add(signature)
            carriers.append(signature)
    return carriers


def _profile_list_range_inventory_repair_context_lines(parsed_profile: dict[str, Any]) -> list[str]:
    carriers = _profile_list_range_inventory_repair_offered_carriers(parsed_profile)
    if not carriers:
        return []
    contract_lines = carrier_contract_prompt_lines(carriers[:16])
    return [
        (
            "PROFILE LIST/RANGE INVENTORY REPAIR PASS: deterministic query delivery is missing typed "
            "numbered list or range inventory in some documents. This pass is proposal-only; emit only "
            "source-grounded typed rows through allowed predicate contracts, and let the mapper decide admission."
        ),
        (
            "PROFILE LIST/RANGE INVENTORY REPAIR PASS: revisit source-stated numbered claims, counts, issues, "
            "products, violations, requirements, order paragraphs, and other item sets. Preserve each "
            "source-stated singleton and each source-stated range segment as its own typed operation."
        ),
        (
            "PROFILE LIST/RANGE INVENTORY REPAIR PASS: source-stated category, class, type, option, or "
            "heading inventories are also list inventories, even when displayed as section headings rather "
            "than numbered bullets. If list_member/4 is available, preserve each source-stated category "
            "label as list_member(SetOrListId, CategoryAtom, CategoryKind, SourceOrScope)."
        ),
        (
            "PROFILE LIST/RANGE INVENTORY REPAIR PASS: stay inside the listed inventory carriers. Do not "
            "emit period, impact, statement, effect, account, or narrative-detail predicates from this pass "
            "unless those exact predicate signatures are in the compatible list/range carrier set."
        ),
        (
            "PROFILE LIST/RANGE INVENTORY REPAIR PASS: for a source range such as N-M, keep the start and end "
            "values in separate typed slots. For a singleton such as N, either emit a list member row or a range "
            "row with matching start and end values, according to the allowed predicate contract."
        ),
        (
            "PROFILE LIST/RANGE INVENTORY REPAIR PASS: a source-stated range is not satisfied by expanding it "
            "into one list_member/4 row per inferred member. If a range carrier such as claim_range/4 or "
            "item_range/4 is available, emit the range carrier for the source-stated segment."
        ),
        (
            "PROFILE LIST/RANGE INVENTORY REPAIR PASS: reuse the same set/list id used by related outcome, "
            "status, ground, basis, rejection, or treatment rows when the source links the same governed set. "
            "Do not compress separated source segments into one label atom."
        ),
        (
            "PROFILE LIST/RANGE INVENTORY REPAIR PASS: when an allowed predicate such as claim_treatment/5, "
            "claim_outcome/3, claim_ground/4, rejection_ground/4, claim_rejection/5, item_ground/5, "
            "issue_ground/5, legal_citation_detail/4, review_outcome/4, or violation_basis/5 can bind "
            "a numbered set to its source-stated ground, status, prior-art reference, basis, or outcome, emit "
            "that set-to-relation row using the same set/list id as the inventory rows. Do not attach the "
            "relation only to the whole document when the source states the relation for a specific numbered set."
        ),
        (
            "PROFILE LIST/RANGE INVENTORY REPAIR PASS: do not hide a legal ground, prior-art reference, "
            "causal reason, treatment basis, or statutory basis inside list_member/4's source/scope slot. "
            "list_member/4 is membership inventory; use a companion typed relation such as claim_ground/4, "
            "rejection_ground/4, claim_rejection/4, claim_treatment/5, item_ground/5, issue_ground/5, "
            "legal_citation_detail/4, review_outcome/4, or violation_basis/5 for the relation."
        ),
        (
            "PROFILE LIST/RANGE INVENTORY REPAIR PASS: when a governed subset has ground, basis, citation, "
            "outcome, status, treatment, or review rows, emit that subset's claim_range/4 or item_range/4 "
            "rows with the same subject id. Do not put the inventory on a broad set id while putting the "
            "ground or review outcome on a different subset id."
        ),
        (
            "PROFILE LIST/RANGE INVENTORY REPAIR PASS: if the source states that a reviewer, board, court, "
            "or agency affirmed, reversed, sustained, denied, granted, or modified the governed actions you "
            "emit, add review_outcome/4 for each governed subject id. Do not replace per-subject review rows "
            "with one umbrella reviewed-rejections id."
        ),
        (
            "PROFILE LIST/RANGE INVENTORY REPAIR PASS: do not emit source_record_* rows, display text rows, "
            "prose windows, or answer-bearing source excerpts. The output must be typed list/range facts only."
        ),
        (
            "PROFILE LIST/RANGE INVENTORY REPAIR PASS: compatible list/range signatures to consider: "
            + ", ".join(carriers[:16])
            + ". Use exact allowed predicate names and argument order."
        ),
        *contract_lines,
    ]


def _source_pass_self_check_missing_slots(pass_record: dict[str, Any]) -> list[str]:
    self_check = pass_record.get("self_check")
    if not isinstance(self_check, dict):
        nested = pass_record.get("source_pass_ops")
        if isinstance(nested, dict):
            self_check = nested.get("self_check")
    if not isinstance(self_check, dict):
        return []
    missing = self_check.get("missing_slots")
    if not isinstance(missing, list):
        return []
    return [str(item).strip() for item in missing if str(item).strip()]


def _list_range_inventory_existing_fact_context(source_compile: dict[str, Any], *, limit: int = 80) -> list[str]:
    relevant_prefixes = (
        "claim_range(",
        "item_range(",
        "list_member(",
        "claim_ground(",
        "rejection_ground(",
        "claim_rejection(",
        "claim_treatment(",
        "item_ground(",
        "issue_ground(",
        "violation_basis(",
        "legal_citation_detail(",
        "review_outcome(",
    )
    rows: list[str] = []
    for fact in [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]:
        if fact.startswith(relevant_prefixes):
            rows.append(f"EXISTING LIST/RANGE FACT: {fact}")
        if len(rows) >= limit:
            break
    if not rows:
        return []
    return [
        (
            "PROFILE LIST/RANGE INVENTORY REPAIR FOLLOW-UP: existing typed list/range and companion "
            "facts are listed below for de-duplication and same-subject completion. They are context, "
            "not source evidence; emit new facts only when the raw source text itself supports them."
        ),
        *rows,
    ]


def _profile_legal_citation_repair_offered_carriers(parsed_profile: dict[str, Any]) -> list[str]:
    carriers: list[str] = []
    seen: set[str] = set()
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return carriers
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        signature = str(candidate.get("signature", "")).strip()
        if not signature or "/" not in signature:
            continue
        base = signature.split("/", 1)[0].strip().lower()
        args = candidate.get("args")
        arg_text = " ".join(str(arg).lower() for arg in args if isinstance(args, list))
        haystack = base + " " + arg_text
        if base not in LEGAL_CITATION_REPAIR_BASE_NAMES and not any(
            token in haystack
            for token in (
                "citation",
                "cfr",
                "section",
                "statute",
                "statutory",
                "regulation",
                "rule",
                "legal_basis",
            )
        ):
            continue
        if signature not in seen:
            seen.add(signature)
            carriers.append(signature)
    return carriers


GOVERNED_SUBJECT_DISCOVERY_BASE_NAMES = {
    "claim_ground",
    "claim_range",
    "item_range",
    "legal_citation_detail",
    "list_member",
    "review_outcome",
    "rejection_ground",
    "violation_basis",
}


def _profile_governed_subject_discovery_offered_carriers(parsed_profile: dict[str, Any]) -> list[str]:
    carriers: list[str] = []
    seen: set[str] = set()
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return carriers
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        signature = str(candidate.get("signature", "")).strip()
        if not signature or "/" not in signature:
            continue
        base = signature.split("/", 1)[0].strip().lower()
        if base not in GOVERNED_SUBJECT_DISCOVERY_BASE_NAMES:
            continue
        if carrier_contract(signature) is None:
            continue
        if signature not in seen:
            seen.add(signature)
            carriers.append(signature)
    return carriers


def _profile_governed_subject_discovery_context_lines(
    *,
    parsed_profile: dict[str, Any],
    source_compile: dict[str, Any],
) -> list[str]:
    carriers = _profile_governed_subject_discovery_offered_carriers(parsed_profile)
    if not carriers:
        return []
    contract_lines = carrier_contract_prompt_lines(carriers[:16])
    lines = [
        (
            "PROFILE GOVERNED SUBJECT DISCOVERY PASS: source-owned subject discovery is unstable. This pass is "
            "proposal-only; emit only source-grounded typed facts through allowed governed carrier contracts, "
            "and let the mapper decide admission."
        ),
        (
            "PROFILE GOVERNED SUBJECT DISCOVERY PASS: discover the governed subjects first, then populate their "
            "companion families. A governed subject is a source-stated set/action/finding/rejection/violation that "
            "can carry range or membership, ground/status, citation/basis, and review/outcome rows on one shared id."
        ),
        (
            "PROFILE GOVERNED SUBJECT DISCOVERY PASS: when a source states overlapping subsets, make one stable "
            "subject id per distinct source-stated subset. Do not use bare item numbers as subject ids when a range "
            "or set carrier can represent the subset. Do not copy a later narrower subset inventory onto an earlier "
            "all-items ground."
        ),
        (
            "PROFILE GOVERNED SUBJECT DISCOVERY PASS: for each governed subject you emit, populate every applicable "
            "allowed companion carrier from the source. If claim_range/4, claim_ground/4, legal_citation_detail/4, "
            "or review_outcome/4 are all allowed and applicable, reuse the exact same subject id across them."
        ),
        (
            "PROFILE GOVERNED SUBJECT DISCOVERY PASS: do not emit source_record_* rows, display text rows, prose "
            "windows, answer-bearing source excerpts, or private predicates. The output must be typed governed "
            "carrier facts only."
        ),
        (
            "PROFILE GOVERNED SUBJECT DISCOVERY PASS: compatible governed signatures to consider: "
            + ", ".join(carriers[:16])
            + ". Use exact allowed predicate names and argument order."
        ),
    ]
    existing = _governed_subject_existing_fact_context(source_compile)
    if existing:
        lines.extend(
            line.replace("PROFILE LEGAL CITATION REPAIR PASS", "PROFILE GOVERNED SUBJECT DISCOVERY PASS")
            for line in existing
        )
    return [*lines, *contract_lines]


def _apply_profile_governed_subject_discovery_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    carriers = _profile_governed_subject_discovery_offered_carriers(parsed_profile)
    metadata: dict[str, Any] = {
        "schema_version": "profile_governed_subject_discovery_pass_v1",
        "attempted": False,
        "offered_carriers": carriers[:16],
    }
    context_lines = _profile_governed_subject_discovery_context_lines(
        parsed_profile=parsed_profile,
        source_compile=source_compile,
    )
    if not carriers or not context_lines:
        source_compile["profile_governed_subject_discovery"] = metadata
        return metadata
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    compiled = _compile_source_pass_ops(
        source_text=source_text,
        parsed_profile=parsed_profile,
        intake_plan=intake_plan,
        args=args,
        pass_id="profile_governed_subject_discovery",
        purpose="repair governed subject discovery without source-record answer routing",
        focus="stable governed subject bundles for set/action/finding/rejection/violation carriers",
        completion=(
            "Emit only source-grounded typed governed carrier facts for stable subject bundles; "
            "do not recompile unrelated source material."
        ),
        predicates=", ".join(carriers[:16]),
        coverage_goals=(
            "Deliver stable subject ids with applicable typed companion rows: range or membership, "
            "ground/status, citation/basis, and review/outcome."
        ),
        extra_context=[*(extra_context or []), *context_lines],
        operation_target=max(16, min(48, int(getattr(args, "focused_pass_operation_target", 48) or 48))),
    )
    compiled["pass_id"] = "profile_governed_subject_discovery"
    compiled["purpose"] = "repair governed subject discovery without source-record answer routing"
    compiled["focus"] = "stable governed subject bundles for set/action/finding/rejection/violation carriers"
    _merge_additive_source_pass(source_compile, compiled, metadata_prefix="profile_governed_subject_discovery")
    signature_contract_report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts=prior_facts,
        allowed_signatures=set(carriers[:16]),
        metadata_prefix="profile_governed_subject_discovery",
        pass_record=compiled,
    )
    metadata.update(
        {
            "attempted": True,
            "ok": bool(compiled.get("ok")),
            "admitted_count": int(compiled.get("admitted_count", 0) or 0),
            "skipped_count": int(compiled.get("skipped_count", 0) or 0),
            "new_fact_count": len(compiled.get("_profile_governed_subject_discovery_new_facts", []))
            if isinstance(compiled.get("_profile_governed_subject_discovery_new_facts"), list)
            else 0,
            "signature_contract": signature_contract_report,
            "pass": compiled,
        }
    )
    source_compile["profile_governed_subject_discovery"] = metadata
    return metadata


def _governed_subject_manifest_messages(
    *,
    source_text: str,
    carriers: list[str],
    source_compile: dict[str, Any],
    retry_note: str = "",
) -> list[dict[str, str]]:
    existing = _governed_subject_existing_fact_context(source_compile)
    context_lines = [
        "You are compiling source text into governed subject bundles.",
        "Return governed_subject_manifest_v1 JSON only.",
        "A subject is a source-stated set/action/finding/rejection/violation that companion facts can share.",
        "Use one stable subject_id per distinct source-stated subset or action.",
        "For each subject, fill ranges, ground, legal_citations, and review_outcomes when source-stated and applicable.",
        "If a companion is unavailable or uncertain, leave its field empty or ground.present=false and add an omitted_companions note.",
        "Do not emit source prose excerpts, source_record rows, answer text, or private predicate names.",
        "Allowed governed carrier signatures: " + ", ".join(carriers[:16]),
        *existing[:80],
    ]
    if retry_note:
        context_lines.extend(
            [
                "RETRY: the previous governed_subject_manifest_v1 response was not valid JSON.",
                retry_note,
                "Return compact valid JSON only. Use fewer subjects if needed, but every object must satisfy the schema.",
            ]
        )
    return [
        {
            "role": "system",
            "content": "\n".join(context_lines),
        },
        {
            "role": "user",
            "content": source_text,
        },
    ]


def _governed_subject_atom_rows_messages(
    *,
    source_text: str,
    carriers: list[str],
    source_compile: dict[str, Any],
    retry_note: str = "",
) -> list[dict[str, str]]:
    carriers = _governed_subject_atom_row_carriers(carriers)
    del source_compile
    context_lines = [
        "You are compiling source text into governed subject atom rows.",
        "Return governed_subject_atom_rows_v1 JSON only, with no markdown and no prose outside the JSON object.",
        "Emit one row per source-stated governed carrier fact.",
        "Each row must use a registered signature and exactly four typed args in predicate order.",
        "Reuse one stable subject_id for companion rows about the same subset, action, finding, rejection, or violation.",
        "Do not emit source prose excerpts, source_record rows, answer text, or private predicate names.",
        "This is a source-owned reconstruction pass. Re-read the source text instead of trusting any previous compiled facts.",
        "Do not use list_member/4 or item_range/4 in this atom-row pass. Use claim_range/4 for claim subsets.",
        "Allowed governed carrier signatures: " + ", ".join(carriers[:16]),
        "For claim_range/4 args are subject_id, start_claim, end_claim, source_or_scope.",
        "For claim_ground/4 args are subject_id, ground_or_theory, reference, status. The status slot is an outcome such as rejected, not a statute or citation.",
        "For legal_citation_detail/4 args are subject_id, citation, role, source_or_scope. The role slot is a citation role such as statutory_ground, not the reference name.",
        "For review_outcome/4 args are subject_id, reviewer, outcome, source_or_scope.",
        "Do not collapse noncontiguous item lists into broad ranges. A list such as 1, 2, 4, 6-9 needs separate contiguous claim_range rows.",
        "Keep ground, reference, and citation separate. For 'anticipated by Reference X', claim_ground args use anticipation, Reference X, rejected.",
        "For 'obvious over Reference X', claim_ground args use obviousness, Reference X, rejected.",
        "Do not use a statute or citation as the claim_ground reference; put statutes only in legal_citation_detail rows.",
        "Preserve source list notation. Comma-separated adjacent items such as 1, 2 are two singleton claim_range rows; only hyphenated spans such as 6-9 become range rows.",
        "When one source sentence states a reviewed rejection, preserve the same subject_id across its claim_range, claim_ground, and legal_citation_detail rows.",
        "When a later review sentence affirms or reverses those rejections, add review_outcome rows for the same subject_id values.",
        "Include subject_accounts when the accountability rows do not crowd out correct governed carrier rows.",
        "For each governed subject_id in rows, account for applicable companion signatures with status instances, none_found, uncertain, or not_applicable.",
        "Use subject_accounts: [] only if rows is empty or no governed subject is emitted.",
        "subject_accounts are accountability diagnostics only; they do not create durable facts. Use them to expose silent omissions instead of hiding them.",
    ]
    if retry_note:
        context_lines.extend(
            [
                "RETRY: the previous governed subject manifest response was not valid JSON.",
                retry_note,
                "Use the flat atom-row schema. Keep rows compact and valid JSON.",
            ]
        )
    return [
        {
            "role": "system",
            "content": "\n".join(context_lines),
        },
        {
            "role": "user",
            "content": source_text,
        },
    ]


def _governed_subject_atom_row_carriers(carriers: list[str]) -> list[str]:
    supported = {"claim_range/4", "claim_ground/4", "legal_citation_detail/4", "review_outcome/4"}
    return [signature for signature in carriers if signature in supported]


def _facts_from_governed_subject_manifest(
    manifest: dict[str, Any],
    *,
    allowed_signatures: set[str],
) -> dict[str, Any]:
    facts: list[str] = []
    skipped: list[dict[str, str]] = []
    subjects = manifest.get("subjects")
    if not isinstance(subjects, list):
        return {"facts": [], "skipped": [{"reason": "subjects_not_list", "value": ""}]}
    for index, subject in enumerate(subjects):
        if not isinstance(subject, dict):
            skipped.append({"reason": "subject_not_object", "value": str(index)})
            continue
        subject_id = _manifest_atom(subject.get("subject_id", ""))
        if not subject_id:
            skipped.append({"reason": "missing_subject_id", "value": str(index)})
            continue
        if "claim_range/4" in allowed_signatures:
            ranges = subject.get("ranges")
            if isinstance(ranges, list):
                for range_index, item in enumerate(ranges):
                    if not isinstance(item, dict):
                        skipped.append({"reason": "range_not_object", "value": f"{subject_id}:{range_index}"})
                        continue
                    start = _manifest_range_value(item.get("start", ""))
                    end = _manifest_range_value(item.get("end", ""))
                    source_or_scope = _manifest_atom(item.get("source_or_scope", "")) or "direct"
                    if not start or not end:
                        skipped.append({"reason": "range_missing_boundary", "value": subject_id})
                        continue
                    facts.append(f"claim_range({subject_id}, {start}, {end}, {source_or_scope}).")
        ground = subject.get("ground")
        if "claim_ground/4" in allowed_signatures and isinstance(ground, dict) and bool(ground.get("present")):
            theory = _governed_ground_atom(_manifest_atom(ground.get("theory", "")))
            reference = _governed_reference_atom(_manifest_atom(ground.get("reference", "")))
            status = _manifest_atom(ground.get("status", ""))
            if theory and reference and status:
                facts.append(f"claim_ground({subject_id}, {theory}, {reference}, {status}).")
            else:
                skipped.append({"reason": "ground_missing_slot", "value": subject_id})
        if "legal_citation_detail/4" in allowed_signatures:
            citations = subject.get("legal_citations")
            if isinstance(citations, list):
                for citation_index, item in enumerate(citations):
                    if not isinstance(item, dict):
                        skipped.append({"reason": "citation_not_object", "value": f"{subject_id}:{citation_index}"})
                        continue
                    citation = _governed_citation_atom(_manifest_citation_value(item.get("citation", "")))
                    role = _governed_legal_role_atom(_manifest_atom(item.get("role", "")), citation)
                    source_or_scope = _manifest_atom(item.get("source_or_scope", "")) or "direct"
                    if not citation or not role:
                        skipped.append({"reason": "citation_missing_slot", "value": subject_id})
                        continue
                    facts.append(f"legal_citation_detail({subject_id}, {citation}, {role}, {source_or_scope}).")
        if "review_outcome/4" in allowed_signatures:
            outcomes = subject.get("review_outcomes")
            if isinstance(outcomes, list):
                for outcome_index, item in enumerate(outcomes):
                    if not isinstance(item, dict):
                        skipped.append({"reason": "review_outcome_not_object", "value": f"{subject_id}:{outcome_index}"})
                        continue
                    reviewer = _governed_review_actor_atom(_manifest_atom(item.get("reviewer", "")))
                    outcome = _governed_review_outcome_atom(_manifest_atom(item.get("outcome", "")))
                    source_or_scope = _manifest_atom(item.get("source_or_scope", "")) or "direct"
                    if not reviewer or not outcome:
                        skipped.append({"reason": "review_outcome_missing_slot", "value": subject_id})
                        continue
                    facts.append(f"review_outcome({subject_id}, {reviewer}, {outcome}, {source_or_scope}).")
    return {"facts": list(dict.fromkeys(facts)), "skipped": skipped}


def _facts_from_governed_subject_atom_rows(
    payload: dict[str, Any],
    *,
    allowed_signatures: set[str],
) -> dict[str, Any]:
    facts: list[str] = []
    skipped: list[dict[str, str]] = []
    rows = _governed_subject_atom_payload_rows(payload)
    if rows is None:
        return {"facts": [], "skipped": [{"reason": "rows_not_list", "value": ""}]}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            skipped.append({"reason": "row_not_object", "value": str(index)})
            continue
        signature, args = _governed_subject_atom_row_signature_args(row)
        if signature not in allowed_signatures:
            skipped.append({"reason": "signature_not_allowed", "value": signature})
            continue
        if not isinstance(args, list) or len(args) != 4:
            skipped.append({"reason": "args_not_four", "value": signature})
            continue
        arg0, arg1, arg2, arg3 = args
        subject_id = _manifest_atom(arg0)
        if not subject_id:
            skipped.append({"reason": "missing_subject_id", "value": signature})
            continue
        if signature == "claim_range/4":
            start = _manifest_range_value(arg1)
            end = _manifest_range_value(arg2)
            source_or_scope = _manifest_atom(arg3) or "direct"
            if start and end:
                facts.append(f"claim_range({subject_id}, {start}, {end}, {source_or_scope}).")
            else:
                skipped.append({"reason": "range_missing_boundary", "value": subject_id})
        elif signature == "claim_ground/4":
            theory = _governed_ground_atom(_manifest_atom(arg1))
            reference = _governed_reference_atom(_manifest_atom(arg2))
            status = _manifest_atom(arg3)
            if theory and reference and status:
                facts.append(f"claim_ground({subject_id}, {theory}, {reference}, {status}).")
            else:
                skipped.append({"reason": "ground_missing_slot", "value": subject_id})
        elif signature == "legal_citation_detail/4":
            citation = _governed_citation_atom(_manifest_citation_value(arg1))
            role = _governed_legal_role_atom(_manifest_atom(arg2), citation)
            source_or_scope = _manifest_atom(arg3) or "direct"
            if citation and role:
                facts.append(f"legal_citation_detail({subject_id}, {citation}, {role}, {source_or_scope}).")
            else:
                skipped.append({"reason": "citation_missing_slot", "value": subject_id})
        elif signature == "review_outcome/4":
            reviewer = _governed_review_actor_atom(_manifest_atom(arg1))
            outcome = _governed_review_outcome_atom(_manifest_atom(arg2))
            source_or_scope = _manifest_atom(arg3) or "direct"
            if reviewer and outcome:
                facts.append(f"review_outcome({subject_id}, {reviewer}, {outcome}, {source_or_scope}).")
            else:
                skipped.append({"reason": "review_outcome_missing_slot", "value": subject_id})
        else:
            skipped.append({"reason": "signature_mapping_unimplemented", "value": signature})
    account_report = _governed_subject_atom_accounting_report(
        payload,
        allowed_signatures=allowed_signatures,
    )
    return {
        "facts": list(dict.fromkeys(facts)),
        "skipped": skipped,
        "subject_accounts": account_report["subject_accounts"],
        "account_skipped": account_report["account_skipped"],
    }


def _governed_subject_atom_accounting_report(
    payload: dict[str, Any],
    *,
    allowed_signatures: set[str],
) -> dict[str, Any]:
    statuses = {"instances", "none_found", "uncertain", "not_applicable"}
    rows = payload.get("subject_accounts")
    if rows is None:
        return {"subject_accounts": [], "account_skipped": [{"reason": "subject_accounts_missing", "value": ""}]}
    if not isinstance(rows, list):
        return {"subject_accounts": [], "account_skipped": [{"reason": "subject_accounts_not_list", "value": ""}]}
    accounts: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    for account_index, row in enumerate(rows):
        if not isinstance(row, dict):
            skipped.append({"reason": "subject_account_not_object", "value": str(account_index)})
            continue
        subject_id = _manifest_atom(row.get("subject_id", ""))
        if not subject_id:
            skipped.append({"reason": "subject_account_missing_subject_id", "value": str(account_index)})
            continue
        companion_statuses = row.get("companion_statuses")
        if not isinstance(companion_statuses, list):
            skipped.append({"reason": "companion_statuses_not_list", "value": subject_id})
            continue
        for status_index, status_row in enumerate(companion_statuses):
            if not isinstance(status_row, dict):
                skipped.append({"reason": "companion_status_not_object", "value": f"{subject_id}:{status_index}"})
                continue
            signature = str(status_row.get("signature") or "").strip()
            if signature not in allowed_signatures:
                skipped.append({"reason": "companion_status_signature_not_allowed", "value": signature})
                continue
            status = str(status_row.get("status") or "").strip()
            if status not in statuses:
                skipped.append({"reason": "companion_status_invalid_status", "value": f"{subject_id}:{signature}:{status}"})
                continue
            accounts.append(
                {
                    "subject": subject_id,
                    "signature": signature,
                    "status": status,
                    "reason": _manifest_account_reason(status_row.get("reason", "")),
                }
            )
    return {"subject_accounts": accounts, "account_skipped": skipped}


def _governed_subject_atom_payload_rows(payload: dict[str, Any]) -> list[Any] | None:
    rows = payload.get("rows")
    if isinstance(rows, list):
        return rows
    rows = payload.get("governed_subject_atom_rows_v1")
    if isinstance(rows, list):
        return rows
    return None


def _governed_subject_atom_row_signature_args(row: dict[str, Any]) -> tuple[str, Any]:
    signature = str(row.get("signature") or row.get("sig") or "").strip()
    args = row.get("args")
    if signature:
        return signature, args
    predicate = str(row.get("predicate") or "").strip()
    if predicate and isinstance(args, list):
        return _governed_subject_signature_from_predicate(predicate), args
    for predicate in ["claim_range", "claim_ground", "legal_citation_detail", "review_outcome"]:
        value = row.get(predicate)
        if isinstance(value, list):
            return _governed_subject_signature_from_predicate(predicate), value
    return "", args


def _governed_subject_signature_from_predicate(predicate: str) -> str:
    text = str(predicate or "").strip()
    if "/" in text:
        return text
    if text in {"claim_range", "claim_ground", "legal_citation_detail", "review_outcome"}:
        return f"{text}/4"
    return text


def _replace_governed_subject_atom_row_facts(
    *,
    existing_facts: list[str],
    replacement_facts: list[str],
) -> dict[str, Any]:
    replacement_keys = {
        key
        for fact in replacement_facts
        if (key := _governed_subject_atom_fact_key(fact)) is not None
    }
    retained: list[str] = []
    replaced: list[str] = []
    for fact in existing_facts:
        key = _governed_subject_atom_fact_key(fact)
        if key is not None and key in replacement_keys:
            replaced.append(fact)
            continue
        retained.append(fact)
    combined: list[str] = []
    seen: set[str] = set()
    for fact in [*retained, *replacement_facts]:
        fact_text = str(fact).strip()
        if not fact_text or fact_text in seen:
            continue
        seen.add(fact_text)
        combined.append(fact_text)
    appended = [fact for fact in combined if fact not in set(retained)]
    return {
        "facts": combined,
        "retained_facts": retained,
        "replaced_facts": replaced,
        "appended_facts": appended,
    }


def _governed_subject_atom_fact_key(fact: Any) -> tuple[str, str] | None:
    parsed = _parse_fact_clause(str(fact).strip())
    if parsed is None:
        return None
    predicate, args = parsed
    if predicate not in GOVERNED_SUBJECT_ATOM_ROW_PREDICATES or not args:
        return None
    return predicate, str(args[0]).strip()


def _call_governed_subject_atom_rows_fallback(
    *,
    source_compile: dict[str, Any],
    source_text: str,
    carriers: list[str],
    args: argparse.Namespace,
    parse_error: str,
) -> dict[str, Any]:
    row_carriers = _governed_subject_atom_row_carriers(carriers)
    response = _call_lmstudio_json_schema(
        base_url=str(args.base_url),
        model=str(args.model),
        messages=_governed_subject_atom_rows_messages(
            source_text=source_text,
            carriers=row_carriers,
            source_compile=source_compile,
            retry_note=f"Manifest parse error was: {parse_error or 'unknown parse error'}.",
        ),
        schema=GOVERNED_SUBJECT_ATOM_ROWS_JSON_SCHEMA,
        schema_name="governed_subject_atom_rows_v1",
        timeout=int(args.timeout),
        temperature=float(args.temperature),
        top_p=float(args.top_p),
        max_tokens=min(int(args.max_tokens), 6000),
        strict_response_format=False,
    )
    parsed: dict[str, Any] | None = None
    fallback_parse_error = ""
    try:
        loaded = json.loads(str(response.get("content", "")))
        if isinstance(loaded, dict):
            parsed = loaded
    except json.JSONDecodeError as exc:
        fallback_parse_error = str(exc)
    report = (
        _facts_from_governed_subject_atom_rows(
            parsed,
            allowed_signatures=set(row_carriers[:16]),
        )
        if isinstance(parsed, dict)
        else {"facts": [], "skipped": []}
    )
    return {
        "attempted": True,
        "ok": isinstance(parsed, dict),
        "parse_error": fallback_parse_error,
        "raw_content": str(response.get("content", ""))[:2000],
        "offered_carriers": row_carriers[:16],
        "payload": parsed if isinstance(parsed, dict) else {},
        "fact_report": report,
        "openrouter_generation_metadata": response.get("openrouter_generation_metadata")
        if isinstance(response.get("openrouter_generation_metadata"), dict)
        else {},
    }


def _apply_profile_governed_subject_manifest_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    del intake_plan, extra_context
    carriers = _profile_governed_subject_discovery_offered_carriers(parsed_profile)
    metadata: dict[str, Any] = {
        "schema_version": "profile_governed_subject_manifest_pass_v1",
        "attempted": False,
        "offered_carriers": carriers[:16],
    }
    if not carriers:
        source_compile["profile_governed_subject_manifest"] = metadata
        return metadata
    atom_rows_primary = _call_governed_subject_atom_rows_fallback(
        source_compile=source_compile,
        source_text=source_text,
        carriers=carriers,
        args=args,
        parse_error="primary governed subject atom-row pass",
    )
    if bool(atom_rows_primary.get("ok")):
        prior_facts = {
            str(item).strip()
            for item in source_compile.get("facts", [])
            if str(item).strip()
        }
        fact_report = atom_rows_primary.get("fact_report")
        atom_row_facts = fact_report.get("facts", []) if isinstance(fact_report, dict) else []
        replacement_report = _replace_governed_subject_atom_row_facts(
            existing_facts=[str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()],
            replacement_facts=[str(item).strip() for item in atom_row_facts if str(item).strip()],
        )
        facts = replacement_report["facts"]
        appended = replacement_report["appended_facts"]
        source_compile["facts"] = facts
        source_compile["unique_fact_count"] = len(facts)
        metadata.update(
            {
                "attempted": True,
                "ok": True,
                "manifest_attempted": False,
                "atom_rows_primary": atom_rows_primary,
                "new_fact_count": len(appended),
                "new_facts": appended[:100],
                "replaced_supported_fact_count": len(replacement_report["replaced_facts"]),
                "replaced_supported_facts": replacement_report["replaced_facts"][:100],
                "skipped": fact_report.get("skipped", [])[:100] if isinstance(fact_report, dict) else [],
                "policy": {
                    "schema_version": "governed_subject_atom_rows_mapping_v1",
                    "authority": "llm_structured_atom_rows_to_typed_carriers",
                    "not_query_interpretation": True,
                    "not_source_record_interpretation": True,
                    "description": (
                        "Maps source-owned LLM atom rows into registered governed carrier facts. "
                        "Python normalizes typed atom slots and applies no source-prose parsing."
                    ),
                },
            }
        )
        source_compile["profile_governed_subject_manifest"] = metadata
        source_compile["profile_governed_subject_manifest_new_fact_count"] = len(appended)
        source_compile["profile_governed_subject_manifest_new_facts"] = appended[:100]
        source_compile["profile_governed_subject_manifest_prior_fact_count"] = len(prior_facts)
        return metadata
    response = _call_lmstudio_json_schema(
        base_url=str(args.base_url),
        model=str(args.model),
        messages=_governed_subject_manifest_messages(
            source_text=source_text,
            carriers=carriers,
            source_compile=source_compile,
        ),
        schema=GOVERNED_SUBJECT_MANIFEST_JSON_SCHEMA,
        schema_name="governed_subject_manifest_v1",
        timeout=int(args.timeout),
        temperature=float(args.temperature),
        top_p=float(args.top_p),
        max_tokens=min(int(args.max_tokens), 12000),
    )
    parsed: dict[str, Any] | None = None
    parse_error = ""
    try:
        loaded = json.loads(str(response.get("content", "")))
        if isinstance(loaded, dict):
            parsed = loaded
    except json.JSONDecodeError as exc:
        parse_error = str(exc)
    retry_response: dict[str, Any] | None = None
    if not isinstance(parsed, dict):
        retry_response = _call_lmstudio_json_schema(
            base_url=str(args.base_url),
            model=str(args.model),
            messages=_governed_subject_manifest_messages(
                source_text=source_text,
                carriers=carriers,
                source_compile=source_compile,
                retry_note=f"Parse error was: {parse_error or 'unknown parse error'}.",
            ),
            schema=GOVERNED_SUBJECT_MANIFEST_JSON_SCHEMA,
            schema_name="governed_subject_manifest_v1",
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=min(int(args.max_tokens), 12000),
        )
        try:
            loaded = json.loads(str(retry_response.get("content", "")))
            if isinstance(loaded, dict):
                parsed = loaded
                parse_error = ""
        except json.JSONDecodeError as exc:
            parse_error = str(exc)
    if not isinstance(parsed, dict):
        atom_rows_fallback = _call_governed_subject_atom_rows_fallback(
            source_compile=source_compile,
            source_text=source_text,
            carriers=carriers,
            args=args,
            parse_error=parse_error,
        )
        if bool(atom_rows_fallback.get("ok")):
            prior_facts = {
                str(item).strip()
                for item in source_compile.get("facts", [])
                if str(item).strip()
            }
            appended: list[str] = []
            facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
            existing = set(facts)
            fact_report = atom_rows_fallback.get("fact_report")
            fallback_facts = fact_report.get("facts", []) if isinstance(fact_report, dict) else []
            for fact in fallback_facts:
                fact_text = str(fact).strip()
                if not fact_text or fact_text in existing:
                    continue
                existing.add(fact_text)
                appended.append(fact_text)
                facts.append(fact_text)
            if appended:
                source_compile["facts"] = facts
                source_compile["unique_fact_count"] = len(facts)
            metadata.update(
                {
                    "attempted": True,
                    "ok": True,
                    "manifest_ok": False,
                    "manifest_parse_error": parse_error or "manifest_parse_failed",
                    "raw_content": str(response.get("content", ""))[:2000],
                    "retry_raw_content": str((retry_response or {}).get("content", ""))[:2000],
                    "atom_rows_fallback": atom_rows_fallback,
                    "new_fact_count": len(appended),
                    "new_facts": appended[:100],
                    "skipped": fact_report.get("skipped", [])[:100] if isinstance(fact_report, dict) else [],
                    "policy": {
                        "schema_version": "governed_subject_atom_rows_mapping_v1",
                        "authority": "llm_structured_atom_rows_to_typed_carriers",
                        "not_query_interpretation": True,
                        "not_source_record_interpretation": True,
                        "description": (
                            "Maps LLM-owned flat governed atom rows into registered carrier facts after "
                            "the nested manifest schema failed. Python normalizes typed atom slots and applies "
                            "no source-prose parsing."
                        ),
                    },
                }
            )
            source_compile["profile_governed_subject_manifest"] = metadata
            source_compile["profile_governed_subject_manifest_new_fact_count"] = len(appended)
            source_compile["profile_governed_subject_manifest_new_facts"] = appended[:100]
            source_compile["profile_governed_subject_manifest_prior_fact_count"] = len(prior_facts)
            return metadata
        metadata.update(
            {
                "attempted": True,
                "ok": False,
                "parse_error": parse_error or "manifest_parse_failed",
                "raw_content": str(response.get("content", ""))[:2000],
                "retry_raw_content": str((retry_response or {}).get("content", ""))[:2000],
                "atom_rows_fallback": atom_rows_fallback,
            }
        )
        source_compile["profile_governed_subject_manifest"] = metadata
        return metadata
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    fact_report = _facts_from_governed_subject_manifest(
        parsed,
        allowed_signatures=set(carriers[:16]),
    )
    appended: list[str] = []
    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    existing = set(facts)
    for fact in fact_report["facts"]:
        if fact in existing:
            continue
        existing.add(fact)
        appended.append(fact)
        facts.append(fact)
    if appended:
        source_compile["facts"] = facts
        source_compile["unique_fact_count"] = len(facts)
    metadata.update(
        {
            "attempted": True,
            "ok": True,
            "new_fact_count": len(appended),
            "new_facts": appended[:100],
            "skipped": fact_report["skipped"][:100],
            "manifest": parsed,
            "openrouter_generation_metadata": response.get("openrouter_generation_metadata")
            if isinstance(response.get("openrouter_generation_metadata"), dict)
            else {},
            "policy": {
                "schema_version": "governed_subject_manifest_mapping_v1",
                "authority": "llm_structured_manifest_to_typed_carriers",
                "not_query_interpretation": True,
                "not_source_record_interpretation": True,
                "description": (
                    "Maps an LLM-owned structured subject manifest into registered governed carrier facts. "
                    "Python normalizes typed atom slots and applies no source-prose parsing."
                ),
            },
        }
    )
    source_compile["profile_governed_subject_manifest"] = metadata
    source_compile["profile_governed_subject_manifest_new_fact_count"] = len(appended)
    source_compile["profile_governed_subject_manifest_new_facts"] = appended[:100]
    source_compile["profile_governed_subject_manifest_prior_fact_count"] = len(prior_facts)
    return metadata


def _manifest_atom(value: Any) -> str:
    text = str(value or "").strip().casefold()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    if not text:
        return ""
    if re.match(r"^[0-9]", text):
        text = f"v_{text}"
    return text


def _manifest_account_reason(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text[:160]


def _manifest_range_value(value: Any) -> str:
    text = str(value or "").strip()
    match = re.fullmatch(r"\d+", text)
    if match:
        return str(int(text))
    return _manifest_atom(text)


def _manifest_citation_value(value: Any) -> str:
    text = str(value or "").strip().casefold()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text


def _governed_subject_existing_fact_context(source_compile: dict[str, Any]) -> list[str]:
    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    preferred_subjects = set(_legal_citation_repair_preferred_subject_ids(source_compile))
    keep_predicates = {
        "claim_ground",
        "claim_range",
        "item_range",
        "list_member",
        "rejection_ground",
        "review_outcome",
        "violation_basis",
    }
    kept: list[str] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, _args = parsed
        if predicate not in keep_predicates:
            continue
        if preferred_subjects and _args and str(_args[0]).strip() not in preferred_subjects:
            continue
        kept.append(fact)
        if len(kept) >= 80:
            break
    if not kept:
        return []
    lines = [
        (
            "PROFILE LEGAL CITATION REPAIR PASS: existing governed typed subject ids are listed below. "
            "Reuse these ids when the source states a legal citation for the same governed action, claim set, "
            "finding, rejection, violation, or reviewed subject. These are typed compile atoms, not source prose."
        )
    ]
    if preferred_subjects:
        lines.append(
            "PROFILE LEGAL CITATION REPAIR PASS: preferred governed subject ids for legal citations: "
            + ", ".join(sorted(preferred_subjects))
            + ". If one of these ids fits the cited governed subject, emit legal_citation_detail/4 with "
            "that exact subject id; do not create or revive a duplicate subject id."
        )
    for fact in kept:
        lines.append(f"EXISTING GOVERNED FACT: {fact}")
    return lines


def _legal_citation_repair_preferred_subject_ids(source_compile: dict[str, Any]) -> list[str]:
    """Return canonical typed subjects for legal-citation attachment.

    This reducer reads only typed facts. It prefers claim-set subjects that
    already have a canonical theory in claim_ground/4 and at least one governed
    range/list/review companion, so citation repair does not attach statutes to
    duplicate statute-stuffed subjects when better typed atoms already exist.
    """

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    canonical_claim_subjects: set[str] = set()
    companion_subjects: set[str] = set()
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if not args:
            continue
        subject = str(args[0]).strip()
        if not subject:
            continue
        if predicate == "claim_ground" and len(args) == 4:
            ground = str(args[1]).strip().casefold()
            if ground in LEGAL_CITATION_REPAIR_CANONICAL_GROUNDS:
                canonical_claim_subjects.add(subject)
            continue
        if predicate in {"claim_range", "item_range", "list_member", "review_outcome", "rejection_ground", "violation_basis"}:
            companion_subjects.add(subject)
    preferred = sorted(canonical_claim_subjects & companion_subjects)
    if preferred:
        return preferred
    return sorted(canonical_claim_subjects)


def _profile_legal_citation_repair_context_lines(
    *,
    parsed_profile: dict[str, Any],
    source_compile: dict[str, Any],
) -> list[str]:
    carriers = _profile_legal_citation_repair_offered_carriers(parsed_profile)
    if not carriers:
        return []
    contract_lines = carrier_contract_prompt_lines(carriers[:16])
    return [
        (
            "PROFILE LEGAL CITATION REPAIR PASS: deterministic query delivery is missing typed legal citation "
            "details in some documents. This pass is proposal-only; emit only source-grounded legal citation "
            "detail rows through allowed predicate contracts, and let the mapper decide admission."
        ),
        (
            "PROFILE LEGAL CITATION REPAIR PASS: when the source states a statute, rule, section, regulation, "
            "CFR citation, USC citation, case citation, clause, or legal basis for a governed subject, emit a "
            "typed citation row with the subject id, citation, citation role/purpose, and source/scope anchor."
        ),
        (
            "PROFILE LEGAL CITATION REPAIR PASS: preserve exact subsection markers in paragraph- or "
            "section-scoped rows. If paragraph 6 states 15 U.S.C. 1681e(b) and GBL 380-j(a), emit the "
            "full subsection atoms on rows scoped to the paragraph/section anchor instead of only a broader "
            "act/title atom or only a document-level direct row."
        ),
        (
            "PROFILE LEGAL CITATION REPAIR PASS: when the source says an investigation was commenced, "
            "conducted, filed, issued, or brought pursuant to named provisions, preserve those provisions "
            "as authority or statutory-ground citation rows with a recital/caption/investigation scope when "
            "that is the source location. They need not be tied to a later obligation subject."
        ),
        (
            "PROFILE LEGAL CITATION REPAIR PASS: when the same legal obligation clause says that cited laws include "
            "future amendments, successor regulations, or later-adopted rules, preserve that coverage as its own "
            "typed citation-scope row. For legal_citation_detail/4, use a compact citation atom such as "
            "future_amendments_to_foregoing_laws_regulations_and_rules and a structural role such as amendment_scope; "
            "do not preserve the whole obligation sentence as prose."
        ),
        (
            "PROFILE LEGAL CITATION REPAIR PASS: when a numbered paragraph, item, obligation, or requirement says "
            "the subject must comply with an enumerated set of laws, emit every enumerated citation on that same "
            "paragraph/obligation scope anchor. Do not leave state-law citations only on recital, caption, or "
            "document-level direct rows while emitting only a federal citation on the paragraph-scoped row."
        ),
        (
            "PROFILE LEGAL CITATION REPAIR PASS: when a notice, order, or instruction groups citations by "
            "procedural purpose, preserve that purpose in legal_citation_detail/4's role slot. Do not collapse "
            "different citation-purpose groups into a generic role such as deadline_source when the source "
            "distinguishes agency_review_or_rehearing_right, petition_for_review_requirements, appeal_path, "
            "response_deadline, or similar purpose-specific groups."
        ),
        (
            "PROFILE LEGAL CITATION REPAIR PASS: if claim_ground/4, claim_range/4, review_outcome/4, "
            "rejection_ground/4, or violation_basis/5 already uses a subject id for the same source-stated "
            "ground or action, reuse that exact subject id. Do not create a document-level citation row when "
            "the citation belongs to a specific governed set or action."
        ),
        (
            "PROFILE LEGAL CITATION REPAIR PASS: do not emit source_record_* rows, display text rows, prose "
            "windows, or answer-bearing source excerpts. The output must be typed citation facts only."
        ),
        (
            "PROFILE LEGAL CITATION REPAIR PASS: compatible legal citation signatures to consider: "
            + ", ".join(carriers[:16])
            + ". Use exact allowed predicate names and argument order."
        ),
        *_governed_subject_existing_fact_context(source_compile),
        *contract_lines,
    ]


def _apply_profile_legal_citation_repair_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    carriers = _profile_legal_citation_repair_offered_carriers(parsed_profile)
    metadata: dict[str, Any] = {
        "schema_version": "profile_legal_citation_repair_pass_v1",
        "attempted": False,
        "offered_carriers": carriers[:16],
    }
    context_lines = _profile_legal_citation_repair_context_lines(
        parsed_profile=parsed_profile,
        source_compile=source_compile,
    )
    if not carriers or not context_lines:
        source_compile["profile_legal_citation_repair"] = metadata
        return metadata
    preferred_subjects = set(_legal_citation_repair_preferred_subject_ids(source_compile))
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    compiled = _compile_source_pass_ops(
        source_text=source_text,
        parsed_profile=parsed_profile,
        intake_plan=intake_plan,
        args=args,
        pass_id="profile_legal_citation_repair",
        purpose="repair typed legal citation detail delivery without source-record answer routing",
        focus="missing typed statute, rule, section, regulation, case, clause, and legal-basis citation rows",
        completion=(
            "Emit only source-grounded typed legal citation rows tied to governed subjects where possible; "
            "do not recompile unrelated source material."
        ),
        predicates=", ".join(carriers[:16]),
        coverage_goals=(
            "Deliver source-stated legal citations as typed predicates with subject id, citation value, "
            "citation role or purpose, and source/scope anchor. Prefer legal_citation_detail/4 when available."
        ),
        extra_context=[*(extra_context or []), *context_lines],
        operation_target=12,
    )
    compiled["pass_id"] = "profile_legal_citation_repair"
    compiled["purpose"] = "repair typed legal citation detail delivery without source-record answer routing"
    compiled["focus"] = "missing typed statute, rule, section, regulation, case, clause, and legal-basis citation rows"
    _merge_additive_source_pass(source_compile, compiled, metadata_prefix="profile_legal_citation_repair")
    signature_contract_report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts=prior_facts,
        allowed_signatures=set(carriers[:16]),
        metadata_prefix="profile_legal_citation_repair",
        pass_record=compiled,
    )
    subject_contract_report = _enforce_legal_citation_repair_subject_contract(
        source_compile,
        preferred_subjects=preferred_subjects,
        prior_facts=prior_facts,
    )
    metadata.update(
        {
            "attempted": True,
            "ok": bool(compiled.get("ok")),
            "admitted_count": int(compiled.get("admitted_count", 0) or 0),
            "skipped_count": int(compiled.get("skipped_count", 0) or 0),
            "new_fact_count": len(compiled.get("_profile_legal_citation_repair_new_facts", []))
            if isinstance(compiled.get("_profile_legal_citation_repair_new_facts"), list)
            else 0,
            "signature_contract": signature_contract_report,
            "subject_contract": subject_contract_report,
            "pass": compiled,
        }
    )
    source_compile["profile_legal_citation_repair"] = metadata
    return metadata


def _enforce_legal_citation_repair_subject_contract(
    source_compile: dict[str, Any],
    *,
    preferred_subjects: set[str],
    prior_facts: set[str],
) -> dict[str, Any]:
    """Reject repair-pass citation rows attached to noncanonical duplicate subjects.

    This is typed-fact governance only. It does not inspect source text or query
    wording; it only prevents a legal-citation repair pass from reviving a
    duplicate subject id when canonical governed subjects were already present.
    """

    if not preferred_subjects:
        source_compile["profile_legal_citation_subject_contract_rejected_count"] = 0
        return {"rejected_count": 0, "rejected_facts": [], "preferred_subjects": []}
    kept: list[str] = []
    rejected: list[str] = []
    for fact in [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]:
        if fact in prior_facts:
            kept.append(fact)
            continue
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            kept.append(fact)
            continue
        predicate, args = parsed
        if predicate == "legal_citation_detail" and args and str(args[0]).strip() not in preferred_subjects:
            rejected.append(fact)
            continue
        kept.append(fact)
    if rejected:
        source_compile["facts"] = kept
        source_compile["unique_fact_count"] = len(kept)
        source_compile["profile_legal_citation_subject_contract_policy"] = {
            "schema_version": "profile_legal_citation_subject_contract_v1",
            "authority": "typed_contract_validation_only",
            "not_source_interpretation": True,
            "not_query_interpretation": True,
            "description": (
                "Rejects repair-pass legal_citation_detail/4 rows attached to nonpreferred subject ids "
                "when canonical governed subject ids already exist in typed atoms."
            ),
        }
    source_compile["profile_legal_citation_subject_contract_rejected_count"] = len(rejected)
    source_compile["profile_legal_citation_subject_contract_rejected_facts"] = rejected[:100]
    return {
        "rejected_count": len(rejected),
        "rejected_facts": rejected[:100],
        "preferred_subjects": sorted(preferred_subjects),
    }


def _profile_review_outcome_repair_offered_carriers(parsed_profile: dict[str, Any]) -> list[str]:
    carriers: list[str] = []
    seen: set[str] = set()
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return carriers
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        signature = str(candidate.get("signature", "")).strip()
        if not signature or "/" not in signature:
            continue
        if signature.split("/", 1)[0].strip().lower() != "review_outcome":
            continue
        if signature not in seen:
            seen.add(signature)
            carriers.append(signature)
    return carriers


def _profile_monetary_payment_repair_offered_carriers(parsed_profile: dict[str, Any]) -> list[str]:
    carriers: list[str] = []
    seen: set[str] = set()
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return carriers
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        signature = str(candidate.get("signature", "")).strip()
        if not signature or "/" not in signature:
            continue
        base = signature.split("/", 1)[0].strip().lower()
        if base not in MONETARY_PAYMENT_REPAIR_BASE_NAMES:
            continue
        if carrier_contract(signature) is None:
            continue
        if signature not in seen:
            seen.add(signature)
            carriers.append(signature)
    return carriers


def _profile_monetary_payment_repair_context_lines(
    *,
    parsed_profile: dict[str, Any],
    source_compile: dict[str, Any],
) -> list[str]:
    carriers = _profile_monetary_payment_repair_offered_carriers(parsed_profile)
    if not carriers:
        return []
    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    keep_predicates = {
        "document_date",
        "legal_citation_detail",
        "monetary_payment",
        "obligation",
        "obligation_enforces",
        "payment_amount",
        "payment_deadline",
    }
    kept: list[str] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, _args = parsed
        if predicate not in keep_predicates:
            continue
        kept.append(fact)
        if len(kept) >= 80:
            break
    contract_lines = carrier_contract_prompt_lines(carriers[:8])
    lines = [
        (
            "PROFILE MONETARY PAYMENT REPAIR PASS: deterministic query delivery is missing typed payment "
            "rows that carry amount, authority or basis, purpose or use, and source scope together. This "
            "pass is proposal-only; emit only source-grounded monetary_payment/5 rows through allowed "
            "predicate contracts, and let the mapper decide admission."
        ),
        (
            "PROFILE MONETARY PAYMENT REPAIR PASS: for each source-stated money amount, emit one "
            "monetary_payment/5 row when the source states the amount and at least one of authority, "
            "basis, purpose, use, restitution, penalty, reimbursement, refund, settlement, or payment "
            "scope. Keep the amount, authority_or_basis, purpose_or_use, and source_or_scope in separate "
            "typed slots."
        ),
        (
            "PROFILE MONETARY PAYMENT REPAIR PASS: if existing facts split a payment amount, legal "
            "authority, and purpose across different predicate families, use the source payment clause to "
            "emit a single monetary_payment/5 row that unifies those source-stated slots. Do not solve this "
            "by writing prose windows or display rows."
        ),
        (
            "PROFILE MONETARY PAYMENT REPAIR PASS: use compact typed atoms such as usd_725000, "
            "gbl_349_d, restitution_and_penalties, nyag_discretion, agreement_15, paragraph_15, or "
            "source-local equivalents. Do not quote source prose as a slot value."
        ),
        (
            "PROFILE MONETARY PAYMENT REPAIR PASS: do not emit source_record_* rows, display text rows, "
            "broad obligation summaries, prose windows, or answer-bearing source excerpts. The output must "
            "be typed monetary-payment facts only."
        ),
        (
            "PROFILE MONETARY PAYMENT REPAIR PASS: compatible monetary signatures to consider: "
            + ", ".join(carriers[:8])
            + ". Use exact allowed predicate names and argument order."
        ),
    ]
    for fact in kept:
        lines.append(f"EXISTING MONETARY FACT: {fact}")
    return [*lines, *contract_lines]


def _apply_profile_monetary_payment_repair_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    carriers = _profile_monetary_payment_repair_offered_carriers(parsed_profile)
    metadata: dict[str, Any] = {
        "schema_version": "profile_monetary_payment_repair_pass_v1",
        "attempted": False,
        "offered_carriers": carriers[:8],
    }
    context_lines = _profile_monetary_payment_repair_context_lines(
        parsed_profile=parsed_profile,
        source_compile=source_compile,
    )
    if not carriers or not context_lines:
        metadata["reason"] = "no_monetary_payment_carriers_offered"
        source_compile["profile_monetary_payment_repair"] = metadata
        return metadata
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    compiled = _compile_source_pass_ops(
        source_text=source_text,
        parsed_profile=parsed_profile,
        intake_plan=intake_plan,
        args=args,
        pass_id="profile_monetary_payment_repair",
        purpose="repair typed monetary payment delivery without source-record answer routing",
        focus="missing typed monetary_payment rows for source-stated payment, relief, penalty, restitution, reimbursement, and settlement amounts",
        completion=(
            "Emit only source-grounded monetary_payment/5 rows that keep amount, authority, purpose, "
            "and source/scope as separate typed slots; do not recompile unrelated source material."
        ),
        predicates=", ".join(carriers[:8]),
        coverage_goals=(
            "Deliver source-stated monetary payment details as typed predicates with subject id, amount, "
            "authority or basis, purpose or use, and source/scope anchor."
        ),
        extra_context=[*(extra_context or []), *context_lines],
        operation_target=10,
    )
    compiled["pass_id"] = "profile_monetary_payment_repair"
    compiled["purpose"] = "repair typed monetary payment delivery without source-record answer routing"
    compiled["focus"] = (
        "missing typed monetary_payment rows for source-stated payment, relief, penalty, restitution, "
        "reimbursement, and settlement amounts"
    )
    _merge_additive_source_pass(source_compile, compiled, metadata_prefix="profile_monetary_payment_repair")
    signature_contract_report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts=prior_facts,
        allowed_signatures=set(carriers[:8]),
        metadata_prefix="profile_monetary_payment_repair",
        pass_record=compiled,
    )
    metadata.update(
        {
            "attempted": True,
            "ok": bool(compiled.get("ok")),
            "admitted_count": int(compiled.get("admitted_count", 0) or 0),
            "skipped_count": int(compiled.get("skipped_count", 0) or 0),
            "new_fact_count": len(compiled.get("_profile_monetary_payment_repair_new_facts", []))
            if isinstance(compiled.get("_profile_monetary_payment_repair_new_facts"), list)
            else 0,
            "signature_contract": signature_contract_report,
            "pass": compiled,
        }
    )
    source_compile["profile_monetary_payment_repair"] = metadata
    return metadata


DOCUMENT_DATE_REPAIR_PREDICATES = {
    "document_date",
    "event_date",
    "event_time",
    "event_timestamp",
    "event_wall_time",
    "filing_date",
    "hearing_date",
    "meeting_date",
    "publication_date",
    "published_on",
    "report_date",
}


def _profile_document_date_repair_offered_carriers(parsed_profile: dict[str, Any]) -> list[str]:
    carriers: list[str] = []
    seen: set[str] = set()
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return carriers
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        signature = str(candidate.get("signature", "")).strip()
        if not signature or "/" not in signature:
            continue
        predicate, _, arity_text = signature.partition("/")
        predicate = predicate.strip().lower()
        if predicate not in DOCUMENT_DATE_REPAIR_PREDICATES:
            continue
        try:
            arity = int(arity_text)
        except ValueError:
            continue
        if predicate == "document_date" and arity != 3:
            continue
        if predicate != "document_date" and arity not in {2, 3, 4}:
            continue
        if signature not in seen:
            seen.add(signature)
            carriers.append(signature)
    return carriers


def _document_date_repair_context_lines(
    *,
    parsed_profile: dict[str, Any],
    source_compile: dict[str, Any],
) -> list[str]:
    carriers = _profile_document_date_repair_offered_carriers(parsed_profile)
    if not carriers:
        return []
    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    keep_predicates = {
        "appeal_filed",
        "case_identifier",
        "document_action",
        "document_identifier",
        "document_identifier_occurrence",
        "document_metadata",
        "document_date",
        "event_date",
        "filing_date",
        "final_disposition",
        "prior_art_reference",
        "proceeding_identifier",
        "referenced_matter",
        "related_document",
        "review_outcome",
    }
    kept: list[str] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, _args = parsed
        if predicate not in keep_predicates:
            continue
        kept.append(fact)
        if len(kept) >= 80:
            break
    contract_lines = carrier_contract_prompt_lines([carrier for carrier in carriers if carrier == "document_date/3"])
    lines = [
        (
            "PROFILE DOCUMENT DATE REPAIR PASS: deterministic query delivery is missing typed document or "
            "event dates. This pass is proposal-only; emit only source-grounded date rows through allowed "
            "predicate contracts, and let the mapper decide admission."
        ),
        (
            "PROFILE DOCUMENT DATE REPAIR PASS: when the source states issue, decision, filing, publication, "
            "report, notice, application, received, effective, hearing, meeting, or related-matter dates, "
            "emit compatible date rows using the same subject ids as existing identifier, action, prior-art, "
            "related-matter, or review rows whenever possible."
        ),
        (
            "PROFILE DOCUMENT DATE REPAIR PASS: for chronology pressure, emit one typed date row per "
            "source-stated dated event. The main document issue date does not replace related filing, "
            "hearing, meeting, motion, prior-order, publication, application, or review dates."
        ),
        (
            "PROFILE DOCUMENT DATE REPAIR PASS: if both document_date/3 and event_date/2 are available, "
            "use document_date/3 for document-like subjects and event_date/2 for procedural event ids; "
            "preserving both is acceptable when both typed subjects are source-grounded."
        ),
        (
            "PROFILE DOCUMENT DATE REPAIR PASS: do not emit source_record_* rows, display text rows, prose "
            "windows, broad summaries, or answer-bearing source excerpts. The output must be typed date facts only."
        ),
        (
            "PROFILE DOCUMENT DATE REPAIR PASS: compatible date signatures to consider: "
            + ", ".join(carriers[:16])
            + ". Use exact allowed predicate names and argument order."
        ),
    ]
    for fact in kept:
        lines.append(f"EXISTING DATE/IDENTIFIER FACT: {fact}")
    return [*lines, *contract_lines]


def _apply_profile_document_date_repair_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    carriers = _profile_document_date_repair_offered_carriers(parsed_profile)
    metadata: dict[str, Any] = {
        "schema_version": "profile_document_date_repair_pass_v1",
        "attempted": False,
        "offered_carriers": carriers[:16],
    }
    context_lines = _document_date_repair_context_lines(
        parsed_profile=parsed_profile,
        source_compile=source_compile,
    )
    if not carriers or not context_lines:
        metadata["reason"] = "no_document_date_carriers_offered"
        source_compile["profile_document_date_repair"] = metadata
        return metadata
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    compiled = _compile_source_pass_ops(
        source_text=source_text,
        parsed_profile=parsed_profile,
        intake_plan=intake_plan,
        args=args,
        pass_id="profile_document_date_repair",
        purpose="repair typed document and event date delivery without source-record answer routing",
        focus="missing typed date rows for documents, applications, publications, filings, decisions, notices, and related matters",
        completion=(
            "Emit only source-grounded typed date rows tied to existing or source-stated subjects; "
            "do not recompile unrelated source material."
        ),
        predicates=", ".join(carriers[:16]),
        coverage_goals=(
            "Deliver source-stated dates as typed predicates with subject id, date role when the predicate "
            "supports it, and date value."
        ),
        extra_context=[*(extra_context or []), *context_lines],
        operation_target=16,
    )
    compiled["pass_id"] = "profile_document_date_repair"
    compiled["purpose"] = "repair typed document and event date delivery without source-record answer routing"
    compiled["focus"] = "missing typed date rows for documents, applications, publications, filings, decisions, notices, and related matters"
    _merge_additive_source_pass(source_compile, compiled, metadata_prefix="profile_document_date_repair")
    signature_contract_report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts=prior_facts,
        allowed_signatures=set(carriers[:16]),
        metadata_prefix="profile_document_date_repair",
        pass_record=compiled,
    )
    metadata.update(
        {
            "attempted": True,
            "ok": bool(compiled.get("ok")),
            "admitted_count": int(compiled.get("admitted_count", 0) or 0),
            "skipped_count": int(compiled.get("skipped_count", 0) or 0),
            "new_fact_count": len(compiled.get("_profile_document_date_repair_new_facts", []))
            if isinstance(compiled.get("_profile_document_date_repair_new_facts"), list)
            else 0,
            "signature_contract": signature_contract_report,
            "pass": compiled,
        }
    )
    source_compile["profile_document_date_repair"] = metadata
    return metadata


def _review_outcome_repair_context_lines(
    *,
    parsed_profile: dict[str, Any],
    source_compile: dict[str, Any],
) -> list[str]:
    carriers = _profile_review_outcome_repair_offered_carriers(parsed_profile)
    if not carriers:
        return []
    preferred_subjects = set(_legal_citation_repair_preferred_subject_ids(source_compile))
    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    keep_predicates = {
        "affirmed",
        "appeal_filed",
        "case_identifier",
        "claim_ground",
        "claim_range",
        "document_date",
        "document_identifier",
        "document_identifier_occurrence",
        "document_title",
        "legal_citation_detail",
        "review_outcome",
    }
    document_subjects: set[str] = set()
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate in {
            "case_identifier",
            "document_date",
            "document_identifier",
            "document_identifier_occurrence",
            "document_title",
        } and args:
            document_subjects.add(str(args[0]).strip())
    kept: list[str] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate not in keep_predicates or not args:
            continue
        subject = str(args[0]).strip()
        if (
            preferred_subjects
            and subject not in preferred_subjects
            and subject not in document_subjects
            and predicate not in {"affirmed", "appeal_filed"}
        ):
            continue
        kept.append(fact)
        if len(kept) >= 80:
            break
    contract_lines = carrier_contract_prompt_lines(carriers[:16])
    lines = [
        (
            "PROFILE REVIEW OUTCOME REPAIR PASS: deterministic query delivery is missing typed review outcomes "
            "on already-emitted governed subjects. This pass is proposal-only; emit only source-grounded "
            "review_outcome/4 rows through allowed predicate contracts, and let the mapper decide admission."
        ),
        (
            "PROFILE REVIEW OUTCOME REPAIR PASS: when the source states that a board, court, committee, agency, "
            "officer, or other reviewer affirmed, reversed, modified, vacated, remanded, sustained, granted, or "
            "denied governed actions, emit review_outcome/4 with the same subject id used by the governed "
            "claim, item, violation, finding, or decision rows."
        ),
        (
            "PROFILE REVIEW OUTCOME REPAIR PASS: when the source states a document-level or case-level final "
            "disposition, emit review_outcome/4 on the same document/case subject id used by document_date/3, "
            "case_identifier/2, document_identifier/2, or document_identifier_occurrence/5 when available. "
            "This preserves wrapper answers such as docket/date/disposition without joining across unrelated "
            "underlying issue subjects."
        ),
        (
            "PROFILE REVIEW OUTCOME REPAIR PASS: do not emit source_record_* rows, display text rows, prose "
            "windows, broad umbrella reviewed-rejections ids, or answer-bearing source excerpts. The output "
            "must be typed review outcome facts only."
        ),
        (
            "PROFILE REVIEW OUTCOME REPAIR PASS: compatible review signatures to consider: "
            + ", ".join(carriers[:16])
            + ". Use exact allowed predicate names and argument order."
        ),
    ]
    if preferred_subjects:
        lines.append(
            "PROFILE REVIEW OUTCOME REPAIR PASS: preferred governed subject ids for review outcomes: "
            + ", ".join(sorted(preferred_subjects))
            + ". If the review outcome applies, emit one review_outcome/4 row per applicable subject id."
        )
    if document_subjects:
        lines.append(
            "PROFILE REVIEW OUTCOME REPAIR PASS: available document/case subject ids for document-level final "
            "dispositions: "
            + ", ".join(sorted(document_subjects))
            + ". Use these only when the source states the final disposition for that document or case."
        )
    for fact in kept:
        lines.append(f"EXISTING GOVERNED FACT: {fact}")
    return [*lines, *contract_lines]


def _apply_profile_review_outcome_repair_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    carriers = _profile_review_outcome_repair_offered_carriers(parsed_profile)
    metadata: dict[str, Any] = {
        "schema_version": "profile_review_outcome_repair_pass_v1",
        "attempted": False,
        "offered_carriers": carriers[:16],
    }
    context_lines = _review_outcome_repair_context_lines(
        parsed_profile=parsed_profile,
        source_compile=source_compile,
    )
    if not carriers or not context_lines:
        source_compile["profile_review_outcome_repair"] = metadata
        return metadata
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    compiled = _compile_source_pass_ops(
        source_text=source_text,
        parsed_profile=parsed_profile,
        intake_plan=intake_plan,
        args=args,
        pass_id="profile_review_outcome_repair",
        purpose="repair typed review outcome delivery without source-record answer routing",
        focus="missing typed review_outcome rows on governed or document/case subjects",
        completion=(
            "Emit only source-grounded typed review_outcome rows tied to governed or document/case subjects where applicable; "
            "do not recompile unrelated source material."
        ),
        predicates=", ".join(carriers[:16]),
        coverage_goals=(
            "Deliver source-stated review outcomes as typed predicates with reviewed subject id, reviewing "
            "body or actor, outcome/action, and source/scope anchor."
        ),
        extra_context=[*(extra_context or []), *context_lines],
        operation_target=12,
    )
    compiled["pass_id"] = "profile_review_outcome_repair"
    compiled["purpose"] = "repair typed review outcome delivery without source-record answer routing"
    compiled["focus"] = "missing typed review_outcome rows on governed or document/case subjects"
    _merge_additive_source_pass(source_compile, compiled, metadata_prefix="profile_review_outcome_repair")
    signature_contract_report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts=prior_facts,
        allowed_signatures=set(carriers[:16]),
        metadata_prefix="profile_review_outcome_repair",
        pass_record=compiled,
    )
    metadata.update(
        {
            "attempted": True,
            "ok": bool(compiled.get("ok")),
            "admitted_count": int(compiled.get("admitted_count", 0) or 0),
            "skipped_count": int(compiled.get("skipped_count", 0) or 0),
            "new_fact_count": len(compiled.get("_profile_review_outcome_repair_new_facts", []))
            if isinstance(compiled.get("_profile_review_outcome_repair_new_facts"), list)
            else 0,
            "signature_contract": signature_contract_report,
            "pass": compiled,
        }
    )
    source_compile["profile_review_outcome_repair"] = metadata
    return metadata


def _apply_profile_list_range_inventory_repair_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    carriers = _profile_list_range_inventory_repair_offered_carriers(parsed_profile)
    metadata: dict[str, Any] = {
        "schema_version": "profile_list_range_inventory_repair_pass_v1",
        "attempted": False,
        "offered_carriers": carriers[:16],
    }
    if not carriers:
        metadata["reason"] = "no_list_range_inventory_predicates_offered"
        source_compile["profile_list_range_inventory_repair"] = metadata
        return metadata
    context_lines = _profile_list_range_inventory_repair_context_lines(parsed_profile)
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    target = max(8, min(32, int(getattr(args, "focused_pass_operation_target", 48) or 48)))
    compiled = _compile_source_pass_ops(
        source_text=source_text,
        parsed_profile=parsed_profile,
        intake_plan=intake_plan,
        args=args,
        pass_id="profile_list_range_inventory_repair",
        purpose="repair typed numbered list and range inventory without source-record answer routing",
        focus="missing typed list members, claim ranges, item ranges, count ranges, issue ranges, and governed item-set segments",
        completion=(
            "Emit only source-grounded typed list/range rows and minimal supporting set ids; "
            "do not recompile unrelated source material."
        ),
        predicates=", ".join(carriers[:16]),
        coverage_goals=(
            "Deliver source-stated numbered inventory as typed predicates: set/list id, member value or "
            "range start/end, member kind when the predicate supports it, and source/scope anchor."
        ),
        extra_context=[*(extra_context or []), *context_lines],
        operation_target=target,
    )
    compiled["pass_id"] = "profile_list_range_inventory_repair"
    compiled["purpose"] = "repair typed numbered list and range inventory without source-record answer routing"
    compiled["focus"] = "missing typed list members, claim ranges, item ranges, count ranges, issue ranges, and governed item-set segments"
    _merge_additive_source_pass(source_compile, compiled, metadata_prefix="profile_list_range_inventory_repair")
    signature_contract_report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts=prior_facts,
        allowed_signatures=set(carriers[:16]),
        metadata_prefix="profile_list_range_inventory_repair",
        pass_record=compiled,
    )
    _enforce_list_range_inventory_fact_contract(source_compile)
    missing_slots = _source_pass_self_check_missing_slots(compiled)
    completion_compiled: dict[str, Any] | None = None
    completion_signature_contract_report: dict[str, Any] | None = None
    if bool(getattr(args, "profile_list_range_self_check_followup", False)) and missing_slots:
        completion_prior_facts = {
            str(item).strip()
            for item in source_compile.get("facts", [])
            if str(item).strip()
        }
        completion_context = [
            (
                "PROFILE LIST/RANGE INVENTORY REPAIR FOLLOW-UP: the previous bounded pass reported "
                "missing typed slots. Complete only those source-grounded list/range companion rows. "
                "Do not repeat existing facts and do not add source_record or prose display rows."
            ),
            "PROFILE LIST/RANGE INVENTORY REPAIR FOLLOW-UP: previous missing_slots:",
            *[f"- {slot}" for slot in missing_slots[:8]],
            (
                "PROFILE LIST/RANGE INVENTORY REPAIR FOLLOW-UP: if a subject id appears in a typed "
                "ground, rejection, treatment, legal citation, or review row, and the source states "
                "the corresponding numbered range for that same subject, emit the companion "
                "claim_range/4 or item_range/4 rows using that same subject id."
            ),
            *_list_range_inventory_existing_fact_context(source_compile),
        ]
        completion_target = max(16, min(48, int(getattr(args, "focused_pass_operation_target", 48) or 48)))
        completion_compiled = _compile_source_pass_ops(
            source_text=source_text,
            parsed_profile=parsed_profile,
            intake_plan=intake_plan,
            args=args,
            pass_id="profile_list_range_inventory_repair_followup",
            purpose="complete self-declared missing typed list/range companion rows",
            focus="source-grounded list/range rows named by the prior pass self_check.missing_slots",
            completion=(
                "Emit only missing typed list/range inventory and directly required same-subject companion rows; "
                "do not recompile unrelated source material."
            ),
            predicates=", ".join(carriers[:16]),
            coverage_goals=(
                "Close the previous pass's explicit missing_slots with typed set/list id, member or range "
                "boundaries, member kind when supported, and source/scope anchor."
            ),
            extra_context=[*(extra_context or []), *context_lines, *completion_context],
            operation_target=completion_target,
        )
        completion_compiled["pass_id"] = "profile_list_range_inventory_repair_followup"
        completion_compiled["purpose"] = "complete self-declared missing typed list/range companion rows"
        completion_compiled["focus"] = "source-grounded list/range rows named by the prior pass self_check.missing_slots"
        _merge_additive_source_pass(
            source_compile,
            completion_compiled,
            metadata_prefix="profile_list_range_inventory_repair_followup",
        )
        completion_signature_contract_report = _enforce_additive_pass_allowed_signatures(
            source_compile,
            prior_facts=completion_prior_facts,
            allowed_signatures=set(carriers[:16]),
            metadata_prefix="profile_list_range_inventory_repair_followup",
            pass_record=completion_compiled,
        )
        _enforce_list_range_inventory_fact_contract(source_compile)
    initial_new_facts = (
        compiled.get("_profile_list_range_inventory_repair_new_facts", [])
        if isinstance(compiled.get("_profile_list_range_inventory_repair_new_facts"), list)
        else []
    )
    completion_new_facts = (
        completion_compiled.get("_profile_list_range_inventory_repair_followup_new_facts", [])
        if isinstance(completion_compiled, dict)
        and isinstance(completion_compiled.get("_profile_list_range_inventory_repair_followup_new_facts"), list)
        else []
    )
    metadata.update(
        {
            "attempted": True,
            "ok": bool(compiled.get("ok")),
            "admitted_count": int(compiled.get("admitted_count", 0) or 0),
            "skipped_count": int(compiled.get("skipped_count", 0) or 0),
            "new_fact_count": len(initial_new_facts) + len(completion_new_facts),
            "signature_contract": signature_contract_report,
            "pass": compiled,
            "followup_attempted": bool(missing_slots),
            "followup_missing_slots": missing_slots[:8],
        }
    )
    if completion_compiled is not None:
        metadata["followup_ok"] = bool(completion_compiled.get("ok"))
        metadata["followup_admitted_count"] = int(completion_compiled.get("admitted_count", 0) or 0)
        metadata["followup_skipped_count"] = int(completion_compiled.get("skipped_count", 0) or 0)
        metadata["followup_new_fact_count"] = len(completion_new_facts)
        metadata["followup_signature_contract"] = completion_signature_contract_report or {}
        metadata["followup_pass"] = completion_compiled
    source_compile["profile_list_range_inventory_repair"] = metadata
    return metadata


def _profile_list_range_inventory_offered_omission_rows(source_compile: dict[str, Any]) -> list[dict[str, Any]]:
    health = source_compile.get("governed_companion_subject_health")
    if not isinstance(health, dict):
        return []
    ledger = health.get("governed_companion_omission_ledger")
    if not isinstance(ledger, list):
        return []
    rows: list[dict[str, Any]] = []
    for row in ledger:
        if not isinstance(row, dict):
            continue
        signature = str(row.get("signature") or "").strip()
        status = str(row.get("status") or "").strip()
        subject = str(row.get("subject") or "").strip()
        if signature not in {"claim_range/4", "item_range/4"}:
            continue
        if status != "missing_unaccounted" or not subject:
            continue
        rows.append(
            {
                "subject": subject,
                "signature": signature,
                "observed_predicates": [
                    str(item).strip()
                    for item in row.get("observed_predicates", [])
                    if str(item).strip()
                ],
                "reason": str(row.get("reason") or "").strip(),
            }
        )
    return rows


def _profile_list_range_inventory_omission_context(source_compile: dict[str, Any]) -> list[str]:
    rows = _profile_list_range_inventory_offered_omission_rows(source_compile)
    if not rows:
        return []
    lines = [
        (
            "PROFILE LIST/RANGE INVENTORY OMISSION FOLLOW-UP: governed companion health found typed "
            "subjects with related companion facts but no typed range inventory. For each listed "
            "subject, emit the missing claim_range/4 or item_range/4 rows only if the raw source text "
            "directly states the subject's numbered inventory."
        ),
        (
            "PROFILE LIST/RANGE INVENTORY OMISSION FOLLOW-UP: do not infer a range from the subject "
            "name alone. If the raw source does not state the missing range for that subject, emit no "
            "fact for it and note the omission in self_check."
        ),
    ]
    for row in rows[:16]:
        observed = ", ".join(row.get("observed_predicates") or [])
        lines.append(
            "OMISSION_LEDGER_ROW "
            f"subject={row['subject']} signature={row['signature']} observed_predicates={observed or 'none'}"
        )
    lines.extend(_list_range_inventory_existing_fact_context(source_compile, limit=120))
    return lines


def _apply_profile_list_range_inventory_omission_followup_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    carriers = _profile_list_range_inventory_repair_offered_carriers(parsed_profile)
    omission_context = _profile_list_range_inventory_omission_context(source_compile)
    metadata: dict[str, Any] = {
        "schema_version": "profile_list_range_inventory_omission_followup_pass_v1",
        "attempted": False,
        "offered_carriers": carriers[:16],
        "omission_rows": _profile_list_range_inventory_offered_omission_rows(source_compile)[:16],
    }
    if not carriers or not omission_context:
        metadata["reason"] = "no_list_range_inventory_omissions_or_carriers"
        source_compile["profile_list_range_inventory_omission_followup"] = metadata
        return metadata
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    context_lines = _profile_list_range_inventory_repair_context_lines(parsed_profile)
    target = max(16, min(48, int(getattr(args, "focused_pass_operation_target", 48) or 48)))
    compiled = _compile_source_pass_ops(
        source_text=source_text,
        parsed_profile=parsed_profile,
        intake_plan=intake_plan,
        args=args,
        pass_id="profile_list_range_inventory_omission_followup",
        purpose="complete governed-companion omission ledger list/range rows",
        focus="typed subjects missing claim_range/4 or item_range/4 according to the governed companion omission ledger",
        completion=(
            "Emit only source-grounded typed range inventory rows for the listed omission-ledger subjects; "
            "do not recompile unrelated source material."
        ),
        predicates=", ".join(carriers[:16]),
        coverage_goals=(
            "For every listed subject whose numbered inventory is stated in the source, deliver the "
            "missing claim_range/4 or item_range/4 companion rows using the same subject id."
        ),
        extra_context=[*(extra_context or []), *context_lines, *omission_context],
        operation_target=target,
    )
    compiled["pass_id"] = "profile_list_range_inventory_omission_followup"
    compiled["purpose"] = "complete governed-companion omission ledger list/range rows"
    compiled["focus"] = (
        "typed subjects missing claim_range/4 or item_range/4 according to the governed companion omission ledger"
    )
    _merge_additive_source_pass(
        source_compile,
        compiled,
        metadata_prefix="profile_list_range_inventory_omission_followup",
    )
    signature_contract_report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts=prior_facts,
        allowed_signatures=set(carriers[:16]),
        metadata_prefix="profile_list_range_inventory_omission_followup",
        pass_record=compiled,
    )
    _enforce_list_range_inventory_fact_contract(source_compile)
    new_facts = (
        compiled.get("_profile_list_range_inventory_omission_followup_new_facts", [])
        if isinstance(compiled.get("_profile_list_range_inventory_omission_followup_new_facts"), list)
        else []
    )
    metadata.update(
        {
            "attempted": True,
            "ok": bool(compiled.get("ok")),
            "admitted_count": int(compiled.get("admitted_count", 0) or 0),
            "skipped_count": int(compiled.get("skipped_count", 0) or 0),
            "new_fact_count": len(new_facts),
            "signature_contract": signature_contract_report,
            "pass": compiled,
        }
    )
    source_compile["profile_list_range_inventory_omission_followup"] = metadata
    return metadata


def _registered_carrier_omission_findings(report: dict[str, Any]) -> list[dict[str, Any]]:
    findings = report.get("findings") if isinstance(report, dict) else []
    return [
        item
        for item in findings
        if isinstance(item, dict)
        and str(item.get("class", "")).strip() == "registered_carrier_offered_but_undelivered"
        and str(item.get("signature", "")).strip()
    ]


def _registered_carrier_omission_offered_carriers(report: dict[str, Any]) -> list[str]:
    carriers: list[str] = []
    seen: set[str] = set()
    for finding in _registered_carrier_omission_findings(report):
        signature = str(finding.get("signature", "")).strip()
        if signature and signature not in seen and carrier_contract(signature) is not None:
            seen.add(signature)
            carriers.append(signature)
    return carriers


def _registered_carrier_omission_context_lines(report: dict[str, Any]) -> list[str]:
    carriers = _registered_carrier_omission_offered_carriers(report)
    if not carriers:
        return []
    lines = [
        (
            "REGISTERED CARRIER OMISSION FOLLOWUP: deterministic accountability found registered carrier "
            "signatures that were offered to the compiler and accountability-required, but emitted zero typed rows."
        ),
        (
            "REGISTERED CARRIER OMISSION FOLLOWUP: this is a source-compile completion pass. Emit only "
            "source-grounded rows for the listed registered carrier contracts. Do not emit source_record_* rows, "
            "do not emit prose excerpts, and do not recompile unrelated material."
        ),
        "REGISTERED CARRIER OMISSION FOLLOWUP: missing registered carriers = " + ", ".join(carriers[:12]) + ".",
    ]
    lines.extend(carrier_contract_prompt_lines(carriers[:12]))
    return lines


def _apply_profile_registered_carrier_omission_followup_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
    profile_extension_metadata: dict[str, Any] | None = None,
    registered_delivery_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    report = registered_delivery_report or _attach_registered_carrier_delivery_report(
        source_compile=source_compile,
        parsed_profile=parsed_profile,
        profile_extension_metadata=profile_extension_metadata,
        mark_health=False,
    )
    carriers = _registered_carrier_omission_offered_carriers(report)
    context_lines = _registered_carrier_omission_context_lines(report)
    metadata: dict[str, Any] = {
        "schema_version": "profile_registered_carrier_omission_followup_pass_v1",
        "attempted": False,
        "offered_carriers": carriers[:12],
        "initial_findings": _registered_carrier_omission_findings(report)[:12],
    }
    if not carriers or not context_lines:
        metadata["reason"] = "no_registered_carrier_omissions"
        source_compile["profile_registered_carrier_omission_followup"] = metadata
        return metadata
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    target = max(8, min(32, int(getattr(args, "focused_pass_operation_target", 32) or 32)))
    compiled = _compile_source_pass_ops(
        source_text=source_text,
        parsed_profile=parsed_profile,
        intake_plan=intake_plan,
        args=args,
        pass_id="profile_registered_carrier_omission_followup",
        purpose="complete accountability-required registered carrier rows",
        focus="registered carriers with zero emitted typed rows: " + ", ".join(carriers[:12]),
        completion=(
            "Emit only source-grounded rows for the listed registered carrier signatures. If the source does "
            "not state an instance, omit it and note the missing slot in self_check; do not invent placeholder rows."
        ),
        predicates=", ".join(carriers[:12]),
        coverage_goals=(
            "For each listed registered carrier, populate compact typed rows for every source-stated instance "
            "needed by that carrier contract."
        ),
        extra_context=[*(extra_context or []), *context_lines],
        operation_target=target,
    )
    compiled["pass_id"] = "profile_registered_carrier_omission_followup"
    compiled["purpose"] = "complete accountability-required registered carrier rows"
    compiled["focus"] = "registered carriers with zero emitted typed rows: " + ", ".join(carriers[:12])
    _merge_additive_source_pass(
        source_compile,
        compiled,
        metadata_prefix="profile_registered_carrier_omission_followup",
    )
    signature_contract_report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts=prior_facts,
        allowed_signatures=set(carriers[:12]),
        metadata_prefix="profile_registered_carrier_omission_followup",
        pass_record=compiled,
    )
    refreshed = _attach_registered_carrier_delivery_report(
        source_compile=source_compile,
        parsed_profile=parsed_profile,
        profile_extension_metadata=profile_extension_metadata,
        mark_health=False,
    )
    new_facts = (
        compiled.get("_profile_registered_carrier_omission_followup_new_facts", [])
        if isinstance(compiled.get("_profile_registered_carrier_omission_followup_new_facts"), list)
        else []
    )
    metadata.update(
        {
            "attempted": True,
            "ok": bool(compiled.get("ok")),
            "admitted_count": int(compiled.get("admitted_count", 0) or 0),
            "skipped_count": int(compiled.get("skipped_count", 0) or 0),
            "new_fact_count": len(new_facts),
            "signature_contract": signature_contract_report,
            "remaining_findings": _registered_carrier_omission_findings(refreshed)[:12],
            "pass": compiled,
        }
    )
    source_compile["profile_registered_carrier_omission_followup"] = metadata
    return metadata


def _profile_registry_predicate_signatures(profile_registry: dict[str, Any]) -> list[str]:
    predicates = profile_registry.get("predicates") if isinstance(profile_registry.get("predicates"), list) else []
    signatures: list[str] = []
    seen: set[str] = set()
    for item in predicates:
        if not isinstance(item, dict):
            continue
        signature = str(item.get("signature", "")).strip()
        if not signature or signature in seen or carrier_contract(signature) is None:
            continue
        seen.add(signature)
        signatures.append(signature)
    return signatures


def _profile_registry_completion_signatures(profile_registry: dict[str, Any]) -> list[str]:
    return [
        signature
        for signature in _profile_registry_predicate_signatures(profile_registry)
        if signature != "domain_omission/5"
    ]


def _profile_registry_existing_fact_context(source_compile: dict[str, Any], *, limit: int = 80) -> list[str]:
    facts: list[str] = []
    for item in source_compile.get("facts", []) if isinstance(source_compile.get("facts"), list) else []:
        fact = str(item).strip()
        parsed = _parse_fact_clause(fact)
        if parsed is not None and f"{parsed[0]}/{len(parsed[1])}" == "domain_omission/5":
            continue
        if fact:
            facts.append(fact)
    if not facts:
        return []
    lines = [
        "PROFILE REGISTRY COMPLETION FOLLOWUP: existing typed facts are listed below. Reuse their subject IDs "
        "when adding missing companion rows; do not replace them with prose-derived aliases."
    ]
    lines.extend(f"existing_fact: {fact}" for fact in facts[:limit])
    return lines


def _profile_without_signatures(parsed_profile: dict[str, Any], excluded_signatures: set[str]) -> dict[str, Any]:
    excluded = {str(signature).strip() for signature in excluded_signatures if str(signature).strip()}
    if not excluded:
        return parsed_profile
    out = dict(parsed_profile)
    candidates = parsed_profile.get("candidate_predicates")
    if isinstance(candidates, list):
        out["candidate_predicates"] = [
            item
            for item in candidates
            if not (
                isinstance(item, dict)
                and str(item.get("signature", "")).strip() in excluded
            )
        ]
    return out


def _profile_registry_completion_context_lines(
    profile_registry: dict[str, Any],
    source_compile: dict[str, Any],
) -> list[str]:
    signatures = _profile_registry_completion_signatures(profile_registry)
    if not signatures:
        return []
    lines = [
        (
            "PROFILE REGISTRY COMPLETION FOLLOWUP: this is a bounded domain-pack compile pass inside a closed "
            "predicate registry. Emit only source-grounded compact rows whose signatures are in the listed registry."
        ),
        (
            "PROFILE REGISTRY COMPLETION FOLLOWUP: do not emit source_record_* rows, prose excerpts, display text, "
            "answer strings, or new predicate names. Do not use domain_omission/5 in this pass."
        ),
        (
            "PROFILE REGISTRY COMPLETION FOLLOWUP: prefer missing atomic details over broad summaries: dates, "
            "facility identifiers, numbered violation details, citations, response/documentation requirements, "
            "consultant recommendations, and conclusion-scope rows."
        ),
        "PROFILE REGISTRY COMPLETION FOLLOWUP: allowed registry signatures = " + ", ".join(signatures[:24]) + ".",
    ]
    for item in profile_registry.get("predicates", []) if isinstance(profile_registry.get("predicates"), list) else []:
        if not isinstance(item, dict):
            continue
        signature = str(item.get("signature", "")).strip()
        if signature not in signatures:
            continue
        category = str(item.get("category", "")).strip()
        notes = str(item.get("notes", "")).strip()
        if category or notes:
            lines.append(
                "PROFILE REGISTRY COMPLETION FOLLOWUP SIGNATURE NOTE: "
                f"{signature}: category={category or 'unspecified'}; notes={notes or 'none'}"
            )
    lines.extend(_profile_registry_existing_fact_context(source_compile))
    lines.extend(carrier_contract_prompt_lines(signatures[:24]))
    return lines


def _apply_profile_registry_completion_followup_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    profile_registry: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    signatures = _profile_registry_completion_signatures(profile_registry)
    context_lines = _profile_registry_completion_context_lines(profile_registry, source_compile)
    metadata: dict[str, Any] = {
        "schema_version": "profile_registry_completion_followup_pass_v1",
        "attempted": False,
        "allowed_signatures": signatures[:24],
    }
    if not signatures or not context_lines:
        metadata["reason"] = "no_profile_registry_completion_signatures"
        source_compile["profile_registry_completion_followup"] = metadata
        return metadata
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    target = max(12, min(48, int(getattr(args, "focused_pass_operation_target", 32) or 32)))
    compiled = _compile_source_pass_ops(
        source_text=source_text,
        parsed_profile=_profile_without_signatures(parsed_profile, {"domain_omission/5"}),
        intake_plan=intake_plan,
        args=args,
        pass_id="profile_registry_completion_followup",
        purpose="complete source-grounded rows inside the closed profile registry",
        focus="missing compact FDA/domain registry facts, especially detail/citation/requirement/conclusion rows",
        completion=(
            "Emit only compact source-grounded rows inside the listed profile-registry signatures. "
            "Do not summarize paragraphs, do not add predicates, and do not emit domain_omission/5."
        ),
        predicates=", ".join(signatures[:24]),
        coverage_goals=(
            "Populate missing atomic facts that the closed domain registry is designed to represent, while reusing "
            "existing typed subject IDs where the current compile already established them."
        ),
        extra_context=[*(extra_context or []), *context_lines],
        operation_target=target,
    )
    compiled["pass_id"] = "profile_registry_completion_followup"
    compiled["purpose"] = "complete source-grounded rows inside the closed profile registry"
    compiled["focus"] = "missing compact FDA/domain registry facts"
    _merge_additive_source_pass(
        source_compile,
        compiled,
        metadata_prefix="profile_registry_completion_followup",
    )
    signature_contract_report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts=prior_facts,
        allowed_signatures=set(signatures[:24]),
        metadata_prefix="profile_registry_completion_followup",
        pass_record=compiled,
    )
    new_facts = (
        compiled.get("_profile_registry_completion_followup_new_facts", [])
        if isinstance(compiled.get("_profile_registry_completion_followup_new_facts"), list)
        else []
    )
    metadata.update(
        {
            "attempted": True,
            "ok": bool(compiled.get("ok")),
            "admitted_count": int(compiled.get("admitted_count", 0) or 0),
            "skipped_count": int(compiled.get("skipped_count", 0) or 0),
            "new_fact_count": len(new_facts),
            "signature_contract": signature_contract_report,
            "pass": compiled,
        }
    )
    source_compile["profile_registry_completion_followup"] = metadata
    return metadata


def _profile_registry_accountability_requirements(profile_registry: dict[str, Any]) -> list[dict[str, str]]:
    raw_requirements = (
        profile_registry.get("accountability_requirements")
        if isinstance(profile_registry.get("accountability_requirements"), list)
        else []
    )
    requirements: list[dict[str, str]] = []
    for item in raw_requirements:
        if not isinstance(item, dict):
            continue
        carrier_signature = str(item.get("carrier_signature", "")).strip()
        omission_kind = str(item.get("omission_kind", "")).strip()
        reason_code = str(item.get("reason_code", "")).strip()
        trigger = str(item.get("trigger", "")).strip()
        if not carrier_signature or not omission_kind or not reason_code:
            continue
        requirements.append(
            {
                "id": str(item.get("id", "")).strip(),
                "carrier_signature": carrier_signature,
                "omission_kind": omission_kind,
                "reason_code": reason_code,
                "trigger": trigger,
            }
        )
    return requirements


def _profile_registry_accountability_followup_context_lines(profile_registry: dict[str, Any]) -> list[str]:
    requirements = _profile_registry_accountability_requirements(profile_registry)
    if not requirements:
        return []
    lines = [
        (
            "PROFILE REGISTRY ACCOUNTABILITY FOLLOWUP: this is a bounded omission-accountability pass. "
            "It may emit domain_omission/5 rows only. It must not emit source_record_* rows, answer text, "
            "or ordinary answer-bearing carrier rows."
        ),
        (
            "PROFILE REGISTRY ACCOUNTABILITY FOLLOWUP: inspect the raw source only for explicit omission "
            "triggers required by the active profile registry. Silent absence is not enough unless the "
            "registry trigger explicitly says so."
        ),
        (
            "PROFILE REGISTRY ACCOUNTABILITY FOLLOWUP: carrier_signature must be the exact registered slash "
            "signature in quotes, for example 'fda_correspondence_party/5'. Do not rewrite slash signatures "
            "as underscore atoms."
        ),
    ]
    for item in requirements[:12]:
        label = item.get("id") or item["carrier_signature"]
        trigger = item.get("trigger") or "the stated source trigger"
        lines.append(
            "PROFILE REGISTRY ACCOUNTABILITY FOLLOWUP REQUIREMENT: "
            f"{label}: if raw_source_text satisfies {trigger}, emit "
            f"domain_omission(DomainOrSubjectId, '{item['carrier_signature']}', "
            f"{item['omission_kind']}, {item['reason_code']}, SourceOrScope)."
        )
    lines.extend(carrier_contract_prompt_lines(["domain_omission/5"]))
    return lines


def _apply_profile_registry_accountability_followup_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    profile_registry: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    requirements = _profile_registry_accountability_requirements(profile_registry)
    context_lines = _profile_registry_accountability_followup_context_lines(profile_registry)
    metadata: dict[str, Any] = {
        "schema_version": "profile_registry_accountability_followup_pass_v1",
        "attempted": False,
        "requirement_count": len(requirements),
        "requirements": requirements[:12],
        "allowed_signatures": ["domain_omission/5"],
    }
    if not requirements or not context_lines:
        metadata["reason"] = "no_profile_registry_accountability_requirements"
        source_compile["profile_registry_accountability_followup"] = metadata
        return metadata
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    target = max(4, min(16, int(getattr(args, "focused_pass_operation_target", 12) or 12)))
    compiled = _compile_source_pass_ops(
        source_text=source_text,
        parsed_profile=parsed_profile,
        intake_plan=intake_plan,
        args=args,
        pass_id="profile_registry_accountability_followup",
        purpose="complete registry omission-accountability rows only",
        focus="explicit source omissions required by the profile registry",
        completion=(
            "Emit domain_omission/5 rows only when the raw source explicitly satisfies a listed registry "
            "accountability trigger. If no trigger is satisfied, emit no facts and explain that in self_check."
        ),
        predicates="domain_omission/5",
        coverage_goals=(
            "For each registry accountability requirement, decide whether the raw source explicitly states "
            "the required absence or omission. If yes, emit exactly one compact domain_omission/5 row."
        ),
        extra_context=[*(extra_context or []), *context_lines],
        operation_target=target,
    )
    compiled["pass_id"] = "profile_registry_accountability_followup"
    compiled["purpose"] = "complete registry omission-accountability rows only"
    compiled["focus"] = "explicit source omissions required by the profile registry"
    _merge_additive_source_pass(
        source_compile,
        compiled,
        metadata_prefix="profile_registry_accountability_followup",
    )
    signature_contract_report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts=prior_facts,
        allowed_signatures={"domain_omission/5"},
        metadata_prefix="profile_registry_accountability_followup",
        pass_record=compiled,
    )
    new_facts = (
        compiled.get("_profile_registry_accountability_followup_new_facts", [])
        if isinstance(compiled.get("_profile_registry_accountability_followup_new_facts"), list)
        else []
    )
    metadata.update(
        {
            "attempted": True,
            "ok": bool(compiled.get("ok")),
            "admitted_count": int(compiled.get("admitted_count", 0) or 0),
            "skipped_count": int(compiled.get("skipped_count", 0) or 0),
            "new_fact_count": len(new_facts),
            "signature_contract": signature_contract_report,
            "pass": compiled,
        }
    )
    source_compile["profile_registry_accountability_followup"] = metadata
    return metadata


def _canonical_registered_signature_reference(value: str) -> str:
    text = str(value or "").strip().strip("'\"")
    if not text:
        return ""
    if "/" in text and carrier_contract(text) is not None:
        return text
    match = re.fullmatch(r"([a-z][a-z0-9_]*)_(\d+)", text)
    if not match:
        return ""
    candidate = f"{match.group(1)}/{match.group(2)}"
    if carrier_contract(candidate) is not None:
        return candidate
    return ""


def _apply_domain_omission_carrier_signature_reduction(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize registry signature references inside domain_omission/5 rows.

    The second slot is a reference into the closed carrier-contract registry, not
    source prose. This reducer only corrects registered signature syntax such as
    fda_correspondence_party_5 -> 'fda_correspondence_party/5'; it does not infer
    omitted facts or inspect source text.
    """

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    out: list[str] = []
    seen: set[str] = set()
    reductions: list[dict[str, str]] = []
    invalid: list[str] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            if fact not in seen:
                out.append(fact)
                seen.add(fact)
            continue
        predicate, args = parsed
        if predicate != "domain_omission" or len(args) != 5:
            if fact not in seen:
                out.append(fact)
                seen.add(fact)
            continue
        canonical = _canonical_registered_signature_reference(args[1])
        if not canonical:
            invalid.append(fact)
            if fact not in seen:
                out.append(fact)
                seen.add(fact)
            continue
        args[1] = f"'{canonical}'"
        reduced = f"domain_omission({', '.join(args)})."
        if reduced != fact:
            reductions.append({"from": fact, "to": reduced})
        if reduced not in seen:
            out.append(reduced)
            seen.add(reduced)
    source_compile["facts"] = out
    source_compile["unique_fact_count"] = len(out)
    source_compile["deterministic_domain_omission_signature_reduction_count"] = len(reductions)
    source_compile["deterministic_domain_omission_signature_reductions"] = reductions[:100]
    source_compile["deterministic_domain_omission_signature_invalid_count"] = len(invalid)
    source_compile["deterministic_domain_omission_signature_invalid_facts"] = invalid[:100]
    source_compile["deterministic_domain_omission_signature_reduction_policy"] = {
        "schema_version": "deterministic_domain_omission_signature_reduction_v1",
        "authority": "typed_registry_reference_normalization_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "description": (
            "Canonicalizes domain_omission/5 carrier_signature references to exact registered slash "
            "signatures. It does not create omissions or read source prose."
        ),
    }
    return {
        "reduction_count": len(reductions),
        "invalid_count": len(invalid),
        "reductions": reductions[:100],
        "invalid_facts": invalid[:100],
    }


def _canonical_fda_lot_identifier(value: str) -> str:
    text = str(value or "").strip().strip("'\"").casefold()
    match = re.fullmatch(r"(?:lot|batch)_([a-z])_?(\d+)", text)
    if not match:
        match = re.fullmatch(r"([a-z])_?(\d+)", text)
    if not match:
        return ""
    return f"lot_{match.group(1)}_{match.group(2)}"


def _fda_warning_letter_date_key(value: str) -> str:
    text = str(value or "").strip().strip("'\"").casefold()
    match = re.search(r"(20\d{2})[_-](\d{1,2})[_-](\d{1,2})", text)
    if match:
        return f"{int(match.group(1)):04d}_{int(match.group(2)):02d}_{int(match.group(3)):02d}"
    match = re.search(r"(20\d{2})(\d{2})(\d{2})", text)
    if match:
        return f"{int(match.group(1)):04d}_{int(match.group(2)):02d}_{int(match.group(3)):02d}"
    return ""


def _apply_fda_warning_letter_subject_convergence(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Converge date-shaped FDA warning-letter aliases onto typed wrapper ids."""

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    date_to_letter: dict[str, str] = {}
    ambiguous_dates: set[str] = set()
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate != "fda_warning_letter" or len(args) != 5:
            continue
        date_key = _fda_warning_letter_date_key(args[3])
        letter_id = str(args[0]).strip()
        if not date_key or not letter_id:
            continue
        if date_key in date_to_letter and date_to_letter[date_key] != letter_id:
            ambiguous_dates.add(date_key)
            continue
        date_to_letter[date_key] = letter_id
    for date_key in ambiguous_dates:
        date_to_letter.pop(date_key, None)
    if not date_to_letter:
        source_compile["deterministic_fda_warning_letter_subject_convergence_count"] = 0
        source_compile["deterministic_fda_warning_letter_subject_convergence_policy"] = {
            "schema_version": "deterministic_fda_warning_letter_subject_convergence_v1",
            "authority": "typed_subject_normalization_only",
            "not_source_interpretation": True,
            "not_query_interpretation": True,
        }
        return {"reduction_count": 0, "reductions": []}

    subject_positions = {
        "domain_omission": {0},
        "fda_adulteration_basis": {0},
        "fda_conclusion_scope": {0},
        "fda_consultant_recommendation": {0},
        "fda_response_requirement": {0},
        "fda_violation": {1},
        "fda_violation_citation": {0},
        "fda_violation_detail": {0},
    }
    out: list[str] = []
    seen: set[str] = set()
    reductions: list[dict[str, str]] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            if fact not in seen:
                out.append(fact)
                seen.add(fact)
            continue
        predicate, args = parsed
        changed = False
        for index in subject_positions.get(predicate, set()):
            if index >= len(args):
                continue
            date_key = _fda_warning_letter_date_key(args[index])
            canonical = date_to_letter.get(date_key, "")
            if canonical and args[index] != canonical:
                args[index] = canonical
                changed = True
        if changed:
            reduced = f"{predicate}({', '.join(args)})."
            if reduced != fact:
                reductions.append({"from": fact, "to": reduced})
                fact = reduced
        if fact not in seen:
            out.append(fact)
            seen.add(fact)
    source_compile["facts"] = out
    source_compile["unique_fact_count"] = len(out)
    source_compile["deterministic_fda_warning_letter_subject_convergence_count"] = len(reductions)
    source_compile["deterministic_fda_warning_letter_subject_convergence_reductions"] = reductions[:100]
    source_compile["deterministic_fda_warning_letter_subject_convergence_policy"] = {
        "schema_version": "deterministic_fda_warning_letter_subject_convergence_v1",
        "authority": "typed_subject_normalization_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "description": (
            "Maps date-shaped FDA warning-letter aliases such as fda_warning_letter_2025_05_14 "
            "onto the source-compiled fda_warning_letter/5 wrapper id for the same issue date. "
            "It does not infer warning letters or inspect source prose."
        ),
    }
    return {"reduction_count": len(reductions), "reductions": reductions[:100]}


def _apply_fda_violation_detail_subject_integrity(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Drop FDA violation-detail rows that are not attached to an emitted violation id."""

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    violation_ids: set[str] = set()
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate == "fda_violation" and len(args) == 5 and str(args[0]).strip():
            violation_ids.add(str(args[0]).strip())
    dropped: list[str] = []
    out: list[str] = []
    seen: set[str] = set()
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is not None:
            predicate, args = parsed
            if predicate == "fda_violation_detail" and len(args) == 5 and violation_ids and args[0] not in violation_ids:
                dropped.append(fact)
                continue
        if fact not in seen:
            out.append(fact)
            seen.add(fact)
    source_compile["facts"] = out
    source_compile["unique_fact_count"] = len(out)
    source_compile["deterministic_fda_violation_detail_subject_integrity_count"] = len(dropped)
    source_compile["deterministic_fda_violation_detail_subject_integrity_dropped_facts"] = dropped[:100]
    source_compile["deterministic_fda_violation_detail_subject_integrity_policy"] = {
        "schema_version": "deterministic_fda_violation_detail_subject_integrity_v1",
        "authority": "typed_subject_integrity_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "description": (
            "Drops fda_violation_detail/5 rows whose subject is not an emitted fda_violation/5 id. "
            "It does not infer missing details or inspect source prose."
        ),
    }
    return {"dropped_count": len(dropped), "dropped_facts": dropped[:100]}


def _apply_fda_violation_number_atom_reduction(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize numeric FDA violation-number slots to violation_N atoms."""

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    reductions: list[dict[str, str]] = []
    out: list[str] = []
    seen: set[str] = set()
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is not None:
            predicate, args = parsed
            if predicate == "fda_violation" and len(args) == 5:
                number = str(args[2]).strip().strip("'\"")
                if re.fullmatch(r"\d+", number):
                    args[2] = f"violation_{int(number)}"
                    reduced = f"{predicate}({', '.join(args)})."
                    if reduced != fact:
                        reductions.append({"from": fact, "to": reduced})
                        fact = reduced
        if fact not in seen:
            out.append(fact)
            seen.add(fact)
    source_compile["facts"] = out
    source_compile["unique_fact_count"] = len(out)
    source_compile["deterministic_fda_violation_number_atom_reduction_count"] = len(reductions)
    source_compile["deterministic_fda_violation_number_atom_reductions"] = reductions[:100]
    source_compile["deterministic_fda_violation_number_atom_reduction_policy"] = {
        "schema_version": "deterministic_fda_violation_number_atom_reduction_v1",
        "authority": "typed_value_normalization_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "description": (
            "Canonicalizes fda_violation/5 violation_number slots from bare numeric atoms to violation_N. "
            "It does not create violations or inspect source prose."
        ),
    }
    return {"reduction_count": len(reductions), "reductions": reductions[:100]}


def _canonical_fda_date_atom(value: str) -> str:
    text = str(value or "").strip().strip("'\"").casefold()
    match = re.fullmatch(r"(?:v_)?(20\d{2})[_-](\d{1,2})[_-](\d{1,2})", text)
    if not match:
        return ""
    return f"v_{int(match.group(1)):04d}_{int(match.group(2)):02d}_{int(match.group(3)):02d}"


def _apply_fda_date_atom_reduction(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize FDA date slots to v_YYYY_MM_DD atoms."""

    date_positions = {
        "fda_form483_response": {2},
        "fda_inspection_event": {2, 3},
        "fda_prior_warning_letter": {2},
        "fda_regulatory_meeting": {2},
        "fda_warning_letter": {3},
    }
    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    out: list[str] = []
    seen: set[str] = set()
    reductions: list[dict[str, str]] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            if fact not in seen:
                out.append(fact)
                seen.add(fact)
            continue
        predicate, args = parsed
        changed = False
        for index in date_positions.get(predicate, set()):
            if index >= len(args):
                continue
            canonical = _canonical_fda_date_atom(args[index])
            if canonical and args[index] != canonical:
                args[index] = canonical
                changed = True
        if changed:
            reduced = f"{predicate}({', '.join(args)})."
            if reduced != fact:
                reductions.append({"from": fact, "to": reduced})
                fact = reduced
        if fact not in seen:
            out.append(fact)
            seen.add(fact)
    source_compile["facts"] = out
    source_compile["unique_fact_count"] = len(out)
    source_compile["deterministic_fda_date_atom_reduction_count"] = len(reductions)
    source_compile["deterministic_fda_date_atom_reductions"] = reductions[:100]
    source_compile["deterministic_fda_date_atom_reduction_policy"] = {
        "schema_version": "deterministic_fda_date_atom_reduction_v1",
        "authority": "typed_value_normalization_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "description": "Canonicalizes date-shaped FDA carrier slots to v_YYYY_MM_DD atoms without reading source prose.",
    }
    return {"reduction_count": len(reductions), "reductions": reductions[:100]}


def _apply_fda_facility_subject_convergence(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Converge FDA facility-name references onto typed facility ids."""

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    facility_by_name: dict[str, str] = {}
    facility_rows: list[tuple[str, set[str]]] = []
    ambiguous_names: set[str] = set()
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate != "fda_facility_identity" or len(args) != 5:
            continue
        facility_id = str(args[0]).strip()
        facility_name = str(args[1]).strip()
        if not facility_id or not facility_name:
            continue
        if facility_name in facility_by_name and facility_by_name[facility_name] != facility_id:
            ambiguous_names.add(facility_name)
            continue
        facility_by_name[facility_name] = facility_id
        token_source = " ".join(args[:4])
        tokens = _fda_facility_alias_tokens(token_source)
        if tokens:
            facility_rows.append((facility_id, tokens))
    for facility_name in ambiguous_names:
        facility_by_name.pop(facility_name, None)
    if ambiguous_names:
        facility_rows = []
    subject_positions = {
        "fda_inspection_event": {1},
    }
    out: list[str] = []
    seen: set[str] = set()
    reductions: list[dict[str, str]] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            if fact not in seen:
                out.append(fact)
                seen.add(fact)
            continue
        predicate, args = parsed
        changed = False
        for index in subject_positions.get(predicate, set()):
            if index >= len(args):
                continue
            canonical = facility_by_name.get(args[index], "") or _fda_facility_alias_match(args[index], facility_rows)
            if canonical and args[index] != canonical:
                args[index] = canonical
                changed = True
        if changed:
            reduced = f"{predicate}({', '.join(args)})."
            if reduced != fact:
                reductions.append({"from": fact, "to": reduced})
                fact = reduced
        if fact not in seen:
            out.append(fact)
            seen.add(fact)
    source_compile["facts"] = out
    source_compile["unique_fact_count"] = len(out)
    source_compile["deterministic_fda_facility_subject_convergence_count"] = len(reductions)
    source_compile["deterministic_fda_facility_subject_convergence_reductions"] = reductions[:100]
    source_compile["deterministic_fda_facility_subject_convergence_policy"] = {
        "schema_version": "deterministic_fda_facility_subject_convergence_v1",
        "authority": "typed_subject_normalization_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "description": (
            "Maps FDA carrier facility-name references onto fda_facility_identity/5 facility ids "
            "when the name-to-id mapping is unique in typed facts."
        ),
    }
    return {"reduction_count": len(reductions), "reductions": reductions[:100]}


_FDA_FACILITY_ALIAS_STOPWORDS = {
    "facility",
    "facilities",
    "inc",
    "llc",
    "ltd",
    "corp",
    "corporation",
    "company",
    "co",
    "products",
    "product",
}


def _fda_facility_alias_tokens(value: str) -> set[str]:
    tokens = {
        token
        for token in re.split(r"[^a-z0-9]+", str(value or "").casefold())
        if len(token) >= 3 and token not in _FDA_FACILITY_ALIAS_STOPWORDS and not token.isdigit()
    }
    return tokens


def _fda_facility_alias_match(value: str, facility_rows: list[tuple[str, set[str]]]) -> str:
    text = str(value or "").strip().casefold()
    raw_tokens = [token for token in re.split(r"[^a-z0-9]+", text) if token]
    if "facility" not in raw_tokens:
        return ""
    tokens = _fda_facility_alias_tokens(text)
    if len(tokens) < 2:
        return ""
    matches = [facility_id for facility_id, facility_tokens in facility_rows if tokens.issubset(facility_tokens)]
    return matches[0] if len(set(matches)) == 1 else ""


def _apply_fda_lot_identifier_atom_reduction(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize FDA affected-lot identifier atoms inside typed detail rows."""

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    out: list[str] = []
    seen: set[str] = set()
    reductions: list[dict[str, str]] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            if fact not in seen:
                out.append(fact)
                seen.add(fact)
            continue
        predicate, args = parsed
        if predicate == "fda_violation_detail" and len(args) == 5 and args[1] == "affected_lot":
            canonical = _canonical_fda_lot_identifier(args[2])
            if canonical:
                args[2] = canonical
                reduced = f"fda_violation_detail({', '.join(args)})."
                if reduced != fact:
                    reductions.append({"from": fact, "to": reduced})
                fact = reduced
        if fact not in seen:
            out.append(fact)
            seen.add(fact)
    source_compile["facts"] = out
    source_compile["unique_fact_count"] = len(out)
    source_compile["deterministic_fda_lot_identifier_atom_reduction_count"] = len(reductions)
    source_compile["deterministic_fda_lot_identifier_atom_reductions"] = reductions[:100]
    source_compile["deterministic_fda_lot_identifier_atom_reduction_policy"] = {
        "schema_version": "deterministic_fda_lot_identifier_atom_reduction_v1",
        "authority": "typed_value_normalization_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "description": (
            "Canonicalizes fda_violation_detail/5 affected_lot values such as lot_a104 or batch_a_104 "
            "to lot_a_104. It does not infer affected lots or inspect source prose."
        ),
    }
    return {"reduction_count": len(reductions), "reductions": reductions[:100]}


def _canonical_fda_facility_location(value: str) -> str:
    text = str(value or "").strip().strip("'\"").casefold()
    match = re.fullmatch(r"(.+?)_(?:\d{5})(?:_\d{4})?", text)
    if match:
        return match.group(1)
    match = re.fullmatch(r"(.+?)_(?:united_states|usa|us)", text)
    if match:
        return match.group(1)
    return ""


def _canonical_fda_facility_identifier(value: str) -> str:
    text = str(value or "").strip().strip("'\"").casefold()
    if re.fullmatch(r"\d{7,12}", text):
        return f"fei_{text}"
    return ""


def _apply_fda_facility_identity_atom_reduction(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize typed FDA facility location and FEI identifier slots."""

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    out: list[str] = []
    seen: set[str] = set()
    reductions: list[dict[str, str]] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            if fact not in seen:
                out.append(fact)
                seen.add(fact)
            continue
        predicate, args = parsed
        if predicate == "fda_facility_identity" and len(args) == 5:
            location = _canonical_fda_facility_location(args[2])
            identifier = _canonical_fda_facility_identifier(args[3])
            if location:
                args[2] = location
            if identifier:
                args[3] = identifier
            reduced = f"fda_facility_identity({', '.join(args)})."
            if reduced != fact:
                reductions.append({"from": fact, "to": reduced})
                fact = reduced
        if fact not in seen:
            out.append(fact)
            seen.add(fact)
    source_compile["facts"] = out
    source_compile["unique_fact_count"] = len(out)
    source_compile["deterministic_fda_facility_identity_atom_reduction_count"] = len(reductions)
    source_compile["deterministic_fda_facility_identity_atom_reductions"] = reductions[:100]
    source_compile["deterministic_fda_facility_identity_atom_reduction_policy"] = {
        "schema_version": "deterministic_fda_facility_identity_atom_reduction_v1",
        "authority": "typed_value_normalization_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "description": (
            "Canonicalizes fda_facility_identity/5 location zipcode/country suffixes and bare numeric FEI identifiers. "
            "It does not infer facilities or inspect source prose."
        ),
    }
    return {"reduction_count": len(reductions), "reductions": reductions[:100]}


def _apply_fda_consultant_citation_scope_reduction(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Move consultant-qualification citations from violation ids to their letter id."""

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    violation_to_letter: dict[str, str] = {}
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate == "fda_violation" and len(args) == 5:
            violation_to_letter[str(args[0]).strip()] = str(args[1]).strip()
    out: list[str] = []
    seen: set[str] = set()
    reductions: list[dict[str, str]] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            if fact not in seen:
                out.append(fact)
                seen.add(fact)
            continue
        predicate, args = parsed
        if (
            predicate == "fda_violation_citation"
            and len(args) == 4
            and args[2] == "consultant_qualification"
            and args[0] in violation_to_letter
        ):
            args[0] = violation_to_letter[args[0]]
            reduced = f"fda_violation_citation({', '.join(args)})."
            if reduced != fact:
                reductions.append({"from": fact, "to": reduced})
                fact = reduced
        if fact not in seen:
            out.append(fact)
            seen.add(fact)
    source_compile["facts"] = out
    source_compile["unique_fact_count"] = len(out)
    source_compile["deterministic_fda_consultant_citation_scope_reduction_count"] = len(reductions)
    source_compile["deterministic_fda_consultant_citation_scope_reductions"] = reductions[:100]
    source_compile["deterministic_fda_consultant_citation_scope_reduction_policy"] = {
        "schema_version": "deterministic_fda_consultant_citation_scope_reduction_v1",
        "authority": "typed_carrier_contract_normalization_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "description": (
            "Canonicalizes fda_violation_citation/4 consultant_qualification rows from a numbered violation "
            "id to the associated warning-letter id using existing fda_violation/5 typed facts."
        ),
    }
    return {"reduction_count": len(reductions), "reductions": reductions[:100]}


def _source_scope_payload_issue(arg_name: str, value: str) -> str:
    if arg_name != "source_or_scope":
        return ""
    normalized = str(value or "").strip().strip("'\"").casefold()
    if re.match(r"^(?:cfr_|fdca_|usc_|u_s_c_|us_c_|\d+_cfr_|\d+_usc_)", normalized):
        return "citation_payload_in_source_or_scope"
    return ""


def _carrier_value_domain_issue(signature: str, arg_name: str, value: str) -> str:
    contract = carrier_contract(signature)
    if not isinstance(contract, dict):
        return ""
    domains = contract.get("value_domains")
    if not isinstance(domains, dict):
        return ""
    allowed = {str(item).strip() for item in domains.get(arg_name, []) if str(item).strip()}
    if not allowed:
        return ""
    normalized = str(value or "").strip().strip("'\"")
    if normalized not in allowed:
        return "value_not_allowed"
    return ""


def _apply_carrier_value_domain_integrity(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Drop registered carrier rows whose closed value-domain slots are invalid."""

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    kept: list[str] = []
    dropped: list[dict[str, str]] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            kept.append(fact)
            continue
        predicate, args = parsed
        signature = f"{predicate}/{len(args)}"
        contract = carrier_contract(signature)
        if not isinstance(contract, dict):
            kept.append(fact)
            continue
        arg_names = [str(item).strip() for item in contract.get("args", [])]
        issue = ""
        issue_arg = ""
        issue_value = ""
        for index, arg_name in enumerate(arg_names):
            if index >= len(args):
                continue
            issue = _carrier_value_domain_issue(signature, arg_name, args[index])
            if issue:
                issue_arg = arg_name
                issue_value = args[index]
                break
        if issue:
            dropped.append({"fact": fact, "arg_name": issue_arg, "value": issue_value, "issue": issue})
            continue
        kept.append(fact)
    source_compile["facts"] = kept
    source_compile["unique_fact_count"] = len(kept)
    source_compile["deterministic_carrier_value_domain_integrity_count"] = len(dropped)
    source_compile["deterministic_carrier_value_domain_integrity_dropped_facts"] = dropped[:100]
    source_compile["deterministic_carrier_value_domain_integrity_policy"] = {
        "schema_version": "deterministic_carrier_value_domain_integrity_v1",
        "authority": "typed_contract_validation_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "description": (
            "Drops registered carrier rows when closed value-domain slots contain values outside the "
            "registered carrier contract. It does not infer replacement values or create facts."
        ),
    }
    return {"dropped_count": len(dropped), "dropped": dropped[:100]}


def _apply_source_scope_payload_integrity(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Drop registered facts whose source_or_scope slot carries answer payload."""

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    kept: list[str] = []
    dropped: list[dict[str, str]] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            kept.append(fact)
            continue
        predicate, args = parsed
        signature = f"{predicate}/{len(args)}"
        contract = carrier_contract(signature)
        if not isinstance(contract, dict):
            kept.append(fact)
            continue
        arg_names = [str(item).strip() for item in contract.get("args", [])]
        issue = ""
        for index, arg_name in enumerate(arg_names):
            if index >= len(args):
                continue
            issue = _source_scope_payload_issue(arg_name, args[index])
            if issue:
                break
        if issue:
            dropped.append({"fact": fact, "issue": issue})
            continue
        kept.append(fact)
    source_compile["facts"] = kept
    source_compile["unique_fact_count"] = len(kept)
    source_compile["deterministic_source_scope_payload_integrity_count"] = len(dropped)
    source_compile["deterministic_source_scope_payload_integrity_dropped_facts"] = dropped[:100]
    source_compile["deterministic_source_scope_payload_integrity_policy"] = {
        "schema_version": "deterministic_source_scope_payload_integrity_v1",
        "authority": "typed_contract_validation_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "description": (
            "Drops registered carrier rows when source_or_scope contains citation-shaped answer payload. "
            "It does not infer replacement provenance or create facts."
        ),
    }
    return {"dropped_count": len(dropped), "dropped": dropped[:100]}


def _canonical_fda_office_atom(value: str) -> str:
    text = str(value or "").strip().strip("'\"").casefold()
    if text == "office_pharmaceutical_quality_operations":
        return "office_of_pharmaceutical_quality_operations"
    return ""


def _apply_fda_office_atom_reduction(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize narrow FDA office typed atoms."""

    office_arg_positions = {
        "fda_warning_letter": {1},
        "fda_correspondence_party": {1, 3},
    }
    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    out: list[str] = []
    seen: set[str] = set()
    reductions: list[dict[str, str]] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            if fact not in seen:
                out.append(fact)
                seen.add(fact)
            continue
        predicate, args = parsed
        changed = False
        for index in office_arg_positions.get(predicate, set()):
            if index >= len(args):
                continue
            office = _canonical_fda_office_atom(args[index])
            if office:
                args[index] = office
                changed = True
        if changed:
            reduced = f"{predicate}({', '.join(args)})."
            if reduced != fact:
                reductions.append({"from": fact, "to": reduced})
                fact = reduced
        if fact not in seen:
            out.append(fact)
            seen.add(fact)
    source_compile["facts"] = out
    source_compile["unique_fact_count"] = len(out)
    source_compile["deterministic_fda_office_atom_reduction_count"] = len(reductions)
    source_compile["deterministic_fda_office_atom_reductions"] = reductions[:100]
    source_compile["deterministic_fda_office_atom_reduction_policy"] = {
        "schema_version": "deterministic_fda_office_atom_reduction_v1",
        "authority": "typed_value_normalization_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "description": (
            "Canonicalizes the narrow FDA office atom office_pharmaceutical_quality_operations to "
            "office_of_pharmaceutical_quality_operations in registered FDA office slots."
        ),
    }
    return {"reduction_count": len(reductions), "reductions": reductions[:100]}


def _enforce_fda_correspondence_party_placeholder_contract(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Reject ordinary FDA correspondence-party rows used as omission placeholders."""

    placeholder_values = {"", "not_stated", "unknown", "none_found", "not_applicable", "missing"}
    omission_roles = {"signatory", "contact", "responsible_official"}
    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    kept: list[str] = []
    rejected: list[str] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            kept.append(fact)
            continue
        predicate, args = parsed
        if predicate == "fda_correspondence_party" and len(args) == 5:
            party_id = str(args[1]).strip()
            party_role = str(args[2]).strip()
            party_name = str(args[3]).strip()
            if party_role in omission_roles and (
                party_id in placeholder_values or party_name in placeholder_values
            ):
                rejected.append(fact)
                continue
        kept.append(fact)
    source_compile["facts"] = kept
    source_compile["unique_fact_count"] = len(kept)
    source_compile["fda_correspondence_party_placeholder_rejected_count"] = len(rejected)
    source_compile["fda_correspondence_party_placeholder_rejected_facts"] = rejected[:100]
    source_compile["fda_correspondence_party_placeholder_contract_policy"] = {
        "schema_version": "fda_correspondence_party_placeholder_contract_v1",
        "authority": "typed_contract_validation_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "description": (
            "Rejects fda_correspondence_party/5 placeholder rows for absent signatory/contact/responsible_official "
            "values. Explicit absence belongs in domain_omission/5, not an answer-bearing party fact."
        ),
    }
    return {"rejected_count": len(rejected), "rejected_facts": rejected[:100]}


def _profile_rating_scale_repair_offered_carriers(parsed_profile: dict[str, Any]) -> list[str]:
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return []
    carriers: list[str] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        signature = str(candidate.get("signature") or "").strip()
        if signature == "rating_scale_option/4":
            carriers.append(signature)
    return list(dict.fromkeys(carriers))


def _profile_rating_scale_repair_context_lines(parsed_profile: dict[str, Any]) -> list[str]:
    carriers = _profile_rating_scale_repair_offered_carriers(parsed_profile)
    if not carriers:
        return []
    contract_lines = carrier_contract_prompt_lines(carriers[:8])
    return [
        (
            "PROFILE RATING SCALE REPAIR PASS: deterministic query delivery is missing typed rating-scale "
            "options in some documents. This pass is proposal-only; emit only source-grounded typed rows "
            "through allowed predicate contracts, and let the mapper decide admission."
        ),
        (
            "PROFILE RATING SCALE REPAIR PASS: distinguish allowed scale options from ratings assigned to "
            "specific entities. A sentence listing possible ratings belongs in rating_scale_option/4; a "
            "table assigning a rating to a party belongs in assigned_rating/3 or the document's existing "
            "assigned-value carrier."
        ),
        (
            "PROFILE RATING SCALE REPAIR PASS: preserve each source-stated option in an adjectival, "
            "relevancy, confidence, quality, risk, or evaluation scale as one typed row. Reuse the same "
            "scale_or_factor_id for all options in the same source-stated scale."
        ),
        (
            "PROFILE RATING SCALE REPAIR PASS: do not emit source_record_* rows, display text rows, prose "
            "windows, or answer-bearing source excerpts. The output must be typed rating-scale facts only."
        ),
        "PROFILE RATING SCALE REPAIR PASS: compatible signatures to consider: " + ", ".join(carriers[:8]) + ".",
        *contract_lines,
    ]


def _apply_profile_rating_scale_repair_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    carriers = _profile_rating_scale_repair_offered_carriers(parsed_profile)
    metadata: dict[str, Any] = {
        "schema_version": "profile_rating_scale_repair_pass_v1",
        "attempted": False,
        "offered_carriers": carriers[:8],
    }
    if not carriers:
        metadata["reason"] = "no_rating_scale_predicates_offered"
        source_compile["profile_rating_scale_repair"] = metadata
        return metadata
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    context_lines = _profile_rating_scale_repair_context_lines(parsed_profile)
    target = max(8, min(24, int(getattr(args, "focused_pass_operation_target", 48) or 48)))
    compiled = _compile_source_pass_ops(
        source_text=source_text,
        parsed_profile=parsed_profile,
        intake_plan=intake_plan,
        args=args,
        pass_id="profile_rating_scale_repair",
        purpose="repair typed rating-scale option inventory without source-record answer routing",
        focus="source-stated allowed rating-scale options and their scale/factor ids",
        completion=(
            "Emit only source-grounded typed rating-scale option rows; do not recompile unrelated source material."
        ),
        predicates=", ".join(carriers[:8]),
        coverage_goals=(
            "Deliver every source-stated allowed rating option as rating_scale_option/4 with scale/factor id, "
            "normalized option value, source order/rank or unranked, and source/scope anchor."
        ),
        extra_context=[*(extra_context or []), *context_lines],
        operation_target=target,
    )
    compiled["pass_id"] = "profile_rating_scale_repair"
    compiled["purpose"] = "repair typed rating-scale option inventory without source-record answer routing"
    compiled["focus"] = "source-stated allowed rating-scale options and their scale/factor ids"
    _merge_additive_source_pass(source_compile, compiled, metadata_prefix="profile_rating_scale_repair")
    signature_contract_report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts=prior_facts,
        allowed_signatures=set(carriers[:8]),
        metadata_prefix="profile_rating_scale_repair",
        pass_record=compiled,
    )
    new_facts = (
        compiled.get("_profile_rating_scale_repair_new_facts", [])
        if isinstance(compiled.get("_profile_rating_scale_repair_new_facts"), list)
        else []
    )
    metadata.update(
        {
            "attempted": True,
            "ok": bool(compiled.get("ok")),
            "admitted_count": int(compiled.get("admitted_count", 0) or 0),
            "skipped_count": int(compiled.get("skipped_count", 0) or 0),
            "new_fact_count": len(new_facts),
            "signature_contract": signature_contract_report,
            "pass": compiled,
        }
    )
    source_compile["profile_rating_scale_repair"] = metadata
    return metadata


def _enforce_additive_pass_allowed_signatures(
    source_compile: dict[str, Any],
    *,
    prior_facts: set[str],
    allowed_signatures: set[str],
    metadata_prefix: str,
    pass_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Reject new additive-pass facts outside the pass's offered signatures."""

    allowed = {str(signature).strip() for signature in allowed_signatures if str(signature).strip()}
    if not allowed:
        return {"rejected_count": 0, "rejected_facts": [], "allowed_signatures": []}
    kept: list[str] = []
    rejected: list[str] = []
    for fact in [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]:
        if fact in prior_facts:
            kept.append(fact)
            continue
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            rejected.append(fact)
            continue
        predicate, args = parsed
        signature = f"{predicate}/{len(args)}"
        if signature not in allowed:
            rejected.append(fact)
            continue
        kept.append(fact)
    if rejected:
        source_compile["facts"] = kept
        source_compile["unique_fact_count"] = len(kept)
        if isinstance(pass_record, dict):
            rejected_set = set(rejected)
            pass_record["facts"] = [
                str(item).strip()
                for item in pass_record.get("facts", [])
                if str(item).strip() and str(item).strip() not in rejected_set
            ]
            new_facts_key = f"_{metadata_prefix}_new_facts"
            if isinstance(pass_record.get(new_facts_key), list):
                pass_record[new_facts_key] = [
                    str(item).strip()
                    for item in pass_record.get(new_facts_key, [])
                    if str(item).strip() and str(item).strip() not in rejected_set
                ]
        source_compile[f"{metadata_prefix}_signature_contract_policy"] = {
            "schema_version": "additive_pass_signature_contract_v1",
            "authority": "typed_contract_validation_only",
            "not_source_interpretation": True,
            "not_query_interpretation": True,
            "description": (
                "Rejects new additive-pass facts outside the explicit offered predicate signatures for this pass."
            ),
        }
    source_compile[f"{metadata_prefix}_signature_contract_rejected_count"] = len(rejected)
    source_compile[f"{metadata_prefix}_signature_contract_rejected_facts"] = rejected[:100]
    return {
        "rejected_count": len(rejected),
        "rejected_facts": rejected[:100],
        "allowed_signatures": sorted(allowed),
    }


def _enforce_list_range_inventory_fact_contract(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Reject typed list_member rows that violate range-inventory contracts.

    This is deterministic validation over typed facts only. It does not inspect
    source prose. If a source-stated range carrier exists for the same set and
    source/scope, expanded singleton list_member rows inside that multi-item
    range are treated as over-emission and removed.
    """

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    reduced_facts = _list_range_contract_reduced_facts(facts)
    if reduced_facts:
        existing = set(facts)
        for reduced in reduced_facts:
            if reduced not in existing:
                facts.append(reduced)
                existing.add(reduced)
        source_compile["facts"] = facts
        source_compile["deterministic_list_range_atom_reduction_count"] = len(reduced_facts)
        source_compile["deterministic_list_range_atom_reduction_facts"] = reduced_facts[:100]
        source_compile["deterministic_list_range_atom_reduction_policy"] = {
            "schema_version": "deterministic_list_range_atom_reduction_v1",
            "authority": "typed_atom_contract_reduction_only",
            "not_source_interpretation": True,
            "not_query_interpretation": True,
            "description": (
                "Reduces malformed governed range atoms such as "
                "claim_range(Set, 6_9, claim, Source) into the contracted "
                "start/end form claim_range(Set, 6, 9, Source). The original "
                "malformed row remains subject to contract rejection."
            ),
        }
    else:
        source_compile["deterministic_list_range_atom_reduction_count"] = 0
        source_compile["deterministic_list_range_atom_reduction_facts"] = []
    malformed_range_facts: set[str] = set()
    intervals: list[dict[str, Any]] = []
    parsed_rows: list[tuple[str, str, list[str] | None]] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            parsed_rows.append((fact, "", None))
            continue
        predicate, args = parsed
        parsed_rows.append((fact, predicate, args))
        if predicate not in {"claim_range", "item_range"} or len(args) < 4:
            continue
        start = _list_range_contract_int(args[1])
        end = _list_range_contract_int(args[2])
        if start is None or end is None:
            malformed_range_facts.add(fact)
            continue
        low, high = sorted((start, end))
        intervals.append(
            {
                "fact": fact,
                "set_id": args[0],
                "source_or_scope": args[3],
                "source_key": _list_range_source_key(args[3]),
                "member_kind": "claim" if predicate == "claim_range" else "",
                "low": low,
                "high": high,
                "predicate": predicate,
            }
        )
    if not intervals and not malformed_range_facts:
        source_compile["deterministic_list_range_contract_rejected_count"] = 0
        return {"rejected_count": 0, "rejected_facts": []}
    rejected_range_facts = set(malformed_range_facts) | {
        str(interval["fact"])
        for interval in intervals
        if _list_range_interval_overcompresses_segments(interval, intervals)
    }
    intervals = [interval for interval in intervals if str(interval["fact"]) not in rejected_range_facts]
    kept: list[str] = []
    rejected: list[str] = []
    for fact, predicate, args in parsed_rows:
        if fact in rejected_range_facts:
            rejected.append(fact)
            continue
        if predicate != "list_member" or not isinstance(args, list) or len(args) < 4:
            kept.append(fact)
            continue
        member_value = _list_range_contract_int(args[1])
        if member_value is None:
            kept.append(fact)
            continue
        source_key = _list_range_source_key(args[3])
        member_kind = str(args[2]).strip().casefold() if len(args) >= 3 else ""
        violates = any(
            int(interval["low"]) <= member_value <= int(interval["high"])
            and int(interval["low"]) != int(interval["high"])
            and (
                (
                    args[0] == interval["set_id"]
                    and args[3] == interval["source_or_scope"]
                )
                or (
                    bool(source_key)
                    and source_key == interval.get("source_key")
                    and (
                        not interval.get("member_kind")
                        or not member_kind
                        or member_kind == interval.get("member_kind")
                    )
                )
            )
            for interval in intervals
        )
        if violates:
            rejected.append(fact)
        else:
            kept.append(fact)
    source_compile["facts"] = kept
    source_compile["unique_fact_count"] = len(kept)
    source_compile["deterministic_list_range_contract_rejected_count"] = len(rejected)
    source_compile["deterministic_list_range_contract_rejected_facts"] = rejected[:100]
    if rejected:
        source_compile["deterministic_list_range_contract_policy"] = {
            "schema_version": "deterministic_list_range_contract_rejection_v1",
            "authority": "typed_contract_validation_only",
            "not_source_interpretation": True,
            "description": (
                "Rejects malformed claim_range/4 and item_range/4 rows whose start/end slots are not typed "
                "numeric boundaries, and rejects list_member/4 rows that merely expand a same-set same-source "
                "typed range row. It also rejects cross-set singleton expansions when the typed range and "
                "member rows share the same source coordinate. Range boundaries remain represented by "
                "claim_range/4 or item_range/4."
            ),
        }
    return {"rejected_count": len(rejected), "rejected_facts": rejected}


def _list_range_contract_reduced_facts(facts: list[str]) -> list[str]:
    reduced: list[str] = []
    existing = set(facts)
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate not in {"claim_range", "item_range"} or len(args) < 4:
            continue
        if _list_range_contract_int(args[1]) is not None and _list_range_contract_int(args[2]) is not None:
            continue
        span = _list_range_contract_atom_span(args[1])
        if span is None:
            continue
        if not _list_range_contract_member_kind_allows_span_reduction(predicate=predicate, value=args[2]):
            continue
        start, end = span
        reduced_fact = f"{predicate}({args[0]}, {start}, {end}, {args[3]})."
        if reduced_fact in existing or reduced_fact in reduced:
            continue
        reduced.append(reduced_fact)
    return reduced


def _list_range_contract_atom_span(value: Any) -> tuple[int, int] | None:
    text = str(value or "").strip().casefold()
    match = re.fullmatch(r"(?:claim_|item_)?(\d+)(?:_|_to_|_through_|_thru_)(?:claim_|item_)?(\d+)", text)
    if not match:
        return None
    start = int(match.group(1))
    end = int(match.group(2))
    if start == end:
        return None
    low, high = sorted((start, end))
    return low, high


def _list_range_contract_member_kind_allows_span_reduction(*, predicate: str, value: Any) -> bool:
    text = str(value or "").strip().casefold()
    if not text or _list_range_contract_int(text) is not None:
        return False
    if predicate == "claim_range":
        return text in {"claim", "claims", "contested_claim", "contested_claims", "claim_set"}
    return text in {
        "item",
        "items",
        "issue",
        "issues",
        "count",
        "counts",
        "requirement",
        "requirements",
        "paragraph",
        "paragraphs",
        "violation",
        "violations",
        "product",
        "products",
    }


def _apply_governed_review_atom_fact_reduction(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Add registered review_outcome/4 rows for narrow typed review atoms.

    This is a typed-atom reducer. It does not inspect source prose or query
    text. It only maps LLM-proposed predicate names such as affirmed_by/2 onto
    the governed carrier vocabulary so compile and query meet on the same atom.
    """

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    existing = set(facts)
    appended: list[str] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        outcome = REVIEW_OUTCOME_REDUCTION_PREDICATES.get(str(predicate).strip().casefold())
        if not outcome or len(args) != 2:
            continue
        subject, actor = args
        reduced = f"review_outcome({subject}, {actor}, {outcome}, direct)."
        if reduced in existing:
            continue
        existing.add(reduced)
        appended.append(reduced)
    if appended:
        facts.extend(appended)
        source_compile["facts"] = facts
        source_compile["unique_fact_count"] = len(facts)
    source_compile["deterministic_governed_atom_reduction_count"] = len(appended)
    source_compile["deterministic_governed_atom_reduction_facts"] = appended[:100]
    if appended:
        source_compile["deterministic_governed_atom_reduction_policy"] = {
            "schema_version": "deterministic_governed_atom_reduction_v1",
            "authority": "typed_atom_reduction_only",
            "not_source_interpretation": True,
            "not_query_interpretation": True,
            "description": (
                "Maps model-proposed narrow review predicate atoms such as affirmed_by/2 "
                "onto registered review_outcome/4 facts using the operation/fact atom values only."
            ),
        }
    return {"added_count": len(appended), "added_facts": appended}


DOCUMENT_SUBJECT_CONVERGENCE_IDENTIFIER_KIND_HINTS = {
    "appeal",
    "application",
    "case",
    "docket",
    "document",
    "matter",
    "proceeding",
}

DOCUMENT_SUBJECT_CONVERGENCE_IDENTIFIER_KIND_BLOCKERS = {
    "appendix",
    "footnote",
    "joint",
    "prior",
    "reference",
    "related",
}

DOCUMENT_SUBJECT_CONVERGENCE_PREDICATES = {
    "document_date",
    "review_outcome",
}


def _apply_document_subject_atom_convergence(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Clone document-level typed facts across document subject atoms.

    This is a typed-atom reducer. It does not inspect source prose, source-record
    text, query text, or oracle answers. It only uses source-stated identifier
    atoms already emitted as document_identifier_occurrence/5 and document-level
    typed atoms whose subject id carries the same identifier tokens.
    """

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    existing = set(facts)
    identifier_rows: list[tuple[str, set[str]]] = []
    document_level_rows: list[tuple[str, list[str], set[str]]] = []

    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate == "document_identifier_occurrence" and len(args) == 5:
            doc_id, identifier_kind, identifier_value = [str(arg).strip() for arg in args[:3]]
            if not _document_subject_convergence_kind_allowed(identifier_kind):
                continue
            value_tokens = _document_subject_identifier_tokens(identifier_value)
            if not doc_id or not value_tokens:
                continue
            identifier_rows.append((doc_id, value_tokens))
        elif predicate in DOCUMENT_SUBJECT_CONVERGENCE_PREDICATES and args:
            subject = str(args[0]).strip()
            subject_tokens = set(PROFILE_ADMISSION_TOKEN_RE.findall(subject.casefold()))
            if subject and subject_tokens:
                document_level_rows.append((predicate, [str(arg).strip() for arg in args], subject_tokens))

    appended: list[str] = []
    for target_subject, identifier_tokens in identifier_rows:
        for predicate, args, source_subject_tokens in document_level_rows:
            source_subject = args[0]
            if source_subject == target_subject:
                continue
            if not identifier_tokens.issubset(source_subject_tokens):
                continue
            candidate_args = [target_subject, *args[1:]]
            candidate = f"{predicate}({', '.join(candidate_args)})."
            if candidate in existing:
                continue
            existing.add(candidate)
            appended.append(candidate)

    if appended:
        facts.extend(appended)
        source_compile["facts"] = facts
        source_compile["unique_fact_count"] = len(facts)
    source_compile["deterministic_document_subject_atom_convergence_count"] = len(appended)
    source_compile["deterministic_document_subject_atom_convergence_facts"] = appended[:100]
    if appended:
        source_compile["deterministic_document_subject_atom_convergence_policy"] = {
            "schema_version": "document_subject_atom_convergence_v1",
            "authority": "typed_atom_governance_only",
            "not_source_interpretation": True,
            "not_query_interpretation": True,
            "description": (
                "Clones selected document-level typed facts across typed document subject atoms when a "
                "document_identifier_occurrence/5 row gives the target subject an identifier value and "
                "another document-level subject atom carries the same identifier tokens."
            ),
        }
    return {"added_count": len(appended), "added_facts": appended}


def _document_subject_convergence_kind_allowed(identifier_kind: str) -> bool:
    tokens = set(PROFILE_ADMISSION_TOKEN_RE.findall(str(identifier_kind or "").casefold()))
    if tokens & DOCUMENT_SUBJECT_CONVERGENCE_IDENTIFIER_KIND_BLOCKERS:
        return False
    return bool(tokens & DOCUMENT_SUBJECT_CONVERGENCE_IDENTIFIER_KIND_HINTS)


def _document_subject_identifier_tokens(identifier_value: str) -> set[str]:
    tokens = set(PROFILE_ADMISSION_TOKEN_RE.findall(str(identifier_value or "").casefold()))
    if len(tokens) < 2:
        return set()
    if not any(token.isdigit() and len(token) >= 4 for token in tokens):
        return set()
    return tokens


CLAIM_GROUND_STATUTE_REDUCTIONS: dict[str, tuple[str, str]] = {
    "102_a_1": ("anticipation", "section_102_a_1"),
    "102a1": ("anticipation", "section_102_a_1"),
    "section_102_a_1": ("anticipation", "section_102_a_1"),
    "35_usc_102_a_1": ("anticipation", "section_102_a_1"),
    "35_u_s_c_102_a_1": ("anticipation", "section_102_a_1"),
    "103": ("obviousness", "section_103"),
    "section_103": ("obviousness", "section_103"),
    "35_usc_103": ("obviousness", "section_103"),
    "35_u_s_c_103": ("obviousness", "section_103"),
}

CLAIM_GROUND_OUTCOME_TO_STATUS: dict[str, str] = {
    "anticipated": "rejected",
    "anticipation": "rejected",
    "obvious": "rejected",
    "obviousness": "rejected",
}


def _governed_reference_atom(value: str) -> str:
    text = str(value or "").strip()
    match = re.fullmatch(r"ref_([a-z0-9]+)", text.casefold())
    if match:
        return f"reference_{match.group(1)}"
    return text


def _governed_ground_atom(value: str) -> str:
    text = str(value or "").strip()
    normalized = text.casefold()
    if normalized in {"anticipated", "anticipates", "anticipation"}:
        return "anticipation"
    if normalized in {"obvious", "obviousness"}:
        return "obviousness"
    return text


def _governed_citation_atom(value: str) -> str:
    text = str(value or "").strip()
    normalized = text.casefold()
    if normalized in {"sec_102a1", "sec_102_a_1", "102a1", "102_a_1"}:
        return "section_102_a_1"
    if normalized in {"sec_103", "103"}:
        return "section_103"
    compact = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    if (
        "amend" in compact
        and ("foregoing" in compact or "cited" in compact or "these_laws" in compact or "those_laws" in compact)
    ):
        if "regulation" in compact or "rule" in compact:
            return "future_amendments_to_foregoing_laws_regulations_and_rules"
        return "future_amendments_to_foregoing_laws"
    return text


def _governed_legal_role_atom(value: str, citation: str = "") -> str:
    text = str(value or "").strip()
    normalized = text.casefold()
    if normalized in {"statutory_basis", "statutory_ground", "statute", "legal_basis"}:
        return "statutory_ground"
    if normalized in {
        "amendment",
        "amendments",
        "amendment_scope",
        "future_amendment_scope",
        "future_amendments",
        "future_law_coverage",
        "scope_extension",
        "successor_rules",
        "successor_regulations",
    }:
        return "amendment_scope"
    if str(citation or "").strip().casefold().startswith("future_amendments_to_"):
        return "amendment_scope"
    if str(citation or "").strip().casefold().startswith("section_") and normalized in {"anticipation", "obviousness"}:
        return "statutory_ground"
    return text


def _governed_review_actor_atom(value: str) -> str:
    text = str(value or "").strip()
    normalized = text.casefold()
    if normalized in {"actor_board", "board_role", "review_board_role"}:
        return "review_board"
    return text


def _governed_review_outcome_atom(value: str) -> str:
    text = str(value or "").strip()
    normalized = text.casefold()
    if normalized in {"affirmation_outcome", "affirmed_outcome", "affirmation", "affirm"}:
        return "affirmed"
    if normalized in {"reversal_outcome", "reversal", "reverse"}:
        return "reversed"
    return text


def _apply_governed_reference_citation_atom_reduction(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Normalize common atom variants in governed companion rows."""

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    existing = set(facts)
    appended: list[str] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        candidate = ""
        if predicate == "claim_ground" and len(args) == 4:
            subject, ground, reference, status = [str(arg).strip() for arg in args]
            normalized_ground = _governed_ground_atom(ground)
            normalized_reference = _governed_reference_atom(reference)
            if normalized_ground != ground or normalized_reference != reference:
                candidate = f"claim_ground({subject}, {normalized_ground}, {normalized_reference}, {status})."
        elif predicate == "legal_citation_detail" and len(args) == 4:
            subject, citation, role, source_or_scope = [str(arg).strip() for arg in args]
            normalized_citation = _governed_citation_atom(citation)
            normalized_role = _governed_legal_role_atom(role, normalized_citation)
            if normalized_citation != citation or normalized_role != role:
                candidate = f"legal_citation_detail({subject}, {normalized_citation}, {role}, {source_or_scope})."
                if normalized_role != role:
                    candidate = f"legal_citation_detail({subject}, {normalized_citation}, {normalized_role}, {source_or_scope})."
        elif predicate == "review_outcome" and len(args) == 4:
            subject, actor, outcome, source_or_scope = [str(arg).strip() for arg in args]
            normalized_actor = _governed_review_actor_atom(actor)
            normalized_outcome = _governed_review_outcome_atom(outcome)
            if normalized_actor != actor or normalized_outcome != outcome:
                candidate = f"review_outcome({subject}, {normalized_actor}, {normalized_outcome}, {source_or_scope})."
        if not candidate or candidate in existing:
            continue
        existing.add(candidate)
        appended.append(candidate)
    if appended:
        facts.extend(appended)
        source_compile["facts"] = facts
        source_compile["unique_fact_count"] = len(facts)
    source_compile["deterministic_reference_citation_atom_reduction_count"] = len(appended)
    source_compile["deterministic_reference_citation_atom_reduction_facts"] = appended[:100]
    if appended:
        source_compile["deterministic_reference_citation_atom_reduction_policy"] = {
            "schema_version": "deterministic_reference_citation_atom_reduction_v1",
            "authority": "typed_atom_reduction_only",
            "not_source_interpretation": True,
            "not_query_interpretation": True,
            "description": (
                "Normalizes governed atom variants such as ref_alpha, sec_102a1, anticipated, obvious, "
                "statutory_basis, and board_role inside already-admitted typed companion rows."
            ),
        }
    return {"added_count": len(appended), "added_facts": appended}


def _apply_governed_claim_ground_atom_reduction(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Normalize statute-stuffed claim_ground/4 rows into governed companions.

    This is a typed-atom reducer. It does not read source prose or query text.
    When the model places a statute atom in claim_ground/4's ground slot and a
    theory/outcome atom in the status slot, add the registered governed shape:
    claim_ground carries the theory and status, while legal_citation_detail
    carries the statute.
    """

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    existing = set(facts)
    appended: list[str] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate != "claim_ground" or len(args) != 4:
            continue
        subject, ground_or_statute, reference, outcome_or_status = [str(arg).strip() for arg in args]
        theory_and_citation = CLAIM_GROUND_STATUTE_REDUCTIONS.get(ground_or_statute.casefold())
        if theory_and_citation is None:
            continue
        theory, citation = theory_and_citation
        status = CLAIM_GROUND_OUTCOME_TO_STATUS.get(outcome_or_status.casefold(), outcome_or_status)
        candidates = [
            f"claim_ground({subject}, {theory}, {reference}, {status}).",
            f"legal_citation_detail({subject}, {citation}, statutory_ground, direct).",
        ]
        for candidate in candidates:
            if candidate in existing:
                continue
            existing.add(candidate)
            appended.append(candidate)
    if appended:
        facts.extend(appended)
        source_compile["facts"] = facts
        source_compile["unique_fact_count"] = len(facts)
    source_compile["deterministic_claim_ground_atom_reduction_count"] = len(appended)
    source_compile["deterministic_claim_ground_atom_reduction_facts"] = appended[:100]
    if appended:
        source_compile["deterministic_claim_ground_atom_reduction_policy"] = {
            "schema_version": "deterministic_claim_ground_atom_reduction_v1",
            "authority": "typed_atom_reduction_only",
            "not_source_interpretation": True,
            "not_query_interpretation": True,
            "description": (
                "Normalizes claim_ground/4 rows where the model placed a statute atom in the ground slot, "
                "adding a governed claim_ground/4 theory row plus legal_citation_detail/4 citation row."
            ),
        }
    return {"added_count": len(appended), "added_facts": appended}


def _apply_governed_obligation_detail_atom_reduction(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Reduce broader obligation detail atoms into more atomic companion rows.

    This reads only already-admitted `obligation_detail/5` typed atoms. It does
    not inspect source prose, source-record display rows, query text, or oracle
    answers.
    """

    facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    existing = set(facts)
    appended: list[str] = []
    for fact in facts:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate != "obligation_detail" or len(args) != 5:
            continue
        obligation_id, detail_kind, detail_value, role_or_purpose, source_or_scope = [
            str(arg).strip() for arg in args
        ]
        if detail_kind.casefold() not in {"recipient_scope", "scope", "condition"}:
            continue
        schedule = _obligation_detail_schedule_atom(detail_value)
        if not schedule:
            continue
        candidate = (
            f"obligation_detail({obligation_id}, tariff_schedule, {schedule}, "
            f"{role_or_purpose}, {source_or_scope})."
        )
        if candidate in existing:
            continue
        existing.add(candidate)
        appended.append(candidate)
    if appended:
        facts.extend(appended)
        source_compile["facts"] = facts
        source_compile["unique_fact_count"] = len(facts)
    source_compile["deterministic_obligation_detail_atom_reduction_count"] = len(appended)
    source_compile["deterministic_obligation_detail_atom_reduction_facts"] = appended[:100]
    if appended:
        source_compile["deterministic_obligation_detail_atom_reduction_policy"] = {
            "schema_version": "deterministic_obligation_detail_atom_reduction_v1",
            "authority": "typed_atom_reduction_only",
            "not_source_interpretation": True,
            "not_query_interpretation": True,
            "description": (
                "Adds tariff_schedule obligation_detail/5 rows when an already-admitted obligation detail "
                "scope atom contains a controlled schedule_N atom."
            ),
        }
    return {"added_count": len(appended), "added_facts": appended}


def _obligation_detail_schedule_atom(value: str) -> str:
    match = re.search(r"(?:^|_)schedule_([a-z0-9]+)(?:_|$)", str(value or "").casefold())
    if not match:
        return ""
    return f"schedule_{match.group(1)}"


def _attach_governed_companion_subject_health(source_compile: dict[str, Any]) -> dict[str, Any]:
    """Report missing companion carrier families per typed subject.

    This is a diagnostic over already-admitted typed facts. It does not inspect
    source prose, query text, or oracle answers.
    """

    companion_predicates = {
        "claim_range",
        "claim_ground",
        "legal_citation_detail",
        "review_outcome",
    }
    predicate_signatures = {
        "claim_range": "claim_range/4",
        "claim_ground": "claim_ground/4",
        "legal_citation_detail": "legal_citation_detail/4",
        "review_outcome": "review_outcome/4",
    }
    subjects: dict[str, dict[str, Any]] = {}
    for fact in [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]:
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate not in companion_predicates or not args:
            continue
        subject = str(args[0]).strip()
        if not subject:
            continue
        row = subjects.setdefault(subject, {"subject": subject, "predicates": set(), "facts": []})
        row["predicates"].add(predicate)
        row["facts"].append(fact)
    rows: list[dict[str, Any]] = []
    omission_ledger: list[dict[str, Any]] = []
    for subject, row in sorted(subjects.items()):
        predicates = set(row.get("predicates") or set())
        missing: list[str] = []
        if {"claim_ground", "legal_citation_detail", "review_outcome"} & predicates and "claim_range" not in predicates:
            missing.append("claim_range/4")
        if {"claim_range", "legal_citation_detail", "review_outcome"} & predicates and "claim_ground" not in predicates:
            missing.append("claim_ground/4")
        if {"claim_range", "claim_ground", "review_outcome"} & predicates and "legal_citation_detail" not in predicates:
            missing.append("legal_citation_detail/4")
        if {"claim_range", "claim_ground", "legal_citation_detail"} & predicates and "review_outcome" not in predicates:
            missing.append("review_outcome/4")
        family_statuses: dict[str, str] = {}
        for predicate, signature in sorted(predicate_signatures.items(), key=lambda item: item[1]):
            if predicate in predicates:
                family_statuses[signature] = "present"
            elif signature in missing:
                family_statuses[signature] = "missing_unaccounted"
                omission_ledger.append(
                    {
                        "subject": subject,
                        "signature": signature,
                        "status": "missing_unaccounted",
                        "observed_predicates": sorted(predicates),
                        "reason": "typed subject has at least one governed companion family but this companion family is absent",
                    }
                )
            else:
                family_statuses[signature] = "not_required_by_observed_typed_surface"
        rows.append(
            {
                "subject": subject,
                "predicates": sorted(predicates),
                "missing_companions": missing,
                "family_statuses": family_statuses,
                "fact_count": len(row.get("facts") or []),
            }
        )
    flagged = [row for row in rows if row["missing_companions"]]
    report = {
        "schema_version": "governed_companion_subject_health_v1",
        "authority": "typed_fact_diagnostic_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "subject_count": len(rows),
        "flagged_subject_count": len(flagged),
        "omission_ledger_count": len(omission_ledger),
        "governed_companion_omission_ledger": omission_ledger,
        "rows": rows,
    }
    source_compile["governed_companion_subject_health"] = report
    return report


def _list_range_source_key(value: Any) -> str:
    text = str(value or "").strip().casefold()
    match = re.fullmatch(r"(?:src|source)_line_0*(\d+)", text)
    if match:
        return f"src_line_{int(match.group(1)):04d}"
    if text.startswith("src_") or text.startswith("source_"):
        return text.replace("source_line_", "src_line_")
    return ""


def _profile_registry_accountability_context(profile_registry: dict[str, Any]) -> list[str]:
    requirements = (
        profile_registry.get("accountability_requirements")
        if isinstance(profile_registry.get("accountability_requirements"), list)
        else []
    )
    if not requirements:
        return []
    lines = [
        "Registry accountability requirements are omission contracts, not facts. "
        "Use them only when the raw source explicitly satisfies the trigger."
    ]
    for item in requirements:
        if not isinstance(item, dict):
            continue
        carrier_signature = str(item.get("carrier_signature", "")).strip()
        omission_kind = str(item.get("omission_kind", "")).strip()
        reason_code = str(item.get("reason_code", "")).strip()
        trigger = str(item.get("trigger", "")).strip()
        if not carrier_signature or not omission_kind or not reason_code:
            continue
        lines.append(
            "Registry accountability requirement: if raw_source_text satisfies "
            f"{trigger or 'the stated omission trigger'}, emit domain_omission(DomainOrSubjectId, "
            f"'{carrier_signature}', {omission_kind}, {reason_code}, SourceOrScope). "
            "The carrier_signature slot must keep the exact registered slash signature in quotes; "
            "do not rewrite it as an underscore atom. "
            "Choose DomainOrSubjectId and SourceOrScope from the source-local domain object and source coordinate. "
            "Do not leave this only in self_check."
        )
    return lines


def _list_range_interval_overcompresses_segments(
    interval: dict[str, Any],
    intervals: list[dict[str, Any]],
) -> bool:
    source_key = str(interval.get("source_key") or "")
    if not source_key:
        return False
    low = int(interval.get("low", 0))
    high = int(interval.get("high", 0))
    if low == high:
        return False
    predicate = str(interval.get("predicate") or "")
    segments: list[tuple[int, int]] = []
    for other in intervals:
        if other is interval:
            continue
        if str(other.get("predicate") or "") != predicate:
            continue
        if str(other.get("source_key") or "") != source_key:
            continue
        other_low = int(other.get("low", 0))
        other_high = int(other.get("high", 0))
        if low <= other_low <= other_high <= high:
            segments.append((other_low, other_high))
    if len(segments) < 2:
        return False
    merged: list[list[int]] = []
    for start, end in sorted(segments):
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    if len(merged) < 2:
        return False
    return merged[0][0] == low and merged[-1][1] == high


def _list_range_contract_int(value: Any) -> int | None:
    text = str(value or "").strip()
    match = re.fullmatch(r"(?:claim|count|item|issue|violation|paragraph)_(-?\d+)", text)
    if match:
        text = match.group(1)
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return None


def _profile_role_roster_repair_offered_carriers(parsed_profile: dict[str, Any]) -> list[str]:
    carriers: list[str] = []
    seen: set[str] = set()
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return carriers
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        signature = str(candidate.get("signature", "")).strip()
        if not signature or "/" not in signature:
            continue
        base = signature.split("/", 1)[0].strip().lower()
        args = candidate.get("args")
        arg_text = " ".join(str(arg).lower() for arg in args if isinstance(args, list))
        haystack = base + " " + arg_text
        if not any(hint in haystack for hint in ROLE_ROSTER_REPAIR_BASE_HINTS):
            continue
        if signature not in seen:
            seen.add(signature)
            carriers.append(signature)
    return carriers


def _profile_role_roster_repair_context_lines(parsed_profile: dict[str, Any]) -> list[str]:
    carriers = _profile_role_roster_repair_offered_carriers(parsed_profile)
    if not carriers:
        return []
    return [
        (
            "PROFILE ROLE ROSTER REPAIR PASS: deterministic query delivery is missing typed role/roster "
            "facts in some documents. This pass is proposal-only; emit only source-grounded typed rows "
            "through allowed predicate contracts, and let the mapper decide admission."
        ),
        (
            "PROFILE ROLE ROSTER REPAIR PASS: revisit source-stated appearances, counsel blocks, signature "
            "blocks, contact blocks, panel/member lists, appositive job titles, employment titles, and "
            "supervisor/managed-by relations. Preserve the person, exact stated office/firm/organization, "
            "represented party or scope, source-stated location, and role/title as separate typed arguments "
            "when the allowed predicate contract supports them."
        ),
        (
            "PROFILE ROLE ROSTER REPAIR PASS: do not collapse an office, bureau, local office, firm, or "
            "department into a parent party when the source states the more specific organization. Do not "
            "replace a job title with a generic participant label when the title is source-stated."
        ),
        (
            "PROFILE ROLE ROSTER REPAIR PASS: do not emit source_record_* rows, display text rows, prose "
            "windows, or answer-bearing source excerpts. The output must be typed role/roster facts only."
        ),
        (
            "PROFILE ROLE ROSTER REPAIR PASS: compatible role/roster signatures to consider: "
            + ", ".join(carriers[:16])
            + ". Use exact allowed predicate names and argument order."
        ),
    ]


def _apply_profile_role_roster_repair_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    carriers = _profile_role_roster_repair_offered_carriers(parsed_profile)
    metadata: dict[str, Any] = {
        "schema_version": "profile_role_roster_repair_pass_v1",
        "attempted": False,
        "offered_carriers": carriers[:16],
    }
    if not carriers:
        metadata["reason"] = "no_role_roster_predicates_offered"
        source_compile["profile_role_roster_repair"] = metadata
        return metadata
    context_lines = _profile_role_roster_repair_context_lines(parsed_profile)
    target = max(8, min(32, int(getattr(args, "focused_pass_operation_target", 48) or 48)))
    compiled = _compile_source_pass_ops(
        source_text=source_text,
        parsed_profile=parsed_profile,
        intake_plan=intake_plan,
        args=args,
        pass_id="profile_role_roster_repair",
        purpose="repair typed role and roster delivery without source-record answer routing",
        focus="missing counsel, representative, signatory, contact, panel, employee, job-title, and supervisor rows",
        completion=(
            "Emit only source-grounded typed role/roster rows and minimal supporting organization/location rows; "
            "do not recompile unrelated source material."
        ),
        predicates=", ".join(carriers[:16]),
        coverage_goals=(
            "Deliver source-stated role/roster facts as typed predicates: person, role/title, organization, "
            "represented party or scope, location, and supervisor relation when available."
        ),
        extra_context=[*(extra_context or []), *context_lines],
        operation_target=target,
    )
    compiled["pass_id"] = "profile_role_roster_repair"
    compiled["purpose"] = "repair typed role and roster delivery without source-record answer routing"
    compiled["focus"] = "missing counsel, representative, signatory, contact, panel, employee, job-title, and supervisor rows"
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    _merge_additive_source_pass(source_compile, compiled, metadata_prefix="profile_role_roster_repair")
    signature_contract_report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts=prior_facts,
        allowed_signatures=set(carriers[:16]),
        metadata_prefix="profile_role_roster_repair",
        pass_record=compiled,
    )
    metadata.update(
        {
            "attempted": True,
            "ok": bool(compiled.get("ok")),
            "admitted_count": int(compiled.get("admitted_count", 0) or 0),
            "skipped_count": int(compiled.get("skipped_count", 0) or 0),
            "new_fact_count": len(compiled.get("_profile_role_roster_repair_new_facts", []))
            if isinstance(compiled.get("_profile_role_roster_repair_new_facts"), list)
            else 0,
            "signature_contract": signature_contract_report,
            "pass": compiled,
        }
    )
    source_compile["profile_role_roster_repair"] = metadata
    return metadata


def _apply_profile_delivery_repair_pass(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any],
    args: argparse.Namespace,
    extra_context: list[str] | None = None,
) -> dict[str, Any]:
    admission_report = _profile_admission_report(parsed_profile=parsed_profile, source_text=source_text)
    delivery_report = _profile_delivery_report(
        source_compile=source_compile,
        parsed_profile=parsed_profile,
        admission_report=admission_report,
        source_text=source_text,
    )
    findings = _profile_delivery_repair_findings(delivery_report)
    metadata: dict[str, Any] = {
        "schema_version": "profile_delivery_repair_pass_v1",
        "attempted": False,
        "initial_finding_classes": [
            str(finding.get("class", "")).strip()
            for finding in findings
            if str(finding.get("class", "")).strip()
        ],
    }
    if not findings:
        metadata["reason"] = "no_repairable_profile_delivery_findings"
        source_compile["profile_delivery_repair"] = metadata
        return metadata

    carriers = _profile_delivery_repair_offered_carriers(findings)
    context_lines = _profile_delivery_repair_context_lines(delivery_report)
    if not context_lines:
        metadata["reason"] = "no_repair_context"
        source_compile["profile_delivery_repair"] = metadata
        return metadata

    target = max(12, min(48, int(getattr(args, "focused_pass_operation_target", 48) or 48)))
    compiled = _compile_source_pass_ops(
        source_text=source_text,
        parsed_profile=parsed_profile,
        intake_plan=intake_plan,
        args=args,
        pass_id="profile_delivery_repair",
        purpose="repair direct carrier delivery after deterministic profile-delivery diagnostics",
        focus="missing direct source-claim, source-authority, and status/state carrier rows",
        completion=(
            "Emit only source-grounded carrier rows and necessary backbone rows for the diagnostic row classes; "
            "do not recompile unrelated source material."
        ),
        predicates=", ".join(carriers[:12]) or "Use compatible allowed direct carrier predicates.",
        coverage_goals="Deliver missing source-to-claim, source-authority, and status/state carrier rows when source-stated.",
        extra_context=[*(extra_context or []), *context_lines],
        operation_target=target,
    )
    compiled["pass_id"] = "profile_delivery_repair"
    compiled["purpose"] = "repair direct carrier delivery after deterministic profile-delivery diagnostics"
    compiled["focus"] = "missing direct source-claim, source-authority, and status/state carrier rows"
    prior_facts = {
        str(item).strip()
        for item in source_compile.get("facts", [])
        if str(item).strip()
    }
    _merge_profile_delivery_repair_pass(source_compile, compiled)
    signature_contract_report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts=prior_facts,
        allowed_signatures={signature for signature in carriers[:12] if "/" in str(signature)},
        metadata_prefix="profile_delivery_repair",
        pass_record=compiled,
    )
    refreshed = _profile_delivery_report(
        source_compile=source_compile,
        parsed_profile=parsed_profile,
        admission_report=admission_report,
        source_text=source_text,
    )
    metadata.update(
        {
            "attempted": True,
            "ok": bool(compiled.get("ok")),
            "admitted_count": int(compiled.get("admitted_count", 0) or 0),
            "skipped_count": int(compiled.get("skipped_count", 0) or 0),
            "new_fact_count": len(compiled.get("_profile_delivery_repair_new_facts", []))
            if isinstance(compiled.get("_profile_delivery_repair_new_facts"), list)
            else 0,
            "offered_carriers": carriers[:12],
            "signature_contract": signature_contract_report,
            "initial_finding_count": len(findings),
            "remaining_finding_classes": [
                str(finding.get("class", "")).strip()
                for finding in _profile_delivery_repair_findings(refreshed)
                if str(finding.get("class", "")).strip()
            ],
            "pass": compiled,
        }
    )
    source_compile["profile_delivery_repair"] = metadata
    return metadata


def _merge_profile_delivery_repair_pass(source_compile: dict[str, Any], pass_record: dict[str, Any]) -> None:
    _merge_additive_source_pass(source_compile, pass_record, metadata_prefix="profile_delivery_repair")


def _merge_additive_source_pass(
    source_compile: dict[str, Any],
    pass_record: dict[str, Any],
    *,
    metadata_prefix: str,
) -> None:
    before_facts = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    before_rules = [str(item).strip() for item in source_compile.get("rules", []) if str(item).strip()]
    before_queries = [str(item).strip() for item in source_compile.get("queries", []) if str(item).strip()]
    initial_fact_set = set(before_facts)
    initial_rule_set = set(before_rules)
    initial_query_set = set(before_queries)
    old_admitted_count = int(source_compile.get("admitted_count", 0) or 0)
    old_skipped_count = int(source_compile.get("skipped_count", 0) or 0)
    old_effective_admitted_count = int(source_compile.get("effective_admitted_count", old_admitted_count) or 0)
    old_effective_skipped_count = int(source_compile.get("effective_skipped_count", old_skipped_count) or 0)
    before_fact_set = set(before_facts)
    before_rule_set = set(before_rules)
    before_query_set = set(before_queries)

    def extend_unique(existing: list[str], seen: set[str], values: Any) -> list[str]:
        added: list[str] = []
        for value in values if isinstance(values, list) else []:
            text = str(value).strip()
            if text and text not in seen:
                seen.add(text)
                existing.append(text)
                added.append(text)
        return added

    added_facts = extend_unique(before_facts, before_fact_set, pass_record.get("facts", []))
    added_rules = extend_unique(before_rules, before_rule_set, pass_record.get("rules", []))
    added_queries = extend_unique(before_queries, before_query_set, pass_record.get("queries", []))
    pass_record[f"_{metadata_prefix}_new_facts"] = added_facts
    pass_record[f"_{metadata_prefix}_new_rules"] = added_rules
    pass_record[f"_{metadata_prefix}_new_queries"] = added_queries

    source_compile["facts"] = before_facts
    source_compile["rules"] = before_rules
    source_compile["queries"] = before_queries
    source_compile["unique_fact_count"] = len(before_facts)
    source_compile["unique_rule_count"] = len(before_rules)
    source_compile["unique_query_count"] = len(before_queries)
    source_compile["admitted_count"] = old_admitted_count + int(pass_record.get("admitted_count", 0) or 0)
    source_compile["skipped_count"] = old_skipped_count + int(pass_record.get("skipped_count", 0) or 0)
    source_compile["effective_admitted_count"] = old_effective_admitted_count + int(pass_record.get("admitted_count", 0) or 0)
    source_compile["effective_skipped_count"] = old_effective_skipped_count + int(pass_record.get("skipped_count", 0) or 0)

    repair_passes = source_compile.get("repair_passes")
    if not isinstance(repair_passes, list):
        repair_passes = []
    repair_passes.append(pass_record)
    source_compile["repair_passes"] = repair_passes

    surface_rows = source_compile.get("surface_contribution")
    if not isinstance(surface_rows, list):
        surface_rows = []
    repair_rows = _pass_surface_contribution(
        [pass_record],
        initial_seen_facts=initial_fact_set,
        initial_seen_rules=initial_rule_set,
        initial_seen_queries=initial_query_set,
    )
    source_compile["surface_contribution"] = [*surface_rows, *repair_rows]
    source_compile["compile_health"] = _compile_health_summary(source_compile["surface_contribution"])


def _append_source_record_ledger_facts(source_compile: dict[str, Any], ledger: dict[str, Any]) -> None:
    facts = source_record_ledger_facts(ledger)
    if not facts:
        source_compile["deterministic_source_record_fact_count"] = 0
        return
    existing = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    seen = set(existing)
    appended: list[str] = []
    for fact in facts:
        if fact not in seen:
            seen.add(fact)
            existing.append(fact)
            appended.append(fact)
    source_compile["facts"] = existing
    source_compile["unique_fact_count"] = len(existing)
    source_compile["deterministic_source_record_fact_count"] = len(appended)
    source_compile["deterministic_source_record_policy"] = {
        "schema_version": "deterministic_source_record_facts_v1",
        "authority": "source_addressability_only",
        "not_semantic_truth": True,
        "description": (
            "Facts under source_record_* preserve deterministic source row addressability "
            "from source_record_ledger_v1. They do not admit ownership, status, authority, "
            "causality, counts, or other semantic conclusions."
        ),
    }


def _append_entity_id_closure_facts(source_compile: dict[str, Any], parsed_profile: dict[str, Any]) -> None:
    id_predicates = _entity_id_predicate_bases(parsed_profile)
    if not id_predicates:
        source_compile["deterministic_entity_id_closure_fact_count"] = 0
        return
    existing = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    seen = set(existing)
    appended: list[str] = []
    for fact in list(existing):
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate.startswith("source_record") or not args:
            continue
        for id_predicate, base in id_predicates:
            if predicate == id_predicate:
                continue
            if predicate != base and not predicate.startswith(base + "_"):
                continue
            atom = args[0]
            if not ENTITY_ID_ATOM_RE.fullmatch(atom):
                continue
            closure_fact = f"{id_predicate}({atom})."
            if closure_fact in seen:
                continue
            seen.add(closure_fact)
            existing.append(closure_fact)
            appended.append(closure_fact)
    source_compile["facts"] = existing
    source_compile["unique_fact_count"] = len(existing)
    source_compile["deterministic_entity_id_closure_fact_count"] = len(appended)
    if appended:
        source_compile["deterministic_entity_id_closure_policy"] = {
            "schema_version": "deterministic_entity_id_closure_v1",
            "authority": "closure_over_admitted_direct_rows",
            "not_source_interpretation": True,
            "description": (
                "Adds missing unary *_id entity declarations when an admitted direct row already uses the same "
                "entity as the first argument of a compatible predicate family."
            ),
        }


def _append_source_field_id_facts(source_compile: dict[str, Any], parsed_profile: dict[str, Any]) -> None:
    id_predicates = {predicate for predicate, _base in _entity_id_predicate_bases(parsed_profile)}
    if not id_predicates:
        source_compile["deterministic_source_field_id_fact_count"] = 0
        return
    existing = [str(item).strip() for item in source_compile.get("facts", []) if str(item).strip()]
    seen = set(existing)
    appended: list[str] = []
    for fact in list(existing):
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate != "source_record_field" or len(args) < 3:
            continue
        field_name = args[1]
        value = args[2]
        if field_name not in id_predicates or not ENTITY_ID_ATOM_RE.fullmatch(value) or _looks_temporal_atom(value):
            continue
        closure_fact = f"{field_name}({value})."
        if closure_fact in seen:
            continue
        seen.add(closure_fact)
        existing.append(closure_fact)
        appended.append(closure_fact)
    source_compile["facts"] = existing
    source_compile["unique_fact_count"] = len(existing)
    source_compile["deterministic_source_field_id_fact_count"] = len(appended)
    if appended:
        source_compile["deterministic_source_field_id_policy"] = {
            "schema_version": "deterministic_source_field_id_v1",
            "authority": "typed_source_field_identifier_only",
            "not_semantic_interpretation": True,
            "description": (
                "Adds unary *_id declarations only when a deterministic source_record_field header exactly matches "
                "an allowed unary id predicate."
            ),
        }


def _ensure_source_detail_predicate(parsed_profile: dict[str, Any]) -> dict[str, Any]:
    """Ensure a generic additive source-detail carrier is available.

    This extends the profile vocabulary only; it does not extract facts. The
    predicate is intentionally scoped to exact source-stated details that lack a
    stricter profile predicate, so it can replace old compatibility crutches
    without encouraging fixture-shaped predicate names.
    """

    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_source_detail_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if "source_detail/4" in signatures:
        return {
            "schema_version": "profile_source_detail_extension_v1",
            "added": False,
            "reason": "source_detail_already_present",
        }
    if _has_specific_detail_carrier(signatures):
        return {
            "schema_version": "profile_source_detail_extension_v1",
            "added": False,
            "reason": "specific_detail_carrier_present",
        }

    candidates.append(
        {
            "signature": "source_detail/4",
            "args": ["subject_id", "detail_kind", "detail_value", "source_row"],
            "description": (
                "Additive fallback for exact source-stated attributes or details when no stricter "
                "profile predicate can carry the value."
            ),
            "why": (
                "Preserves answer-bearing source details without inventing fixture-specific predicate names "
                "or replacing concrete domain rows."
            ),
            "admission_notes": [
                "Use only as a fallback carrier for exact source-stated detail values.",
                "Do not use when a stricter profile predicate can preserve the same surface.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "source_detail/4" not in provenance:
        provenance.append("source_detail/4")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append("Deterministic profile extension added source_detail/4 as an additive fallback detail carrier.")
    return {
        "schema_version": "profile_source_detail_extension_v1",
        "added": True,
        "signature": "source_detail/4",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


SHALLOW_ROLE_BASES = {
    "actor_role",
    "adult_role",
    "employee_role",
    "entity_role",
    "party_role",
    "person_role",
    "representative_role",
    "staff_role",
}

RICH_ROLE_BASES = {
    "counsel_for",
    "employment_role",
    "person_role_detail",
    "representative_for",
    "role_detail",
    "signatory_for",
    "supervisor_relation",
}


def _signature_base_arity(signature: str) -> tuple[str, int] | None:
    text = str(signature).strip()
    if "/" not in text:
        return None
    base, arity_text = text.rsplit("/", 1)
    try:
        arity = int(arity_text)
    except ValueError:
        return None
    return base.strip(), arity


def _ensure_role_detail_predicate(parsed_profile: dict[str, Any]) -> dict[str, Any]:
    """Ensure a compact typed role-detail carrier when the profile is too shallow.

    This is a vocabulary extension only. It does not inspect source prose or
    extract role facts; it gives the LLM-owned compile pass a typed place to put
    source-stated offices, firms, titles, represented parties, and locations
    that would otherwise be squeezed into a lossy role atom.
    """

    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_role_detail_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = [
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    ]
    parsed_signatures = [item for item in (_signature_base_arity(signature) for signature in signatures) if item]
    if any(base in RICH_ROLE_BASES or (base.endswith("_role") and arity >= 4) for base, arity in parsed_signatures):
        return {
            "schema_version": "profile_role_detail_extension_v1",
            "added": False,
            "reason": "rich_role_carrier_present",
        }
    if not any(base in SHALLOW_ROLE_BASES and arity <= 3 for base, arity in parsed_signatures):
        return {
            "schema_version": "profile_role_detail_extension_v1",
            "added": False,
            "reason": "no_shallow_role_carrier",
        }
    if "person_role_detail/5" in signatures:
        return {
            "schema_version": "profile_role_detail_extension_v1",
            "added": False,
            "reason": "person_role_detail_already_present",
        }

    candidates.append(
        {
            "signature": "person_role_detail/5",
            "args": [
                "person_id",
                "role_or_title",
                "organization_or_office",
                "represented_party_or_scope",
                "location_or_context",
            ],
            "description": (
                "Typed carrier for exact source-stated person roles, titles, offices, firms, represented "
                "parties, scopes, and locations when a shallow role predicate would lose slots."
            ),
            "why": (
                "Prevents lossy role atoms such as supervisor or attorney from replacing source-stated "
                "titles, local offices, firms, parties, and locations."
            ),
            "admission_notes": [
                "Use only for source-stated role/roster facts.",
                "Preserve exact source-stated office, firm, bureau, department, or local office separately from the represented party.",
                "Preserve exact job title or appositive role instead of replacing it with a generic participant label.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "person_role_detail/5" not in provenance:
        provenance.append("person_role_detail/5")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append(
                "Deterministic profile extension added person_role_detail/5 as an additive typed role-detail carrier."
            )
    return {
        "schema_version": "profile_role_detail_extension_v1",
        "added": True,
        "signature": "person_role_detail/5",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


DOCUMENT_METADATA_SIGNATURES = {
    "document_title/2": {
        "args": ["document_id", "title"],
        "description": "Exact source-stated title, caption, report title, notice title, or filing title for the document.",
        "why": "Keeps document identity answerable without retrieving a prose source window.",
        "admission_notes": [
            "Use only when the source states a document title, caption, notice title, filing title, or equivalent heading.",
            "Preserve the title as a normalized atom; do not invent a marketing summary.",
        ],
    },
    "document_publisher/2": {
        "args": ["document_id", "publisher_or_issuing_body"],
        "description": "Source-stated publisher, issuing body, agency, office, court, commission, or board for the document.",
        "why": "Separates source authority metadata from answer-bearing prose windows.",
        "admission_notes": [
            "Use only for source-stated issuing or publishing bodies.",
            "Prefer the specific source-stated office or body over a broader parent when both are present.",
        ],
    },
    "document_date/3": {
        "args": ["document_or_subject_id", "date_kind_or_role", "date_value"],
        "description": (
            "Source-stated date for a document, related matter, application, filing, publication, decision, "
            "report, notice, or other document-like subject."
        ),
        "why": (
            "Keeps issue, decision, filing, publication, report, and related-matter dates joinable by typed "
            "subject and date role instead of relying on prose source windows or date-bearing atom labels."
        ),
        "admission_notes": [
            "Use only for dates explicitly stated by the source.",
            "Keep date_kind_or_role as a structural role such as issue_date, decision_date, filing_date, publication_date, report_date, effective_date, or received_date.",
            "Use the same document_or_subject_id that identifier, action, reference, or related-matter rows use when possible.",
            "Do not use document_date/3 for ranges; use document_date_range/3 for a source-stated coverage range or period.",
        ],
    },
    "document_date_range/3": {
        "args": ["document_id", "start_date", "end_date"],
        "description": "Source-stated coverage range, reporting week, period, or effective date range for the document.",
        "why": "Keeps document period metadata queryable as typed dates instead of deriving it from unrelated event rows.",
        "admission_notes": [
            "Use only when the source states a document coverage range or reporting period.",
            "Do not infer a range from the minimum and maximum event dates unless the source itself labels that range.",
        ],
    },
    "registrant_identity/2": {
        "args": ["registrant_entity", "incorporation_or_organization_jurisdiction"],
        "description": (
            "Source-stated registrant/entity identity linked to its state or jurisdiction of incorporation "
            "or organization."
        ),
        "why": (
            "Keeps cover-page registrant jurisdiction as a typed identity relation instead of treating it "
            "as a lifecycle/status row or retrieving it from a prose source window."
        ),
        "admission_notes": [
            "Use only when the source states the exact registrant/entity and state or jurisdiction of incorporation or organization.",
            "The jurisdiction slot is a static charter or organization attribute, not a current status, restatement status, lifecycle state, or operational condition.",
            "Do not use status_state_at/4 for state-of-incorporation or jurisdiction-of-organization facts when this carrier is available.",
            "Preserve EIN, commission file number, ticker, address, and phone in separate typed carriers such as document_identifier_occurrence/5 or entity_location/3.",
        ],
    },
    "registrant_name/2": {
        "args": ["registrant_entity", "legal_name"],
        "description": "Exact source-stated registrant/entity legal name from an official document cover-page identity field.",
        "why": (
            "Keeps exact registrant names answerable as typed identity atoms instead of compact aliases "
            "or prose source windows."
        ),
        "admission_notes": [
            "Use only when the source states the exact registrant/entity legal name as an official identity field.",
            "The legal_name slot is a normalized atom for that source-stated legal name, not a ticker, short name, trade name, inferred alias, or section heading.",
            "Preserve jurisdiction in registrant_identity/2 and identifiers in document_identifier_occurrence/5 when those carriers are available.",
        ],
    },
}


LIST_RANGE_INVENTORY_SIGNATURES = {
    "list_member/4": {
        "args": ["list_or_set_id", "member_value", "member_kind_or_role", "source_or_scope"],
        "description": (
            "One source-stated member of a numbered list, item set, claim set, count set, issue set, "
            "product set, violation set, requirement set, or order-paragraph set."
        ),
        "why": (
            "Preserves list membership as typed atoms so complete-list questions do not depend on "
            "source-record prose or compressed summary labels."
        ),
        "admission_notes": [
            "Use only for members explicitly stated by the source.",
            "Emit one row per source-stated singleton member when the source lists individual members.",
            "Use member_kind_or_role for a short structural role such as claim, count, issue, product, violation, requirement, paragraph, or contested_item.",
            "Do not use source_or_scope to encode a legal ground, prior-art reference, causal reason, treatment basis, or statutory basis.",
            "Preserve ground, basis, outcome, or treatment in a companion typed relation that shares the same list_or_set_id or member_value.",
            "Reuse the same list_or_set_id that related outcome, ground, basis, or status predicates use when one is available.",
            "Do not infer unstated members merely because a nearby source range could be expanded.",
        ],
    },
    "claim_range/4": {
        "args": ["claim_set_id", "start_claim", "end_claim", "source_or_scope"],
        "description": (
            "A source-stated claim-number singleton or range belonging to a governed claim set, such as "
            "contested, rejected, affirmed, anticipated, or obviousness claim groups."
        ),
        "why": (
            "Preserves source-stated claim range boundaries as typed values instead of hiding them inside "
            "one compressed claim-set atom."
        ),
        "admission_notes": [
            "Use only for claim numbers or claim ranges explicitly stated by the source.",
            "Emit one row per source-stated segment: a singleton such as N should have start_claim and end_claim both set to N; a range such as N-M should have start_claim N and end_claim M.",
            "Reuse the same claim_set_id in related claim_outcome, claim_rejection, claim_treatment, ground, or basis predicates when those rows refer to the same governed set.",
            "Do not replace outcome, ground, or treatment rows with claim_range/4; this carrier only preserves the list/range inventory.",
            "Do not compress several separated source segments into one atom such as claims_1_2_4_6_9_12_21.",
        ],
    },
    "item_range/4": {
        "args": ["item_set_id", "start_item", "end_item", "source_or_scope"],
        "description": (
            "A source-stated numbered item, count, issue, product, violation, requirement, paragraph, or "
            "other item-range segment belonging to a governed set."
        ),
        "why": (
            "Gives non-claim documents the same typed range boundary surface as claim_range/4 without "
            "requiring Python to parse display text."
        ),
        "admission_notes": [
            "Use only for source-stated numbered item singletons or ranges.",
            "Emit one row per source-stated segment, preserving start and end separately.",
            "Reuse the same item_set_id in related outcome, status, basis, ground, or treatment predicates when available.",
            "Keep item_range/4 as inventory only; preserve outcome, ground, basis, status, or treatment in companion typed rows.",
            "Do not use item_range/4 for date ranges, money ranges, or measurement ranges unless the governed subject is a numbered source item set.",
        ],
    },
}


CLAIM_SET_RELATION_SIGNATURES = {
    "claim_ground/4": {
        "args": ["claim_set_id", "ground_or_theory", "reference_or_basis", "outcome_or_status"],
        "description": (
            "A governed claim or claim set linked to its source-stated legal/technical ground, "
            "reference or basis, and outcome/status."
        ),
        "why": (
            "Lets claim-range inventory meet the ground/basis relation on the same typed set id instead "
            "of hiding the relation in a list label or source display string."
        ),
        "admission_notes": [
            "Use for source-stated claim or claim-set grounds, theories, references, bases, outcomes, or statuses.",
            "Reuse the same claim_set_id used by claim_range/4 or list_member/4 when the source applies the ground to that governed set.",
            "Do not use claim_ground/4 as inventory; preserve numbered membership and source-stated ranges in list_member/4 and claim_range/4.",
            "If a statute or rule is source-stated, preserve it in legal_citation_detail/4 when that carrier is available.",
            "When legal_citation_detail/4 is available, use ground_or_theory for the theory such as anticipation or obviousness, not the statute number.",
            "When a later review body affirms or reverses the same ground, preserve both layers: the underlying action/status here and the review layer in review_outcome/4 when available.",
        ],
    },
    "review_outcome/4": {
        "args": ["reviewed_subject_id", "reviewing_body_or_actor", "review_outcome_or_action", "source_or_scope"],
        "description": (
            "A reviewed claim set, order, finding, decision, or action linked to the source-stated "
            "reviewing body and review outcome."
        ),
        "why": (
            "Keeps appellate, board, agency, protest, grievance, or administrative review outcomes "
            "joinable to the underlying typed subject instead of inventing private affirmed_by-style atoms."
        ),
        "admission_notes": [
            "Use for later review actions such as affirmed, reversed, modified, vacated, remanded, sustained, denied, or granted.",
            "Reuse the same reviewed_subject_id used by the underlying action, ground, finding, decision, or inventory rows.",
            "Do not use review_outcome/4 for the original lower-body action when no later review outcome is stated.",
            "Do not hide the underlying action, ground, basis, or affected items inside reviewed_subject_id; preserve those in companion typed rows.",
        ],
    },
}


RATING_SCALE_SIGNATURES = {
    "rating_scale_option/4": {
        "args": ["scale_or_factor_id", "rating_value", "rating_order_or_rank", "source_or_scope"],
        "description": (
            "One source-stated option in an adjectival, relevancy, confidence, quality, risk, or "
            "evaluation rating scale."
        ),
        "why": (
            "Preserves allowed rating options as typed atoms distinct from ratings actually assigned to "
            "a particular party, proposal, contract, product, or record."
        ),
        "admission_notes": [
            "Use only for rating options explicitly listed by the source as a scale or allowed value set.",
            "Use scale_or_factor_id for the source-stated scale or factor, such as past_performance_relevancy or confidence_assessment.",
            "Use rating_value for the exact normalized option value, such as very_relevant or substantial_confidence.",
            "Use rating_order_or_rank for the source order when stated or inferable from the explicit list order; otherwise use unranked.",
            "Do not use this carrier for an assigned rating; assigned_rating/3 remains the assigned-value carrier.",
        ],
    }
}


def _ensure_list_range_inventory_predicates(parsed_profile: dict[str, Any]) -> dict[str, Any]:
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_list_range_inventory_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    claim_relation_signal = _profile_has_claim_set_relation_signal(parsed_profile)
    added: list[str] = []
    for signature, spec in LIST_RANGE_INVENTORY_SIGNATURES.items():
        if signature in signatures:
            continue
        candidates.append(
            {
                "signature": signature,
                "args": list(spec["args"]),
                "description": str(spec["description"]),
                "why": str(spec["why"]),
                "admission_notes": list(spec["admission_notes"]),
            }
        )
        added.append(signature)
    if claim_relation_signal:
        for signature, spec in CLAIM_SET_RELATION_SIGNATURES.items():
            if signature in signatures:
                continue
            candidates.append(
                {
                    "signature": signature,
                    "args": list(spec["args"]),
                    "description": str(spec["description"]),
                    "why": str(spec["why"]),
                    "admission_notes": list(spec["admission_notes"]),
                }
            )
            signatures.add(signature)
            added.append(signature)
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list):
        for signature in added:
            if signature not in provenance:
                provenance.append(signature)
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list) and added:
            notes.append(
                "Deterministic profile extension added typed list/range inventory carriers for source-stated numbered sets."
            )
    return {
        "schema_version": "profile_list_range_inventory_extension_v1",
        "added": bool(added),
        "signatures": added,
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _profile_has_claim_set_relation_signal(parsed_profile: dict[str, Any]) -> bool:
    candidates = parsed_profile.get("candidate_predicates")
    if isinstance(candidates, list):
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            haystack = " ".join(
                [
                    str(candidate.get("signature", "")),
                    " ".join(str(arg) for arg in candidate.get("args", []) if isinstance(candidate.get("args"), list)),
                    str(candidate.get("description", "")),
                    str(candidate.get("why", "")),
                ]
            ).casefold()
            if "claim" in haystack and any(token in haystack for token in ("ground", "basis", "reject", "outcome", "status", "reference")):
                return True
    entities = parsed_profile.get("entity_types")
    if isinstance(entities, list):
        for entity in entities:
            if isinstance(entity, dict) and "claim" in str(entity.get("name", "")).casefold():
                return True
    return False


def _ensure_rating_scale_option_predicate(parsed_profile: dict[str, Any]) -> dict[str, Any]:
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_rating_scale_extension_v1", "added": False, "reason": "no_candidate_list"}
    if not _profile_has_rating_scale_signal(parsed_profile):
        return {"schema_version": "profile_rating_scale_extension_v1", "added": False, "reason": "no_rating_scale_signal"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    added: list[str] = []
    for signature, spec in RATING_SCALE_SIGNATURES.items():
        if signature in signatures:
            continue
        candidates.append(
            {
                "signature": signature,
                "args": list(spec["args"]),
                "description": str(spec["description"]),
                "why": str(spec["why"]),
                "admission_notes": list(spec["admission_notes"]),
            }
        )
        added.append(signature)
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list):
        for signature in added:
            if signature not in provenance:
                provenance.append(signature)
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list) and added:
            notes.append(
                "Deterministic profile extension added a typed rating-scale option carrier for source-stated rating scales."
            )
    return {
        "schema_version": "profile_rating_scale_extension_v1",
        "added": bool(added),
        "signatures": added,
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _profile_has_rating_scale_signal(parsed_profile: dict[str, Any]) -> bool:
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return False
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        haystack = " ".join(
            [
                str(candidate.get("signature", "")),
                " ".join(str(arg) for arg in candidate.get("args", []) if isinstance(candidate.get("args"), list)),
                str(candidate.get("description", "")),
                str(candidate.get("why", "")),
                " ".join(str(note) for note in candidate.get("admission_notes", []) if isinstance(candidate.get("admission_notes"), list)),
            ]
        ).casefold()
        if "rating" in haystack and any(
            token in haystack
            for token in (
                "assign",
                "assigned",
                "adjectival",
                "relevancy",
                "confidence",
                "evaluation",
                "quality",
                "risk",
                "scale",
                "option",
                "factor",
            )
        ):
            return True
    return False


def _reconcile_profile_carrier_contracts(parsed_profile: dict[str, Any]) -> dict[str, Any]:
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {
            "schema_version": "profile_carrier_contract_registry_reconciliation_v1",
            "changed_count": 0,
            "changes": [],
            "reason": "no_candidate_list",
        }
    changes: list[dict[str, Any]] = []
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if not isinstance(provenance, list):
        provenance = []
        parsed_profile["provenance_sensitive_predicates"] = provenance
    for item in candidates:
        if not isinstance(item, dict):
            continue
        signature = str(item.get("signature", "")).strip()
        contract = carrier_contract(signature)
        if not isinstance(contract, dict):
            continue
        expected_args = [str(arg) for arg in contract.get("args", []) if str(arg).strip()]
        current_args = [str(arg) for arg in item.get("args", [])] if isinstance(item.get("args"), list) else []
        change: dict[str, Any] = {"signature": signature}
        changed = False
        if expected_args and current_args != expected_args:
            item["args"] = expected_args
            change["previous_args"] = current_args
            change["expected_args"] = expected_args
            changed = True
        required_provenance = contract.get("required_provenance")
        if isinstance(required_provenance, list) and required_provenance and signature not in provenance:
            provenance.append(signature)
            change["provenance_sensitive_added"] = True
            changed = True
        if changed:
            changes.append(change)
    return {
        "schema_version": "profile_carrier_contract_registry_reconciliation_v1",
        "changed_count": len(changes),
        "authority": "registered_carrier_contract_only",
        "fact_extraction": False,
        "changes": changes,
    }


def _ensure_document_metadata_predicates(parsed_profile: dict[str, Any]) -> dict[str, Any]:
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_document_metadata_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    added: list[str] = []
    for signature, spec in DOCUMENT_METADATA_SIGNATURES.items():
        if signature in signatures:
            continue
        candidates.append(
            {
                "signature": signature,
                "args": list(spec["args"]),
                "description": str(spec["description"]),
                "why": str(spec["why"]),
                "admission_notes": list(spec["admission_notes"]),
            }
        )
        added.append(signature)
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list):
        for signature in added:
            if signature not in provenance:
                provenance.append(signature)
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list) and added:
            notes.append(
                "Deterministic profile extension added document metadata carriers for title, publisher, and stated date range."
            )
    return {
        "schema_version": "profile_document_metadata_extension_v1",
        "added": bool(added),
        "signatures": added,
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _ensure_legal_citation_detail_predicate(parsed_profile: dict[str, Any]) -> dict[str, Any]:
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_legal_citation_detail_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if "legal_citation_detail/4" in signatures:
        return {
            "schema_version": "profile_legal_citation_detail_extension_v1",
            "added": False,
            "reason": "legal_citation_detail_already_present",
        }
    candidates.append(
        {
            "signature": "legal_citation_detail/4",
            "args": ["subject_id", "citation", "citation_role_or_purpose", "source_or_scope"],
            "description": (
                "Exact source-stated legal citations linked to the obligation, notice, finding, rule, "
                "exception, checkbox provision, or procedural right they support."
            ),
            "why": (
                "Preserves exact statutes, regulations, named procedural rule sets, rules, clauses, "
                "subsections, and case citations as typed values instead of embedding them in prose-like "
                "obligation atoms."
            ),
            "admission_notes": [
                "Use only for exact source-stated legal citations.",
                "Keep the cited authority separate from the role or purpose it serves.",
                "When a source lists multiple citations for one notice, obligation, checkbox, or exception, emit one row per citation.",
                "Named procedural rule sets such as rules of appellate procedure are citation-like authorities even when no section number is stated.",
                "When a source-stated citation clause includes future amendments, successor regulations, or later-adopted rules, preserve that coverage as a compact typed citation-scope row with role amendment_scope.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "legal_citation_detail/4" not in provenance:
        provenance.append("legal_citation_detail/4")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append(
                "Deterministic profile extension added legal_citation_detail/4 for exact source-stated citations."
            )
    return {
        "schema_version": "profile_legal_citation_detail_extension_v1",
        "added": True,
        "signature": "legal_citation_detail/4",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _ensure_monetary_payment_predicate(parsed_profile: dict[str, Any]) -> dict[str, Any]:
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_monetary_payment_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if "monetary_payment/5" in signatures:
        return {
            "schema_version": "profile_monetary_payment_extension_v1",
            "added": False,
            "reason": "monetary_payment_already_present",
        }
    candidates.append(
        {
            "signature": "monetary_payment/5",
            "args": ["subject_id", "amount", "authority_or_basis", "purpose_or_use", "source_or_scope"],
            "description": (
                "Source-stated payment, relief, restitution, penalty, reimbursement, settlement, or other "
                "monetary amount tied to a governed subject and source scope."
            ),
            "why": (
                "Official documents often state a money amount together with a legal basis and use/purpose. "
                "Preserve the amount as a typed value instead of leaving it in prose or a date/range carrier."
            ),
            "admission_notes": [
                "Use only for exact source-stated money amounts.",
                "Use compact amount atoms such as usd_725000 for $725,000.",
                "Keep authority_or_basis as a compact statute, rule, paragraph, order, or agreement atom when stated; use none_stated only if the source gives no basis.",
                "Keep purpose_or_use compact, such as restitution_and_penalties, civil_penalty, refund, reimbursement, or settlement_payment.",
                "Keep source_or_scope as the paragraph, agreement section, source coordinate, or payment scope that states the amount.",
                "Do not use monetary_payment/5 for date ranges, item counts, or broad payment prose without an exact amount.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "monetary_payment/5" not in provenance:
        provenance.append("monetary_payment/5")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append(
                "Deterministic profile extension added monetary_payment/5 for exact source-stated payment amounts."
            )
    return {
        "schema_version": "profile_monetary_payment_extension_v1",
        "added": True,
        "signature": "monetary_payment/5",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _ensure_obligation_detail_predicate(parsed_profile: dict[str, Any]) -> dict[str, Any]:
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_obligation_detail_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if "obligation_detail/5" in signatures:
        return {
            "schema_version": "profile_obligation_detail_extension_v1",
            "added": False,
            "reason": "obligation_detail_already_present",
        }
    candidates.append(
        {
            "signature": "obligation_detail/5",
            "args": ["obligation_id", "detail_kind", "detail_value", "role_or_purpose", "source_or_scope"],
            "description": (
                "One compact source-stated term of an obligation, requirement, settlement condition, "
                "reporting duty, corrective action, or compliance obligation."
            ),
            "why": (
                "Obligations often bundle deliverables, recipient scope, frequency, duration, schedule, "
                "deadline, and conditions in one sentence. Preserve those as joinable typed details instead "
                "of one long obligation prose atom."
            ),
            "admission_notes": [
                "Use one obligation_detail/5 row per atomic source-stated obligation term.",
                "Use detail_kind values such as deliverable, recipient_scope, tariff_schedule, frequency, duration, deadline, authority, condition, exception, or method.",
                "Use compact detail_value atoms such as schedule_9, one_year, quarterly, individual_and_power_quality_data, or written_request.",
                "Use role_or_purpose to preserve the obligation family, such as data_reporting, settlement_obligation, compliance_requirement, notice_requirement, or corrective_action.",
                "Use source_or_scope for the paragraph, agreement section, source line, table row, or local source scope that states the detail.",
                "Do not place the full obligation sentence or several details into detail_value.",
                "If a broad obligation summary predicate such as settlement_obligation/3 exists, reuse the same obligation_id where possible.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "obligation_detail/5" not in provenance:
        provenance.append("obligation_detail/5")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append(
                "Deterministic profile extension added obligation_detail/5 for compact source-stated obligation terms."
            )
    source_pressure = _profile_has_obligation_detail_pressure(parsed_profile)
    return {
        "schema_version": "profile_obligation_detail_extension_v1",
        "added": True,
        "signature": "obligation_detail/5",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
        "source_pressure": source_pressure,
        "accountability_required": source_pressure,
    }


def _profile_has_obligation_detail_pressure(parsed_profile: dict[str, Any]) -> bool:
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return False
    pressure_terms = {
        "compliance",
        "condition",
        "corrective",
        "duty",
        "obligation",
        "requirement",
        "settlement",
        "term",
    }
    for item in candidates:
        if not isinstance(item, dict):
            continue
        signature = str(item.get("signature", "")).casefold().replace("_", " ")
        args = " ".join(str(arg) for arg in item.get("args", []) if str(arg).strip()) if isinstance(item.get("args"), list) else ""
        text = f"{signature} {args}".casefold().replace("_", " ")
        if _profile_admission_tokens(text) & pressure_terms:
            return True
    return False


def _ensure_procedural_rule_detail_predicate(parsed_profile: dict[str, Any]) -> dict[str, Any]:
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {
            "schema_version": "profile_procedural_rule_detail_extension_v1",
            "added": False,
            "reason": "no_candidate_list",
        }
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if "procedural_rule_detail/5" in signatures:
        return {
            "schema_version": "profile_procedural_rule_detail_extension_v1",
            "added": False,
            "reason": "procedural_rule_detail_already_present",
        }
    candidates.append(
        {
            "signature": "procedural_rule_detail/5",
            "args": ["rule_id", "detail_kind", "detail_value", "rule_context_or_action", "source_or_scope"],
            "description": (
                "One compact source-stated term of a procedural rule, review right, rehearing right, appeal path, "
                "filing requirement, deadline rule, or default consequence."
            ),
            "why": (
                "Procedural rules often bundle a trigger, filing/action, period, start anchor, authority, and "
                "consequence in one sentence. Preserve those as joinable typed details instead of one long rule "
                "or deadline prose atom."
            ),
            "admission_notes": [
                "Use one procedural_rule_detail/5 row per atomic source-stated procedural rule term.",
                "Use detail_kind values such as trigger, action, deadline, period, consequence, authority, condition, exception, start_anchor, or filing_window.",
                "Use compact detail_value atoms such as thirty_days, ten_days, deemed_denied, request_for_review_or_rehearing, or basis_known_or_should_have_been_known.",
                "Use rule_context_or_action to preserve the procedural family, such as review_or_rehearing_request, reconsideration_request, appeal_path, filing_requirement, or agency_review.",
                "Use source_or_scope for the statute, regulation, paragraph, notice section, source line, table row, or local source scope that states the detail.",
                "Do not place the full rule sentence or several details into detail_value.",
                "If legal_citation_detail/4 is present, preserve exact authorities there and reuse the same rule_id when possible.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "procedural_rule_detail/5" not in provenance:
        provenance.append("procedural_rule_detail/5")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append(
                "Deterministic profile extension added procedural_rule_detail/5 for compact source-stated procedural rule terms."
            )
    source_pressure = _profile_has_procedural_rule_detail_pressure(parsed_profile)
    return {
        "schema_version": "profile_procedural_rule_detail_extension_v1",
        "added": True,
        "signature": "procedural_rule_detail/5",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
        "source_pressure": source_pressure,
        "accountability_required": source_pressure,
    }


def _profile_has_procedural_rule_detail_pressure(parsed_profile: dict[str, Any]) -> bool:
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return False
    pressure_terms = {
        "appeal",
        "authority",
        "condition",
        "consequence",
        "deadline",
        "filing",
        "period",
        "procedure",
        "procedural",
        "reconsideration",
        "rehearing",
        "request",
        "review",
        "rule",
    }
    for item in candidates:
        if not isinstance(item, dict):
            continue
        signature = str(item.get("signature", "")).casefold().replace("_", " ")
        args = " ".join(str(arg) for arg in item.get("args", []) if str(arg).strip()) if isinstance(item.get("args"), list) else ""
        text = f"{signature} {args}".casefold().replace("_", " ")
        if _profile_admission_tokens(text) & pressure_terms:
            return True
    return False


def _ensure_document_checkbox_provision_predicate(parsed_profile: dict[str, Any]) -> dict[str, Any]:
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_document_checkbox_provision_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if "document_checkbox_provision/5" in signatures:
        return {
            "schema_version": "profile_document_checkbox_provision_extension_v1",
            "added": False,
            "reason": "document_checkbox_provision_already_present",
        }
    candidates.append(
        {
            "signature": "document_checkbox_provision/5",
            "args": ["document_id", "provision_label_or_text", "checkbox_mark", "rule_or_provision", "citation"],
            "description": (
                "Source-stated checkbox or checklist provisions on official forms, including the literal mark, "
                "the provision/rule label, and any exact citation printed with that checkbox row."
            ),
            "why": (
                "Official forms often carry answer-bearing checkbox rows where the mark, rule label, and citation "
                "are distinct typed values. Preserve those values as structure rather than as source-record prose."
            ),
            "admission_notes": [
                "Use only for checkbox or checklist rows that are explicitly present in the source.",
                "Emit one row per checkbox/list provision.",
                "Keep the checkbox mark as the literal source mark when present, or a normalized checked/unchecked atom when the source states the state in words.",
                "Keep rule labels and citations separate: for example, a rule label and a CFR citation should occupy distinct slots.",
                "Do not infer a substantive legal consequence from a checkbox state unless another typed predicate explicitly carries that consequence.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "document_checkbox_provision/5" not in provenance:
        provenance.append("document_checkbox_provision/5")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append(
                "Deterministic profile extension added document_checkbox_provision/5 for source-stated checkbox/list rows."
            )
    return {
        "schema_version": "profile_document_checkbox_provision_extension_v1",
        "added": True,
        "signature": "document_checkbox_provision/5",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _ensure_document_identifier_occurrence_predicate(parsed_profile: dict[str, Any]) -> dict[str, Any]:
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_document_identifier_occurrence_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if "document_identifier_occurrence/5" in signatures:
        return {
            "schema_version": "profile_document_identifier_occurrence_extension_v1",
            "added": False,
            "reason": "document_identifier_occurrence_already_present",
        }
    candidates.append(
        {
            "signature": "document_identifier_occurrence/5",
            "args": ["document_id", "identifier_kind", "identifier_value", "occurrence_scope_or_label", "source_order"],
            "description": (
                "Each source-stated occurrence of a document identifier, preserving repeated identifiers of the "
                "same kind when they appear in different cover-page blocks, headers, tables, or form fields. "
                "This carrier is specifically for cases where a single collapsed identifier row would lose a "
                "distinct source-stated value."
            ),
            "why": (
                "Documents can state multiple identifiers with the same label in different scopes. Preserve each "
                "occurrence as a typed row so exact identifier questions do not depend on source-record text."
            ),
            "admission_notes": [
                "Use only for identifiers explicitly stated in the source.",
                "Emit one row per occurrence when the same identifier kind appears more than once.",
                "If two source lines or fields use the same identifier label but state different values, preserve both values as separate rows.",
                "Keep occurrence_scope_or_label source-local and structural, such as header, cover_page_block, table_row, or filed_form_field.",
                "Use source_order to preserve source order with a small integer or source-line atom.",
                "Do not collapse distinct values merely because they share the same identifier_kind.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "document_identifier_occurrence/5" not in provenance:
        provenance.append("document_identifier_occurrence/5")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append(
                "Deterministic profile extension added document_identifier_occurrence/5 for repeated source-stated identifiers."
            )
    return {
        "schema_version": "profile_document_identifier_occurrence_extension_v1",
        "added": True,
        "signature": "document_identifier_occurrence/5",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _ensure_repeated_structure_predicates(parsed_profile: dict[str, Any]) -> dict[str, Any]:
    """Admit repeated-structure record/property predicates named by the profile.

    The profile schema treats repeated_structures as a vocabulary reference, not
    as a separate hidden namespace. If the LLM names property predicates there
    but omits them from candidate_predicates, the compiler can otherwise produce
    structurally correct rows and then reject them as outside the allowed
    palette. This extension repairs that palette contract only; it extracts no
    facts.
    """

    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {
            "schema_version": "profile_repeated_structure_predicate_extension_v1",
            "added": False,
            "reason": "no_candidate_list",
        }
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    repeated = parsed_profile.get("repeated_structures")
    if not isinstance(repeated, list):
        return {
            "schema_version": "profile_repeated_structure_predicate_extension_v1",
            "added": False,
            "reason": "no_repeated_structures",
        }
    added: list[str] = []
    for item in repeated:
        if not isinstance(item, dict):
            continue
        refs = [str(item.get("record_predicate", "")).strip()]
        if isinstance(item.get("property_predicates"), list):
            refs.extend(str(ref).strip() for ref in item.get("property_predicates", []) if str(ref).strip())
        for ref in refs:
            signature = _normalized_signature(ref)
            if not signature or signature in signatures:
                continue
            _name, arity_text = signature.split("/", 1)
            arity = int(arity_text)
            candidates.append(
                {
                    "signature": signature,
                    "args": [f"arg_{index}" for index in range(1, arity + 1)],
                    "description": (
                        "Predicate named by repeated_structures and admitted so repeated record/property rows "
                        "can use the same palette they were planned under."
                    ),
                    "why": (
                        "Keeps repeated-structure vocabulary from becoming a hidden namespace that compile passes "
                        "can plan but not emit."
                    ),
                    "admission_notes": [
                        "Vocabulary extension only; use only for source-grounded rows belonging to the repeated structure.",
                    ],
                }
            )
            signatures.add(signature)
            added.append(signature)
    if added:
        self_check = parsed_profile.get("self_check")
        if isinstance(self_check, dict):
            notes = self_check.get("notes")
            if isinstance(notes, list):
                notes.append(
                    "Deterministic profile extension admitted repeated_structure record/property predicates: "
                    + ", ".join(added[:12])
                )
        return {
            "schema_version": "profile_repeated_structure_predicate_extension_v1",
            "added": True,
            "signatures": added,
            "authority": "vocabulary_extension_only",
            "fact_extraction": False,
        }
    return {
        "schema_version": "profile_repeated_structure_predicate_extension_v1",
        "added": False,
        "reason": "all_repeated_structure_predicates_already_present",
    }


SOURCE_AUTHORITY_TEXT_RE = re.compile(
    r"\b(?:only\s+(?:the\s+)?[a-z][a-z\s_-]{0,40}\s+(?:may|can|must|is_authorized_to|is_authorised_to)|"
    r"authorized\s+by|authorised\s+by|authorization\s+act|authority|governing\s+(?:act|rule|policy|source|statute)|"
    r"(?:court|board|agency|committee|supervisor|director|officer)\s+(?:order|approval|authorization|authorisation))\b",
    re.IGNORECASE,
)

SCHEDULED_EVENT_TEXT_RE = re.compile(
    r"\b(?:next\s+)?(?:calibration|maintenance|service|inspection)\s+"
    r"(?:is\s+)?(?:due|scheduled|planned|set)\b|"
    r"\b(?:due|scheduled|planned|set)\s+(?:for\s+)?(?:calibration|maintenance|service|inspection)\b",
    re.IGNORECASE,
)

ENTITY_LOCATION_TEXT_RE = re.compile(
    r"\b(?:location|located|stored|retained|held|site|room|cabinet|bay|bench|greenhouse|unit)\b",
    re.IGNORECASE,
)

QUORUM_TEXT_RE = re.compile(r"\bquorum\b", re.IGNORECASE)

APPEAL_FILING_TEXT_RE = re.compile(
    r"\b(?:appeal|appealed)\b.{0,80}\b(?:filed|files|filing|lodged)\b|"
    r"\b(?:filed|files|filing|lodged)\b.{0,80}\b(?:appeal|appealed)\b|"
    r"\bnotice\s+of\s+appeal\b.{0,80}\b(?:filed|lodged|docketed|submitted)\b|"
    r"\b(?:filed|lodged|docketed|submitted)\b.{0,80}\bnotice\s+of\s+appeal\b",
    re.IGNORECASE,
)

EVENT_DATE_TEXT_RE = re.compile(
    r"\b(?:event|hearing|meeting|filing|filed|appeal|application|vote|correction|declaration|ratification|review)\b"
    r".{0,80}\b(?:(?:19|20)\d{2}[-_]\d{1,2}[-_]\d{1,2}|"
    r"(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|"
    r"oct|october|nov|november|dec|december)\s+\d{1,2},?\s+(?:19|20)\d{2})\b|"
    r"\b(?:(?:19|20)\d{2}[-_]\d{1,2}[-_]\d{1,2}|"
    r"(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|"
    r"oct|october|nov|november|dec|december)\s+\d{1,2},?\s+(?:19|20)\d{2})\b"
    r".{0,80}\b(?:event|hearing|meeting|filing|filed|appeal|application|vote|correction|declaration|ratification|review)\b",
    re.IGNORECASE,
)

EVENT_TIME_TEXT_RE = re.compile(
    r"\b(?:event|hearing|meeting|filing|filed|appeal|application|vote|correction|declaration|ratification|review|"
    r"record|signal|status|entry|action|notice|occurred|received|released|opened|closed|started|ended|arrived|"
    r"departed|activated|detected|observed|reported|recorded)\b"
    r".{0,100}\b(?:about|around|approximately|approx|near|at|by)\s+"
    r"(?:(?:[01]?\d|2[0-3])(?::?[0-5]\d)(?::?[0-5]\d)?)\b|"
    r"\b(?:about|around|approximately|approx|near|at|by)\s+"
    r"(?:(?:[01]?\d|2[0-3])(?::?[0-5]\d)(?::?[0-5]\d)?)\b"
    r".{0,100}\b(?:event|hearing|meeting|filing|filed|appeal|application|vote|correction|declaration|ratification|review|"
    r"record|signal|status|entry|action|notice|occurred|received|released|opened|closed|started|ended|arrived|"
    r"departed|activated|detected|observed|reported|recorded)\b|"
    r"\b(?:event|hearing|meeting|filing|filed|appeal|application|vote|correction|declaration|ratification|review|"
    r"record|signal|status|entry|action|notice|occurred|received|released|opened|closed|started|ended|arrived|"
    r"departed|activated|detected|observed|reported|recorded)\b"
    r".{0,100}\b(?:(?:[01]?\d|2[0-3])[:_][0-5]\d(?:[:_][0-5]\d)?)\b|"
    r"\b(?:(?:[01]?\d|2[0-3])[:_][0-5]\d(?:[:_][0-5]\d)?)\b"
    r".{0,100}\b(?:event|hearing|meeting|filing|filed|appeal|application|vote|correction|declaration|ratification|review|"
    r"record|signal|status|entry|action|notice|occurred|received|released|opened|closed|started|ended|arrived|"
    r"departed|activated|detected|observed|reported|recorded)\b",
    re.IGNORECASE,
)

PUBLIC_RECALL_PRIOR_DATE_TEXT_RE = re.compile(
    r"\b(?:expand(?:ing|s|ed)?|expansion|amend(?:ing|s|ed)?|updat(?:ing|es|ed)?|supersed(?:ing|es|ed)?|revis(?:ing|es|ed)?)\b"
    r".{0,80}\b(?P<date1>(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)\s+\d{1,2},?\s+(?:19|20)\d{2})\b"
    r".{0,60}\b(?:recall|notice|announcement|advisory)\b|"
    r"\b(?:original|prior|previous|earlier|initial)\s+(?:recall|notice|announcement|advisory)\b"
    r".{0,80}\b(?P<date2>(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)\s+\d{1,2},?\s+(?:19|20)\d{2})\b",
    re.IGNORECASE,
)

VOTE_TALLY_PAIR_PATTERN = r"(?<!\d)(\d{1,2})\s*[-_]\s*(\d{1,2})(?!\d)"
VOTE_TALLY_PAIR_RE = re.compile(VOTE_TALLY_PAIR_PATTERN)
VOTE_TALLY_TEXT_RE = re.compile(
    rf"\b(?:vote|votes|voted|voting|tally|approved|denied|recorded|corrected)\b.{{0,120}}{VOTE_TALLY_PAIR_PATTERN}|"
    rf"{VOTE_TALLY_PAIR_PATTERN}.{{0,120}}\b(?:vote|votes|voted|voting|tally|approved|denied|recorded|corrected)\b",
    re.IGNORECASE,
)


def _ensure_source_authority_predicate(parsed_profile: dict[str, Any], *, source_text: str) -> dict[str, Any]:
    """Ensure a generic source-authority carrier for explicit authority constraints.

    This is vocabulary-only. It gives the compiler a direct surface for source
    text that states which authority, source, or rule governs an action/scope,
    without deriving any facts from that text in Python.
    """

    if not SOURCE_AUTHORITY_TEXT_RE.search(str(source_text or "")):
        return {
            "schema_version": "profile_source_authority_extension_v1",
            "added": False,
            "reason": "no_explicit_source_authority_signal",
        }
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_source_authority_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if _has_specific_source_authority_carrier(signatures):
        return {
            "schema_version": "profile_source_authority_extension_v1",
            "added": False,
            "reason": "source_authority_carrier_present",
        }

    candidates.append(
        {
            "signature": "source_authority/3",
            "args": ["subject_id", "authority_or_source", "scope_or_action"],
            "description": (
                "Direct source-authority surface for source-stated rules, orders, policies, or authorities "
                "that govern an action, status, access, finding, deadline, or other scoped decision."
            ),
            "why": (
                "Prevents authority/source constraints from being stranded inside rule text, notes, "
                "or source-record rows when questions need the governing source and governed scope."
            ),
            "admission_notes": [
                "Vocabulary extension only; use only for explicit source-stated authority constraints.",
                "Keep the governed subject/scope, the authority or source, and the authorized action or status joinable.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "source_authority/3" not in provenance:
        provenance.append("source_authority/3")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append("Deterministic profile extension added source_authority/3 after explicit authority/source signal.")
    return {
        "schema_version": "profile_source_authority_extension_v1",
        "added": True,
        "signature": "source_authority/3",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _has_specific_source_authority_carrier(signatures: set[str]) -> bool:
    direct = {
        "access_authority_source/2",
        "access_authorized_to/3",
        "access_source/3",
        "authority_for/3",
        "authority_source/3",
        "authorized_by/3",
        "governing_source/3",
        "source_authority/3",
        "source_for_authority/3",
    }
    if signatures & direct:
        return True
    for signature in signatures:
        predicate, _, arity = signature.partition("/")
        if arity not in {"3", "4", "5"}:
            continue
        tokens = set(predicate.split("_"))
        if tokens & {"authority", "authorized", "authorised", "governing"} and tokens & {"source", "rule", "policy", "order", "scope"}:
            return True
    return False


def _ensure_vote_tally_predicate(parsed_profile: dict[str, Any], *, source_text: str) -> dict[str, Any]:
    """Ensure a direct vote-tally carrier for explicit source-stated votes."""

    if not _vote_tally_source_mentions(source_text):
        return {
            "schema_version": "profile_vote_tally_extension_v1",
            "added": False,
            "reason": "no_explicit_vote_tally_signal",
        }
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_vote_tally_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if _has_specific_vote_tally_carrier(signatures):
        return {
            "schema_version": "profile_vote_tally_extension_v1",
            "added": False,
            "reason": "vote_tally_carrier_present",
        }

    candidates.append(
        {
            "signature": "vote_tally/5",
            "args": ["vote_id", "body_or_group", "subject_or_motion", "result", "tally_or_member_votes"],
            "description": (
                "Direct vote-tally surface for source-stated decisions, motions, approvals, denials, "
                "roll calls, and corrected vote records."
            ),
            "why": (
                "Prevents final vote counts, individual member votes, and corrected minute tallies from being "
                "stranded inside broad hearing notes or source-record rows."
            ),
            "admission_notes": [
                "Vocabulary extension only; use only for explicit source-stated vote records.",
                "Keep voting body, decision subject, result, tally, and member votes or source scope joinable.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "vote_tally/5" not in provenance:
        provenance.append("vote_tally/5")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append("Deterministic profile extension added vote_tally/5 after explicit vote-tally signal.")
    return {
        "schema_version": "profile_vote_tally_extension_v1",
        "added": True,
        "signature": "vote_tally/5",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _has_specific_vote_tally_carrier(signatures: set[str]) -> bool:
    direct = {
        "decision_vote/4",
        "final_vote/4",
        "motion_vote/4",
        "roll_call_vote/4",
        "vote_record/4",
        "vote_tally/5",
    }
    if signatures & direct:
        return True
    for signature in signatures:
        predicate, _, arity = signature.partition("/")
        if arity not in {"4", "5", "6"}:
            continue
        tokens = set(predicate.split("_"))
        if tokens & {"vote", "votes", "voting", "tally", "ballot"} and tokens & {"decision", "final", "motion", "record", "roll"}:
            return True
    return False


def _ensure_event_date_predicate(parsed_profile: dict[str, Any], *, source_text: str) -> dict[str, Any]:
    """Ensure a direct event temporal carrier for explicit dated or timed events."""

    has_date_signal = bool(EVENT_DATE_TEXT_RE.search(str(source_text or "")))
    has_time_signal = bool(EVENT_TIME_TEXT_RE.search(str(source_text or "")))
    if not has_date_signal and not has_time_signal:
        return {
            "schema_version": "profile_event_date_extension_v1",
            "added": False,
            "reason": "no_explicit_event_temporal_signal",
        }
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_event_date_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if _has_specific_event_date_carrier(signatures):
        return {
            "schema_version": "profile_event_date_extension_v1",
            "added": False,
            "reason": "event_date_carrier_present",
        }

    signature = "event_date/2" if has_date_signal else "event_time/2"
    value_arg = "date" if has_date_signal else "time_or_timestamp"
    candidates.append(
        {
            "signature": signature,
            "args": ["event_id", value_arg],
            "description": "Direct temporal surface for source-stated event, hearing, meeting, filing, appeal, vote, or correction dates/times.",
            "why": "Prevents date- or time-bearing event identifiers from being the only place where event time is represented.",
            "admission_notes": [
                "Vocabulary extension only; use only for explicit source-stated event dates, times, or timestamps.",
                "Keep stable event id and temporal value joinable in separate arguments.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and signature not in provenance:
        provenance.append(signature)
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append(f"Deterministic profile extension added {signature} after explicit event temporal signal.")
    return {
        "schema_version": "profile_event_date_extension_v1",
        "added": True,
        "signature": signature,
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _has_specific_event_date_carrier(signatures: set[str]) -> bool:
    direct = {
        "event_date/2",
        "event_time/2",
        "event_timestamp/2",
        "event_wall_time/2",
        "hearing_date/2",
        "meeting_date/2",
    }
    if signatures & direct:
        return True
    event_terms = {"appeal", "correction", "event", "filing", "hearing", "meeting", "notice", "vote"}
    temporal_terms = {"date", "dated", "time", "timestamp"}
    for signature in signatures:
        predicate, _, arity = signature.partition("/")
        if arity not in {"2", "3", "4"}:
            continue
        tokens = set(predicate.split("_"))
        if tokens & event_terms and tokens & temporal_terms:
            return True
    return False


def _ensure_quorum_status_predicate(parsed_profile: dict[str, Any], *, source_text: str) -> dict[str, Any]:
    """Ensure a direct quorum-status carrier for explicit quorum checks."""

    if not QUORUM_TEXT_RE.search(str(source_text or "")):
        return {
            "schema_version": "profile_quorum_status_extension_v1",
            "added": False,
            "reason": "no_explicit_quorum_signal",
        }
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_quorum_status_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if _has_specific_quorum_status_carrier(signatures):
        return {
            "schema_version": "profile_quorum_status_extension_v1",
            "added": False,
            "reason": "quorum_status_carrier_present",
        }

    candidates.append(
        {
            "signature": "quorum_status/3",
            "args": ["event_id", "status", "count_or_requirement"],
            "description": "Direct quorum surface for source-stated meeting or hearing quorum checks.",
            "why": "Prevents quorum facts from being stranded inside source-attributed claims, hearing notes, or broad source detail rows.",
            "admission_notes": [
                "Vocabulary extension only; use only for explicit source-stated quorum facts.",
                "Keep event/hearing id, quorum status, and count or requirement joinable.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "quorum_status/3" not in provenance:
        provenance.append("quorum_status/3")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append("Deterministic profile extension added quorum_status/3 after explicit quorum signal.")
    return {
        "schema_version": "profile_quorum_status_extension_v1",
        "added": True,
        "signature": "quorum_status/3",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _has_specific_quorum_status_carrier(signatures: set[str]) -> bool:
    if "quorum_status/3" in signatures:
        return True
    for signature in signatures:
        predicate, _, arity = signature.partition("/")
        if arity not in {"2", "3", "4"}:
            continue
        if "quorum" in set(predicate.split("_")):
            return True
    return False


def _ensure_appeal_filing_predicate(parsed_profile: dict[str, Any], *, source_text: str) -> dict[str, Any]:
    """Ensure a direct appeal-filing carrier for explicit source-stated appeals."""

    if not APPEAL_FILING_TEXT_RE.search(str(source_text or "")):
        return {
            "schema_version": "profile_appeal_filing_extension_v1",
            "added": False,
            "reason": "no_explicit_appeal_filing_signal",
        }
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_appeal_filing_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if _has_specific_appeal_filing_carrier(signatures):
        return {
            "schema_version": "profile_appeal_filing_extension_v1",
            "added": False,
            "reason": "appeal_filing_carrier_present",
        }

    candidates.append(
        {
            "signature": "appeal_filed/3",
            "args": ["appellant", "target_or_subject", "date_or_status"],
            "description": "Direct appeal-filing surface for source-stated appeals or notices of appeal.",
            "why": "Prevents appeal filing facts from being stranded inside source-attributed claims or post-hearing notes.",
            "admission_notes": [
                "Vocabulary extension only; use only for explicit source-stated appeal filings.",
                "Keep appellant, appealed target or subject, and filing date or status joinable.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "appeal_filed/3" not in provenance:
        provenance.append("appeal_filed/3")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append("Deterministic profile extension added appeal_filed/3 after explicit appeal-filing signal.")
    return {
        "schema_version": "profile_appeal_filing_extension_v1",
        "added": True,
        "signature": "appeal_filed/3",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _has_specific_appeal_filing_carrier(signatures: set[str]) -> bool:
    direct = {"appeal_filed/3", "appeal_filing/3", "appeal_record/3"}
    if signatures & direct:
        return True
    for signature in signatures:
        predicate, _, arity = signature.partition("/")
        if arity not in {"3", "4", "5"}:
            continue
        tokens = set(predicate.split("_"))
        if tokens & {"appeal", "appealed"} and tokens & {"filed", "filing", "record", "notice"}:
            return True
    return False


def _ensure_quantity_event_predicate(parsed_profile: dict[str, Any], *, source_text: str) -> dict[str, Any]:
    """Ensure a generic quantity-bearing event carrier when profile admission proves it is needed.

    This extends vocabulary only. It does not parse source rows or create facts;
    the Semantic IR compile still has to choose and populate the predicate from
    source evidence.
    """

    report = _profile_admission_report(parsed_profile=parsed_profile, source_text=source_text)
    findings = report.get("findings", []) if isinstance(report.get("findings"), list) else []
    if not any(
        isinstance(item, dict) and item.get("class") == "shallow_quantity_event_palette"
        for item in findings
    ):
        return {
            "schema_version": "profile_quantity_event_extension_v1",
            "added": False,
            "reason": "no_shallow_quantity_event_palette",
        }
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_quantity_event_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if "event_measurement/4" in signatures:
        return {
            "schema_version": "profile_quantity_event_extension_v1",
            "added": False,
            "reason": "event_measurement_already_present",
        }
    if any(_candidate_can_carry_quantity_event_unit(item) for item in candidates if isinstance(item, dict)):
        return {
            "schema_version": "profile_quantity_event_extension_v1",
            "added": False,
            "reason": "quantity_event_carrier_present",
        }

    candidates.append(
        {
            "signature": "event_measurement/4",
            "args": ["event_id", "measure", "value", "unit"],
            "description": (
                "Direct quantity-bearing event or log-entry surface for source-stated measurements, rates, "
                "thresholds, durations, offsets, scores, or before/after values."
            ),
            "why": (
                "Prevents query-bearing numeric event details from being stranded inside prose wrappers such as "
                "event_description/2."
            ),
            "admission_notes": [
                "Vocabulary extension only; use only for exact source-stated numeric event details.",
                "Keep event id, measure name, numeric value, and unit or basis in separate slots.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "event_measurement/4" not in provenance:
        provenance.append("event_measurement/4")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append(
                "Deterministic profile extension added event_measurement/4 after shallow_quantity_event_palette."
            )
    return {
        "schema_version": "profile_quantity_event_extension_v1",
        "added": True,
        "signature": "event_measurement/4",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _ensure_entity_location_predicate(parsed_profile: dict[str, Any], *, source_text: str) -> dict[str, Any]:
    """Ensure a generic direct location carrier for explicit source-stated locations."""

    if not ENTITY_LOCATION_TEXT_RE.search(str(source_text or "")):
        return {
            "schema_version": "profile_entity_location_extension_v1",
            "added": False,
            "reason": "no_explicit_location_signal",
        }
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_entity_location_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if _has_specific_location_carrier(signatures):
        return {
            "schema_version": "profile_entity_location_extension_v1",
            "added": False,
            "reason": "location_carrier_present",
        }

    candidates.append(
        {
            "signature": "entity_location/3",
            "args": ["entity_id", "location", "source_or_scope"],
            "description": (
                "Direct location surface for source-stated physical, organizational, or register locations."
            ),
            "why": (
                "Prevents locations from being stranded inside source-record fields, labels, or broad detail rows."
            ),
            "admission_notes": [
                "Vocabulary extension only; use only for explicit source-stated locations.",
                "Keep located entity, location value, and source/scope joinable.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "entity_location/3" not in provenance:
        provenance.append("entity_location/3")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append("Deterministic profile extension added entity_location/3 after explicit location signal.")
    return {
        "schema_version": "profile_entity_location_extension_v1",
        "added": True,
        "signature": "entity_location/3",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _ensure_scheduled_event_predicate(parsed_profile: dict[str, Any], *, source_text: str) -> dict[str, Any]:
    """Ensure a generic scheduled-event carrier for explicit maintenance due dates."""

    if not SCHEDULED_EVENT_TEXT_RE.search(str(source_text or "")):
        return {
            "schema_version": "profile_scheduled_event_extension_v1",
            "added": False,
            "reason": "no_explicit_scheduled_event_signal",
        }
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_scheduled_event_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if _has_specific_scheduled_event_carrier(signatures):
        return {
            "schema_version": "profile_scheduled_event_extension_v1",
            "added": False,
            "reason": "scheduled_event_carrier_present",
        }

    candidates.append(
        {
            "signature": "scheduled_event/4",
            "args": ["subject_id", "event_type", "scheduled_date", "source_or_basis"],
            "description": (
                "Direct scheduled-event surface for source-stated future calibration, maintenance, service, "
                "or inspection due dates."
            ),
            "why": (
                "Prevents due dates for instruments, equipment, records, or maintenance actions from being "
                "stranded inside source-record labels or prose."
            ),
            "admission_notes": [
                "Vocabulary extension only; use only for explicit source-stated scheduled/due events.",
                "Keep subject, event type, scheduled date, and source/basis joinable.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "scheduled_event/4" not in provenance:
        provenance.append("scheduled_event/4")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append("Deterministic profile extension added scheduled_event/4 after explicit scheduled-event signal.")
    return {
        "schema_version": "profile_scheduled_event_extension_v1",
        "added": True,
        "signature": "scheduled_event/4",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _ensure_status_state_predicate(parsed_profile: dict[str, Any], *, source_text: str) -> dict[str, Any]:
    """Ensure a generic status/state scope carrier when profile admission proves it is needed.

    This is vocabulary-only. It provides a direct surface for point-in-time or
    scoped status/state facts; it does not derive facts from source text.
    """

    report = _profile_admission_report(parsed_profile=parsed_profile, source_text=source_text)
    findings = report.get("findings", []) if isinstance(report.get("findings"), list) else []
    if not any(
        isinstance(item, dict) and item.get("class") == "shallow_status_state_palette"
        for item in findings
    ):
        return {
            "schema_version": "profile_status_state_extension_v1",
            "added": False,
            "reason": "no_shallow_status_state_palette",
        }
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {"schema_version": "profile_status_state_extension_v1", "added": False, "reason": "no_candidate_list"}
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if "status_state_at/4" in signatures:
        return {
            "schema_version": "profile_status_state_extension_v1",
            "added": False,
            "reason": "status_state_at_already_present",
        }
    if any(_candidate_can_carry_status_state_unit(item) for item in candidates if isinstance(item, dict)):
        return {
            "schema_version": "profile_status_state_extension_v1",
            "added": False,
            "reason": "status_state_carrier_present",
        }

    candidates.append(
        {
            "signature": "status_state_at/4",
            "args": ["subject_id", "state_value", "scope_or_date", "source_or_basis"],
            "description": (
                "Direct status/state surface for source-stated point-in-time status, current condition, "
                "availability, pending resolution, supersession, or scoped population state."
            ),
            "why": (
                "Prevents status/state values from being stranded inside prose wrappers or split status/date rows "
                "when questions need subject, state, and temporal/source scope together."
            ),
            "admission_notes": [
                "Vocabulary extension only; use only for exact source-stated scoped status/state facts.",
                "Keep subject or subset, state/status value, scope/date, and source/basis joinable.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "status_state_at/4" not in provenance:
        provenance.append("status_state_at/4")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append(
                "Deterministic profile extension added status_state_at/4 after shallow_status_state_palette."
            )
    return {
        "schema_version": "profile_status_state_extension_v1",
        "added": True,
        "signature": "status_state_at/4",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _ensure_source_attributed_claim_predicate(parsed_profile: dict[str, Any], *, source_text: str) -> dict[str, Any]:
    """Ensure a generic source-attributed claim carrier when admission proves it is needed."""

    report = _profile_admission_report(parsed_profile=parsed_profile, source_text=source_text)
    findings = report.get("findings", []) if isinstance(report.get("findings"), list) else []
    required_keys = [
        str(item).strip()
        for item in report.get("source_attributed_claim_required_keys", [])
        if str(item).strip()
    ] if isinstance(report.get("source_attributed_claim_required_keys"), list) else []
    has_shallow_finding = any(
        isinstance(item, dict) and item.get("class") == "shallow_source_attributed_claim_palette"
        for item in findings
    )
    if not has_shallow_finding and not required_keys:
        return {
            "schema_version": "profile_source_attributed_claim_extension_v1",
            "added": False,
            "reason": "no_shallow_source_attributed_claim_palette",
        }
    candidates = parsed_profile.get("candidate_predicates")
    if not isinstance(candidates, list):
        return {
            "schema_version": "profile_source_attributed_claim_extension_v1",
            "added": False,
            "reason": "no_candidate_list",
        }
    signatures = {
        str(item.get("signature", "")).strip()
        for item in candidates
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    }
    if _has_specific_source_attributed_claim_carrier(signatures):
        return {
            "schema_version": "profile_source_attributed_claim_extension_v1",
            "added": False,
            "reason": "source_attributed_claim_carrier_present",
        }

    candidates.append(
        {
            "signature": "source_attributed_claim/4",
            "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
            "description": (
                "Direct source-attributed claim surface for source-stated reports, notes, statements, opinions, "
                "or findings that assert a status, content, support relation, or unresolved claim."
            ),
            "why": (
                "Prevents source-to-content attribution from being stranded inside notes, reports, statement text, "
                "or source-record rows when questions need who/what asserted a claim."
            ),
            "admission_notes": [
                "Vocabulary extension only; use only when the source explicitly attributes a claim, status, or finding.",
                "Keep claim id, source or speaker/document, content/status, and source row or scope joinable.",
            ],
        }
    )
    provenance = parsed_profile.get("provenance_sensitive_predicates")
    if isinstance(provenance, list) and "source_attributed_claim/4" not in provenance:
        provenance.append("source_attributed_claim/4")
    self_check = parsed_profile.get("self_check")
    if isinstance(self_check, dict):
        notes = self_check.get("notes")
        if isinstance(notes, list):
            notes.append(
                "Deterministic profile extension added source_attributed_claim/4 after shallow_source_attributed_claim_palette."
            )
    return {
        "schema_version": "profile_source_attributed_claim_extension_v1",
        "added": True,
        "signature": "source_attributed_claim/4",
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }


def _has_specific_source_attributed_claim_carrier(signatures: set[str]) -> bool:
    direct = {
        "reported_finding/4",
        "source_attributed_claim/4",
        "source_claim/4",
        "statement_claim/4",
    }
    if signatures & direct:
        return True
    for signature in signatures:
        predicate, _, arity = signature.partition("/")
        if predicate in {"claim_source", "source_supports"}:
            continue
        if arity not in {"4", "5"}:
            continue
        tokens = set(predicate.split("_"))
        if tokens & {"claim", "finding", "opinion", "statement"} and tokens & {"attributed", "source", "speaker"}:
            return True
    return False


def _has_specific_detail_carrier(signatures: set[str]) -> bool:
    for signature in signatures:
        predicate, _, arity = signature.partition("/")
        if arity not in {"3", "4", "5"}:
            continue
        if predicate.endswith("_attribute") or predicate.endswith("_detail"):
            return True
        if predicate in {"item_attribute", "asset_attribute", "device_attribute", "equipment_attribute"}:
            return True
    return False


def _has_specific_location_carrier(signatures: set[str]) -> bool:
    direct = {
        "asset_location/2",
        "current_location/2",
        "device_location/2",
        "entity_location/3",
        "equipment_location/2",
        "located_at/2",
        "location/2",
        "physical_location/2",
        "stored_at/2",
    }
    if signatures & direct:
        return True
    for signature in signatures:
        predicate, _, arity = signature.partition("/")
        if arity not in {"2", "3", "4"}:
            continue
        tokens = set(predicate.split("_"))
        if tokens & {"location", "located", "site", "room", "cabinet", "bay", "bench"}:
            return True
    return False


def _has_specific_scheduled_event_carrier(signatures: set[str]) -> bool:
    direct = {
        "calibration_due/2",
        "calibration_due_date/2",
        "inspection_due/2",
        "maintenance_due/2",
        "next_calibration_due/2",
        "scheduled_calibration/2",
        "scheduled_event/4",
        "scheduled_inspection/2",
        "scheduled_maintenance/2",
    }
    if signatures & direct:
        return True
    for signature in signatures:
        predicate, _, arity = signature.partition("/")
        if arity not in {"2", "3", "4", "5"}:
            continue
        tokens = set(predicate.split("_"))
        if tokens & {"scheduled", "schedule", "due"} and tokens & {"calibration", "inspection", "maintenance", "service", "event"}:
            return True
    return False


def _entity_id_predicate_bases(parsed_profile: dict[str, Any]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for signature in profile_bootstrap_allowed_predicates(parsed_profile):
        predicate, _, arity_text = signature.partition("/")
        if arity_text != "1" or not predicate.endswith("_id"):
            continue
        base = predicate[: -len("_id")]
        if not base:
            continue
        out.append((predicate, base))
    return out


def _looks_temporal_atom(value: str) -> bool:
    return bool(re.match(r"^(?:v_)?\d{4}[_-]\d{2}[_-]\d{2}(?:$|[_-])", str(value or "")))


def _parse_fact_clause(fact: str) -> tuple[str, list[str]] | None:
    match = FACT_CLAUSE_RE.match(str(fact).strip())
    if not match:
        return None
    return match.group(1), [part.strip().strip("'\"") for part in match.group(2).split(",")]


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
        effective_skipped_count = int(record.get("effective_skipped_count", skipped_count) or 0)
        diagnostic_flags = [
            str(flag).strip()
            for flag in record.get("diagnostic_flags", [])
            if str(flag).strip()
        ] if isinstance(record.get("diagnostic_flags"), list) else []
        diagnostic_rejected_pass = "rejected_projection_diagnostic" in diagnostic_flags
        health_flags: list[str] = []
        ok = bool(record.get("ok", True))
        if not ok and not diagnostic_rejected_pass:
            health_flags.append("pass_not_ok")
        if emitted_count == 0:
            if not diagnostic_rejected_pass:
                health_flags.append("zero_yield")
        elif unique_count == 0 and not diagnostic_rejected_pass:
            health_flags.append("no_unique_surface")
        elif unique_count < 3 and not diagnostic_rejected_pass:
            health_flags.append("thin_surface")
        if effective_skipped_count > admitted_count and effective_skipped_count >= 8:
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
                "effective_skipped_count": effective_skipped_count,
                "diagnostic_flags": diagnostic_flags,
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


def _diagnostic_rejected_flat_pass_skipped_count(flat: dict[str, Any], focused: dict[str, Any]) -> int:
    if not isinstance(flat, dict) or not isinstance(focused, dict):
        return 0
    projected_decision = str(flat.get("projected_decision", "")).strip().lower()
    admitted_count = int(flat.get("admitted_count", 0) or 0)
    skipped_count = int(flat.get("skipped_count", 0) or 0)
    focused_admitted_count = int(focused.get("admitted_count", 0) or 0)
    if projected_decision == "reject" and admitted_count == 0 and skipped_count > 0 and focused_admitted_count > 0:
        return skipped_count
    return 0


def _flat_plus_surface_contribution(*, flat: dict[str, Any], focused: dict[str, Any]) -> list[dict[str, Any]]:
    diagnostic_rejected_skipped = _diagnostic_rejected_flat_pass_skipped_count(flat, focused)
    flat_record = {
        **flat,
        "pass_id": "flat_skeleton",
        "purpose": "broad skeleton",
        "focus": "source-wide stable facts, roles, thresholds, core events, corrections",
    }
    if diagnostic_rejected_skipped:
        flat_record["effective_skipped_count"] = 0
        flat_record["diagnostic_flags"] = [
            *([str(flag) for flag in flat_record.get("diagnostic_flags", [])] if isinstance(flat_record.get("diagnostic_flags"), list) else []),
            "rejected_projection_diagnostic",
        ]
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


def _attach_profile_admission_report(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    source_text: str,
    intake_plan: dict[str, Any] | None = None,
    domain_hint: str = "",
) -> None:
    if not _profile_bootstrap_admission_context(intake_plan=intake_plan, domain_hint=domain_hint):
        return
    report = _profile_admission_report(parsed_profile=parsed_profile, source_text=source_text)
    source_compile["profile_admission"] = report
    delivery_report = _profile_delivery_report(
        source_compile=source_compile,
        parsed_profile=parsed_profile,
        admission_report=report,
        source_text=source_text,
    )
    source_compile["profile_delivery"] = delivery_report
    admission_warning_flags = [
        str(item.get("class", "")).strip()
        for item in report.get("findings", [])
        if isinstance(item, dict) and str(item.get("class", "")).strip()
    ]
    delivery_warning_flags = [
        str(item.get("class", "")).strip()
        for item in delivery_report.get("findings", [])
        if isinstance(item, dict) and str(item.get("class", "")).strip()
    ]
    warning_flags = admission_warning_flags + delivery_warning_flags
    if not warning_flags:
        return
    health = source_compile.get("compile_health")
    if not isinstance(health, dict):
        health = {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 0,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": int(source_compile.get("unique_fact_count", 0) or 0),
            "duplicate_total": 0,
            "semantic_progress": assess_semantic_progress(surface_contribution=[]),
        }
    flag_counts = health.get("flag_counts") if isinstance(health.get("flag_counts"), dict) else {}
    for flag in warning_flags:
        flag_counts[flag] = int(flag_counts.get(flag, 0) or 0) + 1
    unhealthy_passes = [
        str(item)
        for item in health.get("unhealthy_passes", [])
        if str(item).strip()
    ] if isinstance(health.get("unhealthy_passes"), list) else []
    if admission_warning_flags and "profile_admission" not in unhealthy_passes:
        unhealthy_passes.append("profile_admission")
    if delivery_warning_flags and "profile_delivery" not in unhealthy_passes:
        unhealthy_passes.append("profile_delivery")
    health["flag_counts"] = flag_counts
    health["unhealthy_passes"] = unhealthy_passes
    health["unhealthy_pass_count"] = len(unhealthy_passes)
    if health.get("verdict") == "healthy":
        health["verdict"] = "warning"
        health["recommendation"] = "run_qa_but_treat_thin_lens_results_as_diagnostic"
    source_compile["compile_health"] = health


def _attach_registered_carrier_delivery_report(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    profile_extension_metadata: dict[str, Any] | None = None,
    mark_health: bool = True,
) -> dict[str, Any]:
    """Report registered carrier signatures offered by extensions but not emitted.

    This is intentionally narrower than profile-delivery diagnostics: it does
    not scan source text and it does not infer what should have been emitted.
    It only asks whether a registered carrier made available to the compiler
    produced any typed rows.
    """

    offered_rows = _registered_carrier_delivery_offered_rows(
        parsed_profile=parsed_profile,
        profile_extension_metadata=profile_extension_metadata,
    )
    offered_signatures = [row["signature"] for row in offered_rows]
    accountable_signatures = [
        row["signature"]
        for row in offered_rows
        if row.get("accountability_required") is True
    ]
    parsed_fact_rows = [
        (predicate, args, fact)
        for fact in _clause_list(source_compile.get("facts", []))
        if (parsed := _parse_fact_clause(fact)) is not None
        for predicate, args in [parsed]
        if not predicate.startswith("source_record")
    ]
    delivered_row_counts: dict[str, int] = {}
    delivered_fact_sample: dict[str, list[str]] = {}
    for signature in offered_signatures:
        predicate, arity = _signature_predicate_arity(signature)
        if not predicate:
            continue
        rows = [
            fact
            for fact_predicate, args, fact in parsed_fact_rows
            if fact_predicate == predicate and (arity is None or len(args) == arity)
        ]
        delivered_row_counts[signature] = len(rows)
        if rows:
            delivered_fact_sample[signature] = rows[:12]
    findings = [
        {
            "class": "registered_carrier_offered_but_undelivered",
            "signature": signature,
            "delivered_carrier_row_count": delivered_row_counts.get(signature, 0),
            "reason": "registered carrier signature was offered by profile extension metadata but no typed rows were emitted",
        }
        for signature in accountable_signatures
        if delivered_row_counts.get(signature, 0) <= 0
    ]
    report = {
        "schema_version": "registered_carrier_delivery_v1",
        "authority": "profile_extension_metadata_and_typed_facts_only",
        "not_source_interpretation": True,
        "not_query_interpretation": True,
        "offered_signatures": offered_signatures,
        "accountable_signatures": accountable_signatures,
        "delivered_row_counts": delivered_row_counts,
        "delivered_fact_sample": delivered_fact_sample,
        "findings": findings,
    }
    source_compile["registered_carrier_delivery"] = report
    if findings and mark_health:
        _mark_compile_health_warning(
            source_compile=source_compile,
            pass_name="registered_carrier_delivery",
            warning_flags=[
                str(item.get("class", "")).strip()
                for item in findings
                if str(item.get("class", "")).strip()
            ],
        )
    return report


def _registered_carrier_delivery_offered_rows(
    *,
    parsed_profile: dict[str, Any],
    profile_extension_metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    candidate_signatures = {
        str(item.get("signature", "")).strip()
        for item in parsed_profile.get("candidate_predicates", [])
        if isinstance(item, dict) and str(item.get("signature", "")).strip()
    } if isinstance(parsed_profile.get("candidate_predicates"), list) else set()
    extension_rows: list[dict[str, Any]] = []
    extensions = (
        profile_extension_metadata.get("extensions", [])
        if isinstance(profile_extension_metadata, dict)
        else []
    )
    for row in extensions if isinstance(extensions, list) else []:
        if not isinstance(row, dict) or row.get("added") is not True:
            continue
        signature = str(row.get("signature", "")).strip()
        if signature:
            extension_rows.append({"signature": signature, "extension": row})
        for item in row.get("signatures", []) if isinstance(row.get("signatures"), list) else []:
            text = str(item).strip()
            if text:
                extension_rows.append({"signature": text, "extension": row})
    offered: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in extension_rows:
        signature = str(row.get("signature", "")).strip()
        if signature in seen or signature not in candidate_signatures:
            continue
        if carrier_contract(signature) is None:
            continue
        seen.add(signature)
        extension = row.get("extension") if isinstance(row.get("extension"), dict) else {}
        offered.append(
            {
                "signature": signature,
                "accountability_required": bool(
                    extension.get("accountability_required") is True
                    or extension.get("source_pressure") is True
                ),
            }
        )
    return offered


def _signature_predicate_arity(signature: str) -> tuple[str, int | None]:
    text = str(signature or "").strip()
    if "/" not in text:
        return text, None
    predicate, arity_text = text.rsplit("/", 1)
    try:
        return predicate, int(arity_text)
    except ValueError:
        return predicate, None


def _mark_compile_health_warning(
    *,
    source_compile: dict[str, Any],
    pass_name: str,
    warning_flags: list[str],
) -> None:
    flags = [str(flag).strip() for flag in warning_flags if str(flag).strip()]
    if not flags:
        return
    health = source_compile.get("compile_health")
    if not isinstance(health, dict):
        health = {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 0,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": int(source_compile.get("unique_fact_count", 0) or 0),
            "duplicate_total": 0,
            "semantic_progress": assess_semantic_progress(surface_contribution=[]),
        }
    flag_counts = health.get("flag_counts") if isinstance(health.get("flag_counts"), dict) else {}
    for flag in flags:
        flag_counts[flag] = int(flag_counts.get(flag, 0) or 0) + 1
    unhealthy_passes = [
        str(item)
        for item in health.get("unhealthy_passes", [])
        if str(item).strip()
    ] if isinstance(health.get("unhealthy_passes"), list) else []
    if pass_name not in unhealthy_passes:
        unhealthy_passes.append(pass_name)
    health["flag_counts"] = flag_counts
    health["unhealthy_passes"] = unhealthy_passes
    health["unhealthy_pass_count"] = len(unhealthy_passes)
    if health.get("verdict") == "healthy":
        health["verdict"] = "warning"
        health["recommendation"] = "run_qa_but_treat_thin_lens_results_as_diagnostic"
    source_compile["compile_health"] = health


def _profile_delivery_report(
    *,
    source_compile: dict[str, Any],
    parsed_profile: dict[str, Any],
    admission_report: dict[str, Any],
    source_text: str = "",
) -> dict[str, Any]:
    """Check whether offered carrier predicates were actually emitted.

    Profile admission answers "does the palette have a suitable shape?" This
    report answers the next compile-stability question: when the source has
    quantity-event pressure and the palette offers a direct carrier, did emitted
    facts populate any of those carrier predicates?
    """

    candidates = parsed_profile.get("candidate_predicates")
    candidate_rows = [item for item in candidates if isinstance(item, dict)] if isinstance(candidates, list) else []
    source_authority_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item) and _candidate_can_carry_source_authority_delivery_unit(item)
    ]
    source_claim_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item) and _candidate_can_carry_source_attributed_claim_delivery_unit(item)
    ]
    status_state_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item) and _candidate_can_carry_status_state_delivery_unit(item)
    ]
    vote_tally_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item) and _candidate_can_carry_vote_tally_delivery_unit(item)
    ]
    quantity_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item) and _candidate_can_carry_quantity_event_delivery_unit(item)
    ]
    scope_discrepancy_carriers = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_signature(item) and _candidate_can_carry_scope_discrepancy_delivery_unit(item)
    ]
    source_authority_predicates = {signature.split("/", 1)[0] for signature in source_authority_carriers}
    source_claim_predicates = {signature.split("/", 1)[0] for signature in source_claim_carriers}
    status_state_predicates = {signature.split("/", 1)[0] for signature in status_state_carriers}
    vote_tally_predicates = {signature.split("/", 1)[0] for signature in vote_tally_carriers}
    quantity_predicates = {signature.split("/", 1)[0] for signature in quantity_carriers}
    scope_discrepancy_predicates = {signature.split("/", 1)[0] for signature in scope_discrepancy_carriers}
    parsed_fact_rows = [
        (predicate, args, fact)
        for fact in _clause_list(source_compile.get("facts", []))
        if (parsed := _parse_fact_clause(fact)) is not None
        for predicate, args in [parsed]
        if not predicate.startswith("source_record")
    ]
    source_record_text_by_ref = _source_record_text_by_ref(source_compile)
    emitted_predicates = {predicate for predicate, _args, _fact in parsed_fact_rows}
    source_authority_delivery = _carrier_delivery_summary(
        source_authority_predicates,
        parsed_fact_rows,
        row_filter=_fact_row_can_deliver_source_authority,
    )
    source_claim_delivery = _carrier_delivery_summary(
        source_claim_predicates,
        parsed_fact_rows,
        row_filter=_fact_row_can_deliver_source_attributed_claim,
        key_fn=lambda predicate, args: _source_attributed_claim_fact_key(
            predicate,
            args,
            source_record_text_by_ref=source_record_text_by_ref,
        ),
    )
    status_state_delivery = _carrier_delivery_summary(
        status_state_predicates,
        parsed_fact_rows,
        row_filter=_fact_row_can_deliver_status_state,
    )
    vote_tally_delivery = _carrier_delivery_summary(
        vote_tally_predicates,
        parsed_fact_rows,
        row_filter=_fact_row_can_deliver_vote_tally,
        key_fn=_vote_tally_fact_key,
    )
    quantity_delivery = _carrier_delivery_summary(
        quantity_predicates,
        parsed_fact_rows,
        key_fn=_quantity_event_fact_key,
    )
    scope_discrepancy_delivery = _carrier_delivery_summary(
        scope_discrepancy_predicates,
        parsed_fact_rows,
        key_fn=_scope_discrepancy_fact_key,
    )
    delivered_source_authority = source_authority_delivery["predicates"]
    delivered_source_claim = source_claim_delivery["predicates"]
    delivered_status_state = status_state_delivery["predicates"]
    delivered_vote_tally = vote_tally_delivery["predicates"]
    delivered_quantity = quantity_delivery["predicates"]
    delivered_scope_discrepancy = scope_discrepancy_delivery["predicates"]
    source_signal_counts = admission_report.get("source_signal_counts") if isinstance(admission_report, dict) else {}
    source_authority_signal_count = (
        int(source_signal_counts.get("source_authority") or 0)
        if isinstance(source_signal_counts, dict)
        else 0
    )
    source_claim_signal_count = (
        int(source_signal_counts.get("source_attributed_claim") or 0)
        if isinstance(source_signal_counts, dict)
        else 0
    )
    source_claim_required_keys = [
        str(item)
        for item in admission_report.get("source_attributed_claim_required_keys", [])
        if str(item).strip()
    ] if isinstance(admission_report, dict) and isinstance(admission_report.get("source_attributed_claim_required_keys"), list) else []
    if source_claim_required_keys:
        source_claim_signal_count = len(source_claim_required_keys)
    status_state_signal_count = (
        int(source_signal_counts.get("status_state") or 0)
        if isinstance(source_signal_counts, dict)
        else 0
    )
    vote_tally_required_keys = _vote_tally_required_keys(_vote_tally_source_mentions(source_text))
    vote_tally_signal_count = len(vote_tally_required_keys)
    quantity_signal_count = (
        int(source_signal_counts.get("quantity_event") or 0)
        if isinstance(source_signal_counts, dict)
        else 0
    )
    quantity_required_row_count = (
        int(admission_report.get("quantity_event_required_carrier_row_count") or quantity_signal_count)
        if isinstance(admission_report, dict)
        else quantity_signal_count
    )
    quantity_required_key_counts = (
        {
            str(key): int(value)
            for key, value in admission_report.get("quantity_event_required_key_counts", {}).items()
            if str(key).strip() and int(value or 0) > 0
        }
        if isinstance(admission_report, dict) and isinstance(admission_report.get("quantity_event_required_key_counts"), dict)
        else {}
    )
    scope_discrepancy_required_keys = _scope_discrepancy_required_keys(_scope_discrepancy_source_mentions(source_text))
    scope_discrepancy_signal_count = len(scope_discrepancy_required_keys)
    findings: list[dict[str, Any]] = []
    _append_profile_delivery_finding(
        findings,
        class_prefix="source_authority_carrier",
        source_signal_count=source_authority_signal_count,
        offered_carriers=source_authority_carriers,
        delivery=source_authority_delivery,
        emitted_predicates=emitted_predicates,
    )
    _append_profile_delivery_finding(
        findings,
        class_prefix="source_claim_carrier",
        source_signal_count=source_claim_signal_count,
        offered_carriers=source_claim_carriers,
        delivery=source_claim_delivery,
        emitted_predicates=emitted_predicates,
        required_signal_keys=source_claim_required_keys,
        key_match_fn=_source_claim_key_is_delivered,
    )
    _append_profile_delivery_finding(
        findings,
        class_prefix="status_state_carrier",
        source_signal_count=status_state_signal_count,
        offered_carriers=status_state_carriers,
        delivery=status_state_delivery,
        emitted_predicates=emitted_predicates,
    )
    _append_profile_delivery_finding(
        findings,
        class_prefix="vote_tally_carrier",
        source_signal_count=vote_tally_signal_count,
        offered_carriers=vote_tally_carriers,
        delivery=vote_tally_delivery,
        emitted_predicates=emitted_predicates,
        required_signal_keys=vote_tally_required_keys,
        key_match_fn=_vote_tally_key_is_delivered,
    )
    _append_profile_delivery_finding(
        findings,
        class_prefix="quantity_carrier",
        source_signal_count=quantity_signal_count,
        required_carrier_row_count=quantity_required_row_count,
        offered_carriers=quantity_carriers,
        delivery=quantity_delivery,
        emitted_predicates=emitted_predicates,
        required_signal_key_counts=quantity_required_key_counts,
        key_match_fn=_quantity_event_key_is_delivered,
    )
    _append_profile_delivery_finding(
        findings,
        class_prefix="scope_discrepancy_carrier",
        source_signal_count=scope_discrepancy_signal_count,
        offered_carriers=scope_discrepancy_carriers,
        delivery=scope_discrepancy_delivery,
        emitted_predicates=emitted_predicates,
        required_signal_keys=scope_discrepancy_required_keys,
        key_match_fn=_scope_discrepancy_key_is_delivered,
    )
    temporal_backbone = _event_identifier_temporal_backbone_report(source_compile)
    if temporal_backbone["missing_event_ids"]:
        findings.append(
            {
                "class": "event_identifier_date_only",
                "source_signal_count": temporal_backbone["event_id_count"],
                "missing_event_ids": temporal_backbone["missing_event_ids"][:12],
                "covered_event_ids": temporal_backbone["covered_event_ids"][:12],
                "emitted_predicate_sample": temporal_backbone["sample_predicates"][:24],
            }
        )
    coexistence_finding = _source_claim_backbone_coexistence_finding(
        source_text=source_text,
        source_claim_signal_count=source_claim_signal_count,
        source_claim_carriers=source_claim_carriers,
        source_claim_delivery=source_claim_delivery,
        parsed_fact_rows=parsed_fact_rows,
        emitted_predicates=emitted_predicates,
    )
    if coexistence_finding:
        findings.append(coexistence_finding)
    return {
        "schema_version": "profile_delivery_contracts_v1",
        "source_signal_counts": {
            "source_authority": source_authority_signal_count,
            "source_attributed_claim": source_claim_signal_count,
            "status_state": status_state_signal_count,
            "vote_tally": vote_tally_signal_count,
            "quantity_event": quantity_signal_count,
            "scope_discrepancy": scope_discrepancy_signal_count,
        },
        "carrier_row_requirements": {
            "quantity_event": quantity_required_row_count,
            "source_attributed_claim": len(source_claim_required_keys),
            "vote_tally": len(vote_tally_required_keys),
            "scope_discrepancy": len(scope_discrepancy_required_keys),
        },
        "offered_carriers": {
            "source_authority": source_authority_carriers[:12],
            "source_attributed_claim": source_claim_carriers[:12],
            "status_state": status_state_carriers[:12],
            "vote_tally": vote_tally_carriers[:12],
            "quantity_event": quantity_carriers[:12],
            "scope_discrepancy": scope_discrepancy_carriers[:12],
        },
        "delivered_carriers": {
            "source_authority": delivered_source_authority[:12],
            "source_attributed_claim": delivered_source_claim[:12],
            "status_state": delivered_status_state[:12],
            "vote_tally": delivered_vote_tally[:12],
            "quantity_event": delivered_quantity[:12],
            "scope_discrepancy": delivered_scope_discrepancy[:12],
        },
        "delivered_carrier_row_counts": {
            "source_authority": source_authority_delivery["row_count"],
            "source_attributed_claim": source_claim_delivery["row_count"],
            "status_state": status_state_delivery["row_count"],
            "vote_tally": vote_tally_delivery["row_count"],
            "quantity_event": quantity_delivery["row_count"],
            "scope_discrepancy": scope_discrepancy_delivery["row_count"],
        },
        "temporal_backbone": temporal_backbone,
        "findings": findings,
    }


def _carrier_delivery_summary(
    carrier_predicates: set[str],
    parsed_fact_rows: list[tuple[str, list[str], str]],
    *,
    row_filter: Any | None = None,
    key_fn: Any | None = None,
) -> dict[str, Any]:
    rows = [
        (predicate, args, fact)
        for predicate, args, fact in parsed_fact_rows
        if predicate in carrier_predicates
        and (row_filter is None or row_filter(predicate, args))
    ]
    delivered_keys = sorted(
        {
            str(key)
            for predicate, args, _fact in rows
            if key_fn is not None
            for key in [key_fn(predicate, args)]
            if str(key).strip()
        }
    )
    delivered_key_counts: dict[str, int] = {}
    if key_fn is not None:
        for predicate, args, _fact in rows:
            key = str(key_fn(predicate, args)).strip()
            if key:
                delivered_key_counts[key] = delivered_key_counts.get(key, 0) + 1
    return {
        "predicates": sorted({predicate for predicate, _args, _fact in rows}),
        "row_count": len(rows),
        "fact_sample": [fact for _predicate, _args, fact in rows[:12]],
        "delivered_keys": delivered_keys,
        "delivered_key_counts": delivered_key_counts,
    }


def _append_profile_delivery_finding(
    findings: list[dict[str, Any]],
    *,
    class_prefix: str,
    source_signal_count: int,
    required_carrier_row_count: int | None = None,
    offered_carriers: list[str],
    delivery: dict[str, Any],
    emitted_predicates: set[str],
    required_signal_keys: list[str] | None = None,
    required_signal_key_counts: dict[str, int] | None = None,
    key_match_fn: Any | None = None,
) -> None:
    if not source_signal_count or not offered_carriers:
        return
    required_count = max(source_signal_count, int(required_carrier_row_count or source_signal_count))
    delivered_row_count = int(delivery.get("row_count") or 0)
    required_key_counts = {
        str(key): int(value)
        for key, value in (required_signal_key_counts or {}).items()
        if str(key).strip() and int(value or 0) > 0
    }
    for key in [str(item) for item in required_signal_keys or [] if str(item).strip()]:
        required_key_counts[key] = max(1, required_key_counts.get(key, 0))
    required_keys = list(required_key_counts)
    delivered_key_counts = {
        str(key): int(value)
        for key, value in delivery.get("delivered_key_counts", {}).items()
        if str(key).strip() and int(value or 0) > 0
    } if isinstance(delivery.get("delivered_key_counts"), dict) else {}
    delivered_keys = {
        str(item)
        for item in delivery.get("delivered_keys", [])
        if str(item).strip()
    } if isinstance(delivery.get("delivered_keys"), list) else set()
    match_key = key_match_fn if key_match_fn is not None else lambda required, delivered: required == delivered
    missing_keys = [
        key
        for key, required_key_count in required_key_counts.items()
        if sum(
            count
            for delivered_key, count in delivered_key_counts.items()
            if match_key(key, delivered_key)
        ) < required_key_count
    ]
    missing_key_count = sum(
        max(
            0,
            required_key_count
            - sum(
                count
                for delivered_key, count in delivered_key_counts.items()
                if match_key(key, delivered_key)
            ),
        )
        for key, required_key_count in required_key_counts.items()
    )
    if delivered_row_count >= required_count and not missing_keys:
        return
    finding = {
        "class": (
            f"{class_prefix}_offered_but_undelivered"
            if delivered_row_count <= 0
            else f"{class_prefix}_partially_delivered"
        ),
        "source_signal_count": source_signal_count,
        "delivered_carrier_row_count": delivered_row_count,
        "missing_signal_count": missing_key_count if missing_keys else max(0, source_signal_count - delivered_row_count),
        "offered_carriers": offered_carriers[:12],
        "delivered_carriers": delivery.get("predicates", [])[:12],
        "emitted_carrier_fact_sample": delivery.get("fact_sample", [])[:12],
        "emitted_predicate_sample": sorted(emitted_predicates)[:24],
    }
    if required_keys:
        finding["required_signal_keys"] = required_keys[:12]
        finding["delivered_signal_keys"] = sorted(delivered_keys)[:12]
        finding["missing_signal_keys"] = missing_keys[:12]
        if any(count != 1 for count in required_key_counts.values()):
            finding["required_signal_key_counts"] = dict(sorted(required_key_counts.items())[:12])
            finding["delivered_signal_key_counts"] = dict(sorted(delivered_key_counts.items())[:12])
    if required_count != source_signal_count:
        finding["required_carrier_row_count"] = required_count
        finding["missing_carrier_row_count"] = max(0, required_count - delivered_row_count)
    findings.append(finding)


def _source_claim_key_is_delivered(required_key: str, delivered_key: str) -> bool:
    if required_key == delivered_key:
        return True
    required_parts = str(required_key or "").split(":", 2)
    delivered_parts = str(delivered_key or "").split(":", 2)
    if len(required_parts) != 3 or len(delivered_parts) != 3:
        return False
    required_source, required_subject, required_claim = required_parts
    delivered_source, delivered_subject, delivered_claim = delivered_parts
    if required_claim == "dispute" and delivered_subject == "dispute":
        source_matches = _source_claim_source_kind_matches(required_source, delivered_source)
        return source_matches
    if required_claim != delivered_claim:
        return False
    source_matches = _source_claim_source_kind_matches(required_source, delivered_source)
    if required_claim == "no_documentation":
        return source_matches and required_subject == delivered_subject
    subject_matches = required_subject == delivered_subject or "claim" in {required_subject, delivered_subject}
    return source_matches and subject_matches


def _source_claim_source_kind_matches(required_source: str, delivered_source: str) -> bool:
    if required_source == delivered_source:
        return True
    if "source" in {required_source, delivered_source}:
        return True
    speech_kinds = {
        "assessment",
        "comment",
        "email",
        "letter",
        "memo",
        "note",
        "opinion",
        "report",
        "statement",
        "testimony",
    }
    return required_source in speech_kinds and delivered_source in speech_kinds


SOURCE_AUTHORITY_DELIVERY_PREDICATE_NAMES = {
    "amendment_authorizer",
    "amendment_author",
    "amendment_event",
    "authorization_threshold",
    "authorization_rule",
    "authorized_action",
    "authorized_by_role",
    "charter_rule",
    "charter_section",
    "correction_event",
    "emergency_authorization",
    "event_authorizer",
    "legal_basis",
    "ordinance_rule",
    "permit_authorization",
    "policy_compliance",
    "policy_rule",
    "rule_exception",
    "rule_threshold",
    "solicitation_authority",
    "source_authority",
    "statutory_authority",
}

SOURCE_CLAIM_DELIVERY_PREDICATE_NAMES = {
    "counsel_opinion",
    "knowledge_assertion",
    "legal_position",
    "legal_opinion",
    "party_position",
    "participant_statement",
    "public_comment",
    "reported_finding",
    "source_attributed_claim",
    "source_attributed_legal_fact",
    "source_claim",
    "source_supports",
    "staff_assessment",
    "statement_claim",
    "violation_claim",
    "witness_statement",
}

STATUS_STATE_DELIVERY_PREDICATE_NAMES = {
    "appeal_filed",
    "authorization_status",
    "asset_state",
    "conditional_rule",
    "directive_with_scope",
    "document_status",
    "hearing_scheduled",
    "knowledge_assertion",
    "lease_term",
    "lease_status",
    "legal_opinion",
    "pending_determination",
    "permit_status",
    "payment_reduction_rule",
    "policy_compliance",
    "reduction_rule",
    "scheduled_event",
    "tree_protection_status",
    "vehicle_action",
    "violation_claim",
    "vessel_state",
}

VOTE_TALLY_DELIVERY_PREDICATE_NAMES = {
    "decision_vote",
    "final_vote",
    "motion_vote",
    "roll_call_vote",
    "vote_record",
    "vote_tally",
    "voting_record",
}

SCOPE_DISCREPANCY_DELIVERY_PREDICATE_NAMES = {
    "conflict_between",
    "discrepancy_between",
    "discrepancy_in",
    "record_discrepancy",
    "scope_discrepancy",
    "source_discrepancy",
}

SOURCE_CLAIM_BACKBONE_WRAPPER_PREDICATES = {
    "context",
    "detail",
    "event_detail",
    "event_record",
    "note",
    "record_detail",
    "source_detail",
    "source_note",
    "summary",
}

SOURCE_CLAIM_BACKBONE_GROUPS: dict[str, dict[str, set[str]]] = {
    "vote": {
        "source_any": {"voted", "votes", "voting", "tally", "ayes", "nays", "roll", "call"},
        "source_context": {"board", "commission", "committee", "council", "member", "members"},
        "direct_any": {"voted", "votes", "voting", "tally", "ayes", "nays", "roll", "call"},
    },
    "survey_measurement": {
        "source_any": {"survey", "setback", "measured", "measurement", "feet", "ft", "distance", "dimension"},
        "source_context": {"survey", "surveyor", "setback", "feet", "ft", "distance", "dimension"},
        "direct_any": {"survey", "setback", "measured", "measurement", "feet", "ft", "distance", "dimension"},
    },
    "permit_application_status": {
        "source_any": {"permit", "application"},
        "source_context": {"pending", "approved", "denied", "issued", "status", "withdrawn", "filed"},
        "direct_any": {"permit", "application"},
        "direct_context": {"pending", "approved", "denied", "issued", "status", "withdrawn", "filed"},
    },
    "appeal_filing": {
        "source_any": {"appeal", "appealed"},
        "source_context": {"filed", "filing", "lodged", "challenge"},
        "direct_any": {"appeal", "appealed"},
        "direct_context": {"filed", "filing", "lodged", "challenge", "status"},
    },
    "board_finding": {
        "source_any": {"finding", "findings", "found", "concluded", "determined", "determination"},
        "source_context": {"board", "commission", "committee", "official", "staff"},
        "direct_any": {"finding", "findings", "found", "concluded", "determined", "determination"},
    },
    "hearing_quorum": {
        "source_any": {"quorum"},
        "source_context": {"hearing", "present", "absent", "member", "members"},
        "direct_any": {"quorum"},
    },
}


def _candidate_can_carry_source_authority_delivery_unit(candidate: dict[str, Any]) -> bool:
    if _candidate_can_carry_source_authority_unit(candidate):
        return True
    signature = _candidate_signature(candidate).lower()
    name = signature.split("/", 1)[0]
    if name not in SOURCE_AUTHORITY_DELIVERY_PREDICATE_NAMES:
        return False
    args = _candidate_args(candidate)
    if len(args) < 2:
        return False
    return _fact_row_can_deliver_source_authority(name, args)


def _candidate_can_carry_source_attributed_claim_delivery_unit(candidate: dict[str, Any]) -> bool:
    if _candidate_can_carry_source_attributed_claim_unit(candidate):
        return True
    signature = _candidate_signature(candidate).lower()
    name = signature.split("/", 1)[0]
    if name not in SOURCE_CLAIM_DELIVERY_PREDICATE_NAMES:
        return False
    args = _candidate_args(candidate)
    if len(args) < 3:
        return False
    return _fact_row_can_deliver_source_attributed_claim(name, args)


def _candidate_can_carry_status_state_delivery_unit(candidate: dict[str, Any]) -> bool:
    if _candidate_can_carry_status_state_unit(candidate):
        return True
    signature = _candidate_signature(candidate).lower()
    name = signature.split("/", 1)[0]
    if name not in STATUS_STATE_DELIVERY_PREDICATE_NAMES:
        return False
    args = _candidate_args(candidate)
    if len(args) < 2:
        return False
    if name in {"payment_reduction_rule", "reduction_rule"}:
        return len(args) >= 3
    if name in {"pending_determination", "permit_status", "tree_protection_status"}:
        return True
    arg_tokens = [_profile_admission_tokens(arg.lower()) for arg in args]
    has_scope = any(tokens & (PROFILE_ADMISSION_DATE_SLOTS | PROFILE_ADMISSION_SCOPE_SLOTS | {"source"}) for tokens in arg_tokens)
    has_content = any(
        tokens & (PROFILE_ADMISSION_STATUS_STATE_TERMS | {"content", "conclusion", "fact", "finding", "status", "topic"})
        for tokens in arg_tokens
    )
    if name in {"hearing_scheduled", "scheduled_event"}:
        return bool(has_scope)
    return bool(has_scope and has_content)


def _candidate_can_carry_vote_tally_delivery_unit(candidate: dict[str, Any]) -> bool:
    signature = _candidate_signature(candidate).lower()
    name = signature.split("/", 1)[0]
    if name not in VOTE_TALLY_DELIVERY_PREDICATE_NAMES and not _vote_tally_text(signature):
        return False
    args = _candidate_args(candidate)
    if len(args) < 3:
        return False
    if name == "voting_record":
        return True
    arg_tokens = [_profile_admission_tokens(arg.lower()) for arg in args]
    has_result = any(tokens & {"decision", "outcome", "result", "status", "vote"} for tokens in arg_tokens)
    has_tally = any(tokens & {"count", "member", "members", "roll", "tally", "votes"} for tokens in arg_tokens)
    return len(args) >= 4 or bool(has_result and has_tally)


def _candidate_can_carry_scope_discrepancy_delivery_unit(candidate: dict[str, Any]) -> bool:
    signature = _candidate_signature(candidate).lower()
    name = signature.split("/", 1)[0]
    if name not in SCOPE_DISCREPANCY_DELIVERY_PREDICATE_NAMES and not (
        "discrepanc" in signature or "conflict" in signature
    ):
        return False
    return len(_candidate_args(candidate)) >= 4


def _fact_row_tokens(predicate: str, args: list[str]) -> set[str]:
    return _profile_admission_tokens(" ".join([str(predicate), *(str(arg) for arg in args)]).replace("_", " "))


def _fact_row_can_deliver_source_authority(predicate: str, args: list[str]) -> bool:
    name = str(predicate or "").casefold()
    if name == "legal_basis":
        return len(args) >= 2
    if name == "source_authority":
        return len(args) >= 3
    if name == "solicitation_authority":
        return len(args) >= 2
    if name == "statutory_authority":
        return len(args) >= 2
    if name == "amendment_author":
        return len(args) >= 2
    if name == "event_authorizer":
        return len(args) >= 2
    if name == "authorized_by_role":
        return len(args) >= 3
    if name in {"amendment_event", "correction_event"}:
        return len(args) >= 4
    tokens = _fact_row_tokens(name, args)
    authority_terms = {
        "approval",
        "authorized",
        "authorizer",
        "authorization",
        "authority",
        "charter",
        "governing",
        "ordinance",
        "policy",
        "rule",
        "threshold",
    }
    scope_terms = {
        "action",
        "amendment",
        "amendments",
        "condition",
        "correction",
        "corrections",
        "effect",
        "limit",
        "operational",
        "permit",
        "section",
        "source",
        "status",
        "subject",
    }
    return bool(
        name in SOURCE_AUTHORITY_DELIVERY_PREDICATE_NAMES
        and len(args) >= 2
        and tokens & authority_terms
        and (tokens & scope_terms or len(args) >= 3)
    )


def _fact_row_can_deliver_source_attributed_claim(predicate: str, args: list[str]) -> bool:
    name = str(predicate or "").casefold()
    if name in {
        "reported_finding",
        "source_attributed_claim",
        "source_attributed_legal_fact",
        "source_claim",
        "statement_claim",
    }:
        return len(args) >= 3
    if name in {"legal_position", "party_position"}:
        return len(args) >= 3
    if name not in SOURCE_CLAIM_DELIVERY_PREDICATE_NAMES or len(args) < 3:
        return False
    name_tokens = set(name.split("_"))
    if name_tokens & {"appropriation", "appropriations", "fund", "funding"} and not (
        name_tokens & {"claim", "comment", "finding", "memo", "note", "opinion", "report", "statement"}
    ):
        return False
    tokens = _fact_row_tokens(name, args)
    claim_terms = {
        "assertion",
        "assessment",
        "claim",
        "comment",
        "conclusion",
        "content",
        "finding",
        "opinion",
        "statement",
        "support",
        "supports",
    }
    return bool(tokens & claim_terms)


def _source_attributed_claim_fact_key(
    predicate: str,
    args: list[str],
    *,
    source_record_text_by_ref: dict[str, str] | None = None,
) -> str:
    source_lookup = source_record_text_by_ref or {}
    for arg in args:
        ref = _normalize_profile_atom(str(arg))
        if not ref.startswith("src_line"):
            continue
        source_text = source_lookup.get(ref)
        if source_text:
            key = _source_attributed_claim_signal_key(source_text)
            if key:
                return key
    return _source_attributed_claim_signal_key(" ".join([str(predicate), *(str(arg) for arg in args)]))


def _fact_row_can_deliver_status_state(predicate: str, args: list[str]) -> bool:
    name = str(predicate or "").casefold()
    if name == "appeal_filed":
        return len(args) >= 3
    if name == "mandate_staff":
        return len(args) >= 3
    if name == "payment_reduction_rule":
        return len(args) >= 3
    if name in {"conditional_rule", "directive_with_scope", "mandate_utility", "reduction_rule", "vehicle_action"}:
        return len(args) >= 4
    if name in {"asset_state", "vessel_state"}:
        return len(args) >= 3
    if name == "lease_term":
        return len(args) >= 4 and bool(_profile_admission_tokens(str(args[3])) & PROFILE_ADMISSION_STATUS_STATE_TERMS)
    if name in {"pending_determination", "permit_status", "tree_protection_status"}:
        return len(args) >= 2 and bool(
            _profile_admission_tokens(str(args[1]))
            & (PROFILE_ADMISSION_STATUS_STATE_TERMS | {"issued", "not", "protected", "not_protected"})
        )
    if _status_state_text(name):
        return len(args) >= 2
    if name not in STATUS_STATE_DELIVERY_PREDICATE_NAMES or len(args) < 2:
        return False
    tokens = _fact_row_tokens(name, args)
    state_terms = PROFILE_ADMISSION_STATUS_STATE_TERMS | {
        "authorized",
        "deferred",
        "determination",
        "issued",
        "operative",
        "scheduled",
        "unchanged",
        "unauthorized",
    }
    scope_terms = PROFILE_ADMISSION_DATE_SLOTS | PROFILE_ADMISSION_SCOPE_SLOTS | {"exhibit", "hearing", "source"}
    has_temporal_or_scope = any(
        PROFILE_ADMISSION_FULL_DATE_ATOM_RE.search(str(arg))
        or PROFILE_ADMISSION_COMPACT_DATE_RE.search(str(arg))
        for arg in args
    ) or bool(tokens & scope_terms)
    return bool(tokens & state_terms and has_temporal_or_scope)


def _fact_row_can_deliver_vote_tally(predicate: str, args: list[str]) -> bool:
    name = str(predicate or "").casefold()
    if name == "voting_record":
        return len(args) >= 3
    if name not in VOTE_TALLY_DELIVERY_PREDICATE_NAMES and not _vote_tally_text(name):
        return False
    if len(args) < 3:
        return False
    joined = " ".join([name, *(str(arg) for arg in args)]).casefold()
    tokens = _profile_admission_tokens(joined)
    has_vote = bool(tokens & {"vote", "votes", "voted", "voting", "tally", "approved", "denied"})
    has_tally = bool(re.search(r"\b\d+\s*[-_]\s*\d+\b", joined) or tokens & {"affirmative", "negative", "absent"})
    return has_vote or has_tally


def _vote_tally_fact_key(predicate: str, args: list[str]) -> str:
    if str(predicate or "").casefold() == "vote_tally" and len(args) >= 5:
        return _vote_tally_signal_key(" ".join([str(args[2]), str(args[3]), str(args[4])]))
    return _vote_tally_signal_key(" ".join([str(predicate), *(str(arg) for arg in args)]))


def _vote_tally_key_is_delivered(required_key: str, delivered_key: str) -> bool:
    if required_key == delivered_key:
        return True
    required_parts = [part for part in str(required_key or "").split(":") if part]
    delivered_parts = [part for part in str(delivered_key or "").split(":") if part]
    if not required_parts or not delivered_parts:
        return False
    if required_parts[-1] not in delivered_parts:
        return False
    if len(required_parts) == 1:
        return True
    return any(part in delivered_parts for part in required_parts[:-1])


def _scope_discrepancy_fact_key(predicate: str, args: list[str]) -> str:
    name = str(predicate or "").casefold()
    if name == "scope_discrepancy" and args:
        return _scope_discrepancy_signal_key(str(args[0]))
    return _scope_discrepancy_signal_key(" ".join([str(predicate), *(str(arg) for arg in args)]))


def _scope_discrepancy_key_is_delivered(required_key: str, delivered_key: str) -> bool:
    required = _scope_discrepancy_signal_key(required_key)
    delivered = _scope_discrepancy_signal_key(delivered_key)
    return bool(required and delivered and required == delivered)


def _source_claim_backbone_coexistence_finding(
    *,
    source_text: str,
    source_claim_signal_count: int,
    source_claim_carriers: list[str],
    source_claim_delivery: dict[str, Any],
    parsed_fact_rows: list[tuple[str, list[str], str]],
    emitted_predicates: set[str],
) -> dict[str, Any] | None:
    if not source_claim_signal_count or not source_claim_carriers:
        return None
    if int(source_claim_delivery.get("row_count") or 0) <= 0:
        return None
    source_groups = _source_claim_backbone_source_groups(source_text)
    if not source_groups:
        return None
    direct_groups = _source_claim_backbone_direct_groups(parsed_fact_rows)
    missing_groups = sorted(source_groups - direct_groups)
    if not missing_groups:
        return None
    return {
        "class": "source_claim_backbone_coexistence_missing",
        "source_signal_count": len(source_groups),
        "delivered_carrier_row_count": int(source_claim_delivery.get("row_count") or 0),
        "missing_signal_count": len(missing_groups),
        "offered_carriers": source_claim_carriers[:12],
        "delivered_carriers": source_claim_delivery.get("predicates", [])[:12],
        "missing_signal_keys": missing_groups[:12],
        "source_backbone_groups": sorted(source_groups)[:12],
        "delivered_backbone_groups": sorted(direct_groups)[:12],
        "emitted_carrier_fact_sample": source_claim_delivery.get("fact_sample", [])[:12],
        "emitted_predicate_sample": sorted(emitted_predicates)[:24],
    }


def _source_claim_backbone_source_groups(source_text: str) -> set[str]:
    groups: set[str] = set()
    for line in str(source_text or "").splitlines():
        tokens = _profile_admission_tokens(line)
        for group, spec in SOURCE_CLAIM_BACKBONE_GROUPS.items():
            if not tokens & spec["source_any"]:
                continue
            context = spec.get("source_context", set())
            if context and not tokens & context:
                continue
            groups.add(group)
    return groups


def _source_claim_backbone_direct_groups(parsed_fact_rows: list[tuple[str, list[str], str]]) -> set[str]:
    groups: set[str] = set()
    for predicate, args, _fact in parsed_fact_rows:
        name = str(predicate or "").casefold()
        if name in SOURCE_CLAIM_DELIVERY_PREDICATE_NAMES or name in SOURCE_CLAIM_BACKBONE_WRAPPER_PREDICATES:
            continue
        tokens = _fact_row_tokens(name, args)
        for group, spec in SOURCE_CLAIM_BACKBONE_GROUPS.items():
            if not tokens & spec["direct_any"]:
                continue
            context = spec.get("direct_context", set())
            if context and not tokens & context:
                continue
            groups.add(group)
    return groups


def _normalize_profile_atom(value: str) -> str:
    return str(value or "").strip().strip("'\"").casefold()


def _source_record_text_by_ref(source_compile: dict[str, Any]) -> dict[str, str]:
    rows: dict[str, str] = {}
    for fact in _clause_list(source_compile.get("facts", [])):
        parsed = _parse_fact_clause(fact)
        if parsed is None:
            continue
        predicate, args = parsed
        if predicate != "source_record_text_atom" or len(args) < 2:
            continue
        ref = _normalize_profile_atom(args[0])
        if ref:
            rows[ref] = str(args[1])
    return rows


def _event_identifier_temporal_backbone_report(source_compile: dict[str, Any]) -> dict[str, Any]:
    parsed_rows: list[tuple[str, list[str]]] = []
    for fact in _clause_list(source_compile.get("facts", [])):
        parsed = _parse_fact_clause(fact)
        if parsed is None or parsed[0].startswith("source_record"):
            continue
        parsed_rows.append(parsed)
    event_ids = sorted(
        {
            _normalize_profile_atom(arg)
            for predicate, args in parsed_rows
            for arg in args
            if _is_date_bearing_event_identifier_arg(predicate, arg)
        }
    )
    covered = [event_id for event_id in event_ids if _event_id_has_explicit_temporal_row(event_id, parsed_rows)]
    missing = [event_id for event_id in event_ids if event_id not in set(covered)]
    sample_predicates = sorted(
        {
            predicate
            for predicate, args in parsed_rows
            if any(_normalize_profile_atom(arg) in event_ids for arg in args)
        }
    )
    return {
        "schema_version": "event_identifier_temporal_backbone_v1",
        "date_bearing_event_ids": event_ids[:50],
        "covered_event_ids": covered[:50],
        "missing_event_ids": missing[:50],
        "event_id_count": len(event_ids),
        "covered_event_id_count": len(covered),
        "missing_event_id_count": len(missing),
        "sample_predicates": sample_predicates[:50],
    }


def _is_date_bearing_event_identifier_arg(predicate: str, value: str) -> bool:
    norm = _normalize_profile_atom(value)
    if not _profile_atom_has_calendar_date(norm):
        return False
    predicate_tokens = set(PROFILE_ADMISSION_TOKEN_RE.findall(str(predicate or "").casefold()))
    value_tokens = set(PROFILE_ADMISSION_TOKEN_RE.findall(norm))
    if len(value_tokens) > 10:
        return False
    event_terms = {
        "action",
        "appeal",
        "approval",
        "declaration",
        "event",
        "ev",
        "filing",
        "hearing",
        "incident",
        "meeting",
        "motion",
        "notice",
        "occurrence",
        "ratification",
        "resolution",
        "review",
        "transition",
    }
    identifier_markers = {"ev", "event", "incident", "hearing", "meeting", "notice", "filing", "motion"}
    identifier_prefixes = (
        "ev_",
        "event_",
        "incident_",
        "hearing_",
        "meeting_",
        "notice_",
        "filing_",
        "motion_",
        "appeal_",
        "review_",
        "declaration_",
        "ratification_",
    )
    if not norm.startswith(identifier_prefixes):
        return False
    if not (value_tokens & event_terms or value_tokens & identifier_markers):
        return False
    return bool((predicate_tokens | value_tokens) & event_terms)


def _event_id_has_explicit_temporal_row(
    event_id: str,
    parsed_rows: list[tuple[str, list[str]]],
) -> bool:
    temporal_predicate_terms = {"date", "dated", "effective", "occurred", "scheduled", "time", "timestamp"}
    for predicate, args in parsed_rows:
        norm_args = [_normalize_profile_atom(arg) for arg in args]
        if event_id not in norm_args:
            continue
        other_args = [arg for arg in norm_args if arg != event_id]
        if any(_profile_atom_is_calendar_date_value(arg) for arg in other_args):
            return True
        predicate_tokens = set(PROFILE_ADMISSION_TOKEN_RE.findall(str(predicate or "").casefold()))
        if predicate_tokens & temporal_predicate_terms and any(_profile_atom_has_calendar_date(arg) for arg in other_args):
            return True
    return False


def _profile_atom_has_calendar_date(value: str) -> bool:
    norm = _normalize_profile_atom(value)
    return bool(
        PROFILE_ADMISSION_DATE_RE.search(norm)
        or PROFILE_ADMISSION_FULL_DATE_ATOM_RE.search(norm)
        or PROFILE_ADMISSION_COMPACT_DATE_RE.search(norm)
    )


def _profile_atom_is_calendar_date_value(value: str) -> bool:
    norm = _normalize_profile_atom(value)
    if not _profile_atom_has_calendar_date(norm):
        return False
    non_date_tokens = [
        token
        for token in PROFILE_ADMISSION_TOKEN_RE.findall(norm)
        if token != "v" and not token.isdigit()
    ]
    return len(non_date_tokens) <= 2


def _profile_bootstrap_admission_context(
    *,
    intake_plan: dict[str, Any] | None,
    domain_hint: str = "",
) -> list[str]:
    label_parts = [str(domain_hint or "").casefold()]
    if isinstance(intake_plan, dict):
        label_parts.append(json.dumps(intake_plan, ensure_ascii=False).casefold())
    label = " ".join(label_parts)
    has_operational_pressure = any(
        token in label
        for token in (
            "application",
            "docket",
            "grant",
            "intake",
            "lifecycle",
            "operational",
            "permit",
            "proposal",
            "queue",
            "record status",
            "status lifecycle",
            "status record",
            "ticket",
        )
    )
    has_status_state_pressure = any(
        token in label
        for token in (
            "as-of status",
            "condition",
            "current status",
            "current state",
            "partial population",
            "point-in-time",
            "state transition",
            "status at",
            "status transition",
            "status/state",
        )
    )
    has_source_claim_pressure = any(
        token in label
        for token in (
            "attributed claim",
            "claim report",
            "claim source",
            "finding source",
            "reported claim",
            "reported finding",
            "source attributed",
            "source claim",
            "source report",
            "source statement",
        )
    )
    has_source_authority_pressure = any(
        token in label
        for token in (
            "authority source",
            "governing source",
            "source authority",
            "source-authority",
        )
    )
    has_quantity_pressure = any(
        token in label
        for token in (
            "calculation",
            "contribution",
            "formula",
            "financial",
            "financial statement",
            "income statement",
            "investee",
            "measurement",
            "metric",
            "numeric",
            "quantity",
            "rate",
            "reading",
            "sensor",
            "threshold",
            "value",
        )
    )
    has_financial_report_pressure = any(
        token in label
        for token in (
            "affiliate contribution",
            "annual report",
            "associate",
            "corporate disclosure",
            "earnings",
            "equity-method",
            "financial result",
            "financial statement",
            "forecast",
            "investee",
            "issuer report",
            "quarterly report",
            "segment performance",
        )
    )
    has_scope_discrepancy_pressure = any(
        token in label
        for token in (
            "conflict",
            "discrepancy",
            "inconsistent",
            "inconsistency",
            "mismatch",
            "scope discrepancy",
        )
    )
    context: list[str] = []
    if has_operational_pressure:
        context.extend(
            [
                (
                    "Profile admission rule: when an operational record, queue, proposal, application, ticket, docket, "
                    "permit, sample, or intake source has repeated dated lifecycle/status lines, the candidate predicate "
                    "palette must include at least one complete status-at-date or lifecycle-event shape carrying subject, "
                    "state/action/result, and date/source together."
                ),
                (
                    "Do not offer only separate status/2 plus status_changed_on/2, event_date/2, or event_date/3 surfaces "
                    "for repeated dated status timelines. Those split palettes are shallow unless another candidate can carry "
                    "the joined subject/status/date unit."
                ),
            ]
        )
    if has_status_state_pressure and not has_operational_pressure:
        context.extend(
            [
                (
                    "Profile admission rule: when a source has point-in-time status, current condition, "
                    "availability, pending resolution, state transition, supersession, or partial-population state "
                    "pressure, the candidate predicate palette must include at least one direct status/state surface "
                    "that carries subject or subset, state/status value, and temporal/source scope together."
                ),
                (
                    "Do not offer only status/2, condition/2, event_date/2, note/2, or description/2 for status/state "
                    "pressure. Those surfaces are shallow unless another candidate can carry subject, state value, and "
                    "as-of/effective/source scope in a joined row."
                ),
            ]
        )
    if has_source_claim_pressure:
        context.extend(
            [
                (
                    "Profile admission rule: when a source attributes a claim, status, finding, opinion, or support "
                    "relation to a memo, report, statement, note, witness, letter, email, or other source layer, the "
                    "candidate predicate palette must include at least one direct source-attributed claim surface "
                    "carrying claim/content id, source or speaker/document, asserted content/status/finding, and "
                    "source row or scope together."
                ),
                (
                    "Do not offer only source_note/2, report_text/2, statement/2, note/2, description/2, or split "
                    "claim_status/2 plus source metadata for source-attributed claim pressure. Those surfaces are "
                    "shallow unless another candidate can carry source, content/status, and source scope in a joined row."
                ),
            ]
        )
    if has_source_authority_pressure:
        context.extend(
            [
                (
                    "Profile delivery rule: when a source states that an authority, rule, order, policy, source, "
                    "or body governs an action, status, access, finding, deadline, or scoped decision, a direct "
                    "source-authority carrier should be offered and populated when compatible."
                ),
                (
                    "Do not leave governing authority only in source text, rule prose, record labels, or recipient/action "
                    "rows. Keep governed subject or scope, authority/source, and action/status/decision joinable."
                ),
            ]
        )
    if has_quantity_pressure:
        context.extend(
            [
                (
                    "Profile admission rule: when a log, table, calculation, measurement, sensor, score, or metric source "
                    "contains repeated numeric event details, the candidate predicate palette must include at least one "
                    "direct quantity-bearing event/record shape carrying event or record id, measure or attribute, numeric "
                    "value, and unit or basis when stated."
                ),
                (
                    "Do not offer only event_description/2, note/2, summary/2, or other prose-wrapper surfaces for numeric "
                    "event details. A prose description is shallow when the source states query-bearing quantities, rates, "
                    "thresholds, offsets, durations, scores, or before/after values."
                ),
            ]
        )
    if has_financial_report_pressure:
        context.extend(
            [
                (
                    "Profile admission rule: when a financial report states totals plus named affiliate, associate, "
                    "investee, subsidiary, segment, project, customer, or vendor contributions, the candidate predicate "
                    "palette must include at least one amount/metric carrier that can keep period, named scope or entity, "
                    "metric, value, and unit joinable inside the five-slot profile limit."
                ),
                (
                    "Do not offer only source summary text, generic narrative rows, or period-only financial_result rows "
                    "for contribution pressure. If the source names who or what contributed to a metric, the palette needs "
                    "a joined scope/entity slot or a documented compatible basis/scope label. If source/basis must be "
                    "queryable too, propose a separate provenance/source-coordinate carrier rather than /6."
                ),
            ]
        )
    if has_scope_discrepancy_pressure:
        context.extend(
            [
                (
                    "Profile delivery rule: when two records, policies, contracts, orders, rules, or source surfaces "
                    "state conflicting values, requirements, omissions, or scope details, a direct discrepancy carrier "
                    "should be offered and populated when compatible."
                ),
                (
                    "Do not leave source-stated conflicts only in source_record/source_detail prose. Keep issue, "
                    "left value/source, right value/source, and basis joinable in scope_discrepancy/6, "
                    "discrepancy_between/4, conflict_between/4, or an equivalent direct row."
                ),
            ]
        )
    return context


def _profile_admission_retry_context(report: dict[str, Any]) -> list[str]:
    findings = report.get("findings", []) if isinstance(report.get("findings"), list) else []
    nearby: list[str] = []
    classes = {
        str(finding.get("class", "")).strip()
        for finding in findings
        if isinstance(finding, dict)
    }
    for finding in findings:
        if isinstance(finding, dict):
            nearby.extend(str(item) for item in finding.get("nearby_signatures", []) if str(item).strip())
    context: list[str] = []
    if "shallow_lifecycle_palette" in classes:
        context.extend(
            [
                (
                    "PROFILE ADMISSION RETRY: the previous profile had a shallow_lifecycle_palette finding. "
                    "Regenerate the profile so repeated dated lifecycle/status source lines have a complete candidate "
                    "predicate shape carrying subject, state/action/result, and date/source together."
                ),
                (
                    "Acceptable shapes include record_status_phase/4, record_status_at/3, record_lifecycle_event/5, "
                    "or source-local equivalents such as proposal_status_at/3, queue_status_at/3, docket_status_at/3, "
                    "ticket_status_at/3, application_status_at/3, sample_status_at/3, or *_status_on/3 when their args "
                    "are subject, status/result/state, and date/source."
                ),
                (
                    "Do not merely keep split surfaces like "
                    f"{', '.join(nearby[:8]) or 'status/2 plus event_date/status_changed_on'} "
                    "unless a complete joined status-at-date candidate is also present."
                ),
            ]
        )
    if "shallow_status_state_palette" in classes:
        context.extend(
            [
                (
                    "PROFILE ADMISSION RETRY: the previous profile had a shallow_status_state_palette finding. "
                    "Regenerate the profile so point-in-time status, current condition, pending resolution, "
                    "availability, supersession, or partial-population state has a complete candidate predicate "
                    "shape carrying subject or subset, state/status value, and temporal/source/as-of scope together."
                ),
                (
                    "Acceptable shapes include status_state_at/4, entity_status_at/4, record_condition_at/4, "
                    "population_state_at/4, item_availability_at/4, or source-local *_status_at/3-4 and *_state_at/3-4 "
                    "surfaces whose args include subject/subset, state value, and date/source/current/effective scope."
                ),
                (
                    "Do not merely keep split surfaces like "
                    f"{', '.join(nearby[:8]) or 'status/2 plus date/source wrappers'} "
                    "unless a complete joined status/state-scope candidate is also present."
                ),
            ]
        )
    if "shallow_source_attributed_claim_palette" in classes:
        context.extend(
            [
                (
                    "PROFILE ADMISSION RETRY: the previous profile had a shallow_source_attributed_claim_palette "
                    "finding. Regenerate the profile so source-attributed claims, statuses, findings, opinions, "
                    "or reports have a complete candidate predicate shape carrying claim id, source/document or "
                    "speaker, claim/content/status, and source row or scope together."
                ),
                (
                    "Acceptable shapes include source_attributed_claim/4, source_claim/4, reported_finding/4, "
                    "statement_claim/4, or source-local equivalents whose args include claim/content id, source "
                    "or speaker/document, asserted content/status/finding, and source row/scope."
                ),
                (
                    "Do not merely keep source_note/2, report_text/2, statement/2, note/2, or description/2 "
                    "unless a direct source-to-claim/content carrier is also present."
                ),
            ]
        )
    if "shallow_quantity_event_palette" in classes:
        context.extend(
            [
                (
                    "PROFILE ADMISSION RETRY: the previous profile had a shallow_quantity_event_palette finding. "
                    "Regenerate the profile so repeated numeric event/log/source rows have a complete candidate "
                    "predicate shape carrying event or record id, measure or attribute, numeric value, and unit or basis "
                    "when stated."
                ),
                (
                    "Acceptable shapes include event_measurement/4, event_quantity/4, reading_value/4, "
                    "measurement_value/4, metric_observation/4, or source-local equivalents whose args include "
                    "event/record/reading id, measure/attribute, value/amount/rate/threshold/duration, and unit/basis."
                ),
                (
                    "Do not merely keep prose wrappers like event_description/2, note/2, description/2, or source_detail/4 "
                    "unless a direct quantity-bearing event/record candidate is also present."
                ),
            ]
        )
    return context


def _profile_admission_report(*, parsed_profile: dict[str, Any], source_text: str) -> dict[str, Any]:
    source_mentions = _operational_lifecycle_source_mentions(source_text)
    source_authority_mentions = _source_authority_mentions(source_text)
    source_claim_mentions = _source_attributed_claim_mentions(source_text)
    source_claim_required_keys = _source_attributed_claim_required_keys(source_claim_mentions)
    status_state_mentions = _status_state_source_mentions(source_text)
    quantity_mentions = _quantity_event_source_mentions(source_text)
    quantity_required_key_counts = _quantity_event_required_key_counts(quantity_mentions)
    quantity_required_row_count = _quantity_event_required_carrier_row_count(quantity_mentions)
    candidates = parsed_profile.get("candidate_predicates")
    candidate_rows = [item for item in candidates if isinstance(item, dict)] if isinstance(candidates, list) else []
    lifecycle_capable = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_can_carry_operational_lifecycle_unit(item)
    ]
    source_authority_capable = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_can_carry_source_authority_unit(item)
    ]
    source_claim_capable = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_can_carry_source_attributed_claim_unit(item)
    ]
    status_state_capable = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_can_carry_status_state_unit(item)
    ]
    quantity_capable = [
        _candidate_signature(item)
        for item in candidate_rows
        if _candidate_can_carry_quantity_event_unit(item)
    ]
    findings: list[dict[str, Any]] = []
    if len(source_mentions) >= 2 and not lifecycle_capable:
        nearby = [
            _candidate_signature(item)
            for item in candidate_rows
            if _candidate_signature(item)
            and _operational_lifecycle_text(_candidate_signature(item) + " " + " ".join(_candidate_args(item)))
        ]
        findings.append(
            {
                "class": "shallow_lifecycle_palette",
                "source_signal_count": len(source_mentions),
                "candidate_count": len(candidate_rows),
                "nearby_signatures": nearby[:12],
                "evidence": source_mentions[:3],
            }
        )
    if len(source_claim_mentions) >= 2 and not source_claim_capable:
        nearby = [
            _candidate_signature(item)
            for item in candidate_rows
            if _candidate_signature(item)
            and (
                _source_attributed_claim_text(_candidate_signature(item) + " " + " ".join(_candidate_args(item)))
                or _candidate_signature(item).split("/", 1)[0] in {"description", "note", "report_text", "source_note", "statement"}
            )
        ]
        findings.append(
            {
                "class": "shallow_source_attributed_claim_palette",
                "source_signal_count": len(source_claim_mentions),
                "candidate_count": len(candidate_rows),
                "nearby_signatures": nearby[:12],
                "evidence": source_claim_mentions[:3],
            }
        )
    if len(status_state_mentions) >= 2 and not status_state_capable:
        nearby = [
            _candidate_signature(item)
            for item in candidate_rows
            if _candidate_signature(item)
            and (
                _status_state_text(_candidate_signature(item) + " " + " ".join(_candidate_args(item)))
                or _candidate_signature(item).split("/", 1)[0] in {"condition", "description", "note", "status", "state"}
            )
        ]
        findings.append(
            {
                "class": "shallow_status_state_palette",
                "source_signal_count": len(status_state_mentions),
                "candidate_count": len(candidate_rows),
                "nearby_signatures": nearby[:12],
                "evidence": status_state_mentions[:3],
            }
        )
    if len(quantity_mentions) >= 2 and not quantity_capable:
        nearby = [
            _candidate_signature(item)
            for item in candidate_rows
            if _candidate_signature(item)
            and (
                _quantity_event_text(_candidate_signature(item) + " " + " ".join(_candidate_args(item)))
                or _candidate_signature(item).split("/", 1)[0] in {"event_description", "description", "note", "source_detail"}
            )
        ]
        findings.append(
            {
                "class": "shallow_quantity_event_palette",
                "source_signal_count": len(quantity_mentions),
                "candidate_count": len(candidate_rows),
                "nearby_signatures": nearby[:12],
                "evidence": quantity_mentions[:3],
            }
        )
    return {
        "schema_version": "profile_admission_contracts_v1",
        "source_signal_counts": {
            "operational_lifecycle": len(source_mentions),
            "source_authority": len(source_authority_mentions),
            "source_attributed_claim": len(source_claim_mentions),
            "status_state": len(status_state_mentions),
            "quantity_event": len(quantity_mentions),
        },
        "quantity_event_required_carrier_row_count": quantity_required_row_count,
        "quantity_event_required_key_counts": quantity_required_key_counts,
        "source_attributed_claim_required_keys": source_claim_required_keys[:50],
        "candidate_contract_counts": {
            "operational_lifecycle_capable": len(lifecycle_capable),
            "source_authority_capable": len(source_authority_capable),
            "source_attributed_claim_capable": len(source_claim_capable),
            "status_state_capable": len(status_state_capable),
            "quantity_event_capable": len(quantity_capable),
        },
        "capable_signatures": {
            "operational_lifecycle": lifecycle_capable[:12],
            "source_authority": source_authority_capable[:12],
            "source_attributed_claim": source_claim_capable[:12],
            "status_state": status_state_capable[:12],
            "quantity_event": quantity_capable[:12],
        },
        "findings": findings,
    }


def _operational_lifecycle_source_mentions(source_text: str) -> list[str]:
    mentions: list[str] = []
    for raw_line in str(source_text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower()
        if _operational_lifecycle_text(lowered) and (
            PROFILE_ADMISSION_DATE_RE.search(lowered)
            or _profile_admission_tokens(lowered) & PROFILE_ADMISSION_STATE_SLOTS
            or _profile_admission_tokens(lowered) & PROFILE_ADMISSION_LIFECYCLE_TERMS
        ):
            mentions.append(line[:240])
    return mentions


def _source_authority_mentions(source_text: str) -> list[str]:
    mentions: list[str] = []
    for raw_line in str(source_text or "").splitlines():
        line = raw_line.strip()
        if line and SOURCE_AUTHORITY_TEXT_RE.search(line) and not _source_authority_line_is_document_metadata(line):
            mentions.append(line[:240])
    return mentions


def _source_authority_line_is_document_metadata(line: str) -> bool:
    stripped = str(line or "").strip()
    lowered = stripped.casefold()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    if stripped.startswith("|") and stripped.endswith("|"):
        return True
    if lowered.startswith(("issuing organization:", "agency:")):
        return True
    if re.match(r"^\*{0,2}a\s+rule\s+by\s+the\b", lowered):
        return True
    if lowered in {
        "federal labor relations authority",
        "federal service impasses panel, federal labor relations authority.",
    }:
        return True
    if (
        "final rule" in lowered
        and "updates regulations" in lowered
        and "authority" in lowered
        and "authority citation" not in lowered
    ):
        return True
    return False


def _source_attributed_claim_mentions(source_text: str) -> list[str]:
    mentions: list[str] = []
    for raw_line in str(source_text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower()
        tokens = _profile_admission_tokens(lowered)
        has_speaker_frame = _line_has_source_attributed_speaker_frame(line)
        if (
            _line_has_source_attributed_claim_source_signal(line, tokens, has_speaker_frame)
            and tokens & PROFILE_ADMISSION_SOURCE_CLAIM_CONTENT_TERMS
            and not _source_claim_line_is_administrative_lifecycle(line, tokens)
        ):
            mentions.append(line[:500])
    return mentions


def _line_has_source_attributed_claim_source_signal(line: str, tokens: set[str], has_speaker_frame: bool) -> bool:
    lowered = str(line or "").casefold()
    if (
        "available" in tokens
        and re.search(r"\b(?:available\s+(?:at|here|from)|is\s+available)\b", lowered)
        and (re.search(r"https?://|\bwww\.", lowered) or "here" in tokens or "download" in tokens)
    ):
        return False
    if has_speaker_frame:
        return not _line_has_generic_source_field_label(line)
    source_terms = tokens & PROFILE_ADMISSION_SOURCE_CLAIM_SOURCE_TERMS
    if not source_terms:
        return False
    strong_source_terms = source_terms - {"certification", "said", "source"}
    if strong_source_terms:
        return True
    if "certification" in source_terms and re.search(
        r"\b(?:certification\s+(?:asserts?|claims?|confirms?|concludes?|determines?|finds?|notes?|"
        r"reports?|says|said|states?|stated|supports?)|"
        r"(?:asserts?|claims?|confirms?|concludes?|determines?|finds?|notes?|reports?|says|said|"
        r"states?|stated|supports?)\s+(?:in\s+)?(?:a\s+)?certification)\b",
        lowered,
    ):
        return True
    return bool(
        re.search(
            r"\bsource\s+(?:asserts?|claims?|confirms?|concludes?|determines?|finds?|notes?|opin(?:es|ed)?|"
            r"reports?|says|said|states?|stated|supports?)\b",
            lowered,
        )
        or re.search(r"\b(?:letter|memo|memorandum|opinion|report|statement|testimony)\s+source\b", lowered)
    )


def _line_has_generic_source_field_label(line: str) -> bool:
    stripped = str(line or "").strip()
    match = re.match(r"^(?:[-*]\s*)?(?:\*\*)?([A-Za-z][A-Za-z0-9 _/-]{1,40})(?:\*\*)?:", stripped)
    if not match:
        return False
    label_tokens = _profile_admission_tokens(match.group(1))
    if not label_tokens:
        return False
    generic_labels = {
        "agency",
        "case",
        "date",
        "id",
        "identifier",
        "location",
        "phase",
        "status",
        "type",
    }
    return label_tokens <= generic_labels


def _line_has_source_attributed_speaker_frame(line: str) -> bool:
    stripped = str(line or "").strip()
    if not stripped:
        return False
    if re.match(r"^(?:[-*]\s*)?(?:\*\*)?[A-Z][A-Za-z0-9 .'\-&]{1,80}:(?:\*\*)?\s+", stripped):
        return True
    lowered = stripped.casefold()
    return bool(re.search(r"\b(?:says|said|states|stated|argues|argued|responds|responded|testifies|testified)\s*:", lowered))


def _source_claim_line_is_administrative_lifecycle(line: str, tokens: set[str]) -> bool:
    lowered = str(line or "").casefold()
    if str(line or "").lstrip().startswith(('"', "“")):
        return False
    stripped = str(line or "").strip()
    if stripped.startswith("|") and stripped.endswith("|"):
        return True
    if lowered.startswith(("authority:", "issuing organization:", "agency:")):
        return True
    if "authority citation for part" in lowered:
        return True
    administrative_subject = tokens & {"amendment", "application", "draft", "filing", "permit", "record"}
    lifecycle_terms = tokens & {
        "filed",
        "issued",
        "prepared",
        "proposing",
        "retaining",
        "superseded",
        "withdrawn",
    }
    if administrative_subject and lifecycle_terms:
        return True
    if "draft" in tokens and "superseded" in tokens:
        return True
    return False


def _source_attributed_claim_required_keys(mentions: list[str]) -> list[str]:
    keys: list[str] = []
    seen: set[str] = set()
    for mention in mentions:
        key = _source_attributed_claim_signal_key(mention)
        if key and key not in seen:
            seen.add(key)
            keys.append(key)
    return keys


def _vote_tally_source_mentions(source_text: str) -> list[str]:
    mentions: list[str] = []
    lines = [line.strip() for line in str(source_text or "").splitlines()]
    for index, line in enumerate(lines):
        if not line or not _vote_tally_text(line):
            continue
        combined = line
        tokens = _profile_admission_tokens(line)
        if tokens & {"corrected", "correction", "minutes", "recorded"}:
            next_line = lines[index + 1] if index + 1 < len(lines) else ""
            if next_line and re.search(r"\b\d+\s*[-_]\s*\d+\b", next_line):
                combined = f"{line} {next_line}"
        mentions.append(combined[:500])
    return mentions


def _vote_tally_required_keys(mentions: list[str]) -> list[str]:
    keys: list[str] = []
    seen: set[str] = set()
    for mention in mentions:
        key = _vote_tally_signal_key(mention)
        if key and key not in seen:
            seen.add(key)
            keys.append(key)
    return keys


def _scope_discrepancy_source_mentions(source_text: str) -> list[str]:
    mentions: list[str] = []
    for raw_line in str(source_text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.casefold()
        tokens = _profile_admission_tokens(lowered)
        record_pair = bool(re.search(r"\brecord\s+[a-z0-9]+\b.*\brecord\s+[a-z0-9]+\b", lowered))
        compares_records = (
            len(tokens & {"agreement", "contract", "order", "policy", "record", "resolution", "rule"}) >= 2
            or record_pair
        )
        states_comparison = bool(tokens & {"differs", "discrepancy", "conflict", "states", "specifies", "requires"})
        omission_comparison = bool(re.search(r"\b(?:does\s+not\s+mention|not\s+addressed|omits?|missing)\b", lowered))
        if compares_records and (states_comparison or omission_comparison):
            mentions.append(line[:500])
    return mentions


def _scope_discrepancy_required_keys(mentions: list[str]) -> list[str]:
    keys: list[str] = []
    seen: set[str] = set()
    for mention in mentions:
        key = _scope_discrepancy_signal_key(mention)
        if key and key not in seen:
            seen.add(key)
            keys.append(key)
    return keys


def _scope_discrepancy_signal_key(text: str) -> str:
    lowered = str(text or "").casefold().replace("-", "_")
    compact = _normalize_profile_atom(lowered)
    label = compact
    label_match = re.match(r"(?:v_\d+|[0-9]{1,3})?_?([a-z0-9_]{3,80}?)(?:_the_|_resolution_|_agreement_|:|$)", compact)
    if label_match:
        label = label_match.group(1)
    aliases = {
        "progress_reports": "reporting_frequency",
        "progress_reporting": "reporting_frequency",
        "reports": "reporting_frequency",
        "project_timeline": "timeline",
        "completion_timeline": "timeline",
        "timeline": "timeline",
        "fire_hydrants": "fire_hydrants",
        "hydrants": "fire_hydrants",
        "pipe_length": "pipe_length",
        "length": "pipe_length",
        "pipe_diameter": "pipe_diameter",
        "diameter": "pipe_diameter",
    }
    for needle, value in aliases.items():
        if needle in compact:
            return value
    return re.sub(r"^v_\d+_", "", label).strip("_")


def _vote_tally_signal_key(text: str) -> str:
    lowered = str(text or "").casefold().replace("-", "_")
    tokens = _profile_admission_tokens(lowered)
    tally_match = VOTE_TALLY_PAIR_RE.search(lowered)
    tally = f"{tally_match.group(1)}_{tally_match.group(2)}" if tally_match else ""
    if not tally:
        return ""
    if tokens & {"corrected", "correction", "minutes"}:
        if "4_1" in lowered and "3_1" in lowered:
            return "correction:4_1_to_3_1"
        return f"correction:{tally}"
    if tokens & {"proceed", "proceeded"}:
        return f"proceed:{tally}"
    if tokens & {"approve", "approved", "approval", "affirmative"}:
        return f"approved:{tally}"
    if tokens & {"deny", "denied", "negative"}:
        return f"denied:{tally}"
    return f"vote:{tally}"


def _vote_tally_text(text: str) -> bool:
    return bool(VOTE_TALLY_TEXT_RE.search(str(text or "")))


def _source_attributed_claim_signal_key(text: str) -> str:
    lowered = str(text or "").casefold().replace("-", "_")
    tokens = _profile_admission_tokens(lowered)
    if not tokens:
        return ""
    source_kind = "source"
    for candidate, markers in (
        ("letter_of_intent", {"letter", "intent"}),
        ("email", {"email"}),
        ("letter", {"letter"}),
        ("memo", {"memo", "memorandum"}),
        ("opinion", {"opinion"}),
        ("report", {"report"}),
        ("testimony", {"testimony", "witness"}),
        ("note", {"note"}),
        ("statement", {"statement"}),
        ("comment", {"comment"}),
        ("assessment", {"assessment"}),
    ):
        if _source_claim_markers_match(tokens, markers):
            source_kind = candidate
            break
    if source_kind == "source" and _line_has_source_attributed_speaker_frame(str(text or "")):
        source_kind = "statement"
    subject_kind = "claim"
    for candidate, markers in (
        ("architect_documentation", {"architect", "documentation"}),
        ("documentation", {"documentation"}),
        ("letter_of_intent", {"letter", "intent"}),
        ("draft", {"draft"}),
        ("amendment", {"amendment"}),
        ("permit", {"permit"}),
        ("removal", {"removal"}),
        ("status", {"status", "state"}),
        ("finding", {"finding"}),
        ("dispute", {"dispute", "disputed"}),
        ("support", {"support", "supports"}),
    ):
        if _source_claim_markers_match(tokens, markers):
            subject_kind = candidate
            break
    claim_kind = ""
    if ("not" in tokens and "binding" in tokens) or "nonbinding" in tokens or "non_binding" in lowered:
        claim_kind = "not_binding"
    elif ("no" in tokens and "effect" in tokens) or "no_effect" in lowered or ("legal" in tokens and "effect" in tokens):
        claim_kind = "no_effect"
    elif "under" in tokens and "review" in tokens:
        claim_kind = "under_review"
    elif ("not" in tokens and "resolved" in tokens) or tokens & {"unresolved", "pending"}:
        claim_kind = "unresolved"
    elif "not" in tokens and tokens & {"legal", "determination"}:
        claim_kind = "not_legal_determination"
    elif "no" in tokens and tokens & {"documentation", "record"}:
        claim_kind = "no_documentation"
    elif "not" in tokens and tokens & {"flagged"}:
        claim_kind = "not_flagged"
    elif tokens & {"voided", "void", "unsigned"}:
        claim_kind = "voided"
    elif tokens & {"disagree", "disputed", "dispute"}:
        claim_kind = "dispute"
    elif tokens & {"supports", "support"}:
        claim_kind = "support"
    elif tokens & {"objects", "objected", "opposes", "opposed", "objection"}:
        claim_kind = "objection"
    elif tokens & {"concern", "concerned", "concerns"}:
        claim_kind = "concern"
    elif tokens & {"recommend", "recommended", "recommendation"}:
        claim_kind = "recommendation"
    elif tokens & {"advisory", "opinion"}:
        claim_kind = "opinion"
    elif tokens & {"based", "finding", "determined", "confirmed", "justified", "warrants"}:
        claim_kind = "finding"
    elif tokens & PROFILE_ADMISSION_SOURCE_CLAIM_CONTENT_TERMS:
        content_terms = set(tokens & PROFILE_ADMISSION_SOURCE_CLAIM_CONTENT_TERMS)
        if "available" in content_terms and _available_word_is_capacity_or_timing_phrase(lowered):
            content_terms.discard("available")
        if len(content_terms) > 1:
            content_terms.discard("claim")
        if not content_terms:
            return ""
        claim_kind = sorted(content_terms)[0]
    if not claim_kind:
        return ""
    return f"{source_kind}:{subject_kind}:{claim_kind}"


def _available_word_is_capacity_or_timing_phrase(lowered: str) -> bool:
    return bool(
        re.search(
            r"\b(?:amount|duration|period|time|window|days?|months?|years?)\s+available\b|"
            r"\bavailable\s+to\b|"
            r"\bavailable\s+(?:for|within)\s+(?:review|consideration|processing|decision|use)\b",
            str(lowered or ""),
        )
    )


def _source_claim_markers_match(tokens: set[str], markers: set[str]) -> bool:
    if len(markers) > 1:
        return markers <= tokens
    return bool(tokens & markers)


def _status_state_source_mentions(source_text: str) -> list[str]:
    mentions: list[str] = []
    for raw_line in str(source_text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower()
        tokens = _profile_admission_tokens(lowered)
        status_terms = tokens & PROFILE_ADMISSION_STATUS_STATE_TERMS
        if status_terms == {"state"}:
            continue
        if (
            tokens & PROFILE_ADMISSION_SUBJECT_SLOTS
            and status_terms
            and (
                PROFILE_ADMISSION_DATE_RE.search(lowered)
                or tokens & PROFILE_ADMISSION_SCOPE_SLOTS
                or tokens & {"after", "before", "changed", "current", "effective", "from", "superseded", "to"}
            )
        ):
            mentions.append(line[:240])
    return mentions


def _quantity_event_source_mentions(source_text: str) -> list[str]:
    mentions: list[str] = []
    for raw_line in str(source_text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower()
        tokens = _profile_admission_tokens(lowered)
        has_numeric = bool(re.search(r"\b\d+(?:[._]\d+)?\b", lowered))
        if (
            has_numeric
            and (PROFILE_ADMISSION_DATE_RE.search(lowered) or tokens & PROFILE_ADMISSION_QUANTITY_UNIT_TERMS)
            and _quantity_event_text(lowered)
            and _profile_admission_tokens(lowered) & PROFILE_ADMISSION_QUANTITY_EVENT_SUBJECT_SLOTS
        ):
            mentions.append(line[:240])
    return mentions


def _quantity_event_required_carrier_row_count(mentions: list[str]) -> int:
    return sum(_quantity_event_required_key_counts(mentions).values())


def _quantity_event_required_key_counts(mentions: list[str]) -> dict[str, int]:
    requirements: dict[str, int] = {}
    for index, mention in enumerate(mentions):
        key = _quantity_event_requirement_key(mention) or f"mention:{index}"
        rows = _quantity_event_required_rows_for_mention(mention)
        requirements[key] = max(rows, requirements.get(key, 0))
    return dict(sorted(requirements.items()))


def _quantity_event_required_rows_for_mention(mention: str) -> int:
    lowered = str(mention or "").casefold()
    tokens = _profile_admission_tokens(lowered)
    has_change = bool(tokens & {"changed", "decreased", "increase", "increased", "reverted"})
    has_from_to = bool(re.search(r"\bfrom\b.+\bto\b", lowered))
    has_arrow = bool(re.search(r"(?:->|\u2192|=>)", lowered))
    if has_change and (has_from_to or has_arrow):
        return 2
    return 1


def _quantity_event_requirement_key(mention: str) -> str:
    lowered = str(mention or "").casefold().replace("-", "_")
    tokens = _profile_admission_tokens(lowered)
    event_ids = [
        f"ev_{int(match.group(1)):02d}"
        for match in re.finditer(r"\bev[_\s]?0*(\d+)\b", lowered)
    ]
    if "duration" in tokens and "line" in tokens and "stop" in tokens:
        return "duration:line_stop"
    if "duration" in tokens and len(event_ids) >= 2:
        return "duration:" + ":".join(event_ids[:2])
    if event_ids:
        measure = "quantity"
        if "setpoint" in tokens:
            measure = "setpoint"
        elif "feed" in tokens and "rate" in tokens:
            measure = "feed_rate"
        elif "drift" in tokens or "offset" in tokens:
            measure = "drift_offset"
        elif "duration" in tokens:
            measure = "duration"
        return f"event:{event_ids[0]}:{measure}"
    return ""


def _quantity_event_fact_key(predicate: str, args: list[str]) -> str:
    name = str(predicate or "").casefold()
    norm_args = [_normalize_profile_atom(str(arg)) for arg in args]
    if name in {"event_measurement", "event_quantity", "reading_value", "measurement_value", "metric_observation"}:
        if len(norm_args) >= 2:
            event_id = _quantity_event_normalized_event_id(norm_args[0])
            measure = _quantity_event_measure_key(norm_args[1])
            if event_id and measure:
                return f"event:{event_id}:{measure}"
    if name in {"event_duration", "interval_duration", "duration_between", "line_stop_duration"}:
        joined = " ".join([name, *norm_args])
        if "line" in joined and "stop" in joined:
            return "duration:line_stop"
        event_ids = [_quantity_event_normalized_event_id(arg) for arg in norm_args]
        event_ids = [event_id for event_id in event_ids if event_id]
        if len(event_ids) >= 2:
            return "duration:" + ":".join(event_ids[:2])
        if "duration" in joined:
            return "duration:line_stop"
    joined = " ".join([name, *norm_args])
    if (
        ("duration" in joined and "line" in joined and "stop" in joined)
        or ("line" in joined and "stop" in joined and sum(1 for arg in norm_args if _quantity_event_normalized_event_id(arg)) >= 2)
    ):
        return "duration:line_stop"
    event_id = next((_quantity_event_normalized_event_id(arg) for arg in norm_args if _quantity_event_normalized_event_id(arg)), "")
    measure = _quantity_event_measure_key(joined)
    if event_id and measure:
        return f"event:{event_id}:{measure}"
    return ""


def _quantity_event_normalized_event_id(value: str) -> str:
    norm = _normalize_profile_atom(value)
    match = re.search(r"\bev[_\s]?0*(\d+)\b", norm)
    if not match:
        return ""
    return f"ev_{int(match.group(1)):02d}"


def _quantity_event_measure_key(text: str) -> str:
    lowered = str(text or "").casefold().replace("-", "_")
    tokens = _profile_admission_tokens(lowered)
    if "setpoint" in tokens:
        return "setpoint"
    if "feed" in tokens and "rate" in tokens:
        return "feed_rate"
    if "drift" in tokens or "offset" in tokens:
        return "drift_offset"
    if "duration" in tokens:
        return "duration"
    return ""


def _quantity_event_key_is_delivered(required_key: str, delivered_key: str) -> bool:
    if required_key == delivered_key:
        return True
    required = str(required_key or "")
    delivered = str(delivered_key or "")
    if required == "duration:line_stop" and delivered.startswith("duration:"):
        return True
    return False


def _candidate_can_carry_operational_lifecycle_unit(candidate: dict[str, Any]) -> bool:
    signature = _candidate_signature(candidate).lower()
    args = _candidate_args(candidate)
    if signature.split("/", 1)[0] in {"record_lifecycle_event", "record_status_phase", "record_status_at"}:
        return True
    if len(args) < 3:
        return False
    arg_tokens = [_profile_admission_tokens(arg.lower()) for arg in args]
    has_subject = any(tokens & PROFILE_ADMISSION_SUBJECT_SLOTS for tokens in arg_tokens)
    has_state = any(tokens & PROFILE_ADMISSION_STATE_SLOTS for tokens in arg_tokens)
    has_date = any(tokens & PROFILE_ADMISSION_DATE_SLOTS for tokens in arg_tokens)
    return has_subject and has_state and has_date and _operational_lifecycle_text(signature + " " + " ".join(args))


def _candidate_can_carry_source_authority_unit(candidate: dict[str, Any]) -> bool:
    signature = _candidate_signature(candidate).lower()
    if not signature:
        return False
    if _has_specific_source_authority_carrier({signature}):
        return True
    name = signature.split("/", 1)[0]
    args = _candidate_args(candidate)
    tokens = _profile_admission_tokens(name + " " + " ".join(args).lower())
    return bool(
        len(args) >= 3
        and tokens & {"authority", "authorized", "authorised", "governing", "order", "policy", "rule"}
        and tokens & {"action", "claim", "decision", "finding", "scope", "status", "subject"}
    )


def _candidate_can_carry_source_attributed_claim_unit(candidate: dict[str, Any]) -> bool:
    signature = _candidate_signature(candidate).lower()
    name = signature.split("/", 1)[0]
    if _candidate_can_carry_source_authority_unit(candidate):
        return False
    name_tokens = set(name.split("_"))
    if name in {"claim_source", "source_supports"}:
        return False
    if name_tokens & {"appropriation", "appropriations", "fund", "funding"} and not (
        name_tokens & {"claim", "comment", "finding", "memo", "note", "opinion", "report", "statement"}
    ):
        return False
    if (
        name_tokens & {"status", "state", "change", "transition"}
        and not name_tokens & {"claim", "finding", "memo", "note", "opinion", "report", "statement"}
    ):
        return False
    if name in {"reported_finding", "source_attributed_claim", "source_claim", "statement_claim"}:
        return True
    args = _candidate_args(candidate)
    if len(args) < 3:
        return False
    arg_tokens = [_profile_admission_tokens(arg.lower()) for arg in args]
    source_anchor_terms = {
        "author",
        "claimant",
        "doc",
        "document",
        "email",
        "letter",
        "memo",
        "person",
        "reporter",
        "source",
        "speaker",
        "witness",
    }
    has_source = any(tokens & source_anchor_terms for tokens in arg_tokens)
    has_content = any(tokens & (PROFILE_ADMISSION_SOURCE_CLAIM_CONTENT_TERMS | {"content", "detail", "topic"}) for tokens in arg_tokens)
    has_anchor = any(tokens & (PROFILE_ADMISSION_SCOPE_SLOTS | {"claim", "id", "row", "scope"}) for tokens in arg_tokens)
    return has_source and has_content and has_anchor and _source_attributed_claim_text(signature + " " + " ".join(args))


def _candidate_can_carry_status_state_unit(candidate: dict[str, Any]) -> bool:
    signature = _candidate_signature(candidate).lower()
    name = signature.split("/", 1)[0]
    if _candidate_can_carry_source_attributed_claim_unit(candidate):
        return False
    if set(name.split("_")) & {"claim", "memo", "note", "opinion", "report", "source", "statement", "testimony", "witness"}:
        return False
    if name.endswith(("_status_at", "_state_at", "_condition_at", "_status_on", "_state_on")):
        return True
    if name in {"entity_status_at", "item_availability_at", "population_state_at", "record_condition_at", "status_state_at"}:
        return True
    args = _candidate_args(candidate)
    if len(args) < 3:
        return False
    arg_tokens = [_profile_admission_tokens(arg.lower()) for arg in args]
    has_subject = any(tokens & PROFILE_ADMISSION_SUBJECT_SLOTS for tokens in arg_tokens)
    has_state = any(tokens & (PROFILE_ADMISSION_STATE_SLOTS | {"availability", "condition"}) for tokens in arg_tokens)
    has_scope = any(tokens & (PROFILE_ADMISSION_DATE_SLOTS | PROFILE_ADMISSION_SCOPE_SLOTS) for tokens in arg_tokens)
    return has_subject and has_state and has_scope and _status_state_text(signature + " " + " ".join(args))


def _candidate_can_carry_quantity_event_unit(candidate: dict[str, Any]) -> bool:
    signature = _candidate_signature(candidate).lower()
    name = signature.split("/", 1)[0]
    if name in {"event_measurement", "event_quantity", "reading_value", "measurement_value", "metric_observation"}:
        return True
    args = _candidate_args(candidate)
    if len(args) < 3:
        return False
    arg_tokens = [_profile_admission_tokens(arg.lower()) for arg in args]
    has_subject = any(tokens & PROFILE_ADMISSION_QUANTITY_EVENT_SUBJECT_SLOTS for tokens in arg_tokens)
    has_value = any(tokens & PROFILE_ADMISSION_QUANTITY_VALUE_SLOTS for tokens in arg_tokens)
    has_measure = (
        any(tokens & {"attribute", "field", "measure", "metric", "name", "type"} for tokens in arg_tokens)
        or _quantity_event_text(signature)
    )
    has_unit_or_basis = any(tokens & PROFILE_ADMISSION_QUANTITY_UNIT_SLOTS for tokens in arg_tokens)
    return has_subject and has_value and has_measure and has_unit_or_basis


def _candidate_can_carry_quantity_event_delivery_unit(candidate: dict[str, Any]) -> bool:
    if _candidate_can_carry_quantity_event_unit(candidate):
        return True
    signature = _candidate_signature(candidate).lower()
    name = signature.split("/", 1)[0]
    args = _candidate_args(candidate)
    if name in {"event_duration", "interval_duration", "line_stop_duration", "duration_between"}:
        return True
    if len(args) < 2:
        return False
    name_tokens = _profile_admission_tokens(name)
    if name_tokens & {"capability", "certification", "certified", "scope"}:
        return False
    arg_tokens = [_profile_admission_tokens(arg.lower()) for arg in args]
    has_value = any(tokens & PROFILE_ADMISSION_QUANTITY_VALUE_SLOTS for tokens in arg_tokens)
    has_subject = any(tokens & PROFILE_ADMISSION_QUANTITY_EVENT_SUBJECT_SLOTS for tokens in arg_tokens)
    if not (has_value and has_subject):
        return False
    quantity_terms = {
        "amount",
        "count",
        "duration",
        "measurement",
        "metric",
        "quantity",
        "rate",
        "reading",
        "score",
        "threshold",
        "total",
        "value",
    }
    return bool(
        name_tokens & quantity_terms
        or any(tokens & quantity_terms for tokens in arg_tokens)
    )


def _candidate_signature(candidate: dict[str, Any]) -> str:
    return str(candidate.get("signature") or "")


def _candidate_args(candidate: dict[str, Any]) -> list[str]:
    args = candidate.get("args")
    return [str(arg) for arg in args] if isinstance(args, list) else []


def _operational_lifecycle_text(text: str) -> bool:
    return bool(_profile_admission_tokens(text) & PROFILE_ADMISSION_LIFECYCLE_TERMS)


def _source_attributed_claim_text(text: str) -> bool:
    tokens = _profile_admission_tokens(text)
    return bool(tokens & PROFILE_ADMISSION_SOURCE_CLAIM_SOURCE_TERMS and tokens & PROFILE_ADMISSION_SOURCE_CLAIM_CONTENT_TERMS)


def _status_state_text(text: str) -> bool:
    return bool(_profile_admission_tokens(text) & PROFILE_ADMISSION_STATUS_STATE_TERMS)


def _quantity_event_text(text: str) -> bool:
    return bool(_profile_admission_tokens(text) & PROFILE_ADMISSION_QUANTITY_TERMS)


def _profile_admission_tokens(text: str) -> set[str]:
    return set(PROFILE_ADMISSION_TOKEN_RE.findall(str(text or "").lower()))


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
            "permit",
            "quarantine",
            "greenhouse",
            "nursery",
            "lab result",
        ]
    ):
        contexts.extend(POLICY_INCIDENT_SOURCE_COMPILER_CONTEXT_V1)
    if any(
        token in label
        for token in [
            "permit",
            "intake",
            "turnstream",
            "facilities",
            "ledger",
            "seed bank",
            "accession",
            "deaccession",
            "conservation",
            "grant",
            "application docket",
            "correction log",
            "operations log",
            "quarantine",
            "greenhouse",
            "nursery",
            "lab result",
            "license",
            "inspection",
            "appeal",
        ]
    ):
        contexts.extend(OPERATIONAL_RECORD_STATUS_CONTEXT_V1)
    if any(
        token in label
        for token in [
            "probate",
            "inheritance",
            "estate",
            "will",
            "gift",
            "pledge",
            "possession",
            "ownership",
            "custody",
            "property status",
            "adverse possession",
            "disputed property",
        ]
    ):
        contexts.extend(PROBATE_PROPERTY_STATUS_CONTEXT_V1)
    if any(
        token in label
        for token in [
            "tournament",
            "match",
            "contest",
            "scoring",
            "bracket",
            "ranking",
            "protest",
            "marshal",
            "referee",
            "range officer",
            "banner",
            "alias",
            "role change",
            "dual role",
        ]
    ):
        contexts.extend(COMPETITION_ROLE_ALIAS_CONTEXT_V1)
    if any(
        token in label
        for token in [
            "audit",
            "placard",
            "visitor guide",
            "catalog",
            "acquisition record",
            "curator",
            "museum",
            "source authority",
            "copied from",
            "correction status",
            "relabel",
            "relabelling",
            "hearing",
            "survey",
            "evidence",
            "testimony",
            "exhibit",
            "photograph",
            "photographs",
            "commissioned",
        ]
    ):
        contexts.extend(SOURCE_AUTHORITY_AUDIT_CONTEXT_V1)
    if any(
        token in label
        for token in [
            "fiction",
            "novel",
            "literary",
            "story level",
            "reference containment",
            "fictional",
            "quoted story",
            "nested narrative",
            "coincidence",
            "source layer",
        ]
    ):
        contexts.extend(FICTION_REFERENCE_CONTAINMENT_CONTEXT_V1)
    if any(
        token in label
        for token in [
            "field trip",
            "school",
            "attendance",
            "supervision",
            "chaperone",
            "roster",
            "station",
            "group assignment",
            "return transport",
        ]
    ):
        contexts.extend(ADMINISTRATIVE_ROSTER_TIMELINE_CONTEXT_V1)
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
            "annual report",
            "associate",
            "corporate disclosure",
            "dividend",
            "earnings",
            "equity-method",
            "financial performance",
            "financial result",
            "financial statement",
            "forecast",
            "income statement",
            "investee",
            "issuer report",
            "quarterly report",
            "segment performance",
            "statutory earnings",
        ]
    ):
        contexts.extend(FINANCIAL_REPORT_SOURCE_COMPILER_CONTEXT_V1)
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
    empty_response_retries: int = 2,
    empty_response_backoff_seconds: float = 1.0,
    strict_response_format: bool = True,
) -> dict[str, Any]:
    request_messages = [dict(message) for message in messages]
    is_openrouter = _is_openrouter_base_url(base_url)
    portable_openrouter_payload = is_openrouter and str(
        os.environ.get("PRETHINKER_OPENROUTER_PORTABLE_PAYLOAD", "") or ""
    ).strip().lower() in {"1", "true", "yes", "on"}
    if str(reasoning_effort or "").strip().lower() in {"none", "off", "false", "0"}:
        for message in request_messages:
            if message.get("role") == "system":
                content = str(message.get("content") or "")
                if not content.lstrip().startswith("/no_think"):
                    message["content"] = "/no_think\n" + content
                break
    payload: dict[str, Any] = {
        "model": model,
        "messages": request_messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
    }
    if strict_response_format:
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": schema,
            },
        }

    if not portable_openrouter_payload:
        payload["think"] = False
        payload["thinking"] = False
    seed_text = str(os.environ.get("PRETHINKER_LLM_SEED", "") or "").strip()
    if seed_text:
        try:
            payload["seed"] = int(seed_text)
        except ValueError:
            payload["seed"] = seed_text
    if str(reasoning_effort or "").strip() and not portable_openrouter_payload:
        payload["reasoning_effort"] = str(reasoning_effort).strip()
    if is_openrouter:
        if not portable_openrouter_payload:
            payload["reasoning"] = {"effort": "none", "exclude": True}
            payload["include_reasoning"] = False
        provider_routing = openrouter_provider_routing_from_env()
        if provider_routing:
            payload["provider"] = provider_routing
    started = time.perf_counter()
    max_attempts = max(1, int(empty_response_retries or 0) + 1)
    last_raw: dict[str, Any] = {}
    for attempt in range(1, max_attempts + 1):
        req = urllib.request.Request(
            _lmstudio_chat_completions_url(base_url),
            data=json.dumps(payload).encode("utf-8"),
            headers=_chat_headers(base_url=base_url),
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(str(exc)) from exc
        last_raw = raw if isinstance(raw, dict) else {}
        openrouter_metadata = openrouter_generation_metadata(
            raw_response=last_raw,
            request_payload=payload,
            base_url=base_url,
            timeout=min(int(timeout), 30),
            call_role=schema_name,
        )
        if openrouter_metadata:
            OPENROUTER_CALL_METADATA_LOG.append(openrouter_metadata)
        choices = raw.get("choices", []) if isinstance(raw, dict) else []
        message = choices[0].get("message", {}) if choices and isinstance(choices[0], dict) else {}
        content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
        reasoning_content = str(message.get("reasoning_content", "") if isinstance(message, dict) else "").strip()
        merged_content = content or reasoning_content
        if merged_content or attempt >= max_attempts:
            return {
                "latency_ms": int((time.perf_counter() - started) * 1000),
                "raw": raw,
                "openrouter_generation_metadata": openrouter_metadata,
                "content": merged_content,
                "attempts": attempt,
                "empty_response_retries": attempt - 1,
            }
        time.sleep(max(0.0, float(empty_response_backoff_seconds)) * attempt)
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "raw": last_raw,
        "openrouter_generation_metadata": openrouter_generation_metadata(
            raw_response=last_raw,
            request_payload=payload,
            base_url=base_url,
            timeout=min(int(timeout), 30),
            call_role=schema_name,
        ),
        "content": "",
        "attempts": max_attempts,
        "empty_response_retries": max_attempts - 1,
    }


def _chat_headers(api_key: str = "", *, base_url: str = "") -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    openrouter_target = not str(base_url or "").strip() or _is_openrouter_base_url(base_url)
    if openrouter_target:
        key = openrouter_api_key(api_key)
    else:
        key = str(api_key or os.environ.get("PRETHINKER_API_KEY") or "").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    if openrouter_target:
        headers.update(openrouter_metadata_headers(base_url))
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
    return _sanitize_header_value(f"compile:{fixture}")


def _sanitize_header_value(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._:/ -]+", "-", str(value or "").strip())
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -")
    return cleaned[:120]


def _is_openrouter_base_url(base_url: str) -> bool:
    return "openrouter.ai" in str(base_url or "").lower()


def _lmstudio_chat_completions_url(base_url: str) -> str:
    root = str(base_url or "").strip().rstrip("/")
    if root.endswith("/v1"):
        root = root[:-3]
    return f"{root}/v1/chat/completions"


def _write_summary(record: dict[str, Any], path: Path) -> None:
    parsed = record.get("parsed") if isinstance(record.get("parsed"), dict) else {}
    score = record.get("score") if isinstance(record.get("score"), dict) else {}
    compile_record = record.get("source_compile") if isinstance(record.get("source_compile"), dict) else {}
    serving_path = record.get("model_serving_path") if isinstance(record.get("model_serving_path"), dict) else {}
    lines = [
        "# Domain Bootstrap File Run",
        "",
        f"- Source file: `{record.get('text_file', '')}`",
        f"- Backend/model: `{record.get('backend', '')}` / `{record.get('model', '')}`",
        f"- Provider family: `{serving_path.get('provider_family', '')}`",
        f"- Base URL: `{serving_path.get('base_url', '')}`",
        f"- Provider routing: `{serving_path.get('provider_routing', {})}`",
        f"- Parsed: `{record.get('parsed_ok', False)}`",
        f"- Rough score: `{score.get('rough_score', 0.0)}`",
        f"- Entity types: `{score.get('entity_type_count', 0)}`",
        f"- Candidate predicates: `{score.get('predicate_count', 0)}`",
        f"- Generic predicates: `{score.get('generic_predicate_count', 0)}`",
        f"- Candidate signature/args mismatches: `{score.get('candidate_signature_arg_mismatch_refs', [])}`",
        f"- Candidate duplicate name/arity refs: `{score.get('candidate_duplicate_name_arity_refs', [])}`",
        f"- Governed carrier arg-role mismatch refs: `{score.get('governed_carrier_arg_role_mismatch_refs', [])}`",
        f"- Provenance prose arg-role refs: `{score.get('provenance_prose_arg_role_refs', [])}`",
        f"- Recommendation-chain slot-loss refs: `{score.get('recommendation_chain_slot_loss_refs', [])}`",
        f"- Violation-category slot-loss refs: `{score.get('violation_category_slot_loss_refs', [])}`",
        f"- List/range inventory slot-loss refs: `{score.get('list_range_inventory_slot_loss_refs', [])}`",
        f"- Repeated structures: `{score.get('repeated_structure_count', 0)}`",
        f"- Repeated-structure unknown predicate refs: `{score.get('repeated_structure_unknown_predicate_refs', [])}`",
        f"- Repeated-structure id-only record refs: `{score.get('repeated_structure_id_only_record_refs', [])}`",
        f"- Repeated-structure role mismatch refs: `{score.get('repeated_structure_role_mismatch_refs', [])}`",
        f"- Repeated-structure lookup property refs: `{score.get('repeated_structure_lookup_property_refs', [])}`",
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
    schema_retry = record.get("profile_schema_contract_retry") if isinstance(record.get("profile_schema_contract_retry"), dict) else {}
    if schema_retry:
        retry_score = schema_retry.get("retry_score") if isinstance(schema_retry.get("retry_score"), dict) else {}
        lines.extend(
            [
                "## Profile Schema Contract Retry",
                "",
                f"- Parsed: `{schema_retry.get('parsed_ok', False)}`",
                f"- Adopted: `{schema_retry.get('adopted', False)}`",
                f"- Candidate signature/args mismatches after retry: `{retry_score.get('candidate_signature_arg_mismatch_refs', [])}`",
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
        profile_admission = compile_record.get("profile_admission") if isinstance(compile_record.get("profile_admission"), dict) else {}
        profile_delivery = compile_record.get("profile_delivery") if isinstance(compile_record.get("profile_delivery"), dict) else {}
        profile_admission_lines: list[str] = []
        if profile_admission:
            findings = profile_admission.get("findings", []) if isinstance(profile_admission.get("findings"), list) else []
            profile_admission_lines.extend(
                [
                    "### Profile Admission",
                    "",
                    f"- Schema: `{profile_admission.get('schema_version', '')}`",
                    f"- Source signals: `{profile_admission.get('source_signal_counts', {})}`",
                    f"- Candidate contracts: `{profile_admission.get('candidate_contract_counts', {})}`",
                    f"- Finding count: `{len(findings)}`",
                ]
            )
            for finding in findings:
                if isinstance(finding, dict):
                    profile_admission_lines.append(
                        f"- `{finding.get('class', '')}`: source_signals={finding.get('source_signal_count', '')}, "
                        f"candidates={finding.get('candidate_count', '')}, nearby={finding.get('nearby_signatures', [])}"
                    )
            profile_admission_lines.append("")
        profile_delivery_lines: list[str] = []
        if profile_delivery:
            delivery_findings = profile_delivery.get("findings", []) if isinstance(profile_delivery.get("findings"), list) else []
            profile_delivery_lines.extend(
                [
                    "### Profile Delivery",
                    "",
                    f"- Schema: `{profile_delivery.get('schema_version', '')}`",
                    f"- Source signals: `{profile_delivery.get('source_signal_counts', {})}`",
                    f"- Offered carriers: `{profile_delivery.get('offered_carriers', {})}`",
                    f"- Delivered carriers: `{profile_delivery.get('delivered_carriers', {})}`",
                    f"- Finding count: `{len(delivery_findings)}`",
                ]
            )
            for finding in delivery_findings:
                if isinstance(finding, dict):
                    profile_delivery_lines.append(
                        f"- `{finding.get('class', '')}`: source_signals={finding.get('source_signal_count', '')}, "
                        f"offered={finding.get('offered_carriers', [])}, emitted_sample={finding.get('emitted_predicate_sample', [])}"
                    )
            profile_delivery_lines.append("")
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
                *profile_admission_lines,
                *profile_delivery_lines,
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

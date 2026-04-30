from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


SCHEMA_CONTRACT: dict[str, Any] = {
    "schema_version": "semantic_ir_v1",
    "decision": "commit|clarify|quarantine|reject|answer|mixed",
    "turn_type": "state_update|query|correction|rule_update|mixed|unknown",
    "entities": [
        {
            "id": "e1",
            "surface": "",
            "normalized": "",
            "type": "person|object|medication|lab_test|condition|symptom|place|time|unknown",
            "confidence": 0.0,
        }
    ],
    "referents": [
        {
            "surface": "it|her|his|that",
            "status": "resolved|ambiguous|unresolved",
            "candidates": ["e1"],
            "chosen": None,
        }
    ],
    "assertions": [
        {
            "kind": "direct|question|claim|correction|rule",
            "subject": "e1",
            "relation_concept": "",
            "object": "e2",
            "polarity": "positive|negative",
            "certainty": 0.0,
        }
    ],
    "unsafe_implications": [
        {
            "candidate": "",
            "why_unsafe": "",
            "commit_policy": "clarify|quarantine|reject",
        }
    ],
    "candidate_operations": [
        {
            "operation": "assert|retract|rule|query|none",
            "predicate": "",
            "args": [],
            "clause": "ancestor(X, Y) :- parent(X, Y).",
            "polarity": "positive|negative",
            "source": "direct|inferred|context",
            "safety": "safe|unsafe|needs_clarification",
        }
    ],
    "truth_maintenance": {
        "support_links": [
            {
                "operation_index": 0,
                "support_kind": "direct_utterance|context_clause|source_document|rule|claim|observation|correction|inference",
                "support_ref": "",
                "role": "grounds|retracts|conflicts_with|depends_on|derives|questions",
                "confidence": 0.0,
            }
        ],
        "conflicts": [
            {
                "new_operation_index": 0,
                "existing_ref": "",
                "conflict_kind": "functional_overwrite|claim_vs_observation|temporal_overlap|rule_violation|identity_ambiguity|polarity_conflict|unknown",
                "recommended_policy": "commit|mixed|clarify|quarantine|reject",
                "why": "",
            }
        ],
        "retraction_plan": [
            {
                "operation_index": 0,
                "target_ref": "",
                "reason": "explicit_correction|superseded_current_state|source_priority|temporal_update|other",
            }
        ],
        "derived_consequences": [
            {
                "statement": "",
                "basis": ["op:0"],
                "commit_policy": "query_only|quarantine|future_rule_support|do_not_commit",
            }
        ],
    },
    "temporal_graph": {
        "schema_version": "temporal_graph_v1",
        "events": [
            {
                "id": "ev1",
                "label": "",
                "participants": ["e1"],
                "source_status": "direct_assertion|claim|observation|inferred|context",
                "support_ref": "",
            }
        ],
        "time_anchors": [
            {
                "id": "t1",
                "value": "2026-04-29",
                "precision": "instant|day|month|year|relative|unknown",
                "source_status": "direct_assertion|claim|observation|inferred|context",
                "support_ref": "",
            }
        ],
        "intervals": [
            {
                "id": "i1",
                "start": "t1",
                "end": "t2",
                "source_status": "direct_assertion|claim|observation|inferred|context",
                "support_ref": "",
            }
        ],
        "edges": [
            {
                "relation": "before|after|during|overlaps|starts|ends|same_time|supersedes|unknown",
                "a": "ev1",
                "b": "ev2",
                "source_status": "direct_assertion|claim|observation|inferred|context",
                "support_ref": "",
            }
        ],
    },
    "clarification_questions": [""],
    "self_check": {
        "bad_commit_risk": "low|medium|high",
        "missing_slots": [],
        "notes": [],
    },
}


SEMANTIC_IR_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "decision",
        "turn_type",
        "entities",
        "referents",
        "assertions",
        "unsafe_implications",
        "candidate_operations",
        "truth_maintenance",
        "clarification_questions",
        "self_check",
    ],
    "properties": {
        "schema_version": {"type": "string", "const": "semantic_ir_v1"},
        "decision": {
            "type": "string",
            "enum": ["commit", "clarify", "quarantine", "reject", "answer", "mixed"],
        },
        "turn_type": {
            "type": "string",
            "enum": ["state_update", "query", "correction", "rule_update", "mixed", "unknown"],
        },
        "entities": {
            "type": "array",
            "maxItems": 64,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "surface", "normalized", "type", "confidence"],
                "properties": {
                    "id": {"type": "string"},
                    "surface": {"type": "string"},
                    "normalized": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": [
                            "person",
                            "object",
                            "medication",
                            "lab_test",
                            "condition",
                            "symptom",
                            "place",
                            "time",
                            "unknown",
                        ],
                    },
                    "confidence": {"type": "number"},
                },
            },
        },
        "referents": {
            "type": "array",
            "maxItems": 32,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["surface", "status", "candidates", "chosen"],
                "properties": {
                    "surface": {"type": "string"},
                    "status": {"type": "string", "enum": ["resolved", "ambiguous", "unresolved"]},
                    "candidates": {"type": "array", "items": {"type": "string"}},
                    "chosen": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                },
            },
        },
        "assertions": {
            "type": "array",
            "maxItems": 64,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["kind", "subject", "relation_concept", "object", "polarity", "certainty"],
                "properties": {
                    "kind": {"type": "string", "enum": ["direct", "question", "claim", "correction", "rule"]},
                    "subject": {"type": "string"},
                    "relation_concept": {"type": "string"},
                    "object": {"type": "string"},
                    "polarity": {"type": "string", "enum": ["positive", "negative"]},
                    "certainty": {"type": "number"},
                },
            },
        },
        "unsafe_implications": {
            "type": "array",
            "maxItems": 32,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["candidate", "why_unsafe", "commit_policy"],
                "properties": {
                    "candidate": {"type": "string"},
                    "why_unsafe": {"type": "string"},
                    "commit_policy": {"type": "string", "enum": ["clarify", "quarantine", "reject"]},
                },
            },
        },
        "candidate_operations": {
            "type": "array",
            "maxItems": 128,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["operation", "predicate", "args", "polarity", "source", "safety"],
                "properties": {
                    "operation": {"type": "string", "enum": ["assert", "retract", "rule", "query", "none"]},
                    "predicate": {"type": "string"},
                    "args": {"type": "array", "items": {"type": "string"}},
                    "clause": {"type": "string"},
                    "polarity": {"type": "string", "enum": ["positive", "negative"]},
                    "source": {"type": "string", "enum": ["direct", "inferred", "context"]},
                    "safety": {"type": "string", "enum": ["safe", "unsafe", "needs_clarification"]},
                },
            },
        },
        "truth_maintenance": {
            "type": "object",
            "additionalProperties": False,
            "required": ["support_links", "conflicts", "retraction_plan", "derived_consequences"],
            "properties": {
                "support_links": {
                    "type": "array",
                    "maxItems": 64,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["operation_index", "support_kind", "support_ref", "role", "confidence"],
                        "properties": {
                            "operation_index": {"type": "integer", "minimum": 0},
                            "support_kind": {
                                "type": "string",
                                "enum": [
                                    "direct_utterance",
                                    "context_clause",
                                    "source_document",
                                    "rule",
                                    "claim",
                                    "observation",
                                    "correction",
                                    "inference",
                                ],
                            },
                            "support_ref": {"type": "string"},
                            "role": {
                                "type": "string",
                                "enum": ["grounds", "retracts", "conflicts_with", "depends_on", "derives", "questions"],
                            },
                            "confidence": {"type": "number"},
                        },
                    },
                },
                "conflicts": {
                    "type": "array",
                    "maxItems": 32,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["new_operation_index", "existing_ref", "conflict_kind", "recommended_policy", "why"],
                        "properties": {
                            "new_operation_index": {"type": "integer", "minimum": 0},
                            "existing_ref": {"type": "string"},
                            "conflict_kind": {
                                "type": "string",
                                "enum": [
                                    "functional_overwrite",
                                    "claim_vs_observation",
                                    "temporal_overlap",
                                    "rule_violation",
                                    "identity_ambiguity",
                                    "polarity_conflict",
                                    "unknown",
                                ],
                            },
                            "recommended_policy": {
                                "type": "string",
                                "enum": ["commit", "mixed", "clarify", "quarantine", "reject"],
                            },
                            "why": {"type": "string"},
                        },
                    },
                },
                "retraction_plan": {
                    "type": "array",
                    "maxItems": 32,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["operation_index", "target_ref", "reason"],
                        "properties": {
                            "operation_index": {"type": "integer", "minimum": 0},
                            "target_ref": {"type": "string"},
                            "reason": {
                                "type": "string",
                                "enum": [
                                    "explicit_correction",
                                    "superseded_current_state",
                                    "source_priority",
                                    "temporal_update",
                                    "other",
                                ],
                            },
                        },
                    },
                },
                "derived_consequences": {
                    "type": "array",
                    "maxItems": 32,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["statement", "basis", "commit_policy"],
                        "properties": {
                            "statement": {"type": "string"},
                            "basis": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
                            "commit_policy": {
                                "type": "string",
                                "enum": ["query_only", "quarantine", "future_rule_support", "do_not_commit"],
                            },
                        },
                    },
                },
            },
        },
        "temporal_graph": {
            "type": "object",
            "additionalProperties": False,
            "required": ["schema_version", "events", "time_anchors", "intervals", "edges"],
            "properties": {
                "schema_version": {"type": "string", "const": "temporal_graph_v1"},
                "events": {
                    "type": "array",
                    "maxItems": 64,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["id", "label", "participants", "source_status", "support_ref"],
                        "properties": {
                            "id": {"type": "string"},
                            "label": {"type": "string"},
                            "participants": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
                            "source_status": {
                                "type": "string",
                                "enum": ["direct_assertion", "claim", "observation", "inferred", "context"],
                            },
                            "support_ref": {"type": "string"},
                        },
                    },
                },
                "time_anchors": {
                    "type": "array",
                    "maxItems": 64,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["id", "value", "precision", "source_status", "support_ref"],
                        "properties": {
                            "id": {"type": "string"},
                            "value": {"type": "string"},
                            "precision": {
                                "type": "string",
                                "enum": ["instant", "day", "month", "year", "relative", "unknown"],
                            },
                            "source_status": {
                                "type": "string",
                                "enum": ["direct_assertion", "claim", "observation", "inferred", "context"],
                            },
                            "support_ref": {"type": "string"},
                        },
                    },
                },
                "intervals": {
                    "type": "array",
                    "maxItems": 32,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["id", "start", "end", "source_status", "support_ref"],
                        "properties": {
                            "id": {"type": "string"},
                            "start": {"type": "string"},
                            "end": {"type": "string"},
                            "source_status": {
                                "type": "string",
                                "enum": ["direct_assertion", "claim", "observation", "inferred", "context"],
                            },
                            "support_ref": {"type": "string"},
                        },
                    },
                },
                "edges": {
                    "type": "array",
                    "maxItems": 64,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["relation", "a", "b", "source_status", "support_ref"],
                        "properties": {
                            "relation": {
                                "type": "string",
                                "enum": [
                                    "before",
                                    "after",
                                    "during",
                                    "overlaps",
                                    "starts",
                                    "ends",
                                    "same_time",
                                    "supersedes",
                                    "unknown",
                                ],
                            },
                            "a": {"type": "string"},
                            "b": {"type": "string"},
                            "source_status": {
                                "type": "string",
                                "enum": ["direct_assertion", "claim", "observation", "inferred", "context"],
                            },
                            "support_ref": {"type": "string"},
                        },
                    },
                },
            },
        },
        "clarification_questions": {"type": "array", "maxItems": 6, "items": {"type": "string"}},
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


UNGROUNDED_ARGUMENT_ATOMS = {
    "he",
    "him",
    "his",
    "she",
    "her",
    "hers",
    "they",
    "them",
    "their",
    "theirs",
    "it",
    "its",
    "this",
    "that",
    "patient",
    "person",
    "someone",
    "somebody",
    "unknown",
    "null",
    "none",
    "n_a",
    "na",
    "not_provided",
    "unspecified",
    "unknown_male",
    "unknown_female",
    "unknown_agent",
    "unknown_person",
    "unknown_actor",
    "male_actor",
    "female_actor",
}

IDENTITY_PREDICATES = {
    "candidate_identity",
    "same_person",
    "identity",
    "identified_as",
}


BEST_GUARDED_V2_SYSTEM = (
    "You are a semantic IR compiler for a governed symbolic memory system. "
    "The root object must be semantic_ir_v1 itself, with schema_version and decision as top-level keys. "
    "Do not wrap the answer under schema_contract, result, output, or semantic_ir. "
    "You do not answer the user and you do not commit durable truth. "
    "Use direct language understanding aggressively, but mark unsafe commitments explicitly."
)

DOCUMENT_TO_LOGIC_COMPILER_STRATEGY: dict[str, Any] = {
    "name": "document_to_logic_compiler_strategy_v1",
    "authority": "model_strategy_only_runtime_admission_remains_authoritative",
    "core_principle": (
        "Model the utterance or source's epistemic structure before choosing predicates: "
        "who says it, what status it has, whether it is durable, and how it can support later reasoning."
    ),
    "source_boundary": [
        "Identify whether the input is a user observation, source document, testimony, policy, contract, medical note, court record, fictional source, or ordinary conversation.",
        "Treat source documents, testimony, claims, allegations, grievances, and declarations as attributed speech/source acts unless external verification is present in context.",
        "Do not collapse source claims into objective world facts merely because they are confidently worded.",
    ],
    "assertion_status": [
        "Classify content before writing: durable fact, observation, claim/allegation/report, correction, rule/norm/obligation, query, unsafe implication, or test-only scaffold.",
        "Claims can become durable claim records; they do not become durable world facts unless the source context authorizes that promotion.",
        "For source-owned repeated records such as grievances, allegations, complaints, and accusations, preserve epistemic status explicitly when the allowed palette offers a status/provenance predicate. Useful labels include source_bound_accusation, source_claim, unverified_claim, observed_fact, and externally_confirmed_fact.",
        "Derived consequences belong in truth_maintenance unless the utterance directly states them or an executable rule/query needs them.",
    ],
    "entity_selection": [
        "Promote a term to an entity when it recurs, bears a role, acts, is acted on, names a source/document, identifies a group/institution/place/object, creates ambiguity pressure, or is needed for a later rule/query.",
        "Do not turn every noun phrase into an entity; low-query-value descriptive text can remain in labels, rule_text-style fields, or claim content.",
        "Preserve source-local names and explicit aliases; do not substitute model-prior names or famous-source defaults.",
    ],
    "predicate_selection": [
        "A predicate earns its place when it supports querying, inference, provenance, contradiction prevention, correction, repeated structure, or claim/fact separation.",
        "Prefer stable predicate families over one-off surface verbs when the source has repeated records such as grievances, docket entries, obligations, incidents, symptoms, clauses, or observations.",
        "Use the allowed predicate palette and contracts exactly. If the palette lacks a faithful relation, omit/quarantine the operation or keep it in assertions rather than mapping to an approximate predicate.",
        "Prefer source-attributed predicates for principles, legitimacy statements, accusations, character judgments, and other source-owned claims.",
    ],
    "repeated_structure_strategy": [
        "For list-like source material, use stable ids plus record/property predicates, for example record(id, label), actor(id, actor), target(id, target), method(id, method), purpose(id, purpose), effect(id, effect).",
        "For source-owned record lists, include an epistemic-status or provenance property keyed by the record id when the palette supports it, so later questions can distinguish accusations, claims, observations, and confirmed facts.",
        "Balance coverage across source boundary, entities, rules, representative records, conclusions, and commitments instead of spending the whole operation budget on the first repeated list.",
    ],
    "truth_maintenance_strategy": [
        "For every write/query/rule candidate, include support_links that explain what grounds it.",
        "For corrections, cite old KB/source support and propose explicit retract/assert operations when the target and replacement are clear.",
        "For conflicts, preserve the competing claim/observation/source states and recommend clarify/quarantine/mixed rather than silently overwriting.",
        "For temporal changes, preserve anchors and intervals durably when predicates allow them; a corrected date should retract or supersede the stale date anchor, not only the derived consequence.",
    ],
    "temporal_graph_strategy": [
        "When the utterance/source contains meaningful time, order, duration, interval, deadline, correction, or before/after language, include an optional temporal_graph_v1 proposal.",
        "Model temporal structure as event nodes, separated time anchors, intervals, and edges such as before, during, overlaps, or supersedes instead of burying all time information in labels.",
        "temporal_graph_v1 is proposal-only diagnostic structure. It does not create durable facts unless matching candidate_operations are separately emitted and admitted by the mapper.",
        "Preserve source_status and support_ref for temporal nodes and edges so claims, observations, direct assertions, and inferred ordering remain distinguishable.",
    ],
    "query_strategy": [
        "For questions, query the actual predicate surface available in allowed_predicates, predicate_contracts, and kb_context_pack examples.",
        "Use full predicate arity with uppercase variables for unknown slots.",
        "For multi-hop questions, emit several precise query operations rather than inventing a composite predicate.",
        "A query is not a durable truth claim; do not write the answer as a fact.",
    ],
    "self_check_questions": [
        "Can this be queried later?",
        "Does this preserve who said it?",
        "Am I treating a claim as a fact?",
        "Am I inventing a predicate or alias from model prior knowledge?",
        "Should this be a source-attributed record, a rule, a correction, a query, or a parked unsafe implication?",
    ],
}


BEST_GUARDED_V2_GUIDANCE = (
    "Decision policy:\n"
    "- reject: user asks for treatment, dose, medication stop/hold/start, or clinical recommendation. You may still include clarification questions, but the decision remains reject.\n"
    "- quarantine: direct facts conflict with a claim, a claim would overwrite observed state, or a candidate fact is plausible but unsafe.\n"
    "- clarify: missing referent, measurement direction, patient identity, object of 'it/that', or allergy-vs-intolerance distinction blocks a write.\n"
    "- mixed: same turn contains both safe writes and a query/rule/unsafe implication. If unsafe_implications is non-empty and safe operations are also present, decision MUST be mixed, not commit.\n"
    "- commit: direct state update or correction has a clear target and safe predicate mapping.\n"
    "Special guards:\n"
    "- Use compiler_strategy as the mental procedure before selecting predicates: establish source boundary, assertion status, entity value, predicate usefulness, repeated structure, and truth-maintenance implications.\n"
    "- Completeness beats summary. For narrative ingestion, enumerate every concrete direct event/state that can be safely mapped to allowed predicates; do not compress a sequence into only the main plot points.\n"
    "- Source fidelity is mandatory. Durable candidate_operations must be grounded in the current utterance, provided context, selected domain_context, or kb_context_pack. Do not import names, aliases, roles, motives, or facts from general world knowledge, famous stories, common versions of tales, or likely background priors.\n"
    "- Normalize entity atoms only for spelling/case/spacing/plural cleanup, explicit aliases in the utterance/context/domain ontology, or KB-resolved identity. If the utterance says 'Little Wee Bear', do not write baby_bear unless the utterance/context explicitly says Little Wee Bear is Baby Bear. Keep the text-local name as little_wee_bear and list any tempting prior alias in self_check.notes or unsafe_implications instead of committing it.\n"
    "- Preserve distinctive text-local names when forming atoms. Do not shorten a named phrase like 'Little Slip of an Otter' to little_otter when the source phrase contains identity-bearing words; use little_slip_of_an_otter unless an explicit alias is supplied.\n"
    "- Relation fidelity is mandatory. Do not map one relation to an approximate different predicate just to create a write. For example, 'went to gather X' is not gave(...), and group membership is member_of/2 when available, not is_a/2. If no allowed predicate matches the source relation, omit, quarantine, or keep it in assertions rather than committing a wrong predicate.\n"
    "- Use all needed candidate_operations up to the schema cap. If a turn contains more safe direct facts than fit in candidate_operations, choose mixed or clarify and put 'segment_required_for_complete_ingestion' in self_check.missing_slots/notes rather than silently summarizing.\n"
    "- Never repeat equivalent assertions, but do not drop distinct parallel facts such as three bowls, three chairs, and three beds.\n"
    "- For possession language such as 'has', 'had', 'owned', 'belonged to', or object/furnishing assignment, prefer owns/2 when available. Use carries/2 only for physical carrying/transporting/holding in hand, not for possession of furniture, bowls, beds, rooms, or ordinary belongings.\n"
    "- For ordinary story-world narration, prefer specific event/state predicates from allowed_predicates when present. Examples: is_a/2 for category, walked_through/2 or ran_through/2 for movement through a place, entered/2 and exited/2 for boundary crossing, found/2 for discovery, on/2 for physical support, tasted/2, ate/2 or ate_all/2 for consumption, sat_in/2 and lay_in/2 for chairs/beds, asleep_in/2 for sleeping location, broke/1 for a broken object, returned_home/1 for returning home, and too_hot_for/2, too_cold_for/2, too_hard_for/2, too_soft_for/2, just_right_for/2 for preference/fit evaluations.\n"
    "- If the story-world profile offers has_trait/2 and the utterance directly says an entity is too fizzy, too hot, too cold, too hard, too soft, just right, missing, tired, or otherwise described, preserve that source-local quality as has_trait(entity, trait) unless a more specific allowed predicate captures the exact relation. Do not drop the adjective/evaluation just because another event predicate such as tasted/2 was admitted.\n"
    "- Do not use inside/2 as a generic substitute for sitting, lying, tasting, eating, seeing, owning, or being about/near something. Use inside/2 only when the utterance says physical containment/interior location.\n"
    "- Do not use carries/2 for voices, properties, evidence, names, relationships, rooms, furniture, or ownership. If someone spoke or cried out and no speech predicate is available, represent it in assertions, not as a candidate_operation.\n"
    "- Do not create durable writes with placeholder actors such as unknown_agent/unknown_person/someone. If the actor is unknown but the object state is direct, use passive state predicates from allowed_predicates such as was_tasted/1, was_eaten/1, was_sat_in/1, or was_lain_in/1. Otherwise quarantine or omit the write.\n"
    "- Preserve stable object identity across segments. Reuse object atoms already present in context for the same object. For possessive story objects, prefer possessor-scoped atoms such as papa_bear_porridge, mama_bear_chair, or baby_bear_bed over generic size-only atoms like big_chair or small_bed. If size is mentioned, it may inform the object atom only when no possessor is available.\n"
    "- If a segment says an observer saw that an unknown person had acted on an object, commit the passive object state when available, not a vague saw(observer, event_something_...) write. Example: 'Papa saw someone had tasted his porridge' should prefer was_tasted(papa_bear_porridge) and omit the unknown actor/event wrapper unless a precise observed-event predicate is available.\n"
    "- Context entries are already-known state/rules, not new user assertions. Do not create candidate_operations that merely restate context.\n"
    "- Use context to resolve referents and answer queries; only the current utterance may introduce a new write candidate.\n"
    "- If the current utterance contains policy/rule language such as all/every/unless/must/before and also direct facts, choose mixed. Commit the direct facts and represent rule/policy material in assertions or unsafe_implications if no safe rule clause is available.\n"
    "- Preserve policy vocabulary and temporal anchors as symbolic terms when predicates allow it. For example, do not drop role aliases such as employee_seeking_reimbursement, announcement events such as launch_date, or relative expressions such as ten_days_after_service simply because the final rule/query result is not yet decidable.\n"
    "- If time/order/duration/interval/correction language is important, include temporal_graph_v1 as a proposal-only sub-IR with event nodes, time anchors, intervals, and temporal edges. Do not rely on temporal_graph_v1 to write facts; durable temporal facts still require candidate_operations that pass mapper admission.\n"
    "- Simple Horn rules such as 'if parent(X,Y) then ancestor(X,Y)' may commit as operation='rule' when you can emit a precise executable clause using allowed predicates. Put that Prolog-style text in candidate_operations[].clause. Default/exception rules with unless/except/only-if are not ordinary facts; if negation/exception semantics are unclear, choose mixed and represent the rule as a rule assertion or unsafe implication, not as a current fact.\n"
    "- Never mark a rule operation safe without an executable clause. If you cannot provide candidate_operations[].clause, do not emit a safe rule operation.\n"
    "- Existing current facts in context are state constraints. If a new utterance gives a different value for the same likely functional predicate such as lives_in/2 or scheduled_for/2, choose clarify unless the user explicitly marks it as a correction with words like correction, actually, wrong, not X, or instead.\n"
    "- If a new current-state write conflicts with kb_context_pack.current_state_candidates and the utterance is not an explicit correction, the top-level decision should be clarify, the write operation should be needs_clarification, and clarification_questions should ask whether the new value is intended to replace the old KB value.\n"
    "- If the new write would contradict a consequence implied by existing context rules and facts, choose clarify or quarantine. Do not assert the opposite fact until the user supplies an explicit correction, exception, or revocation.\n"
    "- If direct facts should be recorded but they create an unresolved conflict with context rules, choose mixed, keep the direct writes as safe operations, and describe the conflict in unsafe_implications/self_check. If self_check says there is a logical conflict or consistency check still needed, the decision should not be commit.\n"
    "- Use truth_maintenance to explain support, dependency, conflict, retraction, and derived-consequence structure. This block is a proposal/audit workspace only; it never authorizes writes. Every executable write/query still must appear in candidate_operations.\n"
    "- Every safe candidate_operation that writes, retracts, queries, or proposes a rule should have at least one truth_maintenance.support_links entry with the same operation_index. Use support_ref='current_utterance' for direct utterance support, or cite the exact context/KB clause when context grounds a correction, query, or conflict.\n"
    "- In truth_maintenance.conflicts, point to the candidate operation index and the existing context/source/rule it conflicts with. In truth_maintenance.retraction_plan, point to explicit correction targets. In derived_consequences, mark consequences query_only, quarantine, future_rule_support, or do_not_commit instead of committing them as facts.\n"
    "- kb_context_pack contains deterministic KB retrieval. Treat exact KB clauses as current committed state for resolving references, corrections, and conflicts. Do not restate KB clauses as new writes. Use candidate_operations only for the current utterance, and use truth_maintenance to cite KB support or conflict pressure.\n"
    "- If kb_context_pack.current_state_candidates contains an old current-state fact and the utterance explicitly corrects it with words like actually, instead, wrong, not X, or no longer, propose a safe retract for the old clause and a safe assert for the replacement when the target and replacement are clear.\n"
    "- If a pronoun or short referent has exactly one plausible entity in kb_context_pack.current_state_subject_candidates, and the utterance is an explicit correction of that entity's current state, you may resolve the referent from KB context and propose the retract/assert pair. If there are multiple plausible candidates, clarify instead.\n"
    "- If an explicit correction preserves the same ambiguous alias from an existing clause and changes only a non-identity slot such as date, room, status, or amount, you may retract/assert using the alias atom without resolving the underlying person. Treat the alias as the record key; identity ambiguity is irrelevant when the corrected clause keeps the same alias atom. Do not invent same_person or candidate_identity writes, and do not ask for clarification solely to resolve that preserved alias.\n"
    "- Do not ask for clarification solely because the subject is a pronoun when there is exactly one current_state_subject_candidate, no competing named subject, and an explicit correction marker. In that narrow case, set the referent status to resolved and cite the KB clause in truth_maintenance.\n"
    "- If the utterance says someone claims/alleges/reports a state that conflicts with an observed or source-backed KB clause, do not overwrite the observed/source-backed fact. If a claim predicate is available, record only the claim as a claim; otherwise quarantine or clarify.\n"
    "- Some predicates are non-exclusive, such as has_condition/2. A new compatible condition can be committed without retracting an existing different condition.\n"
    "- Do not turn a claim into a fact. 'Bob says he has it' is a claim, not possession.\n"
    "- Do not infer diagnosis or staging from a single lab value request. Quarantine or clarify.\n"
    "- Do not infer allergy from nausea/vomiting alone. Clarify allergy vs side effect/intolerance when the user only reports symptoms.\n"
    "- If the user explicitly says 'not allergic' and gives a side-effect/intolerance explanation such as nausea, the correction is clear: propose retracting the allergy and recording the side effect; do not ask for allergy-vs-intolerance clarification.\n"
    "- A clear correction like 'not Mara, Fred has it' may propose retract/assert.\n"
    "- Retraction is a governance operation, not a predicate. You may propose operation='retract' even when 'retract/1' is not in allowed_predicates.\n"
    "- candidate_operations[].predicate must be the bare predicate name such as lives_in, not a signature such as lives_in/2. The arity is implied by args.\n"
    "- Query operations must obey the arity in allowed_predicates and predicate_contracts. If a query asks for an unknown slot, keep the slot as a variable-like atom such as X, Who, What, or Blocker instead of dropping the argument. For example, if blocked_by/2 is allowed, ask blocked_by(launch, Blocker), not blocked_by(launch).\n"
    "- A correction like 'it should be quarantined instead' with context containing the old fact is enough to retract the old fact and assert the replacement fact; do not ask for authority/provenance unless the predicate itself requires it.\n"
    "- Do not invent required governance slots that are not in the predicate schema. Source document, authority, or reason fields are optional provenance unless the allowed predicate explicitly requires them.\n"
    "- A direct correction like 'remove X allergy; stomach upset only' is explicit enough to retract the allergy and record side effect/intolerance when the old allergy fact is in context.\n"
    "- Medical comparative labs can still be direct facts: 'lower than last week but still above the upper bound' means lab_result_high remains safe; do not require the numeric value unless the predicate requires a value slot.\n"
    "- 'Do not call it normal' is explicit negative classification; do not treat it as an ambiguous referent when the preceding lab test is clear.\n"
    "- Do not assert a fact about a quantified group atom such as submitted_form(residents) for 'all residents except Kai'. Use individual known members only when context enumerates them; otherwise mark the class-level write unsafe.\n"
    "- Pure hypothetical questions with 'if ... would ...?' are queries, not writes and not clarification requests when the hypothetical nature is clear. Mark the query operation safe; do not ask whether the user wants a hypothetical answer. Do not assert the hypothetical premise or any derived consequence as a fact.\n"
        "- Pure questions against context rules are answer turns. Do not choose mixed just because a context rule appears in context; context rules are support for the query, not new writes.\n"
        "- If the current utterance contains both a question and new grounded facts about named entities, keep the direct facts as safe candidate_operations and put the question in a query operation. Do not demote newly stated facts into background context just because they help answer the question.\n"
        "- If the current utterance contains new policy/rule language plus concrete entity facts, treat the concrete facts separately from the rule. The rule may be future_rule_support/quarantine when exception semantics are unclear, but direct facts such as customer status, approvals, blockers, observations, and dates remain candidate writes when grounded.\n"
        "- Candidate operation priority under the schema cap: direct grounded facts first, explicit retractions/corrections second, explicit user query third, durable rule clauses last. For complex default/exception/override policies, prefer preserving rule language in assertions, unsafe_implications, and truth_maintenance.derived_consequences rather than omitting concrete facts to fit rule clauses.\n"
        "- Narrative or meeting facts stated before a question are still new utterance facts, not query-only context, unless they are explicitly quoted as already-known context.\n"
        "- A query candidate_operation is not a durable truth claim. If the user asks a well-grounded question over available facts/rules, mark the query operation safe even when the possible answer should remain uncertain, query_only, or quarantined in truth_maintenance.derived_consequences.\n"
        "- If the utterance contains an explicit question and an allowed predicate can represent that question, include a query candidate_operation. Do not rely only on derived_consequences for the user's explicit question.\n"
        "- Compound questions such as 'who has A with B?' often contain more than one query target. When A and B map to allowed predicates, emit separate query candidate_operations for each target with shared variables or the named subject; do not collapse the whole question into only one query.\n"
        "- Query targets should be the specific subject or deliverable named in the utterance, not a generic class noun. If the user asks about 'checkout launch', prefer checkout_launch or checkout consistently over generic launch.\n"
        "- Decision labels must match candidate_operations: use answer only for pure query turns with no new write/retract/rule candidate_operations. If the utterance includes grounded writes plus a question, use mixed.\n"
        "- If a turn contains a negative assertion plus new rule/fact material and the negative assertion cannot safely become a durable fact, use mixed or quarantine rather than answer; the skipped negative assertion is still part of a mixed intake turn.\n"
    "- Necessary conditions are not sufficient conditions. 'No X without Y', 'X requires Y', and 'X depends on Y' may support requires/2 or depends_on/2 facts, but must not be inverted into X_allowed :- Y unless the utterance explicitly says Y is sufficient for X.\n"
    "- Negated condition/application language must not become a positive condition fact. If the utterance says a condition, forfeiture, exception, eligibility rule, or activation should not apply, is not met, should not activate, or is corrected away, do not assert that condition as true. A named condition inside a negative sentence is being discussed or denied, not asserted merely because it has a name. This applies across languages and noisy grammar: no/not/never/no deberia/ne doit pas/nicht/non should preserve denied activation. At most propose a retract of an existing matching positive clause, a safe replacement fact, a query, or a diagnostic assertion/unsafe implication.\n"
    "- Denial predicates are speech/event facts. 'Omar denied signing the waiver' may assert denied(...); it must not assert signed(...) false.\n"
    "- Legal findings are scoped speech/finding facts. 'The court did not find that Pavel paid' must not become negative paid(Pavel, ...). It is an absence of finding; use mixed/quarantine or a finding predicate if available.\n"
    "- 'Only after X did Y become effective; X happened Wednesday' is enough to commit Y's effective date as Wednesday when an effective_on predicate is allowed. Do not mark the effective date unsafe merely because it follows from the stated condition.\n"
    "- Do not include draft thoughts, reversals, or self-debate in unsafe_implications. If the final candidate_operations mark an operation safe, do not also list the same operation as unsafe.\n"
    "- When pronouns or referents are ambiguous and only a generic speech/container fact such as told/said/claimed is safe, choose clarify rather than committing the speech wrapper.\n"
    "- If context supplies exactly one active patient and one active lab test, a direct 'it came back high' may propose a safe lab_result_high write.\n"
        "- For rule-plus-fact or fact-plus-query turns, use mixed and keep unsafe query targets out of committed facts.\n"
    "- If predicate_contracts are present, obey their argument order exactly. A predicate may have the right arity but still be wrong if its argument roles are swapped.\n"
    "- Preserve negation in candidate_operations with polarity='negative'. Do not turn 'never saw X' into a positive saw/2 fact.\n"
    "- available_domain_profiles is a thin skill-like roster. Use it only to understand which domain context may be relevant; do not invent writes from unselected profile descriptions. domain_context and predicate_contracts are the thick selected-profile context."
)


@dataclass(frozen=True)
class SemanticIRCallConfig:
    backend: str = "ollama"
    base_url: str = "http://127.0.0.1:11434"
    model: str = "qwen3.6:35b"
    context_length: int = 16384
    timeout: int = 120
    temperature: float = 0.0
    top_p: float = 0.82
    top_k: int = 20
    think_enabled: bool = False
    reasoning_effort: str = "none"
    max_tokens: int = 12000


def build_semantic_ir_input_payload(
    *,
    utterance: str,
    context: list[str] | None = None,
    domain_context: list[str] | None = None,
    available_domain_profiles: list[dict[str, Any]] | None = None,
    allowed_predicates: list[str] | None = None,
    predicate_contracts: list[dict[str, Any]] | None = None,
    kb_context_pack: dict[str, Any] | None = None,
    domain: str = "runtime",
    include_schema_contract: bool = True,
) -> dict[str, Any]:
    payload = {
        "task": "Analyze the utterance and emit semantic_ir_v1 JSON only.",
        "output_instruction": "Return exactly one semantic_ir_v1 JSON object.",
        "domain": domain,
        "utterance": utterance,
        "context": context or [],
        "available_domain_profiles": available_domain_profiles or [],
        "domain_context": domain_context or [],
        "allowed_predicates": allowed_predicates or [],
        "predicate_contracts": predicate_contracts or [],
        "kb_context_pack": kb_context_pack or {},
        "source_fidelity_policy": {
            "commit_scope": "Only propose durable operations grounded in the current utterance, explicit context, selected domain context, or committed KB context.",
            "normalization_scope": [
                "Allowed: casing, punctuation, whitespace, morphology, and explicit aliases supplied by the utterance/context/domain ontology/KB.",
                "Not allowed: replacing a text-local name with a familiar name from model prior knowledge.",
                "Not allowed: adding roles/facts from a well-known source text unless the current input or context states them.",
            ],
            "alias_policy": [
                "If an alias is plausible but not source-grounded, keep the literal source name in candidate operations.",
                "Record the alias pressure in self_check.notes or unsafe_implications when relevant.",
                "Clarify or quarantine when the alias choice changes identity, role, or durable facts.",
            ],
            "relation_policy": [
                "Commit a predicate only when it preserves the source relation concept.",
                "Do not use an approximate predicate solely because it is available.",
                "Use member_of/2 for group membership when available; do not use is_a/2 for membership.",
                "Treat gathering/collecting, giving, owning, carrying, and being located at as different relations.",
            ],
        },
        "kb_context_policy": {
            "purpose": "Give the model compact visibility into committed KB state for reference resolution, correction handling, and conflict analysis.",
            "authority": "Context only. Durable effects still require admitted candidate_operations.",
            "do_not": [
                "Do not copy existing KB clauses into candidate_operations as new writes.",
                "Do not treat retrieved KB context as permission to infer unrelated facts.",
                "Do not overwrite observed/source-backed facts with a claim.",
            ],
            "correction_policy": [
                "Explicit correction markers such as actually, instead, wrong, not X, no longer, or correction can justify retract/assert against a matching current-state KB clause when target and replacement are clear.",
                "A conflicting current-state update without an explicit correction marker should clarify whether the new value replaces the old KB value.",
            ],
            "reference_policy": [
                "A pronoun may resolve from KB context only when exactly one plausible current_state_subject_candidate is relevant to the utterance.",
                "Do not ask solely because of the pronoun when there is one current_state_subject_candidate, no competing named subject, and an explicit correction marker.",
                "Multiple plausible KB candidates require clarification.",
            ],
            "claim_policy": "Claims, allegations, and reports remain speech/source facts. They do not overwrite observed/source-backed KB clauses.",
        },
        "compiler_strategy": DOCUMENT_TO_LOGIC_COMPILER_STRATEGY,
        "authority_boundary": "The runtime validates and commits; you only propose semantic structure.",
        "variant_guidance": BEST_GUARDED_V2_GUIDANCE,
    }
    if include_schema_contract:
        payload["required_top_level_json_shape"] = SCHEMA_CONTRACT
        payload["output_instruction"] = (
            "Return exactly one JSON object using required_top_level_json_shape as the root shape. "
            "Do not copy the key name required_top_level_json_shape into your response."
        )
    return payload


def build_semantic_ir_messages(
    *,
    utterance: str,
    context: list[str] | None = None,
    domain_context: list[str] | None = None,
    available_domain_profiles: list[dict[str, Any]] | None = None,
    allowed_predicates: list[str] | None = None,
    predicate_contracts: list[dict[str, Any]] | None = None,
    kb_context_pack: dict[str, Any] | None = None,
    domain: str = "runtime",
    include_schema_contract: bool = True,
) -> list[dict[str, str]]:
    payload = build_semantic_ir_input_payload(
        utterance=utterance,
        context=context,
        domain_context=domain_context,
        available_domain_profiles=available_domain_profiles,
        allowed_predicates=allowed_predicates,
        predicate_contracts=predicate_contracts,
        kb_context_pack=kb_context_pack,
        domain=domain,
        include_schema_contract=include_schema_contract,
    )
    return [
        {"role": "system", "content": BEST_GUARDED_V2_SYSTEM},
        {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
    ]


def call_semantic_ir(
    *,
    utterance: str,
    config: SemanticIRCallConfig,
    context: list[str] | None = None,
    domain_context: list[str] | None = None,
    available_domain_profiles: list[dict[str, Any]] | None = None,
    allowed_predicates: list[str] | None = None,
    predicate_contracts: list[dict[str, Any]] | None = None,
    kb_context_pack: dict[str, Any] | None = None,
    domain: str = "runtime",
    include_model_input: bool = False,
) -> dict[str, Any]:
    backend = str(config.backend or "ollama").strip().lower()
    input_payload = build_semantic_ir_input_payload(
        utterance=utterance,
        context=context,
        domain_context=domain_context,
        available_domain_profiles=available_domain_profiles,
        allowed_predicates=allowed_predicates,
        predicate_contracts=predicate_contracts,
        kb_context_pack=kb_context_pack,
        domain=domain,
        include_schema_contract=True,
    )
    messages = build_semantic_ir_messages(
        utterance=utterance,
        context=context,
        domain_context=domain_context,
        available_domain_profiles=available_domain_profiles,
        allowed_predicates=allowed_predicates,
        predicate_contracts=predicate_contracts,
        kb_context_pack=kb_context_pack,
        domain=domain,
        include_schema_contract=True,
    )
    if backend == "lmstudio":
        result = _call_lmstudio_semantic_ir(config=config, messages=messages)
    elif backend == "ollama":
        result = _call_ollama_semantic_ir(config=config, messages=messages)
    else:
        raise RuntimeError(f"semantic_ir_v1 backend not supported: {backend}")
    if include_model_input:
        result["model_input"] = {
            "backend": backend,
            "model": config.model,
            "messages": messages,
            "input_payload": input_payload,
            "options": {
                "temperature": float(config.temperature),
                "top_p": float(config.top_p),
                "top_k": int(config.top_k),
                "num_ctx": int(config.context_length),
                "max_tokens": int(config.max_tokens),
                "thinking": bool(config.think_enabled),
                "reasoning_effort": str(config.reasoning_effort or ""),
            },
        }
    return result


def _call_ollama_semantic_ir(*, config: SemanticIRCallConfig, messages: list[dict[str, str]]) -> dict[str, Any]:
    payload = {
        "model": config.model,
        "stream": False,
        "format": "json",
        "think": bool(config.think_enabled),
        "messages": messages,
        "options": {
            "temperature": float(config.temperature),
            "top_p": float(config.top_p),
            "top_k": int(config.top_k),
            "num_ctx": int(config.context_length),
        },
    }
    req = urllib.request.Request(
        f"{config.base_url.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=int(config.timeout)) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc)) from exc

    message = raw.get("message", {}) if isinstance(raw, dict) else {}
    content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
    parsed = parse_semantic_ir_json(content)
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "raw": raw,
        "content": content,
        "parsed": parsed,
    }


def _call_lmstudio_semantic_ir(*, config: SemanticIRCallConfig, messages: list[dict[str, str]]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": config.model,
        "messages": messages,
        "temperature": float(config.temperature),
        "top_p": float(config.top_p),
        "max_tokens": int(config.max_tokens),
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "semantic_ir_v1",
                "strict": True,
                "schema": SEMANTIC_IR_JSON_SCHEMA,
            },
        },
    }
    if str(config.reasoning_effort or "").strip():
        payload["reasoning_effort"] = str(config.reasoning_effort).strip()
    base_url = config.base_url.rstrip("/")
    endpoint = f"{base_url}/chat/completions" if base_url.endswith("/v1") else f"{base_url}/v1/chat/completions"
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
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
    if not content and isinstance(message, dict):
        content = str(message.get("reasoning_content", "") or "").strip()
    parsed = parse_semantic_ir_json(content)
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "raw": raw,
        "content": content,
        "parsed": parsed,
    }


def parse_semantic_ir_json(text: str) -> dict[str, Any] | None:
    raw = str(text or "").strip()
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    if "semantic_ir" in parsed and isinstance(parsed.get("semantic_ir"), dict):
        parsed = parsed["semantic_ir"]
    if str(parsed.get("schema_version", "")).strip() != "semantic_ir_v1":
        return None
    if not str(parsed.get("decision", "")).strip():
        return None
    return parsed


def semantic_ir_to_prethink_payload(ir: dict[str, Any]) -> dict[str, Any]:
    decision = _projected_decision(ir)
    intent = _intent_from_ir(ir)
    questions = _string_list(ir.get("clarification_questions"))
    risk = _bad_commit_risk(ir)
    needs_clarification = decision == "clarify" or bool(_missing_slots(ir))
    if decision in {"reject", "quarantine"}:
        intent = "other"
        needs_clarification = False
    uncertainty = {
        "low": 0.12,
        "medium": 0.48,
        "high": 0.86,
    }.get(risk, 0.48)
    if not needs_clarification and decision in {"commit", "mixed", "answer"} and _has_safe_direct_write(ir):
        uncertainty = min(uncertainty, 0.2)
    if needs_clarification:
        uncertainty = max(uncertainty, 0.82)
    return {
        "intent": intent,
        "logic_string": "",
        "components": {"atoms": [], "variables": [], "predicates": []},
        "facts": [],
        "rules": [],
        "queries": [],
        "confidence": _confidence_object(round(1.0 - min(max(uncertainty, 0.0), 1.0), 2)),
        "ambiguities": _semantic_ir_ambiguities(ir),
        "needs_clarification": needs_clarification,
        "uncertainty_score": round(uncertainty, 2),
        "uncertainty_label": "high" if uncertainty >= 0.67 else ("medium" if uncertainty >= 0.34 else "low"),
        "clarification_question": questions[0] if needs_clarification and questions else "",
        "clarification_reason": _semantic_ir_reason(ir, decision),
        "rationale": f"semantic_ir_v1 decision={decision}; risk={risk}",
    }


def semantic_ir_admission_diagnostics(
    ir: dict[str, Any],
    *,
    allowed_predicates: Any = None,
    predicate_contracts: Any = None,
) -> dict[str, Any]:
    """Explain mapper admission choices without granting authority.

    These diagnostics are intentionally deterministic and structural. They are
    a scorecard for traces and experiments, not a second admission path.
    """
    model_decision = _normalize_decision(ir.get("decision"))
    allowed_signatures = _allowed_predicate_signature_set(allowed_predicates)
    raw_contracts = predicate_contracts if predicate_contracts is not None else allowed_predicates
    contract_map = _predicate_contract_map(raw_contracts)
    contract_details = _predicate_contract_detail_map(raw_contracts)
    predicate_aliases = _predicate_alias_map(raw_contracts)
    ir_for_admission = _ir_with_predicate_aliases(ir, predicate_aliases)
    if not allowed_signatures and contract_map:
        allowed_signatures = set(contract_map)
    projected_decision = _projected_decision(
        ir_for_admission,
        allowed_signatures=allowed_signatures,
        contract_map=contract_map,
        contract_details=contract_details,
    )
    operations: list[dict[str, Any]] = []
    warning_counts: dict[str, int] = {}
    admitted_count = 0
    skipped_count = 0
    clauses_by_effect: dict[str, list[str]] = {
        "facts": [],
        "rules": [],
        "queries": [],
        "retracts": [],
    }
    supports_by_effect: dict[str, list[dict[str, Any]]] = {
        "facts": [],
        "rules": [],
        "queries": [],
        "retracts": [],
    }
    entity_names = _entity_name_map(ir_for_admission)
    entity_meta = _entity_metadata_map(ir_for_admission)
    admitted_clause_keys: set[tuple[str, str]] = set()
    temporal_invalid_operation_indexes = _temporal_invalid_operation_indexes(ir_for_admission, entity_names=entity_names)
    for index, op in enumerate(_candidate_operations(ir_for_admission)):
        diagnosis = _diagnose_candidate_operation(
            ir_for_admission,
            op,
            index=index,
            entity_names=entity_names,
            entity_meta=entity_meta,
            allowed_signatures=allowed_signatures,
            contract_map=contract_map,
            contract_details=contract_details,
            temporal_invalid_operation_indexes=temporal_invalid_operation_indexes,
        )
        if (
            projected_decision in {"reject", "quarantine", "clarify"}
            and bool(diagnosis.get("admitted"))
            and str(diagnosis.get("effect", "")).strip()
            in (
                {"fact", "rule", "retract", "query"}
                if projected_decision in {"reject", "quarantine"}
                else {"fact", "rule", "retract"}
            )
        ):
            diagnosis = dict(diagnosis)
            diagnosis["blocked_effect"] = str(diagnosis.get("effect", "")).strip()
            diagnosis["blocked_clauses"] = [
                str(item).strip()
                for item in diagnosis.get("clauses", [])
                if str(item).strip()
            ]
            diagnosis["admitted"] = False
            diagnosis["skip_reason"] = f"projected_decision_{projected_decision}_blocks_write"
            diagnosis["clauses"] = []
            diagnosis["rationale_codes"] = list(diagnosis.get("rationale_codes", [])) + [
                "decision_projection_gate"
            ]
        if bool(diagnosis.get("admitted")):
            effect = str(diagnosis.get("effect", "")).strip()
            clauses = [str(item).strip() for item in diagnosis.get("clauses", []) if str(item).strip()]
            duplicate_clause = next(
                (
                    clause
                    for clause in clauses
                    if (effect, clause) in admitted_clause_keys
                ),
                "",
            )
            if duplicate_clause:
                diagnosis = dict(diagnosis)
                diagnosis["admitted"] = False
                diagnosis["skip_reason"] = "duplicate_candidate_operation"
                diagnosis["warning"] = "skipped duplicate candidate operation"
                diagnosis["clauses"] = []
                diagnosis["rationale_codes"] = list(diagnosis.get("rationale_codes", [])) + [
                    "duplicate_operation_gate"
                ]
            else:
                for clause in clauses:
                    admitted_clause_keys.add((effect, clause))
        diagnosis["admission_justification"] = _operation_admission_justification(diagnosis)
        operations.append(diagnosis)
        warning = str(diagnosis.get("warning", "")).strip()
        if warning:
            warning_counts[warning] = warning_counts.get(warning, 0) + 1
        if bool(diagnosis.get("admitted")):
            admitted_count += 1
            effect = str(diagnosis.get("effect", "")).strip()
            clauses = [str(item).strip() for item in diagnosis.get("clauses", []) if str(item).strip()]
            if effect == "fact":
                clauses_by_effect["facts"].extend(clauses)
                supports_by_effect["facts"].extend(_clause_support_records(diagnosis, clauses))
            elif effect == "rule":
                clauses_by_effect["rules"].extend(clauses)
                supports_by_effect["rules"].extend(_clause_support_records(diagnosis, clauses))
            elif effect == "query":
                clauses_by_effect["queries"].extend(clauses)
                supports_by_effect["queries"].extend(_clause_support_records(diagnosis, clauses))
            elif effect == "retract":
                clauses_by_effect["retracts"].extend(clauses)
                supports_by_effect["retracts"].extend(_clause_support_records(diagnosis, clauses))
        else:
            skipped_count += 1

    features = _admission_feature_summary(
        ir_for_admission,
        allowed_signatures=allowed_signatures,
        contract_map=contract_map,
        contract_details=contract_details,
    )
    truth_maintenance = _truth_maintenance_summary(ir_for_admission)
    temporal_graph = _temporal_graph_summary(ir_for_admission)
    epistemic_worlds = _epistemic_worlds_summary(
        projected_decision,
        operations,
        truth_maintenance=truth_maintenance,
    )
    return {
        "version": "admission_diagnostics_v1",
        "authority": "diagnostic_only_mapper_remains_authoritative",
        "model_decision": model_decision,
        "projected_decision": projected_decision,
        "projection_reason": _projection_reason(
            ir_for_admission,
            model_decision,
            projected_decision,
            allowed_signatures=allowed_signatures,
            contract_map=contract_map,
            contract_details=contract_details,
        ),
        "predicate_alias_count": len(predicate_aliases),
        "predicate_aliases_applied": _predicate_alias_applications(ir, predicate_aliases),
        "features": features,
        "operation_count": len(operations),
        "admitted_count": admitted_count,
        "skipped_count": skipped_count,
        "warning_counts": dict(sorted(warning_counts.items())),
        "clauses": clauses_by_effect,
        "clause_supports": supports_by_effect,
        "admission_justifications": [
            item.get("admission_justification", {})
            for item in operations
            if isinstance(item, dict) and isinstance(item.get("admission_justification"), dict)
        ],
        "truth_maintenance": truth_maintenance,
        "temporal_graph": temporal_graph,
        "truth_maintenance_alignment": _truth_maintenance_alignment(
            truth_maintenance,
            operations,
            projected_decision=projected_decision,
            epistemic_worlds=epistemic_worlds,
        ),
        "epistemic_worlds": epistemic_worlds,
        "operations": operations,
    }


def semantic_ir_to_legacy_parse(
    ir: dict[str, Any],
    *,
    allowed_predicates: Any = None,
    predicate_contracts: Any = None,
) -> tuple[dict[str, Any], list[str]]:
    allowed_signatures = _allowed_predicate_signature_set(allowed_predicates)
    raw_contracts = predicate_contracts if predicate_contracts is not None else allowed_predicates
    contract_map = _predicate_contract_map(raw_contracts)
    contract_details = _predicate_contract_detail_map(raw_contracts)
    predicate_aliases = _predicate_alias_map(raw_contracts)
    ir_for_admission = _ir_with_predicate_aliases(ir, predicate_aliases)
    if not allowed_signatures and contract_map:
        allowed_signatures = set(contract_map)
    decision = _projected_decision(
        ir_for_admission,
        allowed_signatures=allowed_signatures,
        contract_map=contract_map,
        contract_details=contract_details,
    )
    facts: list[str] = []
    rules: list[str] = []
    queries: list[str] = []
    retracts: list[str] = []
    diagnostics = semantic_ir_admission_diagnostics(
        ir,
        allowed_predicates=allowed_signatures,
        predicate_contracts=raw_contracts,
    )
    warnings = [
        str(item.get("warning", "")).strip()
        for item in diagnostics.get("operations", [])
        if isinstance(item, dict) and str(item.get("warning", "")).strip()
    ]

    for item in diagnostics.get("operations", []):
        if not isinstance(item, dict) or not bool(item.get("admitted")):
            continue
        effect = str(item.get("effect", "")).strip()
        clauses = [str(clause).strip() for clause in item.get("clauses", []) if str(clause).strip()]
        if effect == "fact":
            facts.extend(clauses)
        elif effect == "query":
            queries.extend(clauses)
        elif effect == "retract":
            retracts.extend(clauses)
        elif effect == "rule":
            rules.extend(clauses)

    if decision in {"reject", "quarantine", "clarify"}:
        facts = []
        rules = []
        queries = [] if decision != "clarify" else queries
        retracts = []

    intent = _legacy_intent(facts=facts, rules=rules, queries=queries, retracts=retracts, decision=decision)
    if intent == "assert_fact":
        logic_parts = facts
    elif intent == "assert_rule":
        logic_parts = rules
    elif intent == "query":
        logic_parts = queries
    else:
        logic_parts = facts + rules + queries
    if not logic_parts and retracts:
        logic_parts = [_retract_command(clause) for clause in retracts]
    payload = {
        "intent": intent,
        "logic_string": " ".join(logic_parts),
        "components": _components_from_clauses(logic_parts),
        "facts": facts,
        "rules": rules,
        "queries": queries,
        "confidence": _confidence_object(0.9 if decision in {"commit", "answer", "mixed"} else 0.25),
        "ambiguities": _semantic_ir_ambiguities(ir_for_admission),
        "needs_clarification": decision == "clarify",
        "uncertainty_score": 0.85 if decision == "clarify" else (0.65 if decision in {"quarantine", "reject"} else 0.2),
        "uncertainty_label": "high" if decision == "clarify" else ("medium" if decision in {"quarantine", "reject"} else "low"),
        "clarification_question": _first_question(ir_for_admission) if decision == "clarify" else "",
        "clarification_reason": _semantic_ir_reason(ir_for_admission, decision) if decision == "clarify" else "",
        "rationale": f"Mapped from semantic_ir_v1 decision={decision}; skipped={len(warnings)}",
        "admission_diagnostics": diagnostics,
        "clause_supports": diagnostics.get("clause_supports", {}),
        "truth_maintenance": diagnostics.get("truth_maintenance", {}),
        "temporal_graph": diagnostics.get("temporal_graph", {}),
        "epistemic_worlds": diagnostics.get("epistemic_worlds", {}),
    }
    if retracts:
        payload["correction_retract_clauses"] = retracts
    return payload, warnings


def _temporal_graph_summary(ir: dict[str, Any]) -> dict[str, Any]:
    graph = ir.get("temporal_graph") if isinstance(ir, dict) else None
    if not isinstance(graph, dict):
        return {
            "version": "temporal_graph_v1",
            "authority": "proposal_only_no_durable_effect_without_candidate_operations",
            "present": False,
            "event_count": 0,
            "time_anchor_count": 0,
            "interval_count": 0,
            "edge_count": 0,
            "events": [],
            "time_anchors": [],
            "intervals": [],
            "edges": [],
        }

    def bounded_rows(key: str, fields: list[str], limit: int) -> list[dict[str, str]]:
        rows = graph.get(key, [])
        if not isinstance(rows, list):
            return []
        out: list[dict[str, str]] = []
        for row in rows[:limit]:
            if not isinstance(row, dict):
                continue
            out.append({field: _bounded_text(row.get(field), max_chars=160) for field in fields})
        return out

    events = graph.get("events", []) if isinstance(graph.get("events"), list) else []
    anchors = graph.get("time_anchors", []) if isinstance(graph.get("time_anchors"), list) else []
    intervals = graph.get("intervals", []) if isinstance(graph.get("intervals"), list) else []
    edges = graph.get("edges", []) if isinstance(graph.get("edges"), list) else []
    return {
        "version": "temporal_graph_v1",
        "authority": "proposal_only_no_durable_effect_without_candidate_operations",
        "present": True,
        "event_count": len(events),
        "time_anchor_count": len(anchors),
        "interval_count": len(intervals),
        "edge_count": len(edges),
        "events": bounded_rows("events", ["id", "label", "source_status", "support_ref"], 12),
        "time_anchors": bounded_rows("time_anchors", ["id", "value", "precision", "source_status", "support_ref"], 12),
        "intervals": bounded_rows("intervals", ["id", "start", "end", "source_status", "support_ref"], 8),
        "edges": bounded_rows("edges", ["relation", "a", "b", "source_status", "support_ref"], 12),
    }


def _epistemic_worlds_summary(
    projected_decision: str,
    operations: list[dict[str, Any]],
    *,
    truth_maintenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    worlds: dict[str, dict[str, Any]] = {}
    world_clauses: list[str] = []
    world_operation_count = 0
    decision = str(projected_decision or "").strip().lower()
    support_indexes = {
        int(item.get("operation_index"))
        for item in (truth_maintenance or {}).get("support_links", [])
        if isinstance(item, dict) and _operation_index(item.get("operation_index")) is not None
    }
    retraction_plans_by_index: dict[int, list[dict[str, str]]] = {}
    for item in (truth_maintenance or {}).get("retraction_plan", []):
        if not isinstance(item, dict):
            continue
        index = _operation_index(item.get("operation_index"))
        if index is None:
            continue
        retraction_plans_by_index.setdefault(index, []).append(
            {
                "target_ref": _bounded_text(item.get("target_ref"), max_chars=400),
                "reason": _bounded_text(item.get("reason"), max_chars=80),
            }
        )
    for op in operations:
        if not isinstance(op, dict):
            continue
        index = _operation_index(op.get("index"))
        blocked_clauses = [
            str(item).strip()
            for item in op.get("blocked_clauses", [])
            if str(item).strip()
        ]
        operation = str(op.get("operation") or "").strip().lower()
        predicate = _predicate_name(op.get("predicate")) or "unknown"
        args = [str(arg).strip() for arg in op.get("args", []) if str(arg).strip()]
        effect = _atomize(str(op.get("blocked_effect") or op.get("effect") or "fact"))
        admitted_retract = bool(op.get("admitted")) and effect == "retract"
        scoped_retraction_plans = (
            retraction_plans_by_index.get(index, [])
            if index is not None and not admitted_retract
            else []
        )
        supported_but_skipped = (
            index is not None
            and index in support_indexes
            and not bool(op.get("admitted"))
            and operation in {"assert", "rule", "retract", "query"}
            and predicate != "unknown"
            and bool(args)
        )
        if not blocked_clauses and not supported_but_skipped and not scoped_retraction_plans:
            continue
        if scoped_retraction_plans:
            world_id = "retraction_plan_world"
        else:
            world_id = _epistemic_world_id(decision if blocked_clauses else "skipped")
        world = worlds.setdefault(
            world_id,
            {
                "world_id": world_id,
                "world_type": (
                    "retraction_plan"
                    if scoped_retraction_plans
                    else decision if blocked_clauses else "skipped_supported"
                ),
                "authority": "scoped_memory_not_global_truth",
                "operations": [],
                "clauses": [],
            },
        )
        op_id = f"op_{index if index is not None else world_operation_count}"
        source = _atomize(str(op.get("source") or "unknown"))
        safety = _atomize(str(op.get("safety") or "unknown"))
        skip_reason = _atomize(str(op.get("skip_reason") or "projected_decision_blocks_write"))
        if scoped_retraction_plans:
            policy = "retraction_plan_only"
        else:
            policy = decision if blocked_clauses and decision else "skipped"
        clauses = [
            _clause("world_operation", [world_id, op_id, predicate, effect]),
            _clause("world_policy", [world_id, op_id, policy]),
            _clause("world_source", [world_id, op_id, source]),
            _clause("world_safety", [world_id, op_id, safety]),
            _clause("world_skip_reason", [world_id, op_id, skip_reason]),
        ]
        for arg_index, arg in enumerate(args, start=1):
            clauses.append(_clause("world_arg", [world_id, op_id, str(arg_index), _atomize(arg)]))
        for clause_index, clause in enumerate(blocked_clauses, start=1):
            clauses.append(
                _clause(
                    "world_clause",
                    [world_id, op_id, str(clause_index), _atomize(clause)],
                )
            )
        for plan_index, plan in enumerate(scoped_retraction_plans, start=1):
            target_ref = _atomize(plan.get("target_ref") or "unknown_target")
            reason = _atomize(plan.get("reason") or "unspecified")
            clauses.append(_clause("world_retraction_target", [world_id, op_id, str(plan_index), target_ref]))
            clauses.append(_clause("world_retraction_reason", [world_id, op_id, str(plan_index), reason]))
        operation_record = {
            "operation_index": op.get("index"),
            "world_id": world_id,
            "world_operation_id": op_id,
            "predicate": predicate,
            "effect": effect,
            "source": source,
            "safety": safety,
            "skip_reason": str(op.get("skip_reason") or ""),
            "args": args,
            "blocked_clauses": blocked_clauses,
            "retraction_plans": scoped_retraction_plans,
            "world_clauses": clauses,
        }
        world["operations"].append(operation_record)
        world["clauses"].extend(clauses)
        world_clauses.extend(clauses)
        world_operation_count += 1

    return {
        "version": "epistemic_worlds_v1",
        "authority": "diagnostic_only_scoped_memory_does_not_mutate_global_truth",
        "world_count": len(worlds),
        "operation_count": world_operation_count,
        "clauses": world_clauses,
        "worlds": list(worlds.values()),
    }


def _epistemic_world_id(projected_decision: str) -> str:
    decision = _atomize(projected_decision)
    if decision in {"reject", "quarantine", "clarify"}:
        return f"{decision}_world"
    if decision == "skipped":
        return "skipped_world"
    return "scoped_world"


def _operation_admission_justification(diagnosis: dict[str, Any]) -> dict[str, Any]:
    admitted = bool(diagnosis.get("admitted"))
    rationale_codes = [
        str(item).strip()
        for item in diagnosis.get("rationale_codes", [])
        if str(item).strip()
    ]
    features = diagnosis.get("features", {}) if isinstance(diagnosis.get("features"), dict) else {}
    accepted_because: list[str] = []
    blocked_because: list[str] = []

    if admitted:
        accepted_because.extend(_human_rationale(code) for code in rationale_codes)
        if features.get("predicate_in_allowed_palette") is True:
            accepted_because.append("predicate signature is in the active allowed palette")
        if features.get("predicate_contract_enabled") is True and not features.get("contract_role_mismatch"):
            accepted_because.append("predicate contract roles passed structural validation")
        if str(diagnosis.get("safety") or "").strip() == "safe":
            accepted_because.append("candidate operation was explicitly marked safe by the semantic workspace")
        if str(diagnosis.get("source") or "").strip() == "direct":
            accepted_because.append("candidate operation is sourced directly from the current utterance")
    else:
        blocked_because.extend(_human_rationale(code) for code in rationale_codes)
        skip_reason = str(diagnosis.get("skip_reason") or "").strip()
        if skip_reason and skip_reason not in rationale_codes:
            blocked_because.append(_human_rationale(skip_reason))
        warning = str(diagnosis.get("warning") or "").strip()
        if warning:
            blocked_because.append(warning)

    return {
        "operation_index": diagnosis.get("index"),
        "predicate": diagnosis.get("predicate"),
        "operation": diagnosis.get("operation"),
        "effect": diagnosis.get("effect"),
        "admitted": admitted,
        "clauses": diagnosis.get("clauses", []),
        "accepted_because": _dedupe_text(accepted_because),
        "blocked_because": _dedupe_text(blocked_because),
        "rationale_codes": rationale_codes,
    }


def _human_rationale(code: str) -> str:
    code = str(code or "").strip()
    mapping = {
        "safe_direct_fact": "safe direct fact candidate",
        "safe_fact": "safe fact candidate",
        "safe_query": "safe query candidate",
        "safe_retract": "safe explicit retraction candidate",
        "safe_rule_clause": "safe explicit rule clause",
        "safe_rule_record_without_clause": "safe direct rule-like record without executable clause",
        "rule_label_demoted_to_fact_record": "rule label treated as a fact record because no executable clause was supplied",
        "candidate_safety_gate": "candidate operation was not marked safe",
        "source_policy": "source policy blocks durable write",
        "inference_not_truth": "inferred candidate is not durable truth",
        "context_is_not_new_write": "context-sourced material is not a new write",
        "predicate_shape_gate": "predicate name failed structural validation",
        "predicate_palette_gate": "predicate signature is outside the active allowed palette",
        "predicate_contract_gate": "predicate contract validation failed",
        "contract_policy_gate": "profile contract policy blocked the operation",
        "temporal_policy": "temporal policy blocked the operation",
        "interval_order_gate": "interval start/end ordering is invalid",
        "polarity_policy": "polarity policy blocked a general negative fact",
        "no_general_negative_fact_system": "general negative fact semantics are not supported yet",
        "rule_policy": "rule policy blocked the operation",
        "no_rule_synthesis": "durable rule synthesis requires an explicit clause",
        "variable_args_not_fact": "variable-like rule arguments cannot be demoted into facts",
        "operation_policy": "operation type is unsupported",
        "duplicate_operation_gate": "duplicate candidate operation was collapsed",
        "decision_projection_gate": "projected turn decision blocks this write",
        "quantifier_policy": "quantified set needs expansion before durable write",
        "no_group_atom_commit": "group/set atom cannot stand in for individual facts",
        "hypothetical_policy": "hypothetical/query-scoped premise is not durable truth",
        "identity_premise_not_truth": "identity premise was scoped to a query, not a committed fact",
        "hypothetical_inferred_query_exception": "inferred candidate was allowed only as a query",
    }
    return mapping.get(code, code.replace("_", " "))


def _dedupe_text(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        text = str(item or "").strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
    return out


def _diagnose_candidate_operation(
    ir: dict[str, Any],
    op: dict[str, Any],
    *,
    index: int,
    entity_names: dict[str, str],
    entity_meta: dict[str, dict[str, Any]],
    allowed_signatures: set[tuple[str, int]],
    contract_map: dict[tuple[str, int], list[str]],
    contract_details: dict[tuple[str, int], dict[str, Any]],
    temporal_invalid_operation_indexes: set[int],
) -> dict[str, Any]:
    operation = str(op.get("operation", "")).strip().lower()
    safety = str(op.get("safety", "")).strip().lower()
    source = str(op.get("source", "")).strip().lower()
    polarity = str(op.get("polarity", "positive") or "positive").strip().lower()
    predicate = _predicate_name(op.get("predicate"))
    args = _operation_args(op.get("args"), entity_names=entity_names, for_query=operation == "query")
    base = {
        "index": index,
        "operation": operation,
        "predicate": predicate,
        "args": args,
        "polarity": polarity,
        "source": source,
        "safety": safety,
        "admitted": False,
        "effect": "skip",
        "clauses": [],
        "skip_reason": "",
        "warning": "",
        "rationale_codes": [],
        "features": _operation_feature_summary(
            ir,
            predicate=predicate,
            args=args,
            operation=operation,
            source=source,
            safety=safety,
            polarity=polarity,
            allowed_signatures=allowed_signatures,
            contract_map=contract_map,
        ),
    }

    def skip(reason: str, *, warning: str = "", codes: list[str] | None = None) -> dict[str, Any]:
        base["skip_reason"] = reason
        base["warning"] = warning
        base["rationale_codes"] = codes or [reason]
        return base

    if safety != "safe":
        return skip("operation_not_marked_safe", codes=["candidate_safety_gate"])
    if source == "inferred" and operation != "query":
        return skip(
            "inferred_write_not_admissible",
            warning="skipped inferred safe operation pending policy",
            codes=["source_policy", "inference_not_truth"],
        )
    if source == "context" and operation in {"assert", "rule"}:
        return skip(
            "context_write_not_admissible",
            warning="skipped context-sourced write operation",
            codes=["source_policy", "context_is_not_new_write"],
        )
    if not predicate:
        return skip("invalid_predicate_name", codes=["predicate_shape_gate"])
    grounding_problem = _generic_grounding_problem(predicate, args, operation=operation)
    if grounding_problem:
        return skip(
            str(grounding_problem["reason"]),
            warning=str(grounding_problem["warning"]),
            codes=list(grounding_problem["codes"]),
        )
    if operation == "assert" and _operation_targets_quantified_set(op, entity_meta):
        return skip(
            "quantified_group_without_expansion",
            warning="skipped quantified set assertion without individual expansion",
            codes=["quantifier_policy", "no_group_atom_commit"],
        )
    if operation == "assert" and _is_query_scoped_identity_premise(ir, predicate):
        return skip(
            "query_scoped_identity_premise_not_admissible",
            warning="skipped identity premise scoped to a query",
            codes=["hypothetical_policy", "identity_premise_not_truth"],
        )
    palette_problem = _operation_palette_problem(
        op,
        predicate=predicate,
        args=args,
        operation=operation,
        allowed_signatures=allowed_signatures,
    )
    if palette_problem:
        return skip(
            str(palette_problem["reason"]),
            warning=str(palette_problem["warning"]),
            codes=list(palette_problem["codes"]),
        )
    contract_problem = _operation_contract_role_problem(
        op,
        predicate=predicate,
        args=args,
        operation=operation,
        entity_meta=entity_meta,
        contract_map=contract_map,
    )
    if contract_problem:
        return skip(
            str(contract_problem["reason"]),
            warning=str(contract_problem["warning"]),
            codes=list(contract_problem["codes"]),
        )
    contract_policy_problem = _operation_contract_policy_problem(
        predicate=predicate,
        args=args,
        operation=operation,
        contract_map=contract_map,
        contract_details=contract_details,
    )
    if contract_policy_problem:
        return skip(
            str(contract_policy_problem["reason"]),
            warning=str(contract_policy_problem["warning"]),
            codes=list(contract_policy_problem["codes"]),
        )
    if index in temporal_invalid_operation_indexes:
        return skip(
            "temporal_interval_order_mismatch",
            warning=f"skipped {predicate}/{len(args)} because interval start is after interval end",
            codes=["temporal_policy", "interval_order_gate"],
        )
    if polarity == "negative" and operation == "assert" and not _is_negative_event_predicate(predicate):
        return skip(
            "negative_fact_semantics_not_supported",
            warning="skipped negative assertion pending explicit negation policy",
            codes=["polarity_policy", "no_general_negative_fact_system"],
        )
    if operation == "rule":
        clause = str(op.get("clause") or op.get("logic") or "").strip()
        if not clause:
            if _operation_has_variable_like_raw_arg(op):
                return skip(
                    "rule_clause_missing",
                    warning="skipped rule operation with variable-like args but no executable clause",
                    codes=["rule_policy", "no_rule_synthesis", "variable_args_not_fact"],
                )
            if args and source == "direct" and polarity == "positive":
                base["admitted"] = True
                base["effect"] = "fact"
                base["clauses"] = [_clause(predicate, args)]
                base["rationale_codes"] = ["safe_rule_record_without_clause", "rule_label_demoted_to_fact_record"]
                return base
            return skip(
                "rule_clause_missing",
                warning="skipped rule operation without explicit clause",
                codes=["rule_policy", "no_rule_synthesis"],
            )
        base["admitted"] = True
        base["effect"] = "rule"
        base["clauses"] = [_ensure_period(clause)]
        base["rationale_codes"] = ["safe_rule_clause"]
        return base
    if operation == "assert":
        base["admitted"] = True
        base["effect"] = "fact"
        base["clauses"] = [_clause(predicate, args)]
        base["rationale_codes"] = ["safe_direct_fact" if source == "direct" else "safe_fact"]
        return base
    if operation == "query":
        base["admitted"] = True
        base["effect"] = "query"
        base["clauses"] = [_clause(predicate, args)]
        base["rationale_codes"] = ["safe_query"]
        if source == "inferred":
            base["rationale_codes"].append("hypothetical_inferred_query_exception")
        return base
    if operation == "retract":
        base["admitted"] = True
        base["effect"] = "retract"
        base["clauses"] = _retract_clause_variants(predicate, args)
        base["rationale_codes"] = ["safe_retract"]
        return base
    return skip("unsupported_operation", codes=["operation_policy"])


def _operation_has_variable_like_raw_arg(op: dict[str, Any]) -> bool:
    raw_args = op.get("args")
    if not isinstance(raw_args, list):
        return False
    for item in raw_args:
        if isinstance(item, dict):
            for key in ("value", "surface", "normalized", "entity", "id"):
                if key in item and _raw_arg_looks_like_variable(item.get(key)):
                    return True
            continue
        if _raw_arg_looks_like_variable(item):
            return True
    return False


def _raw_arg_looks_like_variable(value: Any) -> bool:
    raw = str(value or "").strip()
    if raw.startswith("?"):
        return True
    return bool(re.fullmatch(r"[A-Z][A-Za-z_]*", raw))


def _clause_support_records(diagnosis: dict[str, Any], clauses: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for clause in clauses:
        text = str(clause).strip()
        if not text:
            continue
        records.append(
            {
                "clause": text,
                "effect": str(diagnosis.get("effect", "")).strip(),
                "operation_index": diagnosis.get("index"),
                "operation": str(diagnosis.get("operation", "")).strip(),
                "predicate": str(diagnosis.get("predicate", "")).strip(),
                "args": [str(item) for item in diagnosis.get("args", []) if str(item).strip()],
                "source": str(diagnosis.get("source", "")).strip(),
                "safety": str(diagnosis.get("safety", "")).strip(),
                "polarity": str(diagnosis.get("polarity", "")).strip(),
                "rationale_codes": [
                    str(item).strip()
                    for item in diagnosis.get("rationale_codes", [])
                    if str(item).strip()
                ],
            }
        )
    return records


def _bounded_text(value: Any, *, max_chars: int = 400) -> str:
    text = str(value or "").strip()
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip()


def _operation_index(value: Any) -> int | None:
    try:
        parsed = int(value)
    except Exception:
        return None
    if parsed < 0:
        return None
    return parsed


def _truth_maintenance_summary(ir: dict[str, Any]) -> dict[str, Any]:
    """Surface model-proposed truth-maintenance structure without authority."""
    result: dict[str, Any] = {
        "authority": "proposal_only_candidate_operations_remain_authoritative",
        "support_links": [],
        "conflicts": [],
        "retraction_plan": [],
        "derived_consequences": [],
    }
    raw = ir.get("truth_maintenance")
    if not isinstance(raw, dict):
        return result

    for item in raw.get("support_links", []):
        if not isinstance(item, dict):
            continue
        index = _operation_index(item.get("operation_index"))
        if index is None:
            continue
        result["support_links"].append(
            {
                "operation_index": index,
                "support_kind": _bounded_text(item.get("support_kind"), max_chars=80),
                "support_ref": _bounded_text(item.get("support_ref")),
                "role": _bounded_text(item.get("role"), max_chars=80),
                "confidence": item.get("confidence"),
            }
        )

    for item in raw.get("conflicts", []):
        if not isinstance(item, dict):
            continue
        index = _operation_index(item.get("new_operation_index"))
        if index is None:
            continue
        result["conflicts"].append(
            {
                "new_operation_index": index,
                "existing_ref": _bounded_text(item.get("existing_ref")),
                "conflict_kind": _bounded_text(item.get("conflict_kind"), max_chars=80),
                "recommended_policy": _bounded_text(item.get("recommended_policy"), max_chars=80),
                "why": _bounded_text(item.get("why"), max_chars=800),
            }
        )

    for item in raw.get("retraction_plan", []):
        if not isinstance(item, dict):
            continue
        index = _operation_index(item.get("operation_index"))
        if index is None:
            continue
        result["retraction_plan"].append(
            {
                "operation_index": index,
                "target_ref": _bounded_text(item.get("target_ref")),
                "reason": _bounded_text(item.get("reason"), max_chars=80),
            }
        )

    for item in raw.get("derived_consequences", []):
        if not isinstance(item, dict):
            continue
        raw_basis = item.get("basis", [])
        basis = [
            _bounded_text(entry, max_chars=120)
            for entry in (raw_basis if isinstance(raw_basis, list) else [])
            if _bounded_text(entry, max_chars=120)
        ]
        result["derived_consequences"].append(
            {
                "statement": _bounded_text(item.get("statement"), max_chars=800),
                "basis": basis,
                "commit_policy": _bounded_text(item.get("commit_policy"), max_chars=80),
            }
        )

    return result


def _identity_ambiguity_allows_source_record_admission(conflict: dict[str, Any], op: dict[str, Any]) -> bool:
    """Identity ambiguity can quarantine a linking inference without blocking a source record."""
    conflict_kind = str(conflict.get("conflict_kind") or "").strip().lower()
    if conflict_kind != "identity_ambiguity":
        return False
    predicate = str(op.get("predicate") or "").strip()
    if not predicate or predicate in IDENTITY_PREDICATES:
        return False
    operation = str(op.get("operation") or "").strip().lower()
    effect = str(op.get("effect") or "").strip().lower()
    source = str(op.get("source") or "").strip().lower()
    if operation != "assert" or effect != "fact":
        return False
    if source not in {"direct", "observed", "source", "document"}:
        return False
    return True


def _truth_maintenance_alignment(
    truth_maintenance: dict[str, Any],
    operations: list[dict[str, Any]],
    *,
    projected_decision: str = "",
    epistemic_worlds: dict[str, Any] | None = None,
) -> dict[str, Any]:
    operation_count = len(operations)
    operation_by_index = {
        int(op.get("index")): op
        for op in operations
        if isinstance(op, dict) and _operation_index(op.get("index")) is not None
    }
    support_indexes = {
        int(item.get("operation_index"))
        for item in truth_maintenance.get("support_links", [])
        if isinstance(item, dict) and _operation_index(item.get("operation_index")) is not None
    }
    soft_out_of_range_question_support_indexes = {
        int(item.get("operation_index"))
        for item in truth_maintenance.get("support_links", [])
        if (
            isinstance(item, dict)
            and _operation_index(item.get("operation_index")) is not None
            and int(item.get("operation_index")) == operation_count
            and str(item.get("role") or "").strip().lower() in {"question", "questions", "query"}
        )
    }
    conflict_indexes = {
        int(item.get("new_operation_index"))
        for item in truth_maintenance.get("conflicts", [])
        if isinstance(item, dict) and _operation_index(item.get("new_operation_index")) is not None
    }
    conflict_policy_by_index: dict[int, set[str]] = {}
    for item in truth_maintenance.get("conflicts", []):
        if not isinstance(item, dict):
            continue
        index = _operation_index(item.get("new_operation_index"))
        if index is None:
            continue
        policy = str(item.get("recommended_policy") or "").strip().lower()
        if policy:
            conflict_policy_by_index.setdefault(index, set()).add(policy)
    retraction_indexes = {
        int(item.get("operation_index"))
        for item in truth_maintenance.get("retraction_plan", [])
        if isinstance(item, dict) and _operation_index(item.get("operation_index")) is not None
    }
    scoped_indexes = _epistemic_world_operation_indexes(epistemic_worlds or {})
    scoped_retraction_indexes = _epistemic_world_retraction_plan_indexes(epistemic_worlds or {})
    fuzzy_edges: list[dict[str, Any]] = []

    def add_edge(kind: str, *, operation_index: int | None = None, detail: str = "", severity: str = "note") -> None:
        fuzzy_edges.append(
            {
                "kind": kind,
                "operation_index": operation_index,
                "severity": severity,
                "detail": _bounded_text(detail, max_chars=800),
            }
        )

    def check_ref(index: int, kind: str) -> None:
        if index not in operation_by_index:
            if kind == "support link" and index in soft_out_of_range_question_support_indexes:
                return
            add_edge(
                "truth_maintenance_invalid_operation_ref",
                operation_index=index,
                detail=f"{kind} references operation {index}, but only {operation_count} candidate operation(s) exist.",
                severity="warning",
            )

    for index in support_indexes:
        check_ref(index, "support link")
    for index in conflict_indexes:
        check_ref(index, "conflict")
    for index in retraction_indexes:
        check_ref(index, "retraction plan")

    for op in operations:
        if not isinstance(op, dict):
            continue
        index = _operation_index(op.get("index"))
        if index is None:
            continue
        admitted = bool(op.get("admitted"))
        effect = str(op.get("effect", "")).strip()
        operation = str(op.get("operation", "")).strip()
        if admitted and effect in {"fact", "rule", "query", "retract"} and index not in support_indexes:
            add_edge(
                "admitted_operation_without_model_support_link",
                operation_index=index,
                detail=f"Admitted {effect} operation has no truth_maintenance.support_links entry.",
            )
        if (
            not admitted
            and index in support_indexes
            and str(op.get("safety", "")).strip().lower() != "needs_clarification"
            and index not in scoped_indexes
            and not (conflict_policy_by_index.get(index, set()) & {"clarify", "quarantine", "reject"})
            and str(projected_decision or "").strip().lower() not in {"clarify", "quarantine", "reject"}
        ):
            add_edge(
                "supported_operation_skipped_by_mapper",
                operation_index=index,
                detail=str(op.get("skip_reason") or "mapper skipped operation despite model support link"),
                severity="warning",
            )
        if admitted and effect == "retract" and index not in retraction_indexes:
            add_edge(
                "admitted_retract_without_retraction_plan",
                operation_index=index,
                detail="Mapper admitted a retract operation, but the model did not include it in truth_maintenance.retraction_plan.",
                severity="warning",
            )
        if (
            index in retraction_indexes
            and not (admitted and effect == "retract")
            and index not in scoped_retraction_indexes
        ):
            add_edge(
                "retraction_plan_not_admitted_as_retract",
                operation_index=index,
                detail=f"Model proposed a retraction plan for operation='{operation}' effect='{effect}', admitted={admitted}.",
                severity="warning",
            )

    for conflict in truth_maintenance.get("conflicts", []):
        if not isinstance(conflict, dict):
            continue
        index = _operation_index(conflict.get("new_operation_index"))
        if index is None or index not in operation_by_index:
            continue
        op = operation_by_index[index]
        policy = str(conflict.get("recommended_policy") or "").strip().lower()
        if (
            bool(op.get("admitted"))
            and policy in {"clarify", "quarantine", "reject"}
            and str(projected_decision or "").strip().lower() not in {"clarify", "quarantine", "reject"}
            and not _identity_ambiguity_allows_source_record_admission(conflict, op)
        ):
            add_edge(
                "conflict_policy_mismatch_admitted_operation",
                operation_index=index,
                detail=f"Model conflict recommends {policy}, but mapper admitted the operation. Existing ref: {conflict.get('existing_ref', '')}",
                severity="warning",
            )

    for consequence in truth_maintenance.get("derived_consequences", []):
        if not isinstance(consequence, dict):
            continue
        policy = str(consequence.get("commit_policy") or "").strip().lower()
        if policy not in {"query_only", "quarantine", "future_rule_support", "do_not_commit"}:
            add_edge(
                "derived_consequence_unknown_policy",
                detail=f"Derived consequence has unknown commit policy: {policy}",
                severity="warning",
            )

    missing_support_ref_count = sum(
        1
        for item in truth_maintenance.get("support_links", [])
        if isinstance(item, dict) and not str(item.get("support_ref") or "").strip()
    )
    if missing_support_ref_count:
        add_edge(
            "support_link_missing_reference",
            detail=f"{missing_support_ref_count} support link(s) omit support_ref.",
        )

    admitted_with_support = sum(
        1
        for op in operations
        if bool(op.get("admitted")) and _operation_index(op.get("index")) in support_indexes
    )
    admitted_without_support = sum(
        1
        for op in operations
        if bool(op.get("admitted")) and _operation_index(op.get("index")) not in support_indexes
    )
    skipped_with_support = sum(
        1
        for op in operations
        if not bool(op.get("admitted")) and _operation_index(op.get("index")) in support_indexes
    )
    skipped_with_scoped_memory = sum(
        1
        for op in operations
        if not bool(op.get("admitted")) and _operation_index(op.get("index")) in scoped_indexes
    )
    retraction_plans_with_scoped_memory = sum(
        1
        for index in retraction_indexes
        if index in scoped_retraction_indexes
    )
    needs_clarification_with_support = sum(
        1
        for op in operations
        if (
            not bool(op.get("admitted"))
            and _operation_index(op.get("index")) in support_indexes
            and str(op.get("safety", "")).strip().lower() == "needs_clarification"
        )
    )
    return {
        "authority": "diagnostic_only_no_admission_effect",
        "operation_count": operation_count,
        "support_link_count": len(truth_maintenance.get("support_links", [])),
        "conflict_count": len(truth_maintenance.get("conflicts", [])),
        "retraction_plan_count": len(truth_maintenance.get("retraction_plan", [])),
        "derived_consequence_count": len(truth_maintenance.get("derived_consequences", [])),
        "admitted_with_support_count": admitted_with_support,
        "admitted_without_support_count": admitted_without_support,
        "skipped_with_support_count": skipped_with_support,
        "skipped_with_scoped_memory_count": skipped_with_scoped_memory,
        "retraction_plan_scoped_count": retraction_plans_with_scoped_memory,
        "soft_out_of_range_question_support_count": len(soft_out_of_range_question_support_indexes),
        "needs_clarification_with_support_count": needs_clarification_with_support,
        "conflict_on_admitted_count": sum(
            1
            for index in conflict_indexes
            if index in operation_by_index and bool(operation_by_index[index].get("admitted"))
        ),
        "fuzzy_edge_count": len(fuzzy_edges),
        "fuzzy_edges": fuzzy_edges,
    }


def _epistemic_world_operation_indexes(epistemic_worlds: dict[str, Any]) -> set[int]:
    indexes: set[int] = set()
    raw_worlds = epistemic_worlds.get("worlds", [])
    if not isinstance(raw_worlds, list):
        return indexes
    for world in raw_worlds:
        if not isinstance(world, dict):
            continue
        operations = world.get("operations", [])
        if not isinstance(operations, list):
            continue
        for op in operations:
            if not isinstance(op, dict):
                continue
            index = _operation_index(op.get("operation_index"))
            if index is not None:
                indexes.add(index)
    return indexes


def _epistemic_world_retraction_plan_indexes(epistemic_worlds: dict[str, Any]) -> set[int]:
    indexes: set[int] = set()
    raw_worlds = epistemic_worlds.get("worlds", [])
    if not isinstance(raw_worlds, list):
        return indexes
    for world in raw_worlds:
        if not isinstance(world, dict):
            continue
        operations = world.get("operations", [])
        if not isinstance(operations, list):
            continue
        for op in operations:
            if not isinstance(op, dict):
                continue
            plans = op.get("retraction_plans", [])
            if not isinstance(plans, list) or not plans:
                continue
            index = _operation_index(op.get("operation_index"))
            if index is not None:
                indexes.add(index)
    return indexes


def _admission_feature_summary(
    ir: dict[str, Any],
    *,
    allowed_signatures: set[tuple[str, int]],
    contract_map: dict[tuple[str, int], list[str]] | None = None,
    contract_details: dict[tuple[str, int], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    contract_map = contract_map or {}
    contract_details = contract_details or {}
    safe_ops = [
        op
        for op in _candidate_operations(ir)
        if str(op.get("safety", "")).strip().lower() == "safe"
    ]
    sources = sorted(
        {
            str(op.get("source", "")).strip().lower()
            for op in _candidate_operations(ir)
            if str(op.get("source", "")).strip()
        }
    )
    risk = _bad_commit_risk(ir)
    risk_score = {"low": 0.15, "medium": 0.55, "high": 0.9}.get(risk, 0.55)
    return {
        "direct_operation_count": sum(
            1 for op in safe_ops if str(op.get("source", "")).strip().lower() == "direct"
        ),
        "context_operation_count": sum(
            1 for op in safe_ops if str(op.get("source", "")).strip().lower() == "context"
        ),
        "inferred_operation_count": sum(
            1 for op in safe_ops if str(op.get("source", "")).strip().lower() == "inferred"
        ),
        "sources_present": sources,
        "has_missing_required_slots": bool(_missing_slots(ir)),
        "has_raw_missing_slots": bool(_raw_missing_slots(ir)),
        "has_unresolved_referents": bool(_semantic_ir_ambiguities(ir)),
        "has_unsafe_implications": _has_unsafe_implications(ir),
        "has_claim_and_direct_assertions": _has_claim_and_direct_assertions(ir),
        "has_self_check_rule_conflict": _self_check_mentions_unresolved_rule_conflict(ir),
        "predicate_palette_enabled": bool(allowed_signatures),
        "predicate_palette_size": len(allowed_signatures),
        "predicate_contract_enabled": bool(contract_map),
        "predicate_contract_size": len(contract_map),
        "has_out_of_palette_safe_write": _has_out_of_palette_safe_write(
            ir,
            allowed_signatures=allowed_signatures,
        ),
        "has_contract_invalid_safe_write": _has_contract_invalid_safe_write(
            ir,
            contract_map=contract_map,
        ),
        "has_contract_policy_invalid_safe_write": _has_contract_policy_invalid_safe_write(
            ir,
            contract_map=contract_map,
            contract_details=contract_details,
        ),
        "has_temporal_interval_order_mismatch": _has_temporal_interval_order_mismatch(ir),
        "bad_commit_risk": risk,
        "bad_commit_risk_score": risk_score,
        "diagnostic_note": "These values explain mapper pressure; they do not authorize writes.",
    }


def _operation_feature_summary(
    ir: dict[str, Any],
    *,
    predicate: str,
    args: list[str],
    operation: str,
    source: str,
    safety: str,
    polarity: str,
    allowed_signatures: set[tuple[str, int]],
    contract_map: dict[tuple[str, int], list[str]] | None = None,
) -> dict[str, Any]:
    source_support = {
        "direct": 1.0,
        "context": 0.75,
        "inferred": 0.25,
    }.get(source, 0.0)
    return {
        "directness": 1.0 if source == "direct" else 0.0,
        "evidence_support": source_support,
        "predicate_shape_valid": bool(predicate),
        "predicate_palette_allowed": _operation_signature_allowed(
            predicate=predicate,
            args=args,
            operation=operation,
            allowed_signatures=allowed_signatures,
        ),
        "predicate_contract_present": (predicate, len(args)) in (contract_map or {}),
        "predicate_contract_roles": list((contract_map or {}).get((predicate, len(args)), [])),
        "arg_count": len(args),
        "model_marked_safe": safety == "safe",
        "write_operation": operation in {"assert", "retract", "rule"},
        "query_operation": operation == "query",
        "negative_polarity": polarity == "negative",
        "bad_commit_risk": _bad_commit_risk(ir),
        "has_ungrounded_argument_atom": any(arg in UNGROUNDED_ARGUMENT_ATOMS for arg in args),
    }


def _allowed_predicate_signature_set(raw: Any) -> set[tuple[str, int]]:
    if raw is None:
        return set()
    values = raw
    if isinstance(raw, set):
        values = list(raw)
    elif isinstance(raw, tuple):
        values = list(raw)
    elif not isinstance(raw, list):
        values = [raw]
    signatures: set[tuple[str, int]] = set()
    for item in values:
        if isinstance(item, dict):
            text = str(item.get("signature") or "").strip()
            if not text:
                predicate = str(item.get("predicate") or item.get("name") or "").strip()
                args = item.get("arguments", item.get("args", []))
                if predicate and isinstance(args, list):
                    name = _predicate_name(predicate)
                    if name:
                        signatures.add((name, len(args)))
                continue
            match = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*/\s*(\d+)\s*", text)
            if match:
                name = _predicate_name(match.group(1))
                if name:
                    signatures.add((name, int(match.group(2))))
            continue
        if isinstance(item, tuple) and len(item) == 2:
            name = _predicate_name(item[0])
            try:
                arity = int(item[1])
            except Exception:
                continue
            if name and arity >= 0:
                signatures.add((name, arity))
            continue
        text = str(item or "").strip()
        match = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*/\s*(\d+)\s*", text)
        if not match:
            continue
        name = _predicate_name(match.group(1))
        arity = int(match.group(2))
        if name:
            signatures.add((name, arity))
    return signatures


def _predicate_contract_map(raw: Any) -> dict[tuple[str, int], list[str]]:
    if raw is None:
        return {}
    if isinstance(raw, dict) and all(isinstance(key, tuple) and len(key) == 2 for key in raw):
        out: dict[tuple[str, int], list[str]] = {}
        for key, value in raw.items():
            name = _predicate_name(key[0])
            try:
                arity = int(key[1])
            except Exception:
                continue
            roles = value if isinstance(value, list) else []
            if name and arity >= 0:
                out[(name, arity)] = [str(role).strip() for role in roles if str(role).strip()]
        return out
    values = raw
    if isinstance(raw, dict):
        values = [raw]
    elif isinstance(raw, set):
        values = list(raw)
    elif isinstance(raw, tuple):
        values = list(raw)
    elif not isinstance(raw, list):
        values = [raw]
    out: dict[tuple[str, int], list[str]] = {}
    for item in values:
        if not isinstance(item, dict):
            continue
        signature = str(item.get("signature") or "").strip()
        name = ""
        arity: int | None = None
        if signature:
            match = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*/\s*(\d+)\s*", signature)
            if match:
                name = _predicate_name(match.group(1))
                arity = int(match.group(2))
        if not name:
            predicate_text = str(item.get("predicate") or item.get("name") or "").strip()
            name = _predicate_name(predicate_text) if predicate_text else ""
        roles = item.get("arguments", item.get("args", []))
        if not isinstance(roles, list):
            roles = []
        role_names = [str(role).strip() for role in roles if str(role).strip()]
        if arity is None:
            arity = len(role_names)
        if name and arity >= 0:
            out[(name, arity)] = role_names
    return out


def _predicate_contract_detail_map(raw: Any) -> dict[tuple[str, int], dict[str, Any]]:
    if raw is None:
        return {}
    if isinstance(raw, dict) and all(isinstance(key, tuple) and len(key) == 2 for key in raw):
        return {}
    values = raw
    if isinstance(raw, dict):
        values = [raw]
    elif isinstance(raw, set):
        values = list(raw)
    elif isinstance(raw, tuple):
        values = list(raw)
    elif not isinstance(raw, list):
        values = [raw]
    out: dict[tuple[str, int], dict[str, Any]] = {}
    for item in values:
        if not isinstance(item, dict):
            continue
        signature = str(item.get("signature") or "").strip()
        name = ""
        arity: int | None = None
        if signature:
            match = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*/\s*(\d+)\s*", signature)
            if match:
                name = _predicate_name(match.group(1))
                arity = int(match.group(2))
        if not name:
            predicate_text = str(item.get("predicate") or item.get("name") or "").strip()
            name = _predicate_name(predicate_text) if predicate_text else ""
        roles = item.get("arguments", item.get("args", []))
        if not isinstance(roles, list):
            roles = []
        if arity is None:
            arity = len([role for role in roles if str(role).strip()])
        if name and arity >= 0:
            out[(name, arity)] = dict(item)
    return out


def _predicate_alias_map(raw: Any) -> dict[tuple[str, int], tuple[str, int]]:
    if raw is None:
        return {}
    values = raw
    if isinstance(raw, dict):
        values = [raw]
    elif isinstance(raw, set):
        values = list(raw)
    elif isinstance(raw, tuple):
        values = list(raw)
    elif not isinstance(raw, list):
        values = [raw]
    aliases: dict[tuple[str, int], tuple[str, int]] = {}
    for item in values:
        if not isinstance(item, dict):
            continue
        canonical = _signature_tuple_from_contract(item)
        if canonical is None:
            continue
        raw_aliases = item.get("aliases", item.get("predicate_aliases", []))
        if not isinstance(raw_aliases, list):
            continue
        for alias in raw_aliases:
            alias_signature = _signature_tuple(str(alias or ""), default_arity=canonical[1])
            if alias_signature is None:
                continue
            if alias_signature[1] != canonical[1]:
                continue
            if alias_signature != canonical:
                aliases[alias_signature] = canonical
    return aliases


def _signature_tuple_from_contract(item: dict[str, Any]) -> tuple[str, int] | None:
    signature = str(item.get("signature") or "").strip()
    parsed = _signature_tuple(signature)
    if parsed is not None:
        return parsed
    predicate_text = str(item.get("predicate") or item.get("name") or "").strip()
    name = _predicate_name(predicate_text) if predicate_text else ""
    roles = item.get("arguments", item.get("args", []))
    if not name or not isinstance(roles, list):
        return None
    return (name, len([role for role in roles if str(role).strip()]))


def _signature_tuple(text: str, *, default_arity: int | None = None) -> tuple[str, int] | None:
    raw = str(text or "").strip()
    if not raw:
        return None
    match = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*/\s*(\d+)\s*", raw)
    if match:
        name = _predicate_name(match.group(1))
        arity = int(match.group(2))
        return (name, arity) if name and arity >= 0 else None
    if default_arity is None:
        return None
    name = _predicate_name(raw)
    return (name, int(default_arity)) if name and int(default_arity) >= 0 else None


def _ir_with_predicate_aliases(
    ir: dict[str, Any],
    predicate_aliases: dict[tuple[str, int], tuple[str, int]],
) -> dict[str, Any]:
    if not predicate_aliases or not isinstance(ir, dict):
        return ir
    try:
        clone = json.loads(json.dumps(ir))
    except Exception:
        clone = dict(ir)
    ops = clone.get("candidate_operations", [])
    if not isinstance(ops, list):
        return clone
    for op in ops:
        if not isinstance(op, dict):
            continue
        predicate = _predicate_name(op.get("predicate"))
        args = op.get("args", [])
        arity = len(args) if isinstance(args, list) else 0
        canonical = predicate_aliases.get((predicate, arity))
        if canonical is None:
            continue
        op.setdefault("original_predicate", predicate)
        op["predicate"] = canonical[0]
    return clone


def _predicate_alias_applications(
    ir: dict[str, Any],
    predicate_aliases: dict[tuple[str, int], tuple[str, int]],
) -> list[dict[str, Any]]:
    if not predicate_aliases:
        return []
    applications: list[dict[str, Any]] = []
    for index, op in enumerate(_candidate_operations(ir)):
        predicate = _predicate_name(op.get("predicate"))
        args = op.get("args", [])
        arity = len(args) if isinstance(args, list) else 0
        canonical = predicate_aliases.get((predicate, arity))
        if canonical is None:
            continue
        applications.append(
            {
                "operation_index": index,
                "from": f"{predicate}/{arity}",
                "to": f"{canonical[0]}/{canonical[1]}",
                "authority": "profile_predicate_alias",
            }
        )
    return applications


def _operation_signature_allowed(
    *,
    predicate: str,
    args: list[str],
    operation: str,
    allowed_signatures: set[tuple[str, int]],
) -> bool:
    if not allowed_signatures or not predicate:
        return True
    if operation == "rule" and not args:
        return True
    return (predicate, len(args)) in allowed_signatures


def _operation_palette_problem(
    op: dict[str, Any],
    *,
    predicate: str,
    args: list[str],
    operation: str,
    allowed_signatures: set[tuple[str, int]],
) -> dict[str, Any] | None:
    if not allowed_signatures or operation not in {"assert", "query", "retract", "rule"}:
        return None
    if operation == "rule":
        clause = str(op.get("clause") or op.get("logic") or "").strip()
        signatures = _predicate_signatures_from_clause(clause)
        if signatures:
            unknown = sorted(signature for signature in signatures if signature not in allowed_signatures)
            if unknown:
                return {
                    "reason": "predicate_not_in_allowed_palette",
                    "warning": "skipped rule operation outside allowed predicate palette: "
                    + ", ".join(f"{name}/{arity}" for name, arity in unknown),
                    "codes": ["predicate_palette_gate", "allowed_predicate_contract"],
                }
            return None
    if (predicate, len(args)) not in allowed_signatures:
        return {
            "reason": "predicate_not_in_allowed_palette",
            "warning": f"skipped {predicate}/{len(args)} outside allowed predicate palette",
            "codes": ["predicate_palette_gate", "allowed_predicate_contract"],
        }
    return None


def _operation_contract_role_problem(
    op: dict[str, Any],
    *,
    predicate: str,
    args: list[str],
    operation: str,
    entity_meta: dict[str, dict[str, Any]],
    contract_map: dict[tuple[str, int], list[str]],
) -> dict[str, Any] | None:
    if not contract_map or operation not in {"assert", "query", "retract"}:
        return None
    roles = contract_map.get((predicate, len(args)))
    if not roles:
        return None
    raw_args = op.get("args", [])
    if not isinstance(raw_args, list):
        raw_args = []
    for index, (arg, role) in enumerate(zip(args, roles), start=1):
        if _is_variable_term(arg):
            continue
        meta = _metadata_for_operation_arg(raw_args[index - 1] if index - 1 < len(raw_args) else "", arg, entity_meta)
        problem = _role_argument_problem(str(role), arg, meta)
        if problem:
            return {
                "reason": "predicate_contract_role_mismatch",
                "warning": (
                    f"skipped {predicate}/{len(args)} because argument {index} "
                    f"for role {role} looks like {problem}"
                ),
                "codes": ["predicate_contract_gate", "argument_role_mismatch"],
            }
    return None


def _operation_contract_policy_problem(
    *,
    predicate: str,
    args: list[str],
    operation: str,
    contract_map: dict[tuple[str, int], list[str]],
    contract_details: dict[tuple[str, int], dict[str, Any]],
) -> dict[str, Any] | None:
    if operation not in {"assert", "query", "retract"}:
        return None
    signature = (predicate, len(args))
    detail = contract_details.get(signature, {})
    if not isinstance(detail, dict):
        return None
    validators = detail.get("validators", detail.get("admission_validators", []))
    if not isinstance(validators, list):
        return None
    roles = contract_map.get(signature, [])
    for validator in validators:
        if not isinstance(validator, dict):
            continue
        kind = str(validator.get("kind", "")).strip()
        if kind != "argument_must_not_contain_terms":
            continue
        index = _validator_argument_index(validator.get("argument"), roles)
        if index is None or index < 0 or index >= len(args):
            continue
        arg_atom = _atomize(args[index])
        terms = [_atomize(str(item)) for item in validator.get("terms", []) if str(item).strip()]
        if not terms:
            continue
        if any(term and term in arg_atom for term in terms):
            reason = str(validator.get("reason") or "profile_contract_validator_failed").strip()
            warning = str(validator.get("warning") or "").strip()
            if not warning:
                warning = f"skipped {predicate}/{len(args)} because profile validator {reason} matched argument {index + 1}"
            return {
                "reason": reason,
                "warning": warning,
                "codes": ["profile_contract_validator", "argument_content_policy"],
            }
    return None


def _validator_argument_index(raw: Any, roles: list[str]) -> int | None:
    if isinstance(raw, int):
        return raw if raw < 0 else raw - 1
    text = str(raw or "").strip()
    if not text:
        return None
    if re.fullmatch(r"\d+", text):
        return int(text) - 1
    wanted = _atomize(text)
    for index, role in enumerate(roles):
        if _atomize(role) == wanted:
            return index
    return None


def _metadata_for_operation_arg(
    raw_arg: Any,
    atom: str,
    entity_meta: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    candidates: list[str] = []
    if isinstance(raw_arg, dict):
        for key in ("id", "entity", "value", "normalized", "surface"):
            if key in raw_arg:
                candidates.append(str(raw_arg.get(key) or "").strip())
    else:
        candidates.append(str(raw_arg or "").strip())
    candidates.append(str(atom or "").strip())
    for candidate in candidates:
        if candidate in entity_meta:
            return entity_meta[candidate]
    atomized = _atomize(atom)
    for meta in entity_meta.values():
        normalized = _atomize(str(meta.get("normalized") or meta.get("surface") or ""))
        surface = _atomize(str(meta.get("surface") or ""))
        if atomized and atomized in {normalized, surface}:
            return meta
    return {}


def _role_argument_problem(role: str, arg: str, meta: dict[str, Any]) -> str:
    role_kind = _contract_role_kind(role)
    if not role_kind:
        return ""
    entity_type = str(meta.get("type") or "").strip().lower() if isinstance(meta, dict) else ""
    value = _atomize(str(meta.get("normalized") or meta.get("surface") or arg)) if isinstance(meta, dict) else _atomize(arg)
    if role_kind == "interval":
        if entity_type == "person":
            return "a person, not an interval"
        if _looks_like_date_atom(value):
            return "a date, not an interval"
        if "interval" not in value and not value.endswith("_period") and not value.endswith("_span"):
            return "a non-interval atom"
    elif role_kind == "date":
        if entity_type == "person":
            return "a person, not a date/time"
        if entity_type == "place":
            return "a place, not a date/time"
        if not _looks_like_temporal_atom(value):
            return "a non-temporal atom"
        if entity_type and entity_type not in {"time", "unknown"} and not _looks_like_temporal_atom(value):
            return f"{entity_type}, not a date/time"
    elif role_kind == "document":
        if entity_type == "person":
            return "a person, not a source document"
        if entity_type == "time":
            return "a time, not a source document"
    elif role_kind == "person_or_document":
        if entity_type == "time":
            return "a time, not a person/source document"
    elif role_kind == "court_or_judge":
        if entity_type in {"time", "medication", "lab_test", "condition", "symptom"}:
            return f"{entity_type}, not a court/judge"
    elif role_kind == "person":
        if entity_type in {"time", "place", "medication", "lab_test", "condition", "symptom"}:
            return f"{entity_type}, not a person/party"
    return ""


def _contract_role_kind(role: str) -> str:
    value = _atomize(role)
    if not value:
        return ""
    if "speaker" in value and "document" in value:
        return "person_or_document"
    if "interval" in value:
        return "interval"
    if value in {"date", "time", "date_filed", "decision_date", "filing_date"}:
        return "date"
    if value in {"timestamp", "datetime"}:
        return "date"
    if (
        value.endswith("_date")
        or value.startswith("date_")
        or value.endswith("_time")
        or value.endswith("_at")
        or value.endswith("_on")
        or "date_or" in value
    ):
        return "date"
    if "authority" in value:
        return ""
    if any(marker in value for marker in ("document", "filing", "exhibit", "docket", "source")):
        return "document"
    if value in {"case", "contract", "clause", "obligation"} or value.endswith("_case"):
        return "document"
    if any(
        marker in value
        for marker in (
            "court_or_judge",
            "court",
            "tribunal",
            "panel",
            "person",
            "patient",
            "judge",
            "attorney",
            "beneficiary",
            "guardian",
            "ward",
            "witness",
            "speaker",
            "actor",
        )
    ):
        if "court" in value or "tribunal" in value or "panel" in value:
            return "court_or_judge"
        return "person"
    return ""


def _looks_like_date_atom(value: str) -> bool:
    atom = str(value or "").strip().lower()
    if re.fullmatch(r"\d{4}(_\d{1,2}){0,2}", atom):
        return True
    if re.fullmatch(r"\d{4}_\d{1,2}_\d{1,2}t\d{1,2}_\d{2}", atom):
        return True
    if re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)_", atom):
        return True
    return bool(re.search(r"\b\d{1,2}_\d{1,2}_\d{2,4}\b", atom))


def _looks_like_temporal_atom(value: str) -> bool:
    atom = str(value or "").strip().lower()
    if _looks_like_date_atom(atom):
        return True
    if re.fullmatch(r"\d{1,2}_\d{2}", atom):
        return True
    if any(marker in atom for marker in ("today", "tomorrow", "yesterday", "morning", "afternoon", "evening")):
        return True
    return False


def _date_sort_key(value: str) -> tuple[int, int, int] | None:
    atom = _atomize(str(value or ""))
    match = re.fullmatch(r"(\d{4})(?:_(\d{1,2}))?(?:_(\d{1,2}))?", atom)
    if not match:
        return None
    year = int(match.group(1))
    month = int(match.group(2) or 1)
    day = int(match.group(3) or 1)
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None
    return (year, month, day)


def _temporal_invalid_operation_indexes(ir: dict[str, Any], *, entity_names: dict[str, str]) -> set[int]:
    intervals: dict[str, dict[str, tuple[int, tuple[int, int, int]]]] = {}
    for index, op in enumerate(_candidate_operations(ir)):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        if str(op.get("operation", "")).strip().lower() != "assert":
            continue
        predicate = _predicate_name(op.get("predicate"))
        if predicate not in {"interval_start", "interval_end"}:
            continue
        args = _operation_args(op.get("args"), entity_names=entity_names, for_query=False)
        if len(args) != 2:
            continue
        date_key = _date_sort_key(args[1])
        if date_key is None:
            continue
        row = intervals.setdefault(args[0], {})
        row[predicate] = (index, date_key)
    invalid: set[int] = set()
    for row in intervals.values():
        start = row.get("interval_start")
        end = row.get("interval_end")
        if start and end and start[1] > end[1]:
            invalid.add(start[0])
            invalid.add(end[0])
    return invalid


def _is_variable_term(value: str) -> bool:
    text = str(value or "").strip()
    return bool(text) and (text[0].isupper() or text.startswith("_"))


def _predicate_signatures_from_clause(clause: str) -> set[tuple[str, int]]:
    signatures: set[tuple[str, int]] = set()
    text = str(clause or "")
    for match in re.finditer(r"\b([a-z_][a-z0-9_]*)\s*\(([^()]*)\)", text):
        predicate = _predicate_name(match.group(1))
        if not predicate:
            continue
        args_text = match.group(2).strip()
        arity = 0 if not args_text else len([item for item in args_text.split(",")])
        signatures.add((predicate, arity))
    return signatures


def _generic_grounding_problem(
    predicate: str,
    args: list[str],
    *,
    operation: str,
) -> dict[str, Any] | None:
    if not predicate or operation not in {"assert", "rule"}:
        return None
    if any(arg in UNGROUNDED_ARGUMENT_ATOMS for arg in args):
        return {
            "reason": "ungrounded_argument_atom",
            "warning": f"skipped {predicate}/{len(args)} because an argument is an unresolved placeholder",
            "codes": ["grounding_policy", "no_placeholder_commit"],
        }
    if any(_is_placeholder_atom(arg) for arg in args):
        return {
            "reason": "ungrounded_argument_atom",
            "warning": f"skipped {predicate}/{len(args)} because an argument is an unresolved placeholder",
            "codes": ["grounding_policy", "no_placeholder_commit"],
        }
    return None


def _is_placeholder_atom(arg: str) -> bool:
    value = str(arg or "").strip().lower()
    if not value:
        return True
    return (
        value.startswith("unknown_")
        or value in {"null", "none", "n_a", "na", "not_provided", "unspecified"}
        or value.endswith("_null")
        or value.endswith("_not_provided")
        or value.endswith("_unspecified")
        or value.startswith("someone_")
        or value.endswith("_actor")
        or value.endswith("_unknown")
        or value.endswith("_unknown_agent")
    )


def _projection_reason(
    ir: dict[str, Any],
    model_decision: str,
    projected_decision: str,
    *,
    allowed_signatures: set[tuple[str, int]],
    contract_map: dict[tuple[str, int], list[str]] | None = None,
    contract_details: dict[tuple[str, int], dict[str, Any]] | None = None,
) -> str:
    if projected_decision == model_decision:
        return "model_decision_preserved"
    if _has_clinical_advice_query(ir):
        return "clinical_advice_query_projected_to_reject"
    if _truth_maintenance_recommends_hard_reject(ir):
        return "truth_maintenance_hard_reject_conflict_projected_to_reject"
    if _truth_maintenance_recommends_reject(ir):
        if _has_safe_direct_write(ir) and projected_decision == "mixed":
            return "truth_maintenance_reject_conflict_projected_to_mixed"
        return "truth_maintenance_reject_conflict_projected_to_reject"
    if _truth_maintenance_recommends_policy(ir, {"clarify"}) and not _has_safe_direct_write(ir):
        return "truth_maintenance_clarify_conflict_projected_to_clarify"
    if _is_pure_hypothetical_query(ir):
        return "pure_hypothetical_query_projected_to_answer"
    if model_decision == "clarify" and _speculative_ambiguous_observation_should_quarantine(ir):
        return "speculative_ambiguous_observation_projected_to_quarantine"
    if _ambiguous_content_should_clarify(ir):
        return "ambiguous_referents_with_only_speech_wrapper_projected_to_clarify"
    if model_decision == "commit" and _has_initialed_person_state_write(ir):
        return "initialed_person_state_write_projected_to_mixed"
    if model_decision in {"commit", "mixed"} and _has_only_communication_writes_with_unsafe_implications(
        ir,
        allowed_signatures=allowed_signatures,
    ):
        return "only_communication_writes_with_unsafe_implications_projected_to_quarantine"
    if model_decision in {"commit", "mixed"} and _has_out_of_palette_safe_write(
        ir,
        allowed_signatures=allowed_signatures,
    ):
        if _has_palette_allowed_safe_write(ir, allowed_signatures=allowed_signatures):
            return "out_of_palette_write_projected_to_mixed"
        return "out_of_palette_write_projected_to_quarantine"
    if model_decision in {"commit", "mixed"} and _has_contract_invalid_safe_write(
        ir,
        contract_map=contract_map or {},
    ):
        if _has_contract_valid_safe_write(ir, contract_map=contract_map or {}):
            return "contract_role_mismatch_projected_to_mixed"
        return "contract_role_mismatch_projected_to_quarantine"
    if model_decision in {"commit", "mixed"} and _has_contract_policy_invalid_safe_write(
        ir,
        contract_map=contract_map or {},
        contract_details=contract_details or {},
    ):
        if _has_contract_valid_safe_write(ir, contract_map=contract_map or {}):
            return "profile_contract_policy_projected_to_mixed"
        return "profile_contract_policy_projected_to_quarantine"
    if model_decision in {"commit", "mixed"} and _has_temporal_interval_order_mismatch(ir):
        if _has_temporal_valid_safe_write(ir):
            return "temporal_interval_order_projected_to_mixed"
        return "temporal_interval_order_projected_to_quarantine"
    if model_decision == "commit" and _has_only_context_writes_with_unsafe_implications(ir):
        return "context_writes_with_unsafe_implications_projected_to_mixed"
    if model_decision == "commit" and _has_safe_direct_write(ir) and _has_projection_relevant_unsafe_implications(ir):
        return "safe_write_with_unsafe_implications_projected_to_mixed"
    if model_decision == "commit" and _has_safe_direct_write(ir) and _has_claim_and_direct_assertions(ir):
        return "claim_plus_direct_observation_projected_to_mixed"
    if model_decision == "commit" and _has_safe_direct_write(ir) and _has_general_negative_assertion(ir):
        return "positive_write_with_unsupported_negative_assertion_projected_to_mixed"
    if model_decision == "commit" and _has_safe_direct_write(ir) and _has_partial_write_admission_pressure(ir):
        return "partial_write_admission_pressure_projected_to_mixed"
    if model_decision == "commit" and _has_safe_direct_write(ir) and _self_check_mentions_unresolved_rule_conflict(ir):
        return "self_check_rule_conflict_projected_to_mixed"
    if model_decision == "mixed" and _low_risk_correction_with_only_safe_mutations_should_commit(ir):
        return "low_risk_correction_with_only_safe_mutations_projected_to_commit"
    if model_decision == "quarantine" and _raw_missing_slots(ir) and not _missing_slots(ir):
        return "only_optional_metadata_missing_projected_to_mixed"
    if model_decision == "quarantine" and str(ir.get("turn_type", "")).strip().lower() == "correction":
        if _has_safe_direct_retract(ir):
            return "quarantined_correction_with_safe_retract_projected_to_mixed"
    if model_decision == "quarantine" and _quarantine_with_safe_direct_write_should_mixed(ir):
        return "quarantine_with_safe_direct_write_projected_to_mixed"
    return "structural_projection"


def _candidate_operations(ir: dict[str, Any]) -> list[dict[str, Any]]:
    raw = ir.get("candidate_operations", [])
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def _normalize_decision(value: Any) -> str:
    decision = str(value or "").strip().lower()
    if decision not in {"commit", "clarify", "quarantine", "reject", "answer", "mixed"}:
        return "quarantine"
    return decision


def _has_clinical_advice_query(ir: dict[str, Any]) -> bool:
    direct_clinical_query_terms = {
        "dose",
        "dosage",
        "dose_recommendation",
        "medication_change",
    }
    medication_terms = {
        "drug",
        "med",
        "medication",
        "medicine",
        "rx",
        "warfarin",
    }
    action_terms = {"hold", "held", "start", "stop", "dose", "dosage"}
    recommendation_terms = {"advice", "advise", "recommend", "recommendation", "should"}
    for op in _candidate_operations(ir):
        if str(op.get("operation") or "").strip().lower() != "query":
            continue
        text_parts = [
            str(op.get("predicate") or ""),
            " ".join(str(item) for item in op.get("args", []) if str(item).strip())
            if isinstance(op.get("args"), list)
            else "",
            str(op.get("safety") or ""),
        ]
        text = _atomize(" ".join(text_parts))
        tokens = set(part for part in text.split("_") if part)
        if direct_clinical_query_terms & tokens or any(term in text for term in direct_clinical_query_terms):
            return True
        if (action_terms & tokens) and (medication_terms & tokens):
            return True
        if "treatment" in tokens and (recommendation_terms & tokens):
            return True
        if (recommendation_terms & tokens) and (medication_terms & tokens):
            return True
    return False


def _truth_maintenance_recommends_reject(ir: dict[str, Any]) -> bool:
    return _truth_maintenance_recommends_policy(ir, {"reject"})


def _truth_maintenance_recommends_policy(ir: dict[str, Any], policies: set[str]) -> bool:
    raw = ir.get("truth_maintenance")
    if not isinstance(raw, dict):
        return False
    for item in raw.get("conflicts", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("recommended_policy") or "").strip().lower() in policies:
            return True
    return False


def _truth_maintenance_recommends_hard_reject(ir: dict[str, Any]) -> bool:
    raw = ir.get("truth_maintenance")
    if not isinstance(raw, dict):
        return False
    hard_markers = {"avoid_when", "boundary", "safety", "clinical", "medical"}
    for item in raw.get("conflicts", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("recommended_policy") or "").strip().lower() != "reject":
            continue
        text = _atomize(
            " ".join(
                str(item.get(key) or "")
                for key in ("existing_ref", "conflict_kind", "why")
            )
        )
        if any(marker in text for marker in hard_markers):
            return True
    return False


def _projected_decision(
    ir: dict[str, Any],
    *,
    allowed_signatures: set[tuple[str, int]] | None = None,
    contract_map: dict[tuple[str, int], list[str]] | None = None,
    contract_details: dict[tuple[str, int], dict[str, Any]] | None = None,
) -> str:
    allowed_signatures = allowed_signatures or set()
    contract_map = contract_map or {}
    contract_details = contract_details or {}
    decision = _normalize_decision(ir.get("decision"))
    if _has_clinical_advice_query(ir):
        return "reject"
    if _truth_maintenance_recommends_hard_reject(ir):
        return "reject"
    if _truth_maintenance_recommends_reject(ir):
        if _has_safe_direct_write(ir):
            return "mixed"
        return "reject"
    if _ambiguous_content_should_clarify(ir):
        return "clarify"
    if _truth_maintenance_recommends_policy(ir, {"clarify"}) and not _has_safe_direct_write(ir):
        return "clarify"
    if _is_pure_hypothetical_query(ir):
        return "answer"
    if decision == "clarify" and _speculative_ambiguous_observation_should_quarantine(ir):
        return "quarantine"
    if decision == "commit" and _has_initialed_person_state_write(ir):
        return "mixed"
    if decision in {"commit", "mixed"} and _has_only_communication_writes_with_unsafe_implications(
        ir,
        allowed_signatures=allowed_signatures,
    ):
        return "quarantine"
    if decision in {"commit", "mixed"} and _has_out_of_palette_safe_write(
        ir,
        allowed_signatures=allowed_signatures,
    ):
        if _has_palette_allowed_safe_write(ir, allowed_signatures=allowed_signatures):
            return "mixed"
        return "quarantine"
    if decision in {"commit", "mixed"} and _has_contract_invalid_safe_write(
        ir,
        contract_map=contract_map,
    ):
        if _has_contract_valid_safe_write(ir, contract_map=contract_map):
            return "mixed"
        return "quarantine"
    if decision in {"commit", "mixed"} and _has_contract_policy_invalid_safe_write(
        ir,
        contract_map=contract_map,
        contract_details=contract_details,
    ):
        if _has_contract_valid_safe_write(ir, contract_map=contract_map):
            return "mixed"
        return "quarantine"
    if decision in {"commit", "mixed"} and _has_temporal_interval_order_mismatch(ir):
        if _has_temporal_valid_safe_write(ir):
            return "mixed"
        return "quarantine"
    if decision == "commit" and _has_only_context_writes_with_unsafe_implications(ir):
        return "mixed"
    if decision == "commit" and _has_safe_direct_write(ir) and _has_projection_relevant_unsafe_implications(ir):
        return "mixed"
    if decision == "commit" and _has_safe_direct_write(ir) and _has_claim_and_direct_assertions(ir):
        return "mixed"
    if decision == "commit" and _has_safe_direct_write(ir) and _has_general_negative_assertion(ir):
        return "mixed"
    if decision == "commit" and _has_safe_direct_write(ir) and _has_partial_write_admission_pressure(ir):
        return "mixed"
    if decision == "commit" and _has_safe_direct_write(ir) and _self_check_mentions_unresolved_rule_conflict(ir):
        return "mixed"
    if decision == "mixed" and _low_risk_correction_with_only_safe_mutations_should_commit(ir):
        return "commit"
    if (
        decision == "quarantine"
        and _raw_missing_slots(ir)
        and not _missing_slots(ir)
        and _has_safe_direct_write(ir)
    ):
        return "mixed"
    if decision == "quarantine" and str(ir.get("turn_type", "")).strip().lower() == "correction":
        if _has_safe_direct_retract(ir):
            return "mixed"
    if decision == "quarantine" and _quarantine_with_safe_direct_write_should_mixed(ir):
        return "mixed"
    return decision


def projected_semantic_ir_decision(ir: dict[str, Any]) -> str:
    return _projected_decision(ir)


def _intent_from_ir(ir: dict[str, Any]) -> str:
    safe_ops: list[str] = []
    if _is_pure_hypothetical_query(ir):
        return "query"
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        operation = str(op.get("operation", "")).strip().lower()
        source = str(op.get("source", "")).strip().lower()
        polarity = str(op.get("polarity", "positive") or "positive").strip().lower()
        if source == "inferred":
            continue
        if source == "context" and operation in {"assert", "rule"}:
            continue
        predicate = _predicate_name(op.get("predicate"))
        if polarity == "negative" and operation == "assert" and not _is_negative_event_predicate(predicate):
            continue
        safe_ops.append(operation)
    if "assert" in safe_ops:
        return "assert_fact"
    if "rule" in safe_ops:
        return "assert_rule"
    if "retract" in safe_ops:
        return "retract"
    if "query" in safe_ops or _normalize_decision(ir.get("decision")) == "answer":
        return "query"
    return "other"


def _legacy_intent(
    *,
    facts: list[str],
    rules: list[str],
    queries: list[str],
    retracts: list[str],
    decision: str,
) -> str:
    if facts:
        return "assert_fact"
    if rules:
        return "assert_rule"
    if retracts:
        return "retract"
    if queries:
        return "query"
    if decision == "answer":
        return "query"
    return "other"


def _entity_name_map(ir: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    raw = ir.get("entities", [])
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, dict):
            continue
        entity_id = str(item.get("id", "")).strip()
        if not entity_id:
            continue
        name = str(item.get("normalized") or item.get("surface") or "").strip()
        if name:
            out[entity_id] = name
    return out


def _entity_metadata_map(ir: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    raw = ir.get("entities", [])
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, dict):
            continue
        entity_id = str(item.get("id", "")).strip()
        if entity_id:
            out[entity_id] = item
    return out


def _operation_args(raw_args: Any, *, entity_names: dict[str, str], for_query: bool) -> list[str]:
    if not isinstance(raw_args, list):
        return []
    return [_term_from_arg(item, entity_names=entity_names, for_query=for_query) for item in raw_args]


def _term_from_arg(value: Any, *, entity_names: dict[str, str], for_query: bool) -> str:
    if isinstance(value, dict):
        for key in ("id", "entity", "value", "normalized", "surface"):
            if key in value:
                return _term_from_arg(value.get(key), entity_names=entity_names, for_query=for_query)
        return "unknown"
    raw = str(value or "").strip()
    if raw in entity_names:
        raw = entity_names[raw]
    if for_query and raw.startswith("?"):
        return _variable_name(raw[1:] or "X")
    if for_query and re.fullmatch(r"[A-Z][A-Za-z0-9]*(_[A-Z][A-Za-z0-9]*)+", raw):
        return _variable_name(raw)
    if for_query and re.fullmatch(r"[A-Z]", raw):
        return _variable_name(raw)
    if for_query and raw in {"?", "X", "Y", "Z", "Who", "What", "Where", "When"}:
        return raw if raw in {"X", "Y", "Z"} else "X"
    if for_query and _is_query_placeholder_arg(raw):
        return _placeholder_variable_name(raw)
    if re.fullmatch(r"-?\d+(\.\d+)?", raw):
        return raw
    if raw.startswith("'") and raw.endswith("'"):
        raw = raw[1:-1]
    return _atomize(raw)


def _is_query_placeholder_arg(raw: str) -> bool:
    value = _atomize(str(raw or ""))
    if re.fullmatch(
        r"(actor|arg|count|date|interval|ledger|level|person|point|requiredactor|role|rule|source|status|threshold|time|value|var|zone)\d+",
        value,
    ):
        return True
    if value in {
        "answer",
        "arg",
        "actor",
        "action",
        "accused",
        "authorizer",
        "batch",
        "batch_id",
        "batchid",
        "condition",
        "consequence",
        "candidate",
        "character",
        "content",
        "count",
        "declaration",
        "entity",
        "entry",
        "evidence",
        "explanation",
        "explanation_detail",
        "explanationdetail",
        "event",
        "fact",
        "facility",
        "grievance",
        "grievance_id",
        "grievance_label",
        "grievanceid",
        "grievancelabel",
        "grievancetype",
        "institution",
        "inspectiondate",
        "inspector",
        "item",
        "issuer",
        "label",
        "ledger",
        "location",
        "level",
        "method",
        "method_detail",
        "methoddetail",
        "object",
        "observer",
        "owner",
        "person",
        "place",
        "point",
        "reason",
        "reading",
        "reporter",
        "required_actor",
        "requiredactor",
        "record",
        "result",
        "role",
        "rule",
        "ruleid",
        "speaker",
        "source",
        "status",
        "subject",
        "target",
        "tester",
        "thing",
        "threshold",
        "timestamp",
        "time",
        "type",
        "value",
        "violation",
        "zone",
        "what",
        "when",
        "where",
        "who",
    }:
        return True
    if value in {
        "interval",
        "mode",
        "noticeid",
        "noticedzone",
        "notifiedzone",
        "obsid",
        "recallid",
        "recordtype",
        "rulecondition",
        "rulecontent",
        "violationlabel",
        "authtime",
        "endtime",
        "end_time",
        "starttime",
        "start_time",
        "validitydays",
        "validity_days",
    }:
        return True
    if (
        len(value) > 3
        and not any(char.isdigit() for char in value)
        and value.endswith(("id", "label", "content", "condition", "type", "value", "date", "time", "days", "hours"))
    ):
        return True
    return False


def _placeholder_variable_name(raw: str) -> str:
    value = _atomize(str(raw or "X"))
    if not value:
        return "X"
    return "".join(part[:1].upper() + part[1:] for part in value.split("_") if part) or "X"


def _variable_name(raw: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_]+", "_", str(raw or "X")).strip("_") or "X"
    if not name[0].isalpha() or not name[0].isupper():
        name = "X" + name[:1].upper() + name[1:]
    return name


def _predicate_name(value: Any) -> str:
    raw = str(value or "").strip()
    if "/" in raw:
        raw = raw.split("/", 1)[0]
    raw = _atomize(raw)
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", raw):
        return ""
    return raw


def _atomize(raw: str) -> str:
    value = str(raw or "").strip().lower()
    value = value.replace("%", " percent ")
    value = re.sub(r"[^a-z0-9_]+", "_", value).strip("_")
    return value or "unknown"


def _clause(predicate: str, args: list[str]) -> str:
    return _ensure_period(f"{predicate}({', '.join(args)})")


def _retract_command(clause: str) -> str:
    target = str(clause or "").strip()
    target = target[:-1] if target.endswith(".") else target
    return _ensure_period(f"retract({target})")


def _retract_clause_variants(predicate: str, args: list[str]) -> list[str]:
    variants: list[list[str]] = [[]]
    for arg in args:
        choices = _term_aliases_for_retract(arg)
        variants = [prefix + [choice] for prefix in variants for choice in choices]
    clauses: list[str] = []
    seen: set[str] = set()
    for variant_args in variants[:8]:
        clause = _clause(predicate, variant_args)
        if clause not in seen:
            seen.add(clause)
            clauses.append(clause)
    return clauses


def _term_aliases_for_retract(term: str) -> list[str]:
    raw = str(term or "").strip()
    if not raw:
        return ["unknown"]
    aliases = [raw]
    compact = re.sub(r"(?<=[a-zA-Z])_(?=\d)", "", raw)
    compact = re.sub(r"(?<=\d)_(?=[a-zA-Z])", "", compact)
    if compact and compact != raw:
        aliases.append(compact)
    split_number = re.sub(r"(?<=[a-zA-Z])(?=\d)", "_", compact)
    if split_number and split_number not in aliases:
        aliases.append(split_number)
    return aliases


def _is_negative_event_predicate(predicate: str) -> bool:
    return predicate in {
        "denied",
        "denies",
        "denial",
        "refuted",
        "disputed",
        "rejected_claim",
    }


def _has_safe_direct_write(ir: dict[str, Any]) -> bool:
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        if str(op.get("source", "")).strip().lower() != "direct":
            continue
        if str(op.get("operation", "")).strip().lower() in {"assert", "retract", "rule"}:
            return True
    return False


def _quarantine_with_safe_direct_write_should_mixed(ir: dict[str, Any]) -> bool:
    if not _has_safe_direct_write(ir):
        return False
    if _has_ambiguous_or_unresolved_referent(ir):
        return False
    if _has_only_communication_writes_with_unsafe_implications(ir, allowed_signatures=set()):
        return False
    return True


def _has_general_negative_assertion(ir: dict[str, Any]) -> bool:
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        if str(op.get("operation", "")).strip().lower() != "assert":
            continue
        if str(op.get("polarity", "positive") or "positive").strip().lower() != "negative":
            continue
        predicate = _predicate_name(op.get("predicate"))
        if not _is_negative_event_predicate(predicate):
            return True
    return False


def _has_partial_write_admission_pressure(ir: dict[str, Any]) -> bool:
    for op in _candidate_operations(ir):
        operation = str(op.get("operation", "")).strip().lower()
        if operation not in {"assert", "retract", "rule"}:
            continue
        safety = str(op.get("safety", "")).strip().lower()
        source = str(op.get("source", "")).strip().lower()
        if safety != "safe":
            return True
        if source == "inferred":
            return True
    return False


def _self_check_mentions_unresolved_rule_conflict(ir: dict[str, Any]) -> bool:
    if str(ir.get("turn_type", "")).strip().lower() == "correction":
        return False
    self_check = ir.get("self_check", {})
    if not isinstance(self_check, dict):
        return False
    text = " ".join(_string_list(self_check.get("notes"))).lower()
    if not text:
        return False
    rule_scope = any(marker in text for marker in ("context rule", "under the rule", "constraint"))
    unresolved = any(
        marker in text
        for marker in (
            "logical conflict",
            "consistency check",
            "validity check",
            "invalid under the rule",
            "might be invalid",
        )
    )
    return rule_scope and unresolved


def _has_unsafe_implications(ir: dict[str, Any]) -> bool:
    raw = ir.get("unsafe_implications", [])
    if not isinstance(raw, list):
        return False
    return any(
        isinstance(item, dict) and not _unsafe_implication_duplicates_safe_operation(item, ir)
        for item in raw
    )


def _has_projection_relevant_unsafe_implications(ir: dict[str, Any]) -> bool:
    raw = ir.get("unsafe_implications", [])
    if not isinstance(raw, list):
        return False
    relevant = [
        item
        for item in raw
        if isinstance(item, dict) and not _unsafe_implication_duplicates_safe_operation(item, ir)
    ]
    if not relevant:
        return False
    if (
        str(ir.get("turn_type", "")).strip().lower() == "correction"
        and _has_safe_retract(ir)
        and _bad_commit_risk(ir) == "low"
        and not _string_list(ir.get("clarification_questions"))
        and all(str(item.get("commit_policy", "")).strip().lower() == "clarify" for item in relevant)
    ):
        return False
    return True


def _low_risk_correction_with_only_safe_mutations_should_commit(ir: dict[str, Any]) -> bool:
    if str(ir.get("turn_type", "")).strip().lower() != "correction":
        return False
    if _bad_commit_risk(ir) != "low":
        return False
    if _string_list(ir.get("clarification_questions")) or _missing_slots(ir):
        return False
    if _has_projection_relevant_unsafe_implications(ir):
        return False
    ops = _candidate_operations(ir)
    if not ops:
        return False
    has_retract = False
    has_assert = False
    for op in ops:
        operation = str(op.get("operation", "")).strip().lower()
        source = str(op.get("source", "")).strip().lower()
        safety = str(op.get("safety", "")).strip().lower()
        if operation not in {"assert", "retract"}:
            return False
        if safety != "safe":
            return False
        if source not in {"direct", "context"}:
            return False
        has_retract = has_retract or operation == "retract"
        has_assert = has_assert or operation == "assert"
    return has_retract and has_assert


def _has_only_context_writes_with_unsafe_implications(ir: dict[str, Any]) -> bool:
    if not _has_projection_relevant_unsafe_implications(ir):
        return False
    safe_writes = [
        op
        for op in _candidate_operations(ir)
        if str(op.get("safety", "")).strip().lower() == "safe"
        and str(op.get("operation", "")).strip().lower() in {"assert", "rule"}
    ]
    if not safe_writes:
        return False
    return all(str(op.get("source", "")).strip().lower() == "context" for op in safe_writes)


def _unsafe_implication_duplicates_safe_operation(item: dict[str, Any], ir: dict[str, Any]) -> bool:
    candidate = str(item.get("candidate", "")).strip().lower()
    if not candidate:
        return False
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        operation = str(op.get("operation", "")).strip().lower()
        predicate = _predicate_name(op.get("predicate"))
        args = _operation_args(op.get("args"), entity_names=_entity_name_map(ir), for_query=operation == "query")
        if operation and operation != "retract" and operation not in candidate:
            continue
        if predicate and predicate not in candidate:
            continue
        if all(str(arg).strip().lower() in candidate for arg in args):
            return True
    return False


def _has_claim_and_direct_assertions(ir: dict[str, Any]) -> bool:
    raw = ir.get("assertions", [])
    if not isinstance(raw, list):
        return False
    kinds = {
        str(item.get("kind", "")).strip().lower()
        for item in raw
        if isinstance(item, dict)
    }
    return "claim" in kinds and "direct" in kinds


COMMUNICATION_CONTAINER_PREDICATES = {
    "said",
    "says",
    "told",
    "reported",
    "claimed",
    "claim",
    "stated",
    "mentioned",
}


def _ambiguous_content_should_clarify(ir: dict[str, Any]) -> bool:
    if _normalize_decision(ir.get("decision")) not in {"commit", "mixed"}:
        return False
    if not _has_ambiguous_or_unresolved_referent(ir):
        return False
    if not _string_list(ir.get("clarification_questions")):
        return False
    if _bad_commit_risk(ir) != "high":
        return False
    safe_write_predicates: list[str] = []
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        if str(op.get("operation", "")).strip().lower() not in {"assert", "rule"}:
            continue
        if str(op.get("source", "")).strip().lower() != "direct":
            continue
        predicate = _predicate_name(op.get("predicate"))
        if predicate:
            safe_write_predicates.append(predicate)
    if not safe_write_predicates:
        return False
    return all(predicate in COMMUNICATION_CONTAINER_PREDICATES for predicate in safe_write_predicates)


def _has_only_communication_writes_with_unsafe_implications(
    ir: dict[str, Any],
    *,
    allowed_signatures: set[tuple[str, int]] | None = None,
) -> bool:
    allowed_signatures = allowed_signatures or set()
    if not _has_projection_relevant_unsafe_implications(ir):
        return False
    write_predicates: list[str] = []
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        if str(op.get("source", "")).strip().lower() != "direct":
            continue
        operation = str(op.get("operation", "")).strip().lower()
        if operation not in {"assert", "rule"}:
            continue
        predicate = _predicate_name(op.get("predicate"))
        if allowed_signatures and _operation_palette_problem(
            op,
            predicate=predicate,
            args=_operation_args(op.get("args"), entity_names=_entity_name_map(ir), for_query=False),
            operation=operation,
            allowed_signatures=allowed_signatures,
        ):
            continue
        if predicate:
            write_predicates.append(predicate)
    if not write_predicates:
        return False
    return all(predicate in COMMUNICATION_CONTAINER_PREDICATES for predicate in write_predicates)


def _has_out_of_palette_safe_write(
    ir: dict[str, Any],
    *,
    allowed_signatures: set[tuple[str, int]],
) -> bool:
    if not allowed_signatures:
        return False
    entity_names = _entity_name_map(ir)
    for op in _candidate_operations(ir):
        operation = str(op.get("operation", "")).strip().lower()
        if operation not in {"assert", "retract", "rule"}:
            continue
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        if _is_query_scoped_identity_premise(ir, _predicate_name(op.get("predicate"))):
            continue
        predicate = _predicate_name(op.get("predicate"))
        args = _operation_args(op.get("args"), entity_names=entity_names, for_query=False)
        if _operation_palette_problem(
            op,
            predicate=predicate,
            args=args,
            operation=operation,
            allowed_signatures=allowed_signatures,
        ):
            return True
    return False


def _has_contract_invalid_safe_write(
    ir: dict[str, Any],
    *,
    contract_map: dict[tuple[str, int], list[str]],
) -> bool:
    if not contract_map:
        return False
    entity_meta = _entity_metadata_map(ir)
    entity_names = _entity_name_map(ir)
    for op in _candidate_operations(ir):
        operation = str(op.get("operation", "")).strip().lower()
        if operation not in {"assert", "retract", "query"}:
            continue
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        predicate = _predicate_name(op.get("predicate"))
        args = _operation_args(op.get("args"), entity_names=entity_names, for_query=operation == "query")
        if _operation_contract_role_problem(
            op,
            predicate=predicate,
            args=args,
            operation=operation,
            entity_meta=entity_meta,
            contract_map=contract_map,
        ):
            return True
    return False


def _has_contract_policy_invalid_safe_write(
    ir: dict[str, Any],
    *,
    contract_map: dict[tuple[str, int], list[str]],
    contract_details: dict[tuple[str, int], dict[str, Any]],
) -> bool:
    if not contract_details:
        return False
    entity_names = _entity_name_map(ir)
    for op in _candidate_operations(ir):
        operation = str(op.get("operation", "")).strip().lower()
        if operation not in {"assert", "retract", "query"}:
            continue
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        predicate = _predicate_name(op.get("predicate"))
        args = _operation_args(op.get("args"), entity_names=entity_names, for_query=operation == "query")
        if _operation_contract_policy_problem(
            predicate=predicate,
            args=args,
            operation=operation,
            contract_map=contract_map,
            contract_details=contract_details,
        ):
            return True
    return False


def _has_contract_valid_safe_write(
    ir: dict[str, Any],
    *,
    contract_map: dict[tuple[str, int], list[str]],
) -> bool:
    if not contract_map:
        return False
    entity_meta = _entity_metadata_map(ir)
    entity_names = _entity_name_map(ir)
    for op in _candidate_operations(ir):
        operation = str(op.get("operation", "")).strip().lower()
        if operation not in {"assert", "retract", "query"}:
            continue
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        predicate = _predicate_name(op.get("predicate"))
        args = _operation_args(op.get("args"), entity_names=entity_names, for_query=operation == "query")
        if (predicate, len(args)) not in contract_map:
            continue
        if not _operation_contract_role_problem(
            op,
            predicate=predicate,
            args=args,
            operation=operation,
            entity_meta=entity_meta,
            contract_map=contract_map,
        ):
            return True
    return False


def _has_temporal_interval_order_mismatch(ir: dict[str, Any]) -> bool:
    return bool(_temporal_invalid_operation_indexes(ir, entity_names=_entity_name_map(ir)))


def _has_temporal_valid_safe_write(ir: dict[str, Any]) -> bool:
    entity_names = _entity_name_map(ir)
    invalid = _temporal_invalid_operation_indexes(ir, entity_names=entity_names)
    for index, op in enumerate(_candidate_operations(ir)):
        if index in invalid:
            continue
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        if str(op.get("source", "")).strip().lower() != "direct":
            continue
        if str(op.get("operation", "")).strip().lower() in {"assert", "retract", "rule"}:
            return True
    return False


def _has_palette_allowed_safe_write(
    ir: dict[str, Any],
    *,
    allowed_signatures: set[tuple[str, int]],
) -> bool:
    if not allowed_signatures:
        return False
    entity_names = _entity_name_map(ir)
    for op in _candidate_operations(ir):
        operation = str(op.get("operation", "")).strip().lower()
        if operation not in {"assert", "retract", "rule"}:
            continue
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        predicate = _predicate_name(op.get("predicate"))
        args = _operation_args(op.get("args"), entity_names=entity_names, for_query=False)
        if not _operation_palette_problem(
            op,
            predicate=predicate,
            args=args,
            operation=operation,
            allowed_signatures=allowed_signatures,
        ):
            return True
    return False


def _has_safe_direct_retract(ir: dict[str, Any]) -> bool:
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        if str(op.get("source", "")).strip().lower() != "direct":
            continue
        if str(op.get("operation", "")).strip().lower() == "retract":
            return True
    return False


def _has_safe_retract(ir: dict[str, Any]) -> bool:
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        if str(op.get("operation", "")).strip().lower() == "retract":
            return True
    return False


def _operation_targets_quantified_set(op: dict[str, Any], entity_meta: dict[str, dict[str, Any]]) -> bool:
    raw_args = op.get("args", [])
    if not isinstance(raw_args, list):
        return False
    for arg in raw_args:
        entity_id = ""
        if isinstance(arg, dict):
            entity_id = str(arg.get("id") or arg.get("entity") or arg.get("value") or "").strip()
        else:
            entity_id = str(arg or "").strip()
        meta = entity_meta.get(entity_id)
        if not isinstance(meta, dict):
            continue
        surface = str(meta.get("surface") or "").strip().lower()
        normalized = str(meta.get("normalized") or "").strip().lower()
        if surface.startswith(("all ", "every ", "each ")):
            return True
        if normalized in {"all", "everyone", "everybody"}:
            return True
    return False


def _has_safe_query(ir: dict[str, Any]) -> bool:
    for op in _candidate_operations(ir):
        if str(op.get("operation", "")).strip().lower() != "query":
            continue
        if str(op.get("safety", "")).strip().lower() == "safe":
            return True
    return False


def _is_query_scoped_identity_premise(ir: dict[str, Any], predicate: str) -> bool:
    if predicate not in IDENTITY_PREDICATES:
        return False
    if not _has_safe_query(ir):
        return False
    turn_type = str(ir.get("turn_type", "")).strip().lower()
    text = flatten_semantic_text(ir)
    if turn_type in {"query", "mixed"}:
        return True
    return any(marker in text for marker in ("hypothetical", "conditional question", " if ", "would"))


def _has_initialed_person_state_write(ir: dict[str, Any]) -> bool:
    if str(ir.get("turn_type", "")).strip().lower() == "correction" and _has_safe_direct_retract(ir):
        return False
    entity_meta = _entity_metadata_map(ir)
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        if str(op.get("source", "")).strip().lower() != "direct":
            continue
        if str(op.get("operation", "")).strip().lower() not in {"assert", "retract"}:
            continue
        predicate = _predicate_name(op.get("predicate"))
        if not predicate or predicate in IDENTITY_PREDICATES:
            continue
        raw_args = op.get("args", [])
        if not isinstance(raw_args, list):
            continue
        for arg in raw_args:
            entity_id = ""
            if isinstance(arg, dict):
                entity_id = str(arg.get("id") or arg.get("entity") or arg.get("value") or "").strip()
            else:
                entity_id = str(arg or "").strip()
            meta = entity_meta.get(entity_id)
            if isinstance(meta, dict) and _is_initialed_person_entity(meta):
                return True
    return False


def _is_initialed_person_entity(meta: dict[str, Any]) -> bool:
    entity_type = str(meta.get("type") or "").strip().lower()
    if entity_type and entity_type != "person":
        return False
    surface = str(meta.get("surface") or "").strip()
    normalized = str(meta.get("normalized") or "").strip()
    text = f"{surface} {normalized}"
    if re.search(r"\b[A-Za-z]\.\s+[A-Za-z][A-Za-z'-]+\b", text):
        return True
    atomish = _atomize(normalized or surface)
    return bool(re.fullmatch(r"[a-z]_[a-z][a-z0-9_]+", atomish))


def _is_pure_hypothetical_query(ir: dict[str, Any]) -> bool:
    if _has_ambiguous_or_unresolved_referent(ir):
        return False
    turn_type = str(ir.get("turn_type", "")).strip().lower()
    if turn_type not in {"query", "unknown"} and _normalize_decision(ir.get("decision")) != "answer":
        text = " ".join(
            [
                str(ir.get("decision", "")),
                json.dumps(ir.get("self_check", {}), ensure_ascii=False),
                json.dumps(ir.get("unsafe_implications", []), ensure_ascii=False),
            ]
        ).lower()
        if (
            "hypothetical" not in text
            and "counterfactual" not in text
            and "conditional question" not in text
        ):
            return False
    ops = _candidate_operations(ir)
    if not ops:
        return False
    safe_queries = [
        op
        for op in ops
        if str(op.get("operation", "")).strip().lower() == "query"
        and str(op.get("safety", "")).strip().lower() == "safe"
    ]
    if not safe_queries:
        return False
    unsafe_writes = [
        op
        for op in ops
        if str(op.get("operation", "")).strip().lower() in {"assert", "retract", "rule"}
        and str(op.get("source", "")).strip().lower() != "context"
        and not _is_query_scoped_identity_premise(ir, _predicate_name(op.get("predicate")))
    ]
    if unsafe_writes:
        return False
    text = flatten_semantic_text(ir)
    return (
        "hypothetical" in text
        or "counterfactual" in text
        or "conditional question" in text
        or "if " in text
        or "would" in text
    )


def _has_ambiguous_or_unresolved_referent(ir: dict[str, Any]) -> bool:
    refs = ir.get("referents", [])
    if not isinstance(refs, list):
        return False
    return any(
        isinstance(ref, dict)
        and str(ref.get("status", "")).strip().lower() in {"ambiguous", "unresolved"}
        for ref in refs
    )


def _speculative_ambiguous_observation_should_quarantine(ir: dict[str, Any]) -> bool:
    if _bad_commit_risk(ir) != "high":
        return False
    if not _has_ambiguous_or_unresolved_referent(ir):
        return False
    if not _has_unsafe_implications(ir):
        return False
    if _has_safe_candidate_operation(ir):
        return False
    assertions = ir.get("assertions", [])
    if not isinstance(assertions, list) or not assertions:
        return False
    for assertion in assertions:
        if not isinstance(assertion, dict):
            continue
        kind = str(assertion.get("kind", "")).strip().lower()
        try:
            certainty = float(assertion.get("certainty", 0.0) or 0.0)
        except Exception:
            certainty = 0.0
        if kind == "question" or certainty <= 0.55:
            return True
    return False


def _has_safe_candidate_operation(ir: dict[str, Any]) -> bool:
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() == "safe":
            return True
    return False


def flatten_semantic_text(value: Any) -> str:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, dict):
        return " ".join(flatten_semantic_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(flatten_semantic_text(item) for item in value)
    return str(value).lower()


def _ensure_period(clause: str) -> str:
    text = str(clause or "").strip()
    return text if text.endswith(".") else f"{text}."


def _components_from_clauses(clauses: list[str]) -> dict[str, list[str]]:
    atoms: set[str] = set()
    variables: set[str] = set()
    predicates: set[str] = set()
    for clause in clauses:
        match = re.match(r"\s*([a-z_][a-z0-9_]*)\s*\(", clause)
        if match:
            predicates.add(match.group(1))
        for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", clause):
            if token[:1].isupper() or token.startswith("_"):
                variables.add(token)
            else:
                atoms.add(token)
    return {"atoms": sorted(atoms), "variables": sorted(variables), "predicates": sorted(predicates)}


def _confidence_object(value: float) -> dict[str, float]:
    clipped = max(0.0, min(1.0, float(value)))
    return {"overall": clipped, "intent": clipped, "logic": clipped}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _bad_commit_risk(ir: dict[str, Any]) -> str:
    self_check = ir.get("self_check", {})
    risk = ""
    if isinstance(self_check, dict):
        risk = str(self_check.get("bad_commit_risk", "")).strip().lower()
    return risk if risk in {"low", "medium", "high"} else "medium"


OPTIONAL_METADATA_MISSING_SLOTS = {
    "source_document_id",
    "source_note_id",
    "source_encounter_id",
    "reason",
    "reason_for_quarantine",
    "quarantine_reason",
    "authority",
}


def _raw_missing_slots(ir: dict[str, Any]) -> list[str]:
    self_check = ir.get("self_check", {})
    if not isinstance(self_check, dict):
        return []
    return _string_list(self_check.get("missing_slots", []))


def _missing_slots(ir: dict[str, Any]) -> list[str]:
    slots = _raw_missing_slots(ir)
    if _has_safe_direct_write(ir):
        return [
            slot
            for slot in slots
            if slot.strip().lower() not in OPTIONAL_METADATA_MISSING_SLOTS
        ]
    return slots


def _semantic_ir_ambiguities(ir: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for item in _missing_slots(ir):
        out.append(f"missing slot: {item}")
    for ref in ir.get("referents", []) if isinstance(ir.get("referents"), list) else []:
        if not isinstance(ref, dict):
            continue
        status = str(ref.get("status", "")).strip().lower()
        if status in {"ambiguous", "unresolved"}:
            surface = str(ref.get("surface", "referent")).strip() or "referent"
            out.append(f"{surface} referent {status}")
    return out


def _semantic_ir_reason(ir: dict[str, Any], decision: str) -> str:
    missing = _missing_slots(ir)
    if missing:
        return f"Missing {missing[0]}"[:80]
    if decision == "reject":
        return "Rejected by semantic IR policy"
    if decision == "quarantine":
        return "Unsafe implication or claim"
    if decision == "clarify":
        return "Clarification needed"
    return "semantic_ir_v1"


def _first_question(ir: dict[str, Any]) -> str:
    questions = _string_list(ir.get("clarification_questions"))
    return questions[0] if questions else "Please clarify the missing semantic slot?"

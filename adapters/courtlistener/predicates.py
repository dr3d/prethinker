from __future__ import annotations

from typing import Any


LEGAL_COURTLISTENER_PREDICATE_CONTRACTS: list[dict[str, Any]] = [
    {"signature": "case_caption/2", "args": ["case", "caption"]},
    {"signature": "court_of/2", "args": ["case", "court"]},
    {"signature": "filed_on/2", "args": ["case_or_document", "date"]},
    {"signature": "decided_on/2", "args": ["case_or_opinion", "date"]},
    {"signature": "authored_by/2", "args": ["opinion_or_document", "judge"]},
    {"signature": "judge_on_case/2", "args": ["judge", "case"]},
    {"signature": "party_to_case/3", "args": ["party", "case", "role"]},
    {"signature": "represented_by/3", "args": ["attorney", "party", "case"]},
    {"signature": "cites_case/2", "args": ["citing_case", "cited_case"]},
    {"signature": "document_states/4", "args": ["document", "case", "content", "source"]},
    {"signature": "claim_made/4", "args": ["speaker_or_document", "claim_subject", "claim_content", "source"]},
    {"signature": "finding/4", "args": ["court_or_judge", "case", "finding_content", "source"]},
    {"signature": "holding/3", "args": ["case", "holding_content", "source"]},
    {"signature": "procedural_event/4", "args": ["case", "event_type", "date", "source"]},
    {"signature": "docket_entry/4", "args": ["case", "entry_number", "date", "description"]},
    {"signature": "candidate_identity/2", "args": ["ambiguous_alias", "candidate_entity"]},
]


def legal_predicate_signatures() -> list[str]:
    return [str(row["signature"]) for row in LEGAL_COURTLISTENER_PREDICATE_CONTRACTS]


def semantic_ir_contracts() -> list[dict[str, Any]]:
    return [
        {
            "signature": str(row["signature"]),
            "arguments": list(row.get("args", [])),
        }
        for row in LEGAL_COURTLISTENER_PREDICATE_CONTRACTS
    ]

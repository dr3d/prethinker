from __future__ import annotations

from typing import Any


SEC_CONTRACT_PREDICATE_CONTRACTS: list[dict[str, Any]] = [
    {"signature": "filing_form/2", "args": ["filing", "form_type"]},
    {"signature": "filed_on/2", "args": ["filing_or_document", "date"]},
    {"signature": "accession_number/2", "args": ["filing", "accession_number"]},
    {"signature": "exhibit_to_filing/3", "args": ["exhibit", "filing", "exhibit_type"]},
    {"signature": "party_to_contract/3", "args": ["party", "contract", "role"]},
    {"signature": "obligation/3", "args": ["obligated_party", "obligation_content", "source"]},
    {"signature": "entitled_to/3", "args": ["party", "right_or_benefit", "source"]},
    {"signature": "effective_on/2", "args": ["contract_or_clause", "date_or_trigger"]},
    {"signature": "terminates_on/2", "args": ["contract_or_clause", "date_or_trigger"]},
    {"signature": "subject_to/2", "args": ["clause_or_obligation", "condition"]},
    {"signature": "condition_met/2", "args": ["condition", "evidence_source"]},
    {"signature": "breach_event/2", "args": ["contract_or_obligation", "event"]},
    {"signature": "governing_law/2", "args": ["contract", "jurisdiction"]},
    {"signature": "document_states/4", "args": ["document", "filing_or_contract", "content", "source"]},
    {"signature": "candidate_identity/2", "args": ["ambiguous_alias", "candidate_entity"]},
]


def sec_contract_predicate_signatures() -> list[str]:
    return [str(row["signature"]) for row in SEC_CONTRACT_PREDICATE_CONTRACTS]


def semantic_ir_contracts() -> list[dict[str, Any]]:
    return [
        {
            "signature": str(row["signature"]),
            "arguments": list(row.get("args", [])),
        }
        for row in SEC_CONTRACT_PREDICATE_CONTRACTS
    ]

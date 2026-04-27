from __future__ import annotations

import re

from adapters.sec_edgar.models import FilingSourceRecord, SemanticIRHarnessCase
from adapters.sec_edgar.predicates import sec_contract_predicate_signatures, semantic_ir_contracts


def record_to_harness_case(record: FilingSourceRecord, *, index: int = 1) -> SemanticIRHarnessCase:
    filing_atom = _atom(record.accession_number or record.source_id)
    source_atom = _atom(f"{record.source}_{record.source_kind}_{record.source_id}")
    utterance_parts = []
    if record.company_name:
        utterance_parts.append(f"Company: {record.company_name}.")
    if record.form_type:
        utterance_parts.append(f"SEC form: {record.form_type}.")
    if record.accession_number:
        utterance_parts.append(f"Accession number: {record.accession_number}.")
    if record.filing_date:
        utterance_parts.append(f"Filed on: {record.filing_date}.")
    if record.exhibit_type:
        utterance_parts.append(f"Exhibit type: {record.exhibit_type}.")
    if record.text_excerpt:
        utterance_parts.append(f"Excerpt: {record.text_excerpt}")
    utterance = " ".join(utterance_parts).strip() or f"SEC EDGAR filing {record.source_id}."
    context = [
        f"Source: SEC EDGAR {record.source_kind} record {record.source_id}.",
        f"Source atom: {source_atom}.",
        f"Suggested filing atom: {filing_atom}.",
        "SEC filings and exhibits are source evidence, not investment advice or legal advice.",
        "Contract shall/must language creates obligations or constraints, not proof that an action already occurred.",
        "May/is entitled to language creates rights or permissions, not proof that the right was exercised.",
    ]
    if record.provenance_url:
        context.append(f"Provenance URL: {record.provenance_url}")
    return SemanticIRHarnessCase(
        id=f"sec_{record.source_kind}_{index:04d}",
        domain="sec_contracts",
        utterance=utterance,
        context=context,
        allowed_predicates=sec_contract_predicate_signatures(),
        predicate_contracts=semantic_ir_contracts(),
        expected_decision="mixed",
        admission_expectations={
            "must_preserve_obligation_not_fact": True,
            "must_preserve_condition_not_event": True,
            "must_scope_role_to_contract": True,
            "must_preserve_temporal_scope": True,
            "must_not_write": [
                "repaid(...) from shall repay language",
                "breach_event(...) from obligation-only language",
                "global borrower/lender role facts",
                "condition_met(...) without explicit evidence",
            ],
        },
    )


def _atom(value: str) -> str:
    text = str(value or "").casefold()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unknown"

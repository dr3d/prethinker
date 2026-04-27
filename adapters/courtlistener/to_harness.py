from __future__ import annotations

import re

from adapters.courtlistener.models import LegalSourceRecord, SemanticIRHarnessCase
from adapters.courtlistener.predicates import legal_predicate_signatures, semantic_ir_contracts


def record_to_harness_case(record: LegalSourceRecord, *, index: int = 1) -> SemanticIRHarnessCase:
    case_atom = _atom(record.title or record.source_id)
    source_atom = _atom(f"{record.source}_{record.source_kind}_{record.source_id}")
    utterance_parts = []
    if record.title:
        utterance_parts.append(f"Case caption: {record.title}.")
    if record.court:
        utterance_parts.append(f"Court: {record.court}.")
    if record.date_filed:
        utterance_parts.append(f"Date filed or decided: {record.date_filed}.")
    if record.judges:
        utterance_parts.append(f"Judges listed: {', '.join(record.judges)}.")
    if record.citations:
        utterance_parts.append(f"Citations listed: {', '.join(record.citations)}.")
    if record.text_excerpt:
        utterance_parts.append(f"Excerpt: {record.text_excerpt}")
    utterance = " ".join(utterance_parts).strip() or f"CourtListener record {record.source_id} has no excerpt."
    context = [
        f"Source: CourtListener {record.source_kind} record {record.source_id}.",
        f"Source atom: {source_atom}.",
        "CourtListener records are source evidence. They do not authorize legal advice or outcome prediction.",
        "Party allegations and complaint text are claims, not court findings.",
        "Citations are citation relations, not endorsement or precedent-following facts.",
    ]
    if record.provenance_url:
        context.append(f"Provenance URL: {record.provenance_url}")
    if case_atom:
        context.append(f"Suggested case atom: {case_atom}")
    return SemanticIRHarnessCase(
        id=f"courtlistener_{record.source_kind}_{index:04d}",
        domain="legal_courtlistener",
        utterance=utterance,
        context=context,
        allowed_predicates=legal_predicate_signatures(),
        predicate_contracts=semantic_ir_contracts(),
        expected_decision="mixed",
        admission_expectations={
            "must_preserve_claim_not_fact": True,
            "must_preserve_citation_not_endorsement": True,
            "must_scope_role_to_case": True,
            "must_preserve_temporal_scope": True,
            "must_not_write": [
                "finding(...) from allegation-only language",
                "follows_precedent(...) from cites_case-only language",
                "global plaintiff/defendant role facts",
            ],
        },
    )


def _atom(value: str) -> str:
    text = str(value or "").casefold()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unknown"

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class FilingSourceRecord:
    source: str
    source_kind: str
    source_id: str
    company_name: str | None = None
    cik: str | None = None
    accession_number: str | None = None
    form_type: str | None = None
    filing_date: str | None = None
    report_date: str | None = None
    primary_document: str | None = None
    exhibit_type: str | None = None
    text_excerpt: str = ""
    provenance_url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticIRHarnessCase:
    id: str
    domain: str
    utterance: str
    context: list[str]
    allowed_predicates: list[str]
    predicate_contracts: list[dict[str, Any]]
    expected_decision: str | None = None
    admission_expectations: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

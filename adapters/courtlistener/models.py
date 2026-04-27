from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class LegalSourceRecord:
    source: str
    source_kind: str
    source_id: str
    title: str | None = None
    court: str | None = None
    date_filed: str | None = None
    judges: list[str] = field(default_factory=list)
    parties: list[str] = field(default_factory=list)
    attorneys: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
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

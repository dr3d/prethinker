"""Stable public data models for the Prethinker Engine API."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class DocumentType(str, Enum):
    """Document content types accepted by the public Engine API."""

    MD = "md"
    TXT = "txt"
    PDF = "pdf"


@dataclass(slots=True)
class CleanlinessCounters:
    """Operational hygiene counters exposed on compile and query results."""

    compatibility_rows: int = 0
    runtime_load_errors: int = 0
    write_proposals: int = 0

    @property
    def is_clean(self) -> bool:
        return self.compatibility_rows == 0 and self.runtime_load_errors == 0 and self.write_proposals == 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(slots=True)
class SourceRecord:
    """A source-grounded evidence row returned through the public API."""

    record_id: str
    kb_id: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CompiledArtifactBundle:
    """Frozen files and structured metadata for a compiled document artifact."""

    schema_version: str
    artifact_paths: dict[str, str]
    world_facts: list[str] = field(default_factory=list)
    world_rules: list[str] = field(default_factory=list)
    epistemic_facts: list[str] = field(default_factory=list)
    ledger_facts: list[str] = field(default_factory=list)
    query_policy: dict[str, Any] = field(default_factory=dict)
    manifest: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_paths": dict(self.artifact_paths),
            "world_facts": list(self.world_facts),
            "world_rules": list(self.world_rules),
            "epistemic_facts": list(self.epistemic_facts),
            "ledger_facts": list(self.ledger_facts),
            "query_policy": dict(self.query_policy),
            "manifest": dict(self.manifest),
            "diagnostics": dict(self.diagnostics),
        }


@dataclass(slots=True)
class AuditTrace:
    """Query audit trace: failure surface, hygiene counters, and evidence."""

    failure_surface: str
    cleanliness_counters: CleanlinessCounters
    source_records: list[SourceRecord] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "failure_surface": self.failure_surface,
            "cleanliness_counters": self.cleanliness_counters.to_dict(),
            "source_records": [record.to_dict() for record in self.source_records],
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class KBMetadata:
    """Metadata for a compiled local KB artifact."""

    kb_id: str
    document_name: str
    document_type: str
    created_at: str
    updated_at: str
    source_record_count: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CompileResult:
    """Result returned by Engine.compile_document."""

    kb_id: str
    metadata: KBMetadata
    cleanliness_counters: CleanlinessCounters
    source_records: list[SourceRecord] = field(default_factory=list)
    artifact_bundle: CompiledArtifactBundle | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "kb_id": self.kb_id,
            "metadata": self.metadata.to_dict(),
            "cleanliness_counters": self.cleanliness_counters.to_dict(),
            "source_records": [record.to_dict() for record in self.source_records],
            "artifact_bundle": self.artifact_bundle.to_dict() if self.artifact_bundle is not None else None,
        }


@dataclass(slots=True)
class QueryResult:
    """Result returned by Engine.query."""

    kb_id: str
    question: str
    answer: str | None
    status: str
    audit_trace: AuditTrace

    def to_dict(self) -> dict[str, Any]:
        return {
            "kb_id": self.kb_id,
            "question": self.question,
            "answer": self.answer,
            "status": self.status,
            "audit_trace": self.audit_trace.to_dict(),
        }

from __future__ import annotations

from enum import Enum

import prethinker
from prethinker import (
    AuditTrace,
    CleanlinessCounters,
    CompileResult,
    DocumentType,
    Engine,
    KBMetadata,
    QueryResult,
    SourceRecord,
)


class ExternalDocumentType(str, Enum):
    MD = "md"


def test_public_package_exports_version_and_engine() -> None:
    assert prethinker.__version__ == "0.1.0"
    assert Engine is prethinker.Engine
    assert all(
        item is not None
        for item in [
            AuditTrace,
            CleanlinessCounters,
            CompileResult,
            DocumentType,
            KBMetadata,
            QueryResult,
            SourceRecord,
        ]
    )


def test_engine_compile_query_and_lifecycle(tmp_path) -> None:
    engine = Engine(storage_dir=tmp_path / "kbs")
    assert engine.is_ready is True

    compiled = engine.compile_document(
        document_name="sample.md",
        document_bytes=(
            b"# Inspection Summary\n\n"
            b"Maria Chen signed the inspection notice.\n"
            b"- Finding: storage temperature exceeded the written limit.\n"
        ),
        document_type=DocumentType.MD,
    )

    assert compiled.kb_id.startswith("kb_")
    assert compiled.cleanliness_counters.is_clean is True
    assert compiled.metadata.document_name == "sample.md"
    assert compiled.metadata.document_type == "md"
    assert compiled.metadata.source_record_count == 3
    assert [record.kb_id for record in compiled.source_records] == [compiled.kb_id] * 3

    listed = engine.list_kbs()
    assert [item.kb_id for item in listed] == [compiled.kb_id]
    assert engine.get_kb(compiled.kb_id) == listed[0]

    result = engine.query(kb_id=compiled.kb_id, question="Who signed the inspection notice?")
    assert result.kb_id == compiled.kb_id
    assert result.answer is None
    assert result.status == "evidence_available"
    assert result.audit_trace.failure_surface == "answer_surface_gap"
    assert result.audit_trace.cleanliness_counters.is_clean is True
    assert result.audit_trace.cleanliness_counters.write_proposals == 0
    assert result.audit_trace.source_records
    assert any("Maria Chen" in record.payload["text"] for record in result.audit_trace.source_records)

    assert engine.delete_kb(compiled.kb_id) is True
    assert engine.delete_kb(compiled.kb_id) is False
    assert engine.get_kb(compiled.kb_id) is None


def test_engine_accepts_enum_like_document_type(tmp_path) -> None:
    engine = Engine(storage_dir=tmp_path / "kbs")
    compiled = engine.compile_document(
        document_name="sample.md",
        document_bytes=b"Plain source line.",
        document_type=ExternalDocumentType.MD,
    )

    assert compiled.metadata.document_type == "md"


def test_query_missing_kb_returns_audit_trace(tmp_path) -> None:
    engine = Engine(storage_dir=tmp_path / "kbs")
    result = engine.query(kb_id="kb_missing", question="What is known?")

    assert result.status == "kb_not_found"
    assert result.answer is None
    assert result.audit_trace.failure_surface == "kb_not_found"
    assert result.audit_trace.cleanliness_counters.runtime_load_errors == 1


def test_pdf_compile_is_opaque_without_fake_source_records(tmp_path) -> None:
    engine = Engine(storage_dir=tmp_path / "kbs")
    compiled = engine.compile_document(
        document_name="sample.pdf",
        document_bytes=b"%PDF-opaque",
        document_type="pdf",
    )

    assert compiled.source_records == []
    result = engine.query(kb_id=compiled.kb_id, question="What does the PDF say?")
    assert result.status == "coverage_gap"
    assert result.answer is None
    assert result.audit_trace.failure_surface == "compile_surface_gap"

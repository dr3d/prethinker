from __future__ import annotations

from enum import Enum

import prethinker
from prethinker import (
    AuditTrace,
    CleanlinessCounters,
    CompiledArtifactBundle,
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
    assert prethinker.__version__ == "0.4.0"
    assert Engine is prethinker.Engine
    assert all(
        item is not None
        for item in [
            AuditTrace,
            CleanlinessCounters,
            CompiledArtifactBundle,
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
    assert compiled.artifact_bundle is not None
    assert compiled.artifact_bundle.schema_version == "semantic_artifact_bundle_v1"
    assert compiled.artifact_bundle.query_policy["qa_writes_allowed"] is False
    assert compiled.artifact_bundle.diagnostics["semantic_compile"]["status"] == "not_run"
    assert any(fact.startswith("source_document(") for fact in compiled.artifact_bundle.world_facts)
    assert any("source_record_text_atom" in fact for fact in compiled.artifact_bundle.ledger_facts)
    bundle_dir = tmp_path / "kbs" / compiled.kb_id / "compiled_source"
    assert (bundle_dir / "world.pl").exists()
    assert (bundle_dir / "epistemic.pl").exists()
    assert (bundle_dir / "ledgers.pl").exists()
    assert (bundle_dir / "query_policy.json").exists()
    assert (bundle_dir / "manifest.json").exists()
    assert (bundle_dir / "diagnostics.json").exists()
    assert "source_record_text" in (bundle_dir / "ledgers.pl").read_text(encoding="utf-8")

    listed = engine.list_kbs()
    assert [item.kb_id for item in listed] == [compiled.kb_id]
    assert engine.get_kb(compiled.kb_id) == listed[0]

    result = engine.query(kb_id=compiled.kb_id, question="Who signed the inspection notice?")
    assert result.kb_id == compiled.kb_id
    assert result.answer == "Maria Chen signed the inspection notice."
    assert result.status == "answered"
    assert result.audit_trace.failure_surface == "not_applicable"
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


def test_markdown_table_rows_compile_into_deterministic_ledger_fields(tmp_path) -> None:
    engine = Engine(storage_dir=tmp_path / "kbs")
    compiled = engine.compile_document(
        document_name="table.md",
        document_bytes=(
            b"# Corrective Actions\n\n"
            b"| Item | Status |\n"
            b"| --- | --- |\n"
            b"| Alarm calibration | Complete |\n"
        ),
        document_type="md",
    )

    assert compiled.artifact_bundle is not None
    ledger_text = (tmp_path / "kbs" / compiled.kb_id / "compiled_source" / "ledgers.pl").read_text(encoding="utf-8")
    assert 'source_record_field("src_line_0005", "Item", "Alarm calibration").' in ledger_text
    assert 'source_record_field("src_line_0005", "Status", "Complete").' in ledger_text


def test_query_missing_kb_returns_audit_trace(tmp_path) -> None:
    engine = Engine(storage_dir=tmp_path / "kbs")
    result = engine.query(kb_id="kb_missing", question="What is known?")

    assert result.status == "kb_not_found"
    assert result.answer is None
    assert result.audit_trace.failure_surface == "kb_not_found"
    assert result.audit_trace.cleanliness_counters.runtime_load_errors == 1


def test_query_keeps_weak_evidence_as_answer_surface_gap(tmp_path) -> None:
    engine = Engine(storage_dir=tmp_path / "kbs")
    compiled = engine.compile_document(
        document_name="sample.md",
        document_bytes=b"# Inspection Summary\n\nThe notice was logged.",
        document_type=DocumentType.MD,
    )

    result = engine.query(kb_id=compiled.kb_id, question="Who signed the inspection notice?")

    assert result.answer is None
    assert result.status == "evidence_available"
    assert result.audit_trace.failure_surface == "answer_surface_gap"
    assert result.audit_trace.source_records
    assert result.audit_trace.cleanliness_counters.write_proposals == 0


def test_pdf_compile_extracts_source_records_and_answers(tmp_path) -> None:
    engine = Engine(storage_dir=tmp_path / "kbs")
    compiled = engine.compile_document(
        document_name="sample.pdf",
        document_bytes=_minimal_pdf_bytes("Maria Chen signed the PDF notice."),
        document_type=DocumentType.PDF,
    )

    assert compiled.metadata.document_type == "pdf"
    assert compiled.metadata.source_record_count == 1
    assert compiled.source_records[0].payload["page"] == 1
    assert compiled.source_records[0].payload["page_line"] == 1
    assert compiled.source_records[0].payload["text"] == "Maria Chen signed the PDF notice."

    result = engine.query(kb_id=compiled.kb_id, question="Who signed the PDF notice?")
    assert result.answer == "Maria Chen signed the PDF notice."
    assert result.status == "answered"
    assert result.audit_trace.failure_surface == "not_applicable"


def test_unextractable_pdf_stays_coverage_gap_without_fake_source_records(tmp_path) -> None:
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


def _minimal_pdf_bytes(text: str) -> bytes:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 72 100 Td ({escaped}) Tj ET".encode("ascii")
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\n"
        b"endobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        b"5 0 obj\n<< /Length "
        + str(len(stream)).encode("ascii")
        + b" >>\nstream\n"
        + stream
        + b"\nendstream\nendobj\n",
    ]
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(output))
        output.extend(obj)
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode(
            "ascii"
        )
    )
    return bytes(output)

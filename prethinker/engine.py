"""Public Engine facade for Prethinker.

This alpha facade establishes the import/package boundary and a product-shaped
KB lifecycle. It intentionally avoids exposing the research harness directly.
"""

from __future__ import annotations

from io import BytesIO
import os
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from prethinker.models import (
    AuditTrace,
    CleanlinessCounters,
    CompileResult,
    DocumentType,
    KBMetadata,
    QueryResult,
    SourceRecord,
)
from prethinker.storage import LocalKBStore


class Engine:
    """Small public API for document compile, query, and KB lifecycle."""

    def __init__(self, storage_dir: str | os.PathLike[str] | None = None) -> None:
        self.storage_dir = Path(storage_dir or os.getenv("PRETHINKER_STORAGE_DIR", ".prethinker/kbs"))
        self._store = LocalKBStore(self.storage_dir)

    @classmethod
    def from_env(cls) -> "Engine":
        """Create an engine from environment configuration."""

        return cls(storage_dir=os.getenv("PRETHINKER_STORAGE_DIR"))

    @property
    def is_ready(self) -> bool:
        """Return True when the local KB store can be created and written."""

        return self._store.is_ready()

    def compile_document(
        self,
        *,
        document_name: str,
        document_bytes: bytes,
        document_type: DocumentType | str | Any,
    ) -> CompileResult:
        """Compile a document into a local KB artifact.

        The alpha compile path preserves deterministic source records for text
        documents and extractable PDFs. It does not yet run the full semantic
        compile harness.
        """

        if not isinstance(document_name, str) or not document_name.strip():
            raise ValueError("document_name must be a non-empty string")
        if not isinstance(document_bytes, bytes):
            raise TypeError("document_bytes must be bytes")

        doc_type = _normalize_document_type(document_type)
        source_records = _source_records_from_document(document_bytes, doc_type)
        metadata = self._store.create_kb(
            document_name=document_name.strip(),
            document_type=doc_type,
            document_bytes=document_bytes,
            source_records=source_records,
        )
        compiled_records = [
            SourceRecord(record_id=record.record_id, kb_id=metadata.kb_id, payload=dict(record.payload))
            for record in source_records
        ]
        cleanliness = CleanlinessCounters()
        return CompileResult(
            kb_id=metadata.kb_id,
            metadata=metadata,
            cleanliness_counters=cleanliness,
            source_records=compiled_records,
        )

    def query(self, *, kb_id: str, question: str) -> QueryResult:
        """Run a product-shaped query over a stored KB.

        This alpha query returns source-record evidence and an audit trace. It
        renders a deterministic extractive answer only when the source-record
        match is strong enough; otherwise it reports the appropriate gap.
        """

        if not question or not str(question).strip():
            raise ValueError("question must be a non-empty string")

        loaded = self._store.load_kb(kb_id)
        if loaded is None:
            trace = AuditTrace(
                failure_surface="kb_not_found",
                cleanliness_counters=CleanlinessCounters(runtime_load_errors=1),
                source_records=[],
                notes=[f"KB not found: {kb_id}"],
            )
            return QueryResult(
                kb_id=kb_id,
                question=str(question),
                answer=None,
                status="kb_not_found",
                audit_trace=trace,
            )

        metadata, records = loaded
        scored_matches = _score_source_records(records, str(question))
        matches = [record for _score, _index, record in scored_matches[:8]]
        answer = _render_extractive_answer(scored_matches)
        cleanliness = CleanlinessCounters()
        if not records:
            failure_surface = "compile_surface_gap"
            status = "coverage_gap"
            notes = ["The stored KB has no text source records. The document may be binary or have no extractable text."]
        elif answer is not None:
            failure_surface = "not_applicable"
            status = "answered"
            notes = [
                "Deterministic extractive answer rendered from source-record evidence; no LLM synthesis or durable writes."
            ]
        elif matches:
            failure_surface = "answer_surface_gap"
            status = "evidence_available"
            notes = [
                "Source-record evidence was found, but it was not strong enough for deterministic extractive answering."
            ]
        else:
            failure_surface = "query_surface_gap"
            status = "coverage_gap"
            notes = ["No source-record rows matched the question terms."]

        trace = AuditTrace(
            failure_surface=failure_surface,
            cleanliness_counters=cleanliness,
            source_records=matches,
            notes=notes,
        )
        return QueryResult(
            kb_id=metadata.kb_id,
            question=str(question),
            answer=answer,
            status=status,
            audit_trace=trace,
        )

    def list_kbs(self) -> list[KBMetadata]:
        """List stored KB metadata sorted by creation time."""

        return self._store.list_kbs()

    def get_kb(self, kb_id: str) -> KBMetadata | None:
        """Return KB metadata, or None when absent."""

        return self._store.get_kb(kb_id)

    def delete_kb(self, kb_id: str) -> bool:
        """Delete a KB by id. Returns False when the KB is absent."""

        return self._store.delete_kb(kb_id)


def _normalize_document_type(document_type: DocumentType | str | Any) -> str:
    value = getattr(document_type, "value", document_type)
    value = str(value or "").strip().lower()
    aliases = {
        "markdown": "md",
        "text": "txt",
    }
    return aliases.get(value, value)


def _source_records_from_document(document_bytes: bytes, document_type: str) -> list[SourceRecord]:
    if document_type in {"md", "txt"}:
        text = document_bytes.decode("utf-8", errors="replace")
        return _source_records_from_text(text)
    if document_type == "pdf":
        return _source_records_from_pdf(document_bytes)
    return []


def _source_records_from_text(text: str) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        kind = _source_line_kind(line)
        records.append(
            SourceRecord(
                record_id=f"src_line_{line_number:04d}",
                kb_id="",
                payload={
                    "line": line_number,
                    "kind": kind,
                    "text": line,
                    "text_atom": _text_atom(line),
                },
            )
        )
    return records


def _source_records_from_pdf(document_bytes: bytes) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    try:
        reader = PdfReader(BytesIO(document_bytes))
    except Exception:
        return []

    source_line_number = 0
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception:
            continue
        for page_line_number, raw_line in enumerate(page_text.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            source_line_number += 1
            records.append(
                SourceRecord(
                    record_id=f"src_page_{page_number:04d}_line_{page_line_number:04d}",
                    kb_id="",
                    payload={
                        "line": source_line_number,
                        "page": page_number,
                        "page_line": page_line_number,
                        "kind": _source_line_kind(line),
                        "text": line,
                        "text_atom": _text_atom(line),
                    },
                )
            )
    return records


def _source_line_kind(line: str) -> str:
    if line.startswith("#"):
        return "heading"
    if re.match(r"^[-*+]\s+", line):
        return "list_row"
    if "|" in line and line.count("|") >= 2:
        return "table_row"
    return "paragraph"


def _rank_source_records(records: list[SourceRecord], question: str) -> list[SourceRecord]:
    return [record for _score, _index, record in _score_source_records(records, question)[:8]]


def _score_source_records(records: list[SourceRecord], question: str) -> list[tuple[int, int, SourceRecord]]:
    question_tokens = _token_set(question)
    if not question_tokens:
        return []
    scored: list[tuple[int, int, SourceRecord]] = []
    for index, record in enumerate(records):
        payload_text = " ".join(str(value) for value in record.payload.values())
        record_tokens = _token_set(payload_text)
        overlap = question_tokens & record_tokens
        if not overlap:
            continue
        score = len(overlap) * 10
        if record.payload.get("kind") == "heading":
            score += 2
        scored.append((score, index, record))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return scored


def _render_extractive_answer(scored_matches: list[tuple[int, int, SourceRecord]]) -> str | None:
    for score, _index, record in scored_matches:
        if score < 20:
            return None
        if record.payload.get("kind") == "heading":
            continue
        text = str(record.payload.get("text", "")).strip()
        answer = _clean_source_text(text)
        if answer:
            return answer
    return None


def _clean_source_text(value: str) -> str:
    text = re.sub(r"^#{1,6}\s*", "", value.strip())
    text = re.sub(r"^[-*+]\s+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _token_set(value: str) -> set[str]:
    stop = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "by",
        "did",
        "do",
        "does",
        "for",
        "from",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "the",
        "to",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "with",
    }
    return {token for token in re.findall(r"[a-z0-9]+", value.casefold()) if len(token) >= 2 and token not in stop}


def _text_atom(value: str) -> str:
    atom = "_".join(re.findall(r"[a-z0-9]+", value.casefold()))
    return atom[:240]

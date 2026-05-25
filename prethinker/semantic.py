"""Bounded public semantic compiler for source-record artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
import re
from typing import Any
from urllib import error, request

from prethinker.artifacts import prolog_fact
from prethinker.models import SourceRecord


SEMANTIC_CORE_SCHEMA_VERSION = "semantic_core_v1"
DEFAULT_BASE_URL = "http://127.0.0.1:1234"
DEFAULT_MODEL = "qwen/qwen3.6-35b-a3b"


@dataclass(slots=True)
class SemanticCompileAdmission:
    """Deterministically admitted semantic compile result."""

    status: str
    world_facts: list[str] = field(default_factory=list)
    epistemic_facts: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    schema_version: str = SEMANTIC_CORE_SCHEMA_VERSION

    def to_bundle_payload(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "schema_version": self.schema_version,
            "world_facts": list(self.world_facts),
            "epistemic_facts": list(self.epistemic_facts),
            "diagnostics": dict(self.diagnostics),
        }


class OpenAICompatibleSemanticCompiler:
    """Small LM Studio/OpenAI-compatible semantic proposal client."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout_seconds: float | None = None,
        chunk_size: int | None = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("PRETHINKER_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or os.getenv("PRETHINKER_MODEL") or DEFAULT_MODEL
        self.api_key = api_key if api_key is not None else os.getenv("PRETHINKER_API_KEY")
        self.timeout_seconds = timeout_seconds or float(os.getenv("PRETHINKER_TIMEOUT_SECONDS", "180"))
        self.chunk_size = chunk_size or int(os.getenv("PRETHINKER_SEMANTIC_CHUNK_SIZE", "80"))

    @classmethod
    def from_env(cls) -> "OpenAICompatibleSemanticCompiler":
        return cls()

    def compile(
        self,
        *,
        kb_id: str,
        document_name: str,
        source_records: list[SourceRecord],
    ) -> SemanticCompileAdmission:
        if not source_records:
            return SemanticCompileAdmission(
                status="skipped",
                diagnostics={"reason": "no_extractable_source_records", "source_record_count": 0},
            )

        world_facts: list[str] = []
        epistemic_facts: list[str] = []
        skipped_candidates: list[dict[str, Any]] = []
        chunks = list(_chunks(source_records, max(1, self.chunk_size)))
        for chunk_index, chunk in enumerate(chunks, start=1):
            proposal = self._request_semantic_proposal(
                document_name=document_name,
                source_records=chunk,
                chunk_index=chunk_index,
                chunk_count=len(chunks),
            )
            admission = admit_semantic_proposal(
                kb_id=kb_id,
                proposal=proposal,
                source_records=source_records,
                chunk_index=chunk_index,
            )
            world_facts.extend(admission.world_facts)
            epistemic_facts.extend(admission.epistemic_facts)
            skipped_candidates.extend(admission.diagnostics.get("skipped_candidates") or [])

        world_facts = _dedupe(world_facts)
        epistemic_facts = _dedupe(epistemic_facts)
        return SemanticCompileAdmission(
            status="completed",
            world_facts=world_facts,
            epistemic_facts=epistemic_facts,
            diagnostics={
                "model": self.model,
                "base_url": self.base_url,
                "chunk_count": len(chunks),
                "source_record_count": len(source_records),
                "admitted_world_fact_count": len(world_facts),
                "admitted_epistemic_fact_count": len(epistemic_facts),
                "skipped_candidate_count": len(skipped_candidates),
                "skipped_candidates": skipped_candidates[:50],
            },
        )

    def _request_semantic_proposal(
        self,
        *,
        document_name: str,
        source_records: list[SourceRecord],
        chunk_index: int,
        chunk_count: int,
    ) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": _semantic_messages(
                document_name=document_name,
                source_records=source_records,
                chunk_index=chunk_index,
                chunk_count=chunk_count,
            ),
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        try:
            raw = self._post_chat_completion(payload)
        except error.HTTPError as exc:
            detail = _http_error_detail(exc)
            if exc.code == 400 and "response_format" in payload:
                fallback_payload = dict(payload)
                fallback_payload.pop("response_format", None)
                try:
                    raw = self._post_chat_completion(fallback_payload)
                except error.HTTPError as fallback_exc:
                    fallback_detail = _http_error_detail(fallback_exc)
                    raise RuntimeError(
                        "semantic compiler request failed: "
                        f"HTTP {exc.code}: {detail}; fallback HTTP {fallback_exc.code}: {fallback_detail}"
                    ) from fallback_exc
            else:
                raise RuntimeError(f"semantic compiler request failed: HTTP {exc.code}: {detail}") from exc
        data = json.loads(raw)
        content = data["choices"][0]["message"]["content"]
        return _parse_json_object(content)

    def _post_chat_completion(self, payload: dict[str, Any]) -> str:
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = request.Request(f"{self.base_url}/v1/chat/completions", data=body, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                return response.read().decode("utf-8")
        except error.HTTPError:
            raise
        except error.URLError as exc:
            raise RuntimeError(f"semantic compiler request failed: {exc}") from exc


def admit_semantic_proposal(
    *,
    kb_id: str,
    proposal: dict[str, Any],
    source_records: list[SourceRecord],
    chunk_index: int = 1,
) -> SemanticCompileAdmission:
    """Validate and admit source-anchored semantic proposal rows."""

    source_text = {record.record_id: str(record.payload.get("text", "")) for record in source_records}
    world_facts: list[str] = []
    epistemic_facts: list[str] = []
    skipped: list[dict[str, Any]] = []

    def admit_world(kind: str, index: int, item: dict[str, Any], predicate: str, *fields: str) -> None:
        source_record_id = _source_record_id(item)
        candidate_id = _candidate_id(item, kind, chunk_index, index)
        quote = _source_quote(item, fields)
        if not _supported(source_text, source_record_id, quote):
            skipped.append(_skip(kind, candidate_id, source_record_id, "unsupported_source_quote"))
            return
        values = [_text(item.get(field)) for field in fields]
        if not all(values):
            skipped.append(_skip(kind, candidate_id, source_record_id, "missing_required_field"))
            return
        world_facts.append(prolog_fact(predicate, candidate_id, *values, source_record_id))
        epistemic_facts.append(prolog_fact("semantic_source_support", candidate_id, source_record_id, quote))

    for index, item in enumerate(_items(proposal, "entities"), start=1):
        admit_world("entity", index, item, "semantic_entity", "kind", "name")
    for index, item in enumerate(_items(proposal, "events"), start=1):
        admit_world("event", index, item, "document_event", "label")
    for index, item in enumerate(_items(proposal, "statuses"), start=1):
        admit_world("status", index, item, "document_status", "subject", "status")
    for index, item in enumerate(_items(proposal, "actions"), start=1):
        admit_world("action", index, item, "document_action", "actor", "action", "target")
    for index, item in enumerate(_items(proposal, "obligations"), start=1):
        admit_world("obligation", index, item, "document_obligation", "actor", "action", "target")
    for index, item in enumerate(_items(proposal, "quantities"), start=1):
        admit_world("quantity", index, item, "document_quantity", "subject", "value", "unit")
    for index, item in enumerate(_items(proposal, "dates"), start=1):
        admit_world("date", index, item, "document_date", "subject", "date")
    for index, item in enumerate(_items(proposal, "identifiers"), start=1):
        admit_world("identifier", index, item, "document_identifier", "subject", "identifier", "value")

    for index, item in enumerate(_items(proposal, "claims"), start=1):
        source_record_id = _source_record_id(item)
        candidate_id = _candidate_id(item, "claim", chunk_index, index)
        quote = _source_quote(item, ("subject", "object"))
        if not _supported(source_text, source_record_id, quote):
            skipped.append(_skip("claim", candidate_id, source_record_id, "unsupported_source_quote"))
            continue
        subject = _text(item.get("subject"))
        predicate = _text(item.get("predicate"))
        object_value = _text(item.get("object"))
        if not subject or not predicate or not object_value:
            skipped.append(_skip("claim", candidate_id, source_record_id, "missing_required_field"))
            continue
        epistemic_facts.append(prolog_fact("source_claim", candidate_id, subject, predicate, object_value, source_record_id))
        epistemic_facts.append(prolog_fact("semantic_source_support", candidate_id, source_record_id, quote))

    for index, item in enumerate(_items(proposal, "findings"), start=1):
        source_record_id = _source_record_id(item)
        candidate_id = _candidate_id(item, "finding", chunk_index, index)
        quote = _source_quote(item, ("finding",))
        if not _supported(source_text, source_record_id, quote):
            skipped.append(_skip("finding", candidate_id, source_record_id, "unsupported_source_quote"))
            continue
        authority = _text(item.get("authority")) or "source"
        finding = _text(item.get("finding"))
        if not finding:
            skipped.append(_skip("finding", candidate_id, source_record_id, "missing_required_field"))
            continue
        epistemic_facts.append(prolog_fact("source_finding", candidate_id, authority, finding, source_record_id))
        epistemic_facts.append(prolog_fact("semantic_source_support", candidate_id, source_record_id, quote))

    for index, item in enumerate(_items(proposal, "uncertainties"), start=1):
        source_record_id = _source_record_id(item)
        candidate_id = _candidate_id(item, "uncertainty", chunk_index, index)
        quote = _source_quote(item, ("description",))
        if not _supported(source_text, source_record_id, quote):
            skipped.append(_skip("uncertainty", candidate_id, source_record_id, "unsupported_source_quote"))
            continue
        kind = _text(item.get("kind")) or "uncertainty"
        description = _text(item.get("description"))
        if not description:
            skipped.append(_skip("uncertainty", candidate_id, source_record_id, "missing_required_field"))
            continue
        epistemic_facts.append(prolog_fact("uncertainty_note", candidate_id, kind, description, source_record_id))
        epistemic_facts.append(prolog_fact("semantic_source_support", candidate_id, source_record_id, quote))

    world_facts = _dedupe(world_facts)
    epistemic_facts = _dedupe(epistemic_facts)
    return SemanticCompileAdmission(
        status="completed",
        world_facts=world_facts,
        epistemic_facts=epistemic_facts,
        diagnostics={
            "admitted_world_fact_count": len(world_facts),
            "admitted_epistemic_fact_count": len(epistemic_facts),
            "skipped_candidate_count": len(skipped),
            "skipped_candidates": skipped,
        },
    )


def semantic_compile_error_payload(exc: Exception) -> dict[str, Any]:
    return SemanticCompileAdmission(
        status="error",
        diagnostics={"error_type": type(exc).__name__, "error": str(exc)},
    ).to_bundle_payload()


def semantic_compile_skipped_payload(reason: str, source_record_count: int) -> dict[str, Any]:
    return SemanticCompileAdmission(
        status="skipped",
        diagnostics={"reason": reason, "source_record_count": source_record_count},
    ).to_bundle_payload()


def _semantic_messages(
    *,
    document_name: str,
    source_records: list[SourceRecord],
    chunk_index: int,
    chunk_count: int,
) -> list[dict[str, str]]:
    rows = [
        {
            "record_id": record.record_id,
            "section": record.payload.get("section", ""),
            "text": record.payload.get("text", ""),
        }
        for record in source_records
    ]
    system = (
        "You propose sparse semantic candidates for Prethinker. "
        "Return only JSON. Do not write Prolog. Do not infer facts not stated in the source records. "
        "Every candidate must include source_record_id and source_quote, where source_quote is an exact substring "
        "of that source record's text. Omit candidates if no exact quote supports them."
    )
    user = {
        "task": "Extract a bounded semantic_core_v1 proposal from these source records.",
        "document_name": document_name,
        "chunk_index": chunk_index,
        "chunk_count": chunk_count,
        "schema": {
            "entities": ["id", "kind", "name", "source_record_id", "source_quote"],
            "claims": ["id", "subject", "predicate", "object", "source_record_id", "source_quote"],
            "findings": ["id", "authority", "finding", "source_record_id", "source_quote"],
            "events": ["id", "label", "source_record_id", "source_quote"],
            "statuses": ["id", "subject", "status", "source_record_id", "source_quote"],
            "actions": ["id", "actor", "action", "target", "source_record_id", "source_quote"],
            "obligations": ["id", "actor", "action", "target", "source_record_id", "source_quote"],
            "quantities": ["id", "subject", "value", "unit", "source_record_id", "source_quote"],
            "dates": ["id", "subject", "date", "source_record_id", "source_quote"],
            "identifiers": ["id", "subject", "identifier", "value", "source_record_id", "source_quote"],
            "uncertainties": ["id", "kind", "description", "source_record_id", "source_quote"],
        },
        "source_records": rows,
    }
    return [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(user, ensure_ascii=False)}]


def _parse_json_object(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("semantic compiler response must be a JSON object")
    return data


def _http_error_detail(exc: error.HTTPError) -> str:
    try:
        detail = exc.read().decode("utf-8", errors="replace").strip()
    except Exception:
        detail = ""
    return detail or str(exc)


def _items(proposal: dict[str, Any], key: str) -> list[dict[str, Any]]:
    items = proposal.get(key) or []
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _source_record_id(item: dict[str, Any]) -> str:
    return _text(item.get("source_record_id"))


def _source_quote(item: dict[str, Any], fallback_fields: tuple[str, ...]) -> str:
    quote = _text(item.get("source_quote"))
    if quote:
        return quote
    for field in fallback_fields:
        value = _text(item.get(field))
        if value:
            return value
    return ""


def _supported(source_text: dict[str, str], source_record_id: str, quote: str) -> bool:
    text = source_text.get(source_record_id)
    if not text or not quote:
        return False
    return _squash(quote) in _squash(text)


def _candidate_id(item: dict[str, Any], kind: str, chunk_index: int, index: int) -> str:
    raw = _text(item.get("id")) or f"{kind}_{chunk_index}_{index}"
    safe = "_".join(re.findall(r"[a-z0-9]+", raw.casefold()))
    return f"{kind}_{safe}" if safe and not safe.startswith(f"{kind}_") else safe or f"{kind}_{chunk_index}_{index}"


def _skip(kind: str, candidate_id: str, source_record_id: str, reason: str) -> dict[str, Any]:
    return {"kind": kind, "id": candidate_id, "source_record_id": source_record_id, "reason": reason}


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()[:500]


def _squash(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


def _chunks(items: list[SourceRecord], size: int) -> list[list[SourceRecord]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        output.append(item)
    return output

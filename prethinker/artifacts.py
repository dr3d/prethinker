"""Compiled artifact bundle construction for the public Engine API."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from prethinker.models import CompiledArtifactBundle, SourceRecord


SEMANTIC_ARTIFACT_SCHEMA_VERSION = "semantic_artifact_bundle_v1"

COMPILED_ARTIFACT_PATHS = {
    "world": "compiled_source/world.pl",
    "epistemic": "compiled_source/epistemic.pl",
    "ledgers": "compiled_source/ledgers.pl",
    "query_policy": "compiled_source/query_policy.json",
    "manifest": "compiled_source/manifest.json",
    "diagnostics": "compiled_source/diagnostics.json",
    "bundle": "compiled_source/artifact_bundle.json",
}


def build_compiled_artifact_bundle(
    *,
    kb_id: str,
    document_name: str,
    document_type: str,
    document_bytes: bytes,
    source_records: list[SourceRecord],
) -> CompiledArtifactBundle:
    """Build the semantic compiled artifact bundle for a public compile.

    The public API currently admits deterministic source identity and ledger
    facts. Rich semantic world admission remains behind the research harness, so
    the bundle records that status explicitly instead of overstating compiled
    truth.
    """

    source_hash = hashlib.sha256(document_bytes).hexdigest()
    created_at = datetime.now(timezone.utc).isoformat()
    world_facts = [
        _fact("compiled_artifact", kb_id, SEMANTIC_ARTIFACT_SCHEMA_VERSION),
        _fact("source_document", kb_id),
        _fact("source_document_name", kb_id, document_name),
        _fact("source_document_type", kb_id, document_type),
        _fact("source_document_sha256", kb_id, source_hash),
    ]
    for record in source_records:
        world_facts.append(_fact("source_record", kb_id, record.record_id))

    epistemic_facts = [
        _fact("compile_artifact_status", kb_id, "semantic_bundle_created"),
        _fact("semantic_world_status", kb_id, "document_identity_only"),
        _fact("semantic_admission_status", kb_id, "pending_public_semantic_compiler"),
        _fact("query_policy_status", kb_id, "deterministic_extractive_source_record_policy"),
    ]
    if not source_records:
        epistemic_facts.append(_fact("coverage_status", kb_id, "no_extractable_source_records"))

    ledger_facts = _source_record_ledger_facts(source_records)
    query_policy = {
        "schema_version": "query_policy_v1",
        "answer_surfaces": ["world", "epistemic", "ledgers", "source_records"],
        "default_query_mode": "deterministic_extractive_source_record",
        "llm_synthesis": False,
        "qa_writes_allowed": False,
        "compatibility_adapters": "disabled",
    }
    manifest = {
        "schema_version": "compiled_artifact_manifest_v1",
        "artifact_schema_version": SEMANTIC_ARTIFACT_SCHEMA_VERSION,
        "kb_id": kb_id,
        "document_name": document_name,
        "document_type": document_type,
        "source_sha256": source_hash,
        "created_at": created_at,
        "source_record_count": len(source_records),
        "world_fact_count": len(world_facts),
        "world_rule_count": 0,
        "epistemic_fact_count": len(epistemic_facts),
        "ledger_fact_count": len(ledger_facts),
        "artifact_paths": dict(COMPILED_ARTIFACT_PATHS),
    }
    diagnostics = {
        "schema_version": "compile_diagnostics_v1",
        "semantic_compile": {
            "status": "not_run",
            "reason": (
                "public Engine writes the semantic artifact bundle contract; "
                "full LLM semantic admission remains behind the research harness"
            ),
        },
        "coverage": {
            "status": "source_records_available" if source_records else "no_extractable_source_records",
            "source_record_count": len(source_records),
        },
        "cleanliness": {
            "compatibility_rows": 0,
            "runtime_load_errors": 0,
            "write_proposals": 0,
        },
    }
    return CompiledArtifactBundle(
        schema_version=SEMANTIC_ARTIFACT_SCHEMA_VERSION,
        artifact_paths=dict(COMPILED_ARTIFACT_PATHS),
        world_facts=world_facts,
        world_rules=[],
        epistemic_facts=epistemic_facts,
        ledger_facts=ledger_facts,
        query_policy=query_policy,
        manifest=manifest,
        diagnostics=diagnostics,
    )


def render_compiled_artifact_files(bundle: CompiledArtifactBundle) -> dict[str, str]:
    """Render bundle members to relative file paths and textual contents."""

    return {
        bundle.artifact_paths["world"]: _render_prolog_program(
            title="world",
            schema_version=bundle.schema_version,
            facts=bundle.world_facts,
            rules=bundle.world_rules,
        ),
        bundle.artifact_paths["epistemic"]: _render_prolog_program(
            title="epistemic",
            schema_version=bundle.schema_version,
            facts=bundle.epistemic_facts,
            rules=[],
        ),
        bundle.artifact_paths["ledgers"]: _render_prolog_program(
            title="ledgers",
            schema_version=bundle.schema_version,
            facts=bundle.ledger_facts,
            rules=[],
        ),
        bundle.artifact_paths["query_policy"]: _json_text(bundle.query_policy),
        bundle.artifact_paths["manifest"]: _json_text(bundle.manifest),
        bundle.artifact_paths["diagnostics"]: _json_text(bundle.diagnostics),
        bundle.artifact_paths["bundle"]: _json_text(bundle.to_dict()),
    }


def compiled_artifact_bundle_from_dict(data: dict[str, Any]) -> CompiledArtifactBundle:
    """Rehydrate a bundle JSON mirror from storage."""

    return CompiledArtifactBundle(
        schema_version=str(data["schema_version"]),
        artifact_paths=dict(data.get("artifact_paths") or {}),
        world_facts=[str(item) for item in data.get("world_facts") or []],
        world_rules=[str(item) for item in data.get("world_rules") or []],
        epistemic_facts=[str(item) for item in data.get("epistemic_facts") or []],
        ledger_facts=[str(item) for item in data.get("ledger_facts") or []],
        query_policy=dict(data.get("query_policy") or {}),
        manifest=dict(data.get("manifest") or {}),
        diagnostics=dict(data.get("diagnostics") or {}),
    )


def _source_record_ledger_facts(source_records: list[SourceRecord]) -> list[str]:
    facts: list[str] = []
    for record in source_records:
        payload = record.payload
        kind = _payload_text(payload, "kind", default="source_row")
        line = _payload_int(payload, "line", default=0)
        section = _payload_text(payload, "section")
        label = _payload_text(payload, "label")
        facts.append(_fact("source_record_row", record.record_id, kind, line, section, label))
        facts.append(_fact("source_record_kind", record.record_id, kind))
        if line:
            facts.append(_fact("source_record_line", record.record_id, line))
        if section:
            facts.append(_fact("source_record_section", record.record_id, section))
        if label:
            facts.append(_fact("source_record_label", record.record_id, label))
        if payload.get("page") is not None:
            facts.append(_fact("source_record_page", record.record_id, _payload_int(payload, "page")))
        if payload.get("page_line") is not None:
            facts.append(_fact("source_record_page_line", record.record_id, _payload_int(payload, "page_line")))
        text_atom = _payload_text(payload, "text_atom")
        if text_atom:
            facts.append(_fact("source_record_text_atom", record.record_id, text_atom))
        text = _payload_text(payload, "text")
        if text:
            facts.append(_fact("source_record_text", record.record_id, text))
        cells = payload.get("cells")
        if isinstance(cells, list):
            for index, cell in enumerate(cells, start=1):
                facts.append(_fact("source_record_cell", record.record_id, index, str(cell)))
        headers = payload.get("headers")
        if isinstance(headers, list) and isinstance(cells, list):
            for header, cell in zip(headers, cells):
                facts.append(_fact("source_record_field", record.record_id, str(header), str(cell)))
    return facts


def _render_prolog_program(*, title: str, schema_version: str, facts: list[str], rules: list[str]) -> str:
    lines = [
        "% Generated by Prethinker public Engine.",
        f"% artifact: {title}",
        f"% schema_version: {schema_version}",
        "",
    ]
    lines.extend(facts)
    if rules:
        lines.append("")
        lines.extend(rules)
    lines.append("")
    return "\n".join(lines)


def _fact(name: str, *args: Any) -> str:
    return f"{name}({', '.join(_term(arg) for arg in args)})."


def _term(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    return json.dumps(str(value), ensure_ascii=False)


def _payload_text(payload: dict[str, Any], key: str, *, default: str = "") -> str:
    value = payload.get(key, default)
    if value is None:
        return default
    return str(value)


def _payload_int(payload: dict[str, Any], key: str, *, default: int = 0) -> int:
    try:
        return int(payload.get(key, default) or default)
    except (TypeError, ValueError):
        return default


def _json_text(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"

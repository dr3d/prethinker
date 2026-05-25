# Public API

Prethinker's public Python API starts with a narrow engine facade:

```python
from prethinker import Engine

engine = Engine(storage_dir=".prethinker/kbs")
compiled = engine.compile_document(
    document_name="source.md",
    document_bytes=b"# Source\n\nMaria Chen signed the notice.",
    document_type="md",
)

result = engine.query(
    kb_id=compiled.kb_id,
    question="Who signed the notice?",
)
```

This is an alpha package boundary, not a claim that the full research harness
has become a stable SDK. The purpose is to expose a small product-shaped
surface while keeping scripts, datasets, worksheets, and run artifacts private.

## Exports

```python
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
```

## Engine

```python
engine = Engine(storage_dir=".prethinker/kbs")
engine = Engine.from_env()
```

`Engine.from_env()` reads `PRETHINKER_STORAGE_DIR` when present.

Methods:

```python
engine.compile_document(
    *,
    document_name: str,
    document_bytes: bytes,
    document_type: str | DocumentType,
) -> CompileResult

engine.query(*, kb_id: str, question: str) -> QueryResult
engine.list_kbs() -> list[KBMetadata]
engine.get_kb(kb_id: str) -> KBMetadata | None
engine.delete_kb(kb_id: str) -> bool
```

`Engine.is_ready` is a cheap local storage readiness check.

## Models

`CleanlinessCounters` are always present:

```text
compatibility_rows: int
runtime_load_errors: int
write_proposals: int
```

`CompileResult` contains:

```text
kb_id
metadata
cleanliness_counters
source_records
artifact_bundle
```

`QueryResult` contains:

```text
kb_id
question
answer
status
audit_trace
```

`AuditTrace` contains:

```text
failure_surface
cleanliness_counters
source_records
notes
```

All models are dataclasses and provide `to_dict()` for JSON-facing adapters.

## Alpha Behavior

The `0.4.0` Engine facade compiles Markdown, plain-text documents, and PDFs
with extractable text into a semantic compiled artifact bundle. The bundle is
returned on `CompileResult.artifact_bundle` and persisted under the KB
directory:

```text
compiled_source/
  world.pl
  epistemic.pl
  ledgers.pl
  query_policy.json
  manifest.json
  diagnostics.json
  artifact_bundle.json
```

The public package now has the product-shaped artifact contract. Its admitted
semantic layer is intentionally narrow: deterministic source identity and
source-record ledgers are durable, while rich LLM semantic admission is recorded
as `not_run` in `diagnostics.json` until that research compiler is promoted into
a stable SDK surface.

The alpha query path returns source-record evidence and an audit trace. When a
source-record match is strong enough, `QueryResult.answer` contains a
deterministic extractive answer copied from the source row, with
`status = "answered"` and `failure_surface = "not_applicable"`.

When source evidence exists but is too weak for deterministic answer rendering,
`QueryResult.answer` remains `None` and `status` is `evidence_available` with
`failure_surface = "answer_surface_gap"`. This is deliberate: the public API
should report evidence without overclaiming.

The public query path does not use LLM synthesis, reference answers, or durable
query-time writes.

`query_policy.json` records that boundary:

```json
{
  "default_query_mode": "deterministic_extractive_source_record",
  "llm_synthesis": false,
  "qa_writes_allowed": false,
  "compatibility_adapters": "disabled"
}
```

PDF input is parsed with `pypdf`. Extractable page text becomes source records
with `page` and `page_line` payload fields. Scanned/image-only or malformed PDFs
remain clean coverage gaps: they are stored, but no fake source records are
created.

## Install Smoke

Local editable install:

```bash
pip install -e .
python -c "import prethinker; print(prethinker.__version__)"
```

Wheel check:

```bash
python -m pip wheel . -w tmp/package_smoke --no-deps
```

## Boundary

The public package should speak in engine terms:

- compile
- query
- KB
- source record
- audit trace
- coverage
- cleanliness counters

It should not expose fixture language, worksheet language, private run
artifacts, or current harness internals as stable API.

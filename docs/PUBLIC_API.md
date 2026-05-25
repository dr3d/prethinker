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

The `0.1.0` Engine facade preserves deterministic source records for Markdown
and plain-text documents. It stores KB artifacts in a local filesystem registry.

The alpha query path returns source-record evidence and an audit trace, but it
does not synthesize final natural-language answers yet. When source evidence is
available, `QueryResult.answer` remains `None` and `status` is
`evidence_available` with `failure_surface = "answer_surface_gap"`.

This is deliberate. The public API should not overclaim while the product-shaped
non-oracle answer renderer is still being hardened.

PDF input is accepted as an opaque stored document in this alpha. It does not
yet produce text source records through the public facade.

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

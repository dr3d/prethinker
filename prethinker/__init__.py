"""Public Prethinker package facade.

The package API is intentionally narrow. Research harnesses, datasets, scripts,
and worksheets remain private implementation/support surfaces.
"""

from prethinker.engine import Engine
from prethinker.models import (
    AuditTrace,
    CleanlinessCounters,
    CompiledArtifactBundle,
    CompileResult,
    DocumentType,
    KBMetadata,
    QueryResult,
    SourceRecord,
)

__version__ = "0.5.0"

__all__ = [
    "AuditTrace",
    "CleanlinessCounters",
    "CompiledArtifactBundle",
    "CompileResult",
    "DocumentType",
    "Engine",
    "KBMetadata",
    "QueryResult",
    "SourceRecord",
    "__version__",
]

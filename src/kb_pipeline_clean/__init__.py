"""Daily-driver harness surface for the cleaner KB pipeline factoring."""

from .parity_harness import (
    canonical_execution_result,
    canonical_parse_result,
    canonical_process_result,
    compare_signatures,
    normalizer_inventory_audit,
)
from .instrument import instrument_manifest, render_instrument_markdown
from .parse_normalization import NORMALIZER_PIPELINE, legacy_symbol_index, trace_plan

__all__ = [
    "NORMALIZER_PIPELINE",
    "canonical_execution_result",
    "canonical_parse_result",
    "canonical_process_result",
    "compare_signatures",
    "instrument_manifest",
    "legacy_symbol_index",
    "normalizer_inventory_audit",
    "render_instrument_markdown",
    "trace_plan",
]

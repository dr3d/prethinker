"""SEC EDGAR adapter package for Prethinker contract/obligation experiments."""

from adapters.sec_edgar.models import FilingSourceRecord, SemanticIRHarnessCase
from adapters.sec_edgar.normalize import normalize_submission_filing
from adapters.sec_edgar.to_harness import record_to_harness_case

__all__ = [
    "FilingSourceRecord",
    "SemanticIRHarnessCase",
    "normalize_submission_filing",
    "record_to_harness_case",
]

"""CourtListener adapter package for Prethinker legal intake experiments."""

from adapters.courtlistener.models import LegalSourceRecord, SemanticIRHarnessCase
from adapters.courtlistener.normalize import normalize_opinion_record
from adapters.courtlistener.to_harness import record_to_harness_case

__all__ = [
    "LegalSourceRecord",
    "SemanticIRHarnessCase",
    "normalize_opinion_record",
    "record_to_harness_case",
]

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ArchivalIdentifier:
    kind: str
    exact: str
    normalized_atom: str
    line: int


PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "exhibit_label",
        re.compile(r"\bExhibit\s+[A-Z]{1,4}(?:[-\s]\d+[A-Z]?)+(?:\.\d+)?\b"),
    ),
    (
        "section_or_tree_label",
        re.compile(r"\b(?:Tree|Bus|Room|Lot|Block|Parcel|Zone|Station)\s+#?[A-Z0-9][A-Z0-9.-]*\b"),
    ),
    (
        "timestamp",
        re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b"),
    ),
    (
        "archival_code",
        re.compile(r"\b[A-Z][A-Z0-9]{0,11}(?:-[A-Za-z0-9]{1,16}){1,5}\b"),
    ),
    (
        "case_or_docket_number",
        re.compile(r"\b(?:Case|Docket|No\.|File|Matter)\s+(?:No\.\s+)?[A-Z0-9][A-Z0-9:.-]*(?:-[A-Z0-9:.-]+)*\b"),
    ),
    (
        "named_system_with_model",
        re.compile(r"\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z0-9]+){1,5}\s+\d{3,5}[A-Z]?\b"),
    ),
)


def extract_archival_identifier_ledger(
    source_text: str,
    *,
    max_items: int = 180,
) -> dict[str, object]:
    """Extract exact lexical identifiers without interpreting source meaning.

    The ledger intentionally records only surface spans and line numbers. It
    does not infer relations, answer questions, or author KB clauses.
    """

    seen: set[tuple[str, str, int]] = set()
    identifiers: list[ArchivalIdentifier] = []
    for line_no, line in enumerate(source_text.splitlines(), start=1):
        for kind, pattern in PATTERNS:
            for match in pattern.finditer(line):
                exact = _clean_span(match.group(0))
                if not _useful_span(exact):
                    continue
                key = (kind, exact, line_no)
                if key in seen:
                    continue
                seen.add(key)
                identifiers.append(
                    ArchivalIdentifier(
                        kind=kind,
                        exact=exact,
                        normalized_atom=_normalize_atom(exact),
                        line=line_no,
                    )
                )
                if len(identifiers) >= max_items:
                    return _ledger(identifiers, truncated=True)
    return _ledger(identifiers, truncated=False)


def archival_identifier_context(ledger: dict[str, object] | None) -> list[str]:
    if not isinstance(ledger, dict):
        return []
    identifiers = ledger.get("identifiers")
    if not isinstance(identifiers, list) or not identifiers:
        return []
    return [
        "archival_identifier_ledger_v1 is deterministic lexical context, not truth and not a gold fact set.",
        "It records exact identifier-like spans and line numbers from the source so compiler passes can preserve printed labels instead of paraphrasing them.",
        "Use these exact strings only when the raw source supports the candidate operation and an allowed archival/source predicate can represent the span.",
        "Prefer exact_printed_identifier, row_display_label, row_source_name, document_identifier, exhibit_label, catalog_identifier, receipt_identifier, case_number, system_name, or row_value fields when preserving these spans.",
        "Do not infer ownership, authority, status, or causality from this ledger. It only pins lexical addressability.",
        "archival_identifier_ledger_v1_payload: "
        + json.dumps(ledger, ensure_ascii=False, sort_keys=True),
    ]


def _ledger(identifiers: Iterable[ArchivalIdentifier], *, truncated: bool) -> dict[str, object]:
    items = [asdict(item) for item in identifiers]
    return {
        "schema_version": "archival_identifier_ledger_v1",
        "description": "Deterministic lexical spans for archival addressability; not admitted facts.",
        "truncated": truncated,
        "identifier_count": len(items),
        "identifiers": items,
    }


def _clean_span(value: str) -> str:
    return value.strip().strip(".,;:()[]{}")


def _useful_span(value: str) -> bool:
    if len(value) < 3:
        return False
    folded = value.casefold()
    if folded in {"status", "active", "source"}:
        return False
    return True


def _normalize_atom(value: str) -> str:
    folded = value.casefold()
    folded = folded.replace("#", " number ")
    atom = re.sub(r"[^a-z0-9]+", "_", folded).strip("_")
    atom = re.sub(r"_+", "_", atom)
    return atom or "identifier"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--max-items", type=int, default=180)
    args = parser.parse_args()
    source_path = args.source
    text = source_path.read_text(encoding="utf-8-sig")
    print(json.dumps(extract_archival_identifier_ledger(text, max_items=args.max_items), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

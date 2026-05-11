from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SourceRecordRow:
    row_id: str
    kind: str
    line: int
    section: str
    exact: str
    label: str
    cells: list[str] | None = None
    headers: list[str] | None = None


HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")
TABLE_RE = re.compile(r"^\s*\|(.+)\|\s*$")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|[0-9]{1,3}[.)])\s+(.+?)\s*$")
LABEL_RE = re.compile(
    r"\b(?:"
    r"(?:Exhibit|Appendix|Schedule|Section|Clause|Item|Row|Entry|Event|Note|Memo)\s+[A-Z0-9][A-Z0-9:._-]*|"
    r"[A-Z][A-Z0-9]{0,11}(?:-[A-Za-z0-9]{1,16}){1,6}"
    r")\b"
)


def extract_source_record_ledger(
    source_text: str,
    *,
    max_rows: int = 220,
    max_chars_per_row: int = 360,
) -> dict[str, object]:
    """Extract source row addressability without interpreting source meaning.

    The ledger preserves line-numbered markdown-ish structure: headings, table
    rows, bullets, numbered rows, and labeled prose rows. It does not infer
    relations, answer questions, or author KB clauses.
    """

    rows: list[SourceRecordRow] = []
    current_section = ""
    pending_table_header: list[str] | None = None
    active_table_header: list[str] | None = None
    continuation_label = ""
    continuation_line = 0
    for line_no, raw_line in enumerate(source_text.splitlines(), start=1):
        line = _strip_blockquote_marker(raw_line.rstrip())
        if not line.strip():
            pending_table_header = None
            active_table_header = None
            continuation_label = ""
            continuation_line = 0
            continue
        heading = HEADING_RE.match(line)
        if heading:
            current_section = _clean_text(heading.group(2), max_chars=120)
            pending_table_header = None
            active_table_header = None
            continuation_label = ""
            continuation_line = 0
            rows.append(
                SourceRecordRow(
                    row_id=_row_id(line_no),
                    kind="heading",
                    line=line_no,
                    section=current_section,
                    exact=_clean_text(line, max_chars=max_chars_per_row),
                    label=current_section,
                )
            )
        elif TABLE_RE.match(line):
            cells = [_clean_text(part, max_chars=180) for part in line.strip().strip("|").split("|")]
            if _is_table_separator(cells):
                if pending_table_header:
                    active_table_header = pending_table_header
                pending_table_header = None
                continue
            headers = active_table_header if active_table_header and len(active_table_header) == len(cells) else None
            label = _best_label(line) or _clean_text(cells[0] if cells else "", max_chars=80)
            rows.append(
                SourceRecordRow(
                    row_id=_row_id(line_no),
                    kind="table_row",
                    line=line_no,
                    section=current_section,
                    exact=_clean_text(line, max_chars=max_chars_per_row),
                    label=label,
                    cells=cells,
                    headers=headers,
                )
            )
            continuation_label = label
            continuation_line = line_no
            if active_table_header is None:
                pending_table_header = cells
        elif bullet := BULLET_RE.match(line):
            pending_table_header = None
            active_table_header = None
            body = bullet.group(1)
            label = _best_label(line) or _clean_text(body.split(":", 1)[0], max_chars=80)
            rows.append(
                SourceRecordRow(
                    row_id=_row_id(line_no),
                    kind="list_row",
                    line=line_no,
                    section=current_section,
                    exact=_clean_text(line, max_chars=max_chars_per_row),
                    label=label,
                )
            )
            continuation_label = label
            continuation_line = line_no
        elif _best_label(line):
            pending_table_header = None
            active_table_header = None
            label = _best_label(line)
            rows.append(
                SourceRecordRow(
                    row_id=_row_id(line_no),
                    kind="labeled_line",
                    line=line_no,
                    section=current_section,
                    exact=_clean_text(line, max_chars=max_chars_per_row),
                    label=label,
                )
            )
            continuation_label = label
            continuation_line = line_no
        elif _has_source_anchor(line):
            pending_table_header = None
            active_table_header = None
            label = _clean_text(line.split(".", 1)[0], max_chars=80)
            rows.append(
                SourceRecordRow(
                    row_id=_row_id(line_no),
                    kind="anchored_line",
                    line=line_no,
                    section=current_section,
                    exact=_clean_text(line, max_chars=max_chars_per_row),
                    label=label,
                )
            )
            continuation_label = label
            continuation_line = line_no
        elif continuation_label and line_no == continuation_line + 1:
            pending_table_header = None
            active_table_header = None
            rows.append(
                SourceRecordRow(
                    row_id=_row_id(line_no),
                    kind="continuation_line",
                    line=line_no,
                    section=current_section,
                    exact=_clean_text(line, max_chars=max_chars_per_row),
                    label=continuation_label,
                )
            )
            continuation_line = line_no
        if len(rows) >= max_rows:
            return _ledger(rows, truncated=True)
    return _ledger(rows, truncated=False)


def source_record_ledger_context(ledger: dict[str, object] | None) -> list[str]:
    if not isinstance(ledger, dict):
        return []
    rows = ledger.get("rows")
    if not isinstance(rows, list) or not rows:
        return []
    return [
        "source_record_ledger_v1 is deterministic source-structure context, not truth and not a gold fact set.",
        "It records exact line-numbered headings, table rows, bullet rows, numbered rows, and labeled lines so compiler passes can preserve document addressability.",
        "For markdown tables, it preserves deterministic column headers alongside row cells so table values can be queried as source-record fields without semantic interpretation.",
        "For explicit roster tables with both a grouping column and a member column, it also emits roster_table_member/4 as structural table membership; it does not infer membership from nearby prose.",
        "Use this ledger only when the raw source supports the candidate operation and the allowed profile has compatible source/record predicates.",
        "Prefer stable row ids, exact printed labels, source section names, row_display_label, row_source_name, record_row, row_value, source_line, source_record_field, document_identifier, and status-at-row predicates when the profile supports them.",
        "Do not infer ownership, authority, status, causality, or counts from this ledger. It only pins source row addressability and exact row text.",
        "source_record_ledger_v1_payload: " + json.dumps(ledger, ensure_ascii=False, sort_keys=True),
    ]


def source_record_ledger_facts(
    ledger: dict[str, object] | None,
    *,
    max_rows: int = 220,
) -> list[str]:
    """Render deterministic source-address rows as queryable Prolog facts.

    These clauses preserve document structure only. They intentionally avoid
    semantic predicates such as ownership, authority, status, causality, or
    counts; those still have to be proposed by a semantic compile pass and
    admitted by the mapper.
    """

    if not isinstance(ledger, dict):
        return []
    rows = ledger.get("rows")
    if not isinstance(rows, list):
        return []
    facts: list[str] = []
    for raw in rows[: max(0, int(max_rows))]:
        if not isinstance(raw, dict):
            continue
        row_id = _atom(str(raw.get("row_id", "")))
        kind = _atom(str(raw.get("kind", "")))
        section = _atom(str(raw.get("section", ""))) or "no_section"
        label_atom = _atom(str(raw.get("label", ""))) or "no_label"
        if not row_id or not kind:
            continue
        try:
            line = int(raw.get("line", 0) or 0)
        except (TypeError, ValueError):
            line = 0
        facts.append(f"source_record_row({row_id}, {kind}, {line}, {section}, {label_atom}).")
        facts.append(f"source_record_kind({row_id}, {kind}).")
        if line > 0:
            facts.append(f"source_record_line({row_id}, {line}).")
        label = _atom(str(raw.get("label", "")))
        section_text = _atom(str(raw.get("section", "")))
        exact = _atom(str(raw.get("exact", "")))
        exact_key = _text_key(str(raw.get("exact", "")))
        if label:
            facts.append(f"source_record_label({row_id}, {label}).")
        if section_text:
            facts.append(f"source_record_section({row_id}, {section_text}).")
        if exact:
            facts.append(f"source_record_text_atom({row_id}, {exact}).")
        if exact_key:
            facts.append(f"source_record_text_key({row_id}, {exact_key}).")
        cells = raw.get("cells")
        if isinstance(cells, list):
            headers = raw.get("headers")
            header_atoms: list[str] = []
            if isinstance(headers, list):
                header_atoms = [_atom(str(header_raw)) for header_raw in headers]
            for index, cell_raw in enumerate(cells, start=1):
                cell = _atom(str(cell_raw))
                if not cell:
                    continue
                facts.append(f"source_record_cell({row_id}, {index}, {cell}).")
                header_atom = header_atoms[index - 1] if index <= len(header_atoms) else ""
                if header_atom:
                    facts.append(f"source_record_cell_header({row_id}, {index}, {header_atom}).")
                    facts.append(f"source_record_field({row_id}, {header_atom}, {cell}).")
                cell_key = _text_key(str(cell_raw))
                if cell_key:
                    facts.append(f"source_record_cell_text_key({row_id}, {index}, {cell_key}).")
            facts.extend(_roster_table_member_facts(raw, row_id=row_id))
        for token in _numeric_tokens(str(raw.get("exact", ""))):
            facts.append(f"source_record_numeric_token({row_id}, {token}).")
    return _dedupe(facts)


def _ledger(rows: Iterable[SourceRecordRow], *, truncated: bool) -> dict[str, object]:
    items = [asdict(row) for row in rows]
    return {
        "schema_version": "source_record_ledger_v1",
        "description": "Deterministic source row addressability; not admitted facts.",
        "truncated": truncated,
        "row_count": len(items),
        "rows": items,
    }


def _row_id(line_no: int) -> str:
    return f"src_line_{line_no:04d}"


def _strip_blockquote_marker(line: str) -> str:
    return re.sub(r"^\s{0,3}>\s?", "", str(line or "").rstrip())


def _clean_text(value: str, *, max_chars: int) -> str:
    cleaned = re.sub(r"\s+", " ", str(value).strip())
    return cleaned[:max_chars]


def _is_table_separator(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells if cell.strip())


def _best_label(line: str) -> str:
    bold_label = re.match(r"^\s*\*\*([^*]{1,80}?)\.?\*\*", line)
    if bold_label:
        return _clean_text(bold_label.group(1).rstrip(".:"), max_chars=80)
    matches = [_clean_text(match.group(0), max_chars=80) for match in LABEL_RE.finditer(line)]
    if not matches:
        return ""
    for label in matches:
        if label.casefold().startswith(("memo ", "note ", "section ")):
            tail = label.split(None, 1)[1] if " " in label else ""
            if "-" in tail:
                return tail
        if "-" in label and not label.casefold().startswith(("memo ", "note ", "section ")):
            return label
    return matches[0]


def _has_source_anchor(line: str) -> bool:
    text = str(line or "")
    if re.search(r"\b(?:location|adult lodging)\s*:", text, flags=re.IGNORECASE):
        return True
    if re.search(
        r"\b(?:appeal|award|cap|carryover|committee|declined|eligib|quorum|recusal|threshold|vote)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return True
    if re.search(
        r"\b(?:assign(?:ed)?\s+root\s+cause|root\s+cause\s+assignment|not\s+part\s+of\s+this\s+packet|separate\s+root-cause\s+analysis)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return True
    if re.search(
        r"\b(?:counts?\s*\([^)]*\)\s*sum\s+to|counts?\s+sum\s+to|sum\s+to\s+\d+)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return True
    if re.search(
        r"\b(?:timestamp|timestamps|clock|clocks)\b.*\b(?:audit|audited|external|local\s+time|synchroni[sz]ed|sync)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return True
    if re.search(
        r"\b(?:audit|audited|external|local\s+time|synchroni[sz]ed|sync)\b.*\b(?:timestamp|timestamps|clock|clocks)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return True
    if re.search(
        r"\b(?:referenced\s+but\s+not\s+reproduced|not\s+reproduced|reproduction\s+does\s+not\s+constitute|finding\s+of\s+fact|"
        r"authoritative\s+sources?|not\s+been\s+ruled\s+upon|has\s+not\s+been\s+ruled|court\s+has\s+not\s+found|"
        r"forensic\s+handwriting|ultimate\s+rulings|named\s+lender|loan\s+period|registrar|directed\s+delivery|"
        r"codicil\s+dispute|individual\s+access)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return True
    if re.search(r"\b\d{4}-\d{2}-\d{2}\b", text):
        return True
    if re.search(r"\b\d{1,2}:\d{2}\b", text):
        return True
    if re.search(r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\b", text, flags=re.IGNORECASE):
        return True
    if re.search(r"\b[A-Z]\.\s*[A-Z][A-Za-z]+\b.*\b\d+\b", text):
        return True
    if re.search(r"\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z0-9]+){1,5}\b", text) and re.search(r"\b\d+\b", text):
        return True
    return False


def _numeric_tokens(text: str) -> list[str]:
    out: list[str] = []
    for match in re.finditer(r"\b\d+(?:[._:-]\d+)*\b", str(text or "")):
        atom = _atom(match.group(0))
        if atom:
            out.append(atom)
    return out


def _roster_table_member_facts(raw: dict[str, object], *, row_id: str) -> list[str]:
    """Emit structural membership facts only when a table names the columns.

    This deliberately requires an explicit grouping column such as Homeroom,
    Group, Team, Cohort, or Bus and an explicit member column such as Students
    or Student IDs. Nearby prose and section titles may provide a version atom,
    but they do not create membership by themselves.
    """

    headers = raw.get("headers")
    cells = raw.get("cells")
    if not isinstance(headers, list) or not isinstance(cells, list):
        return []
    if len(headers) != len(cells):
        return []

    member_indexes = [
        index
        for index, header in enumerate(headers)
        if re.search(r"\b(?:student(?:s| ids?)?|members?|participants?)\b", str(header), flags=re.IGNORECASE)
    ]
    group_indexes = [
        index
        for index, header in enumerate(headers)
        if re.search(r"\b(?:homeroom|group|team|cohort|bus)\b", str(header), flags=re.IGNORECASE)
    ]
    if not member_indexes or not group_indexes:
        return []

    section = str(raw.get("section", "") or "")
    version = _version_atom_from_text(section) or _version_atom_from_text(" ".join(str(cell) for cell in cells))
    if not version:
        version = "unspecified_version"

    out: list[str] = []
    for group_index in group_indexes:
        group = _roster_group_atom(str(cells[group_index]))
        if not group:
            continue
        for member_index in member_indexes:
            member_header = _atom(str(headers[member_index]))
            for member, printed_member in _roster_member_mentions(str(cells[member_index])):
                out.append(f"roster_table_member({row_id}, {version}, {group}, {member}).")
                out.append(f"roster_table_member_header({row_id}, {member_header}).")
                out.append(f"roster_table_member_label({row_id}, {version}, {group}, {member}, {printed_member}).")
                out.append(f"roster_table_member_alias({member}, {printed_member}).")
                out.append(f"roster_table_scope({row_id}, {group}).")
                out.append(f"roster_table_version({row_id}, {version}).")
    return out


def _version_atom_from_text(value: str) -> str:
    text = str(value or "").lower()
    match = re.search(r"\bv(?P<major>\d+)(?:[._](?P<minor>\d+))?\b", text)
    if not match:
        return ""
    major = int(match.group("major"))
    minor = match.group("minor")
    if minor is None:
        return f"v{major}"
    return f"v{major}_{int(minor)}"


def _roster_group_atom(value: str) -> str:
    atom = _atom(value)
    if re.fullmatch(r"v_\d+_[a-z]", atom):
        return atom.removeprefix("v_")
    return atom


def _roster_member_atoms(value: str) -> list[str]:
    return _dedupe(member for member, _printed_member in _roster_member_mentions(value))


def _roster_member_mentions(value: str) -> list[tuple[str, str]]:
    text = str(value or "")
    out: list[tuple[str, str]] = []
    for chunk in re.split(r"[·,;]+", text):
        match = re.search(
            r"\b(?P<prefix>STU|S)[-_\s]?(?P<num>\d{3,})\b(?:\s+(?P<name>[A-Z][A-Za-z'-]*(?:\s+[A-Z][A-Za-z'-]*)?))?",
            chunk.strip(),
            flags=re.IGNORECASE,
        )
        if not match:
            continue
        prefix = match.group("prefix").lower()
        num = match.group("num")
        member = f"stu_{num}" if prefix == "stu" else f"s_{num}"
        printed = f"{match.group('prefix').upper()}-{num}"
        if match.group("name"):
            printed = f"{printed} {match.group('name').strip()}"
        printed_atom = _atom(printed)
        if member and printed_atom:
            out.append((member, printed_atom))
    return _dedupe(out)


def _atom(value: str) -> str:
    lowered = str(value or "").strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "_", lowered)
    lowered = lowered.strip("_")
    if not lowered:
        return ""
    if not lowered[0].isalpha():
        lowered = "v_" + lowered
    return lowered


def _text_key(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", str(value or "").strip())
    if not cleaned:
        return ""
    return "text_" + hashlib.sha1(cleaned.encode("utf-8")).hexdigest()[:16]


def _dedupe(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--max-rows", type=int, default=220)
    args = parser.parse_args()
    text = args.source.read_text(encoding="utf-8-sig")
    print(json.dumps(extract_source_record_ledger(text, max_rows=int(args.max_rows)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

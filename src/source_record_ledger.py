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
STATE_ABBR_RE = re.compile(
    r"^\s*(?:A[LKZR]|C[AOT]|D[CE]|FL|GA|HI|I[ADLN]|K[SY]|LA|M[ADEINOST]|N[CDEHJMVY]|O[HKR]|"
    r"P[AWR]|RI|S[CD]|T[NX]|UT|V[AIT]|W[AIVY])\b(?:\s*(?:\(|[,;|]|$))",
    re.IGNORECASE,
)


def extract_source_record_ledger(
    source_text: str,
    *,
    max_rows: int = 220,
    max_chars_per_row: int = 2400,
) -> dict[str, object]:
    """Extract source row addressability without interpreting source meaning.

    The ledger preserves line-numbered markdown-ish structure: headings, table
    rows, bullets, numbered rows, labeled prose rows, and plain paragraph rows.
    It does not infer relations, answer questions, or author KB clauses.
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
            cells = [_clean_text(part, max_chars=min(max_chars_per_row, 700)) for part in line.strip().strip("|").split("|")]
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
        else:
            pending_table_header = None
            active_table_header = None
            label = _clean_text(line.split(".", 1)[0], max_chars=80) or current_section or f"line {line_no}"
            rows.append(
                SourceRecordRow(
                    row_id=_row_id(line_no),
                    kind="paragraph_line",
                    line=line_no,
                    section=current_section,
                    exact=_clean_text(line, max_chars=max_chars_per_row),
                    label=label,
                )
            )
            continuation_label = label
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
        "It records exact line-numbered headings, table rows, bullet rows, numbered rows, labeled lines, and plain paragraph lines so compiler passes can preserve document addressability.",
        "For markdown tables and literal key-value source lines, it preserves deterministic headers/keys alongside values so source-record fields can be queried without semantic interpretation. It also exposes printed table-cell list items, cross-cell item pairs, and parenthetical qualifiers as source_record_cell_item/source_record_cell_item_pair/source_record_cell_item_qualifier rows.",
        "For explicit membership tables with both a grouping column and a member column, it also emits explicit_table_membership/4 as structural table membership; legacy roster_table_member/4 aliases are emitted only for school-roster compatibility. It does not infer membership from nearby prose.",
        "For heading/scope/list blocks, source_record_section_list_count/* counts contiguous printed source-list rows only. It is a source structure count, not a semantic claim that all listed items share any fact beyond the printed heading/scope text.",
        "Use this ledger only when the raw source supports the candidate operation and the allowed profile has compatible source/record predicates.",
        "Prefer stable row ids, exact printed labels, source section names, row_display_label, row_source_name, record_row, row_value, source_line, source_record_field, document_identifier, and status-at-row predicates when the profile supports them.",
        "Do not infer ownership, authority, status, causality, or semantic totals from this ledger. It only pins source row addressability, exact row text, and deterministic printed-row structure.",
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
    normalized_rows: list[dict[str, object]] = []
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
        normalized_rows.append(
            {
                "row_id": row_id,
                "kind": kind,
                "line": line,
                "section": section,
                "label": label_atom,
                "text": exact,
            }
        )
        if label:
            facts.append(f"source_record_label({row_id}, {label}).")
        if section_text:
            facts.append(f"source_record_section({row_id}, {section_text}).")
        if exact:
            facts.append(f"source_record_text_atom({row_id}, {exact}).")
            facts.append(f"source_record_row_context({row_id}, {label_atom}, {exact}, {section}).")
            facts.extend(_checkbox_state_facts(str(raw.get("exact", "")), row_id=row_id, label_atom=label_atom))
        if exact_key:
            facts.append(f"source_record_text_key({row_id}, {exact_key}).")
        facts.extend(_citation_facts(str(raw.get("exact", "")), row_id=row_id))
        facts.extend(_compact_date_facts(str(raw.get("exact", "")), row_id=row_id))
        facts.extend(_count_word_facts(str(raw.get("exact", "")), row_id=row_id))
        for field_name, field_value in _inline_key_value_fields(str(raw.get("exact", ""))):
            facts.append(f"source_record_inline_field({row_id}, {field_name}, {field_value}).")
            facts.append(f"source_record_field({row_id}, {field_name}, {field_value}).")
        cells = raw.get("cells")
        if isinstance(cells, list):
            headers = raw.get("headers")
            header_atoms: list[str] = []
            if isinstance(headers, list):
                header_atoms = [_atom(str(header_raw)) for header_raw in headers]
            cell_items_by_index: dict[int, list[str]] = {}
            cell_qualifiers_by_index_item: dict[tuple[int, str], list[str]] = {}
            for index, cell_raw in enumerate(cells, start=1):
                cell = _atom(str(cell_raw))
                header_atom = header_atoms[index - 1] if index <= len(header_atoms) else ""
                if not cell and header_atom:
                    cell = "blank"
                if not cell:
                    continue
                facts.append(f"source_record_cell({row_id}, {index}, {cell}).")
                if header_atom:
                    facts.append(f"source_record_cell_header({row_id}, {index}, {header_atom}).")
                    facts.append(f"source_record_field({row_id}, {header_atom}, {cell}).")
                cell_key = _text_key(str(cell_raw))
                if cell_key:
                    facts.append(f"source_record_cell_text_key({row_id}, {index}, {cell_key}).")
                for item, qualifier in _cell_list_items(str(cell_raw)):
                    cell_items_by_index.setdefault(index, []).append(item)
                    facts.append(f"source_record_cell_item({row_id}, {index}, {item}).")
                    if header_atom:
                        facts.append(f"source_record_field_item({row_id}, {header_atom}, {item}).")
                    if qualifier:
                        cell_qualifiers_by_index_item.setdefault((index, item), []).append(qualifier)
                        facts.append(f"source_record_cell_item_qualifier({row_id}, {index}, {item}, {qualifier}).")
                        if header_atom:
                            facts.append(
                                f"source_record_field_item_qualifier({row_id}, {header_atom}, {item}, {qualifier})."
                            )
            facts.extend(
                _cross_cell_item_pair_facts(
                    row_id=row_id,
                    header_atoms=header_atoms,
                    cell_items_by_index=cell_items_by_index,
                    cell_qualifiers_by_index_item=cell_qualifiers_by_index_item,
                )
            )
            facts.extend(_explicit_table_membership_facts(raw, row_id=row_id))
        for token in _numeric_tokens(str(raw.get("exact", ""))):
            facts.append(f"source_record_numeric_token({row_id}, {token}).")
        facts.extend(_parenthetical_alias_facts(str(raw.get("exact", "")), row_id=row_id))
    facts.extend(_section_list_count_facts(normalized_rows))
    return _dedupe(facts)


def _cross_cell_item_pair_facts(
    *,
    row_id: str,
    header_atoms: list[str],
    cell_items_by_index: dict[int, list[str]],
    cell_qualifiers_by_index_item: dict[tuple[int, str], list[str]],
) -> list[str]:
    facts: list[str] = []
    indexes = sorted(cell_items_by_index)
    for left_index in indexes:
        for right_index in indexes:
            if right_index <= left_index:
                continue
            for left_item in cell_items_by_index.get(left_index, []):
                for right_item in cell_items_by_index.get(right_index, []):
                    facts.append(
                        "source_record_cell_item_pair("
                        f"{row_id}, {left_index}, {left_item}, {right_index}, {right_item})."
                    )
                    left_header = header_atoms[left_index - 1] if left_index <= len(header_atoms) else ""
                    right_header = header_atoms[right_index - 1] if right_index <= len(header_atoms) else ""
                    if left_header and right_header:
                        facts.append(
                            "source_record_field_item_pair("
                            f"{row_id}, {left_header}, {left_item}, {right_header}, {right_item})."
                        )
                    for qualifier in cell_qualifiers_by_index_item.get((right_index, right_item), []):
                        facts.append(
                            "source_record_cell_item_pair_qualifier("
                            f"{row_id}, {left_index}, {left_item}, {right_index}, {right_item}, {qualifier})."
                        )
                        if left_header and right_header:
                            facts.append(
                                "source_record_field_item_pair_qualifier("
                                f"{row_id}, {left_header}, {left_item}, {right_header}, {right_item}, {qualifier})."
                            )
    return facts


def _citation_facts(text: str, *, row_id: str) -> list[str]:
    facts: list[str] = []
    for match in re.finditer(r"\b(?P<volume>\d{1,4})\s+FR\s+(?P<page>\d{1,7})\b", str(text or ""), flags=re.IGNORECASE):
        volume = _atom(match.group("volume"))
        page = _atom(match.group("page"))
        citation = _atom(f"{match.group('volume')}_fr_{match.group('page')}")
        if volume and page and citation:
            facts.append(f"source_record_citation({row_id}, {citation}).")
            facts.append(f"source_record_citation_parts({row_id}, {volume}, fr, {page}).")
    return facts


def _compact_date_facts(text: str, *, row_id: str) -> list[str]:
    facts: list[str] = []
    for match in re.finditer(r"\b(?P<month>\d{1,2})[-/](?P<day>\d{1,2})[-/](?P<year>\d{2,4})\b", str(text or "")):
        month = int(match.group("month"))
        day = int(match.group("day"))
        year = match.group("year")
        if not (1 <= month <= 12 and 1 <= day <= 31):
            continue
        full_year = int(year) + 2000 if len(year) == 2 else int(year)
        compact = _atom(match.group(0))
        canonical = _atom(f"{full_year:04d}_{month:02d}_{day:02d}")
        if compact and canonical:
            facts.append(f"source_record_date_alias({row_id}, {compact}, {canonical}).")
            facts.append(f"source_record_date_parts({row_id}, {full_year}, {month}, {day}).")
    return facts


_COUNT_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}


def _count_word_facts(text: str, *, row_id: str) -> list[str]:
    facts: list[str] = []
    for match in re.finditer(
        r"\b(" + "|".join(re.escape(word) for word in sorted(_COUNT_WORDS, key=len, reverse=True)) + r")\b",
        str(text or ""),
        flags=re.IGNORECASE,
    ):
        word = _atom(match.group(1))
        count = _COUNT_WORDS.get(match.group(1).casefold())
        if word and count is not None:
            facts.append(f"source_record_count_word({row_id}, {word}, {count}).")
    return facts


def _section_list_count_facts(rows: list[dict[str, object]]) -> list[str]:
    facts: list[str] = []
    ordered = sorted(
        [row for row in rows if row.get("row_id") and isinstance(row.get("line"), int)],
        key=lambda row: int(row.get("line", 0)),
    )
    for index, heading in enumerate(ordered):
        if heading.get("kind") not in {"paragraph_line", "labeled_line", "anchored_line"}:
            continue
        heading_text = str(heading.get("text", ""))
        if not _looks_like_list_count_heading(heading_text):
            continue
        scope = None
        members: list[dict[str, object]] = []
        for candidate in ordered[index + 1 :]:
            if candidate.get("section") != heading.get("section"):
                continue
            if int(candidate.get("line", 0)) > int(heading.get("line", 0)) + 18:
                break
            if scope is None and candidate.get("kind") != "list_row":
                if _looks_like_list_scope_text(str(candidate.get("text", ""))):
                    scope = candidate
                continue
            if candidate.get("kind") == "list_row":
                if scope is None:
                    continue
                members.append(candidate)
                continue
            if members:
                break
        if scope is None or not members:
            continue
        count = len(members)
        heading_row = str(heading.get("row_id", ""))
        scope_row = str(scope.get("row_id", ""))
        facts.append(f"source_record_section_list_count({heading_row}, {scope_row}, {count}).")
        facts.append(
            "source_record_section_list_count_detail("
            f"{heading_row}, {scope_row}, {str(heading.get('text', ''))}, {str(scope.get('text', ''))}, {count})."
        )
        for position, member in enumerate(members, start=1):
            facts.append(
                "source_record_section_list_count_member("
                f"{heading_row}, {scope_row}, {position}, {str(member.get('row_id', ''))}, {str(member.get('text', ''))})."
            )
    return facts


def _looks_like_list_count_heading(text: str) -> bool:
    tokens = set(_atom(str(text or "")).split("_"))
    return bool(tokens & {"item", "items", "product", "products"}) and bool(
        tokens & {"retail", "packaged", "bulk", "listed", "affected"}
    )


def _looks_like_list_scope_text(text: str) -> bool:
    tokens = set(_atom(str(text or "")).split("_"))
    return bool(tokens & {"sold", "distributed", "shipped", "available", "listed"}) and len(tokens) >= 3


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
    cleaned = re.sub(r"\s+", " ", _replace_source_state_glyphs(str(value)).strip())
    return cleaned[:max_chars]


def _replace_source_state_glyphs(value: str) -> str:
    text = str(value or "")
    replacements = {
        "\u00c2\u00a8": " unchecked_box ",
        "\u00a8": " unchecked_box ",
        "☐": " unchecked_box ",
        "☑": " checked_box ",
        "☒": " checked_box ",
        "✓": " checked_mark ",
        "✔": " checked_mark ",
    }
    for source, replacement in replacements.items():
        text = text.replace(source, replacement)
    return text


def _checkbox_state_facts(text: str, *, row_id: str, label_atom: str) -> list[str]:
    raw = str(text or "")
    normalized = _replace_source_state_glyphs(raw)
    state = ""
    if "unchecked_box" in normalized:
        state = "unchecked"
    elif "checked_box" in normalized or re.search(r"\[[xX]\]", raw):
        state = "checked"
    if not state:
        return []
    label_source = re.sub(r"unchecked_box|checked_box|\[[xX]\]", " ", normalized)
    label = label_atom if label_atom and label_atom not in {"no_label", "unchecked_box", "checked_box"} else _atom(label_source)
    if not label:
        return []
    return [
        f"source_record_checkbox_state({row_id}, {label}, {state}).",
        f"source_record_field({row_id}, {label}, {state}).",
    ]


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
        r"\b(?:count|counts|total|amount|number|estimate|estimated|stated|listed|included|excluded|reserve|provisional)\b",
        text,
        flags=re.IGNORECASE,
    ) and re.search(r"\b\d+\b", text):
        return True
    if _has_numeric_prose_anchor(text):
        return True
    if re.search(
        r"\b\d+\s+of\s+(?:the\s+)?\d+\s+(?:sampled\s+)?(?:samples?|plants|items|records|units)\b.*\b(?:tested|positive|negative|confirmed)\b",
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
        r"\b(?:referenced\s+but\s+not\s+reproduced|not\s+reproduced|reproduction\s+does\s+not\s+constitute|"
        r"finding\s+of\s+fact|authoritative\s+sources?|controlling\s+sources?|noncontrolling\s+sources?|"
        r"not\s+been\s+ruled\s+upon|has\s+not\s+been\s+ruled|has\s+not\s+found|has\s+not\s+determined|"
        r"recorded\s+but\s+not\s+(?:found|ruled|determined)|source\s+(?:states|records|supports|corroborates)|"
        r"basis\s+(?:is\s+)?(?:stated|recorded|supported|corroborated)|"
        r"(?:authorized|governed|controlled|directed|approved|recorded|compiled|filed|signed)\s+by)\b",
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
    if re.search(r"\b[A-Z][A-Za-z0-9'&.-]+(?:\s+[A-Z][A-Za-z0-9'&.-]+){1,8}\s*\([A-Z][A-Z0-9&.-]{1,11}\)", text):
        return True
    return False


def _has_numeric_prose_anchor(text: str) -> bool:
    """Preserve numeric prose without assuming English count vocabulary."""

    if not re.search(r"\b\d+\b", text):
        return False
    alpha_words = re.findall(r"\b[A-Za-z]{2,}\b", text)
    if len(alpha_words) < 4:
        return False
    if len("".join(alpha_words)) < 18:
        return False
    return True


def _numeric_tokens(text: str) -> list[str]:
    out: list[str] = []
    for match in re.finditer(r"\b\d+(?:[._:-]\d+)*\b", str(text or "")):
        atom = _atom(match.group(0))
        if atom:
            out.append(atom)
    return out


def _inline_key_value_fields(text: str) -> list[tuple[str, str]]:
    """Extract literal ``Key: Value`` pairs from one source row.

    This is source addressability only. It preserves printed key/value pairs but
    does not decide whether a key is semantically true, current, authoritative,
    or complete.
    """

    clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", str(text or ""))
    out: list[tuple[str, str]] = []
    active_key_raw = ""
    for segment in re.split(r"[;|]", clean):
        if ":" not in segment and not active_key_raw:
            continue
        if ":" in segment:
            key_raw, value_raw = segment.split(":", 1)
        else:
            key_raw = active_key_raw
            value_raw = segment
        key_raw = re.split(r"\s+(?:—|–|--)\s*", key_raw)[-1].strip()
        value_raw = value_raw.strip(" .")
        if not key_raw or not value_raw:
            continue
        if len(key_raw) > 40 or len(value_raw) > 180:
            continue
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9 /_-]{0,39}", key_raw):
            continue
        if not re.search(r"[A-Za-z0-9]", value_raw):
            continue
        key = _atom(key_raw)
        value = _atom(value_raw)
        if not key or not value or key == value:
            continue
        active_key_raw = key_raw
        out.append((key, value))
    return _dedupe_pairs(out)


def _cell_list_items(text: str) -> list[tuple[str, str]]:
    """Preserve printed table-cell list structure without interpreting it."""

    raw = str(text or "").strip()
    if not raw or len(raw) > 700:
        return []
    parts = _split_top_level_list(raw)
    out: list[tuple[str, str]] = []
    for part in parts:
        item_raw, qualifier_raw = _trailing_parenthetical(part.strip())
        item = _atom(item_raw)
        qualifier = _atom(qualifier_raw) if qualifier_raw else ""
        if not item:
            continue
        out.append((item, qualifier))
    return _dedupe_pairs(out)


def _split_top_level_list(text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    index = 0
    raw = str(text or "")
    while index < len(raw):
        char = raw[index]
        if char == "(":
            depth += 1
            current.append(char)
            index += 1
            continue
        if char == ")" and depth > 0:
            depth -= 1
            current.append(char)
            index += 1
            continue
        if depth == 0 and char == "," and not _comma_stays_inside_location(raw, index):
            _append_list_part(parts, current)
            current = []
            index += 1
            continue
        if depth == 0 and char == ";":
            _append_list_part(parts, current)
            current = []
            index += 1
            continue
        if depth == 0 and raw[index : index + 5].casefold() == " and ":
            _append_list_part(parts, current)
            current = []
            index += 5
            continue
        current.append(char)
        index += 1
    _append_list_part(parts, current)
    return parts or [raw]


def _comma_stays_inside_location(text: str, comma_index: int) -> bool:
    return bool(STATE_ABBR_RE.match(str(text or "")[comma_index + 1 :]))


def _append_list_part(parts: list[str], current: list[str]) -> None:
    part = "".join(current).strip()
    if part:
        parts.append(part)


def _trailing_parenthetical(text: str) -> tuple[str, str]:
    match = re.match(r"^(?P<item>.+?)\s*\((?P<qualifier>[^()]*)\)\s*$", str(text or "").strip())
    if not match:
        return text, ""
    item = match.group("item").strip()
    qualifier = match.group("qualifier").strip()
    if not item or not qualifier:
        return text, ""
    return item, qualifier


def _parenthetical_alias_facts(text: str, *, row_id: str) -> list[str]:
    """Emit source-local alias surfaces for ``Full Name (ABC)`` patterns.

    This is deterministic source scaffolding, not a global synonym claim. The
    trigger is intentionally narrow: a short uppercase parenthetical token whose
    letters match, or agency-style prefix-match, the initials of the immediately
    preceding capitalized phrase.
    """

    out: list[str] = []
    for match in re.finditer(r"\((?P<abbr>[A-Z][A-Z0-9&.-]{1,11})\)", str(text or "")):
        abbr_surface = match.group("abbr").strip()
        before = str(text or "")[: match.start()].rstrip()
        expansion_surface = _parenthetical_alias_expansion(before, abbr_surface)
        if not expansion_surface:
            continue
        abbr = _atom(abbr_surface)
        expansion = _atom(expansion_surface)
        if not abbr or not expansion or abbr == expansion:
            continue
        out.append(f"source_record_parenthetical_alias({row_id}, {abbr}, {expansion}).")
        out.append(f"source_record_alias({row_id}, {abbr}, {expansion}).")
        out.append(f"source_record_alias({row_id}, {expansion}, {abbr}).")
    return out


def _dedupe_pairs(values: list[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str]] = []
    for item in values:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _parenthetical_alias_expansion(before: str, abbr: str) -> str:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9'&.-]*", before)
    if not tokens:
        return ""
    phrase_tokens: list[str] = []
    for token in reversed(tokens[-10:]):
        lower = token.casefold()
        if token[:1].isupper() or lower in {"of", "and", "the", "for"}:
            phrase_tokens.append(token)
            continue
        break
    phrase_tokens.reverse()
    while phrase_tokens and not phrase_tokens[0][:1].isupper():
        phrase_tokens.pop(0)
    while phrase_tokens and phrase_tokens[0].casefold() in {"the", "a", "an"}:
        phrase_tokens.pop(0)
    capitalized = [token for token in phrase_tokens if token[:1].isupper()]
    if len(capitalized) < 2:
        return ""
    initials = "".join(token[0] for token in phrase_tokens if token[:1].isupper()).upper()
    normalized_abbr = re.sub(r"[^A-Z0-9]", "", abbr.upper())
    if not normalized_abbr:
        return ""
    if initials != normalized_abbr:
        prefix_match = (
            len(initials) >= 3
            and len(normalized_abbr) > len(initials)
            and len(normalized_abbr) - len(initials) <= 4
            and normalized_abbr.startswith(initials)
        )
        if not prefix_match:
            return ""
    return " ".join(phrase_tokens)


def _explicit_table_membership_facts(raw: dict[str, object], *, row_id: str) -> list[str]:
    """Emit structural membership facts only when a table names the columns.

    This deliberately requires an explicit grouping column such as group, team,
    cohort, unit, department, committee, or bus and an explicit member column
    such as members, participants, contributors, staff, or student IDs. Nearby
    prose and section titles may provide a version atom, but they do not create
    membership by themselves.
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
        if re.search(
            r"\b(?:student(?:s| ids?)?|members?|participants?|contributors?|assignees?|owners?|staff|people|persons?)\b",
            str(header),
            flags=re.IGNORECASE,
        )
    ]
    group_indexes = [
        index
        for index, header in enumerate(headers)
        if re.search(
            r"\b(?:homeroom|group|team|cohort|bus|unit|department|committee|workstream|section)\b",
            str(header),
            flags=re.IGNORECASE,
        )
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
            for member, printed_member, is_legacy_roster in _explicit_table_member_mentions(str(cells[member_index])):
                out.append(f"explicit_table_membership({row_id}, {version}, {group}, {member}).")
                out.append(f"explicit_table_member_header({row_id}, {member_header}).")
                out.append(f"explicit_table_member_label({row_id}, {version}, {group}, {member}, {printed_member}).")
                out.append(f"explicit_table_member_alias({member}, {printed_member}).")
                out.append(f"explicit_table_scope({row_id}, {group}).")
                out.append(f"explicit_table_version({row_id}, {version}).")
                if is_legacy_roster:
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
    return _dedupe(member for member, _printed_member, is_legacy in _explicit_table_member_mentions(value) if is_legacy)


def _explicit_table_member_mentions(value: str) -> list[tuple[str, str, bool]]:
    text = str(value or "")
    out: list[tuple[str, str, bool]] = []
    for chunk in re.split(r"[·,;]+", text):
        match = re.search(
            r"\b(?P<prefix>STU|S)[-_\s]?(?P<num>\d{3,})\b(?:\s+(?P<name>[A-Z][A-Za-z'-]*(?:\s+[A-Z][A-Za-z'-]*)?))?",
            chunk.strip(),
            flags=re.IGNORECASE,
        )
        if not match:
            generic_match = re.search(
                r"\b(?P<id>[A-Z][A-Z0-9]{1,11}[-_][A-Z0-9]{2,12})\b(?:\s+(?P<name>[A-Z][A-Za-z'-]*(?:\s+[A-Z][A-Za-z'-]*)?))?",
                chunk.strip(),
            )
            if not generic_match:
                continue
            member = _atom(generic_match.group("id"))
            printed = generic_match.group("id")
            if generic_match.group("name"):
                printed = f"{printed} {generic_match.group('name').strip()}"
            printed_atom = _atom(printed)
            if member and printed_atom:
                out.append((member, printed_atom, False))
            continue
        prefix = match.group("prefix").lower()
        num = match.group("num")
        member = f"stu_{num}" if prefix == "stu" else f"s_{num}"
        printed = f"{match.group('prefix').upper()}-{num}"
        if match.group("name"):
            printed = f"{printed} {match.group('name').strip()}"
        printed_atom = _atom(printed)
        if member and printed_atom:
            out.append((member, printed_atom, True))
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

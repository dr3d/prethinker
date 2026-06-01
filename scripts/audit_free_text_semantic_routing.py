#!/usr/bin/env python3
"""Audit Python-side semantic routing over free-text fields.

The sign-clean boundary is operational, not nominal:

- allowed: deterministic joins over typed compile slots, Prolog terms, dates,
  identifiers, numeric values, and explicit source-row IDs;
- suspicious/blocking: regex, token overlap, or substring routing over prose
  display fields, regardless of whether the text came from the user's question
  or from a source ledger.

This audit is intentionally conservative. It should be used as a stop-claim
tripwire and then narrowed by moving legitimate structural parsers into explicit
allowlists with reasons.
"""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATHS = (
    REPO_ROOT / "scripts" / "run_domain_bootstrap_qa.py",
    REPO_ROOT / "src",
)

RE_MODULE_CALLS = {"search", "match", "fullmatch", "findall", "finditer", "split", "sub", "subn"}
TOKENIZER_CALL_HINTS = {
    "_query_atom_tokens",
    "_loose_atom_token_set",
    "_source_record_field_name_tokens",
    "_source_text_question_needles",
    "_source_record_hint_tokens",
    "_count_scope_tokens",
    "_numeric_measure_surfaces",
}

FREE_TEXT_NAME_HINTS = (
    "utterance",
    "question",
    "reference",
    "source_text",
    "source_display",
    "sourcetextdisplay",
    "windowtextdisplay",
    "textdisplay",
    "text_atom",
    "textatom",
    "displayvalue",
    "prose",
)

GENERIC_FREE_TEXT_NAMES = {
    "text",
    "raw",
    "value",
    "display",
    "label",
    "line",
    "reference_text",
    "source_line",
}

SOURCE_TEXT_FUNCTION_HINTS = (
    "source_record",
    "source_text",
    "semantic_target",
    "question_overlap",
    "reference_supported",
)

ALLOWED_FUNCTIONS = {
    # Syntax/serialization helpers, not answer routing.
    "_md_cell",
    "_display_path",
    "_normalized_oracle_question_id",
    "_source_record_row_id",
    "parse_markdown_answer_key",
    "parse_numbered_markdown_questions",
}


@dataclass(frozen=True)
class FreeTextRouteHit:
    file: str
    line: int
    function: str
    category: str
    operation: str
    subject: str
    rationale: str
    claim_path: bool
    disposition: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", action="append", type=Path, default=[])
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--max-rows", type=int, default=500)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = tuple(args.path) if args.path else DEFAULT_PATHS
    report = build_report(paths, max_rows=max(1, int(args.max_rows)))
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.exit_zero:
        return 0
    return 0 if report["summary"]["status"] == "pass" else 1


def build_report(paths: tuple[Path, ...], *, max_rows: int = 500) -> dict[str, Any]:
    hits: list[FreeTextRouteHit] = []
    parse_errors: list[dict[str, Any]] = []
    files = list(_iter_files(paths))
    for path in files:
        try:
            hits.extend(_scan_file(path))
        except SyntaxError as exc:
            parse_errors.append({"file": _display_path(path), "line": exc.lineno, "error": str(exc)})
    category_counts: dict[str, int] = {}
    file_counts: dict[str, int] = {}
    for hit in hits:
        category_counts[hit.category] = category_counts.get(hit.category, 0) + 1
        file_counts[hit.file] = file_counts.get(hit.file, 0) + 1
    claim_hits = [hit for hit in hits if hit.claim_path]
    legacy_hits = [hit for hit in hits if not hit.claim_path]
    rows = [asdict(hit) for hit in sorted(hits, key=lambda row: (row.file, row.line, row.function))[:max_rows]]
    return {
        "schema_version": "free_text_semantic_routing_audit_v1",
        "scope": (
            "active Python runtime files; docs/tests/datasets excluded unless explicitly passed; "
            "claim-path status separates default strict QA from explicit forensic/structural legacy paths"
        ),
        "summary": {
            "status": "fail" if claim_hits else "pass",
            "file_count": len(files),
            "hit_count": len(hits),
            "claim_path_hit_count": len(claim_hits),
            "forensic_or_structural_hit_count": len(legacy_hits),
            "parse_error_count": len(parse_errors),
            "category_counts": dict(sorted(category_counts.items())),
            "file_counts": dict(sorted(file_counts.items())),
        },
        "rows_truncated": len(hits) > len(rows),
        "rows": rows,
        "parse_errors": parse_errors,
    }


def _scan_file(path: Path) -> list[FreeTextRouteHit]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    visitor = _Visitor(path=path)
    visitor.visit(tree)
    return visitor.hits


class _Visitor(ast.NodeVisitor):
    def __init__(self, *, path: Path) -> None:
        self.path = path
        self.function_stack: list[str] = []
        self.hits: list[FreeTextRouteHit] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.function_stack.append(node.name)
        self.generic_visit(node)
        self.function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def visit_Call(self, node: ast.Call) -> Any:
        function = self.function_stack[-1] if self.function_stack else "<module>"
        if function in ALLOWED_FUNCTIONS:
            self.generic_visit(node)
            return
        call_name = _call_name(node.func)
        if _is_re_call(call_name):
            subject = _subject_arg(node)
            if _touches_free_text(subject, function=function):
                self._add(
                    node,
                    function=function,
                    category="free_text_regex",
                    operation=call_name,
                    subject=subject,
                    rationale="regex operation over free-text-like subject in query/source-record path",
                )
        elif _call_leaf(call_name) in TOKENIZER_CALL_HINTS:
            subject = ", ".join(ast.unparse(arg)[:160] for arg in node.args)
            if _touches_free_text(subject, function=function):
                self._add(
                    node,
                    function=function,
                    category="free_text_tokenizer",
                    operation=call_name,
                    subject=subject,
                    rationale="tokenizer/measure extraction over free-text-like subject",
                )
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> Any:
        function = self.function_stack[-1] if self.function_stack else "<module>"
        if function not in ALLOWED_FUNCTIONS and any(isinstance(op, (ast.In, ast.NotIn)) for op in node.ops):
            subject = ast.unparse(node)[:220]
            if not _is_structural_membership_subject(subject) and _touches_free_text(subject, function=function):
                self._add(
                    node,
                    function=function,
                    category="free_text_membership",
                    operation="in/not-in",
                    subject=subject,
                    rationale="substring or token membership check over free-text-like subject",
                )
        self.generic_visit(node)

    def _add(
        self,
        node: ast.AST,
        *,
        function: str,
        category: str,
        operation: str,
        subject: str,
        rationale: str,
    ) -> None:
        claim_path, disposition = _claim_path_disposition(file=_display_path(self.path), function=function)
        self.hits.append(
            FreeTextRouteHit(
                file=_display_path(self.path),
                line=int(getattr(node, "lineno", 0) or 0),
                function=function,
                category=category,
                operation=operation,
                subject=subject,
                rationale=rationale,
                claim_path=claim_path,
                disposition=disposition,
            )
        )


def _is_re_call(call_name: str) -> bool:
    if call_name in {f"re.{name}" for name in RE_MODULE_CALLS}:
        return True
    return any(call_name.endswith(f".{name}") for name in RE_MODULE_CALLS)


def _subject_arg(node: ast.Call) -> str:
    call_name = _call_name(node.func)
    if not call_name.startswith("re."):
        return ast.unparse(node.args[0])[:220] if node.args else ""
    if len(node.args) < 2:
        return ""
    return ast.unparse(node.args[1])[:220]


def _touches_free_text(subject: str, *, function: str) -> bool:
    normalized_subject = subject.casefold().replace("_", "")
    if any(hint.replace("_", "") in normalized_subject for hint in FREE_TEXT_NAME_HINTS):
        return True
    function_folded = function.casefold()
    if not any(hint in function_folded for hint in SOURCE_TEXT_FUNCTION_HINTS):
        return False
    terms = {
        term.strip(" .()[]{}'\"").casefold()
        for term in subject.replace("(", " ").replace(")", " ").replace(",", " ").split()
    }
    return bool(terms & GENERIC_FREE_TEXT_NAMES)


def _is_structural_membership_subject(subject: str) -> bool:
    text = subject.casefold()
    structural_markers = {
        "signature",
        "predicate",
        "allowed_predicates",
        "disabled_support_predicates",
        "generic_query_placeholders",
        "display_vars",
        "seen",
        "item.get('role')",
        'item.get("role")',
        "soft_out_of_range_question_support_indexes",
        "_prose_bearing_arg_roles",
    }
    return any(marker in text for marker in structural_markers)


def _claim_path_disposition(*, file: str, function: str) -> tuple[bool, str]:
    """Classify whether a hit belongs to the default strict score path.

    This is intentionally narrow: the old source-record/free-text QA companion
    stack remains visible as debt, but it is not claim-path evidence now that
    strict QA is the default and non-strict routing requires an explicit
    forensic opt-in. Hits outside these reviewed buckets still block claims.
    """

    normalized_file = file.replace("/", "\\")
    if normalized_file == r"src\source_record_ledger.py" and function == "extract_source_record_ledger":
        return False, "structural_source_record_ledger_parser"
    if normalized_file == r"src\kb_pipeline_clean\parity_harness.py":
        return False, "parity_harness_payload_kind_normalization"
    if normalized_file == r"src\mcp_server.py" and function in {
        "_normalize_clarification_answer",
        "_clarification_family_relation_drift",
    }:
        return False, "clarification_control_plane_not_score_path"
    if normalized_file == r"scripts\run_domain_bootstrap_qa.py" and _qa_function_is_forensic_legacy(function):
        return False, "explicit_non_sign_clean_forensic_qa_surface"
    return True, "claim_path_blocker"


def _qa_function_is_forensic_legacy(function: str) -> bool:
    prefixes = (
        "_source_record",
        "_source_text",
        "_asks_for_source_record",
        "_current_state_source_text",
        "_source_field_question",
        "_source_section_question",
        "_source_label_question",
        "_clinic",
        "_grant_award",
    )
    exact = {
        "_is_temporal_source_text_question",
        "_is_quantity_source_text_question",
        "_utterance_asks_for_count",
        "_count_scope_tokens",
        "_display_phrase_contains_reference",
        "_numeric_measure_reference_supported_by_display_results",
        "_negative_reference_supported_by_results",
        "_agreement_counterparty_reference_supported_by_results",
        "_event_date_range_reference_supported_by_results",
        "_speaker_name_from_why_question",
        "_turn_section_targets_from_utterance",
        "_looks_like_source_record_person_label",
        "_parenthetical_role_name_reference_chunk_matches_entry",
        "_parenthetical_role_name_reference_chunks",
        "_source_display_ascii_tokens",
        "_source_rows_matching_query_tokens",
        "_display_source_record_section_label",
        "_asks_source_record_numeric_range",
        "_display_case_identifier_atom",
        "_display_source_record_exhibit",
        "_compiled_value_set_target_tokens",
        "_best_source_record_field_for_tokens",
        "_numeric_unit_ranges_from_text_atom",
        "_vote_threshold_from_query_results",
        "_reference_count_tokens",
        "_without_source_reference_stop_tokens",
    }
    return function in exact or function.startswith(prefixes)


def _call_leaf(call_name: str) -> str:
    return call_name.rsplit(".", 1)[-1]


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _iter_files(paths: tuple[Path, ...]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            files.append(path)
        elif path.is_dir():
            files.extend(candidate for candidate in path.rglob("*.py") if _include_file(candidate))
    return sorted(set(files))


def _include_file(path: Path) -> bool:
    parts = {part.casefold() for part in path.parts}
    return not ({"tests", "datasets", "__pycache__"} & parts)


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "# Free-Text Semantic Routing Audit",
        "",
        f"- Schema: `{report.get('schema_version')}`",
        f"- Status: `{summary.get('status')}`",
        f"- Hits: `{summary.get('hit_count')}`",
        f"- Claim-path hits: `{summary.get('claim_path_hit_count')}`",
        f"- Forensic/structural hits: `{summary.get('forensic_or_structural_hit_count')}`",
        f"- Parse errors: `{summary.get('parse_error_count')}`",
        f"- Category counts: `{summary.get('category_counts')}`",
        "",
        "## Meaning",
        "",
        "A claim-path hit means default strict QA can still pattern-match or tokenize prose-like fields.",
        "Forensic/structural hits remain visible debt, but do not support sign-clean score claims unless the run explicitly opts out of strict mode.",
    ]
    rows = report.get("rows", [])
    claim_rows = [row for row in rows if row.get("claim_path")]
    legacy_rows = [row for row in rows if not row.get("claim_path")]
    if claim_rows:
        lines.extend(["", "## Claim-Path Blocking Rows", "", "| File | Line | Function | Category | Operation | Subject |", "| --- | ---: | --- | --- | --- | --- |"])
        for row in claim_rows[:80]:
            lines.append(
                "| `{}` | {} | `{}` | `{}` | `{}` | `{}` |".format(
                    row.get("file", ""),
                    row.get("line", ""),
                    row.get("function", ""),
                    row.get("category", ""),
                    row.get("operation", ""),
                    _md_cell(str(row.get("subject", ""))[:120]),
                )
            )
    if legacy_rows:
        lines.extend(["", "## Rows", "", "| File | Line | Function | Category | Operation | Subject |", "| --- | ---: | --- | --- | --- | --- |"])
        for row in legacy_rows[:80]:
            lines.append(
                "| `{}` | {} | `{}` | `{}` | `{}` | `{}` |".format(
                    row.get("file", ""),
                    row.get("line", ""),
                    row.get("function", ""),
                    row.get("category", ""),
                    row.get("operation", ""),
                    _md_cell(str(row.get("subject", ""))[:120]),
                )
            )
    return "\n".join(lines).rstrip() + "\n"


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Audit regex use near utterance/question/query interpretation.

This is an informational governance audit. It does not fail CI. The purpose is
to make Python-side language triggers visible so they can be migrated toward
structured query intent over time.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATHS = (
    REPO_ROOT / "scripts" / "run_domain_bootstrap_qa.py",
    REPO_ROOT / "src",
)

QUERY_NAMES = {"utterance", "question", "query", "queries", "text"}
QUERY_NAME_FRAGMENTS = ("utterance", "question", "query")
RE_MODULE_CALLS = {"search", "match", "fullmatch", "findall", "finditer", "split", "sub", "subn"}
ALLOWED_SYNTAX_HINTS = {
    "prolog",
    "predicate",
    "signature",
    "clause",
    "atom",
    "identifier",
    "schema",
    "json",
    "url",
}
STRUCTURAL_PATTERN_HINTS = (
    '"',
    "'",
    "`",
    "?P<",
    "[A-Z]",
    "[a-z]",
    "\\d",
    "\\s",
)
SEMANTIC_PATTERN_HINT_RE = re.compile(r"[A-Za-z]{3,}(?:\|[A-Za-z]{3,}){1,}")
FORBIDDEN_PATTERN_HINT_RE = re.compile(
    r"\b(?:fresh_ugly|ugly_public|sealed_unseen|native_corpus|"
    r"black_lantern|identifier_ledger|lantern_school|sherlock|holmes)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class RegexHit:
    file: str
    line: int
    function: str
    category: str
    call: str
    pattern: str
    subject: str
    rationale: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", action="append", type=Path, default=[])
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--max-rows", type=int, default=500)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = tuple(args.path) if args.path else DEFAULT_PATHS
    report = build_report(paths, max_rows=max(1, int(args.max_rows)))
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def build_report(paths: tuple[Path, ...], *, max_rows: int = 500) -> dict[str, Any]:
    files = list(_iter_files(paths))
    hits: list[RegexHit] = []
    parse_errors: list[dict[str, Any]] = []
    for path in files:
        try:
            hits.extend(_scan_file(path))
        except SyntaxError as exc:
            parse_errors.append(
                {
                    "file": _display_path(path),
                    "line": exc.lineno,
                    "error": str(exc),
                }
            )
    category_counts: dict[str, int] = {}
    file_counts: dict[str, int] = {}
    for hit in hits:
        category_counts[hit.category] = category_counts.get(hit.category, 0) + 1
        file_counts[hit.file] = file_counts.get(hit.file, 0) + 1
    rows = [hit.__dict__ for hit in sorted(hits, key=lambda row: (row.file, row.line, row.function))[:max_rows]]
    return {
        "schema_version": "utterance_regex_governance_audit_v1",
        "scope": "active Python runtime files; docs/tests/datasets excluded unless explicitly passed",
        "summary": {
            "file_count": len(files),
            "regex_hit_count": len(hits),
            "parse_error_count": len(parse_errors),
            "category_counts": dict(sorted(category_counts.items())),
            "file_counts": dict(sorted(file_counts.items())),
            "status": "informational",
        },
        "rows_truncated": len(hits) > len(rows),
        "rows": rows,
        "parse_errors": parse_errors,
    }


def _scan_file(path: Path) -> list[RegexHit]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    visitor = _RegexVisitor(path=path)
    visitor.visit(tree)
    return visitor.hits


class _RegexVisitor(ast.NodeVisitor):
    def __init__(self, *, path: Path) -> None:
        self.path = path
        self.stack: list[ast.AST] = []
        self.function_stack: list[str] = []
        self.hits: list[RegexHit] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.function_stack.append(node.name)
        self.stack.append(node)
        self.generic_visit(node)
        self.stack.pop()
        self.function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def visit_Lambda(self, node: ast.Lambda) -> Any:
        self.stack.append(node)
        self.generic_visit(node)
        self.stack.pop()

    def visit_Call(self, node: ast.Call) -> Any:
        call_name = _call_name(node.func)
        if _is_re_call(call_name) and self._touches_query_language(node):
            pattern = _pattern_arg(node)
            subject = _subject_arg(node)
            function = self.function_stack[-1] if self.function_stack else "<module>"
            category, rationale = _classify(
                pattern=pattern,
                subject=subject,
                function=function,
                call_name=call_name,
                file=_display_path(self.path),
            )
            self.hits.append(
                RegexHit(
                    file=_display_path(self.path),
                    line=int(getattr(node, "lineno", 0) or 0),
                    function=function,
                    category=category,
                    call=call_name,
                    pattern=pattern,
                    subject=subject,
                    rationale=rationale,
                )
            )
        self.generic_visit(node)

    def _touches_query_language(self, node: ast.Call) -> bool:
        enclosing = self.stack[-1] if self.stack else None
        if isinstance(enclosing, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names = {arg.arg for arg in [*enclosing.args.args, *enclosing.args.kwonlyargs]}
            if names & QUERY_NAMES:
                return True
            if any(fragment in name.casefold() for name in names for fragment in QUERY_NAME_FRAGMENTS):
                return True
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                name = child.id.casefold()
                if name in QUERY_NAMES or any(fragment in name for fragment in QUERY_NAME_FRAGMENTS):
                    return True
            elif isinstance(child, ast.Attribute):
                name = child.attr.casefold()
                if any(fragment in name for fragment in QUERY_NAME_FRAGMENTS):
                    return True
        function = self.function_stack[-1] if self.function_stack else ""
        return any(fragment in function.casefold() for fragment in QUERY_NAME_FRAGMENTS)


def _is_re_call(call_name: str) -> bool:
    if call_name in {f"re.{name}" for name in RE_MODULE_CALLS}:
        return True
    return any(call_name.endswith(f".{name}") for name in RE_MODULE_CALLS)


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _pattern_arg(node: ast.Call) -> str:
    call_name = _call_name(node.func)
    if not call_name.startswith("re."):
        return "<compiled-regex>"
    if not node.args:
        return ""
    value = _literal_string(node.args[0])
    if value:
        return value[:220]
    return ast.unparse(node.args[0])[:220]


def _subject_arg(node: ast.Call) -> str:
    call_name = _call_name(node.func)
    if not call_name.startswith("re."):
        if node.args:
            return ast.unparse(node.args[0])[:220]
        return ""
    if len(node.args) < 2:
        return ""
    return ast.unparse(node.args[1])[:220]


def _literal_string(node: ast.AST) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "<f-string>"
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _literal_string(node.left)
        right = _literal_string(node.right)
        if left or right:
            return f"{left}{right}"
    return ""


def _classify(
    *,
    pattern: str,
    subject: str,
    function: str,
    call_name: str,
    file: str,
) -> tuple[str, str]:
    joined = " ".join([pattern, subject, function, call_name, file]).casefold()
    if FORBIDDEN_PATTERN_HINT_RE.search(pattern):
        return "forbidden_or_needs_review", "pattern contains fixture/batch/probe vocabulary"
    if any(hint in joined for hint in ALLOWED_SYNTAX_HINTS):
        return "allowed_syntax", "appears to validate syntax, identifiers, schema, predicates, or clauses"
    if _looks_like_structural_pattern(pattern):
        return "allowed_structural", "appears to extract quoted spans, tokens, casing, or other source/query structure"
    if SEMANTIC_PATTERN_HINT_RE.search(pattern):
        if "utterance" in subject.casefold() or "question" in subject.casefold():
            return "semantic_trigger", "English-looking alternation inspects raw utterance/question text"
        if file.startswith("scripts\\run_domain_bootstrap_qa.py") or file.startswith("scripts/run_domain_bootstrap_qa.py"):
            return "semantic_trigger", "English-looking alternation controls a QA/source-record route"
        return "legacy_tolerated", "English-looking trigger outside the main QA hotspot; review before changing"
    if "utterance" in subject.casefold() or "question" in subject.casefold():
        return "semantic_trigger", "regex subject is raw utterance/question text"
    return "legacy_tolerated", "query-adjacent regex that needs manual classification"


def _looks_like_structural_pattern(pattern: str) -> bool:
    if not pattern:
        return False
    if any(hint in pattern for hint in STRUCTURAL_PATTERN_HINTS):
        if not SEMANTIC_PATTERN_HINT_RE.search(pattern):
            return True
    if re.search(r"\\b[A-Z]\]", pattern) or re.search(r"\[\^", pattern):
        return True
    return False


def _iter_files(paths: tuple[Path, ...]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        path = raw if raw.is_absolute() else REPO_ROOT / raw
        if path.is_file() and path.suffix == ".py":
            out.append(path)
        elif path.is_dir():
            out.extend(sorted(item for item in path.rglob("*.py") if _is_active_path(item)))
    return sorted(set(out))


def _is_active_path(path: Path) -> bool:
    parts = {part.casefold() for part in path.parts}
    return not ({"tests", "docs", "datasets", "tmp", "__pycache__"} & parts)


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "# Utterance Regex Governance Audit",
        "",
        f"- Schema: `{report.get('schema_version')}`",
        f"- Status: `{summary.get('status')}`",
        f"- Files scanned: `{summary.get('file_count')}`",
        f"- Regex hits: `{summary.get('regex_hit_count')}`",
        f"- Parse errors: `{summary.get('parse_error_count')}`",
        "",
        "## Category Counts",
        "",
        "| Category | Count |",
        "| --- | ---: |",
    ]
    for category, count in (summary.get("category_counts") or {}).items():
        lines.append(f"| `{category}` | {count} |")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| File | Line | Function | Category | Pattern | Rationale |",
            "| --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for row in report.get("rows", []):
        lines.append(
            "| `{file}` | {line} | `{function}` | `{category}` | `{pattern}` | {rationale} |".format(
                file=row.get("file", ""),
                line=row.get("line", ""),
                function=row.get("function", ""),
                category=row.get("category", ""),
                pattern=_md_cell(str(row.get("pattern", ""))[:120]),
                rationale=_md_cell(str(row.get("rationale", ""))),
            )
        )
    if report.get("rows_truncated"):
        lines.extend(["", "_Rows truncated by `--max-rows`._"])
    if report.get("parse_errors"):
        lines.extend(["", "## Parse Errors", ""])
        for error in report.get("parse_errors", []):
            lines.append(f"- `{error.get('file')}` line {error.get('line')}: {error.get('error')}")
    return "\n".join(lines).rstrip() + "\n"


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Block resurrection of contaminated historical score claims in public docs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOTS = [Path("README.md"), Path("PROJECT_STATE.md"), Path("docs")]
SKIP_DOC_PATTERNS = ["*WORKSHEET*.md"]
SCORE_PATTERN = re.compile(
    r"(?<![\d.])("
    r"80\.5%|91\.12%|91\.25%|92\.33%|95%|95\.2%|98\.5%|99%|90%\+|90\+"
    r")(?![\d.])",
    re.IGNORECASE,
)
DISCLAIMER_PATTERN = re.compile(
    r"("
    r"not\s+current|historical|contaminated|does\s+not\s+support|do\s+not\s+claim|"
    r"not\s+a\s+claim|not\s+claim-bearing|not\s+current\s+public|not\s+current\s+accuracy|"
    r"not\s+evidence|non-claims|what\s+this\s+does\s+not\s+support|old\s+high-score"
    r")",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--doc", action="append", default=[], type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    docs = args.doc or _default_docs(args.root)
    report = audit_docs(root=args.root, docs=docs)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(_report_md(report), encoding="utf-8")
    blocked = report["summary"]["status"] != "pass"
    return 0 if args.exit_zero or not blocked else 1


def audit_docs(*, root: Path, docs: list[Path]) -> dict[str, Any]:
    occurrences: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    skipped_docs: list[str] = []
    for doc in docs:
        path = doc if doc.is_absolute() else root / doc
        if not path.exists():
            skipped_docs.append(str(doc))
            continue
        text = path.read_text(encoding="utf-8")
        for match in SCORE_PATTERN.finditer(text):
            context = _context(text, match.start(), match.end())
            item = {
                "doc": str(doc),
                "score": match.group(1),
                "line": _line_number(text, match.start()),
                "context": context.strip(),
                "disclaimed": bool(DISCLAIMER_PATTERN.search(context)),
            }
            occurrences.append(item)
            if not item["disclaimed"]:
                blockers.append(item)
    return {
        "schema": "prethinker.historical_score_claim_audit.v1",
        "summary": {
            "occurrence_count": len(occurrences),
            "blocking_occurrence_count": len(blockers),
            "skipped_doc_count": len(skipped_docs),
            "status": "pass" if not blockers and not skipped_docs else "fail",
        },
        "occurrences": occurrences,
        "blocking_occurrences": blockers,
        "skipped_docs": skipped_docs,
    }


def _default_docs(root: Path) -> list[Path]:
    docs: list[Path] = []
    for item in DEFAULT_ROOTS:
        path = root / item
        if path.is_file():
            docs.append(item)
        elif path.is_dir():
            docs.extend(
                path.relative_to(root)
                for path in sorted(path.glob("*.md"))
                if not _skip_doc(path)
            )
    return docs


def _skip_doc(path: Path) -> bool:
    return any(path.match(pattern) for pattern in SKIP_DOC_PATTERNS)


def _context(text: str, start: int, end: int) -> str:
    line_starts = [0]
    for match in re.finditer(r"\n", text):
        line_starts.append(match.end())
    line_index = 0
    for index, line_start in enumerate(line_starts):
        if line_start > start:
            break
        line_index = index
    min_line = max(0, line_index - 5)
    max_line = min(len(line_starts) - 1, line_index + 5)
    context_start = line_starts[min_line]
    if max_line + 1 < len(line_starts):
        context_end = line_starts[max_line + 1]
    else:
        context_end = len(text)
    return text[context_start:context_end]


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _report_md(report: dict[str, Any]) -> str:
    lines = [
        "# Historical Score Claim Audit",
        "",
        f"Status: `{report['summary']['status']}`",
        f"Occurrences: `{report['summary']['occurrence_count']}`",
        f"Blocking occurrences: `{report['summary']['blocking_occurrence_count']}`",
        f"Skipped docs: `{report['summary']['skipped_doc_count']}`",
        "",
    ]
    if report["blocking_occurrences"]:
        lines.append("## Blocking Occurrences")
        lines.append("")
        for item in report["blocking_occurrences"]:
            lines.append(f"- `{item['doc']}:{item['line']}` contains `{item['score']}` without nearby disclaimer language")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())

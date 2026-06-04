#!/usr/bin/env python3
"""Check current research docs for missing local artifact handles.

This audit intentionally scans inline code spans, not fenced command/log blocks.
Fenced blocks often contain examples or historical transcript snippets. Inline
artifact handles in the current evidence docs are stronger claims: if they name
a local `tmp/`, `datasets/`, or archive path, that path should exist.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCS = [
    Path("README.md"),
    Path("PROJECT_STATE.md"),
    Path("docs/CURRENT_RESEARCH_HEADLINE.md"),
    Path("docs/ACTIVE_RESEARCH_LANES.md"),
    Path("docs/CLOSED_DOMAIN_PREDICATE_PACKS_TECHNICAL_NOTE.md"),
    Path("docs/DOMAIN_PACK_RESEARCH_EVIDENCE.md"),
    Path("docs/PUBLIC_DOCS_GUIDE.md"),
]


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
    docs = args.doc or DEFAULT_DOCS
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
    checked: list[dict[str, str]] = []
    missing: list[dict[str, str]] = []
    skipped_docs: list[str] = []
    for doc in docs:
        path = doc if doc.is_absolute() else root / doc
        if not path.exists():
            skipped_docs.append(str(doc))
            continue
        text = _strip_fenced_code(path.read_text(encoding="utf-8"))
        for candidate in _candidate_paths(text):
            resolved = _resolve_candidate(root=root, candidate=candidate)
            item = {
                "doc": str(doc),
                "path": candidate,
                "resolved_path": str(resolved),
            }
            checked.append(item)
            if not resolved.exists():
                missing.append(item)
    return {
        "schema": "prethinker.research_artifact_path_audit.v1",
        "summary": {
            "checked_count": len(checked),
            "missing_count": len(missing),
            "skipped_doc_count": len(skipped_docs),
            "status": "pass" if not missing and not skipped_docs else "fail",
        },
        "checked": checked,
        "missing": missing,
        "skipped_docs": skipped_docs,
    }


def _candidate_paths(markdown_without_fences: str) -> list[str]:
    candidates: list[str] = []
    for match in re.finditer(r"`([^`\n]+)`", markdown_without_fences):
        value = match.group(1).strip()
        if not _looks_like_local_artifact_path(value):
            continue
        if _is_example_or_glob(value):
            continue
        candidates.append(value)
    return candidates


def _strip_fenced_code(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def _looks_like_local_artifact_path(value: str) -> bool:
    normalized = value.replace("\\", "/")
    return (
        normalized.startswith("tmp/")
        or normalized.startswith("datasets/")
        or value.startswith("C:\\prethinker_tmp_archive\\")
    )


def _is_example_or_glob(value: str) -> bool:
    normalized = value.replace("\\", "/")
    if any(token in normalized for token in ["*", "...", "path/to", "fixture_id", "bundle_root"]):
        return True
    if normalized in {"tmp/", "datasets/", "C:/prethinker_tmp_archive"}:
        return True
    if normalized.startswith("tmp/judged_qa_probe") or normalized.startswith("tmp/compile_fact_qa_manifest_run"):
        return True
    if normalized.startswith("tmp/licensed/") or normalized.startswith("tmp/package_smoke"):
        return True
    return False


def _resolve_candidate(*, root: Path, candidate: str) -> Path:
    if re.match(r"^[A-Za-z]:\\", candidate):
        return Path(candidate)
    return root / candidate


def _report_md(report: dict[str, Any]) -> str:
    lines = [
        "# Research Artifact Path Audit",
        "",
        f"Status: `{report['summary']['status']}`",
        f"Checked: `{report['summary']['checked_count']}`",
        f"Missing: `{report['summary']['missing_count']}`",
        f"Skipped docs: `{report['summary']['skipped_doc_count']}`",
        "",
    ]
    if report["missing"]:
        lines.append("## Missing")
        lines.append("")
        for item in report["missing"]:
            lines.append(f"- `{item['doc']}` -> `{item['path']}`")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())

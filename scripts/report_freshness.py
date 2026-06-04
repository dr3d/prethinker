"""Shared freshness checks for generated markdown reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def apply_markdown_freshness_check(
    *,
    report: dict[str, Any],
    expected_path: Path,
    rendered_md: str,
    blocking_key: str = "blocking_reasons",
) -> None:
    expected_text = _read_optional_text(expected_path)
    reason = ""
    if expected_text is None:
        reason = f"expected_markdown_missing:{expected_path}"
    elif normalize_markdown(expected_text) != normalize_markdown(rendered_md):
        reason = f"expected_markdown_stale:{expected_path}"
    if not reason:
        return

    summary = report.setdefault("summary", {})
    blockers = summary.setdefault(blocking_key, [])
    blockers.append(reason)
    summary["status"] = "fail"


def normalize_markdown(text: str) -> str:
    return text.replace("\r\n", "\n").rstrip() + "\n"


def _read_optional_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None

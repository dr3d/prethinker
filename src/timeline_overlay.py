"""Deterministic timeline overlay.

The overlay orders explicitly supplied event rows and reports chronology
warnings. It does not call an LLM, read source text, or write KB state.
"""

from __future__ import annotations

from datetime import date
import re
from typing import Any


DATE_RE = re.compile(r"^(?P<year>\d{4})(?:-(?P<month>\d{2})(?:-(?P<day>\d{2}))?)?$")


def analyze_timeline_overlay(payload: dict[str, Any]) -> dict[str, Any]:
    events = _indexed_events(payload.get("events", []))
    warnings: list[dict[str, Any]] = []
    rows = []
    for index, event in enumerate(events):
        parsed = _parse_date(event.get("date"))
        if parsed["warning"]:
            warnings.append({"kind": parsed["warning"], "event_id": event["id"], "value": event.get("date", "")})
        rows.append(
            {
                **event,
                "source_index": index,
                "date_key": parsed["date_key"],
                "date_precision": parsed["precision"],
                "sortable": bool(parsed["date_key"]),
            }
        )

    dated = [row for row in rows if row["sortable"]]
    undated = [row for row in rows if not row["sortable"]]
    dated.sort(key=lambda row: (row["date_key"], row["source_index"]))
    same_date_groups = _same_date_groups(dated)
    gaps = _date_gaps(dated)
    return {
        "schema_version": "timeline_overlay_report_v1",
        "event_count": len(rows),
        "dated_event_count": len(dated),
        "undated_event_count": len(undated),
        "warnings": warnings,
        "ordered_events": [_public_event(row) for row in dated],
        "undated_events": [_public_event(row) for row in undated],
        "same_date_groups": same_date_groups,
        "date_gaps": gaps,
    }


def _indexed_events(items: Any) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        raise ValueError("events must be a list")
    out = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError("events entries must be objects")
        event_id = str(item.get("id") or "").strip()
        if not event_id:
            raise ValueError("events entries require id")
        if event_id in seen:
            raise ValueError(f"events contains duplicate id: {event_id}")
        seen.add(event_id)
        out.append(
            {
                "id": event_id,
                "label": str(item.get("label") or event_id).strip(),
                "date": str(item.get("date") or "").strip(),
                "source_coords": str(item.get("source_coords") or "").strip(),
                "text_anchor": str(item.get("text_anchor") or "").strip(),
                "event_type": str(item.get("event_type") or "").strip(),
                "confidence": str(item.get("confidence") or "").strip(),
                "input_order": index,
            }
        )
    return out


def _parse_date(value: Any) -> dict[str, Any]:
    text = str(value or "").strip()
    if not text:
        return {"date_key": "", "precision": "", "warning": "missing_event_date"}
    match = DATE_RE.match(text)
    if not match:
        return {"date_key": "", "precision": "", "warning": "invalid_event_date"}
    year = int(match.group("year"))
    month_text = match.group("month")
    day_text = match.group("day")
    if not month_text:
        return {"date_key": f"{year:04d}-01-01", "precision": "year", "warning": ""}
    month = int(month_text)
    if not day_text:
        try:
            date(year, month, 1)
        except ValueError:
            return {"date_key": "", "precision": "", "warning": "invalid_event_date"}
        return {"date_key": f"{year:04d}-{month:02d}-01", "precision": "month", "warning": ""}
    day = int(day_text)
    try:
        date(year, month, day)
    except ValueError:
        return {"date_key": "", "precision": "", "warning": "invalid_event_date"}
    return {"date_key": f"{year:04d}-{month:02d}-{day:02d}", "precision": "day", "warning": ""}


def _public_event(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "label": row["label"],
        "date": row["date"],
        "date_key": row["date_key"],
        "date_precision": row["date_precision"],
        "event_type": row["event_type"],
        "source_coords": row["source_coords"],
        "text_anchor": row["text_anchor"],
        "confidence": row["confidence"],
        "input_order": row["input_order"],
    }


def _same_date_groups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = {}
    for row in rows:
        groups.setdefault(str(row["date_key"]), []).append(str(row["id"]))
    return [
        {"date_key": key, "event_ids": ids}
        for key, ids in sorted(groups.items())
        if len(ids) > 1
    ]


def _date_gaps(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gaps = []
    for left, right in zip(rows, rows[1:]):
        left_date = date.fromisoformat(left["date_key"])
        right_date = date.fromisoformat(right["date_key"])
        days = (right_date - left_date).days
        if days > 30:
            gaps.append(
                {
                    "from_event_id": left["id"],
                    "to_event_id": right["id"],
                    "from_date_key": left["date_key"],
                    "to_date_key": right["date_key"],
                    "gap_days": days,
                }
            )
    return gaps

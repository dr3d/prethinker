import pytest

from scripts.run_timeline_overlay import build_report, render_markdown
from src.timeline_overlay import analyze_timeline_overlay


def test_timeline_overlay_orders_events_and_reports_gaps() -> None:
    report = analyze_timeline_overlay(
        {
            "events": [
                {"id": "e_late", "label": "Late", "date": "2026-04-10"},
                {"id": "e_early", "label": "Early", "date": "2026-01-01"},
                {"id": "e_month", "label": "Month precision", "date": "2026-03"},
            ]
        }
    )

    assert [row["id"] for row in report["ordered_events"]] == ["e_early", "e_month", "e_late"]
    assert report["ordered_events"][1]["date_precision"] == "month"
    assert report["date_gaps"] == [
        {
            "from_event_id": "e_early",
            "to_event_id": "e_month",
            "from_date_key": "2026-01-01",
            "to_date_key": "2026-03-01",
            "gap_days": 59,
        },
        {
            "from_event_id": "e_month",
            "to_event_id": "e_late",
            "from_date_key": "2026-03-01",
            "to_date_key": "2026-04-10",
            "gap_days": 40,
        },
    ]


def test_timeline_overlay_flags_missing_invalid_and_same_date() -> None:
    report = analyze_timeline_overlay(
        {
            "events": [
                {"id": "e1", "date": "2026-02-30"},
                {"id": "e2", "date": ""},
                {"id": "e3", "date": "2026-05-01"},
                {"id": "e4", "date": "2026-05-01"},
            ]
        }
    )

    assert report["dated_event_count"] == 2
    assert report["undated_event_count"] == 2
    assert report["warnings"] == [
        {"kind": "invalid_event_date", "event_id": "e1", "value": "2026-02-30"},
        {"kind": "missing_event_date", "event_id": "e2", "value": ""},
    ]
    assert report["same_date_groups"] == [{"date_key": "2026-05-01", "event_ids": ["e3", "e4"]}]


def test_timeline_overlay_rejects_duplicate_event_ids() -> None:
    with pytest.raises(ValueError, match="duplicate id"):
        analyze_timeline_overlay({"events": [{"id": "e1"}, {"id": "e1"}]})


def test_timeline_runner_wraps_report() -> None:
    report = build_report(
        payload={
            "id": "demo",
            "events": [{"id": "e1", "label": "One", "date": "2026", "source_coords": "[1]"}],
        }
    )

    assert report["schema_version"] == "timeline_overlay_run_v1"
    assert report["summary"]["event_count"] == 1
    assert report["summary"]["dated_event_count"] == 1
    assert report["timeline_report"]["ordered_events"][0]["date_precision"] == "year"
    assert "# Timeline Overlay Report" in render_markdown(report)

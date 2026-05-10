from scripts.audit_helper_classes import render_markdown, rollup, summarize_rows


def test_helper_class_audit_rollup_counts_clean_candidate_and_unlabeled_rows() -> None:
    rows = [
        {"SupportKind": "raw_event_count", "HelperClass": "clean-helper"},
        {"SupportKind": "sensor_vendor_model", "HelperClass": "candidate-helper"},
        {"SupportKind": "legacy_row"},
    ]

    summary = summarize_rows(rows)

    assert summary["row_count"] == 3
    assert summary["helper_class_counts"] == {
        "candidate-helper": 1,
        "clean-helper": 1,
        "unlabeled": 1,
    }
    assert summary["support_kind_counts"]["raw_event_count"] == 1


def test_helper_class_audit_markdown_renders_rollup_table() -> None:
    entries = [
        {
            "fixture": "demo_fixture",
            "companions": {
                "industrial_sensor_support": {
                    "available": True,
                    "row_count": 2,
                    "helper_class_counts": {"clean-helper": 1, "candidate-helper": 1},
                }
            },
        }
    ]
    payload = {
        "generated_at": "2026-05-10T00:00:00+00:00",
        "entries": entries,
        "rollup": rollup(entries),
    }

    markdown = render_markdown(payload)

    assert "| industrial_sensor_support | 2 | 1 | 1 | 0 |" in markdown
    assert "### demo_fixture" in markdown

from scripts.compare_selector_runs import build_report, render_markdown


def _run(label: str, verdicts: dict[str, str]) -> dict:
    return {
        "label": label,
        "path": f"{label}.json",
        "selection_policy": label,
        "summary": {
            "selected_best_count": 1,
            "selected_exact": sum(1 for verdict in verdicts.values() if verdict == "exact"),
            "selected_partial": sum(1 for verdict in verdicts.values() if verdict == "partial"),
            "selected_miss": sum(1 for verdict in verdicts.values() if verdict == "miss"),
            "selector_error_count": 0,
        },
        "rows": [
            {
                "id": row_id,
                "question": f"Question {row_id}?",
                "selected_verdict": verdict,
            }
            for row_id, verdict in verdicts.items()
        ],
    }


def _group_run(label: str, group_name: str, verdicts: dict[str, str]) -> dict:
    run = _run(label, verdicts)
    run["group_name"] = group_name
    return run


def test_selector_run_comparison_marks_volatile_rows() -> None:
    report = build_report(
        runs=[
            _run("direct", {"q1": "partial", "q2": "exact"}),
            _run("selfcheck", {"q1": "exact", "q2": "exact"}),
        ],
        label="toy",
    )

    rows = {row["id"]: row for row in report["rows"]}

    assert report["aggregate"]["volatile_row_count"] == 1
    assert report["aggregate"]["best_selector_counts"]["exact"] == 2
    assert rows["q1"]["best_selector_labels"] == ["selfcheck"]


def test_selector_run_comparison_prefixes_group_row_ids() -> None:
    report = build_report(
        runs=[
            _group_run("lark_structural", "lark", {"q007": "miss"}),
            _group_run("north_structural", "north", {"q007": "exact"}),
        ],
        label="toy",
    )

    rows = {row["id"]: row for row in report["rows"]}

    assert set(rows) == {"lark:q007", "north:q007"}
    assert report["aggregate"]["row_count"] == 2


def test_selector_run_comparison_can_align_by_bare_row_id() -> None:
    report = build_report(
        runs=[
            _group_run("policy_a", "fixture_a", {"q007": "miss"}),
            _group_run("policy_b", "fixture_b", {"q007": "exact"}),
        ],
        label="toy",
        row_scope="id",
    )

    rows = {row["id"]: row for row in report["rows"]}

    assert set(rows) == {"q007"}
    assert rows["q007"]["volatile"] is True


def test_selector_run_comparison_rolls_up_policy_totals() -> None:
    direct = _run("direct_a", {"q1": "partial"})
    direct["selection_policy"] = "direct"
    direct["summary"]["row_count"] = 1
    direct["summary"]["selected_best_count"] = 1
    selfcheck = _run("direct_b", {"q2": "exact"})
    selfcheck["selection_policy"] = "direct"
    selfcheck["summary"]["row_count"] = 1
    selfcheck["summary"]["selected_best_count"] = 1

    report = build_report(runs=[direct, selfcheck], label="toy")

    assert report["aggregate"]["policy_count"] == 1
    assert report["policy_summaries"][0]["selection_policy"] == "direct"
    assert report["policy_summaries"][0]["selected_best_count"] == 2


def test_selector_run_comparison_markdown_names_policy() -> None:
    report = build_report(runs=[_run("direct", {"q1": "exact"})], label="toy")

    markdown = render_markdown(report)

    assert "# Selector Policy Comparison" in markdown
    assert "does not read source prose" in markdown
    assert "Row scope" in markdown
    assert "## Policy Totals" in markdown
    assert "| `direct` |" in markdown

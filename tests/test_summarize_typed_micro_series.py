import json
from pathlib import Path

from scripts.summarize_typed_micro_series import build_report, render_markdown


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _compile(path: Path, facts: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"source_compile": {"facts": facts}}, indent=2), encoding="utf-8")
    return path


def test_typed_micro_series_counts_support_across_runs(tmp_path: Path) -> None:
    root = tmp_path / "micro"
    fixture = root / "demo_fixture"
    _write(
        fixture / "expected_facts.pl",
        "\n".join(
            [
                "demo_fact(A, alpha).",
                "demo_fact(A, beta).",
                "demo_fact(A, gamma).",
            ]
        ),
    )
    run1 = _compile(
        tmp_path / "run1" / "compile.json",
        ["demo_fact(item_1, alpha).", "demo_fact(item_1, beta)."],
    )
    run2 = _compile(
        tmp_path / "run2" / "compile.json",
        ["demo_fact(item_1, alpha).", "demo_fact(item_1, gamma)."],
    )

    report = build_report(
        fixture_id="demo_fixture",
        root=root,
        compile_paths=[run1, run2],
        support_threshold=2,
    )

    assert report["summary"]["compile_count"] == 2
    assert report["summary"]["supported_fact_count"] == 1
    rows = {row["expected_fact"]: row for row in report["rows"]}
    assert rows["demo_fact(A, alpha)."]["support_count"] == 2
    assert rows["demo_fact(A, alpha)."]["meets_threshold"] is True
    assert rows["demo_fact(A, beta)."]["support_count"] == 1
    assert rows["demo_fact(A, gamma)."]["support_count"] == 1


def test_typed_micro_series_reports_same_predicate_variants_for_unsupported_rows(tmp_path: Path) -> None:
    root = tmp_path / "micro"
    fixture = root / "demo_fixture"
    _write(
        fixture / "expected_facts.pl",
        "\n".join(
            [
                "demo_fact(A, alpha, expected_value).",
                "other_fact(A, alpha).",
            ]
        ),
    )
    run1 = _compile(
        tmp_path / "run1" / "compile.json",
        [
            "demo_fact(item_1, alpha, nearby_value).",
            "other_fact(item_1, alpha).",
        ],
    )
    run2 = _compile(
        tmp_path / "run2" / "compile.json",
        [
            "demo_fact(item_2, alpha, nearby_value).",
            "other_fact(item_1, alpha).",
        ],
    )

    report = build_report(
        fixture_id="demo_fixture",
        root=root,
        compile_paths=[run1, run2],
        support_threshold=2,
    )

    rows = {row["expected_fact"]: row for row in report["rows"]}
    variants = rows["demo_fact(A, alpha, expected_value)."]["same_predicate_variants"]
    assert variants == [
        {"fact": "demo_fact(item_1, alpha, nearby_value).", "runs": ["run1"], "run_count": 1},
        {"fact": "demo_fact(item_2, alpha, nearby_value).", "runs": ["run2"], "run_count": 1},
    ]
    assert "Unsupported Same-Predicate Variants" in render_markdown(report)

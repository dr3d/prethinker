import json
from pathlib import Path

from scripts.summarize_typed_micro_series import build_report, main, render_markdown


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


def test_typed_micro_series_constant_slot_matcher_floats_ids(tmp_path: Path) -> None:
    root = tmp_path / "micro"
    fixture = root / "demo_fixture"
    _write(
        fixture / "expected_facts.pl",
        "\n".join(
            [
                "demo_fact(Entity, alpha, Src).",
                "demo_fact(Entity, beta, Src).",
            ]
        ),
    )
    run1 = _compile(
        tmp_path / "run1" / "compile.json",
        ["demo_fact(item_1, alpha, source_a).", "demo_fact(item_2, beta, source_b)."],
    )

    unification_report = build_report(
        fixture_id="demo_fixture",
        root=root,
        compile_paths=[run1],
        support_threshold=1,
    )
    constant_slot_report = build_report(
        fixture_id="demo_fixture",
        root=root,
        compile_paths=[run1],
        support_threshold=1,
        matcher="constant_slot",
    )

    assert unification_report["summary"]["supported_fact_count"] == 1
    assert constant_slot_report["summary"]["supported_fact_count"] == 2
    assert constant_slot_report["matcher"] == "constant_slot"


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


def test_typed_micro_series_can_apply_domain_reducers_before_support(tmp_path: Path) -> None:
    root = tmp_path / "micro"
    fixture = root / "fda_fixture"
    _write(
        fixture / "expected_facts.pl",
        "\n".join(
            [
                "fda_violation(Violation, Letter, violation_1, quality_unit_failure, Src).",
            ]
        ),
    )
    run1 = _compile(
        tmp_path / "run1" / "compile.json",
        ["fda_violation(violation_1, letter_1, 1, quality_unit_failure, src_line_1)."],
    )
    run2 = _compile(
        tmp_path / "run2" / "compile.json",
        ["fda_violation(violation_2, letter_1, 2, contamination_control, src_line_2)."],
    )

    without_reducers = build_report(
        fixture_id="fda_fixture",
        root=root,
        compile_paths=[run1, run2],
        support_threshold=1,
    )
    with_reducers = build_report(
        fixture_id="fda_fixture",
        root=root,
        compile_paths=[run1, run2],
        support_threshold=1,
        apply_domain_reducers=True,
    )

    expected = "fda_violation(Violation, Letter, violation_1, quality_unit_failure, Src)."
    without_rows = {row["expected_fact"]: row for row in without_reducers["rows"]}
    with_rows = {row["expected_fact"]: row for row in with_reducers["rows"]}
    assert without_rows[expected]["support_count"] == 0
    assert with_rows[expected]["support_count"] == 1
    assert with_reducers["domain_reducers_applied"] is True


def test_typed_micro_series_reports_supported_forbidden_facts(tmp_path: Path) -> None:
    root = tmp_path / "micro"
    fixture = root / "demo_fixture"
    _write(
        fixture / "expected_facts.pl",
        "\n".join(
            [
                "demo_fact(Entity, allowed_value, Src).",
            ]
        ),
    )
    _write(
        fixture / "forbidden_facts.pl",
        "\n".join(
            [
                "demo_fact(Entity, prose_shaped_value, Src).",
            ]
        ),
    )
    run1 = _compile(
        tmp_path / "run1" / "compile.json",
        [
            "demo_fact(row_1, allowed_value, source_1).",
            "demo_fact(row_1, prose_shaped_value, source_1).",
        ],
    )

    report = build_report(
        fixture_id="demo_fixture",
        root=root,
        compile_paths=[run1],
        support_threshold=1,
        matcher="constant_slot",
    )

    assert report["summary"]["supported_fact_count"] == 1
    assert report["summary"]["forbidden_fact_count"] == 1
    assert report["summary"]["supported_forbidden_fact_count"] == 1
    assert report["forbidden_rows"] == [
        {
            "forbidden_fact": "demo_fact(Entity, prose_shaped_value, Src).",
            "support_count": 1,
            "support_runs": ["run1"],
            "supported": True,
        }
    ]
    assert "Supported Forbidden Facts" in render_markdown(report)


def test_typed_micro_series_cli_enforce_no_forbidden_bites(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "micro"
    fixture = root / "demo_fixture"
    _write(fixture / "expected_facts.pl", "demo_fact(Entity, allowed_value, Src).\n")
    _write(fixture / "forbidden_facts.pl", "demo_fact(Entity, prose_shaped_value, Src).\n")
    run1 = _compile(
        tmp_path / "run1" / "compile.json",
        [
            "demo_fact(row_1, allowed_value, source_1).",
            "demo_fact(row_1, prose_shaped_value, source_1).",
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "summarize_typed_micro_series.py",
            "--fixture",
            "demo_fixture",
            "--root",
            str(root),
            "--compile-json",
            str(run1),
            "--support-threshold",
            "1",
            "--matcher",
            "constant_slot",
            "--enforce-supported",
            "--enforce-no-forbidden",
        ],
    )

    assert main() == 1

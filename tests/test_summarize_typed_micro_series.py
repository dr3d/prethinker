import json
from pathlib import Path

from scripts.summarize_typed_micro_series import build_report, main, render_markdown


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _compile(
    path: Path,
    facts: list[str],
    *,
    mode: str | None = None,
    union_source_compile: dict | None = None,
    active_profile_registry_lens: dict | None = None,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"source_compile": {"facts": facts}}
    if mode is not None:
        payload["mode"] = mode
    if union_source_compile is not None:
        payload["union_source_compile"] = union_source_compile
    if active_profile_registry_lens is not None:
        payload["active_profile_registry_lens"] = active_profile_registry_lens
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
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


def test_typed_micro_series_reducers_do_not_prune_deterministic_union_with_stale_lens_metadata(
    tmp_path: Path,
) -> None:
    root = tmp_path / "micro"
    fixture = root / "fda_fixture"
    _write(
        fixture / "expected_facts.pl",
        "\n".join(
            [
                "fda_warning_letter(Letter, cder, firm_1, v_2025_01_02, Src).",
                "fda_violation(Violation, Letter, violation_1, quality_unit_failure, Src).",
            ]
        ),
    )
    run1 = _compile(
        tmp_path / "run1_all_lenses_union" / "compile.json",
        [
            "fda_warning_letter(wl_1, cder, firm_1, v_2025_01_02, src_line_1).",
            "fda_violation(violation_1, wl_1, violation_1, quality_unit_failure, src_line_2).",
        ],
        mode="deterministic_compile_union",
        union_source_compile={"source_runs": ["wrapper.json", "violation.json"]},
        active_profile_registry_lens={
            "id": "wrapper",
            "allowed_signatures": ["fda_warning_letter/5"],
        },
    )

    report = build_report(
        fixture_id="fda_fixture",
        root=root,
        compile_paths=[run1],
        support_threshold=1,
        matcher="constant_slot",
        apply_domain_reducers=True,
    )

    rows = {row["expected_fact"]: row for row in report["rows"]}
    assert rows["fda_warning_letter(Letter, cder, firm_1, v_2025_01_02, Src)."]["support_count"] == 1
    assert rows["fda_violation(Violation, Letter, violation_1, quality_unit_failure, Src)."]["support_count"] == 1
    reducer_report = report["runs"][0]["domain_reducer_reports"]["active_lens_scope_integrity"]
    assert reducer_report["dropped_count"] == 0


def test_typed_micro_series_domain_reducers_include_ntsb_actor_ids(tmp_path: Path) -> None:
    root = tmp_path / "micro"
    fixture = root / "ntsb_fixture"
    expected = (
        "ntsb_safety_action(Action, Occurrence, org_teutopolis_fire_dept, "
        "hazmat_training, not_stated, Src)."
    )
    _write(fixture / "expected_facts.pl", expected)
    run1 = _compile(
        tmp_path / "run1" / "compile.json",
        ["ntsb_safety_action(action_1, occurrence_1, org_teutopolis_fd, hazmat_training, not_stated, src_line_1)."],
    )
    run2 = _compile(
        tmp_path / "run2" / "compile.json",
        ["ntsb_safety_action(action_2, occurrence_1, org_teutopolis_fire, hazmat_training, not_stated, src_line_2)."],
    )

    without_reducers = build_report(
        fixture_id="ntsb_fixture",
        root=root,
        compile_paths=[run1, run2],
        support_threshold=2,
        matcher="constant_slot",
    )
    with_reducers = build_report(
        fixture_id="ntsb_fixture",
        root=root,
        compile_paths=[run1, run2],
        support_threshold=2,
        matcher="constant_slot",
        apply_domain_reducers=True,
    )

    without_rows = {row["expected_fact"]: row for row in without_reducers["rows"]}
    with_rows = {row["expected_fact"]: row for row in with_reducers["rows"]}
    assert without_rows[expected]["support_count"] == 0
    assert with_rows[expected]["support_count"] == 2
    assert with_rows[expected]["meets_threshold"] is True
    reducer_reports = [run["domain_reducer_reports"] for run in with_reducers["runs"]]
    assert all(report["ntsb_actor_id_atom_reduction"]["reduction_count"] == 1 for report in reducer_reports)


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


def test_typed_micro_series_reports_unexpected_same_signature_facts(tmp_path: Path) -> None:
    root = tmp_path / "micro"
    fixture = root / "demo_fixture"
    _write(fixture / "expected_facts.pl", "demo_fact(Entity, allowed_value, Src).\n")
    _write(fixture / "forbidden_facts.pl", "demo_fact(Entity, forbidden_value, Src).\n")
    run1 = _compile(
        tmp_path / "run1" / "compile.json",
        [
            "demo_fact(row_1, allowed_value, source_1).",
            "demo_fact(row_2, unexpected_value, source_2).",
            "demo_fact(row_3, forbidden_value, source_3).",
            "other_fact(row_4, unexpected_value, source_4).",
        ],
    )

    report = build_report(
        fixture_id="demo_fixture",
        root=root,
        compile_paths=[run1],
        support_threshold=1,
        matcher="constant_slot",
        expected_signatures={"demo_fact/3"},
        report_unexpected=True,
    )

    assert report["summary"]["unexpected_fact_count"] == 1
    assert report["unexpected_rows"] == [
        {
            "fact": "demo_fact(row_2, unexpected_value, source_2).",
            "support_count": 1,
            "support_runs": ["run1"],
        }
    ]
    rendered = render_markdown(report)
    assert "Unexpected Same-Signature Facts" in rendered
    assert "other_fact" not in rendered


def test_typed_micro_series_can_filter_expected_facts_by_signature(tmp_path: Path) -> None:
    root = tmp_path / "micro"
    fixture = root / "demo_fixture"
    _write(
        fixture / "expected_facts.pl",
        "\n".join(
            [
                "kept_fact(Entity, alpha, Src).",
                "dropped_fact(Entity, beta, Src).",
            ]
        ),
    )
    _write(
        fixture / "forbidden_facts.pl",
        "\n".join(
            [
                "kept_fact(Entity, forbidden_alpha, Src).",
                "dropped_fact(Entity, forbidden_beta, Src).",
            ]
        ),
    )
    run1 = _compile(
        tmp_path / "run1" / "compile.json",
        [
            "kept_fact(row_1, alpha, source_1).",
            "dropped_fact(row_1, beta, source_1).",
            "kept_fact(row_1, forbidden_alpha, source_1).",
            "dropped_fact(row_1, forbidden_beta, source_1).",
        ],
    )

    report = build_report(
        fixture_id="demo_fixture",
        root=root,
        compile_paths=[run1],
        support_threshold=1,
        matcher="constant_slot",
        expected_signatures={"kept_fact/3"},
    )

    assert report["expected_signature_filter"] == ["kept_fact/3"]
    assert report["summary"]["expected_fact_count"] == 1
    assert report["summary"]["supported_fact_count"] == 1
    assert report["summary"]["forbidden_fact_count"] == 1
    assert report["summary"]["supported_forbidden_fact_count"] == 1
    assert report["rows"][0]["expected_fact"] == "kept_fact(Entity, alpha, Src)."
    assert report["forbidden_rows"][0]["forbidden_fact"] == "kept_fact(Entity, forbidden_alpha, Src)."
    assert "Expected signature filter: `kept_fact/3`" in render_markdown(report)


def test_typed_micro_series_filters_domain_omissions_to_offered_carriers(tmp_path: Path) -> None:
    root = tmp_path / "micro"
    fixture = root / "demo_fixture"
    _write(
        fixture / "expected_facts.pl",
        "\n".join(
            [
                "chronology_fact(Entity, alpha, Src).",
                "domain_omission(Entity, 'chronology_fact/3', none_found, no_chronology, Src).",
                "domain_omission(Entity, 'wrapper_fact/3', none_found, no_wrapper, Src).",
            ]
        ),
    )
    run1 = _compile(
        tmp_path / "run1" / "compile.json",
        [
            "chronology_fact(row_1, alpha, source_1).",
            "domain_omission(row_1, 'chronology_fact/3', none_found, no_chronology, source_1).",
            "domain_omission(row_1, 'wrapper_fact/3', none_found, no_wrapper, source_1).",
        ],
    )

    report = build_report(
        fixture_id="demo_fixture",
        root=root,
        compile_paths=[run1],
        support_threshold=1,
        matcher="constant_slot",
        expected_signatures={"chronology_fact/3", "domain_omission/5"},
    )

    expected_rows = [row["expected_fact"] for row in report["rows"]]
    assert report["summary"]["expected_fact_count"] == 2
    assert "chronology_fact(Entity, alpha, Src)." in expected_rows
    assert "domain_omission(Entity, 'chronology_fact/3', none_found, no_chronology, Src)." in expected_rows
    assert "domain_omission(Entity, 'wrapper_fact/3', none_found, no_wrapper, Src)." not in expected_rows


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


def test_typed_micro_series_forbidden_constant_slot_allows_wildcard_guards(tmp_path: Path) -> None:
    root = tmp_path / "micro"
    fixture = root / "demo_fixture"
    _write(fixture / "expected_facts.pl", "")
    _write(
        fixture / "forbidden_facts.pl",
        "demo_accident(_, _, _, v_2025_11_18, trench_collapse, 1, _).\n",
    )
    run1 = _compile(
        tmp_path / "run1" / "compile.json",
        [
            "demo_accident(accident_yarmouth, inspection_1794687, accident_summary_yarmouth, v_2025_11_18, trench_collapse, 1, direct).",
        ],
    )

    report = build_report(
        fixture_id="demo_fixture",
        root=root,
        compile_paths=[run1],
        support_threshold=1,
        matcher="constant_slot",
    )

    assert report["summary"]["supported_forbidden_fact_count"] == 1
    assert report["forbidden_rows"] == [
        {
            "forbidden_fact": "demo_accident(_, _, _, v_2025_11_18, trench_collapse, 1, _).",
            "support_count": 1,
            "support_runs": ["run1"],
            "supported": True,
        }
    ]


def test_typed_micro_series_cli_enforce_no_unexpected_bites(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "micro"
    fixture = root / "demo_fixture"
    _write(fixture / "expected_facts.pl", "demo_fact(Entity, allowed_value, Src).\n")
    run1 = _compile(
        tmp_path / "run1" / "compile.json",
        [
            "demo_fact(row_1, allowed_value, source_1).",
            "demo_fact(row_2, unexpected_value, source_2).",
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
            "--expected-signature",
            "demo_fact/3",
            "--enforce-supported",
            "--enforce-no-unexpected",
        ],
    )

    assert main() == 1


def test_typed_micro_series_constant_slot_treats_anonymous_underscore_as_variable(
    tmp_path: Path,
) -> None:
    root = tmp_path / "micro"
    fixture = root / "demo_fixture"
    _write(fixture / "expected_facts.pl", "demo_fact(_, governed_value, _Src).\n")
    run1 = _compile(
        tmp_path / "run1" / "compile.json",
        ["demo_fact(row_1, governed_value, source_1)."],
    )

    report = build_report(
        fixture_id="demo_fixture",
        root=root,
        compile_paths=[run1],
        support_threshold=1,
        matcher="constant_slot",
    )

    assert report["summary"]["supported_fact_count"] == 1

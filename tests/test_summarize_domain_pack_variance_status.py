import json
from pathlib import Path

from scripts.summarize_domain_pack_variance_status import build_report, render_markdown


def test_domain_pack_variance_status_reports_support_band(tmp_path: Path) -> None:
    root_a = _write_bundle_root(
        tmp_path / "root_a",
        label="a",
        supported=11,
        expected=13,
        unexpected=0,
        per_run_exact=[11, 12, 12],
    )
    root_b = _write_bundle_root(
        tmp_path / "root_b",
        label="b",
        supported=13,
        expected=13,
        unexpected=1,
        per_run_exact=[13, 12, 12],
        value_status="pass",
        value_violations=0,
        reconcile_count=13,
    )
    manifest = _write_variance_manifest(tmp_path, [root_a, root_b])

    report = build_report(manifest_path=manifest)
    md = render_markdown(report)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["group_count"] == 1
    group = report["groups"][0]
    assert group["supported_min"] == 11
    assert group["supported_max"] == 13
    assert group["expected_min"] == 13
    assert group["expected_max"] == 13
    assert group["unexpected_min"] == 0
    assert group["unexpected_max"] == 1
    assert "`11-13/13`" in md
    assert "`0-1`" in md
    assert "`13` value-mode facts" in md
    assert "value `not_recorded`" in md
    assert "value_domain_report_not_recorded" in md


def test_domain_pack_variance_status_uses_archived_value_domain_report(tmp_path: Path) -> None:
    root = _write_bundle_root(
        tmp_path / "root",
        label="legacy",
        supported=12,
        expected=13,
        value_report_status="pass",
        value_report_violations=0,
        typed_report_count=12,
    )
    manifest = _write_variance_manifest(tmp_path, [root])

    report = build_report(manifest_path=manifest)
    md = render_markdown(report)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["warnings"] == []
    root_row = report["groups"][0]["roots"][0]
    assert root_row["value_domain_status"] == "pass"
    assert root_row["value_domain_violation_count"] == 0
    assert root_row["typed_reconcile_fact_count"] == 12
    assert "value `pass`" in md
    assert "`12` value-mode facts" in md
    assert "value_domain_report_not_recorded" not in md


def test_domain_pack_variance_status_blocks_claim_breaking_gates(tmp_path: Path) -> None:
    root = _write_bundle_root(
        tmp_path / "root",
        label="bad",
        supported=12,
        expected=13,
        forbidden=1,
        atom_blockers=1,
        lens_blockers=1,
        value_status="fail",
        value_violations=1,
    )
    manifest = _write_variance_manifest(tmp_path, [root])

    report = build_report(manifest_path=manifest)

    assert report["summary"]["status"] == "fail"
    reasons = report["summary"]["blocking_reasons"]
    assert "r1:supported_forbidden_fact" in reasons
    assert "r1:atom_shape_blocker" in reasons
    assert "r1:lens_scope_blocker" in reasons
    assert "r1:value_domain_violation" in reasons


def _write_variance_manifest(tmp_path: Path, roots: list[Path]) -> Path:
    path = tmp_path / "variance_manifest.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "prethinker.domain_pack_variance_manifest.v1",
                "groups": [
                    {
                        "id": "sec_band",
                        "title": "SEC Band",
                        "fixture_id": "sec_form_8k_skeleton_transfer_003",
                        "claim_read": "do not promote favorable draw",
                        "roots": [
                            {"id": f"r{index}", "role": "test", "path": str(root)}
                            for index, root in enumerate(roots, start=1)
                        ],
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def _write_bundle_root(
    root: Path,
    *,
    label: str,
    supported: int,
    expected: int,
    forbidden: int = 0,
    unexpected: int = 0,
    atom_blockers: int = 0,
    lens_blockers: int = 0,
    per_run_exact: list[int] | None = None,
    value_status: str | None = None,
    value_violations: int | None = None,
    value_report_status: str | None = None,
    value_report_violations: int | None = None,
    typed_report_count: int | None = None,
    reconcile_count: int | None = None,
) -> Path:
    (root / "reports").mkdir(parents=True)
    manifest = {
        "schema_version": "domain_lens_bundle_manifest_v1",
        "label": label,
        "fixture": "sec_form_8k_skeleton_transfer_003",
        "repeat": 3,
        "score_summary": {
            "compile_count": 3,
            "expected_fact_count": expected,
            "forbidden_fact_count": 10,
            "supported_fact_count": supported,
            "supported_forbidden_fact_count": forbidden,
            "unexpected_fact_count": unexpected,
            "unsupported_fact_count": expected - supported,
        },
        "settings": {
            "backend": "lmstudio",
            "model": "qwen/qwen3.6-35b-a3b",
            "temperature": 0.0,
            "top_p": 1.0,
            "num_ctx": 65536,
            "matcher": "constant_slot",
            "support_threshold": 2,
        },
        "union_atom_audit_summary": {
            "atom_shape_blocker_count": atom_blockers,
            "lens_scope_blocker_count": lens_blockers,
            "registered_fact_rate": 1.0,
        },
    }
    if value_status is not None:
        manifest["union_carrier_value_domain_summary"] = {
            "status": value_status,
            "violation_count": value_violations or 0,
        }
    if value_report_status is not None:
        (root / "reports" / "union_carrier_value_domains.json").write_text(
            json.dumps(
                {
                    "schema_version": "carrier_value_domain_audit_v1",
                    "summary": {
                        "status": value_report_status,
                        "violation_count": value_report_violations or 0,
                    },
                    "violations": [],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    if reconcile_count is not None:
        manifest["typed_reconcile_summary"] = {
            "reconciled_fact_count": reconcile_count,
        }
    if typed_report_count is not None:
        (root / "reports" / "typed_reconcile_support_ge2_value.json").write_text(
            json.dumps(
                {
                    "schema_version": "governed_typed_micro_reconciliation_v1",
                    "fixture_id": "sec_form_8k_skeleton_transfer_003",
                    "source_compile": {
                        "mode": "governed_typed_micro_reconciliation",
                        "facts": [f"test_fact_{index}." for index in range(typed_report_count)],
                        "unique_fact_count": typed_report_count,
                        "governed_reconciliation": {
                            "schema_version": "governed_typed_micro_reconciliation_v1",
                            "fixture_id": "sec_form_8k_skeleton_transfer_003",
                            "support_mode": "value",
                        },
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if per_run_exact is not None:
        series = {
            "runs": [
                {"matched_fact_count": exact, "expected_fact_count": expected}
                for exact in per_run_exact
            ]
        }
        (root / "reports" / "typed_micro_series_summary.json").write_text(
            json.dumps(series, indent=2),
            encoding="utf-8",
        )
    return root

import json
import zipfile
from pathlib import Path

from scripts.audit_pending_external_work_orders import build_report, main, render_markdown


def test_pending_external_work_order_audit_accepts_source_only_zip(tmp_path: Path) -> None:
    proposal = _write_proposal(tmp_path, zip_path=tmp_path / "work_order.zip")
    _write_zip(
        tmp_path / "work_order.zip",
        [
            "WORK_ORDER.md",
            "expected_facts_TEMPLATE.pl",
            "forbidden_facts_TEMPLATE.pl",
            "manifest_TEMPLATE.json",
            "example_wrapper_v1.json",
            "fixture_a/source.md",
            "fixture_a/metadata.json",
            "fixture_a/provenance.md",
            "fixture_a/fixture_notes.md",
        ],
    )

    report = build_report([proposal])
    md = render_markdown(report)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["work_order_count"] == 1
    assert report["work_orders"][0]["errors"] == []
    assert "source_only_expected_forbidden_oracle" in md


def test_pending_external_work_order_audit_blocks_missing_fixture_package(tmp_path: Path) -> None:
    proposal = _write_proposal(tmp_path, zip_path=tmp_path / "work_order.zip")
    _write_zip(
        tmp_path / "work_order.zip",
        [
            "WORK_ORDER.md",
            "expected_facts_TEMPLATE.pl",
            "forbidden_facts_TEMPLATE.pl",
            "manifest_TEMPLATE.json",
            "example_wrapper_v1.json",
            "fixture_a/source.md",
        ],
    )

    report = build_report([proposal])

    assert report["summary"]["status"] == "fail"
    errors = report["work_orders"][0]["errors"]
    assert "fixture_a:missing_metadata.json" in errors
    assert "fixture_a:missing_provenance.md" in errors


def test_pending_external_work_order_audit_blocks_zip_traversal_entries(tmp_path: Path) -> None:
    proposal = _write_proposal(tmp_path, zip_path=tmp_path / "work_order.zip")
    _write_zip(
        tmp_path / "work_order.zip",
        [
            "WORK_ORDER.md",
            "expected_facts_TEMPLATE.pl",
            "forbidden_facts_TEMPLATE.pl",
            "manifest_TEMPLATE.json",
            "example_wrapper_v1.json",
            "fixture_a/source.md",
            "fixture_a/metadata.json",
            "fixture_a/provenance.md",
            "../outside.txt",
        ],
    )

    report = build_report([proposal])

    assert report["summary"]["status"] == "fail"
    assert "unsafe_zip_entry_traversal:../outside.txt" in report["work_orders"][0]["errors"]


def test_pending_external_work_order_audit_can_inventory_standalone_tmp_zips(tmp_path: Path) -> None:
    proposal = _write_proposal(tmp_path, zip_path=tmp_path / "declared.zip")
    _write_zip(
        tmp_path / "declared.zip",
        [
            "WORK_ORDER.md",
            "expected_facts_TEMPLATE.pl",
            "forbidden_facts_TEMPLATE.pl",
            "manifest_TEMPLATE.json",
            "example_wrapper_v1.json",
            "fixture_a/source.md",
            "fixture_a/metadata.json",
            "fixture_a/provenance.md",
        ],
    )
    _write_zip(
        tmp_path / "standalone.zip",
        [
            "README.md",
            "expected_facts.pl",
            "forbidden_facts.pl",
            "source.md",
            "current_judged_qa_manifest.json",
        ],
    )

    report = build_report([proposal], tmp_root=tmp_path, include_tmp_zips=True)
    md = render_markdown(report)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["work_order_count"] == 2
    assert report["summary"]["standalone_work_order_count"] == 1
    assert any(row["source"] == "tmp_zip" for row in report["work_orders"])
    assert "standalone_external_work_order" in md


def test_pending_external_work_order_audit_accepts_candidate_review_packet_shape(tmp_path: Path) -> None:
    proposal = _write_proposal(
        tmp_path,
        zip_path=tmp_path / "candidate_review.zip",
        kind="source_only_candidate_oracle_review",
        fixtures=["fda_transfer_001"],
    )
    _write_zip(
        tmp_path / "candidate_review.zip",
        [
            "README.md",
            "candidate_expected_facts.pl",
            "candidate_forbidden_facts.pl",
            "output_template/manifest.json",
            "example_wrapper_v1.json",
            "fixtures/fda_transfer_001/manifest.json",
            "fixtures/fda_transfer_001/source.md",
        ],
    )

    report = build_report([proposal])

    assert report["summary"]["status"] == "pass"
    assert report["work_orders"][0]["errors"] == []


def test_pending_external_work_order_audit_blocks_candidate_review_packet_missing_manifest(tmp_path: Path) -> None:
    proposal = _write_proposal(
        tmp_path,
        zip_path=tmp_path / "candidate_review.zip",
        kind="source_only_candidate_oracle_review",
        fixtures=["fda_transfer_001"],
    )
    _write_zip(
        tmp_path / "candidate_review.zip",
        [
            "README.md",
            "candidate_expected_facts.pl",
            "candidate_forbidden_facts.pl",
            "example_wrapper_v1.json",
            "fixtures/fda_transfer_001/source.md",
        ],
    )

    report = build_report([proposal])

    assert report["summary"]["status"] == "fail"
    assert "fda_transfer_001:missing_manifest.json" in report["work_orders"][0]["errors"]


def test_pending_external_work_order_audit_blocks_absolute_standalone_entries(tmp_path: Path) -> None:
    _write_zip(
        tmp_path / "standalone.zip",
        [
            "README.md",
            "expected_facts.pl",
            "forbidden_facts.pl",
            "source.md",
            "manifest.json",
            "/absolute.txt",
        ],
    )

    report = build_report([], tmp_root=tmp_path, include_tmp_zips=True)

    assert report["summary"]["status"] == "fail"
    assert "unsafe_zip_entry_absolute:/absolute.txt" in report["work_orders"][0]["errors"]


def test_pending_external_work_order_audit_accepts_manifest_as_standalone_metadata(tmp_path: Path) -> None:
    _write_zip(
        tmp_path / "standalone.zip",
        [
            "README.md",
            "expected_facts.pl",
            "forbidden_facts.pl",
            "manifest.json",
            "source.md",
        ],
    )

    report = build_report([], tmp_root=tmp_path, include_tmp_zips=True)

    assert report["summary"]["status"] == "pass"
    assert report["work_orders"][0]["warnings"] == []


def test_pending_external_work_order_audit_expect_md_marks_stale_report(
    tmp_path: Path,
    monkeypatch,
) -> None:
    proposal = _write_proposal(tmp_path, zip_path=tmp_path / "work_order.zip")
    _write_zip(
        tmp_path / "work_order.zip",
        [
            "WORK_ORDER.md",
            "expected_facts_TEMPLATE.pl",
            "forbidden_facts_TEMPLATE.pl",
            "manifest_TEMPLATE.json",
            "example_wrapper_v1.json",
            "fixture_a/source.md",
            "fixture_a/metadata.json",
            "fixture_a/provenance.md",
        ],
    )
    expected_md = tmp_path / "expected.md"
    expected_md.write_text("# stale\n", encoding="utf-8")
    out_md = tmp_path / "out.md"
    out_json = tmp_path / "out.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "audit_pending_external_work_orders.py",
            "--proposal",
            str(proposal),
            "--proposal-root",
            str(tmp_path / "no-proposals"),
            "--out-md",
            str(out_md),
            "--out-json",
            str(out_json),
            "--expect-md",
            str(expected_md),
        ],
    )

    assert main() == 1
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["summary"]["status"] == "fail"
    assert "expected_markdown_stale" in payload["summary"]["blocking_reasons"][0]


def _write_proposal(
    tmp_path: Path,
    *,
    zip_path: Path,
    kind: str = "source_only_expected_forbidden_oracle",
    fixtures: list[str] | None = None,
) -> Path:
    path = tmp_path / "proposal.json"
    path.write_text(
        json.dumps(
            {
                "proposal_id": "example_wrapper_v1",
                "pending_external_work_orders": [
                    {
                        "kind": kind,
                        "path": str(zip_path),
                        "fixtures": fixtures or ["fixture_a"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def _write_zip(path: Path, entries: list[str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for entry in entries:
            archive.writestr(entry, "placeholder\n")

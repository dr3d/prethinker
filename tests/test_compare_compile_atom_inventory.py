import json
import os
from pathlib import Path

from scripts.compare_compile_atom_inventory import build_comparison, render_markdown


def _write_compile(path: Path, facts: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "source_compile": {
                    "facts": facts,
                }
            }
        ),
        encoding="utf-8",
    )


def test_compile_atom_inventory_comparison_reports_signature_drift(tmp_path: Path) -> None:
    left = tmp_path / "left.json"
    right = tmp_path / "right.json"
    _write_compile(
        left,
        [
            "document_date(doc_a, v_2026_05_30).",
            "document_identifier(doc_a, commission_file_number, id_001_39898).",
            "document_signatory(doc_a, person_a, chief_financial_officer).",
            "source_record_text_display(src_line_0001, 'Commission file number 001-39898').",
        ],
    )
    _write_compile(
        right,
        [
            "document_date(doc_a, v_2026_05_30).",
            "entity_identity(doc_a, id_001_39898, commission_file_number).",
            "entity_identity(doc_a, drvn, trading_symbol).",
            "source_record_text_display(src_line_0001, 'Commission file number 001-39898').",
        ],
    )

    report = build_comparison(left=left, right=right, max_examples=2)

    assert report["summary"]["left_fact_count"] == 3
    assert report["summary"]["right_fact_count"] == 3
    assert report["summary"]["common_fact_count"] == 1
    assert report["summary"]["added_signature_count"] == 1
    assert report["summary"]["removed_signature_count"] == 2
    assert report["summary"]["signature_jaccard"] == 0.25
    assert report["summary"]["left_registered_signature_count"] == 1
    assert report["summary"]["right_registered_signature_count"] == 0
    assert report["summary"]["common_registered_signature_count"] == 0
    assert report["left"]["summary"]["rejected_counts"] == {"source_record": 1}
    assert report["right"]["summary"]["rejected_counts"] == {"source_record": 1}
    assert [row["signature"] for row in report["added_signatures"]] == ["entity_identity/3"]
    assert {row["signature"] for row in report["removed_signatures"]} == {
        "document_identifier/3",
        "document_signatory/3",
    }


def test_compile_atom_inventory_comparison_resolves_latest_json_in_directory(tmp_path: Path) -> None:
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    _write_compile(left_dir / "old.json", ["document_date(doc_a, v_2026_05_29)."])
    _write_compile(left_dir / "new.json", ["document_date(doc_a, v_2026_05_30)."])
    _write_compile(right_dir / "run.json", ["document_date(doc_a, v_2026_05_30)."])
    os.utime(left_dir / "old.json", (1, 1))
    os.utime(left_dir / "new.json", (2, 2))

    report = build_comparison(left=left_dir, right=right_dir)

    assert report["summary"]["fact_jaccard"] == 1.0
    assert report["left"]["compile_json"].endswith("new.json")
    assert report["right"]["compile_json"].endswith("run.json")


def test_compile_atom_inventory_comparison_redacts_prose_arguments_not_typed_slots(
    tmp_path: Path,
) -> None:
    left = tmp_path / "left.json"
    right = tmp_path / "right.json"
    prose = (
        "This is a long source-derived detail sentence with enough words that it "
        "must be redacted from the comparison while preserving the category atom."
    )
    _write_compile(
        left,
        [
            f"error_declaration(err_a, lease_adjustments, '{prose}', item_4_02).",
        ],
    )
    _write_compile(
        right,
        [
            f"error_declaration(err_a, lease_adjustments, '{prose}', item_4_02).",
        ],
    )

    report = build_comparison(left=left, right=right)

    assert report["summary"]["common_fact_count"] == 1
    assert report["summary"]["fact_jaccard"] == 1.0
    assert report["left"]["summary"]["rejected_counts"] == {"prose_arg_redacted": 1}
    assert report["right"]["summary"]["rejected_counts"] == {"prose_arg_redacted": 1}
    assert report["unchanged_common_signatures"][0]["signature"] == "error_declaration/4"
    assert report["unchanged_common_signatures"][0]["registered_contract"] is False


def test_compile_atom_inventory_comparison_markdown_names_added_removed(tmp_path: Path) -> None:
    left = tmp_path / "left.json"
    right = tmp_path / "right.json"
    _write_compile(left, ["document_identifier(doc_a, accession_number, acc_1)."])
    _write_compile(right, ["entity_identity(doc_a, acc_1, accession_number)."])

    markdown = render_markdown(build_comparison(left=left, right=right))

    assert "# Compile Atom Inventory Comparison" in markdown
    assert "`entity_identity/3`" in markdown
    assert "`document_identifier/3`" in markdown
    assert "| Signature | Registered | Left | Right | Fact Jaccard | Examples |" in markdown
    assert "not a query router" in markdown

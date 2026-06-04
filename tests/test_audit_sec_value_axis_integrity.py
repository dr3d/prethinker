from pathlib import Path

from scripts.audit_sec_value_axis_integrity import build_report


def test_sec_value_axis_audit_flags_mixed_role_axes(tmp_path: Path) -> None:
    fact_file = tmp_path / "expected_facts.pl"
    fact_file.write_text(
        "\n".join(
            [
                "sec_filing_item(Filing, item_2_02, results_of_operations_financial_condition, furnished, SrcItem202).",
                "sec_filing_item_treatment(Filing, item_9_01, furnished, SrcItem901).",
                "sec_filing_item_treatment(Filing, item_2_02, furnished, exhibit_table_row_99_1).",
                "sec_exhibit(Filing, exhibit_104, cover_page_ixbrl, embedded_ixbrl, SrcExhibit104).",
                "sec_exhibit(Filing, exhibit_104, cover_page_ixbrl, filed, SrcExhibit104).",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_report(compile_roots=[], compile_jsons=[], fact_files=[fact_file])

    assert report["summary"]["status"] == "fail"
    assert {row["issue"] for row in report["issues"]} == {
        "legal_treatment_in_item_role",
        "exhibit_item_treatment_misattached",
        "item_treatment_from_exhibit_table_scope",
        "content_format_in_exhibit_legal_treatment_slot",
        "cover_page_ixbrl_treatment_inferred",
    }


def test_sec_value_axis_audit_accepts_axis_clean_roles(tmp_path: Path) -> None:
    fact_file = tmp_path / "expected_facts.pl"
    fact_file.write_text(
        "\n".join(
            [
                "sec_filing_item(Filing, item_5_02, officer_departure_appointment, substantive, SrcItem502).",
                "sec_filing_item_treatment(Filing, item_2_02, furnished, SrcItem202).",
                "sec_exhibit(Filing, exhibit_99_1, press_release, furnished, SrcExhibit991).",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_report(compile_roots=[], compile_jsons=[], fact_files=[fact_file])

    assert report["summary"]["status"] == "pass"
    assert report["issues"] == []

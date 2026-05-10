from src.source_record_ledger import (
    extract_source_record_ledger,
    source_record_ledger_facts,
    source_record_ledger_context,
)
from kb_pipeline import CorePrologRuntime


def test_extract_source_record_ledger_preserves_rows_and_sections() -> None:
    text = "\n".join(
        [
            "# Incident Packet",
            "",
            "## Section 2 Evidence",
            "| Source | Time | Claim |",
            "| --- | --- | --- |",
            "| BAS-002 | 22:12 | Raw badge event |",
            "- Exhibit C-1 records corrected timestamp.",
            "Memo LAB4C-MEM-2026-04-22 says the autoclave was unclosed.",
            "**Subject.** The Halberd Collection consists of forty-seven items.",
        ]
    )

    ledger = extract_source_record_ledger(text)
    rows = ledger["rows"]

    exact = {row["exact"] for row in rows}
    labels = {row["label"] for row in rows}
    kinds = {row["kind"] for row in rows}

    assert "# Incident Packet" in exact
    assert "| BAS-002 | 22:12 | Raw badge event |" in exact
    assert "- Exhibit C-1 records corrected timestamp." in exact
    assert "Memo LAB4C-MEM-2026-04-22 says the autoclave was unclosed." in exact
    assert "**Subject.** The Halberd Collection consists of forty-seven items." in exact
    assert "Section 2 Evidence" in labels
    assert "BAS-002" in labels
    assert "Exhibit C-1" in labels
    assert "LAB4C-MEM-2026-04-22" in labels
    assert "Subject" in labels
    assert {"heading", "table_row", "list_row", "labeled_line"}.issubset(kinds)
    assert any(row.get("cells") == ["BAS-002", "22:12", "Raw badge event"] for row in rows)
    assert any(row.get("headers") == ["Source", "Time", "Claim"] for row in rows if row.get("label") == "BAS-002")


def test_source_record_ledger_context_is_guidance_not_truth() -> None:
    ledger = extract_source_record_ledger("## Section 2\n- Exhibit C-1 records a row.")

    context = "\n".join(source_record_ledger_context(ledger))

    assert "not truth" in context
    assert "Do not infer ownership" in context
    assert "Exhibit C-1" in context


def test_source_record_ledger_facts_are_queryable_source_address_only() -> None:
    ledger = extract_source_record_ledger("## Section 2\n| Source | Time |\n| --- | --- |\n| BAS-002 | 22:12 |\n- Exhibit C-1 records a row.")

    facts = source_record_ledger_facts(ledger)

    assert "source_record_row(src_line_0005, list_row, 5, section_2, exhibit_c_1)." in facts
    assert "source_record_label(src_line_0005, exhibit_c_1)." in facts
    assert any(fact.startswith("source_record_text_atom(src_line_0005, ") for fact in facts)
    assert any(fact.startswith("source_record_text_key(src_line_0005, text_") for fact in facts)
    assert "source_record_cell(src_line_0004, 1, bas_002)." in facts
    assert "source_record_cell(src_line_0004, 2, v_22_12)." in facts
    assert "source_record_cell_header(src_line_0004, 1, source)." in facts
    assert "source_record_cell_header(src_line_0004, 2, time)." in facts
    assert "source_record_field(src_line_0004, source, bas_002)." in facts
    assert "source_record_field(src_line_0004, time, v_22_12)." in facts
    assert "source_record_numeric_token(src_line_0004, v_22_12)." in facts
    assert not any(fact.startswith("owns(") or fact.startswith("status(") for fact in facts)

    runtime = CorePrologRuntime()
    for fact in facts:
        assert runtime.assert_fact(fact).get("status") == "success"

    result = runtime.query_rows("source_record_label(Row, Label).")

    assert result.get("status") == "success"
    assert {"Row": "src_line_0005", "Label": "exhibit_c_1"} in result.get("rows", [])

    cell_result = runtime.query_rows("source_record_cell(Row, Index, Cell).")

    assert cell_result.get("status") == "success"
    assert {"Row": "src_line_0004", "Index": "1", "Cell": "bas_002"} in cell_result.get("rows", [])

    field_result = runtime.query_rows("source_record_field(Row, Header, Cell).")

    assert field_result.get("status") == "success"
    assert {"Row": "src_line_0004", "Header": "time", "Cell": "v_22_12"} in field_result.get("rows", [])


def test_source_record_ledger_keeps_wrapped_official_prose() -> None:
    ledger = extract_source_record_ledger(
        "\n".join(
            [
                "## Section 3 Lodging",
                "Adult lodging: T. Mendez 202; J. Phelps 204; K. Rosario 208;",
                "M. Okonkwo 210; N. Park 206 (medical-coverage station).",
                "",
                "## Section 9 Provenance",
                "Roster v1 and v2 are retained in the audit binder (location: Activities Office filing",
                "cabinet 3, drawer 2) and are not the operational document.",
            ]
        )
    )

    rows = ledger["rows"]
    exact_by_line = {row["line"]: row["exact"] for row in rows}
    kind_by_line = {row["line"]: row["kind"] for row in rows}

    assert exact_by_line[2].startswith("Adult lodging:")
    assert kind_by_line[3] in {"anchored_line", "continuation_line"}
    assert "N. Park 206" in exact_by_line[3]
    assert kind_by_line[6] == "anchored_line"
    assert kind_by_line[7] == "continuation_line"
    assert "cabinet 3, drawer 2" in exact_by_line[7]


def test_source_record_ledger_keeps_root_cause_scope_refusal() -> None:
    ledger = extract_source_record_ledger(
        "\n".join(
            [
                "## Section 8 Inferences",
                "This packet does not assign root cause. Root cause assignment is the",
                "function of a separate root-cause analysis (RCA), which is in",
                "preparation but not part of this packet.",
            ]
        )
    )

    rows = ledger["rows"]
    exact_by_line = {row["line"]: row["exact"] for row in rows}
    kind_by_line = {row["line"]: row["kind"] for row in rows}

    assert kind_by_line[2] == "anchored_line"
    assert kind_by_line[3] in {"anchored_line", "continuation_line"}
    assert kind_by_line[4] in {"anchored_line", "continuation_line"}
    assert "does not assign root cause" in exact_by_line[2]
    assert "separate root-cause analysis" in exact_by_line[3]
    assert "not part of this packet" in exact_by_line[4]

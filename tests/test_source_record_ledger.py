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
    assert "plain paragraph lines" in context


def test_source_record_ledger_preserves_plain_prose_lines_without_anchors() -> None:
    ledger = extract_source_record_ledger(
        "\n".join(
            [
                "# Procedure Notes",
                "",
                "Harbor planners compare dock vibration in the north alcove using impact logging.",
                "",
                "Field coordinators verify generator readiness from the mobile trailer using load cycling.",
            ]
        )
    )

    rows = ledger["rows"]
    kind_by_line = {row["line"]: row["kind"] for row in rows}
    exact_by_line = {row["line"]: row["exact"] for row in rows}

    assert kind_by_line[3] == "paragraph_line"
    assert kind_by_line[5] == "paragraph_line"
    assert "dock vibration" in exact_by_line[3]
    assert "generator readiness" in exact_by_line[5]


def test_source_record_ledger_preserves_long_statement_tail_clauses() -> None:
    long_statement = (
        '"At about 13:55 I returned from break. '
        + "I checked the cabinet and reviewed the pump line. " * 10
        + 'I did not respond to the 14:37 alarm at bedside because I was in Room 502."'
    )

    ledger = extract_source_record_ledger("## Statements\n" + long_statement)

    exact_rows = [row["exact"] for row in ledger["rows"] if row["kind"] == "anchored_line"]
    assert exact_rows
    assert "14:37 alarm at bedside" in exact_rows[0]
    assert "Room 502" in exact_rows[0]


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


def test_source_record_exact_round_trips_table_text_with_commas() -> None:
    runtime = CorePrologRuntime()
    fact = (
        "source_record_exact(src_line_0039, "
        "'| EX-U-1 | USB thumb drive, 32 GB | SLIP-7721 | BC-883075 | LK-3 | Held |')."
    )

    assert runtime.assert_fact(fact).get("status") == "success"

    result = runtime.query_rows("source_record_exact(src_line_0039, Exact).")

    assert result.get("status") == "success"
    assert result.get("rows") == [
        {
            "Exact": "| EX-U-1 | USB thumb drive, 32 GB | SLIP-7721 | BC-883075 | LK-3 | Held |"
        }
    ]


def test_source_record_exact_round_trips_escaped_apostrophe_text() -> None:
    runtime = CorePrologRuntime()
    fact = "source_record_exact(src_line_0104, '- BAY-04-I is behind the bay\\'s mesh door.')."

    assert runtime.assert_fact(fact).get("status") == "success"

    result = runtime.query_rows("source_record_exact(src_line_0104, Exact).")

    assert result.get("status") == "success"
    assert result.get("rows") == [{"Exact": "- BAY-04-I is behind the bay's mesh door."}]


def test_source_record_ledger_emits_explicit_roster_table_members() -> None:
    ledger = extract_source_record_ledger(
        "\n".join(
            [
                "### 6.1 Students by homeroom (v1.3)",
                "| Homeroom | Count | Student IDs |",
                "|---|---|---|",
                "| 7-A | 4 | STU-1023 Park · STU-1041 Lin · STU-1058 Cohen · STU-1077 Bauer |",
            ]
        )
    )

    facts = source_record_ledger_facts(ledger)

    assert "explicit_table_membership(src_line_0004, v1_3, 7_a, stu_1023)." in facts
    assert "explicit_table_member_label(src_line_0004, v1_3, 7_a, stu_1023, stu_1023_park)." in facts
    assert "explicit_table_member_alias(stu_1023, stu_1023_park)." in facts
    assert "explicit_table_member_header(src_line_0004, student_ids)." in facts
    assert "explicit_table_scope(src_line_0004, 7_a)." in facts
    assert "explicit_table_version(src_line_0004, v1_3)." in facts
    assert "roster_table_member(src_line_0004, v1_3, 7_a, stu_1023)." in facts
    assert "roster_table_member(src_line_0004, v1_3, 7_a, stu_1041)." in facts
    assert "roster_table_member_label(src_line_0004, v1_3, 7_a, stu_1023, stu_1023_park)." in facts
    assert "roster_table_member_alias(stu_1023, stu_1023_park)." in facts
    assert "roster_table_member_header(src_line_0004, student_ids)." in facts
    assert "roster_table_scope(src_line_0004, 7_a)." in facts
    assert "roster_table_version(src_line_0004, v1_3)." in facts


def test_source_record_ledger_emits_generic_explicit_table_memberships() -> None:
    ledger = extract_source_record_ledger(
        "\n".join(
            [
                "### 4.2 Maintenance crews",
                "| Team | Members |",
                "|---|---|",
                "| Pump crew | EMP-204 Rivera; EMP-311 Okafor |",
            ]
        )
    )

    facts = source_record_ledger_facts(ledger)

    assert "explicit_table_membership(src_line_0004, unspecified_version, pump_crew, emp_204)." in facts
    assert "explicit_table_membership(src_line_0004, unspecified_version, pump_crew, emp_311)." in facts
    assert "explicit_table_member_label(src_line_0004, unspecified_version, pump_crew, emp_204, emp_204_rivera)." in facts
    assert "explicit_table_member_header(src_line_0004, members)." in facts
    assert not any(fact.startswith("roster_table_member(") for fact in facts)


def test_source_record_ledger_does_not_infer_roster_members_without_group_column() -> None:
    ledger = extract_source_record_ledger(
        "\n".join(
            [
                "### 2.1 Bus 1",
                "| Seat row | Students |",
                "|---|---|",
                "| 1-4 | S-001, S-002, S-003, S-004, S-005, S-006 |",
            ]
        )
    )

    facts = source_record_ledger_facts(ledger)

    assert "source_record_field(src_line_0004, students, s_001_s_002_s_003_s_004_s_005_s_006)." in facts
    assert not any(fact.startswith("roster_table_member(") for fact in facts)


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
    assert kind_by_line[7] in {"anchored_line", "continuation_line"}
    assert "cabinet 3, drawer 2" in exact_by_line[7]


def test_source_record_ledger_keeps_count_summary_and_clock_audit_prose() -> None:
    ledger = extract_source_record_ledger(
        "\n".join(
            [
                "## Section 5. Attendance Scans",
                "| Scan time | Location | Student count |",
                "| --- | --- | --- |",
                "| 06:18 | North lot | 18 |",
                "| 06:33 | South lot | 17 |",
                "",
                "Bus 1 and Bus 2 outbound counts (18 + 17) sum to 35, matching v3",
                "roster. The scanner timestamps are nominally local time and have not",
                "been audited against an external clock for this packet.",
            ]
        )
    )

    rows = ledger["rows"]
    exact_by_line = {row["line"]: row["exact"] for row in rows}
    kind_by_line = {row["line"]: row["kind"] for row in rows}

    assert kind_by_line[7] == "anchored_line"
    assert kind_by_line[8] in {"anchored_line", "continuation_line"}
    assert kind_by_line[9] in {"anchored_line", "continuation_line"}
    assert "counts (18 + 17) sum to 35" in exact_by_line[7]
    assert "scanner timestamps are nominally local time" in exact_by_line[8]
    assert "audited against an external clock" in exact_by_line[9]


def test_source_record_ledger_keeps_standalone_sample_result_prose() -> None:
    ledger = extract_source_record_ledger(
        "\n".join(
            [
                "## Lab Result",
                "",
                "3 of 5 samples from Batch 9C tested positive for contaminant.",
            ]
        )
    )

    rows = ledger["rows"]
    exact_by_line = {row["line"]: row["exact"] for row in rows}
    kind_by_line = {row["line"]: row["kind"] for row in rows}
    facts = source_record_ledger_facts(ledger)

    assert kind_by_line[3] == "anchored_line"
    assert exact_by_line[3].startswith("3 of 5 samples from Batch 9C")
    assert "source_record_numeric_token(src_line_0003, v_3)." in facts
    assert "source_record_numeric_token(src_line_0003, v_5)." in facts
    assert any(fact.startswith("source_record_text_atom(src_line_0003, v_3_of_5_samples") for fact in facts)


def test_source_record_ledger_keeps_explicit_count_statement_lines() -> None:
    ledger = extract_source_record_ledger(
        "\n".join(
            [
                "## Compact Count Statement",
                "",
                "Affected items, stated total: 14.",
                "The statement includes 3 reserve items not listed individually.",
                "A pending addendum proposed adding 2 provisional items.",
                "An analyst withdrew an estimate of 15 items.",
            ]
        )
    )

    rows = ledger["rows"]
    exact_by_line = {row["line"]: row["exact"] for row in rows}
    kind_by_line = {row["line"]: row["kind"] for row in rows}
    facts = source_record_ledger_facts(ledger)

    assert kind_by_line[3] == "anchored_line"
    assert kind_by_line[4] in {"anchored_line", "continuation_line"}
    assert kind_by_line[5] in {"anchored_line", "continuation_line"}
    assert kind_by_line[6] in {"anchored_line", "continuation_line"}
    assert exact_by_line[3] == "Affected items, stated total: 14."
    assert "source_record_numeric_token(src_line_0003, v_14)." in facts
    assert "source_record_numeric_token(src_line_0004, v_3)." in facts
    assert "source_record_numeric_token(src_line_0005, v_2)." in facts
    assert "source_record_numeric_token(src_line_0006, v_15)." in facts


def test_source_record_ledger_keeps_numeric_prose_without_english_count_words() -> None:
    ledger = extract_source_record_ledger(
        "\n".join(
            [
                "## Proposta pendente",
                "",
                "Uma proposta pendente queria adicionar 2 registros temporarios. A proposta nao",
                "foi aprovada antes do fechamento; portanto esses 2 registros temporarios nao",
                "fazem parte do total final.",
                "",
                "Uma estimativa anterior indicou 11 registros afetados. Essa estimativa foi",
                "retirada antes do fechamento.",
            ]
        )
    )

    rows = ledger["rows"]
    exact_by_line = {row["line"]: row["exact"] for row in rows}
    kind_by_line = {row["line"]: row["kind"] for row in rows}
    facts = source_record_ledger_facts(ledger)

    assert kind_by_line[3] == "anchored_line"
    assert kind_by_line[4] in {"anchored_line", "continuation_line"}
    assert kind_by_line[5] == "continuation_line"
    assert kind_by_line[7] == "anchored_line"
    assert kind_by_line[8] == "continuation_line"
    assert exact_by_line[3].startswith("Uma proposta pendente queria adicionar 2")
    assert exact_by_line[4].startswith("foi aprovada antes do fechamento")
    assert exact_by_line[7].startswith("Uma estimativa anterior indicou 11")
    assert "source_record_numeric_token(src_line_0003, v_2)." in facts
    assert "source_record_numeric_token(src_line_0004, v_2)." in facts
    assert "source_record_numeric_token(src_line_0007, v_11)." in facts


def test_source_record_ledger_emits_parenthetical_alias_surfaces() -> None:
    ledger = extract_source_record_ledger(
        "\n".join(
            [
                "## Passage",
                "",
                "The Harbor Review League (HRL) convened the meeting.",
                "The Maritime Audit Council (MAC) observed but did not vote.",
                "The event named the parent body as part of the National Football League (NFL).",
                "N. Park 206 (medical-coverage station) stayed unchanged.",
            ]
        )
    )

    facts = source_record_ledger_facts(ledger)

    assert "source_record_parenthetical_alias(src_line_0003, hrl, harbor_review_league)." in facts
    assert "source_record_alias(src_line_0003, hrl, harbor_review_league)." in facts
    assert "source_record_alias(src_line_0003, harbor_review_league, hrl)." in facts
    assert "source_record_parenthetical_alias(src_line_0004, mac, maritime_audit_council)." in facts
    assert "source_record_parenthetical_alias(src_line_0005, nfl, national_football_league)." in facts
    assert not any(
        fact.startswith(("source_record_parenthetical_alias(", "source_record_alias("))
        and "of_the_national_football_league" in fact
        for fact in facts
    )
    assert not any(
        fact.startswith(("source_record_parenthetical_alias(", "source_record_alias("))
        and "medical_coverage_station" in fact
        for fact in facts
    )


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


def test_source_record_ledger_keeps_document_standing_and_reference_prose() -> None:
    ledger = extract_source_record_ledger(
        "\n".join(
            [
                "## Section F. Recorded Statements",
                "Reproduction does not constitute a finding of fact.",
                "The forensic handwriting analyst's report and the Court's",
                "ultimate rulings are the authoritative sources for findings.",
                "",
                "## Section G. Compilation Notes",
                "The following are referenced but not reproduced in this register: the",
                "decedent's last will and testament dated 2018-07-22.",
            ]
        )
    )

    rows = ledger["rows"]
    exact_by_line = {row["line"]: row["exact"] for row in rows}

    assert exact_by_line[2] == "Reproduction does not constitute a finding of fact."
    assert exact_by_line[3].startswith("The forensic handwriting")
    assert exact_by_line[4].startswith("ultimate rulings are the authoritative sources")
    assert exact_by_line[7].startswith("The following are referenced but not reproduced")
    assert exact_by_line[8].startswith("decedent's last will and testament")


def test_source_record_ledger_keeps_blockquoted_memo_metadata() -> None:
    ledger = extract_source_record_ledger(
        "\n".join(
            [
                "### 8.1 Site Lead Memo",
                "> **From:** D. Rourke, NBFH Site Lead",
                "> **Date:** 2026-04-13",
                "> I will retain the keys personally pending verification visit.",
            ]
        )
    )

    rows = ledger["rows"]
    exact_by_line = {row["line"]: row["exact"] for row in rows}
    label_by_line = {row["line"]: row["label"] for row in rows}

    assert exact_by_line[2] == "**From:** D. Rourke, NBFH Site Lead"
    assert label_by_line[2] == "From"
    assert exact_by_line[3] == "**Date:** 2026-04-13"
    assert label_by_line[3] == "Date"
    assert exact_by_line[4] == "I will retain the keys personally pending verification visit."

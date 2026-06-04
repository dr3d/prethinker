import json

from scripts.audit_redaction_replay import _iter_qa_files, _redacted_row, build_report, parse_args


def test_parse_args_prefers_openrouter_key_for_redacted_rejudge(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "or-secret")
    monkeypatch.setenv("PRETHINKER_API_KEY", "local-token")
    monkeypatch.setattr("sys.argv", ["audit_redaction_replay.py", "qa.json"])

    args = parse_args()

    assert args.api_key == "or-secret"


def test_redaction_replay_proxy_separates_typed_from_prose_exact(tmp_path):
    qa_path = tmp_path / "fixture_a" / "qa.json"
    qa_path.parent.mkdir()
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "utterance": "What is the docket?",
                        "reference_answer": "no_2025_1705",
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {
                                "query": "case_identifier(Case, Docket).",
                                "result": {
                                    "predicate": "case_identifier",
                                    "status": "success",
                                    "rows": [{"Case": "case_a", "Docket": "no_2025_1705"}],
                                },
                            }
                        ],
                    },
                    {
                        "id": "q002",
                        "utterance": "What phrase appears?",
                        "reference_answer": "clogged or collapsed pores",
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {
                                "query": "source_record_text_display(Row, Text).",
                                "result": {
                                    "predicate": "source_record_text_display",
                                    "status": "success",
                                    "rows": [{"Row": "src_line_1", "Text": "clogged or collapsed pores"}],
                                },
                            }
                        ],
                    },
                    {
                        "id": "q003",
                        "utterance": "What was partial?",
                        "reference_answer": "missing",
                        "reference_judge": {"verdict": "partial"},
                        "query_results": [],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path])

    assert report["summary"]["product_exact"] == 2
    assert report["summary"]["thesis_exact"] == 1
    assert report["summary"]["prose_dependent_exact"] == 1
    assert report["summary"]["status"] == "blocked"
    rows = {row["id"]: row for row in report["rows"]}
    assert rows["q001"]["thesis_verdict"] == "survived"
    assert rows["q002"]["thesis_verdict"] == "prose_dependent"


def test_redaction_replay_blocks_when_no_product_exact_rows(tmp_path):
    qa_dir = tmp_path / "fixture_a"
    qa_dir.mkdir()
    qa_file = qa_dir / "qa.json"
    qa_file.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "utterance": "What is A?",
                        "reference_answer": "A",
                        "reference_judge": {"verdict": "miss"},
                        "query_results": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_file])

    assert report["summary"]["product_exact"] == 0
    assert report["summary"]["blocking_reasons"] == ["no_product_exact_rows"]
    assert report["summary"]["status"] == "blocked"


def test_redaction_replay_redacts_control_plane_prose_fields(tmp_path):
    qa_path = tmp_path / "fixture_a" / "qa.json"
    qa_path.parent.mkdir()
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "utterance": "What is the docket?",
                        "reference_answer": "no_2025_1705",
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {
                                "query": "case_identifier(Case, Docket).",
                                "result": {
                                    "predicate": "case_identifier",
                                    "status": "success",
                                    "note": "control-plane prose, not evidence",
                                    "original_query": "case_identifier(Case, Docket).",
                                    "repaired_query": "case_identifier(Case, Docket).",
                                    "reasoning_basis": {
                                        "bound_query_constants": [
                                            {"name": "Kind", "value": "docket"}
                                        ]
                                    },
                                    "rows": [{"Case": "case_a", "Docket": "no_2025_1705"}],
                                },
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path])

    assert report["summary"]["thesis_exact"] == 1
    assert report["summary"]["unclassified_fields"] == []


def test_redaction_replay_treats_internal_variable_keys_as_metadata(tmp_path):
    qa_path = tmp_path / "fixture_a" / "qa.json"
    qa_path.parent.mkdir()
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "reference_answer": "finding_a",
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {
                                "query": "finding(Finding).",
                                "result": {
                                    "predicate": "finding",
                                    "status": "success",
                                    "rows": [{"_Finding": "finding_a"}],
                                },
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path])

    assert report["summary"]["thesis_exact"] == 1
    assert report["summary"]["unclassified_fields"] == []


def test_redaction_replay_keeps_deterministic_bound_arg_display(tmp_path):
    qa_path = tmp_path / "fixture_a" / "qa.json"
    qa_path.parent.mkdir()
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "reference_answer": "2026_03_24",
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {
                                "query": "source_detail(case_a, decision_date, Date, Source).",
                                "result": {
                                    "predicate": "source_detail",
                                    "status": "success",
                                    "rows": [
                                        {
                                            "BoundArg2": "decision_date",
                                            "BoundArg2Display": "decision date",
                                            "Date": "2026_03_24",
                                            "Source": "src_line_1",
                                        }
                                    ],
                                },
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    payload = json.loads(qa_path.read_text(encoding="utf-8"))
    unclassified: set[str] = set()
    redacted_row, _redaction = _redacted_row(payload["rows"][0], unclassified_fields=unclassified)
    redacted_result_row = redacted_row["query_results"][0]["result"]["rows"][0]

    assert redacted_result_row["BoundArg2Display"] == "decision date"
    report = build_report(qa_files=[qa_path])
    assert report["summary"]["thesis_exact"] == 1
    assert report["summary"]["unclassified_fields"] == []


def test_redaction_replay_proxy_accepts_typed_atom_display_variants(tmp_path):
    qa_path = tmp_path / "fixture_a" / "qa.json"
    qa_path.parent.mkdir()
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "reference_answer": (
                            "Driven Brands Holdings Inc.; Delaware; "
                            "I.R.S. Employer Identification No. 47-3595252."
                        ),
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {
                                "query": "registrant_name(drvn, RegistrantName).",
                                "result": {
                                    "predicate": "registrant_name",
                                    "status": "success",
                                    "rows": [{"RegistrantName": "driven_brands_holdings_inc"}],
                                },
                            },
                            {
                                "query": "registrant_identity(drvn, Jurisdiction).",
                                "result": {
                                    "predicate": "registrant_identity",
                                    "status": "success",
                                    "rows": [{"Jurisdiction": "delaware"}],
                                },
                            },
                            {
                                "query": "document_identifier_occurrence(drvn, ein, EIN, Scope, SourceOrder).",
                                "result": {
                                    "predicate": "document_identifier_occurrence",
                                    "status": "success",
                                    "rows": [{"BoundArg2": "ein", "EIN": "47_3595252"}],
                                },
                            },
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path])

    assert report["summary"]["thesis_exact"] == 1
    assert report["summary"]["prose_dependent_exact"] == 0


def test_redaction_replay_proxy_accepts_compact_citation_atom(tmp_path):
    qa_path = tmp_path / "fixture_a" / "qa.json"
    qa_path.parent.mkdir()
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "reference_answer": "Dec. 16, 2024, Hr'g Tr. at 1364:22-1365:7.",
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {
                                "query": "claim_ground(Subject, Ground, ReferenceOrBasis, Outcome).",
                                "result": {
                                    "predicate": "claim_ground",
                                    "status": "success",
                                    "rows": [
                                        {
                                            "ReferenceOrBasis": "dec_16_2024_hr_g_tr_at_1364_22_1365_7"
                                        }
                                    ],
                                },
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path])

    assert report["summary"]["thesis_exact"] == 1
    assert report["summary"]["prose_dependent_exact"] == 0


def test_redaction_replay_proxy_accepts_prolog_reference_constants_from_compiled_fact(tmp_path):
    qa_path = tmp_path / "fixture_a" / "qa.json"
    qa_path.parent.mkdir()
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "reference_answer": (
                            "fda_warning_letter(Letter, cder, "
                            "apothecary_pharma_llc, v_2025_12_01, SrcLetter)."
                        ),
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {
                                "query": (
                                    "fda_warning_letter(Letter, cder, "
                                    "apothecary_pharma_llc, v_2025_12_01, SrcLetter)."
                                ),
                                "result": {
                                    "predicate": "fda_warning_letter",
                                    "status": "answered",
                                    "rows": [
                                        {
                                            "compiled_fact": (
                                                "fda_warning_letter(wl_717972, cder, "
                                                "apothecary_pharma_llc, v_2025_12_01, source_url)."
                                            ),
                                            "Letter": "wl_717972",
                                            "SrcLetter": "source_url",
                                        }
                                    ],
                                },
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path])

    assert report["summary"]["thesis_exact"] == 1
    assert report["summary"]["prose_dependent_exact"] == 0


def test_redaction_replay_proxy_rejects_wrong_prolog_compiled_fact(tmp_path):
    qa_path = tmp_path / "fixture_a" / "qa.json"
    qa_path.parent.mkdir()
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "reference_answer": (
                            "fda_warning_letter(Letter, cder, "
                            "apothecary_pharma_llc, v_2025_12_01, SrcLetter)."
                        ),
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {
                                "query": (
                                    "fda_warning_letter(Letter, cder, "
                                    "apothecary_pharma_llc, v_2025_12_01, SrcLetter)."
                                ),
                                "result": {
                                    "predicate": "fda_warning_letter",
                                    "status": "answered",
                                    "rows": [
                                        {
                                            "compiled_fact": (
                                                "fda_warning_letter(wl_717972, cber, "
                                                "apothecary_pharma_llc, v_2025_12_01, source_url)."
                                            ),
                                            "Letter": "wl_717972",
                                            "SrcLetter": "source_url",
                                        }
                                    ],
                                },
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path])

    assert report["summary"]["thesis_exact"] == 0
    assert report["summary"]["prose_dependent_exact"] == 1


def test_redaction_replay_proxy_rejects_all_variable_prolog_reference(tmp_path):
    qa_path = tmp_path / "fixture_a" / "qa.json"
    qa_path.parent.mkdir()
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "reference_answer": "fda_warning_letter(Letter, Center, Firm, Date, Source).",
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {
                                "query": "fda_warning_letter(Letter, Center, Firm, Date, Source).",
                                "result": {
                                    "predicate": "fda_warning_letter",
                                    "status": "answered",
                                    "rows": [
                                        {
                                            "compiled_fact": (
                                                "fda_warning_letter(wl_717972, cder, "
                                                "apothecary_pharma_llc, v_2025_12_01, source_url)."
                                            ),
                                            "Letter": "wl_717972",
                                            "Center": "cder",
                                            "Firm": "apothecary_pharma_llc",
                                            "Date": "v_2025_12_01",
                                            "Source": "source_url",
                                        }
                                    ],
                                },
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path])

    assert report["summary"]["thesis_exact"] == 0
    assert report["summary"]["prose_dependent_exact"] == 1


def test_redaction_replay_prefers_row_fixture_over_file_parent(tmp_path):
    qa_path = tmp_path / "combined" / "qa.json"
    qa_path.parent.mkdir()
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "fixture": "fixture_from_row",
                        "id": "q001",
                        "reference_answer": "no_2025_1705",
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {
                                "query": "case_identifier(Case, Docket).",
                                "result": {
                                    "predicate": "case_identifier",
                                    "status": "success",
                                    "rows": [{"Case": "case_a", "Docket": "no_2025_1705"}],
                                },
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path])

    assert "fixture_from_row" in report["by_fixture"]
    assert report["rows"][0]["fixture"] == "fixture_from_row"


def test_redaction_replay_redacts_all_source_record_predicates(tmp_path):
    qa_path = tmp_path / "fixture_a" / "qa.json"
    qa_path.parent.mkdir()
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "id": "q001",
                        "reference_answer": "document title",
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {
                                "query": "source_record_label(src_line_1, Label).",
                                "result": {
                                    "predicate": "source_record_label",
                                    "status": "success",
                                    "rows": [{"Row": "src_line_1", "Label": "document_title"}],
                                },
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path])

    assert report["summary"]["thesis_exact"] == 0
    assert report["summary"]["prose_dependent_exact"] == 1
    assert report["rows"][0]["redacted_predicates"] == ["source_record_label"]


def test_redaction_replay_file_discovery_ignores_own_artifacts(tmp_path):
    fixture_path = tmp_path / "fixture_a" / "qa.json"
    fixture_path.parent.mkdir()
    fixture_path.write_text('{"rows": [], "reference_judge": {}}', encoding="utf-8")
    scratch_path = tmp_path / "redaction_replay_8_problem_rows_input.json"
    scratch_path.write_text('{"rows": [], "reference_judge": {}}', encoding="utf-8")

    files = _iter_qa_files(tmp_path)

    assert files == [fixture_path]

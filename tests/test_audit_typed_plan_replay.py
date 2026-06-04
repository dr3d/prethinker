import json

from scripts.audit_typed_plan_replay import build_report


def test_typed_plan_replay_executes_product_exact_queries_over_typed_atoms(tmp_path):
    compile_dir = tmp_path / "compile" / "fixture_a"
    compile_dir.mkdir(parents=True)
    compile_path = compile_dir / "compile.json"
    compile_path.write_text(
        json.dumps(
            {
                    "source_compile": {
                        "facts": [
                            "party_role_context(case_a, union_one, petitioner, direct).",
                            "source_record_text_atom(src_line_1, union_one).",
                        ],
                        "rules": [],
                    }
            }
        ),
        encoding="utf-8",
    )
    qa_path = tmp_path / "qa" / "qa.json"
    qa_path.parent.mkdir()
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                        {
                            "fixture": "fixture_a",
                            "id": "q001",
                            "reference_answer": "Union One",
                            "reference_judge": {"verdict": "exact"},
                            "queries": ["party_role_context(Context, Petitioner, petitioner, Source)."],
                        }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path], compile_root=tmp_path / "compile")

    assert report["summary"]["product_exact"] == 1
    assert report["summary"]["typed_plan_replayed_exact"] == 1
    assert report["summary"]["status"] == "pass"
    assert report["rows"][0]["status"] == "all_queries_success"
    assert report["rows"][0]["typed_fact_count"] == 1


def test_typed_plan_replay_blocks_source_record_query_plans(tmp_path):
    compile_dir = tmp_path / "compile" / "fixture_a"
    compile_dir.mkdir(parents=True)
    (compile_dir / "compile.json").write_text(
        json.dumps({"source_compile": {"facts": ["source_record_text_atom(src_line_1, value_a)."], "rules": []}}),
        encoding="utf-8",
    )
    qa_path = tmp_path / "qa.json"
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "fixture": "fixture_a",
                        "id": "q001",
                        "reference_answer": "value_a",
                        "reference_judge": {"verdict": "exact"},
                        "queries": ["source_record_text_atom(Row, Text)."],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path], compile_root=tmp_path / "compile")

    assert report["summary"]["typed_plan_replayed_exact"] == 0
    assert report["summary"]["blocked_source_record_plan_rows"] == 1
    assert "blocked_source_record_plan_rows" in report["summary"]["blocking_reasons"]
    assert report["rows"][0]["status"] == "blocked_source_record_query"


def test_typed_plan_replay_blocks_when_no_product_exact_rows(tmp_path):
    qa_path = tmp_path / "qa.json"
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "fixture": "fixture_a",
                        "id": "q001",
                        "reference_answer": "no_2025_1705",
                        "reference_judge": {"verdict": "miss"},
                        "queries": ["case_identifier(Case, Docket)."],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path])

    assert report["summary"]["product_exact"] == 0
    assert report["summary"]["blocking_reasons"] == ["no_product_exact_rows"]
    assert report["summary"]["status"] == "blocked"


def test_typed_plan_replay_excludes_prose_like_compile_atoms(tmp_path):
    compile_dir = tmp_path / "compile" / "fixture_a"
    compile_dir.mkdir(parents=True)
    (compile_dir / "compile.json").write_text(
        json.dumps(
            {
                "source_compile": {
                    "facts": [
                        "finding_description(finding_a, long_text_atom).",
                        "finding_status(finding_a, affirmed).",
                    ],
                    "rules": [],
                }
            }
        ),
        encoding="utf-8",
    )
    qa_path = tmp_path / "qa.json"
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "fixture": "fixture_a",
                        "id": "q001",
                        "reference_answer": "long_text_atom",
                        "reference_judge": {"verdict": "exact"},
                        "queries": ["finding_description(Finding, Text)."],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path], compile_root=tmp_path / "compile")

    assert report["summary"]["typed_plan_replayed_exact"] == 0
    assert report["rows"][0]["status"] == "no_query_success"


def test_typed_plan_replay_keeps_party_role_context_atoms(tmp_path):
    compile_dir = tmp_path / "compile" / "fixture_a"
    compile_dir.mkdir(parents=True)
    (compile_dir / "compile.json").write_text(
        json.dumps(
            {
                "source_compile": {
                    "facts": ["party_role_context(case_a, union_one, petitioner, direct)."],
                    "rules": [],
                }
            }
        ),
        encoding="utf-8",
    )
    qa_path = tmp_path / "qa.json"
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "fixture": "fixture_a",
                        "id": "q001",
                        "reference_answer": "Union One",
                        "reference_judge": {"verdict": "exact"},
                        "queries": ["party_role_context(Context, Petitioner, petitioner, Source)."],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path], compile_root=tmp_path / "compile")

    assert report["summary"]["typed_plan_replayed_exact"] == 1
    assert report["summary"]["registered_typed_plan_replayed_exact"] == 1
    assert report["rows"][0]["status"] == "all_queries_success"
    assert report["rows"][0]["unregistered_query_signatures"] == []


def test_typed_plan_replay_reports_unregistered_typed_alias_queries(tmp_path):
    compile_dir = tmp_path / "compile" / "fixture_a"
    compile_dir.mkdir(parents=True)
    (compile_dir / "compile.json").write_text(
        json.dumps(
            {
                "source_compile": {
                    "facts": [
                        "registrant_identity(drvn, delaware).",
                        "incorporation_jurisdiction(drvn, delaware).",
                    ],
                    "rules": [],
                }
            }
        ),
        encoding="utf-8",
    )
    qa_path = tmp_path / "qa.json"
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "fixture": "fixture_a",
                        "id": "q001",
                        "reference_answer": "Delaware",
                        "reference_judge": {"verdict": "exact"},
                        "queries": ["incorporation_jurisdiction(drvn, Jurisdiction)."],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path], compile_root=tmp_path / "compile")

    assert report["summary"]["typed_plan_replayed_exact"] == 1
    assert report["summary"]["registered_typed_plan_replayed_exact"] == 0
    assert report["summary"]["unregistered_plan_exact_rows"] == 1
    assert report["rows"][0]["unregistered_query_signatures"] == ["incorporation_jurisdiction/2"]


def test_typed_plan_replay_uses_top_level_run_json_when_compile_root_absent(tmp_path):
    compile_path = tmp_path / "compile.json"
    compile_path.write_text(
        json.dumps({"source_compile": {"facts": ["event_date(event_a, may_20_2023)."], "rules": []}}),
        encoding="utf-8",
    )
    qa_path = tmp_path / "qa.json"
    qa_path.write_text(
        json.dumps(
            {
                "run_json": str(compile_path),
                "rows": [
                    {
                        "id": "q001",
                        "reference_answer": "may_20_2023",
                        "reference_judge": {"verdict": "exact"},
                        "queries": ["event_date(Event, Date)."],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path])

    assert report["summary"]["typed_plan_replayed_exact"] == 1
    assert report["rows"][0]["compile_json"] == str(compile_path)


def test_typed_plan_replay_replays_deterministic_typed_inventory_composition(tmp_path):
    compile_dir = tmp_path / "compile" / "fixture_a"
    compile_dir.mkdir(parents=True)
    (compile_dir / "compile.json").write_text(
        json.dumps(
            {
                "source_compile": {
                    "facts": [
                        "claim_range(set_a, 1, 2, contested_claims).",
                        "claim_range(set_a, 4, 4, contested_claims).",
                    ],
                    "rules": [],
                }
            }
        ),
        encoding="utf-8",
    )
    qa_path = tmp_path / "qa.json"
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "fixture": "fixture_a",
                        "id": "q001",
                        "reference_answer": "1-2, 4",
                        "reference_judge": {"verdict": "exact"},
                        "queries": [
                            "claim_range(SetId, Start, End, contested_claims).",
                            "typed_list_range_inventory_composition(SetId, RenderedInventory).",
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path], compile_root=tmp_path / "compile")

    assert report["summary"]["typed_plan_replayed_exact"] == 1
    assert report["rows"][0]["status"] == "all_queries_success"
    assert report["rows"][0]["replay_results"][1]["derived"] is True
    assert report["rows"][0]["replay_results"][1]["row_count"] == 1


def test_typed_plan_replay_replays_deterministic_legal_citation_composition(tmp_path):
    compile_dir = tmp_path / "compile" / "fixture_a"
    compile_dir.mkdir(parents=True)
    (compile_dir / "compile.json").write_text(
        json.dumps(
            {
                "source_compile": {
                    "facts": [
                        "legal_citation_detail(sub_a, n_y_exec_law_63_12, compliance_standard, agreement_5).",
                        "legal_citation_detail(sub_a, n_y_gen_bus_law_349, compliance_standard, agreement_5_7).",
                        "legal_citation_detail(sub_a, future_amendments_to_foregoing_laws, amendment_scope, direct).",
                    ],
                    "rules": [],
                }
            }
        ),
        encoding="utf-8",
    )
    qa_path = tmp_path / "qa.json"
    qa_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "fixture": "fixture_a",
                        "id": "q001",
                        "reference_answer": "Executive Law 63(12), GBL 349, and future amendments",
                        "reference_judge": {"verdict": "exact"},
                        "queries": [
                            "legal_citation_detail(Relaxed1, Citation, Relaxed3, Relaxed4).",
                            "typed_legal_citation_inventory_composition(Subject, RoleGroup, ScopeGroup, CitationAtoms).",
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_files=[qa_path], compile_root=tmp_path / "compile")

    assert report["summary"]["typed_plan_replayed_exact"] == 1
    assert report["rows"][0]["status"] == "all_queries_success"
    assert report["rows"][0]["replay_results"][1]["derived"] is True
    assert report["rows"][0]["replay_results"][1]["row_count"] >= 1

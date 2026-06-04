import json
from pathlib import Path

from scripts.build_compile_fact_judged_qa import (
    _parse_domain_lens_bundles,
    build_bundle,
    build_run_payload,
    write_bundle,
)


def test_build_compile_fact_judged_qa_exact_partial_miss_and_forbidden(tmp_path: Path) -> None:
    fixture_root = tmp_path / "fixtures"
    fixture_dir = fixture_root / "fixture_a"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "expected_facts.pl").write_text(
        "\n".join(
            [
                "fda_warning_letter(Letter, cder, apothecary_pharma_llc, v_2025_12_01, SrcLetter).",
                "fda_correspondence_party(Letter, Recipient, recipient, rechon_life_science_ab, SrcRecipient).",
                "fda_correspondence_party(Letter, ResponsibleOfficial, responsible_official, roland_holmqvist, SrcResponsibleOfficial).",
                "fda_warning_letter(Letter, Center, Firm, Date, Src).",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (fixture_dir / "forbidden_facts.pl").write_text(
        "fda_warning_letter(Letter, cber, apothecary_pharma_llc, v_2025_12_01, SrcLetter).\n",
        encoding="utf-8",
    )
    compile_json = tmp_path / "compile.json"
    compile_json.write_text(
        json.dumps(
            {
                "source_compile": {
                    "facts": [
                        "fda_warning_letter(wl_717972, cder, apothecary_pharma_llc, v_2025_12_01, source_url).",
                        "fda_correspondence_party(wl_717972, roland_holmqvist, recipient, roland_holmqvist, direct).",
                        "fda_warning_letter(wl_999999, cber, apothecary_pharma_llc, v_2025_12_01, source_url).",
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    payload = build_run_payload(
        fixture_root=fixture_root,
        fixture_id="fixture_a",
        run_id="run1",
        compile_json=compile_json,
        created_utc="2026-06-04T00:00:00Z",
    )

    assert payload["verdict_summary"] == {"exact": 1, "miss": 2, "partial": 1}
    assert payload["forbidden_emissions"] == [
        {
            "forbidden_fact": "fda_warning_letter(Letter, cber, apothecary_pharma_llc, v_2025_12_01, SrcLetter).",
            "compiled_fact": "fda_warning_letter(wl_999999, cber, apothecary_pharma_llc, v_2025_12_01, source_url).",
        }
    ]
    assert payload["unexpected_same_signature_emissions"] == [
        "fda_correspondence_party(wl_717972, roland_holmqvist, recipient, roland_holmqvist, direct)."
    ]

    rows = {row["id"].rsplit("__", 1)[-1]: row for row in payload["rows"]}
    assert rows["r001"]["reference_judge"]["verdict"] == "exact"
    assert rows["r001"]["query_results"][0]["result"]["rows"][0]["Letter"] == "wl_717972"
    assert rows["r002"]["reference_judge"]["verdict"] == "partial"
    assert "oracle 'rechon_life_science_ab' vs compile 'roland_holmqvist'" in rows["r002"]["reference_judge"]["rationale"]
    assert rows["r003"]["reference_judge"]["verdict"] == "miss"
    assert rows["r004"]["reference_judge"]["verdict"] == "miss"
    assert "all-variable facts are not answer-bearing" in rows["r004"]["reference_judge"]["rationale"]


def test_build_compile_fact_judged_qa_applies_typed_domain_reducers(tmp_path: Path) -> None:
    fixture_root = tmp_path / "fixtures"
    fixture_dir = fixture_root / "fixture_sec"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "expected_facts.pl").write_text(
        "sec_registrant_identifier(Filing, servicenow_inc, exchange_name, exchange_new_york_stock_exchange, SrcExchange).\n",
        encoding="utf-8",
    )
    compile_json = tmp_path / "compile.json"
    compile_json.write_text(
        json.dumps(
            {
                "source_compile": {
                    "facts": [
                        "sec_registrant_identifier(filing_sec_8k_servicenow_20251223, servicenow_inc, exchange_name, exchange_nyse, direct)."
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    payload = build_run_payload(
        fixture_root=fixture_root,
        fixture_id="fixture_sec",
        run_id="run1",
        compile_json=compile_json,
        created_utc="2026-06-04T00:00:00Z",
    )

    assert payload["domain_reducers_applied"] is True
    assert payload["domain_reducer_reports"]["sec_identifier_value_atom_reduction"]["reduction_count"] == 1
    assert payload["verdict_summary"] == {"exact": 1}
    assert payload["rows"][0]["answer"] == (
        "sec_registrant_identifier("
        "filing_sec_8k_servicenow_20251223, servicenow_inc, exchange_name, "
        "exchange_new_york_stock_exchange, direct)."
    )


def test_build_compile_fact_judged_qa_writes_bundle(tmp_path: Path) -> None:
    fixture_root = tmp_path / "fixtures"
    fixture_dir = fixture_root / "fixture_a"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "expected_facts.pl").write_text(
        "fda_warning_letter(Letter, cder, apothecary_pharma_llc, v_2025_12_01, SrcLetter).\n",
        encoding="utf-8",
    )
    compile_json = tmp_path / "compile.json"
    compile_json.write_text(
        json.dumps(
            {
                "source_compile": {
                    "facts": [
                        "fda_warning_letter(wl_717972, cder, apothecary_pharma_llc, v_2025_12_01, source_url)."
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    bundle = build_bundle(
        fixture_root=fixture_root,
        run_specs=[
            {
                "fixture_id": "fixture_a",
                "run_id": "run1",
                "compile_json": str(compile_json),
            }
        ],
        created_utc="2026-06-04T00:00:00Z",
    )
    out_dir = tmp_path / "out"

    write_bundle(bundle=bundle, out_dir=out_dir)

    qa_file = out_dir / "fixture_a__run1__judged_qa.json"
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    qa = json.loads(qa_file.read_text(encoding="utf-8"))

    assert manifest["schema"] == "prethinker.judged_qa_bundle.v1"
    assert manifest["files"] == ["fixture_a__run1__judged_qa.json"]
    assert manifest["verdict_summary_by_file"]["fixture_a__run1__judged_qa.json"] == {"exact": 1}
    assert manifest["unexpected_same_signature_summary_by_fixture"]["fixture_a"] == {
        "runs_seen": 1,
        "unexpected_same_signature_ge_1": 0,
        "unexpected_same_signature_ge_2": 0,
    }
    assert manifest["support_summary_by_fixture"]["fixture_a"] == {
        "exact_support_ge_1": 1,
        "exact_support_ge_2": 0,
        "miss_support_ge_1": 0,
        "partial_support_ge_1": 0,
        "reference_count": 1,
        "runs_seen": 1,
        "zero_exact_support": 0,
    }
    assert qa["rows"][0]["queries"] == [
        "fda_warning_letter(Letter, cder, apothecary_pharma_llc, v_2025_12_01, SrcLetter)."
    ]


def test_parse_domain_lens_bundle_discovers_union_runs(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    for run_id in ["run2", "run1"]:
        run_dir = bundle / "unions" / run_id
        run_dir.mkdir(parents=True)
        (run_dir / "compile.json").write_text("{}", encoding="utf-8")

    specs = _parse_domain_lens_bundles([f"fixture_a={bundle}"])

    assert specs == [
        {
            "compile_json": str(bundle / "unions" / "run1" / "compile.json"),
            "fixture_id": "fixture_a",
            "run_id": "run1",
        },
        {
            "compile_json": str(bundle / "unions" / "run2" / "compile.json"),
            "fixture_id": "fixture_a",
            "run_id": "run2",
        },
    ]


def test_parse_domain_lens_bundle_discovers_flat_union_files(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    union_dir = bundle / "unions"
    union_dir.mkdir(parents=True)
    for name in [
        "domain_bootstrap_file_20260603_fixture-run2_model.json",
        "domain_bootstrap_file_20260603_fixture-run1_model.json",
    ]:
        (union_dir / name).write_text("{}", encoding="utf-8")

    specs = _parse_domain_lens_bundles([f"fixture_a={bundle}"])

    assert specs == [
        {
            "compile_json": str(union_dir / "domain_bootstrap_file_20260603_fixture-run1_model.json"),
            "fixture_id": "fixture_a",
            "run_id": "run1",
        },
        {
            "compile_json": str(union_dir / "domain_bootstrap_file_20260603_fixture-run2_model.json"),
            "fixture_id": "fixture_a",
            "run_id": "run2",
        },
    ]

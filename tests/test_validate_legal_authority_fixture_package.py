from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

from scripts.validate_legal_authority_fixture_package import build_report
from src.legal_authority_verification import facts_text, verify_legal_authorities


def test_validate_legal_authority_fixture_package_accepts_clean_public_batch(tmp_path: Path) -> None:
    package = _write_package(tmp_path)

    report = build_report(package_path=package)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["fixture_count"] == 3
    assert report["summary"]["matched_expected_fact_count"] == report["summary"]["expected_fact_count"]
    assert report["summary"]["matched_forbidden_fact_count"] == 0
    assert report["summary"]["false_verified"] == 0
    assert report["summary"]["citation_mentions"] == 9
    assert report["summary"]["metadata_checks"] == 45
    assert report["summary"]["metadata_match"] == 45
    assert report["summary"]["metadata_mismatch"] == 0
    signatures = {row["signature"]: row for row in report["summary"]["fact_signature_summary"]}
    assert signatures["legal_authority_metadata_check/5"] == {
        "signature": "legal_authority_metadata_check/5",
        "expected": 45,
        "matched_expected": 45,
        "forbidden": 0,
        "matched_forbidden": 0,
    }
    assert signatures["legal_citation_mention/5"] == {
        "signature": "legal_citation_mention/5",
        "expected": 9,
        "matched_expected": 9,
        "forbidden": 0,
        "matched_forbidden": 0,
    }
    assert signatures["legal_quote_span_match/5"] == {
        "signature": "legal_quote_span_match/5",
        "expected": 6,
        "matched_expected": 6,
        "forbidden": 3,
        "matched_forbidden": 0,
    }
    assert signatures["legal_pin_cite_check/5"] == {
        "signature": "legal_pin_cite_check/5",
        "expected": 6,
        "matched_expected": 6,
        "forbidden": 3,
        "matched_forbidden": 0,
    }
    assert all(row["errors"] == [] for row in report["fixtures"])


def test_validate_legal_authority_fixture_package_rejects_model_output_oracle(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    metadata_path = package / "clean_legal_filing_002" / "source_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["oracle_independence"]["used_model_output"] = True
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = build_report(package_path=package)

    assert report["summary"]["status"] == "fail"
    assert "oracle_independence_used_model_output_true" in report["fixtures"][1]["errors"]


def test_validate_legal_authority_fixture_package_rejects_expected_fact_miss(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    expected_path = package / "clean_legal_filing_003" / "expected_facts.pl"
    with expected_path.open("a", encoding="utf-8") as handle:
        handle.write("legal_authority_resolution(mention_999, cite_1_us_1, resolved, auth_fake, source_line_99).\n")

    report = build_report(package_path=package)

    assert report["summary"]["status"] == "fail"
    assert "missing_expected_facts:1" in report["fixtures"][2]["errors"]


def test_validate_legal_authority_fixture_package_requires_four_forbidden_traps(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    forbidden_path = package / "clean_legal_filing_001" / "forbidden_facts.pl"
    forbidden_path.write_text(
        "legal_authority_resolution(mention_001, cite_576_us_644, unresolved, authority_not_found, source_line_5).\n",
        encoding="utf-8",
    )

    report = build_report(package_path=package)

    assert report["summary"]["status"] == "fail"
    assert "forbidden_facts_expected_at_least_4_got_1" in report["fixtures"][0]["errors"]


def test_validate_legal_authority_fixture_package_rejects_claim_bearing_support_rows(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    expected_path = package / "clean_legal_filing_001" / "expected_facts.pl"
    with expected_path.open("a", encoding="utf-8") as handle:
        handle.write(
            "legal_support_assessment(prop_001, auth_obergefell_576_us_644, reviewed_support, "
            "independent_review_recorded, source_line_5).\n"
        )
        handle.write(
            "legal_proposition_support_boundary(mention_001, prop_001, reviewed_support, "
            "no_review_required, source_line_5).\n"
        )

    report = build_report(package_path=package)

    assert report["summary"]["status"] == "fail"
    errors = report["fixtures"][0]["errors"]
    assert "expected_facts.pl:line_31:tier2_support_assessment_not_allowed_clean_public" in errors
    assert "expected_facts.pl:line_32:proposition_boundary_must_abstain_clean_public" in errors


def test_validate_legal_authority_fixture_package_requires_expected_authority_text_receipts(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    expected_path = package / "clean_legal_filing_001" / "expected_facts.pl"
    expected_path.write_text(
        "\n".join(
            line
            for line in expected_path.read_text(encoding="utf-8").splitlines()
            if not line.startswith("legal_authority_text_source(")
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_report(package_path=package)

    assert report["summary"]["status"] == "fail"
    assert "expected_facts_missing_authority_text_source_receipt" in report["fixtures"][0]["errors"]


def test_validate_legal_authority_fixture_package_requires_forbidden_authority_text_trap(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    forbidden_path = package / "clean_legal_filing_001" / "forbidden_facts.pl"
    forbidden_lines = [
        line
        for line in forbidden_path.read_text(encoding="utf-8").splitlines()
        if not line.startswith("legal_authority_text_source(")
    ]
    forbidden_lines.append(
        "legal_authority_resolution(mention_999, cite_1_us_1, unresolved, authority_not_found, source_line_99)."
    )
    forbidden_path.write_text("\n".join(forbidden_lines) + "\n", encoding="utf-8")

    report = build_report(package_path=package)

    assert report["summary"]["status"] == "fail"
    assert "forbidden_facts_missing_authority_text_source_trap" in report["fixtures"][0]["errors"]


def test_validate_legal_authority_fixture_package_rejects_unknown_metadata_authority_source(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    metadata_path = package / "clean_legal_filing_001" / "source_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["authority_sources"][0]["authority_id"] = "auth_unknown_1_us_1"
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = build_report(package_path=package)

    assert report["summary"]["status"] == "fail"
    assert (
        "source_metadata_authority_source_1:authority_id_not_in_inventory:auth_unknown_1_us_1"
        in report["fixtures"][0]["errors"]
    )


def test_validate_legal_authority_fixture_package_rejects_metadata_citation_mismatch(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    metadata_path = package / "clean_legal_filing_001" / "source_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["authority_sources"][0]["canonical_citation"] = "1 U.S. 1"
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = build_report(package_path=package)

    assert report["summary"]["status"] == "fail"
    assert "source_metadata_authority_source_1:canonical_citation_mismatch" in report["fixtures"][0]["errors"]


def test_validate_legal_authority_fixture_package_accepts_federal_reporter_inventory(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    inventory_path = package / "clean_legal_filing_001" / "authority_inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory["authorities"][0]["canonical_citation"] = "12 F.3d 34"
    inventory["authorities"][0]["reporter"] = "F.3d"
    inventory["authorities"][0]["volume"] = "12"
    inventory["authorities"][0]["page"] = "34"
    inventory_path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    metadata_path = package / "clean_legal_filing_001" / "source_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["authority_sources"][0]["canonical_citation"] = "12 F.3d 34"
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = build_report(package_path=package)

    assert "authority_1:reporter_not_allowed:F.3d" not in report["fixtures"][0]["errors"]


def test_validate_legal_authority_fixture_package_rejects_unknown_reporter_inventory(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    inventory_path = package / "clean_legal_filing_001" / "authority_inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory["authorities"][0]["canonical_citation"] = "12 Umbrella 34"
    inventory["authorities"][0]["reporter"] = "Umbrella"
    inventory["authorities"][0]["volume"] = "12"
    inventory["authorities"][0]["page"] = "34"
    inventory_path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    metadata_path = package / "clean_legal_filing_001" / "source_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["authority_sources"][0]["canonical_citation"] = "12 Umbrella 34"
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = build_report(package_path=package)

    assert "authority_1:reporter_not_allowed:Umbrella" in report["fixtures"][0]["errors"]


def test_validate_legal_authority_fixture_package_accepts_zip_shape(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    zip_path = tmp_path / "legal_authority_clean_public_filings_20260606_01.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for path in package.rglob("*"):
            if path.is_file():
                archive.write(path, arcname=str(Path(package.name) / path.relative_to(package)))

    report = build_report(package_path=zip_path)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["fixture_count"] == 3
    assert any(row["signature"] == "legal_citation_mention/5" for row in report["summary"]["fact_signature_summary"])


def test_validate_legal_authority_fixture_package_accepts_known_sanction_shape(tmp_path: Path) -> None:
    package = _write_package(tmp_path)
    _convert_package_to_known_sanction_shape(package)

    report = build_report(
        package_path=package,
        fixture_class="known_hallucination_or_sanction_filings",
    )

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["fixture_class"] == "known_hallucination_or_sanction_filings"


def test_validate_legal_authority_fixture_package_requires_sanction_source_for_known_sanction_shape(
    tmp_path: Path,
) -> None:
    package = _write_package(tmp_path)
    _convert_package_to_known_sanction_shape(package)
    (package / "clean_legal_filing_001" / "sanction_or_correction_source.md").unlink()

    report = build_report(
        package_path=package,
        fixture_class="known_hallucination_or_sanction_filings",
    )

    assert report["summary"]["status"] == "fail"
    assert "missing_sanction_or_correction_source.md" in report["fixtures"][0]["errors"]


def test_validate_legal_authority_fixture_package_rejects_wrong_known_sanction_source_kind(
    tmp_path: Path,
) -> None:
    package = _write_package(tmp_path)
    _convert_package_to_known_sanction_shape(package)
    manifest_path = package / "clean_legal_filing_001" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source_kind"] = "public_legal_filing_excerpt"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = build_report(
        package_path=package,
        fixture_class="known_hallucination_or_sanction_filings",
    )

    assert report["summary"]["status"] == "fail"
    assert (
        "manifest_source_kind_not_known_hallucination_or_sanction_filing_excerpt"
        in report["fixtures"][0]["errors"]
    )


def _write_package(tmp_path: Path) -> Path:
    package = tmp_path / "legal_authority_clean_public_filings_20260606_01"
    package.mkdir()
    for index in range(1, 4):
        fixture_id = f"clean_legal_filing_{index:03d}"
        _write_fixture(package / fixture_id, fixture_id=fixture_id)
    return package


def _convert_package_to_known_sanction_shape(package: Path) -> None:
    for fixture in package.iterdir():
        if not fixture.is_dir():
            continue
        manifest_path = fixture / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["source_kind"] = "known_hallucination_or_sanction_filing_excerpt"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (fixture / "sanction_or_correction_source.md").write_text(
            "# Sanction Or Correction Source\n\n"
            "Public correction source says the legal-authority issue was independently identified.\n",
            encoding="utf-8",
        )


def _write_fixture(path: Path, *, fixture_id: str) -> None:
    path.mkdir()
    source = """# Clean Public Legal Filing Fixture

## Public Filing Excerpt

Obergefell v. Hodges, 576 U.S. 644, 675 (2015), states that "same-sex couples may exercise the fundamental right to marry."

Brown v. Board of Education, 347 U.S. 483, 495 (1954), states that "Separate educational facilities are inherently unequal."

Miranda v. Arizona, 384 U.S. 436 (1966), is also cited.
"""
    (path / "source.md").write_text(source, encoding="utf-8")
    (path / "authority_inventory.json").write_text(
        json.dumps(_authority_inventory(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (path / "source_metadata.json").write_text(
        json.dumps(
            {
                "fixture_id": fixture_id,
                "source_title": f"Clean public legal filing fixture {fixture_id}",
                "source_url": "https://example.test/public-filing",
                "source_court_or_body": "Test court",
                "source_docket_or_case": "Test docket",
                "source_date": "2026-06-06",
                "excerpt_method": "faithful_public_excerpt_or_transcription",
                "omitted_source_scope": "",
                "authority_sources": [
                    {
                        "authority_id": "auth_obergefell_576_us_644",
                        "canonical_citation": "576 U.S. 644",
                        "authority_text_url": "https://example.test/obergefell",
                        "page_or_span_used": "page_675",
                        "notes": "",
                    }
                ],
                "oracle_independence": {
                    "used_model_output": False,
                    "review_basis": "source_and_authority_inventory_only",
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (path / "manifest.json").write_text(
        json.dumps(
            {
                "fixture_id": fixture_id,
                "domain_profile": "legal_authority_verification_v1",
                "schema_version": "compile_micro_fixture_manifest_v1",
                "purpose": "Clean public legal filing baseline for deterministic legal authority verification.",
                "source_kind": "public_legal_filing_excerpt",
                "files": {
                    "source": "source.md",
                    "expected_facts": "expected_facts.pl",
                    "forbidden_facts": "forbidden_facts.pl",
                },
                "claim_status": "research_fixture_not_legal_advice",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    report = verify_legal_authorities(
        source_path=path / "source.md",
        authority_inventory_path=path / "authority_inventory.json",
        document_id=fixture_id,
    )
    (path / "expected_facts.pl").write_text(facts_text(report), encoding="utf-8")
    (path / "forbidden_facts.pl").write_text(
        "\n".join(
            [
                "legal_authority_resolution(mention_001, cite_576_us_644, unresolved, authority_not_found, source_line_5).",
                "legal_quote_span_match(quote_001, auth_obergefell_576_us_644, no_match, no_match, authority_inventory).",
                "legal_pin_cite_check(mention_001, auth_obergefell_576_us_644, page_675, quote_outside_pin, source_line_5).",
                "legal_authority_text_source(auth_obergefell_576_us_644, page_675, authority_unavailable, no_digest, authority_inventory).",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (path / "review_notes.md").write_text(
        "# Review Notes\n\nSynthetic unit-test package for the intake validator.\n",
        encoding="utf-8",
    )


def _authority_inventory() -> dict[str, object]:
    return {
        "schema_version": "legal_authority_inventory_v1",
        "authorities": [
            {
                "authority_id": "auth_obergefell_576_us_644",
                "canonical_citation": "576 U.S. 644",
                "case_name": "Obergefell v. Hodges",
                "court": "Supreme Court of the United States",
                "year": "2015",
                "reporter": "U.S.",
                "volume": "576",
                "page": "644",
                "pages": {
                    "675": "The Court now holds that same-sex couples may exercise the fundamental right to marry."
                },
            },
            {
                "authority_id": "auth_brown_347_us_483",
                "canonical_citation": "347 U.S. 483",
                "case_name": "Brown v. Board of Education",
                "court": "Supreme Court of the United States",
                "year": "1954",
                "reporter": "U.S.",
                "volume": "347",
                "page": "483",
                "pages": {
                    "495": "Separate educational facilities are inherently unequal."
                },
            },
            {
                "authority_id": "auth_miranda_384_us_436",
                "canonical_citation": "384 U.S. 436",
                "case_name": "Miranda v. Arizona",
                "court": "Supreme Court of the United States",
                "year": "1966",
                "reporter": "U.S.",
                "volume": "384",
                "page": "436",
                "pages": {
                    "444": "The prosecution may not use statements stemming from custodial interrogation unless it demonstrates procedural safeguards."
                },
            },
        ],
    }

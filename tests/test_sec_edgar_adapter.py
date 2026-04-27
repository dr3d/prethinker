from __future__ import annotations

import json
from pathlib import Path

import pytest

from adapters.sec_edgar.client import SecEdgarClient, archive_document_url
from adapters.sec_edgar.normalize import normalize_contract_excerpt, normalize_submission_filing
from adapters.sec_edgar.predicates import sec_contract_predicate_signatures, semantic_ir_contracts
from adapters.sec_edgar.to_harness import record_to_harness_case
from src.domain_profiles import load_domain_profile_catalog, load_profile_package, profile_package_contracts


ROOT = Path(__file__).resolve().parents[1]


def test_sec_contracts_profile_is_cataloged_and_contracts_load():
    catalog = load_domain_profile_catalog(ROOT / "modelfiles" / "domain_profile_catalog.v0.json")
    profile = load_profile_package("sec_contracts@v0", catalog)
    assert profile["profile_id"] == "sec_contracts@v0"
    contracts = profile_package_contracts(profile)
    signatures = {row["signature"] for row in contracts}
    assert "obligation/3" in signatures
    assert "subject_to/2" in signatures
    assert "effective_on/2" in signatures
    assert "party_to_contract/3" in signatures


def test_sec_client_requires_user_agent_for_live_calls(tmp_path, monkeypatch):
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    client = SecEdgarClient(cache_dir=tmp_path)
    with pytest.raises(RuntimeError, match="SEC_USER_AGENT"):
        client.submissions("320193")


def test_archive_document_url_matches_sec_archive_shape():
    url = archive_document_url(
        cik="0000320193",
        accession_number="0000320193-24-000123",
        primary_document="aapl-20240928.htm",
    )
    assert url == "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm"


def test_normalize_submission_filing_extracts_recent_metadata():
    submission = {
        "name": "Example Corp",
        "cik": "1234567",
        "sic": "7372",
        "tickers": ["EXMP"],
        "filings": {
            "recent": {
                "accessionNumber": ["0001234567-24-000001"],
                "form": ["8-K"],
                "filingDate": ["2024-05-01"],
                "reportDate": ["2024-04-30"],
                "primaryDocument": ["exmp-20240501.htm"],
            }
        },
    }
    record = normalize_submission_filing(submission, 0)
    assert record.source == "sec_edgar"
    assert record.source_kind == "filing"
    assert record.company_name == "Example Corp"
    assert record.cik == "1234567"
    assert record.accession_number == "0001234567-24-000001"
    assert record.form_type == "8-K"
    assert record.filing_date == "2024-05-01"
    assert record.provenance_url.endswith("/1234567/000123456724000001/exmp-20240501.htm")


def test_contract_excerpt_to_harness_includes_obligation_boundaries():
    record = normalize_contract_excerpt(
        source_id="exhibit-10-1",
        company_name="Example Corp",
        cik="1234567",
        accession_number="0001234567-24-000001",
        form_type="8-K",
        filing_date="2024-05-01",
        primary_document="ex10-1.htm",
        text_excerpt="The borrower shall repay the loan after the maturity date.",
    )
    case = record_to_harness_case(record, index=3)
    payload = case.to_dict()
    assert payload["id"] == "sec_contract_excerpt_0003"
    assert payload["domain"] == "sec_contracts"
    assert "obligation/3" in payload["allowed_predicates"]
    assert any(row["signature"] == "subject_to/2" for row in payload["predicate_contracts"])
    assert payload["admission_expectations"]["must_preserve_obligation_not_fact"] is True


def test_sec_predicate_contracts_have_expected_shapes():
    signatures = sec_contract_predicate_signatures()
    contracts = semantic_ir_contracts()
    assert "party_to_contract/3" in signatures
    obligation = next(row for row in contracts if row["signature"] == "obligation/3")
    assert obligation["arguments"] == ["obligated_party", "obligation_content", "source"]


def test_synthetic_sec_seed_fixture_is_jsonl_with_contracts():
    path = ROOT / "datasets" / "sec_edgar" / "samples" / "sec_contracts_synthetic_5.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 5
    assert all(row["domain"] == "sec_contracts" for row in rows)
    assert all(row["predicate_contracts"] for row in rows)
    assert any(row["admission_expectations"].get("must_preserve_condition_not_event") for row in rows)

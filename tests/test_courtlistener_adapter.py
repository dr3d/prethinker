from __future__ import annotations

import json
from pathlib import Path

import pytest

from adapters.courtlistener.client import CourtListenerClient
from adapters.courtlistener.normalize import normalize_opinion_record
from adapters.courtlistener.predicates import legal_predicate_signatures, semantic_ir_contracts
from adapters.courtlistener.to_harness import record_to_harness_case
from src.domain_profiles import load_domain_profile_catalog, load_profile_package, profile_package_contracts


ROOT = Path(__file__).resolve().parents[1]


def test_legal_courtlistener_profile_is_cataloged_and_contracts_load():
    catalog = load_domain_profile_catalog(ROOT / "modelfiles" / "domain_profile_catalog.v0.json")
    profile = load_profile_package("legal_courtlistener@v0", catalog)
    assert profile["profile_id"] == "legal_courtlistener@v0"
    contracts = profile_package_contracts(profile)
    signatures = {row["signature"] for row in contracts}
    assert "claim_made/4" in signatures
    assert "finding/4" in signatures
    assert "cites_case/2" in signatures
    assert "party_to_case/3" in signatures


def test_courtlistener_client_requires_token_for_live_calls(tmp_path, monkeypatch):
    monkeypatch.delenv("COURTLISTENER_API_TOKEN", raising=False)
    client = CourtListenerClient(cache_dir=tmp_path)
    with pytest.raises(RuntimeError, match="COURTLISTENER_API_TOKEN"):
        client.search(q="breach of lease")


def test_normalize_opinion_record_tolerates_search_result_shape():
    raw = {
        "id": 123,
        "caseName": "Doe v. Acme",
        "court": {"full_name": "United States Court of Appeals"},
        "dateFiled": "2024-03-03",
        "judge": "Jane Smith",
        "citation": [{"cite": "123 F.4th 456"}],
        "snippet": "<b>The complaint alleged breach.</b>",
        "absolute_url": "/opinion/123/doe-v-acme/",
    }
    record = normalize_opinion_record(raw)
    assert record.source == "courtlistener"
    assert record.source_kind == "opinion"
    assert record.source_id == "123"
    assert record.title == "Doe v. Acme"
    assert record.court == "United States Court of Appeals"
    assert record.date_filed == "2024-03-03"
    assert record.judges == ["Jane Smith"]
    assert record.citations == ["123 F.4th 456"]
    assert "complaint alleged breach" in record.text_excerpt
    assert record.provenance_url == "https://www.courtlistener.com/opinion/123/doe-v-acme/"


def test_record_to_harness_case_includes_legal_contracts_and_boundaries():
    record = normalize_opinion_record(
        {
            "id": "abc",
            "caseName": "Doe v. Acme",
            "court": "D. Fiction",
            "dateFiled": "2024-03-03",
            "snippet": "The complaint alleged breach, but the court found only timeliness.",
        }
    )
    case = record_to_harness_case(record, index=7)
    payload = case.to_dict()
    assert payload["id"] == "courtlistener_opinion_0007"
    assert payload["domain"] == "legal_courtlistener"
    assert "claim_made/4" in payload["allowed_predicates"]
    assert any(row["signature"] == "finding/4" for row in payload["predicate_contracts"])
    assert payload["admission_expectations"]["must_preserve_claim_not_fact"] is True


def test_legal_predicate_contracts_have_expected_shapes():
    signatures = legal_predicate_signatures()
    contracts = semantic_ir_contracts()
    assert "party_to_case/3" in signatures
    party = next(row for row in contracts if row["signature"] == "party_to_case/3")
    assert party["arguments"] == ["party", "case", "role"]


def test_synthetic_legal_seed_fixture_is_jsonl_with_contracts():
    path = ROOT / "datasets" / "courtlistener" / "samples" / "legal_seed_synthetic_5.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 5
    assert all(row["domain"] == "legal_courtlistener" for row in rows)
    assert all(row["predicate_contracts"] for row in rows)
    assert any(row["admission_expectations"].get("must_preserve_citation_not_endorsement") for row in rows)

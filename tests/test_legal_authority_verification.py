from __future__ import annotations

import json
import urllib.parse
from pathlib import Path

from adapters.courtlistener.client import CourtListenerClient
from src.legal_authority_resolvers import (
    CitationResolution,
    CourtListenerCitationLookupResolver,
    LocalAuthorityInventoryResolver,
)
from src.legal_authority_verification import facts_text, main, render_markdown, verify_legal_authorities


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "datasets" / "compile_micro_fixtures" / "legal_authority_verification_micro_v1"
FIXTURE_V2 = ROOT / "datasets" / "compile_micro_fixtures" / "legal_authority_verification_micro_v2"
FIXTURE_V3 = ROOT / "datasets" / "compile_micro_fixtures" / "legal_authority_verification_micro_v3"
FIXTURE_V4 = ROOT / "datasets" / "compile_micro_fixtures" / "legal_authority_verification_micro_v4"
FIXTURE_V5 = ROOT / "datasets" / "compile_micro_fixtures" / "legal_authority_verification_micro_v5"
FIXTURE_V6 = ROOT / "datasets" / "compile_micro_fixtures" / "legal_authority_verification_micro_v6"


def test_legal_authority_micro_fixture_catches_hallucination_shapes() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE / "source.md",
        authority_inventory_path=FIXTURE / "authority_inventory.json",
    )

    assert report["summary"]["citation_mentions"] == 5
    assert report["summary"]["verified_mentions"] == 1
    assert report["summary"]["blocked_mentions"] == 3
    assert report["summary"]["review_required_mentions"] == 1
    assert report["summary"]["resolved"] == 4
    assert report["summary"]["unresolved"] == 1
    assert report["summary"]["metadata_checks"] == 20
    assert report["summary"]["metadata_match"] == 20
    assert report["summary"]["metadata_mismatch"] == 0
    assert report["summary"]["quote_mismatch"] == 1
    assert report["summary"]["pin_mismatch"] == 1
    assert report["summary"]["proposition_boundaries"] == 1
    assert report["summary"]["verification_abstentions"] == 4
    assert report["summary"]["false_verified"] == 0
    assert report["summary"]["document_outcome"] == "review_required"
    assert report["resolver"] == {
        "mode": "local_inventory",
        "class": "LocalAuthorityInventoryResolver",
        "default_local": "yes",
        "provider": "local",
        "external_lookup": "no",
        "inventory_assisted": "yes",
    }

    issues = {row["issue"] for row in report["issues"]}
    assert "unresolved" in issues
    assert "quote_not_found_in_authority" in issues
    assert "quote_outside_cited_pin" in issues
    assert "proposition_support_requires_human_review" in issues

    queries = report["ledger_queries"]
    assert len(queries["which_citations_do_not_resolve"]) == 1
    assert len(queries["which_quotes_cannot_be_found"]) == 1
    assert len(queries["which_pin_cites_do_not_contain_the_quote"]) == 1
    assert len(queries["which_propositions_require_human_review"]) == 1
    assert queries["which_authorities_are_attached_to_propositions"] == [
        {
            "proposition_id": "proposition_005",
            "mention_id": "mention_005",
            "citation": "347 U.S. 483",
            "authority_id": "auth_brown_347_us_483",
            "review_requirement": "human_review_required",
            "support_assessment": "deterministic_abstain",
        }
    ]
    assert queries["can_this_filing_be_certified_citation_clean"] == {
        "citation_clean": False,
        "blocking_issue_count": 3,
        "blocking_issue_types": [
            "quote_not_found_in_authority",
            "quote_outside_cited_pin",
            "unresolved",
        ],
        "review_required_count": 1,
        "answer": "no",
    }


def test_local_authority_inventory_resolver_uses_courtlistener_like_lookup_shape() -> None:
    resolver = LocalAuthorityInventoryResolver.from_path(FIXTURE / "authority_inventory.json")

    resolved = resolver.lookup_citation(citation="576 U.S. 644", start_index=12, end_index=24)
    assert len(resolved.authority_matches) == 1
    assert resolved.lookup_row["status"] == 200
    assert resolved.lookup_row["error_message"] == ""
    assert resolved.lookup_row["start_index"] == 12
    assert resolved.lookup_row["end_index"] == 24
    assert resolved.lookup_row["clusters"][0]["authority_id"] == "auth_obergefell_576_us_644"

    unresolved = resolver.lookup_citation(citation="999 U.S. 999", start_index=3, end_index=15)
    assert unresolved.authority_matches == []
    assert unresolved.lookup_row["status"] == 404
    assert unresolved.lookup_row["error_message"] == "citation_not_found"


def test_legal_authority_verifier_accepts_explicit_resolver_without_inventory_load(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("Brown v. Board of Education, 347 U.S. 483 (1954).", encoding="utf-8")
    inventory = json.loads((FIXTURE / "authority_inventory.json").read_text(encoding="utf-8"))
    brown = next(row for row in inventory["authorities"] if row["authority_id"] == "auth_brown_347_us_483")
    calls = []

    class FakeResolver:
        def lookup_citation(self, *, citation: str, start_index: int, end_index: int) -> CitationResolution:
            calls.append((citation, start_index, end_index))
            return CitationResolution(
                authority_matches=[brown],
                lookup_row={
                    "citation": citation,
                    "normalized_citations": [citation],
                    "start_index": start_index,
                    "end_index": end_index,
                    "status": 200,
                    "error_message": "",
                    "clusters": [
                        {
                            "authority_id": brown["authority_id"],
                            "case_name": brown["case_name"],
                            "canonical_citation": brown["canonical_citation"],
                            "year": brown["year"],
                        }
                    ],
                },
            )

    report = verify_legal_authorities(
        source_path=source,
        authority_inventory_path=tmp_path / "missing_inventory.json",
        document_id="legal_authority_injected_resolver",
        resolver=FakeResolver(),
    )

    assert calls == [("347 U.S. 483", 29, 41)]
    assert report["summary"]["citation_mentions"] == 1
    assert report["summary"]["verified_mentions"] == 1
    assert report["summary"]["false_verified"] == 0


def test_courtlistener_lookup_resolver_maps_lookup_clusters_to_local_inventory() -> None:
    calls = []

    class FakeCourtListenerClient:
        def citation_lookup(self, *, text: str) -> list[dict[str, object]]:
            calls.append(text)
            return [
                {
                    "citation": "576 U.S. 644",
                    "normalized_citations": ["576 U.S. 644"],
                    "start_index": 0,
                    "end_index": 12,
                    "status": 200,
                    "error_message": "",
                    "clusters": [
                        {
                            "id": 576644,
                            "case_name": "Obergefell v. Hodges",
                            "citations": [
                                {
                                    "volume": 576,
                                    "reporter": "U.S.",
                                    "page": "644",
                                }
                            ],
                            "date_filed": "2015-06-26",
                        }
                    ],
                }
            ]

    resolver = CourtListenerCitationLookupResolver.from_inventory_path(
        client=FakeCourtListenerClient(),
        path=FIXTURE / "authority_inventory.json",
    )
    resolved = resolver.lookup_citation(citation="576 U.S. 644", start_index=0, end_index=12)

    assert calls == ["576 U.S. 644"]
    assert resolved.lookup_row["status"] == 200
    assert resolved.lookup_row["clusters"][0]["case_name"] == "Obergefell v. Hodges"
    assert [row["authority_id"] for row in resolved.authority_matches] == ["auth_obergefell_576_us_644"]


def test_courtlistener_lookup_resolver_can_emit_limited_external_authority_without_inventory() -> None:
    class FakeCourtListenerClient:
        def citation_lookup(self, *, text: str) -> list[dict[str, object]]:
            return [
                {
                    "citation": "347 U.S. 483",
                    "normalized_citations": ["347 U.S. 483"],
                    "status": 200,
                    "clusters": [
                        {
                            "id": 347483,
                            "case_name": "Brown v. Board of Education",
                            "citations": [{"volume": 347, "reporter": "U.S.", "page": "483"}],
                            "date_filed": "1954-05-17",
                        }
                    ],
                }
            ]

    resolver = CourtListenerCitationLookupResolver(client=FakeCourtListenerClient())
    resolved = resolver.lookup_citation(citation="347 U.S. 483", start_index=4, end_index=16)

    assert resolved.lookup_row["start_index"] == 4
    assert resolved.lookup_row["end_index"] == 16
    assert resolved.authority_matches == [
        {
            "authority_id": "courtlistener_cluster_347483",
            "canonical_citation": "347 U.S. 483",
            "case_name": "Brown v. Board of Education",
            "court": "",
            "year": "1954",
            "reporter": "U.S.",
            "volume": "347",
            "page": "483",
            "pages": {},
        }
    ]


def test_courtlistener_lookup_resolver_preserves_ambiguity_even_with_one_inventory_match() -> None:
    class FakeCourtListenerClient:
        def citation_lookup(self, *, text: str) -> list[dict[str, object]]:
            return [
                {
                    "citation": "347 U.S. 483",
                    "normalized_citations": ["347 U.S. 483", "347 Fiction 483"],
                    "status": 300,
                    "error_message": "Multiple Choices",
                    "clusters": [
                        {
                            "id": 347483,
                            "case_name": "Brown v. Board of Education",
                            "citations": [{"volume": 347, "reporter": "U.S.", "page": "483"}],
                        },
                        {
                            "id": 909,
                            "case_name": "Example v. Example",
                            "citations": [{"volume": 347, "reporter": "Fiction", "page": "483"}],
                        },
                    ],
                }
            ]

    resolver = CourtListenerCitationLookupResolver.from_inventory_path(
        client=FakeCourtListenerClient(),
        path=FIXTURE / "authority_inventory.json",
    )
    resolved = resolver.lookup_citation(citation="347 U.S. 483", start_index=0, end_index=12)

    assert resolved.lookup_row["status"] == 300
    assert [row["authority_id"] for row in resolved.authority_matches] == [
        "auth_brown_347_us_483",
        "courtlistener_cluster_909",
    ]


def test_external_resolver_throttling_is_unavailable_not_unresolved(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("Brown v. Board of Education, 347 U.S. 483 (1954).", encoding="utf-8")

    class ThrottledResolver:
        def lookup_citation(self, *, citation: str, start_index: int, end_index: int) -> CitationResolution:
            return CitationResolution(
                authority_matches=[],
                lookup_row={
                    "citation": citation,
                    "normalized_citations": [citation],
                    "start_index": start_index,
                    "end_index": end_index,
                    "status": 429,
                    "error_message": "Too many citations requested.",
                    "clusters": [],
                },
            )

    report = verify_legal_authorities(
        source_path=source,
        authority_inventory_path=tmp_path / "missing_inventory.json",
        document_id="legal_authority_throttled_resolver",
        resolver=ThrottledResolver(),
    )

    assert report["mentions"][0]["resolution_status"] == "unavailable"
    assert report["issues"] == [
        {
            "mention_id": "mention_001",
            "issue": "unavailable",
            "reason": "authority_lookup_unavailable",
            "line": 1,
        }
    ]
    assert (
        "legal_verification_abstention("
        "mention_001, authority_resolution, authority_lookup_unavailable, source_line_1)."
    ) in report["facts"]


def test_legal_authority_micro_fixture_v2_catches_metadata_ambiguity_and_unavailable_text() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE_V2 / "source.md",
        authority_inventory_path=FIXTURE_V2 / "authority_inventory.json",
        document_id="legal_authority_micro_v2",
    )

    assert report["summary"]["citation_mentions"] == 4
    assert report["summary"]["verified_mentions"] == 0
    assert report["summary"]["blocked_mentions"] == 4
    assert report["summary"]["review_required_mentions"] == 0
    assert report["summary"]["resolved"] == 3
    assert report["summary"]["ambiguous"] == 1
    assert report["summary"]["metadata_checks"] == 15
    assert report["summary"]["metadata_match"] == 13
    assert report["summary"]["metadata_mismatch"] == 2
    assert report["summary"]["quote_claims"] == 1
    assert report["summary"]["authority_text_sources"] == 2
    assert report["summary"]["authority_text_available_sources"] == 1
    assert report["summary"]["authority_text_unavailable_sources"] == 1
    assert report["summary"]["verification_abstentions"] == 2
    assert report["summary"]["false_verified"] == 0
    assert report["summary"]["document_outcome"] == "review_required"

    issues = {row["issue"] for row in report["issues"]}
    assert "metadata_mismatch" in issues
    assert "ambiguous" in issues
    assert "authority_text_unavailable" in issues

    queries = report["ledger_queries"]
    assert len(queries["which_citations_do_not_resolve"]) == 1
    assert len(queries["which_citations_are_ambiguous"]) == 1
    assert len(queries["which_cases_have_metadata_mismatches"]) == 2
    assert len(queries["which_authority_text_is_unavailable"]) == 1
    assert len(queries["which_authority_text_sources_were_used"]) == 2
    assert queries["can_this_filing_be_certified_citation_clean"] == {
        "citation_clean": False,
        "blocking_issue_count": 4,
        "blocking_issue_types": [
            "ambiguous",
            "authority_text_unavailable",
            "metadata_mismatch",
        ],
        "review_required_count": 0,
        "answer": "no",
    }


def test_legal_authority_micro_fixture_v3_catches_unsupported_reporter() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE_V3 / "source.md",
        authority_inventory_path=FIXTURE_V3 / "authority_inventory.json",
        document_id="legal_authority_verification_micro_v3",
    )

    assert report["summary"]["citation_mentions"] == 1
    assert report["summary"]["verified_mentions"] == 0
    assert report["summary"]["blocked_mentions"] == 1
    assert report["summary"]["review_required_mentions"] == 0
    assert report["summary"]["resolved"] == 0
    assert report["summary"]["unresolved"] == 0
    assert report["summary"]["ambiguous"] == 0
    assert report["summary"]["invalid_reporter"] == 1
    assert report["summary"]["metadata_checks"] == 0
    assert report["summary"]["verification_abstentions"] == 1
    assert report["summary"]["false_verified"] == 0
    assert report["summary"]["document_outcome"] == "review_required"

    issues = {row["issue"] for row in report["issues"]}
    assert issues == {"invalid_reporter"}

    queries = report["ledger_queries"]
    assert len(queries["which_citations_do_not_resolve"]) == 1
    assert len(queries["which_citations_use_unsupported_reporters"]) == 1
    assert queries["can_this_filing_be_certified_citation_clean"] == {
        "citation_clean": False,
        "blocking_issue_count": 1,
        "blocking_issue_types": ["invalid_reporter"],
        "review_required_count": 0,
        "answer": "no",
    }


def test_legal_authority_resolves_declared_federal_reporter_inventory(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("Smith v. Jones, 12 F.3d 34, 36 (9th Cir. 1995).", encoding="utf-8")
    inventory = tmp_path / "authority_inventory.json"
    inventory.write_text(
        json.dumps(
            {
                "schema_version": "legal_authority_inventory_v1",
                "authorities": [
                    {
                        "authority_id": "auth_smith_12_f_3d_34",
                        "canonical_citation": "12 F.3d 34",
                        "case_name": "Smith v. Jones",
                        "court": "United States Court of Appeals",
                        "year": "1995",
                        "reporter": "F.3d",
                        "volume": "12",
                        "page": "34",
                        "pages": {},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    report = verify_legal_authorities(
        source_path=source,
        authority_inventory_path=inventory,
        document_id="legal_authority_federal_reporter",
    )

    assert report["summary"]["citation_mentions"] == 1
    assert report["summary"]["resolved"] == 1
    assert report["summary"]["invalid_reporter"] == 0
    assert report["summary"]["verified_mentions"] == 1
    assert report["mentions"][0]["pin"] == "36"
    assert report["mentions"][0]["metadata_checks"] == [
        {"field": "case_name", "extracted": "Smith v. Jones", "authority_value": "Smith v. Jones", "status": "match"},
        {"field": "volume", "extracted": "12", "authority_value": "12", "status": "match"},
        {"field": "reporter", "extracted": "F.3d", "authority_value": "F.3d", "status": "match"},
        {"field": "page", "extracted": "34", "authority_value": "34", "status": "match"},
        {"field": "year", "extracted": "1995", "authority_value": "1995", "status": "match"},
    ]


def test_legal_authority_pin_range_contains_matched_quote_page(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text(
        (
            "Obergefell v. Hodges, 576 U.S. 644, 675-76 (2015), states "
            '"The Court now holds that same-sex couples may exercise the fundamental right to marry."'
        ),
        encoding="utf-8",
    )

    report = verify_legal_authorities(
        source_path=source,
        authority_inventory_path=FIXTURE / "authority_inventory.json",
        document_id="legal_authority_pin_range",
    )

    assert report["summary"]["verified_mentions"] == 1
    assert report["summary"]["pin_mismatch"] == 0
    assert report["mentions"][0]["pin_check"] == {
        "pin": "page_675_76",
        "status": "pin_contains_quote",
    }


def test_legal_authority_report_carries_authority_text_source_url_without_fact_expansion(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text(
        (
            "Brown v. Board of Education, 347 U.S. 483, 495 (1954), states "
            '"Separate educational facilities are inherently unequal."'
        ),
        encoding="utf-8",
    )
    inventory_data = json.loads((FIXTURE / "authority_inventory.json").read_text(encoding="utf-8"))
    for authority in inventory_data["authorities"]:
        if authority["authority_id"] == "auth_brown_347_us_483":
            authority["authority_text_url"] = "https://example.test/authority/brown"
    inventory = tmp_path / "authority_inventory.json"
    inventory.write_text(json.dumps(inventory_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = verify_legal_authorities(
        source_path=source,
        authority_inventory_path=inventory,
        document_id="legal_authority_text_source_url",
    )

    assert report["authority_text_sources"] == [
        {
            "authority_id": "auth_brown_347_us_483",
            "source_url": "https://example.test/authority/brown",
            "text_digest": "sha256_85cc42e31389",
            "text_scope": "page_495",
            "text_status": "available",
        }
    ]
    assert report["ledger_queries"]["which_authority_text_sources_were_used"] == report["authority_text_sources"]
    assert (
        "legal_authority_text_source("
        "auth_brown_347_us_483, page_495, available, sha256_85cc42e31389, authority_inventory)."
    ) in report["facts"]


def test_legal_authority_micro_fixture_v4_keeps_quote_verification_authority_scoped() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE_V4 / "source.md",
        authority_inventory_path=FIXTURE_V4 / "authority_inventory.json",
        document_id="legal_authority_verification_micro_v4",
    )

    assert report["summary"]["citation_mentions"] == 1
    assert report["summary"]["verified_mentions"] == 0
    assert report["summary"]["blocked_mentions"] == 1
    assert report["summary"]["review_required_mentions"] == 0
    assert report["summary"]["resolved"] == 1
    assert report["summary"]["metadata_checks"] == 5
    assert report["summary"]["metadata_match"] == 5
    assert report["summary"]["metadata_mismatch"] == 0
    assert report["summary"]["quote_claims"] == 1
    assert report["summary"]["quote_exact_or_normalized_match"] == 0
    assert report["summary"]["quote_mismatch"] == 1
    assert report["summary"]["verification_abstentions"] == 1
    assert report["summary"]["false_verified"] == 0
    assert report["summary"]["document_outcome"] == "review_required"

    mention = report["mentions"][0]
    assert mention["authority_id"] == "auth_brown_347_us_483"
    assert mention["quote_check"]["status"] == "no_match"

    queries = report["ledger_queries"]
    assert len(queries["which_quotes_cannot_be_found"]) == 1
    assert queries["can_this_filing_be_certified_citation_clean"] == {
        "citation_clean": False,
        "blocking_issue_count": 1,
        "blocking_issue_types": ["quote_not_found_in_authority"],
        "review_required_count": 0,
        "answer": "no",
    }


def test_legal_authority_micro_fixture_v5_resolves_bare_reporter_citations_without_metadata_invention() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE_V5 / "source.md",
        authority_inventory_path=FIXTURE_V5 / "authority_inventory.json",
        document_id="legal_authority_verification_micro_v5",
    )

    assert report["summary"]["citation_mentions"] == 4
    assert report["summary"]["verified_mentions"] == 4
    assert report["summary"]["blocked_mentions"] == 0
    assert report["summary"]["resolved"] == 4
    assert report["summary"]["metadata_checks"] == 14
    assert report["summary"]["metadata_match"] == 14
    assert report["summary"]["metadata_mismatch"] == 0
    assert report["summary"]["quote_claims"] == 2
    assert report["summary"]["quote_exact_or_normalized_match"] == 2
    assert report["summary"]["pin_mismatch"] == 0
    assert report["summary"]["verification_abstentions"] == 0
    assert report["summary"]["false_verified"] == 0
    assert report["summary"]["document_outcome"] == "citation_clean"

    full = report["mentions"][0]
    bare = report["mentions"][1:]
    assert full["case_name"] == "Brown v. Board of Education"
    assert {check["field"]: check["status"] for check in full["metadata_checks"]} == {
        "case_name": "match",
        "volume": "match",
        "reporter": "match",
        "page": "match",
        "year": "match",
    }
    assert report["mentions"][2]["citation"] == "576 U.S. 644"
    assert all(row["case_name"] == "" for row in bare)
    assert [
        {check["field"]: check["status"] for check in row["metadata_checks"]}
        for row in bare
    ] == [
        {"volume": "match", "reporter": "match", "page": "match"},
        {"volume": "match", "reporter": "match", "page": "match"},
        {"volume": "match", "reporter": "match", "page": "match"},
    ]

    queries = report["ledger_queries"]
    assert queries["which_cases_have_metadata_mismatches"] == []
    assert queries["which_pin_cites_do_not_contain_the_quote"] == []
    assert queries["which_authorities_are_attached_to_propositions"] == []
    assert queries["can_this_filing_be_certified_citation_clean"] == {
        "citation_clean": True,
        "blocking_issue_count": 0,
        "blocking_issue_types": [],
        "review_required_count": 0,
        "answer": "yes",
    }


def test_legal_authority_micro_fixture_v6_checks_quotes_before_citations() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE_V6 / "source.md",
        authority_inventory_path=FIXTURE_V6 / "authority_inventory.json",
        document_id="legal_authority_verification_micro_v6",
    )

    assert report["summary"]["citation_mentions"] == 2
    assert report["summary"]["verified_mentions"] == 1
    assert report["summary"]["blocked_mentions"] == 1
    assert report["summary"]["metadata_checks"] == 10
    assert report["summary"]["metadata_match"] == 10
    assert report["summary"]["metadata_mismatch"] == 0
    assert report["summary"]["quote_claims"] == 2
    assert report["summary"]["quote_exact_or_normalized_match"] == 1
    assert report["summary"]["quote_mismatch"] == 1
    assert report["summary"]["authority_text_sources"] == 1
    assert report["summary"]["authority_text_available_sources"] == 1
    assert report["summary"]["verification_abstentions"] == 1
    assert report["summary"]["false_verified"] == 0

    assert report["mentions"][0]["quote_check"]["status"] == "normalized_match"
    assert report["mentions"][0]["pin_check"]["status"] == "pin_contains_quote"
    assert report["mentions"][1]["quote_check"]["status"] == "no_match"
    assert report["mentions"][1]["verification_status"] == "blocked"

    queries = report["ledger_queries"]
    assert len(queries["which_quotes_cannot_be_found"]) == 1
    assert queries["which_authority_text_sources_were_used"] == [
        {
            "authority_id": "auth_brown_347_us_483",
            "text_digest": "sha256_85cc42e31389",
            "text_scope": "page_495",
            "text_status": "available",
        }
    ]
    assert queries["can_this_filing_be_certified_citation_clean"] == {
        "citation_clean": False,
        "blocking_issue_count": 1,
        "blocking_issue_types": ["quote_not_found_in_authority"],
        "review_required_count": 0,
        "answer": "no",
    }


def test_legal_authority_micro_fixture_emits_expected_and_not_forbidden_facts() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE / "source.md",
        authority_inventory_path=FIXTURE / "authority_inventory.json",
    )
    emitted = {line.strip() for line in facts_text(report).splitlines() if line.strip()}
    expected = {
        line.strip()
        for line in (FIXTURE / "expected_facts.pl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    forbidden = {
        line.strip()
        for line in (FIXTURE / "forbidden_facts.pl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }

    assert expected <= emitted
    assert emitted.isdisjoint(forbidden)


def test_legal_authority_micro_fixture_v2_emits_expected_and_not_forbidden_facts() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE_V2 / "source.md",
        authority_inventory_path=FIXTURE_V2 / "authority_inventory.json",
        document_id="legal_authority_micro_v2",
    )
    emitted = {line.strip() for line in facts_text(report).splitlines() if line.strip()}
    expected = {
        line.strip()
        for line in (FIXTURE_V2 / "expected_facts.pl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    forbidden = {
        line.strip()
        for line in (FIXTURE_V2 / "forbidden_facts.pl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }

    assert expected <= emitted
    assert emitted.isdisjoint(forbidden)


def test_legal_authority_micro_fixture_v3_emits_expected_and_not_forbidden_facts() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE_V3 / "source.md",
        authority_inventory_path=FIXTURE_V3 / "authority_inventory.json",
        document_id="legal_authority_verification_micro_v3",
    )
    emitted = {line.strip() for line in facts_text(report).splitlines() if line.strip()}
    expected = {
        line.strip()
        for line in (FIXTURE_V3 / "expected_facts.pl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    forbidden = {
        line.strip()
        for line in (FIXTURE_V3 / "forbidden_facts.pl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }

    assert expected <= emitted
    assert emitted.isdisjoint(forbidden)


def test_legal_authority_micro_fixture_v4_emits_expected_and_not_forbidden_facts() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE_V4 / "source.md",
        authority_inventory_path=FIXTURE_V4 / "authority_inventory.json",
        document_id="legal_authority_verification_micro_v4",
    )
    emitted = {line.strip() for line in facts_text(report).splitlines() if line.strip()}
    expected = {
        line.strip()
        for line in (FIXTURE_V4 / "expected_facts.pl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    forbidden = {
        line.strip()
        for line in (FIXTURE_V4 / "forbidden_facts.pl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }

    assert expected <= emitted
    assert emitted.isdisjoint(forbidden)


def test_legal_authority_micro_fixture_v5_emits_expected_and_not_forbidden_facts() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE_V5 / "source.md",
        authority_inventory_path=FIXTURE_V5 / "authority_inventory.json",
        document_id="legal_authority_verification_micro_v5",
    )
    emitted = {line.strip() for line in facts_text(report).splitlines() if line.strip()}
    expected = {
        line.strip()
        for line in (FIXTURE_V5 / "expected_facts.pl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    forbidden = {
        line.strip()
        for line in (FIXTURE_V5 / "forbidden_facts.pl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }

    assert expected <= emitted
    assert emitted.isdisjoint(forbidden)


def test_legal_authority_micro_fixture_v6_emits_expected_and_not_forbidden_facts() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE_V6 / "source.md",
        authority_inventory_path=FIXTURE_V6 / "authority_inventory.json",
        document_id="legal_authority_verification_micro_v6",
    )
    emitted = {line.strip() for line in facts_text(report).splitlines() if line.strip()}
    expected = {
        line.strip()
        for line in (FIXTURE_V6 / "expected_facts.pl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    forbidden = {
        line.strip()
        for line in (FIXTURE_V6 / "forbidden_facts.pl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }

    assert expected <= emitted
    assert emitted.isdisjoint(forbidden)


def test_legal_authority_report_renders_review_required_boundary() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE / "source.md",
        authority_inventory_path=FIXTURE / "authority_inventory.json",
    )
    markdown = render_markdown(report)

    assert "Document outcome: `review_required`" in markdown
    assert "Verified mentions: `1`" in markdown
    assert "Metadata checks / matches / mismatches: `20 / 20 / 0`" in markdown
    assert "Verification abstentions: `4`" in markdown
    assert "`review_required`" in markdown
    assert "`blocked`" in markdown
    assert "`quote_not_found_in_authority`" in markdown
    assert "`quote_outside_cited_pin`" in markdown
    assert "`human_review_required`" in markdown
    assert "Ledger Query Answers" in markdown
    assert "Certification answer: `no`" in markdown
    assert "Blocking issue types: `quote_not_found_in_authority, quote_outside_cited_pin, unresolved`" in markdown
    assert "Proposition authority links: `1`" in markdown


def test_legal_authority_cli_defaults_to_local_resolver(tmp_path: Path) -> None:
    out_json = tmp_path / "report.json"

    exit_code = main(
        [
            "--source",
            str(FIXTURE_V5 / "source.md"),
            "--authority-inventory",
            str(FIXTURE_V5 / "authority_inventory.json"),
            "--document-id",
            "legal_authority_cli_local",
            "--out-json",
            str(out_json),
        ]
    )

    report = json.loads(out_json.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert report["resolver"]["mode"] == "local_inventory"
    assert report["resolver"]["default_local"] == "yes"
    assert report["summary"]["false_verified"] == 0


def test_legal_authority_cli_can_use_cached_courtlistener_resolver_without_token(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("COURTLISTENER_API_TOKEN", raising=False)
    source = tmp_path / "source.md"
    source.write_text("Brown v. Board of Education, 347 U.S. 483 (1954).", encoding="utf-8")
    cache_dir = tmp_path / "courtlistener-cache"
    client = CourtListenerClient(cache_dir=cache_dir)
    text = "347 U.S. 483"
    url = client._url("/citation-lookup/", {})
    body = urllib.parse.urlencode({"text": text}).encode("utf-8")
    cached = client._cache_path(method="POST", url=url, body=body)
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_text(
        json.dumps(
            [
                {
                    "citation": text,
                    "normalized_citations": [text],
                    "start_index": 0,
                    "end_index": 12,
                    "status": 200,
                    "error_message": "",
                    "clusters": [
                        {
                            "id": 347483,
                            "case_name": "Brown v. Board of Education",
                            "citations": [{"volume": 347, "reporter": "U.S.", "page": "483"}],
                            "date_filed": "1954-05-17",
                        }
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )
    out_json = tmp_path / "report.json"

    exit_code = main(
        [
            "--source",
            str(source),
            "--authority-inventory",
            str(FIXTURE / "authority_inventory.json"),
            "--document-id",
            "legal_authority_cli_courtlistener_cached",
            "--resolver",
            "courtlistener",
            "--courtlistener-cache-dir",
            str(cache_dir),
            "--out-json",
            str(out_json),
        ]
    )

    report = json.loads(out_json.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert report["resolver"] == {
        "mode": "courtlistener_citation_lookup",
        "class": "CourtListenerCitationLookupResolver",
        "default_local": "no",
        "provider": "courtlistener",
        "external_lookup": "explicit",
        "base_url": "https://www.courtlistener.com/api/rest/v4",
        "cache_dir": str(cache_dir),
        "inventory_assisted": "yes",
        "live_call_policy": "cache_replay_or_token_required",
    }
    assert report["summary"]["verified_mentions"] == 1
    assert report["summary"]["false_verified"] == 0


def test_legal_authority_courtlistener_resolver_carries_cluster_source_url(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("COURTLISTENER_API_TOKEN", raising=False)
    source = tmp_path / "source.md"
    source.write_text("Brown v. Board of Education, 347 U.S. 483 (1954).", encoding="utf-8")
    inventory = tmp_path / "authority_inventory.json"
    inventory.write_text(
        json.dumps({"schema_version": "legal_authority_inventory_v1", "authorities": []}),
        encoding="utf-8",
    )
    cache_dir = tmp_path / "courtlistener-cache"
    client = CourtListenerClient(cache_dir=cache_dir)
    text = "347 U.S. 483"
    url = client._url("/citation-lookup/", {})
    body = urllib.parse.urlencode({"text": text}).encode("utf-8")
    cached = client._cache_path(method="POST", url=url, body=body)
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_text(
        json.dumps(
            [
                {
                    "citation": text,
                    "normalized_citations": [text],
                    "start_index": 0,
                    "end_index": 12,
                    "status": 200,
                    "error_message": "",
                    "clusters": [
                        {
                            "id": 347483,
                            "absolute_url": "/opinion/347483/brown-v-board/",
                            "case_name": "Brown v. Board of Education",
                            "court": "Supreme Court of the United States",
                            "citations": [{"volume": 347, "reporter": "U.S.", "page": "483"}],
                            "date_filed": "1954-05-17",
                        }
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )
    out_json = tmp_path / "report.json"

    exit_code = main(
        [
            "--source",
            str(source),
            "--authority-inventory",
            str(inventory),
            "--document-id",
            "legal_authority_cli_courtlistener_url",
            "--resolver",
            "courtlistener",
            "--courtlistener-cache-dir",
            str(cache_dir),
            "--out-json",
            str(out_json),
        ]
    )

    report = json.loads(out_json.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert report["authority_text_sources"] == [
        {
            "authority_id": "courtlistener_cluster_347483",
            "source_url": "https://www.courtlistener.com/opinion/347483/brown-v-board/",
            "text_digest": "no_digest",
            "text_scope": "authority_text",
            "text_status": "authority_unavailable",
        }
    ]
    assert (
        "legal_authority_text_source("
        "courtlistener_cluster_347483, authority_text, authority_unavailable, no_digest, authority_inventory)."
    ) in report["facts"]


def test_legal_authority_short_form_citation_blocks_certification_without_fake_resolution(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text(
        "Brown v. Board of Education, 347 U.S. 483, 495 (1954).\nId. at 495.",
        encoding="utf-8",
    )

    report = verify_legal_authorities(
        source_path=source,
        authority_inventory_path=FIXTURE / "authority_inventory.json",
        document_id="legal_authority_short_form",
    )

    assert report["summary"]["citation_mentions"] == 1
    assert report["summary"]["short_form_citations"] == 1
    assert report["summary"]["document_outcome"] == "review_required"
    assert report["ledger_queries"]["which_citations_require_context"] == [
        {
            "short_form_id": "short_form_001",
            "citation": "Id. at 495",
            "line": 2,
            "reason": "short_form_citation_requires_context",
        }
    ]
    assert report["ledger_queries"]["can_this_filing_be_certified_citation_clean"] == {
        "citation_clean": False,
        "blocking_issue_count": 1,
        "blocking_issue_types": ["short_form_citation_requires_context"],
        "review_required_count": 0,
        "answer": "no",
    }
    assert (
        "legal_verification_abstention("
        "short_form_001, authority_resolution, short_form_citation_requires_context, source_line_2)."
    ) in report["facts"]
    assert not any("legal_authority_resolution(short_form_001" in fact for fact in report["facts"])


def test_legal_fixture_corpus_manifest_defers_sanction_expansion() -> None:
    manifest = json.loads(
        (ROOT / "datasets" / "legal_authority_verification" / "fixture_corpus_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    classes = {row["id"]: row for row in manifest["fixture_classes"]}

    assert classes["controlled_adversarial_mutations"]["status"] == "seeded"
    assert "datasets/compile_micro_fixtures/legal_authority_verification_micro_v1" in classes[
        "controlled_adversarial_mutations"
    ]["fixtures"]
    assert "datasets/compile_micro_fixtures/legal_authority_verification_micro_v2" in classes[
        "controlled_adversarial_mutations"
    ]["fixtures"]
    assert "datasets/compile_micro_fixtures/legal_authority_verification_micro_v3" in classes[
        "controlled_adversarial_mutations"
    ]["fixtures"]
    assert "datasets/compile_micro_fixtures/legal_authority_verification_micro_v4" in classes[
        "controlled_adversarial_mutations"
    ]["fixtures"]
    assert "datasets/compile_micro_fixtures/legal_authority_verification_micro_v5" in classes[
        "controlled_adversarial_mutations"
    ]["fixtures"]
    assert "datasets/compile_micro_fixtures/legal_authority_verification_micro_v6" in classes[
        "controlled_adversarial_mutations"
    ]["fixtures"]
    assert classes["known_hallucination_or_sanction_filings"]["status"] == "deferred_until_clean_public_baseline"
    assert manifest["next_external_work_order_needed"]["needed_now"] is True
    assert "clean-public-filings batch" in manifest["next_external_work_order_needed"]["reason"]
    assert "legal_authority_clean_public_filings_work_order_20260606_r9.zip" in manifest[
        "next_external_work_order_needed"
    ]["reason"]
    assert "Known hallucination/sanction filings remain deferred" in manifest["next_external_work_order_needed"]["reason"]

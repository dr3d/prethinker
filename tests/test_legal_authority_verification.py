from __future__ import annotations

import json
from pathlib import Path

from src.legal_authority_resolvers import LocalAuthorityInventoryResolver
from src.legal_authority_verification import facts_text, render_markdown, verify_legal_authorities


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
    assert report["summary"]["metadata_checks"] == 8
    assert report["summary"]["metadata_match"] == 8
    assert report["summary"]["metadata_mismatch"] == 0
    assert report["summary"]["quote_mismatch"] == 1
    assert report["summary"]["pin_mismatch"] == 1
    assert report["summary"]["proposition_boundaries"] == 1
    assert report["summary"]["verification_abstentions"] == 4
    assert report["summary"]["false_verified"] == 0
    assert report["summary"]["document_outcome"] == "review_required"

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
    assert report["summary"]["metadata_checks"] == 6
    assert report["summary"]["metadata_match"] == 4
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
    assert report["summary"]["metadata_checks"] == 2
    assert report["summary"]["metadata_match"] == 2
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
    assert report["summary"]["metadata_checks"] == 2
    assert report["summary"]["metadata_match"] == 2
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
        "year": "match",
    }
    assert report["mentions"][2]["citation"] == "576 U.S. 644"
    assert all(row["case_name"] == "" for row in bare)
    assert all(row["metadata_checks"] == [] for row in bare)

    queries = report["ledger_queries"]
    assert queries["which_cases_have_metadata_mismatches"] == []
    assert queries["which_pin_cites_do_not_contain_the_quote"] == []
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
    assert report["summary"]["metadata_checks"] == 4
    assert report["summary"]["metadata_match"] == 4
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
    assert "Metadata checks / matches / mismatches: `8 / 8 / 0`" in markdown
    assert "Verification abstentions: `4`" in markdown
    assert "`review_required`" in markdown
    assert "`blocked`" in markdown
    assert "`quote_not_found_in_authority`" in markdown
    assert "`quote_outside_cited_pin`" in markdown
    assert "`human_review_required`" in markdown
    assert "Ledger Query Answers" in markdown
    assert "Certification answer: `no`" in markdown
    assert "Blocking issue types: `quote_not_found_in_authority, quote_outside_cited_pin, unresolved`" in markdown


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
    assert classes["known_hallucination_or_sanction_filings"]["status"] == "deferred_until_resolver_contract_stable"
    assert manifest["next_external_work_order_needed"]["needed_now"] is True
    assert "clean-public-filings batch" in manifest["next_external_work_order_needed"]["reason"]
    assert "Known hallucination/sanction filings remain deferred" in manifest["next_external_work_order_needed"]["reason"]

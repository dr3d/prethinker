from __future__ import annotations

import json
from pathlib import Path

from src.legal_authority_verification import facts_text, render_markdown, verify_legal_authorities


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "datasets" / "compile_micro_fixtures" / "legal_authority_verification_micro_v1"


def test_legal_authority_micro_fixture_catches_hallucination_shapes() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE / "source.md",
        authority_inventory_path=FIXTURE / "authority_inventory.json",
    )

    assert report["summary"]["citation_mentions"] == 5
    assert report["summary"]["resolved"] == 4
    assert report["summary"]["unresolved"] == 1
    assert report["summary"]["quote_mismatch"] == 1
    assert report["summary"]["pin_mismatch"] == 1
    assert report["summary"]["proposition_boundaries"] == 1
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
        "review_required_count": 1,
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


def test_legal_authority_report_renders_review_required_boundary() -> None:
    report = verify_legal_authorities(
        source_path=FIXTURE / "source.md",
        authority_inventory_path=FIXTURE / "authority_inventory.json",
    )
    markdown = render_markdown(report)

    assert "Document outcome: `review_required`" in markdown
    assert "`quote_not_found_in_authority`" in markdown
    assert "`quote_outside_cited_pin`" in markdown
    assert "`human_review_required`" in markdown
    assert "Ledger Query Answers" in markdown
    assert "Certification answer: `no`" in markdown


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
    assert classes["known_hallucination_or_sanction_filings"]["status"] == "deferred_until_resolver_contract_stable"
    assert manifest["next_external_work_order_needed"]["needed_now"] is False

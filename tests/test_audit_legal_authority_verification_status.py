from __future__ import annotations

from scripts.audit_legal_authority_verification_status import build_report, render_markdown


def test_legal_authority_status_audits_manifest_fixtures() -> None:
    report = build_report()
    summary = report["summary"]

    assert summary["status"] == "pass"
    assert summary["fixture_count"] == 12
    assert summary["matched_expected_fact_count"] == summary["expected_fact_count"] == 217
    assert summary["matched_forbidden_fact_count"] == 0
    assert summary["forbidden_fact_count"] == 63
    assert summary["citation_mentions"] == 30
    assert summary["false_verified"] == 0
    assert summary["verified_mentions"] == 18
    assert summary["blocked_mentions"] == 11
    assert summary["review_required_mentions"] == 1
    assert summary["invalid_reporter"] == 1
    assert summary["unavailable"] == 0
    assert summary["metadata_checks"] == 125
    assert summary["metadata_match"] == 123
    assert summary["metadata_mismatch"] == 2
    assert summary["authority_text_sources"] == 22
    assert summary["authority_text_available_sources"] == 14
    assert summary["authority_text_unavailable_sources"] == 8
    assert summary["short_form_citations"] == 2
    assert summary["pin_unavailable"] == 1
    assert summary["verification_abstentions"] == 12
    signatures = {row["signature"]: row for row in summary["fact_signature_summary"]}
    assert signatures["legal_citation_mention/5"] == {
        "signature": "legal_citation_mention/5",
        "expected": 30,
        "matched_expected": 30,
        "forbidden": 2,
        "matched_forbidden": 0,
    }
    assert signatures["legal_authority_metadata_check/5"] == {
        "signature": "legal_authority_metadata_check/5",
        "expected": 89,
        "matched_expected": 89,
        "forbidden": 13,
        "matched_forbidden": 0,
    }
    assert signatures["legal_quote_span_match/5"] == {
        "signature": "legal_quote_span_match/5",
        "expected": 13,
        "matched_expected": 13,
        "forbidden": 12,
        "matched_forbidden": 0,
    }
    assert signatures["legal_verification_abstention/4"] == {
        "signature": "legal_verification_abstention/4",
        "expected": 12,
        "matched_expected": 12,
        "forbidden": 2,
        "matched_forbidden": 0,
    }

    fixtures = {row["fixture_id"]: row for row in report["fixtures"]}
    assert fixtures["legal_authority_verification_micro_v1"]["matched_expected_fact_count"] == 51
    assert fixtures["legal_authority_verification_micro_v2"]["matched_expected_fact_count"] == 29
    assert fixtures["legal_authority_verification_micro_v3"]["matched_expected_fact_count"] == 3
    assert fixtures["legal_authority_verification_micro_v4"]["matched_expected_fact_count"] == 12
    assert fixtures["legal_authority_verification_micro_v5"]["matched_expected_fact_count"] == 31
    assert fixtures["legal_authority_verification_micro_v6"]["matched_expected_fact_count"] == 21
    assert fixtures["legal_authority_verification_micro_v7"]["matched_expected_fact_count"] == 1
    assert fixtures["legal_authority_verification_micro_v8"]["matched_expected_fact_count"] == 1
    assert fixtures["legal_authority_verification_micro_v9"]["matched_expected_fact_count"] == 12
    assert fixtures["clean_legal_filing_001"]["matched_expected_fact_count"] == 18
    assert fixtures["clean_legal_filing_002"]["matched_expected_fact_count"] == 20
    assert fixtures["clean_legal_filing_003"]["matched_expected_fact_count"] == 18
    assert report["next_external_work_order_needed"]["needed_now"] is True
    assert "legal_authority_known_hallucination_sanction_work_order_20260606_r1.zip" in report[
        "next_external_work_order_needed"
    ]["reason"]


def test_legal_authority_status_markdown_names_false_verified_gate() -> None:
    markdown = render_markdown(build_report())

    assert "Legal Authority Verification Status" in markdown
    assert "False verified: `0`" in markdown
    assert "Expected facts: `217 / 217`" in markdown
    assert "Matched forbidden facts: `0 / 63`" in markdown
    assert "Authority text sources: `22`" in markdown
    assert "Resolved / unresolved / ambiguous / invalid reporter / unavailable:" in markdown
    assert "Metadata checks / matches / mismatches: `125 / 123 / 2`" in markdown
    assert "Short-form citations requiring context: `2`" in markdown
    assert "Pin unavailable: `1`" in markdown
    assert "Verification abstentions: `12`" in markdown
    assert "Fact Signature Coverage" in markdown
    assert "`legal_quote_span_match/5` | 13/13 | 0/12" in markdown
    assert "Clean-public legal filings have been imported" in markdown

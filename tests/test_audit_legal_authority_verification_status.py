from __future__ import annotations

from scripts.audit_legal_authority_verification_status import build_report, render_markdown


def test_legal_authority_status_audits_manifest_fixtures() -> None:
    report = build_report()
    summary = report["summary"]

    assert summary["status"] == "pass"
    assert summary["fixture_count"] == 6
    assert summary["matched_expected_fact_count"] == summary["expected_fact_count"] == 105
    assert summary["matched_forbidden_fact_count"] == 0
    assert summary["forbidden_fact_count"] == 35
    assert summary["citation_mentions"] == 17
    assert summary["false_verified"] == 0
    assert summary["verified_mentions"] == 6
    assert summary["blocked_mentions"] == 10
    assert summary["review_required_mentions"] == 1
    assert summary["invalid_reporter"] == 1
    assert summary["metadata_checks"] == 22
    assert summary["metadata_match"] == 20
    assert summary["metadata_mismatch"] == 2
    assert summary["authority_text_sources"] == 11
    assert summary["authority_text_available_sources"] == 10
    assert summary["authority_text_unavailable_sources"] == 1
    assert summary["verification_abstentions"] == 9
    signatures = {row["signature"]: row for row in summary["fact_signature_summary"]}
    assert signatures["legal_citation_mention/5"] == {
        "signature": "legal_citation_mention/5",
        "expected": 17,
        "matched_expected": 17,
        "forbidden": 0,
        "matched_forbidden": 0,
    }
    assert signatures["legal_quote_span_match/5"] == {
        "signature": "legal_quote_span_match/5",
        "expected": 9,
        "matched_expected": 9,
        "forbidden": 9,
        "matched_forbidden": 0,
    }
    assert signatures["legal_verification_abstention/4"] == {
        "signature": "legal_verification_abstention/4",
        "expected": 9,
        "matched_expected": 9,
        "forbidden": 1,
        "matched_forbidden": 0,
    }

    fixtures = {row["fixture_id"]: row for row in report["fixtures"]}
    assert fixtures["legal_authority_verification_micro_v1"]["matched_expected_fact_count"] == 39
    assert fixtures["legal_authority_verification_micro_v2"]["matched_expected_fact_count"] == 20
    assert fixtures["legal_authority_verification_micro_v3"]["matched_expected_fact_count"] == 3
    assert fixtures["legal_authority_verification_micro_v4"]["matched_expected_fact_count"] == 9
    assert fixtures["legal_authority_verification_micro_v5"]["matched_expected_fact_count"] == 19
    assert fixtures["legal_authority_verification_micro_v6"]["matched_expected_fact_count"] == 15
    assert report["next_external_work_order_needed"]["needed_now"] is True


def test_legal_authority_status_markdown_names_false_verified_gate() -> None:
    markdown = render_markdown(build_report())

    assert "Legal Authority Verification Status" in markdown
    assert "False verified: `0`" in markdown
    assert "Expected facts: `105 / 105`" in markdown
    assert "Matched forbidden facts: `0 / 35`" in markdown
    assert "Authority text sources: `11`" in markdown
    assert "Resolved / unresolved / ambiguous / invalid reporter:" in markdown
    assert "Metadata checks / matches / mismatches: `22 / 20 / 2`" in markdown
    assert "Verification abstentions: `9`" in markdown
    assert "Fact Signature Coverage" in markdown
    assert "`legal_quote_span_match/5` | 9/9 | 0/9" in markdown
    assert "clean-public-filings batch" in markdown

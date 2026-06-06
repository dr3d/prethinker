from __future__ import annotations

from scripts.audit_legal_authority_verification_status import build_report, render_markdown


def test_legal_authority_status_audits_manifest_fixtures() -> None:
    report = build_report()
    summary = report["summary"]

    assert summary["status"] == "pass"
    assert summary["fixture_count"] == 6
    assert summary["matched_expected_fact_count"] == summary["expected_fact_count"] == 94
    assert summary["matched_forbidden_fact_count"] == 0
    assert summary["forbidden_fact_count"] == 33
    assert summary["citation_mentions"] == 17
    assert summary["false_verified"] == 0
    assert summary["verified_mentions"] == 6
    assert summary["blocked_mentions"] == 10
    assert summary["review_required_mentions"] == 1
    assert summary["invalid_reporter"] == 1

    fixtures = {row["fixture_id"]: row for row in report["fixtures"]}
    assert fixtures["legal_authority_verification_micro_v1"]["matched_expected_fact_count"] == 35
    assert fixtures["legal_authority_verification_micro_v2"]["matched_expected_fact_count"] == 18
    assert fixtures["legal_authority_verification_micro_v3"]["matched_expected_fact_count"] == 3
    assert fixtures["legal_authority_verification_micro_v4"]["matched_expected_fact_count"] == 8
    assert fixtures["legal_authority_verification_micro_v5"]["matched_expected_fact_count"] == 16
    assert fixtures["legal_authority_verification_micro_v6"]["matched_expected_fact_count"] == 14
    assert report["next_external_work_order_needed"]["needed_now"] is True


def test_legal_authority_status_markdown_names_false_verified_gate() -> None:
    markdown = render_markdown(build_report())

    assert "Legal Authority Verification Status" in markdown
    assert "False verified: `0`" in markdown
    assert "Expected facts: `94 / 94`" in markdown
    assert "Matched forbidden facts: `0 / 33`" in markdown
    assert "Resolved / unresolved / ambiguous / invalid reporter:" in markdown
    assert "clean-public-filings batch" in markdown

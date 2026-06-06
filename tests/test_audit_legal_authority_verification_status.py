from __future__ import annotations

from scripts.audit_legal_authority_verification_status import build_report, render_markdown


def test_legal_authority_status_audits_manifest_fixtures() -> None:
    report = build_report()
    summary = report["summary"]

    assert summary["status"] == "pass"
    assert summary["fixture_count"] == 2
    assert summary["matched_expected_fact_count"] == summary["expected_fact_count"] == 53
    assert summary["matched_forbidden_fact_count"] == 0
    assert summary["false_verified"] == 0
    assert summary["verified_mentions"] == 1
    assert summary["blocked_mentions"] == 7
    assert summary["review_required_mentions"] == 1

    fixtures = {row["fixture_id"]: row for row in report["fixtures"]}
    assert fixtures["legal_authority_verification_micro_v1"]["matched_expected_fact_count"] == 35
    assert fixtures["legal_authority_verification_micro_v2"]["matched_expected_fact_count"] == 18
    assert report["next_external_work_order_needed"]["needed_now"] is True


def test_legal_authority_status_markdown_names_false_verified_gate() -> None:
    markdown = render_markdown(build_report())

    assert "Legal Authority Verification Status" in markdown
    assert "False verified: `0`" in markdown
    assert "Expected facts: `53 / 53`" in markdown
    assert "Matched forbidden facts: `0 / 13`" in markdown
    assert "clean-public-filings batch" in markdown

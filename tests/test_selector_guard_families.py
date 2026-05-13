from scripts.summarize_selector_guard_families import (
    DEFAULT_SELECTOR,
    RETIRED_SCAR_GUARDS,
    build_guard_ledger,
    build_report,
    extract_guard_reasons,
    render_guard_ledger_markdown,
    render_markdown,
)


def test_selector_guard_reasons_are_classified_into_families() -> None:
    report = build_report(DEFAULT_SELECTOR)

    assert report["guard_reason_count"] >= 5
    assert report["unique_guard_reason_count"] <= report["guard_reason_count"]
    assert report["duplicate_reason_count"] == report["guard_reason_count"] - report["unique_guard_reason_count"]
    assert report["family_count"] <= 8
    assert report["unclassified_count"] == 0


def test_selector_guard_rollup_has_family_purposes() -> None:
    report = build_report(DEFAULT_SELECTOR)

    families = {family["family"]: family for family in report["families"]}
    assert "state_custody_ownership" in families
    assert "regulatory_access_scope" in families
    assert all(family["purpose"] for family in families.values())
    assert all(family["guards"] for family in families.values())


def test_selector_guard_rollup_reports_growth_health() -> None:
    report = build_report(DEFAULT_SELECTOR)

    health = report["health"]
    assert health["status"] in {"pass", "warn"}
    assert health["family_count"] == report["family_count"]
    assert health["family_count"] <= health["family_budget"]
    assert health["unclassified_count"] == 0
    assert health["largest_family"]
    assert 0 < health["largest_family_share"] <= 1.0
    assert "semantic compression" in health["interpretation"]
    if health["status"] == "warn":
        assert health["warnings"]


def test_selector_guard_reason_extraction_stays_scoped() -> None:
    reasons = extract_guard_reasons(DEFAULT_SELECTOR)
    reason_text = "\n".join(reason["reason"] for reason in reasons)

    assert "source prose, reference answers" not in reason_text
    assert "question needs" in reason_text


def test_selector_guard_rollup_markdown_renders() -> None:
    report = build_report(DEFAULT_SELECTOR)
    markdown = render_markdown(report)

    assert "# Selector Guard Family Rollup" in markdown
    assert "## Growth Health" in markdown
    assert "duplicate guard reasons" in markdown
    assert "## Promotion Discipline" in markdown
    assert "`state_custody_ownership`" in markdown


def test_selector_guard_ledger_scaffolds_audit_fields() -> None:
    report = build_report(DEFAULT_SELECTOR)
    ledger = build_guard_ledger(report)

    assert ledger["schema_version"] == "selector_guard_ledger_v1"
    assert ledger["summary"]["entry_count"] == report["guard_reason_count"] + len(RETIRED_SCAR_GUARDS)
    assert ledger["summary"]["unclassified_count"] == 0
    assert ledger["summary"]["status_counts"]
    assert ledger["summary"]["status_counts"]["scar_guard"] == len(RETIRED_SCAR_GUARDS)
    assert ledger["entries"]
    first = ledger["entries"][0]
    assert "audit_status" in first
    assert "transfer_evidence" in first
    assert "retirement_bucket" in first
    assert "retirement_priority" in first
    assert "retirement_condition" in first
    assert ledger["summary"]["retirement_bucket_counts"]
    assert ledger["summary"]["retirement_priority_counts"]


def test_selector_guard_ledger_markdown_renders() -> None:
    ledger = build_guard_ledger(build_report(DEFAULT_SELECTOR))
    markdown = render_guard_ledger_markdown(ledger)

    assert "# Selector Guard Ledger" in markdown
    assert "## Audit Policy" in markdown
    assert "## Retirement Pressure" in markdown
    assert "## First Retirement Slices" in markdown
    assert "## Ledger Entries" in markdown
    assert "retirement" in markdown.casefold()

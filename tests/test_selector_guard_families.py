from scripts.summarize_selector_guard_families import (
    DEFAULT_SELECTOR,
    build_report,
    extract_guard_reasons,
    render_markdown,
)


def test_selector_guard_reasons_are_classified_into_families() -> None:
    report = build_report(DEFAULT_SELECTOR)

    assert report["guard_reason_count"] >= 35
    assert report["unique_guard_reason_count"] <= report["guard_reason_count"]
    assert report["family_count"] <= 8
    assert report["unclassified_count"] == 0


def test_selector_guard_rollup_has_family_purposes() -> None:
    report = build_report(DEFAULT_SELECTOR)

    families = {family["family"]: family for family in report["families"]}
    assert "rule_activation_surface" in families
    assert "operational_record_status" in families
    assert all(family["purpose"] for family in families.values())
    assert all(family["guards"] for family in families.values())


def test_selector_guard_reason_extraction_stays_scoped() -> None:
    reasons = extract_guard_reasons(DEFAULT_SELECTOR)
    reason_text = "\n".join(reason["reason"] for reason in reasons)

    assert "source prose, reference answers" not in reason_text
    assert "question needs" in reason_text


def test_selector_guard_rollup_markdown_renders() -> None:
    report = build_report(DEFAULT_SELECTOR)
    markdown = render_markdown(report)

    assert "# Selector Guard Family Rollup" in markdown
    assert "## Promotion Discipline" in markdown
    assert "`rule_activation_surface`" in markdown

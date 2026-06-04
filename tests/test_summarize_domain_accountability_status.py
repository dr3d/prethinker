from scripts.summarize_domain_accountability_status import build_report, render_markdown


def test_domain_accountability_status_reports_live_requirement_coverage():
    report = build_report()

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["registry_requirement_count"] >= 6
    assert report["summary"]["fixture_omission_fact_count"] >= 7
    assert report["summary"]["fixture_only_omission_pattern_count"] == 0


def test_domain_accountability_status_counts_fda_no_fei_requirement():
    report = build_report()
    fda = next(row for row in report["domains"] if row["profile_id"] == "fda_warning_letter_v1")
    requirement = next(row for row in fda["requirements"] if row["id"] == "facility_fei_not_shown")

    assert requirement["carrier_signature"] == "fda_facility_identity/5"
    assert requirement["omission_kind"] == "none_found"
    assert requirement["reason_code"] == "no_fei_shown_in_letter"
    assert requirement["fixture_support_count"] == 3
    assert fda["fixture_only_omission_patterns"] == []


def test_domain_accountability_status_covers_sec_signature_negative_control():
    report = build_report()
    sec = next(row for row in report["domains"] if row["profile_id"] == "sec_form_8k_v1")

    assert sec["requirements"][0]["id"] == "missing_signature_block"
    assert sec["requirements"][0]["fixture_support_count"] == 1
    assert sec["requirements"][0]["fixtures"] == ["sec_form_8k_signature_omission_v1"]


def test_domain_accountability_status_markdown_names_static_boundary():
    markdown = render_markdown(build_report())

    assert "does not read source prose" in markdown
    assert "Compile-time enforcement remains the job" in markdown
    assert "fixture-only omission patterns" in markdown.lower()

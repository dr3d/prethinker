from scripts.plan_incoming_variant_selector_training import build_report, render_markdown


def _overlay() -> dict:
    return {
        "summary": {
            "overlay_counts": {"exact": 3, "partial": 0, "miss": 0},
            "accepted_variant_row_count": 1,
            "protected_baseline_exact_row_count": 1,
        },
        "fixtures": [
            {
                "fixture": "alpha",
                "accepted_variant_rows": [
                    {
                        "id": "q001",
                        "question": "Rescue?",
                        "baseline_verdict": "partial",
                        "selected_variant": "variant_a",
                        "selected_verdict": "exact",
                        "variants": [
                            {"name": "baseline", "verdict": "partial", "failure_surface": "compile_surface_gap"},
                            {"name": "variant_a", "verdict": "exact", "failure_surface": ""},
                        ],
                    }
                ],
                "protected_baseline_exact_rows": [
                    {
                        "id": "q002",
                        "question": "Protect?",
                        "baseline_verdict": "exact",
                        "selected_variant": "baseline",
                        "selected_verdict": "exact",
                        "variants": [
                            {"name": "baseline", "verdict": "exact", "failure_surface": ""},
                            {"name": "variant_a", "verdict": "miss", "failure_surface": "query_surface_gap"},
                        ],
                    }
                ],
                "unchanged_non_exact_rows": [],
            }
        ],
    }


def test_variant_selector_training_marks_row_gated_variant_risk() -> None:
    report = build_report(overlay=_overlay())

    assert report["summary"]["activation_training_target_count"] == 1
    assert report["summary"]["exact_protection_target_count"] == 1
    assert report["summary"]["global_recommendation"] == "train_row_variant_selector_with_exact_protection"
    assert report["variant_risks"][0]["variant"] == "variant_a"
    assert report["variant_risks"][0]["global_risk"] == "unsafe_global_variant_row_gate_required"
    assert report["training_rows"][0]["selector_recommendation"] == "row_gated_only"


def test_variant_selector_training_markdown_names_policy_boundary() -> None:
    markdown = render_markdown(build_report(overlay=_overlay()))

    assert "does not read source prose" in markdown
    assert "Variant Risk Buckets" in markdown
    assert "Rescue?" in markdown

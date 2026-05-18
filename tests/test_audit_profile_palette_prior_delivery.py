import json
from pathlib import Path

from scripts.audit_profile_palette_prior_delivery import audit_prior_delivery, render_markdown


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_prior_delivery_reports_offered_delivered_and_zero_yield(tmp_path: Path) -> None:
    registry = _write_json(
        tmp_path / "registry.json",
        {
            "fixture": "fixture_a",
            "predicates": [
                {"signature": "entity_status/2"},
                {"signature": "event_time/2"},
                {"signature": "event_measurement/4"},
            ],
        },
    )
    compile_json = _write_json(
        tmp_path / "compile" / "fixture_a" / "domain_bootstrap_file_a.json",
        {
            "parsed": {
                "candidate_predicates": [
                    {"signature": "entity_status/2"},
                    {"signature": "event_time/2"},
                    {"signature": "event_measurement/4"},
                    {"signature": "extra_surface/3"},
                ]
            },
            "source_compile": {
                "facts": [
                    "entity_status(packet_1, active).",
                    "event_time(ev_1, t1).",
                    "extra_surface(a, b, c).",
                    "source_record_field(src_line_1, label, value).",
                ]
            },
        },
    )

    audit = audit_prior_delivery(registry, [compile_json])
    row = audit["compiles"][0]

    assert audit["prior_signature_count"] == 3
    assert row["prior_offered_count"] == 3
    assert row["prior_delivered_count"] == 2
    assert row["prior_missing_signatures"] == []
    assert row["prior_zero_yield_signatures"] == ["event_measurement/4"]
    assert row["offered_non_prior_signatures"] == ["extra_surface/3"]
    assert row["delivered_non_prior_signatures"] == ["extra_surface/3"]
    assert audit["summary"]["all_prior_offered_compile_count"] == 1
    assert audit["summary"]["all_prior_delivered_compile_count"] == 0


def test_prior_delivery_reports_missing_prior_signature(tmp_path: Path) -> None:
    registry = _write_json(
        tmp_path / "registry.json",
        {"predicates": [{"signature": "entity_status/2"}, {"signature": "missing_surface/3"}]},
    )
    compile_json = _write_json(
        tmp_path / "compile" / "fixture_a" / "domain_bootstrap_file_a.json",
        {
            "parsed": {"candidate_predicates": [{"name": "entity_status", "args": ["entity", "status"]}]},
            "source_compile": {"facts": ["entity_status(packet_1, active)."]},
        },
    )

    audit = audit_prior_delivery(registry, [compile_json])

    assert audit["compiles"][0]["prior_missing_signatures"] == ["missing_surface/3"]
    assert audit["summary"]["ever_missing_prior_signatures"] == ["missing_surface/3"]


def test_prior_delivery_markdown_states_vocabulary_only(tmp_path: Path) -> None:
    registry = _write_json(tmp_path / "registry.json", {"predicates": [{"signature": "entity_status/2"}]})
    compile_json = _write_json(
        tmp_path / "compile" / "fixture_a" / "domain_bootstrap_file_a.json",
        {
            "parsed": {"candidate_predicates": [{"signature": "entity_status/2"}]},
            "source_compile": {"facts": ["entity_status(packet_1, active)."]},
        },
    )

    markdown = render_markdown(audit_prior_delivery(registry, [compile_json]))

    assert "vocabulary-only" in markdown
    assert "Prior signatures" in markdown
    assert "`[]`" in markdown

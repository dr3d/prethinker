import json
from pathlib import Path

from scripts.build_profile_palette_registry import build_registry, render_markdown


def _write_compile(path: Path, predicates: list[dict], facts: list[str] | None = None) -> Path:
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "parsed_ok": True,
                "parsed": {"candidate_predicates": predicates},
                "source_compile": {"facts": facts or []},
            }
        ),
        encoding="utf-8",
    )
    return path


def test_palette_registry_threshold_selects_shared_vocabulary(tmp_path: Path) -> None:
    draw1 = _write_compile(
        tmp_path / "draw1" / "fixture_a" / "domain_bootstrap_file_a.json",
        [
            {"signature": "entity_assignment/3", "args": ["entity", "version", "group"]},
            {"signature": "attribute_exception/3", "args": ["entity", "attribute", "basis"]},
        ],
    )
    draw2 = _write_compile(
        tmp_path / "draw2" / "fixture_a" / "domain_bootstrap_file_b.json",
        [
            {"signature": "entity_assignment/3", "args": ["entity", "version", "cohort"]},
            {"signature": "source_capture/4", "args": ["source", "record", "field", "value"]},
        ],
    )

    registry = build_registry([draw1, draw2], mode="threshold", min_draw_share=1.0)

    assert registry["schema"] == "candidate_profile_registry_v1"
    assert registry["fixture"] == "fixture_a"
    assert registry["source"].startswith("compile_candidate_palette_v1 vocabulary only")
    assert [row["signature"] for row in registry["predicates"]] == ["entity_assignment/3"]
    assert registry["predicates"][0]["args"] == ["entity", "version", "group"]
    assert registry["predicates"][0]["draw_share"] == 1.0


def test_palette_registry_union_keeps_draw_counts_without_facts(tmp_path: Path) -> None:
    draw1 = _write_compile(
        tmp_path / "draw1" / "fixture_a" / "domain_bootstrap_file_a.json",
        [{"signature": "entity_status/2", "args": ["entity", "status"]}],
    )
    draw2 = _write_compile(
        tmp_path / "draw2" / "fixture_a" / "domain_bootstrap_file_b.json",
        [{"signature": "event_timestamp/2", "args": ["event", "timestamp"]}],
    )

    registry = build_registry([draw1, draw2], mode="union")

    assert [row["signature"] for row in registry["predicates"]] == ["entity_status/2", "event_timestamp/2"]
    assert {row["category"] for row in registry["predicates"]} == {"status_state", "temporal"}
    assert all("Vocabulary scaffold only" in row["notes"] for row in registry["predicates"])
    assert "facts" not in json.dumps(registry["predicates"]).casefold()


def test_palette_registry_markdown_states_vocabulary_only(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw1" / "fixture_a" / "domain_bootstrap_file_a.json",
        [{"signature": "entity_status/2", "args": ["entity", "status"]}],
    )

    markdown = render_markdown(build_registry([draw], mode="first"))

    assert "vocabulary-only" in markdown
    assert "`entity_status/2`" in markdown


def test_palette_registry_can_require_delivered_signatures(tmp_path: Path) -> None:
    draw1 = _write_compile(
        tmp_path / "draw1" / "fixture_a" / "domain_bootstrap_file_a.json",
        [
            {"signature": "entity_status/2", "args": ["entity", "status"]},
            {"signature": "source_detail/4", "args": ["source", "record", "field", "value"]},
        ],
        facts=["entity_status(item_a, active)."],
    )
    draw2 = _write_compile(
        tmp_path / "draw2" / "fixture_a" / "domain_bootstrap_file_b.json",
        [
            {"signature": "entity_status/2", "args": ["entity", "status"]},
            {"signature": "source_detail/4", "args": ["source", "record", "field", "value"]},
        ],
        facts=["entity_status(item_b, pending).", "source_record_text_atom(src_line_1, ignored)."],
    )

    registry = build_registry([draw1, draw2], mode="threshold", min_draw_share=1.0, require_delivered=True)

    assert [row["signature"] for row in registry["predicates"]] == ["entity_status/2"]
    assert registry["selection"]["require_delivered"] is True


def test_palette_registry_threshold_uses_ceiling(tmp_path: Path) -> None:
    draws = []
    for index in range(7):
        predicates = [{"signature": "always_present/2", "args": ["entity", "value"]}]
        if index < 4:
            predicates.append({"signature": "four_of_seven/2", "args": ["entity", "value"]})
        draws.append(_write_compile(tmp_path / f"draw{index}" / "fixture_a" / f"domain_bootstrap_file_{index}.json", predicates))

    registry = build_registry(draws, mode="threshold", min_draw_share=0.6)

    assert [row["signature"] for row in registry["predicates"]] == ["always_present/2"]

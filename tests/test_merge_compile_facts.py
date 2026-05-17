import json
from pathlib import Path

from scripts.merge_compile_facts import merge_compile_files


def _write(path: Path, facts: list[str], predicates: list[str]) -> Path:
    path.write_text(
        json.dumps(
            {
                "parsed_ok": True,
                "parsed": {"candidate_predicates": predicates},
                "source_compile": {"facts": facts},
            }
        ),
        encoding="utf-8",
    )
    return path


def test_merge_compile_facts_preserves_baseline_and_adds_candidate(tmp_path: Path) -> None:
    baseline = _write(
        tmp_path / "baseline.json",
        [
            "source_record_text_atom(src_line_001, baseline_source).",
            "event_happened(event_1, opened, 2026_01_01).",
            "vote_cast(event_1, alice, yes, item_1).",
        ],
        ["event_happened/3", "vote_cast/4"],
    )
    candidate = _write(
        tmp_path / "candidate.json",
        [
            "source_record_text_atom(src_line_001, candidate_source).",
            "event_happened(event_1, opened, 2026_01_01).",
            "participant_statement(statement_1, alice, meeting_1, concern).",
        ],
        ["event_happened/3", "participant_statement/4"],
    )

    payload = merge_compile_files(baseline, candidate)
    facts = payload["compile"]["source_compile"]["facts"]

    assert "source_record_text_atom(src_line_001, candidate_source)." in facts
    assert "source_record_text_atom(src_line_001, baseline_source)." not in facts
    assert "vote_cast(event_1, alice, yes, item_1)." in facts
    assert "participant_statement(statement_1, alice, meeting_1, concern)." in facts
    assert facts.count("event_happened(event_1, opened, 2026_01_01).") == 1
    assert payload["metadata"]["baseline_direct_fact_count"] == 2
    assert payload["metadata"]["candidate_direct_fact_count"] == 2
    assert payload["metadata"]["merged_direct_fact_count"] == 3
    assert set(payload["compile"]["parsed"]["candidate_predicates"]) == {
        "event_happened/3",
        "vote_cast/4",
        "participant_statement/4",
    }

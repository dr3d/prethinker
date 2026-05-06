import json
from pathlib import Path

from scripts.validate_autolab_candidate_artifacts import build_report


def _write_source_candidate(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "autolab_source_candidate_v1",
                "candidate_id": "board_minutes_001",
                "source_url": "https://example.test/minutes",
                "domain_label": "governance",
                "why_it_is_hard": ["authority_chain", "temporal_status"],
                "expected_sparse_score": "medium",
                "provenance_notes": "Public meeting minutes with amendment language.",
                "source_text_path": "tmp/hermes_mailbox/runs/board_minutes_001/source.md",
                "do_not_use_reason": "",
            }
        ),
        encoding="utf-8",
    )


def _write_qa_candidate(path: Path, *, include_answer: bool = False, mode: str = "not_established") -> None:
    rows = []
    surfaces = ["temporal_status", "authority_chain", "absence"]
    modes = ["exact", "uncertain", mode]
    for index in range(1, 11):
        row = {
            "qid": f"q{index:03d}",
            "question": f"What does the packet establish about row {index}?",
            "surface_family": surfaces[index % len(surfaces)],
            "expected_answer_mode": modes[index % len(modes)],
            "source_anchor": "section label",
            "why_this_is_hard": "The source is sparse and cross-referenced.",
        }
        if include_answer and index == 3:
            row["answer"] = "leaked oracle"
        rows.append(row)
    path.write_text(
        json.dumps(
            {
                "schema_version": "autolab_candidate_qa_v1",
                "source_candidate_id": "board_minutes_001",
                "rows": rows,
            }
        ),
        encoding="utf-8",
    )


def test_autolab_candidate_validator_accepts_hunter_and_qa_shapes(tmp_path: Path) -> None:
    source = tmp_path / "source_candidate.json"
    qa = tmp_path / "qa_candidate.json"
    _write_source_candidate(source)
    _write_qa_candidate(qa)

    report = build_report(source_paths=[source], qa_paths=[qa])

    assert report["summary"]["passed_artifact_count"] == 2
    assert report["summary"]["failed_artifact_count"] == 0
    assert report["artifacts"][1]["qa"]["row_count"] == 10


def test_autolab_candidate_validator_blocks_answer_keys(tmp_path: Path) -> None:
    qa = tmp_path / "qa_candidate.json"
    _write_qa_candidate(qa, include_answer=True)

    report = build_report(source_paths=[], qa_paths=[qa])

    assert report["summary"]["failed_artifact_count"] == 1
    assert any("contains_answer_key" in item for item in report["artifacts"][0]["errors"])


def test_autolab_candidate_validator_requires_sparse_qa_size(tmp_path: Path) -> None:
    qa = tmp_path / "too_short.json"
    qa.write_text(
        json.dumps(
            {
                "schema_version": "autolab_candidate_qa_v1",
                "source_candidate_id": "tiny",
                "rows": [
                    {
                        "qid": "q001",
                        "question": "Too little?",
                        "surface_family": "absence",
                        "expected_answer_mode": "clarification",
                        "why_this_is_hard": "The packet is too thin.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    report = build_report(source_paths=[], qa_paths=[qa])

    assert "row_count_expected_10_to_25_got_1" in report["artifacts"][0]["errors"]

import json
from pathlib import Path

from scripts.audit_governed_subject_stability import build_report


def _write_compile(path: Path, facts: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"source_compile": {"facts": facts}}), encoding="utf-8")
    return path


def test_subject_stability_counts_repeated_claim_ground_keys(tmp_path: Path) -> None:
    first = _write_compile(
        tmp_path / "run1" / "compile.json",
        [
            "claim_ground(set_a, anticipated, ref_alpha, rejected).",
            "claim_range(set_a, 1, 1, src_line_0001).",
        ],
    )
    second = _write_compile(
        tmp_path / "run2" / "compile.json",
        [
            "claim_ground(alpha_subject, anticipation, reference_alpha, rejected).",
            "review_outcome(alpha_subject, review_board, affirmed, src_line_0002).",
        ],
    )
    third = _write_compile(
        tmp_path / "run3" / "compile.json",
        [
            "claim_range(range_only, 1, 1, src_line_0003).",
        ],
    )

    report = build_report([first, second, third])

    key = "anticipation|reference_alpha|rejected"
    assert report["repeated_claim_ground_keys"] == {key: ["run1", "run2"]}
    assert report["summary"]["runs_with_keyable_subjects"] == 2
    assert report["summary"]["runs_without_keyable_subjects"] == 1
    assert report["runs"][2]["unkeyable_subjects"] == [
        {"subject": "range_only", "predicates": ["claim_range"], "claim_ground_keys": []}
    ]

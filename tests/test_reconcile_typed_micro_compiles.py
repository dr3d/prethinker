import json
from pathlib import Path

from scripts.reconcile_typed_micro_compiles import build_reconciliation


def _write_compile(path: Path, facts: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"source_compile": {"facts": facts}}, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def test_reconciles_subject_id_drift_using_governed_claim_ground_key(tmp_path: Path) -> None:
    first = _write_compile(
        tmp_path / "run_a" / "compile.json",
        [
            "claim_ground(set_a, anticipated, ref_alpha, rejected).",
            "claim_range(set_a, 1, 1, src_line_0001).",
            "legal_citation_detail(set_a, sec_102a1, statutory_basis, src_line_0002).",
        ],
    )
    second = _write_compile(
        tmp_path / "run_b" / "compile.json",
        [
            "claim_ground(alpha_subject, anticipation, reference_alpha, rejected).",
            "review_outcome(alpha_subject, actor_board, affirmation_outcome, src_line_0003).",
            "source_record_surface_mention(src, alpha, display).",
        ],
    )

    report = build_reconciliation(fixture_id="fixture", compile_paths=[first, second])
    facts = set(report["artifact"]["source_compile"]["facts"])

    subject = "claim_issue_anticipation_reference_alpha_rejected"
    assert f"claim_ground({subject}, anticipation, reference_alpha, rejected)." in facts
    assert f"claim_range({subject}, 1, 1, src_line_0001)." in facts
    assert f"legal_citation_detail({subject}, section_102_a_1, statutory_ground, src_line_0002)." in facts
    assert f"review_outcome({subject}, review_board, affirmed, src_line_0003)." in facts
    assert "source_record_surface_mention(src, alpha, display)." not in facts
    assert report["summary"]["blocking_errors"] == 0


def test_unmapped_subject_facts_are_reported_but_not_reconciled(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "run_a" / "compile.json",
        [
            "review_outcome(board_event, board, affirmed, src_line_0001).",
            "claim_range(orphan_set, 1, 3, src_line_0002).",
        ],
    )

    report = build_reconciliation(fixture_id="fixture", compile_paths=[compile_json])

    assert report["artifact"]["source_compile"]["facts"] == []
    skipped_reasons = {item["reason"] for item in report["artifact"]["source_compile"]["governed_reconciliation"]["skipped"]}
    assert skipped_reasons == {"unmapped_subject"}

import json
from pathlib import Path

from scripts.audit_lens_vocabulary_transfer import EVIDENCE_PROVENANCE_TERMS, audit_compile, summarize_reports


def _write_compile(path: Path, facts: list[str]) -> Path:
    path.write_text(
        json.dumps(
            {
                "parsed_ok": True,
                "source_compile": {"facts": facts},
            }
        ),
        encoding="utf-8",
    )
    return path


def test_lens_vocabulary_audit_classifies_structural_and_source_only_terms(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, report_commissioned_and_later_revised).",
            "report_commissioned_by(report_a, board, 2026_04_02).",
            "report_date(report_a, 2026_04_02).",
        ],
    )

    report = audit_compile(compile_json, lens="evidence_provenance", terms=EVIDENCE_PROVENANCE_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["commissioned"] == "structural"
    assert rows["dated"] == "structural"
    assert rows["corrected"] == "source_only"


def test_lens_vocabulary_audit_marks_shallow_structural_when_slots_are_missing(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, summary_presented_by_mina_to_circle).",
            "presented_to(summary_a, circle).",
        ],
    )

    report = audit_compile(compile_json, lens="evidence_provenance", terms=EVIDENCE_PROVENANCE_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["presented"] == "shallow_structural"


def test_lens_vocabulary_summary_counts_terms(tmp_path: Path) -> None:
    first = audit_compile(
        _write_compile(
            tmp_path / "first.json",
            [
                "source_record_text_atom(src_1, report_prepared_by_clerk).",
                "report_prepared_by(report_a, clerk).",
            ],
        ),
        lens="evidence_provenance",
        terms=EVIDENCE_PROVENANCE_TERMS,
    )
    second = audit_compile(
        _write_compile(
            tmp_path / "second.json",
            ["source_record_text_atom(src_1, report_prepared_by_clerk)."],
        ),
        lens="evidence_provenance",
        terms=EVIDENCE_PROVENANCE_TERMS,
    )

    summary = summarize_reports([first, second], EVIDENCE_PROVENANCE_TERMS)

    assert summary["term_status_counts"]["prepared"]["structural"] == 1
    assert summary["term_status_counts"]["prepared"]["source_only"] == 1

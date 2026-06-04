from pathlib import Path

from scripts.audit_research_artifact_paths import audit_docs


def test_audit_research_artifact_paths_checks_inline_paths(tmp_path: Path) -> None:
    (tmp_path / "tmp" / "artifact").mkdir(parents=True)
    doc = tmp_path / "doc.md"
    doc.write_text(
        "\n".join(
            [
                "Existing: `tmp/artifact`.",
                "Missing: `tmp/missing_artifact`.",
                "Example: `tmp/compile_fact_qa_manifest_run`.",
                "```text",
                "Fenced missing should not count: `tmp/fenced_missing`",
                "```",
            ]
        ),
        encoding="utf-8",
    )

    report = audit_docs(root=tmp_path, docs=[Path("doc.md")])

    assert report["summary"] == {
        "checked_count": 2,
        "missing_count": 1,
        "skipped_doc_count": 0,
        "status": "fail",
    }
    assert report["missing"][0]["path"] == "tmp/missing_artifact"


def test_audit_research_artifact_paths_skips_missing_docs(tmp_path: Path) -> None:
    report = audit_docs(root=tmp_path, docs=[Path("missing.md")])

    assert report["summary"] == {
        "checked_count": 0,
        "missing_count": 0,
        "skipped_doc_count": 1,
        "status": "fail",
    }
    assert report["skipped_docs"] == ["missing.md"]

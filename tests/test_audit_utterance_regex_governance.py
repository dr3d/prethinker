import textwrap
from pathlib import Path

from scripts.audit_utterance_regex_governance import build_report


def test_utterance_regex_audit_classifies_semantic_trigger(tmp_path: Path) -> None:
    path = tmp_path / "sample.py"
    path.write_text(
        textwrap.dedent(
            """
            import re

            def route(utterance):
                return re.search(r"\\b(?:heading|section)\\b", utterance)
            """
        ),
        encoding="utf-8",
    )

    report = build_report((path,))

    assert report["summary"]["regex_hit_count"] == 1
    assert report["rows"][0]["category"] == "semantic_trigger"


def test_utterance_regex_audit_ignores_file_path_for_allowed_hints(tmp_path: Path) -> None:
    path = tmp_path / "identifier_scratch" / "sample.py"
    path.parent.mkdir()
    path.write_text(
        textwrap.dedent(
            """
            import re

            def route(utterance):
                return re.search(r"\\b(?:heading|section)\\b", utterance)
            """
        ),
        encoding="utf-8",
    )

    report = build_report((path,))

    assert report["summary"]["regex_hit_count"] == 1
    assert report["rows"][0]["category"] == "semantic_trigger"


def test_utterance_regex_audit_treats_compiled_regex_subject_separately(tmp_path: Path) -> None:
    path = tmp_path / "sample.py"
    path.write_text(
        textwrap.dedent(
            """
            import re

            TOKEN_RE = re.compile(r"[A-Za-z0-9]+")

            def tokens_from_question(question):
                return TOKEN_RE.findall(question)
            """
        ),
        encoding="utf-8",
    )

    report = build_report((path,))

    assert report["summary"]["regex_hit_count"] == 1
    assert report["rows"][0]["pattern"] == "<compiled-regex>"
    assert report["rows"][0]["subject"] == "question"

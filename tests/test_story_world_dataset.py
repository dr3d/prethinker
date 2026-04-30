import json
from pathlib import Path

from scripts.run_domain_bootstrap_qa import (
    parse_markdown_answer_key,
    parse_numbered_markdown_questions,
)


ROOT = Path(__file__).resolve().parents[1]
OTTERS = ROOT / "datasets" / "story_worlds" / "otters_clockwork_pie"


def test_otters_story_world_bundle_is_complete() -> None:
    expected = {
        "README.md",
        "story.md",
        "gold_kb.pl",
        "gold_kb_notes.md",
        "qa_source.md",
        "qa.md",
        "qa_battery.jsonl",
        "intake_plan.md",
    }

    assert expected.issubset({path.name for path in OTTERS.iterdir()})


def test_otters_qa_battery_is_harness_ready() -> None:
    records = [
        json.loads(line)
        for line in (OTTERS / "qa_battery.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 100
    assert records[0]["id"] == "q001"
    assert records[-1]["id"] == "q100"
    assert "Goldilocks" in records[0]["likely_mistake"]

    qa_text = (OTTERS / "qa.md").read_text(encoding="utf-8")
    questions = parse_numbered_markdown_questions(qa_text)
    answers = parse_markdown_answer_key(qa_text)
    assert len(questions) == 100
    assert len(answers) == 100
    assert questions[0]["id"] == "q001"
    assert "Little Slip of an Otter" in answers["q001"]


def test_otters_gold_kb_exercises_story_world_edges() -> None:
    kb = (OTTERS / "gold_kb.pl").read_text(encoding="utf-8")
    assert kb.count("event(") >= 100
    assert kb.count("story_time(") >= 100
    assert "judged(tilly_tumbletop" in kb
    assert "said(" in kb
    assert "final_state(" in kb
    assert "before(E1, E2)" in kb


def test_otters_fixture_text_is_ascii_stable() -> None:
    for path in OTTERS.iterdir():
        if path.suffix.lower() not in {".md", ".pl", ".jsonl"}:
            continue
        text = path.read_text(encoding="utf-8")
        assert all(ord(char) < 128 for char in text), path.name

import json
import re
from pathlib import Path

from scripts.run_domain_bootstrap_qa import (
    parse_markdown_answer_key,
    parse_numbered_markdown_questions,
)


ROOT = Path(__file__).resolve().parents[1]
OTTERS = ROOT / "datasets" / "story_worlds" / "otters_clockwork_pie"
IRON_HARBOR = ROOT / "datasets" / "story_worlds" / "iron_harbor_water_crisis"


def test_otters_story_world_bundle_is_complete() -> None:
    expected = {
        "README.md",
        "story.md",
        "gold_kb.pl",
        "gold_kb_notes.md",
        "ontology_registry.json",
        "failure_buckets.json",
        "qa_source.md",
        "qa.md",
        "qa_battery.jsonl",
        "intake_plan.md",
        "progress_journal.md",
        "progress_metrics.jsonl",
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
    assert "location_after_event(clockwork_pie, e005, windowsill)." in kb
    for forbidden in ["goldilocks", "bear", "bears", "porridge", "chair", "chairs", "bed", "beds"]:
        assert re.search(rf"(?<![a-z0-9_]){forbidden}(?![a-z0-9_])", kb.casefold()) is None


def test_otters_metadata_is_graph_ready() -> None:
    buckets = json.loads((OTTERS / "failure_buckets.json").read_text(encoding="utf-8"))
    registry = json.loads((OTTERS / "ontology_registry.json").read_text(encoding="utf-8"))
    metrics = [
        json.loads(line)
        for line in (OTTERS / "progress_metrics.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(buckets["buckets"]) >= 10
    assert any(item["id"] == "template_contamination" for item in buckets["buckets"])
    assert registry["source"] == "gold_kb.pl"
    signatures = {item["signature"] for item in registry["predicates"]}
    for signature in ["event/5", "story_time/2", "before/2", "judged/4", "final_state/1"]:
        assert signature in signatures
    assert [row["timestamp"] for row in metrics] == sorted(row["timestamp"] for row in metrics)


def test_otters_fixture_text_is_ascii_stable() -> None:
    for path in OTTERS.iterdir():
        if path.suffix.lower() not in {".md", ".pl", ".jsonl"}:
            continue
        text = path.read_text(encoding="utf-8")
        assert all(ord(char) < 128 for char in text), path.name


def test_iron_harbor_story_world_bundle_is_complete() -> None:
    expected = {
        "README.md",
        "story.md",
        "gold_kb.pl",
        "gold_kb_notes.md",
        "ontology_registry.json",
        "failure_buckets.json",
        "qa_source.md",
        "qa.md",
        "qa_battery.jsonl",
        "intake_plan.md",
        "progress_journal.md",
        "progress_metrics.jsonl",
    }

    assert expected.issubset({path.name for path in IRON_HARBOR.iterdir()})


def test_iron_harbor_qa_battery_is_harness_ready() -> None:
    records = [
        json.loads(line)
        for line in (IRON_HARBOR / "qa_battery.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 100
    assert records[0]["id"] == "q001"
    assert records[0]["source_id"] == "IH-001"
    assert records[-1]["id"] == "q100"
    assert records[-1]["source_id"] == "IH-100"
    assert records[23]["expected_answer"].startswith("No -- his last inspection was February 1")

    qa_text = (IRON_HARBOR / "qa.md").read_text(encoding="utf-8")
    questions = parse_numbered_markdown_questions(qa_text)
    answers = parse_markdown_answer_key(qa_text)
    assert len(questions) == 100
    assert len(answers) == 100
    assert questions[0]["id"] == "q001"
    assert "85 CFU/100mL" in answers["q001"]


def test_iron_harbor_metadata_is_graph_ready() -> None:
    buckets = json.loads((IRON_HARBOR / "failure_buckets.json").read_text(encoding="utf-8"))
    registry = json.loads((IRON_HARBOR / "ontology_registry.json").read_text(encoding="utf-8"))
    metrics = [
        json.loads(line)
        for line in (IRON_HARBOR / "progress_metrics.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(buckets["buckets"]) >= 10
    assert any(item["id"] == "false_positive_violation" for item in buckets["buckets"])
    assert registry["source"] == "gold_kb.pl"
    signatures = {item["signature"] for item in registry["predicates"]}
    for signature in ["coliform_reading/4", "bypass_authorization/3", "notification/5", "before/2"]:
        assert signature in signatures
    assert [row["timestamp"] for row in metrics] == sorted(row["timestamp"] for row in metrics)


def test_iron_harbor_fixture_text_is_ascii_stable() -> None:
    for path in IRON_HARBOR.iterdir():
        if path.suffix.lower() not in {".md", ".pl", ".json", ".jsonl"}:
            continue
        text = path.read_text(encoding="utf-8")
        assert all(ord(char) < 128 for char in text), path.name


def test_iron_harbor_traps_do_not_import_obvious_false_priors() -> None:
    story = (IRON_HARBOR / "story.md").read_text(encoding="utf-8").casefold()
    kb = (IRON_HARBOR / "gold_kb.pl").read_text(encoding="utf-8").casefold()

    assert "old harbor is not included in the notice" in story
    assert "non_residential_zone(foundry_row)" in kb
    assert re.search(r"(?<![a-z0-9_])residential_zone\(foundry_row\)", kb) is None
    assert "boil_water_notice(old_harbor" not in kb
    assert "inspection(pier_7_chlorination_unit, luis_ferreira, '2026-02-01')" in kb
    assert "inspection(pier_7_chlorination_unit, luis_ferreira, '2026-01-28')" not in kb

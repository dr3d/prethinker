from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = REPO_ROOT / "datasets" / "real_world_transfer" / "20260521"
PILOT_ROOT = REPO_ROOT / "datasets" / "real_world_transfer" / "20260523"
NTSB_TWO_DOC_ROOT = REPO_ROOT / "datasets" / "real_world_transfer" / "20260523_ntsb_pilot_2doc"

EXPECTED_FIXTURES = {
    "cpsc_recall_polaris_rzr200_2023",
    "fda_recall_wiers_farm_2024",
    "federal_register_flra_fsip_2024",
    "ntsb_marine_carol_jean_2023",
}


def test_real_world_transfer_fixtures_are_retained() -> None:
    fixture_dirs = {path.name for path in DATASET_ROOT.iterdir() if path.is_dir()}

    assert EXPECTED_FIXTURES <= fixture_dirs

    for fixture in EXPECTED_FIXTURES:
        fixture_root = DATASET_ROOT / fixture
        for name in ("source.md", "qa.md", "oracle.jsonl"):
            assert (fixture_root / name).is_file(), f"{fixture} missing {name}"


def test_real_world_transfer_oracles_keep_forty_row_shape() -> None:
    for fixture in EXPECTED_FIXTURES:
        oracle_path = DATASET_ROOT / fixture / "oracle.jsonl"
        rows = [
            json.loads(line)
            for line in oracle_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        ids = [row["id"] for row in rows]

        assert len(rows) == 40, f"{fixture} should retain 40 oracle rows"
        assert len(set(ids)) == 40, f"{fixture} should retain unique row ids"
        assert ids[0] == "q001"
        assert ids[-1] == "q040"


def test_real_world_transfer_pilot_fixture_is_retained() -> None:
    fixture = "ntsb_aviation_001"
    fixture_root = PILOT_ROOT / fixture

    assert fixture_root.is_dir()
    for name in (
        "source.md",
        "source_original.pdf",
        "story.md",
        "qa.md",
        "oracle.jsonl",
        "qa_questions.jsonl",
        "qa_battery.json",
        "metadata.json",
        "provenance.md",
        "README.md",
        "fixture_notes.md",
        "anti_leakage_manifest.md",
    ):
        assert (fixture_root / name).is_file(), f"{fixture} missing {name}"


def test_real_world_transfer_pilot_keeps_twenty_five_row_shape() -> None:
    fixture = "ntsb_aviation_001"
    fixture_root = PILOT_ROOT / fixture
    oracle_rows = [
        json.loads(line)
        for line in (fixture_root / "oracle.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    question_rows = [
        json.loads(line)
        for line in (fixture_root / "qa_questions.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    qa_battery = json.loads((fixture_root / "qa_battery.json").read_text(encoding="utf-8"))

    assert len(oracle_rows) == 25
    assert len(question_rows) == 25
    assert len(qa_battery) == 25
    assert [row["id"] for row in oracle_rows] == [f"q{i:03d}" for i in range(1, 26)]
    assert [row["id"] for row in question_rows] == [f"q{i:03d}" for i in range(1, 26)]
    assert all("reference_answer" not in row for row in question_rows)
    assert all("reference_answer" in row for row in qa_battery)


def test_real_world_transfer_ntsb_two_doc_pilot_is_retained() -> None:
    for fixture in ("ntsb_001", "ntsb_002"):
        fixture_root = NTSB_TWO_DOC_ROOT / fixture

        assert fixture_root.is_dir()
        for name in (
            "source.md",
            "source_original.pdf",
            "story.md",
            "qa.md",
            "qa_authored.md",
            "oracle.jsonl",
            "qa_questions.jsonl",
            "qa_battery.json",
            "metadata.json",
            "provenance.md",
            "README.md",
            "fixture_notes.md",
            "anti_leakage_manifest.md",
        ):
            assert (fixture_root / name).is_file(), f"{fixture} missing {name}"


def test_real_world_transfer_ntsb_two_doc_pilot_keeps_twenty_five_row_shape() -> None:
    for fixture in ("ntsb_001", "ntsb_002"):
        fixture_root = NTSB_TWO_DOC_ROOT / fixture
        oracle_rows = [
            json.loads(line)
            for line in (fixture_root / "oracle.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        question_rows = [
            json.loads(line)
            for line in (fixture_root / "qa_questions.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        qa_battery = json.loads((fixture_root / "qa_battery.json").read_text(encoding="utf-8"))

        assert len(oracle_rows) == 25
        assert len(question_rows) == 25
        assert len(qa_battery) == 25
        assert [row["id"] for row in oracle_rows] == [f"q{i:03d}" for i in range(1, 26)]
        assert [row["id"] for row in question_rows] == [f"q{i:03d}" for i in range(1, 26)]
        assert all("reference_answer" not in row for row in question_rows)
        assert all("reference_answer" in row for row in qa_battery)

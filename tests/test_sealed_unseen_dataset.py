from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = REPO_ROOT / "datasets" / "sealed_unseen" / "20260521"

EXPECTED_FIXTURES = {
    "civic_hearing_correction_packet",
    "clinical_recall_source_packet",
    "grant_exception_vote_matrix",
    "lease_amendment_status_register",
}


def test_sealed_unseen_fixtures_are_retained() -> None:
    fixture_dirs = {path.name for path in DATASET_ROOT.iterdir() if path.is_dir()}

    assert EXPECTED_FIXTURES <= fixture_dirs

    for fixture in EXPECTED_FIXTURES:
        fixture_root = DATASET_ROOT / fixture
        for name in ("source.md", "qa.md", "oracle.jsonl"):
            assert (fixture_root / name).is_file(), f"{fixture} missing {name}"


def test_sealed_unseen_oracles_keep_forty_row_shape() -> None:
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

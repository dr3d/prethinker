from __future__ import annotations

import json
from pathlib import Path

from scripts.build_router_training_set import build_router_training_rows


def test_router_training_builder_produces_seed_corpus():
    rows = build_router_training_rows()
    profiles = {row["expected_profile"] for row in rows}

    assert len(rows) >= 100
    assert {
        "medical@v0",
        "legal_courtlistener@v0",
        "sec_contracts@v0",
        "story_world@v0",
        "probate@v0",
    } <= profiles
    assert all(row["schema_version"] == "semantic_router_training_v1" for row in rows)


def test_router_training_seed_file_is_current_jsonl():
    path = Path("docs/data/router_training/router_training_seed_v1.jsonl")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    assert len(rows) >= 100
    assert rows[0]["schema_version"] == "semantic_router_training_v1"

from __future__ import annotations

from scripts.build_router_training_set import build_router_training_rows


def test_router_training_builder_produces_seed_corpus():
    rows = build_router_training_rows()
    profiles = {row["expected_profile"] for row in rows}

    assert len(rows) >= 80
    assert {
        "medical@v0",
        "legal_courtlistener@v0",
        "sec_contracts@v0",
        "story_world@v0",
        "probate@v0",
    } <= profiles
    assert all(row["schema_version"] == "semantic_router_training_v1" for row in rows)


def test_router_training_rows_are_deduplicated():
    rows = build_router_training_rows()
    keys = {
        (
            row["utterance"],
            "\n".join(row["context"]),
            row["expected_profile"],
        )
        for row in rows
    }

    assert len(keys) == len(rows)

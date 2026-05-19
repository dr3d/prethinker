import json
from pathlib import Path

from scripts.build_compile_preservation_candidate import (
    build_preservation_candidate,
    _signatures_from_stability,
)


def _write(path: Path, payload: dict[str, object]) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_preservation_candidate_merges_only_selected_direct_carriers(tmp_path: Path) -> None:
    anchor = _write(
        tmp_path / "anchor.json",
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "source_authority/3"}]},
            "source_compile": {
                "facts": [
                    "source_record_text_atom(src_1, authority_statement).",
                    "lease_status(lease_a, active).",
                ]
            },
        },
    )
    draw_with_authority = _write(
        tmp_path / "draw_with_authority.json",
        {
            "parsed_ok": True,
            "parsed": {
                "candidate_predicates": [
                    {"signature": "source_authority/3"},
                    {"signature": "source_attributed_claim/4"},
                ]
            },
            "source_compile": {
                "facts": [
                    "source_record_text_atom(src_1, alternate_source).",
                    "source_authority(item_a, reader_one, policy_a).",
                    "source_attributed_claim(claim_1, policy_a, item_a, active).",
                    "unselected_surface(item_a, extra).",
                ]
            },
        },
    )

    payload = build_preservation_candidate(
        compile_paths=[anchor, draw_with_authority],
        signatures=["source_authority/3"],
    )
    facts = payload["compile"]["source_compile"]["facts"]

    assert "source_record_text_atom(src_1, authority_statement)." in facts
    assert "source_record_text_atom(src_1, alternate_source)." not in facts
    assert "lease_status(lease_a, active)." in facts
    assert "source_authority(item_a, reader_one, policy_a)." in facts
    assert "source_attributed_claim(claim_1, policy_a, item_a, active)." not in facts
    assert "unselected_surface(item_a, extra)." not in facts
    assert payload["metadata"]["added_direct_fact_count"] == 1
    assert payload["metadata"]["selected_signatures"] == ["source_authority/3"]


def test_signatures_from_stability_keeps_only_preservation_candidates(tmp_path: Path) -> None:
    stability = _write(
        tmp_path / "stability.json",
        {
            "fixtures": [
                {
                    "fixture": "fixture_a",
                    "profile_delivery_telemetry": [
                        {
                            "response_hint": "multi_draw_preservation_candidate",
                            "carrier_delivery": [
                                {
                                    "carrier": "source_authority/3",
                                    "draws_with_rows": 1,
                                },
                                {
                                    "carrier": "claim_made/3",
                                    "draws_with_rows": 0,
                                },
                            ],
                        },
                        {
                            "response_hint": "compile_retry_or_projection_candidate",
                            "carrier_delivery": [
                                {
                                    "carrier": "status_state_at/4",
                                    "draws_with_rows": 0,
                                }
                            ],
                        },
                    ],
                },
                {
                    "fixture": "fixture_b",
                    "profile_delivery_telemetry": [
                        {
                            "response_hint": "multi_draw_preservation_candidate",
                            "carrier_delivery": [
                                {
                                    "carrier": "other_surface/2",
                                    "draws_with_rows": 1,
                                }
                            ],
                        }
                    ],
                },
            ]
        },
    )

    assert _signatures_from_stability(stability, fixture="fixture_a") == ["source_authority/3"]
    assert _signatures_from_stability(stability, fixture="") == ["other_surface/2", "source_authority/3"]

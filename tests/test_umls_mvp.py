from __future__ import annotations

from src import umls_mvp


def test_normalize_lookup_text_collapses_spacing_and_punctuation():
    assert umls_mvp.normalize_lookup_text(" HbA1c / test ") == "hba1c test"


def test_choose_best_candidate_prefers_source_then_tty_then_ispref():
    candidates = [
        {
            "cui": "C2",
            "sab": "LOINC",
            "tty": "SY",
            "ispref": "N",
            "str": "Hemoglobin A1c",
            "alias_rank": 0,
        },
        {
            "cui": "C1",
            "sab": "RXNORM",
            "tty": "IN",
            "ispref": "Y",
            "str": "Metformin",
            "alias_rank": 0,
        },
    ]
    best = umls_mvp.choose_best_candidate(
        candidates,
        preferred_sources=["RXNORM"],
        global_priority=["SNOMEDCT_US", "RXNORM", "LOINC"],
    )
    assert best is not None
    assert best["cui"] == "C1"


def test_extract_grounded_mentions_prefers_longest_non_overlapping_aliases():
    alias_records = [
        {"alias": "blood pressure", "seed_id": "pressure", "preferred_name": "Blood pressure"},
        {"alias": "high blood pressure", "seed_id": "hypertension", "preferred_name": "Hypertension"},
        {"alias": "type 2 diabetes", "seed_id": "t2dm", "preferred_name": "Type 2 diabetes mellitus"},
    ]
    matches = umls_mvp.extract_grounded_mentions(
        "She has high blood pressure and type 2 diabetes.",
        alias_records,
    )
    assert [row["seed_id"] for row in matches] == ["hypertension", "t2dm"]


def test_render_sharp_memory_facts_includes_seed_aliases_and_types():
    facts = umls_mvp.render_sharp_memory_facts(
        [
            {
                "seed_id": "metformin",
                "cui": "C0025598",
                "preferred_name": "Metformin",
                "semantic_types": [{"tui": "T121", "sty": "Pharmacologic Substance"}],
                "aliases": [{"text": "Glucophage"}],
            }
        ],
        [],
    )
    assert "umls_seed(metformin, 'C0025598')." in facts
    assert "umls_alias(metformin, 'Glucophage')." in facts
    assert "umls_semantic_type(metformin, 'T121', 'Pharmacologic Substance')." in facts


def test_seed_alias_map_includes_probe_aliases():
    mapping = umls_mvp.seed_alias_map(
        {
            "concept_seeds": [
                {
                    "seed_id": "shortness_of_breath",
                    "seed_aliases": ["shortness of breath"],
                    "probe_aliases": ["short of breath"],
                }
            ]
        }
    )
    assert "short of breath" in mapping
    assert mapping["short of breath"][0]["seed_id"] == "shortness_of_breath"


def test_inject_requested_alias_rows_adds_missing_curated_aliases():
    rows = umls_mvp.inject_requested_alias_rows(
        [{"text": "Shortness of breath", "sab": "SNOMEDCT_US", "tty": "PT", "ispref": "Y"}],
        {"short of breath", "shortness of breath"},
    )
    texts = {umls_mvp.normalize_lookup_text(row["text"]) for row in rows}
    assert "shortness of breath" in texts
    assert "short of breath" in texts

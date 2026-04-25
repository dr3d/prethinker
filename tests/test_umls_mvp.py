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


def test_semantic_group_for_tui_maps_umls_types_to_profile_groups():
    assert umls_mvp.semantic_group_for_tui("T195", "Antibiotic") == "medication"
    assert umls_mvp.semantic_group_for_tui("T047", "Disease or Syndrome") == "condition"
    assert umls_mvp.semantic_group_for_tui("T184", "Sign or Symptom") == "symptom_or_finding"
    assert umls_mvp.semantic_group_for_tui("T059", "Laboratory Procedure") == "lab_or_procedure"


def test_concept_semantic_groups_adds_bounded_seed_overrides():
    groups = umls_mvp.concept_semantic_groups(
        {
            "seed_id": "penicillin_allergy",
            "semantic_types": [{"tui": "T047", "sty": "Disease or Syndrome"}],
        }
    )
    assert groups == ["condition", "allergy"]


def test_render_umls_bridge_facts_includes_normalized_aliases_and_groups():
    facts = umls_mvp.render_umls_bridge_facts(
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
    assert "umls_concept(metformin, 'C0025598')." in facts
    assert "umls_preferred_atom(metformin, metformin)." in facts
    assert "umls_semantic_group(metformin, medication)." in facts
    assert "umls_alias_norm(metformin, glucophage)." in facts


def test_load_semantic_network_reads_srdef_srstr_and_inherited_relations(tmp_path):
    (tmp_path / "SRDEF").write_text(
        "\n".join(
            [
                "STY|T047|Disease or Syndrome|B2.2.1.2.1|A condition.|Disease example|Use note|N|dsyn|",
                "STY|T033|Finding|A2.2|An observation.|Finding example|Use note|N|fndg|",
                "RL|T186|isa|R1|Hierarchical relation.||||isa|inverse_isa",
                "RL|T151|affects|R3|Affects relation.||||affects|affected_by",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "SRSTR").write_text(
        "\n".join(
            [
                "Finding|isa||D",
                "Disease or Syndrome|isa|Finding|D",
                "Disease or Syndrome|affects|Organism|D",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "SRSTRE2").write_text(
        "Disease or Syndrome|affects|Organism|\n",
        encoding="utf-8",
    )
    (tmp_path / "SRSTRE1").write_text(
        "T047|T151|T001|\n",
        encoding="utf-8",
    )

    network = umls_mvp.load_semantic_network(tmp_path)

    assert [row["ui"] for row in network["semantic_types"]] == ["T033", "T047"]
    assert [row["name"] for row in network["semantic_relations"]] == ["affects", "isa"]
    assert any(row["source"] == "Disease or Syndrome" and row["target"] == "Finding" for row in network["structure"])
    assert network["inherited_ui_relations"][0]["source"] == "T047"
    assert network["inherited_name_relations"][0]["relation_atom"] == "affects"


def test_render_semantic_network_facts_includes_roots_parents_and_relations(tmp_path):
    (tmp_path / "SRDEF").write_text(
        "STY|T047|Disease or Syndrome|B2.2.1.2.1|A condition.||||dsyn|\n"
        "RL|T151|affects|R3|Affects relation.||||affects|affected_by\n",
        encoding="utf-8",
    )
    (tmp_path / "SRSTR").write_text(
        "Disease or Syndrome|isa|Finding|D\n"
        "Entity|isa||D\n",
        encoding="utf-8",
    )
    (tmp_path / "SRSTRE1").write_text(
        "T047|T151|T001|\n",
        encoding="utf-8",
    )
    network = umls_mvp.load_semantic_network(tmp_path)
    facts = umls_mvp.render_semantic_network_facts(network)

    assert "umls_semantic_type_def('T047', disease_or_syndrome, 'Disease or Syndrome', 'B2.2.1.2.1')." in facts
    assert "umls_semantic_relation_def('T151', affects, 'affects', 'affected_by')." in facts
    assert "umls_semantic_parent(disease_or_syndrome, finding, 'D')." in facts
    assert "umls_semantic_root(entity)." in facts
    assert "umls_semantic_inherited_ui_relation('T047', 'T151', 'T001')." in facts


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

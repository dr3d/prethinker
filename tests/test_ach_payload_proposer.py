from scripts.run_ach_payload_proposer import (
    build_messages,
    build_scorer_payload,
    proposal_contract_violations,
    public_prompt_payload,
)


def test_ach_payload_prompt_omits_oracle_fields() -> None:
    payload = {
        "fixture_id": "demo",
        "ach_question": "Which hypothesis survives?",
        "hypotheses": [{"id": "h1", "label": "A", "claim": "A happened."}],
        "evidence_rows": [
            {
                "id": "e1",
                "label": "Finding",
                "source_coords": "[A]",
                "text_anchor": "finding text",
                "expected_relevance": "oracle-only explanation",
            }
        ],
        "expected_read": {"best_hypothesis": "h1"},
    }

    prompt_payload = public_prompt_payload(payload)
    messages = build_messages(payload=payload, source_text="finding text")
    joined = "\n".join(message["content"] for message in messages)

    assert "expected_read" not in prompt_payload
    assert "expected_relevance" not in prompt_payload["evidence_rows"][0]
    assert "expected_read" not in joined
    assert "expected_relevance" not in joined
    assert "oracle-only explanation" not in joined
    assert "audit every evidence row as a possible interpretation anchor" in joined


def test_counterfactual_prompt_omits_evidence_row_but_names_omission() -> None:
    payload = {
        "fixture_id": "demo",
        "ach_question": "Which hypothesis survives?",
        "hypotheses": [{"id": "h1"}, {"id": "h2"}],
        "evidence_rows": [{"id": "e1", "label": "One"}, {"id": "e2", "label": "Two"}],
    }

    reduced = {**payload, "evidence_rows": [{"id": "e2", "label": "Two"}]}
    prompt_payload = public_prompt_payload(reduced, omitted_evidence={"id": "e1", "label": "One", "text_anchor": "A"})
    messages = build_messages(payload=reduced, source_text="A and B", omitted_evidence={"id": "e1", "label": "One"})

    assert [item["id"] for item in prompt_payload["evidence_rows"]] == ["e2"]
    assert prompt_payload["counterfactual_mode"] is True
    assert "e1" not in str(prompt_payload)
    assert "One" not in str(prompt_payload)
    assert "counterfactual_mode" in "\n".join(message["content"] for message in messages)


def test_build_scorer_payload_maps_evidence_rows_and_filters_invalid_judgments() -> None:
    payload = {
        "hypotheses": [{"id": "h1", "label": "One", "claim": "One."}, {"id": "h2"}],
        "evidence_rows": [{"id": "e1", "label": "Row 1", "source_coords": "[A]", "text_anchor": "A"}],
    }
    proposal = {
        "hypothesis_axis_fit": [{"hypothesis_id": "h1", "axis_fit": "partial", "rationale": "qualifies"}],
        "evidence_diagnosticity": [{"evidence_id": "e1", "diagnosticity": "critical", "rationale": "direct"}],
        "judgments": [
            {"evidence_id": "e1", "hypothesis_id": "h1", "assessment": "consistent", "weight": 4, "rationale": "fits"},
            {"evidence_id": "e1", "hypothesis_id": "h2", "assessment": "inconsistent", "weight": 5, "rationale": "rules out"},
            {"evidence_id": "e1", "hypothesis_id": "h2", "assessment": "neutral", "weight": 1, "rationale": "duplicate"},
            {"evidence_id": "missing", "hypothesis_id": "h1", "assessment": "consistent", "weight": 2, "rationale": "bad"},
        ],
        "omission_effects": [
            {
                "omitted_evidence_id": "e1",
                "evidence_id": "e1",
                "hypothesis_id": "h1",
                "assessment": "inconsistent",
                "weight": 5,
                "rationale": "self effect ignored",
            }
        ],
    }

    scorer_payload = build_scorer_payload(payload, proposal)

    assert scorer_payload["evidence"] == [
        {
            "id": "e1",
            "label": "Row 1",
            "diagnosticity": "critical",
            "source_coords": "[A]",
            "text_anchor": "A",
        }
    ]
    assert scorer_payload["judgments"] == [
        {"evidence_id": "e1", "hypothesis_id": "h1", "assessment": "consistent", "weight": 4, "rationale": "fits"},
        {"evidence_id": "e1", "hypothesis_id": "h2", "assessment": "inconsistent", "weight": 5, "rationale": "rules out"},
    ]
    assert scorer_payload["hypotheses"] == [
        {"id": "h1", "label": "One", "claim": "One.", "axis_fit": "partial"},
        {"id": "h2", "label": "", "claim": "", "axis_fit": "direct"},
    ]
    assert scorer_payload["omission_effects"] == []


def test_build_scorer_payload_preserves_valid_omission_effects() -> None:
    payload = {
        "hypotheses": [{"id": "h1"}, {"id": "h2"}],
        "evidence_rows": [{"id": "e1"}, {"id": "e2"}],
    }
    proposal = {
        "evidence_diagnosticity": [],
        "judgments": [
            {"evidence_id": "e1", "hypothesis_id": "h1", "assessment": "consistent", "weight": 3, "rationale": ""},
            {"evidence_id": "e1", "hypothesis_id": "h2", "assessment": "inconsistent", "weight": 3, "rationale": ""},
            {"evidence_id": "e2", "hypothesis_id": "h1", "assessment": "consistent", "weight": 2, "rationale": ""},
            {"evidence_id": "e2", "hypothesis_id": "h2", "assessment": "consistent", "weight": 2, "rationale": ""},
        ],
        "omission_effects": [
            {
                "omitted_evidence_id": "e1",
                "evidence_id": "e2",
                "hypothesis_id": "h1",
                "assessment": "inconsistent",
                "weight": 5,
                "rationale": "e2 changes meaning without e1",
            }
        ],
    }

    scorer_payload = build_scorer_payload(payload, proposal)

    assert scorer_payload["omission_effects"] == [
        {
            "omitted_evidence_id": "e1",
            "evidence_id": "e2",
            "hypothesis_id": "h1",
            "assessment": "inconsistent",
            "weight": 5,
            "rationale": "e2 changes meaning without e1",
        }
    ]


def test_build_scorer_payload_converts_judgment_dependencies_to_omission_effects() -> None:
    payload = {
        "hypotheses": [{"id": "h1"}, {"id": "h2"}],
        "evidence_rows": [{"id": "e_anchor"}, {"id": "e_dependent"}],
    }
    proposal = {
        "evidence_diagnosticity": [],
        "judgments": [
            {"evidence_id": "e_anchor", "hypothesis_id": "h1", "assessment": "consistent", "weight": 5, "rationale": ""},
            {"evidence_id": "e_anchor", "hypothesis_id": "h2", "assessment": "neutral", "weight": 1, "rationale": ""},
            {"evidence_id": "e_dependent", "hypothesis_id": "h1", "assessment": "consistent", "weight": 3, "rationale": ""},
            {"evidence_id": "e_dependent", "hypothesis_id": "h2", "assessment": "neutral", "weight": 1, "rationale": ""},
        ],
        "judgment_dependencies": [
            {
                "evidence_id": "e_dependent",
                "hypothesis_id": "h1",
                "depends_on_evidence_id": "e_anchor",
                "assessment_without_dependency": "inconsistent",
                "weight_without_dependency": 4,
                "rationale": "dependent row changes meaning without anchor",
            }
        ],
        "omission_effects": [],
    }

    scorer_payload = build_scorer_payload(payload, proposal)

    assert scorer_payload["omission_effects"] == [
        {
            "omitted_evidence_id": "e_anchor",
            "evidence_id": "e_dependent",
            "hypothesis_id": "h1",
            "assessment": "inconsistent",
            "weight": 4,
            "rationale": "dependent row changes meaning without anchor",
        }
    ]


def test_proposal_contract_flags_cross_evidence_reference_without_dependency() -> None:
    payload = {
        "evidence_rows": [{"id": "e1"}, {"id": "e2"}],
    }
    proposal = {
        "judgments": [
            {
                "evidence_id": "e2",
                "hypothesis_id": "h1",
                "assessment": "consistent",
                "weight": 3,
                "rationale": "This depends on e1.",
            }
        ],
        "judgment_dependencies": [],
        "omission_effects": [],
    }

    assert proposal_contract_violations(payload, proposal) == [
        {
            "kind": "missing_judgment_dependency",
            "evidence_id": "e2",
            "hypothesis_id": "h1",
            "referenced_evidence_id": "e1",
        }
    ]

    proposal["judgment_dependencies"] = [
        {
            "evidence_id": "e2",
            "hypothesis_id": "h1",
            "depends_on_evidence_id": "e1",
        }
    ]
    assert proposal_contract_violations(payload, proposal) == []

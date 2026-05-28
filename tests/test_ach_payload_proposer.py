from scripts.run_ach_payload_proposer import build_messages, build_scorer_payload, public_prompt_payload


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


def test_build_scorer_payload_maps_evidence_rows_and_filters_invalid_judgments() -> None:
    payload = {
        "hypotheses": [{"id": "h1", "label": "One", "claim": "One."}, {"id": "h2"}],
        "evidence_rows": [{"id": "e1", "label": "Row 1", "source_coords": "[A]", "text_anchor": "A"}],
    }
    proposal = {
        "evidence_diagnosticity": [{"evidence_id": "e1", "diagnosticity": "critical", "rationale": "direct"}],
        "judgments": [
            {"evidence_id": "e1", "hypothesis_id": "h1", "assessment": "consistent", "rationale": "fits"},
            {"evidence_id": "e1", "hypothesis_id": "h2", "assessment": "inconsistent", "rationale": "rules out"},
            {"evidence_id": "e1", "hypothesis_id": "h2", "assessment": "neutral", "rationale": "duplicate"},
            {"evidence_id": "missing", "hypothesis_id": "h1", "assessment": "consistent", "rationale": "bad"},
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
        {"evidence_id": "e1", "hypothesis_id": "h1", "assessment": "consistent", "rationale": "fits"},
        {"evidence_id": "e1", "hypothesis_id": "h2", "assessment": "inconsistent", "rationale": "rules out"},
    ]

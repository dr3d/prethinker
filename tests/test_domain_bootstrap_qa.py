from scripts.run_domain_bootstrap_qa import (
    clause_signature,
    compiled_kb_inventory,
    parse_markdown_answer_key,
    parse_numbered_markdown_questions,
    score_oracle,
)


def test_parse_numbered_markdown_questions_keeps_phase_labels() -> None:
    text = """# Phase 1 - Straight Queries

1. Which items were explicitly declared recalled?
2. Who is the authority accused of wrongdoing?

# Phase 2 - Ambiguity

16. Who is K. Lume?

## Answers 1-16

1. Batch P-44.
16. Unknown unless resolved.
"""

    rows = parse_numbered_markdown_questions(text)

    assert [row["id"] for row in rows] == ["q001", "q002", "q016"]
    assert rows[0]["phase"] == "Phase 1 - Straight Queries"
    assert rows[2]["phase"] == "Phase 2 - Ambiguity"
    assert rows[2]["utterance"] == "Who is K. Lume?"


def test_parse_markdown_answer_key_reads_answer_section_only() -> None:
    text = """# Questions

1. Which items were recalled?
2. Who signed?

## Answers 1-2

1. Batch P-44 and the welcome loaf.
2. Unknown until K. Lume is resolved.
"""

    answers = parse_markdown_answer_key(text)

    assert answers == {
        "q001": "Batch P-44 and the welcome loaf.",
        "q002": "Unknown until K. Lume is resolved.",
    }


def test_reference_answers_are_not_structured_oracle_expectations() -> None:
    row = {"projected_decision": "answer", "queries": [], "query_results": []}

    assert score_oracle(row=row, oracle={"reference_answer": "Unknown."}) is None


def test_compiled_kb_inventory_uses_clause_surfaces_not_english() -> None:
    facts = [
        "affected_item(grievance_1, batch_p_44).",
        "claimed_label(grievance_1, plain_oat_ration).",
    ]
    rules = ["can_depart(Batch) :- affected_item(G, Batch), claimed_label(G, plain_oat_ration)."]

    inventory = compiled_kb_inventory(facts=facts, rules=rules)

    assert clause_signature(rules[0]) == "can_depart/1"
    assert inventory["signatures"] == ["affected_item/2", "can_depart/1", "claimed_label/2"]
    assert inventory["examples"]["affected_item/2"] == ["affected_item(grievance_1, batch_p_44)."]


def test_score_oracle_can_match_decision_predicate_and_answer_text() -> None:
    row = {
        "projected_decision": "answer",
        "queries": ["declares_recalled(flour_moon_seven, X)."],
        "query_results": [{"result": {"rows": [{"X": "batch_p_44"}]}}],
    }
    oracle = {
        "expected_decision": "answer",
        "expected_query_predicates": ["declares_recalled"],
        "expected_answer_contains": ["batch_p_44"],
    }

    assert score_oracle(row=row, oracle=oracle) is True


def test_score_oracle_returns_none_without_answer_key() -> None:
    assert score_oracle(row={"queries": []}, oracle={}) is None

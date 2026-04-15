from ingest_frontend import propose_frontend_parse


def test_propose_assert_fact_with_registry_parent():
    result = propose_frontend_parse(
        utterance="Ann is a parent of Scott.",
        allowed_signatures=["parent/2", "brother/2"],
        known_atoms=["ann", "scott"],
        max_candidates=4,
        min_score=0.2,
    )
    assert result["status"] in {"proposed", "no_candidate"}
    if result["status"] == "proposed":
        payload = result["parse_payload"]
        assert payload["intent"] == "assert_fact"
        assert "parent(" in payload["logic_string"]


def test_propose_query_with_variables():
    result = propose_frontend_parse(
        utterance="Who is a parent of Scott?",
        allowed_signatures=["parent/2"],
        known_atoms=["scott"],
        max_candidates=3,
        min_score=0.2,
    )
    assert result["intent"] == "query"
    if result["status"] == "proposed":
        query = result["parse_payload"]["queries"][0]
        assert query.endswith(".")


def test_no_candidate_when_registry_empty():
    result = propose_frontend_parse(
        utterance="Ann is a parent of Scott.",
        allowed_signatures=[],
        known_atoms=["ann", "scott"],
    )
    assert result["status"] == "no_candidate"

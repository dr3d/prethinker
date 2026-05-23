import io
import urllib.error
import urllib.request
from pathlib import Path

import scripts.run_domain_bootstrap_qa as qa_module
from scripts.run_domain_bootstrap_qa import (
    POST_INGESTION_QA_QUERY_STRATEGY,
    _assessment_revenue_companion,
    _assessment_transfer_policy_companion,
    _anchor_relation_hint_queries,
    _award_cap_quantity_hint_queries,
    _authority_instrument_metadata_hint_queries,
    _counsel_opinion_hint_queries,
    _classification_deferral_effect_companion,
    _complementary_relation_hint_queries,
    _conversion_assessment_delta_companion,
    _clinic_device_recall_companion,
    _dedupe_helper_query_results,
    _industrial_sensor_companion,
    _fallback_queries_from_semantic_ir,
    _limit_helper_query_results,
    _location_floor_hint_queries,
    _negative_join_with_previous,
    _negative_reference_supported_by_results,
    _source_record_citation_text_companion,
    _source_record_compile_surface_hint_queries,
    _source_record_numeric_count_supported_by_results,
    _source_record_reference_supported_by_results,
    _source_record_relative_next_day_companion,
    _source_record_section_list_count_companion,
    _default_openrouter_title,
    _chat_headers,
    _method_frame_purpose_companion,
    _method_actor_frame_source_companion,
    _placeholder_repaired_query,
    _relaxed_constant_query,
    _source_record_field_sibling_repaired_query,
    _source_coordinate_hint_queries,
    _source_column_text_hint_queries,
    _source_section_question_key_hint_queries,
    _source_record_table_count_hint_queries,
    _source_text_question_token_hint_queries,
    _temporal_join_with_previous,
    _urlopen_json_with_transient_retries,
    _vacancy_voting_eligibility_companion,
    _vote_record_hint_queries,
    cache_key_for_question,
    clause_signature,
    compact_relevant_clauses_for_evidence_plan,
    compiled_kb_contracts,
    compiled_kb_inventory,
    hash_text,
    is_cacheable_row,
    parse_markdown_answer_key,
    parse_numbered_markdown_questions,
    read_cached_row,
    run_evidence_bundle_plan_queries,
    run_query_plan as _run_query_plan,
    score_oracle,
    summarize,
    summarize_compatibility_rows,
    write_cached_row,
)
from kb_pipeline import CorePrologRuntime


def run_query_plan(
    runtime: CorePrologRuntime,
    queries: list[str],
    **kwargs,
) -> list[dict]:
    """Preserve legacy-adapter coverage tests while production defaults stay off."""
    kwargs.setdefault("include_legacy_native_helpers", True)
    return _run_query_plan(runtime, queries, **kwargs)


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


def test_openrouter_transient_http_errors_retry_before_row_failure(monkeypatch) -> None:
    calls = []

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self) -> bytes:
            return b'{"ok": true}'

    def fake_urlopen(_req, *, timeout):
        calls.append(timeout)
        if len(calls) == 1:
            raise urllib.error.HTTPError(
                url="https://openrouter.ai/api/v1/chat/completions",
                code=503,
                msg="Service Unavailable",
                hdrs=None,
                fp=io.BytesIO(b'{"error":{"message":"No healthy backends"}}'),
            )
        return FakeResponse()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr("scripts.run_domain_bootstrap_qa.time.sleep", lambda _seconds: None)

    result = _urlopen_json_with_transient_retries(
        urllib.request.Request("https://openrouter.ai/api/v1/chat/completions"),
        timeout=7,
        retry_transient=True,
    )

    assert result == {"ok": True}
    assert calls == [7, 7]


def test_qa_cache_key_changes_when_question_changes() -> None:
    context = {
        "schema_version": "domain_bootstrap_qa_cache_v1",
        "script_hash": hash_text("script"),
        "run_hash": hash_text("run"),
        "qa_hash": hash_text("qa"),
        "config": {"model": "model"},
    }
    oracle = {"reference_answer": "A"}
    first = cache_key_for_question(
        context=context,
        item={"id": "q001", "utterance": "Who signed?"},
        oracle=oracle,
    )
    second = cache_key_for_question(
        context=context,
        item={"id": "q001", "utterance": "Who signed it?"},
        oracle=oracle,
    )

    assert first != second


def test_qa_cache_row_round_trips(tmp_path) -> None:
    row = {"id": "q001", "ok": True, "queries": ["p(X)."], "reference_judge": {"verdict": "exact"}}

    assert is_cacheable_row(row) is True
    write_cached_row(cache_dir=tmp_path, cache_key="abc", row=row)

    assert read_cached_row(cache_dir=tmp_path, cache_key="abc") == row


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
    assert "affected_item(X, Y)." in inventory["query_templates"]
    assert "can_depart(X)." in inventory["query_templates"]


def test_compiled_kb_inventory_groups_present_surface_alias_families() -> None:
    facts = [
        "item_id(ex_001, painting).",
        "asset_id(ex_001).",
        "asset_description(ex_001, sealed_crate).",
        "external_reference(ex_001, catalog_44).",
        "access_authorized(ex_001, executor, standing, court_order).",
        "authorized_party(ex_001, executor, physical_access).",
        "order_id(order_1, p_26_347_d).",
        "order_effect(order_1, access_granted).",
        "chronological_event(event_1, inventory_opened, d_2026_01_01).",
        "event_occurred_before(event_1, event_2).",
        "source_claim(claim_1, subject_1, private_gift).",
        "assertion_recorded(assertion_1, private_gift, section_h_3).",
        "assigned_to_bus(person_1, vehicle_1, outbound).",
        "adult_in_version(v1, person_2, observer).",
        "distinct_student_count(v1, 38).",
        "required_chaperones(v1, 4).",
        "score_entry(app_1, reviewer_1, quality, 30, original).",
        "recorded_in(item_1, source_1, raw).",
        "docket_entry(entry_1, case_1, 2026_01_01, filed).",
        "state_changed(item_1, active, event_1).",
        "applicant_attribute(app_1, region, north).",
        "administrative_action(action_1, quarantine_hold, lot_1, inspector_1, 2026_01_01).",
        "owns(person_1, item_1, 2026).",
        "consistent_with(fragment_1, candidate_1, report_1).",
        "involved_actor(event_1, actor_1).",
        "rule_consequence(rule_1, threshold_applies, procedural).",
        "log_turn(turn_1, user_corrected_prior_claim).",
        "ambiguous_utterance(utt_1, she_approved_it).",
        "entity_type(entity_1, organization).",
        "document_type(doc_1, policy_memo).",
        "compiled_by(doc_1, analyst_1, 2026_01_01).",
        "correction_applied(record_1, correction_1, 2026_01_01).",
    ]

    inventory = compiled_kb_inventory(facts=facts, rules=[])
    families = {row["family"]: row for row in inventory["surface_alias_inventory"]}

    assert "item_identifier_surface" in families
    assert {"item_id/2", "asset_id/1", "asset_description/2"}.issubset(
        set(families["item_identifier_surface"]["signatures"])
    )
    assert "external_identifier_surface" in families
    assert "external_reference/2" in families["external_identifier_surface"]["signatures"]
    assert "access_authorization_surface" in families
    assert {"access_authorized/4", "authorized_party/3"}.issubset(
        set(families["access_authorization_surface"]["signatures"])
    )
    assert "order_effect_surface" in families
    assert {"order_id/2", "order_effect/2"}.issubset(set(families["order_effect_surface"]["signatures"]))
    assert "chronology_event_surface" in families
    assert {"chronological_event/3", "event_occurred_before/2"}.issubset(
        set(families["chronology_event_surface"]["signatures"])
    )
    assert "source_assertion_surface" in families
    assert {"source_claim/3", "assertion_recorded/3"}.issubset(
        set(families["source_assertion_surface"]["signatures"])
    )
    assert "assignment_allocation_surface" in families
    assert "assigned_to_bus/3" in families["assignment_allocation_surface"]["signatures"]
    assert "versioned_membership_surface" in families
    assert "adult_in_version/3" in families["versioned_membership_surface"]["signatures"]
    assert "count_requirement_surface" in families
    assert {"distinct_student_count/2", "required_chaperones/2"}.issubset(
        set(families["count_requirement_surface"]["signatures"])
    )
    assert "score_measurement_surface" in families
    assert "score_entry/5" in families["score_measurement_surface"]["signatures"]
    assert "record_provenance_surface" in families
    assert {"recorded_in/3", "docket_entry/4"}.issubset(
        set(families["record_provenance_surface"]["signatures"])
    )
    assert "state_transition_surface" in families
    assert "state_changed/3" in families["state_transition_surface"]["signatures"]
    assert "attribute_value_surface" in families
    assert "applicant_attribute/3" in families["attribute_value_surface"]["signatures"]
    assert "action_decision_surface" in families
    assert "administrative_action/5" in families["action_decision_surface"]["signatures"]
    assert "ownership_interest_surface" in families
    assert "owns/3" in families["ownership_interest_surface"]["signatures"]
    assert "evidence_consistency_surface" in families
    assert "consistent_with/3" in families["evidence_consistency_surface"]["signatures"]
    assert "actor_participation_surface" in families
    assert "involved_actor/2" in families["actor_participation_surface"]["signatures"]
    assert "rule_outcome_surface" in families
    assert "rule_consequence/3" in families["rule_outcome_surface"]["signatures"]
    assert "conversation_utterance_surface" in families
    assert {"log_turn/2", "ambiguous_utterance/2"}.issubset(
        set(families["conversation_utterance_surface"]["signatures"])
    )
    assert "entity_catalog_surface" in families
    assert {"entity_type/2", "document_type/2", "compiled_by/3"}.issubset(
        set(families["entity_catalog_surface"]["signatures"])
    )
    assert "correction_revision_surface" in families
    assert "correction_applied/3" in families["correction_revision_surface"]["signatures"]
    assert all("compiled_predicate_inventory" in row["query_policy"] for row in families.values())


def test_compiled_kb_contracts_name_role_and_generic_replacement_slots() -> None:
    contracts = {
        row["signature"]: row["args"]
        for row in compiled_kb_contracts(
            [
                "person_role/2",
                "person_role/3",
                "group_assignment/3",
                "recorded_statement/3",
                "custom_fact/2",
            ]
        )
    }

    assert contracts["person_role/2"] == ["person", "role"]
    assert contracts["person_role/3"] == ["person", "role", "scope_or_context"]
    assert contracts["group_assignment/3"] == ["person", "version_or_context", "group"]
    assert contracts["recorded_statement/3"] == ["statement_id", "speaker", "content"]
    assert contracts["custom_fact/2"] == ["arg1", "arg2"]


def test_query_strategy_keeps_source_coordinate_queries_variable_first() -> None:
    strategy_text = "\n".join(POST_INGESTION_QA_QUERY_STRATEGY["epistemic_policy"])

    assert "source-coordinate questions" in strategy_text
    assert "discover the source row with variables before binding a section or label" in strategy_text
    assert "Do not hardcode a guessed section/label atom" in strategy_text
    assert "Source-stated role lines are evidence" in strategy_text


def test_query_strategy_treats_title_as_slot_label_not_constant() -> None:
    strategy_text = "\n".join(POST_INGESTION_QA_QUERY_STRATEGY["arity_and_variable_policy"])

    assert "label, title, description, content" in strategy_text
    assert "Label, Title, Description, Content" in strategy_text


def test_source_coordinate_hint_queries_expose_addressability_surfaces() -> None:
    hints = _source_coordinate_hint_queries(
        utterance="Which section contains the chronology of custody events?",
        kb_inventory={
            "signatures": [
                "source_record_section/2",
                "source_record_label/2",
                "source_record_line/2",
                "source_record_field/3",
                "source_record_text_atom/2",
            ]
        },
    )

    assert hints == [
        "source_record_section(SourceRow, Section).",
        "source_record_label(SourceRow, Label).",
        "source_record_line(SourceRow, Line).",
        "source_record_field(SourceRow, Field, Value).",
        "source_record_text_atom(SourceRow, TextAtom).",
    ]


def test_source_coordinate_hint_queries_cover_source_stated_capacity_without_role_nouns() -> None:
    hints = _source_coordinate_hint_queries(
        utterance="Who is identified as the record contact?",
        kb_inventory={"signatures": ["source_record_text_atom/2"]},
    )

    assert hints == ["source_record_text_atom(SourceRow, TextAtom)."]


def test_post_ingestion_qa_strategy_prefers_compiled_kb_surface() -> None:
    strategy = POST_INGESTION_QA_QUERY_STRATEGY

    assert strategy["name"] == "post_ingestion_qa_query_strategy_v1"
    assert "compiled_predicate_inventory.signatures" in " ".join(strategy["predicate_surface_policy"])
    assert "compiled_surface_alias_inventory" in " ".join(strategy["predicate_surface_policy"])
    assert "relevant_clauses" in " ".join(strategy["predicate_surface_policy"])
    assert "complementary phrasing" in " ".join(strategy["predicate_surface_policy"])
    assert "sibling predicates over the same subject" in " ".join(strategy["predicate_surface_policy"])
    assert any("full compiled predicate arity" in item for item in strategy["arity_and_variable_policy"])
    assert any("Do not pre-fill an answer slot" in item for item in strategy["arity_and_variable_policy"])
    assert any("Do not over-constrain descriptive label slots" in item for item in strategy["arity_and_variable_policy"])
    assert any("record id too early" in item for item in strategy["arity_and_variable_policy"])
    assert any("source-owned record predicates" in item for item in strategy["arity_and_variable_policy"])
    assert any("institution, ledger, record, or source questions" in item for item in strategy["arity_and_variable_policy"])
    assert any("source-of-access questions" in item for item in strategy["arity_and_variable_policy"])
    assert any("access_source" in item and "authorized_party" in item for item in strategy["arity_and_variable_policy"])
    assert any("who-reported or reporter questions" in item for item in strategy["arity_and_variable_policy"])
    assert any("longer normalized atom" in item for item in strategy["arity_and_variable_policy"])
    assert any("grievance(Grievance, Label)" in item for item in strategy["arity_and_variable_policy"])
    assert any("source-attributed claims" in item for item in strategy["epistemic_policy"])
    assert any("policy_requirement/3" in item for item in strategy["epistemic_policy"])
    assert "elapsed_days" in " ".join(strategy["epistemic_policy"])
    assert any("alternate atom order" in item for item in strategy["arity_and_variable_policy"])
    assert any("product, retailer, store, state" in item for item in strategy["arity_and_variable_policy"])
    assert any("sold_at_retailer(Item, Retailer) plus sold_in_state(Item, State)" in item for item in strategy["arity_and_variable_policy"])
    assert any("bulk item, retail packaged item" in item for item in strategy["arity_and_variable_policy"])
    assert any("restriction and constraint predicates as answer-bearing rows" in item for item in strategy["arity_and_variable_policy"])
    assert any("source_record_cell_item_pair(Row" in item for item in strategy["arity_and_variable_policy"])
    assert any("source_record_cell_item_pair_qualifier(Row" in item for item in strategy["arity_and_variable_policy"])
    assert any("federal_agency_authority" in item for item in strategy["epistemic_policy"])
    assert any("conflict_policy" in item for item in strategy["epistemic_policy"])
    assert any("witness_statement(Speaker, Language" in item for item in strategy["epistemic_policy"])
    assert any("extension_reason" in item for item in strategy["epistemic_policy"])
    assert any("subgrant_amount" in item for item in strategy["epistemic_policy"])
    assert any("prior_complaint/4" in item for item in strategy["epistemic_policy"])


def test_complementary_relation_hints_query_sibling_subject_surfaces() -> None:
    kb_inventory = {
        "examples": {
            "carries/2": ["carries(field_team, access_badges)."],
            "has_experience_with/2": ["has_experience_with(field_team, failed_sequence)."],
            "source_record_row/5": [
                "source_record_row(src_line_0001, body, 1, packet, line_label)."
            ],
        }
    }

    hints = _complementary_relation_hint_queries(
        utterance="What did the field team have besides the badges?",
        kb_inventory=kb_inventory,
        queries=["carries(field_team, Item)."],
    )

    assert hints == ["has_experience_with(field_team, Complement)."]


def test_anchor_relation_hints_query_direct_trigger_surfaces() -> None:
    kb_inventory = {
        "examples": {
            "occurred_before/2": ["occurred_before(archive_migration, fee_reconciliation)."],
            "triggered_by/2": ["triggered_by(moved_to_permit_queue, archive_migration)."],
        }
    }

    hints = _anchor_relation_hint_queries(
        utterance="What event came before the reviewers moved to the queue?",
        kb_inventory=kb_inventory,
        queries=["occurred_before(X, moved_to_permit_queue)."],
    )

    assert hints == ["triggered_by(moved_to_permit_queue, Anchor)."]


def test_run_query_plan_exposes_bound_query_constants_as_evidence() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    assert runtime.assert_fact("source_record_text_atom(src_line_001, court_alpha_probate_court).").get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_text_atom(Row, court_alpha_probate_court)."])

    result = rows[0]["result"]
    assert result["status"] == "success"
    assert result["bound_query_constants"] == [
        {"arg_index": 2, "value": "court_alpha_probate_court", "display": "court alpha probate court"}
    ]
    assert result["rows"] == [
        {
            "Row": "src_line_001",
            "BoundArg2": "court_alpha_probate_court",
            "BoundArg2Display": "court alpha probate court",
        }
    ]


def test_reference_judge_policy_treats_normalized_purpose_atoms_as_answer_bearing() -> None:
    source = Path("scripts/run_domain_bootstrap_qa.py").read_text(encoding="utf-8")

    assert "Purpose/action atom policy" in source
    assert "fetching_fog_leaves" in source
    assert "Predicate-relation policy" in source
    assert "has_knowledge_of(Entity, mislabeled_folders)" in source
    assert "Complementary-relation policy" in source
    assert "Anchor-answer policy" in source
    assert "Causal-chain policy" in source
    assert "Causal support policy" in source
    assert "Identifier-display policy" in source
    assert "cn_2026_04_15" in source
    assert "Identifier-metadata policy" in source
    assert "driver_license/2" in source


def test_negative_reference_supported_by_negative_query_results() -> None:
    row = {
        "query_results": [
            {
                "query": "exercises_quality_control(operator, X).",
                "result": {
                    "status": "success",
                    "rows": [{"X": "no_control"}],
                },
            },
            {
                "query": "source_record_text_atom(src_line_0011, TextAtom).",
                "result": {
                    "status": "success",
                    "rows": [{"TextAtom": "operator_does_not_carry_any_control_over_output_quality"}],
                },
            },
        ]
    }

    assert _negative_reference_supported_by_results(row=row, reference="not") is True
    assert _negative_reference_supported_by_results(row=row, reference="picture quality") is False


def test_openrouter_title_header_uses_experiment_label(monkeypatch) -> None:
    monkeypatch.delenv("PRETHINKER_OPENROUTER_TITLE", raising=False)
    monkeypatch.delenv("OPENROUTER_APP_TITLE", raising=False)
    monkeypatch.delenv("OPENROUTER_X_TITLE", raising=False)

    title = _default_openrouter_title(Path("tmp") / "squad_probe_20260513" / "fixture_a")

    assert title == "qa:fixture_a"


def test_chat_headers_add_openrouter_title(monkeypatch) -> None:
    monkeypatch.setenv("PRETHINKER_OPENROUTER_TITLE", "Prethinker SQuAD Probe")
    monkeypatch.setenv("PRETHINKER_OPENROUTER_REFERER", "https://example.test/prethinker/squad")
    monkeypatch.delenv("PRETHINKER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    headers = _chat_headers()

    assert headers["X-Title"] == "Prethinker SQuAD Probe"
    assert headers["X-OpenRouter-Title"] == "Prethinker SQuAD Probe"
    assert headers["HTTP-Referer"] == "https://example.test/prethinker/squad"


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


def test_evidence_bundle_plan_accepts_conjunctive_source_record_queries() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_record_row(src_1, list_row, 12, access_log, entry_1405).",
        "source_record_text_atom(src_1, tilling_entered_room_504_at_14_05_11).",
        "source_record_numeric_token(src_1, v_14_05_11).",
        "source_record_numeric_token(src_1, v_504).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={
            "signatures": [
                "source_record_row/5",
                "source_record_text_atom/2",
                "source_record_numeric_token/2",
            ]
        },
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "source_join",
                    "purpose": "Join source row addressability with text and numeric tokens.",
                    "query_templates": [
                        "source_record_row(Line, list_row, LineNum, Section, TextAtom), "
                        "source_record_text_atom(Line, SourceText), "
                        "source_record_numeric_token(Line, v_14_05_11), "
                        "source_record_numeric_token(Line, v_504)."
                    ],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "success"
    assert results[0]["result"]["reasoning_basis"]["validation"] == "predicate_and_arity_checked"
    assert results[0]["result"]["rows"][0]["Line"] == "src_1"


def test_evidence_bundle_plan_normalizes_simple_equality_constraints() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_record_label(src_1, correction_notice_a).",
        "source_record_label(src_2, unrelated_notice).",
        "source_record_text_atom(src_1, correction_notice_a_reason_adjacent_tenant_complaints).",
        "source_record_text_atom(src_2, unrelated_notice_reason_staffing).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["source_record_label/2", "source_record_text_atom/2"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "source_row_reason",
                    "purpose": "Retrieve source text for a labeled source row.",
                    "query_templates": [
                        "source_record_text_atom(SourceLine, TextAtom), "
                        "source_record_label(SourceLine, Label), "
                        "Label = correction_notice_a, TextAtom = ReasonText."
                    ],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "success"
    assert results[0]["result"]["reasoning_basis"]["validation"] == "predicate_and_arity_checked"
    assert results[0]["result"]["reasoning_basis"]["original_query"].endswith("TextAtom = ReasonText.")
    assert results[0]["derived_from_queries"] == [
        "source_record_text_atom(SourceLine, TextAtom), source_record_label(SourceLine, correction_notice_a)."
    ]
    assert results[0]["result"]["rows"] == [
        {"SourceLine": "src_1", "TextAtom": "correction_notice_a_reason_adjacent_tenant_complaints"}
    ]


def test_evidence_bundle_plan_does_not_turn_alias_only_equality_into_broad_scan() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    assert runtime.assert_fact("source_record_text_atom(src_1, unrestricted_source_text).").get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["source_record_text_atom/2"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "broad_alias",
                    "purpose": "This should not become a broad source scan.",
                    "query_templates": ["source_record_text_atom(Line, Text), Text = OtherText."],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "error"
    assert results[0]["result"]["reasoning_basis"]["validation"] == "rejected"


def test_evidence_bundle_plan_repairs_source_text_memberchk_filter() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_record_text_atom(src_1, records_are_verified_in_the_field).",
        "source_record_text_atom(src_2, records_are_verified_in_the_laboratory).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["source_record_text_atom/2"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "source_text_contains",
                    "purpose": "Find source text containing the requested normalized phrase.",
                    "query_templates": [
                        "source_record_text_atom(Line, Text), memberchk('in_the_laboratory', Text)."
                    ],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "success"
    assert results[0]["result"]["reasoning_basis"]["validation"] == "source_text_contains_filter_repaired"
    assert results[0]["result"]["rows"] == [
        {"Line": "src_2", "Text": "records_are_verified_in_the_laboratory"}
    ]


def test_evidence_bundle_plan_repairs_multiple_source_text_memberchk_filters() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_record_text_atom(src_1, correction_notice_mentions_threshold_only).",
        "source_record_text_atom(src_2, correction_notice_mentions_threshold_and_appeal_window).",
        "source_record_text_atom(src_3, appeal_window_reference_without_required_floor).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["source_record_text_atom/2"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "source_text_multi_contains",
                    "purpose": "Find source text containing both normalized phrases.",
                    "query_templates": [
                        "source_record_text_atom(Line, Text), "
                        "memberchk('threshold', Text), "
                        "memberchk('appeal_window', Text)."
                    ],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "success"
    assert results[0]["result"]["reasoning_basis"]["contains_needles"] == ["threshold", "appeal_window"]
    assert results[0]["result"]["rows"] == [
        {"Line": "src_2", "Text": "correction_notice_mentions_threshold_and_appeal_window"}
    ]


def test_evidence_bundle_plan_repairs_source_row_context_token_filter() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        (
            "source_record_row_context(src_1, applicant_narrative, "
            "we_believe_project_is_consistent_with_housing_element, section_a)."
        ),
        (
            "source_record_row_context(src_2, opposition_letter, "
            "neighbor_disputes_general_plan_consistency, section_b)."
        ),
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["source_record_row_context/4"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "row_context_text_filter",
                    "purpose": "Find row-context text containing the requested source phrase.",
                    "query_templates": [
                        "source_record_row_context(Line, Label, Text, Section), "
                        "memberchk(consistent_with_housing_element, Text_tokens)."
                    ],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "success"
    assert results[0]["result"]["reasoning_basis"]["validation"] == "single_goal_post_filter_repaired"
    assert results[0]["result"]["rows"] == [
        {
            "Label": "applicant_narrative",
            "Line": "src_1",
            "Section": "section_a",
            "Text": "we_believe_project_is_consistent_with_housing_element",
        }
    ]


def test_evidence_bundle_plan_repairs_conjunctive_source_text_filter() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_attributed_claim(claim_a, src_1, fdr_hold, context_a).",
        "source_attributed_claim(claim_b, src_2, receipt_notice, context_b).",
        "source_record_text_atom(src_1, fdr_hold_was_released_after_review).",
        "source_record_text_atom(src_2, biogenix_received_the_order_on_october_23).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["source_attributed_claim/4", "source_record_text_atom/2"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "claim_source_text_filter",
                    "purpose": "Find source-attributed claims whose source text contains a requested token.",
                    "query_templates": [
                        "source_attributed_claim(Claim, Source, Detail, Context), "
                        "source_record_text_atom(Source, Text), "
                        "memberchk('biogenix', Text)."
                    ],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "success"
    assert results[0]["result"]["reasoning_basis"]["validation"] == "single_goal_post_filter_repaired"
    assert results[0]["result"]["rows"] == [
        {
            "Claim": "claim_b",
            "Context": "context_b",
            "Detail": "receipt_notice",
            "Source": "src_2",
            "Text": "biogenix_received_the_order_on_october_23",
        }
    ]


def test_evidence_bundle_plan_repairs_atom_chars_member_filter() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_record_text_atom(src_1, project_consistent_with_housing_element).",
        "source_record_text_atom(src_2, project_consistent_with_general_plan_only).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["source_record_text_atom/2"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "atom_chars_text_filter",
                    "purpose": "Find source text containing both requested tokens.",
                    "query_templates": [
                        "source_record_text_atom(Line, Text), "
                        "memberchk(consistent, atom_chars(Text, Chars)), "
                        "memberchk(housing_element, atom_chars(Text, Chars))."
                    ],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "success"
    assert results[0]["result"]["reasoning_basis"]["validation"] == "source_text_contains_filter_repaired"
    assert results[0]["result"]["reasoning_basis"]["contains_needles"] == ["consistent", "housing_element"]
    assert results[0]["result"]["rows"] == [
        {"Line": "src_1", "Text": "project_consistent_with_housing_element"}
    ]


def test_evidence_context_filter_carries_source_record_pair_rows_for_source_text_plans() -> None:
    facts = [
        "retailer_sold_in(foodland, pennsylvania, cucumber_only).",
        "source_record_text_atom(src_line_0096, west_virginia_foodland_cucumber_green_bell_pepper).",
        "source_record_cell_item_pair(src_line_0096, 1, west_virginia, 2, foodland).",
        (
            "source_record_cell_item_pair_qualifier(src_line_0096, 1, west_virginia, 2, "
            "foodland, cucumber_green_bell_pepper_and_pickling_cucumber_only)."
        ),
    ]

    clauses = compact_relevant_clauses_for_evidence_plan(
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "source_text",
                    "purpose": "Find source table support.",
                    "query_templates": ["source_record_text_atom(Row, TextAtom)."],
                }
            ]
        },
        facts=facts,
        rules=[],
        max_clauses=4,
        broad_floor=0,
    )

    assert "source_record_cell_item_pair(src_line_0096, 1, west_virginia, 2, foodland)." in clauses
    assert (
        "source_record_cell_item_pair_qualifier(src_line_0096, 1, west_virginia, 2, "
        "foodland, cucumber_green_bell_pepper_and_pickling_cucumber_only)."
    ) in clauses


def test_distribution_pair_companion_exposes_source_record_pair_qualifier_after_miss() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    facts = [
        (
            "source_record_cell_item_pair_qualifier(src_line_0096, 1, west_virginia, 2, "
            "foodland, cucumber_green_bell_pepper_and_pickling_cucumber_only)."
        ),
        "source_record_cell_item_pair(src_line_0096, 1, west_virginia, 2, foodland).",
    ]
    for fact in facts:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        ["retailer_sold_in(foodland, west_virginia, scope)."],
        helper_companions_enabled=True,
    )

    companion = next(
        item
        for item in results
        if item.get("result", {}).get("predicate") == "source_record_cell_item_pair"
    )
    rows = companion["result"]["rows"]
    assert rows
    assert companion["result"]["reasoning_basis"]["kind"] == "core-local"
    assert rows[0]["Row"] == "src_line_0096"
    assert rows[0]["Qualifier"] == "cucumber_green_bell_pepper_and_pickling_cucumber_only"


def test_distribution_pair_companion_uses_single_retailer_constant() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    facts = [
        (
            "source_record_cell_item_pair_qualifier(src_line_0096, 1, west_virginia, 2, "
            "foodland, cucumber_green_bell_pepper_and_pickling_cucumber_only)."
        ),
        "source_record_cell_item_pair(src_line_0096, 1, west_virginia, 2, foodland).",
    ]
    for fact in facts:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        ["product_sold_at(ProductID, retailer_foodland)."],
        helper_companions_enabled=True,
    )

    companion = next(
        item
        for item in results
        if item.get("result", {}).get("predicate") == "source_record_cell_item_pair"
    )
    rows = companion["result"]["rows"]
    assert rows
    assert companion["result"]["reasoning_basis"]["kind"] == "core-local"
    assert rows[0]["LeftItem"] == "west_virginia"
    assert rows[0]["Qualifier"] == "cucumber_green_bell_pepper_and_pickling_cucumber_only"


def test_evidence_bundle_plan_repairs_source_text_string_contains_filter() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_record_text_atom(src_1, license_notes_contain_expiration_only).",
        "source_record_text_atom(src_2, permit_condition_requires_supervisor_signature).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["source_record_text_atom/2"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "source_text_string_contains",
                    "purpose": "Find source text containing a requested normalized phrase.",
                    "query_templates": [
                        "source_record_text_atom(Line, Text), "
                        "string_contains(Text, 'supervisor_signature')."
                    ],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "success"
    assert results[0]["result"]["reasoning_basis"]["validation"] == "source_text_contains_filter_repaired"
    assert results[0]["result"]["rows"] == [
        {"Line": "src_2", "Text": "permit_condition_requires_supervisor_signature"}
    ]


def test_evidence_bundle_plan_repairs_source_record_field_contains_filter() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_record_field(src_1, disposition, salt_debt_pending).",
        "source_record_field(src_2, disposition, salt_debt_repaid_by_receipt).",
        "source_record_field(src_3, disposition, tool_debt_repaid_by_receipt).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["source_record_field/3"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "source_field_contains",
                    "purpose": "Find source-record field values containing both requested normalized phrases.",
                    "query_templates": [
                        "source_record_field(Line, Field, Value), "
                        "string_contains(Value, 'salt'), "
                        "string_contains(Value, 'repaid')."
                    ],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "success"
    assert results[0]["result"]["reasoning_basis"]["validation"] == "source_record_contains_filter_repaired"
    assert results[0]["result"]["rows"] == [
        {"Field": "disposition", "Line": "src_2", "Value": "salt_debt_repaid_by_receipt"}
    ]


def test_evidence_bundle_plan_falls_back_from_source_field_filter_to_labeled_source_text() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_record_field(src_line_0038, staff_note, dr_holm_density_calculation_is_correct).",
        (
            "source_record_text_atom(src_line_0040, "
            "dr_holm_s_traffic_estimate_has_not_been_verified_by_public_works)."
        ),
        "source_record_label(src_line_0040, staff_note).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["source_record_field/3", "source_record_text_atom/2"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "staff_note_source_text_fallback",
                    "purpose": "Find staff-note text containing the verification status.",
                    "query_templates": [
                        "source_record_field(Line, staff_note, Text), "
                        "memberchk(dr_holm, Text), memberchk(traffic, Text), memberchk(verified, Text)."
                    ],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "success"
    assert (
        results[0]["result"]["reasoning_basis"]["validation"]
        == "source_record_field_text_atom_contains_fallback"
    )
    assert results[0]["result"]["rows"] == [
        {
            "BoundArg2": "staff_note",
            "BoundArg2Display": "staff note",
            "Line": "src_line_0040",
            "SourcePredicate": "source_record_text_atom",
            "Text": "dr_holm_s_traffic_estimate_has_not_been_verified_by_public_works",
        }
    ]


def test_source_field_text_fallback_requires_matching_label_or_prefix() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_record_field(src_line_0038, staff_note, dr_holm_density_calculation_is_correct).",
        (
            "source_record_text_atom(src_line_0040, "
            "dr_holm_s_traffic_estimate_has_not_been_verified_by_public_works)."
        ),
        "source_record_label(src_line_0040, neighbor_letter).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["source_record_field/3", "source_record_text_atom/2"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "staff_note_source_text_fallback",
                    "purpose": "Do not broaden a field query to unrelated source text.",
                    "query_templates": [
                        "source_record_field(Line, staff_note, Text), "
                        "memberchk(dr_holm, Text), memberchk(traffic, Text), memberchk(verified, Text)."
                    ],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "success"
    assert results[0]["result"]["reasoning_basis"]["validation"] == "source_record_contains_filter_repaired"
    assert results[0]["result"]["rows"] == []


def test_evidence_bundle_plan_repairs_source_record_label_memberchk_filter() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_record_label(src_1, ordinary_notice).",
        "source_record_label(src_2, formal_compliance_determination).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["source_record_label/2"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "source_label_contains",
                    "purpose": "Find source-record labels containing a requested normalized phrase.",
                    "query_templates": [
                        "source_record_label(Line, Label), memberchk(formal_compliance, split_atom(Label))."
                    ],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "success"
    assert results[0]["result"]["reasoning_basis"]["validation"] == "source_record_contains_filter_repaired"
    assert results[0]["result"]["rows"] == [
        {"Label": "formal_compliance_determination", "Line": "src_2"}
    ]


def test_evidence_bundle_plan_repairs_single_goal_list_membership_filter() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "holds_role(ana, acting_watch_captain, may_1_to_may_10).",
        "holds_role(bo, acting_watch_captain, may_11_to_may_20).",
        "holds_role(cy, acting_watch_captain, june_1_to_june_10).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["holds_role/3"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "role_window_filter",
                    "purpose": "Filter admitted role rows by a proposed interval list.",
                    "query_templates": [
                        "holds_role(Person, acting_watch_captain, TimePeriod), "
                        "member(TimePeriod, [may_1_to_may_10, may_11_to_may_20])."
                    ],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "success"
    assert results[0]["result"]["reasoning_basis"]["validation"] == "single_goal_post_filter_repaired"
    assert results[0]["result"]["rows"] == [
        {
            "BoundArg2": "acting_watch_captain",
            "BoundArg2Display": "acting watch captain",
            "Person": "ana",
            "TimePeriod": "may_1_to_may_10",
        },
        {
            "BoundArg2": "acting_watch_captain",
            "BoundArg2Display": "acting watch captain",
            "Person": "bo",
            "TimePeriod": "may_11_to_may_20",
        },
    ]


def test_evidence_bundle_plan_repairs_single_goal_concat_contains_filter() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "claim_made_by(claim_1, witness_a, blue_crate_not_abandoned).",
        "claim_made_by(claim_2, witness_b, red_crate_abandoned).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["claim_made_by/3"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "claim_text_filter",
                    "purpose": "Filter admitted claim rows by a contains-like concat expression.",
                    "query_templates": [
                        "claim_made_by(ClaimId, Person, ClaimText), "
                        "string_concat(_, 'not_abandoned', ClaimText)."
                    ],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "success"
    assert results[0]["result"]["reasoning_basis"]["validation"] == "single_goal_post_filter_repaired"
    assert results[0]["result"]["rows"] == [
        {"ClaimId": "claim_1", "ClaimText": "blue_crate_not_abandoned", "Person": "witness_a"}
    ]


def test_evidence_bundle_plan_does_not_repair_unbound_source_text_filter() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    assert runtime.assert_fact("source_record_text_atom(src_1, threshold_and_appeal_window).").get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={"signatures": ["source_record_text_atom/2"]},
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "source_text_unbound_filter",
                    "purpose": "This should not become a broad scan without a source text surface.",
                    "query_templates": ["string_contains(Text, 'appeal_window')."],
                }
            ]
        },
    )

    assert results[0]["result"]["status"] == "error"
    assert results[0]["result"]["reasoning_basis"]["validation"] == "rejected"


def test_method_frame_purpose_companion_links_method_to_agent_frame() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "agent_uses_method(operator, laser_scan).",
        "agent_operates_in(operator, surface_defect_detection).",
        "method_action(laser_scan, measures_reflection_variance).",
        "source_record_label(src_1, operators_detect_surface_defects_with_laser_scan_and_visual_review).",
        "source_record_text_atom(src_1, operators_detect_surface_defects_with_laser_scan_and_visual_review).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _method_frame_purpose_companion(
        runtime,
        predicate="method_action",
        args=("laser_scan", "Action"),
        query="method_action(laser_scan, Action).",
    )

    assert companion is not None
    result = companion["result"]
    assert result["predicate"] == "method_frame_purpose_support"
    assert result["rows"][0]["SupportKind"] == "method_frame_purpose_support"
    assert result["rows"][0]["Method"] == "laser_scan"
    assert result["rows"][0]["Agent"] == "operator"
    assert result["rows"][0]["FramePurpose"] == "surface_defect_detection"
    assert "surface defects" in result["rows"][0]["FrameTextDisplay"]


def test_method_actor_frame_source_companion_links_actor_method_to_source_frame() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "method_actor(impact_logging, planner).",
        "method_primary_location(impact_logging, north_alcove).",
        "method_measures(impact_logging, peak_force).",
        "source_record_text_atom(src_1, planners_compare_dock_vibration_in_the_north_alcove_using_impact_logging).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _method_actor_frame_source_companion(
        runtime,
        predicate="method_actor",
        args=("Method", "planner"),
        query="method_actor(Method, planner).",
    )

    assert companion is not None
    result = companion["result"]
    assert result["predicate"] == "method_actor_frame_source_support"
    assert result["rows"][0]["SupportKind"] == "method_actor_frame_source_support"
    assert result["rows"][0]["Actor"] == "planner"
    assert result["rows"][0]["Method"] == "impact_logging"
    assert "dock vibration" in result["rows"][0]["FrameTextDisplay"]


def test_method_actor_frame_source_companion_prefers_bound_method_source_text() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "method_actor(residue_spectroscopy, calibration_analyst).",
        "method_primary_location(residue_spectroscopy, intake_bay).",
        "source_record_label(src_1, calibration_analysts_document_package_defects_inside_the_intake_bay).",
        "source_record_label(src_2, calibration_analysts_document_package_defects_inside_the_intake_bay).",
        "source_record_text_atom(src_2, residue_spectroscopy_runs_under_a_blue_filter).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _method_actor_frame_source_companion(
        runtime,
        predicate="method_primary_location",
        args=("residue_spectroscopy", "Location"),
        query="method_primary_location(residue_spectroscopy, Location).",
    )

    assert companion is not None
    frame_texts = [row["FrameTextDisplay"] for row in companion["result"]["rows"]]
    assert "residue spectroscopy runs under a blue filter" in frame_texts


def test_source_record_reference_supports_embedded_reference_answer() -> None:
    row = {
        "query_results": [
            {
                "result": {
                    "predicate": "source_record_text_atom",
                    "rows": [
                        {
                            "Line": "src_1",
                            "Text": "planners_compare_dock_vibration_in_the_north_alcove",
                        }
                    ],
                }
            }
        ]
    }

    assert _source_record_reference_supported_by_results(row=row, reference="dock vibration") is True
    assert _source_record_reference_supported_by_results(row=row, reference="generator readiness") is False


def test_source_record_reference_support_tokenizes_natural_phrases() -> None:
    row = {
        "query_results": [
            {
                "result": {
                    "predicate": "source_record_text_atom",
                    "rows": [
                        {
                            "SourceRow": "src_line_0058",
                            "TextAtom": "polaris_industries_inc_of_medina_minnesota",
                        },
                        {
                            "SourceRow": "src_line_0030",
                            "TextAtom": "polaris_at_800_765_2747_from_7_a_m_to_7_p_m_ct_monday_through_friday",
                        },
                    ],
                }
            }
        ]
    }

    assert _source_record_reference_supported_by_results(row=row, reference="Medina, Minnesota") is True
    assert _source_record_reference_supported_by_results(row=row, reference="Central Time (CT)") is True
    assert _source_record_reference_supported_by_results(row=row, reference="Boston, Massachusetts") is False


def test_source_record_reference_support_handles_dates_and_connector_words() -> None:
    row = {
        "query_results": [
            {
                "result": {
                    "predicate": "source_record_text_atom",
                    "rows": [
                        {
                            "SourceRow": "src_line_0159",
                            "TextAtom": "fr_doc_2024_06370_filed_3_25_24_8_45_am",
                        },
                        {
                            "SourceRow": "src_line_0056",
                            "TextAtom": "at_0713_the_device_was_about_7_5_miles_northwest_of_where_it_had_originally_started",
                        },
                    ],
                }
            }
        ]
    }

    assert _source_record_reference_supported_by_results(
        row=row,
        reference="3-25-24 (March 25, 2024); the FR Doc was filed at 8:45 am",
    )
    assert _source_record_reference_supported_by_results(
        row=row,
        reference="Northwest - by 0713 the device was about 7.5 miles northwest of where it had originally started",
    )


def test_source_record_numeric_count_supports_source_text_count_scope() -> None:
    row = {
        "utterance": "How many deficiencies did the inspection team issue for the device at that examination?",
        "query_results": [
            {
                "result": {
                    "predicate": "source_record_text_atom",
                    "rows": [
                        {
                            "SourceRow": "src_line_0080",
                            "TextAtom": "the_inspection_team_issued_ten_deficiencies_for_the_device",
                        }
                    ],
                }
            }
        ],
    }

    assert _source_record_numeric_count_supported_by_results(row=row, reference="Ten") is True

    row["query_results"][0]["result"]["rows"][0]["TextAtom"] = "the_hearing_lasted_ten_days"
    assert _source_record_numeric_count_supported_by_results(row=row, reference="Ten") is False


def test_source_record_row_context_companion_follows_source_row_ids() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_record_text_atom(src_line_0157, solicitor_federal_register_liaison).",
        "source_record_label(src_line_0157, thomas_tso).",
        "source_record_section(src_line_0157, signature_block).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = _run_query_plan(
        runtime,
        ["source_record_text_atom(X, solicitor_federal_register_liaison)."],
        helper_companions_enabled=False,
    )

    companion = next(
        item
        for item in results
        if item.get("result", {}).get("predicate") == "source_record_label"
        and item.get("result", {}).get("reasoning_basis", {}).get("kind") == "core-local"
    )
    rows = companion["result"]["rows"]
    assert any(row.get("SourceRecordLabel") == "thomas_tso" for row in rows)


def test_source_record_citation_companion_scans_federal_register_citations() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_record_text_atom(src_line_0011, document_citation_89_fr_20843).",
        (
            "source_record_text_atom(src_line_0046, "
            "on_february_16_2024_in_89_fr_12287_the_agency_noted_the_proposed_change)."
        ),
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _source_record_citation_text_companion(
        runtime,
        utterance="At what Federal Register citation was the proposed rule originally published?",
    )

    assert companion is not None
    rows = companion["result"]["rows"]
    assert rows[0]["SourceRow"] == "src_line_0046"
    assert any(row.get("TextAtom", "").startswith("on_february_16_2024_in_89_fr_12287") for row in rows)


def test_source_record_section_list_count_companion_counts_scoped_list_block() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    facts = [
        "source_record_row(src_line_0039, paragraph_line, 39, company_announcement, retail_packaged_items).",
        "source_record_text_atom(src_line_0039, retail_packaged_items).",
        "source_record_row(src_line_0041, paragraph_line, 41, company_announcement, sold_at_select_walmart_stores).",
        "source_record_text_atom(src_line_0041, sold_at_select_walmart_stores_in_ct_de_and_wv).",
        "source_record_row(src_line_0043, list_row, 43, company_announcement, item_a).",
        "source_record_text_atom(src_line_0043, wiers_farm_item_a).",
        "source_record_row(src_line_0044, list_row, 44, company_announcement, item_b).",
        "source_record_text_atom(src_line_0044, wiers_farm_item_b).",
        "source_record_row(src_line_0045, list_row, 45, company_announcement, item_c).",
        "source_record_text_atom(src_line_0045, wiers_farm_item_c).",
        "source_record_row(src_line_0053, paragraph_line, 53, company_announcement, sold_at_aldi_stores).",
        "source_record_text_atom(src_line_0053, sold_at_aldi_stores_in_ky).",
    ]
    for fact in facts:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _source_record_section_list_count_companion(
        runtime,
        utterance="How many distinct retail-packaged items sold at Walmart are listed in the announcement?",
    )

    assert companion is not None
    row = companion["result"]["rows"][0]
    assert row["Count"] == "3"
    assert row["DisplayCount"] == "three"
    assert row["MemberRows"] == ["src_line_0043", "src_line_0044", "src_line_0045"]
    assert _source_record_numeric_count_supported_by_results(
        row={
            "utterance": "How many distinct retail-packaged items sold at Walmart are listed in the announcement?",
            "query_results": [companion],
        },
        reference="Three",
    )


def test_evidence_bundle_plan_preserves_source_record_repairs_for_temporal_joins() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "asset_event(asset_1, ev_start).",
        "asset_event(asset_1, ev_end).",
        "corrected_timestamp(ev_start, 2026_01_01_10_00_00).",
        "corrected_timestamp(ev_end, 2026_01_01_10_02_30).",
        "source_record_field(src_start, event, ev_start).",
        "source_record_field(src_start, description, hold_start).",
        "source_record_field(src_end, event, ev_end).",
        "source_record_field(src_end, description, hold_end).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        kb_inventory={
            "signatures": [
                "asset_event/2",
                "corrected_timestamp/2",
                "source_record_field/3",
            ]
        },
        evidence_plan={
            "support_bundles": [
                {
                    "bundle_id": "timed_interval",
                    "purpose": "Bind interval endpoint events through source rows before computing elapsed time.",
                    "query_templates": [
                        "asset_event(asset_1, StartEvent), "
                        "source_record_field(StartEvent, description, hold_start), "
                        "corrected_timestamp(StartEvent, StartTime).",
                        "asset_event(asset_1, EndEvent), "
                        "source_record_field(EndEvent, description, hold_end), "
                        "corrected_timestamp(EndEvent, EndTime).",
                        "elapsed_minutes(StartTime, EndTime, DurationMinutes).",
                    ],
                }
            ]
        },
    )

    temporal = [
        item
        for item in results
        if "elapsed_minutes" in item.get("query", "")
        and item.get("result", {}).get("status") == "success"
    ]
    assert temporal
    rows = temporal[-1]["result"]["rows"]
    assert len(rows) == 1
    assert rows[0]["StartEventJoin1"] == "ev_start"
    assert rows[0]["EndEventJoin2"] == "ev_end"
    assert rows[0]["DurationMinutes"] == "2.5"
    assert "SourceRowForStartEventJoin1" in temporal[-1]["query"]
    assert "SourceRowForEndEventJoin2" in temporal[-1]["query"]


def test_run_query_plan_repairs_source_record_numeric_token_constants() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_record_row(src_1, list_row, 12, source_section, row_label).",
        "source_record_numeric_token(src_1, v_14_02_51).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        [
            "source_record_row(Line, Kind, LineNum, Section, Label), "
            "source_record_numeric_token(Line, '14_02_51')."
        ],
    )

    result = rows[0]["result"]
    assert result["status"] == "success"
    assert result["rows"][0]["Line"] == "src_1"
    assert result["reasoning_basis"]["repairs"] == [
        {"predicate": "source_record_numeric_token", "from": "'14_02_51'", "to": "v_14_02_51"}
    ]


def test_run_query_plan_derives_duration_from_compact_same_day_interval_atom() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    assert (
        runtime.assert_fact("temporary_assignment(s_007, group_c, bridge_engineering, 2026_05_02_11_00_12_30).").get(
            "status"
        )
        == "success"
    )

    rows = run_query_plan(
        runtime,
        [
            "temporary_assignment(s_007, group_c, Assignment, StartEnd).",
            "elapsed_minutes(StartEnd, EndTime, DurationMinutes).",
        ],
    )

    companion = next(item for item in rows if item["result"].get("predicate") == "compact_interval_duration_support")
    support = companion["result"]["rows"][0]
    assert support["IntervalAtom"] == "2026_05_02_11_00_12_30"
    assert support["Start"] == "2026_05_02_11_00"
    assert support["End"] == "2026_05_02_12_30"
    assert support["DurationMinutes"] == "90"
    assert support["Duration"] == "1 hour 30 minutes"


def test_run_query_plan_derives_duration_from_defined_corrected_interval() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "interval_start(preparation_interval, preparation_started).",
        "interval_end(preparation_interval, preparation_ended).",
        "corrected_timestamp(preparation_started, record_1, 2026_08_02_06_44_15).",
        "corrected_timestamp(preparation_ended, record_1, 2026_08_02_07_08_15).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["elapsed_minutes(StartTime, EndTime, DurationMinutes)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "defined_interval_duration_support")
    support = companion["result"]["rows"][0]
    assert support["Interval"] == "preparation_interval"
    assert support["StartEvent"] == "preparation_started"
    assert support["EndEvent"] == "preparation_ended"
    assert support["DurationSeconds"] == "1440"
    assert support["DurationMinutes"] == "24"
    assert support["Duration"] == "24 minutes"


def test_run_query_plan_derives_status_from_corrected_interval() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "credential_status(credential_a, active, 2026_01_15).",
        "credential_status(credential_a, active, 2026_02_11).",
        "notice_type(suspension_notice, suspension).",
        "original_interval(suspension_notice, 2026_02_03, 2026_02_10).",
        "notice_type(correction_notice, correction).",
        "corrected_interval(correction_notice, 2026_02_05, 2026_02_10).",
        "active_on(credential_a, 2026_02_04).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["credential_status(credential_a, Status, 2026_02_06)."])

    support = next(
        item
        for item in rows
        if item["result"].get("prolog_query", "").startswith("credential_status_interval_support")
    )
    assert support["result"]["rows"][0]["Status"] == "suspended"
    assert support["result"]["rows"][0]["SupportKind"] == "corrected_or_stated_interval"

    rows = run_query_plan(runtime, ["credential_status(credential_a, Status, 2026_02_04)."])

    support = next(
        item
        for item in rows
        if item["result"].get("prolog_query", "").startswith("credential_status_interval_support")
    )
    assert support["result"]["rows"][0]["Status"] == "active"
    assert support["result"]["rows"][0]["SupportKind"] == "explicit_point_state"


def test_status_interval_support_runs_when_helper_companions_disabled() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "record_status(record_alpha, pending, 2026_01_05).",
        "record_status(record_alpha, active, 2026_01_15).",
        "notice_type(pause_notice, suspension).",
        "corrected_interval(pause_notice, 2026_02_05, 2026_02_10).",
        "record_status(record_alpha, active, 2026_02_11).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["record_status(record_alpha, Status, 2026_02_06)."],
        helper_companions_enabled=False,
        include_legacy_native_helpers=False,
    )

    support = next(
        item
        for item in rows
        if item["result"].get("prolog_query", "").startswith("record_status_interval_support")
    )
    result_row = support["result"]["rows"][0]
    assert result_row["Status"] == "suspended"
    assert result_row["SupportKind"] == "corrected_or_stated_interval"
    assert "HelperClass" not in result_row
    assert support["result"]["reasoning_basis"]["kind"] == "core-local"


def test_run_query_plan_derives_status_from_scheduled_state_after_effective_date() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "credential_status(credential_a, active, 2026_02_11).",
        "scheduled_archive(credential_a, 2026_03_05).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["credential_status(credential_a, Status, 2026_03_06)."])

    support = next(
        item
        for item in rows
        if item["result"].get("prolog_query", "").startswith("credential_status_interval_support")
    )
    assert support["result"]["rows"][0]["Status"] == "archived"
    assert support["result"]["rows"][0]["SupportKind"] == "scheduled_state_transition"


def test_run_query_plan_exposes_status_timeline_summary_for_broad_status_query() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "credential_status(credential_a, pending, 2026_01_05).",
        "credential_status(credential_a, active, 2026_02_11).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["credential_status(credential_a, Status, Date)."])

    support = next(item for item in rows if item["result"].get("predicate") == "status_timeline_summary_support")
    assert support["result"]["rows"][0]["HelperClass"] == "clean-helper"
    assert support["result"]["rows"][0]["CurrentStatus"] == "active"
    assert support["result"]["rows"][0]["SupportKind"] == "latest_status_transition"


def test_status_timeline_summary_requires_status_projection_variable() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "review_status(document_a, reviewer_alpha, 2026_01_05).",
        "review_status(document_a, reviewer_beta, 2026_02_11).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["review_status(document_a, Reviewer, Date)."])

    assert not any(item["result"].get("predicate") == "status_timeline_summary_support" for item in rows)


def test_run_query_plan_exposes_scheduled_state_summary_for_scheduled_query() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    assert runtime.assert_fact("scheduled_archive(credential_a, 2026_03_05).").get("status") == "success"

    rows = run_query_plan(runtime, ["scheduled_archive(credential_a, ArchiveDate)."])

    support = next(item for item in rows if item["result"].get("predicate") == "status_timeline_summary_support")
    assert support["result"]["rows"][0]["HelperClass"] == "clean-helper"
    assert support["result"]["rows"][0]["ScheduledStatus"] == "archived"
    assert support["result"]["rows"][0]["SupportKind"] == "scheduled_state_transition"


def test_scheduled_state_summary_ignores_non_state_scheduled_events() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    assert runtime.assert_fact("scheduled_meeting(credential_a, 2026_03_05).").get("status") == "success"

    rows = run_query_plan(runtime, ["scheduled_meeting(credential_a, MeetingDate)."])

    assert not any(item["result"].get("predicate") == "status_timeline_summary_support" for item in rows)


def test_run_query_plan_exposes_identifier_alias_count_for_event_surface() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "issue_opened_on(i_01, 2026_06_01).",
        "issue_opened_on(issue_i_01, 2026_06_01).",
        "issue_opened_on(i_02, 2026_06_02).",
        "issue_opened_on(issue_i_02, 2026_06_02).",
        "issue_opened_on(i_03, 2026_06_03).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["issue_opened_on(Issue, Date)."])

    support = next(item for item in rows if item["result"].get("predicate") == "identifier_alias_count_support")
    assert support["result"]["rows"] == [
        {
            "HelperClass": "clean-helper",
            "SourcePredicate": "issue_opened_on",
            "RawEntityCount": "5",
            "DistinctEntityCount": "3",
            "CanonicalEntities": "i_01, i_02, i_03",
            "AliasGroups": "i_01: i_01, issue_i_01; i_02: i_02, issue_i_02",
            "SupportKind": "identifier_alias_distinct_count",
        }
    ]


def test_identifier_alias_count_requires_observed_canonical_suffix_entity() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "inspection_opened_on(north_zone_01, 2026_06_01).",
        "inspection_opened_on(south_zone_01, 2026_06_02).",
        "inspection_opened_on(east_zone_02, 2026_06_03).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["inspection_opened_on(Inspection, Date)."])

    assert not any(item["result"].get("predicate") == "identifier_alias_count_support" for item in rows)


def test_run_query_plan_exposes_duplicate_exclusion_count_for_unary_entity_surface() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "record_id(rec_001).",
        "record_id(rec_002).",
        "record_id(rec_003).",
        "record_id(rec_003_copy).",
        "record_duplicate_of(rec_003_copy, rec_003).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["record_id(Record)."])

    support = next(item for item in rows if item["result"].get("predicate") == "duplicate_exclusion_count_support")
    assert support["result"]["rows"] == [
        {
            "HelperClass": "clean-helper",
            "SourcePredicate": "record_id",
            "RawEntityCount": "4",
            "DistinctEntityCount": "3",
            "CanonicalEntities": "rec_001, rec_002, rec_003",
            "DuplicateGroups": "rec_003: rec_003_copy",
            "SupportKind": "duplicate_relation_distinct_count",
        }
    ]


def test_run_query_plan_derives_policy_gated_counterfactual_total() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "final_count(8).",
        "proposal_unapproved(2).",
        "temporary_record_excluded(2).",
        "estimate_withdrawn(11).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["final_count(BaseTotal).", "proposal_unapproved(Delta)."])

    support = next(
        item for item in rows if item["result"].get("predicate") == "policy_gated_counterfactual_total_support"
    )
    assert support["result"]["rows"] == [
        {
            "HelperClass": "clean-helper",
            "SupportKind": "policy_gated_counterfactual_total",
            "BasePredicate": "final_count",
            "BaseTotal": "8",
            "DeltaSources": "proposal_unapproved,temporary_record_excluded",
            "DeltaValue": "2",
            "Operation": "add_if_gate_were_lifted",
            "CounterfactualTotal": "10",
        }
    ]


def test_policy_gated_counterfactual_total_uses_gated_adjustment_subject() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "certified_total(memo_a, 12).",
        "adjustment_request(memo_a, adj_5, 4).",
        "adjustment_status(memo_a, adj_5, rejected_pending).",
        "adjustment_request(memo_a, adj_6, -2).",
        "adjustment_status(memo_a, adj_6, rejected).",
        "adjustment_request(memo_a, adj_7, 3).",
        "adjustment_status(memo_a, adj_7, approved).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["adjustment_request(memo_a, Adjustment, Delta)."])

    support = next(
        item for item in rows if item["result"].get("predicate") == "policy_gated_counterfactual_total_support"
    )
    assert support["result"]["rows"] == [
        {
            "HelperClass": "clean-helper",
            "SupportKind": "policy_gated_counterfactual_total",
            "BasePredicate": "certified_total",
            "BaseTotal": "12",
            "DeltaSources": "adjustment_request",
            "DeltaValue": "4",
            "Operation": "add_if_gate_were_lifted",
            "CounterfactualTotal": "16",
        }
    ]


def test_run_query_plan_exposes_review_bound_remaining_set_support() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "member_of(item_01, source_set_a).",
        "member_of(item_02, source_set_a).",
        "member_of(item_03, source_set_a).",
        "excluded_by(item_02, notice_a).",
        "review_source(review_a, source_set_a).",
        "review_applies_notice(review_a, notice_a).",
        "review_source(review_b, source_set_a).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["review_source(Review, SourceSet)."])

    support = next(item for item in rows if item["result"].get("predicate") == "review_remaining_set_support")
    assert support["result"]["rows"] == [
        {
            "HelperClass": "clean-helper",
            "Review": "review_a",
            "SourceSet": "source_set_a",
            "ExclusionNotice": "notice_a",
            "RemainingCount": "2",
            "RemainingMembers": "item_01, item_03",
            "ExcludedMembers": "item_02",
            "SupportKind": "review_bound_remaining_set",
        }
    ]


def test_run_query_plan_derives_residual_absolute_amount_support() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "scenario_total(sample_plan, sealed_samples, 48).",
        "allocated_absolute(sample_plan, archive_testing, 30).",
        "receives_remainder(sample_plan, field_validation).",
        "scenario_total(other_plan, sealed_samples, 20).",
        "allocated_absolute(other_plan, archive_testing, 8).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["scenario_total(sample_plan, sealed_samples, Total)."])

    support = next(item for item in rows if item["result"].get("predicate") == "residual_absolute_amount_support")
    assert support["result"]["rows"] == [
        {
            "HelperClass": "clean-helper",
            "SupportKind": "residual_absolute_amount",
            "Scenario": "sample_plan",
            "Resource": "sealed_samples",
            "TotalPredicate": "scenario_total",
            "TotalAmount": "48",
            "AllocatedPredicates": "allocated_absolute",
            "AllocatedRecipients": "archive_testing",
            "AllocatedAmount": "30",
            "RemainderRecipient": "field_validation",
            "RemainingAmount": "18",
        }
    ]


def test_run_query_plan_derives_causal_end_state_support() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "leads_to(safety_recall, closure_order).",
        "ended(closure_order, pilot_expansion).",
        "documented(archive_memo, closure_order).",
        "did_not_cause(archive_memo, closure_order).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["ended(X, pilot_expansion)."])

    support = next(item for item in rows if item["result"].get("predicate") == "causal_end_state_support")
    assert support["result"]["rows"] == [
        {
            "HelperClass": "clean-helper",
            "SupportKind": "causal_end_state_chain",
            "Cause": "safety_recall",
            "EndingEvent": "closure_order",
            "EndedState": "pilot_expansion",
            "CausePredicate": "leads_to",
            "EndPredicate": "ended",
            "ChainKind": "cause_to_ending_event",
        }
    ]


def test_summarize_counts_reference_judge_verdicts() -> None:
    rows = [
        {"ok": True, "queries": ["p(X)."], "reference_answer": "A", "reference_judge": {"verdict": "exact"}},
        {"ok": True, "queries": ["q(X)."], "reference_answer": "B", "reference_judge": {"verdict": "partial"}},
        {"ok": True, "queries": [], "reference_answer": "C", "reference_judge": {"verdict": "miss"}},
    ]

    summary = summarize(rows=rows, load_errors=[], elapsed_ms=12)

    assert summary["judge_rows"] == 3
    assert summary["judge_exact"] == 1
    assert summary["judge_partial"] == 1
    assert summary["judge_miss"] == 1


def test_summarize_counts_compatibility_rows_by_companion() -> None:
    rows = [
        {
            "ok": True,
            "query_results": [
                {
                    "result": {
                        "predicate": "industrial_sensor_support",
                        "rows": [
                            {"SupportKind": "raw_event_count", "HelperClass": "clean-helper"},
                            {"SupportKind": "sensor_vendor_model", "HelperClass": "candidate-helper"},
                        ],
                    }
                },
                {
                    "result": {
                        "predicate": "legacy_support",
                        "rows": [{"SupportKind": "legacy"}],
                    }
                },
                {
                    "result": {
                        "predicate": "item_description_detail_support",
                        "rows": [{"Item": "ex_001", "Year": "1987"}],
                        "reasoning_basis": {"kind": "core-local"},
                    }
                },
            ],
        }
    ]

    compatibility_summary = summarize_compatibility_rows(rows)

    assert compatibility_summary["row_count"] == 3
    assert compatibility_summary["row_class_counts"] == {
        "direct": 1,
        "tentative": 1,
        "unlabeled": 1,
    }
    assert compatibility_summary["companion_row_class_counts"]["industrial_sensor_support"] == {
        "direct": 1,
        "tentative": 1,
    }


def test_score_oracle_returns_none_without_answer_key() -> None:
    assert score_oracle(row={"queries": []}, oracle={}) is None


def test_temporal_join_builds_dependency_closure_for_derived_threshold() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "facility_status(eastgate_treatment_facility, offline, 2026_03_04t08_00).",
        "eastgate_offline_threshold_hours(6).",
        "boil_water_notice(millbrook, 2026_03_04t14_45, diane_cheng).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "facility_status(eastgate_treatment_facility, offline, Starttime).",
            "eastgate_offline_threshold_hours(Thresholdhours).",
            "add_hours(Starttime, Thresholdhours, Thresholdtime).",
            "boil_water_notice(Zone, Noticetime, Issuer).",
        ],
        query="elapsed_minutes(Thresholdtime, Noticetime, Minutes).",
    )

    assert joined is not None
    result = joined["result"]
    assert result["status"] == "success"
    assert any(str(row.get("Minutes")) == "45" for row in result["rows"])
    assert "facility_status(eastgate_treatment_facility, offline, Starttime)" in joined["query"]
    assert "eastgate_offline_threshold_hours(Thresholdhours)" in joined["query"]


def test_temporal_join_synthesizes_missing_threshold_bridge() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "facility_status(eastgate_treatment_facility, offline, 2026_03_04t08_00).",
        "eastgate_offline_threshold_hours(6).",
        "boil_water_notice(millbrook, 2026_03_04t14_45, diane_cheng).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "facility_status(eastgate_treatment_facility, offline, Starttime).",
            "eastgate_offline_threshold_hours(Thresholdhours).",
            "boil_water_notice(Zone, Noticetime, Issuer).",
        ],
        query="elapsed_minutes(Thresholdtime, Noticetime, Minutes).",
    )

    assert joined is not None
    assert joined["result"]["status"] == "success"
    assert any(str(row.get("Minutes")) == "45" for row in joined["result"]["rows"])
    assert "add_hours(Starttime, Thresholdhours, Thresholdtime)" in joined["query"]


def test_hoa_assessment_revenue_companion_uses_current_counts_and_rates() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "unit_count(single_family, 84).",
        "unit_count(single_family, 96).",
        "unit_count(townhome, 36).",
        "unit_count(townhome, 42).",
        "unit_count(condominium, 24).",
        "unit_count(condominium, 18).",
        "assessment_rate(single_family, 3600).",
        "assessment_rate(townhome, 3600).",
        "assessment_rate(condominium, 2700).",
        "conversion_effective_date(unit_c13, condominium, townhome).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _assessment_revenue_companion(runtime, predicate="unit_count", query="unit_count(Type, Count).")

    assert companion is not None
    rows = companion["result"]["rows"]
    assert any(row.get("RowKind") == "total" and row.get("TotalRevenue") == "545400" for row in rows)


def test_industrial_sensor_companion_derives_event_and_sensor_support() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    facts = [
        "source_record_field(src_line_0067, event_id, ev_01).",
        "source_record_field(src_line_0067, system, sys_a).",
        "source_record_field(src_line_0067, recorded_time_raw, v_2026_04_22_14_02_13).",
        "source_record_field(src_line_0074, event_id, ev_08).",
        "source_record_field(src_line_0074, system, sys_b).",
        "source_record_field(src_line_0074, recorded_time_raw, v_2026_04_22_15_09_33).",
        "source_record_field(src_line_0075, event_id, ev_09).",
        "source_record_field(src_line_0075, system, sys_a).",
        "source_record_field(src_line_0075, recorded_time_raw, v_2026_04_22_15_14_50).",
        "source_record_field(src_line_0074, description, batch_b_2026_0422_3_flagged_off_spec_by_qis_opt_12).",
        "source_record_field(src_line_0079, event_id, ev_13).",
        "source_record_field(src_line_0079, system, sys_c).",
        "source_record_field(src_line_0079, recorded_time_raw, v_2026_04_22_15_30_00).",
        "source_record_field(src_line_0079, description, maintenance_window_opened_for_sensor_diagnostics_maintenance_ticket_wo_2026_0422_1).",
        "source_record_field(src_line_0088, event_id, ev_01).",
        "source_record_field(src_line_0088, wall_clock_time_utc_corrected, v_2026_04_22_14_01_26).",
        "source_record_field(src_line_0095, event_id, ev_08).",
        "source_record_field(src_line_0095, wall_clock_time_utc_corrected, v_2026_04_22_15_11_51).",
        "source_record_field(src_line_0096, event_id, ev_09).",
        "source_record_field(src_line_0096, wall_clock_time_utc_corrected, v_2026_04_22_15_14_03).",
        "source_record_line(src_line_0095, 95).",
        "source_record_section(src_line_0095, section_4_corrected_timeline).",
        "source_record_line(src_line_0159, 159).",
        "source_record_text_atom(src_line_0159, inferred_from_these_entries_r_kim_was_not_the_originating_reporter).",
        "source_record_line(src_line_0160, 160).",
        "source_record_text_atom(src_line_0160, of_ev_08_or_ev_12_those_originated_from_qis_opt_12_automatic_flagging).",
        "sensor_id(hum_d_04).",
        "sensor_id(qis_opt_12).",
        "source_record_line(src_line_0118, 118).",
        "source_record_label(src_line_0118, qis_opt_12).",
        "source_record_section(src_line_0118, v_5_1_qis_opt_12_calibration_2026_04_15).",
        "source_record_line(src_line_0120, 120).",
        "source_record_label(src_line_0120, wo_2026_0414_3).",
        "source_record_section(src_line_0120, v_5_1_qis_opt_12_calibration_2026_04_15).",
        "source_record_text_atom(src_line_0120, calibration_ticket_wo_2026_0414_3_the_line_continued_to_operate).",
        "source_record_line(src_line_0219, 219).",
        "source_record_label(src_line_0219, hum_d_04).",
        "source_record_section(src_line_0219, section_9_sensor_register_excerpts).",
        "source_record_text_atom(src_line_0219, hum_d_04_vendor_sentec_model_sentec_rh_220_plus_location).",
        "source_record_line(src_line_0223, 223).",
        "source_record_label(src_line_0223, next_calibration_due_2026_07_12).",
        "source_record_section(src_line_0223, section_9_sensor_register_excerpts).",
        "source_record_text_atom(src_line_0223, next_calibration_due_2026_07_12).",
        "source_record_text_atom(src_line_0255, v_2026_04_25_buffer_overflow_on_dry_dl_04_confirmed_by_maintenance_team_no_recovery).",
        "source_record_text_atom(src_line_0252, v_2026_04_22_lab_2026_0422_s3_sample_sent_for_moisture_analysis).",
        "source_record_text_atom(src_line_0257, v_2026_04_29_estimated_return_date_for_lab_2026_0422_s3_per_lab_confirmation).",
        "source_record_text_atom(src_line_0044, sys_c_timestamps_are_accepted_as_wall_clock).",
        "source_record_line(src_line_0208, 208).",
        "source_record_text_atom(src_line_0208, this_packet_does_not_assign_root_cause_root_cause_assignment_is_the).",
        "source_record_line(src_line_0209, 209).",
        "source_record_text_atom(src_line_0209, function_of_a_separate_root_cause_analysis_rca_which_is_in).",
        "source_record_line(src_line_0210, 210).",
        "source_record_text_atom(src_line_0210, preparation_but_not_part_of_this_packet).",
    ]
    for fact in facts:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _industrial_sensor_companion(
        runtime,
        predicate="source_record_field",
        args=[],
        query="source_record_field(SourceRow, Header, Value).",
    )

    assert companion is not None
    rows = companion["result"]["rows"]
    details = " ".join(str(row.get("Detail", "")) for row in rows)
    assert any(
        row.get("SupportKind") == "raw_event_count"
        and row.get("Value") == "4"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "corrected_event_time"
        and row.get("Subject") == "EV-08"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "sensor_vendor_model"
        and row.get("Subject") == "HUM-D-04"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "sensor_register_section"
        and row.get("Subject") == "HUM-D-04"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "sensor_next_calibration"
        and row.get("Subject") == "HUM-D-04"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "sensor_calibration_ticket"
        and row.get("Subject") == "QIS-OPT-12"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "event_batch_identifier"
        and row.get("Subject") == "EV-08"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "event_maintenance_ticket"
        and row.get("Subject") == "EV-13"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "data_loss_status"
        and row.get("Subject") == "DRY-DL-04"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "lab_sample_status"
        and row.get("Subject") == "LAB-2026-0422-S3"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "lab_sample_estimated_return"
        and row.get("Subject") == "LAB-2026-0422-S3"
        and row.get("Value") == "2026-04-29"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "system_clock_authority"
        and row.get("Subject") == "SYS-C"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "packet_scope_exclusion"
        and row.get("Subject") == "root_cause"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "operator_not_originating_events"
        and row.get("Subject") == "R. Kim"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert "Vendor Sentec; model Sentec RH-220-Plus." in details
    assert "Next calibration due 2026-07-12." in details
    assert "R. Kim did not originate EV-08 or EV-12" in details


def test_clinic_recall_companion_derives_official_source_record_support() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    facts = [
        "source_record_text_atom(src_line_0021, high_viscosity_infusates_failure_rate_observed_in_field_returns_0_7_per).",
        "source_record_line(src_line_0021, 21).",
        "source_record_text_atom(src_line_0022, v_1_000_hours_of_use).",
        "source_record_line(src_line_0022, 22).",
        "source_record_text_atom(src_line_0027, manufacturer_contact_k_halberg_regional_liaison_eastern_network).",
        "source_record_text_atom(src_line_0074, nbfh_northbridge_family_health).",
        "source_record_text_atom(src_line_0075, epa_eastfield_pediatric_associates).",
        "source_record_text_atom(src_line_0076, cim_crestmont_internal_medicine).",
        "source_record_section(src_line_0074, section_3_network_inventory_table).",
        "source_record_section(src_line_0075, section_3_network_inventory_table).",
        "source_record_section(src_line_0076, section_3_network_inventory_table).",
        "source_record_text_atom(src_line_0116, procedure_mv_vp_04_a).",
        "source_record_text_atom(src_line_0195, medical_director_s_patient_use_exception_authority_cabinet_b_3_has).",
        "source_record_line(src_line_0195, 195).",
        "source_record_section(src_line_0195, v_8_1_nbfh_site_lead_memo).",
        "source_record_text_atom(src_line_0196, been_sealed_with_tamper_evident_tape_seal_numbers_seal_nbfh_04_001).",
        "source_record_line(src_line_0196, 196).",
        "source_record_section(src_line_0196, v_8_1_nbfh_site_lead_memo).",
        "source_record_text_atom(src_line_0197, through_seal_nbfh_04_003_one_seal_per_shelf_i_will_retain_the_keys).",
        "source_record_line(src_line_0197, 197).",
        "source_record_section(src_line_0197, v_8_1_nbfh_site_lead_memo).",
        "source_record_text_atom(src_line_0187, from_d_rourke_nbfh_site_lead).",
        "source_record_section(src_line_0187, v_8_1_nbfh_site_lead_memo).",
        "source_record_text_atom(src_line_0087, from_dr_r_iwasaki_network_medical_director).",
        "source_record_section(src_line_0087, section_4_patient_use_exception_memo).",
        "source_record_text_atom(src_line_0111, reproduced_from_the_manufacturer_technician_visit_log_2026_04_14_through).",
        "source_record_line(src_line_0111, 111).",
        "source_record_section(src_line_0111, section_5_manufacturer_repair_verification_log).",
        "source_record_text_atom(src_line_0112, v_2026_04_15).",
        "source_record_line(src_line_0112, 112).",
        "source_record_section(src_line_0112, section_5_manufacturer_repair_verification_log).",
        "source_record_text_atom(src_line_0117, coverage_all_cim_held_mp_450_devices_with_serials_in_the_inclusive).",
        "source_record_section(src_line_0117, section_5_manufacturer_repair_verification_log).",
        "source_record_text_atom(src_line_0126, coverage_epa_held_mp_450_devices_with_serials_4501_aa_100159_and).",
        "source_record_section(src_line_0126, section_5_manufacturer_repair_verification_log).",
        "source_record_text_atom(src_line_0230, issue_the_formal_release_for_verified_devices_at_the_network_level_once).",
        "source_record_field(src_line_0063, device_id, mp_009).",
        "source_record_field(src_line_0063, serial, v_4501_aa_100158).",
        "source_record_section(src_line_0230, v_8_3_network_medical_director_reply).",
        "source_record_line(src_line_0230, 230).",
    ]
    for fact in facts:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _clinic_device_recall_companion(
        runtime,
        predicate="source_record_text_atom",
        args=[],
        query="source_record_text_atom(SourceRow, TextAtom).",
    )

    assert companion is not None
    rows = companion["result"]["rows"]
    details = " ".join(str(row.get("Detail", "")) for row in rows)
    assert any(
        row.get("SupportKind") == "device_serial_lookup"
        and row.get("Subject") == "MP-009"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "manufacturer_liaison"
        and row.get("Value") == "K. Halberg"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "recall_failure_rate"
        and row.get("Value") == "0.7 per 1,000 hours of use"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "clinic_abbreviation"
        and row.get("Value") == "EPA"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "clinic_abbreviation"
        and row.get("Value") == "NBFH"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "verification_visit_date_range"
        and row.get("Subject") == "CIM/EPA"
        and row.get("Value") == "2026-04-14 through 2026-04-15"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "verification_procedure"
        and row.get("Value") == "MV-VP-04-A"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "quarantine_seal_range"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "cabinet_key_retainer"
        and row.get("Value") == "D. Rourke"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "patient_use_exception_authority"
        and "Dr. R. Iwasaki" in row.get("Value", "")
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert "K. Halberg" in details
    assert "0.7 per 1,000 hours of use" in details
    assert "EPA = Eastfield Pediatric Associates" in details
    assert "MV-VP-04-A" in details
    assert "SEAL-NBFH-04-001 through SEAL-NBFH-04-003" in details
    assert "MP-009 has serial 4501-AA-100158" in details


def test_hoa_conversion_assessment_delta_companion_derives_rate_increase() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "unit_count(townhome, 36).",
        "unit_count(townhome, 42).",
        "unit_count(condominium, 24).",
        "unit_count(condominium, 18).",
        "assessment_rate(townhome, 3600).",
        "assessment_rate(condominium, 2700).",
        "conversion_effective_date(unit_c13, condominium, townhome).",
        "conversion_effective_date(unit_c14, condominium, townhome).",
        "conversion_effective_date(unit_c15, condominium, townhome).",
        "conversion_effective_date(unit_c16, condominium, townhome).",
        "conversion_effective_date(unit_c17, condominium, townhome).",
        "conversion_effective_date(unit_c18, condominium, townhome).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _conversion_assessment_delta_companion(
        runtime,
        predicate="conversion_effective_date",
        query="conversion_effective_date(Unit, condominium, townhome).",
    )

    assert companion is not None
    assert companion["result"]["rows"][0]["RateDelta"] == "900"
    assert companion["result"]["rows"][0]["RevenueDelta"] == "5400"


def test_hoa_classification_deferral_companion_exposes_current_effect() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "unit_count(total, 156).",
        "classification_deferred(lot_52, pending_review).",
        "conditional_outcome(lot_52_reclassification, reclassified, count_157_revenue_549000).",
        "conditional_outcome(lot_52_reclassification, count_becomes_157, revenue_increase_3600).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _classification_deferral_effect_companion(
        runtime,
        predicate="classification_deferred",
        query="classification_deferred(lot_52, Status).",
    )

    assert companion is not None
    row = companion["result"]["rows"][0]
    assert row["CurrentAssessments"] == "1"
    assert row["AdditionalUnitsIfReclassified"] == "1"


def test_vacancy_voting_eligibility_companion_preserves_all_units_vote_surface() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "voting_eligibility(all_units, eligible).",
        "occupancy_status(lot_91, vacant).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _vacancy_voting_eligibility_companion(
        runtime,
        predicate="voting_eligibility",
        query="voting_eligibility(X, Y).",
    )

    assert companion is not None
    assert companion["result"]["rows"][0]["VacancyAffectsEligibility"] == "no"
    assert companion["result"]["rows"][0]["VacantUnitsCarryVotes"] == "yes"


def test_assessment_transfer_policy_companion_detects_seller_buyer_boundary() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "assessment_responsibility(lot_47, eriksen_family, 2025_01_01, 2025_01_22).",
        "assessment_responsibility(lot_47, chao_family, 2025_01_23, 2025_03_01).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _assessment_transfer_policy_companion(
        runtime,
        predicate="assessment_responsibility",
        query="assessment_responsibility(Unit, Party, StartDate, EndDate).",
    )

    assert companion is not None
    row = companion["result"]["rows"][0]
    assert row["SellerResponsibleThrough"] == "2025_01_22"
    assert row["BuyerResponsibleFrom"] == "2025_01_23"
    assert row["PolicyPattern"] == "seller_through_closing_buyer_from_day_after"


def test_temporal_join_adds_minute_precision_for_elapsed_hours() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "facility_status(eastgate_treatment_facility, offline, 2026_03_04t08_00).",
        "eastgate_offline_threshold_hours(6).",
        "boil_water_notice(millbrook, 2026_03_04t14_45, diane_cheng).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "facility_status(eastgate_treatment_facility, offline, Starttime).",
            "eastgate_offline_threshold_hours(Thresholdhours).",
            "boil_water_notice(Zone, Noticetime, Issuer).",
        ],
        query="elapsed_hours(Thresholdtime, Noticetime, Elapsedhours).",
    )

    assert joined is not None
    assert "elapsed_minutes(Thresholdtime, Noticetime, Minutes)" in joined["query"]
    assert any(
        str(row.get("Elapsedhours")) == "0" and str(row.get("Minutes")) == "45"
        for row in joined["result"]["rows"]
    )


def test_temporal_join_disambiguates_relaxed_source_slots_for_duration_helpers() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "notice_issued(bwn_2026_04_28_a, 2026_04_28_08_00, e_02).",
        "notice_lifted(bwn_2026_04_28_a, 2026_05_04_12_00, e_12).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "notice_issued(Relaxed1, Issuedtime, Relaxed3).",
            "notice_lifted(Relaxed1, Lifttime, Relaxed3).",
        ],
        query="elapsed_hours(Issuedtime, Lifttime, Totalhours).",
    )

    assert joined is not None
    assert "Relaxed3Join1" in joined["query"]
    assert "Relaxed3Join2" in joined["query"]
    assert any(
        str(row.get("Totalhours")) == "148" and str(row.get("Minutes")) == "8880"
        for row in joined["result"]["rows"]
    )


def test_placeholder_repair_promotes_lowercase_temporal_helper_slots() -> None:
    repaired = _placeholder_repaired_query("elapsed_hours(issuedtimestamp, liftedtimestamp, totalhours).")

    assert repaired is not None
    assert repaired["query"] == "elapsed_hours(Issuedtimestamp, Liftedtimestamp, Totalhours)."


def test_placeholder_repair_promotes_lowercase_event_slots() -> None:
    repaired = _placeholder_repaired_query("badge_usage(bdg_44217, ingressevent).")

    assert repaired is not None
    assert repaired["query"] == "badge_usage(bdg_44217, Ingressevent)."


def test_placeholder_repair_promotes_lowercase_evidence_slots() -> None:
    repaired = _placeholder_repaired_query("claim_evidence(claim, evidencetype, evidencesource).")

    assert repaired is not None
    assert repaired["query"] == "claim_evidence(Claim, Evidencetype, Evidencesource)."
    assert repaired["repairs"] == [
        {"index": 1, "from": "claim", "to": "Claim"},
        {"index": 2, "from": "evidencetype", "to": "Evidencetype"},
        {"index": 3, "from": "evidencesource", "to": "Evidencesource"},
    ]


def test_placeholder_repair_promotes_lowercase_document_version_slots() -> None:
    repaired = _placeholder_repaired_query("field_absent(form, emergency_contact).")

    assert repaired is not None
    assert repaired["query"] == "field_absent(Form, emergency_contact)."
    assert repaired["repairs"] == [{"index": 1, "from": "form", "to": "Form"}]


def test_placeholder_repair_promotes_lowercase_field_slot() -> None:
    repaired = _placeholder_repaired_query("field_absent(document, field).")

    assert repaired is not None
    assert repaired["query"] == "field_absent(Document, Field)."
    assert repaired["repairs"] == [
        {"index": 1, "from": "document", "to": "Document"},
        {"index": 2, "from": "field", "to": "Field"},
    ]


def test_placeholder_repair_promotes_lowercase_title_slot() -> None:
    repaired = _placeholder_repaired_query("item_id(asset_17, title).")

    assert repaired is not None
    assert repaired["query"] == "item_id(asset_17, Title)."
    assert repaired["repairs"] == [{"index": 2, "from": "title", "to": "Title"}]


def test_run_query_plan_preserves_literal_title_when_original_query_succeeds() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "document_kind(doc_a, title).",
        "document_kind(doc_b, description).",
        "document_kind(doc_c, notice).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["document_kind(doc_a, title)."])

    assert rows[0]["query"] == "document_kind(doc_a, title)."
    assert rows[0]["result"]["status"] == "success"
    assert rows[0]["result"]["rows"][0]["BoundArg1"] == "doc_a"
    assert rows[0]["result"]["rows"][0]["BoundArg2"] == "title"
    assert not any(
        row.get("query") == "document_kind(doc_a, Title)." and row.get("derived_from_queries") == ["document_kind(doc_a, title)."]
        for row in rows
    )


def test_run_query_plan_repairs_title_only_after_original_query_misses() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    assert runtime.assert_fact("item_id(asset_17, catalog_entry_alpha).").get("status") == "success"

    rows = run_query_plan(runtime, ["item_id(asset_17, title)."])

    repaired = [
        row
        for row in rows
        if row.get("query") == "item_id(asset_17, Title)."
        and row.get("derived_from_queries") == ["item_id(asset_17, title)."]
    ]
    assert repaired
    assert repaired[0]["result"]["rows"][0]["Title"] == "catalog_entry_alpha"


def test_source_record_field_repair_joins_sibling_event_field() -> None:
    repaired = _source_record_field_sibling_repaired_query(
        "source_record_field(IngressEvent, description, lab_entry)."
    )

    assert repaired is not None
    assert repaired["query"] == (
        "source_record_field(SourceRowForIngressEvent, event, IngressEvent), "
        "source_record_field(SourceRowForIngressEvent, description, lab_entry)."
    )


def test_source_record_field_repair_works_inside_conjunctive_query() -> None:
    repaired = _source_record_field_sibling_repaired_query(
        "badge_usage(bdg_44217, IngressEvent), "
        "source_record_field(IngressEvent, description, lab_entry), "
        "corrected_timestamp(IngressEvent, IngressTime)."
    )

    assert repaired is not None
    assert repaired["query"] == (
        "badge_usage(bdg_44217, IngressEvent), "
        "source_record_field(SourceRowForIngressEvent, event, IngressEvent), "
        "source_record_field(SourceRowForIngressEvent, description, lab_entry), "
        "corrected_timestamp(IngressEvent, IngressTime)."
    )


def test_run_query_plan_adds_source_record_sibling_repair_even_when_direct_query_hits_row() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    for fact in [
        "source_record_field(src_line_1, event, event_a).",
        "source_record_field(src_line_1, description, lab_entry).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_field(Event, description, lab_entry)."])

    repaired = [
        item
        for item in rows
        if "source_record_field(SourceRowForEvent, event, Event)" in item.get("query", "")
    ]
    assert repaired
    assert repaired[0]["result"]["rows"][0]["Event"] == "event_a"


def test_run_query_plan_falls_back_to_source_record_text_for_unsplit_line_field() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    assert (
        runtime.assert_fact(
            "source_record_text_atom(src_line_0006, compiled_by_s_aurelio_plant_engineering_lead)."
        ).get("status")
        == "success"
    )

    rows = run_query_plan(runtime, ["source_record_field(src_line_0006, compiled_by, CompiledBy)."])

    fallback = [
        item
        for item in rows
        if item.get("query") == "source_record_text_atom(src_line_0006, SourceTextAtom)."
    ]
    assert fallback
    assert fallback[0]["result"]["rows"][0]["SourceTextAtom"] == "compiled_by_s_aurelio_plant_engineering_lead"
    assert "source-record field text fallback" in fallback[0]["result"]["reasoning_basis"]["note"]


def test_run_query_plan_keeps_placeholder_repairs_before_relaxed_temporal_join() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "notice_issued(bwn_2026_04_28_a, 2026_04_28_08_00, e_02).",
        "notice_lifted(bwn_2026_04_28_a, 2026_05_04_12_00, e_12).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        [
            "notice_issued(bwn_2026_04_28_a, issuedtimestamp, issuedevent).",
            "notice_lifted(bwn_2026_04_28_a, liftedtimestamp, liftedevent).",
            "elapsed_hours(issuedtimestamp, liftedtimestamp, Totalhours).",
        ],
    )

    joined = [item for item in results if "elapsed_minutes" in item.get("query", "")]
    assert joined
    assert any(str(row.get("Totalhours")) == "148" for row in joined[-1]["result"]["rows"])


def test_temporal_join_localizes_repeated_event_id_provenance_variables() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "notice_issued(bwn_2026_04_28_a, 2026_04_28_08_00, e_02).",
        "notice_lifted(bwn_2026_04_28_a, 2026_05_04_12_00, e_12).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "notice_issued(bwn_2026_04_28_a, Issuedtimestamp, Eventid).",
            "notice_lifted(bwn_2026_04_28_a, Liftedtimestamp, Eventid).",
        ],
        query="elapsed_hours(Issuedtimestamp, Liftedtimestamp, Totalhours).",
    )

    assert joined is not None
    assert "EventidJoin1" in joined["query"]
    assert "EventidJoin2" in joined["query"]
    assert any(str(row.get("Totalhours")) == "148" for row in joined["result"]["rows"])


def test_clear_sample_clock_pause_companion_derives_counted_hours_during_pause() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "rule_exception(rule_6_2a, clock_pauses_on_sampler_offline).",
        "clear_sample_segment(cs_seg_1, 2026_04_30_15_00, 2026_05_01_09_00, 18).",
        "sampler_offline_interval(station_s_3, 2026_05_01_09_00, 2026_05_01_11_00, routine_sampler_maintenance).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        [
            "clear_sample_segment(Segmentid, start, end, Nominalhours).",
            "sampler_offline_interval(station, start, end, cause).",
        ],
    )

    support = [item for item in results if item.get("result", {}).get("predicate") == "clear_sample_clock_pause_support"]
    assert support
    row = support[-1]["result"]["rows"][0]
    assert row["ClockState"] == "paused"
    assert row["Rule"] == "rule_6_2a"
    assert row["CountedHours"] == "18"
    assert row["PauseStart"] == "2026_05_01_09_00"
    assert row["HelperClass"] == "clean-helper"


def test_authority_custody_companion_counts_grouped_physical_custody() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "physical_custody(notebook_b, pellico_society).",
        "physical_custody(letters_at_pellico_16, pellico_society).",
        "physical_custody(personal_letters, pellico_society).",
        "physical_custody(loose_photos_18, pellico_society).",
        "physical_custody(personal_letter_1903_04_11, stille_conservation_studio).",
        "physical_custody(notebook_a, stille_conservation_studio).",
        "physical_custody(letters_at_stille, stille_conservation_studio).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["physical_custody(Item, pellico_society)."])

    support = [item for item in results if item.get("result", {}).get("predicate") == "archive_authority_custody_support"]
    assert support
    rows = support[-1]["result"]["rows"]
    pellico = next(row for row in rows if row.get("SupportKind") == "physical_custody_count" and row.get("Holder") == "pellico_society")
    assert pellico["Count"] == "35"
    assert "letters_at_pellico_16:16" in pellico["Components"]
    assert "loose_photos_18:18" in pellico["Components"]
    assert pellico["HelperClass"] == "candidate-helper"
    stille = next(row for row in rows if row.get("SupportKind") == "physical_custody_count" and row.get("Holder") == "stille_conservation_studio")
    assert stille["Count"] == "10"


def test_authority_custody_companion_surfaces_object_custody_status_rows() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "object_custody_status(crimson_notebooks, hartwell_college_special_collections, physical_possession, 2026_05_04, probate_packet).",
        "object_custody_status(crimson_notebooks, hartwell_college_special_collections, restricted_access, 2026_04_30, probate_packet).",
        "object_custody_status(crimson_notebooks, katherine_hennessy_brown, title_claim, 2026_03_04, probate_packet).",
        "object_custody_status(crimson_notebooks, hartwell_college_special_collections, disputed, 2026_05_04, probate_packet).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        ["object_custody_status(crimson_notebooks, Holder, StatusKind, TimeOrDate, SourceDocument)."],
    )

    support = [item for item in results if item.get("result", {}).get("predicate") == "archive_authority_custody_support"]
    assert support
    rows = support[-1]["result"]["rows"]
    kinds = {row["SupportKind"] for row in rows}
    assert "physical_possession_at_time" in kinds
    assert "access_restriction_status" in kinds
    assert "legal_title_or_ownership_claim" in kinds
    assert "ownership_or_custody_dispute_status" in kinds
    assert all(row.get("HelperClass") == "clean-helper" for row in rows)


def test_authority_custody_companion_pairs_stille_access_with_pellico_authorization() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "physical_custody(letters_at_stille, stille_conservation_studio).",
        "access_log_entry(access_2026_03_11_01, 2026_03_11, dr_k_phenwick, letters_at_stille, stille_premises).",
        "access_authorized_by(access_2026_03_11_01, pellico_society_with_stille_coordination).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["access_log_entry(Event, 2026_03_11, dr_k_phenwick, Item, Location)."])

    support = [item for item in results if item.get("result", {}).get("predicate") == "archive_authority_custody_support"]
    assert support
    row = next(row for row in support[-1]["result"]["rows"] if row.get("SupportKind") == "access_custody_authorization")
    assert row["Custodian"] == "stille_conservation_studio"
    assert row["AuthorizedBy"] == "pellico_society_with_stille_coordination"
    assert row["HelperClass"] == "clean-helper"


def test_authority_custody_companion_derives_access_support_from_source_record_cells() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "physical_custody(letters_at_stille, stille_conservation_studio).",
        "source_record_cell(src_line_0112, 1, v_2026_03_11).",
        "source_record_cell(src_line_0112, 2, dr_k_phenwick).",
        "source_record_cell(src_line_0112, 3, stille_premises).",
        "source_record_cell(src_line_0112, 4, v_8_letters_under_conservation).",
        "source_record_cell(src_line_0112, 5, pellico_society_with_stille_coordination).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["source_record_cell(src_line_0112, Column, Value)."])

    support = [item for item in results if item.get("result", {}).get("predicate") == "archive_authority_custody_support"]
    assert support
    row = next(row for row in support[-1]["result"]["rows"] if row.get("SupportKind") == "access_custody_authorization")
    assert row["Custodian"] == "stille_conservation_studio"
    assert row["AuthorizedBy"] == "pellico_society_with_stille_coordination"
    assert row["Item"] == "v_8_letters_under_conservation"
    assert row["HelperClass"] == "candidate-helper"


def test_authority_custody_companion_derives_clean_custody_location_from_source_fields() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_field(src_line_0052, item_id, ex_010).",
        "source_record_field(src_line_0052, external_id, ssv_v_402_a).",
        "source_record_field(src_line_0052, custodian_physical, safestore_vault_box_v_402).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["physical_custodian(ex_010, X)."])

    support = [item for item in results if item.get("result", {}).get("predicate") == "archive_authority_custody_support"]
    assert support
    row = next(row for row in support[-1]["result"]["rows"] if row.get("SupportKind") == "source_record_custody_location")
    assert row["Item"] == "ex_010"
    assert row["Location"] == "safestore_vault_box_v_402"
    assert row["ExternalId"] == "ssv_v_402_a"
    assert row["HelperClass"] == "clean-helper"


def test_authority_custody_companion_surfaces_recall_and_notice_clauses() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "reserved_right(amendment_2024, pellico_society, recall, right_to_recall_any_item_from_a_contractor_s_custody_on_demand).",
        "custody_recall(photograph_album, stille_conservation_studio, 2026_03_03).",
        "source_record_text_atom(src_line_0040, notice_consent_of_the_trust_shall_not_be_required_for_placement_of_items_into_contractor_custody_but_the_society_shall_notify_the_trust_within_thirty_days_of_any_such_placement_of_personal_correspondence).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["reserved_right(Document, pellico_society, recall, Description)."])

    support = [item for item in results if item.get("result", {}).get("predicate") == "archive_authority_custody_support"]
    assert support
    rows = support[-1]["result"]["rows"]
    recall = next(row for row in rows if row.get("SupportKind") == "recall_clause_exercised")
    notice = next(row for row in rows if row.get("SupportKind") == "contractor_custody_consent_notice")
    assert recall["AnswerValue"] == "amendment_2024"
    assert recall["Item"] == "photograph_album"
    assert recall["HelperClass"] == "clean-helper"
    assert notice["ConsentRequired"] == "no"
    assert notice["NoticeRequired"] == "personal_correspondence_within_30_days"
    assert notice["HelperClass"] == "candidate-helper"


def test_source_record_clock_sync_companion_derives_last_successful_ntp_sync_date() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_text_atom(src_line_0106, status_timeline_resolvable_the_building_engineering_office_confirmed_on_2026_04_28_that_pem_bas_7_s_clock_had_drifted_from_ntp_pem_bas_7_s_last_successful_ntp_sync_was_2026_03_19_engineering_s_audit_measured_drift).",
        "source_record_numeric_token(src_line_0106, v_2026_03_19).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["event_occurred_at(pem_bas_7, ntp_sync, X)."])

    support = [item for item in results if item.get("result", {}).get("predicate") == "source_record_clock_sync_support"]
    assert support
    row = support[-1]["result"]["rows"][0]
    assert row["System"] == "pem_bas_7"
    assert row["SupportKind"] == "last_successful_ntp_sync"
    assert row["SyncKind"] == "last_successful_ntp_sync"
    assert row["Date"] == "2026_03_19"
    assert row["SourceRow"] == "src_line_0106"
    assert row["HelperClass"] == "clean-helper"


def test_source_record_clock_sync_companion_triggers_for_timestamp_queries() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_text_atom(src_line_0106, status_timeline_resolvable_the_building_engineering_office_confirmed_on_2026_04_28_that_pem_bas_7_s_clock_had_drifted_from_ntp_pem_bas_7_s_last_successful_ntp_sync_was_2026_03_19_engineering_s_audit_measured_drift).",
        "source_record_numeric_token(src_line_0106, v_2026_03_19).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["has_corrected_timestamp(pem_bas_7, Time)."])

    support = [item for item in results if item.get("result", {}).get("predicate") == "source_record_clock_sync_support"]
    assert support
    row = support[-1]["result"]["rows"][0]
    assert row["SupportKind"] == "last_successful_ntp_sync"
    assert row["Date"] == "2026_03_19"


def test_temporal_join_supports_elapsed_days_for_inspection_windows() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "inspection(pier_7, luis_ferreira, 2026_02_01).",
        "bypass_authorization(pier_7, luis_ferreira, 2026_03_04t15_30).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "inspection(Facility, Officer, Inspectiondate).",
            "bypass_authorization(Facility, Officer, Authtime).",
        ],
        query="elapsed_days(Inspectiondate, Authtime, Days).",
    )

    assert joined is not None
    assert joined["result"]["status"] == "success"
    assert any(str(row.get("Days")) == "31" for row in joined["result"]["rows"])


def test_temporal_elapsed_placeholder_repair_keeps_lowercase_outputs_queryable() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "extension_request(req_1, 2025_06_20).",
        "deadline_value(nov_1, response, 2025_07_02).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        [
            "extension_request(Request, extensiondate).",
            "deadline_value(Nov, response, originaldeadline).",
            "elapsed_days(Extensiondate, originaldeadline, dayselapsed).",
        ],
    )

    assert any(
        "elapsed_days(Extensiondate, Originaldeadline, Dayselapsed)" in item.get("query", "")
        and any(str(row.get("Dayselapsed")) == "12" for row in item.get("result", {}).get("rows", []))
        for item in results
    )


def test_temporal_join_recovers_from_overconstrained_date_surface() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "proceeding_event(inquiry_committee_first_meeting, february_10_2026, inquiry_committee, first_meeting).",
        "deadline_met(inquiry_report, 2026_02_10, 2026_04_25, yes).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "proceeding_event(inquiry_committee_first_meeting, Starttime, inquiry_committee, first_meeting).",
            "deadline_met(inquiry_report, Starttime, Endtime, Status).",
        ],
        query="elapsed_days(Starttime, Endtime, Elapseddays).",
    )

    assert joined is not None
    assert joined["result"]["status"] == "success"
    assert "over-constraining prior query" in joined["result"]["reasoning_basis"]["note"]
    assert any(str(row.get("Elapseddays")) == "74" for row in joined["result"]["rows"])


def test_temporal_join_localizes_order_ids_when_dates_are_the_helper_arguments() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "deadline_requirement(p_26_347_c, 2026_06_03, forensic_handwriting_analysis_report_due).",
        "hearing_scheduled(p_26_347_e, 2026_06_17, codicil_validity_evidentiary_hearing).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "deadline_requirement(Orderid, Reportduedate, forensic_handwriting_analysis_report_due).",
            "hearing_scheduled(Orderid, Hearingdate, codicil_validity_evidentiary_hearing).",
        ],
        query="elapsed_days(Reportduedate, Hearingdate, Intervaldays).",
    )

    assert joined is not None
    assert joined["result"]["status"] == "success"
    assert any(str(row.get("Intervaldays")) == "14" for row in joined["result"]["rows"])


def test_negative_query_join_supports_set_difference() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "residential_zone(millbrook).",
        "residential_zone(old_harbor).",
        "boil_water_notice(millbrook, 2026_03_04t14_45, diane_cheng).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _negative_join_with_previous(
        runtime,
        previous_queries=["residential_zone(Zone)."],
        query="\\+(boil_water_notice(Zone, Time, Issuer)).",
    )

    assert joined is not None
    assert joined["result"]["status"] == "success"
    assert joined["result"]["rows"][0]["Zone"] == "old_harbor"


def test_relaxed_constant_query_recovers_over_bound_atom_drift() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    assert runtime.assert_fact("inspection(pier_7, luis_ferreira, 2026_02_01).").get("status") == "success"

    exact = runtime.query_rows("inspection(pier_7, ferreira_luis, Date).")
    assert exact["status"] == "no_results"

    relaxed = _relaxed_constant_query(runtime, query="inspection(pier_7, ferreira_luis, Date).")

    assert relaxed is not None
    assert relaxed["result"]["status"] == "success"
    assert relaxed["result"]["reasoning_basis"]["kind"] == "core-local"
    assert relaxed["result"]["reasoning_basis"]["original_query"] == "inspection(pier_7, ferreira_luis, Date)."
    assert relaxed["result"]["rows"] == [
        {
            "Relaxed1": "pier_7",
            "Relaxed2": "luis_ferreira",
            "Date": "2026_02_01",
        }
    ]


def test_run_query_plan_falls_back_to_source_identifier_slots() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "document_type(crq_31, conservation_request).",
        "asset_status(m_208, dry_imaging_only, crq_31).",
        "asset_restriction(m_208, no_wet_flattening, cn_14).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        ["asset_restriction(crq_31, restriction, Source)."],
        helper_companions_enabled=False,
    )

    fallback = [
        item
        for item in results
        if "source-identifier slot fallback" in str(item.get("result", {}).get("reasoning_basis", {}).get("note", ""))
    ]
    assert fallback
    assert fallback[0]["query"] == "asset_status(SourceSlot1, SourceSlot2, crq_31)."
    assert fallback[0]["result"]["rows"] == [{"SourceSlot1": "m_208", "SourceSlot2": "dry_imaging_only"}]


def test_source_text_filter_over_source_id_adds_source_slot_fallback() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "document_type(crq_31, conservation_request).",
        "asset_status(m_208, dry_imaging_only, crq_31).",
        "source_record_text_atom(src_line_1, conservation_request_crq_31_is_approved_for).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        ['source_record_text_atom(SourceRow, TextAtom), memberchk("crq_31", TextAtom).'],
        helper_companions_enabled=False,
    )

    fallback = [
        item
        for item in results
        if "source-identifier slot fallback" in str(item.get("result", {}).get("reasoning_basis", {}).get("note", ""))
    ]
    assert fallback
    assert fallback[0]["query"] == "asset_status(SourceSlot1, SourceSlot2, crq_31)."


def test_source_identifier_fallback_rows_feed_temporal_join_context() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "document_type(ccl_5, cold_chain_log).",
        "event_end(evt_temp_check_f12, 2026_06_11t08_10, ccl_5).",
        "event_start(evt_alarm_f12, 2026_06_11t09_02, af_5).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        [
            "event_start(evt_temp_check_f12, Starttime, ccl_5).",
            "event_start(evt_alarm_f12, Endtime, af_5).",
            "elapsed_minutes(Starttime, Endtime, Minutes).",
        ],
        helper_companions_enabled=False,
    )

    joined = [
        item
        for item in results
        if "elapsed_minutes" in item.get("query", "")
        and item.get("result", {}).get("status") == "success"
    ]
    assert joined
    assert joined[-1]["result"]["rows"] == [
        {"Starttime": "2026_06_11t08_10", "Endtime": "2026_06_11t09_02", "Minutes": "52"}
    ]


def test_relaxed_constant_query_filters_token_subset_matches() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "located_at(ex_001, safestore_vault).",
        "located_at(ex_002, estate_warehouse_bay_4).",
        "located_at(ex_003, northpoint_regional_museum).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    exact = runtime.query_rows("located_at(Item, safestore_vault_services).")
    assert exact["status"] == "no_results"

    relaxed = _relaxed_constant_query(runtime, query="located_at(Item, safestore_vault_services).")

    assert relaxed is not None
    assert relaxed["result"]["status"] == "success"
    assert relaxed["result"]["reasoning_basis"]["token_subset_filter"] is True
    assert relaxed["result"]["reasoning_basis"]["unfiltered_num_rows"] == 3
    assert relaxed["result"]["rows"] == [{"Item": "ex_001", "Relaxed2": "safestore_vault"}]


def test_run_query_plan_derives_recall_classification_at_date() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "recall_classification(recall_oxalis_2026, class_ii, 2026_01_22).",
        "recall_reclassification(recall_oxalis_2026, class_ii, class_i, 2026_02_03).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["recall_classification(recall_oxalis_2026, Class, 2026_02_05)."])

    companion = next(
        item for item in results if item["result"].get("predicate") == "recall_classification_at_date_support"
    )
    assert companion["result"]["rows"][0]["Class"] == "class_i"
    assert companion["result"]["rows"][0]["EffectiveDate"] == "2026_02_03"


def test_run_query_plan_counts_admitted_lot_range_atoms() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    assert (
        runtime.assert_fact("unit_count(oxalis_recall_2026, 7200_2024_a_through_7200_2024_f, 2026_01_18).").get(
            "status"
        )
        == "success"
    )

    results = run_query_plan(runtime, ["unit_count(recall_oxalis_2026, lot, Date)."])

    companion = next(item for item in results if item["result"].get("predicate") == "unit_range_count_support")
    assert companion["result"]["rows"][0]["RangeCount"] == "6"
    assert companion["result"]["rows"][0]["Date"] == "2026_01_18"


def test_run_query_plan_derives_recall_accounted_units_from_latest_unaccounted() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "termination_request(recall_oxalis_2026, veridian, 2026_05_15).",
        "unit_count(recall_oxalis_2026, 4200, 2026_01_30).",
        "unit_status_change(recall_oxalis_2026, 2026_03_15, unaccounted, 353, veridian).",
        "unit_status_change(recall_oxalis_2026, 2026_05_10, unaccounted, 73, veridian).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["termination_request(recall_oxalis_2026, veridian, 2026_05_15)."])

    companion = next(item for item in results if item["result"].get("predicate") == "recall_accounted_units_support")
    row = companion["result"]["rows"][0]
    assert row["AccountedUnits"] == "4127"
    assert row["TotalUnits"] == "4200"
    assert row["UnaccountedUnits"] == "73"
    assert row["AccountedPercent"] == "98.3"


def test_run_query_plan_keeps_recall_accounted_units_scoped_to_termination_questions() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "unit_count(recall_oxalis_2026, 4200, 2026_01_30).",
        "unit_status_change(recall_oxalis_2026, 2026_05_10, unaccounted, 73, veridian).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["unit_status_change(recall_oxalis_2026, Date, accounted, Count, Actor)."])

    assert not any(item["result"].get("predicate") == "recall_accounted_units_support" for item in results)


def test_run_query_plan_derives_category_count_ratio_from_admitted_surfaces() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "inventory_disposition(batch_alpha, returned, 20, 2026_02_10).",
        "inventory_disposition(batch_alias, returned, 20, 2026_02_10).",
        "inventory_disposition(batch_alpha, repaired, 5, 2026_02_10).",
        "inventory_disposition(batch_alpha, unaccounted, 3, 2026_02_10).",
        "source_detail(batch_scope, total_units, 28_units, src_line_1).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        ["inventory_disposition(batch, status, Count, 2026_02_10)."],
        helper_companions_enabled=False,
        include_legacy_native_helpers=False,
    )

    companion = next(item for item in results if item["result"].get("predicate") == "category_count_ratio_support")
    row = companion["result"]["rows"][0]
    assert row["IncludedTotal"] == "25"
    assert row["ExcludedTotal"] == "3"
    assert row["TotalCount"] == "28"
    assert row["IncludedPercent"] == "89.3"
    assert row["IncludedCategories"] == "repaired,returned"


def test_run_query_plan_does_not_ratio_unrelated_measurement_rows() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "sensor_measurement(sensor_alpha, temperature, 20, 2026_02_10).",
        "sensor_measurement(sensor_alpha, pressure, 5, 2026_02_10).",
        "source_detail(sensor_alpha, total_units, 25_units, src_line_1).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        ["sensor_measurement(Sensor, Metric, Value, 2026_02_10)."],
        helper_companions_enabled=False,
        include_legacy_native_helpers=False,
    )

    assert not any(item["result"].get("predicate") == "category_count_ratio_support" for item in results)


def test_run_query_plan_adds_story_choice_contrast_support() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "judged(mina_moonbutton, cart_great, pride, too_proud).",
        "judged(mina_moonbutton, cart_middle, officiality, too_official).",
        "has_property(cart_little, just_brisk_enough).",
        "event(evt_mina_enter_little_cart, mina_moonbutton, entered, cart_little, kettle_house).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["has_property(cart, property)."])

    companion = next(item for item in results if item["result"].get("predicate") == "story_choice_contrast_support")
    row = companion["result"]["rows"][0]
    assert row["AcceptedCandidate"] == "cart_little"
    assert row["PositiveProperty"] == "just_brisk_enough"
    assert row["RejectedCandidates"] == "cart_great,cart_middle"


def test_run_query_plan_can_infer_story_choice_from_complete_family_contrast() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "event(evt_mina_ride_great_cart, mina_moonbutton, rode, great_cart, kettle_house).",
        "event(evt_mina_ride_middle_cart, mina_moonbutton, rode, middle_sized_cart, kettle_house).",
        "event(evt_mina_ride_little_cart, mina_moonbutton, rode, little_cart, kettle_house).",
        "said(mina_moonbutton, narrative, this_cart_is_too_proud).",
        "said(mina_moonbutton, narrative, this_cart_is_too_official).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["event(Evt, mina_moonbutton, Action, cart, Location)."])

    companion = next(item for item in results if item["result"].get("predicate") == "story_choice_contrast_support")
    row = companion["result"]["rows"][0]
    assert row["AcceptedCandidate"] == "little_cart"
    assert row["PositiveProperty"] == "accepted_by_contrast"
    assert row["EvidenceStatus"] == "inferred_by_complete_family_contrast"


def test_run_query_plan_pairs_story_remediation_method_with_extraction() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "event(evt_winding, great_burrow_mole, wound, mina_moonbutton, kettle_house).",
        "event(evt_key_extraction, great_burrow_mole, extracted, seven_silver_beetle_keys, mina_moonbutton_mouth).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["event(Event, great_burrow_mole, extracted, beetle_keys, Target)."])

    companion = next(item for item in results if item["result"].get("predicate") == "story_remediation_method_support")
    row = companion["result"]["rows"][0]
    assert row["MethodAction"] == "wound"
    assert row["Patient"] == "mina_moonbutton"
    assert row["OutcomeObject"] == "seven_silver_beetle_keys"


def test_run_query_plan_adds_roster_state_support_from_group_membership() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "group_membership(arden, red_group, 2025_10_07t09_15, 2025_10_07t16_00).",
        "group_membership(bettina, red_group, 2025_10_07t09_15, 2025_10_07t16_00).",
        "supervision_assignment(ms_strand, red_group, 2025_10_07t09_15, 2025_10_07t16_00).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["group_membership(Student, Group, Start, End)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "group_count"
        and row.get("Group") == "red_group"
        and row.get("Count") == "2"
        and row.get("Members") == "arden,bettina"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "supervision_assignment"
        and row.get("Supervisor") == "ms_strand"
        and row.get("Target") == "red_group"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert companion["result"]["reasoning_basis"]["adapter_status"] == "legacy_native_compatibility_adapter"


def test_run_query_plan_suppresses_legacy_native_helpers_when_disabled() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "group_membership(arden, red_group, 2025_10_07t09_15, 2025_10_07t16_00).",
        "group_membership(bettina, red_group, 2025_10_07t09_15, 2025_10_07t16_00).",
        "supervision_assignment(ms_strand, red_group, 2025_10_07t09_15, 2025_10_07t16_00).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["group_membership(Student, Group, Start, End)."],
        include_legacy_native_helpers=False,
    )

    assert all(item["result"].get("predicate") != "roster_state_support" for item in rows)
    assert any(item["result"].get("predicate") == "group_membership" for item in rows)


def test_run_query_plan_suppresses_legacy_native_helpers_after_generic_companion(monkeypatch) -> None:
    runtime = CorePrologRuntime(max_depth=200)

    def fake_generic_companion(*args, **kwargs):
        return {
            "query": "generic_probe.",
            "result": {
                "status": "success",
                "predicate": "status_timeline_summary_support",
                "rows": [{"SupportKind": "generic"}],
                "num_rows": 1,
            },
        }

    def fake_roster_companion(*args, **kwargs):
        return {
            "query": "legacy_roster_probe.",
            "result": {
                "status": "success",
                "predicate": "roster_state_support",
                "rows": [{"SupportKind": "legacy"}],
                "num_rows": 1,
            },
        }

    monkeypatch.setattr(qa_module, "_status_timeline_summary_companion", fake_generic_companion)
    monkeypatch.setattr(qa_module, "_roster_state_companion", fake_roster_companion)

    rows = run_query_plan(
        runtime,
        ["group_membership(Student, Group, Start, End)."],
        include_legacy_native_helpers=False,
    )

    assert any(item["result"].get("predicate") == "status_timeline_summary_support" for item in rows)
    assert all(item["result"].get("predicate") != "roster_state_support" for item in rows)


def test_run_query_plan_can_disable_helper_companion_assembly(monkeypatch) -> None:
    runtime = CorePrologRuntime(max_depth=200)
    assert runtime.assert_fact("case_status(case_a, closed, 2026_01_02).").get("status") == "success"

    called = False

    def fake_generic_companion(*args, **kwargs):
        nonlocal called
        called = True
        return {
            "query": "generic_probe.",
            "result": {
                "status": "success",
                "predicate": "status_timeline_summary_support",
                "rows": [{"HelperClass": "clean-helper", "SupportKind": "status_timeline"}],
                "num_rows": 1,
            },
        }

    monkeypatch.setattr(qa_module, "_status_timeline_summary_companion", fake_generic_companion)

    rows = run_query_plan(
        runtime,
        ["case_status(Case, Status, Date)."],
        helper_companions_enabled=False,
    )

    assert called is False
    assert any(item["result"].get("predicate") == "case_status" for item in rows)
    assert all(item["result"].get("predicate") != "status_timeline_summary_support" for item in rows)


def test_run_query_plan_dedupes_repeated_helper_companion_rows() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "group_membership(arden, red_group, 2025_10_07t09_15, 2025_10_07t16_00).",
        "group_membership(bettina, red_group, 2025_10_07t09_15, 2025_10_07t16_00).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        [
            "group_membership(Student, red_group, Start, End).",
            "group_membership(Person, red_group, From, To).",
        ],
    )

    companions = [item for item in rows if item["result"].get("predicate") == "roster_state_support"]
    assert len(companions) == 1
    assert companions[0]["result"]["num_rows"] == 3


def test_compatibility_row_limit_prefers_question_relevant_support_rows() -> None:
    results = [
        {
            "result": {
                "predicate": "grant_award_support",
                "rows": [
                    {
                        "HelperClass": "clean-helper",
                        "SupportKind": "committee_recusal_vote_count",
                        "Value": "5",
                    },
                    {
                        "HelperClass": "clean-helper",
                        "SupportKind": "appeal_window_rule",
                        "Value": "14 days",
                    },
                    {
                        "HelperClass": "clean-helper",
                        "SupportKind": "total_application_count",
                        "Value": "12",
                    },
                ],
            }
        }
    ]

    filtered = _limit_helper_query_results(
        results,
        1,
        utterance="What is the appeal window length specified by procedure?",
        queries=["grant_award(App, Status, Amount)."],
    )

    assert len(filtered) == 1
    assert filtered[0]["result"]["rows"] == [
        {
            "HelperClass": "clean-helper",
            "SupportKind": "appeal_window_rule",
            "Value": "14 days",
        }
    ]
    assert filtered[0]["result"]["reasoning_basis"]["delivery_filter"] == "query_relevance_compatibility_row_budget"


def test_helper_companion_row_limit_zero_suppresses_helper_results_only() -> None:
    results = [
        {"result": {"predicate": "direct_fact", "rows": [{"Value": "kept"}]}},
        {
            "result": {
                "predicate": "item_description_detail_support",
                "rows": [{"Item": "ex_001", "Year": "1987"}],
                "reasoning_basis": {"kind": "core-local"},
            }
        },
        {
            "result": {
                "predicate": "source_record_packet_metadata_support",
                "rows": [{"HelperClass": "clean-helper", "SupportKind": "identifier"}],
            }
        },
    ]

    filtered = _limit_helper_query_results(results, 0, utterance="Which identifier?", queries=[])

    assert filtered == [
        {"result": {"predicate": "direct_fact", "rows": [{"Value": "kept"}]}},
        {
            "result": {
                "predicate": "item_description_detail_support",
                "rows": [{"Item": "ex_001", "Year": "1987"}],
                "reasoning_basis": {"kind": "core-local"},
            }
        },
    ]


def test_run_query_plan_summarizes_type_categories_without_counting_instances() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "artifact_type(kind_a_primary_review).",
        "artifact_type(kind_b_field_test).",
        "artifact_type(kind_c_archive_copy).",
        "artifact_type(kind_a_2026).",
        "artifact_type(kind_b_2026).",
        "artifact_type(kind_c_2026).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["artifact_type(Type)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "type_category_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "type_category_summary"
        and row.get("CategoryCount") == "3"
        and row.get("RawValueCount") == "6"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "type_category"
        and row.get("CategoryKey") == "kind_a"
        and row.get("Members") == "kind_a_2026,kind_a_primary_review"
        and row.get("CategoryDisplay") == "A: primary review"
        for row in result_rows
    )


def test_run_query_plan_does_not_summarize_unrelated_type_values() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "artifact_type(primary_review).",
        "artifact_type(field_test).",
        "artifact_type(archive_copy).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["artifact_type(Type)."])

    assert not any(item["result"].get("predicate") == "type_category_support" for item in rows)


def test_run_query_plan_bundles_lifecycle_period_with_same_entity_exceptions() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "validity_period(item_a_2026, 2026_06_01, 2026_06_10).",
        "lifecycle_extension(item_a_2026, requester_unit, approver_unit, 2026_06_11).",
        "lifecycle_status(item_a_operational, active, active_through_2026_06_11_limited_use_only).",
        "validity_period(item_b_2026, 2026_06_01, 2026_06_10).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["validity_period(item_a_operational, StartDate, EndDate)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "lifecycle_period_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "lifecycle_period_summary"
        and row.get("RequestedEntity") == "item_a_operational"
        and row.get("EntityFamilyKey") == "item_a"
        and row.get("MatchedEntities") == "item_a_2026,item_a_operational"
        and row.get("StartDate") == "2026_06_01"
        and row.get("EndDate") == "2026_06_10"
        and row.get("EffectiveEndDate") == "2026_06_11"
        and row.get("ContextPredicates") == "lifecycle_extension,lifecycle_status"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "lifecycle_period_context"
        and row.get("ContextPredicate") == "lifecycle_extension"
        and row.get("ContextDate") == "2026_06_11"
        for row in result_rows
    )


def test_run_query_plan_bundles_lifecycle_context_query_with_same_entity_period() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "validity_period(item_a_2026, 2026_06_01, 2026_06_10).",
        "lifecycle_extension(item_a_2026, requester_unit, approver_unit, 2026_06_11).",
        "lifecycle_status(item_a_operational, active, limited_use_only_on_2026_06_11).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["lifecycle_extension(item_a_operational, Requester, Approver, ExtendedTo)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "lifecycle_period_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "lifecycle_period_summary"
        and row.get("RequestedEntity") == "item_a_operational"
        and row.get("StartDate") == "2026_06_01"
        and row.get("EndDate") == "2026_06_10"
        and row.get("EffectiveEndDate") == "2026_06_11"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "lifecycle_period_context"
        and row.get("ContextPredicate") == "lifecycle_status"
        and row.get("ContextArgs") == "active,limited_use_only_on_2026_06_11"
        for row in result_rows
    )


def test_run_query_plan_does_not_bundle_lifecycle_period_without_entity_family_match() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "validity_period(item_b_2026, 2026_06_01, 2026_06_10).",
        "lifecycle_extension(item_b_2026, requester_unit, approver_unit, 2026_06_11).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["validity_period(item_a_operational, StartDate, EndDate)."])

    assert not any(item["result"].get("predicate") == "lifecycle_period_support" for item in rows)


def test_run_query_plan_derives_vote_threshold_counterfactual_from_counts_and_source_tokens() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "body_vote(item_42, 2026_06_01, 3, 2, fail).",
        "voting_threshold(default_action, 4_of_7).",
        "source_record_label(src_line_001, vote_on_item_42).",
        "source_record_line(src_line_001, 1).",
        "source_record_text_atom(src_line_001, vote_on_item_42_alfa_yes_bravo_yes_casey_yes_delta_no).",
        "source_record_label(src_line_002, vote_on_item_42).",
        "source_record_line(src_line_002, 2).",
        "source_record_text_atom(src_line_002, echo_no).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["body_vote(item_42, Date, yescount, nocount, outcome)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "vote_threshold_counterfactual_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "vote_threshold_counterfactual"
        and row.get("VoteId") == "item_42"
        and row.get("BaselineYes") == "3"
        and row.get("BaselineNo") == "2"
        and row.get("ChangedVoter") == "delta"
        and row.get("CounterfactualYes") == "4"
        and row.get("CounterfactualNo") == "1"
        and row.get("CounterfactualOutcome") == "pass"
        and row.get("CounterfactualYesVoters") == "alfa,bravo,casey,delta"
        and row.get("CounterfactualNoVoters") == "echo"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )


def test_run_query_plan_derives_absent_voter_counterfactual_scenarios() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "body_vote(item_42, 2026_06_01, 3, 2, fail).",
        "voting_threshold(default_action, 4_of_7).",
        "source_record_section(src_line_001, hearing_section).",
        "source_record_label(src_line_001, members_absent).",
        "source_record_line(src_line_001, 1).",
        "source_record_text_atom(src_line_001, members_absent_delta_echo).",
        "source_record_section(src_line_002, hearing_section).",
        "source_record_label(src_line_002, vote_on_item_42).",
        "source_record_line(src_line_002, 2).",
        "source_record_text_atom(src_line_002, vote_on_item_42_alfa_yes_bravo_yes_casey_yes_fiona_no_gale_no).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["body_vote(item_42, Date, yesvotes, novotes, outcome)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "vote_threshold_counterfactual_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("ChangeAssumption") == "additional_absent_voters_all_yes"
        and row.get("ChangedVoter") == "delta,echo"
        and row.get("CounterfactualYes") == "5"
        and row.get("CounterfactualNo") == "2"
        and row.get("CounterfactualOutcome") == "pass"
        for row in result_rows
    )
    assert any(
        row.get("ChangeAssumption") == "additional_absent_voters_one_yes"
        and row.get("CounterfactualYes") == "4"
        and row.get("CounterfactualNo") == "3"
        and row.get("CounterfactualOutcome") == "pass"
        for row in result_rows
    )
    assert any(
        row.get("ChangeAssumption") == "additional_absent_voters_all_no"
        and row.get("CounterfactualYes") == "3"
        and row.get("CounterfactualNo") == "4"
        and row.get("CounterfactualOutcome") == "fail"
        for row in result_rows
    )


def test_run_query_plan_does_not_derive_vote_counterfactual_without_threshold() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    assert runtime.assert_fact("body_vote(item_42, 2026_06_01, 3, 2, fail).").get("status") == "success"

    rows = run_query_plan(runtime, ["body_vote(item_42, Date, YesCount, NoCount, Outcome)."])

    assert not any(item["result"].get("predicate") == "vote_threshold_counterfactual_support" for item in rows)


def test_run_query_plan_separates_initial_status_scope_from_later_status_context() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "site_status(site_a, affected).",
        "site_status(site_b, affected).",
        "source_record_section(src_line_001, initial_review_june_1).",
        "source_record_label(src_line_001, initial_review).",
        "source_record_line(src_line_001, 1).",
        "source_record_text_atom(src_line_001, initial_review_site_a_flagged_for_hold).",
        "source_record_section(src_line_010, expansion_june_3).",
        "source_record_label(src_line_010, later_expansion).",
        "source_record_line(src_line_010, 10).",
        "source_record_text_atom(src_line_010, later_expansion_site_b_added_after_transfer).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["site_status(Entity, affected)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "initial_status_scope_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "initial_status_summary"
        and row.get("InitialEntities") == "site_a"
        and row.get("AllStatusEntities") == "site_a,site_b"
        and row.get("LaterContextEntities") == "site_b"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "initial_status_entity"
        and row.get("Entity") == "site_a"
        and row.get("SectionAtom") == "initial_review_june_1"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )


def test_run_query_plan_does_not_emit_initial_status_scope_without_initial_source_scope() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "site_status(site_a, affected).",
        "site_status(site_b, affected).",
        "source_record_label(src_line_001, current_review).",
        "source_record_line(src_line_001, 1).",
        "source_record_text_atom(src_line_001, current_review_site_a_and_site_b_affected).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["site_status(Entity, affected)."])

    assert not any(item["result"].get("predicate") == "initial_status_scope_support" for item in rows)


def test_run_query_plan_derives_scoped_status_counts_from_scope_and_status_rows() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "is_segment_4_case(case_c_01).",
        "is_segment_4_case(case_c_02).",
        "is_segment_4_case(case_c_03).",
        "case_status(case_c_01, unresolved, 2026_09_30).",
        "case_status(case_c_02, resolved_by_authority, 2026_09_30).",
        "case_status(case_c_03, unresolved, 2026_09_30).",
        "case_status(case_c_04, unresolved, 2026_09_30).",
        "defines_status_term(genuinely_unresolved, remains_unresolved_at_packet_close).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        [
            "is_segment_4_case(Case).",
            "case_status(Case, Status, 2026_09_30).",
            "defines_status_term(genuinely_unresolved, Definition).",
        ],
    )

    result_rows = [
        row
        for item in rows
        if item["result"].get("predicate") == "scoped_status_count_support"
        for row in item["result"]["rows"]
    ]
    assert any(
        row.get("SupportKind") == "scoped_status_criterion_count"
        and row.get("ScopePredicate") == "is_segment_4_case"
        and row.get("StatusPredicate") == "case_status"
        and row.get("SemanticCriterion") == "genuinely_unresolved"
        and row.get("StatusValue") == "unresolved"
        and row.get("Count") == "2"
        and row.get("Members") == "case_c_01,case_c_03"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert not any("case_c_04" in row.get("Members", "") for row in result_rows)


def test_run_query_plan_does_not_emit_scoped_status_counts_without_scope_predicate() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "case_status(case_c_01, unresolved, 2026_09_30).",
        "case_status(case_c_02, unresolved, 2026_09_30).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["case_status(Case, unresolved, 2026_09_30)."])

    assert not any(item["result"].get("predicate") == "scoped_status_count_support" for item in rows)


def test_run_query_plan_derives_section_status_counts_from_source_record_status_labels() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_section(src_line_0106, v_3_1_lobby_ingress_timestamp_disagreement).",
        "source_record_label(src_line_0106, status_timeline_resolvable).",
        "source_record_section(src_line_0119, v_3_2_internal_event_timestamps).",
        "source_record_label(src_line_0119, status_timeline_resolvable_for_ordering_only).",
        "source_record_section(src_line_0125, v_3_3_identity_question).",
        "source_record_label(src_line_0125, status_genuinely_unresolved).",
        "source_record_section(src_line_0140, v_3_4_activity_question).",
        "source_record_label(src_line_0140, status_genuinely_unresolved).",
        "source_record_section(src_line_0152, v_3_5_departure_time).",
        "source_record_label(src_line_0152, status_timeline_resolvable).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_label(SourceRow, status_timeline_resolvable)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "scoped_status_count_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "source_section_status_count"
        and row.get("SemanticCriterion") == "timeline_resolvable"
        and row.get("Count") == "3"
        and "v_3_1_lobby_ingress_timestamp_disagreement" in row.get("Members", "")
        and "v_3_5_departure_time" in row.get("Members", "")
        for row in result_rows
    )
    assert not any(row.get("SemanticCriterion") == "genuinely_unresolved" for row in result_rows)


def test_run_query_plan_derives_section_status_counts_for_related_status_terms() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_section(src_line_0125, v_3_3_identity_question).",
        "source_record_label(src_line_0125, status_genuinely_unresolved).",
        "source_record_section(src_line_0140, v_3_4_activity_question).",
        "source_record_label(src_line_0140, status_genuinely_unresolved).",
        "source_record_section(src_line_0152, v_3_5_departure_time).",
        "source_record_label(src_line_0152, status_timeline_resolvable).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_label(SourceRow, status_genuinely_unresolved)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "scoped_status_count_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "source_section_status_count"
        and row.get("SemanticCriterion") == "genuinely_unresolved"
        and row.get("Count") == "2"
        for row in result_rows
    )
    assert not any(row.get("SemanticCriterion") == "timeline_resolvable" for row in result_rows)


def test_section_status_counts_require_source_record_label_query_surface() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_section(src_line_0125, v_3_3_identity_question).",
        "source_record_label(src_line_0125, status_genuinely_unresolved).",
        "source_record_section(src_line_0140, v_3_4_activity_question).",
        "source_record_label(src_line_0140, status_genuinely_unresolved).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["case_status(Case, unresolved)."])

    assert not any(item["result"].get("predicate") == "scoped_status_count_support" for item in rows)


def test_run_query_plan_does_not_emit_section_status_counts_for_broad_source_label_scan() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_section(src_line_0106, v_3_1_lobby_ingress_timestamp_disagreement).",
        "source_record_label(src_line_0106, status_timeline_resolvable).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_label(SourceRow, Label)."])

    assert not any(item["result"].get("predicate") == "scoped_status_count_support" for item in rows)


def test_combined_query_results_dedupe_helper_rows_across_evidence_phase() -> None:
    duplicate = {
        "query": "helper(Row).",
        "result": {
            "status": "success",
            "predicate": "roster_state_support",
            "num_rows": 1,
            "rows": [{"SupportKind": "adult_role", "Person": "a_diaz", "HelperClass": "clean-helper"}],
        },
    }

    filtered = _dedupe_helper_query_results(
        [
            duplicate,
            {
                **duplicate,
                "result": {
                    **duplicate["result"],
                    "reasoning_basis": {"kind": "evidence-bundle-plan"},
                },
            },
        ]
    )

    assert len(filtered) == 1


def test_roster_state_support_exposes_person_ratio_and_lodging_status() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "adult_role(a_diaz, parent_observer).",
        "adult_role(n_park, medical_staff).",
        "ratio_count_status(a_diaz, false).",
        "ratio_count_status(n_park, false).",
        "lodging_assignment(n_park, 206, adult).",
        "group_membership(s_001, group_a, 2026_05_01_09_00, 2026_05_01_10_00).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["adult_role(a_diaz, Role)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "adult_role"
        and row.get("Person") == "a_diaz"
        and row.get("CountsTowardRatio") == "false"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "adult_ratio_count_status"
        and row.get("Person") == "a_diaz"
        and row.get("CountsTowardRatio") == "false"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "adult_lodging_status"
        and row.get("Person") == "a_diaz"
        and row.get("LodgingStatus") == "not_assigned"
        and row.get("DisplayValue") == "a_diaz does not lodge with the group"
        for row in result_rows
    )
    assert not any(row.get("Person") == "n_park" for row in result_rows)
    assert not any(row.get("SupportKind") == "group_count" for row in result_rows)
    assert not any(row.get("SupportKind") == "group_membership" for row in result_rows)


def test_run_query_plan_adds_roster_role_hints_from_admitted_group_atoms() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "group_member(shore_team_recording, lotte, 2025_10_09t10_30_to_2025_10_09t13_00).",
        "group_member(station_b_watch, freya, 2025_10_08t10_15_to_2025_10_08t14_00).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["group_member(Group, lotte, Day)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "group_member"
        and row.get("Person") == "lotte"
        and row.get("Group") == "shore_team_recording"
        and row.get("RoleHint") == "recording,shore"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "group_member"
        and row.get("Person") == "freya"
        and row.get("Group") == "station_b_watch"
        and row.get("RoleHint") == "station_b"
        for row in result_rows
    )


def test_role_count_query_scopes_by_requested_role_not_person() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "adult_role(a_diaz, parent_observer).",
        "adult_role(t_mendez, lead_chaperone).",
        "role_counts_towards_ratio(parent_observer, false).",
        "role_counts_towards_ratio(lead_chaperone, true).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["role_counts_towards_ratio(parent_observer, Counts)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "role_ratio_scope"
        and row.get("Role") == "parent_observer"
        and row.get("CountsTowardRatio") == "false"
        for row in result_rows
    )
    assert not any(row.get("Role") == "lead_chaperone" for row in result_rows)


def test_adult_role_query_drops_generic_roster_assignments_when_role_rows_match() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "adult_role(t_mendez, lead_chaperone).",
        "adult_role(a_diaz, parent_observer).",
        "student_group_assignment(s_001, v1, group_a).",
        "source_record_section(src_line_001, roster_v1).",
        "source_record_line(src_line_001, 1).",
        "source_record_text_atom(src_line_001, group_a_1).",
        "source_record_section(src_line_002, roster_v1).",
        "source_record_line(src_line_002, 2).",
        "source_record_text_atom(src_line_002, s_001_s_002).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["adult_role(X, lead_chaperone)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "adult_role"
        and row.get("Person") == "t_mendez"
        and row.get("Role") == "lead_chaperone"
        for row in result_rows
    )
    assert not any(
        row.get("SupportKind")
        in {
            "group_count",
            "student_group_assignment",
            "source_record_student_group_assignment",
        }
        for row in result_rows
    )


def test_group_assignment_query_uses_generic_assignment_surface() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "group_assignment(person_alpha, v1, cohort_red).",
        "group_assignment(person_beta, v1, cohort_red).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["group_assignment(Person, v1, cohort_red)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "group_assignment"
        and row.get("Person") == "person_alpha"
        and row.get("Group") == "cohort_red"
        and row.get("Version") == "v1"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "group_count"
        and row.get("Group") == "cohort_red"
        and row.get("Version") == "v1"
        and row.get("Count") == "2"
        for row in result_rows
    )


def test_roster_version_query_keeps_version_level_support_not_member_roster_volume() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "roster_version(v1, 2026_04_01, operational).",
        "student_group_assignment(s_001, v1, group_a).",
        "student_group_assignment(s_002, v1, group_a).",
        "source_record_section(src_line_001, roster_v1).",
        "source_record_line(src_line_001, 1).",
        "source_record_text_atom(src_line_001, group_a_2).",
        "source_record_section(src_line_002, roster_v1).",
        "source_record_line(src_line_002, 2).",
        "source_record_text_atom(src_line_002, s_001_s_002).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["roster_version(v1, Date, Status)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "group_count"
        and row.get("Group") == "group_a"
        and row.get("Version") == "v1"
        and row.get("Count") == "2"
        for row in result_rows
    )
    assert not any(
        row.get("SupportKind")
        in {
            "student_group_assignment",
            "source_record_student_group_assignment",
        }
        for row in result_rows
    )
    all_roster_rows = [
        row
        for item in rows
        if item["result"].get("predicate") == "roster_state_support"
        for row in item["result"].get("rows", [])
    ]
    assert not any(
        row.get("SupportKind")
        in {
            "student_group_assignment",
            "source_record_student_group_assignment",
        }
        for row in all_roster_rows
    )


def test_student_assignment_broad_version_scan_prefers_group_counts() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "student_group_assignment(s_001, v3, group_a).",
        "student_group_assignment(s_002, v3, group_a).",
        "student_group_assignment(s_003, v2, group_a).",
        "source_record_section(src_line_001, roster_v3).",
        "source_record_line(src_line_001, 1).",
        "source_record_text_atom(src_line_001, group_a_2).",
        "source_record_section(src_line_002, roster_v3).",
        "source_record_line(src_line_002, 2).",
        "source_record_text_atom(src_line_002, s_001_s_002).",
        "source_record_section(src_line_003, roster_v2).",
        "source_record_line(src_line_003, 3).",
        "source_record_text_atom(src_line_003, group_a_1).",
        "source_record_section(src_line_004, roster_v2).",
        "source_record_line(src_line_004, 4).",
        "source_record_text_atom(src_line_004, s_003).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["student_group_assignment(Student, Group, roster_v3)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "group_count"
        and row.get("Group") == "group_a"
        and row.get("Version") == "v3"
        and row.get("Count") == "2"
        for row in result_rows
    )
    assert not any(row.get("Version") == "v2" for row in result_rows)
    assert not any(
        row.get("SupportKind")
        in {
            "student_group_assignment",
            "source_record_student_group_assignment",
        }
        for row in result_rows
    )


def test_student_assignment_swapped_group_version_slots_still_yield_clean_group_counts() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "student_group_assignment(s_001, group_a, roster_v3).",
        "student_group_assignment(s_002, group_a, roster_v3).",
        "source_record_section(src_line_001, roster_v3).",
        "source_record_line(src_line_001, 1).",
        "source_record_text_atom(src_line_001, group_a_2).",
        "source_record_section(src_line_002, roster_v3).",
        "source_record_line(src_line_002, 2).",
        "source_record_text_atom(src_line_002, s_001_s_002).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["student_group_assignment(Student, Group, roster_v3)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "group_count"
        and row.get("Group") == "group_a"
        and row.get("Version") == "v3"
        and row.get("Count") == "2"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )


def test_source_record_section_display_renders_normalized_section_atoms() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_section(src_line_0074, v_1_4_roster_v3_2026_04_15).",
        "source_record_line(src_line_0074, 74).",
        "source_record_section(src_line_0225, v_6_1_temporary_in_day_assignment).",
        "source_record_line(src_line_0225, 225).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_section(SourceRow, SectionAtom)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "source_record_section_display")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SourceRow") == "src_line_0074"
        and row.get("DisplaySection") == "Section 1.4"
        and row.get("SectionTitleHint") == "roster_v3_2026_04_15"
        for row in result_rows
    )
    assert any(
        row.get("SourceRow") == "src_line_0225"
        and row.get("DisplaySection") == "Section 6.1"
        and row.get("SectionTitleHint") == "temporary_in_day_assignment"
        for row in result_rows
    )


def test_source_record_packet_metadata_surfaces_identifiers_and_pending_items() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_label(src_line_0158, sco_ch_3).",
        "source_record_text_atom(src_line_0003, packet_id_chms_rso_2026_t07).",
        "source_record_text_atom(src_line_0158, sco_ch_3_chaperone_counting_rules_defines_who_counts_toward_the).",
        "source_record_text_atom(src_line_0198, a_handheld_scanner_dev_scan_07_records_badge_taps).",
        "source_record_text_atom(src_line_0102, v_2_1_bus_1_driver_v_lee_license_cdl_ma_44291).",
        "source_record_text_atom(src_line_0192, a_diaz_is_the_parent_of_s_014_and_is_permitted_to_observe_group_b).",
        "source_record_text_atom(src_line_0193, events_on_saturday_afternoon_only_2026_05_02_13_00_17_00_a_diaz).",
        "source_record_text_atom(src_line_0249, return_leg_attendance_scans_will_be_appended_after_the_trip_and).",
        "source_record_section(src_line_0104, v_2_1_bus_1_driver_v_lee_license_cdl_ma_44291).",
        "source_record_line(src_line_0104, 104).",
        "source_record_text_atom(src_line_0104, capacity_24_students_departure_2026_05_01_06_30_from_cedar_hollow).",
        "source_record_line(src_line_0149, 149).",
        "source_record_text_atom(src_line_0149, adult_lodging_t_mendez_202_j_phelps_204_k_rosario_208).",
        "source_record_line(src_line_0150, 150).",
        "source_record_text_atom(src_line_0150, m_okonkwo_210_n_park_206_medical_coverage_station).",
        "source_record_line(src_line_0262, 262).",
        "source_record_text_atom(src_line_0262, retained_in_the_audit_binder_location_activities_office_filing).",
        "source_record_line(src_line_0263, 263).",
        "source_record_text_atom(src_line_0263, cabinet_3_drawer_2_and_are_not_the_operational_document).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_text_atom(Line, Text)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "compact_identifier"
        and row.get("Value") == "sco_ch_3"
        and row.get("DisplayValue") == "SCO-CH-3"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "compact_identifier"
        and row.get("DisplayValue") == "CHMS-RSO-2026-T07"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "compact_identifier"
        and row.get("DisplayValue") == "DEV-SCAN-07"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "compact_identifier"
        and row.get("DisplayValue") == "CDL-MA-44291"
        for row in result_rows
    )
    retired_candidate_kinds = {
        "adult_lodging_location",
        "observer_permission_scope",
        "pending_packet_item",
        "physical_retention_location",
        "policy_name",
        "role_authority_definition",
        "role_restriction_definition",
        "transport_departure",
    }
    assert not any(row.get("Kind") in retired_candidate_kinds for row in result_rows)


def test_source_record_packet_metadata_does_not_attach_identifier_inventory_to_unrelated_bound_queries() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "adult_role(person_alpha, lead_role).",
        "source_record_text_atom(src_line_001, packet_id_demo_2026_a).",
        "source_record_label(src_line_002, policy_demo_2026_b).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["adult_role(Person, lead_role)."])

    assert not any(
        item["result"].get("predicate") == "source_record_packet_metadata_support"
        for item in rows
    )


def test_source_record_packet_metadata_compacts_broad_identifier_inventory() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_text_atom(src_line_001, packet_id_chms_rso_2026_t07).",
        "source_record_text_atom(src_line_002, packet_id_chms_rso_2026_t07).",
        "source_record_label(src_line_003, sco_ch_3).",
        "source_record_text_atom(src_line_004, sco_ch_3_chaperone_counting_rules).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_text_atom(Line, Text)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert sum(1 for row in result_rows if row.get("Kind") == "compact_identifier") == 2
    assert any(row.get("DisplayValue") == "CHMS-RSO-2026-T07" for row in result_rows)
    assert any(row.get("DisplayValue") == "SCO-CH-3" for row in result_rows)


def test_source_record_packet_metadata_keeps_discovery_notes_anchored_to_source_rows() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_label(src_line_0062, note_v2_errata_discovered_2026_04_14_by_team_coach_p_rivera).",
        "source_record_text_atom(src_line_0062, note_v2_errata_discovered_2026_04_14_by_team_coach_p_rivera).",
        "source_record_numeric_token(src_line_0062, v_2026_04_14).",
        "source_record_text_atom(src_line_0063, unrelated_packet_note).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    broad_rows = run_query_plan(runtime, ["source_record_text_atom(Line, Text)."])
    assert not any(
        item["result"].get("predicate") == "source_record_packet_metadata_support"
        and any(row.get("Kind") == "source_record_discovery_note" for row in item["result"].get("rows", []))
        for item in broad_rows
    )

    rows = run_query_plan(runtime, ["source_record_text_atom(src_line_0062, Text)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "source_record_discovery_note"
        and row.get("Value") == "v_2026_04_14"
        and "discovered on 2026-04-14" in row.get("DisplayValue", "")
        and "team coach p rivera" in row.get("DisplayValue", "")
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )


def test_source_record_packet_metadata_surfaces_temporal_source_notes_without_fixture_terms() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_row(src_line_0029, labeled_line, 29, scope_expansion, zone_5).",
        "source_record_section(src_line_0029, scope_expansion).",
        "source_record_line(src_line_0029, 29).",
        "source_record_text_atom(src_line_0029, site_manager_m_river_reported_to_auditor_that_batch_7a_units_had_been_temporarily_moved_to_zone_5_on_july_30_for_rework_then_returned_to_zone_3_on_august_2_this_movement_was_not_disclosed_during_the_initial_inspection).",
        "source_record_row(src_line_0035, list_row, 35, scope_expansion, zone_5).",
        "source_record_section(src_line_0035, scope_expansion).",
        "source_record_line(src_line_0035, 35).",
        "source_record_text_atom(src_line_0035, zone_5_batch_9c_widgets_15_units_not_quarantined_batch_9c_arrived_in_zone_5_on_august_5_after_the_batch_7a_units_were_returned_to_zone_3_no_overlap_exposure).",
        "event_occurred(evt_movement_1, movement, 2025_07_30).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["event_occurred(Event, movement, Date)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "source_record_temporal_event_note"
        and row.get("Subject") == "batch_7a"
        and row.get("Action") == "temporarily_moved_and_returned"
        and row.get("Location") == "zone_5"
        and row.get("ReturnLocation") == "zone_3"
        and row.get("ReportedBy") == "site_manager_m_river"
        and "movement was not disclosed" in row.get("DisplayValue", "")
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "source_record_temporal_relation_note"
        and row.get("Subject") == "batch_9c"
        and row.get("RelatedSubject") == "batch_7a"
        and row.get("Relation") == "after_return"
        and row.get("TemporalStatus") == "no_overlap_exposure"
        and "no overlap exposure" in row.get("DisplayValue", "")
        for row in result_rows
    )


def test_source_record_packet_metadata_surfaces_generic_event_time_notes() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_row(src_line_0010, labeled_line, 10, event_sequence, calendar_context).",
        "source_record_section(src_line_0010, event_sequence).",
        "source_record_line(src_line_0010, 10).",
        "source_record_text_atom(src_line_0010, on_april_4_the_team_started_the_trial).",
        "source_record_row(src_line_0012, labeled_line, 12, event_sequence, timed_event).",
        "source_record_section(src_line_0012, event_sequence).",
        "source_record_line(src_line_0012, 12).",
        "source_record_text_atom(src_line_0012, about_1415_when_the_device_was_in_room_7_the_guard_arm_released_and_the_status_changed_to_open).",
        "source_record_numeric_token(src_line_0012, v_1415).",
        "event_occurred(evt_release, released, 1415).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["event_occurred(Event, released, Time)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "source_record_event_time_note"
        and row.get("EventTime") == "v_1415"
        and row.get("EventDate") == "v_04_04"
        and row.get("TemporalQualifier") == "about"
        and row.get("EventAction") == "released"
        and row.get("EventSubject") == "guard_arm"
        and "About 1415 on April 4" in row.get("DisplayValue", "")
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )


def test_temporal_source_text_hint_joins_filtered_text_to_numeric_tokens() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_row(src_line_0010, labeled_line, 10, event_sequence, calendar_context).",
        "source_record_section(src_line_0010, event_sequence).",
        "source_record_line(src_line_0010, 10).",
        "source_record_text_atom(src_line_0010, on_april_4_the_team_started_the_trial).",
        "source_record_row(src_line_0012, labeled_line, 12, event_sequence, timed_event).",
        "source_record_section(src_line_0012, event_sequence).",
        "source_record_line(src_line_0012, 12).",
        "source_record_text_atom(src_line_0012, about_1415_when_the_device_was_in_room_7_the_guard_arm_released_and_the_status_changed_to_open).",
        "source_record_numeric_token(src_line_0012, v_1415).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        [
            'source_record_text_atom(SourceRow, TextAtom), memberchk("released", TextAtom), '
            "source_record_numeric_token(SourceRow, NumericToken)."
        ],
    )

    result = rows[0]["result"]
    assert result["predicate"] == "source_record_text_atom"
    assert result["rows"] == [
        {
            "SourceRow": "src_line_0012",
            "TextAtom": "about_1415_when_the_device_was_in_room_7_the_guard_arm_released_and_the_status_changed_to_open",
            "NumericToken": "v_1415",
        }
    ]


def test_source_record_packet_metadata_surfaces_sample_result_notes_without_fixture_terms() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_row(src_line_0055, anchored_line, 55, lab_result, v_3_of_5_samples_from_batch_9c_tested_positive).",
        "source_record_section(src_line_0055, lab_result).",
        "source_record_line(src_line_0055, 55).",
        "source_record_text_atom(src_line_0055, v_3_of_5_samples_from_batch_9c_tested_positive_for_contaminant).",
        "source_record_text_atom(src_line_0061, the_laboratory_report_ref_lab_2026_0422_confirmed_contaminant_in_4_of_the_6_sampled_units_from_batch_7a_the_other_2_samples_were_negative).",
        "lab_result(lab_1, batch_9c, positive, 5).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["lab_result(Report, batch_9c, positive, Count)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "source_record_sample_result_note"
        and row.get("Subject") == "batch_9c"
        and row.get("Result") == "positive"
        and row.get("Count") == "3"
        and row.get("Total") == "5"
        and "3 of 5" in row.get("DisplayValue", "")
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "source_record_sample_result_note"
        and row.get("Subject") == "batch_7a"
        and row.get("Count") == "4"
        and row.get("Total") == "6"
        for row in result_rows
    )


def test_source_record_packet_metadata_links_time_token_to_source_section_without_fixture_terms() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "system_log_event(evt_1, 14_02_51, operator_a, withdrawal).",
        "source_record_row(src_line_0039, list_row, 39, v_4_device_cabinet_log_room_9_excerpt, item_123).",
        "source_record_section(src_line_0039, v_4_device_cabinet_log_room_9_excerpt).",
        "source_record_line(src_line_0039, 39).",
        "source_record_text_atom(src_line_0039, v_14_02_51_operator_a_withdraw_item_123).",
        "source_record_numeric_token(src_line_0039, v_14_02_51).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["system_log_event(Event, 14_02_51, Actor, Action)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "source_record_matching_token_source"
        and row.get("MatchedToken") == "v_14_02_51"
        and row.get("SourceName") == "v_4_device_cabinet_log_room_9_excerpt"
        and row.get("DisplaySourceName") == "device cabinet log room 9 excerpt"
        and row.get("SourceAddressability") == "bound_query_token"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )


def test_source_record_packet_metadata_surfaces_timestamp_authority_without_fixture_terms() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "system_log_event(evt_1, 14_02_51, operator_a, withdrawal).",
        "source_record_row(src_line_0124, anchored_line, 124, addendum_c_timestamp_correction, event_was_first_recorded).",
        "source_record_section(src_line_0124, addendum_c_timestamp_correction).",
        "source_record_line(src_line_0124, 124).",
        "source_record_text_atom(src_line_0124, the_event_was_first_recorded_in_the_device_nightly_summary_as_14_02_21_after_clock_skew_was_corrected_on_march_12_2026_the_authoritative_timestamp_from_the_central_server_record_is_14_02_51_the_earlier_nightly_summary_value_14_02_21_should_be_considered_superseded).",
        "source_record_numeric_token(src_line_0124, v_14_02_21).",
        "source_record_numeric_token(src_line_0124, v_14_02_51).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["system_log_event(Event, Time, Actor, Action)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "source_record_timestamp_authority_note"
        and row.get("PreferredTimestamp") == "v_14_02_51"
        and row.get("PreferredSource") == "the_central_server_record"
        and row.get("SupersededTimestamp") == "v_14_02_21"
        and row.get("SupersededSource") == "nightly_summary"
        and row.get("AuthorityStatus") == "authoritative_over_superseded"
        for row in result_rows
    )


def test_source_record_packet_metadata_surfaces_statement_filing_notes_without_fixture_terms() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "staff_statement(stmt_001, person_alpha, checked_device_status).",
        "source_record_row(src_line_0012, labeled_line, 12, statements_section, person_alpha_rn_statement_filed_16_02).",
        "source_record_section(src_line_0012, statements_section).",
        "source_record_line(src_line_0012, 12).",
        "source_record_text_atom(src_line_0012, person_alpha_rn_statement_filed_16_02).",
        "source_record_numeric_token(src_line_0012, v_16_02).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["staff_statement(StatementId, Speaker, Content)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "source_record_statement_filing_note"
        and row.get("Speaker") == "person_alpha"
        and row.get("FiledTime") == "v_16_02"
        and row.get("StatementRole") == "rn"
        and row.get("StatementId") == "stmt_001"
        and row.get("StatementContent") == "checked_device_status"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )


def test_source_record_packet_metadata_accepts_generic_recorded_statement() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "recorded_statement(stmt_001, person_alpha, checked_device_status).",
        "source_record_row(src_line_0012, labeled_line, 12, statements_section, person_alpha_rn_statement_filed_16_02).",
        "source_record_section(src_line_0012, statements_section).",
        "source_record_line(src_line_0012, 12).",
        "source_record_text_atom(src_line_0012, person_alpha_rn_statement_filed_16_02).",
        "source_record_numeric_token(src_line_0012, v_16_02).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["recorded_statement(StatementId, Speaker, Content)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "source_record_statement_filing_note"
        and row.get("Speaker") == "person_alpha"
        and row.get("FiledTime") == "v_16_02"
        and row.get("StatementRole") == "rn"
        and row.get("StatementId") == "stmt_001"
        and row.get("StatementContent") == "checked_device_status"
        for row in result_rows
    )


def test_broad_source_record_queries_do_not_flood_high_pressure_candidate_notes() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "staff_statement(stmt_001, person_alpha, checked_device_status).",
        "system_log_event(evt_1, 14_02_51, operator_a, withdrawal).",
        "event_occurred(evt_release, released, 1415).",
        "source_record_row(src_line_0012, labeled_line, 12, statements_section, person_alpha_rn_statement_filed_16_02).",
        "source_record_section(src_line_0012, statements_section).",
        "source_record_text_atom(src_line_0012, person_alpha_rn_statement_filed_16_02).",
        "source_record_numeric_token(src_line_0012, v_16_02).",
        "source_record_row(src_line_0030, anchored_line, 30, correction_section, event_was_first_recorded).",
        "source_record_section(src_line_0030, correction_section).",
        "source_record_text_atom(src_line_0030, event_was_first_recorded_in_the_device_summary_as_14_02_21_the_authoritative_timestamp_from_the_server_record_is_14_02_51).",
        "source_record_numeric_token(src_line_0030, v_14_02_21).",
        "source_record_numeric_token(src_line_0030, v_14_02_51).",
        "source_record_row(src_line_0040, labeled_line, 40, event_sequence, timed_event).",
        "source_record_section(src_line_0040, event_sequence).",
        "source_record_text_atom(src_line_0040, about_1415_when_the_device_was_in_room_7_the_guard_arm_released_and_the_status_changed_to_open).",
        "source_record_numeric_token(src_line_0040, v_1415).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_text_atom(Line, Text)."])

    candidate_kinds = {
        row.get("Kind")
        for item in rows
        if item["result"].get("predicate") == "source_record_packet_metadata_support"
        for row in item["result"].get("rows", [])
    }
    assert "source_record_statement_filing_note" not in candidate_kinds
    assert "source_record_timestamp_authority_note" not in candidate_kinds
    assert "source_record_event_time_note" not in candidate_kinds


def test_source_record_packet_metadata_surfaces_routing_order_and_timed_source_notes() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "has_role(person_beta, reviewer, 2026_04_01, day).",
        "order(ord_1001, clinician_alpha, 2026_04_01_09_00, infusion_protocol).",
        "telemetry_reading(subject_a, 2026_04_01_10_15_30, rhythm_event, observed).",
        "source_record_row(src_line_0010, anchored_line, 10, review_section, request_was_routed).",
        "source_record_section(src_line_0010, review_section).",
        "source_record_text_atom(src_line_0010, review_request_was_routed_to_person_beta_md_quality_director_for_review).",
        "source_record_row(src_line_0020, anchored_line, 20, order_section, protocol_order).",
        "source_record_section(src_line_0020, order_section).",
        "source_record_text_atom(src_line_0020, infusion_per_protocol_order_ord_1001_entered_by_clinician_alpha_at_09_00).",
        "source_record_row(src_line_0021, anchored_line, 21, order_section, authority_note).",
        "source_record_section(src_line_0021, order_section).",
        "source_record_text_atom(src_line_0021, attending_physician_s_signed_order_is_the_authoritative_directive_resident_verbal_order_at_09_30_was_requiring_attending_co_signature_the_10_45_attending_order_satisfies_that_requirement).",
        "source_record_row(src_line_0030, list_row, 30, telemetry_monitor_device_x_subject_a_room_12, event_row).",
        "source_record_section(src_line_0030, telemetry_monitor_device_x_subject_a_room_12).",
        "source_record_text_atom(src_line_0030, v_10_15_30_rhythm_event_observed).",
        "source_record_numeric_token(src_line_0030, v_10_15_30).",
        "source_record_row(src_line_0040, anchored_line, 40, timekeeping_section, clock_out).",
        "source_record_section(src_line_0040, timekeeping_section).",
        "source_record_text_atom(src_line_0040, person_gamma_rn_clocked_out_of_the_timekeeping_system_at_11_14).",
        "source_record_row(src_line_0050, anchored_line, 50, item_event_section, item_event).",
        "source_record_section(src_line_0050, item_event_section).",
        "source_record_text_atom(src_line_0050, device_at_bedside_checked_lot_abc_2026_0241_hung_13_44_remaining_count_2).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    role_rows = run_query_plan(runtime, ["has_role(Person, quality_director, 2026_04_01, day)."])
    broad_role_rows = run_query_plan(runtime, ["has_role(Person, Role, Date, Shift)."])
    order_rows = run_query_plan(runtime, ["order(OrderId, Prescriber, Time, Detail)."])
    telemetry_rows = run_query_plan(runtime, ["telemetry_reading(Subject, 2026_04_01_10_15_30, Event, Status)."])
    clock_rows = run_query_plan(runtime, ["has_role(person_gamma, Role, Date, Shift)."])
    system_event_rows = run_query_plan(runtime, ["system_event(Event, 2026_04_01_13_44_00, Actor, Action, Detail)."])

    all_metadata = [
        row
        for rows in (role_rows, order_rows, telemetry_rows, clock_rows)
        for item in rows
        if item["result"].get("predicate") == "source_record_packet_metadata_support"
        for row in item["result"].get("rows", [])
    ]
    system_event_metadata = [
        row
        for item in system_event_rows
        if item["result"].get("predicate") == "source_record_packet_metadata_support"
        for row in item["result"].get("rows", [])
    ]
    broad_role_metadata = [
        row
        for item in broad_role_rows
        if item["result"].get("predicate") == "source_record_packet_metadata_support"
        for row in item["result"].get("rows", [])
    ]
    assert any(
        row.get("Kind") == "source_record_role_routing_note"
        and row.get("RoutedTo") == "person_beta"
        and row.get("Role") == "quality_director"
        for row in all_metadata
    )
    assert not any(row.get("Kind") == "source_record_role_routing_note" for row in broad_role_metadata)
    assert any(
        row.get("Kind") == "source_record_order_identifier_note"
        and row.get("OrderId") == "ord_1001"
        and row.get("DisplayOrderId") == "ORD-1001"
        and row.get("OrderScope") == "protocol_order"
        for row in all_metadata
    )
    assert any(
        row.get("Kind") == "source_record_order_authority_note"
        and row.get("Requirement") == "attending_co_signature"
        and row.get("AuthoritativeOrderTime") == "v_10_45"
        for row in all_metadata
    )
    assert any(
        row.get("Kind") == "source_record_matching_token_source"
        and row.get("SourceName") == "telemetry_monitor_device_x_subject_a_room_12"
        and row.get("MatchedToken") == "v_2026_04_01_10_15_30"
        and row.get("SourceAddressability") == "bound_query_token"
        and row.get("HelperClass") == "clean-helper"
        for row in all_metadata
    )
    assert any(
        row.get("Kind") == "source_record_clock_event_note"
        and row.get("Actor") == "person_gamma"
        and row.get("EventTime") == "v_11_14"
        for row in all_metadata
    )
    assert any(
        row.get("Kind") == "source_record_item_event_identifier_note"
        and row.get("ItemIdentifier") == "abc_2026_0241"
        and row.get("DisplayItemIdentifier") == "ABC-2026-0241"
        and row.get("EventAction") == "hung"
        and row.get("EventTime") == "v_13_44"
        for row in system_event_metadata
    )


def test_source_record_packet_metadata_exposes_grant_packet_identifiers_and_rules() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_label(src_line_0003, cycle_id).",
        "source_record_text_atom(src_line_0003, cycle_id_bwcf_mg_2026_s).",
        "source_record_section(src_line_0095, v_5_1_score_correction_memo_sc_2026_04_22).",
        "source_record_text_atom(src_line_0101, paper_score_sheet_was_correct_the_correction_memo_sc_2026_04_22).",
        "source_record_field(src_line_0117, recusal_memo, rc_2026_04_20_v).",
        "source_record_text_atom(src_line_0122, items_and_does_not_automatically_decide_the_named_item_in_any_direction).",
        "source_record_text_atom(src_line_0179, v_2026_04_29_within_the_14_day_appeal_window_from_the_decision_letter).",
        "source_record_text_atom(src_line_0180, v_2026_04_27_the_appeal_is_logged_as_ap_2026_0429_a).",
        "source_record_text_atom(src_line_0189, on_2026_05_22_as_of_the_compilation_date_ap_2026_0429_a_is).",
        "source_record_line(src_line_0223, 223).",
        "source_record_text_atom(src_line_0223, cycle_procedure_manual_bwcf_cp_2025_defines_threshold_vote).",
        "source_record_line(src_line_0224, 224).",
        "source_record_text_atom(src_line_0224, requirement_for_borderline_scores_appeal_window_and_supplementary).",
        "source_record_row(src_line_0221, list_row, 221, section_11_provenance_and_source_notes, briarwood_foundation_by_laws_defines_committee_composition_and).",
        "source_record_section(src_line_0221, section_11_provenance_and_source_notes).",
        "source_record_text_atom(src_line_0221, briarwood_foundation_by_laws_defines_committee_composition_and).",
        "source_record_row(src_line_0226, list_row, 226, section_11_provenance_and_source_notes, reviewer_score_sheets_paper_originals_filed_in_audit_binder_the).",
        "source_record_section(src_line_0226, section_11_provenance_and_source_notes).",
        "source_record_text_atom(src_line_0226, reviewer_score_sheets_paper_originals_filed_in_audit_binder_the).",
        "source_record_row(src_line_0228, list_row, 228, section_11_provenance_and_source_notes, decision_letters_issued_separately_to_each_applicant_not_in).",
        "source_record_section(src_line_0228, section_11_provenance_and_source_notes).",
        "source_record_text_atom(src_line_0228, decision_letters_issued_separately_to_each_applicant_not_in).",
        "source_record_row(src_line_0230, list_row, 230, section_11_provenance_and_source_notes, census_designated_rural_block_data_most_recent_decennial_census).",
        "source_record_section(src_line_0230, section_11_provenance_and_source_notes).",
        "source_record_text_atom(src_line_0230, census_designated_rural_block_data_most_recent_decennial_census).",
        "source_record_line(src_line_0233, 233).",
        "source_record_text_atom(src_line_0233, not_the_operational_composite_recusal_memos_rc_2026_04_20_v_and).",
        "source_record_line(src_line_0234, 234).",
        "source_record_text_atom(src_line_0234, rc_2026_04_20_k_are_summarized_in_section_6_the_originals_are_filed).",
        "source_record_line(src_line_0235, 235).",
        "source_record_text_atom(src_line_0235, with_the_foundation_secretary).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_text_atom(Line, Text)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(row.get("Kind") == "compact_identifier" and row.get("DisplayValue") == "BWCF-MG-2026-S" for row in result_rows)
    assert any(row.get("Kind") == "compact_identifier" and row.get("DisplayValue") == "SC-2026-04-22" for row in result_rows)
    assert any(row.get("Kind") == "compact_identifier" and row.get("DisplayValue") == "RC-2026-04-20-V" for row in result_rows)
    assert any(row.get("Kind") == "compact_identifier" and row.get("DisplayValue") == "AP-2026-0429-A" for row in result_rows)
    assert any(
        row.get("Kind") == "compact_identifier"
        and row.get("DisplayValue") == "AP-2026-0429-A"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    retired_candidate_kinds = {
        "appeal_award_funding_source",
        "appeal_pending_status",
        "appeal_review_date",
        "appeal_window_rule",
        "procedure_manual_scope",
        "recusal_procedure_rule",
    }
    assert not any(row.get("Kind") in retired_candidate_kinds for row in result_rows)
    assert any(
        row.get("Kind") == "unreproduced_reference"
        and row.get("Value") == "briarwood_foundation_by_laws"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "unreproduced_reference"
        and row.get("Value") == "reviewer_score_sheets"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "original_filing_location"
        and row.get("Value") == "recusal_memo_originals"
        and "foundation secretary" in row.get("DisplayValue", "")
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )


def test_roster_state_support_does_not_promote_local_packet_content_notes() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_text_atom(src_line_0158, sco_ch_3_chaperone_counting_rules_defines_who_counts_toward_the).",
        "source_record_line(src_line_0104, 104).",
        "source_record_text_atom(src_line_0104, capacity_24_students_departure_2026_05_01_06_30_from_cedar_hollow).",
        "source_record_line(src_line_0192, 192).",
        "source_record_text_atom(src_line_0192, a_diaz_is_the_parent_of_s_014_and_is_permitted_to_observe_group_b).",
        "source_record_line(src_line_0193, 193).",
        "source_record_text_atom(src_line_0193, events_on_saturday_afternoon_only_2026_05_02_13_00_17_00_a_diaz).",
        "source_record_line(src_line_0232, 232).",
        "source_record_section(src_line_0232, v_6_1_temporary_in_day_assignment).",
        "source_record_label(src_line_0232, sch_2026_05_02_a).",
        "source_record_text_atom(src_line_0232, sch_2026_05_02_a).",
        "temporary_event_assignment(s_007, bridge_engineering, 2026_05_02_11_00, 2026_05_02_12_30).",
        "source_record_text_atom(src_line_0249, return_leg_attendance_scans_will_be_appended_after_the_trip_and).",
        "source_record_line(src_line_0150, 150).",
        "source_record_text_atom(src_line_0150, m_okonkwo_210_n_park_206_medical_coverage_station_central_to_all).",
        "source_record_line(src_line_0262, 262).",
        "source_record_text_atom(src_line_0262, retained_in_the_audit_binder_location_activities_office_filing).",
        "source_record_line(src_line_0263, 263).",
        "source_record_text_atom(src_line_0263, cabinet_3_drawer_2_and_are_not_the_operational_document).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["policy_requirement(policy, requirement)."])

    support_kinds = {
        str(row.get("SupportKind", ""))
        for item in rows
        if item["result"].get("predicate") == "roster_state_support"
        for row in item["result"].get("rows", [])
    }
    assert not any("school_packet" in support_kind for support_kind in support_kinds)
    assert not {
        "adult_lodging_location",
        "device_clock_audit_status",
        "document_policy_title",
        "pending_document_item",
        "scheduled_transport_departure",
        "source_record_observer_permission_scope",
        "temporary_assignment_source_record",
    } & support_kinds
    assert "document_retention_location" in support_kinds
    assert "temporary_event_source_link" in support_kinds
    retention = next(
        row
        for item in rows
        if item["result"].get("predicate") == "roster_state_support"
        for row in item["result"].get("rows", [])
        if row.get("SupportKind") == "document_retention_location"
    )
    assert retention.get("Person") == "audit_binder"
    assert retention.get("Location") == "activities_office_filing_cabinet_3_drawer_2"
    assert "activities office filing cabinet 3, drawer 2" in retention.get("DisplayValue", "")

    assert not any(
        item["result"].get("predicate") == "source_record_packet_metadata_support"
        for item in rows
    )


def test_temporary_assignment_query_exposes_source_note_support() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_section(src_line_0232, v_6_1_temporary_in_day_assignment).",
        "source_record_label(src_line_0232, sch_2026_05_02_a).",
        "source_record_line(src_line_0232, 232).",
        "temporary_assignment(s_007, group_c, bridge_engineering, 2026_05_02_11_00_12_30).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["temporary_assignment(s_007, Group, Event, StartEnd)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "temporary_event_source_link"
        and row.get("Person") == "s_007"
        and row.get("Event") == "bridge_engineering"
        and row.get("Start") == "2026_05_02_11_00"
        and row.get("End") == "2026_05_02_12_30"
        and row.get("SourceNote") == "sch_2026_05_02_a"
        and "Section 6.1" in row.get("DisplayValue", "")
        for row in result_rows
    )


def test_attendance_scan_query_does_not_promote_local_departure_note() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "attendance_scan(scan_001, 2026_05_01_06_31, cedar_hollow_parking_bus_1, 18).",
        "source_record_line(src_line_0104, 104).",
        "source_record_text_atom(src_line_0104, capacity_24_students_departure_2026_05_01_06_30_from_cedar_hollow).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["attendance_scan(Scan, Timestamp, cedar_hollow_parking_bus_1, Count)."])

    assert not any(
        row.get("SupportKind") == "scheduled_transport_departure"
        for item in rows
        if item["result"].get("predicate") == "roster_state_support"
        for row in item["result"].get("rows", [])
    )


def test_source_record_packet_metadata_surfaces_generic_document_standing_rows() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_row(src_line_0002, anchored_line, 2, section_f_recorded_statements, reproduction_does_not_constitute_a_finding_of_fact).",
        "source_record_section(src_line_0002, section_f_recorded_statements).",
        "source_record_line(src_line_0002, 2).",
        "source_record_text_atom(src_line_0002, reproduction_does_not_constitute_a_finding_of_fact).",
        "source_record_row(src_line_0003, anchored_line, 3, section_f_recorded_statements, the_forensic_handwriting_analyst_s_report_and_the_court_s).",
        "source_record_section(src_line_0003, section_f_recorded_statements).",
        "source_record_line(src_line_0003, 3).",
        "source_record_text_atom(src_line_0003, the_forensic_handwriting_analyst_s_report_and_the_court_s).",
        "source_record_row(src_line_0004, continuation_line, 4, section_f_recorded_statements, ultimate_rulings_are_the_authoritative_sources_for_findings).",
        "source_record_section(src_line_0004, section_f_recorded_statements).",
        "source_record_line(src_line_0004, 4).",
        "source_record_text_atom(src_line_0004, ultimate_rulings_are_the_authoritative_sources_for_findings).",
        "source_record_row(src_line_0007, anchored_line, 7, section_g_compilation_notes, the_following_are_referenced_but_not_reproduced_in_this_register_the).",
        "source_record_section(src_line_0007, section_g_compilation_notes).",
        "source_record_line(src_line_0007, 7).",
        "source_record_text_atom(src_line_0007, the_following_are_referenced_but_not_reproduced_in_this_register_the).",
        "source_record_row(src_line_0008, continuation_line, 8, section_g_compilation_notes, decedent_s_last_will_and_testament_dated_2018_07_22).",
        "source_record_section(src_line_0008, section_g_compilation_notes).",
        "source_record_line(src_line_0008, 8).",
        "source_record_text_atom(src_line_0008, decedent_s_last_will_and_testament_dated_2018_07_22).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_text_atom(Line, Text)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "recorded_assertion_not_finding"
        and row.get("Value") == "recorded_assertion"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "authoritative_finding_sources"
        and row.get("Value") == "forensic_handwriting_report_and_court_rulings"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "unreproduced_reference"
        and row.get("Value") == "last_will_and_testament"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )


def test_source_record_packet_metadata_surfaces_generic_probate_register_rows() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_row(src_line_0129, anchored_line, 129, d_3_reeder_held_items, the_executor_has_not_yet_directed_delivery_taking_the_position_that_the).",
        "source_record_section(src_line_0129, d_3_reeder_held_items).",
        "source_record_line(src_line_0129, 129).",
        "source_record_text_atom(src_line_0129, the_executor_has_not_yet_directed_delivery_taking_the_position_that_the).",
        "source_record_row(src_line_0130, continuation_line, 130, d_3_reeder_held_items, codicil_dispute_d_1_must_be_resolved_first_reeder_declines_to).",
        "source_record_section(src_line_0130, d_3_reeder_held_items).",
        "source_record_line(src_line_0130, 130).",
        "source_record_text_atom(src_line_0130, codicil_dispute_d_1_must_be_resolved_first_reeder_declines_to).",
        "source_record_row(src_line_0228, labeled_line, 228, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02, nrm_ll_2020_02).",
        "source_record_section(src_line_0228, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02).",
        "source_record_line(src_line_0228, 228).",
        "source_record_text_atom(src_line_0228, nrm_ll_2020_02_each_name_the_estate_of_margaret_w_holloway_as).",
        "source_record_row(src_line_0229, continuation_line, 229, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02, lender_the_2024_amendment_to_the_second_agreement_requested_by_ms).",
        "source_record_section(src_line_0229, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02).",
        "source_record_line(src_line_0229, 229).",
        "source_record_text_atom(src_line_0229, lender_the_2024_amendment_to_the_second_agreement_requested_by_ms).",
        "source_record_row(src_line_0230, anchored_line, 230, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02, holloway_personally_on_2024_09_30_did_not_change_the_named_lender_it).",
        "source_record_section(src_line_0230, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02).",
        "source_record_line(src_line_0230, 230).",
        "source_record_text_atom(src_line_0230, holloway_personally_on_2024_09_30_did_not_change_the_named_lender_it).",
        "source_record_row(src_line_0231, continuation_line, 231, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02, extended_the_loan_period_to_2027_09_30).",
        "source_record_section(src_line_0231, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02).",
        "source_record_line(src_line_0231, 231).",
        "source_record_text_atom(src_line_0231, extended_the_loan_period_to_2027_09_30).",
        "source_record_row(src_line_0236, labeled_line, 236, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02, nrm_rr_2018_44).",
        "source_record_section(src_line_0236, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02).",
        "source_record_line(src_line_0236, 236).",
        "source_record_text_atom(src_line_0236, the_reading_room_access_policy_at_nrm_rr_2018_44_the_letter).",
        "source_record_row(src_line_0237, continuation_line, 237, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02, collection_is_as_you_know_set_by_museum_policy_and_is_not_subject).",
        "source_record_section(src_line_0237, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02).",
        "source_record_line(src_line_0237, 237).",
        "source_record_text_atom(src_line_0237, collection_is_as_you_know_set_by_museum_policy_and_is_not_subject).",
        "source_record_row(src_line_0238, continuation_line, 238, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02, to_change_by_the_lender).",
        "source_record_section(src_line_0238, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02).",
        "source_record_line(src_line_0238, 238).",
        "source_record_text_atom(src_line_0238, to_change_by_the_lender).",
        "source_record_row(src_line_0240, anchored_line, 240, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02, beatrice_caulfield_registrar).",
        "source_record_section(src_line_0240, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02).",
        "source_record_line(src_line_0240, 240).",
        "source_record_text_atom(src_line_0240, beatrice_caulfield_registrar).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["external_id(Item, nrm_ll_2020_02)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(row.get("Kind") == "role_holder" and row.get("DisplayValue") == "Beatrice Caulfield, Registrar" for row in result_rows)
    assert any(row.get("Kind") == "loan_amendment_effect" and row.get("Value") == "nrm_ll_2020_02" for row in result_rows)
    assert any(row.get("Kind") == "non_revocable_access_policy" and row.get("Value") == "nrm_rr_2018_44" for row in result_rows)
    assert any(row.get("Kind") == "no_delivery_direction" and row.get("Value") == "executor_reeder_items" for row in result_rows)


def test_source_record_packet_metadata_scopes_rows_by_query_surface() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_row(src_line_0100, anchored_line, 100, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02, collection_is_as_you_know_set_by_museum_policy_and_is_not_subject).",
        "source_record_section(src_line_0100, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02).",
        "source_record_line(src_line_0100, 100).",
        "source_record_text_atom(src_line_0100, collection_is_as_you_know_set_by_museum_policy_and_is_not_subject).",
        "source_record_row(src_line_0101, anchored_line, 101, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02, to_change_by_the_lender_beatrice_caulfield_registrar).",
        "source_record_section(src_line_0101, h_3_northpoint_regional_museum_b_caulfield_registrar_to_c_sutter_2026_04_02).",
        "source_record_line(src_line_0101, 101).",
        "source_record_text_atom(src_line_0101, to_change_by_the_lender_beatrice_caulfield_registrar).",
        "source_record_row(src_line_0102, anchored_line, 102, section_f_recorded_statements_and_their_standing, record_reproduction_does_not_constitute_a_finding_of_fact_specifically).",
        "source_record_section(src_line_0102, section_f_recorded_statements_and_their_standing).",
        "source_record_line(src_line_0102, 102).",
        "source_record_text_atom(src_line_0102, record_reproduction_does_not_constitute_a_finding_of_fact_specifically).",
        "source_record_row(src_line_0103, anchored_line, 103, section_f_recorded_statements_and_their_standing, the_private_gift_assertion_of_daniel_holloway_regarding_ex_003_is_recorded_but_has_not_been_ruled_upon).",
        "source_record_section(src_line_0103, section_f_recorded_statements_and_their_standing).",
        "source_record_line(src_line_0103, 103).",
        "source_record_text_atom(src_line_0103, the_private_gift_assertion_of_daniel_holloway_regarding_ex_003_is_recorded_but_has_not_been_ruled_upon).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["party_role(Person, registrar, museum)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert result_rows
    assert result_rows[0]["Kind"] == "role_holder"
    assert result_rows[0]["DisplayValue"] == "Beatrice Caulfield, Registrar"


def test_source_record_packet_metadata_surfaces_unruled_motion_status() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_row(src_line_0138, anchored_line, 138, section_e_court_orders_and_pending_motions, p_26_347_m_3_the_court_has_not_ruled_on_this_motion).",
        "source_record_section(src_line_0138, section_e_court_orders_and_pending_motions).",
        "source_record_line(src_line_0138, 138).",
        "source_record_text_atom(src_line_0138, p_26_347_m_3_the_court_has_not_ruled_on_this_motion).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["court_order(Orderid, Orderdate, Ordercontent)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "motion_status"
        and row.get("Value") == "p_26_347_m_3"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )


def test_source_record_packet_metadata_surfaces_asserted_event_dates() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_row(src_line_0249, table_row, 249, section_i_chronology_of_custody_affecting_events, v_2024_11_19_date_asserted_by_d_holloway_as_date_of_in_person_gift_of_ex_003).",
        "source_record_section(src_line_0249, section_i_chronology_of_custody_affecting_events).",
        "source_record_line(src_line_0249, 249).",
        "source_record_text_atom(src_line_0249, v_2024_11_19_date_asserted_by_d_holloway_as_date_of_in_person_gift_of_ex_003).",
        "source_record_numeric_token(src_line_0249, v_2024_11_19).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["contested_by(ex_003, Person, Basis)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "asserted_event_date"
        and row.get("Value") == "v_2024_11_19"
        and row.get("DisplayValue") == "2024-11-19 asserted event date."
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )


def test_source_record_field_text_atom_fallback_declines_unparseable_query() -> None:
    assert qa_module._source_record_field_text_atom_fallback_query("not a valid prolog query") is None


def test_item_description_detail_core_query_declines_unparseable_query() -> None:
    runtime = CorePrologRuntime(max_depth=200)

    assert (
        qa_module._item_description_detail_core_query(
            runtime,
            query="not a valid prolog query",
        )
        is None
    )


def test_item_description_detail_companion_derives_year_from_description_atom() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    assert runtime.assert_fact("item_description(ex_001, painting_three_apples_in_saucer_1987).").get("status") == "success"

    rows = run_query_plan(runtime, ["item_description(ex_001, Description)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "item_description_detail_support"
    )
    result_rows = companion["result"]["rows"]
    assert result_rows == [
        {
            "Item": "ex_001",
            "Description": "painting_three_apples_in_saucer_1987",
            "DisplayDescription": "Painting Three Apples in Saucer",
            "Year": "1987",
            "SourcePredicate": "item_description",
            "HelperClass": "clean-helper",
        }
    ]


def test_item_description_detail_companion_accepts_evidence_item_surface() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    assert runtime.assert_fact("evidence_item(ex_u_1, usb_thumb_drive_32_gb).").get("status") == "success"

    rows = run_query_plan(runtime, ["item_description(Item, Description)."])
    companion = next(
        item for item in rows if item["result"].get("predicate") == "item_description_detail_support"
    )

    assert companion["result"]["rows"] == [
        {
            "Item": "ex_u_1",
            "Description": "usb_thumb_drive_32_gb",
            "DisplayDescription": "Usb Thumb Drive 32 gb",
            "Year": "",
            "SourcePredicate": "evidence_item",
            "HelperClass": "clean-helper",
        }
    ]


def test_run_query_plan_derives_item_description_detail_without_helper_rows_when_disabled() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    assert runtime.assert_fact("item_description(ex_001, painting_three_apples_in_saucer_1987).").get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["item_description(ex_001, Description)."],
        helper_companions_enabled=False,
        include_legacy_native_helpers=False,
    )

    detail = next(item for item in rows if item["result"].get("predicate") == "item_description_detail_support")
    assert detail["result"]["reasoning_basis"]["kind"] == "core-local"
    assert detail["result"]["rows"] == [
        {
            "Item": "ex_001",
            "Description": "painting_three_apples_in_saucer_1987",
            "DisplayDescription": "Painting Three Apples in Saucer",
            "Year": "1987",
            "SourcePredicate": "item_description",
        }
    ]


def test_item_description_detail_accepts_item_id_surface_without_helper_rows() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    assert runtime.assert_fact("item_id(asset_17, catalog_entry_alpha_1994).").get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["item_id(asset_17, Title)."],
        helper_companions_enabled=False,
        include_legacy_native_helpers=False,
    )

    detail = next(item for item in rows if item["result"].get("predicate") == "item_description_detail_support")
    assert detail["result"]["reasoning_basis"]["kind"] == "core-local"
    assert detail["result"]["rows"] == [
        {
            "Item": "asset_17",
            "Description": "catalog_entry_alpha_1994",
            "DisplayDescription": "Catalog Entry Alpha",
            "Year": "1994",
            "SourcePredicate": "item_id",
        }
    ]


def test_source_record_table_body_count_companion_excludes_header_rows() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_row(src_line_0041, table_row, 41, section_b_item_inventory_and_custody_register, item_id).",
        "source_record_field(src_line_0041, item_id, item_id).",
        "source_record_field(src_line_0041, external_id, external_id).",
        "source_record_row(src_line_0043, table_row, 43, section_b_item_inventory_and_custody_register, ex_001).",
        "source_record_field(src_line_0043, item_id, ex_001).",
        "source_record_field(src_line_0043, external_id, nrm_ll_2019_08).",
        "source_record_row(src_line_0044, table_row, 44, section_b_item_inventory_and_custody_register, ex_002).",
        "source_record_field(src_line_0044, item_id, ex_002).",
        "source_record_field(src_line_0044, external_id, nrm_ll_2020_02).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["source_record_row(Row, table_row, Line, section_b_item_inventory_and_custody_register, Label)."],
    )

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_table_body_count_support"
    )
    result_rows = companion["result"]["rows"]
    assert result_rows == [
        {
            "SectionAtom": "section_b_item_inventory_and_custody_register",
            "RowType": "table_row",
            "BodyRowCount": 2,
            "Labels": "ex_001, ex_002",
            "HelperClass": "clean-helper",
        }
    ]


def test_source_record_table_count_hint_routes_explicit_table_count_questions() -> None:
    inventory = {"signatures": ["source_record_row/5", "source_record_field/3"]}

    assert _source_record_table_count_hint_queries(
        utterance="How many events are recorded in the raw event log?",
        kb_inventory=inventory,
    ) == ["source_record_row(SourceRow, table_row, Line, SectionAtom, Label)."]

    assert _source_record_table_count_hint_queries(
        utterance="How many applications were eligible?",
        kb_inventory=inventory,
    ) == []


def test_source_column_text_hint_routes_exact_source_column_questions() -> None:
    inventory = {"signatures": ["source_record_text_atom/2"]}

    assert _source_column_text_hint_queries(
        utterance="What source column is listed for the access row?",
        kb_inventory=inventory,
    ) == ["source_record_text_atom(SourceRow, TextAtom)."]

    assert _source_column_text_hint_queries(
        utterance="Which access row applies?",
        kb_inventory=inventory,
    ) == []


def test_location_floor_hint_routes_comparative_locker_questions() -> None:
    inventory = {"signatures": ["located_at/2", "locker_floor/2"]}

    assert _location_floor_hint_queries(
        utterance="Which two locker codes differ only by a leading zero, and what item is in each?",
        kb_inventory=inventory,
    ) == ["located_at(Item, Location).", "locker_floor(Location, Floor)."]

    assert _location_floor_hint_queries(
        utterance="Which item is stored in LK-3?",
        kb_inventory=inventory,
    ) == []


def test_authority_instrument_metadata_hint_routes_source_authority_questions() -> None:
    inventory = {"signatures": ["instrument_type/2", "instrument_issuer/2", "instrument_date/2"]}

    assert _authority_instrument_metadata_hint_queries(
        utterance="What source authorizes the release of PK-8?",
        kb_inventory=inventory,
    ) == [
        "instrument_type(Instrument, InstrumentType).",
        "instrument_issuer(Instrument, Issuer).",
        "instrument_date(Instrument, Date).",
    ]

    assert _authority_instrument_metadata_hint_queries(
        utterance="Which packages were cleared for transfer?",
        kb_inventory=inventory,
    ) == []


def test_counsel_opinion_hint_routes_eligibility_prong_questions() -> None:
    inventory = {"signatures": ["counsel_opinion/3", "source_record_text_atom/2"]}

    assert _counsel_opinion_hint_queries(
        utterance="Which percentage made the applicant eligible under the geographic prong?",
        kb_inventory=inventory,
    ) == [
        "counsel_opinion(Document, Subject, Conclusion).",
        "source_record_text_atom(SourceRow, TextAtom).",
    ]

    assert _counsel_opinion_hint_queries(
        utterance="Which counsel opinion explains the available award basis?",
        kb_inventory=inventory,
    ) == [
        "counsel_opinion(Document, Subject, Conclusion).",
        "source_record_text_atom(SourceRow, TextAtom).",
    ]


def test_vote_record_hint_routes_tally_and_motion_questions() -> None:
    inventory = {"signatures": ["vote_record/5", "motion_result/2"]}

    assert _vote_record_hint_queries(
        utterance="What was the vote tally on the exception motion?",
        kb_inventory=inventory,
    ) == [
        "vote_record(Motion, ForVotes, AgainstVotes, Denominator, ThresholdRequired).",
        "motion_result(Motion, Result).",
    ]

    assert _vote_record_hint_queries(
        utterance="Which source authorizes the release?",
        kb_inventory=inventory,
    ) == []


def test_award_cap_quantity_hint_routes_total_exceedance_questions() -> None:
    inventory = {"signatures": ["award_declaration/3", "budget_cap/2", "source_record_text_atom/2"]}

    assert _award_cap_quantity_hint_queries(
        utterance="By how much did the awarded grants exceed the original budget cap?",
        kb_inventory=inventory,
    ) == [
        "award_declaration(Subject, Amount, Basis).",
        "budget_cap(CapType, Amount).",
        "source_record_text_atom(SourceRow, TextAtom).",
    ]

    assert _award_cap_quantity_hint_queries(
        utterance="Which applicant received the grant?",
        kb_inventory=inventory,
    ) == []


def test_source_text_question_hints_prioritize_source_stated_unigrams() -> None:
    inventory = {"signatures": ["source_record_text_atom/2", "source_record_numeric_token/2"]}

    flag_hints = _source_text_question_token_hint_queries(
        utterance="Which applicant was initially flagged as ineligible by the Grants Administrator?",
        kb_inventory=inventory,
    )
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("initially", TextAtom).' in flag_hints
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("flagged", TextAtom).' in flag_hints
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("ineligible", TextAtom).' in flag_hints

    abstention_hints = _source_text_question_token_hint_queries(
        utterance="Which member abstained on the motion to award APP-S26-001, and on what basis?",
        kb_inventory=inventory,
    )
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("app_s26_001", TextAtom).' in abstention_hints
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("abstained", TextAtom).' in abstention_hints
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("basis", TextAtom).' in abstention_hints

    authority_hints = _source_text_question_token_hint_queries(
        utterance="What is the identifier of the board resolution authorizing the supplemental allocation?",
        kb_inventory=inventory,
    )
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("identifier", TextAtom).' in authority_hints
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("resolution", TextAtom).' in authority_hints
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("allocation", TextAtom).' in authority_hints

    sold_hints = _source_text_question_token_hint_queries(
        utterance="Where broadly were the recalled vehicles sold?",
        kb_inventory=inventory,
    )
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("sold", TextAtom).' in sold_hints

    phone_hints = _source_text_question_token_hint_queries(
        utterance="In which time zone are Polaris' phone hours given?",
        kb_inventory=inventory,
    )
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("phone", TextAtom).' in phone_hints
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("zone", TextAtom).' in phone_hints

    company_hints = _source_text_question_token_hint_queries(
        utterance="In what city and state is Polaris Industries Inc. located?",
        kb_inventory=inventory,
    )
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("polaris_industries_inc", TextAtom).' in company_hints

    state_abbrev_hints = _source_text_question_token_hint_queries(
        utterance="Which retail chain in Kentucky, New York, Ohio, Pennsylvania, and West Virginia carried the items?",
        kb_inventory=inventory,
    )
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("ky_ny_oh_pa_wv", TextAtom).' in state_abbrev_hints

    filing_hints = _source_text_question_token_hint_queries(
        utterance="What was the filing date stamped on the Federal Register document?",
        kb_inventory=inventory,
    )
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("filed", TextAtom).' in filing_hints

    final_rule_hints = _source_text_question_token_hint_queries(
        utterance="What is the document type — proposed rule, final rule, or notice?",
        kb_inventory=inventory,
    )
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("final", TextAtom).' in final_rule_hints

    timed_event_hints = _source_text_question_token_hint_queries(
        utterance="At what time did the guard arm release?",
        kb_inventory=inventory,
    )
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("released", TextAtom).' in timed_event_hints
    assert (
        'source_record_text_atom(SourceRow, TextAtom), memberchk("released", TextAtom), '
        "source_record_numeric_token(SourceRow, NumericToken)."
    ) in timed_event_hints

    quantity_hints = _source_text_question_token_hint_queries(
        utterance="How many devices total are active in batch v2?",
        kb_inventory=inventory,
    )
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("total_devices", TextAtom).' in quantity_hints


def test_source_section_question_key_hint_routes_sold_at_section_text() -> None:
    inventory = {
        "signatures": ["source_record_section/2", "source_record_text_atom/2"],
        "examples": {
            "source_record_section/2": [
                "source_record_section(src_line_0052, sold_at).",
                "source_record_section(src_line_0058, importer_s).",
            ]
        },
    }

    assert _source_section_question_key_hint_queries(
        utterance="Where broadly were the recalled vehicles sold?",
        kb_inventory=inventory,
    ) == ["source_record_section(SourceRow, sold_at), source_record_text_atom(SourceRow, TextAtom)."]


def test_source_record_compile_surface_hints_route_new_ledger_carriers() -> None:
    inventory = {
        "signatures": [
            "source_record_row_context/4",
            "source_record_citation/2",
            "source_record_date_alias/3",
            "source_record_count_word/3",
            "source_record_section_list_count_detail/5",
            "source_record_section_list_count_member/5",
        ]
    }

    assert "source_record_citation(SourceRow, Citation)." in _source_record_compile_surface_hint_queries(
        utterance="At what Federal Register citation was the proposed rule originally published?",
        kb_inventory=inventory,
    )
    assert "source_record_date_alias(SourceRow, CompactDate, CanonicalDate)." in _source_record_compile_surface_hint_queries(
        utterance="What was the filing date stamped on the Federal Register document?",
        kb_inventory=inventory,
    )
    count_hints = _source_record_compile_surface_hint_queries(
        utterance="How many distinct retail-packaged items sold at Walmart are listed in the announcement?",
        kb_inventory=inventory,
    )
    assert "source_record_section_list_count_detail(HeadingRow, ScopeRow, Category, ScopeText, Count)." in count_hints
    assert "source_record_section_list_count_member(HeadingRow, ScopeRow, Position, MemberRow, MemberText)." in count_hints

    vin_hints = _source_record_compile_surface_hint_queries(
        utterance="To verify if a vehicle is part of the recall, what should the consumer check?",
        kb_inventory={"signatures": ["source_record_text_atom/2", "source_record_row_context/4"]},
    )
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("vehicle_identification_number_vin", TextAtom).' in vin_hints

    free_hints = _source_record_compile_surface_hint_queries(
        utterance="Was the repair offered free of charge or for a fee?",
        kb_inventory={"signatures": ["source_record_text_atom/2", "source_record_row_context/4"]},
    )
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("free_repair", TextAtom).' in free_hints


def test_source_record_relative_next_day_companion_derives_event_date() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    runtime.assert_fact("source_record_text_atom(src_line_0040, on_march_14_2023_the_operator_started_the_device).")
    runtime.assert_fact(
        "source_record_text_atom(src_line_0066, "
        "on_march_18_at_1418_the_response_team_located_the_device_which_was_disabled_"
        "at_the_remote_site_the_device_broke_apart_at_the_site_the_next_day)."
    )

    companion = _source_record_relative_next_day_companion(
        runtime,
        utterance="On what date did the device break apart at the site?",
    )

    assert companion is not None
    result = companion["result"]
    assert result["predicate"] == "source_record_relative_next_day_event"
    assert result["rows"][0]["AnchorDate"] == "2023_03_18"
    assert result["rows"][0]["DerivedDate"] == "2023_03_19"
    assert result["rows"][0]["DerivedDateDisplay"] == "2023-03-19"


def test_source_record_packet_metadata_links_access_authority_to_court_order() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "access_authority(ex_004, lillian_park, p_26_347_d).",
        "court_order(p_26_347_d, v_2026_02_14, grants_observation_access).",
        "source_record_text_atom(src_line_0001, neutral_packet_anchor).",
        "source_record_section(src_line_0001, section_e_court_orders).",
        "source_record_line(src_line_0001, 1).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["access_authority(ex_004, lillian_park, SourceId)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "access_authority_order"
        and row.get("Value") == "p_26_347_d"
        and "2026-02-14" in row.get("DisplayValue", "")
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )


def test_source_record_pair_core_bridge_handles_state_abbreviation() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_cell_item_pair(src_line_0096, 1, west_virginia, 2, foodland).",
        "source_record_cell_item_pair_qualifier(src_line_0096, 1, west_virginia, 2, foodland, cucumbers_green_bell_peppers_and_pickling_cucumbers).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = _run_query_plan(
        runtime,
        ["source_record_cell_item_pair(row, stateindex, wv, retailerindex, foodland)."],
        helper_companions_enabled=False,
    )

    companion = next(
        item
        for item in rows
        if item["result"].get("predicate") == "source_record_cell_item_pair"
        and item["result"].get("reasoning_basis", {}).get("kind") == "core-local"
        and item["result"].get("rows")
    )
    assert any(
        "west_virginia" in row.get("source_query", "")
        and "foodland" in row.get("source_query", "")
        and row.get("Qualifier") == "cucumbers_green_bell_peppers_and_pickling_cucumbers"
        for row in companion["result"]["rows"]
    )


def test_source_record_packet_metadata_derives_reading_room_policy_from_access_fields() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_row(src_line_0078, table_row, 78, section_c_access_register, ex_009).",
        "source_record_section(src_line_0078, section_c_access_register).",
        "source_record_line(src_line_0078, 78).",
        "source_record_text_atom(src_line_0078, ex_009_executor_museum_reading_room_patrons_per_museum_policy_museum_policy_mrp_04_estate_authority).",
        "source_record_field(src_line_0078, item_id, ex_009).",
        "source_record_field(src_line_0078, authorized_parties_access, executor_museum_reading_room_patrons_per_museum_policy).",
        "source_record_field(src_line_0078, authorizing_source, museum_policy_mrp_04_estate_authority).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["access_type(ex_009, museum_reading_room_patrons, standing)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "non_revocable_access_policy"
        and row.get("Value") == "mrp_04"
        and "Reading-room patron access governed by museum policy" in row.get("DisplayValue", "")
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )


def test_source_record_packet_metadata_links_court_order_to_source_section() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_row(src_line_0147, table_row, 147, section_e_court_orders_affecting_this_register, p_26_347_d).",
        "source_record_section(src_line_0147, section_e_court_orders_affecting_this_register).",
        "source_record_line(src_line_0147, 147).",
        "source_record_text_atom(src_line_0147, p_26_347_d_2026_02_14_l_park_granted_observation_access).",
        "source_record_field(src_line_0147, order_id, p_26_347_d).",
        "source_record_field(src_line_0147, date, v_2026_02_14).",
        "court_order(p_26_347_d, v_2026_02_14, l_park_granted_observation_access).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["court_order(p_26_347_d, Date, Content)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "source_record_order_section"
        and row.get("Value") == "p_26_347_d"
        and row.get("DisplayValue") == "Section E"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )


def test_source_record_section_display_renders_roman_section_atoms() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_section(src_line_0242, section_i_chronology_of_custody_affecting_events).",
        "source_record_line(src_line_0242, 242).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_section(Row, section_i_chronology_of_custody_affecting_events)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_section_display"
    )
    assert any(
        row.get("SectionAtom") == "section_i_chronology_of_custody_affecting_events"
        and row.get("DisplaySection") == "Section I"
        for row in companion["result"]["rows"]
    )


def test_source_record_section_display_renders_letter_section_atoms() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_section(src_line_0160, section_f_recorded_statements_and_their_standing).",
        "source_record_line(src_line_0160, 160).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_section(Row, section_f_recorded_statements_and_their_standing)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_section_display"
    )
    assert any(
        row.get("SectionAtom") == "section_f_recorded_statements_and_their_standing"
        and row.get("DisplaySection") == "Section F"
        for row in companion["result"]["rows"]
    )


def test_grant_award_support_derives_counts_caps_recusals_and_appeal_status() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "application_eligibility(a_01, er_1, pass).",
        "application_eligibility(a_01, er_2, pass).",
        "application_eligibility(a_02, er_1, pass).",
        "application_eligibility(a_02, er_2, pass).",
        "application_eligibility(a_05, er_1, pass).",
        "application_eligibility(a_05, er_2, fail).",
        "requested_amount(a_02, 24000).",
        "bonus_eligibility(a_02, rural).",
        "final_award(a_01, 20000, awarded).",
        "final_award(a_02, 25000, awarded).",
        "final_award(a_07, 0, pending).",
        "source_record_field(src_line_0146, app_id, a_02).",
        "source_record_field(src_line_0146, pre_cap_amount, v_26_400).",
        "source_record_field(src_line_0146, capped, yes_25_000).",
        "source_record_field(src_line_0146, final_award, v_25_000).",
        "source_record_field(src_line_0020, parameter, number_of_applications).",
        "source_record_field(src_line_0020, value, v_7).",
        "source_record_field(src_line_0117, recusal_memo, rc_2026_04_20_v).",
        "source_record_field(src_line_0117, member, j_vasquez).",
        "source_record_field(src_line_0117, item, a_04).",
        "source_record_field(src_line_0117, reason, j_vasquez_serves_on_the_board_of_westside_arts_collective).",
        "source_record_line(src_line_0179, 179).",
        "source_record_text_atom(src_line_0179, v_2026_04_29_within_the_14_day_appeal_window_from_the_decision_letter).",
        "source_record_line(src_line_0189, 189).",
        "source_record_text_atom(src_line_0189, on_2026_05_22_as_of_the_compilation_date_ap_2026_0429_a_is).",
        "source_record_line(src_line_0190, 190).",
        "source_record_text_atom(src_line_0190, pending_a_07_has_neither_been_awarded_nor_finally_declined).",
        "source_record_line(src_line_0191, 191).",
        "source_record_text_atom(src_line_0191, if_the_a_12_appeal_is_sustained_the_appeal_award_would_be_drawn_against_fall_2026_carryover_not_spring_2026_awards).",
        "source_record_line(src_line_0126, 126).",
        "source_record_text_atom(src_line_0126, the_committee_has_7_voting_members_with_one_recusal_6_members_vote).",
        "source_record_line(src_line_0103, 103).",
        "source_record_section(src_line_0103, v_5_1_score_correction_memo_sc_2026_04_22).",
        "source_record_text_atom(src_line_0103, composite_from_7_4_to_8_4_a_02_s_revised_composite_is_above_the).",
        "source_record_line(src_line_0106, 106).",
        "source_record_section(src_line_0106, v_5_1_score_correction_memo_sc_2026_04_22).",
        "source_record_text_atom(src_line_0106, the_corrected_score_is_operational_as_of_2026_04_22_the_pre_correction).",
        "source_record_line(src_line_0107, 107).",
        "source_record_section(src_line_0107, v_5_1_score_correction_memo_sc_2026_04_22).",
        "source_record_text_atom(src_line_0107, composite_7_4_is_retained_in_the_audit_binder_but_is_not_used_for).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["application_eligibility(App, Rule, Result)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "grant_award_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "eligible_application_count"
        and row.get("Amount") == "2"
        and "a_05=er_2:fail" in row.get("Detail", "")
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "cap_applied_application_count"
        and row.get("Amount") == "1"
        and "a_02:$26,400->$25,000" in row.get("Detail", "")
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "final_award_total"
        and row.get("Amount") == "$45,000"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "recusal_record"
        and row.get("Status") == "RC-2026-04-20-V"
        and "J. Vasquez recused from a_04" in row.get("Detail", "")
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "appeal_pending_status"
        and row.get("App") == "a_07"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "appeal_review_date"
        and row.get("App") == "a_07"
        and row.get("Amount") == "2026-05-22"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "appeal_award_funding_source"
        and row.get("App") == "a_12"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "total_application_count"
        and row.get("Amount") == "7"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "committee_recusal_vote_count"
        and row.get("Amount") == "6"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "appeal_window_rule"
        and row.get("Amount") == "14 days"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "score_correction_operational"
        and row.get("App") == "a_02"
        and row.get("Amount") == "8.4"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )


def test_grant_award_support_adapts_older_rule_predicate_vocabulary() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "application_status(app_2026_014, approved).",
        "final_grant_amount(app_2026_014, 25000, 33750).",
        "bonus_qualification(app_2026_014, hospitality, 25).",
        "bonus_qualification(app_2026_014, underrepresented_owner, 15).",
        "determination_status(app_2026_019, pending).",
        "eligibility_determination(app_2026_019, 2_1, satisfied).",
        "eligibility_determination(app_2026_019, 2_5, pending).",
        "final_status(app_2026_027, approved).",
        "grant_calculation(app_2026_027, total, 33750, base_25_000_35_percent_cap_bonus).",
        "determination_status(app_2026_038, denied).",
        "grant_amount(app_2026_038, 0).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["application_status(App, Status)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "grant_award_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "final_award_row"
        and row.get("App") == "app_2026_014"
        and row.get("Amount") == "$33,750"
        and row.get("Status") == "awarded"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "final_award_row"
        and row.get("App") == "app_2026_027"
        and row.get("Amount") == "$33,750"
        and row.get("Status") == "awarded"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "eligible_application_count"
        and "app_2026_019=2_5:pending" in row.get("Detail", "")
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )


def test_roster_state_support_derives_operational_roster_from_source_record_ledger() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_section(src_line_0058, v_1_2_roster_v2_2026_04_09).",
        "source_record_line(src_line_0058, 58).",
        "source_record_text_atom(src_line_0058, group_c_physics_engineering_13).",
        "source_record_section(src_line_0059, v_1_2_roster_v2_2026_04_09).",
        "source_record_line(src_line_0059, 59).",
        "source_record_text_atom(src_line_0059, s_022_s_025).",
        "source_record_section(src_line_0074, v_1_4_roster_v3_2026_04_15).",
        "source_record_line(src_line_0074, 74).",
        "source_record_text_atom(src_line_0074, v_1_4_roster_v3_2026_04_15).",
        "source_record_section(src_line_0078, v_1_4_roster_v3_2026_04_15).",
        "source_record_line(src_line_0078, 78).",
        "source_record_text_atom(src_line_0078, s_022_is_correctly_assigned_to_group_b_only_the_group_c_listing).",
        "source_record_section(src_line_0088, v_1_4_roster_v3_2026_04_15).",
        "source_record_line(src_line_0088, 88).",
        "source_record_text_atom(src_line_0088, group_b_life_science_10).",
        "source_record_section(src_line_0089, v_1_4_roster_v3_2026_04_15).",
        "source_record_line(src_line_0089, 89).",
        "source_record_text_atom(src_line_0089, s_013_s_014_s_015_s_016_s_017_s_020_s_021_s_022_s_023_s_024).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["student_group_assignment(Student, v3, group_b)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "source_record_student_group_assignment"
        and row.get("Person") == "s_022"
        and row.get("Group") == "group_b"
        and row.get("Version") == "v3"
        and row.get("SourceRow") == "src_line_0089"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "group_count"
        and row.get("Group") == "group_b"
        and row.get("Version") == "v3"
        and row.get("Count") == "10"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )
    assert not any(
        row.get("SupportKind") == "source_record_student_group_assignment"
        and row.get("Person") == "s_022"
        and row.get("Group") == "group_c"
        and row.get("Version") == "v3"
        for row in result_rows
    )


def test_roster_state_support_handles_homeroom_table_and_semantic_rows() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "student_in_homeroom(stu_1019, 7_c, v1_3).",
        "source_record_section(src_line_0126, v_6_1_students_by_homeroom_v1_3).",
        "source_record_line(src_line_0126, 126).",
        "source_record_text_atom(src_line_0126, v_7_a_4_stu_1023_park_stu_1041_lin_stu_1058_cohen_stu_1077_bauer).",
        "roster_table_member(src_line_0126, v1_3, 7_a, stu_1023).",
        "roster_table_member(src_line_0126, v1_3, 7_a, stu_1041).",
        "roster_table_member_label(src_line_0126, v1_3, 7_a, stu_1023, stu_1023_park).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["student_in_homeroom(Student, Homeroom, Version)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "student_group_assignment"
        and row.get("Person") == "stu_1019"
        and row.get("Group") == "7_c"
        and row.get("Version") == "v1_3"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "roster_table_student_group_assignment"
        and row.get("Person") == "stu_1023"
        and row.get("PrintedMember") == "stu_1023_park"
        and row.get("Group") == "7_a"
        and row.get("Version") == "v1_3"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "source_record_student_group_assignment"
        and row.get("Person") == "stu_1023"
        and row.get("Group") == "7_a"
        and row.get("Version") == "v1_3"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )

    focused_rows = run_query_plan(runtime, ["student_in_homeroom(stu_1023, 7_a, v1_3)."])
    focused_companion = next(
        item for item in focused_rows if item["result"].get("predicate") == "roster_state_support"
    )
    first_row = focused_companion["result"]["rows"][0]
    assert first_row.get("SupportKind") == "roster_table_student_group_assignment"
    assert first_row.get("Person") == "stu_1023"
    assert first_row.get("Group") == "7_a"
    assert first_row.get("Version") == "v1_3"

    homeroom_rows = run_query_plan(runtime, ["homeroom_member(stu_1023, 7_a, v1_3)."])
    homeroom_companion = next(
        item for item in homeroom_rows if item["result"].get("predicate") == "roster_state_support"
    )
    homeroom_first = homeroom_companion["result"]["rows"][0]
    assert homeroom_first.get("SupportKind") == "roster_table_student_group_assignment"
    assert homeroom_first.get("Person") == "stu_1023"
    assert homeroom_first.get("Group") == "7_a"
    assert homeroom_first.get("Version") == "v1_3"

    printed_label_rows = run_query_plan(runtime, ["homeroom_member(stu_1023_park, 7_a, v1_3)."])
    printed_label_companion = next(
        item for item in printed_label_rows if item["result"].get("predicate") == "roster_state_support"
    )
    printed_label_first = printed_label_companion["result"]["rows"][0]
    assert printed_label_first.get("SupportKind") == "roster_table_student_group_assignment"
    assert printed_label_first.get("Person") == "stu_1023"
    assert printed_label_first.get("PrintedMember") == "stu_1023_park"

    latest_rows = run_query_plan(runtime, ["student_in_homeroom(stu_1023, homeroom, version)."])
    latest_companion = next(
        item for item in latest_rows if item["result"].get("predicate") == "roster_state_support"
    )
    assert latest_companion["result"]["rows"][0].get("Version") == "v1_3"


def test_roster_state_support_derives_adult_counts_and_compliance_log() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_section(src_line_0139, v_6_2_accompanying_adults_v1_3).",
        "source_record_text_atom(src_line_0139, trip_leader_mr_r_avery_yes).",
        "source_record_section(src_line_0140, v_6_2_accompanying_adults_v1_3).",
        "source_record_text_atom(src_line_0140, chaperone_ms_t_reyes_yes).",
        "source_record_section(src_line_0141, v_6_2_accompanying_adults_v1_3).",
        "source_record_text_atom(src_line_0141, chaperone_ms_l_cardenas_yes).",
        "source_record_section(src_line_0142, v_6_2_accompanying_adults_v1_3).",
        "source_record_text_atom(src_line_0142, chaperone_ms_p_garcia_yes).",
        "source_record_section(src_line_0143, v_6_2_accompanying_adults_v1_3).",
        "source_record_text_atom(src_line_0143, medical_ms_s_patel_rn_no_per_3_4).",
        "source_record_section(src_line_0162, v_7_3_2_compliance_log).",
        "source_record_text_atom(src_line_0162, v1_3_after_cn_03_2026_05_21_4_4_yes).",
        "source_record_section(src_line_0164, v_7_3_2_compliance_log).",
        "source_record_text_atom(src_line_0164, the_3_2_compliance_status_flipped_three_times_across_the_four_versions).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["adult_role(Adult, Role)."])
    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]

    assert any(
        row.get("SupportKind") == "ratio_counted_adults"
        and row.get("Version") == "v1_3"
        and row.get("Count") == "4"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "adult_manifest_total"
        and row.get("Version") == "v1_3"
        and row.get("Count") == "5"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "compliance_status"
        and row.get("Version") == "v1_3"
        and row.get("Count") == "4"
        and row.get("Required") == "4"
        and row.get("Compliant") == "true"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "compliance_flip_count"
        and row.get("Count") == "3"
        for row in result_rows
    )


def test_explicit_table_member_alias_support_maps_legacy_printed_labels() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "roster_table_member(src_line_0041, v1_0, 7_a, stu_1063).",
        "roster_table_member(src_line_0042, v1_0, 7_b, stu_1063).",
        "roster_table_member_label(src_line_0041, v1_0, 7_a, stu_1063, stu_1063_vinokur).",
        "roster_table_member_label(src_line_0042, v1_0, 7_b, stu_1063, stu_1063_vinokur).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["roster_table_member(Row, v1_0, Homeroom, stu_1063_vinokur)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "explicit_table_member_alias_support")
    result_rows = companion["result"]["rows"]

    assert {
        row.get("Group")
        for row in result_rows
        if row.get("SupportKind") == "roster_table_member_label"
        and row.get("Member") == "stu_1063"
        and row.get("PrintedMember") == "stu_1063_vinokur"
    } == {"7_a", "7_b"}


def test_explicit_table_member_alias_support_maps_generic_printed_labels() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "explicit_table_membership(src_line_0004, unspecified_version, pump_crew, emp_204).",
        "explicit_table_membership(src_line_0004, unspecified_version, pump_crew, emp_311).",
        "explicit_table_member_label(src_line_0004, unspecified_version, pump_crew, emp_204, emp_204_rivera).",
        "explicit_table_member_label(src_line_0004, unspecified_version, pump_crew, emp_311, emp_311_okafor).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["explicit_table_membership(Row, unspecified_version, Team, emp_204_rivera)."],
    )

    companion = next(item for item in rows if item["result"].get("predicate") == "explicit_table_member_alias_support")
    result_rows = companion["result"]["rows"]

    assert result_rows == [
        {
            "SupportKind": "explicit_table_member_label",
            "SourceRow": "src_line_0004",
            "Version": "unspecified_version",
            "Group": "pump_crew",
            "Member": "emp_204",
            "PrintedMember": "emp_204_rivera",
            "HelperClass": "clean-helper",
        }
    ]


def test_homeroom_member_alias_support_prioritizes_latest_printed_label_row() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "roster_table_member_label(src_line_0041, v1_0, 7_a, stu_1063, stu_1063_vinokur).",
        "roster_table_member_label(src_line_0042, v1_0, 7_b, stu_1063, stu_1063_vinokur).",
        "roster_table_member_label(src_line_0127, v1_3, 7_b, stu_1063, stu_1063_vinokur).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["homeroom_member(stu_1063_vinokur, Homeroom, Version)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "homeroom_member_alias_support"
    )
    first_row = companion["result"]["rows"][0]

    assert first_row.get("SupportKind") == "homeroom_member_printed_label"
    assert first_row.get("Student") == "stu_1063"
    assert first_row.get("PrintedMember") == "stu_1063_vinokur"
    assert first_row.get("Homeroom") == "7_b"
    assert first_row.get("Version") == "v1_3"
    assert first_row.get("HelperClass") == "clean-helper"


def test_explicit_table_count_support_distinguishes_legacy_entries_from_distinct_members() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "roster_table_member(src_line_0041, v1_0, 7_a, stu_1019).",
        "roster_table_member(src_line_0041, v1_0, 7_a, stu_1063).",
        "roster_table_member(src_line_0042, v1_0, 7_b, stu_1063).",
        "roster_table_member(src_line_0042, v1_0, 7_b, stu_1085).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["roster_table_member(Row, v1_0, Homeroom, Student)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "explicit_table_count_support")
    result_rows = companion["result"]["rows"]

    assert result_rows == [
        {
            "SupportKind": "explicit_table_distinct_member_count",
            "Version": "v1_0",
            "EntryCount": "4",
            "DistinctCount": "3",
            "DuplicateMembers": "stu_1063",
            "GroupCounts": "7_a:2,7_b:2",
            "HelperClass": "clean-helper",
        }
    ]


def test_fallback_queries_project_roster_compliance_ir() -> None:
    ir = {
        "entities": [
            {"surface": "roster v1.3", "normalized": "v1_3"},
            {"surface": "§3.2 ratio", "normalized": "3_2"},
            {"surface": "counting chaperones", "normalized": "qualifying_chaperone"},
        ],
        "assertions": [
            {
                "kind": "question",
                "subject": "e3",
                "relation_concept": "count",
                "object": "e1",
            }
        ],
    }

    queries = _fallback_queries_from_semantic_ir(
        ir,
        allowed_predicates={"adult_role", "role_counts_towards_ratio", "roster_version"},
    )

    assert queries == [
        "adult_role(Adult, Role).",
        "role_counts_towards_ratio(Role, Counts).",
        "roster_version(v1_3).",
    ]


def test_roster_state_support_joins_adult_roles_to_ratio_scope() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "adult_role(t_mendez, lead_chaperone).",
        "adult_role(j_phelps, chaperone).",
        "adult_role(n_park, medical_staff).",
        "role_counts_towards_ratio(lead_chaperone, true).",
        "role_counts_towards_ratio(chaperone, true).",
        "role_counts_towards_ratio(medical_staff, false).",
        "adult_role(v_lee, bus_1_driver).",
        "role_counts_towards_ratio(bus_1_driver, false).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["role_counts_towards_ratio(Role, true)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "ratio_counted_adults"
        and row.get("Count") == "2"
        and row.get("Members") == "j_phelps,t_mendez"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "adult_role"
        and row.get("Person") == "n_park"
        and row.get("CountsTowardRatio") == "false"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "ratio_excluded_adults"
        and row.get("Count") == "2"
        and row.get("Members") == "n_park,v_lee"
        for row in result_rows
    )


def test_query_strategy_mentions_official_identity_duty_rows() -> None:
    policy = "\n".join(POST_INGESTION_QA_QUERY_STRATEGY["arity_and_variable_policy"])

    assert "who-is or what-is identity questions about a named official" in policy
    assert "Name plus role is often only partial support" in policy
    assert "ruling_by/3" in policy


def test_person_role_query_adds_official_action_companions() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "person_role(osric_thane, fair_warden).",
        "ruling_by(osric_thane, moth_lantern, disqualified_from_judging).",
        "permission_granted(osric_thane, tobias_wren_repair_request).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["person_role(osric_thane, Role)."])
    queries = [str(row.get("query", "")) for row in rows]

    assert "ruling_by(osric_thane, Subject, Outcome)." in queries
    assert "permission_granted(osric_thane, Request)." in queries


def test_deadline_calculated_query_adds_deadline_family_companion() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "deadline_calculated(deadline_answer_resumed, answer, march_18_2026, 14_calendar_days, april_1_2026).",
        "deadline_calculated(reply_deadline, reply, october_28_2026, 14_calendar_days, november_11_2026).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["deadline_calculated(deadline_answer_resumed, Answer, X, Y, Z)."],
    )
    companion = [
        row
        for row in rows
        if row.get("query") == "deadline_calculated(Deadline, Type, StartDate, Duration, EndDate)."
    ]

    assert companion
    result_rows = companion[0]["result"]["rows"]
    assert any(row.get("Deadline") == "reply_deadline" and row.get("Type") == "reply" for row in result_rows)
    assert "deadline-family questions" in companion[0]["result"]["reasoning_basis"]["note"]


def test_conversion_effect_query_adds_balanced_classification_count_companion() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "unit_count(condominium, 24).",
        "unit_count(condominium, 18).",
        "unit_count(townhome, 36).",
        "unit_count(townhome, 42).",
        "conversion_effective_date(unit_c13, condominium, townhome).",
        "conversion_effective_date(unit_c14, condominium, townhome).",
        "conversion_effective_date(unit_c15, condominium, townhome).",
        "conversion_effective_date(unit_c16, condominium, townhome).",
        "conversion_effective_date(unit_c17, condominium, townhome).",
        "conversion_effective_date(unit_c18, condominium, townhome).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["conversion_effective_date(Unit, FromType, ToType)."])
    companion = [
        row
        for row in rows
        if row["result"].get("predicate") == "classification_conversion_effect_support"
    ]

    assert companion
    result_row = companion[0]["result"]["rows"][0]
    assert result_row["FromType"] == "condominium"
    assert result_row["ToType"] == "townhome"
    assert result_row["ConvertedCount"] == "6"
    assert result_row["FromTypeDelta"] == "-6"
    assert result_row["ToTypeDelta"] == "6"
    assert result_row["TotalCountEffect"] == "no_change"


def test_case_status_at_date_query_derives_interval_support_from_transition_anchors() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "case_status_at_date(case_2026_cv_1847, 2026_03_31, active_discovery).",
        "case_status_at_date(case_2026cv1847, 2026_09_15, active_dispositive).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["case_status_at_date(case_2026_cv_1847, 2026_08_10, Status)."],
    )
    companion = [
        row
        for row in rows
        if row.get("query")
        == "case_status_at_date_interval_support(QueryCase, RequestedDate, Status, EffectiveFrom, EffectiveUntil)."
    ]

    assert companion
    result_row = companion[0]["result"]["rows"][0]
    assert result_row["Status"] == "active_discovery"
    assert result_row["EffectiveFrom"] == "2026_03_31"
    assert result_row["EffectiveUntil"] == "2026_09_15"
    assert "interval support" in companion[0]["result"]["reasoning_basis"]["note"]


def test_generic_status_query_derives_interval_support_from_transition_anchors() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "lot_status(lot_5b, precautionary_hold, 2025_08_28).",
        "lot_status(lot_5b, suspect, 2025_09_10).",
        "lot_status(lot_5b, cleared, 2025_09_22).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["lot_status(lot_5b, Status, 2025_09_15)."],
    )
    companion = [
        row
        for row in rows
        if row.get("query") == "lot_status_interval_support(QueryEntity, RequestedDate, Status, EffectiveFrom, EffectiveUntil)."
    ]

    assert companion
    result_row = companion[0]["result"]["rows"][0]
    assert result_row["Status"] == "suspect"
    assert result_row["EffectiveFrom"] == "2025_09_10"
    assert result_row["EffectiveUntil"] == "2025_09_22"
    assert result_row["ObservedEntity"] == "lot_5b"


def test_generic_status_query_uses_admitted_status_change_as_interval_anchor() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "asset_status(asset_42, baseline_hold, 2026_02_01).",
        "status_change(asset_42, escalated_hold, reviewer_7, 2026_02_10).",
        "status_change(asset_42, released, reviewer_8, 2026_02_22).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["asset_status(asset_42, Status, 2026_02_15)."])

    companion = [
        row
        for row in rows
        if row.get("query") == "asset_status_interval_support(QueryEntity, RequestedDate, Status, EffectiveFrom, EffectiveUntil)."
    ]
    assert companion
    result_row = companion[0]["result"]["rows"][0]
    assert result_row["Status"] == "escalated_hold"
    assert result_row["EffectiveFrom"] == "2026_02_10"
    assert result_row["EffectiveUntil"] == "2026_02_22"
    assert result_row["SupportKind"] == "status_change_anchor"


def test_status_at_date_query_derives_interval_support_from_transition_anchors() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "lot_status_at_date(lot_5b, precautionary_hold, 2025_08_28).",
        "lot_status_at_date(lot_5b, suspect, 2025_09_10).",
        "lot_status_at_date(lot_5b, cleared, 2025_09_22).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["lot_status_at_date(lot_5b, Status, 2025_09_15)."],
    )
    companion = [
        row
        for row in rows
        if row.get("query")
        == "lot_status_at_date_interval_support(QueryEntity, RequestedDate, Status, EffectiveFrom, EffectiveUntil)."
    ]

    assert companion
    result_row = companion[0]["result"]["rows"][0]
    assert result_row["Status"] == "suspect"
    assert result_row["EffectiveFrom"] == "2025_09_10"
    assert result_row["EffectiveUntil"] == "2025_09_22"
    assert result_row["ObservedEntity"] == "lot_5b"


def test_status_on_date_query_derives_interval_support_from_transition_anchors() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "asset_status_on_date(asset_42, 2026_01_03, baseline_hold).",
        "asset_status_on_date(asset_42, 2026_01_10, escalated_hold).",
        "asset_status_on_date(asset_42, 2026_01_22, released).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["asset_status_on_date(asset_42, 2026_01_15, Status)."],
    )
    companion = [
        row
        for row in rows
        if row.get("query")
        == "asset_status_on_date_interval_support(QueryEntity, RequestedDate, Status, EffectiveFrom, EffectiveUntil)."
    ]

    assert companion
    result_row = companion[0]["result"]["rows"][0]
    assert result_row["Status"] == "escalated_hold"
    assert result_row["EffectiveFrom"] == "2026_01_10"
    assert result_row["EffectiveUntil"] == "2026_01_22"
    assert result_row["ObservedEntity"] == "asset_42"


def test_status_at_query_derives_interval_support_from_transition_anchors() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "asset_status_at(asset_9, 2025_08_28, held).",
        "asset_status_at(asset_9, 2025_09_10, under_review).",
        "asset_status_at(asset_9, 2025_09_22, released).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["asset_status_at(asset_9, 2025_09_15, Status)."],
    )
    companion = [
        row
        for row in rows
        if row.get("query")
        == "asset_status_at_interval_support(QueryEntity, RequestedDate, Status, EffectiveFrom, EffectiveUntil)."
    ]

    assert companion
    result_row = companion[0]["result"]["rows"][0]
    assert result_row["Status"] == "under_review"
    assert result_row["EffectiveFrom"] == "2025_09_10"
    assert result_row["EffectiveUntil"] == "2025_09_22"
    assert result_row["ObservedEntity"] == "asset_9"


def test_run_query_plan_exposes_scoped_population_state_from_related_subsets() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "batch_status(batch_alpha, released, 2026_01_01).",
        "population_subset(batch_alpha, batch_alpha_diverted).",
        "population_remainder(batch_alpha, batch_alpha_remaining).",
        "batch_status(batch_alpha_diverted, held, 2026_01_10).",
        "batch_status(batch_alpha_remaining, released, 2026_01_10).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["batch_status(batch_alpha, Status, 2026_01_12)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "scoped_population_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("RelatedEntity") == "batch_alpha_diverted"
        and row.get("Status") == "held"
        and row.get("EffectiveFrom") == "2026_01_10"
        and row.get("ScopeKind") == "population_subset"
        and row.get("SupportKind") == "scoped_status_at_requested_date"
        for row in result_rows
    )
    assert any(
        row.get("RelatedEntity") == "batch_alpha_remaining"
        and row.get("Status") == "released"
        and row.get("ScopeKind") == "population_remainder"
        for row in result_rows
    )


def test_run_query_plan_exposes_scoped_population_event_window_without_asserting_status() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "asset_status(crate_7, normal, 2026_03_01).",
        "entity_subset(crate_7, crate_7_diverted).",
        "transfer_window(crate_7_diverted, station_b, station_c, 2026_03_12, 2026_03_14).",
        "asset_status(crate_7_diverted, hold, 2026_03_15).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["asset_status(crate_7, Status, 2026_03_13)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "scoped_population_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("RelatedEntity") == "crate_7_diverted"
        and row.get("SupportKind") == "scoped_event_window"
        and row.get("EventPredicate") == "transfer_window"
        and row.get("EventStart") == "2026_03_12"
        and row.get("EventEnd") == "2026_03_14"
        and row.get("FutureStatus") == "hold"
        and row.get("Status") == ""
        for row in result_rows
    )


def test_scoped_population_state_requires_related_population_surface() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "asset_status(crate_7, normal, 2026_03_01).",
        "asset_status(crate_7_diverted, hold, 2026_03_15).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["asset_status(crate_7, Status, 2026_03_13)."])

    assert not any(item["result"].get("predicate") == "scoped_population_state_support" for item in rows)


def test_scoped_population_state_runs_with_companion_delivery_disabled() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "case_status(case_group, open, 2026_04_01).",
        "case_subset(case_group, case_group_remainder).",
        "case_status(case_group_remainder, stayed, 2026_04_05).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["case_status(case_group, Status, 2026_04_06)."],
        helper_companions_enabled=False,
        include_legacy_native_helpers=False,
    )

    assert any(item["result"].get("predicate") == "scoped_population_state_support" for item in rows)


def test_unary_distinct_count_supports_placeholder_count_queries() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "exhibit_id(exhibit_t_1).",
        "exhibit_id(exhibit_t1).",
        "exhibit_id(exhibit_k1).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["exhibit_id(exhibit)."],
        helper_companions_enabled=False,
        include_legacy_native_helpers=False,
    )

    companion = next(item for item in rows if item["result"].get("predicate") == "unary_distinct_count_support")
    result_row = companion["result"]["rows"][0]
    assert result_row["SourcePredicate"] == "exhibit_id"
    assert result_row["RawEntityCount"] == "3"
    assert result_row["DistinctEntityCount"] == "2"
    assert result_row["AliasGroups"].startswith("exhibitt1:")
    assert "exhibit_t1" in result_row["AliasGroups"]
    assert "exhibit_t_1" in result_row["AliasGroups"]


def test_unary_distinct_count_does_not_expand_specific_absent_entity() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "person_id(alice).",
        "person_id(ben).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["person_id(clara)."],
        helper_companions_enabled=False,
        include_legacy_native_helpers=False,
    )

    assert not any(item["result"].get("predicate") == "unary_distinct_count_support" for item in rows)


def test_duration_display_accepts_t_separator_datetime_atoms() -> None:
    assert qa_module._duration_between_atoms("2025_10_12t22_00", "2025_10_12t22_47") == "47 minutes"


def test_return_to_state_query_derives_support_from_intervening_state_end() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "state_start(unit_7, standby, 2026_09_14_06_10).",
        "state_start(unit_7, active, 2026_09_14_07_25).",
        "state_end(unit_7, active, 2026_09_14_11_55).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["state_start(unit_7, standby, ReturnTime)."])
    companion = [
        row
        for row in rows
        if row.get("query")
        == "return_to_state_transition_support(QueryEntity, ReturnedState, ReturnTime, InterveningState, SupportKind)."
    ]

    assert companion
    result_row = companion[0]["result"]["rows"][0]
    assert result_row["QueryEntity"] == "unit_7"
    assert result_row["ReturnedState"] == "standby"
    assert result_row["ReturnTime"] == "2026_09_14_11_55"
    assert result_row["InterveningState"] == "active"


def test_set_minus_query_derives_projected_difference_members() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "group_member(base_set, item_a).",
        "group_member(base_set, item_b).",
        "group_member(base_set, item_c).",
        "excluded_member(exclusion_set, item_b).",
        "set_minus(output_view, base_set, exclusion_set).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["set_minus(output_view, base_set, exclusion_set)."])
    support = [
        item
        for item in rows
        if item.get("result", {}).get("predicate") == "set_difference_support"
    ]

    assert support
    members = {row["Member"] for row in support[0]["result"]["rows"]}
    assert members == {"item_a", "item_c"}
    assert {row["SupportKind"] for row in support[0]["result"]["rows"]} == {"set_difference_member"}


def test_set_minus_query_derives_difference_after_resolving_exclusion_variable() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "group_member(base_set, item_a).",
        "group_member(base_set, item_b).",
        "group_member(base_set, item_c).",
        "excluded_member(exclusion_set, item_b).",
        "set_minus(output_view, base_set, exclusion_set).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["set_minus(output_view, base_set, ExclusionSet)."])
    support = [
        item
        for item in rows
        if item.get("result", {}).get("predicate") == "set_difference_support"
    ]

    assert support
    result_rows = support[0]["result"]["rows"]
    assert {row["ExclusionSet"] for row in result_rows} == {"exclusion_set"}
    assert {row["Member"] for row in result_rows} == {"item_a", "item_c"}

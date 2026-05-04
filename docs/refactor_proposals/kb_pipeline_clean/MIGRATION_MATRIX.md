# Migration Matrix

This matrix maps active symbols to proposed homes. The new names are general and
avoid fixture-specific legacy labels.

| Current symbol | Proposed home | Proposed name | Notes |
| --- | --- | --- | --- |
| `CorePrologRuntime` | `runtime.py` | `CorePrologRuntime` | Move exact deterministic runtime first; keep compatibility import. |
| `ParseOnlyRuntime` | `runtime.py` | `ParseOnlyRuntime` | Scenario/local fallback runtime. |
| `_normalize_clause` | `runtime.py` or `clause_codec.py` | `normalize_clause` | Shared structural clause utility. |
| `_split_top_level_args`, `_extract_calls_with_args` | `runtime.py` or `clause_codec.py` | `split_top_level_args`, `extract_calls` | Shared parser helpers. |
| `_apply_to_kb` | `apply_engine.py` | `LegacyScenarioApplyEngine.apply` | Preserve batch, corpus, registry, type, and temporal dual-write behavior. |
| `PrologMCPServer._apply_compiled_parse` | `apply_engine.py` | `MCPApplyEngine.apply_compiled_parse` | Preserve correction retracts, stored-logic conflicts, supports, and operation records. |
| `PreThinkSessionState` | `gate_session.py` | `PreThinkSessionConfig` | Session policy values. |
| `PrologMCPServer.pre_think` | `mcp_tools.py` + `gate_session.py` | `ProcessUtteranceService.pre_think` | Compiler projection plus pending gate registration. |
| `_check_prethink_gate` | `gate_session.py` | `PreThinkGate.check_tool_call` | Token, confirmation, clarification, and query loop checks. |
| `_consume_prethink_after_call` | `gate_session.py` | `PreThinkGate.consume_tool_result` | Keep mixed-turn authorization alive. |
| `record_clarification_answer` | `gate_session.py` | `PreThinkGate.record_clarification_answer` | Clears query gate after confirmation. |
| `process_utterance` | `mcp_tools.py` | `ProcessUtteranceService.process_utterance` | Orchestrates pre-think, clarify, parse, apply, trace. |
| `_compile_prethink_semantics` | `compiler_client.py` | `CompilerClient.compile_prethink` | Legacy compiler backend. |
| `_compile_prethink_semantics_with_semantic_ir` | `compiler_client.py` + `semantic_mapper.py` | `SemanticPreThinkProjector.compile_prethink` | Semantic IR projection boundary. |
| `_compile_apply_parse` | `compiler_client.py` | `CompilerClient.compile_parse` | Legacy parse compiler plus normalizer pipeline. |
| `_compile_apply_parse_with_semantic_ir` | `semantic_mapper.py` | `SemanticIRMapper.compile_parse` | Calls mapper, then profile guard. |
| `_build_classifier_prompt`, `_build_extractor_prompt`, `_build_repair_prompt` | `compiler_client.py` | `PromptBuilder` | Prompt construction only. |
| `_call_model_prompt`, `_post_json`, `_parse_model_json` | `compiler_client.py` | `ModelTransport`, `ModelJsonParser` | Transport and JSON parsing. |
| `_normalize_clarification_fields` | `parse_normalization.py` | `schema_field_normalizer` | Structural field coercion. |
| `_validate_parsed`, registry/type validators | `parse_normalization.py` | `parse_schema_validator` | Preserve exact validation errors during migration. |
| `_apply_directional_fact_guard` | `parse_normalization.py` | `relation_orientation_normalizer` | Structured clause orientation correction. |
| `_apply_retract_exclusion_guard` | `parse_normalization.py` | `retraction_target_normalizer.drop_protected_targets` | Preserve target filtering behavior. |
| `_apply_retract_edge_target_guard` | `parse_normalization.py` | `retraction_target_normalizer.normalize_edge_targets` | Arrow-edge target normalization. |
| `_apply_retract_comma_tuple_guard` | `parse_normalization.py` | `retraction_target_normalizer.normalize_tuple_command` | Comma target normalization. |
| `_apply_unsafe_retract_downgrade_guard` | `parse_normalization.py` | `retraction_target_normalizer.downgrade_unsafe_retract` | Non-mutating downgrade when no safe target exists. |
| `_apply_anonymous_fact_clarification_guard` | `parse_normalization.py` | `clarification_policy_normalizer.allow_ground_placeholders` | Keep grounded placeholder behavior. |
| `_apply_predicate_naming_clarification_guard` | `parse_normalization.py` | `clarification_policy_normalizer.predicate_naming_gate` | Clarify unsafe predicate naming gaps. |
| `_apply_speculative_clarification_downgrade_guard` | `parse_normalization.py` | `clarification_policy_normalizer.downgrade_speculative_turn` | Preserve non-mutating staging. |
| `_apply_speaker_prefixed_clarification_downgrade_guard` | `parse_normalization.py` | `clarification_policy_normalizer.downgrade_speaker_prefixed_comment` | Speaker-comment guard. |
| `_apply_concession_contrast_guard` | `parse_normalization.py` | `relation_orientation_normalizer.concession_contrast` | Structured contrast correction. |
| `_apply_location_move_guard` | `parse_normalization.py` | `event_sequence_normalizer.location_move` | Structured move/event sequence normalization. |
| `_apply_declared_predicate_hint_guard` | `parse_normalization.py` | `registry_schema_normalizer.declared_predicate_hint` | Declared predicate hinting. |
| `_rewrite_fact_subject_anchor`, `_apply_leading_subject_anchor_guard` | `parse_normalization.py` | `subject_anchor_normalizer` | Subject anchoring and predicate rewrite. |
| `_apply_type_direction_guard` | `parse_normalization.py` | `entity_type_normalizer.type_direction` | Type relation orientation. |
| `_apply_type_entity_alias_guard` | `parse_normalization.py` | `entity_type_normalizer.entity_alias` | Alias canonicalization. |
| `_apply_observed_someone_event_guard` | `parse_normalization.py` | `story_world_observation_normalizer.observed_actor_event` | General observation event shape. |
| `_apply_observed_asleep_event_guard` | `parse_normalization.py` | `story_world_observation_normalizer.observed_state_event` | General observed state. |
| `_apply_observed_in_bed_event_guard` | `parse_normalization.py` | `story_world_observation_normalizer.observed_location_event` | General observed location. |
| `_apply_observed_sat_possessive_chair_guard` | `parse_normalization.py` | `story_world_observation_normalizer.observed_possessive_object_event` | No fixture-specific name. |
| `_apply_three_bears_observation_guard` | `parse_normalization.py` | `story_world_observation_normalizer.observation_cluster` | Preserve behavior under general cluster name. |
| `_apply_group_returned_home_guard` | `parse_normalization.py` | `group_event_normalizer.returned_to_location` | Group event normalization. |
| `_apply_observed_possessive_broken_guard` | `parse_normalization.py` | `story_world_observation_normalizer.observed_possessive_state` | General broken/state observation. |
| `_apply_possessive_break_guard` | `parse_normalization.py` | `possessive_object_normalizer.break_event` | Structural possessive object event. |
| `_apply_possessive_bed_target_guard` | `parse_normalization.py` | `possessive_object_normalizer.location_target` | Structural target normalization. |
| `_apply_explicit_if_then_rule_guard` | `parse_normalization.py` | `explicit_rule_normalizer.if_then_rule` | Rule shape correction. |
| `_apply_query_open_variable_guard` | `parse_normalization.py` | `query_shape_normalizer.open_variable_query` | Query variable correction. |
| `_apply_explicit_ground_fact_confidence_guard` | `parse_normalization.py` | `clarification_policy_normalizer.ground_fact_confidence` | Commit low-risk ground facts. |
| `_apply_ops_supply_chain_guard` | `parse_normalization.py` | `domain_event_normalizer.supply_chain_event` | Domain structural rewrite; eventually profile-specific. |
| `_apply_retract_parent_correction_guard` | `parse_normalization.py` | `retraction_target_normalizer.parent_correction` | Parent correction target generation. |
| `_apply_declared_signature_coverage_guard` | `parse_normalization.py` | `registry_schema_normalizer.declared_signature_coverage` | Preserve coverage clarification. |
| `_apply_registry_fact_salvage_guard` | `parse_normalization.py` | `registry_schema_normalizer.salvage_allowed_fact_subset` | Keep registry subset behavior. |
| `_apply_assert_fact_shape_sync_guard` | `parse_normalization.py` | `schema_field_normalizer.sync_assert_fact_shape` | Keep logic/components sync. |
| `_rewrite_is_a_predicate_fact`, `_apply_predicate_name_sanity_guard` | `parse_normalization.py` | `registry_schema_normalizer.rewrite_phrase_predicates` | Registry-compatible unary facts. |
| `_rewrite_reserved_temporal_predicate_fact`, `_apply_temporal_predicate_namespace_guard` | `parse_normalization.py` | `temporal_namespace_normalizer` | Reserved temporal predicate policy. |
| `_rewrite_narrative_specific_fact`, `_apply_narrative_fact_normalization_guard` | `parse_normalization.py` | `narrative_fact_normalizer` | Registry-gated narrative facts. |
| `_apply_narrative_rule_normalization_guard` | `parse_normalization.py` | `narrative_rule_normalizer` | Registry-gated narrative rules. |
| `src.semantic_ir.semantic_ir_to_legacy_parse` | `semantic_mapper.py` | `SemanticIRMapper.to_legacy_parse` | Keep active mapper as authority. |
| `src.semantic_ir.semantic_ir_to_prethink_payload` | `semantic_mapper.py` | `SemanticIRMapper.to_prethink_payload` | Pre-think projection. |
| `src.semantic_ir.semantic_ir_admission_diagnostics` | `semantic_mapper.py` | `SemanticIRMapper.admission_diagnostics` | Diagnostic-only view. |
| `_runtime_constraint_check` | `apply_engine.py` | `ApplyConstraintChecker` | Registry/type constraints before deterministic execution. |
| progress memory helpers | `scenario_cli.py` or `progress_memory.py` | `ProgressMemoryStore` | Keep out of runtime and MCP surface. |
| `parse_args`, `main` in `kb_pipeline.py` | `scenario_cli.py` | `main` | Legacy runner only. |


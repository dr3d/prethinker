"""Structural parse normalizer registry proposal.

This file intentionally does not implement English interpretation. It records
the ordered homes for existing structural guards so they can be ported and
tested one category at a time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NormalizerSpec:
    phase: str
    new_name: str
    legacy_symbols: tuple[str, ...]
    operates_on: tuple[str, ...]
    trace_event: str


NORMALIZER_PIPELINE: tuple[NormalizerSpec, ...] = (
    NormalizerSpec(
        phase="schema",
        new_name="schema_field_normalizer",
        legacy_symbols=("_normalize_clarification_fields", "_apply_assert_fact_shape_sync_guard"),
        operates_on=("parse fields", "facts", "logic_string", "components"),
        trace_event="schema_field_normalized",
    ),
    NormalizerSpec(
        phase="relation",
        new_name="relation_orientation_normalizer",
        legacy_symbols=("_apply_directional_fact_guard", "_apply_concession_contrast_guard"),
        operates_on=("clauses", "predicate calls", "arguments"),
        trace_event="relation_orientation_normalized",
    ),
    NormalizerSpec(
        phase="retraction",
        new_name="retraction_target_normalizer",
        legacy_symbols=(
            "_apply_retract_exclusion_guard",
            "_apply_retract_edge_target_guard",
            "_apply_retract_comma_tuple_guard",
            "_apply_unsafe_retract_downgrade_guard",
            "_apply_retract_parent_correction_guard",
        ),
        operates_on=("intent", "retract clauses", "fact targets"),
        trace_event="retraction_target_normalized",
    ),
    NormalizerSpec(
        phase="clarification",
        new_name="clarification_policy_normalizer",
        legacy_symbols=(
            "_apply_anonymous_fact_clarification_guard",
            "_apply_predicate_naming_clarification_guard",
            "_apply_speculative_clarification_downgrade_guard",
            "_apply_speaker_prefixed_clarification_downgrade_guard",
            "_apply_explicit_ground_fact_confidence_guard",
        ),
        operates_on=("clarification fields", "ambiguities", "confidence"),
        trace_event="clarification_policy_normalized",
    ),
    NormalizerSpec(
        phase="subject_anchor",
        new_name="subject_anchor_normalizer",
        legacy_symbols=("_rewrite_fact_subject_anchor", "_apply_leading_subject_anchor_guard"),
        operates_on=("facts", "predicate calls", "arguments"),
        trace_event="subject_anchor_normalized",
    ),
    NormalizerSpec(
        phase="entity_type",
        new_name="entity_type_normalizer",
        legacy_symbols=("_apply_type_direction_guard", "_apply_type_entity_alias_guard"),
        operates_on=("type clauses", "entity aliases", "schema metadata"),
        trace_event="entity_type_normalized",
    ),
    NormalizerSpec(
        phase="nested_event_observation",
        new_name="nested_event_observation_normalizer",
        legacy_symbols=(
            "_apply_observed_someone_event_guard",
            "_apply_observed_asleep_event_guard",
            "_apply_observed_in_bed_event_guard",
            "_apply_observed_sat_possessive_chair_guard",
            "_apply_three_bears_observation_guard",
            "_apply_observed_possessive_broken_guard",
        ),
        operates_on=("nested event clauses", "possessive object terms"),
        trace_event="nested_event_observation_normalized",
    ),
    NormalizerSpec(
        phase="collective_actor_event",
        new_name="collective_actor_event_normalizer",
        legacy_symbols=("_apply_group_returned_home_guard",),
        operates_on=("event clauses", "entity groups"),
        trace_event="collective_actor_event_normalized",
    ),
    NormalizerSpec(
        phase="possessive_target",
        new_name="possessive_target_normalizer",
        legacy_symbols=("_apply_possessive_break_guard", "_apply_possessive_bed_target_guard"),
        operates_on=("possessive object terms", "facts"),
        trace_event="possessive_target_normalized",
    ),
    NormalizerSpec(
        phase="rule_query",
        new_name="explicit_rule_and_query_shape_normalizer",
        legacy_symbols=("_apply_explicit_if_then_rule_guard", "_apply_query_open_variable_guard"),
        operates_on=("rules", "queries", "variables"),
        trace_event="rule_query_shape_normalized",
    ),
    NormalizerSpec(
        phase="domain_event",
        new_name="domain_event_normalizer",
        legacy_symbols=("_apply_location_move_guard", "_apply_ops_supply_chain_guard"),
        operates_on=("profile-safe structured event clauses", "registry signatures"),
        trace_event="domain_event_normalized",
    ),
    NormalizerSpec(
        phase="registry",
        new_name="registry_schema_normalizer",
        legacy_symbols=(
            "_apply_declared_predicate_hint_guard",
            "_apply_declared_signature_coverage_guard",
            "_apply_registry_fact_salvage_guard",
            "_rewrite_is_a_predicate_fact",
            "_apply_predicate_name_sanity_guard",
        ),
        operates_on=("predicate registry", "declared signatures", "facts"),
        trace_event="registry_schema_normalized",
    ),
    NormalizerSpec(
        phase="temporal",
        new_name="temporal_namespace_normalizer",
        legacy_symbols=(
            "_rewrite_reserved_temporal_predicate_fact",
            "_apply_temporal_predicate_namespace_guard",
        ),
        operates_on=("temporal predicate signatures", "facts"),
        trace_event="temporal_namespace_normalized",
    ),
    NormalizerSpec(
        phase="domain_schema_shape",
        new_name="domain_schema_shape_normalizer",
        legacy_symbols=(
            "_rewrite_narrative_specific_fact",
            "_apply_narrative_fact_normalization_guard",
            "_apply_narrative_rule_normalization_guard",
        ),
        operates_on=("registry-gated facts", "registry-gated rules"),
        trace_event="domain_schema_shape_normalized",
    ),
)


def legacy_symbol_index() -> dict[str, NormalizerSpec]:
    index: dict[str, NormalizerSpec] = {}
    for spec in NORMALIZER_PIPELINE:
        for symbol in spec.legacy_symbols:
            index[symbol] = spec
    return index


def trace_plan() -> list[dict[str, Any]]:
    return [
        {
            "phase": spec.phase,
            "normalizer": spec.new_name,
            "trace_event": spec.trace_event,
            "legacy_symbols": list(spec.legacy_symbols),
            "operates_on": list(spec.operates_on),
        }
        for spec in NORMALIZER_PIPELINE
    ]


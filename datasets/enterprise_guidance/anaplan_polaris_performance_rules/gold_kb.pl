% Oracle-only reference KB for Anaplan Polaris performance guidance.
% Do not place this file in model context for cold runs.

source_document(anaplan_polaris_performance_rules).
document_type(anaplan_polaris_performance_rules, enterprise_technical_guidance).
guidance_domain(anaplan_polaris_performance_rules, anaplan_polaris).

performance_metric(calculation_effort).
performance_metric(memory).
performance_metric(populated_cell_count).
performance_metric(complexity).
performance_metric(gb).
performance_metric(model_open_time).
performance_metric(ux_rendering_speed).

module_type(output_module).
module_type(reporting_module).
module_type(input_module).

symptom(actions_running_slowly).
symptom(latent_model_open_time).
symptom(sluggish_cell_data_entry).
symptom(routine_health_check).

use_guide_when(actions_running_slowly).
use_guide_when(latent_model_open_time).
use_guide_when(sluggish_cell_data_entry).
use_guide_when(routine_health_check).

monitor_metric(calculation_effort).
monitor_metric(memory).
monitor_metric(populated_cell_count).
monitor_metric(integrations).
monitor_metric(long_running_processes).
monitor_metric(ux_rendering_speed).
monitor_metric(model_open_time).
monitor_metric(key_formulas).
monitor_metric(scheduled_data_flows).

review_window(calculation_effort, first_10_minutes_after_model_open).

action_when(performance_degrades, export_line_items_tab).
action_when(performance_degrades, identify_formulas_for_optimization).
action_when(performance_degrades, test_at_scale_in_fully_loaded_test_model).
action_when(performance_degrades, test_most_used_features).

optimization_priority(high_calc_effort_high_complexity_high_gb, 1).
optimization_priority(high_calc_effort_intensive_functions, 2).
optimization_priority(summary_methods_high_cell_count, 3).
optimization_priority(high_complexity_high_cell_count, 4).
optimization_priority(all_cells_high_cell_count, 5).

priority_reason(high_calc_effort_high_complexity_high_gb, largest_performance_improvement_opportunity).
priority_reason(high_complexity_high_cell_count, addressable_cell_count_and_complexity_can_create_risk).
priority_reason(all_cells_high_cell_count, all_cells_calculations_are_fully_dense).

computationally_intensive_function(finditem).
computationally_intensive_function(isfirstoccurrence).
computationally_intensive_function(rank).
computationally_intensive_function(rankcumulate).
computationally_intensive_function(cumulate).

summary_review_question(can_move_summary_to_end_of_calculation_chain).
summary_review_question(are_all_hierarchy_summary_levels_needed).
enables(end_of_calculation_chain, on_demand_calculation).

metric_semantics(gb, size_equivalent_of_populated_cells).
does_not_directly_determine(gb, performance).
validates_when_high(gb, high_complexity).
validates_when_high(gb, high_calculation_effort).

recommendation(use_alm_from_start).
recommendation(test_complex_modules_in_stages).
recommendation(use_guards_effectively).
recommendation(create_sys_calculate_boolean_master_switch).
recommendation(avoid_unnecessary_memory).
recommendation(centralize_and_reuse_filters).
recommendation(use_tabular_multiple_column_export).
recommendation(use_combined_grids_for_large_exports).
recommendation(use_delta_loads_for_intraday_reporting).
recommendation(seed_dev_lists_with_one_member).
recommendation(round_tiny_conditional_formatting_values).

guard_value(zero).
guard_value(false).
guard_value(blank).
guard_mechanism(if_then_statement).
guard_effect(introduces_new_information).
guard_effect(increases_sparsity).
guard_effect(only_performs_math_where_needed).

prefer_aggregation(sum).
higher_effort_aggregation(formula).
higher_effort_aggregation(ratio).
higher_effort_aggregation(any).
higher_effort_aggregation(all).
higher_effort_aggregation(first_non_blank).
higher_effort_aggregation(last_non_blank).

avoid_pattern(all_cells_formula_substantial_cell_count).
avoid_pattern(multiple_lookups_when_sum_possible).
avoid_pattern(user_based_filters_high_dimensionality).
avoid_pattern(full_clear_and_reload_intraday).
avoid_pattern(pivot_and_export_on_very_large_grid).

tradeoff(split_nested_if_formula, greater_parallelization, may_force_more_cells_to_calculate).
tradeoff(separate_models_by_business_process, shorter_calculation_chains, integration_complexity).
tradeoff(separate_models_by_business_process, fewer_unnecessary_recalculations, broken_real_time_views).
tradeoff(separate_models_by_business_process, separate_security_requirements, integration_complexity).

debugging_tactic(non_winding_cyclic_error, split_formula).
debugging_tactic(non_winding_cyclic_error, identify_circular_reference_piece).
debugging_tactic(non_winding_cyclic_error, use_staging_line_items).
debugging_tactic(dca_performance_issue, check_selective_access_replacement).
debugging_tactic(dca_performance_issue, remove_unneeded_dimensions).
debugging_tactic(dca_performance_issue, use_early_exit).
debugging_tactic(dca_performance_issue, avoid_text_operations).
debugging_tactic(dca_performance_issue, avoid_finditem).
debugging_tactic(dca_performance_issue, avoid_isfirstoccurrence_large_lists).

workspace_rule(max_polaris_models_per_workspace, 1).

export_rule(very_large_grids, do_not_allow_both_pivot_and_export).
export_reason(very_large_grids, default_pivot_all_levels_all_dimensions_can_lock_model).
preferred_export(combined_grids, efficient_compact_leaf_level_exports).
preferred_export(tabular_multiple_column_export, polaris_large_datasets).

intraday_update_rule(reporting_model, avoid_full_clear_and_reload).
intraday_update_rule(reporting_model, use_delta_loads_only).
delta_load_pattern(stage_upstream_input_model_data, intermediate_flat_model).
delta_load_pattern(use_dimension, current_previous).
incremental_filter(current_not_equal_previous).
recovery_path(full_unfiltered_load_option).

list_load_risk(adding_list_members, creates_large_numbers_of_cells).
list_load_risk(adding_list_members, requires_recalculation_during_loading).
reduce_list_load_impact(decouple_downstream_modules).
reduce_list_load_impact(run_action_less_frequently).
reduce_list_load_impact(create_dummy_members).

should_monitor(calculation_effort) :- building_in_polaris.
should_monitor(memory) :- building_in_polaris.
should_monitor(populated_cell_count) :- building_in_polaris.
should_test_in_stages(Module) :- complex_module(Module).
optimize_first(LineItem) :- high_calculation_effort(LineItem), high_complexity(LineItem), high_gb(LineItem).
review_intensive_function(LineItem) :- high_calculation_effort(LineItem), uses_function(LineItem, Function), computationally_intensive_function(Function).
review_summary_methods(LineItem) :- high_cell_count(LineItem), uses_summary_method(LineItem).
review_all_cells(LineItem) :- calculation_complexity(LineItem, all_cells), high_cell_count(LineItem).
avoid_formula(LineItem) :- formula_results_in(LineItem, all_cells), substantial_cell_count(LineItem).
prefer_sum_over_lookup(LineItem) :- uses_multiple_lookups(LineItem), sum_possible(LineItem).
investigate_memory(LineItem) :- populated_cell_count_much_higher_than_peers(LineItem).


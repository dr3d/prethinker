# Domain Bootstrap File Run

- Source file: `C:\prethinker\experiments\boundary_probes\compile_surface_stage1\answer_detail_surface_transfer\source.md`
- Backend/model: `lmstudio` / `qwen/qwen3.6-35b-a3b`
- Parsed: `True`
- Rough score: `0.944`
- Entity types: `5`
- Candidate predicates: `17`
- Generic predicates: `0`
- Repeated structures: `1`
- Repeated-structure unknown predicate refs: `[]`
- Repeated-structure id-only record refs: `[]`
- Repeated-structure role mismatch refs: `[]`
- Frontier unknown positive predicate refs: `[]`

## Intake Plan

- Parsed: `True`
- Source type: `procedural_status_report`
- Epistemic stance: `operational_fact_with_conditional_constraints`
- Passes: `3`

- `pass_1` Extract Probe A: Equipment Service Desk status and actions.: Ticket TK-480, Pump P-17, Technician Mara Velasquez, Warehouse, Gasket.
- `pass_2` Extract Probe B: Archive Imaging Queue constraints and schedule.: Request IMG-22, Folio F-113, Lab Room C, Omar Price, Imaging constraints.
- `pass_3` Extract Probe C: Garden Allocation conditions and deadlines.: Allocation GA-9, Bed 12, North Gate youth group, Watering schedule, Board.

## Profile Review

- Parsed: `True`
- Verdict: `retry_recommended`
- Coverage OK: `False`
- Missing capabilities: `4`

- Retry guidance: Add a predicate to link Assets to Records (e.g., `record_covers_asset/2`) to enable cross-referencing between the asset and its administrative record.
- Retry guidance: Add a predicate to link Facts to their Source Section/Probe (e.g., `recorded_in_probe/2`) to preserve the structural boundary of the source text.
- Retry guidance: Add a generic attribute capability (e.g., `asset_location/2` or `item_attribute/3`) to capture 'Bay 4', 'Lab Room C', and 'Bed 12' which are currently missing.
- Retry guidance: Ensure `action_outcome/2` or a similar predicate can be queried by record or asset, not just by action label, to maintain provenance.
- Retry guidance: Consider adding a `prohibited_action/2` or `negative_constraint/2` predicate to explicitly capture 'must not be placed' rather than relying on `handling_constraint`.

## Profile Review Retry

- Parsed: `True`
- Parse error: ``

## Candidate Predicates

- `record_covers_asset/2` args=['record_id', 'asset_id']: Links an administrative record to the specific asset it governs.
- `recorded_in_probe/2` args=['record_id', 'probe_id']: Preserves the structural boundary of the source text by linking a record to its originating probe/section.
- `asset_location/2` args=['asset_id', 'location']: Captures physical or logical location attributes of an asset.
- `action_outcome/2` args=['action_id', 'outcome_label']: Records the result of a completed action, including negative or insufficient outcomes.
- `prohibited_action/2` args=['asset_id', 'action']: Explicitly captures negative constraints or 'must not' actions.
- `ticket_status/2` args=['ticket_id', 'status']: Captures the current operational state of a service ticket.
- `blocking_reason/2` args=['ticket_id', 'reason']: Captures the specific reason an asset or ticket is blocked.
- `action_completed_by/3` args=['action_id', 'person_id', 'date']: Records who completed an action and when.
- `scheduled_date/2` args=['event_id', 'date']: Captures scheduled dates for events or updates.
- `allocation_status/2` args=['allocation_id', 'status']: Captures the current state of an allocation (e.g., conditional, active).
- `condition_for/2` args=['allocation_id', 'condition']: Specifies the requirement that must be met for an allocation to proceed or remain valid.
- `deadline_date/2` args=['condition_id', 'date']: Specifies the deadline for a condition to be met.
- `consequence_if/2` args=['condition_id', 'consequence']: Specifies the outcome if a condition is not met.
- `excluded_service/2` args=['request_id', 'service']: Captures services explicitly excluded from a request.
- `handling_constraint/2` args=['asset_id', 'constraint']: Captures physical or procedural constraints on handling an asset.
- `assigned_role/2` args=['person_id', 'role']: Links a person to their assigned role.
- `accepted_document/2` args=['organization_id', 'document_type']: Records that an organization has accepted a specific type of document.

## Repeated Structures

- `Operational Record with Status and Constraints` record=`record_covers_asset/2` properties=['ticket_status/2', 'blocking_reason/2', 'allocation_status/2', 'condition_for/2', 'deadline_date/2', 'consequence_if/2', 'excluded_service/2', 'handling_constraint/2', 'prohibited_action/2', 'scheduled_date/2', 'action_completed_by/3', 'action_outcome/2', 'asset_location/2', 'assigned_role/2', 'recorded_in_probe/2']: Each probe contains a record (Ticket, Request, Allocation) with a status, constraints, and temporal elements. This structure repeats across domains.
  - `record_covers_asset(tk_480, p_17).`
  - `record_covers_asset(img_22, f_113).`
  - `record_covers_asset(ga_9, bed_12).`

## Admission Risks

- Conflating 'blocked' status in Probe A with 'conditional' status in Probe C. Must use distinct predicates or context-aware predicates.
- Inferring that 'safety lockout review' implies the pump is safe. The source explicitly states it does not. Must capture the negative outcome.
- Missing the causal link between 'water-sensitive ink' and 'excluded chemical flattening'. Must preserve this reasoning.
- Treating the 'North Gate youth group' as a single person. It is a group entity. Must model it as such.
- Missing the deadline 2026-04-25 for the watering schedule. This is a critical temporal constraint.

## Source Compile

- OK: `True`
- Model decision: ``
- Projected decision: ``
- Admitted: `48`
- Skipped: `0`
- Lens health: `warning`
- Lens health recommendation: `run_qa_but_treat_thin_lens_results_as_diagnostic`
- Semantic progress risk: `low`
- Semantic progress action: `continue`

### Profile Admission

- Schema: `profile_admission_contracts_v1`
- Source signals: `{'operational_lifecycle': 4}`
- Candidate contracts: `{'operational_lifecycle_capable': 0}`
- Finding count: `1`
- `shallow_lifecycle_palette`: source_signals=4, candidates=17, nearby=['ticket_status/2', 'action_completed_by/3', 'allocation_status/2', 'assigned_role/2']

### Surface Contribution

| Pass | Unique | Duplicates | Facts | Rules | Queries | Health | Purpose |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `flat_skeleton` | 24 | 0 | 24 | 0 | 0 | ok | broad skeleton |
| `pass_1` | 6 | 4 | 10 | 0 | 0 | ok | Extract Probe A: Equipment Service Desk status and actions. |
| `pass_2` | 0 | 5 | 5 | 0 | 0 | no_unique_surface | Extract Probe B: Archive Imaging Queue constraints and schedule. |
| `pass_3` | 4 | 5 | 9 | 0 | 0 | ok | Extract Probe C: Garden Allocation conditions and deadlines. |

### Facts

```prolog
record_covers_asset(tk_480, p_17).
recorded_in_probe(tk_480, probe_a).
ticket_status(tk_480, blocked).
blocking_reason(tk_480, replacement_gasket_has_not_arrived).
asset_location(p_17, bay_4).
scheduled_date(tk_480, 2026_06_06).
action_completed_by(safety_lockout_review_p_17, mara_velasquez, 2026_06_03).
action_outcome(safety_lockout_review_p_17, insufficient_for_operation).
recorded_in_probe(img_22, probe_b).
record_covers_asset(img_22, f_113).
scheduled_date(img_22, 2026_07_14).
asset_location(f_113, lab_room_c).
excluded_service(img_22, chemical_flattening).
handling_constraint(f_113, separate_transport_required).
prohibited_action(f_113, placed_in_normal_courier_tray).
assigned_role(omar_price, imaging_lead).
recorded_in_probe(ga_9, probe_c).
record_covers_asset(ga_9, bed_12).
allocation_status(ga_9, conditional).
condition_for(ga_9, signed_watering_schedule).
deadline_date(ga_9, 2026_04_25).
consequence_if(ga_9, bed_12_returns_to_reserve_pool).
accepted_document(board, soil_test).
scheduled_date(board_accepted_soil_test, 2026_04_18).
blocking_reason(tk_480, gasket_not_arrived).
action_completed_by(safety_lockout_review, mara_velasquez, 2026_06_03).
record_covers_asset(safety_lockout_review, p_17).
action_outcome(safety_lockout_review, insufficient_for_operation).
scheduled_date(gasket_arrival_update, 2026_06_06).
assigned_role(mara_velasquez, technician).
deadline_date(signed_watering_schedule, 2026_04_25).
consequence_if(signed_watering_schedule, bed_returns_to_reserve).
scheduled_date(soil_test_acceptance, 2026_04_18).
action_outcome(soil_test_acceptance, does_not_waive_watering_schedule).
source_record_row(src_line_0001, heading, 1, boundary_probe_answer_detail_surface_transfer, boundary_probe_answer_detail_surface_transfer).
source_record_kind(src_line_0001, heading).
source_record_line(src_line_0001, 1).
source_record_label(src_line_0001, boundary_probe_answer_detail_surface_transfer).
source_record_section(src_line_0001, boundary_probe_answer_detail_surface_transfer).
source_record_text_atom(src_line_0001, boundary_probe_answer_detail_surface_transfer).
source_record_text_key(src_line_0001, text_7d6ec77d4d531e44).
source_record_row(src_line_0003, heading, 3, probe_a_equipment_service_desk, probe_a_equipment_service_desk).
source_record_kind(src_line_0003, heading).
source_record_line(src_line_0003, 3).
source_record_label(src_line_0003, probe_a_equipment_service_desk).
source_record_section(src_line_0003, probe_a_equipment_service_desk).
source_record_text_atom(src_line_0003, probe_a_equipment_service_desk).
source_record_text_key(src_line_0003, text_e2735a62d45e8fb6).
source_record_row(src_line_0005, labeled_line, 5, probe_a_equipment_service_desk, tk_480).
source_record_kind(src_line_0005, labeled_line).
source_record_line(src_line_0005, 5).
source_record_label(src_line_0005, tk_480).
source_record_section(src_line_0005, probe_a_equipment_service_desk).
source_record_text_atom(src_line_0005, service_ticket_tk_480_was_opened_on_2026_06_03_for_pump_p_17_at_bay_4_the).
source_record_text_key(src_line_0005, text_737ad84ddc152265).
source_record_numeric_token(src_line_0005, v_480).
source_record_numeric_token(src_line_0005, v_2026_06_03).
source_record_numeric_token(src_line_0005, v_17).
source_record_numeric_token(src_line_0005, v_4).
source_record_row(src_line_0006, continuation_line, 6, probe_a_equipment_service_desk, tk_480).
source_record_kind(src_line_0006, continuation_line).
source_record_line(src_line_0006, 6).
source_record_label(src_line_0006, tk_480).
source_record_section(src_line_0006, probe_a_equipment_service_desk).
source_record_text_atom(src_line_0006, ticket_status_is_blocked).
source_record_text_key(src_line_0006, text_0497eb7fb62784c1).
source_record_row(src_line_0008, paragraph_line, 8, probe_a_equipment_service_desk, the_blocking_reason_is_that_the_replacement_gasket_has_not_arrived).
source_record_kind(src_line_0008, paragraph_line).
source_record_line(src_line_0008, 8).
source_record_label(src_line_0008, the_blocking_reason_is_that_the_replacement_gasket_has_not_arrived).
source_record_section(src_line_0008, probe_a_equipment_service_desk).
source_record_text_atom(src_line_0008, the_blocking_reason_is_that_the_replacement_gasket_has_not_arrived_the).
source_record_text_key(src_line_0008, text_63378ca80c70f1b4).
source_record_row(src_line_0009, continuation_line, 9, probe_a_equipment_service_desk, the_blocking_reason_is_that_the_replacement_gasket_has_not_arrived).
source_record_kind(src_line_0009, continuation_line).
source_record_line(src_line_0009, 9).
source_record_label(src_line_0009, the_blocking_reason_is_that_the_replacement_gasket_has_not_arrived).
source_record_section(src_line_0009, probe_a_equipment_service_desk).
source_record_text_atom(src_line_0009, warehouse_acknowledged_the_back_order_and_promised_an_arrival_update_on).
source_record_text_key(src_line_0009, text_025b8792cc5ab98e).
source_record_row(src_line_0010, anchored_line, 10, probe_a_equipment_service_desk, v_2026_06_06).
source_record_kind(src_line_0010, anchored_line).
source_record_line(src_line_0010, 10).
source_record_label(src_line_0010, v_2026_06_06).
source_record_section(src_line_0010, probe_a_equipment_service_desk).
source_record_text_atom(src_line_0010, v_2026_06_06).
source_record_text_key(src_line_0010, text_50fa0fd033df5592).
source_record_numeric_token(src_line_0010, v_2026_06_06).
source_record_row(src_line_0012, labeled_line, 12, probe_a_equipment_service_desk, p_17).
source_record_kind(src_line_0012, labeled_line).
source_record_line(src_line_0012, 12).
source_record_label(src_line_0012, p_17).
source_record_section(src_line_0012, probe_a_equipment_service_desk).
source_record_text_atom(src_line_0012, technician_mara_velasquez_completed_the_safety_lockout_review_for_p_17_on).
source_record_text_key(src_line_0012, text_14bc6b5641c06302).
source_record_numeric_token(src_line_0012, v_17).
source_record_row(src_line_0013, anchored_line, 13, probe_a_equipment_service_desk, v_2026_06_03).
source_record_kind(src_line_0013, anchored_line).
source_record_line(src_line_0013, 13).
source_record_label(src_line_0013, v_2026_06_03).
source_record_section(src_line_0013, probe_a_equipment_service_desk).
source_record_text_atom(src_line_0013, v_2026_06_03_that_review_does_not_clear_the_pump_for_operation_because_the_gasket).
source_record_text_key(src_line_0013, text_3b88e66cba9350f4).
source_record_numeric_token(src_line_0013, v_2026_06_03).
source_record_row(src_line_0014, continuation_line, 14, probe_a_equipment_service_desk, v_2026_06_03).
source_record_kind(src_line_0014, continuation_line).
source_record_line(src_line_0014, 14).
source_record_label(src_line_0014, v_2026_06_03).
source_record_section(src_line_0014, probe_a_equipment_service_desk).
source_record_text_atom(src_line_0014, replacement_is_still_pending).
source_record_text_key(src_line_0014, text_93b3720bc0bf503b).
source_record_row(src_line_0016, heading, 16, probe_b_archive_imaging_queue, probe_b_archive_imaging_queue).
source_record_kind(src_line_0016, heading).
source_record_line(src_line_0016, 16).
source_record_label(src_line_0016, probe_b_archive_imaging_queue).
source_record_section(src_line_0016, probe_b_archive_imaging_queue).
source_record_text_atom(src_line_0016, probe_b_archive_imaging_queue).
source_record_text_key(src_line_0016, text_9094b896ad803a31).
source_record_row(src_line_0018, labeled_line, 18, probe_b_archive_imaging_queue, img_22).
source_record_kind(src_line_0018, labeled_line).
source_record_line(src_line_0018, 18).
source_record_label(src_line_0018, img_22).
source_record_section(src_line_0018, probe_b_archive_imaging_queue).
source_record_text_atom(src_line_0018, imaging_request_img_22_covers_folio_f_113_and_is_scheduled_for_2026_07_14_in).
source_record_text_key(src_line_0018, text_c13b6e8ccb17a2d6).
source_record_numeric_token(src_line_0018, v_22).
source_record_numeric_token(src_line_0018, v_113).
source_record_numeric_token(src_line_0018, v_2026_07_14).
source_record_row(src_line_0019, continuation_line, 19, probe_b_archive_imaging_queue, img_22).
source_record_kind(src_line_0019, continuation_line).
source_record_line(src_line_0019, 19).
source_record_label(src_line_0019, img_22).
source_record_section(src_line_0019, probe_b_archive_imaging_queue).
source_record_text_atom(src_line_0019, lab_room_c).
source_record_text_key(src_line_0019, text_da17f54f8c5f53da).
source_record_row(src_line_0021, paragraph_line, 21, probe_b_archive_imaging_queue, the_request_is_approved_for_imaging_only).
source_record_kind(src_line_0021, paragraph_line).
source_record_line(src_line_0021, 21).
source_record_label(src_line_0021, the_request_is_approved_for_imaging_only).
source_record_section(src_line_0021, probe_b_archive_imaging_queue).
source_record_text_atom(src_line_0021, the_request_is_approved_for_imaging_only_it_excludes_chemical_flattening).
source_record_text_key(src_line_0021, text_03892efe28bbcebd).
source_record_row(src_line_0022, continuation_line, 22, probe_b_archive_imaging_queue, the_request_is_approved_for_imaging_only).
source_record_kind(src_line_0022, continuation_line).
source_record_line(src_line_0022, 22).
source_record_label(src_line_0022, the_request_is_approved_for_imaging_only).
source_record_section(src_line_0022, probe_b_archive_imaging_queue).
source_record_text_atom(src_line_0022, because_the_conservation_note_says_the_ink_is_water_sensitive).
source_record_text_key(src_line_0022, text_128c902e5f0de04a).
source_record_row(src_line_0024, paragraph_line, 24, probe_b_archive_imaging_queue, the_folio_may_be_handled_by_imaging_lead_omar_price).
source_record_kind(src_line_0024, paragraph_line).
source_record_line(src_line_0024, 24).
source_record_label(src_line_0024, the_folio_may_be_handled_by_imaging_lead_omar_price).
source_record_section(src_line_0024, probe_b_archive_imaging_queue).
source_record_text_atom(src_line_0024, the_folio_may_be_handled_by_imaging_lead_omar_price_separate_transport_is).
source_record_text_key(src_line_0024, text_f73105d196d7fa72).
source_record_row(src_line_0025, continuation_line, 25, probe_b_archive_imaging_queue, the_folio_may_be_handled_by_imaging_lead_omar_price).
source_record_kind(src_line_0025, continuation_line).
source_record_line(src_line_0025, 25).
source_record_label(src_line_0025, the_folio_may_be_handled_by_imaging_lead_omar_price).
source_record_section(src_line_0025, probe_b_archive_imaging_queue).
source_record_text_atom(src_line_0025, required_the_folio_must_not_be_placed_in_the_normal_courier_tray).
source_record_text_key(src_line_0025, text_cd4251eb35ba4506).
source_record_row(src_line_0027, heading, 27, probe_c_community_garden_allocation, probe_c_community_garden_allocation).
source_record_kind(src_line_0027, heading).
source_record_line(src_line_0027, 27).
source_record_label(src_line_0027, probe_c_community_garden_allocation).
source_record_section(src_line_0027, probe_c_community_garden_allocation).
source_record_text_atom(src_line_0027, probe_c_community_garden_allocation).
source_record_text_key(src_line_0027, text_379caf9ce5432ed9).
source_record_row(src_line_0029, labeled_line, 29, probe_c_community_garden_allocation, ga_9).
source_record_kind(src_line_0029, labeled_line).
source_record_line(src_line_0029, 29).
source_record_label(src_line_0029, ga_9).
source_record_section(src_line_0029, probe_c_community_garden_allocation).
source_record_text_atom(src_line_0029, plot_allocation_ga_9_assigns_bed_12_to_the_north_gate_youth_group_for_the_summer).
source_record_text_key(src_line_0029, text_4efadf253be14f49).
source_record_numeric_token(src_line_0029, v_9).
source_record_numeric_token(src_line_0029, v_12).
source_record_row(src_line_0030, anchored_line, 30, probe_c_community_garden_allocation, cycle).
source_record_kind(src_line_0030, anchored_line).
source_record_line(src_line_0030, 30).
source_record_label(src_line_0030, cycle).
source_record_section(src_line_0030, probe_c_community_garden_allocation).
source_record_text_atom(src_line_0030, cycle_the_bed_count_is_one_raised_bed).
source_record_text_key(src_line_0030, text_1bf1d36aacca89cd).
source_record_row(src_line_0032, paragraph_line, 32, probe_c_community_garden_allocation, the_allocation_is_conditional_because_the_group_still_needs_to_submit_a_signed).
source_record_kind(src_line_0032, paragraph_line).
source_record_line(src_line_0032, 32).
source_record_label(src_line_0032, the_allocation_is_conditional_because_the_group_still_needs_to_submit_a_signed).
source_record_section(src_line_0032, probe_c_community_garden_allocation).
source_record_text_atom(src_line_0032, the_allocation_is_conditional_because_the_group_still_needs_to_submit_a_signed).
source_record_text_key(src_line_0032, text_de1cfaddf247ee4c).
source_record_row(src_line_0033, anchored_line, 33, probe_c_community_garden_allocation, watering_schedule).
source_record_kind(src_line_0033, anchored_line).
source_record_line(src_line_0033, 33).
source_record_label(src_line_0033, watering_schedule).
source_record_section(src_line_0033, probe_c_community_garden_allocation).
source_record_text_atom(src_line_0033, watering_schedule_the_board_accepted_the_soil_test_on_2026_04_18_but_that).
source_record_text_key(src_line_0033, text_1027d04a8a27ca3b).
source_record_numeric_token(src_line_0033, v_2026_04_18).
source_record_row(src_line_0034, continuation_line, 34, probe_c_community_garden_allocation, watering_schedule).
source_record_kind(src_line_0034, continuation_line).
source_record_line(src_line_0034, 34).
source_record_label(src_line_0034, watering_schedule).
source_record_section(src_line_0034, probe_c_community_garden_allocation).
source_record_text_atom(src_line_0034, acceptance_does_not_waive_the_watering_schedule).
source_record_text_key(src_line_0034, text_622d38a5deb8ef6d).
source_record_row(src_line_0036, anchored_line, 36, probe_c_community_garden_allocation, if_the_schedule_is_not_submitted_by_2026_04_25_bed_12_returns_to_the_reserve).
source_record_kind(src_line_0036, anchored_line).
source_record_line(src_line_0036, 36).
source_record_label(src_line_0036, if_the_schedule_is_not_submitted_by_2026_04_25_bed_12_returns_to_the_reserve).
source_record_section(src_line_0036, probe_c_community_garden_allocation).
source_record_text_atom(src_line_0036, if_the_schedule_is_not_submitted_by_2026_04_25_bed_12_returns_to_the_reserve).
source_record_text_key(src_line_0036, text_5020417897109af0).
source_record_numeric_token(src_line_0036, v_2026_04_25).
source_record_numeric_token(src_line_0036, v_12).
source_record_row(src_line_0037, continuation_line, 37, probe_c_community_garden_allocation, if_the_schedule_is_not_submitted_by_2026_04_25_bed_12_returns_to_the_reserve).
source_record_kind(src_line_0037, continuation_line).
source_record_line(src_line_0037, 37).
source_record_label(src_line_0037, if_the_schedule_is_not_submitted_by_2026_04_25_bed_12_returns_to_the_reserve).
source_record_section(src_line_0037, probe_c_community_garden_allocation).
source_record_text_atom(src_line_0037, pool).
source_record_text_key(src_line_0037, text_9822062ed7e36d60).
```

### Rules

```prolog
```

## Full Profile JSON

```json
{
  "admission_risks": [
    "Conflating 'blocked' status in Probe A with 'conditional' status in Probe C. Must use distinct predicates or context-aware predicates.",
    "Inferring that 'safety lockout review' implies the pump is safe. The source explicitly states it does not. Must capture the negative outcome.",
    "Missing the causal link between 'water-sensitive ink' and 'excluded chemical flattening'. Must preserve this reasoning.",
    "Treating the 'North Gate youth group' as a single person. It is a group entity. Must model it as such.",
    "Missing the deadline 2026-04-25 for the watering schedule. This is a critical temporal constraint."
  ],
  "candidate_predicates": [
    {
      "admission_notes": [
        "Directly stated in source (e.g., 'ticket TK-480... for pump P-17')."
      ],
      "args": [
        "record_id",
        "asset_id"
      ],
      "description": "Links an administrative record to the specific asset it governs.",
      "signature": "record_covers_asset/2",
      "why": "Required by profile review to enable cross-referencing between assets and their administrative records."
    },
    {
      "admission_notes": [
        "Source explicitly structures data into Probe A, B, and C."
      ],
      "args": [
        "record_id",
        "probe_id"
      ],
      "description": "Preserves the structural boundary of the source text by linking a record to its originating probe/section.",
      "signature": "recorded_in_probe/2",
      "why": "Required by profile review to preserve source-local provenance and prevent cross-domain predicate collision."
    },
    {
      "admission_notes": [
        "Source states 'pump P-17 at Bay 4', 'Lab Room C', 'Bed 12'."
      ],
      "args": [
        "asset_id",
        "location"
      ],
      "description": "Captures physical or logical location attributes of an asset.",
      "signature": "asset_location/2",
      "why": "Required by profile review to capture 'Bay 4', 'Lab Room C', 'Bed 12' which are currently missing."
    },
    {
      "admission_notes": [
        "Source states review 'does not clear the pump'. Outcome is 'insufficient_for_operation'."
      ],
      "args": [
        "action_id",
        "outcome_label"
      ],
      "description": "Records the result of a completed action, including negative or insufficient outcomes.",
      "signature": "action_outcome/2",
      "why": "Required by profile review to query outcomes by record/asset, not just action label. Captures 'does not clear' or 'insufficient' states."
    },
    {
      "admission_notes": [
        "Source states 'must not be placed in the normal courier tray'."
      ],
      "args": [
        "asset_id",
        "action"
      ],
      "description": "Explicitly captures negative constraints or 'must not' actions.",
      "signature": "prohibited_action/2",
      "why": "Required by profile review to explicitly capture 'must not be placed' rather than relying on generic handling constraints."
    },
    {
      "admission_notes": [
        "Source states 'ticket status is blocked'."
      ],
      "args": [
        "ticket_id",
        "status"
      ],
      "description": "Captures the current operational state of a service ticket.",
      "signature": "ticket_status/2",
      "why": "Core status tracking for Probe A."
    },
    {
      "admission_notes": [
        "Source states 'blocking reason is that the replacement gasket has not arrived'."
      ],
      "args": [
        "ticket_id",
        "reason"
      ],
      "description": "Captures the specific reason an asset or ticket is blocked.",
      "signature": "blocking_reason/2",
      "why": "Distinguishes 'blocked' status from other states; captures causal dependency."
    },
    {
      "admission_notes": [
        "Source states 'Technician Mara Velasquez completed... on 2026-06-03'."
      ],
      "args": [
        "action_id",
        "person_id",
        "date"
      ],
      "description": "Records who completed an action and when.",
      "signature": "action_completed_by/3",
      "why": "Captures completed actions and their actors."
    },
    {
      "admission_notes": [
        "Source states 'promised an arrival update on 2026-06-06', 'scheduled for 2026-07-14'."
      ],
      "args": [
        "event_id",
        "date"
      ],
      "description": "Captures scheduled dates for events or updates.",
      "signature": "scheduled_date/2",
      "why": "Temporal precision is critical for status determination."
    },
    {
      "admission_notes": [
        "Source states 'allocation is conditional'."
      ],
      "args": [
        "allocation_id",
        "status"
      ],
      "description": "Captures the current state of an allocation (e.g., conditional, active).",
      "signature": "allocation_status/2",
      "why": "Distinct from 'blocked'; captures 'conditional' state in Probe C."
    },
    {
      "admission_notes": [
        "Source states 'group still needs to submit a signed watering schedule'."
      ],
      "args": [
        "allocation_id",
        "condition"
      ],
      "description": "Specifies the requirement that must be met for an allocation to proceed or remain valid.",
      "signature": "condition_for/2",
      "why": "Models conditions as first-class logical constraints."
    },
    {
      "admission_notes": [
        "Source states 'If the schedule is not submitted by 2026-04-25'."
      ],
      "args": [
        "condition_id",
        "date"
      ],
      "description": "Specifies the deadline for a condition to be met.",
      "signature": "deadline_date/2",
      "why": "Critical temporal constraint for conditional allocations."
    },
    {
      "admission_notes": [
        "Source states 'Bed 12 returns to the reserve pool'."
      ],
      "args": [
        "condition_id",
        "consequence"
      ],
      "description": "Specifies the outcome if a condition is not met.",
      "signature": "consequence_if/2",
      "why": "Encodes if-then logic governing allocations."
    },
    {
      "admission_notes": [
        "Source states 'excludes chemical flattening'."
      ],
      "args": [
        "request_id",
        "service"
      ],
      "description": "Captures services explicitly excluded from a request.",
      "signature": "excluded_service/2",
      "why": "Captures 'excludes chemical flattening' in Probe B."
    },
    {
      "admission_notes": [
        "Source states 'Separate transport is required', 'ink is water-sensitive'."
      ],
      "args": [
        "asset_id",
        "constraint"
      ],
      "description": "Captures physical or procedural constraints on handling an asset.",
      "signature": "handling_constraint/2",
      "why": "Captures 'separate transport is required' and 'ink is water-sensitive'."
    },
    {
      "admission_notes": [
        "Source states 'Imaging Lead Omar Price', 'Technician Mara Velasquez'."
      ],
      "args": [
        "person_id",
        "role"
      ],
      "description": "Links a person to their assigned role.",
      "signature": "assigned_role/2",
      "why": "Maps roles explicitly as requested in entity strategy."
    },
    {
      "admission_notes": [
        "Source states 'board accepted the soil test'."
      ],
      "args": [
        "organization_id",
        "document_type"
      ],
      "description": "Records that an organization has accepted a specific type of document.",
      "signature": "accepted_document/2",
      "why": "Captures 'board accepted the soil test'."
    }
  ],
  "clarification_policy": [
    "When an operational record has repeated dated lifecycle/status lines, use the `record_covers_asset/2` plus specific status/constraint predicates to capture the joined subject/status/date unit.",
    "Do not merge entities across probes. P-17, F-113, and Bed 12 are unrelated assets in different systems.",
    "Model conditions as first-class logical constraints rather than narrative descriptions."
  ],
  "confidence": 0.85,
  "domain_guess": "operational_status_and_constraint_management",
  "domain_scope": "Cross-domain operational records (maintenance, archival, horticultural) featuring status tracking, conditional allocations, and explicit constraints.",
  "entity_types": [
    {
      "description": "Physical or digital objects under management (e.g., pumps, folios, beds).",
      "examples": [
        "P-17",
        "F-113",
        "Bed 12"
      ],
      "name": "Asset"
    },
    {
      "description": "Administrative or procedural documents/tickets associated with an asset or process.",
      "examples": [
        "TK-480",
        "IMG-22",
        "GA-9"
      ],
      "name": "Record"
    },
    {
      "description": "Individuals performing roles or actions.",
      "examples": [
        "Mara Velasquez",
        "Omar Price"
      ],
      "name": "Person"
    },
    {
      "description": "Organizational units or teams.",
      "examples": [
        "North Gate youth group",
        "Warehouse",
        "Board"
      ],
      "name": "Group"
    },
    {
      "description": "Functional positions held by persons or groups.",
      "examples": [
        "Technician",
        "Imaging Lead",
        "Beneficiary"
      ],
      "name": "Role"
    }
  ],
  "likely_functional_predicates": [
    "action_outcome/2",
    "consequence_if/2",
    "deadline_date/2"
  ],
  "provenance_sensitive_predicates": [
    "recorded_in_probe/2",
    "action_completed_by/3",
    "action_outcome/2"
  ],
  "repeated_structures": [
    {
      "admission_notes": [
        "This structure allows querying all properties of a specific operational record regardless of domain."
      ],
      "example_records": [
        "record_covers_asset(tk_480, p_17).",
        "record_covers_asset(img_22, f_113).",
        "record_covers_asset(ga_9, bed_12)."
      ],
      "id_strategy": "Use the source ID (TK-480, IMG-22, GA-9) as the primary key.",
      "name": "Operational Record with Status and Constraints",
      "property_predicates": [
        "ticket_status/2",
        "blocking_reason/2",
        "allocation_status/2",
        "condition_for/2",
        "deadline_date/2",
        "consequence_if/2",
        "excluded_service/2",
        "handling_constraint/2",
        "prohibited_action/2",
        "scheduled_date/2",
        "action_completed_by/3",
        "action_outcome/2",
        "asset_location/2",
        "assigned_role/2",
        "recorded_in_probe/2"
      ],
      "record_predicate": "record_covers_asset/2",
      "why": "Each probe contains a record (Ticket, Request, Allocation) with a status, constraints, and temporal elements. This structure repeats across domains."
    }
  ],
  "schema_version": "profile_bootstrap_v1",
  "self_check": {
    "notes": [
      "The profile proposes a compact set of predicates to handle status, constraints, and conditions across three distinct domains.",
      "Predicate families are designed to handle conditions, deadlines, and constraints explicitly.",
      "No Prolog or semantic_ir_v1 is emitted; this is a strategy document.",
      "The epistemic stance correctly identifies the source as procedural status reports with conditional logic.",
      "All predicates in repeated_structures are present in candidate_predicates."
    ],
    "profile_authority": "proposal_only"
  },
  "source_summary": [
    "Three distinct operational probes (Service Desk, Archive Imaging, Garden Allocation) containing status reports, conditional rules, and temporal deadlines.",
    "Each probe involves specific assets, personnel/roles, and administrative records with explicit blocking reasons or exclusion criteria.",
    "Key logical structures include conditional states (blocked, conditional), negative constraints (must not, excluded), and temporal deadlines."
  ],
  "starter_frontier_cases": [
    {
      "expected_boundary": "record_covers_asset(tk_480, p_17). asset_location(p_17, bay_4). ticket_status(tk_480, blocked). blocking_reason(tk_480, gasket_not_arrived).",
      "must_not_write": [
        "gasket_arrived(tk_480, true).",
        "pump_status(p_17, blocked)."
      ],
      "utterance": "Service ticket TK-480 was opened on 2026-06-03 for pump P-17 at Bay 4. The ticket status is blocked. The blocking reason is that the replacement gasket has not arrived."
    },
    {
      "expected_boundary": "action_completed_by(safety_lockout_review_p17, mara_velasquez, 2026-06-03). action_outcome(safety_lockout_review_p17, insufficient_for_operation).",
      "must_not_write": [
        "pump_safe(p_17, true).",
        "action_outcome(safety_lockout_review_p17, cleared)."
      ],
      "utterance": "Technician Mara Velasquez completed the safety lockout review for P-17 on 2026-06-03. That review does not clear the pump for operation because the gasket replacement is still pending."
    },
    {
      "expected_boundary": "record_covers_asset(img_22, f_113). scheduled_date(img_22, 2026-07-14). asset_location(f_113, lab_room_c). excluded_service(img_22, chemical_flattening). handling_constraint(f_113, ink_water_sensitive).",
      "must_not_write": [
        "imaging_completed(img_22, true).",
        "folio_status(f_113, flattened)."
      ],
      "utterance": "Imaging request IMG-22 covers folio F-113 and is scheduled for 2026-07-14 in Lab Room C. The request is approved for imaging only. It excludes chemical flattening because the conservation note says the ink is water-sensitive."
    },
    {
      "expected_boundary": "handling_constraint(f_113, separate_transport_required). prohibited_action(f_113, placed_in_normal_courier_tray).",
      "must_not_write": [
        "handling_constraint(f_113, normal_courier_tray)."
      ],
      "utterance": "Separate transport is required; the folio must not be placed in the normal courier tray."
    },
    {
      "expected_boundary": "record_covers_asset(ga_9, bed_12). allocation_status(ga_9, conditional). condition_for(ga_9, signed_watering_schedule). deadline_date(ga_9, 2026-04-25). consequence_if(ga_9, bed_returns_to_reserve). accepted_document(board, soil_test).",
      "must_not_write": [
        "allocation_status(ga_9, active).",
        "watering_schedule_submitted(ga_9, true)."
      ],
      "utterance": "Plot allocation GA-9 assigns Bed 12 to the North Gate youth group for the summer cycle. The bed count is one raised bed. The allocation is conditional because the group still needs to submit a signed watering schedule. The board accepted the soil test on 2026-04-18, but that acceptance does not waive the watering schedule. If the schedule is not submitted by 2026-04-25, Bed 12 returns to the reserve pool."
    }
  ],
  "unsafe_transformations": [
    "Do not infer gasket arrival; only record the promise.",
    "Do not infer imaging results.",
    "Do not infer that the North Gate youth group is fully active; it is conditional.",
    "Do not collapse 'blocked' and 'conditional' into a single status predicate without context."
  ]
}
```

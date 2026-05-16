# Domain Bootstrap QA Run

- Run JSON: `C:\prethinker\tmp\answer_detail_surface_transfer_compile_20260516\domain_bootstrap_file_20260516T214242209068Z_source_qwen-qwen3-6-35b-a3b.json`
- QA file: `C:\prethinker\experiments\boundary_probes\compile_surface_stage1\answer_detail_surface_transfer\qa.md`
- Model: `qwen/qwen3.6-35b-a3b`
- Source facts/rules: `224` / `0`
- Questions: `10`
- Parsed OK: `10`
- Rows with queries: `10`
- Rows with proposed writes: `0`
- Oracle rows/matches: `0` / `0`
- Reference judge: exact=`9` partial=`1` miss=`0`
- Failure surfaces: `{'not_applicable': 9, 'hybrid_join_gap': 1}`
- Helper classes: `{}` rows=`0`
- Cache: enabled=`False` hits=`0` misses=`10`

## Rows

### q001 - What status does ticket TK-480 have?

- Phase: `Answer Detail Surface Transfer QA`
- Decision: model=`answer` projected=`answer`
- Queries: `['ticket_status(tk_480, X).']`
- Proposed writes: facts=`0` rules=`0`
- Oracle match: `None`
- Reference answer: Ticket TK-480 has blocked status.
- Reference judge: `exact`
- Failure surface: `not_applicable`

```json
[
  {
    "query": "ticket_status(tk_480, X).",
    "result": {
      "status": "success",
      "result_type": "table",
      "predicate": "ticket_status",
      "prolog_query": "ticket_status(tk_480, X).",
      "variables": [
        "X"
      ],
      "rows": [
        {
          "X": "blocked",
          "BoundArg1": "tk_480",
          "BoundArg1Display": "tk 480"
        }
      ],
      "num_rows": 1,
      "reasoning_basis": {
        "kind": "core-local",
        "bound_query_constants_visible": true
      },
      "bound_query_constants": [
        {
          "arg_index": 1,
          "value": "tk_480",
          "display": "tk 480"
        }
      ]
    }
  }
]
```

### q002 - Why is TK-480 blocked?

- Phase: `Answer Detail Surface Transfer QA`
- Decision: model=`answer` projected=`answer`
- Queries: `['blocking_reason(tk_480, X).']`
- Proposed writes: facts=`0` rules=`0`
- Oracle match: `None`
- Reference answer: TK-480 is blocked because the replacement gasket has not arrived.
- Reference judge: `exact`
- Failure surface: `not_applicable`

```json
[
  {
    "query": "blocking_reason(tk_480, X).",
    "result": {
      "status": "success",
      "result_type": "table",
      "predicate": "blocking_reason",
      "prolog_query": "blocking_reason(tk_480, X).",
      "variables": [
        "X"
      ],
      "rows": [
        {
          "X": "replacement_gasket_has_not_arrived",
          "BoundArg1": "tk_480",
          "BoundArg1Display": "tk 480"
        },
        {
          "X": "gasket_not_arrived",
          "BoundArg1": "tk_480",
          "BoundArg1Display": "tk 480"
        }
      ],
      "num_rows": 2,
      "reasoning_basis": {
        "kind": "core-local",
        "bound_query_constants_visible": true
      },
      "bound_query_constants": [
        {
          "arg_index": 1,
          "value": "tk_480",
          "display": "tk 480"
        }
      ]
    }
  }
]
```

### q003 - What update did the warehouse promise, and on what date?

- Phase: `Answer Detail Surface Transfer QA`
- Decision: model=`answer` projected=`answer`
- Queries: `['scheduled_date(X, Y).']`
- Proposed writes: facts=`0` rules=`0`
- Oracle match: `None`
- Reference answer: The warehouse promised an arrival update on 2026-06-06.
- Reference judge: `exact`
- Failure surface: `not_applicable`

```json
[
  {
    "query": "scheduled_date(X, Y).",
    "result": {
      "status": "success",
      "result_type": "table",
      "predicate": "scheduled_date",
      "prolog_query": "scheduled_date(X, Y).",
      "variables": [
        "X",
        "Y"
      ],
      "rows": [
        {
          "X": "tk_480",
          "Y": "2026_06_06"
        },
        {
          "X": "img_22",
          "Y": "2026_07_14"
        },
        {
          "X": "board_accepted_soil_test",
          "Y": "2026_04_18"
        },
        {
          "X": "gasket_arrival_update",
          "Y": "2026_06_06"
        },
        {
          "X": "soil_test_acceptance",
          "Y": "2026_04_18"
        }
      ],
      "num_rows": 5,
      "reasoning_basis": {
        "kind": "core-local"
      }
    }
  }
]
```

### q004 - Does the safety lockout review clear P-17 for operation?

- Phase: `Answer Detail Surface Transfer QA`
- Decision: model=`answer` projected=`answer`
- Queries: `['record_covers_asset(safety_lockout_review, p_17).', 'action_outcome(safety_lockout_review, X).']`
- Proposed writes: facts=`0` rules=`0`
- Oracle match: `None`
- Reference answer: No. The safety lockout review does not clear P-17 for operation because the gasket replacement is still pending.
- Reference judge: `exact`
- Failure surface: `not_applicable`

```json
[
  {
    "query": "record_covers_asset(safety_lockout_review, p_17).",
    "result": {
      "status": "success",
      "result_type": "table",
      "predicate": "record_covers_asset",
      "prolog_query": "record_covers_asset(safety_lockout_review, p_17).",
      "variables": [],
      "rows": [
        {
          "BoundArg1": "safety_lockout_review",
          "BoundArg1Display": "safety lockout review",
          "BoundArg2": "p_17",
          "BoundArg2Display": "p 17"
        }
      ],
      "num_rows": 1,
      "reasoning_basis": {
        "kind": "core-local",
        "bound_query_constants_visible": true
      },
      "bound_query_constants": [
        {
          "arg_index": 1,
          "value": "safety_lockout_review",
          "display": "safety lockout review"
        },
        {
          "arg_index": 2,
          "value": "p_17",
          "display": "p 17"
        }
      ]
    }
  },
  {
    "query": "action_outcome(safety_lockout_review, X).",
    "result": {
      "status": "success",
      "result_type": "table",
      "predicate": "action_outcome",
      "prolog_query": "action_outcome(safety_lockout_review, X).",
      "variables": [
        "X"
      ],
      "rows": [
        {
          "X": "insufficient_for_operation",
          "BoundArg1": "safety_lockout_review",
          "BoundArg1Display": "safety lockout review"
        }
      ],
      "num_rows": 1,
      "reasoning_basis": {
        "kind": "core-local",
        "bound_query_constants_visible": true
      },
      "bound_query_constants": [
        {
          "arg_index": 1,
          "value": "safety_lockout_review",
          "display": "safety lockout review"
        }
      ]
    }
  }
]
```

### q005 - Where is IMG-22 scheduled?

- Phase: `Answer Detail Surface Transfer QA`
- Decision: model=`answer` projected=`answer`
- Queries: `['scheduled_date(img_22, X).']`
- Proposed writes: facts=`0` rules=`0`
- Oracle match: `None`
- Reference answer: IMG-22 is scheduled for 2026-07-14 in Lab Room C.
- Reference judge: `partial`
- Failure surface: `hybrid_join_gap`

```json
[
  {
    "query": "scheduled_date(img_22, X).",
    "result": {
      "status": "success",
      "result_type": "table",
      "predicate": "scheduled_date",
      "prolog_query": "scheduled_date(img_22, X).",
      "variables": [
        "X"
      ],
      "rows": [
        {
          "X": "2026_07_14",
          "BoundArg1": "img_22",
          "BoundArg1Display": "img 22"
        }
      ],
      "num_rows": 1,
      "reasoning_basis": {
        "kind": "core-local",
        "bound_query_constants_visible": true
      },
      "bound_query_constants": [
        {
          "arg_index": 1,
          "value": "img_22",
          "display": "img 22"
        }
      ]
    }
  }
]
```

### q006 - What does IMG-22 exclude, and why?

- Phase: `Answer Detail Surface Transfer QA`
- Decision: model=`answer` projected=`answer`
- Queries: `['excluded_service(img_22, X).', 'source_record_text_atom(X, Y).']`
- Proposed writes: facts=`0` rules=`0`
- Oracle match: `None`
- Reference answer: IMG-22 excludes chemical flattening because the conservation note says the ink is water-sensitive.
- Reference judge: `exact`
- Failure surface: `not_applicable`

```json
[
  {
    "query": "excluded_service(img_22, X).",
    "result": {
      "status": "success",
      "result_type": "table",
      "predicate": "excluded_service",
      "prolog_query": "excluded_service(img_22, X).",
      "variables": [
        "X"
      ],
      "rows": [
        {
          "X": "chemical_flattening",
          "BoundArg1": "img_22",
          "BoundArg1Display": "img 22"
        }
      ],
      "num_rows": 1,
      "reasoning_basis": {
        "kind": "core-local",
        "bound_query_constants_visible": true
      },
      "bound_query_constants": [
        {
          "arg_index": 1,
          "value": "img_22",
          "display": "img 22"
        }
      ]
    }
  },
  {
    "query": "source_record_text_atom(X, Y).",
    "result": {
      "status": "success",
      "result_type": "table",
      "predicate": "source_record_text_atom",
      "prolog_query": "source_record_text_atom(X, Y).",
      "variables": [
        "X",
        "Y"
      ],
      "rows": [
        {
          "X": "src_line_0001",
          "Y": "boundary_probe_answer_detail_surface_transfer"
        },
        {
          "X": "src_line_0003",
          "Y": "probe_a_equipment_service_desk"
        },
        {
          "X": "src_line_0005",
          "Y": "service_ticket_tk_480_was_opened_on_2026_06_03_for_pump_p_17_at_bay_4_the"
        },
        {
          "X": "src_line_0006",
          "Y": "ticket_status_is_blocked"
        },
        {
          "X": "src_line_0008",
          "Y": "the_blocking_reason_is_that_the_replacement_gasket_has_not_arrived_the"
        },
        {
          "X": "src_line_0009",
          "Y": "warehouse_acknowledged_the_back_order_and_promised_an_arrival_update_on"
        },
        {
          "X": "src_line_0010",
          "Y": "v_2026_06_06"
        },
        {
          "X": "src_line_0012",
          "Y": "technician_mara_velasquez_completed_the_safety_lockout_review_for_p_17_on"
        },
        {
          "X": "src_line_0013",
          "Y": "v_2026_06_03_that_review_does_not_clear_the_pump_for_operation_because_the_gasket"
        },
        {
          "X": "src_line_0014",
          "Y": "replacement_is_still_pending"
        },
        {
          "X": "src_line_0016",
          "Y": "probe_b_archive_imaging_queue"
        },
        {
          "X": "src_line_0018",
          "Y": "imaging_request_img_22_covers_folio_f_113_and_is_scheduled_for_2026_07_14_in"
        },
        {
          "X": "src_line_0019",
          "Y": "lab_room_c"
        },
        {
          "X": "src_line_0021",
          "Y": "the_request_is_approved_for_imaging_only_it_excludes_chemical_flattening"
        },
        {
          "X": "src_line_0022",
          "Y": "because_the_conservation_note_says_the_ink_is_water_sensitive"
        },
        {
          "X": "src_line_0024",
          "Y": "the_folio_may_be_handled_by_imaging_lead_omar_price_separate_transport_is"
        },
        {
          "X": "src_line_0025",
          "Y": "required_the_folio_must_not_be_placed_in_the_normal_courier_tray"
        },
        {
          "X": "src_line_0027",
          "Y": "probe_c_community_garden_allocation"
        },
        {
          "X": "src_line_0029",
          "Y": "plot_allocation_ga_9_assigns_bed_12_to_the_north_gate_youth_group_for_the_summer"
        },
        {
          "X": "src_line_0030",
          "Y": "cycle_the_bed_count_is_one_raised_bed"
        },
        {
          "X": "src_line_0032",
          "Y": "the_allocation_is_conditional_because_the_group_still_needs_to_submit_a_signed"
        },
        {
          "X": "src_line_0033",
          "Y": "watering_schedule_the_board_accepted_the_soil_test_on_2026_04_18_but_that"
        },
        {
          "X": "src_line_0034",
          "Y": "acceptance_does_not_waive_the_watering_schedule"
        },
        {
          "X": "src_line_0036",
          "Y": "if_the_schedule_is_not_submitted_by_2026_04_25_bed_12_returns_to_the_reserve"
        },
        {
          "X": "src_line_0037",
          "Y": "pool"
        }
      ],
      "num_rows": 25,
      "reasoning_basis": {
        "kind": "core-local"
      }
    }
  }
]
```

### q007 - What separate arrangement is required for folio F-113?

- Phase: `Answer Detail Surface Transfer QA`
- Decision: model=`answer` projected=`answer`
- Queries: `['handling_constraint(f_113, X).', 'prohibited_action(f_113, X).']`
- Proposed writes: facts=`0` rules=`0`
- Oracle match: `None`
- Reference answer: Separate transport is required for folio F-113; it must not be placed in the normal courier tray.
- Reference judge: `exact`
- Failure surface: `not_applicable`

```json
[
  {
    "query": "handling_constraint(f_113, X).",
    "result": {
      "status": "success",
      "result_type": "table",
      "predicate": "handling_constraint",
      "prolog_query": "handling_constraint(f_113, X).",
      "variables": [
        "X"
      ],
      "rows": [
        {
          "X": "separate_transport_required",
          "BoundArg1": "f_113",
          "BoundArg1Display": "f 113"
        }
      ],
      "num_rows": 1,
      "reasoning_basis": {
        "kind": "core-local",
        "bound_query_constants_visible": true
      },
      "bound_query_constants": [
        {
          "arg_index": 1,
          "value": "f_113",
          "display": "f 113"
        }
      ]
    }
  },
  {
    "query": "prohibited_action(f_113, X).",
    "result": {
      "status": "success",
      "result_type": "table",
      "predicate": "prohibited_action",
      "prolog_query": "prohibited_action(f_113, X).",
      "variables": [
        "X"
      ],
      "rows": [
        {
          "X": "placed_in_normal_courier_tray",
          "BoundArg1": "f_113",
          "BoundArg1Display": "f 113"
        }
      ],
      "num_rows": 1,
      "reasoning_basis": {
        "kind": "core-local",
        "bound_query_constants_visible": true
      },
      "bound_query_constants": [
        {
          "arg_index": 1,
          "value": "f_113",
          "display": "f 113"
        }
      ]
    }
  }
]
```

### q008 - How many beds does GA-9 assign?

- Phase: `Answer Detail Surface Transfer QA`
- Decision: model=`answer` projected=`answer`
- Queries: `['record_covers_asset(ga_9, X).']`
- Proposed writes: facts=`0` rules=`0`
- Oracle match: `None`
- Reference answer: GA-9 assigns one raised bed, Bed 12.
- Reference judge: `exact`
- Failure surface: `not_applicable`

```json
[
  {
    "query": "record_covers_asset(ga_9, X).",
    "result": {
      "status": "success",
      "result_type": "table",
      "predicate": "record_covers_asset",
      "prolog_query": "record_covers_asset(ga_9, X).",
      "variables": [
        "X"
      ],
      "rows": [
        {
          "X": "bed_12",
          "BoundArg1": "ga_9",
          "BoundArg1Display": "ga 9"
        }
      ],
      "num_rows": 1,
      "reasoning_basis": {
        "kind": "core-local",
        "bound_query_constants_visible": true
      },
      "bound_query_constants": [
        {
          "arg_index": 1,
          "value": "ga_9",
          "display": "ga 9"
        }
      ]
    }
  }
]
```

### q009 - What pending item makes GA-9 conditional?

- Phase: `Answer Detail Surface Transfer QA`
- Decision: model=`answer` projected=`answer`
- Queries: `['condition_for(ga_9, Item).']`
- Proposed writes: facts=`0` rules=`0`
- Oracle match: `None`
- Reference answer: GA-9 is conditional because the group still needs to submit a signed watering schedule.
- Reference judge: `exact`
- Failure surface: `not_applicable`

```json
[
  {
    "query": "condition_for(ga_9, Item).",
    "result": {
      "status": "success",
      "result_type": "table",
      "predicate": "condition_for",
      "prolog_query": "condition_for(ga_9, Item).",
      "variables": [
        "Item"
      ],
      "rows": [
        {
          "Item": "signed_watering_schedule",
          "BoundArg1": "ga_9",
          "BoundArg1Display": "ga 9"
        }
      ],
      "num_rows": 1,
      "reasoning_basis": {
        "kind": "core-local",
        "bound_query_constants_visible": true
      },
      "bound_query_constants": [
        {
          "arg_index": 1,
          "value": "ga_9",
          "display": "ga 9"
        }
      ]
    }
  }
]
```

### q010 - What happens if the watering schedule is not submitted by 2026-04-25?

- Phase: `Answer Detail Surface Transfer QA`
- Decision: model=`answer` projected=`answer`
- Queries: `['consequence_if(signed_watering_schedule, X).']`
- Proposed writes: facts=`0` rules=`0`
- Oracle match: `None`
- Reference answer: If the schedule is not submitted by 2026-04-25, Bed 12 returns to the reserve pool.
- Reference judge: `exact`
- Failure surface: `not_applicable`

```json
[
  {
    "query": "consequence_if(signed_watering_schedule, X).",
    "result": {
      "status": "success",
      "result_type": "table",
      "predicate": "consequence_if",
      "prolog_query": "consequence_if(signed_watering_schedule, X).",
      "variables": [
        "X"
      ],
      "rows": [
        {
          "X": "bed_returns_to_reserve",
          "BoundArg1": "signed_watering_schedule",
          "BoundArg1Display": "signed watering schedule"
        }
      ],
      "num_rows": 1,
      "reasoning_basis": {
        "kind": "core-local",
        "bound_query_constants_visible": true
      },
      "bound_query_constants": [
        {
          "arg_index": 1,
          "value": "signed_watering_schedule",
          "display": "signed watering schedule"
        }
      ]
    }
  }
]
```

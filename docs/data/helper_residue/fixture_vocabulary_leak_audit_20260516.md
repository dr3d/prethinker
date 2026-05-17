# Fixture Vocabulary Leak Audit

This audit separates live architecture vocabulary from legacy compatibility and historical strata.
A hit is not automatically a bug; the `status` and `replacement` columns define the current contract.

| Term | Status | Risk | Active code | Tests | Current docs | Worksheets | Replacement |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `explicit_table_membership` | `structural` | `low` | 17 | 7 | 2 | 3 | n/a |
| `explicit_table_member_label` | `structural` | `low` | 18 | 5 | 2 | 2 | n/a |
| `explicit_table_count_support` | `structural` | `low` | 4 | 2 | 0 | 0 | n/a |
| `roster_table_member` | `compatibility_alias` | `medium` | 27 | 37 | 0 | 7 | explicit_table_membership |
| `roster_table_member_label` | `compatibility_alias` | `medium` | 8 | 12 | 0 | 2 | explicit_table_member_label |
| `roster_table_count_support` | `compatibility_alias` | `medium` | 1 | 5 | 0 | 1 | explicit_table_count_support |
| `roster_table_student_group_assignment` | `compatibility_alias` | `high` | 5 | 4 | 0 | 1 | explicit_table_group_assignment |
| `source_record_student_group_assignment` | `quarantined_candidate_helper` | `high` | 6 | 8 | 0 | 1 | direct group_assignment/group_membership/explicit_table_membership compile surfaces |
| `student_group_assignment` | `compatibility_predicate` | `high` | 24 | 28 | 0 | 9 | group_assignment(Person, Version, Group) or group_membership(Person, Group, Start, End) |
| `student_in_homeroom` | `compatibility_predicate` | `high` | 8 | 12 | 0 | 3 | explicit_table_membership or group_assignment |
| `homeroom_member` | `compatibility_predicate` | `high` | 15 | 7 | 0 | 2 | explicit_table_membership or group_assignment |
| `adult_role` | `compatibility_predicate` | `medium` | 28 | 25 | 0 | 8 | person_role(Person, Role) or role_assignment(Person, Role, Scope) |
| `source_record_adult_role` | `quarantined_candidate_helper` | `high` | 2 | 0 | 0 | 1 | direct person_role/role_assignment compile surfaces |
| `staff_statement` | `compatibility_predicate` | `medium` | 11 | 3 | 0 | 6 | recorded_statement(StatementId, Speaker, Content) |
| `industrial_sensor_support` | `legacy_native_helper_adapter` | `high` | 4 | 4 | 0 | 4 | direct device/instrument, measurement, timestamp, correction-rule, and status compile surfaces |
| `_industrial_sensor_companion` | `legacy_native_helper_adapter` | `high` | 5 | 3 | 0 | 0 | direct device/instrument, measurement, timestamp, correction-rule, and status compile surfaces |
| `sensor_id` | `domain_predicate_under_transfer` | `medium` | 9 | 2 | 0 | 1 | item_identifier/device_identifier/instrument_identifier surfaces when the profile is not sensor-specific |
| `sensor_calibration_date` | `domain_predicate_under_transfer` | `medium` | 0 | 0 | 0 | 0 | calibration_event/device_status_date with governed device and source anchor |
| `sensor_certified_scope` | `domain_predicate_under_transfer` | `medium` | 1 | 0 | 0 | 0 | certification_scope(Device, Scope) or authority/status scoped to a governed device |
| `sensor_next_calibration_due` | `domain_predicate_under_transfer` | `medium` | 0 | 0 | 0 | 0 | scheduled_event/device_due_date with event type and governed device |
| `sensor_not_certified_for` | `domain_predicate_under_transfer` | `medium` | 1 | 0 | 0 | 0 | negative_certification_scope(Device, Scope, Source) or exclusion/status surface |
| `roster_state_support` | `legacy_native_helper_adapter` | `high` | 10 | 57 | 1 | 6 | direct compile surfaces plus explicit_table_* ledger facts |
| `trip_leader_` | `quarantined_parser_marker` | `high` | 1 | 1 | 0 | 0 | direct person_role/role_assignment compile surfaces |
| `chaperone_` | `quarantined_parser_marker` | `high` | 2 | 14 | 0 | 5 | direct person_role/role_assignment compile surfaces |
| `medical_` | `quarantined_parser_marker` | `medium` | 75 | 54 | 1 | 0 | direct person_role/role_assignment compile surfaces |

## High-Risk Active Hits

### `roster_table_student_group_assignment`

School-shaped support kind. Keep only when reading old roster_table_member rows.

- `scripts/run_domain_bootstrap_qa.py:9629` - "roster_table_student_group_assignment"
- `scripts/run_domain_bootstrap_qa.py:9697` - "roster_table_student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9861` - if support_kind in {"explicit_table_group_assignment", "roster_table_student_group_assignment", "group_assignment"}
- `scripts/run_domain_bootstrap_qa.py:9877` - if support_kind in {"explicit_table_group_assignment", "roster_table_student_group_assignment"}
- `scripts/run_domain_bootstrap_qa.py:9947` - "roster_table_student_group_assignment",

### `source_record_student_group_assignment`

Candidate parser over school roster prose; should stay disabled by default.

- `scripts/run_domain_bootstrap_qa.py:9698` - "source_record_student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9863` - if support_kind == "source_record_student_group_assignment"
- `scripts/run_domain_bootstrap_qa.py:9879` - if support_kind == "source_record_student_group_assignment"
- `scripts/run_domain_bootstrap_qa.py:9948` - "source_record_student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:10071` - "SupportKind": "source_record_student_group_assignment",
- `scripts/select_qa_mode_without_oracle.py:3193` - {"group_count", "source_record_student_group_assignment", "student_group_assignment"}

### `student_group_assignment`

School-shaped admitted predicate name. Keep for old compiles while preferring generic assignment names.

- `scripts/audit_helper_classes.py:86` - "student_group_assignment",
- `scripts/audit_helper_classes.py:87` - "student_group_assignment(Student, Version, Group).",
- `scripts/run_domain_bootstrap_qa.py:4193` - "student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9376` - "student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9392` - student_assignment_rows = _runtime_rows(runtime, "student_group_assignment(Student, Version, Group).")
- `scripts/run_domain_bootstrap_qa.py:9577` - "SupportKind": "student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9611` - "SupportKind": "student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9629` - "roster_table_student_group_assignment"
- `scripts/run_domain_bootstrap_qa.py:9697` - "roster_table_student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9698` - "source_record_student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9699` - "student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9773` - "student_group_assignment(Student, Version, Group).",
- ... 12 more active-code hits

### `student_in_homeroom`

School-shaped query predicate. Keep only for old compiles/tests.

- `scripts/run_domain_bootstrap_qa.py:4195` - "student_in_homeroom",
- `scripts/run_domain_bootstrap_qa.py:9280` - if predicate not in {"explicit_table_membership", "roster_table_member", "student_in_homeroom", "homeroom_member"}:
- `scripts/run_domain_bootstrap_qa.py:9288` - elif predicate in {"student_in_homeroom", "homeroom_member"} and len(args) >= 3 and not _is_prolog_variable(str(args[2]).strip()):
- `scripts/run_domain_bootstrap_qa.py:9377` - "student_in_homeroom",
- `scripts/run_domain_bootstrap_qa.py:9394` - student_homeroom_rows = _runtime_rows(runtime, "student_in_homeroom(Student, Homeroom, Version).")
- `scripts/run_domain_bootstrap_qa.py:9870` - elif predicate in {"homeroom_member", "student_in_homeroom"} and len(args) >= 3:
- `scripts/select_qa_mode_without_oracle.py:2095` - "student_in_homeroom",
- `scripts/select_qa_mode_without_oracle.py:3200` - if "student entries" in question and predicates.intersection({"student_in_homeroom", "member_of_homeroom"}):

### `homeroom_member`

School-shaped query predicate. Keep only for old compiles/tests.

- `scripts/run_domain_bootstrap_qa.py:4171` - _homeroom_member_alias_companion(runtime, predicate=predicate, args=args, query=query),
- `scripts/run_domain_bootstrap_qa.py:4187` - "homeroom_member",
- `scripts/run_domain_bootstrap_qa.py:9195` - def _homeroom_member_alias_companion(
- `scripts/run_domain_bootstrap_qa.py:9202` - if predicate != "homeroom_member" or len(args) < 3:
- `scripts/run_domain_bootstrap_qa.py:9233` - "SupportKind": "homeroom_member_printed_label",
- `scripts/run_domain_bootstrap_qa.py:9246` - "query": "homeroom_member_alias_support(Student, Homeroom, Version, PrintedMember).",
- `scripts/run_domain_bootstrap_qa.py:9249` - "predicate": "homeroom_member_alias_support",
- `scripts/run_domain_bootstrap_qa.py:9250` - "prolog_query": "homeroom_member_alias_support(Student, Homeroom, Version, PrintedMember).",
- `scripts/run_domain_bootstrap_qa.py:9258` - "query-only homeroom alias companion answers a sparse homeroom_member/3 "
- `scripts/run_domain_bootstrap_qa.py:9280` - if predicate not in {"explicit_table_membership", "roster_table_member", "student_in_homeroom", "homeroom_member"}:
- `scripts/run_domain_bootstrap_qa.py:9288` - elif predicate in {"student_in_homeroom", "homeroom_member"} and len(args) >= 3 and not _is_prolog_variable(str(args[2]).strip()):
- `scripts/run_domain_bootstrap_qa.py:9370` - "homeroom_member",
- ... 3 more active-code hits

### `source_record_adult_role`

Derived by the legacy school-roster adult parser; should stay disabled by default.

- `scripts/run_domain_bootstrap_qa.py:9904` - "source_record_adult_role",
- `scripts/run_domain_bootstrap_qa.py:10124` - "SupportKind": "source_record_adult_role",

### `industrial_sensor_support`

Query-time helper over one sensor-log family. It must not become the normal path for instrument records.

- `scripts/audit_helper_classes.py:69` - "industrial_sensor_support": (
- `scripts/run_domain_bootstrap_qa.py:7751` - "query": "industrial_sensor_support(SupportKind, Subject, Value, Detail, SourceRow).",
- `scripts/run_domain_bootstrap_qa.py:7754` - "predicate": "industrial_sensor_support",
- `scripts/run_domain_bootstrap_qa.py:7755` - "prolog_query": "industrial_sensor_support(SupportKind, Subject, Value, Detail, SourceRow).",

### `_industrial_sensor_companion`

Implementation hook for industrial_sensor_support; keep disabled with helper delivery unless transfer evidence promotes a generic replacement.

- `scripts/audit_helper_classes.py:25` - _industrial_sensor_companion,
- `scripts/audit_helper_classes.py:37` - _industrial_sensor_companion,
- `scripts/audit_helper_classes.py:70` - _industrial_sensor_companion,
- `scripts/run_domain_bootstrap_qa.py:4175` - _industrial_sensor_companion(runtime, predicate=predicate, args=args, query=query),
- `scripts/run_domain_bootstrap_qa.py:7318` - def _industrial_sensor_companion(

### `roster_state_support`

Broad compatibility helper. It is acceptable only because default delivery is disabled.

- `scripts/audit_helper_classes.py:84` - "roster_state_support": (
- `scripts/run_domain_bootstrap_qa.py:9737` - "query": "roster_state_support(SupportKind, PersonOrSupervisor, GroupOrTarget, Start, End, CountOrRole).",
- `scripts/run_domain_bootstrap_qa.py:9740` - "predicate": "roster_state_support",
- `scripts/run_domain_bootstrap_qa.py:9741` - "prolog_query": "roster_state_support(SupportKind, PersonOrSupervisor, GroupOrTarget, Start, End, CountOrRole).",
- `scripts/select_qa_mode_without_oracle.py:1069` - "roster_state_support",
- `scripts/select_qa_mode_without_oracle.py:1954` - "roster_state_support",
- `scripts/select_qa_mode_without_oracle.py:2929` - if "what role" in question and "assigned" in question and "roster_state_support" in predicates:
- `scripts/select_qa_mode_without_oracle.py:2930` - if "roster_state_support" in direct_predicates:
- `scripts/select_qa_mode_without_oracle.py:3079` - if "roster_state_support" in predicates and support_kinds.intersection(
- `scripts/select_qa_mode_without_oracle.py:3192` - if "roster_state_support" in predicates and support_kinds.intersection(

### `trip_leader_`

Fixture-shaped source atom prefix inside the legacy roster adult parser.

- `scripts/run_domain_bootstrap_qa.py:10172` - ("trip_leader_", "trip_leader", "true"),

### `chaperone_`

Fixture-shaped source atom prefix inside the legacy roster adult parser.

- `scripts/run_domain_bootstrap_qa.py:10173` - ("chaperone_", "chaperone", "true"),
- `scripts/select_qa_mode_without_oracle.py:2947` - hazard_predicates = {"chaperone_observation", "hazard_status", "incident_occurred"}

## Operating Rule

- `structural`: allowed as architecture.
- `compatibility_alias` / `compatibility_predicate`: allowed for old artifacts and old compile outputs; new surfaces should prefer the replacement.
- `quarantined_candidate_helper` / `quarantined_parser_marker`: allowed only behind disabled legacy-helper paths or in historical documentation.
- Any new high-risk active-code hit needs transfer evidence or a generic replacement before it can be promoted.

# Fixture Vocabulary Leak Audit

This audit separates live architecture vocabulary from legacy compatibility and historical strata.
A hit is not automatically a bug; the `status` and `replacement` columns define the current contract.

| Term | Status | Risk | Active code | Tests | Current docs | Worksheets | Replacement |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `explicit_table_membership` | `structural` | `low` | 17 | 7 | 4 | 3 | n/a |
| `explicit_table_member_label` | `structural` | `low` | 18 | 5 | 2 | 2 | n/a |
| `explicit_table_count_support` | `structural` | `low` | 4 | 2 | 3 | 0 | n/a |
| `roster_table_member` | `compatibility_alias` | `medium` | 27 | 37 | 3 | 2 | explicit_table_membership |
| `roster_table_member_label` | `compatibility_alias` | `medium` | 8 | 12 | 0 | 1 | explicit_table_member_label |
| `roster_table_count_support` | `compatibility_alias` | `medium` | 1 | 5 | 0 | 1 | explicit_table_count_support |
| `roster_table_student_group_assignment` | `compatibility_alias` | `high` | 5 | 4 | 0 | 0 | explicit_table_group_assignment |
| `source_record_student_group_assignment` | `quarantined_candidate_helper` | `high` | 6 | 8 | 2 | 0 | direct group_assignment/group_membership/explicit_table_membership compile surfaces |
| `student_group_assignment` | `compatibility_predicate` | `high` | 24 | 28 | 2 | 2 | group_assignment(Person, Version, Group) or group_membership(Person, Group, Start, End) |
| `student_in_homeroom` | `compatibility_predicate` | `high` | 8 | 12 | 1 | 0 | explicit_table_membership or group_assignment |
| `homeroom_member` | `compatibility_predicate` | `high` | 15 | 7 | 0 | 0 | explicit_table_membership or group_assignment |
| `adult_role` | `compatibility_predicate` | `medium` | 27 | 25 | 1 | 2 | person_role(Person, Role) or role_assignment(Person, Role, Scope) |
| `source_record_adult_role` | `quarantined_candidate_helper` | `high` | 2 | 0 | 0 | 0 | direct person_role/role_assignment compile surfaces |
| `staff_statement` | `compatibility_predicate` | `medium` | 10 | 3 | 0 | 1 | recorded_statement(StatementId, Speaker, Content) |
| `roster_state_support` | `legacy_native_helper_adapter` | `high` | 10 | 56 | 4 | 5 | direct compile surfaces plus explicit_table_* ledger facts |
| `trip_leader_` | `quarantined_parser_marker` | `high` | 1 | 1 | 0 | 0 | direct person_role/role_assignment compile surfaces |
| `chaperone_` | `quarantined_parser_marker` | `high` | 2 | 14 | 0 | 0 | direct person_role/role_assignment compile surfaces |
| `medical_` | `quarantined_parser_marker` | `medium` | 75 | 54 | 1 | 0 | direct person_role/role_assignment compile surfaces |

## High-Risk Active Hits

### `roster_table_student_group_assignment`

School-shaped support kind. Keep only when reading old roster_table_member rows.

- `scripts/run_domain_bootstrap_qa.py:9485` - "roster_table_student_group_assignment"
- `scripts/run_domain_bootstrap_qa.py:9552` - "roster_table_student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9715` - if support_kind in {"explicit_table_group_assignment", "roster_table_student_group_assignment"}
- `scripts/run_domain_bootstrap_qa.py:9731` - if support_kind in {"explicit_table_group_assignment", "roster_table_student_group_assignment"}
- `scripts/run_domain_bootstrap_qa.py:9800` - "roster_table_student_group_assignment",

### `source_record_student_group_assignment`

Candidate parser over school roster prose; should stay disabled by default.

- `scripts/run_domain_bootstrap_qa.py:9553` - "source_record_student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9717` - if support_kind == "source_record_student_group_assignment"
- `scripts/run_domain_bootstrap_qa.py:9733` - if support_kind == "source_record_student_group_assignment"
- `scripts/run_domain_bootstrap_qa.py:9801` - "source_record_student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9924` - "SupportKind": "source_record_student_group_assignment",
- `scripts/select_qa_mode_without_oracle.py:3193` - {"group_count", "source_record_student_group_assignment", "student_group_assignment"}

### `student_group_assignment`

School-shaped admitted predicate name. Keep for old compiles while preferring generic assignment names.

- `scripts/audit_helper_classes.py:86` - "student_group_assignment",
- `scripts/audit_helper_classes.py:87` - "student_group_assignment(Student, Version, Group).",
- `scripts/run_domain_bootstrap_qa.py:4078` - "student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9251` - "student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9267` - student_assignment_rows = _runtime_rows(runtime, "student_group_assignment(Student, Version, Group).")
- `scripts/run_domain_bootstrap_qa.py:9451` - "SupportKind": "student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9467` - "SupportKind": "student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9485` - "roster_table_student_group_assignment"
- `scripts/run_domain_bootstrap_qa.py:9552` - "roster_table_student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9553` - "source_record_student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9554` - "student_group_assignment",
- `scripts/run_domain_bootstrap_qa.py:9628` - "student_group_assignment(Student, Version, Group).",
- ... 12 more active-code hits

### `student_in_homeroom`

School-shaped query predicate. Keep only for old compiles/tests.

- `scripts/run_domain_bootstrap_qa.py:4079` - "student_in_homeroom",
- `scripts/run_domain_bootstrap_qa.py:9156` - if predicate not in {"explicit_table_membership", "roster_table_member", "student_in_homeroom", "homeroom_member"}:
- `scripts/run_domain_bootstrap_qa.py:9164` - elif predicate in {"student_in_homeroom", "homeroom_member"} and len(args) >= 3 and not _is_prolog_variable(str(args[2]).strip()):
- `scripts/run_domain_bootstrap_qa.py:9252` - "student_in_homeroom",
- `scripts/run_domain_bootstrap_qa.py:9268` - student_homeroom_rows = _runtime_rows(runtime, "student_in_homeroom(Student, Homeroom, Version).")
- `scripts/run_domain_bootstrap_qa.py:9724` - elif predicate in {"homeroom_member", "student_in_homeroom"} and len(args) >= 3:
- `scripts/select_qa_mode_without_oracle.py:2095` - "student_in_homeroom",
- `scripts/select_qa_mode_without_oracle.py:3200` - if "student entries" in question and predicates.intersection({"student_in_homeroom", "member_of_homeroom"}):

### `homeroom_member`

School-shaped query predicate. Keep only for old compiles/tests.

- `scripts/run_domain_bootstrap_qa.py:4056` - _homeroom_member_alias_companion(runtime, predicate=predicate, args=args, query=query),
- `scripts/run_domain_bootstrap_qa.py:4072` - "homeroom_member",
- `scripts/run_domain_bootstrap_qa.py:9071` - def _homeroom_member_alias_companion(
- `scripts/run_domain_bootstrap_qa.py:9078` - if predicate != "homeroom_member" or len(args) < 3:
- `scripts/run_domain_bootstrap_qa.py:9109` - "SupportKind": "homeroom_member_printed_label",
- `scripts/run_domain_bootstrap_qa.py:9122` - "query": "homeroom_member_alias_support(Student, Homeroom, Version, PrintedMember).",
- `scripts/run_domain_bootstrap_qa.py:9125` - "predicate": "homeroom_member_alias_support",
- `scripts/run_domain_bootstrap_qa.py:9126` - "prolog_query": "homeroom_member_alias_support(Student, Homeroom, Version, PrintedMember).",
- `scripts/run_domain_bootstrap_qa.py:9134` - "query-only homeroom alias companion answers a sparse homeroom_member/3 "
- `scripts/run_domain_bootstrap_qa.py:9156` - if predicate not in {"explicit_table_membership", "roster_table_member", "student_in_homeroom", "homeroom_member"}:
- `scripts/run_domain_bootstrap_qa.py:9164` - elif predicate in {"student_in_homeroom", "homeroom_member"} and len(args) >= 3 and not _is_prolog_variable(str(args[2]).strip()):
- `scripts/run_domain_bootstrap_qa.py:9246` - "homeroom_member",
- ... 3 more active-code hits

### `source_record_adult_role`

Derived by the legacy school-roster adult parser; should stay disabled by default.

- `scripts/run_domain_bootstrap_qa.py:9758` - "source_record_adult_role",
- `scripts/run_domain_bootstrap_qa.py:9977` - "SupportKind": "source_record_adult_role",

### `roster_state_support`

Broad compatibility helper. It is acceptable only because default delivery is disabled.

- `scripts/audit_helper_classes.py:84` - "roster_state_support": (
- `scripts/run_domain_bootstrap_qa.py:9592` - "query": "roster_state_support(SupportKind, PersonOrSupervisor, GroupOrTarget, Start, End, CountOrRole).",
- `scripts/run_domain_bootstrap_qa.py:9595` - "predicate": "roster_state_support",
- `scripts/run_domain_bootstrap_qa.py:9596` - "prolog_query": "roster_state_support(SupportKind, PersonOrSupervisor, GroupOrTarget, Start, End, CountOrRole).",
- `scripts/select_qa_mode_without_oracle.py:1069` - "roster_state_support",
- `scripts/select_qa_mode_without_oracle.py:1954` - "roster_state_support",
- `scripts/select_qa_mode_without_oracle.py:2929` - if "what role" in question and "assigned" in question and "roster_state_support" in predicates:
- `scripts/select_qa_mode_without_oracle.py:2930` - if "roster_state_support" in direct_predicates:
- `scripts/select_qa_mode_without_oracle.py:3079` - if "roster_state_support" in predicates and support_kinds.intersection(
- `scripts/select_qa_mode_without_oracle.py:3192` - if "roster_state_support" in predicates and support_kinds.intersection(

### `trip_leader_`

Fixture-shaped source atom prefix inside the legacy roster adult parser.

- `scripts/run_domain_bootstrap_qa.py:10025` - ("trip_leader_", "trip_leader", "true"),

### `chaperone_`

Fixture-shaped source atom prefix inside the legacy roster adult parser.

- `scripts/run_domain_bootstrap_qa.py:10026` - ("chaperone_", "chaperone", "true"),
- `scripts/select_qa_mode_without_oracle.py:2947` - hazard_predicates = {"chaperone_observation", "hazard_status", "incident_occurred"}

## Operating Rule

- `structural`: allowed as architecture.
- `compatibility_alias` / `compatibility_predicate`: allowed for old artifacts and old compile outputs; new surfaces should prefer the replacement.
- `quarantined_candidate_helper` / `quarantined_parser_marker`: allowed only behind disabled legacy-helper paths or in historical documentation.
- Any new high-risk active-code hit needs transfer evidence or a generic replacement before it can be promoted.

# Lantern School Field Trip Progress Journal

Fixture id: `lantern_school_field_trip`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## LSFT-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming/lantern_school_field_trip.zip`

Files admitted:

- `source.md` / `story.md`
- `fixture_notes.md`
- `qa.md`
- `qa_questions.jsonl`
- `oracle.jsonl`
- `qa_battery.json`

Benchmark discipline:

- `source.md`/`story.md` is the only cold compile source.
- `oracle.jsonl`, `qa_battery.json`, `qa.md`, and `fixture_notes.md` are scoring/review assets, not compile context.
- No Python source-prose interpretation is allowed.

## LSFT-001 - First Full-40 Cold Baseline

Date: 2026-05-07

Evidence lane: `cold_unseen`

Score: `21 exact / 5 partial / 14 miss`

Artifacts:

- Compile: `tmp/incoming_10_cold_runs_20260507/lantern_school_field_trip`
- QA: `tmp/incoming_10_cold_qa_20260507/lantern_school_field_trip`

Boundary: `0` write proposals and `0` runtime load errors. This is an immediate repair frontier fixture.

## LSFT-002 - Administrative Roster Timeline Candidate

Date: 2026-05-07

Evidence lane: `candidate_compile_mode`

Candidate context: `administrative_roster_timeline_strategy_v1`

Targeted non-exact replay: `9 exact / 1 partial / 9 miss` across the `19`
baseline non-exact rows. This rescued attendance, lead-teacher/chaperone
identity, Hana/Niles pairing, Shore Team composition, sealed-container contact
and determination, return-coach count, and final incident-report summary rows.

Full guardrail replay: `18 exact / 4 partial / 18 miss` across all `40` rows,
down from the baseline `21 / 5 / 14`. The candidate rescued `9` old non-exact
rows but regressed `12` old exact rows, mostly original group membership,
Day-1/Day-2 supervision, reassignment, and observation-point rows.

Row-gated upper bound against the cold baseline: `30 exact / 1 partial / 9
miss`.

Artifacts:

- Candidate compile: `tmp/incoming_10_repair_lantern_context_v1c`
- Targeted QA: `tmp/incoming_10_repair_lantern_context_v1c_qa_nonexact`
- Full guardrail QA: `tmp/incoming_10_repair_lantern_context_v1c_qa_full`

Decision: useful row-gated evidence mode and selector-training artifact, not a
global default compile lens. The lesson is to preserve temporary pair/station
surfaces without thinning the standing roster and supervision backbone.

## LSFT-003 - Administrative Roster Row-Gated Selector

Date: 2026-05-07

Evidence lane: `candidate_mode_selector`

Selector replay:
`tmp/incoming_10_candidate_mode_selectors/lantern_guarded_selector_v2.md`

Result: `30 exact / 1 partial / 9 miss`, matching the perfect available upper
bound from baseline plus administrative-roster candidate modes. The selector
chose the best available mode on all `40/40` rows with `0` selector errors.

Guard lessons:

- Student-count questions need scoped final-attendance rows, not broad roster
  volume.
- Temporary team/shore-team questions need group-formation rows, not standing
  group membership alone.
- No-touch hazard questions need incident/hazard observation surfaces, not
  attendance rosters.
- Same-name distinction questions need alias plus group-membership context, not
  an identity table alone.

Decision update: administrative roster/timeline is now a dependable row-gated
lane. The remaining misses press on richer supervision intervals, station
membership, role assignment, and incident-report discrepancy surfaces.

## LSFT-004 - Interval Atom Admission Repair

Date: 2026-05-07

Evidence lane: `candidate_compile_mode`

Harness repair: the mapper now accepts source-grounded `start_to_end` atoms such
as `2025_10_07t11_00_to_2025_10_07t12_30` for predicate-contract roles named
`interval` or `time_interval`. Previously these rows were skipped as
non-interval atoms unless the literal word `interval` appeared in the atom.

Candidate score: `22 exact / 4 partial / 14 miss`

Targeted replay over the `10` remaining non-exact selector rows: `3 exact / 0
partial / 7 miss`. The recovered rows were Day 1 group-designation suspension,
Jostad's Day 2 family-emergency departure reason, and the Day 3 found-object
surface.

Artifacts:

- Candidate compile: `tmp/incoming_10_repair_lantern_interval_admission_v3`
- Targeted QA: `tmp/incoming_10_repair_lantern_interval_admission_v3_qa_remaining`
- Full QA: `tmp/incoming_10_repair_lantern_interval_admission_v3_qa_full`

Decision: not a global compile replacement. The interval-admission candidate
adds useful event/state rows but remains thinner than the baseline and roster
candidate on static group membership and Day 3 hazard/accounting surfaces.

## LSFT-005 - Three-Mode Row-Gated Selector

Date: 2026-05-07

Evidence lane: `row_gated_candidate_selection`

Selector modes: cold baseline, administrative-roster candidate, and
interval-admission candidate.

Score: `33 exact / 0 partial / 7 miss`

Artifacts:

- Selector: `tmp/incoming_10_candidate_mode_selectors/lantern_guarded_selector_v5.json`
- Selector report: `tmp/incoming_10_candidate_mode_selectors/lantern_guarded_selector_v5.md`

Lesson: interval-shaped event rows are valuable only when the question asks
about a bounded state transition or event surface. The selector must still keep
baseline/roster modes for stable membership, final attendance, and hazard
resolution rows.

## LSFT-006 - Station/Role Assignment Candidate

Date: 2026-05-07

Evidence lane: `candidate_compile_mode` plus `candidate_mode_selector`

Harness/context change: expanded `administrative_roster_timeline_strategy_v1`
with station-split, temporary-monitor, absence-coverage, role-task, and
completion-report guidance. The additions are domain-general administrative
surfaces, not Lantern-specific rows.

Candidate compile:
`tmp/incoming_10_repair_lantern_station_role_v1_compile/domain_bootstrap_file_20260507T220121650139Z_source_qwen-qwen3-6-35b-a3b.json`

Candidate targeted replay over current weak rows:
`2 exact / 1 partial / 6 miss` across 9 probed rows. The useful new row was
Mr. Tullis's Day 1 11:00-12:30 absence/coverage activity: staying with Cosmo at
the coach. The candidate also answered the final incident summary, which was
already covered by the roster lane.

Full candidate replay:
`tmp/incoming_10_repair_lantern_station_role_v1_qa_full/domain_bootstrap_qa_20260507T221332658915Z_qa_qwen-qwen3-6-35b-a3b.json`

Candidate score: `22 exact / 4 partial / 14 miss`, so it is not a global
default.

Four-mode selector replay:
`tmp/incoming_10_candidate_mode_selectors/lantern_station_guarded_selector_v2.md`

Result: `34 exact / 0 partial / 6 miss`, matching the perfect available upper
bound across baseline, roster, interval, and station-role modes. The selector
chose the best available mode on all `40/40` rows with `0` selector errors.

Guard additions: temporary-supervisor absence questions route to
location-change plus supervision/medical-event evidence; post-reassignment
group-count questions keep the stable membership/count surface; source-specific
witness questions keep witness-report/claim evidence rather than unresolved
discrepancy summaries.

Lesson: station/role guidance is a real administrative sub-lens, but this
fixture shows it still does not reliably acquire station rosters or ad hoc role
assignments such as Station B watch duty or Lotte's recording-clipboard role.
The durable gain is absence-coverage activity; the remaining frontier is
explicit station roster and task-assignment acquisition.

## LSFT-007 - Roster-State Query Helper

Date: 2026-05-08

Evidence lane: `query_helper_substrate`

Harness change: `run_domain_bootstrap_qa.py` now exposes a query-only
`roster_state_support` companion over admitted roster facts:

- `group_member/3`
- `group_membership/4`
- `supervises/3`
- `supervision_assignment/4`

The helper normalizes membership rows, supervision rows, group counts, interval
surfaces, and role hints derived from admitted group atoms. It does not read
source prose and does not create durable facts.

Targeted replay over the six remaining Lantern selected misses using the
station-role compile:

`1 exact / 0 partial / 5 miss`

Artifact:

- `tmp/incoming_10_repair_lantern_roster_state_helper_probe/domain_bootstrap_qa_20260508T011155032876Z_qa_qwen-qwen3-6-35b-a3b.json`

Recovered row:

- `q033`: Lotte's Day 3 role. The admitted group atom
  `shore_team_recording` now surfaces as a role hint (`recording,shore`), enough
  for the judge to accept "recording clipboard" support.

Remaining frontier:

- `q010`: Day 1 afternoon attendance still lacks a direct 31-student attendance
  surface.
- `q016`, `q025`, `q026`: Station B supervisor and Station A/B membership still
  lack admitted station-roster links.
- `q031`: Day 3 chaperone count still lacks admitted three-chaperone Day 3
  support.

Decision: keep `roster_state_support` as a reusable query helper substrate, but
do not count it as a full Lantern promotion until a full replay and row-gated
selector prove exact-row protection. The important lesson is the boundary: the
helper can compose admitted roster atoms and expose role hints, but it must not
invent missing station/chaperone facts.

## LSFT-008 - Aggregate Roster/Station Registry Context

Date: 2026-05-08

Evidence lane: `candidate_compile_mode` plus `targeted_row_gated_selection`

Harness/context change: added a vocabulary-only aggregate roster scaffold:

- `session_attendance_count/5`
- `station_roster/5`
- `station_member/5`
- `station_supervisor/5`
- `task_assignment/5`
- `chaperone_roster/4`
- `chaperone_presence/4`
- `temporary_group_formed/5`

The direct-registry compile was too thin. The useful variant used the registry
as intake context rather than as the direct profile, allowing the model to keep
its discovered story-world shape while seeing aggregate roster hooks.

Compile artifact:

- `tmp/incoming_10_repair_lantern_roster_station_registry_v2_context_compile/domain_bootstrap_file_20260508T014756966175Z_source_qwen-qwen3-6-35b-a3b.json`

Admitted gains:

- `session_attendance_count(day1_afternoon_beach_survey, 31, all_students_except_cosmo, cosmo, 2025_10_07t13_30_to_16_00)`
- complete Station A roster: Quinn, Rafe, Suki, Tamsin, Uriel, Vera, Willem,
  Xiomara
- complete Station B roster: Brigid, Cleo, Dion, Elio, Freya
- Freya as Station B watch/supervisor

Targeted QA over the six remaining selected misses:

- registry-context mode: `4 exact / 0 partial / 2 miss`
- combined targeted selector with baseline, roster, interval, station-helper,
  and registry-context modes: `5 exact / 0 partial / 1 miss`
- selector chose best available mode on `6/6` rows with `0` selector errors

Selector artifact:

- `tmp/incoming_10_candidate_mode_selectors/lantern_roster_station_targeted_selector_v2.json`

New selector guard:

- attendance-count questions route to explicit `session_attendance_count`
  surfaces rather than interval roster volume.

Remaining frontier:

- `q031`: Day 3 chaperone count. The compile still fails to admit the explicit
  "Three chaperones supervised all 32 students" surface and the Jostad
  did-not-return exclusion as a count-bearing row.

Decision: this is a real compile-side gain, but still targeted evidence. A full
Lantern replay and row-gated selector are required before changing the durable
fixture headline from `34 / 0 / 6`. The likely available path is `39 / 0 / 1`
if full replay protects the previous exact rows.

## LSFT-009 - Day 3 Supervision Count And Station Supervisor Routing

Date: 2026-05-08

Evidence lane: `targeted_compile_mode_and_row_gated_selection`

Harness/context change: tried a vocabulary-only adult supervision count
registry. The first version used `date_or_interval` argument roles and failed
admission because day-level atoms such as `day3` are not clock intervals. The
useful version renamed those roles to event/context terms:

- `adult_presence_count/5`
- `adult_presence_status/5`
- `supervision_scope_count/5`
- `trip_exception_summary/5`

Compile artifact:

- `tmp/incoming_10_repair_lantern_supervision_count_registry_v2_compile/domain_bootstrap_file_20260508T020544273105Z_source_qwen-qwen3-6-35b-a3b.json`

Admitted gain:

- `supervision_scope_count(day3_beachclean_departure, day3, 3, 32, all_students_accounted_for_on_return_coach_3_chaperones_strand_tullis_okafor_supervised_all_32_students)`
- `trip_exception_summary(trip_completion_report, mr_henrik_jostad, early_departure, day2, departed_at_noon_due_to_family_emergency_did_not_return)`

Targeted QA:

- Day 3 chaperone count `q031`: `1 exact / 0 partial / 0 miss`
- six-row roster/station/supervision selector with baseline, roster, interval,
  station-helper, station-registry, and supervision-count modes:
  `6 exact / 0 partial / 0 miss`
- selector chose best available mode on `6/6` rows with `0` selector errors

Selector artifact:

- `tmp/incoming_10_candidate_mode_selectors/lantern_roster_station_supervision_targeted_selector_v2.json`

New selector guard:

- station-supervisor questions route to explicit `station_supervisor` surfaces
  rather than standing group-supervision rows. This corrected the q016 selector
  trap where broad interval evidence treated Ms. Okafor's group supervision as
  the Station B answer even though the admitted station row names Freya's watch
  role.

Decision: promote the selector guard and the lesson about event/context roles
for day-level aggregate statements. Do not promote the supervision registry as
a durable lens yet: the compile has useful Day 3 rows but is broad and
duplicate-heavy, so it needs either a tighter pass or transfer evidence before
joining the pegboard.

## LSFT-010 - Full Lantern Row-Gated Replay

Date: 2026-05-08

Evidence lane: `full_fixture_row_gated_selection`

After the station-registry candidate was replayed across all 40 questions, the
combined mode set had an exact upper bound on every Lantern row:

- baseline cold QA
- roster/context full QA
- interval admission full QA
- station-role full QA
- roster-state helper targeted QA
- roster/station registry-context full QA
- supervision-count targeted QA

Full selector artifact:

- `tmp/incoming_10_candidate_mode_selectors/lantern_full_roster_station_supervision_selector_v2.json`

Result:

- rows: `40`
- perfect selector upper bound: `40 exact`
- selected best available mode: `40 / 40`
- selected verdicts: `40 exact / 0 partial / 0 miss`
- selector errors: `0`

Selector repairs required for full promotion:

- narrowed the attendance-count guard so it no longer routes total trip counts
  or return-coach counts to a Day 1 session count surface;
- added a station-arrival-time guard so timestamp questions prefer event/report
  timestamp rows over roster identity volume;
- added a temporary-role guard so role-assignment questions can prefer
  `roster_state_support` role hints over bare group membership;
- added a completion-report incident-list guard so report-summary questions
  prefer trip-outcome plus issue/medical/hazard surfaces over a single
  incident-report row.

Decision: Lantern's current row-gated fixture headline is `40 / 0 / 0`. The
durable lesson is not "add more Lantern branches"; it is that the selector must
prefer the semantic surface named by the question act: total attendance vs
session attendance, station-specific role vs standing group supervision,
timestamp event vs identity roster, temporary role hint vs group atom, and
completion report summary vs individual incident row.

## LSFT-011 - Transfer Safety Proof

Date: 2026-05-08

Evidence lane: `cross_fixture_selector_transfer_control`

After the Lantern selector repairs, three unlike cold-batch fixtures were
replayed through guarded activation using their existing candidate mode sets.
The goal was not to improve their headlines; it was to test whether the new
Lantern-derived guards acted like fixture-shaped overfit and pulled other
fixtures away from their available upper bounds.

Transfer controls:

- Tournament Borrowed Names:
  `37 exact / 3 partial / 0 miss`, selected best `40 / 40`
- Greenhouse Quarantine:
  `35 exact / 4 partial / 1 miss`, selected best `40 / 40`
- Festival Permit Maze:
  `35 exact / 2 partial / 3 miss`, selected best `40 / 40`

Artifacts:

- `tmp/incoming_10_candidate_mode_selectors/tournament_admin_transfer_after_lantern_guards_v1.json`
- `tmp/incoming_10_candidate_mode_selectors/greenhouse_transfer_after_lantern_guards_v1.json`
- `tmp/incoming_10_candidate_mode_selectors/festival_transfer_after_lantern_guards_v1.json`

Decision: the Lantern repairs pass a first transfer-safety proof. They do not
yet prove a new lens, because the positive lift was Lantern-local. They do
support promoting the guards as family-shaped selector boundaries: avoid
session-count capture for total counts, prefer explicit event/time surfaces for
arrival-time questions, and route role/report questions by answer-bearing
surface rather than row volume.

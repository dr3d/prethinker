# Count Composition Roster Progress Journal

Fixture id: `count_composition_roster`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## CCR-000 - Fixture Admission

Date: 2026-05-09

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming\prethinker_fixtures_2026_05_09\count_composition_roster`

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

## CCR-002 - OpenRouter Parallel Candidate Lanes

Date: 2026-05-09

Evidence lane: `openrouter_parallel_candidate_lanes`

Artifacts:

- parallel compile: `tmp/openrouter_precision_20260509/parallel_compile_full_lanes6/count_composition_roster/`
- parallel QA: `tmp/openrouter_precision_20260509/parallel_qa_full_lanes6/count_composition_roster/`
- entity-ledger compile: `tmp/openrouter_precision_20260509/parallel_compile_entity_ledger_lanes6/count_composition_roster/`
- entity-ledger QA: `tmp/openrouter_precision_20260509/parallel_qa_entity_ledger_lanes6/count_composition_roster/`
- selector: `tmp/openrouter_precision_20260509/selector_three_candidate_guarded_lanes6/count_composition_roster/selector.json`

Results:

- baseline: `27 / 3 / 10`
- parallel lane: `33 / 1 / 6`
- entity-ledger lane: `29 / 2 / 9`
- guarded three-candidate selector: `33 / 1 / 6`
- perfect three-candidate ceiling: `38 / 1 / 1`

Lesson: the broad parallel lane is better than entity-ledger for this roster
fixture. The high perfect ceiling shows answer surfaces exist, but the selector
needs better discrimination for count/composition rows.

## CCR-001 - OpenRouter Full Cold Baseline

Date: 2026-05-09

Evidence lane: `openrouter_full_cold_baseline`

Artifacts:

- compile: `tmp/openrouter_precision_20260509/cold_compile_full/count_composition_roster/domain_bootstrap_file_20260509T153830009272Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/openrouter_precision_20260509/cold_qa_full/count_composition_roster/domain_bootstrap_qa_20260509T160649582659Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `27 exact / 3 partial / 10 miss` over `40`.

Compile admitted/skipped: `143 / 3`.

Lesson: composition rows were strong (`11/12` exact), which is the important
diagnostic. The system is often preserving membership/composition rather than
only reading the leaked distinct-student count. Remaining misses are mostly
lookup/count exactness.
## CCR-003 - Selector Policy Sweep

Date: 2026-05-09

Evidence lane: `openrouter_selector_policy_sweep`

Artifacts:

- completeness selector: `tmp/openrouter_precision_20260509/selector_three_candidate_completeness_lanes6/count_composition_roster/selector.json`
- policy readout: `tmp/openrouter_precision_20260509/parallel_lane6_research_readout.md`

Results:

- guarded three-candidate selector: `33 / 1 / 6`
- direct selector: `36 / 1 / 3`
- relevance selector: `36 / 1 / 3`
- completeness selector: `36 / 1 / 3`
- perfect three-candidate ceiling: `38 / 1 / 1`

Lesson: count/composition is mostly solved by existing candidates once the
selector is asked to score completeness rather than guarded structural safety.
This fixture now argues for selector calibration and query helpers, not for new
lenses.

## CCR-004 - Source-Record Ledger V2 Probe

Date: 2026-05-10

Evidence lane: `deterministic_source_record_ledger_v2`

Artifacts:

- refreshed compile: `tmp/openrouter_precision_20260509/source_record_facts_v2_compile_no_llm/count_composition_roster/`
- QA: `tmp/openrouter_precision_20260509/source_record_facts_v2_qa_lanes6/count_composition_roster/`
- selector: `tmp/openrouter_precision_20260509/selector_seven_candidate_source_record_v2_lanes6/count_composition_roster/selector.json`

Results:

- source-record V2 standalone: `27 / 4 / 9`
- seven-candidate selected: `38 / 0 / 2`
- seven-candidate ceiling: `40 / 0 / 0`

Lesson: all rows are reachable from the current candidate set. The remaining
gap is row routing or a narrow count/query helper, not compile acquisition.

## CCR-005 - Roster Helper Sibling Replay

Date: 2026-05-10

Evidence lane: `candidate_helper_sibling_replay`

Artifacts:

- source-record V2 compile:
  `tmp/openrouter_precision_20260509/source_record_facts_v2_compile_no_llm/count_composition_roster/`
- judged QA replay:
  `tmp/openrouter_precision_20260509/roster_sibling_helper_judged_replay_20260510/count_composition_roster/`
- helper usage audit:
  `tmp/helper_usage_audit_20260510/helper_usage_audit.md`

Result:

- judged replay: `24 / 3 / 13`
- zero write proposals
- `roster_state_support` companion rows: `4386`
- helper classes: `1326 clean-helper / 3060 candidate-helper`

Comparison:

- older source-record V2 QA on the same compile family: `27 / 4 / 9`

Lesson: the generalized roster helper is now present in completed QA artifacts
for a sibling fixture, so it is no longer merely a one-fixture parser probe.
However, the judged replay did not improve the sibling score. Several misses had
useful roster helper rows present while the model-selected direct homeroom
predicate was empty, so the hard edge is query/selector discrimination over
helper surfaces, not source-record parser transfer. Keep roster rows
candidate-labeled until a selector replay proves lift without fixture constants.

## CCR-006 - Focused Roster Helper Replay

Date: 2026-05-10

Evidence lane: `candidate_helper_focused_replay`

Artifacts:

- focused targeted replay:
  `tmp/openrouter_precision_20260509/roster_sibling_focused_replay_20260510/count_composition_roster/`
- focused full replay:
  `tmp/openrouter_precision_20260509/roster_sibling_focused_full_replay_20260510/count_composition_roster/`

Result:

- focused targeted replay on `q016,q024,q034`: `2 / 0 / 1`
- focused full replay: `29 / 2 / 9`
- zero write proposals
- focused full helper classes: `1209 clean-helper / 2790 candidate-helper`

Comparison:

- older source-record V2 QA: `27 / 4 / 9`
- unfocused roster-helper sibling replay: `24 / 3 / 13`

Lesson: `student_in_homeroom/3` needed roster-specific prioritization. Once the
companion treats its argument order as `(student, homeroom, version)` and sorts
wildcard-version questions latest-first, exact homeroom-count/current-homeroom
rows such as `q016` and `q024` become judgeable from helper output. The full run
improves the standalone source-record V2 result by two exact rows, but row-level
churn remains: some older exact rows regress because query generation still
misses chaperone/count compliance surfaces. This is useful candidate-helper
transfer evidence, not yet clean promotion.

## CCR-007 - Adult Compliance Helper And IR Fallback

Date: 2026-05-10

Evidence lane: `candidate_helper_compliance_projection`

Artifacts:

- targeted low-token replay:
  `tmp/openrouter_precision_20260509/roster_sibling_adult_compliance_targeted_20260510/count_composition_roster/`
- full low-token replay:
  `tmp/openrouter_precision_20260509/roster_sibling_adult_compliance_full_20260510/count_composition_roster/`
- targeted 3000-token replay:
  `tmp/openrouter_precision_20260509/roster_sibling_compliance_fallback_targeted_3000_20260510/count_composition_roster/`
- full 3000-token replay:
  `tmp/openrouter_precision_20260509/roster_sibling_compliance_full_3000_20260510/count_composition_roster/`

Results:

- low-token targeted compliance rows: `1 / 0 / 4`
- 3000-token targeted compliance rows (`q017,q033,q034,q035`): `4 / 0 / 0`
- 3000-token full replay: `30 / 2 / 8`
- zero write proposals
- full helper classes: `2242 clean-helper / 3420 candidate-helper`

Lesson: the adult/compliance surface was present in deterministic source-record
memory but needed a helper bridge: v1.3 adult rows expose 5 adults, 4 counted
chaperones, Patel excluded under `§3.4`, and the compliance log exposes
`v1_3_after_cn_03_2026_05_21_4_4_yes` plus the 3-flip summary. Four compliance
questions initially looked like query failures because the model's Semantic IR
was truncated at `max_tokens=1200`. With `max_tokens=3000`, the narrow fallback
from parsed no-query IR to roster helper triggers made the targeted compliance
set exact. The full run improves to `30 / 2 / 8`, but remaining row churn means
the next step is row-gating/selector discrimination across complementary
surfaces.

## CCR-008 - Roster Sibling Row Gate

Date: 2026-05-10

Evidence lane: `artifact_only_row_gate`

Artifacts:

- row-gate report:
  `tmp/openrouter_precision_20260509/roster_sibling_row_gate_20260510/row_gate.md`
- row-gate JSON:
  `tmp/openrouter_precision_20260509/roster_sibling_row_gate_20260510/row_gate.json`

Inputs:

- old source-record V2 QA: `27 / 4 / 9`
- focused homeroom helper replay: `29 / 2 / 9`
- adult/compliance fallback replay: `30 / 2 / 8`

Result:

- row-gated ceiling: `36 / 3 / 1`
- chosen run counts: old V2 `30`, focused homeroom `8`,
  adult/compliance `2`

Lesson: the helper work exposed complementary surfaces rather than one dominant
replacement surface. Old V2 still carries many policy/source lookup rows,
focused homeroom carries current membership/count rows, and adult/compliance
carries compliance rows. The remaining gap is selector discrimination across
known surfaces. Do not promote the helper as clean architecture yet; promote the
pattern that artifact packages must report which helper class and surface won
each row.

## CCR-009 - Selector Discrimination Probe

Date: 2026-05-10

Evidence lane: `selector_discrimination_probe`

Artifacts:

- feature readout:
  `tmp/openrouter_precision_20260509/roster_sibling_selector_discrimination_20260510/selector_discrimination.md`
- structural selector:
  `tmp/openrouter_precision_20260509/roster_sibling_selector_discrimination_20260510/structural_selector.json`
- guarded activation selector:
  `tmp/openrouter_precision_20260509/roster_sibling_selector_discrimination_20260510/guarded_activation_selector.json`
- support-kind guarded selector:
  `tmp/openrouter_precision_20260509/roster_sibling_selector_discrimination_20260510/guarded_activation_selector_support_kind.json`

Results:

- structural selector: `29 / 2 / 9`, selected-best `32 / 40`
- guarded activation selector: `34 / 2 / 4`, selected-best `37 / 40`
- support-kind guarded selector: `34 / 2 / 4`, selected-best `37 / 40`
- row-gated ceiling remains `36 / 3 / 1`

Lesson: existing guarded activation can use most of the complementary roster
surfaces when allowed to inspect activation evidence. Adding support-kind
extraction to selector quality made the helper evidence visible and moved the
Marrero total-count row into deterministic structural override, but the overall
score did not improve yet. The remaining gap is small and content-sensitive:
`q024` needs current-version support rather than any roster helper rows, and
`q028` needs bus-assignment/correction-notice source support rather than
homeroom rows. Do not add fixture-named guards; next selector work should expose
version/content hints from helper rows or leave this as selector-training data.

## CCR-010 - Explicit Roster Table Ledger Spike

Date: 2026-05-10

Evidence lane: `deterministic_precompile_ledger_spike`

Artifacts:

- compile with deterministic roster-table facts:
  `tmp/transfer_fixtures_20260510/count_roster_table_ledger_compile_v2_20260510/`
- full QA replay:
  `tmp/transfer_fixtures_20260510/count_roster_table_ledger_qa_v2_20260510/`
- initial no-source compile attempt, retained only as a harness note:
  `tmp/transfer_fixtures_20260510/count_roster_table_ledger_compile_20260510/`
  and `tmp/transfer_fixtures_20260510/count_roster_table_ledger_qa_20260510/`

Results:

- deterministic `roster_table_member/4` facts emitted for explicit roster
  tables in this fixture: `89`
- deterministic `roster_table_member/4` facts emitted for the fresh school
  transfer fixture: `0`, because its bus tables do not name a group column
- focused code tests: `99 passed`
- fresh compile: `37` admitted semantic facts, `0` skipped, plus `1519`
  deterministic source-record facts
- full QA replay: `28 / 3 / 9`
- zero write proposals

Lesson: this is a clean substrate boundary, not a saturated-score bite. The
source-record ledger now emits `roster_table_member(SourceRow, Version, Group,
Student)` only when the table itself has both an explicit grouping column
(`Homeroom`, `Group`, `Team`, `Cohort`, or `Bus`) and an explicit member column
(`Students`, `Student IDs`, `Members`, or `Participants`). It does not infer bus
or group membership from nearby prose or section titles. In the replay, rows
such as `q014` can query `roster_table_member/4` directly, but broader score did
not improve because the QA planner still routes many rows to older semantic
predicates or underspecified relaxed queries. This moves part of roster
membership from candidate-helper parsing toward deterministic memory, but it is
not yet a helper-promotion proof. The next work is a row-level comparison of
clean ledger wins versus older helper/selector wins, then selector guidance if
the deterministic surface is being missed.

## CCR-011 - Roster Table Query Guidance

Date: 2026-05-10

Evidence lane: `deterministic_ledger_query_guidance`

Artifacts:

- row comparison report:
  `tmp/transfer_fixtures_20260510/count_roster_table_row_compare_20260510/row_compare.md`
- first broad query guidance full replay:
  `tmp/transfer_fixtures_20260510/count_roster_table_query_guidance_full_20260510/`
- narrowed guidance targeted replay:
  `tmp/transfer_fixtures_20260510/count_roster_table_query_guidance_narrow_targeted_20260510/`
- narrowed guidance full replay:
  `tmp/transfer_fixtures_20260510/count_roster_table_query_guidance_narrow_full_20260510/`

Results:

- old source-record V2: `27 / 4 / 9`
- focused homeroom helper: `29 / 2 / 9`
- adult/compliance helper: `30 / 2 / 8`
- table ledger replay before guidance: `28 / 3 / 9`
- narrow table-guidance full replay: `30 / 3 / 7`
- guarded selector remains higher: `34 / 2 / 4`
- zero write proposals

Lesson: deterministic table memory helps when the query planner is told exactly
where it applies. Broad wording around "roster/group count" churned unrelated
chaperone and compliance questions; narrowed wording to "homeroom membership or
homeroom student-count" moved q015 and q016 to direct
`roster_table_member/4` queries and made both exact. The full replay now matches
the previous best exact count without relying on the larger candidate-helper
surface as the main route, but it does not close the selector gap. Remaining
hard rows are not a reason to widen deterministic parsing: q023/q024 are
identifier/name-normalization and registrar-authority answer-surface problems,
while q028 still needs correction-notice/bus-assignment routing.

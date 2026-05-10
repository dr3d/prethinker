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

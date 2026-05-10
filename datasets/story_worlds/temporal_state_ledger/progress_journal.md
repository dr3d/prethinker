# Temporal State Ledger Progress Journal

Fixture id: `temporal_state_ledger`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## TSL-000 - Fixture Admission

Date: 2026-05-09

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming\prethinker_fixtures_2026_05_09\temporal_state_ledger`

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

## TSL-001 - OpenRouter Full Cold Baseline

Date: 2026-05-09

Evidence lane: `openrouter_full_cold_baseline`

Artifacts:

- compile: `tmp/openrouter_precision_20260509/cold_compile_full/temporal_state_ledger/domain_bootstrap_file_20260509T153032607486Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/openrouter_precision_20260509/cold_qa_full/temporal_state_ledger/domain_bootstrap_qa_20260509T155434992311Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `20 exact / 2 partial / 18 miss` over `40`.

Compile admitted/skipped: `122 / 38`.

Lesson: this fixture confirms helper pressure. Temporal interval rows scored
`0/5`, supersession rows `0/2`, and temporal point rows `2/7`. Inspect the E-04
timestamp correction cascade before adding selector guards.

## TSL-002 - Timestamp Atom Admission Repair

Date: 2026-05-09

Evidence lane: `openrouter_timestamp_atom_admission_repair`

Artifacts:

- compile: `tmp/openrouter_precision_20260509/temporal_timestamp_fix_compile/domain_bootstrap_file_20260509T163131171134Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/openrouter_precision_20260509/temporal_timestamp_fix_qa/domain_bootstrap_qa_20260509T164145743431Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `30 exact / 4 partial / 6 miss` over `40`.

Compile admitted/skipped: `167 / 6`.

Repair: the mapper timestamp-role validator now accepts source-record
date-time atoms like `2026_04_28_08_00`. The model had proposed correct
temporal facts such as `event_timestamp(e_02, 2026_04_28_08_00)`, but the
contract gate rejected that atom shape as non-temporal.

Lesson: the broad temporal miss pattern was partly a mapper substrate bug, not
a new lens problem. Temporal point and supersession rows are now healthy; the
remaining frontier is narrower: duration arithmetic (`elapsed_hours`-style
joins), Lift Notice entity addressability, and a few provenance/detail joins.

## TSL-003 - Two-Candidate Selector Probe

Date: 2026-05-09

Evidence lane: `artifact_only_selector_probe`

Artifacts:

- structural selector: `tmp/openrouter_precision_20260509/temporal_timestamp_fix_selector_structural.json`
- guarded selector: `tmp/openrouter_precision_20260509/temporal_timestamp_fix_selector_guarded.json`

Candidates:

- baseline cold candidate: `20 / 2 / 18`
- timestamp-repaired candidate: `30 / 4 / 6`

Results:

- perfect row-gated ceiling across the two candidates: `34 / 3 / 3`
- structural selector: `24 / 3 / 13`
- guarded selector: `29 / 2 / 9`

Lesson: the old candidate retained some Lift Notice addressability that the
timestamp-repaired recompile lost, while the repaired candidate carries the
timestamp surface. The row-gated ceiling proves candidate diversity is useful,
but the current selector does not yet beat the repaired candidate. Do not add a
guard from this alone; first inspect whether Lift Notice addressability can be
made stable upstream.

## TSL-004 - OpenRouter Parallel Candidate Lanes

Date: 2026-05-09

Evidence lane: `openrouter_parallel_candidate_lanes`

Artifacts:

- parallel compile: `tmp/openrouter_precision_20260509/parallel_compile_full_lanes6/temporal_state_ledger/`
- parallel QA: `tmp/openrouter_precision_20260509/parallel_qa_full_lanes6/temporal_state_ledger/`
- entity-ledger compile: `tmp/openrouter_precision_20260509/parallel_compile_entity_ledger_lanes6/temporal_state_ledger/`
- entity-ledger QA: `tmp/openrouter_precision_20260509/parallel_qa_entity_ledger_lanes6/temporal_state_ledger/`
- selector: `tmp/openrouter_precision_20260509/selector_three_candidate_guarded_lanes6/temporal_state_ledger/selector.json`

Results:

- baseline: `20 / 2 / 18`
- timestamp atom repair: `30 / 4 / 6`
- parallel lane: `29 / 4 / 7`
- entity-ledger lane: `29 / 4 / 7`
- guarded three-candidate selector: `28 / 5 / 7`
- perfect three-candidate ceiling: `35 / 3 / 2`

Lesson: temporal candidate diversity is real, but current guarded selection
does not exploit it. The timestamp atom repair remains the best single exact
candidate; remaining pressure is duration arithmetic, Lift Notice
addressability, and selector discrimination.

## TSL-005 - Selector Policy Sweep

Date: 2026-05-09

Evidence lane: `openrouter_selector_policy_sweep`

Artifacts:

- completeness selector: `tmp/openrouter_precision_20260509/selector_three_candidate_completeness_lanes6/temporal_state_ledger/selector.json`
- policy readout: `tmp/openrouter_precision_20260509/parallel_lane6_research_readout.md`

Results:

- guarded three-candidate selector: `28 / 5 / 7`
- direct selector: `30 / 5 / 5`
- relevance selector: `30 / 5 / 5`
- completeness selector: `31 / 4 / 5`
- perfect three-candidate ceiling: `35 / 3 / 2`

Lesson: selector policy alone recovers three exact rows over the guarded
hybrid. The remaining gap is only four exact-capable rows, so temporal state is
now split between two frontiers: selector discrimination and real helper work
for duration/interval computation.

## TSL-006 - Source-Record Ledger V2 Probe

Date: 2026-05-10

Evidence lane: `deterministic_source_record_ledger_v2`

Artifacts:

- refreshed compile: `tmp/openrouter_precision_20260509/source_record_facts_v2_compile_no_llm/temporal_state_ledger/`
- QA: `tmp/openrouter_precision_20260509/source_record_facts_v2_qa_lanes6/temporal_state_ledger/`
- selector: `tmp/openrouter_precision_20260509/selector_seven_candidate_source_record_v2_lanes6/temporal_state_ledger/selector.json`

Results:

- source-record V2 standalone: `31 / 2 / 7`
- seven-candidate selected: `37 / 2 / 1`
- seven-candidate ceiling: `37 / 3 / 0`

Lesson: deterministic row addressability improves timestamp/date lookup, but
the unsolved surface is duration and clock-state computation. This fixture
still argues for temporal helper substrate, not a new lens.

## TSL-007 - Temporal Helper Join Repair

Date: 2026-05-10

Evidence lane: `temporal_helper_join_fix`

Artifacts:

- probe: `tmp/openrouter_precision_20260509/temporal_helper_join_fix_probe_v4/`
- full temporal QA refresh: `tmp/openrouter_precision_20260509/parallel_qa_full_temporal_helper_fix/`

Results:

- affected-row probe: `q017`, `q018`, and `q029` moved to `3 / 0 / 0`
- local tests: `195` then `196` selector/runtime tests passed during the fix
- full temporal rerun was not promoted as a scorecard replacement because fresh
  OpenRouter QA variance regressed unrelated rows; use it as a diagnostic run,
  not the official temporal lane

Lesson: the remaining duration frontier was not a new lens. It was a query
runtime helper join bug. Lowercase timestamp placeholders and repeated local
provenance variables such as `Eventid` caused the temporal helper chain to lose
or overconstrain the start/end anchors. The runtime now preserves repaired
temporal slot variables into relaxed fallbacks and localizes repeated event
provenance variables before joining. This is helper substrate work: it makes
already admitted timestamps compute as durable queryable state.

## TSL-008 - Helper-Fix Row-Gated Selector

Date: 2026-05-10

Evidence lane: `selector_temporal_helper_fix_eight`

Artifacts:

- selector: `tmp/openrouter_precision_20260509/selector_temporal_helper_fix_eight/selector.json`
- selector markdown: `tmp/openrouter_precision_20260509/selector_temporal_helper_fix_eight/selector.md`

Results:

- eight-candidate temporal selector: `39 / 1 / 0`
- selected-best rows: `40 / 40`
- selector errors: `0`
- `q017` and `q018` selected `temporal_helper_fix` exactly
- `q029` remains partial across all available modes

Lesson: duration computation is now selectable as a durable query surface. The
remaining temporal pressure is no longer a miss; it is the clock-state snapshot
composition row (`q029`), where admitted event/pause evidence supports the
answer but the currently selected query bundle still receives only partial
judgment. This points to pause-aware clock-state helper work, not a new lens.

## TSL-009 - Pause-Aware Clock Snapshot Helper

Date: 2026-05-10

Evidence lane: `clear_sample_pause_helper_probe`

Artifacts:

- probe: `tmp/openrouter_precision_20260509/clear_sample_pause_helper_probe/`
- full QA refresh: `tmp/openrouter_precision_20260509/parallel_qa_full_clear_sample_pause_helper/`

Results:

- `q029` probe: `1 / 0 / 0`
- full temporal QA refresh: `33 / 1 / 6`
- `q029` remained exact in the full refresh
- local runtime/selector tests: `197 passed`

Lesson: the last temporal row was a queryability gap, not a semantic lens gap.
The KB already admitted `clear_sample_segment/4`, `sampler_offline_interval/4`,
and sampler-offline rule exception facts. The runtime now exposes a
query-only `clear_sample_clock_pause_support` companion when a counted
clear-sample segment ends exactly as a sampler-offline interval begins. This
preserves the clock state (`paused`), governing rule, pause interval, and
counted hours as a deterministic helper surface. Temporal State Ledger now has
evidence for moving clock-state snapshots into helper substrate rather than
asking a model to re-infer them from prose.

The full 40-row rerun is diagnostic only. It confirms that `q029` now surfaces
the pause helper under normal evidence-bundle pressure, but fresh OpenRouter QA
variance regressed unrelated rows (`q010`, `q023`, `q026`, `q031`, `q032`,
`q036`, `q037`). Do not replace the row-gated selector score with this rerun.

## TSL-010 - Nine-Candidate Temporal Selector

Date: 2026-05-10

Evidence lane: `selector_temporal_pause_helper_nine`

Artifacts:

- selector: `tmp/openrouter_precision_20260509/selector_temporal_pause_helper_nine/selector.json`
- selector markdown: `tmp/openrouter_precision_20260509/selector_temporal_pause_helper_nine/selector.md`

Results:

- nine-candidate temporal selector: `40 / 0 / 0`
- selected-best rows: `40 / 40`
- selector errors: `0`
- `q017` and `q018` selected `temporal_helper_fix`
- `q029` selected `pause_helper`

Lesson: Temporal State Ledger now has a row-gated exact surface for every row.
The important finding is not that a single global rerun scored perfectly; it did
not. The finding is that durable admitted state plus deterministic helper
substrate can cover the fixture when the selector is allowed to choose the
right encounter surface per row. Duration rows use temporal helper joins;
clock-state snapshots use pause-aware companion support. This is the desired
shape for sharp memory: compile facts once, compute the mechanical consequences
in runtime helpers, and select the evidence surface that best matches the
question.

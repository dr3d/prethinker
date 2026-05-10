# Identifier Ledger Torture Progress Journal

Fixture id: `identifier_ledger_torture`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## ILT-000 - Fixture Admission

Date: 2026-05-09

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming\prethinker_fixtures_2026_05_09\identifier_ledger_torture`

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

## ILT-002 - OpenRouter Parallel Candidate Lanes

Date: 2026-05-09

Evidence lane: `openrouter_parallel_candidate_lanes`

Artifacts:

- parallel compile: `tmp/openrouter_precision_20260509/parallel_compile_full_lanes6/identifier_ledger_torture/`
- parallel QA: `tmp/openrouter_precision_20260509/parallel_qa_full_lanes6/identifier_ledger_torture/`
- entity-ledger compile: `tmp/openrouter_precision_20260509/parallel_compile_entity_ledger_lanes6/identifier_ledger_torture/`
- entity-ledger QA: `tmp/openrouter_precision_20260509/parallel_qa_entity_ledger_lanes6/identifier_ledger_torture/`
- selector: `tmp/openrouter_precision_20260509/selector_three_candidate_guarded_lanes6/identifier_ledger_torture/selector.json`

Results:

- baseline: `25 / 1 / 14`
- parallel lane: `30 / 4 / 6`
- entity-ledger lane: `32 / 2 / 6`
- guarded three-candidate selector: `33 / 2 / 5`
- perfect three-candidate ceiling: `36 / 2 / 2`

Lesson: source-entity ledger context helps this identifier-heavy fixture, but
the perfect ceiling still beats guarded selection. The next pressure is row
selection among candidate surfaces, not a new lens.

## ILT-001 - OpenRouter Full Cold Baseline

Date: 2026-05-09

Evidence lane: `openrouter_full_cold_baseline`

Artifacts:

- compile: `tmp/openrouter_precision_20260509/cold_compile_full/identifier_ledger_torture/domain_bootstrap_file_20260509T152728095249Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/openrouter_precision_20260509/cold_qa_full/identifier_ledger_torture/domain_bootstrap_qa_20260509T155358848361Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `25 exact / 1 partial / 14 miss` over `40`.

Compile admitted/skipped: `139 / 4`.

Lesson: archival identifier support helps, but the remaining misses are not all
raw identifier extraction. Lookup rows were strong (`12/15` exact), while
provenance/current-label and composition rows still need row-level inspection.
Compare missed exact labels against the archival identifier ledger before adding
selector guards.
## ILT-003 - Selector Policy Sweep

Date: 2026-05-09

Evidence lane: `openrouter_selector_policy_sweep`

Artifacts:

- completeness selector: `tmp/openrouter_precision_20260509/selector_three_candidate_completeness_lanes6/identifier_ledger_torture/selector.json`
- policy readout: `tmp/openrouter_precision_20260509/parallel_lane6_research_readout.md`

Results:

- guarded three-candidate selector: `33 / 2 / 5`
- completeness selector: `35 / 3 / 2`
- perfect three-candidate ceiling: `36 / 2 / 2`

Lesson: identifier-heavy rows are now nearly saturated by existing candidate
artifacts. The remaining gap is one exact-capable row, so this fixture does not
argue for a new lens. The useful discovery is selector policy: the
completeness prompt reads query evidence better than the guarded hybrid for
exact-string and current-identifier surfaces.

## ILT-004 - Source-Record Ledger V2 Probe

Date: 2026-05-10

Evidence lane: `deterministic_source_record_ledger_v2`

Artifacts:

- refreshed compile: `tmp/openrouter_precision_20260509/source_record_facts_v2_compile_no_llm/identifier_ledger_torture/`
- QA: `tmp/openrouter_precision_20260509/source_record_facts_v2_qa_lanes6/identifier_ledger_torture/`
- selector: `tmp/openrouter_precision_20260509/selector_seven_candidate_source_record_v2_lanes6/identifier_ledger_torture/selector.json`

Results:

- source-record V2 standalone: `34 / 3 / 3`
- seven-candidate selected: `39 / 1 / 0`
- seven-candidate ceiling: `40 / 0 / 0`

Lesson: exact identifier preservation is now mostly deterministic
addressability. No new lens is indicated; the last row is selector/query
surface pressure over available evidence.

# Contradictory Evidence Packet Progress Journal

Fixture id: `contradictory_evidence_packet`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## CEP-000 - Fixture Admission

Date: 2026-05-09

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming\prethinker_fixtures_2026_05_09\contradictory_evidence_packet`

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

## CEP-002 - OpenRouter Parallel Candidate Lanes

Date: 2026-05-09

Evidence lane: `openrouter_parallel_candidate_lanes`

Artifacts:

- parallel compile: `tmp/openrouter_precision_20260509/parallel_compile_full_lanes6/contradictory_evidence_packet/`
- parallel QA: `tmp/openrouter_precision_20260509/parallel_qa_full_lanes6/contradictory_evidence_packet/`
- entity-ledger compile: `tmp/openrouter_precision_20260509/parallel_compile_entity_ledger_lanes6/contradictory_evidence_packet/`
- entity-ledger QA: `tmp/openrouter_precision_20260509/parallel_qa_entity_ledger_lanes6/contradictory_evidence_packet/`
- selector: `tmp/openrouter_precision_20260509/selector_three_candidate_guarded_lanes6/contradictory_evidence_packet/selector.json`

Results:

- baseline: `17 / 1 / 22`
- parallel lane: `33 / 3 / 4`
- entity-ledger lane: `31 / 3 / 6`
- guarded three-candidate selector: `30 / 4 / 6`
- perfect three-candidate ceiling: `37 / 1 / 2`

Lesson: the broad parallel lane largely solves the apparent contradictory
evidence frontier. The selector currently chooses worse than the strongest
single candidate, so this is a selector discrimination problem, not an
unresolved-state or new-lens problem.

## CEP-003 - Selector Policy Sweep

Date: 2026-05-09

Evidence lane: `openrouter_selector_policy_sweep`

Artifacts:

- completeness selector: `tmp/openrouter_precision_20260509/selector_three_candidate_completeness_lanes6/contradictory_evidence_packet/selector.json`
- policy readout: `tmp/openrouter_precision_20260509/parallel_lane6_research_readout.md`

Results:

- guarded three-candidate selector: `30 / 4 / 6`
- direct selector: `34 / 4 / 2`
- relevance selector: `34 / 3 / 3`
- completeness selector: `35 / 3 / 2`
- perfect three-candidate ceiling: `37 / 1 / 2`

Lesson: the alleged unresolved-state frontier collapsed into selector policy.
The completeness selector recovers five exact rows over the guarded hybrid
without new compiles. The remaining exact gap is only two rows; unresolved-state
preservation remains healthy.


## CEP-001 - OpenRouter Full Cold Baseline

Date: 2026-05-09

Evidence lane: `openrouter_full_cold_baseline`

Artifacts:

- compile: `tmp/openrouter_precision_20260509/cold_compile_full/contradictory_evidence_packet/domain_bootstrap_file_20260509T154117409640Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/openrouter_precision_20260509/cold_qa_full/contradictory_evidence_packet/domain_bootstrap_qa_20260509T161429182163Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `17 exact / 1 partial / 22 miss` over `40`.

Compile admitted/skipped: `99 / 54`.

Lesson: unresolved-state preservation is not the main weakness: unresolved rows
scored `3/3` and negative-existential rows `4/5`. The pressure is lookup/source
addressability, count classification, and conflict/source-reliability joins.

## CEP-004 - Source-Record Ledger V2 Probe

Date: 2026-05-10

Evidence lane: `deterministic_source_record_ledger_v2`

Artifacts:

- refreshed compile: `tmp/openrouter_precision_20260509/source_record_facts_v2_compile_no_llm/contradictory_evidence_packet/`
- QA: `tmp/openrouter_precision_20260509/source_record_facts_v2_qa_lanes6/contradictory_evidence_packet/`
- selector: `tmp/openrouter_precision_20260509/selector_seven_candidate_source_record_v2_lanes6/contradictory_evidence_packet/selector.json`

Results:

- source-record V2 standalone: `35 / 2 / 3`
- seven-candidate selected and ceiling: `39 / 0 / 1`

Lesson: the weak surface was exact source addressability, not epistemic
refusal. Preserving table cells, labels, timestamps, and anchored official prose
nearly saturates the fixture without a new semantic lens.

## CEP-005 - Clock-Sync Source-Record Helper

Date: 2026-05-10

Evidence lane: `source_record_clock_sync_helper`

Artifacts:

- focused q011 probe: `tmp/openrouter_precision_20260509/contradictory_clock_sync_helper_probe/`
- full helper QA candidate: `tmp/openrouter_precision_20260509/contradictory_clock_sync_helper_full_source_record_v2/`
- selector: `tmp/openrouter_precision_20260509/selector_contradictory_clock_sync_helper_eight/selector.json`

Results:

- focused q011 probe: `1 / 0 / 0`
- full helper candidate: `26 / 4 / 10`
- eight-candidate selector: `40 / 0 / 0`
- selected-best rows: `40 / 40`
- selector errors: `0`
- local runtime/selector tests: `203 passed`

Lesson: the final contradictory-evidence miss was not an epistemic refusal
problem and not a new semantic lens. The answer date was already preserved in
the deterministic source-record ledger as a text atom plus numeric token:
`PEM-BAS-7's last successful NTP sync was 2026-03-19`. The query planner asked
for event/timestamp predicates, so the runtime now exposes a query-only
`source_record_clock_sync_support` companion when clock-sync/timestamp surfaces
are queried. The helper is deliberately narrow: it derives exact last-successful
NTP sync dates from admitted source-record rows and leaves all broader conflict
interpretation to the existing KB and selector.

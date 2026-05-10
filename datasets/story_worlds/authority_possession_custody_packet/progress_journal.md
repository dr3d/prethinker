# Authority Possession Custody Packet Progress Journal

Fixture id: `authority_possession_custody_packet`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## APCP-000 - Fixture Admission

Date: 2026-05-09

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming\prethinker_fixtures_2026_05_09\authority_possession_custody_packet`

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

## APCP-002 - OpenRouter Parallel Candidate Lanes

Date: 2026-05-09

Evidence lane: `openrouter_parallel_candidate_lanes`

Artifacts:

- parallel compile: `tmp/openrouter_precision_20260509/parallel_compile_full_lanes6/authority_possession_custody_packet/`
- parallel QA: `tmp/openrouter_precision_20260509/parallel_qa_full_lanes6/authority_possession_custody_packet/`
- entity-ledger compile: `tmp/openrouter_precision_20260509/parallel_compile_entity_ledger_lanes6/authority_possession_custody_packet/`
- entity-ledger QA: `tmp/openrouter_precision_20260509/parallel_qa_entity_ledger_lanes6/authority_possession_custody_packet/`
- selector: `tmp/openrouter_precision_20260509/selector_three_candidate_guarded_lanes6/authority_possession_custody_packet/selector.json`

Results:

- baseline: `23 / 1 / 16`
- parallel lane: `21 / 5 / 14`
- entity-ledger lane: `25 / 5 / 10`
- guarded three-candidate selector: `26 / 3 / 11`
- perfect three-candidate ceiling: `30 / 4 / 6`

Lesson: entity-ledger context is useful for authority/possession/custody, but
the remaining gap is still mostly candidate choice and joins. Do not treat the
larger entity compile as a global default without row gating.

## APCP-001 - OpenRouter Full Cold Baseline

Date: 2026-05-09

Evidence lane: `openrouter_full_cold_baseline`

Artifacts:

- compile: `tmp/openrouter_precision_20260509/cold_compile_full/authority_possession_custody_packet/domain_bootstrap_file_20260509T152746141305Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/openrouter_precision_20260509/cold_qa_full/authority_possession_custody_packet/domain_bootstrap_qa_20260509T155810949591Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `23 exact / 1 partial / 16 miss` over `40`.

Compile admitted/skipped: `190 / 20`.

Lesson: authority rows mostly landed (`11/14` exact), and unresolved rows were
healthy (`3/4`). The weak surfaces are count, custody, and provenance joins, so
this fixture does not yet argue for a new guard family.
## APC-003 - Selector Policy Sweep

Date: 2026-05-09

Evidence lane: `openrouter_selector_policy_sweep`

Artifacts:

- completeness selector: `tmp/openrouter_precision_20260509/selector_three_candidate_completeness_lanes6/authority_possession_custody_packet/selector.json`
- policy readout: `tmp/openrouter_precision_20260509/parallel_lane6_research_readout.md`

Results:

- guarded three-candidate selector: `26 / 3 / 11`
- relevance selector: `28 / 2 / 10`
- direct selector: `28 / 3 / 9`
- completeness selector: `27 / 2 / 11`
- perfect three-candidate ceiling: `30 / 4 / 6`

Lesson: authority/custody remains the main exception to the completeness
policy's global win. Relevance/direct selection better preserve the specific
authority or custody surface here. The next investigation should focus on the
remaining small selector gap before adding authority guards.

## APCP-004 - Source-Record Ledger V2 Probe

Date: 2026-05-10

Evidence lane: `deterministic_source_record_ledger_v2`

Artifacts:

- refreshed compile: `tmp/openrouter_precision_20260509/source_record_facts_v2_compile_no_llm/authority_possession_custody_packet/`
- QA: `tmp/openrouter_precision_20260509/source_record_facts_v2_qa_lanes6/authority_possession_custody_packet/`
- selector: `tmp/openrouter_precision_20260509/selector_seven_candidate_source_record_v2_lanes6/authority_possession_custody_packet/selector.json`

Results:

- source-record V2 standalone: `29 / 4 / 7`
- seven-candidate selected: `33 / 3 / 4`
- seven-candidate ceiling: `36 / 1 / 3`

Lesson: deterministic source-record V2 helped boring official addressability,
but the remaining rows still need custody/count and document-clause helpers
more than another semantic lens.

## APCP-005 - Personal-Letter Reading Access Guard Replay

Date: 2026-05-10

Evidence lane: `selector_authority_personal_letter_guard_replay`

Artifacts:

- selector: `tmp/openrouter_precision_20260509/selector_authority_personal_letter_guard_replay/authority_possession_custody_packet/selector.json`
- selector markdown: `tmp/openrouter_precision_20260509/selector_authority_personal_letter_guard_replay/authority_possession_custody_packet/selector.md`

Results:

- authority selector: `36 / 1 / 3`
- selected-best rows: `40 / 40`
- selector errors: `0`
- `q019` selected `memory_ledger_combo` exactly

Lesson: personal-letter reading access is not answered by raw source-record
volume. It needs the semantic boundary between reading-room access and
publication restriction. The guard now excludes broad `source_record` rows for
this question shape, the same way it already excluded source-record-facts
scaffolding. This is selector discrimination over existing admitted surfaces,
not a new lens.

## APCP-006 - Authority/Custody Helper Surface

Date: 2026-05-10

Evidence lane: `authority_custody_helper`

Artifacts:

- q022/q032/q037/q038 probe: `tmp/openrouter_precision_20260509/authority_custody_helper_probe/`
- q022/q032 probe after grouped-count fix: `tmp/openrouter_precision_20260509/authority_custody_helper_probe_v2_source_record/`
- q032 source-record-cell probe: `tmp/openrouter_precision_20260509/authority_custody_helper_probe_v3_source_record/`
- full QA candidate: `tmp/openrouter_precision_20260509/authority_custody_helper_full_source_record_v2/`
- selector: `tmp/openrouter_precision_20260509/selector_authority_custody_helper_eight_v2/selector.json`

Results:

- full helper candidate: `37 / 1 / 2`
- eight-candidate authority selector: `40 / 0 / 0`
- selected-best rows: `40 / 40`
- local runtime/selector tests: `202 passed`

Lesson: the remaining Authority/Possession misses were not a new lens problem.
They were queryability gaps over already admitted archive state. The runtime now
exposes an `archive_authority_custody_support` companion that derives grouped
custody counts, access/custody/authorization rows, recall-clause support, and
contractor custody consent/notice support from admitted facts and deterministic
source-record cells. The important distinction is weighted grouped inventory
versus raw custodian row count: three Pellico custody rows can represent
thirty-five physical items. Selector guarding now prefers the grouped helper
surface for this count shape.

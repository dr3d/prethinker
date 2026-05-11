# Rule Activation Exception Matrix Progress Journal

Fixture id: `rule_activation_exception_matrix`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## RAEM-000 - Fixture Admission

Date: 2026-05-09

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming\prethinker_fixtures_2026_05_09\rule_activation_exception_matrix`

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

## RAEM-002 - OpenRouter Parallel Candidate Lanes

Date: 2026-05-09

Evidence lane: `openrouter_parallel_candidate_lanes`

Artifacts:

- parallel compile: `tmp/openrouter_precision_20260509/parallel_compile_full_lanes6/rule_activation_exception_matrix/`
- parallel QA: `tmp/openrouter_precision_20260509/parallel_qa_full_lanes6/rule_activation_exception_matrix/`
- entity-ledger compile: `tmp/openrouter_precision_20260509/parallel_compile_entity_ledger_lanes6/rule_activation_exception_matrix/`
- entity-ledger QA: `tmp/openrouter_precision_20260509/parallel_qa_entity_ledger_lanes6/rule_activation_exception_matrix/`
- selector: `tmp/openrouter_precision_20260509/selector_three_candidate_guarded_lanes6/rule_activation_exception_matrix/selector.json`

Results:

- baseline: `36 / 2 / 2`
- parallel lane: `32 / 1 / 7`
- entity-ledger lane: `33 / 2 / 5`
- guarded three-candidate selector: `36 / 2 / 2`
- perfect three-candidate ceiling: `39 / 1 / 0`

Lesson: the original cold candidate remains very strong. The perfect ceiling
confirms some candidate diversity, but rule activation is not the urgent
frontier for this batch.

## RAEM-001 - OpenRouter Full Cold Baseline

Date: 2026-05-09

Evidence lane: `openrouter_full_cold_baseline`

Artifacts:

- compile: `tmp/openrouter_precision_20260509/cold_compile_full/rule_activation_exception_matrix/domain_bootstrap_file_20260509T153703643672Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/openrouter_precision_20260509/cold_qa_full/rule_activation_exception_matrix/domain_bootstrap_qa_20260509T160628915395Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `36 exact / 2 partial / 2 miss` over `40`.

Compile admitted/skipped: `110 / 5`.

Lesson: rule activation, threshold, exception, and cap surfaces are already
strong. This fixture is evidence that the existing rule/threshold guard families
are absorbing new pressure without a new lens.
## RAEM-003 - Selector Policy Sweep

Date: 2026-05-09

Evidence lane: `openrouter_selector_policy_sweep`

Artifacts:

- completeness selector: `tmp/openrouter_precision_20260509/selector_three_candidate_completeness_lanes6/rule_activation_exception_matrix/selector.json`
- policy readout: `tmp/openrouter_precision_20260509/parallel_lane6_research_readout.md`

Results:

- guarded three-candidate selector: `36 / 2 / 2`
- protected selector: `38 / 2 / 0`
- completeness selector: `38 / 1 / 1`
- perfect three-candidate ceiling: `39 / 1 / 0`

Lesson: rule activation is saturated by the current architecture. The fixture
does not demand a new guard family; the only remaining pressure is choosing
between equivalent rule/exception surfaces and auditing the author's flagged
leakage rows before any public claim.

## RAEM-004 - Source-Record Ledger V2 Probe

Date: 2026-05-10

Evidence lane: `deterministic_source_record_ledger_v2`

Artifacts:

- refreshed compile: `tmp/openrouter_precision_20260509/source_record_facts_v2_compile_no_llm/rule_activation_exception_matrix/`
- QA: `tmp/openrouter_precision_20260509/source_record_facts_v2_qa_lanes6/rule_activation_exception_matrix/`
- selector: `tmp/openrouter_precision_20260509/selector_seven_candidate_source_record_v2_lanes6/rule_activation_exception_matrix/selector.json`

Results:

- source-record V2 standalone: `32 / 7 / 1`
- seven-candidate selected: `37 / 2 / 1`
- seven-candidate ceiling: `40 / 0 / 0`

Lesson: source-record V2 is useful as a row-gated candidate, but rule activation
itself remains handled by existing semantic surfaces. This is not a global
source-record replacement.

## RAEM-005 - Grant Predicate Alias Bridge Sibling Proof

Date: 2026-05-11

Evidence lane: `canonical_predicate_completeness`

Artifacts:

- sibling audit:
  `tmp/transfer_fixtures_20260510/grant_award_alias_bridge_rule_cold_20260511.json`
- precision-wide audit:
  `tmp/transfer_fixtures_20260510/grant_award_alias_bridge_precision_all_20260511.json`

Result:

- cold artifact now emits `3 clean / 0 candidate / 0 unlabeled`
  `grant_award_support` rows through generic predicate aliases
- precision-wide audit now emits `26 clean / 0 candidate / 0 unlabeled`
  `grant_award_support` rows

Lesson:

This fixture already held award/status memory under older predicates such as
`final_grant_amount/3`, `application_status/2`, and
`eligibility_determination/3`. The newer grant helper did not trigger until a
generic alias bridge adapted those admitted predicates. The repair is not a new
lens and not source-prose extraction; it is canonical predicate-completeness
work over governed memory.

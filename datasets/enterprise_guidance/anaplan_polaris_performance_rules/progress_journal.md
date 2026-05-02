# Anaplan Polaris Progress Journal

This journal tracks attempts to compile the Anaplan Polaris performance-guidance fixture into a governed, queryable symbolic surface.

## APR-000 - Fixture Admission

- Mode: `fixture_setup`
- Source: `tmp/anaplan_polaris/anaplan_polaris.md`
- Expected Prolog guidance: no.
- Profile guidance: not run yet.
- Status: fixture created with source document, oracle-only gold KB, starter ontology registry, 43-question QA battery, failure buckets, and empty metrics ledger.

### Lesson

This is a different pressure shape from story worlds, legal cases, and maritime insurance. It asks Prethinker to preserve conditional operational guidance without converting recommendations into facts. The hard parts are priority order, condition/effect mapping, procedure/checklist preservation, and tradeoff handling.

## APR-001 - Profile-Guided Baseline

- Mode: `profile_guided`
- Registry guidance: `ontology_registry.json` starter enterprise-guidance profile.
- Expected Prolog guidance: no.
- Change: first source compile and QA sweep for the new fixture.
- Compile: parsed, 136 admitted operations, 186 skipped operations.
- Profile surface: 46 candidate predicates.
- Full-43 QA: 29 exact, 6 partial, 8 miss.
- Write proposals during QA: 0.

### Lesson

The fixture is immediately useful. The compiler captured enough priority/order/recommendation structure to answer most questions, but the misses are concentrated in the intended hard zones: preserving explanatory reasons for summary methods and user-based filters, linking guards to all three effects, keeping the positive side of avoid/prefer pairs, distinguishing Combined Grids from Tabular Multiple Column Export, preserving delta-load recommendations as positive rows, and querying `prefer_aggregation(sum)` instead of only higher-effort aggregation rows.

The high skip count is also diagnostic. It suggests the profile and compiler context need a clearer enterprise-guidance row-class contract rather than a wider predicate menu.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T024243609116Z_source_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T024857982496Z_qa_qwen-qwen3-6-35b-a3b.json`

## APR-002 - Query Strategy Hardening, Same Compile

- Mode: `profile_guided_requery`
- Registry guidance: same APR-001 compile artifact.
- Expected Prolog guidance: no.
- Change: expanded post-ingestion QA query strategy and evidence-table companion queries for enterprise guidance predicates.
- Full-43 QA: 34 exact, 1 partial, 8 miss.
- Write proposals during QA: 0.

### Lesson

The first improvement was query-side, not compile-side. Rows for export guidance, delta-load patterns, guard values/effects, and preferred aggregation were already present in the compiled KB, but the QA planner was sometimes asking a neighboring predicate family. Better query choreography converted five ambiguous rows without weakening admission.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T024243609116Z_source_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T031907173770Z_qa_qwen-qwen3-6-35b-a3b.json`

## APR-003 - Enterprise Guidance Compiler Context

- Mode: `profile_guided_compile_context`
- Registry guidance: starter enterprise-guidance profile.
- Expected Prolog guidance: no.
- Change: added a generic enterprise-guidance compiler context module for trigger/recommendation/reason/tradeoff/procedure boundaries.
- Compile: parsed, 175 admitted operations, 125 skipped operations.
- Full-43 QA: 34 exact, 3 partial, 6 miss.
- Write proposals during QA: 0.

### Lesson

The new context reduced compile skips and recovered some missing support, especially around positive/negative guidance pairs and procedure rows. Exact score did not move because the remaining misses were either true missing rationale rows or query-planner failures over already-admitted priority/debugging support.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T032627851936Z_source_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T033301870573Z_qa_qwen-qwen3-6-35b-a3b.json`

## APR-004 - Generic Rationale Predicate Regression

- Mode: `profile_guided_profile_widening_experiment`
- Registry guidance: temporary wider profile with generic `guidance_reason/2` and `guidance_alternative/2`.
- Expected Prolog guidance: no.
- Change: tested whether adding generic rationale/alternative predicates would improve answer support.
- Compile: parsed, 149 admitted operations, 147 skipped operations.
- Full-43 QA: 31 exact, 6 partial, 6 miss.
- Disposition: reverted from the fixture starter registry.

### Lesson

Widening the profile with a generic reason predicate was not a free win. It diluted row selection and reduced exact QA support. This matches the earlier story-world lesson: a broader predicate menu can make the compiler less decisive unless the row-class contract is very tight.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T033738934666Z_source_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T034415369059Z_qa_qwen-qwen3-6-35b-a3b.json`

## APR-005 - Priority And Debugging Support Queries

- Mode: `profile_guided_requery`
- Registry guidance: APR-003 compile artifact.
- Expected Prolog guidance: no.
- Change: tightened post-ingestion QA strategy for priority reasons, computationally intensive functions, All Cells risk, and already-optimized slow-line follow-up questions.
- Full-43 QA: 37 exact, 1 partial, 5 miss.
- Write proposals during QA: 0.

### Lesson

The best current result came from asking the KB for the right support bundle: priority rank plus priority reason, function class plus review target, and slow-line condition plus debugging tactic. The remaining misses are mostly compile-surface gaps around explanatory rationale: summary-method memory/on-demand blocking, nested-IF downside, DEV-list rationale, user-filter density/performance reason, and a low-complexity/high-populated-cell on-demand optimization explanation.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T032627851936Z_source_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T035140452175Z_qa_qwen-qwen3-6-35b-a3b.json`

## APR-006 - Causal-Cue Prose Pressure Regression

- Mode: `profile_guided_compile_context_experiment`
- Registry guidance: starter enterprise-guidance profile.
- Expected Prolog guidance: no.
- Change: added stronger generic guidance for because/so-that/however causal cues.
- Compile: parsed, 104 admitted operations, 167 skipped operations.
- QA: not run; compile surface was visibly thinner than APR-003.
- Disposition: keep the lesson, not the result.

### Lesson

More prose pressure again made the compiler less useful. The guidance was generic and non-oracle, but it reduced admitted coverage instead of preserving more rationale rows. Current best remains APR-005: use the APR-003 compile plus tighter query strategy.

Artifact:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T040527110122Z_source_qwen-qwen3-6-35b-a3b.json`

## APR-007 - Typed Rationale Predicate Regression

- Mode: `profile_guided_typed_rationale_experiment`
- Registry guidance: temporary typed rationale predicates for summary methods, nested IFs, DEV-list seeding, user-filter risks, and On-Demand Calculation candidates.
- Expected Prolog guidance: no.
- Change: tested narrow typed rationale predicates instead of generic `guidance_reason/2`.
- Compile: parsed, 79 admitted operations, 60 skipped operations.
- Full-43 QA: 24 exact, 4 partial, 15 miss.
- Disposition: reverted from the fixture starter registry and query strategy.

### Lesson

The typed rationale patch was cleaner than the generic reason predicate but still hurt the default compile. It pulled the model toward narrow answer-shaped row classes and away from the broader enterprise-guidance backbone that made APR-003 useful. This is an important negative result: the remaining rationale misses probably need better pass planning or support-bundle answering, not a larger default predicate menu.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T041700167450Z_source_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T042324220694Z_qa_qwen-qwen3-6-35b-a3b.json`

## APR-008 - Deterministic Safe-Compile Union

- Mode: `profile_guided_compile_union`
- Registry guidance: APR-001 and APR-003 both used the starter enterprise-guidance profile.
- Expected Prolog guidance: no.
- Change: deterministic set union of mapper-admitted facts/rules from APR-001 and APR-003 safe compile artifacts.
- Compile surface: 219 unique admitted facts, 0 rules.
- Full-43 QA: 37 exact, 4 partial, 2 miss.
- Write proposals during QA: 0.

### Lesson

Unioning two safe admitted compile surfaces can recover useful rows that a later stronger compile dropped, without reading the source prose or using the answer key. APR-001 preserved a useful `tradeoff/3` row for nested IF splitting that APR-003 lost, while APR-003 preserved broader enterprise guidance and procedure rows. Exact score stayed tied with APR-005, but exact-plus-partial improved to 41/43 and misses dropped to 2/43.

This is the strongest current APR answer-surface result, but the methodology should be labeled carefully: it is a deterministic union of two safe compiles, not a single-pass compile.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T044500000000Z_anaplan_apr008_union_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T044145321640Z_qa_qwen-qwen3-6-35b-a3b.json`

## APR-009 - Evidence-Bundle Planner Probe

- Mode: `profile_guided_evidence_bundle_probe`
- Registry guidance: APR-008 union compile.
- Expected Prolog guidance: no.
- Change: added an optional LLM-owned `evidence_bundle_plan_v1` prepass for post-ingestion QA. The prepass sees only the compiled KB predicate inventory, relevant admitted clauses, and the question. It does not see the raw source document or the answer key, and it cannot authorize writes.
- Probe scope: six APR-008 non-exact questions.
- Result on six-question probe: 1 exact, 2 partial, 3 miss.
- Write proposals during QA: 0.

### Lesson

The evidence-bundle planner is architecturally right but not yet a scoring win on APR. It often identifies useful support bundles, but the downstream Semantic IR query pass does not always carry the suggested queries through, and true compile-surface gaps remain for several rationale questions. The useful next step is not to widen the predicate menu again; it is to improve the handoff from evidence-bundle plan to admitted query operations and to classify misses as planner-bundle, compile-surface, or hybrid-join gaps.

Artifacts:

- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T043339252494Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T044356324512Z_qa_qwen-qwen3-6-35b-a3b.json`

## APR-010 - Reusable Compile-Union Tool And Failure-Surface Labels

- Mode: `profile_guided_compile_union_tooled`
- Registry guidance: APR-001 and APR-003 both used the starter enterprise-guidance profile.
- Expected Prolog guidance: no.
- Change: promoted the APR-008 one-off union into `scripts/union_domain_bootstrap_compiles.py`, then reran the full QA battery with `qa_failure_surface_v1` classification enabled.
- Compile surface: 219 unique admitted facts, 0 rules, 0 runtime load errors.
- Full-43 QA: 37 exact, 4 partial, 2 miss.
- Failure surfaces: 37 not applicable, 4 compile-surface gaps, 2 answer-surface gaps.
- Write proposals during QA: 0.

### Lesson

The reusable union tool reproduces APR-008's surface without reading source prose, using answer keys, or adding new interpretation. The new failure-surface scorer makes the remaining work sharper: most non-exacts need admitted rationale rows, while a smaller number are answer-surface/judge-recognition issues where normalized atoms already carry enough meaning for a human reader.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T045123776046Z_anaplan-apr010-tool-union_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T045849287928Z_qa_qwen-qwen3-6-35b-a3b.json`

## APR-011 - Executed Evidence-Bundle Plan Regression

- Mode: `profile_guided_executed_evidence_bundle_probe`
- Registry guidance: APR-010 union compile.
- Expected Prolog guidance: no.
- Change: executed only validated query templates from the LLM-authored `evidence_bundle_plan_v1` as additional query-only diagnostic evidence.
- Full-43 QA: 36 exact, 4 partial, 3 miss.
- Failure surfaces: 36 not applicable, 3 compile-surface gaps, 3 answer-surface gaps, 1 query-surface gap.
- Write proposals during QA: 0.

### Lesson

Executed evidence-bundle plans are useful diagnostics but should stay experimental. They recovered q008 in the six-question probe, but the full run regressed by adding noisy evidence to otherwise exact rows. The next useful APR move is not default plan execution; it is either narrower compile-surface acquisition for missing rationale rows or a cleaner answer-surface policy for normalized atoms that already encode the expected answer.

Artifacts:

- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T050303238601Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T051305781340Z_qa_qwen-qwen3-6-35b-a3b.json`

## APR-012 - Sparse Support-Row Acquisition Probe

- Mode: `support_acquisition_pass`
- Backbone guidance: APR-010 safe compile union.
- Expected Prolog guidance: no.
- Answer-key guidance: no.
- Change: added `scripts/run_support_acquisition_pass.py`, a separate LLM-owned source pass that sees the raw source and an already-admitted backbone surface, but may emit only support/rationale rows through the normal mapper.
- Support pass compile: 18 admitted facts, 4 skipped, 0 rules.
- Union surface: 237 facts, 0 rules, 0 runtime load errors.
- Full-43 QA: 36 exact, 4 partial, 3 miss.
- Write proposals during QA: 0.

### Lesson

The support-acquisition primitive is safe but the first sparse contract regressed the score. It admitted useful rows, but too few of the remaining rationale gaps and enough new support surface to perturb otherwise exact answers. This confirmed the design direction while rejecting the first target size: support rows belong in a separate pass, but the pass must be complete enough to cover the rationale class it claims to address.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T124546690424Z_source-support_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T124555193751Z_anaplan-apr012-support-union_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T125358899583Z_qa_qwen-qwen3-6-35b-a3b.json`

## APR-013 - Support-Row Companion Query Probe

- Mode: `support_acquisition_symbolic_access_probe`
- Backbone guidance: APR-012 support union.
- Expected Prolog guidance: no.
- Answer-key guidance: no.
- Change: when a QA query touches enterprise-guidance evidence predicates, the runtime now gathers admitted `support_reason/2`, `support_effect/2`, `support_tradeoff/3`, `support_exception/2`, and `support_positive_counterpart/2` rows as query-only companion evidence.
- Probe scope: `q004`, `q008`, `q022`, `q024`, `q026`, `q038`.
- Probe result: 2 exact, 0 partial, 4 miss.
- Write proposals during QA: 0.

### Lesson

Companion retrieval made the admitted support rows visible: `q008` and `q022` became exact on the sparse support surface. The misses showed the remaining problem was acquisition coverage, not companion retrieval. The first support pass had not captured loaded-test-model rationale, user-filter density risk, or low-complexity/high-populated-cell On-Demand Calculation support.

Artifact:

- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T125737501831Z_qa_qwen-qwen3-6-35b-a3b.json`

## APR-014 - Wider Support-Row Acquisition High-Water

- Mode: `support_acquisition_pass_plus_union`
- Backbone guidance: APR-010 safe compile union.
- Expected Prolog guidance: no.
- Answer-key guidance: no.
- Change: reran the support-acquisition pass with a larger operation target, then deterministically unioned the mapper-admitted support rows with the APR-010 backbone. The default enterprise profile was not widened.
- Support pass compile: 55 admitted facts, 6 skipped, 0 rules.
- Union surface: 274 facts, 0 rules, 0 runtime load errors.
- Hard-slice probe: 3 exact, 2 partial, 1 miss over `q004`, `q008`, `q022`, `q024`, `q026`, `q038`.
- Full-43 QA: 40 exact, 2 partial, 1 miss.
- Failure surfaces: 40 not applicable, 3 compile-surface gaps.
- Write proposals during QA: 0.

### Lesson

This is the clean APR breakthrough. The default compile should preserve the durable guidance backbone; a separate support-acquisition pass should attach reasons, effects, tradeoffs, exceptions, and positive counterparts to that backbone. Deterministic safe union then creates a stronger queryable surface without Python reading prose, without answer-key guidance, and without widening the default profile. Remaining misses are still true compile-surface gaps: summary-method blocking/memory effect, DEV-list seeding linked specifically to non-winding cyclic rejection, and low-complexity/high-populated-cell On-Demand Calculation support.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T125853927698Z_source-support_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T125900776472Z_anaplan-apr014-wide-support-union_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T130047997590Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T130928006686Z_qa_qwen-qwen3-6-35b-a3b.json`

## APR-015 - Contrast-Aware Support Acquisition Probe

- Mode: `support_acquisition_contract_tightening`
- Backbone guidance: APR-010 safe compile union.
- Expected Prolog guidance: no.
- Answer-key guidance: no.
- Change: tightened the support-pass contract generically to preserve named examples/error classes, negative mechanisms, and contrastive conditions rather than compressing them into generic rationale atoms.
- Support pass compile: 37 admitted facts, 27 skipped, 0 rules.
- Union surface: 256 facts, 0 rules, 0 runtime load errors.
- Probe scope: `q008`, `q022`, `q038`.
- Probe result: 1 exact, 2 partial, 0 miss.
- Write proposals during QA: 0.

### Lesson

This pass fixed the DEV-list rationale by preserving the named non-winding cyclic calculation error as part of the support effect. It was weaker than APR-014 on other rows, which makes the architectural lesson sharper: independent safe support views can preserve different useful rationale details. The next step is safe-surface accumulation, not picking one support pass as the winner.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T131328846950Z_source-support_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T131336861484Z_anaplan-apr015-contrast-support-union_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T131434945275Z_qa_qwen-qwen3-6-35b-a3b.json`

## APR-016 - Multi-Support Safe-Surface Accumulation

- Mode: `multi_support_safe_compile_union`
- Backbone guidance: APR-010 safe compile union.
- Expected Prolog guidance: no.
- Answer-key guidance: no.
- Change: deterministically unioned APR-010's safe backbone with the mapper-admitted support rows from APR-014 and APR-015. No source prose was read by the union tool and no new interpretation was added by Python.
- Union surface: 296 facts, 0 rules, 0 runtime load errors.
- Hard-slice probe: 5 exact, 1 partial, 0 miss over `q004`, `q008`, `q022`, `q024`, `q026`, `q038`.
- Full-43 QA: 42 exact, 1 partial, 0 miss.
- Failure surfaces: 42 not applicable, 1 compile-surface gap.
- Write proposals during QA: 0.

### Lesson

This is the strongest APR result and a broader architecture result: one perfect compile is not required. Multiple independent safe semantic views can be accumulated if every view passes the mapper and the merge is deterministic. The remaining partial is a real support gap around summary-method high-cell-count memory/blocking effects. Everything else in the 43-question enterprise-guidance battery is now exact or supported strongly enough to pass the structured judge.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T131454387229Z_anaplan-apr016-multi-support-union_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T131631440298Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T132446050930Z_qa_qwen-qwen3-6-35b-a3b.json`

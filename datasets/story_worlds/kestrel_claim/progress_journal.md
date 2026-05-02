# Kestrel Claim Progress Journal

This journal tracks Prethinker's progress on the Kestrel maritime-insurance fixture.

The fixture is intentionally harder than Iron Harbor and Blackthorn: most important rows are source-attributed, financially layered, temporally scoped, or contract-boundary sensitive. The reference KB is an oracle only and must not be used as compiler guidance for cold-score claims.

## KCL-000 - Fixture Admitted

- Integrated source story, reference KB, QA battery, strategy notes, failure buckets, and first-20 support scaffold.
- Added a non-oracle starter profile for later profile-guided experiments.
- Cold benchmark is still pending.

### Initial Hypothesis

The first cold run should be usefully bad. Expected weak spots are competing-account preservation, dual-role Harbour Mutual, cover-suspension duration, reinsurance notice/attachment interaction, salvage-security status, and multilingual technical statements.

## Evidence Lanes

Kestrel uses three labels so the results do not overclaim:

- `cold_source_profile`: raw source goes to the LLM intake/profile/compile path, with no starter registry and no expected Prolog signatures in model context.
- `source_aware_profile_review`: the LLM reviews its own proposed profile from the raw source and intake plan, still with no starter registry or expected Prolog signatures in model context.
- `profile_guided`: a pre-existing domain/starter profile is supplied. This is a legitimate product mode, but not a cold-discovery claim.

The reference `gold_kb.pl` is oracle-only. It may be used by scripts for after-the-fact signature comparison and QA scoring, but not as prompt guidance for any run reported as cold or source-aware.

## KCL-001 - Cold Source Profile Baseline

- Mode: `cold_source_profile`
- Registry guidance: none.
- Expected Prolog guidance: no.
- Compile: parsed, 20 admitted operations, 77 skipped operations.
- Profile surface: 10 candidate predicates; emitted/gold signature recall 0.000.
- First-20 QA: 5 exact, 0 partial, 15 miss.

### Lesson

The raw source-profile path recognized the domain but under-built the symbolic surface. It proposed plausible high-level predicates such as policy clauses, survey findings, claim amounts, reinsurance layers, and regulatory findings, but missed enough row classes that basic vessel, underwriter, deductible, correction, and financial-net questions failed.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T162928184931Z_story_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T163225690260Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-002 - Starter Profile Probe

- Mode: `profile_guided`
- Registry guidance: `datasets/story_worlds/kestrel_claim/ontology_registry.json`.
- Expected Prolog guidance: no.
- Compile: parsed, 71 admitted operations, 86 skipped operations.
- Profile surface: 30 candidate predicates; emitted/gold signature recall 0.035.
- First-20 QA: 14 exact, 3 partial, 3 miss.
- Full-100 QA: 38 exact, 12 partial, 50 miss.

### Lesson

A domain pack helps immediately, but this is an assisted lane. It should be used to evaluate profile-guided product behavior, not cold discovery. The jump from 5 exact to 14 exact demonstrates the value of domain packs, not autonomous ontology induction.

The full-100 result shows that a starter profile alone is not enough. It improves over source-aware KCL-007 (`38/100` exact versus `30/100` exact), but still misses half the battery. Kestrel needs stronger source-surface coverage and query support for arithmetic chains, contract boundaries, status/correction propagation, and unresolved positions.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T163457622550Z_story_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T163824400322Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T174959973157Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-003 - Source-Aware Profile Review, Before Insurance Prompt Tightening

- Mode: `source_aware_profile_review`
- Registry guidance: none.
- Expected Prolog guidance: no.
- Compile: parsed, 66 admitted operations, 70 skipped operations.
- First-20 QA: 8 exact, 5 partial, 7 miss.

### Lesson

LLM-owned profile review improves over raw cold, but only modestly without stronger general guidance about dense insurance/coverage-dispute row classes. The review found real missing capabilities, but the profile still stayed too compact for source-surface coverage.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T164226219002Z_story_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T164539201667Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-004 - General Insurance Profile Guidance

- Mode: `cold_source_profile`
- Registry guidance: none.
- Expected Prolog guidance: no.
- Change: added general insurance/coverage-dispute profile-planning guidance; no Kestrel oracle content.
- Compile: parsed, 124 admitted operations, 37 skipped operations.
- Profile surface: 25 candidate predicates; emitted/gold signature recall 0.028.
- First-20 QA: 12 exact, 5 partial, 3 miss.

### Lesson

General domain planning guidance improved source coverage substantially without using a starter registry. Remaining first-20 gaps were precise: vessel physical attributes, grounding-time correction, direct underwriter-share rows, survey methodology detail, and claimant net position.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T164945165012Z_story_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T165317186564Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-005 - Insurance Compiler Context Regression

- Mode: `cold_source_profile`
- Registry guidance: none.
- Expected Prolog guidance: no.
- Change: added general insurance/coverage-dispute compiler context.
- Compile: parsed, 62 admitted operations, 102 skipped operations.
- First-20 QA: 12 exact, 1 partial, 7 miss.

### Lesson

More context is not automatically better. The compiler context was conceptually right, but the profile bootstrap over-compressed, leaving fewer usable row classes. This mirrors earlier Blackthorn lessons: context modules need to increase row-class coverage, not crowd the control plane into a smaller schema.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T165828705291Z_story_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T170145764453Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-006 - Review-Retry JSON Discipline Failure

- Mode: `source_aware_profile_review`
- Registry guidance: none.
- Expected Prolog guidance: no.
- Compile: same profile shape as KCL-005 because the review-retry profile JSON was malformed.

### Lesson

The LLM review retry tried to put example values into an argument role name and produced invalid JSON. This exposed a control-object hygiene issue, not a semantic-insurance issue. The profile prompt now instructs the model to keep `args` as short role names and to keep values for later candidate operations.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T170620447979Z_story_qwen-qwen3-6-35b-a3b.json`

## KCL-007 - Review-Retry With JSON Hygiene

- Mode: `source_aware_profile_review`
- Registry guidance: none.
- Expected Prolog guidance: no.
- Change: added short-argument-role discipline for profile bootstrap.
- Compile: parsed, 53 admitted operations, 101 skipped operations.
- First-20 QA: 14 exact, 2 partial, 4 miss.
- Full-100 QA: 30 exact, 12 partial, 58 miss.

### Lesson

This is the best non-registry Kestrel result so far. It reached the same exact count as the starter-profile run, but with fewer partials and a thinner compile surface. The remaining failures are mostly profile/query-surface gaps: vessel attributes, insured value, underwriter share percentages, methodology explanation rows, and net-difference support.

The full-100 run is usefully bad. It confirms that first-20 improvement does not mean the whole document is solved. Stronger sections include competing survey accounts, corrections, pi exposure, and some basic financial rows. Weak sections include reinsurance temporal arithmetic, sanctions/non-breach reasoning, salvage security/payment distinction, multilingual statement details, legal citations, loss-of-hire interpretation, regulatory non-retroactivity, and comprehensive summaries.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T171021561773Z_story_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T171335753424Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T173245184797Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-008 - Starter Profile With Current Insurance Compiler Context

- Mode: `profile_guided`
- Registry guidance: `datasets/story_worlds/kestrel_claim/ontology_registry.json`.
- Expected Prolog guidance: no.
- Change: reran the same starter profile after adding the general insurance/coverage-dispute compiler context.
- Compile: parsed, 97 admitted operations, 13 skipped operations.
- First-20 QA: 16 exact, 2 partial, 2 miss.
- Full-100 QA: 48 exact, 12 partial, 39 miss, plus 1 unjudged row.

### Lesson

This is the current profile-guided high-water mark. It improves materially over KCL-002 without editing the Kestrel starter registry, so the general insurance compiler context is doing real work. The improvement was broad: it converted underwriter/dual-role details, net-claim positions, disputed claim items, reinsurance-trigger questions, regulatory non-retroactivity, financial arithmetic, multilingual witness statements, and several claim-vs-fact questions.

Regressions also matter. Narrow rows around grounding cause/time, loss-of-hire coverage, sanctions chain, policy-clause citation, class-survey scope, reinsurance late-notice effect, and some comprehensive summaries dropped. The next profile-guided move should add row-class floors for these details rather than simply increasing context volume.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T175749799414Z_story_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T180104212746Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T181745431472Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-009 - Assisted Maritime Row-Class Expansion

- Mode: `profile_guided`
- Registry guidance: expanded generic maritime-insurance starter profile.
- Expected Prolog guidance: no.
- Change: added non-oracle domain-pack row classes for loss-of-hire, P&I cover, sanctions/trading-warranty chains, class-survey scope, itemized repair-cost agreement/disagreement, reinsurance notice effect, attachment comparison, and source-detail rows.
- Compile: parsed, 117 admitted operations, 20 skipped operations.
- Profile surface: 52 candidate predicates; emitted/gold signature recall 0.049.
- First-20 QA: 17 exact, 1 partial, 2 miss.
- Full-100 QA: 61 exact, 7 partial, 32 miss.

### Lesson

This is the current profile-guided ceiling. The expanded domain pack moved the full battery from KCL-008's `48/12/39` to `61/7/32` without using the gold KB or expected answers as prompt guidance. The strongest gains came from the row classes that were intentionally made queryable: vessel value/cause rows, loss-of-hire interpretation, sanctions/trading-warranty defenses, legal citations, cargo/charter facts, P&I structure, reinsurance late-notice effect, and comprehensive disputed-item summaries.

The remaining misses are now sharper. They cluster around query-time temporal arithmetic (`72`-hour notice deltas), exact suspension/condition-of-class windows, navigation/source-detail distinctions, repair-cost agreement sets, survey/class non-findings, P&I exposure totals, and richer chronological event summaries. This looks less like "the compiler cannot understand Kestrel" and more like the runtime/query layer still needs better support bundles for arithmetic, negative/absence facts, and multi-row summaries.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T182613198722Z_story_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T182931559082Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T184627103331Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-010 - Overwide Assisted Profile Regression

- Mode: `profile_guided`
- Registry guidance: temporarily expanded generic maritime-insurance starter profile beyond KCL-009.
- Expected Prolog guidance: no.
- Change: added further row classes for explicit CoC/cover windows, regulatory directives, voyage events, expert comparisons, P&I exposure items, value estimates, and recommendations.
- Compile: parsed, 88 admitted operations, 48 skipped operations.
- Profile surface: 64 candidate predicates; emitted/gold signature recall 0.049.
- First-20 QA: 16 exact, 2 partial, 2 miss.
- Full-100 QA: not run.

### Lesson

This is a negative control. The added row classes were conceptually relevant, but the profile became too wide and the compiler admitted fewer rows with more skips. The first-20 slice regressed from KCL-009's `17/1/2` to `16/2/2`, so the full battery was intentionally not run. This repeats the Blackthorn/Kestrel lesson: useful domain-pack context must create row-class coverage, not a larger menu. The active registry was backed down to the KCL-009 shape after recording this run.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T185554690932Z_story_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T185901718524Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-011 - Source-Aware Row-Class Example Regression

- Mode: `source_aware_profile_review`
- Registry guidance: none.
- Expected Prolog guidance: no.
- Change: temporarily added generic maritime-insurance row-class examples to the LLM-owned profile-planning guidance.
- Compile: parsed, 158 admitted operations, 92 skipped operations.
- Profile surface: 11 candidate predicates; emitted/gold signature recall 0.000.
- First-20 QA: 14 exact, 1 partial, 5 miss.
- Full-100 QA: not run.

### Lesson

This did not close the cold/source-aware to assisted gap. The LLM admitted many rows but compressed the profile to only `11` predicate families, so query usefulness did not improve over KCL-007 and partial coverage got worse. The negative result is important: transferring KCL-009's row-class vocabulary into source-aware profile discovery as prose examples is not enough, and may make the control plane choose broad catch-all predicates. The active source-aware guidance was backed down after recording this run.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T190628306219Z_story_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T191000176774Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-012 - Maritime QA Query Strategy

- Mode: `profile_guided_qa_requery`
- Registry guidance: same KCL-009 compiled KB; no source recompile.
- Expected Prolog guidance: no.
- Change: added generic maritime-insurance QA query strategy for financial rows, H&M versus P&I cover, reinsurance late-notice effects, legal citations, trading-warranty chains, surveyor agreement/disagreement, witness counts, and LOH calculation support.
- Compile: reused KCL-009 (`117` admitted operations, `20` skipped operations).
- Full-100 QA: 61 exact, 13 partial, 26 miss.

### Lesson

This did not raise the exact count, but it improved support retrieval: KCL-009's `61/7/32` became `61/13/26`. Several previous misses became exact or partial, including net-difference, H&M suspension timing, trading-warranty status, Ashworth finding-vs-observation, reinsurance late notice, cost-agreement questions, and surveyor-disagreement support.

The regressions are instructive. Some simple witness/defense questions became overconstrained when the query planner chose the wrong role constant or skipped a known answer-bearing predicate. A small follow-up restored several targeted regressions, but q039 still shows a predicate-contract problem: `trading_warranty_status/4` can carry party intent in a long detail/source slot, and the planner keeps binding that slot too tightly. The next durable fix is probably a profile/contract shape or a query-review pass, not more prose guidance.

Artifacts:

- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T220745183042Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T221146199699Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-013 - Query-Review And Role-Named Evidence Companions

- Mode: `profile_guided_qa_requery`
- Registry guidance: same KCL-009 compiled KB; no source recompile.
- Expected Prolog guidance: no.
- Change: added deterministic query-review over already structured Prolog queries. Lowercase generic slot labels such as `language`, `amount`, `currency`, `step`, and `note` are repaired into variables; table-like evidence predicates get role-named companion queries such as `trading_warranty_status(Policy, Subject, Status, Detail)`.
- Compile: reused KCL-009 (`117` admitted operations, `20` skipped operations).
- Full-100 QA: 63 exact, 11 partial, 26 miss.

### Lesson

This is a small but important runtime/query-surface gain. The patch did not inspect source prose or answers; it only corrected the LLM's structured query shape before Prolog execution. It converted failures such as `witness_statement(..., language, ...)` into real variable queries and made q039 exact by surfacing the normalized detail atom `oceanic_does_not_intend_to_raise_the_defense...` instead of treating the fourth `trading_warranty_status/4` slot as a party-only column.

The gain is modest because many remaining misses are compile-surface gaps rather than query-shape problems. The KB still lacked enough source detail for notice arithmetic, itemized repair-cost statements, witness quantitative details, and claims-handler non-acceptance/reservation statements.

Artifacts:

- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T002317659453Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-014 - Insurance Detail Compile Surface

- Mode: `profile_guided`
- Registry guidance: same non-oracle maritime-insurance starter profile.
- Expected Prolog guidance: no.
- Change: strengthened generic insurance compiler context for deadline anchors, notice windows, cover-suspension windows, claim-handler acceptance/reservation statements, witness quantitative details, and source-owned detail rows.
- Compile: parsed, 170 admitted operations, 73 skipped operations.
- First-20 QA: 18 exact, 1 partial, 1 miss.
- Full-100 QA: 67 exact, 12 partial, 21 miss.

### Lesson

This confirms the remaining Kestrel ceiling was partly compile-surface coverage. The new compile added useful rows for P&I exposure, cargo damage, condition-of-class timing, class-survey scope, late-notice effect, separate H&M/P&I contract roles, and some source-detail records. It also regressed some prior witness/language rows, proving that one dense compile can preserve one slice while dropping another.

The lesson is not to blindly make prompts longer. The better pattern is complementary safe compiles with deterministic admitted-clause union, provided all runs remain in the same evidence lane and the mapper admits every clause independently.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T003525050762Z_story_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T003910991415Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T005753489591Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-015 - Deterministic Admitted-Clause Union

- Mode: `profile_guided_union`
- Registry guidance: KCL-009 plus KCL-014, both profile-guided and non-oracle.
- Expected Prolog guidance: no.
- Change: deterministic union of mapper-admitted facts from two safe source compiles of the same document. Python did not inspect source prose, question text, answers, or gold KB; it only deduplicated admitted Prolog clauses.
- Union KB: 274 unique admitted facts, 0 rules.
- First-20 QA: 20 exact, 0 partial, 0 miss.
- Full-100 QA: 72 exact, 10 partial, 18 miss.

### Lesson

This is the strongest Kestrel architectural result so far. KCL-009 preserved witness and some broad coverage that KCL-014 dropped; KCL-014 preserved insurance-detail rows that KCL-009 lacked. The deterministic union recovered both without weakening the authority boundary. This suggests a general product/research pattern: repeated LLM compiles can be treated as complementary extraction passes when each candidate clause still goes through the same mapper firewall and the merged KB is audited for conflicts.

This should remain labeled as profile-guided union evidence, not cold discovery. It is legitimate product-mode context engineering, but it is not a claim that a single cold pass discovered the full domain.

Artifacts:

- `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T005830000000Z_story_kcl_union_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T010345602750Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T012543732789Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-016 - Source-Faithful Temporal Atom Runtime

- Mode: `profile_guided_union_runtime_temporal`
- Registry guidance: same KCL-015 union KB; no source recompile.
- Expected Prolog guidance: no.
- Change: extended the deterministic temporal runtime to parse admitted timestamp atoms such as `october_15_2025_08_00_utc`, `oct_2_2025`, and `2025_10_12t03_17_00z`. This is KB-term parsing, not source-prose interpretation.
- Full-100 QA: 73 exact, 11 partial, 16 miss.

### Lesson

Temporal helpers were too brittle for source-faithful timestamp atoms. Once the runtime could understand month-name atoms and timestamp atoms with seconds/UTC suffixes, joined support queries such as `cover_suspension(...), elapsed_days(Start, End, Days)` began to work. q027 moved to exact on the targeted slice, and the full battery reached the current high-water `73/11/16`.

The remaining misses now cluster around missing source detail or harder arithmetic/summary reasoning: navigation-position enumeration, AIS/depth details, pollution-plan deadline basis, 72-hour reinsurance deltas with the correct awareness anchor, itemized surveyor cost disagreements, witness/expert count completeness, post-repair value, survey-schedule effects, Cotonou cancellation timing, and hypothetical share arithmetic.

Artifacts:

- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T012831205571Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T015030503386Z_qa_qwen-qwen3-6-35b-a3b.json`

## KCL-017 - Post-Run Failure-Surface Classification

- Timestamp: `2026-05-02T05:18:59Z`
- Mode: `post_run_failure_surface_classification`
- QA artifact classified: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T015030503386Z_qa_qwen-qwen3-6-35b-a3b.json`
- Classified artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T015030503386Z_qa_qwen-qwen3-6-35b-a3b_failure_surface_20260502T051859206593Z.json`
- Baseline score preserved: `73 exact / 11 partial / 16 miss`
- Classified non-exacts: 27
- Failure surfaces: 20 compile-surface gaps, 4 query-surface gaps, 3 hybrid-join gaps.

### Lesson

Kestrel is still mostly bottlenecked on source-surface preservation, not answer rendering. The useful next Kestrel compile work is to preserve more admitted rows for navigation positions, witness statements, DAM/regulatory timing, survey cost agreements/disagreements, P&I period boundaries, and specific cost/financial items. The query surface still matters, but the post-run classifier says the bigger remaining frontier is compile coverage.

## KCL-018 - Evidence-Bundle Context Filter Probe

- Timestamp: `2026-05-02T07:02:29Z`
- Mode: `evidence_bundle_context_filter_broad_floor_probe`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T005830000000Z_story_kcl_union_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T070229264766Z_qa_qwen-qwen3-6-35b-a3b.json`
- Probe scope: the 27 KCL-017 non-exact rows from KCL-016.
- Result: 4 exact, 9 partial, 14 miss.
- Converted rows: `q037`, `q055`, `q076`, `q088`.
- Failure surfaces after the probe: 16 compile-surface gaps, 7 hybrid-join gaps.

### Lesson

The broad-floor context filter transfers to Kestrel but only modestly. It can rescue query-surface rows such as retroactivity, witness statement, P&I period, and accepted-amount questions, but the fixture remains dominated by missing admitted source rows. Kestrel's next high-leverage move is better compile-surface preservation, not a wider QA planner.

## KCL-019 - Row-Class Focused Compile Union Probe

- Timestamp: `2026-05-02T07:36:25Z`
- Mode: `profile_guided_rowclass_compile_union_probe`
- New compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T071629254933Z_story_qwen-qwen3-6-35b-a3b.json`
- Union artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260502T072319175776Z_kcl019-rowclass-union_qwen-qwen3-6-35b-a3b.json`
- QA probe artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260502T073625383617Z_qa_qwen-qwen3-6-35b-a3b.json`
- Change: added non-oracle focused-pass floors for source positions, operational timeline, itemized finance, statement census, and authority/deadline rows, then unioned that safe admitted surface with KCL-015.
- Union KB: 382 unique admitted facts, 0 rules, 0 runtime load errors.
- Probe scope: same 27 KCL-017 non-exact rows.
- Result: 5 exact, 10 partial, 12 miss.
- Converted rows: `q037`, `q055`, `q063`, `q076`, `q095`.
- Failure surfaces after the probe: 13 compile-surface gaps, 9 hybrid-join gaps.

### Lesson

The row-class floors are directionally correct but not enough by themselves. The new surface recovered survey-scope and statement-census support (`q063`, `q095`) and lowered compile-surface gaps on the weak slice from 16 to 13, but Kestrel still needs stronger source-surface preservation for navigation positions, itemized repair/cost disagreements, operational chronology, sanctions timing, and conditional financial arithmetic. A full-100 run is not yet worth the GPU time until the weak slice moves more decisively.

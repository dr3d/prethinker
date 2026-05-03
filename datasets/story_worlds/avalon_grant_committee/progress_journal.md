# Avalon Grant Committee Progress Journal

## Fixture Admission - AG-000

- Timestamp: `2026-05-03`
- Source: `tmp/The Avalon Grant Committee`
- Files admitted: source document plus 40-question JSON QA battery.
- Gold KB: none supplied.
- Starter ontology/profile: none supplied.
- Benchmark runs: none yet.

### Purpose

This fixture is intended to test governed compilation of grant-committee rules
where eligibility, formal interpretation authority, exceptions, corrections,
appeals, quorum, recusal, conditional approvals, and counterfactuals interact.

### Initial Research Hypothesis

The first useful baseline should separate at least six surfaces:

- source-stated eligibility rules and exceptions;
- applicant records, prior grants, and project components;
- committee meetings, votes, recusal, quorum, and replacement authority;
- formal interpretations versus committee decisions;
- conditional approval requirements, deadlines, and satisfaction evidence;
- appeal chain and finality.

No run has been executed at admission time.

## Run AG-001 - Cold Semantic Parallax Baseline

- Timestamp: `2026-05-03T14:21Z` through `2026-05-03T14:36Z`
- Evidence lane: `cold_unseen`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only profile bootstrap plus current semantic-parallax compile:
  flat-plus-focused intake-plan passes, compact focused-pass operations schema,
  and LLM-authored source entity ledger. No gold KB, starter registry, strategy
  file, or QA source was used during compilation.

### Artifacts

- Compile:
  `tmp/cold_baselines/avalon_grant_committee/domain_bootstrap_file_20260503T142117952071Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/avalon_grant_committee/domain_bootstrap_qa_20260503T143610001875Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: `114` admitted operations, `6` skips, `109` unique facts, `0`
  rules.
- Profile rough score: `0.889` with `30` candidate predicates.
- QA: `25 exact / 12 partial / 3 miss` over `40` questions.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `11` compile-surface gaps, `2` query-surface gaps, `2`
  hybrid-join gaps.

### Lesson

Avalon lands in the desired fixture difficulty band. The baseline is strong
enough to show transfer from prior governance fixtures, but still exposes the
rule-composition frontier. The source compile preserved useful eligibility,
interpretation, correction, quorum, and appeal rows, but admitted no executable
rules. The remaining non-exacts cluster around NYA deferral detail, Petrov
conditional/matching-fund reasoning, Bianchi/SCLT recusal and replacement
mechanics, eligible-category enumeration, Worthington's German ambiguity remark,
and counterfactual procedure. This is a good target for the next pass: acquire
body facts and executable rules without using the answer key or starter
registry.

## Run AG-002 - Section A Rule-Lens Diagnostic Replay

- Timestamp: `2026-05-03T14:44Z`
- Evidence lane: `diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: Section A rule-acquisition lens over the AG-001 mapper-admitted
  backbone. The active predicate registry was derived from AG-001's own
  source-only candidate profile and stored only as a temporary replay artifact;
  no gold KB, starter profile, QA answer key, or reference rule surface was
  used.

### Artifacts

- Temporary registry:
  `tmp/cold_baselines/avalon_grant_committee/source_derived_registry_ag001.json`
- Rule replay:
  `tmp/cold_baselines/avalon_grant_committee/rules/domain_bootstrap_file_20260503T144419947611Z_story-rules_qwen-qwen3-6-35b-a3b.json`

### Result

- Rule lens: `8` admitted rule clauses, `3` skips, `0` facts.
- Runtime trial: `1` firing rule, `1` promotion-ready rule, `0` runtime rule
  errors.
- Verifier diagnostics: `5` unsupported body goals, `3` unsupported body
  signatures, and `4` unsupported body fragments.

### Lesson

Avalon reproduces the Glass Tide rule-acquisition shape: a narrow rule lens can
create executable rules, but promotion depends on body support and helper-shape
discipline. The useful firing rule was the Rule 3 individual plus
for-profit-representative branch for `app3`. The matching-fund rule exposed a
general verifier gap: the LLM wrote `value_greater_than(Amount, 25000)` and
`value_at_most(Match, 0.3 * Amount)`, using numeric measure variables where
the deterministic helper contract requires an entity argument and a literal
threshold. The verifier now flags both the measure-variable misuse and computed
threshold expression. The expiry rule also remains blocked on unsupported
negation (`\+`). The next structural need is still body-fact/helper acquisition
for rule families, not broader prose pressure.

## Run AG-003 - Rule 5 Ratio Helper Lens

- Timestamp: `2026-05-03T14:59Z`
- Evidence lane: `diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: narrow Rule 5 threshold lens over the AG-001 backbone. This replay used
  a source-derived temporary predicate registry plus a restricted active
  predicate filter for applicant IDs, requested amounts, matching-fund
  commitments, numeric helpers, percentage helpers, and derived conditions.
  No QA answer key or reference Prolog was used.

### Artifact

- Rule replay:
  `tmp/cold_baselines/avalon_grant_committee/rules/domain_bootstrap_file_20260503T145941969433Z_story-rules_qwen-qwen3-6-35b-a3b.json`

### Result

- Rule lens: `4` admitted rule clauses, `0` skips, `0` facts.
- Runtime trial: `3` firing rules, `3` promotion-ready rules, `0` runtime rule
  errors.
- Unsupported body surface: `2` unsupported body goals, `0` unsupported body
  fragments.

### Lesson

Rule 5 needed helper substrate, not a broader prompt. Adding generic
`number_greater_than/2`, `number_at_most/2`, `percent_at_least/3`, and
`percent_below/3` lets the rule lens express threshold and ratio branches
without abusing entity-value helpers. The run also exposed and fixed a runtime
bug: repeated anonymous variables (`_`) were being treated as the same variable
inside a rule, which prevented otherwise valid ratio rules from firing. After
fixing anonymous-variable semantics, the threshold-exceeded and ratio-met rules
became promotion-ready. The ratio-failed branch remained dormant because the
current admitted data has no below-30-percent case, which is correct dormancy
rather than verifier failure.

## Run AG-004 - AG-001 plus Rule 5 Ready-Rule Union QA

- Timestamp: `2026-05-03T15:01Z` through `2026-05-03T15:10Z`
- Evidence lane: `diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: deterministic union of the AG-001 cold compile and AG-003 Rule 5
  promotion-ready rules, followed by the same 40-question QA runner. The union
  read no source prose and inferred no new clauses; it only kept
  mapper-admitted facts plus promotion-ready rules.

### Artifacts

- Union:
  `tmp/cold_baselines/avalon_grant_committee/union/domain_bootstrap_file_20260503T150150892550Z_avalon-ag001-plus-rule5-ready_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/avalon_grant_committee/union/domain_bootstrap_qa_20260503T151019375682Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Union surface: `109` facts, `3` rules, `0` runtime load errors.
- QA: `27 exact / 8 partial / 5 miss` over `40` questions.
- Safety: `40/40` parsed, `0` write-proposal rows, `0` runtime load errors.
- Verdict deltas versus AG-001: exact improvements on q007, q011, q025, and
  q030; regressions on q003, q008, and q020.

### Lesson

Rule accumulation helped some rows but is not yet safe as a blind global
default. The added Rule 5 surface improved matching-fund and recusal-adjacent
answers, but it also perturbed query planning for a few rows where the answer
needed source-detail or deadline evidence rather than the new derived rules.
This confirms the APR lesson in a rule setting: the right architecture is not
"always add more admitted surface"; it is row-level activation, fallback
selection, or answer-mode protection over a safely accumulated surface.

## Run AG-005 - Rule Mapper Control-Construct Gate

- Timestamp: `2026-05-03T17:07Z` through `2026-05-03T17:09Z`
- Evidence lane: `diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: replay of the Section A eligibility-rule lens after adding the Sable
  backbone fact-signature support summary and then tightening durable rule
  mapper admission against raw Prolog control constructs. The replay used the
  AG-001 source-only backbone and source-derived temporary registry; no gold
  KB, starter profile, QA answer key, or reference rule surface was used.

### Artifacts

- Pre-gate replay:
  `tmp/cold_baselines/avalon_grant_committee/rules/domain_bootstrap_file_20260503T170704687082Z_source-rules_qwen-qwen3-6-35b-a3b.json`
- Post-gate replay:
  `tmp/cold_baselines/avalon_grant_committee/rules/domain_bootstrap_file_20260503T170921665371Z_source-rules_qwen-qwen3-6-35b-a3b.json`

### Result

- Pre-gate replay: `8` admitted executable rules, `0` skips, `2`
  promotion-ready rules, `1` unsupported body goal, and `5` unsupported body
  fragments.
- Post-gate replay: `3` admitted executable rules, `5` skips, `2`
  promotion-ready rules, `0` unsupported body goals, and `0` unsupported body
  fragments.
- The retained firing rules were the helper-composed Rule 5 matching-fund
  branches:

```prolog
derived_status(Applicant, matching_funds_met, rule_5) :-
    applicant_id(Applicant, _Name),
    requested_amount(Applicant, Amount),
    number_greater_than(Amount, 25000),
    matching_fund_commitment(Applicant, Match, _Source),
    percent_at_least(Match, Amount, 30).

derived_status(Applicant, matching_funds_exempt, rule_5) :-
    applicant_id(Applicant, _Name),
    requested_amount(Applicant, Amount),
    number_at_most(Amount, 25000).
```

### Lesson

The Sable support-summary improvement transfers to Avalon, but the more
important general fix is the mapper-side control-construct gate. Durable
candidate rules are now skipped when they use raw negation, disjunction, lists,
arithmetic, equality, or comparison operators. Those constructs must be
represented through deterministic helper predicates or later explicit support
substrates. This moves non-helper branches out of the admitted-rule surface
instead of relying only on the promotion verifier to mark them non-promotable.

## Run AG-006 - Post-Gate Rule Union QA

- Timestamp: `2026-05-03T17:12Z` through `2026-05-03T17:20Z`
- Evidence lane: `diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: deterministic union of AG-001 and the post-gate AG-005
  promotion-ready rules, followed by the same 40-question QA runner. The union
  read no source prose, inferred no new clauses, and kept only
  promotion-ready rules from the rule-lens artifact.

### Artifacts

- Union:
  `tmp/cold_baselines/avalon_grant_committee/union/domain_bootstrap_file_20260503T171222999543Z_avalon-ag001-plus-postgate-rules_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/avalon_grant_committee/union/domain_bootstrap_qa_20260503T172017844591Z_qa_qwen-qwen3-6-35b-a3b.json`
- Mode comparison:
  `tmp/cold_baselines/avalon_grant_committee/union/avalon_rule_union_mode_comparison.md`

### Result

- Union surface: `109` facts, `2` rules, `0` runtime load errors.
- QA: `27 exact / 10 partial / 3 miss` over `40` questions.
- Compared with AG-004's older rule union, the post-gate union kept the same
  exact count while reducing misses from `5` to `3`.
- Compared with AG-001 baseline, rule-union modes rescue `5` baseline
  non-exact rows but can still regress `2` baseline-exact rows.
- Diagnostic perfect-selector upper bound across baseline, old rule union, and
  post-gate rule union: `29 exact / 9 partial / 2 miss`.

### Lesson

Mapper-side rule hygiene reduces harmful rule-surface perturbation but does not
solve row-level selection. Safe accumulated rule surfaces are useful, yet global
activation can still shift query planning. The next general mechanism should
activate alternate evidence/rule surfaces only when pre-judge structural signals
show near-miss risk, while preserving baseline-like rows that already have
strong direct evidence.

## Run AG-007 - Non-Oracle Evidence Mode Selector

- Timestamp: `2026-05-03T18:46Z`
- Evidence lane: `diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: LLM-owned selector over three already-executed QA evidence modes:
  baseline, post-gate rule union, and focused evidence-context QA.

### Method

New selector harness:

```text
scripts/select_qa_mode_without_oracle.py
```

The selector receives only:

```text
question
mode labels
planned queries
executed query results
small structured row samples
```

It does **not** receive:

```text
source prose
answer key
reference answer
judge label
failure-surface label
gold KB
```

Python packages structured evidence and scores the selected mode after the
selection. It does not interpret source language or derive answers.

### Artifacts

- Focused-context full QA:
  `tmp/cold_baselines/avalon_grant_committee/selector_probe_full/domain_bootstrap_qa_20260503T183704170227Z_qa_qwen-qwen3-6-35b-a3b.json`
- Three-mode comparison:
  `tmp/cold_baselines/avalon_grant_committee/selector_probe_full/avalon_query_modes_comparison.md`
- Selector run:
  `tmp/cold_baselines/avalon_grant_committee/selector_probe_full/selector_full_sample16.json`
- Selector report:
  `tmp/cold_baselines/avalon_grant_committee/selector_probe_full/selector_full_sample16.md`

### Result

Mode scores:

```text
baseline:             25 exact / 12 partial / 3 miss
postgate_rule_union:  27 exact / 10 partial / 3 miss
focused_context:      29 exact /  7 partial / 4 miss
```

Diagnostic perfect-selector upper bound:

```text
32 exact / 7 partial / 1 miss
```

Non-oracle selector result:

```text
31 exact / 7 partial / 2 miss
selected best available mode on 38/40 rows
selector errors: 0
write proposals: 0
```

The first selector pass used only five sampled rows per query result and scored
`28 exact / 9 partial / 3 miss`. Widening the structured evidence sample to
sixteen rows fixed hidden-support failures on wide result tables and raised the
selector to `31 exact`.

### Lesson

AG-007 is the first strong row-level activation result. Safe accumulated
surfaces do not need to be globally activated. A separate selector can choose
among already-executed query-evidence modes without reading the answer key or
source document.

This turns the earlier perfect-selector measurement into a plausible runtime
shape:

```text
compile surface A
compile/rule/query surface B
focused evidence surface C
  -> strip oracle/judge/source fields
  -> LLM selector chooses evidence mode
  -> answer from selected support bundle
```

The remaining misses are informative:

- `q003`: the phrase "why was the decision deferred" is scope-ambiguous between
  the procedural quorum/recusal reason and the substantive Rule 2 dispute.
- `q011`: the selector overvalued extra direct quorum evidence and undervalued
  the more answer-complete rule text bundle.

Those failures point to selector calibration, not unsafe admission. The
architecture gain is that row-level activation can be model-owned while the
truth boundary remains unchanged.

## Run AG-008 - Selector Policy Calibration Check

- Timestamp: `2026-05-03T19:44Z`
- Evidence lane: `diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: selector-policy replay over the AG-007 evidence modes.

### Result

The stable direct-evidence policy replayed at:

```text
30 exact / 9 partial / 1 miss
selected best available mode on 38/40 rows
selector errors: 0
```

The experimental completeness-first policy plus QA self-check notes replayed at:

```text
27 exact / 9 partial / 2 miss
2 selector errors
```

### Lesson

Selector calibration is now a real harness surface. The completeness-first
policy helped Black Lantern, but it is not a safe default because it regressed
Avalon. The selector harness now exposes:

```text
--selection-policy direct|completeness
--include-self-check
```

The default remains direct evidence over broad relaxed fallbacks. Completeness
and self-check notes are research dials, not baseline behavior.

## Run AG-009 - Rule 2 Exception Lens and Global-Union Regression

- Timestamp: `2026-05-03T19:52Z`
- Evidence lane: `diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: narrow Rule 2 prior-funding rule lens over the AG-001 backbone.

### Method

The lens was constrained to simple conjunctions over:

```text
applicant_id/2
prior_grant_history/4
derived_status/3
```

It was explicitly blocked from text-atom search, fiscal-year atom comparison,
negation, equality, arithmetic, lists, disjunction, and derived-condition body
goals.

### Result

The successful run admitted `3` executable rules:

```prolog
derived_status(Applicant, ineligible, prior_funding) :-
    applicant_id(Applicant, _Name),
    prior_grant_history(Applicant, _FY, _Amt, used_in_full).

derived_status(Applicant, ineligible, prior_funding) :-
    applicant_id(Applicant, _Name),
    prior_grant_history(Applicant, _FY, _Amt, partial_return).

derived_status(Applicant, eligible, prior_funding_reset) :-
    applicant_id(Applicant, _Name),
    prior_grant_history(Applicant, _FY, _Amt, returned_unused).
```

Verifier result:

```text
promotion-ready rules: 2
firing rules: 2
positive probes: 3/3
negative probes: 2/2
unsupported body goals: 1
```

The unsupported reset branch is correctly visible because the backbone has no
`returned_unused` row.

Unioning only the promotion-ready Rule 2 rules into AG-001 produced:

```text
25 exact / 10 partial / 5 miss
```

compared with the baseline:

```text
25 exact / 12 partial / 3 miss
```

The rule surface rescued `q010`, `q025`, and `q030`, but regressed `q003`,
`q007`, `q008`, and `q020`. A two-mode selector over baseline and Rule2-union
selected:

```text
25 exact / 11 partial / 4 miss
```

### Lesson

This is a rule-ingestion win and a global-activation loss. The rule lens can
now acquire a source-faithful, helper-free exception branch that passes
positive and negative probes, but globally unioning even promotion-ready rules
can still perturb answer planning.

Rule promotion needs a second decision:

```text
promotion-ready for runtime
!=
activate for every question
```

The next activation policy should know whether a question actually needs the
derived rule surface before allowing it to displace baseline evidence.

## Run AG-010 - Relevance-First Selector Probe

- Timestamp: `2026-05-03T20:09Z`
- Evidence lane: `diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: experimental selector posture that scores entity/scope relevance before
  evidence directness.

### Result

On the Rule2-only two-mode comparison:

```text
25 exact / 12 partial / 3 miss
selected best available mode on 38/40 rows
```

This recovered `q010` relative to the direct selector but still wrongly
activated the Rule2 surface for `q020` and missed the `q030` partial rescue.

On the full three-mode Avalon selector replay:

```text
30 exact / 8 partial / 2 miss
selected best available mode on 37/40 rows
selector errors: 0
```

### Lesson

Relevance-first selection names a real failure mode: direct evidence can be
about the wrong subject or neighboring rule. But it is not a replacement for
the direct selector. It shifts which rows fail rather than closing the
selector gap.

## Run AG-011 - Rule 8 Explicit-Condition Aliasing Diagnostic

- Timestamp: `2026-05-03T23:17Z` through `2026-05-03T23:18Z`
- Evidence lane: `diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: Rule 8 conditional-approval temporal/status lens over the AG-001
  backbone.

### Artifacts

- List-membership attempt:
  `tmp/cold_baselines/avalon_grant_committee/rules/domain_bootstrap_file_20260503T231748462003Z_source-rules_qwen-qwen3-6-35b-a3b.json`
- Explicit-condition attempt:
  `tmp/cold_baselines/avalon_grant_committee/rules/domain_bootstrap_file_20260503T231838103927Z_source-rules_qwen-qwen3-6-35b-a3b.json`
- Post-run shortcut audit:
  `tmp/diagnostic_replays/avalon_rule8_shortcut_audit_post_aliasing_guard.json`

### Result

The first Rule 8 pass emitted plausible rules, but `0` were admitted. The
mapper correctly skipped `5` candidates that depended on `member/2` and `1`
candidate that depended on negation/comparison control constructs.

The second pass blocked list membership and negation in the context. It admitted
`1` executable rule:

```prolog
derived_status(Applicant, conditionally_eligible, rule_8) :-
    conditional_approval(Applicant, Conditions),
    deadline_requirement(Applicant, Cond1, Deadline),
    deadline_requirement(Applicant, Cond2, Deadline),
    deadline_met(Applicant, Cond1),
    deadline_met(Applicant, Cond2).
```

Verifier result:

```text
promotion-ready rules: 1
firing rules: 1
negative probes: 2/2
positive probes: 0/2
runtime errors: 0
unsupported body goals: 0
```

The upgraded semantic shortcut audit then flagged the admitted rule with
`repeated_body_aliasing_risk`: the two `deadline_requirement/3` goals share
`Applicant` and `Deadline` but do not anchor `Cond1` and `Cond2` to distinct
literal requirement atoms. The rule can therefore satisfy a two-condition
requirement with the same admitted row twice.

### Lesson

This is the first clean Avalon example of a rule that is syntactically safe,
body-supported, firing, and still semantically underconstrained. Rule
composition over multiple required conditions needs one of these structural
supports:

```text
literal condition anchors in the rule body
or a deterministic all_required_conditions_met/1 helper
or a separate body-fact lens that emits required_condition/2 rows
```

The new shortcut-audit risk is structural and does not inspect source prose. It
looks only at repeated body-goal shapes that can alias when a rule is trying to
represent distinct requirements.

## Run AG-012 - Body-Fact Anchors Rescue Rule 8 Composition

- Timestamp: `2026-05-03T23:22Z` through `2026-05-03T23:25Z`
- Evidence lane: `diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: body-fact acquisition plus Rule 8 rule lens over the AG-001 backbone.

### Artifacts

- First body-fact attempt:
  `tmp/cold_baselines/avalon_grant_committee/support/domain_bootstrap_file_20260503T232259999645Z_source-support_qwen-qwen3-6-35b-a3b.json`
- Atom-aligned body-fact attempt:
  `tmp/cold_baselines/avalon_grant_committee/support/domain_bootstrap_file_20260503T232355724065Z_source-support_qwen-qwen3-6-35b-a3b.json`
- Backbone plus aligned body facts:
  `tmp/cold_baselines/avalon_grant_committee/union/domain_bootstrap_file_20260503T232406484376Z_avalon-ag001-plus-aligned-required-conditions_qwen-qwen3-6-35b-a3b.json`
- Rule lens:
  `tmp/cold_baselines/avalon_grant_committee/rules/domain_bootstrap_file_20260503T232444595365Z_source-rules_qwen-qwen3-6-35b-a3b.json`
- Deterministic rule union:
  `tmp/cold_baselines/avalon_grant_committee/union/domain_bootstrap_file_20260503T232509486037Z_avalon-rule8-bodyfact-rule-union_qwen-qwen3-6-35b-a3b.json`

### Result

The new body-fact lens predicate `required_condition/2` gives rule composition
an explicit support surface for multi-condition rules. The first pass admitted
`3` rows but chose richer source-detail atoms that did not align with the
existing `deadline_met/2` body facts. The aligned replay admitted exactly the
two body rows needed by Rule 8:

```prolog
required_condition(anya_petrov, submit_revised_budget).
required_condition(anya_petrov, provide_matching_docs).
```

With those rows unioned into the backbone, the Rule 8 lens admitted `4`
executable rules, all firing and promotion-ready. The main composed rule was:

```prolog
derived_status(Subject, conditional_approved, rule_8) :-
    required_condition(Subject, submit_revised_budget),
    required_condition(Subject, provide_matching_docs),
    deadline_met(Subject, submit_revised_budget),
    deadline_met(Subject, provide_matching_docs).
```

Runtime result:

```text
admitted rules: 4
promotion-ready rules: 4
firing rules: 4
runtime errors: 0
unsupported body goals: 0
semantic shortcut findings: 0
```

The deterministic union replay over the aligned body-fact surface passed:

```text
positive probes: 4/4
negative probes: 2/2
probe-adjusted promotion ready: true
```

### Lesson

AG-012 is the positive counterpart to AG-011. The rule lens did not need a
cleverer prompt; it needed an explicit body-fact acquisition step that pinned
the condition atoms used by later rule bodies. Multi-condition rule composition
now has a repeatable pattern:

```text
body-fact lens -> aligned required_condition rows
rule lens -> literal condition anchors
shortcut audit -> no repeated-body aliasing
deterministic union -> positive/negative probes
```

The first body-fact attempt also shows a new alignment frontier: support/body
rows must be source-faithful and atom-compatible with admitted body predicates.
Pretty source-detail atoms are less useful than boring atoms that let rules
join safely.

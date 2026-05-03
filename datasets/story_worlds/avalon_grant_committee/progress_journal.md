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

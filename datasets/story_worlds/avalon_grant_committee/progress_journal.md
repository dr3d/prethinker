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

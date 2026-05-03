# Ridgeline Fire Progress Journal

## Fixture Admission - RF-000

- Timestamp: `2026-05-03`
- Source: `tmp/The Ridgeline Fire`
- Files admitted: source document plus 40-question JSON QA battery.
- Gold KB: none supplied.
- Starter ontology/profile: none supplied.
- Benchmark runs: none yet.

### Purpose

This fixture is intended to test governed compilation of an incident-command
record where rules, deadlines, authority boundaries, exclusions, corrections,
claims, and counterfactual policy violations all interact.

### Initial Research Hypothesis

The first useful baseline should separate at least five surfaces:

- standing-order rules and deadlines;
- incident-event timeline and authoritative correction targets;
- role/authority facts for IC, Air Ops, and Emergency Manager;
- WUI/non-WUI zone membership and exclusion rows;
- violation candidates versus documented context or non-violations.

No run has been executed at admission time.

## Run RF-001 - Cold Semantic Parallax Baseline

- Timestamp: `2026-05-03T05:09Z` through `2026-05-03T05:19Z`
- Evidence lane: `cold_unseen`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only profile bootstrap plus current semantic-parallax compile:
  flat-plus-focused intake-plan passes, compact focused-pass operations schema,
  and LLM-authored source entity ledger. No gold KB, starter registry, or QA
  source was used during compilation.

### Artifacts

- Compile:
  `tmp/cold_baselines/ridgeline_fire/domain_bootstrap_file_20260503T050937886014Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/ridgeline_fire/domain_bootstrap_qa_20260503T051902240724Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: `133` admitted operations, `27` skips, `130` unique facts, `0`
  rules.
- QA: `17 exact / 10 partial / 13 miss` over `40` questions.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `12` compile-surface gaps, `6` hybrid-join gaps, `5`
  query-surface gaps.

### Lesson

Ridgeline is already less dominated by pure compile gaps than the lower cold
story baseline. The current surface often has pieces of the answer, but the
deadline/authority/rule joins are not yet strong enough. This fixture should be
a good cold counterpart to Iron Harbor and Glass Tide.

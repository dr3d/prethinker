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

## Run RF-002 - Focused Retry Diagnostic

- Timestamp: `2026-05-03T06:53Z`
- Evidence lane: `diagnostic_compile_only`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only semantic-parallax compile after adding focused-pass
  contribution accounting and compact source-pass JSON retry. No gold KB,
  starter registry, or QA source was used.

### Artifact

- Compile:
  `tmp/diagnostic_replays/ridgeline_rf002/domain_bootstrap_file_20260503T065349352859Z_story_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: `49` admitted operations, `20` skips, `49` unique facts, `0`
  rules.
- QA: not run because the compile surface visibly regressed.
- Pass contribution: flat skeleton `0`, standing orders `30`, incident
  timeline `0`, compliance findings `0`, witness statements `8`, corrections
  `11`.

### Lesson

The new accounting exposed a different failure than Three Moles. The compact
retry triggered for the incident-timeline pass, but the retry still failed to
produce valid JSON at the default `32` operation target. This suggests dense
timeline/event passes need either smaller retry targets or better source-pass
budgeting. The run is a useful negative diagnostic, not a benchmark
improvement.

## Run RF-003 - Smaller Retry Target Diagnostic

- Timestamp: `2026-05-03T06:57Z`
- Evidence lane: `diagnostic_compile_only`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only semantic-parallax compile with focused retry target reduced
  from `32` to `16`. No gold KB, starter registry, or QA source was used.

### Artifact

- Compile:
  `tmp/diagnostic_replays/ridgeline_rf003/domain_bootstrap_file_20260503T065711457800Z_story_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: `38` admitted operations, `73` skips, `38` unique facts, `0`
  rules.
- QA: not run because the compile surface visibly regressed.
- Pass contribution: flat skeleton `5`, standing orders `25`, incident
  timeline `2`, witness/analysis `0`, compliance synthesis `1`, final states
  `5`.

### Lesson

Simply lowering the retry target is not enough. In this run the passes parsed,
but the admitted surface was too thin and skip-heavy. Ridgeline now points at a
general lens-quality problem: source-pass success must mean more than valid JSON
and nonzero rows. It needs row-class contribution floors and skip diagnostics
that can distinguish "parsed but too thin" from "failed to parse."

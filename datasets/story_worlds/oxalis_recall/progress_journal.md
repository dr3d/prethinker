# The Oxalis Recall Progress Journal

This journal records cold, diagnostic, assisted, and oracle-calibration runs for
this fixture. Keep evidence lanes separate.

## Fixture Admission

- Timestamp: `2026-05-03`
- Evidence lane: `fixture_admission`
- Source files admitted from: `tmp/oxalis_recall`
- Initial status: source and 40-question QA battery installed; no compile or QA
  run has been executed.

## First Baseline Plan

Use the current source-only semantic-parallax cold baseline recipe:

```text
story.md
  -> source-only profile bootstrap
  -> flat-plus-focused semantic-parallax compile
  -> mapper admission
  -> QA over admitted KB
```

No gold KB, starter registry, strategy document, or QA answer key should be used
for source compilation in the cold lane.

## Run OX-001 - Cold Semantic Parallax Baseline

- Timestamp: `2026-05-03T15:36Z` through `2026-05-03T15:44Z`
- Evidence lane: `cold_unseen`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only profile bootstrap plus current semantic-parallax compile:
  flat-plus-focused intake-plan passes, compact focused-pass operations schema,
  and LLM-authored source entity ledger. No gold KB, starter registry, strategy
  file, or QA source was used during compilation.

### Artifacts

- Compile:
  `tmp/cold_baselines/oxalis_recall/domain_bootstrap_file_20260503T153614838562Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/oxalis_recall/domain_bootstrap_qa_20260503T154413658124Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: `106` admitted operations, `0` skips, `94` unique facts, `0`
  rules.
- Profile rough score: `0.833` with `23` candidate predicates.
- QA: `16 exact / 9 partial / 15 miss` over `40` questions.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `16` compile-surface gaps, `2` query-surface gaps, `6`
  hybrid-join gaps.

### Lesson

Oxalis is a useful counterweight to the strong Dulse score. The compile admitted
many rows with no mapper skips, but downstream QA still missed deadline values,
scope expansions, distributor counts, termination status, unit-accounting
percentages, quote details, and chronological status summaries. This is the
clearest recent reminder that "clean admission" is not the same as
answer-bearing coverage. The pass plan captured product, lot, correction,
notification, and inventory surfaces, but the classification/deadline and
termination-outcome passes were thin or duplicate-heavy. The general next move
should be richer source-surface acquisition for regulatory deadlines, status
windows, and count/percentage support, not an Oxalis-specific profile patch.

## Run OX-002 - Post-Ingestion Evidence Filter Replay

- Timestamp: `2026-05-03T21:31Z`
- Evidence lane: `diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: QA replay over unchanged OX-001 compile with evidence-bundle planning
  and evidence-bundle context filtering. No source recompile, no gold KB, no
  strategy material, no QA answer key in query planning, and no QA write
  proposals.

### Artifacts

- QA:
  `tmp/cold_baselines/oxalis_recall/query_modes/domain_bootstrap_qa_20260503T213134039699Z_qa_qwen-qwen3-6-35b-a3b.json`
- Comparison:
  `tmp/cold_baselines/oxalis_recall/query_modes/oxalis_query_mode_comparison.md`
- Selector:
  `tmp/cold_baselines/oxalis_recall/query_modes/selector_direct_v1.json`

### Result

OX-001 baseline:

```text
16 exact / 9 partial / 15 miss
```

Evidence-filter replay:

```text
18 exact / 11 partial / 11 miss
```

Diagnostic perfect-selector upper bound:

```text
21 exact / 9 partial / 10 miss
```

Direct non-oracle selector:

```text
19 exact / 9 partial / 12 miss
selected best available mode on 37/40 rows
selector errors: 0
```

### Lesson

Oxalis confirms the same post-ingestion pattern in a regulatory recall fixture.
Evidence filtering reduced hard misses substantially, while the selector traded
some miss reduction for higher exact count. The remaining gap is not one knob:
activation needs to balance exact-answer precision against miss reduction.

## Run OX-003 - Compact Flat-Skeleton Cold Replay

- Timestamp: `2026-05-04T00:21Z` through `2026-05-04T00:29Z`
- Evidence lane: `cold_after_general_architecture_change`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only semantic-parallax replay after the compact flat-skeleton
  harness change. No gold KB, starter registry, strategy file, or QA source was
  used during compilation.

### Artifacts

- Compile:
  `tmp/cold_baselines/oxalis_recall/domain_bootstrap_file_20260504T002108990486Z_source_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/oxalis_recall/domain_bootstrap_qa_20260504T002915270497Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

Compile:

```text
91 admitted operations
4 skips
compile health: healthy
flat_skeleton unique rows: 37
unhealthy passes: 0
```

QA:

```text
OX-001 cold baseline: 16 exact / 9 partial / 15 miss
OX-002 evidence replay: 18 exact / 11 partial / 11 miss
OX-003 compact flat: 27 exact / 8 partial / 5 miss
```

Safety:

```text
40/40 parsed
39/40 query rows
0 runtime load errors
0 write proposals
```

Failure surfaces:

```text
2 compile-surface gaps
5 query-surface gaps
6 hybrid-join gaps
```

### Lesson

Oxalis is the strongest immediate transfer result for the compact flat-skeleton
change. The same fixture that previously looked like an ingestion-coverage
problem (`16` exact, `15` miss) now compiles as a healthy surface and reaches
`27` exact with only `5` misses. This suggests the old full-IR flat pass was not
only a Dulse issue; compact source-pass operations give dense regulatory
documents a much better broad skeleton.

The remaining Oxalis frontier is now post-ingestion access and joins, not broad
source admission. Only `2` non-exacts are classified as compile-surface gaps.

## Run OX-004 - Global Partial-Skeleton Transfer Check

- Timestamp: `2026-05-04T01:55Z` through `2026-05-04T02:25Z`
- Evidence lane: `anti_meta_rot_diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only semantic-parallax replay after testing a global compact-pass
  instruction that missing illustrative predicates should not collapse a whole
  pass. No gold KB, starter registry, strategy file, or QA source was used
  during compilation.

### Artifacts

- Compile:
  `tmp/diagnostic_replays/oxalis_ox004/domain_bootstrap_file_20260504T015507244683Z_source_qwen-qwen3-6-35b-a3b.json`
- Plain QA:
  `tmp/diagnostic_replays/oxalis_ox004/domain_bootstrap_qa_20260504T020344155145Z_qa_qwen-qwen3-6-35b-a3b.json`
- Evidence-filter QA:
  `tmp/diagnostic_replays/oxalis_ox004/domain_bootstrap_qa_20260504T021457168528Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

Compile:

```text
128 admitted operations
12 skips
101 unique facts
compile health: healthy
```

QA:

```text
OX-003 compact flat: 27 exact / 8 partial / 5 miss
OX-004 plain:        22 exact / 9 partial / 9 miss
OX-004 evidence:     21 exact / 10 partial / 9 miss
```

### Lesson

This is a useful failed transfer. The partial-skeleton instruction that helped
Three Moles should not be a global compact-pass default. On Oxalis it widened
the compile surface but reduced downstream QA quality. The fix was scoped back
to ledger-backed narrative passes, where the failure mode was observed and where
coverage targets give the instruction a bounded job.

## Run OX-005 - Evidence-Bundle Access and Regulatory Selector Guards

- Timestamp: `2026-05-05T18:39Z` through `2026-05-05T18:46Z`
- Evidence lane: `post_ingestion_access_selector`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: QA replay over the frozen OX-003 compact-flat compile with
  evidence-bundle planning, validated evidence-bundle execution, and compact
  evidence-bundle context filtering. No source recompile, no gold KB, no
  strategy file, no QA-derived compile context, and no QA write proposals.

### Artifacts

- Evidence-bundle QA:
  `tmp/oxalis_access_replay/ox003_evidence_bundle_20260505/domain_bootstrap_qa_20260505T183919321569Z_qa_qwen-qwen3-6-35b-a3b.json`
- Plain-vs-evidence comparison:
  `tmp/oxalis_access_replay/ox003_plain_vs_evidence_comparison_20260505.md`
- Guarded selector before access guards:
  `tmp/oxalis_access_replay/ox003_guarded_selector_20260505.json`
- Guarded selector after access guards:
  `tmp/oxalis_access_replay/ox003_guarded_selector_refined_access_guards_20260505.json`

### Result

```text
OX-003 plain QA:              27 exact / 8 partial / 5 miss
evidence-bundle QA:           32 exact / 6 partial / 2 miss
two-mode upper bound:         33 exact / 6 partial / 1 miss
guarded selector before:      30 exact / 8 partial / 2 miss
guarded selector after:       33 exact / 6 partial / 1 miss
selected-best rows after:     40/40
selector errors after:        0
```

New reason-named selector guards:

- `universal_scope_enumeration_guard`
- `termination_denial_quantity_threshold_guard`
- `lot_affected_target_exclusion_guard`
- `counterfactual_reclassification_deadline_guard`

### Lesson

Oxalis confirms a different kind of harness gain: after the compact compile
surface was already healthy, post-ingestion access and regulatory answer-surface
routing mattered more than another compile prompt. Evidence-bundle mode alone
was strong, but still regressed one exact row. The selector reached the
two-mode upper bound only after adding guards for universal-scope enumeration,
denial rationale with quantity support, explicit lot exclusion, and
classification-bound counterfactual deadlines.

## Run OX-006 - Current Harness Score Hold and Domain-Hint Negative Probe

Date: 2026-05-06

Evidence lane: `anti_meta_rot_score_hold`

Mode: current flat-plus-focused source compile with markdown answer-key judging,
evidence-bundle QA, and failure-surface classification. A follow-up probe tried
a cleaner recall/regulatory domain hint instead of the broader story-world
source-fidelity hint used by the shared story-world planner. No gold KB,
oracle rows, or QA-derived compile context was used.

Artifacts:

- Current-harness compile:
  `tmp/story_world_cold_runs/oxalis_recall/domain_bootstrap_file_20260506T051515844149Z_source_qwen-qwen3-6-35b-a3b.json`
- Current-harness QA:
  `tmp/story_world_cold_qa/oxalis_recall/domain_bootstrap_qa_20260506T055218233575Z_qa_qwen-qwen3-6-35b-a3b.json`
- Regulatory-hint compile:
  `tmp/story_world_cold_runs/oxalis_recall_regulatory_hint/domain_bootstrap_file_20260506T061217973824Z_source_qwen-qwen3-6-35b-a3b.json`
- Regulatory-hint QA:
  `tmp/story_world_cold_qa/oxalis_recall_regulatory_hint/domain_bootstrap_qa_20260506T062409905100Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

```text
current harness:
  compile: 162 admitted / 0 skipped
  QA:      36 exact / 4 partial / 0 miss
  failures: 2 compile, 1 hybrid, 1 answer

recall/regulatory hint probe:
  compile: 73 admitted / 15 skipped
  QA:      24 exact / 11 partial / 5 miss
  failures: 10 compile, 6 hybrid
```

Lesson:

Rejected. A cleaner-looking domain hint was worse than the current broader
source-fidelity run shape. Oxalis is now a score-hold fixture for acquisition
experiments: do not replace the current compact source surface merely because a
domain label reads more specific. The frontier remains post-ingestion access,
deadline/status helpers, and row-level selector protection.


# The Dulse Ledger Progress Journal

This journal records cold, diagnostic, assisted, and oracle-calibration runs for
this fixture. Keep evidence lanes separate.

## Fixture Admission

- Timestamp: `2026-05-03`
- Evidence lane: `fixture_admission`
- Source files admitted from: `tmp/dulse_ledger`
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

## Run DL-001 - Cold Semantic Parallax Baseline

- Timestamp: `2026-05-03T15:23Z` through `2026-05-03T15:31Z`
- Evidence lane: `cold_unseen`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only profile bootstrap plus current semantic-parallax compile:
  flat-plus-focused intake-plan passes, compact focused-pass operations schema,
  and LLM-authored source entity ledger. No gold KB, starter registry, strategy
  file, or QA source was used during compilation.

### Artifacts

- Compile:
  `tmp/cold_baselines/dulse_ledger/domain_bootstrap_file_20260503T152352243239Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/dulse_ledger/domain_bootstrap_qa_20260503T153106149780Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: `70` admitted operations, `21` skips, `52` unique facts, `0`
  rules.
- Profile rough score: `0.833` with `19` candidate predicates.
- QA: `27 exact / 7 partial / 6 miss` over `40` questions.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `9` compile-surface gaps, `4` hybrid-join gaps.

### Lesson

Dulse is a useful transfer baseline: strong enough to show the governance
pipeline can handle source-local custom and ledger records cold, but not so
strong that it hides the next edges. The broad skeleton and adjudication passes
carried most of the useful surface; two focused passes contributed no unique
rows, which keeps lens-health accounting relevant. The non-exacts cluster
around due/return dates, late-debt consequences, restitution after void trades,
fictional/source-bound status, counterfactual date reasoning, and unresolved
dispute summaries. This reinforces the cross-fixture theme: the next gains are
not one fixture patch, but better temporal/status support, consequence rows,
and row-level query activation over safe symbolic surfaces.

## Run DL-002 - Post-Ingestion Evidence Filter Saturation Probe

- Timestamp: `2026-05-03T21:45Z`
- Evidence lane: `diagnostic_replay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: QA replay over unchanged DL-001 compile with evidence-bundle planning
  and evidence-bundle context filtering. No source recompile and no QA writes.

### Artifacts

- QA:
  `tmp/cold_baselines/dulse_ledger/query_modes/domain_bootstrap_qa_20260503T214550100261Z_qa_qwen-qwen3-6-35b-a3b.json`
- Comparison:
  `tmp/cold_baselines/dulse_ledger/query_modes/dulse_query_mode_comparison.md`
- Selector:
  `tmp/cold_baselines/dulse_ledger/query_modes/selector_direct_v1.json`

### Result

DL-001 baseline:

```text
27 exact / 7 partial / 6 miss
```

Evidence-filter replay:

```text
27 exact / 8 partial / 5 miss
```

Diagnostic perfect-selector upper bound:

```text
29 exact / 6 partial / 5 miss
```

Direct non-oracle selector:

```text
27 exact / 7 partial / 6 miss
selected best available mode on 37/40 rows
selector errors: 0
```

### Lesson

Dulse is now the saturation case. Evidence filtering slightly reduced misses,
but the selector stayed conservative and returned to the strong baseline shape.
This is useful because it shows query-surface machinery is not automatically
inflating scores on fixtures that are already well supported.

## Run DL-003 - Cold Replay Compile-Health Warning

- Timestamp: `2026-05-03T23:47Z` through `2026-05-03T23:55Z`
- Evidence lane: `cold_after_general_architecture_change`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only semantic-parallax replay after the rule/body-fact harness
  changes. No gold KB, starter registry, strategy file, or QA source was used
  during compilation.

### Artifacts

- Compile:
  `tmp/cold_baselines/dulse_ledger/domain_bootstrap_file_20260503T234722435138Z_source_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/dulse_ledger/domain_bootstrap_qa_20260503T235508010355Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

```text
DL-001 cold baseline: 27 exact / 7 partial / 6 miss
DL-003 cold replay:   24 exact / 8 partial / 8 miss
```

Compile:

```text
79 admitted operations
35 skips
0 rules
compile health: poor
unhealthy pass: flat_skeleton
recommendation: repair_compile_before_qa
```

QA:

```text
40/40 parsed
40/40 query rows
0 runtime load errors
0 write proposals
failure surfaces: 9 compile-surface, 4 query-surface, 3 hybrid-join
```

### Lesson

This is a useful negative replay. The broad skeleton pass failed and contributed
`0` rows, while the focused passes still admitted a large surface. The compile
looked superficially rich (`79` admitted rows) but the health gate correctly
warned that it should be repaired before QA. The worse QA result confirms that
compile-lens health is not cosmetic; losing the broad skeleton can reduce
answer-bearing coverage even when focused passes are productive.

The next Dulse work should not tune the QA planner against this weaker surface.
It should either replay the cold compile until the skeleton is healthy or run a
targeted skeleton repair pass, then compare against DL-001 and DL-002.

## Run DL-004 - Compact Flat-Skeleton Replay

- Timestamp: `2026-05-04T00:04Z` through `2026-05-04T00:12Z`
- Evidence lane: `cold_after_general_architecture_change`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: replay after a general harness change: when
  `--focused-pass-ops-schema` is enabled, the broad `flat_skeleton` pass now
  also uses compact `source_pass_ops_v1` instead of the full Semantic IR
  workspace.

### Artifacts

- Compile:
  `tmp/cold_baselines/dulse_ledger/domain_bootstrap_file_20260504T000429764914Z_source_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/dulse_ledger/domain_bootstrap_qa_20260504T001248841341Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

Compile:

```text
flat_skeleton unique rows: 51
total admitted operations: 90
total skips: 17
compile health: poor
unhealthy passes: pass_2, pass_3
```

QA:

```text
DL-001 cold baseline: 27 exact / 7 partial / 6 miss
DL-003 weak replay:   24 exact / 8 partial / 8 miss
DL-004 compact flat:  27 exact / 11 partial / 2 miss
```

Safety:

```text
40/40 parsed
40/40 query rows
0 runtime load errors
0 write proposals
```

Notable row changes from DL-001:

```text
miss -> exact: q009, q028, q030, q036
miss -> partial: q019, q020
partial -> exact: q010, q014, q018, q026
exact -> miss: q002
partial -> miss: q038
```

### Lesson

The compact flat-skeleton change fixes the failure exposed by DL-003. The broad
pass no longer JSON-overflows into `semantic_ir_parse_failed`, and the resulting
QA surface cuts misses from `6` to `2` while preserving the old exact count.

This is not a clean monotonic win: several previously exact rows degrade to
partial, and two rows become misses. But the direction is architecturally
important. The flat skeleton should be a compact operation surface, not a giant
workspace. Focused passes still need health repair, especially the thin/skip-heavy
ledger-entry and dispute passes.


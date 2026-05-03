# Veridia-9 Supply Chain & Patent Integrity Dispute Progress Journal

## Fixture Admission - V9-000

- Timestamp: `2026-05-03`
- Source: `tmp/The Veridia-9 Supply Chain & Patent Integrity Dispute`
- Files admitted: source document plus 40-question QA table.
- Gold KB: none supplied.
- Starter ontology/profile: none supplied.
- Benchmark runs: none yet.

### Purpose

This fixture is intended to test cold governed compilation on a compact but
high-density dispute record. It combines product liability, patent warranty,
reinsurance notice, regulatory hold, lab-account conflict, corrections, and
financial arithmetic.

### Initial Research Hypothesis

The first useful baseline should separate at least four surfaces:

- backbone facts: parties, roles, policy, batch, dates, values;
- claim/source facts: Biogenix, Helix, Zenith, FDR, GRV, and Vance positions;
- temporal/correction facts: actual breach time, superseded reset time,
  degradation correction, late notice;
- arithmetic/query support: deductible, underwriter lines, reinsurance share,
  notification threshold, and duration.

No run has been executed at admission time.

## Run V9-001 - Cold Semantic Parallax Baseline

- Timestamp: `2026-05-03T04:58Z` through `2026-05-03T05:05Z`
- Evidence lane: `cold_unseen`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only profile bootstrap plus current semantic-parallax compile:
  flat-plus-focused intake-plan passes, compact focused-pass operations schema,
  and LLM-authored source entity ledger. No gold KB, starter registry, or QA
  source was used during compilation.

### Artifacts

- Compile:
  `tmp/cold_baselines/veridia9/domain_bootstrap_file_20260503T045802618841Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/veridia9/domain_bootstrap_qa_20260503T050519283344Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: `94` admitted operations, `13` skips, `79` unique facts, `0`
  rules.
- QA: `18 exact / 5 partial / 17 miss` over `40` questions.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `18` compile-surface gaps, `3` hybrid-join gaps, `1`
  answer-surface gap.

### Lesson

Veridia starts higher than Three Moles and shows that compact dispute records
transfer reasonably well to the current lenses. The remaining misses likely
need better claim/source preservation, temporal arithmetic, and financial-layer
join support rather than a fixture-specific starter registry.

## Run V9-002 - Lens-Health Diagnostic Replay

- Timestamp: `2026-05-03T12:13Z` through `2026-05-03T12:30Z`
- Evidence lane: `cold_after_general_architecture_change`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only semantic-parallax replay after adding top-level
  compile-lens health summaries. No gold KB, starter registry, expected Prolog,
  or QA source was used during compilation.

### Artifacts

- Compile:
  `tmp/diagnostic_replays/veridia9_v9002/domain_bootstrap_file_20260503T121301361568Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/diagnostic_replays/veridia9_v9002/domain_bootstrap_qa_20260503T122216572924Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: `76` admitted operations, `7` skips, `61` unique facts, `0`
  rules.
- Lens health: `healthy`, recommendation `qa_run_reasonable`, `7` passes,
  `0` unhealthy passes, `61` unique contributed rows, `15` duplicates.
- QA: `19 exact / 6 partial / 15 miss` over `40` questions.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `16` compile-surface gaps, `4` hybrid-join gaps, `1`
  answer-surface gap.

### Lesson

The new compile-health gate did not merely approve a larger surface. V9-002
admitted fewer rows than V9-001 but still improved from `18/5/17` to `19/6/15`.
That is a useful sign that zero-yield/thin/skip-heavy pass diagnostics can
screen for obviously bad compiles without requiring answer-key knowledge.

The improvement is still small, so lens health should not be confused with
downstream sufficiency. Veridia still needs answer-bearing coverage for product
kind detail, claim/source lineage, temporal notice math, financial joins, and
regulatory/patent consequences. The next metric should pair pass health with
question-support coverage: a pass can be structurally healthy and still miss the
rows that later QA needs.

## Run V9-003 - Evidence-Bundle Context Filtering

- Timestamp: `2026-05-03T12:49Z` through `2026-05-03T12:59Z`
- Evidence lane: `cold_after_general_architecture_change`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: post-ingestion QA replay over the unchanged V9-002 compile, with
  `evidence_bundle_plan_v1` and evidence-bundle context filtering enabled.
  This did not recompile the source, did not read a gold KB, did not use a
  starter registry, and did not allow QA write proposals.

### Artifacts

- Compile reused:
  `tmp/diagnostic_replays/veridia9_v9002/domain_bootstrap_file_20260503T121301361568Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/diagnostic_replays/veridia9_v9003/domain_bootstrap_qa_20260503T124919727431Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: unchanged from V9-002, `61` unique facts, `0` rules.
- QA: `22 exact / 4 partial / 14 miss` over `40` questions.
- Delta from V9-002: `+3` exact, `-2` partial, `-1` miss.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `15` compile-surface gaps, `1` hybrid-join gap, `1`
  query-surface gap, `1` answer-surface gap.

### Lesson

V9-003 shows that post-ingestion access choreography is a real lever. The KB
surface did not change, but evidence-bundle context filtering converted q021,
q035, and q040 to exact. That supports the three-surface model:

```text
compile surface != query surface != answer surface
```

The improvement is not free. q012 and q034 regressed from partial to miss, so
evidence-bundle context filtering should remain a measured query-strategy mode
rather than an unquestioned default. It is best viewed as a targeted tool for
near-miss rows where the KB contains relevant surface but ordinary query
planning does not assemble the right support bundle.

## Run V9-004 - Broader Evidence-Bundle Context Floor Negative Control

- Timestamp: `2026-05-03T13:28Z` through `2026-05-03T13:38Z`
- Evidence lane: `cold_after_general_architecture_change`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: post-ingestion QA replay over the unchanged V9-002 compile with
  evidence-bundle context filtering and a broader fallback surface:
  `max_clauses=320`, `broad_floor=160`.

### Artifacts

- Compile reused:
  `tmp/diagnostic_replays/veridia9_v9002/domain_bootstrap_file_20260503T121301361568Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/diagnostic_replays/veridia9_v9004/domain_bootstrap_qa_20260503T132852446387Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: unchanged from V9-002, `61` unique facts, `0` rules.
- QA: `19 exact / 7 partial / 14 miss` over `40` questions.
- Delta from V9-002: same exact count, `+1` partial, `-1` miss.
- Delta from V9-003: `-3` exact, `+3` partial, same miss count.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.

Changed rows versus V9-002:

- Improved to partial: q006, q035, q040.
- Regressed: q012 partial -> miss; q034 partial -> miss.

Changed rows versus V9-003:

- Improved from miss to partial: q006.
- Regressed from exact: q021 exact -> miss; q035/q040 exact -> partial.

### Lesson

V9-004 is the counterweight to BLM-003. A broader evidence-filter floor reduced
hard misses but lost the exact gains that the narrower evidence-filter run had
found. The evidence-filter budget is therefore not a simple "more context is
better" knob. It is a query-surface control parameter that needs row-level
activation or fixture/lane evaluation.

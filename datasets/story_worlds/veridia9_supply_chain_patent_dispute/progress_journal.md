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

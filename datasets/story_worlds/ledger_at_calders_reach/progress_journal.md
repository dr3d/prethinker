# The Ledger at Calder's Reach Progress Journal

## Fixture Admission - CAL-000

- Timestamp: `2026-05-03`
- Source: `tmp/The Ledger at Calder's Reach`
- Files admitted: source story plus extracted 110-question QA file.
- Gold KB: none admitted.
- Starter ontology/profile: none admitted.
- Benchmark runs: none yet.

### Oracle Boundary

The supplied QA source contained extra canonical inventories, suggested
predicate families, snapshots, gold triples, and scoring notes. Those were not
copied into this fixture. Only the Q/A pairs were extracted for post-ingestion
scoring.

### Purpose

This fixture is intended to test governed compilation of a long evolving story
with overlapping legal, family, role, residence, trust, inheritance, and
boundary-state changes.

No run has been executed at admission time.

## Run CAL-001 - Cold Semantic Parallax Baseline

- Timestamp: `2026-05-03T05:23Z` through `2026-05-03T05:45Z`
- Evidence lane: `cold_unseen`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only profile bootstrap plus current semantic-parallax compile:
  flat-plus-focused intake-plan passes, compact focused-pass operations schema,
  and LLM-authored source entity ledger. No gold KB, starter registry, or QA
  source was used during compilation.

### Artifacts

- Compile:
  `tmp/cold_baselines/ledger_at_calders_reach/domain_bootstrap_file_20260503T052338731954Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/ledger_at_calders_reach/domain_bootstrap_qa_20260503T054553171055Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: `187` admitted operations, `23` skips, `180` unique facts, `0`
  rules.
- QA: `65 exact / 9 partial / 36 miss` over `110` questions.
- Safety: `109/110` parsed, `108/110` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `37` compile-surface gaps, `6` query-surface gaps, `2`
  hybrid-join gaps.

### Lesson

Calder's Reach is the strongest cold long-story signal so far. The current
pipeline handles many state-at-time and identity questions without oracle
material, but the misses still cluster around missing compiled support and a
few query-surface failures. This should become the main anti-meta-rot story
fixture for long-range state tracking.

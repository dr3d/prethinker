# Generalization Baseline Matrix

Last updated: 2026-05-03

This page records frozen `cold_unseen` baselines for newly admitted fixtures.
The goal is to detect meta-rot: cases where the harness becomes too good at the
shape of its existing research fixtures instead of general governed
language-to-truth transformation.

Companion diagnostic: [Cold Baseline Failure Rollup](https://github.com/dr3d/prethinker/blob/main/docs/COLD_BASELINE_FAILURE_ROLLUP.md).

All runs below used the same source-only semantic-parallax recipe:

- source document only for compilation;
- no gold KB, ontology registry, starter profile, expected Prolog signatures, or
  QA source in compile context;
- flat-plus-focused intake-plan passes;
- compact focused-pass operations schema;
- LLM-authored source entity ledger;
- deterministic mapper admission;
- post-ingestion QA scored from the fixture QA file.

## Cold Baselines

| Run | Fixture | Qs | Exact | Partial | Miss | Exact+Partial | Admitted | Skipped | Facts | Rules | Parsed | Query Rows | Write Leaks | Runtime Errors |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `MMM-001` | Three Moles | 40 | 10 | 8 | 22 | 18 | 174 | 10 | 110 | 0 | 40 | 40 | 0 | 0 |
| `V9-001` | Veridia-9 | 40 | 18 | 5 | 17 | 23 | 94 | 13 | 79 | 0 | 40 | 40 | 0 | 0 |
| `RF-001` | Ridgeline Fire | 40 | 17 | 10 | 13 | 27 | 133 | 27 | 130 | 0 | 40 | 40 | 0 | 0 |
| `CAL-001` | Calder's Reach | 110 | 65 | 9 | 36 | 74 | 187 | 23 | 180 | 0 | 109 | 108 | 0 | 0 |
| `BLM-001` | Black Lantern Maze | 40 | 27 | 7 | 6 | 34 | 299 | 28 | 299 | 0 | 40 | 39 | 0 | 0 |
| `AG-001` | Avalon Grant Committee | 40 | 25 | 12 | 3 | 37 | 114 | 6 | 109 | 0 | 40 | 40 | 0 | 0 |
| `DL-001` | Dulse Ledger | 40 | 27 | 7 | 6 | 34 | 70 | 21 | 52 | 0 | 40 | 40 | 0 | 0 |
| `OX-001` | Oxalis Recall | 40 | 16 | 9 | 15 | 25 | 106 | 0 | 94 | 0 | 40 | 40 | 0 | 0 |
| `SC-001` | Sable Creek Budget | 40 | 20 | 8 | 12 | 28 | 58 | 9 | 49 | 0 | 40 | 40 | 0 | 0 |
| `TV-001` | Thornfield Variance | 40 | 20 | 6 | 14 | 26 | 67 | 7 | 63 | 0 | 40 | 40 | 0 | 0 |

## Pending Cold Fixtures

All fixtures admitted in this batch now have a first cold score. New fixtures
should use the same source-only cold recipe before any assisted or diagnostic
lane is created.

| Fixture | Questions | Primary Pressure |
| --- | ---: | --- |
| _none_ | 0 | _none_ |

## Failure Surface Snapshot

| Run | Compile Gaps | Query Gaps | Hybrid Join Gaps | Answer Gaps |
| --- | ---: | ---: | ---: | ---: |
| `MMM-001` | 22 | 2 | 4 | 2 |
| `V9-001` | 18 | 0 | 3 | 1 |
| `RF-001` | 12 | 5 | 6 | 0 |
| `CAL-001` | 37 | 6 | 2 | 0 |
| `BLM-001` | 7 | 0 | 6 | 0 |
| `AG-001` | 11 | 2 | 2 | 0 |
| `DL-001` | 9 | 0 | 4 | 0 |
| `OX-001` | 16 | 2 | 6 | 0 |
| `SC-001` | 13 | 5 | 1 | 1 |
| `TV-001` | 14 | 4 | 1 | 1 |

## Early Read

The cold results do not look bogus or fixture-memorized. They are uneven in the
right way:

- **Three Moles** is mostly a compile-support problem, suggesting the current
  story-world lenses still do not preserve all source-local magical object
  families, causality, and final state.
- **Veridia-9** transfers moderately well to compact dispute records but needs
  stronger claim/source, correction, and financial-layer joins.
- **Ridgeline Fire** has more partial support and more hybrid/query gaps,
  pointing at rule/deadline/authority joins rather than raw extraction alone.
- **Calder's Reach** is the strongest long-story cold result so far and should
  become a key anti-meta-rot state-tracking fixture.
- **Black Lantern Maze** is the strongest 40-question cold score, but because it
  is closer to the existing policy/governance fixture family, it should be used
  as a transfer check rather than proof of universal generality.
- **Avalon Grant Committee** lands in the intended useful-difficulty band:
  strong exact+partial coverage, very few hard misses, and no executable rules.
  That makes it a good next rule-composition target rather than a finished
  success.
- **Dulse Ledger** is a strong cold transfer check for customary ledger
  reasoning: `27 exact / 7 partial / 6 miss`, with non-exacts concentrated in
  temporal debt consequences, restitution, counterfactuals, and unresolved
  dispute summaries.
- **Oxalis Recall** is deliberately less flattering: despite `106` admitted
  operations and `0` skips, it scored `16 exact / 9 partial / 15 miss`. That
  makes it a strong reminder that clean admission is not the same as
  answer-bearing regulatory coverage.
- **Sable Creek Budget** scored `20 exact / 8 partial / 12 miss` after first
  exposing a profile-bootstrap JSON role-field runaway. A general schema cap on
  argument role names fixed the structural failure. The actual score points at
  thin amendment-cycle passes, vote-record/tally coverage, reserve-balance
  support, and public-comment authority boundaries.
- **Thornfield Variance** scored `20 exact / 6 partial / 14 miss`, mirroring
  Sable's score shape while testing zoning variance law instead of municipal
  budgeting. It preserved many zoning, notice, hearing, and vote rows, but still
  admitted `0` rules and missed survey authority, individual vote aggregation,
  testimony detail, dimensional exceptions, and appeal state.

## Guardrail

Do not tune the harness from any single row above. A change should either
improve at least two cold fixtures or improve one cold fixture while preserving
known regression fixtures such as Iron Harbor, Glass Tide, CE, and APR.

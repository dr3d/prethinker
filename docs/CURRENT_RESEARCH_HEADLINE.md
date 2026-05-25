# Current Research Headline

Last updated: 2026-05-25

## Current Measurement Position

Prethinker now has a measurable direct-surface instrument and fresh public
document pressure that is strong enough to guide engineering:

```text
source document
  -> deterministic source ledgers
  -> semantic compile candidates
  -> mapper-admitted KB artifact
  -> QA over admitted predicates, deterministic ledgers, selectors, and guards
```

The current research question is no longer whether query-time compatibility
bridges can rescue old rows. They are retired from the forward path. The
question is whether the compiler can emit recurring answer-bearing distinctions
as direct admitted surfaces without leaking fixture vocabulary, and whether
those surfaces transfer to fresh ugly public documents.

## Current Empirical Anchor

The 2026-05-22 native restamp remains the internal non-regression anchor:

```text
2163 judged rows
1997 exact / 46 partial / 120 miss
92.33% exact
0 compatibility rows
0 runtime load errors
0 write proposal rows
```

The newest public-document pressure is fresh ugly public Batch 03. The latest
guarded slices are:

```text
SEC subset:      75 exact / 0 partial / 0 miss over 75 rows
Non-SEC subset: 216 exact / 6 partial / 3 miss over 225 rows
Slice-combined: 291 exact / 6 partial / 3 miss over 300 rows = 97.0%
0 compatibility rows
0 runtime load errors
0 write proposal rows
```

That slice-combined Batch 03 view is not a single fresh 300-row rerun. It is a
current guarded view assembled from the latest SEC and non-SEC slices, and some
mechanisms were learned from Batch 03 itself. Read it as product-thermometer
and regression evidence, not as a leaderboard claim.

The current measurement stack is:

- Native restamp: `1997 / 46 / 120` on `2163` rows (`92.33%` exact), with
  `0` compatibility rows, `0` runtime load errors, and `0` write proposals.
- Fresh ugly public Batch 03: latest guarded slices `75 / 0 / 0` SEC and
  `216 / 6 / 3` non-SEC, slice-combined `291 / 6 / 3` over `300` rows
  (`97.0%` exact), with `0` compatibility rows, `0` runtime load errors, and
  `0` write proposals.
- Real-world external spotcheck: four externally sourced fixtures at latest
  fixture-level `160 / 0 / 0`, with `4 / 4` compile gates clean.
- Sealed unseen authored transfer: `152 / 1 / 6` on `160` rows (`95.0%`
  exact), with `0` compatibility rows.
- Earlier cold transfer baseline: six fresh transfer fixtures at
  `177 / 10 / 53` on `240` rows (`73.75%` exact).

## Caveats That Travel With The Claim

- The native restamp used the same 56 maintained native corpus members as the
  2026-05-20 baseline and a clean git dataset tree, but no prior per-file hash
  manifest was found. The comparability claim is same named corpus, not proven
  byte-identical corpus.
- Compile quality gate noise increased from `26 / 30` pass/hold to `9 / 47`.
  QA improved anyway, so this is a gate-calibration and diagnostic issue, not a
  reason to suppress the measurement.
- Failure surfaces improved overall except query-surface gaps:
  `compile_surface_gap 116 -> 96`, `hybrid_join_gap 47 -> 39`,
  `query_surface_gap 20 -> 29`, `answer_surface_gap 5 -> 1`,
  `judge_uncertain 4 -> 1`.
- Three native-corpus regressions remain in the worksheet trail; they are not
  public doctrine and should not become architecture.
- The diagnostic rejected flat-pass skip count changed from `128 -> 0`, which
  is useful but should be read together with the gate-calibration shift.
- Batch 03 is not a sealed benchmark anymore. It has become a working
  regression surface after mechanism repair, so the next generalization check
  needs fresh ugly documents.

## What Changed

The recent architecture moved from guard compression to source-record and
surface discipline:

- guard families compressed to a small semantic rollup;
- compatibility-adapter language was removed from the public front door;
- deterministic source ledgers became part of the compiled artifact contract;
- palette priors became control-plane vocabulary aids, not fact sources;
- compile-quality checks started flagging vague wrapper rows when concrete
  backbone rows disappear;
- lens audits shifted from "add a term" to "prove slot contracts on unlike
  documents."
- Batch 03 repairs were mostly generic source-record/query-only surfaces:
  exact row labels, field/value pairs, postal-state and address-block
  extraction, attachment labels, incident statistics, source-stated
  enforcement inventories, signatory responsibility, and ratio calculation.

## Active Pressure

The highest-value next work is fresh-transfer discipline:

1. Classify the remaining Batch 03 non-exacts as generic mechanisms or declared
   source/oracle limits.
2. Use fresh ugly documents for the next honest generalization read before
   polishing Batch 03 further.
3. Keep the native restamp warm as a non-regression corroboration, not as the
   only proof of progress.
4. Keep fixture nouns, row IDs, answer strings, and dataset labels out of the
   harness.

## Read Next

- [Active Research Lanes](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md)
- [Audit Grammar Measurement Note](https://github.com/dr3d/prethinker/blob/main/docs/AUDIT_GRAMMAR_MEASUREMENT_NOTE.md)
- [Audit Grammar Technical Note](https://github.com/dr3d/prethinker/blob/main/docs/AUDIT_GRAMMAR_TECHNICAL_NOTE.md)
- [Compiled KB Artifact Package](https://github.com/dr3d/prethinker/blob/main/docs/COMPILED_KB_ARTIFACT_PACKAGE.md)
- [Boundary Probe Research Method](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_PROBE_RESEARCH_METHOD.md)
- [Product And Palette Governance](https://github.com/dr3d/prethinker/blob/main/docs/PRODUCT_AND_PALETTE_GOVERNANCE.md)

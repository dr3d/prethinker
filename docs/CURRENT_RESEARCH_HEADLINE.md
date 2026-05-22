# Current Research Headline

Last updated: 2026-05-22

## Publishable Direct-Surface Measurement

Prethinker now has a measurable direct-surface instrument:

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
as direct admitted surfaces without leaking fixture vocabulary.

## Current Empirical Anchor

The 2026-05-22 native restamp measured the direct-surface path at:

```text
2163 judged rows
1997 exact / 46 partial / 120 miss
92.33% exact
0 compatibility rows
0 runtime load errors
0 write proposal rows
```

That score is an anchor, not a finish line. It says the instrument can now be
described publicly with caveats intact: compatibility adapters stayed off,
runtime stayed clean, and the answer path improved while the failure taxonomy
remained inspectable.

The current measurement stack is:

- Native restamp: `1997 / 46 / 120` on `2163` rows (`92.33%` exact), with
  `0` compatibility rows, `0` runtime load errors, and `0` write proposals.
- Real-world external spotcheck: four externally sourced fixtures at latest
  fixture-level `160 / 0 / 0`, with `4 / 4` compile gates clean.
- Sealed unseen authored transfer: `152 / 1 / 6` on `160` rows (`95.0%`
  exact), with `0` compatibility rows.
- Earlier cold transfer baseline: six fresh transfer fixtures at
  `177 / 10 / 53` on `240` rows (`73.75%` exact).

## Caveats That Travel With The Claim

- The native restamp used the same 56 fixture names as the 2026-05-20 baseline
  and a clean git dataset tree, but no prior per-file hash manifest was found.
  The comparability claim is same named corpus, not proven byte-identical
  corpus.
- Compile quality gate noise increased from `26 / 30` pass/hold to `9 / 47`.
  QA improved anyway, so this is a gate-calibration and diagnostic issue, not a
  reason to suppress the measurement.
- Failure surfaces improved overall except query-surface gaps:
  `compile_surface_gap 116 -> 96`, `hybrid_join_gap 47 -> 39`,
  `query_surface_gap 20 -> 29`, `answer_surface_gap 5 -> 1`,
  `judge_uncertain 4 -> 1`.
- The clearest fixture regressions are `black_lantern_maze`,
  `identifier_ledger_torture`, and `lantern_school_field_trip`.
- The diagnostic rejected flat-pass skip count changed from `128 -> 0`, which
  is useful but should be read together with the gate-calibration shift.

## What Changed

The recent architecture moved from guard compression to surface discipline:

- guard families compressed to a small semantic rollup;
- compatibility-adapter language was removed from the public front door;
- deterministic source ledgers became part of the compiled artifact contract;
- palette priors became control-plane vocabulary aids, not fact sources;
- compile-quality checks started flagging vague wrapper rows when concrete
  backbone rows disappear;
- lens audits shifted from "add a term" to "prove slot contracts on unlike
  documents."

## Active Pressure

The highest-value next work is release-followup discipline, not delaying the
claim:

1. Investigate query-surface gap growth without changing the published stamp.
2. Explain the `9 / 47` native compile-gate distribution and calibrate the gate
   against answer-bearing impact.
3. Read the three regressed fixtures for structural causes.
4. Preserve the real-world four-fixture batch as transfer evidence, not native
   baseline material.
5. Keep fixture nouns, row IDs, answer strings, and dataset labels out of the
   harness.

## Read Next

- [Active Research Lanes](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md)
- [Audit Grammar Measurement Note](https://github.com/dr3d/prethinker/blob/main/docs/AUDIT_GRAMMAR_MEASUREMENT_NOTE.md)
- [Compiled KB Artifact Package](https://github.com/dr3d/prethinker/blob/main/docs/COMPILED_KB_ARTIFACT_PACKAGE.md)
- [Boundary Probe Research Method](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_PROBE_RESEARCH_METHOD.md)
- [Product And Palette Governance](https://github.com/dr3d/prethinker/blob/main/docs/PRODUCT_AND_PALETTE_GOVERNANCE.md)

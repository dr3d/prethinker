# Current Research Headline

Last updated: 2026-05-18

## Direct-Surface Instrument, Compile-Stability Pressure

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

The latest native fixed-compile QA restamp measured the direct-surface path at:

```text
2163 judged rows
1934 exact / 64 partial / 162 miss
89.41% exact
0 compatibility rows
0 runtime load errors
0 write proposal rows
```

That score is an anchor, not a finish line. It says the query layer is strong
enough that remaining misses are mostly compile-surface, source-fidelity,
hybrid-join, or answer-surface coordinates.

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

The highest-value current work is compile-surface stability:

1. Find rows where answer text is stranded only in source-record ledgers.
2. Promote only generic direct surfaces that recover those rows on unlike
   documents.
3. Detect candidate palettes that offer useful predicates but fail to deliver
   admitted rows.
4. Keep fixture nouns, row IDs, answer strings, and dataset labels out of the
   harness.
5. Use QA-only restamps when work is query-layer only; use full recompiles only
   when compile behavior changed.

## Read Next

- [Current Harness Instrument](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_HARNESS_INSTRUMENT.md)
- [Active Research Lanes](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md)
- [Compiled KB Artifact Package](https://github.com/dr3d/prethinker/blob/main/docs/COMPILED_KB_ARTIFACT_PACKAGE.md)
- [Boundary Probe Research Method](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_PROBE_RESEARCH_METHOD.md)
- [Product And Palette Governance](https://github.com/dr3d/prethinker/blob/main/docs/PRODUCT_AND_PALETTE_GOVERNANCE.md)

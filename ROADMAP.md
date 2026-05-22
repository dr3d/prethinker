# Prethinker Roadmap

Last updated: 2026-05-22

This is a secondary planning note. Treat
[PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md),
[docs/CURRENT_RESEARCH_HEADLINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_RESEARCH_HEADLINE.md),
and [docs/AUDIT_GRAMMAR_MEASUREMENT_NOTE.md](https://github.com/dr3d/prethinker/blob/main/docs/AUDIT_GRAMMAR_MEASUREMENT_NOTE.md)
as the current truth surfaces.

## Current Positioning

Prethinker is a governed document-compile and QA workbench:

```text
source document
  -> semantic compile candidates
  -> deterministic mapper/admission gate
  -> compiled Prolog KB artifact package
  -> governed QA over admitted state, deterministic ledgers, selectors, and guards
```

The authority boundary remains the core thesis. Neural models may interpret,
compile, plan, and judge rows; deterministic runtime code decides what can
become durable state and whether a QA run stayed inside the allowed evidence
surface.

## Current Measurement Anchor

The current public measurement stack is:

- Native restamp, 2026-05-22: `1997 exact / 46 partial / 120 miss` over `2163`
  rows (`92.33%` exact), with `0` compatibility rows, `0` runtime load errors,
  and `0` QA write proposals.
- Real-world external four-fixture spotcheck: latest fixture-level
  `160 / 0 / 0`, with `4 / 4` compile gates clean.
- Sealed unseen authored transfer: `152 / 1 / 6` over `160` rows (`95.0%`
  exact).
- Earlier cold transfer baseline: `177 / 10 / 53` over `240` rows (`73.75%`
  exact).

The caveats are part of the roadmap: native compile-gate noise increased from
`26 / 30` pass/hold to `9 / 47`, query-surface gaps rose from `20` to `29`, and
the clearest current regressions are `black_lantern_maze`,
`identifier_ledger_torture`, and `lantern_school_field_trip`.

## Near-Term Priorities

1. **Gate calibration without gate collapse**
   - Explain why the native quality gate now holds `47` fixtures while QA
     improved.
   - Separate over-sensitive diagnostic flags from true answer-bearing source
     surface failures.
   - Keep source-claim, source-authority, vote-tally, quantity, and coexistence
     checks strict when they correspond to real misses.

2. **Query-surface gap investigation**
   - Read the rows behind the `20 -> 29` query-surface increase.
   - Prefer structural query planner or selector-policy fixes over fixture
     phrasing patches.
   - Preserve compatibility adapters as forensic tools only.

3. **Regressed fixture reading**
   - Start with `black_lantern_maze`, `identifier_ledger_torture`, and
     `lantern_school_field_trip`.
   - Compare current misses against the 2026-05-20 native baseline and the
     current compile-gate reasons.
   - Promote only repairs that survive unlike probes.

4. **Messy-document transfer**
   - Keep the four externally sourced real-world fixtures as transfer evidence,
     not native baseline material.
   - Ask for or stage messier external fixtures only after the current gate and
     query-surface lessons are understood.

5. **Public docs hygiene**
   - Keep root docs and `docs/` aligned with the current measurement claim.
   - Keep long worksheets and generated reports out of the public front door.
   - Use `C:\prethinker_tmp_archive` and Git history for old run archaeology.

## Still Out Of Scope

- Letting model output directly authorize KB writes.
- Treating structured JSON as proof of truth.
- Tuning to fixture names, row ids, answer strings, local people, or
  story-specific phrasing.
- Production medical, legal, regulatory, or financial advice claims.
- Full fine-tuning as the primary path before the governed compile/QA
  instrument is better characterized.

# Prethinker Roadmap

Last updated: 2026-05-25

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
- Fresh ugly public Batch 03, latest guarded slices: SEC subset `75 / 0 / 0`
  over `75` rows and non-SEC subset `216 / 6 / 3` over `225` rows (`96.0%`).
  Read together, the current slice view is `291 / 6 / 3` over `300` rows
  (`97.0%`), with `0` compatibility rows, `0` runtime load errors, and `0`
  QA write proposals. This is not a single fresh 300-row rerun.
- Real-world external four-fixture spotcheck: latest fixture-level
  `160 / 0 / 0`, with `4 / 4` compile gates clean.
- Sealed unseen authored transfer: `152 / 1 / 6` over `160` rows (`95.0%`
  exact).
- Earlier cold transfer baseline: `177 / 10 / 53` over `240` rows (`73.75%`
  exact).

The caveats are part of the roadmap: native compile-gate noise increased from
`26 / 30` pass/hold to `9 / 47`, query-surface gaps rose from `20` to `29`, and
Batch 03 is now partly tuned evidence rather than a pristine benchmark. The
next clean generalization check needs fresh ugly documents that did not shape
the current mechanism set.

## Near-Term Priorities

1. **Fresh ugly transfer discipline**
   - Treat Batch 03 as current product-thermometer and regression evidence, not
     as a surface to polish indefinitely.
   - Ask for fresh ugly documents whenever remaining fixes start moving residue
     between adjacent rows instead of reducing total residue.
   - Keep external, authored, native, and narrative probes separate.

2. **Remaining source-record and query-surface blockers**
   - Work the Batch 03 non-exacts as generic mechanisms: first-occurrence source
     rows, raw spelling/casing preservation, source-section joins,
     cross-document limits, and authority/acronym normalization.
   - Prefer structural query planner, ledger, or selector-policy fixes over
     fixture phrasing patches.
   - Preserve compatibility adapters as forensic tools only.

3. **Native non-regression stamp**
   - Re-run the native corpus when mechanism changes are stable enough to make
     the cost worthwhile.
   - Compare failure-surface distribution, not only headline exact rate.
   - Keep the May 22 native anchor visible until a new full native stamp exists.

4. **Gate calibration without gate collapse**
   - Explain why the native quality gate held `47` fixtures while QA improved.
   - Separate over-sensitive diagnostic flags from true answer-bearing source
     surface failures.
   - Keep source-claim, source-authority, vote-tally, quantity, and coexistence
     checks strict when they correspond to real misses.

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

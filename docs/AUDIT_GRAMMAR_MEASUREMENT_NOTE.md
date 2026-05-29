# Audit Grammar Measurement Note

Last updated: 2026-05-28

This note captures the current public measurement claim for Prethinker. It is
not a benchmark leaderboard. It is a disciplined snapshot of the instrument as
measured across native, fresh ugly public, sealed unseen, real-world, and older
cold-transfer evidence.

For the fuller methodology, read
[Audit Grammar Technical Note](https://github.com/dr3d/prethinker/blob/main/docs/AUDIT_GRAMMAR_TECHNICAL_NOTE.md).

## Claim

Prethinker has crossed the line from "interesting harness" to a governed
document-compile instrument with measured transfer evidence.

The strongest current claim is not that every document is solved. The claim is
that a model-proposed, deterministically admitted symbolic write layer can now
answer row-level questions over compiled documents with high accuracy, zero
compatibility-adapter pressure, zero runtime load errors, and zero QA write
proposals across several distinct measurement classes.

## Measurements

| Measurement class | Corpus | Result | Discipline metrics |
| --- | --- | ---: | --- |
| Native restamp | 56 maintained native corpus members, 2163 rows | `1997 / 46 / 120`, `92.33%` exact | `0` compatibility rows, `0` runtime load errors, `0` write proposals |
| Fresh ugly public 2026-05-28 R2 | 8 newly landed public-document fixtures, 200 rows | `198 / 2 / 0`, `99.0%` exact | full replay after query-template normalization; row churn `2` improved / `1` regressed, so not a clean promotion; compile gate `2 / 6` old pass/hold and `4 / 6 / 0` blocking/diagnostic/advisory holds; `0` compatibility rows, `0` runtime load errors, `0` write proposals |
| Fresh ugly public 2026-05-28 R1 | 8 newly landed public-document fixtures, 200 rows | `197 / 3 / 0`, `98.5%` exact | fresh R1; compile gate `2 / 6` old pass/hold and `4 / 6 / 0` blocking/diagnostic/advisory holds; `0` compatibility rows, `0` runtime load errors, `0` write proposals |
| Fresh ugly public Batch 03 | 12 externally sourced public-document fixtures, latest guarded slices | SEC `75 / 0 / 0`, non-SEC `216 / 6 / 3`; slice-combined current view `291 / 6 / 3` over `300`, `97.0%` exact | not a single fresh 300-row rerun; `0` compatibility rows, `0` runtime load errors, `0` write proposals |
| Real-world external spotcheck | 4 externally sourced real-world fixtures, 160 rows | `160 / 0 / 0` latest fixture-level QA, not a single fresh 160-row rerun | `4 / 4` compile gates pass, `0` compatibility rows, `0` runtime load errors, `0` write proposals |
| Sealed unseen authored transfer | 4 sealed fixtures, 160 rows | `152 / 1 / 6`, `95.0%` exact | `0` compatibility rows, `0` runtime load errors, `0` write proposals |
| Earlier cold transfer baseline | 6 fresh transfer fixtures, 240 rows | `177 / 10 / 53`, `73.75%` exact | cold source-only transfer before the current direct-surface work |

## Method

The audit grammar is the discipline around the numbers:

- freeze the artifact before QA;
- separate compile-surface, hybrid-join, query-surface, answer-surface, and
  judge-uncertain failures;
- keep compatibility adapters off the forward path;
- count compatibility rows, runtime load errors, and write proposals as
  discipline metrics, not footnotes;
- journal caveats before interpreting the result;
- continue investigating regressions after the stamp instead of repairing
  during the stamp.

This matters because the headline score is only meaningful if the system did
not buy it by letting query-time compatibility rows, answer-key leakage, or
runtime writes rescue weak compiles.

## Caveats

- The 2026-05-22 native restamp used the same 56 maintained native corpus
  members as the 2026-05-20 baseline, and the current dataset tree had no git
  drift, but no prior per-file hash manifest was found. The strict
  comparability claim is therefore same named corpus, not proven
  byte-identical corpus.
- The compile quality gate became noisier on the native restamp:
  `26 / 30 -> 9 / 47` pass/hold under the old overloaded gate. Current tooling
  also reports reason tiers; a 2026-05-28 rescore of saved May 22 native compile
  artifacts reads `2 / 54` old-style pass/hold, with `11` blocking-tier holds,
  `53` diagnostic-tier holds, and `0` advisory holds. QA improved despite the
  gate noise, so the gate is a calibration and diagnostic problem, not a native
  QA blocker.
- The diagnostic rejected flat-pass skip count changed from `128 -> 0`; this is
  useful evidence but should be interpreted with the gate-change caveat.
- Query-surface gaps increased from `20 -> 29` even as compile-surface,
  hybrid-join, answer-surface, and judge-uncertain gaps improved.
- Three native-corpus regressions remain in the worksheet trail. They should be
  read for structural causes, not promoted as public vocabulary.
- The sealed unseen fixtures were authored for this project, so they are useful
  transfer evidence but not a substitute for messy external documents.
- The earlier cold-transfer baseline and the current real-world spotcheck are
  different corpora, not the same documents measured before and after.
- Fresh ugly public Batch 03 is now partly tuned evidence: it is valuable as a
  product thermometer and regression guard, but the next generalization claim
  requires fresh ugly documents that did not shape the mechanisms.
- Fresh ugly public 2026-05-28 R2 is the latest full replay, but it was not a
  clean promotion because one previously exact row became partial. It was also
  not provider-pinned inside OpenRouter; artifact metadata records mixed backend
  providers. Treat it as current hosted-path transfer evidence with row-churn
  caveat, not a single-provider variance study.

## Artifact Pointers

- Native restamp worksheet: `docs/NATIVE_RESTAMP_WORKSHEET.md`
- Real-world fixture inputs:
  `datasets/real_world_transfer/20260521`
- Fresh ugly public Batch 03 fixture inputs:
  `datasets/real_world_transfer/fresh_ugly_public_20260524_03`
- Fresh ugly public transfer worksheet:
  `docs/FRESH_UGLY_PUBLIC_BATCH_04_WORKSHEET.md`
- Fresh ugly public 2026-05-28 worksheet:
  `docs/FRESH_UGLY_PUBLIC_20260528_WORKSHEET.md`
- Sealed unseen fixture inputs:
  `datasets/sealed_unseen/20260521`
- Native compile summary:
  `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\native_corpus_full_compile_stamp_20260522_current_summary.json`
- Native QA summary:
  `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\native_corpus_full_qa_stamp_20260522_openrouter6_summary.json`
- Fresh ugly public transfer worksheet:
  `docs/FRESH_UGLY_PUBLIC_BATCH_04_WORKSHEET.md`
- Current fresh fixture request spec:
  `docs/NEXT_FRESH_FIXTURE_REQUESTS_20260528.md`
- Retired sealed-unseen worksheet in the local cold archive:
  `C:\prethinker_tmp_archive\prestamp_hardening_worksheet_retired_20260522\PRESTAMP_HARDENING_WORKSHEET.md`

## Public Summary Draft

Prethinker now has a 92.33% native restamp and a fresh ugly public May 28 R2
transfer replay at 198/2/0 over 200 rows, both with zero compatibility rows,
zero runtime load errors, and zero QA write proposals. R2 improved the aggregate
but carried row churn, so it is not a clean promotion over R1. The sealed-unseen
authored result remains 95.0%, and the older four-fixture real-world spotcheck
remains clean at latest fixture-level 160/0/0. The caveat is open: the May 28
compile gate still held, so the product answer path is stronger than the
release-grade compile coverage signal. Current active-instrument leakage audit is clean at
`0` forbidden hits and `0` warning hits.

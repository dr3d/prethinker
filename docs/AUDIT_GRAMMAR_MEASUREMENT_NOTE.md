# Audit Grammar Measurement Note

Last updated: 2026-05-22

This note captures the current public measurement claim for Prethinker. It is
not a benchmark leaderboard. It is a disciplined snapshot of the instrument as
measured across native, sealed unseen, real-world, and older cold-transfer
evidence.

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
| Native restamp | 56 maintained story-world fixtures, 2163 rows | `1997 / 46 / 120`, `92.33%` exact | `0` compatibility rows, `0` runtime load errors, `0` write proposals |
| Real-world external spotcheck | 4 externally sourced real-world fixtures, 160 rows | `160 / 0 / 0` latest fixture-level QA | `4 / 4` compile gates pass, `0` compatibility rows, `0` runtime load errors, `0` write proposals |
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

- The 2026-05-22 native restamp used the same 56 fixture names as the
  2026-05-20 baseline, and the current dataset tree had no git drift, but no
  prior per-file hash manifest was found. The strict comparability claim is
  therefore same named corpus, not proven byte-identical corpus.
- The compile quality gate became noisier on the native restamp:
  `26 / 30 -> 9 / 47` pass/hold. QA improved despite that, so the gate noise is
  a calibration and diagnostic problem, not a native QA blocker.
- The diagnostic rejected flat-pass skip count changed from `128 -> 0`; this is
  useful evidence but should be interpreted with the gate-change caveat.
- Query-surface gaps increased from `20 -> 29` even as compile-surface,
  hybrid-join, answer-surface, and judge-uncertain gaps improved.
- Three notable fixture regressions need follow-up:
  `black_lantern_maze`, `identifier_ledger_torture`, and
  `lantern_school_field_trip`.
- The sealed unseen fixtures were authored for this project, so they are useful
  transfer evidence but not a substitute for messy external documents.

## Artifact Pointers

- Native restamp worksheet: `docs/NATIVE_RESTAMP_WORKSHEET.md`
- Real-world fixture inputs:
  `datasets/real_world_transfer/20260521`
- Native compile summary:
  `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\native_corpus_full_compile_stamp_20260522_current_summary.json`
- Native QA summary:
  `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\native_corpus_full_qa_stamp_20260522_openrouter6_summary.json`
- Real-world surface worksheet:
  `docs/SOURCE_LEDGER_COMPILE_SURFACE_WORKSHEET.md`
- Retired sealed-unseen worksheet in the local cold archive:
  `C:\prethinker_tmp_archive\prestamp_hardening_worksheet_retired_20260522\PRESTAMP_HARDENING_WORKSHEET.md`

## Public Summary Draft

Prethinker moved from a 73.75% cold-transfer baseline six weeks ago to a
92.33% native restamp, a 95.0% sealed-unseen transfer result, and a clean
160/0/0 four-fixture real-world spotcheck, all with zero compatibility rows,
zero runtime load errors, and zero QA write proposals. The caveat is open:
native compile-gate noise increased and a few fixtures regressed, so the next
cycle investigates gate calibration, query-surface gaps, and those regressions
without hiding the current result.

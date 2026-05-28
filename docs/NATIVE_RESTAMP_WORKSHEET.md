# Native Restamp Worksheet

This worksheet is the current lab note for the maintained native-corpus stamp
and its unresolved compile-gate readout. It replaces the larger May 22 worksheet
that was retired to `C:\prethinker_tmp_archive`.

## 2026-05-22 Native Stamp Snapshot

Corpus and conditions:

- Corpus: same 56 named `datasets/story_worlds` fixtures used by the
  2026-05-20 baseline.
- Strict caveat: no prior per-file hash manifest was found, so the comparison is
  same named corpus, not proven byte-identical corpus.
- Provider path: OpenRouter-compatible API.
- Model: `qwen/qwen3.6-35b-a3b`.
- Compile lanes: `6`.
- QA lanes: `6`.

Baseline QA, 2026-05-20:

- Rows: `2163`
- Exact / partial / miss: `1971 / 64 / 127`
- Exact rate: `91.12%`
- Compatibility rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`

Current native QA, 2026-05-22:

- Rows: `2163`
- Exact / partial / miss: `1997 / 46 / 120`
- Exact rate: `92.33%`
- Compatibility rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`

Failure-surface distribution:

| Surface | 2026-05-20 | 2026-05-22 |
| --- | ---: | ---: |
| Compile-surface gap | `116` | `96` |
| Hybrid-join gap | `47` | `39` |
| Query-surface gap | `20` | `29` |
| Answer-surface gap | `5` | `1` |
| Judge-uncertain | `4` | `1` |

Read: the QA stamp improved cleanly under the hygiene counters, but
query-surface gaps increased and remain a real blocker.

## Compile Gate Readout

Baseline compile gate, 2026-05-20:

- Parsed fixtures: `56 / 56`
- Candidate predicates: `1380`
- Compile admitted / skipped: `8198 / 991`
- Effective admitted / skipped: `8198 / 863`
- Diagnostic rejected flat-pass skips: `128`
- Quality gate: `26 pass / 30 hold`

Current compile gate, 2026-05-22:

- Parsed fixtures: `56 / 56`
- Candidate predicates: `1383`
- Compile admitted / skipped: `7814 / 1106`
- Effective admitted / skipped: `7814 / 1106`
- Diagnostic rejected flat-pass skips: `0`
- Quality gate: `9 pass / 47 hold`

The gate got much more pessimistic while QA improved. The strongest current read
is not "native quality collapsed"; it is that the gate had become a mixed
diagnostic surface where advisory compile-profile warnings and stamp-blocking
failures were both counted as holds.

## 2026-05-28 Gate Noise Triage

Artifacts:

- Original May 20 compile summary:
  `C:\prethinker_tmp_archive\tmp_unload_20260521_2106\native_corpus_full_compile_stamp_20260520_summary.json`
- Original May 22 compile summary:
  `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\native_corpus_full_compile_stamp_20260522_current_summary.json`
- May 22 artifacts rescored with current summarizer:
  `C:\prethinker_tmp_archive\native_gate_rescore_20260528\native_20260522_rescored_current_code_summary.json`

Observed transition from the original May 20 gate to the original May 22 gate:

- Hold -> hold: `30`
- Pass -> pass: `9`
- Pass -> hold: `17`
- Hold -> pass: `0`

The 17 new holds were previously clean fixtures that picked up profile-delivery
diagnostics, mostly source-claim and vote-tally carrier warnings. The new May 22
reason distribution was led by:

- `source_claim_carrier_partially_delivered`: `22`
- `source_claim_carrier_offered_but_undelivered`: `15`
- `vote_tally_carrier_offered_but_undelivered`: `11`
- `source_authority_pair_preservation`: `7`
- `source_claim_backbone_coexistence_missing`: `5`

Rescoring the May 22 compile artifacts with the current 2026-05-28 summarizer
made the gate stricter again:

- Quality gate: `2 pass / 54 hold`
- Blocking tier: hold, `11` fixtures with blocking reasons
- Diagnostic tier: `53` fixtures with diagnostic reasons
- Advisory tier: `0` fixtures with advisory reasons
- Diagnostic rejected flat-pass skips: `64`
- All 56 fixture artifacts were readable.

Current-code rescore added more diagnostic families to the hold surface,
including profile schema contracts and compile-health warnings. That is useful
telemetry, but it confirms the same issue: the single pass/hold gate is now
overloaded.

## Current Decision

Do not relax the gate silently. The project rule remains: warnings are evidence,
not decoration.

The gate report now carries explicit tiers:

- `blocking_reasons`: conditions that invalidate a stamp or public compile-gate
  claim.
- `diagnostic_reasons`: useful compile-profile pressure that should be tracked,
  counted, and investigated, but does not by itself mean QA or artifact hygiene
  failed.
- `advisory_reasons`: low-risk quality hints that should never be promoted to a
  release claim without unlike-fixture validation.

The older `pass / hold` headline remains available for continuity, but a
future public claim should name which tier is clean. A clean QA stamp with noisy
diagnostics is not the same as a clean compile gate.

## Next Native Stamp Protocol

Before spending another full native restamp:

1. Keep the latest fresh ugly and ACH heldout runs separate from native.
2. Run focused smoke checks for compatibility rows, runtime load errors, and QA
   write proposals.
3. Decide whether compile-gate tiering is code-complete or whether the next
   stamp should report the old overloaded gate explicitly as noisy.
4. If the stamp runs, do not repair mid-run.
5. Report QA score, hygiene counters, failure-surface distribution, and gate
   tier distribution separately.

## Retired Detail

The long May 22 worksheet was moved out of the public docs tree and remains in:

`C:\prethinker_tmp_archive\docs_worksheet_archive_20260527\NATIVE_RESTAMP_WORKSHEET.md`

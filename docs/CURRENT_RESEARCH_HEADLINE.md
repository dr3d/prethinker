# Current Research Headline

Last updated: 2026-05-29

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
current blocker is stricter: after removing Python-side semantic routing over
raw English questions, a follow-up audit found Python-side semantic routing over
free-text source/display fields. Claims are blocked until answer delivery is
rebuilt through sign-clean mechanisms only: LLM-produced query semantics,
typed/source-contained compile artifacts, and deterministic joins over admitted
facts.

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

The newest public-document pressure is the post-raw-utterance-cut English
regression on fresh ugly public 2026-05-29:

```text
Fresh ugly 2026-05-29 R9 post-raw-utterance-cut QA replay:
161 exact / 22 partial / 17 miss over 200 rows = 80.5%
0 compatibility rows
0 runtime load errors
0 write proposal rows
raw-utterance audit: pass
free-text semantic-routing audit: fail
claim status: blocked
compile artifacts: reused/frozen from R1 to isolate query-path impact
```

Diff against the prior May 29 clean replay was `197 / 1 / 2` to `161 / 22 /
17`. The drop is too large to treat as hosted-provider variance. It means the
retired raw-utterance routing was carrying meaningful delivery capacity. The
good news is that the cleaned instrument failed honestly on compatibility,
runtime, and write-proposal hygiene. The bad news is that source-ledger
free-text routing remains in active code, so the score is still provisional.

The high May 28/early May 29 ugly-public measurements are now historical
pre-reset evidence, not current headline claims for the sign-clean instrument.

The prior fresh ugly public Batch 03 guarded slices remain useful regression
evidence:

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
mechanisms were learned from Batch 03 itself. Read it as regression evidence,
not as a leaderboard claim.

The current measurement stack is:

- Native restamp: `1997 / 46 / 120` on `2163` rows (`92.33%` exact), with
  `0` compatibility rows, `0` runtime load errors, and `0` write proposals.
- Fresh ugly public 2026-05-29 post-raw-utterance-cut replay: `161 / 22 / 17`
  over `200` rows (`80.5%` exact), hygiene `0 / 0 / 0`, but sign-clean claim
  status blocked by the free-text semantic-routing audit.
- Fresh ugly public 2026-05-28 and early 2026-05-29 high-score replays:
  historical pre-reset evidence only; do not use as current product or
  architecture claims until the sign-clean delivery path recovers.
- Fresh ugly public Batch 03: latest guarded slices `75 / 0 / 0` SEC and
  `216 / 6 / 3` non-SEC, slice-combined `291 / 6 / 3` over `300` rows
  (`97.0%` exact), with `0` compatibility rows, `0` runtime load errors, and
  `0` write proposals; historical pre-reset regression evidence.
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
- Compile quality gate noise increased from `26 / 30` pass/hold to `9 / 47`
  under the old overloaded gate. Current tooling now also reports reason tiers:
  a 2026-05-28 rescore of saved May 22 native compile artifacts reads `2 / 54`
  old-style pass/hold, with `11` blocking-tier holds, `53` diagnostic-tier
  holds, and `0` advisory holds. QA improved anyway, so this is a gate
  calibration and diagnostic issue, not a reason to suppress the measurement.
- Failure surfaces improved overall except query-surface gaps:
  `compile_surface_gap 116 -> 96`, `hybrid_join_gap 47 -> 39`,
  `query_surface_gap 20 -> 29`, `answer_surface_gap 5 -> 1`,
  `judge_uncertain 4 -> 1`.
- Three native-corpus regressions remain in the worksheet trail; they are not
  public doctrine and should not become architecture.
- The diagnostic rejected flat-pass skip count changed from `128 -> 0`, which
  is useful but should be read together with the gate-calibration shift.
- Batch 03 and the high-score May 28/early May 29 runs are not sealed
  benchmarks anymore. They are working regression surfaces after mechanism
  repair, and the post-sign-clean score reset must travel with any mention of
  them.
- The May 28 fresh ugly run is fresh transfer evidence, but OpenRouter routing
  was not provider-pinned; artifact metadata shows mixed backend providers.
  Treat it as current hosted-path evidence, not a single-provider variance
  study.

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

The highest-value next work is sign-clean delivery recovery:

1. Remove or quarantine Python semantic routing over free-text source/display fields.
2. Rebuild query delivery without Python-side raw-utterance routing.
3. Identify which of the `38` R5-exact rows that became non-exact need compile
   surfaces versus semantic query-intent coverage.
4. Decide whether stamp claims should pin OpenRouter provider/quantization or
   report hosted-path variance bands explicitly.
5. Keep Batch 03 as regression evidence instead of polishing it for another
   headline.
6. Validate the ACH stress package with the profile-aware validator using
   `--package-profile ach`.
7. Keep the native restamp warm as a non-regression corroboration, not as the
   only proof of progress.
8. Keep fixture nouns, row IDs, answer strings, and dataset labels out of the
   harness.

ACH remains an overlay, not a mutation path. Ranking is product-plausible, high
and low sensitivity are promising, and medium family-level sensitivity has only
same-batch rescore evidence so far. It needs a fresh heldout ACH stress package
before becoming a product claim.

## Read Next

- [Active Research Lanes](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md)
- [Audit Grammar Measurement Note](https://github.com/dr3d/prethinker/blob/main/docs/AUDIT_GRAMMAR_MEASUREMENT_NOTE.md)
- [Audit Grammar Technical Note](https://github.com/dr3d/prethinker/blob/main/docs/AUDIT_GRAMMAR_TECHNICAL_NOTE.md)
- [Compiled KB Artifact Package](https://github.com/dr3d/prethinker/blob/main/docs/COMPILED_KB_ARTIFACT_PACKAGE.md)
- [Boundary Probe Research Method](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_PROBE_RESEARCH_METHOD.md)
- [Product And Palette Governance](https://github.com/dr3d/prethinker/blob/main/docs/PRODUCT_AND_PALETTE_GOVERNANCE.md)
- [Next Fresh Fixture Requests](https://github.com/dr3d/prethinker/blob/main/docs/NEXT_FRESH_FIXTURE_REQUESTS_20260528.md)
- [Overlay Architecture](https://github.com/dr3d/prethinker/blob/main/docs/OVERLAY_ARCHITECTURE.md)

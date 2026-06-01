# Audit Grammar Technical Note

Last updated: 2026-05-28

> Status: historical pre-reset context. Do not cite the score claims in this
> document as current. After the May 29 to June 1 sign-clean reset, the current
> claim-bearing hard-clean floor is `73 / 200` (`36.5%`) on the 8-fixture
> English batch. Current direction is documented in
> [Domain Tier Strategy](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_TIER_STRATEGY.md)
> and
> [Active Research Lanes](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md).

This is the public technical note for Prethinker's current measurement method.
It explains what the audit grammar measures, why the discipline metrics matter,
and how to read the current numbers without turning them into a benchmark claim
they are not.

Prethinker is a governed semantic compile and QA system. A model proposes
semantic structure, but deterministic code decides what becomes durable truth,
what can be queried, and what gets counted.

## The Short Claim

As of May 28, 2026, Prethinker measures as follows:

| Evidence class | Corpus | Result | Cleanliness counters |
| --- | --- | ---: | --- |
| Native restamp | 56 maintained fixtures, 2163 judged rows | `1997 exact / 46 partial / 120 miss`, `92.33%` exact | `0` compatibility rows, `0` runtime load errors, `0` QA write proposals |
| Fresh ugly public 2026-05-28 R2 | 8 newly landed public-document fixtures, 200 rows | `198 exact / 2 partial / 0 miss`, `99.0%` exact | full replay after query-template normalization; row churn `2` improved / `1` regressed, so not a clean promotion; compile gate `2 / 6` old pass/hold and `4 / 6 / 0` blocking/diagnostic/advisory holds; `0` compatibility rows, `0` runtime load errors, `0` QA write proposals |
| Fresh ugly public 2026-05-28 R1 | 8 newly landed public-document fixtures, 200 rows | `197 exact / 3 partial / 0 miss`, `98.5%` exact | fresh R1; compile gate `2 / 6` old pass/hold and `4 / 6 / 0` blocking/diagnostic/advisory holds; `0` compatibility rows, `0` runtime load errors, `0` QA write proposals |
| Fresh ugly public Batch 03 | 12 externally sourced public-document fixtures, latest guarded slices | SEC `75 / 0 / 0`, non-SEC `216 / 6 / 3`; slice-combined current view `291 / 6 / 3` over `300`, `97.0%` exact | not a single fresh 300-row rerun; `0` compatibility rows, `0` runtime load errors, `0` QA write proposals |
| Real-world external spotcheck | 4 externally sourced fixtures, 160 rows | `160 / 0 / 0` latest fixture-level QA, not a single fresh 160-row rerun | `4 / 4` compile gates clean, `0` compatibility rows, `0` runtime load errors, `0` QA write proposals |
| Sealed unseen authored transfer | 4 sealed fixtures, 160 rows | `152 / 1 / 6`, `95.0%` exact | `0` compatibility rows, `0` runtime load errors, `0` QA write proposals |
| Earlier cold transfer baseline | 6 fresh transfer fixtures, 240 rows | `177 / 10 / 53`, `73.75%` exact | measured before the current direct-surface work |

The core claim is not "Prethinker solves documents." The claim is narrower and
more useful: a model-proposed, deterministically admitted symbolic write layer
can answer row-level questions over compiled document artifacts with high
accuracy while preserving an auditable account of how the answer was reached.

That discipline matters most in domains where plausible answers are not enough:
legal, clinical, financial, safety, and regulatory workflows. In those settings
the difference between a useful system and a liability is often whether the
system can show what state was admitted, what policy answered from it, and which
failure surface is responsible when an answer is wrong or incomplete.

The externally sourced four-fixture real-world transfer inputs are retained at
`datasets/real_world_transfer/20260521`; they remain separate from the native
`datasets/story_worlds` baseline.

The project-authored sealed unseen inputs are retained at
`datasets/sealed_unseen/20260521`; they remain separate from both the native
baseline and the externally sourced real-world fixtures.

## What "Audit Grammar" Means

The audit grammar is the measurement language of the instrument. It is the set
of counters, labels, gates, and rules that make a run interpretable after the
fact.

It answers these questions:

- Was the source compiled into a frozen artifact before QA?
- Did QA answer from admitted state, deterministic ledgers, direct surfaces,
  selectors, and guards?
- Did any row depend on retired compatibility rescue?
- Did the compiled Prolog/runtime load cleanly?
- Did QA try to write new truth while answering?
- If a row missed, did the failure belong to compile, query, join, answer
  shape, or judge uncertainty?
- Were caveats recorded before interpretation, rather than patched away after
  seeing the score?

The audit grammar is not the same as the model prompt. It is the accounting
layer around the run.

## The Unit Of Measurement

The measured unit is a QA row over a frozen compiled artifact.

```text
source document
  -> semantic compile passes
  -> deterministic mapper admission
  -> frozen KB artifact package
  -> row-level QA over admitted state
  -> exact / partial / miss judgment
  -> failure-surface and cleanliness accounting
```

Rows do not become truth. Rows test whether the compiled artifact preserved
truth, made it queryable, and allowed the harness to answer safely.

This distinction matters. A row can fail even if the source document contains
the answer. That is not necessarily a model comprehension failure. It might be:

- a compile-surface gap, where the answer-bearing relation was not admitted;
- a query-surface gap, where the artifact had the answer but the query did not
  reach it;
- a hybrid-join gap, where pieces existed but were not joinable;
- an answer-surface gap, where the evidence was close but the answer shape was
  wrong;
- judge uncertainty, where the scorer could not cleanly classify the row.

## Artifact Freezing

The method separates compile from QA.

Compile produces an artifact package:

```text
world.pl          admitted source state
epistemic.pl      claims, findings, corrections, uncertainty
ledgers.pl        deterministic source addressability
query_policy.json what QA may use
manifest.json     reproducibility metadata
diagnostics.json  skipped, blocked, and coverage notes
```

QA then runs over that package. If a later answer requires rereading raw source
prose as hidden retrieval, that is evidence of a compile-surface or
artifact-design gap. Source text can be preserved for provenance, audit, and
recompilation, but it is not supposed to be the ordinary answer substrate.

## Cleanliness Counters

The headline exact rate is not enough. Prethinker reports discipline counters
beside the score.

### Compatibility Rows

`0 compatibility rows` means the row did not depend on a retired or non-clean
compatibility adapter to rescue an answer. This does not mean the LLM was
absent. It means the audited path stayed inside the intended governed QA
surface.

### Runtime Load Errors

`0 runtime load errors` means the compiled artifact could load and execute in
the runtime. A high score with load errors would be ambiguous because some rows
might be judged around a broken artifact.

### QA Write Proposals

`0 QA write proposals` means the QA phase did not attempt to mutate durable
truth while answering. This is central to the authority boundary. QA may plan,
query, judge, and classify. It may not patch the KB to make the answer work.

## Failure Surface Taxonomy

The May 22 native restamp also recorded failure-surface movement relative to
the May 20 baseline:

| Failure surface | Baseline | May 22 restamp | Direction |
| --- | ---: | ---: | --- |
| Compile-surface gap | `116` | `96` | improved |
| Hybrid-join gap | `47` | `39` | improved |
| Query-surface gap | `20` | `29` | regressed |
| Answer-surface gap | `5` | `1` | improved |
| Judge-uncertain | `4` | `1` | improved |

This is why two runs with the same headline score would not be equivalent. The
failure distribution says which part of the instrument changed.

The current score improved, but query-surface gaps rose. That is useful
pressure. It says the next repair should not simply add more compile facts. It
should inspect where question planning or executable query shape failed to
reach state that may already exist.

## Compile Gate Accounting

The native compile quality gate became noisier:

```text
May 20 baseline: 26 pass / 30 hold
May 22 restamp: 9 pass / 47 hold
```

That is not hidden. It travels with the claim.

The old pass/hold headline is now preserved as a continuity metric, not the
only release signal. Current tooling also emits reason tiers:

```text
May 22 saved native artifacts, rescored on May 28:
old-style gate: 2 pass / 54 hold
blocking-tier holds: 11
diagnostic-tier holds: 53
advisory-tier holds: 0
```

QA improved to `92.33%` despite the gate shift. Operationally, this means the
gate is flagging many source-claim, source-authority, vote-tally, quantity, and
coexistence surfaces that did not all become answer misses. The gate may be
useful diagnostic pressure, or it may be over-sensitive. The next cycle has to
separate blocking, diagnostic, and advisory cases rather than suppress the gate
or loosen it blindly.

## Why Multiple Evidence Classes

The native corpus is the development set. It is important for non-regression,
but not enough for generalization.

The current public claim therefore names five evidence classes:

- Native restamp: shows current behavior on the maintained 56-fixture corpus.
- Fresh ugly public 2026-05-28 R2: tests a newly landed ugly public English
  official-document batch after the Batch 03 repairs and the display-filter
  query-template normalization repair. It is the current fresh-transfer
  thermometer, with the important caveats that row churn was not clean and
  OpenRouter routing was not provider-pinned.
- Fresh ugly public Batch 03: tests ugly public documents with tables, official
  formats, identifiers, attachments, redactions, and regulatory/incident
  structure. It is now partly tuned evidence and should be read as a product
  thermometer plus regression guard, not as a sealed benchmark.
- Real-world external spotcheck: tests documents from external sources and
  domains outside the fixture author's usual patterns.
- Sealed unseen authored transfer: tests withheld fixtures created for transfer
  pressure, while acknowledging they are authored for this project.
- Earlier cold transfer baseline: preserves the before-state from a less
  mature instrument.

The earlier cold transfer baseline and the current real-world spotcheck are not
the same documents measured before and after. They are different corpora, with
different row counts and fixture shapes. The comparison is architectural
context, not a controlled paired-document delta.

The real-world and sealed-unseen results do not erase the native caveats. They
answer a different question: whether the architecture transfers beyond the
development corpus.

## Comparability Caveat

The May 22 native restamp used the same 56 maintained native corpus members as
the May 20 baseline, and the dataset tree was clean in git. However, no prior
per-file hash manifest was found for the May 20 run. The strict public
statement is therefore:

```text
same named native corpus, not proven byte-identical corpus
```

This caveat matters because small source or QA drift can change the meaning of
a comparison. The current May 22 run does include a fixture hash manifest so
future native stamps can be compared more tightly.

## What The Numbers Do Not Claim

These measurements do not claim:

- universal document understanding;
- production readiness for legal, clinical, financial, or safety decisions;
- model-free QA;
- proof that LLM-authored fixtures represent messy real-world documents;
- proof that Batch 03 is an untouched benchmark after the May 25 mechanism
  work;
- proof that May 28 R2 is single-provider stable;
- proof that the compile gate is calibrated correctly at every tier;
- proof that `91.12%` and `92.33%` are strictly comparable under identical gate
  behavior;
- proof that `92.33%` is a stable ceiling or floor.

They do claim that the current instrument can be measured honestly, that it can
separate answer accuracy from cleanliness, and that failure modes remain
locatable after a run.

## Why This Is Different From Ordinary RAG Evaluation

Ordinary retrieval evaluation often asks whether a system found enough text to
produce a plausible answer.

Prethinker asks a stricter question:

```text
Was the source compiled into admitted, queryable state,
and did the answer come from that state under an auditable policy?
```

Retrieval can still help find source material. But the product claim is about
compiled memory: source facts, epistemic status, deterministic ledgers, query
policy, runtime execution, and explicit failure accounting.

## Reading The May 22 Result

The best reading is balanced:

- The architecture is stronger than the earlier cold-transfer baseline.
- The fresh ugly public Batch 03 slice view remains useful regression evidence,
  but it is not a single fresh 300-row rerun and is no longer untouched after
  mechanism repair.
- The fresh ugly public May 28 R2 run is now the strongest fresh real-document
  transfer signal at `99.0%`, with clean hygiene, one row-churn regression, and
  a still-noisy compile gate.
- The real-world four-fixture spotcheck is clean and remains useful context.
- The native restamp improved from `91.12%` to `92.33%` exact under the current
  measurement, but the two runs carried different gate calibration behavior.
- The sealed unseen authored transfer at `95.0%` is useful, but it is not a
  substitute for messy external documents.
- The compile gate is noisy, now tiered, and must be read by tier rather than
  as one overloaded pass/hold number.
- Query-surface regression is the most direct next technical pressure.
- Three native-corpus regressions need structural reading from the worksheet
  trail, but their local names are not public doctrine.

The public claim is therefore publishable with caveats, not finished without
caveats.

## Reproducibility Pointers

- Current measurement card:
  [Audit Grammar Measurement Note](https://github.com/dr3d/prethinker/blob/main/docs/AUDIT_GRAMMAR_MEASUREMENT_NOTE.md)
- Retired detailed worksheets:
  `C:\prethinker_tmp_archive\docs_worksheet_archive_20260601`
- Current fresh fixture request spec:
  [Next Fresh Fixture Requests](https://github.com/dr3d/prethinker/blob/main/docs/NEXT_FRESH_FIXTURE_REQUESTS_20260528.md)
- QA boundary:
  [QA Instrument](https://github.com/dr3d/prethinker/blob/main/docs/QA_INSTRUMENT.md)
- Compiled artifact contract:
  [Compiled KB Artifact Package](https://github.com/dr3d/prethinker/blob/main/docs/COMPILED_KB_ARTIFACT_PACKAGE.md)

The local bulk artifacts live in `C:\prethinker_tmp_archive`. Retired
worksheets are preserved there and in Git history; they are intentionally not
kept in the public docs front door.

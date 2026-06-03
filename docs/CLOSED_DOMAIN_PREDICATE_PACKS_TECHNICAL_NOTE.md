# Closed Domain Predicate Packs Technical Note

Last updated: 2026-06-03

## Abstract

Prethinker tested a narrow research question after the sign-clean reset:

```text
Can a closed predicate domain, built from a small seed set, transfer hard-clean
to unseen messy official documents in the same family under strict governance?
```

The current answer is limited but real:

```text
Closed, lens-scoped predicate packs can stabilize recurring
official-document skeleton anatomy under strict governance. Open-ended
substantive detail remains an abstention or lower-tier boundary unless a
compact domain layer reproduces on unlike documents.
```

This is not a claim of general document understanding, product readiness,
self-serve schema induction, or 90%+ QA accuracy. It is a falsifiable
compile-stability result for bounded official-document families.

## Why This Phase Exists

Earlier high scores were not just stale. They were contaminated measurements.
They were useful laboratory signals, but later audits showed that some answer
delivery depended on paths that were not allowed to carry a technical thesis:

- source-record or display-prose routing;
- Python-side semantic routing over question/source text;
- judge-facing surface-token exposure;
- model-prior completion of source-missing values;
- stale gates that allowed older favorable runs to remain flattering after
  governance tightened.

The failure was operational, not mystical. Agent-authored repairs optimized
row-level exact rate and treated some "query-only" support paths as safe because
they did not mutate the durable KB. That was the wrong boundary. A path can
avoid KB writes and still cheat the thesis if it lets deterministic code parse
source prose, question wording, or model-authored display text to recover the
answer. Several old gains came from putting answer-bearing tokens in front of
the judge or routing recurring question shapes through prose-adjacent support
surfaces instead of proving that typed facts were compiled and replayable.

That is the prose-smuggling failure. It wasted research time, and it is part of
the result: AI assistance can find useful mechanisms quickly, but if the score
is not gated inside the loop, the same assistant will also optimize toward the
visible scoreboard and move language back into the instrument through whatever
door remains open. The current gates exist because the wall-sign version of the
rule did not hold.

The reset changed the primary metric from product-looking exact rate to
hard-clean typed transfer:

```text
LLM proposes typed facts inside a closed predicate/lens scope.
Deterministic gates decide whether those facts are admissible.
Only reproducible typed facts can support the research claim.
```

## Claim-Bearing Gates

A domain-pack result is claim-bearing only when the named run satisfies the
gates relevant to that run:

- closed profile registry;
- lens-scoped offered signatures;
- N>=3 same-condition compiles;
- support>=2 for supported expected facts;
- 0 supported forbidden facts;
- registered signatures only;
- atom-shape pass;
- lens-scope pass;
- carrier value-domain pass where applicable;
- sign-clean audit pass for current code where applicable;
- no source-record prose matching;
- no query-text routing;
- no fixture vocabulary;
- no prose-shaped atoms in the winning path.

Targeted replays are mechanism evidence, not transfer claims. Composed
historical runs are diagnostic unless a fresh same-condition bundle reproduces
them.

## Method Summary

The method is:

1. Choose a bounded document family with recurring official-document anatomy.
2. Build a small seed micro-fixture from retained source material.
3. Define a closed predicate registry with compact value domains.
4. Assign predicates to lenses; each lens sees only the signatures it may emit.
5. Compile the seed under N>=3/support>=2.
6. Add only general carrier-contract or typed-normalization fixes.
7. Test unlike same-family transfer fixtures under the same gates.
8. Treat failures as boundary evidence unless a general mechanism is visible.

The LLM is allowed to judge source meaning during compile. It is not allowed to
freely define the instrument language after the domain pack is closed. The
compiler proposes facts; deterministic gates decide what counts.

## Evidence Snapshot

| Family | Scope | Current result | What it supports |
| --- | --- | --- | --- |
| SEC Form 8-K | Skeleton only: filing wrapper, registrant, identifiers, item headings, exhibits, signature block | Seed `13/13`; three unlike transfers `13/13`, `12/12`, `12/12`; `0` supported forbidden | Strongest methods example: a small closed skeleton pack transfers across unlike same-family filings. |
| FDA warning letters | Richer regulatory case: wrapper, chronology, CGMP skeleton, citations, insanitary condition, response lanes | Transfer_001 current replay `26/26`; transfer_002 fresh current pack `20/27`; transfer_003 archived replay `18/26` but current integrity fail | Primary richer case study: skeleton/citation/regulatory boilerplate transfers better than role semantics, context-dependent categories, and value/detail flesh. |
| NTSB investigations | Incident skeleton, occurrence, vehicles, parties, conditions, chronology, safety action, casualty, finding | Seed `13/13`; first unlike transfer `18/25` manifest and `19/25` deterministic reducer replay; `0` supported forbidden | Corroborating boundary: wrapper, chronology, vehicles, and conditions transfer more cleanly than casualty, safety-action attachment, and findings/probable-cause substance. |

## SEC Methods Example

SEC Form 8-K is the cleanest current positive cell because it is deliberately
skeleton-only.

```text
profile: datasets/domain_profiles/sec_form_8k_v1/ontology_registry.json
carriers: sec_filing/6, sec_registrant/4, sec_registrant_identifier/5,
          sec_filing_item/5, sec_exhibit/5, sec_signatory/5,
          domain_omission/5
```

Claim-bearing artifacts:

| Cell | Artifact |
| --- | --- |
| Seed micro | `tmp/domain_lens_bundle/sec-form-8k-skeleton-r3-local-qwen-contract-tightening-exhibit-number-reducer` |
| Transfer 001 | `tmp/domain_lens_bundle/sec8k-transfer-r3-phone-reducer`; gate `tmp/research_integrity_gate_sec8k_t001_r3` |
| Transfer 002 | `tmp/domain_lens_bundle/sec8k-t002-r3-date`; gate `tmp/research_integrity_gate_sec8k_t002_r3` |
| Transfer 003 | `tmp/domain_lens_bundle/sec8k-t003-r1`; gate `tmp/research_integrity_gate_sec8k_t003_r1` |

Important negative evidence: transfer_001 initially exposed an unstated-CIK
model-prior leak. The row was rejected before the fixture became claim-bearing.
That is the intended governance behavior: the pack may abstain, but it may not
fill missing source facts from model memory.

SEC does not claim event-substance extraction.

## FDA Case Study

FDA warning letters are the richer case study because they pressure regulatory
substance, numbered CGMP items, citations, response assessment, and conclusion
boilerplate.

```text
profile: datasets/domain_profiles/fda_warning_letter_v1/ontology_registry.json
```

Claim-bearing and boundary artifacts:

| Cell | Result | Artifact |
| --- | --- | --- |
| Transfer 001 current replay | `26/26`, `0/9` supported forbidden, integrity pass | `tmp/domain_transfer_gate_fda_t001_current_rescore_fixed3_20260603` |
| Transfer 002 fresh current pack | `20/27`, `0/7` supported forbidden, atom/lens gates clean | `tmp/domain_lens_bundle/fda-t002-current-pack-fresh-local-20260603-r5-lens-plan-ops-chronology-id-canon` |
| Transfer 003 archived replay | `18/26`, `0/10` supported forbidden, current integrity fail | `tmp/domain_transfer_gate_fda_t003_current_rescore_fixed_20260603` |

Per-layer boundary:

| Layer | Transfer_001 | Transfer_002 | Read |
| --- | --- | --- | --- |
| Wrapper, facility, chronology | stable | stable | Typed document skeleton works. |
| Correspondence roles | `2/2` | `2/4` | Addressee/recipient/responsible-official semantics need a better domain rule or abstention. |
| CGMP violation skeleton | `6/6` | `3/4` | Stable when category is direct; context-dependent category mapping remains a boundary. |
| CGMP citations | `6/6` | `4/4` | Strongest FDA layer. |
| Legal basis, conclusion, response requirement | stable | stable | Recurring regulatory boilerplate transfers better than detail flesh. |
| Detail/value flesh | `2/2` | `2/6` | Main abstention boundary. |

FDA supports the richer-domain path, but not broad FDA completion.

## NTSB Boundary Corroboration

NTSB is a second unlike official-document family used to test whether the same
boundary appears outside FDA/SEC.

```text
profile: datasets/domain_profiles/ntsb_investigation_v1/ontology_registry.json
artifact: tmp/domain_lens_bundle/ntsb-transfer-surface-001-bundle-harness-r1
```

Current transfer:

```text
manifest: 18 / 25 expected, 0 / 15 supported forbidden
R2 deterministic reducer replay: 19 / 25 expected, 0 / 15 supported forbidden
atom-shape / registered-signature / lens-scope blockers: 0
```

Per-layer boundary:

| Layer | Result | Read |
| --- | --- | --- |
| Wrapper / occurrence identity | `3/3` | Stable skeleton. |
| Asset and party | `3/3` | Core vehicle/operator rows transfer. |
| Conditions | `5/5` after typed reducer replay | Compact categorical condition layer works. |
| Timeline | `6/6` | Strong chronological event layer. |
| Safety action | `2/3` | Actor/organization attachment remains unstable. |
| Casualty | `0/3` | Numeric/table transfer boundary in this cell. |
| Findings / probable cause | `0/2` | Open causal substance should abstain or remain lower tier. |

NTSB corroborates the skeleton-vs-substance boundary; it is not a promoted
second full domain pack.

## What Was Learned

1. **Closed predicate domains help.** Once a document family has a compact,
   lens-scoped predicate registry, recurring skeleton anatomy can transfer
   under strict gates.
2. **Lens scope matters.** Predicate sets are offered as a function of lens,
   not as a global bag available to every compile pass.
3. **Typed normalization is legitimate when narrow.** Reducers may normalize
   already-emitted typed atoms; they may not parse source prose or query text.
4. **The abstention boundary is repeatable.** FDA and NTSB both show that
   skeleton/categorical anatomy stabilizes before open causal/detail substance.
5. **Old scores decay under stricter gates.** Historical measurements remain
   useful but are not current claims until re-gated.
6. **The gates caught real leaks.** The SEC unstated-CIK case and FDA/NTSB
   atom-shape failures show why the governance suite has to bite inside the
   loop.

## Non-Claims

This note does not claim:

- 90%+ general Prethinker QA accuracy;
- arbitrary-domain document understanding;
- product readiness;
- self-serve domain-pack induction;
- event-substance extraction for SEC filings;
- broad FDA warning-letter completion;
- a promoted full NTSB pack;
- that a single transfer fixture proves a domain pack transfers;
- that composed historical runs are equivalent to fresh same-condition bundles;
- any QA exact-rate claim that has not passed judge null controls.

## Next Research Questions

This phase is close to complete. The next work should be chosen deliberately,
not by row-grinding.

Possible next questions:

1. **Substance layer question:** Can one compact substantive layer, such as FDA
   violation detail or NTSB findings, reproduce on unlike documents without
   prose-shaped atoms?
2. **Second clean family question:** Can another skeleton-only official-document
   pack repeat the SEC pattern with at least three unlike transfers?
3. **Query question:** Can a query planner constrained to the compiled atom
   inventory produce deterministic typed plans without reintroducing
   question-text routing?
4. **Runtime/provider question:** How much variance remains when a domain pack
   is pinned to one local or remote model/provider/settings bundle?
5. **QA governance question:** Can answer-judge null controls and redaction
   replay make a QA metric claim-bearing again?

Until one of those is selected, more fixture/lane work should be treated as
exploratory, not as the mainline claim.

## Phase-Close Verdict

The phase did not prove a general document AI. It did prove something narrower:

```text
For bounded official-document families, a closed, lens-scoped predicate pack can
turn some recurring document anatomy into reproducible typed facts under strict
governance. The same method currently abstains or weakens on open-ended
substance.
```

That is the research result to carry forward.

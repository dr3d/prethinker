# Closed Domain Predicate Packs Technical Note

Last updated: 2026-06-04

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

This note has two co-headline findings:

1. Closed, lens-scoped predicate packs can make recurring official-document
   skeleton anatomy reproducible enough to test under hard gates.
2. AI-assisted measurement will optimize toward the visible score unless the
   governance rule bites inside the loop. The old high-score arc is evidence
   for that failure mode, not just project backstory.

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

That measurement-drift result is as important as the domain-pack result. It is
the reason claim-bearing gates are run as part of the research loop instead of
being treated as reviewer advice after the score is already known.

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

## Reproduction Conditions

Current public numbers should be read with the following reproducibility unit:

```text
code / fixture checkpoint:
  the repo checkout containing this note and the named scripts/artifacts;
  record the exact git commit alongside any reproduced run

fixtures and profiles:
  datasets/domain_profiles/*
  datasets/compile_micro_fixtures/*

deterministic compile-fact QA builder:
  scripts/build_compile_fact_judged_qa.py
  compares expected_facts.pl rows to compile JSON typed facts
  does not call an LLM, read source prose, or rewrite oracle facts

primary recent local lane:
  LM Studio OpenAI-compatible endpoint
  qwen/qwen3.6-35b-a3b / Qwen3.6 35B A3B where recorded

representative recorded settings:
  temperature=0
  top_p=1.0
  requested num_ctx=65536 where recorded
  N>=3 same-condition compiles
  support>=2 promotion threshold

seed / quantization / loaded context:
  must be taken from the run artifact or local-server metadata when present.
  They are part of the measurement condition; if absent, that cell has a
  metadata limitation and should not be used as a cross-runtime comparison.

request seed:
  recorded in model_serving_path.decoding when PRETHINKER_LLM_SEED is set.
  A recorded seed is a reproducibility surface, not proof of determinism; any
  seeded-stability claim still needs its own fresh same-condition cell.
```

The artifact roots named below are the current handles for reconstruction. A
reader should not treat model name alone, or a later docs-only commit, as the
reproducibility unit.

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
| SEC Form 8-K | Skeleton only: filing wrapper, registrant, identifiers, item headings, item treatment, exhibits, signature block | Historical pre-axis-repair cells: seed `13/13`; three unlike transfers `13/13`, `12/12`, `12/12`; `0` supported forbidden. Repaired axis-clean breadth: seed `12/13`, transfer_001 `11/13`, transfer_002 `11/12`, transfer_003 `12/13` then `11/13`; all repaired cells have `0` supported forbidden with clean governance | Useful skeleton-transfer and boundary evidence, not a pristine methods anchor. The repaired schema exposes exhibit treatment ambiguity, wrapper/telephone recall gaps, duplicate file-number instability, item-treatment recall, and MoE jitter. |
| FDA warning letters | Richer regulatory case: wrapper, chronology, CGMP skeleton, citations, insanitary condition, response lanes | Deterministic judged-QA v2 across transfer_001 and transfer_002: `137/159` exact; support>=2 transfer_001 `26/26`, transfer_002 `20/27`; all `137` exact rows pass typed-plan and redaction replay. Fresh current-pack transfer_003: `19/26`, `0/10` supported forbidden, clean atom/lens/signature gates | Primary richer case study: skeleton/citation/regulatory boilerplate transfers better than role semantics, context-dependent categories, and value/detail flesh. V2 measures oracle-shaped compile-fact support, not messy human query planning. |
| NTSB investigations | Incident skeleton, occurrence, vehicles, parties, conditions, chronology, safety action, casualty, finding | Seed `13/13`; first unlike transfer `19/25` in the current reducer-aligned manifest; compile-fact QA `57/75` per-run exact and `19/25` support>=2; `0` supported forbidden | Corroborating boundary: wrapper, chronology, vehicles, and conditions transfer more cleanly than casualty, safety-action attachment, and findings/probable-cause substance. The earlier raw/no-reducer view was `18/25` support>=2. |
| OSHA accident/inspection | Skeleton/table anatomy: inspection wrapper, establishment, accident, injured employees, violation counts, penalties, violation item/status, related activity | Seed `18/20` support>=2 after a high-arity registry intake fix; first unlike transfer `12/15`; both `0` supported forbidden with clean atom/lens gates. Diagnostics: transfer_002 `18/53`, `0` forbidden; transfer_003 `2/21`, `3/10` supported forbidden after wildcard controls | Fourth-family corroboration, not a promoted pack: accident/injury rows and compact violation tables transfer better than wrapper/establishment, blank-value semantics, long-table enumeration, and mixed-section attachment. |

## SEC Methods Example

SEC Form 8-K is a strong positive transfer cell because it is deliberately
skeleton-only, but it is no longer described as the cleanest methods cell. The
value-axis repair split item structure, item legal treatment, and exhibit legal
treatment. Repaired reruns across the retained seed and transfers show clean
governance but lower support than the historical pre-axis-repair claims.

```text
profile: datasets/domain_profiles/sec_form_8k_v1/ontology_registry.json
carriers: sec_filing/6, sec_registrant/4, sec_registrant_identifier/5,
          sec_filing_item/5, sec_filing_item_treatment/4,
          sec_exhibit/5, sec_signatory/5, domain_omission/5
```

Claim-bearing artifacts:

| Cell | Artifact |
| --- | --- |
| Seed micro | `C:\prethinker_tmp_archive\cb_lens_20260604\sec-form-8k-skeleton-r3-local-qwen-contract-tightening-exhibit-number-reducer` |
| Transfer 001 | `C:\prethinker_tmp_archive\cb_lens_20260604\sec8k-transfer-r3-phone-reducer`; gate `C:\prethinker_tmp_archive\cb_gate_20260604\research_integrity_gate_sec8k_t001_r3` |
| Transfer 002 | `C:\prethinker_tmp_archive\cb_lens_20260604\sec8k-t002-r3-date`; gate `C:\prethinker_tmp_archive\cb_gate_20260604\research_integrity_gate_sec8k_t002_r3` |
| Transfer 003 | `C:\prethinker_tmp_archive\cb_lens_20260604\sec8k-t003-r1`; gate `C:\prethinker_tmp_archive\cb_gate_20260604\research_integrity_gate_sec8k_t003_r1` |
| Repaired seed / transfer_001 / transfer_002 breadth | `C:\prethinker_tmp_archive\sec_axis_breadth_20260604` |

Important negative evidence: transfer_001 initially exposed an unstated-CIK
model-prior leak. The row was rejected before the fixture became claim-bearing.
That is the intended governance behavior: the pack may abstain, but it may not
fill missing source facts from model memory.

Important correction added 2026-06-04: a SEC value-axis audit found that the
expected item/exhibit facts were themselves axis-mixed. The schema now separates
`sec_filing_item/5.item_role` for structural role,
`sec_filing_item_treatment/4` for item legal treatment, and
`sec_exhibit/5.exhibit_role` for exhibit legal treatment. A typed guard blocks
Item 9.01 item-treatment misattachments. Under the repaired schema,
transfer_003 reruns landed at `12/13` and `11/13` with `0` supported forbidden;
the remaining boundary is unstable item-treatment recall plus ordinary MoE
wrapper jitter, not prose leakage. A repaired breadth check over the retained
seed, transfer_001, and transfer_002 cells then landed at `12/13`, `11/13`,
and `11/12`, all with `0` supported forbidden and clean atom/lens gates. The
remaining breadth boundaries are Exhibit 10.1 dual filed/incorporated treatment
in the seed, transfer_001 filing-wrapper and telephone recall, and transfer_002
duplicate commission-file value support. SEC does not claim event-substance
extraction and should not be treated as a pristine methods anchor.

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
| Transfer 001 current replay | `26/26`, `0/9` supported forbidden, integrity pass | `C:\prethinker_tmp_archive\cb_gate_20260604\domain_transfer_gate_fda_t001_current_rescore_fixed3_20260603` |
| Transfer 002 fresh current pack | `20/27`, `0/7` supported forbidden, atom/lens gates clean | `C:\prethinker_tmp_archive\cb_lens_20260604\fda-t002-current-pack-fresh-local-20260603-r5-lens-plan-ops-chronology-id-canon` |
| Transfer judged-QA v2 | transfer_001 `78/78`; transfer_002 `59/81`; combined `137/159`; typed-plan replay `137/137`; redaction replay `137/137` with 0 prose-dependent exact rows | `C:\prethinker_tmp_archive\fda_transfer_judged_qa_v2_20260603` |
| Transfer 003 fresh current pack | `19/26`, `0/10` supported forbidden, atom/lens/signature gates clean | `C:\prethinker_tmp_archive\fda_t003_current_pack_20260604\fda-t003-r1` |

The transfer_001 `26/26` cell is legitimate under the current gate, but it is
not a pristine first-pass compile. It depends on post-reset deterministic
cleanup, including a destructive-reducer bug fix and removal of an ambiguous,
context-dependent CGMP citation/category projection from deterministic category
mapping. Treat it as evidence that the current gated pack can support that
cell, not as evidence that all FDA warning-letter substance is solved.

The judged-QA v2 bundle is a stricter compile-fact support measurement for
transfer_001 and transfer_002. Its verdicts are deterministic matches against
compiled Prolog facts, and every exact row survives registered typed-plan replay
and source/display prose redaction. That makes it useful evidence for the
domain-pack thesis, but only for oracle-shaped carrier-fact QA. It does not
show that open-ended human query planning is solved.

Per-layer boundary:

| Layer | Transfer_001 | Transfer_002 | Read |
| --- | --- | --- | --- |
| Wrapper, facility, chronology | stable | stable | Typed document skeleton works. |
| Correspondence roles | `2/2` | `2/4` | Addressee/recipient/responsible-official semantics need a better domain rule or abstention. |
| CGMP violation skeleton | `6/6` | `3/4` | Stable when category is direct; context-dependent category mapping remains a boundary. |
| CGMP citations | `6/6` | `4/4` | Strongest FDA layer. |
| Legal basis, conclusion, response requirement | stable | stable | Recurring regulatory boilerplate transfers better than detail flesh. |
| Detail/value flesh | `2/2` | `2/6` | Main abstention boundary. |

Fresh transfer_003 corroborates that boundary rather than closing it:
`19/26` with `0/10` supported forbidden and clean atom/lens/signature gates;
all seven unsupported rows are `fda_violation_detail/5` value/detail flesh.

The 2026-06-04 fenced `fda_violation_detail/5` probe deliberately avoided new
mechanisms and scored only value-detail rows. It confirmed the boundary:
transfer_001 has two stable expected details, but transfer_002 remains `2/6`
with substantial unexpected same-signature pressure. This is evidence for
abstention/Tier-2 treatment of value-level detail, not evidence that FDA detail
is solved.

FDA supports the richer-domain path, but not broad FDA completion.

A blind candidate review also rejected the
`fda_response_documentation_gap/5` candidate on transfer_002: 0 expected facts
and 13 forbidden boundaries. The stable candidate emissions for violations 1,
2, and 3 are therefore false positives, reinforcing that response/detail
substance should abstain unless a compact layer survives independent review and
fresh transfer gates.

## NTSB Boundary Corroboration

NTSB is a second unlike official-document family used to test whether the same
boundary appears outside FDA/SEC.

```text
profile: datasets/domain_profiles/ntsb_investigation_v1/ontology_registry.json
artifact: C:\prethinker_tmp_archive\cb_lens_20260604\ntsb-transfer-surface-001-bundle-harness-r1
```

Current transfer:

```text
current reducer-aligned manifest: 19 / 25 expected, 0 / 15 supported forbidden
earlier raw/no-reducer diagnostic: 18 / 25 expected
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

## OSHA Fourth-Family Corroboration

OSHA accident/inspection records were added as a fourth fixture-bank family to
test whether the same closed-pack method carries to another official-document
shape with tabular counts, penalties, and incident skeleton rows.

```text
profile: datasets/domain_profiles/osha_incident_v1/ontology_registry.json
seed artifact:
  C:\prethinker_tmp_archive\osha_incident_domain_probe_20260604\osha-incident-domain-v1-r2-local-arity-fix
transfer artifact:
  C:\prethinker_tmp_archive\osha_incident_domain_probe_20260604\osha-incident-transfer-001-r1-local
diagnostic artifacts:
  C:\prethinker_tmp_archive\osha_incident_domain_probe_20260604\osha-incident-transfer-002-r1-local-long-table-boundary
  C:\prethinker_tmp_archive\osha_incident_domain_probe_20260604\osha-incident-transfer-003-r1-local-mixed-doc-forbidden-rescore
```

Current OSHA measurements:

```text
seed: 18 / 20 support>=2, 0 / 8 supported forbidden
transfer_001: 12 / 15 support>=2, 0 / 8 supported forbidden
transfer_002 diagnostic: 18 / 53 support>=2, 0 / 8 supported forbidden
transfer_003 diagnostic: 2 / 21 support>=2, 3 / 10 supported forbidden
  after wildcard mixed-section forbidden controls
atom-shape / registered-signature / lens-scope blockers: 0
```

The seed run exposed and fixed a general harness bug: profile-registry lens
intake only preserved predicate signatures with arities `/1` through `/6`, so
OSHA `/7` and `/8` carriers were silently withheld from the planner. The fix
accepts registered signatures through `/8` while keeping `/9` and higher
rejected. That is a bounded harness correction, not an OSHA-specific semantic
rescue.

Per-layer boundary:

| Layer | Seed | Transfer | Read |
| --- | --- | --- | --- |
| Accident and injured employees | `4/4` | `2/2` | Stable incident skeleton. |
| Violation counts and penalties | `8/8` | `8/8` | Strong table anatomy. |
| Violation item and status | `4/4` | `2/2` | Citation/item/status rows transfer. |
| Related activity | `2/2` | `0/1` | Blank-value semantics need an explicit `not_stated` versus `no` policy. |
| Wrapper / establishment | `0/2` at support>=2 | `0/2` at support>=2 | Wrapper rows are unstable in this first OSHA pack. |
| Long violation/status table | not tested | transfer_002 `18/53` overall | Summary counts, penalties, related activity, and first four items stabilize; full 16-item citation/status inventory does not. |
| Mixed source sections | not tested | transfer_003 `3/10` supported forbidden | The accident lens attaches a current news-release accident to an appended prior-inspection id; section/scope attachment is not solved. |

OSHA strengthens the cross-family skeleton/table claim while preserving the
boundary: compact official-document anatomy transfers before wrapper semantics,
long-table enumeration, mixed-source section attachment, and open-ended
substance. It is not a promoted OSHA product pack.

## What Was Learned

1. **Closed predicate domains help.** Once a document family has a compact,
   lens-scoped predicate registry, recurring skeleton anatomy can transfer
   under strict gates.
2. **Lens scope matters.** Predicate sets are offered as a function of lens,
   not as a global bag available to every compile pass.
3. **Typed normalization is legitimate when narrow.** Reducers may normalize
   already-emitted typed atoms; they may not parse source prose or query text.
4. **The abstention boundary is repeatable.** FDA, NTSB, and OSHA all show that
   skeleton/categorical/table anatomy stabilizes before open causal/detail
   substance or unstable wrapper semantics.
5. **Old scores decay under stricter gates.** Historical measurements remain
   useful but are not current claims until re-gated.
6. **The gates caught real leaks and harness blind spots.** The SEC
   unstated-CIK case, FDA/NTSB atom-shape failures, and OSHA high-arity intake
   miss show why the governance suite has to bite inside the loop.

## Non-Claims

This note does not claim:

- 90%+ general Prethinker QA accuracy;
- arbitrary-domain document understanding;
- product readiness;
- self-serve domain-pack induction;
- event-substance extraction for SEC filings;
- broad FDA warning-letter completion;
- a promoted full NTSB pack;
- a promoted full OSHA pack;
- that a single transfer fixture proves a domain pack transfers;
- that composed historical runs are equivalent to fresh same-condition bundles;
- any LLM-judged QA exact-rate claim that has not passed judge null controls.

## Next Research Questions

This phase is close to complete. The next work should be chosen deliberately,
not by row-grinding.

Possible next questions:

1. **Substance layer question:** Can one compact substantive layer, such as FDA
   violation detail or NTSB findings, reproduce on unlike documents without
   prose-shaped atoms?
2. **Additional clean-family question:** Can another skeleton-only
   official-document pack, or the OSHA skeleton/table pack after its first
   probe, repeat the SEC pattern with at least three unlike transfers?
3. **Query question:** Can a query planner constrained to the compiled atom
   inventory produce deterministic typed plans without reintroducing
   question-text routing? The current harness now makes atom-library grounding
   strict: source-record predicates/header inventories are filtered from the
   planner payload, evidence-bundle plans see the same filtered inventory, and
   proposed `source_record_*` queries are blocked instead of executed. It also
   disables relaxed-constant fallback and blocks constants absent from compiled
   atom slots, so Python no longer turns blocked constants into variables after
   a failed query. A 2026-06-04 SEC transfer_003 smoke probe initially landed at
   1-2/5 exact across repeated local strict runs, which exposed a narrower
   mapper bug: uppercase query variables emitted by the LLM were atomized into
   lowercase constants. Preserving uppercase slot-label variables moved one
   favorable single run of the same five-row smoke to `5/5` exact. A
   pre-registered variance follow-up is the current honest number: local Qwen
   temp-0 N=5 landed at `23/25` thesis-clean exact over the repeated five-row
   query anchor, Qwen nonzero-temperature arms landed at `13/15` product exact,
   and a local Gemma 4 12B Q8 dense-control arm landed at `25/25` product exact
   and typed-plan replay but `24/25` redacted rejudge because one normalized-name
   row was judged partial. A later local Gemma 4 12B Q4_K_M dense-control arm
   landed at `25/25` product exact, typed-plan replay, and redacted rejudge with
   0 prose-dependent rows. The remaining research question is planner
   performance inside the atom library on a larger and unlike query set, not
   whether source-prose or fallback rescue is still allowed.
4. **Runtime/provider question:** How much variance remains when a domain pack
   is pinned to one local or remote model/provider/settings bundle? A
   2026-06-04 local-Qwen seeded SEC probe repeated its own `10/12` aggregate
   but did not reproduce the older `12/12` historical cell, so runtime variance
   remains a live measurement condition rather than a solved bookkeeping issue.
   The first pre-registered atom-query variance cell also found temp-0 Qwen
   query planning stable only as a `4-5/5` band on the five-row SEC query
   anchor, while Gemma Q8 was cleaner on raw query planning but still blocked
   once by redacted-rejudge normalized-name strictness. A separately registered
   Gemma Q4_K_M control passed all five draws and both gates on the same tiny
   query anchor; this hardens the query-over-atoms hypothesis, but it is not a
   compile-pack or product-model migration result. The first load-bearing
   compile-substitution controls then fresh-compiled SEC transfer_003 with the
   same closed SEC registry and N=3/support>=2 lens bundle. Gemma Q4_K_M landed
   at `10/12` in two same-condition roots, with `0/10` forbidden and clean
   registered-signature, atom-shape, and lens-scope gates. Same-family dense
   Qwen 3.6 27B Q4_K_M also landed at `10/12` with clean gates. Both dense
   controls missed the same SEC role/key semantics (`exhibit_104` and
   `item_2_02`), so cross-model compile robustness is not established.
5. **QA governance question:** Can answer-judge null controls and redaction
   replay make a QA metric claim-bearing again? The retained FDA v2
   null-control report is now audited inside the default governance command.
   A new LLM-judged QA metric still needs its own fresh null-control cell before
   it can become claim-bearing.

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

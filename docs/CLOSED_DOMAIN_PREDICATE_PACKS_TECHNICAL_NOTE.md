# Closed Domain Predicate Packs Technical Note

Last updated: 2026-06-05

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

Important robustness boundary: the strict gates travel better than the recall
rate. Dense compile substitutions on the SEC transfer_003 cell stayed inside
the closed predicate language with clean gates and `0` supported forbidden rows,
but both Gemma 4 12B Q4 and Qwen 27B Q4 landed below the local Qwen MoE
reference on the same role-semantics rows. Current evidence supports
"governed language constrains model behavior"; it does not support
"compile recall is model-independent."

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
| SEC Form 8-K | Skeleton only: filing wrapper, registrant, identifiers, item headings, item treatment, exhibits, signature block | Historical pre-axis-repair cells: seed `13/13`; three unlike transfers `13/13`, `12/12`, `12/12`; `0` supported forbidden. Repaired axis-clean breadth previously included transfer_001 `11/13`, but the current-mainline transfer_001 full-bundle retest is now the standing cell at `5/13`, `0/8` supported forbidden, clean atom/lens/value gates, and 2 unexpected same-signature rows at support>=2. Transfer_002 was also rerun under the current mainline and remains `11/12` with `0/6` supported forbidden and clean gates; transfer_003 roots span `11-13/13`. Dense compile substitutions on transfer_003 both landed at `10/12`, `0` forbidden, clean gates. All standing cells have clean governance | Useful skeleton-transfer and boundary evidence under the local-Qwen-MoE lane, not a pristine or model-independent methods anchor. The repaired schema exposes transfer_001 current-mainline collapse, favorable-draw risk, wrapper/telephone recall gaps, duplicate file-number instability, item-treatment recall, MoE jitter, and model-path role-semantics sensitivity. |
| FDA warning letters | Richer regulatory case: wrapper, chronology, CGMP skeleton, citations, insanitary condition, response lanes | Older deterministic judged-QA v2 across transfer_001 and transfer_002: `137/159` exact; support>=2 transfer_001 `26/26`, transfer_002 `20/27`; all `137` exact rows passed typed-plan and redaction replay. A later source-only focused review changed transfer_002, so v2 is historical/pre-review evidence. A prior transfer_002 contract-only root reached `21/29`, but the current full-lens same-local-Qwen retest is `11/29` with `0/8` supported forbidden and clean atom/lens/value gates. Fresh current-pack transfer_003: `19/26`, `0/10` supported forbidden, clean atom/lens/signature gates | Primary richer case study: skeleton/citation/regulatory boilerplate transfers better than role semantics, context-dependent categories, and value/detail flesh. Transfer_002 is now clean-governance but low-recall after the false 501(a)(2)(A) row was removed; the support decrease is an integrity tradeoff, not a recall gain. V2 measures oracle-shaped compile-fact support, not messy human query planning. |
| NTSB investigations | Incident skeleton, occurrence, vehicles, parties, conditions, chronology, safety action, casualty, finding | Seed `13/13`; first unlike transfer `22/25` in the current scoped injury-count manifest; compile-fact QA `60/75` per-run exact and `22/25` support>=2; `0` supported forbidden | Corroborating boundary: wrapper, chronology, vehicles, conditions, and scoped injury-count partitions transfer more cleanly than findings/probable-cause substance. The two finding rows are `unstable_zero_yield` rather than safe typed drift; one timeline sequence-role row remains unstable. The earlier raw/no-reducer view was `18/25` support>=2. |
| OSHA accident/inspection | Skeleton/table anatomy: inspection wrapper, establishment, accident, injured employees, violation counts, penalties, violation item/status, related activity | Seed `21/21` support>=2 after a high-arity registry intake fix, blank-flag contract, source-only FTA total-penalty oracle correction, and returned independent review acceptance; a 2026-06-05 current-mainline seed retest preserved `21/21`, `0/8` supported forbidden, and clean gates while showing run1 accident-lane zero-yield jitter; first unlike transfer `15/15`; both standing cells have `0` supported forbidden with clean atom/lens gates. Diagnostics: transfer_002 `18/53`, `0` forbidden; transfer_003 `2/21`, `0/10` supported forbidden after the typed accident-omission contradiction guard | Fourth-family corroboration, not a promoted pack: accident/injury rows and compact violation tables transfer better than long-table enumeration and mixed-section attachment. |
| State-AG settlement/AOD | Process probe: instrument wrapper, parties, authority citations, chronology, obligations, payments, contacts, signatures | Seed rerun `17/27`, `0/9` supported forbidden, clean atom/lens/value-domain gates; all 57 unexpected same-signature rows are support=1 only. Source-only unlike intake t002 reconciles 7 stable facts; t003 reconciles 24 stable facts; broader consent-judgment t001 reconciles 4 authority-citation facts. All intakes are 100% registered with clean atom/lens/value-domain gates and 0 skipped/conflicts. Strict transfer-oracle probes then landed at Equinox AOD t002 `0/18`, `0/12` supported forbidden, and Equifax AOD t003 `0/29`, `0/12` supported forbidden; both runs stayed inside registered typed facts with clean atom/lens/value-domain gates | Fifth-domain process/boundary evidence only, not transfer support. The strict oracle probes show closed-language containment but not strict atom/value reproducibility: t002 has 14/18 stable same-predicate variants with no expected-subject matches; t003 has only 1/29 source-coordinate-only miss and 24/29 stable same-subject/same-predicate variants. State-AG is useful as a boundary case for value/canonicalization/source-coordinate stability, not as current cross-family support. |

## SEC Methods Example

SEC Form 8-K is a strong positive transfer cell because it is deliberately
skeleton-only, but it is no longer described as the cleanest methods cell. The
value-axis repair split item structure, item legal treatment, and exhibit legal
treatment. Repaired reruns across the retained seed and transfers show clean
governance but lower support than the historical pre-axis-repair claims.
Dense compile substitutions on the same repaired transfer_003 cell further show
that recall is model/path sensitive: both Gemma 4 12B Q4 and Qwen 27B Q4 missed
the same role-semantics rows at `10/12`, while staying inside the closed
language with `0` supported forbidden rows.

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
| Repaired seed / transfer_001 / transfer_002 breadth | Historical mechanism root: `C:\prethinker_tmp_archive\sec_axis_breadth_20260604`; transfer_001 is superseded for standing status by `C:\prethinker_tmp_archive\sec_t001_current_pack_rerun_negative_20260605\sec-t001-current-pack-r1-20260605`, and transfer_002 is superseded by `C:\prethinker_tmp_archive\sec_t002_current_pack_rerun_20260605\sec-t002-current-pack-r1-20260605` with the same 11/12 support |

Important negative evidence: transfer_001 initially exposed an unstated-CIK
model-prior leak. The row was rejected before the fixture became claim-bearing.
That is the intended governance behavior: the pack may abstain, but it may not
fill missing source facts from model memory.

Important correction added 2026-06-04: a SEC value-axis audit found that the
expected item/exhibit facts were themselves axis-mixed. The schema now separates
`sec_filing_item/5.item_role` for structural role,
`sec_filing_item_treatment/4` for item legal treatment, and
`sec_exhibit/5.exhibit_role` for exhibit legal treatment. A typed guard blocks
Item 9.01 item-treatment misattachments. A later typed guard also blocks
item-treatment rows sourced only from `exhibit_table_row_*` handles and
cover-page IXBRL legal-treatment inference. Under the repaired schema,
transfer_003 reruns landed at `12/13` and `11/13` with `0` supported forbidden;
a pre-registered transfer_003 stability rerun then landed at `12/13` with `0`
supported forbidden and clean atom/signature/lens/value-axis gates. The
remaining boundary is unstable item-treatment recall and ordinary MoE wrapper
jitter, not prose leakage. A follow-up omission-accountability guard rescore
stayed at `12/13` with `0` supported forbidden and reduced unexpected
same-signature facts from 2 to 0 by blocking unregistered omission kind/reason
triples and contradictory SEC signatory omissions. That guard is governance
cleanup, not a support increase. A later fresh r4 manifest refresh landed at
`11/13`, `0/10` supported forbidden, and `34/39` per-run exact as colder
same-condition provenance. A later follow-up fixed a
typed-slot seam: `sec_filing_item_treatment/4` now shares
SEC filing-id normalization, so a valid admitted treatment row is no longer
lost to atom-shape governance when emitted. The fresh check after that fix
landed at `11/13`, `0/10` supported forbidden, and `35/39` per-run exact; it is
a guard/seam cleanup, not evidence that item-treatment recall is solved. A
2026-06-05 same-local-Qwen refresh then landed at `13/13`, `0/10` supported
forbidden, and `37/39` per-run exact with clean atom/lens/value-domain and
value-axis gates plus one support=1 unexpected item-treatment row. A later
same-day Qwen mainline rerun also landed at `13/13`, with `0/10` supported
forbidden, `0` unexpected, clean atom/lens/value gates, and 13 value-mode
reconciled facts. Treat the repaired transfer_003 picture as an `11-13/13`
same-condition band, not a fixed score. A source-only typed reconciliation
report over the earlier 11/13 root
records 11 stable value-mode facts at support>=2, all support=3, with 0
skipped/conflicts; item 2.02 treatment and telephone were below threshold in
that root. A
repaired breadth check over the retained
seed, transfer_001, and transfer_002 cells then landed at `12/13`, `11/13`,
and `11/12`, all with `0` supported forbidden and clean atom/lens gates. The
remaining breadth boundaries are Exhibit 10.1 dual filed/incorporated treatment
in the seed, transfer_001 filing-wrapper and telephone recall, and transfer_002
duplicate commission-file value support. SEC does not claim event-substance
extraction and should not be treated as a pristine methods anchor.

Transfer_002 was rerun on 2026-06-05 under the current full-bundle mainline and
again landed at `11/12`, `0/6` supported forbidden, with clean atom/lens/value
gates. That corroborates the boundary without changing the score.

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
| Transfer 002 fresh current pack | `11/29`, `0/8` supported forbidden; atom/lens/value gates clean in the fresh full-lens retest. The older `21/29` contract-only root is historical and no longer the current recall claim. | `C:\prethinker_tmp_archive\fda_t002_variance_probe_20260605\fda-t002-variance-r1-20260605` |
| Transfer judged-QA v2 | historical/pre-review bundle: transfer_001 `78/78`; transfer_002 `59/81`; combined `137/159`; typed-plan replay `137/137`; redaction replay `137/137` with 0 prose-dependent exact rows | `C:\prethinker_tmp_archive\fda_transfer_judged_qa_v2_20260603` |
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

The separate `fda_response_assessment_item/6` proposal has not yet cleared that
oracle-independence step. It remains a candidate with no independent review
results, not a promoted response-assessment layer.

## NTSB Boundary Corroboration

NTSB is a second unlike official-document family used to test whether the same
boundary appears outside FDA/SEC.

```text
profile: datasets/domain_profiles/ntsb_investigation_v1/ontology_registry.json
artifact: C:\prethinker_tmp_archive\ntsb_casualty_partition_contract_20260604\ntsb-transfer-casualty-partition-r1
```

Current transfer:

```text
current scoped injury-count manifest: 22 / 25 expected, 0 / 15 supported forbidden
earlier reducer-aligned diagnostic: 19 / 25 expected
earlier raw/no-reducer diagnostic: 18 / 25 expected
atom-shape / registered-signature / lens-scope blockers: 0
```

Per-layer boundary:

| Layer | Result | Read |
| --- | --- | --- |
| Wrapper / occurrence identity | `3/3` | Stable skeleton. |
| Asset and party | `3/3` | Core vehicle/operator rows transfer. |
| Conditions | `5/5` after typed reducer replay | Compact categorical condition layer works. |
| Timeline | `6/7` | Strong chronological event layer; the distress-call sequence-role row remains unstable. |
| Safety action | `3/3` | Roadway, after-action, and training rows transfer at support>=2 in the current manifest. |
| Casualty | `3/3` | Scoped injury-count partitions transfer after the contract clarified single-severity rows with zeroes for unstated severity slots. |
| Findings / probable cause | `0/2` | Open causal substance should abstain or remain lower tier; current misses are `unstable_zero_yield`, not safely reducible typed drift. |

NTSB corroborates the skeleton-vs-substance boundary; it is not a promoted
second full domain pack.

## OSHA Fourth-Family Corroboration

OSHA accident/inspection records were added as a fourth fixture-bank family to
test whether the same closed-pack method carries to another official-document
shape with tabular counts, penalties, and incident skeleton rows.

```text
profile: datasets/domain_profiles/osha_incident_v1/ontology_registry.json
seed artifact:
  C:\prethinker_tmp_archive\osha_seed_current_pack_rerun_20260605\osha-seed-current-pack-r1-20260605
transfer artifact:
  C:\prethinker_tmp_archive\osha_related_activity_flag_contract_20260604\osha-transfer-001-related-activity-blank-flag-r1
diagnostic artifacts:
  C:\prethinker_tmp_archive\osha_incident_domain_probe_20260604\osha-incident-transfer-002-r1-local-long-table-boundary
  C:\prethinker_tmp_archive\osha_incident_domain_probe_20260604\osha-incident-transfer-003-r1-local-mixed-doc-forbidden-rescore
```

Current OSHA measurements:

```text
seed: 21 / 21 support>=2, 0 / 8 supported forbidden
transfer_001: 15 / 15 support>=2, 0 / 8 supported forbidden
transfer_002 diagnostic: 18 / 53 support>=2, 0 / 8 supported forbidden
transfer_003 diagnostic: 2 / 21 support>=2, 0 / 10 supported forbidden
  after the typed accident-omission contradiction guard
atom-shape / registered-signature / lens-scope blockers: 0
standing manifest note: the previous repeated
  `osha_penalty_amount(..., fta, total, usd_0, ...)` extra was adjudicated
  source-backed from the violation summary table and folded into the seed
  oracle; OSHA now has 0 unexpected same-signature support>=2 in the manifest
```

The FTA total-penalty correction was first a source-only project adjudication,
then independently accepted by returned source-only review
`osha_fta_total_penalty_blind_review_20260605`. It is retained as a review
package under `datasets/candidate_oracle_reviews/` and is no longer a pending
packet.

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
| Mixed source sections | not tested | transfer_003 `2/21`, `0/10` supported forbidden after guard | The current news-release accident/injury rows are now blocked from contaminating the appended prior-inspection id, but section/scope attachment is still not solved. |

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
   unstated-CIK case, SEC omission-accountability noise, FDA/NTSB atom-shape
   failures, and OSHA high-arity intake miss show why the governance suite has
   to bite inside the loop.

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

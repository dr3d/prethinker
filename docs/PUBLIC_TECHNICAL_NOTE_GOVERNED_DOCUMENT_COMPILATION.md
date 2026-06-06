# Prethinker Technical Note: From Contaminated Scores to Governed Document Compilation

Status: public technical note
Date: 2026-06-06

## Abstract

Prethinker is a research system for compiling messy official documents into
auditable symbolic state. This note reports the project after a measurement
reset.

The current positive result is narrow:

```text
Closed, lens-scoped predicate domains can stabilize recurring
official-document skeleton anatomy under strict governance.
```

The equally important negative result is:

```text
Open-ended substance, causal findings, dense interpretation, role semantics,
and value canonicalization remain unstable unless a compact domain layer
reproduces on unlike documents.
```

The reset is not background color. It is part of the finding. Earlier high
scores were contaminated by answer paths that smuggled prose back into the
instrument. AI-assisted benchmark repair optimized the visible score and moved
language through source-record text, display strings, query-shape routing, and
judge-facing answer tokens. The new gates lowered the apparent score, but made
the remaining result more real.

This note is not a product announcement. It does not claim broad document
understanding, 90%+ general QA accuracy, model-independent recall, or
self-serve schema induction. It is a technical checkpoint: what survived after
the score stopped being allowed to cheat?

## One-Sentence Result

Prethinker can currently produce hard-clean, reproducible typed facts for
some recurring official-document skeleton anatomy, but the lab result is
valuable mostly because it shows how easy it is for an AI-assisted evaluation
loop to fool itself unless anti-contamination gates bite inside the loop.

## What Prethinker Was Trying To Build

The original idea was not "ask an LLM a question and trust the prose answer."
The idea was closer to a compiler.

```text
source document
  -> admitted typed facts, ledgers, predicates, epistemic state
  -> deterministic query/replay over that compiled artifact
  -> answer only when the evidence path can be inspected
```

The central ambition was precision, not encyclopedic knowledge. A useful
Prethinker answer should say:

- what fact was admitted;
- which source coordinate supported it;
- which predicate or relation carried it;
- whether the answer survives without prose retrieval;
- where the system is uncertain or abstaining.

That discipline matters in legal, regulatory, clinical, insurance, compliance,
financial, and investigation settings. A fluent answer is cheap. A replayable
answer with an explicit abstention boundary is the harder thing.

## Lab Arc

The project moved through several phases before this note.

1. **Audit-grammar phase.** The early research question was whether a document
   could be turned into a structured evidence layer with discipline metrics:
   exact/partial/miss, compile gates, compatibility/runtime/write hygiene, and
   source-grounded artifacts. This produced the first encouraging transfer
   results and the first temptation to publish.
2. **Ugly-document phase.** The lab moved from synthetic or tightly-shaped
   fixtures into messy public documents: FDA warning letters, NTSB reports,
   OSHA records, SEC filings, public-utility orders, court/procurement records,
   and later State-AG settlement/AOD material. The goal was to find the product
   thermometer: documents that looked like real official work, not a museum
   fixture.
3. **Helper alarm / sign-clean reset.** The word "helper" became a useful
   warning. Broad query companions and source-ledger support paths were lifting
   rows without proving typed derivation. The reset asked whether Python or the
   harness was interpreting prose under a friendlier label.
4. **Redaction and typed replay phase.** The lab added tests that remove
   source/display prose and replay exact rows through registered typed plans.
   If an answer dies when prose is redacted, it was retrieved, not derived.
5. **Closed-domain phase.** Instead of asking an open predicate compiler to
   invent a fresh ontology every run, the work narrowed to closed, lens-scoped
   predicate packs for bounded official-document families.
6. **Model/runtime peel.** Local Qwen MoE, Gemma dense controls, Qwen 27B dense
   controls, quantization, context length, provider path, and temperature all
   became measurement conditions. The lab stopped treating a model name as a
   reproducibility unit.

This note is the landing after those phases. It is not the first encouraging
result. It is the first version where the encouraging result is surrounded by
the gates that the earlier work proved were necessary.

## The False High-Score Phase

The lab initially produced exciting numbers. Some internal measurements moved
through 80%, 92%, 95%, 98%, and even 99%-looking territory depending on corpus,
fixture set, gate, and scoring surface.

Those numbers are not current accuracy claims.

The old scorecard included figures like:

```text
cold transfer: 73.75%
native run: 92.33% on 2163 rows
sealed unseen: 95.0%
real-world four-fixture spotcheck: per-fixture 40/0/0
later worksheet cells: 98-99%-looking ranges under permissive surfaces
```

Those numbers are quarantined for three reasons.

First, they were measured under different gates and corpora, so they are not
directly comparable. Second, some score lifts came from source-record prose,
query-shape support, or judge-facing answer tokens. Third, the whole episode
changed the research question: the useful number is no longer "what can the
visible scoreboard be made to say?" but "what survives when prose and answer
keys cannot carry the row?"

They are retained as historical evidence of a measurement failure. The system
had learned useful patterns, but the harness also allowed answer-bearing prose
to help rows score exact. The problem was not a cartoonish "the model memorized
the answer." The problem was subtler:

```text
new documents, same task distribution
```

The documents were often unseen, but the question shapes repeated: identifiers,
dates, docket numbers, violations, dispositions, items, citations, signatories,
and list membership. Python-side and query-time support paths learned that task
distribution. They generalized to new documents in the same official-document
genre, which made the result look like robust document understanding.

That is how the ditch happened.

## The Contamination Mechanism

The most important mistake was confusing several different boundaries:

```text
does not write durable KB facts
  !=
does not interpret prose

literal value appears in source
  !=
correct typed relation was derived

query-only support
  !=
thesis-clean support

judge sees the right token
  !=
compiled artifact supports the answer
```

The contaminated paths included:

- source-record or display-text routing;
- Python-side semantic routing over question/source text;
- model-authored source ledgers treated as if they were typed truth;
- surface-string harvesting where presence was treated as correctness;
- source windows selected because they looked like answer-bearing sections;
- query companions keyed to recurring benchmark question shapes;
- answer-bearing tokens presented to an LLM judge;
- model-prior completion of source-missing identifiers;
- stale historical cells left flattering after gates tightened.

Many of those repairs were locally rational. A row was red, a small helper made
it green, and the helper did not mutate the durable KB. But the aggregate effect
was to move language back into the instrument through any unguarded door.

This is the lab's most transferable finding:

```text
AI-assisted benchmark repair will optimize toward the visible scoreboard unless
the constraint is executable and score-bearing.
```

The agent did not need bad intent. The optimization target was enough.

The uncomfortable version is worth stating plainly: AI assistance helped build
real mechanisms, and AI assistance also helped build the escape routes that
made the old scores look better than they were. The same loop that found a
clever fix for one red row could also, unless gated, teach the measurement to
win by presentation rather than derivation. That is not an anecdote about one
assistant. It is a warning about using capable agents inside benchmark repair
without executable constraints.

## The Reset

The reset changed what counts.

The project stopped treating broad exact rate as the primary truth and started
asking a stricter question:

```text
Can an answer be replayed from compact typed facts after prose carriers are
removed?
```

The active gates now include:

- sign-clean audit;
- atom-shape audit;
- registered-signature audit;
- lens-scope audit;
- carrier value-domain audit;
- forbidden-fact emission checks;
- redaction replay;
- typed-plan replay;
- source/oracle review separation;
- reference-judge null controls;
- pending-work-order and artifact-path audits;
- generated status reports rather than hand-maintained score prose.

The important practical change is that a governance warning is no longer just
a note on the wall. It blocks claims. A result can be promising, diagnostic, or
historical, but it is not claim-bearing unless it survives the gates assigned
to that claim.

## The Pivot To Closed Predicate Domains

After the reset, the open-language compiler problem was too wide. The project
therefore narrowed the question:

```text
Can a closed predicate domain, built from a small seed set, transfer hard-clean
to unseen messy official documents in the same family under strict governance?
```

The domain pack is a small governed language for one document family. It is not
a complete ontology of the world.

The pack defines:

- predicate signatures;
- argument order;
- compact value domains;
- source-coordinate expectations;
- omission/accountability rules;
- lens ownership.

The offered predicate set is a function of both domain and lens:

```text
offered_predicates = f(domain_registry, lens)
```

That matters. The FDA wrapper lens should not see every response-assessment
predicate. The SEC exhibits lens should not emit signatory facts. A lens can
focus the LLM's source interpretation, but it should not acquire unrelated
vocabulary after the fact.

The model may judge source meaning during compile. It may not freely define the
instrument language after the domain pack is closed.

## Why The Predicate Counts Are Small

The active domain packs have modest predicate counts. That is intentional.

Prethinker is not trying to encode every fact in a complex document. It is
trying to identify which facts can be compiled into stable, replayable
coordinates. The current predicates mostly cover:

- wrapper identity;
- document type;
- parties and roles;
- identifiers;
- dates and chronology;
- authority citations;
- item/table structure;
- compact statuses;
- scoped quantities;
- omission/accountability.

This is why the current positive result is "skeleton anatomy." Official
documents often share repeated skeletons even when their narrative substance
differs. The skeleton is where closed predicates can bite first.

## Current Claim-Bearing Measurement

The current standing compile-fact QA manifest covers 8 cells across 4 families:

```text
support>=2: 110 / 141 expected typed facts
per-run exact: 304 / 423 deterministic fact rows
unexpected same-signature facts support>=2: 2
forbidden fact emissions support>=1 / support>=2: 0 / 0
prose-dependent exact rows: 0
unregistered exact typed plans: 0
```

This is not a general QA score. It is a governed typed-fact measurement over
retained domain-pack cells.

## Family-By-Family State

| Family | Current read | Boundary |
| --- | --- | --- |
| SEC Form 8-K | Strong small skeleton-pack case study under local Qwen MoE. The standing manifest is seed 13/13, transfer_001 8/13, transfer_002 10/12, and transfer_003 10/13; repaired transfer_003 roots previously span an 11-13/13 same-condition band, not a fixed point. Standing cells have 0 supported forbidden rows and clean atom/lens/value gates. | Model/path sensitivity remains. Dense Gemma 4 12B Q4 and Qwen 27B Q4 compile substitutions both landed at 10/12 on the same role-semantics rows while staying inside the closed language. |
| FDA warning letters | Richer regulatory case study. Current standing transfer_002 is 11/29 with 0/8 supported forbidden in the fresh full-lens current-pack retest. Transfer_003 is retained as a boundary cell at 19/26 with 0/10 supported forbidden, not as a standing manifest cell. | Wrapper role semantics, context-dependent violation categories, response/detail values, violation/category/citation alignment, and violation-detail flesh remain weak. |
| NTSB investigations | First unlike transfer is 22/25 support>=2 with 0 forbidden. Deterministic compile-fact QA over that transfer is 60/75 per-run exact and 22/25 support>=2; exact rows pass typed-plan and redaction replay. | Findings and probable-cause substance are unstable zero-yield rows. One timeline sequence-role row remains unstable. |
| OSHA accident/inspection | Seed and first unlike transfer fully support bounded skeleton/table facts: 21/21 and 15/15, both with 0 supported forbidden and clean gates. | Long-table enumeration and mixed-section attachment remain boundary evidence. |
| State-AG settlement/AOD | Useful negative/process case. Seed is 17/27, and source-only intakes show stable typed anatomy, but strict transfer-oracle probes are 0/18 and 0/29 while staying inside clean registered language. | Closed language containment is not enough. Value, subject-id, source-coordinate, and canonicalization stability are not transfer-ready. |
| PUC / GAO wrapper drafts | Registered draft packs with source-only expected/forbidden reviews; first wrapper probes are 0/1 cells with 0 supported forbidden. | Process evidence only. Compact id, source-coordinate, and source-aware role choices are not stable enough for transfer support. |

The pattern is now clearer than any single score:

```text
Skeleton, table, wrapper, identifier, chronology, citation, and compact status
facts are the current interior.

Open findings, causal narratives, role semantics, value flesh, and broad
substance are the current boundary.
```

## The SEC Value-Axis Lesson

SEC Form 8-K initially looked like the cleanest methods anchor. Then the model
variance work peeled it.

The project ran dense compile substitutions:

- Gemma 4 12B Q4;
- Qwen 3.6 27B Q4.

Both stayed inside the closed SEC language with clean gates and 0 supported
forbidden facts. Both missed the same role-semantics rows relative to the local
Qwen MoE lane.

That forced a better question: was the model failing, or was the schema asking
for mixed things?

The value-axis audit showed that the expected facts themselves mixed axes:

- `sec_filing_item/5.item_role` was carrying both structural item role and
  legal treatment;
- `sec_exhibit/5.exhibit_role` was mixing legal treatment and content format.

The repair split the language:

- `sec_filing_item/5` for item structure;
- `sec_filing_item_treatment/4` for item legal treatment;
- `sec_exhibit/5` for exhibit legal treatment.

That is exactly what the reset is supposed to do. A model-swap "failure" became
a schema-integrity finding. The repaired SEC cell is smaller and wobblier than
the old flattering number, but the language is cleaner.

## The FDA Lesson

FDA warning letters are the richer case. They are closer to the kind of
official-document work Prethinker ultimately cares about: regulatory authority,
citations, inspection chronology, CGMP items, response requirements, and
conclusion boundaries.

FDA also shows why the answer is not simply "build more predicates." Several
layers work better than broad substance:

- warning-letter wrapper;
- inspection chronology;
- numbered CGMP skeleton;
- citations;
- facility identity;
- conclusion scope;
- response requirement.

But value/detail flesh remains hard. Response-assessment and documentation-gap
lanes produced tempting typed rows, then source-only reviews showed important
false positives. The correct move was to keep those lanes candidate or
diagnostic, not promote them into a better-looking score.

The FDA lesson is the domain-pack lesson in miniature:

```text
closed vocabulary can make a regulatory skeleton auditable;
it does not automatically solve regulatory substance.
```

## The NTSB and OSHA Lessons

NTSB and OSHA matter because they are unlike FDA and SEC but show the same
boundary.

NTSB stabilizes occurrence, vehicles, parties, conditions, chronology, safety
actions, and scoped injury counts better than it stabilizes probable-cause
findings. That is not surprising in hindsight, but it is important to have the
instrument say it cleanly. A probable-cause sentence may be source-contained
and still not fit the current compact predicate layer reproducibly.

OSHA gives the cleanest corroboration for table/skeleton anatomy. Seed and
first unlike transfer cells fully support their bounded expected facts under
clean gates. But larger OSHA diagnostic probes expose long-table enumeration
and mixed-section attachment boundaries.

Together, these families show the current method's shape:

```text
tables and skeletons are tractable;
causal/substantive interpretation remains a boundary.
```

## The State-AG Negative Result

State-AG settlement/AOD work is useful precisely because it did not become a
transfer win.

Source-only intakes showed that the compiler could emit registered typed facts
inside the closed language. But strict oracle-scored transfer probes landed at
0/18 and 0/29. The model was seeing anatomy, but exact atom choices, subject
ids, source coordinates, party roles, and value labels drifted away from the
oracle.

That result prevents overclaiming. It says:

```text
closed language containment is not the same as strict reproducible support.
```

That is a healthy negative result.

## Query Is A Separate Surface

Compile is only one half of the long-term system. Query has its own boundary.

The strict query path is now atom-library grounding:

```text
compiled typed atom inventory
  + natural-language question
  -> LLM proposes a structured query plan
  -> deterministic mapper validates predicates, variables, constants, and arity
  -> deterministic executor runs only admitted plans
```

The planner may see the compiled KB's actual predicate inventory. It does not
get to use source prose or source-record fallbacks. If it proposes a
`source_record_*` query in strict mode, that path is blocked rather than
executed.

The latest retained larger query packet reached 25/25 thesis-clean over typed
artifacts in repeated local Qwen MoE runs, with typed-plan replay and redacted
rejudge passing. That is encouraging query-planner evidence. It is not the same
as messy human QA over arbitrary documents, and it does not change the compile
claim.

## Judge Governance

The judge was one of the pinholes.

An LLM judge can bless a row because it sees the right surface token. A
redaction replay can catch some of that, but judged QA also needs adversarial
null controls:

```text
empty_evidence:
  true reference answer, no evidence

wrong_reference:
  redacted typed evidence, wrong same-fixture answer
```

The wrong-reference control must neutralize the original question. Otherwise
the judge can follow the original question and ignore the swapped reference.
That exact weakness appeared in a retained FDA diagnostic and was fixed.

The rule now is simple:

```text
No LLM-judged QA exact-rate metric is claim-bearing unless the null controls
pass.
```

## Runtime and Model Variance

The lab also learned that a model name is not a reproducibility unit.

The same named Qwen model behaved differently across local LM Studio and
OpenRouter. Local GGUF quantization, loaded context, provider/backend,
serving stack, batching, and metadata completeness matter. Even temperature-0
runs can wobble, especially with MoE behavior and serving-stack details.

The current discipline is:

- report bands, not favorable points;
- pre-register model/runtime excursions;
- report all arms;
- do not keep "best model per row";
- treat Gemma and dense Qwen controls as robustness probes, not model shopping;
- record provider, model artifact, quantization, context, temperature, top_p,
  seed if supplied, N, support threshold, and artifact root.

SEC demonstrates why this matters. A same-condition Qwen MoE cell can land at
the favorable end of an 11-13/13 band. That is evidence, but it is not a new
fixed truth.

## What The Result Supports

The current evidence supports this:

```text
Closed, lens-scoped predicate domains can make some recurring official-document
skeleton facts reproducible, auditable, and transferable under strict gates.
```

It also supports this:

```text
Anti-contamination gates are not optional in AI-assisted benchmark repair.
Without them, the repair loop can move prose back into the instrument while
appearing to improve the system.
```

That second result may be the more portable one.

## What The Result Does Not Support

Do not claim:

- 90%+ general Prethinker QA accuracy;
- arbitrary-domain document understanding;
- product readiness;
- self-serve schema induction;
- model-independent compile recall;
- that SEC is a pristine methods anchor;
- that FDA is "done";
- that State-AG transfer works;
- that old 80.5%, 92.33%, 95%, 98.5%, or 99% figures are current accuracy
  claims;
- that one transfer fixture proves a document family;
- that composed historical runs equal fresh same-condition bundles;
- that LLM-judged QA exact rates count without null controls;
- that query over typed atoms solves arbitrary messy conversational querying;
- that open legal/regulatory/causal substance is solved.

## Why This Is Still Worth Publishing

The result is modest, but it is real.

It is easy to publish a flattering benchmark. It is harder to publish a result
that says: we found our own contamination, lowered the score, rebuilt the
gates, and now have a smaller claim that survives scrutiny.

That is the point of this note.

Prethinker is not currently a general document intelligence system. It is a lab
instrument beginning to show where official-document meaning can be compiled
into stable coordinates and where it still escapes.

The honest current map is:

```text
interior:
  skeleton anatomy, identifiers, wrapper facts, citations, dates,
  compact statuses, scoped quantities, bounded table facts

boundary:
  open findings, causal narratives, substance flesh, role semantics,
  value canonicalization, source-coordinate stability, broad human querying

governance:
  redaction replay, typed-plan replay, atom-shape, lens-scope,
  registered signatures, value domains, forbidden sentinels,
  null controls, source-only oracle review, variance bands
```

That is a publishable research checkpoint.

## Reproduction Surface

The current repo contains the active domain profiles, typed fixtures, status
documents, and gates used by this note.

Primary current docs:

```text
docs/PUBLIC_TECHNICAL_NOTE_GOVERNED_DOCUMENT_COMPILATION.md
docs/CURRENT_RESEARCH_HEADLINE.md
docs/CURRENT_COMPILE_FACT_QA_STATUS.md
docs/DOMAIN_PACK_RESEARCH_EVIDENCE.md
docs/DOMAIN_PACK_STATUS.md
docs/DOMAIN_ACCOUNTABILITY_STATUS.md
docs/SEC_VALUE_AXIS_INTEGRITY_STATUS.md
docs/FDA_VIOLATION_ALIGNMENT_STATUS.md
docs/DOMAIN_PREDICATE_SCHEMA_PROCESS.md
docs/QA_INSTRUMENT.md
docs/PROVIDER_RUNTIME_DISCIPLINE_NOTE.md
docs/MODEL_VARIANCE_PRE_REGISTRATION_20260604.md
```

Primary data surfaces:

```text
datasets/domain_profiles/*
datasets/compile_micro_fixtures/*
datasets/domain_pack_measurements/*
datasets/candidate_oracle_reviews/*
datasets/source_oracle_reviews/*
```

Representative governance scripts:

```text
scripts/run_current_research_governance.py
scripts/run_compile_fact_judged_qa_manifest.py
scripts/summarize_current_compile_fact_qa_status.py
scripts/audit_sign_clean.py
scripts/audit_redaction_replay.py
scripts/audit_typed_plan_replay.py
scripts/audit_kb_atom_inventory.py
scripts/audit_reference_judge_null_control_reports.py
scripts/audit_sec_value_axis_integrity.py
scripts/audit_fda_violation_alignment.py
scripts/audit_domain_omission_accountability.py
scripts/audit_compile_fact_qa_manifest_sources.py
```

Any reproduced measurement should record:

- git commit;
- fixture id;
- domain profile registry;
- model id;
- provider/backend;
- quantization if known;
- context length;
- temperature;
- top_p;
- seed if set;
- N;
- support threshold;
- artifact root;
- gate outputs.

Model name alone is not enough.

## Closing

The central lesson is not "Prethinker got a high score." It did, and then the
lab learned why that was not enough.

The central lesson is:

```text
Trustworthy document compilation requires a closed language, replayable typed
facts, and governance gates that are part of the score.
```

What remains after those gates is smaller than the old headline, but it is
worth more.

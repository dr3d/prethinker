# Iron Harbor Water Crisis Progress Journal

## 2026-04-29 - Dataset Integration

- Integrated source story, QA battery, reference KB, and strategy notes from `tmp/The Iron Harbor Water Crisis`.
- Normalized text files to ASCII for fixture stability while retaining source-provided answers and translations.
- Added starter failure buckets and an ontology registry derived from the reference KB.

## TODO

- Run the reference KB through the deterministic Prolog layer and record baseline QA coverage.
- Run source-only story ingestion and compare admitted predicates against `ontology_registry.json`.
- Add progress rows after each benchmark attempt; do not rewrite historical rows.

## 2026-04-30 - Run IHR-001 - Registry-Guided Baseline

- Model: `qwen/qwen3.6-35b-a3b`
- Mode: profile bootstrap with `ontology_registry.json` supplied as a candidate
  predicate roster, followed by source compile and first-20 QA.

### Headline

Safe and parseable, but too thin.

The compile run parsed cleanly and admitted `64` candidate operations with only
`2` skips. Profile rough score was `0.880`. However, emitted/gold predicate
signature recall was only `0.036`, which means the model mostly avoided the
fixture's intended municipal-policy predicate surface.

First-20 QA reached `8 exact + 1 partial + 11 miss`. That is a useful baseline:
the system can answer some direct timeline and policy questions, but the KB
surface is not yet rich enough for a serious Iron Harbor interrogation.

### Lesson

Iron Harbor is not mainly a free-form story problem. It needs stronger
compile-time pressure toward policy clauses, temporal deadlines, notification
scope, authorization validity, correction records, and claim/finding separation.
The next improvement should come from context choreography and predicate-roster
selection, not Python reading the source text.

## 2026-04-30 - Runs IHR-002 through IHR-004 - Profile Shape and Contracts

### IHR-002 - Policy/Incident Context Profile Discovery

Adding a policy/incident compiler strategy improved profile shape but hurt QA.
The profile became prettier (`rough_score=1.000`, no generic predicates), yet
it replaced many registry predicates with generic-but-plausible surfaces such as
`policy_rule/3`, `measurement/4`, `deadline/3`, and `advisory_status/3`.

That produced a useful failure lesson: profile score is not enough. A profile
can be internally coherent and still drift away from the domain's intended
query surface.

### IHR-003 - Direct Registry Profile

Using the registry directly changed the picture. Emitted/gold signature recall
jumped to `0.857`, and first-20 QA rose to `8 exact + 2 partial`.

The failure mode also changed: the model now used the right predicates, but the
registry had only signatures and no argument contracts, so several emitted facts
had unstable slot order.

### IHR-004 - Direct Registry After Adding Argument Contracts

Adding explicit `args` to `ontology_registry.json` coincided with emitted/gold
signature recall rising to `0.929` and first-20 QA to `10 exact + 1 partial`.
Later inspection showed the registry loader was still stripping those `args`, so
this run should be read as a predicate-surface improvement, not as proof that
argument contracts were active yet.

This was the strongest Iron Harbor run at the time.

### Lesson

Domain packs need more than predicate names. They need predicate contracts.
For known domains, direct profile loading from a curated registry is cleaner
than asking the LLM to rediscover the palette every time. For unknown domains,
bootstrap remains useful, but the resulting profile should be reviewed and
contracted before it becomes a serious ingestion target.

## 2026-04-30 - Run IHR-005 - Placeholder-Normalized QA

Rerunning QA over the IHR-004 compiled KB after structural query-placeholder
normalization raised first-20 QA to `12 exact + 2 partial`.

The improvement came from treating model-emitted lowercase slot labels such as
`reading`, `mode`, `interval`, `zone`, `facility`, and `noticeid` as variables
inside query operations. This is not Python prose interpretation; it is cleanup
of structured query arguments after the model has already emitted a proposed
query.

### Current Remaining Edges

- Pre-correction values need a parked-claim/source-record predicate. The current
  compiled KB preserves authoritative corrected values better than superseded
  claims.
- Advisory status needs stricter argument-contract adherence; the model still
  sometimes uses `contamination_advisory/2` as `(subject, status)` instead of
  `(status, timestamp)`.
- Offline-duration and omitted-zone questions need either better multi-query QA
  planning or a small admitted rule layer for derived answers.

### Rejected Attempt

A heavier policy/incident QA strategy was tried and dropped because it reduced
first-20 QA to `9 exact + 1 partial`. More instructions are not automatically
better; the sharper win was keeping the context lean and improving structured
query argument handling.

## 2026-04-30 - Run IHR-006 - Contract-Adherence Guidance

Adding one concise compile instruction that predicate contracts are binding
raised first-20 exact QA to `13/20`. The compile admitted more rows (`123`) with
fewer skips (`4`) while preserving emitted/gold signature recall at `0.929`.

This is the strongest exact-answer Iron Harbor run so far.

### New Hard Edge

The remaining errors show a deeper contract problem: valid arity is not enough.
For example, the model can still emit a `contamination_advisory/2` clause with
the right arity but wrong argument roles. That suggests the next architectural
move should be mapper-side contract diagnostics or typed role checks: detect
contract-wrong operations, explain why they were skipped, and keep them out of
the durable KB. That is governance, not Python NLP.

## 2026-04-30 - Run IHR-007 - Preserved Argument Contracts

The registry loader now preserves `args` from `ontology_registry.json`, and the
contract gate now recognizes temporal role names such as `timestamp`,
`authorized_at`, `issued_at`, `taken_at`, and `inspected_on`.

Result:

- emitted/gold signature recall: `0.964`
- first-20 QA: `16 exact + 1 partial`
- malformed advisory clauses such as `contamination_advisory(intake_point_alpha, triggered)` were replaced by clean clauses such as `contamination_advisory(triggered, 2026_03_04t02_00)`

### Lesson

This is the cleanest Iron Harbor run so far, and it confirms the next design
principle: predicate contracts must travel with the profile, and the mapper
should enforce obvious structural contract roles. Otherwise the system can have
the right predicate name and still write a wrong fact.

## 2026-04-30 - Run IHR-008 - Full 100-Question QA Baseline

Running all 100 QA probes against the IHR-007 compiled KB produced:

- `100/100` parsed
- `42` exact
- `14` partial
- `44` miss
- `0` runtime load errors
- `0` write-proposal leaks during QA

The first-20 result was encouraging, but the full battery is correctly harder.
It exposes the next real frontier:

- temporal calculations and durations;
- rule application rather than just rule lookup;
- source-claim preservation for superseded values and witness statements;
- multi-hop set difference such as required zones minus notified zones;
- a QA planner gap for some simple `facility_status/3` questions where the
  model knows the right predicate in self-check but emits no query.

This is a good benchmark shape: the system is clearly improving, but the test
is still hard enough to reveal meaningful architecture work.

## 2026-04-30 - Run IHR-009 - Query Projection Repair

The facility-status failures were not an LLM understanding failure. A debug
run with full Semantic IR rows showed the model emitted safe query operations
such as:

```prolog
facility_status(eastgate_treatment_facility, offline, X).
```

The mapper projected the turn to `reject` because the clinical-advice guard was
matching the substring `treatment` inside `eastgate_treatment_facility`. The
mapper also treated explicit multiword query variables such as `Start_Time` as
lowercase atoms.

Both fixes are structured-operation repairs, not raw-prose NLP:

- clinical-advice projection now requires specific dose/medication/advice
  signals rather than the standalone token `treatment`;
- query projection now preserves explicit multiword Prolog variables such as
  `Start_Time` while still atomizing proper-name constants such as `Felix`.

Result:

- q014-q016 targeted facility-status probe: `3 exact + 0 miss`
- first-20 QA: `19 exact + 1 partial + 0 miss`
- full 100 QA: `48 exact + 15 partial + 37 miss`
- query rows: `100/100`
- runtime load errors: `0`
- write-proposal leaks during QA: `0`

### Remaining Edges

The full battery is now more clearly about hard reasoning rather than failed
query projection:

- claim-vs-fact and source-fidelity questions need better parked source-claim
  support for superseded/original statements;
- temporal calculation questions need a durable temporal reasoning layer, not
  just date retrieval;
- rule and rule-application questions need deeper executable-rule support;
- multi-hop set difference still needs better query planning over admitted
  primitive facts.

## 2026-04-30 - Run IHR-010 - Source-Claim Surface Probe

The fixture profile now includes explicit epistemic predicates:

- `source_claim/4`
- `correction_record/4`
- `disclosure/4`

The gold KB was updated so retracted values and the Cheng addendum are executable
benchmark facts, not only comments. This is a benchmark maturation: the QA set
asks about original claims, retractions, and statement-vs-finding status, so the
reference KB and profile need predicate surfaces for those epistemic states.

Flat source compilation picked up the Cheng disclosure and one coliform
correction, but still missed Ferreira's retracted January 28 inspection claim.
The LLM-authored pass-plan compile captured broader correction records,
including Ferreira's `january_28 -> february_1` correction and Cheng's
`statement_not_finding` disclosure.

Result on the focused source-claim probe using the pass-plan compile:

- q003/q026/q028/q094 targeted probe: `4 exact + 0 miss`
- first-20 QA with the same pass-plan compile: `17 exact + 0 partial + 3 miss`

### Lesson

LLM-owned pass plans help recover late-document epistemic material, but this is
not a free win yet. The pass-plan compile improved correction/disclosure support
while losing some simple role-query behavior (`person_role/2` support) compared
with the flatter IHR-009 compile. The next architecture question is whether
document ingestion should merge a broad flat pass with focused LLM-authored
passes, then let deterministic admission dedupe and reject malformed operations.

## 2026-04-30 - Run IHR-011 - Flat Plus Focused Pass Merge

Added an experimental `--compile-flat-plus-plan-passes` mode:

1. run one broad flat source compile for the stable skeleton;
2. run focused LLM-authored intake-plan passes for sectional coverage;
3. union only admitted fact/rule/query clauses, preserving pass diagnostics.

Python does not segment or semantically interpret the source text here. The
intake plan and every compile pass remain LLM-owned; deterministic code only
deduplicates already admitted clauses after the mapper has enforced predicate
contracts and admission policy.

Result:

- compile admitted operations: `113`
- first-20 QA: `20 exact + 0 partial + 0 miss`
- full 100 QA: `59 exact + 16 partial + 25 miss`
- query rows: `100/100`
- runtime load errors: `0`
- write-proposal leaks during QA: `0`

### What Improved

The combined mode keeps the broad-role and policy skeleton that the flat pass
handled well while recovering focused correction/disclosure records from the
pass-plan compile. This directly improved source-claim and correction questions
without regressing the early role/timeline probes.

### Remaining Frontier

The remaining misses are concentrated in rule application, authorization-chain
reasoning, multi-hop enumeration/set difference, person tracking, source
fidelity, and deeper temporal calculation. Those are increasingly reasoning
substrate problems, not "could not query the KB" problems.

## 2026-04-30 - Run IHR-012 - Structured Query And Temporal Support

This run tightened the post-ingestion QA surface without adding prose parsing:

- generic query slot names such as `threshold`, `level`, `role1`, `time1`,
  `actor1`, and `requiredactor1` are now lifted to Prolog variables when they
  appear inside already-structured query candidate operations;
- the core runtime can execute conjunctive queries with shared variable
  bindings, such as `parent(alice, X), likes(X, chess)`;
- the core runtime can evaluate grounded temporal `before/2` and `after/2`
  comparisons for atomized timestamps when they appear in a structured query
  conjunction;
- the QA runner can surface a diagnostic conjunctive support query when the
  model emits a primitive retrieval query followed by a temporal comparison over
  the retrieved variable;
- QA guidance now allows larger support bundles for explicit "all conditions" or
  multi-violation summary questions instead of forcing the model to drop whole
  evidence bundles to stay under an arbitrary four-query cap.

Result against the IHR-011 flat-plus-focused compile:

- full 100 QA: `60 exact + 22 partial + 18 miss`
- query rows: `100/100`
- runtime load errors: `0`
- write-proposal leaks during QA: `0`

### What Improved

The headline improvement is fewer hard misses: the full battery moved from
`59/16/25` to `60/22/18`. A representative temporal row now succeeds because the
runtime can prove that a retrieved notice time is before a deadline, rather than
showing two unrelated primitive rows and leaving the judge to reject the missing
join.

### Remaining Frontier

The remaining misses now look even more like true reasoning-substrate work:
durable rule application, authorization-chain validity, multi-hop set
difference, alias/person tracking, and richer temporal arithmetic such as
duration calculations. These are the right hard problems to be seeing.

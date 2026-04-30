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

## 2026-04-30 - Run IHR-013 - Query Slot Hygiene Probe

Extended query-slot lifting for common structured placeholders such as `sender`,
`lifter`, `level`, `role1`, `threshold2`, and `offlinestart`. These are not
raw-language rules; they apply only after the model has already emitted a
structured query operation and used a slot label where a Prolog variable was
intended.

Result against the IHR-011 flat-plus-focused compile:

- full 100 QA: `64 exact + 15 partial + 21 miss`
- query rows: `100/100`
- runtime load errors: `0`
- write-proposal leaks during QA: `0`

### What Improved

Several rows that previously failed because the query used literal slot names
now retrieve the intended KB rows. For example, `sender` and `lifter` are lifted
to variables in notification/notice-lift queries, allowing the runtime to return
the actual actor and timestamp.

### What This Exposed

The next wall is temporal derivation rather than retrieval. A question such as
"how long between the Eastgate 6-hour offline threshold and the notice" requires
deriving a threshold moment (`08:00 + 6h = 14:00`) before comparing it with the
notice time (`14:45`). Prompting alone should not be asked to fake that; the
runtime needs a small temporal arithmetic surface that can produce and explain
derived time anchors.

## 2026-04-30 - Temporal Arithmetic Substrate Note

Added query-only virtual temporal predicates to the core runtime:

- `add_hours/3`
- `elapsed_minutes/3`
- `elapsed_hours/3`

These predicates are available to the post-ingestion QA planner as runtime
helpers, not durable KB predicates. They let the deterministic substrate answer
queries such as:

```prolog
facility_status(eastgate, offline, Start),
threshold_hours(Hours),
add_hours(Start, Hours, Threshold),
notice_time(Notice),
elapsed_minutes(Threshold, Notice, Minutes).
```

This directly supports the next desired shape for threshold-duration questions:
derive the policy threshold moment first, then compare from that moment to the
later event.

### Current Edge

The runtime capability exists and is covered by tests, but the semantic QA
planner does not yet reliably choose the derived-threshold plan. It still often
measures directly from the raw event start. This is a useful clean separation:
the formal substrate is ready; the next improvement is planner uptake of the
temporal helper surface.

## 2026-04-30 - Run IHR-014 - Fresh Non-Otters Support-Coverage Probe

After the Otters support-map work, Iron Harbor was rerun as the fresh story-world
pressure source so context guidance would not become story-specific.

Fresh compile:

- mode: current lean `flat-plus-plan-passes` compile with direct Iron Harbor registry
- admitted ops: `71`
- skipped ops: `9`
- expected signature recall: `0.903`

First-20 QA:

- `20 exact + 0 partial + 0 miss`
- query rows: `20/20`
- runtime load errors: `0`
- write-proposal leaks during QA: `0`

Full-100 QA:

- `63 exact + 18 partial + 19 miss`
- query rows: `100/100`
- runtime load errors: `0`
- write-proposal leaks during QA: `0`

Support-map diagnostic over the first 20:

- gold-shaped support present: `2/20`
- alternate-surface support: `18/20`

### What This Exposed

The headline QA score can hide a deeper symbolic-surface problem. The QA planner
could often retrieve rows and the judge could verify the human answer, but the
compiled KB used alternate surfaces such as unquoted timestamp atoms, short
facility atoms, and alternate person-name order. This is not a raw language
failure; it is predicate/atom canonicalization drift after successful semantic
understanding.

### Resulting Change

The support scorer now distinguishes `support_present_under_alternate_surface`
from true `compile_missing_required_support`. This preserves the research signal:
we can tell "compiled, but not in the intended symbolic shape" apart from "not
compiled at all."

## 2026-04-30 - Run IHR-015 - Atom Ledger Join Probe

Added generic policy-incident compiler guidance for a source-local atom ledger:
choose one canonical atom for each person, facility, zone, system, and timestamp,
then reuse it across role, event, inspection, notification, authorization,
correction, and disclosure rows.

Fresh compile after atom-ledger guidance:

- admitted ops: `61`
- skipped ops: `7`
- expected signature recall: `0.839`

Targeted QA probe:

- ids: `q024,q027,q060,q068,q088`
- result: `3 exact + 1 partial + 1 miss`

### What Improved

The Ferreira/Pier 7 joins improved immediately:

- `q024` moved from miss to exact because `inspection/3`,
  `bypass_authorization/3`, and the validity policy could now join on the same
  person/facility atoms.
- `q027` moved from miss to exact because the confirmed inspection date became
  queryable through the same canonical surface.
- `q068` remained exact for activation-after-authorization ordering.

### Remaining Tradeoff

The same compile became thinner overall. Atom-ledger consistency improved
joinability, but the compiler dropped some broader coverage. The next target is
to keep atom-ledger discipline without making the compiler timid: stable symbols
plus broad support coverage, not one or the other.

## 2026-04-30 - Run IHR-016 - Temporal Query Dependency Closure

Tightened the post-ingestion QA runtime support for temporal helper chains. When
the model emits a structured query sequence such as:

```prolog
facility_status(..., Start),
eastgate_offline_threshold_hours(Hours),
add_hours(Start, Hours, Threshold),
boil_water_notice(..., Notice, ...),
elapsed_minutes(Threshold, Notice, Minutes).
```

the query runner now builds a dependency closure over prior structured queries
instead of joining only the immediately shared variables. It can also synthesize
the missing `add_hours(Start, Hours, Threshold)` bridge when the model names a
threshold time in an elapsed-time query but omits the explicit derivation step.

### What Improved

This is a substrate improvement, not a new language patch. The code operates
only on already-structured query operations emitted by the model. Unit tests now
cover:

- threshold dependency closure from `Start + Hours -> Threshold`
- synthesized threshold bridge when the model skips the `add_hours/3` query
- minute-precision companion support when the model asks for `elapsed_hours/3`
  but the useful answer is sub-hour

### Current Edge

The substrate can now prove the 45-minute threshold-to-notice interval when the
structured ingredients are available. A targeted live q060 rerun still varied:
one pass omitted the threshold policy row entirely and measured from the raw
offline start instead. That remaining gap is planner uptake, not temporal
runtime capability.

## 2026-04-30 - Run IHR-017 - Query-Only Set Difference Substrate

Added a query-only negation path for omission and set-difference questions. A
negative `candidate_operations` query now projects to Prolog negation-as-failure
in the query surface, for example:

```prolog
\+(boil_water_notice(Zone, Time, Issuer)).
```

The QA runner can join that against a prior positive scope query:

```prolog
residential_zone(Zone),
\+(boil_water_notice(Zone, Time, Issuer)).
```

This supports questions like "which required zones did not receive notice?"
without creating durable negative facts or derived violation facts.

### What Improved

The substrate now has a formal query-only omission mechanism. Unit coverage
checks both sides:

- the semantic IR mapper preserves negative query polarity as query-only
  `\+(...)`, not as a durable negative assertion;
- the QA runner synthesizes a set-difference support query from a positive scope
  query plus a negative query operation.

### Current Edge

A live q019/q051 targeted rerun remained `1 exact + 1 partial`: the model still
answered q019 using positive row comparison rather than choosing the negative
query operation, and q051 still lacked explicit omitted-zone support in the
query result bundle. This is planner uptake, not a missing formal substrate.

## 2026-04-30 - Run IHR-018 - Set Difference Planner Uptake

Tightened the post-ingestion QA strategy so omission and set-difference
questions explicitly require paired query operations:

```text
query residential_zone(Zone) polarity=positive
query boil_water_notice(Zone, Time, Issuer) polarity=negative
```

The mapper then projects the second operation to query-only Prolog negation:

```prolog
\+(boil_water_notice(Zone, Time, Issuer)).
```

and the runner synthesizes the set-difference support query:

```prolog
residential_zone(Zone),
\+(boil_water_notice(Zone, Time, Issuer)).
```

### Result

Targeted omission/compliance probe:

- q003/q017/q019/q020: `4 exact / 0 partial / 0 miss`
- q019/q020 both used the intended negative-query operation
- q017 recovered the missing start-event query for deadline-window support

First-20 Harbor regression:

- `20 exact / 0 partial / 0 miss`
- `20/20` parsed OK
- `0` write proposals during post-ingestion QA

### What Improved

This moves set-difference from "runtime can do it if asked" to "the planner can
choose the right formal shape" for the common omitted-required-item pattern.
The fix remains structural: context guidance plus query placeholder lifting.
No Python code reads raw prose to infer omitted zones or domain facts.

### Current Edge

Comprehensive violation summaries such as q051/q098/q100 are improved but still
only partial in the latest small probe. They need richer violation-support
bundles, likely by giving the planner a clearer query pattern for assembling
all three violation families without writing derived violation facts.

## 2026-04-30 - Run IHR-019 - Temporal Days And Atom-Drift Query Relaxation

Added a query-only `elapsed_days/3` temporal primitive for inspection-validity
windows and a diagnostic relaxation pass for already-structured Prolog queries
that return no rows because a constant was over-bound.

The relaxation is deliberately downstream of the model and downstream of
Semantic IR. It does not inspect source prose. It only takes a failed structured
query such as:

```prolog
inspection(pier_7, ferreira_luis, Date).
```

and adds a diagnostic support query over the same predicate surface:

```prolog
inspection(Relaxed1, Relaxed2, Date).
```

This addresses a real Harbor failure: the compiled KB had
`inspection(pier_7, luis_ferreira, 2026_02_01)` while another predicate family
used `ferreira_luis`. The model selected the right predicate family but mixed
atom surfaces across families.

### Result

Targeted inspection-validity probe:

- q024/q027/q085/q086: `4 exact / 0 partial / 0 miss`
- previous targeted result before the relaxation: `0 exact / 0 partial / 4 miss`
- `elapsed_days/3` is now covered by unit tests as a query-only runtime helper

Full Harbor 100-question rerun:

- `68 exact / 17 partial / 15 miss`
- previous comparable full run: `63 exact / 16 partial / 21 miss`
- `99/100` parsed OK
- `99/100` query rows
- `0` write proposals during post-ingestion QA

### What Improved

This converts several predicate-correct / atom-drift failures into supported
answers without adding any raw-language handling in Python. It also gives the
planner a more natural formal helper for "31 days between inspection and
authorization" questions.

### Current Edge

The remaining misses are now mostly compile-coverage and richer source-surface
issues: witness statement metadata, bylaw identity, review-meeting support,
confirmation/reporting attribution, and explicit policy-condition support.
These should be handled by better source-document compilation and profile
predicates, not by answer-time prose tricks.

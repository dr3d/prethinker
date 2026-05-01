# Blackthorn Misconduct Case Progress Journal

This journal tracks how Prethinker learns to compile and query the Blackthorn
fixture. Keep the ugly deltas. The point is to record what breaks, what improved,
and whether improvements came from context/profile machinery, mapper/runtime
structure, or QA support accounting.

## BTC-000 - Fixture Admission

- Timestamp: `2026-05-01T02:07:26Z`
- Source: `tmp/The Blackthorn Misconduct Case`
- Destination: `datasets/story_worlds/blackthorn_misconduct_case`

### Headline

Blackthorn is now admitted as a story-world/source-document benchmark. No model
run has been scored yet in this journal entry.

### Why This Hurts

Blackthorn combines procedural policy, authority chains, business-day and
calendar-day deadlines, corrections, findings, sanctions, witness claims,
multilingual testimony, financial dependencies, advisory non-determinations, and
unresolved questions. It should expose whether the current Harbor-hardened source
compiler can handle procedural state rather than only incident compliance.

### First Measurement Plan

1. Compile `story.md` with the fixture registry via the normal raw-file
   bootstrap runner.
2. Run first-20 QA with reference judging.
3. Score first-20 support with `qa_support_map.jsonl`.
4. Log every improvement as a structural/context change, never as Python prose
   interpretation.

## BTC-001 - Baseline Direct Registry Compile

- Timestamp: `2026-05-01T02:17:01Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T021701287577Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T021957914312Z_qa_qwen-qwen3-6-35b-a3b.json`
- Support artifact: `tmp/story_world_support/20260501T022008310417Z_domain_bootstrap_file_20260501T021701287577Z_story_qwen-qwen3-6-35b-a3b_support.json`

### Headline

The first run was usefully bad: `37` admitted operations, `0` skipped,
signature recall `0.247`, and first-20 QA at `2 exact / 1 partial / 17 miss`.
Support coverage scored `0/20`.

### What Worked

The compiler preserved some witness claims, findings, sanctions, financial
fragments, advisory opinion, and Okonkwo conflict-window facts. Admission stayed
strict: no parser rescue and no out-of-palette writes.

### What Broke

The compile missed the procedural backbone: roles, organizational hierarchy,
committee rosters, proceeding events, deadline requirements/outcomes,
corrections, and temporal order. The QA runner had almost nothing to join for
basic role/deadline questions.

### Lesson

Blackthorn is not mainly a claim/finding benchmark. It is a procedural-state
benchmark. Witness/finding rows are additive detail, not a substitute for the
case backbone.

## BTC-002 - Procedural Guidance First Try

- Timestamp: `2026-05-01T02:29:14Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T022914579226Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T023152551097Z_qa_qwen-qwen3-6-35b-a3b.json`
- Support artifact: `tmp/story_world_support/20260501T023201116513Z_domain_bootstrap_file_20260501T022914579226Z_story_qwen-qwen3-6-35b-a3b_support.json`

### Headline

Adding procedural-misconduct guidance initially regressed compile coverage:
`12` admitted, `2` skipped, signature recall `0.067`. First-20 QA rose only to
`4 exact / 1 partial / 15 miss`, with support still `0/20`.

### What Broke

The model built reasonable pass plans, but broad passes overflowed: policy,
timeline, findings, and financial passes produced long semantic workspaces that
failed to close valid JSON. The surviving rows were mostly witness claims and a
small correction/conflict slice.

### Lesson

Correct high-level guidance is not enough. Dense source compilation needs output
budget discipline. If the model spends the front of every response on entities
and assertions, the candidate operations never reach the mapper.

## BTC-003 - Audit-Cap Recovery

- Timestamp: `2026-05-01T02:45:00Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T024500352527Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T024732923839Z_qa_qwen-qwen3-6-35b-a3b.json`
- Support artifact: `tmp/story_world_support/20260501T024740383586Z_domain_bootstrap_file_20260501T024500352527Z_story_qwen-qwen3-6-35b-a3b_support.json`

### Headline

Reducing audit-array pressure improved the run to `22` admitted, `2` skipped,
signature recall `0.090`, and first-20 QA `5 exact / 0 partial / 15 miss`.

### What Improved

The role/static pass began to produce organizational hierarchy and role facts,
instead of spending the response on a huge entity catalogue. This confirmed the
right lever: the compiler needs to allocate tokens to operations, not workspace
furniture.

### Lesson

The semantic IR schema itself is context engineering. Large optional audit arrays
can become an attractive nuisance on long documents. Candidate-operation budget
must be protected.

## BTC-007 - Tight Entity Cap Breakthrough

- Timestamp: `2026-05-01T03:12:21Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T031221332315Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T031516261117Z_qa_qwen-qwen3-6-35b-a3b.json`
- Support artifact: `tmp/story_world_support/20260501T031523675627Z_domain_bootstrap_file_20260501T031221332315Z_story_qwen-qwen3-6-35b-a3b_support.json`

### Headline

Capping `entities` to `8` while preserving the `128` candidate-operation schema
cap produced the first real movement: `49` admitted, `1` skipped, signature
recall `0.157`, and first-20 QA `6 exact / 1 partial / 13 miss`.

### What Improved

The compiler now emitted a usable organizational and committee backbone:
`org_hierarchy/3`, `org_head/3`, `person_role/2`,
`person_department/2`, `committee_member/3`,
`committee_member_replaced/4`, `conflict_recusal/3`, witness claims, and
correction/conflict rows all survived the same run.

### What Still Hurts

Policy/deadline, findings/sanctions, and financial passes still often produce
semantically plausible but unparseable long JSON. The support scorer remains
`0/20` because the current first-20 support map is exact-clause strict while the
compiler is producing alternate but related surfaces, such as `contains` instead
of the gold KB's `college`/`department` role labels.

### Lesson

The next frontier is canonical support shape, not merely more facts. The model
can now emit backbone rows, but QA support accounting needs either stricter
contract pressure on argument values or a support map that can distinguish
wrong-support from acceptable alternate surface.

## BTC-008 - Focused-Cap Regression

- Timestamp: `2026-05-01T03:21:27Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T032127868583Z_story_qwen-qwen3-6-35b-a3b.json`

### Headline

Reducing focused-pass operation pressure to `24` was a regression:
`29` admitted, `0` skipped, signature recall `0.090`.

### Lesson

For Blackthorn, the tight entity cap helped, but tight operation caps did not.
The compiler needs room to emit the procedural backbone once the audit arrays are
under control.

## BTC-009 - Canonical Contract Pressure Tradeoff

- Timestamp: `2026-05-01T03:27:50Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T032750017195Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T033033696282Z_qa_qwen-qwen3-6-35b-a3b.json`
- Support artifact: `tmp/story_world_support/20260501T033041402370Z_domain_bootstrap_file_20260501T032750017195Z_story_qwen-qwen3-6-35b-a3b_support.json`

### Headline

Tightening the procedural organization and policy-contract guidance improved
some argument shape but reduced breadth: `32` admitted, `2` skipped, signature
recall `0.135`, and first-20 QA `4 exact / 0 partial / 16 miss`.

### What Improved

The model began emitting gold-shaped organization rows such as:

```prolog
org_hierarchy(blackthorn_university, college_of_sciences, college).
org_hierarchy(college_of_sciences, department_of_chemistry, department).
```

This is the right shape for later support accounting. It shows that contract
pressure can correct vague relation labels like `contains`.

### What Broke

The gain in canonical shape cost too much source coverage. The run lost enough
role, committee, and proceeding surface that QA regressed despite better
argument values in the rows that survived.

### Lesson

Canonicalization pressure must be paired with row-class floors. Blackthorn needs
the compiler to keep shape and breadth at the same time: roles, organization,
rosters, proceeding events, deadline requirements, findings, sanctions,
corrections, witness claims, and financial dependencies all need their own
minimum working surface.

## BTC-010 - Role Guidance Regression

- Timestamp: `2026-05-01T03:39:40Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T033940687734Z_story_qwen-qwen3-6-35b-a3b.json`

### Headline

Adding stronger case-role guidance regressed the compile to `19` admitted, `3`
skipped, and signature recall `0.079`.

### Lesson

More natural-language guidance is not automatically better. The next experiment
should avoid piling more prose into the compiler and instead ask the LLM
control-plane for a narrower pass plan with explicit row-class goals. The hard
target is not "mention more rules"; it is preserving a balanced executable
surface under the candidate-operation budget.

## BTC-007S - Support-Scorer Calibration

- Timestamp: `2026-05-01T03:55:40Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T031221332315Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T033428175169Z_qa_qwen-qwen3-6-35b-a3b.json`
- Support artifact: `tmp/story_world_support/20260501T035540401948Z_domain_bootstrap_file_20260501T031221332315Z_story_qwen-qwen3-6-35b-a3b_support.json`

### Headline

The support scorer was too binary. Re-scoring the BTC-007 compile after query
planner cleanup gave exact support `2/20`, loose predicate/arity bundle support
`7/20`, and loose query-signature matches `12/37`.

### What Improved

The scorer now distinguishes three cases:

- exact support clause is present and queryable
- the right predicate/arity family exists but arguments or atom shape drift
- the required support family is missing entirely

This gives a gradient without feeding support expectations into compilation.

### Lesson

Blackthorn misses are not one blob. Some are true compile omissions; some are
argument-shape or atom-drift gaps; some are QA planner surface gaps. The support
map should remain strict, but the diagnostic layer needs loose predicate-family
signal so progress is measurable before exact clauses line up.

## BTC-011 - Coverage Goals Improve Shape, Not QA

- Timestamp: `2026-05-01T04:00:46Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T040046004826Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T040330769231Z_qa_qwen-qwen3-6-35b-a3b.json`
- Support artifact: `tmp/story_world_support/20260501T040339256615Z_domain_bootstrap_file_20260501T040046004826Z_story_qwen-qwen3-6-35b-a3b_support.json`

### Headline

Adding `coverage_goals` to `intake_plan_v1` improved emitted signature recall to
`0.202` with `46` admitted operations and `4` skipped, but first-20 QA regressed
to `5 exact / 0 partial / 15 miss`. Exact support was `0/20`, loose bundle
support `4/20`, and loose query-signature matches `8/37`.

### What Improved

The plan became more explicit about row classes: roles, rosters, deadlines,
findings, sanctions, corrections, witness claims, and financial dependency
surfaces were named as coverage targets.

### What Broke

Without registry vocabulary visible to the intake planner, several pass plans
recommended plausible but unavailable predicate surfaces such as generic
procedural-event and finding names. The compiler then spent budget translating
plan intent instead of preserving queryable rows.

### Lesson

`coverage_goals` are the right control-plane abstraction, but they need to be
paired with vocabulary discipline. A plan can improve high-level shape while
still losing QA usefulness if its row-class goals are not anchored to the
actual allowed predicate contracts.

## BTC-012 - Registry-Visible Intake Planner Regression

- Timestamp: `2026-05-01T04:09:45Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T040945854750Z_story_qwen-qwen3-6-35b-a3b.json`

### Headline

Passing the registry into the intake planner made recommended predicates much
more exact, but the compile collapsed to `9` admitted operations, `1` skipped,
and signature recall `0.067`.

### What Improved

The planner recommended real registry signatures such as `committee_member/3`,
`deadline_requirement/4`, `deadline_met/4`, `finding/4`, `sanction/4`,
`witness_claim/4`, and `correction/4`.

### What Broke

The focused passes became too broad and exacting. Most pass responses emitted
long operations-first Semantic IR objects that still truncated before closing
valid JSON. Predicate choice improved, but parseable admitted coverage fell.

### Lesson

Registry-visible planning is promising, but it is not ready as a default. It
should be an explicit experiment until focused source passes have a smaller
operation-only schema or stronger output budgeting.

## BTC-013 - Operations-First Focused Pass Still Too Large

- Timestamp: `2026-05-01T04:16:05Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T041605741272Z_story_qwen-qwen3-6-35b-a3b.json`

### Headline

Forcing focused passes to set `entities=[]`, `assertions=[]`,
`propositions=[]`, and `unsafe_implications=[]` still regressed the compile to
`5` admitted operations, `0` skipped, and signature recall `0.034`.

### Lesson

The problem was not only entity-catalogue bloat. Even operations-first
`semantic_ir_v1` can be too heavy for dense focused source passes when the
registry-visible plan asks for many exact row classes in one pass.

## BTC-014 - Small Focused Target Regression

- Timestamp: `2026-05-01T04:21:37Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T042137327530Z_story_qwen-qwen3-6-35b-a3b.json`

### Headline

Reducing each focused pass target to `16` candidate operations did not solve the
registry-visible truncation problem. The run admitted only `3` operations, all
from the advisory-opinion pass; signature recall stayed at `0.034`.

### Lesson

The next architectural move is not simply "smaller pass targets." The likely
next move is either a dedicated compact source-pass operation schema or a
two-level planner that emits fewer, narrower row-class passes. Until then,
registry-visible intake planning remains opt-in, while the default path keeps
the wider focused-pass budget that produced BTC-007.

## BTC-015 - Compact Source-Pass Operation Schema Breakthrough

- Timestamp: `2026-05-01T04:31:57Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T043157366665Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T043523888619Z_qa_qwen-qwen3-6-35b-a3b.json`
- Support artifact: `tmp/story_world_support/20260501T043531170104Z_domain_bootstrap_file_20260501T043157366665Z_story_qwen-qwen3-6-35b-a3b_support.json`

### Headline

Adding an opt-in compact `source_pass_ops_v1` schema for focused passes produced
the first Blackthorn jump after BTC-007: `105` admitted operations, `45`
skipped, expected-signature recall `0.551`, and first-20 QA at
`11 exact / 3 partial / 6 miss`.

### What Improved

The registry-visible intake planner became useful once focused passes no longer
had to emit the full `semantic_ir_v1` workspace. The LLM still proposed only
operation candidates; Python wrapped those proposals into a normal
`semantic_ir_v1` object and sent them through the same deterministic mapper.
This preserved the authority boundary while removing schema furniture from
dense row-class passes.

Support diagnostics also improved: loose predicate/arity bundle support reached
`9/20`, and loose query-signature matches reached `19/37`.

### What Still Hurts

Exact support stayed low at `1/20`, because the support map is intentionally
strict and the compile still has atom/argument drift. The `45` skipped
operations are useful pressure: the compact schema is now getting enough
candidates to the mapper that contract enforcement can reveal concrete shape
failures.

### Lesson

This is the Blackthorn version of the Iron Harbor flat-plus-focused breakthrough.
The right abstraction is not more prose guidance and not Python reading the
source. It is a narrower LLM proposal schema for focused source passes, followed
by the existing mapper firewall. The next move is to study the skipped
operations and tighten row-class/argument contracts without reducing breadth.

## BTC-016 - Source-Boundary Correction High-Water

- Timestamp: `2026-05-01T05:40:06Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T054006460252Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T054324965775Z_qa_qwen-qwen3-6-35b-a3b.json`
- Support artifact: `tmp/story_world_support/20260501T054337952383Z_domain_bootstrap_file_20260501T054006460252Z_story_qwen-qwen3-6-35b-a3b_support.json`

### Headline

The skipped-operation audit exposed a clean source-boundary bug in the context
choreography: one focused pass was correctly proposing committee/procedural rows
but marking them `source=context`, so the mapper correctly blocked them as
context-sourced writes. Making the source policy explicit moved Blackthorn to
`190` admitted operations, only `3` skipped operations, expected-signature recall
`0.719`, and first-20 QA `15 exact / 2 partial / 3 miss`.

### What Improved

The authority boundary held. The LLM was not given write authority; it was told
that `raw_source_text` is the direct source document being compiled, while the
profile, registry, intake plan, ledger, and guidance are context guidance only.
Once the model labeled source-grounded operations as `source=direct`, the normal
mapper admitted the rows.

Support diagnostics also jumped: loose predicate/arity support reached `20/20`,
loose query-signature matches reached `35/37`, and exact support rose to `3/20`.
The remaining first-20 misses concentrated around initial allegation timing
(`q007`-`q009`) and temporal/deadline explanation detail (`q017`-`q018`).

### Lesson

This is the strongest Blackthorn evidence so far for the architecture: one
sentence of context-boundary correction unlocked real rows without weakening the
mapper. The model proposes; the mapper still decides. The next hard edge is not
admission safety, but making the compiled procedural surface consistently expose
date-bearing allegation/reporting rows and duration support.

### Full-100 Follow-Up

- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T063746842876Z_qa_qwen-qwen3-6-35b-a3b.json`

Running the BTC-016 compiled KB across all 100 Blackthorn QA probes produced
`73 exact / 6 partial / 21 miss`, with `100/100` parsed QA workspaces,
`100/100` query rows, `0` runtime load errors, and `0` write proposals during
QA. The remaining misses cluster around initial allegation timing, duration and
deadline explanation, conflict-window policy, finance/equipment consequences,
prior-concern dispute tracking, chronological stage summaries, and multilingual
witness-statement counting.

## BTC-017 - Wider Focused Target Tradeoff

- Timestamp: `2026-05-01T05:51:20Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T055120274404Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T055445255894Z_qa_qwen-qwen3-6-35b-a3b.json`
- Support artifact: `tmp/story_world_support/20260501T055501408590Z_domain_bootstrap_file_20260501T055120274404Z_story_qwen-qwen3-6-35b-a3b_support.json`

### Headline

Increasing the focused-pass target to `64` operations produced a cleaner compile
surface, `199` admitted operations, `0` skipped operations, expected-signature
recall `0.742`, and exact support `5/20`, but first-20 QA stayed essentially
flat at `15 exact / 1 partial / 4 miss`.

### Lesson

More admitted rows are not automatically better. Once loose support is already
`20/20`, the bottleneck shifts to exact row shape and QA query use. This run
improved structural coverage but did not beat BTC-016's first-20 answer quality.

## BTC-018 - Contract-Order Migration Regression

- Timestamp: `2026-05-01T06:02:00Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T060200860082Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T060528440033Z_qa_qwen-qwen3-6-35b-a3b.json`
- Support artifact: `tmp/story_world_support/20260501T060546434902Z_domain_bootstrap_file_20260501T060200860082Z_story_qwen-qwen3-6-35b-a3b_support.json`

### Headline

Hardening several vague `arg_1`/`arg_2` registry contracts into meaningful slot
names was architecturally appealing but regressed the benchmark to
`10 exact / 3 partial / 7 miss`.

### Lesson

Predicate contracts matter, but changing argument meaning after a fixture has
already developed compile/query habits is a migration, not a tuning knob. Future
contract hardening should be introduced as a versioned profile change with a
paired QA-query migration, not mixed into an active score run.

## BTC-019 - Row-Class Floor Regression

- Timestamp: `2026-05-01T06:10:39Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T061039014208Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T061357936120Z_qa_qwen-qwen3-6-35b-a3b.json`
- Support artifact: `tmp/story_world_support/20260501T061412785657Z_domain_bootstrap_file_20260501T061039014208Z_story_qwen-qwen3-6-35b-a3b_support.json`

### Headline

Adding an explicit procedural allegation row-class floor preserved compile
breadth (`190` admitted, `0` skipped, recall `0.742`) but regressed first-20 QA
to `14 exact / 1 partial / 5 miss`.

### Lesson

Broad row-class floors can distract the model when the immediate bottleneck is
exact support for a few early procedural questions. The row-class-floor idea is
still likely useful, but it should be tested in narrower pass plans rather than
added as global prose pressure.

## BTC-020 - Intake Planner Allegation-Pass Regression

- Timestamp: `2026-05-01T06:20:17Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T062017942835Z_story_qwen-qwen3-6-35b-a3b.json`

### Headline

Adding a generic procedural instruction for the intake planner to allocate an
initiating allegation/reporting pass caused compile breadth to collapse to `93`
admitted operations, `6` skipped operations, and expected-signature recall
`0.539`, so the run was not advanced to QA.

### Lesson

The missing initial allegation rows should probably be solved by a narrower
pass-local refinement or a second-stage planner, not by forcing the top-level
planner to add another broad pass inside the same `max-plan-passes` budget. The
best current default remains BTC-016's source-boundary correction.

## BTC-021 - Deadline Query-Planning Lift

- Timestamp: `2026-05-01T12:12:57Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T054006460252Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T121257287411Z_qa_qwen-qwen3-6-35b-a3b.json`

### Headline

Using the BTC-016 compiled KB, a narrow post-ingestion QA strategy update moved
the full-100 score from `73 exact / 6 partial / 21 miss` to
`75 exact / 4 partial / 21 miss`, with `100/100` parsed QA workspaces,
`100/100` query rows, `0` runtime load errors, and `0` write proposals.

### What Changed

The retained guidance is intentionally small and generic: for duration/deadline
questions, prefer an existing `deadline_met(Phase, StartDate, EndDate, Status)`
row plus `elapsed_days(StartDate, EndDate, Days)` when that row represents the
asked phase. This prevents the QA planner from computing durations from two
start-event rows when the compiled KB already contains a source-grounded
deadline/completion row.

The deterministic temporal subset fallback also remains in the runtime query
path. It recovers when an otherwise valid temporal helper query is
over-constrained by a previous structured query that binds a date surface
differently from the admitted deadline row.

### Result Movement

Compared with BTC-016 full-100, the run converted:

- `q009` allegation filing timeframe from `miss` to `exact`.
- `q017` inquiry duration from `partial` to `exact`.
- `q036` FSRB decision from `miss` to `exact`.
- `q059` federal-grant equipment disposition from `miss` to `exact`.

It also exposed two unstable query-planning edges:

- `q077` federal agency authority moved from `partial` to `miss` because the KB
  still lacks an explicit authority/independent-review predicate.
- `q080` FSRB final appealability moved from `exact` to `miss` in the retained
  run because the planner chose deadline rows instead of final-status finding
  rows. A proposed finality/appealability guidance line recovered `q080` in a
  slice test but caused broader regressions, so it was not kept.

### Lesson

Blackthorn's current frontier is now split cleanly:

- Compile/support gaps: initial allegation dates, conflict-window policy,
  Petrova-specific findings, federal-agency authority, and finality rules need
  better admitted source surface.
- Query-planning gaps: duration/deadline questions benefit from a small
  generic strategy rule, but broader procedural-finality guidance is too
  disruptive unless the compile surface provides a clearer finality predicate.

This is useful progress because it separates source ingestion work from
post-ingestion reasoning work without adding Python prose interpretation.

## BTC-022 - Procedural Surface Maturation

- Timestamp: `2026-05-01T14:40:58Z`
- Compile artifact: `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T134756047982Z_story_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260501T144058931677Z_qa_qwen-qwen3-6-35b-a3b.json`
- Support artifact: `tmp/story_world_support/20260501T134816111146Z_domain_bootstrap_file_20260501T134756047982Z_story_qwen-qwen3-6-35b-a3b_support.json`

### Headline

Blackthorn reached a new full-100 high-water mark:
`82 exact / 9 partial / 9 miss`, with `100/100` parsed QA workspaces,
`100/100` query rows, `0` runtime load errors, and `0` write proposals.
The compile used `246` admitted operations, `0` skipped operations, and
expected-signature recall `0.876`.

### What Changed

This run matured the procedural profile rather than adding Python language
handling. The profile gained two narrow predicates for source-stated policy
surface:

- `federal_agency_authority/2`
- `fsrb_decision_effect/2`

The procedural compiler context also gained explicit pressure to preserve:

- FSRB finality, sanction rationale, and sanction effective timing.
- Federal independent-review authority and federal reporting consequences.
- Conflict windows and corrected publication dates.
- Prior complaints and unresolved/deferred reporting questions.
- Title aliases as roles rather than person-atom prefixes.

The QA planner gained two narrow distinctions:

- Actual FSRB decision questions should query `finding`, `sanction`,
  `sanction_modified`, `sanction_upheld`, and `fsrb_rationale` rather than
  treating `fsrb_decision_effect/2` as the decision itself.
- Counterfactual FSRB-overturn questions should query standing policy
  consequences such as federal notification and expungement deadlines rather
  than actual sanction rows from the source outcome.

### Result Movement

Compared with BTC-021 (`75 / 4 / 21`), BTC-022 converted major misses:

- `q007` and `q008`: initial discovery/reporting dates.
- `q026`: conflict-of-interest window.
- `q030`: investigation duration.
- `q033`: Petrova-specific investigation finding/non-finding support.
- `q038`: FSRB suspension-reduction rationale.
- `q047`: sequestration custody.
- `q070` and `q071`: October 2025 prior-concern dispute.
- `q090`: chronological proceeding stages.

The run also exposed remaining tradeoffs:

- `q019` inquiry-extension rationale and `q043` inquiry lateness regressed.
- `q077` federal independent authority and `q080` FSRB finality remain misses
  because the compile still does not reliably preserve those exact rows.
- `q096` witness-statement count became partial; multilingual/language-count
  support remains a weak edge.

### Negative Experiment

Hardening `proceeding_event/4` from vague `arg_1..arg_4` slots into a meaningful
`case_or_proceeding/event_type/date/actor_or_authority` contract collapsed a
compile to only `32` admitted operations and recall `0.146`. The change was
reverted. This confirms the earlier lesson: contract hardening is a profile
migration that needs a paired compiler/query migration, not a tuning knob inside
an active benchmark run.

### Lesson

The strongest lever was not broader prose guidance. It was giving the profile
named surfaces for source-stated procedural concepts, then telling the model
which epistemic layer those concepts belong to. Blackthorn is now bottlenecked
less by admission and more by:

- stable event/date contract migration,
- federal/finality policy surface,
- witness-language counting,
- and exact support-map atom alignment.

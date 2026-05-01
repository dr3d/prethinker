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

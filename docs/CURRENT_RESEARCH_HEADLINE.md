# Current Research Headline

Last updated: 2026-05-03

## Semantic Parallax

The newest insight is that one LLM compile is only one viewpoint.

This page is a short lab-note headline, not a victory lap. It exists so a new
reader can see what the project is learning right now before diving into the
longer architecture notes and fixture journals.

Prethinker is moving toward **multi-pass semantic compilation**: separate
semantic lenses look at the same source for backbone facts, support/evidence,
temporal state, and executable rules. Each lens proposes. The mapper admits or
skips. Deterministic union accumulates only mapper-admitted clauses.

```text
source
  -> backbone lens
  -> support/source lens
  -> temporal/status lens
  -> rule lens
  -> mapper admission per lens
  -> deterministic safe-surface union
  -> Prolog query / rule trial
```

## Why This Matters

APR showed that a safe union of independent support views can beat any single
compile: the Anaplan Polaris fixture reached `42 exact / 1 partial / 0 miss`
without answer-key guidance.

Glass Tide is now exercising the harder rule-ingestion frontier:

- broad compiles preserve rules as source records, but executable behavior
  comes from separate rule lenses plus runtime trial;
- a separate rule lens can admit executable clauses, including a role-joined
  repair rule that passes both positive and negative probes:
  `derived_authorization(repair_order_71, valid, glass_tide_repair)` succeeds,
  while the one-signer repair order does not;
- runtime trial exposes the real risks: overgeneralized class-predicate fanout
  versus clean but dormant rules whose bodies lack matching admitted facts;
- the verifier now checks body-goal support, so a rule is not considered
  promotion-ready merely because predicate signatures match.
- threshold tax rules now work over deterministic numeric helpers, and a split
  exception lens covers the high-value relief-cargo exemption.
- a split exception lens now derives `lamp_rice` as `exempt` under the correct
  `harbor` scope and does not derive it as taxable; the combined threshold plus
  exception bundle remains fragile and exposed numeric-helper argument misuse
  (`value_greater_than(Value, 100)` instead of `value_greater_than(Cargo, 100)`).
- deterministic rule-surface union now accumulates the separate threshold and
  exception lenses into `3` promotion-ready tax rules with `3/3` positive probes
  and `1/1` negative probe, without reading source prose or inventing new rules.
- the same pattern now works for salvage: a body-fact lens admitted
  `recovered_from_water/3`, `abandoned/1`, `sacred/1`, and `not_sacred/1` rows;
  a rule-lens union retained `2` promotion-ready salvage rules and passed both
  the Tomas reward positive probe and Nell sacred-cargo negative probe.
- the verifier now scores promotion-readiness in isolated per-rule runtimes
  before combined probes run over the accumulated surface. Tax stayed at `3`
  promotion-ready rules and salvage stayed at `2`, so the gains survived the
  stricter test.
- quarantine now adds the temporal-helper branch: a body-fact lens admitted
  `quarantine_patient/1`, `no_fever/2`, and `negative_test/2`; `hours_at_least/3`
  let the verifier retain a Dax clearance rule while rejecting Mira's five-hour
  test spacing.
- council voting now has a first priority/override branch: the body-fact lens
  admitted proposal, support, veto, and no-override rows; the verifier retained
  the budget-veto failure rule and dropped unsupported normal-vote branches.
- the first aggregation helper (`support_count_at_least/2`) is now in the
  runtime, but GLT-037 showed the rule lens still needs sharper guidance:
  threshold-met is not the same thing as final passage when veto/override logic
  is also active.
- GLT-038 fixed that shape: the aggregation lens now emits
  `derived_condition(Proposal, support_threshold_met, council_vote)` and leaves
  final passage to a later priority/override branch.
- GLT-039 unions the council threshold and veto branches: the accumulated
  surface proves both "threshold met" and "budget veto failure" while still not
  deriving final passage.
- GLT-040 adds a restraint guard: rule lenses no longer get credit for
  re-emitting existing backbone rules. The council final-outcome lens declined
  to invent a broader `council_vote` failure rule when the budget-veto branch
  already represented the source-stated outcome.
- The rule verifier now has dependency-composed promotion trials. A rule is
  still tested in isolation first, but it can also be retested with upstream
  sibling rules whose heads appear in its body while same-head siblings remain
  excluded. This is the next step toward safe final-outcome composition:
  intermediate conditions may support later rules without letting a neighboring
  final-status rule fake success.
- Avalon reproduced the numeric-helper misuse edge on a fresh governance
  fixture: the rule lens wrote amount/match variables into entity-first helper
  calls. The verifier now flags measure-variable helper misuse and computed
  thresholds, keeping those rules visibly non-promotable instead of merely
  dormant.
- Avalon also exposed a runtime bug in anonymous-variable semantics: repeated
  `_` occurrences were being treated as the same variable. After fixing that
  and adding bound-number plus percentage helpers, a narrow Rule 5 lens produced
  `3` promotion-ready threshold/ratio rules from `4` admitted clauses.
- Deterministically unioning those Rule 5 rules into the Avalon QA surface
  improved exact answers from `25` to `27`, but also increased misses from `3`
  to `5`. This is the rule-side version of the APR lesson: safe accumulation is
  powerful, but global activation can perturb query planning. The next tool
  needs row-level activation or exact-answer protection.
- Dulse Ledger is now scored cold at `27 exact / 7 partial / 6 miss`, with
  `70` admitted operations, `21` skips, `0` runtime errors, and `0` write
  proposals during QA. Oxalis Recall, Sable Creek Budget, and Thornfield
  Variance remain admitted and pending baseline runs.

Clarification Eagerness Trap is exercising the companion governance frontier:

- the current CE high-water is `40/40` correct with `0` over-eager asks,
  `0` under-eager misses, `0` unsafe candidates, and `0` context-write
  violations;
- blocked-slot question coverage is now measured structurally from authored
  fixture slots and model-emitted clarification surfaces; CET-010 reached
  `10/10` blocked-slot coverage and `0` blocked-slot safe-write violations;
- CE must be measured across ingestion, query, safe partials, blocked rows, and
  authority-boundary violations;
- CET-011/CET-012 exposed a context-availability effect: no-source-context CE
  regressed to `24/40` with `15` over-eager asks, while the same fixture with
  source context returned to `40/40`. CE scores must say what authority surface
  was available.

The cold generalization lane is now active:

- seven newly admitted source-only fixtures produced `189 exact / 58 partial /
  103 miss` across `350` QA items;
- the cross-fixture failure rollup shows `116` compile-surface gaps, `27`
  hybrid/reasoning gaps, `15` query-surface gaps, and `3` answer-surface gaps;
- Avalon Grant Committee joins the cold lane at `25 exact / 12 partial /
  3 miss` over `40` questions, with `114` admitted operations, `6` skips,
  `0` runtime errors, and `0` write proposals during QA. It is strong enough
  to show transfer, but it admitted `0` executable rules, making it a clean
  rule-composition/body-fact acquisition target rather than a solved fixture.
- a Three Moles diagnostic replay added pass-contribution accounting and showed
  the event/causal lens contributing `0` unique rows, making lens usefulness
  measurable instead of aesthetic;
- a compact focused-pass JSON retry recovered that same event/causal lens to
  `28` unique rows, but QA stayed essentially flat, proving that mechanical
  lens recovery is necessary but not sufficient for answer-bearing coverage;
- compile-lens health now rolls per-pass diagnostics into a top-level
  `healthy` / `warning` / `poor` verdict. A Veridia-9 cold replay with healthy
  lenses improved slightly from `18 exact / 5 partial / 17 miss` to `19 / 6 /
  15` while admitting fewer rows, which is useful but also clarifies the next
  metric: healthy lenses still need question-support coverage.
- the cold rollup now includes a non-exact query-evidence proxy. The surprising
  result is that most misses still returned some Prolog rows, so the current
  pain is not just empty retrieval. It is answer-bearing support: the query path
  often finds nearby symbolic surface without finding the exact row, join, or
  rule consequence needed by the question.
- Veridia-9 V9-003 confirms that post-ingestion query choreography can lift a
  cold run without touching the compile: evidence-bundle context filtering moved
  the unchanged V9-002 surface from `19 / 6 / 15` to `22 / 4 / 14`. It also
  regressed two partials, so this is a measured near-miss tool, not a blind
  default.
- Black Lantern BLM-002 repeats the pattern on a second cold fixture: unchanged
  compile, evidence-bundle context filtering, `27 / 7 / 6` to `32 / 3 / 5`.
  It also regressed two rows, which sharpens the lesson: query choreography is
  powerful, but it needs row-level risk prediction before it becomes default.
- BLM-003 widened the evidence-filter fallback (`max_clauses=320`,
  `broad_floor=160`) and kept `32` exact while moving hard misses down from `5`
  to `3`. It still swapped which rows won and lost, so the next tool should
  decide when to activate evidence filtering per row rather than globally.
- V9-004 is the negative control: the same broader floor on Veridia reduced one
  hard miss but lost the exact gains from V9-003 (`22` exact back down to `19`).
  More context is not automatically better; the budget is a query-surface
  control parameter.
- The first query-mode comparison report covers Veridia and Black Lantern across
  baseline, narrow evidence filtering, and broad evidence filtering. Only `16`
  of `80` rows are volatile; `12` baseline rows can be rescued by an alternate
  mode, while only `1` baseline exact regresses. That makes row-level selection
  worth pursuing, with exact-row protection as the first invariant.

The architecture is becoming sharper:

```text
multiple model views may propose;
only deterministic admission decides what can accumulate.
```

## Current Hard Question

Can Prethinker turn explicit English charter rules into executable Prolog rules
without allowing a bad rule to generalize into false derived truth, and can it
ask exactly when durable truth would otherwise require an unauthorized choice?

That is the Glass Tide plus CE frontier.

## Tonight's Research Queue

The next work should stay on the sharp edges:

0. **Cold generalization baselines.** Seven newly admitted fixtures now test
   whether semantic parallax generalizes beyond the research stories that shaped
   the harness. The current aggregate says compile-surface coverage is the
   largest general issue, followed by hybrid/reasoning support. Next changes
   should improve at least two cold fixtures or preserve older regression
   lanes. The newest lens-health gate should help decide when a compile is worth
   sending through full QA and when the compile itself needs repair first. The
   newest evidence-return proxy says many misses already retrieve rows, so the
   next compile/query work should target answer-bearing support, not just more
   rows. V9-003 shows evidence-bundle context filtering can help that query
   surface, and BLM-002 confirms the lift on another fixture, but both runs need
   regression checks because they can perturb partial/exact rows. BLM-003 shows
   broader context can reduce hard misses, while V9-004 shows the same broader
   setting can lose exact answers. The next version needs row-level activation
   or a fallback ensemble policy. The new query-mode comparison report shows a
   diagnostic perfect-selector upper bound of `56` exact across 80 compared
   rows, versus `46` baseline exacts, but that bound is for research only and
   must not become an oracle selector. The next unscored cold queue is Oxalis
   Recall, Sable Creek Budget, and Thornfield Variance.
1. **Glass Tide final-outcome composition.** Tax, salvage, quarantine, council
   veto, and council support-threshold conditions now have promotion-ready
   slices. The next frontier is a final outcome lens that joins intermediate
   conditions without collapsing provenance or overclaiming state. GLT-040 now
   makes duplicate branch echo visible as a non-contribution rather than a score
   gain. Avalon AG-002 confirms the same discipline is needed outside Glass
   Tide: rule lenses can emit executable clauses, but helper-shape and body
   support decide promotion.
2. **Rule probe discipline.** Recent preflight runs show that a rule can be
   body-supported but fail under the wrong scope atom, can become dormant by
   using lowercase placeholders such as `warden` and `repair_order`, or can look
   firing only because a sibling rule shares its derived head. Keep isolated
   per-rule promotion plus combined positive/negative probes in the loop.
3. **Clarification Eagerness drift.** CET-010 reached `40/40` with perfect
   ask/no-ask posture and `1.000` blocked-slot coverage after adding structural
   scorer lanes. The next CE move is a small hard replay pack for variance, not
   another broad prompt patch.
4. **Regression cadence.** Keep compact Anaplan/Glass Tide/CE checks running so
   new rule machinery does not reopen older query, admission, or ask/no-ask
   failures.

## Read Next

- [Multi-Pass Semantic Compiler](https://github.com/dr3d/prethinker/blob/main/docs/MULTI_PASS_SEMANTIC_COMPILER.md)
- [Cold Baseline Failure Rollup](https://github.com/dr3d/prethinker/blob/main/docs/COLD_BASELINE_FAILURE_ROLLUP.md)
- [Frontier Progress Report](https://github.com/dr3d/prethinker/blob/main/docs/FRONTIER_PROGRESS_REPORT.md)
- [Clarification Eagerness Strategy](https://github.com/dr3d/prethinker/blob/main/docs/CLARIFICATION_EAGERNESS_STRATEGY.md)
- [Project State](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md)
- [Glass Tide progress journal](https://github.com/dr3d/prethinker/blob/main/datasets/story_worlds/glass_tide_charter/progress_journal.md)
- [Clarification Eagerness Trap journal](https://github.com/dr3d/prethinker/blob/main/datasets/clarification_eagerness/clarification_eagerness_trap/progress_journal.md)

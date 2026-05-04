# Current Research Headline

Last updated: 2026-05-04

## Semantic Parallax

The newest insight is that one LLM compile is only one viewpoint.

The north star is **hard to fool**: Prethinker should not confuse claims with
facts, rules with outcomes, missing evidence with permission to guess, or
semantic struggle with a reason to keep burning passes.

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

Glass Tide opened the harder rule-ingestion frontier, and Sable/Avalon are now
testing whether those gains transfer:

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
- Sable Creek added a rule-safety regression test from a fresh municipal-budget
  fixture. A narrow rule lens initially appeared to produce `2` promotion-ready
  rules, but both had a head variable that did not appear in the body. The
  mapper and verifier now block unbound-head rules, and the mapper also rejects
  fact-shaped clauses submitted as `operation="rule"`.
- The compact rule-lens prompt now carries the same non-negotiable rule-shape
  constraints as the full lens: real `Head :- Body` clauses only, all head
  variables body-bound, first-order lenses use admitted backbone predicates in
  bodies, and `derived_*` body goals require an explicit composition dependency.
- Sable Creek then produced the first fresh-fixture promotion-ready rule under
  those stricter gates: the rule lens used a deterministic admitted-fact
  signature support summary to bind `AmendmentId` and `Amount` through
  `amendment_introduced/4`, then composed `number_greater_than/2` to derive
  `requires_public_hearing` without unbound head variables, fact-shaped rule
  clauses, oracle rows, or Python prose interpretation.
- The current Sable/Avalon parallax lesson is now a verifier rule instead of a
  fixture note: repeated body predicates that share multiple variables need
  distinct literal role anchors, otherwise they can falsely satisfy two
  requirements with one admitted row. The promotion scorer blocks that aliasing
  shape while still allowing anchored body-fact composition such as
  `submit_revised_budget` plus `provide_matching_docs`.
- Sable SC-007 crossed the important line from probe success to full-QA lift.
  A body-fact lens admitted `proposal/1` and `supported/2` vote rows, the
  aggregation lens derived only `support_threshold_met`, and the
  promotion-filtered threshold+vote union moved the full 40-question replay
  from `20 / 8 / 12` to `24 / 6 / 10` with no runtime errors or QA write
  proposals. The harness lesson was sharp: body-fact guidance must not confuse
  `supported/2` vote facts with generic `support_*` rationale rows, and
  aggregation lenses need condition-label restraint as well as scope restraint.
- Avalon then repeated the rule-lens transfer with a sharper mapper boundary:
  raw Prolog negation, disjunction, lists, arithmetic, equality, and comparison
  operators are now skipped at rule admission, so the post-gate Section A replay
  retained only `3` executable clauses, including `2` promotion-ready
  helper-composed matching-fund branches and `0` unsupported body goals.
- Unioning those post-gate Avalon rules into the AG-001 surface produced
  `27 exact / 10 partial / 3 miss`, improving the older rule union's miss count
  while preserving exact count. A diagnostic mode comparison shows a `29 exact`
  upper bound, so row-level activation remains the next query-surface frontier.
- Avalon AG-007 adds the first non-oracle evidence-mode selector. It compared
  baseline (`25 / 12 / 3`), post-gate rule union (`27 / 10 / 3`), and focused
  evidence-context QA (`29 / 7 / 4`) without showing the selector source prose,
  answer keys, judge labels, failure labels, or gold KBs. The selector chose
  among stripped query-evidence bundles and reached `31 exact / 7 partial /
  2 miss`, selecting the best available mode on `38/40` rows against a
  diagnostic upper bound of `32 / 7 / 1`.
- This is the practical bridge from semantic parallax to row-level activation:
  safe symbolic surfaces can be accumulated independently, then selected per
  question by a model-owned control plane that still has no write authority and
  no oracle access.
- The transfer report now gives that bridge a sharper target surface. Existing
  Sable/Avalon direct-2400 comparisons split into `54` stable rows, `15` clean
  nonbaseline rescue rows, `7` baseline-exact protection rows, and `4` volatile
  baseline-preferred rows. The next selector should learn those risk buckets
  rather than simply choosing the most rule-heavy mode.
- Joining the existing direct selector artifacts back into that report adds a
  first governor-compliance audit: `54/54` stable rows, `11/15` rescue rows,
  `6/7` baseline-exact protection rows, and `2/4` volatile baseline-preferred
  rows pass. The visible misses are now a small, named calibration set instead
  of a vague selector problem. This report now also carries
  `semantic_progress_assessment_v1`; the selector lane is `medium` zombie risk
  until the next pass names which miss class it expects to repair.
- Black Lantern BLM-004 is the necessary caution: the same selector mechanism
  ran cleanly but scored only `28 / 9 / 3` over baseline/narrow/broad query
  modes, below the best individual modes. Adding QA self-check notes moved to
  `29 / 7 / 4`, not a clean fix. The mechanism exists; cross-fixture selector
  calibration is now the hard part.
- The selector calibration surface is now explicit. `direct` remains the stable
  default posture, while `completeness` and bounded self-check context are
  research dials. The completeness+self-check policy recovered Black Lantern to
  `31 / 6 / 3` and selected the best mode on `38/40` rows, but the same posture
  regressed Avalon to `27 / 9 / 2` with two selector errors. Selector policy is
  therefore a measured control problem, not a hidden prompt tweak.
- A third `relevance` selector policy now exists for the wrong-subject evidence
  failure mode. It fixed one Avalon Rule2 activation miss, but full replays did
  not beat the alternatives: Avalon scored `30 / 8 / 2`; Black Lantern scored
  `28 / 8 / 3` with one selector error.
- Veridia V9-005 is a better selector transfer check: over baseline, narrow,
  and broad query modes, the direct non-oracle selector reached `22 / 6 / 12`,
  matched the best exact count, and selected the best available mode on `39/40`
  rows. It still missed one broad-mode partial rescue, so row-level activation
  is useful but not solved.
- A first hybrid selector now lets deterministic structure handle confident
  rows and calls the LLM only for uncertainty. It reached the Avalon Rule8
  comparison upper bound (`27 / 12 / 1`) while avoiding LLM choice on `13/40`
  rows, but Three Moles and Sable regressed because the fallback LLM overrode
  structurally correct relaxed evidence. The lesson is specific: uncertainty
  gating needs row-level risk prediction, not just "ask the model when close."
- Otters OTR-015 shows the same post-ingestion access idea transfers back to a
  source-local story world: replaying QA with evidence-bundle filtering over
  the unchanged OTR-014 compile improved `17 / 4 / 19` to `22 / 5 / 13`, with
  `9` rescued rows and `0` baseline-exact regressions.
- Three Moles MMM-004 is the cautionary story-world contrast: evidence
  filtering over the unchanged MMM-003 compile improved exact count from
  `10` to `13`, but misses stayed at `23`, and the selector regressed to
  `11 / 4 / 25`. Some stories still need better lens coverage more than better
  retrieval.
- Three Moles MMM-005 then found the compile-side story win: opt-in
  `source_entity_ledger_v1` plus the current semantic-parallax passes admitted
  `193` operations and lifted QA to `16 / 7 / 17`; evidence filtering stacked
  to `18 / 5 / 17`. This is the first positive story-fixture evidence that the
  ledger-to-compile handoff can transfer when later passes actually cash in the
  ledger.
- Oxalis OX-002 carries the post-ingestion pattern into regulatory recall:
  evidence filtering improved `16 / 9 / 15` to `18 / 11 / 11`, while the direct
  selector chose `19 / 9 / 12`. Exact precision and miss reduction are still
  competing activation objectives.
- Dulse DL-002 is the saturation check: a strong `27 / 7 / 6` cold baseline
  moved only to `27 / 8 / 5` under evidence filtering, and the selector returned
  to `27 / 7 / 6`. Query-surface tools help, but they do not automatically
  inflate already-supported fixtures.
- Avalon AG-009 adds a clean Rule 2 exception-lens result: the lens admitted
  `3` rules, `2` were promotion-ready, and the prior-funding branch passed
  `3/3` positive and `2/2` negative probes. But globally unioning those
  promotion-ready rules regressed QA from `25 / 12 / 3` to `25 / 10 / 5`.
  The lesson is now explicit: runtime promotion-ready does not mean activate
  for every question.
- Dulse Ledger is now scored cold at `27 exact / 7 partial / 6 miss`, Oxalis
  Recall scored `16 exact / 9 partial / 15 miss` despite `106` admitted
  operations and `0` skips, Sable Creek Budget scored `20 exact / 8 partial /
  12 miss` after exposing a profile-bootstrap role-field JSON runaway, and
  Thornfield Variance scored `20 exact / 6 partial / 14 miss`. Together they
  sharpen the lesson: rotating fixtures matters because "clean admission,"
  "schema hygiene," and "answer-bearing coverage" are distinct surfaces.
- The newest incoming challenge batch has a standard smoke scorecard generated
  from compile/QA artifacts only. All five fixtures now compile after
  Copperfall recovered through compact profile retry, and the batch scored `44
  exact / 4 partial / 2 miss` over `50` no-answer QA rows with `0` write
  proposals. Copperfall and Harrowgate were clean at `10/10`; Larkspur reached
  `8 / 2 / 0`; Northbridge and Meridian landed at `8 / 1 / 1`. The non-exact
  surface is still mostly compile coverage, so the next useful work is
  acquisition and hybrid-helper substrate, not answer-key-shaped tuning.
- The newest harness lesson is negative but valuable: broad global
  detail/specification guidance improved Meridian locally but regressed the
  five-fixture batch to `41 exact / 4 partial / 5 miss`. The new scorecard
  comparer marks that run `reject_candidate`, so future policy changes should
  be promoted by artifact deltas, not by one good-looking fixture.
- A narrower evidence-bundle diagnostic over only the current non-exact rows
  shows why row-level activation matters. It lifted exacts from `44` to `46`,
  but also increased misses from `2` to `3`, so the batch remains rejected as a
  default mode. The row overlay plan identifies two useful rescues and one
  regression, turning "evidence mode helps sometimes" into a small selector
  target.
- On that six-row target, deterministic structural mode selection found `5/6`
  best choices but still picked the harmful Larkspur q009 evidence row. The LLM
  `activation` selector reached `6/6` best choices without source prose,
  answers, judge labels, or failure labels. This is the clean next hint:
  selector control should learn answer-bearing relevance, not just evidence
  volume.
- The full first-10 replay keeps that hint honest. Evidence mode over all smoke
  rows stayed at `44` exact but increased misses; structural selection reached
  `24 / 3 / 3` across the three imperfect fixtures. After adding a selector JSON
  retry guard, activation reached `23 / 5 / 2`: fewer misses, but weaker exact
  preservation. The selector frontier is exact-row protection, not blanket
  activation.
- A first protected selector now tests that idea: structural by default, with
  activation only for high-volume nonbaseline overrides. It reached `24 / 4 /
  2` on the incoming first-10 selector slice and reduced Avalon misses by one,
  but it failed to transfer to Sable, where direct selection remains much
  stronger. This keeps selector control in research mode and points back to
  compile-side repair for the current incoming misses.
- The incoming repair queue is now explicit: two row-selector calibration rows,
  three scoped source-surface repair rows, and one helper/query-join row. That
  is the next practical compiler frontier: repair missing answer-bearing source
  surface locally without promoting another global detail prompt.
- A ledger compile diagnostic sharpened the selector frontier. Ledger mode is
  not a default promotion: it raised the incoming batch to `45 exact / 2 partial
  / 3 miss`, so the scorecard gate rejected it. But row-level selection can use
  it: the new `guarded_activation` policy keeps structural choices for
  confident rows and calls activation with bounded self-check evidence for
  uncertain rows. On the three imperfect first-10 fixtures, it selected the
  best available mode on `30/30` rows, preserving Larkspur at `8 / 2 / 0` while
  lifting Meridian and Northbridge to `9 / 0 / 1` each.
- The transfer check keeps that result honest: guarded activation did not beat
  `protected` on Avalon miss control and did not beat `direct` on Sable. The
  harness now has a better named diagnostic policy, not a new universal default.
  The next selector problem is deciding when a fixture/mode family is safe for
  activation fallback at all.
- A selector risk-gate planner now makes that decision surface explicit. It
  reads selector artifacts only and classifies rows as safe activation,
  calibration activation, baseline protection, or compile repair. With
  Avalon/Sable transfer checks attached, the incoming guarded-activation
  rescues remain calibration targets rather than promotion targets, which is the
  right conservative behavior for a moving research instrument.
- Scoped compile repair then produced a real but gated batch lift: the incoming
  scorecard moved from `44 / 4 / 2` to `45 / 4 / 1`, with Northbridge improving
  to `9 / 1 / 0`. The same run regressed Meridian q010 from exact to miss, so
  the scorecard comparer now tracks baseline-exact row regressions and returns
  `row_level_gate_required` instead of `promote_candidate` for this shape.
- The row-gated scorecard planner makes the opportunity concrete: accepting the
  three scoped-repair rescues while rejecting the Meridian q010 regression gives
  a protected target of `46 / 4 / 0` on the incoming five-fixture first-10
  scorecard.
- Scoped compile repair plus evidence-bundle context filtering has now made
  that target real: the batch replays at `46 / 4 / 0`, with no QA write
  proposals, no baseline-exact row regressions, and a `promote_candidate`
  scorecard gate. The next incoming frontier is the four remaining partials,
  not miss recovery.
- A follow-on compile-variant diagnostic found complementary surfaces rather
  than a blanket replacement. Shifted Meridian/Northbridge compiles stay
  aggregate-neutral at `46 / 4 / 0`, but row-level overlay across variants gives
  a judged `48 / 2 / 0` upper target while protecting two baseline-exact rows.
- Larkspur then exposed a clean compiler guardrail: numeric character
  attributes must not become names/aliases, and official roles need duty and
  authority surfaces. The first guarded replay is high-risk as a compile, but
  it repairs the youngest-exhibitor row. Added as a variant, the judged overlay
  target reached `49 / 1 / 0`.
- The remaining Larkspur row turned out to be a query-surface issue over an
  admitted compile surface: `person_role(osric_thane, fair_warden)` was true
  but too thin. The QA harness now adds structural official-identity companions
  over admitted authority/action predicates such as `ruling_by/3` and
  `permission_granted/2`, making Osric's row exact without Python prose
  interpretation. The candidate remains unsafe globally because Larkspur q010
  regresses, but the judged compile/query overlay target is now `50 / 0 / 0`
  with four accepted variant rows and three protected exact rows. The hard
  problem is learning a non-oracle selector/control signal for these variants.
- The first bridge artifact for that control signal now exists:
  `plan_incoming_variant_selector_training.py` turns the judged overlay into
  `4` activation targets and `3` exact-protection targets without reading
  source prose, gold KBs, answer keys, strategy files, or raw compile outputs.
  Both nonbaseline variants are marked
  `unsafe_global_variant_row_gate_required`, so the current evidence says
  "train row-gated activation," not "promote a new global compile."
- Guarded activation now has a structural volume-trap uncertainty trigger:
  row-count-heavy or relaxed-fallback-heavy structural winners get sent to the
  LLM selector instead of being treated as confident. On the seven incoming
  variant calibration rows, this moved the non-oracle selector to `6 / 1 / 0`
  with `6/7` best choices and no selector errors. The remaining Northbridge
  q007 partial is a requirement-detail relevance problem, not a volume problem.
- The requirement-detail relevance guard now closes that last row: activation
  selection treats count-only/status-only support as partial when another mode
  returns requirement details such as spacing, interval, threshold, scope,
  condition, duration, unit, or authority. The same seven-row calibration slice
  now reaches `7 / 0 / 0` and `7/7` best choices without source prose, answer
  keys, judge labels, failure labels, or gold KBs in selector input.

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
- CET-013 reran the source-context CE lane after the rule-admission changes and
  held `40/40` correct with `0` unsafe candidates, `0` context-write
  violations, and `10/10` blocked-slot coverage. The residual signal is
  safe-partial richness (`11/13`), not ask/no-ask posture.
- CET-014 repeated the source-context CE sentinel after the evidence-selector
  work and again held `40/40` correct with `0` unsafe candidates, `0`
  context-write violations, and `10/10` blocked-slot coverage.

The cold generalization lane is now active:

- ten newly admitted source-only fixtures produced `245 exact / 81 partial /
  144 miss` across `470` QA items;
- the cross-fixture failure rollup shows `159` compile-surface gaps, `35`
  hybrid/reasoning gaps, `26` query-surface gaps, and `5` answer-surface gaps;
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

Can Prethinker activate the right admitted symbolic surface for each question:
facts when facts are enough, accumulated support when rationale is needed,
promotion-ready rules when inference is needed, and clarification when durable
truth would otherwise require an unauthorized choice?

That is the rule-composition, row-level activation, and CE frontier.

## Tonight's Research Queue

The next work should stay on the sharp edges:

0. **Cold generalization baselines.** Ten newly admitted fixtures now test
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
   must not become an oracle selector. Sable Creek added a new general harness
   lesson: profile argument-role slots now have deterministic length/pattern
   constraints, because role names are schema labels, not places for source
   values or prose alternatives. Thornfield completed the current cold batch
   and independently repeated the governance-fixture pain: useful procedural
   rows, no executable rules, and misses around dimensional/authority joins.
   Sable's rule-lens replay then found a more important safety edge: no
   promotion credit for unbound-head rules or fact-shaped rule clauses. The
   latest compact-guidance replay moved the failure mode to a cleaner place:
   valid-but-unsupported rules are admitted as non-promotable, while derived-body
   composition attempts are held until a dependency exists.
1. **Rule composition transfer.** Glass Tide has promotion-ready slices for
   tax, salvage, quarantine, council veto, and support-threshold conditions.
   Sable and Avalon now show the discipline transfers: helper shape, body
   support, mapper gates, and promotion trials decide usefulness, not the mere
   presence of a Prolog-looking clause. The next frontier is joining
   intermediate conditions without collapsing provenance or overclaiming state.
2. **Rule probe discipline.** Recent preflight runs show that a rule can be
   body-supported but fail under the wrong scope atom, can become dormant by
   using lowercase placeholders such as `warden` and `repair_order`, or can look
   firing only because a sibling rule shares its derived head. Keep isolated
   per-rule promotion plus combined positive/negative probes in the loop.
3. **Clarification Eagerness drift.** CET-013 held the source-context lane at
   `40/40` after the latest rule-admission changes. The next CE move is safe
   partial richness and a small hard replay pack for variance, not another broad
   prompt patch.
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

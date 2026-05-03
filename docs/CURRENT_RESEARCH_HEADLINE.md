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

Clarification Eagerness Trap is exercising the companion governance frontier:

- the current CE high-water is `40/40` correct with `0` over-eager asks,
  `0` under-eager misses, `0` unsafe candidates, and `0` context-write
  violations;
- blocked-slot question coverage is now measured structurally from authored
  fixture slots and model-emitted clarification surfaces; CET-010 reached
  `10/10` blocked-slot coverage and `0` blocked-slot safe-write violations;
- CE must be measured across ingestion, query, safe partials, blocked rows, and
  authority-boundary violations.

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

1. **Glass Tide final-outcome composition.** Tax, salvage, quarantine, council
   veto, and council support-threshold conditions now have promotion-ready
   slices. The next frontier is a final outcome lens that joins intermediate
   conditions without collapsing provenance or overclaiming state.
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
- [Frontier Progress Report](https://github.com/dr3d/prethinker/blob/main/docs/FRONTIER_PROGRESS_REPORT.md)
- [Clarification Eagerness Strategy](https://github.com/dr3d/prethinker/blob/main/docs/CLARIFICATION_EAGERNESS_STRATEGY.md)
- [Project State](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md)
- [Glass Tide progress journal](https://github.com/dr3d/prethinker/blob/main/datasets/story_worlds/glass_tide_charter/progress_journal.md)
- [Clarification Eagerness Trap journal](https://github.com/dr3d/prethinker/blob/main/datasets/clarification_eagerness/clarification_eagerness_trap/progress_journal.md)

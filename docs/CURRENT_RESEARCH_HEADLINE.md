# Current Research Headline

Last updated: 2026-05-02

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

- broad compiles preserve rules as source records, but do not yet make them
  executable;
- a separate rule lens can admit executable clauses, including a role-joined
  repair rule that passes both positive and negative probes:
  `derived_authorization(repair_order_71, valid, glass_tide_repair)` succeeds,
  while the one-signer repair order does not;
- runtime trial exposes the real risks: overgeneralized class-predicate fanout
  versus clean but dormant rules whose bodies lack matching admitted facts;
- the verifier now checks body-goal support, so a rule is not considered
  promotion-ready merely because predicate signatures match.
- threshold tax rules now work over deterministic numeric helpers, but
  positive/negative probes exposed the next hard gap: exception-branch
  promotion for high-value relief cargo.
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

Clarification Eagerness Trap is exercising the companion governance frontier:

- the current CE high-water is `39/40` correct with `0` over-eager asks,
  `0` unsafe candidates, and `0` context-write violations;
- the remaining errors expose blocked-slot question posture and run-to-run
  variance, not just "ask more" or "ask less";
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

1. **Glass Tide vote aggregation.** Tax, salvage, quarantine, and the council
   budget-veto branch now have promotion-ready rule slices. The remaining
   council frontier is normal three-of-five aggregation plus override handling.
2. **Rule probe discipline.** Recent preflight runs show that a rule can be
   body-supported but fail under the wrong scope atom, can become dormant by
   using lowercase placeholders such as `warden` and `repair_order`, or can look
   firing only because a sibling rule shares its derived head. Keep isolated
   per-rule promotion plus combined positive/negative probes in the loop.
3. **Clarification Eagerness drift.** A post-move preflight run completed
   safely with `0` unsafe candidates and `0` context-write violations, but it
   over-asked badly. CET-008 later reached `39/40` with no context-write
   violations; the next move is structural blocked-slot/context-support review,
   not another broad prompt patch.
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

# Frontier Progress Report

Last updated: 2026-05-02

This report collects the current hard-fixture evidence for Prethinker. The raw
progress journals remain inside each dataset directory; this page is the
visitor-readable map of what improved, what regressed, and what the improvements
mean.

## Current Headline

**Semantic parallax:** one LLM compile is one viewpoint. The current architecture
frontier is multi-pass semantic compilation: backbone, support/source,
temporal/status, and rule lenses each propose a constrained view; the mapper
admits each view independently; deterministic union accumulates only admitted
clauses.

This matters because the latest fixtures show that one giant pass compresses or
dominates. Separate safe lenses can recover more useful symbolic surface without
weakening the authority boundary.

The important rule for these results:

```text
No Python prose interpretation.
```

Python may execute deterministic infrastructure: mapper admission, Prolog
runtime calls, cache keys, support-surface union, failure classification, and
structured artifact validation. Python must not read the source prose to derive
entities, predicates, facts, rules, or answers.

## Why These Fixtures Matter

Prethinker is not just trying to answer questions from text. It is trying to
turn messy language into a governed symbolic surface:

```text
source text
  -> model-owned context/profile/compiler passes
  -> Semantic IR candidate operations
  -> deterministic mapper admission
  -> Prolog KB
  -> post-ingestion query/answer checks
```

The frontier fixtures are designed to hurt different parts of that path:

- Iron Harbor: municipal water crisis, temporal corrections, policy violations,
  multilingual witness statements, and claim/fact separation.
- Blackthorn: procedural misconduct, authority chains, deadlines, findings,
  sanctions, financial dependencies, and stage-aware epistemic status.
- Kestrel Claim: maritime insurance, competing legal/financial positions,
  reinsurance deadlines, dual-role entities, citations, and temporal arithmetic.
- Anaplan Polaris: enterprise technical guidance, recommendations, risks,
  tradeoffs, procedures, and rationale-bearing support rows.
- Glass Tide Charter: dense charter rules, exceptions, permissions, tax,
  evidence priority, quarantine, temporal windows, and executable-rule trial.
- Clarification Eagerness Trap: ask/no-ask calibration for ingestion and query
  turns, safe partial commits, source-claim/quarantine without asking, ambiguous
  correction targets, and context-write authority hygiene.

## Headline Trajectories

| Fixture | Starting Point | Current High-Signal Result | Main Lesson |
| --- | ---: | ---: | --- |
| Iron Harbor | `42 exact / 14 partial / 44 miss` on first full-100 run | `86 exact / 14 partial / 0 miss` | Rich source-document surfaces plus temporal/query support can eliminate misses without letting derived answers leak into durable truth. |
| Blackthorn | `2 exact / 1 partial / 17 miss` on first-20 | `85 exact / 4 partial / 11 miss` exact high-water; `83 / 10 / 7` best exact-plus-partial split | Dense procedural documents need broad skeleton preservation plus targeted hard-row support, not simple profile widening. |
| Kestrel Claim | `5 exact / 0 partial / 15 miss` first-20 cold baseline | `73 exact / 11 partial / 16 miss` profile-guided full-100; `30 / 12 / 58` best source-aware full-100 | Domain packs are legitimate product context, but cold/source-aware claims must be reported separately from profile-guided runs. |
| Anaplan Polaris | `29 exact / 6 partial / 8 miss` full-43 baseline | `42 exact / 1 partial / 0 miss` | A safe union of independent mapper-admitted support views can outperform any single compile without using answer-key guidance. |
| Glass Tide Charter | cold profile bootstrap initially failed JSON; assisted starter first-20 was `7 exact / 2 partial / 11 miss` | cold compact bootstrap first-20 `13 exact / 3 partial / 4 miss`; GLT-023 has a probe-gated role-joined repair rule with `1/1` positive and `1/1` negative probes; GLT-027 unions tax lenses into `3` promotion-ready rules with all probes passing; GLT-029 unions body-fact and rule lenses into `2` promotion-ready salvage rules with reward/negative probes passing | Rule ingestion needs planned semantic lenses, active predicate palettes, helper substrates, body-goal support checks, positive/negative probes, and runtime verifier diagnostics, not more rule prose inside the default compile. |
| Clarification Eagerness Trap | `30/40` first full CE baseline | CET-008 high-water `39/40`, `0` over-eager, `1` under-eager, `0` unsafe candidates, `0` context-write violations; CET-009 variance check regressed to `37/40` | CE must be measured as a first-class frontier: ask posture, safe partials, blocked rows, context-write hygiene, and run-to-run variance are separate surfaces. |

## What Improved The Scores

The same pattern appears across fixtures:

- **Predicate contracts matter.** Predicate names alone are not enough; argument
  roles and source permissions must travel with the profile.
- **Output budget matters.** Long documents fail when the model spends too much
  output on workspace furniture and too little on candidate operations.
- **Backbone first, details second.** A broad admitted skeleton is more valuable
  than a narrow compile that chases one answer-shaped predicate family.
- **Post-ingestion QA has its own surface.** A compiled KB can contain the right
  facts while the query planner asks the wrong predicates.
- **Safe-surface union is powerful.** Multiple safe admitted compiles can be
  deterministically merged. That is not the same thing as trusting multiple LLM
  answers; every row still passed the mapper.
- **Support rows should be acquired separately.** Anaplan showed that widening
  the default profile with generic rationale predicates regressed, while
  support-only passes over the raw source plus admitted backbone improved the
  result.
- **Rules need their own lens.** Glass Tide showed that broad compiles preserve
  rules as records. Executable rule clauses start to appear when rule
  acquisition is separated, but runtime trial is needed to catch fanout and
  dormant-body failures.
- **Rule promotion needs body-goal diagnostics.** A span-local Glass Tide rule
  can be executable and runtime-loadable while still dormant because its body
  predicates have no matching admitted facts, or because the predicate/arity is
  right but the argument pattern is wrong. The rule trial now reports
  unsupported body signatures, unsupported body goals, and unsupported body
  fragments instead of leaving that diagnosis to manual clause reading.
- **Rule probes catch scope errors.** A rule can load, fire, and pass body
  support while still deriving the right subject/status under a neighboring
  scope atom. Positive/negative probes make that visible without giving the LLM
  write authority.
- **Threshold/exception rules need helper substrate.** Glass Tide's tax rule
  timed out even under a narrow active palette and `operation_target=1`. Adding
  deterministic `value_greater_than/2` and `value_at_most/2` helpers moved the
  threshold portion to `2` promotion-ready firing rules. GLT-024 then added
  authored positive/negative probes: the high-value and low-value threshold
  cases passed, but the high-value relief-cargo exemption did not. The next
  rule frontier is exception-branch acquisition, not generic threshold support.
- **Helper contracts need semantic argument checks.** GLT-026 showed that a
  model can select the right helper while calling it with the wrong argument:
  `value_greater_than(Value, 100)` after
  `entity_property(Cargo, value, Value)`. The verifier now flags this as an
  unsupported body fragment because numeric helpers are entity helpers, not raw
  comparison operators.
- **Safe rule-surface union beats forced one-pass rule bundles.** GLT-027
  deterministically unioned separately admitted threshold and exception rule
  lenses, dropped non-promotion-ready rules, and passed all tax probes without
  reading source prose or inferring new rules.
- **Rule acquisition may require body-fact acquisition first.** GLT-028 showed
  the salvage backbone lacked the actor recovery relation needed by any safe
  reward rule. A narrow body-fact lens admitted the missing `recovered_from_water`
  and sacred/abandoned rows; GLT-029 then acquired and unioned promotion-ready
  salvage rules.
- **Promotion-ready is not durable.** Glass Tide now separates rule lifecycle
  labels: candidate, mapper-admitted, runtime-loadable, firing,
  promotion-ready, and durable. Durable remains `0` in these trials; the point is
  to verify rule behavior before anything can become product truth.
- **Clarification eagerness is not one dial.** CE has ingestion/query phases,
  ask/no-ask posture, safe partial preservation, and authority-surface hygiene.
  A run can have good ask precision while still leaking context-sourced candidate
  writes, so the scorer now measures those separately. CET-008 reached `39/40`
  by sharpening the authority surface for context-support rows rather than by
  simply increasing or decreasing questions.

## Negative Results Worth Keeping

These regressions are part of the evidence:

- More prose guidance can reduce useful admitted coverage.
- Wider predicate menus can pull the compiler away from the durable backbone.
- Generic rationale predicates can be worse than no rationale predicates.
- Executing evidence-bundle plans by default can add answer-surface noise.
- Hardening argument contracts mid-run is a profile migration, not a tuning knob.
- Registry-guided/product-mode results should not be presented as cold discovery.
- Blunt global prompt pressure against context copying regressed CE from `37/40`
  strict to `35/40`; the right fix is structural separation of context support
  from candidate operations, not more prose.

## Current Frontier Problems

The remaining hard areas are now sharper:

- **Rule ingestion.** Facts and support rows are not enough. The product value
  depends on admitting executable rules safely enough for inference and, later,
  constraint propagation.
- **Temporal reasoning substrate.** Date anchors, intervals, duration helpers,
  and temporal corrections need to become durable enough for complex KB queries.
- **Predicate canonicalization drift.** Equivalent surfaces such as claim,
  allegation, finding, and observation need registry-owned alignment without
  Python reading prose.
- **Evidence/support planning.** Queries need reliable support bundles for
  multi-hop answers without contaminating already-exact answers.
- **Cold profile discovery.** Source-aware bootstrapping is improving, but
  profile-guided product mode remains stronger than cold discovery on hard
  specialist domains.
- **Epistemic state evolution.** Multi-stage documents need queryable transitions:
  who claimed what, when it was corrected, which stage accepted it, and what
  remains disputed.
- **Clarification eagerness.** Prethinker must ask early enough to avoid unsafe
  writes, but not so eagerly that safe source-claim/quarantine paths become
  needless dialogue. The current high-water removes context-write violations,
  but CET-009 shows the surface still varies and needs structural review for
  blocked-slot questions.

## Where The Raw Evidence Lives

- [Iron Harbor journal](https://github.com/dr3d/prethinker/blob/main/datasets/story_worlds/iron_harbor_water_crisis/progress_journal.md)
- [Blackthorn journal](https://github.com/dr3d/prethinker/blob/main/datasets/story_worlds/blackthorn_misconduct_case/progress_journal.md)
- [Kestrel journal](https://github.com/dr3d/prethinker/blob/main/datasets/story_worlds/kestrel_claim/progress_journal.md)
- [Anaplan Polaris journal](https://github.com/dr3d/prethinker/blob/main/datasets/enterprise_guidance/anaplan_polaris_performance_rules/progress_journal.md)
- [Glass Tide journal](https://github.com/dr3d/prethinker/blob/main/datasets/story_worlds/glass_tide_charter/progress_journal.md)
- [Clarification Eagerness Trap journal](https://github.com/dr3d/prethinker/blob/main/datasets/clarification_eagerness/clarification_eagerness_trap/progress_journal.md)
- [Current Research Headline](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_RESEARCH_HEADLINE.md)
- [Multi-Pass Semantic Compiler](https://github.com/dr3d/prethinker/blob/main/docs/MULTI_PASS_SEMANTIC_COMPILER.md)
- [Post-Ingestion QA Surfaces](https://github.com/dr3d/prethinker/blob/main/docs/POST_INGESTION_QA_SURFACES.md)
- [Project State](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md)

## Bottom Line

The strongest evidence is not that one fixture reached a good number. It is that
the same architecture improved across very different domains:

```text
model proposes structure
deterministic admission decides truth
Prolog answers from admitted state
failures are assigned to compile, query, answer, or hybrid surfaces
```

That is the research story. The hard work now is not proving that the direction
is plausible. It is making rule admission, temporal reasoning, and cold profile
discovery strong enough to survive the next fixtures.

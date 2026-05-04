# Active Research Lanes

Last updated: 2026-05-04

This page is the short operational map for choosing the next few hours of work.
It is intentionally stricter than a brainstorm: new ideas belong here only if
they advance multiple fixtures or protect the evidence quality of the project.

## Selection Rule

Prefer work that satisfies at least one of these:

- improves two or more cold fixtures without oracle context;
- improves one hard fixture and preserves regression fixtures;
- reduces a dominant cross-fixture failure surface;
- improves public/demo behavior without weakening the mapper authority boundary;
- makes future GPU runs cheaper or easier to interpret.

Avoid work that only raises one fixture score by adding input-specific hints,
gold KB vocabulary, answer-shaped strategy, or Python prose interpretation.

## Current Priority Order

| Priority | Lane | Why It Matters Now | Good Next Move |
| ---: | --- | --- | --- |
| 1 | Source-surface acquisition | Cold rollup shows compile gaps dominate: `159` compile gaps versus `35` hybrid/reasoning, `26` query, and `5` answer gaps. | Improve compact acquisition/lens coverage and replay against unlike fixtures such as Oxalis, Three Moles, Calder, and Avalon. |
| 2 | Rule composition and promotion | Product power comes from executable inference, but cold fixtures still admit `0` rules by default. Glass Tide proved the staged path. | Generalize body-fact -> rule-lens -> shortcut-audit -> probe workflow to Avalon/Sable/Oxalis without fixture-specific clauses. |
| 3 | Temporal/status/reasoning helpers | Regulatory, grant, ledger, recall, and story fixtures all need dates, intervals, deadlines, status-at-time, threshold, and exception helpers. | Add helper substrates only when two fixtures need the same helper shape. |
| 4 | Clarification and stenographer mode | Live UI use is streaming, not monolithic. CE and queued delivery protect truth while reducing interruption. | Build fixtures/runs that score queued-slot closure, safe partials, and later-turn resolution. |
| 5 | Query-surface selection | APR showed the KB can contain the answer while the query planner fails to ask for it. | Apply row-level/evidence-mode selectors after compile/reasoning changes, not as a substitute for missing source surface. |
| 6 | Anti-meta-rot cold replay | The harness must not become good only at its favorite fixtures. | Every general harness change should replay at least two cold fixtures and one older regression fixture. |
| 7 | Public research narrative | Visitors need to understand the newest real insight without drowning in run history. | Keep docs headline/current-lanes pages current; push journals after meaningful runs. |
| 8 | Domain expansion lanes | UMLS, CourtListener, SEC/contracts, and future finance/metathesaurus-style packs matter, but they should not distract from core compiler/governance lessons. | Advance when a domain pack tests a general admission, ontology, or rule-boundary problem. |

## Current Evidence

Cold baseline snapshot across `10` held-out fixtures:

```text
questions: 470
exact / partial / miss: 245 / 81 / 144
exact rate: 0.521
exact+partial rate: 0.694
failure surfaces:
  compile: 159
  hybrid/reasoning: 35
  query: 26
  answer: 5
```

This says the most useful next work is not a UI flourish, a broader prompt, or
a single fixture registry. The broadest payoff is better acquisition of the
right source surface, followed by reusable reasoning/rule substrates.

## Representative Fixtures

Use small sets rather than the whole zoo for each cycle:

| Cycle Type | Fixtures | Why |
| --- | --- | --- |
| Compile acquisition | Oxalis, Three Moles, Calder, Avalon | Regulatory deadlines, story causality, long state ledger, grant rows. |
| Rule composition | Glass Tide, Avalon, Sable Creek | Existing rule doctrine plus two fresh governance variants. |
| Temporal/status | Iron Harbor, Oxalis, Dulse, Ridgeline | Deadline, recall, ledger debt, fire/notice timing. |
| CE/stenographer | Clarification Eagerness Trap plus a turnstream variant | Ask/queue/hold/resolve behavior under authority boundaries. |
| Anti-regression | Iron Harbor, APR, CE, Glass Tide | Older successes that should not silently degrade. |

## GPU Cycle Template

Each long work block should look like this:

1. Pick one cross-cutting failure surface.
2. Choose two or three representative fixtures.
3. Run the smallest diagnostic replay that can show movement.
4. If a change helps only one fixture, label it fixture-local and do not make it default.
5. If it helps more than one fixture, promote the harness change and run targeted regression.
6. Record numbers in the fixture journal and public state summary.
7. Push after tests pass.

## Current Best Next Bite

Work on source-surface acquisition with rule/reasoning readiness in mind:

```text
target = compact acquisition coverage that improves unlike fixtures
first probes = Oxalis + Three Moles + Avalon
guardrails = no source-specific predicate clues, no gold KB, no QA-derived context
success = at least two fixtures improve or one improves with zero regression
```

That lane advances the most other lanes because better source rows feed rules,
temporal helpers, query planning, CE decisions, and public demos.

Current update: Three Moles improved when source_entity_ledger_v1 added
powerless `coverage_targets`, but an anti-meta-rot replay on Oxalis regressed
when the partial-skeleton recovery instruction was global. Keep that recovery
scoped to ledger-backed narrative passes until another unlike fixture shows
positive transfer.

Larkspur update: the URL-fixed permission/rationale acquisition lens is a
strong row-gated source-surface variant, not a global compile. It scores
`31 / 3 / 6` alone against the `20 / 7 / 13` baseline, with a judged row-gated
upper bound of `37 / 2 / 1`. Guarded activation now reaches that upper bound
with `40/40` best choices after adding answer-surface baseline guards for
identity/action-volume, award/result, and direct status/rule rows. This is the
current best example of using a focused compile lens while protecting exact
baseline rows.

New zip-batch update: Ashgrove Permit, Fenmore Seedbank, Greywell Pipeline,
Heronvale Arts, and Veridia Intake are promoted into `datasets/story_worlds`
and no longer live in `tmp/incoming`. The first-pass baseline over `123` QA
rows is `94 / 13 / 16`; the classified repair rollup is `97 / 11 / 15` with
`16` compile-surface targets, `8` hybrid/join targets, and `2` answer-surface
targets. This batch is now the active cold generalization scorecard for
permit/deadline, conservation ledger, incident investigation, grant-rule, and
turnstream correction behavior.

Activation update: query-mode selection now has deterministic structural and
hybrid structural+LLM controls. The hybrid path saves LLM calls on confident
rows and reached Avalon's Rule8 comparison upper bound (`27 exact / 12 partial
/ 1 miss`) while using structural choice on `13/40` rows. It regressed Three
Moles and Sable because LLM fallback overrode structurally exact relaxed
evidence, so hybrid selection remains diagnostic-only until uncertainty gating
transfers across unlike fixtures.

Harness update: clean KB pipeline factoring now has a daily-driver surface in
`src/kb_pipeline_clean` plus `scripts/run_kb_pipeline_clean_harness.py`. Use it
to capture canonical structural signatures before moving compiler/gate/apply
code; do not delete apparently unused legacy code until those signatures are
covering real fixture replay. The harness is now documented as an instrument in
`docs/CURRENT_HARNESS_INSTRUMENT.md`.

Story-world activation update: `scripts/summarize_rule_activation_transfer.py`
now summarizes existing Sable/Avalon rule-activation comparison artifacts
without rerunning compile or reading source prose. The direct-2400 transfer
summary covers `80` rows across the two fixtures, with `15` baseline rescues,
`7` baseline regressions, and `26` volatile rows. It now also emits activation
governor targets: `54` stable-any-mode rows, `15` clean nonbaseline rescues,
`7` baseline-exact protection rows, and `4` volatile rows where baseline remains
among the best modes. With the direct selector artifacts joined back in, the
governor audit passes `54/54` stable rows, `11/15` rescues, `6/7`
baseline-exact protection rows, and `2/4` volatile baseline-preferred rows. This
makes the next rule frontier clearer: activation needs row-level restraint, not
blanket rule-mode promotion. The same report now emits
`semantic_progress_assessment_v1`; selector-governor misses put the current
selector lane at `zombie_risk=medium`, meaning the next pass must have a named
expected contribution rather than another broad retry.

Rule update: Sable SC-007 is the current rule-composition transfer win. A
body-fact lens admitted `supported/2` vote rows, an aggregation lens derived
only `support_threshold_met`, and the promotion-filtered threshold+vote union
lifted full QA from `20 exact / 8 partial / 12 miss` to `24 / 6 / 10`. Keep
pushing this pattern, but retain the new restraint: aggregation lenses must not
emit sibling scopes or neighboring condition labels merely because the same
threshold helper can fire.

Verifier update: the AG-011/AG-012 Avalon lesson is now part of rule promotion
scoring rather than only post-hoc shortcut reporting. Repeated body predicates
that share multiple variables without distinct literal role anchors are blocked
as unsupported fragments, while the safe `submit_revised_budget` /
`provide_matching_docs` style remains admissible. This is a structural compiler
guardrail over admitted clauses, not Python interpretation of source prose.

Incoming fixture intake: new challenge fixtures should first pass the structural
envelope check before any compile or QA run:

```powershell
python scripts/validate_fixture_intake.py --root datasets/incoming_fixtures --out-json tmp/incoming_fixtures/intake_validation.json
python scripts/stage_incoming_fixtures.py --root tmp/incoming --out-root tmp/incoming_staged
```

This checks requested files, 40-row QA shape, source length, duplicate ids, and
obvious answer-key leakage without interpreting fixture prose. If incoming
`qa.jsonl` rows include authored answers, staging separates no-answer `qa.md`
from `oracle.jsonl` so source compilation and query planning stay oracle-clean.

Incoming smoke result: the first five new challenge fixtures now have a
standard artifact-only scorecard at `tmp/incoming_smoke_summaries/scorecard.md`.
All five now compile after `copperfall_deadline_docket` recovered through the
compact profile retry path, and the batch produced `44 exact / 4 partial / 2
miss` over `50` no-answer QA rows with `0` write proposal rows. The classified
non-exacts are still mostly source-surface problems:
`5` compile-surface gaps and `1` hybrid join gap.

Incoming harness comparison update: candidate smoke scorecards now get compared
artifact-to-artifact by `scripts/compare_incoming_smoke_scorecards.py`. A global
detail/specification guidance retry helped Meridian locally but regressed the
batch from `44 / 4 / 2` to `41 / 4 / 5`; the comparison artifact at
`tmp/incoming_smoke_summaries_detail_retry/baseline_comparison.md` marks it
`reject_candidate`. Treat that as the current lesson: detail repair should be a
scoped diagnostic or row-level acquisition pass, not a broad default prompt.

Incoming row-mode update: evidence-bundle context filtering over only the six
current non-exact rows produced a tempting aggregate (`46 / 1 / 3`) but still
increased misses by one, so the scorecard gate rejects it as a default. The row
overlay planner at
`tmp/incoming_smoke_summaries_evidence_nonexact/row_mode_overlay_plan.md` found
the actionable split: accept candidate evidence mode for Larkspur q007 and
Northbridge q007, reject it for Larkspur q009, and leave Meridian q006/q007 plus
Northbridge q010 unresolved. This is now a compact row-level selector target.

Selector update: the existing non-oracle QA-mode selector was replayed on that
six-row target. Deterministic structural scoring chose the best available mode
on `5/6` rows but accepted the bad Larkspur q009 evidence regression. The LLM
`activation` selector chose the best available mode on `6/6`, yielding `2 exact
/ 2 partial / 2 miss` instead of structural's `2 / 1 / 3`. The comparison
artifact is
`tmp/incoming_selector_runs/incoming-nonexact-structural-vs-activation.md`.
Treat this as a small positive selector calibration, not yet a broad default.

Full-slice selector caution: when evidence-bundle QA was rerun over the full
first-10 smoke slice for Larkspur/Meridian/Northbridge, global evidence mode
stayed at `44` exact but increased misses (`44 / 3 / 3`), and selector policy
was not monotonic. A selector JSON retry guard removed the Larkspur activation
parse failure; after that, structural selection over 30 rows reached `24 / 3 /
3` with `28/30` best-mode choices, while LLM `activation` reached `23 / 5 / 2`
with `28/30` best-mode choices. The retry comparison artifact is
`tmp/incoming_selector_runs/incoming-first10-structural-vs-activation-retry.md`.
Lesson: the six-row target is useful calibration, but daily-driver activation
still needs exact-row protection before promotion.

Protected selector update: `--selection-policy protected` now keeps structural
selection by default and calls activation only for high-volume nonbaseline
overrides. On the 30-row incoming first-10 slice it reached `24 / 4 / 2` with
`29/30` best-mode choices, preserving structural's exact count while reducing
misses by one. Avalon replay was mixed-positive (`28 / 11 / 1`, same exact
count and one fewer miss than structural/direct/activation), but Sable did not
transfer: protected matched structural at `22 / 6 / 12`, while direct stayed
better at `25 / 8 / 7`. Keep protected as a calibration control, not a default.

Compile-repair target update: `scripts/plan_incoming_compile_repair_targets.py`
now converts the official incoming scorecard plus row-overlay artifact into a
repair queue without reading source prose. Current queue:
`2` row-selector calibration targets, `3` scoped source-surface repair targets,
and `1` helper/query-join repair target. The artifact is
`tmp/incoming_smoke_summaries/compile_repair_targets.md`; the next compile-side
work should start with the three scoped source-surface rows rather than another
global detail prompt.

Promoted story-world repair update:
`scripts/plan_story_world_repair_targets.py` now generalizes that idea for
full-QA story-world scorecards. It reads scorecard artifacts only and classifies
repair lenses from query predicate names rather than source prose. The full-40
five-fixture queue remains `46` rows, but the planner makes the work legible:
`39` scoped source-surface repairs, `7` helper/query-join repairs, with
Larkspur as the top fixture (`20` targets). Larkspur splits into `6`
object-state, `5` object-location/custody, `4` permission/rationale, `2`
outcome/status, `1` claim-truth, `1` identity/role, and `1` temporal target.

Larkspur direct-profile acquisition check: bypassing profile discovery with the
tracked `story_world@v0` registry avoided the empty profile/intake responses,
but the resulting compiles were too thin to help. Object-state scored
`0 / 0 / 6` on target rows, custody scored `0 / 2 / 2`, and
permission/rationale scored `0 / 0 / 5`, all with `0` write proposals. Treat
this as a negative result: the next acquisition pass should keep the compact
focused-pass machinery and improve the acquisition contract, not fall back to a
direct registry-only compile.

URL/preflight update: the failed profile/intake attempts were partly a harness
URL issue. `run_domain_bootstrap_file.py` now normalizes LM Studio base URLs so
both `http://127.0.0.1:1234` and `http://127.0.0.1:1234/v1` hit the same chat
endpoint. After that fix, Larkspur permission/rationale acquisition became the
best new source-surface candidate: `5 / 0 / 0` on its target rows and
`31 / 3 / 6` on full-40. It still regresses `6` baseline-exact rows, so the
lesson is row-gated acquisition, not global replacement.

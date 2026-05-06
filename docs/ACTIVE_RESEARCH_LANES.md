# Active Research Lanes

Last updated: 2026-05-06

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

## Lens Roster Note

The harness is now being treated as an artifact-first semantic instrument:
compile once, persist the source/KB/IR/run artifacts, then run cheaper semantic
parallax passes against frozen artifacts. `docs/SEMANTIC_INSTRUMENT.md` is the
public companion for that idea. `docs/SEMANTIC_LENS_ROSTER.md` remains the
deeper lab roster for current lens facets, selector guardrails, and uncertainty
vocabulary. Use that roster when naming new lenses so names describe the
guardrail or semantic reason, not the fixture that first exposed it.

Selector guard growth is now tracked by
`docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`: `53` guard return sites collapse to
`52` unique reasons across `7` families with `0` unclassified. Treat that
family count, not the raw guard count, as the anti-sprawl metric.

Cross-fixture repair growth is now tracked by
`docs/CROSS_FIXTURE_REPAIR_SLICES.md`: the current planner reads repair-target
artifacts only and turns `72` unresolved targets across `10` fixtures into `9`
multi-fixture slices. Use this to pick GPU work that transfers before adding
another lens or guard.

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

Current score-hold check: Larkspur, Calder, Oxalis, Avalon, and Sable frozen
selector lanes still match their documented results with perfect selected-best
counts and `0` selector errors; full verification is `614 passed`.

First repair-slice action: the rule-interpretation/application pass is a
Meridian win and a Heronvale boundary marker. Meridian full-40 now reaches
`39 / 1 / 0` with `14` baseline rescues and `0` baseline-exact regressions.
Heronvale's targeted rows were clean (`3 / 0 / 0`), but full QA is only
`21 / 3 / 1` and regresses one baseline-exact row. Next use the surface as a
candidate mode and transfer probe, not a global compile default.

Second repair-slice action: the combined `object_state_custody` compile is a
negative transfer result and should not become a default. Fenmore fell to
`12 / 3 / 10` versus its `20 / 1 / 4` baseline, and Larkspur fell to
`27 / 7 / 6` versus the sharper final-state artifact at `36 / 2 / 2`. The
positive result is selector-level: adding the dangerous Fenmore object/status
artifact to the frozen roster creates a `25 / 0 / 0` upper bound, and the new
`deaccession-yet` status guard reaches `25 / 0 / 0` with `25/25`
selected-best rows. This reinforces the pegboard model: object final state,
custody roster, rationale, operational threshold/status, and deaccession-yet
status are separate hooks.

Third repair-slice action: `temporal_status_deadline` also split cleanly into
row-level selector gain and global compile rejection. Ashgrove's broad temporal
compile is not a default (`19 / 5 / 1` versus operational `21 / 4 / 0`), but
adjusted-expiration and correction-entitlement guards lift the frozen selector
to `24 / 1 / 0` with `25/25` selected-best rows. Copperfall's broad temporal
compile regresses to `25 / 5 / 10` against its `38 / 1 / 1` high-water; q024 is
rescued, but q034 points to deadline-family query disambiguation.

Follow-up query-surface action: deadline-family disambiguation is now a
query-only companion over admitted `deadline_calculated/5` rows. On Copperfall's
same rejected temporal compile, full QA improves from `25 / 5 / 10` to
`30 / 5 / 5`, with `8` rescues and `0` exact regressions. This helper is
support retrieval, not a new compile lens.

Second query-surface action: sparse status anchors now get query-only interval
support. When exact `case_status_at_date/3` lookup misses for a concrete
case/date, the harness exposes the latest prior admitted status anchor and the
next later anchor without writing a derived fact. On Copperfall this lifts the
same artifact to `35 / 4 / 1`, with `6` more rescues and `0` exact
regressions. The remaining status problem is the stay overlay, which should be
made explicit as compile/status-override surface rather than inferred from
nearby prose-shaped docket atoms.

Current update: Three Moles improved when source_entity_ledger_v1 added
powerless `coverage_targets`, but an anti-meta-rot replay on Oxalis regressed
when the partial-skeleton recovery instruction was global. Keep that recovery
scoped to ledger-backed narrative passes until another unlike fixture shows
positive transfer.

Rule-activation update: Sable/Avalon now have a cleaner frozen-artifact
selector replay for promoted rule surfaces. The guarded selector reaches the
available upper bound on both fixtures: Avalon `32 / 7 / 1`, Sable `26 / 7 / 7`,
and `80/80` selected-best rows. The cross-fixture activation governor improves
from `7` failures under the older direct selector to `1` failure, while all
nonbaseline rescue and baseline-exact protection targets pass. The remaining
work is not more fixture-local selector polish; it is source/rule evidence
acquisition for the rows whose upper bound is still partial or miss, plus
transfer checks on unlike rule fixtures.

Larkspur update: the URL-fixed permission/rationale acquisition lens is a
strong row-gated source-surface variant, not a global compile. It scores
`31 / 3 / 6` alone against the `20 / 7 / 13` baseline, with a judged row-gated
upper bound of `37 / 2 / 1`. Guarded activation now reaches that upper bound
with `40/40` best choices after adding answer-surface baseline guards for
identity/action-volume, award/result, and direct status/rule rows. This is the
current best example of using a focused compile lens while protecting exact
baseline rows.

Current score-hold/frontier replay: Avalon, Oxalis, and Three Moles were rerun
with the current flat-plus-focused harness and markdown answer-key judging.
The combined result is `97 exact / 10 partial / 13 miss` across `120` rows:
Avalon `34 / 2 / 4`, Oxalis `36 / 4 / 0`, and Three Moles `27 / 4 / 9`, all
with `0` write proposals and `0` runtime load errors. Two tempting prompt/hint
probes were rejected: a broad Three Moles micro-detail narrative instruction
fell to `16 / 9 / 15`, and a cleaner Oxalis recall/regulatory hint fell to
`24 / 11 / 5`. Lesson: current acquisition progress is real, but broad
descriptive prompts and prettier domain labels can thin the profile. Next work
should use artifact-level row selection or focused variants, not global prompt
growth. The reproducible scorecard command is
`scripts/rollup_domain_bootstrap_qa_scorecard.py`, with the current local
artifact at `tmp/story_world_cold_qa/avalon_oxalis_three_moles_scorecard.md`.
The repair planner now accepts that generic scorecard shape and names the
frontier slices as `narrative_event_detail_surface`
(`12` targets), `governance_authority_rationale_surface` (`6`), and
`object_state_transition_surface` (`1`), plus `4` rows still too generic for a
named acquisition family. This is the next useful pegboard: narrative concrete
detail and governance authority/rationale, not another broad compile prompt.

New zip-batch update: Ashgrove Permit, Fenmore Seedbank, Greywell Pipeline,
Heronvale Arts, and Veridia Intake are promoted into `datasets/story_worlds`
and no longer live in `tmp/incoming`. The first-pass baseline over `123` QA
rows is `94 / 13 / 16`; the classified repair rollup is `97 / 11 / 15` with
`16` compile-surface targets, `8` hybrid/join targets, and `2` answer-surface
targets. This batch is now the active cold generalization scorecard for
permit/deadline, conservation ledger, incident investigation, grant-rule, and
turnstream correction behavior.

Operational-record honing update: `operational_record_status_v1` is useful as a
row-level lens but rejected as a global compile surface. Raw candidate score is
`96 / 20 / 7` against the zip-batch baseline `97 / 11 / 15`, while the
artifact-only row gate says `111 / 11 / 1` is available. The no-oracle guarded
selector now has an operational/status uncertainty guard and reaches
`101 / 17 / 5`; Greywell hits its per-row selector upper bound at `24 / 1 / 0`.
The baseline-readiness guard then protects direct baseline application/status,
counterfactual rule, and hold/readiness support from broad or relaxed-heavy
candidate surfaces, moving the same frozen-artifact selector rollup to
`106 / 12 / 5` with `117/123` selected-best rows and no new misses. The
question-act guard then fixes the two cleanest remaining hard misses:
request-filing timeliness and commit-readiness. In full replay, hard misses
drop from `5` to `3` while exact count stays flat because unrelated Heronvale
activation rows vary downward. The surface-specificity guard then reaches
`110 / 10 / 3` with `121/123` selected-best rows by protecting explicit
rationale-note, decision-status, and priority predicate surfaces. The
complete-selector guard adds split-rationale, current-constitution, and
resubmission proof/rule distinctions, reaching `111 / 11 / 1` with `123/123`
selected-best rows against the frozen artifact upper bound. Next work is no
longer more tiny selector repair on this batch; it is source-surface/evidence
acquisition for the remaining miss, transfer replay on unlike fixtures, and
selector variance control rather than more broad operational compile prompting.
Fenmore immediately validated that next shape: a rationale/contrast source-note
lens is weak globally (`17 / 1 / 7`) but, under row selection, closes Fenmore to
`24 / 1 / 0` with `25/25` selected-best rows. Treat source-note rationale as a
row-level lens for why/contrast questions, guarded by direct identity and
threshold/status surfaces elsewhere.
Targeted transfer now supports that treatment across the zip batch: Ashgrove,
Fenmore, Greywell, Heronvale, and Veridia reach `49 / 3 / 0` over `52`
reason/status/evidence/correction/commit rows with `52/52` selected-best
choices. Next work should broaden the transfer check carefully, not by firing
four full judged QA runs at once; the current LM Studio setup handled targeted
parallel slices well but wedged under full-25 parallel judging.
The older-fixture transfer check is intentionally more sobering: Larkspur,
Northbridge, Copperfall, and Meridian targeted rows scored `17 / 9 / 7` over
`33` rows. Northbridge and Copperfall show positive transfer on
discrepancy/authority and correction/status surfaces, while Meridian was clean
on only a two-row probe. Larkspur remains the hard source-surface frontier:
why/custody/object-state rows are still mostly compile gaps. Treat this as a
boundary marker for `rationale_contrast_source_note_lens`, not a reason to
widen the prompt.
Larkspur's next focused acquisition pass found the stronger shape:
`final_object_state_transition_surface` is healthy and globally useful,
reaching `36 / 2 / 2` full-40 with only q009 as a baseline-exact regression.
Permission/motive remains row-useful but unsafe globally (`16 / 12 / 12`), and
custody is weak except for q038. The artifact overlay target is now almost
embarrassingly concrete: state for most rows, old permission/rationale for
q011/q036, custody for q038, and protected original baseline q009 gives a
judged `40 / 0 / 0` target. The next selector frontier is not more broad
compile prompting; it is retained q009 identity evidence or a sharper
official-role acquisition lens that gives the selector something honest to
choose.
That frontier closed with a row lens, not a global compile:
`official_role_authority_definition_surface` makes q009 exact by preserving role
authority/duties separately from action examples, while its full-40 result
(`21 / 9 / 10`) keeps it selector-only. Guarded activation over state,
permission/rationale, role-authority, and custody artifacts now reaches
`40 / 0 / 0` on Larkspur full-40 after five reason-named guards:
superlative identity, official-role definition, current component state,
custody-transfer rationale, and award placement. This is selector closure over
frozen artifacts, not a new monolithic prompt.
Transfer also stays honest: the same state lens scored `0 / 2 / 7` on Three
Moles final-state rows, `1 / 0 / 14` on Otters final-state/restitution rows,
and `10 / 2 / 8` on Calder's Reach final ownership/status rows. Larkspur's
state gain transfers as a method, not as a universal prompt.
Calder's follow-up confirms the method: current-state conflict, possession /
inheritance, and legal-title/default surfaces are each unsafe as broad
replacements, but the four-surface overlay reaches `14 / 3 / 3` over the
20-row final/current-state slice, up from final-state alone at `10 / 2 / 8`.
The guarded selector now matches that upper bound with `20/20` selected-best
rows after role-reinstatement, carry/possession, legal-title, contract-authority,
and guardianship-resumption guards. Treat this as evidence for artifact-first
surface routing, not permission to widen compile prompts.
Anti-overtune replay is currently clean: after the Calder guards landed,
Larkspur, Fenmore, Ashgrove, Greywell, Heronvale, and Veridia were rerun against
their frozen selector artifacts. The clean replay covers `163` rows and reaches
`153 / 10 / 0`, matching each fixture's available upper bound with `163/163`
selected-best rows. One initial Ashgrove pass hit transient LM Studio HTTP 500
fallbacks and recovered on rerun; keep recording selector/orchestration
variance separately from semantic regressions.
Oxalis pushes the unlike-domain access lane: over the frozen OX-003 compile,
evidence-bundle access improved full-40 from `27 / 8 / 5` to `32 / 6 / 2`, and
new regulatory access guards let guarded selection match the two-mode upper
bound at `33 / 6 / 1`. The lesson is not more source prompting; it is that
healthy compiles still need access surfaces for universal-scope rows, denial
threshold rationale, explicit negative lot checks, and counterfactual deadline
classification.

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

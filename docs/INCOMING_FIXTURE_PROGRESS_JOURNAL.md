# Incoming Fixture Progress Journal

Last updated: 2026-05-04

This journal preserves discoveries from staged incoming fixtures while their
raw run artifacts still live under ignored `tmp/` paths. It is a durable lab
record, not an oracle file and not compile context.

The current batch lives under `tmp/incoming_staged`:

- `copperfall_deadline_docket`
- `harrowgate_witness_file`
- `larkspur_clockwork_fair`
- `meridian_permit_board`
- `northbridge_authority_packet`

These fixtures have now been promoted into `datasets/story_worlds/`. The `tmp`
paths remain generated artifact/run locations, not the durable research home.

## Policy

- Incoming fixtures start as `cold_unseen` unless explicitly labeled otherwise.
- Python may stage, validate, compile, run QA, judge, classify, score, compare,
  and package artifacts.
- Python must not read source prose to infer answers or author answer-shaped
  fixture repairs.
- Scorecards and selector reports are diagnostic artifacts. They can guide
  general harness changes, but they are not compile hints.
- When an incoming fixture becomes a durable research lane, promote it into
  `datasets/...` with its own `progress_journal.md`.

## 2026-05-04 Batch Baseline

The first standard incoming smoke scorecard compiled all five fixtures:

```text
fixtures compiled: 5/5
qa rows: 50
score: 44 exact / 4 partial / 2 miss
write proposals: 0
```

Per-fixture baseline:

| Fixture | Score | Key Note |
| --- | ---: | --- |
| `copperfall_deadline_docket` | `10 / 0 / 0` | Recovered through compact profile retry. |
| `harrowgate_witness_file` | `10 / 0 / 0` | Clean first-10 smoke run. |
| `larkspur_clockwork_fair` | `8 / 2 / 0` | Two compile-surface partials around youngest exhibitor and warden role surface. |
| `meridian_permit_board` | `8 / 1 / 1` | One helper/query-join partial and one compile-surface miss. |
| `northbridge_authority_packet` | `8 / 1 / 1` | Medium semantic-progress risk; compile surface needs named expected contribution. |

Tracked summary references:

- `docs/CURRENT_HARNESS_INSTRUMENT.md`
- `docs/CURRENT_RESEARCH_HEADLINE.md`
- `PROJECT_STATE.md`

Ignored local artifact references:

- `tmp/incoming_smoke_summaries/scorecard.json`
- `tmp/incoming_smoke_summaries/scorecard.md`
- `tmp/incoming_smoke_summaries/compile_repair_targets.md`

## 2026-05-04 Broad Detail Retry

A broad detail/specification retry improved Meridian locally but regressed the
batch:

```text
score: 41 exact / 4 partial / 5 miss
promotion: reject_candidate
```

Discovery: broad global compile guidance is too blunt for this batch. The
instrument should promote by batch deltas and miss protection, not by a
single-fixture improvement.

## 2026-05-04 Evidence-Bundle Diagnostic

A narrow evidence-bundle diagnostic over current non-exacts lifted exact rows
but increased misses:

```text
baseline: 44 exact / 4 partial / 2 miss
candidate: 46 exact / 1 partial / 3 miss
promotion: reject_candidate
```

Discovery: evidence mode is useful row-by-row, but not as a global default.
The row overlay plan exposed the selector problem directly: accept rescues,
reject regressions, and leave unchanged non-exacts visible.

## 2026-05-04 Protected Selector

`--selection-policy protected` used structural selection by default and called
activation only for high-volume nonbaseline overrides.

Incoming first-10 selector slice over Larkspur, Meridian, and Northbridge:

```text
structural: 24 exact / 3 partial / 3 miss
activation: 23 exact / 5 partial / 2 miss
protected: 24 exact / 4 partial / 2 miss
```

Discovery: protected selection reduced misses without improving exact count,
and it did not transfer cleanly to Sable. It remains calibration machinery, not
the daily-driver policy.

## 2026-05-04 Ledger Compile Diagnostic

A source-entity-ledger compile diagnostic was run without QA hints or answer
keys. It was tested on the three imperfect incoming fixtures and combined with
baseline Copperfall/Harrowgate rows for a five-fixture candidate scorecard.

Compile/QA result:

| Fixture | Ledger Score | Compile Health | Key Note |
| --- | ---: | --- | --- |
| `larkspur_clockwork_fair` | `8 / 1 / 1` | `healthy` | Regressed q007 from partial to miss. |
| `meridian_permit_board` | `9 / 0 / 1` | `healthy` | Repaired q006 from partial to exact. |
| `northbridge_authority_packet` | `8 / 1 / 1` | `poor` | Very thin compile; repaired one row but damaged another. |

Five-fixture ledger candidate:

```text
baseline: 44 exact / 4 partial / 2 miss
candidate: 45 exact / 2 partial / 3 miss
promotion: reject_candidate
```

Discovery: ledger is not a batch default, but it is a useful alternate mode
for row-level selection.

Row overlay result:

| Decision | Fixture | Row | Meaning |
| --- | --- | --- | --- |
| reject | `larkspur_clockwork_fair` | `q007` | Ledger changed partial to miss. |
| accept | `meridian_permit_board` | `q006` | Ledger changed partial to exact. |
| accept | `northbridge_authority_packet` | `q007` | Ledger changed partial to exact. |
| reject | `northbridge_authority_packet` | `q006` | Ledger changed exact to partial. |

Ignored local artifact references:

- `tmp/incoming_smoke_summaries_ledger_repair/scorecard.md`
- `tmp/incoming_smoke_summaries_ledger_repair/baseline_comparison.md`
- `tmp/incoming_smoke_summaries_ledger_repair/row_mode_overlay_plan.md`

## 2026-05-04 Guarded Activation Selector

The selector harness now has two changes from this batch:

1. A mode can merge canonical QA artifacts with `+`, so selector input can use
   the same first-pass + failure-classified row view as scorecards.
2. `--selection-policy guarded_activation` keeps deterministic structural
   scoring for confident rows and calls the activation selector with bounded
   self-check evidence for uncertain rows.

Guarded activation over the three imperfect first-10 fixtures:

```text
larkspur: 8 exact / 2 partial / 0 miss
meridian: 9 exact / 0 partial / 1 miss
northbridge: 9 exact / 0 partial / 1 miss
combined: 26 exact / 2 partial / 2 miss
selected best available mode: 30/30 rows
```

Discovery: the next useful query-surface policy is not "use ledger" and not
"trust activation everywhere." It is guarded row-level activation over
competing compiled/query modes, with canonical artifact merging and
exact-regression protection.

Code landed in commit:

```text
fbe5043 Add guarded activation selector policy
```

## Current Repair Queue

The current six-row repair pack splits into:

```text
row-selector calibration: 2
scoped source-surface repair: 3
helper/query-join repair: 1
```

Current practical next moves:

1. Keep `guarded_activation` as a selector promotion candidate and replay it
   against older selector-transfer fixtures before treating it as a default.
2. Use Meridian q006 and Northbridge q007 as positive row-selector calibration
   examples, and Larkspur q007 plus Northbridge q006 as protection examples.
3. Continue compile-side repair on unresolved Meridian q007 and Northbridge q010
   without answer-shaped prompting.
4. Promote any incoming fixture with repeated discoveries into `datasets/...`
   and give it its own `progress_journal.md`.

## 2026-05-04 Guarded Activation Transfer Check

Guarded activation was replayed against older Avalon and Sable rule-activation
mode packs before treating the incoming result as a policy win.

Avalon comparison:

| Policy | Exact | Partial | Miss | Best Rows |
| --- | ---: | ---: | ---: | ---: |
| `structural` | 28 | 10 | 2 | 36 |
| `direct` | 28 | 10 | 2 | 35 |
| `protected` | 28 | 11 | 1 | 36 |
| `guarded_activation` | 28 | 9 | 3 | 35 |

Sable comparison:

| Policy | Exact | Partial | Miss | Best Rows |
| --- | ---: | ---: | ---: | ---: |
| `structural` | 22 | 6 | 12 | 33 |
| `direct` | 25 | 8 | 7 | 39 |
| `protected` | 22 | 6 | 12 | 33 |
| `guarded_activation` | 25 | 6 | 9 | 37 |

Discovery: guarded activation is a strong incoming-ledger diagnostic policy,
but it is not a cross-fixture default. Avalon still prefers protected for miss
control, while Sable still prefers direct. The durable lesson is sharper than
"activation helps": selector policy needs fixture/mode risk detection before
LLM fallback is allowed to override a mode that older evidence already handles.

Ignored local artifact references:

- `tmp/selector_policy_comparisons/avalon-guarded-activation-transfer.md`
- `tmp/selector_policy_comparisons/sable-guarded-activation-transfer.md`
- `tmp/rule_activation_mode_packs/avalon-rule-activation-guarded_activation_selector.md`
- `tmp/rule_activation_mode_packs/sable-rule-activation-guarded_activation_selector.md`

## 2026-05-04 Selector Risk-Gate Planner

`scripts/plan_selector_risk_gate.py` now turns the transfer lesson into a
named artifact-only planner. It compares a baseline selector run with a
candidate selector run and optionally reads selector-policy comparison reports
to decide whether the candidate policy has transfer support.

Rows are split into:

- `safe_activation_target`: candidate improves the baseline row and the
  candidate policy has measured transfer support.
- `calibration_activation_target`: candidate improves the baseline row, but
  transfer support is weak or unmeasured.
- `protect_baseline_target`: candidate regresses the baseline row.
- `needs_compile_repair`: no compared mode has an exact row available.
- `stable_no_action`: candidate does not change the row and an exact mode is
  available.

Incoming guarded-activation gate results using Avalon/Sable transfer checks:

| Fixture | Recommendation | Transfer | Safe | Calibration | Protect | Compile Repair |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `larkspur_clockwork_fair` | `do_not_promote_candidate_policy` | `weak` | 0 | 0 | 0 | 2 |
| `meridian_permit_board` | `do_not_promote_candidate_policy` | `weak` | 0 | 1 | 0 | 1 |
| `northbridge_authority_packet` | `do_not_promote_candidate_policy` | `weak` | 0 | 1 | 0 | 1 |

Discovery: the incoming policy win is real but remains calibration evidence.
The planner now forces the correct next question: what policy-family signal
would make a candidate activation rescue transfer-supported rather than merely
locally attractive?

Ignored local artifact references:

- `tmp/selector_risk_gates/larkspur-guarded-activation-risk-gate.md`
- `tmp/selector_risk_gates/meridian-guarded-activation-risk-gate.md`
- `tmp/selector_risk_gates/northbridge-guarded-activation-risk-gate.md`

## 2026-05-04 Scoped Compile Repair Diagnostic

Two scoped cold compiles were run without answer keys in compile context:

- Meridian: lot/use/occupant/zoning surface pressure.
- Northbridge: resolution/vote/adoption/document-metadata surface pressure.

Target-row checks:

```text
meridian q007: miss -> exact
northbridge q010: miss -> exact when run alone
```

The full first-10 regression replay was more informative:

| Fixture | Baseline | Scoped Candidate | Lesson |
| --- | ---: | ---: | --- |
| `meridian_permit_board` | `8 / 1 / 1` | `8 / 1 / 1` | q007 repaired, but q010 regressed from exact to miss. |
| `northbridge_authority_packet` | `8 / 1 / 1` | `9 / 1 / 0` | q007 became exact and q010 improved from miss to partial. |

Five-fixture scoped candidate:

```text
baseline: 44 exact / 4 partial / 2 miss
candidate: 45 exact / 4 partial / 1 miss
write proposals: 0
```

The scorecard comparer initially marked this as a promotion from aggregate
deltas alone. That exposed a harness bug: aggregate exact gain can hide a
baseline-exact row regression. The comparer now reports
`baseline_exact_regression_rows` and returns `row_level_gate_required` when a
candidate improves the batch while damaging a previously exact row.

Current comparison:

```text
recommendation: row_level_gate_required
exact delta: +1
miss delta: -1
baseline-exact regressions: 1
regressed row: meridian_permit_board q010
```

Updated repair-target split:

```text
row-selector calibration: 3
scoped source-surface repair: 2
helper/query-join repair: 1
```

Discovery: scoped compile pressure can produce real batch lift, but daily-driver
promotion must be row-gated. Northbridge's remaining q010 problem has shifted
from compile-surface miss to query-surface partial; Meridian q010 is now the
exact-protection regression that blocks promotion.

Ignored local artifact references:

- `tmp/incoming_smoke_summaries_scoped_repair/scorecard.md`
- `tmp/incoming_smoke_summaries_scoped_repair/baseline_comparison.md`
- `tmp/incoming_smoke_summaries_scoped_repair/row_mode_overlay_plan.md`
- `tmp/incoming_smoke_summaries_scoped_repair/compile_repair_targets.md`

## 2026-05-04 Row-Gated Scorecard Plan

`scripts/plan_incoming_row_gated_scorecard.py` now computes the protected
scorecard implied by a row overlay: accepted candidate rows are applied over
the baseline, while rejected rows keep baseline behavior.

For the scoped compile-repair candidate:

```text
baseline: 44 exact / 4 partial / 2 miss
ungated candidate: 45 exact / 4 partial / 1 miss
row-gated plan: 46 exact / 4 partial / 0 miss
```

Accepted rows:

- `meridian_permit_board q007`: miss -> exact
- `northbridge_authority_packet q007`: partial -> exact
- `northbridge_authority_packet q010`: miss -> partial

Rejected row:

- `meridian_permit_board q010`: exact -> miss

Discovery: the current best product-shaped goal is not another global compile
prompt. It is row-gated activation over competing compile/query surfaces. The
concrete target is now `46 / 4 / 0` on the incoming five-fixture first-10
scorecard.

Ignored local artifact reference:

- `tmp/incoming_smoke_summaries_scoped_repair/row_gated_scorecard_plan.md`

## 2026-05-04 Scoped Evidence Candidate

The row-gated target was then realized as an actual replay by combining scoped
compile repair with evidence-bundle query choreography:

- Meridian used the scoped lot/use/zoning compile plus evidence-bundle QA.
- Northbridge used the scoped resolution/vote compile plus evidence-bundle QA.
- Copperfall, Harrowgate, and Larkspur stayed on their current baseline paths.

Result:

```text
baseline: 44 exact / 4 partial / 2 miss
scoped evidence candidate: 46 exact / 4 partial / 0 miss
write proposals: 0
baseline-exact regressions: 0
scorecard gate: promote_candidate
```

Fixture movement:

| Fixture | Baseline | Candidate | Note |
| --- | ---: | ---: | --- |
| `meridian_permit_board` | `8 / 1 / 1` | `9 / 1 / 0` | q007 repaired and q010 protected by evidence query choreography. |
| `northbridge_authority_packet` | `8 / 1 / 1` | `9 / 1 / 0` | q007 exact, q010 partial, no misses. |
| `larkspur_clockwork_fair` | `8 / 2 / 0` | `8 / 2 / 0` | Still true compile-surface work. |

Updated repair queue:

```text
targets: 4
scoped source-surface repair: 3
helper/query-join repair: 1
miss rows: 0
```

Remaining rows:

- `larkspur_clockwork_fair q007`: youngest exhibitor, compile surface.
- `larkspur_clockwork_fair q009`: Fair Warden Osric Thane, compile surface.
- `meridian_permit_board q006`: Lot 7 river-distance join, hybrid/query join.
- `northbridge_authority_packet q007`: hydrant requirement detail, compile surface partial.

Discovery: the first incoming batch now has a promoted diagnostic recipe with
zero misses. The next frontier is reducing partials without reintroducing
exact-row regressions.

Ignored local artifact references:

- `tmp/incoming_smoke_summaries_scoped_evidence/scorecard.md`
- `tmp/incoming_smoke_summaries_scoped_evidence/baseline_comparison.md`
- `tmp/incoming_smoke_summaries_scoped_evidence/compile_repair_targets.md`

## 2026-05-04 Compile-Variant Overlay Diagnostic

The next partial-reduction sweep tried three scoped compile variants:

- Larkspur age/warden repair with source-entity ledger context.
- Meridian spatial-distance repair.
- Northbridge hydrant-spacing repair.

Target-row results:

| Fixture | Target | Result | Lesson |
| --- | --- | --- | --- |
| `larkspur_clockwork_fair` | q007/q009 | no promotion | New compile regressed the target rows; keep baseline. |
| `meridian_permit_board` | q006 | exact under spatial compile | The river-distance surface can be recovered, but the same compile leaves q007 partial. |
| `northbridge_authority_packet` | q007 | exact under hydrant compile | Hydrant count/spacing is recovered, but q004 becomes partial. |

Five-fixture shifted-variant scorecard:

```text
baseline scoped-evidence recipe: 46 exact / 4 partial / 0 miss
shifted compile variants:        46 exact / 4 partial / 0 miss
scorecard gate: row_level_gate_required
```

The aggregate is neutral, but the rows are complementary. The new
`scripts/plan_incoming_compile_variant_overlay.py` planner records this as a
judged artifact upper bound:

```text
overlay target: 48 exact / 2 partial / 0 miss
accepted variant rows: 2
protected baseline-exact rows: 2
unchanged non-exacts: 2
```

Accepted variant rows:

- `meridian_permit_board q006`: partial -> exact via spatial-distance compile.
- `northbridge_authority_packet q007`: partial -> exact via hydrant-spacing compile.

Protected baseline-exact rows:

- `meridian_permit_board q007`: keep baseline/scoped-evidence recipe.
- `northbridge_authority_packet q004`: keep baseline/scoped-evidence recipe.

Discovery: compile-side gains now exist as complementary surfaces rather than
one better compile. The next harness problem is a non-oracle compile-variant
selector with exact-row protection; the remaining true unresolved rows are
Larkspur q007 and q009.

Ignored local artifact references:

- `tmp/incoming_smoke_summaries_compile_variant_selection/scorecard.md`
- `tmp/incoming_smoke_summaries_compile_variant_selection/row_gated_scorecard_plan.md`
- `tmp/incoming_smoke_summaries_compile_variant_selection/compile_variant_overlay_plan.md`

## 2026-05-04 Larkspur Attribute/Duty Guardrail And Official Companion

Larkspur q007 showed a right-shaped/wrong-slot failure: Cassia's age had been
treated as name/alias-like surface instead of a query-bearing character
attribute. The compiler context now has a general narrative guardrail:

- numeric ages and other source-stated character attributes should not be
  encoded as names, aliases, or role labels;
- named officials need duty/authority surface when the profile supports it,
  not just a role row.

The first guarded Larkspur replay is diagnostic, not promotable:

```text
larkspur baseline: 8 exact / 2 partial / 0 miss
guarded replay:    8 exact / 1 partial / 1 miss
compile health: poor
semantic action: stop_and_report_struggle
scorecard gate: reject_candidate
```

Useful row movement:

- `larkspur_clockwork_fair q007`: partial -> exact via `person_role(..., youngest_exhibitor)`.

Regression held behind exact protection:

- `larkspur_clockwork_fair q010`: exact -> miss in the guarded replay.

Still unresolved:

- `larkspur_clockwork_fair q009`: the compile had role/ruling fragments, but
  the first QA plan still treated name plus role as enough identity support.

The query harness now has a structural companion for named official identity
lookups. When a successful query asks `person_role(Constant, Role)`, the
runtime also tries admitted authority/action companions for the same person,
such as `ruling_by/3`, `permission_granted/2`, `official_action/3`, and
`event_affects_person/3`. This is query-only expansion over admitted KB rows;
it does not reread source prose or infer answers in Python.

Targeted and full-slice movement:

```text
q009 official companion query: exact
larkspur companion first-10:   9 exact / 0 partial / 1 miss
candidate scorecard:           47 exact / 2 partial / 1 miss
candidate gate:                reject_candidate
```

The candidate is rejected because `larkspur_clockwork_fair q010` regresses from
exact to miss and the guarded compile is still high-risk. Adding the official
companion replay as a compile/query variant raises the judged artifact overlay
target:

```text
baseline scoped-evidence recipe: 46 exact / 4 partial / 0 miss
variant overlay target:          50 exact / 0 partial / 0 miss
accepted variant rows: 4
protected baseline-exact rows: 3
unchanged non-exacts: 0
```

Discovery: the instrument is now seeing complementary compiler views at the row
level. The product problem is not "run the best compile"; it is "identify which
compile/query view is safe for this question while protecting exact rows." The
next harness step is a non-oracle row-variant selector/risk gate that can learn
from the four accepted rows and three protected exact rows without judge labels
or source-prose access.

That bridge now exists as `scripts/plan_incoming_variant_selector_training.py`.
It reads the compile-variant overlay artifact only and emits selector/risk-gate
training rows:

```text
training rows: 7
activation targets: 4
exact-protection targets: 3
repair targets: 0
recommendation: train_row_variant_selector_with_exact_protection
```

Variant risk buckets:

| Variant | Accepted | Protected Regressions | Risk |
| --- | ---: | ---: | --- |
| `larkspur_attribute_duty_companion` | 2 | 1 | `unsafe_global_variant_row_gate_required` |
| `shifted_compile_variants` | 2 | 2 | `unsafe_global_variant_row_gate_required` |

Discovery: neither nonbaseline variant is safe as a global default. Both are
useful row-level lenses and both damage exact rows elsewhere. This gives the
next selector pass a compact calibration set rather than another broad prompt
change.

The first selector replay over those seven rows exposed a specific structural
failure. Plain structural selection reached only `2/7` best choices, and
guarded activation reached `3/7`; Meridian stayed wrong because structural
confidence was inflated by relaxed fallback volume and broad row-count volume.

The guarded selector now treats those row-volume shapes as uncertainty triggers:

```text
variant calibration rows: 7
guarded activation + volume gate: 6 exact / 1 partial / 0 miss
selected best available mode: 6/7
selector errors: 0
```

Per fixture:

| Fixture | Result | Remaining Note |
| --- | ---: | --- |
| `larkspur_clockwork_fair` | `3 / 0 / 0` | q007 and q010 now route through LLM; q009 stays structural. |
| `meridian_permit_board` | `2 / 0 / 0` | relaxed/broad volume trap sends both rows to activation. |
| `northbridge_authority_packet` | `1 / 1 / 0` | q004 exact is protected; q007 still needs better requirement-detail relevance. |

Discovery: the selector can now approximate most of the judged overlay without
oracle labels, but the remaining problem is not volume. It is answer-bearing
detail relevance: "12 new hydrants" is true but partial when the question asks
what the agreement requires regarding hydrants and the variant has spacing
support.

The activation selector now has a requirement-detail completeness guardrail:
for requirement questions, count-only or status-only rows are often partial when
another mode returns answer-bearing details such as spacing, interval,
threshold, scope, exception, condition, duration, unit, or authority.

Replay result:

```text
variant calibration rows: 7
guarded activation + volume gate + requirement detail: 7 exact / 0 partial / 0 miss
selected best available mode: 7/7
selector errors: 0
```

Discovery: the judged `50 / 0 / 0` overlay target now has a non-oracle selector
calibration proof on the seven rows that matter. This is still a calibration
slice, not a global promotion claim, but the selector now has named guardrails
for both row-volume traps and requirement-detail incompleteness.

The same selector was replayed over the full first-10 variant groups for the
three imperfect fixtures:

```text
larkspur:    10 exact / 0 partial / 0 miss, 10/10 best choices
meridian:    10 exact / 0 partial / 0 miss, 10/10 best choices
northbridge: 10 exact / 0 partial / 0 miss, 10/10 best choices
combined:    30 exact / 0 partial / 0 miss, 30/30 best choices
selector errors: 0
```

Together with Copperfall and Harrowgate's clean first-10 baseline rows, the
current best row-gated incoming surface is `50 exact / 0 partial / 0 miss`.
This is the harness behaving as an instrument: one compile did not become
perfect, but the row-gated selector chose the safe semantic view for each row.

Transfer replay against older rule-activation packs keeps the claim bounded:

```text
avalon requirement-detail guarded replay: 28 exact / 10 partial / 2 miss, 35/40 best choices
sable requirement-detail guarded replay:  25 exact / 6 partial / 9 miss, 37/40 best choices
```

Avalon improves slightly over the previous guarded activation replay by moving
one miss to partial, but it still does not beat the protected policy for miss
control. Sable is unchanged from the earlier guarded activation totals and
still prefers direct selection. The requirement-detail guard therefore remains
a useful named selector guardrail for row-level activation, not a global selector
default.

Ignored local artifact references:

- `tmp/incoming_smoke_summaries_larkspur_attribute_duty_variant/scorecard.md`
- `tmp/incoming_smoke_summaries_larkspur_attribute_duty_variant/scoped_evidence_comparison.md`
- `tmp/incoming_smoke_summaries_larkspur_attribute_duty_variant/compile_variant_overlay_plan.md`
- `tmp/incoming_smoke_summaries_official_companion_overlay/scorecard.md`
- `tmp/incoming_smoke_summaries_official_companion_overlay/scoped_evidence_comparison.md`
- `tmp/incoming_smoke_summaries_official_companion_overlay/compile_variant_overlay_plan.md`
- `tmp/incoming_smoke_summaries_official_companion_overlay/variant_selector_training_plan.md`
- `tmp/incoming_variant_selector_runs/incoming-variant-volume-gate-v2.md`
- `tmp/incoming_variant_selector_runs/incoming-variant-requirement-detail-gate.md`
- `tmp/incoming_variant_selector_runs/incoming-variant-requirement-detail-first10.md`
- `tmp/selector_policy_comparisons/avalon_guarded_activation_requirement_transfer.md`
- `tmp/selector_policy_comparisons/sable_guarded_activation_requirement_transfer.md`

## 2026-05-04 Promoted Story-World Full-40 Replay

The five formerly incoming fixtures were replayed from their promoted
`datasets/story_worlds/` homes using the story-world cold-run planner. This was
not a first-10 selector overlay; it was a regular full-40 cold compile plus
evidence-bundle QA pass, followed by failure-surface classification on the
non-exact rows.

Classified scorecard:

```text
fixtures compiled: 5 / 5
qa rows: 200
exact / partial / miss: 154 / 20 / 26
write proposals: 0
failure surfaces: 39 compile_surface_gap, 7 hybrid_join_gap
repair targets: 46
```

Per fixture:

| Fixture | Full-40 Result | Classified Repair Surface |
| --- | ---: | --- |
| `copperfall_deadline_docket` | `38 / 1 / 1` | `1` compile gap, `1` join gap |
| `harrowgate_witness_file` | `38 / 1 / 1` | `2` compile gaps |
| `larkspur_clockwork_fair` | `20 / 7 / 13` | `20` compile gaps |
| `meridian_permit_board` | `27 / 8 / 5` | `8` compile gaps, `5` join gaps |
| `northbridge_authority_packet` | `31 / 3 / 6` | `8` compile gaps, `1` join gap |

Discovery: the first-10 row-gated result was real but narrow. Full-40
generalization exposes a different frontier: mostly source-surface coverage,
especially Larkspur object state/custody/rationale/final-state rows, with a
smaller helper/query composition lane for Meridian spatial/coverage joins and
Northbridge affordability. Selector work is not the next answer for this batch;
scoped compile-surface acquisition is.

Ignored local artifact references:

- `tmp/story_world_runs/promoted_incoming_cold_run_plan.md`
- `tmp/story_world_full40_scorecards/scorecard.md`
- `tmp/story_world_full40_classified_scorecards/scorecard.md`
- `tmp/story_world_full40_classified_scorecards/compile_repair_targets.md`
- `tmp/story_world_failure_classification/*/*.json`

## 2026-05-04 Larkspur State/Custody Negative Diagnostic

The first full-40 Larkspur repair attempt used a source-entity ledger and a
broader state/custody/rationale domain hint. It improved compile shape but not
answer behavior:

```text
baseline full-40: 20 exact / 7 partial / 13 miss
ledger variant:   18 exact / 10 partial / 12 miss
recommendation:   reject_candidate
baseline exact regressions: 7
```

Discovery: a cleaner compile surface can still miss the answer-bearing rows.
The next Larkspur repair needs narrower source-surface passes for object-state
transitions, custody chain, permission/rationale, and final-state rows, plus
exact-row protection. A broad source-entity ledger is useful diagnostic context
but not a promotion path.

Artifact:

- `tmp/story_world_larkspur_state_custody_variant/larkspur_baseline_comparison.md`

## 2026-05-04 Larkspur Targeted-State Selector Lift

A narrower targeted-state compile variant is still unsafe globally, but it is a
useful row-level lens:

```text
larkspur baseline full-40:                   20 exact / 7 partial / 13 miss
targeted-state compile alone:                14 exact / 8 partial / 18 miss
judged row overlay target:                   23 exact / 6 partial / 11 miss
guarded selector + identity/rationale gates: 23 exact / 8 partial / 9 miss
selected best rows:                          39 / 40
selector errors:                             0
```

Accepted variant rows are q015, q024, q034, and q035. The selector originally
missed q009 because structural row volume preferred authority rows over the
baseline's explicit name/identity support. The new identity-completeness
uncertainty gate sends who-is rows to activation when a competing mode has
explicit name predicates. That fixed q009 without source prose, answer keys,
judge labels, or failure labels in selector input.

Rationale/contrast guidance then protected q029. The remaining missed-best row
is q023, where baseline partial should be protected over a targeted-state
seal/status explanation. This is now the next selector guardrail frontier for
capability-failure rationale rows.

Artifacts:

- `tmp/story_world_larkspur_targeted_state_variant/compile_variant_overlay_plan.md`
- `tmp/story_world_larkspur_targeted_state_variant/guarded_activation_selector_capability_gate_full40.md`
- `tmp/story_world_larkspur_targeted_state_variant/variant_selector_training_plan.md`

## 2026-05-04 Zip Fixture Promotion Batch

Five zip-delivered fixtures were extracted, normalized, promoted into
`datasets/story_worlds`, and removed from active `tmp/incoming`. The raw zips
and temporary extraction/staging folders are archived at
`C:\prethinker_tmp_archive\incoming_zip_batch_20260504_171258`.

Promoted fixtures:

| Fixture | Rows | First QA | Classified Repair Surface |
| --- | ---: | ---: | --- |
| `ashgrove_permit` | 25 | `19 / 2 / 4` | `2` compile gaps, `2` join gaps |
| `fenmore_seedbank` | 25 | `20 / 1 / 4` | `5` compile gaps |
| `greywell_pipeline` | 25 | `22 / 1 / 2` | `1` compile gap, `1` join gap, `1` answer gap |
| `heronvale_arts` | 25 | `18 / 4 / 3` | `5` compile gaps, `1` join gap |
| `veridia_intake` | 23 | `15 / 5 / 3` | `3` compile gaps, `4` join gaps, `1` answer gap |

Batch rollup:

```text
fixtures compiled: 5 / 5
qa rows: 123
first QA exact / partial / miss: 94 / 13 / 16
classified exact / partial / miss: 97 / 11 / 15
write proposals: 0
runtime load errors: 0
failure surfaces: 16 compile_surface_gap, 8 hybrid_join_gap, 2 answer_surface_gap
repair targets: 26
```

Discovery: the new batch confirms that cold generalization is still mainly a
source-surface acquisition problem, but it adds two useful frontier pressures.
Heronvale is the rule/eligibility fixture with medium semantic-progress risk,
and Veridia is a compact turnstream correction fixture for
stenographer-adjacent behavior. Treat the Ashgrove/Heronvale exact-count deltas
between first QA and classified reruns as verdict volatility, not a promoted
harness gain.

Durable per-fixture records now live in:

- `datasets/story_worlds/ashgrove_permit/progress_journal.md`
- `datasets/story_worlds/fenmore_seedbank/progress_journal.md`
- `datasets/story_worlds/greywell_pipeline/progress_journal.md`
- `datasets/story_worlds/heronvale_arts/progress_journal.md`
- `datasets/story_worlds/veridia_intake/progress_journal.md`

Ignored local artifact references:

- `tmp/story_world_runs/new_zip_fixtures_run_plan.md`
- `tmp/story_world_zip_baseline_summaries/scorecard.md`
- `tmp/story_world_zip_baseline_summaries/compile_repair_targets.md`
- `tmp/story_world_failure_classification_zip/*/*.json`

## 2026-05-05 Operational Record Status Lens Trial

The first honing pass after the zip batch added a named
`operational_record_status_strategy_v1` compiler context for permit lifecycles,
intake/facilities logs, conservation ledgers, grant/application dockets,
correction logs, and turnstream-style records. The lens is row-level useful but
not globally promotable.

Raw candidate scorecard:

```text
baseline:  97 exact / 11 partial / 15 miss
candidate: 96 exact / 20 partial / 7 miss
recommendation: reject_candidate
baseline-exact regressions: 15
```

Oracle row-gated artifact target:

```text
row-gated: 111 exact / 11 partial / 1 miss
delta vs baseline: +14 exact / 0 partial / -14 miss
accepted candidate rows: 19
rejected candidate rows: 17
unchanged non-exacts: 5
```

No-oracle selector results:

```text
structural selector:                 95 exact / 19 partial / 9 miss
guarded activation before op guard:  99 exact / 17 partial / 7 miss
guarded activation after op guard:  101 exact / 17 partial / 5 miss
baseline-readiness guard selector:  106 exact / 12 partial / 5 miss
```

Discovery: the lens reduces misses for status, correction, threshold,
operational-decision, and unresolved-item rows, with Greywell reaching its
per-row upper bound (`24 / 1 / 0`) under the selector. It also weakens
rationale, transfer/authorization, application-status, counterfactual
eligibility, and hold-vs-commit rows when applied globally. The promoted lesson
is therefore a selector uncertainty guard: if structural selection prefers the
baseline but a competing mode has specialized operational record-state evidence
and the question asks about status, timeliness, decisions, correction,
thresholds, remedies, unresolved items, or isolation, call activation instead
of trusting row volume.

Follow-up guard: a second selector-only replay added
`selector_baseline_readiness_guard`, protecting baseline when it has direct
application/status, rule, or hold-readiness support and the competing surface is
broad or relaxed-heavy. It moved the no-oracle selector from `101 / 17 / 5` to
`106 / 12 / 5` over the same frozen `123` rows, with selected-best rows moving
from `112/123` to `117/123`. This is a harness-control gain over frozen
artifacts, not a new compile.

Artifacts:

- `tmp/story_world_operational_record_variant_summaries/scorecard.md`
- `tmp/story_world_operational_record_variant_summaries/baseline_comparison.md`
- `tmp/story_world_operational_record_variant_summaries/row_gated_scorecard_plan.md`
- `tmp/story_world_operational_record_selector/guarded_activation_operational_guard_rollup.json`
- `tmp/story_world_operational_record_selector_v3/scorecard.md`

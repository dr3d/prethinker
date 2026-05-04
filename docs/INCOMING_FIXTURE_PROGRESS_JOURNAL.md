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

Ignored local artifact references:

- `tmp/incoming_smoke_summaries_larkspur_attribute_duty_variant/scorecard.md`
- `tmp/incoming_smoke_summaries_larkspur_attribute_duty_variant/scoped_evidence_comparison.md`
- `tmp/incoming_smoke_summaries_larkspur_attribute_duty_variant/compile_variant_overlay_plan.md`
- `tmp/incoming_smoke_summaries_official_companion_overlay/scorecard.md`
- `tmp/incoming_smoke_summaries_official_companion_overlay/scoped_evidence_comparison.md`
- `tmp/incoming_smoke_summaries_official_companion_overlay/compile_variant_overlay_plan.md`
- `tmp/incoming_smoke_summaries_official_companion_overlay/variant_selector_training_plan.md`
- `tmp/incoming_variant_selector_runs/incoming-variant-volume-gate-v2.md`

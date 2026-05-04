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

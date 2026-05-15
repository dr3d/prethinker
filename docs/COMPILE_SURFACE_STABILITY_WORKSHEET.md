# Compile Surface Stability Worksheet

Last updated: 2026-05-14

This is the active workbench for the helper-retirement phase after boundary
hunt and dataset transfer. The question is no longer "can a helper recover this
row?" It is whether the compiler emits durable, answer-bearing direct surfaces
without leaning on legacy native helper adapters or fixture-shaped prose
recognizers.

## Doctrine

- Source-record facts preserve source fidelity; they are not a substitute for
  queryable direct predicates when a source shape recurs.
- A helper can be retired only when the compile surface that replaced it is
  named at a reusable structural level.
- A trigger condition is part of the architecture. Generic helper bodies do not
  excuse fixture-shaped triggers.
- Candidate predicates without admitted facts are a compile mirage: the model
  named the right surface but the package did not acquire it.
- Ledger-only coverage is useful for audit and fallback, but it should stay
  visible as compile-surface debt.
- No invariant may mention fixture names, row IDs, local people, local
  organizations, question IDs, or answer strings.

## Surface Invariants

The first invariant audit tracks seven generic families visible in
source-record ledgers:

| Family | Surface pressure |
| --- | --- |
| `identity_role_surface` | People or organizations bound to roles such as recorder, operator, holder, claimant, or authority. |
| `source_addressability_surface` | Sections, titles, chronology, basis, and negative-inference coordinates. |
| `rule_policy_surface` | Rules, procedures, clauses, thresholds, requirements, and exceptions. |
| `object_device_surface` | Objects, devices, systems, vendor/model identifiers, and inventory ids. |
| `temporal_event_surface` | Events, raw/corrected timestamps, intervals, windows, deadlines, and transitions. |
| `measure_count_surface` | Counts, totals, limits, durations, ratios, formulas, and measurement values. |
| `custody_control_surface` | Custody, access, ownership, location, recall, return, and control state. |

The audit status vocabulary is deliberately pre-QA:

| Status | Meaning |
| --- | --- |
| `pass` | Every triggered group has direct admitted surface support. |
| `partial` | Some triggered groups have direct admitted support; others are still weak. |
| `candidate_only` | Candidate predicates mention the surface, but no direct facts were admitted. |
| `ledger_only` | Source-record facts preserve the surface, but no direct or candidate surface carries it. |
| `fail` | The source-record ledger triggers the family, but no direct, candidate, or ledger fallback group was recognized. |
| `not_applicable` | The source-record ledger did not trigger that invariant family. |

## CSS-001 - First Compile-Surface Invariant Audit

Date: 2026-05-14

Before:

The helper-residue audit showed a suspicious split: external transfer fixtures
often needed `0-3` helper rows, while internal fixtures could emit hundreds or
thousands of helper rows. That made helper volume look less like architecture
and more like legacy compatibility over-delivery. But "delete helpers" was not
yet a safe instruction because the audit could not say which answer-bearing
surfaces the compile had already acquired directly.

Prediction:

If modern compiles can replace legacy helper adapters, then source-record
ledgers should trigger generic surface families that also appear in admitted
non-source-record facts. If a run scores well through source-record fallback
while the direct surface is `candidate_only` or `ledger_only`, helper deletion
would be hiding compile debt rather than retiring architecture.

Intervention:

Added a pre-QA invariant audit that reads domain-bootstrap compile JSON,
separates deterministic `source_record_*` facts from admitted direct facts, and
checks whether generic surface families visible in the source ledger also
appear in the direct compile product.

Artifacts:

- `scripts/audit_compile_surface_invariants.py`
- `tests/test_compile_surface_invariants.py`
- `docs/data/compile_surface_stability/three_fixture_invariant_audit_20260514.json`
- `docs/data/compile_surface_stability/three_fixture_invariant_audit_20260514.md`

After:

The first audit covered three unlike internal probe fixtures across three
compile runs: the frozen instrument stamp, the direct-surface recompile, and
the source-fidelity recompile. Across `9` compiles and `63` invariant-family
checks, the status counts were:

```text
pass: 14
partial: 27
candidate_only: 12
ledger_only: 7
not_applicable: 3
fail: 0
```

The shape is more useful than a simple pass rate:

- The direct-surface recompile produced strong roster surfaces, but collapsed
  the sensor fixture to `0` direct facts: six invariant families became
  `candidate_only` and one became `ledger_only`.
- The source-fidelity recompile repaired the sensor fixture into partial/pass
  direct coverage, but collapsed the custody/control fixture to `0` direct
  facts and mostly `candidate_only`/`ledger_only` coverage.
- The frozen stamp remained the strongest direct-surface baseline for the
  custody/control fixture, with `114` direct facts and no candidate-only or
  ledger-only families.
- Source-record ledgers preserved the weak surfaces, which explains how QA can
  still survive, but the invariant audit shows where direct compile surfaces
  are not yet stable enough to replace helper adapters cleanly.

Verification:

```powershell
python -m py_compile scripts\audit_compile_surface_invariants.py
python -m pytest tests\test_compile_surface_invariants.py -q
```

Result:

```text
3 passed
```

Lesson:

Helper retirement needs a compile-surface readiness gate. The right target is
not "use fewer helpers"; it is "make the compile product emit the generic
surface the helper was bridging to." A run can look cleaner by delivering fewer
helper rows while becoming less directly queryable. The invariant audit catches
that failure mode before QA turns it into a vague score regression.

Next pressure:

Use the invariant audit as the first gate before no-helper QA. For each fixture
family, decide whether the weak state is acceptable source-record fallback,
candidate admission failure, or direct-surface acquisition debt. The next
architectural move should strengthen compile guidance for surfaces that are
already visible in the source ledger, especially source addressability,
identity/role binding, temporal/event state, and custody/control state.

## CSS-002 - Add Fixture-Free Compile Invariant Guidance

Date: 2026-05-14

Before:

CSS-001 could identify weak direct surfaces after a compile, but it did not
change the compiler's behavior. The risk was turning the audit into a report
that explains helper residue after the fact while future compiles continue to
emit candidate predicate names without enough admitted direct fact operations.

Prediction:

A small global compile-context nudge should be safer than adding another native
helper adapter. If the nudge is phrased as generic surface families rather than
local source names, it can push future compiles toward direct rows for the same
surfaces the audit measures.

Intervention:

Added `COMPILE_SURFACE_INVARIANT_CONTEXT_V1` to the source compiler guidance in
`scripts/run_domain_bootstrap_file.py`. The context is injected into both
whole-source Semantic IR compiles and focused `source_pass_ops_v1` compiles.
It asks the model to propose concrete operations for recurring answer-bearing
surfaces when compatible predicates exist:

- identity and role-bound relations;
- source addressability;
- rule/policy requirements and exceptions;
- object, device, system, model, and inventory identifiers;
- temporal anchors, corrections, intervals, windows, and transitions;
- counts, totals, thresholds, durations, ratios, units, and formula components;
- custody, possession, access, ownership, recall, return, and control state.

After:

The compiler now receives the same invariant vocabulary that the audit checks.
This does not admit new truth by itself; the mapper still validates predicate
contracts and source authority. It should reduce the specific bad state where
the profile proposes a useful predicate surface but no fact operations are
emitted for it.

Artifacts:

- `scripts/run_domain_bootstrap_file.py`
- `tests/test_domain_bootstrap_file.py`

Verification:

```powershell
python -m py_compile scripts\run_domain_bootstrap_file.py scripts\audit_compile_surface_invariants.py
python -m pytest tests\test_domain_bootstrap_file.py tests\test_compile_surface_invariants.py -q
```

Result:

```text
30 passed
```

Lesson:

The right replacement for helper bridges is not another bridge. It is a shared
compile-surface contract that says which source-ledger surfaces deserve direct
rows when the profile can express them. That moves the architecture one layer
up: helper pressure becomes compile guidance plus post-compile invariant audit.

Next pressure:

Run a small recompile on the three helper-residue probes with the invariant
context active, then compare the new invariant audit against CSS-001. A useful
gain is fewer `candidate_only`/`ledger_only` families without adding fixture
vocabulary, not merely a higher direct fact count.

## CSS-003 - Invariant-Guided Three-Probe Recompile

Date: 2026-05-14

Before:

CSS-001 showed that the older direct-surface recompile could look clean while
collapsing an entire probe to `0` direct facts. CSS-002 added generic compile
guidance, but it had not yet been tested against the same helper-residue
probes.

Prediction:

If the invariant guidance is useful, it should reduce `candidate_only` and
`ledger_only` families without increasing fixture-specific prompt surface. It
does not need to beat the frozen stamp in one draw, but it should avoid the
worst "candidate names with no admitted facts" failure mode.

Intervention:

Recompiled the same three helper-residue probes through OpenRouter at three
lanes, with source-record facts enabled and the new invariant guidance active.
Then reran the invariant audit against the new compile artifacts.

Artifacts:

- `docs/data/compile_surface_stability/invariant_guided_recompile_audit_20260514.json`
- `docs/data/compile_surface_stability/invariant_guided_recompile_audit_20260514.md`

After:

The invariant-guided run produced:

```text
compiles: 3
pass: 3
partial: 13
candidate_only: 2
ledger_only: 2
not_applicable: 1
fail: 0
```

Fixture-level summary:

```text
count/roster: direct facts 297, pass 2, partial 4, candidate_only 0, ledger_only 0
sensor/correction: direct facts 38, pass 1, partial 5, candidate_only 0, ledger_only 1
custody/control: direct facts 12, pass 0, partial 4, candidate_only 2, ledger_only 1
```

Compared with the older direct-surface recompile, the bad surface debt dropped
from `7` candidate-only and `4` ledger-only families to `2` and `2`. The sensor
probe no longer collapsed to zero direct facts. The custody/control probe is
still weak: it moved from broad ledger/candidate debt into a small direct
surface, but it remains below the frozen stamp and is not ready for helper-free
confidence.

Verification:

```powershell
python scripts\run_domain_bootstrap_file_batch.py --dataset-root datasets\story_worlds --out-root tmp\compile_surface_invariant_recompile_20260514 --fixture count_composition_roster --fixture industrial_sensor_clock_correction --fixture probate_storage_access_register --lanes 3 --timeout 900 --compile-source --source-entity-ledger --archival-identifier-ledger --source-record-ledger --source-record-ledger-facts --review-profile --profile-review-retry
python scripts\audit_compile_surface_invariants.py --compile-json tmp\compile_surface_invariant_recompile_20260514\count_composition_roster --compile-json tmp\compile_surface_invariant_recompile_20260514\industrial_sensor_clock_correction --compile-json tmp\compile_surface_invariant_recompile_20260514\probate_storage_access_register --out-json docs\data\compile_surface_stability\invariant_guided_recompile_audit_20260514.json --out-md docs\data\compile_surface_stability\invariant_guided_recompile_audit_20260514.md
```

Lesson:

The invariant guidance helped, but the architecture has not "solved helpers" by
prompt text. The result is exactly the useful middle state: fewer mirage
surfaces, better direct sensor acquisition, and a clearly named remaining
custody/control compile-surface gap. This keeps helper retirement empirical
instead of ideological.

Next pressure:

Do not run a broad no-helper internal QA yet. First isolate the custody/control
compile gap: source addressability, object/item id admission, temporal event
rows, and custody/possession/recall surfaces are still weak. The next repair
should target admission of those generic surfaces, not a helper resurrection.

## CSS-004 - Focused-Pass Repair For Custody/Control Surface

Date: 2026-05-14

Before:

The invariant-guided three-probe recompile improved the broad helper-residue
picture, but the custody/control probe still had only `12` direct facts and
carried `2` candidate-only plus `1` ledger-only invariant families. The model
had proposed useful profile predicates, but the broad compile did not emit
enough admitted operations for item identity, custody, access, chronology, and
temporal state.

Prediction:

If the weakness is pass coverage rather than missing architecture, then a
focused flat-plus-plan compile should acquire the missing direct surfaces
without adding native helper adapters or local vocabulary rules.

Intervention:

Reran the custody/control probe using the existing flat skeleton plus focused
`source_pass_ops_v1` machinery, with the compile invariant guidance active.
This did not add a helper. It changed the compile route from one broad pass to
an operations-only focused-pass union.

Artifacts:

- `docs/data/compile_surface_stability/focused_probate_invariant_audit_20260514.json`
- `docs/data/compile_surface_stability/focused_probate_invariant_audit_20260514.md`

After:

The focused-pass compile admitted `233` operations and produced `162` direct
non-source-record facts. The invariant audit moved the custody/control probe
to:

```text
pass: 5
partial: 2
candidate_only: 0
ledger_only: 0
fail: 0
```

Remaining weak families:

```text
source_addressability_surface: partial, missing chronology_coordinate
measure_count_surface: partial, missing measurement_value
```

Verification:

```powershell
python scripts\run_domain_bootstrap_file.py --text-file datasets\story_worlds\probate_storage_access_register\source.md --out-dir tmp\compile_surface_invariant_focused_probate_20260514\probate_storage_access_register --timeout 900 --max-tokens 12000 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --max-plan-passes 8 --focused-pass-operation-target 64 --focused-retry-operation-target 32 --source-entity-ledger --archival-identifier-ledger --source-record-ledger --source-record-ledger-facts --review-profile --profile-review-retry
python scripts\audit_compile_surface_invariants.py --compile-json tmp\compile_surface_invariant_focused_probate_20260514\probate_storage_access_register --out-json docs\data\compile_surface_stability\focused_probate_invariant_audit_20260514.json --out-md docs\data\compile_surface_stability\focused_probate_invariant_audit_20260514.md
```

Lesson:

This is the first strong helper-retirement shape in the new lane. The repair
was not "add a custody helper"; it was "use the focused compile substrate so
the direct item/custody/access/title/order surfaces actually enter the package."
The architecture moves upward: helper pressure becomes a compile-routing and
surface-admission question.

Next pressure:

Run QA on the focused custody/control compile with helpers quarantined or
strictly budgeted. If QA holds, the helper-retirement path is: invariant audit
first, focused compile route second, helper deletion third.

## CSS-005 - Focused Custody/Control No-Helper QA

Date: 2026-05-14

Before:

CSS-004 proved that the focused-pass route could acquire direct
custody/control surfaces: `5` invariant families passed, `2` were partial, and
there were no `candidate_only` or `ledger_only` families. The open question was
whether that direct-surface health was enough to replace helper delivery in QA.

Prediction:

If direct surface acquisition is sufficient, no-helper QA should approach the
older frozen no-helper baseline for this probe (`33/0/6` over `40`) while using
zero helper rows. If it falls materially below that, the invariant audit is
necessary but not sufficient: query planning or predicate-palette stability is
still weak.

Intervention:

Ran the focused custody/control compile against the full `40`-question QA file
with helper companions suppressed and legacy native helper adapters left off.
The answer key was supplied from `oracle.jsonl`; a first run without the oracle
was discarded as judge plumbing, not science.

Artifacts:

- `docs/data/compile_surface_stability/focused_probate_no_helper_qa_20260514.json`
- `docs/data/compile_surface_stability/focused_probate_no_helper_qa_20260514.md`

After:

```text
exact: 26
partial: 4
miss: 10
helper rows: 0
runtime load errors: 0
write proposal rows: 0
failure surfaces: compile_surface_gap 9, query_surface_gap 3, hybrid_join_gap 2
```

This is worse than the older frozen no-helper baseline despite a healthier
invariant audit. The focused compile emitted many useful direct facts, but the
profile/predicate palette shifted: some QA queries looked for older or sibling
predicate surfaces, and several source-specific details remained only in source
records or coarse labels.

Verification:

```powershell
python scripts\run_domain_bootstrap_qa.py --run-json tmp\compile_surface_invariant_focused_probate_20260514\probate_storage_access_register\domain_bootstrap_file_20260515T023857493498Z_source_qwen-qwen3-6-35b-a3b.json --qa-file datasets\story_worlds\probate_storage_access_register\qa.md --oracle-jsonl datasets\story_worlds\probate_storage_access_register\oracle.jsonl --out-dir tmp\compile_surface_invariant_focused_probate_qa_limit0_oracle_20260514\probate_storage_access_register --timeout 900 --max-tokens 6000 --helper-companion-row-limit 0 --judge-reference-answers --classify-failure-surfaces --no-cache
```

Lesson:

Invariant health is a readiness gate, not an answer guarantee. The next layer is
predicate-palette stability: a compile can contain the right kind of information
while naming it on a surface the query planner does not reliably choose. Helper
retirement therefore has three gates, not two:

1. direct-surface invariant audit;
2. stable predicate palette / query surface alignment;
3. no-helper QA replay.

Next pressure:

Build a predicate-palette drift audit for the focused compile versus the frozen
no-helper baseline. It should name reusable surface aliases such as item id,
external id, physical custodian, title status, access authorization, source
authority, order date/effect, assertion status, and chronology event without
encoding local row vocabulary. The repair target is stable surface alignment,
not returning to native helpers.

## CSS-006 - Predicate-Palette Drift Audit

Date: 2026-05-14

Before:

CSS-005 showed the awkward result: invariant health improved, helper rows were
zero, but QA fell to `26/4/10`. The non-exact rows were not simply "missing
helpers." Many queries targeted a surface name from one compile while the
focused compile had emitted a sibling surface name or a decomposed row family.

Prediction:

If predicate-palette drift is the real blocker, comparing the focused compile
with the older frozen no-helper baseline should show semantic-equivalent
surface families under different predicate names or packing choices.

Intervention:

Compared direct non-source-record predicate counts from the frozen baseline and
the focused invariant-guided compile, then grouped the drift into reusable
surface families rather than local row language.

Artifacts:

- `docs/data/compile_surface_stability/focused_probate_predicate_palette_drift_20260514.json`
- `docs/data/compile_surface_stability/focused_probate_predicate_palette_drift_20260514.md`

After:

The drift audit named seven surface families:

| Surface | Frozen palette | Focused palette |
| --- | --- | --- |
| `item_identifier` | `item_id/2` | `asset_id/1 + asset_description/2` |
| `external_identifier` | `external_id/2` | `external_reference/2` |
| `title_or_contestation_status` | `title_status/2` | `title_contested_by/2` |
| `access_authorization` | `access_authorized/4` | `authorized_party/3 + access_authority_source/2` |
| `court_order` | `court_order/3` | `order_id/1 + order_date/2 + order_effect/2` |
| `chronology_event` | `chronological_event/3` | `event_occurred_before/2 + event_occurred_after/2` |
| `source_claim_or_assertion` | `source_claim/3 + dispute_claim/3 + dispute_objection/3` | `assertion_recorded/3 + assertion_made_by/2 + dispute_*` |

This explains the QA mismatch. The focused compile is not empty; it is speaking
a different predicate dialect. Some focused surfaces are arguably better
normalized, but the query planner is not yet dialect-stable.

Lesson:

The next architecture layer is not more helper compression. It is stable
surface contracts. A profile may decompose a packed row, but it must preserve a
query-plannable equivalence class: item identifier, external identifier, title
status, access authorization, court order, chronology event, and source
assertion should be recognizable across palette variants.

Next pressure:

Add a small predicate-surface alias inventory or query planner normalization
step for these generic families. It should let QA search equivalent surfaces
without forcing compiles back to one frozen predicate vocabulary and without
adding native helper adapters.

## CSS-007 - Surface Alias Inventory Is Not Enough

Date: 2026-05-14

Before:

CSS-006 showed that the focused compile had a different predicate dialect from
the frozen no-helper baseline. The immediate low-risk repair was to expose a
compact alias inventory to the query planner: item identifier, external
identifier, access authorization, court order/effect, chronology event, source
assertion, and related surface families already present in the compiled KB.

Prediction:

If predicate-palette drift was the dominant blocker, the no-helper QA replay
should improve from `26/4/10` without adding helper rows, because the planner
could search sibling/decomposed predicates before falling back to source-record
text.

Intervention:

Added `surface_alias_inventory` to `compiled_kb_inventory` and exposed it in
QA context packs and evidence-bundle planning. The inventory is derived from
compiled predicate names only; it does not inspect fixture prose, row ids, or
answer strings. A unit test now checks the trigger surface for terse predicate
forms such as `item_id`, `asset_id`, `external_reference`, `authorized_party`,
`order_effect`, `event_occurred_before`, and `assertion_recorded`.

Artifacts:

- `scripts/run_domain_bootstrap_qa.py`
- `tests/test_domain_bootstrap_qa.py`
- `docs/data/compile_surface_stability/surface_alias_inventory_probate_qa_20260514.json`
- `docs/data/compile_surface_stability/surface_alias_inventory_probate_qa_20260514.md`

After:

The replay fell to `24/3/13` with `0` helper rows:

- exact=`24`
- partial=`3`
- miss=`13`
- failure surfaces: `query_surface_gap=5`, `compile_surface_gap=11`,
  `not_applicable=24`

The negative result was useful. Several misses queried the right general
neighborhood but returned only a source address or a broad relaxed row. The
planner could see surface families, but the answer-bearing value was often
still hidden in the bound query term or missing from the direct compile
surface.

Verification:

- `python -m py_compile scripts\run_domain_bootstrap_qa.py`
- `python -m pytest tests\test_domain_bootstrap_qa.py -q` -> `163 passed`
- `python -m pytest tests\test_domain_bootstrap_qa.py tests\test_domain_bootstrap_file.py tests\test_compile_surface_invariants.py -q` -> `193 passed`
- no-helper QA replay: exact=`24` partial=`3` miss=`13`, helper rows=`0`

Lesson:

An alias inventory is a map, not a bridge. It helps the planner recognize
palette variants, but it does not make bound constants visible as evidence and
does not create direct facts that the compiler failed to emit. The architecture
needs answer-bearing evidence visibility before more helper retirement can be
trusted.

Next pressure:

Expose successful bound query constants as evidence rows. This should repair
only the class where the model asks a valid query with a concrete answer atom
and the runtime returns a row id but hides the bound value from the answerer and
judge. It must not create helper rows or admit new facts.

## CSS-008 - Bound Query Constants As Evidence

Date: 2026-05-14

Before:

CSS-007 showed that a successful query like
`source_record_text_atom(X, court_berwick_county_probate_court)` could still
judge as a miss because the returned row exposed only `X=src_line_0004`; the
confirmed bound constant stayed inside the query string. That is not a compile
fact gap. It is evidence visibility debt.

Prediction:

Making bound query constants visible in successful query results should restore
answers whose support is a confirmed source-record atom or other concrete bound
argument. It should not repair true compile gaps, missing joins, or broad count
questions.

Intervention:

Added a generic result augmentation step in `run_query_plan`: when a query
succeeds, any non-variable bound arguments are added as `bound_query_constants`
metadata and as `BoundArgN` / `BoundArgNDisplay` fields on returned rows. This
does not change the KB, write facts, or add helper rows. It only makes already
confirmed query constants visible to downstream answer synthesis and judging.

Artifacts:

- `scripts/run_domain_bootstrap_qa.py`
- `tests/test_domain_bootstrap_qa.py`
- `docs/data/compile_surface_stability/bound_query_constants_probate_qa_20260514.json`
- `docs/data/compile_surface_stability/bound_query_constants_probate_qa_20260514.md`

After:

The replay returned to the earlier focused no-helper baseline:

- exact=`26`
- partial=`4`
- miss=`10`
- helper rows=`0`
- failure surfaces: `compile_surface_gap=9`, `query_surface_gap=3`,
  `hybrid_join_gap=1`, `judge_uncertain=1`, `not_applicable=26`

Concrete movement versus CSS-007 included source-text constant cases becoming
exact, such as jurisdiction/court and death-date answers. The result did not
exceed the CSS-005 baseline; new stochastic losses appeared elsewhere, which
means the intervention repaired one visibility class but did not solve the
remaining no-helper ceiling.

Verification:

- `python -m py_compile scripts\run_domain_bootstrap_qa.py`
- `python -m pytest tests\test_domain_bootstrap_qa.py -q` -> `164 passed`
- `python -m pytest tests\test_domain_bootstrap_qa.py tests\test_domain_bootstrap_file.py tests\test_compile_surface_invariants.py -q` -> `194 passed`
- no-helper QA replay: exact=`26` partial=`4` miss=`10`, helper rows=`0`

Lesson:

Zero-helper QA can recover source-record constant answers when the runtime
exposes the evidence it already proved. But the remaining misses are mostly
compile-surface coverage and query choice: registrar identity, motion numbers,
court-order/source authority, count filters, interval joins, and source
authority distinctions. More native helper rows are not the right repair.

Next pressure:

Split the remaining no-helper misses into two queues:

1. compile coverage: direct facts that the focused compile should emit if it
   sees recurring answer-bearing surfaces;
2. query choice: cases where the needed facts exist but the planner binds a
   placeholder, chooses a broad relaxed query, or stops before the answer slot.

Only the first queue should influence compile-surface invariant guidance. The
second should become query-planning tests, not helper adapters.

## CSS-009 - Strict Relaxed-Row Token Filtering

Date: 2026-05-14

Before:

CSS-008 split the remaining no-helper misses into compile coverage and query
choice. One recurring query-choice shape was over-bound constants: a query
with a concrete atom returned no rows, then the diagnostic relaxed query
returned an entire predicate table. That broad relaxed table helped debugging
but was too noisy for answer selection.

Prediction:

If the over-bound constant and the returned atom are lexical variants of the
same value, a strict token-subset filter can keep only the relevant relaxed
rows. This should help wording drift such as a requested organization/location
name versus a more specific stored location atom. It should not repair missing
facts or single-token placeholders.

Intervention:

Added a filter inside `_relaxed_constant_query`: when relaxed fallback succeeds,
rows are narrowed only if the requested constant's non-generic tokens are a
subset of the returned atom tokens, or the returned atom tokens are a subset of
the requested constant tokens. The filter requires at least two non-generic
tokens. It does not write facts, add helpers, or invent predicates.

Artifacts:

- `scripts/run_domain_bootstrap_qa.py`
- `tests/test_domain_bootstrap_qa.py`
- `docs/data/compile_surface_stability/token_subset_relaxed_probate_qa_20260514.json`
- `docs/data/compile_surface_stability/token_subset_relaxed_probate_qa_20260514.md`
- `docs/data/compile_surface_stability/bound_query_constants_remaining_gap_queue_20260514.md`

After:

The replay produced the best focused no-helper score in this series:

- exact=`28`
- partial=`1`
- miss=`11`
- helper rows=`0`
- failure surfaces: `compile_surface_gap=7`, `query_surface_gap=4`,
  `hybrid_join_gap=1`, `not_applicable=28`

The gain was not a universal score lift; some rows moved backward under
stochastic QA planning. But the net result improved, helper rows stayed at
zero, and compile-surface gaps dropped from `9` to `7`.

Verification:

- `python -m py_compile scripts\run_domain_bootstrap_qa.py`
- `python -m pytest tests\test_domain_bootstrap_qa.py -q` -> `165 passed`
- `python -m pytest tests\test_domain_bootstrap_qa.py tests\test_domain_bootstrap_file.py tests\test_compile_surface_invariants.py -q` -> `195 passed`
- no-helper QA replay: exact=`28` partial=`1` miss=`11`, helper rows=`0`

Guardrail:

A broader "distinctive overlap" variant was tried next: accept relaxed rows
when two or more distinctive tokens overlap, even when neither side is a
subset. That sounded generic, but the replay fell to `26/2/12`, so the
broadening was reverted. The architecture keeps the stricter subset repair.

Lesson:

Query repair can replace a sliver of helper behavior when it is phrased as a
general execution rule: over-bound constant -> relaxed query -> strict lexical
row narrowing. The remaining gap is no longer helper-volume evidence. It is
mostly compile coverage and planner slot choice.

Next pressure:

Use the remaining gap queue to choose the next bounded compile-side repair.
The strongest candidates are direct source-authority surfaces and section
addressability for answer-bearing records, because many misses ask for who/what
authorized, which source governs, or which section contains a record.

## CSS-010 - Strengthen Source Authority Compile Invariants

Date: 2026-05-14

Before:

CSS-009 left a focused no-helper score of `28/1/11`. The remaining gap queue
showed two recurring compile-side shapes:

- records, orders, claims, exhibits, and documents were not always directly
  linked to the section/source coordinate that contained them;
- authority/source rows were not always distinct from the party receiving
  permission or the item under control.

Prediction:

If future compiles preserve these two relations directly, no-helper QA should
need fewer source-record fallbacks for questions asking which section contains
a record, who/what authorized an action, what source governs access, or which
authority controls a finding.

Intervention:

Extended `COMPILE_SURFACE_INVARIANT_CONTEXT_V1` with two fixture-free rules:

- preserve the relation between a subject id and the section/source coordinate
  when a record/order/claim/exhibit/item/event/document is listed, filed,
  reproduced, referenced, or contained by a source layer;
- preserve the authority/source relation separately from the party receiving
  permission or the item being controlled.

Artifacts:

- `scripts/run_domain_bootstrap_file.py`
- `tests/test_domain_bootstrap_file.py`

After:

This is a compile-guidance change, not a replay result yet. It should be tested
by recompiling the focused custody/control probe and rerunning the strict
no-helper QA. The expected improvement is not generic score inflation; it is
movement on the source-authority and section-addressability rows in the
remaining gap queue.

Verification:

- `python -m py_compile scripts\run_domain_bootstrap_file.py`
- `python -m pytest tests\test_domain_bootstrap_file.py tests\test_compile_surface_invariants.py -q` -> `30 passed`
- `python -m pytest tests\test_domain_bootstrap_qa.py tests\test_domain_bootstrap_file.py tests\test_compile_surface_invariants.py -q` -> `195 passed`

Lesson:

Helper retirement now depends on compile contracts that preserve query-bearing
source relations, not only object/status/event facts. Section containment and
authority-source relations are architecture-level surfaces because they recur
across legal, policy, audit, catalog, and operational sources.

Next pressure:

Run one focused recompile on the custody/control probe with the strengthened
invariants active, then audit direct surfaces and rerun strict no-helper QA.
If authority/section rows move while helper rows stay at zero, the next phase
is to widen this compile-side invariant to unlike probes rather than restore
native helpers.

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

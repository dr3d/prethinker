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

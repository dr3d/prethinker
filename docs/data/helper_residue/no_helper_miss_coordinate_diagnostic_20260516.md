# No-Helper Miss Coordinate Diagnostic

Generated: 2026-05-16

Source run: `docs/data/helper_residue/default_retired_smoke_20260516.json`

Baseline:

- Questions: `24`
- Exact / partial / miss: `19 / 0 / 5`
- Helper rows: `0`

Decision:

- Do not restore helper companion delivery.
- Do not run the full native corpus again yet.
- Next layer: focused source-addressability and role/basis preservation probe.

| Coordinate | Existing surface | Diagnostic class | Recommended next layer |
| --- | --- | --- | --- |
| `industrial_sensor_clock_correction` q004 vendor/model | `hybrid_join_gap` | unsupported text membership; entity-labeled source text not planned | query planner or profile palette |
| `probate_storage_access_register` q005 registrar role | `compile_surface_gap` | direct role surface missing; wrong source row anchor | compile-surface invariant |
| `probate_storage_access_register` q006 chronology section | `compile_surface_gap` | section addressability missing; late section not indexed | source-section preservation invariant |
| `probate_storage_access_register` q007 possession basis section | `compile_surface_gap` | explanatory basis section missing; multi-source basis missing | source-basis provenance surface |
| `probate_storage_access_register` q008 item title/year | `hybrid_join_gap` | predicate semantics collision; row-bound field/numeric need | selective query planner guidance |

Summary:

- Compile-surface or source-preservation pressure: `3`
- Query-planner or profile-palette pressure: `2`
- Helper restoration pressure: `0`
- Broad join repair: rejected by HR-013

Lesson:

The no-helper failures are now clearer. The native smoke did not reveal a need
to bring helper companions back; it exposed source-addressability and planner
precision gaps. Three coordinates need better preservation of answer-bearing
source sections, role rows, or basis/corroboration surfaces. Two coordinates
need selective planning over already-preserved source text or same-row fields.
The next repair should therefore begin with unlike probes for addressable source
sections, role-bearing correspondence rows, basis/corroboration rows, and
entity-labeled source text. It should not encode the current fixture nouns or
promote a broad row-context join.

# Blocksworld Multi-Fact Upgrade (2026-04-17)

## Scope
- Improve split-extraction handling for single-utterance, multi-fact payloads.
- Keep strict-registry stability intact (`predicate_registry.blocksworld.json`, `--strict-registry`).
- Re-run identical strict pilot lanes (12 + 40) for before/after comparison.

## Code changes
- `kb_pipeline.py`
  - Updated extractor prompt guidance to allow emitting multiple independent facts in `assert_fact` turns.
  - Updated full-schema and repair prompt constraints to align with existing validator semantics for multi-fact/multi-rule payloads.
  - Enhanced `_refine_logic_only_payload(...)` for `assert_fact`:
    - expands `logic_string` into grounded fact clauses via `_expand_assert_fact_clauses(...)`
    - writes canonical multi-fact `logic_string` as newline-joined clauses.
  - Added `_apply_registry_fact_salvage_guard(...)`:
    - when strict registry is enabled, drops only out-of-registry facts from mixed batches
    - retains and commits registry-compatible subset
    - records an alignment event (`registry_fact_salvage_guard`) for traceability.
  - Added `_looks_blocksworld_state_description(...)` and classifier arbitration guard:
    - preserves `assert_fact` lane when model classifier drifts to `other/query` on Blocksworld-style state/goal prose.

- `tests/test_split_extraction_refine.py`
  - added/extended tests for:
    - multi-fact expansion in refine path
    - registry salvage behavior on mixed known/unknown fact batches.

## Validation
- `python -m py_compile kb_pipeline.py`
- `$env:PYTHONPATH='.'; python -m pytest -q tests/test_split_extraction_refine.py tests/test_language_profile_routing.py tests/test_progressive_gate_profiles.py`
- Result: `14 passed`

## Benchmark runs

### 12-case strict lane (same case IDs)
- Before: `tmp/blocksworld_lane_strict_2026-04-16.summary.json`
- After:  `tmp/blocksworld_lane_strict_mf2_2026-04-17.summary.json`

| Metric | Before | After |
|---|---:|---:|
| Pipeline pass | 12/12 | 12/12 |
| Avg init predicate hit | 0.4375 | 0.5139 |
| Avg goal predicate hit | 0.5000 | 0.5139 |
| Zero-hit cases | n/a | 0 |

### 40-case strict lane (same lane settings)
- Before: `tmp/blocksworld_lane_strict_full40_2026-04-16.summary.json`
- After:  `tmp/blocksworld_lane_strict_full40_mf3_2026-04-17.summary.json`

| Metric | Before | After |
|---|---:|---:|
| Pipeline pass | 40/40 | 40/40 |
| Avg init predicate hit | 0.3688 | 0.6271 |
| Avg goal predicate hit | 0.3250 | 0.5833 |
| Zero-hit cases | 4 | 0 |

## Interpretation
- Multi-fact refine is now materially better at capturing block state from single narrative utterances.
- Strict-registry regressions introduced by wider extraction were resolved by the salvage guard.
- Multi-fact extraction now scales with strict pass stability and no zero-hit residue in the 40-case lane.

## Artifacts
- 12-case report: `docs/reports/BLOCKSWORLD_LANE_STRICT_MF2_2026-04-17.md`
- 12-case report (final): `docs/reports/BLOCKSWORLD_LANE_STRICT_MF3_2026-04-17.md`
- 40-case report (final): `docs/reports/BLOCKSWORLD_LANE_STRICT_FULL40_MF3_2026-04-17.md`
- summary JSONs:
  - `tmp/blocksworld_lane_strict_mf2_2026-04-17.summary.json`
  - `tmp/blocksworld_lane_strict_full40_mf2_2026-04-17.summary.json`
  - `tmp/blocksworld_lane_strict_mf3_2026-04-17.summary.json`
  - `tmp/blocksworld_lane_strict_full40_mf3_2026-04-17.summary.json`

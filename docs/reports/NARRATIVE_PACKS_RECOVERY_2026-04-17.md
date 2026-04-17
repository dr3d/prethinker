# Narrative Strict Recovery Status

Date: 2026-04-17

This note records the current honest frontier for the strict narrative packs after the guardrail batch, long-story routing guard, and targeted general-registry expansion.

## What Changed

- strict Blocksworld stayed stable while additional gates were added
- temporal-question fallback was hardened
- cross-domain registry mistakes now fail fast in suite runners
- long-form story blobs are less likely to be misrouted as single giant rules
- the general predicate registry was expanded only with evidence-backed recurring narrative signatures

## Current Strict Narrative Status

These packs are improved, but still not fully green.

| Pack | Post-Registry Baseline | Current Recovery Best | Pipeline Pass | Best Split | Coverage | Precision | Exam | Temporal Exam |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| Mid | `0.3237` | `0.3812` | `1/3` | `line` | `0.850` | `0.920` | `0.950` | `1.000` |
| Upper-mid | `0.257644` | `0.3922` | `1/3` | `paragraph` | `0.920` | `0.950` | `0.950` | `1.000` |

## Interpretation

- The recovery is real.
- The narrative lanes are still not publishable as "green strict lanes".
- The upper-mid pack benefited the most from the route and registry cleanup.
- Full-mode story ingestion remains weak even when the pipeline technically passes; the strongest useful results are still coming from paragraph and line splits.

## Remaining Blockers

Mid pack still shows concentrated failures around:

- charter/lease predicate families such as `lease_valid/2`, `roof_reserve_transfer/1`, and `title_reverts_to_trust/2`
- residual event naming like `storm_event/1`

Upper-mid still shows concentrated failures around:

- covenant-role vocabulary such as `deputy_curator/1`
- board-meeting and status-summary paragraph compression
- unmapped status/reporting concepts in the final summary paragraph

## References

- `docs/reports/MID_PACK_GENERAL_STRICT_TEMPORAL_2026-04-17.md`
- `docs/reports/UPPER_MID_PACK_GENERAL_STRICT_TEMPORAL_2026-04-17.md`
- `docs/reports/MID_PACK_GENERAL_STRICT_TEMPORAL_RECOVERY2_2026-04-17.md`
- `docs/reports/UPPER_MID_PACK_GENERAL_STRICT_TEMPORAL_RECOVERY3_2026-04-17.md`
- `docs/reports/NARRATIVE_PACKS_POST_REGISTRY_2026-04-17.md`

# Narrative Strict Recovery Status

Date: 2026-04-17

This note records the current honest frontier for the strict narrative packs after the guardrail batch, long-story routing guard, targeted general-registry expansion, and exam-query hardening.

## What Changed

- strict Blocksworld stayed stable while additional gates were added
- temporal-question fallback was hardened
- malformed rule-shaped exam queries and bad boolean row checks are now dropped or repaired before evaluation
- cross-domain registry mistakes now fail fast in suite runners
- long-form story blobs are less likely to be misrouted as single giant rules
- the general predicate registry was expanded only with evidence-backed recurring narrative signatures

## Current Strict Narrative Status

These packs are improved, but still not fully green.

| Pack | Post-Registry Baseline | Latest Rerun Best | Historical Best | Pipeline Pass | Best Split | Coverage | Precision | Exam | Temporal Exam |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| Mid | `0.3237` | `0.3590` | `0.3812` | `1/3` | `paragraph` | `0.850` | `0.920` | `0.800` | `0.667` |
| Upper-mid | `0.257644` | `0.967` | `0.967` | `1/3` | `full` | `0.850` | `1.000` | `1.000` | `1.000` |

## Interpretation

- The recovery is real.
- The narrative lanes are still not publishable as "green strict lanes".
- The upper-mid pack benefited the most from the route, registry, and evaluation cleanup: it now has a strong strict full-mode breakout.
- Upper-mid is still not a fully promoted strict pack because paragraph and line each retain one governance-rule reject.
- Mid recovered from a noisy bad-exam rerun, but it still has a narrower parser/ontology tail that keeps the pack at `1/3`.

## Remaining Blockers

Mid pack still shows concentrated failures around:

- one remaining charter rule body predicate: `annual_operating_surplus/1`
- one dense micro-grant paragraph whose current parser output still invents a whole family of out-of-registry predicates:
  - `accepted_grant/4`
  - `required_classes/5`
  - `required_duration/3`
  - `required_proof/2`
  - `teaching/4`
  - `teaching_topic/4`
  - `kept_attendance_sheets/3`
  - `not_open_to_only_paying_members/1`

Upper-mid still shows concentrated failures around:

- one governance paragraph whose current parser output still drifts on:
  - `revenue_transfer/2`
  - `occupied/2`
  - `dependent_child/1`
- the pack is now closer to promotion, but it is not there yet because paragraph and line still reject on that paragraph

## References

- `docs/reports/MID_PACK_GENERAL_STRICT_TEMPORAL_RECOVERY4_2026-04-17.md`
- `docs/reports/UPPER_MID_PACK_GENERAL_STRICT_TEMPORAL_RECOVERY5_2026-04-17.md`
- `docs/reports/NARRATIVE_PACKS_POST_REGISTRY_2026-04-17.md`

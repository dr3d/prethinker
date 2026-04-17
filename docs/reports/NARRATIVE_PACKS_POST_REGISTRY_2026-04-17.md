# Narrative Packs Post-Registry Verification

Date: 2026-04-17

This note records the live Ollama rerun after `modelfiles/predicate_registry.json` was populated and strict general-lane admission became real.

## Blocksworld Sanity Check

Strict Blocksworld remained stable in the post-registry verification run:

- symbolic harness solve/replay: `20/20`
- prethinker pilot pass: `8/8`
- avg init predicate hit: `0.458334`
- avg goal predicate hit: `0.458334`
- zero-hit cases: `0`

Reference:
- `docs/reports/BLOCKSWORLD_LANE_POST_REGISTRY_2026-04-17.md`

## Honest Strict Narrative Reruns

Both packs were rerun on live Ollama with:

- `--predicate-registry modelfiles/predicate_registry.json`
- `--strict-registry`
- `--modes full,paragraph,line`
- `--temporal on`

Results:

- mid pack
  - previous provisional best: `0.6452`
  - post-registry best: `0.3237`
  - pipeline pass: `1/3`
  - avg coverage: `0.446667`
  - avg precision: `0.9`
  - avg exam pass: `0.4`
  - avg temporal exam pass: `0.666667`
- upper-mid pack
  - previous provisional best: `0.8718`
  - post-registry best: `0.257644`
  - pipeline pass: `1/3`
  - avg coverage: `0.28`
  - avg precision: `0.9`
  - avg exam pass: `0.533333`
  - avg temporal exam pass: `0.666667`

Updated pack reports:

- `docs/reports/MID_PACK_GENERAL_STRICT_TEMPORAL_2026-04-17.md`
- `docs/reports/UPPER_MID_PACK_GENERAL_STRICT_TEMPORAL_2026-04-17.md`

Raw summaries:

- `tmp/mid_pack_general_strict_temporal_post_registry_20260417.summary.json`
- `tmp/upper_mid_pack_general_strict_temporal_post_registry_20260417.summary.json`

## Interpretation

The previous `0.6452` / `0.8718` pack scores were not honest strict-lane numbers because the general registry was effectively empty at the time. After registry population, strict admission rejects much more of the narrative extraction surface, and the corrected baseline is materially lower.

Observed pattern:

- `paragraph` and `line` packaging preserved more semantic content, but both failed pipeline because many turns now hit validation/registry rejection.
- `full` packaging still passed pipeline, but semantic quality collapsed into very sparse KBs and low final scores.

This is the right kind of bad news: it exposes the actual gap to close next rather than hiding it behind a non-binding strict mode.

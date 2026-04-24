# Medical UMLS Bridge Runtime Checkpoint

Date: 2026-04-24

This checkpoint records the move from a batch-side `medical@v0` asset bundle to a live MCP/gateway profile with deterministic UMLS bridge admission checks.

## What Changed

- `medical@v0` now names the bounded local UMLS slice and bridge facts in its profile manifest.
- The canonical MCP server loads profile assets when `active_profile=medical@v0`.
- The compiler guide includes UMLS bridge hints for concept normalization and type steering.
- The active profile parse guard can clear unsafe logic when bridge groups conflict with the predicate argument shape.
- The gateway config can select `medical@v0` and render medical write replies more legibly.
- A deterministic bridge admission preflight now runs before model-backed medical suites.

## Bridge Role

The bridge is deliberately narrow.

It supports:

- alias normalization
- semantic group steering
- clarification pressure for vague shorthand
- predicate/type compatibility checks

It does not promote UMLS concepts into new predicates and does not claim broad clinical reasoning.

## Fast Verification

Latest local verification before long-running model work:

- `python scripts/run_umls_bridge_admission_probe.py`
  - `9/9` pass
- `python -m pytest -q`
  - `206 passed`

The bridge admission report is generated locally under `tmp/licensed/umls/2025AB/prethinker_mvp/bridge_admission_latest/` and should stay out of the public repo with other licensed or run-derived artifacts.

## Next Long-Run Order

1. Run the deterministic bridge admission preflight.
2. Run `python scripts/run_medical_profile_suite.py --model qwen3.5:9b`.
3. Use `qwen3.5:27b` for offline ontology review only after the profile suite is stable.
4. Promote any findings through batteries, docs, and tests before changing runtime behavior.

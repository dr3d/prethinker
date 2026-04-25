# Agent README

This is the short handoff for coding agents working in Prethinker.

## First Read

1. [PROJECT_STATE.md](PROJECT_STATE.md)
2. [README.md](README.md)
3. [docs/PRETHINK_GATEWAY_MVP.md](docs/PRETHINK_GATEWAY_MVP.md)
4. [docs/UMLS_MVP.md](docs/UMLS_MVP.md)
5. [docs/MEDICAL_PROFILE.md](docs/MEDICAL_PROFILE.md)
6. [docs/FREETHINKER_DESIGN.md](docs/FREETHINKER_DESIGN.md)
7. [ui_gateway/README.md](ui_gateway/README.md)

Treat older reports and prompt snapshots as Git history, not live guidance.

## Current Shape

- `src/mcp_server.py` owns the canonical `process_utterance()` runtime.
- `ui_gateway/` is the live manual cockpit for prompt-book demos, route telemetry, KB mutations, and clarification turns.
- `medical@v0` is the active bounded profile.
- `src/umls_mvp.py` and `scripts/build_umls_semantic_network_kb.py` contain the current UMLS bridge/Semantic Network work.
- `Freethinker` is a bounded optional clarification sidecar; it is not an authoritative truth layer.
- The Prolog KB receives committed facts/rules only after runtime gates accept them.

## Core Invariants

- Prefer deterministic validation over trusting model prose.
- Keep model proposals, clarification asks, committed mutations, and blocked mutations visible in the UI.
- Do not broaden the medical profile into general clinical advice.
- Do not commit licensed UMLS source archives or extracted full Metathesaurus tables.
- Keep local run data under ignored paths such as `tmp/`.
- Preserve user changes in a dirty worktree; never revert unrelated edits.

## Verification

Use focused tests while iterating, then run the full suite before a stopping-point commit:

```powershell
python -m pytest tests/test_medical_profile_runtime.py tests/test_ui_gateway_phases.py tests/test_ui_gateway_runtime_hooks.py -q
python -m pytest tests/test_umls_mvp.py tests/test_umls_semantic_network_builder.py -q
python -m pytest -q
```

The last known full-suite result before the docs cleanup was `214 passed`.

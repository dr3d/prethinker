# Agent README

This is the short handoff for coding agents working in Prethinker.

## First Read

1. [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md)
2. [README.md](https://github.com/dr3d/prethinker/blob/main/README.md)
3. [docs/PRETHINK_GATEWAY_MVP.md](https://github.com/dr3d/prethinker/blob/main/docs/PRETHINK_GATEWAY_MVP.md)
4. [docs/PUBLIC_DOCS_GUIDE.md](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_DOCS_GUIDE.md)
5. [docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md)
6. [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md)
7. [docs/DOMAIN_PROFILE_CATALOG.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PROFILE_CATALOG.md)
8. [docs/COURTLISTENER_DOMAIN.md](https://github.com/dr3d/prethinker/blob/main/docs/COURTLISTENER_DOMAIN.md)
9. [docs/SEC_CONTRACTS_DOMAIN.md](https://github.com/dr3d/prethinker/blob/main/docs/SEC_CONTRACTS_DOMAIN.md)
10. [docs/SEMANTIC_ROUTER_EXPERIMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_ROUTER_EXPERIMENT.md)
11. [docs/NO_LANGUAGE_HANDLING_IN_PYTHON_AUDIT.md](https://github.com/dr3d/prethinker/blob/main/docs/NO_LANGUAGE_HANDLING_IN_PYTHON_AUDIT.md)
12. [docs/UMLS_MVP.md](https://github.com/dr3d/prethinker/blob/main/docs/UMLS_MVP.md)
13. [docs/MEDICAL_PROFILE.md](https://github.com/dr3d/prethinker/blob/main/docs/MEDICAL_PROFILE.md)
14. [ui_gateway/README.md](https://github.com/dr3d/prethinker/blob/main/ui_gateway/README.md)

Treat older reports and prompt snapshots as Git history, not live guidance.

## Current Shape

- `src/mcp_server.py` owns the canonical `process_utterance()` runtime.
- `ui_gateway/` is the live manual cockpit for prompt-book demos, route telemetry, KB mutations, and clarification turns.
- `semantic_ir_v1` is the active research path for richer model semantics before deterministic admission; the console default is the LM Studio `qwen/qwen3.6-35b-a3b` lane.
- `src/semantic_ir.py` owns the mapper, projection policy, and admission diagnostics.
- Epistemic Worlds v1 preserves projection-blocked and supported-but-skipped candidates as scoped diagnostics, without admitting them as global truth.
- Long story-like console inputs may be split into focused Semantic IR segments by `ui_gateway/gateway/phases.py`; each segment still goes through canonical `process_utterance()`, then the gateway dedupes the visible mutation list.
- `medical@v0` is the active bounded ontology profile; `legal_courtlistener@v0` and `sec_contracts@v0` are live-data profile lanes for provenance/conflict and obligation/rule pressure.
- `active_profile=auto` uses `semantic_router_v1` to choose one profile per Semantic IR turn and load that profile's thick context/contracts. It is context selection only, not write authority.
- `scripts/run_mixed_domain_agility.py` is the current cross-domain pressure harness for shuffled Goldilocks/Glitch/Ledger/Silverton/Harbor/legal/SEC/medical streams.
- `medical@v0` Semantic IR calls include profile-owned predicate contracts and compact UMLS bridge context; the generic mapper should remain structural rather than accumulating medical type lists.
- `modelfiles/domain_profile_catalog.v0.json` is the thin skill-like roster. `profile.story_world.v0.json`, `profile.probate.v0.json`, `profile.legal_courtlistener.v0.json`, and `profile.sec_contracts.v0.json` are declarative thick-context packages for routing/profile experiments.
- `adapters/courtlistener/` is a conservative legal-source adapter. Keep live generated data under ignored `datasets/courtlistener/generated/`; do not commit raw API caches.
- `adapters/sec_edgar/` is a conservative SEC/contract adapter shell. Keep live generated data under ignored `datasets/sec_edgar/generated/`; do not commit raw API caches.
- `src/umls_mvp.py` and `scripts/build_umls_semantic_network_kb.py` contain the current UMLS bridge/Semantic Network work.
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
python -m pytest tests/test_semantic_ir_runtime.py tests/test_semantic_router.py tests/test_router_training_set.py -q
python -m pytest tests/test_courtlistener_adapter.py tests/test_domain_profiles.py -q
python -m pytest tests/test_sec_edgar_adapter.py tests/test_domain_profiles.py -q
python -m pytest -q
```

The latest full-suite result is `394 passed`. Recent focused batteries also cover CourtListener, SEC/contracts, domain profiles, Semantic IR runtime, UI gateway phases, trace rendering, router agility, router training data, Lava v5, UMLS builders, profile bootstrap, raw-file intake planning, post-ingestion QA, and profile-owned predicate aliases. Live/generated smoke traces belong under ignored paths such as `datasets/*/generated/` and `tmp/semantic_ir_trace_views/`.

# Agent README

This is the short handoff for coding agents working in Prethinker.

## First Read

1. [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md)
2. [README.md](https://github.com/dr3d/prethinker/blob/main/README.md)
3. [docs/PRETHINK_GATEWAY_MVP.md](https://github.com/dr3d/prethinker/blob/main/docs/PRETHINK_GATEWAY_MVP.md)
4. [docs/PUBLIC_DOCS_GUIDE.md](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_DOCS_GUIDE.md)
5. [docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md)
6. [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md)
7. [docs/GUARDRAIL_DEPENDENCY_AB.md](https://github.com/dr3d/prethinker/blob/main/docs/GUARDRAIL_DEPENDENCY_AB.md)
8. [docs/UMLS_MVP.md](https://github.com/dr3d/prethinker/blob/main/docs/UMLS_MVP.md)
9. [docs/MEDICAL_PROFILE.md](https://github.com/dr3d/prethinker/blob/main/docs/MEDICAL_PROFILE.md)
10. [docs/FREETHINKER_DESIGN.md](https://github.com/dr3d/prethinker/blob/main/docs/FREETHINKER_DESIGN.md)
11. [ui_gateway/README.md](https://github.com/dr3d/prethinker/blob/main/ui_gateway/README.md)

Treat older reports and prompt snapshots as Git history, not live guidance.

## Current Shape

- `src/mcp_server.py` owns the canonical `process_utterance()` runtime.
- `ui_gateway/` is the live manual cockpit for prompt-book demos, route telemetry, KB mutations, and clarification turns.
- `semantic_ir_v1` is the active research path for richer model semantics before deterministic admission; the console default is the LM Studio `qwen/qwen3.6-35b-a3b` lane.
- `src/semantic_ir.py` owns the mapper, projection policy, and admission diagnostics.
- Long story-like console inputs may be split into focused Semantic IR segments by `ui_gateway/gateway/phases.py`; each segment still goes through canonical `process_utterance()`, then the gateway dedupes the visible mutation list.
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
python -m pytest tests/test_semantic_ir_runtime.py tests/test_guardrail_dependency_ab.py -q
python -m pytest -q
```

The last known full-suite result was `281 passed`. The latest focused console/story-ingestion pass verified `55 passed` across semantic IR runtime, UI gateway phases, and gateway config.

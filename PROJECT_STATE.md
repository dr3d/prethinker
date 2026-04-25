# Project State

Last updated: 2026-04-25

## One-Sentence Shape

Prethinker is a governed natural-language-to-Prolog workbench: neural parsing proposes symbolic deltas, deterministic gates decide what can become durable KB state, and the UI shows that process live.

## Current Center

- Runtime: `src/mcp_server.py`, especially `process_utterance()`.
- UI: `ui_gateway/`, served locally by `python ui_gateway/main.py` using the stdlib `ThreadingHTTPServer`.
- Active profile: `medical@v0`.
- Active research asset: local UMLS Semantic Network KB built from `sn_current.tgz`.
- Active sidecar experiment: opt-in `semantic_ir_v1` compiler path using `qwen3.6:35b`.
- Current demonstration surface: prompt-book UI plus live ledger cards showing route, clarification, blocked execution, and KB mutation outcomes.

## What Works Now

- The medical profile normalizes a bounded predicate palette: medication use, conditions, symptoms, allergies, lab tests, lab result states, and pregnancy.
- Clarification turns can prevent unsafe patient or lab-test guesses.
- Clarified medical restatements can now recover useful KB writes, such as resolving vague pressure language into a high blood-pressure measurement.
- Session reset now clears pending clarification, recent runtime memory, trace state, and runtime KB state.
- The UI can demonstrate write routes, query/clarification routes, mutation telemetry, and prompt-book-driven examples.
- The UMLS Semantic Network builder produces local Prolog facts for semantic types, semantic relations, structural rows, and inherited relation closures.
- The opt-in semantic IR runtime path can route and commit safe direct assertions without running the legacy parse-side English rescue chain.

## Local UMLS Assets

Kept locally and ignored:

- `tmp/licensed/umls/2025AB/NET/`
- `tmp/licensed/umls/2025AB/semantic_network_kb/`
- `tmp/licensed/umls/2025AB/prethinker_mvp/`

Removed from the workspace cleanup because they are large and reproducible from external source storage:

- full UMLS zip archives
- extracted full Metathesaurus `META/`
- transient run directories, coverage HTML, caches, and trace logs

## Semantic Network KB

The current builder creates a fuller KB than the original nine medical profile predicates. The local Semantic Network output includes:

- 127 semantic types
- 54 semantic relations
- 597 structural relation rows
- 6,217 inherited UI relation facts
- 6,217 inherited name relation facts

This is the next useful layer for type steering and explanation. It should support demos like "why did this medication normalize this way?" or "what semantic family does this lab-test concept belong to?" without turning the app into a broad medical diagnosis system.

## Near-Term Frontiers

- Make the prompt-book examples meatier: each demo should show an utterance, the expected clarification or commit behavior, and the reason it is safer than a plain chatbot answer.
- Wire more Semantic Network explanations into the UI, especially type ancestry and relation paths.
- Keep improving reset/session hygiene so first utterances after reset cannot inherit stale entity context.
- Expand the medical profile only when the new predicate earns its place through tests and a clear demo.
- Measure guardrail dependency directly: compare old pipeline rescue-hook use against semantic IR direct coverage on Glitch, Ledger, medical ambiguity, and temporal packs.

## Verification Snapshot

Recent verified results:

- Full suite: `218 passed`
- Focused semantic IR/config/runtime hooks: `25 passed`
- Python compile check for touched runtime files passed

Rerun the full suite before committing a new stopping point.

## Reading Order

1. `README.md`
2. `AGENT-README.md`
3. `docs/PRETHINK_GATEWAY_MVP.md`
4. `docs/UMLS_MVP.md`
5. `docs/MEDICAL_PROFILE.md`
6. `docs/FREETHINKER_DESIGN.md`
7. `docs/CONSOLE_TRYBOOK.md`
8. `ui_gateway/README.md`

## What Was Pruned

Historical markdown reports, dated prompt snapshots, run summaries, and large session/source notes were removed from the forward-facing tree. Git history still carries them. The repo should now privilege compact current-state docs over a stack of stale status artifacts.

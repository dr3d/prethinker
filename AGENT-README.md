# Agent README

This is the short handoff for coding agents working in Prethinker.

## First Read

1. [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md)
2. [README.md](https://github.com/dr3d/prethinker/blob/main/README.md)
3. [docs/CURRENT_RESEARCH_HEADLINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_RESEARCH_HEADLINE.md)
4. [docs/MULTI_PASS_SEMANTIC_COMPILER.md](https://github.com/dr3d/prethinker/blob/main/docs/MULTI_PASS_SEMANTIC_COMPILER.md)
5. [docs/ACTIVE_RESEARCH_LANES.md](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md)
6. [docs/CURRENT_HARNESS_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_HARNESS_INSTRUMENT.md)
7. [docs/PUBLIC_DOCS_GUIDE.md](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_DOCS_GUIDE.md)
8. [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md)
9. [docs/DOMAIN_PROFILE_CATALOG.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PROFILE_CATALOG.md)
10. [docs/NO_LANGUAGE_HANDLING_IN_PYTHON_AUDIT.md](https://github.com/dr3d/prethinker/blob/main/docs/NO_LANGUAGE_HANDLING_IN_PYTHON_AUDIT.md)
11. [docs/PRETHINK_GATEWAY_MVP.md](https://github.com/dr3d/prethinker/blob/main/docs/PRETHINK_GATEWAY_MVP.md)
12. [ui_gateway/README.md](https://github.com/dr3d/prethinker/blob/main/ui_gateway/README.md)

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

The latest full-suite result is `571 passed, 2 subtests passed`. Recent focused
batteries also cover CourtListener, SEC/contracts, domain profiles, Semantic IR
runtime, UI gateway phases, trace rendering, router agility, router training
data, Lava v5, UMLS builders, profile bootstrap, raw-file intake planning,
post-ingestion QA, story-world fixtures, CE, and rule acquisition. Live/generated
smoke traces belong under ignored paths such as `datasets/*/generated/` and
`tmp/`.

## Harness Preflight Notes

Before a long LM Studio/GPU research burn, run a small readiness pass:

```powershell
python -m pytest -q
Invoke-RestMethod -Uri 'http://127.0.0.1:1234/v1/models' -TimeoutSec 5
python scripts/run_clarification_eagerness_fixture.py --surface both --limit 1 --model qwen/qwen3.6-35b-a3b --temperature 0 --timeout-seconds 240 --max-tokens 4096 --out-dir tmp/preflight_lm_harness
python scripts/run_umls_bridge_admission_probe.py
python scripts/run_domain_profile_smoke.py --dataset datasets/courtlistener/samples/legal_seed_synthetic_5.jsonl --profile-id legal_courtlistener@v0 --domain legal_courtlistener --limit-per-dataset 1 --backend lmstudio --model qwen/qwen3.6-35b-a3b --base-url http://127.0.0.1:1234/v1 --timeout 240 --max-tokens 4096 --out tmp/preflight_lm_harness/legal_profile_smoke.jsonl
python scripts/run_domain_profile_smoke.py --dataset datasets/sec_edgar/samples/sec_contracts_synthetic_5.jsonl --profile-id sec_contracts@v0 --domain sec_contracts --limit-per-dataset 1 --backend lmstudio --model qwen/qwen3.6-35b-a3b --base-url http://127.0.0.1:1234/v1 --timeout 240 --max-tokens 4096 --out tmp/preflight_lm_harness/sec_profile_smoke.jsonl
```

Notes from the 2026-05-03 Codex upgrade/preflight:

- A raw LM Studio ping with `response_format={"type":"json_object"}` returned
  HTTP 400. The project runners use strict `json_schema` payloads; verify with
  the actual runners rather than a generic ping.
- A tiny CE smoke with `--max-tokens 1200` produced a parse error because the
  Semantic IR was clipped. Rerunning the same case with `--max-tokens 4096`
  parsed and scored correctly. Treat low token caps as a likely cause of
  `empty_or_unparseable_semantic_ir`.
- The loaded Qwen endpoint may expose `reasoning_content` during raw manual
  pings. The harness configs pass `think_enabled=False` and
  `reasoning_effort=none`; use temperature `0` for research sweeps unless a run
  is explicitly measuring variance.
- After the Codex app upgrade, bundled `rg` at
  `C:\Program Files\WindowsApps\OpenAI.Codex_...\app\resources\rg.exe` returned
  `Access is denied`. If that happens, use PowerShell `Select-String` /
  `Get-ChildItem` until the bundled tool is available again.
- LM Studio base URL expectations differ by runner. `run_domain_bootstrap_file.py`
  expects `--base-url http://127.0.0.1:1234`; passing `/v1` produced an empty
  profile response in a Three Moles replay. `run_domain_bootstrap_qa.py` and
  the profile smoke scripts use `--base-url http://127.0.0.1:1234/v1`.
- Keep `tmp/` lean. Fixture handoff folders and bulky scratch outputs can be
  moved to `C:\prethinker_tmp_archive`; active local keepers are currently
  `tmp/licensed`, `tmp/cold_baselines`, `tmp/clarification_eagerness_runs`, and
  `tmp/domain_bootstrap_qa_cache`.
- Treat `C:\prethinker_tmp_archive` as the lab's cold-storage/RAG shelf. Search
  it for named artifacts or prior run evidence when needed, but do not bulk-load
  it into context. If an archived artifact becomes an active research result,
  summarize the lesson in tracked docs or fixture journals and reference the
  archive path.

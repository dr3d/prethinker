# Agent README

This is the short handoff for coding agents working in Prethinker.

## First Read

Read these in order before changing code:

1. [README.md](https://github.com/dr3d/prethinker/blob/main/README.md)
2. [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md)
3. [docs/CURRENT_RESEARCH_HEADLINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_RESEARCH_HEADLINE.md)
4. [docs/CTO_ARCHITECTURE_BRIEF.md](https://github.com/dr3d/prethinker/blob/main/docs/CTO_ARCHITECTURE_BRIEF.md)
5. [docs/ACTIVE_RESEARCH_LANES.md](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md)
6. [docs/CURRENT_HARNESS_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_HARNESS_INSTRUMENT.md)
7. [docs/COMPILED_KB_ARTIFACT_PACKAGE.md](https://github.com/dr3d/prethinker/blob/main/docs/COMPILED_KB_ARTIFACT_PACKAGE.md)
8. [docs/SEMANTIC_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_INSTRUMENT.md)
9. [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md)
10. [docs/BOUNDARY_PROBE_RESEARCH_METHOD.md](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_PROBE_RESEARCH_METHOD.md)
11. [docs/TWELVE_LENSES_EXPLAINED.md](https://github.com/dr3d/prethinker/blob/main/docs/TWELVE_LENSES_EXPLAINED.md)
12. [docs/PUBLIC_DOCS_GUIDE.md](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_DOCS_GUIDE.md)

Treat worksheets, generated reports, prompt snapshots, and long run journals as
archive material. Git history and `C:\prethinker_tmp_archive` preserve them; do
not use them as day-one guidance unless the user names a specific artifact.

## Current Shape

- `src/mcp_server.py` owns the canonical `process_utterance()` runtime.
- `ui_gateway/` is the manual cockpit for demos, route telemetry, KB mutation,
  and clarification turns.
- `semantic_ir_v1` is the active path: model-owned semantic workspace first,
  deterministic mapper admission second.
- `src/semantic_ir.py` owns mapper policy, projection policy, admission
  diagnostics, and profile-owned predicate alias normalization.
- `active_profile=auto` uses `semantic_router_v1` for context/profile selection
  only. It never authorizes writes.
- `modelfiles/domain_profile_catalog.v0.json` is the thin profile roster.
  Thick profile context lives in the `profile.*.json` files.
- `adapters/courtlistener/` and `adapters/sec_edgar/` are conservative source
  adapter shells. Keep live generated data and raw caches out of Git.
- The current document product is a compiled KB artifact package:
  `world.pl`, `epistemic.pl`, deterministic ledgers, query policy, manifest,
  and diagnostics.
- The live query policy is no-helper by default. Native helper companion rows
  are legacy/forensic compatibility, not the preferred architecture.

## Core Invariants

- Deterministic code decides what becomes durable truth.
- Model output is proposal material until mapper/runtime gates admit it.
- Keep source claims, established facts, uncertainty, corrections, and derived
  conclusions separate.
- Do not teach the harness fixture names, row IDs, answer strings, local people,
  or source-specific vocabulary.
- Do not reintroduce retired lab-automation, public-benchmarking, publishing,
  helper-era, or generated-report lanes.
- Public docs should describe the living project. Put stale notebooks and bulky
  artifacts in Git history or `C:\prethinker_tmp_archive`.
- Preserve user changes in a dirty worktree; never revert unrelated edits.

## Verification

Use focused tests while iterating, then run the full suite before a stopping
point commit when practical:

```powershell
python -m pytest tests/test_semantic_ir_runtime.py tests/test_semantic_router.py -q
python -m pytest tests/test_domain_bootstrap_file.py tests/test_domain_bootstrap_qa.py -q
python -m pytest tests/test_compile_surface_invariants.py tests/test_compile_surface_stability.py -q
python -m pytest tests/test_qa_mode_selector.py tests/test_selector_guard_families.py -q
python -m pytest -q
```

Latest known full-suite cleanup pass: `996 passed, 2 subtests passed`.

## Long Run Hygiene

- Keep `tmp/` lean; move bulky scratch output to `C:\prethinker_tmp_archive`.
- Use OpenRouter or POWER according to wall-clock throughput and provider
  stability. Hosted runs usually default to six lanes or fewer.
- Tag OpenRouter calls by experiment family/phase/fixture when possible.
- Treat transport/provider failures as transport evidence, not architecture
  evidence.
- If an archived artifact becomes important again, summarize the lesson in a
  current tracked doc instead of relinking the whole notebook.

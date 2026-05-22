# Agent README

This is the short handoff for coding agents working in Prethinker.

## First Read

Read these in order before changing code:

1. [README.md](https://github.com/dr3d/prethinker/blob/main/README.md)
2. [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md)
3. [docs/CURRENT_RESEARCH_HEADLINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_RESEARCH_HEADLINE.md)
4. [docs/AUDIT_GRAMMAR_MEASUREMENT_NOTE.md](https://github.com/dr3d/prethinker/blob/main/docs/AUDIT_GRAMMAR_MEASUREMENT_NOTE.md)
5. [docs/CTO_ARCHITECTURE_BRIEF.md](https://github.com/dr3d/prethinker/blob/main/docs/CTO_ARCHITECTURE_BRIEF.md)
6. [docs/ACTIVE_RESEARCH_LANES.md](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md)
7. [docs/COMPILED_KB_ARTIFACT_PACKAGE.md](https://github.com/dr3d/prethinker/blob/main/docs/COMPILED_KB_ARTIFACT_PACKAGE.md)
8. [docs/SEMANTIC_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_INSTRUMENT.md)
9. [docs/SEMANTIC_LENS_ROSTER.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_LENS_ROSTER.md)
10. [docs/QA_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/QA_INSTRUMENT.md)
11. [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md)
12. [docs/BOUNDARY_PROBE_RESEARCH_METHOD.md](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_PROBE_RESEARCH_METHOD.md)
13. [docs/PUBLIC_DOCS_GUIDE.md](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_DOCS_GUIDE.md)

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
- The live document QA path is governed QA over admitted state: the model may
  propose query plans or judge rows, while deterministic code controls admitted
  evidence, query execution, adapter policy, write blocking, and row accounting.
  Retired compatibility adapters are not day-one architecture.
- Current public measurement anchor: native restamp `1997 / 46 / 120` over
  `2163` rows (`92.33%` exact), real-world four-fixture spotcheck `160 / 0 / 0`,
  and sealed unseen authored transfer `152 / 1 / 6`, all with `0`
  compatibility rows, runtime load errors, and QA write proposals.

## Fresh Context Handoff

Current repo orientation should come from the documents above, not from dated
worksheets or old commit narratives. If a stale public surface, fixture-shaped
vocabulary leak, or active prompt/config drift appears, clean it up or record
the current lesson in a compact active doc.

Do not set cadence timers unless the user explicitly asks. The user prefers
continuous autonomous progress within the current session and will interrupt
when priorities change.

## Core Invariants

- Deterministic code decides what becomes durable truth.
- Model output is proposal material until mapper/runtime gates admit it.
- Keep source claims, established facts, uncertainty, corrections, and derived
  conclusions separate.
- Do not teach the harness fixture names, row IDs, answer strings, local people,
  or source-specific vocabulary.
- Do not reintroduce retired lab-automation, public-benchmarking, publishing,
  generated-report, or compatibility-adapter lanes.
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
python -m pytest tests/test_qa_mode_selector.py -q
python -m pytest -q
```

Latest known full-suite pass is recorded in `PROJECT_STATE.md`; rerun the full
suite before updating that headline.

Current public/current stale-surface checks should scan README, agent docs,
public docs, and active stamp/planner scripts for retired compatibility terms,
deleted guard-rollup links, and old hybrid-repair lane names. That grep should
return no hits. Broader script/test hits may still exist inside legacy
compatibility-adapter internals, virtual runtime predicates, and older test
names; do not rename those mechanically unless they leak into public docs,
fresh stamp artifacts, prompt guidance, or selector outputs.

## Long Run Hygiene

- Keep `tmp/` lean; move bulky scratch output to `C:\prethinker_tmp_archive`.
- Use OpenRouter or POWER according to wall-clock throughput and provider
  stability. Hosted runs usually default to six lanes or fewer.
- Tag OpenRouter calls by experiment family/phase/fixture when possible.
- Treat transport/provider failures as transport evidence, not architecture
  evidence.
- If an archived artifact becomes important again, summarize the lesson in a
  current tracked doc instead of relinking the whole notebook.

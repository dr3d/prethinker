# Agent README

This is the short handoff for coding agents working in Prethinker.

## First Read

Read these in order before changing code:

1. [README.md](https://github.com/dr3d/prethinker/blob/main/README.md)
2. [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md)
3. [docs/CURRENT_RESEARCH_HEADLINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_RESEARCH_HEADLINE.md)
4. [docs/CLOSED_DOMAIN_PREDICATE_PACKS_TECHNICAL_NOTE.md](https://github.com/dr3d/prethinker/blob/main/docs/CLOSED_DOMAIN_PREDICATE_PACKS_TECHNICAL_NOTE.md)
5. [docs/DOMAIN_PREDICATE_SCHEMA_PROCESS.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PREDICATE_SCHEMA_PROCESS.md)
6. [docs/DOMAIN_PACK_RESEARCH_EVIDENCE.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PACK_RESEARCH_EVIDENCE.md)
7. [docs/DOMAIN_PACK_STATUS.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PACK_STATUS.md)
8. [docs/DOMAIN_ACCOUNTABILITY_STATUS.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_ACCOUNTABILITY_STATUS.md)
9. [docs/DOMAIN_PREDICATE_PROPOSAL_STATUS.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PREDICATE_PROPOSAL_STATUS.md)
10. [docs/ACTIVE_RESEARCH_LANES.md](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md)
11. [docs/PUBLIC_DOCS_GUIDE.md](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_DOCS_GUIDE.md)
12. [docs/COMPILED_KB_ARTIFACT_PACKAGE.md](https://github.com/dr3d/prethinker/blob/main/docs/COMPILED_KB_ARTIFACT_PACKAGE.md)
13. [docs/QA_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/QA_INSTRUMENT.md)
14. [docs/OVERLAY_ARCHITECTURE.md](https://github.com/dr3d/prethinker/blob/main/docs/OVERLAY_ARCHITECTURE.md)
15. [docs/BOUNDARY_PROBE_RESEARCH_METHOD.md](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_PROBE_RESEARCH_METHOD.md)

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
- The public Python package facade is `prethinker` `0.5.0`; its
  `Engine.compile_document()` writes and returns that bundle shape. Default
  `compile_mode="ledger"` is deterministic and local; opt-in
  `compile_mode="semantic"` calls an OpenAI-compatible endpoint and only admits
  exact-source-anchored semantic candidates.
- The live document QA path is governed QA over admitted state: the model may
  propose query plans or judge rows, while deterministic code controls admitted
  evidence, query execution, adapter policy, write blocking, and row accounting.
  Retired compatibility adapters are not day-one architecture.
- Compile batch summaries now separate old pass/hold continuity from
  `blocking`, `diagnostic`, and `advisory` reason tiers. Blocking holds are
  release blockers; diagnostic holds are instrument signals. Do not silently
  relax the old headline, and do not treat every diagnostic hold as a release
  failure.
- Current claim-bearing research question: can a closed, lens-scoped predicate
  domain built from a small seed set transfer hard-clean to unlike messy
  official documents in the same family under strict governance?
- Older `80.5%`, `92%+`, `95%`, `98%+`, and `99%` scorecards are historical
  contamination evidence, not current accuracy claims. Some were inflated by
  prose/source-record routing, question-shape routing, and judge-facing answer
  tokens. If an old number is cited, say why it is false or non-claim-bearing.
- Current claim-bearing cells are domain-pack transfer cells that pass the
  gate suite: registered signatures, lens scope, atom shape, carrier value
  domains, redaction replay or typed-plan replay where applicable,
  `N>=3/support>=2`, zero supported forbidden facts, and unlike-document
  transfer. Product-style judge exact rate is diagnostic color unless it
  survives those gates.
- FDA warning letters are the first case study; SEC Form 8-K skeletons, NTSB
  investigations, and OSHA accident/inspection records are
  methodology-transfer/boundary probes. OSHA now has a measured local N=3
  seed/transfer skeleton probe (`21/21`, `15/15`, both `0` supported
  forbidden), but it is fourth-family corroboration rather than a broad OSHA
  product claim. Do not grind rows toward a nicer score. Characterize failure
  classes and abstention boundaries.

## Fresh Context Handoff

Current repo orientation should come from the documents above, not from dated
worksheets or old commit narratives. If a stale public surface, fixture-shaped
vocabulary leak, or active prompt/config drift appears, clean it up or record
the current lesson in a compact active doc.

There are no pending external work orders in the current queue. FDA
documentation-gap review is complete and rejected for transfer_002; FDA
response-assessment item review is complete across transfer_001/002/003 but
remains candidate evidence, not a promoted surface. If a new source-only work
order is created, keep it packetized and blind to model outputs.

ACH remains overlay-only: it may propose and score evidence matrices, but it
must not mutate KB facts, QA verdicts, or compile artifacts.

Do not set cadence timers unless the user explicitly asks. The user prefers
continuous autonomous progress within the current session and will interrupt
when priorities change.

## Core Invariants

- Deterministic code decides what becomes durable truth.
- Model output is proposal material until mapper/runtime gates admit it.
- LLM/router/Semantic IR owns messy human language. Deterministic query support
  may consume structured `query_intents[]`, query templates, predicates,
  identifiers, source coordinates, and typed atoms. It must not add new English
  keyword gates over raw user questions, source-record prose, source/display
  strings, or model-authored prose fields.
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
- Use OpenRouter as the default measured lane for stamps, transfer batches, and
  provider-variance work. Local LM Studio / POWER is a smoke/probe lane until it
  proves benchmark equivalence under captured local metadata.
- Tag OpenRouter calls by experiment family/phase/fixture when possible.
- Treat transport/provider failures as transport evidence, not architecture
  evidence.
- Treat provider/backend, quantization, loaded context, routing, and prompt
  packing as measurement conditions, not incidental runtime details.
- If an archived artifact becomes important again, summarize the lesson in a
  current tracked doc instead of relinking the whole notebook.

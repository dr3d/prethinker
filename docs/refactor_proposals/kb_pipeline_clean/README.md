# KB Pipeline Clean Refactor Proposal

This directory records the proposal for replacing the current `kb_pipeline.py`
plus MCP runtime design. The daily-driver harness surface now lives in
`src/kb_pipeline_clean`, with compatibility imports kept here for proposal
readers.

The design keeps Python structural. Python code may normalize structured model
outputs, predicate clauses, schema fields, registry metadata, traces, and
runtime operation records. It must not infer source-language meaning from prose.

## Target Shape

- `runtime.py`: deterministic Prolog runtime ports and legacy adapters.
- `gate_session.py`: pre-think session state, token checks, clarification
  continuation, confirmation checks, query loop guard, and turn counters.
- `compiler_client.py`: compiler and Semantic IR client ports, with a legacy
  facade for the current MCP implementation.
- `parse_normalization.py`: ordered structural parse normalizer registry.
- `semantic_mapper.py`: boundary around `semantic_ir_v1` admission and
  `semantic_ir_to_legacy_parse`.
- `apply_engine.py`: deterministic assert/retract/query apply boundary.
- `mcp_tools.py`: MCP tool surface definitions and orchestration seams.
- `scenario_cli.py`: optional legacy scenario runner entrypoint.
- `MIGRATION_MATRIX.md`: old symbols mapped to their proposed homes.
- `ARCHITECTURE.md`: details, invariants, and parity plan.

## Safety Properties To Preserve

- Pre-think IDs gate writes, optionally gate all queries, and remain alive for
  mixed ingest/query turns.
- Clarification answers continue the pending turn and clear the query gate only
  after confirmation.
- Compiler traces expose pre-think source, fallback/rescue steps, parse rescues,
  Semantic IR traces, validation errors, and summary fields.
- Deterministic runtime operations keep existing statuses and result shapes for
  assert fact, assert rule, retract fact, and query rows.
- Semantic IR remains an admission mapper boundary. Router/profile context can
  guide model input, but mapper diagnostics and predicate contracts decide
  whether operations become legacy parse operations.
- Normalizers operate only on structured parse payloads, clauses, predicate
  signatures, type schemas, and metadata. They do not interpret free text except
  where the existing legacy fallback explicitly did so; those legacy cases should
  be retired behind compiler output fixtures or moved to model/prompt tests.

## Safe Migration Plan

1. Land this proposal as documentation and static scaffolding only.
2. Add a parity harness that runs current `process_utterance`, deterministic
   runtime tests, and Semantic IR mapper tests against captured fixtures.
3. Extract `CorePrologRuntime` to the new runtime module with a compatibility
   import from `kb_pipeline.py`.
4. Extract `_apply_to_kb` behind `ApplyEngine`, preserving result shapes exactly.
5. Move MCP gate/session code to `gate_session.py`; keep `src/mcp_server.py`
   delegating to it.
6. Move parse normalizers one category at a time. Each move should include
   before/after trace event parity.
7. Finally split legacy scenario CLI from runtime/parser code.

## Suggested Validation

Run these before and after each migration step:

```powershell
python scripts/run_kb_pipeline_clean_harness.py --audit-normalizers
python scripts/run_kb_pipeline_clean_harness.py --trace-plan
python -m pytest tests/test_kb_pipeline_clean_parity_harness.py
Get-ChildItem docs/refactor_proposals/kb_pipeline_clean -Filter *.py | ForEach-Object { python -m py_compile $_.FullName }
python docs/refactor_proposals/kb_pipeline_clean/scenario_cli.py --audit-normalizers
python -m pytest tests/test_core_runtime.py tests/test_mcp_server.py tests/test_semantic_ir_runtime.py
python -m pytest tests/test_clarification_eagerness.py tests/test_process_utterance_forge.py
```

## Daily-Driver Harness

Use the promoted clean harness when replaying current behavior for future
compiler factoring:

```powershell
python scripts/run_kb_pipeline_clean_harness.py --pack path/to/frontier_pack.json --compiler-mode heuristic
```

The harness runs the live `process_utterance` path, writes raw results, and
stores canonical signatures for parity comparison. It does not judge prose or
reward improved behavior; it records the current structural shape so later
extractions can prove they preserved it.

For parity fixtures, compare:

- top-level `status` and `result_type`
- `front_door.route`, `front_door.compiler_intent`, and clarification fields
- `execution.intent`, `writes_applied`, `operations[*].tool`, and operation
  result statuses
- `compiler_trace.summary`, pre-think source, parse rescue names, and
  Semantic IR trace presence


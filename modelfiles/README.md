# Semantic Parser Modelfile Pack

This folder contains a tuned Modelfile for turning Qwen 3.5 9B into a strict semantic parser for Prolog-style structures.

Last updated: 2026-04-09

## Included

- `qwen35-9b-semantic-parser.Modelfile`
- `qwen35-9b-findings.md` (observed 9B behavior and recommended guardrails)
- `test-lmstudio-semparse.ps1` (2-pass validator for LM Studio and Ollama)
- `semantic_parser_system_prompt.md` (human-editable prompt pack used by `kb_pipeline.py`)
- `semantic_parser_system_prompt_candidate.md` (staging candidate for future prompt A/B work; not active by default)
- `freethinker_system_prompt.md` (staging sidecar prompt for future clarification-liaison work; inactive while policy is `off`)
- `history/prompts/*.md` (immutable prompt snapshots keyed by `prompt_id`)

## Build (Ollama)

```bash
ollama create qwen35-semparse -f modelfiles/qwen35-9b-semantic-parser.Modelfile
```

## Rebuild From Latest Prompt (One Command)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/rebake_semparse.ps1
```

Optional smoke test:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/rebake_semparse.ps1 -RunSmokeTest
```

## Run

```bash
ollama run qwen35-semparse "Who is John's parent?"
```

Expected output shape:

```json
{
  "intent": "query",
  "logic_string": "parent(john, X).",
  "components": {
    "atoms": ["john"],
    "variables": ["X"],
    "predicates": ["parent"]
  },
  "facts": [],
  "rules": [],
  "queries": ["parent(john, X)."],
  "confidence": {
    "overall": 0.94,
    "intent": 0.98,
    "logic": 0.92
  },
  "ambiguities": [],
  "needs_clarification": false,
  "rationale": "Question asks for unknown parent binding of john."
}
```

## Optional Model Variants

Keep the same system prompt and change only the `FROM` line:

- `FROM qwen3.5:4b` (faster, weaker on hard ambiguity)
- `FROM qwen3.5:14b` (if available)
- `FROM qwen3.5:27b` (slower, usually stronger extraction)

## Local LM Studio Notes

- Base URL used by pre-thinker tooling: `http://127.0.0.1:1234`
- Chat endpoint used by tooling: `/api/v1/chat`
- Auth env fallback chain in `mcp_server.py`:
  - `PRETHINKER_API_KEY`
  - `LMSTUDIO_API_KEY`
  - `OPENAI_API_KEY`
- Default pre-think model in `mcp_server.py`: `qwen/qwen3.5-9b`

If you stay on LM Studio instead of Ollama, reuse this same prompt as the system instruction in your `/api/v1/chat` calls.

## Prompt-Tuned Harness

Default mode in `test-lmstudio-semparse.ps1` is a tuned 2-pass flow:

1. classify route (`assert_fact|assert_rule|query|retract|other`)
2. route-locked extraction with strict schema/prolog constraints
3. optional repair pass if validation fails

Examples:

```bash
# LM Studio
powershell -ExecutionPolicy Bypass -File modelfiles/test-lmstudio-semparse.ps1 -Backend lmstudio -Model qwen/qwen3.5-9b -Utterance "Who is John's parent?"

# Ollama (when server is running)
powershell -ExecutionPolicy Bypass -File modelfiles/test-lmstudio-semparse.ps1 -Backend ollama -BaseUrl http://127.0.0.1:11434 -Model qwen3.5:9b -Utterance "Who is John's parent?"
```

## Build + Validate KBs (MCP Runtime Tools)

Use `kb_pipeline.py` to:

1. parse utterances with local 9B
2. apply deterministic MCP runtime tools (`assert_fact`, `assert_rule`, `retract_fact`, `query_rows`)
3. run scenario validations

Runtime behavior:

- Named ontology KBs are retained under `kb_store/<kb-name>/kb.pl`
- `empty_kb()` is used only for brand-new ontology namespaces (or when forced)
- Existing ontology namespaces are preloaded from retained corpus
- Prompt guidance is loaded from `modelfiles/semantic_parser_system_prompt.md` by default
- Prompt snapshots are auto-written to `modelfiles/history/prompts/` and tracked in each run report
- Split extraction is enabled by default: pass 1 logic-only parse, pass 2 deterministic schema refinement
- Hub publishing mirrors snapshots to `docs/prompts/` and indexes prompt performance in:
  - `docs/data/runs_manifest.json`
  - `docs/data/prompt_versions.json`

```bash
# Ollama
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/kb_positive.json --out kb_runs/kb_positive_ollama.json

# LM Studio
python kb_pipeline.py --backend lmstudio --base-url http://127.0.0.1:1234 --model qwen/qwen3.5-9b --scenario kb_scenarios/kb_positive.json --out kb_runs/kb_positive_lmstudio.json

# Named retained ontology KB + editable prompt file
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --kb-name people_core --prompt-file modelfiles/semantic_parser_system_prompt.md --scenario kb_scenarios/stage_03_transitive_chain.json --out kb_runs/stage_03_people_core.json
```

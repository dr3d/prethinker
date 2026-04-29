# Modelfiles And Prompt Assets

Last updated: 2026-04-29

This folder contains prompt and profile assets used by Prethinker. The current
mainline path is **Semantic IR v1** through LM Studio with:

```text
qwen/qwen3.6-35b-a3b
```

The older strict-parser Modelfile assets remain only for historical comparison
and legacy A/B work. They are not the default project direction.

## Current Assets

- `profile.*.json`: domain profile manifests and predicate contracts for
  Semantic IR context engineering.
- `predicate_registry*.json`: predicate palettes used by registry/admission
  checks.
- `medical_compiler_prompt_supplement.md`: bounded `medical@v0` profile
  guidance.
- `history/prompts/*.md`: generated local prompt snapshots; useful for
  provenance, not part of the current docs spine.

## Legacy Assets

- `semantic_parser_system_prompt.md`: legacy parser prompt pack retained for
  historical comparison and compatibility tests.
- `semantic_parser_system_prompt_candidate.md`: older staging candidate for
  parser-lane prompt A/B work.
- the old Ollama parser-lane Modelfile retained for historical comparisons.
- `test-lmstudio-semparse.ps1`: older parser-lane smoke harness.

These are retained so historical comparisons can still be reproduced. New
research should start from the Semantic IR path, not by baking another old-style
English parser.

## Current Local Runtime

The current local model endpoint is the LM Studio OpenAI-compatible API:

```text
base URL: http://127.0.0.1:1234
model:    qwen/qwen3.6-35b-a3b
context:  16384
```

The UI gateway and current docs are oriented around that path.

## Useful Commands

Run the current console:

```powershell
python ui_gateway/main.py
```

Run the full local suite:

```powershell
python -m pytest -q
```

Check currently loaded LM Studio models:

```powershell
Invoke-RestMethod http://127.0.0.1:1234/v1/models
```

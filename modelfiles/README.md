# Modelfiles And Prompt Assets

Last updated: 2026-04-29

This folder contains prompt and profile assets used by Prethinker. The current
mainline path is **Semantic IR v1** through LM Studio with:

```text
qwen/qwen3.6-35b-a3b
```

The older strict-parser Modelfile assets were retired from the working tree.
Git history is the archive for that parser lane.

## Current Assets

- `profile.*.json`: domain profile manifests and predicate contracts for
  Semantic IR context engineering.
- `predicate_registry*.json`: predicate palettes used by registry/admission
  checks.
- `medical_compiler_prompt_supplement.md`: bounded `medical@v0` profile
  guidance.
- `blank_prompt.md`: compatibility placeholder for legacy config fields that
  no longer inject parser-lane prompt text.

New research should start from the Semantic IR path, not by baking another
old-style English parser.

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

# Model Size Matrix (3x6)

Generated: 2026-04-11T03:07:00+00:00

Scope: Ollama only, 3 model sizes x 6 core scenarios.

| Model | Overall | Validation | Parser Failures | Apply Failures | Clarification Requests |
| --- | --- | --- | --- | --- | --- |
| qwen3.5:4b | 6/6 | 15/15 | 0 | 0 | 0 |
| qwen3.5:9b | 6/6 | 15/15 | 0 | 0 | 0 |
| qwen3.5:27b | 6/6 | 15/15 | 0 | 0 | 0 |

Best by overall passes: **qwen3.5:4b**

## Scenario Results

### qwen3.5:4b

- `stage_01_facts_only`: `passed` (2/2), parser_fail=0, apply_fail=0, clar=0
- `stage_02_rule_ingest`: `passed` (1/1), parser_fail=0, apply_fail=0, clar=0
- `stage_03_transitive_chain`: `passed` (1/1), parser_fail=0, apply_fail=0, clar=0
- `acid_03_temporal_override`: `passed` (3/3), parser_fail=0, apply_fail=0, clar=0
- `acid_04_alias_pressure`: `passed` (3/3), parser_fail=0, apply_fail=0, clar=0
- `acid_05_long_context_lineage`: `passed` (5/5), parser_fail=0, apply_fail=0, clar=0

### qwen3.5:9b

- `stage_01_facts_only`: `passed` (2/2), parser_fail=0, apply_fail=0, clar=0
- `stage_02_rule_ingest`: `passed` (1/1), parser_fail=0, apply_fail=0, clar=0
- `stage_03_transitive_chain`: `passed` (1/1), parser_fail=0, apply_fail=0, clar=0
- `acid_03_temporal_override`: `passed` (3/3), parser_fail=0, apply_fail=0, clar=0
- `acid_04_alias_pressure`: `passed` (3/3), parser_fail=0, apply_fail=0, clar=0
- `acid_05_long_context_lineage`: `passed` (5/5), parser_fail=0, apply_fail=0, clar=0

### qwen3.5:27b

- `stage_01_facts_only`: `passed` (2/2), parser_fail=0, apply_fail=0, clar=0
- `stage_02_rule_ingest`: `passed` (1/1), parser_fail=0, apply_fail=0, clar=0
- `stage_03_transitive_chain`: `passed` (1/1), parser_fail=0, apply_fail=0, clar=0
- `acid_03_temporal_override`: `passed` (3/3), parser_fail=0, apply_fail=0, clar=0
- `acid_04_alias_pressure`: `passed` (3/3), parser_fail=0, apply_fail=0, clar=0
- `acid_05_long_context_lineage`: `passed` (5/5), parser_fail=0, apply_fail=0, clar=0

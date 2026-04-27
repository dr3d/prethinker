# Golden KB Workflow

This folder defines the source-of-truth benchmark path for story ingestion.

Core idea:

- rigorous run (with crafted probe Q&A) -> verified answer KB
- freeze verified answer KB as golden artifact
- future regression runs compare generated KB directly to golden KB

This makes performance checks fast and deterministic.

## Layout

- `goldens/manifest.json`: benchmark registry
- `goldens/kb/<story_id>.pl`: canonical answer KB per story
- `goldens/probes/<story_id>.json`: crafted probe Q&A coverage set
- `stories/<story_id>.md`: narrative input text

## Commands

Freeze a golden KB from a rigorous run report:

```bash
python scripts/golden_kb.py freeze --report kb_runs/<run>.json --output goldens/kb/<story_id>.pl --meta-out tmp/golden_freeze_<story_id>.json
```

Compare candidate KB to golden KB:

```bash
python scripts/golden_kb.py compare --golden goldens/kb/<story_id>.pl --candidate tmp/kb_store/<ontology>/kb.pl --out tmp/golden_compare_<story_id>.json
```

Fast benchmark (story scenario -> generated KB -> golden compare):

```bash
python scripts/golden_kb.py benchmark --scenario kb_scenarios/<story_id>.json --golden goldens/kb/<story_id>.pl --backend lmstudio --model qwen/qwen3.6-35b-a3b --prompt-file modelfiles/semantic_parser_system_prompt.md --clarification-eagerness 0.0 --max-clarification-rounds 0 --force-empty-kb --out-summary tmp/golden_bench_<story_id>.json
```

Run every manifest entry:

```bash
python scripts/golden_kb.py benchmark-manifest --manifest goldens/manifest.json --prompt-file modelfiles/semantic_parser_system_prompt.md --out-summary tmp/golden_manifest_summary.json
```

## Policy

- Only freeze a golden KB after rigorous probe Q&A coverage.
- Golden KBs should be canonicalized and stable across reruns.
- Routine tuning/regression checks should use fast benchmark mode with Q&A minimized or disabled.

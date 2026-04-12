# Archive Strategy

This folder stores crash-safe backup bundles that are intended for cloud commit.

- Why: `tmp/` is intentionally gitignored for local iteration speed/noise control.
- Goal: preserve full run/prompt history off-machine without flooding published docs.

## Current Bundle Format

- `prethinker-history-<UTCSTAMP>.zip`
  - includes:
    - `tmp/runs/`
    - `tmp/prompt_history/`
    - `modelfiles/history/prompts/`
- `prethinker-history-<UTCSTAMP>.metadata.json`
  - machine-readable manifest for what was packed.

## Publishing Pattern

1. Keep docs hub curated (latest/high-signal runs only).
2. Keep complete historical traces in this archive folder.
3. Push both to cloud so the local machine is not the only source of truth.

# Archive Strategy

This folder stores curated historical artifacts that are worth keeping in Git
but do not belong on the public docs front door.

- Why: `tmp/` is intentionally gitignored for local iteration speed/noise control.
- Goal: keep public docs focused while still preserving durable research artifacts.
- Local bulk scratch archives may live outside the repo, such as
  `C:\prethinker_tmp_archive`, when they are too noisy or too large for Git.

## What Belongs Here

- Small historical reports that explain important research turns.
- Curated manifests for archive bundles that are actually present.
- Legacy notes only when they remain useful after a handoff.

## Promotion Pattern

1. Keep `docs/README.md` and `docs/PUBLIC_DOCS_GUIDE.md` curated
   (latest/high-signal runs only).
2. Keep complete large scratch traces in the external archive unless they are
   intentionally promoted.
3. Promote only curated artifacts that need to be shared; leave bulk scratch
   traces in Git history or the external archive.

## Current External Archive Bundles

Recent repo-cleanup sweeps moved bulky or stale local material to:

- `C:\prethinker_tmp_archive\repo_doc_retire_20260514`
- `C:\prethinker_tmp_archive\repo_stale_assets_20260514`
- `C:\prethinker_tmp_archive\tmp_sweep_20260514`
- `C:\prethinker_tmp_archive\tmp_lean_markdown_docs_cleanup_20260522`
- `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522`

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

## Publishing Pattern

1. Keep docs hub curated (latest/high-signal runs only).
2. Keep complete large scratch traces in the external archive unless they are
   intentionally promoted.
3. Push curated artifacts to cloud so the local machine is not the only source
   of truth.

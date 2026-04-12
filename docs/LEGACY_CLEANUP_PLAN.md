# Legacy Cleanup Plan (Audit Notes)

Date: 2026-04-12

This note captures low-risk cleanup opportunities to reduce repo noise without losing key evidence.

## High-Noise, Low-Risk Candidates

1. `tmp/runs/ladder_summary_*.json`
- Problem: many timestamped summaries with heavy duplication.
- Action: keep latest N snapshots, delete older.

2. `tmp/runs/**` (including `ladder/` and one-off JSONs)
- Problem: large transient corpus already git-ignored.
- Action: periodic delete or zip archive outside repo root.

3. `tmp/docs/**`, `tmp/.tmp_docs/**`, `tmp/publish_runs/**`, `tmp/publish_runs_curated/**`, `tmp/.tmp_runs/**`
- Problem: intermediate build mirrors and stale preview artifacts.
- Action: delete.

4. `tmp/.tmp_*`, `tmp/AGENT._delete_me.md`, `tmp/old_build_hub_index.py`
- Problem: explicit legacy scratch artifacts.
- Action: delete.

## Medium-Risk Candidates (Archive First)

1. `docs/data/runs/*.json` not present in current `docs/data/runs_manifest.json`
- Problem: stale docs data beyond curated set can confuse consumers.
- Action: archive stale extras under `docs/data/runs/history/` or delete after backup.

2. `docs/reports/*.html` not linked from docs hub/explorer
- Problem: legacy report drift (`*_resume5_latest`, size-matrix one-offs, old cycle pages).
- Action: move to `docs/reports/history/` and keep curated top-level reports clean.

3. `kb_runs/*_resume5_latest.json`, `kb_runs/ladder_c*.json`, older stage variants
- Problem: historical naming clutter.
- Action: keep canonical history but archive old families by prefix/date.

4. timestamped one-off namespaces in `kb_store/`
- Problem: KB namespace sprawl from ad-hoc experiments.
- Action: retain canonical namespaces, archive/delete aged timestamped namespaces.

## Keep As-Is

- `kb_runs_published/*.json` (current docs source of truth)
- `kb_runs/size_matrix/20260411/*.json` (used by model-size matrix summary)

## Process Recommendation

1. Introduce a monthly cleanup script that:
- prunes old `tmp/` artifacts,
- reports stale docs runs/reports not in curated manifest,
- optionally migrates stale docs artifacts into a dated `history/` folder.

2. Keep full historical evidence in `kb_runs/`, but keep docs surfaces curated and bounded.

3. Prefer track summaries (`docs/data/tracks/*.json`) for ongoing score reporting over large raw run dumps.

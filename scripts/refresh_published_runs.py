#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
from pathlib import Path
from typing import Any


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Refresh curated published run set from a larger run corpus."
    )
    p.add_argument("--source-dir", default="kb_runs", help="Full run corpus directory.")
    p.add_argument(
        "--output-dir",
        default="kb_runs_published",
        help="Curated output run directory used for docs publishing.",
    )
    p.add_argument(
        "--max-runs",
        type=int,
        default=24,
        help="Maximum newest runs to keep in curated output.",
    )
    p.add_argument(
        "--keep-scenarios",
        default=(
            "stage_00_multilingual_probe,stage_00_foreign_unseen_probe,"
            "acid_03_temporal_override,acid_04_alias_pressure,acid_05_long_context_lineage"
        ),
        help="Comma-separated scenarios to always keep (latest run for each).",
    )
    return p.parse_args()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        raw = path.read_text(encoding="utf-8-sig")
        value = json.loads(raw)
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def _parse_time(text: str) -> dt.datetime:
    t = (text or "").strip()
    if not t:
        return dt.datetime.fromtimestamp(0, tz=dt.timezone.utc)
    try:
        parsed = dt.datetime.fromisoformat(t.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(dt.timezone.utc)
    except ValueError:
        return dt.datetime.fromtimestamp(0, tz=dt.timezone.utc)


def _run_finished_time(path: Path, payload: dict[str, Any]) -> dt.datetime:
    finished = str(payload.get("run_finished_utc", "")).strip()
    started = str(payload.get("run_started_utc", "")).strip()
    parsed = _parse_time(finished) if finished else _parse_time(started)
    if parsed.timestamp() > 0:
        return parsed
    return dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc)


def main() -> int:
    args = _parse_args()
    source = Path(args.source_dir).resolve()
    out = Path(args.output_dir).resolve()
    keep_scenarios = {x.strip() for x in str(args.keep_scenarios).split(",") if x.strip()}

    if not source.exists():
        raise SystemExit(f"source-dir not found: {source}")

    candidates: list[tuple[dt.datetime, Path, dict[str, Any]]] = []
    for p in source.rglob("*.json"):
        if p.name.endswith(".dialog.json"):
            continue
        payload = _read_json(p)
        if not payload:
            continue
        if "overall_status" not in payload:
            continue
        candidates.append((_run_finished_time(p, payload), p, payload))

    candidates.sort(key=lambda row: row[0], reverse=True)
    newest = candidates[: max(0, int(args.max_runs))]

    forced: dict[str, tuple[dt.datetime, Path, dict[str, Any]]] = {}
    for row in candidates:
        scenario = str(row[2].get("scenario", "")).strip()
        if not scenario or scenario not in keep_scenarios:
            continue
        if scenario not in forced:
            forced[scenario] = row

    selected: dict[str, tuple[dt.datetime, Path, dict[str, Any]]] = {}
    for row in newest:
        selected[str(row[1].resolve())] = row
    for row in forced.values():
        selected[str(row[1].resolve())] = row

    out.mkdir(parents=True, exist_ok=True)
    for existing in out.glob("*.json"):
        existing.unlink()

    rows = sorted(selected.values(), key=lambda row: row[0], reverse=True)
    for _, src, _ in rows:
        shutil.copy2(src, out / src.name)

    print(
        f"Curated published runs refreshed: {len(rows)} files "
        f"(newest={len(newest)}, forced={len(forced)})."
    )
    print(f"source={source}")
    print(f"output={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Queue bounded Autolab jobs that are safe to run without Codex watching."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAILBOX = Path(r"\\192.168.0.103\c\prethinker\tmp\hermes_mailbox")
DEFAULT_QUEUE_STATE = REPO_ROOT / "tmp" / "autolab_queue" / "last_queue_plan.json"
SAFE_JOB_TEMPLATES = (
    {
        "slug": "laptop_status_snapshot",
        "title": "Capture laptop checkout and Autolab status snapshot",
        "commands": [
            "git pull --ff-only origin main",
            "mkdir -p tmp/autolab_queue && { date -u; printf '\\nHEAD\\n'; git log -1 --oneline; printf '\\nSTATUS\\n'; git status --short; printf '\\nQUEUE ARTIFACTS\\n'; find tmp/autolab_queue -maxdepth 1 -type f | sort; } > tmp/autolab_queue/laptop_status_snapshot.txt",
        ],
        "timeout_seconds": 120,
    },
    {
        "slug": "focused_reporter_tests",
        "title": "Focused reporter and planner tests",
        "commands": [
            "git pull --ff-only origin main",
            "python -m pytest tests/test_rollup_domain_bootstrap_qa_scorecard.py tests/test_story_world_repair_targets.py tests/test_compare_domain_bootstrap_compiles.py tests/test_plan_story_world_fixture_runs.py tests/test_hermes_poll_mailbox.py tests/test_validate_autolab_candidate_artifacts.py",
        ],
        "timeout_seconds": 240,
    },
    {
        "slug": "story_frontier_plan",
        "title": "Generate current story frontier run plan",
        "commands": [
            "git pull --ff-only origin main",
            "python scripts/plan_story_world_fixture_runs.py --fixture avalon_grant_committee --fixture oxalis_recall --fixture three_moles_moon_marmalade_machine --qa-limit 40 --max-plan-passes 6 --classify-failure-surfaces --out-json tmp/autolab_queue/story_frontier_plan.json --out-md tmp/autolab_queue/story_frontier_plan.md",
        ],
        "timeout_seconds": 180,
    },
    {
        "slug": "reporter_py_compile",
        "title": "Stdlib compile check for Autolab reporter modules",
        "commands": [
            "git pull --ff-only origin main",
            "python -m py_compile scripts/compare_domain_bootstrap_compiles.py scripts/rollup_domain_bootstrap_qa_scorecard.py scripts/plan_story_world_repair_targets.py scripts/plan_story_world_fixture_runs.py scripts/hermes_poll_mailbox.py scripts/autolab_queue_next_safe_jobs.py scripts/validate_autolab_candidate_artifacts.py scripts/summarize_autolab_candidate_batch.py",
        ],
        "timeout_seconds": 180,
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mailbox", type=Path, default=DEFAULT_MAILBOX)
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--prefix", default="autolab_safe")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out-json", type=Path, default=DEFAULT_QUEUE_STATE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mailbox = _resolve_mailbox(args.mailbox)
    plan = build_queue_plan(mailbox=mailbox, limit=max(0, int(args.limit)), prefix=str(args.prefix))
    out_json = _resolve_repo(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")
    if not args.dry_run:
        write_jobs(plan)
    print(json.dumps(plan["summary"], sort_keys=True))
    return 0


def build_queue_plan(*, mailbox: Path, limit: int, prefix: str) -> dict[str, Any]:
    queued_ids = existing_job_ids(mailbox)
    templates = []
    if limit > 0:
        for template in SAFE_JOB_TEMPLATES:
            job_id = f"{prefix}_{template['slug']}"
            if job_id in queued_ids:
                continue
            templates.append(template)
            if len(templates) >= limit:
                break
    jobs = [build_job(template, mailbox=mailbox, prefix=prefix) for template in templates]
    return {
        "schema_version": "autolab_safe_job_queue_plan_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mailbox": str(mailbox),
        "policy": [
            "Queue only bounded JSON shell jobs.",
            "No heavy LM Studio calls.",
            "No source harvesting.",
            "No tracked code edits.",
            "No delete or move operations.",
            "No harness promotion decisions.",
        ],
        "summary": {
            "existing_job_ids": sorted(queued_ids),
            "planned_count": len(jobs),
            "dry_run_safe": True,
        },
        "jobs": jobs,
    }


def build_job(template: dict[str, Any], *, mailbox: Path, prefix: str) -> dict[str, Any]:
    job_id = f"{prefix}_{template['slug']}"
    return {
        "job_id": job_id,
        "kind": "shell",
        "timeout_seconds": int(template["timeout_seconds"]),
        "purpose": template["title"],
        "policy": [
            "Bounded safe Autolab conveyor-belt job.",
            "Uses repo .venv through the poller child environment.",
            "Writes one outbox result and stops.",
            "Codex reviews outputs before any heavy/model/coding follow-up.",
        ],
        "commands": list(template["commands"]),
        "target_path": str(mailbox / "inbox" / f"{job_id}.json"),
    }


def write_jobs(plan: dict[str, Any]) -> None:
    for job in plan.get("jobs", []):
        if not isinstance(job, dict):
            continue
        path = Path(str(job["target_path"]))
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {key: value for key, value in job.items() if key != "target_path"}
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def existing_job_ids(mailbox: Path) -> set[str]:
    ids: set[str] = set()
    for folder in ["inbox", "claimed", "running", "outbox", "failed", "archive"]:
        root = mailbox / folder
        if not root.exists():
            continue
        for path in root.glob("*"):
            parsed = _job_id_from_path(path)
            if parsed:
                ids.add(parsed)
    return ids


def _job_id_from_path(path: Path) -> str:
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            data = {}
        if isinstance(data, dict) and str(data.get("job_id", "")).strip():
            return str(data["job_id"]).strip()
    name = path.stem
    return name[:-7] if name.endswith("_result") else name


def _resolve_mailbox(path: Path) -> Path:
    return path if path.is_absolute() or str(path).startswith("\\\\") else REPO_ROOT / path


def _resolve_repo(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


if __name__ == "__main__":
    raise SystemExit(main())

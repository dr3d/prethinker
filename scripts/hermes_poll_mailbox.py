#!/usr/bin/env python3
"""Poll the shared Hermes mailbox for one autolab job.

The cron contract is intentionally small: run this script once a minute from a
Prethinker checkout. The script claims at most one mailbox job, writes an
outbox result, and exits. Markdown prompt jobs are handed to an operator-owned
Hermes adapter when one is installed; JSON shell jobs are deterministic smoke
jobs for verifying the mailbox and cron plumbing.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MAILBOX = Path(os.environ.get("HERMES_MAILBOX", "/mnt/c/prethinker/tmp/hermes_mailbox"))
REPO = Path(os.environ.get("PRETHINKER_REPO", Path.cwd()))
INBOX = MAILBOX / "inbox"
CLAIMED = MAILBOX / "claimed"
RUNNING = MAILBOX / "running"
OUTBOX = MAILBOX / "outbox"
FAILED = MAILBOX / "failed"
ARCHIVE = MAILBOX / "archive"
LOGS = MAILBOX / "logs"
STATE = MAILBOX / "state"
CONTROL = MAILBOX / "control"
PAUSE = MAILBOX / "PAUSE_HERMES.flag"
LOCK = STATE / "poller.lock"
HEAVY_BASE_URL = os.environ.get("HERMES_HEAVY_LMSTUDIO_BASE_URL", "http://192.168.0.150:1234/v1")
LOCAL_BASE_URL = os.environ.get("HERMES_LOCAL_LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")


def utcstamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_dirs() -> None:
    for path in [INBOX, CLAIMED, RUNNING, OUTBOX, FAILED, ARCHIVE, LOGS, STATE, CONTROL]:
        path.mkdir(parents=True, exist_ok=True)


def log(message: str) -> None:
    ensure_dirs()
    with (LOGS / "poll_mailbox_events.log").open("a", encoding="utf-8") as handle:
        handle.write(f"{datetime.now(timezone.utc).isoformat()} {message}\n")


def write_result(job_id: str, title: str, body: str, extra: dict[str, Any] | None = None) -> Path:
    ensure_dirs()
    result = OUTBOX / f"{job_id}_result.md"
    payload = extra or {}
    result.write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                f"- job_id: `{job_id}`",
                f"- completed_at: `{datetime.now(timezone.utc).isoformat()}`",
                f"- heavy_lmstudio_base_url: `{HEAVY_BASE_URL}`",
                f"- local_lmstudio_base_url: `{LOCAL_BASE_URL}`",
                "",
                body.rstrip(),
                "",
                "```json",
                json.dumps(payload, indent=2, sort_keys=True),
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return result


def parse_job_id(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")[:2000]
    match = re.search(r"(?m)^job_id:\s*([A-Za-z0-9_.:-]+)\s*$", text)
    if match:
        return re.sub(r"[^A-Za-z0-9_.-]+", "_", match.group(1))
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        if isinstance(data, dict) and str(data.get("job_id", "")).strip():
            return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(data["job_id"]).strip())
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", path.stem)


def acquire_lock(max_age_seconds: int = 55 * 60) -> bool:
    ensure_dirs()
    now = time.time()
    if LOCK.exists():
        age = now - LOCK.stat().st_mtime
        if age < max_age_seconds:
            log(f"lock_present age={age:.1f}s; exiting")
            return False
        stale = STATE / f"poller.lock.stale.{utcstamp()}"
        LOCK.rename(stale)
        log(f"moved stale lock to {stale}")
    LOCK.write_text(json.dumps({"pid": os.getpid(), "started_at": utcstamp()}), encoding="utf-8")
    return True


def release_lock() -> None:
    try:
        LOCK.unlink()
    except FileNotFoundError:
        pass


def next_job() -> Path | None:
    candidates = sorted(
        [*INBOX.glob("*.md"), *INBOX.glob("*.json")],
        key=lambda path: (
            0 if "critical" in path.name.lower() or path.name.startswith("0001") else 1,
            path.stat().st_mtime,
        ),
    )
    return candidates[0] if candidates else None


def claim_job(path: Path) -> tuple[str, Path]:
    job_id = parse_job_id(path)
    claimed_path = CLAIMED / f"{utcstamp()}_{path.name}"
    path.rename(claimed_path)
    return job_id, claimed_path


def run_shell_job(data: dict[str, Any]) -> tuple[bool, str, dict[str, Any]]:
    commands = data.get("commands") or []
    if not isinstance(commands, list) or not commands:
        return False, "JSON shell job had no commands list.", {"commands": commands}

    outputs: list[dict[str, Any]] = []
    timeout = int(data.get("timeout_seconds", 3600))
    for command in commands:
        if not isinstance(command, str) or not command.strip():
            continue
        proc = subprocess.run(
            command,
            shell=True,
            cwd=str(REPO),
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        outputs.append(
            {
                "command": command,
                "returncode": proc.returncode,
                "stdout": proc.stdout[-4000:],
                "stderr": proc.stderr[-4000:],
            }
        )
        if proc.returncode != 0:
            return False, f"Command failed: `{command}`", {"outputs": outputs}
    return True, "Shell job completed.", {"outputs": outputs}


def run_prompt_job(running_path: Path) -> tuple[bool, str, dict[str, Any]]:
    runner = STATE / "hermes_runner.sh"
    if runner.exists() and os.access(runner, os.X_OK):
        proc = subprocess.run(
            [str(runner), str(running_path)],
            cwd=str(REPO),
            text=True,
            capture_output=True,
            timeout=3600,
        )
        return (
            proc.returncode == 0,
            "Hermes runner finished.",
            {
                "returncode": proc.returncode,
                "stdout_tail": proc.stdout[-8000:],
                "stderr_tail": proc.stderr[-8000:],
                "runner": str(runner),
            },
        )

    return (
        False,
        "No executable state/hermes_runner.sh is installed. Manual Hermes must create this adapter so the poller can hand markdown prompts to Hermes. The claimed job was preserved; no model work was attempted.",
        {"expected_runner": str(runner), "job_path": str(running_path)},
    )


def process_running_job(job_id: str, running_path: Path) -> tuple[bool, str, dict[str, Any]]:
    if running_path.suffix.lower() == ".json":
        data = json.loads(running_path.read_text(encoding="utf-8"))
        if data.get("kind") == "shell":
            return run_shell_job(data)
        return False, f"Unsupported JSON job kind: {data.get('kind')!r}", {"job": data}
    return run_prompt_job(running_path)


def process_one() -> int:
    ensure_dirs()
    if PAUSE.exists():
        log("pause flag present; exiting")
        return 0
    if not acquire_lock():
        return 0
    try:
        job = next_job()
        if job is None:
            log("no inbox jobs")
            return 0
        job_id, claimed_path = claim_job(job)
        running_path = RUNNING / claimed_path.name
        claimed_path.rename(running_path)
        log(f"running job_id={job_id} path={running_path}")

        try:
            ok, message, extra = process_running_job(job_id, running_path)
        except Exception as error:  # pragma: no cover - defensive outbox reporting
            ok = False
            message = f"Exception while processing job: {error}"
            extra = {"error_type": type(error).__name__}

        title = "Hermes Mailbox Job Success" if ok else "Hermes Mailbox Job Failed"
        write_result(job_id, title, message, {"ok": ok, "job_file": str(running_path), **extra})

        dest_dir = ARCHIVE if ok else FAILED
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(running_path), str(dest_dir / running_path.name))
        log(f"finished job_id={job_id} ok={ok}")
        return 0 if ok else 2
    finally:
        release_lock()


if __name__ == "__main__":
    raise SystemExit(process_one())

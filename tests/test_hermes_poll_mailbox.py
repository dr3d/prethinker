from __future__ import annotations

import importlib
import json
import os


def _load_poller(monkeypatch, tmp_path):
    mailbox = tmp_path / "mailbox"
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setenv("HERMES_MAILBOX", str(mailbox))
    monkeypatch.setenv("PRETHINKER_REPO", str(repo))
    import scripts.hermes_poll_mailbox as poller

    return importlib.reload(poller)


def test_poller_respects_pause_flag(monkeypatch, tmp_path) -> None:
    poller = _load_poller(monkeypatch, tmp_path)
    poller.ensure_dirs()
    poller.PAUSE.write_text("paused", encoding="utf-8")
    (poller.INBOX / "job.md").write_text("---\njob_id: pause_test\n---\n\nDo nothing.\n", encoding="utf-8")

    assert poller.process_one() == 0
    assert (poller.INBOX / "job.md").exists()
    assert not list(poller.OUTBOX.glob("*_result.md"))


def test_poller_runs_json_shell_job_once(monkeypatch, tmp_path) -> None:
    poller = _load_poller(monkeypatch, tmp_path)
    poller.ensure_dirs()
    job = {
        "job_id": "shell_smoke",
        "kind": "shell",
        "commands": ["echo shell_smoke"],
        "timeout_seconds": 30,
    }
    (poller.INBOX / "shell_smoke.json").write_text(json.dumps(job), encoding="utf-8")

    assert poller.process_one() == 0

    result = poller.OUTBOX / "shell_smoke_result.md"
    assert result.exists()
    assert "Hermes Mailbox Job Success" in result.read_text(encoding="utf-8")
    assert not (poller.INBOX / "shell_smoke.json").exists()
    assert list(poller.ARCHIVE.glob("*shell_smoke.json"))


def test_poller_prefers_repo_venv_for_shell_jobs(monkeypatch, tmp_path) -> None:
    poller = _load_poller(monkeypatch, tmp_path)
    poller.ensure_dirs()
    venv_bin = poller.REPO / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    if os.name != "nt":
        python = venv_bin / "python"
        python.write_text("#!/usr/bin/env sh\npython3 \"$@\"\n", encoding="utf-8")
        python.chmod(0o755)
    job = {
        "job_id": "venv_python",
        "kind": "shell",
        "commands": ["python -c \"import os; print(os.environ.get('VIRTUAL_ENV', ''))\""],
        "timeout_seconds": 30,
    }
    (poller.INBOX / "venv_python.json").write_text(json.dumps(job), encoding="utf-8")

    assert poller.process_one() == 0

    text = (poller.OUTBOX / "venv_python_result.md").read_text(encoding="utf-8")
    assert '"venv_present": true' in text
    assert ".venv" in text


def test_json_shell_job_accepts_utf8_bom(monkeypatch, tmp_path) -> None:
    poller = _load_poller(monkeypatch, tmp_path)
    poller.ensure_dirs()
    job = {
        "job_id": "bom_smoke",
        "kind": "shell",
        "commands": ["echo bom_smoke"],
        "timeout_seconds": 30,
    }
    (poller.INBOX / "bom_smoke.json").write_text(json.dumps(job), encoding="utf-8-sig")

    assert poller.process_one() == 0

    result = poller.OUTBOX / "bom_smoke_result.md"
    assert result.exists()
    assert "Hermes Mailbox Job Success" in result.read_text(encoding="utf-8")
    assert not (poller.INBOX / "bom_smoke.json").exists()
    assert list(poller.ARCHIVE.glob("*bom_smoke.json"))


def test_poller_processes_at_most_one_job_per_invocation(monkeypatch, tmp_path) -> None:
    poller = _load_poller(monkeypatch, tmp_path)
    poller.ensure_dirs()
    first = {
        "job_id": "first_smoke",
        "kind": "shell",
        "commands": ["echo first"],
        "timeout_seconds": 30,
    }
    second = {
        "job_id": "second_smoke",
        "kind": "shell",
        "commands": ["echo second"],
        "timeout_seconds": 30,
    }
    (poller.INBOX / "0001_first_smoke.json").write_text(json.dumps(first), encoding="utf-8")
    (poller.INBOX / "0002_second_smoke.json").write_text(json.dumps(second), encoding="utf-8")

    assert poller.process_one() == 0

    assert (poller.OUTBOX / "first_smoke_result.md").exists()
    assert not (poller.OUTBOX / "second_smoke_result.md").exists()
    assert not (poller.INBOX / "0001_first_smoke.json").exists()
    assert (poller.INBOX / "0002_second_smoke.json").exists()


def test_prompt_job_without_runner_fails_with_actionable_result(monkeypatch, tmp_path) -> None:
    poller = _load_poller(monkeypatch, tmp_path)
    poller.ensure_dirs()
    (poller.INBOX / "prompt.md").write_text("---\njob_id: prompt_adapter\n---\n\nRun Hermes.\n", encoding="utf-8")

    assert poller.process_one() == 2

    result = poller.OUTBOX / "prompt_adapter_result.md"
    assert result.exists()
    text = result.read_text(encoding="utf-8")
    assert "Hermes Mailbox Job Failed" in text
    assert "state/hermes_runner.sh" in text
    assert list(poller.FAILED.glob("*prompt.md"))

from __future__ import annotations

import importlib
import json


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

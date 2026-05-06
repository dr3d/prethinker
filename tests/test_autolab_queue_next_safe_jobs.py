import json

from scripts.autolab_queue_next_safe_jobs import build_queue_plan, write_jobs


def test_queue_plan_writes_bounded_safe_jobs(tmp_path) -> None:
    mailbox = tmp_path / "mailbox"

    plan = build_queue_plan(mailbox=mailbox, limit=2, prefix="demo")
    write_jobs(plan)

    assert plan["summary"]["planned_count"] == 2
    paths = sorted((mailbox / "inbox").glob("*.json"))
    assert len(paths) == 2
    payload = json.loads(paths[0].read_text(encoding="utf-8"))
    assert payload["kind"] == "shell"
    assert payload["job_id"].startswith("demo_")
    assert all("python" in command or "git pull" in command for command in payload["commands"])
    assert "target_path" not in payload


def test_queue_plan_avoids_existing_job_ids(tmp_path) -> None:
    mailbox = tmp_path / "mailbox"
    inbox = mailbox / "inbox"
    inbox.mkdir(parents=True)
    existing = {"job_id": "demo_laptop_status_snapshot", "kind": "shell", "commands": ["echo done"]}
    (inbox / "demo_laptop_status_snapshot.json").write_text(json.dumps(existing), encoding="utf-8")

    plan = build_queue_plan(mailbox=mailbox, limit=3, prefix="demo")

    job_ids = [job["job_id"] for job in plan["jobs"]]
    assert "demo_laptop_status_snapshot" not in job_ids
    assert "demo_focused_reporter_tests" in job_ids
    assert "demo_story_frontier_plan" in job_ids


def test_queue_plan_avoids_recent_archive_and_failed_packets(tmp_path) -> None:
    mailbox = tmp_path / "mailbox"
    archive = mailbox / "archive"
    failed = mailbox / "failed"
    archive.mkdir(parents=True)
    failed.mkdir(parents=True)
    (archive / "demo_laptop_status_snapshot.json").write_text(
        json.dumps({"job_id": "demo_laptop_status_snapshot"}), encoding="utf-8"
    )
    (failed / "demo_focused_reporter_tests.json").write_text(
        json.dumps({"job_id": "demo_focused_reporter_tests"}), encoding="utf-8"
    )

    plan = build_queue_plan(mailbox=mailbox, limit=3, prefix="demo")

    job_ids = [job["job_id"] for job in plan["jobs"]]
    assert "demo_laptop_status_snapshot" not in job_ids
    assert "demo_focused_reporter_tests" not in job_ids
    assert "demo_story_frontier_plan" in job_ids


def test_queue_plan_can_dry_run_zero_jobs(tmp_path) -> None:
    plan = build_queue_plan(mailbox=tmp_path / "mailbox", limit=0, prefix="demo")

    assert plan["summary"]["planned_count"] == 0
    assert plan["jobs"] == []

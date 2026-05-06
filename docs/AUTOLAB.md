# Prethinker Autolab

Last updated: 2026-05-06

## What Autolab Is

Prethinker Autolab is the out-of-band harness tester and research factory.
It lets a remote Hermes worker run queued jobs while Codex remains the lab lead,
repo steward, and integration point.

Autolab is not a second source of truth. It is a work queue plus a worker loop:
cron wakes the laptop, the poller claims one mailbox job, Hermes does bounded
work, and the result comes back as an inspectable artifact.

```text
Codex
  -> writes a mailbox job
  -> Hermes claims the job
  -> Hermes runs cheap work locally or routes heavy Prethinker work to desktop LM Studio
  -> Hermes writes an outbox result
  -> Codex inspects, journals durable lessons, changes repo code/docs, and pushes
```

## Roles

| Part | Role |
| --- | --- |
| Codex | Lab lead, job author, result reviewer, repo/doc/journal steward. |
| Hermes | Remote worker agent running on the laptop. |
| Autolab | Mailbox, cron poller, job protocol, and harness work queue. |
| Laptop LM Studio | Light Hermes planning/model lane. |
| Desktop LM Studio | Heavy Prethinker semantic engine, currently exposed at `http://192.168.0.150:1234/v1`. |
| Repo docs/journals | Durable research memory. |
| `tmp/hermes_mailbox` | Operational workbench; mostly disposable. |
| `prethinker_tmp_archive` | Useful retained scratch/RAG-adjacent lab archive. |

## Mailbox Contract

The shared mailbox root is:

```text
Windows: \\192.168.0.103\c\prethinker\tmp\hermes_mailbox
WSL:     /mnt/c/prethinker/tmp/hermes_mailbox
```

The tracked poller is:

```text
scripts/hermes_poll_mailbox.py
```

Cron should run that script once per minute from a current Prethinker checkout.
The poller processes at most one job per invocation.

Mailbox folders:

| Folder | Purpose |
| --- | --- |
| `inbox/` | New markdown or JSON jobs. |
| `claimed/` | Atomically claimed jobs before running. |
| `running/` | The currently active job packet. |
| `outbox/` | Result markdown files. |
| `failed/` | Failed job packets preserved for inspection. |
| `archive/` | Completed operational job packets, not permanent research memory. |
| `logs/` | Poller and job logs. |
| `state/` | Poller state, lock files, endpoint records, Hermes runner adapter. |
| `control/` | Future control-plane files. |

The pause file is:

```text
tmp/hermes_mailbox/PAUSE_HERMES.flag
```

If that file exists, the poller exits without claiming new work.

## Job Types

Markdown jobs are instruction packets for Hermes. They should include a small
YAML-like header with a `job_id`, `kind`, priority, endpoints, and expected
result shape, followed by precise instructions.

JSON jobs are deterministic smoke jobs for the poller itself. The tracked
poller currently supports `kind: "shell"` JSON jobs for simple plumbing checks.
Those are not the normal research lane.

Normal research jobs should be markdown packets because Hermes needs to read,
reason, and report, not blindly execute arbitrary model-generated commands.

## Heavy Work Routing

Hermes may use laptop-local LM Studio for light planning. Real Prethinker
semantic compilation, judging, and classifier jobs that require the 35B lane
must use the desktop endpoint:

```text
http://192.168.0.150:1234/v1
```

Job packets should say this explicitly when they ask for heavy work.

## Durable Memory Policy

Keep the durable story in the repo:

- current architecture and research state in `PROJECT_STATE.md`;
- public orientation in `docs/`;
- fixture-specific lessons in fixture `progress_journal.md` and
  `progress_metrics.jsonl`;
- reusable code in tracked scripts and tests.

Keep `tmp/hermes_mailbox` operational. Do not preserve every false start just
because it happened. Old smoke jobs, duplicate cron experiments, stale root
notes, and one-off test packets can be deleted or left to vanish once their
lesson is captured elsewhere.

Retain only the parts that teach how Autolab is built:

- mailbox protocol decisions;
- cron/poller contract changes;
- endpoint/routing decisions;
- job-result summaries that reveal harness behavior;
- design notes that would help future Codex or Hermes continue the work.

Use `prethinker_tmp_archive` for useful retained scratch that should not fill
the repo, and use Git history for source evolution.

## First Bootstrap

The first laptop bootstrap is manual:

1. Codex writes `HERMES_READ_THIS_NEXT.md` and a critical bootstrap job into
   the laptop mailbox.
2. Scott points Hermes at that file once.
3. Hermes pulls `origin/main`, installs the tracked poller into cron, writes a
   bootstrap result to `outbox/`, and removes the pause flag only after smoke
   verification.
4. After that, Codex can queue new jobs by writing mailbox packets.

The first real post-bootstrap job should be tiny and verifiable. Autolab earns
larger autonomy only after the small path is boring.

## Idle And Control

When Codex says Autolab should idle, create `PAUSE_HERMES.flag`. That keeps cron
installed but prevents new job claims.

When the desktop needs the heavy GPU for local work, Autolab jobs should either
pause or run only light laptop-local tasks. Heavy work should never be started
silently while the main lab is using the desktop model.

## Naming

Use **Prethinker Autolab** for the subsystem. It is the harness tester and
research factory: it runs honing jobs, finds material, drafts QA, runs smoke and
regression jobs, and reports results back for Codex to integrate.

The mailbox is plumbing. The repo is memory. Autolab is the loop.

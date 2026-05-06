# Codex Handover - 2026-05-06

This handover is intentionally compact. The old remote-runner notes from this
date were superseded by the Windows direct Autolab model. Treat Git history as
the archive for the retired experiment; treat the files below as live guidance.

## Read First

1. `AGENT-README.md`
2. `PROJECT_STATE.md`
3. `docs/AUTOLAB.md`
4. `docs/AUTOLAB_OPERATING_MODEL.md`
5. `docs/AUTOLAB_WINDOWS_DIRECT.md`
6. `docs/AUTOLAB_AGENT_SKILL_EVOLUTION.md`

## Current Autolab Shape

Autolab is a remote research-support division, not the product and not the
coder. The live worker lane is Windows Python running known repo scripts from
the clone at:

```text
\\192.168.0.103\c\prethinker
```

The useful remote resources are the checkout, Python environment, Task
Scheduler, optional LM Studio endpoint, and shared scratch folders under
ignored `tmp/` paths.

## Current Proof

Direct artifact drill:

```powershell
cd C:\prethinker
.\.venv\Scripts\python.exe scripts\run_autolab_direct_artifact_drill.py --out-dir tmp\autolab_direct_cycles\artifact_drill --include-blocked --include-source
```

Expected validation headline:

```text
Autolab candidate artifact validation
artifacts=2 pass=2 warning=0 fail=0
```

This proves the source-hunter artifact contract without a background chat
worker, WSL, mailbox polling, web access, source-prose interpretation, compile,
query, judge, or promotion.

## Operating Rule

Autolab can queue work and gather evidence. Codex owns interpretation,
instrument changes, promotion decisions, tests, journals, commits, and pushes.

When in doubt, prefer a small deterministic script that writes JSON and a
summary over an instruction packet that merely asks a worker to explain what it
would have done.

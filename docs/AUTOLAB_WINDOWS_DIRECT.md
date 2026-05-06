# Autolab Windows Direct Mode

Last updated: 2026-05-06

## Short Version

Autolab now runs simplest as Windows Python plus repo scripts.

WSL and mailbox polling are not required for the current Autolab loop. Remote
agents can use the clone at `C:\prethinker`, run the same Python scripts Codex
runs locally, and leave artifacts under ignored `tmp/` paths for Codex to
review.

```text
Codex or remote agent
  -> run a bounded repo script with Windows Python
  -> write artifacts under tmp/autolab_direct_cycles/
  -> validate and summarize structured artifacts
  -> Codex reviews, journals, edits, tests, commits, and pushes
```

## Remote Setup

Clone the repo onto the remote Windows machine:

```powershell
cd C:\
git clone https://github.com/dr3d/prethinker.git C:\prethinker
cd C:\prethinker
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip pytest
```

From Codex on the desktop, that clone is visible as:

```text
\\192.168.0.103\c\prethinker
```

## First Proof

Run the direct artifact contract tests:

```powershell
cd C:\prethinker
.\.venv\Scripts\python.exe -m pytest tests/test_run_autolab_direct_artifact_drill.py tests/test_validate_autolab_candidate_artifacts.py tests/test_summarize_autolab_candidate_batch.py -q
```

Run a tiny direct artifact cycle:

```powershell
.\.venv\Scripts\python.exe scripts\run_autolab_direct_artifact_drill.py --out-dir tmp\autolab_direct_cycles\artifact_drill --include-blocked --include-source
```

Expected result:

```text
Autolab candidate artifact validation
artifacts=2 pass=2 warning=0 fail=0
```

This proves the source-hunter artifact contracts without web search, model
calls, WSL, mailbox polling, or source-prose interpretation.

## Windows Cron

Windows cron is Task Scheduler. A minimal recurring tick can run a known safe
script:

```powershell
$Action = New-ScheduledTaskAction `
  -Execute "C:\prethinker\.venv\Scripts\python.exe" `
  -Argument "scripts\run_autolab_direct_artifact_drill.py --out-dir tmp\autolab_direct_cycles\scheduled_tick --include-blocked --include-source" `
  -WorkingDirectory "C:\prethinker"

$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
  -RepetitionInterval (New-TimeSpan -Minutes 15)

Register-ScheduledTask `
  -TaskName "PrethinkerAutolabTick" `
  -Action $Action `
  -Trigger $Trigger `
  -Description "Runs a small direct Autolab artifact cycle without WSL or mailbox polling." `
  -User $env:USERNAME
```

Check or start it:

```powershell
Get-ScheduledTask -TaskName "PrethinkerAutolabTick"
Start-ScheduledTask -TaskName "PrethinkerAutolabTick"
```

Inspect artifacts:

```powershell
Get-ChildItem C:\prethinker\tmp\autolab_direct_cycles\scheduled_tick
Get-Content C:\prethinker\tmp\autolab_direct_cycles\scheduled_tick\manifest.json
```

Disable or remove it:

```powershell
Disable-ScheduledTask -TaskName "PrethinkerAutolabTick"
Unregister-ScheduledTask -TaskName "PrethinkerAutolabTick" -Confirm:$false
```

## Operating Rules

- Prefer known repo scripts over prose instructions to a background agent.
- Keep artifacts under ignored `tmp/autolab_direct_cycles/` unless Codex
  promotes a durable lesson into docs, journals, tests, or datasets.
- Remote agents may run deterministic planners, validators, summarizers, and
  bounded harness scripts with Windows Python.
- Remote agents must not make promotion decisions, edit tracked harness code as
  scratch, or treat local score gains as global wins.
- Heavy model work should be explicitly requested and routed to the selected LM
  Studio endpoint.
- If a recurring task starts producing stale or unhelpful artifacts, disable it
  before adding more automation.

## Retired Runner Note

The retired WSL/mailbox path taught useful lessons about artifact contracts:
stdout claims do not count, files must exist, and validator reports must pass.
Those lessons remain. The machinery is no longer the default.

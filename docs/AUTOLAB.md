# Prethinker Autolab

Last updated: 2026-05-06

## Short Version

Autolab is the research-support division for Prethinker. It lines up bounded
work, runs known scripts, preserves artifacts, and reports what happened.

The current default is Windows direct mode:

```text
Codex chooses a bounded research question
  -> local or remote Windows Python runs a known repo script
  -> artifacts land under ignored tmp paths
  -> validators and summarizers produce structured reports
  -> Codex reviews evidence, updates journals/docs/code, tests, commits, and pushes
```

No standing WSL runner, mailbox poller, or chat loop is required.

## Current Worker Lane

Remote Windows clone:

```text
\\192.168.0.103\c\prethinker
```

Recommended scratch roots:

| Path | Use |
| --- | --- |
| `tmp/autolab_direct_cycles/` | Direct artifact drills and scheduled ticks. |
| `tmp/autolab_mailbox/` | Optional packet staging if a future worker needs a file queue. |
| `tmp/autolab_queue/` | Local queue previews, plans, and disposable status snapshots. |

See [Autolab Windows Direct Mode](https://github.com/dr3d/prethinker/blob/main/docs/AUTOLAB_WINDOWS_DIRECT.md)
for the remote setup, Task Scheduler tick, and first proof command.

## Artifact Discipline

Autolab work only counts when it leaves inspectable files.

Useful outputs include:

- structured JSON reports;
- markdown summaries;
- compile/QA scorecards;
- validation reports;
- fixture/source candidates under ignored staging paths;
- notes that Codex can promote into journals or docs.

Stdout-only success is not success. A blocked source hunt is allowed, but it
must be written as `source_hunt_blocked.json` and pass validation.

## Current Scripts

Direct artifact drill:

```powershell
python scripts/run_autolab_direct_artifact_drill.py --out-dir tmp/autolab_direct_cycles/artifact_drill --include-blocked --include-source
```

Validate candidate artifacts:

```powershell
python scripts/validate_autolab_candidate_artifacts.py --root tmp/autolab_direct_cycles/artifact_drill --out-json tmp/autolab_direct_cycles/artifact_drill/candidate_validation.json
```

Summarize candidate batches:

```powershell
python scripts/summarize_autolab_candidate_batch.py --root tmp/autolab_direct_cycles/artifact_drill --out-md tmp/autolab_direct_cycles/artifact_drill/candidate_summary.md
```

Optional packet-generation helpers remain available for future worker trials:

```powershell
python scripts/autolab_queue_source_hunter_drill.py --drill blocked_report --dry-run
python scripts/autolab_queue_wildbench_pilot.py --source-only --candidate-count 1 --dry-run
python scripts/autolab_queue_next_safe_jobs.py --dry-run
```

Those helpers generate bounded packets and plans. They are not the current
execution requirement.

## Worker Rules

Autolab may:

- run deterministic planners, validators, summarizers, and focused tests;
- run bounded Prethinker compile/QA jobs when explicitly requested;
- collect source candidates and QA drafts as artifacts;
- classify obvious operational failures from structured JSON;
- keep run outputs under ignored `tmp/` paths.

Autolab must not:

- edit tracked harness code as scratch;
- promote a local score gain into a default;
- delete or rewrite research history;
- call a heavy model endpoint unless the job explicitly asks for it;
- run an unbounded chat loop;
- treat prose claims as artifacts.

## Promotion Discipline

A candidate improvement needs evidence before it becomes part of the
instrument:

- target fixture lift;
- no visible exact-row regression;
- transfer check on unrelated fixtures for broad changes;
- named guard, helper, or lens reason;
- durable artifact trail;
- tests proportional to risk.

This is the same pegboard discipline used for semantic lenses: add a new hook
only when the current set cannot expose the meaning surface, and record why the
new hook earned its slot.

## Heavy Work

Desktop LM Studio remains the heavy semantic lane when a run needs model work:

```text
http://192.168.0.150:1234/v1
```

Use explicit scripts with structured outputs and deterministic validators.
Compile once, persist everything, then run cheaper parallax, selector, QA, and
diagnostic passes against frozen artifacts.

## Retired Runner Lesson

The retired WSL/mailbox experiment taught one durable lesson: artifact
contracts matter more than worker chatter. The direct Windows lane keeps the
lesson and removes the baggage.

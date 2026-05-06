# Codex Handover - 2026-05-06

This note is for the next Codex instance starting a fresh conversation with no
thread history. Do not assume the previous conversation exists or can be
resumed. Everything important from the current thread should be captured here
or in the linked repo docs.

It summarizes the current Prethinker state, the Autolab/Hermes work that is
still landing, and the first things to inspect.

## First Read

Start by reading these, in this order:

1. `AGENT-README.md`
2. `PROJECT_STATE.md`
3. `docs/ACTIVE_RESEARCH_LANES.md`
4. `docs/CURRENT_RESEARCH_HEADLINE.md`
5. `docs/AUTOLAB.md`
6. `docs/AUTOLAB_OPERATING_MODEL.md`
7. `docs/AUTOLAB_AGENT_SKILL_EVOLUTION.md`
8. `docs/COMPILED_KB_ARTIFACT_PACKAGE.md`

The user calls Prethinker an instrument. Treat that literally. The harness is
the product: Python orchestrates, validates, admits, queries, scores, and
reports; LLM passes propose semantic workspaces; deterministic admission gates
decide what becomes durable symbolic state.

## Current Verification

As of this handover, full local pytest was:

```text
647 passed
```

The laptop Autolab lane also passed the latest safe batch:

```text
autolab_safe_20260506_pm6_after_wildbench_focused_reporter_tests: 27 passed
autolab_safe_20260506_pm6_after_wildbench_reporter_py_compile: passed
```

Check the repo is still clean before making changes:

```powershell
git status --short
```

## Core Doctrine

Keep these boundaries intact:

- No Python NLP/prose interpretation. Python can orchestrate, parse structured
  JSON, validate, query admitted KBs, compare artifacts, and score. It must not
  infer meaning from natural language prose.
- The compile product is not raw-source RAG. It is a compiled artifact package:
  admitted symbolic facts, epistemic state, helper code, manifest, and
  diagnostics.
- Q&A should answer from compiled artifacts. If the source text is needed at
  query time, that is a compile/artifact design gap.
- Uncertainty must be compiled, not hand-waved. Prefer enumerated epistemic
  states over numeric confidence. Examples: `established`, `claimed`,
  `contested`, `not_established`, `unknown`, `ambiguous`,
  `requires_clarification`.
- A numeric confidence can be a UI/ranking aid later, but the KB should preserve
  named epistemic states with provenance and rationale.
- Autolab/Hermes is not the star and not the architect. It lines up challenges,
  runs bounded chores, drafts candidate artifacts, and reports. Codex improves
  the instrument.

## Recent Commits To Know

Recent pushed commits on `main`:

```text
0894eb5 Document Autolab artifact runner lessons
6afe374 Enforce Autolab markdown artifacts
db2e882 Stage Autolab wildbench source hunting
2ef0f3c Add Autolab wildbench pilot job author
76f2661 Add Autolab candidate artifact validator
e7ce328 Add Autolab safe queue planner
1120f1a Document compiled KB artifact package doctrine
```

## Autolab/Hermes Topology

Laptop:

```text
host: 192.168.0.103
WSL repo: /home/scott/prethinker
Windows mailbox: \\192.168.0.103\c\prethinker\tmp\hermes_mailbox
WSL mailbox: /mnt/c/prethinker/tmp/hermes_mailbox
```

Models:

```text
Laptop local LM Studio: http://127.0.0.1:1234/v1
Desktop heavy LM Studio: http://192.168.0.150:1234/v1
```

Cron on the laptop runs:

```text
scripts/hermes_poll_mailbox.py
```

It processes one job per invocation. `PAUSE_HERMES.flag` in the mailbox root is
the kill switch.

The live mailbox runner adapter is operational state, not tracked repo code:

```text
\\192.168.0.103\c\prethinker\tmp\hermes_mailbox\state\hermes_runner.sh
```

As of this handover, it should use the Hermes `chat` subcommand for markdown
jobs:

```bash
timeout "${HERMES_RUNNER_TIMEOUT_SECONDS:-600}" /home/scott/.local/bin/hermes -z "$(cat "$TMP_PROMPT")" -m "$MODEL" --provider custom --yolo chat
```

This detail matters. Without `chat`, Hermes emitted tool-call-looking text
without actually writing files.

## Current Autolab Scripts

Important tracked helpers:

```text
scripts/hermes_poll_mailbox.py
scripts/autolab_queue_next_safe_jobs.py
scripts/autolab_queue_wildbench_pilot.py
scripts/validate_autolab_candidate_artifacts.py
scripts/summarize_autolab_candidate_batch.py
```

Safe conveyor belt:

```powershell
python scripts/autolab_queue_next_safe_jobs.py --limit 4 --prefix autolab_safe_YYYYMMDD_label
```

Wildbench source hunter:

```powershell
python scripts/autolab_queue_wildbench_pilot.py --source-only --candidate-count 1 --job-id wildbench_source_only_LABEL
```

Candidate validator:

```bash
python scripts/validate_autolab_candidate_artifacts.py --root /mnt/c/prethinker/tmp/hermes_mailbox/runs/<job_id> --out-json /mnt/c/prethinker/tmp/hermes_mailbox/runs/<job_id>/candidate_validation.json
```

Candidate summarizer:

```bash
python scripts/summarize_autolab_candidate_batch.py --root /mnt/c/prethinker/tmp/hermes_mailbox/runs/<job_id> --out-md /mnt/c/prethinker/tmp/hermes_mailbox/runs/<job_id>/candidate_summary.md
```

## What Just Happened With Wildbench

Goal: make Hermes act as a bounded source/domain hunter and QA drafter for
messy real-world material.

Result: useful failure, not success yet.

What worked:

- Safe JSON shell jobs work reliably.
- Laptop `.venv` activation works.
- Laptop can pull GitHub, run focused pytest, py-compile, and generate no-model
  run plans.
- Markdown runner handshakes work.
- With `hermes ... chat`, Hermes can create required artifact files in the
  mailbox.
- The poller now supports `required_artifact:` header lines and fails markdown
  jobs if those files are missing.

What failed usefully:

- First wildbench jobs asked for too much at once: source hunting plus QA.
- Smaller source-only jobs still ran into government-site access issues and
  bot/404 blocks.
- Hermes tended to report blocked-source findings in stdout rather than writing
  the requested files.
- The new poller correctly marks this as failure when required artifacts are
  missing. This is good. Do not weaken that gate.

Most relevant outbox results:

```text
wildbench_source_only_20260506_pm4_chat_result.md
wildbench_source_only_20260506_pm3_result.md
wildbench_source_only_20260506_pm2_result.md
artifact_handshake_20260506_pm2_chat_result.md
autolab_safe_20260506_pm6_after_wildbench_focused_reporter_tests_result.md
autolab_safe_20260506_pm6_after_wildbench_reporter_py_compile_result.md
```

Outbox command from Windows:

```powershell
Get-ChildItem -Path '\\192.168.0.103\c\prethinker\tmp\hermes_mailbox\outbox' |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 20 Name,Length,LastWriteTime
```

Read the latest wildbench failure:

```powershell
Get-Content -Path '\\192.168.0.103\c\prethinker\tmp\hermes_mailbox\outbox\wildbench_source_only_20260506_pm4_chat_result.md'
```

## First Job For The Next Codex

Rendezvous with Hermes output before writing new harness code.

Do this:

1. Check repo state:

   ```powershell
   git status --short
   git log -5 --oneline
   ```

2. Inspect latest Autolab outbox:

   ```powershell
   Get-ChildItem -Path '\\192.168.0.103\c\prethinker\tmp\hermes_mailbox\outbox' |
     Sort-Object LastWriteTime -Descending |
     Select-Object -First 20 Name,Length,LastWriteTime
   ```

3. Read the latest wildbench and PM6 results:

   ```powershell
   Get-Content -Path '\\192.168.0.103\c\prethinker\tmp\hermes_mailbox\outbox\wildbench_source_only_20260506_pm4_chat_result.md'
   Get-Content -Path '\\192.168.0.103\c\prethinker\tmp\hermes_mailbox\outbox\autolab_safe_20260506_pm6_after_wildbench_focused_reporter_tests_result.md'
   Get-Content -Path '\\192.168.0.103\c\prethinker\tmp\hermes_mailbox\outbox\autolab_safe_20260506_pm6_after_wildbench_reporter_py_compile_result.md'
   ```

4. Inspect the run directory for files:

   ```powershell
   Get-ChildItem -Recurse -Path '\\192.168.0.103\c\prethinker\tmp\hermes_mailbox\runs\wildbench_source_only_20260506_pm4_chat' -ErrorAction SilentlyContinue |
     Select-Object FullName,Length,LastWriteTime
   ```

5. Decide whether to queue another source-hunter job. If yes, make it even more
   artifact-first. The next job should probably say:

   - create `wildbench_pilot_summary.md` and `.json` before web search;
   - if web access is blocked, write a blocked report file immediately;
   - do not attempt two candidates;
   - use a source domain likely accessible to the laptop model, perhaps GitHub,
     arXiv, public meeting minutes from simple static pages, or local cached
     material rather than bot-protected federal search pages.

## Suggested Next Autolab Improvement

The next useful harness/Autolab change is probably a dedicated blocked-report
schema. Right now source-hunter jobs require `source.md` and
`source_candidate.json`, but a legitimately blocked web hunt needs a valid way
to say "no candidate produced; here is why."

Possible schema:

```json
{
  "schema_version": "autolab_source_hunt_blocked_v1",
  "job_id": "wildbench_source_only_...",
  "attempted_urls": [
    {"url": "https://...", "failure_mode": "bot_block | 404 | timeout | no_results"}
  ],
  "candidate_count": 0,
  "recommendation": "retry_domain | use_local_cache | reject_hunt"
}
```

Then update `validate_autolab_candidate_artifacts.py` and the wildbench job
writer so a blocked hunt can succeed honestly if, and only if, it writes a
valid blocked report. This is better than asking Hermes to fabricate a source.

## Harness Work Still In Flight

The main research lane before Autolab took focus:

- rule composition;
- semantic parallax;
- cold fixture generalization;
- source-surface acquisition;
- selector risk gating;
- artifact-first orchestration;
- preventing zombie behavior when evidence is inadequate.

Current-harness replay results from earlier today:

```text
Avalon: 34 exact / 2 partial / 4 miss
Oxalis: 36 / 4 / 0
Three Moles: 27 / 4 / 9
combined: 97 / 10 / 13
write proposals: 0
runtime errors: 0
```

Rejected probes matter:

- Three Moles broad micro-detail prompt regressed to `16 / 9 / 15`.
- Oxalis cleaner recall/regulatory hint regressed to `24 / 11 / 5`.
- Avalon governance/rationale variant had a two-mode upper bound of `36 / 2 / 2`
  but global regression to `25 / 8 / 7`, so keep that row-gated only.

Do not add lenses casually. The user is worried about hyper-refinement. New
lenses/guards should have a named reason for being and transfer evidence.

## Epistemic State Note

The user explicitly prefers enumerated epistemic values over numbers. Preserve
this.

Good shape:

```prolog
epistemic_state(claim_id, established, support_ref, reason_ref).
epistemic_state(claim_id, contested, support_ref, reason_ref).
epistemic_state(claim_id, not_established, support_ref, reason_ref).
epistemic_state(claim_id, requires_clarification, support_ref, reason_ref).
```

Avoid making the KB depend on fake precision like:

```text
confidence = 0.63
```

Numbers can be UI/supporting metadata later. The symbolic KB should preserve
auditable named states.

## Current Product Understanding

Prethinker freezes behavior as a governed compiler/harness, not as an
open-ended researcher. At freeze time, it should:

- compile natural language sources into durable symbolic artifacts;
- preserve epistemic state, not only facts;
- answer Q&A from the compiled artifact package;
- ask for clarification only when compiled ambiguity/absence supports that;
- stop or refuse gracefully when evidence is insufficient;
- be hard to fool and smart about not being stupid.

Autolab is subordinate to that. It is a sample feeder and sensor array, not the
instrument itself.

## Tone And Collaboration

The user wants forward motion without babysitting, but also wants careful
research memory. Push useful changes to GitHub. Journal important findings.
When something fails, name the failure and turn it into a sharper guardrail.

Failures beget creations. Creations earn their names. Names earn their slots.

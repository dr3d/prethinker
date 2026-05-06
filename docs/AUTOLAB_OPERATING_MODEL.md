# Prethinker Autolab Operating Model

Last updated: 2026-05-06

## The Short Version

Prethinker Autolab is a research division inside the Prethinker lab: the group
that lines up challenges, runs bounded experiments, and reports what broke.

Hermes and its possible subagents are the non-coding research staff on the
laptop. Prethinker does governed semantic compilation and QA through the heavy
workhorse model. Codex reviews the evidence, changes the harness, updates the
durable record, and pushes the repo.

```text
Autolab lines up challenges.
Prethinker produces governed artifacts.
Codex improves the instrument.
```

## Why This Exists

Curated fixtures proved that the Prethinker architecture can work. The next
question is whether the harness generalizes when it sees more documents, more
failure shapes, and more awkward semantic surfaces than one person can manually
feed it.

Autolab is the answer to that throughput problem. It keeps the boring but
useful experimental loop running:

1. gather or receive material;
2. prepare bounded fixture/QA jobs;
3. compile source into a KB through Prethinker;
4. query and score the KB;
5. classify failures;
6. write artifacts and summaries;
7. let Codex decide what the results mean.

This is not model fine-tuning. The model weights are frozen. The thing being
trained is the context-engineering instrument: lenses, selector guards, query
helpers, admission policies, repair gates, and documentation.

## The Division Of Labor

| Actor | Job |
| --- | --- |
| Autolab | Research division. Organizes challenge hunting, fixture farming, QA drafting, scoring runs, summaries, and artifact flow. |
| Hermes | Worker/research coordinator. Runs bounded mailbox jobs and may delegate to specialized subagents when the job benefits from separate roles. |
| Finder subagents | Hunt for source material, fixture candidates, domain surfaces, and useful challenge shapes. |
| QA subagents | Draft candidate questions, answer expectations, and coverage rosters as artifacts for later scoring and review. |
| Grader/diagnostic subagents | Summarize scores, classify operational failures, and cluster failure signals without changing harness code. |
| Prethinker | Semantic engine. Uses LLM calls to propose structured semantic workspaces, then deterministic Python admits, rejects, queries, and scores. |
| Desktop LM Studio | Heavy semantic lane for Prethinker compile, QA, judging, and classification jobs; currently the 35B workhorse. |
| Laptop LM Studio | Light Hermes control-plane lane. It should follow instructions, not architect the project. |
| Codex | Code-master, lab lead, and instrument engineer. Reads results, detects patterns, changes harness code, updates docs/journals, runs tests, commits, and pushes. |
| GitHub | Durable source history and recovery line. |
| Mailbox | Operational queue and scratch space, not the permanent research record. |

The Autolab researchers can be capable. They may need to understand what kind
of source surface is being hunted, what makes a good hostile QA row, or what
kind of failure signal is worth surfacing. But they are not the coders. The
small model should not be asked to redesign the compiler, invent global lenses,
or silently edit tracked harness files. It should do small, observable jobs and
stop.

## Research Roles

Autolab can grow specialized roles as the work becomes clearer:

| Role | Hunts For | Output |
| --- | --- | --- |
| Source finder | Real documents with rules, dates, entities, corrections, claims, thresholds, and exceptions. | Clean source packet plus provenance notes. |
| Domain scout | Repeated domain patterns that might stress profiles or lens coverage. | Domain surface brief and fixture candidate list. |
| Fixture builder | Source-to-fixture packaging and metadata alignment. | Staged fixture folder or intake packet. |
| QA drafter | Questions that expose direct facts, authority, temporal state, counterfactuals, absences, and rule composition. | Candidate QA battery and coverage notes. |
| Grader | Score summaries and artifact rollups. | Outbox report with exact/partial/miss counts and failure surfaces. |
| Failure scout | Cross-run patterns such as compile gaps, query gaps, selector risks, and zombie loops. | Pattern report for Codex review. |

These roles are allowed to line up better challenges. They are not allowed to
promote harness behavior. Promotion remains a Codex decision backed by tests,
scorecards, transfer checks, and repo docs.

## The Research Loop

```text
Codex writes a job packet
  -> cron wakes the laptop
  -> scripts/hermes_poll_mailbox.py claims one job
  -> Hermes runs local light work or calls Prethinker commands
  -> heavy Prethinker calls route to http://192.168.0.150:1234/v1
  -> artifacts are written under tmp/hermes_mailbox/runs/
  -> a result summary lands in tmp/hermes_mailbox/outbox/
  -> Codex reviews, journals durable lessons, and changes the harness if warranted
```

The loop is artifact-first. Compile once, persist everything, then run many
cheap parallax, selector, QA, and diagnostic passes against frozen artifacts.
That turns the GPU from one big thinker into a small research factory.

## What Hermes May Do

Autolab researchers can safely do work like this:

- run no-model smoke checks;
- pull `origin/main` when explicitly asked;
- run bounded Prethinker compile/QA jobs;
- generate candidate QA batteries as draft artifacts;
- harvest source material into staging areas;
- summarize run artifacts into outbox reports;
- classify obvious operational failures;
- keep the four LM Studio lanes busy when Codex has queued a batch.

Hermes should prefer one-shot mode, currently:

```bash
hermes -z "<bounded prompt>"
```

For Qwen-family control-plane prompts, prepend the mailbox state prefix:

```text
/no_think
```

The no-think switch is only for Hermes orchestration. It is not a Prethinker
semantic prompt policy.

## What Hermes Must Not Do

Hermes should not:

- run a persistent chat loop as the worker;
- process the same inbox file repeatedly;
- edit tracked repo code as scratch;
- redesign `kb_pipeline`, selectors, lenses, or admission policy on its own;
- decide that a local score gain is a global promotion;
- delete or rewrite research history;
- call the heavy desktop endpoint unless the job packet explicitly asks for it;
- keep going when `PAUSE_HERMES.flag` exists.

If Hermes finds a possible improvement, the output should be a report or a
small proposed patch scope, not a silent architecture change.

## What Codex Does With Results

Codex is responsible for judgment.

When Autolab produces failures, Codex looks for patterns:

- Did the compiler miss source surface?
- Did the query planner ask the wrong predicate shape?
- Did a selector choose a tempting but unsafe surface?
- Did a lens help one fixture but regress another?
- Is this a real transferable repair family or just local noise?

Then Codex runs focused experiments, changes code, updates tests, records the
lesson, and commits only changes that belong in the instrument.

## Promotion Discipline

Autolab can produce lots of candidates. Most should not become defaults.

A candidate improvement needs evidence:

- target fixture lift;
- no visible exact-row regression;
- transfer check on unrelated fixtures when the change is broad;
- named guard or reason for being;
- durable artifact trail;
- test coverage proportional to risk.

This protects Prethinker from becoming overfit to the latest fixture or the
latest model's favorite phrasing.

## The First Heavy-Lane Proof

The first successful laptop-to-desktop heavy orchestration was:

```text
job_id: 0014_fenmore_heavy_smoke
fixture: fenmore_seedbank
desktop endpoint: http://192.168.0.150:1234/v1
compile: parsed, 16 admitted facts, 0 skipped
QA limit: 3 rows
score: 1 exact / 0 partial / 2 miss
write proposals: 0
runtime load errors: 0
```

The result was useful because it proved both sides of the system:

- Autolab routed a real heavy Prethinker job through the laptop control plane.
- The fixture exposed a real harness signal: compile surface acquisition only
  captured the first two Fenmore accessions, so early QA rows immediately found
  missing source coverage.

That is the intended shape. Autolab should produce real signals, not just green
toy checks.

Follow-up job `0016_fenmore_shaped_compile_smoke` proved the caution that
Autolab smoke runs are not automatically score comparisons. A shaped
flat-plus-focused compile admitted `94` rows and scored `2 / 1 / 2` over the
first five QA rows, still below the archived promoted cold baseline with `195`
admitted rows and `20 / 1 / 4` full-25. Treat bounded smoke packets as
orchestration or diagnostic artifacts unless the job explicitly reproduces the
promoted run shape.

## Working Metaphor

Prethinker is the instrument.

Autolab is the sample feeder and sensor array.

Hermes is the lab assistant who can keep loading samples and writing down
measurements.

Codex tunes the instrument.

The point is not to make Hermes brilliant. The point is to make the whole lab
hard to fool, hard to derail, and good at noticing when meaning has not yet
been captured.

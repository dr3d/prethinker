# Prethinker Autolab Operating Model

Last updated: 2026-05-06

## The Short Version

Prethinker Autolab is a research division inside the Prethinker lab: the group
that lines up challenges, runs bounded experiments, and reports what broke.

Current Autolab does not require WSL or mailbox polling. Codex can run useful research
cycles directly, and remote agents can run the same repo scripts through
Windows Python when they are available. Prethinker does governed semantic
compilation and QA through the heavy workhorse model when needed. Codex reviews
the evidence, changes the harness, updates the durable record, and pushes the
repo.

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

For the emerging source-hunter and QA-drafter role design, see
[Autolab Agent Skill Evolution](https://github.com/dr3d/prethinker/blob/main/docs/AUTOLAB_AGENT_SKILL_EVOLUTION.md).
For the current remote Windows setup, see
[Autolab Windows Direct Mode](https://github.com/dr3d/prethinker/blob/main/docs/AUTOLAB_WINDOWS_DIRECT.md).

## The Division Of Labor

| Actor | Job |
| --- | --- |
| Autolab | Research division. Organizes challenge hunting, fixture farming, QA drafting, scoring runs, summaries, and artifact flow. |
| Direct scripts | Current worker lane for no-model planning, artifact drills, validation, summarization, and focused verification through local or remote Windows Python. |
| Finder role | Hunt for source material, fixture candidates, domain surfaces, and useful challenge shapes. This can be Codex-driven until a background worker earns its keep. |
| QA role | Draft candidate questions, answer expectations, and coverage rosters as artifacts for later scoring and review. |
| Grader/diagnostic role | Summarize scores, classify operational failures, compare structured run artifacts, and cluster failure signals without changing harness code. |
| Prethinker | Semantic engine. Uses LLM calls to propose structured semantic workspaces, then deterministic Python admits, rejects, queries, and scores. |
| Desktop LM Studio | Heavy semantic lane for Prethinker compile, QA, judging, and classification jobs; currently the 35B workhorse. |
| Remote Windows Python | Optional direct execution lane for known repo scripts, without WSL or mailbox polling. |
| Remote LM Studio | Optional model endpoint/compute resource. |
| Codex | Code-master, lab lead, and instrument engineer. Reads results, detects patterns, changes harness code, updates docs/journals, runs tests, commits, and pushes. |
| GitHub | Durable source history and recovery line. |
| Legacy mailbox | Historical queue/scratch experiment, not the permanent research record and not currently required. |

The Autolab researchers can be capable. They may need to understand what kind
of source surface is being hunted, what makes a good hostile QA row, or what
kind of failure signal is worth surfacing. But they are not the coders. The
small model should not be asked to redesign the compiler, invent global lenses,
or silently edit tracked harness files. It should do small, observable jobs and
stop.

## Research Roles

Autolab can grow specialized roles as the work becomes clearer:

These roles are planned operating shapes. The current pilot uses direct Codex
cycles and deterministic scripts until repeated failure surfaces justify a
background worker or specialized agent role.

The same discipline applies to agents that applies to lenses: failures beget
creations, creations earn their names, and names earn permanent slots only
after they prove useful across more than one local accident.

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
Codex chooses a bounded research question
  -> local or remote Windows Python runs planners, validators, compile/QA, or artifact drills
  -> heavy Prethinker calls can route to http://192.168.0.150:1234/v1
  -> artifacts are written under ignored tmp paths
  -> Codex reviews, journals durable lessons, and changes the harness if warranted
```

The loop is artifact-first. Compile once, persist everything, then run many
cheap parallax, selector, QA, and diagnostic passes against frozen artifacts.
That turns the GPU from one big thinker into a small research factory.

## Direct Worker Rules

Autolab cycles can safely do work like this:

- run no-model smoke checks;
- run bounded Prethinker compile/QA jobs;
- generate candidate QA batteries as draft artifacts;
- harvest source material into staging areas;
- summarize run artifacts into outbox reports from structured JSON, including compile/QA comparison reports;
- classify obvious operational failures;
- keep the four LM Studio lanes busy when Codex has queued a batch.

When a cycle needs model work, prefer explicit scripts with structured JSON
outputs and deterministic validators. Avoid prose-only file production. If a
background worker is reintroduced later, it must prove file discipline through
the same validators before doing open-ended hunting.

## What Autolab Must Not Do

Autolab should not:

- run a persistent chat loop as the worker;
- process the same inbox file repeatedly;
- edit tracked repo code as scratch;
- redesign `kb_pipeline`, selectors, lenses, or admission policy on its own;
- decide that a local score gain is a global promotion;
- delete or rewrite research history;
- call the heavy desktop endpoint unless the run explicitly asks for it.

If a cycle finds a possible improvement, the output should be a report or a
small proposed patch scope. Codex decides whether to change the harness.

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

`scripts/compare_domain_bootstrap_compiles.py` is the first dedicated Autolab
run-reporter helper. It compares compile and QA JSON artifacts structurally:
admitted rows, skipped rows, unique facts, candidate predicate rosters, fact
predicate counts, compile health, focus predicate counts, and QA judge
summaries. It does not read source prose or make semantic claims. This is the
right boundary for any Autolab worker: report instrument surfaces, then stop.

`scripts/rollup_domain_bootstrap_qa_scorecard.py` is the matching judged-QA
batch reporter. It reads only QA JSON artifacts and reports exact/partial/miss
counts, failure-surface counts, runtime errors, write proposals, and copied
non-exact row metadata. This gives Autolab a deterministic "how did the batch
score?" tool before any human or model interpretation.

## Working Metaphor

Prethinker is the instrument.

Autolab is the sample feeder and sensor array.

Windows Python scripts are the current loading bench: boring, inspectable, and
easy to replace.

Codex tunes the instrument.

The point is not to make a background agent brilliant. The point is to make the
whole lab hard to fool, hard to derail, and good at noticing when meaning has
not yet been captured.

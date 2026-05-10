# Benchmark Publication Plan

Last updated: 2026-05-09

This plan turns the existing fixture corpus into a public benchmark without
turning the report into advocacy for Prethinker. Prethinker should appear as
one evaluated system beside frontier LLM baselines and hosted/local variants.
Where frontier LLMs do better, the publication should say so plainly.

The controlling rule is data first, design second. Do not curate the public
benchmark, write the paper, or build the site until the same fixture rows have
been scored against frontier LLMs.

## Publication Principle

The benchmark should measure source-fidelity and meaning-depth resolution under
pressure:

```text
source fixture
  -> sealed question surface
  -> system response or compiled-state answer
  -> reference scoring
  -> row-level verdict and failure surface
```

Do not compare unlike evidence lanes as if they are the same result. Cold
source-only runs, assisted profile runs, selector-gated repair runs, and
diagnostic upper bounds answer different questions.

The deeper research frame is not "Prethinker beats frontier LLMs." It is:

```text
How finely can different systems distinguish structurally different meanings?
```

A model that separates `claim` from `finding` but collapses `withdrawn claim`,
`disputed claim`, and `unadopted claim` has lower meaning-depth resolution than
a model that preserves those states. The hostile fixtures are probes for that
resolution. Per-category and paired-question breakdowns matter more than a
single aggregate score.

This plan now sits inside the two-axis benchmark frame:

- **Axis 1: what gets through the door** - compile-time fidelity and
  single-document meaning preservation.
- **Axis 2: what stays in the room** - retention durability under stuffed
  context, cross-document interference, and long-context load.

See [Two-Axis Benchmark Frame](https://github.com/dr3d/prethinker/blob/main/docs/TWO_AXIS_BENCHMARK_FRAME.md)
and [Two-Axis Probe Discipline](https://github.com/dr3d/prethinker/blob/main/docs/TWO_AXIS_PROBE_DISCIPLINE.md).
Do not present Axis 2 as methodology until the minimal stuffed-context probe has
produced data.

The strategic positioning around edge-governed systems lives in
[Edge Governance Positioning](https://github.com/dr3d/prethinker/blob/main/docs/EDGE_GOVERNANCE_POSITIONING.md).
Benchmark work should distinguish frontier cloud, edge governed, and edge
ungoverned system classes without turning positioning into methodology.

## Corpus Readiness

Use the generated corpus manifest as the publication denominator:

```powershell
python scripts/benchmarking/build_public_benchmark_manifest.py `
  --out-json tmp/public_benchmark/corpus_manifest.json `
  --out-md tmp/public_benchmark/corpus_manifest.md
```

Current local inventory:

- `55` story/source fixture directories.
- `40` fixtures are structurally ready with source, question surface, scoring
  oracle, and scored history.
- `15` fixtures have scored progress history but should not enter a public
  leaderboard until their public scoring-oracle boundary is explicit.
- The ready subset currently exposes `1523` oracle rows.

The public release should name the exact manifest JSON SHA and publish the
fixture inclusion list. Private answer files may remain audit artifacts, but
they must not be used in compile or question-planning context.

## Phase 1: Data Audit

First answer one question:

```text
For each candidate fixture, how do frontier LLMs score on the same rows?
```

Run a quick comparison scan before organizing the whole corpus. The first scan
should cover about `10` fixtures across distinct pressure types, then expand if
the signal is healthy. Use direct source-plus-question prompts first: no
Prethinker compile, no fixture-internal strategy notes, no answer-shaped hints.

The comparison table should include:

| Column | Meaning |
| --- | --- |
| `fixture` | Fixture slug. |
| `question_id` | Stable row id. |
| `category` | Oracle/category label when available. |
| `prethinker_score` | Existing or rerun Prethinker verdict in the same row schema. |
| `frontier_model_scores` | One verdict per frontier model. |
| `frontier_average` | Average exact/partial score over the frontier baseline models. |
| `prethinker_minus_frontier_average` | Direction and size of the gap. |
| `notes` | Parse/refusal/scoring caveats. |

This table is the foundation. It tells us which fixtures differentiate, which
are parity checks, and where frontier LLMs are better.

The scratch plan named GPT-5, Claude Opus 4.6, and Gemini 3.1 Pro as the first
frontier scan targets. Treat those as intended comparison families, not frozen
model ids. Verify exact provider model ids and availability when the run config
is created.

## Phase 2: Fairness Audit

Cluster fixtures by measured outcome after the frontier scan:

| Bucket | Gap | Publication Use |
| --- | ---: | --- |
| Prethinker dominates | `> 30` points | Include if methodology is clean. |
| Prethinker leads | `10-30` points | Include as meaningful differentiation. |
| Roughly tied | `< 10` points | Include; these make the benchmark credible. |
| Frontier LLMs lead | negative gap | Include some; these are honest limits. |

The tied and frontier-led buckets are not embarrassments. They are what keeps
the benchmark from looking like a Prethinker-shaped obstacle course.

The result narrative should be:

```text
This benchmark measures meaning-depth resolution. Frontier models show jagged
resolution: they preserve some subtle distinctions and flatten others. The
pattern of flattening is the finding.
```

Report both:

- capability comparison: which system answered correctly;
- resolution analysis: which semantic distinction was preserved or flattened.

## Phase 3: Curation And Rework

Do not publish all ready fixtures as the main benchmark. Publish a smaller,
cleaner `10-15` fixture corpus and keep the rest as supplementary calibration.
Select by measured diversity, not by Prethinker win rate.

For each candidate public fixture:

- strip Prethinker-internal lens, guard, selector, or family terminology from
  public-facing notes;
- standardize `fixture_notes`, strategy, and anti-leakage format;
- verify every oracle answer is unambiguous;
- cut ambiguous questions instead of repairing them during scoring;
- remove diagnostic leakage that was useful internally but inappropriate for a
  public benchmark;
- preserve fixture admission timestamps and relevant architecture-change
  timestamps when available.

The strongest anti-contamination evidence is outside-authored or isolated-author
fixtures that Prethinker has never been calibrated against. Add a small number
of those after the first scan if the publication needs a cleaner cold slice.

## Phase 4: Methodology Paper

The paper should be a benchmark paper, not a product pitch:

1. What is measured: meaning-depth resolution, meaning preservation, source
   envelopes, epistemic state, authority, temporal/status, rule and exception
   handling.
2. Why existing benchmarks leave this gap: they usually measure task success,
   hallucination, coding, or time horizon rather than meaning flattening under
   document pressure.
3. Failure taxonomy: categories discovered empirically from rows and fixtures.
4. Fixture authorship methodology: role separation, sealed oracles,
   anti-leakage manifests, strategy declarations, outside submissions.
5. Scoring methodology: exact/partial/miss, abstention, per-category analysis,
   scorer calibration, adjudication policy.
6. Results: frontier LLMs and Prethinker, including parity and losses, with
   per-category resolution patterns.
7. Limitations: sample size, English-only assumptions, synthetic-source limits,
   model/provider drift, possible calibration effects.
8. Open questions: what the benchmark still cannot measure.

## Phase 5: Public Infrastructure

Keep the first public infrastructure simple:

- static site or docs hub;
- per-fixture pages with source document, question battery, categories, and
  public scoring policy;
- downloadable corpus package and manifest;
- leaderboard by fixture and category;
- raw/normalized outputs for evaluated systems;
- clear license;
- documented submission process for external systems and adversarial fixture
  proposals;
- methodology paper PDF.

The infrastructure should make it cheap for others to run evaluations. If the
benchmark requires Prethinker-specific setup to evaluate a non-Prethinker
system, the publication has failed its own fairness test.

## Evidence Lanes

Report at least these lanes separately:

| Lane | What It Measures | Public Use |
| --- | --- | --- |
| `frontier_llm_closed_book` | Frontier model answers from source plus question, no Prethinker compile. | Primary model baseline. |
| `frontier_llm_structured` | Frontier model asked for concise answer plus evidence citation/abstention JSON. | Tests whether structured prompting narrows failures. |
| `prethinker_cold_unseen` | Source-only Prethinker compile, then QA from compiled artifact. | Main Prethinker baseline. |
| `prethinker_model_transfer_cold` | Same as cold unseen, but hosted/model-transfer endpoint. | Portability baseline. |
| `prethinker_selector_gated` | Frozen artifacts plus row-level selector/guard policy. | Product-style diagnostic lane, not cold discovery. |
| `diagnostic_upper_bound` | Best row among available artifacts after the fact. | Ceiling analysis only. |

The paper should never rank `diagnostic_upper_bound` above cold frontier LLMs
as if both systems had the same information.

For the direct LLM pilot, every raw model gets the identical prompt contract and
run settings. Prethinker compiled-system results are a separate system lane:
they may be compared as benchmark results, but the paper must say plainly that
the internal path is not the same as raw source-plus-question prompting. If the
underlying Prethinker development model is included as a raw model, it must run
through the same direct runner as GPT/Claude/Gemini-style baselines.

## First-Week Action

Run the frontier comparison pilot before any further curation. Pick `10`
fixtures across the corpus:

- two surgical fixtures;
- two story-world/state-tracking fixtures;
- two self-authored or sealed submission-style fixtures;
- two Claude 8 dense operational-record fixtures;
- two precision-batch fixtures.

Score each row with the same exact/partial/miss rubric used for Prethinker. If
the pattern shows differentiation, parity, and some losses, the benchmark is
publishable. If every selected row makes Prethinker win by a huge margin, pause
and investigate whether the corpus or scoring setup is biased.

The immediate output should be a CSV/JSONL comparison table, not a paper draft.

Current planner command:

```powershell
python scripts/benchmarking/plan_benchmark_frontier_pilot.py `
  --manifest-json tmp/public_benchmark/corpus_manifest.json `
  --out-json tmp/public_benchmark/frontier_pilot_plan.json `
  --out-md tmp/public_benchmark/frontier_pilot_plan.md
```

Current pilot shape:

- `10` fixtures.
- `370` planned rows.
- `3` repeated runs per model.
- `3` frontier model families.
- `3330` expected model calls before retries.
- default model ids verified against the OpenRouter catalog on 2026-05-09:
  `openai/gpt-5.5`, `anthropic/claude-opus-4.7`, and
  `google/gemini-3.1-pro-preview`.

Current direct-runner command shape:

```powershell
python scripts/benchmarking/run_frontier_direct_qa.py `
  --plan-json tmp/public_benchmark/frontier_pilot_plan.json `
  --model <exact-provider-model-id> `
  --provider <provider-name> `
  --base-url <openai-compatible-base-url> `
  --api-key-env <ENV_VAR_WITH_KEY> `
  --out-dir tmp/public_benchmark/frontier_direct_outputs
```

The runner records run-level raw answers. It does not read `oracle.jsonl`, does
not include fixture strategy notes, and does not score rows. Scoring should be a
separate common-judge pass that applies the same exact/partial/miss rubric to
all direct model outputs.

Current rollup command:

```powershell
python scripts/benchmarking/summarize_frontier_direct_pilot.py `
  --scored-dir tmp/public_benchmark/frontier_direct_scored `
  --out-json tmp/public_benchmark/frontier_direct_rollup.json `
  --out-md tmp/public_benchmark/frontier_direct_rollup.md `
  --out-csv tmp/public_benchmark/frontier_direct_rollup_rows.csv
```

The rollup must report both micro row-weighted rates and macro fixture-averaged
rates. Fenmore and Greywell have `25` rows while most pilot fixtures have `40`,
so a single exact-count total is not enough.

## Model Matrix

The initial model matrix should include:

- one OpenAI frontier model;
- one Anthropic frontier model;
- one Google frontier model;
- one open or hosted open-weight model available through OpenRouter or another
  OpenAI-compatible endpoint;
- Prethinker over the current local research model;
- Prethinker over a hosted transfer endpoint.

For each model, record provider, exact model id, date, temperature, max tokens,
structured-output mode, retries, and refusal/parse policy. If a provider updates
an aliased model, start a new result row instead of silently overwriting the old
one.

## Scoring

Primary row labels:

- `exact`: answer matches the reference answer without material loss.
- `partial`: answer contains the key support but misses a qualifier, scope,
  date, authority boundary, or final-state distinction.
- `miss`: wrong, unsupported, contradictory, or failed to answer.
- `abstain`: explicit uncertainty or inability to answer.
- `invalid`: parse/runtime failure.

Secondary failure surfaces:

- compile or extraction gap;
- query/retrieval gap;
- hybrid join gap;
- answer formatting gap;
- authority/claim/finding collapse;
- temporal/status gap;
- identifier/provenance gap;
- rule/executable-condition gap.

Frontier LLM baselines should receive the same row labels, but their failure
surfaces should be described as answer-behavior labels, not Prethinker-internal
compile gaps.

## Minimum Publication Artifacts

Publish these artifacts together:

- corpus manifest JSON and Markdown;
- fixture inclusion list and per-fixture row counts;
- prompt templates for every model lane;
- raw model outputs or normalized answer JSON;
- scored row verdict JSONL;
- aggregate scorecard by fixture, lane, and model;
- bootstrap confidence intervals for exact rate and exact+partial rate;
- failure-surface rollup;
- leakage policy and evidence-lane declarations;
- limitations section naming where Prethinker underperforms direct frontier
  models.

## Recommended First Public Slice

Draw the public slice from the `40` manifest-ready fixtures rather than all
`55`. This avoids mixing public oracles with historical/internal scoring
boundaries. Keep the main release to `10-15` fixtures and choose a stratified
slice by measured pressure and fairness bucket:

- operational records and source provenance;
- authority and claim/finding separation;
- temporal/status change;
- local rules and exceptions;
- narrative final-state tracking;
- identifier and custody precision.

Freeze that inclusion list after the frontier comparison pilot and before the
final benchmark run.

## Operator Flow

1. Build the corpus manifest.
2. Select a `10` fixture frontier pilot before publication curation.
3. Freeze the pilot run config with model ids, prompts, scoring policy, retry
   policy, and cost cap.
4. Run direct frontier LLM baselines from source plus question only.
5. Align or rerun Prethinker cold lanes on the same rows.
6. Score all rows into one normalized verdict schema.
7. Cluster fixtures into fairness buckets.
8. Curate the `10-15` fixture public corpus from the measured buckets.
9. Run final benchmark lanes and hosted transfer lanes separately.
10. Produce aggregate tables, failure rollups, and limitations.
11. Write the public report with negative results first-class.

## Current Blockers

- No `OPENROUTER_API_KEY`, `PRETHINKER_API_KEY`, or `OPENAI_API_KEY` is present
  in this workspace session, so new hosted frontier evaluations cannot be run
  from this turn.
- The local LM Studio endpoint on `127.0.0.1:1234` is reachable, so local
  Prethinker/lab-model runs can proceed when a concrete fixture/model plan is
  selected.
- Several historically important fixtures have progress rows but no public
  `oracle.jsonl`; keep them out of leaderboard claims until the scoring asset is
  made publication-safe.

## Report Stance

The strongest public story is not "Prethinker beats frontier LLMs." The honest
story is narrower and more durable: a governed compiled-state instrument can
make certain classes of source fidelity, authority separation, and failure
analysis auditable; frontier LLMs may still be stronger direct answerers on
many rows, especially where symbolic admission has not preserved the needed
surface.

## Openness Policy

The benchmark should welcome adversarial submissions. Other teams should be
able to contribute fixtures designed to make Prethinker fail. If those fixtures
expose failures, that is valuable field data. If Prethinker holds up, that is
also stronger evidence than a closed self-authored benchmark.

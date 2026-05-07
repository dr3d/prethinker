# Portability And Model Transfer

Last updated: 2026-05-06

Prethinker should become portable. The current POWER/NITRO rig is a research
machine, not the product.

The product is the governed instrument:

```text
language proposes
admission governs
state records
artifacts persist
transfer is measured
```

The long-term bar is simple: someone should be able to clone the repo, install
dependencies, point the lab at a capable model endpoint, and run a small
truth-and-meaning research cycle without owning this home lab. A high-school
student with a laptop and model tokens should eventually be able to farm a
fixture, compile it into an inspectable artifact, ask hard questions, and see
where the instrument was exact, partial, wrong, or wisely uncertain.

## What Should Travel

These parts are meant to work on someone else's computer:

- repo scripts with explicit model and endpoint settings;
- fixture corpora in markdown, JSONL, and JSON;
- compiled KB artifact packages: Prolog clauses, manifests, diagnostics, and
  helper files;
- deterministic selector guards, validators, scorecards, and comparison tools;
- the lens roster as a semantic vocabulary, not a hardware assumption;
- Autolab artifact discipline: run bounded jobs, write structured outputs, then
  let Codex or a human interpret the results.

The home lab can be faster and more comfortable, but it should not become the
definition of Prethinker.

## What Is Rig-Coupled Today

Some current notes are deliberately local:

- POWER is the current 35B workhorse lane.
- NITRO is the current 8GB sidecar lane.
- LM Studio endpoint behavior, `/v1` URL normalization, `n_ctx` failures, and
  `reasoning_content` quirks are local backend notes, not system requirements.
- The strongest fixture results are calibrated against the current
  `qwen/qwen3.6-35b-a3b` lane.

Those facts are useful operational history. They should not harden into product
architecture.

## Model Coupling Risk

The current instrument has been sharpened through many runs on one specific
model family. That creates a real backward-tuning risk: some lessons may be
semantic discoveries, while some may be Qwen-shaped repair knobs.

Likely transferable:

- the governance boundary;
- compiled KB artifact shape;
- uncertainty vocabulary;
- selector guard families;
- semantic facets and failure surfaces;
- cross-fixture replay discipline.

Likely model-coupled:

- pass sizes and operation budgets;
- compact versus full workspace choices;
- evidence-clause budgets;
- retry triggers and max-token habits;
- structured-output quirks such as `reasoning_content`;
- temperature, thinking, and context-window assumptions.

The answer is not to guess which is which. The answer is to measure.

## Future Evidence Lane: `model_transfer_cold`

Do not make OpenRouter or any other hosted provider a dependency until
Prethinker is strong enough locally to make the transfer test meaningful.

When that time comes, add an explicit `model_transfer_cold` lane:

1. choose a small fixture trio with different difficulty:
   - Fenmore Seedbank as a currently strong/perfect fixture;
   - Meridian Permit Board as a rule/authority fixture with known gains;
   - Three Moles as a frontier narrative fixture;
2. run the same compile and QA scripts against the new backend;
3. compare parse validity, exact/partial/miss counts, write proposals, failure
   surfaces, latency, cost, and context behavior;
4. record score deltas as backend transfer evidence, not as ordinary
   regressions;
5. recalibrate only the contingent parameters that move, while protecting the
   semantic and admission invariants.

Suggested first-pass smoke expectations are qualitative, not promotion gates:
Fenmore should remain recognizably strong, Meridian should retain meaningful
rule/authority signal, and Three Moles should still expose frontier narrative
weakness rather than collapsing into noise.

## Hosted Endpoint Horizon

The likely public-product lane is a hosted OpenAI-compatible provider such as
OpenRouter, but that is future infrastructure work.

Before treating hosted transfer as operational, verify:

- all relevant runners can pass an API key without hardcoding secrets;
- structured JSON-schema output behaves as required;
- model names, context windows, token limits, and reasoning controls are known;
- latency and cost are acceptable for fixture-scale runs;
- transfer scores are close enough to POWER's 35B lane to trust the hosted
  backend as the public instrument.

The eventual someone-else's-computer test is simple:

```text
clone repo
install dependencies
set endpoint/API-key configuration
compile one fixture
run QA against the compiled artifact
compare the scorecard to local evidence
```

Until then, keep building on the rig while keeping endpoint assumptions visible
and measured.

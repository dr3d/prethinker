# Portability And Model Transfer

Last updated: 2026-05-09

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
- bounded artifact discipline: run scoped jobs, write structured outputs, then
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

OpenRouter transfer has now started. The first meaningful evidence lane is not
just endpoint smoke; it separates operational portability, cold compile
portability, lens-output drift, and selector portability.

The first-pass endpoint test established:

- the hosted endpoint accepts strict JSON-schema output;
- `qwen/qwen3.6-35b-a3b` is available with a large context window;
- API-key plumbing now works for compile, QA, and selector runners;
- reasoning can be disabled for the structured-output lane;
- governance held across the first `545` OpenRouter QA rows: no write
  proposals and no runtime load errors;
- parser stability was good, with one failed QA parse in the initial broad run.

The first broad transfer run showed that cold OpenRouter is a usable baseline
lane, but not a drop-in replacement for the repaired POWER lane. Across the
initial scan it reached `310 exact / 51 partial / 184 miss` over `545` rows.
The dense Claude-8 batch landed at `157 / 34 / 129` over `320` rows, while the
local repaired selector lane had already reached `273 / 20 / 27` on that same
batch.

## Lens Output Drift

The key portability lesson is subtle:

```text
lens definitions travel
lens outputs drift
admission still governs
selectors must be transfer-calibrated
```

The same lens prompt and predicate contracts can produce different admitted
surfaces on POWER and OpenRouter, even under the same public model name. This
does not break the architecture. It means the portable unit is the governed
instrument, not a promise of byte-identical workspaces.

Examples from the first repair-stack transfer probe:

| Fixture | Surface | POWER | OpenRouter |
|---|---:|---:|---:|
| `hospital_shift_exception_log` | cold | `13 / 3 / 24` | `17 / 2 / 21` |
| `hospital_shift_exception_log` | source-record v2 | `32 / 0 / 8` | `24 / 4 / 12` |
| `hospital_shift_exception_log` | archival row ledger | `35 / 0 / 5` | `16 / 1 / 23` |
| `estate_archive_access_dispute` | cold | `21 / 9 / 10` | `18 / 4 / 18` |
| `estate_archive_access_dispute` | source-record v2 | `29 / 5 / 6` | `11 / 5 / 24` |
| `estate_archive_access_dispute` | archival row ledger | `36 / 3 / 1` | `26 / 2 / 12` |

The names of the lenses transferred. The exact emitted workspace did not.

## Selector-Aware Transfer

The important follow-up was selector-aware transfer. On OpenRouter artifacts,
the first guarded selector moved:

- Hospital from cold `17 / 2 / 21` to `27 / 1 / 12`;
- Estate from cold `18 / 4 / 18` to `29 / 2 / 9`.

After adding narrow row-shape guards for the OpenRouter missed-best rows, the
same artifacts replayed at:

- Hospital `31 / 2 / 7`, against an available upper bound of `32 / 3 / 5`;
- Estate `34 / 2 / 4`, against an available upper bound of `35 / 3 / 2`.

The selector-aware sweep now covers all eight dense operational fixtures without
using POWER and without adding new candidate types:

| Fixture | Cold OpenRouter | Source-Record v2 | Archival Row Ledger | Guarded Selector | Available Upper Bound |
|---|---:|---:|---:|---:|---:|
| `hospital_shift_exception_log` | `17 / 2 / 21` | `24 / 4 / 12` | `16 / 1 / 23` | `31 / 2 / 7` | `32 / 3 / 5` |
| `estate_archive_access_dispute` | `18 / 4 / 18` | `11 / 5 / 24` | `26 / 2 / 12` | `34 / 2 / 4` | `35 / 3 / 2` |
| `wildfire_evacuation_revision_order` | `26 / 2 / 12` | `23 / 2 / 15` | `20 / 3 / 17` | `35 / 2 / 3` | `36 / 2 / 2` |
| `university_lab_sample_chain` | `13 / 0 / 27` | `20 / 3 / 17` | `20 / 2 / 18` | `29 / 3 / 8` | `29 / 3 / 8` |
| `arts_grant_panel_reconsideration` | `22 / 8 / 10` | `31 / 6 / 3` | `28 / 3 / 9` | `36 / 3 / 1` | `37 / 3 / 0` |
| `maritime_salvage_sensor_packet` | `18 / 6 / 16` | `33 / 2 / 5` | `26 / 3 / 11` | `38 / 1 / 1` | `38 / 1 / 1` |
| `municipal_tree_permit_amendment` | `22 / 6 / 12` | `26 / 3 / 11` | `28 / 5 / 7` | `38 / 1 / 1` | `38 / 1 / 1` |
| `school_trip_bus_roster_split` | `21 / 6 / 13` | `27 / 1 / 11` | `20 / 2 / 18` | `33 / 3 / 4` | `33 / 3 / 4` |

Across the dense eight, cold OpenRouter totaled `157 / 34 / 129`. The guarded
selector over OpenRouter artifacts reached `274 / 17 / 29` out of `320`
(`85.62%` exact), with zero selector errors. The available upper bound from the
same artifacts is `278 / 19 / 23`.

That is at parity with the local POWER repaired lane (`273 / 20 / 27`) by exact
count, though POWER kept more partial rows. It came at a visible cost: guard
pressure rose to `197` return sites and `197` unique guard reasons. The family
count still held at `7` with `0` unclassified, but the rollup correctly reports
enumeration pressure as `warn`. This is useful evidence, not decoration:
OpenRouter can reproduce the dense-record repair lane when the selector is
transfer-calibrated, while the guard ledger now makes the complexity cost
explicit.

The residual selector gap is now small and concentrated:

| Fixture | Selector Gap To Available Upper Bound | Readout |
|---|---:|---|
| `university_lab_sample_chain` | `0` | selector saturated available surface |
| `municipal_tree_permit_amendment` | `0` | selector saturated available surface |
| `school_trip_bus_roster_split` | `0` | selector saturated available surface |
| `hospital_shift_exception_log` | `1` | one timeline/source-authority row remains |
| `estate_archive_access_dispute` | `1` | possession/location boundary remains |
| `wildfire_evacuation_revision_order` | `1` | road-jurisdiction/layer boundary remains |
| `arts_grant_panel_reconsideration` | `1` | resulting-average/helper row remains |
| `maritime_salvage_sensor_packet` | `0` | selector saturated available surface |

This argues against immediately adding more fixtures. The next bounded work is
guard accounting and helper pressure: classify the new transfer guards as
transfer, candidate, or scar; retire any selector branches made unnecessary by
better helper/query surfaces; and avoid adding another guard wave unless a row
names a semantic failure rather than a fixture accident.

That is the practical migration story as of 2026-05-09: OpenRouter can do real
research work, but high-water claims require selector-aware repair lanes and
transfer-calibrated guards. Cold hosted compile alone is a baseline collector,
not the product-grade instrument.

## Sensitivity Matrix

Hosted transfer is also a diagnostic instrument. Provider variance can reveal
which parts of Prethinker are robust semantic structure and which parts depend
on a particular model/runtime behavior.

The working classification is:

- Low sensitivity: broad cold skeletons, source-envelope distinctions,
  authority hierarchy, procedural versus decisional boundaries, and ordinary
  conflict surfacing.
- Moderate sensitivity: source-record status tracking, rule activation
  surfaces, temporal intervals, correction provenance, and selector decisions.
- High sensitivity: exact string preservation, printed labels, exhibit IDs,
  catalog IDs, row labels, long-tail entity recognition, and subtle status
  distinctions such as unadopted versus unsupported.

The first measured examples:

| Fixture | Surface | POWER | OpenRouter | Variance Class |
|---|---:|---:|---:|---|
| `hospital_shift_exception_log` | cold | `13` exact | `17` exact | low |
| `hospital_shift_exception_log` | source-record v2 | `32` exact | `24` exact | moderate |
| `hospital_shift_exception_log` | archival row ledger | `35` exact | `16` exact | high |
| `estate_archive_access_dispute` | cold | `21` exact | `18` exact | low |
| `estate_archive_access_dispute` | source-record v2 | `29` exact | `11` exact | high |
| `estate_archive_access_dispute` | archival row ledger | `36` exact | `26` exact | moderate/high |

The architectural response is not to hide the variance. It is to choose the
right reinforcement:

- Hardy lenses can remain mostly prompt-and-contract driven.
- Moderate lenses should carry calibration metadata by backend/model/provider.
- Sensitive lenses should get deterministic side channels, stricter validation,
  or cross-provider checks.

The archival identifier pinboard is the pattern for sensitive surfaces. Exact
printed strings live partly at the lexical layer, so deterministic extraction
before the LLM can be more portable than asking every backend to preserve those
strings through generation.

Future transfer reports should include a sensitivity row for each lens or
candidate mode. A score delta is not only a regression; it is evidence about
which semantic surfaces are durable and which need architectural support.

The same principle applies to selector guards. Hosted transfer can reveal
whether a guard is portable doctrine or local scar tissue. New guard instances
should be recorded in the
[selector guard ledger](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_LEDGER.md)
and audited under the discipline in
[SELECTOR_GUARD_AUDIT_DISCIPLINE.md](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_AUDIT_DISCIPLINE.md).

## Hosted Endpoint Horizon

The likely public-product lane is a hosted OpenAI-compatible provider such as
OpenRouter, but it must stay measured rather than assumed.

Before treating hosted transfer as a default lane, verify:

- all relevant runners can pass an API key without hardcoding secrets;
- structured JSON-schema output behaves as required;
- model names, context windows, token limits, and reasoning controls are known;
- latency and cost are acceptable for fixture-scale runs;
- selector-aware transfer scores are close enough to POWER's repaired 35B lane
  to trust the hosted backend as the public instrument.

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

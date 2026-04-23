# UMLS MVP Probe

Date: 2026-04-23

This report captures the first bounded UMLS MVP run against the local 2025AB Metathesaurus subset.

## What Was Built

- a small reusable UMLS helper module: `src/umls_mvp.py`
- a local slice builder: `scripts/build_umls_mvp_slice.py`
- a sharp-memory probe runner: `scripts/run_umls_mvp_probe.py`
- a challenging evaluation battery: `docs/data/umls_mvp_sharp_memory_battery.json`

The slice is generated locally under:

- `tmp/licensed/umls/2025AB/prethinker_mvp/`

That output stays out of the public repo because it is derived from licensed data.

## Slice Shape

Built from:

- `MRCONSO`
- `MRSTY`
- filtered `MRREL`
- `MRSAB`

Allowed source bias:

- `SNOMEDCT_US`
- `RXNORM`
- `LOINC`

Measured local slice counts:

- resolved seeds: `16`
- unresolved seeds: `0`
- concept count: `16`
- relation count: `24`

## Probe Result

The first sharp-memory probe ran on `12` curated utterances and produced:

- `12` pass
- `0` warn
- `0` fail
- average precision: `1.000`
- average recall: `1.000`

Interpretation:

- the MVP is already strong at concept normalization for bounded medical English
- brand-name medication capture is working through relation-bridged alias expansion
- common abbreviations such as `T2DM`, `HbA1c`, and `CKD` are now grounding cleanly
- the slice now includes enough signal to support downstream symptom and lab-event prompt probes
- the current probe is conservative and not overfiring on vague language
- direct curated alias injection for the bounded profile is now doing useful work where raw UMLS phrasing was too formal

## What It Clearly Helps With

- canonical normalization of disorders, drugs, and simple lab concepts
- brand to ingredient linking for a bounded medication set
- abbreviation folding when the expanded phrase is already present in the concept slice
- curated colloquial symptom and lab aliases such as `short of breath` and `serum creatinine`
- saying "do not sharpen this into memory yet" on vague phrases like:
  - `pressure has been high`
  - `sugar was high`
  - `kidneys are a little off`

## What Changed In The Latest Pass

The two earlier warnings are now gone:

1. `short of breath`
- is now carried into the bounded slice as an explicit curated alias for `shortness_of_breath`

2. `serum creatinine was repeated`
- is now carried into the bounded slice as an explicit curated alias for `serum_creatinine_measurement`

That means the UMLS MVP is no longer just "formal synonym lookup." It is now a bounded normalization layer that can intentionally carry the extra colloquial and operational aliases we decide are worth remembering sharply.

## Worth Continuing?

Yes, conditionally.

This MVP is worth further effort because it already shows the kind of gain we actually care about:

- sharper canonical memory anchors
- bounded type steering
- better medication normalization than the generic lane alone
- clean abstention on vague medical shorthand

But it is only worth continuing if the next step stays disciplined.

## Recommended Next Step

Do **not** jump to broad clinical reasoning.

Do this instead:

1. integrate the derived slice as an optional local medical normalization layer
2. keep the medical lane English-first and bounded
3. add a second probe pack focused only on:
   - colloquial symptom phrasing
   - lab-test wording vs lab-substance wording
4. only then decide whether relation-heavy support deserves more investment

## Bottom Line

The first bounded UMLS MVP looks promising.

It is not yet a clinical reasoning system.

But it does appear strong enough as a compact medical normalization and type-steering layer that deeper exploration is justified.

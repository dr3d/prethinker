# UMLS MVP

Date: 2026-04-23

This note turns the newly staged UMLS 2025AB Metathesaurus data into a concrete go/no-go plan for Prethinker.

The goal is not "load all of UMLS into the KB."

The goal is to answer one narrower question:

**Does a small, disciplined UMLS-backed medical lane materially improve Prethinker's medical language handling enough to justify further effort?**

## What We Have Now

Local licensed data now exists under:

- `tmp/licensed/umls/2025AB/META/`

Key tables present:

- `MRCONSO.RRF`
- `MRREL.RRF`
- `MRSTY.RRF`
- `MRDEF.RRF`
- `MRSAB.RRF`
- `MRDOC.RRF`
- `MRFILES.RRF`
- `MRCOLS.RRF`

Important clarification:

- there is only one extracted `MRCONSO.RRF` in the working tree
- the other copy is inside the compressed archive `tmp/umls-2025AB-metathesaurus-full.zip`
- so there is no duplicate extracted `MRCONSO.RRF` to delete right now

## Current Status

The first bounded MVP is now built locally.

- slice builder: `scripts/build_umls_mvp_slice.py`
- probe runner: `scripts/run_umls_mvp_probe.py`
- ontology prospector runner: `scripts/run_medical_ontology_prospector.py`
- challenge battery: `docs/data/umls_mvp_sharp_memory_battery.json`
- ontology prospector corpus: `docs/data/medical_ontology_prospector_corpus.json`
- formal profile note: [docs/MEDICAL_PROFILE.md](MEDICAL_PROFILE.md)
- dated result: [docs/reports/UMLS_MVP_PROBE_2026-04-23.md](docs/reports/UMLS_MVP_PROBE_2026-04-23.md)
- clinical checks probe: `scripts/run_umls_mvp_clinical_probe.py`
- medical prompt probe: [docs/reports/MEDICAL_PROMPT_PROBE_2026-04-23.md](docs/reports/MEDICAL_PROMPT_PROBE_2026-04-23.md)
- medical clarification probe: [docs/reports/MEDICAL_CLARIFICATION_PROBE_2026-04-23.md](docs/reports/MEDICAL_CLARIFICATION_PROBE_2026-04-23.md)
- local ontology mining note: [docs/ONTOLOGY_PROSPECTOR.md](ONTOLOGY_PROSPECTOR.md)

Current measured result on the first local probe:

- `16` resolved seeds
- `12` challenge cases
- `12` pass
- `0` warn
- `0` fail

That is enough to justify continued bounded exploration.

We also now have a first prompt-shaping and clarification stack:

- clinical checks probe: `7/7` pass, `0/7` warn, `0/7` fail
- medical prompt probe: `79/79` vs baseline `58/79`
- clarification-aware prompt probe: `38/38` vs baseline `21/38`
- ontology prospector run: `9` candidate predicates across `20` cases, all inside the existing bounded palette

Those probes show:

- the bounded medical supplement improves grounded medical normalization
- clarification materially improves vague shorthand and pronoun-led medical turns
- the bounded slice now captures the intended colloquial/lab aliases cleanly enough for the sharp-memory and clinical checks batteries to stay fully green
- a small deterministic medical-profile guard is worthwhile for keeping unresolved-patient turns empty until clarification lands
- the larger local model is converging toward the existing compact medical predicate set instead of inventing lots of lexicalized one-off predicates

## What "Worth It" Would Mean

UMLS is worth deeper investment only if it gives us leverage in areas the current general lane does not already handle well.

For this repo, the leverage would need to show up in at least one of these:

1. Better concept normalization
- map medical surface forms to stable concept identifiers or canonical names
- reduce synonym drift and spelling/alias confusion

2. Better type steering
- know whether a term is a drug, disorder, finding, procedure, lab concept, anatomy concept, etc.
- use that to reduce predicate misuse and unsafe argument drift

3. Better constrained medical retrieval
- support a small medical query lane with deterministic answers grounded in a compact extracted slice

4. Better medical interrogation scores
- improve a constrained medical test pack more than a generic parser/profile alone

If it only gives us "a giant synonym table" without meaningful gains on actual governed compilation, it is probably not worth the operational weight.

## What Would Make It Not Worth It

UMLS is probably not worth deeper effort if the MVP shows any of these:

- improvements are mostly lexical lookup and do not materially improve compile/admit behavior
- relation graph complexity is too high for a disciplined first lane
- extracting and curating a safe subset costs more than the medical lane is likely to return
- a smaller hand-built medical registry/profile gives most of the same gains

## The Right MVP Shape

The MVP should stay small and English-first.

It should not try to become a universal clinical reasoning engine.

### Scope

Use only a constrained slice built from:

- `MRCONSO`
- `MRSTY`
- filtered `MRREL`
- source metadata from `MRSAB`

### Suggested Source Vocabulary Bias

Start by favoring a short whitelist, not the whole metathesaurus:

- `SNOMEDCT_US`
- `RXNORM`
- `LOINC`
- possibly one diagnosis code family if needed later

Do not begin with every source vocabulary.

## MVP Deliverables

### 1. Slice builder

Build a small extracted slice, for example:

- `tmp/licensed/umls/2025AB/prethinker_mvp/`
- `concepts.jsonl`
- `names.jsonl`
- `semantic_types.jsonl`
- `relations.jsonl`

This slice should be:

- English-only at first
- source-whitelisted
- concept-count bounded
- relation-type bounded

### 2. Medical profile

Create a first explicit medical profile, something like:

- `medical@v0`

It should define:

- allowed predicate families
- type hints
- normalization preferences
- relation subsets we trust enough to use

### 3. Small medical scenario pack

Make a tiny, honest pack focused on what the slice is supposed to help with:

- synonym normalization
- drug/finding/disorder typing
- very constrained relation retrieval

Do not start with open-ended diagnosis or treatment reasoning.

### 4. Medical interrogator pack

Use the existing interrogator framing, but keep the questions narrow:

- concept recognition
- semantic type match
- simple relation lookup
- simple contraindication-style checks only if relation support is real

## The Minimal MVP Questions

The MVP should answer these five questions:

1. Can we normalize common medical surface forms into stable concepts better than the generic lane?
2. Can we attach useful semantic types without flooding the runtime with ontology weight?
3. Can we answer a small class of constrained medical queries deterministically?
4. Can we show measurable improvement on a tiny medical evaluation pack?
5. Can we do all of that without making the rest of the system messier than it is worth?

## Go / No-Go Criteria

### Go

Continue if the MVP demonstrates all of these:

- a compact extracted slice is easy to regenerate
- medical normalization clearly improves on a fixed tiny pack
- semantic type steering is usable in deterministic validation
- the lane stays bounded and explainable

### No-Go

Stop if any of these dominate:

- relation extraction becomes graph-heavy and hard to audit
- gains are mostly cosmetic synonym improvements
- maintenance burden is high relative to measured benefit
- a hand-authored medical profile gets nearly the same result with much less weight

## Recommended First Build

The first build should **not** use all of `MRREL`.

Recommended first pass:

1. inventory `MRSAB`
2. choose a short source whitelist
3. extract English preferred names and aliases from `MRCONSO`
4. attach semantic types from `MRSTY`
5. delay relation import until the concept/type slice proves useful

That gives us a lower-risk first answer:

**Is UMLS worth it even just as a concept normalization and type-steering layer?**

If the answer is no, we stop there.

If the answer is yes, then we add a tightly filtered relation layer.

## Storage Guidance

For now:

- keep the full zip as the canonical local source archive
- keep the extracted `META` folder as the working raw source
- do not commit licensed UMLS data into the public repo

If we later generate a tiny derived slice, we should decide separately whether that slice is safe and appropriate to keep in-repo.

## Recommendation

Yes, a UMLS MVP is worth doing.

But only as a bounded experiment:

- concept normalization first
- type steering second
- constrained relation support only if the first two clearly pay off

Current recommendation after the latest probes:

- keep the shared SP as the constitutional layer
- keep the medical supplement as a profile/wrapper layer
- continue pushing the clarification-aware medical lane
- use the local ontology prospector to mine candidate canonical predicates before promoting anything into a formal `medical@v0` registry
- move next toward a formal `medical@v0` package built around the reinforced nine-predicate palette
- do not market this as general clinical reasoning

That is the cleanest way to learn whether the medical lane deserves real investment without turning the repo into a giant ontology ingestion project.

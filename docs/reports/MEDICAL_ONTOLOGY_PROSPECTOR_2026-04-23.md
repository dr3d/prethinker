# Medical Ontology Prospector

Date: 2026-04-23

This report captures the first local run of the offline medical ontology prospector against a larger local model.

Model:

- `qwen3.5:27b`
- local Ollama
- `32768` context
- `temperature=0.2`
- `think_enabled=true`

Corpus:

- [docs/data/medical_ontology_prospector_corpus.json](../data/medical_ontology_prospector_corpus.json)
- `20` bounded medical cases
- direct medical facts
- clarified shorthand
- pronoun-led cases

## Top-Line Result

Convergence was strong:

- total cases: `20`
- unique candidate predicates: `9`
- predicate/case ratio: `0.45`
- multi-case predicates: `7`
- single-case predicates: `2`
- existing palette hits: `9`

That is a good outcome.

It means the larger local model did **not** explode into a bag of lexicalized one-off predicates.

Instead, it converged on the existing bounded palette.

## Candidate Predicate Set

The run reinforced this compact medical set:

- `taking/2`
- `pregnant/1`
- `underwent_lab_test/2`
- `lab_result_rising/2`
- `has_condition/2`
- `lab_result_high/2`
- `has_symptom/2`
- `has_allergy/2`
- `lab_result_abnormal/2`

Notably:

- `taking/2` had support across `7` cases
- lab/event/result predicates converged cleanly instead of collapsing into phrase predicates
- no new predicate outside the existing palette earned durable multi-case support

## What The Model Rejected

The prospector explicitly rejected lexical junk like:

- `taking_coumadin`
- `taking_metformin`
- `creatinine_repeated`
- `hba1c_climbed`
- `has_high_blood_pressure`
- `high_pressure/1`
- `sugar_high/1`
- `kidneys_off/1`

That is exactly what we wanted to see.

It suggests the ontology-mining frame is good:

- use the larger model offline
- let it scan broader medical language
- demand that it compress toward stable relation shapes

## Interpretation

This run gives us a real answer:

- the evolving medical ontology probably **is** packageable
- the current bounded predicate palette is already close to the right `medical@v0` shape
- the next effort should go into:
  - argument/type normalization
  - clarification behavior
  - formal profile packaging

not into inventing lots of new predicates.

## Recommendation

The strongest next move is:

1. formalize a tracked `medical@v0` registry/profile around this nine-predicate set
2. keep using the local ontology prospector as an offline review tool
3. continue using clarification to rescue pronoun-led and shorthand medical turns
4. treat raw UMLS and local prospector outputs as source material, not runtime truth

## Bottom Line

This looks like real ontology signal, not just 27B cleverness.

The larger model converged on a compact reusable predicate set and rejected the exact kinds of lexical predicate sprawl we were worried about.

# Python Guardrail Audit

Last updated: 2026-04-26

## Purpose

This document separates two things that have both been called "guardrails":

1. **Authority guardrails**: deterministic checks that protect the KB boundary.
2. **Semantic rescue patches**: Python code that tries to repair or reinterpret language after the model emits a weak parse.

The new semantic IR direction should not weaken the authority boundary. It should reduce the second category. The goal is not "less safety." The goal is less English-specific Python doing semantic interpretation that a stronger model should do better.

## Short Take

The Python we probably keep is the boring, crucial part:

- JSON/schema validation
- predicate registry admission
- type/profile checks
- medical safety rejection
- Prolog parsing, mutation, query, and evidence logging
- structured trace/provenance
- deterministic mapping from semantic IR to allowed operations

The Python we should try to delete or demote is the clever, brittle part:

- pronoun and possessive rewrites
- family-bundle expansion
- subject-prefixed predicate canonicalization
- route fallback realignment
- story-specific observation guards
- query phrase canonicalizers
- medical clarification rescues that inspect English phrases directly

The semantic IR path gives us a cleaner target:

```text
utterance + context
  -> LLM semantic workspace proposal
  -> structural mapper
  -> authority gate
  -> KB mutation/query/clarification/quarantine/reject
```

Python should validate and execute the proposal. It should not keep learning English one special case at a time.

## Current Guardrail Classes

| Class | Current examples | Why it exists | Keep? | Semantic IR replacement |
| --- | --- | --- | --- | --- |
| Schema and shape validation | `kb_pipeline._validate_parsed`, semantic IR schema checks | Prevent malformed model output from reaching the runtime | Keep | Structured output plus local validation |
| Predicate registry admission | `kb_pipeline._validate_parsed_against_registry`, `src.mcp_server._load_registry_signatures` | Stop invented predicates from becoming durable state | Keep | Same check, applied after IR mapping |
| Type/domain validation | `kb_pipeline._validate_parsed_types`, medical profile signatures | Prevent wrong arity/type writes | Keep | Same check, applied to candidate operations |
| Medical safety and advice rejection | semantic IR `reject` policy, `medical@v0` profile checks | Avoid treating advice, dosing, or treatment as KB writes | Keep | Stronger model classifies unsafe intent; Python enforces |
| Deterministic runtime execution | `src.mcp_server._apply_compiled_parse` | The model must not directly mutate state | Keep | Same runtime, cleaner input |
| Provenance and trace | parse/prethink traces, operation logs | Make mutation decisions inspectable | Keep | Expand trace with guardrail-kind events |
| Entity/term normalization | retract aliases like `crate12`/`crate_12` | Smooth syntax atoms without changing meaning | Keep narrowly | Move to structural mapper, not English rescue |
| Clarification policy | uncertainty, missing slots, context resolution | Decide when not enough is known to write | Keep, simplify | IR emits missing slots and candidate questions |
| English semantic rescue | possessive/family/pronoun rewrites, route fallbacks | Patch weak model parses for known tests | Delete/demote | LLM emits referents/assertions/candidate operations directly |
| Scenario-specific salvage | "observed someone", "three bears", chair/bed/break guards | Preserve old story pack behavior | Delete or quarantine in legacy mode | Harder scenario batteries should pass through IR |

## Specific Deletion/Demotion Candidates

These are not all bad code. Many were reasonable at the time. The problem is that they encode language understanding in Python, which is exactly the layer we now want the 35B semantic compiler to own.

### Runtime UI Path

- `src/mcp_server.py::_canonicalize_subject_prefixed_predicates`
  - **Why it exists**: older model outputs created predicates like `hope_lives_in(...)` when the subject should have been an argument.
  - **Concern**: Python is repairing semantic role structure.
  - **Replacement**: IR should emit `relation_concept=residence_location` plus `candidate_operations=[lives_in(hope, ...)]`.
  - **Disposition**: demote behind `legacy_rescue_policy=full`; remove after replay passes.

- `src/mcp_server.py::_canonicalize_make_with_query`
  - **Why it exists**: special phrasing around "made with" queries.
  - **Concern**: phrase-level English query interpretation in runtime code.
  - **Replacement**: IR emits `operation=query`, predicate, and open variables.
  - **Disposition**: deletion candidate.

- `src/mcp_server.py::_augment_compound_family_facts`
  - **Why it exists**: expands family utterances into multiple relation facts.
  - **Concern**: Python is deciding the semantic graph.
  - **Replacement**: IR assertions should carry all direct family relations and mark inferred relations separately.
  - **Disposition**: deletion candidate after family battery replay.

- `src/mcp_server.py::_process_utterance_with_possessive_family_bundle_normalization`
  - **Why it exists**: rewrites possessive family phrasing before the main pipeline.
  - **Concern**: pre-parse language rewriting is hard to audit and can change meaning.
  - **Replacement**: IR referents/assertions.
  - **Disposition**: high-priority deletion candidate.

- `src/mcp_server.py::_process_utterance_with_same_clause_spouse_normalization`
  - **Why it exists**: repairs same-clause spouse phrasing for older tests.
  - **Concern**: very test-shaped semantic patch.
  - **Replacement**: IR event/relation extraction.
  - **Disposition**: high-priority deletion candidate.

- `src/mcp_server.py::_process_utterance_with_family_anchor_pronoun_normalization`
  - **Why it exists**: repairs pronouns anchored by family mentions in the same utterance.
  - **Concern**: coreference should be a first-class IR field, not a string rewrite.
  - **Replacement**: `referents[]` with `resolved|ambiguous|unresolved`.
  - **Disposition**: high-priority deletion candidate.

### Medical Profile Path

- `src/medical_profile.py::sanitize_medical_parse_for_clarification`
  - **Why it exists**: blocks unresolved patient pronouns from becoming facts.
  - **Keep?** Partly.
  - **Concern**: the safety goal is right, but phrase handling should come from IR referents.
  - **Replacement**: keep a structural rule: no patient identity, no write. Remove English pronoun text handling once IR is stable.

- `src/medical_profile.py::sanitize_medical_parse_for_bridge`
  - **Why it exists**: UMLS bridge catches vague or incompatible medical concepts.
  - **Keep?** Mostly.
  - **Concern**: vague surface forms like "pressure" and "sugar" are English-specific.
  - **Replacement**: LLM should surface ambiguity; UMLS bridge should validate concept type.

- `src/medical_profile.py::rescue_medical_clarified_lab_result`
  - **Why it exists**: patches the "Mara's pressure is bad" / "blood pressure reading was high" flow into `lab_result_high(...)`.
  - **Concern**: this is exactly the kind of brittle repair the semantic workspace should make unnecessary.
  - **Replacement**: IR should combine pending clarification and answer into a safe direct write.
  - **Disposition**: high-priority deletion candidate after the medical clarification battery passes.

### Batch/Research Pipeline

`kb_pipeline.py` contains the largest legacy rescue surface. It has durable checks we should keep, but it also has many guard functions named after story shapes:

- `_apply_possessive_break_guard`
- `_apply_possessive_bed_target_guard`
- `_apply_observed_someone_event_guard`
- `_apply_observed_sat_possessive_chair_guard`
- `_apply_observed_possessive_broken_guard`
- `_apply_three_bears_observation_guard`
- `_apply_group_returned_home_guard`
- `_apply_narrative_fact_normalization_guard`
- `_apply_narrative_rule_normalization_guard`
- `_apply_registry_fact_salvage_guard`
- `_build_route_fallback_parse`

These are useful as historical evidence of where the old design struggled. They are also the clearest sign that the system was trending toward a pile of semantic patches.

The likely endpoint is:

- keep `kb_pipeline.py` as a legacy benchmark harness and comparison path;
- move active runtime experiments to semantic IR;
- replay the old packs with legacy rescue off;
- delete or isolate story-specific rescue once semantic IR reaches equal or better results.

## What "Less Python" Should Mean

We should not measure success by deleting random lines. We should measure it by moving semantic responsibility to the right layer.

Good Python to keep:

- "Is this object valid JSON with the expected schema?"
- "Is this predicate allowed?"
- "Do the arguments match the profile?"
- "Is this a safe direct write, a query, a correction, or a rejected medical advice request?"
- "Can this operation be executed deterministically?"
- "What trace proves why the runtime admitted or blocked this?"

Python to reduce:

- "When English says X, rewrite it to Y."
- "If this particular story phrasing appears, patch the predicate."
- "If the model guessed a weird predicate, infer what it meant."
- "If a clarification answer contains these words, synthesize a fact."
- "If this possessive phrase appears, split it into a family bundle."

## Proposed Experiment

Add a runtime/research knob:

```text
legacy_rescue_policy = full | structural_only | off
```

Definitions:

- `full`: current behavior, including English/story-specific rescues.
- `structural_only`: schema, registry, type, safety, execution, provenance, and atom-level normalization only.
- `off`: semantic IR output is validated and mapped with minimal rescue; failures are exposed.

Then replay scenario packs through three paths:

```text
legacy 9B + full rescue
semantic_ir 35B + full rescue
semantic_ir 35B + structural_only
```

Track:

- bad commits
- missed safe commits
- unnecessary clarifications
- blocked/rejected unsafe turns
- number of rescue events invoked
- final KB state equivalence
- query answer equivalence
- trace clarity

The win condition is not merely "35B gets more right." The win condition is:

```text
semantic_ir 35B + structural_only >= legacy full rescue
```

with fewer English-specific intervention events.

## First-Pass Estimate

The obvious deletion/demotion target is not a tiny cleanup. A first pass identifies:

- several runtime UI rescue hooks in `src/mcp_server.py`;
- three medical-profile rescue/sanitizer paths that should become structural IR checks;
- dozens of batch-pipeline guard functions in `kb_pipeline.py`, including many scenario-shaped patches.

The realistic near-term goal is to make those paths optional and measurable, not to delete them blind. If the structural-only semantic IR path holds up against the batteries, the project can likely retire hundreds to low-thousands of lines of semantic rescue code over a few focused passes.

## Latest Evidence

The first LM Studio structured-output runtime pass strengthens the case:

- edge battery: semantic IR 17/20 decision OK, 0.930 average score;
- weak-edge battery: semantic IR 10/10 decision OK, 1.000 average score;
- semantic path used zero English/story rescue hooks in those runs;
- remaining interventions were structural mapper/projection events.

This is exactly the kind of Python we want to keep for now: schema-backed
projection, safe operation mapping, hypothetical query handling, duplicate
unsafe-implication cleanup, and claim/direct-observation decision projection.
Those rules do not parse English phrases. They enforce the semantic workspace
contract after the model has done the language understanding.

## Immediate Next Steps

1. Add structured guardrail event labels:
   - `authority_schema`
   - `authority_registry`
   - `authority_type`
   - `authority_safety`
   - `structural_mapper`
   - `semantic_rescue_english`
   - `semantic_rescue_story`
   - `legacy_route_fallback`

2. Add `legacy_rescue_policy` to the runtime/bakeoff harness.

3. Build small batteries around deletion candidates:
   - possessive/family/pronoun
   - medical clarification carry-forward
   - corrections and retracts
   - open-variable queries
   - glitch/airlock temporal state
   - ledger/lease/inheritance temporal story

4. Run a deletion A/B:
   - current full rescue
   - semantic IR with full rescue
   - semantic IR with structural-only rescue

5. Keep only the guardrails whose "why" is durable:
   - safety
   - admissibility
   - executable syntax
   - provenance
   - explicit domain policy

Everything else should have to earn its place with evidence.

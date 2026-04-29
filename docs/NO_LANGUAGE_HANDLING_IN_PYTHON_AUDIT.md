# No Language Handling In Python Audit

Last updated: 2026-04-28

## Working Rule

Prethinker should treat this as a research constraint:

> No language handling in Python.

Python may transport text, store text, count budgets, validate JSON, validate predicate contracts, retrieve KB context, and execute/admit symbolic operations. Python should not decide what an utterance means.

The practical version is not "Python never touches a string." It is:

```text
Python may handle structure.
The LLM should handle language.
The mapper should handle authority.
```

## What Is Allowed To Stay In Python

These are structural/governance operations, not semantic language interpretation:

- JSON schema validation for `semantic_ir_v1`.
- Predicate palette enforcement and arity/argument-contract checks.
- KB clause parsing, Prolog execution, unification, query execution, and truth-maintenance application.
- Context packing after the model or deterministic KB retrieval has selected what to include.
- Token/character budgeting, truncation, trace rendering, and UI presentation.
- Refusing unsafe candidate operations based on structured fields such as `operation`, `predicate`, `polarity`, `source`, `safety`, and contract validators.

## Red-Zone Python Retired

These pieces used to inspect raw utterance text and infer meaning before the
Semantic IR model had done the semantic work.

### 1. Domain Profile Selection

File: `src/domain_profiles.py`

The old `select_domain_profile()` path has been removed from active runtime and
research harnesses. `active_profile=auto` now calls `semantic_router_v1` first.
The domain-profile catalog remains, but it is a roster/context source for the
model router rather than a Python keyword classifier.

Replacement direction:

```text
semantic_router_v1
  input: utterance, recent context summary, thin profile roster, KB manifest
  output: selected_profiles, guidance_modules, retrieval_hints, risk_flags, confidence
```

Python should validate that selected profile IDs and guidance module IDs exist. It should not choose them by reading the utterance.

### 2. UI Story And Query Segmentation

File: `ui_gateway/gateway/phases.py`

The gateway currently splits long user input into story/query segments with punctuation and marker heuristics.

Key examples:

- `_split_story_segments()` lines 37-51.
- `_split_query_boundary_segments()` lines 62-76.
- `_should_segment_story()` lines 79-102.
- `_should_segment_query_boundaries()` lines 105-114.
- `_process_segmented_story()` lines 202-225.
- `_process_segmented_query_boundaries()` lines 228-251.

The need is real: long mixed prose often works better when processed as focused semantic units. But the segmentation decision and boundaries should be model-proposed, especially for non-English text.

Replacement direction:

```text
semantic_segmenter_v1
  input: full utterance, task policy, recent context
  output: exact source spans, segment_type, reason, preserve_order
```

Python should verify exact spans and process them in order.

### 3. Legacy Route And Turn Shape Heuristics

File: `src/mcp_server.py`

Even with Semantic IR enabled, parts of the front door still compute `looks_like_query`, `looks_like_write`, clause splits, turn segments, and route-like hints from raw English.

Key examples:

- Query/write heuristic around lines 3553-3563.
- `_build_turn_segments()` lines 4060-4075.
- `_split_clauses()` lines 4251-4258.
- `_tokenize_words()` lines 4260-4269.

Replacement direction:

Let `semantic_router_v1` or `semantic_ir_v1` provide `turn_type`, `contains_query`, `contains_write`, `contains_rule`, `contains_correction`, and `segment_plan`. Python can then use those structured outputs.

### 4. Legacy Coreference And Family Rescue

File: `src/mcp_server.py`

There are still older Python routines that parse pronouns, family bundles, same-clause spouse phrases, and possessive social relationships.

Key examples:

- `_build_coreference_hint()` lines 3943-4058.
- `_utterance_has_explicit_family_bundle()` lines 3010-3019.
- `_normalize_possessive_family_bundle_utterance()` lines 4882-4906.
- `_normalize_same_clause_spouse_phrase_utterance()` lines 4935-4950.
- `_normalize_same_utterance_family_anchor_pronouns()` lines 4985-5000.
- Monkey patches around `PrologMCPServer.process_utterance` lines 4909-5016.

This is the clearest example of the old architecture: Python learning English one failure at a time.

Replacement direction:

Move these into Semantic IR guidance and tests. The LLM should emit referents, candidates, chosen referents, uncertainty, and candidate operations. Python should only admit or reject those operations.

### 5. Medical Vague-Surface Clarification

Files:

- `src/mcp_server.py`
- `src/medical_profile.py`

The medical lane still has Python checking vague surfaces such as "pressure," "sugar," and "kidney" and constructing clarification questions.

Key examples:

- `_medical_vague_surface_clarification()` lines 3042-3089.
- `_sanitize_compiler_clarification()` lines 3091-3125.
- `src/medical_profile.py` contains UMLS/medical bridge logic that inspects input text for medical ambiguity.

Some medical normalization can remain deterministic when it is ontology lookup, but raw surface interpretation should move into model-authored ambiguity fields.

Replacement direction:

The medical profile should supply ontology hints and allowed predicates. The LLM should decide whether a surface is ambiguous in-context and propose `clarification_questions`. Python should enforce "no unsafe medical advice writes" and predicate contracts.

### 6. Legacy Pipeline Bulk

File: `kb_pipeline.py`

This file contains a large amount of older English-first parsing, route repair, clarification handling, split extraction, family/story rewrites, multilingual detection, and explicit rule/query heuristics. Much of it is now legacy relative to the Semantic IR path.

This is not the immediate live frontier, but it matters because docs and tests can make it look like current architecture.

Current cleanup:

The old parser-lane runners and prompt assets have now been removed from the
working tree. Git history is the archive. Remaining `kb_pipeline.py` imports are
for shared runtime/Prolog utilities until those pieces are split into smaller
modules.

## Yellow-Zone Python

These are acceptable only if they consume structured model output, not raw utterance language:

- Deciding whether a candidate operation is admitted based on `source`, `safety`, `polarity`, `predicate`, and predicate contracts.
- Blocking negative facts until negative-fact semantics exist.
- Blocking durable rules unless rule admission policy allows them.
- Projecting the model's advisory `decision` into the mapper's actual decision.
- Retrieving KB clauses by terms, if those terms come from a model-produced retrieval hint rather than Python tokenizing the utterance.

## Target Architecture

```text
raw utterance
  -> semantic_router_v1
       selects profile(s), context modules, retrieval hints, segmentation policy
  -> semantic_segmenter_v1
       optional exact-span segmentation for long/mixed turns
  -> semantic_ir_v1
       rich semantic workspace proposal for each segment or whole turn
  -> deterministic mapper
       schema, predicate, contract, source, safety, and truth-maintenance gates
  -> Prolog KB
       durable facts/rules/queries/retractions
```

The router and segmenter are not authorities. They are context engineers. The mapper remains the authority.

## Testable Metrics

Track this as a first-class metric:

```text
raw_utterance_language_inspections_in_python
```

Also track:

- `llm_router_profile_accuracy`
- `llm_segmenter_span_accuracy`
- `wrong_profile_harm_rate`
- `wrong_segment_harm_rate`
- `clarification_quality`
- `admission_contract_pass_rate`
- `non_mapper_parse_rescue_count`
- `non_english_domain_routing_score`

The first multilingual router probe made this concrete:

```text
10-case raw multilingual battery
semantic_router_v1: 10/10 expected profile choices
semantic_ir_v1 compiler: 10/10 valid workspaces
```

That result does not prove broad multilingual robustness, but it strongly
suggests that foreign-language understanding belongs in the model router and
compiler, not in a Python translation/keyword layer.

The first fresh held-out Lava v3 router probe made the same point under harder
cross-domain pressure:

```text
17-case held-out frontier
semantic_router_v1: 14/17 expected profile choices
semantic_ir_v1 compiler: 17/17 valid workspaces on the full pass
```

The three router misses are useful failure classes rather than reasons to
return to Python NLP: uncertain retraction ownership, unexpected-domain
bootstrap policy, and legal-vs-probate identity/source jurisdiction. The new
anti-coupling diagnostics now records whether those router choices cause mapper
skips, admitted writes under a nonexpected profile, or profile/predicate
mismatch pressure.

After recording that first held-out result, v3 became calibration evidence. A
generic repair pass then reached:

```text
17-case v3 repair/calibration pass
semantic_router_v1: 17/17 expected profile choices
semantic_ir_v1 compiler: 17/17 valid workspaces
anti-coupling: bootstrap review-only skips for the two unexpected-domain turns
```

Those repairs stayed within the wall-sign discipline: router context-integrity
guidance, bootstrap-aware diagnostics, and profile/predicate contract fixes.
They did not add Python raw-utterance phrase handling.

## Near-Term Plan

1. Keep `semantic_router_v1` as the model prescan with a small JSON schema.
2. Keep current docs and UI traces centered on the router-first path; historical selector comparisons live in Git history.
3. Build `semantic_segmenter_v1` for long story and mixed query/write turns.
4. Replace UI story/query segmentation heuristics with model-proposed exact spans.
5. Disable the family/pronoun monkey patches in the Semantic IR path and measure regressions.
6. Convert any regression into prompt/profile/schema improvements, not new raw-utterance regex.

## Bottom Line

The wall sign is achievable as an architectural rule:

```text
NO LANGUAGE HANDLING IN PYTHON
```

But it requires one more layer before Semantic IR: a model-based context/router/segmenter pass. Python should become the steward of structure and truth, not the first reader of the user's language.

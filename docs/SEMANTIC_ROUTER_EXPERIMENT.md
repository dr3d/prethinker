# Semantic Router Experiment

Last updated: 2026-04-29

## Thesis

The next Prethinker frontier is not a bigger all-purpose prompt. It is staged context engineering:

```text
raw utterance
  -> semantic_router_v1
  -> focused context + action plan
  -> semantic_ir_v1
  -> deterministic mapper/admission gate
  -> Prolog KB
```

The router is becoming the ingestion controller. It chooses attention and the
minimal next processing actions, not truth.

This is intentionally similar to adaptive multi-stage reasoning systems such
as AdapTime (`https://arxiv.org/abs/2604.24175`), but with Prethinker's
authority boundary intact:

```text
controller plans
compiler proposes
mapper admits
KB mutates
```

## Headline Result

The strongest current evidence is the multilingual probe:

```text
router_ok=10/10
compiler_parsed_ok=10/10
```

This is the result to lead with. It is a clean pressure test of the wall-sign
rule: the same raw multilingual turns are sent through the model router without
a Python translation or keyword-routing layer.

That result is not just an incremental score improvement. It demonstrates the
architectural claim directly: when raw Spanish, French, German, Portuguese,
Italian, Japanese, and code-switched turns are routed by the model, profile
selection succeeds without Python reading the utterance for meaning.

This makes the wall sign empirically defensible:

```text
NO LANGUAGE HANDLING IN PYTHON
```

The system still needs deterministic validation and admission. But the language
understanding belongs in the LLM router/compiler path, not in Python phrase
patches.

## Why Not One Giant Prompt?

A single Semantic IR prompt can be made to include every rule:

- medical safety
- legal claim/finding separation
- contract obligations
- story source fidelity
- temporal corrections
- query/write/rule splitting
- non-English normalization
- KB conflict handling
- predicate contract obedience

That works for focused tests, but it turns the compiler prompt into a large manual. The model must remember every policy at once, and irrelevant guidance can lower the signal-to-noise ratio.

The router pass lets the model first ask:

```text
What kind of work is this turn?
Which profile/context module is useful?
What should the compiler pay attention to?
Which processing actions are worth running?
Does this need segmentation?
What KB context should be retrieved?
```

Then the compiler receives a smaller, sharper context.

## Design Rule

```text
LLM controls attention.
LLM proposes semantics.
Deterministic code controls admission.
```

The router must not emit facts, rules, queries, or KB mutations. It emits a strict control-plane object:

```json
{
  "schema_version": "semantic_router_v1",
  "selected_profile_id": "sec_contracts@v0",
  "candidate_profile_ids": ["sec_contracts@v0"],
  "routing_confidence": 0.86,
  "turn_shape": "mixed",
  "should_segment": false,
  "segments": [],
  "guidance_modules": [
    "contract_obligation_semantics",
    "temporal_scope",
    "rule_query_boundary"
  ],
  "action_plan": {
    "actions": [
      "compile_semantic_ir",
      "include_kb_context",
      "extract_query_operations",
      "review_before_admission"
    ],
    "skip_heavy_steps": [
      "segment_before_compile"
    ],
    "review_triggers": [
      "mixed write+query turn",
      "conditional rule language"
    ],
    "why": "The turn mixes policy facts/rules with an explicit question."
  },
  "retrieval_hints": {
    "entity_terms": ["shipment_h7", "ada"],
    "predicate_terms": ["frozen", "cleared", "transfer"],
    "context_needs": ["current shipment state", "active clearance rules"]
  },
  "risk_flags": ["conditional_validity", "temporal_order"],
  "bootstrap_request": {
    "needed": false,
    "proposed_domain_name": "",
    "why": "",
    "candidate_predicate_concepts": []
  },
  "notes": []
}
```

## Harness Responsibility

Python is still allowed to be the harness:

- validate router JSON
- reject unknown or unavailable profile IDs
- load known profile packages
- load known guidance modules
- retrieve KB context from structured router hints
- obey or log the router's action plan
- pass the focused package to `semantic_ir_v1`

Python should not inspect the raw utterance and decide what the language means.

## Action Plan V1

`semantic_router_v1` now emits an explicit `action_plan` block. This is the
first step toward a `semantic_controller_v1` shape:

```json
{
  "actions": [
    "compile_semantic_ir",
    "segment_before_compile",
    "include_kb_context",
    "include_temporal_graph_guidance",
    "include_truth_maintenance_guidance",
    "extract_query_operations",
    "review_before_admission",
    "profile_bootstrap_review",
    "ask_clarification_first"
  ],
  "skip_heavy_steps": [],
  "review_triggers": [],
  "why": ""
}
```

The point is not to add more stages to every turn. The point is the opposite:
make expensive stages conditional and auditable.

Examples:

- simple direct fact: `compile_semantic_ir`, maybe skip segmentation and review;
- correction over current state: `compile_semantic_ir`, `include_kb_context`,
  `include_truth_maintenance_guidance`;
- explicit question mixed with writes: `compile_semantic_ir`,
  `extract_query_operations`, often `review_before_admission`;
- deadline, expiry, before/after, maturity, or date correction:
  `include_temporal_graph_guidance`;
- unknown domain: `profile_bootstrap_review` before ordinary compilation.

The action plan does not authorize writes. It only tells the harness what
context/workflow to assemble for the compiler and what diagnostics to show.

The runtime now carries this plan into the compiler as compact
`router_action_policy:` context. This is the first live use of the action plan
beyond trace visibility: `extract_query_operations` pressures mixed turns to
emit explicit query operations, `include_kb_context` tells the compiler to use
the compact KB seed for grounding, and truth-maintenance/review actions steer
support links, conflicts, retraction plans, and self-checks. The mapper still
ignores the router as authority; admission is determined only by candidate
operations and deterministic gates.

## Fast Frontier Runs

Long 35B structured-output sweeps are useful, but they are not always useful
enough to justify the GPU time. The current interactive smoke command is:

```powershell
python scripts\run_semantic_ir_lava_sweep.py --fast
```

That preset runs a balanced 15-case clean slice with one repeat. It is meant to
answer "did we break the center?" quickly. Larger multi-variant Lava sweeps are
still valuable, but should be treated as longer frontier or nightly work.

## Coupled Hallucination Risk

The main risk in a two-pass LLM design is coupled hallucination:

```text
router chooses the wrong lens
  -> compiler sees only the wrong context
  -> wrong context reinforces wrong interpretation
```

Prethinker handles this by keeping the router advisory:

- `context_available=false` profiles are not loaded.
- Unknown profiles fall back to `general` or bootstrap.
- Router confidence and candidate profiles are logged.
- The compiler still produces explicit candidate operations.
- The mapper still enforces predicate contracts and admission rules.

Detection is not enough. The current system can log the failure, but logging is
not yet a corrective loop. The next design step is to make router-induced
failure attribution explicit: when the mapper catches a bad operation, missing
profile contract, unsafe write, or strange predicate palette mismatch, the trace
should say whether the router's context decision helped cause it.

The feedback loop should be explicit:

```text
router plan
  -> compiler workspace
  -> mapper/admission diagnostics
  -> anti-coupling report
  -> profile/guidance/schema/test update
```

The mapper can catch router-induced failures, but it should also teach us what
went wrong:

- low-confidence router choice followed by a high-risk commit;
- selected profile differs from the predicate palette the compiler tries to use;
- advisory profile should have been primary;
- router selected `general` when a safety boundary profile was needed;
- compiler emits out-of-profile operations because the router chose the wrong
  context;
- mapper skips many operations for reasons tied to missing profile guidance.
- router primary profile disagrees with the predicates that survive admission;
- wrong-profile harm rate rises on a profile boundary family such as
  legal/medical, legal/probate, or contract/policy.

The corrective action should usually be one of:

- improve profile ownership doctrine;
- split a guidance module out of a giant prompt;
- add or tighten predicate contracts;
- add an anti-coupling diagnostic;
- add a fresh validation case.

It should not be a Python phrase patch.

## Current Experiment

Runner:

```powershell
python scripts\run_semantic_router_agility.py --count 8 --include-model-input
```

What it measures:

- router strict match against the older expected profile label
- router semantic near-miss when the expected profile appears as a candidate
- unavailable-profile near-miss
- compiler JSON success after router-crafted context
- admitted/skipped mapper outcomes

Current useful result on the fresh v3 frontier, before v3-specific repair:

```text
Lava v3 first held-out router-only:
router_ok=14/17
router_score_avg=0.868

Lava v3 first held-out router -> compiler:
router_ok=14/17
compiler_parsed_ok=17/17
```

Some misses are informative rather than simply wrong. For example:

- A first pass routed a deed/countersignature scenario to `probate@v0`; disambiguation guidance now sends source-document/minutes/countersignature turns to `legal_courtlistener@v0` unless estate/probate concepts dominate.
- A first pass routed a shipment/clearance rule to unavailable `logistics@v0`; disambiguation guidance now lets `sec_contracts@v0` serve as the implemented conditional-policy/clearance toolset.
- Remaining misses are legal-vs-probate taxonomy pressure in administrative-record follow-ups. These are graded near-misses because the expected profile appears as a candidate and the router's chosen profile has a defensible source-record toolset.

Those cases show why exact old-label scoring is not enough. The router may discover better semantic tool choices than the original hand labels.

## When The Router Disagrees With The Label

This is one of the most important findings so far:

> The router may discover better semantic tool choices than the original hand labels.

That means a strict `selected_profile == expected_profile` metric can be too
crude. A hand-authored label may say `probate@v0` because the scenario came from
the Silverton pack, while the router may correctly choose `legal_courtlistener@v0`
because the actual turn is about a source document, witness statement, access
log, or board minutes rather than inheritance mechanics.

The evaluation needs multiple buckets:

- **strict match**: selected profile equals the old expected label;
- **semantic near miss**: expected profile appears as a candidate, but another
  defensible lane is primary;
- **router-better-than-label**: review decides the router exposed a bad or stale
  expected label;
- **real miss**: router chose a lane that withholds needed safety/context or
  induces downstream mapper/compiler failure.

This matters because the router is not merely a classifier. It is an epistemic
jurisdiction allocator. Sometimes the right answer is not "which scenario file
did this case come from?" but "which profile owns the admission boundary for
this turn?"

## Multilingual Probe

A separate probe now tests the same router-first path on raw non-English and
code-switched utterances:

```powershell
python scripts\run_multilingual_semantic_ir_probe.py
```

The first 10-case battery covers Spanish, French, German, Portuguese, Italian,
Japanese, and mixed English/Spanish across medical, legal, contracts, story, and
probate lanes.

Current result:

```text
router_ok=10/10
router_score_avg=1.000
compiler_parsed_ok=10/10
```

This is useful evidence for the wall-sign rule. The LLM router chooses the right
epistemic lane without a Python translation or keyword-routing layer. Remaining
errors move downstream into predicate palette, negation, query, and
profile-contract design.

See [Multilingual Semantic IR Probe](https://github.com/dr3d/prethinker/blob/main/docs/MULTILINGUAL_SEMANTIC_IR_PROBE.md).

## Lava Pack v2 Calibration Probe

`semantic_ir_lava_pack_v2` is a 36-case calibration frontier pack focused on:

- epistemic jurisdiction/profile ownership;
- router-owned segmentation pressure;
- negation and correction;
- rule/query semantics;
- KB-seeded truth maintenance;
- multilingual/noisy cross-domain turns.

Runner:

```powershell
python scripts\run_semantic_router_agility.py `
  --router-only `
  --count 36 `
  --frontier-pack docs\data\frontier_packs\semantic_ir_lava_pack_v2.json
```

First router-only result after tightening profile ownership doctrine:

```text
semantic_router_v1: 36/36
router_score_avg: 1.000
```

The intermediate run was more important than the final score. It exposed two
systematic ownership gaps:

- clinical advice requests should still select `medical@v0` so the rejection
  boundary is loaded;
- medical facts inside depositions/complaints/witness statements should select
  `legal_courtlistener@v0` primary, with medical as advisory/normalization
  pressure.

Those were fixed in router guidance, not with Python utterance patches.

Important status note: after that tuning loop, Lava Pack v2 is no longer a
held-out validation pack. It is now a **calibration pack**. The 36/36 result is
valuable evidence that the profile ownership doctrine absorbed real failures,
but it should not be used as a generalization claim. It is impressive as a
repair story, not as proof that the router generalizes to untouched examples.

The next validation step is a fresh Lava Pack v3 that the router guidance has
not touched.

```text
Lava v2: calibration signal
Lava v3: held-out validation signal
```

The honest claim is:

```text
We found systematic ownership gaps and fixed them without Python NLP.
We have not yet proven those fixes generalize to an untouched frontier pack.
```

## Lava Pack v3 Held-Out Probe

`semantic_ir_lava_pack_v3` was the first fresh pack after the v2 calibration
loop. Its first run is the honest held-out signal; after that, v3 became a
calibration pack because the misses informed generic router/profile repairs. It
adds pressure on:

- legal/medical provenance boundaries;
- legal/probate jurisdiction boundaries;
- contract rule language inside story wrappers;
- story source fidelity against famous-name priors;
- uncertain retractions against KB context;
- query plus mutation splitting;
- unexpected-domain bootstrap routing.

First held-out router-only result:

```powershell
python scripts\run_semantic_router_agility.py `
  --router-only `
  --count 17 `
  --frontier-pack docs\data\frontier_packs\semantic_ir_lava_pack_v3.json
```

```text
semantic_router_v1: 14/17
router_score_avg: 0.868
```

Full router -> compiler -> mapper pass:

```text
router_ok=14/17
compiler_parsed_ok=17/17
```

This is the right kind of result: not perfect, but strongly in favor of the
router-first architecture. The important part is that the failures are now
visible as classes:

- **uncertain contract correction routed as legal source correction**:
  `lava3_truth_02_soft_retraction_should_clarify` selected
  `legal_courtlistener@v0` instead of `sec_contracts@v0`; mapper skipped rather
  than committing a bad retraction.
- **unexpected lab-protocol bootstrap pressure routed to contracts**:
  `lava3_bootstrap_02_unexpected_domain_lab_protocol` selected
  `sec_contracts@v0` instead of `bootstrap`; mapper skipped an out-of-palette
  validity query.
- **French probate identity routed to legal evidence**:
  `lava3_multilingual_02_french_probate_identity` selected
  `legal_courtlistener@v0` with `probate@v0` as a candidate. This is a semantic
  near miss, not a simple failure: the turn is both probate-contextual and
  legal-source/identity-evidence shaped.

The new anti-coupling diagnostics caught the downstream risk signals:

```text
mapper_skips_tied_to_profile_context: 2
semantic_near_miss_with_admissions: 1
strict_profile_miss_with_admissions: 1
general_effective_profile_with_domain_candidates: 1
```

Repair pass after generic, non-Python-NLP changes:

```text
router_ok=17/17
router_score_avg=0.991
compiler_parsed_ok=17/17
anti_coupling_flags={'bootstrap_review_only_skips': 2}
```

The repairs were deliberately structural:

- tighten router context-integrity policy so prompt examples cannot masquerade
  as recent context;
- score `bootstrap` as a valid request for no existing thick profile;
- suppress bootstrap false positives in anti-coupling diagnostics;
- broaden the legal `court_or_judge` contract to include institutional courts;
- add scoped probate witness-eligibility predicates to the probate profile.
- make bootstrap review-only for durable admission when no approved predicate
  palette exists yet.

Important status note: v3 is no longer pristine held-out evidence. The first
14/17 result is the validation signal. The later 17/17 result is useful
repair/calibration evidence that those failures were addressable without Python
utterance patches. Lava v4 should be the next untouched validation pack.

The next useful move is to decide whether bootstrap should grow into a separate
profile-design workflow:

- profile ownership doctrine changes;
- a clearer bootstrap policy;
- a new profile/guidance module;
- or a label correction because the router found a better epistemic owner.

## Near-Term Sharpening

1. Surface anti-coupling diagnostics in trace/UI reports.
2. Decide whether v3 misses are router failures, stale labels, or missing profile/guidance modules.
3. Tighten bootstrap policy without tuning phrase-by-phrase against v3.
4. Turn guidance module names into small loadable context blocks.
5. Run a second v3 pass after any generic architecture change and compare anti-coupling deltas.
6. Author Lava v4 only after v3 has served as calibration signal.

## Desired End State

The live pipeline should eventually become:

```text
utterance
  -> semantic_router_v1
       profile/module/retrieval/segmentation plan
  -> harness
       validates and assembles focused context
  -> semantic_ir_v1
       semantic workspace proposal
  -> mapper
       deterministic admission
  -> KB
       durable symbolic state
```

This is how Prethinker moves toward the wall sign:

```text
NO LANGUAGE HANDLING IN PYTHON
```

The LLM becomes the context engineer. Python becomes the structural steward.

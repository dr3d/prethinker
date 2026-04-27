# Domain Bootstrapping Meta-Mode

Last updated: 2026-04-27

This note records a frontier idea: Prethinker should eventually help discover
the predicate palette for a domain it does not already know.

Today, the strongest path is profile-aware intake:

```text
utterance + context
  -> selected domain profile
  -> allowed predicates + predicate contracts
  -> semantic_ir_v1 workspace
  -> deterministic mapper/admission
  -> KB mutation, query, clarification, quarantine, or rejection
```

That works when a profile already exists. The open question is what Prethinker
should do when the domain is new, vague, or only partially covered by existing
profiles.

## Core Idea

Add a meta-mode where the model does not propose KB writes. Instead, it proposes
a candidate domain profile:

```text
sample text / conversation / corpus slice
  -> domain analysis workspace
  -> candidate entities, roles, predicates, contracts, risks
  -> human or deterministic review
  -> draft profile package
  -> later ordinary Semantic IR runs use the approved profile
```

This is not a shortcut around admission. It is a way to use the model's broader
semantic intelligence to help design the admission surface.

The boundary should stay strict:

```text
The model may propose the language of a domain.
The runtime decides when that language becomes an approved profile.
Only approved profiles can authorize durable predicate palettes.
```

## Why It Matters

For a random domain, the hardest part may not be extracting one fact. It may be
discovering the right symbolic vocabulary:

- What are the durable entity types?
- Which relationships matter?
- Which relations are claims rather than facts?
- Which predicates are functional or current-state-like?
- Which predicates need provenance?
- Which distinctions should be clarified instead of guessed?
- Which tempting writes should be quarantined?
- Which rules are executable, and which are only policy prose?

If Prethinker can help answer those questions, it becomes more than a set of
hand-authored profiles. It becomes a workbench for growing profiles safely.

## Proposed Output Shape

A future `profile_bootstrap_v1` output could look like:

```json
{
  "domain_guess": "warehouse_safety",
  "confidence": 0.82,
  "entity_types": [
    {"name": "asset", "examples": ["forklift_7", "loading_dock_b"]},
    {"name": "inspection", "examples": ["march_safety_walkthrough"]},
    {"name": "issue", "examples": ["brake_warning", "loose_guardrail"]}
  ],
  "candidate_predicates": [
    {
      "signature": "inspected_on/3",
      "args": ["inspector", "asset", "date"],
      "why": "Repeated source text records inspections as durable events."
    },
    {
      "signature": "requires_repair/2",
      "args": ["asset", "issue"],
      "why": "The domain distinguishes observed issues from completed repairs."
    }
  ],
  "admission_risks": [
    "A worker report is not the same as an inspection finding.",
    "A scheduled repair is not a completed repair.",
    "A cleared asset should probably retract or supersede an active hazard only with explicit source support."
  ],
  "clarification_policy": [
    "Clarify asset identity when location-only descriptions match multiple assets.",
    "Clarify whether a reported issue was observed, alleged, or repaired."
  ],
  "starter_frontier_cases": [
    {
      "utterance": "Mina said forklift 7's brakes squealed, but the inspection only found a loose mirror.",
      "expected_boundary": "claim versus inspection finding"
    }
  ]
}
```

This object is profile-design material. It should not be mapped directly into
the Prolog KB.

## Modes

### 1. Unknown Domain Intake

When no profile matches, Prethinker can use a tiny generic palette for safe
capture:

```text
mentioned/2
claimed/3
candidate_entity/3
candidate_relation/4
needs_profile/2
```

This preserves useful material without pretending the system has domain
authority.

### 2. Profile Proposal

Given a bundle of representative text, the model proposes:

- domain name and scope;
- entity types;
- candidate predicates and argument roles;
- likely functional predicates;
- provenance-sensitive predicates;
- unsafe transformations;
- clarification patterns;
- starter test cases.

### 3. Profile Review

Humans or deterministic checks review the proposal:

- remove vague predicates;
- split overloaded predicates;
- add argument contracts;
- add validators for claim/finding, obligation/fact, condition/event, and
  source-priority boundaries;
- write a small frontier pack before allowing the profile in normal runs.

### 4. Profile Evolution

As frontier cases fail, the system should prefer profile evolution over generic
Python patching:

```text
failure trace
  -> was the predicate missing?
  -> was the contract underspecified?
  -> was the profile guidance too weak?
  -> was the mapper missing a generic structural check?
```

Only the last category belongs in generic Python. The others belong in profile
packages or test packs.

## Context Budget

This mode will need more context than ordinary per-turn intake. A good shape is:

- thin roster of existing profiles;
- small corpus sample or selected representative turns;
- current generic schema;
- profile-design instructions;
- examples of accepted/rejected profile predicates;
- maybe a compact KB or ontology manifest if one exists.

The ordinary 16K context window is enough for early experiments, but this mode
will need aggressive summarization once the corpus grows.

## Research Questions

- Can a strong model propose useful predicates without overfitting to one
  example?
- Can it distinguish domain facts, claims, rules, obligations, events, and
  provenance boundaries?
- Can it produce predicate contracts that the mapper can enforce structurally?
- Can profile proposals reduce future prompt bloat?
- Can this reduce Python-side domain patches?
- Can the system generate starter frontier cases that actually catch its own
  likely mistakes?

## Metrics

Early experiments should measure:

- percentage of proposed predicates accepted after review;
- number of overloaded predicates rejected or split;
- admission failures caused by missing predicate surface;
- reduction in out-of-palette candidate operations after profile update;
- reduction in profile-specific Python code;
- held-out scenario performance before and after the profile proposal.

## Near-Term Experiment

Build a small `domain_bootstrap` harness:

```text
input: 5-20 short texts from an unfamiliar domain
model: qwen/qwen3.6-35b-a3b or other candidate
output: profile_bootstrap_v1 JSON
review: compare against hand-authored starter profile
follow-up: run generated frontier cases through semantic_ir_v1
```

Good first targets:

- warehouse safety reports;
- academic advising notes;
- software incident postmortems;
- meeting commitments;
- procurement approvals.

The goal is not to automate ontology design on day one. The goal is to see
whether a strong model can draft a useful, reviewable domain surface faster than
we can invent one by hand.

## Bottom Line

Domain bootstrapping is the meta-version of Prethinker:

```text
ordinary mode: language -> governed symbolic state
meta-mode: language samples -> governed symbolic vocabulary
```

Both modes keep the same thesis:

The model proposes. Admission governs.

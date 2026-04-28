# Domain Profile Catalog

This note names an important boundary in the Semantic IR direction.

Prethinker should be able to become domain-aware without turning the generic
mapper into a pile of domain-specific Python. The clean shape is a catalog of
domain profiles: small, explicit packages that can provide predicate palettes,
argument contracts, normalization hints, and compact background context to the
Semantic IR compiler.

The analogy is a skill directory. The model should not receive every domain
package all the time. It should first see a thin roster of available profiles,
then choose one or more profiles whose description matches the utterance and
context. Only the selected profile's thicker context is loaded into the
Semantic IR pass.

There is a second, more speculative direction: profile bootstrapping. When no
profile exists, Prethinker should eventually be able to run a meta-mode that
analyzes representative text and proposes candidate entity types, predicates,
argument contracts, admission risks, clarification policies, and starter
frontier cases. That proposal is not authority. It is review material for
creating a new profile package. See [Domain Bootstrapping Meta-Mode](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_BOOTSTRAPPING_META_MODE.md).

## Current Example

`medical@v0` is the first real profile. Two additional live-data lanes now
exercise the same profile idea: `legal_courtlistener@v0` for legal-source
provenance/conflict and `sec_contracts@v0` for filing/contract obligation
pressure.

It owns:

- canonical predicates such as `taking/2`, `has_condition/2`, and
  `lab_result_high/2`
- argument-role contracts and UMLS semantic-group expectations
- compact UMLS bridge context for bounded normalization, such as
  `Coumadin -> warfarin` and `blood pressure reading -> lab/procedure`
- profile policy, including patient-grounding and medical-advice rejection

The generic Semantic IR mapper does not own medical vocabulary. It sees
candidate operations and structural contracts, then decides what is admissible.
Those structural contracts are now executable in a limited way: the mapper can
reject obvious role/order mismatches in candidate operations without learning
domain vocabulary itself.

Two starter/mock profiles also exist for exploration:

- `story_world@v0`: narrative events, object identity, passive observations,
  movement, possession, and scene state
- `probate@v0`: estate/probate claims, witnesses, amendments, beneficiary
  status, identity ambiguity, document evidence, and forfeiture conditions
- `legal_courtlistener@v0`: CourtListener legal source intake for opinions,
  dockets, parties, judges, citations, allegations, findings, holdings, and
  provenance; it has synthetic and ignored live API smoke traces
- `sec_contracts@v0`: SEC/EDGAR and contract-obligation intake for filings,
  exhibits, parties, obligations, conditions, effective dates, termination,
  breach events, and provenance; it has synthetic and ignored live SEC smoke
  traces

These packages are intentionally declarative. They are research scaffolds for
testing the catalog idea, not new automatic runtime authority.

## Desired General Shape

```text
utterance + recent context
  -> domain profile selection
  -> semantic_ir_v1 model input
       - selected profile id
       - allowed predicates
       - predicate contracts
       - compact domain context
  -> semantic workspace proposal
  -> deterministic mapper / profile validators
  -> KB mutation, query, clarification, quarantine, or rejection
```

Domain profile selection can be explicit:

```text
active_profile = medical@v0
```

It can also be catalog-assisted:

```text
available_profiles = [medical@v0, probate@v0, story_world@v0, logistics@v0]
semantic_router_v1(utterance/context + thin roster) -> selected profile candidate(s)
selected profile(s) -> thick Semantic IR context
```

The router is advisory. It may choose the domain context supplied to the model,
but it may not authorize writes.

`active_profile=auto` now uses `semantic_router_v1` as the measured
implementation of this idea. It sends the thin roster to the model router, then
loads only the selected profile package for the Semantic IR call. The trace
records:

- visible roster
- selected profile
- router confidence, candidates, guidance modules, and retrieval hints
- loaded domain context
- loaded predicate contracts
- mapper/admission outcome

The router also accepts explicit per-turn Semantic IR context. This is the
control-plane version of "here is the story so far; now process this sentence":
context can affect profile choice and model input, but it is still treated as
already-known support, not as a new write. The selected profile package may
declare compact `selection_keywords`; those are context assets for the router
and compiler, not generic mapper rules.

A synthetic switching test now walks one server through:

```text
medical@v0 -> legal_courtlistener@v0 -> sec_contracts@v0 -> medical@v0
```

and verifies that each turn receives the matching thick context and predicate
palette. This proves the control-plane mechanism can switch domains; it does
not prove mixed-domain turns are solved.

`scripts/run_mixed_domain_agility.py` is the next pressure gauge. It builds a
randomized stream from Goldilocks, Glitch, Ledger, Silverton, Harbor,
CourtListener, SEC/contracts, and medical scenarios, then runs the stream
through `active_profile=auto`. The first real LM Studio smoke selected the
expected profile for `12/12` shuffled turns and produced valid Semantic IR for
`12/12`. The interesting misses were not routing failures; they were downstream
quality issues such as vague story predicates and placeholder/null arguments in
otherwise useful legal operations.

The first tightening pass on that same seed moved those issues measurably:
bad admitted placeholder/loose-trait clauses dropped from `4` to `0`. The mapper
now rejects `null`/unspecified/generic-actor write arguments, and the story-world
profile exposes `has_trait/2`, `returned_from/2`, and `robot_unit/1` so the model
has better predicates for traits and return events.

A harder mixed-domain seed then exposed context-selection and predicate-shape
weaknesses rather than JSON failures. Those historical selector runs have been
superseded by the router-first path. The useful changes remain declarative:
profile-owned keywords, broader profile-owned predicate contracts for
legal/probate/SEC frontier cases, and a generic duplicate candidate-operation
collapse in the mapper.

The next tightening pass enabled deterministic contract-role checks. On the
same wider seed, the real LM Studio run stayed at `40/40` expected profile
selections and `40/40` valid Semantic IR while the mapper caught a real
`interval_start/2` role mismatch. This is the intended profile pattern:
profiles expose role contracts; the generic mapper enforces only structural
shape.

Profile contracts can now also carry small declarative admission validators.
The first validators live in `legal_courtlistener@v0` and `sec_contracts@v0`:
legal finding/holding predicates can reject allegation/citation-shaped content,
and contract predicates can reject condition/breach writes that are only
obligation or unsatisfied-condition language. This keeps domain guardrails in
profile JSON where they can be reviewed, tested, and eventually reused across
scenario packs.

## Thin Roster Versus Thick Profile

The roster should be small enough to keep in ordinary context:

```json
[
  {
    "profile_id": "medical@v0",
    "description": "Bounded medical memory: medications, conditions, symptoms, allergies, labs, pregnancy.",
    "use_when": ["medication use", "lab result", "patient symptom", "allergy or side effect"],
    "avoid_when": ["clinical advice", "dose recommendation", "broad diagnosis"]
  },
  {
    "profile_id": "probate@v0",
    "description": "Estate/probate claims, witnesses, beneficiary status, amendments, and forfeiture rules.",
    "use_when": ["inheritance", "witnessed amendment", "beneficiary", "estate charter"],
    "avoid_when": ["general family biography with no legal rule"]
  },
  {
    "profile_id": "sec_contracts@v0",
    "description": "SEC/EDGAR and contract intake: filings, exhibits, parties, obligations, conditions, effective dates.",
    "use_when": ["SEC filing", "contract exhibit", "shall/must obligation", "subject to/provided that condition"],
    "avoid_when": ["investment advice", "legal advice", "outcome prediction"]
  },
  {
    "profile_id": "legal_courtlistener@v0",
    "description": "CourtListener source intake: opinions, dockets, parties, judges, citations, claims, findings, holdings.",
    "use_when": ["CourtListener record", "case citation", "docket event", "claim versus finding"],
    "avoid_when": ["legal advice", "outcome prediction", "broad precedent reasoning"]
  },
  {
    "profile_id": "story_world@v0",
    "description": "Narrative events, objects, places, observations, movement, possession, and corrections.",
    "use_when": ["fictional story", "scene narration", "object interactions", "who did what"],
    "avoid_when": ["formal policy or clinical fact intake"]
  }
]
```

If the router selects `medical@v0`, the next Semantic IR call can include the
thicker package: predicate contracts, UMLS aliases, grounding policy, and
medical safety boundaries. If it selects `story_world@v0`, the thicker package
would instead contain story-world predicates, event/observation guidance, and
object identity policy.

This gives the smart LLM more understanding without turning the base prompt
into a giant undifferentiated manual.

## Profile Package Contract

A mature profile should eventually declare:

- `profile_id`
- trigger hints and negative trigger hints
- short roster description
- thicker profile context blocks for selected use
- predicate registry
- predicate contracts and argument roles
- declarative admission validators for profile-owned predicate contracts
- optional ontology or alias context
- profile-specific clarification policy
- profile-specific type/grounding validators
- examples and held-out frontier cases

For unknown domains, the desired process is not to let the model invent
durable writes freely. The desired process is:

```text
unknown-domain text
  -> profile_bootstrap_v1 proposal
  -> review and frontier tests
  -> approved profile package
  -> ordinary semantic_ir_v1 intake with deterministic admission
```

This is intentionally similar to a skill system: the model gets access to a
small relevant capability package when the utterance appears to need it. The
runtime still treats the model output as a proposal.

## Safety Rules

Profile selection must not bypass admission.

- A selected profile can add context, not authority.
- A selected profile can narrow the legal predicate palette, not silently
  broaden it.
- A selected profile can provide type validators, not turn inferred facts into
  committed facts.
- If two profiles plausibly apply, the system should choose `mixed` or
  `clarify` unless both profiles' safe writes can be separated cleanly.

This keeps domain awareness from becoming a hidden prompt hack.

## Open Research Questions

- Should profile selection be a separate small classifier, a Semantic IR
  pre-pass, or part of the same model call?
- How much domain context can be supplied before it distracts the model?
- Can the trace show "profile selected because..." clearly enough for review?
- Can profile validators replace more of the remaining Python rescue chain?
- When a turn crosses domains, should the gateway split it before Semantic IR
  or let one workspace represent the mixture?
- Should the profile selector be allowed to choose multiple profiles, or should
  multi-profile turns be segmented first?

The near-term answer is conservative: use explicit `active_profile` for
development when you need repeatability, and use `active_profile=auto` as a
measured experiment when testing domain switching.

## Control Plane Discipline

This can get complicated quickly if every subsystem is allowed to rewrite the
model context independently. The first implementation should keep orchestration
boring:

1. Build a thin roster of available profiles.
2. Select zero, one, or a small number of candidate profiles.
3. Load thick context only for the selected profile(s).
4. Run Semantic IR once on the focused input.
5. Let deterministic admission decide writes.
6. Log the roster, selected profile, thick context summary, and mapper outcome.

Dynamic context alteration is allowed only as an input-shaping step. It must not
change the admission rules invisibly. If profile selection becomes dynamic, the
trace should answer:

- Which profiles were visible?
- Which profile was selected?
- Why was it selected?
- What extra context was loaded?
- Which mapper/profile validators admitted or skipped each operation?

That trace is the pressure valve. Without it, the system risks becoming prompt
alchemy. With it, profile selection becomes another inspectable stage in the
governed compiler.

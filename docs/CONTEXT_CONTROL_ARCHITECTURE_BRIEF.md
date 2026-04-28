# Context Control Architecture Brief

Last updated: 2026-04-28

This is the broader architecture and research brief for the router/context
control direction. The operational description of the live turn path is
[Current Utterance Pipeline](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_UTTERANCE_PIPELINE.md).

## One-Sentence Shape

Prethinker is becoming a governed language-to-symbolic-state pipeline where an LLM controls **attention and semantic proposal**, while deterministic code controls **admission and durable truth**.

```text
raw utterance
  -> semantic_router_v1
  -> focused context package
  -> semantic_ir_v1
  -> deterministic mapper
  -> Prolog KB / query / clarification / quarantine / rejection
```

The project is not trying to make Python smarter at English. The current research direction is the opposite:

```text
LLM handles language.
Python handles structure.
Mapper handles authority.
```

This document is the shared mental model for the architecture we are converging on. Some pieces already exist experimentally; some still run through older Python front-door logic. The direction is clear:

```text
language work moves toward the LLM;
structural validation stays in Python;
truth admission stays deterministic.
```

## The Four-Layer Mental Model

The near-future system has four distinct layers.

```text
1. Context control
   LLM router decides what the next compiler pass should see.

2. Semantic proposal
   LLM compiler builds a rich semantic workspace.

3. Truth admission
   Deterministic mapper decides what can become KB state.

4. Symbolic execution
   Prolog runtime stores, retracts, queries, and explains.
```

The important point is that we are not simply "trusting the LLM more." We are trusting it with a different job.

```text
Trust the model with language and attention.
Do not trust the model with durable truth.
```

## What Is New Here

Earlier Prethinker mostly asked one constrained model call to parse the utterance, then relied on Python to rescue the awkward parts. The newer direction exposes more machinery to the model, but as a control plane:

- the domain/profile roster;
- recent context;
- compact KB visibility;
- predicate contracts;
- guidance modules;
- context availability;
- possible segmentation;
- retrieval hints;
- risk flags;
- bootstrap requests for unknown domains.

That makes the LLM more like an ingestion controller. It can say, "this turn needs legal claim/fact guidance, recent docket-like records, and a split before the query," without being allowed to assert any of those facts into the KB.

## Why This Pivot Exists

The older Prethinker design proved the authority boundary was valuable:

```text
model proposes
runtime decides
KB remembers
```

But it also exposed a bad pressure: Python started accumulating language-specific repairs:

- keyword routing
- query/write heuristics
- pronoun hints
- family relation rewrites
- story splitting
- medical vague-surface checks
- correction pattern recognizers

Those were useful for getting demos over the line, but they are not the glorious path. They make the system English-first, brittle, and increasingly specific to the test cases that hurt us last week.

The new design asks the stronger model to own more of the semantic front end. Not truth. Not mutation. But the messy language work:

- What kind of turn is this?
- Which domain pressures are present?
- What context would help?
- Does this need segmentation?
- Which ambiguity/risk modules matter?
- What KB state should be retrieved?
- What semantic workspace should be proposed?

That is context engineering as a first-class system capability.

## The Design Rule

```text
LLM controls attention.
LLM proposes semantics.
Deterministic code controls admission.
```

This distinction is everything.

The router can choose context. It cannot write facts.

The Semantic IR compiler can propose candidate operations. It cannot commit them.

The mapper can admit, skip, reject, quarantine, or ask for clarification. It cannot invent semantic meaning from the raw utterance.

## Core Objects

### Raw Utterance

The user-provided text. It may be:

- a single fact
- a query
- a correction
- a rule
- a long story
- a mixed fact/query turn
- non-English or noisy text
- cross-domain text

The architectural goal is that Python does not inspect this text for meaning.

Python may preserve the raw text, attach turn IDs, pass it to a model, validate exact span offsets, and log it. It should not ask, "does this English phrase look like a query?" or "does this noun imply a medical lab?"

### Domain Profile

A domain profile is a skill-like context package. It can provide:

- a description of when the profile is useful
- domain context
- allowed predicates
- predicate contracts
- profile-owned validators
- cautions and admission policy

Examples:

- `medical@v0`
- `legal_courtlistener@v0`
- `sec_contracts@v0`
- `story_world@v0`
- `probate@v0`

A profile gives the compiler better tools. It does not grant write authority.

Profiles are closer to skills than ontologies in the heavy academic sense. They tell the compiler what distinctions matter in a lane and give the mapper a predicate surface it can enforce.

### Guidance Module

A guidance module is a smaller reusable policy block. It is narrower than a profile.

Examples:

- `claim_vs_fact`
- `source_fidelity`
- `medical_advice_boundary`
- `contract_obligation_semantics`
- `rule_query_boundary`
- `temporal_scope`
- `correction_retraction`
- `identity_ambiguity`
- `predicate_contract_obedience`
- `non_english_normalization`

The router can request modules so the compiler receives the relevant warnings without carrying every rule all the time.

Guidance modules are how the system avoids one giant prompt manual. The router chooses the small set of reminders that matter for this turn.

### Semantic Router

`semantic_router_v1` is the proposed first model pass. It is a planner/context engineer.

It emits a strict control-plane object:

```json
{
  "schema_version": "semantic_router_v1",
  "selected_profile_id": "sec_contracts@v0",
  "candidate_profile_ids": ["sec_contracts@v0", "story_world@v0"],
  "routing_confidence": 0.86,
  "turn_shape": "mixed",
  "should_segment": false,
  "segments": [],
  "guidance_modules": [
    "contract_obligation_semantics",
    "temporal_scope",
    "rule_query_boundary"
  ],
  "retrieval_hints": {
    "entity_terms": ["shipment_h7", "ada"],
    "predicate_terms": ["frozen", "cleared", "transfer"],
    "context_needs": ["active clearance rules"]
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

The router does not emit facts, rules, queries, or mutations.

It may emit:

- which profile should be primary;
- which profiles are advisory;
- whether this is one turn or several exact spans;
- what context the compiler should receive;
- what KB terms are worth retrieving;
- which risks are present.

It may not emit:

- `assert_fact`;
- `retract_fact`;
- Prolog clauses;
- answers to the user;
- durable claims about the world.

### Harness

The harness is deterministic Python, but it should be structural only.

It may:

- validate router JSON
- reject unknown profiles
- reject unavailable profiles
- load selected profile packages
- load requested guidance modules
- retrieve compact KB context from structured hints
- split exact router-proposed spans
- assemble the compiler payload
- log all of it

It should not:

- decide a domain by keyword search
- decide query/write/rule shape from punctuation
- split prose by English sentence heuristics
- infer pronouns
- rewrite family relations
- classify medical ambiguity from raw text

In other words:

```text
Python may execute the plan.
Python should not linguistically invent the plan.
```

The harness is the membrane between model freedom and system discipline. It can say:

```text
The router asked for legal_courtlistener@v0 and medical@v0.
Both exist.
Legal will be primary.
Medical will be advisory only.
Load claim-vs-fact and medical-advice-boundary modules.
Retrieve KB entries mentioning Priya, warfarin, complaint, pharmacy log.
Now build the compiler packet.
```

That is not Python interpreting the utterance. It is Python executing a structured plan.

### Semantic IR Compiler

`semantic_ir_v1` is the second model pass. It receives the utterance or focused segment plus a sharpened context package.

It proposes a semantic workspace:

- entities
- referents
- assertions
- candidate operations
- unsafe implications
- clarification questions
- support links
- conflicts
- retraction plans
- derived consequences
- self-check notes

This is where language becomes a structured proposal.

The compiler is allowed to be much more semantically ambitious than the mapper. It can represent possibilities, ambiguities, inferred risks, and unsafe implications because those do not become truth just by existing in the workspace.

### Mapper

The mapper is deterministic admission control.

It decides what, if anything, can become durable KB state.

It checks:

- JSON/schema shape
- allowed predicate palette
- arity
- argument contracts
- profile validators
- direct vs inferred source
- safe vs unsafe operation labels
- claim vs fact boundaries
- negative fact policy
- rule admission policy
- retraction safety
- source/context write blocking
- temporal sanity
- duplicate operations
- stored KB conflicts

The mapper is the firewall.

This is the part that keeps the project from becoming "structured output plus vibes." Even when the router and compiler are smart, the mapper is allowed to be boring, strict, and stubborn.

### Prolog KB

The KB is durable symbolic state.

It may receive:

- admitted facts
- admitted rules
- admitted retractions

It may answer:

- queries
- derived consequences
- contradiction/conflict checks

It should not receive:

- raw LLM guesses
- unsafe implications
- inferred facts that lack admission
- context copied as a new write
- claims promoted to truth

The KB is where soft language becomes hard memory. That conversion is intentionally difficult.

## Near-Future Soup-To-Nuts Pipeline

### 1. Receive the raw utterance

The UI or harness sends the utterance to the pipeline.

The text is preserved exactly. Python may store and transmit it, but should not interpret it.

### 2. Build a thin router packet

The harness assembles a small packet for `semantic_router_v1`:

- raw utterance
- recent context summary
- thin domain profile roster
- profile availability flags
- available guidance modules
- compact KB manifest
- routing policy

This is deliberately thinner than the compiler payload. The router is choosing context, not compiling the full semantic workspace.

The router packet should eventually include only enough information to choose the next context. It should not contain the entire thick domain prompt unless routing itself requires it.

### 3. Router chooses the attention plan

The router answers questions like:

- Which profile best owns this turn?
- Are there secondary domain pressures?
- Is this a story, query, correction, rule, or mixed turn?
- Should it be segmented?
- Which exact spans should be processed separately?
- Which guidance modules should be loaded?
- Which entities/predicates should be used for KB retrieval?
- Is this an unknown-domain bootstrap case?

The output is strict JSON.

A good router output is not "clever prose." It is a compact control-plane object the harness can validate.

### 4. Harness validates the router plan

The harness does not simply obey.

It checks:

- Does the selected profile exist?
- Is profile context available?
- Are requested modules known?
- Are segment texts exact source spans?
- Is confidence low?
- Is the router asking for bootstrap?

If the plan is invalid, the harness can fall back to:

- `general`
- primary profile only
- no segmentation
- clarification
- bootstrap review mode

This is how the system avoids coupled hallucination.

The router is powerful, but not privileged. If it asks for a profile that is not installed, requests a segment that is not an exact source span, or routes with low confidence into a high-risk domain, the harness can refuse the plan or ask for clarification.

### 5. Multi-domain handling is decided

We should avoid the phrase "merged ontology" for now.

The safer design is **multi-domain handling**:

```text
single_domain:
  one profile owns the whole turn

primary_plus_advisory:
  one profile owns admission; other profiles only add caution/context

split_by_segment:
  router splits the turn into domain-specific spans

clarify_domain:
  ask when profile ownership changes meaning

bootstrap_or_general:
  use general/profile-bootstrap when no known lane fits
```

This is not a blended ontology. It is coordinated lanes.

For example:

```text
The complaint says Priya stopped warfarin,
but the pharmacy log says she picked it up Monday.
```

Possible handling:

```text
primary profile: legal_courtlistener@v0
advisory profile: medical@v0
modules:
  claim_vs_fact
  legal_claim_finding_boundary
  medical_entity_normalization
  medical_advice_boundary
  temporal_scope
```

The legal profile owns the claim/log/provenance problem. The medical profile warns that warfarin is medication and clinical advice boundaries apply.

The motto:

```text
Multiple domains may inform attention.
Only explicit lanes govern admission.
```

This is the safer answer to "medical plus legal" or "story plus contract" turns. We do not need to invent one merged super-ontology. We need a routing policy that can say:

```text
This turn has multiple pressures.
One lane owns admission for this segment.
Other lanes may add warnings, normalization hints, or clarification pressure.
```

If two lanes both want to own writes, the safer near-term move is segmentation or clarification, not palette blending.

### 6. Harness assembles focused compiler context

The compiler payload can include:

- utterance or exact segment
- router plan summary
- router authority warning
- primary profile context
- advisory profile cautions, if enabled
- guidance modules
- allowed predicates
- predicate contracts
- compact KB context
- recent accepted turns
- model/runtime settings

The important change is that the model helped choose this context.

This is the meaty center of the new architecture: dynamic context assembly. The compiler is no longer a static prompt plus user text. It gets a carefully shaped workspace:

```text
what the user said
what just happened recently
what domain lens is active
what predicates are legal
what the KB currently remembers nearby
what risks to preserve instead of collapse
```

### 7. Semantic IR compiler proposes a workspace

The compiler emits `semantic_ir_v1`.

It is allowed to be semantically ambitious:

- resolve clear referents
- preserve ambiguous referents
- distinguish claim from fact
- notice conflicts
- propose retraction plans
- propose query operations
- preserve temporal scope
- identify unsafe implications
- ask clarifying questions

It is not allowed to be authoritative.

The workspace is the place where meaning can be rich before truth becomes narrow.

### 8. Mapper performs deterministic admission

The mapper sees candidate operations and decides:

```text
admit
skip
clarify
quarantine
reject
answer/query
```

If multi-domain handling is active, the simplest near-term policy is:

```text
primary profile owns admitted writes.
advisory profiles can add warnings and risk context.
```

Later, we can consider profile-tagged candidate operations:

```json
{
  "operation": "assert",
  "predicate": "taking",
  "args": ["priya", "warfarin"],
  "profile_source": "medical@v0"
}
```

But that should wait until the simpler primary/advisory path is proven.

The mapper may also override the model's top-level decision. If the model says `commit` but every candidate operation is inferred, unsafe, out-of-palette, or contradicted by stored state, the mapper can return quarantine, clarification, or rejection.

### 9. Runtime executes admitted operations

The runtime applies admitted operations:

- assert facts
- retract facts
- assert rules
- run queries
- hold pending clarifications
- quarantine unsafe proposals
- reject unsafe advice requests

Query results and mutation ledgers are written into trace output.

This is where Prethinker becomes visibly different from a chatbot. A normal assistant can summarize what it thinks. Prethinker can show exactly what changed, exactly what was skipped, and exactly which rules or facts supported a query.

### 10. UI exposes the whole chain

The UI should eventually show:

- router decision
- profile/context package
- segmentation plan
- model input summary
- Semantic IR workspace
- mapper diagnostics
- admitted/skipped operations
- KB mutations
- query results
- conflict/retraction plans

The user should be able to see:

```text
why the model looked at this domain
what context it received
what it proposed
what the mapper allowed
what entered the KB
what was refused
```

This turns the UI into a real human test bed.

The UI should eventually make every layer inspectable without flooding the user:

```text
Router: why this profile/context was chosen.
Compiler input: what the model actually saw.
Semantic workspace: what the model proposed.
Mapper: what was admitted, skipped, or challenged.
Runtime: what entered the KB and what query results came back.
```

## Current Versus Soon

### Current Live Path

The current live server still contains Python-side front-door logic:

- profile selection by term scoring
- query/write heuristics
- story/query segmentation heuristics
- some legacy rescue and normalization code

The Semantic IR path has greatly reduced Python rescue dependence, but Python still touches language before the model in several places.

### Current Experiment

The new router experiment proves the staged design:

```text
semantic_router_v1
  -> router-crafted context
  -> semantic_ir_v1
  -> mapper
```

Recent focused result:

```text
16-case router-only:
router_ok=14/16
router_score_avg=0.969

16-case router -> compiler:
router_ok=14/16
compiler_parsed_ok=16/16
```

The remaining router misses are mostly legal/probate taxonomy tension, not broken JSON or compiler failures.

### Near-Future Live Path

The next live architecture should move toward:

```text
process_utterance()
  -> semantic_router_v1
  -> harness validates plan
  -> context assembler
  -> semantic_ir_v1
  -> mapper
  -> runtime
  -> UI trace
```

Legacy Python language handling should be retired, hidden behind A/B flags, or kept only for historical comparison.

## What Gets Exposed To The LLM

We are not necessarily adding more complexity to the system. We are exposing more of the right machinery to the model:

- profile roster
- profile descriptions
- context availability
- guidance module names
- KB manifest
- predicate contracts
- compact current KB state
- recent turn summaries

The model is not being handed authority. It is being handed better control over its own working context.

This is the subtle but powerful move:

```text
the LLM is not trusted more with truth;
it is trusted more with attention.
```

That is why the router experiment matters. It is the first step toward making the model responsible for context engineering instead of having Python keyword logic choose the world for it.

## What Still Belongs In Python

The wall sign is "NO LANGUAGE HANDLING IN PYTHON," not "NO PYTHON."

Python should still do the things software is good at:

- validate JSON;
- enforce schemas;
- enforce predicate arity;
- enforce predicate contracts;
- reject unavailable profiles;
- verify exact segmentation spans;
- retrieve KB clauses from structured hints;
- apply token budgets;
- run Prolog queries;
- apply admitted mutations;
- render traces;
- score tests.

The line is raw-language interpretation. Python should not grow a private shadow NLP system.

## What Moves Toward The LLM

These are the areas we should keep migrating away from Python heuristics:

- domain/profile selection;
- query/write/rule/correction turn shape;
- long-utterance segmentation;
- pronoun and referent interpretation;
- messy family/social relation parsing;
- vague medical surface interpretation;
- non-English normalization;
- source-fidelity decisions;
- deciding which KB facts are relevant context;
- detecting when a new domain needs bootstrap mode.

The LLM may still be wrong. But when it is wrong, we should improve the router prompt, compiler prompt, profile package, schema, or test pack before adding another English-specific Python rescue.

## Open Design Questions

### Should routing and compiling use the same model?

For now, yes. The same 35B model with different prompts is simple and avoids VRAM thrash.

Later, a smaller router model may make sense:

```text
small router model
larger compiler model
```

But only after the router schema/policy stabilizes.

### Should the router call tools or research unknown domains?

Eventually, maybe.

Near-term, bootstrap mode should only propose:

- candidate domain name
- missing conceptual tools
- candidate predicate concepts
- need for profile-building/research

It should not install a new ontology by itself.

### Should multi-domain turns merge predicate palettes?

Not yet.

First version:

```text
primary profile owns admission.
advisory profiles supply warnings/context.
```

Second version, if needed:

```text
profile-tagged candidate operations.
```

Avoid a mushy merged ontology until we have evidence that explicit lanes are insufficient.

### Should the router own segmentation?

Yes, eventually. The router should propose exact spans and segment roles. Python should validate exact spans and preserve order.

This matters because segmentation is language work. Query boundaries, corrections, quoted claims, and narrative shifts are not always marked by English punctuation, and they will be even less reliable in noisy or non-English inputs.

### How do we prevent router mistakes from poisoning the compiler?

Keep router output structured and advisory.

Add diagnostics:

- low-confidence router plus aggressive commit
- selected profile unavailable
- candidate profile disagreement
- compiler operations outside profile contract
- router says medical but compiler emits legal ops
- router asks for bootstrap but compiler commits anyway

The pre-router selector comparison has served its purpose and is no longer part of the
current path. New measurements should focus on router decision quality,
anti-coupling diagnostics, compiler validity, and mapper/admission outcomes.

### Can unexpected domains work?

The honest answer is: not as ordinary durable writes yet.

The future shape is bootstrap mode:

```text
unknown domain text
  -> router says no installed profile owns this
  -> bootstrap/profile-proposal mode
  -> candidate predicates and risks
  -> human or deterministic review
  -> approved profile
  -> normal governed intake
```

The model can help design a domain surface. It should not self-install a domain and immediately start writing durable facts.

## The Near-Term Implementation Path

The clean next steps are:

1. Keep `semantic_router_v1` experimental but visible in traces.
2. Add router bubbles to the UI debug view.
3. Convert guidance module names into small loadable context blocks.
4. Add router-proposed exact-span segmentation.
5. Run noisy, non-English, and mixed-domain agility tests.
6. Wire router-first context assembly into `process_utterance()` behind a flag.
7. Retire or hide older Python language heuristics as each model-controlled piece proves itself.
8. Track the metric that matters: less raw-language Python without higher bad-commit rate.

## What We Are Trying To Understand

The core research question is becoming:

> Can a capable LLM act as a context engineer and semantic compiler while deterministic code remains the authority over durable symbolic state?

If yes, Prethinker becomes something stronger than "English to Prolog."

It becomes:

```text
a governed semantic intake layer
for turning natural language into auditable symbolic memory
without letting the model own truth.
```

That is the thing we are building.

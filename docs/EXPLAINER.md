# Prethinker Explainer

This is the plain-language explanation of what Prethinker is trying to become, what it already does well, and where the boundaries still are.

## The Short Version

Prethinker is a governed adapter that can sit in front of a conversational model and turn parts of a dialogue into auditable symbolic state.

It is not trying to be "a smarter chatbot."

It is trying to do something narrower and, in some settings, more useful:

- watch language as it happens
- decide which turns are safe to formalize
- compile those turns into Prolog-style facts, rules, queries, or retracts
- keep that state deterministic and inspectable

The right metaphor is not just "memory."

It is closer to a governed stenographer and compiler.

## Why This Exists

Ordinary chat systems are good at sounding coherent across a conversation, but they are weak at durable state discipline.

They often:

- forget
- blur revisions into summaries
- lose argument direction
- answer confidently from fuzzy context
- mutate their implied world model without leaving an audit trail

Prethinker exists to intercept that problem.

Instead of letting "whatever the model currently thinks" become the hidden state of the interaction, it tries to create:

- explicit symbolic memory
- explicit ambiguity handling
- explicit mutation authority
- explicit evidence for why a state change happened

## The Product Vision

The long-term product shape is a UI or adapter layer that can sit in front of a user's chatbot of choice.

In that shape:

- the chatbot remains the conversational engine
- Prethinker watches the interaction stream
- eligible turns get compiled into symbolic operations
- the resulting KB becomes durable, queryable memory outside the chatbot's private context window

So yes, Prethinker can be thought of as a kind of stenographer.

But not a passive stenographer.

It is a governed stenographer:

- it does not record everything verbatim as durable truth
- it does not commit uncertain meaning automatically
- it can ask for clarification
- it can refuse a write
- it can show exactly what it believes was committed

## The Two Roles We Care About

### Prethinker

`Prethinker` is the strict role.

Its job is to:

- read the current utterance
- classify the intent
- emit a structured compiler object
- pass that object through deterministic validation and normalization
- allow or deny KB mutation

Prethinker is the authority boundary.

It is intentionally caged:

- schema-bound
- guarded
- allergic to guessing

### Freethinker

`Freethinker` is the planned clarification liaison.

Its job is not to write to the KB.

Its job is to help when Prethinker hesitates.

Freethinker can:

- watch recent context
- track likely referents across turns
- propose a better clarification question
- sometimes suggest a grounded referential resolution
- abstain when weak

Freethinker is not a second authority.

The constitutional rule is:

- Freethinker may suggest.
- Prethinker decides.

## Why Not Just One Bigger Model?

This is the obvious question, and it is a good one.

Why not just give one `qwen3.5:9b` a larger context window, a strong prompt, and let it do both the compiling and the clarification work?

That may turn out to be enough for some slices, but the jobs pull in different directions:

- the compiler role should be narrow, auditable, and conservative
- the clarification role should be softer, more contextual, and better at discourse continuity

When one role must both "never guess" and "use context intelligently," drift starts to creep in.

So the split is not really "two different intelligences."

It is:

- one authority role
- one advisory role

Even if both are backed by the same underlying 9B model family.

## What The System Actually Does On A Turn

At a high level:

`utterance -> proposed operation -> deterministic gate -> apply/query -> evidence`

More concretely:

1. A turn arrives.
2. Prethinker classifies it as a write, query, rule, retract, or `other`.
3. The parser proposes a structured operation.
4. The runtime checks schema, shape, registry/type rules, and ambiguity policy.
5. If accepted, the deterministic runtime mutates or queries the KB.
6. The result is recorded with provenance and can be inspected later.

That means the LLM is allowed to propose structure.

It is not allowed to become the authority on state.

## Where The System Gets Strong

Prethinker is strongest when the task is:

- stateful
- inspectable
- mutation-sensitive
- queryable after the fact

Examples:

- "Remember that Scott runs the bakery."
- "Actually, Blake runs it now."
- "Who runs the bakery?"
- "Keep the prior timeline but retract the false transfer."

Those are the kinds of turns where deterministic memory discipline matters more than conversational style.

## Failure Modes That Still Matter

The failures that matter most are not usually total collapse.

They are near-correctness.

### 1. Argument direction illusions

English form is a bad guide to Prolog argument order.

- "A is B's parent"
- "A has B as a parent"
- "A is parented by B"

These sound similar and can map to different logical direction.

### 2. Multi-clause turns that sound easy

Longer turns are not just bigger turns.

They often contain:

- multiple facts
- corrections
- sequencing
- query intent mixed with write intent

The system can semantically "understand" them while still serializing them badly.

### 3. Clarification that either helps or annoys

The right question is not "ask more" versus "ask less."

It is whether clarification is being used at the right moments.

Clarification helps when:

- referents are unresolved
- predicate direction is genuinely unclear
- the write would otherwise be speculative

Clarification hurts when:

- the parse is already deterministic
- the system is asking internal ontology questions a user should never see
- the model is being starved of obvious local context

### 4. Narrative compression

Long-form inputs can still "pass" while under-capturing the story.

That is why the project measures:

- coverage
- precision
- exam quality
- temporal exam quality

not just whether the pipeline technically completed.

## What Makes This More Than Prompt Theater

The project does not rely only on one system prompt and vibes.

The working stack is:

- shared prompt doctrine
- per-pass schema wrappers
- deterministic validation and normalization
- optional registry/type gates
- persistent KB state
- interrogator-style scoring and report generation

That is also why the repo is careful about honesty:

- stable proof lanes are not the same thing as frontier wins
- historical good-looking scores are not reused if the constraints were not real
- docs are expected to follow the evidence, not flatter it

## What We Know Today

As of April 19, 2026:

- the safety gate is green at `120 passed`
- strict Blocksworld remains the stable proof lane
- strict narrative packs are materially stronger than their first honest post-registry baseline
- the console is now the canonical interactive front door
- Freethinker is a real design-track capability, but still policy-off by default

The important subtlety is this:

the system is stronger today as a governed parser stack than it is as a broad raw-language front door.

That is real progress.
It is not the same as universal robustness.

## What This Does Not Claim

Prethinker does not claim:

- universal semantic parsing
- freeform conversational reasoning as authority
- zero-error open-domain understanding
- production readiness across legal, medical, and arbitrary wild language all at once

What it does claim is narrower:

- deterministic memory discipline
- auditable language-to-logic mutation
- explicit trust boundaries
- a measurable path for improvement

## Why This Is Interesting

If language can be compiled into durable symbolic state under governance, then a user can:

- narrate a world
- revise it
- query it
- inspect the record of how it changed

without giving a probabilistic conversational model silent authority over the world state.

That is the interesting bet here.

Not "a chatbot that sounds smarter."

A conversation-adjacent system that makes stateful reasoning inspectable.

![Prethinker control plane: natural-language input flows through interception, normalization, clarification/confirmation gates, then deterministic KB mutation](D:/_PROJECTS/prethinker/docs/assets/prethinker-control-plane-infographic-v2.png)

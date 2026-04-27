# Prethinker: From Language Parsing to Truth Admission

Date: 2026-04-26

## Short Version

Prethinker started as an experiment in translating natural language into a
small Prolog-like knowledge base. The early question was simple: can a local
language model turn ordinary utterances into durable symbolic facts without
quietly hallucinating?

The answer so far is more interesting than "yes" or "no."

The project is no longer just an English-to-Prolog parser. It is becoming a
governed semantic intake system:

```text
utterance
  -> semantic_ir_v1 workspace
  -> deterministic admission mapper
  -> KB mutation, query, clarification, quarantine, or rejection
```

The key discovery is that the central problem is not making the model "reason"
in the abstract. The central problem is deciding what the system is allowed to
remember as truth.

Prethinker is becoming a truth admission system.

## The Original Failure Mode

The first working design was deliberately conservative. A smaller local model
would propose Prolog-ish facts, then Python would validate, normalize, repair,
or reject the output before anything entered the KB.

That got useful demos running. It also exposed a serious architectural smell.

Every hard language case tempted us to add another Python rescue:

- pronoun repair;
- possessive rewrite;
- family relationship expansion;
- inverse relation cleanup;
- subject-prefixed predicate canonicalization;
- medical ambiguity holds;
- correction special cases;
- route heuristics;
- clarification sanitizers.

Some guardrails are good. A governed memory system needs hard policy. But
Python was starting to do too much semantic interpretation after the model had
already under-expressed the situation.

The risk was clear: the system could become a catalog of remembered failures,
not a scalable semantic compiler.

## The Pivot

The newer direction changes the role of the model.

The old shape was:

```text
small LLM
  -> Prolog-like parse
  -> Python repair logic
  -> KB
```

The new shape is:

```text
stronger LLM
  -> rich semantic workspace
  -> deterministic admission gate
  -> KB
```

The LLM is no longer asked to jump directly from messy language to final
durable facts. Instead, it builds `semantic_ir_v1`: an intermediate workspace
that can hold ambiguity, claims, direct assertions, candidate operations,
unsafe implications, polarity, source labels, and self-check notes.

That workspace is not truth. It is a proposal.

The deterministic mapper remains the authority. It decides which proposed
operations are admissible, which must be skipped, and which should force
clarification, quarantine, rejection, or a mixed outcome.

This preserves the original safety thesis while using more of the model's
semantic ability.

## Why This Matters

Most LLM memory systems blur three things:

- what the user said;
- what the model inferred;
- what the system now believes.

Prethinker tries to keep those separate.

For example, if a witness says "Mira removed the morphine box," but a pharmacy
log says "M. Vale accessed Room 4B," the system should not immediately assert:

```prolog
removed_from(mira, morphine_box).
```

That would be a bad memory write. It turns a claim into world state, and it
also collapses the identity ambiguity around "M. Vale."

The desired behavior is more like:

```text
claim detected
observed log detected
identity ambiguity detected
unsafe implication detected
do not commit the disputed claim as truth
```

That is exactly the kind of distinction the Semantic IR path is now beginning
to make.

## What We Have Learned

### 1. The Model Should Do More Semantic Work

The stronger local model, currently `qwen/qwen3.6-35b-a3b` through LM Studio
structured output, is substantially better at filling a rich workspace than the
older tightly constrained small-model path.

It can often recognize:

- claims versus observed facts;
- direct assertions versus implications;
- ambiguous initials and aliases;
- correction targets;
- temporal intervals;
- rule-like language;
- unsafe medical advice boundaries;
- fact-plus-query and fact-plus-rule turns.

This does not mean the model should be trusted. It means the model can produce
a better object for deterministic code to judge.

### 2. Structured Output Solves Syntax, Not Truth

LM Studio structured output has been useful because it keeps the JSON shaped
correctly. That lets the experiments focus on semantic correctness instead of
broken syntax.

But schema obedience is not the same as safe memory admission.

A model can produce perfect JSON and still label the turn incorrectly. This
showed up clearly in the Harbor frontier pack: the raw model decision label was
often less reliable than the mapper-projected runtime decision.

That is a useful result. It says the architecture should not treat the model's
top-level label as authority. The mapper should compute its own admission view
from the structure.

### 3. The Mapper Is Not Just a Rubber Stamp

The deterministic mapper now does real work:

- skips context restatements;
- blocks unsupported negative facts;
- enforces predicate palettes;
- prevents out-of-palette writes;
- blocks unsafe inferred writes;
- projects partial safe writes plus unsafe material to `mixed`;
- treats unresolved rule/constraint validity notes as admission pressure;
- records admitted and skipped operations with diagnostics.

This is the "governed" part of the governed semantic compiler.

The model proposes. The mapper disposes.

### 4. The Best Metric Is Not Just "Did the Model Pick the Right Label?"

Early evaluations mostly asked whether the model chose the expected decision:
`commit`, `clarify`, `quarantine`, `reject`, `answer`, or `mixed`.

That is still useful, but it is not enough.

The better question is:

```text
What actually reached the KB?
What was skipped?
Why was it skipped?
Did unsafe material stay out?
Were safe direct facts admitted?
```

The Harbor frontier results made this concrete.

Latest local Harbor pass:

| Metric | Result |
|---|---:|
| Scenarios | 14 |
| JSON valid | 14/14 |
| Schema valid | 14/14 |
| Raw model decision labels | 13/14 |
| Mapper-projected decision labels | 14/14 |
| Admission contracts | 14/14 |
| Admission checks | 52/52 |
| Admitted ops | 25 |
| Skipped ops | 15 |
| Average latency | 6.4s |

That gap is important. The model's administrative label was imperfect, but the
structured workspace contained enough signal for the mapper to recover the safe
runtime outcome.

The newer admission-contract score is even closer to the real question. It
checks whether required facts, retracts, and queries reached the runtime
surface, and whether forbidden facts stayed out. That moves the benchmark from
"did the model choose the right label?" toward "what crossed the truth
boundary?"

### 5. Refusal to Commit Is a Feature

The most impressive behavior is not a clever answer. It is refusing to poison
the KB.

Examples from the current frontier packs:

- `S. Hale` could be Silas Hale or Selene Hale, so the system clarifies instead
  of inventing identity.
- `M. Vale` could be Mira Vale or Mara Vale, so the system can correct an alias
  timestamp without resolving the alias prematurely.
- "The court did not find that Pavel approved it" is treated as absence of
  finding, not durable proof of negative approval.
- "All night-shift nurses except Omar signed..." is recognized as a quantified
  group statement, but admission policy still has to decide whether individual
  expansion is allowed.
- "Ada approved H7 on June 4, but her authority was revoked June 1 and
  reinstated June 8" records direct temporal facts while treating the approval's
  validity under the rule as unresolved.

This is where the architecture has teeth. It can say:

```text
I understand the shape of what was said.
I also know this should not become durable truth yet.
```

## What This Is Not

This is not a general medical reasoning system.

The medical profile is intentionally bounded. It has a small predicate palette
for medication use, conditions, symptoms, allergies, lab tests, lab result
states, and pregnancy. UMLS is used as a local normalization and semantic-type
aid, not as a license to perform broad clinical inference.

This is also not proof that the system can perfectly compile arbitrary natural
language into logic. Temporal language, default rules, exceptions, identity
resolution, negation, and cross-document provenance remain hard.

The claim is narrower and more useful:

```text
A capable model can build a rich semantic proposal.
A deterministic gate can decide what is safe to admit.
The trace can show every step.
```

## Why This Feels Different From a Normal LLM Agent

Most agent systems use the LLM as the center of authority. The model reasons,
answers, stores memory, and often decides what matters.

Prethinker is trying to move authority away from the model.

The LLM is treated as a semantic worker. It can be intelligent, holistic, and
useful, but its output is provisional. Durable state belongs to the runtime,
not the model.

That distinction matters for any system where memory has consequences.

If an agent writes a bad summary, that is annoying. If it writes a bad fact into
a durable KB and future decisions build on it, that becomes much worse.

The hard problem is not "can the model say something plausible?"

The hard problem is:

```text
What is allowed to become future context?
```

## Where We Are Going

### Predicate Contracts

The next layer is stricter predicate contracts:

- argument order;
- entity types;
- event versus state;
- temporal scope;
- functional versus non-functional predicates;
- admissible correction and retraction behavior.

Without this, the IR can become semantic soup. With it, the mapper can enforce
clear contracts instead of relying on vibes.

### Admission-Level Test Batteries

Decision labels are too coarse. The next batteries should score:

- `must_admit`;
- `must_skip`;
- `must_skip_reason`;
- `must_query`;
- `must_not_write`;
- `must_preserve_claim_not_fact`;
- `must_preserve_alias_ambiguity`;
- `must_not_derive_temporal_consequence`.

This is where the project can become much more rigorous.

### Rule Ingestion

The model already recognizes rule-like language. The mapper can admit simple
Horn rules when a precise executable clause is available.

The next question is how to handle:

- unless;
- except;
- only if;
- before/after;
- revocation;
- default rules;
- policy priority;
- rule versioning.

The right move is probably not to admit all rule-shaped prose. It is to admit a
small, well-specified subset and quarantine the rest.

### Identity Resolution

Identity is one of the hardest edges.

Right now the system correctly refuses to over-ground ambiguous aliases. That
is good. But future versions need explicit identity states:

- unresolved;
- ambiguous;
- alias-preserving;
- resolved by context;
- resolved by user;
- resolved by trusted document.

Identity should become a first-class admission problem, not a pile of name
normalization hacks.

### Trace UX

The trace is becoming part of the product.

It should show:

```text
input utterance
model workspace
candidate operations
mapper admission
admitted facts
skipped operations
skip reasons
KB outcome
```

This is what makes the system inspectable. It also makes progress visible to
people who do not want to read the code.

## The Research Bet

The bet is not that a model can be perfect.

The bet is that a model can be good enough at semantic organization to produce
a useful workspace, and deterministic admission can prevent the dangerous parts
from becoming durable state.

In one line:

```text
soft semantic intelligence proposes; hard symbolic governance admits.
```

That is the current shape of Prethinker.

## Possible HN/X Framing

Working title:

> I stopped trying to make an LLM remember things, and started building a gate
> for what it is allowed to remember.

Short pitch:

> Prethinker is a local experiment in governed symbolic memory. A stronger LLM
> turns messy language into a rich Semantic IR workspace, but deterministic code
> decides what can become durable Prolog-like state. The surprising discovery:
> the hard problem is not generating facts. It is truth admission.

Thread outline:

1. Started as English-to-Prolog.
2. Hit the Python rescue trap.
3. Switched to Semantic IR.
4. Let the LLM do richer semantic interpretation.
5. Kept deterministic code as the authority.
6. Tested with messy legal/medical/temporal frontier packs.
7. Found that raw model labels are imperfect, but mapper-projected admission can
   still be safe.
8. Current frontier: predicate contracts, rule ingestion, identity resolution,
   trace UX.

## Current Verdict

Prethinker is not a finished product and not a solved research problem.

But it has crossed an important line. It is no longer just a parser demo. It is
a credible architecture for controlled symbolic memory ingestion:

```text
language -> semantic workspace -> governed truth admission -> auditable KB
```

That is worth pushing.

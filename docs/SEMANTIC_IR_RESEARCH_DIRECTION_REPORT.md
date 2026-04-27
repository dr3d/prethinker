# Prethinker Research Direction: From Guarded Parsing to Semantic IR

Last updated: 2026-04-26

## Short Version

Prethinker started with a strong authority-boundary idea: a language model may
propose what an utterance means, but deterministic code decides what can become
durable Prolog-like state. That idea still looks right.

The part we are rethinking is how much semantic work should happen in Python
after a small, tightly constrained parser model emits a brittle parse. The old
path was becoming crowded with English-specific rescue logic: pronoun repairs,
family-relationship rewrites, predicate canonicalizers, correction special
cases, and medical ambiguity holds. Those guardrails made the demos safer, but
they also raised a research concern: were we building a governed semantic
compiler, or just accumulating patches for the latest test case?

The new direction is to give a stronger local model more responsibility for the
semantic understanding step, while keeping the deterministic runtime as the
authority layer. Instead of asking the model to jump straight from English into
Prolog-ish facts, we ask it to build an intermediate semantic workspace:

```text
utterance + context
  -> semantic_ir_v1 proposal
  -> deterministic mapper and gate
  -> safe KB mutation, query, clarification, quarantine, or rejection
```

The bet is simple: a capable LLM should be better than hand-written Python at
forming a broad, holistic interpretation of messy language. Python should still
validate, normalize, reject, and execute. It should not have to keep learning
English one special case at a time.

![Prethinker semantic IR workspace](assets/prethinker-semantic-ir-workspace.png)

## Why We Are Changing Direction

Prethinker has always been strongest at the boundary between language and
durable state. The product idea is not "chatbot memory." It is governed memory:
natural language can suggest a change, but the runtime must decide whether that
change is admissible.

That authority boundary produced good behavior in the UI. It could hold vague
medical utterances instead of guessing, show the user why a turn needed
clarification, and commit only inspected KB mutations. It also gave us a strong
debugging cockpit: route, clarification, commit/block state, and ledger traces
were visible instead of hidden behind a friendly answer.

But the older implementation used a fairly constrained smaller local semantic
parser. Because that parser was boxed tightly, Python increasingly had to rescue
language understanding after the fact. The rescue code was useful, but the shape
was worrying.

Examples of pressure we saw:

- coreference hints and clarification carry-forward for pronouns
- possessive and family-bundle rewrites
- same-clause spouse and family-anchor normalization
- inverse possessive repairs
- subject-prefixed predicate canonicalization
- route heuristics for write/query/mixed turns
- special correction handling for "not X, Y instead"
- medical ambiguity and allergy-vs-intolerance holds
- predicate normalization after the model emitted awkward forms

None of those are bad in isolation. In fact, many are exactly what made the
system safer. The concern is the direction of travel. If each new scenario
requires a new Python semantic patch, then the system is not generalizing. It is
becoming a catalog of remembered failures.

That is the core reason for the new research lane.

## Retired Sidecar Lesson

An earlier clarification-sidecar design helped clarify the permission boundary:
a helper could suggest context, but only Prethinker and the deterministic mapper
could authorize writes. That was useful as a design exercise, but it is not the
current mainline.

The bigger issue was upstream: the main parser was still a tightly caged model
being asked to emit a narrow parse. When it missed the shape of an utterance, a
sidecar could sometimes improve a question, but it did not remove the need for
Python to perform increasingly specific semantic repair.

That is why we are now exploring a more fundamental change:

```text
not: small parser -> Python semantic rescue -> KB gate
but: stronger model -> explicit semantic IR -> deterministic KB gate
```

## The New Idea: Semantic Workspace Before Prolog

The new path is called `semantic_ir_v1`.

The model no longer has to emit final Prolog. Instead, it emits a structured
intermediate representation with:

- entities and normalized names
- referents and ambiguity status
- direct assertions
- claims versus observed facts
- unsafe implications
- candidate operations
- polarity
- source: direct, inferred, or context
- safety: safe, unsafe, or needs clarification
- clarification questions
- a self-check with bad-commit risk and missing slots

This gives the LLM room to use more of its actual strength. It can look at the
utterance as a whole, track discourse context, distinguish claim from fact,
preserve negation, and notice when a rule, query, correction, and unsafe
implication are tangled together.

The deterministic layer still owns admission. The mapper is intentionally
conservative:

- safe direct assertions may become facts
- safe queries may become queries
- safe retractions may become retractions
- unsafe and inferred operations can be skipped
- quantified group atoms can be blocked unless expanded safely
- rules require explicit rule structure before admission
- quarantine, reject, and clarify decisions do not silently write facts

This is not "let the big model write the KB." It is closer to:

```text
let the big model propose a richer workspace;
let deterministic code decide what survives.
```

## Newest Console Extension: Segmented Story Ingestion

The latest UI/gateway work applies the same architecture to long narrative
inputs. A full story should not be forced through one giant model response that
summarizes away concrete events. The console can now split story-like utterances
into focused line/sentence segments, run each segment through the canonical
`process_utterance()` Semantic IR path, and aggregate the admitted mutations for
the visible ledger turn.

The important design constraint is that this is not a story-specific parser.
Each segment still goes through:

```text
segment text
  -> semantic_ir_v1 workspace
  -> deterministic mapper/palette/grounding admission
  -> Prolog tool execution
```

This exposed the next useful boundary. The model was able to understand the
story, but the old generic predicate palette gave it poor legal targets, so it
overused broad predicates like `inside/2`, `at/2`, and `carries/2`. The fix was
structural: add a small generic story-world palette (`tasted/2`, `sat_in/2`,
`lay_in/2`, `broke/1`, `asleep_in/2`, passive observed-state predicates, and
movement predicates), and block placeholder durable writes such as
`unknown_agent`.

On the Goldilocks roundtrip story, the current smoke run produced `56` deduped
mutations across `50` segments in about `180s`. More important than the count,
the failure shape improved: earlier artifacts like `unknown_agent`,
voice-as-`carries`, nonsensical `inside(...)` facts, and stray body-part facts
were removed. The remaining questions are now cleaner research problems:
stable object identity, observed-event representation, and temporal/event
ordering.

The same segmentation idea now applies to long mixed turns with explicit
queries. Query boundaries are treated as natural breaks because a question
changes the mode of the turn: surrounding text may assert state, while the
question should remain a query target rather than becoming another fact-like
candidate. This is another structural boundary, not a domain patch.

## Why a Smarter Model Might Reduce Python Guardrails

The hope is not that a larger model makes guardrails unnecessary. The hope is
that it changes what kind of guardrails we need.

The old style of guardrail was often English-specific:

```text
if the model says this awkward predicate, rewrite it
if the utterance has this family phrase, expand it
if this correction pattern appears, patch the parse
```

The new style should be structural:

```text
is this candidate operation safe?
is this predicate allowed?
are the arguments typed and grounded?
is this a claim or an observed fact?
is this a hypothetical query or a write?
does this contradict current KB state?
```

That is a healthier division of labor. The LLM handles interpretation. Python
handles policy, validation, and execution.

In other words, we are not trying to remove the fence. We are trying to stop
building the fence out of one-off English patches.

## What We Learned From the Model Trials

We tested several local model candidates and prompting modes.

The early bakeoff compared a smaller Qwen baseline, a 27B dense Qwen model,
`qwen3.6:35b-a3b`, `gemma4:26b`, and `medgemma:27b` across semantic workspace,
ambiguity critic, and strict compiler styles.

The important takeaways:

- the smaller Qwen baseline remained a strong fast baseline, especially as a strict compiler.
  But it did not feel like the model we wanted for broader semantic
  understanding.
- `qwen3.6:27b` looked strong when allowed to do rich semantic workspace
  analysis, but it was slower.
- `qwen3.6:35b-a3b` became the most promising general sidecar candidate because
  it kept JSON reliability high and ran much faster than the dense 27B in rich
  mode.
- `gemma4:26b` was worth keeping in the candidate pool, especially with
  non-thinking structured outputs, but it was less reliable in rich thinking
  prompts.
- `medgemma:27b` was interesting as a medical ambiguity critic. It handled vague
  pressure, creatinine pronoun ambiguity, and allergy-versus-intolerance well,
  but it is not the obvious general semantic sidecar.

This led us to fix on `qwen3.6:35b-a3b` as the main research model for the
semantic IR lane.

## What We Have Seen So Far

The first useful result was not just "the model can output JSON." It was that
the model could hold distinctions the old pipeline struggled with.

### Wild Pack

A 12-case wild pack tested vague medical language, active-context lab follow-up,
cart correction, mixed rule/query turns, typo-heavy pronoun ambiguity, and
allergy-versus-side-effect.

`best_guarded_v2` with `qwen3.6:35b` scored:

| Pack | JSON OK | Schema OK | Decision OK | Avg rough score |
|---|---:|---:|---:|---:|
| wild pack | 12/12 | 12/12 | 7/12 | 0.88 |

The main weakness was decision-label calibration. The emitted structure was
often useful, but the top-level label sometimes said `mixed` where the external
policy expected `reject`, `quarantine`, `clarify`, or `commit`.

### Glitch Story Pack

The old "Glitch in the Airlock" story had exposed a prior failure mode: story
roles collapsed, and the system could confuse Unit-Alpha with the freelance
salvager.

The semantic IR run did much better:

| Pack | JSON OK | Schema OK | Decision OK | Avg rough score |
|---|---:|---:|---:|---:|
| Glitch story pack | 6/6 | 6/6 | 6/6 | 0.98 |

The model kept Jax, Unit-Alpha, Widget, the Nano-Cell, and the airlock action
separated. It also preserved Widget's claim as a claim instead of converting it
into observed fact.

### Ledger Story Pack

The Ledger pack tested conditional legal and temporal state: separation
agreements, half-share transfers, default certification, guardianship,
residency loss, and charter sequencing.

Result:

| Pack | JSON OK | Schema OK | Decision OK | Avg rough score |
|---|---:|---:|---:|---:|
| Ledger story pack | 8/8 | 8/8 | 8/8 | 0.98 |

The important result was that the model could separate conditional authority
from completed fact. For example, it could represent a separation clause while
not inventing a completed transfer before later evidence appeared.

### Hard Edge Battery

The hard edge battery added nested exceptions, counterfactuals, quantifiers,
identity repair, provenance, temporal intervals, disjunctive causality, medical
negation, double negation, and hypothetical queries.

Prompt-only semantic IR result:

| Pack | JSON OK | Schema OK | Decision OK | Avg rough score |
|---|---:|---:|---:|---:|
| 20 hard edges | 20/20 | 20/20 | 17/20 | 0.96 |

This was the first sign that the semantic layer might be genuinely carrying
more of the work.

### Runtime Guardrail A/B

The important test was not just prompt output. We compared the legacy path
against the semantic IR path inside the runtime.

Legacy path:

```text
old baked parser-lane model + parser + Python rescue chain
```

Semantic IR path:

```text
qwen3.6:35b + semantic_ir_v1 + deterministic mapper
```

Latest full 20-case edge result:

| Path | Decision OK | Avg score | Parse rescues |
|---|---:|---:|---:|
| legacy | 10/20 | 0.777 | 0 counted legacy parse rescues |
| semantic IR | 20/20 | 0.976 | 0 non-mapper rescues |

That is the first concrete evidence that the new path can reduce dependence on
Python-side semantic rescue while improving final-state quality.

Then we built a 10-case weak-edge fix pass around the exact failures:
hypotheticals, quantified class writes, medical allergy retractions, denial
events, and alias-aware retractions.

Latest weak-edge runtime result:

| Path | Decision OK | Avg score | Parse rescues |
|---|---:|---:|---:|
| legacy | 3/10 | 0.633 | 5 |
| semantic IR | 10/10 | 1.000 | 0 non-mapper rescues |

This is the strongest evidence so far that the new direction is productive.

### Silverton Probate Packs

The Silverton packs are deliberately harder than the demo batteries. They test
claim/fact separation, identity ambiguity, London Ontario versus London UK,
medical-sounding witness discrediting, two-witness policy rules, noisy spelling,
code-switching, and temporal corrections.

Current local results:

| Pack | Runs | Semantic decision OK | Semantic avg score | Interpretation |
|---|---:|---:|---:|---|
| Silverton probate | 10 | 2/10 | 0.725 | Hard frontier pack |
| Silverton noisy temporal | 8 | 2/8 | 0.729 | Noise is readable; policy/temporal admission remains weak |

The useful lesson is not that the model fails at messy text. It often preserves
the important semantic content. The remaining difficulty is administrative:
which parts should be answered, clarified, quarantined, rejected, or admitted as
durable temporal facts.

## What Structured Output Adds

We also tested LM Studio's structured output mode. This is not just a prompt. It
lets the inference server enforce a JSON schema through `response_format`.

That matters because it separates two problems:

1. Can the model obey the JSON shape?
2. Can the model make the right semantic judgment?

With LM Studio structured output, the first problem becomes much less noisy.

Clean no-double-prompt run:

- backend: LM Studio
- model: `qwen/qwen3.6-35b-a3b`
- schema only in `response_format`, not repeated in the prompt
- `reasoning_effort: none`

Result:

| Pack | JSON OK | Schema OK | Decision OK | Avg rough score |
|---|---:|---:|---:|---:|
| 56-case full pack | 56/56 | 56/56 | 43/56 | 0.899 |

The takeaway is nuanced. Structured output clearly makes the mechanical side
cleaner: no wrapper keys, no malformed JSON, no missing top-level fields. It
does not automatically solve semantic policy. The remaining errors are about
judgment: whether a turn should be `commit`, `mixed`, `answer`, `clarify`,
`reject`, or `quarantine`.

That is still valuable. If schema obedience becomes boring, we can spend our
research energy on semantics and admission policy.

## What This Direction Is Not

This is not a plan to trust a bigger model blindly.

The model still does not get to commit durable truth. The runtime still owns:

- predicate admission
- schema validation
- KB mutation
- query execution
- contradiction checks
- clarification holds
- rejection of unsafe advice
- provenance and traceability

The new question is not:

```text
Can the model replace the gate?
```

The question is:

```text
Can the model produce a better candidate workspace so the gate needs fewer
English-specific rescue patches?
```

That is the research shape.

## Current Limitations

Several limitations remain clear.

Decision labels still need calibration. The model often produces a useful
structure but chooses a top-level label that does not match the runtime policy.
That is fixable, but it matters.

Rule admission is still shallow. The mapper can preserve direct safe facts and
queries, but durable rules from natural language need a stricter representation
before we should admit them.

Negation still needs a fuller design. We can preserve polarity and commit
denial events as events, but a general durable negative-fact system is not done.

Medical facts remain bounded. UMLS and MedGemma may help with normalization and
semantic typing, but this is not a clinical reasoning system and should not be
presented as one.

The scorer is still rough. Current metrics are useful for comparison, but they
are not an external benchmark. Some "wrong" decision labels still have safe
final KB state, and some keyword-based scores under-credit good behavior.

Structured output helps syntax, not truth. It makes the JSON clean. It does not
decide what is safe to remember.

## Why This Is Worth Continuing

The evidence so far says this is not just a prettier parser. The new path has
already:

- reduced non-mapper parse rescues to zero on tested runtime batteries
- avoided several legacy bad commits
- handled old story-role failures more cleanly
- represented conditional legal state without collapsing it into completed fact
- improved weak-edge runtime score from roughly 0.650 legacy to 1.000 semantic IR
- reached 20/20 on the edge runtime pack and 10/10 on the weak-edge runtime pack
- made schema obedience reliable through LM Studio structured output

The big picture is still ambitious, but the direction feels more principled:

```text
LLM as semantic workspace builder
Python as deterministic admission controller
Prolog-like KB as durable proof surface
```

That is a better research story than "English to Prolog plus patches."

It is also a better engineering story. We can measure whether a new scenario
requires another English-specific Python rescue. If it does, that is a signal.
If the semantic IR already expresses the meaning and the mapper only has to
validate it, that is progress.

## Near-Term Research Plan

The next useful work is not to add a lot of features. It is to keep pressure on
the architecture.

1. Add LM Studio structured-output runtime integration behind a flag.
2. Keep Ollama and LM Studio bakeoffs comparable.
3. Split scores into mechanical validity, semantic decision, safe operation
   quality, and final KB state.
4. Build harder scenario packs that are less tailored to current rescue code.
5. Measure Python rescue dependency directly, not anecdotally.
6. Tighten the semantic IR schema around rules, negation, claims, and temporal
   scope.
7. Treat the old clarification sidecar as historical scaffolding, not the main
   semantic compiler.

## Slide Outline

1. The original thesis
   - LLM proposes; deterministic runtime decides; KB remembers.

2. The problem we hit
   - Too much semantic rescue was accumulating in Python.
   - The system risked becoming test-specific.

3. Why the retired sidecar was not enough
   - Good clarification sidecar.
   - Not a replacement for richer semantic understanding.

4. The new architecture
   - Utterance to semantic workspace.
   - Semantic workspace to deterministic mapper.
   - Mapper to KB mutation/query/clarification/rejection.

5. Why a stronger model changes the design
   - More holistic language understanding.
   - Better claim/fact/condition/temporal separation.
   - Less pressure for English-specific Python patches.

6. Model exploration
   - 9B remains fast baseline.
   - 27B is strong but slow.
   - 35B-A3B is the best general sidecar candidate so far.
   - MedGemma is interesting for medical ambiguity, not general authority.

7. Evidence so far
   - Glitch pack: 6/6 decisions, old role-collapse failure avoided.
   - Ledger pack: 8/8 decisions, conditional state preserved.
   - Runtime A/B: semantic IR improves score and removes non-mapper rescues.

8. Structured output
   - LM Studio schema enforcement gives 56/56 JSON and schema.
   - Helps mechanics, not semantic judgment.

9. Remaining limitations
   - Decision labels, rule admission, negation, temporal scope, medical bounds,
     scoring quality.

10. The research bet
   - Move from English rescue patches to structural admission gates.
   - Keep the authority boundary.
   - Let the LLM do more semantic work, but never own durable truth.

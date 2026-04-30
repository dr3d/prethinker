Yes - this is exactly the kind of test Prethinker should be aimed at, but I would **not** ask Prethinker to "generate the complete Prolog KB" in one shot.

That is the trap.

The best game-plan is to treat this as a **multi-pass fact-intake and symbolic compilation benchmark**, where Prethinker proposes structure, deterministic gates validate it, and Prolog proves what can actually be proved.

Your current repo is already pointed in this direction: the project describes its spine as language -> pre-thinker proposal -> deterministic policy gates -> symbolic KB -> auditable derivations, with the symbolic core as deterministic truth and the pre-thinker emerging as classifier/router/uncertainty layer. ([GitHub][1]) The repo status also says the deterministic logic layer is solid, but predicate mapping and canonical fact shaping are still early, and durable journaled memory is not complete yet. ([GitHub][2])

So the right test is not:

> "Can Qwen generate my whole KB"

It is:

> "Can Prethinker progressively turn a dense story into safe candidate symbolic structure, while refusing to overcommit when uncertain"

That is very different - and much more valuable.

---

# My recommended game-plan

## Phase 0: Freeze the target ontology before ingestion

For this story test, do **not** let the model invent arbitrary predicates freely. Give it a controlled narrative ontology registry.

Something like:

```prolog
entity/1
character/1
object/1
place/1
food/1
kind/2
name/2
size/2
trait/2
owned_by/2
designed_for/2
located_in/2
part_of/2
event/5
story_time/2
said/3
judged/4
causes/2
caused_by/2
violated_norm/3
entered_without_permission/3
ate_without_permission/3
used_without_permission/3
final_state/1
condition_after_story/2
```

For each predicate, provide:

```json
{
  "predicate": "owned_by",
  "arity": 2,
  "argument_roles": ["object", "owner"],
  "allowed_arg_types": ["object|food|place", "character|household"],
  "example": "owned_by(little_boat, little_slip_otter).",
  "anti_example": "owned_by(little_slip_otter, little_boat)."
}
```

This is critical because your own fact-intake spec already says predicate mapping should target a **controlled predicate vocabulary** with ranked candidates and abstention on low confidence. ([GitHub][3])

For this test, the registry is the difference between useful symbolic extraction and creative Prolog soup.

---

## Phase 1: Run Prethinker as a classifier/router first, not a compiler

Before asking for facts, ask Prethinker to classify the passage into extraction lanes.

The story has several lanes:

```text
entity_introduction
object_inventory
location_structure
ownership_structure
event_sequence
direct_speech
judgment_comparison
causal_consequence
norm_violation
evidence_and_inference
final_state
moral_abstraction
```

This fits your control-plane concept: the pre-thinker should classify statements, route them into ontology context, detect uncertainty, and decide when escalation is needed; it is not supposed to prove facts or override the symbolic engine. ([GitHub][4])

So for each paragraph, Prethinker should emit something like:

```json
{
  "segment_id": "p07",
  "dominant_lanes": [
    "event_sequence",
    "judgment_comparison",
    "causal_consequence"
  ],
  "entities_mentioned": [
    "tilly_tumbletop",
    "great_boat",
    "middle_boat",
    "little_boat",
    "rain_barrel"
  ],
  "requires_temporal_ordering": true,
  "requires_causality": true,
  "escalation_required": false,
  "confidence": 0.88
}
```

This is a much easier task than generating final Prolog. It also gives you a diagnostic: if routing fails, everything downstream is poisoned.

---

## Phase 2: Extract candidate records, not Prolog facts yet

Your fact-intake spec already points at candidate records with fields like statement type, predicate candidate, ranked candidates, arguments, unresolved references, negation, confidence, and recommended action. ([GitHub][3]) That is exactly what you want here.

For example, from:

> The Little Slip of an Otter had a little boat.

Prethinker should not directly write:

```prolog
owned_by(little_boat, little_slip_otter).
```

It should emit:

```json
{
  "source_span": "the Little Slip of an Otter ... a little boat",
  "statement_type": "hard_fact",
  "symbolically_suitable": true,
  "predicate_candidate": "owned_by",
  "predicate_candidates_ranked": ["owned_by", "designed_for"],
  "arguments": ["little_boat", "little_slip_otter"],
  "confidence": 0.96,
  "recommended_action": "stage_for_validation"
}
```

Then a second candidate:

```json
{
  "predicate_candidate": "size",
  "arguments": ["little_boat", "little"],
  "confidence": 0.98
}
```

Then maybe:

```json
{
  "predicate_candidate": "kind",
  "arguments": ["little_boat", "boat"],
  "confidence": 0.99
}
```

This is where Prethinker can shine: **candidate shaping**, not final authority.

---

## Phase 3: Build an entity table before compiling events

I would make entity extraction its own mandatory pass.

Output should look like:

```json
{
  "entities": [
    {
      "atom": "tilly_tumbletop",
      "surface_forms": ["Tilly Tumbletop", "Tilly", "she"],
      "kind": "human_child",
      "role": "intruder_or_visitor",
      "confidence": 0.99
    },
    {
      "atom": "little_slip_otter",
      "surface_forms": ["Little Slip of an Otter", "Little Slip", "he", "his"],
      "kind": "otter",
      "role": "household_member",
      "confidence": 0.98
    }
  ]
}
```

Do this before events because the hard parts of this story are often pronoun/reference problems:

```text
his half-birthday wheels
she ate it
they wound her
somebody had sunk my boat
```

If entity grounding is weak, the KB will be trash. Your benchmark spec already identifies unresolved reference handling and speaker resolution as key dimensions. ([GitHub][5]) This story is a much richer version of that problem.

---

## Phase 4: Compile a chronological event ledger

The event ledger is probably the most important artifact.

Do not start with Prolog. Start with normalized event records:

```json
{
  "event_id": "e035",
  "actor": "tilly_tumbletop",
  "action": "eat_all",
  "object": "little_pie_slice",
  "location": "kitchen",
  "time_index": 35,
  "source_span": "So she ate it all up, crust, crumbs, wheels, and every bit.",
  "confidence": 0.97
}
```

Then compile mechanically to:

```prolog
event(e035, tilly_tumbletop, eat_all, little_pie_slice, kitchen).
story_time(e035, 35).
```

The compiler should be deterministic. The model should not decide syntax at this stage.

This is where your current architecture is very well-aligned: the repo already has a structured IR/compiler area and deterministic logic layer. ([GitHub][1])

---

## Phase 5: Extract state changes separately from events

This is where most LLMs will fail.

The text says:

> She ate the little slice.

But the KB needs:

```prolog
event(e035, tilly_tumbletop, eat_all, little_pie_slice, kitchen).
causes(e035, eaten(little_pie_slice)).
causes(e035, swallowed(tilly_tumbletop, brass_wheel_1)).
...
```

That second layer is **causal expansion**.

Prethinker should emit a candidate like:

```json
{
  "event_id": "e035",
  "causal_effects": [
    "eaten(little_pie_slice)",
    "swallowed(tilly_tumbletop, brass_wheels)"
  ],
  "needs_expansion": true,
  "expansion_basis": "little_pie_slice contains six brass wheels",
  "confidence": 0.84
}
```

Then the deterministic expander can expand `brass_wheels` into six known wheel entities.

This tests the real heart of the system: not just extraction, but **safe enrichment**.

---

## Phase 6: Separate narrator truth from character speech

This is another must-have.

The story contains:

```text
"That was not my fault," said Tilly, though it mostly was.
```

A naive system may assert:

```prolog
not_responsible_for(tilly_tumbletop, jar_incident).
```

That would be wrong.

The correct structure is:

```prolog
said(e055, tilly_tumbletop, "That was not my fault.").
mostly_responsible_for(tilly_tumbletop, jar_incident).
```

So Prethinker needs a source-status field:

```json
{
  "claim": "not_my_fault",
  "speaker": "tilly_tumbletop",
  "source_status": "character_speech",
  "narrator_confirms": false,
  "narrator_contradicts": true,
  "safe_to_assert_as_world_fact": false
}
```

This should become a benchmark category of its own:

```text
speech_vs_truth
```

Because story ingestion will fail badly unless this is handled.

---

## Phase 7: Handle "just right" as judgment, not objective truth

The little boat is the perfect trap.

Tilly judges it "just right," but it later sinks. So this is valid:

```prolog
judged(tilly_tumbletop, little_boat, rowing_fit, just_right).
```

But this is not valid:

```prolog
safe_for(tilly_tumbletop, little_boat).
```

The GIC needs to distinguish:

```text
subjective evaluation
objective property
later consequence
```

So a good candidate record would be:

```json
{
  "predicate_candidate": "judged",
  "arguments": [
    "tilly_tumbletop",
    "little_boat",
    "rowing_fit",
    "just_right"
  ],
  "world_fact": false,
  "subjective_fact": true,
  "confidence": 0.95
}
```

That one field - `subjective_fact` - would save you from a huge class of bad assertions.

---

## Phase 8: Run three versions of the test

I would not run only one test. I would run three increasingly hard lanes.

### Test A: Reasoning-only

Load the human-authored gold KB. Ask the 100 questions.

Goal:

```text
Can the Prolog layer answer correctly if the KB is already right
```

This isolates the deterministic engine.

Expected result: should be high. If this fails, the problem is not ingestion.

---

### Test B: Extraction-only

Give Prethinker the story and ontology registry. Ask it to emit candidate records only.

No Prolog writes.

Score:

```text
entity recall
predicate candidate accuracy
argument order accuracy
confidence calibration
unsafe assertion avoidance
source-span grounding
```

This tests the actual pre-thinker.

---

### Test C: Full ingestion-to-query

Story -> candidate records -> validation -> Prolog compile -> KB load -> 100 questions.

This is the real GIC test.

Score it end-to-end, but also keep per-stage scoring so you know where failure occurred.

---

# What Prethinker probably can do now

Based on the repo status, I would expect your current design to do well at:

```text
statement classification
query-vs-fact routing
simple hard facts
simple entity/kind extraction
simple predicate candidates
basic Prolog execution
basic validation
MCP-style interaction
```

That aligns with the repo's implemented pieces: deterministic Prolog engine, constraint propagation, structured IR/schema validation, semantic grounding, deterministic statement classification, failure translation, MCP integration, and the current 115-test baseline. ([GitHub][1])

For this story, current Prethinker should be able to extract things like:

```prolog
character(tilly_tumbletop).
kind(clockwork_pie, pie).
owned_by(little_boat, little_slip_otter).
event(e035, tilly_tumbletop, eat_all, little_pie_slice, kitchen).
```

It should also classify many of the 100 questions into query form if the KB is already loaded.

That alone is useful.

---

# What Prethinker probably cannot do yet

I would not expect the current system to fully reproduce the KB I generated without help.

The hard parts are:

```text
inventing a clean narrative ontology
maintaining event chronology across a long passage
creating stable event ids
distinguishing speech from narrator truth
extracting implied causality
updating final state versus prior state
expanding grouped entities, like six brass wheels
distinguishing subjective judgment from objective property
creating useful inference rules
creating query helper predicates
```

The repo itself says the current runtime is conservative, the pre-thinker LoRA and full write journaling are design/research tracks rather than default runtime behavior, and runtime mutation is process-local rather than durable journaled memory. ([GitHub][1]) The fact-intake spec also explicitly frames free-form natural-language writes straight into hard facts and automatic ontology creation as out of scope for the first increment. ([GitHub][3])

That means the current system should **not** be judged by whether it can create my full KB in one shot.

It should be judged by whether it can produce safe, staged, inspectable candidates that move toward that KB without polluting the hard-fact store.

---

# The concrete benchmark architecture I would build

Use this folder structure:

```text
data/story_tests/otters_clockwork_pie/
  story.md
  ontology_registry.json
  gold_entities.json
  gold_event_ledger.json
  gold_candidates.json
  gold_kb.pl
  questions_100.jsonl
  expected_answers.jsonl
  scoring_rules.json
```

Each question row should include:

```json
{
  "id": 58,
  "question": "Why was the little boat unsuitable for Tilly",
  "expected_query": "why_did_boat_sink(little_boat, Reason).",
  "expected_answer": "Tilly was heavier than an otter and heavier after eating the clockwork pie.",
  "required_facts": [
    "event(e070, tilly_tumbletop, be_heavier_than, otter, little_boat)",
    "event(e071, tilly_tumbletop, be_heavier_after_eating, little_pie_slice, little_boat)"
  ],
  "failure_traps": [
    "answers only 'too heavy'",
    "misses clockwork pie causal detail",
    "treats subjective just-right as objective safety"
  ],
  "category": [
    "causality",
    "subjective_vs_objective",
    "temporal_reasoning"
  ]
}
```

Then score with multiple metrics:

```text
entity_exact_match
predicate_exact_match
argument_order_match
event_order_accuracy
causal_link_accuracy
norm_violation_accuracy
speech_attribution_accuracy
final_state_accuracy
query_answer_accuracy
unsafe_assertion_rate
abstention_quality
```

Your existing benchmark spec already uses model/scenario rows, scored output records, derived metrics, and failure buckets like predicate miss, argument parse error, resolution safety, overcommit, undercommit, and unexpected write. ([GitHub][5]) I would extend that spec, not replace it.

---

# Add these new failure buckets for this story test

Your current failure buckets are good for atomic fact ingestion. For narrative ingestion, add these:

```text
F9_template_contamination
Imported Goldilocks facts: bears, porridge, chairs, beds, sleeping.

F10_event_order_loss
Correct facts but wrong chronology.

F11_speech_truth_confusion
Character speech asserted as narrator/world truth.

F12_subjective_objective_confusion
"Just right" treated as objective safety or correctness.

F13_causal_gap
Event extracted but consequence omitted.

F14_final_state_staleness
Earlier state remains treated as true after repair/remedy.

F15_group_expansion_failure
"Six brass wheels" not expanded or counted correctly.

F16_ownership_transfer_error
Tilly uses/swallow/holds something, and system mistakes that for ownership.

F17_whimsy_erasure
Magical literal details treated as metaphor or ignored.
```

That last one is surprisingly important. LLMs often "normalize away" whimsical facts. In this story, whimsy is logic.

---

# The prompt I would give Prethinker

Something like this:

```text
You are Prethinker-GIC, a stateless symbolic intake assistant.

Your job is not to answer the story and not to write final Prolog directly.
Your job is to emit candidate symbolic records for deterministic validation.

Use only the provided ontology registry.
If no predicate fits, emit unknown_predicate and recommend abstain_or_escalate.
Do not invent facts from familiar fairy tales.
Do not import Goldilocks, bears, porridge, chairs, beds, sleeping, or running away unless present in the current story.
Distinguish narrator facts from character speech.
Distinguish subjective judgments from objective states.
Distinguish events from resulting states.
Distinguish temporary states from final states.
Every candidate must include source_span, confidence, and recommended_action.

Output JSON only.
```

Then give it a paragraph at a time, not the whole story at once.

---

# The best practical ingestion pipeline

I'd run it like this:

```text
1. Segment story into paragraphs.
2. Prethinker labels extraction lanes per paragraph.
3. Entity pass over entire story.
4. Deterministic entity canonicalizer freezes atom names.
5. Object/ownership/location pass.
6. Event ledger pass.
7. Speech pass.
8. Judgment/comparison pass.
9. Causality/state-change pass.
10. Norm/permission pass.
11. Final-state pass.
12. Compile candidates to Prolog.
13. Load KB.
14. Run syntax validation.
15. Run referential integrity check.
16. Run 100-question benchmark.
17. Produce failure report by bucket.
```

The key is that **each pass constrains the next**.

Once the entity table is frozen, later passes must use those atoms. Once event IDs are frozen, causality must attach to those event IDs. Once ownership is frozen, norm violations can be inferred.

That is how you avoid hallucinated symbolic mush.

---

# The "win condition" for this test

Do not set the first win condition as:

```text
Prethinker generates 100% of the gold KB.
```

That is too harsh and not aligned with the current design.

Set the first win condition as:

```text
Prethinker extracts 90%+ of core entities,
80%+ of explicit ownership/location facts,
75%+ of event ledger facts,
and produces fewer than 3 unsafe hard assertions.
```

Then the second win condition:

```text
With human-approved candidate promotion, the generated KB answers 70%+ of the 100 questions.
```

Then the third:

```text
After adding targeted rules for causality, final state, and subjective judgment, the KB answers 90%+.
```

That gives you a realistic progression.

---

# My blunt assessment

Prethinker can absolutely use this test.

But today, the test should be framed as a **fact-intake stress harness**, not as a demand for autonomous full KB synthesis.

The current design is strongest when Prethinker acts as:

```text
classifier
router
candidate shaper
ambiguity detector
confidence estimator
safe abstainer
```

It is not yet strongest as:

```text
ontology inventor
complete Prolog author
narrative rule synthesizer
truth-maintenance system
durable memory curator
```

And that is okay. In fact, this story test gives you a perfect roadmap: every place it fails tells you which ingestion layer to build next.

The most important principle is this:

> Do not ask the model to be the KB. Ask it to propose evidence-backed symbolic candidates that earn their way into the KB.

That is the Prethinker idea at its best.

[1]: https://github.com/dr3d/prolog-reasoning "GitHub - dr3d/prolog-reasoning: Neuro-Symbolic memory for LLM agents: deterministic fact storage and inference without hallucination. - GitHub"
[2]: https://github.com/dr3d/prolog-reasoning-v2/blob/main/status.md "prolog-reasoning/status.md at main - dr3d/prolog-reasoning - GitHub"
[3]: https://github.com/dr3d/prolog-reasoning/blob/main/docs/fact-intake-pipeline.md "prolog-reasoning/docs/fact-intake-pipeline.md at main - dr3d/prolog-reasoning - GitHub"
[4]: https://github.com/dr3d/prolog-reasoning/blob/main/docs/pre-thinker-control-plane.md "prolog-reasoning/docs/pre-thinker-control-plane.md at main - dr3d/prolog-reasoning - GitHub"
[5]: https://github.com/dr3d/prolog-reasoning/blob/main/docs/research/fact-ingestion-benchmark-matrix-spec.md "prolog-reasoning/docs/research/fact-ingestion-benchmark-matrix-spec.md at main - dr3d/prolog-reasoning - GitHub"

# Clarification Eagerness Strategy

Last updated: 2026-05-03

## Why This Matters

Clarification eagerness, or CE, is not a UI afterthought. It is part of
knowledge acquisition.

Prethinker should ask when an ambiguity would otherwise cause a bad durable
write, a bad rule, a collapsed identity, or a misleading query answer. It should
not ask when the mapper can safely admit partials, quarantine a claim, or skip
an unsafe candidate without losing important work.

The danger is adding CE too late. If the compiler has already flattened a
source into wrong atoms, wrong predicate roles, or wrong rule scope, a later
clarification prompt may only repair the answer surface. The best time to ask
is often during ingestion, while entities, events, time anchors, rule variables,
and support links are still fresh in the semantic workspace.

## Current Status

The runtime already has CE mechanics:

- `_clarification_policy_decision(...)` decides whether uncertainty crosses the
  ask threshold.
- `_compute_effective_clarification_eagerness(...)` supports static and
  adaptive CE.
- The adaptive mode can start higher during ontology bootstrapping and decay as
  turns or admitted KB clauses accumulate.
- The UI/runtime can hold a pending turn, ask a clarification, then resume the
  original turn with the answer in context.

What is missing is frontier-level measurement. Recent fixture journals track
compile, query, and answer quality, but they do not yet treat CE as a first-class
score dimension.

That gap is now closing. The CE Trap structured-output runs now show the arc:

```text
first full baseline: 30/40 correct
best pre-context-write-scoring posture: 38/40 correct, 0 over-eager
first strict authority-aware baseline: 37/40 correct, 0 over-eager,
  2 under-eager, 1 unsafe candidate, 2 context-write violations
CET-010 current high-water: 40/40 correct, 0 over-eager,
  0 under-eager, 0 unsafe candidates, 0 context-write violations,
  10/10 blocked-slot question coverage, 0 blocked-slot safe-write violations
```

The most important lesson is that CE is not a single dial. Ask/no-ask posture,
safe partial preservation, blocked-slot question coverage, blocked-slot write
hygiene, and context-write hygiene can move independently.

## Two Clarification Surfaces

### 1. Ingestion Clarification

Ingestion clarification happens before durable admission, while the source is
being compiled.

It should trigger when ambiguity blocks safe symbolic state:

- an entity could be two people, vessels, projects, committees, or documents;
- a pronoun or title cannot be resolved safely;
- a date, interval, or deadline anchor is underspecified;
- a correction does not identify the old fact it replaces;
- a rule condition, exception, or priority relation is unclear;
- a claim could be mistaken for a finding or fact;
- a source document uses local aliases that are not yet grounded;
- a multi-pass lens needs a missing backbone anchor before it can add support,
  temporal, or rule rows.

The target behavior is:

```text
commit clear partials;
hold only blocked rows;
ask one compact question for the blocked rows;
resume the same semantic pass or the dependent lens after the answer.
```

### 2. Query Clarification

Query clarification happens after a KB surface exists.

It should trigger when the question is not answerable without guessing:

- "Which one violated the rule?" when multiple rule families are active;
- "Did she approve it?" with ambiguous actor or object;
- "Was it late?" without knowing which deadline definition applies;
- "Who was responsible?" when the KB has findings, claims, and allegations with
  different epistemic status;
- "What changed?" when the user has not named the stage, time window, or
  correction target.

The target behavior is:

```text
answer from admitted KB when possible;
ask if the query variable or intended scope is ambiguous;
do not turn a clarification question into a write;
log the clarification as query-surface behavior, not compile failure.
```

## CE Metrics To Log

Every frontier fixture run that exercises ambiguity should record:

```text
base_ce
effective_ce
ce_mode
ce_phase
clarification_requested_count
clarification_correct_count
clarification_overeager_count
clarification_undereager_count
safe_partial_commit_count
blocked_row_count
context_write_violation_count
resumed_turn_success_count
query_clarification_count
```

Useful derived metrics:

```text
clarification_precision = correct / requested
clarification_recall = correct / should_have_asked
overeager_rate = overeager / requested
undereager_rate = missed_needed_clarifications / ambiguity_cases
safe_partial_rate = safe_partials_committed / clear_rows_available
resume_success_rate = resumed_turn_success / clarification_answers
```

## Fixture Strategy

We do not need to regenerate the existing fixtures wholesale.

Instead, add CE overlays beside them:

```text
datasets/story_worlds/<fixture>/ce_variants/
  ingestion_ambiguities.jsonl
  query_ambiguities.jsonl
  answer_keys.jsonl
  progress_journal.md
```

Each row should define the ambiguity and expected behavior:

```json
{
  "id": "glt-ce-001",
  "surface": "ingestion",
  "source_variant": "The harbor clerk said she approved the west sluice permit.",
  "expected_behavior": "clarify",
  "blocked_slots": ["actor"],
  "acceptable_questions": [
    "Who does 'she' refer to?"
  ],
  "safe_partials_expected": true,
  "must_not_commit": [
    "approved(_, west_sluice_permit)"
  ]
}
```

For query ambiguity:

```json
{
  "id": "btc-ce-014",
  "surface": "query",
  "question": "Was the appeal late?",
  "expected_behavior": "clarify",
  "clarification_target": "which appeal deadline or proceeding stage",
  "must_not_answer_as_fact": true
}
```

The overlays can reuse existing story/gold/QA fixtures while adding a new
behavior axis.

## How To Create Ambiguity Without Python NLP

Python must not mangle prose to derive ambiguity cases.

Acceptable methods:

- Codex or another LLM authors CE variants as source text changes and records
  the expected clarification behavior.
- A human edits fixture variants directly.
- A fixture package includes hand-authored ambiguous query rows.
- A model-owned pass proposes possible ambiguous variants, but those variants
  are reviewed before becoming benchmark rows.

Unacceptable methods:

- Python rewrites raw source text by detecting names, pronouns, dates, or
  predicates.
- Python derives expected clarification targets from the gold KB.
- Python generates answerable facts or query answers from raw prose.

Python may still validate JSON shape, run the harness, compare recorded
expected outcomes, and log metrics.

## Current Fixture

The first dedicated CE fixture is checked in at
`datasets/clarification_eagerness/clarification_eagerness_trap/`.

It contains:

- a compact charter/procedure/case-file source;
- 20 hand-authored ingestion CE cases;
- 20 hand-authored query CE cases;
- 10 baseline QA probes;
- machine-readable JSONL views of the authored case tables;
- expected aggregate ask/no-ask behavior.

This fixture should become the first place where CE is measured as its own
frontier metric instead of being inferred from ordinary QA results.

## Fixture Families To Add

### Glass Tide CE

Focus:

- rule variable ambiguity;
- exception scope;
- priority/override ambiguity;
- actor/title ambiguity;
- claim versus finding ambiguity.

This should exercise ingestion CE before executable rules are admitted.

### Blackthorn CE

Focus:

- stage-specific findings;
- title/person identity;
- deadline scope;
- appeal stage;
- witness claim versus committee finding.

This should exercise both ingestion and query CE.

### Kestrel CE

Focus:

- dual-role insurer identity;
- security versus payment;
- cited authority versus holding;
- notice deadline anchor;
- disputed survey account.

This should test whether clarification prevents role collapse.

### Otters CE

Focus:

- story-local pronouns;
- same-size object references;
- speech versus narrator truth;
- final-state ambiguity;
- "the boat" or "the mug" questions with multiple candidates.

This keeps CE grounded in narrative-world ingestion rather than only legal or
policy domains.

## Multi-Pass Interaction

CE should be lens-aware.

Backbone lens:

- ask about blocked core identity or source boundary;
- avoid asking about every support detail.

Support/source lens:

- ask only when support cannot attach to an admitted backbone row.

Temporal/status lens:

- ask when a time anchor or correction target is missing.

Rule lens:

- ask when a rule condition, exception, priority, or variable binding is
  ambiguous enough that admitting the rule would be dangerous.

Query lens:

- ask when a user question cannot be grounded against the admitted KB surface
  without choosing a scope for the user.

## Near-Term Implementation Plan

1. Keep hardening the dedicated CE Trap fixture until the remaining misses are
   assigned to clear structural fixes: unsupported correction/retraction,
   context-sourced candidate writes, and ask/no-ask posture.
2. Add CE overlay files for Glass Tide next, because rule ingestion is the
   current frontier and bad rules amplify.
3. Keep `scripts/run_clarification_eagerness_fixture.py` as a structural
   scorer: it reads authored expected behavior rows and runtime Semantic IR
   outcomes. It must only compare structured outcomes; it must not read prose
   for meaning.
4. Extend fixture progress journals with a CE section:

```text
CE surface:
  ingestion: X correct / Y, overeager Z, undereager W
  query: X correct / Y, overeager Z, undereager W
  safe partials: N
  resumed turns: N successful / M attempted
```

5. Add CE examples to the console trybook so manual sessions can see the same
   behavior.
6. Cross-apply the overlay pattern to Blackthorn, Kestrel, and Otters.

## Design Principle

Clarification is not failure.

In a governed knowledge system, a good clarification is an admission-control
success: the system noticed that durable truth would require a choice it was not
authorized to make.

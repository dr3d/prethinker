# Stenographer Mode Simulation

Last updated: 2026-05-03

Stenographer mode is the turn-by-turn counterpart to document ingestion.
Document ingestion receives a large source and may segment it internally.
Stenographer mode receives only the current utterance plus previously admitted
state, pending clarification state, and recent conversation context.

The research question is:

```text
Can Prethinker safely build a durable symbolic record when the document arrives
as a stream of partial, sometimes ambiguous turns?
```

## Boundary

Segmentation is still allowed, but only inside the utterance that has actually
arrived.

Allowed:

- split the current incoming utterance at query boundaries;
- split the current long pasted sentence/paragraph if it exceeds the UI
  segmentation rules;
- use prior admitted KB clauses and explicitly recorded pending clarification
  state as context.

Forbidden in this lane:

- rebuild the whole fixture as a monolithic document;
- look ahead to future turns;
- use answer keys, gold KBs, or source strategy notes in compile context;
- use Python to interpret sentence meaning or extract facts.

## State Machine

```text
turn_i
  -> route current utterance
  -> build context from admitted KB + pending ledger + recent turns
  -> semantic workspace proposal
  -> deterministic admission
  -> one of:
       commit safe partials
       answer query
       hold blocked candidates
       ask clarification
       quarantine/reject
  -> turn_i+1 sees only the resulting state
```

If a clarification is pending, the next turn is treated as the clarification
answer in the current UI path. A stenographer fixture must therefore label
whether each turn is a normal utterance, a clarification answer, a cancellation,
or an intentionally unresolved continuation.

## Clarification Queue

Clarification Eagerness decides whether a blocked slot deserves a question.
That is not the same thing as deciding whether the system should interrupt the
user immediately.

Stenographer mode needs a second policy surface:

```text
clarification delivery policy =
  immediate ask
  queued ask
  ask only before query
  ask only before risky mutation
  batch questions at checkpoint
  let later turns self-resolve
```

This is the annoyance/interruption dial. A live stenographer may need to keep
listening while ambiguous items accumulate in a pending ledger. Safe partials
can still commit, but blocked candidates should remain outside durable truth
until a later answer, restatement, source document, or checkpoint resolves them.

The pending ledger should eventually carry structured rows like:

```json
{
  "slot_id": "pending_approval_actor_03",
  "opened_turn_id": "t014",
  "blocked_operation_ref": "op_2",
  "question": "Which approval authority did 'it was approved' refer to?",
  "delivery": "queued",
  "blocking_scope": "mutation",
  "safe_partials_committed": ["filed_notice(...)."],
  "status": "open"
}
```

This creates two independent scores:

- did Prethinker correctly identify the blocked slot?
- did the runtime choose an appropriate interruption policy?

The current gateway has a single pending clarification slot and treats the next
non-command turn as the answer. That is useful for the manual UI, but it is not
yet the full queued-stenographer behavior.

## What To Measure

Stenographer runs should report:

- `pending_before_count`
- `pending_after_count`
- `clarification_answer_turns`
- `delayed_commit_after_clarification`
- `commit_applied`
- `commit_blocked`
- `held_segment_turns`
- `held_segments_total`
- `expectation_pass`
- `expectation_fail`

Fixture-authored JSONL rows may include structured expectations such as:

```json
{
  "id": "s007",
  "kind": "clarification_answer",
  "utterance": "I mean the finance chair's approval, not the witness note.",
  "expected_pending_before": true,
  "expected_pending_after": false,
  "expected_clarify_status": "resolved",
  "expected_commit_status": "applied",
  "expected_min_writes": 1
}
```

The runner only compares these declared expectations with structured gateway
output. It does not parse the utterance language.

## Why This Is Hard

Document ingestion can plan a broad symbolic surface. Stenographer mode must
operate under partial observability:

- a sentence may be too ambiguous to commit now but useful after turn `n+2`;
- safe partials should still commit even when one slot is blocked;
- a query may arrive before all relevant source facts are known;
- identity and role atoms must remain stable across turns;
- clarification eagerness can become either too timid or too aggressive;
- a later correction may need to target a fact admitted several turns earlier.

This lane is expected to be harder than monolithic document ingestion. It is
also closer to the live UI use case.

## Current Harness

`scripts/run_gateway_turnset.py` is the first stenographer-mode recorder. It
drives `/api/prethink` one turn at a time through the product gateway and now
records pending-state, delayed-commit, segmentation-hold, and expectation
metrics.

Example:

```powershell
python scripts/run_gateway_turnset.py `
  --turns datasets/stenographer_mode/example/turns.jsonl `
  --turns-format jsonl `
  --strict-lock `
  --reset-session `
  --label stenographer_example
```

Future work:

- add a first cold fixture designed specifically for clarification-in-the-middle;
- distinguish "next turn is a clarification answer" from "next turn is a new
  utterance while clarification remains pending";
- add a queued clarification ledger with an interruption/annoyance dial;
- add pending-slot closure scoring against authored blocked-slot ids;
- compare sentence-at-a-time stenographer runs against monolithic document runs
  without mixing evidence lanes.

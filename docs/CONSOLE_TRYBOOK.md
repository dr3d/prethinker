# Prethinker Console Trybook

This is a practical set of manual tests for the local Prethinker Console UI at [http://127.0.0.1:8765](http://127.0.0.1:8765).

Use it when you want to compare the current front door to direct GIC interaction and see where the console is being helpful, strict, or awkward.

## Ground Rules

- Start the console from [ui_gateway/main.py](../ui_gateway/main.py).
- Keep `Apply Strict Bouncer Lock` enabled unless you are intentionally testing looser behavior.
- Use `Reset Session` before each scenario block unless the script says to keep the same session.
- After interesting turns, use `/state` and `/kb 50`.
- Export the session when a run is especially good or especially bad.

## What To Watch

The UI panel now called `Decision Ledger` is the main thing to study.

For each turn, look at:

- `route`: did it classify as `write`, `query`, `command`, or `other`?
- `Ambiguity`: did the system correctly judge uncertainty?
- `Clarification`: did it ask when it should, and avoid asking when it should not?
- `commit`: did it actually apply a deterministic change or correctly block it?
- operation lines: what fact or rule was really written?

## Helpful Hint

If you want a sentence to be treated as a clear write, prefacing it with `Remember that ...` is still useful in this MVP.

Examples:

- clearer write: `Remember that the museum opens at dawn.`
- clearer query: `Does the museum open at dawn?`
- ambiguity probe: `The museum opens at dawn.`

## Scenario 1: Clean Write Baseline

Fresh session.

1. `Remember that the launch plan ships next week.`
2. `Remember that the museum opens at dawn.`
3. `Remember that Selene chairs the archive board.`
4. `/kb 20`

What to look for:

- all three should route to `write`
- no clarification should be needed
- the commit phase should show one applied mutation per turn

## Scenario 2: Clarification Hold

Fresh session.

1. `Remember that it ships next week.`
2. `Remember that it opens at dawn.`
3. `Remember that she signed it after the hearing.`

What to look for:

- the console should block instead of guessing
- the answer text should be a real clarification question
- the commit phase should show `blocked`

## Scenario 3: Clarification Resolution

Same session for each pair.

1. `Remember that it ships next week.`
2. `The launch plan.`
3. `Remember that it opens at dawn.`
4. `The museum.`
5. `Remember that she signed it after the hearing.`
6. `Selene signed the lease.`

What to look for:

- the follow-up should resolve the pending clarification
- the original write should then commit
- `/state` should show pending clarification disappearing after resolution

## Scenario 4: Query After Write

Same session.

1. `Remember that the launch plan ships next week.`
2. `Does the launch plan ship next week?`
3. `When does the launch plan ship?`
4. `Is the launch plan delayed?`
5. `What do you know about the launch plan?`

What to look for:

- the first turn should commit
- the next turns should route as queries or `other`, not fresh writes
- answers should stay grounded in the KB rather than improvising

## Scenario 5: Correction Pressure

Same session.

1. `Remember that the museum opens at dawn.`
2. `Actually, the museum opens at noon.`
3. `When does the museum open?`
4. `Remember that Unit Alpha returned from the spacewalk.`
5. `Actually, Unit Alpha has not returned yet.`
6. `Did Unit Alpha return from the spacewalk?`

What to look for:

- whether correction language is handled sensibly
- whether the ledger makes the mutation story easy to understand
- whether the follow-up query reflects the revised state

## Scenario 6: Temporal Feel

Same session.

1. `Remember that Jax was in the galley at step 6.`
2. `Remember that Jax was in the mudroom at step 11.`
3. `Where was Jax at step 6?`
4. `Where was Jax at step 11?`
5. `Was Jax ever in the galley?`
6. `Where is Jax now?`

What to look for:

- step-specific facts should not collapse into nonsense
- queries about exact steps should behave differently from "ever" queries
- the KB should not show malformed bare `at_step(entity, place)` facts

## Scenario 7: Multi-Fact Ingestion

Fresh session.

1. `Remember that Mara owns the observatory and Theo manages the night shift.`
2. `Remember that the board approved the renovation and the permit expires in June.`
3. `Remember that Jax loaded the crates, sealed the hatch, and departed at dawn.`
4. `/kb 50`

What to look for:

- whether a single turn yields multiple useful facts
- whether the operation list shows a clean deterministic breakdown
- whether the parser collapses the whole turn into one muddy predicate

## Scenario 8: Long Paragraph Story

Fresh session for each paragraph.

1. `At dawn, the museum opened early for the audit. Selene unlocked the archive room, Theo checked the seal ledger, and Mara signed the intake form before the visitors arrived.`
2. `After the hearing, Selene signed the lease, the board recorded the vote, and the clerk filed the final notice before noon.`
3. `Unit Alpha completed the repair, returned from the spacewalk, and docked at Bay 3 while Jax logged the inspection in the galley.`

What to look for:

- whether the ledger still reads clearly on longer inputs
- whether the console asks for clarification only when truly needed
- whether the resulting KB looks structured rather than bloated or bizarre

## Scenario 9: Mixed Intent Boundary

Fresh session.

1. `Remember that the launch plan ships next week, and tell me whether it is delayed.`
2. `Store that the museum opens at dawn, then tell me if it opens at noon.`
3. `Jax returned from the spacewalk, right?`

What to look for:

- whether the front door separates write and query intent sensibly
- whether it asks for clarification instead of bluffing through mixed instructions

## Scenario 10: Negative Cases

Fresh session.

1. `asdf qwer zzzz`
2. `Maybe sort of keep in mind the thing about the situation.`
3. `Blue because therefore.`
4. `The museum.`
5. `That one from before.`

What to look for:

- the console should not confidently commit junk
- ambiguity should be high
- clarification or `other` routing is a good outcome here

## Scenario 11: Rules And Conditions

Fresh session.

1. `If a permit expires, the renovation must pause.`
2. `If Unit Alpha returns from the spacewalk, the inspection can begin.`
3. `If the board approves the lease, Mara may sign the transfer.`

What to look for:

- whether the compiler treats these as rules rather than ordinary facts
- whether rule-like inputs are admitted, clarified, or rejected honestly

## Scenario 12: Slash Command Workflow

Any session with a few existing turns.

1. `/help`
2. `/state`
3. `/kb 20`
4. `/kb 100`
5. `/cancel`

What to look for:

- slash commands should bypass natural-language routing
- `/state` should reflect session and clarification status
- `/kb` should expose the actual live runtime KB

## One Strong Comparison Pack

If you want one compact run that puts pressure on several surfaces at once, try this in a fresh session:

1. `Remember that the launch plan ships next week.`
2. `Remember that it also requires board approval.`
3. `Who requires board approval?`
4. `The launch plan.`
5. `Does the launch plan ship next week?`
6. `Actually, it ships in two weeks.`
7. `When does the launch plan ship?`
8. `Remember that Jax was in the galley at step 6 and in the mudroom at step 11.`
9. `Where was Jax at step 6?`
10. `Where is Jax now?`
11. `At dawn, Selene unlocked the archive room, Theo checked the ledger, and Mara signed the intake form before the visitors arrived.`
12. `What happened before the visitors arrived?`
13. `/kb 50`

## Compare To Direct GIC

If you are comparing this UI to direct GIC interaction, compare these things rather than just the final answer text:

- how often the console clarifies instead of guessing
- whether the deterministic commit is visible and inspectable
- whether the KB after the turn is cleaner
- whether route and ambiguity feel honest
- whether the session export gives you a better post-mortem than direct chat

## If You Find Something Weird

Export the session and note:

- the exact utterance
- whether strict lock was on
- what the `Decision Ledger` said for `route`, `clarify`, and `commit`
- the relevant `/kb` snapshot

That is usually enough to turn a manual oddity into a reproducible engineering target.

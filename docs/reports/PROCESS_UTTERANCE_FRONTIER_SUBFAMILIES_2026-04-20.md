# Process Utterance Frontier Subfamilies

- date: `2026-04-20`
- path under test: [src/mcp_server.py](</D:/_PROJECTS/prethinker/src/mcp_server.py>) `process_utterance()`
- baseline sources:
  - [process_utterance_correction_pack_v1_baseline.json](</D:/_PROJECTS/prethinker/docs/data/frontier_packs/process_utterance_correction_pack_v1_baseline.json>)
  - [process_utterance_temporal_pack_v1_baseline.json](</D:/_PROJECTS/prethinker/docs/data/frontier_packs/process_utterance_temporal_pack_v1_baseline.json>)

This note turns the two red-family frontier packs into named mechanism clusters so the next pipeline-affecting change comes from a real shared failure shape instead of random annoyance.

## Correction Subfamilies

Correction is still the clearest red family, but it is not one thing.

### 1. False Ambiguity / Nonsense Clarification

Dominant shape:

- status: `clarification_required`
- verdict: mostly `fail`, a few `warn`
- examples:
  - `actually no, archive ledger is with Blake not Jan`
  - `actually no, cart is with Theo not Lena`
  - `actually no, launch plan is with Noor not Blake`

Typical behavior:

- front door routes the turn as `retract`
- asks a nonsense question like:
  - `Which specific fact ... should be retracted?`
  - `Which fact ... should be retracted: one involving X or Y?`

Practical read:

- this is primarily a front-door policy/routing failure
- the utterance is already explicit about the desired end state
- the system is inventing ambiguity rather than preserving the user’s correction

### 2. Invalid Retract / State Corruption

Smaller but harsher shape:

- status: `error`
- examples:
  - `actually no, cart is with Fred not Mara`
  - `actually no, cart is with Mara not Scott`
  - `actually no, drone kestrel is with Nora not Wilma`

Typical bad logic:

- `retract(cart_with_fred).`
- `retract(cart_with_mara).`
- `retract(drone_kestrel_with(nora)).`
- `retract(drone_kestrel_with(wilma)).`

Practical read:

- once correction gets past prethink, the downstream parse still often treats the new target as something to retract
- this is not just “too cautious”; it is semantically inverted

### Correction Recommendation

If we touch the pipeline next, the highest-leverage correction move is:

- **fix the correction interpretation policy before the retract machinery**

More concretely:

- grounded correction forms like `actually no, X is with A not B` should not default to `compiler_intent=retract`
- the first likely win is a policy/routing fix that treats these as state updates or corrected assertions when the surface form is explicit
- only after that should we worry about lower-level retract logic

That gives us the best chance of improving most of the correction pack at once instead of shaving isolated error strings.

## Temporal Subfamilies

Temporal is the stable number-two frontier. It is more yellow than correction, but it also contains a clean red core.

### 1. Step-Sequence Parse / Validation Failure

Red shape:

- status: `error`
- verdict: `fail`
- examples:
  - `at step 11 Noor was in Galley and later moved to Cedar House`
  - `at step 6 Noor was in Bay 3 and later moved to Mudroom`
  - `at step 11 Fred was in Salem and later moved to Harbor City`

Typical trace:

- prethink accepts the utterance with low ambiguity
- parse emits inferred forms like `at_step_11(...)` / `at_step_12(...)`
- validation then rejects them as invalid Prolog fact/goal forms

Practical read:

- this is a real parser/canonicalization seam
- the model is trying to preserve the sequence, but it is choosing an invalid surface representation

### 2. Sequence Flattening / Same-Step Contradiction

Yellow shape with semantic danger:

- status: `success`
- verdict: `warn`
- example:
  - `at step 11 Theo was in Morro Bay and later moved to Market Hall`

Typical bad logic:

- `at_step_11_theo_in_morro_bay.`
- `at_step_11_theo_in_market_hall.`

Practical read:

- the system keeps both legs, but flattens them into the same step
- this is not a crash, but it is still wrong enough to matter

### 3. Relative-Time Over-Simplification

Yellow shape:

- status: `success`
- verdict: `warn`
- examples:
  - `next week Hope was in Pineglass Ridge and later moved to Market Hall`
  - `next week Jan was in Galley and later moved to Mudroom`

Typical bad logic:

- `location(hope, pineglass_ridge, next_week).`
- second leg dropped or weakened

Practical read:

- the system keeps the first state but under-commits on the move
- this is a meaningful semantic loss, but probably a second-wave problem after the hard step failure

### 4. Temporal Binding Drift

Yellow shape:

- status: `success`
- verdict: `warn`
- example:
  - `at 9 AM Friday Jax was in Salem and later moved to Morro Bay`

Typical bad logic:

- `moved(jax, salem, morro_bay, friday_9am).`

Practical read:

- the move is preserved, but wrongly tied to the initial timestamp
- important, but likely not the first fix to chase

### Temporal Recommendation

If we touch the pipeline for temporal next, the highest-leverage move is:

- **fix the step-sequence representation seam before broader temporal reasoning**

More concretely:

- prevent `later moved` from being rendered as invalid `at_step_11(...)` / `at_step_12(...)` fact names
- preserve a valid canonical temporal representation first
- only then tackle same-step contradiction and relative-time softening

That is the cleanest way to reduce the red temporal cases without pretending we have solved all temporal reasoning.

## Recommended Intervention Order

1. `correction`
   Reason: still the clearest red family, and most of it appears to be a shared front-door interpretation mistake rather than many unrelated bugs.

2. `temporal_state`
   Reason: stable number-two frontier, with a clear red subfamily around invalid step-sequence rendering.

3. `query_after_write` / `pronoun_carryover`
   Reason: still important, but broader yellow families with less obvious single-mechanism leverage right now.

## Language Scope Note

This whole frontier stack is still best understood as **English-first**.

That does not mean the architecture must stay English-only forever. It means:

- the packs and forge are currently measuring English behavior
- dialect sensitivity is likely a later profile/context problem
- multilingual support should remain a future architectural seam, not a present claim about `v1`

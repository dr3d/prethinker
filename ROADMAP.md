# Prethinker Roadmap

Last updated: 2026-04-29

## Current Positioning

Prethinker is a local research workbench for governed semantic compilation:

```text
natural language
  -> semantic workspace proposal
  -> deterministic mapper/admission gate
  -> Prolog-like KB mutation, query, clarification, quarantine, or rejection
```

The authority boundary remains the core thesis. Neural models may interpret;
deterministic runtime code decides what can become durable state.

## Current Center Of Gravity

The older English-parser lane remains useful history, but it is no longer the
preferred research direction or the default demo path.

The active frontier is:

- `semantic_router_v1` as the model-owned context/profile planner
- `semantic_ir_v1` as the intermediate semantic workspace
- `qwen/qwen3.6-35b-a3b` as the main local semantic workspace model
- LM Studio/OpenAI-compatible structured output for schema-constrained JSON
- deterministic mapper/admission diagnostics in `src/semantic_ir.py`
- live console demos through `process_utterance()`
- bounded `medical@v0`, `legal_courtlistener@v0`, and `sec_contracts@v0`
- local UMLS Semantic Network assets
- hint-free raw-file/profile bootstrapping through `intake_plan_v1` and
  `profile_bootstrap_v1`

## What Recent Evidence Says

The most useful recent finding is qualitative and structural: the router/semantic
IR path often preserves meaning that the older parser path needed Python rescue
code to recover, and the mapper can keep that richer workspace behind the same
authority boundary.

Latest local verification:

- Full pytest suite: `394 passed`
- Edge runtime A/B: semantic IR `20/20`, `0.976` avg score, `0` non-mapper parse rescues
- Weak-edge runtime A/B: semantic IR `10/10`, `1.000` avg score, `0` non-mapper parse rescues
- Lava v5 source-record alignment rerun: `60/60` parsed, `60/60` domain selector,
  `60/60` admission-safe, `45/60` semantic-clean, `41/60` full expectation score,
  `0/60` temp-0 signature variance groups
- Policy/reimbursement demo: `4/4` parsed, `4/4` apply-error-free, `4/4`
  expected query matches, no derived violation write leak
- Multilingual router probe: `10/10` router choices and `10/10` compiler JSON
- Profile bootstrap closed loop: `8/8` valid workspaces, `7/8`
  expected-boundary hits

The remaining weak points are not JSON shape or basic routing. They are temporal
representation, durable rule admission, predicate canonicalization/query
planning, truth-maintenance dependency depth, and safe partial-operation
handling.

## Near-Term Priorities

1. **Mapper policy and diagnostics**
   - Tighten when `mixed`, `answer`, `clarify`, `quarantine`, and `reject` are
     projected from model IR.
   - Keep all policy changes structural. Avoid story-specific or English-phrase
     patches.
   - Make every admitted/skipped operation explain why it exists.

2. **Temporal fact representation**
   - Preserve dates, intervals, corrections, relative-time anchors, and event
     scope as durable facts when admitted.
   - Keep temporal extraction separate from full temporal proof claims.
   - Build queryable interval examples before claiming temporal reasoning.

3. **Rule admission**
   - Require rules to pass a stricter schema than facts.
   - Distinguish asserted rules, hypothetical rules, policy rules, and claims
     about rules.
   - Add focused tests before allowing new durable rule shapes.

4. **Noisy and multilingual semantic pressure**
   - Keep Silverton, Harbor, Lava, story-world, and raw-document lanes hard.
   - Add small batteries for typos, code-switching, foreign fragments, and
     ambiguous initials/pronouns.
   - Score semantic preservation separately from final admission policy.

5. **Hint-free predicate/profile discovery**
   - Keep `intake_plan_v1` and `profile_bootstrap_v1` LLM-owned.
   - Use human Prolog targets only as calibration, not product-time hints.
   - Measure whether proposed predicate surfaces support later QA and safe
     mapper admission.

6. **Medical/UMLS bounded demos**
   - Use UMLS as a semantic-type and normalization bridge, not a diagnosis
     oracle.
   - Make demos explain why a term was treated as medication, lab/procedure,
     symptom/finding, condition, allergy, or physiologic state.
   - Expand `medical@v0` only when a predicate earns its place through tests and
     a clear demo.

6. **Public docs hygiene**
   - Keep `PROJECT_STATE.md` and `docs/PUBLIC_DOCS_GUIDE.md` current.
   - Let Git history carry older direction notes.
   - Mark older parser-ladder docs as context when they are not the live
     guidance.

## Acceptance Criteria For The Next Good Checkpoint

- Full pytest suite is green.
- Public docs and docs hub describe semantic IR as the active research center.
- The console trybook has at least one semantic-IR-oriented demo that shows:
  - claim versus fact
  - clarification rather than bad commit
  - admitted versus skipped operations
  - temporal extraction limits
- A small temporal mutation representation exists and is queryable.
- No-language-handling discipline remains intact: new improvements come from
  model workspace quality, context/profile contracts, or structural mapper
  checks, not Python phrase patches.

## Still Out Of Scope

- Production medical advice or diagnosis.
- Letting model output directly authorize KB writes.
- Treating structured JSON as proof of truth.
- Broad claims of multilingual or temporal reasoning before the runtime can
  query those structures.
- Full fine-tuning as the primary path before prompt/runtime baselines are
  better understood.

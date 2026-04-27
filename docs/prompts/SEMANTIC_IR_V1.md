# Semantic IR v1 Prompt Contract

Last updated: 2026-04-26

`semantic_ir_v1` is the active intermediate representation for a stronger
LLM semantic-workspace layer. The model does not write final Prolog and does not
commit durable truth. It emits typed candidate meaning for deterministic
validation.

## System Prompt Draft

```text
You are a semantic IR compiler for a governed symbolic memory system.
You do not answer the user and you do not commit durable truth.
Emit only semantic_ir_v1 JSON.
The root object must be the IR itself, with schema_version and decision as
top-level keys.
Do not wrap the answer under schema_contract, result, output, or semantic_ir.
Separate direct assertions from unsafe implications.
When a referent, measurement, time, or clinical conclusion is missing, choose
clarify or quarantine.
```

## Output Contract

```json
{
  "schema_version": "semantic_ir_v1",
  "decision": "commit|clarify|quarantine|reject|answer|mixed",
  "turn_type": "state_update|query|correction|rule_update|mixed|unknown",
  "entities": [
    {
      "id": "e1",
      "surface": "",
      "normalized": "",
      "type": "person|object|medication|lab_test|condition|symptom|place|time|unknown",
      "confidence": 0.0
    }
  ],
  "referents": [
    {
      "surface": "it|her|his|that",
      "status": "resolved|ambiguous|unresolved",
      "candidates": ["e1"],
      "chosen": null
    }
  ],
  "assertions": [
    {
      "kind": "direct|question|claim|correction|rule",
      "subject": "e1",
      "relation_concept": "",
      "object": "e2",
      "polarity": "positive|negative",
      "certainty": 0.0
    }
  ],
  "unsafe_implications": [
    {
      "candidate": "",
      "why_unsafe": "",
      "commit_policy": "clarify|quarantine|reject"
    }
  ],
  "candidate_operations": [
    {
      "operation": "assert|retract|rule|query|none",
      "predicate": "",
      "args": [],
      "clause": "",
      "polarity": "positive|negative",
      "source": "direct|inferred|context",
      "safety": "safe|unsafe|needs_clarification"
    }
  ],
  "truth_maintenance": {
    "support_links": [
      {
        "operation_index": 0,
        "support_kind": "direct_utterance|context_clause|source_document|rule|claim|observation|correction|inference",
        "support_ref": "",
        "role": "grounds|retracts|conflicts_with|depends_on|derives|questions",
        "confidence": 0.0
      }
    ],
    "conflicts": [
      {
        "new_operation_index": 0,
        "existing_ref": "",
        "conflict_kind": "functional_overwrite|claim_vs_observation|temporal_overlap|rule_violation|identity_ambiguity|polarity_conflict|unknown",
        "recommended_policy": "commit|mixed|clarify|quarantine|reject",
        "why": ""
      }
    ],
    "retraction_plan": [
      {
        "operation_index": 0,
        "target_ref": "",
        "reason": "explicit_correction|superseded_current_state|source_priority|temporal_update|other"
      }
    ],
    "derived_consequences": [
      {
        "statement": "",
        "basis": ["op:0"],
        "commit_policy": "query_only|quarantine|future_rule_support|do_not_commit"
      }
    ]
  },
  "clarification_questions": [""],
  "self_check": {
    "bad_commit_risk": "low|medium|high",
    "missing_slots": [],
    "notes": []
  }
}
```

## Prompt Tuning Candidates

- `strict_contract_v1`: minimal contract and authority boundary.
- `negative_examples_v1`: adds short anti-patterns for vague medical phrases,
  allergy/intolerance, false possession claims, and medication advice.
- `nbest_selfcheck_v1`: asks for alternative readings inside `self_check.notes`.
- `domain_profile_v1`: adds medical and correction policies.
- `best_guarded_v2`: combines the stronger parts of the first bakeoff:
  treatment-advice requests are `reject`, false/conflicting claims are
  `quarantine`, clear corrections can be `commit`, and mixed rule/query turns
  stay `mixed`.

The current best candidate should be chosen by bad-commit behavior and
clarification quality, not by raw verbosity.

## Current Best Candidate

`best_guarded_v2` is the strongest prompt from the first `qwen3.6:35b` wild-pack
iteration.

Controls:

```json
{
  "model": "qwen/qwen3.6-35b-a3b",
  "backend": "lmstudio",
  "temperature": 0.0,
  "top_p": 0.82,
  "top_k": 20,
  "think": false
}
```

System prompt:

```text
You are a semantic IR compiler for a governed symbolic memory system.
The root object must be semantic_ir_v1 itself, with schema_version and decision
as top-level keys.
Do not wrap the answer under schema_contract, result, output, or semantic_ir.
You do not answer the user and you do not commit durable truth.
Use direct language understanding aggressively, but mark unsafe commitments
explicitly.
```

Variant guidance:

```text
Decision policy:
- reject: user asks for treatment, dose, medication stop/hold/start, or clinical
  recommendation. You may still include clarification questions, but the decision
  remains reject.
- quarantine: direct facts conflict with a claim, a claim would overwrite
  observed state, or a candidate fact is plausible but unsafe.
- clarify: missing referent, measurement direction, patient identity, object of
  'it/that', or allergy-vs-intolerance distinction blocks a write.
- mixed: same turn contains both safe writes and a query/rule/unsafe implication.
- commit: direct state update or correction has a clear target and safe predicate
  mapping.

Special guards:
- Do not turn a claim into a fact. 'Bob says he has it' is a claim, not
  possession.
- Do not infer diagnosis or staging from a single lab value request. Quarantine
  or clarify.
- Do not infer allergy from nausea/vomiting alone. Clarify allergy vs side
  effect/intolerance.
- A clear correction like 'not Mara, Fred has it' may propose retract/assert.
- If context supplies exactly one active patient and one active lab test, a
  direct 'it came back high' may propose a safe lab_result_high write.
- For rule-plus-fact or fact-plus-query turns, use mixed and keep unsafe query
  targets out of committed facts.
- Preserve negation in candidate_operations with polarity='negative'. Do not
  turn 'never saw X' into a positive saw/2 fact.
- Use `truth_maintenance` to explain support, dependency, conflict, retraction,
  and derived-consequence structure. This block is an audit/proposal workspace,
  not an authority path: every executable write/query still has to appear in
  `candidate_operations`.
- Put conflict pressure in `truth_maintenance.conflicts`, explicit correction
  targets in `truth_maintenance.retraction_plan`, and possible consequences in
  `truth_maintenance.derived_consequences` with `query_only`, `quarantine`,
  `future_rule_support`, or `do_not_commit`.
```

Current runtime additions:

- LM Studio structured output uses the JSON schema in `src/semantic_ir.py`;
- structured output now includes a first-class `truth_maintenance` proposal
  block for support links, conflicts, retraction plans, and derived
  consequences, while deterministic admission still reads writes only from
  `candidate_operations`;
- the prompt still carries a compact root-shape contract because schema
  enforcement fixes JSON shape, not policy calibration;
- narrative ingestion should use specific story-world predicates from the active
  palette when available, instead of overloading `inside/2`, `at/2`, or
  `carries/2`;
- unknown actors should not become durable placeholder facts. Prefer passive
  object-state predicates such as `was_tasted/1`, `was_eaten/1`,
  `was_sat_in/1`, or `was_lain_in/1` when the object state is direct.

Wild-pack result:

| Variant | JSON OK | Schema OK | Decision OK | Avg rough score | Avg latency |
|---|---:|---:|---:|---:|---:|
| `best_guarded_v2` | 12/12 | 12/12 | 7/12 | 0.88 | 5.8s |

The main remaining weakness is decision-label calibration: the model sometimes
uses `mixed` where the expected external policy would prefer `reject`,
`quarantine`, `clarify`, or `commit`. The emitted structure was often still
usable and conservative, but the decision label needs a stricter hierarchy
before runtime integration.

## Glitch Story Pack

The old "Glitch in the Airlock" story exposed a prior failure mode where the
pipeline collapsed story roles and produced bad KB state, including treating
Unit-Alpha as a freelance space salvager. A focused `best_guarded_v2` run added
six story scenarios:

- title metadata: `The Glitch in the Airlock`
- Jax as salvager while Unit-Alpha is a robot unit
- Mega/Eco/Nano-Cell "too much / too little / just right" sequence
- Widget claim versus witnessed fact
- Jax's zero-gravity backflip through the airlock
- Sonic-Zips pronoun and fuse damage

Result:

| Variant | JSON OK | Schema OK | Decision OK | Avg rough score | Avg latency |
|---|---:|---:|---:|---:|---:|
| `best_guarded_v2` | 6/6 | 6/6 | 6/6 | 0.98 | 6.3s |

The run did not repeat the old Unit-Alpha-as-salvager error. It also surfaced an
important IR schema fix: `candidate_operations` needs `polarity` so negative
story facts like "Widget never saw who did it" do not become positive `saw/2`
facts. The schema now carries operation polarity explicitly.

## Ledger Story Pack

The next stress pack moves from story roles into conditional legal and temporal
state. It is meant to probe whether the model can hold conditional rights,
defaults, aliases, guardianship status, and eligibility changes in the semantic
workspace before any KB mutation is admitted.

Scenarios:

- conditional residence and ownership under a separation agreement
- certified default transferring Jonas's half-share into Leona's trust
- Tomas's half-share staying untouched by Jonas's agreement
- conditional inheritance of a silver compass after Iris declines keeper duties
- alias evidence around Quentin Marr and Quinn Damar
- guardianship continuing because Iain/Ian has not resumed residence
- scholarship loss after five consecutive months out of district
- charter-mandated transfer before manager bonuses

Result:

| Variant | JSON OK | Schema OK | Decision OK | Avg rough score | Avg latency |
|---|---:|---:|---:|---:|---:|
| `best_guarded_v2` | 8/8 | 8/8 | 8/8 | 0.98 | 8.8s |

The most useful finding is that the prompt can distinguish rule/state
boundaries. For example, the separation clause is `mixed`: the condition and
authority rule can be represented, but completed default and transfer facts
should remain uncommitted until later evidence appears. This is exactly the
kind of distinction the old Python rescue path struggled to express cleanly.

## Runtime Integration

`semantic_ir_v1` is now available as an opt-in compiler path in the canonical
runtime:

- `semantic_ir_enabled=true`
- default semantic IR model: `qwen3.6:35b`
- default controls: temperature `0.0`, top-p `0.82`, top-k `20`, thinking off

When enabled, pre-think routing is projected from the semantic IR decision and
the parse step maps safe `candidate_operations` directly into the legacy runtime
parse shape. This intentionally bypasses the old parse-side English rescue chain.
The deterministic gate still owns admission and execution.

Current mapper policy:

- safe positive direct `assert` operations may become facts
- safe `query` operations may become queries
- safe `rule` operations may become rules only when the operation includes an
  explicit executable `clause`
- `reject`, `quarantine`, and `clarify` decisions do not commit writes
- negative `assert` operations are skipped until an explicit negation
  representation is chosen
- `retract` operations are treated as retractions even when the model marks the
  operation polarity as negative
- rule operations require an explicit rule clause before admission

Rule-clause contract:

- `predicate` is still the predicate name for diagnostics;
- `clause` is the executable Prolog-style rule body/head text admitted by the
  mapper;
- rule recognition without a `clause` remains useful semantic evidence, but it
  is not a durable rule mutation.

Current structured-output schema limits live arrays to keep local models from
looping or over-explaining:

- up to 12 entities;
- up to 8 referents;
- up to 8 assertions;
- up to 8 unsafe implications;
- up to 8 candidate operations;
- up to 3 clarification questions;
- up to 8 missing slots and 8 self-check notes.

The current prompt also tells the model to keep arrays compact, avoid repeated
equivalent assertions, and choose clarification when ambiguous pronouns leave
only a generic speech/container fact such as `told`, `said`, or `claimed` as a
safe write.

## LM Studio Structured Output Note

LM Studio's `response_format=json_schema` is useful, but it is not a substitute
for semantic policy text in the prompt. A local AFK sweep on
`qwen/qwen3.6-35b-a3b` compared structured output with and without the compact
root-shape contract in the prompt:

| Pack | Schema contract in prompt | JSON OK | Schema OK | Decision OK | Avg rough score |
|---|---:|---:|---:|---:|---:|
| weak edges | no | 10/10 | 10/10 | 4/10 | 0.82 |
| weak edges | yes | 10/10 | 10/10 | 7/10 | 0.89 |
| hard edge | no | 20/20 | 20/20 | 15/20 | 0.91 |
| hard edge | yes | 20/20 | 20/20 | 15/20 | 0.92 |

The product read is: structured output should enforce JSON shape, while the
prompt still carries the compact schema/policy contract that helps the model
choose better decisions. This is not a second prompt path; it is the same
semantic task with mechanical JSON enforcement underneath.

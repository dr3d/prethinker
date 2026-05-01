# Semantic IR v1 Prompt Contract

Last updated: 2026-05-01

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
  "propositions": [
    {
      "id": "prop_1",
      "kind": "fact|claim|observation|rule|query|correction|negation|hypothesis",
      "subject": "e1",
      "relation_concept": "",
      "object": "e2",
      "polarity": "positive|negative|unknown",
      "source_status": "direct_user_assertion|speaker_claim|document_claim|context|inference|observation",
      "temporal_scope": "timeless|current|bounded|event_relative|unknown",
      "epistemic_status": "asserted|claimed|observed|inferred|hypothetical|ambiguous|contradicted",
      "commit_recommendation": "candidate|quarantine|clarify|reject",
      "confidence": 0.0
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
      "proposition_id": "prop_1",
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
- `proposition_spine_v1`: optional v1-compatible bridge toward
  `semantic_ir_v2`; the model may emit `propositions[]` for what the text
  appears to mean, then link `candidate_operations[]` to those propositions.

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
- When useful, populate optional `propositions[]` before
  `candidate_operations[]`. A proposition is meaning; a candidate operation is
  a proposed effect. Every candidate operation includes `proposition_id`; use
  the matching proposition id when one exists, otherwise use an empty string.
- Preserve `source_status` and `epistemic_status` on propositions so claims,
  observations, document claims, hypotheses, and direct assertions remain
  distinct before mapper admission.
- Do not infer diagnosis or staging from a single lab value request. Quarantine
  or clarify.
- Do not infer allergy from nausea/vomiting alone. Clarify allergy vs side
  effect/intolerance.
- A clear correction like 'not Mara, Fred has it' may propose retract/assert.
- If context supplies exactly one active patient and one active lab test, a
  direct 'it came back high' may propose a safe lab_result_high write.
- For rule-plus-fact or fact-plus-query turns, use mixed and keep unsafe query
  targets out of committed facts.
- If a turn contains both a question and new grounded facts about named
  entities, keep the direct facts as safe candidate operations and put the
  question in a query operation. Do not demote newly stated facts into context
  just because they help answer the question.
- Candidate operation priority under the schema cap: direct grounded facts
  first, explicit retractions/corrections second, explicit user query third,
  durable rule clauses last. Complex default/exception/override policy language
  can stay in assertions, unsafe implications, and derived consequences when it
  would otherwise crowd out concrete facts.
- A query operation is not a durable truth claim. If the user asks a grounded
  question over available facts/rules, mark the query operation safe even when
  the possible answer should remain `query_only`, quarantined, or otherwise
  non-committal in `truth_maintenance.derived_consequences`.
- Use `answer` only for pure query turns with no new write/retract/rule
  candidate operations. If the utterance includes grounded writes plus a
  question, use `mixed`.
- Necessary conditions are not sufficient conditions. "No X without Y",
  "X requires Y", and "X depends on Y" may support `requires/2` or
  `depends_on/2` facts, but must not be inverted into `X_allowed :- Y` unless
  the utterance explicitly says Y is sufficient for X.
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
- `candidate_operations[].predicate` should be the bare predicate name, such as
  `lives_in`, not a signature such as `lives_in/2`.
- If `kb_context_pack.current_state_candidates` contains an old current-state
  fact and the utterance explicitly corrects it, propose a safe `retract` for
  the old clause and a safe `assert` for the replacement when clear. If the
  utterance conflicts with the old state but is not an explicit correction,
  choose `clarify` and ask whether the new value should replace the old KB
  value.
- Pronouns may resolve from KB context only when
  `kb_context_pack.current_state_subject_candidates` contains exactly one
  plausible subject for the utterance. Do not ask solely because of the pronoun
  when there is one current-state subject, no competing named subject, and an
  explicit correction marker. Multiple plausible candidates still require
  clarification.
```

Current runtime additions:

- LM Studio structured output uses the JSON schema in `src/semantic_ir.py`;
- structured output now includes a first-class `truth_maintenance` proposal
  block for support links, conflicts, retraction plans, and derived
  consequences, while deterministic admission still reads writes only from
  `candidate_operations`;
- Semantic IR calls can include a compact `kb_context_pack` containing exact
  retrieved KB clauses, current-state candidates, entity candidates, recent
  committed logic, and a small snapshot. This is symbolic context, not write
  authority. The model may use it to resolve references, identify corrections,
  and cite conflicts in `truth_maintenance`;
- Semantic IR calls now include `document_to_logic_compiler_strategy_v1`, a
  reusable context object that tells the model to establish source boundary,
  assertion status, entity value, predicate usefulness, repeated-record shape,
  truth-maintenance support, and query shape before proposing operations. This
  is strategy context only; deterministic admission still decides every write;
- the prompt still carries a compact root-shape contract because schema
  enforcement fixes JSON shape, not policy calibration;
- narrative ingestion should use specific story-world predicates from the active
  palette when available, instead of overloading `inside/2`, `at/2`, or
  `carries/2`;
- unknown actors should not become durable placeholder facts. Prefer passive
  object-state predicates such as `was_tasted/1`, `was_eaten/1`,
  `was_sat_in/1`, or `was_lain_in/1` when the object state is direct.
- policy/meeting/business turns now carry extra context-policy pressure around
  mixed write+query turns, explicit query operations, direct-fact priority, and
  necessary-versus-sufficient rule boundaries.

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

`semantic_ir_v1` is the canonical compiler path in the current runtime:

- `semantic_ir_enabled=true`
- current development Semantic IR model: `qwen/qwen3.6-35b-a3b`
- default controls: temperature `0.0`, top-p `0.82`, top-k `20`, thinking off

The router/context layer chooses the active profile, context modules, and
actions. The compiler emits a semantic workspace, and the deterministic mapper
projects safe `candidate_operations` into runtime mutations, queries, rules, or
diagnostic worlds. The old parse-side English rescue chain is no longer part of
the active path. The deterministic gate still owns admission and execution.

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

Current structured-output schema limits protect candidate-operation budget on
long documents. Optional audit arrays are intentionally smaller than the write
surface:

- up to 8 entities;
- up to 16 referents;
- up to 16 assertions;
- up to 16 unsafe implications;
- up to 64 propositions;
- up to 128 candidate operations;
- up to 6 clarification questions;
- up to 8 missing slots and 12 self-check notes.

The current prompt also tells the model to keep audit arrays sparse for dense
source compilation, avoid repeated equivalent assertions, and spend the budget
on durable/queryable `candidate_operations` using normalized atoms directly. If
safe direct facts exceed the schema cap, the model should mark
`segment_required_for_complete_ingestion` instead of silently summarizing.

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

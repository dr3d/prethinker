# Semantic IR Mapper Specification

Last updated: 2026-04-28

## Purpose

The mapper is the deterministic contract between `semantic_ir_v1` and durable
runtime behavior.

The LLM may propose a semantic workspace. The mapper decides what that proposal
means operationally:

```text
semantic_ir_v1 proposal
  -> projected decision
  -> admissible operations
  -> scoped diagnostic worlds for blocked candidates
  -> legacy parse/runtime packet
  -> KB mutation, query, clarification, quarantine, or rejection
```

This document exists to keep the mapper from becoming a new hidden patch pile.
Every mapper rule should answer:

```text
What IR shape does this handle?
Why does this guardrail exist?
Is it structural policy, or is it secretly language-specific?
What runtime behavior is guaranteed?
```

The mapper should contain structural guardrails. It should not learn English
phrases one special case at a time.

## Authority Boundary

`semantic_ir_v1` is not truth. It is a proposal.

The runtime may commit only after:

- the IR shape is valid enough to parse;
- a projected decision is derived;
- candidate operations pass mapper policy;
- predicate names and terms can be normalized into executable clauses;
- downstream registry/type/runtime gates accept the operation.

The LLM is allowed to be ambitious in interpretation. The mapper is required to
be conservative in admission.

## Mapper Inputs

| IR field | Mapper use | Notes |
| --- | --- | --- |
| `decision` | Initial decision, then projected by structural policy | The model label is advisory, not final. |
| `turn_type` | Helps identify queries, corrections, rules, and mixed turns | Used especially for hypothetical queries and correction projection. |
| `entities` | Maps entity IDs to normalized terms | If an operation arg references `e1`, mapper resolves it through `entities`. |
| `referents` | Exposes unresolved or ambiguous references | Ambiguous/unresolved referents become clarification ambiguities. |
| `assertions` | High-level semantic evidence | Used for projection such as claim plus direct observation -> `mixed`. |
| `unsafe_implications` | Things the model considered but should not commit | Non-duplicate unsafe implications can project `commit` to `mixed`. |
| `candidate_operations` | Only field that may produce clauses | Candidate operations still pass source/safety/polarity policy. |
| `clarification_questions` | User-facing question source for `clarify` | First question is used when clarification is required. |
| `self_check.missing_slots` | Clarification or quarantine signal | Optional provenance slots are ignored when a safe direct write exists. |
| `self_check.bad_commit_risk` | Confidence/uncertainty shaping | Does not by itself authorize or block writes. |

## Decision Projection

The mapper projects the model's top-level `decision` before creating runtime
behavior.

| IR shape | Projected decision | Why |
| --- | --- | --- |
| Pure hypothetical query with a safe query operation | `answer` | Hypothetical questions should be answered as queries and must not write premise/conclusion facts. |
| `commit` plus safe direct write plus non-duplicate unsafe implications | `mixed` | Some direct facts may be safe while other implications must remain uncommitted. |
| `commit` plus both claim and direct assertions | `mixed` | Claims and observations can coexist without collapsing claim content into fact. |
| Low-risk correction plus unsafe alternative whose policy is only `clarify` | `commit` | Harmless alternate modeling candidates such as symptom-vs-side-effect should not downgrade a complete safe correction. |
| Ambiguous referents where only a generic speech/container write is safe | `clarify` | A wrapper fact like `told(...)` should not hide the fact that the content itself needs clarification. |
| `commit` with only context-sourced writes plus unsafe implications | `mixed` | Context-sourced writes are skipped; the decision label must reflect that the useful work is partial/unsafe. |
| `quarantine` with only optional metadata slots missing and a safe direct write | `mixed` | Missing provenance/authority text should not block a clear safe operation. |
| `quarantine` correction with safe direct retract | `mixed` | A safe retraction may be admissible even if replacement assertions are unsafe. |
| `clarify` with missing essential slots | `clarify` | Missing patient/entity/measurement/referent blocks safe admission. |
| `reject` | `reject` | Explicit policy rejection remains authoritative. |

Projection is structural policy. It is not a phrase rewrite.

## Epistemic Worlds V1

Projection can block an operation that was otherwise structured enough to have
become a fact, rule, or retract. For example, a medical turn may contain a safe
memory fact and an unsafe dose-advice query; the mapper projects the turn to
`reject` so the memory fact cannot enter global truth.

The same lane can preserve supported-but-skipped operations. If the model
included a `truth_maintenance.support_links` entry for a candidate that mapper
policy still skips, the candidate is no longer treated as merely lost. It can be
copied into `skipped_world` while remaining outside durable truth.

Epistemic Worlds v1 preserves that blocked candidate in diagnostics using fixed
wrapper predicates:

```prolog
world_operation(reject_world, op_0, taking, fact).
world_arg(reject_world, op_0, 1, priya).
world_arg(reject_world, op_0, 2, warfarin).
world_policy(reject_world, op_0, reject).
world_clause(reject_world, op_0, 1, taking_priya_warfarin).
```

These clauses mean: "this candidate was seen in a rejected/quarantined/clarify
world." They do **not** mean `taking(priya, warfarin).` is true in the durable
domain KB. This gives traces and future UX a way to remember disputed,
rejected, or quarantined content without weakening the admission boundary.

Current status: diagnostic payload only. Persisting and querying scoped worlds
is an explicit future policy decision.

## Operation Admission

Only `candidate_operations` may become executable clauses.

| Operation condition | Mapper behavior | Why |
| --- | --- | --- |
| `safety != safe` | Skip operation | The model itself marked the operation unsafe or incomplete. |
| `source=inferred` write | Skip operation | Plausible inference is not durable truth. |
| `source=inferred` query in a pure hypothetical query | Admit query | Hypothetical answers often require a derived query target, but still do not write. |
| `source=context` assert/rule | Skip operation | Context is already-known state/rules; it must not be re-written as a new user assertion. |
| `source=context` retract | Admit if otherwise safe | Corrections often retract stale context facts. |
| `operation=assert`, positive polarity | Admit if predicate/args normalize | Direct safe facts become facts. |
| `operation=assert`, negative polarity, non-event predicate | Skip operation | The runtime does not yet have a general negative-fact semantics. |
| `operation=assert`, negative polarity, denial/speech event predicate | Admit | `denied(...)` records a speech/event fact, not logical negation. |
| `operation=retract` | Emit retract variants | Numbered aliases like `crate12`/`crate_12` are structural term normalization. |
| `operation=rule` with explicit `clause` | Admit if the rule clause normalizes | The model may propose a rule only when it has already compiled the executable rule shape. |
| `operation=rule` without explicit rule clause and variable-like args | Skip operation | Prevents variable stubs like `R` from becoming fake facts. |
| `operation=rule` without explicit rule clause but positive direct ground args | Admit as a fact-like rule record | Captures direct labels without synthesizing executable Prolog rules. |
| Quantified group assertion without individual expansion | Skip operation | Prevents fake facts like `submitted_form(residents)`. |

## Polarity Policy

`polarity=negative` does not mean "assert a negative Prolog fact."

Current policy:

- negative retracts are allowed;
- negative speech/event assertions are allowed for predicates like `denied/3`;
- general negative assertions are skipped until the runtime has explicit
  negation semantics;
- skipped negative assertions produce mapper warnings.

This avoids turning:

```text
Omar denied taking the key.
```

into:

```prolog
not_took(omar, key).
```

or any equivalent hard negative fact.

## Source Policy

`source` is a trust signal.

| Source | Meaning | Write behavior |
| --- | --- | --- |
| `direct` | Grounded in the current utterance | May write if safe. |
| `context` | Already present in KB/recent context | May support retractions; assert/rule writes are skipped. |
| `inferred` | Derived by model reasoning | Writes are skipped; pure-hypothetical queries may be admitted. |

This is one of the central anti-patch rules. It does not care what language the
utterance was written in; it cares how the IR grounds the operation.

## Grounding Policy

The generic mapper may reject writes whose arguments are obvious unresolved
placeholder atoms such as `patient`, `someone`, `his`, `unknown`, or
placeholder-shaped atoms such as `unknown_agent`.

This is a structural guardrail, not an English phrase repair:

- it applies to admitted write candidates, not to raw utterance text;
- it blocks durable `assert`/`rule` operations until the missing entity is
  grounded;
- it does not block a query that intentionally asks about an unresolved slot.

Domain-specific type grounding belongs to profile contracts. For example,
`medical@v0` stores UMLS semantic-group expectations in
`modelfiles/profile.medical.v0.json`, and `src/medical_profile.py` reads that
metadata when deciding whether `taking(Patient, Thing)` names a medication or a
condition. The semantic IR mapper should not grow medical-specific type lists.

The active Semantic IR call now receives those profile contracts and compact
profile context as model input when `medical@v0` is selected. This is
intentional domain tuning, but it is profile-owned rather than mapper-owned:

- the profile may tell the model what predicate contracts and aliases exist;
- the model may use that context to build a better workspace;
- the mapper and profile validators still decide what can become durable state.

Future domains should follow the same catalog shape instead of adding ad hoc
logic to the generic mapper. See
[docs/DOMAIN_PROFILE_CATALOG.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PROFILE_CATALOG.md).

For narrative ingestion, the same policy blocks tempting but ungrounded event
facts such as:

```prolog
sat_in(unknown_agent, mama_bear_chair).
```

If the utterance only says that an unknown person acted on an object, the model
should prefer an admitted passive object-state predicate when one exists, such
as `was_tasted(papa_bear_porridge)` or `was_sat_in(mama_bear_chair)`.

## Predicate Palette Policy

The active predicate palette is an admission contract, not just prompt advice.
The model may propose any `candidate_operations` it wants, but the mapper skips
operations whose predicate signature is outside the active allowed set.

This applies to:

- `assert` operations;
- `query` operations;
- `retract` targets;
- every predicate signature inside an executable `rule` clause.

For example, if a probate pack allows `claimed/3`, `verbal_amendment/3`, and
`valid_amendment/1`, a model-proposed `excluded(arthur, beatrice)` operation is
not admitted. The trace records:

```text
predicate_not_in_allowed_palette
```

This is a structural guardrail. It does not teach Python Spanish, probate law,
or medical vocabulary; it only enforces the current domain contract after the
LLM has built the semantic workspace.

The current generic registry also includes a small story-world event/state
palette so narrative runs do not have to misuse broad predicates:

- `tasted/2`, `ate/2`, `ate_all/2`
- `sat_in/2`, `lay_in/2`, `asleep_in/2`
- `was_tasted/1`, `was_eaten/1`, `was_sat_in/1`, `was_lain_in/1`
- `walked_through/2`, `ran_through/2`, `entered/2`, `exited/2`
- `broke/1`, `returned_home/1`, `went_to/2`, `woke_up/1`
- preference/fit predicates such as `too_hot_for/2` and `just_right_for/2`

This palette is intentionally generic story/world-state vocabulary, not a
Goldilocks patch. It gives the LLM better legal targets while keeping the mapper
free to reject out-of-palette or ungrounded operations.

## Predicate Contract Role Policy

Predicate contracts may also declare argument roles and ordering, such as:

```json
{
  "signature": "interval_start/2",
  "args": ["interval", "date"]
}
```

The mapper now treats those contracts as admission evidence. Name/arity palette
checks answer "is this predicate allowed?" Contract role checks answer "is this
candidate operation shaped like that predicate contract?"

The current role gate is deliberately conservative. It blocks only clear shape
errors, for example:

- an `interval` slot receiving a date or person-like entity;
- a `date` slot receiving a person or place-like entity;
- a `person` slot receiving a time, place, document, or medical concept;
- a `document`/`source` slot receiving a person or time value.

The mapper does not infer legal, medical, or story meaning from raw English to
make this decision. It uses the IR's normalized arguments, entity metadata, and
profile-owned predicate contracts. Ambiguous cases are allowed to continue to
profile validators or runtime policy; obvious mismatches are skipped with:

```text
predicate_contract_role_mismatch
```

This is the next step after predicate-palette enforcement. It keeps predicate
contracts visible and executable without turning the generic mapper into a
domain ontology.

## Profile Contract Validator Policy

Profiles may attach small declarative validators to individual predicate
contracts. These validators are not prompt hints; they are explicit admission
policy carried by the selected profile package.

Current supported validator:

```json
{
  "kind": "argument_must_not_contain_terms",
  "argument": "finding_content",
  "terms": ["alleged", "complaint"],
  "reason": "allegation_not_court_finding"
}
```

This lets `legal_courtlistener@v0` say that allegation-like content must not be
admitted as `finding/4`, and lets `sec_contracts@v0` say that obligation-like
future language must not be admitted as `breach_event/2`. The rule is still
profile-owned and visible in JSON. The generic mapper only applies the declared
validator to normalized IR arguments.

Skipped operations report the profile reason, such as:

```text
allegation_not_court_finding
obligation_language_not_breach_event
```

The purpose is to make domain guardrails inspectable and reusable without
teaching the mapper hidden legal or contract prose.

## Unsafe Implications

`unsafe_implications` records tempting candidates that should not become durable
state.

The mapper uses unsafe implications to project `commit` to `mixed` when safe
operations coexist with unsafe material. One exception exists:

- if an unsafe implication duplicates an operation that the final
  `candidate_operations` marks safe, the mapper treats it as stale model
  bookkeeping and does not downgrade the decision.

This handles structured-output self-contradictions without adding English
phrase patches.

## Clarification Policy

Clarification is required when essential slots are missing:

- patient/entity identity;
- unresolved referent;
- measurement direction or lab target;
- correction target;
- required predicate argument.

Optional provenance slots do not block a safe direct write:

- `source_document_id`
- `source_note_id`
- `source_encounter_id`
- `reason`
- `reason_for_quarantine`
- `quarantine_reason`
- `authority`

Those slots are useful metadata, not semantic prerequisites unless a predicate
schema explicitly requires them.

One boundary now matters:

- ordinary missing-slot turns should `clarify`;
- high-risk speculative observations with ambiguous referents, unsafe
  implications, question-like/low-certainty assertions, and no safe admissible
  operation should `quarantine`.

That distinction keeps the system from asking users to rescue a turn whose only
available content is unsafe speculation.

## Query Policy

Queries do not mutate the KB.

Pure hypothetical questions are projected to `answer` when:

- the turn is a query or otherwise explicitly hypothetical/counterfactual;
- a safe query operation exists;
- no non-context write operation is present, except identity premises that are
  scoped to the query itself.

The mapper may admit an `inferred` query target for a hypothetical question,
because the whole point of the turn is to ask about a derived consequence. This
exception does not apply to inferred writes.

Identity premises such as `candidate_identity(silverton_a, alfred)` are not
durable truth when they are embedded inside a question like "if A is Alfred,
does Arthur lose?" The mapper skips those candidate identity writes and admits
the query instead.

## Claim-Only Policy

A speech wrapper can be useful evidence, but it is not a free pass through the
authority boundary. When the only safe direct writes are communication
containers such as `claimed(...)` and the same IR also contains unsafe
substantive implications, the mapper projects the turn to `quarantine` and
blocks the write.

That policy prevents a biased or legally loaded claim from becoming the only
durable residue of a turn whose actual content is unsafe.

## Alias Grounding Policy

Initial-only person aliases are weak grounding for durable person-state facts.
If a safe direct state write uses an entity like `A. Silverton`, the mapper may
still admit the factual temporal/event clause, but it projects the decision to
`mixed`. This keeps the KB traceable while preserving the unresolved identity
pressure for follow-up policy.

## Minimal Temporal Vocabulary

Temporal language is in scope for semantic extraction, but full temporal proof is
not yet claimed. The current durable representation should stay factual and
auditable:

```prolog
occurred_on(Event, Date).
interval_start(Event, Date).
interval_end(Event, Date).
corrected_temporal_value(Event, Field, OldValue, NewValue).
```

These predicates let the workspace preserve what the model understood about
dates, intervals, and corrections without pretending the runtime can already
prove every temporal consequence. A future temporal reasoner can consume these
facts for duration, ordering, overlap, and consecutive-interval checks.

The current mapper also checks one temporal invariant: when an IR proposes both
`interval_start(Interval, Start)` and `interval_end(Interval, End)` with
parseable dates, `Start` must not be after `End`. Violations are skipped with:

```text
temporal_interval_order_mismatch
```

This is not full temporal reasoning. It is a structural sanity check before
durable interval facts reach the KB.

## Stored-Logic Conflict Policy

Some writes are dangerous because they look like ordinary additions but may
change the meaning of existing state:

- `lives_in(mara, salem)` when the current KB already has
  `lives_in(mara, denver)`;
- `scheduled_for(audit, tuesday)` when the current KB already has a current
  schedule for Monday;
- `cannot_ship(crate12)` when committed rules and facts imply
  `may_ship(crate12)`;
- a claim that contradicts an observed fact.

The intended policy is:

- explicit corrections may propose retract/assert operations;
- non-exclusive additions, such as a second condition, may commit;
- ambiguous current-state replacements should clarify before mutating;
- claims that contradict observations may be stored as claims, but must not
  erase observed facts;
- rule-derived conflicts should be surfaced as admission pressure until the
  runtime has a general contradiction checker.

This is not an English patch. It is a KB-state admission question: "does this
operation safely add knowledge, or does it silently rewrite what the KB already
means?"

Current implementation is deliberately narrow:

- `src/mcp_server.py` checks candidate fact clauses immediately before runtime
  writes;
- a small structural set of likely-functional current-state predicates, such as
  `lives_in/2`, `located_at/2`, `located_in/2`, and `scheduled_for/2`, blocks a
  different value for the same subject unless the turn already carries an
  explicit retract/correction;
- modal predicate pairs are checked by naming shape: `cannot_*`/`cant_*` facts
  are probed against derivable `may_*`/`can_*` queries, and vice versa;
- numbered atom spelling variants such as `crate12` and `crate_12` are treated
  as structural aliases for this probe.

This guard is not the final contradiction engine. It is a first admission
pressure layer for the most dangerous mutation shape: an apparently harmless
assertion that silently fights stored current state or a rule-derived modal
consequence.

## Trace Obligations

Every structural intervention should be visible in traces or warnings.

Current trace class:

- `structural_mapper`

Examples:

- `semantic_ir_mapper`
- `semantic_ir_prethink_projection`
- skipped inferred write
- skipped context-sourced assert/rule
- skipped negative assertion
- skipped quantified group assertion
- duplicate unsafe implication ignored by projection

The mapper also emits `admission_diagnostics_v1` on semantic IR parse payloads
and mapper trace entries. This is an advisory scorecard, not an authority path.
It records:

- model decision versus projected decision;
- projection reason;
- per-operation source/safety/polarity/predicate features;
- per-operation predicate-contract presence and argument roles;
- admitted versus skipped operations;
- concrete clauses the mapper considered admissible;
- `clause_supports`, which connect each admitted clause back to the mapper
  operation index, predicate, source, polarity, and rationale codes;
- skip reasons and rationale codes such as `source_policy`,
  `candidate_safety_gate`, `polarity_policy`, `predicate_contract_role`,
  `profile_contract_validator`, `temporal_policy`, and `no_rule_synthesis`.

This lets us ask "why does this guardrail exist?" at operation granularity
without turning score features into write permission.

Clause support records are not yet a full truth-maintenance system. They are the
first dependency breadcrumb: enough to show why a fact, rule, retract, or query
was passivated for runtime, and enough to give future derived conclusions
something to point back to.

`semantic_ir_v1` now also has a `truth_maintenance` proposal block. This is the
model's place to do the smarter semantic work we want from the larger model:

- connect candidate operations to direct utterance text, context clauses, source
  documents, claims, observations, rules, corrections, or inferred support;
- identify conflicts such as functional overwrites, claim-vs-observation
  pressure, temporal overlap, rule violations, identity ambiguity, and polarity
  conflict;
- propose explicit retraction targets for corrections;
- list derived consequences while marking them `query_only`, `quarantine`,
  `future_rule_support`, or `do_not_commit`.

The block is intentionally not executable. The mapper copies it into
diagnostics and traces for auditability, but it never admits a write from
`truth_maintenance`. Durable effects still come only from admitted
`candidate_operations`. This gives the LLM a richer truth-maintenance workspace
without turning Python into an English patch layer or turning model inferences
into state.

Diagnostics also compare the model's truth-maintenance proposal against mapper
admission. The comparison is still non-authoritative, but it surfaces fuzzy
compiler edges such as:

- an admitted operation with no model support link;
- a model-supported operation skipped by the mapper;
- a model conflict whose recommended policy is `clarify`, `quarantine`, or
  `reject` while the mapper admitted the operation;
- a retraction plan that does not line up with an admitted `retract` or a
  scoped retraction-plan world record;
- an admitted retract that lacks a retraction-plan entry.

These are research pressure gauges. They are meant to show where the compiler
contract, prompt, profile context, or predicate palette is still fuzzy, not to
silently change admission outcomes.

The current scoped-world path can preserve non-executable retraction pressure as
`world_retraction_target/4` and `world_retraction_reason/4`. That makes "the
model noticed this may supersede an old clause" visible without treating the
proposal as a durable retract. Projection-level `reject`, `quarantine`, or
`clarify` decisions can also explain why supported skipped operations are not
mapper drift.

Semantic IR calls can also receive `kb_context_pack`, a compact deterministic
retrieval packet built from the current runtime KB. It is intentionally small
enough for the current 16K-context model path and includes:

- exact relevant KB clauses;
- likely functional current-state candidates;
- likely current-state subject candidates, so pronouns can be resolved only
  when the KB working set has one plausible subject;
- entity candidates from those clauses;
- recent committed logic;
- a small fallback KB snapshot;
- retrieval terms and a manifest describing the packet.

This is symbolic context, not RAG authority. The model may use it to resolve
referents, recognize corrections, and populate `truth_maintenance`, but it must
not restate old KB clauses as new writes. The mapper still admits only
`candidate_operations`.

The A/B harness additionally classifies non-structural legacy events as:

- `legacy_route_fallback`
- `semantic_rescue_english`
- `domain_medical`
- `clarification_policy`
- `authority_admission`

The deletion-pressure metric is:

```text
semantic_rescue_english_count == 0
```

while scores and final KB state hold.

## Non-Goals

The mapper should not:

- repair English phrases;
- infer domain meaning from raw utterance text;
- synthesize facts from prose outside `candidate_operations`;
- synthesize durable Prolog rules without an explicit rule clause;
- turn claims into facts;
- create a general negative-fact system until the runtime supports one;
- treat structured JSON validity as semantic safety.

## Conformance Batteries

The mapper contract should be guarded by small no-GPU unit tests.

Required cases:

- safe direct assertion maps to a fact;
- unsafe candidate operation is skipped;
- inferred write is skipped;
- inferred hypothetical query is admitted;
- context-sourced assert/rule is skipped;
- context/direct retract is admitted;
- negative non-event assertion is skipped;
- denial event assertion is admitted;
- quantified group atom is skipped;
- placeholder write argument is skipped while placeholder query remains
  representable;
- predicate contract role mismatch is skipped;
- correctly shaped predicate contract arguments are admitted;
- profile contract validator failure is skipped;
- inverted start/end interval pairs are skipped;
- minimal temporal facts are admitted as factual representation, not temporal
  proof;
- duplicate unsafe implication does not downgrade an admitted safe operation;
- claim plus direct observation projects to `mixed`;
- optional provenance slots do not block safe correction;
- unresolved referents project to clarification.

Live model batteries then test whether the LLM can produce good IR. Unit tests
test whether the deterministic mapper keeps its promises.

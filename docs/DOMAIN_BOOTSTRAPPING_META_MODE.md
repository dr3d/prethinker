# Domain Bootstrapping Meta-Mode

Last updated: 2026-04-29

This note records a frontier idea: Prethinker should eventually help discover
the predicate palette for a domain it does not already know.

Today, the strongest path is profile-aware intake:

```text
utterance + context
  -> selected domain profile
  -> allowed predicates + predicate contracts
  -> semantic_ir_v1 workspace
  -> deterministic mapper/admission
  -> KB mutation, query, clarification, quarantine, or rejection
```

That works when a profile already exists. The open question is what Prethinker
should do when the domain is new, vague, or only partially covered by existing
profiles.

## Core Idea

Add a meta-mode where the model does not propose KB writes. Instead, it proposes
a candidate domain profile:

```text
sample text / conversation / corpus slice
  -> domain analysis workspace
  -> candidate entities, roles, predicates, contracts, risks
  -> human or deterministic review
  -> draft profile package
  -> later ordinary Semantic IR runs use the approved profile
```

This is not a shortcut around admission. It is a way to use the model's broader
semantic intelligence to help design the admission surface.

The boundary should stay strict:

```text
The model may propose the language of a domain.
The runtime decides when that language becomes an approved profile.
Only approved profiles can authorize durable predicate palettes.
```

## The Codex Move We Want To Capture

When a capable LLM is asked to "turn this document into Prolog" without a prior
profile, it usually performs an implicit strategy:

1. Read the whole source for recurring roles and relation types.
2. Identify durable entity classes: documents, authorities, groups, rights,
   obligations, grievances, events, sources, claims, and decisions.
3. Choose predicate names that preserve useful distinctions instead of merely
   summarizing the text.
4. Choose argument order and arity so later questions are natural.
5. Separate source claims from objective facts when provenance matters.
6. Notice repeated structures and decide whether to use stable ids, such as
   `grievance(g1, ...)`, plus properties like `grievance_actor/2`.
7. Add a few derived rules only when the source states a general relationship
   clearly enough to make the rule executable.

That strategy is not magic, and it should not live in Codex as an invisible
preprocessor. In Prethinker terms it is an LLM-owned control-plane pass:

```text
raw text
  -> profile_bootstrap_v1 proposal
  -> candidate predicates + contracts + risks + starter cases
  -> review / scoring / optional draft-profile run
  -> ordinary semantic_ir_v1 compiler
  -> deterministic mapper/admission
```

The important rule is that Python may carry the object between stages, validate
schemas, and score structural consistency, but Python must not inspect the raw
language to invent predicates or rewrite the utterance.

## Document-To-Logic Compiler Recipe

The reusable recipe is:

1. Establish the source boundary.
   - Assign a source/document id.
   - Decide whether the source is authoritative, testimonial, fictional,
     legal, medical, contractual, etc.
   - Decide which statements are source claims rather than global facts.
2. Extract stable entities.
   - Promote a term to entity status when it is recurring, role-bearing,
     acting, acted upon, a source of authority, a document, a group, an
     ambiguity target, or needed for a later query/rule.
   - Do not promote every noun phrase.
3. Classify each clause.
   - definition/principle
   - right
   - rule
   - grievance/accusation
   - event
   - relationship
   - declaration/action
   - pledge/obligation
   - appeal/petition
   - ambiguity candidate
4. Decide assertion status.
   - objective durable fact
   - source claim
   - accusation
   - rule-like norm
   - final declaration act
   - unsafe implication
   - test-only scaffold
5. Map clause type to predicate family.
   - principles -> claim/source assertion or right predicates
   - grievances -> stable grievance ids plus actor/target/method/purpose/effect
   - rules -> rule records and optional executable clauses
   - declarations -> explicit declaration/action predicates
   - relationships -> connection/governance/allegiance predicates
   - petitions/appeals -> petitioned/appealed/warned predicates
   - pledges -> pledge predicates
   - ambiguity -> ambiguous alias / candidate identity predicates
6. Normalize names.
   - Use lowercase snake_case atoms.
   - Preserve source-local identity.
   - Use ids for repeated structures.
7. Add provenance and safety.
   - Claims, accusations, grievances, and source records should remain
     distinguishable from objective durable facts.
   - Admission risks should name tempting unsafe collapses.
8. Add derived rules only when useful.
   - Keep derived/test rules separate from extracted facts.
   - Do not pretend derived rules were directly stated unless the source
     actually stated them.

Predicate selection heuristic:

```text
Can I query it?
Can I infer from it?
Can it prevent a bad write?
Can it preserve provenance?
Can it distinguish claim from fact?
Can it represent a repeated structure?
Can it support correction or contradiction handling?
```

Entity selection heuristic:

```text
recurring
role-bearing
acted upon
acting on others
source of authority
document
group
possible ambiguity target
needed for a rule
needed for a later query
```

The highest-level instruction is:

```text
Model the source's epistemic structure, not just its surface grammar.
```

## Hint-Free Predicate Discovery

The cleanest version of this mode gives the model the source text and generic
profile-bootstrap contract, but **does not** give it a human-authored Prolog
target surface. That is the mode closest to future product use.

In hint-free discovery:

- the model proposes entity types, predicate families, argument contracts,
  repeated structures, admission risks, and starter cases;
- Python validates schema and structural consistency;
- Python may compare signatures after the fact for evaluation;
- Python does not derive predicates from source words;
- Python does not split the document on semantic grounds;
- Python does not rewrite model predicate choices into a preferred ontology.

This matters because the product will usually have no `expected.pl` file. The
system has to grow a reviewable symbolic surface from the source material and
then test whether that surface supports safe ingestion and later query.

Human-authored Prolog remains useful for research calibration. It answers a
different question:

```text
Can the model align to this particular symbolic style if we show it the target
signature roster?
```

Hint-free discovery asks the harder product question:

```text
Can the model invent a useful symbolic style when no target roster exists?
```

## Why It Matters

For a random domain, the hardest part may not be extracting one fact. It may be
discovering the right symbolic vocabulary:

- What are the durable entity types?
- Which relationships matter?
- Which relations are claims rather than facts?
- Which predicates are functional or current-state-like?
- Which predicates need provenance?
- Which distinctions should be clarified instead of guessed?
- Which tempting writes should be quarantined?
- Which rules are executable, and which are only policy prose?

If Prethinker can help answer those questions, it becomes more than a set of
hand-authored profiles. It becomes a workbench for growing profiles safely.

## Proposed Output Shape

A future `profile_bootstrap_v1` output could look like:

```json
{
  "domain_guess": "warehouse_safety",
  "confidence": 0.82,
  "entity_types": [
    {"name": "asset", "examples": ["forklift_7", "loading_dock_b"]},
    {"name": "inspection", "examples": ["march_safety_walkthrough"]},
    {"name": "issue", "examples": ["brake_warning", "loose_guardrail"]}
  ],
  "candidate_predicates": [
    {
      "signature": "inspected_on/3",
      "args": ["inspector", "asset", "date"],
      "why": "Repeated source text records inspections as durable events."
    },
    {
      "signature": "requires_repair/2",
      "args": ["asset", "issue"],
      "why": "The domain distinguishes observed issues from completed repairs."
    }
  ],
  "repeated_structures": [
    {
      "name": "inspection finding list",
      "why": "The source records multiple findings with shared actor, target, issue, and status shape.",
      "id_strategy": "finding_1, finding_2, ... per source record",
      "record_predicate": "finding/2",
      "property_predicates": ["finding_actor/2", "finding_target/2", "finding_status/2"],
      "example_records": [
        "finding(finding_1, loose_guardrail).",
        "finding_actor(finding_1, march_safety_walkthrough)."
      ],
      "admission_notes": [
        "A finding id is a source-record id, not proof that an unrelated source confirmed the issue."
      ]
    }
  ],
  "admission_risks": [
    "A worker report is not the same as an inspection finding.",
    "A scheduled repair is not a completed repair.",
    "A cleared asset should probably retract or supersede an active hazard only with explicit source support."
  ],
  "clarification_policy": [
    "Clarify asset identity when location-only descriptions match multiple assets.",
    "Clarify whether a reported issue was observed, alleged, or repaired."
  ],
  "starter_frontier_cases": [
    {
      "utterance": "Mina said forklift 7's brakes squealed, but the inspection only found a loose mirror.",
      "expected_boundary": "claim versus inspection finding"
    }
  ]
}
```

This object is profile-design material. It should not be mapped directly into
the Prolog KB.

## Expected-Prolog Calibration

For research calibration, `scripts/run_domain_bootstrap_file.py` can compare a
raw-file bootstrap run against a human-supplied expected Prolog file:

```powershell
python scripts\run_domain_bootstrap_file.py `
  --text-file tmp\proclamation.md `
  --expected-prolog tmp\proclamation.pl `
  --domain-hint recall_proclamation `
  --backend lmstudio `
  --model qwen/qwen3.6-35b-a3b `
  --compile-source
```

That comparison is structural. Python extracts predicate signatures from the
expected Prolog and from the emitted facts/rules; it does not inspect the raw
English source to invent predicates.

There is also a calibration-only mode:

```powershell
python scripts\run_domain_bootstrap_file.py `
  --text-file tmp\proclamation.md `
  --expected-prolog tmp\proclamation.pl `
  --use-expected-signatures-as-guidance `
  --domain-hint recall_proclamation `
  --backend lmstudio `
  --model qwen/qwen3.6-35b-a3b `
  --compile-source
```

This gives the model the human-supplied predicate signature roster as an
ontology reference. It is useful for learning whether the LLM can align to a
target Prolog style, but it should not be mistaken for open-domain autonomous
profile discovery.

Current lesson from the Declaration and Proclamation targets:

- With target-signature guidance, profile discovery can get close to a supplied
  ontology surface.
- One-shot Semantic IR compilation still hits the operation cap on long,
  information-dense documents.
- The clean architecture move is now LLM-owned intake planning: the model
  chooses follow-up passes such as source metadata, entity taxonomy,
  principles/rules, grievance records, declarations/policies, and pledges.
- Python should continue to validate schemas, compare signatures, and carry
  context between stages; it should not decide where the English document
  should be semantically split.

## LLM-Owned Intake Plan

The raw-file runner now has an explicit `intake_plan_v1` pre-pass. This is the
visible version of the move a capable Codex-like model makes implicitly before
writing Prolog:

```text
raw source document
  -> intake_plan_v1
       source boundary
       epistemic stance
       symbolic strategy
       entity strategy
       predicate-family strategy
       pass plan
       risk policy
  -> profile_bootstrap_v1
  -> semantic_ir_v1 compile
  -> deterministic mapper/admission
```

The intake plan is not truth, not Prolog, and not a KB mutation. It is a
control-plane object: a structured model proposal for how the later compiler
should approach the source.

This matters because the desired behavior is not "extract every noun and verb."
It is:

```text
understand source type
preserve epistemic boundary
choose predicate families
allocate dense material across focused passes
then let deterministic admission decide what can become durable state
```

Python does not inspect the document to decide those passes. It only carries
the model-authored pass plan forward.

## Plan-Pass Compilation

Long source documents are now compilable in two modes:

- one flat source compile;
- `--compile-plan-passes`, which runs one Semantic IR compile per
  LLM-authored `intake_plan_v1.pass_plan` item.

Plan-pass compilation is closer to the way a human or Codex-like model handles a
dense document: first source boundary, then principles/rules, then repeated
records, then final declarations/pledges, instead of one overstuffed pass where
the first repeated list consumes the operation budget.

The current planner guidance is intentionally sharper than "make some chunks."
For long source lists, the model should split work by semantic job when the text
supports it: source records and ledgers, reporters/witnesses/complainants,
measurements, identity ambiguity, rules with conditions, remedies/declarations,
and pledges. Python still does not find those topics in the source; the plan is
LLM-authored and carried forward as context.

Example:

```powershell
python scripts\run_domain_bootstrap_file.py `
  --text-file tmp\declaration.md `
  --expected-prolog tmp\declaration.pl `
  --use-expected-signatures-as-guidance `
  --domain-hint declaration_style_document `
  --backend lmstudio `
  --model qwen/qwen3.6-35b-a3b `
  --compile-source `
  --compile-plan-passes
```

Recent calibration results:

```text
Declaration, one flat compile:
  emitted signature recall: 0.159
  admitted operations: 128

Declaration, intake-plan pass compilation:
  emitted signature recall: 0.623
  admitted operations: 234

Proclamation, first plan-pass compile after canonicalization pressure:
  emitted signature recall: 0.402
  profile signature recall: 0.795
  admitted operations: 302
```

These numbers are calibration against human-authored Prolog style, not product
claims. In the product there is no expected Prolog answer key. The useful lesson
is architectural: LLM-owned planning plus focused passes gives the compiler
more of the same leverage Codex used manually, without Python doing NLP.

The remaining hard edge is predicate canonicalization drift. The model may
understand the document but offer competing surfaces such as
`grievance_observation_location/2` and `observation_location/2`, then compile
with a different surface than the human target. That should be solved by
profile guidance, schema pressure, and review loops, not by a Python synonym
rewriter over the raw utterance.

## Repeated Structure Contract

The current `profile_bootstrap_v1` contract now includes `repeated_structures`.
This is the first explicit attempt to capture the "Declaration of Independence"
style move that a capable LLM makes when it notices a list of recurring
accusations, grievances, commitments, obligations, incidents, or docket entries.

The model should not merely propose:

```prolog
grievance(Source, withheld_assent).
grievance(Source, obstructed_migration).
```

when the source naturally supports a richer record family:

```prolog
grievance(g1, withheld_assent_to_laws).
grievance_actor(g1, central_authority).
grievance_target(g1, colonies).
purpose(g1, obstruct_governance).
```

This does not mean Python has learned the word "grievance." The LLM proposes
the record family, ids, and property predicates inside a strict JSON workspace.
Python only checks structural consistency: the predicates named in
`repeated_structures` must also appear in `candidate_predicates` with exact
arities before the draft profile is considered internally coherent.

## Modes

### 1. Unknown Domain Intake

When no profile matches, Prethinker can use a tiny generic palette for safe
capture:

```text
mentioned/2
claimed/3
candidate_entity/3
candidate_relation/4
needs_profile/2
```

This preserves useful material without pretending the system has domain
authority.

### 2. Profile Proposal

Given a bundle of representative text, the model proposes:

- domain name and scope;
- entity types;
- candidate predicates and argument roles;
- likely functional predicates;
- provenance-sensitive predicates;
- unsafe transformations;
- clarification patterns;
- starter test cases.

### 3. Profile Review

Humans or deterministic checks review the proposal:

- remove vague predicates;
- split overloaded predicates;
- add argument contracts;
- add validators for claim/finding, obligation/fact, condition/event, and
  source-priority boundaries;
- write a small frontier pack before allowing the profile in normal runs.

### 4. Profile Evolution

As frontier cases fail, the system should prefer profile evolution over generic
Python patching:

```text
failure trace
  -> was the predicate missing?
  -> was the contract underspecified?
  -> was the profile guidance too weak?
  -> was the mapper missing a generic structural check?
```

Only the last category belongs in generic Python. The others belong in profile
packages or test packs.

## Context Budget

This mode will need more context than ordinary per-turn intake. A good shape is:

- thin roster of existing profiles;
- small corpus sample or selected representative turns;
- current generic schema;
- profile-design instructions;
- examples of accepted/rejected profile predicates;
- maybe a compact KB or ontology manifest if one exists.

The ordinary 16K context window is enough for early experiments, but this mode
will need aggressive summarization once the corpus grows.

## Research Questions

- Can a strong model propose useful predicates without overfitting to one
  example?
- Can it distinguish domain facts, claims, rules, obligations, events, and
  provenance boundaries?
- Can it produce predicate contracts that the mapper can enforce structurally?
- Can profile proposals reduce future prompt bloat?
- Can this reduce Python-side domain patches?
- Can the system generate starter frontier cases that actually catch its own
  likely mistakes?

## Metrics

Early experiments should measure:

- percentage of proposed predicates accepted after review;
- number of overloaded predicates rejected or split;
- admission failures caused by missing predicate surface;
- reduction in out-of-palette candidate operations after profile update;
- reduction in profile-specific Python code;
- held-out scenario performance before and after the profile proposal.

## Near-Term Experiment

Build a small `domain_bootstrap` harness:

```text
input: 5-20 short texts from an unfamiliar domain
model: qwen/qwen3.6-35b-a3b or other candidate
output: profile_bootstrap_v1 JSON
review: compare against hand-authored starter profile
follow-up: run generated frontier cases through semantic_ir_v1
```

Good first targets:

- warehouse safety reports;
- academic advising notes;
- software incident postmortems;
- meeting commitments;
- procurement approvals.

The goal is not to automate ontology design on day one. The goal is to see
whether a strong model can draft a useful, reviewable domain surface faster than
we can invent one by hand.

## First Harness

A first executable harness now exists:

```powershell
python scripts/run_profile_bootstrap.py `
  --dataset datasets/profile_bootstrap/samples/contracts_compliance_seed_8.jsonl `
  --domain-hint contracts_compliance `
  --backend lmstudio `
  --model qwen/qwen3.6-35b-a3b
```

The runner sends a small representative corpus to the model and asks for strict
`profile_bootstrap_v1` JSON through LM Studio structured output. It writes local
research artifacts under ignored `tmp/profile_bootstrap/`.

The first seed corpus is intentionally contracts/compliance-shaped because that
domain stresses obligations, rights, exceptions, source priority, corrections,
approval events, and rule-versus-fact boundaries. The seed is small enough to
review by hand and large enough to expose profile-design failure modes.

The first measured tightening loop found a useful weakness: the model could
propose a good predicate palette, then write starter frontier cases using
unlisted predicates or different arities. The harness now scores:

- generic predicate count;
- unknown positive predicate references in starter cases;
- arity drift between candidate predicates and example calls;
- schema validity and rough coverage counts.

With the current guidance, a local `qwen/qwen3.6-35b-a3b` run produced:

```text
parsed_ok: true
rough_score: 1.000
candidate_predicates: 10
generic_predicate_count: 0
frontier_unknown_positive_predicate_count: 0
starter_frontier_cases: 8
```

Representative proposed predicates included:

- `obligation/3`
- `conditional_right/3`
- `prohibition/3`
- `override_rule/3`
- `submitted_by/2`
- `approved_by/2`
- `sent_on/2`
- `conflict_rule/3`
- `waiver/2`
- `validity_condition/2`

This is not an approved profile. It is review material. The remaining human
review question is semantic completeness: a structurally coherent profile can
still omit a direct relation from a starter case or choose a predicate surface
that should be split, renamed, or scoped differently.

That is the intended boundary. The model helps draft the vocabulary; review,
tests, and deterministic admission decide whether the vocabulary earns its way
into a real profile.

## Raw File Bootstrap Harness

For single-document experiments, use:

```powershell
python scripts/run_domain_bootstrap_file.py `
  --text-file tmp/declaration.md `
  --domain-hint founding_document `
  --backend lmstudio `
  --model qwen/qwen3.6-35b-a3b `
  --compile-source
```

This runner is deliberately strict about the "no Python NLP" boundary:

- Python reads the file bytes/text.
- If enabled, the LLM emits `intake_plan_v1` to describe source boundary,
  strategy, and focused follow-up passes.
- Python passes the raw source as one sample to `profile_bootstrap_v1`.
- The LLM proposes entity types, predicates, contracts, risks, and starter
  cases.
- If `--compile-source` is enabled, the same raw source is passed to
  `semantic_ir_v1` with that draft predicate surface.
- If `--compile-plan-passes` is enabled, Python iterates over the
  LLM-authored pass plan and asks Semantic IR to compile each focused pass.
- Python validates/admission-scores the output, but does not segment,
  summarize, classify, or derive predicates from the source language.

The first expected limitation is operation-cap pressure: a long document may
contain more safe facts than one Semantic IR response can carry. The right
repair is the current LLM-produced intake plan, not a Python sentence splitter
that makes semantic choices.

## Post-Ingestion QA Probes

Question batteries such as `tmp/proclamation-qa.md` belong after source
ingestion. They should not steer `profile_bootstrap_v1` or
`intake_plan_v1`; otherwise the test questions become hidden training context
for the compiler.

The post-ingestion shape is:

```text
raw source
  -> intake/profile/compile
  -> admitted facts/rules in local KB
  -> QA prompts
  -> semantic_ir_v1 query/probe workspace
  -> deterministic mapper
  -> Prolog query rows / proposed-write diagnostics
  -> optional oracle scoring
```

The runner is:

```powershell
python scripts\run_domain_bootstrap_qa.py `
  --run-json tmp\domain_bootstrap_file\<run>.json `
  --qa-file tmp\proclamation-qa.md `
  --model qwen/qwen3.6-35b-a3b
```

Without an answer key, this produces a diagnostic transcript: what queries the
model proposed, what the KB returned, and whether any QA prompt accidentally
looked like a write. If the markdown contains a section titled `Answers`, those
answers are copied into the diagnostic rows as human reference answers. They do
not feed ingestion and they are not treated as automatic pass/fail expectations.

The QA pass also gives the model the compiled KB surface:

- actual predicate signatures found in admitted facts/rules;
- representative clauses for those predicates;
- legal query templates with full arity;
- a `post_ingestion_qa_query_strategy_v1` block that says to use the compiled
  predicate surface, uppercase Prolog variables, source-attributed claim
  predicates, and primitive multi-hop query operations rather than invented
  composite predicates;
- source fact/rule counts.

That is context engineering, not Python NLP. Python is not deriving meaning
from the question text; it is telling the model which Prolog surface actually
exists so the model can ask useful KB queries.

There is one structural query-syntax repair in this path: generic slot labels
emitted by the model as query arguments, such as `label`, `candidate`,
`grievancelabel`, or `methoddetail`, are normalized to Prolog variables. This
does not inspect the user's question or source language; it prevents model
placeholder words from becoming lowercase Prolog constants that force
`no_results`.

With an oracle JSONL, the runner can score exact structural expectations.

An oracle row can be as small as:

```json
{"id":"q001","expected_decision":"answer","expected_query_predicates":["declares_recalled"],"expected_answer_contains":["batch_p_44"]}
```

This keeps the boundary clean:

- the proclamation source creates the KB;
- the QA file probes the KB;
- the answer key scores the probe;
- Python parses the markdown numbering and JSONL oracle, but does not derive
  semantic answers from the question text.

## First Closed Loop

A second runner now closes the loop:

```powershell
python scripts/run_profile_bootstrap_loop.py `
  --backend lmstudio `
  --model qwen/qwen3.6-35b-a3b
```

It loads the latest local `profile_bootstrap_v1` run, projects the proposed
candidate predicates into a temporary Semantic IR profile, runs the generated
starter frontier cases through the ordinary Semantic IR model+mapper path, and
scores the outcome.

This matters because profile proposal quality has two layers:

```text
profile draft looks coherent
  !=
profile draft actually guides ingestion safely
```

The first closed-loop pass found two useful problems:

- evaluation labels were accidentally visible to the model input, so the runner
  was made label-clean;
- the model often labeled normative record predicates as `operation='rule'`
  without an executable clause, so the mapper now treats a positive direct
  predicate+args `rule` operation with no clause as a fact-like rule record and
  records `rule_label_demoted_to_fact_record` in the rationale.

That mapper change is structural, not domain-language patching. Executable
rules still require a clause, negative/general rule operations still do not
become facts, and durable admission still checks palette and contracts.

The current best closed-loop contracts/compliance smoke produced:

```text
cases: 8
parsed_ok: 8
zero_out_of_palette_skip_cases: 8
zero_must_not_violation_cases: 8
expected_ref_hit_cases: 7
admitted_total: 16
loop_rough_score: 0.969
```

The remaining miss is a real profile-design ambiguity, not a JSON or mapper
failure: "No contractor may access production systems unless sponsored by a
manager" can be represented either as a prohibition with an exception or as a
conditional access right. The model chose the latter while the draft expected
the former. That is exactly the kind of profile-surface decision this loop is
meant to expose.

## Bottom Line

Domain bootstrapping is the meta-version of Prethinker:

```text
ordinary mode: language -> governed symbolic state
meta-mode: language samples -> governed symbolic vocabulary
```

Both modes keep the same thesis:

The model proposes. Admission governs.

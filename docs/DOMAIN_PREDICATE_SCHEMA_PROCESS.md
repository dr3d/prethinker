# Domain Predicate Schema Process

Status: working process note, June 1, 2026. This document explains how
Prethinker builds a domain predicate schema for one document family. It is a
process description, not a score claim.

## Purpose

The domain-tier path depends on a closed predicate pack: a small governed
language for one recurring document type. The model may map source meaning into
that language, but it should not freely invent the instrument language during a
claim-bearing compile.

This document records the process so a domain pack can be customized without
reintroducing the old failure modes:

- Python-side prose interpretation;
- source text hidden inside predicate or atom names;
- row-specific repair tricks;
- fixture vocabulary leaking into the instrument;
- high scores produced by judge-facing surface tokens instead of typed
  derivation.

The goal is not to make one perfect universal ontology. The goal is to make a
repeatable way to ask: for this document family, which typed facts can be
compiled reproducibly enough to earn Tier 1 trust?

## Required Inputs

A domain schema proposal should start with these materials:

- A bounded document family, for example FDA warning letters or consent orders.
- A small source sample set, ideally 3 to 8 documents that share anatomy but
  are not near-duplicates.
- A tiny micro-fixture that compresses the anatomy into a few paragraphs and
  tables without copying fixture-specific row language.
- A draft question inventory that describes user needs by answer class, not by
  exact oracle wording.
- Existing general carriers that may transfer, such as dates, parties, legal
  citations, obligations, findings, and dispositions.
- A place to record omissions, rejected carriers, and schema drift.

Do not derive the schema from answer keys alone. The schema should be drafted
from source anatomy and user tasks, then tested against QA later.

## Current File Shape

The current FDA warning-letter wedge uses this shape:

```text
datasets/domain_profiles/fda_warning_letter_v1/ontology_registry.json
datasets/compile_micro_fixtures/fda_warning_letter_domain_v1/source.md
datasets/compile_micro_fixtures/fda_warning_letter_domain_v1/expected_facts.pl
datasets/compile_micro_fixtures/fda_warning_letter_domain_v1/forbidden_facts.pl
src/carrier_contract_registry.py
docs/DOMAIN_TIER_WORKSHEET.md
```

The registry describes the domain vocabulary. The micro-fixture describes the
source pressure. Expected and forbidden facts make the contract concrete. The
carrier registry gives deterministic tooling one place to inspect signatures,
value domains, and contract guidance. The worksheet records experiments and
decisions.

## Lens-Scoped Predicate Offering

The offered predicate set is a function of both the domain and the semantic
lens:

```text
offered_predicates = f(domain_registry, lens)
```

A domain registry says what language exists at all for the document family. A
lens allowlist says which subset of that language a particular compile pass may
emit. This prevents a focused pass from reaching across the whole domain pack
and creating cross-lens leakage.

Example for FDA warning letters:

```text
wrapper lens:
  fda_warning_letter/5
  fda_facility_identity/5
  fda_correspondence_party/5
  domain_omission/5

violation lens:
  fda_violation/5
  fda_violation_citation/4
  fda_violation_detail/5
  domain_omission/5

response/obligation lens:
  fda_response_requirement/6
  fda_consultant_recommendation/4
  fda_violation_citation/4 only when scoping a consultant citation
  domain_omission/5

conclusion lens:
  fda_conclusion_scope/4
  domain_omission/5
```

The lens may focus attention and extraction. It may not invent predicates, and
it should not emit predicates outside its assigned registry subset. If a needed
fact does not fit the lens subset, the pass should leave it for the proper lens
or emit an accountable omission only when the omission contract applies.

Validate the registry-to-contract seam with:

```text
python scripts\validate_domain_predicate_schema.py --root datasets\domain_profiles
```

This checks that each domain registry uses registered carrier signatures, keeps
argument order aligned with the carrier contracts, and does not silently drift
into a local one-off predicate language.

## Build Loop

1. Pick the wedge.

Choose one document family, not a broad market. A useful wedge has repeated
document anatomy, recurring user questions, and substantive content that looks
typeable inside the domain.

2. Read source anatomy before designing predicates.

Inspect several documents for sections, repeated actor roles, event types,
authority citations, obligations, findings, deadlines, enumerations,
exceptions, and conclusion language. Record the repeated anatomy, not the most
interesting one-off passage.

3. Draft answer classes.

Group expected questions into classes such as:

- document metadata;
- party or facility identity;
- date and event metadata;
- legal authority;
- violation or deficiency;
- finding or reasoning;
- obligation or deadline;
- response requirement;
- conclusion or scope limitation;
- source provenance.

These classes guide predicate design. They are not themselves query regexes.

4. Draft carriers with stable roles.

Each carrier should name a repeated typed relation, not a sentence shape.

Good carrier pressure:

```text
fda_response_requirement(Letter, RequirementId, ActionType, DueDate, SourceId, Confidence)
```

Risky carrier pressure:

```text
fda_paragraph_about_response_deadline(...)
fda_detail_text(...)
fda_failure_to_do_exact_phrase_from_fixture(...)
```

Carrier arguments should have fixed roles, compact value domains where possible,
and explicit source-coordinate requirements.

5. Define allowed value domains.

For enum-like slots, declare compact allowed values before running broad
compiles. Examples:

```text
party_role: recipient, sender, facility_operator, consultant, unknown
requirement_type: written_response, corrective_action, meeting_request, unknown
scope_kind: conclusion_disclaimer, enforcement_reservation, ownership_change
```

Allowed values are not a license to hide prose. Unknown is better than
inventing a one-off phrase.

Define accountability requirements the same way. If a domain pack treats a
missing role, missing signature, absent table value, or explicitly unavailable
detail as meaningful coverage, record that requirement in the registry instead
of leaving it as prompt prose.

Example:

```json
{
  "id": "missing_signatory_role",
  "carrier_signature": "fda_correspondence_party/5",
  "omission_kind": "role_missing",
  "reason_code": "signatory_not_stated",
  "trigger": "source_explicitly_states_no_signatory_or_signature_block"
}
```

6. Build a micro-fixture.

The micro-fixture should pressure the domain anatomy without becoming a copy of
the future benchmark. It should include:

- enough source text to make the carriers meaningful;
- expected facts for the carriers that should fire;
- forbidden facts for tempting overreach;
- at least one omission/accountability case when the document explicitly lacks
  a common field.

Validate the fixture with:

```text
python scripts\validate_typed_micro_fixtures.py --root datasets\compile_micro_fixtures
python scripts\validate_domain_predicate_schema.py --root datasets\domain_profiles
```

7. Run a dry compile.

Compile the micro-fixture and measure:

- expected fact match;
- forbidden fact avoidance;
- carrier signature compliance;
- value-domain compliance;
- atom-shape cleanliness;
- omission/accountability behavior.

The first dry run is allowed to be bad. Its job is to show whether the schema is
under-specified, too broad, too prose-shaped, or missing a value domain.

8. Tighten the contract, not the row.

If a dry run fails, prefer changes that make the domain language clearer:

- add or clarify a carrier signature;
- add a value-domain enum;
- add source-coordinate requirements;
- add an omission rule;
- split an overloaded carrier;
- reject a prose-shaped slot.

Do not add a carrier because one row wants one answer. Do not add source phrases
to the predicate vocabulary.

9. Require omission/accountability.

When a carrier is common for the domain but absent or uncertain in the source,
the compile should emit a typed omission where the domain contract requires it.
Self-check prose is not enough.

Current audit:

```text
python scripts\audit_domain_omission_accountability.py --compile-json PATH --fixture FIXTURE_ID
```

10. Test reproducibility before promotion.

A domain carrier does not promote because it works once. The promotion bar is:

```text
N>=3 same-condition compiles
carrier rows survive with support>=2
no value-domain violations
no atom-shape blockers
no forbidden facts
redaction and typed-plan replay pass for returned answers
unlike document of the same type holds the same mechanism
```

If N=3 shows drift, record the drift. Do not average it into a claim.

## Customization Points

A customer or new domain implementer should be able to customize:

- document family;
- carrier names;
- carrier argument roles;
- value domains;
- required source coordinates;
- omission categories;
- Tier 1 query plans;
- Tier 2 fallback policy;
- Tier 3 retrieval policy;
- abstention rules.

They should not customize:

- whether prose-shaped atoms are allowed;
- whether answer keys can influence compile or query planning;
- whether a judge verdict alone can promote Tier 1;
- whether source-record display text can count as typed derivation;
- whether one successful run counts as reproducible.

Those are governance rules, not preferences.

## Guardrails

Use these checks as the domain pack matures:

```text
python scripts\audit_carrier_value_domains.py --compile-json PATH --fixture FIXTURE_ID
python scripts\audit_domain_omission_accountability.py --compile-json PATH --fixture FIXTURE_ID
python scripts\audit_kb_atom_inventory.py --compile-root PATH
python scripts\audit_typed_plan_replay.py --qa-json PATH --compile-root PATH
python scripts\audit_redaction_replay.py --qa-json PATH
python scripts\audit_reference_judge_null_controls.py --qa-json PATH
```

The exact command shape depends on the artifact being tested. The principle does
not: a Tier 1 answer must survive without prose retrieval, without oracle
leakage, and without prose-shaped typed atoms.

## What To Record

For each domain pack, keep a compact record of:

- source sample criteria;
- documents used for schema design;
- documents held out for unlike tests;
- carrier registry version;
- value-domain changes;
- micro-fixture expected and forbidden facts;
- dry-run failures and contract changes;
- N-cycle reproducibility results;
- hard-clean before/after table;
- omitted classes and why they were not covered;
- rejected carriers and rejection reasons.

This belongs in a worksheet while active, then a short stable domain note once
the pack either promotes or is rejected.

## Reject Conditions

Stop or redesign the domain pack if:

- substantive predicates cannot be made compact;
- carrier names or values start mirroring source prose;
- each row wants a new predicate;
- N>=3 compiles do not reproduce carrier coverage;
- Tier 1 gains require source-window or RAG support;
- omission/accountability stays in self-check prose instead of typed facts;
- unlike documents of the same type lose the mechanism.

A rejected domain pack is a useful result. It means the document family is not
yet reducible to the current governed language.

## Current FDA Lessons

The FDA warning-letter micro-fixture has already taught three process lessons:

- Value domains matter early. The first dry run emitted useful-looking rows
  with bad enum shapes; value-domain enforcement turned that into a visible
  blocker instead of letting it become a hidden score boost.
- Date-bearing wrapper facts need explicit mapper admission. Otherwise valid
  domain rows can be skipped by generic date gates.
- Omission/accountability must be a fact, not a note. The model can notice an
  absent signatory in `self_check`, but Tier 1 needs an emitted
  `domain_omission/5` row when the contract requires one.

That is the desired loop: dry run, find the governance gap, tighten the domain
contract, rerun, and only then test against real held-out documents.

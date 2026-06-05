# Domain Predicate Schema Process

Status: working process note, June 2, 2026. This document explains how
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
datasets/compile_micro_fixtures/fda_warning_letter_insanitary_001/source.md
datasets/compile_micro_fixtures/fda_warning_letter_insanitary_001/expected_facts.pl
datasets/compile_micro_fixtures/fda_warning_letter_insanitary_001/forbidden_facts.pl
src/carrier_contract_registry.py
docs/DOMAIN_PACK_RESEARCH_EVIDENCE.md
docs/CURRENT_COMPILE_FACT_QA_STATUS.md
docs/DOMAIN_PACK_STATUS.md
```

The registry describes the domain vocabulary. The micro-fixture describes the
source pressure. Expected and forbidden facts make the contract concrete. The
carrier registry gives deterministic tooling one place to inspect signatures,
value domains, and contract guidance. Current public summaries live in
`docs/DOMAIN_PACK_RESEARCH_EVIDENCE.md`,
`docs/CURRENT_COMPILE_FACT_QA_STATUS.md`, and generated status pages. Long run
diaries belong in `C:\prethinker_tmp_archive`, not the public docs tree.

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
into a local one-off predicate language. It also validates lens allowlists:
every `lenses[].allowed_signatures[]` entry must already exist in the domain
registry, so a lens cannot acquire predicates that the domain did not offer.

Use a lens-scoped registry in the compile runner with:

```text
python scripts\run_domain_bootstrap_file.py ... --profile-registry datasets\domain_profiles\fda_warning_letter_v1\ontology_registry.json --profile-registry-lens wrapper
```

When `--profile-registry-lens` is set, the runner filters the registry before
profile generation, palette-prior context, registry accountability context, and
registry completion follow-up. This is the executable boundary: a focused lens
does not merely promise to avoid unrelated predicates; those predicates are not
offered to that pass.

The batch wrapper forwards the same flag:

```text
python scripts\run_domain_bootstrap_file_batch.py ... --profile-registry datasets\domain_profiles\fda_warning_letter_v1\ontology_registry.json --profile-registry-lens violation
```

The post-backbone support and rule acquisition passes also accept
`--profile-registry-lens` so an overlay/lens pass can be given a narrowed
domain vocabulary without reopening the whole domain pack.

`domain_omission/5` is special. A lens may declare it as possible shared
vocabulary, but the runner only offers it when that active lens has at least
one retained accountability requirement. Otherwise omission rows become a
decorative escape hatch, which is exactly the thing the domain tier is trying
to avoid.

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

Before adding a new carrier to the central registry or a domain profile, write
it as a proposal and validate the proposal shape:

```text
python scripts\validate_domain_predicate_proposals.py --print-template
python scripts\validate_domain_predicate_proposals.py --proposal PATH_TO_PROPOSAL.json
python scripts\validate_domain_predicate_proposals.py --out-md docs\DOMAIN_PREDICATE_PROPOSAL_STATUS.md --out-json tmp\domain_predicate_proposal_status.json --expect-md docs\DOMAIN_PREDICATE_PROPOSAL_STATUS.md
```

The proposal validator is intentionally stricter than ordinary brainstorming.
It blocks missing lens ownership, missing anti-leak guards, prose-shaped slot
names, weak N/support transfer plans, missing forbidden examples, and promoted
signatures that are not actually registered and lens-allowed. A candidate may
be unregistered while it is still a draft, but it cannot be promoted until the
central carrier registry, domain registry, and lens allowlist all agree.

After a proposal validates, retained compile artifacts can be checked without
changing the fixture oracle:

```text
python scripts\summarize_domain_predicate_proposal_evidence.py --compile-root PATH_TO_RETAINED_BUNDLE --apply-domain-reducers --out-md tmp\proposal_evidence.md --out-json tmp\proposal_evidence.json
```

This evidence report is deliberately not a score. `candidate_signal_no_oracle`
means repeated typed facts exist in retained compiles, but the fixture oracle
did not predeclare them; those rows require independent review before any
claim-bearing promotion.

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

For N-cycle transfer or micro-series summaries, use the expected/forbidden
gate together:

```text
python scripts\summarize_typed_micro_series.py --fixture FIXTURE_ID --support-threshold 2 --matcher constant_slot --enforce-supported --enforce-no-forbidden --compile-json RUN1 --compile-json RUN2 --compile-json RUN3
```

For a domain transfer cell, prefer the bundled gate:

```text
python scripts\run_domain_transfer_gate.py --fixture FIXTURE_ID --compile-root COMPILE_ROOT --compile-json RUN1 --compile-json RUN2 --compile-json RUN3
```

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

9. Adjudicate oracles blind to model output.

Domain work can expose wrong or under-specified expected facts. Correcting an
oracle is allowed, but it is also a measurement risk: the easiest new cheat is
letting the test bend toward the model's miss.

The adjudication rule is:

- decide from the source and carrier contract alone;
- record the source/contract rationale in the fixture notes or worksheet;
- name whether the change is a schema correction, value-domain correction,
  source-faithfulness correction, or fixture-authoring error;
- add a forbidden fact when the old or tempting value represents a real leak;
- never count a changed oracle retroactively as a win;
- rerun a fresh same-condition cell before the changed row becomes
  claim-bearing.

The reviewer test: a reviewer who has not seen the model output should be able
to defend the oracle change from the source and registered domain contract. If
the correction only makes sense because the model emitted that value, leave it
as a miss and treat it as a compile or schema blocker.

For promoted validation cells, keep oracle authorship independent from schema
closure. The person who closed or materially edited the domain predicate pack
should not be the only person authoring the validation oracle for that same
pack. In assisted onboarding this separation can come from customer expert vs.
Prethinker operator roles. In self-serve onboarding it must be explicit:
schema closer and validation-oracle author are separate roles, or a blind
reviewer must approve the oracle before the result becomes claim-bearing.

Returned source-only expected/forbidden oracle packets are retained separately
from candidate-row review packets. Import them through the source-oracle lane:

```text
python scripts\import_source_oracle_review.py --zip PATH_TO_RETURNED_ZIP --proposal datasets\domain_predicate_proposals\PROPOSAL.json --review-id REVIEW_ID
python scripts\audit_source_oracle_reviews.py --out-json tmp\source_oracle_reviews.json --out-md docs\SOURCE_ORACLE_REVIEW_STATUS.md --expect-md docs\SOURCE_ORACLE_REVIEW_STATUS.md
```

The importer keeps only `manifest.json`, per-fixture `expected_facts.pl`,
per-fixture `forbidden_facts.pl`, and optional review notes. It drops source
files, templates, and work-order scaffolding. It also refuses returned
manifests that explicitly declare model-output exposure or non-source-only
review. Once retained, the proposal validator requires the proposal to link the
source-oracle review under `source_oracle_review_results`; otherwise the
proposal and retained oracle evidence have drifted apart.

10. Require omission/accountability.

When a carrier is common for the domain but absent or uncertain in the source,
the compile should emit a typed omission where the domain contract requires it.
Self-check prose is not enough.

Current audit:

```text
python scripts\audit_domain_omission_accountability.py --compile-json PATH --fixture FIXTURE_ID
```

Current static coverage report:

```text
python scripts\summarize_domain_accountability_status.py --out-md docs\DOMAIN_ACCOUNTABILITY_STATUS.md --out-json tmp\domain_accountability_status_current.json --expect-md docs\DOMAIN_ACCOUNTABILITY_STATUS.md
```

The static report reads only registries and typed fixture oracles. It should
surface fixture-only omission patterns before they become hidden conventions.

11. Test reproducibility before promotion.

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

Value domains are configurable, but their compactness is not optional. A
customer may propose any enum or value family that fits the domain, but it only
promotes if it survives the same gates as carrier predicates:

- N>=3 same-condition support with support>=2;
- no atom-shape blockers;
- no prose-shaped values;
- no row-specific value proliferation;
- unlike-document transfer inside the same document family.

A near-open enum is just open vocabulary with a friendlier label. If a value
domain cannot stay compact and reproducible, the pack should abstain for that
class or move the class to a lower, explicitly untrusted product tier. It should
not relax the gate.

## Customer Domain Onboarding

The same process can become a customer-facing onboarding workflow, but it
should be framed as governed domain-pack construction, not automatic schema
invention.

Prethinker can help a customer sort a document corpus into recurring document
families, propose candidate predicate families from representative samples,
and run falsifiability gates over draft packs. The model's proposals are
design material. They do not become trusted instrument language until a human
domain expert and the governance gates close the schema.

Recommended customer flow:

1. Cluster or manually separate unrelated document families before schema
   work begins. Contracts, inspection reports, warning letters, claims files,
   correspondence, and policy manuals should not be forced into one predicate
   pack merely because they belong to the same customer.
2. Use existing discovery mechanisms to propose candidate carriers, lenses,
   value domains, omissions, and answer classes from a small representative
   sample.
3. Reduce those proposals into a closed registry: predicate names, arities,
   argument roles, value domains, lens allowlists, forbidden uses, and
   abstention/omission rules.
4. Validate on same-condition N>=3 compiles and unlike documents from the same
   family. Promotion requires support>=2, clean gates, and no forbidden facts.
5. Treat the resulting artifact as a customer/domain pack: a governed evidence
   compiler for that document family, not a model-weight fine-tune and not a
   claim that arbitrary documents are solved.

Early commercial shape should probably be assisted or done-for-you onboarding:
Prethinker operators build domain packs with customer experts, then measure
how much of schema closure can be handed to non-Prethinker specialists. Fully
self-serve schema induction is a later hypothesis. The risk is the old
open-vocabulary drift returning under a product label; the safeguard is the
same one used in research: LLM proposes, human and gates close, deterministic
checks decide what can be trusted.

Mechanize that handoff instead of treating it as a feeling. In early customer
work, ask the customer or domain expert to close the draft schema first:
approve carriers, reject prose-shaped values, choose compact value domains,
name omissions, and set abstention boundaries. Then have a Prethinker operator
review the result and log every rescue:

- carrier rewritten;
- value domain narrowed;
- lens allowlist changed;
- omission rule added;
- atom-shape or prose leak caught;
- oracle or expected fact corrected;
- abstention boundary changed;
- gate failure interpreted.

The rescue log is the self-serve roadmap. If rescues shrink over engagements,
the workbench can move toward customer-led schema closure. If rescues remain
heavy, the product is still a high-value assisted domain-pack buildout rather
than a fully self-serve schema-induction platform.

Self-serve validation also needs role separation. A customer expert may close
the schema, and another customer reviewer may author or approve the validation
oracle, but the same unchecked person should not both shape the predicate pack
and define the claim-bearing target. Otherwise the workflow can fit the test
to the schema while all mechanical gates still pass.

This implies a useful product distinction:

- **Domain pack buildout:** a service/workbench process that turns one
  repeated document family into a closed, audited predicate domain.
- **Evidence workstation:** the runtime experience that compiles new documents
  against that pack, answers within trusted tiers, and abstains when the typed
  evidence is not there.

If a customer domain cannot close without proliferating row-specific
predicates, prose-shaped atoms, or unstable N-cycle coverage, that is a valid
negative onboarding result rather than a failure to be hidden.

## Pack Maintenance And Drift

A domain pack is not finished forever when it passes its first transfer gate.
Document families drift: agencies revise templates, citation styles change,
forms are reorganized, customer workflows mutate, and recurring roles or
obligations acquire new surface shapes. A silently degrading pack is an audit
failure even if the original buildout was clean.

Treat the hard-clean gate as a maintenance monitor:

1. Sample new production documents on a cadence appropriate to the domain.
2. Compile them against the current closed pack without expanding the
   vocabulary.
3. Run the same governance gates used for promotion: registered signatures,
   lens scope, value domains, atom shape, forbidden facts, typed-plan replay,
   redaction replay, and judge null controls where QA exists.
4. Track coverage by answer class and carrier family, not only aggregate score.
5. When coverage drops or omissions cluster, classify the event as document
   family drift, source-distribution drift, schema gap, or fixture/oracle gap.
6. Re-close the pack only through the normal domain process: propose, reduce,
   gate, N>=3, unlike transfer.

Maintenance is not a loophole for one-off fixes. A new customer document should
not cause a private predicate or permissive value to be added because one row is
important. If the family has genuinely moved, the pack gets a new version and
the before/after hard-clean table records what changed.

Recommended maintenance record:

- pack version and active registry hash;
- documents sampled;
- gate results by answer class;
- coverage changes since the last maintenance run;
- new omissions or repeated abstentions;
- proposed schema changes and their rejection/promotion status;
- whether the pack remains trusted for Tier 1 on that document family.

## Guardrails

Use these checks as the domain pack matures:

```text
python scripts\audit_carrier_value_domains.py --compile-json PATH --fixture FIXTURE_ID
python scripts\audit_domain_omission_accountability.py --compile-json PATH --fixture FIXTURE_ID
python scripts\audit_kb_atom_inventory.py --compile-root PATH --enforce-atom-shape --enforce-registered-signatures --enforce-lens-scope
python scripts\summarize_typed_micro_series.py --fixture FIXTURE_ID --support-threshold 2 --matcher constant_slot --enforce-supported --enforce-no-forbidden --compile-json RUN1 --compile-json RUN2 --compile-json RUN3
python scripts\audit_typed_plan_replay.py --qa-json PATH --compile-root PATH
python scripts\audit_redaction_replay.py --qa-json PATH
python scripts\audit_reference_judge_null_controls.py PATH
python scripts\run_domain_transfer_gate.py --fixture FIXTURE_ID --compile-root COMPILE_ROOT --compile-json RUN1 --compile-json RUN2 --compile-json RUN3
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
- schema-closer and validation-oracle author/reviewer roles;
- maintenance cadence and drift-monitor results;
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

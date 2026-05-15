# Lens Vocabulary Audit Worksheet

This worksheet audits whether Prethinker's lens terms behave like transferable
structural projections or like frozen development-corpus vocabulary.

The operating question for each term is:

> Does this vocabulary term fire on unlike documents that have the structural
> pattern, and does it preserve the slots needed by that term?

This is the helper-residue audit pattern applied one layer up. A term is not
validated merely because it appears in a predicate name. It earns its slot when
unlike documents compile the same structural relation with the needed argument
roles.

## Operating Protocol

For a settled lens vocabulary:

1. Name the vocabulary and its terms before seeing probe results.
2. Build small unlike documents that contain the structural patterns.
3. Compile with the current instrument.
4. Audit term firing as:
   - `structural`: direct facts preserve the term's required slots,
   - `shallow_structural`: direct facts name the term family but omit required slots,
   - `source_only`: term appears in source-record text only,
   - `not_applicable`: term family was absent from the source.
5. Run focused QA where useful to test slot completeness.
6. Classify each term as:
   - `structural`: fires and preserves needed slots,
   - `shallow_structural`: fires but loses required slots,
   - `source_only`: visible in source ledger but not direct rows,
   - `not_applicable`: not tested by this probe,
   - `fixture_shape`: only fires on internal/development examples.

## LV-001 - Evidence Provenance Vocabulary Transfer

Date: 2026-05-15

Lens:

`evidence_provenance`

Vocabulary under audit:

- `prepared`
- `presented`
- `dated`
- `admitted`
- `relied_on`
- `commissioned`
- `corrected`
- `located`

Before:

The semantic lens roster defines evidence provenance as the surface for who
prepared, presented, dated, admitted, relied on, commissioned, corrected, or
physically located a source artifact. That vocabulary was discovered mostly in
legal, archive, hearing, museum, and source-audit fixtures. The risk is that
terms such as `commissioned`, `relied_on`, and `admitted` might be legalistic
labels rather than transferable structural roles.

Prediction:

If the vocabulary is structural, ordinary unlike documents should trigger these
terms without legal/archive framing:

- a community lab notice with preparation, presentation, reliance, correction,
  and location;
- a craft fair review with request/commission, writing/date, admission into a
  packet, reliance, and storage;
- a garden water log with commissioning, preparation/date, submission,
  admission, reliance, amendment, and location.

Intervention:

Added a reusable compile-artifact audit:

- `scripts/audit_lens_vocabulary_transfer.py`
- `tests/test_lens_vocabulary_transfer.py`

Added three unlike probe fixtures:

- `experiments/lens_vocabulary_audits/evidence_provenance_v1/community_lab_notice`
- `experiments/lens_vocabulary_audits/evidence_provenance_v1/craft_fair_review`
- `experiments/lens_vocabulary_audits/evidence_provenance_v1/garden_water_log`

Compiled all three locally with source-record ledger facts enabled, then audited
direct fact tokens against the predeclared vocabulary. Ran QA with helper rows
disabled.

Artifacts:

- `docs/data/lens_vocabulary_audit/evidence_provenance_v1_transfer_audit_20260515.json`
- `docs/data/lens_vocabulary_audit/evidence_provenance_v1_transfer_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/evidence_provenance_v1_qa_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/evidence_provenance_v1_qa_summary_20260515.md`
- `tmp/lens_vocab_evidence_provenance_compile_20260515`
- `tmp/lens_vocab_evidence_provenance_qa_20260515`

After:

Vocabulary transfer audit:

- compiles=`3`
- status counts: `structural=16`, `source_only=2`, `not_applicable=6`

Term readout:

| Term | Structural | Source-only | N/A | Reading |
| --- | ---: | ---: | ---: | --- |
| `admitted` | 2 | 0 | 1 | Transfers in ordinary packet/log sources. |
| `commissioned` | 2 | 0 | 1 | Transfers outside legal/hearing prose via `requested` and `commissioned_test`. |
| `corrected` | 2 | 0 | 1 | Transfers through correction/amendment rows. |
| `dated` | 1 | 0 | 2 | Fires when date is explicitly attached as a provenance/date row. |
| `located` | 3 | 0 | 0 | Strong transfer via `located_in`, `stored_in`, and `held_in`. |
| `prepared` | 1 | 2 | 0 | Weakest term; two compiles used adjacent creation/tester surfaces instead. |
| `presented` | 2 | 0 | 1 | Fires, but one case exposed shallow slot coverage. |
| `relied_on` | 3 | 0 | 0 | Strong transfer across all three probes. |

QA:

| Probe | Questions | Exact | Partial | Miss | Helper rows | Reading |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `community_lab_notice` | 5 | 4 | 0 | 1 | 0 | Presenter slot was not preserved. |
| `craft_fair_review` | 6 | 5 | 0 | 1 | 0 | Storage attached to packet, not note. |
| `garden_water_log` | 7 | 7 | 0 | 0 | 0 | Full vocabulary transfer. |
| Total | 18 | 16 | 0 | 2 | 0 | 88.9% exact, zero helpers. |

Verification:

- `python -m py_compile scripts\audit_lens_vocabulary_transfer.py`
- `python -m pytest tests\test_lens_vocabulary_transfer.py -q` -> `2 passed`

Lesson:

The evidence provenance vocabulary mostly transfers, but the audit exposed a
more important distinction than "term fired" versus "term did not fire."
`presented` fired structurally in the community-lab compile, but as
`presented_to(summary, maintenance_circle)`, losing the presenter. That is
`shallow_structural`: a lens term appears, but the argument roles needed by the
term are incomplete.

`prepared` is also weak: it remained source-only in two of three probes because
the compile chose adjacent predicates such as `created_by`, tester roles, or
commissioning rows. Those may answer some questions, but they do not prove the
`prepared` lens term itself is stable.

The next audit level should therefore test **slot contracts**, not only term
tokens. For evidence provenance, actor/artifact/date/context/source roles need
explicit operational criteria.

Next pressure:

Add a slot-contract audit for evidence provenance terms. Start with
`prepared`, `presented`, `commissioned`, `relied_on`, `corrected`, and
`located`; each should define the minimum direct-row slots that make the term
structural rather than shallow.

## LV-002 - Evidence Provenance Slot Contracts

Date: 2026-05-15

Before:

LV-001 exposed the central risk in vocabulary audits: a term can appear in a
direct predicate without preserving the roles needed by the lens. In the
community-lab probe, `presented` appeared through `presented_to/2`, but the
presenter was missing. That is not fixture-shape leakage, but it is still a
resolution failure.

Prediction:

If the audit distinguishes token presence from role completeness, the evidence
provenance readout should become sharper:

- terms with enough slots remain `structural`;
- terms with a direct term token but too few slots become
  `shallow_structural`;
- terms visible only in source-record text remain `source_only`.

Intervention:

Extended `scripts/audit_lens_vocabulary_transfer.py` with minimum slot
contracts per term. The first pass is deliberately simple: it requires direct
rows for each term to meet a minimum arity before receiving `structural`
credit. Evidence-provenance terms now have these initial minima:

| Term | Minimum direct slots | Rationale |
| --- | ---: | --- |
| `prepared` | 2 | artifact + actor/source |
| `presented` | 3 | artifact + presenter + recipient/context |
| `dated` | 2 | artifact + date |
| `admitted` | 2 | artifact + record/context |
| `relied_on` | 2 | relying actor/body + evidence |
| `commissioned` | 3 | commissioning actor + commissioned actor/body + artifact/task |
| `corrected` | 2 | artifact/detail + correcting actor or correction value |
| `located` | 2 | artifact + location |

Added a regression test proving `presented_to(summary_a, circle).` is
`shallow_structural`, not structural.

Artifacts:

- `scripts/audit_lens_vocabulary_transfer.py`
- `tests/test_lens_vocabulary_transfer.py`
- `docs/data/lens_vocabulary_audit/evidence_provenance_v1_slot_contract_audit_20260515.json`
- `docs/data/lens_vocabulary_audit/evidence_provenance_v1_slot_contract_audit_20260515.md`

After:

Slot-contract audit over the same three compiles:

- compiles=`3`
- `structural=14`
- `shallow_structural=2`
- `source_only=2`
- `not_applicable=6`

Term readout:

| Term | Structural | Shallow | Source-only | N/A | Reading |
| --- | ---: | ---: | ---: | ---: | --- |
| `admitted` | 2 | 0 | 0 | 1 | Stable where present. |
| `commissioned` | 2 | 0 | 0 | 1 | Stable outside legal prose. |
| `corrected` | 2 | 0 | 0 | 1 | Stable through correction/amendment rows. |
| `dated` | 1 | 0 | 0 | 2 | Stable where explicit. |
| `located` | 3 | 0 | 0 | 0 | Strong transfer. |
| `prepared` | 1 | 0 | 2 | 0 | Weak; often source-only or expressed as adjacent creation/tester rows. |
| `presented` | 0 | 2 | 0 | 1 | Fires shallowly; presenter/context slot contract not yet stable. |
| `relied_on` | 3 | 0 | 0 | 0 | Strong transfer. |

Verification:

- `python -m py_compile scripts\audit_lens_vocabulary_transfer.py`
- `python -m pytest tests\test_lens_vocabulary_transfer.py -q` -> `3 passed`

Lesson:

This is the right audit granularity. A lens vocabulary term is not proven by
token transfer. It must carry the structural slots that make it answer-bearing.
`presented` is currently a real lens word but a weak slot contract: the compiler
often preserves the artifact and recipient/context while dropping the
presenting actor. `prepared` is a vocabulary-normalization issue: the structure
is often present as `created_by`, `commissioned_test`, or role rows, but not as
the `prepared` family.

Next pressure:

Decide whether to normalize equivalent creation/preparation predicates under
the evidence-provenance lens, or simply document `prepared` as a broader
artifact-creation slot family. For `presented`, the stronger next move is
compile guidance: when a source states that someone presented/submitted/filed a
document to a body, preserve presenter, artifact, recipient/body, and date or
context when stated.

## LV-003 - Evidence Provenance Predicate Contracts

Date: 2026-05-15

Before:

LV-002 proved that token matching was too weak in two directions. It missed
generic equivalent surfaces such as `created_by/3` for preparation, and it
accepted shallow predicates such as `presented_to/2` as if they carried a full
presentation relation. The compiler guidance also named provenance roles but
did not spell out the slot contract.

Prediction:

If evidence provenance is a structural lens rather than a vocabulary list, then
equivalent predicates should satisfy a term only when they preserve the needed
roles. A `created_by(Artifact, Actor, Date)` row should count for preparation;
a `presented_to(Artifact, Body)` row should remain shallow because it drops the
presenting actor or event context.

Intervention:

- Added an explicit evidence provenance slot contract to source-authority
  guidance and the global compile-surface invariants.
- Extended the lens audit so each term can recognize generic predicate
  contracts in addition to literal term tokens.
- Kept slot arity as the gate: `presented_to/2` and `submitted_to/2` remain
  shallow; `read_aloud/3` counts as a presentation surface because it preserves
  actor, artifact, and context.
- Added focused tests for equivalent preparation predicates and shallow versus
  structural presentation rows.

After:

Artifact:

- `docs/data/lens_vocabulary_audit/evidence_provenance_v1_predicate_contract_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/evidence_provenance_v1_predicate_contract_audit_20260515.json`

Slot-contract audit:

- `structural=16`
- `shallow_structural=2`
- `source_only=1`
- `not_applicable=5`

Delta from LV-002:

- `prepared`: `1 structural / 2 source-only` -> `2 structural / 1 source-only`
- `presented`: `0 structural / 2 shallow / 1 N/A` -> `1 structural / 2 shallow / 0 N/A`

Term readout:

| Term | Structural | Shallow | Source-only | N/A | Reading |
| --- | ---: | ---: | ---: | ---: | --- |
| `admitted` | 2 | 0 | 0 | 1 | Stable where present. |
| `commissioned` | 2 | 0 | 0 | 1 | Stable outside legal prose. |
| `corrected` | 2 | 0 | 0 | 1 | Stable through correction/amendment rows. |
| `dated` | 1 | 0 | 0 | 2 | Stable where explicit date predicates exist. |
| `located` | 3 | 0 | 0 | 0 | Strong transfer. |
| `prepared` | 2 | 0 | 1 | 0 | Improved by accepting artifact-creation predicates with actor slots. |
| `presented` | 1 | 2 | 0 | 0 | One structural equivalent found; two recipient-only rows remain shallow. |
| `relied_on` | 3 | 0 | 0 | 0 | Strong transfer. |

Verification:

- `python -m py_compile scripts\audit_lens_vocabulary_transfer.py scripts\run_domain_bootstrap_file.py`
- `python -m pytest tests\test_lens_vocabulary_transfer.py tests\test_domain_bootstrap_file.py -q` -> `32 passed`

Lesson:

Slot contracts are the right defense against fixture-shaped vocabulary at the
lens layer. A term can transfer through a different predicate name, but only if
the predicate carries the same structural roles. This prevents the audit from
overfitting to internal predicate spelling while also refusing shallow rows that
sound right but cannot answer provenance questions.

Next pressure:

Run the same contract-style audit on another settled lens vocabulary. The best
next candidate is source authority/custody or rule composition, because those
vocabularies are likely to contain official-document terms that may look
generic while depending on development-corpus surface conventions.

## LV-004 - Rule Composition Slot Contracts

Date: 2026-05-15

Before:

Evidence provenance proved the slot-contract audit pattern on mostly flat
2-3 slot relations. Rule composition is harder: the vocabulary is inherently
relational, and many terms are only useful when they preserve partners and
scope, not just a rule label. The terms under audit were named before the
probe run:

- `base_rule`
- `exception`
- `threshold`
- `activation_condition`
- `eligibility_condition`
- `override`
- `precedence`
- `expiration`
- `vote_requirement`
- `fallback_rule`

Prediction:

The audit should find more shallow structural cases than evidence provenance.
Likely weak forms include exception rows without effect, override rows without
scope or overridden partner, precedence levels without compared rules, quorum
rows not anchored to a vote requirement, and fallback actions not joined to the
trigger.

Intervention:

- Added `rule_composition` to `scripts/audit_lens_vocabulary_transfer.py`.
- Extended the audit grammar with shared-anchor contract groups so a term can
  be structural across multiple rows when the rows share a rule/condition
  anchor.
- Added tests for complete and partial exception contracts and split threshold
  contracts.
- Added three unlike rule-composition probes:
  - `experiments/lens_vocabulary_audits/rule_composition_v1/makerspace_tool_access`
  - `experiments/lens_vocabulary_audits/rule_composition_v1/garden_plot_governance`
  - `experiments/lens_vocabulary_audits/rule_composition_v1/library_room_booking`
- Compiled the probes with OpenRouter, source-record ledger facts enabled, and
  no legacy helper adapters.
- Added rule-composition slot-contract guidance to rule-ingestion context and
  global compile-surface invariants.

Artifacts:

- `docs/data/lens_vocabulary_audit/rule_composition_v1_slot_contract_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_slot_contract_audit_20260515.json`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_qa_summary_20260515.json`
- `tmp/lens_vocab_rule_composition_compile_20260515`
- `tmp/lens_vocab_rule_composition_qa_20260515`

After:

Compile batch:

- compiles=`3`
- parsed_ok=`3`
- admitted/skipped=`74 / 6`

Slot-contract audit:

- `structural=12`
- `shallow_structural=9`
- `source_only=5`
- `not_applicable=4`

Term readout:

| Term | Structural | Shallow | Source-only | N/A | Reading |
| --- | ---: | ---: | ---: | ---: | --- |
| `activation_condition` | 0 | 0 | 3 | 0 | Dominant source-only gap; activation phrases stayed in ledger text. |
| `base_rule` | 2 | 1 | 0 | 0 | Usually stable, but one probe emitted adjacent rule rows rather than a base-rule contract. |
| `eligibility_condition` | 1 | 2 | 0 | 0 | Often condition-like but not anchored with all required slots. |
| `exception` | 2 | 1 | 0 | 0 | Transfers, with one shallow exception surface. |
| `expiration` | 2 | 0 | 0 | 1 | Stable where present. |
| `fallback_rule` | 2 | 1 | 0 | 0 | Split trigger/action can be shallow when not joined by an anchor. |
| `override` | 1 | 1 | 1 | 0 | Still weak; scope/partner retention varies. |
| `precedence` | 1 | 2 | 0 | 0 | Often emitted as rank/level instead of pairwise rule order. |
| `threshold` | 1 | 0 | 1 | 1 | Weak in the garden probe; threshold phrase stayed source-only. |
| `vote_requirement` | 0 | 1 | 0 | 2 | Vote rows need scoped quorum/presence contracts. |

QA over the same probes:

- questions=`25`
- exact/partial/miss=`24 / 1 / 0`
- helper rows=`0`

Reading:

The user-facing QA is already strong on the simple probes, but the lens audit
shows why this layer still needs contract work. Rule composition can answer
many questions from thin surfaces, yet those thin surfaces are not robust
architecture: `activation_condition` remained entirely source-only, and
`precedence`, `override`, `vote_requirement`, and `fallback_rule` frequently
lost partner/scope joins. This is exactly the case where exact answers can hide
weak extraction.

Verification:

- `python -m py_compile scripts\audit_lens_vocabulary_transfer.py scripts\run_domain_bootstrap_file.py`
- `python -m pytest tests\test_lens_vocabulary_transfer.py tests\test_domain_bootstrap_file.py -q` -> `36 passed`
- `python -m pytest tests\test_lens_vocabulary_transfer.py tests\test_domain_bootstrap_qa.py tests\test_domain_bootstrap_file.py tests\test_compile_surface_invariants.py -q` -> `210 passed`

Guidance replay:

After adding the slot-contract guidance, the same three probes were recompiled
and audited.

Replay artifacts:

- `docs/data/lens_vocabulary_audit/rule_composition_v1_guidance_replay_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_guidance_replay_audit_20260515.json`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_guidance_replay_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_guidance_replay_qa_summary_20260515.json`
- `tmp/lens_vocab_rule_composition_guidance_replay_compile_20260515`
- `tmp/lens_vocab_rule_composition_guidance_replay_qa_20260515`

Replay compile:

- compiles=`3`
- parsed_ok=`3`
- admitted/skipped=`73 / 4`

Replay slot-contract audit:

- `structural=12`
- `shallow_structural=10`
- `source_only=4`
- `not_applicable=4`

Replay deltas:

- `exception`: `2 structural / 1 shallow` -> `3 structural / 0 shallow`
- `vote_requirement`: `0 structural / 1 shallow / 2 N/A` -> `1 structural / 0 shallow / 2 N/A`
- `activation_condition`: `3 source-only` -> `1 shallow / 2 source-only`
- `override`: `1 structural / 1 shallow / 1 source-only` -> `0 structural / 3 shallow`
- `fallback_rule`: `2 structural / 1 shallow` -> `2 structural / 1 source-only`

Replay QA:

- questions=`25`
- exact/partial/miss=`23 / 1 / 1`
- helper rows=`0`

Replay reading:

The guidance helped the most concrete relational contracts but did not simply
lift the whole lens. `exception` and `vote_requirement` improved. Activation
conditions began to move out of source-only, but remained weak. Override and
precedence stayed resolution-sensitive: the compiler often knows there is a
priority relation but still emits rank/priority or two-slot override rows that
do not carry all partner/scope slots. QA stayed high but slightly less stable
on the replay, with the makerspace activation question becoming a
compile-surface miss. That makes activation-condition anchoring the cleanest
next repair target.

Activation-anchor repair:

A focused repair added an activation-condition anchoring rule to rule-ingestion
guidance and the global compile-surface invariants. Then the makerspace probe,
the coordinate that had regressed on activation QA, was replayed alone.

Activation-anchor artifacts:

- `docs/data/lens_vocabulary_audit/rule_composition_v1_activation_anchor_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_activation_anchor_audit_20260515.json`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_activation_anchor_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_activation_anchor_qa_summary_20260515.json`
- `tmp/lens_vocab_rule_composition_activation_anchor_compile_20260515`
- `tmp/lens_vocab_rule_composition_activation_anchor_qa_20260515`

Activation-anchor replay:

- compile parsed_ok=`1/1`
- admitted/skipped=`37 / 0`
- audit over makerspace: `3 structural / 4 shallow / 0 source-only / 3 N/A`
- `activation_condition`: `source-only` -> `structural`
- QA: `7 exact / 0 partial / 0 miss`
- helper rows=`0`

The successful surface used `rule_condition/2` and `rule_action/2` rows sharing
the same rule anchor. The audit grammar was extended to count that generic
condition/action pair as a structural activation contract. That is not a
fixture-specific synonym: it is the minimum transferable shape for "this rule
activates under this condition and has this governed action."

Pairwise relation follow-on:

The next narrow repair added a pairwise rule-relation contract to rule-ingestion
guidance and the global compile-surface invariants. It also taught the audit
that `rule_precedence(HigherRule, LowerRule, ConflictOrScope)` can satisfy the
`override` term when the source says one rule overrides or controls another.
Two-arity `rule_precedence/2`, `precedence_level/2`, and rank-only rows remain
shallow.

Pairwise artifacts:

- `docs/data/lens_vocabulary_audit/rule_composition_v1_pairwise_relation_reaudit_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_pairwise_relation_reaudit_20260515.json`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_activation_pairwise_reaudit_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_activation_pairwise_reaudit_20260515.json`

Pairwise replay readout over the three-fixture guidance replay:

- `structural=13`
- `shallow_structural=9`
- `source_only=4`
- `not_applicable=4`

Delta from the prior guidance replay:

- `override`: `0 structural / 3 shallow / 0 source-only` -> `1 structural / 2 shallow / 0 source-only`
- total: `12 structural / 10 shallow` -> `13 structural / 9 shallow`

This is intentionally modest. The repair does not pretend every precedence
surface is structural. It only recognizes the pairwise three-slot form as
architecture and leaves rank-only rows as pressure.

Lesson:

Rule composition confirms the value of slot contracts more strongly than
evidence provenance did. The lens vocabulary is not fixture-shaped, but it is
resolution-sensitive: the architecture can preserve enough rule facts for QA
while still losing the joins needed for transfer-stable rule reasoning. The
right repair target is compile-surface guidance for anchored rule relations,
not helper rows and not fixture-specific rule names.

Next pressure:

The remaining weak rule-composition surface is still partner/scope resolution,
but it is now narrower: rank-only precedence and two-slot override/exception
links. The next repair should focus on avoiding `precedence_level(rule, high)`
when the source names the compared rule, and avoiding `rule_exception(Base,
Exception)` without also preserving the exception condition and effect/scope.

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

Exception-link follow-on:

The two-slot exception weakness had a slightly different shape than pairwise
precedence. In the activation-anchor replay, the compiler emitted a generic
and transferable pattern:

- `rule_exception(BaseRule, ExceptionRule)`
- `rule_condition(ExceptionRule, Condition)`
- `rule_action(ExceptionRule, EffectOrScope)`

That should satisfy the exception lens even though no single row has all
slots. The audit now recognizes that linked-row contract. A bare
`rule_exception(BaseRule, ExceptionRule)` remains shallow unless the exception
anchor also has condition and effect/scope rows.

Exception-link artifacts:

- `docs/data/lens_vocabulary_audit/rule_composition_v1_exception_link_reaudit_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_exception_link_reaudit_20260515.json`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_guidance_exception_link_reaudit_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_guidance_exception_link_reaudit_20260515.json`

Focused activation replay delta:

- before: `3 structural / 4 shallow / 0 source-only / 3 N/A`
- after: `4 structural / 3 shallow / 0 source-only / 3 N/A`
- `exception`: `shallow` -> `structural`

Three-fixture guidance replay stayed at `13 structural / 9 shallow / 4
source-only / 4 N/A` because its exception terms had already reached structural
status. This is still a useful audit fix: it prevents future generic
`rule_exception + rule_condition + rule_action` compiles from being falsely
treated as shallow.

Override-scope follow-on:

The two-slot override weakness has the same linked-row form, anchored on the
higher or overriding rule:

- `rule_precedence(HigherRule, LowerRule)` or equivalent two-slot override link
- `rule_condition(HigherRule, Condition)`
- `rule_action(HigherRule, EffectOrScope)`

That is now structural for `override`. A bare two-slot override/precedence link
remains shallow, and rank-only rows remain shallow.

Override-scope artifacts:

- `docs/data/lens_vocabulary_audit/rule_composition_v1_override_scope_reaudit_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_override_scope_reaudit_20260515.json`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_guidance_override_scope_reaudit_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_guidance_override_scope_reaudit_20260515.json`

Focused activation replay delta:

- before exception-link audit: `4 structural / 3 shallow / 0 source-only / 3 N/A`
- after override-scope audit: `5 structural / 2 shallow / 0 source-only / 3 N/A`
- `override`: `shallow` -> `structural`

Three-fixture guidance replay stayed at `13 structural / 9 shallow / 4
source-only / 4 N/A` because the older replay compiles do not expose the
condition/action pair for the two-slot override links. The focused replay now
shows the target state: activation, exception, and override can all become
structural when the compiler emits the linked generic contracts.

Post-contract three-fixture replay:

After the activation, pairwise, exception-link, and override-scope contracts
landed, the three rule-composition probes were freshly recompiled. This was a
score-stamp replay, not a new repair pass.

Post-contract artifacts:

- `docs/data/lens_vocabulary_audit/rule_composition_v1_post_contract_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_post_contract_audit_20260515.json`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_post_contract_calibrated_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_post_contract_calibrated_audit_20260515.json`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_post_contract_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/rule_composition_v1_post_contract_qa_summary_20260515.json`
- `tmp/lens_vocab_rule_composition_post_contract_compile_20260515`
- `tmp/lens_vocab_rule_composition_post_contract_qa_20260515`

Fresh compile:

- compiles=`3`
- parsed_ok=`3`
- admitted/skipped=`98 / 0`
- candidate predicates=`44`

Initial post-contract audit:

- `structural=11`
- `shallow_structural=14`
- `source_only=1`
- `not_applicable=4`

This first readout exposed an audit-calibration issue rather than a compile
failure. The fresh compiles used current generic predicate names such as
`rule_consequence/3`, `requires_count/4`, `requires_vote/3`, and
`exception_for/2`. Those are fixture-free rule surfaces, but the audit still
knew mostly the earlier predicate palette.

Calibrated post-contract audit:

- `structural=15`
- `shallow_structural=11`
- `source_only=0`
- `not_applicable=4`

Term readout:

| Term | Structural | Shallow | Source-only | N/A | Reading |
| --- | ---: | ---: | ---: | ---: | --- |
| `activation_condition` | 1 | 2 | 0 | 0 | Improved but still often under-specified. |
| `base_rule` | 3 | 0 | 0 | 0 | Stable under the current generic condition/consequence palette. |
| `eligibility_condition` | 1 | 2 | 0 | 0 | Still shallow where condition rows lack enough role/context typing. |
| `exception` | 2 | 1 | 0 | 0 | Mostly structural; one exception still lacks full linked effect/scope. |
| `expiration` | 2 | 0 | 0 | 1 | Stable where present. |
| `fallback_rule` | 3 | 0 | 0 | 0 | Stable. |
| `override` | 0 | 3 | 0 | 0 | Main remaining weakness. |
| `precedence` | 0 | 3 | 0 | 0 | Main remaining weakness; rank/pair scope still thin. |
| `threshold` | 2 | 0 | 0 | 1 | Stable after accepting `requires_count/4`. |
| `vote_requirement` | 1 | 0 | 0 | 2 | Stable where present after accepting `requires_vote/3`. |

QA:

- questions=`25`
- exact/partial/miss=`25 / 0 / 0`
- helper rows=`0`

Reading:

The post-contract replay affirms the architecture is holding together. Compile
health improved sharply (`98 admitted / 0 skipped`) and QA is perfect without
helper rows. The lens audit remains stricter than the answer score, which is
the intended behavior. The remaining shallow pressure is no longer broad rule
composition; it is concentrated in `override` and `precedence`, with smaller
activation/eligibility resolution issues. There is no source-only residue left
in this replay.

Verification:

- `python -m pytest tests\test_lens_vocabulary_transfer.py -q` -> `15 passed`

Lesson:

Rule composition confirms the value of slot contracts more strongly than
evidence provenance did. The lens vocabulary is not fixture-shaped, but it is
resolution-sensitive: the architecture can preserve enough rule facts for QA
while still losing the joins needed for transfer-stable rule reasoning. The
right repair target is compile-surface guidance for anchored rule relations,
not helper rows and not fixture-specific rule names.

Next pressure:

The remaining weak rule-composition surface is still partner/scope resolution,
but it is now mostly rank-only precedence and older compiles that never emitted
the linked contracts. Rule composition has reached the point where the next
useful move is either a fresh three-fixture replay under the tightened audit, or
switching to the next lens vocabulary: authority/custody.

Decision:

Rule composition is calibrated enough for this pass. The next lens vocabulary
audit should move to authority/custody rather than continuing to chase the last
rank-only precedence cases in this same probe set.

## LV-005 - Authority/Custody Slot Contracts

Date: 2026-05-15

Question:

Does the authority/custody vocabulary transfer to unlike documents, and can its
terms be audited with slot contracts rather than surface labels?

Before:

The source-authority work from CSS had already improved compile guidance for
orders, board decisions, controlling findings, and custody/access states. What
had not been checked was the lens vocabulary admission layer. The worry was
that terms such as `court_order`, `governing_rule`, `board_vote`,
`official_record`, `staff_note`, `draft_recommendation`,
`controlling_finding`, `noncontrolling_source`, `custody_holder`, and
`access_control` might fire because of familiar labels rather than because the
compiler preserved the governing slots.

Prediction:

Authority/custody should look different from evidence provenance and rule
composition. Its terms form a ladder of authority and custody states:
draft/staff/official/controlling/noncontrolling plus holder/access surfaces. The
right audit should therefore be stricter than QA. It should accept direct
relations such as item+custody-holder or item+access-controller, and it should
also accept transferable linked record contracts such as
`record_entry(Source, Type, Body, Date)` plus answer-bearing
`record_detail/3`, access, rule, vote, or content rows. A label-only
`document_type(Source, court_order)` should remain shallow unless the governed
action/scope/reason is also queryable.

Intervention:

- Added the `authority_custody` lens vocabulary to
  `scripts/audit_lens_vocabulary_transfer.py`.
- Added a noncontrolling-source contract that requires the source plus either
  an in-row reason/content slot or a linked reason detail. A bare
  `source_status(Source, noncontrolling)` remains shallow.
- Added generic record-entry/document-type linked contracts for authority
  records. This accepts unlike, transferable palettes such as
  `record_entry/4 + record_detail/3`, not just named predicates.
- Tightened source-authority and compile-surface guidance to preserve authority
  and custody ladder slots: source/body, governed subject/claim/action/item,
  authority status or precedence, scope/date, custody/access actor, and reason
  noncontrolling when stated.
- Built three fresh unlike fixtures:
  `clinic_device_custody`, `housing_archive_access`, and `lab_sample_chain`.

After:

Compile:

- fixtures=`3`
- parsed_ok=`3`
- candidate predicates=`54`
- admitted/skipped=`348 / 27`

Lens audit:

- `structural=18`
- `shallow_structural=11`
- `source_only=1`
- `not_applicable=0`

Term readout:

| Term | Structural | Shallow | Source-only | Reading |
| --- | ---: | ---: | ---: | --- |
| `access_control` | 3 | 0 | 0 | Stable. Direct access-controller/access-permission surfaces transfer. |
| `custody_holder` | 3 | 0 | 0 | Stable. Item+holder is a legitimate compact relation when stated. |
| `board_vote` | 2 | 1 | 0 | Mostly structural; one compile preserved vote effects without full vote source/body/date. |
| `governing_rule` | 2 | 1 | 0 | Mostly structural; one bylaw-style source lacked anchored rule content. |
| `official_record` | 2 | 1 | 0 | Mostly structural; one official label lacked enough governed content. |
| `staff_note` | 2 | 1 | 0 | Mostly structural; one note was typed without recommendation content. |
| `draft_recommendation` | 1 | 2 | 0 | Weakest recommendation surface; labels often survived without effect/status slots. |
| `controlling_finding` | 1 | 2 | 0 | Controlling status often survived, but finding scope/content remained thin. |
| `court_order` | 1 | 2 | 0 | Strict by design; order label alone does not pass without governed access/action rows. |
| `noncontrolling_source` | 1 | 1 | 1 | Reason-bearing noncontrol transfers, but copied/superseded reasons are still fragile. |

QA:

- questions=`30`
- exact/partial/miss=`30 / 0 / 0`
- helper rows=`0`

Artifacts:

- `docs/data/lens_vocabulary_audit/authority_custody_v1_compile_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_compile_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_slot_contract_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_slot_contract_audit_20260515.json`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_qa_summary_20260515.json`
- `experiments/lens_vocabulary_audits/authority_custody_v1/`
- `tmp/lens_vocab_authority_custody_compile_20260515`
- `tmp/lens_vocab_authority_custody_qa_20260515`

Verification:

- `python -m pytest tests\test_lens_vocabulary_transfer.py tests\test_domain_bootstrap_file.py -q` -> `51 passed`

Lesson:

Authority/custody confirms the distinction between answerability and vocabulary
resolution. The system can answer the unlike fixture questions perfectly with
zero helper rows, but the lens audit still exposes shallow terms where the
compiler preserved a source label or authority status without the governed
action, scope, or noncontrol reason. That is the correct calibration. The
architecture should not treat `court_order` or `controlling_finding` as earned
just because those words reached a type slot.

Next pressure:

The strongest remaining pressure is not helper delivery. It is authority-ladder
resolution: draft recommendation content/effect, controlling finding
scope/content, court-order governed action/scope, and noncontrolling reason
should survive as linked rows when stated. A focused follow-on should strengthen
those compile surfaces and then replay the same three fixtures. After that, the
next lens-vocabulary candidate is operational record status.

## LV-006 - Authority Record-Detail Replay

Date: 2026-05-15

Question:

Does an explicit record-detail invariant reduce authority/custody shallow terms
on the same three unlike probes?

Before:

LV-005 established that QA can be perfect while vocabulary resolution remains
thin. The shallow terms were not random. They clustered around authority record
metadata: `court_order`, `official_record`, `draft_recommendation`,
`controlling_finding`, and `noncontrolling_source`. The compiler often emitted
type/status rows but not a same-anchor governed action, scope, content, or
reason row.

Prediction:

Adding one compact invariant should help if the failure is simply that the
compiler needs a stronger reminder to pair authority record metadata with
same-anchor details. If the result is stochastic or palette-sensitive, the
audit may not improve monotonically even if QA remains stable.

Intervention:

Added an authority record-detail rule to both the source-authority context and
the global compile-surface invariant context:

- when emitting `document_type/2` or `record_entry/4` for an order, rule, vote,
  finding, note, draft, register, copied notice, or custody/access source,
  pair it with same-anchor content/effect/scope/condition/decision/governed
  subject/reason rows when those details are stated;
- type, author, date, and status alone remain shallow record metadata.

After:

Compile:

- fixtures=`3`
- parsed_ok=`3`
- candidate predicates=`53`
- admitted/skipped=`395 / 43`

Lens audit:

- before=`18 structural / 11 shallow / 1 source-only`
- after=`16 structural / 13 shallow / 1 source-only`

Term changes:

- `governing_rule`: `2 structural / 1 shallow` -> `3 structural / 0 shallow`
- `controlling_finding`: `1 structural / 2 shallow` -> `2 structural / 1 shallow`
- `noncontrolling_source`: `1 structural / 1 shallow / 1 source-only` -> `0 structural / 2 shallow / 1 source-only`
- `official_record`: `2 structural / 1 shallow` -> `0 structural / 3 shallow`
- `access_control`: `3 structural / 0 shallow` -> `2 structural / 1 shallow`

QA:

- questions=`30`
- exact/partial/miss=`30 / 0 / 0`
- helper rows=`0`

Artifacts:

- `docs/data/lens_vocabulary_audit/authority_custody_v1_record_detail_compile_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_record_detail_compile_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_record_detail_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_record_detail_audit_20260515.json`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_record_detail_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_record_detail_qa_summary_20260515.json`
- `tmp/lens_vocab_authority_custody_record_detail_compile_20260515`
- `tmp/lens_vocab_authority_custody_record_detail_qa_20260515`

Verification:

- `python -m pytest tests\test_lens_vocabulary_transfer.py tests\test_domain_bootstrap_file.py -q` -> `51 passed`

Lesson:

The record-detail invariant is directionally right but not enough to treat as a
landed repair. It improved governed-rule and controlling-finding resolution but
lost structural credit on official-record and noncontrolling-source terms under
a fresh stochastic compile. QA stayed perfect with zero helper rows. The
scientific reading is that authority/custody is palette-sensitive: the same
source can compile into multiple generic record grammars that answer correctly,
but the lens audit only sees transfer-stable structure when the source row and
its governed detail share an anchor.

Next pressure:

Do not chase this with fixture-shaped record names. The next useful move is to
make the authority record-detail invariant executable at the audit/contract
level for more generic palettes, especially official-register and copied-source
reason rows, then run a two-draw replay only if the contract change is clearly
generic. Otherwise switch to operational record status as the next lens and
return to authority/custody with a larger transfer set.

## LV-007 - Operational Record Status Initial Six-Probe Audit

Date: 2026-05-15

Question:

Does the operational record/status vocabulary transfer on a larger first cycle
than the earlier three-probe lens audits?

Before:

Operational record/status had strong compile guidance but no lens vocabulary
admission audit. The expected vocabulary includes received/filed, assigned,
approved, denied, withdrawn, pending, corrected, superseded, reopened, closed,
current status, and status transition. Because status vocabularies are
transition-heavy and palette-sensitive, this pass used six unlike probes rather
than three.

Prediction:

The answer score should remain strong without helpers, but the vocabulary audit
should be noisier than evidence provenance, rule composition, or
authority/custody. A status word alone should not be enough. Structural credit
requires the record/event id, subject/item/application, actor/body,
timestamp/turn, before/after state when stated, authority/source, and
reason/correction detail when stated.

Intervention:

- Added `operational_record_status` to
  `scripts/audit_lens_vocabulary_transfer.py`.
- Added generic audit contracts for direct status predicates and
  `record_entry`/`record_detail` style linked rows.
- Added operational slot-contract guidance to
  `scripts/run_domain_bootstrap_file.py`.
- Built six unlike probes:
  `permit_renewal_docket`, `clinic_intake_corrections`,
  `warehouse_repair_log`, `water_sample_docket`, `grant_review_queue`, and
  `library_preservation_queue`.

After:

Compile:

- fixtures=`6`
- parsed_ok=`6`
- candidate predicates=`81`
- admitted/skipped=`378 / 18`

Lens audit:

- `structural=15`
- `shallow_structural=41`
- `source_only=14`
- `not_applicable=8`

Term readout:

| Term | Structural | Shallow | Source-only | N/A | Reading |
| --- | ---: | ---: | ---: | ---: | --- |
| `superseded` | 4 | 2 | 0 | 0 | Strongest transfer term. Replacement relations are often explicit. |
| `approved` | 2 | 4 | 0 | 0 | Answerable, but often label-level rather than slot-complete. |
| `corrected` | 2 | 3 | 1 | 0 | Correction details sometimes stay in source text. |
| `current_status` | 2 | 1 | 3 | 0 | Current status is queryable in some compiles, source-only in others. |
| `received` | 0 | 4 | 2 | 0 | Weak: received actor/object often not bound together. |
| `filed` | 0 | 3 | 3 | 0 | Weak: filing events often stay metadata/source-only. |
| `closed` | 0 | 6 | 0 | 0 | Universal but shallow; closure label needs actor/date/outcome slots. |
| `reopened` | 0 | 3 | 0 | 3 | Present in only half the probes and shallow where present. |

QA:

- questions=`48`
- exact/partial/miss=`46 / 0 / 2`
- helper rows=`0`

Misses:

- `permit_renewal_docket q001`: receiving clerk identity stayed in source text;
  structured row answered `applicant` instead of clerk Erin Moss.
- `warehouse_repair_log q006`: withdrawn request returned an internal ticket id
  without the descriptive request content `scanner-replacement request`.

Artifacts:

- `docs/data/lens_vocabulary_audit/operational_record_status_v1_compile_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_compile_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_slot_contract_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_slot_contract_audit_20260515.json`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_qa_summary_20260515.json`
- `experiments/lens_vocabulary_audits/operational_record_status_v1/`
- `tmp/lens_vocab_operational_record_status_compile_20260515`
- `tmp/lens_vocab_operational_record_status_qa_20260515`

Lesson:

The larger initial probe set mattered. Operational status looks much more
palette-sensitive than the earlier lenses. QA is strong at `95.83%` with zero
helpers, but the audit shows the compile often preserves status labels without
binding the actor, governed subject, status transition, and descriptive content
in the same queryable structure. The next repair should target received/filed
actor binding and withdrawn-request descriptive content, not broad helper rows.

Next pressure:

Strengthen operational record compile guidance for two generic surfaces:
received/filed actor-object records and withdrawn/retracted request content.
Then replay the same six probes. Do not add fixture-specific predicates for
permit clerks or scanner requests.

## LV-008 - Authority/Custody Expanded Six-Probe Replay

Date: 2026-05-15

Question:

Does the authority/custody vocabulary hold when expanded from three unlike
probes to six?

Before:

LV-005 and LV-006 showed perfect QA on three probes but exposed shallow
authority ladder terms. The expanded pass added three unlike probes:
`transit_lost_property_release`, `makerspace_tool_lockout`, and
`community_garden_gate_key`.

Prediction:

Adding more samples should keep answer quality high but make the vocabulary
audit less flattering. Stable terms should be direct state surfaces such as
custody holder and access control. Ladder terms such as staff note, draft
recommendation, controlling finding, court order, and noncontrolling source
should remain shallow unless source/detail/scope/reason slots are linked.

Intervention:

- Added three authority/custody probes for lost-property release, machine
  lockout, and gate-key custody.
- Recompiled all six authority/custody fixtures in one OpenRouter six-lane
  batch under the current record-detail guidance.
- Re-ran the authority/custody lens audit and QA over the full six-fixture set.

After:

Compile:

- fixtures=`6`
- parsed_ok=`6`
- candidate predicates=`107`
- admitted/skipped=`805 / 39`

Lens audit:

- prior three-fixture pre-repair readout=`18 structural / 11 shallow / 1 source-only`
- prior three-fixture record-detail replay=`16 structural / 13 shallow / 1 source-only`
- expanded six-fixture replay=`19 structural / 41 shallow / 0 source-only`

Term readout:

| Term | Structural | Shallow | Reading |
| --- | ---: | ---: | --- |
| `access_control` | 6 | 0 | Stable across all six. |
| `custody_holder` | 5 | 1 | Mostly stable; one compile preserved custody as metadata. |
| `board_vote` | 3 | 3 | Half structural, half label-level. |
| `governing_rule` | 3 | 3 | Half structural, half label-level. |
| `court_order` | 1 | 5 | Court/order labels usually lack governed action/scope rows. |
| `official_record` | 1 | 5 | Official-register labels often lack governed content. |
| `staff_note` | 0 | 6 | Notes are consistently typed but not slot-complete. |
| `draft_recommendation` | 0 | 6 | Draft recommendations are consistently shallow. |
| `controlling_finding` | 0 | 6 | Controlling status reaches the KB, but finding content/scope often does not. |
| `noncontrolling_source` | 0 | 6 | Noncontrol status is present, reason/source-of-copy is thin. |

QA:

- questions=`54`
- exact/partial/miss=`54 / 0 / 0`
- helper rows=`0`

Artifacts:

- `docs/data/lens_vocabulary_audit/authority_custody_v1_expanded_compile_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_expanded_compile_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_expanded_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_expanded_audit_20260515.json`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_expanded_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_expanded_qa_summary_20260515.json`
- `experiments/lens_vocabulary_audits/authority_custody_v1/`
- `tmp/lens_vocab_authority_custody_expanded_compile_20260515`
- `tmp/lens_vocab_authority_custody_expanded_qa_20260515`

Lesson:

The expanded replay confirms the earlier warning. Authority/custody is highly
answerable but not yet slot-stable. The direct state terms transfer. The
authority ladder terms mostly do not: the compiler can answer from source
records and nearby facts, but the lens audit is correctly refusing to count
typed documents as structural authority unless governed action, scope, content,
or reason slots are linked. This is a compile-resolution problem, not a helper
problem.

Next pressure:

The next authority/custody repair should focus on one generic linked-record
contract: if a source is typed as `staff_note`, `draft_recommendation`,
`controlling_finding`, or `noncontrolling_source`, preserve a same-anchor
content/effect/scope/reason row. But operational record/status has the more
actionable immediate misses, so the next implementation slice should repair
operational received/filed actor binding and withdrawn-request descriptive
content first.

## LV-009 - Operational Actor/Content Replay

Date: 2026-05-15

Question:

Can a small compile-guidance repair fix the two operational QA misses without
adding helper rows or fixture-specific vocabulary?

Before:

LV-007 produced `46 / 0 / 2` QA on six operational probes with zero helpers.
The misses were generic:

- a received/filed event bound the submitted object to the submitter rather
  than the receiving clerk;
- a withdrawn request row preserved the record id and date but not the
  descriptive requested action.

Prediction:

If the misses are prompt-level compile omissions, explicit guidance should keep
the receiving/filing actor distinct from the submitter/source actor and preserve
withdrawn request content. If the issue is palette instability, the lens audit
may improve while QA variance moves elsewhere.

Intervention:

Added two operational compile-surface rules:

- received/filed/logged/docketed events must bind the receiving or filing actor
  to the submitted object and keep that actor distinct from the
  submitter/source actor;
- withdrawn/retracted/cancelled/denied/approved/superseded request rows must
  preserve the requested action/content/line item or descriptive target when
  stated.

After:

Compile:

- fixtures=`6`
- parsed_ok=`6`
- candidate predicates=`80`
- admitted/skipped=`352 / 8`

Lens audit:

- before=`15 structural / 41 shallow / 14 source-only / 8 N/A`
- after=`32 structural / 29 shallow / 10 source-only / 7 N/A`

QA:

- before=`46 / 0 / 2`
- after=`44 / 1 / 3`
- helper rows=`0`

Result details:

- `warehouse_repair_log q006` improved: the withdrawn scanner-replacement
  request became answerable.
- `permit_renewal_docket q001` stayed a miss: receiving clerk binding remained
  thin.
- New misses/partial appeared in `water_sample_docket` and
  `grant_review_queue`, showing compile variance moved the boundary rather than
  cleanly extending it.

Artifacts:

- `docs/data/lens_vocabulary_audit/operational_record_status_v1_actor_content_compile_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_actor_content_compile_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_actor_content_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_actor_content_audit_20260515.json`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_actor_content_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_actor_content_qa_summary_20260515.json`
- `tmp/lens_vocab_operational_record_status_actor_content_compile_20260515`
- `tmp/lens_vocab_operational_record_status_actor_content_qa_20260515`

Lesson:

This is not a landed repair. The vocabulary audit improved sharply, but QA
worsened. That means stronger prose guidance can move the compile palette
toward slot completeness while also perturbing which facts survive. The correct
next step is not more prose pressure. Operational received/filed and
withdrawn-content surfaces likely need either profile-palette support or an
audit of candidate predicate selection, not helper rows and not fixture-specific
terms.

Next pressure:

Pause operational repair here. Treat LV-009 as evidence that operational status
has higher compile variance than the earlier lenses. Move to the requested
authority gradient slot contracts, where the current pressure is audit
admission and structural ceiling rather than QA failure.

## LV-010 - Authority Gradient Slot Contracts

Date: 2026-05-15

Question:

Can authority/custody gradient terms earn more structural credit under generic
linked contracts, and do the remaining shallow cases indicate a real structural
ceiling?

Before:

The expanded six-probe authority/custody replay was `54 / 0 / 0` QA with zero
helpers, but the audit was `19 structural / 41 shallow`. The direct state terms
held; the gradient terms did not. A manual read showed that several compiles
used generic but previously unrecognized palettes:

- `source_document/2 + source_declares/3`
- `record_type/2 + record_provision/3`
- `event_type/2 + event_outcome/2`
- direct single-row authority surfaces such as `controlling_finding/2`,
  `non_controlling_record/2`, and `vote_outcome/3`

Prediction:

Adding these linked contracts should improve the audit, but gradient terms will
still yield less than direct custody/access terms. Some remaining shallow cases
may be valid sparsity: the source may legitimately identify a source layer
without binding a separate action/scope/reason slot, or the compiler may place
the answer-bearing content in a neighboring state row rather than same-anchor
source detail.

Intervention:

Expanded the authority/custody audit contracts to accept generic linked
authority palettes:

- `source_document`, `record_type`, and `event_type` can provide the typed
  source/event anchor;
- `source_declares`, `source_grants_no_authorization`, `record_provision`,
  `event_outcome`, `vote_outcome`, access/prohibition rows, and rule-effect
  rows can satisfy the governed content/effect/scope slot;
- draft recommendations can be recognized when a recommendation source also has
  a draft label.

After:

Lens audit over the same six authority/custody compiles:

- before=`19 structural / 41 shallow`
- after=`31 structural / 29 shallow`

Term movement:

| Term | Before Structural | After Structural | Reading |
| --- | ---: | ---: | --- |
| `access_control` | 6 | 6 | Already stable. |
| `custody_holder` | 5 | 5 | Already mostly stable. |
| `board_vote` | 3 | 4 | Modest gain via event/vote outcome contracts. |
| `governing_rule` | 3 | 4 | Modest gain via rule-effect contracts. |
| `court_order` | 1 | 3 | Real gain from event/order outcome contracts. |
| `controlling_finding` | 0 | 3 | Real gain from source/record provision contracts. |
| `staff_note` | 0 | 3 | Real gain from record-provision contracts. |
| `official_record` | 1 | 2 | Small gain; often valid sparse metadata. |
| `draft_recommendation` | 0 | 1 | Still weak. |
| `noncontrolling_source` | 0 | 0 | Still weak; reason/source-of-copy is the hard slot. |

QA:

- unchanged expanded authority/custody readout=`54 / 0 / 0`
- helper rows=`0`

Artifacts:

- `docs/data/lens_vocabulary_audit/authority_custody_v1_gradient_contract_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_gradient_contract_audit_20260515.json`

Lesson:

The gradient-slot contract worked, but it also exposed a ceiling shape. There
is no ceiling for authority/custody as a whole: structural count moved from 19
to 31 without fixture-specific names. There is, however, a practical ceiling
for gradient terms in this compile regime. Direct state terms (`access_control`,
`custody_holder`) are compact and stable. Gradient terms need same-anchor source
content, scope, effect, or reason rows, and those are often absent or placed in
neighboring state rows. Some official-record sparsity is acceptable: a source
can be an official register while the custody/access fact carries the operative
content. Noncontrolling-source is different: because the source explicitly
states the reason in all six probes, remaining shallow cases are not valid
sparsity; they are still compile-resolution pressure.

Next pressure:

Do not attempt to force all gradient terms to 100 percent structural. The next
authority/custody work should target only the hard noncontrol reason/source
slot and maybe draft recommendation content. The broader CTO focus should stay
on distinguishing valid sparse authority metadata from missing source-detail
resolution.

## LV-011 - Authority Hard-Case Gradient Replay

Date: 2026-05-15

Question:

Do focused unlike probes for draft-recommendation content and noncontrolling
source reason/source binding show a repairable gap, a valid sparsity ceiling, or
a query-only issue?

Before:

The expanded six-probe authority/custody audit was strong on direct state terms
but weak on gradient terms:

- expanded QA=`54 / 0 / 0`
- expanded audit after gradient contracts=`31 structural / 29 shallow`
- `draft_recommendation`=`1 / 6 structural`
- `noncontrolling_source`=`0 / 6 structural`

Prediction:

If the gradient terms are merely under-tested, fresh focused probes should
produce same-anchor content/reason rows. If they have a structural ceiling, QA
may remain high while the audit stays shallow because the compiler stores
content in neighboring document/status rows or source-record text.

Intervention:

Added six small unlike authority/custody probes:

- `clinic_fridge_notice`
- `repair_room_signage`
- `theater_prop_cage`
- `library_cart_policy_draft`
- `pool_lane_schedule_draft`
- `studio_key_access_draft`

Strengthened the generic surface contracts, not fixture terms:

- source guidance now says draft recommendations need proposed
  content/action/scope plus pending approval/review/vote/legal condition;
- source guidance now says copied/advisory/superseded/rejected/noncontrolling
  sources need the weaker source, copied/superseded relation, and stated reason
  or omitted controlling source;
- the audit now accepts common generic aliases such as `doc_type`, `doc_status`,
  `doc_content`, `proposal_content`, `proposed_action`, `pending_approval`,
  `copied_from`, `omitted_authority`, and source-recorded noncontrol reasons.

After:

Hard-case compile:

- fixtures=`6`
- parsed_ok=`6`
- candidate predicates=`84`
- admitted/skipped=`465 / 8`

Hard-case QA:

- questions=`30`
- exact/partial/miss=`28 / 1 / 1`
- helper rows=`0`

Hard-case lens audit:

- before alias-contract repair=`15 structural / 35 shallow / 1 source-only / 9 N/A`
- after alias-contract repair=`22 structural / 28 shallow / 1 source-only / 9 N/A`
- `draft_recommendation`=`2 structural / 4 shallow`
- `noncontrolling_source`=`1 structural / 4 shallow / 1 N/A`

Combined current authority/custody audit over the earlier six plus the six hard
cases:

- compiles=`12`
- status counts=`53 structural / 57 shallow / 1 source-only / 9 N/A`
- `access_control`=`12 / 12 structural`
- `custody_holder`=`10 structural / 1 shallow / 1 source-only`
- `draft_recommendation`=`3 structural / 9 shallow`
- `noncontrolling_source`=`1 structural / 10 shallow / 1 N/A`

Artifacts:

- `experiments/lens_vocabulary_audits/authority_custody_v1/clinic_fridge_notice`
- `experiments/lens_vocabulary_audits/authority_custody_v1/repair_room_signage`
- `experiments/lens_vocabulary_audits/authority_custody_v1/theater_prop_cage`
- `experiments/lens_vocabulary_audits/authority_custody_v1/library_cart_policy_draft`
- `experiments/lens_vocabulary_audits/authority_custody_v1/pool_lane_schedule_draft`
- `experiments/lens_vocabulary_audits/authority_custody_v1/studio_key_access_draft`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_hardcases_compile_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_hardcases_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_hardcases_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/authority_custody_v1_combined_12_audit_20260515.md`

Lesson:

The answers are mostly inside the set, but the gradient vocabulary is not clean.
Authority/custody direct state is stable without helpers. Draft and
noncontrolling terms are different: the compiler often emits the answer-bearing
content as document text, `doc_content`, `supersedes`, or source-record evidence
near the source anchor, while the vocabulary audit requires a same-anchor
content/reason contract. Some gradient sparsity is valid for official records,
but the hard-case probes state the draft content and noncontrol reason
explicitly, so the remaining shallow rows are compile-resolution pressure, not
acceptable absence.

Next pressure:

Do not chase authority/custody to 100 percent. The hard case is now named:
draft and noncontrolling source need same-anchor content/reason resolution. The
next requested work is operational status, but it should inspect candidate
predicate selection and profile palette before making another repair.

## LV-012 - Operational Palette Inspection

Date: 2026-05-15

Question:

Why did operational record/status stay noisy after LV-009, and is the issue
helper absence, mapper rejection, QA query planning, or profile-palette shape?

Before:

LV-009 improved the operational lens audit but worsened QA:

- audit moved `15 structural / 41 shallow / 14 source-only / 8 N/A` to
  `32 structural / 29 shallow / 10 source-only / 7 N/A`
- QA moved `46 / 0 / 2` to `44 / 1 / 3`
- helper rows remained `0`

Intervention:

Inspected the four not-exact rows and the compile palettes for the six
operational probes. This was an inspection pass only: no new helper, no new
prompt prose, no fixture-specific repair.

After:

The remaining failures are palette/profile issues, not mapper-admission issues:

- `grant_review_queue q008`: the answer exists as
  `status_at(gq_5, approved_with_revised_budget, 2026_05_10)`, but another
  alias `queue_gq5` carries only `approved`.
- `permit_renewal_docket q005`: the source says hold notice `H-2` superseded
  approval, but the compile emits `status_superseded_by(..., pending_payment)`,
  turning the superseding document into the resulting status.
- `water_sample_docket q001`: field receipt and lab receipt both use receipt
  language; the compile puts lab receipt in `sample_received` and field receipt
  in `docket_filed`.
- `water_sample_docket q002`: initial status is in source text but no direct
  initial-status row exists.

Artifact:

- `docs/data/lens_vocabulary_audit/operational_record_status_v1_palette_inspection_20260515.md`

Lesson:

Operational status needs a stable lifecycle palette, not helper rows and not
more broad guidance. The weak slots are canonical record identity, status phase
(`initial`, `current`, `final`, point-in-time), repeated-verb event layer, and
supersession target type. The compiler is producing plausible local predicates,
but the selectors need a cross-fixture grammar to avoid alias splits and
document-vs-status collapse.

Next pressure:

Design a profile-palette contract for operational lifecycle rows before another
compile experiment. The repair should prefer phase-bearing status predicates,
alias/equivalence rows for docket/file/queue ids, separated receipt/logging
event layers, and a distinction between the source/event/document that
supersedes and the resulting status after supersession.

## LV-013 - Operational Lifecycle Palette Diagnostic

Date: 2026-05-15

Question:

Can we measure the operational record/status failure shape without adding
another repair, so the next layer is chosen from data rather than guessed?

Before:

LV-012 named four suspected lifecycle pressures:

- alias splits across local record atoms;
- ambiguous repeated verbs across event layers;
- supersession target collapse, where the compile keeps the resulting status
  but not the superseding document/event;
- missing status phase, especially initial/current/final distinctions.

Prediction:

The diagnostic should show whether the operational problem is widespread or
concentrated. If all four classes fire everywhere, the profile needs a broad
lifecycle grammar. If only specific classes recur, the next repair can be
smaller.

Intervention:

Added `scripts/audit_operational_lifecycle_palette.py`, a compile-artifact
diagnostic. It does not judge QA and does not propose repairs. It detects:

- `alias_split`: compact identity codes with multiple direct atom variants;
- `ambiguous_repeated_verb`: repeated lifecycle verbs whose direct predicates
  lack event-layer distinction;
- `supersession_target_collapse`: source says a document/event superseded
  something, but the direct row collapses the target to a resulting status;
- `phase_classification_missing`: source states initial/current/final status
  but no phase-bearing direct surface exists.

The first detector pass overcounted dates and long source-addressability labels.
Tuned it before treating the output as evidence.

After:

Operational lifecycle diagnostic over the six existing probes:

- compiles=`6`
- fixtures with findings=`4`
- class counts=`6 phase_classification_missing / 4 alias_split / 2 ambiguous_repeated_verb / 1 supersession_target_collapse`

Fixture summary:

| Fixture | Alias Split | Ambiguous Verb | Supersession Collapse | Phase Missing |
| --- | ---: | ---: | ---: | ---: |
| `clinic_intake_corrections` | 0 | 0 | 0 | 1 |
| `grant_review_queue` | 2 | 0 | 0 | 2 |
| `library_preservation_queue` | 0 | 0 | 0 | 0 |
| `permit_renewal_docket` | 1 | 1 | 1 | 2 |
| `warehouse_repair_log` | 0 | 0 | 0 | 0 |
| `water_sample_docket` | 1 | 1 | 0 | 1 |

Artifacts:

- `scripts/audit_operational_lifecycle_palette.py`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_lifecycle_palette_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_lifecycle_palette_audit_20260515.json`

Lesson:

The operational gap is narrower than feared. Two probes are clean under this
diagnostic, and supersession target collapse is not the dominant class. The
largest pressure is phase-bearing status: source text states initial/current
status six times across four fixtures, but the compiles often preserve only a
local status row without a stable phase slot. Alias split is second: record ids
and short ids drift into multiple atoms. Repeated-verb ambiguity is real but
limited to cases where the same ordinary verb names different event layers
(`received` as field receipt versus lab receipt, or application received versus
payment received).

Next pressure:

Design the smallest operational lifecycle profile contract around the measured
classes: phase-bearing status rows first, canonical alias/equivalence second,
and event-layer distinction for repeated verbs third. Supersession target
collapse should be included, but it is a focused one-fixture pressure rather
than the center of the repair.

## LV-014 - Operational Lifecycle Palette Extension

Date: 2026-05-15

Question:

Can a small profile-palette extension make operational record/status compiles
more compact and useful without adding helper rows or teaching the harness the
six probe stories?

Before:

LV-013 showed a narrow operational lifecycle shape:

- `phase_classification_missing` was the largest class;
- alias splits were second;
- repeated-verb ambiguity was real but limited;
- supersession target collapse was present but not central.

The previous actor/content replay also showed a warning sign: stronger slot
guidance improved the vocabulary audit while worsening QA. That meant the next
repair had to be tested against no-helper QA, not only against vocabulary
admission counts.

Prediction:

A compact canonical lifecycle palette should improve answerability and reduce
compile delivery volume. It should not be judged a full vocabulary repair unless
the audit also shows the lifecycle terms binding their required slots.

Intervention:

Added operational lifecycle palette guidance at two layers:

- operational profile context now prefers `record_alias/2`,
  `record_status_phase/4`, `record_status_at/3`,
  `record_lifecycle_event/5`, and `record_superseded_by/4` when those predicates
  can carry stated lifecycle slots;
- compile-surface invariants now ask operational lifecycle compiles to preserve
  phase, dated status, event layer, alias, and supersession source separately
  from local labels.

This is a palette preference, not a helper. It adds no fixture-named predicates
and no corpus-specific vocabulary.

After:

Compile replay over the six operational probes:

- fixtures=`6`
- parsed OK=`6`
- candidate predicates=`58`
- admitted/skipped=`276 / 12`

This is materially more compact than the LV-009 actor/content replay
(`352 / 8`) while preserving the same fixture set.

No-helper QA replay:

- questions=`48`
- exact/partial/miss=`46 / 0 / 2`
- exact rate=`95.83%`
- helper rows=`0`

The replay recovered from the LV-009 QA regression (`44 / 1 / 3`) and matched
the original six-probe exact count while keeping helper delivery at zero. Two
previously fragile surfaces improved: the permit supersession/status case and
the grant current-status case both returned to exact.

The lifecycle diagnostic did not become clean:

- `alias_split`: `6`
- `supersession_target_collapse`: `2`
- `phase_classification_missing`: `7`
- `ambiguous_repeated_verb`: `1`

The lens vocabulary admission audit remains mostly shallow:

- `9 structural / 48 shallow / 13 source-only / 8 N/A`

The two remaining no-helper misses are:

- an assignment join gap where the answer requires binding the assigned actor to
  the review target;
- an initial-status compile gap where the source states the initial status but
  the direct surface is still filed/received-oriented.

Artifacts:

- `docs/data/lens_vocabulary_audit/operational_record_status_v1_palette_compile_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_palette_compile_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_palette_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_palette_qa_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_palette_lifecycle_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_palette_lifecycle_audit_20260515.json`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_palette_lens_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/operational_record_status_v1_palette_lens_audit_20260515.json`

Verification:

- `python -m pytest tests\test_domain_bootstrap_file.py -q` -> `30 passed`
- `python -m pytest tests -q` -> `1230 passed, 2 subtests passed`

Lesson:

Operational lifecycle is a palette/profile problem before it is a helper
problem. A small canonical palette can restore no-helper QA and reduce compile
volume, but vocabulary admission still needs stricter slot contracts before the
terms can be called structurally clean. The architecture should distinguish
"answerable with zero helpers" from "lens vocabulary fully earned." Those are
different claims, and LV-014 proves they can diverge.

Next pressure:

Do not add another broad operational guidance paragraph. The next operational
work should be surgical: deterministic identity normalization for record aliases
and a small query/profile pass for assignment joins and initial/current status
selection. In parallel, the lens audit framework is ready to move to the next
remaining vocabulary, using the same rule: unlike probes first, slot contracts
second, repair only after the audit shape is visible.

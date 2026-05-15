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

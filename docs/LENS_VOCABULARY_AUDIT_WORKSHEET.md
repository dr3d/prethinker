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
   - `structural`: term appears in admitted direct facts,
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

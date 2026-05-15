# Language Transfer Audit Worksheet

This worksheet tracks foreign-language probes for hidden English leakage in the
harness. Measurements are not permission to add fixture-specific vocabulary.

Operating rule:

If a non-English probe fails, classify the failure before repair:

- model comprehension;
- date/number normalization;
- source-record label handling;
- generic placeholder/query planning;
- answer rendering/judging;
- true compile-surface absence.

Do not patch from one language fixture unless the repair names a reusable
contract that would still make sense across languages and domains.

## LT-001 - Spanish Municipal Revision Probe

Date: 2026-05-15

Question:

Can the current harness compile and answer a small Spanish revision/status
fixture without new code, new helper rows, or English fixture vocabulary?

Before:

The current audit work has focused on English fixtures. Hidden English leakage
could live in trigger terms, date/time handling, placeholder repair,
source-record labels, or QA planning.

Prediction:

A compact Spanish municipal revision notice should be mostly inside the set if
the LLM can compile the source and the deterministic harness does not depend on
English surface words. Expected weak spots are Spanish date/time expressions,
negative authorization language, and current-version questions.

Intervention:

Added `experiments/language_transfer/spanish_municipal_revision/` with:

- Spanish source;
- Spanish questions;
- Spanish reference answers;
- revision/amendment, changed counts, unchanged count, changed close time,
  negative authorization, correction notice, and current-version state.

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py ... --fixture spanish_municipal_revision ...` ->
  parsed OK, admitted/skipped=`84 / 3`
- `python scripts\run_domain_bootstrap_qa_batch.py ... --helper-companion-row-limit 0 ...` ->
  `12 / 0 / 0`, helpers=`0`
- initial transition/delta normalizer -> observations=`0`
- after audit-only related-document recognizer -> observations=`5`
- `python -m pytest tests -q` -> `1249 passed, 2 subtests passed`

Lesson:

The first foreign-language probe did not expose an answer-path English-only
failure. Spanish source, Spanish questions, and Spanish reference answers
compiled and answered perfectly with zero helpers.

However, the normalizer initially saw no transition/delta observations. The
compile emitted reusable relation predicates such as `amends/2`, `corrects/2`,
`authorized_count/3`, `closing_time/2`, `prohibited_activity/2`, and
`zone_label/3`, but the normalizer did not yet compare predecessor/successor
documents through amendment/correction relations.

Added an audit-only related-document recognizer:

- relation predicates: `amends/2`, `corrects/2`, `supersedes/2`, and
  `*_supersedes/2`;
- compare same predicate/slot values across predecessor and successor
  documents;
- emit transition, unchanged, or added observations.

After that audit-only recognizer, the Spanish compile produced:

- `related_document_value_transition`: food stall count `18 -> 16`;
- `related_document_value_transition`: closing time `20:00 -> 19:30`;
- `related_document_value_unchanged`: craft stall count remains `6`;
- `related_document_value_unchanged`: amplified music remains prohibited;
- `related_document_value_added`: correction notice labels zone B as craft
  stalls.

One language-fidelity watch item remains: atomization stripped Spanish
diacritics into rough ASCII atoms (`p_blicos`, `m_sica`, `beltr_n`). QA did not
lose resolution here, but future multilingual probes should check whether
accent loss creates collisions or source-addressability problems.

Artifacts:

- `experiments/language_transfer/spanish_municipal_revision/`
- `docs/data/lens_vocabulary_audit/language_transfer_spanish_compile_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/language_transfer_spanish_compile_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/language_transfer_spanish_qa_nohelpers_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/language_transfer_spanish_qa_nohelpers_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/language_transfer_spanish_normalization_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/language_transfer_spanish_normalization_audit_20260515.json`

Next pressure:

Build a second multilingual probe that stresses accent collisions or non-Latin
tokenization, but do not jump straight to a large multilingual dataset. Spanish
simple revision/status is inside the set; the next useful test should make the
language surface itself harder.

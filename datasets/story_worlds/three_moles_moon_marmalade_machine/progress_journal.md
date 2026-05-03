# Three Moles Moon-Marmalade Progress Journal

Fixture id: `three_moles_moon_marmalade_machine_v1`

This is the running research record for the Three Moles fixture.

## MMM-000 - Fixture Admission

Date: 2026-05-03

Source: `tmp/The Three Moles and the Moon-Marmalade Machine/`

Files admitted:

- `story.md`
- `source.md`
- `qa_source.md`
- `qa.md`
- `README.md`
- `progress_journal.md`
- `progress_metrics.jsonl`

No model run was executed.

Benchmark discipline:

- This fixture has no gold KB.
- This fixture has no supplied strategy/intake-plan notes.
- This fixture has no ontology registry.
- `qa.md` and `qa_source.md` are scoring assets, not source-compilation
  context.

Expected research value:

- A fresh story-world probe that is related to Otters in form but not in local
  entities or magic mechanics.
- Useful for checking whether story-world guidance generalizes without
  overfitting to one fixture.
- Directly pressures prior contamination, object-state causality, speech/truth
  separation, final-state updates, and restitution coverage.

## MMM-001 - Cold Semantic Parallax Baseline

Date: 2026-05-03

Evidence lane: `cold_unseen`

Mode: source-only profile bootstrap plus current semantic-parallax compile:
flat-plus-focused intake-plan passes, compact focused-pass operations schema,
and LLM-authored source entity ledger. No gold KB, starter registry, or QA
source was used during compilation.

Artifacts:

- Compile:
  `tmp/cold_baselines/three_moles/domain_bootstrap_file_20260503T044804573005Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/three_moles/domain_bootstrap_qa_20260503T045525066737Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Compile: `174` admitted operations, `10` skips, `110` unique facts, `0`
  rules.
- QA: `10 exact / 8 partial / 22 miss` over `40` questions.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `22` compile-surface gaps, `4` hybrid-join gaps, `2`
  query-surface gaps, `2` answer-surface gaps.

Lesson:

This is a useful low cold baseline. The model built a large source surface, but
most misses are still compile-support gaps. Three Moles should stress whether
the story-world lenses can preserve repeated magical object families, final
state, and causality without leaning on Otters-specific context.

## MMM-002 - Diagnostic Replay With Pass Contribution Accounting

Date: 2026-05-03

Evidence lane: `diagnostic_replay_no_prompt_change`

Mode: same source-only semantic-parallax recipe as MMM-001, but with new
pass-surface contribution accounting in the compile artifact. No profile,
oracle, gold KB, or QA source was added.

Artifacts:

- Compile:
  `tmp/diagnostic_replays/three_moles_mmm002/domain_bootstrap_file_20260503T062549409330Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/diagnostic_replays/three_moles_mmm002/domain_bootstrap_qa_20260503T063340787724Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Compile: `103` admitted operations, `1` skip, `91` unique facts, `0`
  rules.
- QA: `13 exact / 3 partial / 24 miss` over `40` questions.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `24` compile-surface gaps, `3` query-surface gaps.

Pass contribution:

- `flat_skeleton`: `13` unique rows.
- `pass_1` entity/static: `38` unique rows, `10` duplicates.
- `pass_2` event/causal chain: `0` unique rows.
- `pass_3` speech/judgment: `32` unique rows, `1` duplicate.
- `pass_4` resolution/moral: `8` unique rows, `1` duplicate.

Lesson:

The new accounting exposed the failure directly: the event/causal lens produced
no admitted surface in this replay. The score moved from MMM-001's `10 exact /
8 partial / 22 miss` to `13 exact / 3 partial / 24 miss`, so this is not a
behavioral improvement claim. It is a diagnostic win: source-surface acquisition
is being throttled by a decorative or failed event-spine pass, and future
general story-world work should make lens contribution visible before tuning
coverage guidance.

## MMM-003 - Focused Pass JSON Retry

Date: 2026-05-03

Evidence lane: `cold_after_general_architecture_change`

Mode: source-only semantic-parallax replay with the new compact
`source_pass_ops_v1` retry. The retry is structural JSON recovery for failed
focused passes; it does not read QA, gold KBs, profiles, or oracle material.

Artifacts:

- Compile:
  `tmp/diagnostic_replays/three_moles_mmm003/domain_bootstrap_file_20260503T064007276674Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/diagnostic_replays/three_moles_mmm003/domain_bootstrap_qa_20260503T064819186081Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Compile: `133` admitted operations, `4` skips, `118` unique facts, `0`
  rules.
- QA: `10 exact / 7 partial / 23 miss` over `40` questions.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `22` compile-surface gaps, `3` hybrid-join gaps, `4`
  query-surface gaps, `1` answer-surface gap.

Pass contribution:

- `flat_skeleton`: `13` unique rows.
- `pass_1` entity/static: `38` unique rows, `10` duplicates.
- `pass_2` event/causal chain: retry triggered and recovered `28` unique rows,
  `2` duplicates.
- `pass_3` speech/judgment: `32` unique rows, `1` duplicate.
- `pass_4` resolution/moral: `7` unique rows, `2` duplicates.

Lesson:

The compact retry fixed the mechanical pass failure from MMM-002: the event
spine lens went from `0` to `28` unique rows and the compile became OK. QA did
not improve over MMM-001 (`10 exact / 8 partial / 22 miss`), which means the
recovered event rows were not yet the missing answer-bearing support. This is
still a useful general harness repair, but it should not be sold as a score
gain until it transfers to another fixture or becomes part of a broader lens
quality improvement.

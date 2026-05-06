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

## MMM-004 - Post-Ingestion Evidence Filter Replay

Date: 2026-05-03

Evidence lane: `diagnostic_replay`

Mode: QA replay over the unchanged MMM-003 compile using
`evidence_bundle_plan_v1` plus evidence-bundle context filtering. No source
recompile, no gold KB, no strategy material, no QA answer key in query
planning, and no QA write proposals.

Artifacts:

- QA:
  `tmp/cold_baselines/three_moles/query_modes/domain_bootstrap_qa_20260503T204837495073Z_qa_qwen-qwen3-6-35b-a3b.json`
- Comparison:
  `tmp/cold_baselines/three_moles/query_modes/three_moles_query_mode_comparison.md`
- Selector:
  `tmp/cold_baselines/three_moles/query_modes/selector_direct_v1.json`

Result:

MMM-003 baseline:

```text
10 exact / 7 partial / 23 miss
```

Evidence-filter replay:

```text
13 exact / 4 partial / 23 miss
```

Diagnostic perfect-selector upper bound:

```text
14 exact / 6 partial / 20 miss
```

Direct non-oracle selector:

```text
11 exact / 4 partial / 25 miss
selected best available mode on 32/40 rows
selector errors: 0
```

Lesson:

Three Moles is the cautionary story-world counterexample to Otters. Evidence
filtering improved exact count, but it did not reduce hard misses, and the
selector regressed when asked to choose between thin evidence surfaces. The
dominant problem remains compile/lens coverage, especially answer-bearing event,
causal, and final-state rows.

## MMM-005 - Source Entity Ledger Compile Transfer

Date: 2026-05-03

Evidence lane: `cold_after_general_architecture_change`

Mode: source-only semantic-parallax replay with opt-in
`source_entity_ledger_v1`, compact focused-pass operations schema, and the
same no-oracle fixture discipline. No gold KB, strategy file, ontology
registry, or QA source was used during compilation.

Operational note: the first attempt accidentally passed LM Studio base URL as
`http://127.0.0.1:1234/v1` to `run_domain_bootstrap_file.py` and produced an
empty profile response. Rerunning with `http://127.0.0.1:1234` worked. This is
recorded in `AGENT-README.md` for future sessions.

Artifacts:

- Compile:
  `tmp/diagnostic_replays/three_moles_mmm005/domain_bootstrap_file_20260503T205739863995Z_story_qwen-qwen3-6-35b-a3b.json`
- Plain QA:
  `tmp/diagnostic_replays/three_moles_mmm005/domain_bootstrap_qa_20260503T210521403805Z_qa_qwen-qwen3-6-35b-a3b.json`
- Evidence-filter QA:
  `tmp/diagnostic_replays/three_moles_mmm005/domain_bootstrap_qa_20260503T211629744776Z_qa_qwen-qwen3-6-35b-a3b.json`
- Mode comparison:
  `tmp/diagnostic_replays/three_moles_mmm005/mmm005_query_mode_comparison.md`
- Selector:
  `tmp/diagnostic_replays/three_moles_mmm005/selector_direct_v1.json`

Result:

- Compile: `193` admitted operations, `9` skips.
- Plain QA: `16 exact / 7 partial / 17 miss`.
- Evidence-filter QA: `18 exact / 5 partial / 17 miss`.
- Diagnostic perfect-selector upper bound across plain/evidence-filter:
  `20 exact / 5 partial / 15 miss`.
- Direct selector: `16 exact / 7 partial / 17 miss`.

Lesson:

This is the first positive source-ledger handoff transfer on a story fixture.
Earlier Otters ledger probes were too timid; Three Moles shows that the ledger
can materially improve the compile surface when the later passes cash it in.
Evidence filtering stacks on top for exact count, but selector activation still
fails over this thin story surface.

The next story-world compiler target is not "more query filtering." It is a
stronger ledger-to-pass contract:

```text
ledger object/entity families
  -> required static rows
  -> required event-spine rows
  -> required state-change/final-state rows
```

without Python deriving any of those rows from prose.

## MMM-006 - Ledger Coverage Targets

Date: 2026-05-04

Evidence lane: `cold_after_general_architecture_change`

Mode: source-only semantic-parallax replay with `source_entity_ledger_v1`
extended to include powerless `coverage_targets`. No gold KB, strategy file,
ontology registry, or QA source was used during compilation.

Artifacts:

- Compile:
  `tmp/diagnostic_replays/three_moles_mmm006/domain_bootstrap_file_20260504T010911557261Z_story_qwen-qwen3-6-35b-a3b.json`
- Plain QA:
  `tmp/diagnostic_replays/three_moles_mmm006/domain_bootstrap_qa_20260504T011617838520Z_qa_qwen-qwen3-6-35b-a3b.json`
- Evidence-filter QA:
  `tmp/diagnostic_replays/three_moles_mmm006/domain_bootstrap_qa_20260504T012609486033Z_qa_qwen-qwen3-6-35b-a3b.json`
- Mode comparison:
  `tmp/diagnostic_replays/three_moles_mmm006/mmm006_query_mode_comparison.md`
- Selector:
  `tmp/diagnostic_replays/three_moles_mmm006/selector_direct_v1.json`

Result:

- Compile: `170` admitted operations, `0` skips, `156` unique facts, `8`
  ledger coverage targets.
- Compile health: `poor` because the flat skeleton produced `0` rows, but
  focused passes still produced a useful surface.
- Plain QA: `21 exact / 6 partial / 13 miss`.
- Evidence-filter QA: `20 exact / 6 partial / 14 miss`.
- Diagnostic perfect-selector upper bound: `25 exact / 4 partial / 11 miss`.
- Direct selector: `23 exact / 4 partial / 13 miss`.

Lesson:

Coverage targets worked as a story-world compile lever. MMM-006 beat MMM-005
plain QA (`16/7/17`) and evidence-filter QA (`18/5/17`) without adding oracle
context. The remaining problem was visible in the trace: the flat skeleton
rejected itself because preferred narrative predicates from guidance were not
present in the draft palette, even though nearby allowed predicates existed.

## MMM-007 - Scoped Partial-Skeleton Recovery

Date: 2026-05-04

Evidence lane: `cold_after_general_architecture_change`

Mode: same as MMM-006, plus a scoped ledger-backed instruction that missing
illustrative narrative predicates should not collapse an entire pass when
compatible allowed predicates can still preserve a partial skeleton.

Artifacts:

- Compile:
  `tmp/diagnostic_replays/three_moles_mmm007/domain_bootstrap_file_20260504T013300268220Z_story_qwen-qwen3-6-35b-a3b.json`
- Plain QA:
  `tmp/diagnostic_replays/three_moles_mmm007/domain_bootstrap_qa_20260504T014005277734Z_qa_qwen-qwen3-6-35b-a3b.json`
- Evidence-filter QA:
  `tmp/diagnostic_replays/three_moles_mmm007/domain_bootstrap_qa_20260504T014959553156Z_qa_qwen-qwen3-6-35b-a3b.json`
- Mode comparison:
  `tmp/diagnostic_replays/three_moles_mmm007/mmm007_query_mode_comparison.md`
- Selector:
  `tmp/diagnostic_replays/three_moles_mmm007/selector_direct_v1.json`

Result:

- Compile: `218` admitted operations, `4` skips, `172` unique facts.
- Compile health: `healthy`.
- Flat skeleton contribution: `64` rows, up from `0` in MMM-006.
- Plain QA: `20 exact / 5 partial / 15 miss`.
- Evidence-filter QA: `24 exact / 6 partial / 10 miss`.
- Diagnostic perfect-selector upper bound: `26 exact / 5 partial / 9 miss`.
- Direct selector: `21 exact / 7 partial / 12 miss`.
- Completeness selector: `21 exact / 8 partial / 11 miss`.
- Relevance selector: `21 exact / 7 partial / 12 miss`.
- Structural selector: `24 exact / 4 partial / 12 miss`.

Lesson:

Waking up the flat skeleton improved the compiled surface but did not improve
plain QA by itself. The payoff appeared when evidence filtering had a richer
surface to retrieve from: `24/6/10` is the current Three Moles high-water.

The selector regressed relative to the global evidence-filter mode, which means
row-level activation still under-recognizes when a richer evidence bundle should
be trusted. Prompt-only selector variants did not solve it: completeness reduced
misses by one but did not improve exact count, and relevance matched the direct
selector. A deterministic structural selector matched the global evidence-filter
exact count without an LLM selector call, but with two more misses than global
evidence-filter. The useful architecture lesson is:

```text
ledger coverage targets -> broader safe surface
broader safe surface -> better evidence-filter retrieval
row selector still needs better pre-judge activation signals
```

## MMM-008 - Final Object-State Lens Transfer Diagnostic

Date: 2026-05-05

Evidence lane: `state_lens_transfer`

Mode: Larkspur-derived `final_object_state_transition_surface` compile over
Three Moles, followed by targeted QA on final location, reveal, condition,
recovery, restitution, and end-state rows.

Artifacts:

- Compile:
  `tmp/state_lens_transfer/three_moles_final_state_20260505/domain_bootstrap_file_20260505T140237039803Z_source_qwen-qwen3-6-35b-a3b.json`
- Targeted QA:
  `tmp/state_lens_transfer/three_moles_final_state_targeted_qa_20260505/domain_bootstrap_qa_20260505T141022223202Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

```text
compile:              56 admitted / 51 skipped
targeted rows:        9
targeted QA:          0 exact / 2 partial / 7 miss
failure surfaces:     8 compile-surface gaps, 1 hybrid-join gap
write proposals:      0
runtime load errors:  0
```

Lesson:

Negative transfer. The Larkspur state lens does not recover the Three Moles
event-spine/restitution ending by itself. Three Moles still needs the broader
ledger/event-spine surface from MMM-007 rather than a narrow final-state prompt.

## MMM-009 - Current Harness Replay and Micro-Detail Negative Probe

Date: 2026-05-06

Evidence lane: `source_surface_acquisition_frontier`

Mode: current flat-plus-focused story-world compile with markdown answer-key
judging and failure-surface classification. The follow-up micro-detail probe
added a broad narrative instruction to preserve whimsical distractions, odd
object actions, tool/manner details, pretend roles, and morals. No gold KB,
oracle rows, or QA-derived compile context was used.

Artifacts:

- Current-harness compile:
  `tmp/story_world_cold_runs/three_moles_moon_marmalade_machine/domain_bootstrap_file_20260506T051635702903Z_source_qwen-qwen3-6-35b-a3b.json`
- Current-harness QA:
  `tmp/story_world_cold_qa/three_moles_moon_marmalade_machine/domain_bootstrap_qa_20260506T055258954404Z_qa_qwen-qwen3-6-35b-a3b.json`
- Micro-detail compile:
  `tmp/story_world_cold_runs/three_moles_moon_marmalade_machine_microdetail/domain_bootstrap_file_20260506T055735050592Z_source_qwen-qwen3-6-35b-a3b.json`
- Micro-detail QA:
  `tmp/story_world_cold_qa/three_moles_moon_marmalade_machine_microdetail/domain_bootstrap_qa_20260506T060918313540Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

```text
current harness:
  compile: 275 admitted / 8 skipped
  QA:      27 exact / 4 partial / 9 miss
  failures: 10 compile, 1 hybrid, 2 answer

micro-detail broad prompt:
  compile: 192 admitted / 29 skipped
  QA:      16 exact / 9 partial / 15 miss
  failures: 19 compile, 2 hybrid, 1 query, 2 answer
```

Lesson:

Rejected as a global narrative prompt. The problem is real: Three Moles still
misses fine-grained source details such as early distractions, odd cart actions,
jar contents, pretend-role speech, tool/manner details, and the explicit moral.
But naming all of those as a broad compile instruction made the profile thinner
and increased misses. The next attempt should be row-gated or artifact-level:
compare the successful broad ledger/event-spine surface against a narrow detail
variant and select only rows it actually rescues, rather than making
micro-detail coverage a default narrative lens.

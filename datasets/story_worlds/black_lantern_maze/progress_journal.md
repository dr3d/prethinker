# Black Lantern Maze Progress Journal

Fixture id: `black_lantern_maze_v1`

This is the running research record for the Black Lantern Maze fixture.

## BLM-000 - Fixture Admission

Date: 2026-05-03

Source: `tmp/The Black Lantern Maze/`

Files admitted:

- `story.md` / `source.md`
- `gold_kb.pl`
- `qa.md` / `qa_source.md`
- `ambiguity_and_chaos_overlay.md`
- `intake_plan.md` / `gold_kb_notes.md`
- `failure_buckets.json`
- `progress_journal.md`
- `progress_metrics.jsonl`

No model run was executed.

Benchmark discipline:

- `gold_kb.pl` is oracle-only.
- `qa.md`, `qa_source.md`, and `ambiguity_and_chaos_overlay.md` are scoring
  and challenge assets, not source-compilation context.
- `intake_plan.md` / `gold_kb_notes.md` are supplied strategy notes and should
  be kept out of cold-run claims.
- No non-oracle starter ontology registry is included yet.

Expected research value:

- Combines Glass Tide rule-ingestion pressure with CE blocked-slot pressure.
- Adds heavier identity/alias/title-time confusion than Iron Harbor.
- Adds approval-semantics overload as a direct CE and predicate-surface trap.
- Keeps claim/finding/fact separation central rather than decorative.

## BLM-001 - Cold Semantic Parallax Baseline

Date: 2026-05-03

Evidence lane: `cold_unseen`

Mode: source-only profile bootstrap plus current semantic-parallax compile:
flat-plus-focused intake-plan passes, compact focused-pass operations schema,
and LLM-authored source entity ledger. The fixture contains oracle materials,
but they were not used during compilation or QA.

Artifacts:

- Compile:
  `tmp/cold_baselines/black_lantern_maze/domain_bootstrap_file_20260503T055307250452Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/black_lantern_maze/domain_bootstrap_qa_20260503T060152766469Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Compile: `299` admitted operations, `28` skips, `299` unique facts, `0`
  rules.
- QA: `27 exact / 7 partial / 6 miss` over `40` questions.
- Safety: `40/40` parsed, `39/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `7` compile-surface gaps, `6` hybrid-join gaps.

Lesson:

Black Lantern is the strongest 40-question cold baseline in this batch. It
suggests the current semantic-parallax compile can build a broad source surface
when the document shape matches the policy/maze/governance lessons learned from
recent fixtures, even without opening the local oracle materials.

## BLM-002 - Evidence-Bundle Context Filtering Replay

Date: 2026-05-03

Evidence lane: `cold_after_general_architecture_change`

Mode: post-ingestion QA replay over the unchanged BLM-001 compile, with
`evidence_bundle_plan_v1` and evidence-bundle context filtering enabled. This
did not recompile the source and did not expose the oracle KB or supplied
strategy notes.

Artifacts:

- Compile reused:
  `tmp/cold_baselines/black_lantern_maze/domain_bootstrap_file_20260503T055307250452Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/diagnostic_replays/black_lantern_blm002/domain_bootstrap_qa_20260503T130201865280Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Compile: unchanged from BLM-001, `299` unique facts, `0` rules.
- QA: `32 exact / 3 partial / 5 miss` over `40` questions.
- Delta from BLM-001: `+5` exact, `-4` partial, `-1` miss.
- Safety: `40/40` parsed, `39/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `4` compile-surface gaps, `4` hybrid-join gaps.

Changed rows:

- Improved to exact: q007, q011, q015, q016, q035, q037.
- Regressed: q021 partial -> miss; q040 exact -> partial.

Lesson:

BLM-002 confirms the Veridia V9-003 result on a second cold fixture:
post-ingestion query choreography can extract more value from the same admitted
KB surface. The gains are real, but so is volatility. Evidence-bundle context
filtering should remain a measured replay/query strategy until the harness can
predict which rows benefit and which rows risk losing already-good support.

## BLM-003 - Broader Evidence-Bundle Context Floor

Date: 2026-05-03

Evidence lane: `cold_after_general_architecture_change`

Mode: post-ingestion QA replay over the unchanged BLM-001 compile with
evidence-bundle context filtering, but a broader fallback surface:
`max_clauses=320`, `broad_floor=160`.

Artifacts:

- Compile reused:
  `tmp/cold_baselines/black_lantern_maze/domain_bootstrap_file_20260503T055307250452Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/diagnostic_replays/black_lantern_blm003/domain_bootstrap_qa_20260503T131707556205Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Compile: unchanged from BLM-001, `299` unique facts, `0` rules.
- QA: `32 exact / 5 partial / 3 miss` over `40` questions.
- Delta from BLM-001: `+5` exact, `-2` partial, `-3` miss.
- Delta from BLM-002: same exact count, `+2` partial, `-2` miss.
- Safety: `40/40` parsed, `40/40` query rows, `0` write-proposal rows, `0`
  runtime load errors.

Changed rows versus BLM-001:

- Improved to exact: q007, q011, q015, q016, q036, q037.
- Improved to partial: q022.
- Regressed: q040 exact -> partial.

Changed rows versus BLM-002:

- Recovered from miss to partial: q021, q022.
- Improved from miss to exact: q036.
- Regressed from exact to miss: q035.

Lesson:

The broader floor keeps BLM-002's exact-count gain while reducing hard misses.
It does not eliminate volatility: q035 was exact under the narrower filter and
missed under the broader one. The immediate design lesson is that the evidence
filter needs a row-level activation policy, not just a global clause budget.
Still, `32/5/3` is a better diagnostic posture than `32/3/5` because more
failure cases remain partially supported instead of collapsing to miss.

## BLM-004 - Evidence Mode Selector Negative Transfer

Date: 2026-05-03

Evidence lane: `diagnostic_replay`

Mode: replayed the BLM-002 and BLM-003 query-surface modes after the
Avalon AG-007 selector result, then ran the non-oracle evidence-mode selector
over baseline, narrow evidence filtering, and broad evidence filtering.

Artifacts:

- Narrow QA replay:
  `tmp/cold_baselines/black_lantern_maze/query_modes_replay/domain_bootstrap_qa_20260503T190819241354Z_qa_qwen-qwen3-6-35b-a3b.json`
- Broad QA replay:
  `tmp/cold_baselines/black_lantern_maze/query_modes_broad_replay/domain_bootstrap_qa_20260503T191952027537Z_qa_qwen-qwen3-6-35b-a3b.json`
- Mode comparison:
  `tmp/cold_baselines/black_lantern_maze/query_modes_broad_replay/black_lantern_mode_comparison_replay.md`
- Selector:
  `tmp/cold_baselines/black_lantern_maze/query_modes_broad_replay/selector_full_sample16.json`
- Selector with self-check notes:
  `tmp/cold_baselines/black_lantern_maze/query_modes_broad_replay/selector_full_selfcheck_sample16.json`

Result:

Mode scores:

```text
baseline: 27 exact / 7 partial / 6 miss
narrow:   32 exact / 3 partial / 5 miss
broad:    32 exact / 5 partial / 3 miss
```

Diagnostic perfect-selector upper bound:

```text
33 exact / 4 partial / 3 miss
```

Non-oracle selector:

```text
28 exact / 9 partial / 3 miss
selected best available mode on 35/40 rows
```

Selector with QA self-check notes added:

```text
29 exact / 7 partial / 4 miss
selected best available mode on 35/40 rows
```

Lesson:

The Avalon selector result transfers as a mechanism but not yet as a robust
policy. On Black Lantern, the selector overvalued direct-looking but incomplete
baseline evidence for rows q007, q011, q015, and q016, all of which were exact
under both evidence-filtered modes. Adding QA self-check notes improved exact
count by one but added a miss, so self-check context is not a clean fix.

This is a useful negative result. Row-level activation needs calibration across
fixture types before it becomes default. The selector must learn evidence
completeness, not just evidence directness.

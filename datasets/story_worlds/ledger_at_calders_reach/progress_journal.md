# The Ledger at Calder's Reach Progress Journal

## Fixture Admission - CAL-000

- Timestamp: `2026-05-03`
- Source: `tmp/The Ledger at Calder's Reach`
- Files admitted: source story plus extracted 110-question QA file.
- Gold KB: none admitted.
- Starter ontology/profile: none admitted.
- Benchmark runs: none yet.

### Oracle Boundary

The supplied QA source contained extra canonical inventories, suggested
predicate families, snapshots, gold triples, and scoring notes. Those were not
copied into this fixture. Only the Q/A pairs were extracted for post-ingestion
scoring.

### Purpose

This fixture is intended to test governed compilation of a long evolving story
with overlapping legal, family, role, residence, trust, inheritance, and
boundary-state changes.

No run has been executed at admission time.

## Run CAL-001 - Cold Semantic Parallax Baseline

- Timestamp: `2026-05-03T05:23Z` through `2026-05-03T05:45Z`
- Evidence lane: `cold_unseen`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: source-only profile bootstrap plus current semantic-parallax compile:
  flat-plus-focused intake-plan passes, compact focused-pass operations schema,
  and LLM-authored source entity ledger. No gold KB, starter registry, or QA
  source was used during compilation.

### Artifacts

- Compile:
  `tmp/cold_baselines/ledger_at_calders_reach/domain_bootstrap_file_20260503T052338731954Z_story_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/cold_baselines/ledger_at_calders_reach/domain_bootstrap_qa_20260503T054553171055Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

- Compile: `187` admitted operations, `23` skips, `180` unique facts, `0`
  rules.
- QA: `65 exact / 9 partial / 36 miss` over `110` questions.
- Safety: `109/110` parsed, `108/110` query rows, `0` write-proposal rows, `0`
  runtime load errors.
- Failure surfaces: `37` compile-surface gaps, `6` query-surface gaps, `2`
  hybrid-join gaps.

### Lesson

Calder's Reach is the strongest cold long-story signal so far. The current
pipeline handles many state-at-time and identity questions without oracle
material, but the misses still cluster around missing compiled support and a
few query-surface failures. This should become the main anti-meta-rot story
fixture for long-range state tracking.

## Run CAL-002 - Final State Lens Transfer Diagnostic

- Timestamp: `2026-05-05T14:03Z` through `2026-05-05T14:15Z`
- Evidence lane: `state_lens_transfer`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: Larkspur-derived `final_object_state_transition_surface` variant
  narrowed for final ownership, custody, residence, role, trust/admin, and
  carried-versus-owned rows, followed by targeted QA.

### Artifacts

- Compile:
  `tmp/state_lens_transfer/calders_final_state_20260505/domain_bootstrap_file_20260505T140303209218Z_source_qwen-qwen3-6-35b-a3b.json`
- Targeted QA:
  `tmp/state_lens_transfer/calders_final_state_targeted_qa_20260505/domain_bootstrap_qa_20260505T141524873700Z_qa_qwen-qwen3-6-35b-a3b.json`

### Result

```text
compile:              89 admitted / 36 skipped
targeted rows:        20
targeted QA:          10 exact / 2 partial / 8 miss
failure surfaces:     9 compile-surface gaps, 1 hybrid-join gap
write proposals:      0
runtime load errors:  0
```

### Lesson

Mixed transfer. The lens can answer some final ownership, residence, trust, and
carried-versus-owned questions, but it preserves stale current-state conflicts
on mayor, Dock 7, Iain's role, and Jonas residence. Calder needs a
correction/current-state conflict lens, not just final-state extraction.

## Run CAL-003 - Current-State Conflict Overlay

- Timestamp: `2026-05-05T14:48Z` through `2026-05-05T15:15Z`
- Evidence lane: `state_conflict_selector_overlay`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: four narrow source-bound surfaces over the same 20-row final/current
  state slice: final-state, current-state conflict, possession/inheritance, and
  legal-title/default.

### Artifacts

- Current-state conflict compile:
  `tmp/state_conflict_lens/calders_current_conflict_20260505/domain_bootstrap_file_20260505T144843688670Z_source_qwen-qwen3-6-35b-a3b.json`
- Current-state conflict QA:
  `tmp/state_conflict_lens/calders_current_conflict_targeted_qa_20260505/domain_bootstrap_qa_20260505T145330261788Z_qa_qwen-qwen3-6-35b-a3b.json`
- Possession/inheritance compile:
  `tmp/state_conflict_lens/calders_possession_inheritance_20260505/domain_bootstrap_file_20260505T150113635745Z_source_qwen-qwen3-6-35b-a3b.json`
- Possession/inheritance QA:
  `tmp/state_conflict_lens/calders_possession_inheritance_targeted_qa_20260505/domain_bootstrap_qa_20260505T151010205938Z_qa_qwen-qwen3-6-35b-a3b.json`
- Legal-title/default compile:
  `tmp/state_conflict_lens/calders_legal_title_default_20260505/domain_bootstrap_file_20260505T150055572000Z_source_qwen-qwen3-6-35b-a3b.json`
- Legal-title/default QA:
  `tmp/state_conflict_lens/calders_legal_title_default_targeted_qa_20260505/domain_bootstrap_qa_20260505T150933998374Z_qa_qwen-qwen3-6-35b-a3b.json`
- Four-surface comparison:
  `tmp/state_conflict_lens/calders_four_surface_comparison_20260505.md`
- Final guarded selector:
  `tmp/state_conflict_lens/calders_four_surface_guarded_selector_refined_guards_20260505.json`

### Result

```text
final-state surface:             10 exact / 2 partial / 8 miss
current-conflict surface:         6 exact / 2 partial / 12 miss
possession/inheritance surface:  10 exact / 1 partial / 9 miss
legal-title/default surface:      6 exact / 2 partial / 12 miss
four-surface upper bound:        14 exact / 3 partial / 3 miss
guarded selector before guards:   9 exact / 2 partial / 9 miss
guarded selector after guards:   14 exact / 3 partial / 3 miss
selected-best rows:              20/20
selector errors:                 0
```

New reason-named selector guards:

- `role_reinstatement_history_guard`
- `carry_possession_surface_guard`
- `possession_ownership_distinction_guard`
- `legal_title_transfer_guard`
- `contract_authority_surface_guard`
- `guardianship_resumption_condition_guard`

### Lesson

Calder confirms the Larkspur pattern on a very different long-state ledger: a
single compact lens is not the product. The useful shape is persisted semantic
surfaces plus row-level routing. Current-state conflict alone was weaker than
final-state extraction, but it supplied critical reinstatement/title rows.
Possession/inheritance supplied carry-versus-own and non-retroactive inheritance
rows. The selector reached the artifact upper bound only after the guards were
named by answer surface rather than by fixture row.

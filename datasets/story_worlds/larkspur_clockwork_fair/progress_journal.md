# Larkspur Clockwork Fair Progress Journal

Fixture id: `larkspur_clockwork_fair`

This journal records durable research findings for the Larkspur incoming
fixture. Generated run artifacts may live under `tmp/`; the lessons and artifact
references belong here.

## LCF-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming_staged/larkspur_clockwork_fair`

Files admitted:

- `source.md` / `story.md`
- `fixture_notes.md`
- `qa.md`
- `qa_questions.jsonl`
- `oracle.jsonl`
- `qa_authored_with_answers.jsonl`

Benchmark discipline:

- `source.md`/`story.md` is the only cold compile source.
- `oracle.jsonl`, `qa_authored_with_answers.jsonl`, `qa.md`, and
  `fixture_notes.md` are scoring/review assets, not compile context.
- No Python source-prose interpretation is allowed.

## LCF-001 - Incoming First-10 Smoke

Date: 2026-05-04

Evidence lane: `cold_unseen`

Mode: incoming standard first-10 smoke.

Artifacts:

- Baseline scorecard: `tmp/incoming_smoke_summaries/scorecard.md`
- Scoped-evidence scorecard: `tmp/incoming_smoke_summaries_scoped_evidence/scorecard.md`

Result:

- Compile: `195` admitted operations, `1` skip.
- Compile health: `healthy`.
- QA first-10: `8 exact / 2 partial / 0 miss`.
- Non-exacts: q007 youngest exhibitor and q009 Fair Warden identity.
- Safety: `0` write-proposal rows.

Lesson:

The cold compile captured the broad story surface but had right-shaped/wrong-slot
gaps around numeric character attributes and named-official duty/authority.

## LCF-002 - Attribute/Duty Guardrail And Official Companion

Date: 2026-05-04

Evidence lane: `diagnostic_replay`

Mode: narrative compile guardrail plus post-ingestion official-identity
companion query.

Artifacts:

- Attribute/duty compile:
  `tmp/incoming_cold_runs/larkspur_clockwork_fair_attribute_duty_guardrail_repair/domain_bootstrap_file_20260504T151723343869Z_source_qwen-qwen3-6-35b-a3b.json`
- Companion QA first-10:
  `tmp/incoming_cold_qa/larkspur_clockwork_fair_attribute_duty_guardrail_companion_first10/domain_bootstrap_qa_20260504T152559315473Z_qa_qwen-qwen3-6-35b-a3b.json`
- Overlay plan:
  `tmp/incoming_smoke_summaries_official_companion_overlay/compile_variant_overlay_plan.md`

Result:

- Guarded compile health: `poor`; not a global promotion.
- Companion first-10: `9 exact / 0 partial / 1 miss`.
- Rescued rows: q007 and q009.
- Regression: q010 exact -> miss in the guarded compile variant.

Lesson:

The compiler guardrail is useful row-level lensing, not a replacement compile.
The QA companion repaired official identity by querying admitted authority/action
surface for `person_role(Constant, Role)` rows. Exact-row protection must keep
q010 on baseline.

## LCF-003 - Variant Selector Calibration

Date: 2026-05-04

Evidence lane: `selector_calibration`

Artifacts:

- Variant selector training plan:
  `tmp/incoming_smoke_summaries_official_companion_overlay/variant_selector_training_plan.md`
- Volume-gate selector comparison:
  `tmp/incoming_variant_selector_runs/incoming-variant-volume-gate-v2.md`

Result:

- Larkspur activation targets: q007 and q009.
- Larkspur exact-protection target: q010.
- Guarded activation plus volume gate selected `3/3` best Larkspur rows.

Lesson:

Larkspur is now a compact selector calibration fixture: activate the
attribute/duty companion for youngest-exhibitor and official-identity rows, but
protect the baseline recovery-event row.

## LCF-004 - Requirement-Detail Selector Replay

Date: 2026-05-04

Evidence lane: `selector_calibration`

Artifact:

- `tmp/incoming_variant_selector_runs/larkspur_guarded_activation_requirement_detail.json`

Result:

- Larkspur held `3/3` best choices under the requirement-detail selector replay.

Lesson:

The requirement-detail guard did not perturb the Larkspur calibration rows.

## LCF-005 - Full First-10 Variant Selector Replay

Date: 2026-05-04

Evidence lane: `selector_calibration`

Artifact:

- `tmp/incoming_variant_selector_runs/larkspur_guarded_activation_requirement_detail_first10.json`

Result:

- Larkspur first-10 selected `10/10` best choices.
- QA verdict through selected modes: `10 exact / 0 partial / 0 miss`.
- Selector errors: `0`.

Lesson:

The row-gated selector can safely combine the Larkspur baseline and
attribute/duty companion views across the whole first-10 slice.

## LCF-006 - Promoted Story-World Full-40 Run

Date: 2026-05-04

Evidence lane: `cold_unseen_full40`

Mode: promoted story-world cold compile plus evidence-bundle QA, followed by
failure-surface classification for non-exact rows.

Artifacts:

- Scorecard: `tmp/story_world_full40_classified_scorecards/scorecard.md`
- Repair targets: `tmp/story_world_full40_classified_scorecards/compile_repair_targets.md`

Result:

- Compile: `174` admitted operations, `41` skips.
- Compile health: `healthy`; profile scoring still flagged unknown
  `event_record/2` risk in the compile output.
- QA full-40 after classification merge: `20 exact / 7 partial / 13 miss`.
- Failure surfaces: `20` compile-surface gaps.
- Safety: `0` write-proposal rows.

Lesson:

Larkspur is the current story-world generalization frontier. First-10 row-gated
selection worked, but full-40 reveals broader missing source surface around
object state, custody, repair/permission rationale, motive, and final-state
questions. The next repair should be a scoped source-surface pass for event
state transitions and causal chains, not a broader selector prompt.

## LCF-007 - State/Custody Ledger Variant

Date: 2026-05-04

Evidence lane: `negative_diagnostic`

Mode: source-entity-ledger compile with explicit state/custody/rationale domain
hint.

Artifacts:

- Compile:
  `tmp/story_world_cold_runs/larkspur_state_custody_rationale_ledger/domain_bootstrap_file_20260504T173945847618Z_source_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/story_world_cold_qa/larkspur_state_custody_rationale_ledger_full40/domain_bootstrap_qa_20260504T175018471860Z_qa_qwen-qwen3-6-35b-a3b.json`
- Comparison:
  `tmp/story_world_larkspur_state_custody_variant/larkspur_baseline_comparison.md`

Result:

- Compile shape improved: `149` admitted operations, `1` skip, profile score
  `1.0`, and no unknown predicate refs.
- QA full-40 regressed: `18 exact / 10 partial / 12 miss`.
- Baseline comparison: `reject_candidate`, `7` baseline-exact regressions.
- Failure surfaces: `17` compile-surface gaps, `4` helper/query-join gaps,
  `1` answer-surface gap.
- Safety: `0` write-proposal rows.

Lesson:

Cleaner compile shape is not enough. The source-entity ledger and broad
state/custody/rationale hint reduced mapper noise but did not preserve the
right answer-bearing rows. The next Larkspur repair needs narrower source
passes for specific object-state transitions, custody chain, and permission
rationale rows, with exact-row protection from the current full-40 baseline.

## LCF-008 - Targeted-State Row-Gated Selector

Date: 2026-05-04

Evidence lane: `selector_calibration_full40`

Mode: narrower targeted state-transition/custody/rationale compile variant,
then guarded activation with identity-completeness uncertainty gate.

Artifacts:

- Variant overlay:
  `tmp/story_world_larkspur_targeted_state_variant/compile_variant_overlay_plan.md`
- Selector replay:
  `tmp/story_world_larkspur_targeted_state_variant/guarded_activation_selector_identity_gate_full40.md`

Result:

- Targeted compile alone is unsafe globally: `14 exact / 8 partial / 18 miss`.
- Judged row overlay target: `23 exact / 6 partial / 11 miss`; `4` accepted
  variant rows, `9` protected baseline-exact rows.
- Non-oracle selector result: `23 exact / 7 partial / 10 miss`.
- Selector selected best available mode on `38/40` rows.
- Selector errors: `0`.
- Remaining missed-best rows: q023 and q029, both baseline partial versus
  targeted-state miss.

Lesson:

The targeted-state lens is a useful full-40 row variant, not a replacement
compile. The new identity-completeness selector gate fixed the Fair Warden
q009 protection case by refusing to let authority-row volume outrank explicit
name/identity support. The remaining selector frontier is protecting partial
baseline rationale rows when a variant has more but less answer-bearing event
surface.

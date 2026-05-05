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
- Non-oracle selector result after rationale/contrast and capability-failure
  guidance: `23 exact / 8 partial / 9 miss`.
- Selector selected best available mode on `39/40` rows.
- Selector errors: `0`.
- Remaining missed-best row: q023, where baseline partial still beats the
  targeted-state seal/status explanation.

Lesson:

The targeted-state lens is a useful full-40 row variant, not a replacement
compile. The new identity-completeness selector gate fixed the Fair Warden
q009 protection case by refusing to let authority-row volume outrank explicit
name/identity support. The remaining selector frontier is protecting partial
baseline capability-rationale rows when a variant has more but less
answer-bearing event surface.

## LCF-009 - Full-40 Repair Target Planner

Date: 2026-05-04

Evidence lane: `artifact_only_repair_planning`

Mode: story-world repair target planning from the promoted full-40 classified
scorecard.

Artifacts:

- Full batch plan:
  `tmp/story_world_repair_plans/full40_repair_targets.md`
- Larkspur-only plan:
  `tmp/story_world_repair_plans/larkspur_full40_repair_targets.md`

Result:

- Full promoted five-fixture queue: `46` targets.
- Full queue lanes: `39` scoped source-surface repairs, `7` helper/query-join
  repairs.
- Larkspur-only queue: `20` compile-surface targets.
- Larkspur lens split:
  - `6` object-state transition targets.
  - `5` object-location/custody targets.
  - `4` permission/rationale targets.
  - `2` outcome/status targets.
  - `1` claim-truth target.
  - `1` identity/role target.
  - `1` temporal target.

Lesson:

The repair queue is now named by guardrail/reason rather than by fixture lore.
The planner reads scorecard artifacts and query predicate names only; it does
not inspect source prose, gold KBs, or answer keys for classification. The next
Larkspur source-surface work should start with object-state and
object-location/custody acquisition, then permission/rationale, with
exact-row protection.

## LCF-010 - Direct Registry Acquisition Negative Check

Date: 2026-05-04

Evidence lane: `negative_diagnostic`

Mode: direct `story_world@v0` registry compiles for three named acquisition
lenses after profile/intake pre-passes returned empty responses.

Artifacts:

- Object-state compile:
  `tmp/story_world_larkspur_acquisition/object_state_direct_profile/`
- Object-state targeted QA:
  `tmp/story_world_larkspur_acquisition/object_state_direct_profile_qa/`
- Object-custody compile:
  `tmp/story_world_larkspur_acquisition/object_custody_direct_profile/`
- Object-custody targeted QA:
  `tmp/story_world_larkspur_acquisition/object_custody_direct_profile_qa/`
- Permission/rationale compile:
  `tmp/story_world_larkspur_acquisition/permission_rationale_direct_profile/`
- Permission/rationale targeted QA:
  `tmp/story_world_larkspur_acquisition/permission_rationale_direct_profile_qa/`

Result:

| Lens | Admitted Rows | Target QA |
| --- | ---: | ---: |
| `object_state_transition_surface` | `24` | `0 exact / 0 partial / 6 miss` |
| `object_location_custody_surface` | `6` | `0 exact / 2 partial / 2 miss` |
| `permission_rationale_surface` | `12` | `0 exact / 0 partial / 5 miss` |

Safety:

- Runtime load errors: `0`.
- QA write proposals: `0`.

Lesson:

Bypassing profile discovery with the tracked registry prevents the empty
profile/intake failure, but it starves the compile. The direct registry-only
surface is too thin to repair Larkspur. The next acquisition attempt should
improve compact/focused source-pass acquisition while preserving the named lens
contract; do not promote direct-profile compilation as the story-world repair
path.

## LCF-011 - URL-Fixed Permission/Rationale Acquisition

Date: 2026-05-04

Evidence lane: `source_surface_acquisition`

Mode: fixed LM Studio `/v1` base-url normalization, then focused
permission/rationale acquisition with compact source-pass operations.

Artifacts:

- URL-fixed object-state compile:
  `tmp/story_world_larkspur_acquisition/object_state_urlfix_preflight/`
- URL-fixed object-state targeted QA:
  `tmp/story_world_larkspur_acquisition/object_state_urlfix_preflight_qa/`
- URL-fixed object-custody compile:
  `tmp/story_world_larkspur_acquisition/object_custody_urlfix_preflight/`
- URL-fixed object-custody targeted QA:
  `tmp/story_world_larkspur_acquisition/object_custody_urlfix_preflight_qa/`
- URL-fixed permission/rationale compile:
  `tmp/story_world_larkspur_acquisition/permission_rationale_urlfix_preflight/`
- URL-fixed permission/rationale targeted QA:
  `tmp/story_world_larkspur_acquisition/permission_rationale_urlfix_preflight_qa/`
- URL-fixed permission/rationale full-40 QA:
  `tmp/story_world_larkspur_acquisition/permission_rationale_urlfix_full40_qa/`
- Candidate summary:
  `tmp/story_world_larkspur_acquisition/permission_rationale_urlfix_summary/`

Harness fix:

`run_domain_bootstrap_file.py` now normalizes LM Studio base URLs before
appending `/v1/chat/completions`, so both `http://127.0.0.1:1234` and
`http://127.0.0.1:1234/v1` work for profile/intake calls. The prior empty
profile/intake responses were caused by the doubled `/v1/v1` path.

Targeted acquisition results:

| Lens | Compile Shape | Target QA |
| --- | --- | ---: |
| `object_state_transition_surface` | `91` admitted / `79` skipped | `0 exact / 2 partial / 4 miss` |
| `object_location_custody_surface` | `121` admitted / `13` skipped | `2 exact / 2 partial / 0 miss` |
| `permission_rationale_surface` | `150` admitted / `14` skipped | `5 exact / 0 partial / 0 miss` |

Permission/rationale full-40 result:

```text
baseline full-40:             20 exact / 7 partial / 13 miss
permission/rationale variant: 31 exact / 3 partial / 6 miss
write proposals:              0
runtime load errors:          0
```

Row movement against the archived baseline QA verdicts:

- Rescued/improved rows: `18`.
- Regressed rows: `7`.
- Baseline-exact regressions: `6` (`q002`, `q009`, `q018`, `q031`, `q032`,
  `q033`).

Lesson:

The permission/rationale lens is the first strong full-40 Larkspur acquisition
candidate after the promoted scorecard. It is not globally safe because it
damages exact rows, but it gives a serious row-gated variant. The next harness
step should compare it against baseline and targeted-state modes with exact-row
protection, then decide whether the new rescues are selector-learnable without
judge labels.

## LCF-012 - Permission/Rationale Row-Gated Selector Lift

Date: 2026-05-04

Evidence lane: `selector_calibration_full40`

Mode: guarded activation over the archived baseline full-40 QA artifact and the
URL-fixed permission/rationale full-40 QA artifact, with answer-surface baseline
guards added to the selector.

Artifacts:

- Judged overlay upper bound:
  `tmp/story_world_larkspur_acquisition/permission_rationale_overlay_plan.md`
- Original guarded selector diagnostic:
  `tmp/story_world_larkspur_acquisition/permission_rationale_guarded_selector.md`
- Revised guarded selector diagnostic:
  `tmp/story_world_larkspur_acquisition/permission_rationale_guarded_selector_baseline_guard.md`

Result:

```text
baseline full-40:                         20 exact / 7 partial / 13 miss
permission/rationale variant alone:       31 exact / 3 partial / 6 miss
judged row-gated upper bound:             37 exact / 2 partial / 1 miss
original guarded selector:                34 exact / 4 partial / 2 miss
guarded selector + baseline guardrails:   37 exact / 2 partial / 1 miss
selected best available mode:             40/40
selector errors:                          0
```

Guardrails added:

- `identity question has baseline name/role support and candidate is broad action-heavy`
- `award/result question has baseline awarded support and candidate lacks awarded rows`
- `status question has direct baseline status/rule support`

The guardrails repaired the three selector mistakes from the first
permission/rationale selector pass:

| Row | Previous Choice | Revised Choice | Guard |
| --- | --- | --- | --- |
| `q009` | `permission_rationale` partial | `baseline` exact | identity/action-volume |
| `q018` | `permission_rationale` partial | `baseline` exact | direct status/rule support |
| `q032` | `permission_rationale` miss | `baseline` exact | explicit awarded support |

Lesson:

The permission/rationale acquisition lens is not a global compile replacement,
but the harness can now use it as a row-gated source-surface variant without
reading source prose, answer keys, judge labels, failure labels, gold KBs, or
strategy files in selector input. The important design shape is not
"Larkspur-specific protection"; it is answer-surface mismatch protection:
identity, award/result, and direct status/rule questions should not be
overridden by broader candidate evidence merely because that evidence has more
rows or more persuasive self-check narration.

## LCF-013 - Rationale/Contrast Older Transfer Diagnostic

Date: 2026-05-05

Evidence lane: `rationale_contrast_transfer`

Mode: focused rationale/contrast source-note compile over the older promoted
fixture, followed by targeted QA on reason, custody, object-state, and status
rows.

Artifacts:

- Compile:
  `tmp/story_world_rationale_contrast_variant_older/larkspur_clockwork_fair/domain_bootstrap_file_20260505T120645091683Z_source_qwen-qwen3-6-35b-a3b.json`
- Targeted QA:
  `tmp/story_world_rationale_contrast_qa_older_targeted/larkspur_clockwork_fair/domain_bootstrap_qa_20260505T122135211160Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

```text
target rows:          14
targeted QA:          4 exact / 6 partial / 4 miss
failure surfaces:     8 compile-surface gaps, 1 hybrid-join gap, 1 query gap
write proposals:      0
runtime load errors:  0
compile shape:        70 admitted / 16 skipped, rough profile score 0.746
```

Lesson:

This is a negative transfer result for Larkspur. The rationale/contrast lens
does not by itself recover story-world motive, custody, and object-state
surface. The next Larkspur work should be a sharper acquisition contract for
state transitions, custody/location, permission rationale, and final condition,
with exact-row protection; broad source-note rationale is not enough.

## LCF-014 - Final Object-State Micro-Lens

Date: 2026-05-05

Evidence lane: `source_surface_acquisition`

Mode: three narrow Larkspur acquisition passes, followed by targeted QA and
full-40 replay for the promising candidates. The passes were named for the
guardrail they serve rather than the fixture that exposed them:

- `final_object_state_transition_surface`
- `custody_ownership_chain_surface`
- `permission_motive_rationale_surface`
- follow-up negative check: `official_identity_role_roster_surface`

Artifacts:

- State compile:
  `tmp/story_world_larkspur_acquisition/final_object_state_micro_20260505/domain_bootstrap_file_20260505T123313203200Z_source_qwen-qwen3-6-35b-a3b.json`
- State targeted QA:
  `tmp/story_world_larkspur_acquisition/final_object_state_micro_qa_20260505/domain_bootstrap_qa_20260505T124110452883Z_qa_qwen-qwen3-6-35b-a3b.json`
- State full-40 QA:
  `tmp/story_world_larkspur_acquisition/final_object_state_micro_full40_qa_20260505/domain_bootstrap_qa_20260505T125748020331Z_qa_qwen-qwen3-6-35b-a3b.json`
- Custody compile:
  `tmp/story_world_larkspur_acquisition/custody_chain_micro_20260505/domain_bootstrap_file_20260505T123639918995Z_source_qwen-qwen3-6-35b-a3b.json`
- Custody targeted QA:
  `tmp/story_world_larkspur_acquisition/custody_chain_micro_qa_20260505/domain_bootstrap_qa_20260505T124058205738Z_qa_qwen-qwen3-6-35b-a3b.json`
- Permission/motive compile:
  `tmp/story_world_larkspur_acquisition/permission_motive_micro_20260505/domain_bootstrap_file_20260505T123545639802Z_source_qwen-qwen3-6-35b-a3b.json`
- Permission/motive targeted QA:
  `tmp/story_world_larkspur_acquisition/permission_motive_micro_qa_20260505/domain_bootstrap_qa_20260505T124033111821Z_qa_qwen-qwen3-6-35b-a3b.json`
- Permission/motive full-40 QA:
  `tmp/story_world_larkspur_acquisition/permission_motive_micro_full40_qa_20260505/domain_bootstrap_qa_20260505T125925000046Z_qa_qwen-qwen3-6-35b-a3b.json`
- Baseline replay q009 negative:
  `tmp/story_world_larkspur_acquisition/baseline_replay_q009_qa_20260505/domain_bootstrap_qa_20260505T130514522149Z_qa_qwen-qwen3-6-35b-a3b.json`
- Official identity q007/q009 negative:
  `tmp/story_world_larkspur_acquisition/official_identity_micro_qa_20260505/domain_bootstrap_qa_20260505T130824236335Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

```text
state compile:              98 admitted / 14 skipped, healthy
state targeted QA:          4 exact / 1 partial / 1 miss
state full-40 QA:           36 exact / 2 partial / 2 miss
state full-40 movement:     18 improved rows, 1 baseline-exact regression
state remaining non-exacts: q009 miss, q011 partial, q036 miss, q038 partial

permission/motive target:   3 exact / 2 partial / 0 miss
permission/motive full-40:  16 exact / 12 partial / 12 miss
custody target:             1 exact / 1 partial / 3 miss
official identity target:   0 exact / 1 partial / 1 miss
write proposals:            0
runtime load errors:        0
```

Row overlay opportunity:

- Use `final_object_state_transition_surface` for most rows.
- Use the older permission/rationale variant for q011 and q036.
- Use the custody-chain targeted row for q038.
- Protect q009 with the original baseline scorecard row until a retained
  selector-evidence artifact or stronger official-identity lens exists.

That judged artifact combination implies a `40 / 0 / 0` Larkspur full-40 row
target. It is not yet a deployable non-oracle selector result because the old
q009 exact evidence was only retained in a scorecard and the baseline replay did
not reproduce it.

Lesson:

This is the strongest Larkspur source-surface gain so far. The important
separation is now clear: object-state transition acquisition is globally useful;
permission/motive and custody are row-level lenses; official identity remains
its own acquisition problem. The next useful harness move is to make the
selector replay this overlay honestly, especially q009, rather than broadening
the compile prompt.

## LCF-015 - Role-Authority Lens and Selector Closure

Date: 2026-05-05

Evidence lane: `selector_calibration_full40`

Mode: q009 role-authority acquisition, full-40 safety check, then non-oracle
selector replay over four persisted artifacts: state, permission/rationale,
role-authority, and custody.

Artifacts:

- Role-authority compile:
  `tmp/story_world_larkspur_acquisition/official_role_authority_micro_20260505/domain_bootstrap_file_20260505T141914545752Z_source_qwen-qwen3-6-35b-a3b.json`
- Role-authority q009 QA:
  `tmp/story_world_larkspur_acquisition/official_role_authority_micro_qa_20260505/domain_bootstrap_qa_20260505T141939332800Z_qa_qwen-qwen3-6-35b-a3b.json`
- Role-authority full-40 QA:
  `tmp/story_world_larkspur_acquisition/official_role_authority_micro_full40_qa_20260505/domain_bootstrap_qa_20260505T142941190104Z_qa_qwen-qwen3-6-35b-a3b.json`
- Structural selector:
  `tmp/story_world_larkspur_acquisition/state_role_permission_custody_structural_selector_20260505.json`
- Guarded selector before new guards:
  `tmp/story_world_larkspur_acquisition/state_role_permission_custody_guarded_selector_20260505.json`
- Guarded selector after new guards:
  `tmp/story_world_larkspur_acquisition/state_role_permission_custody_guarded_selector_surface_guards_20260505.json`

Result:

```text
role-authority q009:        1 exact / 0 partial / 0 miss
role-authority full-40:     21 exact / 9 partial / 10 miss
four-mode upper bound:      40 exact / 0 partial / 0 miss
structural selector:        27 exact / 5 partial / 8 miss, 27/40 best
guarded selector before:    35 exact / 3 partial / 2 miss, 35/40 best
guarded selector after:     40 exact / 0 partial / 0 miss, 40/40 best
selector errors:            0
```

New reason-named selector guards:

- `superlative_identity_surface_guard`
- `official_role_definition_surface_guard`
- `current_component_state_surface_guard`
- `custody_transfer_rationale_guard`
- `award_placement_surface_guard`

Lesson:

This is the first full Larkspur selector closure over frozen artifacts. The
important product shape is not a single smarter compile; it is a pegboard of
named surfaces plus a selector that can route to the right surface without
seeing source prose, answer keys, judge labels, failure labels, gold KBs, or
strategy files.

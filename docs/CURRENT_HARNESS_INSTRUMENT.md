# Current Harness Instrument

Prethinker's harness is part of the product. It is the research instrument that
lets the project replay live behavior, capture structural signatures, compare
candidate extractions, and explain what changed without asking Python to
interpret source prose.

The product north star is **hard to fool**. The harness exists to make that
measurable: claims stay separate from facts, rules stay separate from outcomes,
authority boundaries stay visible, and zombie retries are stopped instead of
rewarded.

The daily-driver surface is `src/kb_pipeline_clean` plus
`scripts/run_kb_pipeline_clean_harness.py`. The live behavior source remains
`src/mcp_server.py` until each compiler, gate, apply, or normalization piece has
been wrapped, replayed, extracted, compared, and only then retired from the
legacy surface.

## Operator Commands

```powershell
python scripts/run_kb_pipeline_clean_harness.py --instrument-md
python scripts/run_kb_pipeline_clean_harness.py --instrument-manifest
python scripts/run_kb_pipeline_clean_harness.py --audit-normalizers
python scripts/run_kb_pipeline_clean_harness.py --trace-plan
python scripts/run_kb_pipeline_clean_harness.py --pack docs/data/frontier_packs/semantic_ir_lava_pack_v5.json --limit 3 --compiler-backend lmstudio --compiler-base-url http://127.0.0.1:1234 --semantic-ir-enabled --active-profile auto
python scripts/validate_fixture_intake.py --root datasets/incoming_fixtures --out-json tmp/incoming_fixtures/intake_validation.json
python scripts/stage_incoming_fixtures.py --root tmp/incoming --out-root tmp/incoming_staged
python scripts/plan_incoming_fixture_runs.py --manifest tmp/incoming_staged/stage_manifest.json --out-json tmp/incoming_staged/cold_run_plan.json --out-md tmp/incoming_staged/cold_run_plan.md
python scripts/plan_story_world_fixture_runs.py --fixture copperfall_deadline_docket --fixture harrowgate_witness_file --fixture larkspur_clockwork_fair --fixture meridian_permit_board --fixture northbridge_authority_packet --qa-limit 40 --out-json tmp/story_world_runs/promoted_incoming_cold_run_plan.json --out-md tmp/story_world_runs/promoted_incoming_cold_run_plan.md
python scripts/summarize_incoming_fixture_smoke.py --fixture meridian_permit_board --compile-json <COMPILE_RUN_JSON> --qa-json <QA_RUN_JSON> --qa-json <FAILURE_SURFACE_RUN_JSON>
python scripts/rollup_incoming_smoke_scorecard.py --root tmp/incoming_smoke_summaries --out-json tmp/incoming_smoke_summaries/scorecard.json --out-md tmp/incoming_smoke_summaries/scorecard.md
python scripts/compare_incoming_smoke_scorecards.py --baseline-json tmp/incoming_smoke_summaries/scorecard.json --candidate-json tmp/incoming_smoke_summaries_detail_retry/scorecard.json --out-json tmp/incoming_smoke_summaries_detail_retry/baseline_comparison.json --out-md tmp/incoming_smoke_summaries_detail_retry/baseline_comparison.md
python scripts/plan_incoming_row_mode_overlay.py --baseline-json tmp/incoming_smoke_summaries/scorecard.json --candidate-json tmp/incoming_smoke_summaries_evidence_nonexact/scorecard.json --out-json tmp/incoming_smoke_summaries_evidence_nonexact/row_mode_overlay_plan.json --out-md tmp/incoming_smoke_summaries_evidence_nonexact/row_mode_overlay_plan.md
python scripts/plan_incoming_row_gated_scorecard.py --baseline-json tmp/incoming_smoke_summaries/scorecard.json --candidate-json tmp/incoming_smoke_summaries_scoped_repair/scorecard.json --row-overlay-json tmp/incoming_smoke_summaries_scoped_repair/row_mode_overlay_plan.json --out-json tmp/incoming_smoke_summaries_scoped_repair/row_gated_scorecard_plan.json --out-md tmp/incoming_smoke_summaries_scoped_repair/row_gated_scorecard_plan.md
python scripts/plan_incoming_compile_variant_overlay.py --baseline-json tmp/incoming_smoke_summaries_scoped_evidence/scorecard.json --candidate-json shifted_compile_variants=tmp/incoming_smoke_summaries_compile_variant_selection/scorecard.json --out-json tmp/incoming_smoke_summaries_compile_variant_selection/compile_variant_overlay_plan.json --out-md tmp/incoming_smoke_summaries_compile_variant_selection/compile_variant_overlay_plan.md
python scripts/plan_incoming_variant_selector_training.py --overlay-json tmp/incoming_smoke_summaries_official_companion_overlay/compile_variant_overlay_plan.json --out-json tmp/incoming_smoke_summaries_official_companion_overlay/variant_selector_training_plan.json --out-md tmp/incoming_smoke_summaries_official_companion_overlay/variant_selector_training_plan.md
python scripts/plan_incoming_compile_repair_targets.py --scorecard-json tmp/incoming_smoke_summaries/scorecard.json --row-overlay-json tmp/incoming_smoke_summaries_evidence_nonexact/row_mode_overlay_plan.json --out-json tmp/incoming_smoke_summaries/compile_repair_targets.json --out-md tmp/incoming_smoke_summaries/compile_repair_targets.md
python scripts/plan_story_world_repair_targets.py --scorecard-json tmp/story_world_full40_classified_scorecards/scorecard.json --out-json tmp/story_world_repair_plans/full40_repair_targets.json --out-md tmp/story_world_repair_plans/full40_repair_targets.md
python scripts/plan_story_world_repair_targets.py --scorecard-json tmp/story_world_full40_classified_scorecards/scorecard.json --fixture larkspur_clockwork_fair --out-json tmp/story_world_repair_plans/larkspur_full40_repair_targets.json --out-md tmp/story_world_repair_plans/larkspur_full40_repair_targets.md
python scripts/select_qa_mode_without_oracle.py --selection-policy protected --group <name>:baseline=<QA_JSON>,evidence=<QA_JSON> --out-json <OUT_JSON> --out-md <OUT_MD>
python scripts/select_qa_mode_without_oracle.py --selection-policy guarded_activation --group <name>:baseline=<QA_JSON>+<FAILURE_SURFACE_QA_JSON>,candidate=<QA_JSON> --out-json <OUT_JSON> --out-md <OUT_MD>
python scripts/plan_selector_risk_gate.py --baseline-run protected=<SELECTOR_JSON> --candidate-run guarded_activation=<SELECTOR_JSON> --transfer-comparison <SELECTOR_POLICY_COMPARISON_JSON> --out-dir tmp/selector_risk_gates
```

## Instrument Principles

- The harness measures structural behavior; it does not reward "better" model
  answers during refactors.
- Canonical signatures are calibration artifacts for extraction parity.
- New public names should describe the guardrail or reason for being, not the
  fixture that first exposed the issue.
- Legacy symbol names may remain as migration references until the clean surface
  proves parity.
- Dead-code removal waits until the instrument can show that code is genuinely
  unreachable rather than dormant migration scaffolding.
- The harness should detect semantic struggle. If repeated passes add no unique
  admitted surface, duplicate most of their output, go skip-heavy, or fail
  activation-governor targets, the instrument should recommend stopping or
  continuing only with a named expected contribution.

## Extraction Rule

```text
wrap -> replay -> extract -> compare -> retire
```

That order keeps the moving platform usable while the workbench becomes easier
for a human to understand.

## Struggle Detection

`src/semantic_struggle.py` owns the first structural circuit breaker. It reads
only harness telemetry such as per-pass unique contribution counts, duplicate
counts, health flags, and selector-governor compliance counts. It does not read
source prose or infer answers.

The current output is `semantic_progress_assessment_v1`:

- `zombie_risk`: `low`, `medium`, or `high`
- `recommended_action`: `continue`, `continue_only_with_named_expected_contribution`,
  or `stop_and_report_struggle`
- `semantic_progress_delta`: unique contribution total, duplicate total,
  duplicate ratio, recent unique contribution count, and stale tail count
- `stop_reasons` and `caution_reasons`

This is the product behavior: Prethinker should be smart enough to notice when
it is no longer making semantic progress.

## Incoming Fixture Scorecards

Incoming is an intake state, not a research destination. Use `tmp/incoming*`
only to validate a new drop, split source from scoring assets, and plan the
first cold run. As soon as the fixture is structurally valid, promote it into
`datasets/story_worlds/` with `README.md`, `source.md`/`story.md`, QA assets,
`progress_journal.md`, and `progress_metrics.jsonl`. Generated run JSON can
stay under `tmp/`, but durable scorecard lessons and artifact references should
be captured in the tracked fixture journal.

`C:\prethinker_tmp_archive` is the lab's cold-storage/RAG shelf for bulky tmp
evidence worth keeping but not worth carrying in the active tree or model
context. Search it narrowly when a named prior artifact matters. Do not treat it
as live guidance; if an archived run becomes an active lesson, summarize that
lesson in tracked docs or the fixture's journal.

The current incoming rule is now exercised on zip-delivered drops after
extraction, as well as loose folders. The five 2026-05-04 zip fixtures were
normalized, promoted into `datasets/story_worlds`, and given
`progress_journal.md` plus `progress_metrics.jsonl` before baselining. The
generated scorecard lives at `tmp/story_world_zip_baseline_summaries/scorecard.md`;
the durable lesson lives beside each fixture.

`scripts/plan_story_world_fixture_runs.py` is the promoted-fixture daily-driver
planner. It reads runnable fixtures directly from `datasets/story_worlds`,
prefers `source.md` over `story.md`, uses `qa.md` as the question surface, and
uses `oracle.jsonl` only for after-the-fact scoring when present. This is the
normal path for seeing how current harness machinery responds to promoted
fixtures; the older incoming planner remains intake/staging compatibility.

Incoming challenge fixtures now have a two-step instrument panel:

1. `scripts/summarize_incoming_fixture_smoke.py` normalizes one fixture's
   compile, QA, and failure-classification artifacts without rereading source
   prose.
2. `scripts/rollup_incoming_smoke_scorecard.py` rolls those fixture summaries
   into a batch scorecard.
3. `scripts/compare_incoming_smoke_scorecards.py` compares a candidate
   scorecard against a baseline and emits an artifact-only promotion
   recommendation.
4. `scripts/plan_incoming_row_mode_overlay.py` compares row verdicts between
   scorecards and identifies candidate row rescues, regressions, and unchanged
   non-exacts for row-level selector research.
5. `scripts/plan_incoming_compile_repair_targets.py` turns unresolved scorecard
   rows into repair lanes such as row-selector calibration, scoped
   source-surface repair, helper/query-join repair, query-planner repair, and
   answer-surface repair.

The first five-fixture incoming smoke scorecard is under
`tmp/incoming_smoke_summaries/scorecard.{json,md}`. It covers `50` no-answer QA
rows across five compiled fixtures and labels profile fallback paths, such as
Copperfall's compact profile retry, separately from semantic QA performance.

Promotion policy is deliberately conservative: a candidate can be promoted only
when exact rows increase without increasing misses, compile failures, or QA
write proposals. Neutral candidates are `mixed_candidate`; regressions are
`reject_candidate`. Non-exact rows without failure classification are counted as
`unclassified` rather than being treated as improved failure-surface behavior.

The first evidence-bundle diagnostic over current non-exacts lifted the batch
from `44 / 4 / 2` to `46 / 1 / 3`, so it is not a default promotion. The row
overlay plan still found the useful shape: two candidate row rescues, one
candidate regression, and three unchanged non-exacts. That is the next selector
problem in miniature.

Selector comparisons are fixture-aware: `scripts/compare_selector_runs.py`
prefixes row ids by selector group when present and rolls up policy totals. On
the first six-row incoming non-exact target, structural selection reached `5/6`
best available choices while LLM `activation` selection reached `6/6`, both
without giving the selector source prose, answer keys, judge labels, or failure
labels.

The full first-10 selector replay is the promotion guardrail: evidence mode over
all rows stayed exact-flat but increased misses, structural selection reached
`24 / 3 / 3` across the three imperfect fixtures, and activation reached
`23 / 5 / 2` after selector JSON retry handling removed the Larkspur parse
failure. The harness therefore labels activation as calibration signal until
exact-row protection is stronger.

`--selection-policy protected` is the first exact-protection experiment. It uses
structural selection by default, but sends high-volume nonbaseline overrides to
the activation selector because row volume can hide wrong-subject evidence. It
helped the incoming first-10 slice and reduced Avalon misses, but failed to
transfer to Sable, so the instrument keeps it as a comparison mode rather than
daily-driver policy.

`--selection-policy guarded_activation` is the next selector harness shape. It
keeps deterministic structural scoring for confident rows, but sends uncertain
rows through the activation selector with bounded QA self-check evidence. The
selector can now merge multiple QA artifacts for one mode with `+`, so a
baseline can be represented as the same canonical first-pass +
failure-classified row view used by the incoming smoke scorecards. On the
ledger diagnostic over Larkspur, Meridian, and Northbridge, guarded activation
selected the best available mode on `30/30` rows: Larkspur stayed `8 / 2 / 0`,
Meridian moved to `9 / 0 / 1`, and Northbridge moved to `9 / 0 / 1` without
source prose, answer keys, judge labels, or failure labels in selector input.
The immediate transfer check was mixed: Avalon preferred `protected` for miss
control, and Sable still preferred `direct`. Guarded activation is therefore a
named diagnostic policy, not a global daily-driver selector.

Guarded activation now also includes named answer-surface baseline guards:
identity questions with broad action-heavy candidate overrides, award/result
questions where baseline has explicit `awarded` support, and status questions
where baseline has direct status/rule predicates. These guards are named for
the reason they exist rather than the fixture that exposed them. On the
Larkspur permission/rationale full-40 pair, they moved guarded activation from
`34 / 4 / 2` and `37/40` best choices to the judged row-gated upper bound:
`37 / 2 / 1`, `40/40` best choices, and `0` selector errors.

`scripts/plan_selector_risk_gate.py` is the risk-gate planner for that lesson.
It reads selector-run artifacts plus optional selector-policy transfer
comparisons and splits rows into `safe_activation_target`,
`calibration_activation_target`, `protect_baseline_target`,
`needs_compile_repair`, and `stable_no_action`. A candidate rescue is only
called safe when the candidate policy also has measured transfer support; with
weak or unmeasured transfer it remains a calibration target. On the incoming
guarded-activation replay, the gate preserved the Meridian/Northbridge rescues
as calibration targets and pointed Larkspur plus unresolved Meridian/Northbridge
rows back to compile repair instead of promoting guarded activation globally.

`scripts/compare_incoming_smoke_scorecards.py` now also enforces exact-row
protection. Aggregate gains no longer imply promotion if the candidate creates
a baseline-exact row regression visible in `non_exact_rows`; that case returns
`row_level_gate_required`. The scoped compile-repair diagnostic improved the
incoming batch from `44 / 4 / 2` to `45 / 4 / 1`, but regressed Meridian q010,
so the harness correctly keeps it behind a row-level gate instead of promoting
the compile mode globally.

`scripts/plan_incoming_row_gated_scorecard.py` turns that row gate into a
scorecard-shaped planning artifact. It applies only accepted candidate rows over
the baseline and leaves rejected rows at baseline. For the scoped compile-repair
diagnostic, the row-gated scorecard is `46 / 4 / 0`: three accepted rescues
and one rejected Meridian exact-row regression. This is the current activation
target, not a global compile promotion.

The first actual candidate to realize that row-gated target combines scoped
compile repair with evidence-bundle query choreography:
`--evidence-bundle-plan --execute-evidence-bundle-plan
--evidence-bundle-context-filter`. Meridian's scoped compile repaired q007, and
the evidence-filtered QA pass protected q010 instead of repeating the scoped
compile-only regression. Northbridge moved to no misses as well. The resulting
five-fixture scorecard is `46 / 4 / 0`, with `0` QA write proposals, `0`
baseline-exact regressions, and a `promote_candidate` gate. This does not make
evidence filtering a blind global default; it makes scoped compile plus bounded
query choreography the current promoted incoming recipe.

`scripts/plan_incoming_compile_variant_overlay.py` generalizes the row-gate
idea across multiple compile/query scorecards. It is explicitly a judged
artifact upper-bound planner, not a deployable selector policy: it reads
scorecard verdict rows, treats missing `non_exact_rows` as exact within that
artifact, and reports which variant rows are complementary while keeping
baseline-exact rows protected. On the current incoming batch, shifted Meridian
and Northbridge scoped compiles are aggregate-neutral at `46 / 4 / 0`, but the
variant overlay exposes a `48 / 2 / 0` target: accept Meridian q006 and
Northbridge q007 from the shifted variants, while protecting Meridian q007 and
Northbridge q004 from baseline.

The Larkspur attribute/duty guardrail adds the next diagnostic row: narrative
compilation now tells the model that numeric character attributes must not be
encoded as names or aliases, and that named officials need duty/authority
surface when the profile supports it. The first replay is not a blanket
promotion because compile health is `poor`, but it repairs Larkspur q007. With
that variant added, the judged compile-variant overlay target moved to
`49 / 1 / 0`.

The post-ingestion QA harness now adds a deterministic official-identity
companion query: when `person_role(Constant, Role)` succeeds for a named
official or role-holder, the runtime also checks admitted authority/action
surfaces for the same person, such as `ruling_by/3`, `permission_granted/2`,
`official_action/3`, and `event_affects_person/3`. This repaired Larkspur q009
without Python source-prose interpretation. The Larkspur companion candidate is
still rejected globally because q010 regresses, but the compile/query variant
overlay now exposes a judged `50 / 0 / 0` target with four accepted variant
rows, three protected baseline-exact rows, and zero unchanged non-exacts. The
next product step is selector/risk-gate machinery that can approximate that
row choice without oracle verdicts.

`scripts/plan_incoming_variant_selector_training.py` is the bridge artifact for
that step. It reads the compile-variant overlay only and converts accepted rows
into `activation_training_target`s and protected exact rows into
`exact_protection_target`s. On the official-companion overlay it emits `7`
training rows: `4` activation targets, `3` exact-protection targets, and `0`
repair targets. Both nonbaseline variants are labeled
`unsafe_global_variant_row_gate_required`, which is exactly the current lesson:
the selector should learn row-level activation with exact protection, not
global variant promotion.

The guarded selector now has a structural volume-trap uncertainty trigger. If
the top structural score is inflated by relaxed fallback volume or broad row
volume, guarded activation calls the LLM selector instead of treating row count
as confidence. The trigger deliberately does not double-penalize relaxed-only
baseline paths; those already carry ordinary uncertainty reasons. On the seven
incoming variant calibration rows, this moved guarded activation from `3/7`
best choices to `6/7`, scoring `6 exact / 1 partial / 0 miss`. The remaining
miss is Northbridge q007, where the selector still prefers count-only agreement
support over spacing-bearing hydrant support.

The activation selector now also carries a requirement-detail completeness
guardrail: for requirement questions, count-only or status-only rows are often
partial when another mode returns answer-bearing details such as spacing,
interval, threshold, scope, exception, condition, duration, unit, or authority.
That closed the Northbridge q007 calibration miss. The seven-row incoming
variant selector replay now reaches `7/7` best choices and `7 exact / 0 partial
/ 0 miss`, without source prose, answer keys, judge labels, failure labels, or
gold KBs in selector input.

The same guarded selector was then replayed over the full first-10 slices for
Larkspur, Meridian, and Northbridge. Across those `30` rows it selected `30/30`
best modes and scored `30 exact / 0 partial / 0 miss`, with `0` selector
errors. Combined with Copperfall and Harrowgate's baseline `10/10` runs, the
current best harness surface has a first-10 `50 / 0 / 0` incoming-batch result.
This is a row-gated selector result over existing compile/query artifacts, not
a claim that one cold compile is now perfect.

The transfer check remains deliberately conservative. Replaying the same
requirement-detail guarded selector against older rule-activation packs moved
Avalon to `28 exact / 10 partial / 2 miss` with `35/40` best choices, a small
miss-control improvement over the previous guarded replay. Sable stayed at
`25 exact / 6 partial / 9 miss` with `37/40` best choices, so Sable still
prefers direct selection. The daily-driver lesson is row-gated activation with
explicit risk gates, not blanket guarded activation.

The promoted story-world full-40 replay is now the next generalization score.
Using `scripts/plan_story_world_fixture_runs.py`, all five promoted challenge
fixtures compiled and scored `154 exact / 20 partial / 26 miss` across `200`
QA rows, with `0` write proposals. Failure classification reduced the active
repair queue to `46` rows: `39` compile-surface gaps and `7` helper/query-join
gaps. This redirects the next frontier away from selector prompting and toward
scoped source-surface acquisition, especially Larkspur state/custody/rationale
coverage.

The Larkspur targeted-state lens shows the current harness shape. The compile
variant alone is unsafe (`14 / 8 / 18`), but the judged row overlay exposes a
`23 / 6 / 11` target with `4` accepted rows and `9` exact-protection rows. A
new identity-completeness uncertainty gate prevents structural selection from
preferring authority-row volume over explicit name support on who-is rows. With
identity, rationale/contrast, and capability-failure guardrails, guarded
activation selects `23 exact / 8 partial / 9 miss` across Larkspur full-40,
`39/40` best rows, with no selector errors.

`scripts/plan_story_world_repair_targets.py` is the promoted story-world repair
planner. It reads full-QA scorecard artifacts only, extracts query predicate
names, and groups non-exact rows into acquisition lenses without reading source
prose, gold KBs, or answer keys for classification. On the promoted full-40
scorecard it preserves the `46` target queue while naming the next work:
`39` scoped source-surface repairs, `7` helper/query-join repairs, and lens
buckets such as `rule_interpretation_surface`, `authority_document_surface`,
`object_state_transition_surface`, `object_location_custody_surface`,
`permission_rationale_surface`, and `temporal_deadline_surface`. The Larkspur
fixture-specific plan has `20` compile-surface targets split into `6`
object-state, `5` object-location/custody, `4` permission/rationale, `2`
outcome/status, `1` claim-truth, `1` identity/role, and `1` temporal target.

A direct-profile Larkspur acquisition check is a negative result. Bypassing
profile discovery with `story_world@v0` avoided empty profile/intake responses,
but the source compiles were too thin: object-state admitted `24` rows and
scored `0 exact / 0 partial / 6 miss` on its target rows; object-custody
admitted `6` rows and scored `0 / 2 / 2`; permission/rationale admitted `12`
rows and scored `0 / 0 / 5`. All had `0` write proposals. The lesson is that
the next source-surface move needs richer compact/focused acquisition, not a
direct registry-only compile.

The same work exposed a harness URL issue. `run_domain_bootstrap_file.py` now
normalizes LM Studio base URLs before appending `/v1/chat/completions`, so
operator commands work with either `http://127.0.0.1:1234` or
`http://127.0.0.1:1234/v1`. After that fix, the focused
permission/rationale acquisition path produced a real Larkspur candidate:
`150` admitted rows, `14` skips, target QA `5 exact / 0 partial / 0 miss`, and
full-40 QA `31 exact / 3 partial / 6 miss` with `0` write proposals. It also
regressed `6` baseline-exact rows, so it remains a row-gated variant rather
than a promoted global compile.

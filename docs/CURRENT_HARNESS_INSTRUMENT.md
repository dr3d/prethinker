# Current Harness Instrument

Prethinker's harness is part of the product. It is the research instrument that
lets the project replay live behavior, capture structural signatures, compare
candidate extractions, and explain what changed without asking Python to
interpret source prose.

The product north star is **hard to fool**. The harness exists to make that
measurable: claims stay separate from facts, rules stay separate from outcomes,
authority boundaries stay visible, and zombie retries are stopped instead of
rewarded.

Current harness vocabulary:

```text
compiled KB = durable state
row = measured encounter with that state
selector = chooses the best encounter surface
guard = prevents a tempting wrong surface
verdict = records what happened
```

Rows are the unit of scoring, classification, guarding, selection, and replay.
They are not the truth store. The compiled KB is the truth store; a row is the
stress test that shows whether the right admitted state can be surfaced for a
specific question.

The harness now distinguishes semantic lenses from deterministic pre-compile
ledgers. Lenses ask the model to propose meaning under governance. Ledgers pin
literal source addressability before the model reads: identifiers, headings,
line numbers, table rows, table cells, numeric tokens, and labeled official
prose. Ledgers do not infer source truth; they make the source's printed
structure queryable so a later compile or QA pass can recover the exact row,
date, count, source label, or record cell without relying on model recall.

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
python scripts/select_qa_mode_without_oracle.py --selection-policy hybrid --hybrid-llm-policy activation --include-self-check --group <name>:baseline=<QA_JSON>,candidate=<QA_JSON>,registry=<QA_JSON> --out-json <OUT_JSON> --out-md <OUT_MD>
python scripts/plan_selector_risk_gate.py --baseline-run protected=<SELECTOR_JSON> --candidate-run guarded_activation=<SELECTOR_JSON> --transfer-comparison <SELECTOR_POLICY_COMPARISON_JSON> --out-dir tmp/selector_risk_gates
```

Historical Lava stress packs remain available for calibration/regression
questions, but they are no longer the daily active frontier:

```powershell
python scripts/run_kb_pipeline_clean_harness.py --pack docs/data/frontier_packs/semantic_ir_lava_pack_v5.json --limit 3 --compiler-backend lmstudio --compiler-base-url http://127.0.0.1:1234 --semantic-ir-enabled --active-profile auto
```

## Instrument Principles

- The harness measures structural behavior; it does not reward "better" model
  answers during refactors.
- Prefer artifact-first orchestration: compile once, persist the source/KB/IR
  and run metadata, then run many cheaper semantic parallax passes against
  frozen artifacts.
- Treat the compile product as a durable KB artifact package. Ordinary Q&A
  should answer from admitted world state, admitted epistemic/provenance state,
  deterministic helpers, and manifest metadata, not by rereading source prose.
  See `docs/COMPILED_KB_ARTIFACT_PACKAGE.md`.
- Canonical signatures are calibration artifacts for extraction parity.
- New public names should describe the guardrail or reason for being, not the
  fixture that first exposed the issue.
- Treat registry-scaffolded candidates as vocabulary scaffolds, not fact
  sources. A registry can name `report_commissioned_by/4` or
  `item_received_from/4`, but it must not supply fixture facts; promotion still
  requires compile artifacts, QA replay, selector gating, and journaled transfer
  evidence.
- Maintain a lens roster for meaning surfaces such as source acquisition, rule
  composition, temporal/status, authority, uncertainty, query, selector, answer,
  and struggle detection. See `docs/SEMANTIC_INSTRUMENT.md` for the public
  reader-facing instrument spec and `docs/SEMANTIC_LENS_ROSTER.md` for the
  deeper lab calibration roster.
- Legacy symbol names may remain as migration references until the clean surface
  proves parity.
- Dead-code removal waits until the instrument can show that code is genuinely
  unreachable rather than dormant migration scaffolding.
- The harness should detect semantic struggle. If repeated passes add no unique
  admitted surface, duplicate most of their output, go skip-heavy, or fail
  activation-governor targets, the instrument should recommend stopping or
  continuing only with a named expected contribution.
- Guard growth is itself telemetry. A new guard should name a reusable
  question/evidence mismatch; if it only names a fixture, it is probably
  overfitting. Merge duplicate guards only after replay proof, and retire guards
  when better compile/helper surfaces make them unnecessary.
- Selector improvements can close real score gaps without new compiles. On
  2026-05-10, replaying existing precision-batch artifacts with the latest
  guarded selector and helper surfaces moved the six precision fixtures to a
  candidate-helper row-gated `240 / 0 / 0` over `240`, equal to the available candidate ceiling.
  Authority/Possession reached `40 / 0 / 0` after a query-only
  archive-authority/custody companion exposed grouped custody counts, access
  authorization from source-record table cells, recall rights, and contractor
  custody notice/consent clauses from already admitted state. Contradictory
  Evidence reached `40 / 0 / 0` after a query-only source-record clock-sync
  companion exposed exact last-successful NTP sync dates from admitted text
  atoms and numeric tokens. Treat that as evidence that this batch is now
  exhausted by helper/queryability over admitted memory, not by new lens or
  guard-family expansion; under the helper classification doctrine, do not
  report this as clean-helper architecture until the contributing helpers have
  passed audit or transfer proof without fixture-shaped constants.
- Deterministic ledger growth is not lens growth. Promote a ledger expansion
  only when it preserves source structure without semantic interpretation and
  improves row-gated replay. The 2026-05-10 source-record ledger V2 added table
  cells, numeric tokens, bold-label rows, and anchored official prose; on the
  precision batch it raised the seven-candidate selected score to `223 / 8 / 9`
  and the candidate ceiling to `232 / 4 / 4` over `240` rows.
- Cold acquisition now preserves table cell headers as deterministic source
  addressability. `source_record_cell/3` already made table cells queryable, but
  cell position alone loses the printed field name. The ledger now adds
  `source_record_cell_header/3` and `source_record_field/3` for markdown-table
  data rows. This is still not semantic truth: it says "this row has a printed
  `Time` field with value `22:12`," not that an event truly happened then.
- Temporal helpers are part of the query substrate, not a lens. A 2026-05-10
  repair showed that admitted notice timestamps were present but duration rows
  failed because placeholder repair and relaxed fallback queries lost shared
  temporal variables or accidentally joined local `Eventid` provenance slots.
  The helper join now preserves repaired start/end variables, computes
  `elapsed_hours/3` plus `elapsed_minutes/3`, and localizes repeated source
  event variables before joining. A follow-on clear-sample probe made the same
  point for clock-state snapshots: the runtime can derive
  `clear_sample_clock_pause_support` from admitted counted segments,
  sampler-offline intervals, and rule exceptions, so "paused with 18 hours
  counted" is queryable state rather than fresh model inference. The
  row-gated nine-candidate temporal selector then reached `40 / 0 / 0` on
  Temporal State Ledger by selecting the duration-helper surface for duration
  rows and the pause-helper surface for the clock-state snapshot row.
- Constraint propagation is now beginning as its own substrate. The existing
  `engine.constraint_propagation` runner still treats admitted state as input,
  not source prose, but it can now narrow numeric and date/time domains with
  ordered constraints such as `before`, `before_or_equal`, `after`, and
  `at_or_before`. This is the first small bridge from "known rows" to
  spreadsheet-like degrees of freedom: a candidate timestamp set can shrink
  deterministically when a deadline, correction, or interval boundary is known.
- Roster-state and source-address helpers are now candidate-tested against a fresh fixture. On
  `school_activity_roster_reconciliation`, the cold OpenRouter compile admitted
  rich source-record rows but missed operational v3 roster composition. A
  helper-only replay derived v3 group membership and counted-adult ratio scope
  from admitted `source_record_text_atom/2`, `source_record_section/2`,
  `source_record_line/2`, `adult_role/2`, and `role_counts_towards_ratio/2`
  rows, moving the same compile artifact from `21 / 3 / 16` to `28 / 2 / 10`.
  The helper resets at version and section boundaries so superseded v2 roster
  rows do not leak into v3. A follow-on section-display companion renders
  normalized section atoms such as `v_1_4_roster_v3_2026_04_15` into
  `Section 1.4`, moving the same artifact again to `30 / 1 / 9`. The remaining
  pressure was small policy/device/location/permission companions. After a
  deterministic wrapped-line ledger refresh and packet-metadata companion, the
  candidate-helper replay reached `40 / 0 / 0` without a new semantic compile or new lens.
  Across the fresh transfer batch, this changes the cold/repaired read from
  `177 / 10 / 53` to `196 / 7 / 37` if only this fixture's helper repair is
  substituted, with the weakest fixture becoming a candidate-helper proof of
  source addressability.
- Industrial sensor/source-clock helpers are also candidate-tested. On
  `industrial_sensor_clock_correction`, a query-only
  `industrial_sensor_support/5` companion over admitted `source_record_*` rows
  moved the cold artifact to a candidate-helper replay of `39 / 1 / 0` without
  a new lens, guard family, or compile. The remaining partial is the clean
  boundary case:
  deterministic source records expose `EV-14` and the 14-row raw log, while the
  canonical semantic predicate inventory still lacks `event_id(ev_14)`.
- Clinic recall source-record helpers now show the same pattern on a different
  domain. A refreshed deterministic source-record ledger plus
  `clinic_recall_support/5` moved `clinic_device_recall_field_packet` from
  `31 / 0 / 9` to a candidate-helper replay of `40 / 0 / 0`, recovering exact liaison, failure-rate,
  cabinet/seal/key-custody, verification-procedure, full serial, and
  medical-director authority details without a new lens or guard family.

Under `docs/ARTIFACT_UNIT_AND_HELPER_CLASSIFICATION.md`, these recent
helper-assisted high-water results are candidate-helper evidence until the
mixed helpers are split into clean generic substrate, declared lens companions,
or transfer-proven helpers without fixture-shaped constants. The
source-record packet metadata, industrial sensor, clinic recall, and grant
award helpers have begun that cleanup: emitted rows now label generic
identifier/event/timestamp, device/serial, award, cap, eligibility, and
field-recusal extraction as `clean-helper` and quarantine packet-family,
sensor/ticket, clinic, liaison, seal, authority, appeal, procedure, and
score-correction recognizers as `candidate-helper`.

`scripts/audit_helper_classes.py` can now run this audit artifact-only against
domain bootstrap compile JSONs. The first six-fixture transfer pass over
`tmp/transfer_fixtures_20260510/cold_acquisition_compile_lanes6` initially
produced 160 companion rows with zero unlabeled rows: 116 `clean-helper` and 44
`candidate-helper`. Normal `domain_bootstrap_qa` JSON and Markdown summaries
also include `helper_class_summary` when companion rows are present, so this
provenance can ride with score reports instead of living only in a side audit.
The first candidate-retirement passes moved industrial sensor-register section
support plus calibration due-date/ticket support from text recognizers to
generic source-record label/section joins, bringing the six-fixture audit to 162
companion rows: 122 `clean-helper` and 40 `candidate-helper`. A subsequent
generic parser for `<sensor_id>_vendor_<vendor>_model_<model>` source atoms
moved sensor vendor/model rows to `clean-helper` and exposed one additional
sensor model row, bringing the audit to 163 companion rows: 125 `clean-helper`
and 38 `candidate-helper`. Generic extraction of batch IDs and maintenance
tickets from raw event descriptions then brought the audit to 164 companion
rows: 128 `clean-helper` and 36 `candidate-helper`.
Adding `roster_state_support` to the same artifact-only audit widened the pass
to 344 companion rows: 191 `clean-helper` and 153 `candidate-helper`. The roster
helper itself emits 63 clean admitted-predicate join rows and 117 candidate rows
from source-record roster parsing. That formalizes the school roster saturation
as a split-helper result, not a fully clean-helper result. Adding
`archive_authority_custody_support` then brought the audit to 348 companion
rows: 191 `clean-helper` and 157 `candidate-helper`; the transfer-batch
authority/custody rows currently reached by that companion are all
candidate-helper rows from older family-specific source-cell/text recognizers.
The first clinic cleanup moved manufacturer-liaison and verification-procedure
recognizers to generic source-record atom extraction, shifting the six-fixture
transfer audit to 192 `clean-helper` and 156 `candidate-helper` rows.
A follow-on clinic failure-rate rewrite uses adjacent source-record continuation
lines instead of a hard-coded rate string. The old cold transfer artifact does
not contain that failure-rate source row, so its class counts do not move; the
refreshed clinic source-record artifact audits at 19 `clean-helper` and 10
`candidate-helper` rows, confirming the helper is generic where the source
ledger acquired the needed line.
The clinic abbreviation parser now promotes only mechanically derivable
acronym/name rows to `clean-helper`; `EPA` and `CIM` move clean, while
non-initialism `NBFH` remains candidate. That brings the six-fixture transfer
audit to 194 `clean-helper` and 154 `candidate-helper` rows.
The cabinet/seal/key pass then promoted cabinet and seal-range rows to generic
source-record adjacency extraction while leaving key-retainer identity
candidate. The six-fixture transfer audit now stands at 196 `clean-helper` and
151 `candidate-helper` rows; `clinic_recall_support` itself is 21 clean / 4
candidate.
The complementary precision-batch audit over `tmp/openrouter_precision_20260509`
shows `source_record_clock_sync_support` as clean deterministic substrate:
2 rows, both `clean-helper`, with zero unlabeled rows.
The same audit now covers `clear_sample_clock_pause_support`: 1 row,
`clean-helper`, zero candidate rows, zero unlabeled rows, confirming that the
pause-aware clock helper is currently generic temporal substrate over admitted
segments, offline intervals, and rule exceptions.
Grant cleanup promoted appeal-window and committee-recusal vote-count support
to generic source-record extraction, bringing `grant_award_support` to 14 clean
/ 2 candidate rows and the six-fixture transfer audit to 198 `clean-helper` and
149 `candidate-helper` rows.
Industrial cleanup promoted computed corrected-response and line-stop durations
from candidate rows to clean timestamp arithmetic over admitted corrected event
times. `industrial_sensor_support` is now 35 clean / 9 candidate, and the
six-fixture transfer audit is 200 `clean-helper` and 147 `candidate-helper`
rows.
Packet-id and data-loss status recognizers then moved to generic source-record
patterns, bringing `industrial_sensor_support` to 37 clean / 7 candidate and
the six-fixture transfer audit to 202 `clean-helper` and 145
`candidate-helper` rows.
Lab-sample status and estimated-return rows were then generalized over
`lab_YYYY_MMDD_sN` sample identifiers and source-record date atoms, bringing
`industrial_sensor_support` to 39 clean / 5 candidate and the six-fixture
transfer audit to 204 `clean-helper` and 143 `candidate-helper` rows.
System clock authority then moved from a SYS-C literal to the generic
`<system>_timestamps_are_accepted_as_wall_clock` source-record pattern,
bringing `industrial_sensor_support` to 40 clean / 4 candidate and the
six-fixture transfer audit to 205 `clean-helper` and 142 `candidate-helper`
rows.

`scripts/audit_helper_usage.py` adds the complementary transfer-pressure view:
fixtures per helper and helpers per fixture across QA artifacts. The first scan
over `tmp/transfer_fixtures_20260510` plus `tmp/openrouter_precision_20260509`
observed 9 support helpers across 453 JSON files; 8 appeared on two or fewer
fixtures and should be treated as transfer-pending or candidate-scar surfaces
until wider replay evidence proves otherwise. Only
`source_record_packet_metadata_support` appeared on more than two fixtures in
that artifact set. The audit now also checks whether observed `_support`
predicates are currently implemented in the registered QA companion source. That
exposed `probate_storage_support` as an orphaned artifact helper: it appears in
historical probate QA outputs but has no current repo implementation, so those
rows should be treated as candidate-helper archaeology rather than promoted
architecture.
`docs/HELPER_LEDGER.md` is the durable rollup of this audit surface: each helper
gets fixture count, implementation status, class-audit counts, current read, and
next action.

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

The current incoming rule is now exercised on zip-delivered drops and loose
folders. Two authoring shapes are first-class:

- legacy source-plus-QA folders: `source.md`, `qa.jsonl`, and
  `fixture_notes.md`;
- sealed story zips: `story.md`, `qa_questions.md`,
  `qa_answers_private.jsonl`, `challenge_strategy.md`, and
  `anti_leakage_manifest.md`.

`scripts/validate_fixture_intake.py` validates both shapes without interpreting
source prose. `scripts/stage_incoming_fixtures.py` normalizes both shapes into
the promoted harness package: `source.md`/`story.md`, question-only `qa.md`,
question-only `qa_questions.jsonl`, scoring-only `oracle.jsonl`, fixture notes,
and progress scaffolds. The private answer file is preserved for audit but must
not enter compile or query-planning context.

The five 2026-05-04 zip fixtures were normalized, promoted into
`datasets/story_worlds`, and given `progress_journal.md` plus
`progress_metrics.jsonl` before baselining. The generated scorecard lives at
`tmp/story_world_zip_baseline_summaries/scorecard.md`; the durable lesson lives
beside each fixture.

The 2026-05-07 sealed story zip batch follows the same path through the updated
intake tools. Its first full-40 cold baseline is
`tmp/incoming_10_cold_qa_20260507/scorecard.md`: `276 exact / 44 partial / 80
miss` over `400` rows, with `0` write proposal rows and `0` runtime load
errors.

The same batch now has a row-gated high-water after candidate-mode farming:
`361 exact / 16 partial / 23 miss` over `400` rows (`90.25%`). The result is
artifact-first and selector-gated, not a single cold compile. The current best
selector artifacts are under `tmp/incoming_10_candidate_mode_selectors/`,
including:

- `clockmaker_object_registry_guarded_selector_v2.json`:
  `39 exact / 1 partial / 0 miss`;
- `nested_hearing_registry_guarded_selector_v2.json`:
  `40 exact / 0 partial / 0 miss`;
- `tournament_admin_guarded_selector_v2.json`:
  `37 exact / 3 partial / 0 miss`.

The durable lens lessons are captured in the fixture journals and
`docs/SEMANTIC_LENS_ROSTER.md`: evidence provenance and ledger/object
provenance are narrow pegboard lenses. They rescue explicit provenance rows but
regress broad legal, financial, or narrative rows when used as global compile
replacements.

The 2026-05-08 six-fixture administrative/story batch demonstrates the newer
GPU discipline: compile sparingly, select aggressively, and add helpers only
when the admitted KB already contains the needed arithmetic substrate. The cold
full-40 result was `186 / 16 / 38` over `240` rows (`77.5%`). Artifact selection
and scoped helper/compile work raised the row-gated high-water to
`223 / 6 / 11` (`92.9%`). A final residual repair pass then reached a
diagnostic row-gated `240 / 0 / 0` over the batch. This is not a single global
compile mode; it is the proof that every row has a reachable admitted surface
when the harness can select among existing and narrow repair artifacts. Proof
artifact:
`tmp/incoming_6_full40_qa_20260508/batch_exhaustion_proof_20260508.md`.

Census is the cleanest helper lesson: baseline `29 / 1 / 10`,
helper/accounting surfaces plus two scoped compiles, diagnostic upper bound
`40 / 0 / 0`, with the comparison artifact at
`tmp/incoming_6_full40_qa_20260508/census_multisurface_comparison.md`. The
other incoming-six lessons are row-shape transfer candidates: source lists,
last-confirmed-at, unresolved authority question answer surfaces,
rejected-version planning rows, and procedural date-event anchors.

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

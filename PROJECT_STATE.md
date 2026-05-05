# Project State

Last updated: 2026-05-05

## One-Sentence Shape

Prethinker is a governed natural-language-to-Prolog workbench: neural models propose semantic workspaces, deterministic gates decide what can become durable KB state, and the UI shows that process live. The product goal is not omniscience; it is to be hard to fool.

## Current Center

- Runtime: `src/mcp_server.py`, especially `process_utterance()`.
- Current pipeline reference: `docs/CURRENT_UTTERANCE_PIPELINE.md`.
- Clean harness daily driver: `scripts/run_kb_pipeline_clean_harness.py`, backed
  by `src/kb_pipeline_clean`, captures canonical structural signatures while
  delegating behavior to the live compiler/runtime path.
- Harness instrument reference: `docs/CURRENT_HARNESS_INSTRUMENT.md`.
- Research prioritization: `docs/ACTIVE_RESEARCH_LANES.md`.
- UI: `ui_gateway/`, served locally by `python ui_gateway/main.py` using the stdlib `ThreadingHTTPServer`.
- Active profile: `medical@v0`; active profile-lane experiments: `legal_courtlistener@v0` and `sec_contracts@v0`.
- Background domain asset: local UMLS Semantic Network KB built from `sn_current.tgz` for bounded medical type steering and explanation.
- Active architecture pivot: two-pass `semantic_router_v1 -> semantic_ir_v1`, using the LLM as the context/profile/action planner and the deterministic mapper as the admission authority.
- Active architecture frontier: multi-pass semantic compilation with safe-surface accumulation. Independent backbone/support/temporal/rule lenses can propose fragments, the mapper admits each lens independently, and deterministic union accumulates only admitted clauses.
- Active harness frontier: stenographer-mode simulation, where fixtures arrive as ordered utterance streams and Prethinker may only see the current turn plus prior admitted/pending state.
- Current development model: `qwen/qwen3.6-35b-a3b` through LM Studio/OpenAI-compatible structured output. This is the best-known local path, not a permanent product dependency.
- Current demonstration surface: prompt-book UI plus live ledger cards showing route, semantic workspace, deterministic admission, clarification, blocked execution, and KB mutation outcomes.

## Capabilities Live

- `process_utterance()` in `src/mcp_server.py` is the canonical runtime entrypoint. The UI, prompt book, and command-line harnesses exercise the shared server path rather than a forked demo lane.
- The active runtime path is `semantic_router_v1 -> semantic_ir_v1 -> deterministic mapper -> Prolog runtime`. Neural calls plan, segment, retrieve context, and propose operations; deterministic admission decides what can become KB state.
- Python no longer owns English-language interpretation in the active lane. It owns structure: validation, normalization of model-emitted fields, admission, execution, caching, scoring, and trace assembly.
- The mapper enforces predicate palettes, arity, argument-role contracts, placeholder guards, source/write boundaries, likely-functional conflict checks, temporal sanity checks, and profile-owned validators.
- The console can show write, query, clarification, blocked-admission, and mixed write+query turns. Ledger cards expose route, semantic workspace, deterministic admission, scoped diagnostic worlds, and KB mutation outcomes.
- Epistemic Worlds v1 preserves projection-blocked and supported-but-skipped candidates as scoped diagnostic memory rather than global truth.
- `semantic_ir_v1` supports entities, referents, ambiguities, source claims, propositions, candidate operations, truth-maintenance proposals, temporal graph proposals, and self-check diagnostics. Durable truth still flows solely through mapper-admitted operations.
- `kb_context_pack` gives the compiler exact relevant KB clauses, likely current-state candidates, entity candidates, recent committed logic, and a bounded fallback snapshot without granting context-sourced write authority.
- Multi-pass semantic compilation is now a named frontier: backbone, support, temporal/status, claim/source, and rule lenses can emit constrained fragments; the mapper admits each independently; deterministic union accumulates only admitted clauses.
- Rule ingestion now uses runtime verification: candidate clause admission, temporary load, body-goal/body-fragment support checks, fanout diagnostics, isolated per-rule trial, authored positive/negative probes, and promotion-ready filtering.
- Semantic shortcut auditing now has a first structural tool: `scripts/run_semantic_shortcut_audit.py` scans admitted Prolog surfaces for right-shaped/wrong-meaning risks such as unbound head variables, helper misuse, claim-to-fact collapse, broad class fanout, sibling masking, and aggregation overclaim.
- Post-ingestion QA has a governed symbolic retrieval path over compiled KB predicate inventories and admitted clauses. Evidence-bundle diagnostics can improve access, but cannot authorize writes.
- Clarification Eagerness is measurable across ask/no-ask posture, safe partial preservation, blocked-slot coverage, unsafe candidates, context-write hygiene, and source-context availability.
- `scripts/run_gateway_turnset.py` now records stenographer-mode metrics over the product gateway path: pending-before/after counts, queued-clarification counts, clarification-answer turns, delayed commits after clarification, segment holds, and authored structured expectation pass/fail counts.
- `medical@v0` remains bounded to memory-style predicates for medications, conditions, symptoms, allergies, lab tests/results, and pregnancy. UMLS support is profile-owned type steering, not broad diagnosis or treatment advice.
- CourtListener and SEC/contracts are starter domain lanes for claim/finding, citation-not-endorsement, docket-not-holding, filing/exhibit provenance, obligation-not-fact, condition-not-event, and breach-boundary tests.
- The default development model is `qwen/qwen3.6-35b-a3b` through LM Studio/OpenAI-compatible structured output. Other models are comparison/runtime-portability questions, not release gates.

## Recent Frontier Results

- Current full-suite verification: `603 passed, 2 subtests passed`.
- Iron Harbor: `86 exact / 14 partial / 0 miss` on a full 100-question source-document battery, with `0` write proposals during post-ingestion QA.
- Blackthorn: baseline first-20 was `2 exact / 1 partial / 17 miss`; current diagnostic lanes include BTC-022 at `82 / 9 / 9` full-100 and BTC-027 at `85 / 4 / 11`. These are different configurations, so compare within lane rather than treating one number as a universal replacement.
- Kestrel: profile-guided KCL-016 reached `73 exact / 11 partial / 16 miss` full-100 with `0` write proposals. Cold/source-aware evidence remains much lower, and the distinction is intentional.
- Anaplan Polaris: APR-016 reached `42 exact / 1 partial / 0 miss` on 43 QA by accumulating independent mapper-admitted support views over an admitted backbone.
- Glass Tide: separate rule lenses plus deterministic union now produce promotion-ready slices for role joins, threshold/exception rules, temporal clearance, salvage exceptions, budget-veto failure, and support-threshold conditions. Durable rule activation remains gated.
- Sable Creek: rule promotion probes now support structural any-of groups, and SC-007 shows rule composition improving full QA. A body-fact lens admitted `supported/2` vote rows; an aggregation lens derived `support_threshold_met`; the promotion-filtered threshold+vote union moved full QA from `20 exact / 8 partial / 12 miss` to `24 / 6 / 10` with `0` runtime errors and `0` write proposals.
- Query-mode activation now has deterministic structural and hybrid structural+LLM selector controls. Hybrid reached the Avalon Rule8 perfect-selector upper bound at `27 exact / 12 partial / 1 miss` while saving `13/40` LLM choices, but Three Moles and Sable regressed when the LLM fallback overrode structurally exact relaxed evidence. Treat this as a measured control surface, not a default QA policy.
- Clean KB pipeline factoring has a first daily-driver harness surface:
  `src/kb_pipeline_clean` owns the structural parity inventory and
  `scripts/run_kb_pipeline_clean_harness.py` replays current `process_utterance`
  behavior into canonical signatures. This is harness organization, not a
  behavior change.
- Story-world rule activation now has a cross-fixture transfer summary harness:
  `scripts/summarize_rule_activation_transfer.py` reads existing Sable/Avalon
  activation comparison artifacts and reports rescues, regressions, volatile
  rows, best-label counts, and activation-governor target buckets without
  rerunning compile or reading source prose. The current direct-2400 Sable/Avalon
  rollup has `54` stable rows, `15` nonbaseline rescue targets, `7`
  baseline-exact protection targets, and `4` volatile baseline-preferred rows.
  The direct selector now has an after-the-fact governor audit: `54/54` stable
  rows, `11/15` rescue rows, `6/7` baseline-exact protection rows, and `2/4`
  volatile baseline-preferred rows pass their target. The same report now emits
  `semantic_progress_assessment_v1`; current selector-governor failures produce
  `zombie_risk=medium` and
  `continue_only_with_named_expected_contribution`.
- Rule-activation selection has its first cleaner surface-guard replay across
  the same Sable/Avalon frozen artifacts. Reason-named guards now cover
  deferment rationale, component/rule-condition questions, recusal rationale,
  counterfactual recusal outcome, three-year window merit, amendment recall,
  rejection cause, and hypothetical reserve-status rows. Avalon reaches its
  upper bound at `32 exact / 7 partial / 1 miss` with `40/40` selected-best;
  Sable reaches its upper bound at `26 / 7 / 7` with `40/40` selected-best.
  The combined governor audit improves from `7` direct selector failures to
  `1`, with all `15/15` nonbaseline rescue targets and `7/7` baseline-exact
  protection targets passing. The remaining failure is a volatile
  prefer-baseline target, not a selected miss.
- Selector guard growth now has a family-level rollup:
  `scripts/summarize_selector_guard_families.py` parses selector guard reasons
  and writes `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`. Current inventory is `50`
  guard return sites, `49` unique guard reasons, `7` semantic families, and
  `0` unclassified. Use the family count to detect lens sprawl; individual
  row guards should stay diagnostic until they transfer or fold into a family.
- Semantic struggle detection is now a named structural guardrail in
  `src/semantic_struggle.py`. It turns pass contribution, duplicate, skip-heavy,
  stale-tail, and selector-governor telemetry into a stop/continue
  recommendation without reading source prose.
- Rule-acquisition promotion scoring now blocks repeated body-goal aliasing:
  duplicate body predicates that share multiple variables without distinct
  literal role anchors are unsupported fragments, while anchored Avalon-style
  multi-condition clauses remain allowed.
- The five challenge fixtures that arrived through `tmp/incoming` are now
  promoted into `datasets/story_worlds/`; `tmp/incoming*` is intake/staging
  only. Their first smoke scorecard remains useful historical evidence:
  `5/5` fixtures compiled, `44 exact / 4 partial / 2 miss` over `50`
  no-answer QA rows, and `0` write proposals.
- Incoming scorecard comparison is now an instrument gate:
  `scripts/compare_incoming_smoke_scorecards.py` compares baseline and
  candidate scorecards without source-prose interpretation. The first candidate
  check rejected a broad detail/specification guidance retry: it helped
  Meridian locally but regressed the batch to `41 exact / 4 partial / 5 miss`
  and increased misses by `3`.
- Incoming row-mode overlay planning is now available through
  `scripts/plan_incoming_row_mode_overlay.py`. A narrow evidence-bundle rerun
  over current non-exacts reached `46 exact / 1 partial / 3 miss`, which the
  promotion gate rejects because misses increased. The row overlay artifact
  still finds useful selector targets: two candidate rescues, one candidate
  regression, and three unchanged non-exacts.
- Selector comparison now handles fixture-scoped row ids and policy totals.
  On the six-row incoming non-exact target, structural selection picked the best
  available mode on `5/6` rows, while LLM `activation` selection picked `6/6`
  without source prose, answers, judge labels, or failure labels.
- A full first-10 replay over the three imperfect incoming fixtures tempered
  that result: evidence mode stayed at `44` exact but increased misses, while
  structural selector totals were `24 exact / 3 partial / 3 miss`. A selector
  JSON retry guard removed the Larkspur parse failure; activation then reached
  `23 / 5 / 2`, trading exact preservation for miss reduction. Activation
  remains a research control surface, not a daily-driver default.
- Protected selector mode is now implemented as `--selection-policy protected`.
  It uses structural selection by default and calls activation only for
  high-volume nonbaseline overrides. Incoming first-10 improved to `24 / 4 / 2`
  on the three imperfect fixtures, and Avalon reduced misses by one at the same
  exact count, but Sable failed to transfer. Treat it as calibration machinery.
- Guarded activation is the next named selector policy:
  `--selection-policy guarded_activation` keeps structural scoring for confident
  rows and uses activation plus bounded self-check evidence for uncertain rows.
  The selector can merge canonical QA mode artifacts with `+`, matching the
  smoke-scorecard first-pass + failure-classified view. On the ledger diagnostic
  for Larkspur, Meridian, and Northbridge, it selected the best available mode
  on `30/30` rows and reached `26 exact / 2 partial / 2 miss` across that
  three-fixture slice without source prose or answer keys in selector input.
  Transfer remains unsolved: Avalon still preferred `protected` for miss
  control, and Sable still preferred `direct`, so guarded activation is
  diagnostic machinery rather than a global default.
- Selector risk-gate planning is now available through
  `scripts/plan_selector_risk_gate.py`. It reads selector artifacts and optional
  transfer comparisons only, then labels rows as safe activation targets,
  calibration activation targets, baseline-protection targets, compile-repair
  targets, or stable. Current incoming guarded-activation rescues are
  calibration targets because Avalon/Sable transfer support is weak.
- Incoming scorecard comparison now protects row-level exactness: aggregate
  exact gains cannot promote a candidate that creates a visible baseline-exact
  regression. The scoped compile repair candidate improved the incoming batch to
  `45 exact / 4 partial / 1 miss`, but regressed Meridian q010, so the comparer
  reports `row_level_gate_required`.
- Row-gated incoming scorecard planning is now available through
  `scripts/plan_incoming_row_gated_scorecard.py`. Applying accepted scoped
  candidate rows while rejecting the Meridian q010 regression gives a protected
  incoming target of `46 exact / 4 partial / 0 miss` over the current
  five-fixture first-10 scorecard.
- Scoped compile repair plus evidence-bundle context filtering has now realized
  that target as an actual replay rather than a virtual overlay: the incoming
  high-water is `46 exact / 4 partial / 0 miss`, with `0` QA write proposals,
  `0` baseline-exact regressions, and a `promote_candidate` scorecard gate.
- Compile-variant overlay planning is now available through
  `scripts/plan_incoming_compile_variant_overlay.py`. A shifted
  Meridian/Northbridge compile candidate is aggregate-neutral at `46 / 4 / 0`,
  but complementary row surfaces imply a judged `48 exact / 2 partial / 0 miss`
  overlay target with exact-row protection.
- Narrative compile context now includes an attribute/duty guardrail: numeric
  character attributes should not be encoded as names or aliases, and named
  officials should preserve duty/authority surfaces when the profile supports
  them. The first Larkspur replay repaired q007 but stayed high-risk overall;
  adding it as a row-gated variant raised the judged overlay target to
  `49 exact / 1 partial / 0 miss`.
- Post-ingestion QA now has a deterministic official-identity companion over
  admitted rows: successful `person_role(Constant, Role)` queries also check
  authority/action predicates such as `ruling_by/3`, `permission_granted/2`,
  `official_action/3`, and `event_affects_person/3`. This repaired Larkspur
  q009, and the latest judged compile/query variant overlay target is
  `50 exact / 0 partial / 0 miss` with exact-row protection. This is a selector
  target, not a deployable oracle policy.
- `scripts/plan_incoming_variant_selector_training.py` now converts that judged
  overlay into selector/risk-gate training rows without reading source prose or
  raw compile outputs. The current official-companion overlay yields `4`
  activation targets, `3` exact-protection targets, and marks both nonbaseline
  variants `unsafe_global_variant_row_gate_required`.
- Guarded activation now treats relaxed-fallback-heavy and broad-row-volume
  structural winners as uncertain instead of confident. On the seven incoming
  variant calibration rows, the non-oracle selector improved to `6 exact / 1
  partial / 0 miss` and `6/7` best choices. The remaining Northbridge q007
  error needs requirement-detail relevance, not more row-volume scoring.
- Activation selection now has that requirement-detail relevance guard:
  count-only/status-only support is partial when another mode returns
  answer-bearing details such as spacing, interval, threshold, scope,
  condition, duration, unit, or authority. The seven-row incoming variant
  calibration slice now reaches `7 exact / 0 partial / 0 miss` and `7/7` best
  choices without source prose or judge labels in selector input.
- Full first-10 variant selection over Larkspur, Meridian, and Northbridge now
  reaches `30 exact / 0 partial / 0 miss` and `30/30` best choices with no
  selector errors. With Copperfall and Harrowgate's clean baseline rows, the
  promoted incoming batch has a current best first-10 row-gated harness result
  of `50 / 0 / 0`.
- Requirement-detail guarded selection has been transfer-checked against older
  Avalon/Sable rule-activation packs. Avalon moved to `28 exact / 10 partial /
  2 miss` with `35/40` best choices, a small miss reduction versus the previous
  guarded replay; Sable stayed at `25 / 6 / 9` and `37/40`, so direct selection
  still wins there. Treat the guard as row-level harness machinery, not a
  global default policy.
- Promoted story-world full-40 replay now gives the batch a broader scorecard:
  all five fixtures compiled, `200/200` QA rows parsed, no runtime load errors,
  and `0` write proposals. After failure-surface classification the scored
  surface is `154 exact / 20 partial / 26 miss`; active repairs are `39`
  compile-surface gaps and `7` helper/query-join gaps. The next frontier is
  scoped source-surface acquisition, not broader selector prompting.
- A Larkspur source-entity-ledger/state-custody variant is a negative
  diagnostic: compile shape improved to `149` admitted operations and `1` skip,
  but full-40 QA regressed to `18 / 10 / 12` with `7` baseline-exact
  regressions. Do not promote broad ledger prompting; use narrower
  state-transition, custody-chain, permission/rationale, and final-state passes
  with exact-row protection.
- Larkspur targeted-state lensing now gives a row-gated lift. The variant alone
  is unsafe at `14 / 8 / 18`, but the overlay target is `23 / 6 / 11`. A new
  selector uncertainty trigger for who-is identity rows protects explicit
  name/identity support from being outranked by authority-row volume. Guarded
  activation with identity, rationale/contrast, and capability-failure guidance
  reaches `23 exact / 8 partial / 9 miss`, `39/40` best choices, and `0`
  selector errors on Larkspur full-40.
- Story-world full-40 repair planning is now artifact-only and lens-named:
  `scripts/plan_story_world_repair_targets.py` reads scorecards, extracts query
  predicate names, and groups repair targets without source-prose
  interpretation. The five-fixture queue remains `46` rows, but Larkspur now
  has a concrete acquisition split: `6` object-state, `5` object-location or
  custody, `4` permission/rationale, `2` outcome/status, `1` claim-truth, `1`
  identity/role, and `1` temporal target. A direct `story_world@v0` registry
  compile was a negative acquisition check: clean but too thin (`0/0/6`,
  `0/2/2`, and `0/0/5` on targeted Larkspur QA slices), so the next move is
  richer focused acquisition rather than registry-only compilation.
- LM Studio base-url handling in the domain-bootstrap runner now accepts either
  root URLs or `/v1` URLs before appending `/v1/chat/completions`. That fixed
  the empty profile/intake responses seen under the Larkspur acquisition run.
  With the URL fix, the permission/rationale lens became a strong row-gated
  candidate: target QA `5 / 0 / 0`, full-40 `31 / 3 / 6`, `0` write
  proposals, but `6` baseline-exact regressions. Treat it as an acquisition
  variant for row gating, not a global replacement compile.
- Guarded activation now has answer-surface baseline guards for identity rows,
  award/result rows, and direct status/rule rows. On the Larkspur
  permission/rationale full-40 pair, the first guarded selector reached
  `34 / 4 / 2` with `37/40` best choices; the guarded selector with these
  named guards reaches the judged row-gated upper bound at `37 / 2 / 1`,
  `40/40` best choices, and `0` selector errors without source prose, answer
  keys, judge labels, failure labels, gold KBs, or strategy files in selector
  input.
- The five incoming challenge fixtures have been promoted into
  `datasets/story_worlds/` with standard source, QA, oracle-for-scoring,
  `progress_journal.md`, and `progress_metrics.jsonl` files. `tmp/incoming*`
  is now explicitly treated as short intake/staging only; the durable research
  record lives beside the other fixtures.
- The next five zipped incoming fixtures are also promoted and baselined from
  `datasets/story_worlds/`: Ashgrove Permit, Fenmore Seedbank, Greywell
  Pipeline, Heronvale Arts, and Veridia Intake. All `5/5` compiled; first-pass
  QA over `123` rows scored `94 exact / 13 partial / 16 miss` with `0` write
  proposals and `0` runtime load errors. The classified repair rollup is
  `97 / 11 / 15`, with failure surfaces `16` compile, `8` hybrid/join, and
  `2` answer. Heronvale is the only medium semantic-progress risk; Veridia is
  the new turnstream/stenographer-adjacent correction fixture.
- The first honing pass on that batch produced `operational_record_status_v1`.
  As a global compile candidate it is rejected (`96 / 20 / 7` versus baseline
  `97 / 11 / 15`) because it creates `15` baseline-exact regressions, but the
  row-gated artifact target is strong (`111 / 11 / 1`). A no-oracle selector
  guard now sends operational/status rows to activation when structural
  selection prefers baseline but a competing mode has specialized record-state
  evidence. That lifts the selector from `99 / 17 / 7` to `101 / 17 / 5`;
  Greywell reaches its per-row upper bound at `24 / 1 / 0`. The next
  selector-only guard, `selector_baseline_readiness_guard`, protects direct
  baseline application/status, counterfactual rule, and hold-readiness support
  from broad or relaxed-heavy candidate surfaces. Over the same frozen `123`
  rows it lifts the selector to `106 / 12 / 5` and selected-best rows to
  `117/123`, with no new misses. A follow-up
  `selector_question_act_guard` then fixes two remaining hard misses:
  request-filing timeliness now prefers request/reinstatement threshold
  evidence over completion-window evidence, and commit-readiness now prefers
  unresolved-process evidence over a bare status value. The full stochastic LLM
  replay is `106 / 14 / 3`, so exact count is flat but hard misses fall from
  `5` to `3`; record this as miss-discipline progress plus visible selector
  variance, not as a clean exact-count lift. The next
  `selector_surface_specificity_guard` adds explicit rationale-note,
  decision-status, and priority-surface guards. It reaches `110 / 10 / 3` with
  `121/123` selected-best rows; Ashgrove, Greywell, and Veridia are now at
  their per-row selector upper bounds. The complete-selector follow-up adds
  split-rationale, current-constitution, and resubmission proof/rule guards.
  It reaches `111 / 11 / 1`, matches the frozen-artifact upper bound, and
  selects the best available mode on `123/123` rows. The remaining miss is an
  artifact/evidence limitation, not a selector-choice miss.
- Fenmore then turned that limitation into a useful row-level acquisition
  result. A rationale/contrast source-note lens is unsafe globally (`17 / 1 /
  7` on Fenmore full-25), but as a third selector mode it repairs the Vault 4
  conservation-versus-viability rows. New guards for explicit source-note
  rationale, viability-concern contrast, pending-test status, direct collector
  identity, and failed-viability threshold/storage protection move Fenmore to
  `24 / 1 / 0` with `25/25` selected-best rows, matching the available
  three-mode upper bound. This is a compile-lens gain plus selector restraint,
  not a global prompt promotion.
- The rationale/contrast lens now has a targeted transfer check across
  Ashgrove, Fenmore, Greywell, Heronvale, and Veridia. On `52` rows that ask
  about reasons, non-reasons, evidentiary status, current position/status,
  correction, and commit-readiness, the selector reaches `49 / 3 / 0` and
  `52/52` selected-best rows, matching the available upper bound. New named
  guards cover current operational final-state, evidentiary report surface,
  board concern event/action history, and commit-readiness process evidence.
  Full-25 parallel QA over the four transfer fixtures was too heavy for the
  current LM Studio setup, so targeted transfer slices are the practical lane
  until the orchestration layer can throttle long judging runs.
- The older-fixture rationale/contrast transfer diagnostic keeps that result
  bounded. Four focused compiles plus targeted QA over Larkspur, Northbridge,
  Copperfall, and Meridian scored `17 exact / 9 partial / 7 miss` across `33`
  reason/status/authority/correction rows with `0` write proposals and `0`
  runtime load errors. Northbridge (`4 / 1 / 1`), Copperfall (`7 / 2 / 2`), and
  Meridian (`2 / 0 / 0` on a tiny slice) show useful transfer for
  discrepancy/authority, correction/status, and counterfactual surfaces.
  Larkspur stayed hard at `4 / 6 / 4`; its misses are mostly compile-surface
  gaps around narrative motive, custody, and object-state rationale. The next
  frontier is a stronger Larkspur acquisition contract, not a broader
  rationale prompt.
- Larkspur now has that stronger acquisition contract in first form:
  `final_object_state_transition_surface` compiled healthy (`98` admitted,
  `14` skipped) and scored `36 exact / 2 partial / 2 miss` on full-40, with
  `0` writes and `0` runtime errors. It improves `18` baseline non-exact rows
  and creates one baseline-exact regression, q009 official identity. The
  companion `permission_motive_rationale_surface` is target-useful (`3 / 2 /
  0`) but globally unsafe (`16 / 12 / 12`); `custody_ownership_chain_surface`
  is weak overall (`1 / 1 / 3`) but gives an exact q038 custody row; a new
  official-identity micro-lens did not solve q009. The judged artifact overlay
  opportunity is now visible: state lens for most rows, old permission/rationale
  for q011/q036, custody for q038, and protected original baseline q009 gives a
  `40 / 0 / 0` row target, but q009 still needs retained selector evidence or a
  better official-identity acquisition surface before this can become a
  non-oracle selector run.
- That last Larkspur obstacle is now solved as a row lens. The
  `official_role_authority_definition_surface` compile scored q009 exact by
  preserving role authority/duties separately from action examples; globally it
  is unsafe (`21 / 9 / 10`), so it remains a selector-only surface. The
  guarded selector over four persisted artifacts - state, old
  permission/rationale, role-authority, and custody - initially reached `35 /
  3 / 2`; after reason-named surface guards for superlative identity,
  official-role definition, current component state, custody-transfer
  rationale, and award placement, it reaches `40 / 0 / 0` and `40/40`
  selected-best rows without source prose, answer keys, judge labels, failure
  labels, or gold KBs in selector input. This is the first full Larkspur
  selector closure over frozen artifacts.
- State-lens transfer is now bounded. The same final-state acquisition contract
  is not a universal story-world fix: Three Moles targeted final-state rows
  scored `0 / 2 / 7`, Otters scored `1 / 0 / 14`, and Calder's Reach scored
  `10 / 2 / 8` on a final-status/ownership slice. The useful distinction is
  now sharper: Larkspur had compact named-device state transitions that the
  lens could acquire; Otters/Three Moles need richer event-spine/restitution
  coverage, while Calder needs correction/current-state conflict resolution.
- Calder now validates the multi-surface overlay shape on a long-state ledger.
  Current-state conflict alone was weaker (`6 / 2 / 12`), possession/inheritance
  tied final-state exact count (`10 / 1 / 9`), and legal-title/default was
  weak globally (`6 / 2 / 12`), but the four persisted artifacts expose a
  `14 / 3 / 3` upper bound on the same 20-row final/current-state slice.
  Refined reason-named guards for role reinstatement, carry/possession,
  possession-vs-ownership, legal title transfer, contract authority, and
  guardianship resumption let the guarded selector reach that upper bound with
  `20/20` selected-best rows and `0` selector errors.
- The new selector guards have an anti-overtune replay: Larkspur state overlay,
  Fenmore rationale/contrast, and the Ashgrove/Greywell/Heronvale/Veridia
  operational-record overlays were rerun against frozen artifacts after the
  Calder guards landed. The clean replay covers `163` rows and matches each
  fixture's available upper bound: `153 exact / 10 partial / 0 miss`,
  `163/163` selected-best rows, and `0` selector errors. An initial Ashgrove
  run exposed a transient LM Studio HTTP 500 fallback on q005; rerun recovered
  the prior upper-bound result, so record this as orchestration variance rather
  than a semantic regression.
- Oxalis now shows the next non-story-world access frontier. Replaying
  evidence-bundle planning/execution/context filtering over the frozen OX-003
  compact-flat compile moved full-40 QA from `27 / 8 / 5` to `32 / 6 / 2`.
  Plain-vs-evidence artifacts expose a `33 / 6 / 1` upper bound; refined
  regulatory answer-surface guards for universal-scope enumeration,
  termination-denial quantity thresholds, target-lot exclusion, and
  counterfactual reclassification deadlines let guarded selection reach that
  upper bound with `40/40` selected-best rows and `0` selector errors.
- Incoming compile repair targets are now generated at
  `tmp/incoming_smoke_summaries/compile_repair_targets.{json,md}`. The current
  scoped-evidence queue is down to four partial rows: `3` scoped source-surface
  repair targets and `1` helper/query-join repair target.
- Clarification Eagerness Trap: source-context lane reached and held `40/40`, with `0` unsafe candidates, `0` context-write violations, and `10/10` blocked-slot coverage.
- New held-out fixtures such as Black Lantern, Three Moles, Oxalis, Dulse, Avalon, Sable Creek, Ridgeline, Veridia, and Ledger are being used to test whether gains transfer beyond the original fixture families.
- Active lane triage now prioritizes source-surface acquisition first because the cold rollup shows `159` compile gaps versus `35` hybrid/reasoning, `26` query, and `5` answer gaps.
- Three Moles: ledger `coverage_targets` plus scoped partial-skeleton recovery produced the current story-world high-water at `24 exact / 6 partial / 10 miss` under evidence-filter QA. The same broadening failed to transfer globally to Oxalis, so the recovery rule is scoped to ledger-backed narrative passes.
- Declaration and Proclamation show that curated document/profile vocabulary can improve dense source compilation, but expected-signature recall alone is not enough; question-support coverage is the next scoring layer.
- Otters remains a hard story-world frontier. Recent cross-apply work did not beat the earlier high-water; the next useful move is a ledger-to-compile contract with row-class floors.

## Known Issues / Sharp Edges

- Predicate canonicalization remains hard. Profile registries, aliases, argument-role contracts, and semantic shortcut audits reduce drift, but right-shaped/wrong-meaning candidates are still possible.
- Temporal representation is useful but incomplete. Ordering and selected helpers work; richer date arithmetic, interval validity, status-at-time, and correction propagation need more substrate.
- Rule promotion is not rule activation. A rule can pass isolated probes and still hurt global QA if activated indiscriminately; row-level activation and branch-union policy are active research.
- Multi-pass lensing can add surface area without answer lift. Each lens needs contribution accounting, duplicate/conflict tracking, and QA lift per admitted clause.
- Query and answer surfaces can bottleneck even when compile quality is good. APR made this especially clear: the KB already had useful rows before the QA planner learned how to ask for them.
- Hybrid query-mode selection is not automatically better than structural selection. On story-like evidence, the model can distrust relaxed but answer-bearing rows; fallback should be gated by row-level risk, not invoked just because structural evidence is partial.
- Clarification Eagerness depends on an explicit authority surface. Runs without source-context support can regress even when the apparent ask/no-ask posture is reasonable.
- Stenographer mode is only partially exercised. The gateway already handles turn-by-turn clarification, current-turn query-boundary segmentation, and a first `clarification_delivery_policy=queued` ledger. Fixture scoring for queued-slot closure, safe partial preservation under queued delivery, interrupted clarification, and sentence-at-a-time atom continuity is new.
- Domain packs are legitimate product context; gold KBs, answer keys, and input-specific oracle hints are calibration material only. Evidence lanes must stay labeled.
- Story-world ingestion still struggles with stable object identity, event spine completeness, causality, speech-vs-truth, subjective judgment, and final-state repair under one compact source surface.
- The no-big-local-GPU path is planned but not yet a first-class setup. Hosted OpenAI-compatible backends need structured-output smoke allowlisting plus cost/latency guidance.

## Detailed Current Notes

This section keeps useful current detail for maintainers. Public-facing pages should lead with the capability and frontier-result summaries above, then link into fixture ledgers for the long run histories.

- The medical profile normalizes a bounded predicate palette: medication use, conditions, symptoms, allergies, lab tests, lab result states, and pregnancy.
- Clarification turns can prevent unsafe patient or lab-test guesses.
- Clarified medical restatements can now recover useful KB writes, such as resolving vague pressure language into a high blood-pressure measurement.
- Session reset now clears pending clarification, recent runtime memory, trace state, and runtime KB state.
- The UI can demonstrate write routes, query/clarification routes, mutation telemetry, and prompt-book-driven examples.
- The UI pipeline trace now makes Epistemic Worlds visible as a two-zone firewall: admitted operations that can mutate the global KB versus scoped diagnostic worlds for blocked, quarantined, or supported-but-skipped candidates.
- The UMLS Semantic Network builder produces local Prolog facts for semantic types, semantic relations, structural rows, and inherited relation closures.
- The current Semantic IR runtime path can route and commit safe direct assertions without running the legacy parse-side English rescue chain.
- The current semantic IR edge battery shows `qwen3.6:35b-a3b` holding difficult provenance, temporal, exception, correction, and counterfactual distinctions with `20/20` decision labels and `0.976` average score in runtime A/B.
- A 10-case weak-edge fix pass now reaches `10/10` decision labels and `1.000` average score, with zero non-mapper parse rescues.
- Silverton probate packs are intentionally hard frontier batteries for claim/fact separation, identity ambiguity, temporal intervals, noisy spelling, multilingual fragments, and policy-label calibration. They are pressure gauges, not polished demo headlines yet.
- `medical@v0` now owns its UMLS semantic-group argument contracts in the profile manifest, so medical type steering stays profile-specific instead of leaking into the generic semantic IR mapper.
- The semantic IR mapper now has a structural placeholder-argument guard for writes and a minimal temporal fact vocabulary for dates, intervals, and temporal corrections.
- The semantic IR contract now allows `operation=rule` candidates to carry an executable `clause`, which lets structured-output model runs produce durable Prolog rules instead of only recognizing rule-like language.
- Runtime admission now has a first stored-logic conflict guard: likely-functional current-state overwrites and simple `may_*`/`cannot_*` modal contradictions are blocked before mutation.
- Local model-family testing shows model choice still matters even with LM Studio structured output. Nemotron underfit the current contract, Gemma 26B was a serious different-family challenger, and `qwen/qwen3.6-35b-a3b` remains the default development model.
- The A/B harness now separates exact decision labels, safe outcomes, semantic extraction score, and final KB safety, so hard packs can distinguish product-policy misses from unsafe KB writes.
- The noisy Silverton frontier improved through structural mapper policy: query-scoped identity premises stay out of the KB, initial-only person aliases project state writes to `mixed`, and claim-only wrappers with unsafe implications project to `quarantine`.
- Semantic IR candidate operations now go through deterministic predicate-palette admission. Out-of-palette assert/query/retract/rule predicate signatures are skipped with diagnostics before they reach the legacy parse shape.
- The final noisy Silverton miss was repaired by projecting speculative ambiguous observations with no safe operation to `quarantine`.
- The Harbor frontier pack now has admission-level contracts for selected scenarios: expected admitted facts/retracts/queries, forbidden admitted facts, skipped operations, and skip reasons.
- Predicate contracts can now be supplied in Semantic IR input payloads so a predicate's argument roles and ordering are explicit instead of being hidden in test expectations.
- The mapper now enforces obvious predicate-contract argument role mismatches. This extends palette admission from "is this predicate name/arity allowed?" to "do the proposed arguments fit the contract shape?", while leaving domain vocabulary in profile packages.
- Profile packages can now carry declarative admission validators on predicate contracts. The first legal and SEC validators block allegation-shaped `finding/4`, citation/unclear `holding/3`, obligation-shaped `breach_event/2`, and unevidenced `condition_met/2` proposals without baking those rules into the generic mapper.
- The mapper now has a first temporal sanity gate for interval facts: a proposed `interval_start/2` plus `interval_end/2` pair with parseable dates is skipped if the start is after the end.
- Admitted Semantic IR clauses now carry first-pass support records from mapper operation to runtime payload. Each support record includes the originating operation index, predicate, source, polarity, and rationale codes, giving the trace a seed for future dependency/truth-maintenance work.
- `semantic_ir_v1` now has a first-class `truth_maintenance` proposal block. The large model can propose support links, conflicts, retraction plans, and derived consequences; the mapper only copies that structure into diagnostics/traces and still admits durable effects exclusively from `candidate_operations`.
- Admission diagnostics now compare the model's `truth_maintenance` proposal against mapper outcomes. Trace reports show support/conflict/retraction/consequence counts plus fuzzy edges such as admitted operations without model support, skipped operations with model support, conflict-policy mismatches, and retraction-plan/admitted-retract mismatches.
- `semantic_ir_v1` now has an optional proposition spine as a v1-compatible bridge toward `semantic_ir_v2`: `propositions[]` records what the model thinks the text means, and `candidate_operations[].proposition_id` links proposed effects back to those meaning candidates. This is diagnostic only; durable truth still flows solely through mapper-admitted operations.
- The Iron Harbor source-document benchmark now has a full 100-question run at `86 exact / 14 partial / 0 miss`, up from the prior best `81 / 14 / 5`. The improvement came from backbone-plus-detail source compilation and QA planner support-shape guidance, not Python prose interpretation.
- `datasets/story_worlds/blackthorn_misconduct_case/` is now the hostile procedural-misconduct frontier fixture. It packages a university research-integrity source file, gold Prolog KB, 100-question QA battery, first-20 support map, failure buckets, fixture-owned ontology registry, and progress ledger. The current exact high-water run is BTC-027 at `85 exact / 4 partial / 11 miss`, with `0` write proposals, using evidence-bundle context filtering with a small broad-clause floor. BTC-023 still has the stronger exact-plus-partial split at `83 / 10 / 7`. BTC-024 post-run failure-surface classification split the BTC-023 remaining 17 non-exacts into 9 compile-surface gaps, 5 hybrid-join gaps, 2 query-surface gaps, and 1 answer-surface gap, suggesting Blackthorn is ready for compact question-shaped KB context and hybrid join support rather than simple predicate widening.
- `datasets/story_worlds/kestrel_claim/` is now the maritime-insurance frontier fixture. It packages a source dispute record, oracle-only gold KB, 100-question QA battery, failure buckets, first-20 support map, a non-oracle starter domain profile, and a progress ledger that separates cold/source-aware/profile-guided evidence lanes. Current best source-aware non-registry run is KCL-007 at `14 exact / 2 partial / 4 miss` first-20 and `30 exact / 12 partial / 58 miss` full-100. Current profile-guided high-water is KCL-016 at `73 exact / 11 partial / 16 miss` full-100 after query-review, a richer non-oracle insurance-detail compile, deterministic admitted-clause union across two safe compiles, and source-faithful temporal atom parsing; KCL-015 also reached `20 exact / 0 partial / 0 miss` on first-20. KCL-017 failure-surface classification says 20 of 27 non-exacts are compile-surface gaps; KCL-018 broad-floor context filtering rescued 4 of those 27, and KCL-019 row-class focused compile union rescued 5 while lowering compile-surface gaps on the weak slice from 16 to 13. Kestrel remains primarily source-surface limited.
- `datasets/enterprise_guidance/anaplan_polaris_performance_rules/` is now the first enterprise technical-guidance fixture. It packages a Polaris performance-tuning guidance source, oracle-only gold KB, 43-question QA battery, failure buckets, a non-oracle starter profile, and a progress ledger. APR-001 profile-guided baseline compiled `136` admitted operations with `186` skips and scored `29 exact / 6 partial / 8 miss` over 43 QA with `0` write proposals. APR-005 is the current single-compile exact high-water at `37 exact / 1 partial / 5 miss`; APR-010 raised the answer surface to `37 exact / 4 partial / 2 miss` by deterministic union of two safe admitted compile surfaces using `scripts/union_domain_bootstrap_compiles.py`. APR-016 is the current high-water at `42 exact / 1 partial / 0 miss`: it kept the default enterprise profile unchanged, used `scripts/run_support_acquisition_pass.py` for independent support-only source passes over the raw source plus APR-010's admitted backbone, then deterministically unioned the mapper-admitted support views into a `296`-fact surface with `0` runtime load errors and `0` QA write proposals. APR-006/APR-007 showed that broader causal-cue prose pressure and answer-shaped typed rationale predicates both regress the default compile; APR-011 showed that executing evidence-bundle plan queries can add answer-surface noise. Current lesson: preserve the backbone first, then acquire and accumulate rationale/effect/tradeoff support rows in separate safe passes.
- `datasets/story_worlds/glass_tide_charter/` is now the rule-ingestion frontier fixture. It packages a dense charter/rule source, oracle-only gold KB with executable Prolog rules, 100-question QA battery, first-20 support map, failure buckets, generic non-oracle starter profile, and progress ledger. GLT-001 exposed cold profile-bootstrap JSON overflow; compact rule-source profile guidance fixed that in GLT-009, which parsed cold, admitted `274` operations, and reached first-20 QA `13 exact / 3 partial / 4 miss` with no starter registry. GLT-002/003 showed that broad compiles preserve source rules as records but admit `0` executable rules. GLT-004 through GLT-008 introduced `scripts/run_rule_acquisition_pass.py`: a separate rule lens can admit executable clauses, but runtime trial exposed the true frontier: overgeneralized class-predicate fanout versus clean but dormant rules whose bodies lack matching backbone facts. GLT-023 through GLT-039 now show the emerging rule-acquisition method: body-fact lenses, active predicate palettes, helper substrates, isolated per-rule promotion trials, combined authored probes, deterministic rule-surface union, intermediate `derived_condition/3` rows, and promotion filtering. Current promotion-ready slices cover role-joined repair authorization, tax threshold plus relief exception, salvage reward exception, temporal quarantine clearance, council budget-veto failure, and council support-threshold condition; durable product rule promotion remains intentionally separate.
- `datasets/clarification_eagerness/clarification_eagerness_trap/` is now the first CE-first fixture. It packages a small charter/procedure/case-file source, a compact clear answer key, 20 ingestion clarification-eagerness cases, 20 query clarification-eagerness cases, 10 baseline QA probes, expected CE behavior, and machine-readable JSONL views of the authored tables. The fixture measures when Prethinker should ask, when it should commit safe partials, when it should source-attribute or quarantine without asking, and when query ambiguity should become a clarification instead of a guessed answer. CET-013 held the source-context lane at `40/40` after the latest rule-admission changes, with `0` unsafe candidates, `0` context-write violations, `10/10` blocked-slot coverage, and safe partials at `11/13`. The scorer now separates ask/no-ask posture from safe partials, context-write hygiene, authored blocked-slot coverage, and source-context availability.
- `datasets/story_worlds/black_lantern_maze/` is the hostile confusion frontier fixture for claim/finding/fact separation, title-time identity, near-name aliases, multilingual notes, overloaded approval semantics, correction safety, helper-supported rules, priority/anti-rule behavior, and CE over/under-eagerness. The cold lane has since run it; evidence-bundle context filtering lifted one unchanged compile from `27 exact / 7 partial / 6 miss` to `32 exact / 3 partial / 5 miss`, and a broader fallback held `32` exact while reducing hard misses to `3`. The remaining lesson is row-level activation, not more global context.
- `datasets/story_worlds/three_moles_moon_marmalade_machine/` is a source-plus-QA-only story-world fixture. It intentionally has no gold KB, no strategy notes, and no ontology registry. A diagnostic replay added pass-contribution accounting: the event/causal lens initially contributed `0` unique rows, then a compact focused-pass retry recovered `28` unique rows while QA stayed mostly flat. This made lens usefulness measurable instead of aesthetic.
- Post-ingestion QA now has optional `evidence_bundle_plan_v1`, `--execute-evidence-bundle-plan`, `--evidence-bundle-context-filter`, and `qa_failure_surface_v1` diagnostics. These passes see only the compiled KB predicate inventory, relevant admitted clauses, emitted query rows, query results, the current question, and, for failure classification, the benchmark reference answer. They do not see the raw source document and cannot authorize writes. `scripts/run_support_acquisition_pass.py` is a separate compile-surface experiment rather than a QA shortcut: it sees raw source plus an admitted backbone, emits only support/rationale operations, and still goes through mapper admission. APR-016 showed multi-support acquisition plus safe union is stronger than widening the default profile. BTC-026 showed plan-shaped context can rescue focused hard rows but needs a broad-context floor before becoming a default.
- `semantic_ir_v1` now has an optional `temporal_graph_v1` proposal block for event nodes, time anchors, intervals, and ordering edges. It is deliberately diagnostic: the mapper surfaces the graph in traces but does not write temporal facts unless matching `candidate_operations` independently pass admission.
- A first deterministic temporal kernel now sits beside `temporal_graph_v1`: admitted `before/2` facts can support `after/2`, transitive `precedes/2`, `follows/2`, and coarse `concurrent/2` queries through Prolog rules instead of model-side reasoning. Its predicate contracts are loaded as a cross-cutting context module alongside selected domain profiles.
- Stored-logic admission now treats `event_on/2`, `interval_start/2`, and `interval_end/2` as likely functional temporal anchors: a replacement anchor for the same record is blocked unless the Semantic IR includes an explicit retract/correction plan.
- Low-risk correction projection now treats an unsafe implication that merely repeats the stale fact being retracted as duplicate diagnostic residue, not a reason to downgrade the safe retract/assert mutation plan.
- Semantic IR calls now receive a compact deterministic `kb_context_pack`: exact relevant KB clauses, likely functional current-state candidates, entity candidates, recent committed logic, and a small fallback snapshot. This gives the 35B model current-KB visibility for corrections and conflict reasoning without granting it write authority.
- `kb_context_pack` now includes role-aware `current_state_subject_candidates`, and the Semantic IR prompt payload carries explicit `kb_context_policy` guidance. This teaches the model how to use retrieved KB state for correction, pronoun resolution, claim-vs-observation boundaries, and conflict explanation without expanding Python-side language patches.
- `semantic_ir_v1` payloads now carry a first-class `document_to_logic_compiler_strategy_v1` context object. It captures the Codex-style mental procedure for source boundary, assertion status, entity selection, predicate selection, repeated structures, truth maintenance, and query planning, while preserving the rule that runtime admission remains the only write authority.
- `scripts/run_semantic_ir_lava_sweep.py` now provides a broad mixed-domain lava harness. It balances scenario sources, generates typo/bad-grammar/context-switch variants, can repeat temperature-0 runs for signature variance checks, applies admitted writes to a private stream KB, and records admitted queries without executing them by default so recursive toy-Prolog queries cannot monopolize CPU.
- The console now defaults to the current LM Studio Semantic IR lane (`qwen/qwen3.6-35b-a3b`) instead of the former Ollama parser path.
- Long story-like utterances in the UI can use segmented Semantic IR ingestion: the gateway splits the narrative into focused segments, processes each through the canonical `process_utterance()` path, dedupes applied mutations, and exposes segment-level workspace/admission traces.
- Mixed long utterances can now segment at query boundaries, so questions do not pile up in the same semantic workspace as surrounding write facts.
- The generic predicate registry now includes a small story-world event/state palette (`tasted/2`, `sat_in/2`, `lay_in/2`, `broke/1`, `asleep_in/2`, `was_tasted/1`, `was_eaten/1`, `was_sat_in/1`, `was_lain_in/1`, etc.) so narrative ingestion no longer has to squeeze ordinary events into `inside/2`, `at/2`, or `carries/2`.
- The mapper now blocks placeholder-like durable write arguments such as `unknown_agent`, while the prompt steers unknown-actor observations toward passive object-state predicates when those are available.
- `datasets/story_worlds/otters_clockwork_pie/` is now the main playful-but-hard story-world frontier fixture. It includes a source-local Goldilocks-shaped story, human gold KB, 100-question QA battery, failure buckets, ontology registry scaffold, and an append-only progress ledger for graphing runs.
- Otters OTR-001 through OTR-007 plus OTR-006Q are the first mini-journal series. The cold baseline scored `7/20` exact first-20 QA and `0.000` emitted/gold predicate-signature recall. OTR-003 remains the best first-20 QA support point at `8/20` exact plus `3/20` partial. OTR-006, which gives the model the fixture ontology registry as vocabulary but not facts, is the best compile-alignment point so far at `0.195` emitted/gold signature recall and `0.917` precision. The series exposed a real tradeoff between coverage, canonical predicate alignment, source-local control-plane vocabulary, and query planning.
- Raw-file story compilation now has generic narrative-source context pressure selected from LLM-owned intake classification or explicit domain hint. It asks the model for story spine, event order, speech/truth separation, subjective judgments, causality, remediation, and final-state support without Python inspecting the prose for meaning.
- `medical@v0` Semantic IR calls now receive profile-owned predicate contracts and compact UMLS bridge context before the model proposes a workspace. This lets the model normalize examples like `Coumadin` to `warfarin` and see argument-role/semantic-group expectations, while the deterministic mapper still owns admission.
- The profile context now explicitly treats an explicit named patient as sufficient grounding for the research profile, while pronouns, multiple candidates, aliases, and missing patient identity still require clarification.
- A thin domain-profile roster now exists in `modelfiles/domain_profile_catalog.v0.json` and is included in Semantic IR input as `available_domain_profiles`. This is the first skill-directory-style control-plane hook: it advertises possible profile contexts without loading every thick package or authorizing writes.
- `active_profile=auto` now uses model-owned `semantic_router_v1` as the first-pass context/profile/guidance controller before the Semantic IR compiler. It emits a strict control-plane JSON object, loads only the selected profile context/contracts, and never authorizes writes.
- `semantic_router_v1` now emits an explicit `action_plan` block inspired by adaptive staged-reasoning work such as AdapTime. The router can request focused actions such as `compile_semantic_ir`, `segment_before_compile`, `include_kb_context`, `include_temporal_graph_guidance`, `include_truth_maintenance_guidance`, `extract_query_operations`, `review_before_admission`, `profile_bootstrap_review`, or `ask_clarification_first`. This is context choreography only; it does not authorize facts, rules, queries, or writes.
- Router action plans are now projected into compact `router_action_policy:` lines in the Semantic IR `domain_context`. The compiler receives focused pressure such as explicit query extraction, KB-context use, truth-maintenance guidance, review-before-admission, and clarification-first behavior without Python interpreting the utterance text.
- Profile packages still own declarative `selection_keywords`, `selection_hints`, predicate contracts, and domain context, but those are now context assets for the router/compiler rather than a Python keyword selector.
- The former Python catalog selector has been removed from the active runtime and research harnesses. Current traces and metrics center router quality, compiler validity, admission diagnostics, and anti-coupling flags.
- The multilingual router probe is the cleanest current evidence for the wall-sign rule: `router_ok=10/10` and full router -> compiler JSON success `10/10` on raw Spanish, French, German, Portuguese, Italian, Japanese, and code-switched turns.
- The router agility harness now emits `anti_coupling_diagnostics_v1` after the compiler/mapper pass. It flags low-confidence admissions, strict profile misses with admissions, semantic near misses with admissions, profile/predicate mismatches, out-of-palette skips, and cases where admitted predicates fit another profile better. Bootstrap fallback is treated as a valid context-engineering request rather than a profile miss.
- `semantic_router_v1` now emits a `context_audit` block explaining why the profile/context was selected, which context sources should be loaded, which secondary profiles were considered, and why they were not primary. Runtime and router harness traces copy this as `context_audit_v1` with loaded context/contract/predicate counts.
- The router harness now also emits `router_diagnostics_v1`, a structural router/compiler alignment layer that can flag cases such as "router chose medical, but the compiler emitted legal predicate surfaces" without inspecting raw language.
- Mapper admission diagnostics now include human-readable `admission_justifications` derived from deterministic gates and rationale codes. Each operation can explain accepted-because and blocked-because reasons such as allowed palette, predicate contract pass, direct source, source-policy block, or missing durable rule clause.
- A first labeled router training seed lives at `docs/data/router_training/router_training_seed_v1.jsonl` with 164 examples assembled from frontier packs, multilingual probes, and mixed-domain agility cases.
- `semantic_ir_lava_pack_v5` is the current mixed-domain lava frontier. It targets truth-maintenance dependency pressure, predicate canonicalization drift, claim/fact/observation promotion, segmentation semantics, multilingual ontology pressure, rule sufficiency, source fidelity, and bootstrap behavior.
- `scripts/run_semantic_ir_lava_sweep.py --fast` is now the interactive frontier smoke. It runs a balanced 15-case clean slice with one repeat so routine checks do not waste GPU time on multi-variant sweeps unless the research question really needs them.
- A new research note, `docs/DOMAIN_BOOTSTRAPPING_META_MODE.md`, captures the meta-profile idea: when no domain profile exists, a strong model may propose candidate entity types, predicates, contracts, risks, clarification policies, and starter frontier cases. This is review material for creating a profile, not authority for durable writes.
- A first `profile_bootstrap_v1` harness now exists at `scripts/run_profile_bootstrap.py` with a contracts/compliance seed fixture. It asks the local structured-output model to propose a candidate domain profile, then scores schema validity, generic predicate use, and whether starter frontier cases stay inside the proposed predicate palette and arities.
- `scripts/run_profile_bootstrap_loop.py` now closes the meta-profile loop: it loads a local profile bootstrap run, projects its candidate predicates/contracts into a temporary Semantic IR profile, runs the generated starter cases through the normal model+mapper path, and scores valid JSON, palette skips, must-not violations, and expected-boundary hits.
- `scripts/run_domain_bootstrap_file.py` now captures the Codex-style open-domain move as an explicit LLM-owned profile-bootstrap path: Python reads a raw text file, the model proposes the predicate/entity surface, and optional source compilation uses that draft profile without Python deriving predicates or segmenting the language.
- Raw-file bootstrapping now has a first-class `intake_plan_v1` control-plane pass. The model proposes the source boundary, epistemic stance, symbolic/entity/predicate-family strategy, focused pass plan, and risk policy before profile/bootstrap compilation. This is the explicit version of the document-to-logic strategy Codex was doing implicitly.
- The raw-file runner can now compile by LLM-authored intake passes via `--compile-plan-passes`. Python iterates over the model's pass plan and carries context; it does not choose semantic segments from the source text. The intake planner is now explicitly told to split long repeated-record material into focused passes for ledgers/source records, reporters/witnesses, measurements, identity ambiguity, rules/conditions, remedies, and pledges instead of one operation-budget-constrained gulp.
- `profile_bootstrap_v1` now has a first-class `repeated_structures` block. This captures the document-to-logic compiler move where the model sees a repeated list, such as Declaration-style grievances, and proposes a stable record predicate plus property predicates like `grievance/2`, `grievance_actor/2`, `grievance_target/2`, `grievance_method/2`, and `grievance_purpose/2`.
- Raw-file source compilation now has a generic operation-budget policy for long documents: preserve source/provenance boundary, core speech acts, representative repeated records, and concluding commitments, while marking `segment_required_for_complete_ingestion` instead of letting one repeated list consume the entire Semantic IR operation cap.
- Raw-file profile bootstrapping now has a compact LLM retry when the structured profile JSON is invalid or truncated. The retry asks the model to emit a smaller unique predicate surface; Python does not repair or reinterpret the language.
- Declaration/Proclamation calibration exposed the next hard edge: predicate canonicalization drift. The model can understand a document and still offer competing equivalent predicate surfaces. Current guidance pushes the LLM to choose one canonical family; the intended repair remains profile/schema/context pressure, not Python synonym rewriting.
- Declaration/Proclamation now have narrow fixture-owned ontology registries for document-intake testing. These registries are vocabulary/context surfaces only, not facts and not write authority. The latest lesson matches Iron Harbor and Otters: a curated working profile can help, while a giant mixed predicate menu makes the compiler timid.
- Profile-owned predicate aliases now provide the first structural repair for predicate canonicalization drift: a profile contract can declare equivalent predicate signatures such as `dad_of/2` or `father_of/2` for canonical `parent/2`, and the mapper rewrites candidate operations only from that declared registry with traceable `profile_predicate_alias` authority. Python still does not inspect utterance prose to infer synonyms.
- The Semantic IR candidate-operation cap is now `128` per turn, raised from `64` after Declaration/Proclamation calibration showed the previous cap was crowding out dense document sections.
- A post-ingestion document QA runner now lives at `scripts/run_domain_bootstrap_qa.py`. It loads admitted facts/rules from a raw-file compile run, gives the QA model the actual compiled KB predicate inventory and representative clauses, maps question turns through Semantic IR, and executes admitted query clauses against the local Prolog runtime. The QA file can carry human reference answers without feeding them back into profile bootstrap or source compilation.
- Post-ingestion QA now carries a first-class `post_ingestion_qa_query_strategy_v1` context object. It teaches the model to query the compiled KB predicate surface, preserve full arity, use uppercase Prolog variables for unknown slots, avoid invented composite predicates, and keep source-claim/observation boundaries visible.
- Post-ingestion QA now has an exact-input per-question cache keyed by compiled KB artifact content, QA file content, question, reference answer, model/settings, prompt/runtime script hash, and judge/include flags. This avoids re-burning GPU on unchanged questions during frontier iteration, while `--no-cache` still gives a fresh validation or variance run.
- Query candidate arguments now get a structural placeholder-to-variable normalization pass for generic slot labels such as `action`, `label`, `candidate`, `grievancelabel`, `violationlabel`, `rulecontent`, `recordtype`, and `methoddetail`. This operates on model-emitted query arguments, not raw user prose, and prevents accidental constants like `grievance(Grievance, label)` from causing false no-result answers.
- Document-to-logic profile bootstrapping now explicitly asks for epistemic-status/provenance predicates on source-owned repeated records such as grievances, allegations, complaints, and accusations. A hint-free Proclamation recompile invented and used `grievance_status/2` with `source_bound_accusation`, proving the model can learn that missing structure through context pressure rather than Python NLP.
- The mapper now admits positive direct `operation='rule'` records with predicate+args but no executable clause as fact-like rule records, with rationale `rule_label_demoted_to_fact_record`. This is a structural repair for model administrative labels; true executable rules still require a clause, and negative/general rule operations still do not become facts.
- The mapper now blocks variable-like no-clause rule stubs from being demoted into facts. This closes a concrete policy-demo failure where `operation='rule'` plus `args=['R', ...]` could otherwise become a bogus durable atom such as `violation(r, reimbursement_policy).`
- A focused cross-turn policy/reimbursement demo runner now lives at `scripts/run_policy_reimbursement_demo.py`. It records reimbursement rules, ingests February events, asks which reimbursements violated policy, applies an explicit approval correction, and verifies that derived `violation/2` answers are not written as durable facts.
- A mixed-domain agility harness now lives at `scripts/run_mixed_domain_agility.py`. It randomizes Goldilocks, Glitch, Ledger, Silverton, Harbor, CourtListener, SEC/contracts, and medical scenarios through `active_profile=auto` so router-owned profile switching can be tested as a stream rather than isolated lanes.
- Router prompt/context policy now makes recent context visible for anaphoric/follow-up utterances such as "it came back high", while keeping the final profile choice in `semantic_router_v1` rather than Python keyword logic.
- Declarative starter profile packages now exist for exploration: `modelfiles/profile.story_world.v0.json`, `modelfiles/profile.probate.v0.json`, and `modelfiles/profile.legal_courtlistener.v0.json`. They provide mock thick context and predicate contracts for future routing experiments without changing runtime admission authority.
- The probate profile now owns a few noisy selection aliases for the Silverton/London frontier, such as `Btrice`, `Londn`, `Londres`, `ONT`, and weekend/country shorthand. These are context-loading hints, not mapper admission rules.
- The legal/probate/SEC starter profiles now carry a broader profile-owned predicate surface for the current frontier packs: legal source documents, access logs, relative-date anchors, interval facts, probate guardianship/conditional-gift facts, and contract-like clearance/lock/stock state.
- The mapper now collapses duplicate admitted candidate operations. This catches schema-cap repetition floods without teaching Python any story-specific language.
- The rule/query frontier now has its own `rule_query_semantics` bakeoff group. It stresses mixed turns where English policy, direct facts, explicit questions, necessary conditions, recusal rules, and derived compliance answers must stay separated.
- Prompt policy now tells the model to preserve compound query targets such as "active access with expired sponsorship" as multiple query operations when the palette supports them, and to bind queries to named subjects rather than generic class nouns.
- Medical safety projection now rejects clinical dose/treatment advice queries even if the same utterance contains otherwise safe medical-memory facts. This keeps bounded medical memory separate from clinical recommendation.
- Predicate contract role validation now treats `authority_or_source` as intentionally broad, so authorities such as auditors can be admitted without being mistaken for source-document role violations.
- A first-pass CourtListener adapter shell now lives under `adapters/courtlistener/`. It includes a conservative token-based REST client, normalizer, legal predicate contracts, harness conversion, README, and an offline synthetic legal seed fixture for claim/finding, citation, role-scope, docket, and identity-boundary tests.
- First CourtListener live smoke generated ignored `breach of lease` and `summary judgment` harness slices and ran legal Semantic IR cases through LM Studio. All emitted valid JSON; the legal palette preserved claim/finding, citation-not-endorsement, docket-not-holding, role-scope, and ambiguous judge identity boundaries.
- `sec_contracts@v0` is now the third large starter domain. It targets SEC/EDGAR and contract-obligation intake: filing/exhibit provenance, party roles, obligations, rights, conditions, effective/termination triggers, and breach-event boundaries.
- A first-pass SEC EDGAR adapter shell now lives under `adapters/sec_edgar/`. It requires `SEC_USER_AGENT` for live calls, caches raw responses locally, emits harness cases, and includes an offline synthetic fixture for obligation-not-fact and condition-not-event tests.
- First SEC live smoke generated ignored Apple/Microsoft filing harness data and ran 11 Semantic IR cases through LM Studio. All emitted valid JSON; adding `filer_of/2` fixed an initial palette gap where filing metadata was being squeezed into `party_to_contract/3`.
- A new held-out cross-turn frontier proposal lives at `docs/data/frontier_packs/semantic_ir_cross_turn_frontier_pack_v1.json`. It targets identity drift, claim/observation separation, noisy multilingual corrections, mixed rule/query/fact turns, temporal corrections, and domain type ambiguity.
- A new `policy_demo` Semantic IR bakeoff group now targets the "talk your rules into existence" demo family: reimbursement-policy violations, meeting commitments, access sponsorship expiry, customer-support override ladders, story-world throne claims, and business dependency credibility.
- Prompt/context policy now explicitly separates pure answers from mixed write+query turns, prioritizes direct grounded facts before complex rule clauses under the operation cap, requires explicit query operations for explicit questions, and blocks necessary-condition-to-sufficient-rule inversions such as turning "no launch without QA" into `launch_allowed(...)`.
- Epistemic Worlds v1 now surfaces projection-blocked and supported-but-skipped writes as scoped diagnostic memory instead of global truth. The mapper can preserve the candidate as fixed wrapper clauses such as `world_operation/4`, `world_arg/4`, and `world_policy/3`; these are diagnostic scoped-memory clauses and do not enter the durable domain predicates.

## Local UMLS Assets

Kept locally and ignored:

- `tmp/licensed/umls/2025AB/NET/`
- `tmp/licensed/umls/2025AB/semantic_network_kb/`
- `tmp/licensed/umls/2025AB/prethinker_mvp/`

Removed from the workspace cleanup because they are large and reproducible from external source storage:

- full UMLS zip archives
- extracted full Metathesaurus `META/`
- transient run directories, coverage HTML, caches, and trace logs

## Semantic Network KB

The current builder creates a fuller KB than the original nine medical profile predicates. The local Semantic Network output includes:

- 127 semantic types
- 54 semantic relations
- 597 structural relation rows
- 6,217 inherited UI relation facts
- 6,217 inherited name relation facts

This is the next useful layer for type steering and explanation. It should support demos like "why did this medication normalize this way?" or "what semantic family does this lab-test concept belong to?" without turning the app into a broad medical diagnosis system.

## Near-Term Frontiers

Top priority:

- Extend the new temporal kernel from ordering relations into richer date/interval and correction semantics. The first slice now supports deterministic ordering queries over admitted temporal facts; the next slice should let extracted dates, intervals, corrections, and relative-time anchors support policy-demo questions without writing derived conclusions as durable facts.
- Build on the new `temporal_graph_v1` sub-IR inspired by TG-LLM: event nodes, separated start/end anchors, interval edges, ordering/gap/overlap facts, support refs, and graph-derived QA probes. The key adaptation is Prethinker's authority boundary: the LLM proposes temporal graph structure, deterministic admission decides durable facts, and Prolog/temporal context answers queries.

Supporting architecture:

- Grow deterministic stored-logic admission beyond the first guard: profile-declared functional predicates, temporal scope, negation policy, and richer contradiction probes are still open.
- Grow clause support records and the `truth_maintenance` proposal block into a real dependency layer: derived conclusions should eventually point to supporting facts, rules, source documents, and retractions without granting model-proposed consequences write authority.
- Generalize multi-pass semantic compilation: make backbone, support/source, temporal/status, and rule lenses first-class pass types; keep mapper admission per lens; keep deterministic union restricted to mapper-admitted clauses; measure QA lift per admitted clause, firing-rule count, high-fanout count, and runtime rule errors.
- Add a semantic determination audit for right-shaped/wrong-meaning candidates: over structured alternatives and profile contracts, search for alternate valid predicate/entity/status/argument-role mappings, then admit invariant rows and hold or clarify shortcut-sensitive rows. This belongs in profile verification/evaluation and mapper diagnostics, not Python prose interpretation.
- Decide when Epistemic Worlds should graduate from diagnostic payloads into optional durable scoped memory. The first slice preserves rejected/quarantined candidates without polluting global truth; the next step is explicit world-query UX and policy for which worlds are persisted.
- Push the remaining mapper frontier: durable rule admission for quantified exception language, better decision-label calibration for safe partial commits, and cleaner nested event predicate shapes.
- For rule ingestion, separate the problems now exposed by Glass Tide: source-rule record capture, body-fact acquisition, executable rule clause proposal, active predicate-palette selection, body-goal/body-fragment support verification, fanout diagnostics, threshold/helper substrate, and temporary runtime trial before durable rule promotion.
- Promote clarification eagerness into the frontier harness: log base/effective CE, CE phase, correct asks, overeager asks, undereager misses, safe partial commits, blocked rows, and resumed-turn success for both ingestion and query CE. The new CE trap fixture should establish the first dedicated ask/no-ask baseline.
- Keep profile contracts out of the generic mapper: profile packages should own domain type/grounding policy, while the mapper stays structural and auditable.
- Promote scenario-local predicate contracts into reusable profile/predicate manifests so fewer expectations live only inside individual frontier packs.

Router/context work:

- Treat richer domain context as a catalog/skill mechanism, not hardwired prompt drift. The current auto path is router-owned and measured; next steps are multi-profile turns, router confidence UX, and deciding when mixed-domain utterances should be segmented before Semantic IR.
- Treat `docs/data/router_training/router_training_seed_v1.jsonl` as a router contract surface, not a fine-tuning set. It is large enough to harden schema/prompt expectations, but still thin around bootstrap and legal/probate boundary tension.
- Expand router/profile-selection tests from clean synthetic switching into messy mixed-domain turns. Profile selection is advisory context loading, not admission authority.
- Harden `profile_bootstrap_v1`: feed unfamiliar-domain text through profile proposal, review, retry, starter-case generation, and closed-loop mapper evaluation. The success criterion remains reviewable profile-design material, not automatic profile authority.

Demo-critical evidence and UX:

- Push the policy-demo frontier into the UI/prompt book once the command-line harness stays stable: the highest-impact demo is still "record reimbursement policy, ingest February events, ask which reimbursements violated policy, and show why without writing derived violation facts."
- Expand trace views around admission contracts so reviewers can see not only the model decision, but also which exact boundary checks passed.
- Keep temporal graphs visible in traces as event/time-anchor/interval/edge tables so temporal structure can be reviewed without spelunking through raw JSON.

Polish:

- Make the prompt-book examples meatier: each demo should show an utterance, the expected clarification or commit behavior, and the reason it is safer than a plain chatbot answer.
- Wire more Semantic Network explanations into the UI, especially type ancestry and relation paths.

Regression hygiene:

- Keep measuring router/compiler/admission quality directly on Glitch, Ledger, medical ambiguity, temporal packs, and mixed-domain Lava packs. The old Python-selector comparison has served its purpose and is no longer a useful frontier metric.
- Use the truth-maintenance/admission delta as a regular frontier metric: the next good improvements should reduce fuzzy edges by improving model workspace quality, profile contracts, or predicate surfaces, not by adding English phrase patches.
- Keep a regular regression cadence around segmentation, predicate-palette admission, stored-logic conflicts, and rule/query mixed turns; the frontier is productive enough that small improvements can easily re-open older failure modes.
- Keep improving reset/session hygiene so first utterances after reset cannot inherit stale entity context.

Domain/data lanes:

- Expand the medical profile only when the new predicate earns its place through tests and a clear demo.
- Keep expanding the CourtListener lane with small live API slices and curated synthetic boundaries. Generated live data remains ignored under `datasets/courtlistener/generated/` unless a tiny fixture is intentionally curated.
- Run the SEC adapter against a small EDGAR submissions slice only after setting `SEC_USER_AGENT` and choosing a durable cache/review policy. Keep generated live data under ignored `datasets/sec_edgar/generated/`.
- Tighten narrative ingestion next around stable object identity, event observation predicates, and temporal/event ordering instead of adding story-specific Python phrase patches.
- Keep the Semantic IR harness model-agnostic, but use `qwen/qwen3.6-35b-a3b` as the default development model unless a specific comparison question needs another local model.
- Add and document a "no big local GPU" runtime path for people who clone the repo without an RTX-class card. The intended shape is an OpenAI-compatible hosted backend such as OpenRouter/OpenAI with strict structured-output support, per-model schema-smoke allowlisting, cost/latency notes, and the same mapper/Prolog authority boundary. Codex/sub-agents remain research helpers around the repo, not the per-utterance Semantic IR compiler.
- When comparing local LM Studio models, unload/eject the previous model before loading the next one. If multiple large models remain resident, VRAM pressure can push work toward CPU and make tokens/sec measurements meaningless.

## Verification Snapshot

**Current headline:** the lean full pytest suite is `603 passed, 2 subtests passed`. The current research center is semantic parallax: multi-pass semantic compilation, mapper-admitted safe-surface accumulation, rule-lens promotion trials, row-level activation, clarification eagerness under an explicit authority boundary, and stenographer-mode stream simulation.

Recent verified results:

- Historical post-move preflight on `C:\prethinker`: an earlier branch point had full pytest at `464 passed`. Sable Creek produced the first fresh-fixture promotion-ready rule under the stricter rule gates, then SC-005 exposed a probe role-policy issue where the rule preserved a more precise source anchor than the authored probe expected. Avalon AG-012 added a body-fact acquisition step for `required_condition/2`; aligned body facts plus a Rule 8 lens yielded `4` promotion-ready rules with `4/4` positive probes, `2/2` negative probes, and `0` semantic shortcut findings. CET-013 reran source-context CE after the rule-admission changes and held `40/40` correct with `0` unsafe candidates and `0` context-write violations. The newest harness addition is stenographer-mode stream accounting in `scripts/run_gateway_turnset.py`, covering pending state, queued clarification counts, delayed clarification commits, segment holds, and authored expectation checks.
- Dulse Ledger replay: DL-003 exposed a repeated broad-skeleton JSON failure that compile health correctly marked `poor`; DL-004 moved the broad skeleton to compact `source_pass_ops_v1`, producing `51` flat-skeleton rows and improving full QA from the original `27 exact / 7 partial / 6 miss` baseline to `27 exact / 11 partial / 2 miss`. DL-005 then used the non-oracle row-level selector over the baseline and compact-flat evidence modes to reach `32 exact / 6 partial / 2 miss`. This is a harness-level gain, not fixture-specific Python language handling.
- Oxalis Recall replay: the same compact flat-skeleton change transferred to a safety-adjacent regulatory fixture. OX-003 produced a healthy compile with `91` admitted operations, `4` skips, and full QA `27 exact / 8 partial / 5 miss`, up from the original OX-001 `16 exact / 9 partial / 15 miss`.
- Iron Harbor full 100-question source-document run: `86 exact / 14 partial / 0 miss`, `100/100` parsed OK, `100/100` query rows, `0` runtime load errors, and `0` write proposals during post-ingestion QA. The compiled KB used `179` admitted operations and `116` unique facts, preserving roles, facilities, policy requirements, witness statements, reported events, disclosures, correction filings, and statement details in the same source surface.
- Blackthorn hostile procedural-misconduct fixture admission: baseline first-20 QA was `2 exact / 1 partial / 17 miss`. BTC-016 fixed `source=context` proposals without weakening the mapper, and BTC-021 reached full-100 QA `75 exact / 4 partial / 21 miss`. BTC-022 reached `82 exact / 9 partial / 9 miss`; BTC-027 later reached `85 exact / 4 partial / 11 miss` under a different evidence-filter configuration. Treat these as lane-specific results, not a single monotonic scoreboard. Fixture details and run-by-run lessons live in the Blackthorn progress journal.
- Kestrel maritime-insurance fixture admission: cold source-profile baseline KCL-001 landed at `5 exact / 0 partial / 15 miss` on first-20 QA with only `20` admitted operations. General insurance profile/context work and LLM-owned profile review lifted the best non-registry source-aware run to KCL-007 at `14 exact / 2 partial / 4 miss` first-20 and `30 exact / 12 partial / 58 miss` full-100, with `0` write proposals. Starter-profile-assisted KCL-002 reached `14 exact / 3 partial / 3 miss` first-20 and `38 exact / 12 partial / 50 miss` full-100; KCL-009 expanded the generic maritime-insurance row classes and reached `17 exact / 1 partial / 2 miss` first-20 and `61 exact / 7 partial / 32 miss` full-100. KCL-013 added deterministic query-review and role-named evidence companions, moving the same compiled KB to `63 / 11 / 26`. KCL-014 strengthened generic insurance-detail compile coverage and reached `67 / 12 / 21`. KCL-015 deterministically unioned mapper-admitted facts from KCL-009 and KCL-014, reaching `20 exact / 0 partial / 0 miss` on first-20 and `72 / 10 / 18` full-100. KCL-016 added source-faithful temporal atom parsing (`october_15_2025_08_00_utc`, `2025_10_12t03_17_00z`) and reached the current high-water `73 / 11 / 16`, with `100/100` parsed, `99/100` query rows, `0` runtime load errors, and `0` write proposals. KCL-010 and KCL-011 remain negative lessons: a wider starter profile and prose row-class examples both reduced usefulness. These assisted/union runs are explicitly labeled profile-guided, not cold-discovery evidence; domain packs are legitimate product context, but gold KB/QA-derived prompt clues are not.
- Anaplan Polaris enterprise-guidance fixture admission: APR-000 promoted the tmp seed into `datasets/enterprise_guidance/anaplan_polaris_performance_rules/` with source, oracle KB, starter profile, 43 QA probes, failure buckets, and progress ledger. APR-001 profile-guided baseline reached `29 exact / 6 partial / 8 miss`, with `43/43` parsed QA workspaces, `43/43` query rows, `0` runtime load errors, and `0` write proposals. APR-016 is the current high-water: multi-support safe-surface accumulation reached `42 exact / 1 partial / 0 miss`, `43/43` parsed, `43/43` query rows, `0` runtime load errors, and `0` write proposals. The remaining partial is a rationale compile-surface gap around summary-method high-cell-count memory/blocking effects.
- Glass Tide Charter rule-ingestion fixture admission: early broad compiles preserved source-rule records but admitted `0` executable rules. Separate rule lenses then exposed the real rule frontier: fanout, dormancy, body support, helper misuse, and promotion readiness. Current promotion-ready slices cover role-joined repair authorization, tax threshold plus relief exception, salvage reward exception, temporal quarantine clearance, council budget-veto failure, and support-threshold condition. The retained doctrine is staged rule acquisition: body-fact lens, active palette, mapper admission, runtime trial, positive/negative probes, deterministic rule-surface union, and promotion filtering before durable activation.
- Clarification Eagerness Trap fixture admission: CET-000 promoted the tmp seed into `datasets/clarification_eagerness/clarification_eagerness_trap/` with `20` ingestion CE cases, `20` query CE cases, and `10` baseline QA probes. Expected behavior is balanced enough to expose both over-eagerness and under-eagerness: ingestion expects `10` ask/partial-ask and `10` no-ask outcomes; query expects `7` clarification outcomes and `13` no-ask outcomes. CET-006 established the first strict authority-aware baseline: `37/40` correct, `0` over-eager, `2` under-eager, `1` unsafe candidate, and `2` context-write violations. CET-010 reached `40/40`; CET-011/CET-012 exposed the importance of source-context availability; CET-013 held the source-context lane at `40/40` after the rule-admission changes, with `0` unsafe candidates, `0` context-write violations, `10/10` blocked-slot coverage, and safe partials at `11/13`. Lesson: CE gains come from structural authority-surface scoring for context support and blocked slots, not merely asking more or less.
- Declaration document-intake cross-apply: hint-free recheck reached `211` admitted rows with expected-signature recall `0.116`; a narrow direct fixture registry reached `161` admitted rows and `0.391`; hybrid registry selection reached `323` admitted rows and `0.464`. This is current evidence that document profiles should supply a curated working vocabulary while still letting the LLM select the active compile surface.
- Proclamation document-intake cross-apply: hint-free compile reached first-20 QA at `14 exact / 2 partial / 4 miss`; narrow direct registry improved signature precision but dropped to `12 / 1 / 7`; hybrid registry selection compiled `249` admitted rows with first-20 QA `13 / 2 / 4`. The lesson is that expected-signature recall is not enough; source-support coverage per question is the next scoring layer.
- Otters cross-apply recheck: Harbor-style backbone/detail guidance did not beat the current Otters high-water mark. The best recheck landed at `8 exact / 1 partial / 11 miss` with support-map score `4/20`; stronger taxonomy/ledger guidance produced useful rows but reduced event/speech/judgment coverage. The next Otters move is a ledger-to-compile contract with row-class floors, not more raw prose prompting.
- Proposition-spine smoke: strict LM Studio structured output accepted the v1-compatible schema extension. The model emitted `propositions[]` and linked all candidate operations by `proposition_id`; mapper diagnostics carried the proposition data while admitting truth through the existing operation gates.
- Historical cleanup milestone: unreachable JSON fixtures and parser-era family/social rewrite crutches were retired from the active test surface; the current full-suite count is reported in the headline above.
- Selector-only Lava smoke after cleanup: `15/15` cases traversed, `12/12` checked selectors, `0` fuzzy edge kinds, with all remaining `kb_scenarios/*.json` fixtures mined by the Lava loader.
- Full suite after router action-plan compile-pressure wiring: `338 passed`.
- Focused router/context tests after action-plan compile-pressure wiring: `67 passed` across `tests/test_semantic_router.py` and `tests/test_mcp_server.py`.
- Live action-plan compile-pressure smoke: a mixed reimbursement rule/query turn routed to `sec_contracts@v0`, projected `segment_before_compile` and `extract_query_operations` into `router_action_policy` compiler context, and the compiler returned `decision=mixed` with both a write candidate and a query candidate. The remaining edge is improving query predicate specificity under the selected profile.
- Router action-plan smoke: `3/3` router-only LM Studio calls parsed under the strict schema and produced useful action plans. Simple story/contract turns requested `compile_semantic_ir`; a medical correction requested `compile_semantic_ir`, `include_kb_context`, and `include_truth_maintenance_guidance`.
- Fast Lava smoke: `15/15` parsed JSON, `11/11` selector-checked, `5/15` records with scoped epistemic memory, and `{}` fuzzy edge kinds in about 3.5 minutes on the local 35B LM Studio path.
- Soup-to-nuts shakedown after the cleanup exposed the current practical testing boundary: broad `scenario-group=all` and multi-variant Lava runs are useful frontier/nightly jobs, but too slow for frequent interactive checks. Use `--fast` or focused source filters for daily research pulses.
- Temporal kernel slice: admitted `before/2` facts now support deterministic `after/2`, transitive `precedes/2`, and `follows/2` queries through Prolog rules while `temporal_graph_v1` stays proposal-only unless matching candidate operations pass admission.
- Temporal correction admission: unannounced replacement `event_on/2` anchors are blocked as stored-logic conflicts; explicit retract/assert temporal corrections succeed and remove the stale anchor.
- Policy/reimbursement cross-turn demo: `4/4` parsed OK, `4/4` apply-error-free, `4/4` expected query matches, `4/4` no derived violation write leak, rough score `1.000`. The path installs executable rules from English policy, ingests February events, answers with derived violations, then retracts an approval and changes the answer without writing derived `violation/2` facts.
- Lava v5 source-record alignment rerun: `60/60` parsed JSON, `60/60` domain selector, `60/60` admission-safe, `45/60` semantic-clean, `41/60` full expectation score, `0/60` temp-0 signature variance groups, and `{}` fuzzy edge kinds. Remaining misses are mainly missing semantic anchors, temporal label calibration, and exception-rule representation rather than unsafe durable writes.
- Multilingual router probe: `router_ok=10/10`, `compiler_parsed_ok=10/10` on raw Spanish, French, German, Portuguese, Italian, Japanese, and code-switched turns. This remains the cleanest evidence for the no-Python-language-handling direction.
- Rule/query semantics focused bakeoff: `9/9` JSON/schema, `9/9` raw model decisions, `9/9` mapper-projected decisions, `9/9` admission contracts, `75/75` admission checks, average rough score `0.96`.
- Harbor frontier focused pass: `14/14` JSON/schema, raw model labels `12/14`, mapper-projected decisions `12/14`, admission contracts `13/14`, admission checks `51/52`, average rough score `0.95`. The useful remaining frontier is temporal correction: asserting the new relative-date anchor while also retracting the old anchor reliably.
- Truth-maintenance smoke: correction-plus-claim, rule-consequence-as-query, and observed-document-vs-witness-claim turns emitted support links, conflicts, retraction plans, and `query_only`/`do_not_commit` consequences while the mapper admitted only candidate-operation effects.
- KB-context smoke: with `lives_in(mara, london).` in the KB, `Actually, she lives in Paris now.` resolved the pronoun through the KB context pack, produced retract/assert operations, and yielded `0` truth-maintenance fuzzy edges.
- Profile bootstrap closed-loop smoke on the contracts/compliance draft: `8/8` valid Semantic IR, `8/8` zero out-of-palette skip cases, `8/8` zero must-not violation cases, `7/8` expected-boundary hit cases, `16` admitted clauses, loop rough score `0.969`.
- Raw Declaration document calibration: flat source compile emitted-signature recall `0.159`; LLM-authored intake-plan pass compilation raised that to `0.623` with `234` admitted operations. This is current evidence that document-to-logic planning belongs inside Prethinker as an LLM control-plane pass.
- Raw Proclamation profile-review experiment without target-signature handholding: useful early run produced `30` candidate predicates, `93` admitted source-compile operations, `4/4` successful planned passes, and first-20 post-ingestion QA at `10 exact / 5 partial / 4 miss / 1 not judged`. After source-record/reporter/condition pressure, a product-like compile produced a stronger style-aligned profile shape (`18` predicates, `4` repeated structures, `497` admitted operations, profile rough score `1.000`); structural query-placeholder normalization and QA strategy pressure raised its first-20 QA pass to `19 exact / 1 miss`, with the remaining miss exposing the need for explicit grievance epistemic status. A subsequent hint-free status-aware recompile invented `grievance_status/2` and emitted `source_bound_accusation`; after placeholder normalization its first-20 QA pass reached `18 exact / 2 miss`. This is the current live tradeoff: better epistemic structure can still shift predicate surfaces enough to stress compiled-KB query planning.
- Goldilocks full-story segmented Semantic IR smoke after narrative palette: `56` deduped mutations across `50` segments in about `180s`, with the major bad-write artifacts from the first UI attempt removed.
- A curated Otters/Clockwork Pie story-world fixture now lives at `datasets/story_worlds/otters_clockwork_pie/`. It packages a source-local whimsical story, reference Prolog KB, strategy notes, and 100 QA probes to pressure source fidelity, famous-template contamination, chronology, subjective judgment, speech-vs-truth, and final-state updates.
- CourtListener and SEC/contracts adapters have offline synthetic fixtures plus live-smoke paths. Current legal/SEC evidence is useful for claim/finding, citation-not-endorsement, role-scope, docket-not-holding, obligation-not-fact, condition-not-event, and filing/exhibit provenance boundaries, but generated live data remains ignored unless curated.
- Current model note: local model-family testing showed model choice matters even with structured output. `qwen/qwen3.6-35b-a3b` remains the default development model; other models are comparison tools, not release gates.

Older milestone ladders and superseded calibration packs are intentionally left to Git history rather than repeated here.

## Reading Order

If you read 3 things:

1. `README.md`
2. `docs/CURRENT_RESEARCH_HEADLINE.md`
3. `docs/MULTI_PASS_SEMANTIC_COMPILER.md`

If you have an hour:

1. `PROJECT_STATE.md`
2. `docs/ACTIVE_RESEARCH_LANES.md`
3. `docs/CURRENT_HARNESS_INSTRUMENT.md`
4. `docs/PUBLIC_DOCS_GUIDE.md`
5. `docs/EXPLAINER.md`
6. `docs/FRONTIER_PROGRESS_REPORT.md`
7. `docs/CLARIFICATION_EAGERNESS_STRATEGY.md`

Deep dives:

1. `docs/PROJECT_HORIZON.md`
2. `docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md`
3. `docs/SEMANTIC_ROUTER_EXPERIMENT.md`
4. `docs/MULTILINGUAL_SEMANTIC_IR_PROBE.md`
5. `docs/NO_LANGUAGE_HANDLING_IN_PYTHON_AUDIT.md`
6. `docs/DOMAIN_PROFILE_CATALOG.md`
7. `docs/COURTLISTENER_DOMAIN.md`
8. `docs/SEC_CONTRACTS_DOMAIN.md`
9. `docs/UMLS_MVP.md`
10. `docs/MEDICAL_PROFILE.md`
11. `docs/CONSOLE_TRYBOOK.md`
12. `docs/PUBLIC_DOCS_GUIDE.md`
13. `ui_gateway/README.md`

## What Was Pruned

Historical markdown reports, dated prompt snapshots, generated ladder/report HTML, stale run manifests, old parser-lane orchestration notes, old direct parser-probe scripts, the old ladder-era JSON fixture set, generated `kb_runs/`, generated `kb_store/`, and large session/source notes were removed from the forward-facing tree. Git history still carries them. The repo should now privilege source, compact current-state docs, small fixtures, and tests over a stack of stale status artifacts.

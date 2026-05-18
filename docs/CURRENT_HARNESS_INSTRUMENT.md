# Current Harness Instrument

Last updated: 2026-05-17

Prethinker compiles documents into governed, queryable KB artifacts and audits
whether questions can be answered from admitted state alone, without rereading
source prose. This document describes the harness as a research instrument: how
it measures compile quality, row delivery, selector behavior, guard pressure,
and semantic progress. Its purpose is to keep the project hard to fool while
making every architectural move replayable.

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

## Current Artifact Unit

The live no-helper artifact under evaluation is:

```text
source + lens set + deterministic ledgers + admitted predicates + query policy
```

The default query policy is no-helper:

```text
--helper-companion-row-limit 0
```

Legacy helper adapters are compatibility and forensic tools only. They remain
opt-in for replaying older artifacts and understanding how past high-water
surfaces were reached, but they are not the current architecture. The current
repair path is direct compile-surface stability: when a recurring query-time
join matters, make the compiler or deterministic ledger emit a reusable,
fixture-free surface directly.

Helper-era evidence and retirement history were retired from the public docs
tree. Git history preserves the old worksheet for cases where a historical
result mentions `candidate-helper`, `clean-helper`, or legacy companion rows.
New contexts should treat that material as migration history, not as the active
harness center.

## Current Paths

### Clean Surface And Live Surface

The daily-driver surface is `src/kb_pipeline_clean` plus
`scripts/run_kb_pipeline_clean_harness.py`. The live behavior source remains
`src/mcp_server.py` until each compiler, gate, apply, or normalization piece has
been wrapped, replayed, extracted, compared, and only then retired from the
legacy surface.

In practice, `src/kb_pipeline_clean` is the intended interface for new agents
and repeatable harness work. `src/mcp_server.py` is still the behavior reservoir
for pieces that have not completed the migration loop:

```text
wrap -> replay -> extract -> compare -> retire
```

That two-surface state is deliberate. New work should prefer the clean surface,
but old behavior should only disappear after replay evidence shows parity or a
better replacement.

Document work follows this shape:

```text
source
  -> deterministic source-address ledgers
  -> intake/profile/bootstrap passes
  -> semantic compile candidates
  -> mapper-admitted KB artifact
  -> no-helper QA over direct compile surfaces, ledgers, selectors, and guards
```

POWER, the local workstation with an RTX 5090, and OpenRouter, the cloud lane,
are both measurement lanes. Model/provider variation is treated as data:
durable surfaces should transfer; sensitive surfaces such as exact string
preservation get deterministic reinforcement.

## Instrument Principles

- The harness measures structural behavior; it does not reward "better" model
  answers during refactors.
- Prefer artifact-first orchestration: compile once, persist the source/KB/IR
  and run metadata, then run many cheaper semantic parallax passes against
  frozen artifacts.
- Treat the compile product as a durable KB artifact package. Ordinary Q&A
  should answer from admitted world state, admitted epistemic/provenance state,
  deterministic source ledgers, direct query surfaces, and manifest metadata,
  not by rereading source prose.
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
  and struggle detection. See `docs/SEMANTIC_INSTRUMENT.md` and
  `docs/SEMANTIC_LENS_ROSTER.md`.
- Legacy symbol names may remain as migration references until the clean
  surface proves parity.
- Dead-code removal waits until the instrument can show that code is genuinely
  unreachable rather than dormant migration scaffolding.
- The harness should detect semantic struggle. If repeated passes add no unique
  admitted surface, duplicate most of their output, go skip-heavy, or fail
  activation-governor targets, the instrument should recommend stopping or
  continuing only with a named expected contribution.
- Guard growth is itself telemetry. A new guard should name a reusable
  question/evidence mismatch; if it only names a fixture, it is probably
  overfitting. Merge duplicate guards only after replay proof, and retire guards
  when better direct compile surfaces or deterministic ledgers make them
  unnecessary.

## Source Ledgers

The harness distinguishes semantic lenses from deterministic pre-compile
ledgers. Lenses ask the model to propose meaning under governance. Ledgers pin
literal source addressability before the model reads: identifiers, headings,
line numbers, table rows, table cells, numeric tokens, and labeled official
prose.

Ledgers do not infer source truth. They make the source's printed structure
queryable so a later compile or QA pass can recover the exact row, date, count,
source label, record cell, or printed identifier without relying on model
recall.

Recent no-helper work made this boundary explicit:

- `explicit_table_membership/4`, `explicit_table_member_label/5`, and
  `explicit_table_member_alias/2` replaced school-shaped roster table names as
  the primary explicit grouping/member table surface.
- Source-coordinate profile work moved old packet-style source lookup pressure
  toward direct ledger facts and query planning rather than restoring helper
  rows.
- Source/role review pressure treats old names such as
  `industrial_sensor_clock_correction` as fixture-risk audit coordinates, not
  public architecture.
- Source-surface gap audits now distinguish answer strings that are stranded in
  deterministic `source_record_*` rows from values that have earned direct
  admitted predicates. `source_detail/4` is available only as an additive
  fallback carrier when a stricter profile attribute/detail predicate is absent;
  it must not replace concrete identity, event, status, temporal, count, amount,
  rule, role, or authority rows.
- Compile-surface stability now tracks candidate predicate palette stability,
  not just admitted fact stability. A compile draw can preserve enough meaning
  to answer some questions while still alternating between incompatible
  predicate names or arities for the same source. Those palette shifts are
  measured as first-class churn before any repair is designed.
- Literal `Key: Value` source lines now emit deterministic
  `source_record_inline_field/3` plus the shared `source_record_field/3`
  surface used for tables. This is source addressability, not semantic
  interpretation: it preserves printed keys and values so no-helper query
  planning can retrieve them when the question names the same key.

## Selector And Guard Discipline

The selector chooses the best encounter surface per row. A guard prevents a
tempting wrong surface from winning.

Every guard should answer:

```text
What question/evidence mismatch does this prevent?
Can it transfer across fixtures?
Can a better compile surface or deterministic ledger retire it?
```

The healthy long-term motion is not infinite guard growth. It is direct
compile-surface and ledger improvements retiring downstream selector scars.

## Current Evidence Pattern

Recent transfer work supports the current direction:

- The 2026-05-17 native MoE no-helper stamp compiled all 56 native fixtures
  and answered 2163 judged rows with helper companion delivery disabled:
  1880 exact, 83 partial, 196 miss, for an exact rate of 86.92%. Runtime load
  errors and write proposals were both zero, and helper rows were exactly zero.
- External corpora and unlike probes routinely run with 0-3 helper rows because
  the modern path relies on admitted predicates and source ledgers instead of
  native compatibility adapters.
- The native corpus still carries many historical shapes, which makes it the
  best place to find legacy residue and compile-surface gaps. That is not a
  reason to restore helpers; it is the reason to convert reachable distinctions
  into direct admitted predicates, deterministic ledgers, or query policy.
- Predicate inventory is now tracked directly so fixture-shaped names can be
  audited by frequency, scope, and layer rather than discovered by surprise in
  archived notebooks.
- Compile-surface invariant audits now include a quality contract for generic
  detail/event wrappers: wrappers may remain as additive residue, but they are
  flagged when event identity, time, participant/system, subject, and outcome
  backbone rows are missing.
- Compile-surface stability audits now report candidate-palette churn and
  predicate arity drift across redraws, plus signature-level row delivery drift
  and zero-yield candidate signatures. Recent roster redraws showed high
  palette churn even when QA stayed in the same rough band, and palette-prior
  replay showed the sharper failure mode: a compile can preserve many labels
  while losing the delivered rows that made those labels queryable.
- Palette registries can now be built from compile artifacts as vocabulary-only
  scaffolds. Early roster replay showed that a palette prior can reduce churn,
  but overly strict name/arity preservation can still lose answer-bearing slots.
  The next repair layer must preserve the structural slots that make the
  surface queryable, not merely freeze predicate labels.
- Palette delivery contracts are the current stabilization target. The contract
  asks whether a retained repeated signature actually delivers rows across
  redraws, classifying each draw as `healthy`, `zero_yield`, `arity_drift`, or
  `delivery_collapse`. Delivery-contract guidance improved the roster replay
  from 29/2/9 under strict palette prior to 33/1/6 with helpers still disabled,
  while reducing palette churn and arity drift.
- Transfer validation is mixed and therefore still active. On
  `sable_creek_budget`, delivery-guided replay preserved the accepted no-helper
  QA score at 36/1/3 and removed arity drift, but still swapped many
  row-bearing signatures. On `dulse_ledger`, the same pattern regressed from
  34/5/1 to 32/5/3 with helpers still disabled, mainly around ledger/detail
  enumeration, restitution, and rule-consequence joins. The next repair should
  protect structural slot delivery and detail-bearing ledger surfaces; it
  should not freeze fixture predicate names or restore legacy helper rows.
- A small model-variance spot check on `dulse_ledger` did not make the issue
  disappear. Qwen 3.6 27B compiled to 29/5/4 with parse loss and higher palette
  drift; DeepSeek V4 Pro compiled to 33/5/2 with helpers still disabled but
  continued delivery drift. Treat model/provider choice as variance evidence,
  not as a substitute for the missing structural delivery contract.
- The invariant audit now includes `repeated_record_detail_delivery_contract`.
  It looks for repeated source-owned record anchors whose source text carries
  transfer/action/status language, then checks whether admitted rows preserve
  record identity, participant/actor, item/value, and status/consequence slots
  as joinable surfaces. This is an audit gate only; an attempted prompt repair
  was rejected because it over-compressed Dulse rather than improving QA. On
  the 56-fixture native draw-1 preflight, the contract surfaced three weak
  cases: `avalon_grant_committee`, `dulse_ledger`, and
  `rotating_chair_authority`.
- The stamp's remaining gap is still mostly compile-surface addressability:
  170 compile-surface gaps, 59 hybrid-join gaps, 44 query-surface gaps, 8
  judge-uncertain rows, and 2 answer-surface gaps. That keeps the next repair
  pressure on direct admitted surfaces and deterministic ledgers, not on
  restoring helper compatibility rows.
- The first post-stamp repair targeted evidence-bundle query execution, not
  fixture content. The source-surface diagnostic found that 84 of the 170
  compile-surface gaps had strong answer evidence in deterministic
  `source_record_*` rows, including 67 where the answer was stranded there and
  absent from direct admitted rows. Evidence-bundle plans were sometimes
  proposing Prolog-like equality constraints such as `Label = some_source_row`
  inside otherwise valid source-record joins. The harness now folds simple
  variable-to-constant equality constraints into predicate arguments before
  validating and executing the bundle, while rejecting alias-only equality that
  would become a broad source scan. A no-helper smoke over two affected native
  fixtures showed the bounded effect: one source-row reason miss became exact,
  while unrelated rows remained outside the repair.
- Quantity questions now participate in the same deterministic source-text hint
  path. Previously, `How many...` rows could skip question-token source scans
  entirely, leaving prose counts stranded even when the source row was present.
  The query path now treats quantity prompts as source-text probes and allows a
  slightly wider question-token hint set. This remains query routing only: it
  uses question tokens and deterministic `source_record_text_atom/2` rows, does
  not inspect reference answers, and does not create helper rows. A no-helper
  smoke over a quantity miss confirmed the source row became visible and the
  row judged exact.
- A six-fixture no-helper replay over source-stranded native rows measured the
  combined source-query repairs as a bounded gain, not a blanket fix: exact
  rows moved by +10 net across 240 judged rows, with zero helper rows and zero
  runtime errors. The lift concentrated in fixtures where source rows already
  carried the missing detail but prior query routing failed to expose them.
  One fixture regressed by two exact rows, so these changes remain query-route
  evidence rather than a new stamped baseline.
- Evidence-bundle source-text filters are now repaired as bounded execution
  filters when they start from `source_record_text_atom/2`. The harness accepts
  LLM-authored forms such as `memberchk(...)`, `string_contains(...)`,
  `text_contains(...)`, and simple `Text contains ...` only after a source-text
  surface has already bound the row and text variables, then requires all
  normalized needles to appear in the deterministic source text. This converts
  common rejected query templates into row filters without adding facts,
  helper rows, or fixture vocabulary. Local replay over existing stamp/replay
  artifacts found 112 newly executable templates, 95 with hits, including 65
  that had previously been rejected. A targeted four-fixture OpenRouter smoke
  stayed helper-free and moved two fixtures up by +5 exact combined, while two
  fixtures showed no net score movement and normal stochastic row flips; treat
  this as routing validation, not a stamped baseline.
- The same bounded filter pattern now covers source-record labels, sections,
  text keys, and fields when the query first binds one deterministic
  `source_record_*` surface and then filters a returned variable. Local replay
  found this is a smaller hygiene layer than source text: 27 newly executable
  templates, 13 with hits, and 2 on non-exact rows. It is useful for avoiding
  rejected ledger-column filters, but it is not expected to move the native
  score materially by itself.
- A final query-layer cleanup before restamp added deterministic post-filter
  execution for single admitted predicates followed by simple list-membership
  or concat-as-contains filters. This catches evidence plans such as "query the
  admitted role/claim rows, then keep rows whose returned value belongs to this
  list or contains this atom" without inventing new predicates. Local replay
  found 101 newly executable templates, 58 with hits, including 14 hits on
  previously non-exact rows. A targeted three-fixture OpenRouter smoke moved
  +5 exact over 120 rows with helpers still at zero. This is the cutoff for
  query-layer cleanup before a QA-only native no-helper restamp; the remaining
  stranded-only compile-surface gaps need direct compile-surface work rather
  than more runtime normalizers.
- The QA-only native no-helper restamp on the same 56 compiled fixtures
  measured the cumulative query-layer movement without introducing compile
  variance: 1934 exact, 64 partial, 162 miss over 2163 rows, for 89.41% exact.
  This is +54 exact and +2.49 percentage points over the 86.92% native MoE
  no-helper stamp. Runtime load errors and write proposals remained zero, and
  helper rows remained exactly zero. Failure surfaces moved from 170 to 148
  compile-surface gaps, 59 to 57 hybrid-join gaps, 44 to 17 query-surface
  gaps, and 8 to 3 judge-uncertain rows. The source-surface audit of the 148
  remaining compile gaps still found 58 `answer_stranded_in_source_record`
  rows, down from 67, so the next high-value layer is direct compile-surface
  emission for source-record-only distinctions rather than more query-filter
  normalization.
- The operating protocol now distinguishes measurement layers: pure
  query/runtime changes should use a QA-only restamp on fixed compile artifacts;
  compile-guidance changes should start with small replay compiles and quality
  gates before any full compile+QA stamp. A first four-fixture source-record
  promotion probe was diagnostic rather than a compile-layer win: all four
  replay compiles parsed, but all four quality gates held because detail
  wrappers or lifecycle fragments still failed to preserve enough direct
  backbone slots. That result confirms the remaining work is real
  compile-surface preservation, not another QA normalizer.

The main weak surface is no longer "can the model understand the document?" It
is often "did the admitted state become addressable, composable, and queryable
at the exact row shape the question demands?"

## Current Commands

```powershell
python scripts/run_kb_pipeline_clean_harness.py --instrument-md
python scripts/run_kb_pipeline_clean_harness.py --instrument-manifest
python scripts/run_kb_pipeline_clean_harness.py --audit-normalizers
python scripts/run_kb_pipeline_clean_harness.py --trace-plan
python scripts/validate_fixture_intake.py --root datasets/incoming_fixtures --out-json tmp/incoming_fixtures/intake_validation.json
python scripts/stage_incoming_fixtures.py --root tmp/incoming --out-root tmp/incoming_staged
python scripts/plan_story_world_fixture_runs.py --fixture copperfall_deadline_docket --fixture harrowgate_witness_file --fixture larkspur_clockwork_fair --fixture meridian_permit_board --fixture northbridge_authority_packet --qa-limit 40 --out-json tmp/story_world_runs/promoted_incoming_cold_run_plan.json --out-md tmp/story_world_runs/promoted_incoming_cold_run_plan.md
python scripts/select_qa_mode_without_oracle.py --selection-policy guarded_activation --group <name>:baseline=<QA_JSON>+<FAILURE_SURFACE_QA_JSON>,candidate=<QA_JSON> --out-json <OUT_JSON> --out-md <OUT_MD>
python scripts/plan_selector_risk_gate.py --baseline-run protected=<SELECTOR_JSON> --candidate-run guarded_activation=<SELECTOR_JSON> --transfer-comparison <SELECTOR_POLICY_COMPARISON_JSON> --out-dir tmp/selector_risk_gates
python scripts/audit_compile_surface_stability.py --compile-json <COMPILE_JSON_OR_DIR> --compile-json <COMPILE_JSON_OR_DIR> --out-json tmp/compile_surface_stability.json --out-md tmp/compile_surface_stability.md
python scripts/build_profile_palette_registry.py --compile-json <COMPILE_JSON_OR_DIR> --mode first --out-json tmp/profile_palette_registry.json --out-md tmp/profile_palette_registry.md
```

Generated run JSON can stay under `tmp/`. Durable scorecard lessons and
artifact references should be captured in tracked fixture journals or compact
current docs.

`C:\prethinker_tmp_archive` is cold storage for bulky tmp evidence worth keeping
but not worth carrying in the active tree or model context. Search it narrowly
when a named prior artifact matters. Do not treat it as live guidance; if an
archived run becomes an active lesson, summarize that lesson in tracked docs or
the fixture's journal.

## Struggle Detection

`src/semantic_struggle.py` owns the structural circuit breaker. It reads only
harness telemetry such as per-pass unique contribution counts, duplicate
counts, health flags, and selector-governor compliance counts. It does not read
source prose or infer answers.

The current output is `semantic_progress_assessment_v1`:

- `zombie_risk`: `low`, `medium`, or `high`
- `recommended_action`: `continue`,
  `continue_only_with_named_expected_contribution`, or
  `stop_and_report_struggle`
- `semantic_progress_delta`: unique contribution total, duplicate total,
  duplicate ratio, recent unique contribution count, and stale tail count
- `stop_reasons` and `caution_reasons`

This is the product behavior: Prethinker should be smart enough to notice when
it is no longer making semantic progress.

# Current Harness Instrument

Last updated: 2026-05-17

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

The daily-driver surface is `src/kb_pipeline_clean` plus
`scripts/run_kb_pipeline_clean_harness.py`. The live behavior source remains
`src/mcp_server.py` until each compiler, gate, apply, or normalization piece has
been wrapped, replayed, extracted, compared, and only then retired from the
legacy surface.

Document work follows this shape:

```text
source
  -> deterministic source-address ledgers
  -> intake/profile/bootstrap passes
  -> semantic compile candidates
  -> mapper-admitted KB artifact
  -> no-helper QA over direct compile surfaces, ledgers, selectors, and guards
```

OpenRouter and POWER are both measurement lanes. Model/provider variation is
treated as data: durable surfaces should transfer; sensitive surfaces such as
exact string preservation get deterministic reinforcement.

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

- Native no-helper draw-1 scanned 56 compile artifacts with zero helper delivery
  in the active QA path.
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
  predicate arity drift across redraws. Recent roster redraws showed high
  palette churn even when QA stayed in the same rough band, which points toward
  profile/palette stabilization before broad native no-helper stamping.
- Palette registries can now be built from compile artifacts as vocabulary-only
  scaffolds. Early roster replay showed that a palette prior can reduce churn,
  but overly strict name/arity preservation can still lose answer-bearing slots.
  The next repair layer must preserve the structural slots that make the
  surface queryable, not merely freeze predicate labels.

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

## Extraction Rule

```text
wrap -> replay -> extract -> compare -> retire
```

That order keeps the moving platform usable while the workbench becomes easier
for a human to understand.

# Current Harness Instrument

Last updated: 2026-05-18

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
- Source/role review pressure treats fixture-flavored predicate names surfaced
  during native inventory work as audit coordinates, not public architecture.
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
- Compile delivery telemetry now distinguishes "profile or wrapper evidence
  exists" from "the direct answer-bearing carrier was actually emitted." The
  first N=3 compile-only diagnostic found the quantity-rich event target
  unstable while a narrative control stayed quiet after source-line locators
  were excluded from quantity detection. This is a diagnostic signal, not a
  repair permission.
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

## Current Empirical State

The current native no-helper capstone is the 2026-05-17 QA-only restamp over
the same 56 compiled native fixtures. It measured cumulative query-layer work
without introducing compile variance:

- 2163 judged rows: 1934 exact, 64 partial, 162 miss
- 89.41% exact, up from the prior 86.92% native no-helper stamp
- +54 exact rows and +2.49 percentage points over the previous no-helper
  baseline
- zero helper rows, zero runtime load errors, and zero write proposals

The remaining gaps are no longer primarily helper or query-filter failures.
After the query-layer restamp, compile-surface gaps fell to 148 and
query-surface gaps fell to 17. A source-surface audit still found 58 rows where
answer-bearing values are stranded in deterministic `source_record_*` rows.
That makes direct compile-surface emission for source-record-only distinctions
the next high-value layer.

## Operating Protocol

Measurement now follows the layer being changed:

- Pure query/runtime changes use QA-only restamps on fixed compile artifacts.
- Compile, profile, palette, or invariant changes start with small replay
  compiles and quality gates before any full compile+QA stamp.
- Full corpus stamps are reserved for frozen instrument states, not for every
  local repair.

This separation matters because a full recompile would mix query-layer progress
with compile stochasticity. The 89.41% result is meaningful precisely because
it used fixed compile artifacts.

## Delivery Contracts

Palette delivery contracts are the current stabilization vocabulary. They ask
whether a retained repeated signature actually delivers rows across redraws,
not merely whether the same predicate label appears. Each draw is classified as
one of four states:

- `healthy`: the signature still delivers usable rows
- `zero_yield`: the signature exists but emits no rows
- `arity_drift`: the name survives but the slot shape changes
- `delivery_collapse`: the retained surface loses the rows that made it
  queryable

This vocabulary keeps palette stability honest. Freezing names is not enough;
the harness must preserve the structural slots that make those names answer
questions.

## Current Evidence Pattern

Recent transfer work supports the current direction:

- Helpers are retired from the daily path. External corpora and unlike probes
  routinely run with 0-3 helper rows because the modern path relies on admitted
  predicates, deterministic source ledgers, selectors, and guards rather than
  native compatibility adapters.
- The native corpus is still valuable because it contains historical pressure:
  legacy residue, fixture-flavored predicates, and compile-surface gaps. Those
  are audit coordinates, not permission to restore helpers or freeze fixture
  vocabulary into public architecture.
- Query-layer cleanup is bounded. Source-record text, labels, sections, fields,
  simple equality constraints, list membership, and contains-style filters are
  executed only after a deterministic or admitted surface has already bound the
  row. These repairs add no facts, no helper rows, and no fixture vocabulary.
- Compile-surface stability is now measured at the palette and delivery level:
  candidate-palette churn, predicate arity drift, zero-yield signatures, and
  row delivery collapse are first-class telemetry.
- Offered-but-not-delivered telemetry is being added one surface at a time.
  The current quantity-event detector only searches content slots, ignores
  source-line locators, and reports issues when numeric event/log details are
  trapped in generic wrappers without a direct quantity-bearing event carrier.
- Source-record ledgers preserve fidelity but are not semantic substitutes.
  When source rows carry answer-bearing identity, status, count, time, amount,
  role, authority, or rationale, the target state is a direct admitted predicate
  or stricter profile surface, not source text as the only carrier.
- Compile-quality gates now distinguish true compile loss from noisy audit
  alarms. Generic detail/event wrappers may remain as additive residue, but
  they are flagged when concrete backbone rows disappear. Calibration has
  already separated false lifecycle alarms from real quantity-backbone drift.
- Quantity-rich event preservation now has the same bounded shape as
  source-detail preservation: a deterministic vocabulary extension can add
  `event_measurement/4` only when profile admission sees repeated numeric
  event/log details and no direct quantity-bearing event carrier. This is
  vocabulary-only and extracts no facts. Focused replay proved the slot can
  carry setpoint and feed-rate values; four-fixture replay still found one
  stochastic sensor hold, so this is an architectural advance, not a stamp.
- Transfer validation is mixed and active. Model/provider variation is treated
  as variance evidence, not as a replacement for structural delivery contracts.
  The next compile-layer pressure is quantity-rich event/profile preservation
  and other source-record-only distinctions, not a native full stamp.

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

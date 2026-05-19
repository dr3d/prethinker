# Current Harness Instrument

Last updated: 2026-05-19

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

The live artifact under evaluation is:

```text
source + lens set + deterministic ledgers + admitted predicates + direct query policy
```

The current repair path is direct compile-surface stability: when a recurring
query-time join matters, make the compiler or deterministic ledger emit a
reusable, fixture-free surface directly. Retired compatibility adapters exist
only for historical replay and are not day-one architecture for new work.

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
  -> QA over direct compile surfaces, ledgers, selectors, and guards
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

Recent direct-surface work made this boundary explicit:

- `explicit_table_membership/4`, `explicit_table_member_label/5`, and
  `explicit_table_member_alias/2` replaced school-shaped roster table names as
  the primary explicit grouping/member table surface.
- Source-coordinate profile work moved old packet-style source lookup pressure
  toward direct ledger facts and query planning.
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
  interpretation: it preserves printed keys and values so direct query
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

The current native direct-surface capstone is the 2026-05-17 QA-only restamp over
the same 56 compiled native fixtures. It measured cumulative query-layer work
without introducing compile variance:

- 2163 judged rows: 1934 exact, 64 partial, 162 miss
- 89.41% exact, up from the prior 86.92% native direct-surface stamp
- +54 exact rows and +2.49 percentage points over the previous direct-surface
  baseline
- zero compatibility rows, zero runtime load errors, and zero write proposals

The remaining gaps are no longer primarily query-filter or compatibility
adapter failures.
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

- Current document QA relies on admitted predicates, deterministic source
  ledgers, selectors, and guards. Retired native compatibility adapters are
  not part of the daily path.
- The native corpus is still valuable because it contains historical pressure:
  legacy residue, fixture-flavored predicates, and compile-surface gaps. Those
  are audit coordinates, not permission to restore compatibility adapters or freeze fixture
  vocabulary into public architecture.
- Query-layer cleanup is bounded. Source-record text, labels, sections, fields,
  simple equality constraints, list membership, and contains-style filters are
  executed only after a deterministic or admitted surface has already bound the
  row. These repairs add no facts, no compatibility rows, and no fixture vocabulary.
- Current query routing can now expose source-attribution carriers, event
  description rows, and deterministic current-state source text when the
  question language asks for source-stated reasons, responsibility,
  availability, correction, or current values. On the amended-register replay,
  this moved the preserved compile artifact from `33/3/4` to `40/0/0` with
  zero compatibility rows, zero writes, and zero residual query fallback
  signals. This is query routing, not a license to leave recurring answer
  distinctions stranded in source text forever.
- Source-coordinate wording now treats `according to ...`, `per the ...`,
  source-within-packet, packet-id, ticket, and reported-by phrasing as explicit
  requests for deterministic source addressability. On the 17-row native
  source-reference stranded slice, query-only replay moved from `7/1/9` to
  `17/0/0` on the same frozen compile artifacts, with zero compatibility rows.
  The final row exposed a placeholder-vs-content distinction: `title` remains a
  protected slot placeholder in Prolog query arguments, but legal title phrases
  such as `transfer title` are preserved as source-text needles because there
  the word is source content.
- Compile-surface stability is now measured at the palette and delivery level:
  candidate-palette churn, predicate arity drift, zero-yield signatures, and
  row delivery collapse are first-class telemetry.
- Offered-but-not-delivered telemetry is being added one surface at a time.
  The current quantity-event detector only searches content slots, ignores
  source-line locators, and reports issues when numeric event/log details are
  trapped in generic wrappers without a direct quantity-bearing event carrier.
  Applied to the 56 compiled native stamp artifacts, the calibrated detector
  found 10 candidate quantity-rich wrapper queues. That is a repair queue, not
  a scorecard: each queue still needs replay or transfer evidence before it can
  become a compile invariant.
- Repeated-structure property predicates are now admitted into the profile
  palette when the profile names them under `repeated_structures` but omits
  them from `candidate_predicates`. This is a vocabulary contract repair, not
  fact extraction. On the focused recall/inventory replay it changed the
  compile from 32 admitted / 27 skipped rows to 128 admitted / 1 skipped row,
  dropped compile-surface QA gaps from 10 to 4, and moved the fixture from
  25/5/10 to 29/3/8 on direct-surface QA.
  Transfer replay was mixed: a fire/operations fixture improved slightly
  (28/3/9 to 29/3/8), while a variance/hearing fixture regressed under a fresh
  compile draw (28/1/11 to 23/4/13). Treat the repair as proven for hidden
  repeated-structure palettes, not as a universal compile-stability solution.
- The variance/hearing regression isolated a different layer: predicate
  palette instability. Three fresh compile-only draws produced only 2 common
  candidate signatures out of 40 union signatures, 38 unstable signatures, and
  371 unstable direct facts. A vocabulary-only multi-draw palette registry
  replay then recovered the fixture to 30/3/7 on direct-surface QA and
  compile-surface gaps down to 8. This is evidence for a control-plane
  response path: use multi-draw palette priors to stabilize ontology choice
  without supplying facts, answers, expected rows, or source authority. A
  follow-up replay with the calibrated quality gate remained at 30 exact,
  confirming that the source-authority extension did not over-trigger on this
  source; the remaining pressure is still compile-surface coverage.
- Source-authority preservation is now a bounded vocabulary/delivery contract.
  When source text explicitly says a rule, policy, order, or authority governs
  an action/status/scope, the profile can add `source_authority/3` as
  vocabulary only. Quality retry then asks the compile to deliver a direct
  source-authority row instead of leaving the distinction in rule prose or
  source-record text. On a procedural docket replay, a vocabulary-only palette
  prior plus source-authority retry cleared the quality hold, emitted direct
  authority rows, and moved direct-surface QA from 31/1/8 to 39/0/1.
  A four-fixture authority transfer slice then split cleanly: two fixtures
  passed quality gates and each scored 39/0/1, while two
  denser custody/access fixtures remained held because source-authority units
  were still partial or ledger-only. That makes dense custody/access authority
  the next diagnostic coordinate, not a reason to weaken the gate.
- Source-authority audit grammar now recognizes structural equivalents rather
  than one preferred predicate spelling. Access pairs expressed as
  `authorized_access/3` plus `access_authority_source/3`, and direct surfaces
  such as title, custody, publication authority, access authority, and negative
  authority count as source-authority delivery. Shallow presentation rows still
  do not count. Replaying the held authority slice without recompilation moved
  the custody/title/access packet from held to pass, while the probate/access
  register remained held for lifecycle/state backbone loss. The newly
  pass-qualified custody packet then scored 34/1/5, showing
  that detector calibration was necessary but not sufficient; remaining misses
  are still compile/hybrid resolution pressure.
- Lifecycle/state quality gates are now stricter about what they mean. Token
  matching prevents words such as `estate` from firing the `state` lifecycle
  marker, and schedule/deadline/static-status snapshots are no longer treated
  as operational lifecycle transitions. Static contested/uncontested values now
  count as state backbone when they appear in direct rows. With those
  calibrations, the probate/access register also passed quality without
  recompilation and scored 36/0/4. The authority transfer
  slice therefore becomes a clean measurement set: two simpler authority probes
  at 39/0/1, one dense custody/title/access probe at 34/1/5, and one dense
  probate/access probe at 36/0/4. The remaining pressure is concrete
  compile-surface coverage, not compatibility-adapter resurrection or looser gates.
- A six-fixture stranded-source promotion slice tested whether recent
  compile-surface invariants move the largest native gap class before a full
  stamp. Against the prior native direct-surface stamp on the same fixtures, QA
  moved from 196/6/38 to 215/4/21 over 240 questions, with compile-surface gaps
  dropping from 35 to 18. The slice is not a
  stamp, because two compiles carried caveats, but it is strong directional
  evidence that source-record promotion and quality-gate calibration are
  reducing real native misses. A source-surface audit on the new slice still
  found 9 compile-surface rows where answer text remains stranded only in
  source-record rows, so the next repair target is direct promotion of
  recurring source-stated identity, role, location, status, and
  document-reference values without copying fixture vocabulary.
- A proposed prompt-level compact-label micro-fact invariant was tested and
  rejected for now. A two-fixture replay on label-heavy fixtures regressed
  relative to the preceding stranded-source slice, so the wording did not earn
  an architecture slot. The lesson is that compact source-record promotion
  needs instrumentation or profile-palette support, not another broad prompt
  sentence.
- Compile-surface invariant audit now includes source-record promotion
  telemetry. It scans compact source-record labels, fields, inline fields, and
  cells for structurally promotable identity/role/id/date/status/list-like
  values, then reports values whose tokens are not substantially covered by
  direct admitted rows. This is telemetry only, not a quality hold. On the
  six-fixture stranded-source slice it reports 1433 compact candidates and 169
  stranded candidates after using only the latest compile per fixture. A
  calibration check confirmed overlap with all 9 QA-proven stranded rows, but
  the candidate set is still too broad for a hard gate. The next step is to
  reduce false positives or use the telemetry as a targeted retry hint, not as
  permission to promote every compact source-record value.
  The telemetry now classifies stranded candidates into fixture-free queues
  before any repair is attempted. On the same slice the largest classes were
  compact identifiers (171), source addresses/headings (39), other source
  detail (29), date/time values (27), and identity/role values (9). This keeps
  the next work out of a generic "promote labels" trap: compact ticket/tag/id
  recovery, source-address recovery, and date/status/role recovery are
  different surfaces with different safety checks.
- Source-record ledgers preserve fidelity but are not semantic substitutes.
  When source rows carry answer-bearing identity, status, count, time, amount,
  role, authority, or rationale, the target state is a direct admitted predicate
  or stricter profile surface, not source text as the only carrier.
- Compile-quality gates now distinguish true compile loss from noisy audit
  alarms. Generic detail/event wrappers may remain as additive residue, but
  they are flagged when concrete backbone rows disappear. Calibration has
  already separated false lifecycle alarms from real quantity-backbone drift.
  Date-like atoms in direct rows now count as date/time backbone evidence, so
  a row such as `event(..., 2026_04_24, ...)` is not mistaken for a missing
  date surface merely because the predicate name is not date-specific.
- Quantity-rich event preservation now has the same bounded shape as
  source-detail preservation: a deterministic vocabulary extension can add
  `event_measurement/4` only when profile admission sees repeated numeric
  event/log details and no direct quantity-bearing event carrier. This is
  vocabulary-only and extracts no facts. Focused replay proved the slot can
  carry setpoint and feed-rate values; four-fixture replay still found one
  stochastic sensor hold, so this is an architectural advance, not a stamp.
- A broader native direct-surface stamp-candidate run on 2026-05-18 gives the
  current empirical reading after the recent compile-surface work. All 56
  source fixtures compiled and scored through the current direct-surface path:
  `1902/100/160` over 2163 questions, or 87.93% exact. This is below the
  prior 89.41% QA-only anchor, so the cumulative work has not earned a freeze.
  The compile quality gate held 20 of 56 fixtures. Pass fixtures scored 88.77%
  exact; held fixtures scored 86.50%, so the gate is directionally predictive
  but not sufficient. The dominant not-exact surface remains compile-surface
  loss: 165 compile-surface gaps out of 261 not-exact rows, with 81 answers
  stranded only in source-record rows. Compatibility adapters are no longer the explanation;
  direct surface preservation is.
- A 2026-05-19 QA-only remeasure on the same native compile root tested the
  query-layer promotion of status-at-date interval inference into core runtime
  behavior. The full fresh OpenRouter run scored `1959/73/200` over 2233
  questions with `0` compatibility rows, `0` runtime load errors, and `0` write
  proposals. Because this run evaluated 70 more rows than the prior scorecard,
  the clean comparison is the 2163-row overlap: exact rows moved from `1902`
  to `1905`; old status/state compile-gap rows had 8 improvements, 1
  regression, and 13 unchanged rows. The result validates the core interval
  inference move but does not constitute a new freeze stamp. The remaining
  compile-surface map is led by `other_answer_bearing_detail` (43 rows) and
  `source_reference` (25 rows), so the next pressure is source-addressed answer
  detail preservation rather than restoring retired compatibility adapters.
- The source-surface gap audit now splits source-addressed answer detail more
  sharply. A classifier leak where the substring `id ` matched ordinary
  question text such as `did ` was removed. The old 43-row
  `other_answer_bearing_detail` bucket now resolves into concrete pressure
  classes such as `point_in_time_status` (14), `source_actor_or_authority`
  (10), `count_or_total` (9), `official_or_staff_role_identity` (8),
  `deadline_or_duration_arithmetic` (8), `monetary_rate_or_amount` (7),
  participant statements (6), source stated facts (5), set/list detail (5),
  and true compact identifiers (4).
  A second pass removed source-reference substring traps such as `report`
  matching `reported` and `date` matching `update`, while preserving explicit
  source-addressability questions ahead of status/rule words inside the quoted
  statement. The lesson is that the next repair should follow the refined
  coordinate, not a generic prompt broadening for "details."
- A focused status-heavy replay tested the refined pressure against a fresh
  current compile. The new compile emitted direct status-transition and lab
  result surfaces that the older stamp compile had missed, and a tiny QA replay
  over the six prior status/result misses scored `5/0/1`. The one remaining
  miss is a denser subset-status question where the source distinguishes a
  moved subset from the parent population. This confirms two layers: current
  compile guidance can recover missing transition anchors, and the remaining
  hard case is scoped population state, not a reason to restore retired
  compatibility machinery.
- The scoped-state query layer now treats admitted `*_status_change` rows as
  interval anchors and exposes parent/subset population state evidence as a
  core query surface. A focused three-row replay on the same fresh status-heavy
  compile moved from `1/2/0` before the repair to `3/0/0`. Point-in-time status
  over status-change rows became exact, and the subset-status case resolved by
  exposing parent status, subset event window, and nearby subset state anchors
  together. The important guardrail is that event-window support does not assert
  the subset's interior status; it only exposes the admitted window and nearby
  state anchors for the answering layer.
- Count pressure is now split between stale wins, missing compile delivery, and
  query access. A focused replay of the old `count_or_total` rows found two
  already exact under the current instrument. A new core unary distinct-count
  surface handles the query-layer case where a placeholder-like constant
  over-binds an enumerable unary predicate, then collapses compact identifier
  aliases for the distinct count. The first replay moved a numbered-exhibit row
  from miss to exact by exposing raw count `10`, distinct count `9`, and the
  alias group responsible for the difference.
- Deadline/duration pressure is mostly compile delivery at this point. A focused
  replay of the old `deadline_or_duration_arithmetic` rows found three already
  exact under the current instrument. The remaining live failures are dominated
  by missing raw temporal/event rows or contradictory derived statuses; one
  apparent query arithmetic bug did not reproduce on rerun, so no new duration
  support surface was admitted from that pass.
- Monetary/rate pressure is also compile-side. A focused replay of the old
  `monetary_rate_or_amount` rows found one already exact, with the remaining
  six rows all classified as compile-surface gaps. This bucket should move next
  through compile-surface preservation and profile delivery, not QA-side numeric
  patching.
- Quantity/value preservation now has an audit contract rather than another
  query patch. `quantity_value_delivery_contract` detects source-stated counts,
  quantities, rates, durations, thresholds, or monetary values that remain only
  in source-record text or broad wrappers instead of admitted rows with subject,
  value, and measure/unit slots. A calibration pass over the latest native
  compile artifacts found `22` passes, `11` palette-offered-but-undelivered
  cases, `7` missing direct quantity delivery cases, `6` shallow wrapper-only
  cases, and `10` not applicable after stripping source-row coordinates such as
  headings, labels, and table-row numbers. A targeted sensor recompile after the
  direct-value guidance still produced `quantity_palette_offered_but_undelivered`
  for `event_measurement/4`: the candidate carrier existed, but only
  `event_description` rows were emitted. That makes this a delivery/preservation
  problem, not merely a vocabulary problem.
- Profile delivery telemetry now carries that distinction inside the compile
  artifact. When profile admission offers a direct quantity carrier and the
  source has quantity-event pressure, `profile_delivery` records whether emitted
  facts actually populated the carrier. Missing delivery raises
  `quantity_carrier_offered_but_undelivered` in compile health; successful
  delivery leaves the artifact healthy. This prepares the next layer for
  retry/consensus decisions based on compile health rather than a later audit
  script alone.
  A three-fixture OpenRouter replay on 2026-05-19 confirmed the path can
  improve delivery rather than only classify it: the measurement-heavy probe
  emitted `event_measurement/4` rows and had no quantity carrier delivery
  warning. The replay still exposed residual pressure in direct event backbone,
  source-reference, and source-authority pairing, which keeps the next work on
  compile-surface preservation instead of query-layer patching.
  A current QA-only replay of the 26 old quantity/duration source-surface rows
  scored `8/3/15` on the frozen native compile artifacts. The four rows still
  classified as query-surface pressure did not improve under a transfer-safe
  source-text-access experiment, and two reclassified into compile or hybrid
  pressure. The live quantity work is therefore compile delivery and join
  preservation, not broader query hinting.
  One hybrid row did earn a generic query-layer repair: when admitted
  category/count/date rows expose included and unresolved categories, and an
  admitted total-count surface exists, `category_count_ratio_support` computes
  the included total and percentage without reading source prose. The primitive
  was validated on unlike inventory rows plus a non-disposition measurement
  control, then replayed on the recall/inventory fixture where the March 15
  accounted-unit percentage moved to exact. A fresh 40-row replay of that
  fixture scored `31/2/7`, with zero compatibility rows and no runtime errors.
  A two-draw stability audit over the four-fixture quantity slice showed the
  harder compile-stability problem directly: all four fixtures had palette and
  direct-fact drift. A bounded preservation candidate for a municipal notice
  row merged only volatile `source_authority/3` and `source_detail/4` rows from
  a sibling draw into the anchor compile; the public-notice question moved to
  exact, but a nearby emergency-ratification row came back partial because the
  query plan did not assemble the hour calculation. Multi-draw preservation is
  therefore an active experiment, not a default stamp path yet.
  The follow-up invariant audit and compile-health telemetry now record
  `event_identifier_temporal_backbone_contract` / `event_identifier_date_only`:
  event ids may contain dates, but date-bearing ids do not count as temporal
  backbone unless a same-event date/time row is also emitted. On the same
  four-fixture slice this signal was bounded: four compiles were not
  applicable, one passed with explicit temporal rows, and three flagged
  identifier-only dates. That makes the next pressure a generic
  compile-delivery issue, not a fixture-specific arithmetic patch.
- The same profile-admission/profile-delivery shape now covers status/state
  pressure. Point-in-time status, current condition, availability, pending
  resolution, supersession, and partial-population state must offer a direct
  carrier that binds subject or subset, state/status value, and temporal/source
  scope. If the palette offers that carrier but emitted facts never populate it,
  compile health records `status_state_carrier_offered_but_undelivered`.
  Shallow palettes can now receive a vocabulary-only `status_state_at/4`
  extension; that extension admits no facts by itself and exists only to give
  the compiler a transferable carrier when the source already has scoped
  status/state pressure. The recognizer explicitly keeps source/provenance
  claim rows from satisfying the status/state contract just because one argument
  is named `status`; a source-attributed claim can support a status, but it is
  not itself the direct status/state surface.
- Source-reference pressure now has the same audit shape.
  `source_attributed_claim_contract` detects source-record prose that attributes
  a status, finding, authority, or unresolved claim to a memo, report, statement,
  note, opinion, source actor, or document, then asks whether admitted state has
  a direct row binding source/document, content, and source/scope. On the latest
  native compile artifacts it found `29` passes, `21` missing direct
  source-reference surfaces, and `6` not applicable. This is measurement only:
  it does not license copying local source names into the architecture, but it
  exposes when attribution remains stranded in source-record text.
- Source-attributed claims now also participate in profile admission, profile
  delivery, and vocabulary-only extension. Shallow palettes can receive
  `source_attributed_claim/4`, and compile health records
  `source_claim_carrier_offered_but_undelivered` when that carrier is offered
  but never populated. This keeps source/reference repair in the same measured
  architecture as quantity and status/state, rather than adding another
  after-the-fact special case.
- Source-authority delivery now has the same compile-health signal. When a
  source states that an authority, rule, order, policy, source, or body governs
  an action/status/finding/scope and a compatible authority carrier is offered,
  missing emitted rows raise `source_authority_carrier_offered_but_undelivered`.
  The recognizer is intentionally stricter than provenance: plain `source`
  wording does not make a claim row authority-like unless authority, governing,
  order, policy, or rule semantics are also present.
- Batch quality gates now read profile-delivery findings directly. A replay
  with quality retry repaired the source-authority delivery gap by emitting
  `source_authority/3`, but the final artifact still had a status/state delivery
  warning. That result matters: quality retries can repair delivery failures,
  and the gate now treats remaining profile-delivery warnings as hold reasons
  instead of allowing a superficially clean pass.
- A fresh quality-retry run with profile-delivery reasons included closed the
  same authority/source-claim pressure cleanly: the initial draw exposed
  source-authority and source-claim offered-but-undelivered flags, the retry
  received generic correction lines for both, and the final artifact passed with
  zero compile-surface contract flags and zero profile-delivery flags. This is
  the current model for compile-stability work: detect offered-but-undelivered
  carriers, retry with fixture-free slot contracts, then only treat the draw as
  stamp-ready if delivery telemetry is clean.
- The follow-up three-fixture slice showed why coverage matters: two fixtures
  passed clean, while the authority-heavy case improved from no direct authority
  rows to partial direct coverage. The retry instruction now explicitly asks for
  every distinct stated authority coordinate, not only a representative
  authority row.
- A later replay with the stronger authority/status/source-claim retry language
  regressed back to offered-but-undelivered source-authority and source-claim
  carriers. That is the current decision point: this is no longer primarily a
  wording problem. The evidence now points at compile variance/preservation, so
  further progress should consider multi-draw consensus or deterministic
  preservation for offered carriers rather than another prompt-only tweak.
- The compile-surface audit now reports relation-contract status counts in its
  top-level summary, so pressure boards no longer need ad hoc counting scripts
  for quantity delivery, source attribution, status scope, repeated-record
  delivery, financial derivation, and wrapper/backbone contracts.
- The participant-statement status recognizer was tightened so plain negation
  in a statement no longer counts as binding/advisory status pressure. After
  calibration, its native contract pressure is `6` missing status companions,
  `8` missing structural surfaces, `1` partial, `2` pass, and `39` not
  applicable; the previous broader count was mostly recognizer noise.
- The vague-wrapper/backbone contract now uses row-local triggering instead of
  cross-joining event/date/subject/status words from unrelated source rows. On
  the native compile set this moved the contract from `3` not applicable to
  `12` not applicable, while preserving `22` missing backbone and `7`
  wrapper-without-backbone signals that still look like real compile pressure.
- Transfer validation is mixed and active. Model/provider variation is treated
  as variance evidence, not as a replacement for structural delivery contracts.
  The next compile-layer pressure is preserving direct identity, role,
  location, state, date/time, quantity, and source-authority surfaces when the
  source-record ledger already carries those values. Do not broaden prompt
  guidance without replay evidence; use telemetry, palette priors, targeted
  retries, or multi-draw consensus experiments to reduce variance without
  teaching the harness fixture vocabulary.
- Retrieval-constrained palette grounding is now an audit-only experiment, not
  active compiler behavior. A first coordinate-level proxy on six unstable
  native direct-surface fixtures showed that retrieval scope is the load-bearing
  variable. Searching the global 948-signature registry recalled only 18 of 49
  exact hinted schemas at `k=20`; scoping retrieval to the active fixture/profile
  candidate palette recalled 46 of 49. Source-gap evidence did not beat
  fixture/profile scoping in this proxy. Hard category filtering reduced recall
  to 31 of 49, or 36 of 49 with source-gap context, so coarse lens/category
  labels are ranking hints, not admission filters yet. The result says top-k
  gating is plausible but not ready for admission: the next layer needs
  source-span attachment, richer registry metadata, or multi-draw palette
  consensus before constrained emission.
- A mixed-protocol repeated-compile stability audit on 2026-05-18 used the
  available native direct-surface, surface-promotion, and delivery-diagnostic
  compile roots as variance evidence. This is not a stamp and not a clean N=3
  statistic, because the roots used different prompt/protocol states. It is
  still diagnostically useful: across 165 compile artifacts and 56 fixtures it
  found only 5 palette-stable fixtures, 2746 unstable candidate signatures,
  159 predicate-arity drift rows, 2383 signature-delivery drift rows, and 618
  candidate zero-yield signatures. The lesson is that the next layer cannot
  merely retrieve the right schema; it must also stabilize whether that schema
  is offered, whether its arity stays fixed, and whether offered schemas
  produce direct rows. Treat this as pressure for a clean same-protocol N=3
  palette/delivery experiment, not as permission to constrain admission yet.
- A cleaner same-protocol slice on three repeated-draw probes confirmed that
  the pressure is real, not merely an artifact of mixing old and new protocol
  roots. Across 9 compile artifacts, 0 of 3 fixtures were palette-stable. The
  audit found 121 unstable candidate signatures, 3 predicate-arity drifts,
  118 signature-delivery drifts, 18 candidate zero-yield signatures, and 1019
  unstable direct facts. The worst sensor/time fixture had only 2 common
  signatures across a 61-signature union; a variance/authority fixture had only
  2 common signatures across a 40-signature union. The interpretation is now
  sharper: query-layer cleanup is not enough, and prompt broadening is too
  blunt. The next architectural response should be audit-first palette
  stabilization: profile-local retrieval, multi-draw palette priors, or
  targeted retry when high-value schemas are offered inconsistently.
- Registry-mode calibration on the same three probes split the options:
  intersection registries were too sparse (2, 2, and 5 signatures), union
  registries were too broad (61, 40, and 29 signatures), and majority-threshold
  registries were the plausible middle (9, 10, and 11 signatures). Majority
  signatures are not facts and do not earn admission by repetition. They are
  candidate vocabulary priors for later constrained compile or retry tests.
- A first majority-prior causal probe on the sensor/time fixture offered and
  delivered all 9 majority-prior signatures in a fresh compile, while allowing
  6 non-prior signatures through the normal compiler path. The compile passed
  quality gates with 15 candidate predicates and 81 admitted rows. QA remained
  only 30/3/7 over 40 questions, below stronger recent runs on the same
  fixture, so the result is a partial win: soft priors can stabilize recurring
  vocabulary without hard-caging the compiler, but they do not recover
  rare/high-value answer-bearing surfaces by themselves.
- Running the retrieval audit on the 10 not-exact rows from that same replay
  recalled hinted schemas for 9 of 10 rows at `k=10` from the 15-signature
  active candidate palette. This says the vocabulary neighborhood is usually
  visible by the end of compile. The unresolved pressure is source-span
  binding, direct-row delivery, and query composition, not simply absence of a
  candidate predicate name.
- The compile-stability audit now imports generic profile-delivery findings
  from compile artifacts and summarizes them across draws. On the four recent
  authority/claim/status delivery draws for one variance probe, it found
  source-authority carrier loss in 2 of 4 draws, source-claim carrier loss in
  2 of 4 draws, and status-state carrier loss in 1 of 4 draws. The key lesson
  is that targeted retry can recover direct carriers in some draws, but the
  layer is not stable enough to treat prompt wording as the final repair. This
  is evidence for preservation or multi-draw consensus experiments.
- The same stability audit now splits profile-delivery findings by response
  path. If an offered carrier is missing in some draws but delivered in others,
  it is a multi-draw preservation candidate; if it is never delivered, it stays
  a compile-retry or deterministic-projection candidate. In the authority
  replay, source-authority and source-claim carriers are preservation
  candidates, while the status-state carrier is still projection/retry pressure.
- A bounded preservation-candidate builder now exists for experiments. It takes
  the stability audit's multi-draw preservation signatures, keeps one anchor
  compile's source-record ledger, and imports only direct facts matching those
  volatile carrier signatures from sibling draws. On the authority replay, this
  selected `source_attributed_claim/4` and `source_authority/3`, adding 9
  direct facts to the anchor rather than unioning the whole compile set. This
  is not default admission; it is a disciplined replay artifact for testing
  whether row-level preservation can beat prompt-only retry.
- The first QA replay of that bounded preservation candidate scored `33/3/4`
  on the 40-question authority/claim/status fixture. It recovered the volatile
  carriers without runtime errors or writes, but did not lift QA by itself. The
  residuals were current-state temporal joins, correction reasons, and
  pre-amendment state resolution. So preservation is a substrate stabilizer;
  answer gains still need query composition or missing direct state surfaces.
- A query-surface residual audit now separates post-compile query failure
  signals from compile-surface gaps. On the preservation replay, all 4
  query/hybrid residual rows carried fallback evidence: 3 used relaxed
  over-bound query widening, and 4 used repaired source-text contains filters.
  That makes the next query-layer pressure measurable: reduce reliance on
  broad relaxed/source-text fallbacks by planning direct state/date joins over
  already admitted rows.
- Query placeholder repair now treats compact lowercase slot labels for
  state/value/time fields as variables when the original query returns no rows.
  This is a runtime fallback repair, not new compile vocabulary. On the four
  preservation-replay query/hybrid residual rows, exacts moved from `0/4` to
  `3/4` and relaxed over-bound fallback dropped from `3` rows to `0`. A fresh
  full 40-row replay landed at `34 exact / 1 partial / 5 miss`, so this is a
  useful query-layer cleanup but not a full residual repair.

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
python scripts/plan_story_world_fixture_runs.py --fixture <fixture_a> --fixture <fixture_b> --qa-limit 40 --out-json tmp/story_world_runs/promoted_incoming_cold_run_plan.json --out-md tmp/story_world_runs/promoted_incoming_cold_run_plan.md
python scripts/select_qa_mode_without_oracle.py --selection-policy guarded_activation --group <name>:baseline=<QA_JSON>+<FAILURE_SURFACE_QA_JSON>,candidate=<QA_JSON> --out-json <OUT_JSON> --out-md <OUT_MD>
python scripts/plan_selector_risk_gate.py --baseline-run protected=<SELECTOR_JSON> --candidate-run guarded_activation=<SELECTOR_JSON> --transfer-comparison <SELECTOR_POLICY_COMPARISON_JSON> --out-dir tmp/selector_risk_gates
python scripts/audit_compile_surface_stability.py --compile-json <COMPILE_JSON_OR_DIR> --compile-json <COMPILE_JSON_OR_DIR> --out-json tmp/compile_surface_stability.json --out-md tmp/compile_surface_stability.md
python scripts/audit_retrieval_constrained_palette.py --boundary-plan-json <BOUNDARY_PLAN_JSON> --compile-root <COMPILE_ROOT> --registry-scope fixture --out-json tmp/retrieval_constrained_palette_audit.json --out-md tmp/retrieval_constrained_palette_audit.md
python scripts/audit_profile_palette_prior_delivery.py --registry-json <PROFILE_REGISTRY_JSON> --compile-json <COMPILE_JSON_OR_DIR> --out-json tmp/profile_palette_prior_delivery_audit.json --out-md tmp/profile_palette_prior_delivery_audit.md
python scripts/build_profile_palette_registry.py --compile-json <COMPILE_JSON_OR_DIR> --mode first --out-json tmp/profile_palette_registry.json --out-md tmp/profile_palette_registry.md
python scripts/build_compile_preservation_candidate.py --stability-json tmp/compile_surface_stability.json --fixture <fixture> --compile-json <COMPILE_A.json> --compile-json <COMPILE_B.json> --out-json tmp/compile_preservation_candidate.json --out-md tmp/compile_preservation_candidate.md
python scripts/audit_query_surface_residuals.py --qa-json <QA_JSON> --out-json tmp/query_surface_residuals.json --out-md tmp/query_surface_residuals.md
python scripts/run_domain_bootstrap_file_batch.py --fixture <name> --compile-source --compile-flat-plus-plan-passes --source-record-ledger --source-record-ledger-facts --quality-gate --quality-retry-on-hold --profile-registry tmp/profile_palette_registry.json --profile-registry-palette-prior
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

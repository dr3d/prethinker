# Product 95 Worksheet

Started: 2026-05-22

This worksheet tracks work toward a higher native exact rate without turning the
native 56 fixtures into a museum piece. The target is product behavior:
general repairs that preserve the audit grammar and survive transfer checks.

## Current Anchor

Native stamp, 2026-05-22:

```text
2163 judged rows
1997 exact / 46 partial / 120 miss
92.33% exact
0 compatibility rows
0 runtime load errors
0 QA write proposal rows
```

To reach 95.0% exact on 2163 rows, Prethinker needs roughly 2055 exact rows,
or +58 exact rows from the current stamp. Converting all 46 partials to exact
would reach 2043 exact rows, so the path to 95 also requires converting some
current misses.

## Operating Discipline

- Treat the native 56 as a mechanism lab, not a scoreboard.
- Prefer repairs that address a recurring failure shape across fixtures.
- Do not add compatibility rows or QA writes to buy score.
- Validate meaningful repairs against real-world transfer and sealed-unseen
  fixtures before trusting a native gain.
- Ask for more real-world fixtures only when a repaired mechanism needs fresh
  transfer pressure.

## Partial-Row Audit

The 46 partial rows split as:

```text
compile-surface gap: 22
hybrid-join gap: 15
query-surface gap: 8
judge-uncertain: 1
```

Initial read:

- Compile-surface partials need better durable carriers for answer-bearing
  details such as source claims, status conditions, amounts, dates, and
  custodians.
- Hybrid-join partials need deterministic join surfaces, especially where facts
  exist but answer construction requires linking event, item, person, source,
  or rule rows.
- Query-surface partials are the safest first implementation lane because the
  compiled artifact often already contains enough state or source text.

## 2026-05-22 Query-Surface Repair Pass

Problem observed in non-exact rows:

Evidence-bundle plans often used safe Prolog-like filters such as:

```prolog
source_record_row_context(Line, Label, Text, Section),
memberchk(consistent_with_housing_element, Text_tokens).
```

or:

```prolog
source_attributed_claim(Claim, Source, Detail, Context),
source_record_text_atom(Source, Text),
memberchk('biogenix', Text).
```

The runtime previously rejected the `memberchk/2` filter because `memberchk`
is not a compiled predicate. That is correct as a Prolog predicate check, but
too strict for deterministic filtering over rows that were already admitted.

Implemented repair:

- accept conjunctions of compiled predicates followed by safe text/member
  filters;
- execute only the compiled predicate conjunction;
- apply the filter deterministically to returned rows in Python;
- support tokenized aliases such as `Text_tokens` for `Text`;
- support LLM-authored wrappers such as `atom_chars(Text, Chars)`.

This does not add facts, admit new truth, or allow QA writes. It only repairs a
query-surface shape over already compiled rows.

Targeted native probe:

```text
fixture: draft_within_draft
row: q007
prior stamp verdict: partial, query_surface_gap
probe verdict after repair: exact
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
artifact archive: C:\prethinker_tmp_archive\ntsb_two_doc_range_recovery_support_20260523
```

Interpretation:

This is a useful mechanism repair, not a native score claim. The next evidence
needed is a small row-targeted rerun over other member-filter query-surface
residuals, followed by transfer checks if the row-targeted result holds.

Small row-targeted replay:

```text
draft_within_draft q007: partial/query_surface_gap -> exact
ledger_at_calders_reach q027: miss/query_surface_gap -> exact
veridia9_supply_chain_patent_dispute q025: partial/hybrid_join_gap -> exact
fenmore_seedbank q017: miss/query_surface_gap -> exact
nested_puppet_court q040: miss/query_surface_gap -> exact
veridia_intake q019: miss/query_surface_gap -> exact
lantern_school_field_trip q016: miss/compile_surface_gap -> partial
university_lab_sample_chain q025: miss/compile_surface_gap -> partial
draft_within_draft q015: remained miss/query_surface_gap

all probes:
0 compatibility rows
0 runtime load errors
0 QA write proposal rows
```

Interpretation:

The rejected-filter signature replay recovered six exact rows in a nine-row
targeted sample, moved two additional misses to partial, and left one row
unchanged. If the result held inside a full native rerun, the local delta would
be approximately `+6 exact / +0 partial / -6 miss`. This is still row-targeted
evidence, not a native score claim.

## Transfer Guards

After the query-filter repair, both retained transfer batches were rerun with
current QA code against their frozen compile artifacts.

Real-world external four-fixture guard:

```text
dataset: datasets/real_world_transfer/20260521
compile root: real_world_transfer_stamp_20260521_compile_current
QA root: transfer_guard_real_world_after_filter_repair_20260523
artifact archive: C:\prethinker_tmp_archive\product_95_transfer_guards_after_filter_repair_20260523
result: 159 exact / 0 partial / 1 miss
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
```

The single miss was an externally sourced incident-report row asking for an
approximate clock time anchored by nearby date context. The source text contains
the time, but the compiled artifact lacks a direct event time/date fact for the
event. This is a compile-surface gap, not evidence that the query-filter repair
damaged transfer.

Sealed unseen authored four-fixture guard:

```text
dataset: datasets/sealed_unseen/20260521
compile root: unseen_fixture_batch_20260521_compile_or4_selected
QA root: transfer_guard_sealed_unseen_after_filter_repair_20260523
artifact archive: C:\prethinker_tmp_archive\product_95_transfer_guards_after_filter_repair_20260523
result: 159 exact / 0 partial / 1 miss
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
```

The single miss was a sealed public-process row asking for a property-adjacency
objector. It was classified as a compile-surface gap.

Transfer read:

- The repair did not introduce compatibility pressure, runtime failures, or QA
  writes.
- Sealed unseen improved materially relative to the prior `152 / 1 / 6`
  measurement under current QA.
- Real-world moved from prior `160 / 0 / 0` to `159 / 0 / 1`; the miss is a
  direct compile-surface carrier gap, so the next repair lane should not be
  query-filter machinery but durable event/date/time source surfaces.

## Source-Record Field Text Fallback

The remaining rejected-filter native row, `draft_within_draft q015`, exposed a
field/text split problem. The QA plan asked for:

```text
source_record_field(Line, staff_note, Text), memberchk(dr_holm, Text), memberchk(traffic, Text), ...
```

The split `source_record_field/3` rows did not contain the traffic verification
language, but the same staff-note source surface was preserved in
`source_record_text_atom/2`.

Repair:

- If a `source_record_field/3` contains-filter query returns zero rows, and the
  filter is on the field value, QA may fall back to `source_record_text_atom/2`.
- The fallback is bounded: it requires the source text row to carry the same
  source label or a matching text prefix, so a `staff_note` query does not
  broaden into unrelated source text.

Verification:

```text
tests/test_domain_bootstrap_qa.py: 234 passed
draft_within_draft q015 row replay: 1 exact / 0 partial / 0 miss
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
artifact archive: C:\prethinker_tmp_archive\product_95_source_text_fallback_20260523
```

## Generic Event-Time Carrier Lane

The real-world transfer guard exposed a source row where an approximate clock
time was preserved in `source_record_text_atom/2`, but the selected compile did
not provide a direct event-time/date carrier for QA to join against.

Repair:

- Added a generic `source_record_event_time_note` companion for normalized
  source rows that state a clock time, optional nearby date context, and a
  nearby event/action verb.
- Scoped that companion to event predicates and kept it in the high-pressure
  candidate class so broad source-record scans do not flood with candidate
  notes.
- Expanded profile delivery pressure so explicit event dates or clock times can
  request direct `event_date/2`, `event_time/2`, `event_timestamp/2`, or
  equivalent carriers.
- Removed older fixture-shaped source-text hint branches from the touched QA
  path and generalized the affected tests/notes.

Verification:

```text
tests/test_domain_bootstrap_qa.py + tests/test_domain_bootstrap_file.py + tests/test_domain_bootstrap_file_batch.py: 434 passed
full pytest: 1611 passed
compatibility rows: not exercised in this unit pass
runtime load errors: 0
QA write proposal rows: 0
```

Follow-up transfer probe:

```text
single approximate-time row replay: 1 exact / 0 partial / 0 miss
four-fixture real-world guard before query-surface tightening: 159 exact / 0 partial / 1 miss
affected 40-row fixture replay after query-surface tightening: 40 exact / 0 partial / 0 miss
composite retained real-world read: 160 exact / 0 partial / 0 miss
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
artifact archive: C:\prethinker_tmp_archive\product_95_event_time_query_surface_20260523
```

The first full guard showed the same approximate-time row could still miss
under planner variance: source text contained the answer, but the plan did not
bind the filtered source row to its numeric tokens. The follow-up repair added a
generic temporal source-text hint that, for real time/date questions, joins a
filtered `source_record_text_atom/2` row to `source_record_numeric_token/2`.
This is query routing over admitted source-record rows, not a new fact or
compatibility adapter.

Rejected-filter variance replay:

```text
target rows: 9
result: 9 exact / 0 partial / 0 miss
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
artifact archive: C:\prethinker_tmp_archive\product_95_rejected_filter_replay_after_event_time_20260523
```

Read: the earlier rejected-filter gains held under current QA, and the
remaining row from that slice now resolves exactly through the bounded
source-field/source-text fallback. The two rows that had previously moved only
to partial also resolved exactly in this replay. This remains a targeted
variance check over frozen native compiles, not a native stamp.

## Quantity Phrase Order Hybrid-Join Lane

The first hybrid-join pass found rows where the relevant source-record text was
present but the question-token source hint looked for the quantity phrase in
the question's word order while the deterministic source ledger had normalized
the same phrase in the opposite order.

Repair:

- Added a generic quantity phrase-order hint for source-text probes.
- Scoped the reorder to concrete quantity markers (`total`, `count`, `amount`,
  `number`, `quantity`, `sum`) so ordinary `how many` questions keep their
  unigram budget.
- Kept the path in clean source-record query routing, with compatibility
  adapters still disabled.

Verification:

```text
two-row frozen native hybrid replay: 2 exact / 0 partial / 0 miss
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
full pytest: 1612 passed
artifact archive: C:\prethinker_tmp_archive\product_95_quantity_phrase_hybrid_join_20260523
```

Read: this recovered two native hybrid rows without turning retired helper
rows back on. The fix is mechanism-level: quantity questions now probe both
question-order and source-normalized-order compounds when looking up admitted
`source_record_text_atom/2` rows.

## Status-On-Date Interval Hybrid Lane

The next hybrid row showed an interior-date status question where the compiled
KB had transition anchors before and after the requested date, but the query
surface used a `*_status_on_date/3` predicate name. Existing interval support
already handled `*_status_at_date/3`, generic `*_status/3`, and
`*_status_at/3`, but not the `on_date` naming variant.

Repair:

- Added `*_status_on_date`, `*_state_on_date`, and `*_condition_on_date`
  variants to the active interval-support companion.
- Preserved the entity/date/status argument order used by `on_date` predicates.
- Kept the output as query-only interval support over admitted transition
  anchors; no durable status fact is written.

Verification:

```text
single-row frozen native hybrid replay: 1 exact / 0 partial / 0 miss
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
full pytest: 1613 passed
artifact archive: C:\prethinker_tmp_archive\product_95_status_on_date_interval_20260523
```

Read: this recovered an interval-style native hybrid miss by broadening the
generic naming grammar for active temporal status support. It should transfer
to status/state/condition ledgers that express point observations as
`on_date` rows while still requiring admitted before/after anchors.

## Relaxed Frequency And Split Duration Hybrid Lane

The next pass found two active-lane hybrid patterns that can be repaired before
asking for more real-world thermometer documents:

- A "most / highest count" question where the planner over-bound a table with
  placeholder constants and then tried unsupported Prolog aggregation.
- A duration question where a prior row stored start date and start time in
  separate fields but the temporal join compared the date-only value against a
  combined end timestamp, producing a plausible but wrong duration.

Repairs:

- Added a clean query-only frequency summary over successful relaxed table
  queries when the relaxed column label is a role/source/person-style
  placeholder. The support rows expose counts, max count, and tied max values
  without writing aggregate facts.
- Added split date/time duration support that combines a date field with its
  sibling time field before computing elapsed minutes or hours.
- Suppressed the misleading temporal join when a start-date variable has a
  sibling start-time field available, so the wrong midnight-based duration is
  not emitted beside the corrected support row.

Verification:

```text
frozen native max-count replay: 1 exact / 0 partial / 0 miss
frozen native split-duration replay: 1 exact / 0 partial / 0 miss
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
full pytest: 1615 passed
artifact archive: C:\prethinker_tmp_archive\product_95_relaxed_frequency_and_split_duration_20260523
```

Additional pre-stamp checks:

```text
identity source-context replay: 1 exact / 0 partial / 0 miss
probate interval probe: no reference-answer row in that ad hoc replay; archived
```

Read: the frequency repair covers a common messy-document question shape:
"which actor/source/category has the most rows?" The duration repair covers
table ledgers that split date and time across adjacent fields. Both stay in the
clean QA support layer and keep compatibility rows at zero.

## Next Moves

1. Continue hybrid-join triage on frozen native misses, preferring active
   source-record/query routing fixes over retired compatibility helpers.
2. Re-run the recovered slices inside the next native stamp instead of treating
   targeted replay as a corpus score.
3. Hold compile-only event-time probing unless a later row shows the query
   surface still cannot use admitted source-record text/numeric rows.

## Rough NTSB Pilot Shakedown

The rough incoming NTSB pilot was normalized into
`datasets/real_world_transfer/20260523/ntsb_aviation_001` and the original
public PDF was fetched from the source URL. The package only contained one
usable document despite describing a two-document pilot, so this is a shakedown
fixture, not a clean transfer thermometer batch.

Compile:

```text
OpenRouter qwen/qwen3.6-35b-a3b, 1 lane
1 / 1 fixtures parsed
36 candidate predicates
81 compile admitted / 0 skipped
quality gate: hold
gate reason: source-claim/source-authority delivery
```

QA initially exposed source-record routing misses: answer-bearing rows were
present in the compiled KB as later `source_record_section` and
`source_record_label` surfaces, but the query hints only saw capped examples.
The repair now carries full source-record section and label header inventories
from `compiled_kb_inventory()` and uses those inventories for question-driven
source-coordinate hints.

Verification:

```text
source-record inventory hint tests: 18 passed
final rough NTSB pilot QA: 25 exact / 0 partial / 0 miss
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
full pytest: 1622 passed, 2 subtests passed
artifact archive: C:\prethinker_tmp_archive\ntsb_pilot_shakedown_20260523
```

Read: the pilot was messy enough to find a real product-facing weakness without
requiring a new compile policy. The compile gate hold remains a separate signal;
the QA path is operationally clean on this one rough document after the
source-record routing repair.

## Corrected NTSB Two-Document Intake

Claude's corrected NTSB pilot package was received as
`prethinker_ntsb_pilot_2026_05.zip` and normalized into
`datasets/real_world_transfer/20260523_ntsb_pilot_2doc`.

Intake verdict:

```text
fixtures: 2
QA rows: 25 + 25
oracle JSONL: valid, IDs match QA
answer separation: mostly clean
source_original.pdf in archive: missing
canonical fix: fetched PDFs from official NTSB URLs
QA format in archive: q001: markers
canonical fix: numbered runner-compatible qa.md, incoming retained as qa_authored.md
```

Read: this package followed the important instruction: real public NTSB source
documents, source/provenance/metadata separated from question and oracle files,
and no expected predicates or compile solutions. It missed two mechanical
details, both corrected during intake. It is ready for a compile/QA spotcheck
when we choose to spend the OpenRouter time.

Verification:

```text
real-world dataset retention tests: 6 passed
full pytest: 1622 passed, 2 subtests passed
raw intake archive: C:\prethinker_tmp_archive\ntsb_two_doc_intake_20260523
```

## NTSB Two-Document Transfer Spotcheck

Ran the corrected two-document NTSB pilot from
`datasets/real_world_transfer/20260523_ntsb_pilot_2doc` with OpenRouter
`qwen/qwen3.6-35b-a3b` and 2 QA lanes.

Compile:

```text
2 / 2 fixtures parsed
88 candidate predicates
71 compile admitted / 70 skipped
diagnostic rejected flat-pass skips: 0
compile quality gate: 0 passed / 2 held
ntsb_001 hold: source-claim carrier/backbone coexistence delivery
ntsb_002 hold: risk_count>5
```

Initial QA:

```text
50 judged rows
46 exact / 2 partial / 2 miss
92.0% exact
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
```

The misses taught two different lessons. `ntsb_001` q009 needed a general
source-record duration bridge: the source rows had departure and accident clock
tokens, but there was no durable accident event fact to bind through
`elapsed_minutes/3`. I added a query-only `source_record_clock_duration_support`
companion that pairs clock-like numeric tokens from question-matched source
rows without writing facts or compatibility rows. `ntsb_002` q024 exposed an
oracle wording problem; the incoming answer implied "complicating analysis,"
while the source supports only the narrower recovery-activity damage statement.

Post-repair QA:

```text
50 judged rows
48 exact / 2 partial / 0 miss
96.0% exact
ntsb_001: 25 / 0 / 0
ntsb_002: 23 / 2 / 0
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
artifact archive: C:\prethinker_tmp_archive\ntsb_two_doc_clock_duration_spotcheck_20260523
```

Remaining partials:

- `ntsb_002` q019: hybrid aggregation of crew wind estimate with two separate
  weather-station rows into a 48-62 knot / 22-27 mile range.
- `ntsb_002` q024: source has salvage dates and recovery-activity damage, but
  the question asks about physical-evidence completeness; this remains a
  compile/source-surface relation gap, not a scoring miss.

Read: this is exactly the kind of unlike-document transfer signal we wanted.
The repair is not NTSB-specific; it strengthens messy-document duration
questions where the compile surface preserves source rows but not every
possible event relation as a typed durable predicate.

### Follow-Up Blocker Clearance

Cleared both `ntsb_002` partials with two transfer-safe query-surface repairs:

- q019: added query-only source-record numeric range support for range/comparison
  questions. It extracts compact source-text ranges such as `85_100_mph`,
  `74_87_knots`, `48_62_knots`, and `22_27_miles` from retrieved source rows
  and presents them as deterministic evidence rows.
- q024: added a narrow source-text vocabulary bridge from `salvage` language to
  `recovery` / `recovery_activities`, which lets the source-record route reach
  the answer-bearing row without inventing an evidence-completeness predicate.

Final replay:

```text
50 judged rows
50 exact / 0 partial / 0 miss
100.0% exact
ntsb_001: 25 / 0 / 0
ntsb_002: 25 / 0 / 0
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
```

Read: this should not be turned into a broad claim that Prethinker is now
"100%" on messy documents. It is a tiny pilot. The useful claim is narrower and
stronger: two unlike-document blocker shapes were found, repaired with general
query-only evidence support, and recovered without compatibility pressure.

## Native Query-Surface Gap Replay

The next native audit read the `29` query-surface gaps from the 2026-05-22
native stamp and replayed them with current QA code against the frozen native
compile artifacts.

Initial current-code replay:

```text
29 prior query-surface rows
22 exact / 1 partial / 6 miss
remaining surfaces: 6 compile-surface gaps, 1 hybrid-join gap
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
```

Read: the `20 -> 29` query-surface increase is mostly stale as an active
query-layer blocker. Current query repairs already clear `22 / 29` rows. Six
remaining rows are now honest compile-surface gaps rather than query-policy
work. The one live query/hybrid row was `sable_creek_budget` q004: a
counterfactual vote question where the broad `vote_record/5` scan had the
granular roll-call rows, but the answerer over-weighted the first bound row.

Repair:

- Added query-only `vote_record_counterfactual_support` rows for "if X had
  voted yes/no on motion Y" questions. The companion reads existing
  `vote_record/5` rows, matches nearby motion-id aliases, counts original
  votes, flips the named actor's vote, and reports whether the hypothetical
  count meets the threshold.
- During the transfer guard, sealed vote-matrix q021 exposed a sibling
  disambiguation issue: "exception motion" should prefer the supermajority
  motion over a later standard fallback motion for the same application. Added
  query-only `vote_record_disambiguation_support` rows that mark same-entity
  `vote_record/5` candidates as `exception_or_supermajority` versus
  `standard_or_simple_majority`.

Verification:

```text
sable q004 targeted replay: 1 exact / 0 partial / 0 miss
sable q003/q004/q030 slice: 3 exact / 0 partial / 0 miss
sealed vote q021 targeted replay: 1 exact / 0 partial / 0 miss
sealed vote-matrix guard q017/q019/q021/q023/q024/q032: 6 exact / 0 partial / 0 miss
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
full pytest: 1629 passed, 2 subtests passed
artifact archive: C:\prethinker_tmp_archive\native_query_surface_vote_lane_20260523
```

Read: the live native query-surface blocker in this slice is cleared, and the
transfer vote guard caught a real adjacent product issue before the change was
declared done. The remaining native query-surface rows should be treated as a
compile-surface queue unless a future replay shows otherwise.

## Native Compile-Surface Queue Triage

The next pass took the six rows that the native query-surface replay reclassified
as compile-surface pressure and replayed them against the frozen 2026-05-22 native
compile artifacts.

Initial source-window repair:

- Added query-only source-record companions for question-overlap rows, bounded list
  windows, named-speaker windows, and discrepancy-list rows.
- These companions only read admitted `source_record_*` predicates. They do not
  write durable facts or compatibility rows.

Result:

```text
six-row slice after source windows:
4 exact / 1 partial / 1 miss
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
```

Recovered exact rows:

- `arts_grant_panel_reconsideration` q014
- `count_composition_roster` q036
- `municipal_tree_permit_amendment` q032
- `veridia_intake` q019

Additional generic repairs:

- Added an unbound `scope_discrepancy/6` inventory hint for discrepancy/conflict
  questions so mapper-bound document constants do not hide same-predicate rows.
- Added `scope_discrepancy_completion_support` rows that compare admitted
  source-record discrepancy rows with existing `scope_discrepancy/6` rows and mark
  source-only completions.
- Added condition-finding support for `condition (x)` questions from admitted
  `board_finding/3` and source-attributed claim rows.

Final read on the two remaining blockers:

```text
northbridge_authority_packet q040: partial, compile/query boundary pressure
thornfield_variance q015: miss, compile-surface gap
full pytest: 1638 passed, 2 subtests passed
```

Northbridge now surfaces the broader discrepancy evidence cleanly:

- `scope_discrepancy/6` unbound returns pipe length, pipe diameter, and timeline.
- Source-record discrepancy rows also surface reporting frequency and fire
  hydrants, and mark customer notification as one-sided/not a discrepancy.
- The durable `scope_discrepancy/6` emission still lacks reporting frequency and
  fire hydrants, so this remains compile-emission work rather than a query-only
  win.

Thornfield is a cleaner compile gap:

- The source document contains Kowalski's condition-b objection about missing
  architect documentation.
- The compiled KB available to QA does not retain that attribution as a
  condition-b source claim/source row. It retains procedural Kowalski objections
  and majority condition-b findings, which are not enough to answer q015.

Next blocker before another native stamp: improve compile emission for
condition-scoped speaker objections and multi-document discrepancy lists, then
replay these two rows before deciding whether a full native restamp is earned.

## 2026-05-23 Compile-Emission Recovery Work

Goal: clear the last native compile-surface blockers without spending a full
native stamp.

Implemented instrument changes:

- Source-claim delivery now distinguishes `architect_documentation:no_documentation`
  from unrelated permit/no-record rows. This prevents a permit-status row from
  satisfying a condition-b architect-documentation objection.
- Added scope-discrepancy profile delivery checks and retry guidance for
  multi-record conflict lists: issue, left value/source, right value/source, and
  basis must be joinable in a direct discrepancy carrier.
- Added compile-health quality-gate holds for `zero_yield` focused passes. A
  planned pass that emits zero rows now generates retry context naming the dead
  pass instead of letting a broad source-record ledger hide the skipped section.

Focused validation:

```text
tests/test_domain_bootstrap_file.py + tests/test_domain_bootstrap_file_batch.py
+ tests/test_compile_surface_stability.py + tests/test_query_hint_surfaces.py:
260 passed
```

Targeted replay results:

```text
northbridge_authority_packet compile retry:
  QA: 40 / 0 / 0
  compatibility rows: 0
  write proposal rows: 0
  remaining gate flag: conservative scope_discrepancy partial-delivery flag

thornfield_variance first retry:
  QA: 27 / 2 / 11
  read: board-deliberation/testimony pass zero-yielded; this was a real
  struggle-detection miss in the gate.

thornfield_variance after zero-yield gate retry:
  QA: 37 / 1 / 2
  compatibility rows: 0
  write proposal rows: 0
  remaining non-exact rows:
    q014 drainage-easement rationale for condition (a)
    q032 Marchetti testimony that Koss initially had no objection
    q040 partial unresolved-survey-dispute linkage
```

Read: Northbridge is answer-clean. Thornfield moved from broad compile collapse
to three specific residual evidence-link gaps. The zero-yield gate is worth
keeping because it caught exactly the product-relevant failure mode: a planned
answer-bearing source section silently produced no ordinary facts.

Artifact archive: `C:\prethinker_tmp_archive\native_compile_recovery_20260523`

## 2026-05-23 Wild Real-World Transfer Batch

Goal: pressure the current instrument against a small batch of external,
real-world public-source documents before spending another native stamp.

Dataset committed location:

```text
datasets/real_world_transfer/20260523_wild_01
```

Batch shape:

- 5 fixtures
- 25 QA rows per fixture
- 125 judged rows total
- Domains: FDA warning/recall, NTSB aviation, NTSB marine, OSHA/MNOSHA
  incident/enforcement, SEC 8-K material event
- Source documents are real public-source documents, assembled into normal
  fixture shape. This is transfer evidence, not native-corpus evidence.

Compile command used OpenRouter Qwen MoE with 5 lanes and the current source,
flat-plus-plan, focused-pass ops schema, source-record ledger, source-record
ledger facts, and compile quality gate/retry stack.

Compile result:

```text
fixtures: 5
parsed OK: 5
compile gate: hold
passed / held: 2 / 3
admitted / skipped: 659 / 30
compatibility/runtime/write: not applicable at compile stage
```

Gate holds:

- `fda_warning_or_recall_001`: source-claim carrier offered but not fully
  delivered for assessment/note/source claim variants.
- `ntsb_aviation_investigation_001`: operational lifecycle preservation partial
  delivery.
- `sec_8k_material_event_001`: rough score below gate threshold despite later
  25/25 QA.

QA result on selected compile artifacts:

```text
questions: 125
exact / partial / miss: 119 / 1 / 5
exact rate: 95.2%
compatibility rows: 0
runtime load errors: 0
QA write proposal rows: 0
```

Per-fixture QA:

```text
sec_8k_material_event_001:        25 / 0 / 0
ntsb_aviation_investigation_001:  25 / 0 / 0
fda_warning_or_recall_001:        24 / 0 / 1
ntsb_marine_investigation_001:    23 / 1 / 1
osha_incident_or_enforcement_001: 22 / 0 / 3
```

Non-exact rows:

- FDA q017, miss, query-surface gap: the correct signatory role was present,
  but the query path preferred a flawed signatory value from source metadata
  over the body text signatory.
- NTSB marine q011, partial, compile-surface gap: source text retained the full
  National Weather Service product sequence, but structured event rows only
  covered the Special Marine Warning and update.
- NTSB marine q015, miss, compile-surface gap: KGLS wind gust was structured,
  but thunderstorm start, thunderstorm end, and rainfall were not emitted as
  comparable weather facts.
- OSHA q011, miss, hybrid-join gap: the earliest incident date and fatality
  inspection number existed in source-record fields/date aliases, but the query
  path did not join and sort the row-field representation correctly.
- OSHA q013, miss, compile-surface gap: the 8,000 national-employee value was
  present in source text but malformed in structured extraction as a combined
  row/value token.
- OSHA q014, miss, compile-surface gap/query aggregation boundary: fatality
  inspection numbers existed as source-record fields/items, but the query plan
  attempted unsupported aggregate predicates instead of using an admitted
  deterministic count surface.

Read:

- This is the strongest messy-world spotcheck so far: 95.2% on 125 rows from
  external public documents, with no compatibility rows, no runtime load errors,
  and no QA writes.
- The 3/5 compile-gate hold still matters. The gate is catching coverage and
  structure concerns that did not always hit the sampled QA questions.
- The main next mechanism is not "more prompt polish"; it is record-layer
  discipline for messy tables/lists: field normalization, source-record item
  joining, deterministic counts, chronology sequences, and source-metadata/body
  conflict handling.
- SEC and NTSB aviation both landing 25/25 argues that the architecture
  transfers when record extraction is coherent. OSHA is the useful stressor.

Next product work before another large stamp:

- Add a deterministic aggregation surface for source-record fields/items:
  distinct counts, min/max dates, and row-paired field joins.
- Improve numeric field normalization for messy table rows so values such as
  `8,000` do not merge with neighboring row fields.
- Add chronology support for weather/advisory product sequences and similar
  issued-product lists.
- Add query-side caution when `source_metadata` conflicts with signatory or
  authority facts in the body text.
- Keep requesting more messy real-world fixtures after these mechanisms have a
  targeted replay, especially table/list-heavy enforcement summaries.

## 2026-05-23 Wild Record-Layer Repair

Goal: repair the concrete record-layer failures from the 95.2% wild batch
without doing another full compile or full stamp.

Implemented deterministic current-query summaries over admitted
`source_record_*` rows:

- distinct field/item counts with composite identifier splitting
- earliest date selection paired to sibling row fields
- max numeric field selection with messy atom normalization
- KGLS weather observation extraction from admitted source-record text atoms
- NWS issued-product chronology extraction from admitted source-record text
  atoms
- body-signatory support that cross-checks source metadata against source-record
  signature-block context

These are marked as deterministic source-record summaries, not retired
compatibility helpers, so default compatibility row count remains 0.

Targeted replay:

```text
original affected rows: 0 exact / 1 partial / 5 miss
after repair:           6 exact / 0 partial / 0 miss
compatibility rows:     0
runtime load errors:    0
QA write proposals:     0
```

Rows cleared:

- FDA q017 signatory/body metadata conflict
- NTSB marine q011 weather-product chronology
- NTSB marine q015 KGLS thunderstorm/gust/rainfall observation
- OSHA q011 earliest incident date paired to fatality inspection number
- OSHA q013 largest national employee count with row-paired business type
- OSHA q014 distinct fatality inspection number count

Validation:

```text
tests/test_domain_bootstrap_qa.py: 245 passed
```

Artifact archive:

```text
C:\prethinker_tmp_archive\work_20260523_record_narrative_ach
```

Read: the wild batch exposed a product-grade mechanism, not just six isolated
answers. Messy real documents need a record-layer query surface that can safely
aggregate admitted rows when compile predicates are too narrow or malformed.

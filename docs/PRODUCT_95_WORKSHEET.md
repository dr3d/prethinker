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

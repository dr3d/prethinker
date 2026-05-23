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

## Next Moves

1. Run a focused real-world row replay for the approximate-time miss against the
   current selected compile to see whether the new QA companion is enough, or
   whether a recompile is needed to produce a direct event-time carrier.
2. If the row still misses, run a compile-only probe on the same real-world
   document and check whether profile delivery now admits a direct event-time
   row.
3. Re-run the small rejected-filter replay set if we want a variance check on
   the bounded source-text fallback.
4. Move to hybrid-join partials after the event/date/time source carrier is
   scoped.

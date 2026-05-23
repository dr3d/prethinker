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

all probes:
0 compatibility rows
0 runtime load errors
0 QA write proposal rows
```

Interpretation:

The repair appears to recover more than one brittle row, including one miss and
two partials, but this is still a row-targeted sample. It justifies a slightly
larger replay set over the same rejected-filter signature before any full stamp.

## Next Moves

1. Build a slightly larger row-targeted replay set from non-exact rows that had
   rejected `memberchk`/contains filter evidence-bundle queries.
2. Rerun that set against the frozen native compile artifact.
3. If the replay improves without compatibility pressure, run the real-world
   and sealed-unseen fixture batches as transfer guards.
4. Move to hybrid-join partials only after the query-surface repair is bounded.

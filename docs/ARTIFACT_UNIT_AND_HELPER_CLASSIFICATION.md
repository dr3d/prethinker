# Artifact Unit And Helper Classification

Last updated: 2026-05-10

This note fixes a boundary that became visible during the May 2026 transfer
fixture work: helpers are not invisible plumbing. They are part of the
instrument's epistemic surface.

The current helper audit lives in `docs/HELPER_LEDGER.md`.

## Artifact Unit

The evaluated Prethinker artifact is:

```text
source + lens set + deterministic ledgers + admitted predicates + helper set
```

Reporting any one of these in isolation understates what was measured. A score
does not describe "the model" or even "the compiled KB" alone. It describes the
whole artifact package active for that run.

| Piece | What It Contributes |
| --- | --- |
| `source` | The document or utterance being compiled. |
| `lens set` | The compile-time reading strategies that proposed semantic surfaces. |
| `deterministic ledgers` | Pre-compile lexical and structural addressability: lines, sections, table rows, fields, exact identifiers, and text atoms. |
| `admitted predicates` | Durable governed state accepted by the mapper. |
| `helper set` | Query-time computation, joins, formatting, and support surfaces available when answering. |

Two runs over the same source can produce different answerable surfaces if they
use different lens sets, ledgers, admitted predicate contracts, or helper sets.
Those differences must be named in research reports.

## Helper Classes

Helpers are query-only. They do not mutate the KB and do not admit new truth.
But they can change what is retrievable from admitted state, so they must be
classified and reported.

| Class | Definition | Governance |
| --- | --- | --- |
| Generic helper | Operates over broad substrate such as `source_record_field/3`, `source_record_text_atom/2`, dates, intervals, counts, identifiers, or admitted predicate joins. | Architectural; available across lenses when its input predicates exist. |
| Lens companion | Tied to a declared lens contract or predicate family. | Acceptable when explicitly packaged with that lens and reported with the artifact. |
| Candidate scar | Born from a fixture, miss cluster, or one-batch repair. | Quarantined until rewritten generically or transfer-proven on fresh sibling fixtures. |
| Transfer-proven helper | A former candidate that succeeds on fresh fixtures without adding new fixture constants. | Promotable, but still carries a retirement condition when better compile acquisition makes it unnecessary. |

## Leakage Test

A helper is legitimate when it performs a general operation over admitted KB
state, deterministic source-record rows, or generic identifier/time/count
formats.

A helper is suspicious when it knows a fixture's proper nouns, exact row payloads,
or oracle targets before it runs.

Examples of legitimate operations:

- count distinct entities by stable identifier
- compute intervals from admitted timestamps
- render normalized source-record atoms into exact display strings
- enumerate table rows with a requested identifier
- join custody, authority, access, and title predicates by item id
- expose adjacent source-record lines for a query constant

Examples of suspicious operations:

- hard-code a fixture item such as `ex_010`
- hard-code a person, organization, or document id unique to one fixture
- return a prose answer that was copied from a reference answer rather than
  derived from admitted rows
- trigger only on the fixture's signature names

Suspicious helpers are useful as probes, but not as promoted architecture.

## Promotion Path

Candidate helpers move through the same kind of discipline as selector guards:

```text
candidate scar
  -> generic rewrite or declared lens companion
  -> targeted replay on the origin fixture
  -> full replay/no-regression on the origin fixture
  -> transfer replay on sibling fixtures
  -> promotion or retirement
```

The promotion question is not "did it rescue rows?" The question is:

```text
What general operation did this helper add to the instrument?
Did that operation transfer without fixture-specific constants?
What upstream compile or ledger improvement would retire it?
```

## Reporting Labels

Use these labels in journals and score reports:

| Label | Meaning |
| --- | --- |
| `cold` | Stable compiler plus stable helper library only. |
| `candidate-helper` | Uses a helper with fixture-family constants or unproven transfer behavior. |
| `transfer-proven-helper` | Uses a helper that passed sibling-fixture replay without new fixture constants. |
| `clean-helper` | Uses a generic helper over predicates, ledgers, identifiers, dates, intervals, or counts. |

Recent saturated results that used newly written helper bridges should be
described with the `candidate-helper` label until the helper audit and transfer
proof are complete.

## Current Audit Snapshot

This is a working classification, not a final ledger.

| Helper Surface | Current Status | Notes |
| --- | --- | --- |
| `source_record_section_display` | Clean helper | Renders admitted section atoms; no fixture answer knowledge. |
| `source_record_clock_sync_support` | Clean helper | Deterministically extracts last-successful clock-sync dates from admitted source-record text/numeric rows. |
| `clear_sample_clock_pause_support` | Clean helper | Joins admitted segments and offline intervals. |
| temporal and negative join helpers | Clean helper | Query-composition substrate over prior query results. |
| authority/custody support | Split, audit ongoing | Generic `object_custody_status/5`, access-log, authorization, and recall-right joins are labeled `clean-helper`; older Pellico/Stille/Halberd family count, source-cell, contractor-notice, and text fallback recognizers are labeled `candidate-helper`. |
| roster state support | Split, audit ongoing | Admitted-predicate joins for adult roles, supervision, memberships, and group counts are labeled `clean-helper`; source-record roster parsing over school-roster shapes remains `candidate-helper`. A first deterministic roster-table ledger emits `roster_table_member/4` for explicit table rows with both grouping and member columns, which lets that narrow surface be consumed as clean structural memory. Section/prose-derived roster membership remains candidate-helper. |
| grant award support | Clean helper on transfer batch | Award, cap, eligibility, field-driven recusal, appeal-window, committee-recusal vote-count, score-correction operational status, and appeal-pending status rows are labeled `clean-helper` on the current transfer batch; sibling transfer proof is still pending. |
| industrial sensor support | Split, audit ongoing | Field-driven event/timestamp/count, computed-duration, packet-id, data-loss, lab-sample logistics, and system clock-authority rows are labeled `clean-helper`; root-cause refusal and operator-origin rows become `clean-helper` when refreshed source-record artifacts preserve the necessary prose. Stated-duration exact-prose recognizers were retired as duplicate/overclaiming scar rows. |
| clinic recall support | Split, audit ongoing | Device/serial rows plus generic manufacturer-liaison, verification-procedure, explicit clinic abbreviations, cabinet/seal range, failure-rate atoms, visit-date ranges, key-retainer identity, and named medical-director authority are labeled `clean-helper` when acquired by refreshed source-record ledgers; stale artifacts keep sender-dependent rows candidate-labeled. |
| source-record packet metadata | Split, audit ongoing | Generic identifier/metadata rows are labeled `clean-helper`; embedded school/grant packet facts are now labeled `candidate-helper` in the emitted rows. |
| probate storage support | Orphaned artifact helper | Appears in historical probate QA artifacts, but no current companion implementation is registered in the repo. Treat those historical rows as candidate-helper archaeology, not active architecture. |

## Doctrine

Helpers are part of the instrument. A helper set can make durable state more
retrievable without changing what the KB believes. That is powerful, but it must
be visible.

The honest unit of evaluation is the whole artifact package:

```text
source + lens set + deterministic ledgers + admitted predicates + helper set
```

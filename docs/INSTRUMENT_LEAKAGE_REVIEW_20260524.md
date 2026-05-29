# Instrument Leakage Review

Date: 2026-05-24

Purpose:

Answer the risk question directly: how much have research fixtures, native
corpus shapes, and fresh-ugly public documents worked themselves into the
instrument?

## Short Read

The instrument does not appear to be driven by dataset folder names, row IDs, or
native fixture names in the active compile/QA path. I did not find active core
logic branching on names such as `fresh_ugly`, native story fixture names,
Sherlock probe names, or Batch 01 fixture IDs.

There is real shape memory in the instrument. It mostly appears as:

- domain/document-class prompt priors in the compiler;
- deterministic query-only summaries over admitted `source_record_*` rows;
- public-record identifier and section/citation normalizers;
- tests and worksheets preserving examples from the corpora.

That is not the same as answer-key leakage, but it is a product risk. The danger
is that recurring research document shapes become substrate before they have
transfer evidence on unlike documents.

## Terminology Correction

The project previously retired helper companions by default. That retirement
was about compatibility-rescue delivery, not every query-time support surface.

Current categories:

| Category | Forward status | Meaning |
| --- | --- | --- |
| Retired compatibility adapter | Off by default; forensic only | Old query-time rescue path. Rows count as compatibility pressure. |
| Current deterministic support surface | Allowed but monitored | Query-only derived table over admitted facts/source-record rows. Writes no durable facts. |
| Current source-record summary | Allowed but high scrutiny | Deterministic support surface over `source_record_*` rows. Useful for messy public docs, but closest to document-shape memory. |
| Direct compile surface | Preferred | Ordinary admitted predicate/fact that preserves the answer-bearing slots directly. |
| Fixture-shaped support | Forbidden | Any branch or predicate that relies on dataset names, row IDs, answer words, local story nouns, or one document's accidental constants. |

The comparison tool now reports added `support` surfaces and their classes while
preserving legacy `helper` keys for old artifacts.

## Timeline

`b18d618e Retire helper companion delivery by default` changed the normal QA
path so retired query-helper companions were not assembled unless explicitly
enabled. It did not delete all `_support` code.

Later messy-document work added deterministic source-record summaries:

- `fae3bee8 Repair wild record layer and add ACH probe`
- `1eaae40a Harden source-record summaries for wild QA`
- `4e6a0764 Harden known-wild chronology and source summaries`

Batch 01 then added more source-record summaries:

- `source_record_identifier_set_support`
- `source_record_date_pair_duration_support`
- `source_record_field_state_support`
- `source_record_citation_list_support`
- `source_record_contact_signatory_support`
- `source_record_date_range_duration_support`
- `source_record_same_day_event_time_support`

Those were added because messy public documents carried answer-bearing evidence
in source-record ledger rows when direct compile predicates were too narrow or
missing. They kept compatibility rows at `0`, but they reintroduced a
helper-shaped support layer under a different discipline.

## Current Code Exposure

Broad scan of active core scripts:

- `scripts/run_domain_bootstrap_qa.py`: no active branches on dataset/folder
  names found; many source-record support surfaces; several domain-specific
  public-document normalizers.
- `scripts/run_domain_bootstrap_file.py`: compiler prompt contexts contain
  domain-shape priors for operational records, policy incidents, probate,
  competition, permits, quarantine/lab/greenhouse records, custody, and similar
  recurring document classes.
- `scripts/run_domain_bootstrap_file_batch.py`: mostly batch/gate mechanics;
  no meaningful fixture-content leakage found beyond generic fixture handling.
- `src/`: no obvious fresh-ugly/native fixture constants found in the main
  runtime path; domain names such as `sec_contracts@v0` are profile names.

## Concerning Spots

These are not proof of corruption, but they deserve scrutiny.

1. Public-document constants in QA support:

- `MARCS-CMS`, `FEI`, FDA warning-letter identifiers;
- CFR/CGMP citation-list parsing;
- `KGLS` weather observation extraction;
- `NWS` issued-product chronology extraction;
- MNOSHA field names such as `outcome_of_mnosha_investigation`;
- an NTSB ATC not-formed-group summary.

Most are document-class terms, not answer keys. Still, they are closer to the
fixture corpus than I want the forward product instrument to be.

2. Compiler prompt priors shaped by research fixtures:

The compiler now has rich instructions for operational lifecycle records,
quarantine/greenhouse/lab results, permits, custody, probate, competition,
policy incidents, and public-document style source fidelity. These are framed
generically, but they reflect the sequence of corpora used to train the
instrument's behavior.

3. Source-record summaries bypass the retired helper flag:

The retired compatibility adapters are still off by default, but current
source-record summaries run on the clean path. That is why compatibility rows
stay at `0` while support surfaces can still affect answers. This is technically
cleaner than retired helpers, but it must be monitored as a first-class support
layer, not hidden under the word "no-helper".

## Not Found

In the active compile/QA scripts, I did not find:

- branches on `fresh_ugly_public_20260524_01`;
- branches on Batch 01 fixture IDs;
- branches on specific native fixture names;
- direct use of QA row IDs as behavior switches;
- use of oracle/reference answers by support surfaces.

Tests and docs contain many fixture names and answer strings. That is expected
for validation and history, but those should not be imported into active
instrument prompts or runtime decisions.

## Honest Risk Assessment

Current risk: medium.

I do not see direct answer-key leakage or obvious fixture-name branching in the
instrument. The stronger risk is subtler: document shapes from the research
thermometers have become operational priors and query-only summaries. That can
be good product learning if it transfers. It becomes benchmark overfitting if
new support surfaces are justified only by the same corpus rows that created
them.

The most exposed area is the source-record summary layer. It is useful because
real public documents are messy; it is dangerous because it can become a
parallel semantic compiler built out of row-shape recognizers.

## Controls To Add

1. Support-surface registry:

Every `_support`/`_companion` surface should be classified as retired
compatibility, current deterministic summary, source-record summary, direct
compile adjunct, or forbidden fixture-shaped support.

2. Fixture-vocabulary audit for active code:

Run an explicit audit against active scripts for dataset names, fixture IDs,
native story nouns, QA row IDs, and answer phrases. Keep tests/docs separate
from runtime code in the report.

3. Transfer requirement:

Any source-record summary added from one corpus must either:

- pass on an unlike fixture/document class; or
- be marked document-class-specific with a narrow product rationale and a
  retirement path toward direct compile surfaces.

4. Regression guard:

Any new support surface must be checked against previously exact rows. Report
added support surfaces by class, not as a generic "helper" count.

5. Prefer compile promotion:

If a source-record summary proves useful across documents, promote the
answer-bearing structure into direct compile surfaces and retire the summary
where possible.

## Current Decision

Do not rip out the current source-record summaries before Batch 02. They are
part of the R4 instrument being tested. But treat Batch 02 as the thermometer:
if the same surfaces transfer cleanly, they are product learning; if they mostly
serve Batch 01 shapes, they are research-corpus memory and should be retired or
converted into stricter direct compile surfaces.

## Same-Day Adjudication

Follow-up work added three adjudication instruments:

- source-record-summary ablation switches in the QA runner:
  `--disable-current-source-record-summaries` and
  `--disable-support-predicate`;
- an active-code leakage audit:
  `scripts/audit_active_instrument_leakage.py`;
- metamorphic unit tests for two previously over-literal summaries.

Static audit result:

```text
artifact archive:
  C:\prethinker_tmp_archive\support_surface_ablation_20260524

status:
  pass
active files scanned:
  23
forbidden hits:
  0
warnings:
  10
```

The warnings are document-class terms in active code: `MARCS`, `CMS`, `FEI`,
`CFR`, and the `SEC` profile/router label. They are not fixture names or answer
phrases, but they should stay visible as document-class priors.

Metamorphic fixes:

- Weather observation support no longer keys on `KGLS`; a test with synthetic
  station code `KABC` now exercises the same structure.
- Group-formation exception support no longer hardcodes the NTSB ATC group; a
  test with a synthetic `hazmat_group` and `hazardous_materials_specialist` now
  exercises the same structure.

Batch 01 ablation over fixed R3 compiles:

```text
baseline R4 with current source-record summaries:
  193 / 3 / 4 = 96.5%

R4 with --disable-current-source-record-summaries:
  187 / 4 / 9 = 93.5%

delta:
  -6 exact, +1 partial, +5 miss

hygiene:
  runtime load errors: 0
  write proposal rows: 0
  compatibility rows: 0
```

Row movement versus R4:

```text
changed rows: 15
improved rows under ablation: 4
regressed rows under ablation: 11
baseline exact -> non-exact under ablation: 10
baseline exact -> miss under ablation: 7
```

Read:

The source-record summary layer is materially load-bearing on Batch 01. It is
worth roughly six exact rows on this corpus, and several of those rows become
compile-surface gaps when the layer is removed. That means the layer is not
cosmetic and should not be described as absent. It is a clean query-only support
layer with zero compatibility pressure, but it is also carrying product answers
that direct compile surfaces do not yet carry.

This sharpens the Batch 02 question. If Batch 02 holds near the R4 level, the
source-record summaries are likely product learning over messy documents. If it
falls back toward the ablated level or shows class-specific failures, those
summaries should be treated as Batch 01 shape memory and promoted into stricter
compile surfaces or retired.

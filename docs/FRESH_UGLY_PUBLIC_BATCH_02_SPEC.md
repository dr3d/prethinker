# Fresh Ugly Public Batch 02 Collection Spec

Date: 2026-05-24

Purpose:

Collect a second fresh public-document transfer batch that tests whether the
R4 mechanisms from `fresh_ugly_public_20260524_01` generalize outside the
documents they were repaired against. This batch should not be optimized for a
high score. It should pressure messy, product-relevant public documents with
tables, redactions, nested headings, chronology, repeated numeric values,
signatures, identifiers, and multi-step elapsed-time or set/list questions.

Do not inspect Prethinker internals, prior QA outputs, run artifacts, worksheets,
or source code while authoring the batch. Use only the public source documents
and the instructions below.

## Deliverable

Create one zip file named:

`fresh_ugly_public_20260524_02.zip`

Inside the zip, include exactly one top-level directory:

`fresh_ugly_public_20260524_02/`

That directory must contain 12 document folders:

```text
fda_warning_ugly_003/
fda_warning_ugly_004/
fda_warning_ugly_005/
ntsb_aviation_ugly_002/
ntsb_marine_ugly_002/
ntsb_surface_ugly_001/
osha_incident_ugly_003/
osha_incident_ugly_004/
osha_incident_ugly_005/
sec_material_event_ugly_003/
sec_material_event_ugly_004/
sec_material_event_ugly_005/
```

Each folder must contain:

```text
source.md
source_original.txt
qa.md
qa_questions.jsonl
oracle.jsonl
metadata.json
provenance.md
fixture_notes.md
anti_leakage_manifest.md
qa_authored_with_answers.md
```

`qa.md` must contain questions only. Answers belong only in `oracle.jsonl` and
`qa_authored_with_answers.md`.

## Source Selection Rules

Use real public documents from official sources only:

- FDA: `fda.gov`
- NTSB: `ntsb.gov`
- OSHA: `osha.gov`
- SEC: `sec.gov` or official SEC filing pages

Do not use any document already present in earlier Prethinker batches. Do not
use LLM-authored or synthetic documents. Do not use summaries, press releases,
or secondary commentary when an official source document is available.

Prefer documents that are messy but parseable:

- redactions such as `(b)(4)` or FOIA-style omissions
- tables with repeated values or blank cells
- section headings, sub-headings, and nested numbered findings
- signature blocks, contact lines, FEI/inspection/case/accession identifiers
- event chronologies with dates and times in more than one section
- source text where the correct answer is present but requires joining nearby
  rows, not outside knowledge

Avoid documents whose answers require external expertise, private records, or
facts outside the selected source document.

## Per-Document QA Requirements

Create 25 QA rows per document, for 300 total rows.

Use IDs `q001` through `q025` in both `qa_questions.jsonl` and `oracle.jsonl`.

Question mix per document:

```text
5 direct metadata / identifier / party / address / title questions
5 date, time, chronology, deadline, or elapsed-duration questions
5 table, list, nested-heading, citation, or repeated-value questions
5 source-state, exception, absence, response-status, or qualification questions
5 harder join/comparison questions that require combining two or more source rows
```

Reference answers must be concise but complete. Include enough detail to judge
exactness. If the answer is not present in the source document, do not ask the
question.

For arithmetic questions, include the arithmetic in the reference answer, for
example: `1657 to 1808 is 71 minutes`.

For list questions, preserve source order when the question asks for order.

For absence or negative questions, cite the document basis in the answer, for
example: `No. The only response described is an extension request, and the
letter says no further correspondence had been received.`

## Domain-Specific Pressure Targets

### FDA Warning Letters

Choose three FDA warning letters that contain at least four of these:

- multiple numbered violations or observations
- CFR citations with section/subpart detail
- nested sub-headings under one violation
- firm response chronology, including extension requests or inadequate response
- signature block with named official and title
- reply/contact email, ATTN line, FEI number, CMS/MARCS number
- redacted product/process/lot details

QA must include:

- one ordered citation-list question
- one nested-heading or sub-section question
- one question about whether a response was substantive, adequate, absent, or
  only an extension/request
- one chronology question spanning inspection dates, response dates, and letter
  date
- one signatory/contact/identifier question

### NTSB Reports

Choose:

- one aviation accident report
- one marine accident report
- one surface transportation report: highway, rail, pipeline, or hazmat

Prefer final reports with factual chronology, probable cause, injuries/fatalities,
weather/mechanical/operator factors, and at least one table or similar-events
section.

QA must include:

- one event-sequence question with date and time anchors
- one elapsed-time question between two clock events
- one fatality/injury count comparison question, preferably involving a similar
  event or prior accident if present
- one question distinguishing probable cause from contributing factors
- one question that requires joining narrative text with a table or appendix

### OSHA Incident Reports

Choose three OSHA accident/incident documents with inspection metadata and
employee/accident detail tables.

Prefer documents that contain:

- inspection open/close/citation dates
- close conference date
- employer/site metadata
- accident narrative plus structured employee fields
- repeated numeric values across narrative/table fields
- violation/citation/penalty rows where available

QA must include:

- one close-conference vs citation-issued date question
- one repeated numeric value question, naming where each value appears
- one question joining accident narrative with employee detail rows
- one question about inspection/case identifiers
- one chronology question spanning incident, inspection, close conference, and
  citation dates when those are present

### SEC Material Event Filings

Choose three SEC 8-K or 8-K/A filings with exhibits or detailed event text.

Prefer filings involving:

- executive appointment/resignation with effective dates and prior role dates
- agreement amendments with from/to date changes
- merger/acquisition/financing event chronology
- exhibits whose date differs from report/signature dates
- multiple parties, titles, committees, or board actions

QA must include:

- one report-date vs signature-date vs event-date chronology question
- one role-start to appointment/effective-date duration question if available
- one amendment from/to date or deadline-extension question if available
- one question that distinguishes a filed exhibit date from the 8-K filing date
- one party/title/signatory question

## File Format Details

### `source.md`

Markdown rendering of the source document. Preserve the document's actual
structure as much as possible:

- headings and subheadings
- numbered lists
- tables
- signature blocks
- redactions
- identifiers
- footnotes

Remove website navigation, cookie banners, unrelated footer links, and site
chrome. Do not add answer hints or QA-specific labels.

### `source_original.txt`

Plain-text capture of the original source text before Markdown cleanup. It can
include rough extraction artifacts, but it should not include website chrome
unless unavoidable. If the source is a PDF, extract the PDF text here and note
the extraction method in `provenance.md`.

### `qa.md`

Questions only, numbered 1 through 25:

```text
# fda_warning_ugly_003 QA

Questions only. Reference answers are isolated in `oracle.jsonl`.

1. ...
2. ...
```

### `qa_questions.jsonl`

One JSON object per line:

```jsonl
{"id":"q001","question":"...?"}
{"id":"q002","question":"...?"}
```

### `oracle.jsonl`

One JSON object per line:

```jsonl
{"id":"q001","reference_answer":"..."}
{"id":"q002","reference_answer":"..."}
```

### `qa_authored_with_answers.md`

Human-readable QA with answers. This is scoring-only material and must not be
used as compile or answer context.

### `metadata.json`

Use this shape:

```json
{
  "fixture_id": "fda_warning_ugly_003",
  "batch": "fresh_ugly_public_20260524_02",
  "source_domain": "FDA",
  "document_title": "...",
  "document_date": "YYYY-MM-DD or unknown",
  "retrieved_at": "2026-05-24",
  "source_url": "https://...",
  "source_type": "official_public_document",
  "document_format_original": "html or pdf or txt",
  "notes": "One short paragraph describing why this document is useful."
}
```

### `provenance.md`

Include:

- source URL
- retrieval date
- original format
- extraction/transformation steps
- excerpt boundaries: full document or named excerpt
- any caveats, such as redactions, missing tables, OCR artifacts, or removed site
  chrome

### `fixture_notes.md`

Briefly state what this document pressures. Use plain language. Example:

```text
This document pressures nested violation headings, ordered CFR citation lists,
inspection/response chronology, redacted product details, and signatory/contact
lines.
```

### `anti_leakage_manifest.md`

Include:

```text
# Anti-leakage manifest - <fixture_id>

- The collector did not inspect Prethinker internals, repository contents, prior
  QA outputs, run artifacts, or evaluation harness while preparing this document.
- The selected source document is not from any prior Prethinker batch.
- All QA pairs were written from the public source document only.
- No outside knowledge, AI summary, or inference beyond what is explicitly
  recoverable from `source.md` was used for the reference answers.
- No QA hints, answer keys, or evaluation labels were embedded into `source.md`.
- `qa.md` is questions-only. `oracle.jsonl` and `qa_authored_with_answers.md`
  are scoring-only and must not be used as compile or answer context.
```

## Quality Checks Before Zipping

Before delivering the zip:

- Confirm every folder has exactly 25 questions and 25 oracle rows.
- Confirm every `qa_questions.jsonl` ID matches the corresponding `oracle.jsonl`
  ID.
- Confirm `qa.md` contains no answers.
- Confirm `source.md` contains no QA hints or answer-key language.
- Confirm all URLs are official public-source URLs.
- Confirm none of the 12 source documents duplicate prior Prethinker documents.
- Confirm the zip has one top-level directory, not loose files.

## Why This Batch Exists

Batch 01 R4 reached `193 / 3 / 4 = 96.5%` on a QA-over-existing-compile rerun,
but row churn remained visible: 16 changed rows, 9 improvements, 7 regressions,
and 5 prior exact rows becoming non-exact. Batch 02 should test whether the R4
mechanisms transfer to fresh public documents and whether the remaining weak
surfaces recur:

- nested FDA violation subheadings
- FDA response chronology and extension-vs-substantive-response distinctions
- NTSB elapsed time between narrative clock events
- NTSB similar-event fatality arithmetic
- OSHA close-conference and citation-issued date binding
- SEC approximate duration from role-start to appointment/effective date

The desired result is not an easy score. The desired result is a truthful product
thermometer for messy public documents.

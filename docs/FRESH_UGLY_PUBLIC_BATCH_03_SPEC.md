# Fresh Ugly Public Batch 03 Spec

Purpose: collect the next product thermometer batch. These documents should be
new to Prethinker, structurally messy, public, and not selected to resemble the
current native or Batch 02 rows.

## Target Shape

- 12 documents total.
- 3 FDA warning letters or enforcement letters.
- 3 OSHA accident, citation, or fatality packets.
- 3 SEC 8-K or proxy/event filings with dense attachments or tables.
- 3 non-NTSB public investigation or regulatory reports from another source
  such as EPA, FTC, CFPB, CPSC, state insurance regulators, or state health
  departments.

Prefer documents with:

- tables, lists, blanks, redactions, attachments, signatures, or addenda;
- multiple dates and deadlines;
- named entities with roles and aliases;
- obligations, violations, corrective actions, penalties, or consequences;
- source sections that require cross-reference, not just single-sentence lookup.

Avoid:

- documents already present anywhere under `datasets/`;
- documents used in Batch 01 or Batch 02;
- LLM-written or LLM-rewritten source text;
- documents chosen because they match a known failing row;
- artificial question wording that mirrors existing test language.

## Folder Layout

Create:

```text
datasets/real_world_transfer/fresh_ugly_public_20260524_03/
```

Each document gets one subfolder with a stable lowercase identifier:

```text
datasets/real_world_transfer/fresh_ugly_public_20260524_03/<source_family>_ugly_###/
```

Each subfolder must contain:

```text
source.md
qa.md
qa_authored_with_answers.md
fixture_notes.md
metadata.json
```

`source.md` should contain the extracted public text in markdown. Preserve
headings, tables, lists, redactions, signature blocks, attachments, and visible
line/order structure as much as practical. Do not simplify the prose.

`qa.md` should contain exactly 25 numbered questions and no answers.

`qa_authored_with_answers.md` should contain the same 25 questions plus reference
answers. Answers should cite the document section, paragraph, row, table, or
line where practical.

`fixture_notes.md` should explain:

- public source URL;
- collection date;
- why the document is messy;
- what shapes it pressures;
- any extraction caveats;
- whether the document has attachments, redactions, tables, or missing fields.

`metadata.json` should include:

```json
{
  "schema_version": "fresh_ugly_public_batch_v1",
  "batch_id": "fresh_ugly_public_20260524_03",
  "document_id": "<folder_name>",
  "source_family": "<fda|osha|sec|other>",
  "source_url": "<public URL>",
  "collected_utc": "<ISO timestamp>",
  "public_domain_or_public_record": true,
  "llm_authored_source": false,
  "llm_rewritten_source": false,
  "question_count": 25,
  "answer_count": 25,
  "pressure_tags": [
    "dates",
    "roles",
    "tables",
    "obligations",
    "source_sections"
  ]
}
```

## QA Pressure Mix

For each document, write 25 questions:

- 5 direct source facts.
- 5 source-coordinate or provenance questions.
- 5 list/table/identifier questions.
- 4 date, deadline, duration, or sequence questions.
- 3 obligation, violation, consequence, or corrective-action questions.
- 3 cross-section questions that require joining two separated parts of the
  document.

At least 5 questions per document should be answerable only by preserving source
shape, such as table rows, section headers, redaction markers, signature blocks,
or attachment references.

At least 3 questions per document should ask for qualified answers where the
correct response includes uncertainty, limitation, pending status, or absence of
evidence.

## Packaging

Package the completed folder as:

```text
fresh_ugly_public_20260524_03.zip
```

The zip should unpack directly to:

```text
fresh_ugly_public_20260524_03/<document folders...>
```

Do not include run artifacts, compiled KBs, model outputs, cache directories, or
temporary files in the zip.

## Acceptance Check

Before handing off, verify:

- every subfolder has the five required files;
- every `qa.md` has exactly 25 numbered questions;
- every `qa_authored_with_answers.md` has exactly 25 reference answers;
- every `metadata.json` parses as JSON;
- source URLs are public and reachable;
- no source text was generated or rewritten by an LLM.

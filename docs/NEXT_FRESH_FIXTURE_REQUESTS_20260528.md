# Next Fresh Fixture Requests

Date: 2026-05-28

These are cut-and-paste requests for external collection agents. They are meant
to keep Prethinker honest: fresh official documents, no source rewriting, no
inspection of Prethinker internals, and no tuning to known row failures.

## Request A - Fresh Ugly Public Batch 05

Copy/paste to the collecting agent:

```text
You are building a fresh heldout messy-public-document batch for Prethinker.
Do not inspect Prethinker source code, docs, worksheets, prior run artifacts,
or existing QA outputs. Use only the public source documents you collect and
the instructions below. The purpose is to test generalization on ugly English
official documents, not to produce an easy high score.

Create one zip file named:

fresh_ugly_public_20260528_01.zip

Inside the zip, include exactly one top-level folder:

fresh_ugly_public_20260528_01/

Inside that folder, create exactly 8 fixture folders:

court_order_ugly_002/
procurement_contract_ugly_002/
puc_order_ugly_002/
state_ag_settlement_ugly_002/
labor_board_ugly_002/
fda_warning_ugly_006/
osha_incident_ugly_006/
sec_material_event_ugly_006/

Each fixture folder must contain exactly these files:

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

Use real public English-language official documents only. Do not use synthetic
documents, LLM-authored documents, LLM-rewritten source text, secondary
summaries, press articles, blog posts, or documents already present in prior
Prethinker batches. It is fine to use an AI assistant to help extract text and
write questions, but the source text itself must be copied/extracted from the
public official document and preserved without simplification.

Source targets:

1. court_order_ugly_002
   Use a real public court order, administrative decision, consent order, or
   appellate/agency legal decision. Prefer nested findings, party roles,
   citations, footnotes, procedural history, multiple dates, and a clear order
   or disposition. Avoid famous cases likely to be memorized.

2. procurement_contract_ugly_002
   Use a public procurement award notice, solicitation addendum, contract award,
   bid protest decision, or government purchasing packet. Prefer line-item
   tables, awardee/vendor identifiers, solicitation numbers, effective dates,
   contract amounts, amendments, delivery terms, and signatory/authority text.

3. puc_order_ugly_002
   Use a public utility commission order, tariff order, rate-case order, docket
   order, or service-quality enforcement document. Prefer docket numbers,
   parties, settlement terms, tariffs, footnotes, commission vote/order clauses,
   deadlines, and appendices.

4. state_ag_settlement_ugly_002
   Use a state attorney general settlement, assurance of discontinuance,
   consent judgment, consumer-protection order, or enforcement press/settlement
   document with official terms. Prefer injunctive terms, restitution/penalty
   amounts, covered entities, deadlines, release/scope clauses, and reporting
   obligations.

5. labor_board_ugly_002
   Use an NLRB, state labor board, public employment relations board, or labor
   administrative decision. Prefer case numbers, citations, employer/union
   names, locations, charge numbers, procedural posture, remedies, and multiple
   consolidated cases.

6. fda_warning_ugly_006
   Use an FDA warning letter or enforcement letter. Prefer CFR citations,
   FEI/CMS/MARCS identifiers, nested observations, firm-response chronology,
   extension/adequacy language, redactions, signature blocks, and contact
   instructions.

7. osha_incident_ugly_006
   Use an OSHA accident/incident/citation record or official investigation
   report. Prefer inspection metadata, employer/site data, employee detail
   rows, close-conference/citation dates, accident narrative, violation/citation
   tables, and repeated numeric values.

8. sec_material_event_ugly_006
   Use a SEC 8-K, 8-K/A, proxy supplement, administrative order, or filing with
   exhibits. Prefer report dates vs event dates vs signature dates, amendments,
   executive roles, accession/file numbers, exhibit dates, committees, or
   material agreement terms.

Required pressure per document:

- 25 questions per fixture, exactly q001 through q025.
- At least 5 direct metadata/identifier/party questions.
- At least 5 date, deadline, sequence, or elapsed-duration questions.
- At least 5 table/list/citation/roster/source-coordinate questions.
- At least 4 source-state, exception, qualification, absence, or limitation
  questions.
- At least 4 cross-section questions requiring two separated source parts.
- At least 3 questions where the answer must preserve exact source wording,
  identifier spelling, citation string, row label, section heading, or redaction
  marker.

Do not write questions whose answers require outside knowledge. Do not write
questions designed around Prethinker fixture vocabulary. Do not reuse question
wording from previous batches if you know it.

File requirements:

source.md:
Markdown rendering of the source document. Preserve headings, tables, lists,
footnotes, redactions, signature blocks, docket/accession/inspection/case
identifiers, and visible ordering. Do not simplify the prose.

source_original.txt:
Raw or near-raw extracted source text. If the official source is HTML, include
the readable extracted text. If PDF, include OCR/text extraction as available.

qa.md:
Exactly 25 numbered questions, no answers.

qa_questions.jsonl:
Exactly 25 JSON Lines rows. Each row:
{"id":"q001","question":"..."}

oracle.jsonl:
Exactly 25 JSON Lines rows. Each row:
{"id":"q001","reference_answer":"..."}

qa_authored_with_answers.md:
The same 25 questions with reference answers. Each answer should include enough
source-local support to judge exactness, such as section, heading, table row,
paragraph, line label, or document coordinate.

metadata.json:
Valid JSON with this shape:
{
  "schema_version": "fresh_ugly_public_batch_v2",
  "batch_id": "fresh_ugly_public_20260528_01",
  "fixture_id": "<folder_name>",
  "source_family": "<court|procurement|puc|state_ag|labor|fda|osha|sec>",
  "source_title": "<official title>",
  "source_url": "<public official URL>",
  "source_date": "<YYYY-MM-DD or unknown>",
  "collected_at": "<YYYY-MM-DD>",
  "public_source": true,
  "language": "en",
  "llm_authored_source": false,
  "llm_rewritten_source": false,
  "question_count": 25,
  "pressure_tags": ["identifiers","dates","source_coordinates","tables","cross_section"]
}

provenance.md:
List source URL, collection date, extraction method, official-source status,
and any OCR/extraction caveats.

fixture_notes.md:
Explain why the document is messy, what structures it pressures, and any known
ambiguities in the source. Do not mention Prethinker internals or expected
system behavior.

anti_leakage_manifest.md:
State that the source was not LLM-authored or LLM-rewritten, no Prethinker
worksheets/docs/code/run artifacts were inspected, and questions were authored
only from the source document.

Packaging:

The zip must unpack directly to:

fresh_ugly_public_20260528_01/<fixture folders...>

Do not include compiled KBs, model outputs, run artifacts, caches, screenshots,
temporary folders, or extra top-level directories.

Before delivery, verify:

- exactly 8 fixture folders;
- every fixture has all required files;
- every qa.md has 25 questions and no answers;
- every qa_questions.jsonl has 25 rows with ids q001-q025;
- every oracle.jsonl has 25 rows with ids q001-q025;
- every metadata.json parses;
- all source_url values are public official sources;
- all llm_authored_source and llm_rewritten_source fields are false.
```

## Request B - Fresh ACH Heldout Batch 04

Copy/paste to the collecting agent:

```text
You are building a fresh heldout ACH/evidence-matrix stress batch for
Prethinker. Do not inspect Prethinker source code, docs, worksheets, prior ACH
outputs, or run artifacts. Use only the public official source documents you
collect and these instructions. The purpose is to test whether ACH ranking and
sensitivity generalize on new evidence matrices.

Create one zip file named:

fresh_ach_stress_public_20260528_04.zip

Inside the zip, include exactly one top-level folder:

fresh_ach_stress_public_20260528_04/

Inside that folder, create exactly 6 fixture folders:

ach_high_single_pivot_001/
ach_high_single_pivot_002/
ach_medium_family_dependence_001/
ach_medium_family_dependence_002/
ach_low_redundant_support_001/
ach_low_redundant_support_002/

Each fixture folder must contain:

source.md
source_original.txt
ach_payload.json
qa.md
qa_questions.jsonl
oracle.jsonl
metadata.json
provenance.md
fixture_notes.md
anti_leakage_manifest.md
qa_authored_with_answers.md

Also include a top-level batch_manifest.json.

Use real public English-language official documents only. Good sources include:
NTSB final reports, SEC administrative orders, FDA warning letters, OSHA/OSHRC
decisions, FTC/CFPB/state AG orders or complaints, public utility commission
orders, or court/agency decisions. Avoid documents already used in prior
Prethinker batches. Avoid famous cases likely to be memorized.

Batch distribution:

- 2 high-sensitivity fixtures: one evidence row should be clearly pivotal.
- 2 medium-sensitivity fixtures: no single row should dominate, but a small
  family of two or three rows should materially weaken the winner if omitted.
- 2 low-sensitivity fixtures: the winner should be robust because several
  independent rows support the same conclusion; no row or small family should
  be pivotal.

Important: The source document must support the expected ACH read. Do not
invent facts. The ACH payload should be analyst-authored from the source,
not generated from Prethinker output.

ach_payload.json schema:

{
  "fixture_id": "<folder_name>",
  "ach_question": "<one concrete question the matrix answers>",
  "balanced_fixture": true,
  "hypotheses": [
    {
      "id": "h1",
      "label": "<short label>",
      "claim": "<full hypothesis claim>"
    }
  ],
  "evidence_rows": [
    {
      "id": "e1",
      "label": "<short evidence label>",
      "source_coords": "<section/table/paragraph/heading coordinate>",
      "text_anchor": "<short exact or near-exact source anchor>",
      "expected_relevance": "<why this evidence matters; may mention whether it supports, weakens, distinguishes, or conditions hypotheses>"
    }
  ],
  "expected_read": {
    "best_hypothesis": "<hypothesis id>",
    "rationale": "<source-grounded explanation>",
    "sensitivity_expectation": "high|medium|low",
    "pivotal_evidence": "<evidence id, evidence id family like e1+e3, or none>",
    "flip_note": "<what should happen if pivotal evidence/family is removed>"
  }
}

Hypothesis requirements:

- 3 to 5 hypotheses per fixture.
- Hypotheses must be plausible alternatives from the source context.
- At least one alternative must have real support, not a strawman.
- Avoid labels that encode the answer too obviously.

Evidence requirements:

- 6 to 10 evidence rows per fixture.
- Every evidence row must have a source coordinate and text anchor.
- Include at least one row that supports an alternative hypothesis.
- Include at least one row that weakens or qualifies a hypothesis.
- Include at least one row whose interpretation depends on another row for
  medium-sensitivity fixtures.

High-sensitivity fixture design:

- There should be one central evidence row that connects mechanism to outcome,
  authority to consequence, or factual finding to legal/regulatory conclusion.
- Removing that row should make the top hypothesis collapse, tie, or become
  materially uncertain.
- Put that row in expected_read.pivotal_evidence.

Medium-sensitivity fixture design:

- There should not be one obvious single pivot.
- Instead, two or three rows together should frame the winning interpretation.
- Removing one row alone may not flip the winner, but removing the family should
  weaken or destabilize it.
- Put the family in expected_read.pivotal_evidence, for example "e2+e4".

Low-sensitivity fixture design:

- The top hypothesis should be independently supported by multiple rows.
- Removing any one row or small family should not change the conclusion.
- Use "none" for expected_read.pivotal_evidence.

QA requirements:

Each fixture also needs 10 ordinary QA rows about the source document so the
same package can test ordinary evidence extraction:

- 3 direct source facts;
- 2 source-coordinate/provenance questions;
- 2 date/sequence/identifier questions;
- 2 finding/cause/order/consequence questions;
- 1 question asking for a limitation, caveat, or absence.

qa.md must contain the 10 questions only. qa_questions.jsonl and oracle.jsonl
must use ids q001 through q010. qa_authored_with_answers.md must include the
same 10 questions with answers.

metadata.json:

{
  "schema_version": "fresh_ach_stress_batch_v2",
  "batch_id": "fresh_ach_stress_public_20260528_04",
  "fixture_id": "<folder_name>",
  "domain": "<ntsb|sec|fda|osha|ftc|cfpb|court|puc|state_ag|other>",
  "source_title": "<official title>",
  "source_url": "<public official URL>",
  "source_date": "<YYYY-MM-DD or unknown>",
  "collected_at": "<YYYY-MM-DD>",
  "document_type": "<short type>",
  "public_source": true,
  "language": "en",
  "sensitivity_target": "high|medium|low",
  "primary_pressure": "<one sentence>",
  "llm_authored_source": false,
  "llm_rewritten_source": false
}

Top-level batch_manifest.json:

{
  "batch_id": "fresh_ach_stress_public_20260528_04",
  "created_at": "<YYYY-MM-DD>",
  "purpose": "Fresh heldout ACH stress batch for ranking and sensitivity generalization.",
  "expected_distribution": {
    "high": 2,
    "medium": 2,
    "low": 2
  },
  "fixtures": [
    {
      "fixture_id": "<folder_name>",
      "domain": "<domain>",
      "sensitivity_target": "high|medium|low",
      "source_url": "<public official URL>",
      "document_type": "<short type>"
    }
  ],
  "notes": "Do not tune to Prethinker. This is an unseen heldout batch."
}

Packaging:

The zip must unpack directly to:

fresh_ach_stress_public_20260528_04/<fixture folders...>

Do not include compiled KBs, model outputs, run artifacts, caches, screenshots,
temporary folders, or extra top-level directories.

Before delivery, verify:

- exactly 6 fixture folders;
- every fixture has all required files;
- every ach_payload.json parses and has 3-5 hypotheses and 6-10 evidence rows;
- two fixtures have sensitivity_target high, two medium, two low;
- every qa.md has exactly 10 questions and no answers;
- every oracle.jsonl has exactly 10 rows with ids q001-q010;
- all source_url values are public official sources;
- all llm_authored_source and llm_rewritten_source fields are false;
- no Prethinker internals, prior worksheets, prior fixture answers, or run
  artifacts were used.
```

## Which One To Prioritize

If only one batch can be built now, build Request A first. It is the product
thermometer for core compile/query behavior. Request B is valuable if we want to
turn ACH sensitivity into a credible product claim, but it should remain an
overlay validation lane.

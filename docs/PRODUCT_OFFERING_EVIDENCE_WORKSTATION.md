# Product Offering: Evidence Workstation

Last updated: 2026-05-24

## One-Sentence Shape

Prethinker is an evidence workstation for messy official documents: document
packs go in; compiled evidence ledgers, governed QA, coverage warnings, and
optional competing-hypothesis matrices come out.

## Product Position

The supportable product is not "upload anything and trust the answer." That is
too broad, hard to support, and easy to overclaim.

The stronger product is a decision-support instrument for domains where
reviewers already care about source authority, audit trails, citations, dates,
actors, obligations, findings, and uncertainty.

```text
document pack
  -> compiled evidence artifact
  -> governed question answering
  -> coverage and uncertainty report
  -> optional ACH / evidence matrix
  -> exportable audit bundle
```

The customer value is not just the answer. It is the answer plus the evidence
path, source coordinates, cleanliness counters, and explicit weak spots.

## First Buyers

The first product surface should stay close to messy official documents with
regular structure:

| Market | Good starting documents | Buyer value |
| --- | --- | --- |
| Regulatory and compliance review | Warning letters, inspection reports, enforcement packets, filings, citation records | Extract cited violations, dates, deadlines, corrective actions, authority findings, and missing coverage. |
| Legal and investigation support | Incident reports, contracts, claims files, expert reports, discovery packets | Build fact ledgers, contradiction notes, source-attributed claims, timelines, and reviewable evidence matrices. |
| Insurance, claims, and risk | Accident packets, safety reports, estimates, correspondence, medical-adjacent narratives | Reduce triage time, organize facts, expose missing evidence, and produce reviewer-ready notes. |
| Safety and root-cause analysis | Transportation, workplace, product, facility, and operational incident records | Separate chronology, causal hypotheses, severity factors, prior warnings, and source confidence. |

The best first demo vertical is likely incident investigation. It naturally
shows timelines, actors, causal theories, technical evidence, coverage gaps,
and ACH without making the product look like a simple citation extractor.

## What The User Gets

### 1. Compiled Evidence Artifact

The durable product is a compiled knowledge package, not a hidden chat history:

```text
world.pl          admitted source state
epistemic.pl      source claims, uncertainty, findings, corrections
ledgers.pl        source rows, sections, table cells, identifiers, dates
query_policy.json answer policy and allowed evidence surfaces
manifest.json     source hash, compiler/model/schema/run metadata
diagnostics.json  skipped, held, weak, or missing coverage notes
```

This package is the answer substrate. QA should answer over admitted state and
deterministic ledgers, not by rereading the source as invisible RAG.

### 2. Governed QA Report

A user can ask ordinary questions about the document pack. Prethinker returns
answers grounded in the compiled artifact, with source support and row-level
accounting.

The report should expose:

- concise answer;
- supporting facts, source rows, table coordinates, or claims;
- whether the answer rests on an established fact, source claim, unresolved
  conflict, explicit absence, or missing compiled coverage;
- exact / partial / miss accounting for evaluated runs;
- compatibility rows, runtime load errors, and QA write proposals.

The key product claim is governed QA over admitted state, not model-free QA.
Models may propose query plans or judge rows; deterministic code controls what
can execute and whether any answer stayed inside policy.

### 3. Coverage And Gate Report

Coverage warnings are a feature. They tell the reviewer where the compiled
artifact is strong and where a human should be careful.

The report should distinguish:

- compile-surface gaps: the source distinction was not preserved;
- query-surface gaps: the artifact had enough information, but query planning
  missed it;
- hybrid-join gaps: pieces existed, but the join was missing or misbound;
- answer-surface gaps: evidence was close, but the answer shape was wrong;
- judge-uncertain rows: the evaluation could not cleanly classify the issue.

For buyers, this is the difference between "the system answered" and "the
system showed where it was strong, weak, or silent."

### 4. ACH / Evidence Matrix

The Analysis of Competing Hypotheses overlay is a sibling product surface. It
does not mutate the KB and does not inflate QA scores.

ACH is useful when the task is not simply fact lookup:

```text
admitted evidence rows
  -> competing hypotheses
  -> consistency / inconsistency / neutral / not-applicable judgments
  -> least-disconfirmed ranking
  -> sensitivity and diagnostic evidence report
```

This is likely the clearest buyer-facing front door. Many domains immediately
understand "evidence matrix." It gives Prethinker a familiar language for
investigation, claims, legal review, compliance review, root-cause analysis,
and expert workflows.

### 5. Exportable Audit Bundle

A product run should export enough material for a reviewer, supervisor, or
customer-side auditor to inspect the path:

- source manifest and hash;
- compile artifact package;
- QA report;
- coverage/gate report;
- ACH payload and matrix report, if used;
- run metadata: model, provider, schema version, timestamp, and policy flags;
- cleanliness counters.

The bundle should be boring in the best way: replayable, inspectable, and clear
about its limits.

## What We Can Already Show

The repo already has the core artifacts needed for a credible soup-to-nuts
demo:

- compiled KB artifact doctrine:
  [Compiled KB Artifact Package](https://github.com/dr3d/prethinker/blob/main/docs/COMPILED_KB_ARTIFACT_PACKAGE.md);
- governed QA doctrine:
  [QA Instrument](https://github.com/dr3d/prethinker/blob/main/docs/QA_INSTRUMENT.md);
- public measurement discipline:
  [Audit Grammar Measurement Note](https://github.com/dr3d/prethinker/blob/main/docs/AUDIT_GRAMMAR_MEASUREMENT_NOTE.md);
- current headline:
  [Current Research Headline](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_RESEARCH_HEADLINE.md);
- ACH overlay design and probes:
  [ACH Overlay Probe](https://github.com/dr3d/prethinker/blob/main/docs/ACH_OVERLAY_PROBE.md);
- fresh public-document worksheets and archived run artifacts for transfer
  evidence.

The current public measurement stack supports a serious, caveated story:

```text
native maintained corpus:
  1997 / 46 / 120 over 2163 rows = 92.33% exact
  0 compatibility rows
  0 runtime load errors
  0 QA write proposals

sealed unseen authored transfer:
  152 / 1 / 6 over 160 rows = 95.0% exact

real-world public-document evidence:
  clean four-fixture spotcheck at latest fixture-level QA
  newer fresh ugly public batches under active transfer measurement

ACH real-document probes:
  complete matrices, 0 warnings, top hypotheses matching report-level cause
  findings on incident-report payloads
```

These are not universal benchmark claims. They are evidence that the instrument
is becoming product-shaped for messy, structurally regular official documents.

## What Not To Claim

Do not sell Prethinker as:

- an autonomous legal, medical, regulatory, or financial decision-maker;
- a chatbot that can safely answer anything from any upload;
- a model-free deterministic reasoner;
- a system that has already proven 95% accuracy on arbitrary messy documents;
- a substitute for professional review.

The truthful claim is stronger and safer:

```text
Prethinker organizes messy official documents into auditable evidence artifacts
and supports reviewer decisions with grounded answers, coverage warnings, and
competing-hypothesis analysis.
```

## Demo Package

A polished first demo should use one real public incident or enforcement record
and show the whole path:

1. Import a document pack.
2. Compile into the evidence artifact package.
3. Show the evidence ledger: dates, actors, events, claims, quantities, source
   rows, identifiers, and findings.
4. Run a governed QA set with support rows.
5. Show coverage warnings and non-answerable areas.
6. Build an ACH evidence matrix from admitted rows.
7. Export the audit bundle.

The demo should make the product legible without explaining every internal
mechanism. A buyer should see:

```text
I can inspect the evidence.
I can ask grounded questions.
I can see weak coverage.
I can compare explanations.
I can export the audit trail.
```

## Near-Term Product Work

The next product-shaped engineering work is:

1. Build a polished demo bundle around one incident-report workflow.
2. Make the compiled artifact package easier to browse: source rows, facts,
   claims, dates, quantities, and uncertainty in separate views.
3. Add a lightweight report generator for QA plus coverage warnings.
4. Build an ACH payload proposer that suggests hypotheses and evidence rows
   from admitted state while leaving judgments reviewable.
5. Keep expanding the fresh public-document thermometer with ugly documents
   from official sources.
6. Preserve anti-leakage discipline: no fixture names, answer strings, row IDs,
   or research-only vocabulary in the instrument.

## Pricing Shape

The natural packaging is by document packs, seats, and audit retention:

| Tier | Shape |
| --- | --- |
| Solo / Pro | Limited document packs, local exports, small-team review. |
| Team | Shared workspaces, larger pack volume, reusable schemas, review notes. |
| Enterprise / Compliance | Private deployment, audit retention, custom schemas, admin controls, support. |

The pricing unit should track expensive work: compile runs, QA batches, ACH
matrices, storage, and audit retention. The product should not encourage
unbounded arbitrary upload without cost visibility.

## Product North Star

Prethinker should become the workstation a reviewer opens when the document set
is too messy for a spreadsheet and too consequential for a chatbot answer.

The product succeeds when it makes the evidence legible, the answer path
auditable, the uncertainty explicit, and the reviewer faster without pretending
to replace their judgment.

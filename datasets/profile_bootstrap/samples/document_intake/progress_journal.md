# Document Intake Progress Journal

This journal tracks Declaration/Proclamation source-document ingestion as a
cross-application of the Iron Harbor lessons. The goal is not to make Python
read the documents. The goal is to improve the context/profile surface so the
LLM can do the same document-to-logic work through the governed pipeline.

## DCI-001 - Hint-Free Declaration Recheck

- Timestamp: `2026-05-01T00:51Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Run:
  `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T005130258045Z_declaration_qwen-qwen3-6-35b-a3b.json`

### Result

- Candidate predicates: `17`
- Source compile: `211` admitted, `0` skipped
- Expected signature recall: `0.116`

### Lesson

The model understood the Declaration, but profile bootstrap still over-compressed
the predicate surface. It kept useful high-level predicates such as
`grievance/2`, `grievance_actor/2`, and `grievance_target/2`, but it omitted too
much of the reusable document backbone (`document/1`, `claim_made/3`, `rule/2`,
`right/2`, appeal/final-action predicates, and detail slots).

## DCI-002 - Narrow Declaration Registry

- Timestamp: `2026-05-01T01:29Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: Declaration-only fixture registry supplied as candidate vocabulary;
  LLM still owns source compilation and the mapper still owns admission.
- Run:
  `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T012931093611Z_declaration_qwen-qwen3-6-35b-a3b.json`

### Result

- Candidate predicates: `68`
- Source compile: `161` admitted, `4` skipped
- Expected signature recall: `0.391`

### Lesson

A narrow registry beats both hint-free over-compression and the too-wide
combined document registry. This mirrors the Harbor/Otters finding: the model
benefits from a curated working surface, but a giant menu makes it timid.

## DCI-003 - Hybrid Declaration Registry Selection

- Timestamp: `2026-05-01T01:59Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: Declaration registry supplied as candidate context, but the model chose
  the active profile surface.
- Run:
  `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T015931102218Z_declaration_qwen-qwen3-6-35b-a3b.json`

### Result

- Candidate predicates: `75`
- Source compile: `323` admitted, `0` skipped
- Expected signature recall: `0.464`

### Lesson

The hybrid path is the strongest current Declaration result. The LLM can use a
curated registry without being forced to expose the entire registry to every
compile pass. This is a good template for document-domain profile packages.

## DCI-004 - Proclamation Baselines

- Timestamp: `2026-05-01T01:08Z` through `2026-05-01T01:52Z`
- Model: `qwen/qwen3.6-35b-a3b`

### Runs

- Hint-free compile:
  `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T010851274237Z_proclamation_qwen-qwen3-6-35b-a3b.json`
- Narrow direct registry:
  `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T013416198203Z_proclamation_qwen-qwen3-6-35b-a3b.json`
- Hybrid registry selection:
  `tmp/domain_bootstrap_file/domain_bootstrap_file_20260501T014919748579Z_proclamation_qwen-qwen3-6-35b-a3b.json`

### Result

- Hint-free: `147` admitted, expected signature recall `0.066`,
  first-20 QA `14 exact / 2 partial / 4 miss`
- Narrow direct registry: `46` admitted, expected signature recall `0.246`,
  first-20 QA `12 exact / 1 partial / 7 miss`
- Hybrid registry selection: `249` admitted, expected signature recall `0.197`,
  first-20 QA `13 exact / 2 partial / 4 miss`

### Lesson

Signature recall alone is not the right target. The narrow direct registry
improved predicate precision but lost support coverage. The hybrid path has the
best compile surface, while the hint-free run still edged it on first-20 QA.
Next work should score required symbolic support per question, not merely
profile/expected signature overlap.

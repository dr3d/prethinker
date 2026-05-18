# Source Reference Surface Transfer

Boundary class: `source_reference`

This probe tests whether source-stated document, ticket, report, memo, section,
and source-of-status references become direct queryable surfaces on unlike
documents.

The fixture-free geometry is:

- the source states an operational fact such as status, schedule, exclusion, or
  assignment;
- the same source states which source document, ticket, report, section, memo,
  or note carries that fact;
- questions ask for both the fact and the source reference;
- source-record ledgers may preserve the printed text, but direct compile
  surfaces should make source references addressable without rereading prose;
- no repair may name this probe, its identifiers, or its domains.

## 2026-05-18 replay

Compile artifact:
`tmp/source_reference_surface_transfer_compile_20260518/domain_bootstrap_file_20260518T224812863960Z_source_qwen-qwen3-6-35b-a3b.json`

Initial QA replay: `9/0/1`. The miss was not a missing compile surface: the KB
contained a direct source-bound status row, but the query plan treated the
source document identifier as the subject of a neighboring restriction query.

Repair tested:

- add a query-only source-identifier slot fallback;
- only fire after query routing touches an identifier the KB already recognizes
  as document/source-like;
- retrieve admitted rows where that identifier appears in a provenance/source
  slot;
- do not parse source prose, introduce new predicates, or name probe content.

Post-repair QA replay:
`10/0/0`, failure surfaces `{'not_applicable': 10}`, compatibility rows `0`,
runtime load errors `0`, write proposals `0`.

Lesson: this source-reference boundary is mostly an interior coordinate with a
query-routing blur. A source/document id may be the provenance slot for the
answer-bearing row rather than the answer subject. The generic repair is to
search admitted provenance slots for KB-recognized source identifiers, not to
teach the harness the local source names.

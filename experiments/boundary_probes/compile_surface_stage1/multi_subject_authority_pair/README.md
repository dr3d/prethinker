# Multi-Subject Authority Pair

Boundary class: `multi_subject_authority_coverage`

This probe tests whether the compile layer preserves every governed subject
when one source authority applies to multiple named items, actions, or status
changes.

The fixture-free geometry is:

- a source document, directive, bulletin, or board record names an authority;
- the same authority governs more than one subject/action;
- questions ask for the source authority for individual governed subjects;
- a nearby non-authority or unrelated authority is present to prevent broad
  source-label answers;
- no helper should reconstruct missing rows from prose after compile.

No repair should name this probe, its identifiers, or its domains.

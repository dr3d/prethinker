# Fixture Notes — lease_amendment_status_register

## What this fixture pressures

The fixture stresses a model's ability to navigate a multi-document lease lifecycle in which several documents have explicit non-binding or no-legal-effect declarations, alongside documents that ARE binding. The model must distinguish source authority (the executed amendment AMD-2026-014, the corrected register entry REG-E-2026-061-R) from source opinion (counsel's advisory opinion COP-2026-031), source statement (the clerk's advisory note CN-2026-022), and source declaration of intent (the tenant's non-binding letter TLOI-2026-019).

A central pressure point is *non-binding source claims*: TLOI-2026-019 expresses tenant intent in considerable detail; its footer makes the entire document non-binding. A naive extractor will ingest the LOI's substantive terms as if they had legal effect. The model must preserve the speech-act (Quillvale stated intent) without treating the stated terms as committed facts.

A second pressure point is the *amendment lifecycle*: a draft (PA-2026-014-D1) is superseded by a revised draft (PA-2026-014-D2), which is superseded by the executed amendment (AMD-2026-014). A separate void notice (VD-2026-003) is later issued specifically against the original draft. The model must track the supersession chain.

A third pressure point is the *register correction*: the initial register entry REG-E-2026-061 recorded the ROFR as Unit 4C, which was a transcription error against the executed amendment (which had been changed at execution to Unit 4D). CORR-2026-008 corrects this. The current ROFR is on Unit 4D. A model that snapshots either the early drafts (Unit 4C) or the initial register entry (Unit 4C) will report the stale unit.

A fourth pressure point is *source-record label/detail stranding*: each row has a row label (ROW-LSE-001, ROW-AMD-001, etc.) and a document identifier (LSE-2024-0331-007, PA-2026-014-D1, etc.). The model must retain both as separately queryable identifiers without losing the pairing.

## Intended pressure categories

1. non_binding_no_effect — TLOI-2026-019 and CN-2026-022 are non-binding/advisory by their own terms; their stated content must not be promoted to committed facts.
2. source_attributed_letters_and_notes — clerk note, tenant LOI, counsel opinion are each source-attributed to named authors and must remain so.
3. amendment_current_state — the executed amendment AMD-2026-014 is the operative governing instrument; current rent, term-end, and ROFR derive from it as corrected by CORR-2026-008.
4. correction_record — CORR-2026-008 corrects the initial register entry's ROFR unit; the corrected entry is REG-E-2026-061-R.
5. source_authority_vs_source_opinion — counsel's opinion is advisory; the executed amendment is binding; the register entry is the official Register record.
6. source_record_label_detail — row labels and document identifiers must both remain individually queryable.
7. effective_void_under_review_state — multiple status states co-exist in the same packet (EFFECTIVE, SUPERSEDED, SUPERSEDED BY EXECUTION, SUPERSEDED BY CORRECTION, OPERATIVE, CURRENT, ADVISORY, NON-BINDING, VOID).
8. dated_source_labels — every row carries a date; the date is part of the source label and must be retrievable.

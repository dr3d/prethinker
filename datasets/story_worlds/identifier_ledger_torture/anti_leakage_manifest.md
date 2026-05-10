# Anti-Leakage Manifest — identifier_ledger_torture

This manifest classifies each oracle answer by how it is supported in `source.md` and flags any prose that, if naively used, would corrupt an answer. Tags follow the spec.

## Per-question classification

| qid | tags |
|---|---|
| q001 | direct_lookup, identifier_exact |
| q002 | direct_lookup, identifier_exact |
| q003 | direct_lookup, identifier_exact |
| q004 | direct_lookup, identifier_exact |
| q005 | direct_lookup, identifier_exact |
| q006 | direct_lookup, identifier_exact, withdrawn_trap |
| q007 | direct_lookup, identifier_exact |
| q008 | direct_lookup, identifier_exact |
| q009 | direct_lookup, identifier_exact |
| q010 | composition, identifier_exact |
| q011 | direct_lookup, identifier_exact, withdrawn_trap |
| q012 | direct_lookup, identifier_exact, withdrawn_trap |
| q013 | composition, identifier_exact |
| q014 | direct_lookup, identifier_exact |
| q015 | composition, identifier_exact |
| q016 | composition, unresolved |
| q017 | direct_lookup, derived_count |
| q018 | direct_lookup, derived_count |
| q019 | direct_lookup, derived_count |
| q020 | composition, identifier_exact |
| q021 | direct_lookup, identifier_exact |
| q022 | direct_lookup, identifier_exact |
| q023 | composition, identifier_exact |
| q024 | direct_lookup |
| q025 | direct_lookup |
| q026 | composition, identifier_exact |
| q027 | direct_lookup, identifier_exact |
| q028 | direct_lookup, identifier_exact |
| q029 | direct_lookup, identifier_exact |
| q030 | direct_lookup, identifier_exact |
| q031 | direct_lookup, identifier_exact, withdrawn_trap |
| q032 | direct_lookup, identifier_exact |
| q033 | composition, identifier_exact |
| q034 | composition, identifier_exact |
| q035 | direct_lookup |
| q036 | direct_lookup |
| q037 | derived_time |
| q038 | unresolved |
| q039 | unresolved |
| q040 | derived_count, composition |

## Direct lookups vs derivations

- **direct_lookup** rows: the answer string appears explicitly in `source.md`, typically in Section 2, Section 9.6, or one of the named tables. These rows test retrieval and exact-string fidelity, not derivation.
- **derived_count** rows: q017 (twelve active labels), q018 (two withdrawals), q019 (three open exceptions), q040 (eleven items physically held). q017 is also stated explicitly in the prose ("the master inventory contains twelve active labels"); it is therefore not a pure derivation test, but the derivation chain (start − withdrawals + replacements counted as carryforward) is also fully documented in Section 11. q040 is **not** stated explicitly and requires combining the active-label count with the released-status flag on EX-D-04.
- **derived_time** rows: q037 (interval during which the wrong barcode was on file). Endpoints are stated; the interval label is the derivation.
- **composition** rows: q010, q013, q015, q020, q023, q026, q033, q034, q040 require combining at least two source sections (typically one identifier table plus one note or another table).
- **unresolved** rows: q016, q038, q039 require preserving pending or non-yet-resolved status without inventing a resolution.
- **withdrawn_trap** rows: q006, q011, q012, q031 explicitly require returning a withdrawn or superseded value. Any system that filters out withdrawn values before answering will fail these.

## Sections of `source.md` that, if used naively, would contaminate answers

1. **Section 4 (Withdrawn / Superseded Labels)** lists the withdrawn label strings. These must be retrievable when the question explicitly asks for a withdrawn label (q011, q012) but must not contaminate "current label" questions (q001, q014).
2. **Section 5 (Open Audit Exceptions)** describes the revolver's location and pending disposition together. A retrieval system must not confuse the location (confirmed) with the disposition (pending).
3. **Section 5.5 (Prior-Window Carryforward Notes)** describes the lineage of EX-C-01 and EX-E-10. A naive retrieval may pull the legacy label EX-C-1 in answer to "current label" questions because the lineage prose mentions it many times.
4. **Section 9.5 (Scan History Excerpt — Revolver)** retains the original mistaken barcode `BC-833014` in the historical row. This row must not be returned for "current barcode" queries, but must be returned for q006 and q037.
5. **Section 6 (Bay 04 Walk-Down Detail)** notes a 2025 audit error that put the laptop at BAY-04-L. That historical mistake must not be returned for current location queries.
6. **The cover memo's mention of "expected no earlier than 2026-05-20"** must not be paraphrased as "the order will issue 2026-05-20" — the date is a floor, not the issuance date.

## Answers explicitly stated in `source.md`

The following are direct lookups whose answers appear verbatim or near-verbatim in the source. They are still useful tests of exact-string fidelity but are not derivation tests: q001, q002, q003, q004, q005, q008, q009, q011, q012, q014, q017, q018, q019, q021, q022, q024, q025, q027, q028, q029, q032, q035, q036.

## Answers that are *not* explicitly stated and therefore are derivation tests

q010 (the meaning of suffixes is stated in Section 6, but the comparison framing is not), q013 (joins Section 4 with Section 9.6), q015 (denial of identity is implied, not stated as a sentence), q020, q023, q026, q033, q034 (all multi-field compositions), q037 (interval inference), q040 (count after status filter), q038 and q039 (negative/unresolved framings derived from absence of an action or order in the audit window).

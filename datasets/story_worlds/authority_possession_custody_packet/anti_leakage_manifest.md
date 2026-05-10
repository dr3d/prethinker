# Anti-Leakage Manifest — authority_possession_custody_packet

## Per-question classification

| qid | tags |
|---|---|
| q001 | direct_lookup |
| q002 | direct_lookup |
| q003 | direct_lookup |
| q004 | composition |
| q005 | composition |
| q006 | direct_lookup |
| q007 | direct_lookup |
| q008 | direct_lookup |
| q009 | direct_lookup |
| q010 | composition |
| q011 | direct_lookup |
| q012 | direct_lookup |
| q013 | direct_lookup |
| q014 | unresolved |
| q015 | unresolved |
| q016 | direct_lookup |
| q017 | unresolved |
| q018 | composition |
| q019 | composition |
| q020 | direct_lookup |
| q021 | derived_count, direct_lookup |
| q022 | derived_count |
| q023 | derived_count |
| q024 | composition |
| q025 | composition |
| q026 | direct_lookup |
| q027 | direct_lookup |
| q028 | direct_lookup |
| q029 | direct_lookup |
| q030 | direct_lookup |
| q031 | direct_lookup |
| q032 | composition |
| q033 | composition |
| q034 | unresolved |
| q035 | unresolved |
| q036 | derived_time |
| q037 | direct_lookup |
| q038 | direct_lookup |
| q039 | composition |
| q040 | composition, derived_count |

## Direct lookups vs derivations

- **Section 9 (Quick-Reference Stewardship Summary)** is a derived summary table that ALSO appears in the source. This is a deliberate leakage: many composition answers are visible there. The manifest discloses that q005, q010, q024, q025, q032, q033, q039 are partially visible in Section 9. They remain useful as state-tracking tests because the source's preamble explicitly says "the governing documents above control where there is any conflict," and a system that prefers the table over Sections 1–8 will get a correct answer here but is doing the wrong thing in principle.
- **derived_count** rows: q021 is stated explicitly in the receipt text but counting the table also gives 12; q022 requires forty-seven minus twelve and an additional check that the photograph album's recall has ended by 2026-04-30 (it has); q023 requires distinguishing letters at Pellico (16) from letters at Stille (8) and is supported by Section 9.
- **derived_time** row: q036 requires reading the recall note in Section 5 and reporting the interval 2026-03-03 through 2026-03-05.
- **unresolved** rows: q014, q015, q017, q034, q035 require preserving pending or absent state. q035 is a negative-existential about MOU scope additions.

## Sections that, if used naively, would contaminate answers

1. **Section 6 (Counsel Memorandum)** offers Latham & Carr's reading that the right covers facsimile only. A model that returns this as "the answer" will fail q014, which requires preserving both readings as unresolved.
2. **Section 7 (Resolution 2026-08)** says publication is paused. A model that says "publication of all Halberd materials is paused" will fail q024 and q025 because the pause applies only to personal correspondence.
3. **Section 5 (access log)** lists "Pellico Society" as the authorizer for every visit, including those at Stille premises. A model that confuses "authorized by Pellico Society" with "in custody of Pellico Society" will fail q032 and q002 for the relevant dates.
4. **Section 9 row "Photograph album"** shows physical custody at Stille (since 2025-11-12). A model that does not also read the access log's recall note (under "Notes on the 2026-03-04 visit") will be unable to answer q036 correctly.
5. **The phrase "subject to the Halberd Family Trust's reserved right of pre-publication review"** appears in multiple rows. A model that drops the qualifier in answers about Notebook B (which is not subject to the right) will introduce a false constraint.

## Answers explicitly stated vs derived

**Stated explicitly:** q001 (Section 1; reinforced in Section 9), q002 (Section 3 and Section 9), q006 (Section 9), q007 (Section 4), q008 (Section 4 and 9), q009 (Section 4), q011 (Section 4), q012 (Section 5 row 2026-03-11), q013 (Section 5 note), q016 (Section 8), q020 (Section 0 + Section 1), q021 (Section 3), q026 (Section 2), q027 (Section 3 and Section 2), q028 (Section 3), q029 (Section 1), q030 (Section 4), q031 (Section 3), q037 (Section 5 note + Section 2), q038 (Section 2).

**Derived:** q004 (joins authority + Resolution 2026-08), q005 (joins multiple sections), q010 (joins Section 4 with Sections 1–3), q017 (read absence of determination from Section 8), q018 (joins Resolution + counsel + agreement), q019 (joins Resolution §2 + access log), q022 (count subtraction with custody-state check), q023 (count split), q024 (joins Section 1 definition with Section 7 scope), q025 (joins Section 7 with Section 1), q032 (joins Section 3 custody with Section 5 authorization), q033 (joins Section 9 with Section 7), q034 (joins Section 6 caveat with Section 7 §4), q035 (Section 4 'None' line), q036 (Section 5 recall note), q039 (joins Section 9 with Section 1 definition), q040 (cross-cutting filter across the stewardship table).

## Withdrawn or superseded text

The packet has no withdrawn text; the dispute is about scope of an active reservation, not about superseded text. The recall note documents a temporary location change, not a withdrawal. There is therefore no `withdrawn_trap` tag in this fixture.

# Anti-Leakage Manifest — contradictory_evidence_packet

This manifest discloses which reference answers are **stated verbatim** in source.md, **derived** from source content, or **partially derived**. The contradictory_evidence_packet is unusual among the six fixtures because its highest-signal questions (the unresolved cluster) are answered correctly by *not synthesizing* a resolution that the source explicitly declines to provide. For these questions, "verbatim" cuts both ways — the unresolved status is stated in the packet, but a parser oriented toward helpful answers may override the explicit non-resolution.

## Per-question disclosure

| Q | Tag | Verbatim? | Notes |
|---|-----|-----------|-------|
| q001 | direct_lookup | YES | "IIR-2026-0084" in header. |
| q002 | direct_lookup | YES | Compiler and date stated in header. |
| q003 | identifier_exact | YES | "BDG-44217" stated in §1. |
| q004 | direct_lookup | YES | Date range stated in §1. |
| q005 | direct_lookup | YES | "21:00 on weekdays" stated in §1. |
| q006 | direct_lookup | YES | "2025-09-01" stated in §1. |
| q007 | identifier_exact | YES | Raw 22:07:34 in BAS table. |
| q008 | identifier_exact | YES | 22:54:29 in CCTV §2.2. |
| q009 | derived_time | NO | The corrected wall-clock 22:54:46 is stated in §3.1, but it's stated as a specific arithmetic example. The parser must show the correction was applied; a model could pattern-match the stated answer. **Flag: §3.1 explicitly walks through this arithmetic, so q009 is partially leaked.** |
| q010 | direct_lookup | YES | "+47-minute-12-second drift" stated verbatim in §3.1. |
| q011 | direct_lookup | YES | "2026-03-19" stated in §3.1. |
| q012 | authority | YES | "BAS-MAINT-2026-04-28-003" stated in §3.1. |
| q013 | derived_time | PARTIAL | The corrected times for BAS-003 through BAS-006 are listed in §3.2 verbatim. **Flag: §3.2's bulleted corrected-times list leaks q013 and q014.** This is a known leak; the test value is whether the parser binds raw→corrected as a *transformation* rather than copying the stated value. |
| q014 | derived_time | PARTIAL | Same flag as q013. Corrected egress 02:41:34 stated in §3.2. |
| q015 | arithmetic | NO | The 3h42m duration is NOT stated explicitly. The packet states "≈3 hours 42 minutes of corrected presence" in §3.4, which is close but not identical to the precise 3h42m34s. **Flag: §3.4 leaks an approximate value of this answer; the precise value requires arithmetic on q013 and q014.** |
| q016 | composition | YES | §3.1 states the agreement explicitly ("within 17 seconds"). |
| q017 | unresolved | YES (status) | §3.3 explicitly flags identity as "genuinely unresolved." Useful as exact-string fidelity for the unresolved status; the parser's challenge is to *not* resolve it despite circumstantial pressure. |
| q018 | composition | YES | §2.2 and §4 state CCTV reliability/limits explicitly. |
| q019 | direct_lookup | YES | "23:00 to 23:40" stated in §2.3. |
| q020 | composition | PARTIAL | §3.6 explicitly states "not in conflict" and walks through the timeline. **Flag: q020 is largely stated; the test value is whether the parser correctly classifies the relationship as consistent rather than conflicting.** |
| q021 | composition | YES | §2.3 reliability bullet stated explicitly. |
| q022 | composition | YES | §2.3 not-reliable bullet stated explicitly. |
| q023 | direct_lookup | YES | "21:58" stated in §2.4. |
| q024 | composition | YES | §2.4 quoted memo content + summary stated. |
| q025 | negative_existential | YES | §2.4 explicitly states Hsiao "do[es] not have personal knowledge." |
| q026 | composition | YES | §2.5 reliability statement explicit. |
| q027 | composition | YES | §2.5 not-reliable statement explicit. |
| q028 | direct_lookup | YES | §2.6 caveats stated explicitly (400m, 4.2km, sectors named). |
| q029 | derived_time | NO | The intervals must be inferred from the ping table; not stated as a single sentence. Genuine extraction question. |
| q030 | composition | YES | §2.6 carrier note stated explicitly. |
| q031 | derived_count | NO | Source labels are A through F; counting them and confirming six requires aggregation. **Flag: while the labels A–F are stated, the source never says "six sources." The parser must count.** |
| q032 | derived_count | NO | The classification requires inspecting each §3.x subsection's "Status:" line. Three are stated as "timeline-resolvable" (§3.1, §3.2, §3.5). §3.6 is "not in conflict" (not counted as a resolved conflict because there is no conflict). **Flag: this is a genuine classification task.** |
| q033 | derived_count | NO | Two are stated as "genuinely unresolved" (§3.3, §3.4). Same classification task as q032. |
| q034 | unresolved | YES | §5 enumerates the open items explicitly (1, 2, 3). |
| q035 | unresolved | YES (status) | §1 states "The Inspector takes no position in this packet." Useful as fidelity; the test is whether the parser respects the explicit non-conclusion. |
| q036 | negative_existential | NO | The negative is not stated as a single sentence. The parser must combine: badge use was recorded, but no source places Aldridge inside. The correct answer requires recognizing that badge-use is not equivalent to holder-identity. **Highest-signal question in the fixture.** |
| q037 | negative_existential | YES | §3.3 states explicitly "no witness contradicts Aldridge's denial." |
| q038 | negative_existential | YES | §3.2 and §3.4 state explicitly "no CCTV inside Lab 4-C or in the 4th-floor corridor." |
| q039 | direct_lookup | YES | "2026-05-19" stated in §5. |
| q040 | negative_existential | YES | §3.3 states "Aldridge has not reported the badge as lost or stolen." |

## Verbatim count

- **Pure verbatim (no derivation):** q001–q008, q010, q011, q012, q016, q018, q019, q021, q022, q023, q024, q025, q026, q027, q028, q030, q034, q037, q038, q039, q040 → 26 questions.
- **Partial derivation:** q013, q014, q017, q020, q035 → 5 questions.
- **Full derivation:** q009 (arithmetic from raw + drift, but example shown in §3.1), q015 (precise duration from corrected timestamps), q029 (interval extraction), q031, q032, q033 (classification counts), q036 (badge-vs-identity composition) → 7 questions.

## Implication for scoring

The contradictory_evidence_packet has heavier verbatim leakage than the rule_activation_exception_matrix because the packet is structured as a self-contained adjudication record where every reliability claim is stated. The discriminating questions are:

- **q036** — does the parser separate badge-use from holder-identity? (full derivation, not stated)
- **q032 and q033** — does the parser correctly classify each conflict subsection? (classification, not stated)
- **q015 and q029** — can the parser do timestamp arithmetic? (genuine derivation)
- **q017 and q035** — does the parser preserve unresolved status under pressure to resolve? (verbatim status, but tests refusal-to-confabulate)

A parser scoring high on the verbatim portion but failing q036, q032/q033, and especially q017/q035 has done string-matching, not reasoning.

## Known leakage to flag

- **q013 and q014 leak via §3.2 bulleted list.** A stricter variant fixture would remove the §3.2 bulleted corrected-times and require the parser to compute them. The current variant tests both transformation-recognition and exact-string fidelity simultaneously.
- **q009 leaks via §3.1 walked-through arithmetic.** Same comment.
- **q020 leaks via §3.6's explicit "not in conflict" line.** A stricter variant would remove §3.6's narrative and require the parser to discover the non-conflict from the timestamps.
- **q017/q035 unresolved status is stated.** This is intentional — the test is not whether the parser can find the unresolved status, but whether the parser *respects* it when other parts of the packet (badge logs, CCTV, autoclave memo) generate circumstantial pressure to resolve. A model that resolves these questions despite the explicit non-resolution is the failure mode this fixture is built to detect.
- **The §3.5 "departure 19:30 vs 19:31" subsection is intentionally classified as "timeline-resolvable" in q032's count.** A parser may want to call this "not a conflict at all" (since the sources agree within 45 seconds). The packet's classification is a borderline case; either interpretation is defensible. Flag for review: if Prethinker's count is off by one on q032, check whether it is excluding §3.5 or §3.6.

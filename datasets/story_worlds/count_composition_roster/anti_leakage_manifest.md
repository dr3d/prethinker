# Anti-Leakage Manifest — count_composition_roster

| q | tag | leakage notes |
|---|---|---|
| q001 | direct_lookup | Stated verbatim in title and §0. |
| q002 | direct_lookup | Stated verbatim in title and §0. |
| q003 | direct_lookup | Stated verbatim in §2.2 and §6.2. |
| q004 | direct_lookup | Stated verbatim in §2.2, §6.2. |
| q005 | direct_lookup | Stated verbatim in §1. |
| q006 | direct_lookup | Stated verbatim in §1. |
| q007 | direct_lookup | Stated verbatim in §1 §3.2. |
| q008 | direct_lookup, identifier_exact | Stated verbatim in §2.1 (8-B row). |
| q009 | direct_lookup, identifier_exact | Stated verbatim in §3 / §6.1. |
| q010 | direct_lookup | Stated verbatim in §4 header. |
| q011 | direct_lookup | Stated verbatim in §2 ("Total entries: 39"). The 39 figure is explicit; the qualifier "including the duplicate" is in §2.1 last sentence. |
| q012 | direct_lookup | Stated verbatim ("38 distinct students" implicit; §2 says 39 entries with a Vinokur duplicate, and §3.1 / §8 say 38 distinct). |
| q013 | direct_lookup | Stated verbatim in §6.1 ("Distinct students: 38"). |
| q014 | direct_lookup | Stated verbatim in §2.1 (7-A row, "6 entries"). |
| q015 | direct_lookup | Stated verbatim in §6.1 (7-A count column "4"). |
| q016 | direct_lookup | Stated verbatim in §6.1 (7-C count column "7"). |
| q017 | direct_lookup | Stated verbatim in §6.2 ("Counting chaperones: 4") and §7. |
| q018 | direct_lookup | Stated verbatim in §6.2 ("Total adults: 5"). |
| q019 | composition | Requires reading §8 (stable-composition observations) — explicitly stated there. A parser that reads only §6.1 and not §8 still has 38 = 38 across versions, but the answer "no, it didn't change" is in §8. |
| q020 | composition | Stated explicitly in §8 ("The 7th-grade total student count is 18 in every version"). |
| q021 | composition | Stated explicitly in §4 (CN-02 step 3). |
| q022 | composition | Stated explicitly in §5 (CN-03 step 1). |
| q023 | composition | Stated explicitly in §2 ("STU-1063 Vinokur appears in both 7-A and 7-B") and §4 (CN-02 step 1). |
| q024 | composition | Stated explicitly in §4 ("The registrar's authoritative homeroom for STU-1063 is 7-B"). |
| q025 | composition | Stated explicitly in §3 (CN-01 step 1). |
| q026 | composition | Stated explicitly in §4 (CN-02 step 2). |
| q027 | composition | Stated explicitly in §4 ("Marrero remains on the trip; this change does not affect attendance"). |
| q028 | composition | Stated explicitly in §5 (CN-03 step 2) and §6.3. |
| q029 | direct_lookup | Stated verbatim in §2 header. |
| q030 | direct_lookup | Stated verbatim in §5 header. |
| q031 | direct_lookup | Stated explicitly in §1 §3.4 plus §2.2 / §6.2 ("No (per §3.4)"). |
| q032 | derived_count | §3.2 states the formula ⌈students ÷ 10⌉. For 38 students: 4. The number "4" is also stated in §2.2 / §7 explicitly. Mostly direct. |
| q033 | composition | Source explicitly states "The v1.0 roster does not meet §3.2" in §2.2 and "No" in the §7 compliance log row for v1.0. Direct lookup of compliance status. |
| q034 | composition | Source explicitly states "Compliant" in §5.1 and "Yes" in the §7 compliance log row for v1.3. |
| q035 | derived_count | Source explicitly states "compliance status flipped three times" in §7 last paragraph. Direct lookup of a derived figure. |
| q036 | direct_lookup | Stated verbatim in §4 first paragraph. |
| q037 | direct_lookup | Stated verbatim in §4. |
| q038 | unresolved | Stated verbatim in §9 first bullet. The deadline 17:00 on 2026-05-21 is direct; the unresolved status at packet close 17:00 on 2026-05-21 is direct. |
| q039 | direct_lookup | Stated verbatim in §9 third bullet ("Per §3.5, Lopez does not count toward §3.2 unless added to the trip-day manifest. As of packet close Lopez is not on the manifest"). |
| q040 | negative_existential | Wu does not appear in §6.1's 7-C row (Stahl is in Wu's slot). Source also states Wu withdrew in §4. Direct. |

## Self-flagged leakage

- **q011 vs. q012.** Both answers are explicit in source. The trap is whether the parser distinguishes "entries" from "distinct students". A parser that picks one number for both will fail one of them.
- **q014 vs. q015 (and q016).** Both answers are explicit. The trap is identifying the right version. v1.0 and v1.3 have different per-homeroom counts and the parser must use the right table.
- **q035.** Compliance-flip count is stated verbatim in §7. A parser that re-computes from §7's table can also derive 3. Direct lookup.
- **q032.** The formula ⌈38 ÷ 10⌉ = 4 is one operation away from full lookup; both the formula and the result are in source.
- **q019** is a stable-aggregate-changing-composition question. The "no, didn't change" half is in §8. The "but composition shifted" half is also in §8. A parser can pass q019 by quoting §8 verbatim, but will still need real composition tracking for q021–q028.
- **§7 compliance log table** leaks the answer to q033, q034, and q035 in tabular form. This is intentional — the compliance log is the kind of artifact a real audit packet would contain — but the leakage means q033/q034/q035 are not stress tests of compliance computation, only of compliance-table reading. A separate test that hides §7 would test the derivation.
- **Naming-collision risk.** Mr. J. Donovan (parent chaperone, withdrew in CN-02) and STU-1104 Dovland (student in 7-B) are distinct entities with similar names. The source spells them differently throughout (Donovan vs. Dovland). A parser that fuzzy-matches names may merge them. None of the 40 questions tests this directly, but a stricter test set could.

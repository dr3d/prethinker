# Anti-Leakage Manifest — temporal_state_ledger

For each question, this manifest records whether the reference answer is stated verbatim in source.md, requires derivation, or both. "Stated verbatim" means a parser that does pure substring lookup could plausibly find the answer without reasoning. "Derivation required" means the parser must combine ≥2 source statements or perform arithmetic.

| q | tag | leakage notes |
|---|---|---|
| q001 | direct_lookup | Stated verbatim in §2 (E-02 row) and §6 (Notification cross-reference). |
| q002 | direct_lookup, identifier_exact | Stated verbatim in §2, §4, and §6. Tests exact identifier reproduction (LFT-2026-05-04, including hyphens). |
| q003 | direct_lookup | Stated verbatim in §2 and §6. |
| q004 | direct_lookup | Stated verbatim in §2 and §6. |
| q005 | direct_lookup | Stated verbatim in §2 (E-04 row, parenthetical "cause: power supply fault") and §3.3. |
| q006 | direct_lookup | Stated verbatim in §3.3 ("routine sampler maintenance"); §2 row says "routine sampler maintenance window opens". |
| q007 | direct_lookup | Stated verbatim in §0 header and §8. |
| q008 | direct_lookup | Stated verbatim in §8 only. Tests whether parser indexes the personnel section. |
| q009 | direct_lookup | Stated verbatim in §8 only. |
| q010 | direct_lookup | Stated in §2 note on E-04 ("post-event review on 2026-05-02") and §8. Direct. |
| q011 | direct_lookup | Stated verbatim in §2 (corrected column) and §3.3. |
| q012 | direct_lookup | Stated verbatim in §2 (as-logged column). |
| q013 | direct_lookup, derived_time | Stated verbatim in §2 (E-10 row) and §3.4 ("Requirement met at 2026-05-01 17:00"). The accompanying explanation requires composition of §6.1, §6.2a, and §3.4 segment durations. |
| q014 | direct_lookup | Stated verbatim in §2 (E-11 row) and §4 (implicit; §6.3 clock starts from §6.1-met, but the packet's E-11 row records 17:30 as the log entry). The reference answer cites E-11 explicitly. |
| q015 | direct_lookup, derived_time | Stated verbatim in §4 ("therefore falls at 2026-05-03 17:00, a Sunday"). A parser that derives directly from §6.1 met + 48 hours can also produce this. |
| q016 | direct_lookup, derived_time | Stated verbatim in §4 ("adjusted deadline is therefore 2026-05-04 at 17:00"). A parser that applies §6.3 weekend shift can also derive. |
| q017 | direct_lookup | Stated verbatim in §3.1 ("6 days, 4 hours"). |
| q018 | direct_lookup | Stated verbatim in §3.2 ("6 days, 3 hours, 30 minutes"). |
| q019 | direct_lookup | Stated verbatim in §3.3 ("10 hours, 35 minutes"). |
| q020 | direct_lookup | Stated verbatim in §3.3 ("Duration: 2 hours"). |
| q021 | direct_lookup | Stated verbatim in §3.4 ("Pause: 2026-05-01 09:00 to 2026-05-01 11:00"). |
| q022 | derived_count | Requires reading §3.3 and recognizing two distinct intervals; the count "two" is implicit (two bullets). Source does not explicitly state "two intervals". |
| q023 | derived_count | Requires reading §2 and counting positive E. coli detections (E-01, E-06). Source does not state the count "two positive samples". |
| q024 | derived_count | Requires reading §2 or §6 and counting BWN, RUN, LFT issuances. Source does not state the count "three". |
| q025 | direct_lookup | Source says "Twelve entries above correspond to thirteen events" — the row count of 13 is explicit. (Trap: a parser that locks onto "twelve entries" will answer 12.) |
| q026 | derived_count | §7 lists three bullet items. Count "three" is implicit. |
| q027 | direct_lookup | Stated verbatim in §9 snapshot row. |
| q028 | direct_lookup | Stated verbatim in §9 snapshot row ("Lifted"). |
| q029 | direct_lookup | Stated verbatim in §9 snapshot row ("Paused (18 hr counted)"). Cross-checks against §3.4 segment math. |
| q030 | direct_lookup | Stated verbatim in §9 snapshot row ("Operational"). |
| q031 | composition | Requires reading §5 in full. Source explicitly states "should not be cited as an announcement, schedule, or commitment". A parser that reads only §2 and §6 will not encounter this disqualifier. |
| q032 | composition | Requires linking §5 (projection on 2026-04-29 16:00, conditional on no further positive samples) to §2 (E-06 positive at 2026-04-30 09:00). Source states the link in §5: "supersedes the projection". |
| q033 | direct_lookup | §1 §6.5 is the named rule. Direct. |
| q034 | direct_lookup | §1 §6.2a is the named rule. Direct. |
| q035 | direct_lookup | §1 §6.3 (the weekend/holiday clause) is the named rule. Direct. |
| q036 | unresolved | §7 explicitly states "expected by 2026-05-19" and "has not yet issued". Direct. |
| q037 | unresolved | §7 explicitly states "scheduled for 2026-05-13" and "has not been issued". Direct. |
| q038 | composition | Requires reading §1 §6.2a ("does not constitute a positive sample and does not trigger §6.2") and applying it to E-08 / E-09. Source states the rule but does not explicitly say "the maintenance window did not trigger §6.2". Genuine derivation. |
| q039 | composition | Requires reading §6 ("not a separate Lift Notice") and applying. Source states the disqualifier directly. |
| q040 | direct_lookup | §4 explicitly states "the Authority would have missed the original Sunday deadline by 19 hours". Direct lookup of a derived figure. |

## Self-flagged leakage

- **q040** is presented in the strategy as a compound-hard arithmetic question, but the answer is stated verbatim in §4. A parser that does pure substring lookup will pass q040 without doing the arithmetic. The question is preserved because the verbatim phrase tests exact-string fidelity ("19 hours") and a parser that paraphrases or re-derives might produce "approximately 19 hours" or "19 hours and 0 minutes", which an exact-match grader would mark wrong. Use as fidelity test, not as derivation test.
- **q025** is a row-count question and the source contains the trap phrase "Twelve entries above correspond to thirteen events". The reference answer accepts 13. If the grader wants to test for the trap, q025 is the cleanest place.
- **q014**: §6.3 strictly speaking starts at §6.1-met (17:00), not at the operations log entry (17:30). The source's E-11 row records 17:30 as "§6.3 48-hour clock starts" — this is a slight imprecision in the source. The reference answer follows the source (17:30) but a strictly rule-based parser may answer 17:00 and be marked wrong by the grader. **Flagged for spec-author review.** The unshifted deadline q015 and shifted deadline q016 are derived from 17:00, not 17:30, in the source's own §4 derivation, so the source is internally inconsistent on this 30-minute point. Recommended grader behavior: accept either 2026-05-01 17:00 or 2026-05-01 17:30 for q014.
- **q029** verbatim leaks the §6.2a pause state and the 18-hour count. A parser that does not read §9 (snapshot table) but does read §3.4 can still derive: 15:00 to 09:00 = 18 hours.
- **q036, q037**: open-item answers are stated verbatim in §7. The unresolved category is preserved because the question requires the parser to *not* invent a finding; the leakage tag is direct_lookup of the unresolved status itself.

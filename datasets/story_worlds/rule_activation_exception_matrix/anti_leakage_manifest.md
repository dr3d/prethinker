# Anti-Leakage Manifest — rule_activation_exception_matrix

This manifest discloses, per question, whether the reference answer is **stated verbatim** in source.md, **derived** from source content, or **partially derived**. Verbatim items are still useful as exact-string fidelity tests but are NOT derivation tests. Derivation-dependent items are the real signal.

## Per-question disclosure

| Q | Tag | Verbatim? | Notes |
|---|-----|-----------|-------|
| q001 | direct_lookup | YES | "$25,000" appears in §5.1 and in the program summary. |
| q002 | direct_lookup | YES | "NAICS major group 72" appears in §3.1. |
| q003 | direct_lookup | YES | "+15%" appears in §3.2. |
| q004 | direct_lookup | YES | "+25%" appears in §3.1. |
| q005 | direct_lookup | YES | "35%" combined cap appears in §3.4. |
| q006 | direct_lookup | YES | Application deadline 2026-04-30 stated in §1 and timeline. |
| q007 | direct_lookup | YES | Award announcement 2026-06-15 stated in timeline. |
| q008 | direct_lookup | YES | "2 FTE" lower bound in §2.4. |
| q009 | direct_lookup | YES | "25 FTE" upper bound in §2.4. |
| q010 | direct_lookup | YES | "$1,000" tax threshold in §2.5. |
| q011 | composition | NO | Requires binding App-014 incorporation date 2024-08-15 to §2.1's 12-month rule against application deadline 2026-04-30. |
| q012 | composition | PARTIAL | The §3.4 cap value (35%) is verbatim; whether the cap *engages* requires deriving 25%+15%=40% > 35%. |
| q013 | composition | YES (result) | "$33,750" appears in App-014's review block. Useful as exact-string but not a derivation test. |
| q014 | composition | NO | The unrealized "$35,000" / 40% counterfactual is NOT in source. Must be derived from base × (1 + 0.25 + 0.15). High-signal derivation question. |
| q015 | composition | NO | Requires Borden-incorporation-date arithmetic; App-019's Borden incorporation is 2025-09-12, less than 12 months before 2026-04-30. |
| q016 | composition | PARTIAL | §4.1's cross-county clock continuation is in rule text; applying it to App-019's 2024-02 prior-county incorporation requires the addition. |
| q017 | unresolved | YES (status) | "PENDING — §4.3 determination outstanding" appears in the App-019 review. Useful as exact-string; the parser must resist resolving it. |
| q018 | composition | NO | Requires checking App-021's NAICS (812) against §4.2's NAICS-72 gate. The gate text is verbatim; the binding is derivation. |
| q019 | direct_lookup | YES | "DENIED" status in App-021 review. |
| q020 | composition | PARTIAL | §4.2's three conditions are enumerated verbatim; binding all three to App-027's facts (sole prop, NAICS 722410, 18.3 months) is derivation. |
| q021 | composition | NO | Requires confirming App-027 NAICS 722410 ⊂ NAICS 72. |
| q022 | direct_lookup | YES | App-027 owner classification stated in review. |
| q023 | direct_lookup | YES | "$33,750" stated in App-027 review (same value as App-014 because both hit the §3.4 cap). |
| q024 | composition | PARTIAL | Pellicano's $1,200 outstanding tax is verbatim; the 23-days-late §4.3 arithmetic is derivation. |
| q025 | composition | PARTIAL | Kintaro's 1 FTE and 16.8 months are verbatim; the §4.2-unavailable conclusion requires conjunction-failure reasoning. |
| q026 | derived_count | YES | "Six applications" stated in §6 summary. |
| q027 | derived_count | YES | "2 approved" stated in §6 summary. |
| q028 | derived_count | YES | "3 denied" stated in §6 summary. |
| q029 | derived_count | YES | "1 pending" stated in §6 summary. |
| q030 | derived_count | YES | "$67,500 total approved" stated in §6 summary. **Useful as exact-string but NOT a sum-derivation test.** |
| q031 | authority | YES | §3.4 stated as the cap rule. |
| q032 | authority | YES | §4.2 stated as the floor-waiver rule. |
| q033 | authority | YES | §4.1 stated as the cross-county clock-continuation rule. |
| q034 | authority | YES | §4.3 stated as the cure rule. |
| q035 | unresolved | PARTIAL | The unresolved status is stated; the *specific* unresolved question (Tax Office confirmation that 2026-03-28 plan entry is ≥30 days before 2026-04-30) requires arithmetic to articulate (33 days, but only if confirmed). |
| q036 | derived_time | YES | "2026-03-31" stated as the §4.3 cure deadline in §4.3. |
| q037 | direct_lookup | YES | "2026-05-29" expected confirmation date stated in App-019 review. |
| q038 | negative_existential | NO | Requires recognizing that App-021's §2.4 denial precedes §3 evaluation. |
| q039 | negative_existential | PARTIAL | Pellicano's NAICS 811 is verbatim; §4.2's NAICS-72 gate is verbatim; the negative conclusion is derivation. |
| q040 | negative_existential | PARTIAL | Kintaro's lack of relocation is implicit (no relocation mentioned in App-042). The negative conclusion requires recognizing §4.1 simply does not apply (no trigger condition). |

## Verbatim count

- **Pure verbatim (no derivation):** q001–q010, q013, q017, q019, q022, q023, q026–q034, q036, q037 → 26 questions.
- **Partial derivation:** q012, q016, q020, q024, q025, q035, q039, q040 → 8 questions.
- **Full derivation:** q011, q014, q015, q018, q021, q038 → 6 questions.

## Implication for scoring

A parser that simply does string-matching against the source can score ~65% on this fixture without any rule-graph reasoning. The discriminating questions are the 6 full-derivation items plus the 8 partial-derivation items, weighted toward q014 (counterfactual cap arithmetic), q020 (§4.2 conjunction), q025 (Kintaro §4.2 unavailability), q038 (gating order), and q040 (rule-non-applicability vs. rule-denial distinction).

## Known leakage to flag

- **q030 leaks via §6 summary:** the total approved dollars ($67,500) is stated explicitly. A genuine sum-derivation test would require a variant fixture where the summary block is removed. Flag for variant generation.
- **q017 status leak:** the word "PENDING" and the §4.3 reason are written together in the review. A parser cannot avoid this. Flag if a stricter unresolved-detection variant is needed: redact the disposition line and require the parser to infer pending from the missing determination.
- **q013 and q023 amounts leak:** both $33,750 values appear verbatim in their review blocks. These are exact-string tests, not arithmetic tests. q014's counterfactual ($35,000) is the corresponding derivation question and is NOT in source.

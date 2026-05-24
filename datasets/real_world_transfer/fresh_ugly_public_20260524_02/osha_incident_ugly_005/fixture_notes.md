# Fixture notes — osha_incident_ugly_005

## What this document pressures

This fixture combines a recent (April 2026) OSHA news release with a prior (2024–2025) OSHA inspection record for the same employer at the same Cape Cod locale. The combination probes cross-document arithmetic, count reconciliation, and implicit-link inference.

### Multi-year date chronology (q006–q010)
The fixture spans 12/20/2024 (prior inspection opened) through 04/01/2026 (news release), with intermediate anchors at 02/04/2025 (prior citations issued), 02/26/2025 (prior citations contested), 07/16/2025 (prior case closed via formal settlement), and 11/18/2025 (fatal trench collapse). Models must compute four distinct intervals: 46 days (inspection-open → issuance), 22 days (issuance → contest), 125 days (case closed → fatal incident), and 134 days (fatal incident → news release). The 134-day calculation specifically requires the model to know that 2026 is not a leap year (February = 28 days, since 2024 was the most recent leap year and 2028 will be the next).

### Headline-vs-body count reconciliation (q021)
News release headline: "7 willful, 33 repeat violations" → 40 implied.
News release body: "seven willful citations, 33 repeat, and 17 serious violations" → 57 actual.
The headline omits the 17 serious citations. Pipelines that latch onto the headline number will be off by 17.

### Sub-headline rounding (q022)
Sub-headline: "$4.6M in proposed penalties."
Body: "$4,699,362 in proposed penalties."
The sub-headline uses a floor/truncation convention rather than round-to-nearest (which would yield $4.7M). This probes whether the model recognizes which rounding rule was applied.

### "Citation has been deleted." convention (q014, q015, q020)
OSHA's IMIS uses a specific note text "Citation has been deleted." to record citations withdrawn during settlement. Two of three items in inspection 1794687.015 have this note (01001B and 02001). The third item (01001A) had its penalty reduced but not deleted ($11,585 → $6,950). q020 forces explicit reconciliation between deletions in the items table and the resulting Current Violations count (1) in the Summary table.

### Initial vs Current column accounting (q013, q023)
After formal settlement:
- Initial Violations: 2 (Serious + Other grouped)
- Current Violations: 1 (only Other)
- Initial Penalty: $13,240
- Current Penalty: $6,950
The Other column's Current Penalty of $6,950 equals the Total column's $6,950 because all other columns are $0 after settlement. q023 forces verification of the column-total relationship.

### "F - Formal Settlement" Latest Event (q015, q016)
This is a rarely-encountered Latest Event code in OSHA inspection records; most cases show "Z - Penalty Payment" or "C - Contested." All three items in inspection 1794687.015 show "F - Formal Settlement," indicating the case closed via written settlement agreement rather than affirmance or contest resolution.

### Implicit cross-document link (q024)
The 2026 news release describes the fatal incident as occurring at "a Yarmouth worksite" with no street address. The prior inspection lists 174 South Shore Drive, South Yarmouth, MA 02664. Although third-party news coverage links the 2025 fatal cave-in to a worksite "on South Shore Drive, near Parker's River Beach" — possibly identical to the inspection's address — the OSHA source documents themselves do NOT explicitly identify the two worksites as the same location. q024 tests whether the model recognizes that the link is implicit and not stated in the source.

### Multiple media contacts with shared phone (q004)
Three media contacts on the news release: Eric R. Lucero (678-237-0630), Erika Ruthman (same 678-237-0630), and Juan Rodriguez (different 972-850-4709). The 678-237-0630 number is the OSHA Atlanta regional office line shared by two contacts. The 972-850-4709 number is for a separate contact at OSHA Dallas regional office. q004 forces enumeration of all three with attention to the duplicate phone.

### Negative-finding probe on 2026 citation timing (q017)
The news release announces $4.6M in proposed penalties but does NOT state: (a) the citation issuance date, (b) the abatement deadline, or (c) any contest status. q017 tests whether the model correctly reports the source's silence on these points rather than confabulating dates.

### Worker-outcome enumeration (q018)
The news release describes "two workers" trapped, "one worker engulfed" with fatal injuries, and "another" seriously injured — implying 1 fatality + 1 serious injury out of 2 trapped. The news release does not describe a third worker who escaped (though some media reports do). The fixture preserves only what the news release says. q018 probes recovery of the exact source counts.

### Penalty-history ratio (q025)
2026 proposed penalty / 2024–2025 initial penalty = $4,699,362 / $13,240 ≈ 354.94 ≈ 355x. The dramatic increase illustrates how OSHA's per-violation penalty maximums multiply when violations are classified as Willful or Repeat rather than Other or Serious. q025 tests whether the model performs the ratio calculation and articulates the enforcement-history implication.

### Bullet-list extraction (q011)
The news release contains a seven-bullet category list. q011 forces extraction in source order. Pipelines that re-order alphabetically, alphabetize within categories, or drop the trailing "electrical and fall hazards" composite item will fail.

# Fixture notes — osha_incident_ugly_004

## What this document pressures

This fixture pairs an OSHA national news release with the underlying OSHA inspection-detail page (IMIS Establishment Search), so QA can stress how official OSHA records and the announcing press release describe the same case in different ways.

### Violation-count reconciliation: 16 vs 9 (q021)
The news release says "16 safety violations" but the OSHA Violation Summary says 9. Both are correct in their own counting convention:
- 16 = total line items in the violation-items table (some citations have A/B sub-items)
- 9 = distinct citation numbers (2 Serious + 6 Willful + 1 Repeat)

Pipelines that pick a number without explaining the convention will be wrong half the time. q021 forces the reconciliation.

### Grouped sub-item $0 sub-rows (q025)
Seven items in the table show standard 1910.147(d) at $0. They are paired with a sibling A subpart that holds the per-violation penalty for the same citation number. This is OSHA's grouped-citation accounting; the fixture stresses recognition of the convention.

### Identifier recurrence and standards aliasing (q012, q024)
The same standard (1910.147(c)(4)(i), written as "19100147 C04 I" in IMIS) is cited 7 times (1 Serious + 6 Willful), and the willful citations carry a uniform $165,514 penalty. q022 forces arithmetic verification that 6 × $165,514 = $993,084, matching the Willful column total in the Violation Summary.

### Same-amount-different-party probe (q023)
$33,100 appears (a) as Taylor Farms' Serious-class column total in the Violation Summary and (b) as PL Solutions Group's entire proposed penalty in the news release. The coincidence is meaningful only when the model preserves the party attribution.

### Negative finding probe on victim identity (q018)
Both sources are silent on the worker's name, age, or other identifying details. The news release says only "a worker" and "the fatality." OSHA inspection-detail has no narrative section. Models that hallucinate details fail q018.

### Field blanks vs zeros (q011, q016)
- Violation Summary row "Initial Violations" / "Current Violations" — the "Other" and "Unclass" columns are blank, not zero. The penalty rows below are explicit "$0."
- Case Closed field is blank. SIC field is blank. Health column entries in Related Activity are blank. Pipelines that conflate blank with zero or with "not present" will miss subtle structural cues.

### Standard's "C - Contested" status across all 16 items (q016, q017)
The same Contest Date (12/08/2025) appears for all 16 items, and the Latest Event "C - Contested" repeats 16 times. This is structurally redundant but factually significant: the entire citation package was contested at once.

### Cross-document field alignment (q002, q003)
- Employer name: "Taylor Farms New Jersey, Inc." (inspection header, with comma) vs "Taylor Farms New Jersey Inc." (news release, no comma).
- Parent company appears only in news release: "subsidiary of Taylor Fresh Foods Inc."
- NAICS code appears only in inspection detail: "311991/Perishable Prepared Food Manufacturing."
- Site address only in inspection detail: 406 Heron Drive.
- OSHA office only in inspection detail: Marlton Area Office.
- News release dateline ("WASHINGTON") differs from the field office (Marlton, NJ). Models that conflate "WASHINGTON" with the actual inspection office will misattribute the case.

### Calendar-day spans on real OSHA timelines (q007-q010)
The 178-day inspection duration (5/27 → 11/21), 27-day abatement window (11/21 → 12/18), 17-day contest window (11/21 → 12/08), and 3-day citation-to-news-release gap (11/21 → 11/24) all illustrate the calendar-day mechanics of OSHA enforcement.

### Case-status nuance
The case is OPEN, Case Closed is blank, all items are contested, and the news-release advisory says penalties may be adjusted. q016 tests whether the model recognizes that a contested OSHA case has provisional numbers that may not be final.

### Same Date Opened and Close Conference (q001)
Date Opened: 05/27/2025; Close Conference: 05/27/2025. The two fields share a date. q001 tests recognition that this is what the source actually says (rather than the more common pattern where the close conference happens later than opening).

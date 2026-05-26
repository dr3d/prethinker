# Fixture Notes — nlrb_ugly_001

## Source

- Public URL: https://www.nlrb.gov/cases-decisions/weekly-summaries-decisions/summary-of-nlrb-decisions-for-week-of-february-23-27-0
- Document type: NLRB weekly Summary of Decisions — informational compendium prepared by the Office of the Executive Secretary that lists Board decisions issued during a single Monday-through-Friday week, with brief narrative entries for each. Not itself a Board opinion; it summarizes Board opinions.
- Week covered: February 23 - 27, 2026
- Collected: 2026-05-26 (UTC)
- Note on FERC substitution: this fixture was originally slotted as ferc_ugly_001, but the FERC website returned 403 to direct fetches. I pivoted to a parallel federal regulator (NLRB) whose docs are publicly fetchable. Folder renamed from ferc_ugly_001 to nlrb_ugly_001; metadata and fixture_notes reflect the substitution.

## Why messy

- **Compendium format.** A single document containing multiple distinct decisions, each with its own caption, case numbers, location, date, and narrative. An extractor must treat each entry as a self-contained unit while preserving the document-level scope (week of Feb 23–27, 2026).
- **Three section types.** "Summarized Board Decisions" (4 substantive entries), "Appellate Court Decisions" (1 entry — Brown-Forman / 6th Cir.), and "Unpublished Board Decisions in Representation and Unfair Labor Practice Cases" (empty this week: "*No Unpublished Board Decisions Issued.*"). The empty section is a structural placeholder.
- **Two case-number formats.** Some cases cite an NLRB volume-and-number citation (374 NLRB No. 46; 374 NLRB No. 47); others only give the regional case number (14-CA-344872; 14-CA-294830, et al.). The former indicates a published, citable Board opinion; the latter indicates a no-exceptions adoption or otherwise unpublished disposition. Asymmetric citation formats within the same Summary.
- **Consolidated and "et al." case numbers.** "32-CA-160759 and 32-RC-109684" combines a charging case (CA) and a representation case (RC) under one decision. "14-CA-294830, et al." denotes multiple consolidated charges under one decision without enumerating them.
- **Multi-doctrine "d/b/a" caption.** "Browning-Ferris Industries of California, Inc. d/b/a BFI Newby Island Recyclery and FPR-II, LLC d/b/a Leadpoint Business Services" — TWO d/b/a entities in a single caption joined by "and." Each `d/b/a` is a "doing business as" alias; both legal entities and both DBA aliases must be preserved.
- **Skipped Roman numeral in case lineage.** The Summary cites "Browning-Ferris I" (2015) and "Browning-Ferris III" (2020) but not "Browning-Ferris II." The Roman numeral II is conspicuously absent, with no explanation — possibly because what would have been II was a D.C. Circuit opinion rather than a Board decision, or possibly a quirk in the Board's own retrospective labeling. The current 2026 decision is not numbered in the Summary; the law-firm commentary externally labels it Browning-Ferris IV but the Board does not.
- **"Law of the case" doctrine reference.** The Board explicitly invokes "law of the case" — i.e., the D.C. Circuit's remand instructions bind the Board on remand. This is a procedural-not-substantive justification for the outcome.
- **Express scope limitation.** The Board says "expressly limited the holding to the facts of the instant case." Narrow holding signal — the Board is not announcing a new general rule.
- **Same-section different-conduct violations.** GE Appliances: Section 8(a)(5) and (1) is violated by both (a) unilaterally changing pay and (b) delaying information provision. Same statutory section, two factually-distinct conducts.
- **Doctrinal pair on the same facts.** GE Appliances: Section 8(a)(5) and (1), "within the meaning of Section 8(d)," found on the same facts as both a "unilateral change" and a "midterm modification." Two doctrinal characterizations of one course of conduct.
- **Declined "novel monetary remedy."** Board declined to extend pay increases to all unit employees as remedy. Identifies the remedy as "novel." Remedy < violation scope.
- **No-exceptions adoption pathway.** Hoffmann Brothers entry shows the no-exceptions default path: ALJ decides → 28-day exception window → if no exceptions, Board adopts ALJ's findings/conclusions/recommended Order. Board does not name participating Members in these routine adoptions.
- **Partial summary judgment.** Starbucks entry: Board grants partial summary judgment on certain alleged violations (admitted by Respondent's answer), severs the rest for ALJ hearing. Bifurcated procedural posture.
- **Three-Member panel attribution.** "Chairman Murphy and Members Prouty and Mayer participated." Last-name-only convention. Same three-Member panel for all substantive decisions in this Summary. Full first names recoverable from the NLRB org chart but not provided in this Summary.
- **Multi-part union names.** "Sanitary Truck Drivers and Helpers Local 350, International Brotherhood of Teamsters"; "IUE-CWA, the Industrial Division of the Communications Workers of America, AFL-CIO, CLC"; "International Association of Sheet Metal, Air, Rail, and Transportation Workers, Local Union No. 36"; "Workers United, a/w Service Employees International Union." Parent/affiliate/local convention, with various comma punctuation, "a/w" (affiliated with), and AFL-CIO/CLC postfixes.
- **Multi-format dates within the week.** Each entry's date follows the case caption, e.g., "Milpitas, CA, February 23, 2026." Geographic location precedes the date; entry-level date may differ from the week-level range. Dates within the week: Feb 23 (×2), Feb 24, Feb 26 (×2 including 1 appellate). No entries on Feb 25 or Feb 27.
- **Italicized case names.** Entry-level case captions use italicized formatting in the source (rendered as `*...*` in source.md). Prior Board iterations within narrative also use italics. Citation styling matters for distinguishing case names from regular prose.
- **Appellate court citation format.** "Brown-Forman Corp. d/b/a Woodford Reserve Distillery, Board No. 09-CA-307806 (reported at 373 NLRB No. 145) (6th Cir. February 26, 2026)" — caption + Board case number + NLRB citation parenthetical + court + date parenthetical, all in one citation line.
- **Partial enforcement / partial denial.** Brown-Forman: Sixth Circuit "denied enforcement with respect to the Board's bargaining-order remedy and remanded" but "otherwise enforced the Board's findings of Section 8(a)(1) and (3) violations." Underlying violations stand; specific remedy does not.
- **Non-breaking hyphens in phone number.** The disclaimer phone number "202‑273‑1940" uses Unicode non-breaking hyphens (U+2011) rather than ASCII hyphens. Affects tokenization.
- **Empty section "*No Unpublished Board Decisions Issued.*"** Section header is present with explicit "none this week" content rather than absent. Distinguishes "no decisions" from "section not applicable."
- **Multi-decade litigation tracking.** Browning-Ferris lineage spans 2015 → 2020 → 2026 with two D.C. Circuit remands in between. 11-year span on a single case.

## What shapes are pressured

- Compendium document where each entry is a self-contained decision.
- Section taxonomy (Summarized Board / Appellate Court / Unpublished).
- Empty section as explicit "none" content vs. structural absence.
- Asymmetric citation format (NLRB volume-number vs. regional case number only).
- Consolidated case numbers (CA + RC; multiple-CA with et al.).
- Multi-doctrine d/b/a captions with two legal entities.
- Skipped Roman numeral in case lineage (I → III, no II).
- Law of the case doctrine driving reversal on the same record.
- Express scope limitation as narrow-holding signal.
- Same-section different-conduct violations.
- Two doctrinal characterizations on the same facts.
- Declined novel remedy with explicit "novel" label.
- No-exceptions adoption pathway (no panel named).
- Partial summary judgment with severance.
- Three-Member panel last-name-only attribution.
- Multi-part union name parsing (parent/affiliate/local, AFL-CIO/CLC postfix, a/w).
- Per-date count aggregation across a week.
- Italicized case names vs. regular prose.
- Appellate court multi-part citation format.
- Partial enforcement / partial denial of Board orders.
- Non-breaking hyphens in phone numbers.
- Multi-decade case lineage tracking with remand pingpong.
- "Brown-Forman" hyphenated proper noun vs. "Browning-Ferris" hyphenated proper noun (both in same Summary).
- Case-number prefix as region-office code (32-CA = Region 32 = San Francisco Bay area; 09-CA = Region 9 = Cincinnati; 14-CA = Region 14 = St. Louis; etc.). Implicit geographic semantics in the case-number prefix.

## Attachments, redactions, tables, missing fields

- Attachments: none in the Summary itself. Each entry links to the underlying Board decision via an "apps.nlrb.gov/link/document.aspx/..." URL (preserved in the source.md citation). Full Board opinions are separate documents not extracted here.
- Redactions: none.
- Tables: none.
- Missing fields: full first names of Board Members (recoverable from external org chart); ALJ first names for cases other than Hoffmann Brothers (the Starbucks entry, e.g., does not name the ALJ); specific NLRA section citations for Hoffmann Brothers (says "certain unfair labor practices" without specifying); exact text of recommended Orders; underlying factual records; the missing "Browning-Ferris II" identity.

## Extraction caveats

- Each Summary entry is a discrete decision. Do not merge attributes across entries.
- Distinguish "Summarized Board Decisions" (Board opinions) from "Appellate Court Decisions" (federal court rulings on prior Board decisions). The Brown-Forman entry is NOT a Board decision; it is a Sixth Circuit ruling on Board No. 09-CA-307806 (which was itself decided by the Board at 373 NLRB No. 145).
- Preserve the "Browning-Ferris I" / "Browning-Ferris III" naming as given. The Board itself does not number the present (2026) decision; do not fabricate "Browning-Ferris IV." Note the missing "II" in source view as a known gap.
- Preserve all d/b/a aliases. "Browning-Ferris Industries of California, Inc." (legal entity) and "BFI Newby Island Recyclery" (DBA) are not interchangeable; both must be retained.
- For Browning-Ferris, the petitioned-for unit consists of Leadpoint employees. Browning-Ferris is the joint employer of those Leadpoint employees. Do not flip the relationship.
- Bind "law of the case" to the D.C. Circuit's 2018 (first) and 2022 (second) remand instructions; the 2026 Board decision does not revisit the question of whether Browning-Ferris I applies because the Circuit has foreclosed that escape route.
- Bind "expressly limited the holding to the facts of the instant case" as a scope limitation. The Board is complying with a court order, not announcing a new doctrine.
- For GE Appliances, treat the two violation findings (unilateral pay change, delayed information) as TWO distinct findings, each under Section 8(a)(5) and (1). The unilateral pay change is additionally characterized as a Section 8(d) midterm modification on the same facts. The 8(d) characterization is descriptive, not a separate violation count.
- For Hoffmann Brothers, "certain unfair labor practices" is intentionally non-specific in the Summary; the specifics are in the underlying ALJ decision (Jan 5, 2026 by ALJ Andrew S. Gollin).
- For Starbucks, the partial-summary-judgment dispositive ruling and the severance for further proceedings are co-equal procedural outcomes. The Respondent's "answer admitted facts sufficient" is the basis for granting partial summary judgment.
- Brown-Forman: distinguish the appellate ruling (6th Cir.) from the underlying Board decision (373 NLRB No. 145). The Sixth Circuit enforced 8(a)(1) and (3) findings but denied enforcement of the bargaining-order remedy. The case returns to the Board on remand for further remedy proceedings.
- Three-Member panel: "Chairman Murphy and Members Prouty and Mayer participated." Preserve last-name-only convention; do not infer or supply full names from external knowledge unless the question explicitly asks for them.
- Treat the "*No Unpublished Board Decisions Issued.*" entry as a structural placeholder with explicit "none" content. Do not omit the section or treat it as "section absent."
- Phone number 202-273-1940 uses non-breaking hyphens in the source. Preserve verbatim; do not normalize to ASCII hyphens.
- Case-number prefixes (32, 09, 14) encode the NLRB Regional Office. Region 32 = Oakland/Bay Area (Milpitas, CA fits); Region 09 = Cincinnati (Louisville, KY fits); Region 14 = St. Louis (Brentwood, MO and Nichols Hills, OK fit — Region 14 is multi-state). Recover region-office identity only if asked.

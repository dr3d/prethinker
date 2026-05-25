# Fixture Notes — other_ugly_001

## Source

- Public URL: https://www.epa.gov/enforcement/meyer-distributing-clean-air-act-settlement-summary
- Collected: 2026-05-24 (UTC)
- Page last updated (per page footer): January 15, 2026
- Page first published (per metadata): January 10, 2025
- Page review date (per metadata): January 15, 2027

## Document type

EPA Office of Civil Enforcement settlement-summary web page. This is a summary page, not the consent decree itself; the consent decree (3.14 MB PDF) and complaint (2.57 MB PDF) are linked but not extracted. The page is the *primary regulator-authored explanation* of the settlement.

## Why messy

- **Section-structured prose with bulleted obligations.** The 8-bullet "In addition, the consent decree requires Meyer Distributing to:" list mixes negative obligations (refrain from X), affirmative obligations (notify, train), and structural obligations (destroy, forfeit). No bullet labels, no IDs.
- **Date inconsistency in the lead paragraph.** Announcement "January 10, 2025"; DOJ filing "Jan. 6th" with no year stated — the year (2025) must be inferred from context (announcement is four days later in 2025; PDFs labeled "2025-01").
- **30-day comment period without a stated start date.** The page tells you the duration but not when the clock starts; computing an end date requires external information.
- **Annualized vs. lifetime pollution figures.** NOx reductions stated two ways: 1,517 tons "on an annual basis" (broader settlement) vs. 1,484 tons "over 20 years" (tugboat replacement). Easy to wrongly add or compare.
- **Open list of vehicle manufacturers.** "numerous vehicle models, including diesel trucks manufactured by Ford, General Motors, and Stellantis" — "including" signals the list is illustrative, not closed.
- **Asymmetric remedy scope.** Defendant must destroy devices in its possession; officers must forfeit personal-possession devices; customers receive only notification. Easy to over-generalize the destruction obligation.
- **Open count.** "over 90,000 aftermarket defeat devices" is a floor, not an exact count.
- **Metadata drift.** DC.date.reviewed = 2027-01-15 is a future date relative to page collection; meta-article:modified_time = 2026-01-15; meta-DC.date.created = 2025-01-10. Three different "dates" on one page, not all of the same kind.
- **Typo preserved.** "particular matter" appears in the final sentence of the Environmental Benefits section where "particulate matter" is meant.
- **Comment period scope ambiguity.** The comment period and final court approval are gating events; the consent decree is described as "proposed" — at extraction time the decree was not yet final.

## What shapes are pressured

- Open-list vs. closed-list extraction (manufacturers list with "including"; section "On this page" enumeration).
- Multi-bullet obligation extraction with mixed obligation polarity (refrain/ensure/deny/refrain/notify/notify/require/provide).
- Date arithmetic where one operand is missing (30-day comment period, no start date).
- Source-coordinate questions across labeled sections (About / Violations / Impacts / Benefits / Decree / Comment Period / Contact).
- Per-unit derivation (penalty per device) where the source does not perform the arithmetic and the count is a lower bound.
- Time-base normalization (annual vs. 20-year totals for the same pollutant).
- Metadata-vs-body date consistency (modified, published, reviewed, last-updated).
- Asymmetric remedy attribution (defendant / officers / customers).
- Provisional / pending status of a "proposed" consent decree.
- Forward-scheduled review timestamp interpretation.

## Attachments, redactions, tables, missing fields

- Attachments: Consent Decree PDF (3.14 MB, not extracted here), Complaint PDF (2.57 MB, not extracted here), Press Release (separate URL, not extracted here).
- Redactions: none.
- Tables: none; bulleted lists in two places (Settlement Resources; the "In addition" obligation list).
- Missing fields on this page: docket number; case caption; assigned judge; civil action number; effective date of the consent decree (none stated; pending final court approval); start date and end date of the 30-day public comment period; total number of customers to be notified; deadline for compliance training; deadline for customer notifications; deadlines for tugboat retirement and replacement.

## Extraction caveats

- Treat the consent decree as **proposed**, not entered. Do not assert effectiveness without the court-approval predicate.
- Preserve "Jan. 6th" without a year as a partial date; year is inferable from context but should be tagged as inferred, not extracted.
- Bind "over 90,000" as a lower-bound count; do not treat it as exact.
- Preserve "including" semantics: the three named manufacturers (Ford, GM, Stellantis) are illustrative, not exhaustive.
- Bind annualized pollution figures (1,517 t NOx etc.) to the *settlement as a whole*, not specifically to the tugboat SEP; bind the 20-year figures (1,484 t NOx, 19 t PM) to the *tugboat SEP only*.
- Bind the destruction obligation to "in its possession or control" (defendant); the forfeiture obligation to officers' "possession or installed on any motor vehicle they own or operate"; the customer-side requirement is *notification only* on this page.
- Distinguish three timestamp fields: DC.date.created (2025-01-10), DC.date.modified (2026-01-15), DC.date.reviewed (2027-01-15). Only the first two reflect actions taken; the third is a forward-scheduled review target.
- Preserve "particular matter" verbatim where it appears in the final sentence of Environmental Benefits; do not normalize to "particulate matter."
- Treat the contact attorney (Ed Kulschinsky) as an information contact for the settlement, not a signatory of the consent decree — the page does not provide signatories.
- Do not infer the per-device penalty as a stated fact; if computed, label as a derived figure with the lower-bound caveat.

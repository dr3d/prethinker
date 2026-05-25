# Fixture notes: sec_ugly_003

## Source

- Public source URL: https://www.sec.gov/Archives/edgar/data/1046311/000119312526232581/d228027d8k.htm
- Source family: SEC EDGAR Form 8-K
- Registrant: Choice Hotels International, Inc. (ticker CHH)
- Date of report (date of earliest event reported): May 20, 2026
- Filing date: May 20, 2026
- Collection date (UTC): 2026-05-24

## What this is

A Choice Hotels Form 8-K reporting the sudden CEO transition: Patrick S. Pacious steps down as President & CEO; Dominic E. Dragisich, the Chief Growth & Strategy Officer, becomes Interim CEO; a search committee is established for a permanent CEO. Exhibits: 10.1 (Separation Agreement), 99.1 (Press Release), 104 (XBRL). Only Item 5.02 and Item 9.01 are filed. The Item 5.02 narrative includes a five-bullet severance schedule for Pacious and a Dragisich biographical paragraph showing four roles at the Company over nine years.

## Why this document is messy

1. **XBRL-style bullet cover page.** Rather than the traditional cover-page table layout (see sec_ugly_001 and sec_ugly_002), this 8-K's cover renders as flat bullets keyed to XBRL element names: "Entity Incorporation State Country Code — 2026-05-20 to 2026-05-20: Delaware." This is the inline-XBRL data view, not the human-readable cover. The "2026-05-20 to 2026-05-20" effectivity range is the same for every field. An extractor must treat these as point-in-time facts, not as duration-keyed facts.

2. **Five-bullet severance schedule with embedded date carve-outs.** Each of the five bullets uses table-row syntax (`| • | text | --- | --- |`) — each bullet is rendered as its own one-cell-plus-bullet-cell table. The bullets carry multiple date-sensitive constraints: "after May 5, 2011" (equity-award eligibility cutoff), "August 31, 2026" (Transition Period end and likely Separation Date), "September 30, 2032" (health-premium cutoff), "through 2037" (Stay at Choice end). An extractor that fails to bind each date to its specific bullet conflates entitlements.

3. **"Separation Date" definition embedded mid-bullet.** The term `(the "Separation Date")` is defined parenthetically inside the second severance bullet. This means subsequent bullets that reference "Separation Date" (e.g., the health-premium bullet) depend on a definition introduced earlier in the same list. Tabular extractors that process bullets independently lose this dependency.

4. **Conditional triggers.** Several benefits are conditional: continued employment through December 31, 2026 for Dragisich's cash bonus; non-coverage under another plan for Pacious's health premiums. These conditions are easy to miss in extraction.

5. **Reference to a prior Severance Benefit Agreement (May 24, 2022) that is not attached.** The benefits package is described as "substantially the same" as the 2022 agreement. The 2022 agreement is not Exhibit 10.1; only the new Separation Agreement is. An extractor that follows references will hit a dead end.

6. **Multiple short-tenure roles for Dragisich.** Four roles over nine years, with the most recent (Chief Growth & Strategy Officer) lasting only ~57 days. The pattern is suspicious: CGSO appears to have been a transitional title in anticipation of the Interim CEO appointment. The 8-K does not flag this.

7. **Possible date gap in Dragisich's bio.** Role 2 (EVP/CGBO) ends "March 2026" with no day specified. Role 3 (CGSO) starts March 24, 2026. The gap (if any) is unresolved.

8. **Bilateral release of claims.** "Each of the Company and Mr. Pacious is providing a release of claims" — both parties release, not just the departing executive. This is structurally distinct from the more common one-way employee release.

9. **Pacious's dollar severance value is not computable from the 8-K.** Base salary and target bonus are not stated, so 200% × (base + target) is symbolic. An extractor that records "200%" without flagging the missing operands gives a misleading picture.

10. **"Furnished" vs. "filed" wording inconsistency.** The exhibit index lists Exhibit 99.1 simply as "Press Release of the Company, dated May 20, 2026" without the "furnished" disclaimer present in sec_ugly_001 and sec_ugly_002. The body text uses "furnished" once. The legal status of Exhibit 99.1 is therefore underspecified in this 8-K compared to typical practice.

11. **Ampersand vs. "and".** "President & Chief Executive Officer" uses an ampersand in the first paragraph; subsequent references use mixed forms. A name-canonicalization step that normalizes punctuation may produce different keys for the same title.

12. **No Item 7.01.** Unlike sec_ugly_001 and sec_ugly_002, this 8-K does not have a separate Item 7.01 for the press release; the press release is mentioned in passing inside Item 5.02 and listed under Item 9.01. An extractor that always expects an Item 7.01 section will not find one.

## Shapes this pressures

- **Heterogeneous cover-page formats.** Same SEC document type, three different cover-page representations across sec_ugly_001/002/003.
- **Multi-bullet schedule with cross-bullet definitions.** "Separation Date" defined in bullet 2, used in bullets 3 and 5.
- **Date carve-outs embedded in benefit clauses.** "after May 5, 2011," "August 31, 2026," "September 30, 2032," "through 2037" — each tied to a specific benefit.
- **Conditional entitlements.** Continued employment, non-coverage elsewhere.
- **Reference to prior agreement not in the exhibit set.** Dead-end cross-reference.
- **Multiple short-tenure roles indicating role-engineering.** Detect the implausibility.
- **Date gap in biographical record.** Resolve with limited precision.
- **Symbolic compensation (200% multiplier without operands).**
- **Bilateral release.** Different from common one-sided release.
- **Variable Item set.** Don't assume Item 7.01 exists.

## Attachments, redactions, tables, missing fields

- Attachments: Exhibit 10.1 (Separation Agreement; not extracted here); Exhibit 99.1 (Press Release; not extracted here); Exhibit 104 (XBRL).
- Redactions: none.
- Tables: cover-page XBRL bullets (multiple); Item-header tables; per-bullet table rows in severance schedule; exhibit-index table; signature block table.
- Missing fields: Pacious's base salary; Pacious's target annual bonus; the May 24, 2022 Severance Benefit Agreement itself; the exact end date of Dragisich's EVP/CGBO role; the disposition of Dragisich's CGSO title upon becoming Interim CEO; whether the $500,000 cash bonus survives early appointment to permanent CEO.

## Extraction caveats

- Treat each XBRL-style bullet as a (field_name, effective_date, value) triple; do not infer additional fields.
- Bind the Separation Date carve-out to bullet 2's definition; use that definition in bullets 3 and 5.
- Preserve "200%" as a multiplier without operands; do not invent base salary or bonus figures.
- Preserve "May 5, 2011" as a hard cutoff date for equity-award eligibility.
- Treat the bilateral release as bilateral; not a one-sided executive release.
- Preserve the four Dragisich roles as four separate role-states; note the possible CGSO-to-Interim-CEO overlap as unresolved.
- Treat references to the May 24, 2022 Severance Benefit Agreement as out-of-document references; do not assume its terms.
- Do not assume an Item 7.01 exists.

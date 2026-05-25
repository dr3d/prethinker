# Fixture notes: osha_ugly_002

## Source

- Public source URL: https://www.osha.gov/news/newsreleases/chicago/20260318
- Source family: OSHA national news release (Chicago regional office)
- Release number: 26-210-CHI
- Release date: March 18, 2026
- Collection date (UTC): 2026-05-24

## What this is

A regional-office OSHA news release issued from Chicago after a nitrocellulose drum explosion at SV Labs Prescott Corp., a California-based beauty and personal care products manufacturer with a facility in Prescott, WI. OSHA cited 2 repeat + 10 serious + 6 other-than-serious violations and proposed $275,694 in penalties. The employer has contested.

## Why this document is messy

1. **Headline/body location mismatch.** The headline calls the company a "Wisconsin beauty products manufacturer." The body identifies it as "California-based." The mismatch is not a contradiction — the headline references the incident-site state, the body references corporate domicile — but a naive extractor will treat one or the other as canonical and lose information.

2. **Duplicated lede.** The lede paragraph appears twice — once at the top of the release and once again after a section heading that restates the release title. A deduplicator must recognize that these are the same content, not two independent statements.

3. **Citation totals are not summed.** The release gives the three category counts (2 repeat, 10 serious, 6 other-than-serious) and the dollar penalty, but never states the total number of citations. The total (18) must be derived.

4. **No incident date.** The release does not state when the explosion occurred, when the inspection was opened, or when the contest was filed. Only the release issuance date is given. Many natural questions about timeline therefore require qualified "not stated" answers.

5. **Serious-violation hazard groups are not numerically broken out.** Five hazard areas are listed for the 10 serious citations, but the release does not say how many citations fall under each.

6. **Phone-number anomaly.** Erika B. Ruthman and Eric R. Lucero are listed with the same phone number (678-237-0630). Cross-checking against another OSHA release (26-574-ATL, the Yarmouth cave-in release) shows Ruthman's number listed there as 678-237-0631, suggesting a transcription error here. The single-document view cannot resolve this; the multi-document view can.

7. **Non-ASCII in name.** "Juan J. Rodríguez" contains a U+00ED character. Extractors that normalize to ASCII silently change identity.

8. **Section-heading restatement.** The release title is restated as a markdown H4 mid-document. A flat-text extractor risks treating this as a new section starting fresh content.

## Shapes this pressures

- **Headline vs. body extraction.** Which framing wins when the headline and the body locate the company differently?
- **Cross-document fact validation.** The Ruthman phone-number discrepancy can only be caught by joining against a sibling document.
- **Open-list extraction with grouped totals.** Five hazard subcategories under "10 serious violations" — open list, sum constraint, but no per-item count.
- **Absence-of-evidence answers.** Several Qs ask for dates the document simply does not contain. Honest answer must say so rather than fabricating.
- **Provisional fact tagging.** Paragraph 4 explicitly tells the reader penalty and citation counts may change. A KB that commits these as final has lost the disclaimer.
- **Headline normalization.** "Wisconsin beauty products manufacturer" → company identity? No, that's a descriptor, not a name.

## Attachments, redactions, tables, missing fields

- Attachments: none.
- Redactions: none.
- Tables: none.
- Missing fields: incident date, inspection-open date, contest-filing date, abatement deadline, per-subcategory serious-citation counts, per-subcategory OTS-citation counts.

## Extraction caveats

- Treat headline location and body location as orthogonal facts, not synonyms.
- Treat the second paragraph-1 occurrence as a duplicate of the first.
- Do not invent a total citation count without showing the arithmetic from the three category counts.
- Treat Lucero/Ruthman shared phone as suspicious until validated against another source.
- Treat "California-based" as a corporate-domicile claim, not a contradiction of the Wisconsin dateline.
- Preserve the "# # #" separator literally; it marks end-of-body and start-of-press-block.

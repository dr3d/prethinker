# Fixture notes: sec_ugly_001

## Source

- Public source URL: https://www.sec.gov/Archives/edgar/data/1641631/000149315226014676/form8-k.htm
- Source family: SEC EDGAR Form 8-K
- Registrant: Beyond Air, Inc. (ticker XAIR)
- Date of report (date of earliest event reported): March 26, 2026
- Filing date: April 1, 2026
- Collection date (UTC): 2026-05-24

## What this is

A Beyond Air, Inc. Form 8-K disclosing the resignation of CEO Steven A. Lisi and the appointment of Robert Goodman as his successor. The filing reports four Items: 1.01 (material agreement — Separation and Release), 5.02 (officer departure/appointment), 7.01 (Regulation FD — press release), and 9.01 (exhibits). Three exhibits: 10.1 (filed Separation Agreement), 99.1 (furnished press release), 104 (cover XBRL).

## Why this document is messy

1. **Untagged tables.** Multiple cover-page and Item-header tables carry the marker "*(untagged table — column alignment not verified)*". This is a structural caveat that the column-to-header binding may not match what a renderer would show. An extractor that assumes column 1 = state, column 2 = file number, column 3 = EIN must verify alignment from header text, not column position.

2. **Signature-block name mismatch.** The "/s/" line reads "Daniel Moorehead" but the printed "Name:" line directly underneath reads "Daniel Moorhead" — surname spelled differently across two adjacent rows of the same signature table. The 8-K does not resolve which is canonical. Sticky for any name-canonicalization pass.

3. **Missing colon in "Title" row.** Adjacent rows in the signature block use "By:" and "Name:" with colons; the "Title" row omits the colon ("Title Chief Financial Officer"). Tiny but representative of OCR/encoding inconsistency.

4. **Biographical sentence gap.** "...as Division President and Business Head of BioTel Care and Alliance from and Senior Vice President of Global Sales and Marketing at BioTel Research, helping scale..." — the word "from" hangs without a date or trailing phrase. The sentence is grammatically broken; preserve verbatim. Extractors that auto-fix grammar will alter the source.

5. **Same-day vs. next-day events.** Resignation notification: March 26, 2026. Resignation effective: March 27, 2026. Successor effective: March 27, 2026. Separation Agreement executed: March 27, 2026. Press release issued: March 26, 2026. The "date of earliest event reported" is March 26, but two of the five events occur on March 27. An extractor that collapses all of these to one date loses information.

6. **Item 1.01 by-reference cross-link.** Item 1.01 contains no substantive content of its own; it points to Item 5.02. A linearizing extractor must follow the pointer.

7. **Furnished vs. filed distinction.** The Item 7.01 disclosure language explicitly disclaims "filed" status under Section 18 of the Exchange Act. Extractors that treat all exhibits as equivalent lose this legal distinction.

8. **Forward-looking compensation commitment.** Mr. Goodman is appointed without compensation arrangements; the Company commits to negotiate and disclose later. The 8-K therefore creates an obligation to file a subsequent 8-K, but does not date it. Compensation values for Goodman are unknown.

9. **Negative-fact assertions vs. absence of disclosure.** "There are no family relationships..." and "there are no transactions ... that require disclosure" are positive assertions of non-existence, not silence. A KB that records "no information" loses the affirmative claim.

10. **Revocation Period definition.** The Revocation Period is defined as "seven business days from March 27, 2026, and excluding such date" — the "excluding such date" qualifier matters and is easy to miss in extraction. The calendar end date is not stated.

## Shapes this pressures

- **Multi-event 8-K with cross-item references.** Item 1.01 → Item 5.02; Item 7.01 → Exhibit 99.1; Item 9.01 → exhibit numbering.
- **Untagged table semantics.** Header row vs. data row must be inferred, not positionally assumed.
- **Same-named-person spelling drift within one signature.** Single-document name canonicalization.
- **Same-date / next-date event clustering.** Multiple events; one cover-page "earliest" date.
- **Filed-vs-furnished distinction.** Legal status of each exhibit differs.
- **Summary-qualified-by-full-text.** Standard SEC pattern; the body summary is non-binding if it conflicts with the full exhibit.
- **Forward-looking obligations.** "Will disclose in a subsequent report" creates a pending fact.
- **Negative-fact assertions.** Distinguish "no X exists" from "X not mentioned."
- **Date-derivation under exclusion clause.** "Seven business days from X, excluding such date" — off-by-one risk.

## Attachments, redactions, tables, missing fields

- Attachments: Exhibit 10.1 (Separation and Release of Claims Agreement, not included in this fixture extraction — referenced only); Exhibit 99.1 (Press Release, referenced only); Exhibit 104 (Cover Page XBRL, machine-readable, not human content).
- Redactions: none.
- Tables: cover-page jurisdiction/file-number/EIN table; cover-page check-box table; Section 12(b) registration table; Item-header tables; exhibit-index table; signature block table — all flagged "untagged ... column alignment not verified."
- Missing fields: Mr. Goodman's compensation, Revocation Period expiration calendar date, BioTelemetry date gap in Mr. Goodman's bio.

## Extraction caveats

- Treat Exhibits 10.1 and 99.1 as external — their full text is not in this source.md.
- Preserve "Moorehead" / "Moorhead" spelling discrepancy in signature block.
- Preserve "from and Senior Vice President" sentence as written.
- Treat "March 26" as cover-page "earliest event" date; events on March 27 are still within scope of the same 8-K.
- Treat Item 1.01 as a pointer, not a substantive item.
- Treat "shall not be deemed 'filed'" language under Item 7.01 as legally meaningful, not boilerplate.

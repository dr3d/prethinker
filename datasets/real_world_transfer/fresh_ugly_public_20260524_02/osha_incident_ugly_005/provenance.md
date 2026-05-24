# Provenance — osha_incident_ugly_005

## Source
- **Title (news release):** US Department of Labor cites construction contractor with 7 willful, 33 repeat violations after fatal Yarmouth cave-in
- **News release date:** April 1, 2026
- **News release number:** 26-574-NAT
- **Title (prior inspection):** Inspection 1794687.015 — Revoli Construction Co., Inc. (OSHA IMIS Establishment Search inspection-detail page)
- **Prior inspection number:** 1794687.015
- **Prior inspection Report ID:** 0111400
- **Prior inspection Date Opened:** December 20, 2024
- **Prior inspection Case Closed:** July 16, 2025
- **Trench-collapse incident date:** November 18, 2025
- **Issuing agency:** US Department of Labor / Occupational Safety and Health Administration (OSHA); prior inspection conducted by the Boston South Area Office
- **Authoritative URLs:**
  - DOL News Release: `https://www.dol.gov/newsroom/releases/osha/osha20260401`
  - OSHA Inspection Detail (prior): `https://www.osha.gov/ords/imis/establishment.inspection_detail?id=1794687.015`
- **Retrieved:** 2026-05-24
- **Original format:** HTML (DOL news release) and HTML (OSHA Establishment Search / IMIS inspection-detail page)

## Extraction steps
1. Located the news release via the OSHA news-releases listing and DOL newsroom archive.
2. Retrieved the DOL news release HTML from `https://www.dol.gov/newsroom/releases/osha/osha20260401`.
3. Identified Revoli Construction's prior OSHA inspection history via OSHA Establishment Search and selected Inspection 1794687.015 as the most relevant prior inspection — same employer, same general worksite locale (South Yarmouth, MA), formally settled and closed ~4 months before the November 2025 fatal trench collapse.
4. Retrieved the OSHA inspection-detail HTML from `https://www.osha.gov/ords/imis/establishment.inspection_detail?id=1794687.015`.
5. Converted both documents to Markdown, preserving:
   - The news release header (headline, sub-headline, dateline), body paragraphs (incident narrative, Secretary of Labor quote, seven-bullet violation category list, total proposed penalty, 15-business-day option language, National Emphasis Program reference), and all three media-contact blocks (Eric R. Lucero, Erika Ruthman, Juan Rodriguez).
   - The OSHA inspection-detail page header ("Case Status: CLOSED" twice), the Inspection Information block (Inspection Nr, Report ID, Date Opened), Site Address and Mailing Address blocks, supplemental fields (Union Status, SIC, NAICS, Inspection Type, Scope, Advanced Notice, Ownership, Safety/Health, Close Conference, Emphasis, Case Closed).
   - The Related Activity table verbatim (Referral 2243934).
   - The Violation Summary table preserving the blank cells in the Violations rows and explicit "$0" cells in the Penalty rows.
   - The Violation Items table preserving all three rows including the per-row Note text where present ("Citation has been deleted." on items 01001B and 02001).
6. `source_original.txt` is a byte-for-byte copy of `source.md`. Both documents were extracted to Markdown directly; the originals are the HTML pages at the URLs above.

## Excerpt boundaries
- News release: begins at "News Release" / headline and ends after the third media-contact block. Site chrome, share buttons, related-news links, and the "Skip to main content" navigation are omitted.
- OSHA inspection detail: begins at "Case Status: CLOSED" header line and ends after the Violation Items table. Site chrome (top navigation, Google Translate dropdown, footer) is omitted.
- Hyperlinks to per-item violation-detail subpages are omitted from the source body (the Citation IDs are preserved verbatim).
- No editorial commentary, summary, or QA hint has been added inside `source.md`.

## Caveats
- The news release describes the 2025 fatal incident as occurring at "a Yarmouth worksite" without specifying a street address. The prior inspection 1794687.015 lists the worksite address as 174 South Shore Drive, South Yarmouth, MA 02664. Source preserves both as written; the fixture explicitly probes whether the model recognizes that the source does NOT explicitly identify the 2025 fatal worksite as the 174 South Shore Drive address (q024).
- "Yarmouth" and "South Yarmouth" are colocated on Cape Cod, MA. The town of Yarmouth includes South Yarmouth as a village; this geographic relationship is general knowledge not stated in the source.
- The news release does not state the citation issuance date, abatement deadline, or contest status for the 2026 citations. The fixture treats these as absent information (q017).
- The "Latest Event" code "F - Formal Settlement" appears verbatim in the OSHA inspection-detail table. The fixture preserves this code verbatim; it indicates that the case closed via formal settlement agreement rather than by contest, payment, or affirmance.
- The Notes "Citation has been deleted." appear in the source verbatim for items 01001B and 02001. These notes follow OSHA's IMIS convention for citations that were withdrawn during settlement.
- The Initial Violations count of 2 in the prior inspection reflects OSHA's grouped-citation convention (01001A and 01001B as one grouped citation; 02001 as a separate citation), even though the Violation Items table shows three line items.
- Both the news release and the inspection-detail page describe Revoli Construction as a Massachusetts water/sewer line construction contractor; the OSHA inspection's NAICS code 237110/Water and Sewer Line and Related Structures Construction is consistent with the news release's industry description.

# Provenance — osha_incident_ugly_004

## Source
- **Primary source (news release):** US Department of Labor / OSHA news release, *US Department of Labor proposes more than $1M fine following worker fatality at New Jersey vegetable processing facility*
- **Primary source (inspection record):** OSHA Inspection Detail page for Inspection 1826893.015 — Taylor Farms New Jersey, Inc.
- **News release date:** November 24, 2025
- **News release number:** 25-1520-NAT
- **Inspection number:** 1826893.015
- **Inspection Report ID:** 0213900
- **Inspection Date Opened:** May 27, 2025
- **Citation Issuance Date (all 16 items):** November 21, 2025
- **Abatement Due Date (all 16 items):** December 18, 2025
- **Contest Date (all 16 items):** December 8, 2025
- **Issuing agency:** US Department of Labor / Occupational Safety and Health Administration (OSHA), Marlton, NJ Area Office, Region 2 (New York)
- **Authoritative URLs:**
  - DOL News Release: `https://www.dol.gov/newsroom/releases/osha/osha20251124`
  - OSHA Inspection Detail: `https://www.osha.gov/ords/imis/establishment.inspection_detail?id=1826893.015`
- **Retrieved:** 2026-05-24
- **Original format:** HTML (OSHA Establishment Search / IMIS inspection-detail page) plus HTML (DOL News release)

## Extraction steps
1. Located the news release via the OSHA news-releases enforcement listing.
2. Retrieved the DOL news release HTML from `https://www.dol.gov/newsroom/releases/osha/osha20251124`.
3. Looked up the underlying inspection via the OSHA Establishment Search and identified Inspection 1826893.015 as the citation case referenced in the news release.
4. Retrieved the OSHA inspection-detail HTML from `https://www.osha.gov/ords/imis/establishment.inspection_detail?id=1826893.015`.
5. Converted both documents to Markdown, preserving:
   - The news release header (Agency, Date, Release Number, dateline), body paragraphs, the "Penalties and citations may be adjusted throughout the course of the case process" advisory, and the single media-contact block (Kristen Knebel, phone, email).
   - The OSHA inspection-detail page header ("Case Status: OPEN" twice), the citations-posting advisory note, the Inspection Information block (Inspection Nr, Report ID, Date Opened), Site Address and Mailing Address blocks, the supplemental information fields (Union Status, SIC, NAICS, Inspection Type, Scope, Advanced Notice, Ownership, Safety/Health, Close Conference, Emphasis, Case Closed).
   - The Related Activity table verbatim (Complaint 2316392, Inspection 1828075).
   - The Violation Summary table preserving the blank cells (the "Other" and "Unclass" columns have blanks in the Violation rows, $0 in the Penalty rows).
   - The Violation Items table preserving all 16 rows with Citation IDs, Citation Type, Standard Cited, Issuance Date, Abatement Due Date, Current Penalty, Initial Penalty, FTA Penalty, Contest, and Latest Event columns.
6. `source_original.txt` is a byte-for-byte copy of `source.md`. Both documents were extracted to Markdown directly; the originals are the HTML pages at the URLs above.

## Excerpt boundaries
- News release: begins at the headline and ends after the media contact block. Site chrome (navigation, footer, share buttons, etc.) is omitted.
- OSHA inspection detail: begins at the "Case Status: OPEN" header line and ends after the Violation Items table. Site chrome (navigation, Google Translate dropdown, footer) is omitted.
- Hyperlinks to per-item violation-detail subpages are omitted from the source body (the citation IDs themselves are preserved verbatim).
- The OSHA "Note" advisory paragraph about citation items being posted 30 days after employer receipt is preserved.
- No editorial commentary, summary, or QA hint has been added inside `source.md`.

## Caveats
- The OSHA inspection-detail page is a snapshot at retrieval time (2026-05-24). Case status was "OPEN" with all 16 items in "Contested" status; the case has not yet closed and any subsequent penalty adjustments are not reflected in this snapshot. The news release explicitly warns that "Penalties and citations may be adjusted throughout the course of the case process."
- The employer's name appears in two slightly different forms across the source: "Taylor Farms New Jersey, Inc." (with internal comma, in the inspection-detail header) and "Taylor Farms New Jersey Inc." (no comma, in the news release body). Both forms are preserved verbatim. Fixture QA permits either form as correct.
- The Violation Summary table shows blanks (not zeros) in the "Initial Violations" and "Current Violations" rows for the "Other" and "Unclass" columns. The source's Markdown preserves these as blank cells.
- The Close Conference date in OSHA IMIS is recorded as the same date as the Date Opened (05/27/2025), which means OSHA opened the inspection and conducted its close conference on the same day. (Citations were issued months later on 11/21/2025.)
- The Marlton Area Office is the OSHA office handling the inspection; the news release dateline ("WASHINGTON") reflects national-news-release issuance from DOL headquarters and is not the field office.
- The standard codes in the OSHA inspection table are stored without periods (e.g., "19100147 C04 I" rather than "1910.147(c)(4)(i)"). Both representations are equivalent.

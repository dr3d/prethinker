# osha_incident_ugly_004 — Questions with reference answers

This file pairs each question with its reference answer for human review and grading. The QA pipeline must read questions only from `qa.md` (or `qa_questions.jsonl`); reference answers live in `oracle.jsonl`.

## q001 — metadata_identifier

**Question.** State the OSHA Inspection Number, Report ID, Date Opened, and Close Conference date for the inspection of Taylor Farms New Jersey, Inc.

**Reference answer.** Inspection Number: 1826893.015. Report ID: 0213900. Date Opened: 05/27/2025 (May 27, 2025). Close Conference: 05/27/2025 (also May 27, 2025 — the close conference date appears in the Inspection Information field as the same date as the opening).

## q002 — metadata_identifier

**Question.** State the full employer name as written on the OSHA inspection record, the parent company identified in the news release, and the NAICS code and description.

**Reference answer.** Full employer name as written on the OSHA inspection record: "Taylor Farms New Jersey, Inc." (the comma before "Inc." appears in the inspection header; the news release uses "Taylor Farms New Jersey Inc." without the comma — both forms appear verbatim in the source). Parent company per the news release: Taylor Fresh Foods Inc. NAICS code/description: 311991 / Perishable Prepared Food Manufacturing.

## q003 — metadata_identifier

**Question.** State the inspection site address, mailing address, and OSHA office handling the inspection.

**Reference answer.** Inspection site address: Taylor Farms New Jersey, Inc., 406 Heron Drive, Swedesboro, NJ 08085. Mailing address: 406 Heron Drive, Swedesboro, NJ 08085 (identical to the site address). OSHA office handling the inspection: Marlton Area Office.

## q004 — metadata_identifier

**Question.** State the OSHA news release date, release number, dateline city, and the news release media contact's full name, phone number, and email address.

**Reference answer.** News release date: November 24, 2025. Release Number: 25-1520-NAT. Dateline city: WASHINGTON. Media contact full name: Kristen Knebel. Phone Number: 202-693-3435. Email: knebel.kristen.cr@dol.gov.

## q005 — metadata_identifier

**Question.** State the alternate "operating as" trade name of PL Solutions Group LLC, the number of citations issued against that company per the news release, and the proposed penalties against that company.

**Reference answer.** Alternate trade name of PL Solutions Group LLC (per news release): "operating as People Logistics" — the news release describes it as "the onsite temporary employment agency." Number of citations issued against PL Solutions Group per the news release: three serious violations. Proposed penalties against PL Solutions Group: $33,100.

## q006 — date_chronology

**Question.** List, in calendar order, the dates referenced in the source: Date Opened, Close Conference, Citation Issuance Date (any citation), Abatement Due Date, Contest Date, and News Release Date.

**Reference answer.** In calendar order: (a) 05/27/2025 — Date Opened (also the same date as the Close Conference). (b) 11/21/2025 — Citation Issuance Date for all 16 violation items. (c) 11/24/2025 — News Release Date. (d) 12/08/2025 — Contest Date (Taylor Farms contested all 16 items on this date). (e) 12/18/2025 — Abatement Due Date for all 16 violation items.

## q007 — date_chronology

**Question.** How many calendar days elapsed between the inspection Date Opened (05/27/2025) and the Citation Issuance Date (11/21/2025) for all violation items? Show the arithmetic.

**Reference answer.** Date Opened 05/27/2025 → Citation Issuance Date 11/21/2025. From May 27 to May 31 = 4 days. June = 30. July = 31. August = 31. September = 30. October = 31. November 1–21 = 21 days. Total: 4 + 30 + 31 + 31 + 30 + 31 + 21 = 178 calendar days.

## q008 — date_chronology

**Question.** How many calendar days elapsed between the Citation Issuance Date (11/21/2025) and the Abatement Due Date (12/18/2025)? Show the arithmetic.

**Reference answer.** Citation Issuance 11/21/2025 → Abatement Due 12/18/2025. From November 21 to November 30 = 9 days. December 1–18 = 18 days. Total: 9 + 18 = 27 calendar days.

## q009 — date_chronology

**Question.** How many calendar days elapsed between the Citation Issuance Date (11/21/2025) and the News Release Date (11/24/2025)? Show the arithmetic.

**Reference answer.** Citation Issuance 11/21/2025 → News Release Date 11/24/2025. From November 21 to November 24 = 3 calendar days.

## q010 — date_chronology

**Question.** How many calendar days elapsed between the Citation Issuance Date (11/21/2025) and the Contest Date (12/08/2025) when Taylor Farms contested the citations? Show the arithmetic.

**Reference answer.** Citation Issuance 11/21/2025 → Contest Date 12/08/2025. From November 21 to November 30 = 9 days. December 1–8 = 8 days. Total: 9 + 8 = 17 calendar days.

## q011 — table_list_citation

**Question.** Reproduce the values of the Violation Summary table for every column (Serious, Willful, Repeat, Other, Unclass, Total) and for every row (Initial Violations, Current Violations, Initial Penalty, Current Penalty, FTA Penalty).

**Reference answer.** Violation Summary table values (Serious / Willful / Repeat / Other / Unclass / Total): Initial Violations: 2 / 6 / 1 / blank / blank / 9. Current Violations: 2 / 6 / 1 / blank / blank / 9. Initial Penalty: $33,100 / $993,084 / $99,300 / $0 / $0 / $1,125,484. Current Penalty: $33,100 / $993,084 / $99,300 / $0 / $0 / $1,125,484. FTA Penalty: $0 / $0 / $0 / $0 / $0 / $0.

## q012 — table_list_citation

**Question.** List, in source order, the four distinct standards cited across the 16 violation items in the OSHA inspection record (give the standard codes exactly as they appear in the source's "Standard Cited" column).

**Reference answer.** In source order (first appearance in the violation-items table), the four distinct standards cited are: (1) 19100147 C04 I (first appears at item 1, Citation ID 01001A); (2) 19100147 D (first appears at item 2, Citation ID 01001B); (3) 19100147 C04 II (first appears at item 3, Citation ID 01002); (4) 19100147 C07 I A (first appears at item 16, Citation ID 03001). These correspond to 29 CFR 1910.147(c)(4)(i), 1910.147(d), 1910.147(c)(4)(ii), and 1910.147(c)(7)(i)(A), respectively — all subsections of the OSHA Control of Hazardous Energy (lockout/tagout) standard.

## q013 — table_list_citation

**Question.** Reproduce the Related Activity table verbatim, including the two row types, their Activity Numbers, and the Safety/Health columns.

**Reference answer.** Related Activity table verbatim: Row 1 — Type: Complaint; Activity Nr: 2316392; Safety: Yes; Health: (blank). Row 2 — Type: Inspection; Activity Nr: 1828075; Safety: Yes; Health: (blank).

## q014 — table_list_citation

**Question.** List, in source order, the six Citation IDs in the violation-items table that are classified as Willful and whose Citation ID ends in "A" (i.e., the willful sub-A citations that carry the per-violation penalty).

**Reference answer.** In source order, the six Willful Citation IDs ending in "A" are: 02001A, 02002A, 02003A, 02004A, 02005A, 02006A. Each carries a Current Penalty and Initial Penalty of $165,514 in the violation-items table.

## q015 — table_list_citation

**Question.** State each of the following Inspection Information values verbatim as they appear in the source: Inspection Type, Scope, Advanced Notice, Ownership, Safety/Health, Union Status, and Emphasis.

**Reference answer.** Verbatim: Inspection Type: Unprog Rel. Scope: Complete. Advanced Notice: N. Ownership: Private. Safety/Health: Safety. Union Status: NonUnion. Emphasis: N:Amputate.

## q016 — source_state_response_status

**Question.** State the Case Status of the inspection, the value in the Case Closed field, and the Latest Event value that appears for every one of the 16 violation items.

**Reference answer.** Case Status: OPEN (stated twice in the inspection-detail header). Case Closed field: blank (no value present). Latest Event for every one of the 16 violation items: "C - Contested."

## q017 — source_state_response_status

**Question.** Did Taylor Farms contest the citations? If so, on what date, and how many of the 16 violation items show a contest entry?

**Reference answer.** Yes — Taylor Farms contested the citations. Contest Date: 12/08/2025. All 16 violation items in the inspection's violation-items table show a Contest entry of 12/08/2025 with Latest Event "C - Contested."

## q018 — source_state_response_status

**Question.** Does the source identify the worker who died by name, gender, age, or any other identifying detail? Answer with what the source actually states.

**Reference answer.** No — the source does not identify the worker by name, gender, age, or any other identifying detail. The news release says only that "a worker was fatally injured while cleaning and sanitizing a machine" and refers to "the fatality" generically. The OSHA inspection detail page contains no narrative description of the fatality or victim. No personal identifiers are present in the source.

## q019 — source_state_response_status

**Question.** State the FTA Penalty value for every violation item and the FTA Penalty row totals from the Violation Summary table.

**Reference answer.** FTA (Failure to Abate) Penalty value for every one of the 16 violation items: $0 in both the Initial and Current FTA Penalty columns of the violation-items table. Violation Summary row "FTA Penalty": $0 in every column (Serious $0, Willful $0, Repeat $0, Other $0, Unclass $0, Total $0).

## q020 — source_state_response_status

**Question.** Per the news release, what three options does the company have within 15 business days of receipt of the citations and penalties, and what does the news release say about the possibility that penalties or citations may change later?

**Reference answer.** Per the news release, within 15 business days of receipt of citations and penalties, the company has three options: (1) comply, (2) request an informal conference with OSHA, or (3) contest the findings before the independent Occupational Safety and Health Review Commission. The news release also explicitly states that "Penalties and citations may be adjusted throughout the course of the case process" and directs readers to check the OSHA establishment search page periodically for any changes in the inspection or penalty status.

## q021 — hard_join_comparison

**Question.** The news release says OSHA cited Taylor Farms for "16 safety violations" but the OSHA Violation Summary table says only 9 violations total. Reconcile these two counts by explaining how the violation items table groups sub-items, and identify which is which.

**Reference answer.** The "16 safety violations" figure in the news release counts every line item in the violation-items table (16 rows: items 1 through 16). The "9 violations" figure in the Violation Summary table counts distinct citation numbers, where citations with grouped sub-items (subpart A and subpart B with the same Citation Number) are counted as a single violation. Breakdown of the 9 distinct violations: Citation 1 Item 1 (with subparts 01001A and 01001B) = 1 Serious violation; Citation 1 Item 2 (01002) = 1 Serious violation (subtotal 2 Serious); Citations 2 Items 1–6 (02001 through 02006, each with subparts A and B) = 6 Willful violations; Citation 3 Item 1 (03001) = 1 Repeat violation. Total: 2 + 6 + 1 = 9 distinct citations / 16 line items.

## q022 — hard_join_comparison

**Question.** The maximum willful penalty appears verbatim in multiple rows of the violation-items table. State that exact penalty amount, how many violation items are at that exact amount, and verify with arithmetic that those items account for the Willful column total in the Violation Summary.

**Reference answer.** Maximum willful penalty: $165,514 per item. Number of violation items at that exact amount: 6 (items 4, 6, 8, 10, 12, 14 — Citation IDs 02001A, 02002A, 02003A, 02004A, 02005A, 02006A). Arithmetic verification: 6 × $165,514 = $993,084, which exactly matches the Willful column total in the Violation Summary table ($993,084 for both Initial and Current Penalty).

## q023 — hard_join_comparison

**Question.** The exact dollar amount $33,100 appears in the source attached to two different parties / contexts. State the two distinct locations in which this amount appears and what each represents.

**Reference answer.** The dollar amount $33,100 appears in two distinct locations: (1) The Violation Summary table for Taylor Farms's inspection 1826893.015, in the "Serious" column for both Initial Penalty and Current Penalty rows — totaling the Serious violation items 01001A ($16,550), 01001B ($0), and 01002 ($16,550): $16,550 + $0 + $16,550 = $33,100. (2) The news release statement that the on-site temporary employment agency PL Solutions Group LLC (operating as People Logistics) was cited for three serious violations with proposed penalties of $33,100. The same exact dollar amount thus represents two unrelated penalty totals attached to two different parties (Taylor Farms's Serious-class subtotal vs PL Solutions Group's total proposed penalties).

## q024 — hard_join_comparison

**Question.** The standard "19100147 C04 I" (i.e., 29 CFR 1910.147(c)(4)(i)) appears in multiple violation items. Count the items citing this standard, and break down by Citation Type (Serious vs Willful).

**Reference answer.** Standard 19100147 C04 I (1910.147(c)(4)(i)) appears in 7 violation items: (1) item 1, Citation ID 01001A, Serious; (4) item 4, 02001A, Willful; (6) item 6, 02002A, Willful; (8) item 8, 02003A, Willful; (10) item 10, 02004A, Willful; (12) item 12, 02005A, Willful; (14) item 14, 02006A, Willful. Breakdown by Citation Type: 1 Serious + 6 Willful = 7 items total.

## q025 — hard_join_comparison

**Question.** The standard "19100147 D" appears seven times in the violation-items table, every time with a $0 penalty. Explain the source's grouping convention that produces these $0 sub-items, citing specific Citation IDs to illustrate.

**Reference answer.** The standard 19100147 D appears at $0 in seven items because the violation-items table uses a grouped-citation convention: when a single citation cites two related provisions of the same standard, OSHA splits the citation into subpart A (which carries the per-violation penalty) and subpart B (which represents the additional grouped sub-citation at $0, since the penalty is already counted under subpart A). Specific Citation ID examples: (a) 01001A (Serious, 19100147 C04 I, $16,550) is paired with 01001B (Serious, 19100147 D, $0); (b) 02001A (Willful, 19100147 C04 I, $165,514) is paired with 02001B (Willful, 19100147 D, $0); the same A/B pairing holds for 02002–02006. In each pair, the underlying violation is treated as a single grouped citation; only one subpart carries the dollar penalty.


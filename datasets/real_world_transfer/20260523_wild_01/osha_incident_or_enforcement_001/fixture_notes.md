# Fixture Notes: osha_incident_or_enforcement_001

## Why this document was chosen

A real, public Minnesota OSHA (state-plan OSHA) fatality investigation summary covering federal fiscal year 2024 (October 2023 – September 2024). This is exactly the kind of sparse, tabular, slow-updating public enforcement record that real-world OSHA data tends to be: column-oriented, incomplete fields, status values that mix "Case open," "Citations issued," "No citations issued," and "No inspection" (with statutory or factual reasons).

## Pressure applied to Prethinker

1. **Sparse public records.** The document is a wide table with intentionally limited fields per fatality. No employee names, no specific employer/company names — only type-of-business, NAICS, worksite city, date, employee-count, description, and outcome. This forces the system to answer many questions with "the document does not say."
2. **Identifier discipline under blank cells.** Inspection numbers like 318202041 are extractable identifiers; but four entries have no inspection number at all (Mankato 12/7/23; Virginia 3/7/24; Apple Valley 5/21/24; Red Wing 9/21/24). Each of these four blanks is paired with "Case open" — a structural correlation that the system can either recognize or miss.
3. **Event descriptions vs enforcement status.** A fatality entry's "Description of event" (e.g., "Employee diagnosed with COVID-19," "Employee was overcome while working in a manhole") describes a factual incident; the "Outcome" column describes what MNOSHA did or did not do administratively. Confusing the two is a major risk.
4. **Multi-employer incidents.** Two entries (1/4/24 North Mankato and 5/30/24 Duluth) each represent a single fatality referenced by two contractor inspection numbers, with the outcome column making employer-specific assertions ("Citations issued for 318201902; no citations issued for 318202009" vs "Citations issued for both employers"). This forces split-attribution reasoning.
5. **Negative/unknown answers.** Negative-limitation questions force the model to refuse to fabricate a name or an inspection number that the document does not contain.
6. **Non-chronological row order.** Rows are not sorted by date of incident; the earliest date (9/27/23) appears mid-document, not first. A model that mistakes "first row in the table" for "earliest event" will be wrong.

## Messy features

- **Recurring page-header line** repeated five times: "Inspection data, including citations, can be viewed at osha.gov/data." (a self-referential pointer to the underlying federal dataset).
- **Column-header row repeated** at the top of each page-section table, mimicking the printed PDF layout.
- **Blank cells in the leftmost column** (inspection number) for four entries.
- **Two distinct dual-inspection entries** with within-cell concatenation of two contractor records, each with its own NAICS and national-employee count.
- **Inconsistent singular/plural** in the outcome column ("Citation issued" vs "Citations issued") — preserved verbatim.
- **Five distinct outcome status phrasings:** "Citations issued," "Citation issued," "No citations issued," "Case open," "No inspection – not work-related," "No inspection – farm appropriations rider."
- **No personally identifiable information.** Deceased employees and specific employer companies are NOT named anywhere.
- **An en-dash** is used in "No inspection –" status values (not a hyphen).

## Expected hard question types

- Temporal-sequence q011 — the document is not sorted by date and includes a 9/27/23 entry partway through; the system must scan the whole date column, not just the first row.
- Numeric q014 — counting distinct inspection numbers across the document, including the two dual-inspection rows.
- Numeric q015 — counting entries with no inspection number (requires identifying the blank cells).
- Conflict q021 — comparing two dual-employer entries with opposite citation outcomes.
- Negative-limitation q024 — recognizing that employee names and employer names are NOT present anywhere.
- Synthesis q025 — combining the schema, the variety of outcome statuses, and the blank-inspection-number / dual-inspection cases to articulate why fatality count ≠ inspection count ≠ citation count.

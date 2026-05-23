# Real-World Transfer Batch — 20260523_wild_01 — MANIFEST

A 5-fixture transfer-batch of real, public-source documents for Prethinker. Each fixture preserves the awkwardness, caveats, redactions, sparse fields, and conflicting statements of the underlying primary source.

| # | Fixture | Domain | Source title | Document date | Source URL | Pressure target |
|---|---|---|---|---|---|---|
| 1 | `ntsb_aviation_investigation_001` | aviation accident investigation | NTSB Preliminary Report DCA26MA024 — UPS Flight 2976 (McDonnell Douglas MD-11F, N259UP), Louisville, KY | 2025-11 (preliminary, dated within 30 days of the November 4, 2025 accident) | https://www.ntsb.gov/investigations/Documents/Preliminary%20Report%20DCA26MA024.pdf | Temporal reasoning (timestamps to the second), numeric/unit extraction (altitudes, speeds, injuries), preliminary-status caveats, FDR-vs-ADS-B altitude discrepancy, Emergency AD cross-references, comparison to AA Flight 191 (1979), six-party investigation roster |
| 2 | `ntsb_marine_investigation_001` | marine accident investigation | NTSB Marine Investigation Report MIR-25-21 — Capsizing of liftboat *Baylor J. Tregre*, Gulf of America, 23 nm S of Galveston | 2024-05-13 event; MIR issued in 2025 | https://www.ntsb.gov/investigations/AccidentReports/Reports/MIR2521.pdf | AIS timestamps to the second, multi-day timeline (departure → casualty → salvage → exam), wind-speed source discrepancy (captain vs NWS), explicit probable-cause statement, three-factor synthesis (tow + release + flooding), NWS product sequence, IMO/classification-society N/A negative cases, preserves "Gulf of America" verbatim |
| 3 | `fda_warning_or_recall_001` | pharmaceutical regulation | FDA Warning Letter — Granules India Limited (MARCS-CMS 697115 / Warning Letter 320-25-48) | 2025-02-26 | https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/granules-india-limited-697115-02262025 | Regulatory source attribution, (b)(4) redactions preserved verbatim, three numbered CGMP violations (21 CFR 211.67(b), 211.58, 211.68(a)), MACO-calculation conflict, three "Your response is inadequate" verdicts, no named products/lots, explicit non-exhaustive disclaimer, GDUFA III footnote |
| 4 | `sec_8k_material_event_001` | securities disclosure | Hamilton Lane Incorporated Form 8-K (event date October 1, 2025; filed October 6, 2025) | 2025-10-01 (earliest event reported); 2025-10-06 (signed/filed) | https://www.sec.gov/Archives/edgar/data/1433642/000143364225000110/hlne-20251001.htm | Corporate/legal document structure, Item 1.01 → Item 2.03 incorporation by reference, Exhibit 10.1 cross-reference with "qualified in its entirety" caveat, three-date sequence (2022 origination, 2025 amendment, 2025 filing), interest-rate formula change (Prime − 1.50% → Prime − 1.35% with unchanged 3.00% floor), $75M→$50M principal change under $325M cap, no cover-page boxes checked, dates "changed" but not specified in the 8-K text |
| 5 | `osha_incident_or_enforcement_001` | occupational safety enforcement | Minnesota OSHA fatality investigation summary — Federal-fiscal-year 2024 | 2026-04-21 (last updated); covers FFY 2024 (Oct. 1, 2023 – Sept. 30, 2024) | https://dli.mn.gov/sites/default/files/pdf/24_FFY_fatality_log.pdf | Sparse public records, NAICS identifiers, blank inspection-number cells (4 entries), five distinct outcome statuses, two dual-employer entries with split per-employer outcomes, non-chronological row ordering, no employee or employer names, "No inspection – farm appropriations rider" statutory exclusion |

## Fixture file inventory (each fixture contains all 12 files)

```
source.md
story.md            (byte-equivalent copy of source.md)
qa.md               (25 numbered questions, no answers)
oracle.jsonl        (25 rows, q001–q025)
qa_battery.json     (25 objects with answers)
qa_questions.jsonl  (25 rows, questions only)
metadata.json
provenance.md
README.md
fixture_notes.md
anti_leakage_manifest.md
source_original.txt
```

## Category distribution (per fixture)

Each fixture's 25 QA rows are split as: 5 direct_lookup, 3 identifier_entity, 4 temporal_sequence, 4 numeric_unit, 3 source_attribution, 3 conflict_discrepancy, 2 negative_limitation, 1 synthesis. Distribution was validated mechanically for all five fixtures.

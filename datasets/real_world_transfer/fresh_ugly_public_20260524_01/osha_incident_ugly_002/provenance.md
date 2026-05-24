# Provenance — osha_incident_ugly_002

- **Source URLs (two):**
    - https://www.osha.gov/pls/imis/accidentsearch.accident_detail?id=123160.015 (the Accident Report Detail)
    - https://www.osha.gov/ords/imis/establishment.inspection_detail?id=1455758.015 (the matched Inspection Detail with citations, settlement record, and the embedded Investigation Summary)
- **Retrieval date:** 2026-05-24
- **Document format (original):** HTML pages on osha.gov (OSHA's IMIS public interface).
- **Transformation performed:**
    - Both HTML pages were fetched and the data tables, headings, and narrative were extracted.
    - `source_original.txt` is a plain-text capture of both pages with the table values preserved.
    - `source.md` is a Markdown rendering of the combined record. Both the Accident Report Detail and the Inspection Detail are presented in the order in which they appear in OSHA's interface, including the establishment header table, the boilerplate "Case Status" notes, the Accident Details table, the Employee Details, the Violation Summary, the Violation Items, and the Investigation Summary / Investigated Inspection.
    - OSHA site chrome (top/bottom navigation menus, language selectors, footer link lists) removed.
- **Excerpt boundaries:** `source.md` contains the **full content** of the two referenced OSHA IMIS pages. The two are presented together because the Accident Report Detail page alone is intentionally brief; the Inspection Detail page is where the citation, penalty changes after settlement, and the duplicated Investigation Summary live.
- **Caveats:**
    - The SIC field is unpopulated in both source pages; only NAICS (238160) is populated. Preserved as blank, not filled in.
    - The "Nature of Injury" cell for the employee is blank on both pages, and the "Fatality Cause" sub-field in the Employee Details Construction column is blank as well. Preserved as blank.
    - The "Contest" column for the single citation is blank — the case was resolved by Informal Settlement, not by contest. Preserved as blank.
    - The standard cited is rendered by OSHA as "19260760 A01"; this is OSHA IMIS shorthand for 29 CFR 1926.760(a)(1) (steel erection — fall protection). The source page does not spell out the expanded CFR citation; only the IMIS code is shown.
    - The Accident Details table shows "Non-building Height" of 23 (feet), and the Employee Details "Distance of Fall" and "Worker Height Above Ground/Floor" are both 23 feet, while the Abstract / Investigation Summary narrative gives the fall height as 22.8 feet. Both values are preserved verbatim from the source; the discrepancy is in the original OSHA record.

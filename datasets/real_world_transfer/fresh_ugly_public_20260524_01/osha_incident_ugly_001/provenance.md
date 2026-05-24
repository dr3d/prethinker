# Provenance — osha_incident_ugly_001

- **Source URLs (two):**
    - https://osha.prod.pace.dol.gov/ords/imis/accidentsearch.accident_detail?id=180500.015 (the Accident Report Detail)
    - https://osha.prod.pace.dol.gov/ords/imis/establishment.inspection_detail?id=1814187.015 (the matched Inspection Detail with citations, violation summary, and the embedded Investigation Summary)
- **Retrieval date:** 2026-05-24
- **Document format (original):** HTML pages on osha.prod.pace.dol.gov (OSHA's IMIS public interface)
- **Transformation performed:**
    - Both HTML pages were fetched and the data tables, headings, and narrative were extracted.
    - `source_original.txt` is a plain-text capture of both pages with the table values preserved.
    - `source.md` is a Markdown rendering of the combined record. Both the Accident Report Detail and the Inspection Detail are presented in the order in which they appear in OSHA's interface, including the establishment header tables, the boilerplate "Case Status: OPEN" note, the Accident Details table, the Employee Details / Investigated Inspection tables (which both list the same three fatally injured employees), the Violation Summary, and the Violation Items.
    - OSHA site chrome (top/bottom navigation menus, language selectors, footer link lists) removed.
- **Excerpt boundaries:** `source.md` contains the **full content** of the two referenced OSHA IMIS pages. The two are presented together because the Accident Report Detail page alone is intentionally brief and the IMIS Inspection Detail page is where the citations, penalties, and the duplicated Investigation Summary live; reading them together is the normal workflow for an OSHA accident dossier.
- **Caveats:**
    - Some rows in the source contain blank cells (e.g., the SIC value is unpopulated, the "Nature of Injury" column is blank for all three employees, the Emphasis / Case Closed fields are blank). These blanks are preserved as blanks, not filled in.
    - The standard cited is rendered by OSHA as "19260200 G01" / "19260200 G02"; this is OSHA IMIS shorthand for 29 CFR 1926.200(g)(1) and (g)(2) (traffic signs for highway construction work zones). The source pages do not spell out the expanded CFR citation; only the IMIS code is shown.
    - The employer name appears as "Premier Fence, Llc" (lowercase 'llc') in the source pages; preserved verbatim.

# Fixture notes — sec_material_event_ugly_005

## What this document pressures

This fixture exercises the standard SEC Form 8-K/A probes (form type, amendment number, identifier set, date chronology) plus several less-obvious behaviors specific to Item 4.02 financial-restatement amendments.

### Six distinct calendar dates (q006, q007, q008, q009, q010)
The fixture has the densest date-anchor cluster of any SEC fixture in the batch:
- March 31, 2025 — end of Non-Reliance Period
- May 16, 2025 — original 10-Q filing
- August 13, 2025 — Audit Committee conclusion / Date of Report
- August 14, 2025 — Original 8-K filing AND amended 10-Q filing (two events on one date)
- August 22, 2025 — Amendment 8-K/A signature date

Four explicit arithmetic probes (46, 89, 9, 8 days) plus enumeration in calendar order force the model to maintain six anchors simultaneously without conflating any.

### Same-date two-event probe (q025)
August 14, 2025 anchors both the Original 8-K filing and the amended 10-Q filing. The source establishes sequential order via the word "Subsequent" ("Subsequent to the filing of the Original Form 8-K, the Company completed[]its restatement..."). Pipelines that treat the date alone as sufficient miss the explicit ordering language.

### Double-negative emerging-growth-company checkbox (q017)
The second EGC checkbox uses a double-negative construction: checked = "elected NOT to use" (i.e., opted out of the extended transition period). The registrant left this box unchecked, so the registrant uses the extended transition period. A model that pattern-matches "unchecked = no" without parsing the double negative will report the substantive opposite of the literal source state.

Critically, q017 forces explicit articulation of: (a) the literal checkbox state (☐ unchecked); (b) what that state means under the double-negative semantics; and (c) the practical consequence (registrant uses the extended transition period).

### Emerging growth company status (q016, q012)
Unlike the ServiceNow and Blackstone 8-Ks in this batch (where the EGC checkbox is ☐ unchecked), SHF Holdings IS an emerging growth company (☒ checked). The fixture exposes this contrast.

### Two registered securities with ticker convention (q004, q024)
SHFS (common stock) and SHFSW (warrants exercisable into SHFS at $11.50). The W-suffix ticker convention links the two — a Nasdaq norm that the source does not articulate but the fixture probes via q024. Pipelines that report only one ticker (typically the more-traded SHFS) will fail.

### Auditor identifier — abbreviation vs full name (q005)
"Macias Gini & O'Connell LLP" and "MGO" both appear in the source. The fixture forces extraction of both forms plus the role description ("the independent registered public accounting firm for the Company"). The apostrophe in "O'Connell" must be preserved.

### Item 4.02 disclosure completeness (q014, q020, q023)
Item 4.02(a)(3) of Form 8-K requires disclosure that the registrant has discussed the matters disclosed under the item with the independent accountant. The Original 8-K omitted this disclosure; Amendment No. 1 cures the omission. The fixture probes:
- q014: the Item number and full topic title
- q020: what the Audit Committee did (discussed with MGO)
- q023: what was missing from the Original 8-K (the Audit Committee / MGO discussion)

### Black-Scholes input pair (q013)
"Expected term" and "stock price" — exactly two inputs, named in that order. Pipelines that confabulate other Black-Scholes inputs (volatility, risk-free rate, dividend yield) will fail q013. The source is specific about which two were incorrect.

### Verbatim typo "completedits" (q018)
The Item 4.02 final paragraph contains the run-on "completedits" (missing space). Fixture question q018 quotes this verbatim, testing whether the model preserves source idiosyncrasies vs silently correcting them.

### "$500,000" affects two line items (q022)
Single error → two line items (operating expenses AND net loss). The source uses conjunction "and" to indicate the same approximately $500,000 figure affects both. Models that treat the language as two separate $500,000 adjustments will overstate the impact.

### Signatory is the CEO (q002)
Terrance E. Mendez, Chief Executive Officer, signs the Amendment. This contrasts with sec_003 (General Counsel signs Item 5.02 executive-compensation 8-K) and sec_004 (Chief Financial Officer signs Item 2.02 results-announcement 8-K). The fixture batch as a whole demonstrates three different signatory conventions matched to three different Item types.

### Date of Report ≠ Signature Date (q002, q009, q021)
This fixture is the only one in the SEC trio where Date of Report (Aug 13) and signature date (Aug 22) differ. The 9-day gap reflects the Amendment-filing process: the underlying triggering event is the Aug 13 Audit Committee conclusion, but the amendment itself is signed and filed 9 days later. q021 explicitly contrasts the 1-day gap (Date of Report → Original 8-K filing) with the 9-day gap (Date of Report → Amendment signature).

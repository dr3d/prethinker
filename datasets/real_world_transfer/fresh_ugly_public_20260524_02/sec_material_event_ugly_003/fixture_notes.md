# Fixture notes — sec_material_event_ugly_003

## What this document pressures

This fixture exercises the standard SEC Form 8-K probes — multi-date chronology, enumerated benefit lists, and identifier sets — while also stressing several less-obvious behaviors specific to executive-employment-amendment disclosures.

### Same-day report and signature (q002, q006)
The "Date of report (Date of earliest event reported)" and the signature date are both December 23, 2025. q002 and q006 force enumeration of dates referenced in the source; models that assume the report and signature dates differ will misorder the chronology.

### Effective date in the future (q006, q007)
The amendment and the Executive Severance Policy are both dated to become effective January 1, 2026 — nine days AFTER the Date of report. This is a common 8-K pattern (announce now, effective at year-end) but probes whether the model can hold three temporal anchors simultaneously: report date, effective date, and end-of-service date.

### Multi-year span with embedded leap day (q008, q009, q023)
The 5-year span from January 1, 2026 to December 31, 2030 includes the February 29, 2028 leap day. The total is 1,825 days (not 1,825 - 0 days or 1,824 days). q008 and q009 explicitly probe leap-year-aware arithmetic; q023 cross-checks by demanding a year-by-year breakdown.

### Two enumerated lists with different cardinalities (q014, q015)
- CIC scenario: 4 benefits (i, ii, iii, iv)
- Non-CIC scenario: 5 benefits (i, ii, iii, iv, v)

Models that naturally pattern-match equal-cardinality lists will miscount one of the two scenarios. The non-CIC scenario has an extra PRSU prorata vesting element (v) that the CIC scenario folds into a single 100% acceleration line.

### Four-role title enumeration (q013, q022)
Four titled roles in source order: CEO, co-CEO, Executive Chairman, Non-Executive Chairman. q022 specifically asks about role-specific compensation, where the source addresses three of the four roles (CEO/co-CEO get peer-group benchmark, Executive Chairman gets responsibilities-level benchmark, Non-Executive Chairman is silent). Models that confabulate compensation for Non-Executive Chairman fail q022.

### Multiple appearances of the same phrase (q010)
The phrase "March 15th of the year following the then-current fiscal year" appears verbatim in TWO different subsections (CIC subsection (i) for Target Bonus; non-CIC subsection (ii) for Actual Bonus). q010 probes whether the model recovers both occurrences and correctly identifies their scenarios.

### Negative-finding probes (q016, q017, q018, q019, q020)
- q016: emerging growth company status — checkbox unchecked
- q017: former name/address — verbatim "Not Applicable"
- q018: four securities-registration boxes — all unchecked
- q019: no specific dollar amounts disclosed for compensation
- q020: no specific dollar amounts disclosed for severance (only formulas, multipliers, durations)

A model that confabulates dollar figures or treats unchecked boxes as omitted will fail multiple negative-finding probes.

### Inference probe: "Amendment No. 3" implication (q024)
The exhibit title "Amendment No. 3 to Employment Agreement" implies prior amendments No. 1 and No. 2 must exist. The source itself does NOT describe or attach those prior amendments. q024 tests the inference (at least 2 prior amendments exist) and the recognition that the source does not provide them.

### Signatory-vs-subject distinction (q025)
The Item 5.02 subject (McDermott, Chairman and CEO) and the signatory (Elmer, General Counsel) are different individuals. q025 forces explicit recognition of the role separation, including that the General Counsel signs because the CEO is the counterparty to the contract being amended (a corporate-governance norm the source does not state but the fixture probe allows answering as standard practice).

### Identifier set with mixed formats (q001)
ServiceNow's identifiers include: Commission File Number "001-35580" (with leading zeros and dash), IRS EIN "20-2056195" (with dash), par value "$0.001" (with leading $ and three decimal places), ticker "NOW" (alphabetic). q001 probes preservation of formats verbatim.

### Cover-page checkbox completeness (q011, q018)
Four named provisions (Rule 425, 14a-12, 14d-2(b), 13e-4(c)) all unchecked. q011 enumerates the provisions; q018 confirms all four checkbox states. A model that conflates "the registrant is not relying on any of these" with "these provisions are not on the cover page" will fail q011.

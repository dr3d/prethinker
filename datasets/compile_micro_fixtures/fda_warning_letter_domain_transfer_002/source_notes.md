# source_notes.md - fda_warning_letter_domain_transfer_002

## Source

- URL: https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/rechon-life-science-ab-701040-04302025
- Title: Rechon Life Science AB - 701040 - 04/30/2025
- Issuing office: Center for Drug Evaluation and Research (CDER), Office of Manufacturing Quality, Office of Compliance
- Source type: real public FDA warning letter, not synthetic and not derived from the Apothecary or Marigold fixtures.

## Why This Letter Was Selected

This letter pressures the same FDA warning-letter domain pack on a different
company, facility, date range, country, and violation mix. It contains:

- a warning-letter wrapper and reference number;
- a regulated facility with FEI;
- recipient, responsible official, signatory, and response contact roles;
- an inspection date range;
- a Form FDA 483 response date;
- four numbered CGMP violations;
- four CFR citations;
- an FDCA adulteration basis;
- response instructions and electronic reply channel;
- conclusion language about non-exhaustive violations and recurrence prevention;
- a GDUFA footnote that mentions future meeting eligibility without stating a meeting occurred.

## Oracle Adjudication

The first landed package used the correct registered predicate names but guessed
several argument orders and value domains. This fixture was corrected before any
claim-bearing compile. The corrections are source/contract adjudications, not
model-output concessions.

Key corrections:

- Date values use `v_YYYY_MM_DD` atoms.
- `fda_correspondence_party/5` follows the registered order:
  `letter_id, party_id, party_role, party_name, source_or_scope`.
- `fda_violation/5` follows the registered order:
  `violation_id, letter_id, violation_number, violation_category, source_or_scope`.
- CFR values use compact citation atoms such as `cfr_21_211_113_b`, not quoted rule text.
- `fda_violation_detail/5` uses only registered detail kinds and roles.
- `domain_omission/5` quotes the carrier signature as `'fda_regulatory_meeting/4'`
  and uses a registered omission kind.

## Violation Category Rationale

- Violation 1 uses `contamination_control` because the source headline and
  citation concern procedures designed to prevent microbiological contamination.
- Violation 2 uses `other_registered_category`. The source pressure is
  investigation of unexplained discrepancies and OOS results under 21 CFR
  211.192. The current FDA category palette does not have a dedicated
  investigation category. Using `data_integrity` would overstate the source.
- Violation 3 uses `aseptic_processing` because the source frames cleaning and
  disinfection as the system for producing aseptic conditions.
- Violation 4 uses `facility_equipment_control` because the source describes
  buildings and room surfaces not maintained in good repair.

## Details Included

- `sop_0870_3_0` captures the named filling/sealing SOP scope without copying
  the source paragraph.
- `response_inadequate` captures source-stated response inadequacy for the
  contamination-control and investigation failures.
- `environmental_monitoring_excursion` captures the investigation subject
  without turning the environmental-monitoring paragraph into prose.
- `decontamination_effectiveness_validation` captures the validation/assessment
  scope for the aseptic-room cleaning/disinfection issue.
- `iso_7_room` captures the facility area with peeling/bubbled paint and rust.

## Deliberately Omitted

- `fda_prior_warning_letter/5`: the source states a prior inspection finding,
  not a prior warning letter.
- `fda_consultant_recommendation/4`: the source does not state a consultant
  recommendation or 21 CFR 211.34 consultant language.
- `fda_regulatory_meeting/4`: the source states only future eligibility for a
  Post-Warning Letter Meeting. This is accounted for with `domain_omission/5`.

## Forbidden Facts

The forbidden facts catch:

- prose-shaped violation categories;
- full response instructions hidden as one atom;
- full rule text hidden as a citation value;
- source-excerpt detail values;
- inferred signatories;
- inferred prior warning letters;
- inferred meetings asserted as already held.

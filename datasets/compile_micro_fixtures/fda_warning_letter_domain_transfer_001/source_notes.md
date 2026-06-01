# Source Notes - fda_warning_letter_domain_transfer_001

## Source

- URL: https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/apothecary-pharma-llc-717972-12012025
- Title: Apothecary Pharma, LLC - 717972 - 12/01/2025 | FDA
- Issuing office: Center for Drug Evaluation and Research (CDER); signed by the
  Office of Compounding Quality and Compliance, Office of Compliance.
- WL #: 717972 (MARCS-CMS 717972). Issue date: 2025-12-01.
- Public-domain U.S. Government work. Not synthetic, not LLM-authored, not
  derived from the Marigold micro.

## Why This Letter Was Selected

- A CDER sterile-drug CGMP warning letter that is structurally unlike the
  Marigold micro but pressures the same registered FDA carriers.
- Six numbered CGMP violations, each with one CFR citation.
- A real 211.113(b) microbiological-contamination-control violation alongside
  211.42(c)(10)(v)/(vi) aseptic-condition violations, which tests both sides of
  the contamination-control / aseptic-processing category boundary.
- A third-party sterile-consultant recommendation, a 15-working-day response
  requirement, two adulteration bases, conclusion responsibility language, and a
  real signatory block.

## Oracle Alignment

The original package used registered predicate names but several stale argument
layouts. This version follows the current carrier contracts exactly:

- `fda_correspondence_party/5`: letter, party id, role, party name, source.
- `fda_inspection_event/6`: inspection id, facility id, start date, end date,
  inspecting body, source.
- `fda_violation_citation/4`: violation-or-letter subject, citation, role,
  source.
- `fda_response_requirement/6`: letter, action, deadline, recipient/channel,
  consequence/purpose, source.
- `fda_consultant_recommendation/4`: letter, consultant kind, action, source.
- `fda_conclusion_scope/4`: letter, scope kind, scope value, source.

IDs and source coordinates are variables in `expected_facts.pl`; semantic slots
are concrete governed atoms.

## Violation Category Rationale

- Violation 1: 21 CFR 211.22(d), quality unit responsibilities/procedures ->
  `quality_unit_failure`.
- Violation 2: 21 CFR 211.113(b), written procedures to prevent
  microbiological contamination of sterile drug products ->
  `contamination_control`.
- Violation 3: 21 CFR 211.28(a), clothing appropriate to protect drug product
  from contamination -> `contamination_control`.
- Violation 4: 21 CFR 211.42(c)(10)(vi), equipment used to control aseptic
  conditions -> `aseptic_processing`.
- Violation 5: 21 CFR 211.42(c)(10)(v), cleaning/disinfecting to produce
  aseptic conditions -> `aseptic_processing`.
- Violation 6: 21 CFR 211.188, batch production and control records ->
  `other_registered_category` because the current closed FDA category palette
  does not yet include a more specific recordkeeping category.

## Deliberate Omissions

- No prior warning letter is stated -> no `fda_prior_warning_letter/5` row.
- No meeting/teleconference is stated -> no `fda_regulatory_meeting/4` row.
- No FEI number appears. Because the current FDA domain accountability registry
  only requires explicit signatory omission handling, the fixture does not add a
  FEI `domain_omission/5` row.
- The consultant recommendation does not cite 21 CFR 211.34, so there is no
  consultant-qualification citation row.

## Hard-To-Represent Facts

- `fda_facility_identity/5` has an identifier slot, but this source excerpt does
  not state FEI. The expected row uses `registered_outsourcing_facility`, drawn
  from the source statement that the firm registered the facility as an
  outsourcing facility under FDCA section 503B. This is a pressure point for the
  current carrier shape.
- The signatory title chain is not represented because
  `fda_correspondence_party/5` preserves party role and party name, not title.
- 501(a)(2)(A) insanitary-conditions adulteration required adding
  `adulteration_insanitary_conditions` to the closed
  `fda_adulteration_basis/5` basis-kind palette. This is a domain-pack extension
  from a real FDA warning-letter source, not a new predicate family.

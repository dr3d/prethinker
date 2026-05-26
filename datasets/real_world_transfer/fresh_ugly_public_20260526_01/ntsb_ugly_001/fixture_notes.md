# Fixture Notes — ntsb_ugly_001

## Source

- Public URL: https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/193599/pdf
- NTSB Accident Number: WPR24LA063
- Investigation Docket: https://data.ntsb.gov/Docket?ProjectID=193599
- Collected: 2026-05-26 (UTC)
- Document type: NTSB Aviation Investigation Final Report (6-page PDF), Class 3 investigation, undetermined cause.

## Why messy

- **Owner-builder aircraft make.** The "Aircraft Make" field reads BENDER THOMAS G (per FAA experimental-amateur-built registration convention — the kit-builder's name is the registered make). The narrative separately describes the aircraft as a "Vans RV-6," referring to the kit type designer. Both are correct but they refer to different roles. Trivially conflatable; the report makes no attempt to reconcile.
- **Implausible numerical claim preserved verbatim.** Analysis says the pilot rebuilt an engine "70 yrs ago." Factual Information says "in 1954." Pilot Age is "81." 81 − 70 = 11. The report makes no editorial comment on the 11-year-old engine rebuilder.
- **Two phrasings for the same date.** "70 yrs ago" in the Analysis (relative) vs. "in 1954" in the Factual Information (absolute). Same underlying event.
- **Time format inconsistency.** Page 1 header gives "10:30 Local" (HH:MM, no timezone). Page 3 narrative gives "1030 mountain standard time" (HHMM military, explicit timezone). Same instant, two formats.
- **Blank-after-colon fields as no-data sentinels.** Multiple structured fields are present but empty: "Last Revision Date:", "Toxicology Performed:", "Last FAA Medical Exam:", "Last Flight Review or Equivalent:", "Visibility (RVR):", "Departure Time:", and the slash-with-blanks pattern "Turbulence Type Forecast/Actual: /". Distinguishing a blank field (=no-data, present-but-empty) from a missing field (=not collected) requires page-structure awareness.
- **Slash-with-blanks pair.** "Turbulence Type Forecast/Actual: /" encodes two blank values separated by a slash within a single label-value cell.
- **Concatenated count-and-type field.** "Engines: 1 Reciprocating" packs count (1) and type (Reciprocating) into one field with whitespace separation.
- **Packed list inside one field.** "Flight Time:" holds six comma-separated subfields (Total all aircraft, Total make/model, PIC, last 90 days, last 30 days, last 24 hours).
- **Name format inconsistency in attribution.** IIC is "Baker, Daniel" (lastname-first). Additional Participating Person is "Geary Monckton; FAA; Albuquerque, NM" (firstname-first, semicolon-delimited). Two conventions in adjacent lines.
- **"On file" as redaction-equivalent.** Registered Owner and Operator both read "On file" — a sentinel meaning "withheld from this public report"; not the same as a blank or unknown.
- **Medical history split across structured and narrative.** "Medical Certification: Unknown" and "Last FAA Medical Exam:" blank in structured Page 4. The Page 3 narrative says the last application was "denied in 2009" — a specific fact present only in prose.
- **Round-robin local flight.** Departure Point and Destination both read "Moriarty, NM"; no Departure Time given.
- **Investigation limitation pile-up.** Pilot uncontactable, logbooks not located, no on-scene NTSB visit (Class 3). All three limitations are stated, and the undetermined probable cause is a direct consequence.
- **Statutory citations in closing boilerplate.** The closing prose cites 49 CFR § 831.4 (quoting it) and 49 U.S.C. § 1154(b) — these are not flagged with footnote numbers or as legal citations in the layout; they sit inline in prose.
- **Two-level findings taxonomy.** Findings list uses "(Category) - (Subcategory)" two-level format with categories like "Aircraft (general)" and "Aircraft Altitude."
- **Section split across pages.** The grouping "Probable Cause and Findings" is split: Probable Cause sentence on Page 1, Findings list on Page 2 under its own subheader.

## What shapes are pressured

- Entity canonicalization (owner-builder vs. kit-maker).
- Numerical sanity-checking across sections.
- Relative-time vs. absolute-date phrasings for the same event.
- Time format inconsistency (colon vs. military, implicit vs. explicit timezone).
- Blank field detection and interpretation as no-data sentinel.
- Slash-with-blanks pair encoding.
- Concatenated multi-value field parsing.
- Packed-list-inside-one-field extraction with comma-separated subfields.
- Name format inconsistency within a single section.
- "On file" as redaction-equivalent sentinel.
- Narrative-only details that contradict or supplement blank structured fields.
- Round-robin (departure = destination) flight detection.
- Investigation limitation chain → undetermined cause.
- Statutory citation extraction from inline prose.
- Two-level taxonomy parsing.
- Section-split-across-pages reconstruction.

## Attachments, redactions, tables, missing fields

- Attachments: investigation docket linked separately (data.ntsb.gov/Docket?ProjectID=193599); not extracted as part of this fixture.
- Redactions: Registered Owner = "On file"; Operator = "On file." Several structured fields blank (Last Revision Date, Toxicology Performed, Last FAA Medical Exam, Last Flight Review or Equivalent, Visibility (RVR), Departure Time, Turbulence pair).
- Tables: two-column label/value grids on Pages 1, 4, 5, 6.
- Missing fields: Pilot name; specific 6-to-12-month prior-event date; biannual flight review last date ("in decades" — no number); revision date; toxicology results; current medical certification status (Unknown).

## Extraction caveats

- Preserve "BENDER THOMAS G" verbatim as the registered Aircraft Make. Do not silently substitute "Van's Aircraft" or "Vans"; tag the narrative-mentioned "Vans RV-6" as the kit family, separately.
- Preserve "70 yrs ago" verbatim; tag with cross-reference to "1954" in Factual Information; flag the numerical implausibility with respect to pilot age 81 without rewriting either value.
- Preserve "Age: 81,Male" verbatim (note the missing space after the comma).
- Treat "On file" as a sentinel meaning "registered owner/operator information withheld from the public report," distinct from a blank or unknown field.
- Treat blank-after-colon fields (e.g., "Last Revision Date:") as "no data on this page," not as "not applicable." Where context indicates not-applicable (e.g., Total Injuries reconciliation), tag explicitly.
- Treat "Passenger Injuries: N/A" as 0 for arithmetic reconciliation against Total Injuries, but preserve the N/A literal in the source view.
- Treat the slash-with-blanks pattern "Turbulence Type Forecast/Actual: /" as one labeled field containing two blank sub-values.
- Bind the probable cause to "A loss of engine power for undetermined reasons" verbatim; do not paraphrase to a mechanical or pilot cause.
- Bind "denied in 2009" to the narrative on Page 3; the Page 4 structured fields do not capture this fact and must not be reported as containing it.
- Bind statutory citations to the closing boilerplate prose, not to the body of the investigation.
- Preserve "Baker, Daniel" lastname-first; preserve "Geary Monckton" firstname-first; do not normalize either to the other convention.
- The probable cause sentence and the findings list are different objects with different source coordinates (Page 1 vs. Page 2); do not flatten them into a single "findings" object.

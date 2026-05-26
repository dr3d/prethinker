# Authored QA With Answers - ntsb_ugly_001

## Questions and Reference Answers

**1. What is the NTSB Accident Number for this investigation?**

**Reference answer.**
WPR24LA063. Appears on the Page 1 header and repeated as a page-footer identifier on Pages 2–6.

**Source coordinates.** Page 1 header; Pages 2–6 footer

**Pressure tags.** identifier_format, repeated_identifier

**2. What is the registration (tail number) of the accident aircraft?**

**Reference answer.**
N111XF. Appears in the Page 1 header (Registration: N111XF) and is repeated in the Factual Information narrative and in the Aircraft and Owner/Operator Information block on Page 4.

**Source coordinates.** Page 1 header; Page 3 narrative; Page 4 Aircraft and Owner/Operator Information

**Pressure tags.** repeated_identifier

**3. What aircraft make does the NTSB report list, and what model/series?**

**Reference answer.**
Aircraft Make: BENDER THOMAS G. Model/Series: RV-6. This is the owner-builder convention used by the FAA registry for experimental amateur-built aircraft — the name of the kit-builder is recorded as the 'make.' The narrative separately describes the aircraft as a 'Vans RV-6,' referring to the kit manufacturer (Van's Aircraft); these are two different things and the report does not reconcile them.

**Source coordinates.** Page 1 header (Aircraft); Page 4 Aircraft and Owner/Operator Information (Aircraft Make, Model/Series); Page 3 Factual Information narrative ('Vans RV-6')

**Pressure tags.** entity_canonicalization, owner_builder_vs_kit_maker, discrepancy_between_sections

**4. Where did the accident occur (city, state), and what was the airport identifier?**

**Reference answer.**
Moriarty, New Mexico. Airport: MORIARTY MUNI, identifier 0E0. The pilot departed from and was returning to Moriarty (departure and destination both listed as Moriarty, NM — a local flight).

**Source coordinates.** Page 1 header (Location); Page 5 Airport Information; Page 5 Meteorological Information and Flight Plan (Departure Point, Destination)

**Pressure tags.** round_robin_flight, airport_identifier_format

**5. What does the NTSB list as the probable cause of this accident?**

**Reference answer.**
'A loss of engine power for undetermined reasons.' This is a qualified/undetermined-cause finding rather than an assignment of mechanical, environmental, or pilot cause.

**Source coordinates.** Page 1, 'Probable Cause and Findings' section

**Pressure tags.** qualified_finding, undetermined_cause

**6. On which page of the report does the Probable Cause section appear?**

**Reference answer.**
Page 1. The Probable Cause section follows directly after the Analysis section on Page 1, before the Page 1/Page 2 break. The two-level findings list, also part of the 'Probable Cause and Findings' grouping, appears on Page 2 under its own 'Findings' header.

**Source coordinates.** Page 1 (Probable Cause and Findings); Page 2 (Findings list)

**Pressure tags.** section_split_across_pages

**7. In which named section of the report is the pilot's medical-certificate history described?**

**Reference answer.**
The pilot's medical-certificate history is split across two locations: (a) a narrative reference in the Factual Information section on Page 3 ('his last recorded application for a medical certificate was denied in 2009'), and (b) two structured fields on the Page 4 Pilot Information block — 'Medical Certification: Unknown' and 'Last FAA Medical Exam:' (blank). The 'denied in 2009' detail is only in the narrative; the Page 4 fields do not capture it.

**Source coordinates.** Page 3 Factual Information narrative; Page 4 Pilot Information (Medical Certification, Last FAA Medical Exam)

**Pressure tags.** narrative_only_vs_structured, blank_field_with_narrative_detail

**8. The "Findings" section lists two two-level findings. On which page do they appear?**

**Reference answer.**
Page 2. The two findings are: 'Aircraft (general) - Unknown/Not determined' and 'Aircraft Altitude - Attain/maintain not possible.' Each follows the NTSB two-level taxonomy of (category) - (subcategory).

**Source coordinates.** Page 2, Findings section

**Pressure tags.** two_level_taxonomy

**9. The narrative says the pilot rebuilt an engine "70 yrs ago" in one place and "in 1954" in another. In which two sections of the report do these two phrasings appear?**

**Reference answer.**
'70 yrs ago' appears in the Analysis section on Page 1: 'a used fuel pump that was on an engine that he rebuilt 70 yrs ago.' 'in 1954' appears in the Factual Information section on Page 3: 'when he rebuilt it in 1954.' The two phrasings refer to the same event but use a relative-time vs. absolute-date format. Both are consistent with each other (1954 → about 70 years before the 2024 accident) but inconsistent with the pilot's biographical possibility (see cross-section).

**Source coordinates.** Page 1 Analysis; Page 3 Factual Information narrative

**Pressure tags.** relative_vs_absolute_date, duplicate_with_different_phrasing

**10. Under which subsection on Page 6 are the IIC and "Additional Participating Persons" identified?**

**Reference answer.**
The 'Administrative Information' section on Page 6. Investigator In Charge (IIC): Baker, Daniel (lastname-first format). Additional Participating Persons: 'Geary Monckton; FAA; Albuquerque, NM' (semicolon-separated name/organization/city; firstname-first format). The two attribution conventions differ within the same section.

**Source coordinates.** Page 6, Administrative Information

**Pressure tags.** name_format_inconsistency, lastname_first_vs_firstname_first

**11. List all the pilot ratings (Airplane Rating, Instrument Rating, Instructor Rating, Other Aircraft Rating) and their values.**

**Reference answer.**
Airplane Rating(s): Single-engine land. Other Aircraft Rating(s): None. Instrument Rating(s): None. Instructor Rating(s): None. Source order in the Pilot Information block alternates with non-rating fields (Seat Occupied, Restraint Used, Second Pilot Present); the four ratings are not contiguous in the source.

**Source coordinates.** Page 4 Pilot Information

**Pressure tags.** non_contiguous_field_extraction, structured_field_block

**12. List, in the order they appear in the report, the six flight-time totals reported for the pilot.**

**Reference answer.**
(1) 2943 hours — Total, all aircraft; (2) 943 hours — Total, this make and model; (3) 943 hours — Pilot In Command, all aircraft; (4) 15 hours — Last 90 days, all aircraft; (5) 7 hours — Last 30 days, all aircraft; (6) 0 hours — Last 24 hours, all aircraft. All six are concatenated into a single 'Flight Time:' field on Page 4 as a comma-separated list.

**Source coordinates.** Page 4 Pilot Information, Flight Time field

**Pressure tags.** packed_list_in_single_field, comma_separated_subfields

**13. List the four labeled fields on Page 5 that are present but contain no value (blank-after-colon fields).**

**Reference answer.**
From the Meteorological Information and Flight Plan block: 'Visibility (RVR):' (blank), 'Turbulence Type Forecast/Actual: /' (slash with blanks on both sides), 'Turbulence Severity Forecast/Actual: /' (slash with blanks on both sides), and 'Departure Time:' (blank). Additionally on Page 4 Pilot Information: 'Toxicology Performed:', 'Last FAA Medical Exam:', 'Last Flight Review or Equivalent:' are blank (page 4, not page 5). Strictly limiting to Page 5 fields, the four are as listed above. Treat slash-with-blanks as a single 'no-data' marker per pair, not two empty fields.

**Source coordinates.** Page 5 Meteorological Information and Flight Plan

**Pressure tags.** blank_field_detection, slash_separated_pair_blanks, sentinel_for_missing_data

**14. List the engine identification fields (manufacturer, model/series, rated power, count, type).**

**Reference answer.**
Engine Manufacturer: Lycoming. Engine Model/Series: O-320 A-28. Rated Power: 150 Horsepower. Engines: 1. Type: Reciprocating (the 'Engines: 1 Reciprocating' field concatenates count and type). All five values appear in the Page 4 Aircraft and Owner/Operator Information block.

**Source coordinates.** Page 4 Aircraft and Owner/Operator Information

**Pressure tags.** concatenated_field_count_and_type, non_contiguous_field_extraction

**15. List, in the order they appear in the Aviation Investigation Final Report header on Page 1, the eight header label-value pairs.**

**Reference answer.**
(1) Location: Moriarty, New Mexico; (2) Accident Number: WPR24LA063; (3) Date & Time: January 2, 2024, 10:30 Local; (4) Registration: N111XF; (5) Aircraft: BENDER THOMAS G RV-6; (6) Aircraft Damage: Substantial; (7) Defining Event: Unknown or undetermined; (8) Injuries: 1 Minor. A ninth line follows (Flight Conducted Under: Part 91: General aviation - Personal) but is on its own line outside the four-row label/value grid.

**Source coordinates.** Page 1 header (label/value grid)

**Pressure tags.** two_column_label_value_grid, row_count_disambiguation

**16. What is the Original Publish Date of the report, and what is the Last Revision Date?**

**Reference answer.**
Original Publish Date: April 24, 2025. Last Revision Date: (blank — the field is present but has no value). The report has not been revised since original publication.

**Source coordinates.** Page 6 Administrative Information

**Pressure tags.** blank_field_as_no_revision, negative_fact_from_blank

**17. What was the local time of the accident, and what was the time-zone-explicit local time per the Factual Information narrative?**

**Reference answer.**
Page 1 header: '10:30 Local.' Factual Information narrative on Page 3: '1030 mountain standard time.' The two expressions refer to the same instant. The header uses HH:MM format without time-zone identification; the narrative uses HHMM (military-style, no colon) with explicit time zone.

**Source coordinates.** Page 1 header (Date & Time); Page 3 Factual Information narrative

**Pressure tags.** time_format_inconsistency, colon_vs_military_format, implicit_vs_explicit_timezone

**18. The pilot reports a prior engine-failure event. How long before the accident did that prior event occur, and how was it resolved?**

**Reference answer.**
The prior engine-failure event occurred '6 to 12 months before the accident' — a range, not a fixed date. The pilot resolved it by attributing the loss of power to a failed fuel pump and replacing the failed pump with a used fuel pump that had been originally installed on a Lycoming engine when the pilot rebuilt that engine in 1954 (Factual Information narrative) / 'rebuilt 70 yrs ago' (Analysis).

**Source coordinates.** Page 1 Analysis; Page 3 Factual Information narrative

**Pressure tags.** time_range_not_point, prior_event_attribution

**19. According to the report, when was the pilot's last recorded application for a medical certificate, and what was its outcome?**

**Reference answer.**
The pilot's last recorded application for a medical certificate was in 2009 and was denied (per FAA inspectors, as cited in the Page 3 Factual Information narrative). The Page 4 'Last FAA Medical Exam:' field is blank, and 'Medical Certification:' is listed as 'Unknown' — so the structured fields do not capture the 2009 denial.

**Source coordinates.** Page 3 Factual Information narrative; Page 4 Pilot Information (blank fields)

**Pressure tags.** denial_not_lapse, narrative_outranks_structured_blank

**20. Does the NTSB assign fault or legal liability in this report, and which statutory authority does the report cite for that position?**

**Reference answer.**
No. The closing boilerplate explicitly states: 'The NTSB does not assign fault or blame for an accident or incident.' The report cites two authorities: (a) Title 49 Code of Federal Regulations section 831.4, quoted in the report ('accident/incident investigations are fact-finding proceedings with no formal issues and no adverse parties … and are not conducted for the purpose of determining the rights or liabilities of any person'); and (b) Title 49 United States Code section 1154(b), which prohibits admission of NTSB report content into evidence in civil actions for damages.

**Source coordinates.** Page 6 closing boilerplate

**Pressure tags.** statutory_citation_in_boilerplate, no_fault_no_liability_doctrine

**21. The report states that the airframe and engine logbooks were not located. What investigative consequence followed from that, combined with the inability to contact the pilot?**

**Reference answer.**
Two combined investigation limitations are described: (1) 'Attempts to contact the pilot to access the airplane and engine for an examination were unsuccessful,' and (2) 'The airframe and engine logbooks were not located during the investigation.' Their combined consequence, as stated by the NTSB: 'Although the fuel pump was reportedly 70 yrs old, investigators could not determine if it failed. Therefore, the reason for the loss of engine power could not be determined.' The undetermined cause is a direct consequence of the access and documentary limitations.

**Source coordinates.** Page 1 Analysis; Page 3 Factual Information narrative

**Pressure tags.** investigation_limitations, causal_chain_to_undetermined_cause

**22. What is the Investigation Class assigned to this case, and what does the report note about NTSB on-scene presence?**

**Reference answer.**
Investigation Class: Class 3. The report includes the note: 'The NTSB did not travel to the scene of this accident.' The Class 3 designation and the no-on-scene-travel note appear together in the Page 6 Administrative Information section.

**Source coordinates.** Page 6 Administrative Information

**Pressure tags.** investigation_class_taxonomy, no_on_scene_note

**23. The pilot is listed as 81 years old. The Analysis section refers to an engine rebuild "70 yrs ago." Compare the two values and identify the numerical sanity issue, if any.**

**Reference answer.**
The pilot is listed on Page 4 as 'Age: 81,Male.' The Analysis section on Page 1 says the engine was rebuilt '70 yrs ago' (i.e., circa 1954, as corroborated by Page 3). If accurate, the pilot would have been approximately 11 years old when he rebuilt a Lycoming engine. This is implausible as a literal claim but is presented in the report without commentary or correction. The report does not flag the inconsistency; an extractor should preserve both values verbatim and flag the implausibility as a data-quality concern rather than choose between them.

**Source coordinates.** Page 1 Analysis; Page 3 Factual Information narrative; Page 4 Pilot Information (Age)

**Pressure tags.** numerical_sanity_check_across_sections, implausible_assertion_preserved_verbatim, no_editorial_correction

**24. Compare the "Aircraft Make" field on Page 4 against the aircraft description in the Factual Information narrative on Page 3. Identify and explain the apparent discrepancy.**

**Reference answer.**
Page 4 Aircraft and Owner/Operator Information lists 'Aircraft Make: BENDER THOMAS G' (the owner-builder's name, per FAA experimental-amateur-built registration convention). The Page 3 Factual Information narrative refers to the aircraft as 'an experimental amateur-built Vans RV-6' (Van's Aircraft is the original kit designer/manufacturer). The two are not interchangeable: 'BENDER THOMAS G' is the registered builder of this specific airframe (Serial Number 24474), while 'Vans' is the kit type designer. Both are correct; they refer to different roles. The report does not explain this distinction, so an extractor should treat 'BENDER THOMAS G' as the structured-field manufacturer and 'Vans' as the kit family.

**Source coordinates.** Page 3 Factual Information narrative; Page 4 Aircraft and Owner/Operator Information

**Pressure tags.** entity_canonicalization, owner_builder_vs_kit_maker, structured_vs_narrative_label

**25. The "Total Injuries" line on Page 5 reads "1 Minor." Reconstruct that figure from the three constituent injury fields (Crew, Passenger, Ground). Is the total consistent?**

**Reference answer.**
Crew Injuries: 1 Minor. Passenger Injuries: N/A. Ground Injuries: (blank). Total Injuries: 1 Minor. The total is consistent with the Crew Injuries figure alone, treating N/A and blank as 0 (or as not-applicable). 'Passenger Injuries: N/A' is most naturally read as 'no passengers were aboard,' consistent with the Pilot Information line 'Second Pilot Present: No' and the Seats: 2 / Single-engine personal flight pattern. Treat the total as built from Crew + Passenger (0) + Ground (0) = 1 Minor.

**Source coordinates.** Page 5 Wreckage and Impact Information

**Pressure tags.** sum_reconstruction, na_vs_zero_vs_blank, injury_taxonomy

# Authored QA With Answers - ntsb_ugly_002

## Questions and Reference Answers

**1. What is the NTSB Investigation ID for this case?**

**Reference answer.**
RRD26FR001. Appears in the 'Investigation Details' block and in the 'Docket' section, and is also part of the source URL.

**Source coordinates.** Investigation Details block; Docket section; URL

**Pressure tags.** repeated_identifier, id_format

**2. On what date and at approximately what local time did the accident occur?**

**Reference answer.**
October 19, 2025, at about 9:32 a.m. local time. Footnote 1 specifies 'All times in this report are local.'

**Source coordinates.** What Happened section, paragraph 1; Investigation Details (Event Date 10/19/2025); footnote 1

**Pressure tags.** redundant_local_time_clarification, dual_date_formats

**3. Where did the accident occur (city, state) and at what milepost?**

**Reference answer.**
Columbus, Montana. The train H-ALTPAS1-13A (on which the conductor was working) was parked in the Columbus siding, adjacent and north of the main track around milepost 40.1 on BNSF's MRL Second Subdivision.

**Source coordinates.** What Happened, paragraph 1; Investigation Details (Location: Columbus, MT)

**Pressure tags.** location_with_milepost, subdivision_naming

**4. What is the status of the investigation as of this report?**

**Reference answer.**
Ongoing. Stated explicitly as 'Status: Ongoing' in the Investigation Details block and also as 'The investigation is ongoing' near the end of the What Happened narrative. The preliminary-status caveat italicized at the top of the narrative — 'This information is preliminary and subject to change.' — reinforces this.

**Source coordinates.** What Happened preamble; What Happened final paragraph; Investigation Details (Status: Ongoing)

**Pressure tags.** redundant_status_statements, preliminary_caveat

**5. The conductor was struck by which train, and what speed was that train traveling?**

**Reference answer.**
Empty BNSF grain train X-INBMCU9-17M, traveling eastbound about 37 mph on the main track. The train was empty (no cargo) at the time. The 37 mph figure is qualified by 'about' and is below the 60 mph maximum authorized speed for that segment per footnote 3.

**Source coordinates.** What Happened, paragraph 2; footnote 3

**Pressure tags.** approximate_speed, train_identifier_format, empty_vs_loaded_train

**6. In which section of the page does the preliminary-status caveat appear, and what does it say?**

**Reference answer.**
At the top of the 'What Happened' section, immediately under the section heading and before paragraph 1 of the narrative, in italics: 'This information is preliminary and subject to change.' It is the first content line of the What Happened section.

**Source coordinates.** What Happened section, italicized preamble line

**Pressure tags.** italicized_caveat, section_preamble

**7. Where on the page is the milepost noted, and what is its value?**

**Reference answer.**
Inside the What Happened narrative, paragraph 1: 'around milepost 40.1 on BNSF's MRL Second Subdivision.' The milepost is given as approximate ('around'). It does not appear in any structured Investigation Details field.

**Source coordinates.** What Happened, paragraph 1

**Pressure tags.** approximate_milepost, narrative_only_fact

**8. Where on the page is the parties-to-the-investigation list, and how many parties are listed?**

**Reference answer.**
In the final paragraph of the What Happened section. Five parties are listed: (1) the Federal Railroad Administration; (2) the State of Montana; (3) BNSF; (4) the Brotherhood of Locomotive Engineers and Trainmen; and (5) the International Association of Sheet Metal, Air, Rail and Transportation Workers. Note that BNSF appears both as a party to the investigation and as the operator of both trains involved.

**Source coordinates.** What Happened, final paragraph (Parties to the investigation include...)

**Pressure tags.** semicolon_separated_list, operator_also_party

**9. Which of the footnotes defines the term "in the foul"?**

**Reference answer.**
Footnote 4. The definition reads: 'In the foul means close enough to a track to be struck by a moving train or within 4 feet of the nearest rail.' The term 'foul' is italicized in the footnote definition.

**Source coordinates.** Footnote 4

**Pressure tags.** domain_specific_terminology, footnote_glossary

**10. Which on-page sections are present but empty in this preliminary report?**

**Reference answer.**
Four sections are present in the page structure but contain no substantive content: 'What We Found,' 'What We Recommended,' 'Lessons Learned,' and 'Video.' Additionally 'Safety Alert' contains only an empty link. These empties are structural placeholders consistent with the preliminary-status caveat — they are reserved for content that will be added when the final report is issued.

**Source coordinates.** What We Found; What We Recommended; Lessons Learned; Video; Safety Alert

**Pressure tags.** empty_section_placeholders, preliminary_stage_indicator

**11. List, in source order, the five parties to the investigation.**

**Reference answer.**
(1) Federal Railroad Administration; (2) State of Montana; (3) BNSF; (4) Brotherhood of Locomotive Engineers and Trainmen; (5) International Association of Sheet Metal, Air, Rail and Transportation Workers. Semicolon-delimited in the source, with 'and' before the final item. The list is presented as 'Parties to the investigation include...' — semantically 'include' could be open-ended, but in practice for an NTSB preliminary report the parties list is the complete enumeration as of the report date.

**Source coordinates.** What Happened, final paragraph

**Pressure tags.** semicolon_separated_list, include_open_vs_closed_semantics

**12. List the two train identifiers mentioned in the report and the role of each in the accident.**

**Reference answer.**
(1) H-ALTPAS1-13A — a westbound BNSF mixed-freight train. Parked in the Columbus siding. The conductor (the fatality) was part of the crew sent out to operate this train and was working on its railcars (releasing handbrakes) when struck. (2) X-INBMCU9-17M — an empty BNSF grain train, traveling eastbound on the main track at about 37 mph. This is the train that struck and killed the conductor. The two trains were on different tracks (siding vs. main).

**Source coordinates.** What Happened, paragraphs 1 and 2

**Pressure tags.** alphanumeric_identifier_format, role_attribution

**13. List the six categories of investigative activity the NTSB conducted while on scene.**

**Reference answer.**
From paragraph 3 of What Happened: (1) conducted accident reenactments; (2) reviewed data from locomotive event recorders and inward- and outward-facing image recorders; (3) inspected train equipment and track structures; (4) conducted sight distance observations; (5) reviewed BNSF's policies and procedures; (6) completed interviews. The list uses comma-and-then-and structure rather than bullets.

**Source coordinates.** What Happened, paragraph 3

**Pressure tags.** inline_comma_list, and_separated_final_item

**14. List the three focus areas of future investigative activity.**

**Reference answer.**
From paragraph 4 of What Happened: (1) communications among railroad employees; (2) crew qualifications and training; (3) railroad operating rules regarding safety around tracks. The list uses comma-and-then-and structure in a single sentence.

**Source coordinates.** What Happened, paragraph 4

**Pressure tags.** forward_looking_obligations, inline_comma_list

**15. List, in source order, the four footnotes and the content of each.**

**Reference answer.**
Footnote 1: 'All times in this report are local.' Footnote 2: 'The subdivision was previously leased from BNSF by Montana Rail Link, which was acquired by BNSF in 2022.' Footnote 3: 'The maximum authorized speed for this segment of track is 60 mph.' Footnote 4: 'In the foul means close enough to a track to be struck by a moving train or within 4 feet of the nearest rail.' Footnotes 1 and 4 attach to terminological references ('local time,' 'in the foul'); footnotes 2 and 3 attach to substantive contextual facts (subdivision history, speed limit).

**Source coordinates.** Footnotes 1–4 (below horizontal rule)

**Pressure tags.** footnote_extraction, footnote_type_taxonomy

**16. The conductor's train (H-ALTPAS1-13A) was traveling in which direction, and the train that struck the conductor (X-INBMCU9-17M) in which direction?**

**Reference answer.**
H-ALTPAS1-13A was westbound (per paragraph 1: 'westbound BNSF mixed-freight train H-ALTPAS1-13A'). Note that at the time of the accident this train was parked in the siding, not moving. X-INBMCU9-17M was eastbound (per paragraph 2: 'BNSF grain train X-INBMCU9-17M was traveling eastbound about 37 mph on the main track'). The two trains' nominal directions were opposite.

**Source coordinates.** What Happened, paragraphs 1 and 2

**Pressure tags.** nominal_direction_vs_actual_motion, opposite_direction_trains

**17. From the moment the engineer of train X-INBMCU9-17M observed the conductor to the moment of impact, what two actions did the engineer take, and what distance did the train travel?**

**Reference answer.**
Per paragraph 2: 'The engineer of train X-INBMCU9-17M sounded the horn upon observing the conductor and initiated an emergency application of the air brakes. The train then traveled about 232 feet before striking the conductor.' Two actions: (1) sounded the horn; (2) initiated emergency air brake application. Distance: about 232 feet (qualified by 'about').

**Source coordinates.** What Happened, paragraph 2

**Pressure tags.** sequence_of_actions, approximate_distance, post_observation_distance

**18. The subdivision is BNSF's MRL Second Subdivision. According to footnote 2, what is the history of that subdivision's ownership?**

**Reference answer.**
Footnote 2 states: 'The subdivision was previously leased from BNSF by Montana Rail Link, which was acquired by BNSF in 2022.' The lease ran from BNSF to Montana Rail Link in the past; Montana Rail Link was then acquired by BNSF in 2022, ending the lease arrangement. The 'MRL' in the subdivision name (MRL Second Subdivision) preserves the legacy Montana Rail Link naming despite ownership unification.

**Source coordinates.** Footnote 2

**Pressure tags.** historical_entity_lease, legacy_naming_after_acquisition, ownership_transition

**19. What was the maximum authorized speed for the segment of track on which the striking train was traveling, and how does that compare to the train's actual speed?**

**Reference answer.**
Maximum authorized speed: 60 mph (footnote 3). Actual speed: about 37 mph. The train was traveling well below the maximum authorized speed for that segment. The report does not assert that the speed was a factor in the accident; the footnote merely provides the speed-limit context.

**Source coordinates.** What Happened, paragraph 2; footnote 3

**Pressure tags.** actual_vs_authorized_speed, below_limit_observation, footnote_provided_context

**20. According to the preliminary report, has the NTSB issued any safety recommendations or findings yet? Cite specific section status.**

**Reference answer.**
No. The 'What We Found,' 'What We Recommended,' and 'Lessons Learned' sections are present in the page structure but empty — they have headers but no content beneath them. The 'Safety Alert' section contains only an empty link. The preliminary-status caveat at the top of the What Happened section ('This information is preliminary and subject to change') and the explicit 'The investigation is ongoing' statement in paragraph 4 reinforce that no formal findings or recommendations have been issued.

**Source coordinates.** What We Found; What We Recommended; Lessons Learned; Safety Alert; What Happened preamble and paragraph 4

**Pressure tags.** negative_fact_from_empty_sections, absence_of_findings, preliminary_stage

**21. The investigation will focus on three areas going forward. Which area most directly addresses procedural safety vs. personnel-readiness vs. inter-employee coordination?**

**Reference answer.**
Three focus areas (paragraph 4): (1) 'communications among railroad employees' — inter-employee coordination; (2) 'crew qualifications and training' — personnel readiness; (3) 'railroad operating rules regarding safety around tracks' — procedural safety. The mapping is one-to-one: communications → coordination; qualifications and training → personnel readiness; operating rules → procedural safety. The report does not weight these or rank them.

**Source coordinates.** What Happened, paragraph 4

**Pressure tags.** taxonomy_mapping, forward_looking_focus_areas

**22. What does the report identify as the conductor's specific task at the moment immediately before the accident, and where was the conductor positioned relative to the main track?**

**Reference answer.**
Task: 'walking east between the siding track and the main track, releasing the handbrakes on the railcars of train H-ALTPAS1-13A.' Position relative to main track: 'walking in the foul of the main track just before the accident.' Per footnote 4, 'in the foul' means 'close enough to a track to be struck by a moving train or within 4 feet of the nearest rail.' The two descriptions are consistent: the conductor was performing handbrake-release duties on H-ALTPAS1-13A in the siding but had moved into the fouling distance of the adjacent main track.

**Source coordinates.** What Happened, paragraph 2; footnote 4

**Pressure tags.** task_attribution, fouling_distance_definition, narrative_with_glossary_footnote

**23. The report gives the striking train's speed as "about 37 mph" and the maximum authorized speed as "60 mph" (footnote 3). The conductor's own train (H-ALTPAS1-13A) was parked. Reconcile the speed-related facts for both trains.**

**Reference answer.**
Train X-INBMCU9-17M (the striking train) was in motion: actual speed about 37 mph, below the 60 mph maximum authorized speed for that segment of main track. Train H-ALTPAS1-13A (the conductor's assigned train) was at speed 0 — parked in the Columbus siding while the conductor released handbrakes. The two trains were not in relative motion as a pair; only the eastbound grain train was moving. The conductor was being struck by a passing train while standing in the foul of the main track during stationary work on his own parked train.

**Source coordinates.** What Happened, paragraphs 1 and 2; footnote 3

**Pressure tags.** stationary_vs_moving_train, two_train_speed_reconciliation, below_limit_vs_at_limit

**24. The "What Happened" narrative is the only substantive content on the page. The sections "What We Found," "What We Recommended," and "Lessons Learned" are present but empty. What does this combination of substantive narrative + empty findings sections indicate about the report stage?**

**Reference answer.**
The combination indicates the report is at the *preliminary* stage of the NTSB investigation lifecycle, not the final stage. NTSB preliminary reports document only the factual narrative (what happened, where, when, who, parties involved, on-scene investigative activity) and explicitly defer findings, recommendations, and lessons learned until the final report. The italicized 'This information is preliminary and subject to change' caveat at the top of the narrative is the canonical signal. The Status field 'Ongoing' is the structured counterpart. An extractor should treat the empty sections as 'reserved for the final report,' not as 'NTSB found nothing.'

**Source coordinates.** What Happened preamble; What We Found, What We Recommended, Lessons Learned (empty); Investigation Details Status: Ongoing

**Pressure tags.** preliminary_vs_final_report_stage, empty_sections_as_reservation, lifecycle_inference

**25. The narrative describes BNSF's "MRL Second Subdivision," but footnote 2 explains that "MRL" refers to a previously separate entity (Montana Rail Link) that was acquired by BNSF in 2022. What is the implication for entity canonicalization of "MRL" within this report?**

**Reference answer.**
Within this report, 'MRL' is preserved as a legacy naming artifact embedded in the subdivision name 'MRL Second Subdivision' — a fixed proper noun denoting the track infrastructure. As of October 19, 2025 (the accident date), Montana Rail Link no longer exists as an independent operator: BNSF acquired it in 2022 (footnote 2). The current operator and owner of the track is BNSF. Implication: 'MRL' should be canonicalized as a track-segment-name fragment, not as an active corporate entity. BNSF is the sole rail operator entity referenced in the report's body. Montana Rail Link is referenced only historically and only in footnote 2.

**Source coordinates.** What Happened, paragraph 1 (MRL Second Subdivision); footnote 2

**Pressure tags.** legacy_entity_in_proper_noun, post_acquisition_naming, entity_canonicalization_historical

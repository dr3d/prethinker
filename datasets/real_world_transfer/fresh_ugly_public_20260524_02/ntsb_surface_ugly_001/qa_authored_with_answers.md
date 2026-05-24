# ntsb_surface_ugly_001 — Questions with reference answers

This file pairs each question with its reference answer for human review and grading. The QA pipeline must read questions only from `qa.md` (or `qa_questions.jsonl`); reference answers live in `oracle.jsonl`.

## q001 — metadata_identifier

**Question.** What NTSB report number, NTSB accident case number, document publication date, and accident date are assigned to this investigation?

**Reference answer.** NTSB report number: HIR-25-06 (Highway Investigation Report). NTSB accident case number: HWY23MH017. Document publication date: September 16, 2025. Accident date: September 29, 2023 (about 8:41 p.m. central daylight time).

## q002 — metadata_identifier

**Question.** The combination vehicle that crashed consisted of a truck-tractor pulling a cargo tank semitrailer. Give the model year, make, and model designation of each piece (the truck-tractor and the cargo tank semitrailer).

**Reference answer.** Truck-tractor: 2005 International 9900ix. Cargo tank semitrailer: 1978 Mississippi Tank Company MC331 cargo tank.

## q003 — metadata_identifier

**Question.** Who operated the combination vehicle (carrier name), where was the carrier facility located, when did the carrier obtain its USDOT number and operating authority, and what was the composition of the carrier's fleet at the time of the crash?

**Reference answer.** Carrier name: Prairieland Transport. Carrier facility: Brownstown, Illinois (the driver was completing a round trip that began around 6:30 a.m. in Brownstown and was about 35 miles from the carrier facility at the time of the crash). The carrier obtained its USDOT number and operating authority in December 2010. At the time of the crash the carrier employed 11 drivers and operated a fleet of 5 truck-tractors, 4 dry van semitrailers, and 18 hazardous materials cargo tank semitrailers (footnote 22 adds that the carrier also employed six owner/operators with leased truck-tractors and leased hazardous materials cargo tank semitrailers).

## q004 — metadata_identifier

**Question.** State the year, make, and model of the minivan involved; the age of the driver; the class and state of issuance of the driver's license; and the dates the license was issued and was set to expire.

**Reference answer.** Minivan: 2013 Toyota Sienna. Driver: 17 years old. License class: probationary Class D Ohio driver's license (with endorsement for motorcycles). License issued: November 2022 (when the driver was 16 years old). License set to expire: February 2027.

## q005 — metadata_identifier

**Question.** State the highway designation, the mile markers between which the crash occurred, the town, the county, and the state of the crash location.

**Reference answer.** US Highway 40 (US-40), between mile markers 21 and 22, Teutopolis, Effingham County, Illinois.

## q006 — date_chronology

**Question.** List, in order, the times and events for the hazmat emergency-response sequence up to the request for MABAS mutual aid, beginning with the crash itself: crash time, first 911 notification time, order closing both approaches, time both directions were closed, and time of the MABAS request.

**Reference answer.** (1) Crash: 8:41 p.m. CDT (combination vehicle departed the roadway, overturned, struck the utility trailer, releasing anhydrous ammonia). (2) 8:43 p.m.: Effingham County Sheriff's Office dispatchers received the first 911 notification from a passenger in the 2019 Volkswagen. (3) About 8:55 p.m.: both eastbound and westbound approaches to the crash scene on US-40 were ordered closed. (4) 9:06 p.m.: both directions were closed. (5) 9:16 p.m.: the incident commander sent a request for Mutual Aid Box Alarm System (MABAS).

## q007 — date_chronology

**Question.** Figure 4 labels five video events with cumulative offsets from event (1) (the combination vehicle entering the no passing zone). Give the elapsed time between each consecutive pair of labeled events and the total cumulative elapsed time from event (1) to event (5).

**Reference answer.** Elapsed time between consecutive labeled events from figure 4: event (1)→(2) = 5.6 seconds (entering no passing zone → beginning of rightward steering); event (2)→(3) = 1.9 seconds (rightward steering → minivan front end visible in oncoming lane); event (3)→(4) = 0.3 seconds (minivan front end in oncoming lane → minivan emerging in front of the combination vehicle); event (4)→(5) = 0.3 seconds (minivan emerging → minivan reentering westbound lane). Total cumulative elapsed time from event (1) to event (5): 5.6 + 1.9 + 0.3 + 0.3 = 8.1 seconds.

## q008 — date_chronology

**Question.** How many minutes elapsed between the crash itself and the Effingham County Sheriff's Office dispatchers receiving the first notification of the crash? Show the clock times and the arithmetic.

**Reference answer.** Crash: 8:41 p.m. First 911 notification received by Effingham County Sheriff's Office dispatchers: 8:43 p.m. Elapsed: 8:43 − 8:41 = 2 minutes.

## q009 — date_chronology

**Question.** How many hours and minutes elapsed between MABAS Division 26 first entering the hot zone and the hazmat team's fifth entry the next morning when a member was splashed? Show the clock times and the arithmetic.

**Reference answer.** MABAS Division 26 first entered the hot zone at 11:17 p.m. (the evening of the crash, September 29, 2023). The hazmat team's fifth entry, when the splash injury occurred, was at 10:01 a.m. the following morning (September 30, 2023). Elapsed: from 11:17 p.m. to 12:00 a.m. (midnight) = 43 minutes; from 12:00 a.m. to 10:01 a.m. = 10 hours 1 minute. Total: 10 hours 44 minutes.

## q010 — date_chronology

**Question.** How many hours and minutes elapsed between the crash itself and the hazmat operation being completed (when US-40 was reopened)? Show the clock times and the arithmetic, and state how the report describes that elapsed time.

**Reference answer.** Crash: 8:41 p.m. on September 29, 2023. Hazmat operation completed and US-40 reopened in both directions: 8:20 p.m. on September 30, 2023. Elapsed: 24 hours from 8:41 p.m. Sept 29 to 8:41 p.m. Sept 30, minus 21 minutes (because 8:20 p.m. is 21 minutes earlier than 8:41 p.m.) = 23 hours 39 minutes. The report describes this as the hazmat operation being completed "nearly 24 hours after the crash."

## q011 — table_list_citation

**Question.** Reproduce the Casualty Summary fields and values for: Location, Date, Time, Involved vehicles, Involved people, Injuries, Weather, and Roadway information.

**Reference answer.** Location: US Highway 40, between mile markers 21 and 22, Teutopolis, Illinois (see figure 2). Date: September 29, 2023. Time: 8:41 p.m. central daylight time. Involved vehicles: 1 (the combination vehicle was the only one involved in the roadway departure, rollover, and release of anhydrous ammonia). Involved people: The combination vehicle driver, 16 bystanders, and 1 first responder. Injuries: Combination vehicle driver: serious. Bystanders: 5 fatal (3 residents of a house at the crash location and 2 drivers of nearby vehicles), 8 serious (occupants of nearby vehicles), and 3 minor (2 occupants of nearby vehicles and 1 resident of a house within the area of the anhydrous ammonia plume). First responders: 1 minor. Weather: Dry, clear, and nighttime. Roadway information: Rural, unlit, undivided highway with one westbound and one eastbound travel lane; straight with a horizontal curve, asphalt concrete pavement, narrow shoulders; 55-mph speed limit.

## q012 — table_list_citation

**Question.** List the five fatally injured people as described in section 1.3, including the vehicle each was associated with (if any) and where each was found.

**Reference answer.** The five fatally injured people, in source order: (1) Three residents of the house in the driveway of which the cargo tank released anhydrous ammonia: an adult male and his two young children — the adult was found by first responders behind his house, lying on the ground, and the two children were found in the back seat of a parked vehicle in front of the house. (2) Driver of a 2015 Kenworth truck-tractor combination vehicle, which approached from the east and was found parked in the drainage channel off the right shoulder approximately 275 feet west from the overturned cargo tank; first responders found the driver lying in the drainage channel next to his vehicle. (3) Driver of a 2023 Hyundai, which approached from the west and was found stopped after striking the fence of the residential house; first responders found the driver lying on the ground near his vehicle.

## q013 — table_list_citation

**Question.** The Casualty Summary lists "8 serious (occupants of nearby vehicles)" bystanders. Section 1.3 enumerates them. List the eight seriously injured people other than the combination vehicle driver, identifying them by the vehicle each was occupying.

**Reference answer.** Section 1.3 lists the other eight seriously injured people in source order as: (1)–(4) four occupants of a 2019 Volkswagen; (5) the passenger of the 2023 Hyundai; (6) the driver of a 2022 Freightliner combination vehicle (found parked on the eastbound lane of US-40, west of the cargo tank's final rest position, not captured in figure 7); (7)–(8) two occupants of a vehicle traveling east on US-40 through the area of the crash (not captured in figure 7).

## q014 — table_list_citation

**Question.** The report's References section cites six prior NTSB publications. List them in source order with their report or proceedings numbers and one-line descriptions.

**Reference answer.** In source order: (1) NTSB. *Vehicle Collision with Stopped School Bus and Student Pedestrian, Town of Excelsior, Wisconsin May 12, 2023.* NTSB/HIR-25-03 (2025). (2) NTSB. 2024. *Intersection Crash Between Passenger Car and Combination Vehicle, Tishomingo, Oklahoma, March 22, 2022.* NTSB/HIR-24-04. (3) NTSB. 2023. *Multivehicle Collision Involving a Milk Tank Combination Vehicle and Stopped Traffic Queue, Phoenix, Arizona, June 9, 2021.* NTSB/HIR-23-04. (4) NTSB. 2022. *Anhydrous Ammonia Release from a Nurse Tank Trailer During Transport, Beach Park, Illinois April 25, 2019.* NTSB/HZIR-22/01. (5) NTSB. 2005. *Proceedings of the National Transportation Safety Board Public Forum on Driver Education and Training, October 28–29, 2003, Report of Proceedings.* NTSB/RP-05/01. (6) NTSB. 1977. *Transport Company of Texas, Tractor-Semitrailer (Tank) Collision with Bridge Column and Sudden Dispersal of Anhydrous Ammonia Cargo, I-610 at Southwest Freeway, Houston, Texas. May 11, 1976.* NTSB/HAR-77/01.

## q015 — table_list_citation

**Question.** According to footnote 24, the FMCSA's BASIC system has seven categories. List the seven BASIC categories in source order, and state which one had a value for Prairieland Transport (and that value) at the time of the crash, and what the alert threshold was for hazmat carriers.

**Reference answer.** The seven FMCSA BASIC categories (in source order per footnote 24): unsafe driving, crash indicator, HOS compliance, vehicle maintenance, controlled substances/alcohol, hazardous materials compliance, and driver fitness. At the time of the crash, the only BASIC category in which Prairieland Transport had a value was vehicle maintenance (55%). The alert threshold for the vehicle maintenance BASIC is 75% for hazardous materials carriers; the carrier was therefore below the alert threshold.

## q016 — source_state_response_status

**Question.** What did the combination vehicle driver's postcrash toxicology screening (conducted by the FAA at NTSB request) test positive for, and why did Prairieland Transport itself not conduct a postcrash drug test under USDOT requirements?

**Reference answer.** The combination vehicle driver's postcrash toxicology screening, conducted by the Federal Aviation Administration's Forensic Sciences Laboratory at NTSB's request, was positive for cetirizine, a second-generation antihistamine found in over-the-counter products such as Zyrtec. Prairieland Transport was unable to conduct a postcrash drug test under USDOT requirements (49 CFR 382.303) because the driver sustained serious injuries (per footnote 33).

## q017 — source_state_response_status

**Question.** What did the minivan driver tell Illinois State Police about her actions during the crash, and what was her interview status with the NTSB?

**Reference answer.** In a postcrash interview with Illinois State Police (conducted five days after the crash, per footnote 36), the minivan driver reported that she passed the combination vehicle because it was varying its speed; that during the passing maneuver she accelerated to about 90 mph, partly because the oncoming vehicle was approaching faster than initially estimated; that she initiated the passing maneuver in the passing zone; that her mother was nervous because of the oncoming headlights; that she and the vehicle passengers were unaware that the combination vehicle had crashed and learned of the crash from the news; and that she had a history of not accurately judging the distances and time needed to pass safely. The minivan driver declined interview requests by the NTSB.

## q018 — source_state_response_status

**Question.** What were Prairieland Transport's safety ratings from FMCSA compliance reviews before and after the crash, and how many violations did the postcrash review identify (and how many of those were critical)?

**Reference answer.** Pre-crash compliance review: in 2011 Prairieland Transport underwent one FMCSA compliance review and received a Satisfactory rating. Post-crash compliance review: the FMCSA conducted a compliance review after the crash that identified 11 violations, one of which was critical (footnote 28 identifies the critical violation as failure to retain a cargo tank manufacturer's data report certificate, 49 CFR 180.417(a)(2)). Despite the 11 violations, the carrier again received a Satisfactory safety rating in the postcrash review.

## q019 — source_state_response_status

**Question.** The Emergency Response Guidebook recommends Level A PPE for responding to anhydrous ammonia. What level of PPE did the MABAS Division 26 hazmat team members actually wear, what did the Charleston Fire Chief describe versus what the interviewed team members described, and was Level A PPE available?

**Reference answer.** The ERG recommends Level A PPE (which per footnote 10(b) includes SCBA and a totally encapsulated chemical- and vapor-protective suit) for responding to anhydrous ammonia. MABAS Division 26 team members actually entered the hot zone wearing turnout gear and self-contained breathing apparatus (SCBA). Per footnote 9(b), the Charleston Fire Chief described the team as donning Level C PPE plus turnout gear and SCBA, while the interviewed MABAS team members specified only turnout gear and SCBA. Level A PPE was available to the team, but the team leader stated that because there was no large anhydrous ammonia plume at that time, the team remained in turnout gear with SCBA, and the team never donned Level A PPE in subsequent entries either.

## q020 — source_state_response_status

**Question.** Describe the federal agricultural HOS exemption the carrier was operating under, the geographic radius and reference point the exemption applied to in the crash trip, and how many of the driver's on-duty hours did not count toward the 14-hour regulatory limit.

**Reference answer.** The carrier was operating under a federal agricultural HOS exemption (49 CFR 395.1(k) and 49 CFR 395.3(b)) when transporting anhydrous ammonia, which exempts drivers from federal hours-of-service regulations when driving within a 150-air-mile radius of the source of the commodity. For this crash trip, the exemption applied within a 150-air-mile radius from Lima, Ohio (the pickup location). Per footnote 31, about 7.5 of the driver's on-duty hours were within the 150-air-mile radius and therefore did not count toward the 14-hour regulatory HOS limit.

## q021 — hard_join_comparison

**Question.** State the NTSB's probable cause for the crash as written in section 3.1, and state separately whether the report includes any contributing factor or contributing factors language.

**Reference answer.** Probable cause (section 3.1, verbatim): "the unsafe passing maneuver by a teen driver that caused the combination vehicle driver to initiate an evasive action that resulted in loss of vehicle control and rollover." The same section 3.1 paragraph also contains contributing-factor language: "Contributing to the severity of the crash was the subsequent impact of the overturned cargo tank with a parked utility trailer that resulted in the release of anhydrous ammonia." So unlike many marine investigation reports, this report does include contributing-factor language — embedded in the same Probable Cause subsection, not in a separately labeled contributing-factor subsection.

## q022 — hard_join_comparison

**Question.** Compare the speeds reported by the report's narrative: (a) the combination vehicle's speed in the first 45 seconds of video; (b) the combination vehicle's speed when it crossed onto the shoulder; (c) the minivan driver's reported speed during the passing maneuver; (d) the witness's estimated speed of his own vehicle pulling a camper behind the combination vehicle; and (e) the posted speed limit on US-40 at the crash location.

**Reference answer.** (a) Combination vehicle's speed in the first 45 seconds of video: 59 to 61 mph (traveling in the center of the westbound lane). (b) Combination vehicle's speed when it crossed onto the shoulder: 56 mph. (c) Minivan driver's reported speed during the passing maneuver (per her ISP interview): about 90 mph. (d) Witness pulling a camper behind the combination vehicle: estimated 58 mph as his own speed. (e) Posted speed limit on US-40 at the crash location: 55 mph.

## q023 — hard_join_comparison

**Question.** The report describes federal violations relating to two different parties. State the violation count and any critical-violation detail for: (a) the FMCSA postcrash inspection of Paul Akers, Inc. (the cargo-tank recertification facility), and (b) the FMCSA postcrash compliance review of Prairieland Transport itself.

**Reference answer.** (a) FMCSA postcrash inspection of Paul Akers, Inc. (the cargo-tank recertification facility): four violations, two of which pertained to the crash-involved cargo tank; one of these was for failing to perform the wet fluorescent magnetic particle test on the entire interior cargo tank head. (b) FMCSA postcrash compliance review of Prairieland Transport: 11 violations, one of which was critical — the critical violation was failure to retain a cargo tank manufacturer's data report certificate (49 CFR 180.417(a)(2), per footnote 28).

## q024 — hard_join_comparison

**Question.** According to section 1.5.1, anhydrous ammonia is regulated differently for domestic versus international transportation. State (a) the UN identification number; (b) the domestic CFR classification division and what that division denotes; (c) the international classification division and what that division denotes; and (d) the special additional requirement imposed on domestic shipments to compensate for the lower division.

**Reference answer.** (a) UN global identification number: UN1005. (b) Domestic classification under 49 CFR 172.101: Division 2.2 hazmat, which denotes "non-flammable, nonpoisonous compressed gas." (c) International classification: Division 2.3, which denotes "gas poisonous by inhalation." (d) The special additional requirement on domestic shipments is the "Inhalation Hazard" marking on packages (cargo tanks) and shipping papers, denoted by Special Provision #13 in column 7 of the 49 CFR 172.101 hazardous materials table (per footnote 15(a)). The 1993 PHMSA-predecessor ruling permitted the lower Division 2.2 classification domestically — instead of poison-gas classification — because of the extremely large volume transported nationally and the extensive worker knowledge of its hazards, but it required the "Inhalation Hazard" marking as a compensating requirement.

## q025 — hard_join_comparison

**Question.** The driver went on duty at 6:22 a.m. and the crash occurred at 8:41 p.m. that evening. (a) How many hours did the driver work? (b) What is the general regulatory on-duty limit per shift for property-carrying commercial motor vehicle drivers? (c) How many of the driver's on-duty hours did not count toward the 14-hour regulatory limit, and why?

**Reference answer.** (a) The driver went on duty at 6:22 a.m. and the crash occurred at 8:41 p.m. on the same day. From 6:22 a.m. to 8:41 p.m. is 14 hours 19 minutes; the report states he "had been on duty for about 14.5 hours when the crash occurred." (b) Property-carrying commercial motor vehicle drivers are generally restricted to 14 hours of on-duty time per shift. (c) Per footnote 31, about 7.5 of the driver's on-duty hours were within the 150-air-mile radius from Lima, Ohio (the source of the commodity), and therefore did not count toward the 14-hour regulatory HOS limit because the driver was operating under a federal agricultural HOS exemption.


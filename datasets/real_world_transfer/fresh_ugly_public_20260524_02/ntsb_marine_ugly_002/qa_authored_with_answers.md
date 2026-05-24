# ntsb_marine_ugly_002 — Questions with reference answers

This file pairs each question with its reference answer for human review and grading. The QA pipeline must read questions only from `qa.md` (or `qa_questions.jsonl`); reference answers live in `oracle.jsonl`.

## q001 — metadata_identifier

**Question.** What is the name of the towing vessel that capsized and sank, who owned/operated it at the time of the casualty, what NTSB report number is assigned to the marine investigation report, and what NTSB case number is assigned to the underlying investigation?

**Reference answer.** Vessel name: Baylor J. Tregre. Owner/operator at the time of the casualty: Trinity Tugs LLC (which had acquired the vessel in 2023 and renamed it). NTSB Marine Investigation Report number: MIR-25-21 (dated May 15, 2025). NTSB case number for the underlying investigation: DCA24FM038.

## q002 — metadata_identifier

**Question.** What are the latitude and longitude of the casualty location, and how is the location described in nautical miles from the nearest major port city?

**Reference answer.** Latitude/longitude of the casualty location: 28°56.34' N, 094°54.7' W. The location is described as the Gulf of America, about 23 nautical miles south of Galveston, Texas (the opening narrative says "23 miles south of Galveston, Texas" and footnote 1 specifies that all miles in the report are nautical miles).

## q003 — metadata_identifier

**Question.** The vessel was not originally named Baylor J. Tregre. Give the year built, the builder, the original name, the original owner, and the year and name of the company that renamed the vessel.

**Reference answer.** Year built: 1997. Builder: R&S Fabricators, Inc., in Lockport, Louisiana. Original name: Trent Joseph. Original owner: Coastal Towing LLC. The vessel was acquired and renamed in 2023 by Trinity Tugs LLC.

## q004 — metadata_identifier

**Question.** How many crewmembers were aboard, what were their roles, and what watch schedules did each pair work?

**Reference answer.** Four crewmembers were aboard: a captain, a mate, and two deckhands (deckhands 1 and 2). The captain and deckhand 1 worked a watch schedule of 0600–1200 and 1800–2400. The mate and deckhand 2 worked the opposite watch schedule of 0000–0600 and 1200–1800.

## q005 — metadata_identifier

**Question.** State the length, breadth, and depth of the barge MARMAC 27, who owned and who leased it, and what the barge was carrying at the time of the casualty.

**Reference answer.** MARMAC 27 dimensions: 260 feet long, 72 feet wide, 16-foot depth (described as a "260-foot-long, 72-foot-wide, 16-foot-depth oceangoing deck barge"). Owner: McDonough Marine Service. Lessee: Manson Construction Co. At the time of the casualty the barge was loaded with a production platform and helideck, being towed from Houma, Louisiana, to Brazos Area Block 538A in the Gulf of America.

## q006 — date_chronology

**Question.** On what date did Trinity Tugs enter the towing agreement with Manson Construction, on what date and at what time did the Baylor J. Tregre depart Houma, and on what date did the casualty occur?

**Reference answer.** Agreement date: May 11, 2024 (Trinity Tugs entered the agreement with Manson Construction Co. to tow the MARMAC 27 from Houma to Brazos Area Block 538A). Departure from Houma: May 11, 2024, about 0340 (same day as the agreement). Casualty date: May 13, 2024, about 1657 local (central daylight) time.

## q007 — date_chronology

**Question.** According to the AIS data cited in the Event Sequence section, what was the vessel's speed in knots at 1647:04, at 1650:09, and at 1654:20?

**Reference answer.** At 1647:04 the vessel's speed was 4.0 knots; at 1650:09 it had dropped to 1.8 knots; at 1654:20 it had dropped to 0.6 knots. (The Event Sequence cites these AIS readings to show that the vessel went from 4.0 knots to almost a full stop in about seven minutes.)

## q008 — date_chronology

**Question.** How many minutes elapsed between the mate's distress call on VHF channel 16 and the last AIS transmission from the Baylor J. Tregre? Show the clock times and the arithmetic.

**Reference answer.** Distress call on VHF channel 16: 1657. Last AIS transmission from the Baylor J. Tregre: 1712. Elapsed time: 1712 − 1657 = 15 minutes.

## q009 — date_chronology

**Question.** How many minutes elapsed between Coast Guard District 8 New Orleans receiving the EPIRB alert and the response boat recovering all four crewmembers? Show the clock times and the arithmetic.

**Reference answer.** Coast Guard District 8 New Orleans received the EPIRB alert at 1717. The response boat recovered the four crewmembers at 1808. Elapsed time: 1808 − 1717 = 51 minutes.

## q010 — date_chronology

**Question.** How many hours and minutes elapsed between the National Weather Service issuing the 1409 Coastal Waters Forecast for High Island to the Matagorda Ship Channel and the 1657 distress call from the Baylor J. Tregre? Show the arithmetic.

**Reference answer.** NWS Coastal Waters Forecast issued at 1409. Mate's VHF channel 16 distress call at 1657. Elapsed: 1657 − 1409 = 2 hours 48 minutes (the Analysis describes the 1409 forecast as having been issued "about 3 hours before the casualty," consistent with this 2 h 48 min interval).

## q011 — table_list_citation

**Question.** Reproduce the Vessel Particulars table values for: Vessel, Type, Owner/Operator, Flag, Port of registry, Year built, Official number, IMO number, Classification society, Length (overall), Breadth (max.), Draft (casualty), Tonnage, and Engine power; manufacturer.

**Reference answer.** Vessel: Baylor J. Tregre. Type: Towing/Barge (Towing Vessel). Owner/Operator: Trinity Tugs LLC (Commercial). Flag: United States. Port of registry: New Orleans, Louisiana. Year built: 1997. Official number: 1055480 (US). IMO number: N/A. Classification society: N/A. Length (overall): 67.2 ft (20.4 m). Breadth (max.): 24.0 ft (7.3 m). Draft (casualty): 9.0 ft (2.7 m). Tonnage: 97 GRT. Engine power; manufacturer: 2 x 750 hp (559 kW); Caterpillar 3412 diesel engines.

## q012 — table_list_citation

**Question.** Reproduce the Casualty Summary values for: Casualty type, Location, Date, Time, Persons on board, Injuries, Property damage, and Environmental damage.

**Reference answer.** Casualty type: Capsizing/Listing. Location: Gulf of America, 23 nm south of Galveston, Texas; 28°56.34' N, 094°54.7' W. Date: May 13, 2024. Time: 1657 central daylight time (coordinated universal time –5). Persons on board: 4. Injuries: 1 minor. Property damage: $2 million est. Environmental damage: None.

## q013 — table_list_citation

**Question.** List, in source order, the four National Weather Service products described in section 1.3.3.2 (Weather Forecasts) with their issuance times and a one-line description of each.

**Reference answer.** Source order, with issuance times and brief descriptions: (1) 1257 — NWS Severe Thunderstorm Watch for portions of southwest Louisiana, southeast Texas, and coastal waters, effective until 2000, warning of thunderstorms capable of large hail and wind gusts of 60–80 knots. (2) 1409 — NWS Coastal Waters Forecast for High Island to the Matagorda Ship Channel out 60 miles, including Galveston and Matagorda Bays, forecasting scattered storms continuing across southeast Texas with an area of storms pushing offshore. (3) 1501 — NWS Special Marine Warning applicable to coastal waters near Galveston (including the Baylor J. Tregre's route) for severe thunderstorms capable of wind gusts to 40 knots, large hail, and frequent lightning, advising mariners to move to safe harbor. (4) 1544 — Special Marine Warning update reporting strong thunderstorms with wind gusts of 34 knots or greater and small hail.

## q014 — table_list_citation

**Question.** What Coast Guard inspections of the Baylor J. Tregre are described in section 1.3.2, on what dates were they completed, and what additional non-Coast Guard survey was completed on April 22, 2024?

**Reference answer.** The last Coast Guard inspections of the Baylor J. Tregre were an internal structural examination and periodic drydock inspection completed on April 15, 2024, and an annual inspection completed on April 22, 2024; both were completed satisfactorily. Also on April 22, 2024, at the request of the company that would receive the production platform and helideck on the MARMAC 27, a surveyor completed a suitability survey on the Baylor J. Tregre in Houma to ascertain the vessel's suitability to tow the MARMAC 27.

## q015 — table_list_citation

**Question.** The report states the Baylor J. Tregre had five exterior doors on the main deck. What does the report specifically describe about the condition of any of those exterior doors after the casualty?

**Reference answer.** The report states that the starboard-side exterior door to the engine room was found separated from the hinges and lying on the deck; that the salvage master told investigators divers found the forward starboard main deck door open before salvage operations began; and that various door hinges and sealing gaskets on both sides of the vessel were found deteriorated.

## q016 — source_state_response_status

**Question.** Was there an emergency tow release function in the Baylor J. Tregre's wheelhouse, and was such a function required?

**Reference answer.** There was no emergency tow release function in the Baylor J. Tregre wheelhouse, and the report states such a function was not required (footnote 8 cites 46 CFR Subchapter M). Instead, releasing the towline required a crewmember to start the winch engine in the upper engine room and another crewmember to operate the winch controls in the doghouse on the second deck.

## q017 — source_state_response_status

**Question.** The Analysis section addresses whether the mate received the Special Marine Warnings and whether the crew could have avoided the storm. What does the report conclude on each point?

**Reference answer.** The Analysis states the mate did not recall hearing any updated weather forecasts over VHF radio and was therefore unaware of the Special Marine Warnings. The Analysis also concludes that even if the crew had received the Special Marine Warnings, they would not have been able to avoid the storm, given the vessel's speed (about 4–5 knots), the tow's position (about 17 miles from Galveston and surrounded by storms), and the speed of the storm's advance.

## q018 — source_state_response_status

**Question.** The April 22, 2024 suitability survey recommended consideration of weather criteria. Did the survey specify weather criteria limits for the tow, and what did the survey conclude about suitability?

**Reference answer.** The April 22, 2024 suitability survey recommended that "Careful consideration is to be given to weather criteria for the tow of MARMAC 27," but did NOT specify weather criteria limits for the tow. The survey concluded that the Baylor J. Tregre was suitable for the towing operation.

## q019 — source_state_response_status

**Question.** What did NTSB investigators find when they examined the Baylor J. Tregre after the casualty during the July 9–10 examination?

**Reference answer.** During the July 9–10 post-casualty examination, NTSB investigators found multiple fractures and indentations on the vessel's superstructure that appeared to be from recovery activities; the doghouse was missing; and the port and starboard engine room/fiddley stack blowers were missing. The outboard bulwark aft and to port of the centerline aft roller chocks exhibited abrasion and scarring to the paint coating, exposing bare metal, while the bulwarks to starboard of the centerline aft roller chocks did not show similar markings. Of the five exterior doors on the main deck, the starboard-side exterior door to the engine room was separated from its hinges and lying on the deck; the salvage master told investigators that divers had found the forward starboard main deck door open before salvage began; and various door hinges and sealing gaskets on both sides of the vessel were found deteriorated.

## q020 — source_state_response_status

**Question.** Section 2 (Analysis) lists openings through which the capsized vessel would have flooded. List, in source order, the openings the report names as possible flooding paths and the condition the report cites for each.

**Reference answer.** In source order, the Analysis names three openings as possible flooding paths: (1) the fiddley blowers (on the second deck), which were missing when the vessel was salvaged; (2) windows, which blew open during the storm; and (3) — to a lesser degree — exterior doors, whose hinges and sealing gaskets were found deteriorated after the casualty.

## q021 — hard_join_comparison

**Question.** State the NTSB's probable cause for the casualty as written in section 3.1. Does the report's Conclusions section include any separately labeled contributing factor or contributing factors section?

**Reference answer.** Probable cause (section 3.1, verbatim): "the mate's inability to maneuver the tow into the wind due to the overwhelming towline force generated by the towed barge during the sudden onset of severe weather, resulting in unrecoverable heeling." The report's Conclusions section (section 3) contains only the 3.1 Probable Cause subsection; it does NOT include any separately labeled contributing factor or contributing factors section.

## q022 — hard_join_comparison

**Question.** Using the AIS times cited in the Event Sequence, how much time elapsed while the vessel's speed dropped from 4.0 knots to 0.6 knots? Show the start time, end time, and the elapsed time in minutes and seconds.

**Reference answer.** Start of speed drop: 1647:04 at 4.0 knots. End of speed drop: 1654:20 at 0.6 knots. Elapsed: 1654:20 − 1647:04 = 7 minutes 16 seconds. (The Analysis summarizes this as the vessel going from 4.0 knots to "almost a full stop" in this interval.)

## q023 — hard_join_comparison

**Question.** The report cites three different wind-speed estimates near the time of the casualty: the captain's estimate, the closest NWS reporting location, and the Galveston Bay entrance (north jetty) buoy station GNJT2. State each estimate, the location/source, and the corresponding time when available.

**Reference answer.** Captain's estimate: about 85–100 mph (about 74–87 knots), at the time of the casualty (around 1654:20, when the captain arrived in the wheelhouse and the vessel's speed had dropped to 0.6 knots); no exact clock time is stated. Closest NWS reporting location, Scholes International Airport at Galveston (KGLS), about 22 miles north of the casualty site: winds gusting to 48 knots at 1724. Galveston Bay entrance (north jetty) buoy station GNJT2, 27 miles from the casualty site: wind gust to 62 knots at 1718.

## q024 — hard_join_comparison

**Question.** The Analysis explains why the mate could not release the tow even though the doghouse housed the winch controls. Give both reasons the Analysis states for why releasing the tow from the doghouse was not possible at the time of the casualty.

**Reference answer.** Reason 1: The doghouse itself was inaccessible because it was partially submerged; the mate, when he proceeded aft, saw the doghouse was halfway underwater with windows blown out. Reason 2: Even if the mate could have reached the doghouse, the winch engine was not running (the tow winch drive engine was located in the upper engine room and would need to be started), and the engine room was inaccessible because the vessel was heeling so far to port.

## q025 — hard_join_comparison

**Question.** The Casualty Summary lists "1 minor" injury, while the narrative describes a crewmember being airlifted from the response boat to a hospital. Reconcile these two facts: identify which crewmember sustained the injury, where the injury fact appears in the narrative, and what level of severity the Casualty Summary assigns.

**Reference answer.** The narrative identifies deckhand 2 as the crewmember who sustained the injury: "Deckhand 2 reported injuries and was airlifted by the rescue helicopter from the response boat and transported to a local hospital." The Casualty Summary table classifies this as "1 minor" injury under the Injuries field. The two facts are consistent — one crewmember (deckhand 2) was hurt, and the Casualty Summary characterizes the injury as minor.


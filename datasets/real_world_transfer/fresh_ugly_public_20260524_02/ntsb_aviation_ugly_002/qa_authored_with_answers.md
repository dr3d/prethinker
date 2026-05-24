# ntsb_aviation_ugly_002 — Questions with reference answers

This file pairs each question with its reference answer for human review and grading. The QA pipeline must read questions only from `qa.md` (or `qa_questions.jsonl`); reference answers live in `oracle.jsonl`.

## q001 — metadata_identifier

**Question.** What is the NTSB accident number, the aircraft registration, and the aircraft make and model for this report?

**Reference answer.** Accident Number: WPR24FA083; Registration: N900VA; Aircraft: HAWKER BEECHCRAFT CORP HAWKER 900XP.

## q002 — metadata_identifier

**Question.** Where (city and state) and when (date and Local time) did the accident occur?

**Reference answer.** Westwater, Utah, on February 7, 2024, at 10:48 Local.

## q003 — metadata_identifier

**Question.** Who is the registered owner of the airplane, who is the operator, and what operating certificate does the operator hold?

**Reference answer.** Registered Owner: VICI AVIATION LLC. Operator: Clay Lacy Aviation, Inc. (doing business as Clay Lacy Aviation). Operating Certificate(s) Held: On-demand air taxi (135).

## q004 — metadata_identifier

**Question.** Who is the Investigator In Charge (IIC), and list the six Additional Participating Persons by full name, organization, and city as they appear in the Administrative Information block.

**Reference answer.** IIC: Stein, Stephen. Six Additional Participating Persons: (1) Patrick Lusch; FAA; Washington, DC; (2) Jay Eller; Honeywell; Phoenix, AZ; (3) Ricardo Asensio; Textron Aviation; Wichita, KS; (4) Dondi Pangalangan; Clay Lacy; Van Nuys, CA; (5) Ed Mirzhakanian; Clay Lacy; Van Nuys, CA; (6) Allen McReynolds; West Star; Grand Junction, CO.

## q005 — metadata_identifier

**Question.** What is this report's Investigation Class, and what is the URL for the Investigation Docket?

**Reference answer.** Investigation Class: Class 2. Investigation Docket: https://data.ntsb.gov/Docket?ProjectID=193761

## q006 — date_chronology

**Question.** In the History of Flight section, the report uses clock times in the 10:xx hour. List, in chronological order, what occurred at each of these clock anchors (give the time and a brief description of the event): 1037; 1044:00; 1046:33; 1046:37; 1046:47; 1047:44.

**Reference answer.** In chronological order: 1037 — airplane departed GJT and entered a climb on a southeast heading. 1044:00 — airspeed began to decrease from 219 kts as pitch attitude and AOA began to increase. 1046:33 — cockpit area microphone recorded a sound consistent with the stick shaker; SIC reported "one nineteen." 1046:37 — Stall Valve A opened (while decelerating from 118 kts), and the CVR CAM recorded a rattling sound accompanied by the stick shaker. 1046:47 — flight track data show the airplane began a rapid descent in a corkscrew pattern. 1047:44 — the recorded flight track ended after multiple circular rotations.

## q007 — date_chronology

**Question.** According to the History of Flight, how many seconds elapsed from when the cockpit area microphone recorded the stick shaker sound to when the flight track data show the airplane began the rapid corkscrew descent?

**Reference answer.** 14 seconds. From 1046:33 to 1046:47 is 14 seconds.

## q008 — date_chronology

**Question.** According to the Routine Maintenance subsection, how many days elapsed from the date the airplane arrived at the maintenance facility to the date it was returned to service?

**Reference answer.** 48 days. The airplane arrived at West Star Aviation on December 20, 2023, and was returned to service on February 6, 2024: 11 days remaining in December (Dec 21–Dec 31) + 31 (January) + 6 days in February = 48 days.

## q009 — date_chronology

**Question.** How many days elapsed from the date the airplane was returned to service to the date of the accident?

**Reference answer.** 1 day. The airplane was returned to service on February 6, 2024, and the accident occurred on February 7, 2024.

## q010 — date_chronology

**Question.** Within the History of Flight FDR sequence, how many seconds elapsed between Stall Valve A first opening (consistent with stick shaker active) and both Stall Valve A and Stall Valve B transitioning to OPEN (consistent with stick pusher activation)?

**Reference answer.** 2 seconds. Stall Valve A first opened at 1046:37 (consistent with stick shaker active); at 1046:39 both Stall Valve A and Stall Valve B transitioned to OPEN (consistent with stick pusher activation).

## q011 — table_list_citation

**Question.** The "Findings" table lists ten findings, each with a category and a description. List all ten in source order as `Category — Description`.

**Reference answer.** Ten findings in source order: (1) Personnel issues — Decision making/judgment - Flight crew; (2) Personnel issues — Total instruct/training recvd - Flight crew; (3) Personnel issues — Use of policy/procedure - Flight crew; (4) Personnel issues — Use of equip/system - Flight crew; (5) Personnel issues — Aircraft control - Flight crew; (6) Aircraft — Angle of attack - Not specified; (7) Aircraft — Pitch control - Incorrect use/operation; (8) Environmental issues — Conducive to structural icing - Decision related to condition; (9) Environmental issues — Conducive to structural icing - Effect on equipment; (10) Organizational issues — Adequacy of policy/proc - Manufacturer.

## q012 — table_list_citation

**Question.** The CAE Simulator Flight section lists six configuration items for the simulator test runs. Reproduce that six-item configuration list in source order.

**Reference answer.** Six configuration items, in source order: (1) Weight: 23,890 lbs; (2) Fuel: 7,290 lbs; (3) % MAC: 24; (4) Outside air temperature: 8°C on ground; dew point -1°C; (5) Cloud heights: Scattered 6,000 ft above ground level (agl), overcast 10,000 ft agl, tops at 17,000 ft msl; (6) Stalls were carried out about 18,000 ft msl.

## q013 — table_list_citation

**Question.** The Routine Maintenance subsection summarizes maintenance work-order entries on four distinct calendar dates in January 2024. List the four dates in chronological order and, for each, briefly describe what was performed.

**Reference answer.** Four work-order dates in chronological order: (1) January 3, 2024 — the wing leading edge structural inspection began and the TKS panels were removed; (2) January 4, 2024 — the TKS panels were cleaned and closed except for the left and right No. 2 stall trigger panels (both stall trigger TKS lines were found leaking and were re-sealed, with new seals installed on the right and left wing stall trigger TKS lines); (3) January 18, 2024 — the left and right leading edges were prepped and installed on the wings (one screw was missing from the right leading edge and the right TKS proportioning valve had a leaking line); (4) January 30, 2024 — the structural inspection of the wing leading edges was completed and signed off; inspection and double inspection were also endorsed the same day. (Note: the source text also contains a separate entry stating that the stall trigger work was signed off and inspected on "January 11, 2025," which is reproduced as written in the original report.)

## q014 — table_list_citation

**Question.** Section 57-41-00 of the structural repair manual lists the two conditions that require the post-maintenance stall test flight. State both conditions.

**Reference answer.** Section 57-41-00 requires that the airplane be test flown by a pilot familiar with the stall identification system and stall characteristics if: (1) The leading edge assembly was removed as a whole for any reason; (2) Two or more TKS [de-icing] wing distribution panels on one side are removed or installed.

## q015 — table_list_citation

**Question.** The POM "required conditions" for the stall test (in the Stall Test Procedure from Pilot's Operating Manual subsection) include an altitude rule, a cloud-clearance rule, a maximum altitude, and several other conditions. List all the POM-required conditions as enumerated in that paragraph.

**Reference answer.** The POM required conditions for the stall test are: altitude above 10,000 ft above ground level; 10,000 ft above clouds; below 18,000 ft mean sea level; conducted during day visual meteorological conditions with a good visual horizon; autopilot disengaged; operative stall identification system; external surfaces free of ice; ventral tank empty; and weather radar on standby.

## q016 — source_state_response_status

**Question.** Which of the POM stall-test conditions did the accident crew comply with, and which did they not comply with? Distinguish the two sets based on what the Accident Flight Stall Test subsection says.

**Reference answer.** Complied with: empty ventral tank, operative stall identification system, autopilot OFF, and (per the Accident Flight Stall Test subsection) the flight was in VMC conditions. Did NOT comply with: the cloud clearance rule (flown about 5,000 ft above clouds, well above the 10,000-ft-above-clouds clearance) and the maximum-altitude limit (flown about 2,000 ft above the prescribed maximum of 18,000 ft msl), and there is no evidence the crew verified external surfaces were free of ice after flying through IMC and icing conditions. The flight crew's visual horizon and weather radar status are unknown (not confirmed either way).

## q017 — source_state_response_status

**Question.** According to the report, how many prior inflight stall tests had the PIC and SIC each conducted, and what role did the PIC have in his prior stall test?

**Reference answer.** The PIC had conducted an inflight stall test once before, on December 7, 2019, and was the second-in-command on that flight (not the PIC). There was no record that the SIC had conducted an inflight stall test before the accident flight.

## q018 — source_state_response_status

**Question.** What did FAA toxicology testing detect in the PIC's samples, and what did it identify in the SIC's samples?

**Reference answer.** FAA toxicology testing detected unknown quantities of Zolpidem and Terbinafine in the PIC's kidney and muscle. For the SIC, FAA toxicology testing did not identify any substances of abuse in any of the samples submitted.

## q019 — source_state_response_status

**Question.** Could the investigation definitively determine whether wing contamination was introduced by the maintenance team during reassembly? Why or why not?

**Reference answer.** No. The report states that the postcrash fire prevented the investigation from determining if there was any wing contamination introduced by the maintenance team during reassembly. However, the number of post-maintenance and preflight inspections decreases the likelihood of improper maintenance.

## q020 — source_state_response_status

**Question.** Were both pilots' Last FAA Medical Exam dates the same, and what were their two most-recent Last Flight Review or Equivalent dates?

**Reference answer.** Yes, both pilots' Last FAA Medical Exam date was December 11, 2023. Their Last Flight Review or Equivalent dates were different: the right-seat pilot's was October 6, 2023; the left-seat pilot's was October 28, 2024.

## q021 — hard_join_comparison

**Question.** The Probable Cause statement and the report's analysis distinguish causal factors from contributing factors. State, in the report's own structure: (a) what the probable cause findings are, and (b) what the contributing factor is.

**Reference answer.** (a) The probable cause findings are: the flight crew's decision to conduct a post-maintenance stall test in an area of icing conditions, which resulted in wing contamination that significantly decreased the airplane's critical angle of attack; and (also causal) the airplane manufacturer's lack of training and experience requirements for the flight crew to safely conduct the stall test, which resulted in an attempted remedial action that aggravated the aerodynamic stall and led to a loss of control from which they were unable to recover. (b) The contributing factor is the flight crew's failure to follow the test conditions regarding cloud clearance, altitude limit, visual meteorological conditions, and ensuring all external surfaces were free from ice.

## q022 — hard_join_comparison

**Question.** The Previous Accident (CHI06IA127) section describes a prior event. What aircraft type was involved, what was the key cause finding in that investigation, and which two elements of that finding parallel the Westwater accident?

**Reference answer.** The prior event involved a British Aerospace BAe 125-800A airplane (on the same type certificate as the accident airplane). The investigation determined that the pilot in command failed to maintain control during the initial roll at the onset of the stall due to his improper remedial action related to stall recovery, and that the stall was initiated with wing contamination due to icing which resulted in the stall occurring at a higher-than-anticipated airspeed. Two elements that parallel the Westwater accident: (1) wing contamination due to icing initiating the stall; and (2) improper remedial action by the flight crew during stall recovery.

## q023 — hard_join_comparison

**Question.** From the Pilot Information tables, compare the two pilots' total flight time, total time in this make and model, and Pilot In Command time. State each pilot's three values.

**Reference answer.** Pilot 1 (right seat, age 58): 8,188 hours total all aircraft; 70 hours total this make and model; 4,062 hours Pilot In Command all aircraft. Pilot 2 (left seat, age 65): 15,734 hours total all aircraft; 2,249 hours total this make and model; 12,190 hours Pilot In Command all aircraft.

## q024 — hard_join_comparison

**Question.** The CAE Simulator Flight section reports test results in icing conditions where the simulated stall response was "subtle" with no roll indications. Compare that simulator behavior to what the FDR shows happened during the accident at and immediately after 1046:37. What does this comparison imply about simulator training adequacy for this maneuver?

**Reference answer.** In the simulator's icing test run the stall response was subtle and there were no roll indications throughout the maneuver. In the actual accident, at 1046:37 the airplane abruptly banked right beyond 45° at a roll rate exceeding 40° per second (reaching 83° right bank within two seconds), with vertical acceleration dropping from about 0.9g to about 0.6g and pitch attitude decreasing from about 15° to about 6°. The comparison implies that simulator training did not expose the crew to the violent roll/spin behavior actually possible in this airplane with wing contamination, so the simulator training was not adequate preparation for the accident maneuver. The report states this directly: "it is unlikely that the flight crewmembers' simulator training on the stall warning and identification system and the PIC's previous participation in a stall test flight adequately prepared them to safely conduct a stall flight test or address any unacceptable stall behavior."

## q025 — hard_join_comparison

**Question.** The Wing Contamination analysis identifies two possible explanations for the degraded lift-to-AOA relationship. Name both, and explain why the report could not conclusively determine which explanation applied.

**Reference answer.** The two possible explanations are (1) ice accretion due to exposure to icing conditions during the accident flight, and (2) wing contamination introduced during routine maintenance, since the wing leading edges had recently been removed to facilitate an inspection of the wings and TKS panels. The report could not conclusively determine which applied because the postcrash fire mostly consumed the airplane and the wing leading edges, leaving the wings significantly damaged or soot-covered, which prevented a complete examination of any contamination state at the time of the accident.


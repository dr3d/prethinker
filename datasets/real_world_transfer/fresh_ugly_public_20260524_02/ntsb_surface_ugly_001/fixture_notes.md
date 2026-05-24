# Fixture notes — ntsb_surface_ugly_001

## What this document pressures

This NTSB highway investigation report (HIR-25-06) sits in the surface/hazmat subdomain and exercises several pressure points distinct from the aviation and marine reports in this batch.

### Two-party violation attribution (FMCSA → Paul Akers + Prairieland Transport)
The FMCSA conducted two separate postcrash inspections of two separate parties: the cargo-tank recertification facility Paul Akers, Inc. (4 violations, 2 pertaining to the crash-involved cargo tank) and the carrier Prairieland Transport itself (11 violations, 1 critical). Pipelines that conflate the two — or summarize "FMCSA found violations" without specifying which party — will fail q023. The critical violation against the carrier is specifically the failure to retain a cargo tank manufacturer's data report certificate (49 CFR 180.417(a)(2), per footnote 28).

### Probable cause + contributing factor in one paragraph
Unlike the marine report (ntsb_marine_ugly_002), this report's section 3.1 *does* contain contributing-factor language — but embedded in the same paragraph as the probable-cause statement, not in a separately labeled subsection. q021 distinguishes these forms explicitly.

### Domestic vs international hazmat classification (Division 2.2 vs 2.3)
Anhydrous ammonia carries Division 2.2 ("non-flammable, nonpoisonous compressed gas") in 49 CFR for domestic shipments and Division 2.3 ("gas poisonous by inhalation") internationally, with an "Inhalation Hazard" marking imposed as a compensating special requirement domestically. q024 forces recovery of all four facts (UN number, both divisions and their meanings, the special marking) from section 1.5.1.

### Agricultural HOS exemption arithmetic
The driver was on duty from 6:22 a.m. to 8:41 p.m. = 14 h 19 min (the report rounds to "about 14.5 hours"), exceeding the 14-hour property-carrying CMV regulatory limit. But about 7.5 of those hours were within a 150-air-mile radius of Lima, Ohio, and did not count toward the limit per the agricultural HOS exemption (49 CFR 395.1(k)). q025 requires all three facts and the join from main text to footnote 31.

### Figure-4 cumulative time arithmetic
The video-event figure 4 caption labels five events with relative offsets: 0, +5.6, +1.9, +0.3, +0.3 seconds. The cumulative time from event (1) to event (5) is 8.1 seconds (5.6+1.9+0.3+0.3). q007 tests both the consecutive elapsed values and the running total.

### Cross-midnight chronology
The hazmat operation crosses midnight: Division 26 first entry at 11:17 p.m. on Sept 29 to fifth entry at 10:01 a.m. on Sept 30 (q009: 10 h 44 min), and end-to-end crash to reopening from 8:41 p.m. Sept 29 to 8:20 p.m. Sept 30 (q010: 23 h 39 min, which the report describes as "nearly 24 hours"). Both require correct handling of the date boundary.

### Casualty enumeration vs summary count
The Casualty Summary table lists "5 fatal, 8 serious, 3 minor" bystander injuries plus "1 minor" for first responders, plus the combination vehicle driver who is "serious" — so the lead paragraph's "five fatalities ... serious injuries to nine, and minor injuries to four" partitions across two table rows (driver row and bystanders row plus first responder row). q011 reproduces the table, q012 enumerates the five fatalities by vehicle/location, and q013 enumerates the eight other seriously injured people by vehicle. These are different cuts of the same dataset and pipelines that just paraphrase the lead paragraph will fail the table-vs-narrative joins.

### PPE-level mismatch with conflicting witness accounts
Footnote 9(b) reports that "The Charleston Fire Chief described the MABAS team members as donning Level C personal protective equipment (PPE), turnout gear, and SCBA, although the interviewed MABAS team members specified only turnout gear and SCBA." The ERG recommends Level A. Three different PPE descriptions, each from a different source — q019 requires preserving all three.

### Speed-claim cluster across narrator + driver + witness + posted limit
q022 collects five separate speed claims (combination vehicle 59–61 mph baseline, 56 mph at shoulder crossing, minivan ~90 mph, witness's own 58 mph, posted limit 55 mph) scattered across §1.2 Event Sequence, §1.5.4.2 Minivan Driver, and the Casualty Summary.

### Driver inexperience pattern
The combination vehicle driver's CDL was 2 years old; the minivan driver's probationary license was less than a year old; both drivers were comparatively inexperienced for their respective roles. The fixture preserves both ages (24 and 17), license issue dates (CDL in 2021; minivan license in November 2022), and expiration dates.

### Negative findings
The report's Analysis section makes several explicit negative findings: no impairment, no fatigue evidence for the combination vehicle driver; no phone-use distraction for either driver at the time of the crash; no mechanical preexisting deficiencies; minivan driver was not violating probationary license restrictions at the time of day or in passenger count. These are easy to drop from a summary but matter for any joint-investigation analysis.

# Fixture notes — ntsb_marine_ugly_002

## What this document pressures

This NTSB marine investigation report is well-suited to several stress points that frequently break naive extraction pipelines and shallow reading by LLMs.

### Clock-time arithmetic anchored to AIS data
The Event Sequence cites AIS data with seconds-level precision (1647:04, 1650:09, 1654:20). The Analysis re-uses these to claim a near-full-stop in roughly seven minutes. Three of the date/chronology questions exercise elapsed-time computation:
- 1657 distress call → 1712 last AIS = 15 min (q008).
- 1717 EPIRB alert → 1808 response-boat recovery = 51 min (q009).
- 1409 NWS Coastal Waters Forecast → 1657 distress = 2 h 48 min (q010).
- 1647:04 (4.0 kt) → 1654:20 (0.6 kt) = 7 min 16 sec (q022).

### Identity-shift across vessel lifetime
The towing vessel was built in 1997 as `Trent Joseph` for Coastal Towing LLC, acquired in 2023 by Trinity Tugs LLC and renamed `Baylor J. Tregre`. The Vessel Particulars table records only the current name and current owner. q003 requires a join across the Background section (1.1) and the Vessel Particulars table to surface the prior-name history.

### Absence-as-fact in the Conclusions
Section 3 contains only 3.1 Probable Cause. There is no separately labeled "Contributing Factor(s)" subsection. q021 explicitly tests whether a model fabricates contributing factors or correctly reports their absence.

### Survey "recommended" but did not specify
The April 22, 2024 suitability survey said "Careful consideration is to be given to weather criteria for the tow of MARMAC 27" but did not specify weather-criteria limits, yet concluded the vessel was suitable. q018 probes this nuanced "recommended without quantifying" pattern.

### Two-prong reason joins
q024 requires both reasons the doghouse-based tow release was infeasible:
1. doghouse partially submerged / inaccessible
2. winch engine not running AND engine room inaccessible due to port heel

Pipelines that summarize the Analysis to one sentence ("the doghouse was underwater") miss the second prong.

### Multi-source wind-speed reconciliation
q023 forces a comparison among the captain's qualitative estimate (85–100 mph ≈ 74–87 kt, no exact time given), the closest NWS reporting site KGLS at 48 kt at 1724, and the GNJT2 buoy at 62 kt at 1718. The Analysis collapses the latter two into "48–62 knots (22–27 miles from the casualty site)"; the question requires recovering the per-source values from section 1.3.3.1.

### Severity mismatch surface vs narrative
q025 reconciles the Casualty Summary's "1 minor" injury entry with the narrative's deckhand 2 airlift to a local hospital. The fields appear in different sections; a join is required.

### Foreign-name preservation
The source uses "Gulf of America" rather than "Gulf of Mexico." Preservation is intentional; QA does not test the body of water by name but the geographic facts (distance, direction from Galveston) hold under either name.

### "Subchapter M" footnote chain
Footnote 3 defines 46 CFR Subchapter M. Footnote 8 invokes the same authority to explain why an emergency tow release in the wheelhouse was not required. q016 tests both prongs (absence + non-requirement).

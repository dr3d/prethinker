# Fixture notes — ntsb_marine_investigation_001

## Why this document

NTSB Marine Investigation Report MIR-25-21 (capsizing and sinking of the towing vessel Baylor J. Tregre, Gulf of America, 23 nm south of Galveston, May 13, 2024; case DCA24FM038) was chosen because it is a real, final-status NTSB marine report that combines:

- A formal probable-cause statement (forcing the system to recognize a deterministic-style declaration distinct from preliminary language).
- An extensive Event Sequence section with secondsecond-level AIS timestamps (1647:04, 1650:09, 1654:20, 1657, 1712, 1717, 1804, 1808, 2130).
- Multi-day chronology: agreement signed May 11; departure 0340 May 11; course change 0630 May 13; capsizing 1657 May 13; assist tug 2130 May 13; surveyor on barge May 14; tow wire cut May 15; salvage May 18 – June 15; vessel to dock June 12; NTSB examination July 9–10.
- A nested cast: Trinity Tugs LLC (operator), Coastal Towing LLC (original owner), R&S Fabricators Inc. (builder), Manson Construction Co. (lessee of barge), McDonough Marine Service (owner of barge), American Bureau of Shipping (barge load line), US Coast Guard (multiple units: Sector Houston-Galveston, District 8 New Orleans, Station Freeport, Air Station Houston, Marine Safety Unit Texas City).
- Multiple weather authorities with overlapping but discordant observations (KGLS, GNJT2, KGVW, the Space Science Engineering Center at U. Wisconsin-Madison via GOES-16), plus NWS-issued products at four distinct times (1257 watch, 1409 Coastal Waters Forecast, 1501 SMW, 1544 SMW update).
- A clear conflict between an eyewitness (captain) wind estimate (85–100 mph / 74–87 knots) and recorded NWS observations (48–62 knots), which the report itself flags rather than resolves.
- Multiple negative facts: no pollution; suitability survey did not specify weather criteria limits; IMO number "N/A"; classification society "N/A".

## Pressure this fixture applies to Prethinker

1. **Cause vs contributing factor separation.** The Probable Cause is one sentence; the Analysis contains additional contributing conditions (loss of stability via deck edge immersion, multiple flooding openings, no emergency tow release). The system should not conflate these into the probable cause.
2. **Authority disambiguation.** "The closest NWS location reported … 48–62 knots" is itself an aggregated claim that the source partitions into KGLS (48), GNJT2 (62), and KGVW (40 gust) at different distances. A faithful KB should not collapse them.
3. **Negative-knowledge handling.** Three explicit negatives: "did not specify weather criteria limits," "IMO N/A," "Classification society N/A," plus an environmental damage "None" cell. The system must not infer "0" or "unknown" — it must store "not specified / not applicable."
4. **Multi-condition reasoning.** The "could not release the tow" finding requires combining three conditions: (a) no emergency release in wheelhouse / not required, (b) doghouse partially submerged and inaccessible, (c) winch engine not running and engine room inaccessible due to heel. Single-condition answers should be considered incomplete.
5. **Numeric units.** Knots vs mph vs kts, statute miles vs nautical miles (Footnote 1 explicitly defines), feet vs meters, GRT, hp vs kW. The fixture should not allow silent unit drift.
6. **Entity continuity.** The vessel name changed (Trent Joseph → Baylor J. Tregre, 2023). Trinity Tugs LLC is named both as "Trinity Tugs LLC" and "Trinity Towing LLC" in different captions (the Figure 1 source is "Trinity Towing LLC"). A faithful representation may need to record both forms.

## Messy features present

- Section numbers (1.3.3.1, 1.3.3.2) and a deeply nested heading structure.
- Footnotes 1–8 inline, including a regulatory footnote (Subchapter M; effective July 20, 2018) and a definitional one (mesoscale convective system).
- A direct quotation from the suitability survey that is itself non-specific ("Careful consideration is to be given to weather criteria for the tow of MARMAC 27.").
- Multi-source weather data, each at its own distance from the casualty.
- "Gulf of America" used as a place name in the source — a politically/temporally specific usage that must not be modernized or substituted by the extraction process.
- "Trinity Tugs LLC" vs "Trinity Towing LLC" inconsistency in the source (Figure 1 caption attribution).

## Expected hard question types

- Reconstruct the NWS product timeline with each product type and time (q011).
- Reconcile captain's wind estimate with NWS observations and acknowledge the source's explicit framing (q020).
- Enumerate flooding openings and distinguish pre-storm deterioration from storm damage (q021).
- Three-factor synthesis for the tow release failure (q025).

# Fixture notes — ntsb_aviation_investigation_001

## Why this document

NTSB preliminary report DCA26MA024 (UPS Flight 2976, MD-11F, Louisville, KY, Nov 4 2025) was chosen because it is a real-world, federally issued investigative document that is:

- Public and citable, with a stable issuer (NTSB).
- Heavy in fact density: multiple timestamps to the second, multiple casualty counts, multiple identifiers (accident number, registration, runway, ICAO/FAA airport codes, AD numbers), and an internal pair of altitude readings that disagree.
- Stamped as preliminary on every page, which gives the fixture a documented "no probable cause yet" surface to test negative-knowledge handling.
- Multi-party — explicitly names FAA, UPS, Boeing, IPA, GE, and Teamsters as participants, which is good source-attribution pressure.
- Includes a comparison to a 46-year-old similar event (American Airlines flight 191, May 25 1979), which enables a cross-section synthesis question without inventing facts.

## Pressure this fixture applies to Prethinker

1. **Preliminary-status discipline.** The repeated caveat "This information is preliminary and subject to change" must propagate into the KB. Asking for a probable cause should resolve to "not yet determined / report is preliminary," not a guess.
2. **Conflicting numeric authority.** FDR radio altitude says "~30 ft agl"; FAA-provided ADS-B data says "100 ft agl / 481 ft msl" for the last data point. The fixture must not silently pick one. Either both are stored with source attribution, or the system reports a discrepancy.
3. **Negative space.** Passenger Injuries is blank in the table; the flight was non-scheduled cargo with 3 crew aboard. A correct answer is "blank / not stated," not "0".
4. **Source attribution.** Different actions were taken by different entities (Boeing recommended grounding, UPS grounded the fleet, FAA issued ADs, the NTSB issued the report). Conflating these is failure.
5. **Identifier preservation.** Accident number, registration, runway, AD numbers, and crew names should all be recoverable verbatim.
6. **Cycles vs interval reasoning.** SDI tasks "had not been accomplished," but the airplane had not reached their cycle thresholds either. This is a subtle conflict_discrepancy case that asks the system to report what is in the source rather than infer fault.

## Messy features present

- Page-break artifacts in the running text where the original PDF wraps mid-paragraph.
- A mixture of narrative prose, key/value tables, and figure callouts.
- Multiple time formats (`17:14`, `1714 EST`, `1713:30 EST`, `2033:41` in cited prior reports).
- A blank cell preserved from the source.
- Cross-referenced prior NTSB report (DCA79AA017 / AAR-79-17) without giving full content.

## Expected hard question types

- Two-source altitude reconciliation (q020).
- SDI threshold vs cycles-on-airframe reasoning (q021).
- ATC group absence despite specialist on scene (q022).
- Synthesis pulling the History of Flight section together with the Similar Events section (q025).

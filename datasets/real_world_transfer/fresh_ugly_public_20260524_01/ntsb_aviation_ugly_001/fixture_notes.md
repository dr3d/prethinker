# Fixture Notes — ntsb_aviation_ugly_001

## Why this document was chosen

This is an active NTSB Class 1 preliminary aviation report for a recent high-profile multi-fatal accident (UPS Flight 2976, Louisville, Nov 4 2025). It has the structural features that pressure-test a system claiming to be a logic extractor over real documents: many overlapping date/time fields (event time vs. recorder times vs. maintenance task dates vs. AD issuance dates vs. comparator 1979 event), multi-category injury totals split across crew / ground / total, identifiers that look similar but mean different things (registration N259UP, accident number DCA26MA024, flight 2976, AD 2025-23-51, AD 2025-23-53), and an explicit set of parties (FAA, UPS, Boeing, IPA, GE, Teamsters) with named individuals attached.

## Messy features

- **Two engine numbering conventions interleaved**: the report alternates "left (No. 1)" and "right (No. 3)" — a question asking "which engine separated" must resolve "left" and "No. 1" to the same referent.
- **A 1979 comparator accident** (American Airlines 191, DCA79AA017) is described in narrative form inside the report. Naive keyword matching could confuse the comparator's casualties (273 total deaths) with the 2025 UPS accident's casualties (14 fatal).
- **Three crewmember roles** (captain = pilot monitoring; first officer = pilot flying; relief officer) with three different total-flight-hour figures and three different time-in-type figures.
- **Two FDR/CVR time anchors**: CVR holds 2h4m; FDR holds 63h spanning 24 flights; the accident-flight data itself is bounded by 1707 EST start and 1713:30 EST end with a 1712 EST takeoff roll. The "event time" is 1714 Local in the header — but the FDR ended at 1713:30. Asking "when did the flight data end" vs. "when did the accident occur" tests source-vs-summary discrimination.
- **Maintenance dates with a missed-inspection finding**: GVI/detailed visual last done Oct 28 2021; lube task last done Oct 18 2025; two SDIs would have been due at cycle thresholds the aircraft had not yet reached (29,200 and 28,000 cycles vs. actual 21,043). The reasoning trap is whether "not accomplished" means "overdue" — the report makes clear it does not, because the cycle threshold was beyond current cycles. A logic extractor that flattens "had not been accomplished" into "was overdue" will be wrong.
- **Two emergency ADs in sequence**: AD 2025-23-51 (Nov 8) superseded by AD 2025-23-53 (Nov 14), with the second expanding scope to include DC-10. Order, supersession, and scope expansion all matter.
- **Mixed coordinate formats**: site debris center given in DMS ("38° 8' 49.85" north by 85° 44' 3.86" west") AND in decimal ("38.14718, -85.734333") in different parts of the report. They refer to the same point but use different notations.
- **Ground-vs-air injury split**: total injuries (14F/2S/21M) decompose into 3F crew + 11F/2S/21M ground. A question on "total fatalities" must add 3 + 11.
- **Tabular layout artifacts**: form fields wrap across lines ("Injuries: 14 Fatal, 2 Serious, 21 / Minor"). PDF text extraction shows the line break.
- **Operator name appears in two cases**: "United Parcel Service (UPS)" in narrative, "UNITED PARCEL SERVICE CO" in the tabular operator field.
- **A page-numbering artifact**: extracted text stream is missing "Page 9 of 12" header line (figure-only page).

## Prethinker design pressure

1. **Source-record vs. summary discrimination**: the tabular blocks at the end are the canonical record. The narrative re-states facts in prose. A question like "what was the destination airport ICAO" is answered from the table (PHNL); the narrative gives only the name. Likewise, the table gives lat/long in decimal; the narrative gives DMS.
2. **Timeline reconstruction across heterogeneous anchors**: clearance ~1711 → takeoff roll ~1712 → FDR end 1713:30 → "event time" 1714 → NTSB on-scene Nov 5 → fleet grounded Nov 7 → AD #1 Nov 8 → AD #2 Nov 14. These are not all on the same clock granularity.
3. **Entity disambiguation under aliasing**: "left (No. 1) engine", "left pylon", "left wing clevis", "aft mount", "spherical bearing" all refer to a chain of components. Asking "what was found fractured" requires distinguishing the aft mount lugs (fatigue+overstress), the forward lug outboard surface (overstress only), and the spherical bearing outer race (circumferential fracture).
4. **Negation and conditional facts**: "had not been accomplished" combined with "would have been due at 29,200 cycles" combined with "the airplane had 21,043 cycles" means the SDI was NOT overdue. Any clean rule like "missed inspection → overdue" is wrong.
5. **Numeric quantity reasoning**: counting fatalities, counting ground vs. air, distinguishing total flight hours from time-in-type, decoding "92,992 hours and 21,043 cycles" as two separate quantities.
6. **Parties-with-people join**: who from UPS participated? who from Boeing? Requires looking up the Additional Participating Persons block, which is rendered as a two-column "Name; Organization" list.

## Source caveats

- Document is explicitly marked "preliminary and subject to change." Oracle answers reflect the state of this preliminary report as published; the eventual NTSB final report may revise facts.
- The fatigue/overstress findings are factual observations of fracture morphology, not a causal determination. The report does NOT state a probable cause; final probable cause determination will appear in the final NTSB report.

## Local normalization note

The incoming `qa.md` contained both questions and authored reference answers using `q001`-style markers. It was preserved as `qa_authored_with_answers.md`; the canonical `qa.md` was regenerated from `qa_questions.jsonl` as numbered, questions-only Markdown for `scripts/run_domain_bootstrap_qa.py`. Reference answers remain isolated in `oracle.jsonl` for after-the-fact scoring only.

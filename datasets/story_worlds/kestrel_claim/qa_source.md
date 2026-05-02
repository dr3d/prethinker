# The Kestrel Claim QA Source

Source-provided 100-question battery converted from `qa_battery_100.json`.

## KS-001 (basic_fact)

**Question:** What type of vessel is the M/V Kestrel?

**Answer:** An 82,000 DWT bulk carrier, built in 2018

**Notes:** Vessel identification

## KS-002 (basic_fact)

**Question:** Who manages the Kestrel?

**Answer:** Meridian Ship Management Ltd, Cyprus

**Notes:** Management identification

## KS-003 (basic_fact)

**Question:** What is the insured value of the Kestrel?

**Answer:** USD 28,500,000

**Notes:** Policy value

## KS-004 (basic_fact)

**Question:** What caused the grounding?

**Answer:** Contact with an uncharted submerged obstruction while transiting the Bight of Benin

**Notes:** Incident cause

## KS-005 (temporal)

**Question:** When did the grounding occur?

**Answer:** October 12, 2025 at 03:17 UTC (corrected from initially reported 03:22 UTC)

**Notes:** Must use corrected time

## KS-006 (correction)

**Question:** What was the initially reported grounding time and why was it wrong?

**Answer:** 03:22 UTC — this was actually the time of the Chief Engineer's flooding report, not the impact itself. The VDR shows the impact at 03:17 UTC.

**Notes:** Correction with explanation

## KS-007 (insurance_structure)

**Question:** Who is the lead H&M underwriter and what is their share?

**Answer:** Oceanic Syndicate 1847 at Lloyd's of London, with a 45% line

**Notes:** Lead underwriter identification

## KS-008 (insurance_structure)

**Question:** What are the shares of all three H&M underwriters?

**Answer:** Oceanic Syndicate 1847: 45% (lead), Nordic Marine Insurance AS: 30%, Harbour Mutual P&I: 25%

**Notes:** Full underwriter enumeration

## KS-009 (dual_role)

**Question:** In what two capacities does Harbour Mutual participate in this loss?

**Answer:** As an H&M following underwriter (25% line on Policy HM-KES-2025-0417) and as the P&I club insurer for third-party liabilities. These are separate contracts with separate terms.

**Notes:** Dual-role identification — critical test

## KS-010 (deductible)

**Question:** What is the applicable deductible for this grounding claim?

**Answer:** USD 250,000 (the grounding/stranding deductible, not the machinery damage deductible of USD 150,000)

**Notes:** Must select correct deductible type

## KS-011 (competing_accounts)

**Question:** What fracture length did the owner's surveyor report for the No. 2 double-bottom tank?

**Answer:** Approximately 3.2 meters

**Notes:** Source-attributed measurement — Papadopoulos

## KS-012 (competing_accounts)

**Question:** What fracture length did the underwriters' surveyor report for the same damage?

**Answer:** Approximately 2.8 meters

**Notes:** Source-attributed measurement — Ashworth

## KS-013 (competing_accounts)

**Question:** Why do the two surveyors' fracture measurements differ?

**Answer:** Papadopoulos measured the widest extent including hairline extensions visible under magnetic particle inspection. Ashworth measured only the structural fracture requiring plate renewal, excluding hairline extensions that would be addressed by weld repair. Both methodologies are defensible.

**Notes:** Must preserve both methodologies without resolving

## KS-014 (competing_accounts)

**Question:** Did the owner's surveyor report any damage to the No. 3 double-bottom tank?

**Answer:** No — Papadopoulos did not report any damage to No. 3 tank

**Notes:** Absence in one report

## KS-015 (competing_accounts)

**Question:** Did the underwriters' surveyor report damage to the No. 3 tank?

**Answer:** Yes — Ashworth noted minor indentation to the No. 3 tank shell plating, not requiring immediate repair but recommended for monitoring

**Notes:** Present in one report, absent in other

## KS-016 (correction)

**Question:** What was the original depth measurement for the No. 3 tank indentation and how was it corrected?

**Answer:** Originally reported as approximately 15mm deep, corrected to approximately 8mm deep. The 15mm was a preliminary field measurement superseded by calibrated drydock measurement. The corrected 8mm figure is within class society tolerance for shell plating deformation.

**Notes:** Correction that changes both measurement AND significance

## KS-017 (financial)

**Question:** What is the total H&M claim amount before deductible?

**Answer:** USD 1,009,000 (claimant's figure)

**Notes:** Gross claim — claimant position

## KS-018 (financial)

**Question:** What is the net H&M claim after deductible according to the claimant?

**Answer:** USD 759,000 (USD 1,009,000 minus USD 250,000 deductible)

**Notes:** Net claim — claimant position

## KS-019 (financial)

**Question:** What is Oceanic's adjusted total before deductible?

**Answer:** USD 720,000

**Notes:** Gross claim — underwriter position

## KS-020 (financial)

**Question:** What is the net difference between the claimant's and Oceanic's positions?

**Answer:** USD 289,000 (claimant net USD 759,000 minus Oceanic net USD 470,000)

**Notes:** Net difference calculation

## KS-021 (claim_dispute)

**Question:** What three items are in dispute between claimant and underwriter?

**Answer:** 1) Hull repair quantum (USD 40,000 difference due to fracture measurement methodology); 2) Loss of hire (USD 234,000 — claimant says covered as consequential loss, Oceanic says no LOH clause); 3) BV accelerated survey fee (USD 15,000 — claimant says consequential to covered loss, Oceanic says not a direct repair cost)

**Notes:** Must enumerate all three with amounts and reasoning

## KS-022 (reinsurance)

**Question:** Is Pinnacle Re triggered on this claim?

**Answer:** No — Oceanic's 45% share of the adjusted net claim is USD 211,500, which is below Pinnacle Re's attachment point of USD 500,000

**Notes:** Reinsurance arithmetic

## KS-023 (reinsurance)

**Question:** Would Pinnacle Re be triggered even if the full claimant figure were accepted?

**Answer:** No — 45% of USD 759,000 is USD 341,550, which is still below the USD 500,000 attachment point

**Notes:** Conditional reinsurance arithmetic

## KS-024 (reinsurance)

**Question:** Was the reinsurance notification to Pinnacle Re timely?

**Answer:** No — Oceanic became aware of the grounding at 07:15 UTC on October 12 and notified Pinnacle Re at 10:00 UTC on October 17, approximately 98.75 hours later. The treaty requires notification within 72 hours.

**Notes:** Temporal arithmetic — elapsed hours calculation

## KS-025 (reinsurance)

**Question:** Does the late reinsurance notification affect the assured's claim?

**Answer:** No — Oceanic has confirmed that the late notification is an internal matter between Oceanic and Pinnacle Re and does not affect the assured's entitlements. Additionally, Pinnacle Re is not triggered on this claim.

**Notes:** Must distinguish reinsurance issue from assured's claim

## KS-026 (cover_suspension)

**Question:** When was H&M cover suspended?

**Answer:** From October 15, 2025 at 08:00 UTC (when the Condition of Class was imposed) to October 28, 2025 at 16:00 UTC (when class was reinstated)

**Notes:** Precise suspension window

## KS-027 (cover_suspension)

**Question:** How long was the cover suspension period?

**Answer:** 13 days and 8 hours

**Notes:** Duration calculation

## KS-028 (cover_suspension)

**Question:** Does the Classification Clause suspension prevent recovery of repair costs?

**Answer:** Disputed. Oceanic argues costs during suspension not directly for class rectification are uncovered. Kestrel argues costs of rectifying the CoC are covered because the condition arose from a covered peril, citing The Bamburi [1982]. The dispute is unresolved.

**Notes:** Must preserve both positions without resolving

## KS-029 (loss_of_hire)

**Question:** How many days was the vessel off-hire?

**Answer:** 16 days total (October 12 to October 28), of which 3 days were salvage operations and 13 days were repair-attributable

**Notes:** Off-hire calculation with salvage/repair split

## KS-030 (loss_of_hire)

**Question:** Is loss of hire covered under the H&M policy?

**Answer:** Disputed. The policy does not contain a Loss of Hire clause. Kestrel argues it's recoverable as consequential loss. Oceanic argues it's excluded under IHC 2003 Clause 23.4 absent a specific LOH endorsement. Kestrel does not have a separate LOH policy.

**Notes:** Coverage interpretation dispute — must preserve both positions

## KS-031 (defense)

**Question:** What three defenses has Oceanic raised?

**Answer:** 1) Classification Clause suspension — cost allocation during suspended cover; 2) Navigation due diligence — reserved but not invoked; 3) Late reinsurance notification — acknowledged as internal matter, not a defense to the assured

**Notes:** Defense enumeration with status

## KS-032 (defense)

**Question:** Has Oceanic alleged negligent navigation?

**Answer:** No — Oceanic has reserved the right to argue that navigation contributed to the loss but has not alleged negligent navigation at this time. The defense is reserved, not invoked.

**Notes:** Critical distinction: reserved vs invoked

## KS-033 (navigation)

**Question:** How many different positions exist on the navigation issue?

**Answer:** Five: 1) Owner's surveyor — consistent with prudent seamanship; 2) Underwriters' surveyor — narrow margin, not alleging negligence; 3) Master — entirely safe; 4) Panama flag state — no fault; 5) Togolese DAM — recommendation not retroactive, no deficiency implied

**Notes:** Multi-position enumeration on unresolved dispute

## KS-034 (navigation)

**Question:** What did Ashworth observe about the vessel's AIS track?

**Answer:** The vessel was approximately 0.7 nautical miles inside the charted 10-meter depth contour, and Ashworth stated that the margin of safety was narrower than would ordinarily be expected

**Notes:** Specific observation from underwriters' surveyor

## KS-035 (regulatory)

**Question:** Was the pollution prevention plan submitted within the required timeframe?

**Answer:** Yes — the DAM directive required submission within 48 hours of October 12 14:00 UTC. The plan was submitted at 12:00 UTC on October 14, which is 46 hours later.

**Notes:** Regulatory deadline compliance

## KS-036 (regulatory)

**Question:** What did the Panama Maritime Authority conclude about the grounding?

**Answer:** Preliminary finding: the grounding was caused by contact with an uncharted submerged object. Navigation was consistent with COLREGs and SOLAS Chapter V requirements. No fault attributed to the vessel, its officers, or its managers.

**Notes:** Flag state finding

## KS-037 (regulatory)

**Question:** Is the DAM recommendation retroactive?

**Answer:** No — the DAM recommendation that vessels maintain 2nm clearance from shallow-water contours is explicitly not retroactive and does not imply that the Kestrel's navigation was deficient under the regulations in force at the time

**Notes:** Non-retroactivity — must not apply to Kestrel

## KS-038 (sanctions)

**Question:** Was the Cotonou port call made?

**Answer:** No — the call was canceled on October 2, 2025 after Meridian's compliance officer determined that the bunker supplier had a corporate parent entity on the US OFAC SDN list

**Notes:** Sanctions compliance — call not made

## KS-039 (sanctions)

**Question:** Has Oceanic raised the trading warranty defense?

**Answer:** No — Oceanic stated on November 28, 2025 that it does not intend to raise the trading warranty defense

**Notes:** Defense not raised

## KS-040 (sanctions)

**Question:** Even if the trading warranty defense were raised, would it succeed?

**Answer:** Wavecrest argues no, because the breach was remedied before the loss occurred and did not contribute to it, per Section 10 of the Insurance Act 2015

**Notes:** Hypothetical defense analysis

## KS-041 (salvage)

**Question:** What salvage contract was executed?

**Answer:** Lloyd's Open Form (LOF 2020), no-cure-no-pay basis, between the Master of Kestrel and Dorado Salvage Ltd (Abidjan)

**Notes:** Salvage contract details

## KS-042 (salvage)

**Question:** What is the salvage security amount?

**Answer:** USD 4,500,000 (corrected from initially reported USD 5,000,000)

**Notes:** Must use corrected amount

## KS-043 (salvage)

**Question:** Is the salvage security an actual payment?

**Answer:** No — it is a guarantee posted pending the outcome of LOF arbitration. The actual salvage award may be significantly less.

**Notes:** Security vs payment distinction

## KS-044 (pi_exposure)

**Question:** What is the total P&I exposure?

**Answer:** USD 7,855,000 — comprising cargo damage claim (USD 3,200,000), salvage security (USD 4,500,000), and pollution prevention costs (USD 180,000), less P&I deductible (USD 25,000 applied to pollution costs)

**Notes:** Financial enumeration with deductible application

## KS-045 (pi_exposure)

**Question:** What is the cargo damage claim?

**Answer:** USD 3,200,000 from Lagos Commodity Trading Ltd, for contamination by seawater of the 12,000 MT of soybean meal discharged into barges during salvage. Status: under investigation.

**Notes:** Cargo claim details

## KS-046 (temporal)

**Question:** When was the Condition of Class imposed?

**Answer:** October 15, 2025 at 08:00 UTC, by BV surveyor Capt. François Delacroix

**Notes:** CoC imposition timestamp

## KS-047 (temporal)

**Question:** When was the Condition of Class lifted?

**Answer:** October 28, 2025, after satisfactory repair and testing, by BV surveyor Delacroix

**Notes:** CoC lifted timestamp

## KS-048 (temporal_calculation)

**Question:** How many hours elapsed between Oceanic becoming aware of the grounding and notifying Pinnacle Re?

**Answer:** Approximately 98.75 hours (October 12 07:15 UTC to October 17 10:00 UTC)

**Notes:** Cross-day hour calculation

## KS-049 (temporal_calculation)

**Question:** By how many hours did Oceanic miss the 72-hour reinsurance notification deadline?

**Answer:** Approximately 26.75 hours (98.75 hours elapsed minus 72 hours required)

**Notes:** Deadline overshoot calculation

## KS-050 (financial_arithmetic)

**Question:** What is Oceanic's 45% share of the adjusted net claim?

**Answer:** USD 211,500 (45% × USD 470,000)

**Notes:** Share calculation

## KS-051 (financial_arithmetic)

**Question:** How far below the Pinnacle Re attachment point is Oceanic's share?

**Answer:** USD 288,500 below (USD 500,000 attachment minus USD 211,500 share)

**Notes:** Difference calculation

## KS-052 (repair_cost)

**Question:** What is the difference in repair cost assessments between the two surveyors?

**Answer:** USD 40,000 (Papadopoulos: USD 485,000; Ashworth: USD 445,000)

**Notes:** Cost comparison

## KS-053 (repair_cost)

**Question:** On which specific cost items do the surveyors agree?

**Answer:** Drydock charges: both assess USD 120,000. They also agree on no damage to propeller, rudder, or shaft.

**Notes:** Agreement identification within competing reports

## KS-054 (repair_cost)

**Question:** On which specific cost items do the surveyors disagree?

**Answer:** Labor (USD 210,000 vs USD 185,000), steel (USD 95,000 vs USD 90,000), NDT/testing (USD 35,000 vs USD 30,000), and coating (USD 25,000 vs USD 20,000)

**Notes:** Disagreement identification with specific figures

## KS-055 (multilingual)

**Question:** What did the Master say about the vessel's navigation?

**Answer:** He said (in Russian) that they followed the recommended route for vessels with draft exceeding 12 meters, the chart showed at least 18 meters on their course, the object was not marked on any chart, and he believes the navigation was entirely safe

**Notes:** Extracted from Russian statement

## KS-056 (multilingual)

**Question:** What did the Chief Engineer report about the damage?

**Answer:** He said (in Greek) that the No. 2 double-bottom tank was breached almost immediately, he activated bilge pumps within three minutes, there was no danger of sinking as damage was limited to one tank, and the engines were not affected

**Notes:** Extracted from Greek statement

## KS-057 (multilingual)

**Question:** What did the Meridian duty manager say about the notification timeline?

**Answer:** He said (in French) that he received the captain's call at 04:00 UTC, immediately contacted the claims department, notification to Oceanic was sent at 06:30 UTC, and the reinsurance notification is Oceanic's responsibility, not his

**Notes:** Extracted from French statement

## KS-058 (claim_vs_fact)

**Question:** Is Ashworth's observation about the navigation margin a finding of negligence?

**Answer:** No — Ashworth states that the margin of safety was narrower than would ordinarily be expected but stops short of alleging negligent navigation. It is an observation, not a finding.

**Notes:** Observation vs finding distinction

## KS-059 (claim_vs_fact)

**Question:** Is Papadopoulos's assessment of navigation prudence a finding?

**Answer:** It is the owner's surveyor's expert opinion, not an official finding. Panama's flag-state investigation is the official regulatory finding.

**Notes:** Expert opinion vs official finding

## KS-060 (legal_citation)

**Question:** What legal authority does Wavecrest cite regarding costs during cover suspension?

**Answer:** The Bamburi [1982] 1 Lloyd's Rep. 312 — for the principle that costs reasonably incurred in mitigating or repairing a covered loss are recoverable even if incurred during a period of suspended cover

**Notes:** Citation retrieval — citation supports argument, not fact

## KS-061 (legal_citation)

**Question:** What legal authority does Wavecrest cite regarding the navigation defense?

**Answer:** The Star Sea [2001] UKHL 1 — for the standard of due diligence under marine insurance

**Notes:** Citation retrieval

## KS-062 (legal_citation)

**Question:** What policy clause does Oceanic cite to exclude loss of hire?

**Answer:** IHC 2003 Clause 23.4 — which excludes consequential losses absent a specific Loss of Hire endorsement

**Notes:** Policy clause citation

## KS-063 (class_survey)

**Question:** Did BV comment on the No. 3 tank damage?

**Answer:** No — BV noted that the No. 3 tank was not within the scope of the Condition of Class inspection. BV does not assess cause, fault, or repair cost; these are outside the scope of a class survey.

**Notes:** Scope limitation of class survey

## KS-064 (enumeration)

**Question:** How many corrections were filed after the incident?

**Answer:** Three corrections and one clarification

**Notes:** Post-incident correction count

## KS-065 (correction)

**Question:** What was Correction 3 about?

**Answer:** The salvage security amount was initially reported as USD 5,000,000 and corrected to USD 4,500,000. The USD 5,000,000 included a contingency not ordered by the arbitrator.

**Notes:** Correction retrieval

## KS-066 (temporal_ordering)

**Question:** List the key events of October 12 in chronological order.

**Answer:** 03:17 UTC grounding impact; 03:22 UTC flooding reported; 03:45 UTC emergency declared; 04:00 UTC Master contacts Meridian; 06:30 UTC Meridian notifies Oceanic; 07:00 UTC Meridian notifies Harbour Mutual P&I; 07:15 UTC Oceanic acknowledges; 14:00 UTC DAM directive issued

**Notes:** Chronological ordering with corrected grounding time

## KS-067 (temporal_ordering)

**Question:** What happened between the refloating and the drydock?

**Answer:** October 14 16:00: vessel refloated, proceeds to Lomé anchorage; October 15 08:00: BV inspection, CoC imposed; October 15 14:00: Oceanic notified of CoC; October 17 10:00: Oceanic notifies Pinnacle Re; October 20: tow to Tema begins; drydocking commences at Tema

**Notes:** Event sequence between refloating and repair

## KS-068 (vessel)

**Question:** What was the vessel's cargo at the time of grounding?

**Answer:** 74,000 MT of Brazilian soybean meal, on a voyage from Santos, Brazil to Lagos, Nigeria

**Notes:** Cargo and voyage details

## KS-069 (salvage)

**Question:** How much cargo was discharged during salvage?

**Answer:** Approximately 12,000 MT of soybean meal, discharged into barges

**Notes:** Salvage cargo quantity

## KS-070 (charter)

**Question:** What is the daily charter rate for the Kestrel?

**Answer:** USD 18,000 per day under a time charter to Atlantic Grain Carriers SA

**Notes:** Charter rate

## KS-071 (financial_arithmetic)

**Question:** How is the loss of hire amount of USD 234,000 calculated?

**Answer:** 13 days of repair-attributable off-hire × USD 18,000/day = USD 234,000. The 3 days of salvage operations are excluded because the vessel was under the salvage master's control, not the charterer's.

**Notes:** Derivation of loss of hire figure

## KS-072 (reinsurance_structure)

**Question:** What are Pinnacle Re's attachment point and limit?

**Answer:** Attachment point: USD 500,000 net to Oceanic. Limit: USD 5,000,000 any one vessel.

**Notes:** Reinsurance layer terms

## KS-073 (reinsurance_structure)

**Question:** What is the retrocession structure above Pinnacle Re?

**Answer:** Fortis Re, Zurich, under Retrocession Certificate FRC-2025-044, with attachment at USD 5,500,000 (USD 5,000,000 excess of USD 500,000 net to Oceanic) and a limit of USD 8,000,000

**Notes:** Retrocession layer

## KS-074 (reinsurance)

**Question:** What is the effect of late notification under Pinnacle Re's treaty?

**Answer:** Late notification does not automatically void coverage. It entitles the reinsurer to reduce its liability by the amount of prejudice caused by the late notice, which must be proved by the reinsurer.

**Notes:** Late notice effect — not automatic void

## KS-075 (pi_structure)

**Question:** What is the P&I notification requirement?

**Answer:** The member must notify the club of any incident likely to give rise to a P&I claim within 14 days of the incident

**Notes:** P&I notification deadline

## KS-076 (pi_structure)

**Question:** When does the P&I club year run?

**Answer:** From February 20 to February 20 (noon GMT), not calendar year

**Notes:** P&I club year — different from H&M policy year

## KS-077 (dual_role)

**Question:** Are Harbour Mutual's H&M and P&I roles governed by the same contract?

**Answer:** No — the two roles are governed by separate contracts with separate terms, separate notification requirements, and separate deductibles

**Notes:** Dual-role contract separation

## KS-078 (follow_clause)

**Question:** Does Harbour Mutual follow Oceanic's coverage decisions?

**Answer:** Yes on coverage, per the follow-the-leader clause in the slip. But Harbour Mutual reserves the right to disagree on quantum. Harbour Mutual has not raised any independent coverage defense.

**Notes:** Follow clause with quantum reservation

## KS-079 (post_repair)

**Question:** What is the estimated post-repair vessel value?

**Answer:** USD 27,800,000 per the owner's surveyor (pre-incident USD 28,500,000 less depreciation from grounding history and accelerated survey). The underwriters' surveyor did not assess post-repair value, stating it was outside his instruction.

**Notes:** Source-attributed value assessment

## KS-080 (class)

**Question:** What is the effect of the grounding on the vessel's survey schedule?

**Answer:** Bureau Veritas accelerated the next intermediate survey from September 2026 to March 2026, citing the grounding history

**Notes:** Class consequence

## KS-081 (salvage)

**Question:** Who posted the salvage security?

**Answer:** Harbour Mutual P&I, on behalf of Kestrel Maritime Holdings

**Notes:** Security posted by P&I club, not owner directly

## KS-082 (sanctions)

**Question:** Who recommended canceling the Cotonou port call?

**Answer:** Dr. Hanae Yamamoto, Meridian's compliance officer

**Notes:** Compliance officer identification

## KS-083 (sanctions)

**Question:** Why was the Cotonou call considered a sanctions risk?

**Answer:** The bunker supplier at Cotonou had a corporate parent entity on the US OFAC Specially Designated Nationals (SDN) list

**Notes:** Specific sanctions concern

## KS-084 (temporal)

**Question:** How many days before the grounding was the Cotonou call canceled?

**Answer:** 10 days (canceled October 2, grounding October 12)

**Notes:** Temporal gap calculation

## KS-085 (port_call)

**Question:** Did the Kestrel make any port calls between Santos and the grounding location?

**Answer:** Yes — a brief stop at Lomé anchorage on October 8 for approximately 4 hours for a crew change (one AB disembarked for medical evacuation, one replacement embarked)

**Notes:** Intermediate port call

## KS-086 (sanctions)

**Question:** Is Togo a sanctioned jurisdiction?

**Answer:** No — Togo is not subject to EU, US, or UN sanctions

**Notes:** Sanctions status check

## KS-087 (absence)

**Question:** Does Nordic Marine Insurance have reinsurance for its 30% line?

**Answer:** No — Nordic retains its 30% line net, with no facultative reinsurance

**Notes:** Absence of reinsurance arrangement

## KS-088 (claim_vs_fact)

**Question:** Has Oceanic accepted the full claimed amount?

**Answer:** No — Marcus Webb explicitly stated that Oceanic has not accepted the full claimed amount and reserves all defenses

**Notes:** Claims handler position

## KS-089 (clarification)

**Question:** What did Oceanic clarify about the late reinsurance notification defense?

**Answer:** Oceanic clarified on January 5, 2026 that the statement regarding late notification was provided for transparency only, is not a defense to the assured's claim, and the assured's claim will be adjusted on its merits without reference to the reinsurance position

**Notes:** Clarification retrieval

## KS-090 (survey_scope)

**Question:** What does BV explicitly state is outside the scope of a class survey?

**Answer:** Cause, fault, and repair cost — these are outside the scope of a class survey

**Notes:** Scope limitation

## KS-091 (competing_accounts)

**Question:** On which findings do both surveyors agree?

**Answer:** Both agree on: no damage to propeller, rudder, or shaft; drydock charges of USD 120,000; and that the cause was contact with a submerged object

**Notes:** Agreement identification across competing reports

## KS-092 (competing_accounts)

**Question:** On which findings do the surveyors disagree?

**Answer:** 1) Fracture length (3.2m vs 2.8m); 2) No. 3 tank damage (none reported vs minor indentation); 3) Total repair cost (USD 485,000 vs USD 445,000); 4) Navigation assessment (prudent seamanship vs narrow margin); 5) Post-repair value (assessed at USD 27.8M vs not assessed)

**Notes:** Disagreement enumeration

## KS-093 (temporal_window)

**Question:** During what period were both Eastgate-equivalent treatment facilities unavailable?

**Answer:** There is no such period in this fixture — this question is about the Kestrel, not Iron Harbor. The relevant gap is between Eastgate offline and Pier 7 activation. In Kestrel, the question is whether untreated water reached anyone, which is not applicable because this is a maritime case.

**Notes:** Cross-fixture contamination trap — must not import Iron Harbor facts

## KS-094 (enumeration)

**Question:** How many witness or expert statements are in the document?

**Answer:** Seven: Master Volkov (Russian), Chief Engineer Stavridis (Greek), duty manager Constantinou (French), owner's surveyor Papadopoulos (English), underwriters' surveyor Ashworth (English), Wavecrest solicitors (English), and Oceanic claims handler Webb (English)

**Notes:** Statement enumeration with languages

## KS-095 (enumeration)

**Question:** In how many languages are statements given?

**Answer:** Four: Russian, Greek, French, and English

**Notes:** Language enumeration

## KS-096 (financial_arithmetic)

**Question:** What would Oceanic's share be if additional claims pushed the total net claim to USD 2,000,000?

**Answer:** USD 900,000 (45% × USD 2,000,000), which would exceed Pinnacle Re's USD 500,000 attachment point, making the reinsurance layer and the late notification issue relevant

**Notes:** Conditional future arithmetic — the late notice issue becomes live

## KS-097 (comprehensive_summary)

**Question:** Summarize all items that are accepted by both sides (not in dispute).

**Answer:** Towing (USD 85,000), drydock hire (USD 120,000), additional crew costs (USD 42,000), and survey fees (USD 28,000) are accepted by both sides. Both agree the grounding is a covered peril. Both agree no damage to propeller, rudder, or shaft.

**Notes:** Agreement summary across financial and factual dimensions

## KS-098 (comprehensive_summary)

**Question:** Summarize all items that remain in dispute.

**Answer:** 1) Hull repair quantum (USD 40,000 difference); 2) Loss of hire (USD 234,000 — coverage question); 3) BV accelerated survey fee (USD 15,000 — direct cost question); 4) Cost allocation during cover suspension period; 5) Navigation due diligence (reserved, not invoked); 6) Drydock hire allocation between covered and uncovered costs during suspension

**Notes:** Dispute summary

## KS-099 (counterfactual)

**Question:** If the Kestrel had called at Cotonou as originally planned before the grounding, and Oceanic raised the trading warranty defense, would the defense succeed under the Insurance Act 2015?

**Answer:** The defense would likely fail. Under Section 10 of the Insurance Act 2015, a breach of warranty does not discharge the insurer if the breach is remedied before the loss occurs and the breach did not contribute to the loss. In this scenario, the Cotonou call and the grounding are unrelated events. However, the key question would be whether the breach was 'remedied' — a completed port call at a sanctioned entity cannot be undone, only not repeated. This is a genuine legal ambiguity.

**Notes:** Counterfactual with legal reasoning — harder than Iron Harbor or Blackthorn counterfactuals because the answer is genuinely ambiguous

## KS-100 (meta_question)

**Question:** Can this dispute be resolved purely from the facts in this document, or does it require external adjudication?

**Answer:** It cannot be resolved from the document alone. The document records competing positions on hull repair quantum, loss of hire coverage, cost allocation during suspension, and navigation prudence. These disputes require either agreement between the parties, mediation, or arbitration to resolve. The document preserves the positions but does not adjudicate between them.

**Notes:** Meta-epistemic question — the system must recognize the limits of what the document determines

# The Veridia-9 Claim QA Source

Source-provided 40-question battery for complexity testing.

## V9-001 (basic_fact)
**Question:** What is the management entity for Veridia-9?
**Answer:** Biogenix Systems Ltd, Singapore
**Notes:** Entity identification

## V9-002 (basic_fact)
**Question:** What type of product is Veridia-9?
**Answer:** A synthetic biological catalyst, Batch V9-402
**Notes:** Product identification

## V9-003 (basic_fact)
**Question:** What is the agreed insured value per major batch of V9?
**Answer:** USD 42,000,000
**Notes:** Policy value

## V9-004 (basic_fact)
**Question:** What caused the refrigeration failure?
**Answer:** A power-loss event in Transport Unit T-88 during transit between Zurich and Rotterdam
**Notes:** Incident cause

## V9-005 (temporal)
**Question:** When did the temperature breach actually begin?
**Answer:** October 15, 2025, at 03:55 UTC (corrected from initially reported 04:15 UTC)
**Notes:** Must use corrected time from VDR/Correction 1

## V9-006 (correction)
**Question:** What was the initially reported cooling system reset time and why was it wrong?
**Answer:** 04:15 UTC; it was wrong because it represented the driver's first attempt to restart the engine, not the start of the failure
**Notes:** Identification of correction source

## V9-007 (role_identity)
**Question:** Who is the beneficial owner of Veridia-9?
**Answer:** Aether Bio-Ventures SA (Luxembourg)
**Notes:** Ownership roles

## V9-008 (financial)
**Question:** What is the total line percentage held by the following (non-lead) underwriters?
**Answer:** 50% (Northern Bio-Secure at 30% and Mediterranean Pharma Mutual at 20%)
**Notes:** Arithmetic on lines

## V9-009 (contract_boundary)
**Question:** What temperature variance is allowed under the Compliance Clause?
**Answer:** +/-2 degrees C
**Notes:** Contractual constraint

## V9-010 (temporal_logic)
**Question:** Within what timeframe must a temperature variance be reported to maintain cover?
**Answer:** 48 hours
**Notes:** Reporting deadline

## V9-011 (epistemic_conflict)
**Question:** What are the competing conclusions regarding the batch's stability?
**Answer:** Biogenix Internal Lab claims it remained stable via "rapid recovery"; Helix Analytics claims significant degradation (15.4%) and non-viability
**Notes:** Managing competing claims

## V9-012 (financial)
**Question:** After the USD 2.5M deductible, what is the net claim amount according to Biogenix?
**Answer:** USD 35,500,000
**Notes:** Simple arithmetic on claim

## V9-013 (provenance)
**Question:** Which document provides the "black box" sensor data?
**Answer:** The revised report of October 18
**Notes:** Source identification

## V9-014 (identity_ambiguity)
**Question:** Does "Zenith" refer to the re-insurer or the lead underwriter?
**Answer:** The lead underwriter (Zenith Underwriting 1902)
**Notes:** Disambiguation

## V9-015 (regulatory_legal)
**Question:** When did the FDR issue the Hold and Sequestration order?
**Answer:** October 21, 2025, at 23:30 UTC
**Notes:** Regulatory event timing

## V9-016 (temporal_arithmetic)
**Question:** How many minutes did the temperature breach actually last according to the secondary sensor?
**Answer:** 35 minutes (03:55 to 04:30)
**Notes:** Duration calculation

## V9-017 (legal_status)
**Question:** Why does Zenith argue they are discharged from liability for the Nairobi shipment?
**Answer:** Because shipping to Nairobi on Oct 22 breached the Trading Warranty (due to the Oct 1 patent stay)
**Notes:** Legal argumentation

## V9-018 (financial_layers)
**Question:** What is Zenith's exposure if the loss is proven to be USD 38M, considering their 50% line and 80% reinsurance?
**Answer:** Zenith's gross exposure is 50% of 38M (USD 19M); their net exposure after 80% reinsurance is USD 3.8M
**Notes:** Multi-layer financial calculation

## V9-019 (correction)
**Question:** What was the initial protein degradation percentage reported by Helix Analytics?
**Answer:** Approximately 22%
**Notes:** Tracking superseded values

## V9-020 (source_fidelity)
**Question:** Did L. Vance claim the temperature stayed within safety limits in his first report?
**Answer:** Yes, on October 16 at 09:00 UTC
**Notes:** Speech act recording

## V9-021 (regulatory_integrity)
**Question:** Was there any safety violation outstanding in the RIR as of Sept 20, 2025?
**Answer:** No, the record was current with no violations outstanding
**Notes:** Compliance status

## V9-022 (late_notice)
**Question:** Why is Global Re-Ventures (GRV) disputing the reinsurance claim?
**Answer:** They claim "late notice" because the notice was sent 5 days after the event (Oct 20 vs Oct 15)
**Notes:** Reinsurance dispute

## V9-023 (location)
**Question:** Where is the regional hub located that received the suspect units?
**Answer:** Nairobi
**Notes:** Geographic entity

## V9-024 (policy_form)
**Question:** On which form is the Supply Chain Liability policy written?
**Answer:** International Bio-Pharma Clauses (IBC) 2012
**Notes:** Contractual detail

## V9-025 (denial)
**Question:** Did Biogenix admit to receiving the FDR hold order before the units were shipped?
**Answer:** No, they claimed they did not receive it until October 23 (after the Oct 22 shipping)
**Notes:** Conflict of claim vs event

## V9-026 (status_change)
**Question:** What is required to restore cover after a Compliance Clause breach?
**Answer:** A re-certification survey
**Notes:** Conditional logic

## V9-027 (financial_dispute)
**Question:** What is the "market value of raw materials" according to Zenith?
**Answer:** USD 12,000,000
**Notes:** Capturing disputed values

## V9-028 (entity_attribute)
**Question:** In which country is Northern Bio-Secure Ltd based?
**Answer:** Sweden (Stockholm)
**Notes:** Attribute identification

## V9-029 (temporal_anchor)
**Question:** When did the Nairobi Patent Tribunal issue its temporary stay?
**Answer:** October 1, 2025
**Notes:** Anchor event timing

## V9-030 (multilingual_technical)
**Question:** What peak temperature was recorded during the breach?
**Answer:** +6.2 degrees C
**Notes:** Precise measurement

## V9-031 (role_scope)
**Question:** Who is T. Obasi?
**Answer:** The Nairobi hub manager
**Notes:** Role identification

## V9-032 (quantified_groups)
**Question:** What percentage of samples showed degradation according to Helix's final report?
**Answer:** 15.4%
**Notes:** Group attribute (corrected)

## V9-033 (financial_arithmetic)
**Question:** If the batch value is 42M and the loss is 38M, what is the salvage value (residual) being claimed by exclusion?
**Answer:** USD 4,000,000
**Notes:** Derived financial value

## V9-034 (policy_id)
**Question:** What is the full Policy Number?
**Answer:** SCL-V9-2025-0812
**Notes:** Explicit identifier

## V9-035 (sequence_of_events)
**Question:** Did the "black box" extraction occur before or after the Helix audit?
**Answer:** Before (Data extraction by Oct 18, Helix audit Nov 10)
**Notes:** Chronology

## V9-036 (denial_semantics)
**Question:** Did Biogenix deny the refrigeration failure happened?
**Answer:** No, they acknowledged the manual reset but disputed the duration and impact
**Notes:** Stance analysis

## V9-037 (exception_handling)
**Question:** Under what condition would shipping to Nairobi not be a breach of warranty?
**Answer:** If there was no "Stay of Patent" active in that jurisdiction
**Notes:** Conditional counterfactual

## V9-038 (reinsurance_threshold)
**Question:** Does the Zenith claim exceed the 10% insured value notification threshold for GRV?
**Answer:** Yes (USD 38M or even USD 12M exceeds 10% of USD 42M which is 4.2M)
**Notes:** Threshold reasoning

## V9-039 (meta_epistemic)
**Question:** Is there a final determination in the document regarding whether the batch is safe for human use?
**Answer:** No, the document records competing lab findings and a regulatory hold, but no final safety clearance
**Notes:** Document limit analysis

## V9-040 (summary_status)
**Question:** As of Jan 5, 2026, is the reinsurance dispute resolved?
**Answer:** No, it is active ("GRV are disputing this")
**Notes:** Current state of dispute

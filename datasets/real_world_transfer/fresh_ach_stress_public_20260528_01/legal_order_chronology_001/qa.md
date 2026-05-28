# QA — legal_order_chronology_001

All answers are contained entirely within source.md. The order defines its own technical terms (threat actor, credential, exfiltration) in [DEFINITIONS]; no outside knowledge of securities law, the SolarWinds attack, or cybersecurity is required beyond what the order states.

---

**Q1 [direct_fact]** What two categories of conduct does the order find Unisys engaged in?
**A:** (1) Negligently making materially misleading statements regarding cybersecurity risks and events; and (2) violations of disclosure controls and procedures requirements.
**Coords:** [SUMMARY] para 1; para 8

**Q2 [direct_fact]** What civil penalty did the order impose?
**A:** $4,000,000.
**Coords:** [COOPERATION AND SANCTION] para 32

**Q3 [evidence_extraction]** In which filings were the materially misleading cybersecurity disclosures made, and when were they filed?
**A:** In the Form 10-K annual reports for fiscal years ended December 31, 2020 and 2021, filed February 26, 2021 and February 22, 2022 respectively.
**Coords:** [SUMMARY] para 3; [FACTS — MATERIALLY MISLEADING CYBERSECURITY RISK DISCLOSURES] para 19

**Q4 [evidence_extraction]** How did the order characterize the way Unisys described its cybersecurity risks in those 10-Ks?
**A:** As hypothetical — Unisys framed risks from cybersecurity events as hypothetical (e.g., that attacks "could" result in loss) despite knowing actual SolarWinds-related intrusions had occurred, rendering the disclosures materially misleading.
**Coords:** [FACTS — MATERIALLY MISLEADING CYBERSECURITY RISK DISCLOSURES] para 19

**Q5 [competing_cause]** Where does the order say the misleading statements "resulted in part" from?
**A:** From the company's failure to design controls and procedures to ensure that information about potentially material cybersecurity incidents was timely reported and communicated to management to allow timely disclosure decisions.
**Coords:** [SUMMARY] para 4

**Q6 [competing_cause]** What does the order say about the relationship between the pre-December-2022 incident-response policies and the cybersecurity personnel's failure to report?
**A:** The policies did not reasonably require cybersecurity personnel to report information to disclosure decision-makers and contained no criteria for what to report outside the information security organization; "consequently," senior cybersecurity personnel repeatedly failed to report incidents to executive management and the legal department in a timely manner. The order frames the personnel non-reporting as a consequence of the policy gap.
**Coords:** [SUMMARY] para 6

**Q7 [competing_cause]** What operational mistakes did cybersecurity personnel make during the July 2022 extortion event?
**A:** They were not sufficiently familiar with the alert format and erroneously believed the Mimikatz malware was on only one machine and only on July 7; they assigned it low priority because one alert said the malware was quarantined; and no one investigated until July 13, almost a week after the initial alert. They later found the EDR system was misconfigured so it did not automatically send alerts to the centralized SIEM.
**Coords:** [FACTS — 2022 EXTORTION EVENT] para 21; para 24

**Q8 [competing_cause]** What evidence supports the view that the disclosure drafting itself was the problem?
**A:** The 2020 and 2021 10-K risk factors framed known intrusions as hypothetical (para 19) and were substantially unchanged from the pre-breach 2019 10-K language, which had been written before Unisys discovered the SolarWinds-related activity.
**Coords:** [FACTS — MATERIALLY MISLEADING CYBERSECURITY RISK DISCLOSURES] para 19

**Q9 [competing_cause]** What did Unisys's own November 21, 2022 disclosure identify as the locus of the problem?
**A:** A material weakness in its disclosure controls and procedures (and internal control over financial reporting) related to the design and maintenance of effective formal policies and procedures over information being communicated by the IT function and the legal and compliance function to those responsible for governance.
**Coords:** [FACTS — 2022 EXTORTION EVENT] para 25; [SUMMARY] para 7

**Q10 [dates_sequence]** Lay out the chronology of the SolarWinds-related activity and the misleading filings.
**A:** Activity began January/February 2020 and persisted over at least sixteen months; December 2020 Unisys identified the infected SolarWinds Orion software and (Dec 13, 2020) senior cybersecurity personnel received credible information of a broader compromise; January 5, 2021 the government publicly attributed the attack as "likely Russian in origin"; February 26, 2021 Unisys filed the FY2020 10-K with hypothetical-framed risk; April–August 2021 a further intrusion occurred (not reported to senior management); February 22, 2022 Unisys filed the FY2021 10-K, again hypothetical-framed.
**Coords:** [SUMMARY] para 2; [FACTS — SOLARWINDS COMPROMISE-RELATED ACTIVITY] paras 12, 13, 14; [FACTS — MATERIALLY MISLEADING CYBERSECURITY RISK DISCLOSURES] para 19

**Q11 [responsibility_framing]** Does the order treat the cybersecurity personnel's failures as an independent root cause or as a consequence of something else? Support with text.
**A:** Primarily as a consequence. The order states the policies did not require escalation and "consequently" the personnel failed to report (para 6), and that "deficient controls contributed to" the misleading disclosures (para 26). The 2022-event operational mistakes (para 21, 24) are described as personnel errors but in the context of the broader controls deficiency. The order's root attribution is the disclosure-controls design.
**Coords:** [SUMMARY] para 6; [FACTS — FAILURE TO MAINTAIN DISCLOSURE CONTROLS AND PROCEDURES] para 26

**Q12 [sensitivity]** If the statement that the misleading disclosures "resulted in part from the company's failure to design controls" were removed, would responsibility still be best located in the disclosure controls? Use only the document.
**A:** Yes, though more narrowly. Even without that causal-bridge sentence, the order's dedicated disclosure-controls findings (no effective escalation controls; no controls ensuring decision-makers reviewed incident information; deficient controls contributed to the misleading risk factors) and the company's own material-weakness disclosure still locate the problem in the controls. The winner would narrow but not clearly change on that single removal.
**Coords:** [SUMMARY] para 4; [FACTS — FAILURE TO MAINTAIN DISCLOSURE CONTROLS AND PROCEDURES] para 26; [FACTS — 2022 EXTORTION EVENT] para 25

**Q13 [negation]** Did the order find that the threat actor exploited the infected SolarWinds Orion implant on the first identified computer?
**A:** No. The order states Unisys found no evidence that the malicious implant was exploited by the SolarWinds threat actor, and that the third-party service provider did not identify evidence of exploitation, though it recommended further forensic review.
**Coords:** [FACTS — SOLARWINDS COMPROMISE-RELATED ACTIVITY] para 11

**Q14 [premise_check]** Is it correct that Unisys admitted the SEC's findings in agreeing to this order?
**A:** No. Unisys submitted an Offer of Settlement and consented to the order without admitting or denying the findings, except as to the Commission's jurisdiction.
**Coords:** [SETTLEMENT POSTURE]

**Q15 [premise_check]** Is it correct that the order attributes the misleading disclosures solely to the cybersecurity personnel who failed to escalate?
**A:** No. The order attributes the misleading disclosures in part to the company's failure to design adequate disclosure controls, frames the personnel non-reporting as a consequence of the policy gap, and separately faults the disclosure content (framing known intrusions as hypothetical). Responsibility is located principally in the disclosure controls, not solely in the personnel.
**Coords:** [SUMMARY] para 4; para 6; [FACTS — MATERIALLY MISLEADING CYBERSECURITY RISK DISCLOSURES] para 19; [FACTS — FAILURE TO MAINTAIN DISCLOSURE CONTROLS AND PROCEDURES] para 26

# UNIVERSITY LAB SAMPLE CUSTODY AND TEST-RESULT CORRECTION RECORD
**Department of Environmental Chemistry, Lakeshore University**
**Project:** Lower Sammish River PFAS Monitoring Study (LSR-PFAS)
**Project PI:** Dr. Henrike Lentz, Associate Professor
**Lab Director:** Dr. Margaret Hsiao, Director, Trace Analytical Facility
**Lab Manager:** Sam Okeke, M.S.
**Packet date:** May 6, 2026, 16:00 PDT
**Compiled by:** Sam Okeke

## 1. Sample identification

- Sample ID: **LS-PFAS-2026-0428-SR7-A** (parent)
- Site: Sammish River, Mile 3.2 (site designation SR-7)
- Matrix: surface water
- Field collection: April 28, 2026, 14:22 PDT
- Field collector: Tara Mendelssohn, graduate student (LSR-PFAS team)
- Receiving lab: Trace Analytical Facility, Lakeshore University
- Method requested: **EPA Method 1633** (PFAS analytes: PFOA, PFOS, GenX) by liquid chromatography–tandem mass spectrometry (LC-MS/MS).

## 2. Chain of custody (LIMS log)

The Trace Analytical Facility maintains chain of custody in the LIMS (LabWare LIMS v.7.4). The following entries are extracted for sample LS-PFAS-2026-0428-SR7-A.

- April 28, 2026, 14:22 — sample collected, sealed, signed by Mendelssohn, T.
- April 28, 2026, 16:18 — transport to Trace Analytical Facility, signed by Mendelssohn, T.; transport cooler ice-pack temperature confirmed at 4 °C.
- April 29, 2026, 09:12 — sample logged in by Okeke, S.; sample integrity confirmed; transferred to freezer F-3 at 09:18.
- April 30, 2026, 13:45 — split performed at prep bench by Tu, B.; aliquot A prepared for next-day analysis; aliquot B returned to freezer F-3 at 14:02 (per LIMS) for backup retention. Co-witness: Okeke, S. (signed at 14:08).
- May 1, 2026, 09:14 — aliquot A loaded into autosampler queue for run **R-2026-0501-12** by Tu, B.
- May 1, 2026, 14:33 — run completed; aliquot A residue archived to refrigerator R-1.

Aliquot B remains in freezer F-3 as of packet time.

## 3. Freezer F-3 telemetry (HOBO U30 logger #FZ-LOG-03)

Freezer F-3 specification: **-20 °C ± 1 °C**. Logger reports temperature at 5-minute intervals. Excursions outside specification trigger an audit-log entry. The following excursions are recorded between April 28 and May 5, 2026:

- April 29, 2026, 02:14–02:32 — temperature rose to -16 °C (max), duration 18 minutes. Audit note: scheduled auto-defrost cycle.
- May 1, 2026, 03:22–03:49 — temperature rose to -14 °C (max), duration 27 minutes. Audit note: compressor cycling event, no maintenance required.
- **May 4, 2026, 19:48 — May 5, 2026, 06:32 — temperature rose to -8 °C (max), duration 10 hours 44 minutes. Audit note: compressor failure.** Maintenance ticket FAC-2026-0428 opened May 5 at 06:35; compressor relay replaced; freezer returned to specification at 07:48 PDT on May 5.

Manual checks of freezer F-3 logged in the lab notebook:
- May 4, 2026, 11:30 — Okeke, S. — freezer reads -20 °C, no anomalies, content inventory verified per LIMS. Next scheduled manual check was the morning of May 5; the May 4–5 compressor failure preceded that scheduled check.

Door-event timestamps relevant to LS-PFAS-2026-0428-SR7-A:
- April 29, 2026, 09:18 — door opened/closed (sample placement by Okeke).
- April 30, 2026, 14:00 — door opened/closed (aliquot B return).

## 4. Badge access log (HID prox card, prep room and freezer alcove)

- April 30, 2026, 13:42 — Tu, B. — prep room entry.
- April 30, 2026, 14:01 — Tu, B. — prep room exit.
- April 30, 2026, 14:01 — Tu, B. — freezer alcove entry.
- April 30, 2026, 14:04 — Tu, B. — freezer alcove exit.
- April 30, 2026, 14:08 — Okeke, S. — prep room entry (co-witness signature).

## 5. Bench notebook entry — Brendan Tu, April 30, 2026

"Pulled LS-PFAS-2026-0428-SR7-A from F-3 at 13:35. Split at 13:45 into A (50 mL, for analysis) and B (50 mL, archive). Used standard amber LC vials, caps from current stock. A loaded into autosampler tray for next-day batch. B labeled and returned to F-3. **Did not record specific cap lot** — both lots LCV-2026-031 and LCV-2026-029 were in active use this week. Co-witness Okeke signed at 14:08."

## 6. Instrument run log — Q-Exactive #INST-04, run R-2026-0501-12

- Run started May 1, 2026, 09:14 PDT.
- Run completed May 1, 2026, 14:33 PDT.
- Operator: Tu, B.
- Method file: PFAS_M1633_v3.mth
- Calibration curve: solution lot **CS-2026-04**, 9-point curve, r² = 0.9994.
- System suitability QC: PASS (PFOA-13C8 retention time within ±0.1 min of spec; mass accuracy < 5 ppm; tailing factor < 1.5).
- Internal standard recovery (PFOA-13C8) for sample LS-PFAS-2026-0428-SR7-A aliquot A: **87%**.
- Per EPA Method 1633, acceptable internal standard recovery range is **50–150%**. The 87% value is within acceptance.

## 7. Initial report — version 1.0

Issued May 2, 2026, 17:18 PDT, by Tu, B.; reviewed by Hsiao, M.; signed by Lentz, H.

| Analyte | Result (ng/L) |
|---------|---------------|
| PFOA    | 142 |
| PFOS    | 89  |
| GenX    | 12  |

Reporting limit per analyte: 5 ng/L. Sample-specific QC: PASS.

## 8. Calibration curve reprocessing memo — May 5, 2026

Filed by Hsiao, M., 11:14 PDT, May 5, 2026.

"Routine post-run review of calibration solution lot **CS-2026-04** identified that the certified reference concentration of internal standard PFOA-13C8 in the calibration solution was reported by the supplier as 1.000 ng/mL but corrected by the supplier on May 4, 2026 to 0.847 ng/mL. The supplier has issued a Certificate of Analysis revision (**COA-2026-04R**). Reprocessing the May 1, 2026 run with the corrected certified value yields a revised PFOA result for sample LS-PFAS-2026-0428-SR7-A of **168 ng/L**. PFOS and GenX values are unchanged because their respective internal standards were unaffected by the COA revision. The corrected PFOA value of 168 ng/L supersedes the initial value of 142 ng/L."

## 9. Corrected report — version 1.1 (erratum)

Issued May 5, 2026, 13:42 PDT, by Hsiao, M.; signed by Lentz, H.

| Analyte | Result (ng/L) | Status |
|---------|---------------|--------|
| PFOA    | **168**       | corrected by erratum |
| PFOS    | 89            | unchanged |
| GenX    | 12            | unchanged |

Per laboratory SOP **TAF-SOP-RPT-02 §5.3**, when an erratum is issued, the corrected report is the report of record for the sample; prior versions are retained for audit but are not the report of record.

## 10. Vial cap manufacturer memo — Acme Vial Co., received May 5, 2026

Email from Acme Vial Co. quality assurance, received at the lab May 5, 2026, 08:55 PDT:

"Notification: Lot **LCV-2026-031** of LC vial caps may have residual fluorinated mold release agent that could contribute background PFAS signal in trace analysis at sub-ng/L levels. Internal investigation ongoing; precautionary advisory issued to all customers receiving this lot. Lot LCV-2026-031 was shipped to your facility on April 21, 2026."

Lab inventory records show two cap lots in use during April 25 – May 1, 2026: **LCV-2026-031** (advisory) and **LCV-2026-029** (no advisory). Tu's bench notebook for the April 30 split does not specify which cap lot was used for either aliquot.

## 11. Personnel substitution

Brendan Tu was at the Pacific Coast Mass Spectrometry Conference May 3–4, 2026. During his absence, **Priya Chatterjee, M.S.**, covered routine lab operations. Chatterjee did not handle LS-PFAS-2026-0428-SR7-A or its aliquots, and her shift coverage does not appear in this sample's chain of custody.

## 12. Contamination review status

Following the May 5 vial cap advisory, Lab Director Dr. Margaret Hsiao has scheduled a formal contamination review for **May 8, 2026, 10:00 PDT**. The review will address two questions:

1. Whether sample LS-PFAS-2026-0428-SR7-A aliquot A was vialed using cap lot LCV-2026-031 or LCV-2026-029. The lab cannot determine this from existing records; supplier shipment-tracing data has been requested but not yet received.
2. Whether aliquot B (still in freezer F-3) is compromised by the May 4–5 compressor failure. Per the freezer specification of -20 °C ± 1 °C, sustained operation at -8 °C for 10 hours 44 minutes is outside specification. PFAS analytes are generally thermally stable at these temperatures, but laboratory acceptance criteria for archived aliquots require a documented determination by the Lab Director.

As of packet time (May 6, 16:00 PDT), **no determination has been issued on either question.**

## 13. Withdrawn pre-analysis quote

A pre-analysis quote, **TAF-Q-2026-04-019**, prepared on April 22, 2026 by Okeke for the LSR-PFAS team, listed PFNA as an additional analyte. The quote was withdrawn on April 24, 2026, before the sample was collected, when the LSR-PFAS team confirmed PFNA was outside the project's analyte list. The withdrawn quote is retained for procurement records and does not authorize any analyte beyond PFOA, PFOS, and GenX.

## 14. Open / unresolved items

1. Cap lot identification for aliquot A — pending Acme Vial Co. shipment-tracing data.
2. Aliquot B integrity following freezer failure — pending Hsiao determination at May 8 review.
3. Whether to re-run aliquot A using a confirmed lot LCV-2026-029 cap, contingent on the May 8 determination.

— End of packet body. Compiled and certified by Sam Okeke, Lab Manager.


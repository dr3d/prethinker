# Expected Failure Modes — lease_amendment_status_register

## Likely model and harness failure modes

**LOI-as-binding drift.** TLOI-2026-019 contains substantive terms (extension, rent escalation, ROFR) that mirror the proposed amendment. A model that ingests the LOI's body without integrating the non-binding footer will report the LOI's terms as committed obligations, contradicting the explicit non-binding declaration.

**Clerk-note-as-binding drift.** CN-2026-022 states that PA-2026-014-D1 has no legal effect. A model could either (a) ingest the note as evidence that the draft IS legally operative (misreading the note's negative claim) or (b) ingest the note as a Register decision rather than an advisory administrative statement. Both are wrong.

**Counsel-opinion-as-ruling.** COP-2026-031 is an outside-counsel opinion to one party (Bridgemarrow). It is advisory and not a judicial ruling. A model that treats counsel's opinion as binding determinations will misattribute authority.

**ROFR unit stale-snapshot.** Three documents reference the ROFR unit: PA-2026-014-D1 (Unit 4C), PA-2026-014-D2 (Unit 4C), and the initial register entry REG-E-2026-061 (Unit 4C). Only the executed amendment AMD-2026-014 (page 7) and the corrected register entry REG-E-2026-061-R record the operative Unit 4D. A model relying on text frequency will likely report Unit 4C as the current ROFR; the correct answer is Unit 4D, established by the executed amendment and confirmed by the register correction.

**Amendment-chain conflation.** The draft → revised-draft → executed-amendment chain has three distinct documents with similar identifiers (PA-2026-014-D1, PA-2026-014-D2, AMD-2026-014). Models that conflate the identifiers will misattribute terms or report the wrong document as operative.

**Void-notice misattribution.** VD-2026-003 voids PA-2026-014-D1 specifically. It does NOT void PA-2026-014-D2 (which was already superseded by execution). Models that treat the void notice as voiding the entire amendment chain will misreport.

**Rent-effective-date error.** The amendment language says rent escalates on the later of April 1, 2026 or the execution date. Execution occurred April 7, 2026. Therefore rent effective date is April 7, 2026. Models that report April 1, 2026 (the earlier candidate) will fail.

**Term-end miscalculation.** Original lease ended March 30, 2029. Amendment adds 2 years → March 30, 2031. Models that compute "5 + 2 = 7 years from March 31, 2024" might report March 30, 2031 correctly, but models that compute from the execution date will get April 6, 2031 or similar, which is wrong.

**Row label and document identifier collapse.** Each row has BOTH a row label (e.g., ROW-AMD-003) AND a document identifier (e.g., AMD-2026-014). The fixture deliberately separates these, and questions probe both. Models that flatten "row label = document id" will fail half of these questions.

**State-vocabulary flattening.** The fixture uses many distinct status terms: EFFECTIVE, SUPERSEDED, SUPERSEDED BY EXECUTION, SUPERSEDED BY CORRECTION, OPERATIVE, CURRENT, ADVISORY, NON-BINDING, VOID. Models that flatten these to a binary active/inactive distinction will fail status-precision queries.

**Harness-level failure: the QA prompt may inject the LOI's substantive body into source-attributed-claim questions, causing the model to attribute Quillvale with binding commitments. The fixture is structured so that the LOI's non-binding footer is presented in the same section as the LOI body, and the LOI's row entry expressly carries a NON-BINDING status, making this a detectable leak.**

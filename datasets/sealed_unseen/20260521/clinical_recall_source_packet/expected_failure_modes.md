# Expected Failure Modes — clinical_recall_source_packet

## Likely model and harness failure modes

**Wrapper-collapsed inventory.** The inventory table contains fourteen rows of nearly identical structure (serial, lot, room, status). A naive extractor will compile a single wrapper template ("all units on hold") instead of fourteen distinct addressable rows. Subsequent queries about a specific serial's room, or a specific row's lot, will then fail or return ambiguous answers.

**Stale lot-0521 status.** The packet narrates lot 0521 as initially on hold and then released. An extractor that locks onto the §2 inventory table without integrating the §5 internal correction will report all lot-0521 units as on hold, missing the supersession.

**Bulletin-chain confusion.** Two manufacturer bulletins exist — primary (SBI-FB-2026-114) and supplemental (SBI-FB-2026-114-S1). A model that treats them as redundant statements rather than as a chain with supersession will produce contradictory or duplicative answers about lot 0521.

**Trumbauer-overrides-Indaharu drift.** The BMET's note expressly reframes Indaharu's negative observation as "not excluding latent firmware vulnerability." A model that lets the BMET's opinion silently displace Indaharu's primary source claim will fail to return Indaharu's actual report ("no anomalies observed") when asked.

**Authority misattribution.** The operative authority for what is recalled is the manufacturer bulletin chain; the operative authority for what is on hold in inventory is the WAIC internal correction notice. A model that conflates these — for instance, claiming Trumbauer's note or Drabolwicz's correction is the source of the lot-0521 non-affected determination — will misattribute.

**Quantity arithmetic across correction.** Counts must be derived from the correction-applied state: 9 on hold (6 + 3), 5 released (lot 0521), 14 total. A model that uses the pre-correction state will report 14 on hold and 0 released.

**Room-vs-floor confusion.** The packet uses both room ids (e.g., 3B-188) and floor labels (e.g., floor 3B). A model that flattens these may mis-locate a unit or misreport loaner deployment counts (4 on 2A, 2 on 3B).

**Identifier paraphrase.** Compact identifiers (TQ9-S/N-A8104, ROW-INV-007, WAIC-CORR-2026-0411) must be returned verbatim. Models that paraphrase ("pump A8104," "row seven," "the April 11 correction") will fail identifier-detail queries.

**Time precision loss.** Bibulwicz's report timestamps the alarm at 03:14 on April 3, 2026. Loss of either the date or the time of day is a precision-loss failure; some models will return only the date or only the time.

**Harness-level failure: the QA prompt may inject the §5 correction text into the source-attributed-claim window, causing the model to attribute the operative supersession to the nurses. The fixture is structured so that all nurse reports precede the correction notice in the document, making this a detectable harness leak.**

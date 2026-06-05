# GAO Bid-Protest Decision Wrapper Oracle — Review Notes

Predicate: `gao_bid_protest_decision(DecisionId, ForumId, DocketId, ProcurementId, DecisionDate, DecisionStatus, SourceOrScope).`
Posture: source-only, independent. Did not use compile output, bootstrap JSON, worksheets, or model answers. The proposal's positive examples are neutral variable shapes and were not used to set any value.

## Result

Both sources support exactly one clean wrapper row. Status: **complete** (no stop condition).

| Fixture | Decision | Forum | Docket | Procurement | Date | Status |
| --- | --- | --- | --- | --- | --- | --- |
| ugly_002 | gao_b_423689 | gao | b_423689 | rfq_9531bp25q0010 | v_2025_11_13 | sustained |
| ugly_003 | gao_b_423552_3 | gao | b_423552_3 | rfp_w912hp25r1000 | v_2026_03_24 | denied |

## ugly_002 (Castro & Company, B-423689) — slot basis

- ForumId `gao`: caption "U.S. Government Accountability Office, Office of the Comptroller General."
- DocketId `b_423689`: "File: B-423689."
- ProcurementId `rfq_9531bp25q0010`: "request for quotations (RFQ) No. 9531BP25Q0010." Footnote 1 records the RFQ/RFP nomenclature dispute and GAO's election to call it an RFQ; the identifier itself is unambiguous.
- DecisionDate `v_2025_11_13`: "Date: November 13, 2025."
- DecisionStatus `sustained`: DECISION "We sustain the protest"; RECOMMENDATION "The protest is sustained"; all three DIGEST grounds (OCI, technical evaluation, tradeoff) sustained. Not `sustained_in_part`.

## ugly_003 (Enviremedial Services, B-423552.3) — slot basis

- ForumId `gao`: "U.S. Government Accountability Office (GAO), Office of the General Counsel."
- DocketId `b_423552_3`: "File: B-423552.3." Distinct from the prior protest filings B-423552 and B-423552.2 (the Aug 28, 2025 decision); conflating them is forbidden.
- ProcurementId `rfp_w912hp25r1000`: "request for proposals (RFP) No. W912HP25R1000."
- DecisionDate `v_2026_03_24`: "Date: March 24, 2026." Distinct from the prior decision (Aug 28, 2025) and the current filing date (Dec 17, 2025).
- DecisionStatus `denied`: HIGHLIGHTS "We deny the protest"; CONCLUSION "The protest is denied."

### The one genuinely hard call (003 status)

DIGEST item 1 is "dismissed as untimely" (the CBFS-subcontractor relevancy ground), while items 2 and 3 are denied on the merits. The closed domain has no combined denied/dismissed value, and GAO's own bottom line states a single disposition: "The protest is denied." The wrapper captures the document's stated overall disposition, so `denied` is correct. The per-ground dismissal is a finding-level detail outside this wrapper carrier. Accordingly `dismissed` (whole protest), `denied_in_part` (a phrasing GAO did not use), and `sustained_in_part` (the prior B-423552/.2 outcome) are all forbidden.

## Forbidden boundaries exercised (both fixtures)

Inferred/wrong disposition (`denied` on 002; `dismissed`/`denied_in_part`/`sustained_in_part` on 003); prior-decision conflation (docket B-423552 / B-423552.2 and the sustained_in_part status on 003); cited-precedent B-number used as docket (B-412870.2 on 002); file number reused as procurement id (002); wrong dates (solicitation-issue date on 002; prior-decision date on 003); and OCI/recommendation/CPAR/tradeoff-finding prose forced into the ProcurementId, DecisionStatus, or SourceOrScope slots.

## Carrier observations (for the owner, not part of the oracle)

- The closed `ForumId`/`DecisionStatus` domains held for both unlike decisions: an outright **sustained** OCI/documentation case and a **denied** post-corrective-action follow-up. The wrapper cleanly separated a fresh decision (003, denied) from the prior partial-sustain it references (sustained_in_part), which is the main forbidden boundary on 003.
- One structural limit surfaced, not a defect here: a GAO decision that both dismisses some grounds and denies/sustains others has no single combined closed value. Both 002 (clean sustain) and 003 (overall denied) were representable because each had an explicit single bottom-line, but a future "denied in part and dismissed in part" decision would force `not_stated` or a domain extension. Worth noting before the unlike-transfer gate.

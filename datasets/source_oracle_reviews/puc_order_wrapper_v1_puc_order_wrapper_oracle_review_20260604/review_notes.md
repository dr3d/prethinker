# PUC Order Wrapper Oracle — Review Notes

Predicate: `puc_order(OrderId, AgencyId, DocketId, OrderKind, IssuedDate, DecisionStatus, SourceOrScope).`
Posture: source-only, independent. Did not use compile output, bootstrap JSON, worksheets, or model answers. The proposal's positive examples were checked against the source and kept only because they are source-correct.

## Result

Both sources support exactly one clean wrapper row. Status: **complete** (no stop condition).

| Fixture | Order | Agency | Docket | Kind | Issued | Status |
| --- | --- | --- | --- | --- | --- | --- |
| ugly_002 | cpuc_alj_445 | cpuc | h_22_07_010 | resolution | v_2023_10_16 | approves_settlement |
| ugly_003 | utah_psc_24_035_04_omd | utah_psc | docket_24_035_04 | order_memorializing_decision | v_2025_06_24 | memorializes_decision |

## ugly_002 (CPUC Resolution ALJ-445) — slot basis

- OrderKind `resolution`: titled "RESOLUTION ALJ-445". 
- DecisionStatus `approves_settlement`: Summary "grants the Joint Motion ... for Approval of Settlement Agreement"; Order para 1 "is granted, and the Settlement Agreement approved herein".
- IssuedDate `v_2023_10_16`: "Date of Issuance: 10/16/2023" (distinct from the 10/12/2023 conference/adoption date — that conflation is forbidden).
- DocketId `h_22_07_010`: "Request for Hearing (H.) 22-07-010". OrderId `cpuc_alj_445`: "Resolution ALJ-445". (Genuine but resolvable ambiguity: ALJ-445 is the order identifier, H.22-07-010 the proceeding identifier; the split is source-grounded, and swapping them is forbidden.)

## ugly_003 (Utah PSC Order Memorializing Decision) — slot basis

- OrderKind `order_memorializing_decision`: titled "ORDER MEMORIALIZING DECISION".
- DecisionStatus `memorializes_decision`: Order "this order memorializes the PSC's approval of the Settlement". The substantive approval occurred at the Dec 16, 2024 hearing and was to be memorialized in the final order; the April 25, 2025 order omitted it; this June 24, 2025 order corrects that omission. Therefore the instrument's disposition is memorialization, not a fresh approval — `approves_settlement` is forbidden as a conflation.
- IssuedDate `v_2025_06_24`: "ISSUED: June 24, 2025" (distinct from the April 25, 2025 prior order — that conflation is forbidden).
- DocketId `docket_24_035_04`: "DOCKET NO. 24-035-04" (distinct from doc-control DW#340357 — that conflation is forbidden).
- Not `final_order`: the final order was the April 25, 2025 order; this is the memorializing correction.

## Forbidden boundaries exercised (both fixtures)

Prose-shaped OrderKind (full caption) and DecisionStatus (settlement-finding sentence); inferred/wrong legal status (`denies_request` on 002, `approves_settlement` on 003); conflated/swapped identifiers (M-4846 authority and id-swap on 002; DW#340357 on 003); conflated dates (conference date 002; prior-order date 003); wrong closed kind (`final_order` on 003); and settlement/ordering-paragraph, commissioner-vote, and certificate-of-service prose forced into wrapper slots.

## Carrier observations (for the owner, not part of the oracle)

- The closed value domains were sufficient for both unlike instruments: a California enforcement **resolution** approving a settlement, and a Utah **order memorializing decision**. `approves_settlement` vs `memorializes_decision` cleanly separated the two even though both concern an approved settlement — a useful sign the status domain is carrying real distinctions rather than collapsing.
- The hardest real call was 003's status: the document both *recites* a past approval and *is* a memorialization. Anchoring DecisionStatus to what the instrument itself does (memorialize) rather than what it recites (approval) is the defensible rule and is the main forbidden boundary on 003.

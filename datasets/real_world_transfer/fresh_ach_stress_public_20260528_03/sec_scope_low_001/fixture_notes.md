# fixture_notes — sec_scope_low_001

## Why this source was chosen
A short, self-contained SEC Form 8-K/A restating a SPAC's audited balance sheet. It cleanly separates the cause of an action (why the company restated) from the scope/consequence of that action (no impact on cash), and the cause is supported by several independent rows — exactly the structure for a low-sensitivity causal fixture with a tempting off-axis scope hypothesis. It is fresh public-record material (a different filer and document type from the prior batch's restatement fixture).

## Why the ACH sensitivity target is low
The reason for the restatement is over-determined. Three independent accounting-classification errors are each sufficient to require correction: warrants recorded in equity rather than as a liability (e1), Class A redeemable shares not stated at full redemption value (e2), and the underwriters' over-allotment option not classified as a liability (e3). On top of these, the audit committee's non-reliance conclusion (e4) and the SEC-staff-guidance trigger (e5) independently support the causal read. Removing any single row leaves the read intact, so there should be no sensitivity rows.

## The tempting wrong / off-axis hypothesis
"No impact on cash / non-cash" (h2). This is true and prominently stated (e6), and a reader could grab it as "the explanation." But it answers a different question — the consequence/scope of the restatement, not why the company restated. It is the batch's off-axis-true hypothesis for this fixture. A second tempting-but-wrong reading is h4 (a material weakness drove the restatement); the document states the opposite causal order — the material weakness was concluded "in light of the errors" (e7).

## Direct / partial / off-axis rows
- Direct to h1 (causal): e1, e2, e3 (the three classification errors), e4 (audit-committee conclusion), e5 (staff-guidance trigger).
- Off-axis to h2 (scope/consequence): e6 (no cash impact), e8 (amendment limited in scope).
- Against h3 (fraud/enforcement): e5 (trigger was guidance, not enforcement).
- Against h4 (control-weakness-as-cause): e7 (errors preceded and produced the material-weakness conclusion).

## Double-edged rows
- e8 (the amendment changes nothing else) reinforces the off-axis "narrow scope" reading (h2) while also confirming the restatement was a targeted error correction (mildly supportive of h1). It should not be treated as a sensitivity row.
- e5 does double duty: it supports the causal read (h1) and simultaneously forecloses the fraud/enforcement reading (h3).

## Extraction quirks
- The filing contains several "untagged table" cover-page artifacts in the raw HTML; these are cover boilerplate and are omitted from source.md while all substantive text is preserved verbatim.
- One sentence is internally awkward ("Class A shares subject to redemption were originally recorded at the correct full redemption value" followed by a description of subsequent mis-restatement and re-correction); it is preserved verbatim because the causal chain matters and should not be smoothed over.
- Accounting citations (ASC 480 and ASC 480-10-S99) are load-bearing for distinguishing the three drivers and are preserved exactly.

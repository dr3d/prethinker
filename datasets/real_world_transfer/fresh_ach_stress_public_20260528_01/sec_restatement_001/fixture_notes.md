# fixture_notes — sec_restatement_001

## Why this document is a good ACH stress test

This fixture is the deliberate **low-sensitivity, robust-winner** counterpart to the balanced NTSB fixture. Together the two form the batch's sensitivity discrimination pair: the NTSB report flips its winner when a single evidence row is removed, while this 8-K does not. An ACH engine that reports the same sensitivity for both — or that cannot tell a flip case from a no-flip case — is not actually measuring sensitivity.

## The competing explanations are all genuinely present in the source

A reader of this 8-K can land on three different stories about why the restatement was necessary:

- **Material weakness in ICFR (h1).** The Company attributes the intersegment-sales errors to a material weakness in internal control over financial reporting, found additional errors while testing its remediation controls, and is still remediating the weakness.
- **Contained segment-disclosure reclassification (h2).** The restatement affects only the segment-information footnotes and is "not expected to result in any material impact" on the consolidated earnings, balance sheet, or cash-flow statements — arguably a presentation matter rather than a substantive misstatement.
- **SEC-staff-dialogue-driven change (h3).** The Board's conclusion came "following the Company's ongoing dialogue with the staff of the" SEC, which a reader could treat as the real driver.

## How the document adjudicates among them

The through-line is the control weakness. It is established three independent times: identified in connection with the original error corrections, surfaced again through remediation-control testing, and still open under active remediation. The no-material-impact statement (h2) bounds the *consequence* of the errors but not their *cause*; the SEC-dialogue reference (h3) fixes the *timing* of the Board's conclusion but does not identify the cause of the underlying errors. So h1 is the best explanation for why a restatement was needed.

## Why sensitivity is low (and not zero)

- h1 is anchored by three redundant rows (e1, e2, e3). Removing any one leaves the material weakness established by the other two — so no single-row removal flips the winner.
- h2's only affirmative anchor is the no-material-impact row (e4). Removing it does not flip the winner; it strengthens h1.
- h3's only affirmative anchor is the SEC-dialogue row (e6). Removing it eliminates h3 without disturbing h1.

There is still *some* sensitivity — the margins between hypotheses move as e4 or e6 are added or removed, which is why this is "low" rather than literally zero. The correct ACH read names h1 as the robust winner, reports low sensitivity, and does not hallucinate a flip.

## Source-containment

Every fact needed is in source.md. The accounting terms that matter are defined in context by the filing itself: intersegment vs intrasegment sales ("sales from one segment to the other" vs "sales within the segment"), material weakness (tied explicitly to "accounting practices and procedures for intersegment sales"), and the list of consolidated statements said to be unaffected. No outside knowledge of SEC Item 4.02 mechanics, ASC segment-reporting rules, or the company's broader history is required to answer the QA or run the ACH. Cover-page checkbox boilerplate and the full forward-looking-statements paragraph are summarized rather than reproduced because they contain no facts load-bearing for any answer.

## Real-document messiness preserved

- A single fact pointing two ways: the intrasegment-vs-intersegment classification (e5) supports the "contained reclassification" reading on its face, yet its recurrence across periods and segments supports the control-weakness reading.
- A discovery context (errors found while testing remediation controls) that can be spun as reassuring (detection improving) or damning (weakness not yet fixed) — the document supplies both readings without resolving the spin.
- A regulator reference that establishes involvement and timing without assigning cause, tempting a reader to over-attribute the restatement to the SEC.

# fixture_notes — fda_warning_letter_001

## Why this document is a good ACH stress test

The brief asks for an FDA enforcement document where responsibility could be framed four ways — process failure, documentation failure, quality-system failure, or vendor/supplier failure. This letter contains all four readings within the source, and — importantly — the document itself takes a position and explicitly forecloses two of the four. That makes it a **robust-winner** counterpart to the balanced NTSB fixture: it tests whether an ACH routine correctly reports that the winner does NOT flip under single-row removal, rather than manufacturing false sensitivity.

## The four framings, all present in the source

- **Vendor/supplier (h1).** The adulteration genuinely originated at the CMO, Brassica: poor aseptic practice, fabricated microbiology records, dirty gowning. A reader could stop there and blame the supplier.
- **Quality-system (h2).** The only violation cited against the recipient is a quality-control-unit failure under 21 CFR 211.22(a): inadequate supplier-qualification procedures, no CMO-disqualification process, other CMOs not assessed.
- **Process/decision-execution (h3).** Two concrete decisions: qualifying Brassica in 2020 despite known deficiencies, and requalifying in 2023 without checking corrective actions.
- **Documentation (h4).** Touched by "failure to maintain raw testing data" (a Brassica deficiency) and the recipient's proposed reliance on certificate-of-analysis comparison.

## How the document adjudicates among them

- It **forecloses h1 as an excuse**: "FDA regards contractors as extensions of the manufacturer" and "You are responsible for the quality of your drugs regardless of agreements."
- It **rejects h4 explicitly**: "Comparing a COA from a CMO to pre-approved specifications does not overcome your responsibility to evaluate, qualify, audit, and monitor your contract manufacturers."
- It **subsumes h3 into h2**: the specific 2020/2023 decisions are cited as instances of an inadequate quality-control unit and inadequate supplier-qualification procedures, with the systemic-gap language ("lacks a process for disqualifying CMOs," "did not propose evaluating the qualification status of your other CMOs") generalizing beyond Brassica.

The best-supported reading is therefore h2 (quality-system failure), matching the cited regulation.

## Why sensitivity is medium, not high or zero

This fixture is deliberately the opposite stress case from the balanced one. The winner (h2) is anchored by multiple independent rows (e2, e3, e8), and the two losing-but-tempting framings (h1, h4) are each knocked down by their own dedicated rows (e7, e6). So:

- Removing any single row does **not** flip the winner to h1 or h4.
- The only genuinely live competition is h2 vs h3 (system vs specific decisions), and both keep responsibility with the recipient. Removing the systemic-gap row (e8) is what most narrows the h2-over-h3 margin — hence medium, not low.

A correct ACH read should report medium sensitivity, identify e2 as the load-bearing citation, and explicitly note that h1 and h4 cannot win on this evidence. An engine that reports this fixture as a coin-flip among all four framings is over-stating sensitivity; one that cannot articulate why h1/h4 are foreclosed is under-reading the document.

## Source-containment

Every fact needed is in source.md. Where a regulation is cited (21 CFR 211.22(a)), the letter states what it requires (an adequate quality control unit with authority to approve/reject and to review records). No outside knowledge of CGMP, the FD&C Act sections, or FDA enforcement practice is required to answer the QA or run the ACH; the redaction markers "(b)(4)" are preserved exactly as the FDA published them and are not load-bearing for any answer.

# Anti-Leakage Manifest — estate_archive_access_dispute

> Purpose: certify that source.md and qa.md do not contain answer keys, and explain how oracle.jsonl was constructed without leaking back into source.md.

## Leakage checks performed

1. **No oracle text appears verbatim in qa.md.** Questions probe lookup, version selection, possession-vs-ownership distinction, and unresolved-determination preservation.
2. **No "answer:" or "the correct answer is" markers appear in source.md.** The source is a probate court packet with embedded exhibits, deed excerpts, codicil quotation, and counsel memos.
3. **The two-layer supersession chain is laid out in source as separate sections (§3 retention, §4 transfer, §6 codicil).** Q18 / Q38 require the parser to compose across all three.
4. **The current-possession vs legal-ownership distinction is signaled in source by the catalog status note's explicit phrasing ("physical removal restricted pending probate court determination").** Q39 requires the parser to invoke this distinction; the oracle restates it concisely.
5. **The April 2024 Calverley withdrawal is flagged in source as "unrelated to the Crimson Notebooks dispute."** This is a deliberate non-leakage: it provides a withdrawn-authorization row shape but no question asks the parser to invoke it as governing.
6. **The Theodore Marchetti / Sophia Hennessy-Marchetti name overlap is signaled in source with explicit "no relation" disclaimer.** No question requires the parser to recognize this as a non-issue, but the trap is in source for parser-confusion probing.
7. **Pending vs decided is named in source as "no determinations have been issued by the court on any disputed question."** The oracle restates this without predicting outcomes.
8. **The PH-2020-067 vs 2019 intake apparent conflict is left unresolved in source.** Source provides the Schedule A retention information in §3 and the photograph in §5, but does not pre-state "the photo is consistent with the intake list because of Schedule A retention." Q40 requires the parser to compose the resolution.
9. **The number of photographs (three) is not pre-tallied in source.** Source enumerates PH-2018-114, PH-2020-067, and PH-2022-181 in §5; Q30 requires the parser to count.
10. **The codicil's beneficiary list (three children) is stated in the codicil quotation in §6.** Q32 is direct lookup of the count from the quoted text.
11. **The 2022 deed's three transferred items are enumerated in source §4.** Q31 is direct lookup of the count.
12. **The legal theories (completed inter vivos gift; reservation of access making gift conditional) are stated in source's quoted memo paraphrases.** Q26 / Q27 are direct lookup of the named theories. The application of these theories to facts is the disputed question, which the source explicitly does not resolve.

## Self-flagged design choices

- The "no relation" disclaimer for Theodore Marchetti vs Sophia Hennessy-Marchetti is a deliberate identity-collision trap. No question asks about this directly. If your parser ever emits a "potential conflict of interest" claim that depends on this identity, that's a hallucination signal worth logging.
- The Calverley withdrawal is included as procedural context for the access framework but is unrelated to the central dispute. No question requires invoking it. If your parser ever invokes Calverley as relevant to ownership, that's a contamination signal.
- Q40's "yes, they are consistent" answer requires the parser to follow the retention mechanism through three sources (Schedule A, the 2019 intake list, and PH-2020-067). The harder version of this question would force the parser to identify the *resolution mechanism* (Schedule A retention) by name; the current phrasing accepts a description of the mechanism.

## What is in source vs oracle

- **source.md** contains: estate summary, archive description, two deeds of gift with intake receipts, three photographs, October 2024 codicil with operative language, withdrawn September 2024 draft, capacity question briefs, withdrawn researcher authorization (procedural reference), estate inventory and Hartwell catalog status, three counsel memos, scheduling order, date-event anchors, open items.
- **qa.md** contains: 40 numbered questions, no answers.
- **oracle.jsonl** contains: 40 reference answers with category tags.
- **strategy.md** contains: design rationale. NOT compile context.
- **anti_leakage_manifest.md** (this file) contains: leakage certification. NOT compile context.

## Categories present and counts

- direct_lookup: 8 (q001–q008)
- provenance: 6 (q009–q014)
- supersession: 5 (q015–q019)
- status_at_time: 5 (q020–q024)
- rule_application: 5 (q025–q029)
- count: 4 (q030–q033)
- unresolved: 4 (q034–q037)
- cross_source_conflict: 3 (q038–q040)

Total: 40.


# Anti-Leakage Manifest — arts_grant_panel_reconsideration

> Purpose: certify that source.md and qa.md do not contain answer keys, and explain how oracle.jsonl was constructed without leaking back into source.md.

## Leakage checks performed

1. **No oracle text appears verbatim in qa.md.** Questions probe lookup, version selection, conjunction enumeration, conditional reasoning, and absence-of-record.
2. **No "answer:" or "the correct answer is" markers appear in source.md.** The source is an institutional docket packet with embedded counsel notes and bylaw citations.
3. **The §IV.B.3 procedural-vs-decisional distinction is stated as a counsel note in source, not as the answer to any specific question.** Q19 / Q40 require the parser to invoke the counsel note's own qualifier ("does not adjudicate the underlying funding question").
4. **The Tovar-recusal recomputed average (75.25) is shown in source as a worked example in §9.** This is a leakage risk for Q32; I included it in source as an institutional disclosure of the recusal scenario, but the manifest flags this. If you'd rather force a true derivation, strip the worked example from §9 and the question becomes harder.
5. **The corrected average of 75.4 is shown explicitly in §6.1 of source.** Q15 is therefore a direct lookup question rather than an arithmetic derivation. If you'd rather force the parser to compute, strip the average line from §6.1.
6. **The 19-fellowship count is stated in source §10.** Q31 is therefore direct lookup. Source uses the parenthetical "19 × $25,000 = $475,000," which leaks the count. Acceptable for direct-lookup design; flagged for awareness.
7. **The fiscal ledger remaining-balance ($25,000) is stated explicitly in §10.** Q22 is direct lookup.
8. **Pending-vs-decided is named in source as "has not issued a determination" and "scheduled… not yet held."** The oracle restates these concisely.
9. **The withdrawn March 27 tentative list is included with explicit "is retained for archival purposes only and does not constitute a funding decision" framing.** No question asks about that list directly, but the trap remains in source for parser-contamination probing.
10. **Counsel's funding-order rule is stated as a quoted note in source §11.** Q27 / Q39 / Q36 require the parser to apply that rule rather than recapitulate it. The order ("highest first") is in source; the application of that order to the specific Okafor-Vance vs Fontaine pair (Fontaine first) is in the oracle only.

## Self-flagged design choices

- Source contains the corrected average (75.4) and the recusal-scenario recomputed average (75.25) as worked examples. This makes Q15 and Q32 closer to direct lookup than to derivation. If you want to harden the fixture, regenerate without these worked examples.
- The oracle answer for Q36 is intentionally a multi-clause conditional. If you'd rather have a flat "not determined," I can simplify.

## What is in source vs oracle

- **source.md** contains: cycle context, panel composition, original panel meeting and score sheet, rejection letters, reconsideration request, score correction audit memo, corrected score sheet, two counsel notes, Tovar conflict question, recusal scenario worked example, fiscal ledger, date-event anchors, withdrawn tentative list, open items.
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


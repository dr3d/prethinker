# Anti-Leakage Manifest — municipal_tree_permit_amendment

> Purpose: certify that source.md and qa.md do not contain answer keys, and explain how oracle.jsonl was constructed without leaking back into source.md.

## Leakage checks performed

1. **No oracle text appears verbatim in qa.md.** Questions probe lookup, version selection, conjunction enumeration, conditional reasoning, and absence-of-record.
2. **No "answer:" or "the correct answer is" markers appear in source.md.** The source is an institutional permit packet with embedded exhibits, ordinance citations, and a solicitor memo.
3. **The "filed vs issued" distinction is signaled in source as an institutional fact (filing on April 18, issuance on April 25, effective immediately upon issuance).** Q20 / Q24 require the parser to apply this distinction without source pre-stating "the operative permit on April 21 was the original."
4. **The two qualifying clauses for tree #19's protection are stated separately in source.** Q29 requires the parser to recognize both §18-12(b)(i) and §18-12(b)(ii) as independently sufficient. The source narrates this as "and independently under §18-12(b)(i)" but does not pre-state "tree #19 has two qualifying paths."
5. **The actual-knowledge question is named in the City Solicitor's memo and quoted, but the source does not predict its outcome.** Q28 / Q35 / Q39 invoke the question; the oracle restates it concisely without predicting.
6. **The protected tree count of 7 is stated explicitly in source §5.** Q15 is therefore direct lookup. Acceptable for direct-lookup design.
7. **The removable tree count of 16 is stated explicitly in source §5.** Q31 is therefore direct lookup.
8. **The total count of 23 trees subject to the Ordinance is stated explicitly in source §1 and §2.** Q30 is direct lookup.
9. **The exhibit count is not pre-tallied as "nine."** Source enumerates exhibits T-1, T-2, K-1, P-1, Ph-1, Ph-2, Ph-3, O-1, and C-1 across multiple sections. Q33 requires the parser to enumerate and count.
10. **The protected tree IDs after amendment are not pre-listed.** Source lists six original IDs in §2 and adds tree #19 in §5; Q32 requires the parser to merge these into a complete list of seven.
11. **The April 21 felling event has three corroborating sources** (Kowalski's email, Ph-2, T-2). No single source pre-states the corroboration; Q10 requires the parser to compose across exhibits.
12. **The withdrawn April 11 draft is included with explicit "is retained for procedural records only" framing.** No question asks the parser to invoke the withdrawn draft as governing; Q19 requires identifying it as non-operative.

## Self-flagged design choices

- The protected tree count (7), removable count (16), and Ordinance-subject count (23) are all stated explicitly in source. These three direct-lookup questions could be hardened by removing the explicit count statements and forcing the parser to derive them from the lists.
- Q32 requires merging the original list (six IDs in §2) with the addition (#19 in §5). If you'd rather have the full list pre-stated in source, easy to add a "complete protected list after amendment" table.
- Q40 oracle answer pulls a specific number (26.2 inches) from source §8. This is supporting evidence rather than the answer itself; the answer is the methodological reasoning. If you want to test whether the parser can ignore the supporting number, that's already what's tested.

## What is in source vs oracle

- **source.md** contains: site context, ordinance criteria, original permit, post-permit re-survey, withdrawn pre-amendment draft, amendment, contractor email, project manager statement, post-removal inspection, photographic evidence, public objection, Tree Warden response, City Solicitor memo, date-event anchors, open items.
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


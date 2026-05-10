# Anti-Leakage Manifest — school_trip_bus_roster_split

> Purpose: certify that source.md and qa.md do not contain answer keys, and explain how oracle.jsonl was constructed without leaking back into source.md.

## Leakage checks performed

1. **No oracle text appears verbatim in qa.md.** Questions probe lookup, version selection, time-windowed status, conjunction enumeration, and absence-of-record.
2. **No "answer:" or "the correct answer is" markers appear in source.md.** The source is a school incident report packet with embedded exhibits, statements, district policy citations, and a parent letter.
3. **The Pruitt-to-Yi substitution is signaled in source as a procedural sequence (Pruitt called out 7:10; Yi added 7:35; April 22 roster superseded).** Q15 / Q16 / Q39 require the parser to apply this sequence.
4. **The bus swap is described in source with conserved counts and named students.** Q17 is direct lookup of the count (38). Q18 is the harder version that probes the parser's understanding that counts can be conserved while composition changes.
5. **Yi's two roles are documented in two separate sections (§9 lunch and §8 nurse note for the demo).** Q15 and Q22 isolate the two roles; the source does not pre-state "Yi had two roles."
6. **The chaperone-to-student ratio of 1:6.58 is stated explicitly in source §13.** Q27 is therefore direct lookup of the conclusion. If you'd rather force the parser to derive the ratio from the counts, strip the explicit ratio statement.
7. **The "no contradiction" framing for Q40 is not pre-stated in source.** Source records the bus count and the scan log independently; the inference that they corroborate is in the oracle only.
8. **Whitaker's observation at 2:33 vs scan log at 2:35 is presented in source without resolution.** Q38 requires the parser to compose the resolution from the timeline.
9. **Pending vs decided is named in source as "no determination has been issued before that meeting" and "scheduled May 1, 2026 (not yet held)."** The oracle restates these without predicting outcomes.
10. **The April 18 withdrawn draft is included with explicit "withdrawn and superseded" framing.** No question requires the parser to invoke the withdrawn draft as governing.

## Self-flagged design choices

- The chaperone-to-student ratio (1:6.58) and policy compliance ("within policy") are stated in source §13. Q27 is therefore direct lookup of a stated conclusion. If you want a derivation test, regenerate §13 to omit the conclusion.
- Q33 requires deduplication of stations (Mill Station appears twice). The source enumerates the scan events; the deduplication count is in the oracle only.
- Q40's "no contradiction" framing is the harder version of the cross-source-conflict pattern: the parser must recognize that *apparent* conflicts can resolve consistently when both records are accurate. Q38 is the same pattern with a less obvious resolution.

## What is in source vs oracle

- **source.md** contains: trip overview, chaperone roster (April 22 and day-of), bus assignments and swaps, bus loading headcount, trip schedule, wristband scan log, headcount records, mid-trip nurse incident, lunch table assignments, three teacher statements, parent letter, school administration response, district policy reference, withdrawn draft, date-event anchors, open items.
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


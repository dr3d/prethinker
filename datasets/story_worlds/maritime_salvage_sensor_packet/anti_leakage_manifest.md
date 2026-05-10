# Anti-Leakage Manifest — maritime_salvage_sensor_packet

> Purpose: certify that source.md and qa.md do not contain answer keys, and explain how oracle.jsonl was constructed without leaking back into source.md.

## Leakage checks performed

1. **No oracle text appears verbatim in qa.md.** Questions probe lookup, supersession, conjunction enumeration, status-at-time isolation, and absence-of-record.
2. **No "answer:" or "the correct answer is" markers appear in source.md.** The source is a court-clerk packet with embedded exhibits, registry excerpts, and a magistrate judge's memo.
3. **The negative-existential answers about title transfer and the "lost at sea" flag are signaled in source as institutional disclaimers, not as answer keys.** The registry note states "the 'lost at sea' status flag does not by itself transfer title or alter ownership of record." Q18 / Q27 invoke that rule; the oracle restates it concisely.
4. **The interpretive non-adjudication on Position A vs Position B is signaled in source as "the survey report does not adjudicate between the two interpretations."** No question is phrased as a recapitulation; Q35 / Q39 require composing this with the absence of any subsequent adjudication.
5. **The 220-meter distance is stated explicitly in source §4.** Q31 is therefore direct lookup. Acceptable for direct-lookup design.
6. **The two legal frameworks (Salvage Convention 1989 and U.S. common law of salvage) are stated in source §9.** Q28 is direct lookup of the framework names. The choice between them is a separate, unresolved question (Q37).
7. **The "84 feet" / "84 meters" supersession pair is signaled in source via the §5 erratum.** Q15 / Q38 require the parser to identify both values and rank them.
8. **Pending-vs-decided is named in source as "no determination on ownership status or salvage award has been issued" and "referred to merits briefing."** The oracle restates these without predicting outcomes.
9. **The withdrawn April 4 draft is included with explicit "is retained for procedural records only and does not represent the salvor's current claim" framing.** No question asks the parser to invoke the withdrawn draft as the salvor's position; Q17 requires identifying both the withdrawn and current versions.
10. **The buoy-placement attribution requires composing across two sources** (Banerjee's observation in Exhibit D-2 and the Velasco Brothers' April 13 letter in Exhibit V-1). No single source states "Banerjee observed a buoy placed by Velasco Brothers"; that synthesis is in the oracle only (Q22).

## Self-flagged design choices

- Q22 is intentionally compositional, requiring the parser to combine the dive log observation with the ownership-assertion letter. If your parser handles only single-source lookup, this question will fail correctly.
- Q33 enumerates events across three days inclusive. The packet does state these events explicitly in the date-event anchor list, so the parser can extract directly; the test is whether it filters correctly to the date range.
- Q40 is intentionally a multi-clause negative-existential. If you'd rather have a flatter "title has not transferred" answer, easy to simplify.

## What is in source vs oracle

- **source.md** contains: vessel/casualty summary, harbor registry excerpt, two sonar survey reports, an erratum, two diver dive logs, Velasco Brothers ownership-assertion letter, insurer claim and subrogation letter, salvor's claim status, storm event, magistrate judge proceedings and memo, withdrawn pre-claim draft, date-event anchors, open items.
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


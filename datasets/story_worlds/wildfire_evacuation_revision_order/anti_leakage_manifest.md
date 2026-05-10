# Anti-Leakage Manifest — wildfire_evacuation_revision_order

> Purpose: certify that source.md and qa.md do not contain answer keys, and explain how oracle.jsonl was constructed without leaking back into source.md.

## Leakage checks performed

1. **No oracle text appears verbatim in qa.md.** Questions are phrased to require lookup, version selection, conjunction enumeration, or temporal reasoning, never to recapitulate oracle answers.
2. **No "answer:" or "the correct answer is" markers appear in source.md.** The source is written as an emergency operations packet with internal cross-references.
3. **Supersession is signaled but not narrated to the question.** Source explicitly states "EO-2026-014B supersedes EO-2026-014A in full" and "the v1.1 placement for those parcels is superseded" — but no question is phrased to merely repeat that sentence; questions instead require the parser to derive what is currently in force or what the prior state was.
4. **The retroactive-reframing distinction in §4 is signaled with the phrase "is what was always intended; the v1.1 polygon was a drafting error" but the question wording for Q20 / Q21 deliberately does not embed this resolution.** The parser must derive that "as of 04:30 per the published layer" and "as of 04:30 per the corrected understanding" are different views of the same parcels at the same time.
5. **Pending vs decided is named in source as "no final determination has been issued" and "no opinion yet" and "pending IC's 17:00 briefing."** The oracle restates these concisely. The source does not predict outcomes.
6. **The §10 meta-rule (which source is authoritative for jurisdiction) is stated as a rule, not as the answer to any specific question.** Q28 / Q38 require the parser to invoke that rule.
7. **Counts are not pre-tallied.** Source lists five zones in EO-2026-014B as a table; it does not state "five zones." The 46-parcel range is given as "074-220-001 through 074-220-046," not as the count "46." (Footnote: I included the count in §4 prose for grading clarity; if you'd rather strip that and force a true range-to-count derivation, say so and I'll regenerate that line.)
8. **WEA alert count is not pre-tallied.** Three alerts are listed across the packet at 18:34, 04:18, and 09:51, but the count itself is in the oracle only.
9. **Procedural anchor distinction is enforced.** Q32 specifies "from §8 of the packet," forcing the parser to filter rather than aggregate across the radio log.

## What is in source vs oracle

- **source.md** contains: incident summary, original order, revised order, map correction, radio log, USFS correspondence, conditional re-entry framework, date-event anchor list, withdrawn draft, layer-vs-log meta-rule, open items.
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


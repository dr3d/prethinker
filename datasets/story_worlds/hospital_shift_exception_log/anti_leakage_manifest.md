# Anti-Leakage Manifest — hospital_shift_exception_log

> Purpose: certify that source.md and qa.md do not contain answer keys, and explain how oracle.jsonl was constructed without leaking back into the source.

## Leakage checks performed

1. **No oracle text appears verbatim in qa.md.** Questions are phrased to require lookup, supersession, or computation against source.md, never to recapitulate the oracle answer.
2. **No "answer:" or "the correct answer is" markers appear in source.md.** The source is written as an institutional packet, not as a study guide.
3. **No question telegraphs its answer's category.** For example, q022 asks whether a flow sheet entry exists; the source records the absence as a procedural fact rather than as a meta-statement about the question.
4. **Conflict resolutions are not pre-stated.** For Q38, the source contains the central station log, Tilling's statement, and Pruitt's statement, but does not include a sentence that says "the conflict resolves in favor of Tilling." That synthesis is in the oracle only.
5. **Supersession is signaled by addendum, not narrated.** The source contains Addendum A, which states that 14:02:51 is authoritative. The reasoning chain ("therefore the 14:02:21 value is wrong for the timeline") is in the oracle only.
6. **Counts and arithmetic are not pre-tallied.** Source contains the seven Room 504 badge events as raw rows but does not state "there were seven entries." Q30 / Q32 / Q33 require the parser to tally.
7. **Unresolved status is named in source as "NOT YET DETERMINED" with the pending evidence (Yamamoto review March 16).** The oracle restates this concisely. The source does not predict the determination.
8. **Policy version selection.** Source includes both the withdrawn February draft and the in-force version. The source explicitly tags the draft as "withdrawn" and "not operative" but does not directly map this to any specific question. Mapping is in the oracle.

## What is in source vs oracle

- **source.md** contains: roster, roster change, patient context, Pyxis log, badge log, telemetry log, flow sheet excerpt, pharmacist note, resident note, attending note, three witness statements, override audit rule, policy version note, quality review filing with pending status, two addenda.
- **qa.md** contains: 40 numbered questions, no answers.
- **oracle.jsonl** contains: 40 reference answers, with category tags.
- **strategy.md** contains: design rationale, failure modes, complexity map. NOT compile context.
- **anti_leakage_manifest.md** (this file) contains: certification of leakage checks. NOT compile context.

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


# Anti-Leakage Manifest — university_lab_sample_chain

> Purpose: certify that source.md and qa.md do not contain answer keys, and explain how oracle.jsonl was constructed without leaking back into source.md.

## Leakage checks performed

1. **No oracle text appears verbatim in qa.md.** Questions probe lookup, supersession, conjunction enumeration, temporal isolation, and absence-of-record.
2. **No "answer:" or "the correct answer is" markers appear in source.md.** The source is an institutional custody record with internal cross-references and an embedded SOP citation.
3. **Supersession is signaled in source but not pre-mapped to questions.** Source states "the corrected report is the report of record for the sample; prior versions are retained for audit but are not the report of record." This is presented as an SOP rule, not as the answer to any specific question. Q17 / Q29 require the parser to invoke that rule.
4. **Aliquot timeline isolation is not pre-stated as a finding.** Source provides the timeline (aliquot A archived to R-1 on May 1; aliquot B in F-3 during the May 4–5 failure) but does not narrate "aliquot A was therefore unaffected." Q19 requires the parser to derive this.
5. **The negative existential at Q37 is signaled directly in source ("Did not record specific cap lot").** This is a deliberate easy entry-point for the harder pending-determination questions in Q34.
6. **The cap-lot count of two is not pre-tallied as "two."** Source enumerates LCV-2026-031 and LCV-2026-029 in §10. Q31 requires the parser to count.
7. **Personnel count of three for chain of custody is not pre-tallied.** Source lists each transfer with a name; Q32 requires deduplication and counting (Okeke appears twice as the same person).
8. **Pending-vs-decided is named in source as "no determination has been issued on either question."** The oracle restates this concisely without predicting outcomes.
9. **The withdrawn quote (§13) is included with explicit "is retained for procurement records and does not authorize any analyte beyond PFOA, PFOS, and GenX" framing.** No question asks about PFNA, but the trap remains in source for potential parser hallucination probing.
10. **Q38's resolution depends on cross-referencing Tu's notebook ("split at 13:45") with the LIMS aliquot B return time ("14:02") and the freezer door event ("14:00").** None of these three values are paired with the resolution sentence in source; the parser must compose the resolution.

## What is in source vs oracle

- **source.md** contains: project metadata, sample ID, LIMS chain-of-custody entries, freezer telemetry, badge access log, bench notebook excerpt, instrument run log, initial report, calibration reprocessing memo, erratum/corrected report, vial cap manufacturer memo, personnel substitution note, contamination review status, withdrawn quote, open items.
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


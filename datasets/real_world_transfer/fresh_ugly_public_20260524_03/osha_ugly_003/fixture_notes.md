# Fixture notes: osha_ugly_003

## Source

- Public source URL: https://www.osha.gov/news/newsreleases/atlanta/20251204
- Source family: OSHA news release (Atlanta Region)
- Release number: 25-1508-ATL (123)
- Release date: December 4, 2025
- Collection date (UTC): 2026-05-24

## What this is

An OSHA Atlanta Region news release issued after a worker fatality at the Hanwa Q Cells Georgia Inc. solar-panel plant under construction in White, Georgia. OSHA cited only the engineering and construction contractor (Hyoungwon E&C America Inc.) — not the plant operator. The citations are two serious violations only (one under the OSH Act general duty clause for nitrogen asphyxiation hazards; one for failure to train) with $20,522 in proposed penalties.

## Why this document is messy

1. **Cited entity vs. site operator separation.** The lede names two corporate entities — Hanwa Q Cells Georgia Inc. (operator) and Hyoungwon E&C America Inc. (cited contractor). Only the latter was cited; the former is named but neither cited nor exonerated. A naive extractor will either fail to distinguish them or will infer that both were cited.

2. **Name spelling: "Hanwa" vs. "Hanwha".** The release prints "Hanwa Q Cells Georgia Inc." Public reporting on this incident consistently spells the parent company "Hanwha Qcells." Whether the OSHA release is using a registered entity name that legitimately differs from the parent brand, or whether this is a transcription error, is unresolvable from this document alone. A name-canonicalization layer that auto-corrects "Hanwa" to "Hanwha" may be silently lossy if a Georgia subsidiary actually registered under the spelling "Hanwa."

3. **Deceased worker not named.** The release refers only to "a worker fatality" — no name, no date, no demographic detail. Downstream news reports (Fox 5 Atlanta) name Marion Jose Rugama, 33, of Norcross. An extractor that pulls the name from out-of-document context has hallucinated; the within-document answer is "not named."

4. **No incident date.** The fatality date is not given. The release was issued December 4, 2025. The Fox 5 report indicates the death occurred in May 2025. The document itself supports only an upper bound (sometime before the release).

5. **General duty clause citation.** One of the two citations is under the OSH Act's general duty clause — the catch-all rather than a specific 29 CFR 1910.X standard. The release does not explain why a specific standard was not used. Questions that ask "what 29 CFR section?" cannot be answered from the document.

6. **Unexplained parenthetical in release number.** The release number is "25-1508-ATL (123)". The "(123)" appears in the document but is not explained. An extractor that strips parentheticals as noise loses information; one that preserves them must flag them as unexplained.

7. **Off-by-one penalty.** $20,522 is unusually small for a worker fatality — it covers only two serious citations at near-statutory-minimum levels. The release does not break out the penalty per citation. A reader expecting a "willful + fatality" multi-million-dollar figure (compare osha_ugly_001 at $4.7M) must accept that the dollar amount here is what it is.

8. **Three response options framed as alternatives but issued under one 15-day clock.** Comply, request informal conference, contest — three actions, one window. A schema that gives each action its own deadline field will either replicate the deadline three times or leave two of the slots blank.

## Shapes this pressures

- **Coreference across entities.** Hanwa Q Cells Georgia Inc. and Hyoungwon E&C America Inc. are two different entities; only one is the subject of the citation. The document never explicitly says "Hanwa Q Cells was not cited" — that fact must be derived from absence.
- **Name fidelity vs. name normalization.** "Hanwa" — preserve or auto-correct?
- **Absence-of-evidence.** No worker name, no fatality date, no inspection-open date, no per-citation penalty breakdown, no specific CFR standard for the general duty clause violation.
- **Question premise pushback.** The reference QA includes a question asking for "four response options" when only three exist; the correct answer must reject the premise rather than fabricate a fourth option.
- **Same-region cross-doc validation.** Same media contacts as osha_ugly_001 — Lucero (678-237-0630) and Ruthman (678-237-0631). osha_ugly_002 lists Ruthman with 678-237-0630, which is the cross-document inconsistency. This document agrees with osha_ugly_001.
- **Provisional-fact tagging.** Explicit disclaimer that citations and penalties may change.

## Attachments, redactions, tables, missing fields

- Attachments: none.
- Redactions: none.
- Tables: none.
- Missing fields: deceased worker name, fatality date, inspection-open date, per-citation penalty breakdown, specific 29 CFR standard for general duty clause citation, explanation of "(123)" parenthetical, Hyoungwon corporate headquarters location.

## Extraction caveats

- Preserve "Hanwa" as written. Do not silently auto-correct to "Hanwha."
- Preserve "25-1508-ATL (123)" as written. The parenthetical is part of the release identifier as printed.
- Do not infer that Hanwa Q Cells Georgia Inc. was cited. The document names them only as the plant operator.
- Do not supply a deceased worker name. The document does not contain one.
- Treat the 15-business-day window as a single window covering three response options, not three independent deadlines.
- Treat the second occurrence of the lede paragraph as a duplicate of the first; the section heading separating them is the only structural difference.

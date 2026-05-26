# Fixture Notes — ntsb_ugly_002

## Source

- Public URL: https://www.ntsb.gov/investigations/Pages/RRD26FR001.aspx
- Investigation ID: RRD26FR001
- Docket: https://data.ntsb.gov/Docket/?NTSBNumber=RRD26FR001
- Event date: October 19, 2025
- Collected: 2026-05-26 (UTC)
- Document type: NTSB Railroad preliminary investigation report (web page, not PDF). Status: Ongoing.

## Why messy

- **Preliminary stage with structured empties.** The page exposes four section headers — What We Found, What We Recommended, Lessons Learned, Video — and an empty Safety Alert link. Each is a structural placeholder reserved for the final report and contains no substantive content. Distinguishing "empty placeholder reserved for later" from "no findings/no recommendations" requires lifecycle awareness.
- **Italicized in-line caveat.** 'This information is preliminary and subject to change.' sits in italics as the first line of the What Happened section, above paragraph 1 of the factual narrative. It is *not* a footnote; it is a section preamble.
- **Footnotes mixed terminology and context.** Four footnotes attach to the narrative: footnotes 1 and 4 define terminology ('local time,' 'in the foul'); footnotes 2 and 3 provide contextual facts (subdivision ownership history; segment speed limit). The taxonomy is mixed.
- **Legacy entity preserved in proper noun.** 'MRL Second Subdivision' embeds the acronym MRL — Montana Rail Link, a previously-separate operator acquired by BNSF in 2022 (footnote 2). The current operator and track-owner is BNSF, but the subdivision name preserves the MRL acronym as a fixed proper-noun fragment. Entity canonicalization must treat 'MRL' inside 'MRL Second Subdivision' as a name fragment, not as an active corporate entity.
- **Alphanumeric train identifiers.** H-ALTPAS1-13A and X-INBMCU9-17M follow BNSF train ID conventions: leading symbol code (H- = manifest/mixed-freight; X- = grain or empties), origin/destination codes, and date suffix. They look noisy but are structured.
- **Train identifier roles.** Both trains in the accident are BNSF; the conductor (the fatality) was working on H-ALTPAS1-13A and was struck by X-INBMCU9-17M. BNSF is therefore simultaneously the operator of both trains and a party to the investigation. Operator-and-party dual role.
- **Approximate qualifiers throughout.** 'about 9:32 a.m.,' 'about 37 mph,' 'about 232 feet,' 'around milepost 40.1.' Multiple approximate-value qualifiers in factual statements.
- **Nominal direction vs. actual motion.** H-ALTPAS1-13A is described as 'westbound' (the train's planned direction) but at the accident time it was parked in the siding, not moving. Direction-of-travel attribute persists even when speed is zero.
- **Stationary-and-moving pair.** Two trains involved; one parked, one moving on the adjacent main track. Speed-reconciliation across the pair requires distinguishing nominal travel direction from instantaneous state.
- **"Include" vs. closed list.** The parties-to-the-investigation list uses 'Parties to the investigation include...' Semantically 'include' could leave room for more, but at the preliminary-report stage the list is the operative enumeration. Five parties named, semicolon-delimited.
- **Inline lists without bullets.** Three substantive lists (investigative activities, future focus areas, parties to the investigation) are all rendered as comma-then-and inline sentences, not bulleted.
- **Conductor name absent.** The fatality is referenced only by role ('the conductor'), not by name. Worker-privacy convention.
- **Cloudflare email obfuscation.** 'Family Assistance Contact' and 'NTSB Media Relations' addresses are returned by the page as obfuscated tokens; the actual mailtos are JavaScript-decoded. The fixture preserves them as `[email obfuscated]`.
- **Domain-specific glossary terms.** 'in the foul,' 'siding,' 'main track,' 'milepost,' 'subdivision,' 'event recorder,' 'inward- and outward-facing image recorders.' Several require domain knowledge or footnote definitions.
- **Static map embedded in Investigation Details.** Coordinates (45.637083, -109.255764) appear in a Google Static Maps URL but not in the page body text.
- **Section headers without subordinate content rendered as empty.** Modern CMS-driven layout produces explicit empty sections. An extractor that looks only for top-level headers will see five sections that "should have" content.

## What shapes are pressured

- Preliminary vs. final NTSB lifecycle inference from empty structured sections.
- Italicized in-line caveat detection.
- Footnote extraction with mixed terminology/context taxonomy.
- Legacy entity preservation inside fixed proper noun.
- Alphanumeric train identifier parsing.
- Operator-also-party dual role attribution.
- Approximate qualifier preservation ('about,' 'around').
- Nominal direction vs. instantaneous-state speed reconciliation.
- 'Include' open-vs-closed list semantics at preliminary-report stage.
- Inline comma-and list extraction.
- Role-only references to anonymized persons.
- Domain-specific glossary terms with footnote-defined meanings.
- Map metadata vs. body text divergence.
- Empty-section interpretation as 'reserved for later' not 'nothing found.'

## Attachments, redactions, tables, missing fields

- Attachments: docket link (https://data.ntsb.gov/Docket/?NTSBNumber=RRD26FR001) not extracted; overhead diagram figure referenced but not extracted in this fixture.
- Redactions: conductor name not provided; the two contact email addresses are Cloudflare-obfuscated and not extracted.
- Tables: none in narrative; Investigation Details block uses a flat label-value layout.
- Missing fields: conductor name; conductor age; conductor years of service; specific accident time precision below the minute; precise milepost; weather observation source; What We Found / What We Recommended / Lessons Learned (reserved for final report); estimated date of final report issuance.

## Extraction caveats

- Treat the four empty sections (What We Found, What We Recommended, Lessons Learned, Video) plus the empty Safety Alert link as 'reserved for final report' placeholders. Do NOT assert 'NTSB found nothing' or 'no recommendations.'
- Preserve 'about 37 mph,' 'about 232 feet,' 'about 9:32 a.m.,' 'around milepost 40.1' as approximate values. Do not round or normalize.
- Treat 'MRL' inside 'MRL Second Subdivision' as a fixed name-fragment. Footnote 2 establishes that Montana Rail Link was acquired by BNSF in 2022; the corporate entity 'Montana Rail Link' is not the current operator and does not appear in the parties list.
- Bind 'westbound' to H-ALTPAS1-13A's nominal travel direction (not instantaneous motion — the train was parked in the siding at the accident time). Bind 'eastbound about 37 mph' to X-INBMCU9-17M's actual motion at the moment of impact.
- BNSF appears in two distinct roles: (a) operator of both trains involved; (b) party to the investigation. Do not deduplicate to a single role.
- Preserve the five-element parties list as a closed set despite the 'include' introducer (NTSB preliminary-report convention).
- Bind 'in the foul' to footnote 4's definition: 'close enough to a track to be struck by a moving train or within 4 feet of the nearest rail.' Do not paraphrase to 'near the track.'
- Preserve the conductor as an unnamed role-only referent ('the conductor'). Do not infer name from external sources.
- Preserve the four-footnote structure as a single ordered list belonging to the What Happened narrative; do not flatten footnotes into body text.
- Bind 'This information is preliminary and subject to change' to the What Happened section preamble (not a footnote, not metadata).
- Investigation status 'Ongoing' is stated three times (Investigation Details Status field; What Happened paragraph 4; preamble caveat). Do not infer that triple-statement indicates anything special — it is standard NTSB preliminary-report convention.
- Track segment maximum authorized speed (60 mph, footnote 3) is *context*, not a finding. The report does not assert that speed was a factor in the accident.

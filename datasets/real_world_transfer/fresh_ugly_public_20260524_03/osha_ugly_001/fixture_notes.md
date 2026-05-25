# Fixture Notes: osha_ugly_001

## Public Source

- URL: https://www.osha.gov/news/newsreleases/osha-national-news-release/20260401
- Document: OSHA news release "US Department of Labor cites construction contractor with 7 willful, 33 repeat violations after fatal Yarmouth cave-in," Release Number 26-574-ATL, dated April 1, 2026.
- Collected: 2026-05-24.
- Public domain (U.S. federal government publication).

## Why this document is messy

- Two distinct date references for the fatal incident: "November 2025" in the lead paragraph and the more precise "Nov. 18, 2025" in the body — these must be reconciled as the same event.
- An internal numerical inconsistency: the subhead says "$4.6M in proposed penalties" but the body precise figure is $4,699,362, which correctly rounds to $4.7M. Secondary news outlets report both $4.6M and $4.7M — the OSHA release itself is the source of the discrepancy.
- A "headline count" mismatch: the headline says "7 willful, 33 repeat violations" but the body adds "and 17 serious violations" — the headline omits the serious count.
- Quote syntax uses doubled smart-quote tokens (`'"…'"`) — a real artifact of the page rendering; not standard `"…"` quotation marks.
- Seven bulleted hazard categories appear in close proximity to the "seven willful" count — a misleading numerical coincidence that invites incorrect 1:1 mapping.
- Two prefatory caveat boxes appear at the top, *both* of which apply to every release — the second one notes that "penalty amount(s)" and "classification(s)" may not reflect current or final status.
- Three media contacts listed at the end, with formatted phone numbers and emails.
- Bulleted list of cited hazards uses sentence-case fragments without consistent grammatical structure (some are gerunds: "Failing to provide…", "Neglecting to install…"; some are noun phrases: "Lack of adequate cave-in protection.").

## What shapes this document pressures

- **Counted enumerations**: three classification counts (willful=7, repeat=33, serious=17) and a sum (57). A schema must extract each count and may need to compute the sum.
- **Currency rounding**: the precise figure vs. the rounded tagline. A check on tagline correctness requires float comparison.
- **Provisional-fact handling**: the prefatory "Notice" explicitly says the penalty and classification numbers may change. A schema treating these as committed facts may incorrectly overcommit.
- **Two-tier date references**: "November 2025" vs. "Nov. 18, 2025" — coreference required.
- **Procedural-option list**: three response paths (comply, informal conference, contest before OSHRC) embedded in a single sentence.
- **Quote attribution**: a multi-sentence quote attributed to a named federal official with role title.

## Extraction caveats

- The unusual quotation token `'"…'"` (apostrophe + smart-quote double + content + apostrophe + smart-quote close) appears around the Secretary's quote. This is preserved verbatim; an extractor should not normalize it silently because the artifact carries information about the page rendering.
- The bullet list is preceded by a sentence that ends with `for:` — the bullets are the grammatical object of that sentence, not a free-standing list.
- "Revoli Construction Inc." appears in the subhead but "Revoli Construction Co. Inc." appears in the body — slight name variant.
- The release was issued from "BOSTON" (the dateline location, where the regional press office is) but the cited employer is described as "Massachusetts-based" — the regional office overseeing the case is in Boston, but the incident occurred in Yarmouth, MA (Cape Cod). Three location references must be disambiguated.

## Attachments / redactions / tables / missing fields

- **Attachments**: none in the release itself; it links externally to OSHA's National Emphasis Program PDF and to compliance-assistance pages.
- **Redactions**: **none** — OSHA news releases do not redact, but they also do not name the decedent worker (the release identifies neither the deceased nor the injured worker). This is a kind of "missing field" rather than a redaction.
- **Tables**: none.
- **Missing fields**: name(s) of affected workers; inspection number; OSHA area office and assigned compliance officer; specific cited regulations (29 CFR sections) for each violation; date the citations were actually issued (the "release date" is when the news release was issued, not necessarily the citation date).

## Pressure on Prethinker shapes

- **Citation counting & arithmetic**: the schema must extract three counts and may need to compute their sum (57).
- **Rounding-check / inconsistency detection**: $4.6M vs $4,699,362 vs $4.7M — a contradiction-detection test.
- **Provisional fact tagging**: the prefatory notice qualifies all penalty/classification facts as provisional. An audit schema should propagate that qualification.
- **Spurious-coincidence resistance**: 7 willful citations + 7 bulleted hazards ≠ 1:1 correspondence. A naïve extractor may incorrectly join them.
- **Coreference**: "November 2025" → "Nov. 18, 2025" → "incident"; "Revoli Construction Inc." → "Revoli Construction Co. Inc.". 
- **Qualified answers**: Q25 (1:1 mapping?) should return "no, not stated"; Q14 (rounding correctness) should flag the inconsistency; Q23 (worker names) should note they're absent from the release.

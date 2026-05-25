# Fixture notes: sec_ugly_002

## Source

- Public source URL: https://www.sec.gov/Archives/edgar/data/1013871/000110465926001602/tm261967d1_8k.htm
- Source family: SEC EDGAR Form 8-K
- Registrant: NRG Energy, Inc. (ticker NRG)
- Date of report (date of earliest event reported): January 6, 2026
- Filing date: January 7, 2026
- Collection date (UTC): 2026-05-24

## What this is

An NRG Energy Form 8-K disclosing a planned three-executive leadership succession: Robert Gaudette appointed President (immediate) and CEO (forward-dated to April 30, 2026, NRG's Annual Meeting); Lawrence Coben stepping down as President (immediate), continuing as CEO and Chair through April 30, 2026, then advisor through end of 2026 fiscal year; Antonio Carrillo named to succeed Coben as Chair effective April 30, 2026. Items reported: 5.02 (officer/director changes) and 7.01 (Reg FD / press release). Exhibits: 99.1 (press release), 104 (cover XBRL). No employment agreement attached — compensation pending.

## Why this document is messy

1. **Three-executive overlapping transition.** Gaudette's two role-changes happen at two different dates; Coben's three role-changes happen at two different dates; Carrillo's role-change happens at one of those dates. The Item 5.02 narrative threads all three through one continuous paragraph, with simultaneity ("effective immediately," "as of April 30, 2026") doing the work of distinguishing events that share a date. A pipeline that extracts one (executive, role, date) tuple per sentence will lose the bundling.

2. **Two-cluster temporal structure.** Five events on January 6, 2026 (the "immediate" cluster). Four events on April 30, 2026 (the "Annual Meeting" cluster). The 16-week gap is not narrated; the document jumps between the two by tense and adverbial phrase.

3. **Forward-dated CEO appointment.** Gaudette is "appointed" CEO on January 6, 2026, "effective April 30, 2026." A naive extractor that records the appointment date as the start date is wrong; the appointment exists, but the role-holder is still Coben until April 30.

4. **Missing word in sentence.** "Biographical and other information about Mr. Gaudette is included the Company's definitive proxy statement" — the preposition "in" is missing. Preserve verbatim.

5. **Stale cross-reference.** The 8-K points readers to a March 19, 2025 proxy for biographical info, but Gaudette's role has materially changed between then and now. The document does not flag the staleness.

6. **Partial table row.** The Section 12(b) registration table has a second row with only "NYSE Texas" in the Trading Symbol column and the other two columns blank. Combined with the standalone "NYSE Texas [Member]" line at the top of the document, this suggests NRG is dual-registered on NYSE and NYSE Texas, but the table does not show this cleanly.

7. **Compensation deferred.** The 8-K states compensation has not been finalized; an amendment will follow. The 8-K creates a future-disclosure obligation but does not date it.

8. **Negative-fact assertions about Gaudette.** Three separate "no X" claims (no family relationships, no arrangements, no transactions). A schema that records absence-of-information loses the affirmative nature of these claims.

9. **"Lead Independent Director" mentioned only in press release.** The 8-K text describes Carrillo only as having "served on the Board since 2019." His pre-Chair title as Lead Independent Director appears in Exhibit 99.1 (per the related press release excerpt visible in other sources), not in the 8-K body. The 8-K therefore under-specifies his old role.

10. **Phone number formatting oddity.** "( 713) 537-3000" has a space after the opening parenthesis. Cosmetic, but a normalization layer that strips/collapses parens may misalign with the source.

## Shapes this pressures

- **Multi-actor, multi-role, multi-date transition.** Pressure on (actor, role, role_state, effective_date) tuples vs. simpler (actor, new_role) extraction.
- **Forward-dated effectiveness.** Distinguish "appointed" from "effective" dates.
- **Cross-reference staleness.** Detect when a referenced prior filing may be out of date with respect to the current 8-K's subject.
- **Partial table rows.** Joining a 1-column row to the 3-column header.
- **Forward-looking compensation obligation.** Pending fact; commits to future disclosure.
- **Negative-fact triples.** Three explicit "no" assertions; preserve as affirmative, not as silence.
- **Two-event clusters with shared dates.** Resolve "effective April 30, 2026" applies to multiple distinct transitions.
- **Off-document title for Carrillo (Lead Independent Director).** Within-document answer must be "not stated"; out-of-document context may resolve it.

## Attachments, redactions, tables, missing fields

- Attachments: Exhibit 99.1 (press release, not included in this fixture extraction); Exhibit 104 (XBRL, machine-readable).
- Redactions: none.
- Tables: cover-page jurisdiction/file/EIN table; cover-page check-box tables (four single-row tables); Section 12(b) registration table (with partial second row); exhibit-index table; signature block table — all "untagged ... column alignment not verified."
- Missing fields: Gaudette's compensation; Carrillo's pre-Chair title; "end of 2026 fiscal year" calendar date; Gaudette's title as of March 19, 2025; the date Gaudette ceases to be EVP NRG Business and Wholesale Operations.

## Extraction caveats

- Treat "effective immediately" as binding to January 6, 2026 (the report date), not to the filing date (January 7).
- Treat "effective April 30, 2026" as a forward effective date; the appointment is current, the role is future.
- Preserve the missing-"in" sentence as written.
- Treat the second row of the Section 12(b) table as containing only "NYSE Texas" in the Trading Symbol column; do not invent the other two cells.
- Do not collapse the four "January 6" events into a single composite event.
- Preserve "Dr. Coben" honorific (Ph.D.) as distinct from a non-honorific reference.
- Treat "end of the 2026 fiscal year" as the literal date specifier; do not auto-resolve to December 31, 2026, without justification.

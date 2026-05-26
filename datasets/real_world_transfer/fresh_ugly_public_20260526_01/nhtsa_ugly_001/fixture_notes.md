# Fixture Notes — nhtsa_ugly_001

## Source

- Public URL: https://static.nhtsa.gov/odi/rcl/2026/RCAK-26V229-1960.pdf
- NHTSA Campaign Number: 26V229
- Mfr's Report Date: April 10, 2026
- NHTSA letter date: April 15, 2026
- Collected: 2026-05-26 (UTC)
- Document type: NHTSA Office of Defects Investigation Recall Acknowledgement Letter (RCAK), 2-page PDF, sent from NHTSA to manufacturer after manufacturer's safety-recall notification.

## Why messy

- **Brand-vs-legal-entity layering.** The letter is addressed to Hyundai Motor America (legal entity), but the products are Genesis-brand vehicles. The parenthetical 'Hyundai Motor America (Genesis) is recalling certain Genesis... vehicles' makes the relationship explicit, but the brand/entity boundary surfaces at five distinct points: salutation (Hyundai), Problem Description (Genesis), Makes/Models block (GENESIS), customer service (Genesis), manufacturer-internal ID ('Genesis' number').
- **Reordered model lists with one year-range omission.** Makes/Models/Model Years block lists GV80, G80, GV70, G90 (with year ranges for each). Problem Description reorders to GV70, G90, G80, GV80 — and omits the year range for GV80 only ('...G80, and GV80 vehicles'). Cross-field recovery is required to obtain GV80's range.
- **Hybrid colon-and-comma component path.** 'FUEL SYSTEM, GASOLINE:DELIVERY:HOSES, LINES/PIPING, AND FITTINGS' encodes hierarchy with colons and items-within-a-level with commas. The leading 'FUEL SYSTEM, GASOLINE' is one item (with embedded comma), not two. Forward slash inside 'LINES/PIPING' is another delimiter.
- **Page-footer letterhead bleed into body.** The two address lines '1200 New Jersey Avenue SE / Washington, DC 20590' appear mid-paragraph in the Remedy section, interrupting the prose between 'Genesis customer service at 844-340-9741' and 'Genesis' number for this recall is 033G.' This is a PDF rendering artifact (the address sits as a right-aligned letterhead block). Treat as letterhead, not as Genesis's address.
- **Three identifier namespaces.** NHTSA Campaign Number 26V229. NHTSA PDF filename includes 'RCAK-26V229-1960' (the -1960 suffix is an internal sequence number). Genesis-internal '033G.' All three identify the same recall in three different naming schemes.
- **Manufacturer-side contact with government email domain.** 'Hyundai Motor America's contact for this recall will be Emily Smith who may be reached by email at emily.c.smith@dot.gov.' The description attributes the contact to the manufacturer; the email is at @dot.gov (federal government). Internally inconsistent on its face. Preserve verbatim; do not silently rationalize.
- **Three reminder paragraphs with multiple statutory/regulatory citations.** 49 U.S.C. § 30112(a)(3); 49 U.S.C. § 30118(f); 49 C.F.R. § 573.7 (cited as bare '573.7'). The bare CFR section number without title-and-part prefix is unusual.
- **Relative deadlines without absolute dates.** First quarterly: 'within one month after the close of the calendar quarter in which notification to purchasers occurs.' First annual: '1 year after the eighth quarterly report was submitted.' Draft owner notification: 'no less than five days prior to mailing.' Copies of final letters: 'no later than 5 days after they are originally sent.' Each requires calendar arithmetic against other dated events to recover an absolute deadline.
- **Conditional remedy.** Dealer action is 'inspect and tighten, OR replace the fuel pipe as necessary.' Two alternative remedies; the choice is condition-dependent.
- **Multiple April dates.** Manufacturer report April 10, 2026; VIN searchable April 11, 2026; NHTSA letter April 15, 2026. Three different April dates within five days for the same recall.
- **Five-act prohibition list.** 49 U.S.C. § 30112(a)(3) prohibits five acts: sell, offer for sale, import, introduce, deliver into interstate commerce.
- **Nested organizational signature title.** 'Chief, Recall Management Division / Office of Defects Investigation / Enforcement' — three nested levels.
- **Dual phone numbers.** Genesis customer service line and NHTSA Vehicle Safety Hotline serve different purposes; TTY variant paired only with the NHTSA hotline.
- **Comma-formatted unit count.** '94,760' affected units. Lower-bound semantics: 'Potential Number of Units Affected' is the recall scope population, not necessarily the actual defect population.

## What shapes are pressured

- Brand-vs-legal-entity canonicalization across multiple surfaces.
- Cross-field recovery of omitted attributes (GV80 year range).
- Reordered list comparison between structured block and prose.
- Hybrid delimiter (colon + comma + slash) hierarchical paths.
- Page-footer artifact recognition (don't bind the NHTSA address to Genesis).
- Multi-namespace identifier extraction (NHTSA campaign, NHTSA filename, manufacturer-internal).
- Internal inconsistency preservation (manufacturer contact with .gov email).
- Statutory and regulatory citation extraction with mixed citation styles.
- Bare CFR section number expansion.
- Relative deadline interpretation requiring calendar arithmetic.
- Conditional / alternative remedy parsing.
- Multi-date chain reconstruction across April events.
- Five-act prohibition enumeration.
- Nested organizational title parsing.
- Dual contact-number extraction with TTY pairing.
- 'Potential' vs. 'actual' population semantics.
- 'Five days prior to' vs. 'five days after' deadline anchoring.
- Open vs. closed reporting cadence (8 quarterly + 3 annual = ~5 years post-notification).
- Question-premise check (question 15 asks for four April dates; only three exist).

## Attachments, redactions, tables, missing fields

- Attachments: none. The PDF is the entire document.
- Redactions: none.
- Tables: none. Field-block format with labeled fields.
- Missing fields: VIN range or VIN identification scheme; specific dealer obligations beyond inspect/tighten/replace; final remedy completion deadline; specific calendar dates for the quarterly/annual reporting (only relative offsets given); whether Emily Smith is a manufacturer or NHTSA contact (description says manufacturer, email says government); the model-year range for GV80 in the Problem Description (must be recovered from the Makes/Models block).

## Extraction caveats

- Treat 'Hyundai Motor America' as the legal entity and 'Genesis' as the brand. Both appear; do not collapse to one.
- Preserve '94,760' verbatim. Tag as 'Potential' population, not 'actual.'
- Treat the component string as a single hierarchical path with mixed delimiters; do not split 'FUEL SYSTEM, GASOLINE' into two items.
- Do NOT bind '1200 New Jersey Avenue SE / Washington, DC 20590' to Genesis or to the Remedy paragraph; it is a NHTSA letterhead address bleeding mid-paragraph.
- Recover GV80's model-year range (2021-2025) from the Makes/Models/Model Years block when needed; preserve the Problem Description's omission verbatim in source view.
- Preserve 'emily.c.smith@dot.gov' and the description 'Hyundai Motor America's contact' verbatim with an internal-inconsistency tag; do not silently relabel the contact as NHTSA-internal.
- Bind 49 U.S.C. § 30112(a)(3), 49 U.S.C. § 30118(f), and 49 C.F.R. § 573.7 (the 'bare 573.7' cite) as three distinct citations.
- Treat 'inspect and tighten, or replace the fuel pipe as necessary' as a conditional remedy with two alternative actions; the dealer's selection is condition-dependent.
- Treat all reporting and notification deadlines stated as relative offsets ('within one month after...,' '5 days after...,' '5 days prior to...') as relative; provide absolute dates only when grounded in another absolutely-dated event.
- Preserve the three-line signature title as a nested organizational path: Chief → Recall Management Division → Office of Defects Investigation → Enforcement.
- Genesis customer service phone (844-340-9741) handles recall 033G / 26V229 inquiries; NHTSA hotline (1-888-327-4236, TTY 1-888-275-9171) handles general consumer safety inquiries. Do not merge.
- When asked for 'all April dates' (question 15), provide the three that exist and flag the premise that exactly four were expected — premise should not silently constrain the answer.

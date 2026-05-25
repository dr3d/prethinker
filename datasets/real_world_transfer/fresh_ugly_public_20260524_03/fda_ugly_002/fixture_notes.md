# Fixture Notes: fda_ugly_002

## Public Source

- URL: https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/vapingcom-710327-06062025
- Document: FDA Center for Tobacco Products Warning Letter to vaping.com, MARCS-CMS 710327, dated June 6, 2025; internal reference RW2502296.
- Collected: 2026-05-24.
- Public domain (U.S. federal government publication).

## Why this document is messy

- A long cc distribution block at the end of the letter listing six distinct entities — four of which are different addresses or d/b/a variants of the same legal entity (SV3, LLC). One cc block contains a `**(b)(6)**` redaction (FOIA Exemption 6, personal privacy) where a contact email/phone is withheld.
- Mixed statutory citation styles throughout: parallel pairs of FD&C Act section numbers and 21 U.S.C. citations, plus 21 C.F.R. Parts and a Public Law reference (Public Law 117-103, Division P, Title I, Subtitle B).
- Two named products embedded inline mid-paragraph rather than in a bulleted list; the rest of the paragraph blends product identification with statutory citation.
- Two distinct date "tiers" — the letter date (June 6, 2025), the receipt-triggered response deadline (15 working days from receipt — i.e., a *relative* deadline), the page-content date (June 17, 2025), and two historical fixed dates from statute (February 15, 2007 and March 15, 2022).
- A long block-format response address (multi-line postal address inside what reads as a single instruction sentence).
- Bold inline heading "**VIA UPS and Electronic Mail**" reappears below the signature block, mirroring the delivery-method field at the top of the letter — a duplicated visual signal.

## What shapes this document pressures

- **Multi-entity disambiguation**: the same legal entity (SV3, LLC) appears under multiple d/b/a names and at multiple addresses in the cc block. Extracting "recipient" requires knowing that the *header* recipient is the website name, while the *legal* recipients are listed below in the cc.
- **Mixed citation systems**: an extractor must handle FD&C Act § 910(c)(1)(A)(i), 21 U.S.C. § 387j(c)(1)(A)(i), 21 C.F.R. Part 1100.1, and Public Law 117-103 side by side.
- **Relative vs. absolute deadlines**: 15 working days "from the date of receipt" cannot be resolved to an absolute date from the letter alone — receipt date is not in the public record.
- **Redaction at the cc level**: a `(b)(6)` rather than `(b)(4)` — different FOIA exemption (personal privacy vs. confidential commercial information). An extractor must distinguish exemption codes.
- **Cross-section joining**: the adulteration/misbranding paragraph uses statutory hooks that are first introduced in the prior background paragraph (section 905(j), section 910(c)(1)(A)(i)); the reader must walk that bridge.

## Extraction caveats

- The recipient block at the top uses three lines for the street/city/state and a separate line for the email; the linebreaks were preserved.
- The cc list uses irregular spacing in the original (some entries are short, one contains a redaction line, two are email-only). Preserved as-is.
- The phrase "abuse@godaddy.com" and "abuse@shopify.com" appear as cc-only items without a postal address; these are platform-abuse contacts, not respondents.
- The body refers to two specific products inline ("including: Mixed Fruit Funky Republic Ti7000 and Tropical Delight Funky Republic Fi3000"); the word "including" implies the list is non-exhaustive — a qualified-answer signal.

## Attachments / redactions / tables / missing fields

- **Attachments**: none.
- **Redactions**: one `(b)(6)` in the cc block for the d/b/a Smoking Vapor entry.
- **Tables**: no formal tables; the cc block is the closest structured listing.
- **Missing fields**: the firm's response (not yet on the record at publish time); the date the letter was received (which would trigger the 15-working-day clock); the identity of the redacted personal contact.

## Pressure on Prethinker shapes

- **Coreference resolution across cc entries**: extracting that four cc entries are the same legal entity at different addresses/dbas.
- **Exemption-code awareness**: distinguishing `(b)(4)` (commercial) from `(b)(6)` (personal) — different downstream handling.
- **Open-list extraction**: the "including:" pattern means the canonical product list is partial; the schema must mark this list as non-exhaustive.
- **Statutory citation pairing**: each FD&C Act section is paired with a U.S.C. citation in parentheses; an extractor must keep both or canonicalize one to the other.
- **Qualified answers required**: Q18 (response deadline) cannot be answered with an absolute date; Q11 (products listed) must note non-exhaustiveness; Q10 must explicitly note the (b)(6) redaction.

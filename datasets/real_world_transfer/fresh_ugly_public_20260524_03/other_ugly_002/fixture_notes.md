# Fixture Notes — other_ugly_002

## Source

- Public URL: https://www.ftc.gov/news-events/news/press-releases/2026/03/ftc-takes-action-against-match-okcupid-deceiving-users-sharing-personal-data-third-party
- Collected: 2026-05-24 (UTC)
- Document type: FTC press release announcing a complaint and proposed stipulated final order, filed in federal district court.
- Release date: March 30, 2026

## Why messy

- **Anonymized referent.** The unrelated third party that received the data is never named in the press release. It is referenced by seven different paraphrases ("an unrelated third party," "a third party," "the third-party data recipient," "the data recipient," "the third party"). Coreference resolution is required, and the referent is unnamed.
- **Motive without identity.** The page imputes a motive to the third party ("OkCupid's founders were financial investors in the third party") without identifying the third party. The investor-relationship motive must be bound to an unnamed entity.
- **Brand vs. legal entity.** "OkCupid" is treated as a product/brand throughout the headline and body, while the actual legal respondents are Humor Rainbow, Inc. (operator) and Match Group Americas (services provider). The stipulated-order PDF filename ("MatchGroupAmericasandHumorRainbowStipulatedOrder.pdf") confirms the respondent identities. Entity canonicalization is required.
- **Two-respondent settlement with shorthand.** The complaint and final order are described as filed against "OkCupid and Match" but the bullets refer to "the companies" and the underlying respondents are Humor Rainbow and Match Group Americas. The shorthand can drop one of the two respondents during careless extraction.
- **Hybrid list of sharing categories.** The privacy-policy paraphrase mixes three recipient categories (service providers, business partners, family-of-businesses entities) with one process condition (notice-and-opt-out). A list extractor that assumes homogeneous types will mis-classify the fourth item.
- **Approximate count.** "Nearly three million" photos is a floor/approximation, not an exact figure.
- **Partial date.** "Since September 2014" gives a month and year but not a day; the concealment has a start date but no end date asserted on the page.
- **No date for the underlying sharing.** The press release does not state when the data sharing itself began or ended — only that the concealment of it dates "since September 2014." Confusing the two yields a wrong sharing-start date.
- **Two-vote Commission.** The "2-0" vote is reported without explanation of the remaining seats; the press release does not state that any commissioners were recused, vacant, or absent.
- **Provisional / pending status.** The "NOTE" paragraph explicitly notes that "Stipulated final orders have the force of law when approved and signed by the District Court judge." The settlement is referred to as "the proposed settlement." Treating it as effective is incorrect.
- **No remedy applied to the third party.** The press release describes only restrictions on Humor Rainbow and Match Group Americas; the unnamed third party is unaffected by the order as described on this page.
- **Three contact persons.** The media contact (Henderson) is separate from the lead staff attorneys (Choi and Rosenberg) and the quoted official (Mufarrige); a single "contact" extractor will collapse these incorrectly.
- **Embedded quotes.** The release contains both a quote from a privacy policy ("your personal information with others except as indicated...") and a quote from Mufarrige ("The FTC enforces the privacy promises..."). They are attributed differently and should not be conflated.
- **"Including" semantics.** The first prohibition bullet uses "such as photos and demographic and geolocation data" — illustrative, not closed.

## What shapes are pressured

- Anonymized / unnamed referents and coreference resolution across paraphrases.
- Brand-vs-legal-entity canonicalization (OkCupid vs. Humor Rainbow, Inc.; OkCupid vs. Match Group Americas).
- Two-respondent obligations with shorthand collapse risk.
- Hybrid lists (recipient categories vs. process conditions).
- Floor / approximate counts.
- Partial dates (month + year only).
- Start-only / open-ended duration assertions.
- Distinguishing two distinct allegation events with different temporal markers (sharing vs. concealment).
- Provisional / pending status of a stipulated final order pending court approval.
- Multi-actor attribution (quoted official, media contact, lead attorneys).
- Open-list semantics (illustrative "such as" phrases).
- Vote-record interpretation with unstated seat composition.
- Negative-fact extraction (what the third party is *not* required to do).

## Attachments, redactions, tables, missing fields

- Attachments: Complaint PDF (linked, not extracted); Stipulated Final Order PDF (linked, not extracted).
- Redactions: none.
- Tables: none; one three-bullet prohibition list.
- Missing fields on the press release: case number / civil action number; assigned judge; filing date in court; effective date of the stipulated final order (contingent on court approval); name of the third-party data recipient; start date and end date of the actual data-sharing conduct (only concealment start is given); monetary relief or civil penalty (none described); count of affected users (only photo count is given, "nearly three million"); start date and end date of the privacy-policy text quoted ("at the time" — undated).

## Extraction caveats

- Treat the stipulated final order as proposed, not entered. Force of law is gated by District Court judge approval and signature.
- Preserve the third party as `Unnamed`/`Anonymous` and do not unify it with any external candidate (e.g., Clearview AI) — the press release does not perform that identification.
- Treat "since September 2014" as a partial date (month + year). Do not invent a day or an end date.
- Bind "since September 2014" to the *concealment* of the data sharing, not to the data sharing itself.
- Treat "nearly three million" as an approximate floor; do not assert an exact count.
- Canonicalize entities: Humor Rainbow, Inc. and Match Group Americas are the legal respondents; OkCupid is a product/brand operated by Humor Rainbow.
- Treat the privacy-policy quote as text attributed to OkCupid's then-current privacy policy, with "at the time" as an unbounded temporal qualifier; do not bind it to a specific date.
- The 2-0 vote should be preserved without an inferred quorum or seat count. Do not infer reasons for the unfilled seats.
- The Mufarrige quote is attributable to the Director of the Bureau of Consumer Protection. Do not confuse this title with the Chairman position (Andrew N. Ferguson, mentioned only in site navigation, not in the press release body).
- Distinguish lead attorneys (Choi, Rosenberg) from the quoted official (Mufarrige) and from the media contact (Henderson).
- Do not infer remedies, restrictions, or obligations on the third party from the absence of named restrictions. The press release does not say the third party is unrestricted; it simply does not address the third party's obligations.

# Fixture Notes: fda_ugly_003

## Public Source

- URL: https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/nupack-inc-722113-03202026
- Document: FDA Human Foods Program Warning Letter to Nupack Inc., CMS #722113, dated March 20, 2026.
- Collected: 2026-05-24.
- Public domain (U.S. federal government publication).

## Why this document is messy

- Numerous inline-quoted product label fragments preserved verbatim with the firm's original formatting errors: ellipses with varying numbers of dots (`…`, `…..`), embedded bracketed editorial corrections (`[N]atural`, `[H]ealthy`, `[heart disease]`, `[sic]`), and one merge of two list items where a "Your firm's label for your Kidney Cleanse states the following:" lead-in sentence is concatenated to the end of a preceding Cleanse-CAMP bullet without a paragraph break.
- Inconsistent product-name casing across sections: "Cleanse-CAMP" in the Unapproved New Drugs section vs. "Cleanse-camp" in the Adulterated Dietary Supplements section and every numbered violation. "Pure Pysyllium Husk" (misspelled) in the opening list vs. "Pure Psyllium Husk" in the label sub-block.
- Different statutory frameworks are invoked across three named sections: Unapproved New Drugs (sections 201(g)(1)(B), 201(p), 301(d), 505(a)), Misbranded Drugs (section 502(f)(1) with 21 CFR 201.5 and section 503(b)(1)(A)), Adulterated Dietary Supplements (section 402(g)(1) with 21 CFR Part 111).
- Recipient email domain (`nupacknutrition.com`) differs from the website being cited as the source of violative claims (`unitechusk.com`).
- The four numbered CGMP violations have a parallel internal structure: each ends with "For example, you did not establish/prepare … for your products, Cardiag, Cleanse-camp, and MACA 1000 mg." Same three products appear in each, signalling that the inspection's documentary evidence comes from the same three product files.
- The response address line is run-on without a comma separator between "Lauren.Crivellone@fda.hhs.gov" and "United States Food and Drug Administration" — a real OCR/formatting artifact preserved as-is.
- A line-break inside an email address: "HFP-\nOCE-DietarySupplements@fda.hhs.gov" — the hyphen at the end of the line is preserved exactly as published.

## What shapes this document pressures

- **Inconsistent identifier casing/spelling**: an extractor that canonicalizes "Cleanse-CAMP" and "Cleanse-camp" as the same product must do so explicitly; questions test that this canonicalization happens.
- **Multi-classification of the same product**: Cardiag, MACA appear in all three legal-status categories; Diabetech and Cleanse-CAMP each appear in only two; Kidney Cleanse and Pure Psyllium Husk appear in only one. A truth table is the cleanest representation.
- **Section-specific statutory frameworks**: each section maps to a different FD&C Act section and different CFR cite.
- **Multi-step timeline**: 483 issuance (Sept 24, 2025) → firm's first response (Jan 12, 2026) → implicit projected response (≈Feb 9, 2026) → silence → warning letter (Mar 20, 2026) → page-current date (Apr 28, 2026). Five datapoints, several derivable rather than stated.
- **Quoted vs. structured claims**: each bulleted claim is inside double quotes; extractor must preserve original punctuation including ellipses.

## Extraction caveats

- The "Pure Pysyllium Husk" misspelling appears twice in the source. Resist the temptation to "correct" it during extraction — that would be an LLM rewrite.
- Bracketed insertions like "[diabetes]", "[N]atural", and "[heart disease]" are FDA editorial annotations, not part of the firm's labels. They must be preserved as bracketed.
- The "[sic]" annotation on "may helps" indicates the firm's grammatical error in the original label.
- The mid-paragraph mash-up of two label headings into one bullet ("…over-the-counter laxatives…" Your firm's label for your Kidney Cleanse states the following:) is reproduced exactly as the FDA publication shows it. This is a genuine source-shape artifact and a good test of whether the extractor preserves or "tidies" it.
- The "HFP-\nOCE-DietarySupplements@fda.hhs.gov" line-broken email is a real artifact of the FDA page rendering. A naive email extractor may emit two strings; a careful one will join them.

## Attachments / redactions / tables / missing fields

- **Attachments**: none referenced (the Form FDA 483 is referenced but not attached).
- **Redactions**: **none** — this is a notable contrast with `fda_ugly_001` and `fda_ugly_002`. Useful as a "clean" comparison point.
- **Tables**: no formal tables; the four numbered violations and the bulleted label claims are list-structured.
- **Missing fields**: the firm's full response (only the extension-request letter is referenced); the actual product specifications, master manufacturing records, and batch production records (all referenced as "did not establish/prepare").

## Pressure on Prethinker shapes

- **Name canonicalization**: dual-spelling "Cleanse-CAMP/Cleanse-camp" and "Psyllium/Pysyllium" — the schema must either preserve both surface forms or canonicalize with explicit alias tracking.
- **Multi-section product status**: same product appears with different legal statuses in different sections; a truth table is the natural answer.
- **Implicit dates**: the "four weeks" extension request must be added to Jan 12, 2026 to derive an implicit projected response date — Prethinker's deterministic schema should expose this as a derivable quantity, not a stated one.
- **Open-ended consequences**: "including, without limitation, seizure and injunction" — the list of consequences is explicitly non-exhaustive; the schema must mark it as such.
- **Quoted speech preservation**: the source contains many quoted label claims; extractor must keep them verbatim including the firm's original errors.

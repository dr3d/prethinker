# Fixture Notes: sec_8k_material_event_001

## Why this document was chosen

A real, recent (October 2025) Form 8-K from Hamilton Lane Incorporated, signed by the General Counsel and filed via SEC EDGAR. It is a typical corporate disclosure document that exhibits dense legal/structural conventions while remaining short enough to be exercised end-to-end.

## Pressure applied to Prethinker

1. **Corporate/legal document structure.** The 8-K layers cover-page entity identifiers (state of incorporation, Commission File No., IRS EIN, principal office address, phone, former name), Section 12(b) securities-registration table (class, symbol, exchange), four standardized cover check boxes (Rule 425, Rule 14a-12, Rule 14d-2(b), Rule 13e-4(c)), then numbered Item disclosures, then exhibits, then a signature block. A system that flattens this loses the legal meaning of where each statement appears.
2. **Exhibit cross-reference and incorporation by reference.** Item 2.03 contains no independent substantive text — it explicitly incorporates Item 1.01 by reference. Exhibit 10.1 is filed and is also incorporated by reference into Item 1.01, with the explicit caveat that the prose description "does not purport to be complete and is qualified in its entirety by reference to the new agreement." Questions test whether the system can track that Item 2.03's content equals Item 1.01's content, and that the prose description is expressly secondary to Exhibit 10.1.
3. **Effective-date discrimination.** Three distinct dates appear: original agreement (October 20, 2022), Second Amendment execution / event reported (October 1, 2025), and Form 8-K signing/filing (October 6, 2025). The temporal-sequence question forces correct ordering across all three.
4. **Obligation vs disclosure language.** The pre-amendment and post-amendment interest-rate formulas are both stated in "greater of (a)... and (b) 3.00%" form. The conflict_discrepancy question requires the model to extract that the Prime-Rate spread tightens from -1.50% to -1.35% (15 basis points) while the 3.00% floor is unchanged — not to simply replace one with the other.
5. **Redaction and confidentiality discipline.** Exhibit 10.1 carries the footnote "Confidential information in this exhibit has been omitted." The synthesis question requires the model to flag that the public disclosure has been intentionally narrowed.

## Messy features

- **Untagged HTML tables** used purely for layout on the EDGAR cover page (entity table, address table, check-box list, securities-registration table). These are not real data tables but the source carries them verbatim because they encode the legally required structure.
- **Defined-term parentheticals** introduced inline: "(\"HLA\")", "(\"JPM\")", "(\"Second Amendment\")", "(\"2022 Term Loan Agreement\")", "(\"Cap\")". Subsequent references use only the defined terms.
- **Nested (a)/(b) lettering** appearing twice in the same paragraph — once for the pre-amendment rate formula's two prongs, again for the post-amendment formula's two prongs, AND a separate (a)/(b)/(c) list of what the Second Amendment changes. A naïve outline parser will collide these.
- **"°" footnote marker** on Exhibit 10.1 in the exhibit list, with the footnote text appearing on a separate line below the table.
- **Empty check boxes** (four "☐" characters) with no marked selections — a negative-limitation pressure point.
- **Item 9.01(d)** ordering convention: "(d) Exhibits" appears as a subsection inside Item 9.01 with no other (a)–(c) content present.

## Expected hard question types

- Conflict/discrepancy q020 — the rate-formula change requires extracting both pre- and post-amendment numbers and recognizing the unchanged 3.00% floor.
- Conflict/discrepancy q021 — the Item 1.01 → Item 2.03 incorporation by reference is structurally non-obvious.
- Source-attribution q019 — combines the Exhibit 10.1 filing with the "qualified in its entirety" caveat.
- Negative-limitation q024 — requires noticing that the dates being changed are NOT actually stated in the 8-K text.
- Synthesis q025 — combines Items 1.01, 2.03, and 9.01 to produce a faithful summary that captures both the disclosure and the registrant's express limits on it.

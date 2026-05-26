# Authored QA With Answers - procurement_ugly_001

## Questions and Reference Answers

**1. What is the date covered by this contracts announcement?**

**Reference answer.**
February 19, 2026. The date appears in the page title 'Contracts for Feb. 19, 2026' and in the URL path '/contracts-for-feb-19-2026'. The page reports contracts awarded as of that calendar date.

**Source coordinates.** Page title; URL path

**Pressure tags.** date_in_title, url_path_anchor

**2. What is the dollar-value threshold for contracts to appear on this page (per the metadata description)?**

**Reference answer.**
$7.5 million. The page meta-description (HTML head, not body) reads: 'Today's Department of War contracts valued at $7.5 million or more are now live on War.gov.' Only contracts at or above this floor are announced on the daily contracts page; smaller awards are not listed here even if they occurred on the same day.

**Source coordinates.** HTML meta description (not body)

**Pressure tags.** floor_threshold_in_metadata_not_body, implicit_publication_rule

**3. Which contractor in this announcement received the largest single contract by maximum dollar value, and what is that amount?**

**Reference answer.**
Elite PPE LLC. Maximum amount: $763,082,470, for a fixed-price, indefinite-delivery/indefinite-quantity contract for physical fitness gear. The 'maximum' qualifier indicates this is an IDIQ ceiling — actual obligations may be less. Elite PPE LLC is also marked with an asterisk indicating Small Business status.

**Source coordinates.** Defense Logistics Agency section, first entry

**Pressure tags.** maximum_vs_obligated_amount, idiq_ceiling_semantics, small_business_marked

**4. What is the asterisk notation on certain contractor names, and what does it indicate?**

**Reference answer.**
The asterisk (*) appears after the contractor name (e.g., 'Elite PPE LLC,*' and 'Gray Analytics, Inc.,*' and 'Mathtech Inc.,*') as a typographic marker. It is explained by a footnote at the bottom of the announcement: '*Small Business'. The asterisk indicates that the awardee is a Small Business under the Small Business Administration size standards applicable to the procurement. It does not indicate any particular socioeconomic subcategory (8(a), HUBZone, WOSB, SDVOSB, etc.); it is the generic small-business marker only.

**Source coordinates.** Contractor name lines; footnote at end of document

**Pressure tags.** typographic_marker_with_footnote_definition, small_business_designation

**5. The page is hosted on which domain, and what was that agency previously called?**

**Reference answer.**
The page is hosted on war.gov (https://www.war.gov/...). The Department of War was previously known as the U.S. Department of Defense (defense.gov). The renaming/rebranding occurred recently (the metadata description still references 'Department of War' as the canonical name as of this page); legacy 'defense.gov' URLs still appear in some image-host references and footer links. The fixture preserves both names verbatim as they appear.

**Source coordinates.** Source URL; page metadata; references to media.defense.gov in image hosts

**Pressure tags.** agency_renaming_with_legacy_references, dual_domain_artifact, entity_canonicalization_across_renaming

**6. Under which agency heading does the Brasfield & Gorrie award appear?**

**Reference answer.**
Under the bold heading **ARMY**. The Brasfield & Gorrie LLC entry is the first of two Army entries, both contracted through U.S. Army Corps of Engineers (Mobile District for Brasfield & Gorrie; Savannah District for Copper Construction). The U.S. Army Corps of Engineers operates as a sub-component of the Army for procurement purposes.

**Source coordinates.** **ARMY** section, first entry

**Pressure tags.** agency_section_taxonomy, corps_of_engineers_district_subdivision

**7. Where in the document is the statutory authority for sole-source procurement cited, and what is the citation?**

**Reference answer.**
In the Mathtech Inc. (Navy) entry: 'One company was solicited for this sole-source requirement pursuant to the authority set forth in 10 U.S. Code 3204 (a)(1) and one offer received.' The citation is 10 U.S.C. § 3204(a)(1), which governs DoD acquisition source-selection authority for sole-source procurements. This is the only entry citing a statutory authority for sole-source; the other entries that are 'competitive acquisitions' do not cite an authority because none is required.

**Source coordinates.** Navy section, Mathtech entry

**Pressure tags.** sole_source_statutory_citation, uscode_section_paragraph_subparagraph

**8. The Mathtech entry breaks out funds by percentage. In which part of the entry are the three percentages stated, and what do they sum to?**

**Reference answer.**
In the funds-obligation sentence of the Mathtech entry: 'Fiscal 2026 working capital funds (Navy) in the amount of $8,132,019 (77%), FMS funds (France) in the amount of $2,064,760 (20%); and FMS funds (Japan) in the amount of $359,089 (3%), will be obligated at time of award...'. The three percentages: 77% + 20% + 3% = 100%. The dollar amounts: $8,132,019 + $2,064,760 + $359,089 = $10,555,868, which matches the contract total ($10,555,868 firm-fixed-price contract for 123 Intercommunication Systems).

**Source coordinates.** Navy section, Mathtech entry, funds-obligation sentence

**Pressure tags.** multi_source_funding_breakdown, percent_sum_to_100, dollar_sum_reconciliation, mixed_semicolon_comma_separator

**9. Where in the document is the asterisk explained?**

**Reference answer.**
In the final line of the announcement body, immediately before the page footer/subscribe section: '*Small Business'. The footnote sits below the last contract entry (Copper Construction Co. Inc., Vidalia, Georgia) without any preceding label or section heading — just the bare asterisk and the two-word expansion. Easy to miss if scanning entries top-down.

**Source coordinates.** End of contract entries, before subscribe block

**Pressure tags.** footnote_at_document_tail, minimal_explanation_text, unlabeled_footnote

**10. Which awards include a contract or solicitation number identifier in parentheses at the end of the entry, and which do not?**

**Reference answer.**
Of the 8 entries, 7 include a parenthetical identifier at the end: (1) Elite PPE — (SPE1C1-26-D-0026); (2) Boeing Distribution — (SPE4AX-26-D-0005); (3) C.W. Roberts — (FA2823-26-D-0004); (4) DCS Corp. — (FA2377-26-C-B005); (5) Gray Analytics — (HQ0854-26-D-E002 and HQ0854-26-F-E010); (6) Mathtech — (N00383-26-C-LA25); (7) Brasfield & Gorrie — (W91278-26-C-A005); (8) Copper Construction — (W912HN-26-C-A002). 7 of 8 use the parenthetical convention. The Huntington Ingalls entry does NOT include a parenthetical identifier for the modification itself; it instead cites the parent contract being modified ('N00024-25-C-2400') inline in prose. So strictly speaking 8 of 8 entries cite at least one contract number; 7 use the trailing-parenthetical format.

**Source coordinates.** End of each entry; Huntington Ingalls inline citation

**Pressure tags.** trailing_parenthetical_id_format, modification_cites_parent_contract_inline, format_inconsistency_one_entry

**11. List, in source order, every contractor named in the announcement with its city and state.**

**Reference answer.**
(1) Elite PPE LLC — Santa Rosa Beach, Florida; (2) Boeing Distribution Services Defense — O'Fallon, Missouri; (3) C.W. Roberts Contracting Inc. — Tallahassee, Florida; (4) DCS Corp. — Alexandria, Virgina (note: source preserves the typo 'Virgina' missing an 'i'; correct is 'Virginia'); (5) Gray Analytics, Inc. — Huntsville, Alabama; (6) Mathtech Inc. — Falls Church, Virginia; (7) Huntington Ingalls Industries — Pascagoula, Mississippi; (8) Brasfield & Gorrie LLC — Birmingham, Alabama; (9) Copper Construction Co. Inc. — Vidalia, Georgia. Nine contractor name-and-location pairs across the eight contract entries (count is 8 entries, 9 contractor lines because one entry mentions one parent contractor for a modification).

**Source coordinates.** Each entry's opening line

**Pressure tags.** preserved_typo_city_state, nine_lines_eight_entries, us_state_full_names_mixed_with_abbreviations

**12. List the eight contract or solicitation identifiers that appear in parentheses at the end of an entry.**

**Reference answer.**
(1) SPE1C1-26-D-0026 (Elite PPE — DLA contract); (2) SPE4AX-26-D-0005 (Boeing — DLA contract); (3) FA2823-26-D-0004 (C.W. Roberts — AF contract); (4) FA2377-26-C-B005 (DCS Corp. — AF contract); (5) HQ0854-26-D-E002 (Gray Analytics — MDA IDIQ contract); (6) HQ0854-26-F-E010 (Gray Analytics — MDA task order under the same IDIQ); (7) N00383-26-C-LA25 (Mathtech — Navy contract); (8) W91278-26-C-A005 (Brasfield & Gorrie — Army contract); (9) W912HN-26-C-A002 (Copper Construction — Army contract). Nine identifiers across 7 entries (Gray Analytics has two; Huntington Ingalls has none in trailing parens — but cites parent N00024-25-C-2400 in prose). Each follows the DoD PIID format: (4-char activity code) + (FY) + (instrument type letter: D = IDIQ, C = definitive contract, F = task order, R = solicitation) + (4-digit sequence).

**Source coordinates.** End-of-entry parentheticals; Huntington Ingalls inline cite

**Pressure tags.** piid_format_decomposition, instrument_type_letter_d_c_f_r, two_ids_one_entry

**13. List the four named "Using customers" or service-recipient designations across the announcement.**

**Reference answer.**
From the 'Using customers' / 'Using customer' fields explicitly named: (1) DLA / Elite PPE: 'Army, Navy, Air Force, Marine Corps, Space Force, and Coast Guard' (six services — all DoD-funded services plus Coast Guard); (2) DLA / Boeing: 'Army'; (3) [other DLA, AF, MDA, Navy, Army entries do not always use the exact phrase 'Using customer']. Specifically only the two DLA entries use the 'Using customer(s)' phrase explicitly. Other entries imply the customer through the contracting activity (e.g., Naval Sea Systems Command → Navy; U.S. Army Corps of Engineers → Army). Counting only entries that explicitly name the using customer: 2 entries; combined service list across both = 6 distinct services (Army, Navy, Air Force, Marine Corps, Space Force, Coast Guard) all naming Army.

**Source coordinates.** DLA section entries (explicit 'Using customer' field)

**Pressure tags.** explicit_vs_implicit_using_customer, six_service_recipient, joint_use_contract

**14. List the five different contract-type designations used across the eight entries.**

**Reference answer.**
(1) fixed-price, indefinite-delivery/indefinite-quantity (Elite PPE; C.W. Roberts uses just 'indefinite-delivery/indefinite-quantity' with ceiling; Gray Analytics uses 'indefinite-delivery/indefinite-quantity'); (2) fixed-price with economic-price-adjustment, indefinite-delivery/indefinite-quantity (Boeing); (3) cost-plus-fixed-fee (DCS Corp.); (4) firm-fixed-price (Mathtech; Brasfield & Gorrie; Copper Construction); (5) cost-plus-award-fee modification (Huntington Ingalls). Five distinct designations. Three sub-variants of IDIQ (with fixed-price, with EPA, and with ceiling-only). The 'modification' on Huntington Ingalls is technically a contract action type, not a contract type per se; the underlying parent contract type is cost-plus-award-fee.

**Source coordinates.** Each entry's contract-type clause

**Pressure tags.** contract_type_taxonomy_idiq_variants, modification_as_action_type, five_distinct_pricing_structures

**15. List, in source order, the small-business-marked (asterisk) contractors.**

**Reference answer.**
Three asterisk-marked contractors: (1) Elite PPE LLC,* — Santa Rosa Beach, Florida (DLA, physical fitness gear, $763M); (2) Gray Analytics, Inc.,* — Huntsville, Alabama (MDA, systems engineering, $59.5M max); (3) Mathtech Inc.,* — Falls Church, Virginia (Navy, Intercommunication Systems, $10.5M). Of the 8 contract entries, 3 (37.5%) went to designated Small Business awardees per the asterisk notation. Notable: the largest contract in this announcement ($763M to Elite PPE) is a small-business award.

**Source coordinates.** Contractor opening lines with asterisk

**Pressure tags.** asterisk_extraction, set_aside_share_count, largest_award_is_small_business

**16. The Elite PPE LLC contract has a five-year contract with one five-year option period. What is the ordering period end date, and what is the implied maximum total period?**

**Reference answer.**
Ordering period end date: Feb. 16, 2031 (per the entry). This is the end of the five-year BASE contract. The contract also has 'one five-year option period.' If the option is exercised, the total ordering period extends to approximately Feb. 16, 2036 (10 years total from the implied start at award date). The entry does not state an explicit option-exercise date or a 10-year end date — the second 5-year period is conditional on option exercise. So the announced end date (Feb. 16, 2031) represents the base period only; full potential duration is 5 + 5 = up to 10 years.

**Source coordinates.** Elite PPE entry

**Pressure tags.** base_plus_option_period, conditional_full_duration, five_plus_five_max

**17. List, in source order, every completion-or-performance-end date stated in the announcement.**

**Reference answer.**
(1) Elite PPE — Feb. 16, 2031 (ordering period end); (2) Boeing — July 31, 2031 (performance completion); (3) C.W. Roberts — Feb. 18, 2031 (expected completion); (4) DCS Corp. — Feb. 19, 2031 (expected completion); (5) Gray Analytics — Feb. 18, 2031 (ordering period end, from Feb. 19, 2026 through Feb. 18, 2031); (6) Mathtech — August 2027 (month-year only); (7) Huntington Ingalls — December 2027 (month-year only); (8) Brasfield & Gorrie — May 19, 2028 (estimated completion); (9) Copper Construction — March 10, 2028 (estimated completion). Nine end dates across 8 entries (Gray Analytics has a start-and-end pair). Format mix: 5 entries use full Month-Day-Year; 2 use month-year only (less precise); 1 (Gray Analytics) uses a start-and-end range. The Boeing date (July 31, 2031) is the outlier among the 5-year-base contracts, suggesting either a longer base period or different start date.

**Source coordinates.** Each entry's completion-date clause

**Pressure tags.** mixed_date_format_precision, month_year_vs_full_date, outlier_completion_date

**18. The Brasfield & Gorrie award is funded with "Fiscal 2019 Department of Agriculture Buildings and Facilities funds." What is unusual about this combination, and what is the estimated completion date?**

**Reference answer.**
Unusual combination: (a) the contracting activity is the U.S. Army Corps of Engineers (a Department of War / DoD organization), but (b) the funds appropriated are Department of Agriculture (USDA) funds; and (c) the fiscal year of the funds is 2019, which is 7 years prior to the FY 2026 announcement date. The construction is for an Auburn, Alabama laboratory and office buildings — likely a USDA research facility being built by the Corps of Engineers as the executing agent under an interagency agreement. Three-way ugly: cross-agency funding source, cross-fiscal-year obligation, and contracting activity ≠ funding source. Estimated completion date: May 19, 2028.

**Source coordinates.** Army section, Brasfield & Gorrie entry

**Pressure tags.** cross_agency_funding, cross_fiscal_year_obligation, contracting_activity_vs_funding_source

**19. The Gray Analytics contract has an ordering period beginning Feb. 19, 2026. What is the relationship between this start date and the date covered by the announcement page?**

**Reference answer.**
They are the same date. The Gray Analytics contract's ordering period begins 'Feb. 19, 2026, through Feb. 18, 2031' — i.e., the contract starts on the same day the announcement is published. The announcement page is dated 'Contracts for Feb. 19, 2026,' meaning these contracts were awarded on or as of that date. For Gray Analytics specifically, the award date and the contract start date align. The five-year ordering period runs Feb. 19, 2026 → Feb. 18, 2031 (exactly 5 years).

**Source coordinates.** Page title; Gray Analytics entry

**Pressure tags.** award_date_equals_contract_start, exact_five_year_window, same_day_award_and_effective

**20. The Mathtech Inc. award includes Foreign Military Sales components. To which two foreign customers, and what are the percentage shares and dollar amounts?**

**Reference answer.**
Foreign Military Sales (FMS) to: (1) France — 20% — $2,064,760; (2) Japan — 3% — $359,089. Navy (domestic) share: 77% — $8,132,019. Total: 100% — $10,555,868 (matches the headline contract amount). The breakdown reflects funding source AND unit allocation: France gets 23 Intercommunication Systems (out of 123); Japan gets 4; Navy gets 96. Unit share 96/123 ≈ 78.0%; France 23/123 ≈ 18.7%; Japan 4/123 ≈ 3.3% — slightly different from the dollar percentages, indicating the per-unit price differs or other costs are unequally allocated. The dollar breakdown is the authoritative one for funding purposes.

**Source coordinates.** Navy section, Mathtech entry

**Pressure tags.** fms_two_countries, dollar_share_vs_unit_share_drift, domestic_plus_foreign_total

**21. The C.W. Roberts Contracting contract has a $200M ceiling but the announcement states only $1,000 in Fiscal 2026 operations and maintenance funds are obligated at time of award. Explain this dollar mismatch.**

**Reference answer.**
The mismatch is intentional and reflects standard DoD IDIQ-contract accounting. The $200,000,000 is a CEILING value for an indefinite-delivery/indefinite-quantity contract — the maximum cumulative obligation across all task orders that may be issued under the contract over its lifetime. The $1,000 is the actual obligation at time of award — typically the minimum contract guarantee or a nominal sum to make the contract a binding obligation. Task orders subsequently issued under the IDIQ will obligate additional funds against the ceiling as work is needed. The contract type ('indefinite-delivery/indefinite-quantity') signals this structure. The huge ceiling-to-obligated ratio ($200M ÷ $1,000 = 200,000×) is characteristic of IDIQ vehicles.

**Source coordinates.** Air Force section, C.W. Roberts entry

**Pressure tags.** idiq_ceiling_vs_initial_obligation, nominal_obligation_at_award, ceiling_to_obligated_ratio

**22. The Huntington Ingalls Industries entry is described as a "modification" rather than a new award. What contract is being modified, and what action does the modification execute?**

**Reference answer.**
Parent contract being modified: N00024-25-C-2400 (a previously-awarded Navy cost-plus-award-fee contract; the prefix N00024 indicates Naval Sea Systems Command as contracting activity, FY25 as award year, C = definitive contract, sequence 2400). Action: 'to exercise an option for the execution of industrial post-delivery availability for the Landing Helicopter Assault Replacement program.' The $9,708,500 modification value is added to (not the total of) the parent contract; the modification action is the exercise of a pre-negotiated option. Work location and execution remain at Pascagoula, Mississippi (Huntington Ingalls's shipyard). Expected completion: December 2027.

**Source coordinates.** Navy section, Huntington Ingalls entry

**Pressure tags.** modification_vs_new_award, parent_contract_cite, option_exercise_action_type

**23. Compare the contracting activity in the Elite PPE LLC entry (Defense Logistics Agency Troop Support, Philadelphia, Pennsylvania) with the location of the contractor (Santa Rosa Beach, Florida) and the using customers (six services). How many distinct geographic and organizational entities are referenced in this single contract entry?**

**Reference answer.**
Distinct geographic entities (3): (a) Santa Rosa Beach, Florida — contractor's address; (b) Philadelphia, Pennsylvania — contracting activity's location; (c) location of performance is implicit (likely contractor-discretion or various delivery points for IDIQ physical fitness gear). Distinct organizational entities (8+): (a) Elite PPE LLC (the awardee); (b) Defense Logistics Agency Troop Support (the contracting activity, a sub-component of DLA); (c-h) Six using-customer services — Army, Navy, Air Force, Marine Corps, Space Force, Coast Guard. The Coast Guard is operationally under the Department of Homeland Security but procures common items via DoD/DLA contracts. So one contract entry involves: 1 contractor + 1 contracting activity + 6 using customers across 2 federal departments (DoW + DHS) = 8 named organizations and 2+ geographic anchors. Single contract; multi-organization joint use.

**Source coordinates.** DLA section, Elite PPE entry

**Pressure tags.** multi_organization_joint_use, contracting_activity_vs_contractor_vs_customer, coast_guard_under_dhs_uses_dod_contracts

**24. The page title and header reference "Department of War" but the embedded image-host URLs reference "media.defense.gov" and some legacy links go to "defense.gov." What is the relationship between these two names, and what does that imply for entity canonicalization across this document?**

**Reference answer.**
Same agency, two names. The U.S. Department of Defense (DoD) was renamed to the U.S. Department of War (DoW) in 2025/2026 (recent at time of fixture collection). The current canonical name is Department of War; the legacy name is Department of Defense. The document inconsistently uses both: (a) page title, header logo, social handles, page domain (war.gov) use the new name; (b) some image-host URLs (media.defense.gov), legacy Multimedia 'Experience' subdomain links, and the strategic plan PDF link still use the old defense.gov domain. An extractor should canonicalize both names to a single entity but preserve verbatim occurrences in source view. The renaming affects URL canonicalization but does NOT affect the substantive contract content — contracts are with 'the Department' under whatever its current name is.

**Source coordinates.** Page title, URL, embedded image hosts, footer links

**Pressure tags.** agency_renaming_partial_propagation, legacy_domain_artifacts, dual_name_canonicalization

**25. The MDA Gray Analytics entry lists two contract identifiers in parentheses: "HQ0854-26-D-E002 and HQ0854-26-F-E010." What is the difference between the D and F segments of these identifiers, and which represents the umbrella contract vs. the specific task order?**

**Reference answer.**
Per the DoD PIID format (Procurement Instrument Identifier per FAR/DFARS): the 9th character (after the second hyphen) is the instrument-type letter. 'D' = Definitive contract / indefinite delivery contract (IDIQ umbrella). 'F' = Task order (issued against a parent IDIQ). So: (a) HQ0854-26-D-E002 is the umbrella IDIQ contract (maximum $59,525,000, awarded by Missile Defense Agency in FY 2026, sequence E002); (b) HQ0854-26-F-E010 is the initial task order issued under that IDIQ (task order amount $8,800,000). The entry confirms: 'A task order in the amount of $8,800,000 is being issued.' The shared 'HQ0854-26' prefix identifies the contracting activity (HQ0854 = Missile Defense Agency, Huntsville) and fiscal year (26 = FY2026); the letter and 4-character sequence after distinguishes them. Two IDs for one contract+task-order pair.

**Source coordinates.** MDA section, Gray Analytics entry

**Pressure tags.** piid_instrument_type_letter_d_vs_f, idiq_plus_task_order_pair, shared_prefix_different_instrument

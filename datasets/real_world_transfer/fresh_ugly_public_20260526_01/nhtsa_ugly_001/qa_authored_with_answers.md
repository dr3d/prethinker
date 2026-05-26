# Authored QA With Answers - nhtsa_ugly_001

## Questions and Reference Answers

**1. What is the NHTSA Campaign Number for this recall?**

**Reference answer.**
26V229. The number appears in three places: the top-right header line of page 1 ('26V229'), the labeled field 'NHTSA Campaign Number: 26V229,' and as part of the source PDF filename (RCAK-26V229-1960.pdf).

**Source coordinates.** Page 1 header (top-right); 'NHTSA Campaign Number' field; PDF filename

**Pressure tags.** repeated_identifier, header_vs_labeled_field

**2. What is the date of the NHTSA letter, and what is the manufacturer's report date?**

**Reference answer.**
NHTSA letter date: April 15, 2026 (top-left of page 1). Mfr's Report Date: April 10, 2026 (labeled field in the structured block). The two are five days apart; the manufacturer notified NHTSA on April 10 and NHTSA acknowledged on April 15.

**Source coordinates.** Page 1 top-left header; 'Mfr's Report Date' field

**Pressure tags.** two_distinct_dates, header_vs_labeled_field

**3. What is the Potential Number of Units Affected?**

**Reference answer.**
94,760. This is the recall's potential population (vehicles believed subject to the recall, not necessarily the number actually defective).

**Source coordinates.** 'Potential Number of Units Affected' field

**Pressure tags.** comma_in_number, potential_vs_actual_population

**4. What is the Subject line of the letter?**

**Reference answer.**
'Fuel Leak at Pipe Connection.' Appears immediately above the salutation 'Dear Shaun Austin.'

**Source coordinates.** Subject line, page 1

**Pressure tags.** letter_format

**5. Who signs the letter on behalf of NHTSA, and what is their title?**

**Reference answer.**
Alex Ansley, Chief, Recall Management Division, Office of Defects Investigation, Enforcement. The four-line title block places Alex Ansley as Chief of the Recall Management Division within the Office of Defects Investigation, which sits within Enforcement at NHTSA.

**Source coordinates.** Page 2 closing signature block

**Pressure tags.** nested_organizational_title, four_line_title_block

**6. In which field block of the letter is the component identified, and what does the full component string read?**

**Reference answer.**
The 'Components:' labeled field, between 'NHTSA Campaign Number' and 'Potential Number of Units Affected.' The full string is: 'FUEL SYSTEM, GASOLINE:DELIVERY:HOSES, LINES/PIPING, AND FITTINGS.' Note the hybrid delimiter scheme: colons separate hierarchy levels (FUEL SYSTEM, GASOLINE → DELIVERY → HOSES, LINES/PIPING, AND FITTINGS) and commas separate items within a level. The leading 'FUEL SYSTEM, GASOLINE' is one item (with embedded comma), not two.

**Source coordinates.** 'Components' field

**Pressure tags.** hybrid_delimiter_colon_and_comma, embedded_comma_in_item, hierarchical_component_path

**7. Which paragraph identifies Genesis' (Hyundai's) own internal number for this recall?**

**Reference answer.**
The 'Remedy:' paragraph: 'Genesis' number for this recall is 033G.' This is the manufacturer-internal recall identifier and is distinct from the NHTSA Campaign Number (26V229).

**Source coordinates.** 'Remedy' paragraph

**Pressure tags.** manufacturer_internal_identifier, dual_id_schemes

**8. Where in the letter does the NHTSA Washington, DC address appear?**

**Reference answer.**
Inserted mid-paragraph between the 'Genesis customer service at 844-340-9741' sentence and the 'Genesis' number for this recall is 033G' sentence, within the Remedy section. The two address lines ('1200 New Jersey Avenue SE' and 'Washington, DC 20590') appear as a right-aligned letterhead-style insertion that interrupts the flowing prose. This is a PDF page-footer artifact bleeding into the body text; treat as letterhead, not as Genesis's address.

**Source coordinates.** Mid-Remedy paragraph (right-aligned letterhead artifact)

**Pressure tags.** page_footer_artifact_in_body, letterhead_bleed, right_aligned_intrusion

**9. The letter cites three statutory or regulatory provisions related to manufacturer obligations. In which paragraphs do they appear and what do they cite?**

**Reference answer.**
(1) The paragraph beginning 'Please be reminded that under...' cites 49 U.S.C. § 30112(a)(3) — the prohibition on selling defective vehicles after NHTSA notification. (2) The next paragraph beginning 'As stated in...' cites 49 U.S.C. § 30118(f) — the eight-quarterly-plus-three-annual reporting requirement. (3) The same paragraph then cites '573.7' — a reference to 49 C.F.R. § 573.7, the regulation that operationalizes the quarterly reporting cadence. The CFR citation is given as a bare section number ('573.7') without the title-and-part prefix.

**Source coordinates.** Reminder paragraphs after the 'Please be reminded of the following requirements:' header

**Pressure tags.** multiple_statutory_citations, bare_section_number_citation, usc_vs_cfr_citation_styles

**10. Where in the letter is the manufacturer-side individual contact named, and what email address is given?**

**Reference answer.**
In the closing paragraph immediately before the signature block: 'Hyundai Motor America's contact for this recall will be Emily Smith who may be reached by email at emily.c.smith@dot.gov.' The contact name is Emily Smith. The email address is emily.c.smith@dot.gov. The @dot.gov domain belongs to the U.S. Department of Transportation, not to Hyundai Motor America (see cross-section question 25).

**Source coordinates.** Closing paragraph, page 2

**Pressure tags.** manufacturer_contact_with_government_email, internal_inconsistency_preserved

**11. List, in source order, the four Make/Model/Year entries in the Makes/Models/Model Years block.**

**Reference answer.**
(1) GENESIS/GV80/2021-2025; (2) GENESIS/G80/2021-2025; (3) GENESIS/GV70/2022-2026; (4) GENESIS/G90/2023-2025. Source order is GV80 → G80 → GV70 → G90. All four entries are Genesis-brand. The block uses slash-delimited fixed-position triples.

**Source coordinates.** Makes/Models/Model Years block

**Pressure tags.** slash_delimited_triple_format, model_year_ranges_per_model

**12. List the four Genesis vehicles named in the Problem Description, in source order, with their model-year ranges.**

**Reference answer.**
(1) GV70 — 2022-2026; (2) G90 — 2023-2025; (3) G80 — 2021-2025; (4) GV80 — model years NOT stated in the Problem Description (the prose runs 'GV70, ... G90, ... G80, and GV80 vehicles' with the GV80 year range omitted). To recover GV80's range one must consult the Makes/Models/Model Years block above: 2021-2025. The Problem Description also reorders the models relative to the Makes/Models block (GV70, G90, G80, GV80 vs. GV80, G80, GV70, G90).

**Source coordinates.** 'Problem Description' paragraph

**Pressure tags.** model_year_omitted_for_one_item, reordered_relative_to_structured_block, cross_field_recovery_required

**13. List the customer-facing phone numbers given in the letter, with their associated organizations and any TTY variant.**

**Reference answer.**
(1) Genesis customer service: 844-340-9741. No TTY variant given. (2) NHTSA Vehicle Safety Hotline: 1-888-327-4236; TTY 1-888-275-9171. The two numbers serve distinct purposes: Genesis handles owner inquiries about the specific recall (033G/26V229), while the NHTSA hotline is for general consumer safety inquiries. The TTY number is paired only with the NHTSA hotline.

**Source coordinates.** 'Remedy' paragraph (Genesis); 'Notes' paragraph (NHTSA hotline)

**Pressure tags.** dual_phone_numbers, tty_paired_only_with_one, two_purposes_two_contacts

**14. List the two NHTSA-internal identifiers for this recall and the one Hyundai/Genesis-internal identifier.**

**Reference answer.**
NHTSA-internal: (a) NHTSA Campaign Number 26V229; (b) PDF report filename identifier RCAK-26V229-1960 (visible in the source URL/filename: the '-1960' suffix appears to be a NHTSA internal sequence number; the '26V229' segment matches the campaign number). Hyundai/Genesis-internal: 033G ('Genesis' number for this recall is 033G'). Three identifiers in three different namespaces for the same underlying recall.

**Source coordinates.** Header (26V229); 'NHTSA Campaign Number' field; 'Remedy' paragraph (033G); source URL/filename (RCAK-26V229-1960)

**Pressure tags.** multi_namespace_identifiers, internal_external_id_pairing

**15. List the four April 2026 dates that appear in the letter, with what each one refers to.**

**Reference answer.**
(1) April 10, 2026 — Mfr's Report Date (date the manufacturer notified NHTSA of the recall). (2) April 11, 2026 — date VINs became searchable on NHTSA.gov. (3) April 15, 2026 — date of the NHTSA acknowledgement letter. (4) No fourth April date appears in the letter — the fourth date in the document timeline is June 8, 2026 (planned owner-notification mailing). The sequence April 10 → April 11 → April 15 spans 5 days from manufacturer report to NHTSA letter; VIN searchability was activated on day 2 of that interval.

**Source coordinates.** 'Mfr's Report Date' field; 'Remedy' paragraph; Page 1 top-left header date

**Pressure tags.** date_sequence_reconstruction, question_premise_check, three_april_dates_not_four

**16. When are owner notification letters expected to be mailed, and what is the sequence of date events preceding that mailing?**

**Reference answer.**
Owner notification letters are expected to be mailed June 8, 2026. The preceding date sequence is: (1) April 10, 2026 — manufacturer reports recall to NHTSA; (2) April 11, 2026 — VINs become searchable on NHTSA.gov; (3) April 15, 2026 — NHTSA issues acknowledgement letter (the source document); (4) At least 5 days before mailing (i.e., on or before June 3, 2026) — manufacturer is required to submit a draft owner notification letter to NHTSA; (5) June 8, 2026 — owner notification letters mailed.

**Source coordinates.** 'Remedy' paragraph; 'Please be reminded of the following requirements' paragraph; 'Mfr's Report Date' field; header date

**Pressure tags.** date_chain_reconstruction, deadline_derived_from_relative_offset

**17. According to the reporting-requirements paragraph, when is the first quarterly status report due?**

**Reference answer.**
The first of eight consecutive quarterly status reports is due within one month (30 days) after the close of the calendar quarter in which notification to purchasers occurs. Owners are expected to be notified on June 8, 2026 (Q2 2026). Q2 2026 closes June 30, 2026. The first quarterly report would therefore be due on or before July 30, 2026. The letter expresses this as a relative deadline ('within one month after the close of the calendar quarter in which notification to purchasers occurs') without providing an absolute date.

**Source coordinates.** 'As stated in 49 U.S.C. § 30118(f)...' paragraph

**Pressure tags.** relative_deadline, calendar_quarter_arithmetic, no_absolute_date_provided

**18. When is the first of three consecutive annual status reports due?**

**Reference answer.**
On or before 1 year after the eighth quarterly report was submitted. The letter does not provide an absolute date; it states the obligation in relative terms. If the first quarterly is due on or before July 30, 2026 (per question 17) and the subsequent seven quarterlies fall at the close of each quarter thereafter, the eighth quarterly would be due in roughly Q2 2028. The first annual would then be due about Q2 2029 — but the letter itself only fixes the relative offset, not the absolute date.

**Source coordinates.** 'As stated in 49 U.S.C. § 30118(f)...' paragraph

**Pressure tags.** relative_deadline_chain, two_step_arithmetic, no_absolute_date_provided

**19. The letter imposes a deadline for submitting copies of the draft owner notification letter "to this office." What is that deadline?**

**Reference answer.**
No less than five days prior to mailing the letter to the customers. The owner notification letters are expected to be mailed June 8, 2026, so the draft would be due to NHTSA on or before June 3, 2026. Additionally, copies of final owner notification letters and any subsequent follow-up letters are required to be submitted to NHTSA no later than 5 days after they are originally sent.

**Source coordinates.** 'You are required to submit a draft owner notification letter...' paragraph

**Pressure tags.** relative_deadline, five_days_before_and_after, two_distinct_obligations

**20. What is the stated consequence of the defect to consumers, and what remedy is the dealer obliged to provide?**

**Reference answer.**
Consequence: 'A fuel leak increases the risk of a fire.' (Consequence field — one sentence.) Remedy: 'Dealers will inspect and tighten, or replace the fuel pipe as necessary, free of charge.' (Remedy paragraph.) The remedy has two possible dealer actions — inspect-and-tighten OR replace — with the selection conditioned on whether tightening is sufficient. Both options are free of charge to the owner.

**Source coordinates.** 'Consequence' field; 'Remedy' paragraph

**Pressure tags.** consequence_and_remedy_pair, conditional_remedy_action, free_of_charge_obligation

**21. Under 49 U.S.C. § 30112(a)(3), what is illegal once the manufacturer has notified NHTSA of a safety defect, and what exception applies?**

**Reference answer.**
Illegal acts: 'to sell, offer for sale, import, or introduce or deliver into interstate commerce, a motor vehicle or item of motor vehicle equipment that contains a safety defect once the manufacturer has notified NHTSA about that safety defect.' Exception: 'This prohibition does not apply once the motor vehicle or motor vehicle equipment has been remedied according to the manufacturer's instructions.' Five prohibited acts: sell, offer for sale, import, introduce, deliver into interstate commerce.

**Source coordinates.** 'Please be reminded that under 49 U.S.C. § 30112(a)(3)...' paragraph

**Pressure tags.** statutory_obligation, five_act_list, exception_clause

**22. Identify all reporting cadence obligations imposed on the manufacturer (quarterly count, annual count, and total reporting period implied).**

**Reference answer.**
Quarterly: 8 consecutive quarterly status reports, the first due within one month after the close of the calendar quarter in which notification to purchasers occurs. Annual: 3 consecutive annual status reports, the first due on or before 1 year after the eighth quarterly was submitted. Total implied reporting period: roughly 8 quarters (~2 years) of quarterly reporting + 3 years of annual reporting = ~5 years of post-recall reporting from the start of the first quarter after consumer notification. The letter cites 49 U.S.C. § 30118(f) as the statutory basis and 49 C.F.R. § 573.7 as the regulatory implementation.

**Source coordinates.** 'As stated in 49 U.S.C. § 30118(f)...' paragraph

**Pressure tags.** multi_phase_reporting_cadence, two_to_five_year_obligation_chain, statutory_and_regulatory_basis

**23. Compare the Problem Description model-year ranges against the Makes/Models/Model Years block. Identify any discrepancy in coverage or in the model-year for GV80.**

**Reference answer.**
The Problem Description omits the GV80 model-year range. The prose reads: 'Genesis 2022-2026 GV70, 2023-2025 G90, 2021-2025 G80, and GV80 vehicles.' Three of four models have explicit year ranges; GV80 has no year range attached. To recover GV80's range, one must consult the Makes/Models/Model Years block (GENESIS/GV80/2021-2025). Beyond the omission, the year ranges that are stated are consistent between the two locations (GV70: 2022-2026 in both; G90: 2023-2025 in both; G80: 2021-2025 in both). The Problem Description also reorders the models (GV70, G90, G80, GV80) relative to the structured block (GV80, G80, GV70, G90). Coverage is the same four models in both locations.

**Source coordinates.** 'Makes/Models/Model Years' block; 'Problem Description' paragraph

**Pressure tags.** range_omission_for_one_item, reordered_lists_same_coverage, cross_field_recovery_required, internal_consistency_check

**24. The letter is addressed to Hyundai Motor America in Fountain Valley, CA, but the products under recall are Genesis-brand vehicles. How does the letter handle the brand/parent relationship, and where does this surface in the document structure?**

**Reference answer.**
The letter handles the brand/parent relationship by treating Hyundai Motor America as the legal entity ('Hyundai Motor America's notification,' 'Hyundai Motor America's contact') and Genesis as the brand under that entity. The parenthetical 'Hyundai Motor America (Genesis) is recalling certain Genesis... vehicles' in the Problem Description makes the relationship explicit. The Makes/Models/Model Years block uses 'GENESIS' as the make (brand level) rather than 'HYUNDAI.' Customer service is via Genesis ('Genesis customer service at 844-340-9741'), and the manufacturer-internal recall ID is Genesis's ('Genesis' number for this recall is 033G'). Three distinct surfaces: legal entity (Hyundai Motor America), brand (Genesis), and customer-facing organization (Genesis). The salutation ('Dear Shaun Austin') uses a Hyundai Motor America addressee.

**Source coordinates.** Salutation; 'Problem Description' parenthetical; 'Makes/Models/Model Years' block; 'Remedy' paragraph; closing manufacturer-contact paragraph

**Pressure tags.** brand_vs_legal_entity, parent_subsidiary_canonicalization, multi_surface_entity_appearance

**25. The named manufacturer-side contact ("Hyundai Motor America's contact for this recall will be Emily Smith") is given an email address at the @dot.gov domain. Is this consistent with the description? Discuss what the document does and does not establish.**

**Reference answer.**
It is internally inconsistent on its face. The description 'Hyundai Motor America's contact for this recall' attributes the contact to the manufacturer, but @dot.gov is the U.S. Department of Transportation domain (NHTSA's parent). A genuine Hyundai/Genesis contact would normally have a @hyundai.com, @genesis.com, or similar private-sector email. The document does NOT establish: (a) whether Emily Smith is a NHTSA staffer assigned as the case officer for this recall (which the @dot.gov address would suggest), (b) whether the email address is a typo or template-fill error, or (c) whether the description 'Hyundai Motor America's contact' is itself a misnomer for 'NHTSA's assigned point-of-contact for this manufacturer recall.' An extractor should preserve both the description and the email verbatim and tag the document with an internal-inconsistency flag rather than infer one over the other.

**Source coordinates.** Closing paragraph before signature block

**Pressure tags.** internal_inconsistency_preserved, manufacturer_contact_with_government_email, no_silent_correction

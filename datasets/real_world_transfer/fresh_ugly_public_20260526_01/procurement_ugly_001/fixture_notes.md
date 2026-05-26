# Fixture Notes — procurement_ugly_001

## Source

- Public URL: https://www.war.gov/News/Contracts/Contract/Article/4410058/contracts-for-feb-19-2026
- Document type: Daily contracts announcement from the U.S. Department of War (formerly Department of Defense). Reports contracts valued at $7.5 million or more awarded on a specific calendar day, organized by component (DLA, Air Force, MDA, Navy, Army, etc.).
- Date covered: February 19, 2026
- Collected: 2026-05-26 (UTC)
- Note: 8 distinct contract entries across 5 component agency sections. The metadata description states the $7.5M floor; smaller awards are not announced here.

## Why messy

- **Agency renaming partially propagated.** Department of Defense → Department of War (rename ~2025/2026). Page is hosted on war.gov; some legacy URLs and image-host references still use defense.gov. The same entity is referred to by two names across the document. Entity canonicalization must handle both.
- **Compendium format.** 8 contract entries across 5 component-agency sections (DLA, Air Force, MDA, Navy, Army). Each entry is self-contained with its own contractor, award amount, type, performance period, and contract number.
- **Asterisk-as-small-business marker.** Three contractors (Elite PPE, Gray Analytics, Mathtech) are marked with a trailing asterisk after the company name. A single-line footnote at the document tail explains: "*Small Business". Easy to miss; minimal label.
- **Floor threshold in metadata, not body.** "$7.5 million or more" is stated only in the HTML meta-description tag, not in the body. Without reading the metadata, the floor is invisible.
- **Multi-namespace identifier scheme (PIID format).** DoD PIIDs follow a fixed structure: 4-char activity code + 2-digit fiscal year + instrument-type letter + 4-char sequence. Activity codes: SPE = DLA; FA = Air Force; HQ = MDA; N = Navy; W = Army. Instrument letters: R = solicitation; D = IDIQ; C = definitive contract; F = task order. Two IDs in one entry (Gray Analytics: D-contract + F-task-order).
- **IDIQ ceiling vs. obligated amount.** Multiple entries have a "maximum" or "ceiling" dollar value (e.g., $763M, $200M, $59.5M) but only a small dollar amount obligated at award (e.g., $1,000 for C.W. Roberts). The IDIQ structure is invisible without contract-vehicle awareness.
- **"Using customer" vs. "contracting activity" distinction.** The using customer is who receives the goods/services; the contracting activity is who manages the procurement. Different organizational entities. Some entries explicitly name "Using customer(s)"; others imply it through the contracting activity.
- **Six-service joint-use contract.** Elite PPE / DLA: using customers are Army, Navy, Air Force, Marine Corps, Space Force, and Coast Guard. The Coast Guard is operationally under DHS but procures DoD-managed items. Single contract spans two federal departments.
- **Multi-source funding with percentages.** Mathtech entry: 77% Navy + 20% France FMS + 3% Japan FMS = 100%, total $10,555,868. Dollar amounts and percentages must reconcile. Unit allocation (96/23/4 of 123 systems) drifts slightly from dollar percentages.
- **Foreign Military Sales (FMS) components.** Awards may include foreign customers funded through FMS cases. France 20%, Japan 3% in the Mathtech contract.
- **Cross-agency funding source.** Brasfield & Gorrie / U.S. Army Corps of Engineers entry uses "Fiscal 2019 Department of Agriculture Buildings and Facilities funds." The contracting activity is DoD; the funding source is USDA. Cross-agency interagency-agreement structure.
- **Cross-fiscal-year obligation.** Same entry uses FY 2019 funds for a FY 2026 award. The 7-year-old appropriation must still be available (continuing appropriation or no-year funds).
- **Sole-source statutory authority cite.** Mathtech entry cites 10 U.S.C. § 3204(a)(1) as the statutory authority for the sole-source procurement. Only entry with explicit statutory cite.
- **Preserved typo "Virgina".** DCS Corp. entry: "Alexandria, Virgina" (missing 'i'). Correct spelling is Virginia.
- **Contract type taxonomy.** Five distinct designations: fixed-price IDIQ, fixed-price-with-EPA IDIQ, cost-plus-fixed-fee, firm-fixed-price, cost-plus-award-fee. Multiple IDIQ sub-variants.
- **Modification vs. new award.** Huntington Ingalls entry is a $9.7M modification to a previously-awarded parent contract (N00024-25-C-2400), exercising an option. No trailing parenthetical ID; the parent ID is cited inline in prose.
- **Base + option period structure.** Multiple awards have "X-year base contract with one X-year option period." Conditional max-duration: 5 + 5 = up to 10 years.
- **Date format inconsistency.** Mix of "Feb. 16, 2031" (abbreviated month + day + year), "May 19, 2028" (similar), "August 2027" (month-year only, no day). Less-precise dates for some completion estimates.
- **Number of offers received.** Each competitive entry states the number of offers received: "one offer was received" (C.W. Roberts), "two received" (Copper), "three responses received" (Boeing), "three received" (Brasfield & Gorrie), "six offers were received" (DCS Corp.). One sole-source entry says "one offer received" (Mathtech) after one company solicited. Competition density varies.
- **Funds expiration qualifiers.** "Funds will not expire at the end of the current fiscal year" (Mathtech, Huntington Ingalls). Default DoD funds expiration not stated for other entries.
- **Procurement-vehicle prose variation.** Variously: "competitive acquisition" / "open competitive acquisition" / "competitively procured via publication on the Governmentwide Point of Entry website" / "Bids were solicited via the internet" / "competitively procured via... through Nimble Options for Buying Layered Effects" (MDA-specific contract vehicle).
- **Award-vs-announcement date alignment.** Page title says Feb. 19, 2026; some entries explicitly have ordering periods starting Feb. 19, 2026 (Gray Analytics). Same-day award and effective start.
- **Sub-component identification.** "Defense Logistics Agency Troop Support" vs. "Defense Logistics Agency Weapons Support" — two sub-components of DLA in adjacent entries. "U.S. Army Corps of Engineers, Mobile District" vs. "U.S. Army Corps of Engineers, Savannah District" — two districts of USACE.

## What shapes are pressured

- Agency renaming with partial propagation across URLs and text.
- Compendium with multiple sub-agency sections.
- Asterisk typographic marker with footnote definition.
- Floor threshold in metadata not body.
- PIID format decomposition (activity / FY / instrument-type / sequence).
- IDIQ ceiling vs. initial obligation mismatch.
- Using customer vs. contracting activity distinction.
- Multi-service joint-use contract.
- Multi-source funding with percentage reconciliation.
- FMS components with foreign-customer breakouts.
- Cross-agency funding source.
- Cross-fiscal-year obligation (FY 2019 funds for FY 2026 award).
- Sole-source statutory authority citation.
- Preserved typo in city/state.
- Five-way contract type taxonomy.
- Modification vs. new award distinction.
- Base + option period conditional duration.
- Mixed date format precision.
- Offers-received count tracking.
- Funds expiration qualifiers.
- Procurement-vehicle prose variation.
- Same-day award and effective start.
- Sub-component (DLA Troop / Weapons; USACE Mobile / Savannah) disambiguation.
- Dollar share vs. unit share drift in multi-source funding.
- Asterisk count as set-aside share metric (3 of 8 entries = 37.5%).
- Largest contract awarded to a Small Business (counterintuitive given ceiling magnitude).
- Two-ID parenthetical for IDIQ + task-order pair.
- Footnote at document tail with minimal explanation text.

## Attachments, redactions, tables, missing fields

- Attachments: none. The contracts page is self-contained; underlying solicitation documents (SPE1C1-25-R-0130, etc.) and award letters are separate documents not extracted here.
- Redactions: none.
- Tables: none — entries are prose paragraphs separated by bold agency headers.
- Missing fields: NAICS codes (not stated in this announcement; PIID encodes activity, not NAICS); PSC codes; specific small-business socioeconomic subcategory (asterisk indicates generic Small Business only, not 8(a)/HUBZone/WOSB/SDVOSB); precise day-level dates for some completion estimates; using-customer field for entries that don't explicitly state it; place-of-performance for the Elite PPE IDIQ (location not stated since deliveries vary).

## Extraction caveats

- Treat "Department of War" and "Department of Defense" as ONE entity (post-renaming and legacy names). The current canonical name is Department of War; preserve verbatim occurrences of both.
- The $7.5M floor threshold is in the HTML meta-description, not the body. An extractor reading body text alone will not see this rule.
- Asterisk after a contractor name signals Small Business per the document-tail footnote. Do not extract the asterisk as part of the name; bind it to the small-business attribute.
- "Maximum" / "ceiling" dollar values are IDIQ contract maxima; "obligated at time of award" is the initial obligation. These differ by orders of magnitude. Preserve both.
- PIID identifiers should be decomposed: (4-char activity) + (FY) + (instrument-type letter) + (4-char sequence). D = IDIQ; C = definitive; F = task order; R = solicitation. Two PIIDs in one entry (Gray Analytics) means one IDIQ + one task order.
- "Using customer" is the recipient service; "contracting activity" is the procurement office. They are different entities.
- DLA Troop Support and DLA Weapons Support are different sub-organizations of DLA. USACE Mobile District and USACE Savannah District are different districts of the same Corps. Do not deduplicate.
- The Brasfield & Gorrie contract is funded by USDA (FY 2019) but contracted by USACE; this is a cross-agency interagency-agreement structure. Preserve both the funding-source agency and the contracting-activity agency.
- "Virgina" in DCS Corp. is a preserved typo. Do not silently correct to "Virginia" in extraction; flag it.
- Preserve "August 2027" and "December 2027" as month-year-only dates without inventing a specific day.
- Coast Guard is named as a using customer despite being under DHS (not DoW). The DoW/DHS boundary does not prevent DLA from procuring for the Coast Guard.
- Foreign Military Sales (FMS) breakdowns are funding shares; the unit-allocation share (96 Navy / 23 France / 4 Japan = 123 total) is a separate metric and may not exactly match dollar percentages.
- The Huntington Ingalls entry is a modification, not a new contract. Preserve the modification action type AND the parent contract number (N00024-25-C-2400).
- "Bids were solicited via the internet" is the Army Corps' phrasing; other entries use "competitively procured via publication on the Governmentwide Point of Entry website" (SAM.gov) for the same concept. Do not deduplicate to a single vehicle.
- The Gray Analytics ordering period starts on the announcement date (Feb. 19, 2026). Other entries may or may not align this way.
- 10 U.S.C. § 3204(a)(1) is the sole-source statutory authority cited for the Mathtech award. The other competitive entries do not require an authority cite.

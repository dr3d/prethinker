# Fixture Notes — other_ugly_003

## Source

- Public URL: https://www.cpsc.gov/Warnings/2026/CPSC-Warns-Consumers-to-Stop-Using-Sperax-Walking-Pads-and-Treadmills-Immediately-Due-to-Risk-of-Serious-Injury-from-Fall-Burn-and-Fire-Hazards
- Collected: 2026-05-24 (UTC)
- Document type: CPSC unilateral Product Safety Warning (not a recall). URL path `/Warnings/2026/...` distinguishes it from the more common `/Recalls/2026/...` pattern.
- Page first issued: April 16, 2026 (Product Safety Warning Date)
- Page identifier: Product Safety Warning Number 26-415

## Why messy

- **Recall vs. Warning category distinction.** This is a *Warning*, not a *Recall*. The page labels its fields with "Product Safety Warning Date" and "Product Safety Warning Number." The URL path is `/Warnings/2026/` not `/Recalls/2026/`. A reader who has only seen CPSC Recall pages may extract this as a recall and misattribute the absence of remedy fields to data sparsity.
- **Firm refusal of recall.** The page states "The importer Quanzhou Wentelai Import and Export Trading Co., Ltd., d/b/a Sperax, has refused to agree to an acceptable recall." This is the *reason* the action is a Warning rather than a Recall. The refusal is undated and the page does not describe what an "acceptable recall" would have entailed.
- **Section 6(b) firm objection.** The page contains the statutorily required Section 6(b) manufacturer comment. CPSC fulfills this with the minimal sentence "The company objects to this press release." That sentence is *both* the entirety of the firm's comment as reproduced on the page *and* the standardized template language. No substantive firm position is reproduced.
- **Two-category incident structure with asymmetric reporting.** The Description paragraph reports two distinct incident categories (stability failures, thermal incidents) with separate counts. The labeled "Incidents/Injuries:" field repeats *only* the thermal-incident numbers. An extractor that takes the "Incidents/Injuries" field as authoritative will silently drop the stability-failure totals (201 reports, 66 falls/injuries, at least one concussion). This is a structural reliability hazard.
- **Lower-bound qualifiers.** "at least 66 falls or injuries" and "at least one concussion" are floors, not exact counts. "201 reports" and "573 reports" are exact CPSC awareness counts. "four reports of minor burns" has no "at least" qualifier.
- **Importer / d/b/a structure.** "Quanzhou Wentelai Import and Export Trading Co., Ltd., d/b/a Sperax" embeds an importer-of-record with a doing-business-as alias. The Sperax *brand* is what consumers see on the products; the legal entity is Quanzhou Wentelai. Brand-vs-legal-entity canonicalization is required.
- **Ordering divergence.** Description model list (Pro, Q1, RM-01, RM-02) differs from carousel order (Q1, Pro, RM-02, RM-01). Both reference the same four-model set; neither is canonical.
- **"Include" vs. "including".** The model list uses "Affected models include..." which is more inclusive-sounding than "are." In practice the Warning enumerates a closed set of four models; the page does not assert other models are or are not affected. The "Sold At" list uses "including," which signals an open list.
- **Missing typical recall fields.** No Units, no price, no manufacturing date range, no sales date range, no consumer remedy (refund/repair/replacement), no recalling-firm contact. These absences are structural and tied to the firm's recall refusal.
- **Brand-name homonym hazard.** "Sperax" is both the product brand name and a known token in cryptocurrency contexts (Sperax USD). The page context — walking pads and treadmills — must be preserved to prevent extractor disambiguation errors.
- **Repeated content.** The model number location, the disposal directive, the "Sold At" platform list, and the manufactured-in country all appear in two places: once inside the Description paragraph and once in a labeled field (or, in some cases, a separate boldface restatement). Deduplication is required without losing the structural-vs-prose distinction.
- **Time field.** Footer says "8 a.m. - 5.30. p.m. ET" — note the malformed time string ("5.30." rather than "5:30").
- **Open count on report timeliness.** CPSC reports it is "aware of" 201 and 573 reports respectively. The page does not give the time window over which these reports were collected or the latest report date.

## What shapes are pressured

- Document-class disambiguation (Warning vs. Recall) based on URL path and labeled-field names.
- Reason-of-action attribution (firm refusal → Warning, not Recall).
- Section 6(b) statutory citation parsing and minimum-comment fulfillment.
- Two-category incident extraction with asymmetric labeled-field coverage (Description-only vs. labeled-field).
- Lower-bound vs. exact count distinction within a single document.
- Importer / d/b/a / brand entity canonicalization.
- Carousel-order vs. prose-order list reconciliation.
- "Include" vs. "including" semantics for closed vs. open lists.
- Structural absence detection (no Units, no price, no remedy).
- Repeated-content deduplication while preserving structural-vs-prose distinction.
- Brand-name homonym disambiguation by domain context.
- Reporting-window inference (none stated; "aware of" is unbounded in time).

## Attachments, redactions, tables, missing fields

- Attachments: four product image files (Sperax Model Q1, Pro, RM-02, RM-01) referenced via the page carousel; not extracted as files.
- Redactions: none.
- Tables: none; flat label-value field structure with embedded Description paragraph.
- Missing fields on this page: total units sold; price; manufacturing date range; sales date range; recall date (does not exist — this is a Warning); consumer remedy (refund / repair / replacement — none offered); firm contact for consumers; date of firm refusal; date range during which the 201 and 573 reports were collected; identification of which model variants were involved in which incident category; whether the firm has been referred for further enforcement; case or docket number for any related Commission proceeding.

## Extraction caveats

- Treat this document as a *Product Safety Warning*, not a recall. Do not assert a recall has occurred.
- Bind the "26-415" identifier to the *Warning Number* slot, not a *Recall Number* slot.
- Preserve "has refused to agree to an acceptable recall" as a firm position; do not infer that no firm action will ever occur.
- Bind the Section 6(b) compliance to the single sentence "The company objects to this press release." Do not infer additional firm comment content.
- Distinguish the two incident categories. Bind 201 reports / 66+ falls / 1+ concussion to *stability-related failures*; bind 573 reports / 4 minor burns to *thermal incidents*. Do not aggregate.
- The "Incidents/Injuries:" labeled field is incomplete relative to the Description. Extract both categories from the Description rather than relying on the labeled field.
- Treat the "Sold At" platforms list as illustrative (open) because of the "including" introducer.
- Treat the model list {Pro, Q1, RM-01, RM-02} as a four-element closed set. Order is presentational.
- The legal entity is Quanzhou Wentelai Import and Export Trading Co., Ltd.; the brand/d/b/a is Sperax. Canonicalize.
- "Sperax" disambiguation: this document concerns treadmills/walking pads, not the cryptocurrency token of the same name.
- No remedy is asserted because none exists. Do not infer refund or replacement entitlements.
- "At least 66" and "at least one concussion" are lower bounds. "201", "573", and "four" are stated counts but the awareness window is unspecified.
- The footer time string "5.30. p.m." should be preserved verbatim if extracted (typo of "5:30").

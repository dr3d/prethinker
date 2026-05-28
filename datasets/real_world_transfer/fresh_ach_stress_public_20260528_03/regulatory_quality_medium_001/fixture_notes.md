# fixture_notes — regulatory_quality_medium_001

## Why this source was chosen
A fresh 2025 FDA CGMP warning letter (not the AACE letter used in the prior batch) that cleanly stages the "systemic quality vs specific decision vs vendor/contractor" pressure. It cites three independent CGMP areas and also carries upstream-contamination and regulatory-status threads, giving genuine competing readings of where responsibility sits.

## Why the ACH sensitivity target is medium
The systemic-quality reading (h1) is supported by three independent pillars — incoming-component identity testing (e1), production/process control of the water system (e3), and quality-unit oversight (e4) — plus an explicit "systemic flaws / six-system audit" framing (e8). Because there are three pillars, the winner survives any single-row removal. But it is not low-sensitivity: a tempting vendor-fault reading (h2) has real pull because the hazards (methanol, DEG/EG) originate in supplier-provided raw materials (e5). The "firm is responsible despite supplier COAs" bridge (e2) is what keeps responsibility with the firm; remove it and the supplier reading gains meaningfully, even though the process-control and quality-unit pillars still hold. That "survives one row but weakens meaningfully, two-row removal creates serious uncertainty" behavior is the medium definition.

## Tempting wrong hypothesis
Vendor/supplier fault (h2). The contamination hazards are upstream, and the firm did rely on supplier COAs — so a reader can wrongly conclude the suppliers are responsible. The letter forecloses this: the firm must test incoming components and establish the reliability of supplier analyses; it cannot offload that duty.

## Off-axis true hypothesis
Regulatory-status problem (h4). The unapproved-new-drug, misbranding, and drug-listing-inactivation findings (e7) are true and serious, but they answer a different question (approval/labeling/listing status), not the CGMP-adulteration responsibility theory the ACH question asks about.

## Direct / partial / off-axis rows
- Direct to h1 (systemic quality): e1 (component testing), e3 (process control), e4 (quality unit), e8 (systemic-flaws framing).
- Causal bridge against h2: e2 (firm responsible despite COAs).
- Direct to h2 (vendor): e5 (upstream hazard).
- Partial to h3 (specific decision): e3 (the water-system choice, viewed narrowly).
- Off-axis to h4: e7 (unapproved drug / misbranding / listing).

## Double-edged rows
- e5 (upstream DEG/EG and methanol hazard) supports the vendor reading on its face but is used by the FDA to justify the firm's own testing duty (h1).
- e6 (CAPA to "secure supply chains" / qualify suppliers) acknowledges the supply-chain dimension (h2) yet frames supplier qualification as the firm's own corrective duty (h1).
- e3 (water system) is both a systemic process-control pillar (h1) and the single finding most amenable to a narrow "one bad decision" reading (h3).

## Extraction quirks
- The letter is heavily redacted with "(b)(4)" markers, especially around the water system ("(b)(4) water," "(b)(4) (No hose)"); these are preserved exactly and are not load-bearing for any QA answer.
- Lengthy "In response to this letter, provide:" remediation bullet lists are retained in condensed bracketed form in source.md to preserve readability; all violation findings themselves are verbatim.
- Two distinct violation families appear (CGMP/adulteration vs unapproved-drug/misbranding/listing); the ACH question concerns only the adulteration/CGMP theory, so the second family is the off-axis material.
- Two signatories from two different CDER offices reflect the two violation families.

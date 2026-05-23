# Fixture Notes: fda_warning_or_recall_001

## Why this document was chosen

This is a public FDA Warning Letter to Granules India Limited (MARCS-CMS 697115 / Warning Letter 320-25-48), dated February 26, 2025, signed by the Director of FDA's Office of Manufacturing Quality (CDER/OC/OMQ). It is a real enforcement document — not a synthetic fixture — that exhibits the messy regulatory-document patterns Prethinker needs to handle in transfer.

## Pressure applied to Prethinker

1. **Regulatory source attribution.** Statements in the letter come from multiple distinct voices: FDA investigators (observations during inspection), the firm (Form 483 response on September 27, 2024), and FDA's own subsequent judgment ("Your response is inadequate"). Questions force the system to disambiguate which voice asserted what.
2. **Requirement vs allegation vs finding.** The letter mixes regulatory requirements (21 CFR citations), factual allegations (bird droppings, swab residues, TNTC microbial contamination, 15+ waste bags of torn records), the firm's responsive assertions, and FDA's adequacy judgments. The system must not collapse these into a single voice.
3. **Identifier extraction under redaction noise.** Product, component, equipment, and bowl-size specifics are uniformly redacted as `(b)(4)`. Identifiers that ARE present (FEI 3004097901, MARCS-CMS 697115, Warning Letter 320-25-48, recipient name, contact ATTN, signer) must be extracted accurately while the system resists hallucinating the redacted material.
4. **Corrective-action status.** The letter establishes that the firm responded but FDA judged each numbered violation's response inadequate. This is a non-terminal status — the firm is given 15 working days to respond again — and requires careful temporal/state reasoning.
5. **Negative / not-stated discipline.** Common readers may expect the letter to name affected products and lot numbers (it does not), to indicate whether an Import Alert was placed (it does not state one was), and to list violations exhaustively (it explicitly disclaims this). The fixture asks negative-limitation questions targeting each of these.

## Messy features

- **Bolded numbered violation headings with embedded regulatory citations** (21 CFR 211.67(b), 211.58, 211.68(a)) in inline parenthetical form.
- **Repeated `(b)(4)` redactions** in the middle of sentences and adjacent to numeric units (e.g., "the (b)(4)μ high efficiency particulate air (HEPA) filters"), breaking simple noun-phrase patterns.
- **Footnote with superscript marker** (¹) referencing the GDUFA III Commitment Letter and Post-Warning Letter Meeting eligibility, with a fiscal-year range (FYs 2023-2027) that is easy to mis-extract as a single year.
- **Two distinct date layers**: the letter signature date (February 26, 2025) and the FDA page's "Content current as of" date (March 4, 2025). These look similar but are different dates with different sources.
- **Three "Your response is inadequate" verdicts**, one per violation, each preceded by the firm's response and each justified differently by FDA. A model that fuses them loses the discriminating detail.
- **MACO/cross-contamination quantitative dispute**: the firm's MACO calculation argument and FDA's rebuttal (denominators inconsistent with bowl size; MACO does not apply where cleaning has not been performed) is a quantitative conflict_discrepancy question.
- **A separate "Concerns with CGMP records" section** outside the three numbered violations, easily missed if the model treats the numbered list as the full set of findings.

## Expected hard question types

- Conflict/discrepancy questions (q020, q021, q022) — require pairing firm assertions with FDA rebuttals.
- Synthesis question (q025) — combines the three numbered CGMP violations with the data-integrity concerns and the adulteration finding to characterize the quality system.
- Negative-limitation questions (q023, q024) — require recognizing that the letter declines to name products/lots and explicitly disclaims an all-inclusive list.
- Source-attribution question (q019) — asks what the firm's own response asserted (reserve sample results confirmed cross-contamination), not what FDA concluded.

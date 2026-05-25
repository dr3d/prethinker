# Fixture Notes: fda_ugly_001

## Public Source

- URL: https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/medical-products-laboratories-inc-721916-04092026
- Document: FDA Warning Letter to Medical Products Laboratories, Inc., MARCS-CMS 721916, Warning Letter 320-26-61, dated April 9, 2026.
- Collected: 2026-05-24 (this batch).
- Public domain (U.S. federal government publication, FDA enforcement record).

## Why this document is messy

- Heavy (b)(4) redactions throughout (FOIA Exemption 4 — confidential commercial information). Lot numbers, product identifiers, microbiological values, recall dates, customer names, stability temperature ranges, and shelf-life expiry are all redacted. Some sentences contain four to six (b)(4) tokens.
- Mixed structural elements: a definition-list header block (delivery method / product / recipient / issuing office), an inline product enumeration that runs for ~12 lines, four numbered CGMP violations each with prose and bulleted CAPA requests, italicized sub-headings inside violations, an inline footnote at the end, and two signature blocks.
- Numbered violations cite four distinct CFR sections; the firm is also charged separately under FD&C Act §§ 301(d) and 505(a) for unapproved new drugs, signed by a different FDA official.
- The same redacted lot identifiers reappear across multiple violations (microbiological, stability OOS, complaint investigations), implying cross-section linkage that the public reader cannot fully resolve.

## What shapes this document pressures

- **Tables/lists with redactions**: the bullet list of contaminated lots is the canonical "shape-only" test — the structure carries information (three distinct lots, two of which had both TAMC and TYMC = TNTC) even though every identifier is redacted.
- **Multiple separate dates** with different roles: inspection start/end, Form 483 response, warning letter signature date, post-warning page-update date, and a redacted recall date.
- **Named entities with offices and roles**: Mr. Elliot Stone (President/CEO of recipient), Andrew Haack (FDA ATTN), Francis Godwin (Director, Office of Manufacturing Quality), Tina Smith (Director, Office of Unapproved Drugs & Labeling Compliance). Two signers map to two distinct violation classes.
- **Obligations & deadlines**: a 15-working-day response window, plus per-violation CAPA submission requirements (microbiological remediation, PPQ timeline, retrospective OOS review, stability remediation).
- **Cross-section joining**: the unapproved-new-drugs paragraph at the front and the labeling-claims section at the back must be joined to map product → claim; the recall reference in Violation #1 cannot be resolved without acknowledging redaction; the two signers must be mapped to their respective sections by office name.

## Extraction caveats

- All (b)(4) redactions in the source are preserved verbatim and inline. The source page uses bold markup around the (b)(4) tokens in places; bolding was not preserved on every occurrence in source.md because the visual emphasis is a rendering artifact rather than substantive content — the (b)(4) token itself is what is informationally present.
- The FDA web page wraps the letter body in a definition-list at top (`Delivery Method:` / `Product:` / `Recipient:` / `Issuing Office:`); this was rendered as a compact header block to keep the field labels visible.
- The signature line "/S/" is preserved on its own line above each signer's name block.
- Hyperlinked URLs in the original page (to FDA guidances) are preserved as literal URLs in the markdown.
- A single footnote anchored from the response-deadline sentence is preserved with `*[1]*` markers.

## Attachments / redactions / tables / missing fields

- **Attachments**: none referenced (no Form 483 attached; the firm's Nov 6, 2025 response is referenced but not appended).
- **Redactions**: pervasive (b)(4) — see above. At least 25 distinct redaction tokens in the body.
- **Tables**: one bulleted three-row "table" of contaminated lots under Violation #1.
- **Missing fields** (from the perspective of a complete public record): the recall date, recalled product, and affected lots; the identity of the customer (b)(4) with whom the firm has a quality agreement; numeric stability temperature/expiry data; and the firm's actual response procedures (referenced as committed-to-revise but not provided).

## Pressure on Prethinker shapes

- **Logical-form extraction with redaction tokens**: the schema must treat `(b)(4)` as a sentinel value, not a literal string, when extracting `lot_id`, `product_name`, `recall_date`, etc. This is a good test of "absence-of-evidence" handling.
- **Coreference across distant sections**: same redacted `lot (b)(4)` token reappears in Violation #1 (microbiological) and Violation #3 (stability OOS); a naïve extractor may merge them, but they are not necessarily the same lot.
- **Multi-signatory attribution**: the two signature blocks each authorize distinct violation classes — a single-signer assumption would lose information.
- **Qualified answers**: at least four questions (Q12, Q15, Q22, Q24) require the answer to explicitly acknowledge redaction or incompleteness rather than guess.

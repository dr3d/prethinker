# Fixture notes — fda_warning_ugly_001

## Why this document was chosen

This is a current (April 2026) FDA CDER warning letter to a US drug manufacturer, with the full spread of features the task spec calls for: identified recipient name/title/address, two named signatories with distinct titles, four numbered CGMP violations citing four distinct CFR sections, a separately structured "Unapproved New Drug Violations" section enumerating 13 named drug products with indications, an inspection date range, a prior firm response that is critiqued, a 15-working-day response deadline, a specific reply email address, an FEI number, an attention-line investigator name, and a long footnoted reference to GDUFA III.

## Messy features

- **Two distinct date types** that look similar but mean different things: the warning-letter date (April 9, 2026), the inspection window (September 29 – October 16, 2025), the firm's Form 483 response date (November 6, 2025), and the "content current as of" date (April 14, 2026).
- **Two co-signatories** from different offices in the same Center: Francis Godwin (OMQ) and Tina Smith (OUDLC) — both within CDER's Office of Compliance, but with distinct office titles. Easy to conflate.
- **Two reference numbers** for the same letter: `MARCS-CMS 721916` (page header) and `320-26-61` (body header). They are not the same number system.
- **Heavy (b)(4) redactions** throughout the microbiology section: the failing lots, the (b)(4) treatment process, the failing CFU/g number, the customer name, the recall date, the recall lots, the stability temperature ranges. Anything that asks for these specifics is unanswerable from the source.
- **Thirteen named drug products** in the unapproved-new-drug list, with overlapping sulfacetamide/sulfur formulations at different strengths (8%/4%, 9%/4%, 9.8%/4.8%, 10%/5%) and three Plexion-branded products. Easy to attribute the wrong indication to the wrong strength.
- **Four CFR citations**, each with its own narrative: 211.113(a), 211.100(a), 211.192, 211.166(a). The "investigations" violation (211.192) has three sub-sections — Finished Drug Product Microbiological Testing, Stability Assay, Complaint Investigations — that each describe a different deficiency.
- **The recipient is a contract manufacturer.** The letter explicitly invokes the "contractor as extension of the manufacturer" doctrine and references a (b)(4) customer with a quality agreement. The recipient's argument that the customer directed certain conduct (formulation changes, stability range labeling, discontinuing a process validation) is repeatedly noted as not absolving the firm — a reasoning trap if a question asks who is responsible.
- **The reply destination is split**: the email address is CDER-OC-OMQ-Communications@fda.hhs.gov but the FEI and "ATTN" investigator (Andrew Haack) must be on the reply. The 15-working-day deadline is footnoted with a GDUFA III post-warning meeting eligibility note.

## Prethinker design pressure

- Signatory-vs-issuing-office vs metadata MARCS-CMS number disambiguation (multiple authoritative identifiers for the same letter).
- Violation-to-CFR-citation grouping (four numbered violations to four CFR sections, with one violation having three sub-deficiencies).
- Product-to-indication mapping across thirteen products with overlapping name stems and percent strengths.
- Date order joins: inspection window → 483 issuance (implicit) → firm response (Nov 6, 2025) → warning letter (Apr 9, 2026).
- Negative/exception reasoning: "did the firm's response address X?" — the letter repeatedly states the response is "inadequate in that..." which is the only ground truth for what the response failed to cover.
- Redaction reasoning: questions that target a (b)(4) field should be refused (or answered "not recoverable from source") rather than guessed.

## Source caveats

The fda.gov page is the official, published warning letter. No content was added, paraphrased, or summarized into source.md.

## Local normalization note

The incoming `qa.md` contained both questions and authored reference answers using `q001`-style markers. It was preserved as `qa_authored_with_answers.md`; the canonical `qa.md` was regenerated from `qa_questions.jsonl` as numbered, questions-only Markdown for `scripts/run_domain_bootstrap_qa.py`. Reference answers remain isolated in `oracle.jsonl` for after-the-fact scoring only.

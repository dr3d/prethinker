# Fixture notes — fda_warning_ugly_002

## Why this document was chosen

Different product area from `fda_warning_ugly_001` (dietary supplements vs prescription drugs), different FDA issuing center (Human Foods Program vs CDER), different recipient profile (small dietary-supplement firm with one owner-signatory recipient vs a contract drug manufacturer with two FDA signatories), and a more complex multi-section product/violation matrix. The letter spans three distinct legal theories — unapproved new drugs, misbranded drugs, and adulterated dietary supplements — applied to overlapping but not identical subsets of the same six products.

## Messy features

- **Six products, three overlapping subsets:**
    - All six products (Cardiag, Diabetech, Cleanse-CAMP, MACA, Kidney Cleanse, Pure Pysyllium Husk) are cited under "Unapproved New Drugs."
    - Only three (Cardiag, Diabetech, MACA) are cited under "Misbranded Drugs."
    - A different three (Cardiag, Cleanse-camp, MACA 1000 mg) are cited under "Adulterated Dietary Supplements" / CGMP. Subset reasoning is a hard pressure.
- **The same product appears with different name forms** in different sections: "Cleanse-CAMP" in the unapproved-new-drug section vs "Cleanse-camp" in the CGMP citations. "MACA" vs "MACA 1000 mg." "Pure Psyllium Husk" vs the firm's "Pure Pysyllium Husk." All preserved from the source.
- **Three distinct CFR/USC regimes** in one letter: section 201/301/505 of the FD&C Act (unapproved new drugs), section 502(f)(1) (misbranded), 21 CFR Part 111 (dietary supplement CGMP) including specific subparts (111.70(e), 111.205(a), 111.255(a), Subpart N).
- **Two different website domains in play**: the recipient's firm is "Nupack Inc." but its product site is www.unitechusk.com. Easy to conflate firm name and website domain.
- **Two different reply email addresses** appear in the source: a personal addressee `Lauren.Crivellone@fda.hhs.gov` and a group address `HFP-OCE-DietarySupplements@fda.hhs.gov`. Plus a postal address: 5001 Campus Drive, College Park, MD 20740-3835.
- **The recipient's response is partial**: the firm replied January 12, 2026 only to request a four-week extension, and never followed up. Questions about whether the firm responded must distinguish "requested extension" from "substantively responded."
- **MACA's claims include an erectile-dysfunction claim with a "[sic]" annotation** ("MACA may helps [sic] to reduce erectile dysfunction.") preserved from the source.
- **Two reference numbers**: `MARCS-CMS 722113` (header) and `CMS #722113` (body header).

## Prethinker design pressure

- Set-difference reasoning over overlapping product subsets ("which products are cited in all three violation types?" vs "which are cited only in one?").
- Joining a quoted claim to a product to a section. The Cardiag-vs-Diabetech-vs-MACA differentiation depends on attribution of each indented bullet to the heading sentence that precedes it.
- Disambiguating spelling variants ("Cleanse-CAMP" / "Cleanse-camp") as the same product without merging with adjacent products.
- Firm vs domain: Nupack Inc. (firm name) and unitechusk.com (website) are not the same string but refer to the same operation.
- Conditional reasoning on the firm's response: only requested an extension; did not provide substantive response. A question phrased as "did the firm respond?" has a defensible nuanced answer in the source.
- Citation specificity: each CGMP violation maps to its own 21 CFR section, including one that maps to a Subpart (N) rather than a numbered section.

## Source caveats

The fda.gov page is the official published warning letter. Spelling errors and bracketed annotations (`[N]atural`, `[sic]`, `[diabetes]`, `[heart disease]`) are preserved as in the original.

## Local normalization note

The incoming `qa.md` contained both questions and authored reference answers using `q001`-style markers. It was preserved as `qa_authored_with_answers.md`; the canonical `qa.md` was regenerated from `qa_questions.jsonl` as numbered, questions-only Markdown for `scripts/run_domain_bootstrap_qa.py`. Reference answers remain isolated in `oracle.jsonl` for after-the-fact scoring only.

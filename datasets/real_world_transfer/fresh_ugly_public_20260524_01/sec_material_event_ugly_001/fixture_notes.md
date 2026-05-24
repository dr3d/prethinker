# Fixture notes — sec_material_event_ugly_001

## Why this document was chosen

A short, clean Form 8-K Item 1.01 (Entry into a Material Definitive Agreement) for an **amendment to a prior agreement** rather than a fresh agreement. Amendments are good Prethinker stress tests because they layer new dates and consideration on top of an unchanged underlying contract — a reasoner has to keep the original Agreement and the First Amendment separate while combining them where the Amendment explicitly modifies a term. The filing is also short enough (under 700 words of substantive text) that all the QA can be defensibly answered from the source.

## Messy features

- **Two distinct dollar amounts at very different scales:** $11,168,864 total purchase price (unchanged), $250,000 earnest-money-now-extension-fee. They play completely different roles and should not be summed or substituted.
- **Earnest money flips role:** the $250,000 was originally earnest money; the Amendment redefines it as a non-refundable extension fee that "shall not be credited against the purchase price at closing, regardless of whether the closing occurs or the Agreement is terminated." Three subtle pieces of meaning: it's now non-refundable; it's no longer credited at closing; and the new treatment survives termination. A reasoner that defaults to "earnest money is applied to purchase price" gets this wrong.
- **Three dates plus a fourth filing date:** Original Agreement effective March 12, 2026; original closing April 15, 2026; new closing May 22, 2026; Date of Report April 13, 2026; signature/filing date April 16, 2026. Multiple ways to confuse these.
- **Date of Report (April 13, 2026) vs Signature Date (April 16, 2026):** the 8-K is dated based on the event (April 13), but the document was actually signed and filed three days later (April 16). The four-business-day rule shows up implicitly here.
- **Multi-state parties:** Nevada corporation (registrant), Texas LLC (counterparty), Texas property (subject), Arizona corporate address. Four states implicated; only one (Texas) for the property and the counterparty.
- **Trading symbol is N/A in the filing** even though the entity's URL slug on EDGAR ("cbdw") suggests a CBDW ticker. The cover-page table truthfully reports N/A; identifying that the filing itself says N/A — not the popularly-used external ticker — is its own piece of pressure.
- **Asymmetric one-way obligation:** the financial-verification clause runs only from Company to Seller, only upon Seller's written request, only between April 13 and the closing date. Three constraints on the trigger; one-way obligation; bounded time window.
- **Underlying transaction described in one phrase only:** "real property and related assets located in Angelina County, Texas" — no acreage, no parcel ID, no description of what the assets are. The fixture should not invent specifics.
- **Emerging growth company indicator is checked YES.** Easy to skip past.
- **No exhibits.** The body does not include or reference an Item 9.01 exhibit list — the First Amendment itself is summarized but not filed as an exhibit to this 8-K (at least not in the body).
- **Signatory titled "Chief Executive Officer," not CEO:** Austen Lambrecht, with the full title spelled out. Preserved verbatim.

## Prethinker design pressure

- Amendment vs underlying agreement: the new closing date supersedes the old; the purchase price is unchanged; the earnest money's treatment is changed. Three different relationships to the prior contract — supersession, persistence, and modification — in one short item.
- Conditional-fee logic: "shall not be credited against the purchase price at closing, regardless of whether the closing occurs or the Agreement is terminated." Two scenarios (closes or terminated); same outcome (fee retained). A reasoner must extract the universal quantifier.
- Dollar-amount distinction: $11,168,864 vs $250,000 — neither is a function of the other, and the $250,000 is not a deposit toward the $11,168,864 anymore.
- Date arithmetic: closing extended by 37 days (April 15 → May 22, 2026). The Amendment doesn't state the number of days; a reasoner must compute it (or refuse to compute when not asked).
- Trigger-precondition tracking: financial-verification obligation runs only on Seller's written request and only between April 13, 2026 and the closing date.
- Multi-state party disambiguation: Nevada corp, Texas LLC, Texas property, Arizona HQ.
- Date-of-report vs signature/filing-date distinction: a real piece of 8-K mechanics that questions can exploit.

## Source caveats

The 8-K does not disclose the original earnest money's deposit instrument or escrow holder, the structure of the underlying transaction beyond what's quoted, or what happens to the $250,000 if the Company chooses not to close (other than that the fee is "fully earned" by Seller and not credited or refunded). Those details are outside this document.

## Local normalization note

The incoming `qa.md` contained both questions and authored reference answers using `q001`-style markers. It was preserved as `qa_authored_with_answers.md`; the canonical `qa.md` was regenerated from `qa_questions.jsonl` as numbered, questions-only Markdown for `scripts/run_domain_bootstrap_qa.py`. Reference answers remain isolated in `oracle.jsonl` for after-the-fact scoring only.

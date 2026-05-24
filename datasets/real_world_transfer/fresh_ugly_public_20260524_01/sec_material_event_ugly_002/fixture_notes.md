# Fixture notes — sec_material_event_ugly_002

## Why this document was chosen

A Form 8-K under Item 5.02 (departure of officers and directors, appointment of officers and directors, compensatory arrangements) is one of the busiest single-event 8-K item types: it routinely combines several distinct human-resource events in one filing with several distinct compensation arrangements. This Pool Corporation filing announces a CEO transition (Arvan out, Watwood in), a Board role change (Stokely from Chair to Executive Chair), an interim appointment (Whalen as interim lead independent director), and a Board size reduction (from nine to eight implied) — all effective the same day. It also defers Item 5.02(e) compensation detail to a later amendment, exercises the "furnished, not filed" distinction in Item 7.01, and is signed by the CFO rather than the (just-departing) CEO. The fixture deliberately contrasts with sec_material_event_ugly_001 (1606 Corp.), which is an Item 1.01 contract-amendment filing.

## Messy features

- **Four named individuals with overlapping first names:** Peter D. Arvan (outgoing CEO/director), John B. Watwood (incoming President/CEO), John E. Stokely (existing Chair → Executive Chair), David G. Whalen (interim lead independent director). Two "Johns." A reasoner that disambiguates only by first name will fail.
- **Three compensation amounts at very different scales and structures:**
    - Watwood salary: $800,000 per year.
    - Watwood equity grant: ~$1,750,000, split 50/50 between restricted shares and performance-based shares.
    - Stokely Executive-Chair fee: $50,000 per month.
    - Whalen interim lead-independent-director fee: $5,000 per month.
    Two of those are monthly, two are annual or one-time; one is split into two equal halves. Easy to confuse units (monthly vs annual) and easy to attribute the wrong amount to the wrong person.
- **Watwood bonus is a target, not a guarantee:** 125% of base salary "upon the achievement of certain performance metrics." A reasoner that reports it as guaranteed extra income overstates it.
- **Stokely's three-role history with three dates in one sentence:** on the Board since 2000, lead independent director since 2003, Chair of the Board since 2017. Three different roles, three different start dates, packed into one sentence. The Executive-Chair role is *new* as of May 4, 2026 — a fourth role on the same body.
- **"Transition Effective Time" is reused** for both Arvan's departure (cease to serve and resign) and Watwood's appointment. They are the same instant. Easy to imagine a gap that isn't there.
- **Item 5.02(e) deferral:** the company explicitly says it will file an *amendment* to this 8-K within four business days after Mr. Arvan's separation-compensation information becomes available. The 8-K cannot tell us his severance; the 8-K/A will. This is a common Item 5.02 pattern and questions can target what's *missing* from the present document.
- **Item 7.01 "furnished, not filed":** the press release at Exhibit 99.1 is *furnished* under Item 7.01, with the boilerplate paragraph stating it is not deemed "filed" for Section 18 purposes and is not incorporated by reference. The Form of Employment Agreement at Exhibit 10.1, by contrast, is filed. The distinction matters for liability and for the question of which exhibits are subject to which standards.
- **Exhibit 10.1 is incorporated by reference,** not re-attached: it points to "Exhibit 10.3 to the Company's Quarterly Report on Form 10-Q filed on October 29, 2025." Questions about exhibit handling can exploit this.
- **Signatory is the CFO, not the CEO:** Melanie M. Hart, Senior Vice President and Chief Financial Officer. This is because the CEO transitioned on the same day the 8-K was signed. A reasoner that defaults to "8-Ks are signed by the CEO" gets this wrong.
- **Watwood's career history names four employers in one paragraph:** Motion Industries (2008 → 2026, ending as SVP sales and operations), SMC Corporation of America, Applied Industrial Technologies, and (effective Jan 2026) Pool Corporation as EVP. The new CEO role then begins May 4, 2026. A reasoner needs to track that Pool Corp hired him as EVP in January 2026 and promoted him to CEO four months later.
- **Board size reduced to eight directors** rather than re-stated explicitly with the old number. Inference: the Board had nine seats before Arvan's resignation took effect. The 8-K does not explicitly say "from nine to eight"; it says "reduced the size of the Board to eight directors."
- **Other contractual boilerplate cleanly disposed of:** no arrangements/understandings, no family relationships, no related-party transactions (with one carve-out — except as disclosed in the 2026 Proxy Statement filed on March 26, 2026). The carve-out reference is a Prethinker test of "what's the exception?"

## Prethinker design pressure

- Multi-person reference resolution under shared first names and shared institution (the Board): which "John" got which role?
- Compensation arithmetic across mixed units (monthly vs annual; total vs target; one-time vs recurring).
- Equity-grant decomposition: $1,750,000 = $875,000 in restricted shares + $875,000 in performance-based shares (50/50 of approximately $1.75M).
- Bonus as target vs guaranteed amount: 125% of $800,000 = $1,000,000 *if* metrics are achieved — not a fixed line item.
- Role-history reasoning for Stokely (three start dates → four roles when counting Executive Chair).
- Missing-information awareness: Item 5.02(e) Arvan-separation compensation is *explicitly not yet disclosed*; the 8-K commits to a follow-up 8-K/A.
- "Filed" vs "furnished" distinction: Exhibit 99.1 is furnished; Exhibits 10.1 and 104 are filed; only Exhibit 10.1 is incorporated by reference from a prior 10-Q.
- Date and entity reasoning: Watwood joined Pool Corp in January 2026 as EVP; promoted to CEO May 4, 2026 — a Pool Corp tenure of about four months at the time of his CEO appointment.
- Implicit-from-explicit: "Board reduced to eight directors" implies one director left to bring it from nine to eight (consistent with Arvan).
- Signatory identity: CFO signs because CEO position just transitioned. Easy to over-attribute.

## Source caveats

- The 8-K does not disclose Mr. Arvan's severance, separation payments, vesting acceleration, or non-compete arrangements. Item 5.02(e) information is deferred to a future 8-K/A. The fixture's QA does not pretend that information is in the source.
- The 8-K does not disclose Mr. Watwood's prior compensation at Motion Industries, SMC Corp of America, or Applied Industrial Technologies.
- The 8-K does not specify the vesting schedule, performance metrics, or measurement period for either the bonus or the equity grant beyond what is quoted.
- The Section 12(b) cover-page table and the registrant's name/state-of-incorporation/file-number cover-page table were not preserved in the page extraction; the registrant ("Pool Corporation, a Delaware corporation") is established only by the Item 5.02 body and the signature block. See `provenance.md`.

## Local normalization note

The incoming `qa.md` contained both questions and authored reference answers using `q001`-style markers. It was preserved as `qa_authored_with_answers.md`; the canonical `qa.md` was regenerated from `qa_questions.jsonl` as numbered, questions-only Markdown for `scripts/run_domain_bootstrap_qa.py`. Reference answers remain isolated in `oracle.jsonl` for after-the-fact scoring only.

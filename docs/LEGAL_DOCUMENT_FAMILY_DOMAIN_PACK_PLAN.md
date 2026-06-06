# Legal Document-Family Domain Pack Plan

This is the research redirect after the legal-authority verifier work.

The current `legal_authority_verification_v1` lane is useful plumbing, but it is
not a legal domain pack. Its predicates are generic citation mechanics:
resolution, authority metadata, quote checks, pin-cite locality, and explicit
abstention for proposition support. That verifier can sit underneath a legal
domain, but it does not by itself show that Prethinker can compile a specific
family of legal documents.

The next differentiated research question is:

```text
Can a closed, lens-scoped predicate pack stabilize the recurring skeleton
anatomy of one narrow legal document family, while citation verification remains
only a deterministic underlay?
```

## Candidate Family

Use **AI citation sanction or correction orders** as the first candidate family.

Why this family:

- It is directly connected to the real-world "AI cannot verify AI" failure mode.
- The repo already has incoming source material and review attempts around
  Mata v. Avianca, Park/Kim, and Wadsworth/Walmart-style sanction/correction
  records.
- The recurring anatomy is more domain-specific than generic citation checking:
  who filed, what was represented, which authority failed, what verification
  duty was breached, what the court did, and what remedy or sanction followed.
- The boundary is honest: proposition-level legal support still abstains unless
  independently reviewed against authority text.

Other possible families, deferred unless this one fails quickly:

- immigration appellate decisions;
- securities class-action complaints;
- patent claim-construction briefs;
- Rule 11 / sanctions orders not limited to AI citation failures.

## Underlay Versus Domain

The citation verifier may provide underlay rows such as:

- `legal_citation_mention/5`
- `legal_authority_resolution/5`
- `legal_authority_metadata_check/5`
- `legal_quote_claim/5`
- `legal_quote_span_match/5`
- `legal_pin_cite_check/5`
- `legal_verification_abstention/4`

Those rows answer "does this cited authority mechanically check out?" They do
not answer the domain question.

The domain pack should add closed predicates for sanction/correction-order
anatomy, for example:

- `legal_ai_citation_failure_order/5`
- `legal_filing_actor/5`
- `legal_defective_authority/5`
- `legal_verification_duty/5`
- `legal_court_finding/5`
- `legal_sanction_or_remedy/5`
- `legal_correction_action/5`
- `legal_failure_mode/5`
- `legal_domain_abstention/5`

These names are candidates only. They must be closed by the same domain-predicate
process used for FDA/SEC/NTSB packs: compact value domains, lens-scoped offered
predicate sets, registered signatures, atom-shape gates, redaction replay,
typed-plan replay where queryable, and N>=3/support>=2 before claim use.

## First Experiment

1. Treat the existing known-sanction packet attempts as source context, not as
   imported fixtures.
2. Pick one seed order and define a tiny closed schema for skeleton anatomy only:
   filing actor, defective citation/authority, failure mode, court response,
   sanction/remedy, and abstention boundary.
3. Compile the seed under the closed schema for N>=3 same-condition runs.
4. Promote only rows surviving support>=2 with:
   - zero unregistered signatures;
   - zero prose-shaped atoms;
   - zero source/display prose routing;
   - zero false verified citation-underlay rows;
   - no proposition-support verification claim.
5. Transfer to one unlike sanction/correction order and report the hard-clean
   rows plus abstention/failure classes.

## Stop Conditions

Stop this family, or report it as a negative result, if:

- the pack cannot stabilize skeleton rows at support>=2 after two bounded
  schema refinements;
- predicate names or value atoms start carrying prose-shaped source text;
- the verifier or compiler attempts to certify legal proposition support without
  independent authority-text review;
- gains depend on rewriting the oracle after seeing model output;
- the domain pack collapses back into generic citation mechanics only.

## Current Incoming Package Status

`legal_authority_known_hallucination_sanction_20260606_02.zip` arrived in
`C:\prethinker\tmp` and was evaluated on 2026-06-06. It is source-shaped and
keeps `false_verified=0`, but it is not imported because its expected facts use
a loose oracle dialect rather than the verifier's exact fact contract. That
package should not be silently rewritten into a passing oracle.

The useful lesson from that packet is not another citation-verifier patch. The
useful lesson is that the legal lane needs a specific document-family domain
pack, with the citation verifier as an underlay and abstention as a first-class
outcome.

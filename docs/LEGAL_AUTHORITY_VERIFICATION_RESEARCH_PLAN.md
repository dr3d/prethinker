# Legal Authority Verification Research Plan

Status: candidate next research lane, June 2026. This document is a plan, not a
claim-bearing result.

## Why This Lane Exists

Courts are now sanctioning filings that contain AI-fabricated legal citations,
fabricated quotations, and mischaracterized authorities. The lesson matches
Prethinker's current research finding:

```text
AI may propose, but verification must bottom out in deterministic or
independently source-backed checks.
```

The legal lane should therefore avoid the broad "AI legal answer" trap. The
first research target is not to decide legal merits. It is to compile a filing
into an authority ledger and verify the parts that can be checked without
asking another LLM to certify the first LLM.

## Research Question

Can Prethinker compile a legal filing into a governed authority ledger that
deterministically verifies citation existence, authority metadata, quotations,
pin-cite locality, and proposition-support boundaries while abstaining from
semantic legal judgment unless an independent reviewer closes that loop?

## Non-Claims

This lane does not claim:

- broad legal QA;
- legal advice;
- "good law" / Shepard's / KeyCite status;
- deterministic verification that a case supports a legal proposition;
- replacement of attorney review;
- product readiness.

The first honest claim, if earned, is narrower:

```text
This document's cited authorities, metadata, quotes, and pin-cite checks were
resolved or flagged through a replayable authority ledger.
```

## Tier Boundary

### Tier 1: Deterministic Or Source-Backed

Tier 1 rows may be claim-bearing if they survive the same governance family as
the domain-pack work:

- citation mention extraction with source coordinates;
- citation resolution against a declared authority inventory or external legal
  authority database;
- case-name, year, reporter, volume, and first-page metadata checks;
- quote existence checks against authority text;
- pin-cite locality checks when source pages or paragraphs are available;
- explicit unresolved, ambiguous, unavailable, and abstention rows.

### Tier 2: Governed Proposal, Review Required

Tier 2 may use an LLM to propose structured review targets:

- what proposition the filing appears to attach to a citation;
- which source span might support that proposition;
- whether a human should review a mismatch or legal-support boundary.

Tier 2 is report-only until independently reviewed. The LLM may propose a
support assessment, but it may not verify itself.

### Tier 3: Out Of Scope For This Phase

These are deliberately outside the first lane:

- drafting legal arguments;
- predicting case outcome;
- determining whether an authority is still good law;
- deciding that a case legally supports a proposition without human or citator
  closure.

## Closed Predicate Domain

Initial domain profile:

```text
datasets/domain_profiles/legal_authority_verification_v1/ontology_registry.json
```

Initial Tier 1 carrier families:

```text
legal_citation_mention/5
legal_authority_resolution/5
legal_authority_metadata_check/5
legal_authority_text_source/5
legal_quote_claim/5
legal_quote_span_match/5
legal_pin_cite_check/5
legal_verification_abstention/4
legal_proposition_support_boundary/5
domain_omission/5
```

The predicates intentionally keep source prose out of answer-bearing atoms.
Quote text is represented by digest and source coordinate, not by storing the
quote as an atom. Proposition text is not a Tier 1 value; a proposition boundary
row can say that review is required without pretending the support question is
deterministically solved.

`legal_authority_text_source/5` is the authority-text provenance receipt. It
records the compact authority coordinate, availability status, and normalized
text digest used by quote and pin-cite checks. It must not store authority
prose or propositions in atoms.

Initial Tier 2 review-target carrier families:

```text
legal_proposition_claim/5
legal_proposition_source_span/5
legal_support_assessment/5
```

These rows are allowed to organize human review. They may carry compact
proposition IDs, proposition digests, candidate span IDs, and review state.
They must not store proposition prose or convert an unreviewed model proposal
into a support verdict.

## Controlled Micro-Fixtures

Initial fixtures:

```text
datasets/compile_micro_fixtures/legal_authority_verification_micro_v1
datasets/compile_micro_fixtures/legal_authority_verification_micro_v2
datasets/compile_micro_fixtures/legal_authority_verification_micro_v3
datasets/compile_micro_fixtures/legal_authority_verification_micro_v4
datasets/compile_micro_fixtures/legal_authority_verification_micro_v5
datasets/compile_micro_fixtures/legal_authority_verification_micro_v6
datasets/compile_micro_fixtures/legal_authority_verification_micro_v7
```

They contain:

- one clean citation and quote;
- one citation that does not resolve;
- metadata mismatch checks;
- ambiguous citation resolution;
- unsupported reporter visibility as `invalid_reporter` plus explicit
  abstention;
- bare reporter citations that resolve without inventing case-name or year
  metadata when those fields are not stated in that citation mention;
- reporter-spacing variants such as `U. S.` normalized to the same authority key
  as `U.S.`;
- quoted language immediately before a citation, including punctuation-normalized
  quote matching and fabricated quote blocking;
- one real authority with a fabricated quote;
- one real quote attached to the wrong cited authority;
- one real authority with the quote present in the authority but outside the
  cited pin page;
- one authority-text-unavailable quote check that must abstain;
- one proposition-support boundary that must abstain.
- one short-form citation such as `Id.` that must require context and abstain
  instead of inventing a resolved authority.

The fixtures use local authority inventories so the first prototype can run
offline. A CourtListener-backed resolver can replace or supplement those
inventories through the same report contract, but live or cached external
lookup is a separate measurement condition from the local claim-bearing
baseline.

## Prototype Resolver

The first deterministic prototype is:

```text
src/legal_authority_resolvers.py
src/legal_authority_verification.py
scripts/run_legal_authority_verification.py
```

It produces CourtListener/Eyecite-shaped citation lookup rows:

```text
citation
normalized_citations
start_index
end_index
status
error_message
clusters
```

Status values follow the same broad shape:

- `200`: resolved;
- `300`: ambiguous;
- `400`: parsed but invalid shape or unsupported reporter;
- `404`: citation-like value did not resolve;
- `429`: reserved for external throttling, not used by the offline fixture.

The current implementation has two layers:

- a local deterministic resolver backed by checked-in
  `authority_inventory.json` files;
- an explicit resolver-injection seam plus a token-gated CourtListener
  citation-lookup resolver adapter for live/cached comparison runs.

The local inventory remains the reproducible claim path. CourtListener live
lookup is useful for fixture acquisition and resolver comparison, but it should
not turn a measurement into an unrecorded external dependency. Live outputs
need a provider manifest and retained cache before they become research
evidence. Retained cache entries include payload JSON plus
`prethinker.courtlistener_cache_metadata.v1` sidecars recording provider,
method, URL, body digest, and cache filename; they may replay without a token.
Cache misses are live calls and remain token-gated.

The verifier defaults to the local resolver. Any external resolver must be
passed explicitly, and a citation resolved by CourtListener without retained
authority text still abstains on quote and pin-cite verification.
When CourtListener lookup returns a cluster URL and no local inventory row
matches it, the synthesized authority row carries the public CourtListener URL
as report metadata only; this does not create authority text or make quote/pin
verification available.

CLI runs expose that boundary as an explicit switch:

```text
python scripts/run_legal_authority_verification.py \
  --source <filing.md> \
  --authority-inventory <authority_inventory.json> \
  --resolver local

python scripts/run_legal_authority_verification.py \
  --source <filing.md> \
  --authority-inventory <authority_inventory.json> \
  --resolver courtlistener \
  --courtlistener-cache-dir datasets/courtlistener/generated/cache
```

The first form is the local claim condition. The second form is a live/cached
resolver comparison condition and must be reported separately. Reports include
a `resolver` block with provider, class, cache directory, external-lookup
policy, and inventory-assist status so comparison runs do not collapse into the
local baseline.

Authority text used for quote/pin verification is also emitted as a compact
provenance ledger: available page/paragraph scopes get a digest, while missing
authority text emits `authority_unavailable` and forces abstention. This keeps
the verifier from silently depending on authority prose that is not visible in
the typed report. When an authority inventory includes a retained authority-text
URL, the report and ledger-query row carry that URL as provenance metadata; the
typed fact remains the compact five-slot `legal_authority_text_source/5`
receipt. Fixture intake treats retained authority/source URLs as public
provenance and rejects non-HTTP(S) local paths or opaque references.

## Ledger Query Surface

The prototype report exposes practical query answers derived only from the
compiled ledger, not from a second pass over source prose:

```text
which_citations_do_not_resolve
which_citations_are_ambiguous
which_citations_use_unsupported_reporters
which_citations_require_context
which_cases_have_metadata_mismatches
which_quotes_cannot_be_found
which_authority_text_is_unavailable
which_authority_text_sources_were_used
which_pin_cites_do_not_contain_the_quote
which_propositions_require_human_review
which_authorities_are_attached_to_propositions
can_this_filing_be_certified_citation_clean
```

The proposition-authority query is deliberately not a support verdict. It only
links a detected proposition boundary to the cited authority and preserves the
review state, usually `human_review_required` / `deterministic_abstain`.

## Metrics

Primary metric:

```text
false_verified = 0
```

In other words, the system must not mark an unresolved citation, fabricated
quote, metadata mismatch, or pin-cite mismatch as verified.

Secondary metrics:

- citation extraction precision/recall;
- authority resolution rate;
- short-form/context-required citation count;
- quote-match precision/recall;
- pin-cite locality accuracy;
- abstention rate;
- human-review burden.

High abstention is acceptable. False verification is the dangerous failure.

## Expansion Sequence

Fixture-class manifest:

```text
datasets/legal_authority_verification/fixture_corpus_manifest.json
```

1. Prove the micro-fixture with deterministic expected/forbidden facts.
2. Add a small public filing sample where all authorities are available.
   Returned clean-public packages must pass the local intake validator before
   they are added to the manifest:

   ```text
   python scripts/validate_legal_authority_fixture_package.py <package-or-zip>
   ```

   Once a returned package passes validation, import it through the
   validation-first importer rather than copying fixtures by hand:

   ```text
   python scripts/import_legal_authority_fixture_package.py <package-or-zip>
   ```

   The validator is offline and deterministic. It checks fixture shape,
   source-only oracle metadata, authority inventory hygiene, registered fact
   signatures, expected/forbidden replay, false_verified=0, quote/pin coverage,
   authority-text provenance receipts, and the clean-public boundary that
   invalid reporters should not appear in this fixture class. Metadata
   `authority_sources` rows must point to authority IDs and canonical citations
   present in the local `authority_inventory.json`. Quote-bearing fixtures must
   include expected `legal_authority_text_source/5` receipts and at least one
   forbidden authority-text-source trap, so authority prose cannot quietly
   become an untracked verifier input. It also blocks claim-bearing
   proposition-support rows in clean-public expected facts: proposition rows may
   only mark deterministic abstention or human review.
3. Add controlled adversarial mutations of that filing.
4. Add known public hallucination/sanction examples only after the resolver and
   report contract are stable.
   The intake validator already reserves this fixture class with
   `source_kind=known_hallucination_or_sanction_filing_excerpt` and a required
   `sanction_or_correction_source.md`, so the next phase has a file-shape gate
   before any real sanction examples become claim-bearing.
5. Add optional CourtListener lookup behind an explicit provider manifest and
   rate-limit discipline.

## Human Intervention Needed Later

The first local prototype does not need a credential. A CourtListener-backed
phase will need:

```text
COURTLISTENER_API_TOKEN=<token>
```

It will also need a decision on whether bulk authority text should be cached
locally, and if so, where the cache lives and what citation/license constraints
apply.

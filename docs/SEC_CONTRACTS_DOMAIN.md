# SEC / Contracts Domain

`sec_contracts@v0` is the third large starter domain in the profile catalog.

Its purpose is to stress Semantic IR on obligations, conditions, temporal
triggers, and executable-looking contract language. It is not investment advice,
legal advice, or contract enforceability analysis.

## Why This Domain

The current three-domain stack has complementary pressure:

- `medical@v0`: ontology and entity normalization
- `legal_courtlistener@v0`: source provenance, ambiguity, claim versus finding
- `sec_contracts@v0`: obligations, rights, conditions, rules, temporal triggers

Contract language is especially useful because weak systems tend to collapse:

```text
The borrower shall repay the loan after the maturity date.
```

into a completed fact such as:

```prolog
repaid(borrower, loan).
```

The desired behavior is to preserve the obligation and temporal/conditional
scope:

```prolog
obligation(borrower, repay_loan_after_maturity, source).
subject_to(repay_loan_after_maturity, after_maturity_date).
```

## Current Adapter

- profile: `modelfiles/profile.sec_contracts.v0.json`
- adapter: `adapters/sec_edgar/`
- synthetic fixture:
  `datasets/sec_edgar/samples/sec_contracts_synthetic_5.jsonl`
- generated live data path, ignored:
  `datasets/sec_edgar/generated/`

The adapter currently supports:

- SEC submissions fetches by CIK
- local raw-response caching
- normalized filing records
- harness case generation
- contract/obligation predicate contracts

Live SEC calls require `SEC_USER_AGENT`.

## First Live Smoke

The first live metadata smoke generated 10 recent filing harness records for
Apple and 10 for Microsoft, kept under ignored generated data. A Semantic IR
smoke ran five synthetic contract cases plus six live metadata cases through
`qwen/qwen3.6-35b-a3b` via LM Studio structured output.

Observed behavior:

- all 11 smoke cases produced valid `semantic_ir_v1` JSON
- synthetic obligation and condition cases preserved obligation/right semantics
  instead of asserting completed repayment/default facts
- live filing metadata initially exposed a palette gap: the model used
  `party_to_contract/3` for ordinary filing/company metadata
- adding `filer_of/2` fixed that shape in the next smoke: all six live metadata
  cases used `filer_of/2` and no longer used `party_to_contract/3`

This is the kind of profile-palette correction we want: domain-specific
predicate vocabulary improves model proposals without adding English phrase
patches to the generic mapper.

## Open Questions

- Should `effective_on(contract, execution_trigger)` be admitted as a trigger,
  or quarantined until actual execution evidence exists?
- How should the mapper represent explicit absence-of-evidence statements such
  as "the filing does not state whether any report was missed"?
- Which contract predicates are current facts, and which are rule/constraint
  material that should stay quarantined until rule admission is stronger?
- How much source metadata should be committed before contract exhibit text is
  available?

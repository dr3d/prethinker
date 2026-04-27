# SEC EDGAR Adapter

This adapter is a first-pass shell for using SEC EDGAR filings and contract
exhibits as Semantic IR stress material.

The goal is controlled source intake, not investment advice, legal advice, or
contract enforceability analysis. SEC/contract text should stress:

- obligation versus completed fact
- entitlement versus exercised right
- condition versus satisfied condition
- temporal triggers and effective dates
- contract-scoped party roles
- filing/exhibit provenance

## Files

- `client.py`: tiny SEC EDGAR client with local response caching
- `models.py`: `FilingSourceRecord` and `SemanticIRHarnessCase`
- `normalize.py`: submission/contract-excerpt normalizers
- `predicates.py`: SEC/contract predicate contracts
- `to_harness.py`: normalized record to Semantic IR harness case
- `sample.py`: small live submissions sample generator

## Live Sampling

SEC requests require a descriptive User-Agent.

```powershell
$env:SEC_USER_AGENT = "Prethinker research contact@example.com"
python adapters/sec_edgar/sample.py --cik 320193 --limit 25
```

Generated live data should stay under ignored `datasets/sec_edgar/generated/`
unless it has been reviewed and intentionally turned into a small durable
fixture.

## Boundary

The adapter may provide source records, predicate contracts, and provenance. It
must not decide whether an obligation was performed, a condition was satisfied,
a breach occurred, or a security is a good investment. The mapper/admission
layer remains the authority for KB writes.

# CourtListener Adapter

This adapter is a first-pass shell for using CourtListener as legal-domain
fodder for Prethinker Semantic IR experiments.

The goal is controlled source intake, not legal reasoning. CourtListener records
should stress:

- claim versus court finding
- docket event versus merits holding
- citation versus endorsement
- case-scoped party roles
- judge/attorney identity ambiguity
- document provenance

## Files

- `client.py`: tiny authenticated REST client with local raw-response caching
- `models.py`: `LegalSourceRecord` and `SemanticIRHarnessCase`
- `normalize.py`: tolerant CourtListener record normalizer
- `predicates.py`: legal predicate contracts
- `to_harness.py`: normalized record to Semantic IR harness case
- `sample.py`: small live API sample generator

## Live Sampling

CourtListener API calls require an API token.

```powershell
$env:COURTLISTENER_API_TOKEN = "..."
python adapters/courtlistener/sample.py --query "breach of lease" --limit 25
```

Generated live data should stay under ignored `datasets/courtlistener/generated/`
unless it has been reviewed and intentionally turned into a small durable
fixture. Cached raw responses can be replayed without a token; cache misses are
live API calls and remain token-gated. Claim-bearing legal verification runs
should retain the cache/provider manifest needed to reproduce the resolver
inputs offline. Cache payloads that become retained research evidence must have
matching `prethinker.courtlistener_cache_metadata.v1` sidecars; governance runs
`scripts/audit_courtlistener_cache_provenance.py` to block orphan payloads or
untracked provider metadata.

## Boundary

The adapter may provide source records, predicate contracts, and provenance. It
must not decide legal truth. The mapper/admission layer remains the authority
for KB writes.

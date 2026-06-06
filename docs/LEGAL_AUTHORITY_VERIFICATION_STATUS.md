# Legal Authority Verification Status

This generated report runs the deterministic legal-authority verifier over fixture-manifest entries.
It reads local fixture files and authority inventories only; it does not call an LLM or live legal resolver.

- Manifest: `datasets/legal_authority_verification/fixture_corpus_manifest.json`
- Fixtures: `2`
- Expected facts: `53 / 53`
- Matched forbidden facts: `0 / 13`
- Citation mentions: `9`
- Verified / blocked / review-required mentions: `1 / 7 / 1`
- Resolved / unresolved / ambiguous: `7 / 1 / 1`
- Quote claims / quote matches / quote mismatches: `4 / 2 / 1`
- Pin mismatches: `1`
- Proposition boundaries: `1`
- False verified: `0`
- Blocking rows: `0`
- Status: `pass`

## Fixture Classes

| Class | Status | Fixtures |
| --- | --- | ---: |
| `controlled_adversarial_mutations` | `seeded` | 2 |
| `clean_public_filings` | `planned` | 0 |
| `known_hallucination_or_sanction_filings` | `deferred_until_resolver_contract_stable` | 0 |

## Fixture Results

| Fixture | Class | Expected | Forbidden matched | False verified | Mentions verified/blocked/review | Certification | Errors |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `legal_authority_verification_micro_v1` | `controlled_adversarial_mutations` | 35/35 | 0 | 0 | `1/3/1` | `no` | `[]` |
| `legal_authority_verification_micro_v2` | `controlled_adversarial_mutations` | 18/18 | 0 | 0 | `0/4/0` | `no` | `[]` |

## Next External Work Order

- Needed now: `True`
- Reason: The controlled micro-fixture gate is now stable. The next external input is a clean-public-filings batch; a local offsite packet is prepared at tmp/legal_authority_clean_public_filings_work_order_20260606_r1.zip. Known hallucination/sanction filings remain deferred until the clean-public baseline lands.

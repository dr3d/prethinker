# Legal Authority Verification Status

This generated report runs the deterministic legal-authority verifier over fixture-manifest entries.
It reads local fixture files and authority inventories only; it does not call an LLM or live legal resolver.

- Manifest: `datasets/legal_authority_verification/fixture_corpus_manifest.json`
- Fixtures: `6`
- Expected facts: `147 / 147`
- Matched forbidden facts: `0 / 35`
- Citation mentions: `17`
- Verified / blocked / review-required mentions: `6 / 10 / 1`
- Resolved / unresolved / ambiguous / invalid reporter: `14 / 1 / 1 / 1`
- Metadata checks / matches / mismatches: `64 / 62 / 2`
- Quote claims / quote matches / quote mismatches: `9 / 5 / 3`
- Pin mismatches: `1`
- Authority text sources: `11`
- Authority text available / unavailable sources: `10 / 1`
- Proposition boundaries: `1`
- Verification abstentions: `9`
- False verified: `0`
- Blocking rows: `0`
- Status: `pass`

## Fact Signature Coverage

| Signature | Expected matched/total | Forbidden matched/total |
| --- | ---: | ---: |
| `legal_authority_metadata_check/5` | 64/64 | 0/8 |
| `legal_authority_resolution/5` | 17/17 | 0/7 |
| `legal_authority_text_source/5` | 11/11 | 0/2 |
| `legal_citation_mention/5` | 17/17 | 0/0 |
| `legal_pin_cite_check/5` | 7/7 | 0/4 |
| `legal_proposition_claim/5` | 1/1 | 0/1 |
| `legal_proposition_source_span/5` | 1/1 | 0/1 |
| `legal_proposition_support_boundary/5` | 1/1 | 0/1 |
| `legal_quote_claim/5` | 9/9 | 0/0 |
| `legal_quote_span_match/5` | 9/9 | 0/9 |
| `legal_support_assessment/5` | 1/1 | 0/1 |
| `legal_verification_abstention/4` | 9/9 | 0/1 |

## Fixture Classes

| Class | Status | Fixtures |
| --- | --- | ---: |
| `controlled_adversarial_mutations` | `seeded` | 6 |
| `clean_public_filings` | `planned` | 0 |
| `known_hallucination_or_sanction_filings` | `deferred_until_clean_public_baseline` | 0 |

## Fixture Results

| Fixture | Class | Expected | Forbidden matched | False verified | Mentions verified/blocked/review | Certification | Errors |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `legal_authority_verification_micro_v1` | `controlled_adversarial_mutations` | 51/51 | 0 | 0 | `1/3/1` | `no` | `[]` |
| `legal_authority_verification_micro_v2` | `controlled_adversarial_mutations` | 29/29 | 0 | 0 | `0/4/0` | `no` | `[]` |
| `legal_authority_verification_micro_v3` | `controlled_adversarial_mutations` | 3/3 | 0 | 0 | `0/1/0` | `no` | `[]` |
| `legal_authority_verification_micro_v4` | `controlled_adversarial_mutations` | 12/12 | 0 | 0 | `0/1/0` | `no` | `[]` |
| `legal_authority_verification_micro_v5` | `controlled_adversarial_mutations` | 31/31 | 0 | 0 | `4/0/0` | `yes` | `[]` |
| `legal_authority_verification_micro_v6` | `controlled_adversarial_mutations` | 21/21 | 0 | 0 | `1/1/0` | `no` | `[]` |

## Next External Work Order

- Needed now: `True`
- Reason: The controlled micro-fixture gate is now stable. The next external input is a clean-public-filings batch; a local offsite packet is prepared at tmp/legal_authority_clean_public_filings_work_order_20260606_r6.zip. Returned packages must pass scripts/import_legal_authority_fixture_package.py before fixtures are added to this manifest. Known hallucination/sanction filings remain deferred until the clean-public baseline lands.

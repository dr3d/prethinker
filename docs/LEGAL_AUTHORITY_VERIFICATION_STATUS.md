# Legal Authority Verification Status

This generated report runs the deterministic legal-authority verifier over fixture-manifest entries.
It reads local fixture files and authority inventories only; it does not call an LLM or live legal resolver.

- Manifest: `datasets/legal_authority_verification/fixture_corpus_manifest.json`
- Fixtures: `15`
- Expected facts: `261 / 261`
- Matched forbidden facts: `0 / 74`
- Citation mentions: `35`
- Verified / blocked / review-required mentions: `18 / 15 / 2`
- Resolved / unresolved / ambiguous / invalid reporter / unavailable: `31 / 2 / 1 / 1 / 0`
- Metadata checks / matches / mismatches: `146 / 142 / 4`
- Quote claims / quote matches / quote mismatches: `14 / 9 / 4`
- Pin mismatches: `1`
- Pin unavailable: `1`
- Authority text sources: `26`
- Authority text available / unavailable sources: `16 / 10`
- Short-form citations requiring context: `2`
- Proposition boundaries: `2`
- Verification abstentions: `15`
- False verified: `0`
- Blocking rows: `0`
- Status: `pass`

## Ledger-Only Query Totals

These counts are derived only from structured verifier ledger rows.

- Citation-clean certification yes / no: `4 / 11`
- Blocking issues / review-required propositions: `17 / 2`
- Unresolved-or-ambiguous citations: `4`
- Unavailable citation lookups: `0`
- Metadata mismatches: `4`
- Quote mismatches / unavailable authority text: `4 / 1`
- Pin mismatches / unavailable pins: `1 / 1`
- Short-form citations requiring context: `2`
- Proposition review rows / authority links: `2 / 2`

## Fact Signature Coverage

| Signature | Expected matched/total | Forbidden matched/total |
| --- | ---: | ---: |
| `legal_authority_metadata_check/5` | 110/110 | 0/15 |
| `legal_authority_resolution/5` | 35/35 | 0/18 |
| `legal_authority_text_source/5` | 19/19 | 0/7 |
| `legal_citation_mention/5` | 35/35 | 0/2 |
| `legal_pin_cite_check/5` | 11/11 | 0/9 |
| `legal_proposition_claim/5` | 2/2 | 0/2 |
| `legal_proposition_source_span/5` | 2/2 | 0/2 |
| `legal_proposition_support_boundary/5` | 2/2 | 0/2 |
| `legal_quote_claim/5` | 14/14 | 0/0 |
| `legal_quote_span_match/5` | 14/14 | 0/13 |
| `legal_support_assessment/5` | 2/2 | 0/2 |
| `legal_verification_abstention/4` | 15/15 | 0/2 |

## Fixture Classes

| Class | Status | Fixtures |
| --- | --- | ---: |
| `controlled_adversarial_mutations` | `seeded` | 12 |
| `clean_public_filings` | `seeded` | 3 |
| `known_hallucination_or_sanction_filings` | `queued_for_source_only_packet` | 0 |

## Fixture Results

| Fixture | Class | Expected | Forbidden matched | False verified | Mentions verified/blocked/review | Certification | Errors |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `legal_authority_verification_micro_v1` | `controlled_adversarial_mutations` | 51/51 | 0 | 0 | `1/3/1` | `no` | `[]` |
| `legal_authority_verification_micro_v2` | `controlled_adversarial_mutations` | 29/29 | 0 | 0 | `0/4/0` | `no` | `[]` |
| `legal_authority_verification_micro_v3` | `controlled_adversarial_mutations` | 3/3 | 0 | 0 | `0/1/0` | `no` | `[]` |
| `legal_authority_verification_micro_v4` | `controlled_adversarial_mutations` | 12/12 | 0 | 0 | `0/1/0` | `no` | `[]` |
| `legal_authority_verification_micro_v5` | `controlled_adversarial_mutations` | 31/31 | 0 | 0 | `4/0/0` | `yes` | `[]` |
| `legal_authority_verification_micro_v6` | `controlled_adversarial_mutations` | 21/21 | 0 | 0 | `1/1/0` | `no` | `[]` |
| `legal_authority_verification_micro_v7` | `controlled_adversarial_mutations` | 1/1 | 0 | 0 | `0/0/0` | `no` | `[]` |
| `legal_authority_verification_micro_v8` | `controlled_adversarial_mutations` | 1/1 | 0 | 0 | `0/0/0` | `no` | `[]` |
| `legal_authority_verification_micro_v9` | `controlled_adversarial_mutations` | 12/12 | 0 | 0 | `0/1/0` | `no` | `[]` |
| `legal_authority_verification_micro_v10` | `controlled_adversarial_mutations` | 22/22 | 0 | 0 | `0/3/0` | `no` | `[]` |
| `legal_authority_verification_micro_v11` | `controlled_adversarial_mutations` | 13/13 | 0 | 0 | `0/0/1` | `no` | `[]` |
| `legal_authority_verification_micro_v12` | `controlled_adversarial_mutations` | 9/9 | 0 | 0 | `0/1/0` | `no` | `[]` |
| `clean_legal_filing_001` | `clean_public_filings` | 18/18 | 0 | 0 | `4/0/0` | `yes` | `[]` |
| `clean_legal_filing_002` | `clean_public_filings` | 20/20 | 0 | 0 | `4/0/0` | `yes` | `[]` |
| `clean_legal_filing_003` | `clean_public_filings` | 18/18 | 0 | 0 | `4/0/0` | `yes` | `[]` |

## Next External Work Order

- Needed now: `False`
- Reason: The first known hallucination/sanction package was returned as legal_authority_known_hallucination_sanction_20260606_01.zip and retained outside active governance after failing intake validation. The package is useful diagnostic material, but it is not ready to add to this manifest: its oracle facts used placeholder variables/source labels, and it exposed local citation-parser coverage gaps for A.D.3d, Illinois Appellate, and full-date WL parentheticals. No new external package is needed until those local parser/intake issues are resolved. Any future corrected concrete-fact work-order request should be emitted as a fresh zip in C:\prethinker\tmp, not in the archive.

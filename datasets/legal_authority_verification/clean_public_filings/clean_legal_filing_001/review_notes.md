# Review notes — clean_legal_filing_001

## Fixture class and claim status
This is a research test fixture in the `clean_public_filings` class for the
`legal_authority_verification_v1` lane. It is **not legal advice**. Its sole
purpose is to exercise citation-existence, authority-metadata, quoted-language,
pin-cite-locality, and authority-text-provenance checks on a deliberately clean
public-filing excerpt.

## Source construction and faithfulness
The `source.md` excerpt is a synthesized clean filing-style passage. Every
citation is real and every quoted span is reproduced **verbatim** from the
public-domain United States Reports opinion named, at the pinpoint page cited.
No citation, quotation, case name, or pin in the source was generated as a model
claim; each was taken from the public record.

## Authorities relied on (provenance)
- `auth_brown_347_us_483` — Brown v. Board of Education of Topeka, 347 U.S. 483 (1954); public-domain source: https://supreme.justia.com/cases/federal/us/347/483/; pin 495 (verbatim).
- `auth_bolling_347_us_497` — Bolling v. Sharpe, 347 U.S. 497 (1954); public-domain source: https://supreme.justia.com/cases/federal/us/347/497/; no quoted span.
- `auth_loving_388_us_1` — Loving v. Virginia, 388 U.S. 1 (1967); public-domain source: https://supreme.justia.com/cases/federal/us/388/1/; no quoted span.

## Oracle independence
Expected and forbidden facts were derived solely from the source text and the
`authority_inventory.json` (review basis `source_and_authority_inventory_only`);
no model output was used as ground truth (`used_model_output: false`).

## Coverage summary (reconstructed verifier)
- Citation mentions: 4
- Quote claims: 1
- Authority-text receipts (available): 1
- Invalid reporters: 0
- Short-form citations: 0
- False verified: 0
- At least one quoted pin-cite and at least one no-quote citation are present.

## Abstentions and out-of-scope citations
None. All citations resolve to inventory authorities; no proposition-level legal
support is asserted, and no out-of-scope citations were ignored.

## Expected vs forbidden
`expected_facts.pl` lists the 18 documented core receipts the
verifier must emit. `forbidden_facts.pl` lists 7 deterministic
near-miss traps (wrong-authority resolution, unresolved resolution, year
mismatch, invented case-name match on a bare citation, authority-text
provenance inversion, quote no-match, and pin-outside-quote) that a faithful
verifier must never emit.

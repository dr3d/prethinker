# Review notes — clean_legal_filing_002

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
- `auth_miranda_384_us_436` — Miranda v. Arizona, 384 U.S. 436 (1966); public-domain source: https://supreme.justia.com/cases/federal/us/384/436/; pin 444 (verbatim).
- `auth_gideon_372_us_335` — Gideon v. Wainwright, 372 U.S. 335 (1963); public-domain source: https://supreme.justia.com/cases/federal/us/372/335/; no quoted span.
- `auth_mapp_367_us_643` — Mapp v. Ohio, 367 U.S. 643 (1961); public-domain source: https://supreme.justia.com/cases/federal/us/367/643/; no quoted span.
- `auth_katz_389_us_347` — Katz v. United States, 389 U.S. 347 (1967); public-domain source: https://supreme.justia.com/cases/federal/us/389/347/; no quoted span.

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
`expected_facts.pl` lists the 20 documented core receipts the
verifier must emit. `forbidden_facts.pl` lists 6 deterministic
near-miss traps (wrong-authority resolution, unresolved resolution, year
mismatch, invented case-name match on a bare citation, authority-text
provenance inversion, quote no-match, and pin-outside-quote) that a faithful
verifier must never emit.

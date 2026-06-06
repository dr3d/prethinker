# Review notes — clean_legal_filing_003

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
- `auth_obergefell_576_us_644` — Obergefell v. Hodges, 576 U.S. 644 (2015); public-domain source: https://supreme.justia.com/cases/federal/us/576/644/; pin 675 (verbatim).
- `auth_griswold_381_us_479` — Griswold v. Connecticut, 381 U.S. 479 (1965); public-domain source: https://supreme.justia.com/cases/federal/us/381/479/; no quoted span.
- `auth_lawrence_539_us_558` — Lawrence v. Texas, 539 U.S. 558 (2003); public-domain source: https://supreme.justia.com/cases/federal/us/539/558/; no quoted span.

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

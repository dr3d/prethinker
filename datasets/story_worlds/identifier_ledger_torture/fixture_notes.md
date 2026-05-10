# identifier_ledger_torture Fixture Notes

Author-reported source words: 2025.

Primary stress: exact-string identifier fidelity under near-duplicate pressure.

Secondary stress: supersession and withdrawal tracking.

Expected hallucination: normalize visually similar IDs or collapse active and
withdrawn labels. The fixture intentionally pressures `EX-C-01` vs `EX-C-1`,
`BAY-04-L` vs `BAY-04-I`, `BC-833014` vs `BC-883014`, and `CASE-22-O917` vs
`CASE-22-0917`.

Review note: this fixture is intended to measure lexical/addressability support,
not just broad semantic recall. Wrong punctuation, zero/letter swaps, or
normalized labels should be treated as meaningful failures.

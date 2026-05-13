# Answer-Bearing Complement Ladder

This probe tests whether compile preserves compact answer-bearing complements
as queryable surfaces instead of only retaining adjacent facts.

The ladder avoids dataset vocabulary and fixture-specific nouns. It covers
generic complement shapes seen in transfer residue:

- descriptive definition complements
- use or purpose complements
- temporal start labels
- relation-target complements
- component-list complements
- generic name and category complements

Expected use:

1. Compile the source with source-record ledger facts enabled.
2. Run QA against `qa.md`.
3. Compare against `oracle.jsonl`.

The probe should be interpreted as a resolution test. A miss means the source
may have been understood locally while the answer-bearing complement was not
preserved as a queryable coordinate.

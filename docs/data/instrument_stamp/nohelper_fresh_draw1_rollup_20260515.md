# No-Helper Fresh Draw 1 Rollup - 2026-05-15

Stamp: `instrument-freeze-20260515-r1`

Mode: fresh compile-plus-QA draw 1 with helper companion row limit `0`, QA cache disabled, and no legacy native helper adapters.

| Corpus | Questions | Exact | Partial | Miss | Exact rate | Helper rows | Runtime errors | Write proposals |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `PrivacyQA-30` | 30 | 27 | 0 | 3 | 90.00% | 0 | 0 | 0 |
| `MAUD-10` | 40 | 17 | 2 | 21 | 42.50% | 0 | 0 | 0 |
| `SQuAD-30` | 171 | 165 | 1 | 5 | 96.49% | 0 | 0 | 0 |
| `CUAD-10` | 40 | 30 | 6 | 4 | 75.00% | 0 | 0 | 0 |
| `RACE-50-options` | 177 | 151 | 1 | 25 | 85.31% | 0 | 0 | 0 |
| **Aggregate** | **458** | **390** | **10** | **58** | **85.15%** | **0** | **0** | **0** |

Failure surfaces by corpus are preserved in the JSON artifact. This rollup is measurement only; anomalies are not repaired inside the freeze window.

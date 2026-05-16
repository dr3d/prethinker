# No-Helper External N=3 Variance Rollup

Stamp: `instrument-freeze-20260515-r1`

Mode: fresh external compile-plus-QA, helpers genuinely off (`--helper-companion-row-limit 0`, no cache, no legacy native helper adapters).

## Aggregate

| Draw | Questions | Exact | Partial | Miss | Exact rate | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `draw1` | 458 | 390 | 10 | 58 | 85.15% | 0 |
| `draw2` | 458 | 381 | 13 | 64 | 83.19% | 0 |
| `draw3` | 458 | 386 | 10 | 62 | 84.28% | 0 |
| **N=3 pooled** | **1374** | **1157** | **33** | **184** | **84.21%** | **0** |

Aggregate mean exact rate: **84.21%**; range: **1.96 points**; peak: **85.15%**.

## By Corpus

| Corpus | Draw 1 | Draw 2 | Draw 3 | Mean | Range | Pooled | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `PrivacyQA-30` | 90.00% (27/30) | 90.00% (27/30) | 83.33% (25/30) | 87.78% | 6.67 pts | 87.78% (79/90) | 0 |
| `MAUD-10` | 42.50% (17/40) | 35.00% (14/40) | 40.00% (16/40) | 39.17% | 7.50 pts | 39.17% (47/120) | 0 |
| `SQuAD-30` | 96.49% (165/171) | 94.15% (161/171) | 94.74% (162/171) | 95.13% | 2.34 pts | 95.13% (488/513) | 0 |
| `CUAD-10` | 75.00% (30/40) | 75.00% (30/40) | 82.50% (33/40) | 77.50% | 7.50 pts | 77.50% (93/120) | 0 |
| `RACE-50-options` | 85.31% (151/177) | 84.18% (149/177) | 84.75% (150/177) | 84.75% | 1.13 pts | 84.75% (450/531) | 0 |

## Notes

- The external no-helper stamp is stable at corpus aggregate level: three fresh draws span only 1.96 points.
- SQuAD and RACE form stable high transfer bands without helper rows.
- PrivacyQA is mostly stable but draw3 moved lower, widening its exact-rate range to 6.67 points.
- CUAD repeats 75 percent twice then rises to 82.50 percent on draw3, making contract QA visibly compile-draw sensitive.
- MAUD remains the low legal-transfer boundary with a 35.00-42.50 percent band.
- All three external draws report zero helper rows, zero runtime load errors, and zero write proposal rows.

Measurement discipline: this rollup records observed variance only. It is not a repair target inside the freeze window.

## Draw 3 Artifact Roots

- `PrivacyQA-30`: `tmp\instrument_stamp_20260515_fresh_privacyqa30_draw3_compile_or`, `tmp\instrument_stamp_20260515_fresh_privacyqa30_draw3_qa_or`
- `MAUD-10`: `tmp\instrument_stamp_20260515_fresh_maud10_draw3_compile_power`, `tmp\instrument_stamp_20260515_fresh_maud10_draw3_qa_power`
- `SQuAD-30`: `tmp\instrument_stamp_20260515_fresh_squad30_draw3_compile_or`, `tmp\instrument_stamp_20260515_fresh_squad30_draw3_qa_or`
- `CUAD-10`: `tmp\instrument_stamp_20260515_fresh_cuad10_draw3_compile_power`, `tmp\instrument_stamp_20260515_fresh_cuad10_draw3_qa_power`
- `RACE-50-options`: `tmp\instrument_stamp_20260515_fresh_race50_draw3_compile_or`, `tmp\instrument_stamp_20260515_fresh_race50_draw3_qa_or`

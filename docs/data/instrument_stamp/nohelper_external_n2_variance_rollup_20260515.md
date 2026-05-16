# No-Helper External N=2 Variance Rollup

Stamp: `instrument-freeze-20260515-r1`

Mode: fresh external compile-plus-QA, helpers genuinely off (`--helper-companion-row-limit 0`, no cache, no legacy native helper adapters).

## Aggregate

| Draw | Questions | Exact | Partial | Miss | Exact rate | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `draw1` | 458 | 390 | 10 | 58 | 85.15% | 0 |
| `draw2` | 458 | 381 | 13 | 64 | 83.19% | 0 |
| **N=2 pooled** | **916** | **771** | **23** | **122** | **84.17%** | **0** |

Aggregate mean exact rate: **84.17%**; range: **1.96 points**.

## By Corpus

| Corpus | Draw 1 | Draw 2 | Mean | Range | Exact delta | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `PrivacyQA-30` | 90.00% (27/30) | 90.00% (27/30) | 90.00% | 0.00 pts | +0 | 0 / 0 |
| `MAUD-10` | 42.50% (17/40) | 35.00% (14/40) | 38.75% | 7.50 pts | -3 | 0 / 0 |
| `SQuAD-30` | 96.49% (165/171) | 94.15% (161/171) | 95.32% | 2.34 pts | -4 | 0 / 0 |
| `CUAD-10` | 75.00% (30/40) | 75.00% (30/40) | 75.00% | 0.00 pts | +0 | 0 / 0 |
| `RACE-50-options` | 85.31% (151/177) | 84.18% (149/177) | 84.75% | 1.13 pts | -2 | 0 / 0 |

## Notes

- PrivacyQA-30 and CUAD-10 repeated exactly across two draws.
- RACE-50-options remained stable within 1.13 points despite MCQ option pressure.
- SQuAD-30 remained high with a 2.34 point spread.
- MAUD-10 is the unstable/low legal-transfer boundary in this N=2 sample, with a 7.50 point spread and a lower draw2.
- All external draws ran with zero helper rows, zero runtime load errors, and zero write-proposal rows.

Measurement discipline: this rollup records observed variance only. It is not a repair target inside the freeze window.

## Draw 2 Artifact Roots

- `PrivacyQA-30`: `tmp\instrument_stamp_20260515_fresh_privacyqa30_draw2_compile_or`, `tmp\instrument_stamp_20260515_fresh_privacyqa30_draw2_qa_or`
- `MAUD-10`: `tmp\instrument_stamp_20260515_fresh_maud10_draw2_compile_power`, `tmp\instrument_stamp_20260515_fresh_maud10_draw2_qa_power`
- `SQuAD-30`: `tmp\instrument_stamp_20260515_fresh_squad30_draw2_compile_or`, `tmp\instrument_stamp_20260515_fresh_squad30_draw2_qa_or`
- `CUAD-10`: `tmp\instrument_stamp_20260515_fresh_cuad10_draw2_compile_power`, `tmp\instrument_stamp_20260515_fresh_cuad10_draw2_qa_power`
- `RACE-50-options`: `tmp\instrument_stamp_20260515_fresh_race50_draw2_compile_or`, `tmp\instrument_stamp_20260515_fresh_race50_draw2_qa_or`

# Query Surface Mode Comparison

Generated: 2026-05-03T13:41:06+00:00

This report compares existing post-ingestion QA artifacts. It does not read source prose,
gold KBs, or strategy files, and it does not rerun the compiler, query planner, judge,
or failure classifier.

## Current Lesson

Evidence-bundle filtering is not a simple replacement for the baseline query
path. It rescues rows that the baseline under-supports, but it can also perturb
already-correct rows. The next runtime-safe direction is a non-oracle selector
that protects baseline exact-like rows and only activates alternate query modes
when pre-judge signals indicate near-miss risk.

The diagnostic perfect-selector counts below use judge labels after the fact.
They are an upper-bound research measurement, not a runtime policy.

## Aggregate

- Rows compared: `80`
- Volatile rows: `16`
- Baseline rows rescued by an alternate mode: `12`
- Baseline exact rows regressed by an alternate mode: `1`

## Groups

### veridia9

- Baseline mode: `baseline`
- Rows: `40`
- Volatile rows: `6`
- Baseline rescued rows: `4`
- Baseline exact regression rows: `0`

| Mode | Exact | Partial | Miss | Unknown |
| --- | ---: | ---: | ---: | ---: |
| `baseline` | 19 | 6 | 15 | 0 |
| `narrow` | 22 | 4 | 14 | 0 |
| `broad` | 19 | 7 | 14 | 0 |

Diagnostic perfect-selector upper bound: `22 exact / 7 partial / 11 miss`.

| Row | Baseline | Best | Mode Verdicts | Note |
| --- | --- | --- | --- | --- |
| `q006` | miss | partial via `broad` | baseline:miss, narrow:miss, broad:partial | rescued |
| `q012` | partial | partial via `baseline` | baseline:partial, narrow:miss, broad:miss |  |
| `q021` | miss | exact via `narrow` | baseline:miss, narrow:exact, broad:miss | rescued |
| `q034` | partial | partial via `baseline` | baseline:partial, narrow:miss, broad:miss |  |
| `q035` | miss | exact via `narrow` | baseline:miss, narrow:exact, broad:partial | rescued |
| `q040` | miss | exact via `narrow` | baseline:miss, narrow:exact, broad:partial | rescued |

### black_lantern

- Baseline mode: `baseline`
- Rows: `40`
- Volatile rows: `10`
- Baseline rescued rows: `8`
- Baseline exact regression rows: `1`

| Mode | Exact | Partial | Miss | Unknown |
| --- | ---: | ---: | ---: | ---: |
| `baseline` | 27 | 7 | 6 | 0 |
| `narrow` | 32 | 3 | 5 | 0 |
| `broad` | 32 | 5 | 3 | 0 |

Diagnostic perfect-selector upper bound: `34 exact / 4 partial / 2 miss`.

| Row | Baseline | Best | Mode Verdicts | Note |
| --- | --- | --- | --- | --- |
| `q007` | partial | exact via `narrow,broad` | baseline:partial, narrow:exact, broad:exact | rescued |
| `q011` | partial | exact via `narrow,broad` | baseline:partial, narrow:exact, broad:exact | rescued |
| `q015` | partial | exact via `narrow,broad` | baseline:partial, narrow:exact, broad:exact | rescued |
| `q016` | partial | exact via `narrow,broad` | baseline:partial, narrow:exact, broad:exact | rescued |
| `q021` | partial | partial via `baseline,broad` | baseline:partial, narrow:miss, broad:partial |  |
| `q022` | miss | partial via `broad` | baseline:miss, narrow:miss, broad:partial | rescued |
| `q035` | miss | exact via `narrow` | baseline:miss, narrow:exact, broad:miss | rescued |
| `q036` | miss | exact via `broad` | baseline:miss, narrow:miss, broad:exact | rescued |
| `q037` | miss | exact via `narrow,broad` | baseline:miss, narrow:exact, broad:exact | rescued |
| `q040` | exact | exact via `baseline` | baseline:exact, narrow:partial, broad:partial | baseline-exact-regression |

# Boundary Hunt Worksheet

Last updated: 2026-05-13

This is the active CTO cockpit for boundary-hunt work. The full historical
worksheet was preserved verbatim at:

`C:\prethinker_tmp_archive\boundary_hunt_20260513\BOUNDARY_HUNT_WORKSHEET_FULL_20260513.md`

Use this file for current state, next pressure, and handoff clarity. Use the
archive copy only for named historical detail.

## Doctrine

Fixture names, question ids, row ids, answer strings, local people, local
organizations, and source-story vocabulary are artifact addresses only. They are
never architecture.

The loop is:

```text
measure -> classify coordinates -> group by fixture-free geometry
  -> predict a reusable repair -> replay on unlike rows -> journal trajectory
```

Do not rescue a row by teaching the harness local nouns. Repair only when the
failure shape remains meaningful after fixture vocabulary is removed.

## Current Phase

Guard compression is archived. Boundary hunt is active.

The hunt target is no longer "retire more guards." It is:

- expose where the current interior gets blurry on unlike source shapes;
- separate compile-surface gaps from helper/selector gaps;
- audit helper trigger conditions as carefully as helper bodies;
- extend the interior only with generic, replayable repairs.

## Seed Measurement

Wide OpenRouter corpus run:

```text
compiled fixtures: 32
questions: 1218
exact / partial / miss: 1008 / 76 / 134
exact rate: 0.8276
not-exact coordinates: 210
runtime load errors: 0
write proposal rows: 0
helper rows: 2877
rows per exact answer: 2.854
```

Main boundary split:

| Surface | Count | Read |
| --- | ---: | --- |
| `compile_surface_gap` | 131 | Largest class. Often resolution/envelope blur rather than absent extraction. |
| `hybrid_join_gap` | 42 | Facts exist in pieces; answer needs reusable join/arithmetic/set logic. |
| `query_surface_gap` | 27 | Compile likely has support; planner misses or overbinds surface. |
| `answer_surface_gap` | 7 | Support reached but answer form/rendering weak. |
| `judge_uncertain` | 3 | Measurement ambiguity; do not repair without audit. |

Important finding:

Only a small part of the wide compile boundary looked like a truly missing
axis. Most misses were resolution blur: wrong authority envelope, wrong
temporal envelope, wrong epistemic envelope, wrong granularity, opaque residue,
or predicate-shape drift.

## Completed Moves

The full entries are archived in the full worksheet copy. Current rollup:

| Entry Range | Result | Status |
| --- | --- | --- |
| BH-006 to BH-011 | Split compile-surface and hybrid-join classes; simple authority and deadline probes passed. | Interior wider than expected; boundary is density/resolution. |
| BH-012 to BH-015 | Status timeline ladder, resolver repair, unlike replay, density split. | First live-set extension; remaining density classified. |
| BH-016 to BH-020 | Status-count aggregation and alias-count work. | Several coordinates moved inside; evidence split created. |
| BH-021 to BH-022 | Explicit source-count source-fidelity repair and transfer replay. | Generic numeric source lines improved; wide target moved exact. |
| BH-023 to BH-024 | Scoped semantic filter repair and unlike replay. | Predicate-scoped and source-section-scoped forms transfer; helper delivery still noisy. |
| BH-025 | Trigger sanity stage 1. | Sectionless scoped counts passed; state-word and non-English source-fidelity risks surfaced. |
| BH-026 | Trigger sanity stage 2. | Canonical alias probe passed; numeric prose source-fidelity repair moved `14/0/2` to `15/0/1`. |

## Current Evidence

Trigger sanity stage 2 after the generic source-record repair:

```text
questions: 16
exact / partial / miss: 15 / 0 / 1
exact rate: 0.9375
helper rows: 0
runtime load errors: 0
write proposal rows: 0
```

Per fixture:

| Probe | Exact | Partial | Miss | Read |
| --- | ---: | ---: | ---: | --- |
| `canonical_alias_register` | 8 | 0 | 0 | Canonical alias duplication is not currently a stable boundary in this focused shape. |
| `multilingual_source_fidelity_card` | 7 | 0 | 1 | Numeric prose source-fidelity improved; remaining miss is hybrid arithmetic. |

Generic repair already made:

- `src/source_record_ledger.py` preserves numeric prose rows when they contain a
  numeric token plus enough prose context.
- This is source addressability only. It does not infer counts, status,
  approval, withdrawal, or causality.
- It does not add source-language word lists.

Verification:

```text
python -m pytest tests\test_source_record_ledger.py -q
16 passed

python -m py_compile src\source_record_ledger.py
passed
```

## Active Pressure Board

| Priority | Boundary | Current Shape | Next Move |
| ---: | --- | --- | --- |
| 1 | `counterfactual_arithmetic_join` | Current total plus excluded/proposed addition count is present, but not assembled as a hypothetical result. | Build an unlike pair before any helper; repair only if the geometry transfers. |
| 2 | `scoped_status_count_support` delivery volume | Transfer succeeded but helper rows were high in unlike replay. | Compress delivery scope without weakening source-fidelity. |
| 3 | trigger audit | Helper bodies may be generic while triggers remain corpus-shaped. | Continue fresh probes for trigger conditions, especially predicate-name and source-form assumptions. |
| 4 | domain transfer | Current evidence is still mostly from the lab corpus plus synthetic probes. | Add small unlike-domain fixtures only when they isolate a named pressure. |

## Next Work

Do this next:

1. Create a focused unlike pair for counterfactual arithmetic joins.
2. Run compile/QA on OpenRouter at 6 lanes or fewer.
3. Classify before repair:
   - if current total and increment are absent, it is compile-surface;
   - if present but not assembled, it is hybrid-join;
   - if the judge misses supported arithmetic, it is answer-surface.
4. Repair only if the pair shows a reusable geometry.
5. Journal the result as BH-027 with before, prediction, intervention, after,
   artifacts, verification, lesson, and next pressure.

## OpenRouter Rule

Default hosted pressure to 6 lanes or fewer. Wider runs produced provider 429s
and lower practical throughput.

## Stop Conditions

Stop a hunt lane when remaining coordinates are:

- transport/provider failures;
- judge-only ambiguity;
- source-fidelity singletons best left as exact source fallback;
- fixture-language leaks that should remain in history;
- low-count residue with no repeated geometry across unlike artifacts.

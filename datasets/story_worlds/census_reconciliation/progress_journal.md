# Census Reconciliation Progress Journal

Fixture id: `census_reconciliation`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## CR-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming_validation_20260508_new6\census_reconciliation`

Files admitted:

- `source.md` / `story.md`
- `fixture_notes.md`
- `qa.md`
- `qa_questions.jsonl`
- `oracle.jsonl`
- `qa_battery.json`

Benchmark discipline:

- `source.md`/`story.md` is the only cold compile source.
- `oracle.jsonl`, `qa_battery.json`, `qa.md`, and `fixture_notes.md` are scoring/review assets, not compile context.
- No Python source-prose interpretation is allowed.

## CR-001 - Query-Only Classification Conversion Effect

Date: 2026-05-08

Evidence lane: `query_helper`

Cold smoke q009 asked whether Building B's condominium-to-townhome conversion
changed the total unit count. The compile had already admitted the necessary
rows:

- `conversion_effective_date(unit_c13..unit_c18, condominium, townhome)`
- `unit_count(condominium, 24)` and `unit_count(condominium, 18)`
- `unit_count(townhome, 36)` and `unit_count(townhome, 42)`

The failure was a query/join surface, not a missing-source surface. The baseline
answer compared `total_base=144` against `total=156`, thereby mixing the
pre-annexation base with the post-annexation total and missing that the
conversion itself was a balanced classification shift.

Implementation:

- Added `classification_conversion_effect_support/4` as a query-only companion
  in `scripts/run_domain_bootstrap_qa.py`.
- The helper fires only when `conversion_effective_date/3` is already queried.
- It derives zero total-count effect only when admitted source-type decreases
  and target-type increases balance over admitted converted units.
- It writes no durable facts and reads no source prose.

Verification:

- Unit test: `test_conversion_effect_query_adds_balanced_classification_count_companion`
- `python -m pytest tests\test_domain_bootstrap_qa.py -q`
  - `34 passed`
- q009 replay:
  - artifact: `tmp\incoming_6_census_no_effect_probe_20260508\q009\domain_bootstrap_qa_20260508T083548778307Z_qa_qwen-qwen3-6-35b-a3b.json`
  - `1 exact / 0 partial / 0 miss`
  - `0` runtime load errors
  - `0` write proposals

Meaning lesson:

Classification conversions, reassignments, and category changes can be
conservation problems. If admitted rows show an equal decrease in one class and
increase in another for the same existing units, the query layer may expose a
`no_change` total-count effect. This is a helper surface, not a compile lens:
missing converted units or missing before/after class counts must still be
compiled explicitly.

## CR-002 - Census Accounting Helper Surface

Date: 2026-05-08

Evidence lane: `query_helper`

Full-40 baseline left Census at `29 / 1 / 10`. The weak rows clustered around
accounting and current-state effects rather than a single missing prose span:

- Lot 52 current one-unit/one-assessment status after deferred reclassification
- vacancy not affecting voting eligibility
- assessment revenue total
- Building B conversion revenue delta

Implementation:

- Added `assessment_revenue_support/6` as a query-only companion over admitted
  `unit_count/2`, `assessment_rate/2|3`, and conversion rows.
- Added `conversion_assessment_delta_support/5` over admitted conversion count
  and admitted before/after assessment rates.
- Added `classification_deferral_effect_support/5` over admitted
  `classification_deferred/2`, `conditional_outcome/3`, and current total count.
- Added `vacancy_voting_eligibility_support/3` over admitted all-units voting
  eligibility and vacant-unit rows.
- Added `assessment_transfer_policy_support/6` over repeated admitted
  `assessment_responsibility/4` intervals.

Verification:

- Unit test: `python -m pytest tests\test_domain_bootstrap_qa.py -q`
  - `39 passed`
- Helper probe:
  - artifact: `tmp\census_helper_probe_20260508\domain_bootstrap_qa_20260508T132835192560Z_qa_qwen-qwen3-6-35b-a3b.json`
  - weak rows: `5 exact / 0 partial / 6 miss`
- Transfer policy probe:
  - artifact: `tmp\census_transfer_policy_probe_20260508\domain_bootstrap_qa_20260508T133410108549Z_qa_qwen-qwen3-6-35b-a3b.json`
  - q037: `1 exact / 0 partial / 0 miss`

Meaning lesson:

HOA-style census fixtures expose a reusable accounting substrate. When the KB
already admits counts, rates, conversion deltas, deferred classification
outcomes, and responsibility intervals, the query layer should expose derived
support tables for totals, deltas, current deferred effects, and repeated
policy patterns. This is not prose interpretation: the helper only computes
over admitted rows and names its derivation surface explicitly.

## CR-003 - Narrow Current-State And Source-Ledger Compiles

Date: 2026-05-08

Evidence lane: `scoped_source_surface_repair`

After CR-002, six rows still needed source surfaces that the cold compile did
not admit compactly:

- q016 Lot 52 dispute basis and bylaw/non-enforcement claim
- q023 Highmark Homes four-unit unsold inventory
- q033 Building B revised notice status
- q036 Building B conversion effective date
- q037 transfer assessment responsibility policy
- q039 Open Item 3 / Vickers GPS cross-reference error

Two narrow compiles were run:

- current-state accounting compile:
  - artifact: `tmp\census_current_state_compile_20260508\domain_bootstrap_file_20260508T133038285126Z_source_qwen-qwen3-6-35b-a3b.json`
  - targeted QA: `3 exact / 1 partial / 2 miss`
- Lot 52 / open-items source-ledger compile:
  - artifact: `tmp\census_lot52_open_items_compile_20260508\domain_bootstrap_file_20260508T133623014182Z_source_qwen-qwen3-6-35b-a3b.json`
  - targeted QA: `2 exact / 0 partial / 0 miss`

Combined comparison:

- artifact: `tmp\incoming_6_full40_qa_20260508\census_multisurface_comparison.md`
- baseline: `29 / 1 / 10`
- diagnostic row-gated upper bound: `40 / 0 / 0`
- rescued rows: `11`
- baseline exact regressions: `0`

Meaning lesson:

The right acquisition surface was not another broad compile. Census needed two
small named surfaces: current administrative state/accounting, and a
source-ledger pass for exact dispute/open-item language. The distinction
matters: arithmetic and repeated responsibility patterns belong in helpers;
bylaw claims, cross-reference errors, notice status, and open-item text belong
in scoped source surfaces.

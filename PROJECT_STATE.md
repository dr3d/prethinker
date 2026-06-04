# Project State

Last updated: 2026-06-03

## One-Sentence Shape

Prethinker is currently a research instrument for testing whether LLM-proposed,
closed, lens-scoped predicate domains can compile messy official documents into
auditable typed facts under strict deterministic governance.

## Current Center

The active research question is:

```text
Can a closed predicate domain, built from a small seed set, transfer hard-clean
to unseen messy official documents in the same family under strict governance?
```

Current evidence says: yes for recurring official-document skeleton anatomy;
not yet for open-ended substantive detail.

The current front-door documents are:

- `docs/CLOSED_DOMAIN_PREDICATE_PACKS_TECHNICAL_NOTE.md`
- `docs/CURRENT_RESEARCH_HEADLINE.md`
- `docs/DOMAIN_PACK_RESEARCH_EVIDENCE.md`
- `docs/DOMAIN_PACK_STATUS.md`
- `docs/DOMAIN_ACCOUNTABILITY_STATUS.md`
- `docs/DOMAIN_PREDICATE_PROPOSAL_STATUS.md`
- `docs/ACTIVE_RESEARCH_LANES.md`
- `docs/DOMAIN_PREDICATE_SCHEMA_PROCESS.md`
- `docs/PUBLIC_DOCS_GUIDE.md`

Older 80.5%, 92.33%, 95%, 98.5%, and 99% measurements remain historical
calibration evidence only. Some were contaminated by prose-smuggling paths:
source/display text, question-shape routing, and judge-facing answer tokens
helped rows score exact without proving typed derivation. They are not current
claim-bearing metrics unless a newer note explicitly re-gates them under the
current hard-clean conditions.

## Claim-Bearing Gates

A domain-pack result is claim-bearing only when the named run satisfies the
gates relevant to that result:

- closed profile registry;
- lens-scoped offered signatures;
- N>=3 same-condition compiles;
- support>=2 for supported expected facts;
- 0 supported forbidden facts;
- registered signatures only;
- atom-shape pass;
- lens-scope pass;
- carrier value-domain pass where applicable;
- sign-clean audit pass for current code where applicable;
- no source-record prose matching;
- no query-text routing;
- no fixture vocabulary;
- no prose-shaped atoms in the winning path.

Targeted replays are mechanism evidence, not transfer claims. Composed
historical runs are diagnostic unless a fresh same-condition bundle reproduces
them.

## Current Evidence

```text
SEC Form 8-K skeleton pack
  seed micro: 13 / 13
  transfer_001: 13 / 13
  transfer_002: 12 / 12
  transfer_003: 12 / 12
  forbidden support: 0 in all claim-bearing cells
  read: strongest current methods example that a small closed skeleton pack
    can transfer across unlike same-family official documents

FDA warning-letter pack
  transfer_001 current replay: 26 / 26, 0 / 9 supported forbidden
  transfer_002 fresh current-pack bundle: 20 / 27, 0 / 7 supported forbidden
  transfer_003 archived replay: 18 / 26, 0 / 10 supported forbidden,
    current integrity fail
  read: primary richer case study; skeleton/citation/regulatory boilerplate
    transfer better than wrapper role semantics, context-dependent categories,
    response/detail value flesh, and other substance lanes
  proposal review: `fda_response_documentation_gap/5` blind review on
    transfer_002 found 0 expected / 13 forbidden; stable candidate emissions
    for violations 1, 2, and 3 are false positives

NTSB investigation pack
  seed micro: 13 / 13
  first unlike transfer: 18 / 25 manifest
  deterministic reducer replay: 19 / 25
  forbidden support: 0 / 15
  read: corroborating boundary evidence; wrapper, chronology, vehicles, and
    conditions transfer more cleanly than casualty, safety-action attachment,
    findings, and probable-cause substance
```

The publishable technical shape is narrow:

```text
Closed, lens-scoped predicate domains can stabilize recurring official-document
anatomy under strict governance. Open-ended substance remains an abstention or
lower-tier boundary unless a compact domain layer reproduces on unlike
documents.
```

This does not support claims of 90%+ general QA accuracy, arbitrary-domain
document understanding, product readiness, or self-serve schema induction.

## Active Architecture

```text
source document family
  -> closed domain profile
  -> lens-scoped offered predicate signatures
  -> LLM compile proposals
  -> deterministic contract / signature / value-domain admission
  -> typed artifact bundle
  -> deterministic replay and governance gates
  -> claim-bearing rows only if they survive hard-clean checks
```

The important boundary is source meaning versus durable truth:

- LLMs may judge source meaning and propose typed facts inside a closed
  domain/lens scope.
- The LLM may not freely define the instrument language after the domain pack is
  closed.
- Deterministic code may normalize and replay typed atoms.
- Deterministic code may not parse source prose, display text, or query text for
  semantic routing.
- Query and compile must meet on the same governed atoms.
- Predicate sets are offered as a function of lens, not as one global bag
  available to every compile pass.

## Current Research Pressure

The next useful work is not another row-grinding climb. It is to preserve and
explain the current falsifiable result:

- keep `docs/DOMAIN_PACK_STATUS.md` regenerated from
  `scripts/summarize_domain_pack_status.py` so domain/predicate/fixture counts
  are visible without worksheet archaeology;
- keep `docs/DOMAIN_ACCOUNTABILITY_STATUS.md` regenerated from
  `scripts/summarize_domain_accountability_status.py` so omission requirements,
  fixture coverage, and fixture-only omission patterns are visible;
- keep SEC as the formal methods example;
- keep FDA as the richer case study with both positive transfer and boundary
  evidence;
- keep NTSB as corroborating boundary evidence, not as a new grind target;
- keep stale-number re-gating visible as a research finding;
- run answer-judge null controls and oracle-isolation checks before any QA
  metric becomes claim-bearing;
- choose any next domain-pack experiment only if it answers a named research
  gap.

## Non-Claims

The repo should not currently claim:

- 90%+ general Prethinker QA accuracy;
- arbitrary-document understanding;
- product readiness;
- broad FDA warning-letter completion;
- a promoted full NTSB pack;
- self-serve schema induction;
- that a targeted replay is a transfer claim;
- that a composed historical run is equivalent to a fresh same-condition
  bundle;
- that judge exactness alone is a claim-bearing score.

## Operating Notes

- OpenRouter remains the main hosted measurement lane when broad runs are
  necessary, but provider/model/settings metadata must be recorded.
- Local LM Studio remains useful for small probes, package/API development, and
  local-domain experiments when speed and reproducibility are adequate.
- Provider/backend, quantization, context, routing, and prompt packing are
  measurement conditions; see `docs/PROVIDER_RUNTIME_DISCIPLINE_NOTE.md`.
- Durable fixtures belong under `datasets/`.
- Temporary run artifacts may live under `tmp/`; old useful run artifacts can
  be moved to `C:\prethinker_tmp_archive`.
- Old worksheets should not become public front-door state. Active worksheets
  should stay run-scoped and should retire to archive/history once the claim is
  summarized in a current note.

## Verification Commands

Current full-suite result on 2026-06-03:

```text
2360 passed, 59 skipped, 9 strict xfailed, 2 subtests passed
```

The strict xfails are legacy MCP/QA selector expectations from before the
sign-clean reset. They are intentionally not claim-bearing; if one XPASSes,
pytest fails and forces review.

Common local checks:

```powershell
$env:PYTHONPATH='.'
pytest -q
python scripts\validate_domain_predicate_schema.py --root datasets\domain_profiles
python scripts\summarize_domain_pack_status.py --out-md docs\DOMAIN_PACK_STATUS.md --out-json tmp\domain_pack_status_current.json
python scripts\summarize_domain_accountability_status.py --out-md docs\DOMAIN_ACCOUNTABILITY_STATUS.md --out-json tmp\domain_accountability_status_current.json
python scripts\validate_domain_predicate_proposals.py --out-md docs\DOMAIN_PREDICATE_PROPOSAL_STATUS.md --out-json tmp\domain_predicate_proposal_status.json
```

Before a public/docs cleanup commit, also run stale-claim greps over
`README.md`, `PROJECT_STATE.md`, `docs/*.md`, and `docs/index.html`.

## Next Decision

This phase is close enough to land as a technical note. The next decision is
whether to:

1. stop and publish the narrow domain-pack transfer finding as the current
   research milestone;
2. run one bounded follow-up that strengthens a missing cell in the note;
3. select a new document family only if it tests a named gap in the closed-pack
   thesis rather than chasing a higher-looking score.

If new research continues, it should start from the phase-close note and the
claim-bearing gates above, not from historical QA-score targets.

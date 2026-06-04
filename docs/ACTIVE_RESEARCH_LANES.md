# Active Research Lanes

Last updated: 2026-06-04

This page is the compact public map of current work. It is not a rolling
session journal. Older lane notes, fixture-specific repair slices, retired
compatibility experiments, and generated reports live in Git history or the
local cold archive.

## Operating Rule

Prethinker's active research asks whether source documents can be compiled into
durable symbolic state, then queried cheaply and safely from the compiled
package.

The mainline technical question is now:

```text
Can a closed predicate domain, built from a small seed set, transfer hard-clean
to unseen messy official documents in the same family under strict governance?
```

This is a lab/research priority, not a product sprint. Product packaging may
follow, but current work is judged by falsifiable compile stability, transfer,
reproducibility, abstention boundaries, and failure-class evidence.

Current default:

```text
source document
  -> compile into admitted predicates, epistemic state, deterministic ledgers,
     manifests, diagnostics
  -> answer from direct KB surfaces and deterministic ledgers
  -> repair only with fixture-free, replay-tested architecture
```

Do not promote a repair because it helps one fixture, row, answer string, or
dataset label. Promote only when the principle survives unlike probes.

## Live Lanes

| Priority | Lane | Question | Current Surface |
| --- | --- | --- | --- |
| 1 | Closed-domain transfer claim | Can a small closed predicate pack transfer hard-clean across unlike same-family official documents? | `docs/CLOSED_DOMAIN_PREDICATE_PACKS_TECHNICAL_NOTE.md`, `docs/DOMAIN_PACK_RESEARCH_EVIDENCE.md` |
| 2 | Domain predicate process | Can pack construction be described without reopening prose smuggling, fixture vocabulary, or open predicate drift? | `docs/DOMAIN_PREDICATE_SCHEMA_PROCESS.md` |
| 3 | Answer-judge governance | Does the evaluator reject empty evidence, wrong-reference evidence, prose-dependent evidence, and oracle leakage? | `scripts/audit_reference_judge_null_controls.py`, `scripts/audit_redaction_replay.py`, `scripts/audit_typed_plan_replay.py` |
| 4 | Atom-shape and carrier governance | Can compiled atoms stay compact, typed, and contract-governed instead of hiding prose in names or slots? | `scripts/audit_kb_atom_inventory.py`, carrier registry |
| 5 | Fixture-bank predicate packs | Which retained official-document families can become closed, lens-scoped predicate packs without collecting new documents or grinding rows? | `docs/DOMAIN_PACK_STATUS.md`, `docs/DOMAIN_ACCOUNTABILITY_STATUS.md`, `docs/DOMAIN_PACK_RESEARCH_EVIDENCE.md`, domain registries |
| 6 | Overlay discipline | Can ACH and future lenses read compiled evidence without mutating KB truth, QA verdicts, or compile metrics? | `docs/OVERLAY_ARCHITECTURE.md`, `docs/ACH_OVERLAY_PROBE.md` |
| 7 | Provider/runtime discipline | Which model/provider/settings conditions are comparable enough for claims? | `docs/PROVIDER_RUNTIME_DISCIPLINE_NOTE.md`, `docs/MODEL_VARIANCE_PRE_REGISTRATION_20260604.md` |
| 8 | Public face hygiene | Does the repo front door describe the living project without surfacing obsolete claims or generated artifact strata? | `README.md`, `docs/PUBLIC_DOCS_GUIDE.md` |

## Current Architecture Pressure

The direct-surface path is the live instrument: admitted predicates,
deterministic ledgers, predicate contracts, selectors, guards, and query policy.
Retired compatibility adapters are not part of the forward repair path.

The highest-value current pressure is therefore:

- preserve concrete source coordinates as deterministic ledgers;
- compile recurring roles, statuses, quantities, transitions, authority
  envelopes, and source-record distinctions as direct admitted predicates;
- detect when a compile used vague `detail/event` wrappers where concrete
  backbone rows should exist;
- use unlike probes before naming any new surface architecture;
- keep fixture nouns, row IDs, answer strings, and dataset labels out of the
  harness.

## Resource Policy

POWER and OpenRouter are both measurement lanes. Prefer the route that gets
clean evidence fastest:

- use local single-lane runs when LM Studio/POWER is stable and avoids provider
  variance;
- use OpenRouter for parallel cold compiles, external transfer measurements,
  and independent draws;
- default hosted pressure to six lanes or fewer unless provider throughput
  evidence says otherwise;
- tag OpenRouter calls by experiment family, phase, and fixture/corpus so cost
  and speed can be inspected later.

Provider failures are transport evidence, not architecture evidence.

## Domain-Pack Readiness

The project is past the sign-clean reset and is now in a narrow domain-pack
transfer phase. Earlier high product scores are not current claim-bearing
numbers because they depended on source-record prose paths, open predicate
drift, or judge-facing surface tokens. The current claim-bearing move is closed
domain schemas measured by hard-clean gates.

FDA warning letters remain the first wedge, but they are not "done". The
current-gate replay picture is stricter than the older worksheet notes:

```text
transfer_001 local all-lens union replay:
  26 / 26 expected, 0 / 9 supported forbidden, research integrity pass

fda_transfer_judged_qa_v2 deterministic compile-fact QA:
  transfer_001: 78 / 78 exact across N=3
  transfer_002: 59 / 81 exact across N=3, with 7 partial and 15 miss
  combined: 137 / 159 exact = 86.16%
  support>=2: transfer_001 26 / 26; transfer_002 20 / 27
  typed-plan replay: 137 / 137 exact rows replay through registered carriers
  redaction replay: 137 / 137 exact rows survive with 0 prose-dependent rows
  scope: oracle-shaped Prolog fact QA, not messy human query planning

transfer_002 fresh current-pack lens-scoped bundle:
  artifact root:
    C:\prethinker_tmp_archive\cb_lens_20260604\fda-t002-current-pack-fresh-local-20260603-r5-lens-plan-ops-chronology-id-canon
  20 / 27 expected, 0 / 7 supported forbidden
  atom-shape / registered-signature / lens-scope blockers: 0
  boundary residue:
    wrapper role semantics
    context-dependent violation-3 category/substance
    response/detail value flesh
    documentation-gap candidate false positives confirmed by blind review

transfer_003 fresh current-pack local lens bundle:
  artifact root:
    C:\prethinker_tmp_archive\fda_t003_current_pack_20260604\fda-t003-r1
  19 / 26 expected, 0 / 10 supported forbidden
  atom-shape / registered-signature / lens-scope blockers: 0
  boundary residue:
    all seven unsupported expected rows are `fda_violation_detail/5`
    value/detail flesh
```

The v2 judged-QA bundle is the cleanest current FDA compile-fact measurement:
the exact rows replay through registered typed plans and survive redaction, but
the queries are oracle-shaped carrier facts. It should not be described as
messy human QA. The package is now reproducible locally with
`scripts/build_compile_fact_judged_qa.py`, which compares `expected_facts.pl`
against compile JSON typed facts and prints support>=2 summaries by fixture.
The `transfer_001` replay is the clean FDA transfer cell.
`transfer_002` and `transfer_003` are clean boundary cells: current gates hold,
but the richer rows do not all transfer. A blind candidate review of
`fda_response_documentation_gap/5` on `transfer_002` found 0 expected facts and
13 forbidden boundaries, so retained stable documentation-gap emissions for
violations 1, 2, and 3 are false positives. Do not grind `transfer_002` upward
row-by-row; use it to name the current abstention boundary. `transfer_003`
now corroborates the same value/detail-flesh boundary under clean atom/lens
governance, not the older archived integrity-fail story. The
`fda_response_assessment_item/6` proposal remains an unreviewed candidate; the
current proposal-status report warns `candidate_has_no_review_results`, so no
assessment-item support should be cited as a promoted claim. The broader
response-assessment lane remains a 16/17 composed diagnostic rather than a
promoted fresh-compile claim. NTSB investigations are the second fixture-bank
pack candidate. The R1 NTSB micro skeleton currently
holds at 13/13 expected facts with 0/13 forbidden facts under local Qwen
N>=3/support>=2 and clean atom-shape/signature/lens-scope gates. That is a
micro-pack result, not a transfer or product claim.

The first unlike retained NTSB transfer fixture is measured but not promoted.
An older broad all-registry recheck reached 19/25 with 0 supported forbidden
facts and clean atom-shape/signature governance. Focused lens runs showed a
stronger manual diagnostic, and a deterministic lens union built from those
historical focused runs reached 23/25. Those numbers are now treated only as
diagnostic history: a fresh scripted same-condition lens-bundle harness
reproduced at 18/25 before reducers, then 19/25 after a typed-only
condition-value reducer. The current manifest is reducer-aligned.

Current harnessed NTSB transfer status:

```text
ntsb_report:          1 / 1
ntsb_occurrence:      1 / 1
ntsb_occurrence_time: 1 / 1
ntsb_party:           1 / 1
ntsb_vehicle:         2 / 2
ntsb_condition:       5 / 5
ntsb_timeline_event:  6 / 6
ntsb_safety_action:   2 / 3
ntsb_injury_count:    0 / 3
ntsb_finding:         0 / 2
```

Current reducer-aligned compile-fact QA over the same first unlike NTSB
transfer:

```text
rows: 57 / 75 exact
support>=2: 19 / 25
redaction replay: 57 / 57 exact rows survive, 0 prose-dependent
typed-plan replay: 57 / 57 exact rows replay through registered carriers
```

The earlier raw/no-reducer view was `18 / 25` support>=2 and `53 / 75`
per-run exact. The difference is the weather atom variant
(`dry_clear_nighttime` vs related compact weather atoms), not prose support.

That is the current claim-bearing research floor for the first NTSB transfer
fixture. It says the skeleton, chronology, vehicles, and conditions are alive,
but casualty and safety-action recall are not yet stable under the fresh
harness, and findings/probable-cause substance should likely abstain or move to
Tier 2 unless a compact, reproducible finding taxonomy transfers on fresh
documents without prose-shaped slots. The compiler atom-shape gate was also
aligned with the external audit so numeric-leading registered-carrier atoms are
dropped in-path rather than merely reported after the run.

SEC Form 8-K is the third fixture-bank candidate under review. Current status
update, 2026-06-04: the old SEC `13/13, 13/13, 12/12, 12/12` cells below are
historical pre-axis-repair measurements. A later value-axis audit found mixed
item/exhibit role semantics. The schema now splits item structure
(`sec_filing_item/5`), item legal treatment
(`sec_filing_item_treatment/4`), and exhibit legal treatment
(`sec_exhibit/5`), with a typed guard against Item 9.01 item-treatment
misattachments. A follow-up typed guard also blocks item-treatment rows sourced
only from `exhibit_table_row_*` handles and cover-page IXBRL legal-treatment
inference. Repaired transfer_003 Qwen MoE reruns landed at `12/13` and
`11/13`, both with `0` supported forbidden and clean axis/value/atom gates. A
pre-registered stability rerun then landed at `12/13`, again with `0`
supported forbidden and clean atom/signature/lens/value-axis gates. A later
fresh r4 manifest refresh landed at `11/13`, `0/10` supported forbidden, and
`34/39` per-run exact. Treat this as a same-condition `11-12/13` band, not a
fixed single score. Do not use the older SEC cells as a pristine methods-anchor
claim without this caveat. A
repaired breadth check over the retained seed, transfer_001, and
transfer_002 cells landed at `12/13`, `11/13`, and `11/12`, all with `0`
supported forbidden and clean atom/lens gates. The remaining boundary is
exhibit legal-treatment ambiguity, wrapper filing/telephone recall, one
duplicate commission-file value, unstable item-treatment recall, and MoE
jitter rather than prose leakage. A follow-up typed omission-accountability
guard now blocks/drops contradictory SEC signatory omissions and unregistered
omission kind/reason triples; rescoring the repaired transfer_003 stability
artifact stayed at `12/13`, `0/10` supported forbidden, while unexpected
same-signature facts dropped from 2 to 0.
The latest guard and manifest artifacts are
`C:\prethinker_tmp_archive\sec_axis_scope_guard_20260604` and
`C:\prethinker_tmp_archive\compile_fact_unexpected_precision_20260604`; the
latest full governance run passed 13 checks and now prints repeated unexpected
same-signature rows as a standing precision diagnostic. This is governance
cleanup, colder provenance refresh, and precision visibility, not a support
lift.

SEC Form 8-K is the third fixture-bank candidate under review. A closed
skeleton-only registry now exists for filing wrapper, registrant, identifiers,
item headings, exhibits, and signature block. It is a methodology probe for the
research claim above, not a product pack. The first skeleton micro is
governance-clean:

```text
fixture: sec_form_8k_skeleton_v1
local-Qwen lens bundle: N=3, support>=2
post-source-scope-guard support: 9 / 13
after skeleton contract tightening: 12 / 13
after typed exhibit-number normalization: 13 / 13
supported forbidden facts: 0 / 6
atom-shape/signature blockers: 0
```

The first unlike retained SEC Form 8-K skeleton transfer has also run:

```text
fixture: sec_form_8k_skeleton_transfer_001
artifact root: C:\prethinker_tmp_archive\cb_lens_20260604\sec8k-transfer-r3-phone-reducer
gate: C:\prethinker_tmp_archive\cb_gate_20260604\research_integrity_gate_sec8k_t001_r3
local-Qwen lens bundle: N=3, support>=2
initial transfer: 5 / 13, 0 / 7 forbidden
fresh R3 after CIK containment: 12 / 13, 0 / 8 forbidden
R3 replay with typed phone-value reducer: 13 / 13, 0 / 8 forbidden, 0 unexpected
atom-shape/signature/lens-scope blockers: 0
research integrity gate: pass
```

The important result is governance, not the final number. The SEC lane caught
two real leak surfaces before trusting the transfer: prose/semantic payload in
`source_or_scope`, and unstated CIK identifiers inferred from model prior
knowledge. Those historical pre-axis-repair cells are no longer the current SEC
claim. The repaired breadth check is the current read: useful skeleton transfer
evidence, but with boundary rows that keep SEC from being a pristine methods
anchor.

The second unlike retained SEC Form 8-K skeleton transfer completed under local
Qwen N=3/support>=2:

```text
fixture: sec_form_8k_skeleton_transfer_002
artifact root: C:\prethinker_tmp_archive\cb_lens_20260604\sec8k-t002-r3-date
supported expected facts: 12 / 12
supported forbidden facts: 0 / 6
unexpected same-signature facts: 1
registered fact/signature rate: 100%
atom-shape/signature/lens-scope blockers: 0
```

The one unexpected row is a single-run signatory-name normalization variant and
is not being repaired until it blocks transfer. The useful intervention was a
contract boundary on `sec_filing/6`: wrapper event date must come from the
cover-page Date of Report / Date of Earliest Event Reported field, while
`filing_date` requires an explicitly labeled filed/submitted/accession date or
else `not_stated`. This keeps item-body events and signature dates out of the
wrapper carrier.

The third unlike retained SEC Form 8-K skeleton transfer used a Blackstone
Form 8-K/A amendment and historically passed before the value-axis repair:

```text
fixture: sec_form_8k_skeleton_transfer_003
artifact root: C:\prethinker_tmp_archive\cb_lens_20260604\sec8k-t003-r1
supported expected facts: 12 / 12
supported forbidden facts: 0 / 10
unexpected same-signature facts: 1
registered fact/signature rate: 100%
atom-shape/signature/lens-scope blockers: 0
research integrity gate: pass
```

That third run required only bounded recurring-palette expansion before
measurement: `form_8_k_a` and `results_of_operations_financial_condition`. It
does not prove event-substance extraction, and after the later value-axis repair
it is historical evidence rather than the current SEC score.

A historical local deterministic compile-fact QA replay over the SEC seed plus
all three transfers gives the complementary pre-axis-repair per-run view:

```text
rows: 144 / 150 exact, 4 partial, 2 miss
support>=2 by fixture:
  seed: 13 / 13
  transfer_001: 13 / 13
  transfer_002: 12 / 12
  transfer_003: 12 / 12
redaction replay: 144 / 144 exact rows survive, 0 prose-dependent
typed-plan replay: 144 / 144 exact rows replay through registered carriers
```

The per-run misses/partials were not a contradiction of that historical SEC
transfer claim; today, use the repaired breadth check above as the current SEC
read.

The pre-registered repaired-schema stability rerun has now been run. Next SEC
work should only occur if a specific research question requires deliberately
testing whether adding a narrow event-substance carrier breaks skeleton
stability. Do not add event-substance carriers by default.

OSHA accident/inspection is the fourth fixture-bank family under review. A
closed skeleton/table registry now exists for inspection wrapper,
establishment, accident, injured employees, violation counts, penalties,
violation item/status, and related activity. The probe is deliberately narrow:
it tests whether retained OSHA accident/inspection tables can compile into
closed typed facts under the same gates, not whether Prethinker understands
OSHA reports broadly.

The seed micro initially exposed a harness bug: profile-registry lens intake
only preserved `/1` through `/6` signatures, so the OSHA `/7` and `/8`
carriers never reached the planner. That was fixed generically by accepting
registered signatures through `/8` while keeping `/9` and higher rejected; it
is not an OSHA-specific reducer.

Current OSHA seed status:

```text
fixture: osha_incident_domain_v1
artifact root: C:\prethinker_tmp_archive\osha_incident_domain_probe_20260604\osha-incident-domain-v1-r2-local-arity-fix
local-Qwen lens bundle: N=3, support>=2
supported expected facts: 18 / 20 using constant-slot support report
supported forbidden facts: 0 / 8
atom-shape/signature/lens-scope blockers: 0
boundary rows: inspection wrapper absent; establishment row 1/3
```

The first unlike retained OSHA transfer also ran under the same local settings:

```text
fixture: osha_incident_transfer_001
artifact root: C:\prethinker_tmp_archive\osha_incident_domain_probe_20260604\osha-incident-transfer-001-r1-local
local-Qwen lens bundle: N=3, support>=2
supported expected facts: 12 / 15
supported forbidden facts: 0 / 8
atom-shape/signature/lens-scope blockers: 0
per-run union facts: 13, 3, 16
boundary rows: inspection wrapper absent, establishment 1/3,
  related activity emits no/no where oracle expected not_stated/not_stated
```

Two additional retained OSHA probes tried to raise OSHA to the SEC transfer bar.
They should be read as diagnostics, not promoted cells:

```text
fixture: osha_incident_transfer_002
artifact root:
  C:\prethinker_tmp_archive\osha_incident_domain_probe_20260604\osha-incident-transfer-002-r1-local-long-table-boundary
local-Qwen lens bundle: N=3, support>=2
supported expected facts: 18 / 53
supported forbidden facts: 0 / 8
atom-shape/signature/lens-scope blockers: 0
read: clean long-table boundary; summary counts, penalties, related activity,
  and first four citation items stabilize, but the 16-item citation/status
  inventory does not.

fixture: osha_incident_transfer_003
artifact root:
  C:\prethinker_tmp_archive\osha_incident_domain_probe_20260604\osha-incident-transfer-003-r1-local-mixed-doc-forbidden-rescore
local-Qwen lens bundle: N=3, support>=2
supported expected facts: 2 / 21
supported forbidden facts: 0 / 10 after the typed accident-omission
  contradiction guard
atom-shape/signature/lens-scope blockers: 0
read: clean mixed-document boundary; support remains 2 / 21, but the current
  news-release trench accident and injury rows are now blocked from
  contaminating the appended prior-inspection id by typed fact consistency.
  This is still not a promoted transfer cell.
```

OSHA strengthens the cross-family pattern without changing the research claim:
accident/injury rows and violation table anatomy transfer better than wrapper
rows, blank-value semantics, long-table enumeration, and mixed-source section
attachment. Keep it as fourth-family corroboration; do not grind the wrapper
or mixed-document lanes unless a named research question requires it.

Before the next technical claim:

1. Keep FDA as the primary case study and keep the per-layer boundary table
   current before reopening any row-level lane.
2. Preserve SEC Form 8-K as a boundary-aware skeleton-pack case study unless a
   pre-registered repaired-schema rerun materially tightens the current
   seed/transfer boundary.
3. Use NTSB as boundary evidence for what transfers, what abstains, and what
   becomes lower tier.
4. Keep OSHA as fourth-family corroboration for skeleton/table transfer and
   compile variance, not as a new row-grinding target.
5. Run answer-judge null controls and oracle-isolation checks for any
   LLM-judged QA result that becomes claim-bearing; deterministic compile-fact
   QA still needs typed-plan and redaction replay.
6. Report transfer, reproducibility, abstention boundaries, and failure classes
   together; do not turn a clean sub-layer into a broad accuracy claim.
7. Treat stale-number re-gating as a first-class research finding: older clean
   cells are historical unless they survive today's gates.

## What Stays Off The Front Door

Do not resurface retired lab-automation, publishing, public-benchmarking,
generated report explorer, old compatibility-residue, or dated run-log strata
in public entry points. Git history keeps that material. The current repo
should remain a sharp map of the instrument as it exists now.

# Active Research Lanes

Last updated: 2026-06-03

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
| 1 | Domain tier strategy | Can one closed document-type schema produce verified Tier 1 answers while the general compiler remains a lower-trust fallback? | `docs/DOMAIN_TIER_STRATEGY.md` |
| 2 | Per-answer-class hard-clean table | Which answer classes survive the hard-clean gate, and which substantive classes need domain predicates? | `docs/DOMAIN_TIER_WORKSHEET.md`, archive artifacts |
| 3 | Answer-judge governance | Does the evaluator reject empty evidence, wrong-reference evidence, prose-dependent evidence, and oracle leakage? | `scripts/audit_reference_judge_null_controls.py`, `scripts/audit_redaction_replay.py`, `scripts/audit_typed_plan_replay.py` |
| 4 | Atom-shape and carrier governance | Can compiled atoms stay compact, typed, and contract-governed instead of hiding prose in names or slots? | `scripts/audit_kb_atom_inventory.py`, carrier registry |
| 5 | Fixture-bank predicate packs | Which retained official-document families can become closed, lens-scoped predicate packs without collecting new documents or grinding rows? | `docs/FIXTURE_BANK_PREDICATE_PACK_WORKSHEET.md`, domain registries |
| 6 | Overlay discipline | Can ACH and future lenses read compiled evidence without mutating KB truth, QA verdicts, or compile metrics? | `docs/OVERLAY_ARCHITECTURE.md`, `docs/ACH_OVERLAY_PROBE.md` |
| 7 | Provider/runtime discipline | Which model/provider/settings conditions are comparable enough for claims? | `docs/PROVIDER_RUNTIME_DISCIPLINE_NOTE.md` |
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

## Reset And Domain-Pack Readiness

The project is in a sign-clean reset, not a release freeze. Earlier high product
scores remain useful history, but they are not current claim-bearing numbers
because they depended on source-record prose paths, open predicate drift, or
judge-facing surface tokens.

The reset hard-road floor on the 8-fixture English batch was:

```text
Product exact:                  88 / 200 = 44.0%
Typed-plan exact:               84 / 200 = 42.0%
Redaction-survived exact:       81 / 200 = 40.5%
Atom-shape-clean product exact: 84 / 200 = 42.0%
Hard-clean floor:               73 / 200 = 36.5%
```

This remains useful reset context, not the current headline claim. It says the
general typed layer is alive but not sufficient as the whole research claim.
The current claim-bearing move is closed domain schemas measured by the same
hard-clean gates.

FDA warning letters remain the first wedge, but they are not "done". The
current-gate replay picture is stricter than the older worksheet notes:

```text
transfer_001 local all-lens union replay:
  26 / 26 expected, 0 / 9 supported forbidden, research integrity pass

transfer_002 fresh current-pack lens-scoped bundle:
  artifact root:
    tmp/domain_lens_bundle/fda-t002-current-pack-fresh-local-20260603-r5-lens-plan-ops-chronology-id-canon
  20 / 27 expected, 0 / 7 supported forbidden
  atom-shape / registered-signature / lens-scope blockers: 0
  boundary residue:
    wrapper role semantics
    context-dependent violation-3 category/substance
    response/detail value flesh

transfer_003 archived single-lens replay:
  18 / 26 expected, 0 / 10 supported forbidden
  research integrity fail: atom-shape
```

The `transfer_001` replay is the clean FDA transfer cell. `transfer_002` is now
the clean boundary cell: current gates hold, but the richer rows do not all
transfer. Do not grind `transfer_002` upward row-by-row; use it to name the
current abstention boundary. `transfer_003` remains archived boundary/blocker
evidence until it is rerun as a fresh current-pack bundle or deliberately left
out of the claim. The response-assessment lane remains a 16/17 composed
diagnostic rather than a promoted fresh-compile claim. NTSB investigations are
the second fixture-bank pack candidate. The R1 NTSB micro skeleton currently
holds at 13/13 expected facts with 0/13 forbidden facts under local Qwen
N>=3/support>=2 and clean atom-shape/signature/lens-scope gates. That is a
micro-pack result, not a transfer or product claim.

The first unlike retained NTSB transfer fixture is measured but not promoted.
An older broad all-registry recheck reached 19/25 with 0 supported forbidden
facts and clean atom-shape/signature governance. Focused lens runs showed a
stronger manual diagnostic, and a deterministic lens union built from those
historical focused runs reached 23/25. Those numbers are now treated only as
diagnostic history: a fresh scripted same-condition lens-bundle harness
reproduced at 18/25, then 19/25 after a typed-only condition-value reducer.

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

That is the current claim-bearing research floor for the first NTSB transfer
fixture. It says the skeleton, chronology, vehicles, and conditions are alive,
but casualty and safety-action recall are not yet stable under the fresh
harness, and findings/probable-cause substance should likely abstain or move to
Tier 2 unless a compact, reproducible finding taxonomy transfers on fresh
documents without prose-shaped slots. The compiler atom-shape gate was also
aligned with the external audit so numeric-leading registered-carrier atoms are
dropped in-path rather than merely reported after the run.

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
artifact root: tmp\domain_lens_bundle\sec8k-transfer-r3-phone-reducer
gate: tmp\research_integrity_gate_sec8k_t001_r3
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
knowledge. Current SEC status is therefore "one seed micro plus three unlike
skeleton transfers passed under hard governance," not an SEC product claim.

The second unlike retained SEC Form 8-K skeleton transfer completed under local
Qwen N=3/support>=2:

```text
fixture: sec_form_8k_skeleton_transfer_002
artifact root: tmp\domain_lens_bundle\sec8k-t002-r3-date
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
Form 8-K/A amendment and also passed:

```text
fixture: sec_form_8k_skeleton_transfer_003
artifact root: tmp\domain_lens_bundle\sec8k-t003-r1
supported expected facts: 12 / 12
supported forbidden facts: 0 / 10
unexpected same-signature facts: 1
registered fact/signature rate: 100%
atom-shape/signature/lens-scope blockers: 0
research integrity gate: pass
```

That third run required only bounded recurring-palette expansion before
measurement: `form_8_k_a` and `results_of_operations_financial_condition`. It
does not prove event-substance extraction. It says the SEC skeleton domain pack
now has one seed micro and three unlike skeleton transfers under hard
governance.

Next SEC work should either summarize the methodology evidence across FDA,
NTSB, and SEC or deliberately test whether adding SEC event-substance carriers
breaks the skeleton stability. Do not add event-substance carriers by default.

Before the next technical claim:

1. Keep FDA as the primary case study and keep the per-layer boundary table
   current before reopening any row-level lane.
2. Preserve SEC Form 8-K as the clean skeleton-pack methodology example.
3. Use NTSB as boundary evidence for what transfers, what abstains, and what
   becomes lower tier.
4. Run answer-judge null controls and oracle-isolation checks for any QA result
   that becomes claim-bearing.
5. Report transfer, reproducibility, abstention boundaries, and failure classes
   together; do not turn a clean sub-layer into a broad accuracy claim.
6. Treat stale-number re-gating as a first-class research finding: older clean
   cells are historical unless they survive today's gates.

## What Stays Off The Front Door

Do not resurface retired lab-automation, publishing, public-benchmarking,
generated report explorer, old compatibility-residue, or dated run-log strata
in public entry points. Git history keeps that material. The current repo
should remain a sharp map of the instrument as it exists now.

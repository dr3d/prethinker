# Fixture Bank Predicate Pack Worksheet

Status: active lab notes, June 3, 2026. This worksheet records internal
predicate-pack construction from fixtures already retained under `datasets/`.
It is not a public scorecard and it should not become a rolling history dump.

## Operating Rule

Use the existing fixture bank to test whether bounded official-document
families can be compiled into closed, lens-scoped predicate packs. Do not
collect new documents until the existing bank has answered the first-order
question: which document families have stable recurring anatomy, and which
families only look useful because row-level fixtures were overworked?

Pack work must preserve the post-reset boundary:

- LLM proposes source meaning inside an offered lens-scoped predicate set.
- Deterministic validators admit, reduce, reject, or abstain.
- Query planning may see the compiled atom inventory and the user question,
  but deterministic Python must not parse source prose or question prose to
  recover meaning.
- A pack does not promote until N>=3 same-condition runs, support>=2,
  value-domain gates, atom-shape gates, redaction replay, typed-plan replay,
  and unlike-document transfer hold.

## Existing Fixture Bank Inventory

Approximate retained fixture counts from `datasets/` as of June 3, 2026 after
FDA and NTSB pack work:

| Candidate family | QA-style fixtures | Typed micro-fixtures | Read |
| --- | ---: | ---: | --- |
| FDA warning letters | 12+ | 8+ | First wedge; useful but not done. Current replay of transfer_001 local all-lens union is clean at 26/26 with integrity pass; fresh current-pack transfer_002 is a clean boundary cell at 20/27 with 0 forbidden; archived transfer_003 replay fails current integrity gates and is blocker evidence. |
| NTSB investigations | 16 | 2 | Second pack-process test. Skeleton/chronology/conditions transfer, but fresh harness manifest is 18/25 and deterministic R2 reducer replay is 19/25, with casualty/safety instability and findings abstention. |
| SEC / corporate disclosure | 14 | 4 | Strong official-document scaffold; Form 8-K skeleton micro reaches 13/13 and three unlike retained transfers now hold at 13/13, 12/12, and 12/12 under hard governance. |
| OSHA / workplace enforcement | 11 | 0 | Good regulatory table/narrative pressure; less current schema machinery. |
| Court / legal orders | 8 | 0 | Valuable but likely needs legal-disposition/findings schema before claim. |
| Procurement / PUC / state AG / labor board | 3 each | 0 | Smaller pilot families; useful after one more full pack proves process. |
| Narrative / story probes | 57 | 0 | Boundary probe lane, not first product-like predicate pack. |
| Non-English probes | 8 | 0 | Sign test only; not current market target. |

Decision: freeze FDA response-assessment row grinding and treat NTSB as a
boundary/process test, not a promoted pack. SEC has since become the cleanest
small skeleton-pack methodology probe. The next fixture-bank work should
strengthen the FDA case-study evidence or formalize the SEC method result, not
continue grinding Teutopolis transfer residue.

## R1 NTSB Pack Skeleton

Fixture samples reviewed:

- `datasets/real_world_transfer/fresh_ugly_public_20260524_01/ntsb_aviation_ugly_001`
- `datasets/real_world_transfer/fresh_ugly_public_20260524_01/ntsb_marine_ugly_001`
- `datasets/real_world_transfer/fresh_ugly_public_20260524_02/ntsb_surface_ugly_001`
- ACH payloads under `fresh_ach_stress_public_20260528_*`

Recurring source anatomy:

- report wrapper: report title, report/investigation id, report date/status;
- occurrence wrapper: date, time, location, occurrence kind;
- involved asset identity: aircraft, vessels, barges, cargo tanks, vehicles;
- party roles: operator, owner, crew, pilot/driver, regulator, investigator,
  participating party, emergency responder;
- casualty summary: table partitions by crew/passenger/bystander/driver/first
  responder with fatal/serious/minor counts;
- timeline: event sequence, warnings, response events, inspections, safety
  actions, report/docket dates;
- conditions: weather, visibility, wind, roadway, hazmat class, equipment and
  recorder states, explicit negative findings;
- findings: probable cause, contributing factors, factual findings, negative
  findings.

R1 closed carrier signatures:

```text
ntsb_report/5
ntsb_occurrence/6
ntsb_occurrence_time/5
ntsb_vehicle/6
ntsb_party/5
ntsb_injury_count/6
ntsb_timeline_event/6
ntsb_condition/5
ntsb_safety_action/6
ntsb_finding/5
domain_omission/5
```

Lens-scoped offering:

| Lens | Offered signatures |
| --- | --- |
| `wrapper` | `ntsb_report/5`, `ntsb_occurrence/6`, `ntsb_occurrence_time/5`, `domain_omission/5` |
| `asset_party` | `ntsb_vehicle/6`, `ntsb_party/5`, `domain_omission/5` |
| `casualty` | `ntsb_injury_count/6`, `domain_omission/5` |
| `timeline` | `ntsb_timeline_event/6`, `ntsb_occurrence_time/5`, `ntsb_safety_action/6`, `domain_omission/5` |
| `conditions` | `ntsb_condition/5`, `domain_omission/5` |
| `findings` | `ntsb_finding/5`, `domain_omission/5` |

Deliberate abstentions in R1:

- rich causal explanation text beyond compact findings;
- witness credibility or competing-account analysis;
- ACH matrix generation;
- figure-level arithmetic and multi-step duration calculation;
- full regulatory-violation taxonomies in highway/hazmat reports.

Those may become later overlays or narrower carrier families. They are not
allowed to sneak into R1 via prose-shaped atom values.

## Next Gate

Before running broad NTSB compiles:

1. Validate the NTSB registry against the central carrier contract registry.
2. Add a small typed micro-fixture for the R1 skeleton using one aviation or
   marine fixture excerpt, with expected facts and forbidden prose-shaped
   facts.
3. Run N>=3 same-condition micro compiles and summarize support>=2.
4. Only if the micro holds, run one unlike NTSB transfer fixture.
5. Treat the first NTSB score as a pack-process measurement, not a product
   claim.

## R1 Static Gate Results

Commands:

```text
python scripts\validate_domain_predicate_schema.py --root datasets\domain_profiles
python scripts\validate_typed_micro_fixtures.py --root datasets\compile_micro_fixtures
python -m pytest tests\test_validate_typed_micro_fixtures.py tests\test_validate_domain_predicate_schema.py tests\test_carrier_contract_registry.py
python scripts\audit_sign_clean.py
```

Results:

```text
Domain predicate schemas: 2 registries, 32 predicates, 0 blocking errors, 0 warnings
Typed micro-fixtures: 12 fixtures, 0 blocking errors
Focused governance tests: 43 passed
Sign-clean: pass, 0 blockers, 0 claim-path free-text semantic routing
```

Notable correction:

- The first casualty carrier name was `ntsb_injury_summary/6`. The atom
  inventory treated `summary` as prose-like wrapper vocabulary, which is the
  right failure mode. The carrier was renamed to `ntsb_injury_count/6` before
  any compile run. This is a small but important example of atom-shape
  governance biting before the pack could accumulate a soft wrapper predicate.

Next blocker:

- Run an N>=3 same-condition compile on
  `datasets/compile_micro_fixtures/ntsb_investigation_domain_v1` with the
  `ntsb_investigation_v1` registry and lens-scoped predicates. The desired
  result is not a score claim; it is a stability read on whether the compiler
  can fill the R1 NTSB skeleton without inventing prose-shaped atoms or
  emitting forbidden facts.

## R2 NTSB Local Micro Smoke

Model/runtime:

```text
LM Studio local
model: qwen/qwen3.6-35b-a3b
temperature: 0
top_p: 1.0
num_ctx: 65536
mode: all-registry direct, compile-source
```

R1 smoke before contract tightening:

```text
Admitted facts: 12 / 12 / 10
Exact expected per run: 5/13, 5/13, 6/13
Support>=2: 5/13
Forbidden supported: 0
```

Diagnosis:

- The compiler emitted registered, atom-clean facts, but drifted on subject
  keys and condition granularity.
- The pack name `ntsb_injury_summary/6` tripped the atom-shape/prose-like
  predicate guard and was renamed to `ntsb_injury_count/6` before any score
  claim.
- First contract tightening added stable occurrence-id guidance, no location
  prefixes, recorder-state identity, split visibility/wind, and omission
  handling for preliminary-report "no probable cause yet" language.

R2 smoke after contract tightening:

```text
Admitted facts: 13 / 13 / 12
Support>=2 after source/contract normalization correction: 12 / 13
Forbidden supported: 0 / 8
Atom-shape blockers: 0
Registered fact rate: 1.0
Focused tests: 43 passed
```

Source/contract normalization correction:

- `vehicle_type=boeing_md_11f` is more source-faithful than `md_11f`.
- `condition_kind=visibility` should pair with `condition_value=10_miles`,
  not `ten_miles` or `visibility_10_miles`.
- `condition_kind=wind` should pair with
  `condition_value=310_degrees_4_knots`, not a value that repeats `wind`.

Remaining blocker:

- `ntsb_timeline_event(Occurrence, AccidentTime, occurrence_time,
  t_1713_30_est, start, SrcAccidentTime)` has 0/3 support in the all-registry
  direct compile. The source states the exact time, and the contract now says
  the occurrence date does not replace the occurrence-time timeline row.
  Next test is the `timeline` lens alone: if the row appears there, this is
  all-registry competition; if not, the timeline carrier contract needs a
  stronger event-time admission pattern.

R3 occurrence-time pivot:

- The timeline-only lens still emitted report issue and safety-action facts,
  but not the accident occurrence time.
- It did fix date-atom shape when directly prompted: `v_2025_11_07` and
  `v_2025_11_14` appeared instead of bare numeric-leading date atoms.
- The missing time appears to be a carrier-shape issue, not just all-registry
  competition. NTSB occurrence time is wrapper anatomy, so a narrow
  `ntsb_occurrence_time/5` carrier was added instead of forcing the generic
  `ntsb_timeline_event/6` carrier to carry occurrence-wrapper semantics.
- A numeric-leading atom-shape blocker was added to
  `scripts/audit_kb_atom_inventory.py`; bare atoms such as `10_miles` and
  `2025_11_07` now fail atom-shape governance. The NTSB expected facts now use
  valid atom shapes such as `miles_10`, `degrees_310_knots_4`, `v_...`, and
  `t_...`.

R4 local Qwen restored:

```text
LM Studio endpoint: http://127.0.0.1:1234/v1
model listed: qwen/qwen3.6-35b-a3b
compile mode: local, single-lane, temperature=0, top_p=1.0, num_ctx=65536
```

The first restored run used `ntsb_occurrence_time/5` and produced support for
the missing occurrence-time carrier, but it exposed a source-normalization
decision: the source states the accident date and about-time together. The
expected fact was corrected from `t_1713_30_est` to
`t_2025_11_05_1713_30_est`. The earlier result is therefore diagnostic only,
not a score claim.

R5 strict value-domain gates:

- `ntsb_finding/5` no longer admits `finding_kind=not_stated`; the absence of
  a probable cause in a preliminary report belongs in `domain_omission/5`.
- `ntsb_injury_count/6` count slots must be integers. Atom values such as
  `zero` are invalid even when source-faithful in prose.
- Numeric-leading atom-shape governance now rejects unquoted atoms such as
  `10_miles`, `2025_11_07`, and `1713_30_est`; valid compact forms are
  `miles_10`, `v_2025_11_07`, and `t_...`.

R6 strict fresh local N>=3:

```text
artifact root: tmp\ntsb_domain_r1_occurrence_time_r3_strict_fresh
compile runs: 3
expected fact count: 13
support threshold: >=2
supported expected facts: 13 / 13
unsupported expected facts: 0
forbidden fact count: 13
supported forbidden facts: 0 / 13
unexpected support>=2 facts: 0
single-run unexpected variants: 3
```

Single-run variants to watch before transfer:

- `ntsb_condition(... fdr_recovered_sent_to_lab ...)` appeared in one run.
- `ntsb_occurrence(... louisville_ky ...)` appeared in one run.
- `ntsb_occurrence_time(... t_1713_30_est ...)` appeared in one run.

These do not break the micro skeleton because all expected facts reach
support>=2 and all forbidden facts remain unsupported. They do show where
transfer may pressure canonicalization: recorder-state granularity, location
abbreviation, and time-only versus timestamp identity.

Atom/signature/lens-scope audit over the three strict fresh runs:

```text
atom-shape blockers: 0
registered fact rate: 1.0
unregistered facts: 0
lens-scope blockers: 0
typed fact count: 36
```

Clean checks after the strict fresh run:

```text
python -m pytest tests\test_carrier_contract_registry.py tests\test_domain_bootstrap_file.py::test_carrier_value_domain_integrity_drops_invalid_closed_slot_rows tests\test_validate_typed_micro_fixtures.py tests\test_validate_domain_predicate_schema.py tests\test_summarize_typed_micro_series.py tests\test_audit_kb_atom_inventory.py
65 passed

python scripts\validate_domain_predicate_schema.py --root datasets\domain_profiles
2 registries, 33 predicates, 0 blocking errors, 0 warnings

python scripts\validate_typed_micro_fixtures.py --root datasets\compile_micro_fixtures
12 fixtures, 0 blocking errors
```

Status:

- The NTSB R1 micro skeleton is working under local Qwen with strict atom and
  value-domain governance. This is not yet a transfer claim.
- FDA is not "done." The FDA warning-letter pack remains the strongest current
  wedge, but its evidence must stay separated by provider, transfer cell, and
  current-gate status: transfer_001 local all-lens union currently replays at
  26/26 with 0/9 supported forbidden and research-integrity pass; fresh
  current-pack transfer_002 is governance-clean at 20/27 with 0/7 supported
  forbidden and documents the current boundary; archived transfer_003 replays
  at 18/26 with atom-shape integrity failure. Response-assessment is parked at
  16/17 composed diagnostic recall rather than promoted.

Next blocker:

- Build or select one unlike NTSB transfer micro from retained `datasets/`
  fixtures. Run the closed `ntsb_investigation_v1` registry against it with the
  same local-Qwen settings. Promotion requires support>=2 over N>=3,
  atom-shape/signature/lens-scope clean, value-domain clean, no forbidden
  support, and no source-prose/query-prose route.

R7 unlike NTSB transfer fixture selected:

- Transfer fixture:
  `datasets/compile_micro_fixtures/ntsb_investigation_transfer_surface_001`
- Source:
  `datasets/real_world_transfer/fresh_ugly_public_20260524_02/ntsb_surface_ugly_001`
- Source type: retained NTSB highway / hazardous-material investigation
  report excerpt, unlike the UPS aviation preliminary micro used for the R1
  NTSB skeleton.

Initial all-registry transfer result:

```text
artifact root: tmp\ntsb_transfer_surface_001_r2_n3_local_qwen
compile runs: 3
expected fact count: 24
support threshold: >=2
supported expected facts: 7 / 24
supported forbidden facts: 0
atom-shape/signature/lens-scope blockers: 0
```

Diagnosis:

- Governance held: the weak transfer score did not come from unregistered
  predicates, prose-shaped atoms, lens leakage, or forbidden rows.
- Main blockers were ordinary domain-pack recall/canonicalization:
  casualty partitions, timeline/safety-action recall, hazmat/speed condition
  split, and vehicle/organization atom stability.
- This is not a promotable NTSB transfer result.

R8 timeline-lens repair:

- The first timeline-only probe exposed a mapper/admission problem rather than
  a source-understanding problem: valid typed timestamps such as
  `t_2023_09_29_204300_cdt` and `t_20230929_2043_cdt` were being rejected or
  counted as different atoms.
- Added temporal acceptance for typed `t_...` atoms and the `not_stated`
  sentinel in temporal slots.
- Added deterministic NTSB timestamp atom reduction:
  `t_2023_09_29_204300_cdt`,
  `t_2023_09_29_2043_00_cdt`, and `t_20230929_2043_cdt`
  converge to `t_2023_09_29_2043_cdt`.
- Added admission diagnostics to whole-source compile artifacts so skipped
  mapper operations remain inspectable.

Fresh timeline N>=3 after timestamp normalization:

```text
artifact root: tmp\ntsb_transfer_surface_001_timeline_r5_n3_local_qwen
compile runs: 3
expected timeline/safety facts: 9
support threshold: >=2
supported expected facts before actor reducer: 8 / 9
supported expected facts with reducer-aware analysis: 9 / 9
supported forbidden facts: 0 / 2
atom-shape/signature/lens-scope blockers: 0
```

The remaining pre-reducer miss was not source reasoning. All three runs emitted
the Teutopolis hazmat-training action, but actor ids drifted among
`org_teutopolis_fd`, `org_teutopolis_fire`, and the expected
`org_teutopolis_fire_dept`.

R9 typed actor-id reducer:

- Added deterministic NTSB safety-action actor normalization for compact fire
  department actor ids only:
  `org_X_fd`, `org_X_fire`, and `X_fire_department` become
  `org_X_fire_dept`.
- This reducer is typed-value normalization only. It does not read source
  prose or query text.
- Added the reducer to the compiler path and to reducer-aware summary/union
  tooling.

Fresh local-Qwen timeline N>=3 with the reducer in the compiler path:

```text
artifact root: tmp\ntsb_transfer_surface_001_timeline_r6_n3_local_qwen
wallclock: 82 seconds for 3 local LM Studio compiles
compile runs: 3
expected timeline/safety facts: 9
support threshold: >=2
supported expected facts: 8 / 9
supported forbidden facts: 0 / 2
atom-shape/signature/lens-scope blockers: 0
```

The actor row stayed fixed, but a different source-faithfulness issue surfaced:
the source has two closure statements. At 8:55 p.m. approaches were ordered
closed; by 9:06 p.m. both directions were closed. The old oracle had only one
generic `road_closure` row at 9:06 p.m., while the compiler often emitted the
8:55 p.m. closure-order event.

R10 closure-stage schema probe:

- Added governed `event_kind` values `road_closure_ordered` and
  `road_closure_completed`.
- Updated the transfer oracle to represent both source-stated closure events:
  8:55 p.m. ordered closure and 9:06 p.m. completed closure.
- Fresh local-Qwen R7 N>=3 showed the split is understood, but not promotable:

```text
artifact root: tmp\ntsb_transfer_surface_001_timeline_r7_n3_local_qwen
compile runs: 3
expected timeline/safety facts: 10
support threshold: >=2
supported expected facts: 4 / 10
supported forbidden facts: 0 / 2
atom-shape/signature/lens-scope blockers: 0
```

Diagnosis:

- The two closure-stage rows were stable at 3/3, which supports the source
  anatomy refinement.
- The added closure-stage pressure destabilized unrelated rows: distress-call
  sequence role, mutual-aid/road-reopen recall, and safety-action actor
  assignment.
- This is a negative prompt-contract result, not an improvement to promote.
  The schema split can stay as source-faithful vocabulary, but the timeline
  lens remains blocked on stable sequence/actor construction.

Current NTSB status:

- Micro skeleton: 13/13 strict local N>=3, clean governance.
- Unlike transfer all-registry: 7/24, clean governance, not promotable.
- Unlike transfer timeline lens:
  - 8/9 under the simpler closure oracle after typed timestamp and actor-id
    normalization.
  - 4/10 under the stricter source-faithful closure-stage oracle.
- No NTSB transfer claim is available yet.

Next NTSB blockers:

1. Do not keep polishing the closure-stage prompt. The experiment showed
   instability outside the closure rows.
2. Run the other transfer lenses separately (`asset_party`, `casualty`,
   `conditions`, `findings`) under local Qwen N>=3 to determine whether the
   all-registry 7/24 failure is competition or carrier recall.
3. Only then decide whether NTSB is worth a second transfer fixture, or whether
   another retained domain has a cleaner path to a second predicate pack.

R11 transfer lens isolation:

```text
artifact root: tmp\ntsb_transfer_surface_001_lens_r1_n3_local_qwen
local model: qwen/qwen3.6-35b-a3b via LM Studio
settings: temperature=0, top_p=1.0, num_ctx=65536, seed=12345
wallclock: 350.8 seconds for 15 local compiles
```

Strict support by lens:

```text
wrapper:     2 / 3
asset_party: 1 / 3
casualty:    0 / 3
conditions:  3 / 5
findings:    0 / 2
timeline:    4 / 10 under stricter closure-stage oracle
```

Interpretation:

- The all-registry 7/24 transfer failure is not mainly all-registry
  competition. Several lanes fail even when isolated.
- Wrapper is close but report status is stable as `factual` while the oracle
  expected `final`. This needs source/oracle adjudication, not code.
- Asset/party reliably finds the operator but does not stably emit the two
  involved vehicle rows under the current carrier contract.
- Casualty is a hard compile-recall failure: all three runs emitted zero
  admitted injury-count rows, with skipped casualty operations.
- Conditions has stable weather, hazmat material, and UN number rows; roadway
  and speed-limit values drift.
- Findings appear in one run only; compact probable-cause/contributing-factor
  finding recall is unstable.

R12 governance alignment:

- Combined audit over the 15 isolated lens artifacts found 6 atom-shape
  blockers, all numeric-leading atoms:
  `17_year_old_driver`, `24_year_old_driver`, and `55_mph`.
- These were registered carrier rows, so the external atom audit was stricter
  than the compiler's in-path `_apply_atom_shape_integrity` reducer.
- The compiler gate now drops numeric-leading registered-carrier atoms unless
  the value is a valid numeric/date/timestamp sentinel already exempted by
  atom-shape policy.
- Reducer-aware summaries now drop the invalid rows; future fresh compiles
  will drop them in-path.

Current NTSB transfer verdict:

- Governance direction is correct, and local LM Studio is fast enough for
  lens-level iteration.
- NTSB is not ready as a second promoted predicate pack. The pressure points are
  real carrier recall and atom convergence, not just provider throughput or
  all-registry competition.
- The highest-leverage next NTSB blocker would be casualty, because it is a
  clean 0/3 isolated compile-recall failure with a simple table-shaped source.
  If casualty cannot be made stable without source-prose parsing or fixture
  vocabulary, NTSB should pause in favor of another retained domain.

R13 casualty-lens repair:

Initial casualty diagnostics showed the compiler was seeing the casualty table
but using the wrong contract shape:

```text
old isolated casualty: 0 / 3
run shapes: ntsb_injury_count/3 or /4, rejected outside allowed palette
example packed value: bystander, 5_8_3
```

Intervention:

- tightened `ntsb_injury_count/6` contract and NTSB registry notes to require
  the full six-slot shape:
  `occurrence_id, subject_scope, fatal_count, serious_count, minor_count,
  source_or_scope`;
- added a fixture-level forbidden row for duplicate
  `subject_scope=not_stated` when the source already names the scope;
- added a typed-only `ntsb_injury_count_scope_specificity` reducer that drops a
  `not_stated` injury-count row when a same occurrence and same
  fatal/serious/minor count triple already has a specific scope. This reads only
  emitted typed facts and creates no replacements.

Posthoc R2 scorer result over the three already-run casualty artifacts:

```text
artifact root: tmp\ntsb_transfer_surface_001_casualty_r2_n3_local_qwen
supported expected facts: 3 / 3
supported forbidden facts: 0 / 3
unexpected same-signature facts: 0
specificity drops: 1 per run
```

Fresh in-path R3 result:

```text
artifact root: tmp\ntsb_transfer_surface_001_casualty_r3_n3_local_qwen
local model: qwen/qwen3.6-35b-a3b via LM Studio
settings: temperature=0, top_p=1.0, num_ctx=65536, seed=12345
support threshold: >=2
supported expected facts: 3 / 3
supported forbidden facts: 0 / 3
unexpected same-signature facts: 0
atom-shape/signature/lens-scope blockers: 0
```

Per-run caution:

- run1 emitted the three expected scoped injury rows;
- run2 emitted `unknown` placeholders in count slots and was correctly rejected
  by the mapper, yielding 0 trusted casualty facts;
- run3 emitted the expected scoped rows after in-path governance.

R4 warning-clean registry note:

- The domain schema validator flagged the earlier registry note as
  `notes_look_like_fact_payload` because the note carried too much concrete
  slot/payload guidance.
- Shortening the registry note removed the schema warning but weakened the
  casualty lens: fresh R4 fell to 1/3 support and therefore failed the
  support>=2 gate.
- This is an important negative result: clean registry vocabulary alone is not
  enough; registry-direct compiles need the central carrier contract lines in
  prompt context.

R5 registry-direct carrier-contract context:

- Added central `carrier_contract_prompt_lines()` to source compile context
  when a profile registry is active. This keeps dataset registry notes short
  and warning-free while giving the lens the binding carrier contract.

```text
artifact root: tmp\ntsb_transfer_surface_001_casualty_r5_n3_local_qwen
local model: qwen/qwen3.6-35b-a3b via LM Studio
settings: temperature=0, top_p=1.0, num_ctx=65536, seed=12345
support threshold: >=2
supported expected facts: 3 / 3
supported forbidden facts: 0 / 3
unexpected same-signature facts: 0
atom-shape/signature/lens-scope blockers: 0
schema validator warnings: 0
```

R5 per-run caution:

- run1 and run3 emitted the expected scoped injury rows;
- run2 zero-yielded after placeholder counts were correctly rejected;
- therefore the casualty lane is support>=2 clean, not every-run stable.

Verdict:

- Casualty is no longer the clean 0/3 blocker; it is now a support>=2 clean
  candidate.
- Do not overstate it as 3/3 stable. The remaining issue is compile recall
  variance in count-slot population, not a missing carrier or a source-prose
  query route.
- The next NTSB pressure should move to another low lens (`asset_party` or
  `findings`) or run a small combined transfer recheck only after at least one
  more lens closes under the same gates.

R14 asset/party negative:

The registry-active central carrier-contract context was then tested on the
asset/party lens, followed by a small contract tightening around NTSB vehicles:
if a source identifies an involved accident/passing vehicle but does not state a
registration or unit identifier, emit the row with `identifier_value=not_stated`;
do not let a struck-object row crowd out accident/passing vehicle rows.

```text
artifact roots:
  tmp\ntsb_transfer_surface_001_asset_party_r2_n3_local_qwen
  tmp\ntsb_transfer_surface_001_asset_party_r3_n3_local_qwen
support threshold: >=2
expected signatures: ntsb_vehicle/6, ntsb_party/5
R3 supported expected facts: 1 / 3
R3 supported forbidden facts: 0 / 3
R3 unexpected same-signature facts: 5
atom-shape/signature/lens-scope blockers: 0
```

What held:

- operator party row for Prairieland Transport was stable 3/3;
- governance remained clean.

What did not move:

- expected accident-vehicle and passing-vehicle rows stayed 0/3;
- occasional struck-object utility-trailer rows appeared instead, but only
  one-run support and not enough to explain the missing expected rows.

Verdict:

- This is not a prompt-polish candidate. Asset/party needs a more deliberate
  vehicle-role bundle or source/oracle adjudication around the source's
  "involved vehicles: 1" table row versus narrative passing-vehicle context.
- Do not promote any asset/party transfer claim from this cell.

R15 findings negative:

The findings lens was rerun under registry-active central carrier-contract
context without additional mechanism edits.

```text
artifact root: tmp\ntsb_transfer_surface_001_findings_r2_n3_local_qwen
support threshold: >=2
expected signature: ntsb_finding/5
supported expected facts: 0 / 2
supported forbidden facts: 0 / 2
unexpected same-signature facts: 0
atom-shape/signature/lens-scope blockers: 0
trusted typed facts after governance: 0
```

Interpretation:

- The compiler attempted finding-like rows, but the trusted typed fact set
  stayed empty under governance.
- One run proposed an explicit negative finding; polarity policy correctly
  rejected it because general negative semantics are not yet admitted.
- This is the same substance-layer wall seen elsewhere: compact probable-cause
  and contributing-factor values are not stable just because the source contains
  the final prose.

Verdict:

- Findings remains 0/2 and should not receive row-level polishing until the
  project decides whether a compact finding taxonomy is a real NTSB domain layer
  or an abstain/Tier 2 product surface.

R16 conditions gain:

The conditions lens was rerun under registry-active central carrier-contract
context. R2 stayed at 3/5: weather, hazmat material, and UN number were stable;
roadway form and speed limit were still either omitted or packed together.

One general contract edit was then made:

- NTSB condition contract now says roadway form and speed limit must be separate
  rows: `condition_kind=roadway` for road form and `condition_kind=speed_limit`
  for posted speed.

Fresh R3 result:

```text
artifact root: tmp\ntsb_transfer_surface_001_conditions_r3_n3_local_qwen
support threshold: >=2
expected signature: ntsb_condition/5
supported expected facts: 5 / 5
supported forbidden facts: 0 / 2
unexpected same-signature facts: 8 one-run rows
atom-shape/signature/lens-scope blockers: 0
```

Supported rows:

- weather `dry_clear_nighttime`: 3/3
- roadway `rural_unlit_undivided_highway`: 3/3
- speed limit `mph_55`: 3/3
- hazmat material `anhydrous_ammonia`: 3/3
- hazmat UN number `un1005`: 2/3

Verdict:

- Conditions is now a support>=2 clean transfer lens, with one-run precision
  noise around hazmat classification/equipment state.
- Do not claim every-run stability or precision-complete condition coverage.

R17 wrapper gain:

The wrapper lens was rerun under registry-active central carrier-contract
context.

```text
artifact root: tmp\ntsb_transfer_surface_001_wrapper_r2_n3_local_qwen
support threshold: >=2
expected signatures: ntsb_report/5, ntsb_occurrence/6, ntsb_occurrence_time/5
supported expected facts: 3 / 3
supported forbidden facts: 0 / 3
unexpected same-signature facts: 1 one-run row
atom-shape/signature/lens-scope blockers: 0
```

Supported rows:

- occurrence identity/date/location: 3/3
- occurrence time: 3/3
- report wrapper/status/date: 2/3

Precision note:

- one run still emitted `report_status=factual` instead of `final`;
- the support>=2 result is clean, but status wording remains a source/oracle
  sensitivity to watch on later NTSB transfer fixtures.

R18 timeline/safety-action gain:

R8 after registry-active carrier-contract context improved the stricter
closure-stage timeline oracle from the older 4/10 to 7/10:

```text
artifact root: tmp\ntsb_transfer_surface_001_timeline_r8_n3_local_qwen
support threshold: >=2
expected signatures: ntsb_timeline_event/6, ntsb_occurrence_time/5, ntsb_safety_action/6
supported expected facts: 7 / 10
supported forbidden facts: 0 / 2
unexpected same-signature facts: 5
atom-shape/signature/lens-scope blockers: 0
```

R8 diagnosis:

- the six timeline-event rows were mostly stable;
- remaining misses were safety-action rows and one actor-id variant
  (`org_tfd`) that cannot be safely expanded deterministically without a typed
  source-stated organization mapping;
- the blocker was therefore safety-action carrier recall, not a general
  chronology failure.

One general contract edit was then made:

- when `ntsb_safety_action/6` is available, postcrash reviews, training,
  recommendations, inspections, directives, operational restrictions, and
  roadway improvements should be emitted as first-class safety-action rows, not
  only as generic `ntsb_timeline_event(..., safety_action, ...)` rows;
- actor ids should prefer compact expanded atoms from source-stated full
  organization names over unexplained initials-only atoms.

Fresh R9 result:

```text
artifact root: tmp\ntsb_transfer_surface_001_timeline_r9_n3_local_qwen
local model: qwen/qwen3.6-35b-a3b via LM Studio
settings: temperature=0, top_p=1.0, num_ctx=65536, seed=12345
wallclock: 80.3 seconds for 3 local compiles
support threshold: >=2
supported expected facts: 10 / 10
supported forbidden facts: 0 / 2
unexpected same-signature facts: 6
atom-shape/signature/lens-scope blockers: 0
```

Supported rows:

- occurrence time: 2/3
- distress call: 3/3
- closure ordered: 2/3
- closure completed: 2/3
- mutual aid request: 2/3
- first hazmat entry: 3/3
- road reopen: 3/3
- RuralMed after-action review: 2/3
- Teutopolis Fire Department hazmat training: 2/3
- IDOT roadway improvement: 2/3

Precision/variance notes:

- run2 still emitted no safety-action rows, so this is support>=2 clean, not
  every-run stable;
- unexpected rows include source-stated 10:01 a.m. patch-removal/hazmat-entry
  and operation-completion timeline variants. These are precision/adjudication
  targets, not automatic forbidden rows.

Current NTSB transfer lens-status snapshot:

```text
wrapper:     3 / 3
asset_party: 1 / 3
casualty:    3 / 3
conditions:  5 / 5
findings:    0 / 2
timeline:   10 / 10
```

This snapshot is a per-lens diagnostic assembled from separate focused runs,
not a deployable combined-pack claim. Asset/party and findings still block NTSB
pack promotion, and the next honest move is either a combined fresh transfer
recheck to measure lens interference or to park NTSB as "skeleton plus
chronology/conditions/casualty, abstain on findings/vehicle-role
disambiguation" while selecting the next fixture-bank domain.

R19 broad all-registry recheck:

After the wrapper, casualty, conditions, and timeline contract gains, the
unlike transfer fixture was rerun as a broad registry-direct compile with all
11 NTSB carriers offered together.

```text
artifact root: tmp\ntsb_transfer_surface_001_all_registry_r2_n3_local_qwen
local model: qwen/qwen3.6-35b-a3b via LM Studio
settings: temperature=0, top_p=1.0, num_ctx=65536, seed=12345
wallclock: 151.1 seconds for 3 local compiles
support threshold: >=2
supported expected facts: 19 / 25
supported forbidden facts: 0 / 15
unexpected same-signature facts: 25
atom-shape/signature blockers: 0
```

By predicate:

```text
ntsb_report:          1 / 1
ntsb_occurrence:      1 / 1
ntsb_occurrence_time: 1 / 1
ntsb_party:           1 / 1
ntsb_condition:       5 / 5
ntsb_timeline_event:  6 / 6
ntsb_finding:         2 / 2
ntsb_vehicle:         1 / 2
ntsb_safety_action:   1 / 3
ntsb_injury_count:    0 / 3
```

Interpretation:

- The broad pack improved substantially over the earlier all-registry 7/24
  baseline, with governance still clean.
- But it lost casualty rows that the casualty lens can produce and retained
  instability in safety-action/vehicle attachment.
- This supports lens-scoped compile bundles as the more plausible pack
  architecture for this domain.

R20 asset/party repair and lens-union diagnostic:

The asset/party lens still blocked the lens-union result. One general
vehicle-contract refinement was added:

- preserve whole highway combination vehicles as `vehicle_type=combination_vehicle`
  before optional component rows;
- passing/oncoming vehicles named in the crash sequence are first-class rows
  even if a summary table counts only the accident/involved vehicle;
- parked struck objects and component equipment are secondary and must not
  substitute for moving accident/passing/oncoming vehicle rows.

Fresh asset/party R4:

```text
artifact root: tmp\ntsb_transfer_surface_001_asset_party_r4_n3_local_qwen
wallclock: 70.6 seconds for 3 local compiles
support threshold: >=2
supported expected facts: 3 / 3
supported forbidden facts: 0 / 3
unexpected same-signature facts: 7
atom-shape/signature/lens-scope blockers: 0
```

Then a deterministic lens union was built by pairing each focused lens run by
cycle (`run1` with `run1`, `run2` with `run2`, `run3` with `run3`) across:
wrapper R2, asset/party R4, casualty R5, conditions R3, findings R2, and
timeline R9. The union reads no source prose and infers no new rows.

```text
artifact root: tmp\ntsb_transfer_surface_001_lens_union_r2_n3_local_qwen
support threshold: >=2
supported expected facts: 23 / 25
supported forbidden facts: 0 / 15
unexpected same-signature facts: 23
atom-shape/signature blockers: 0
```

By predicate:

```text
ntsb_report:          1 / 1
ntsb_occurrence:      1 / 1
ntsb_occurrence_time: 1 / 1
ntsb_party:           1 / 1
ntsb_vehicle:         2 / 2
ntsb_injury_count:    3 / 3
ntsb_condition:       5 / 5
ntsb_timeline_event:  6 / 6
ntsb_safety_action:   3 / 3
ntsb_finding:         0 / 2
```

Verdict:

- The NTSB method has a strong support>=2 skeleton/chronology/conditions/
  casualty/vehicle/safety-action transfer result under lens-scoped compilation.
- This is still not an NTSB product claim: it is one unlike transfer fixture
  and a deterministic union of focused lens compiles, not a broad single-pass
  pack.
- The remaining NTSB transfer blocker is the findings/probable-cause substance
  lane. Given the broader project reset, that lane should probably abstain or
  become Tier 2 unless a compact, reproducible finding taxonomy can transfer
  on fresh documents without prose-shaped slots.

R21 scripted lens-bundle harness:

The manual lens-union diagnostic in R20 was converted into a reusable harness:
`scripts/run_domain_lens_bundle.py`. The harness runs each registry lens as a
separate compile, unions same-cycle mapper-admitted typed facts, then scores and
audits the union. It does not read source prose, oracle answers, or fixture
labels to create facts.

Fresh same-condition local-Qwen harness run:

```text
artifact root: tmp\domain_lens_bundle\ntsb-transfer-surface-001-bundle-harness-r1
lenses: wrapper, asset_party, casualty, timeline, conditions, findings
repeat: 3
local model: qwen/qwen3.6-35b-a3b via LM Studio
settings: temperature=0, top_p=1.0, num_ctx=65536, seed=12345
initial supported expected facts: 18 / 25
initial supported forbidden facts: 0 / 15
registered fact/signature rate: 100%
atom-shape/signature/lens-scope blockers: 0
```

One typed-value reducer was then added for NTSB condition atoms. It canonicalizes
typed condition values such as `weather_dry_clear_night` to
`dry_clear_nighttime`, `roadway_rural_unlit_undivided` to
`rural_unlit_undivided_highway`, and `speed_limit_55_mph` to `mph_55`. This
reducer reads only typed carrier arguments already emitted by the compiler; it
does not parse source text or query text.

Rescored result on the same harness artifacts:

```text
report: tmp\domain_lens_bundle\ntsb-transfer-surface-001-bundle-harness-r1\reports\typed_micro_series_summary_r2_reducer.json
supported expected facts: 19 / 25
supported forbidden facts: 0 / 15
unexpected same-signature facts: 19
atom-shape/signature/lens-scope blockers: 0
```

By predicate after the typed condition reducer:

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

Interpretation:

- R20's 23/25 manual lens-union result was real as a diagnostic but did not
  reproduce under a fresh scripted same-condition bundle. Treat the current
  harnessed NTSB transfer floor as 19/25, not 23/25.
- The harness itself is useful: it makes lens-bundle transfer repeatable and
  keeps the union step inside typed artifacts.
- The repeatability gap is concentrated in casualty recall and one
  safety-action actor attachment. Findings remain a substance lane and should
  abstain or move to a lower tier unless a compact finding taxonomy proves
  transferable on unlike documents.
- Do not run a second NTSB transfer as a claim yet. First decide whether
  casualty/safety stability has a general typed mechanism, or park NTSB as a
  skeleton/chronology/conditions pack with explicit findings abstention.

## R22 SEC Form 8-K Skeleton Candidate

SEC Form 8-K fixtures were selected as the next fixture-bank candidate because
the retained corpus has many official corporate-disclosure documents and a
stable document scaffold. This pass deliberately targets skeleton anatomy only:
cover-page filing identity, registrant identity, cover-page identifiers, item
headings, exhibit table rows, and signature block. It does not attempt event
economics, agreement terms, officer biographies, compensation details, or other
item-body substance.

Reviewed retained examples:

- `datasets/real_world_transfer/20260523_wild_01/sec_8k_material_event_001`
- `datasets/real_world_transfer/fresh_ugly_public_20260524_01/sec_material_event_ugly_001`
- `datasets/real_world_transfer/fresh_ugly_public_20260524_01/sec_material_event_ugly_002`
- `datasets/real_world_transfer/fresh_ugly_public_20260528_01/sec_material_event_ugly_006`

Closed skeleton carriers added:

```text
sec_filing/6
sec_registrant/4
sec_registrant_identifier/5
sec_filing_item/5
sec_exhibit/5
sec_signatory/5
domain_omission/5
```

Lens-scoped offering:

| Lens | Offered signatures |
| --- | --- |
| `wrapper` | `sec_filing/6`, `sec_registrant/4`, `sec_registrant_identifier/5`, `domain_omission/5` |
| `items` | `sec_filing_item/5`, `domain_omission/5` |
| `exhibits` | `sec_exhibit/5`, `domain_omission/5` |
| `signature` | `sec_signatory/5`, `domain_omission/5` |

Typed micro-fixture added:

```text
fixture: datasets/compile_micro_fixtures/sec_form_8k_skeleton_v1
source fixture: datasets/real_world_transfer/20260523_wild_01/sec_8k_material_event_001
expected facts: 13
forbidden facts: 6
```

The first local-Qwen lens-bundle run showed a governance issue before any
claim could be made:

```text
artifact root: tmp\domain_lens_bundle\sec-form-8k-skeleton-r2-local-qwen
local model: qwen/qwen3.6-35b-a3b via LM Studio
settings: temperature=0, top_p=1.0, num_ctx=65536, seed=12345
repeat: 3
pre-source-scope-guard supported expected facts: 10 / 13
pre-source-scope-guard supported forbidden facts: 0 / 6
atom-shape/signature/lens-scope blockers: 0
```

But one supported row depended on a prose-shaped provenance value:

```text
sec_exhibit(..., cover_page_ixbrl, embedded_ixbrl,
  cover_page_interactive_data_file_embedded_within_the_inline_xbrl_document).
```

That value belongs in a description slot if admitted at all, not in
`source_or_scope`. A general source-scope payload guard was therefore tightened
for all registered carriers. It drops provenance slots that carry citation-,
identifier-, or semantic-shaped answer payloads, while allowing source
coordinates, local headings/blocks/rows, document ids, and short source-ish
handles. The guard reads only typed carrier arguments; it does not inspect
source prose or query prose and does not infer replacement provenance.

After regenerating the union artifacts from the same lens compiles with the
stricter deterministic guard:

```text
artifact root: tmp\domain_lens_bundle\sec-form-8k-skeleton-r2-local-qwen-source-scope-guard
supported expected facts: 9 / 13
supported forbidden facts: 0 / 6
unexpected same-signature facts: 4
registered fact/signature rate: 100%
atom-shape/signature blockers: 0
```

Supported rows:

```text
sec_filing:                 1 / 1
sec_registrant:             1 / 1
sec_registrant_identifier:  4 / 5
sec_filing_item:            2 / 3
sec_exhibit:                0 / 2
sec_signatory:              1 / 1
```

Interpretation:

- The SEC skeleton pack is promising for wrapper/registrant/identifier/date/
  signatory anatomy, but it is not promotable.
- The stricter source-scope guard intentionally lowered support from 10/13 to
  9/13 by removing a description-in-provenance row.
- Remaining blockers are compact and useful: exchange-name granularity
  (`exchange_nasdaq` versus full legal exchange name), Item 9.01 role stability,
  and exhibit-table row delivery without description payload.
- Do not add event-substance carriers yet. The next SEC move is to make the
  skeleton clean, then test one unlike Form 8-K before deciding whether SEC is
  a better third pack candidate than OSHA or court orders.

R3 contract tightening:

The next intervention stayed inside the same six SEC skeleton carriers:

- `sec_registrant_identifier/5` now asks for full source-stated exchange venue
  atoms such as `exchange_nasdaq_stock_market_llc`, not only
  `exchange_nasdaq`;
- `sec_filing_item/5` now states that Item 9.01 Financial Statements and
  Exhibits is structural exhibit anatomy, so `item_role=exhibit`;
- `sec_exhibit/5` now requires one row for each exhibit table row, including
  agreement exhibits and cover-page Inline XBRL rows, with source handles such
  as `exhibit_table_row_10_1` rather than description payload in
  `source_or_scope`.

Fresh local-Qwen R3:

```text
artifact root: tmp\domain_lens_bundle\sec-form-8k-skeleton-r3-local-qwen-contract-tightening
repeat: 3
supported expected facts: 12 / 13
supported forbidden facts: 0 / 6
unexpected same-signature facts: 3
atom-shape/signature/lens-scope blockers: 0
source-scope payload drops: 0
```

The remaining miss was typed exhibit-number normalization: one run emitted raw
`10.1` and `104` values in the `sec_exhibit/5` `exhibit_number` slot. A
general typed reducer was added:

```text
10.1 -> exhibit_10_1
104  -> exhibit_104
```

This reducer reads only the `sec_exhibit/5` typed exhibit-number argument. It
does not read source prose or query prose, does not infer exhibit role or kind,
and creates no new facts.

Reducer-aware R3 result:

```text
artifact root: tmp\domain_lens_bundle\sec-form-8k-skeleton-r3-local-qwen-contract-tightening-exhibit-number-reducer
supported expected facts: 13 / 13
supported forbidden facts: 0 / 6
unexpected same-signature facts: 1
registered fact/signature rate: 100%
atom-shape/signature blockers: 0
```

By predicate:

```text
sec_filing:                 1 / 1
sec_registrant:             1 / 1
sec_registrant_identifier:  5 / 5
sec_filing_item:            3 / 3
sec_exhibit:                2 / 2
sec_signatory:              1 / 1
```

Current SEC verdict:

- The skeleton micro is now clean under N>=3/support>=2 with no forbidden rows
  and clean atom/signature gates.
- This is not an SEC pack claim and not a product result. It is one in-family
  micro built from a retained Form 8-K fixture.
- The next honest SEC move is one unlike retained Form 8-K skeleton transfer
  fixture using the same six skeleton carriers. Do not add event-specific
  disclosure substance until skeleton transfer holds.

## R23 SEC Form 8-K Skeleton Transfer

An unlike retained Form 8-K skeleton transfer fixture was added from:

```text
fixture: datasets/compile_micro_fixtures/sec_form_8k_skeleton_transfer_001
source fixture: datasets/real_world_transfer/fresh_ugly_public_20260524_02/sec_material_event_ugly_003
expected facts: 13
forbidden facts: 8
```

The source is a ServiceNow Form 8-K excerpt. The oracle stays skeleton-only:
filing wrapper, registrant, cover-page identifiers, item headings, exhibit
table rows, and signature block. It excludes event-body substance such as
employment-agreement economics, compensation details, policy terms, and officer
biography.

Initial transfer run:

```text
artifact root: tmp\domain_lens_bundle\sec-form-8k-skeleton-transfer-001-r1-local-qwen
local model: qwen/qwen3.6-35b-a3b via LM Studio
settings: temperature=0, top_p=1.0, num_ctx=65536, seed=12345
repeat: 3
supported expected facts: 5 / 13
supported forbidden facts: 0 / 7
unexpected same-signature facts: 24
atom-shape/signature/lens-scope blockers: 0
```

The low score was useful rather than discouraging. The cage held: no new
predicates, no lens-scope failures, and no prose-shaped atoms. The failures
were inside allowed slots:

- `filing_date` was expected as the report date, but the excerpt did not state
  a separate filing date; the source-faithful expected value is `not_stated`.
- `registrant_id` and `jurisdiction` drifted through role prefixes such as
  `registrant_` and `jurisdiction_`.
- exhibit 10.2, a severance policy, was over-classified as `agreement`.
- the compiler inferred unstated CIK rows from issuer knowledge, which the
  original forbidden oracle did not catch.
- telephone values were later emitted as `phone__408__501_8550` instead of the
  compact `phone_408_501_8550` atom.

Interventions kept to typed, source-faithful governance:

- Corrected the transfer oracle's `sec_filing/6` filing-date slot to
  `not_stated`.
- Added a role-scoped SEC typed-slot prefix reducer for selected
  `registrant_id` and `jurisdiction` slots. It strips structural prefixes such
  as `registrant_` and `jurisdiction_` from typed carrier arguments only; it
  does not map one company name to another.
- Tightened `sec_exhibit/5` so policy/plan exhibits use `other_exhibit` unless
  a narrower closed kind exists.
- Added a generic forbidden CIK pattern for the transfer fixture and tightened
  `sec_registrant_identifier/5`: CIK may be emitted only when a CIK label and
  value are explicitly stated in source.
- Added a typed SEC identifier-value reducer for telephone atoms, normalizing
  already-emitted telephone values to `phone_NNN_NNN_NNNN`. It creates no new
  identifier facts and reads no source prose or query prose.

Fresh R3 after the CIK containment guidance:

```text
artifact root: tmp\domain_lens_bundle\sec-form-8k-skeleton-transfer-001-r3-local-qwen-cik-containment
supported expected facts: 12 / 13
supported forbidden facts: 0 / 8
unexpected same-signature facts: 2
atom-shape/signature/lens-scope blockers: 0
```

The remaining miss was only telephone atom formatting. Replaying those same R3
compile artifacts through the typed phone-value reducer produced:

```text
artifact root: tmp\domain_lens_bundle\sec8k-transfer-r3-phone-reducer
supported expected facts: 13 / 13
supported forbidden facts: 0 / 8
unexpected same-signature facts: 0
atom-shape/signature blockers: 0
```

Current SEC transfer verdict:

- The SEC skeleton pack transferred to one unlike retained Form 8-K at
  N>=3/support>=2 after typed-only slot/value normalization.
- This is still not an SEC product claim. It is one unlike transfer fixture.
- The highest-value finding is governance, not 13/13: the run surfaced and
  blocked an unstated-CIK model-prior leak before the score was trusted.
- Next SEC move: run one or two more unlike retained Form 8-K skeleton
  transfers before adding event-substance carriers.

## R24 SEC Form 8-K Second Skeleton Transfer

A second unlike retained Form 8-K skeleton transfer fixture was added from:

```text
fixture: datasets/compile_micro_fixtures/sec_form_8k_skeleton_transfer_002
source fixture: datasets/real_world_transfer/fresh_ugly_public_20260529_01/sec_material_event_ugly_007
expected facts: 12
forbidden facts: 6
```

The source is a Driven Brands Form 8-K excerpt with Item 4.02 Non-Reliance and
Item 9.01 exhibit anatomy. The oracle stays skeleton-only: filing wrapper,
registrant, cover-page identifiers, item headings, one exhibit row, and the
signature block. It excludes restatement substance and audit-committee
conclusions.

Initial local-Qwen transfer run:

```text
artifact root: tmp\domain_lens_bundle\sec-form-8k-skeleton-transfer-002-r1-local-qwen
settings: temperature=0, top_p=1.0, num_ctx=65536, seed=12345
repeat: 3
supported expected facts: 9 / 12
supported forbidden facts: 0 / 6
unexpected same-signature facts: 3
atom-shape/signature/lens-scope blockers: 0
```

The useful residue was not missing predicates. The items lens proposed
`sec_filing_item/5` rows, but the reducer chain correctly dropped them:

- run 1 and run 2 used the registrant/company as `source_or_scope`, which is a
  provenance payload leak;
- run 3 used a numeric-leading commission-file value as `filing_id`, which is
  not a valid compact atom.

Interventions:

- added a typed SEC filing-id atom reducer for registered SEC skeleton carriers
  only; it prefixes numeric-leading `filing_id` values such as `001_39898` to
  `filing_001_39898` and reads no source or query prose;
- tightened `sec_filing_item/5` so `source_or_scope` must be an item-heading
  source handle, not the registrant/company name or item body text;
- kept the source-scope payload guard intact rather than normalizing bad
  provenance into acceptable provenance.

R2 after the item-boundary patch:

```text
artifact root: tmp\domain_lens_bundle\sec-form-8k-skeleton-transfer-002-r2-local-qwen-item-boundary
supported expected facts: 11 / 12
supported forbidden facts: 0 / 6
unexpected same-signature facts: 3
atom-shape/signature/lens-scope blockers: 0
```

The two item-heading rows moved to 3/3. The remaining unsupported row was
`sec_filing/6`: every run emitted the wrapper row, but the date slots drifted
between cover-page report date, Item 4.02 body date, and signature/report date
as `filing_date`.

The next intervention stayed at the carrier-contract boundary:

- `sec_filing/6` now states that wrapper `event_date` is the cover-page Date of
  Report / Date of Earliest Event Reported when stated;
- item-body event dates must not be substituted into the wrapper row;
- `filing_date` requires an explicitly labeled filed/submitted/accession date;
  report date and signature date are not filing date, and the value should be
  `not_stated` when no separate filing date is stated.

A first R3 run with a long label failed during deterministic union because the
generated union filename exceeded the practical Windows path budget. The
compiles themselves had completed; the harness now caps union filename slugs so
measurement labels do not affect write reliability.

Fresh R3 with the shorter label:

```text
artifact root: tmp\domain_lens_bundle\sec8k-t002-r3-date
supported expected facts: 12 / 12
supported forbidden facts: 0 / 6
unexpected same-signature facts: 1
registered fact/signature rate: 100%
atom-shape/signature/lens-scope blockers: 0
```

Research integrity gate:

```text
artifact root: tmp\research_integrity_gate_sec8k_t002_r3
sign-clean audit: pass
atom-shape / registered-signature / lens-scope audit: pass
carrier value-domain audit: pass
domain omission accountability audit: pass
focused governance tests: 524 passed
```

The one unexpected row is a single-run signatory-name normalization variant
(`scott_omelia` vs. the expected `scott_o_melia`). It is not being repaired
because it does not block N>=3/support>=2 and a person-name reducer here would
risk becoming a silent entity-rewrite path.

Current SEC methodology verdict:

- The closed SEC Form 8-K skeleton pack has now transferred hard-clean to two
  unlike retained Form 8-K fixtures under local Qwen N>=3/support>=2.
- The interventions were typed-slot/value normalization and carrier-contract
  boundary tightening, not source-prose matching or query routing.
- This is evidence for the technical research claim that a closed predicate
  domain can stabilize same-family messy official-document compilation under
  governance. It remains a method result, not an SEC product claim.

## R25 SEC Form 8-K/A Third Skeleton Transfer

A third unlike retained Form 8-K skeleton transfer fixture was added from:

```text
fixture: datasets/compile_micro_fixtures/sec_form_8k_skeleton_transfer_003
source fixture: datasets/real_world_transfer/fresh_ugly_public_20260524_02/sec_material_event_ugly_004
expected facts: 12
forbidden facts: 10
```

This source is a Blackstone Form 8-K/A amendment. It pressures a skeleton edge
not covered by the first two transfer fixtures: amended 8-K form type, Item
2.02 Results of Operations and Financial Condition, furnished press-release
exhibit, NYSE listing, cover-page Inline XBRL exhibit, and signature block.

Before running, the closed SEC skeleton palette was expanded in a bounded way:

- `sec_filing/6` now admits `form_8_k_a` in addition to `form_8_k`;
- `sec_filing_item/5` now admits
  `results_of_operations_financial_condition` for Item 2.02.

Those additions are recurring SEC Form 8-K anatomy, not fixture-specific nouns.

Fresh R1 result:

```text
artifact root: tmp\domain_lens_bundle\sec8k-t003-r1
local model: qwen/qwen3.6-35b-a3b via LM Studio
settings: temperature=0, top_p=1.0, num_ctx=65536, seed=12345
repeat: 3
supported expected facts: 12 / 12
supported forbidden facts: 0 / 10
unexpected same-signature facts: 1
registered fact/signature rate: 100%
atom-shape/signature/lens-scope blockers: 0
```

Research integrity gate:

```text
artifact root: tmp\research_integrity_gate_sec8k_t003_r1
sign-clean audit: pass
atom-shape / registered-signature / lens-scope audit: pass
carrier value-domain audit: pass
domain omission accountability audit: pass
focused governance tests: 524 passed
```

The one unexpected row assigned Item 2.02 `substantive` instead of `furnished`
in one run. It did not meet support>=2 and was not added retroactively as a
forbidden oracle row. Treat it as precision residue for the next fresh run, not
as a score adjustment.

Updated SEC methodology verdict:

- The closed SEC Form 8-K skeleton pack has now transferred hard-clean to three
  unlike retained Form 8-K/8-K/A fixtures under local Qwen N>=3/support>=2.
- Two of the three needed typed-slot/value normalization or carrier-boundary
  tightening before claim-bearing transfer; the third passed on first run after
  bounded recurring-palette expansion.
- This strengthens the method claim that a closed predicate domain can
  stabilize same-family official-document skeleton compilation under strict
  governance.
- It still does not prove event-substance extraction, SEC product viability, or
  arbitrary-domain generalization.

## R26 FDA Transfer 002 Boundary Recenter

After the research-priority reset, the FDA `transfer_002` lane was rerun as a
fresh current-pack, lens-scoped bundle rather than as an archived replay:

```text
artifact root:
  tmp/domain_lens_bundle/fda-t002-current-pack-fresh-local-20260603-r5-lens-plan-ops-chronology-id-canon
model/runtime:
  local LM Studio qwen/qwen3.6-35b-a3b, temperature=0, top_p=1.0, num_ctx=65536
repeat:
  N=3, support>=2
  result:
    supported expected facts: 20 / 27
    supported forbidden facts: 0 / 7
    atom-shape blockers: 0
    registered-signature / lens-scope blockers: 0
    unexpected typed rows: 63 at run time; 55 on deterministic replay after
      FDA reference-id subject convergence
```

The run included three governance/harness improvements:

- active-lens accountability, so offered signatures missing from a lens become
  visible instead of silently zero-yielding;
- lens-scoped compile plans, so each lens receives the predicate set it is
  allowed to emit;
- typed FDA warning-letter subject convergence for date-shaped and
  reference-number-shaped wrapper aliases.

The important research decision is to stop treating this fixture as a row-lift
target. Its current value is boundary evidence:

- wrapper role semantics remain unresolved when the source addressee is a named
  executive but the governed recipient entity is the regulated firm;
- `cfr_21_211_42_c_10_v` remains intentionally context-dependent and is not
  mapped by deterministic citation-category projection;
- response/detail value flesh remains softer than the skeleton, citation,
  chronology, and conclusion layers.

Verdict: `transfer_002` is a clean boundary cell, not a failed integrity cell
and not a grind target. The next research move is to summarize FDA per-layer
evidence or test another unlike FDA letter, not to keep lifting this row set.

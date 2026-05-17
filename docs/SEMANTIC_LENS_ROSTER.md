# Semantic Lens Roster

This document captures the current thinking behind Prethinker as a semantic
instrument. It is not a prompt grab bag. It is the start of a roster of the
meaning surfaces the harness should measure, hone, and compare as fixtures get
harder and scores climb.

Current shorthand:

```text
compiled KB = durable state
row = measured encounter with that state
selector = chooses the best encounter surface
guard = prevents a tempting wrong surface
verdict = records what happened
```

Truth lives in the compiled KB. Rows are the unit of measurement and replay.

## Artifact-First Orchestration

Prethinker should prefer artifact-first orchestration:

```text
compile once -> persist source/KB/IR/run artifacts -> run many cheap semantic parallax passes against frozen artifacts
```

The point is to stop treating every question as a fresh act of model
improvisation. A source compile should freeze an inspectable substrate: source
surface, admitted KB, Semantic IR, mapper diagnostics, compile health, and run
metadata. Later passes can then test query variants, selector policies, answer
restraint, failure classification, and repair lenses against the same frozen
world.

This turns the GPU from one big thinker into a small research factory. Python
holds the experiment steady, records what changed, and makes each pass
comparable. The model still performs semantic work; the harness keeps that work
bounded, replayable, and measurable.

## Lens Facets

Lens names should describe the guardrail or semantic reason for being, not the
fixture that first exposed the issue. A good lens answers:

- What meaning surface does this acquire, protect, or compare?
- Which failure surface does it target?
- Which fixtures expose it?
- Does it transfer to unlike fixtures?
- Does it preserve exact rows and authority boundaries?

Current facet roster:

| Facet | What It Measures | Example Pressure |
| --- | --- | --- |
| Source surface | Whether the KB admitted the facts, states, rules, actors, quantities, dates, corrections, and exceptions needed for later reasoning. | Compile gaps dominate current cold rollups. |
| Operational record/status | Permit lifecycles, intake logs, conservation ledgers, application dockets, corrections, reversals, unresolved items, status before/after, and row-level commit readiness. | Ashgrove, Greywell, Heronvale, Veridia. |
| Rule composition | Thresholds, precedence, activation, exception, vote, eligibility, override, and expiration behavior. | Glass Tide, Avalon, Sable, Oxalis. |
| Temporal/status | Status-at-date, interval overlap, deadline arithmetic, business/calendar day distinctions, supersession, and effective/expired boundaries. | Iron Harbor, Oxalis, Dulse, Ashgrove. |
| Authority | Which document, actor, correction, board, rule, vote, or finding controls when accounts conflict. | Northbridge, Greywell, Kestrel, CE. |
| Evidence provenance | Who prepared, presented, dated, admitted, relied on, commissioned, corrected, or physically located a source document, exhibit, survey, receipt, photograph, ledger, or intake item. | Nested Puppet Court, Clockmakers Three Ledgers, Museum/audit lanes. |
| Archival row ledger | Whether exact printed source labels, exhibit IDs, catalog IDs, docket IDs, system names, roster rows, table rows, and source-section labels survive as addressable facts. | Claude 8 dense operational-record batch: Hospital, Maritime, School, Estate. |
| Epistemic uncertainty | Whether the system distinguishes unknown, unstated, pending, disputed, retracted, superseded, unsupported, provisional, inferred, and resolved-negative states. | CE, Veridia Intake, stenographer/turnstream work. |
| Entity and role | Aliases, identity, titles, role changes, custody, ownership, membership, family, organization, and responsibility relationships. | Larkspur, Calder, Three Moles. |
| Query surface | Whether the post-compile query planner asks for the right predicates and joins already present in the KB. | APR, Veridia, Greywell. |
| Selector surface | Whether baseline, direct, protected, activation, evidence, or other modes are chosen under measured risk. | Larkspur, Avalon, Sable, incoming batches. |
| Answer surface | Whether the answer should be concise, hedged, cite uncertainty, refuse, stay quiet, or report insufficient support. | CE, Veridia, answer-surface gaps. |
| Struggle detection | Whether repeated passes have stopped adding unique semantic surface and should stop or continue only with a named expected contribution. | `semantic_progress_assessment_v1`. |

## Evidence Provenance And Registry Scaffolds

The 2026-05-07 cold-injected story-world batch added a new pegboard lesson:
some missing facts are not hidden in deeper narrative reasoning. They are
provenance roles for source artifacts and intake objects.

Two narrow registry-scaffolded candidate modes now sit on the pegboard as
row-gated research lenses:

- `hearing_evidence_provenance_registry_v1` supplies vocabulary for who
  presented, dated, prepared, commissioned, admitted, or relied on evidence
  items such as reports, surveys, photographs, receipts, and exhibits. On
  `nested_puppet_court`, it recovered the photograph years and the authority
  who commissioned the Voss survey, but scored poorly as a global compile. It
  is therefore a surgical evidence-provenance lane, not a replacement lens.
- `ledger_object_provenance_registry_v1` supplies vocabulary for where ledgers
  were found, who brought workshop/intake items in, correction ink/hand status,
  current item status, and client instructions. On
  `clockmakers_three_ledgers`, it recovered the accounts-ledger location and
  Ansonia intake actor, but regressed most broad financial/status rows as a
  standalone compile.

The semantic lesson is durable: source/document provenance and object-intake
provenance are distinct from source content. A ledger entry can say what
happened; a provenance row says where the ledger was found, who brought the
object in, who prepared a report, or who commissioned a survey. These roles
earn explicit predicate scaffolds only when free profile discovery repeatedly
misses them and row-gated replay proves exact-row protection.

The selector guards added by this lesson are named by answer surface:
`survey_commission_provenance_guard`,
`source_claim_witness_statement_guard`,
`permission_request_witness_statement_guard`,
`disputed_strip_object_location_guard`,
`client_ledger_pickup_asset_state_guard`,
`item_received_from_intake_actor_guard`, and
`correction_authorship_expert_attribution_guard`.

## Archival Row Ledger

The Claude 8 dense operational-record batch exposed a separate archival
semantics layer. The source-record V2 scaffold captured what packets said, but
many remaining rows needed the packet's own address system: exact source names,
exhibit labels, catalog IDs, docket IDs, system names, row labels, and table
entries.

`archival_row_ledger_v1` is the current candidate lens for this surface. It
adds predicates such as `record_row/4`, `row_time/2`, `row_actor/2`,
`row_subject/2`, `row_event/2`, `row_value/3`, `row_source_name/2`,
`row_display_label/2`, `document_identifier/3`, `exhibit_label/2`,
`catalog_identifier/2`, `receipt_identifier/2`, `case_number/2`, and
`source_section_label/3`.

The first proof moved the Claude 8 batch from source-record `256 / 23 / 41` to
an archival selected mix of `273 / 20 / 27` over `320` rows (`85.31%`). It helped
Hospital, Maritime, School, and Estate, but regressed University, Arts,
Municipal, and Wildfire as whole-run swaps. That is the lesson: archival row
ledger is a measured candidate lane, not a universal default.

The selector guard added by this lesson is:

`printed source-provenance question needs archival row/source labels rather than generic packet identifiers`

This guard is classified under `rationale_evidence_contrast` because it protects
source/provenance answer surfaces from adjacent but less precise packet IDs.

`archival_identifier_ledger_v1` is the companion lexical pinboard. It
deterministically extracts exact identifier-like spans and line numbers as
context guidance only; it does not admit facts or interpret source meaning. The
first Hospital probe showed both why it matters and why it must stay row-gated:
it rescued one source-record row, but its full QA run regressed because badge
exit rows looked like timekeeping clock-out evidence. The guard added by that
lesson is:

`timekeeping clock-out question needs timekeeping or assignment interval surface rather than badge-exit event rows`

That guard is classified under `operational_record_status`.

## Uncertainty Vocabulary

### Selector Calibration Lessons

- Specialized lenses can be answer-bearing or dazzlingly irrelevant.
  `operational_record_status_v1` is not globally promoted; it is a row-level
  candidate.
- `selector_baseline_readiness_guard` protects direct application/status,
  counterfactual rule, and hold-readiness support when a competing surface is
  broad or relaxed-heavy.
- `selector_question_act_guard` routes request-filing questions to
  request/reinstatement/threshold surface and status-commit questions to
  pending/investigation process surface.
- `selector_surface_specificity_guard` prefers cause/rationale notes,
  decision predicates, and priority predicates over nearby status, condition,
  or event rows when those rows are less answer-bearing.
- `selector_complete_operational_guard` closes the frozen operational batch by
  naming the last distinctions: split rationale, lot-condition/policy surface,
  applicant type plus controlling interpretation, and proof/rule resolution.
  This is selector calibration over persisted artifacts, not evidence that the
  compile surface itself is complete.

### Rationale And Source Notes

- `rationale_contrast_source_note_lens` captures source-stated reasons,
  non-reasons, judgment calls, and explicit contrasts as answer-bearing note
  surface without promoting those notes into policy.
- Its selector companions prefer note rationale for why/contrast questions,
  direct collector predicates for identity questions, pending `test_status` for
  not-yet-tested questions, and threshold/storage policy surfaces for
  failed-viability hypotheticals.
- `current_operational_final_state_guard`,
  `evidentiary_report_surface_guard`, `board_concern_event_action_guard`, and
  `commit_readiness_process_guard` preserve useful rationale/contrast rows
  while protecting final status and commit/hold decisions from incomplete note
  or event surfaces.
- Older-fixture transfer marks the boundary: source-note rationale transfers to
  record/discrepancy/correction surfaces, but it does not solve Larkspur-style
  narrative motive, custody, or object-state coverage without a stronger
  source-surface acquisition contract.

### Object, Custody, And Role Surfaces

- `final_object_state_transition_surface` covers named-device initial/current/
  final condition, state-change event, repair/restoration possibility, and
  stated state-change reason. Its guardrail is that identity/role questions
  must not be overrun by object-state volume; Larkspur q009 remains the active
  counterexample.
- `custody_ownership_chain_surface` is narrower: use it for final holder,
  ownership, or custody rows such as q038, not as a general motive lens.
- `official_role_authority_definition_surface` covers who-is questions where a
  title alone is not enough: role holder, source-stated duties, and authority
  scope.
- New selector guards are named by answer surface:
  `superlative_identity_surface_guard`,
  `official_role_definition_surface_guard`,
  `current_component_state_surface_guard`,
  `custody_transfer_rationale_guard`, and `award_placement_surface_guard`.

### Conflict, Access, And Rule Activation

- Calder adds the longitudinal conflict family:
  `current_state_correction_conflict_surface`,
  `possession_ownership_inheritance_distinction_surface`, and
  `legal_title_default_transfer_surface`.
- Its guards separate stale current-state rows, possession versus ownership,
  trust/default title, contract authority, and non-retroactive guardianship:
  `role_reinstatement_history_guard`, `carry_possession_surface_guard`,
  `possession_ownership_distinction_guard`, `legal_title_transfer_guard`,
  `contract_authority_surface_guard`, and
  `guardianship_resumption_condition_guard`.
- Oxalis adds a regulatory access family that acts after a healthy compile:
  `universal_scope_enumeration_guard`,
  `termination_denial_quantity_threshold_guard`,
  `lot_affected_target_exclusion_guard`, and
  `counterfactual_reclassification_deadline_guard`.
- Rule activation has a parallel promoted-rule family:
  `deferment_rationale_interpretation_guard`,
  `component_rule_condition_surface_guard`,
  `recusal_rationale_rule_surface_guard`,
  `post_recusal_vote_surface_guard`,
  `counterfactual_recusal_outcome_guard`,
  `window_merit_rule_condition_guard`,
  `amendment_recall_authority_surface_guard`,
  `rejection_cause_correction_surface_guard`, and
  `hypothetical_reserve_status_arithmetic_guard`.
- The Sable/Avalon replay reaches both fixtures' frozen upper bounds without
  source prose, answer keys, judge labels, failure labels, gold KBs, or strategy
  files in selector input.

### Negative Replays And Query Helpers

- The latest object/state/custody replay is intentionally negative: a combined
  object-state-custody surface blurred too many Fenmore and Larkspur rows.
  The harness gain was the narrower `deaccession_yet_status_surface_guard`.
- `deaccession_yet_status_surface_guard` routes "has X been deaccessioned
  yet?" questions to compact scheduled/not-formally-completed status evidence,
  keeping deaccession-yet status separate from conservation rationale,
  operational thresholds, final object state, and custody roster evidence.
- Broad temporal surface is not a default compile mode. Ashgrove benefits only
  when the selector uses the right row-level surface, and Copperfall regresses
  globally.
- `adjusted_expiration_current_surface_guard` routes reinstatement/adjusted
  expiration questions to explicit current-expiration predicates.
- `correction_entitlement_effect_surface_guard` routes correction-entitlement
  questions to entitlement-rule plus extension-effect evidence.
- Copperfall keeps the next boundary visible: original answer deadlines,
  resumed answer deadlines, and later reply deadlines must be disambiguated as
  separate deadline families.
- `deadline_calculated_family_companion` is query-side support, not a compile
  lens. It retrieves sibling `deadline_calculated/5` rows whenever a deadline
  calculation is already being queried, exposing typed families such as
  `answer`, `response`, `reply`, `discovery`, and `dispositive`.
- `case_status_interval_support` is query-side support for exact date misses
  over `case_status_at_date/3`. It computes interval rows from admitted
  transition anchors, without adding facts or reading source prose. Temporary
  stay/override status still must be compiled explicitly before the helper can
  return it.
- Oxalis adds three recall/regulatory query companions over frozen artifacts:
  `recall_classification_at_date_support` derives effective classification from
  admitted classification and reclassification anchors, `unit_range_count_support`
  counts admitted lot-range atoms, and `recall_accounted_units_support` derives
  termination-request accounting from admitted total and latest-unaccounted
  rows. The accounting helper is deliberately scoped to termination questions
  after a broader activation perturbed a unit-status row.
- Three Moles adds two story-world companions without promoting a new lens:
  `story_choice_contrast_support` contrasts accepted little/middle/great-family
  items against rejected same-family judgments, and
  `story_remediation_method_support` pairs admitted wound/method events with
  admitted extraction/key outcomes. These helpers are allowed to compose only
  already admitted rows; missing explicit morals, residents, and source phrasing
  still belong to compile-side story acquisition. The companion pass therefore
  adds narrative-only compile guidance for residence rosters, errand/distraction
  setup, contrast choices, comic consequences, and explicit morals rather than
  trying to infer those missing surfaces at query time.
- Lantern adds `roster_state_support`, a query-only helper over admitted
  `group_member`, `group_membership`, `supervises`, and
  `supervision_assignment` rows. It normalizes temporary group membership,
  supervision intervals, group counts, and role hints from admitted group atoms.
  The first targeted replay recovered Lotte's Day 3 recording role, but left
  Station A/B rosters and Day 3 chaperone count as compile gaps. This is the
  desired boundary: helpers compose admitted rows; they do not invent missing
  station facts.
- Lantern then added an aggregate roster/station registry-context candidate.
  Used as intake context rather than a direct profile, it admitted explicit
  `session_attendance_count`, `station_roster`, `station_member`, and
  `station_supervisor` rows. Targeted replay recovered the Day 1 attendance
  count, Station A roster, Station B roster, and Freya Station B watch rows.
  The selector needed an attendance-count guard so explicit count surfaces beat
  broad interval roster volume.
- Lantern's Day 3 chaperone count exposed a day-level aggregate admission
  boundary. A first supervision-count registry failed because `date_or_interval`
  argument roles caused day atoms like `day3` to be rejected as non-intervals.
  The useful version used event/context roles and admitted
  `supervision_scope_count` plus `trip_exception_summary` rows for the three
  Day 3 chaperones and Jostad's non-return. A six-row targeted selector then
  reached `6 exact / 0 miss` after adding a station-supervisor guard, which
  routes named-station supervision questions to explicit `station_supervisor`
  rows rather than standing group-supervision evidence. The supervision-count
  registry is not yet a pegboard lens: its compile was broad and duplicate
  heavy, so the lesson is promoted before the lens.
- The full Lantern replay now reaches `40 exact / 0 miss` under row-gated
  selection. The additional selector repairs are surface boundaries rather than
  new lenses: total attendance must not be routed to a session count; station
  arrival-time questions need event/report timestamps; temporary role questions
  can require roster-state role hints; and trip-completion incident lists need
  summary issue/medical/hazard surfaces instead of a single incident row.
- Transfer safety check: after the Lantern selector repairs, Tournament,
  Greenhouse, and Festival were replayed through their existing guarded
  selectors. All three stayed exactly at their available upper bounds with
  `40/40` selected-best rows. This is enough to keep the guards, but not enough
  to promote the broad supervision-count registry as a durable lens.
- `regulatory_period_deadline_registry_v1` is a candidate source-period/deadline
  scaffold, not a permanent lens. It was created after
  `deadline_cascade_docket` showed that an underlying violation period is a
  different semantic object from a notice issue date or response deadline. Broad
  policy prose did not recover the row; the registry supplied
  `violation_period/4` and lifted Deadline q002/q006 to `2 / 0 / 0`, the
  Deadline first-10 slice to `10 / 0 / 0`, and Deadline full-40 to `35 / 3 / 2`.
  Copperfall q024-q030 then transferred at `7 / 0 / 0`. Both compiles were
  thin/skip-heavy, so the surface is row-gated candidate vocabulary rather than
  a global compile replacement.
- The existing `hearing_evidence_provenance_registry_v1` transferred to
  `harbor_collision_reports` q005/q006, recovering convening authority and CCTV
  as a non-human evidence/source item. Direct first-10 Harbor replay regressed
  ordinary incident rows, so this reinforces the existing evidence-provenance
  lesson: use the lens surgically for source roles, not as a full incident
  compiler.
- `classification_conversion_effect_support` is a query-only conservation
  helper for classification changes. When `conversion_effective_date/3` is
  already queried, it can combine admitted converted-unit rows with admitted
  before/after `unit_count/2` rows and expose `TotalCountEffect = no_change`
  only when the source class decrease and target class increase balance. It
  lifted `census_reconciliation` q009 from partial to exact without writing
  facts or reading source prose. The pegboard lesson is that conversions can be
  semantic conservation problems; missing unit rows or missing before/after
  counts still belong to compile acquisition.
- Census accounting added a broader helper substrate without adding a new
  compile lens. `assessment_revenue_support`, `conversion_assessment_delta_support`,
  `classification_deferral_effect_support`, `vacancy_voting_eligibility_support`,
  and `assessment_transfer_policy_support` expose totals, deltas, deferred
  current-state effects, vacancy/vote effects, and repeated transfer-policy
  boundaries from admitted rows. On `census_reconciliation`, helper work plus
  two scoped source compiles moved the fixture from `29 / 1 / 10` to a
  diagnostic row-gated `40 / 0 / 0`. The pegboard lesson is the split: arithmetic
  and repeated responsibility patterns belong to helpers; bylaw claims,
  cross-reference errors, notice status, and exact open-item language belong to
  narrow source surfaces.
- `planning_application_summary_registry_v1` is a candidate row-gated
  planning/staff-report scaffold. It separates application front matter,
  applicant claims, staff findings, recommendation authority boundaries, draft
  conditions, transit-distance corrections, rejected proposal versions, traffic
  estimates, mitigation authority, environmental mitigations, construction
  limits, existing site conditions, and source-opinion rows. On
  `draft_within_draft`, the tight v3 scaffold compiled cleanly (`82` admitted /
  `1` skipped) and lifted first-10 to `10 / 0 / 0`; the broader v4 scaffold
  preserved first-10 and lifted full-40 to `31 / 2 / 7`. It is not a global
  compiler because the broader version thinned the compile and still missed
  lot-minimum, Saturday-hours, authority-modification, and opinion-rollup rows.
- `board_recusal_conflict_registry_v1` is a candidate row-gated governance
  scaffold for board/committee meeting records. It separates roster/attendance,
  governance rules, agenda items, contract parties, disclosed interests,
  recusal events, temporary authority transfer, and vote surfaces. On
  `rotating_chair_authority`, v1 proved the disclosed-interest lesson by
  recovering Marsh's brother-in-law/Greenline subcontractor conflict, but it
  regressed an absence row until v2 added `meeting_attendance/4`. v2 reaches
  first-10 `10 / 0 / 0` and full-40 `29 / 5 / 6`, so it is useful but not yet a
  global governance compiler.
- `lease_correction_financial_registry_v1` is a candidate row-gated financial
  correction scaffold. It separates lease records, amendment/correction events,
  rent terms, notice requirements, overcharge periods, refund calculations, and
  current refund obligations. On `amended_lease_register`, it recovered the
  `$600` refund calculation row exactly, but direct first-10 regressed Courtyard
  B supersession/authorization questions. Keep it surgical unless paired with a
  broader lease-amendment surface.

Uncertainty is a domain language, not a tone. Future harness work should avoid
collapsing these into a single "not sure" bucket:

| State | Meaning |
| --- | --- |
| `unknown` | The fact is not available in the current record. |
| `unstated` | The source never says it. |
| `pending` | A process has not resolved yet. |
| `disputed` | Competing accounts exist. |
| `retracted` | An earlier claim was withdrawn. |
| `superseded` | A newer rule, correction, or status replaces an older one. |
| `unadopted` | Someone asserted it, but the controlling authority did not accept it. |
| `unsupported` | No evidence in the compiled record supports the claim. |
| `inferred` | Derivable from admitted facts/rules, but not directly stated. |
| `provisional` | Temporarily true until a condition changes. |
| `resolved_negative` | The rule-status uncertainty has been resolved negatively, such as invalid, void, ineligible, denied, or not effective. |
| `temporally_unavailable` | Not yet effective, expired, outside the relevant interval, or before/after the controlling date. |

This matters because "I do not know," "the source does not say," "the source
contains conflicting accounts," "the rule has not activated," and "the answer is
no" are different semantic states. Prethinker should learn to hold them apart.

## Future Roster Shape

As scores approach the higher band, this roster should become more operational:

- each promoted lens gets a stable name and purpose;
- each lens links to the fixtures that expose it;
- each lens records current transfer evidence;
- each lens records failure surfaces helped and regressions caused;
- each uncertainty state gets examples from real fixture rows;
- row-level promotions remain artifact-gated, not vibe-gated.

The goal is an engineered thesaurus of semantic pressure points: not synonyms,
but ways meaning can fracture under question.

Companion inventory:
[Selector Guard Family Rollup](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_FAMILY_ROLLUP.md) is generated
from `scripts/select_qa_mode_without_oracle.py` and tracks whether many
individual selector guards are collapsing into a small number of semantic
families. The current rollup has `5` active guard return sites, `5` unique guard
reasons, `4` families, and `0` unclassified reasons. Detailed retired/scar
ledger output is generated under `tmp` when needed and stays out of the public
docs tree.

[Boundary Probe Research Method](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_PROBE_RESEARCH_METHOD.md)
describes the active method for not-exact rows that remain after guard
compression. Detailed boundary and repair-slice notebooks have moved to the
external archive.

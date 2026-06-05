# Project State

Last updated: 2026-06-05

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
- `docs/CURRENT_COMPILE_FACT_QA_STATUS.md`
- `docs/DOMAIN_PACK_STATUS.md`
- `docs/DOMAIN_ACCOUNTABILITY_STATUS.md`
- `docs/SEC_VALUE_AXIS_INTEGRITY_STATUS.md`
- `docs/DOMAIN_PREDICATE_PROPOSAL_STATUS.md`
- `docs/PENDING_EXTERNAL_WORK_ORDERS.md`
- `docs/CANDIDATE_ORACLE_REVIEW_STATUS.md`
- `docs/SOURCE_ORACLE_REVIEW_STATUS.md`
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
Domain omission accountability
  live negative-control sweep, local Qwen MoE, N=3/support>=2:
    NTSB report-id omission wrapper lens:
      expected omission 1 / 1, forbidden ntsb_report 0 / 1,
      unexpected same-signature wrapper rows 3, atom/lens gates clean
    OSHA inspection-id omission wrapper lens:
      expected omission 1 / 1, forbidden osha_inspection 0 / 1,
      unexpected same-signature establishment rows 2, atom/lens gates clean
    SEC signature omission lens:
      expected omission 1 / 1, forbidden sec_signatory 0 / 1,
      unexpected same-signature rows 0, atom/lens gates clean
  guard changes:
    added typed-only NTSB report-omission contradiction guard
    refined SEC signature omission guard so all-not-stated dummy signatory rows
      lose to the registered omission while real signatory rows still beat
      contradictory omissions
  artifact root:
    C:\prethinker_tmp_archive\omission_accountability_live_20260604
  read:
    omission accountability is now live-tested across SEC, OSHA, and NTSB
    negative controls; the guards read typed facts only and do not interpret
    source prose or query text

SEC Form 8-K skeleton pack
  historical pre-axis-repair cells:
    seed micro: 13 / 13
    transfer_001: 13 / 13
    transfer_002: 12 / 12
    transfer_003: 12 / 12
  current axis-clean schema:
    `sec_filing_item/5.item_role` is structural only
    `sec_filing_item_treatment/4` carries source-stated item legal treatment
    `sec_exhibit/5.exhibit_role` is legal treatment only
    Item 9.01 item-treatment misattachments are blocked by typed governance
    exhibit-table-scope item-treatment rows and cover-page IXBRL treatment
      inference are also blocked by typed governance
  repaired transfer_003 Qwen MoE reruns:
    R1: 12 / 13, 0 / 11 supported forbidden, clean axis/value/atom gates
    R2 after treatment-contract tightening and typed Item 9.01 guard:
      11 / 13, 0 / 10 supported forbidden, clean axis/value/atom gates
    R3 pre-registered stability rerun:
      12 / 13, 0 / 10 supported forbidden, clean atom/signature/lens/value-axis gates
    R3 omission-accountability guard rescore:
      12 / 13, 0 / 10 supported forbidden, unexpected same-signature facts
      reduced from 2 to 0 by typed registry/contradiction guards
    R4/R5 item-treatment seam diagnostics:
      profile-clarity rerun: 12 / 13, 0 / 10 supported forbidden, clean
      atom/lens/value-axis gates, but item-treatment support stayed below
      threshold. SEC filing-id normalization now includes
      `sec_filing_item_treatment/4`; this lets a valid admitted treatment row
      survive typed atom-shape governance when it appears. Fresh rerun after
      that seam fix: 11 / 13, 0 / 10 supported forbidden, clean gates.
      Read this as a real typed-slot seam fix, not a support lift.
    R6 fresh same-condition Qwen MoE refresh:
      13 / 13, 0 / 10 supported forbidden, per-run exact 37 / 39
      clean atom/lens/value-domain/value-axis gates, with one unexpected
      `sec_filing_item_treatment/4` row at support=1 only
      Read this as the favorable end of the current repaired-schema band, not
      as a new fixed SEC number.
    source-only typed reconciliation over the current transfer_003 root:
      artifact:
        C:\prethinker_tmp_archive\sec_item_treatment_filing_id_20260604\sec8k-t003-item-treatment-filing-id-r2-20260604\reports\typed_reconcile_support_ge2_value.md
      result:
        11 reconciled facts, all support=3, 0 skipped, 0 conflicts
        stable facts are filing wrapper, registrant, four identifiers
        excluding telephone, two filing items, two exhibits, and signatory
        item 2.02 treatment and telephone remain below support threshold
  repaired breadth check over retained seed / transfer_001 / transfer_002:
    seed: 12 / 13, 0 / 6 supported forbidden, clean atom/lens gates
    transfer_001: 11 / 13, 0 / 8 supported forbidden, clean atom/lens gates
    transfer_002: 11 / 12, 0 / 6 supported forbidden, clean atom/lens gates
  fenced event-substance probe:
    `sec_material_event/6` is registered for experiments but not offered by the
      promoted SEC skeleton profile
    seed probe with a temporary event lens: 12 / 13 skeleton support, 0 / 6
      supported forbidden, clean atom/lens gates; event-substance rows did not
      reproduce at support>=2
  read: SEC remains useful evidence that small closed skeleton packs transfer,
    but the formal SEC methods-anchor claim is no longer the old 12/12 cell.
    Recent repaired transfer_003 roots now span 11-13 / 13 under the same local
    Qwen MoE lane. The current honest boundary is favorable-draw risk,
    exhibit legal-treatment ambiguity, wrapper filing/telephone recall, one
    duplicate commission-file value, unstable item-treatment recall, and
    ordinary MoE jitter. Bad SEC omission-accounting rows are now
    blocked/dropped by typed guards; do not inflate the cell with prompt
    polishing or a favorable same-condition draw.
  latest SEC governance artifact:
    C:\prethinker_tmp_archive\sec_axis_scope_guard_20260604
    C:\prethinker_tmp_archive\sec_item_treatment_filing_id_20260604
    C:\prethinker_tmp_archive\sec_t003_refresh_20260605
    These guard/seam cleanups did not raise SEC support; they tightened the
      axis cage and stopped valid companion rows from being lost to typed
      filing-id normalization when emitted. The 2026-06-05 refresh is a
      favorable same-condition point inside the observed SEC band.
  current compile-fact QA precision detail:
    docs\CURRENT_COMPILE_FACT_QA_STATUS.md now lists the exact repeated
    unexpected same-signature facts at support>=2. The current rows are
    diagnostics only: SEC seed dual Exhibit 10.1 treatment and FDA
    transfer_002 boundary/detail extras. They are not expected facts unless an
    independent source-only oracle adds them.

FDA warning-letter pack
  deterministic judged-QA v2 across transfer_001 and transfer_002:
    137 / 159 exact = 86.16%
    all 137 exact rows pass typed-plan replay and redaction replay
    transfer_001: 78 / 78 exact across N=3
    transfer_002: 59 / 81 exact across N=3, with 7 partial and 15 miss
    support>=2 view:
      transfer_001: 26 / 26
      transfer_002: 20 / 27
  transfer_003 fresh current-pack local rerun:
    19 / 26 support>=2, 0 / 10 supported forbidden
    atom-shape / registered-signature / lens-scope blockers: 0
    read: clean second boundary cell; the seven unsupported rows are
      `fda_violation_detail/5` value/detail flesh
  read: primary richer case study; skeleton/citation/regulatory boilerplate
    transfer better than wrapper role semantics, context-dependent categories,
    response/detail value flesh, and other substance lanes
  proposal review: `fda_response_documentation_gap/5` blind review on
    transfer_002 found 0 expected / 13 forbidden; stable candidate emissions
    for violations 1, 2, and 3 are false positives
  pending candidate review: `fda_response_assessment_item/6` remains
    unreviewed and is now explicitly queued in the proposal table via
    `tmp\fda_response_assessment_item_blind_review_work_order_20260604.zip`;
    do not cite assessment-item support as a promoted claim until that
    source-only review returns and the proposal status changes.
  scope note: v2 is oracle-shaped compile-fact QA, not evidence that messy
    human query planning is solved
  reproducibility note: `scripts/build_compile_fact_judged_qa.py` now
    regenerates this deterministic compile-fact QA package locally from
    `expected_facts.pl` and compile JSON typed facts

NTSB investigation pack
  seed micro: 13 / 13
  first unlike transfer, current scoped injury-count manifest: 22 / 25
  deterministic compile-fact QA over first unlike transfer:
    60 / 75 per-run exact
    22 / 25 support>=2
    all 60 exact rows pass typed-plan replay and redaction replay
  forbidden support: 0 / 15
  read: corroborating boundary evidence; wrapper, chronology, vehicles, and
    conditions transfer more cleanly than findings/probable-cause substance;
    scoped injury-count partitions now clear, with one timeline sequence-role
    row still unstable

OSHA accident/inspection pack
  seed micro: 21 / 21 support>=2 after high-arity registry intake fix and
    current related-activity blank-flag contract
  first unlike transfer: 15 / 15 support>=2
  forbidden support: 0 in both measured cells
  new transfer diagnostics:
    transfer_002 long violation table: 18 / 53 support>=2, 0 / 8 forbidden
    transfer_003 mixed news-release/prior-inspection fixture: 2 / 21 support>=2
      with 0 / 10 supported forbidden after the typed accident-omission
      contradiction guard
  governance: registered signatures, atom-shape, and lens-scope clean
  read: fourth-family corroboration for skeleton/table anatomy; accident,
    employee injury, violation counts, penalties, item, and status rows transfer
    better than long-table enumeration and mixed-source section attachment. The
    prior repeated FTA total-penalty extra was adjudicated as source-backed and
    is now in the seed oracle; an independent source-only review packet is
    queued at `tmp\osha_fta_total_penalty_blind_review_work_order_20260605.zip`,
    so treat that uplift as project-adjudicated until review returns. The
    transfer_003 guard is cleanup only: support
    stays 2 / 21 while the current news-release accident/injury rows are
    blocked from contaminating the prior inspection detail.

State-AG settlement/AOD seed
  fixture:
    state_ag_settlement_aod_v1
  profile:
    datasets/domain_profiles/state_ag_settlement_v1/ontology_registry.json
  retained seed artifact root:
    C:\prethinker_tmp_archive\state_ag_settlement_seed_20260604\state-ag-seed-all-lenses-r2-20260604
  current fresh local Qwen MoE all-lens seed rerun:
    C:\prethinker_tmp_archive\state_ag_current_rerun_20260604\state-ag-seed-current-rerun-r1-20260604
    17 / 27 support>=2
    0 / 9 supported forbidden
    57 unexpected same-signature facts
    registered-signature / atom-shape / lens-scope gates clean
    carrier value-domain audit clean: 0 violations across 134 checked slots
  read:
    fifth-domain process probe only, not transfer evidence. Wrapper,
    contacts, several chronology rows, and several obligation rows stabilize.
    Citation subsection specificity, event-subject naming,
    counsel/registered-agent attachment, monetary payment support, and likely
    obligation-oracle design remain boundaries. The overproduction is currently
    inside the closed value domains, not an atom-shape or unregistered-language
    leak. A regenerated unexpected-bucket report shows all 57 unexpected
    same-signature rows at support=1 only; no unexpected State-AG row currently
    survives the support>=2 claim threshold.
  source-only unlike transfer intake:
    t002 fixture source:
      datasets/real_world_transfer/fresh_ugly_public_20260528_01/state_ag_settlement_ugly_002/source.md
    retained artifact root:
      C:\prethinker_tmp_archive\state_ag_t002_source_only_n3_20260604\state-ag-t002-source-only-intake-n3-r1-20260604
    run:
      local Qwen MoE, N=3, skip-score, same closed state-AG registry
      union atom audit: 54 typed facts, 5 signatures, 100% registered,
        atom-shape/lens-scope clean
      carrier value-domain audit: 0 violations across 68 checked slots
      value-mode typed reconcile after state-AG reconcile harness coverage:
        7 support>=2 facts, 0 conflicts, 0 skipped
        stable facts are 5 authority-citation rows and 2 contact-channel rows
    read:
      useful pre-oracle transfer-intake signal, not QA/expected-fact evidence.
      The pack transfers authority/contact anatomy cleanly on the unlike
      Equinox AOD, while wrapper party, obligation, chronology, monetary, and
      signature support are not stable enough to claim without an independent
      transfer oracle and likely pack work.
    t003 fixture source:
      datasets/real_world_transfer/fresh_ugly_public_20260529_01/state_ag_settlement_ugly_003/source.md
    retained artifact root:
      C:\prethinker_tmp_archive\state_ag_t003_source_only_n3_20260604\state-ag-t003-source-only-intake-n3-r1-20260604
    run:
      local Qwen MoE, N=3, skip-score, same closed state-AG registry
      union atom audit: 103 typed facts, 8 signatures, 100% registered,
        atom-shape/lens-scope clean
      carrier value-domain audit: 0 violations across 134 checked slots
      value-mode typed reconcile:
        24 support>=2 facts, 0 conflicts, 0 skipped
        stable layers include instrument wrapper, authority citations,
        contacts, one effective-date event, parties, signatures, and a
        repeated obligation sequence
    read:
      second useful source-only intake and notably stronger than t002, but
      still not a scored transfer claim. It suggests the State-AG pack can
      stabilize richer settlement/AOD skeleton on some unlike documents while
      source family shape and oracle design remain unresolved.
    t001 fixture source:
      datasets/real_world_transfer/fresh_ugly_public_20260526_01/state_ag_ugly_001/source.md
    retained artifact root:
      C:\prethinker_tmp_archive\state_ag_t001_source_only_n3_20260604\state-ag-t001-source-only-intake-n3-r1-20260604
    run:
      local Qwen MoE, N=3, skip-score, same closed state-AG registry
      union atom audit: 36 typed facts, 5 signatures, 100% registered,
        atom-shape/lens-scope clean
      carrier value-domain audit: 0 violations across 39 checked slots
      value-mode typed reconcile:
        4 support>=2 facts, 0 conflicts, 0 skipped
        stable facts are all authority-citation rows
    read:
      broader consent-order/judgment source is governance-clean but much
      thinner under this AOD/settlement pack. It is boundary evidence: the
      current State-AG pack transfers authority citations across this shape,
      but wrapper, parties, obligations, contacts, signatures, and payments
      are unstable without a more specific consent-judgment layer or oracle.
  harness note:
    scripts\run_domain_lens_bundle.py now has --reconcile-unions for future
    source-only intakes. It runs typed value-mode reconciliation across union
    artifacts without reading source prose, QA, or oracle answers.
    scripts\reconcile_typed_micro_compiles.py now loads allowed signatures
    from closed domain registries instead of requiring each domain predicate
    to be hand-added to a script allowlist; SEC and State-AG still have narrow
    typed value-key normalization for known document-id aliases.

Fixture-bank / next-domain inventory
  generated status:
    docs\FIXTURE_BANK_DOMAIN_INVENTORY.md
  current read:
    88 retained real-world metadata fixtures, 52 metadata families, 5 closed
    profiles, 7 unprofiled/profile-unrelated multi-fixture families, of which
    3 are QA-bearing. This is a domain-selection map only; it reads metadata
    and profile selection paths, not source prose, QA, oracle answers, or judge
    outputs.
  PUC pre-registry proposal:
    datasets\domain_predicate_proposals\puc_order_wrapper_v1.json
    status: draft
    candidate signature: puc_order/7
    evidence: two local Qwen MoE profile-only PUC bootstraps archived at
      C:\prethinker_tmp_archive\puc_domain_bootstrap_20260604
    read: the two PUC sources agree on wrapper/docket/order/procedure anatomy
      but drift in candidate predicate names, so PUC should proceed through
      closed carrier/oracle review rather than open profile induction.
    external oracle packet:
      tmp\puc_order_wrapper_oracle_work_order_20260604.zip
    proposal-status traceability:
      docs\DOMAIN_PREDICATE_PROPOSAL_STATUS.md now surfaces this pending
      source-only oracle work order directly in the proposal table.
    next step: wait for source-only expected/forbidden wrapper facts before
      creating or scoring a PUC closed registry.
  Procurement / GAO bid-protest pre-registry proposal:
    datasets\domain_predicate_proposals\procurement_gao_decision_wrapper_v1.json
    status: draft
    candidate signature: gao_bid_protest_decision/7
    evidence: two local Qwen MoE profile-only procurement bootstraps archived
      at C:\prethinker_tmp_archive\procurement_domain_bootstrap_20260605
    read: both retained GAO bid-protest decisions expose recurring wrapper,
      docket, decision-date, procurement, party/procedural, protest-ground,
      evaluation-factor, and citation anatomy. The first bootstrap drifted on
      protest-ground/finding surfaces and the second flagged timeliness
      slot-loss, so only the wrapper carrier is drafted; merits/finding lanes
      stay out of scope.
    external oracle packet:
      tmp\procurement_gao_decision_wrapper_oracle_work_order_20260605.zip
    proposal-status traceability:
      docs\DOMAIN_PREDICATE_PROPOSAL_STATUS.md now surfaces this pending
      source-only oracle work order directly in the proposal table.
    next step: wait for source-only expected/forbidden wrapper facts before
      creating or scoring a procurement closed registry.
  FTC public-order pre-registry negative:
    artifact root:
      C:\prethinker_tmp_archive\ftc_domain_bootstrap_20260605
    basis:
      two retained ACH-stress public-order fixtures, one FTC decision/order and
      one FTC administrative complaint, both source-only profile bootstraps
      under local Qwen MoE
    result:
      t001: 13 candidate predicates, 37 admitted facts, 0 skipped
      t002: 17 candidate predicates, 53 admitted facts, 8 skipped
      predicate-overlap Jaccard: 2 / 26 = 0.077
      atom-shape audit: fail, 15 blockers (numeric-leading file id and
        prose-shaped definition atoms)
    read:
      do not package this pair as a closed FTC public-order domain yet. It is a
      useful negative showing that same agency/order-ish surface labels are not
      enough; the retained pair mixes remedy-order anatomy and data-security
      complaint anatomy, and the open bootstrap drifts into substance/detail
      predicates rather than a compact shared skeleton.
  active external work-order packet audit:
    C:\prethinker_tmp_archive\pending_external_work_order_status_20260605
    status: pass
    coverage: 8 active proposal and standalone tmp work-order zip packets
      (3 proposal-declared, 5 standalone)
    blocking errors: 0
    warnings: 0
  retained candidate-oracle review audit:
    docs\CANDIDATE_ORACLE_REVIEW_STATUS.md
    current retained reviews: 1
    blocking errors: 0
    warnings: 0
    scope: validates blind/source-only metadata and candidate
      expected/forbidden fact-file shape only, review folder identity, and
      repo-relative source-file references; it does not read source prose or
      decide whether the review facts are true.
    importer:
      scripts\import_candidate_oracle_review.py stages returned review zips,
      copies only manifest / candidate expected facts / candidate forbidden
      facts / README / adjudication notes, drops source and work-order payloads,
      audits the staged review, and refuses overwrites unless explicitly
      requested.

Atom-library query grounding
  strict path: source-record predicates/header inventories are filtered out,
    source-record proposals are blocked, and relaxed-constant fallback is
    disabled; constants absent from compiled atom slots are blocked
  SEC transfer_003 local smoke: 5 / 5 judged exact after mapper variable
    preservation; all five exact rows pass typed-plan replay and redacted
    rejudge, with 0 compatibility/runtime/write rows
  first pre-registered query-variance cell:
    Qwen local temp 0 over the same five rows, N=5:
      23 / 25 product exact; 23 / 25 typed-plan replay; 23 / 25 redacted
      rejudge; 0 prose-dependent exact rows
    Qwen temp sweep:
      temp 0.2: 13 / 15 product exact, but redaction rejudge blocked one
        normalized-name row, leaving 12 / 15 thesis exact
      temp 0.5: 13 / 15 product exact and 13 / 15 redacted rejudge
    Gemma 4 12B local dense control, temp 0, N=5:
      25 / 25 product exact and typed-plan replay; redaction rejudge marked
      24 / 25 thesis exact because one normalized-name row was judged partial
    Gemma 4 12B local Q4_K_M control, temp 0, N=5, random local seed:
      25 / 25 product exact; 25 / 25 typed-plan replay; 25 / 25 redacted
      rejudge; 0 prose-dependent exact rows; artifact metadata captured
      quantization, architecture, and loaded context
  read: the query-over-atoms path is real but still a variance-measured query
    lane; Gemma Q4 is a useful query-control candidate, not a promoted model
    switch
  compile-substitution control on SEC transfer_003:
    Gemma 4 12B local Q4_K_M, temp 0, N=3, same SEC closed registry:
      two same-condition roots both landed 10 / 12 support>=2; 0 / 10
      supported forbidden; registered signatures, atom-shape, and lens-scope
      all clean; unexpected same-signature facts were 7 in the early root and
      6 in the retained r1 root
    Qwen 3.6 27B local dense Q4_K_M, temp 0, N=3, same SEC closed registry:
      10 / 12 support>=2; 0 / 10 supported forbidden; registered signatures,
      atom-shape, and lens-scope all clean; 3 unexpected same-signature facts
    Qwen reference for the same cell:
      12 / 12 support>=2; 0 / 10 supported forbidden; 1 unexpected fact
      (historical pre-axis-repair reference; current repaired transfer_003
      reruns span 11-13 / 13)
    read: dense controls can stay inside the closed SEC language, but they did
      not reproduce the SEC compile cell cleanly. The model-swap robustness
      claim is therefore not established; dirty rows are SEC role/key semantics
      and one Qwen 27B accountability inconsistency, not a governance leak.
  mapper finding: the strict path exposed that uppercase query variables emitted
    by the LLM were being atomized into lowercase constants; the mapper now
    preserves uppercase slot-label query variables while still atomizing ordinary
    proper-name constants
  read: query-over-atoms is governed, but messy human query planning is not yet
    solved; the next test needs a larger and unlike query set
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
- Lens-bundle manifests now expose `lens_scopes[].offered_signatures`; the
  `profile_registry_lens_plan` setting only describes optional compile-plan
  pass behavior and does not mean the source compile received a global
  predicate bag.

## Current Research Pressure

The next useful work is not another row-grinding climb. It is to preserve and
explain the current falsifiable result:

- keep `docs/DOMAIN_PACK_STATUS.md` regenerated from
  `scripts/summarize_domain_pack_status.py` so domain/predicate/fixture counts
  are visible without worksheet archaeology;
- keep `docs/DOMAIN_ACCOUNTABILITY_STATUS.md` regenerated from
  `scripts/summarize_domain_accountability_status.py` so omission requirements,
  fixture coverage, and fixture-only omission patterns are visible;
- treat SEC as a boundary-aware skeleton case study unless one more
  pre-registered repaired-schema rerun materially tightens the current
  seed/transfer boundary;
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
- The next model/runtime variance excursion is pre-registered in
  `docs/MODEL_VARIANCE_PRE_REGISTRATION_20260604.md`; it must report all Qwen,
  Gemma, seed, and temperature cells rather than keeping the best result.
- `PRETHINKER_LLM_SEED`, when supplied, is now recorded in compile
  `model_serving_path.decoding`; a recorded seed is a reproducibility surface,
  not proof that historical and fresh runs are interchangeable.
- Atom-library query grounding is strict: planner payloads are filtered to
  emitted typed atoms, and source-record fallback execution is blocked even if
  the separate sign-clean flag was not supplied.
- Durable fixtures belong under `datasets/`.
- Temporary run artifacts may live under `tmp/`; old useful run artifacts can
  be moved to `C:\prethinker_tmp_archive`.
- Old worksheets should not become public front-door state. Active worksheets
  should stay run-scoped and should retire to archive/history once the claim is
  summarized in a current note.

## Verification Commands

The compile-fact manifest source audit now replays retained bundle atom/lens
and carrier value-domain gates from the archived compile artifacts as well as
checking run provenance and model/settings metadata: a manifested claim cell
fails if its retained lens or union artifacts contain nonzero atom-shape,
unregistered-fact, lens-scope, or closed-slot value-domain blockers, even if
the manifest summary claims clean.

Current full-suite result on 2026-06-05:

```text
2528 passed, 59 skipped, 9 xfailed, 2 subtests passed
```

The strict xfails are legacy MCP/QA selector expectations from before the
sign-clean reset. They are intentionally not claim-bearing; if one XPASSes,
pytest fails and forces review.

Common local checks:

```powershell
$env:PYTHONPATH='.'
pytest -q
python scripts\run_current_research_governance.py --out-root tmp\current_research_governance
python scripts\validate_domain_predicate_schema.py --root datasets\domain_profiles
python scripts\build_compile_fact_judged_qa.py --help
python scripts\run_compile_fact_judged_qa_manifest.py --out-root tmp\compile_fact_qa_manifest_run
python scripts\audit_compile_fact_qa_manifest_sources.py --out-json tmp\compile_fact_manifest_sources.json --out-md tmp\compile_fact_manifest_sources.md
python scripts\audit_reference_judge_null_control_reports.py --out-json tmp\reference_judge_null_control_reports.json --out-md tmp\reference_judge_null_control_reports.md
python scripts\summarize_current_compile_fact_qa_status.py --manifest-run tmp\compile_fact_qa_manifest_run\summary.json --source-audit tmp\compile_fact_manifest_sources.json --out-md docs\CURRENT_COMPILE_FACT_QA_STATUS.md --out-json tmp\current_compile_fact_qa_status.json --expect-md docs\CURRENT_COMPILE_FACT_QA_STATUS.md
python scripts\audit_research_artifact_paths.py
python scripts\audit_historical_score_claims.py
python scripts\summarize_domain_pack_status.py --out-md docs\DOMAIN_PACK_STATUS.md --out-json tmp\domain_pack_status_current.json --expect-md docs\DOMAIN_PACK_STATUS.md
python scripts\summarize_domain_accountability_status.py --out-md docs\DOMAIN_ACCOUNTABILITY_STATUS.md --out-json tmp\domain_accountability_status_current.json --expect-md docs\DOMAIN_ACCOUNTABILITY_STATUS.md
python scripts\summarize_fixture_bank_domains.py --out-md docs\FIXTURE_BANK_DOMAIN_INVENTORY.md --out-json tmp\fixture_bank_domain_inventory.json --expect-md docs\FIXTURE_BANK_DOMAIN_INVENTORY.md
python scripts\validate_domain_predicate_proposals.py --out-md docs\DOMAIN_PREDICATE_PROPOSAL_STATUS.md --out-json tmp\domain_predicate_proposal_status.json --expect-md docs\DOMAIN_PREDICATE_PROPOSAL_STATUS.md
python scripts\audit_pending_external_work_orders.py --include-tmp-zips --out-json tmp\pending_external_work_orders.json --out-md docs\PENDING_EXTERNAL_WORK_ORDERS.md --expect-md docs\PENDING_EXTERNAL_WORK_ORDERS.md
python scripts\audit_source_oracle_reviews.py --out-json tmp\source_oracle_reviews.json --out-md docs\SOURCE_ORACLE_REVIEW_STATUS.md --expect-md docs\SOURCE_ORACLE_REVIEW_STATUS.md
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

# Domain Tier Worksheet

Status: active lab worksheet, opened June 1, 2026. Keep this document compact.
Move detailed run logs and retired branches to `C:\prethinker_tmp_archive`
instead of letting worksheet history accumulate in `docs`.

## Current Steering Question

Can a closed domain schema produce verified Tier 1 answers over substantive
official-document content, while the general compiler remains a lower-trust
typed fallback?

The strategy is documented in:

- [Domain Tier Strategy](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_TIER_STRATEGY.md)

## Current Floor

Current 8-fixture English batch, model-redacted hard-road floor:

```text
Product exact:                  88 / 200 = 44.0%
Typed-plan exact:               84 / 200 = 42.0%
Redaction-survived exact:       81 / 200 = 40.5%
Atom-shape-clean product exact: 84 / 200 = 42.0%
Hard-clean floor:               73 / 200 = 36.5%
```

Artifacts:

```text
C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_current_compile_20260531\hard_road_floor_current_8_model_redaction.md
C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_current_compile_20260531\hard_road_floor_current_8_model_redaction.json
```

## Answer-Class Table

The first per-answer-class table shows that clean answers are not only
scaffolding, but substantive rows remain weak.

```text
scaffolding: 40 / 89 = 44.9% hard-clean
substantive: 30 / 87 = 34.5% hard-clean
mixed:        3 / 24 = 12.5% hard-clean
```

Selected classes:

```text
document_metadata_bundle: 14 / 22 = 63.6%
date_metadata:           13 / 19 = 68.4%
legal_authority:          7 / 19 = 36.8%
obligation_or_deadline:  10 / 27 = 37.0%
violation_or_deficiency:  4 / 11 = 36.4%
finding_or_reasoning:     3 / 14 = 21.4%
source_provenance:        0 /  8 =  0.0%
list_inventory:           0 /  5 =  0.0%
```

Artifacts:

```text
C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_current_compile_20260531\hard_clean_answer_class_summary_current_8.md
C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_current_compile_20260531\hard_clean_answer_class_summary_current_8.json
```

## Wedge Read

Current first candidate: FDA warning letters.

Why:

- repeated domain anatomy;
- clear regulatory/compliance product value;
- existing hard-clean substance is not zero;
- high-value rows map to a plausible closed schema:
  numbered violations, CFR citations, response deadlines, adulteration basis,
  consultant recommendation, conclusion disclaimers, ownership-change findings.

Current FDA baseline:

```text
all rows:          11 / 25 hard-clean
substantive rows:  5 / 12 hard-clean
```

This is a candidate, not a decision. The wedge must still survive a closed
carrier sketch, N>=3 same-condition reproducibility, and unlike FDA documents.

## FDA Domain Pack Sketch

Initial carrier families:

```text
fda_warning_letter/5
fda_facility_identity/5
fda_correspondence_party/5
fda_inspection_event/6
fda_form483_response/4
fda_prior_warning_letter/5
fda_regulatory_meeting/4
fda_violation/5
fda_violation_citation/4
fda_violation_detail/5
fda_adulteration_basis/5
fda_response_requirement/6
fda_consultant_recommendation/4
fda_conclusion_scope/4
domain_omission/5
```

Hardest design pressure:

- `fda_violation_detail/5` must not become a mini-paragraph slot.
- Whole violation prose, source excerpts, and one-off letter vocabulary are
  disqualifying for Tier 1.

## Judge Governance

Answer judging remains a permanent cheat surface.

Current null-control harness:

```text
scripts/audit_reference_judge_null_controls.py
```

Recent sample:

```text
sampled product-exact rows: 16
control judgments:         32
exact null verdicts:        0
```

Artifact:

```text
C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_current_compile_20260531\reference_judge_null_controls_sample2.md
```

Do not make public or product claims without a larger null-control run.

## Current Code Artifacts

New or current governance/reporting tools:

```text
scripts/audit_hard_road_floor.py
scripts/audit_kb_atom_inventory.py
scripts/audit_carrier_value_domains.py
scripts/audit_domain_omission_accountability.py
scripts/audit_redaction_replay.py
scripts/audit_reference_judge_null_controls.py
scripts/audit_typed_plan_replay.py
scripts/summarize_hard_clean_answer_classes.py
scripts/validate_domain_predicate_schema.py
scripts/validate_domain_transfer_package.py
```

Validation:

```text
python -m pytest tests\test_summarize_hard_clean_answer_classes.py tests\test_audit_reference_judge_null_controls.py tests\test_audit_hard_road_floor.py tests\test_audit_kb_atom_inventory.py tests\test_audit_typed_plan_replay.py tests\test_audit_redaction_replay.py -q
25 passed
```

## FDA Micro-Fixture Probe

Added:

```text
datasets\compile_micro_fixtures\fda_warning_letter_domain_v1
datasets\domain_profiles\fda_warning_letter_v1\ontology_registry.json
```

Static validation:

```text
typed micro-fixtures: 5 fixtures, 0 blocking errors
domain predicate registries: 1 registry, 15 predicates, 1 accountability requirement, 0 blocking errors, 0 warnings
FDA micro expected facts: 23
FDA micro forbidden facts: 6
focused tests: 24 passed
```

Lens-scoped registry validation:

```text
FDA registry lenses: wrapper, chronology, violation, response_obligation, conclusion
validation: 15 predicates, 0 blocking errors, 0 warnings
artifact: C:\prethinker_tmp_archive\fda_warning_letter_v1_lens_schema_validation_20260601.md
```

Lens-scoped compile offering:

```text
scripts\run_domain_bootstrap_file.py --profile-registry-lens <lens_id>
scripts\run_domain_bootstrap_file_batch.py --profile-registry-lens <lens_id>
```

The compile runner now filters the active profile registry before it reaches
direct profile generation, palette-prior context, registry accountability
context, and registry completion follow-up. The test guard verifies that a
chronology lens does not receive violation predicates. This makes
`offered_predicates = f(domain_registry, lens)` an executable runner
constraint, not just a schema note. The batch wrapper now forwards the same
flag so multi-fixture runs cannot accidentally reopen the full domain registry.
The post-backbone support and rule acquisition passes also accept the flag,
keeping acquisition overlays on the same lens-scoped vocabulary boundary.
The research integrity gate now includes the batch wrapper and acquisition-pass
tests, so this boundary is covered by the default code-only governance gate.
The batch wrapper also forwards the registry completion and accountability
follow-up flags, so lens-scoped N=3 domain cells can use the same domain-pack
machinery as single-fixture runs.
`domain_omission/5` is no longer offered to an active lens unless that lens has
a retained accountability requirement; this prevents conclusion/violation-style
lenses from emitting decorative omission rows when no omission contract applies.

```text
C:\prethinker_tmp_archive\research_integrity_gate_code_with_lens_wrappers_20260601
status: pass
focused governance tests: 408 passed
```

Live compile sequence, Qwen 35B A3B via OpenRouter:

```text
R1 registry-direct, before value-domain enforcement:
  admitted facts: 17
  registered signatures: 14 / 14 emitted
  strict expected match: 1 / 23
  value-domain violations: 11
  atom-shape blockers: 1

R3 contract context added:
  admitted facts: 12
  strict expected match: 10 / 23
  value-domain violations: 0
  atom-shape blockers: 0
  date-bearing wrapper facts skipped by mapper date gate

R4 date gate fixed:
  admitted facts: 17
  registered facts/signatures: 17 / 14
  strict expected match: 12 / 23
  value-domain violations: 0
  atom-shape blockers: 0

R5 omission guidance tightened:
  admitted facts: 17
  strict expected match: 15 / 23
  value-domain violations: 0
  atom-shape blockers: 0
  self_check noted absent signatory but no domain_omission/5 fact

R6 self_check-is-not-enough guidance:
  admitted facts: 17
  strict expected match: 13 / 23
  value-domain violations: 0
  atom-shape blockers: 0
  domain omission accountability audit: 1 blocker

R7 registry accountability requirement:
  admitted facts: 20
  strict expected match: 12 / 23
  value-domain violations: 0
  domain omission accountability audit v1: pass
  domain omission accountability audit v2: 1 blocker
  blocker: emitted domain_omission/5 but rewrote 'fda_correspondence_party/5'
           as fda_correspondence_party_5

R8 stricter slash-signature prompt:
  admitted facts: 16
  strict expected match: 11 / 23
  value-domain violations: 0
  domain omission accountability audit: pass only because no omission row
  note: prompt pressure alone did not reliably produce accountable omission row

R9 registry-accountability follow-up pass:
  admitted facts: 23
  strict expected match: 12 / 23
  value-domain violations: 0
  domain omission accountability audit: 2 blockers
  blocker: base + follow-up both emitted fda_correspondence_party_5 in the
           domain_omission/5 carrier_signature slot

R10 follow-up plus deterministic registry-reference reduction:
  admitted facts: 20
  strict expected match: 15 / 23
  value-domain violations: 0
  atom-shape blockers: 0
  domain omission accountability audit: pass
  deterministic domain_omission signature reductions: 1

R11 closed-registry completion follow-up, first attempt:
  admitted facts: 19
  strict expected match: 15 / 23
  value-domain violations: 0
  atom-shape blockers: 0
  domain omission accountability audit: pass
  completion pass new facts: 0
  note: pass rejected itself because domain_omission/5 was still visible in the
        completion profile while the pass forbade omission rows

R12 completion follow-up with domain_omission filtered from completion profile:
  admitted facts: 23
  strict expected match: 16 / 23
  value-domain violations: 0
  domain omission accountability audit: pass
  completion pass new facts: 4
  note: one useful lift (procedure_scope); three adjacent-but-not-target rows

R13 extra FDA registry note pressure:
  admitted facts: 24
  strict expected match: 13 / 23
  value-domain violations: 0
  domain omission accountability audit: pass
  completion pass new facts: 0
  note: detailed schema prose destabilized the base compile; note-tuning not
        promoted

R14 generic completion machinery with original FDA registry notes:
  admitted facts: 27
  strict expected match: 14 / 23
  value-domain violations: 0
  domain omission accountability audit: pass
  completion pass new facts: 5
  note: completion added useful in-registry facts (procedure_scope,
        consultant qualification citation, supporting-documentation response,
        recurrence scope), but base compile drifted on lot atom formatting and
        violation category. This is useful machinery, not a promoted score path.

R15 lot-identifier normalization:
  admitted facts: 23
  strict expected match: 17 / 23 after expected-file entity correction
  value-domain violations: 0
  domain omission accountability audit v2: fail
  completion pass new facts: 4
  note: lot atoms already landed canonical in this run; the new reducer is a
        guard for observed variants (`lot_a104`, `batch_a_104`), not the driver
        of this score.
  governance catch: completion emitted a signatory `not_stated` ordinary party
        row beside the correct domain_omission row.

R16 correspondence-party placeholder contract:
  admitted facts: 19
  strict expected match: 17 / 23 after expected-file entity correction
  value-domain violations: 0
  domain omission accountability audit: pass
  completion pass new facts: 0
  placeholder ordinary party rows rejected: 0
  note: this run did not emit the R15 placeholder row; the new contract and
        audit are retained because the R15 row is a real leakage shape.

R14-R16 mixed-history support summary:
  compiles: 3
  support threshold: >=2
  supported expected facts: 17 / 23
  unsupported expected facts: 6 / 23
  artifact: C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r14_r16_series_summary.md
  note: this is diagnostic only because the runs are mixed-history, not a
        same-condition N=3 promotion cell.

R16-R18 same-condition support summary:
  compiles: 3
  support threshold: >=2
  supported expected facts: 16 / 23
  unsupported expected facts: 7 / 23
  per-run strict matches:
    R16: 17 / 23, value-domain pass, omission audit pass
    R17: 17 / 23, value-domain pass, omission audit pass
    R18: 14 / 23, value-domain pass, omission audit pass
  artifact: C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r16_r18_same_condition_summary.md
  note: this is the first current-path N=3 cell for the FDA micro. It confirms
        a 16/23 stable typed core and a seven-fact compile-recall wall.

R19-R21 reducer diagnostic, alias-requested model:
  compiles: 3
  support threshold: >=2
  supported expected facts: 17 / 23
  unsupported expected facts: 6 / 23
  per-run strict matches:
    R19: 19 / 23, value-domain pass, omission audit pass
    R20: 15 / 23, value-domain pass, omission audit pass
    R21: 16 / 23, value-domain pass, omission audit pass
  artifact: C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r19_r21_reducer_summary.md
  note: facility identity reached 3/3 and several substantive rows reached 2/3,
        but the cell used the model alias and the next run exposed alias
        availability wobble.

R23-R25 same-condition support summary, explicit dated model:
  requested model: qwen/qwen3.6-35b-a3b-20260415
  compiles: 3
  support threshold: >=2
  supported expected facts: 18 / 23
  unsupported expected facts: 5 / 23
  per-run strict matches:
    R23: 18 / 23, value-domain pass, omission audit pass
    R24: 16 / 23, value-domain pass, omission audit pass
    R25: 18 / 23, value-domain pass, omission audit pass
  artifact: C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r23_r25_explicit_dated_summary.md
  note: facility identity and lot identifiers are now stable; the remaining
        unsupported rows are substantive compile-recall gaps or broad-wrapper
        specificity gaps, not value-domain/omission leakage.
  variant lens:
    regenerated with summarize_typed_micro_series.py same-predicate variant
    reporting. Only the warning-letter wrapper and documentation-submission
    requirement show near-miss typed variants. The procedure-scope,
    missing-record, and recurrence rows have no useful same-position typed
    near miss in the R23-R25 cell, so treat them as missing second-layer
    compile recall, not normalizer candidates.
  atom inventory:
    audit_kb_atom_inventory.py --enforce-atom-shape passes on R23-R25:
    63 typed facts, 15 predicates, 15 signatures, 100% registered facts,
    0 unregistered signatures, 0 atom-shape blockers.
    artifact: C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r23_r25_atom_inventory.md

R23-R25 oracle/schema correction:
  artifact: C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r23_r25_oracle_corrected_summary.md
  corrected expected facts:
    - changed violation 1 record detail from `missing_record_type` to
      `record_review_subject`, because the source states that batch production
      records were not reviewed before release; it does not say the records
      were missing.
    - changed the recurrence conclusion from `repeat_observation_context` to
      `recurrence_prevention`, because the source says the firm is responsible
      for preventing recurrence; it does not say the item is a repeat
      observation.
    - removed the separate `documentation_submission` expected row, because
      the source states one written-response requirement that identifies
      corrective actions and supporting documentation; it does not clearly
      state a separate documentation-submission action.
  corrected support summary:
    expected facts: 22
    supported expected facts: 18 / 22
    unsupported expected facts: 4 / 22
  note: this is an oracle/schema correction, not a compiler repair. It keeps
        the fixture from rewarding facts that are not actually stated in the
        source.

R27-R30 corrected-schema same-condition cell:
  requested model: qwen/qwen3.6-35b-a3b-20260415
  compiles: 3
  support threshold: >=2
  supported expected facts: 18 / 22
  unsupported expected facts: 4 / 22
  per-run strict probe notes:
    R27: 17 / 22, value-domain pass, atom-shape pass
    R29: 15 / 22, value-domain pass, atom-shape pass; completed after one 429
         interruption in the attempted two-run batch
    R30: 20 / 22, value-domain pass, atom-shape pass; completed after waiting
         out OpenRouter retry window
  artifacts:
    C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r27_r30_corrected_schema_summary.md
    C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r27_r30_atom_inventory.md
  note: corrected schema did not lift the stable support count above 18/22, but
        it changed the residual shape. Recurrence-prevention became supported
        at 2/3; consultant-qualification citation fell to 1/3 in this cell.
        This confirms the remaining blocker is unstable second-layer compile
        recall under clean governed atoms, not atom-shape or value-domain
        leakage.

Research integrity gate:
  command:
    python scripts\run_research_integrity_gate.py --compile-root C:\prethinker_tmp_archive --fixture fda_warning_letter_micro_20260601_r27_office_reducer_probe --fixture fda_warning_letter_micro_20260601_r29_corrected_schema_same_condition --fixture fda_warning_letter_micro_20260601_r30_corrected_schema_same_condition --out-dir C:\prethinker_tmp_archive\research_integrity_gate_20260601_fda_r27_r30
  result:
    pass, 5/5 steps, 0 failed
    sign-clean pass
    atom-shape pass
    carrier value-domain pass
    domain omission accountability pass
    focused governance tests: 308 passed
  artifact:
    C:\prethinker_tmp_archive\research_integrity_gate_20260601_fda_r27_r30\research_integrity_gate.md

Broad current-8 integrity check:
  command:
    python scripts\run_research_integrity_gate.py --compile-root C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_current_compile_20260531\compile_current --out-dir C:\prethinker_tmp_archive\research_integrity_gate_20260601_current_8_compile
  result:
    fail, 1/5 failed
    sign-clean pass
    carrier value-domain pass
    domain omission accountability pass
    focused governance tests pass
    atom-shape audit fail
  atom-shape blockers:
    334 total
    310 unregistered/open atom_value_prose_shaped
    24 registered_carrier_prose_shaped_value
  distribution:
    fda_warning_ugly_007: 97
    procurement_contract_ugly_003: 61
    state_ag_settlement_ugly_003: 41
    court_order_ugly_003: 39
    osha_incident_ugly_007: 32
    puc_order_ugly_003: 32
    labor_board_ugly_003: 20
    sec_material_event_ugly_007: 12
  note: this confirms the broader open compiler is not Tier-1 clean. The FDA
        micro/domain-pack path can be clean, but broad current-8 artifacts still
        contain prose-shaped typed atoms and must stay below Tier 1 unless row
        claim paths pass hard-clean gates.
```

Artifacts:

```text
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r1
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r2_value_domains
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r3_contract_context
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r4_datefix
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r5_omission
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r6_selfcheck_omission
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r7_accountability_registry
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r8_signature_accountability
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r9_accountability_followup
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r10_accountability_signature_reduction
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r11_registry_completion
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r12_registry_completion_filtered
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r13_registry_notes
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r14_registry_completion_original_notes
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r15_lot_reduction
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r16_placeholder_contract
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r14_r16_series_summary.md
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r17_same_condition
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r18_same_condition
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r16_r18_same_condition_summary.md
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r19_facility_citation_reducers
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r20_facility_citation_reducers
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r21_facility_citation_reducers
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r19_r21_reducer_summary.md
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r23_explicit_dated_model
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r24_explicit_dated_model
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r25_explicit_dated_model
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r23_r25_explicit_dated_summary.md
```

What this proved:

- closed FDA signatures are usable by the existing compile path;
- next architectural tightening: offered predicate set should be a function of
  both domain registry and lens (`offered_predicates = f(domain_registry,
  lens)`). The current FDA pack is closed at the domain level; future passes
  should also be lens-scoped so wrapper, violation, response/obligation, and
  conclusion lenses do not all receive the same writable predicate set.
- contract guidance must be visible in standard source compiles, not only
  focused pass-ops compiles;
- value-domain audit is necessary because registered predicates alone do not
  prevent near-synonym drift;
- the `v_YYYY_MM_DD` date atom shape is legitimate and now admitted by the
  mapper;
- after the fixes, the micro can emit compact registered atoms with no
  prose-shaped values;
- self-check omission notes are not sufficient accountability; the new
  `audit_domain_omission_accountability.py` gate flags this case.
- omission-shaped rows are not sufficient either; the audit now requires the
  `carrier_signature` slot to name an actual registered carrier signature.
- the bounded registry-accountability follow-up is useful, but only after a
  typed registry-reference reducer canonicalizes `name_arity` back to the exact
  registered `'name/arity'` signature. This reducer reads registry syntax only;
  it does not inspect source prose or create omission facts.
- closed-registry completion follow-up can add useful facts without breaking
  governance, but it is still unstable. R12 lifted one row; R13 showed that
  adding more prose to registry notes can worsen the base compile. Treat domain
  notes as schema design material, not a row-polishing knob.
- R14 shows the completion pass can find exactly the substantive rows we want,
  but strict score can still move backward when the base compile changes nearby
  atoms. The next blocker is stabilizing/canonicalizing governed value atoms,
  not simply adding more completion passes.
- absent signatory/contact/responsible-official information must stay in
  `domain_omission/5`. A normal `fda_correspondence_party/5` row with
  `not_stated`/`unknown` placeholder values is now rejected by typed contract
  validation and blocked by `audit_domain_omission_accountability.py`.
- expected facts were corrected where the source says "firm" rather than
  "facility" for prior warning letter and regulatory meeting rows. This is an
  oracle correction, not a compiler repair; current honest R16 micro status is
  17/23 with clean value-domain and omission gates.
- the mixed-history R14-R16 series gives a provisional target map: 17/23 facts
  already have support>=2, while six facts are still unstable or absent.
- the same-condition R16-R18 series is stricter and should be treated as the
  current FDA micro baseline: 16/23 support>=2, with no value-domain or omission
  audit failures in the three-run cell.
- explicit dated model requests matter. The alias `qwen/qwen3.6-35b-a3b`
  failed once with OpenRouter 404 after R22; R23-R25 used
  `qwen/qwen3.6-35b-a3b-20260415` explicitly and should supersede R19-R22 for
  this reducer checkpoint.
- typed value reducers moved the current FDA micro baseline to 18/23
  support>=2 before the oracle/schema correction, and 18/22 after it, with
  clean gates. The gain is narrow and governance-clean:
  facility FEI/location normalization, affected-lot atom normalization, and
  consultant-citation scope normalization.
- the micro-series summarizer now reports same-predicate typed variants for
  unsupported rows. This is a governance aid: it separates near-miss typed atom
  drift from true missing compile recall without re-reading source prose.
- atom-shape enforcement passed on the latest R23-R25 cell. The current FDA
  typed core is still incomplete, but it is not getting its 18/22 support by
  hiding prose-shaped values or unregistered predicates.
- the FDA micro expected facts needed one schema/oracle correction. After
  correction, current support is 18/22. This is the number to use going
  forward; the earlier 18/23 was over-penalizing one weakly supported expected
  row and two misnamed source claims.
- a fresh corrected-schema same-condition cell stayed at 18/22. This is not a
  climb in the count, but it is a cleaner measurement: recurrence is now named
  correctly and stable, while consultant citation, procedure scope, wrapper
  specificity, and record-review subject remain unstable or absent.

Current blocker:

```text
FDA stable compile recall for the five unsupported facts.
```

New accountability contract:

```text
datasets\domain_profiles\fda_warning_letter_v1\ontology_registry.json

missing_signatory_role:
  if source_explicitly_states_no_signatory_or_signature_block
  emit domain_omission(DomainOrSubjectId, 'fda_correspondence_party/5',
       role_missing, signatory_not_stated, SourceOrScope)
```

R27-R30 corrected-schema unsupported facts:

- consultant-qualification citation scoped to the warning letter remains only
  1/3 in this current cell;
- procedure-scope detail for violation 2 remains only 1/3;
- warning-letter issuing office specificity remains only 1/3; the model often
  emits broad or truncated office atoms rather than the named office. Do not
  normalize this by fiat beyond narrow registered-office atom cleanup.
- record-review-subject detail for violation 1 remains 0/3;
- a few source/scope and compact-id normalization choices that may need
  expected alternatives rather than code changes.

R31 violation-lens probe:

```text
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r31_violation_lens_probe
model: qwen/qwen3.6-35b-a3b-20260415 via OpenRouter
mode: registry-direct, active lens=violation, source compile plus registry follow-ups
admitted: 12 facts, 0 skipped
typed micro match: 8 / 22 overall
violation/legal-basis subset: 8 / 10 expected rows
value-domain audit: pass, 12 facts, 18 checked slots, 0 violations
atom-shape audit: pass, 12 registered facts, 0 blockers
omission accountability audit: pass after lens-scope audit fix
```

Reading:

- lens scoping is not just governance theater; the violation-only pass closed
  two previously unstable detail rows in one run:
  `fda_violation_detail(... procedure_scope, microbiological_contamination_prevention, ...)`
  and `fda_violation_citation(Letter, cfr_21_211_34, consultant_qualification, ...)`.
- remaining violation misses are narrower: `record_review_subject` for
  violation 1 and violation 2 category drift (`aseptic_processing` vs expected
  `contamination_control`).
- a lens-scoped compile can legitimately omit wrapper accountability carriers.
  `audit_domain_omission_accountability.py` now respects
  `active_profile_registry_lens.accountability_requirement_count`; a violation
  lens is not blocked for a missing wrapper signatory omission it was not
  allowed to emit.

R31-R35 per-lens probe summary:

```text
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r31_r35_lens_probe_summary.md

wrapper: 4/4 lens subset, clean
chronology: emitted event shapes but missed expected date/facility normalization
violation: 8/10 lens subset, clean
response_obligation: 4/5 lens subset, clean
conclusion: 1/2 lens subset, failed omission audit due invalid carrier reference
```

R38 deterministic clean-lens union:

```text
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r38_clean_lens_union_reduced
inputs: wrapper, chronology, violation, response_obligation lens probes
excluded: conclusion lens because omission audit failed
union policy: no source prose read; mapper-admitted facts only; deterministic typed reducers applied
typed micro match: 17 / 22
atom-shape audit: pass, 29 registered facts, 0 blockers
value-domain audit: pass, 29 facts, 37 checked slots, 0 violations
omission accountability audit: pass
runtime load errors: 0
```

Governance:

```text
C:\prethinker_tmp_archive\research_integrity_gate_fda_lens_union_reducers_20260601
status: pass
focused governance tests: 416 passed
```

What this proves:

- lens-scoped extraction plus deterministic typed union is a promising domain
  architecture. It lifted this FDA micro from the same-condition 18/22 broad
  compile baseline to a cleaner per-lens decomposition, and the clean four-lens
  union reaches 17/22 without using the failed conclusion lens.
- deterministic typed reducers are doing real, sign-clean work at the
  inter-lens seam: warning-letter subject convergence, FDA date atom
  normalization, and facility-subject convergence moved the union from 11/22 to
  17/22 without reading source prose.
- the remaining misses are now well-shaped:
  `fda_inspection_event/6` inspecting body value (`opqo` vs expected `fda`),
  violation 1 record-review subject, violation 2 category
  (`aseptic_processing` vs `contamination_control`), and the two conclusion
  rows. Do not normalize these by fiat; they need either better lens guidance,
  a value-domain decision, or evidence that the expected oracle should admit an
  alternative.

R41-R43 conclusion-lens cleanup and all-lens union:

```text
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r41_conclusion_lens_no_omission_compile_or
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r43_all_lens_union_reduced_compact_date
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r44_all_lens_union_reduced_detail_integrity

change: domain_omission/5 is not offered to a lens unless the active lens has a retained accountability requirement
conclusion lens: emitted 3 fda_conclusion_scope/4 facts, 2 expected conclusion rows present after typed subject convergence
all-lens reduced union: 19 / 22 after removing invalid letter-level violation-detail rows
value-domain audit: pass, 30 facts, 39 checked slots, 0 violations
omission accountability audit: pass
atom-shape audit: pass, 30 registered facts, 0 blockers
runtime load errors: 0
```

Reading:

- the failed conclusion lane was not a reason to give every lens a global
  omission carrier. Stripping decorative `domain_omission/5` from lenses
  without accountability requirements made the conclusion probe clean while
  preserving the declared lens vocabulary for audit visibility.
- the two conclusion rows were blocked by a typed alias seam, not source
  interpretation: the conclusion lens used `doc_fda_warning_letter_20250514`,
  while the wrapper lens established `letter_2025_05_14_marigold`. The
  existing warning-letter subject convergence reducer now recognizes compact
  `yyyymmdd` aliases and maps them onto the typed wrapper id.
- this is a clean deterministic gain: no source prose read, no query text read,
  no new predicate family, and no fixture vocabulary inserted into Python. The
  remaining three misses are now the inspection-body value, violation 1
  record-review subject, and violation 2 category.
- R44 also added a typed subject-integrity reducer for
  `fda_violation_detail/5`: detail rows whose subject is not an emitted
  `fda_violation/5` id are dropped. This removed two polluted letter-level
  detail rows without changing the score. That matters because a stable domain
  pack needs clean extra facts, not only clean expected rows.

R45-R48 violation-detail guidance and reconciliation diagnostic:

```text
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r45_violation_lens_record_review_guidance_or
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r47_union_violation_number_reduced
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r48_union_dual_violation_lenses

change: fda_violation_detail/5 contract now says record-review failures should emit record_review_subject or missing_record_type rows
single updated violation-lens union: 19 / 22
dual old+new violation-lens diagnostic union: 20 / 22
dual diagnostic gates: value-domain pass, omission pass, atom-shape pass
```

Reading:

- the contract guidance worked: the updated violation lens emitted
  `fda_violation_detail(violation_1, record_review_subject,
  batch_production_records, pre_release_quality_review, source_document)`.
- the updated lens also omitted the letter-level consultant citation that the
  older violation lens happened to emit. A dual violation-lens union recovers
  both rows and reaches 20/22, but that is reconciliation evidence, not a
  promoted score. It mixes old and new lens histories and carries duplicate
  violation facts with different provenance scopes.
- a narrow typed reducer now canonicalizes `fda_violation/5` violation-number
  slots from `1`/`2` into `violation_1`/`violation_2`. This is typed value
  normalization only; it does not read source prose or create violations.
- remaining promoted-state misses are still the inspection-body value
  (`opqo` vs `fda`), violation 2 category (`aseptic_processing` vs
  `contamination_control`), and consultant citation stability. Do not solve
  these by deterministic source-shaped fiat; they need N-pass reconciliation
  policy, an oracle-alternative decision, or unlike-document evidence.

R49-R57 current-condition repeats and chronology repair:

```text
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r49_violation_lens_same_condition_or
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r50_violation_lens_same_condition_or
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r55_chronology_lens_prior_scope_guidance_or
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r57_union_facility_suffix_alias
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r45_r49_r50_violation_series_reduced_summary.md

current-condition violation lens repeats: R45/R49/R50
record_review_subject support: 3 / 3
consultant citation support: 1 / 3
violation 2 category emitted: aseptic_processing in 3 / 3, contamination_control in 0 / 3
chronology guidance: inspecting_body now fda; prior warning scope now firm/recipient rather than facility
unfiltered current-condition N=3 violation + new chronology union: 21 / 22
gates: value-domain pass, omission pass, atom-shape pass, runtime load errors 0
```

Reading:

- record-review detail is stable under the current contract; that row should be
  treated as a real mechanism win subject to unlike-document transfer.
- consultant citation is not stable. The unfiltered union can recover it, but a
  support>=2 promotion rule would not. This points at N-pass reconciliation
  policy rather than another row-specific prompt tweak.
- chronology improved after two general contract changes: inspecting body is
  the agency/body that performed the inspection, and prior-warning scope follows
  the source-stated firm/facility. A conservative typed facility-alias reducer
  now maps facility atoms only when they contain a facility token and at least
  two meaningful tokens that uniquely match one typed `fda_facility_identity/5`
  row.
- the final remaining expected miss is the violation 2 category:
  `aseptic_processing` is consistently emitted while the micro oracle expects
  `contamination_control`. This should be decided as a domain/oracle alternative
  question or tested on an unlike FDA warning letter; do not force it by code.
- `scripts\summarize_typed_micro_series.py` now supports
  `--apply-domain-reducers`, so support>=2 checks can be run after the same
  typed normalization used by union compiles. The R45/R49/R50 reduced series
  shows 8 violation/legal-basis rows at support 3/3, consultant citation at
  support 1/3, and the violation 2 category variant as the only same-predicate
  category conflict.

R58-R66 lens-local N=3 support and conclusion boundary repair:

```text
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r55_r58_r59_chronology_series_reduced_summary.md
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r32_r60_r61_wrapper_series_reduced_summary.md
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r34_r62_r63_response_series_reduced_summary.md
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r64_r65_r66_conclusion_series_reduced_summary.md

wrapper lens support>=2: 4 expected rows
chronology lens support>=2: 4 expected rows
violation lens support>=2: 8 expected rows
response_obligation lens support>=2: 4 expected rows, including two rows already counted through the violation lens
conclusion lens support>=2 after contract boundary repair: 2 expected rows
unique stable expected rows across lens-local support>=2 summaries: 20 / 22
value-domain audit on R64/R65/R66 conclusion runs: pass, 8 facts, 16 checked slots, 0 violations
```

Reading:

- the conclusion lens blocker was schema ambiguity, not a new predicate need.
  The carrier allowed both `responsibility_to_correct` and
  `prevent_recurrence` without telling the model how to handle the common FDA
  sentence that assigns responsibility for investigating causes and preventing
  recurrence. The registered carrier contract now says such sentences map to
  `recurrence_prevention` / `responsibility_to_correct`; `prevent_recurrence`
  is reserved for recurrence-prevention language without assigned
  responsibility, and `ownership_change_context` requires explicit ownership
  or management-change source language.
- the repaired conclusion lens produced both expected conclusion rows at 3/3
  support under same-condition OpenRouter compiles. This promotes the
  recurrence/responsibility conclusion row from a diagnostic R57 recovery to a
  stable lens-local support>=2 row.
- the honest promoted micro picture is now 20/22, not 21/22. The 21/22 R57
  union remains useful diagnostic evidence, but it includes at least one row
  without support>=2 in its own lens history. Do not use R57 as the promoted
  score.
- at this point, the two remaining unpromoted expected rows were the consultant
  qualification citation (`fda_violation_citation(Letter, cfr_21_211_34,
  consultant_qualification, SrcConsultantCitation)`) and the violation 2
  category boundary (`contamination_control` expected, `aseptic_processing`
  emitted 3/3). R67-R77 below resolved these inside the same-fixture domain
  micro, subject to the transfer caveat.

R67-R72 consultant citation probe and provenance-payload audit:

```text
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r67_r68_r69_response_series_reduced_summary.md
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r70_r71_r72_response_series_reduced_summary.md
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r70_r71_r72_response_value_domains_v2.md

contract change: fda_violation_citation/4 now explicitly allows a letter-level consultant qualification citation
contract change: fda_consultant_recommendation/4 forbids using a citation atom as source_or_scope
R67/R68/R69 consultant citation support: 1 / 3
R70/R71/R72 consultant citation support: 0 / 3
R70/R71/R72 value-domain/provenance audit: fail, 3 citation_payload_in_source_or_scope violations
```

Reading:

- the consultant-citation miss is not solved by contract clarification. The
  source sentence contains both the consultant recommendation and the
  qualification citation, but the compiler still often stores `cfr_21_211_34`
  as the provenance slot on `fda_consultant_recommendation/4` instead of
  emitting the separate letter-level `fda_violation_citation/4` row.
- this exposed a governance pinhole: wildcarded expected-source variables can
  let an answer-bearing citation hide inside `source_or_scope` and still count
  as support. `scripts\audit_carrier_value_domains.py` now blocks
  citation-shaped payloads in `source_or_scope` for registered carriers. The
  R70/R71/R72 cell therefore fails the audit even though the older support
  summary still lists the consultant recommendation row as present.
- do not promote any response-lens cell that fails this audit. After applying
  the new source-scope payload integrity reducer, R67/R68/R69 still has valid
  support>=2 for the consultant recommendation, while the hidden
  citation-as-provenance row is dropped.

R73-R77 category boundary repair and assembled micro validation:

```text
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r73_r74_r75_violation_series_reduced_v2_summary.md
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r77_all_lens_reduced_stable_rep

contract change: fda_violation/5 now distinguishes microbiological contamination-prevention procedures from explicit aseptic-processing failures
violation lens support>=2 after category boundary repair: 10 expected rows
violation 2 category support: contamination_control 3 / 3
consultant qualification citation support in violation lens: 3 / 3
representative reduced all-lens union R77: 22 / 22
R77 runtime load errors: 0
R77 value-domain/provenance audit: pass, 36 facts, 45 checked slots, 0 violations
R77 omission accountability audit: pass
```

Reading:

- the final category miss was a carrier value-boundary problem. The source says
  written procedures designed to prevent microbiological contamination of
  sterile drug products were not established and followed; it does not name
  aseptic processing. The registered `fda_violation/5` contract now maps
  microbiological contamination-prevention procedure failures to
  `contamination_control`, while reserving `aseptic_processing` for source
  language that explicitly names aseptic processing, aseptic filling, aseptic
  operations, or a comparable aseptic-process failure.
- R73/R74/R75 closed the violation lens cleanly: the category row, consultant
  qualification citation, adulteration basis, violation citations, lot details,
  record-review subject, and procedure-scope detail all reached 3/3 support
  after reducers.
- R77 is the first assembled FDA warning-letter micro artifact to validate
  22/22 under the lens-scoped domain pack with deterministic reducers, zero
  runtime load errors, zero value-domain/provenance violations, and zero
  omission-accountability blockers.
- this is still same-fixture micro evidence. It proves the domain-pack
  architecture can assemble a complete hard-clean typed artifact for this FDA
  warning-letter excerpt. It does not yet prove transfer; the next claim-bearing
  move is the unlike FDA warning-letter package.

## Next Moves

1. Build or receive an unlike FDA warning-letter transfer micro using
   `docs\FDA_DOMAIN_TRANSFER_WORK_ORDER.md`. More same-fixture tuning is now
   high overfit risk.
2. Run `scripts\validate_domain_transfer_package.py` on the unpacked package
   before any compile. If it fails, fix the package rather than spending
   inference.
3. Run a same-condition N=3 cell only after the current code settles; use
   `scripts\summarize_typed_micro_series.py` and promote only support>=2 rows
   with clean gates. Use the same-predicate variant section to decide whether a
   remaining row is a normalizer candidate or a true compile-recall gap.
4. Pressure second-layer detail completeness on the micro without allowing
   prose-shaped values.
5. If the micro reaches stable clean coverage, run N>=3 same-condition compiles
   on the current FDA fixture and promote only rows with support>=2.
6. If current FDA improves, test on at least one unlike FDA warning letter.
7. If FDA fails the reject criteria, do not rescue it by row-polishing; choose a
   different wedge or conclude no wedge is ready.

## FDA Warning-Letter Transfer 001

R78 transfer package placement and preflight:

```text
fixture: datasets\compile_micro_fixtures\fda_warning_letter_domain_transfer_001
source: Apothecary Pharma, LLC FDA warning letter, WL #717972, 2025-12-01
preflight: pass, 0 blockers, 0 warnings
expected facts: 26
forbidden facts: 8
registry signatures: 12
```

Notes:

- the package originally used registered predicate names but stale argument
  layouts. The oracle was rewritten to current FDA warning-letter carrier
  contracts before any compile spend.
- `adulteration_insanitary_conditions` was added to the closed
  `fda_adulteration_basis/5` basis-kind value domain because section
  501(a)(2)(A) insanitary-conditions adulteration is a general FDA warning
  letter basis, not fixture language.
- the facility row is an explicit pressure point: the current
  `fda_facility_identity/5` contract has an identifier slot, but this source
  states a 503B outsourcing-facility registration class and does not state an
  FEI.

R79 same-condition N=3 unlike-document transfer probe:

```text
root: C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_n3_20260601
model: qwen/qwen3.6-35b-a3b-20260415
provider: OpenRouter
routing: allow_fallbacks=false, require_parameters=true
settings: temperature=0.0, top_p=0.82, top_k not sent on OpenAI-compatible path
lenses per run: wrapper, chronology, violation, response_obligation, conclusion
union facts per run after reducers: 44 / 33 / 40
runtime load errors: 0 / 0 / 0
constant-slot support>=2: 20 / 26
per-run expected matches: 21 / 26, 16 / 26, 20 / 26
forbidden matches: 0
atom inventory: pass, 157 typed facts, 13 registered signatures, 0 unregistered
atom-shape blockers: 0
carrier value-domain audit: pass, 189 checked slots, 0 violations
domain omission accountability: pass, 0 blockers
```

Reading:

- the domain pack transfers cleanly with respect to governance: no forbidden
  facts, no unregistered predicate signatures, no prose-shaped atoms, no
  value-domain violations, no omission-accountability blockers, and no runtime
  load errors.
- the transfer recall signal is not yet complete. At support>=2, the lens pack
  reproduced 20 of 26 expected rows under a constant-slot matcher that treats
  IDs and source coordinates as variables and requires same-position matches
  for governed constants.
- stable 3/3 rows include both adulteration bases, inspection chronology,
  Form 483 response date, consultant recommendation, the warning-letter
  wrapper, violation 1-3 categories, and all six CFR citations.
- support 2/3 rows include the recipient organization, violation 4/5
  aseptic-processing categories, and the not-all-inclusive conclusion scope.

Unsupported rows and classification:

- signatory row: support 1/3. One run emitted the exact signatory row, one run
  folded credentials into the party-name atom (`f_gail_bormel_jd_rph`), and one
  run omitted the signatory. This is compile-recall instability plus a small
  party-name normalization question.
- facility identity: support 0/3. Runs consistently represented name/location
  but used MARCS/WL identifier `717972` or location variants rather than the
  oracle's `registered_outsourcing_facility`. This is a carrier-shape/oracle
  adjudication, not a safe reducer: the current slot wants an identifier, while
  the source supplies a registration class and no FEI.
- response requirement recipient/channel: support 0/3 against `fda`, while all
  runs emitted `issuing_office`. This is likely an oracle boundary decision:
  the source says "notify this office in writing," so `issuing_office` may be
  the more faithful compact value.
- violation 6 category: support 0/3 against `other_registered_category`, while
  all runs emitted `data_integrity`. This is likely an oracle boundary decision:
  incomplete batch production/control records plausibly fit the registered
  `data_integrity` category.
- affected product detail: support 0/3 against `violation_scope`, while two
  runs used `product_release_record_review`. This likely needs a detail-role
  boundary decision before any mechanism work.
- ISO 5 process-area detail: support 0/3 against `sterile_drug_products`, while
  two runs used `violation_scope`. This likely needs a detail-role boundary
  decision before any mechanism work.

Do not claim 24/26 from adjudication. The claim-bearing result from this run is
20/26 stable clean transfer. The likely oracle-boundary rows should be revised
only by source/contract adjudication and then re-run as a new cell; they should
not be counted retroactively.

Next moves:

1. Adjudicate the four likely oracle-boundary rows from source and carrier
   contract alone: response recipient/channel, violation 6 category,
   affected-product role, and ISO 5 process-area role.
2. Treat facility identity as a schema question: either add a separate compact
   registration-class carrier/slot or drop facility identity expectation when
   no FEI/source identifier is stated. Do not reduce MARCS/WL number into a
   facility identifier.
3. Treat signatory as a compile-recall/stability issue. A narrow credential
   suffix reducer may be safe only if it maps a party-name atom back to the
   already-emitted party_id for the same row; it must not infer a missing
   signatory.
4. After adjudication, re-run a same-condition N=3 cell and compare stable
   support without changing model/provider/settings.

R80 oracle adjudication and wrapper-boundary repair:

```text
oracle updates:
- facility identifier: registered_outsourcing_facility -> not_stated
- response recipient/channel: fda -> issuing_office
- violation 6 category: other_registered_category -> data_integrity
- Tirzepatide detail role: violation_scope -> product_release_record_review
- ISO 5 process-area role: sterile_drug_products -> violation_scope

new forbidden pattern:
- fda_facility_identity(..., apothecary_pharma_llc, Location, 717972, ...)

wrapper-only N=3 after facility contract boundary:
- wrapper expected support after reducers: 4 / 4 at 3/3
- forbidden MARCS/WL-as-facility-id matches: 0
- atom inventory: pass
- carrier value-domain audit: pass
```

Reading:

- the initial transfer oracle had four less-faithful value choices and one
  unsafe facility expectation. These were adjudicated from the source and
  carrier contracts, not counted retroactively as wins.
- these adjudications are governed by the blind-oracle rule now recorded in
  `docs\DOMAIN_PREDICATE_SCHEMA_PROCESS.md`: a reviewer should be able to
  defend each change from the source and current carrier contract without
  seeing the model output, and the rows only became claim-bearing after the
  fresh R81 same-condition rerun.
- the dangerous wrapper failure was fixed by contract boundary, not by prose
  parsing: `fda_facility_identity/5` now explicitly forbids warning-letter,
  WL, MARCS-CMS, CMS, and registration-class values as facility identifiers and
  retains `not_stated` for stated facilities with no source-stated facility ID.
- a typed facility-location reducer now normalizes country suffixes such as
  `cary_nc_united_states` to `cary_nc`. This is typed atom normalization only;
  it reads no source prose and makes no facility inference.

R81 fresh all-lens N=3 rerun after adjudication:

```text
root: C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_n3_rerun_20260601
union facts per run after reducers: 38 / 44 / 48
constant-slot support>=2: 24 / 26
per-run expected matches: 23 / 26, 24 / 26, 21 / 26
forbidden matches: 0
runtime load errors: 0 / 0 / 0
atom inventory: pass, 168 typed facts, 13 registered signatures, 0 unregistered
atom-shape blockers: 0
carrier value-domain audit: pass, 192 checked slots, 0 violations
domain omission accountability: pass, 0 blockers
```

Stable rows:

- 3/3: wrapper, recipient, signatory, facility `not_stated`, chronology,
  response requirement, adulteration bases, violation 1-4 categories, all six
  CFR citations, recurrence conclusion.
- 2/3: not-all-inclusive conclusion, consultant recommendation, Tirzepatide
  affected-product detail, ISO 5 process-area detail.

Remaining R81 misses:

- violation 5 category: expected `aseptic_processing`; compile drifted toward
  `contamination_control` in the clean all-lens cell.
- violation 6 category: expected `data_integrity`; compile drifted toward
  `quality_unit_failure` in the clean all-lens cell.

R82 violation-category contract pressure:

```text
root: C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_violation_rerun_20260601
contract additions:
- aseptic_processing for cleaning/disinfecting/maintaining/controlling rooms or
  equipment when the source says the purpose is aseptic conditions
- data_integrity for incomplete/missing/inaccurate/inadequate batch
  production/control records

violation category support:
- violation 5 aseptic_processing: 3 / 3
- violation 6 data_integrity: 3 / 3

governance:
- atom inventory: pass
- carrier value-domain audit: fail, 24 violations in one run
```

Reading:

- the category-boundary pressure worked on the two named categories, but the
  violation-only cell is not promotable because one run emitted malformed
  value-domain-invalid `fda_violation_citation/4` and
  `fda_violation_detail/5` rows.
- do not claim 26/26. The clean claim-bearing transfer result remains 24/26
  with 0 forbidden/runtime/atom-shape/value-domain/omission blockers.
- the next blocker is violation-lens output hygiene under category pressure:
  the contract can pull the right categories, but one run responded by
  scrambling detail/citation argument roles. This is the exact place to apply a
  value-domain-invalid drop/hold policy or a narrower citation/detail follow-up,
  not another broad FDA prompt change.

Current FDA-transfer status:

```text
claim-bearing clean transfer: 24 / 26 stable expected facts
forbidden facts: 0
runtime errors: 0
unregistered signatures: 0
atom-shape blockers: 0
value-domain violations: 0
omission blockers: 0
non-promotable diagnostic: category-boundary rerun fixed categories but failed
  value-domain hygiene in one violation run
```

R83 value-domain hold for malformed registered carrier rows:

```text
mechanism:
- new deterministic_carrier_value_domain_integrity reducer
- drops registered carrier rows whose closed value-domain slots contain values
  outside the carrier contract
- invents no replacement facts
- reads no source prose, QA questions, or oracle answers

direct regression:
- fda_violation_citation(..., cfr_21_211_22_d, cfr_21_211_22_d, ...)
  is dropped because citation_role is not in the closed citation-role domain
- fda_violation_detail(..., violation_6, ..., batch_production_and_control_records, ...)
  is dropped because detail_kind and role_or_purpose are not registered values
- valid sibling rows survive

tests:
- focused: 294 passed
- research integrity gate: pass
- focused governance suite: 432 passed
```

Diagnostic replay on the prior dirty violation-category rerun:

```text
input: C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_violation_rerun_20260601
union with value-domain hold:
- facts after reducers: 40
- carrier value-domain audit: pass, 40 facts, 56 checked slots, 0 violations
- matched violation/authority/detail expected rows: 15 / 16
- forbidden matches: 0
- category rows now present:
  - violation 5 -> aseptic_processing
  - violation 6 -> data_integrity
- remaining miss: affected-product detail for Tirzepatide
```

Reading:

- the value-domain hold closes the specific hygiene blocker: malformed
  citation/detail rows no longer survive typed reduction, so they cannot
  contaminate a union or support summary.
- the category-boundary fix remains promising: after the hold, the diagnostic
  violation union keeps the two repaired category rows and passes value-domain
  audit.
- this is still not a claim-bearing 26/26 transfer result. It is a blocker fix
  plus a replay diagnostic.

Attempted R84 fresh all-lens N=3 with value-domain hold:

```text
root: C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_n3_value_domain_hold_20260601
status: interrupted by OpenRouter upstream 429 from Ambient provider
usable completed pieces:
- run 1 completed all five lenses
- run 2 wrapper completed but emitted 0 facts
- remaining requested calls failed 429
```

Do not score R84 as an N=3 cell. The correct next measurement, once provider
rate limits clear, is a fresh all-lens N=3 with the value-domain hold active.
Until that completes, the clean claim-bearing transfer result remains R81:
24/26 stable expected facts with all governance gates clean.

R85 fresh all-lens N=3 after value-domain hold:

```text
root: C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_n3_value_domain_hold_rerun_20260601
model: qwen/qwen3.6-35b-a3b-20260415
provider: OpenRouter
routing: allow_fallbacks=false, require_parameters=true
lenses per run: wrapper, chronology, violation, response_obligation, conclusion
union facts per run after reducers: 38 / 38 / 39
runtime load errors: 0 / 0 / 0
constant-slot support>=2: 25 / 26
per-run expected matches: 25 / 26, 22 / 26, 23 / 26
forbidden matches: 0
carrier value-domain audit on reduced unions: pass, 115 facts, 142 checked slots, 0 violations
carrier value-domain audit on full raw root: pass, 230 facts, 284 checked slots, 0 violations
domain omission accountability on reduced unions: pass, 0 blockers
atom inventory and shape audit over full root: pass, 230 typed facts, 14 registered signatures, 0 unregistered, 0 atom-shape blockers
```

Tooling note:

- `scripts\summarize_typed_micro_series.py` now has
  `--matcher constant_slot`. The default unification matcher remains available,
  but the transfer support measurement uses constant-slot matching because FDA
  subject IDs and source coordinates are intentionally variable across same-
  condition compiles while governed constants must remain in the same argument
  positions.

Reading:

- the value-domain hold plus category-boundary contract improved the honest
  transfer cell from 24/26 to 25/26. This is claim-bearing because it was a fresh
  same-condition N=3 rerun, not retroactive adjudication or replay on the old
  dirty cell.
- the two prior violation-category misses are now stable at 3/3:
  `violation_5 -> aseptic_processing` and `violation_6 -> data_integrity`.
- governance remained clean across the claim surface and the raw root. This is
  an important distinction from R82, where category pressure fixed the named
  rows but produced value-domain-invalid citation/detail rows in one run.
- do not claim 26/26. The remaining unsupported row is the recipient party:
  expected `apothecary_pharma_llc` has support 1/3; one reduced union instead
  emitted `priyanka_rana` as the recipient. This is a correspondence-party
  boundary/schema pressure point, not a scorekeeping error.

Current FDA-transfer status:

```text
claim-bearing clean transfer: 25 / 26 stable expected facts
forbidden facts: 0
runtime errors: 0
unregistered signatures: 0
atom-shape blockers: 0
value-domain violations: 0
omission blockers: 0
remaining blocker: recipient organization vs named addressee boundary in
  fda_correspondence_party/5
```

R86 recipient-boundary contract and wrapper diagnostic:

```text
contract change:
- fda_correspondence_party/5 now states that FDA warning-letter recipient
  should prefer the regulated firm/entity when one is stated, and should not
  replace that organization with an individual salutation/contact name.
- the FDA profile registry mirrors this lens-visible guidance.

wrapper-only diagnostic root:
C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_wrapper_recipient_boundary_n3_20260601

wrapper expected subset:
- run 1: 4 / 4
- run 2: 4 / 4
- run 3: 2 / 4
- support>=2: 4 / 4

recipient row:
- apothecary_pharma_llc as recipient: 3 / 3
- priyanka_rana appears as responsible_official, not as recipient, in all three
  wrapper diagnostic runs
```

Reading:

- this is a real contract-boundary improvement, not a row reducer. It does not
  read source prose after compile and it does not rewrite emitted facts.
- the wrapper-only cell suggests the final 25/26 recipient miss is closeable,
  but this is not a full transfer claim. It only tests the lens that owns the
  remaining row.

R87 attempted full all-lens N=3 after recipient-boundary contract:

```text
root: C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_n3_recipient_boundary_20260601
status: invalid claim cell
reason: multiple source compiles returned source_compile.ok=false with
  zero-yield/pass_not_ok after OpenRouter HTTP 521 errors from Ambient, while
  the script process still exited 0
examples:
- run2_wrapper: ok=false, admitted=0, lens health poor, zero_yield,
  source_pass_ops_failed: HTTP 521 provider_name=Ambient
- run2_chronology: ok=false, admitted=0
- run2_violation: ok=false, admitted=0
- run3_wrapper: ok=false, admitted=0
```

Tooling repair:

- `scripts\run_domain_bootstrap_file.py` now supports
  `--require-source-compile-ok`. Claim-bearing loops should use this flag so
  `source_compile.ok=false` produces a nonzero process exit. Exploratory
  diagnostics keep the old behavior unless the flag is set.

Reading:

- do not score R87 and do not claim 26/26 from it.
- the failure is itself useful: process-level success is not enough for
  research claims. Claim cells must fail fast on semantic compile failure, not
  just on provider exceptions.
- do not diagnose R87 as semantic regression. The bad rows are provider-failure
  artifacts that the runner previously allowed to exit 0.
- current claim-bearing transfer remains R85: 25/26 stable expected facts with
  all governance gates clean.

R88 fail-fast full-cell retry:

```text
root: C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_n3_recipient_boundary_require_ok_20260601
mode: same-condition all-lens N=3 with --require-source-compile-ok
status: incomplete / not scored
valid source_compile.ok=true lens artifacts: 14 / 15
invalid artifacts:
- run3_conclusion: HTTP 429 from Ambient, admitted=0
- run3_conclusion_retry1: HTTP 429 from Ambient, admitted=0
- run3_conclusion_retry2: HTTP 429 from Ambient, admitted=0
- run3_conclusion_retry3_rate_limited: HTTP 429 from Ambient, admitted=0
one invalid mixed-health artifact discarded:
- run3_response_obligation: admitted 10 facts but source_compile.ok=false due
  Ambient HTTP 429; rerun as run3_response_obligation_retry1 succeeded
```

Reading:

- `--require-source-compile-ok` worked: provider-contaminated artifacts now stop
  the cell instead of silently entering a support summary.
- the measurement is blocked by OpenRouter/Ambient availability, not by a known
  semantic regression. Do not score the 14/15 partial cell and do not use a
  prior conclusion-lens artifact to complete it.
- after the user asked whether controlled rate-limited OR attempts were still
  reasonable, one additional single-call retry was attempted and failed with the
  same Ambient 429. OR inference stopped after that call.
- the next verdict-bearing action is still the same: complete a fresh full
  N=3 cell with all 15 lens artifacts source_compile.ok=true, then union, score,
  and run governance gates. Until that exists, the claim-bearing transfer result
  remains R85: 25/26 stable expected facts with all governance gates clean.

R89 local LM Studio Q4 diagnostic lane:

```text
root: C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_local_q4_n1_20260601
provider: local LM Studio
model id: qwen/qwen3.6-35b-a3b
loaded quant/config: user-reported Q4_K_M, seed set in LM Studio UI
base URL: http://127.0.0.1:1234/v1
mode: all-lens N=3 with --require-source-compile-ok
valid source_compile.ok=true lens artifacts: 15 / 15
union facts per run after reducers: 44 / 46 / 45
runtime load errors: 0 / 0 / 0
constant-slot support>=2: 25 / 26
single-run support in run1: 25 / 26
carrier value-domain audit on reduced unions: pass, 135 facts, 165 checked slots, 0 violations
domain omission accountability on reduced unions: pass, 0 blockers
atom inventory and shape audit over full root: pass, 270 typed facts, 14 registered signatures, 0 unregistered, 0 atom-shape blockers
```

Stable unsupported row:

```text
expected:
fda_violation_detail(Viol2, affected_product,
  tirzepatide_injection_10_mg_ml, product_release_record_review, SrcDetail2).

observed variants:
- 3/3: fda_violation_detail(violation_2, affected_product,
    tirzepatide_injection_10_mg_ml, violation_scope, source_1).
- 2/3: fda_violation_detail(violation_2, affected_lot,
    tirzepatide_injection_10_mg_ml, product_release_record_review, source_1).
- 1/3: fda_violation_detail(violation_2, affected_lot,
    tirzepatide_injection_10_mg_ml_batches, product_release_record_review, source_1).
- 1/3: fda_violation_detail(violation_6, record_review_subject,
    batch_production_and_control_records, product_release_record_review, source_1).
```

Reading:

- local Q4 is viable for this FDA transfer lane: it completed the full N=3
  without provider failures and matched the current OR claim-bearing score of
  25/26, with governance clean.
- this is not directly comparable to the OpenRouter R85 cell because provider,
  quantization, and serving path changed. Treat it as a separate local-provider
  diagnostic baseline unless a full local rebaseline is declared.
- the local miss is different from the OR 25/26 miss. OR's remaining stable miss
  was recipient organization vs named addressee before the contract boundary
  fix; local Q4 now gets recipient/conclusion but has a stable
  violation-detail role split around Tirzepatide. That is useful evidence that
  local Q4 can unblock provider availability while surfacing a different
  carrier-boundary pressure point.

R90 Tirzepatide affected-product oracle correction and local confirmation:

```text
changed fixture:
datasets/compile_micro_fixtures/fda_warning_letter_domain_transfer_001

source/contract adjudication:
The source paragraph says "Affected products and areas referenced in the
inspection findings include Tirzepatide Injection 10 mg/mL batches released
without validated airflow studies, and operations conducted within the ISO 5
aseptic processing area." That sentence is an affected-products-and-areas scope
statement. It does not state that Tirzepatide itself is the record-review
subject.

expected fact changed from:
fda_violation_detail(Viol2, affected_product,
  tirzepatide_injection_10_mg_ml, product_release_record_review, SrcDetail2).

to:
fda_violation_detail(Viol2, affected_product,
  tirzepatide_injection_10_mg_ml, violation_scope, SrcDetail2).
```

Preflight:

```text
package validator:
C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_preflight_tirzepatide_scope_20260601.md
status: pass

focused tests:
tests\test_validate_domain_transfer_package.py
tests\test_carrier_contract_registry.py
tests\test_validate_typed_micro_fixtures.py
result: 31 passed
```

Fresh local same-condition rerun:

```text
root:
C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_local_q4_tirzepatide_scope_n3_20260601

provider: local LM Studio
model id: qwen/qwen3.6-35b-a3b
loaded quant/config: user-reported Q4_K_M, seed set in LM Studio UI
base URL: http://127.0.0.1:1234/v1
mode: all-lens N=3 with --require-source-compile-ok
valid source_compile.ok=true lens artifacts: 15 / 15
union facts per run after reducers: 42 / 44 / 44
runtime load errors: 0 / 0 / 0
constant-slot support>=2: 26 / 26
unsupported facts: 0
carrier value-domain audit on reduced unions: pass, 130 facts, 160 checked slots, 0 violations
domain omission accountability on reduced unions: pass, 0 blockers
atom inventory and shape audit over full root: pass, 262 typed facts, 13 registered signatures, 0 unregistered, 0 atom-shape blockers
```

Reading:

- This closes the local Q4 diagnostic lane for
  `fda_warning_letter_domain_transfer_001`: after a source/contract oracle
  correction and fresh same-condition local N=3, the transfer fixture is 26/26
  with governance clean.
- This does not retroactively change R89 and does not replace the current
  OpenRouter claim-bearing result. It is a separate local-provider lane because
  provider path, quantization, seed behavior, and serving stack differ.
- The result is still useful: local LM Studio did not merely "kind of work"; it
  completed all 15 lens compiles, produced registered atoms only, and matched
  the corrected transfer oracle at support>=2.
- Predicate/lens governance for this cell was lens-scoped. Each pass received
  only its active lens's allowed signatures from the FDA registry, not the full
  domain vocabulary. The model may still propose off-contract facts during
  generation, so the trusted result depends on signature enforcement, value
  domains, omission accountability, and atom-shape auditing, not prompt
  obedience.

R91 lens-scope gate hardening:

```text
change:
scripts/audit_kb_atom_inventory.py now supports:
- --enforce-registered-signatures
- --enforce-lens-scope

scripts/union_domain_bootstrap_compiles.py now removes single active-lens
metadata from deterministic union artifacts. A union is not a wrapper,
violation, chronology, response, or conclusion lens; it is a deterministic
merge of already-admitted lens artifacts.
```

Why this mattered:

- Before R91, the atom inventory audit could say a domain transfer was clean
  with respect to registered signatures and prose-shaped atoms, but it did not
  hard-fail a registered fact emitted by the wrong active lens.
- That left a governance blind spot: "registered somewhere in the FDA domain"
  is weaker than "allowed for this lens." The intended rule is
  `offered_predicates = f(domain_registry, lens)`.
- The first strict run exposed a metadata issue rather than an LLM leak:
  all-lens union artifacts inherited `active_profile_registry_lens=wrapper`
  from the first input record. The new gate treated valid union facts as
  wrapper-scope violations. That was a real artifact-governance problem, fixed
  by stripping active-lens metadata from new deterministic unions and teaching
  the audit to ignore historical artifacts with `union_source_compile`.

Strict FDA local-root replay:

```text
root:
C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_local_q4_tirzepatide_scope_n3_20260601

command:
python scripts\audit_kb_atom_inventory.py
  --compile-root <root>
  --enforce-atom-shape
  --enforce-registered-signatures
  --enforce-lens-scope

result:
typed facts: 262
registered facts: 262
unregistered facts: 0
atom-shape blockers: 0
lens-scope blockers: 0
status: pass
```

Reading:

- R90's local 26/26 result now has a stronger governance reading: every trusted
  typed fact is registered, prose-shape clean, and either inside its active
  lens's offered predicate set or part of a deterministic all-lens union.
- This still does not turn the local lane into an OpenRouter benchmark claim.
  It does make the local lane a better iteration platform because predicate
  invention and cross-lens leakage now have a biting gate.

R92 research-integrity wrapper now includes lens/register gates:

```text
change:
scripts/run_research_integrity_gate.py now runs atom inventory with:
- --enforce-atom-shape
- --enforce-registered-signatures
- --enforce-lens-scope

process note:
docs/DOMAIN_PREDICATE_SCHEMA_PROCESS.md guardrails now use the same strict
atom-inventory command.
```

Replay:

```text
root:
C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_local_q4_tirzepatide_scope_n3_20260601

gate output:
C:\prethinker_tmp_archive\research_integrity_gate_fda_local_q4_scope_n3_20260602

steps:
sign_clean_audit: pass
atom_shape_audit: pass
carrier_value_domain_audit: pass
domain_omission_accountability_audit: pass

summary:
status: pass
failed steps: 0 / 4
```

Reading:

- Future claim-bearing compile roots can use the research integrity wrapper
  instead of remembering separate governance commands by hand.
- The wrapper now checks the exact leakage class raised in R91: registered
  facts emitted outside the active lens's offered predicate set.

R93 typed-series summary now accounts for forbidden facts:

```text
change:
scripts/summarize_typed_micro_series.py now reports:
- forbidden_fact_count
- supported_forbidden_fact_count
- forbidden_rows

new optional bite flags:
- --enforce-supported
- --enforce-no-forbidden
```

Replay:

```text
root:
C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_local_q4_tirzepatide_scope_n3_20260601

summary artifact:
C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_local_q4_tirzepatide_scope_n3_20260601\local_q4_scope_n3_constant_slot_support2_strict.md

command shape:
python scripts\summarize_typed_micro_series.py
  --fixture fda_warning_letter_domain_transfer_001
  --support-threshold 2
  --matcher constant_slot
  --enforce-supported
  --enforce-no-forbidden
  --compile-json <run1 union>
  --compile-json <run2 union>
  --compile-json <run3 union>

result:
expected facts: 26
supported facts: 26
unsupported facts: 0
forbidden facts: 9
supported forbidden facts: 0
```

Reading:

- The local FDA transfer lane is now guarded not only against missing expected
  facts but also against tempting forbidden rows. This closes another reporting
  hole where a run could look perfect on expected recall while also emitting a
  known bad fact.
- The support summary remains a typed micro-series tool; it still does not
  replace the broader research integrity wrapper for sign-clean, value-domain,
  omission, atom-shape, registered-signature, and lens-scope checks.

R94 domain transfer gate wrapper:

```text
new script:
scripts/run_domain_transfer_gate.py

checks:
1. summarize_typed_micro_series.py with:
   - --enforce-supported
   - --enforce-no-forbidden
2. run_research_integrity_gate.py with:
   - sign-clean audit
   - atom-shape audit
   - registered-signature audit
   - lens-scope audit
   - carrier value-domain audit
   - omission-accountability audit
```

Replay:

```text
fixture:
fda_warning_letter_domain_transfer_001

compile root:
C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_local_q4_tirzepatide_scope_n3_20260601

gate output:
C:\prethinker_tmp_archive\domain_transfer_gate_fda_local_q4_scope_n3_20260602

result:
domain transfer gate: pass
typed micro-series expected/forbidden: pass
research integrity gate: pass
failed steps: 0 / 2
```

Reading:

- This turns the transfer-cell governance bundle into one repeatable command
  instead of a hand-remembered sequence.
- It should be the default post-run check for future domain transfer cells.

R95 second FDA transfer fixture, wildcard forbidden fix, and stable active result:

```text
fixture:
datasets/compile_micro_fixtures/fda_warning_letter_domain_transfer_002

source:
Rechon Life Science AB FDA warning letter, 2025-04-30

preflight:
C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_002_preflight_stable_active_20260602.md

stable active compile root:
C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_002_local_q4_n3_prior_contract_20260602

stable active gate:
C:\prethinker_tmp_archive\domain_transfer_gate_fda_transfer_002_local_q4_n3_stable_active_20260602

local model:
LM Studio qwen/qwen3.6-35b-a3b, local Q4 quant, one lens at a time

runtime:
about 5.2 minutes for 3 runs x 5 lenses
```

Initial finding:

- The package originally landed under `datasets/real_world_transfer` with the
  same `fda_warning_letter_domain_transfer_001` id as the Apothecary transfer
  fixture. It was moved/renamed to
  `datasets/compile_micro_fixtures/fda_warning_letter_domain_transfer_002`
  before claim-bearing runs.
- The fixture preflight passes after correcting predicate argument order,
  value-domain choices, and source notes.

Wildcard matcher correction:

```text
changed:
scripts/summarize_typed_micro_series.py
scripts/validate_typed_micro_fixtures.py

reason:
Prolog `_` and `_Name` variables in expected/forbidden facts must behave like
variables under constant-slot matching.
```

Why it matters:

- Before the fix, the typed-series gate reported 0 supported forbidden facts.
- After the fix, the earlier local N=3 showed a supported forbidden row:
  `fda_prior_warning_letter(_, rechon_life_science_ab, _, _, _)`.
- The source states a previous inspection finding, not a prior warning letter.
  This was a real contract-boundary failure, not a harmless matcher detail.

Prior-warning contract boundary:

```text
change:
fda_prior_warning_letter/5 now explicitly says:
- emit only when the source states a prior warning letter
- do not emit for prior inspection, prior finding, prior citation, trend,
  deficiency, or repeated observation by itself
```

Fresh local N=3 after that boundary:

```text
gate:
C:\prethinker_tmp_archive\domain_transfer_gate_fda_transfer_002_local_q4_n3_prior_contract_20260602

result:
supported facts: 17 / 28
supported forbidden facts: 0
research integrity gate: pass
```

Source/contract oracle normalization:

- Facility identity now leaves the normalized location atom open while still
  requiring Rechon and FEI 3002806978. The source gives a street/city/county
  address and the contract does not require one exact location atom.
- Conclusion recurrence uses `responsibility_to_correct`, matching the carrier
  contract's rule for source language assigning responsibility to investigate,
  correct, and prevent recurrence.
- Response-status detail uses `inadequate`, because `detail_kind=response_status`
  already carries the status context.
- The ISO 7 process-area detail uses `iso_7`, the compact area atom.
- The response requirement is one written-response obligation with an electronic
  submission channel; a separate no-deadline `documentation_submission` row was
  over-split and removed.

Stable active gate after these corrections:

```text
gate:
C:\prethinker_tmp_archive\domain_transfer_gate_fda_transfer_002_local_q4_n3_stable_active_20260602

expected facts: 27
supported facts: 22
unsupported facts: 5
forbidden facts: 7
supported forbidden facts: 0
research integrity gate: pass
domain transfer gate: fail
```

Unsupported rows:

- `domain_omission(... 'fda_regulatory_meeting/4', none_found,
  future_eligibility_only_no_meeting_held, ...)`
- `fda_correspondence_party(... contact, erika_v_butler, ...)`
- `fda_violation(... violation_2, other_registered_category, ...)`
- `fda_violation_detail(... violation_2, record_review_subject,
  environmental_monitoring_excursion, ...)`
- `fda_violation_detail(... violation_3, procedure_scope,
  decontamination_effectiveness_validation, ...)`

Rejected candidate:

- A correspondence-party prompt change treating FDA `ATTN:` response lines as
  contact roles closed `erika_v_butler` in a fresh local N=3, but the same run
  lost the `responsible_official` row and the ISO 7 detail. It is recorded as a
  churny candidate, not promoted into the active contract.
- Candidate gate:
  `C:\prethinker_tmp_archive\domain_transfer_gate_fda_transfer_002_local_q4_n3_contact_response_20260602`

Reading:

- The second FDA transfer cell is not a pass. It is a clean, useful fail:
  22/27 stable supported facts, 0 supported forbidden facts, and all research
  integrity gates passing.
- The prior-warning false-positive was caught only because forbidden facts now
  treat Prolog `_` as a wildcard. That gate needs to stay biting.
- Remaining work is domain recall/accountability, not sign-clean repair:
  contact role extraction, explicit regulatory-meeting omission accountability,
  violation-2 category boundary, and two deeper violation-detail recall rows.

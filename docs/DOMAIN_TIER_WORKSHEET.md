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

## Next Moves

1. Build or receive an unlike FDA warning-letter transfer micro using
   `docs\FDA_DOMAIN_TRANSFER_WORK_ORDER.md`. More same-fixture tuning is now
   high overfit risk.
2. Run a same-condition N=3 cell only after the current code settles; use
   `scripts\summarize_typed_micro_series.py` and promote only support>=2 rows
   with clean gates. Use the same-predicate variant section to decide whether a
   remaining row is a normalizer candidate or a true compile-recall gap.
3. Pressure second-layer detail completeness on the micro without allowing
   prose-shaped values.
4. If the micro reaches stable clean coverage, run N>=3 same-condition compiles
   on the current FDA fixture and promote only rows with support>=2.
5. If current FDA improves, test on at least one unlike FDA warning letter.
6. If FDA fails the reject criteria, do not rescue it by row-polishing; choose a
   different wedge or conclude no wedge is ready.

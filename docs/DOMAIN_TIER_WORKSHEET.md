# Domain Tier Worksheet

Status: active lab worksheet, opened June 1, 2026. Keep this document compact.
Move detailed run logs and retired branches to `C:\prethinker_tmp_archive`
instead of letting worksheet history accumulate in `docs`.

## Current Steering Question

Can a closed domain schema produce verified Tier 1 answers over substantive
official-document content, while the general compiler remains a lower-trust
typed fallback?

The strategy is documented in:

- [Domain Tier Strategy](DOMAIN_TIER_STRATEGY.md)

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
```

Artifacts:

```text
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r1
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r2_value_domains
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r3_contract_context
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r4_datefix
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r5_omission
C:\prethinker_tmp_archive\fda_warning_letter_micro_20260601_r6_selfcheck_omission
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

Current blocker:

```text
Completeness/accountability, not signature or value-domain governance.
```

R5/R6 still miss:

- explicit `domain_omission/5` for the absent signatory;
- one missing-record detail for violation 1;
- one procedure-scope detail for violation 2;
- documentation-submission response row;
- consultant-qualification citation row;
- recurrence/responsibility conclusion row;
- a few harmless normalization choices that may need expected alternatives
  rather than code changes.

## Next Moves

1. Decide whether explicit domain omissions should be produced by base compile,
   a bounded omission follow-up pass, or a deterministic gate that forces
   abstention until a row exists.
2. Decide whether strict FDA micro expected facts need controlled alternatives
   for legitimate compact normalizations.
3. Pressure second-layer detail completeness on the micro without allowing
   prose-shaped values.
4. If the micro reaches stable clean coverage, run N>=3 same-condition compiles
   on the current FDA fixture and promote only rows with support>=2.
5. If current FDA improves, test on at least one unlike FDA warning letter.
6. If FDA fails the reject criteria, do not rescue it by row-polishing; choose a
   different wedge or conclude no wedge is ready.

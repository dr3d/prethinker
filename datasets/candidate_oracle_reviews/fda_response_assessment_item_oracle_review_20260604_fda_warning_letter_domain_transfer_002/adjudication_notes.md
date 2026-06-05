# FDA Response-Assessment Item Oracle Review Notes

Review ID: `fda_response_assessment_item_oracle_review_20260604`
Predicate: `fda_response_assessment_item/6`
Fixture: `fda_warning_letter_domain_transfer_002` (Rechon Life Science AB)

## Blindness Statement

- Reviewer was blind to model outputs: **yes**
- Reviewer read forbidden inputs: **no**
- Notes: Adjudicated from `source.md`, neutral contract value domains, registry, and the numbered-item map only.

## Overall Finding

Three source-defensible expected facts, one per numbered item that has both an explicit "Your response is inadequate" statement and an in-domain CGMP citation: violation_1 (211.113(b)), violation_2 (211.192), violation_3 (211.42(c)(10)(v)). violation_4 (211.58) is excluded: it carries no response critique and its citation is outside the closed `CgmpCitation` domain.

## Per-Item Adjudication

- **violation_1 -> cfr_21_211_113_b** (211.113(b)):
  1. Assessment present? Yes. "Your response is inadequate. Your revised procedure still allows for (b)(4) adjustments with sanitized, gloved fingertips."
  2. Attaches to violation_1 / cfr_21_211_113_b (in-domain). 
  3. AssessmentKind: `response_inadequate` (explicit verdict).
  4. Scope: `corrective_action_evaluation` — FDA evaluates the firm's revised procedure (a corrective action) and finds it still deficient.
  5. Expected.

- **violation_2 -> cfr_21_211_192** (211.192):
  1. Assessment present? Yes. "Your CAPAs to the persistent contamination ... were not robust"; "Your response is inadequate."
  2. Attaches to violation_2 / cfr_21_211_192 (in-domain).
  3. AssessmentKind: `response_inadequate`. Not `not_investigated` — that is the underlying 211.192 violation; the carrier captures FDA's assessment of the firm's response, which is the explicit "response is inadequate."
  4. Scope: `corrective_action_evaluation` (CAPAs judged not robust).
  5. Expected.

- **violation_3 -> cfr_21_211_42_c_10_v** (211.42(c)(10)(v)):
  1. Assessment present? Yes. After the decontamination-validation and sticky-residue findings: "Your response is inadequate."
  2. Attaches to violation_3 / cfr_21_211_42_c_10_v (in-domain).
  3. AssessmentKind: `response_inadequate`.
  4. Scope: `corrective_action_evaluation`.
  5. Expected.

- **violation_4 -> cfr_21_211_58** (211.58):
  1. Assessment present? No. The item states only an observed condition (peeling paint, bubbled paint, rust); no "your response is inadequate."
  2. Citation 211.58 is not in the closed `CgmpCitation` domain regardless.
  5. Abstain / forbid (double reason).

## Expected Facts

```prolog
fda_response_assessment_item(assessment_1, violation_1, cfr_21_211_113_b, response_inadequate, corrective_action_evaluation, src_item_1).
fda_response_assessment_item(assessment_2, violation_2, cfr_21_211_192, response_inadequate, corrective_action_evaluation, src_item_2).
fda_response_assessment_item(assessment_3, violation_3, cfr_21_211_42_c_10_v, response_inadequate, corrective_action_evaluation, src_item_3).
```

## Forbidden Facts

See `candidate_forbidden_facts.pl`: v4 attachment (out-of-domain citation + no critique); wrong citation on v2 (113b); underlying-violation recast (`not_investigated` on v2); prose quote in slot; organism name in slot; FEI / WL number as `ViolationId`.

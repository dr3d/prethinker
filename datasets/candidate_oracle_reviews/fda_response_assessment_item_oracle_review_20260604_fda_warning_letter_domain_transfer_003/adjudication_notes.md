# FDA Response-Assessment Item Oracle Review Notes

Review ID: `fda_response_assessment_item_oracle_review_20260604`
Predicate: `fda_response_assessment_item/6`
Fixture: `fda_warning_letter_domain_transfer_003` (Liebel-Flarsheim Company LLC)

## Blindness Statement

- Reviewer was blind to model outputs: **yes**
- Reviewer read forbidden inputs: **no**
- Notes: Adjudicated from `source.md`, neutral contract value domains, registry, and the numbered-item map only.

## Overall Finding

One source-defensible expected fact: violation_1 (211.192). violation_2 carries a genuine response critique but cannot be represented because its citation is outside the closed `CgmpCitation` domain — this is an informative carrier boundary, not a source gap.

## Per-Item Adjudication

- **violation_1 -> cfr_21_211_192** (211.192):
  1. Assessment present? Yes, twice. "Your response is inadequate. You failed to adequately investigate these excursions, and your risk assessment minimizes the potential impact to patients." and "Your response is inadequate. While sterility and endotoxin testing are critical final quality controls, they should not be the sole basis for batch release."
  2. Attaches to violation_1 / cfr_21_211_192 (in-domain).
  3. AssessmentKind: `response_inadequate` (explicit). Not `not_investigated` (that is the underlying 211.192 violation).
  4. Scope: `corrective_action_evaluation` — FDA evaluates the firm's response and risk assessment.
  5. Expected. One item only: both "response is inadequate" sentences are the same inadequacy verdict on the same numbered item, so they collapse to one `fda_response_assessment_item` row (the carrier preserves one assessment item, not one per sentence).

- **violation_2 -> cfr_21_211_42_c and cfr_21_211_63** (211.42(c) / 211.63):
  1. Assessment present? Yes. "In your response, you commit to cleanroom reconstruction by August 2026 ... Your response is inadequate. The proposed timelines are unacceptable ..."
  2. Attaches to violation_2, but the matching citations are **bare 211.42(c)** and **211.63**, neither of which is in the closed `CgmpCitation` domain (the domain has `cfr_21_211_42_c_10_iv` and `cfr_21_211_42_c_10_v`, not bare `cfr_21_211_42_c`, and no `cfr_21_211_63`).
  3/4. Would be `response_inadequate` / `corrective_action_evaluation` if representable.
  5. **Abstain.** A real assessment exists but the carrier cannot represent it without fabricating an in-domain citation. Do not emit; do not substitute a different sub-paragraph citation.

- **Consultant (cfr_21_211_34):** the "engage a consultant qualified under 211.34" passage is a recommendation, not a per-item response assessment, and 211.34 is not in the closed `CgmpCitation` domain. Abstain/forbid.

## Expected Facts

```prolog
fda_response_assessment_item(assessment_1, violation_1, cfr_21_211_192, response_inadequate, corrective_action_evaluation, src_item_1).
```

## Forbidden Facts

See `candidate_forbidden_facts.pl`: fabricating an in-domain citation for v2 (42_c_10_v / 42_c_10_iv / 63); consultant 211.34 recast; underlying-violation recast (`not_investigated` on v1); prose quote in slot; FEI / WL number as `ViolationId`.

## Missing-input / boundary note

No missing input blocks this review. One boundary worth surfacing to the carrier owner (not a defect in this review): the closed `CgmpCitation` domain omits `cfr_21_211_58`, bare `cfr_21_211_42_c`, and `cfr_21_211_63`, so genuine source-stated response critiques on those numbered items (e.g., 002/violation_4, 003/violation_2) are unrepresentable and correctly abstained. Extending the domain would be a contract change, outside this source-only review.

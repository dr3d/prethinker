# FDA Response-Assessment Item Oracle Review Notes

Review ID: `fda_response_assessment_item_oracle_review_20260604`
Predicate: `fda_response_assessment_item/6`
Fixture: `fda_warning_letter_domain_transfer_001` (Apothecary Pharma, LLC, 503B)

## Blindness Statement

- Reviewer was blind to model outputs: **yes**
- Reviewer read forbidden inputs: **no** (no `expected_facts.pl` / `forbidden_facts.pl` were read; the proposal-evidence JSON was not used to shape any decision)
- Notes: Adjudicated from `source.md`, the neutral contract value domains, the domain registry, and the numbered-item map only.

## Overall Finding

`RESULT: NO EXPECTED FACTS.` The letter lists six numbered CGMP violations as bare CFR statements with no per-item evidence or per-item response critique. The only response/corrective-action language is in Section D and is general and letter-level, plus a third-party-consultant recommendation. Neither attaches to a numbered `violation_N` with a matching in-domain CGMP citation, so the carrier must abstain. Forbidden boundaries matter more than expected facts here.

## Per-Item Adjudication

- **violation_1 -> cfr_21_211_22_d** (211.22(d) quality unit): no response assessment in source; citation also not in the closed `CgmpCitation` domain. Abstain/forbid.
- **violation_2 -> cfr_21_211_113_b** (211.113(b)): citation is in-domain, but the source states no firm-response/CAPA assessment for this item. Abstain. (Forbidden to attach the general Section-D concern here.)
- **violation_3 -> cfr_21_211_28_a** (211.28(a)): no assessment; citation not in domain. Abstain/forbid.
- **violation_4 -> cfr_21_211_42_c_10_vi** (211.42(c)(10)(vi)): no assessment; citation not in domain. Abstain/forbid.
- **violation_5 -> cfr_21_211_42_c_10_v** (211.42(c)(10)(v)): citation in-domain, but no per-item response assessment. Abstain.
- **violation_6 -> cfr_21_211_188** (211.188): no assessment; citation not in domain. Abstain/forbid.

### Section D (Corrective Actions)

"FDA remains concerned that your firm has not yet demonstrated that adequate correction has been properly implemented ... FDA strongly recommends ... a comprehensive assessment ... A third-party consultant ... should assist you." This is a general letter-level concern plus a recommendation. It is not attached to any numbered item/citation and is not an evaluation of a specific submitted corrective action, so it falls under do-not-emit ("does not attach the critique to a numbered item/citation"; "critique belongs to another carrier family").

## Expected Facts

None. See `candidate_expected_facts.pl` (RESULT: NO EXPECTED FACTS).

## Forbidden Facts

See `candidate_forbidden_facts.pl`:
- general Section-D CAPA concern recast as a per-item assessment on violation_2 / violation_5;
- consultant recommendation recast as a response assessment;
- out-of-domain citation attachments (211.22(d), 211.28(a), 211.42(c)(10)(vi), 211.188);
- prose smuggled into the source slot;
- warning-letter number used as `ViolationId`.

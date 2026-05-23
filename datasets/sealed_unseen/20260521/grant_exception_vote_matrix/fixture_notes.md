# Fixture Notes — grant_exception_vote_matrix

## What this fixture pressures

The fixture stresses a model's ability to integrate charter-rule authority, applicant eligibility (including a rule/exception surface), threshold arithmetic on votes, and a matrix-shaped applicant table with addressable rows. It also includes a corrected budget cap and an eligibility determination that flips based on a corrected interpretation of a rule.

The central pressure point is *threshold arithmetic correctness*: the 2/3 supermajority is computed against the denominator of members voting (excluding abstentions per §4.05). For APP-S26-002 the denominator is 6 (one abstention) so 2/3 is 4. For APP-S26-003 the denominator is 7 (no abstentions) so 2/3 rounds up from 4.67 to 5. For APP-S26-004 the denominator is 7 and the threshold is 5. A model that uses a fixed threshold across motions, or that uses the wrong denominator, will misclassify pass/fail outcomes.

A second pressure point is the *threshold-impossibility case*: APP-S26-004 requested $135,000, which exceeds the §3.05 hard cap of $125,000. The exception request as filed fails regardless of vote. The Committee then votes on an alternative motion at the cap. A model that ignores the threshold-impossibility and reports a vote on $135,000 will misrepresent the proceeding.

A third pressure point is the *eligibility correction*: Coppertown was initially flagged ineligible based on a literal reading of §3.06 against 501(c)(3) status date. Counsel corrected this with reference to "continuous operations" rather than "tax-status duration." The eligibility status changes after the correction.

A fourth pressure point is the *corrected budget cap*: the original cap was $400,000, the corrected cap is $450,000. Total awards ($440,000) are within the corrected cap but would have exceeded the original cap by $40,000. The model must surface the operative (corrected) cap, not the superseded one.

## Intended pressure categories

1. rule_authority — charter sections and counsel memoranda must be cited by their specific identifiers, not paraphrased into general statements.
2. vote_tally — five distinct vote tallies must be retrievable per motion, with abstention handling.
3. numeric_cap and threshold_arithmetic — supermajority denominators, rounding, and hard-cap impossibility must be computed correctly.
4. applicant_eligibility — eligibility flips on a corrected rule interpretation; geographic eligibility under §3.07(b) requires percentage threshold check.
5. corrected_current_value — original cap $400,000 is superseded by corrected cap $450,000; original eligibility flag on Coppertown is superseded by counsel opinion.
6. table_reference — five rows in the applicant matrix must remain addressable by row identifier and individually queryable.
7. rule_exception — §3.04 standard with §3.05 exception, with the §3.05 hard cap acting as a ceiling on the exception itself.
8. source_authority — counsel memoranda are advisory but contain the operative eligibility opinions; charter is the binding authority; board resolutions authorize cycle caps.

# Expected Failure Modes — grant_exception_vote_matrix

## Likely model and harness failure modes

**Fixed-threshold collapse.** A common failure is computing the §3.05 supermajority threshold once and reapplying it to every motion. The correct denominator changes per motion based on abstentions. APP-S26-002 has one abstention (denominator 6, threshold 4); APP-S26-003 and APP-S26-004 have no abstentions (denominator 7, threshold 5). A model that uses 5 as the threshold for APP-S26-002 will misclassify the motion as failed.

**Rounding direction error.** 2/3 of 7 is 4.67. The charter §4.03 rounding rule rounds UP to the next whole number. A model that rounds down (or that uses 4 as the threshold for a 7-member denominator) will misclassify APP-S26-003 as passed and APP-S26-004 as a closer call than it is.

**Voting against §4.05.** Some models will include abstentions in the denominator, producing the wrong threshold. The charter is explicit: abstentions count toward quorum but NOT toward the majority/supermajority denominator.

**Threshold-impossibility miss.** APP-S26-004 requested $135,000. The §3.05 hard cap is $125,000. A model that treats this as a simple vote on $135,000 will report a "carried" exception at $135,000, which is impossible. The model must recognize the threshold-impossibility and then report the alternative motion at $125,000.

**Eligibility-flip drift.** Coppertown's status changes from initially-flagged-ineligible to eligible after counsel opinion. A model that snapshots the early Grants-Administrator flag will report Coppertown as ineligible. The corrected status is the operative one.

**Budget-cap currency.** The original $400,000 cap is superseded by the $450,000 corrected cap. Models that report the original cap as current, or that fail to identify the $440,000 total as within (corrected) cap and over (original) cap, will fail the numeric-cap questions.

**Geographic eligibility misread.** Heatherton is in New York. A model that applies §3.07's incorporation prong rigidly will report Heatherton as ineligible. The §3.07(b) "principally serves" prong (with the 60% threshold) is the operative path; 78% Massachusetts+Vermont meets it.

**Row identifier flattening.** Five row identifiers (APP-S26-001 through APP-S26-005) must remain individually queryable. Models that paraphrase by applicant name only ("the Coppertown application") will fail row-id queries.

**Abstainer attribution error.** Two abstentions occurred, by different members, on different motions, on different bases. Drewes abstained on APP-S26-001 due to a board affiliation with Northbrook. Fairweather abstained on APP-S26-002 due to a prior professional engagement with Coppertown. Models that swap these or that report both abstentions as the same person will fail abstention-attribution queries.

**Fallback-motion conflation.** APP-S26-003's exception failed (4-3-0) and a fall-back §3.04 motion at $75,000 then carried (7-0-0). Models that conflate these into a single "vote tally" will misreport.

**Source-of-correction misattribution.** The corrected budget cap is documented in HFF-CC-2026-0416 of April 16, 2026, on the basis of Board Supplemental Allocation 2026-S-01 of April 14, 2026. The cap correction is therefore Board-originated and Counsel-confirmed; it is not a Counsel decision standing alone.

**Harness-level failure: the QA prompt may inject Counsel-memorandum language into vote-tally questions, causing the model to substitute Counsel's eligibility opinions for the actual vote results. The fixture is structured so that the §5 counsel memorandum precedes §6 votes in the document; vote tallies and counsel opinions are textually segregated.**

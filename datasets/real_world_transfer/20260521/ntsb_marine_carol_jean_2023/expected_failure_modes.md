# Expected Failure Modes — ntsb_marine_carol_jean_2023

Generically, these features are likely to be hard for any QA system reading this document:

- **Two vessels with similar mention frequency.** *Carol Jean* and *Having Faith* are both fishing vessels, both feature in nearly every event, and several details (length, captain's intent) can be confused. A question about "the captain's vessel" vs. "the vessel he was towing" requires careful disambiguation.

- **A footnote-only time-zone declaration.** The report states once, in a footnote, that "all times are eastern daylight time, and all miles are statute miles." Every subsequent time (1903, 1130, 1733, 2127, etc.) inherits that note. Answers that reproduce times without preserving the time zone, or that confuse statute miles with nautical miles elsewhere in the same document, are at risk.

- **24-hour times that look like dates.** Many specific times ("1903", "1733", "1230", "0713") look superficially like dates or year ranges; a model may try to interpret them numerically.

- **Lookalike location names.** Tybee Island, Port Royal, Valona, St. Phillips Island, Savannah, and Darien (port of registry) are all coastal places within a couple hundred miles. Confusing them is plausible.

- **A timeline that crosses multiple days with shifting state.** The vessel is variously: under tow, drifting, anchored, dragging anchor, evacuated, re-boarded, then unattended again. A question about "the current status" depends on which date is being asked about.

- **Probable cause vs. contributing factor.** The report distinguishes "probable cause" (likely flooding from an unknown source) from "contributing" (inadequate tow planning). Conflating them is a common error.

- **Negative facts that follow from non-recovery.** Because the vessel was not recovered, investigators "could not determine how or why the vessel sank." A reader who tries to extract a definitive mechanical cause from the analysis section will misstate the report.

- **The captain's reasoning is reported as his own statements, not as factual findings.** Several sentences begin "the captain stated" or "the captain told investigators." Attributing those statements as if they were NTSB findings is an attribution error.

- **Hedged language.** Words like "likely," "presumably," "approximately," "about" appear throughout (e.g., "likely sank at some point between..."). Strip-the-hedge paraphrases can overstate certainty.

- **Two distinct geographic positions used as anchors.** The vessel's "original anchoring" position, "where it was at 0713," "where the captain was evacuated," and "where the EPIRB activated" are four different points, often described in relation to one another rather than absolutely. A spatial-reasoning question is easy to mis-resolve.

- **Compact regulatory references.** "Coast Guard Authorization Act of 2010" and the "3 nautical miles beyond the baseline" criterion are specific statutory references; abbreviation or generalization loses information.

- **Compound deficiency lists.** The Coast Guard issued ten deficiencies "relating to" four named subsystems "among other items"; the captain "corrected the majority" and "planned to correct" three specific remaining deficiencies. Sorting "corrected" from "remaining" requires careful reading.

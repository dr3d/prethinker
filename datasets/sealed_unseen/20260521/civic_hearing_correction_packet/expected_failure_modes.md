# Expected Failure Modes — civic_hearing_correction_packet

## Likely model and harness failure modes

**Stale-snapshot extraction.** A model that extracts facts from the draft minutes section (§6) without integrating the correction notices (§§8, 10, 11) will report the original 4–1 tally as the current tally, will report Castelletti as having voted, and will report the appeal as untimely. The fixture is structured so that the draft minutes are presented first and at length, exactly the surface a stale-snapshot extractor will lock onto.

**Correction layering collapse.** Three correction notices exist. CORR-001 changes the tally. CORR-002 reverses the initial timeliness reading. CORR-003 affirms CORR-002 after Town Counsel opinion. A model that conflates the three or that fails to recognize CORR-002 as superseded-in-part-and-affirmed by CORR-003 may report inconsistent status or miss the operative authority.

**Quorum miscount after vote void.** Some models will infer that voiding the alternate's vote also drops the meeting below quorum. The fixture requires the model to recognize that the four remaining voters are all regular members (Persaud, Klessig, Vong, Halvorsen) and that four equals the quorum requirement.

**Speaker attribution drift.** Six public commenters spoke, three objecting and two supporting (with one of the supporters explicitly speaking to the precedent question raised by an objector). A common failure is attributing the lot-coverage-specific objection to the wrong speaker, or assigning the Beech Court / Tamarack Lane precedent argument to an objector instead of a supporter.

**Statute-vs-bylaw confusion.** The thirty-day appeal window comes from BZBA Bylaws §6.2, not from RSA 677:2 itself (which provides a twenty-day default and permits local extension). A model that cites RSA 677:2 alone as the source of the thirty-day window is misattributing the rule.

**Recusal misclassification.** Bromberg recused; he did not abstain, vote against, or absent himself. Some extractors will reduce 'recused' to 'absent' or 'abstained,' which destroys the distinction the corrected tally turns on.

**Identifier flattening.** The packet contains many compact identifiers (BZBA-PKT-2026-0411, VAR-2026-019, AP-2026-005, SR-VAR-2026-019, three CORR identifiers, the audio file id, the exhibit id, the Town Counsel opinion id). Models that paraphrase identifiers ('the variance packet,' 'the first correction') instead of returning the compact label will fail identifier-or-label-detail questions.

**Harness-level failure: the QA prompt may incorrectly inject correction text into the source-attributed-claim window, causing speakers to be credited with reading the corrected tally back. The fixture is structured so that all public comment occurs before any correction is issued, making this a detectable harness leak.**

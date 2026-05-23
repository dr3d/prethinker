# Fixture Notes — civic_hearing_correction_packet

## What this fixture pressures

The fixture stresses a model's ability to keep deterministic civic-hearing facts straight across multiple correction layers, while also distinguishing source-attributed claims (what specific named speakers said) from the procedural backbone (what was actually decided, what is currently in effect, what counts as timely).

A central pressure point is the *layered correction*: a draft minute record establishes one set of facts, a first correction notice changes the vote tally by voiding an alternate's vote on procedural grounds, and a second/third correction notice changes whether a filed appeal is timely. A naive extractor that snapshots the draft minutes will report stale tallies and stale timeliness conclusions. A correct extractor must treat the operative correction notices as superseding.

A second pressure point is *attribution discipline*: several speakers make claims (objections, supporting statements, expert recommendations), and the QA mix forces the model to keep the speakers and their specific claims paired without contaminating them with one another or with the procedural backbone.

A third pressure point is *quorum arithmetic under correction*. The required quorum is 4. The corrected vote has 4 voting regular members (Castelletti's vote voided). The model must reason that quorum is still met after the void, not assume the correction invalidates the proceeding.

## Intended pressure categories

1. source_attributed_claim/4 — keep named-speaker objections and recommendations tied to their speakers.
2. vote_tally/5 — initial vs corrected tally must both be retrievable; current value is the corrected one.
3. quorum_status/3 — quorum determination must survive an alternate-vote void.
4. event_date/2 — multiple dates (hearing, minutes adoption, correction notices, appeal filing, appeal deadline) must remain distinguishable.
5. appeal_filed/3 — filing status, timeliness determination, and the corrected timeliness determination.
6. correction_current_value — a correction record changes the current authoritative value; the prior value persists as a historical claim but is not current.
7. source_reference — statute citation (RSA 677:2) and bylaw citation (BZBA Bylaws §6.2) must remain attributable to their named sources, not conflated.
8. identifier_or_label_detail — packet, docket, correction notice, audio, exhibit, and report identifiers must remain queryable as compact identifiers.

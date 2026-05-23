# Fixture Notes — clinical_recall_source_packet

## What this fixture pressures

The fixture stresses a model's ability to handle a recall ledger with compact identifiers (lot ids, serial numbers, room ids, bulletin ids, report ids), a clear status interval per device, and a chain of source-attributed claims that diverge in their assessment of what is happening. A supersession event partway through the chain changes the current status of one lot from on-hold to released, and the model must surface the corrected status without losing the historical original.

A second pressure point is the *wrapper trap*: many of the device rows are similar in shape (serial, lot, room), and a wrapper-only extractor will collapse them into a single template instance. The QA mix forces row-by-row addressability — including a single specific serial whose room must be retrieved without falling into the wrapper summary.

A third pressure point is the *source-attribution asymmetry*: a BMET note offers an opinion about three nurse reports, including reframing a nurse's negative observation as not exclusionary. The BMET is not the operative authority for the recall (the manufacturer bulletin chain is), and the model must preserve both Trumbauer's opinion AND Indaharu's primary observation without one displacing the other.

A fourth pressure point is *quantity arithmetic across the correction*: the model must produce the correct on-hold count (9), the correct released count (5), and the correct total (14) by integrating the inventory table with the correction notice.

## Intended pressure categories

1. source_record ledger — the inventory table with 14 rows must remain row-addressable, not summary-collapsed.
2. identifier_or_label_detail — lot ids, serial numbers, room ids, bulletin ids, report ids must remain queryable as compact identifiers.
3. source_reference — bulletins (SBI-FB-2026-114 and -S1) and the internal correction notice (WAIC-CORR-2026-0411) must remain attributable as named source authorities.
4. status interval and current_state — lot 0521 transitions from on-hold (provisional) to released; lot 0312 and 0418 remain on hold; loaner deployment status must be retrievable per floor.
5. quantity_value delivery — on-hold count, released count, total inventory count, loaner counts, and nurse-report counts must be retrievable without wrapper-only rows.
6. source-owned claim vs established recall fact — Trumbauer's BMET opinion is a source claim, not a finding; Indaharu's no-anomaly observation stands as a source claim and is not superseded by Trumbauer's reframing.
7. correction_supersession — the manufacturer's supplemental bulletin supersedes the primary on lot 0521; the internal correction notice acts on the manufacturer's supersession.

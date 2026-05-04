# Copperfall Deadline Docket — Fixture Notes

## Intended Challenge: Temporal Status Ledger

This fixture tests point-in-time status queries, deadline arithmetic with tolling and stays, corrections that cascade through subsequent deadline calculations, and the difference between party stipulations and court orders.

## Key Traps
- The stay correction (Aug 5 → Aug 8) changes the remaining discovery days from 10 to 7, which cascades through the post-stay deadline, the dispositive motion deadline, and the trial-setting window
- Discovery opens on the motion-to-dismiss denial date, not the answer filing date (LR 7.2 says "whichever is later" — the denial came first, the answer came later, but discovery opened on the denial)
- Party stipulations do not extend court deadlines without a court order (the interrogatory extension is between the parties, not a court extension)
- The stay tolls deadlines but doesn't reset them — 7 days remain, not a new 120-day period
- Status transitions have specific triggers and the system must track which status was active at any given date

---

# Copperfall Deadline Docket — Expected Failure Modes

- Using the uncorrected stay start date (August 5 instead of August 8)
- Confusing discovery opening (March 18, motion denial) with answer filing (March 31)
- Treating the party stipulation on interrogatories as extending the overall discovery deadline
- Resetting the discovery clock after the stay instead of resuming with remaining days
- Using the requested 45-day extension instead of the granted 30 days
- Using the uncorrected service date (January 12 instead of January 14) for the answer deadline
- Confusing the dispositive motion deadline (30 days from discovery close) with the trial window start (45 days from motion denial)
- Failing to track that the case status was Stayed between August 8 and September 8

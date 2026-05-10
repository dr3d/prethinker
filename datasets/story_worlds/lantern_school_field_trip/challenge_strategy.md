# Challenge Strategy — Lantern School Field Trip

## Primary Attack Surface
**Group membership, absences, and "all/except" logic**: Students change groups across three days. Asking "who was in Green Group during the tide pool session" requires tracking the Day 2 reassignment AND the Station A/B split. "All students except Cosmo" is true for Day 1 afternoon but not Day 2.

## Secondary Attack Surfaces
- **Conflicting incident reports**: Freya and Brigid disagree on what Elio was reaching for, whether Dion pushed or grabbed, and who applied the bandage. Ms. Okafor explicitly cannot confirm any of these.
- **Chaperone supervision chain**: Who supervised which group changes four times across three days.
- **Identity disambiguation**: Two students named Arden in different groups.
- **Temporal group membership**: Maeve and Vera swap groups for one hour then swap back.

## Expected Failure Modes
- Listing the wrong students in a group at a specific time
- Treating Freya's account as authoritative over Brigid's (or vice versa) when neither is confirmed
- Confusing Arden Marsh (Red) with Arden Banerjee (Yellow)
- Counting 32 students for Day 1 afternoon when Cosmo was absent

# Larkspur Clockwork Fair — Fixture Notes

## Intended Challenge: Longitudinal Story World

Many entities with near-miss names (Elara Voss / Stellan Voss, Tobias Wren / Cassia Wren, Maren Blackwood / Neve Blackwood), object-state changes tracked across 10 days, multi-step causality chains, aliases, and final-state queries where the current state differs from the initial state.

## Key Traps
- Elara Voss and Stellan Voss share a surname but are NOT related — system must not create a family relationship
- Tobias Wren and Cassia Wren ARE related (grandfather/granddaughter)
- Maren Blackwood is an exhibitor; Neve Blackwood is an attendant, not an exhibitor
- The Compass Rose is never inspected, never registered, and passes through two people's hands (Maren → Cassia → Maren)
- The Gilt Salamander's state changes: gold paint → scraped foreleg → not repainted (final state has bare copper)
- The Pearlescent Loom's state changes: silver shuttle + Undyed Cotton No. 4 → Dyed Silk No. 7 substituted → temperature-chromatic function compromised → exhibited with indigo cloth
- The Bottled Storm's state changes: intact → cracked → wax-repaired → operational at closing
- The Moth Lantern's state changes: amber light → blue light modification → disqualified from judging
- The thread substitution correction (Day 1 → Day 2) matters for the timeline of who was near the stall
- Stellan was suspected then cleared — system must track the suspicion AND the clearance

---

# Larkspur Clockwork Fair — Expected Failure Modes

- Conflating Elara Voss with Stellan Voss (shared surname, no relation)
- Treating Neve as an exhibitor
- Tracking the Compass Rose's custody chain incorrectly
- Reporting the Salamander's paint as gold when the final state has a bare copper foreleg
- Reporting the Loom as temperature-chromatic when the thread substitution compromised that function
- Treating the Moth Lantern as eligible for awards when it was disqualified
- Importing training-data knowledge about real clockwork or weaving technology
- Using the uncorrected thread substitution date (Day 1 instead of Day 2)
- Resolving the thread substitution as deliberate sabotage when Harker confirms it was accidental

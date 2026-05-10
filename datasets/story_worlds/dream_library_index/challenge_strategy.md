# Challenge Strategy — The Dream Library Index
## Primary Attack Surface
**Story level and reference containment**: Three novels contain events that mirror real incidents — same book title, same volunteer name, same discrepancy count, same librarian name. The system must not promote fictional events to real-world facts, even when the overlap is specific and tempting.
## Secondary Surfaces
- **Name collision**: Real Gary Sims and fictional thief Gary. Real June Odell and fictional embezzler June.
- **Number collision**: Real 25-book discrepancy and fictional 25-book discrepancy
- **Temporal ordering**: All three novels were published before the real incidents they resemble
- **Unresolved real incidents**: The missing book and inventory discrepancy are genuinely unresolved — the novels don't explain them
## Expected Failure Modes
- Treating Novel A's sabotage as an explanation for the real pipe burst
- Treating Novel B's theft by Gary as evidence against real Gary Sims
- Treating Novel C's fabrication as evidence that Odell fabricated the discrepancy
- Confusing the fictional navigation-manual "Compass and Wheel" with the real poetry collection

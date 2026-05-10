# Challenge Strategy — The Clockmaker's Three Ledgers

## Primary Attack Surface
**Correction provenance and stale-vs-current state**: Three ledgers disagree on key facts. Marginal corrections in different inks update some entries. One correction is by an unverified hand. The system must track which correction is authoritative and which is disputed.

## Secondary Attack Surfaces
- **Source authority hierarchy**: The accounts ledger, client ledger, and parts ledger have different reliability for different fact types. The document examiner provides an expert opinion on which to trust.
- **False correction**: The unidentified third-hand correction on P-094 contradicts two other sources. The system must not promote it merely because it is the latest entry.
- **Unresolved status**: Multiple items have ambiguous current states (shipped? picked up? in shop?). The system must preserve uncertainty rather than guessing.
- **Arithmetic under dispute**: The commission calculation changes depending on which rate is correct, and the estate's obligation reverses direction.

## Expected Failure Modes
- Treating the P-094 third-hand correction as authoritative over two consistent sources
- Treating the 20% commission correction as superseding the 15% position when Aldric's own client ledger rejects it
- Asserting the Hartley chronometer has been shipped when the document only records the instruction, not the completion
- Asserting the Ansonia clock has been picked up when only completion is recorded

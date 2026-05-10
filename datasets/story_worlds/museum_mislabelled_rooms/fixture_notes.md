# Challenge Strategy — The Museum of Mislabelled Rooms

## Primary Attack Surface
**Labels vs facts**: The public-facing labels (placards, visitor guide) are the most visible text but often wrong. The authoritative sources (acquisition records, conservator reports) are buried deeper. The system must not treat the prominent text as truth.

## Secondary Surfaces
- **Authority override**: The Board rejected the curator's correction for Room 9, creating a case where the public label is knowingly wrong by institutional decision.
- **Error propagation**: The visitor guide copied placard errors, creating a consistent-but-wrong source pair.
- **Unverified species claim**: The visitor guide added a species identification that doesn't appear in any other source.
- **Correction status tracking**: Some corrections are installed, some drafted, some rejected. The current state of each placard differs.

## Expected Failure Modes
- Treating placard text as authoritative over acquisition records
- Treating the visitor guide as an independent confirmation when it copied from the placard
- Asserting the Bourne Chart is authentic when the conservator disputes it
- Treating the curator's recommendation as the current placard text when the Board rejected it
- Stating the ichthyosaur is Ichthyosaurus communis when no formal determination exists

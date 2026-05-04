# Meridian Permit Board — Fixture Notes

## Intended Challenge: Rule Activation Conflict

This fixture tests whether the system can hold multiple locally valid rule paths simultaneously without collapsing to a single answer. The core difficulty is that Application 1 (Lindqvist) has two legitimate interpretations of the REO coverage limit, each leading to a different outcome, and the Board has not yet decided between them. The system must preserve both interpretations as live possibilities.

## Key Traps

- The 2021 Board interpretation and the strict textual reading of the REO produce opposite coverage answers for the same property
- Rule 4 (grandfathering) is triggered or not triggered depending on which REO interpretation is used — a cascading dependency
- The HPO governs appearance only, but a naive system might apply HPO dimensional restrictions
- Rule 6 (conflicting overlays) classifies coverage as dimensional, but this classification is binding only for the specific application
- Application 2 (Oyelaran) has an unresolved interpretation dispute about whether a second-story addition constitutes a footprint change under Rule 4
- Near-miss names: Herrera (staff) vs Herrera (not a Board member); Chen and Nakashima are Board members who speak German in their deliberation remarks
- Correction 2 changes the lot area which changes all coverage calculations — system must use corrected figures throughout

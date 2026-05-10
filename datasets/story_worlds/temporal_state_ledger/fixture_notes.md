# temporal_state_ledger Fixture Notes

Author-reported source words: 1920.

Primary stress: rule-clock interactions across an event sequence, including
clock resets, pauses, corrected timestamps, and deadline shifts.

Secondary stress: superseded operational projections and corrected event times.

Expected hallucination: apply the original 48-hour deadline despite a later
clock reset, treat the superseded `OPS-PROJ-04-29` projection as live, or use
the uncorrected E-04 sampler-fail timestamp.

Review note: the E-04 correction from 04:45 to 03:45 is the cleanest derivation
surface. Using the uncorrected value should cascade into downstream temporal
misses rather than being treated as harmless paraphrase.

# school_trip_bus_roster_split Fixture Notes

## Author Delivery Note

Fixture 7, `school_trip_bus_roster_split`, was described by the author as
complete: source around 2,000 words with the full five-file set delivered.

## Fixture-Specific Notes

- Q38 and Q40 are paired false-conflict tests. Both look like cross-source
  conflicts on the surface but resolve consistently when the timeline is traced:
  - Q38: Whitaker's 2:33 eyewitness observation plus the 2:35 scan log means
    Lila walked with the group, then split off in the next two minutes.
  - Q40: Bus 2 count of 40 plus the scan log placing Lila at Mill Station
    identifies the same missing student from independent sources.
  A parser that flags either as contradiction is overcalling. A parser that
  misses Q38's temporal resolution may also collapse Q40 into "the records
  agree the bus count was right."
- Q17 and Q18 are paired conservation-of-count tests. Bus 1 had 38 before the
  swaps and 38 after. The meaningful change is homeroom composition, not
  cardinality. Returning "no change" for Q18 because the count is unchanged is
  a clean composition-versus-cardinality failure.
- Q22 is the role-overlap probe. Yi covers lunch tables from 12:30 to 1:28 and
  Devin during the demo from 1:30 to 2:30. These are two distinct sequential
  roles, both real. If the parser pins one role per person and drops the other,
  one of Q15 or Q22 may miss while the other lands.
- Q5, Q28, Q27, and Q37 form an inclusion-scope cluster:
  - Q5 asks total students: 79.
  - Q28 asks total adults on roster: 13, meaning 12 chaperones plus 1 nurse.
  - Q27 asks ratio excluding the nurse.
  - Q37 asks whether the nurse counts.
  Together they test whether scope qualifiers are tracked consistently.
- Q34 and Q35 test strict unresolved-state preservation. The May 1 review has
  no determination issued. If the parser softens "not determined" into "likely
  fine" or "appears adequate," log that as an unresolved-state failure.

## Self-Flagged Leakage / Hardness Decision

Source section 13 states the conclusion "within policy" and the ratio `1:6.58`
explicitly. Q27 is therefore partly a stated-conclusion lookup rather than a
pure derivation test.

Possible future choice: strip the explicit conclusion/ratio if the goal is to
force derivation from roster counts and policy ratio. No source edit has been
made yet.

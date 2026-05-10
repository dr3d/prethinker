# Anti-Leakage Manifest — Building Access Reliability Packet

## Per-question classification

| QID  | Class                  | Notes                                                            |
| ---- | ---------------------- | ---------------------------------------------------------------- |
| q001 | direct_lookup          | Header field ("Compiled").                                       |
| q002 | direct_lookup          | Header field ("Subject").                                        |
| q003 | source_address         | Section 7 ("Source Reliability Scoping").                        |
| q004 | source_address         | Section 9.2 ("Not available").                                   |
| q005 | direct_lookup          | Section 1 catalog row.                                           |
| q006 | direct_lookup          | Section 1 custodian column.                                      |
| q007 | direct_lookup          | Section 10 ("held by Corporate Security IT").                    |
| q008 | direct_lookup          | Section 10 ("supersedes the preliminary memo PRELIM-...").       |
| q009 | source_address         | Section 8.1 ("Resolved conflict: lobby entry timestamp").        |
| q010 | direct_lookup          | Section 2 ("Helix Engineering Services").                        |
| q011 | identifier_exact       | Header.                                                          |
| q012 | identifier_exact       | Section 2 / Section 3.                                           |
| q013 | identifier_exact       | Section 4 ("asset tag HLV-LAP-12891").                           |
| q014 | identifier_exact       | Section 10 ("COC-2026-04-21-12891").                             |
| q015 | identifier_exact       | Section 5.1 ("CC-2026-04-22-LOB").                               |
| q016 | identifier_exact       | Section 5.2 ("FW-CAM-2026-04-19").                               |
| q017 | derived_time           | Apply +14m48s drift correction to 21:47:26 → 22:02:14.           |
| q018 | direct_lookup          | Section 3 badge log row.                                         |
| q019 | derived_time           | 22:45:00 − 22:00:00 = 45 minutes.                                |
| q020 | direct_lookup          | Section 10 ("2026-04-20 09:14 UTC").                             |
| q021 | direct_lookup          | Section 6.1 ("approximately 22:30").                             |
| q022 | direct_lookup          | Section 2 ("contract end date 2026-04-14").                      |
| q023 | derived_count          | Count of Section 1 catalog rows = 6.                             |
| q024 | derived_count          | Distinct readers in 22:02–22:51 window = 3 (LOBBY-R1, FLR4-EL2, 4SR-D1). |
| q025 | derived_count          | SRC-04 + SRC-06 = 2.                                             |
| q026 | composition            | Section 7 "Not reliable for" column intersected with "Identity"; SRC-01, SRC-04, SRC-05, SRC-06. |
| q027 | derived_count          | Section 8.2 enumerates (a), (b), (c) = 3.                        |
| q028 | derived_count          | Section 4 table for DEV-12891 = 2 rows.                          |
| q029 | authority_boundary     | Section 2 explicit ("does not record the identity of the bearer"). |
| q030 | status                 | Section 2 explicit ("was not closed as of 2026-04-19").          |
| q031 | direct_lookup          | Section 7 reliability table, SRC-05 row.                         |
| q032 | direct_lookup          | Section 7 reliability table, SRC-05 row.                         |
| q033 | direct_lookup          | Header classification + Section 9.2 explicit.                    |
| q034 | authority_boundary     | Section 9.2 explicit ("does not assign individual responsibility"). |
| q035 | negative_existential   | Section 5.2 explicit ("does not establish").                     |
| q036 | unresolved             | Section 8.2 explicit ("does not resolve" / "preserved as unresolved"). |
| q037 | negative_existential   | Section 5.2 explicit ("no CAM-4S-12 footage of the 4SR-D1 entry"). |
| q038 | direct_lookup          | Section 7 reliability table, SRC-01 row.                         |
| q039 | supersession           | Section 10 explicit ("this packet governs").                     |
| q040 | direct_lookup          | Section 11 enumeration.                                          |

## Leakage disclosure

The following intentional leakage exists in the packet. It is disclosed
because the spec requires disclosure rather than concealment. Each leak
matches what real investigation packets actually contain — the test is
whether the helper uses the explicit prose when present, not whether it
can reconstruct it in its absence.

1. **Section 7 contains an explicit two-column reliability table**
   ("Reliable for" / "Not reliable for") for every source. This
   pre-resolves q031, q032, and q038 as direct lookups rather than
   inferences from the source descriptions in Sections 3–6. A stricter
   variant would force the helper to derive the axis pairing
   (time-vs-identity, location-vs-activity) from the source
   descriptions alone.

2. **Section 8.1 explicitly states "this conflict is resolved"** and
   Section 8.2 explicitly states "the packet does not resolve which
   scenario obtains" and "preserved as unresolved." This pre-resolves
   q036. A stricter variant would force the helper to determine
   resolved-vs-unresolved status from the source content alone.

3. **Section 5.2 explicitly states "the absence of CAM-4S-12 footage
   does not establish that no movement occurred during the window."**
   This pre-resolves q035 as a direct lookup. A stricter variant would
   omit this prose and force the helper to recognize that a recording
   gap is not evidence of absence.

4. **Section 9.2 explicitly states "the packet does not assign
   individual responsibility for the 4SR entry."** This pre-resolves
   q034. A stricter variant would force the helper to infer this from
   the packet's classification ("not a finding of misconduct") and
   distribution list.

5. **Section 10 explicitly states "this packet supersedes the
   preliminary memo PRELIM-2026-04-20-A" and "where this packet
   conflicts with PRELIM-2026-04-20-A, this packet governs."** This
   pre-resolves q039 without requiring a supersession derivation.

6. **Section 2 explicitly states "the badge log records the badge
   identifier; it does not record the identity of the bearer."** This
   pre-resolves q029 as a direct lookup. A stricter variant would
   force the helper to derive the identity-vs-bearer distinction from
   the structure of the badge log itself (no biometric column, no
   photo verification noted).

7. **Section 5.1 explicitly states the corrected wall-clock time
   ("approximately 2026-04-19 22:02:14") and the within-1-second
   match against SRC-01.** This reduces q017 from a clock-arithmetic
   derivation to a direct lookup. The leak is partially mitigated:
   the prose says "approximately" and gives the full match against
   SRC-01, so a helper that cites the corrected time but fails to
   identify the drift direction (slow → add) would still produce the
   right number for the wrong reason.

## What is not leaked

- The three scenarios in Section 8.2 are enumerated but their pairing
  with the reliability scoping in Section 7 is not. A helper asked
  why scenario (b) cannot be ruled out must reason "SRC-01 records
  badge use, not all entries; tailgating produces no badge record;
  CAM-4S-12 was offline, so no corroboration; therefore (b) is not
  excluded by the available sources." This chain is not stated.

- The composition answer for q026 (sources not reliable for identity)
  must be derived row-by-row from the Section 7 table; no list
  enumerating "the sources not reliable for identity are SRC-01,
  SRC-04, SRC-05, SRC-06" appears anywhere. Helpers that include
  SRC-02 or SRC-03 (which are about visual content and timestamps,
  not identity per se) will be wrong; the question is specifically
  about the "Not reliable for" column intersected with the identity
  axis.

- The drift-correction direction (slow → add) for SRC-03 is not
  stated in the form "add 14m48s to the camera timestamp." The
  packet states "the local clock was 14m48s slow" and gives the
  corrected time as a reconciled output. A helper that interprets
  "slow" as "subtract" will produce 21:32:38 instead of 22:02:14.

- The distinct-reader count (q024) is not stated. The helper must
  recognize that LOBBY-R1 appears twice (entry and egress) and count
  it once, not twice.

- The relation between BD-2026-04-15-J (the unclosed deactivation
  ticket) and BD-2026-04-20-EM (the expedited deactivation that
  actually closed the badge) is not enumerated. The helper must
  recognize that the badge being active during the incident is a
  consequence of the first ticket not being closed, and that the
  second ticket's existence does not retroactively change the
  2026-04-19 reads.

- The chain-of-custody record COC-2026-04-21-12891 is given as the
  custody identifier for the disk image, but the relationship between
  the disk image, the wipe (MDM-WIPE-2026-04-21-A), and the
  preservation order is implicit: the disk image was taken before the
  wipe, not after. The packet states this in passing ("preserved
  before wipe") in Section 10 but a helper that confuses preservation
  ordering will produce nonsensical custody chains.

- Whether the 4SR entry was authorized is not stated. The packet
  treats authorization as separate from access (the badge was active
  due to a process failure; the packet does not say whether the
  contract permitted post-end-date 4SR access). A helper that
  produces "the entry was unauthorized" is overreaching.

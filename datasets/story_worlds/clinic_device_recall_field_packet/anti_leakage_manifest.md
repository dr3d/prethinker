# Anti-Leakage Manifest — clinic_device_recall_field_packet

## Per-question manifest classification

| QID  | Manifest class       | Notes                                                                 |
| ---- | -------------------- | --------------------------------------------------------------------- |
| q001 | direct_lookup        | Section 1 names manufacturer.                                         |
| q002 | source_address       | Memo is structurally located.                                         |
| q003 | direct_lookup        | Defined in Section 3 abbreviation list.                               |
| q004 | direct_lookup        | Section 1 contact line.                                               |
| q005 | direct_lookup        | Section 6 quarantine log; Section 8.1 also references.                |
| q006 | source_address       | Section heading refers to "Unresolved Item".                          |
| q007 | direct_lookup        | Quoted in Section 1.                                                  |
| q008 | identifier_exact     | Procedure code in Section 1 and Section 5.                            |
| q009 | direct_lookup        | Quoted in Section 1.                                                  |
| q010 | source_address       | Section 10 (Glossary).                                                |
| q011 | identifier_exact     | Inventory table, MP-009 row.                                          |
| q012 | identifier_exact     | Inventory table, reverse lookup by serial.                            |
| q013 | identifier_exact     | Section 4 names patient ID.                                           |
| q014 | identifier_exact     | Section 2 names supersession notice ID.                               |
| q015 | identifier_exact     | Section 8.1 names seal range.                                         |
| q016 | identifier_exact     | Inventory table reverse lookup.                                       |
| q017 | identifier_exact     | Packet header.                                                        |
| q018 | derived_time         | Section 1 issue date.                                                 |
| q019 | derived_time         | Section 2 issue date.                                                 |
| q020 | direct_lookup        | Inventory table column.                                               |
| q021 | derived_time         | Comparison across two memo expirations (2026-05-01 vs 2026-04-30).    |
| q022 | derived_time         | Section 5 visit log dates.                                            |
| q023 | derived_time         | Halberg quote in Section 7.                                           |
| q024 | derived_count        | Count of inventory rows.                                              |
| q025 | derived_count        | Filtered count over Repair Verified column.                           |
| q026 | composition          | Per-clinic group count and max selection.                             |
| q027 | composition          | Range-membership count against final scope.                           |
| q028 | composition          | Filter on Status column.                                              |
| q029 | authority_boundary   | Memo signatory is the authority.                                      |
| q030 | direct_lookup        | Inventory table column.                                               |
| q031 | direct_lookup        | Inventory table column.                                               |
| q032 | authority_boundary   | Section 6 and Section 8.3 attribute release authority.                |
| q033 | custody_boundary     | Section 8.1 names key custody.                                        |
| q034 | unresolved           | Section 7 explicitly names the open question.                         |
| q035 | negative_existential | Section 5 explicitly states no NBFH visit yet.                        |
| q036 | negative_existential | Section 7 explicitly states firmware not in table.                    |
| q037 | negative_existential | Section 6 (2026-04-15 entry) states release not issued.               |
| q038 | source_reliability   | Section 7 names the missing source.                                   |
| q039 | source_reliability   | Provenance attribution to Section 3 table.                            |
| q040 | source_reliability   | Section 3 preamble + Section 9 caveat about Status reliability.       |

## Disclosed leakage (self-flagged)

The following leakage is present in `source.md` and disclosed:

1. **Glossary in Section 10 names every Status / Repair Verified value
   used in the inventory table.** This makes status-decoding questions
   (q030, q031) close to direct-lookup rather than table-inferred. This
   is a deliberate decision: the questions of interest are not "what
   does Quarantined mean" but "is Status a reliable proxy for scope"
   (q040), which the glossary cannot leak because Section 10 does not
   address scope.
2. **Section 9 explicitly discloses that Status reflects administrative
   state and may lag manufacturer scope.** This makes q040 close to
   direct-lookup. Acceptable because q040 is a calibration question; it
   is intentionally easy if the supersede lens is wired correctly and
   intentionally hard if Status is being used as a scope proxy.
3. **Section 5 explicitly states "No NBFH devices have been visited by
   manufacturer technician as of compilation date."** This is the kind
   of explicit-negative line spec warns about. Disclosed: q035 is
   easier than it would be if a reader had to infer this from absence.
4. **Section 7 explicitly identifies the missing evidence by name** —
   "the Medivolt engineering determination on firmware 4.2.1." This
   makes q034 a near-direct lookup. The instrumental purpose is to test
   that Prethinker preserves "named-missing-evidence" rather than
   resolving the question.
5. **Section 9 enumerates which sources are reproduced and which are
   referenced but not reproduced.** This is a provenance summary
   paragraph and could leak provenance answers. q038 and q039 are
   shaped to test more specific provenance moves (Section 7's
   firmware-determination claim and Section 3's table provenance) than
   what Section 9 directly answers.

## Not present (deliberate)

The following leakage shapes the spec warns against are confirmed
**absent**:

- No `source.md` paragraph stating "the count of in-scope devices is N"
  or otherwise giving worked counts. q024-q028 must be derived.
- No `source.md` paragraph stating final patient-use exception
  expiration; q021 requires comparison across the two exception entries.
- No worked deadline statements in the firmware section beyond Halberg's
  own anticipated date.
- No "the answer is..." phrasing.
- No "therefore..." paragraph linking exception authority to recall
  scope.
- No explicit statement of "MP-001 is out of final scope" or similar
  per-device scope determinations; q027 must be derived from serial
  range membership against the supersession notice.
- No statement of how many devices are at each clinic; q026 is derived.

## Leakage risk-level summary

- **Low risk** of bypass: q003, q005, q008, q011-q017, q018-q020, q030,
  q031.
- **Moderate risk** of bypass via glossary or section captioning: q010
  (defined directly in Section 10), q034 (Section 7 explicit), q035-q037
  (explicit negatives in source).
- **Low risk** but interesting if missed: q021 (requires comparison),
  q025 (requires correct token equality, not Scheduled), q027 (requires
  range arithmetic), q028 (requires filter), q040 (requires reading
  preamble caveat).

End of manifest.

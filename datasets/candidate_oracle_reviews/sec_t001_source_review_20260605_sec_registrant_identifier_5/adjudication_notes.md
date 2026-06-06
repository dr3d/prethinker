# Review Notes — SEC Transfer 001 Source-Only Review

These notes record ambiguity and schema observations. They do not change any
verdict; all ten candidates were decided on source text + predicate schema
alone, without reference to model outputs, run logs, prior scores, or the
diagnostic context files.

## Summary

- Accepted as expected: 0 of 10.
- Rejected as forbidden: 10 of 10.

Every candidate is a deliberate-looking deviation from the source/schema-correct
oracle row. The correct rows already live in `current_expected_facts.pl`
(exhibit rows with `not_stated`; `sec_registrant(Filing, servicenow_inc, ...)`),
and none of the reviewed candidates match them.

## Source anchors used

- Exhibit table (Item 9.01(d)) has two columns only: "Exhibit No." and
  "Description." No row carries "filed," "furnished," "deemed filed," or any
  incorporation/treatment language. Therefore the only schema-faithful
  exhibit role is `not_stated`.
- Registrant legal name is exactly "ServiceNow, Inc." — "ServiceNow" is one
  orthographic word.
- Commission File Number is "001-35580" (so `file_001_35580` as an identifier
  *value* is accurate).
- Line 4 of `source.md` explicitly labels
  `.../sec_material_event_ugly_003` as the **Source fixture** path. It is a
  provenance/scope identifier, not the filing's own identity.

## Two points worth flagging to the receiving agent

1. **Two distinct alias failure modes.** `service_now_inc` and `svc_now_inc`
   are both forbidden, but not for the same reason. `service_now_inc` fails
   because it splits the single word "ServiceNow" into "service_now"
   (mis-tokenization → not a faithful encoding). `svc_now_inc` fails because
   "svc" is an outright abbreviation. Both violate the
   "derived from the full legal name, no abbreviated aliases" rule in the
   `sec_registrant/4` notes, so both are forbidden in claim-bearing facts in
   favor of `servicenow_inc`.

2. **A correct value can still ride on a wrong-slot key.** Two candidates carry
   values that are individually correct but are still forbidden:
   - `sec_registrant_identifier(Filing, service_now_inc, commission_file_number, file_001_35580, ...)`
     and its `svc_now_inc` twin have the correct identifier kind and value;
     they are forbidden only because `registrant_id` is an alias.
   - `sec_exhibit(sec_material_event_ugly_003, exhibit_104, cover_page_ixbrl, not_stated, ...)`
     has the *correct* exhibit role (`not_stated`); it is forbidden only because
     the source-fixture label is placed in `filing_id` instead of
     `source_or_scope`. This is the value-axis / wrong-slot concern that the
     `current_sec_value_axis_status.md` audit theme guards against, observed
     here from source alone rather than from that report.

## Non-issues

- The exhibit `*_kind` values (`agreement`, `other_exhibit`, `cover_page_ixbrl`)
  match the source descriptions and are not the reason for any rejection.
- No `domain_omission/5` accountability row is warranted: the source contains a
  signature block (Russell S. Elmer, General Counsel, dated December 23, 2025),
  so the `missing_signature_block` trigger does not fire. (No signature-block
  candidate was under review here in any case.)

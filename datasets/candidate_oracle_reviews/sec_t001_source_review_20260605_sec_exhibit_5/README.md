# SEC Transfer 001 Source-Only Review Result

Reviewer: Claude (source-only reviewer)

Date: 2026-06-05

## Verdict Summary

| Candidate | Verdict | Source basis | Schema basis | Notes |
| --- | --- | --- | --- | --- |
| `sec_exhibit(Filing, exhibit_10_1, agreement, filed, SrcExhibit101).` | forbidden | Item 9.01(d) exhibit table lists only Exhibit No. + Description; no "filed"/"furnished" wording for any row. | `sec_exhibit/5`: use `filed` only when source says filed; else `not_stated`. | Overstates: turns unstated legal treatment into stated (rule 5). Kind `agreement` is fine. |
| `sec_exhibit(Filing, exhibit_10_2, other_exhibit, filed, SrcExhibit102).` | forbidden | Same; no exhibit-row legal treatment stated. | `sec_exhibit/5`: `not_stated` when no role stated. | Overstates treatment. Kind `other_exhibit` is fine. |
| `sec_exhibit(Filing, exhibit_104, cover_page_ixbrl, filed, SrcExhibit104).` | forbidden | Same; description is the cover-page IXBRL note, no "filed". | `sec_exhibit/5`: `not_stated` when no role stated. | Overstates treatment. Kind `cover_page_ixbrl` is fine. |
| `sec_registrant(Filing, service_now_inc, delaware, SrcRegistrant).` | forbidden | Legal name is "ServiceNow, Inc." — a single word "ServiceNow". | `sec_registrant/4`: `registrant_id` derived from full legal name, no abbreviated aliases. | `service_now` mis-tokenizes one word as two ("Service Now"); not a faithful encoding. Canonical is `servicenow_inc`. |
| `sec_registrant(Filing, svc_now_inc, delaware, SrcRegistrant).` | forbidden | Legal name is "ServiceNow, Inc." | `sec_registrant/4`: no abbreviated aliases. | `svc` is an abbreviation of "Service"; explicit alias, forbidden. |
| `sec_registrant_identifier(Filing, service_now_inc, commission_file_number, file_001_35580, SrcFileNumber).` | forbidden | Commission File Number 001-35580 is correctly stated; registrant name is "ServiceNow, Inc." | `sec_registrant_identifier/5`: must reuse the same full-legal-name-derived `registrant_id` from `sec_registrant/4`. | Identifier value is correct, but `registrant_id` is the rejected `service_now_inc` alias. |
| `sec_registrant_identifier(Filing, svc_now_inc, commission_file_number, file_001_35580, SrcFileNumber).` | forbidden | Same; file number correct, registrant name "ServiceNow, Inc." | `sec_registrant_identifier/5`: reuse canonical `registrant_id`. | `svc_now_inc` is an abbreviated alias. |
| `sec_exhibit(sec_material_event_ugly_003, exhibit_10_1, agreement, filed, SrcExhibit101).` | forbidden | `sec_material_event_ugly_003` is the labeled "Source fixture" path tail (provenance), not a filing identity stated in the 8-K. | `filing_id` is the filing's own identity; a source/scope label belongs in `source_or_scope`. Also `filed` overstates. | Two defects: fixture id used as `filing_id` (wrong slot / axis mixing) and `filed` overstate. |
| `sec_exhibit(sec_material_event_ugly_003, exhibit_10_2, other_exhibit, filed, SrcExhibit102).` | forbidden | Same fixture-id provenance label. | Same wrong-slot `filing_id`; `filed` overstates. | Two defects, as above. |
| `sec_exhibit(sec_material_event_ugly_003, exhibit_104, cover_page_ixbrl, not_stated, SrcExhibit104).` | forbidden | Same fixture-id provenance label. | Wrong-slot `filing_id`: fixture/scope label is not a valid `filing_id` atom. | Role `not_stated` is correct; rejected solely because the fixture id is misused as `filing_id`. |

## Accepted Expected Facts

```prolog
% None. No candidate fact is supported by source + schema exactly enough to be
% expected. Every candidate deviates from the source/schema-correct oracle row.
```

## Rejected Forbidden Facts

```prolog
% Exhibit-role overstatements: source states no exhibit-row legal treatment.
sec_exhibit(Filing, exhibit_10_1, agreement, filed, SrcExhibit101).
sec_exhibit(Filing, exhibit_10_2, other_exhibit, filed, SrcExhibit102).
sec_exhibit(Filing, exhibit_104, cover_page_ixbrl, filed, SrcExhibit104).

% Registrant-id aliases: not faithful encodings of "ServiceNow, Inc.".
sec_registrant(Filing, service_now_inc, delaware, SrcRegistrant).
sec_registrant(Filing, svc_now_inc, delaware, SrcRegistrant).
sec_registrant_identifier(Filing, service_now_inc, commission_file_number, file_001_35580, SrcFileNumber).
sec_registrant_identifier(Filing, svc_now_inc, commission_file_number, file_001_35580, SrcFileNumber).

% Fixture id misused as filing_id: belongs in source_or_scope only.
sec_exhibit(sec_material_event_ugly_003, exhibit_10_1, agreement, filed, SrcExhibit101).
sec_exhibit(sec_material_event_ugly_003, exhibit_10_2, other_exhibit, filed, SrcExhibit102).
sec_exhibit(sec_material_event_ugly_003, exhibit_104, cover_page_ixbrl, not_stated, SrcExhibit104).
```

## Ambiguous Or Schema Issues

No candidate's verdict depends on an unresolved schema decision; all ten resolve
on source content plus the stated predicate/registrant_id rules. See
`review_notes.md` for two points worth flagging to the receiving agent:

1. `service_now_inc` vs `svc_now_inc` are both forbidden but for slightly
   different reasons (single-word mis-tokenization vs explicit abbreviation).
2. The final candidate
   `sec_exhibit(sec_material_event_ugly_003, exhibit_104, cover_page_ixbrl, not_stated, SrcExhibit104).`
   carries the *correct* exhibit role (`not_stated`); it is forbidden only
   because the source-fixture label is placed in the `filing_id` slot rather
   than `source_or_scope`.

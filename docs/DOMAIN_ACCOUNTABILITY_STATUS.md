# Domain Accountability Status

Generated from closed domain registries and typed fixture oracles.
This report does not read source prose, QA questions, judge output, or model self-check text.

Compile-time enforcement remains the job of `scripts/audit_domain_omission_accountability.py`.
This page shows which omission contracts exist and which typed fixture oracles exercise them.

## Summary

- Domains: `3`
- Registry accountability requirements: `6`
- Requirements covered by fixture omissions: `4`
- Requirements not yet covered by fixture omissions: `2`
- Fixture omission facts: `7`
- Fixture-only omission patterns: `0`
- Status: `pass`

| Domain | Requirements | Covered | Fixture omissions | Fixture-only patterns |
| --- | ---: | ---: | ---: | ---: |
| `fda_warning_letter_v1` | 3 | 3 | 6 | 0 |
| `ntsb_investigation_v1` | 2 | 1 | 1 | 0 |
| `sec_form_8k_v1` | 1 | 0 | 0 | 0 |

## fda_warning_letter_v1

### Registry Requirements

| ID | Carrier | Kind | Reason | Fixture support |
| --- | --- | --- | --- | ---: |
| `missing_signatory_role` | `fda_correspondence_party/5` | `role_missing` | `signatory_not_stated` | 1 |
| `meeting_future_eligibility_only` | `fda_regulatory_meeting/4` | `none_found` | `future_eligibility_only_no_meeting_held` | 2 |
| `facility_fei_not_shown` | `fda_facility_identity/5` | `none_found` | `no_fei_shown_in_letter` | 3 |

### Fixture Omission Patterns

| Carrier | Kind | Reason | Count | Registry status | Fixtures |
| --- | --- | --- | ---: | --- | --- |
| `fda_correspondence_party/5` | `role_missing` | `signatory_not_stated` | 1 | `declared` | `fda_warning_letter_domain_v1` |
| `fda_facility_identity/5` | `none_found` | `no_fei_shown_in_letter` | 3 | `declared` | `fda_warning_letter_insanitary_001`, `fda_warning_letter_observation_transfer_002`, `fda_warning_letter_observation_transfer_003` |
| `fda_regulatory_meeting/4` | `none_found` | `future_eligibility_only_no_meeting_held` | 2 | `declared` | `fda_warning_letter_domain_transfer_002`, `fda_warning_letter_domain_transfer_003` |

### Accountability Read

All declared requirements have fixture coverage, and no fixture-only omission patterns are present.

## ntsb_investigation_v1

### Registry Requirements

| ID | Carrier | Kind | Reason | Fixture support |
| --- | --- | --- | --- | ---: |
| `missing_report_identifier` | `ntsb_report/5` | `role_missing` | `report_identifier_not_stated` | 0 |
| `finding_not_stated` | `ntsb_finding/5` | `none_found` | `probable_cause_or_finding_not_stated` | 1 |

### Fixture Omission Patterns

| Carrier | Kind | Reason | Count | Registry status | Fixtures |
| --- | --- | --- | ---: | --- | --- |
| `ntsb_finding/5` | `none_found` | `probable_cause_or_finding_not_stated` | 1 | `declared` | `ntsb_investigation_domain_v1` |

### Accountability Read

Uncovered registry requirements:
- `missing_report_identifier`: `ntsb_report/5` / `role_missing` / `report_identifier_not_stated`

## sec_form_8k_v1

### Registry Requirements

| ID | Carrier | Kind | Reason | Fixture support |
| --- | --- | --- | --- | ---: |
| `missing_signature_block` | `sec_signatory/5` | `role_missing` | `signature_block_not_stated` | 0 |

### Fixture Omission Patterns

_No expected `domain_omission/5` facts in associated fixtures._

### Accountability Read

Uncovered registry requirements:
- `missing_signature_block`: `sec_signatory/5` / `role_missing` / `signature_block_not_stated`

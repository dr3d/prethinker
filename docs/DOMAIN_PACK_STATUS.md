# Domain Pack Status

Generated from closed domain registries and typed micro-fixture oracles.
This report does not read source prose, QA questions, or judge outputs.

## Summary

- Domains: `5`
- Predicates: `60` (`55` domain-specific plus shared carriers)
- Lenses: `29`
- Associated fixtures: `24`
- Unassigned fixtures: `4`
- Expected facts in associated fixtures: `520`
- Forbidden facts in associated fixtures: `183`
- Schema status: `pass` (0 errors, 0 warnings)
- Status: `pass`

| Domain | Predicates | Domain-specific | Lenses | Fixtures | Expected | Forbidden |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `fda_warning_letter_v1` | 22 | 21 | 10 | 10 | 291 | 79 |
| `ntsb_investigation_v1` | 11 | 10 | 6 | 3 | 39 | 29 |
| `osha_incident_v1` | 10 | 9 | 4 | 5 | 111 | 35 |
| `sec_form_8k_v1` | 8 | 7 | 4 | 5 | 52 | 31 |
| `state_ag_settlement_v1` | 9 | 8 | 5 | 1 | 27 | 9 |

## fda_warning_letter_v1

- Registry: `datasets/domain_profiles/fda_warning_letter_v1/ontology_registry.json`
- Predicates: `22`
- Domain-specific predicates: `21`
- Lenses: `10`
- Accountability requirements: `3`

### Lenses

| Lens | Allowed signatures |
| --- | --- |
| `wrapper` | `fda_warning_letter/5`, `fda_facility_identity/5`, `fda_correspondence_party/5`, `domain_omission/5` |
| `chronology` | `fda_inspection_event/6`, `fda_form483_response/4`, `fda_prior_warning_letter/5`, `fda_regulatory_meeting/4`, `domain_omission/5` |
| `violation` | `fda_cgmp_violation_item/5`, `fda_violation/5`, `fda_violation_citation/4`, `fda_violation_detail/5`, `fda_violation_detail_slot/4`, `fda_response_assessment_item/6`, `fda_response_assessment/5`, `fda_adulteration_basis/5`, `domain_omission/5` |
| `insanitary_condition` | `fda_adulteration_basis/5`, `fda_insanitary_condition/5`, `domain_omission/5` |
| `response_obligation` | `fda_response_requirement/6`, `fda_consultant_recommendation/4`, `domain_omission/5` |
| `response_assessment` | `fda_cgmp_violation_item/5`, `fda_response_assessment_item/6`, `fda_response_documentation_gap/5`, `fda_response_investigation_gap/5`, `fda_response_assessment/5`, `domain_omission/5` |
| `response_documentation_gap` | `fda_cgmp_violation_item/5`, `fda_response_documentation_gap/5`, `fda_response_assessment/5`, `domain_omission/5` |
| `response_investigation_gap` | `fda_cgmp_violation_item/5`, `fda_response_investigation_gap/5`, `fda_response_assessment/5`, `domain_omission/5` |
| `violation_detail_slot` | `fda_cgmp_violation_item/5`, `fda_violation_detail_slot/4`, `domain_omission/5` |
| `conclusion` | `fda_conclusion_scope/4`, `domain_omission/5` |

### Fixture Oracles

| Fixture | Association | Expected | Forbidden | Expected signatures |
| --- | --- | ---: | ---: | --- |
| `fda_warning_letter_domain_transfer_001` | `fixture_id_prefix` | 26 | 9 | `fda_adulteration_basis/5`:2, `fda_conclusion_scope/4`:2, `fda_consultant_recommendation/4`:1, `fda_correspondence_party/5`:2, `fda_facility_identity/5`:1, `fda_form483_response/4`:1, `fda_inspection_event/6`:1, `fda_response_requirement/6`:1, `fda_violation/5`:6, `fda_violation_citation/4`:6, `fda_violation_detail/5`:2, `fda_warning_letter/5`:1 |
| `fda_warning_letter_domain_transfer_002` | `fixture_id_prefix` | 27 | 7 | `domain_omission/5`:1, `fda_adulteration_basis/5`:1, `fda_conclusion_scope/4`:2, `fda_correspondence_party/5`:4, `fda_facility_identity/5`:1, `fda_form483_response/4`:1, `fda_inspection_event/6`:1, `fda_response_requirement/6`:1, `fda_violation/5`:4, `fda_violation_citation/4`:4, `fda_violation_detail/5`:6, `fda_warning_letter/5`:1 |
| `fda_warning_letter_domain_transfer_003` | `fixture_id_prefix` | 26 | 10 | `domain_omission/5`:1, `fda_adulteration_basis/5`:1, `fda_conclusion_scope/4`:2, `fda_consultant_recommendation/4`:1, `fda_correspondence_party/5`:3, `fda_facility_identity/5`:1, `fda_form483_response/4`:1, `fda_inspection_event/6`:1, `fda_response_requirement/6`:1, `fda_violation/5`:2, `fda_violation_citation/4`:4, `fda_violation_detail/5`:7, `fda_warning_letter/5`:1 |
| `fda_warning_letter_domain_v1` | `fixture_id_prefix` | 22 | 6 | `domain_omission/5`:1, `fda_adulteration_basis/5`:1, `fda_conclusion_scope/4`:2, `fda_consultant_recommendation/4`:1, `fda_correspondence_party/5`:1, `fda_facility_identity/5`:1, `fda_form483_response/4`:1, `fda_inspection_event/6`:1, `fda_prior_warning_letter/5`:1, `fda_regulatory_meeting/4`:1, `fda_response_requirement/6`:1, `fda_violation/5`:2, `fda_violation_citation/4`:3, `fda_violation_detail/5`:4, `fda_warning_letter/5`:1 |
| `fda_warning_letter_em_detail_micro_v1` | `fixture_id_prefix` | 14 | 7 | `fda_adulteration_basis/5`:1, `fda_facility_identity/5`:1, `fda_form483_response/4`:1, `fda_inspection_event/6`:1, `fda_violation/5`:2, `fda_violation_citation/4`:2, `fda_violation_detail/5`:5, `fda_warning_letter/5`:1 |
| `fda_warning_letter_insanitary_001` | `fixture_id_prefix` | 33 | 10 | `domain_omission/5`:1, `fda_adulteration_basis/5`:1, `fda_cgmp_violation_item/5`:4, `fda_conclusion_scope/4`:1, `fda_consultant_recommendation/4`:1, `fda_correspondence_party/5`:3, `fda_facility_identity/5`:1, `fda_form483_response/4`:1, `fda_insanitary_condition/5`:3, `fda_inspection_event/6`:1, `fda_response_requirement/6`:1, `fda_violation/5`:4, `fda_violation_citation/4`:4, `fda_violation_detail/5`:6, `fda_warning_letter/5`:1 |
| `fda_warning_letter_insanitary_002` | `fixture_id_prefix` | 31 | 7 | `fda_adulteration_basis/5`:1, `fda_cgmp_violation_item/5`:4, `fda_conclusion_scope/4`:1, `fda_consultant_recommendation/4`:1, `fda_correspondence_party/5`:3, `fda_facility_identity/5`:1, `fda_form483_response/4`:1, `fda_insanitary_condition/5`:3, `fda_inspection_event/6`:1, `fda_response_requirement/6`:1, `fda_violation/5`:4, `fda_violation_citation/4`:4, `fda_violation_detail/5`:5, `fda_warning_letter/5`:1 |
| `fda_warning_letter_observation_transfer_001` | `fixture_id_prefix` | 31 | 8 | `fda_adulteration_basis/5`:1, `fda_cgmp_violation_item/5`:2, `fda_conclusion_scope/4`:1, `fda_correspondence_party/5`:3, `fda_facility_identity/5`:1, `fda_form483_response/4`:1, `fda_inspection_event/6`:1, `fda_regulatory_meeting/4`:1, `fda_response_assessment/5`:2, `fda_response_requirement/6`:1, `fda_violation/5`:2, `fda_violation_citation/4`:2, `fda_violation_detail/5`:6, `fda_violation_detail_slot/4`:6, `fda_warning_letter/5`:1 |
| `fda_warning_letter_observation_transfer_002` | `fixture_id_prefix` | 40 | 8 | `domain_omission/5`:1, `fda_adulteration_basis/5`:1, `fda_cgmp_violation_item/5`:4, `fda_conclusion_scope/4`:1, `fda_consultant_recommendation/4`:1, `fda_correspondence_party/5`:3, `fda_facility_identity/5`:1, `fda_form483_response/4`:1, `fda_insanitary_condition/5`:2, `fda_inspection_event/6`:1, `fda_response_assessment/5`:2, `fda_response_requirement/6`:1, `fda_violation/5`:4, `fda_violation_citation/4`:4, `fda_violation_detail/5`:6, `fda_violation_detail_slot/4`:6, `fda_warning_letter/5`:1 |
| `fda_warning_letter_observation_transfer_003` | `fixture_id_prefix` | 41 | 7 | `domain_omission/5`:1, `fda_adulteration_basis/5`:1, `fda_cgmp_violation_item/5`:4, `fda_conclusion_scope/4`:1, `fda_consultant_recommendation/4`:1, `fda_correspondence_party/5`:3, `fda_facility_identity/5`:1, `fda_form483_response/4`:1, `fda_insanitary_condition/5`:2, `fda_inspection_event/6`:1, `fda_response_assessment/5`:3, `fda_response_requirement/6`:1, `fda_violation/5`:4, `fda_violation_citation/4`:4, `fda_violation_detail/5`:6, `fda_violation_detail_slot/4`:6, `fda_warning_letter/5`:1 |

## ntsb_investigation_v1

- Registry: `datasets/domain_profiles/ntsb_investigation_v1/ontology_registry.json`
- Predicates: `11`
- Domain-specific predicates: `10`
- Lenses: `6`
- Accountability requirements: `2`

### Lenses

| Lens | Allowed signatures |
| --- | --- |
| `wrapper` | `ntsb_report/5`, `ntsb_occurrence/6`, `ntsb_occurrence_time/5`, `domain_omission/5` |
| `asset_party` | `ntsb_vehicle/6`, `ntsb_party/5`, `domain_omission/5` |
| `casualty` | `ntsb_injury_count/6`, `domain_omission/5` |
| `timeline` | `ntsb_timeline_event/6`, `ntsb_occurrence_time/5`, `ntsb_safety_action/6`, `domain_omission/5` |
| `conditions` | `ntsb_condition/5`, `domain_omission/5` |
| `findings` | `ntsb_finding/5`, `domain_omission/5` |

### Fixture Oracles

| Fixture | Association | Expected | Forbidden | Expected signatures |
| --- | --- | ---: | ---: | --- |
| `ntsb_investigation_domain_v1` | `fixture_id_prefix` | 13 | 13 | `domain_omission/5`:1, `ntsb_condition/5`:4, `ntsb_injury_count/6`:2, `ntsb_occurrence/6`:1, `ntsb_occurrence_time/5`:1, `ntsb_party/5`:1, `ntsb_report/5`:1, `ntsb_safety_action/6`:1, `ntsb_vehicle/6`:1 |
| `ntsb_investigation_report_id_omission_v1` | `manifest_domain_profile` | 1 | 1 | `domain_omission/5`:1 |
| `ntsb_investigation_transfer_surface_001` | `fixture_id_prefix` | 25 | 15 | `ntsb_condition/5`:5, `ntsb_finding/5`:2, `ntsb_injury_count/6`:3, `ntsb_occurrence/6`:1, `ntsb_occurrence_time/5`:1, `ntsb_party/5`:1, `ntsb_report/5`:1, `ntsb_safety_action/6`:3, `ntsb_timeline_event/6`:6, `ntsb_vehicle/6`:2 |

## osha_incident_v1

- Registry: `datasets/domain_profiles/osha_incident_v1/ontology_registry.json`
- Predicates: `10`
- Domain-specific predicates: `9`
- Lenses: `4`
- Accountability requirements: `2`

### Lenses

| Lens | Allowed signatures |
| --- | --- |
| `wrapper` | `osha_inspection/7`, `osha_establishment/5`, `domain_omission/5` |
| `accident` | `osha_accident/7`, `osha_injured_employee/7`, `domain_omission/5` |
| `violations` | `osha_violation_count/5`, `osha_penalty_amount/5`, `osha_violation_item/8`, `osha_violation_status/5`, `domain_omission/5` |
| `related_activity` | `osha_related_activity/5`, `domain_omission/5` |

### Fixture Oracles

| Fixture | Association | Expected | Forbidden | Expected signatures |
| --- | --- | ---: | ---: | --- |
| `osha_incident_domain_v1` | `manifest_domain_profile` | 21 | 8 | `osha_accident/7`:1, `osha_establishment/5`:1, `osha_injured_employee/7`:3, `osha_inspection/7`:1, `osha_penalty_amount/5`:5, `osha_related_activity/5`:2, `osha_violation_count/5`:4, `osha_violation_item/8`:2, `osha_violation_status/5`:2 |
| `osha_incident_inspection_id_omission_v1` | `manifest_domain_profile` | 1 | 1 | `domain_omission/5`:1 |
| `osha_incident_transfer_001` | `manifest_domain_profile` | 15 | 8 | `osha_accident/7`:1, `osha_establishment/5`:1, `osha_injured_employee/7`:1, `osha_inspection/7`:1, `osha_penalty_amount/5`:4, `osha_related_activity/5`:1, `osha_violation_count/5`:4, `osha_violation_item/8`:1, `osha_violation_status/5`:1 |
| `osha_incident_transfer_002` | `manifest_domain_profile` | 53 | 8 | `osha_accident/7`:1, `osha_establishment/5`:1, `osha_inspection/7`:1, `osha_penalty_amount/5`:8, `osha_related_activity/5`:2, `osha_violation_count/5`:8, `osha_violation_item/8`:16, `osha_violation_status/5`:16 |
| `osha_incident_transfer_003` | `manifest_domain_profile` | 21 | 10 | `domain_omission/5`:1, `osha_establishment/5`:1, `osha_inspection/7`:1, `osha_penalty_amount/5`:6, `osha_related_activity/5`:1, `osha_violation_count/5`:5, `osha_violation_item/8`:3, `osha_violation_status/5`:3 |

## sec_form_8k_v1

- Registry: `datasets/domain_profiles/sec_form_8k_v1/ontology_registry.json`
- Predicates: `8`
- Domain-specific predicates: `7`
- Lenses: `4`
- Accountability requirements: `1`

### Lenses

| Lens | Allowed signatures |
| --- | --- |
| `wrapper` | `sec_filing/6`, `sec_registrant/4`, `sec_registrant_identifier/5`, `domain_omission/5` |
| `items` | `sec_filing_item/5`, `sec_filing_item_treatment/4`, `domain_omission/5` |
| `exhibits` | `sec_exhibit/5`, `domain_omission/5` |
| `signature` | `sec_signatory/5`, `domain_omission/5` |

### Fixture Oracles

| Fixture | Association | Expected | Forbidden | Expected signatures |
| --- | --- | ---: | ---: | --- |
| `sec_form_8k_signature_omission_v1` | `manifest_domain_profile` | 1 | 1 | `domain_omission/5`:1 |
| `sec_form_8k_skeleton_transfer_001` | `manifest_domain_profile` | 13 | 8 | `sec_exhibit/5`:3, `sec_filing/6`:1, `sec_filing_item/5`:2, `sec_registrant/4`:1, `sec_registrant_identifier/5`:5, `sec_signatory/5`:1 |
| `sec_form_8k_skeleton_transfer_002` | `manifest_domain_profile` | 12 | 6 | `sec_exhibit/5`:1, `sec_filing/6`:1, `sec_filing_item/5`:2, `sec_registrant/4`:1, `sec_registrant_identifier/5`:6, `sec_signatory/5`:1 |
| `sec_form_8k_skeleton_transfer_003` | `fixture_id_prefix` | 13 | 10 | `sec_exhibit/5`:2, `sec_filing/6`:1, `sec_filing_item/5`:2, `sec_filing_item_treatment/4`:1, `sec_registrant/4`:1, `sec_registrant_identifier/5`:5, `sec_signatory/5`:1 |
| `sec_form_8k_skeleton_v1` | `manifest_domain_profile` | 13 | 6 | `sec_exhibit/5`:2, `sec_filing/6`:1, `sec_filing_item/5`:3, `sec_registrant/4`:1, `sec_registrant_identifier/5`:5, `sec_signatory/5`:1 |

## state_ag_settlement_v1

- Registry: `datasets/domain_profiles/state_ag_settlement_v1/ontology_registry.json`
- Predicates: `9`
- Domain-specific predicates: `8`
- Lenses: `5`
- Accountability requirements: `0`

### Lenses

| Lens | Allowed signatures |
| --- | --- |
| `wrapper` | `state_ag_instrument/7`, `state_ag_party/5`, `state_ag_authority_citation/4`, `domain_omission/5` |
| `chronology` | `state_ag_event/6`, `domain_omission/5` |
| `obligations` | `state_ag_obligation/7`, `state_ag_monetary_payment/7`, `state_ag_authority_citation/4`, `domain_omission/5` |
| `contacts` | `state_ag_contact_channel/7`, `domain_omission/5` |
| `signature` | `state_ag_signature/6`, `domain_omission/5` |

### Fixture Oracles

| Fixture | Association | Expected | Forbidden | Expected signatures |
| --- | --- | ---: | ---: | --- |
| `state_ag_settlement_aod_v1` | `manifest_domain_profile` | 27 | 9 | `state_ag_authority_citation/4`:4, `state_ag_contact_channel/7`:3, `state_ag_event/6`:4, `state_ag_instrument/7`:1, `state_ag_monetary_payment/7`:1, `state_ag_obligation/7`:6, `state_ag_party/5`:4, `state_ag_signature/6`:4 |

## Unassigned Typed Micro-Fixtures

These fixtures are retained, but they are not currently associated with a closed domain registry.

| Fixture | Expected | Forbidden |
| --- | ---: | ---: |
| `claim_ground_overlapping_subsets_v1` | 24 | 6 |
| `claim_ground_set_relation_v1` | 4 | 4 |
| `numbered_inventory_segments_v1` | 3 | 3 |
| `party_role_context_v1` | 2 | 2 |

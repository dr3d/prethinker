# Transition/Delta Contract TD-002 Surface Inspection

Generated: 2026-05-15

This inspection covers:

- `document_section_delta`
- `status_reason_delta`

## Summary

- Compile fixtures: `2`
- Parsed OK: `2`
- QA: `16 / 0 / 1`
- Helper rows: `0`

## Document Section Delta

Direct rows:

- `form_replaced(of_2, rf_5, rn_14).`
- `form_status(rf_5, active).`
- `field_value_snapshot(of_2, inspection_checklist_section, section_3, before).`
- `field_value_snapshot(rf_5, inspection_checklist_section, section_5, after).`
- `field_unchanged(mina_rao, applicant_name, rn_14).`
- `field_unchanged(40_credits, fee_amount, rn_14).`
- `field_absent(of_2, emergency_contact).`
- `field_absent(rf_5, emergency_contact).`

QA result: `7 / 0 / 1`.

The miss was not a compile-surface absence. The needed facts existed as two
`field_absent/2` rows. The query used `field_absent(form, emergency_contact).`
with lowercase `form`, making it an atom rather than a variable, so it returned
no rows. This is a query-surface gap for "both/all versions" absence, not a
field-delta compile gap.

## Status Reason Delta

Direct rows:

- `ticket_status(t_17, on_hold, 09_00).`
- `transition_occurred(t_17, on_hold, ready_for_scheduling, cl_22).`
- `transition_timestamp(cl_22, 14_20).`
- `transition_reason(t_17, address_proof_received).`
- `ticket_status(t_17, ready_for_scheduling, 14_20).`
- `ticket_assigned_reviewer(t_17, ola_kim).`
- `ticket_service_category(t_17, installation).`
- `payment_receipt_status(t_17, unstated).`
- `not_rejected(t_17).`

QA result: `9 / 0 / 0`.

Status/reason delta remains inside the set with zero helper rows. The only
visible weakness is that the pre-transition reason appears in the status phrase
(`on_hold for missing address proof`) rather than as a separate old-reason row.
That did not hurt QA here, but it is worth watching before promoting a formal
reason-delta contract.

## Lesson

TD-002 weakens the case for immediate compile-surface repair and strengthens
the case for query-surface handling of quantifier-like phrases:

- "both forms"
- "all versions"
- "remained absent"
- "stayed unstated"

The compiler already emitted the two absence rows. The planner failed to bind
the variable over records/forms. Do not turn this into a field-delta compile
patch yet.

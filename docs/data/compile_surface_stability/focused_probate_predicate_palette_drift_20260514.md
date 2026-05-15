# Focused Probate Predicate Palette Drift Audit

- Schema: `predicate_palette_drift_audit_v1`
- Baseline: frozen stamp probate compile
- Focused: invariant-guided flat-plus-focused compile

## Surface Families

| Surface | Frozen palette | Focused palette | Note |
| --- | --- | --- | --- |
| `item_identifier` | `item_id/2` | `asset_id/1 + asset_description/2` | Focused compile split id from description; query planner still often expects item_id/external_id style. |
| `external_identifier` | `external_id/2` | `external_reference/2` | Same semantic surface, different predicate name. |
| `title_or_contestation_status` | `title_status/2` | `title_contested_by/2` | Focused name implies party but often stores status labels. |
| `access_authorization` | `access_authorized/4` | `authorized_party/3 + access_authority_source/2` | Focused compile decomposed source basis from authorization row. |
| `court_order` | `court_order/3` | `order_id/1 + order_date/2 + order_effect/2` | Focused compile decomposed order rows; query planner must join rather than expect a packed row. |
| `chronology_event` | `chronological_event/3` | `event_occurred_before/2 + event_occurred_after/2` | Focused compile preserved ordering but lost event text/date payloads used by QA. |
| `source_claim_or_assertion` | `source_claim/3 + dispute_claim/3 + dispute_objection/3` | `assertion_recorded/3 + assertion_made_by/2 + dispute_*` | Focused compile better separates assertions, but query planning needs the new assertion surface. |

## Predicate Count Delta

| Predicate | Frozen | Focused | Delta |
| --- | ---: | ---: | ---: |
| `event_occurred_before` | 0 | 18 | 18 |
| `authorized_party` | 0 | 14 | 14 |
| `party_role` | 1 | 15 | 14 |
| `asset_id` | 0 | 13 | 13 |
| `asset_description` | 0 | 11 | 11 |
| `title_contested_by` | 0 | 10 | 10 |
| `access_authority_source` | 0 | 9 | 9 |
| `external_reference` | 0 | 8 | 8 |
| `assertion_recorded` | 0 | 7 | 7 |
| `order_date` | 0 | 5 | 5 |
| `order_effect` | 0 | 5 | 5 |
| `order_id` | 0 | 5 | 5 |
| `dispute_ground` | 0 | 4 | 4 |
| `assertion_made_by` | 0 | 3 | 3 |
| `dispute_status` | 0 | 3 | 3 |
| `dispute_subject` | 0 | 3 | 3 |
| `no_access_authority` | 0 | 3 | 3 |
| `dispute_claimant` | 0 | 2 | 2 |
| `party_counsel` | 0 | 2 | 2 |
| `event_occurred_after` | 0 | 1 | 1 |
| `evidence_status` | 1 | 0 | -1 |
| `physical_custodian` | 12 | 11 | -1 |
| `title_recorded_as` | 12 | 10 | -2 |
| `dispute_objection` | 3 | 0 | -3 |
| `court_order` | 5 | 0 | -5 |
| `source_claim` | 5 | 0 | -5 |
| `dispute_claim` | 7 | 0 | -7 |
| `external_id` | 9 | 0 | -9 |
| `item_id` | 12 | 0 | -12 |
| `title_status` | 12 | 0 | -12 |
| `access_authorized` | 17 | 0 | -17 |
| `chronological_event` | 18 | 0 | -18 |

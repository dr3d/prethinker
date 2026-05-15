# Operational Record Status Palette Inspection

Date: 2026-05-15

Scope:

- Compile root: `tmp/lens_vocab_operational_record_status_actor_content_compile_20260515`
- QA root: `tmp/lens_vocab_operational_record_status_actor_content_qa_20260515`
- Prior QA result: `44 / 1 / 3`, helper rows `0`

## Finding

The remaining operational misses are not primarily mapper-admission failures.
The relevant compiles mostly have `0` skipped rows, and the missed facts are
either not proposed in the right structural shape or are proposed under local
predicate/atom choices that the QA layer cannot reliably join.

## Failure Coordinates

| Fixture | Question | Surface | Palette Reading |
| --- | --- | --- | --- |
| `grant_review_queue` | current status of queue | `hybrid_join_gap` | Status exists as `status_at(gq_5, approved_with_revised_budget, 2026_05_10)`, but another alias `queue_gq5` carries only `approved`. This is identity/palette split, not helper need. |
| `permit_renewal_docket` | what superseded approval | `compile_surface_gap` | The source says hold notice `H-2` superseded the approval, but the compile emits `status_superseded_by(approved_subject_to_payment, pending_payment)`. The profile captured resulting status where the question needs superseding document/event. |
| `water_sample_docket` | who received sample | `hybrid_join_gap` | The source has field receipt and lab receipt. The compile treats `sample_received` as lab receipt and puts field receipt into `docket_filed`, so the role/event layer is ambiguous. |
| `water_sample_docket` | initial status | `compile_surface_gap` | The source says initial status `pending lab receipt`; the compile emits final/current status but no initial-status row. |

## Candidate/Palette Reading

Observed predicate palettes are too fixture-local for the operational status
surface:

- `grant_review_queue`: `status_at`, `status_change_event`, `closed`, `withdrawn`, `reopened`, `supersedes`
- `permit_renewal_docket`: `status_changed_at`, `status_superseded_by`, `docket_final_status`
- `water_sample_docket`: `sample_received`, `docket_action`, `docket_filed`, `docket_final_status`, `entry_supersedes`

These are not wrong predicates, but they do not give the selector a stable
status lifecycle grammar. The weak slots are:

- canonical record identity and alias binding (`GQ-5` vs `queue_gq5` vs `gq_5`);
- status phase (`initial`, `current`, `final`, point-in-time);
- event layer for repeated verbs (`field received sample` vs `lab desk logged sample as received`);
- supersession target type (`document/event that supersedes` vs `resulting status after supersession`).

## Conclusion

Do not add more broad operational guidance yet. The next operational repair
should be a profile/palette contract, not a helper and not more prompt prose:

- prefer stable lifecycle predicates such as `record_status_at/4` or equivalent
  phase-bearing rows when the profile supports them;
- require alias/equivalence rows when the same record is referred to by a
  docket id, queue id, file id, or short id;
- separate receipt/logging layers by actor, event type, object, and date;
- distinguish `superseded_by_document_or_event` from `resulting_status`.

This is the same science shape as the authority audit: direct QA can succeed
without helper rows, but the vocabulary layer still needs stricter slot
contracts before it is architecturally clean.

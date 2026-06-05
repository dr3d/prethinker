# SEC Exhibit Treatment Source-Only Review

Date: 2026-06-05

Fixture: `sec_form_8k_skeleton_v1`

Candidate:

```prolog
sec_exhibit(Filing, exhibit_10_1, agreement, incorporated_by_reference, SrcExhibit101).
```

Verdict: `forbidden`

The reviewer found that Exhibit 10.1 is source-stated as filed. The
incorporated-by-reference language is item-body legal treatment, not the
exhibit table row's exhibit-role treatment. The source-correct exhibit row
therefore remains `filed`, and the exhibit-role row with
`incorporated_by_reference` is source-rejected.

This review was source-only and blind to model outputs.

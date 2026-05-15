# Evidence Provenance Vocabulary QA Summary

- Schema: `lens_vocabulary_qa_summary_v1`
- Lens: `evidence_provenance`
- Date: `2026-05-15`
- Questions: `18`
- Reference judge: exact=`16` partial=`0` miss=`2`
- Helper rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`

## Fixture Summary

| Fixture | Questions | Exact | Partial | Miss | Helper rows | Reading |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `community_lab_notice` | 5 | 4 | 0 | 1 | 0 | Presenter slot was not preserved for one presented-to surface. |
| `craft_fair_review` | 6 | 5 | 0 | 1 | 0 | Storage location attached to the review packet rather than the note. |
| `garden_water_log` | 7 | 7 | 0 | 0 | 0 | Full evidence-provenance vocabulary transfer. |

## Lesson

The QA readout separates term transfer from slot completeness. Evidence
provenance mostly transfers to unlike prose without helpers, but a fired term
can still be shallow when it loses the actor/artifact/context slots needed by
the question.

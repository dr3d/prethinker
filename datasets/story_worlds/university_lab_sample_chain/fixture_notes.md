# university_lab_sample_chain Fixture Notes

## Author Delivery Note

Fixture 3, `university_lab_sample_chain`, was described by the author as
complete: source around 1,975 words, 40 oracle rows, and all five files in one
artifact.

## Fixture-Specific Notes

- Q19 is the cleanest timeline-isolation probe in this set. Aliquot A and
  aliquot B share a parent sample identity but have different exposure
  histories. This should catch a parser that collapses on shared sample identity
  instead of tracking aliquot-level state.
- Q39 is the "method-pass is not contamination-cleared" trap. A naive LLM may
  see system suitability QC PASS plus internal standard recovery within range
  and conclude the sample is fine. The fixture intentionally treats method
  acceptance and contamination-source attribution as orthogonal questions.
  Grade this strictly.
- Q37 to Q34 is a deliberate difficulty ladder:
  - Q37 is the easy negative existential because the notebook explicitly says
    something was not recorded.
  - Q34 is harder because the parser has to combine notebook silence with the
    supplier shipment-trace pending state.

## Withdrawn-Content Sentinel

The withdrawn April 22 quote mentions PFNA, but no QA question asks about PFNA.
If Prethinker emits a PFNA fact when answering analyte questions, log that as a
withdrawn-content contamination signal. This sentinel is noted in `strategy.md`
so the check is reproducible.

# Medical Prompt Probe

Date: 2026-04-23

This probe compares:

- the current shared semantic parser system prompt
- the same shared prompt plus a bounded medical supplement and compact UMLS concept hints

Model:

- `qwen3.5:9b`

## What Was Tested

Thirteen short medical utterances covering:

- condition normalization
- symptom normalization
- brand/generic medication normalization
- pregnancy plus medication exposure
- direct lab-event phrasing
- allergy phrasing
- vague medical shorthand that should trigger clarification and empty logic
- unresolved-pronoun medical turns that should not silently invent a patient

## Result

Measured score:

- baseline: `58 / 79`
- medical supplement: `79 / 79`
- delta: `+21`

That is a full-score result on the bounded battery, and it now includes both stronger direct grounded cases and clean empty-logic behavior on vague shorthand and unresolved-patient turns.

## What Improved Clearly

The supplement materially improved grounded medical compilation in these cases:

- `high blood pressure` -> `hypertension`
- `type 2 diabetes` -> `type_2_diabetes_mellitus`
- `Coumadin` -> `warfarin`
- `Advil` -> `ibuprofen`
- `penicillin allergy` -> `penicillin_allergy`
- `short of breath` -> `has_symptom(..., shortness_of_breath)`
- `serum creatinine was repeated` -> `underwent_lab_test(..., serum_creatinine_measurement)`
- `HbA1c climbed again after starting metformin`
  - `lab_result_rising(noah, hemoglobin_a1c).`
  - `taking(noah, metformin).`
- `stage 3 CKD ... serum creatinine was repeated`
  - `has_condition(pia, chronic_kidney_disease).`
  - `underwent_lab_test(pia, serum_creatinine_measurement).`

It also improved the safety posture of vague shorthand:

- `Mara's pressure has been high lately.` now becomes:
  - `needs_clarification=true`
  - empty logic
- `Sugar was high again, but nobody knows why.` now becomes:
  - `needs_clarification=true`
  - empty logic
- `His kidneys are a little off.` now becomes:
  - `needs_clarification=true`
  - empty logic

So the supplement is now doing two useful things at once:

- making grounded medical language sharper
- making vague medical language safer

## What Changed In The Latest Pass

Two additional changes closed the remaining gaps:

- the supplement examples were converted into template-style patterns instead of concrete named patients
- a bounded medical-profile guard now clears logic when the parse itself admits that patient identity is unresolved

That means the unresolved-pronoun medical turns in this battery now hold cleanly instead of smuggling partial facts under an open clarification.

## Interpretation

This gives us a clearer answer:

- prompt shaping absolutely matters for the medical lane
- a bounded medical wrapper is better than the general SP alone
- the best gains are now coming from a combination of:
  - UMLS concept hints
  - canonical predicate discipline
  - clarification-first guardrails

Prompt shaping remains the main driver, but the final clean result now comes from prompt shaping plus a tiny deterministic guard that treats unresolved patient identity as a hard stop.

## Recommendation

Continue, but stay disciplined.

The right next moves are:

1. keep the shared SP
2. keep the medical supplement as a separate profile layer
3. keep the medical-profile clarification guard in place
4. continue pushing clarification-aware medical turns and argument normalization inside the bounded profile

In other words:

- **yes** to bounded medical normalization and type-steering
- **yes** to clarification-aware medical memory
- **maybe** to tiny deterministic clinical checks
- **not yet** to broader clinical reasoning or open-ended medical ingestion

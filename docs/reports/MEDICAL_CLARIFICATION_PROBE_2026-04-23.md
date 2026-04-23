# Medical Clarification Probe

Date: 2026-04-23

This probe asks a narrower and more useful question than the base medical prompt probe:

**When medical language starts vague or pronoun-led, does the bounded medical supplement get materially better once the ambiguity is clarified?**

Model:

- `qwen3.5:9b`

## What Was Tested

Seven clarification-aware medical turns covering:

- vague pressure shorthand -> clarified blood pressure readings
- vague sugar shorthand -> clarified blood glucose reading
- vague kidneys shorthand -> clarified abnormal renal-function labs
- pronoun-led serum creatinine event
- pronoun-led pregnancy + warfarin
- pronoun-led shortness-of-breath symptom
- pronoun-led HbA1c + metformin

Each case was scored in two phases:

1. the initial parse before clarification
2. the final parse after the clarification answer was injected

## Result

Measured score:

- baseline: `21 / 38`
- medical supplement: `38 / 38`
- delta: `+17`

That is a strong result for a bounded lane, because it means clarification is doing real work rather than just cosmetically restating the same vague logic.

## What Improved Clearly

The supplement was clearly stronger after clarification in these cases:

- `Mara's pressure has been high lately.`
  - baseline final: `high_blood_pressure(mara).`
  - medical final: `lab_result_high(mara, blood_pressure_measurement).`

- `Sugar was high again, but nobody knows why.`
  - baseline final: `high_glucose(mara).`
  - medical final: `lab_result_high(mara, blood_glucose_measurement).`

- `His kidneys are a little off.`
  - baseline final: `abnormal_kidney_function(noah).`
  - medical final: `lab_result_abnormal(noah, renal_function_test).`

- `His serum creatinine was repeated this afternoon.`
  - baseline final: `repeated_serum_creatinine(noah).`
  - medical final: `underwent_lab_test(noah, serum_creatinine_measurement).`

- `She is pregnant and still taking Coumadin.`
  - baseline final: `pregnant(lena). taking_coumadin(lena).`
  - medical final: `pregnant(lena). taking(lena, warfarin).`

- `She has been short of breath for two days.`
  - baseline final: `short_of_breath(mara).`
  - medical final: `has_symptom(mara, shortness_of_breath).`

- `Her HbA1c climbed again even after starting metformin.`
  - baseline final: `hba1c_climb(noah).`
  - medical final:
    - `lab_result_rising(noah, hemoglobin_a1c).`
    - `taking(noah, metformin).`

## Why This Matters

This is the best sign so far that the medical lane is worth more effort.

Without clarification, the lane still has trouble on:

- vague shorthand
- unresolved patient references

With clarification, the same supplement becomes much sharper and more canonical:

- symptoms stay symptoms
- lab events stay lab events
- measurement answers do not collapse into diagnoses
- brand medications normalize correctly

That is exactly the kind of bounded power we want from a governed medical lane.

## What Closed The Remaining Gap

The final points came from treating unresolved patient identity as a hard stop in the bounded medical profile:

- if the parse itself says the patient identity is unresolved
- or admits it is leaning on an example patient
- the profile now keeps `logic_string` empty until clarification lands

That means the clarification-aware lane is now doing the full job we want on this bounded battery:

- hold cleanly before clarification
- normalize sharply after clarification

## Bottom Line

Clarification materially improves the bounded medical lane, and the pre-clarification hold is now clean on the bounded battery.

That means the right direction is:

- keep the UMLS-backed supplement bounded
- keep pushing clarification-aware medical turns
- do not overclaim broad clinical reasoning

This looks promising as:

- sharp medical normalization
- type-steered memory
- clarification-aware structured capture

It does **not** yet look like broad, safe clinical reasoning.

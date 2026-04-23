# Medical Compiler Supplement (`medical@v0`)

This supplement applies only to bounded medical compilation.

It does **not** authorize diagnosis completion, treatment advice, or broad clinical reasoning.

## Medical Priorities

1. Prefer stable concept normalization when a provided medical concept hint clearly matches the surface form.
2. Prefer a small canonical predicate palette over phrase-shaped medical predicates.
3. Distinguish conditions, symptoms, medications, allergies, and lab tests.
4. Do not infer diagnoses from vague shorthand.
5. Ask for clarification or abstain rather than hardening weak medical language into durable state.

## Using Provided Medical Concept Hints

When a medical concept hint is provided in the form:

- `<canonical_atom>: preferred='...' ; ...`

the left-hand `<canonical_atom>` is the canonical argument atom to use in emitted logic.

Use that canonical atom directly when the hint clearly matches the utterance.

Examples:

- if the hint says `warfarin: preferred='warfarin' ...`, emit `warfarin`
- if the hint says `ibuprofen: preferred='ibuprofen' ...`, emit `ibuprofen`
- if the hint says `hemoglobin_a1c: preferred='Hemoglobin A1c measurement' ...`, emit `hemoglobin_a1c`
- if the hint says `serum_creatinine_measurement: preferred='Creatinine measurement' ...`, emit `serum_creatinine_measurement`

## Canonical Medical Predicate Palette

When semantically compatible, prefer these predicates:

- `has_condition(Person, Condition).`
- `has_symptom(Person, Symptom).`
- `taking(Person, Medication).`
- `has_allergy(Person, AllergyOrSubstance).`
- `underwent_lab_test(Person, LabTest).`
- `lab_result_high(Person, LabTest).`
- `lab_result_rising(Person, LabTest).`
- `lab_result_abnormal(Person, LabTest).`
- `pregnant(Person).`

Argument discipline:

- `taking(Person, Medication)` means person first, medication second
- `has_condition(Person, Condition)` means person first, condition second
- `has_symptom(Person, Symptom)` means person first, symptom second
- `has_allergy(Person, AllergyOrSubstance)` means person first, allergy second
- `underwent_lab_test(Person, LabTest)` means person first, test second
- `lab_result_high(Person, LabTest)` means person first, test second
- `lab_result_rising(Person, LabTest)` means person first, test second
- `lab_result_abnormal(Person, LabTest)` means person first, test second

Do not create phrase predicates like:

- `taking_coumadin(Person).`
- `hba1c_climbed_again(Person, Medication).`
- `ckd_stage_3_on_chart().`
- `sodium_creatinine_repeated_this_afternoon().`

Prefer canonical concept atoms in arguments instead.

Names and atoms shown in illustrative examples below are templates only.

- They are **not** discourse context.
- They are **not** eligible patient identities for the current utterance.
- Only names explicitly present in the current utterance or clarification answer may appear as patient atoms.

## Micro-Patterns

- pregnancy + medication
  - `pregnant(<person>).`
  - `taking(<person>, warfarin).`

- HbA1c climbed after starting metformin
  - `lab_result_rising(<person>, hemoglobin_a1c).`
  - `taking(<person>, metformin).`

- stage 3 CKD plus repeated serum creatinine
  - `has_condition(<person>, chronic_kidney_disease).`
  - `underwent_lab_test(<person>, serum_creatinine_measurement).`

- repeated serum creatinine
  - `underwent_lab_test(<person>, serum_creatinine_measurement).`

- short of breath
  - `has_symptom(<person>, shortness_of_breath).`

- penicillin allergy
  - `has_allergy(<person>, penicillin_allergy).`

- clarified blood pressure readings high
  - `lab_result_high(<person>, blood_pressure_measurement).`

- clarified blood glucose reading high
  - `lab_result_high(<person>, blood_glucose_measurement).`

- clarified kidney function labs abnormal
  - `lab_result_abnormal(<person>, renal_function_test).`

## Clarification-First Patterns

When the utterance is still underspecified, do not emit a best-guess medical fact.

- `Mara's pressure has been high lately.`
  - `needs_clarification=true`
  - `logic_string=""`

- `Sugar was high again, but nobody knows why.`
  - `needs_clarification=true`
  - `logic_string=""`

- `His kidneys are a little off.`
  - `needs_clarification=true`
  - `logic_string=""`

- `She is pregnant and still taking Coumadin.`
  - if `she` has no grounded antecedent:
    - `needs_clarification=true`
    - `logic_string=""`

- `Her HbA1c climbed again even after starting metformin.`
  - if `her` has no grounded antecedent:
    - `needs_clarification=true`
    - `logic_string=""`

## Medical Interpretation Rules

- If a surface form clearly matches a provided concept hint, normalize to that concept atom.
- Brand medication names should normalize to the canonical medication concept when the hint supports it.
- Lab wording should normally map to a lab test or lab result predicate, not to a disease predicate.
- Allergy wording should map to `has_allergy`, not to `has_condition`, when the language is explicitly allergic history.
- Symptom wording should map to `has_symptom`, not to `has_condition`, unless the utterance explicitly states a diagnosed condition.
- If the utterance says a person *takes* or *is taking* a medication, always keep the person as the first argument and the normalized medication concept as the second argument.
- Unresolved pronouns do not justify inventing a person atom.
- If the person reference is missing or unresolved, ask for clarification and keep `logic_string` empty.
- If a clarification answer explicitly says `readings`, `labs`, `measurement`, or `test`, prefer the measurement/result interpretation over a disease interpretation.
- Do not emit placeholder patient atoms like `she`, `he`, `her`, `his`, `patient`, or `person`.
- Do not copy example names, template labels, or nearby concept-hint names into the current output unless they appear in the current utterance or clarification answer.
- Do not use names from supplement examples as antecedents for unresolved pronouns.
- Do not use names from concept hints as antecedents for unresolved pronouns.

## Vague Language Guardrails

Do not silently convert these kinds of phrases into durable diagnoses:

- `pressure has been high`
- `sugar was high`
- `kidneys are off`
- other vague shorthand without a clear disease concept in the utterance

When medical shorthand is underspecified:

- prefer `needs_clarification=true`
- keep the clarification question focused
- do not guess a disease or medication
- do not choose a nearby hinted concept just because it is available
- when the shorthand is too vague to ground safely, leave `logic_string` empty rather than emitting a guessed medical fact

Specific no-guess rules:

- `pressure has been high` does **not** justify `hypertension`
- `sugar was high` does **not** justify `hemoglobin_a1c` or diabetes
- `kidneys are off` does **not** justify `chronic_kidney_disease`
- `pressure has been high` does **not** justify `lab_result_high(...)` unless a specific test is named
- `sugar was high` does **not** justify `lab_result_high(...)` unless a specific test is named
- unresolved `she` / `her` / `his` does **not** justify choosing a patient from nearby medical concepts
- unresolved `she` / `her` / `his` does **not** justify choosing a patient from supplement examples
- unresolved `she` / `her` / `his` does **not** justify emitting `pregnant(she)` or `taking(she, warfarin)`
- unresolved `her` in a lab sentence does **not** justify copying `noah` or any other example patient into the current output

## Measurement vs Condition Guardrails

- `HbA1c climbed` is closer to a lab-result event than to a diagnosis.
- `serum creatinine was repeated` is closer to a lab-test event than to chronic kidney disease.
- `pregnant and taking warfarin` is two grounded facts, not a diagnosis recommendation.

## Safety Boundary

- Do not recommend treatment.
- Do not invent contraindications or causal claims.
- Do not infer a disease just because a related lab or symptom appears.
- Keep the output strictly at the level of grounded structured memory.

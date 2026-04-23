# Medical Profile Suite

Date: 2026-04-23

This report captures the first manifest-driven end-to-end run of the bounded `medical@v0` profile.

Model:

- `qwen3.5:9b`

Profile assets:

- [modelfiles/profile.medical.v0.json](../../modelfiles/profile.medical.v0.json)
- [modelfiles/predicate_registry.medical.json](../../modelfiles/predicate_registry.medical.json)
- [modelfiles/type_schema.medical.example.json](../../modelfiles/type_schema.medical.example.json)
- [modelfiles/medical_compiler_prompt_supplement.md](../../modelfiles/medical_compiler_prompt_supplement.md)

## Rollup

- sharp-memory: `12/12` pass, `0` warn, `0` fail
- clinical checks: `7/7` pass, `0` warn, `0` fail
- prompt probe: `79/79` vs baseline `58/79`
- clarification probe: `38/38` vs baseline `21/38`

## Why This Matters

This is the first point where the bounded medical lane can be exercised as one coherent package rather than four loosely coupled commands.

That means `medical@v0` is now more than:

- a registry file
- a prompt supplement
- a couple of probe notes

It is now a runnable bounded profile with:

- explicit ontology assets
- explicit clarification posture
- explicit probe rollup

## Interpretation

The suite now confirms a stronger story:

- the lane is good at bounded normalization and sharp memory
- clarification materially improves vague shorthand and pronoun-led medical language
- the profile now holds unresolved-patient turns cleanly before clarification instead of leaking partial logic
- the package is still not broad clinical reasoning

## Next Recommendation

The next best expansion is:

1. keep using the 27B locally for ontology prospecting and offline review
2. keep the 9B as the live bounded compiler
3. continue improving clarification and argument normalization inside `medical@v0`
4. expand only on the argument side and bounded clinical checks, not by growing the predicate palette

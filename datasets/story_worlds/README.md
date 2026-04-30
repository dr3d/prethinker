# Story-World Datasets

Curated narrative fixtures for testing Prethinker's source-fidelity, event-order,
subjective-judgment, final-state, and speech-vs-truth behavior.

These are checked-in calibration assets, not generated traces. Runtime runs,
trace HTML, bakeoff output, and local model artifacts should stay under
`tmp/`.

Current fixtures:

- `otters_clockwork_pie/`: a Goldilocks-shaped but source-local whimsical story
  designed to expose template contamination, predicate drift, chronology loss,
  and weak final-state modeling.

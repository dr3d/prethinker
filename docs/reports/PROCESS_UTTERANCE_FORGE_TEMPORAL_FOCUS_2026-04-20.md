# Process Utterance Forge

## Human Read

- This run deliberately biased the forge toward temporal and step-indexed language while keeping `Freethinker` off.
- The bias worked: temporal became the dominant pressure lane, and the harness stayed on the real `process_utterance()` path.
- Temporal is still the clearest number-two frontier behind correction handling.

### What The Temporal Sweep Says

- Temporal interesting cases: `44`
- Temporal verdicts: `33 warn`, `6 fail`, `5 pass`
- The dominant temporal shape is not pure crashiness. It is yellow behavior:
  - over-clarification on straightforward sequences
  - flattening `later moved` into same-step contradictions
  - partial capture that keeps the first state and weakens or drops the second leg
- Representative hard failures are still real:
  - `at step 11 Noor was in Harbor City and later moved to Market Hall.`
  - `at step 6 Noor was in Bay 3 and later moved to Mudroom.`
  - `at step 11 Fred was in Salem and later moved to Harbor City.`

### Practical Read

- `correction` remains the red family:
  - `39` interesting cases
  - `36` fail
- `temporal_state` is the next important family:
  - `44` interesting cases
  - `6` fail
  - `33` warn
- `query_after_write` and `pronoun_carryover` remain broad yellow families, but temporal is the sharper semantic frontier because it exposes sequence-handling limits rather than just conservative hesitation.

- generated_at_utc: `2026-04-20T12:34:40+00:00`
- episodes: `30`
- turns: `300`
- interesting_cases: `180`
- verdict_counts: `{'warn': 125, 'pass': 129, 'fail': 46}`
- status_counts: `{'success': 254, 'error': 46}`

## Top Tags

- `assert_fact`: `82`
- `temporal_state`: `68`
- `fact_assertion`: `46`
- `over-clarification`: `33`
- `success`: `32`
- `logic_error`: `28`
- `temporal_ambiguity`: `26`
- `context_update`: `24`
- `over_clarification`: `24`
- `grounded`: `24`
- `context_missing`: `24`
- `context_mismatch`: `24`

## Episodes

- episode `1`: turns=10 failures=1 warnings=3 clarifications=0
- episode `2`: turns=10 failures=0 warnings=2 clarifications=0
- episode `3`: turns=10 failures=2 warnings=5 clarifications=0
- episode `4`: turns=10 failures=1 warnings=6 clarifications=0
- episode `5`: turns=10 failures=2 warnings=2 clarifications=0
- episode `6`: turns=10 failures=1 warnings=5 clarifications=0
- episode `7`: turns=10 failures=2 warnings=5 clarifications=0
- episode `8`: turns=10 failures=1 warnings=5 clarifications=0
- episode `9`: turns=10 failures=0 warnings=6 clarifications=0
- episode `10`: turns=10 failures=1 warnings=7 clarifications=0
- episode `11`: turns=10 failures=3 warnings=1 clarifications=0
- episode `12`: turns=10 failures=3 warnings=5 clarifications=0
- episode `13`: turns=10 failures=2 warnings=2 clarifications=0
- episode `14`: turns=10 failures=2 warnings=4 clarifications=0
- episode `15`: turns=10 failures=1 warnings=3 clarifications=0
- episode `16`: turns=10 failures=1 warnings=5 clarifications=0
- episode `17`: turns=10 failures=2 warnings=5 clarifications=0
- episode `18`: turns=10 failures=3 warnings=2 clarifications=0
- episode `19`: turns=10 failures=1 warnings=5 clarifications=0
- episode `20`: turns=10 failures=1 warnings=5 clarifications=0
- episode `21`: turns=10 failures=2 warnings=1 clarifications=0
- episode `22`: turns=10 failures=1 warnings=3 clarifications=0
- episode `23`: turns=10 failures=2 warnings=6 clarifications=0
- episode `24`: turns=10 failures=4 warnings=5 clarifications=0
- episode `25`: turns=10 failures=2 warnings=5 clarifications=0
- episode `26`: turns=10 failures=0 warnings=4 clarifications=0
- episode `27`: turns=10 failures=0 warnings=5 clarifications=0
- episode `28`: turns=10 failures=2 warnings=5 clarifications=0
- episode `29`: turns=10 failures=0 warnings=5 clarifications=0
- episode `30`: turns=10 failures=3 warnings=3 clarifications=0

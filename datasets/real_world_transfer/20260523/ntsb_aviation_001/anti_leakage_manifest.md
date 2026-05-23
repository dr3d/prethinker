# Anti-Leakage Manifest

This fixture is a rough one-document pilot, not a clean benchmark batch.

## Compile Inputs

Use `source.md` or `story.md` only for compilation. The canonical `qa.md` is questions-only and removes the incoming title/header context that contained answer-bearing accident metadata.

## Scoring-Only Inputs

`oracle.jsonl` and `qa_battery.json` are scoring artifacts. They contain reference answers and supporting spans and must not be used by compile prompts, retry prompts, parser priors, or any answer-producing runtime path.

## Intake Caveats

The incoming package claimed a two-document NTSB pilot, but only `ntsb_aviation_001` was complete. The original source extraction also contains encoding artifacts such as degree symbols rendered as `??`; those are preserved in the source text for this shakedown rather than silently normalized.

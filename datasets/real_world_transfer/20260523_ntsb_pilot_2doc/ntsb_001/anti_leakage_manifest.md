# Anti-Leakage Manifest

## Compile Inputs

Use `source.md` or `story.md` only for compilation. The canonical `qa.md` is questions-only and uses the runner-compatible numbered format.

## Scoring-Only Inputs

`oracle.jsonl` and `qa_battery.json` are scoring artifacts. They contain reference answers and supporting spans and must not be used by compile prompts, retry prompts, parser priors, or answer-producing runtime paths.

## Intake Notes

The incoming package kept answers out of `qa.md`, but used `q001:` style question markers that the current QA runner does not parse. The canonical copy rewrites `qa.md` to numbered questions and preserves the incoming version as `qa_authored.md`.

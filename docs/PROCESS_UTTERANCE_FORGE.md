# Process Utterance Forge

`Process Utterance Forge` is a dynamic hammer harness for the canonical interactive entryway:

- [src/mcp_server.py](</D:/_PROJECTS/prethinker/src/mcp_server.py>) `process_utterance()`

The point is not to add infinite canned turnsets. The point is to:

- synthesize fresh user turns
- pressure the real front door
- answer clarifications when the hidden meaning supports it
- rate outcomes
- keep only interesting failures, awkward clarifications, and surprising wins

## Why This Exists

The static ladders and story packs are still useful, but they are not enough by themselves.

We also want a forge that can:

- throw weird everyday language at the GIC
- probe compound turns, pronoun carry-over, corrections, temporal language, and HN-style noise
- behave more like an irritating live user than a benchmark file
- retain signal instead of recording endless boring passes

## Current Script

- [scripts/run_process_utterance_forge.py](</D:/_PROJECTS/prethinker/scripts/run_process_utterance_forge.py>)

The first pass currently does this:

1. creates a fresh in-process `PrologMCPServer`
2. resets the KB for each episode
3. generates synthetic user turns against `process_utterance()`
4. optionally answers clarification questions
5. judges the result
6. stores only interesting cases and aggregate metrics

## Default Shape

The forge is currently aimed at the strict console/GIC path:

- compiler mode: `strict`
- compiler model: `qwen3.5:9b`
- freethinker policy: `off`

That keeps it honest with the current product path before we mix in sidecar behavior.

## Lane Profiles

The forge supports a few weighting profiles so we can stress a frontier without rewriting the harness:

- `balanced`
  Broad conversational mix across facts, carry-over, queries, temporal turns, and noise.
- `error_focus`
  Pushes harder on known brittle families like corrections, pronouns, and follow-up queries.
- `temporal_focus`
  Pushes step-indexed and relative-time sequencing such as `at step 6 ... later moved ...` so we can learn the honest `at_step(...)` envelope before touching core parser logic.

## Suggested Smoke Command

```powershell
python scripts/run_process_utterance_forge.py --episodes 2 --turns-per-episode 3
```

## Suggested Temporal Sweep

```powershell
python scripts/run_process_utterance_forge.py --episodes 30 --turns-per-episode 10 --lane-profile temporal_focus --max-interesting-cases-per-episode 8
```

## Artifact Policy

The forge should prefer:

- aggregate metrics
- top issue tags
- saved interesting cases

It should avoid becoming another giant transcript graveyard.

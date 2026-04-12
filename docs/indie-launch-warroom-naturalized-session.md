# Indie Launch War Room Session (Natural-English Rewrite)

This file preserves the interaction arc from the original launch war-room capture, but rewrites turns as realistic launch-ops chat.

- Original source URL: https://dr3d.github.io/prolog-reasoning/examples/indie-launch-warroom-session.html
- Local source snapshot: `docs/reference/indie-launch-warroom-session.source.md`
- Intent: keep deterministic dependency/risk logic while reducing tool/prolog-heavy phrasing.

## 1) Preflight

User:
"Quick pulse check: what can this setup do right now, and what are its boundaries?"

Assistant:
"Explains deterministic KB reasoning scope, supported domains, and limitations."

## 2) Reset

User:
"Start with a clean runtime board so old edits don’t leak in."

Assistant:
"Runtime state reset confirmed."

## 3) Baseline Ingestion

User:
"Set up the launch board: tasks, dependency graph, durations, supplier mappings/status, completed tasks, and milestones. Then verify that counts are all consistent."

Assistant:
"Board ingestion succeeded and all expected counts match."

## 4) Morning Standup

User:
"Give me an operator view: what is ready now, what is blocked/waiting, and current milestone risk."

Assistant:
"Reports ready tasks, waiting chains, and current milestone-risk state."

## 5) Cloud Incident

User:
"Incident update: cloud vendor is delayed. Reflect it and show propagation to blocked tasks and milestone impact. Give concise mitigations."

Assistant:
"Delay is applied and propagated through dependency graph; impact and mitigation actions are summarized."

## 6) Certification Incident

User:
"Certification risk is now delayed too. Re-evaluate launch protection priorities."

Assistant:
"Provides top launch-protection actions based on updated dependency pressure."

## 7) Clarification Intake Turn

User:
"Producer note: 'I think launch date might be June 3, but it is not locked yet.' Route this safely and explain unknown-entity errors if needed."

Assistant:
"Treats note as tentative (not a hard fact), explains safe handling, and clarifies unknown-entity behavior."

## 8) Recovery

User:
"Good news: delayed suppliers recovered and key tasks completed. Recompute ready/waiting/risk and summarize tomorrow’s board."

Assistant:
"Recovery effects applied; ready set expands, waiting chain narrows, and risk profile is updated."

## Why This Rewrite Exists

- Preserves deterministic incident/recovery logic from the original session.
- Makes turns look like real launch-ops conversation.
- Better fit for pre-thinker training on natural-language ingestion and CE-driven clarification.

## Next (War-Room Focus)

1. Add a clean natural-flow rung for this scenario.
2. Add fuzzy-language turns with hedging/typos/ellipsis.
3. Add ambiguity stress around tentative dates and supplier identity corrections.

# Hospital CPM Session (Natural-English Rewrite)

This file preserves the interaction arc from the original CPM control-room capture, but rewrites the turns as normal human operations chat.

- Original source URL: https://dr3d.github.io/prolog-reasoning/examples/hospital-cpm-playbook-session.html
- Local source snapshot: `docs/reference/hospital-cpm-playbook-session.source.md`
- Intent: keep scenario logic and turn sequence, reduce tool/prolog verbosity.

## 1) Reset

User:
"Let's start clean so no old runtime edits bleed in. Reset the board and confirm."

Assistant:
"Done. Runtime state is reset to baseline."

## 2) Baseline Board Setup (Ingestion)

User:
"Set up a hospital build CPM board. We have site prep, foundation, framing, MEP rough-in, fireproofing, enclosure glazing, roofing, interior buildout, HVAC commissioning, medical gas cert, OR fitout, imaging suite install, IT core, regulatory inspection, occupancy permit, and go-live.

Dependencies are standard critical-path style: upstream construction unlocks interior buildout; interior buildout unlocks commissioning and cert work; those unlock inspection and occupancy; go-live depends on occupancy plus final fitout/install streams.

Suppliers:
- enclosure glazing -> glass vendor
- medical gas cert -> medgas vendor
- imaging suite install -> imaging vendor

Current supplier status is on-time for all three.

Completed so far: site prep, foundation, structural frame.

Milestones: regulatory inspection, occupancy permit, go-live.

Now verify that task/dependency/supplier/completed/milestone counts are consistent."

Assistant:
"Board loaded and counts are consistent."

## 3) Baseline Ops View

User:
"Give me a morning control-room view: what's safe to start now, what's waiting on prerequisites, and whether any milestone is delayed yet."

Assistant:
"No delayed milestones yet. Early-phase tasks are ready; downstream tasks remain waiting on dependency completion."

## 4) Incident A: Glass Vendor Delay

User:
"Update: glass vendor slipped. Reflect that and show what becomes blocked and whether milestone delay appears immediately."

Assistant:
"Enclosure glazing is now blocked by glass_vendor. No milestone delay is triggered yet from this isolated disruption."

## 5) Incident B: Medgas Vendor Delay (Critical)

User:
"Now medgas vendor is delayed too. Recompute blocked tasks and milestone impact, then give top interventions to protect go-live."

Assistant:
"Medgas delay causes wider propagation: multiple blocked tasks and delayed milestones including go-live path milestones. Highest-priority intervention is immediate medgas escalation, then parallel prerequisite acceleration and contingency planning for inspection/occupancy chain."

## 6) Recovery Turn

User:
"Recovery update: glazing is back on track, and rough-in/fireproofing progress resumed. Recompute what is ready now, what is still waiting, and remaining milestone risk."

Assistant:
"Ready set expands after recovery actions. Some downstream tasks remain waiting on unresolved medgas-linked path, and milestone risk persists until that clears."

## Why This Rewrite Exists

- Keeps the same deterministic control-room logic and dependency propagation storyline.
- Makes turns look like real operations chat (what users will actually type).
- Better fit for pre-thinker training on natural-language ingestion, clarification, and routing.

## Next (Hospital CPM Focus)

1. Build a hospital-only rung pack in natural English (`reset -> ingest -> baseline -> incident -> recovery`).
2. Pair each rung with deterministic validations (facts + dependency path checks + supplier state checks).
3. Add fuzzy language variants (hedging, shorthand, typo/no-question-mark turns) after clean version passes.

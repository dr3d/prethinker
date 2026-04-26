# Demo Playbook: Talk Your Rules Into Existence

This playbook merges your 10 high-impact demos with Prethinker-native demos that highlight our governed ingestion model, clarification policy, and deterministic memory.

Last updated: 2026-04-26

Status note: this is a demo-idea bank. The current live demo surface is the
console prompt book plus semantic IR admission traces. For runnable current
operator prompts, start with [docs/CONSOLE_TRYBOOK.md](https://github.com/dr3d/prethinker/blob/main/docs/CONSOLE_TRYBOOK.md).

## Core Positioning

Prethinker is not "chat with memory." It is a **Governed Intent Compiler**:

1. Natural language is proposed as candidate facts/rules/queries.
2. Uncertainty is scored and clarification is triggered when needed.
3. Writes are confirmation-gated before KB mutation.
4. Queries are answered from deterministic symbolic state.

## The 10 Anchor Demos

| Demo | What Users Feel | Killer Query |
|---|---|---|
| Murder Wall | Detective-board inference from story clues | "Who had means, motive, and opportunity?" |
| Family History Oracle | Genealogy consistency and lineage reconstruction | "Which branches conflict on dates?" |
| Policy Stress Test Machine | Rule conflict and eligibility pressure testing | "Did any March grants violate policy?" |
| Story World Interrogator | Narrative world as queryable logic | "Who knew before chapter 12?" |
| Time-Loop Carnival | Stateful world mutation with retractions over looping rounds | "Who can reset the loop now?" |
| Meeting-to-Commitment Extractor | Semantic linting for meetings and commitments | "What commitments were actually made?" |
| Conspiracy Engine | Evidence chain reconstruction under uncertainty | "What chain links the outage to the forged permit?" |
| Constraint Playground | Plain-language constraint solving | "Find all valid seatings." |
| Business Dependency Oracle | Critical-path and blocker chain visibility | "What one fix unlocks most downstream work?" |
| Social World Simulator | Relationship-driven conflict/recusal detection | "Which committees are impossible to staff cleanly?" |
| Talk-to-Your-Rules Assistant | Conversational policy authoring with traceability | "Which rule overrode the earlier one?" |

## Prethinker-Native Additions (Merged)

These are the extra demos that show what is unique about this repo architecture.

1. Ingestion Governance Cockpit
- Shows proposed parse, uncertainty score, CE trigger, and final commit/reject state.
- Highlights: "proposal is not authority."

2. Contradiction Linter
- Feeds conflicting statements and surfaces impossible state combinations.
- Highlights: deterministic inconsistency detection.

3. Counterfactual Branch Replay
- Forks a scenario state and asks "what changes if X is removed?"
- Highlights: simulation-lite over symbolic memory.

4. Ontology Discovery Workshop
- Ingests mixed prose, identifies overloaded predicates, and suggests tighter domain schema.
- Highlights: domain hardening from language data.

## Launch Sequence (Top 3)

1. Meeting-to-Commitment Extractor
2. Policy Stress Test Machine
3. Story World Interrogator

This sequence gives immediate practical value, then shows strategic power, then gives the "magic" effect.

## Runnable Scenario Pack (Now Added)

These are executable starter scenarios in this repo:

- `kb_scenarios/demo_01_meeting_commitment_extractor.json`
- `kb_scenarios/demo_02_policy_stress_test_machine.json`
- `kb_scenarios/demo_03_story_world_interrogator.json`
- `kb_scenarios/demo_04_reimbursement_violation_check.json`
- `kb_scenarios/demo_05_time_loop_carnival.json`

Run one:

```bash
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen35-semparse:9b --runtime core --scenario kb_scenarios/demo_02_policy_stress_test_machine.json --kb-name demo_policy --out kb_runs/demo_02_policy_stress_test_machine.json
```

Render report:

```bash
python scripts/render_kb_run_html.py --input kb_runs/demo_02_policy_stress_test_machine.json --output docs/reports/demo_02_policy_stress_test_machine.html --theme standard
```

## New Demo Focus: Time-Loop Carnival

`demo_05_time_loop_carnival` stresses stateful world updates in one narrative arc:

1. establish world state (`loop_ticket`, `entered`, `has_key`)
2. ask capability query ("Who can reset the loop?")
3. mutate state with movement + explicit retraction
4. add loop-local gate state and infer derived block status
5. retract key ownership and verify capability removal

This scenario is intentionally designed as a "playable world memory" demo rather than a static fact set.

## Demo Pattern (Use Every Time)

1. User speaks naturally.
2. Prethinker shows candidate extraction.
3. System asks clarification only where uncertainty justifies it.
4. User confirms before writes.
5. User asks implication/conflict/counterfactual questions.
6. System answers with traceable supporting facts/rules.

That repeatable pattern is what makes this feel like a new interface category instead of a prompt trick.

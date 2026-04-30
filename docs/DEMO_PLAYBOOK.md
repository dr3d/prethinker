# Demo Playbook: Talk Your Rules Into Existence

This playbook merges your 10 high-impact demos with Prethinker-native demos that highlight our governed ingestion model, clarification policy, and deterministic memory.

Last updated: 2026-04-27

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

## Runnable Scenario Direction

The old rendered HTML demo-report lane has been retired from the public tree.
For live work, use the console prompt book and Semantic IR trace renderer
instead:

```powershell
python ui_gateway/main.py
python scripts/run_mixed_domain_agility.py --help
```

For focused current fixtures, start with:

- `docs/data/frontier_packs/semantic_ir_cross_turn_frontier_pack_v1.json`
- `docs/data/frontier_packs/semantic_ir_lava_pack_v5.json`
- `datasets/story_worlds/otters_clockwork_pie/`
- `datasets/story_worlds/iron_harbor_water_crisis/`

For the current "talk your rules into existence" frontier:

```powershell
python scripts/run_semantic_ir_prompt_bakeoff.py --backend lmstudio --base-url http://127.0.0.1:1234 --model qwen/qwen3.6-35b-a3b --scenario-group policy_demo --variants best_guarded_v2
```

For the focused cross-turn reimbursement demo:

```powershell
python scripts/run_policy_reimbursement_demo.py --backend lmstudio --base-url http://127.0.0.1:1234 --model qwen/qwen3.6-35b-a3b --timeout 600 --include-model-input
```

See [docs/POLICY_REIMBURSEMENT_DEMO.md](https://github.com/dr3d/prethinker/blob/main/docs/POLICY_REIMBURSEMENT_DEMO.md).

The first policy-demo group covers reimbursement rules and February violation
queries, meeting commitments, contractor-access sponsorship expiry, customer
support override ladders, story-world throne claims, and business dependency
credibility. Latest local result: `7/7` JSON/schema, `7/7` model decisions,
`7/7` mapper-projected decisions, `67/70` admission checks, average rough score
`0.95`.

The important demo behavior is not that every derived answer becomes a fact. It
is that the system admits grounded facts, admits explicit queries, and keeps
derived consequences in the trace unless a deterministic rule path really
authorizes them.

The focused reimbursement runner now shows that path end to end: English policy
installs executable rules, later English event reports become facts, the Prolog
runtime derives `r1` and `r2` as policy violations, and an explicit correction
removes `r2` from the derived answer without ever writing `violation(r2, ...)`
as a durable fact. Latest local result: `4/4` parsed, `4/4` expected query
matches, `4/4` no derived violation write leak, rough score `1.000`.

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

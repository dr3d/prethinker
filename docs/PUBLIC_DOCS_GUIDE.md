# Public Docs Guide

Last updated: 2026-04-26

This page is the map for public readers. Git history keeps the older research
trail; these docs should describe the project as it sits now.

![Prethinker semantic IR workspace](assets/prethinker-semantic-ir-workspace.png)

## Current Front Door

Read these first:

1. [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md)
2. [README.md](https://github.com/dr3d/prethinker/blob/main/README.md)
3. [AGENT-README.md](https://github.com/dr3d/prethinker/blob/main/AGENT-README.md)
4. [docs/PRETHINK_GATEWAY_MVP.md](https://github.com/dr3d/prethinker/blob/main/docs/PRETHINK_GATEWAY_MVP.md)
5. [ui_gateway/README.md](https://github.com/dr3d/prethinker/blob/main/ui_gateway/README.md)

## Current Research Center

The active architectural pivot is:

```text
utterance + context
  -> semantic_ir_v1 workspace
  -> deterministic mapper/admission diagnostics
  -> KB mutation, query, clarification, quarantine, or rejection
```

The best current documents for that work are:

- [docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md)
- [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md)
- [docs/GUARDRAIL_DEPENDENCY_AB.md](https://github.com/dr3d/prethinker/blob/main/docs/GUARDRAIL_DEPENDENCY_AB.md)
- [docs/PYTHON_GUARDRAIL_AUDIT.md](https://github.com/dr3d/prethinker/blob/main/docs/PYTHON_GUARDRAIL_AUDIT.md)
- [docs/prompts/SEMANTIC_IR_V1.md](https://github.com/dr3d/prethinker/blob/main/docs/prompts/SEMANTIC_IR_V1.md)

## Current Domain Center

The active domain lane is bounded medical memory, not broad diagnosis:

- [docs/MEDICAL_PROFILE.md](https://github.com/dr3d/prethinker/blob/main/docs/MEDICAL_PROFILE.md)
- [docs/UMLS_MVP.md](https://github.com/dr3d/prethinker/blob/main/docs/UMLS_MVP.md)
- [docs/ONTOLOGY_PROSPECTOR.md](https://github.com/dr3d/prethinker/blob/main/docs/ONTOLOGY_PROSPECTOR.md)
- [docs/ONTOLOGY_STEERING.md](https://github.com/dr3d/prethinker/blob/main/docs/ONTOLOGY_STEERING.md)

## Demo Surface

- [docs/CONSOLE_TRYBOOK.md](https://github.com/dr3d/prethinker/blob/main/docs/CONSOLE_TRYBOOK.md)
- [docs/DEMO_PLAYBOOK.md](https://github.com/dr3d/prethinker/blob/main/docs/DEMO_PLAYBOOK.md)
- [docs/EXPLAINER.md](https://github.com/dr3d/prethinker/blob/main/docs/EXPLAINER.md)

## Historical Or Legacy Context

These docs are still useful, but should be read as context for how the project
got here, not as the current center of gravity:

- [docs/GIC_ENGLISH_INPUT_PIPELINE.md](https://github.com/dr3d/prethinker/blob/main/docs/GIC_ENGLISH_INPUT_PIPELINE.md)
- [docs/WILD_MODE.md](https://github.com/dr3d/prethinker/blob/main/docs/WILD_MODE.md)
- [docs/WILD_FAILURE_ISOLATION.md](https://github.com/dr3d/prethinker/blob/main/docs/WILD_FAILURE_ISOLATION.md)
- older HTML run reports under [docs/reports/](https://github.com/dr3d/prethinker/tree/main/docs/reports)
- ladder/rung history under [docs/rungs/](https://github.com/dr3d/prethinker/tree/main/docs/rungs)

The older 9B English-parser lane is not deleted because it explains the path
that led to the semantic IR pivot. It should not be mistaken for the preferred
future architecture.

## Current Evidence Snapshot

Latest local verification before this refresh:

- Full pytest suite: `248 passed`
- Semantic IR runtime edge pack: `20/20` decision labels, `0.976` avg score
- Semantic IR weak-edge pack: `10/10` decision labels, `1.000` avg score
- Silverton probate pack: intentionally hard frontier pack, currently weak
- Silverton noisy temporal pack: intentionally harder noisy/multilingual pack,
  useful as a pressure gauge rather than a demo headline

The important qualitative result is that semantic IR has reduced dependence on
non-mapper Python rescue code in tested packs. The remaining hard problems are
decision-label calibration, temporal fact representation, rule admission, and
the mapper policy for partial/unsafe operations.

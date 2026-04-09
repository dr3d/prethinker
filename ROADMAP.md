# Prethinker Roadmap

Last updated: 2026-04-09

## Positioning

Prethinker is an open, non-commercial research workbench for neuro-symbolic parsing.
The goal is to make parser behavior inspectable, reproducible, and improvable over time.

## Honest Baseline

- End-to-end flow exists: NL utterance -> route + logic extraction -> deterministic apply -> validation -> persisted KB.
- Prompt/version lineage and run provenance are in place (`prompt_id`, snapshots, run settings, manifests).
- Scenario ladder structure exists and is useful for controlled iteration.
- Evidence is still early: current pass counts are small and do not establish broad generalization.
- Hard phenomena (transitivity depth, ambiguity, quantifiers, negation policy, unseen vocabulary) need much stronger coverage.
- External reproducibility is incomplete due to local environment coupling.

## Near-Term Objectives

1. Make the workbench reproducible by other people.
2. Expand evaluation to hard, "foreign" utterances and publish transparent scorecards.
3. Implement uncertainty-aware clarification behavior as a first-class runtime policy.
4. Tighten symbolic guardrails (predicate alignment and type discipline).

## 2-Week Execution Plan

### Week 1: Reproducibility + Benchmark Backbone

1. Environment portability
- Remove hardcoded local assumptions where possible.
- Add explicit setup docs for required sibling/runtime repos and paths.
- Add a preflight check command that validates local prerequisites.

2. One-command benchmark run
- Add a scripted run mode for a defined scenario pack.
- Emit summary metrics (pass/fail totals, parse/apply failures, timeout counts).
- Keep per-scenario and per-phenomenon outputs machine-readable.

3. Scenario expansion
- Add "foreign utterance" scenarios (unseen nouns/predicates/relations).
- Add deeper transitive-chain and compositional rule stress scenarios.
- Add explicit ambiguity scenarios (pronouns, underspecified references).

### Week 2: Behavior Upgrades + Reporting

1. Clarification policy wiring
- Add uncertainty scoring and labels per turn.
- Add clarification-eagerness setting and gating logic.
- Support multiple clarification rounds for a single user utterance when uncertainty remains high.

2. Predicate/type controls
- Finish predicate alignment integration (canonical predicate + alias handling).
- Strengthen strict registry/type modes and error reporting in run artifacts.

3. Publish comparison snapshots
- Run baseline vs updated prompt/system settings on the same scenario pack.
- Publish before/after deltas in `docs/` manifests and human-readable summaries.

## Acceptance Criteria (For This Phase)

- A new collaborator can run baseline scenarios end-to-end by following docs.
- Benchmark pack has enough coverage to expose failure clusters (not just smoke tests).
- Reports include per-phenomenon breakdowns, not only aggregate pass rates.
- Clarification behavior is observable in run outputs with explicit uncertainty traces.

## Training Track (After Prompt/Runtime Stabilization)

1. Unsloth LoRA experiments
- Use the same scenario pack and scorecards as prompt tuning.
- Compare base vs LoRA checkpoints with identical runtime settings.

2. LoRA promotion gates
- Promote only if improvements hold on hard/foreign utterance sets, not only easy ladders.
- Keep prompt provenance and training provenance side-by-side in reports.

3. GGUF packaging
- Treat GGUF as an inference/export target after behavior is validated.
- Document which base model, adapter, and merge settings produced each GGUF artifact.

## Out of Scope For Now

- Full model fine-tuning as primary strategy before prompt/runtime baselines are strong.
- Productization, monetization, or commercialization work.
- Claims of production reliability before hard-benchmark evidence supports it.

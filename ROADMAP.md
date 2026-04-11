# Prethinker Roadmap

Last updated: 2026-04-11

## Positioning

Prethinker is an open, non-commercial research workbench for neuro-symbolic parsing.
The goal is to make parser behavior inspectable, reproducible, and improvable over time.

## Honest Baseline

- End-to-end flow exists: NL utterance -> route + logic extraction -> deterministic apply -> validation -> persisted KB.
- Prompt/version lineage and run provenance are in place (`prompt_id`, snapshots, run settings, manifests).
- Scenario ladder structure exists and is useful for controlled iteration.
- Observability is currently stronger than proof depth.
- Evidence is still early: current pass counts are small and do not establish broad generalization.
- Hard phenomena (transitivity depth, ambiguity, quantifiers, negation policy, unseen vocabulary) need much stronger coverage.
- External reproducibility is incomplete due to local environment coupling.

## External Critique Response Track (Now Priority 0)

This track captures feedback from external review (`SUPER_CHATGPT.md`) plus DeepWiki surface review.
Goal: move from "well-instrumented prototype" to "skeptically credible public evidence".

### What we already hardened (2026-04-11)

1. Runtime semantics
- `runtime=none` runs are no longer false-green passes.
- Parse-only runs now report `overall_status=skipped`.

2. Clarification safety
- `clarification_requested` is treated as non-success for apply failure accounting.

3. Ladder execution safety
- `run_ladder.py` cache signature now includes KB-state dimensions (`kb_root`, `kb_name`, `corpus_path`, `seed_from_kb_path`).
- `--start-rung` / `--end-rung` bounds are validated with clean CLI errors.

4. Report wiring
- Hub index can resolve nested report HTML paths (not only flat `docs/reports/<stem>.html`).

### Remaining high-priority proof work

1. Freeze public claim language
- Keep the front-door claim scoped to what is currently proven:
  - semantic parser workbench for deterministic KB mutation and validation.
- Keep broader architecture claims (hard/soft decoupling) marked as active research until explicitly benchmarked.

2. Publish strict evidence partitions
- Every benchmark table must segment:
  - strict registry on/off
  - strict types on/off
  - clarification auto-answer on/off
  - model + prompt ID + CE setting
- Avoid blended pass-rate headlines that combine assisted and unassisted modes.

3. Prove strict lane, not only loose lane
- Define one canonical strict benchmark pack with:
  - `--strict-registry`
  - `--strict-types`
  - no clarification auto-answer
- Promote results only when strict pack is green or transparently shows bounded failures.

4. Hero demo policy
- Keep Goldilocks visible as stress/failure analysis unless it passes a defined quality bar.
- Promote a smaller clean roundtrip demo to front-door hero slot.

5. Holdout benchmark discipline
- Add frozen holdout scenarios not used for prompt tuning.
- Require holdout reporting for any "improvement" claim.

6. Reproducibility packaging
- Add missing collaborator essentials:
  - `LICENSE`
  - `.env.example`
  - lightweight env/package manifest
  - one-command preflight + benchmark command
- Remove local absolute paths from published artifacts where possible.

7. Interpreter verification depth
- Expand tests for logic-engine edge behavior:
  - negation, cut, `findall`, recursion depth guards, variable handling, retract semantics.
- Add differential checks against a reference Prolog engine for a focused conformance subset.

8. Docs trust surface
- Ensure hub/rung pages and JSON links remain consistent (no stale 404s, no contradictory "no report found").
- Keep top-line metrics pre-rendered and consistent with published manifests.

9. Real-domain demonstration
- Add one typed domain beyond family trees (for example compliance, incident tracking, or manufacturing).
- Show why deterministic mutation + provenance matters in that domain.

## Near-Term Objectives

1. Make the workbench reproducible by other people.
2. Expand evaluation to hard, "foreign" utterances and publish transparent scorecards.
3. Implement uncertainty-aware clarification behavior as a first-class runtime policy.
4. Tighten symbolic guardrails (predicate alignment and type discipline).
5. Separate architecture storytelling from empirically proven claims in all public surfaces.

## 2-Week Execution Plan

### Week 1: Reproducibility + Benchmark Backbone

1. Environment portability
- Remove hardcoded local assumptions where possible.
- Keep default flow sibling-repo-free.
- Add a preflight check command that validates local prerequisites.
- Add `.env.example`, `LICENSE`, and minimal environment manifest.

2. One-command benchmark run
- Add a scripted run mode for a defined scenario pack.
- Emit summary metrics (pass/fail totals, parse/apply failures, timeout counts).
- Keep per-scenario and per-phenomenon outputs machine-readable.
- Emit partitioned scorecards for strict/unstrict and assisted/unassisted modes.

3. Scenario expansion
- Add "foreign utterance" scenarios (unseen nouns/predicates/relations).
- Add deeper transitive-chain and compositional rule stress scenarios.
- Add explicit ambiguity scenarios (pronouns, underspecified references).
- Add a frozen holdout pack not used during prompt tuning.

### Week 2: Behavior Upgrades + Reporting

1. Clarification policy wiring
- Add uncertainty scoring and labels per turn.
- Add clarification-eagerness setting and gating logic.
- Support multiple clarification rounds for a single user utterance when uncertainty remains high.
- Keep clarification auto-answer results isolated from parser-alone benchmark claims.

2. Predicate/type controls
- Finish predicate alignment integration (canonical predicate + alias handling).
- Strengthen strict registry/type modes and error reporting in run artifacts.
- Make strict-mode runs a first-class benchmark lane.

3. Publish comparison snapshots
- Run baseline vs updated prompt/system settings on the same scenario pack.
- Publish before/after deltas in `docs/` manifests and human-readable summaries.
- Include known-failure pages alongside best-results pages.

## Acceptance Criteria (For This Phase)

- A new collaborator can run baseline scenarios end-to-end by following docs.
- Benchmark pack has enough coverage to expose failure clusters (not just smoke tests).
- Reports include per-phenomenon breakdowns, not only aggregate pass rates.
- Clarification behavior is observable in run outputs with explicit uncertainty traces.
- Public results clearly separate strict vs loose and assisted vs unassisted regimes.
- At least one non-family-tree domain is benchmarked with reproducible artifacts.

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

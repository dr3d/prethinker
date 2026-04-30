# Otters Story-World Progress Journal

This is the side ledger for making Prethinker increasingly good at the
`The Three Otters and the Clockwork Pie` benchmark.

The point is not to cherry-pick polished runs. The point is to keep visible
numbers as the system moves from shallow safe extraction toward source-faithful,
queryable narrative logic.

## Run OTR-001 - Cold Current Pipeline Baseline

- Timestamp: `2026-04-30T01:27:58Z`
- Model: `qwen/qwen3.6-35b-a3b`
- Mode: raw story -> intake plan -> profile bootstrap/review/retry -> source
  compile by LLM-authored plan passes -> QA first 20
- Expected Prolog was used only for after-the-fact signature comparison. It was
  not used as profile guidance.
- Local compile artifact:
  `tmp/domain_bootstrap_file/domain_bootstrap_file_20260430T012758919267Z_story_qwen-qwen3-6-35b-a3b.json`
- Local QA artifact:
  `tmp/domain_bootstrap_qa/domain_bootstrap_qa_20260430T013055910737Z_qa_qwen-qwen3-6-35b-a3b.json`

### Headline

Safe-ish and structured, but not yet a real story-world reasoner.

The run discovered a plausible profile and admitted many facts, but it did not
produce the event/temporal/causal/final-state reasoning surface needed for the
QA battery. This is a good first ugly dot on the graph.

### Compile Metrics

| Metric | Value |
| --- | ---: |
| Parsed profile JSON | `true` |
| Profile rough score | `0.778` |
| Candidate predicates | `25` |
| Generic predicates | `0` |
| Repeated structures | `3` |
| Admission risks | `5` |
| Source compile admitted ops | `96` |
| Source compile skipped ops | `4` |
| Unique facts | `91` |
| Unique rules | `0` |
| Unique queries | `0` |
| Emitted predicate signatures | `15` |
| Expected gold signatures | `113` |
| Emitted/gold signature recall | `0.000` |

### QA First-20 Metrics

| Metric | Value |
| --- | ---: |
| Questions | `20` |
| Parsed query workspaces | `20/20` |
| Query rows attempted | `20/20` |
| Judge exact | `7` |
| Judge partial | `0` |
| Judge miss | `13` |
| Exact rate | `0.350` |
| Runtime load errors | `0` |
| Proposed writes during QA | `0` |

### What It Got Right

- Did not collapse the story into bears/porridge/chairs/beds in the compiled KB.
- Produced a source-local cast: Little Slip, Middle-sized Otter, Great Long
  Otter, Tilly, aunt, clockwork pie, boats, boots, mugs.
- Captured some ownership and object inventory.
- Captured some speech acts as `reported_speech/3`.
- Captured some internal-state/remediation facts.

### What Failed

- No durable event ledger: no `event/5`-style spine and no stable `story_time/2`.
- No real temporal reasoning surface: no admitted ordering graph equivalent to
  the gold KB.
- No causal layer rich enough for "why did X happen?" questions.
- No final-state model strong enough to distinguish "happened during the story"
  from "true after repair."
- Predicate surfaces drifted away from the reference KB, making QA query planning
  fragile.
- Several first-20 questions failed because the compiled KB lacked direct
  house-membership, location, errand, or object-component support in the shapes
  the QA planner could query.

### Next Hypotheses

1. Add narrative-source context pressure that asks the model for an event ledger,
   temporal anchors, causal consequences, and final-state updates when the
   source type is a closed story or fable.
2. Keep the fix as context engineering. Do not add Python phrase handling or
   story-specific extraction rules.
3. Track progress with both compile metrics and QA metrics; QA is the harder,
   more honest signal.
4. Add phase-level QA scoring after the first full 100-question run so we can see
   whether improvements are coming from entity/object facts, chronology,
   causality, speech/truth, or final-state modeling.

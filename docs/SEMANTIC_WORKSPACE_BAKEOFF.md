# Semantic Workspace Bakeoff

Last updated: 2026-04-25

This note records the first local Ollama bakeoff for a larger, more pluggable
Prethinker language layer. Raw model traces stay under `tmp/semantic_bakeoff/`
and are not intended for GitHub.

## Question

The current pipeline uses Python guard rails heavily: route classification,
normalization, schema checks, domain-specific ambiguity holds, and deterministic
KB mutation gates. The research question is whether a larger local model can do
more of the semantic workspace work before the deterministic gate, without
letting the model own durable truth.

The candidate division of labor is:

- LLM semantic workspace: identify readings, direct assertions, unsafe
  implications, missing slots, and candidate symbolic operations.
- Deterministic gate: validate schema, reject unknown predicates, require
  clarification, apply safe mutations, and log provenance.
- Prolog-like runtime: answer and prove from committed facts and rules only.

## Pilot Setup

Harness:

```powershell
python scripts/run_semantic_workspace_bakeoff.py `
  --models qwen3.5:9b,qwen3.6:27b,qwen3.6:35b `
  --modes semantic_workspace,ambiguity_critic,strict_compiler `
  --scenario-ids medical_pressure_vague,medical_pronoun_creatinine_after_two_patients,medical_allergy_vs_side_effect,correction_cart_holder,ancestor_rule_safe_recursion,temporal_false_claim,medical_advice_boundary `
  --timeout 300
```

Scenarios deliberately included vague medical language, pronouns after multiple
patients, allergy-versus-intolerance, correction/retraction, safe recursive rule
creation, temporal false claims, and medical-advice boundaries.

Modes:

- `semantic_workspace`: richer analysis, `think=true`, temperature 0.2.
- `ambiguity_critic`: conservative risk/clarification pass, `think=true`,
  temperature 0.1.
- `strict_compiler`: compact candidate operation compiler, `think=false`,
  temperature 0.0.

## Initial Result

The compact run completed 63 calls. The rough score is intentionally crude and
should be treated as a triage signal, not a benchmark.

| Model | Mode | JSON OK | Avg rough score | Avg latency |
|---|---:|---:|---:|---:|
| `qwen3.5:9b` | `semantic_workspace` | 5/7 | 0.65 | 53.3s |
| `qwen3.5:9b` | `ambiguity_critic` | 6/7 | 0.53 | 39.5s |
| `qwen3.5:9b` | `strict_compiler` | 7/7 | 0.83 | 3.4s |
| `qwen3.6:27b` | `semantic_workspace` | 7/7 | 0.80 | 66.9s |
| `qwen3.6:27b` | `ambiguity_critic` | 7/7 | 0.69 | 52.7s |
| `qwen3.6:27b` | `strict_compiler` | 7/7 | 0.72 | 6.5s |
| `qwen3.6:35b` | `semantic_workspace` | 7/7 | 0.77 | 30.9s |
| `qwen3.6:35b` | `ambiguity_critic` | 7/7 | 0.63 | 23.3s |
| `qwen3.6:35b` | `strict_compiler` | 7/7 | 0.67 | 3.6s |

## Read

The 27B dense model looks best when allowed to perform rich semantic-workspace
analysis, but it is slow enough that it probably belongs on hard turns rather
than every turn.

The 35B-A3B MoE looks unusually promising for this project: it kept JSON
reliability at 7/7 in all modes and ran the rich pass in roughly half the 27B
time. It should be tested further as the default "smart sidecar" candidate.

The 9B strict compiler remains a strong operational baseline. It is fast and
stable, but the richer thinking modes produced empty `content` on several 9B
calls because useful text landed in Ollama's `thinking` channel instead of the
JSON response body.

## Gemma4 26B Check

A follow-up run added `gemma4:26b` on the same seven compact scenarios.

| Model | Mode | JSON OK | Avg rough score | Avg latency |
|---|---:|---:|---:|---:|
| `gemma4:26b` | `semantic_workspace` | 5/7 | 0.66 | 17.8s |
| `gemma4:26b` | `ambiguity_critic` | 4/7 | 0.59 | 20.2s |
| `gemma4:26b` | `strict_compiler` | 7/7 | 0.75 | 6.1s |

Gemma4 26B is worth keeping in the candidate pool, especially as a strict
compiler or structured IR emitter. It handled temporal false claims, pronoun
ambiguity, recursive rule creation, and allergy-versus-intolerance reasonably
well when it returned parseable JSON.

The concern is reliability under richer `think=true` prompts. Several rich
analysis calls either timed out or returned non-JSON output, and two correction
or ambiguity cases produced long stalls before the run resumed. That makes it
less attractive than `qwen3.6:35b` for the first smart sidecar, but it may still
be useful in a non-thinking decision-contract sweep.

Current model read:

- First sidecar candidate: `qwen3.6:35b`, because it gave strong JSON reliability
  and much better latency than dense 27B in rich mode.
- Deep adjudicator candidate: `qwen3.6:27b`, because its rich semantic workspace
  was strongest but slow.
- Fast strict baseline: `qwen3.5:9b`.
- Worth further testing: `gemma4:26b`, but probably with `think=false` and a
  smaller decision-contract output.

## Caveats

- The scorer is keyword-based and can over-credit or under-credit semantically
  correct behavior.
- The initial run was weighted toward ambiguity and safety boundaries, not
  routine clean commits.
- `think=true` confounds reasoning quality with output-channel reliability.
- A good semantic workspace may mention unsafe candidate facts explicitly; a
  naive scorer can mistake that for a bad commit.
- This is local research evidence, not a public benchmark.

## Next Experiment

Run a decision-contract sweep with a smaller, normalized output shape:

```json
{
  "decision": "commit|clarify|quarantine|reject|answer",
  "safe_operations": [],
  "unsafe_candidates": [],
  "clarification_question": null,
  "rationale_tags": []
}
```

Use opaque evaluation items, run `think=false` first for all models, then add a
separate `think=true` run after output capture is understood. Score structure:
exact decision, normalized safe operation match, unsafe-candidate handling,
bad-commit flag, missing clarification flag, and latency.

The architectural question for the next phase is not "can the LLM replace the
gate?" It is whether a model sidecar can reduce bad commits and improve
clarification quality while the deterministic runtime keeps final authority.

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

## MedGemma 27B Check

A follow-up run added `medgemma:27b`. The Google model card describes MedGemma
as a Gemma 3 derivative trained for medical text and image comprehension, with
27B text-only and multimodal variants. It also cautions that outputs are
preliminary and require independent validation, clinical correlation, and
task-specific adaptation before use in clinical settings. That makes MedGemma a
good fit for a governed semantic sidecar, not a final authority layer.

Ollama reported that `medgemma:27b` does not support the `think=true` option, so
the harness now retries unsupported thinking calls with `think=false` and marks
those records with `thinking_fallback=true`.

Fair fallback run on the same seven compact scenarios:

| Model | Mode | JSON OK | Avg rough score | Avg latency |
|---|---:|---:|---:|---:|
| `medgemma:27b` | `semantic_workspace` | 7/7 | 0.45 | 4.5s |
| `medgemma:27b` | `ambiguity_critic` | 7/7 | 0.76 | 6.9s |
| `medgemma:27b` | `strict_compiler` | 7/7 | 0.65 | 4.7s |

Qualitative read:

- Strong medical ambiguity critic. It handled vague pressure, creatinine pronoun
  ambiguity, and allergy-versus-intolerance especially well.
- Fast and reliable JSON once `think=true` was disabled.
- The rich semantic workspace prompt is not a good fit as currently written. It
  often returned structurally valid but semantically thin JSON for non-medical or
  high-level scenarios.
- Strict compiler was mixed: good on allergy-versus-side-effect and temporal
  false-claim cases, weaker on pronoun identity and non-medical correction.

Current model read after MedGemma:

- Medical ambiguity critic candidate: `medgemma:27b`.
- General semantic sidecar candidate: `qwen3.6:35b`.
- Deep general adjudicator candidate: `qwen3.6:27b`.
- Fast strict baseline: `qwen3.5:9b`.
- General Gemma-family backup: `gemma4:26b`, preferably with `think=false`.

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

## Semantic IR Prompt Iteration

A separate prompt iteration fixed `qwen3.6:35b` as the general sidecar candidate
and tested `semantic_ir_v1` prompts on a wilder utterance pack. The first prompt
pass produced valid JSON but wrapped the IR under a `schema_contract` key. After
tightening the system prompt to require `schema_version` and `decision` at the
root, all variants produced valid top-level IR.

The current best candidate is `best_guarded_v2`, documented in
`docs/prompts/SEMANTIC_IR_V1.md`.

Controls:

- model: `qwen3.6:35b`
- temperature: `0.0`
- top_p: `0.82`
- top_k: `20`
- think: `false`

Wild-pack result:

| Variant | JSON OK | Schema OK | Decision OK | Avg rough score | Avg latency |
|---|---:|---:|---:|---:|---:|
| `best_guarded_v2` | 12/12 | 12/12 | 7/12 | 0.88 | 5.8s |

Qualitative read: the prompt is now good enough to demonstrate rich semantic
workspace behavior. It handles vague pressure, active-context lab follow-up,
cart correction, mixed rule/query turns, typo-heavy pronoun ambiguity, and
allergy-versus-side-effect better than the earlier Prolog-ish extraction style.
The remaining weakness is decision-label calibration: it sometimes chooses
`mixed` when the deterministic policy should probably force `reject`,
`quarantine`, `clarify`, or `commit`.

A follow-up "Glitch in the Airlock" story pack tested the old story-state
failure mode directly. `best_guarded_v2` scored 6/6 JSON, 6/6 schema, 6/6
decision, with average rough score 0.98 and average latency 6.3s. The run did
not repeat the old Unit-Alpha-as-salvager error, and it captured the airlock
backflip, Sonic-Zips damage, and Widget's claim without turning the claim into
an observed possession fact. That run also motivated adding `polarity` to
`candidate_operations`, so negative story facts do not become positive KB
mutations by accident.

A harder Ledger story pack then tested conditional legal and temporal state:
separation agreements, default certification, half-share transfers, conditional
inheritance, aliases, guardianship, residency loss, and charter sequencing.
`best_guarded_v2` scored 8/8 JSON, 8/8 schema, 8/8 decision, with average rough
score 0.98 and average latency 8.8s. The important qualitative result is that
the model can keep conditional rules separate from completed facts. In the
separation clause, it marked the turn `mixed`: safe conditional structure can be
represented, while completed default and transfer facts remain uncommitted until
later evidence appears.

## Guardrail Dependency Metric

The next measurement should be whether the semantic IR path actually reduces
Python-side semantic rescue code. The current pipeline still contains concrete
rescue hooks for possessive family bundles, same-clause spouse phrases,
same-utterance family-anchor pronouns, route heuristics, clarification cleanup,
predicate canonicalization, and query fallback behavior.

Proposed metric:

| Metric | Question |
|---|---|
| semantic rescue hooks invoked | How many Python semantic patch paths fired on this turn? |
| rescue-critical commits | Would the old path have committed the correct mutation without a rescue hook? |
| IR direct coverage | Did semantic IR express the same structure before Python repair? |
| unsafe commit rate | Did either path admit a bad fact? |
| false clarification rate | Did either path ask when it could safely proceed? |
| patch pressure | Did a new scenario require new Python English-special-case code? |

The research target is not zero deterministic code. It is fewer English-specific
semantic patches while preserving strict admission, provenance, and auditability.

## Runtime Opt-In

The first executable semantic-IR runtime path is now available behind
`semantic_ir_enabled`. When enabled, `PrologMCPServer.process_utterance()` uses
one `semantic_ir_v1` model call for pre-think routing, then maps only safe
`candidate_operations` into the existing deterministic runtime parse. This path
skips the legacy English rescue chain for the parse step; the parse trace should
show `semantic_ir_mapper` instead of the older compound-family,
subject-prefixed-predicate, correction, step-sequence, and profile rescue passes.

Initial live smoke:

- model: `qwen3.6:35b`
- utterance: `Mara owns the silver compass.`
- semantic IR operation: safe direct `owns/2` assertion
- committed fact: `owns(mara, silver_compass).`
- parse-side rescue list: `semantic_ir_mapper`

The mapper is intentionally conservative. It commits safe positive direct
assertions and queries, but it does not yet commit negative mutations or rule
operations unless an explicit rule clause is present. That keeps the authority
boundary intact while the semantic sidecar grows more capable.

## Edge Exploration

The first hard `qwen3.6:35b` edge battery added 20 cases covering nested
exceptions, counterfactuals, quantifiers, identity repair, provenance, temporal
intervals, disjunctive causality, medical negation, double negation, and
hypothetical queries. `best_guarded_v2` remains the best decision prompt:

| Variant | Runs | JSON OK | Schema OK | Decision OK | Avg rough score |
|---|---:|---:|---:|---:|---:|
| `best_guarded_v2` | 20 | 20/20 | 20/20 | 17/20 | 0.96 |
| `best_guarded_v3` | 20 | 20/20 | 20/20 | 15/20 | 0.92 |

The main finding is that the model is now strong enough that the weak points are
mostly schema and mapper boundaries: hypothetical queries, safe correction
labeling, medical negation policy, durable negation, and full rule admission.
See `docs/SEMANTIC_IR_EDGE_EXPLORATION.md` for the detailed read.

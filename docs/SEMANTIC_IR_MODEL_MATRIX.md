# Semantic IR Model Matrix

Last updated: 2026-04-26

This note records a controlled local model-family pass for the active
`semantic_ir_v1` direction.

The question:

```text
Did the newest gains come mostly from LM Studio structured output,
or does the model still matter?
```

## Method

All runs below use the same runtime path:

- backend: LM Studio OpenAI-compatible API
- output mode: structured JSON schema where supported by the runtime
- prompt contract: `semantic_ir_v1`
- mapper/runtime: current deterministic admission path
- temperature: runtime default for semantic IR, currently `0.0`
- context: semantic IR default, currently `16384`

Only `--semantic-model` changes. This is still a local research harness, not an
external benchmark.

## Runtime Matrix

| Model | Rule/Mutation | Weak Edges | Hard Edge |
| --- | ---: | ---: | ---: |
| `qwen/qwen3.6-35b-a3b` | 10/10, avg 0.917 | 9/10, avg 0.967 | 17/20, avg 0.930 |
| `qwen/qwen3.5-9b` | 10/10, avg 0.917 | 8/10, avg 0.917 | 14/20, avg 0.881 |
| `qwen/qwen3.6-27b` | 9/10, avg 0.883 | 7/10, avg 0.883 | not run |
| `google/gemma-4-26b-a4b` | 10/10, avg 0.917 | 10/10, avg 0.983 | 19/20, avg 0.959 |
| `nvidia/nemotron-3-nano` | 4/10, avg 0.652 | 4/10, avg 0.692 | not run |

Noisy Silverton probate runs remain hard:

| Model | Silverton Noisy |
| --- | ---: |
| `qwen/qwen3.6-35b-a3b` | 3/8, avg 0.760 |
| `google/gemma-4-26b-a4b` | 3/8, avg 0.750 |

## Read

Structured output is doing real work. Even the 9B Qwen model stays schema-clean
and competitive on the smaller rule/mutation pack.

But model choice still matters. Nemotron used the same structured-output path
and still underperformed badly. Its failure shape was not broken JSON; it was
semantic/policy behavior:

- over-clarifying safe commits;
- missing direct rule admission;
- treating context queries as clarification turns;
- weakening explicit correction/retraction cases;
- showing occasional timeout/500 behavior.

Gemma 26B is the surprise. On this local pass it was the best overall model,
especially on the hard edge battery. It preserved the Semantic IR contract while
handling identity repair, temporal correction, denial-vs-negation, exception
pressure, and mixed claim/fact cases well.

Qwen 35B remains a strong default. It is more proven in the project history and
has good behavior on the same architecture, but it is not automatically the
winner on every local battery. The model matrix says we should keep the harness
model-agnostic and avoid overfitting the prompt to one family.

The noisy Silverton pack is a different story. Gemma and Qwen 35B both stalled
around `3/8`. Those misses are less about raw model intelligence and more about
the next formal frontier: temporal policy labels, mixed-language spelling,
relative-date grounding, and whether a safe temporal correction should still be
`mixed` because unsafe legal consequences ride alongside it.

## Current Best Bets

Recommended research defaults:

- primary comparison model: `qwen/qwen3.6-35b-a3b`
- small baseline: `qwen/qwen3.5-9b`
- different-family challenger: `google/gemma-4-26b-a4b`
- negative contrast: `nvidia/nemotron-3-nano`

Do not tune around Nemotron yet. Keep it as evidence that structured output does
not make every capable model suitable for this governed compiler job.

## Harness Notes

The A/B runners now include scenario group, model slug, process ID, and
microseconds in output filenames. This avoids evidence loss when AFK sweeps run
in parallel or start in the same second.

The comparison table can be regenerated from local JSONL artifacts with:

```text
python scripts/summarize_semantic_ir_model_matrix.py tmp/guardrail_dependency_ab/*.jsonl
```

Recent local artifacts:

- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T170337Z.jsonl`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T171644Z.jsonl`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T172302Z.jsonl`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T172636Z.jsonl`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T173223Z.jsonl`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T174503Z.jsonl`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T175038Z.jsonl`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T175858287710Z_rule-mutation_qwen-qwen3-6-27b_pid29360.jsonl`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T180555424988Z_rule-mutation_google-gemma-4-26b-a4b_pid50848.jsonl`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T181205798824Z_weak-edges_google-gemma-4-26b-a4b_pid49060.jsonl`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T181801755453Z_weak-edges_qwen-qwen3-6-27b_pid50688.jsonl`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T182512980833Z_edge_google-gemma-4-26b-a4b_pid44316.jsonl`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T183753729830Z_edge_qwen-qwen3-6-35b-a3b_pid45200.jsonl`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T185356411787Z_silverton-noisy_google-gemma-4-26b-a4b_pid19856.jsonl`
- `tmp/guardrail_dependency_ab/guardrail_dependency_ab_20260426T185825798091Z_silverton-noisy_qwen-qwen3-6-35b-a3b_pid46608.jsonl`

## Next Work

- Repeat the hard-edge battery for top models before treating any ranking as
  stable.
- Add a few multilingual/noisy packs to test whether the Semantic IR direction
  really escapes English-only patching.
- Split the noisy Silverton score into semantic extraction, policy label, and
  final KB safety. Current one-number scoring hides cases where the model reads
  the sentence but chooses the wrong administrative label.
- Score "safe-block equivalent" separately from exact decision labels, because
  `clarify`, `quarantine`, and `mixed` can all avoid bad commits while implying
  different product behavior.

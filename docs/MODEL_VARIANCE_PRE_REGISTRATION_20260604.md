# Model Variance Pre-Registration - 2026-06-04

This protocol freezes the next model/runtime variance excursion before any new
Gemma, Qwen, seed, or temperature result can influence the plan.

The purpose is robustness measurement, not model shopping. The deliverable is a
spread of outcomes with row-level churn and gate status. The deliverable is not
the best score observed in any arm.

## Research Question

```text
Are the current closed-domain transfer cells a property of the governed
predicate-pack method, or are they materially dependent on one local Qwen
serving path and decoding bundle?
```

This protocol can change confidence in the current claim. It does not expand
the claim to new families, broad QA, product readiness, or arbitrary document
understanding.

## Primary Anchors

The first variance cell is SEC Form 8-K because it is the cleanest current
skeleton-pack methods example and already has a seed plus three unlike
transfers.

Compile-fact anchors:

```text
sec_form_8k_skeleton_v1
sec_form_8k_skeleton_transfer_001
sec_form_8k_skeleton_transfer_002
sec_form_8k_skeleton_transfer_003
```

Current reference measurement:

```text
support>=2: 50 / 50
per-run exact: 144 / 150
forbidden support: 0
redaction replay: 144 / 144 exact rows survive
typed-plan replay: 144 / 144 exact rows replay through registered carriers
```

Query anchor:

```text
SEC transfer_003 five-row atom-library query smoke
```

Current reference measurement after mapper variable preservation:

```text
5 / 5 judged exact
typed-plan replay: 5 / 5
redacted rejudge: 5 / 5
prose-dependent exact rows: 0
compatibility/runtime/write rows: 0
```

Do not add or remove anchor cells after seeing a result. If an anchor cannot run
because a runtime is unavailable, mark that cell as unavailable or deferred.
Do not silently substitute a friendlier cell.

## Arms

### Arm A - Reference Local Qwen, Temperature 0

Use the current local LM Studio Qwen lane exactly as loaded and record all
available metadata.

Required metadata:

```text
provider: lmstudio
model id: as returned by /v1/models or /api/v0/models
model file / quantization: as shown by LM Studio
architecture: as returned or observed
loaded context length: as returned or observed
temperature: 0.0
top_p: 1.0 unless the run explicitly records otherwise
seed: recorded if supplied, but not treated as proof of determinism
```

Run count:

```text
N=5 same-condition draws for the SEC compile-fact anchors
N=5 same-condition draws for the SEC atom-library query anchor if practical
```

If N=5 is too expensive, stop at N=3 and record the truncation as a protocol
deviation. Do not replace missing draws with another model/provider.

### Arm B - Reference Local Qwen, Temperature Sweep

This arm is diagnostic only. It does not change the default claim setting.

Run:

```text
temperature=0.2, N=3
temperature=0.5, N=3
```

Use the same SEC anchors and all other settings from Arm A. Report all churn.
Expect scores to wobble. Do not chase the wobble with prompt or schema changes.

### Arm C - Dense Gemma Control

Gemma is a control, not a candidate replacement. Use the exact locally loaded or
hosted Gemma model id if and only if it is available.

First run only:

```text
temperature=0.0
N=5 if practical, otherwise N=3 with deviation recorded
same SEC anchors
same gates
```

If Gemma holds clean, the result hardens the claim by showing that the SEC
skeleton result is not only a Qwen/MoE artifact. If Gemma degrades, that is a
finding, not a reason to discard the cell.

Do not tune predicate contracts, prompts, post-processors, query retry logic, or
oracles between the Qwen and Gemma arms.

### Deferred Arms

OpenRouter Qwen, local dense models, alternate quants, and thinking/reasoning
lanes are not part of this pre-registration unless a later dated protocol adds
them.

Do not mix OpenRouter and local LM Studio results as interchangeable. If
OpenRouter enters a later protocol, provider/backend metadata is part of the
cell identity.

## Gates

Every compile-fact anchor must report:

```text
support>=2 expected facts
per-run exact / partial / miss if a per-run QA view is available
supported forbidden facts
registered signatures
atom-shape findings
lens-scope findings
carrier value-domain findings where applicable
redaction replay for exact rows
typed-plan replay for exact rows
compatibility/runtime/write rows
metadata completeness
```

Every atom-library query anchor must report:

```text
exact / partial / miss
blocked atom constants
blocked source-record plans
typed-plan replay
redacted rejudge
prose-dependent exact rows
compatibility/runtime/write rows
metadata completeness
```

A cell that fails hygiene is reported as failed. It is not repaired inside this
protocol.

## Reporting Rules

Report all cells, including bad ones.

For each arm, report:

```text
mean and range, when a numeric summary is appropriate
row-level churn against the reference cell
which rows are stable exact, unstable, or stable miss
which gates pass or fail
metadata gaps
latency and cost when available
```

Do not report "best model per row" or "best model per fixture" as a claim. That
would be model-shopping.

Do not treat a higher score at a nonzero temperature as a new default. Nonzero
temperature arms are variance probes unless a later pre-registered protocol
turns them into a claim lane.

## Stop Conditions

Stop the protocol and write the result, rather than repairing, when any of these
happen:

- an anchor cell fails a hard governance gate;
- the model/runtime is unavailable;
- metadata cannot identify the model/provider/settings bundle;
- a run hits rate limits or local runtime instability repeatedly;
- row churn is broad enough that the cell no longer tests the same method.

The correct output of a failed arm is a negative or unavailable result, not an
adjacent code-hardening project.

## Non-Goals

This protocol does not:

- choose a production model;
- prove broad Prethinker QA;
- rescue query planning outside typed atom libraries;
- justify prompt/schema edits between arms;
- tune for the maximum observed score;
- revisit old contaminated scores;
- promote Gemma, Qwen, OpenRouter, or LM Studio as generally equivalent.

## Next Action After Completion

Update:

```text
docs/DOMAIN_PACK_RESEARCH_EVIDENCE.md
docs/PROVIDER_RUNTIME_DISCIPLINE_NOTE.md
PROJECT_STATE.md
```

The update should state the measured variance band and whether the SEC methods
example appears stable across the tested runtime/model arms. If the result is
negative, say so plainly and narrow the current research claim accordingly.
